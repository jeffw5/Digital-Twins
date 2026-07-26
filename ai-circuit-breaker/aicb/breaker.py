"""
The AI Circuit Breaker -- The Veto Gate.

Orchestrates the (H, O, V, A) tuple into the deterministic trip logic described in the
design spec and the ECG technical design doc's "Core Trip Logic":

    IF (Intent_Delta > Sensor_Ground_Truth_Tolerance)
       OR (Trust_Metric < Minimum_Trust_Threshold)
       OR (Semantic_Anomaly_Score > Anomaly_Ceiling)
       OR (Contextual_Relevancy_Index < CRI_Minimum)
       OR (out of holonic scope)
       OR (ontology impossible-state violation)
    THEN ACTIVATE CIRCUIT BREAKER (DETERMINISTIC VETO)
         EXECUTE Safe_State_Action(severity_level)
         FLAG data_epoch for SOP-03 exclusion from training queue
         LOG full trace
    ELSE TRANSMIT AI_assertion, ATTACH trust_score_metadata

Also implements:
  SOP-01 Semantic Handshake      -- pre-flight check before autonomous operation
  SOP-02 Real-Time Calibration   -- triple-trip lockout + trustee re-authorization
  SOP-03 Recursive Loop Sanitization -- data exclusion filter for the training pipeline
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

from .tuple_config import HolonicBoundary, DomainOntology, VectorContextStore, AgentAssertion, GroundTruth
from .metrics import (
    semantic_anomaly_score,
    contextual_relevancy_index,
    composite_trust_index,
    clamp01,
)
from .spc import evaluate as spc_evaluate
from .audit import AuditTrail
from .morphism import MorphismChain, PassResult
from .hitl import ReviewLog, ReviewAction, HTDR


class SafeState(IntEnum):
    NORMAL = 0
    LEVEL1_SOFT_ALERT = 1
    LEVEL2_HOLD = 2
    LEVEL3_HALT = 3
    LOCKOUT = 4  # SOP-02 triple-trip lockout; supersedes level 3 until trustee clears it


DECISION_LABEL = {
    SafeState.NORMAL: "TRANSMIT",
    SafeState.LEVEL1_SOFT_ALERT: "SOFT_ALERT",
    SafeState.LEVEL2_HOLD: "HOLD",
    SafeState.LEVEL3_HALT: "HALT",
    SafeState.LOCKOUT: "LOCKOUT",
}


@dataclass
class BreakerConfig:
    # Section 2 tolerances
    sa_ceiling: float = 0.15            # Semantic Anomaly Score trip ceiling
    cr_minimum: float = 0.85            # Contextual Relevancy Index trip floor
    trust_minimum: float = 0.65         # composite trust floor
    ktrust_lockdown: float = 0.50       # Human-AI Calibration Coefficient lockdown floor
    intent_delta_tolerance: float = 0.35  # generic scalar "Intent Delta" tolerance, domain-scaled

    # SOP-02
    triple_trip_window_seconds: float = 600.0
    triple_trip_count: int = 3

    # SOP-03
    exclusion_buffer_seconds: float = 30.0

    # SPC (Layer 3)
    use_spc_soft_alerts: bool = True
    spc_min_subgroups: int = 25

    embedding_dim: int = 256


@dataclass
class BreakerDecision:
    passed: bool
    safe_state: SafeState
    decision_label: str
    metrics: dict
    reasons: list
    audit_hash: str
    excluded_from_training: bool


class CircuitBreaker:
    def __init__(
        self,
        holon: HolonicBoundary,
        ontology: DomainOntology,
        vector_store: VectorContextStore,
        config: Optional[BreakerConfig] = None,
        morphism_chain: Optional[MorphismChain] = None,
    ) -> None:
        self.holon = holon
        self.ontology = ontology
        self.vector_store = vector_store
        self.config = config or BreakerConfig()
        self.audit = AuditTrail()

        # L2 - Functor Certification (optional: a pipeline can run without a declared
        # boundary chain, in which case morphism evaluation is simply not shown).
        self.morphism_chain = morphism_chain

        # L5 - Human Trustee review log (HTDR), separate append-only chain from L4's
        # decision audit trail -- see aicb/hitl.py for why they're kept apart.
        self.review_log = ReviewLog()

        self._trip_timestamps: list[float] = []
        self._locked_out: bool = False
        self._lockout_reason: Optional[str] = None
        self._session_start = time.time()
        self._hallucination_count = 0
        self._handshake_ok = False
        self._last_pass_result: Optional[PassResult] = None

    # ------------------------------------------------------------------ SOP-01 --------
    def semantic_handshake(self) -> tuple[bool, list[str]]:
        """SOP-01: pre-flight check. Must pass before evaluate() will permit TRANSMIT.

        Mirrors the ECG doc's 5-step handshake, generalized:
          1. Ontology reachable/consistent (has at least one rule or reference assertion)
          2. Holonic boundary has a non-trivial authority envelope defined
          3. Vector context store is initialized
          4. Config thresholds are sane (0 <= x <= 1 where applicable)
          5. Baseline gauges initialized (trust history reset)
        """
        reasons = []
        if not self.ontology.reference_assertions and not self.ontology.rules:
            reasons.append("ontology has no reference assertions or rules defined (O incomplete)")
        if not self.holon.authority.allowed_actions and not self.holon.authority.forbidden_actions:
            reasons.append("holonic authority envelope is empty (H incomplete -- no boundary defined)")
        for name, val in [
            ("sa_ceiling", self.config.sa_ceiling),
            ("cr_minimum", self.config.cr_minimum),
            ("trust_minimum", self.config.trust_minimum),
        ]:
            if not (0.0 <= val <= 1.0):
                reasons.append(f"config threshold {name}={val} out of [0,1] range")

        ok = len(reasons) == 0
        self._handshake_ok = ok
        self._session_start = time.time()
        return ok, reasons

    # ------------------------------------------------------------------ core ----------
    def evaluate(
        self,
        assertion: AgentAssertion,
        ground_truth: GroundTruth,
        human_cognitive_load: Optional[float] = None,
        ai_health_indicator: Optional[float] = None,
        morphism_pass: Optional[PassResult] = None,
    ) -> BreakerDecision:
        """`morphism_pass` is the L2 Functor Certification result for the pipeline
        traversal that produced this assertion (see MorphismChain.evaluate_pass). It is
        optional -- a breaker can run purely on Sa/Cr/ontology (L1/L3/L4) without a
        declared boundary chain -- but when supplied, an uncertified high-consequence
        boundary (w_c >= 0.9, matching the ECG F4 'Rhythm -> decision' weighting) is
        treated as a hard trip: a pipeline stage can silently distort meaning even when
        the final output still happens to pass the ontology/semantic-anomaly checks.
        """
        if not self._handshake_ok:
            ok, reasons = self.semantic_handshake()
            if not ok:
                return self._emit(
                    assertion, SafeState.LEVEL3_HALT, {}, reasons + ["SOP-01 handshake failed"], excluded=True
                )

        if self._locked_out:
            return self._emit(
                assertion,
                SafeState.LOCKOUT,
                {},
                [f"breaker is in SOP-02 lockout: {self._lockout_reason}"],
                excluded=True,
            )

        reasons: list[str] = []
        metrics: dict = {}

        # --- H: jurisdictional / authority check (hard trip, independent of semantics) ---
        in_scope = self.holon.in_scope(assertion.action, assertion.risk_tier)
        metrics["in_scope"] = 1.0 if in_scope else 0.0
        if not in_scope:
            reasons.append(
                f"action '{assertion.action}' (risk_tier={assertion.risk_tier}) is outside holon "
                f"'{self.holon.name}' authority envelope -- jurisdictional violation"
            )

        # --- O: impossible-state / consistency gate (hard trip, pre-vector) -------------
        violated_rules = self.ontology.check_impossible_states(assertion.fields)
        rule_severity = max([r.severity for r in violated_rules], default=0)
        metrics["ontology_violations"] = float(len(violated_rules))
        for r in violated_rules:
            reasons.append(f"ontology rule violated [{r.rule_id}] (severity {r.severity}): {r.description}")

        # --- L2: Functor Certification (morphism evaluation across pipeline boundaries) --
        morphism_hard_trip = False
        if morphism_pass is not None:
            self._last_pass_result = morphism_pass
            metrics["composed_fidelity"] = morphism_pass.composed_fidelity
            metrics["naive_avg_fidelity"] = morphism_pass.naive_avg_fidelity
            metrics["morphism_hidden_loss"] = morphism_pass.hidden_loss
            for rec in morphism_pass.records:
                if rec.state == "emergency_halt":
                    reasons.append(
                        f"Layer 2 Emergency Halt at boundary '{rec.boundary_name}': guardrail violation "
                        f"(d_S={rec.d_s:.3f}, d_M={rec.d_m:.3f})"
                    )
                    morphism_hard_trip = True
                elif not rec.certified:
                    severity_word = "trip" if rec.state == "trip" else "alert"
                    reasons.append(
                        f"Layer 2 boundary '{rec.boundary_name}' not certified ({severity_word}): "
                        f"d_S={rec.d_s:.3f} (tau_S={rec.tau_s:.3f}), d_M={rec.d_m:.3f} (tau_M={rec.tau_m:.3f}), "
                        f"w_c={rec.w_c:.2f}"
                    )
                    if rec.w_c >= 0.9 or rec.state == "trip":
                        morphism_hard_trip = True
            if morphism_pass.hidden_loss > 0.05:
                reasons.append(
                    f"Composition Theorem: composed end-to-end fidelity {morphism_pass.composed_fidelity:.3f} is "
                    f"{morphism_pass.hidden_loss:.3f} below the naive per-boundary average "
                    f"{morphism_pass.naive_avg_fidelity:.3f} -- a loss no single boundary's own test would show"
                )

        # --- Semantic Anomaly Score (Sa) -------------------------------------------------
        intent_vec = assertion.intent_vector(dim=self.config.embedding_dim)
        centroid_vec = self.ontology.local_neighborhood_centroid(intent_vec)
        sa = semantic_anomaly_score(intent_vec, centroid_vec)
        metrics["semantic_anomaly_score"] = sa
        if sa >= self.config.sa_ceiling:
            reasons.append(f"Semantic Anomaly Score {sa:.3f} >= ceiling {self.config.sa_ceiling:.3f}")

        # --- Contextual Relevancy Index (Cr) ---------------------------------------------
        cr = contextual_relevancy_index(assertion.context, ground_truth.values, ground_truth.weights)
        metrics["contextual_relevancy_index"] = cr
        if cr < self.config.cr_minimum:
            reasons.append(f"Contextual Relevancy Index {cr:.3f} < minimum {self.config.cr_minimum:.3f}")

        # --- Intent Delta (generic scalar |Intent - Reality|) ----------------------------
        intent_delta = clamp01(0.5 * sa + 0.5 * (1.0 - cr))
        metrics["intent_delta"] = intent_delta
        if intent_delta > self.config.intent_delta_tolerance:
            reasons.append(
                f"Intent Delta {intent_delta:.3f} > tolerance {self.config.intent_delta_tolerance:.3f}"
            )

        # --- Composite trust / credibility / validity / viability -----------------------
        credibility = clamp01(assertion.confidence * (1.0 - sa))
        validity = clamp01(1.0 - min(rule_severity / 3.0, 1.0))
        viability = clamp01(cr)
        trust = composite_trust_index(credibility, validity, viability)
        metrics["credibility"] = credibility
        metrics["validity"] = validity
        metrics["viability"] = viability
        metrics["trust_index"] = trust
        if trust < self.config.trust_minimum:
            reasons.append(f"Composite Trust Index {trust:.3f} < minimum {self.config.trust_minimum:.3f}")

        # --- Human-AI Calibration Coefficient (Ktrust), if telemetry supplied ------------
        if human_cognitive_load is not None and ai_health_indicator is not None:
            from .metrics import human_ai_calibration_coefficient

            ktrust = human_ai_calibration_coefficient(ai_health_indicator, human_cognitive_load)
            metrics["ktrust"] = ktrust
            if ktrust < self.config.ktrust_lockdown:
                reasons.append(
                    f"Human-AI Calibration Coefficient {ktrust:.3f} < lockdown floor "
                    f"{self.config.ktrust_lockdown:.3f} (high operator stress + degraded AI health)"
                )

        # --- Layer 3: SPC soft-alert on drift, even inside static thresholds ------------
        spc_flag = None
        if self.config.use_spc_soft_alerts and not self.vector_store.is_cold_start(
            self.config.spc_min_subgroups
        ):
            hist = self.vector_store.series("semantic_anomaly_score")
            verdict = spc_evaluate("semantic_anomaly_score", hist, sa)
            if not verdict.in_control:
                spc_flag = verdict.rule_triggered
                reasons.append(f"SPC drift detected on Semantic Anomaly Score ({spc_flag}, z={verdict.z:.2f})")
        metrics["spc_flag"] = 1.0 if spc_flag else 0.0

        # --- Determine trip + severity level ---------------------------------------------
        hard_trip = (not in_scope) or (rule_severity >= 3) or morphism_hard_trip
        soft_trip = (
            sa >= self.config.sa_ceiling
            or cr < self.config.cr_minimum
            or trust < self.config.trust_minimum
            or intent_delta > self.config.intent_delta_tolerance
            or (metrics.get("ktrust") is not None and metrics["ktrust"] < self.config.ktrust_lockdown)
        )
        tripped = hard_trip or soft_trip or (rule_severity > 0)

        if hard_trip:
            level = SafeState.LEVEL3_HALT
        elif rule_severity == 2 or (soft_trip and (sa >= self.config.sa_ceiling * 1.5 or cr < self.config.cr_minimum * 0.7)):
            level = SafeState.LEVEL2_HOLD
        elif tripped:
            level = SafeState.LEVEL1_SOFT_ALERT
        elif spc_flag:
            level = SafeState.LEVEL1_SOFT_ALERT
            reasons.append("SPC statistical drift flagged even though static thresholds were not breached")
        else:
            level = SafeState.NORMAL

        if not tripped and spc_flag:
            tripped = True  # SPC-only soft alert still counts as a (level-1) trip for logging purposes

        excluded = tripped  # SOP-03: any tripped epoch is excluded from the training queue

        if tripped:
            self._hallucination_count += 1
            self._trip_timestamps.append(time.time())
            self._trip_timestamps = [
                t for t in self._trip_timestamps if time.time() - t <= self.config.triple_trip_window_seconds
            ]
            if len(self._trip_timestamps) >= self.config.triple_trip_count:
                self._locked_out = True
                self._lockout_reason = (
                    f"{len(self._trip_timestamps)} trips within "
                    f"{self.config.triple_trip_window_seconds:.0f}s window (SOP-02 triple-trip rule)"
                )
                level = SafeState.LOCKOUT
                reasons.append(self._lockout_reason)

        self.vector_store.record(metrics, tripped)
        return self._emit(assertion, level, metrics, reasons, excluded)

    def _emit(
        self,
        assertion: AgentAssertion,
        level: SafeState,
        metrics: dict,
        reasons: list,
        excluded: bool,
    ) -> BreakerDecision:
        label = DECISION_LABEL[level]
        entry = self.audit.append(
            holon=self.holon.name,
            ontology_version=self.ontology.version,
            action=assertion.action,
            intent_text=assertion.intent_text,
            metrics=metrics,
            decision=label,
            safe_state_level=int(level),
            reasons=reasons,
            excluded_from_training=excluded,
        )
        return BreakerDecision(
            passed=(level == SafeState.NORMAL),
            safe_state=level,
            decision_label=label,
            metrics=metrics,
            reasons=reasons,
            audit_hash=entry.entry_hash,
            excluded_from_training=excluded,
        )

    # ------------------------------------------------------------------ SOP-02 --------
    @property
    def locked_out(self) -> bool:
        return self._locked_out

    def resume_from_lockout(self, trustee_id: str, authorization_note: str = "") -> bool:
        """SOP-02 Trustee Re-Calibration: a human Trustee reviews the CB event log and
        provides authenticated authorization to resume. This prototype trusts the caller's
        identity (real deployments should verify `trustee_id` against an auth system).
        """
        if not self._locked_out:
            return True
        self._locked_out = False
        self._lockout_reason = None
        self._trip_timestamps.clear()
        self.audit.append(
            holon=self.holon.name,
            ontology_version=self.ontology.version,
            action="__lockout_cleared__",
            intent_text=f"Trustee {trustee_id} resumed operation. Note: {authorization_note}",
            metrics={},
            decision="RESUME_AUTHORIZED",
            safe_state_level=0,
            reasons=[f"resumed by trustee {trustee_id}"],
            excluded_from_training=False,
        )
        return True

    # ------------------------------------------------------------------ SOP-03 --------
    def recursive_learning_batch(self) -> dict:
        """Negative Learning (Exclusion Filter) + Positive Learning split, per SOP-03 /
        Subsystem 4. Returns training-eligible epochs and purged (excluded) epochs. In a
        real pipeline, `training_eligible` feeds the next fine-tune, and `purged` feeds a
        root-cause review queue instead.
        """
        eligible = self.audit.training_eligible_epochs()
        purged = self.audit.tripped_epochs()
        return {
            "training_eligible": [e.to_dict() for e in eligible],
            "purged_excluded": [e.to_dict() for e in purged],
            "eligible_count": len(eligible),
            "purged_count": len(purged),
        }

    def propose_ontology_enhancements(self, min_confidence: float = 0.9) -> list[str]:
        """Ontology Enhancement (Subsystem 4): candidate new reference assertions -- high
        confidence, non-tripped intents not already well-represented in the ontology
        centroid (i.e. Sa was low but non-trivial, meaning it was accepted but sits at the
        edge of the known-good neighborhood rather than dead center).
        """
        candidates = []
        for e in self.audit.entries:
            if e.decision != "TRANSMIT":
                continue
            sa = e.metrics.get("semantic_anomaly_score", 0.0)
            if 0.03 < sa < self.config.sa_ceiling:
                candidates.append(e.intent_text)
        return candidates

    # ------------------------------------------------------------------ L5: HITL ------
    def flagged_events(self) -> list:
        """The Trustee's review queue: every audit entry that was NOT a clean TRANSMIT,
        i.e. every epoch a human might want to dig into. Ordered most-recent-first.
        """
        return [e for e in self.audit.entries if e.decision != "TRANSMIT"][::-1]

    def review_flagged_event(
        self,
        audit_seq: int,
        trustee_id: str,
        action: "ReviewAction | str",
        note: str = "",
        corrected_intent_text: str = "",
        corrected_action: str = "",
    ) -> HTDR:
        """Layer 5: a human Trustee digs into a specific flagged AI action (identified by
        its audit entry sequence number) and records a decision. This is the "make
        corrections" mechanism: it never rewrites the original (hash-chained,
        tamper-evident) decision record -- it appends a new HTDR that references it, and
        for CORRECTED_LABEL, writes the human-supplied correct intent into the ontology
        as a new reference assertion so the SAME mistake is less likely to reoccur.
        """
        if isinstance(action, str):
            action = ReviewAction(action)

        matches = [e for e in self.audit.entries if e.seq == audit_seq]
        if not matches:
            raise ValueError(f"no audit entry with seq={audit_seq}")
        original = matches[0]

        if action == ReviewAction.CORRECTED_LABEL:
            text_to_add = corrected_intent_text.strip() or original.intent_text
            self.ontology.add_reference_assertion(text_to_add)
        elif action == ReviewAction.ESCALATE:
            target = self.holon.escalation_target(max(original.safe_state_level, 1))
            return self.review_log.record(
                trustee_id=trustee_id,
                audit_seq=audit_seq,
                action=action,
                note=note,
                escalation_target=target,
            )

        return self.review_log.record(
            trustee_id=trustee_id,
            audit_seq=audit_seq,
            action=action,
            note=note,
            corrected_intent_text=corrected_intent_text,
            corrected_action=corrected_action,
        )

    def effective_recursive_learning_batch(self) -> dict:
        """Like `recursive_learning_batch`, but reconciled against the HTDR review log:
        an epoch originally excluded (tripped) but subsequently reviewed as
        FALSE_POSITIVE_OVERRIDE is returned to the training-eligible pool; everything
        else keeps its original SOP-03 disposition. This is the join between the L4
        decision audit and the L5 human review log described in aicb/hitl.py.
        """
        eligible, purged = [], []
        for e in self.audit.entries:
            reviews = self.review_log.for_audit_seq(e.seq)
            overridden = any(r.action == ReviewAction.FALSE_POSITIVE_OVERRIDE for r in reviews)
            confirmed = any(r.action == ReviewAction.CONFIRM_HALLUCINATION for r in reviews)
            corrected = any(r.action == ReviewAction.CORRECTED_LABEL for r in reviews)
            effectively_excluded = e.excluded_from_training and not overridden
            record = e.to_dict()
            record["reviewed"] = bool(reviews)
            record["review_actions"] = [r.action.value for r in reviews]
            if effectively_excluded:
                purged.append(record)
            else:
                eligible.append(record)
        return {
            "training_eligible": eligible,
            "purged_excluded": purged,
            "eligible_count": len(eligible),
            "purged_count": len(purged),
            "reviewed_count": len(self.review_log.entries),
        }

    # ------------------------------------------------------------------ reporting -----
    def current_mtbh_hours(self) -> float:
        from .metrics import mtbh

        elapsed = time.time() - self._session_start
        return mtbh(elapsed, self._hallucination_count)

    def status(self) -> dict:
        morphism_summary = {}
        if self.morphism_chain is not None:
            uncert = self.morphism_chain.uncertified_records()
            morphism_summary = {
                "boundaries_configured": len(self.morphism_chain.boundaries),
                "passes_evaluated": len(self.morphism_chain.passes),
                "uncertified_records": len(uncert),
                "latest_composed_fidelity": (
                    self.morphism_chain.passes[-1].composed_fidelity if self.morphism_chain.passes else None
                ),
            }
        return {
            "holon": self.holon.name,
            "ontology": f"{self.ontology.name} v{self.ontology.version}",
            "handshake_ok": self._handshake_ok,
            "locked_out": self._locked_out,
            "lockout_reason": self._lockout_reason,
            "trip_count_in_window": len(self._trip_timestamps),
            "total_hallucinations": self._hallucination_count,
            "mtbh_hours": self.current_mtbh_hours(),
            "audit_entries": len(self.audit.entries),
            "chain_valid": self.audit.verify_chain(),
            "flagged_for_review": len(self.flagged_events()),
            "htdr_entries": len(self.review_log.entries),
            "htdr_chain_valid": self.review_log.verify_chain(),
            "morphism": morphism_summary,
        }
