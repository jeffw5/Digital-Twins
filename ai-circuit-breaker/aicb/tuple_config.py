"""
The Governance Quad-Tuple (H, O, V, A)

Per Addendum A, the Circuit Breaker cannot be correctly instantiated from any subset of
four co-defined components:

  H - Holonic Boundary Definition  : this agent's authority envelope + escalation topology
  O - Domain Ontology              : formal rules / "impossible states" + reference vocabulary
  V - Vector Context Store         : live scenario context + historical decision baseline
  A - Domain Agent                 : the model/agent being governed (adapted, not rebuilt)

This module defines H, O, V as data structures. A is not a class here -- any callable can
be "A"; see insert.py for how arbitrary agents/models are adapted into the tuple.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

from .vectorize import embed, embed_many, centroid, cosine_similarity


# --------------------------------------------------------------------------------------
# H - Holonic Boundary Definition
# --------------------------------------------------------------------------------------

@dataclass
class AuthorityEnvelope:
    """What this agent (holon) is authorized to do unilaterally."""

    allowed_actions: set[str] = field(default_factory=set)
    forbidden_actions: set[str] = field(default_factory=set)
    max_risk_tier: int = 1  # 1 = low risk ... 3 = high risk requiring human co-sign

    def permits(self, action: str, risk_tier: int = 1) -> bool:
        if action in self.forbidden_actions:
            return False
        if self.allowed_actions and action not in self.allowed_actions:
            return False
        return risk_tier <= self.max_risk_tier


@dataclass
class HolonicBoundary:
    """H: this holon's scope of authority, escalation topology, and lateral interfaces.

    Without H, the breaker can measure "distance from the center of the domain" but has
    no definition of where the domain ends -- it can't tell "operating at the edge of my
    authority" (a proximity warning) from "operating outside my authority entirely"
    (a jurisdictional violation, which is a hard trip regardless of semantic distance).
    """

    name: str
    authority: AuthorityEnvelope
    escalation_topology: dict[int, str] = field(
        default_factory=lambda: {1: "operator", 2: "on_call_trustee", 3: "governance_board"}
    )
    parent_holon: Optional[str] = None
    lateral_holons: list[str] = field(default_factory=list)

    def in_scope(self, action: str, risk_tier: int = 1) -> bool:
        return self.authority.permits(action, risk_tier)

    def escalation_target(self, level: int) -> str:
        return self.escalation_topology.get(level, self.escalation_topology.get(3, "governance_board"))


# --------------------------------------------------------------------------------------
# O - Domain Ontology
# --------------------------------------------------------------------------------------

@dataclass
class OntologyRule:
    """A hard-coded 'impossible state' constraint (the OWL/SHACL rule in the source docs,
    simplified to a Python predicate for the prototype). `predicate` returns True when the
    assertion VIOLATES the rule (i.e. describes something that cannot physically/logically
    be true), mirroring the ECG examples: 'HR > 300 bpm without pre-excitation', etc.
    """

    rule_id: str
    description: str
    predicate: Callable[[dict], bool]
    severity: int = 3  # 1 soft alert, 2 hold, 3 halt -- matches Safe State levels


@dataclass
class DomainOntology:
    """O: the formal semantic representation of the domain -- vocabulary, reference
    ("known-good") assertions used to compute the valid-state centroid, and hard
    constraint rules that define impossible states.
    """

    name: str
    version: str = "1.0.0"
    vocabulary: set[str] = field(default_factory=set)
    reference_assertions: list[str] = field(default_factory=list)
    rules: list[OntologyRule] = field(default_factory=list)
    local_neighborhood_k: int = 3
    embedding_dim: int = 256
    _centroid_cache: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _ref_embedding_cache: Optional[np.ndarray] = field(default=None, init=False, repr=False)

    def centroid_vector(self) -> np.ndarray:
        """The global 'center of gravity' of all known-good/safe states. Only meaningful
        when the reference set is a single tight cluster; for multi-topic domains (most
        real ones) prefer `local_neighborhood_centroid()` below, which is what the
        breaker actually uses for Sa. Kept for callers that want a single fixed reference
        vector (e.g. a coarse pre-filter). Cached because reference_assertions rarely
        change at runtime (they change via the Recursive Learning / Ontology Enhancement
        pipeline).
        """
        if self._centroid_cache is None or self._centroid_cache.shape[0] != self.embedding_dim:
            self._centroid_cache = centroid(self.reference_assertions, dim=self.embedding_dim)
        return self._centroid_cache

    def _reference_embeddings(self) -> np.ndarray:
        if (
            self._ref_embedding_cache is None
            or self._ref_embedding_cache.shape[0] != len(self.reference_assertions)
            or (self._ref_embedding_cache.shape[1] != self.embedding_dim if self._ref_embedding_cache.size else False)
        ):
            if self.reference_assertions:
                self._ref_embedding_cache = embed_many(self.reference_assertions, dim=self.embedding_dim)
            else:
                self._ref_embedding_cache = np.zeros((0, self.embedding_dim))
        return self._ref_embedding_cache

    def local_neighborhood_centroid(
        self, query_vector: np.ndarray, k: Optional[int] = None, sharpness: float = 4.0
    ) -> np.ndarray:
        """No: the 'Local Semantic Neighborhood' -- the cluster of known-good reference
        states that surround the CURRENT operation, per the design spec ("the cluster of
        valid nodes ... that surround the current operation"). Computed as a
        similarity-weighted centroid over the k nearest reference assertions, rather than
        an unweighted centroid of the entire (possibly multi-topic) reference set or a
        flat average of the top-k -- this avoids diluting similarity for domains whose
        valid states form several distinct sub-clusters (e.g. "reroute traffic" vs "adjust
        power" are both valid but semantically distant from each other), and avoids
        letting a mediocre k-th neighbor drag down a near-exact top match. `sharpness`
        controls how strongly nearer neighbors dominate the weighted centroid (higher =
        closer to pure nearest-neighbor).
        """
        refs = self._reference_embeddings()
        if refs.shape[0] == 0:
            return np.zeros(self.embedding_dim, dtype=np.float64)
        k = k or self.local_neighborhood_k
        k = max(1, min(k, refs.shape[0]))
        sims = refs @ query_vector
        top_idx = np.argsort(-sims)[:k]
        top_sims = sims[top_idx]
        weights = np.clip(top_sims, 0.0, None) ** sharpness
        if weights.sum() <= 0:
            weights = np.ones_like(top_sims)
        local = (refs[top_idx] * weights[:, None]).sum(axis=0) / weights.sum()
        norm = np.linalg.norm(local)
        if norm > 0:
            local = local / norm
        return local

    def invalidate_centroid_cache(self) -> None:
        self._centroid_cache = None
        self._ref_embedding_cache = None

    def add_reference_assertion(self, text: str) -> None:
        """Ontology Enhancement: append a verified new known-good state. Called by the
        Recursive Learning pipeline (breaker.recursive_learning_batch) after a batch of
        non-tripped, high-confidence assertions is reviewed.
        """
        self.reference_assertions.append(text)
        self.invalidate_centroid_cache()

    def check_impossible_states(self, assertion: dict) -> list[OntologyRule]:
        """SHACL-style consistency gate. Returns all violated rules. Ontologically invalid
        but *internally consistent* assertions (the kind vector distance alone would miss)
        are caught here, before semantic-distance scoring even runs.
        """
        violated = []
        for rule in self.rules:
            try:
                if rule.predicate(assertion):
                    violated.append(rule)
            except Exception:
                # A malformed assertion that crashes a rule predicate is itself a
                # governance-relevant event -- treat as a violation of that rule.
                violated.append(rule)
        return violated


# --------------------------------------------------------------------------------------
# V - Vector Context Store
# --------------------------------------------------------------------------------------

@dataclass
class GroundTruth:
    """Sensor / environmental ground truth for a single evaluation -- Sgt in the design
    spec. Keys are environmental variable names (arbitrary per domain), values in [0, 1].
    `weights` lets each variable carry a different importance in the Contextual Relevancy
    Index (Cr) computation.
    """

    values: dict[str, float] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    captured_at: float = field(default_factory=time.time)


@dataclass
class _HistoricalRecord:
    timestamp: float
    metrics: dict[str, float]
    tripped: bool


@dataclass
class VectorContextStore:
    """V: the dynamic, scenario-specific store. Holds:
      - the historical decision distribution (behavioral baseline for SPC control limits)
      - the current live scenario context (Cm) used for Contextual Relevancy scoring

    Without V, the breaker evaluates every action against the same static standard
    regardless of scenario, and SPC control limits have no empirical basis -- they'd be
    theoretical numbers rather than measured ones.
    """

    name: str
    max_history: int = 500
    history: list[_HistoricalRecord] = field(default_factory=list)

    def record(self, metrics: dict[str, float], tripped: bool) -> None:
        self.history.append(_HistoricalRecord(time.time(), dict(metrics), tripped))
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def series(self, metric_name: str) -> list[float]:
        return [r.metrics[metric_name] for r in self.history if metric_name in r.metrics]

    def baseline_mean_std(self, metric_name: str) -> tuple[float, float]:
        vals = self.series(metric_name)
        if len(vals) < 2:
            return (float("nan"), float("nan"))
        arr = np.array(vals, dtype=np.float64)
        return float(arr.mean()), float(arr.std(ddof=1))

    def trip_count_since(self, since_ts: float) -> int:
        return sum(1 for r in self.history if r.tripped and r.timestamp >= since_ts)

    def is_cold_start(self, min_subgroups: int = 25) -> bool:
        """Phase I cold-start target from the abstract: SPC thresholds are not considered
        data-derived/calibrated until at least `min_subgroups` observations exist."""
        return len(self.history) < min_subgroups


# --------------------------------------------------------------------------------------
# A - Domain Agent output, standardized
# --------------------------------------------------------------------------------------

@dataclass
class AgentAssertion:
    """Standardized shape that any wrapped model/agent output is normalized into before
    it reaches the breaker. This is the adapter boundary -- see insert.py for helpers
    that build this from raw LLM/agent outputs.
    """

    intent_text: str
    action: str
    confidence: float = 1.0
    risk_tier: int = 1
    context: dict[str, float] = field(default_factory=dict)
    fields: dict = field(default_factory=dict)  # arbitrary structured fields for ontology rules
    raw_output: object = None

    def intent_vector(self, dim: int = 256) -> np.ndarray:
        return embed(self.intent_text, dim=dim)
