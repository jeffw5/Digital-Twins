"""
Layer 2 - Functor Certification (Morphism Evaluation).

Implements the two-axis morphism quality framework from "Morphism-Grounded
Compositional Assurance" (TB-03 / Fig. 3) and the multi-boundary chain pattern from
TB-04 (Fig. 4, the ECG F1-F4 example), generalized to any multi-stage agent pipeline.

Concepts, mapped 1:1 onto the source document:

  Boundary (F_i)         a transformation/handoff between two stages of the agent
                          pipeline (e.g. sensing -> features -> classification -> decision).
                          Each boundary has its own engineering tolerances (tau_S,
                          tau_M) and consequence weight (w_c) -- boundaries closer to
                          the final decision are tighter and weighted higher, exactly
                          as in the ECG F1 (0.25/0.20, w_c=0.3) -> F4 (0.04/0.03, w_c=1.0)
                          progression.

  d_S (structural dist.) how much the *shape* of the representation changed crossing
                          the boundary (approximated here by a normalized distance over
                          a small set of named structural features -- a lightweight
                          stand-in for the graph-edit-distance metric in TB-03).

  d_M (semantic dist.)    how much the *meaning* changed crossing the boundary (cosine
                          distance between domain-encoder embeddings, using the same
                          deterministic embedding used elsewhere in this package).

  Functor Certification   a boundary is "certified" iff d_S <= tau_S AND d_M <= tau_M.
                          An uncertified boundary is a Layer 2 finding independent of
                          whatever Layer 3/4 (ontology + trip logic) conclude -- a
                          pipeline stage can silently distort meaning even when the
                          final output still happens to pass semantic-anomaly checks.

  Composition Theorem     fidelity degrades MULTIPLICATIVELY across a chain of
                          boundaries: phi(Fn o ... o F1) >= prod(phi(Fi)). A pipeline
                          with four boundaries each individually "passing" at 0.95
                          fidelity is only 0.81 end-to-end -- a 19% loss invisible to
                          any single per-boundary test. `PassResult` computes both the
                          composed (correct) fidelity and the naive average (the number
                          per-boundary dashboards usually show) so the gap is visible.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .vectorize import embed, cosine_similarity


def structural_distance(before: dict[str, float], after: dict[str, float]) -> float:
    """Normalized distance between two structural-feature snapshots (a lightweight
    stand-in for normalized graph-edit-distance). Each feature is compared as a
    fraction of its own magnitude so differently-scaled features (node counts vs.
    boolean flags) contribute comparably.
    """
    keys = set(before.keys()) | set(after.keys())
    if not keys:
        return 0.0
    diffs = []
    for k in keys:
        b = before.get(k, 0.0)
        a = after.get(k, 0.0)
        scale = max(abs(b), abs(a), 1.0)
        diffs.append(abs(a - b) / scale)
    return float(min(max(sum(diffs) / len(diffs), 0.0), 1.0))


def semantic_distance(before, after, dim: int = 256) -> float:
    """d_M: cosine distance between two representations. Accepts either raw text
    (embedded with the package's deterministic hashing transform) or precomputed
    vectors.
    """
    bv = embed(before, dim=dim) if isinstance(before, str) else before
    av = embed(after, dim=dim) if isinstance(after, str) else after
    return float(min(max(1.0 - cosine_similarity(bv, av), 0.0), 1.0))


@dataclass
class Boundary:
    """F_i: one transformation boundary in the agent's pipeline."""

    boundary_id: str
    name: str
    tau_s: float           # structural distance tolerance
    tau_m: float           # semantic distance tolerance
    w_c: float             # consequence weight in [0,1] -- how costly a violation here is
    description: str = ""
    trip_multiplier: float = 1.5  # per TB-02: CB trips at 1.5x tau (Alert below this line)


@dataclass
class MorphismEvaluationRecord:
    """MER -- Morphism Evaluation Record. Written every L2 evaluation cycle per the
    provenance mapping in TB-06 (Fig. 7): retained for the operational lifetime + 7yr,
    satisfying NIST AI RMF's Measure function.
    """

    seq: int
    timestamp: float
    pass_id: str
    boundary_id: str
    boundary_name: str
    d_s: float
    d_m: float
    tau_s: float
    tau_m: float
    w_c: float
    certified: bool
    state: str          # "normal" | "alert" | "trip" | "emergency_halt"
    fidelity: float      # phi_i = 1 - d_m, this boundary's contribution to composed fidelity
    notes: str = ""

    def to_dict(self) -> dict:
        return dict(
            seq=self.seq, timestamp=self.timestamp, pass_id=self.pass_id,
            boundary_id=self.boundary_id, boundary_name=self.boundary_name,
            d_s=self.d_s, d_m=self.d_m, tau_s=self.tau_s, tau_m=self.tau_m, w_c=self.w_c,
            certified=self.certified, state=self.state, fidelity=self.fidelity, notes=self.notes,
        )


@dataclass
class PassResult:
    """One full traversal of the pipeline (one 'pass'): every boundary evaluated once."""

    pass_id: str
    records: list[MorphismEvaluationRecord]
    composed_fidelity: float     # correct: product of per-boundary fidelities
    naive_avg_fidelity: float    # what a per-layer-only dashboard would show
    all_certified: bool
    worst_boundary: Optional[str]

    @property
    def hidden_loss(self) -> float:
        """The gap the Composition Theorem exists to expose: how much worse the true
        end-to-end fidelity is than the naive per-layer average would suggest."""
        return max(self.naive_avg_fidelity - self.composed_fidelity, 0.0)


class MorphismChain:
    """L2 Functor Certification: the ordered set of boundaries an agent's pipeline
    crosses, plus the running log of MER evaluations across all passes.
    """

    def __init__(self, boundaries: list[Boundary]) -> None:
        self.boundaries = boundaries
        self._by_id = {b.boundary_id: b for b in boundaries}
        self.records: list[MorphismEvaluationRecord] = []
        self.passes: list[PassResult] = []

    def _state_for(self, boundary: Boundary, d_s: float, d_m: float) -> str:
        over_s = d_s / boundary.tau_s if boundary.tau_s > 0 else 0.0
        over_m = d_m / boundary.tau_m if boundary.tau_m > 0 else 0.0
        worst_ratio = max(over_s, over_m)
        if worst_ratio >= boundary.trip_multiplier:
            return "trip"
        if worst_ratio >= 1.0:
            return "alert"
        return "normal"

    def evaluate_pass(
        self,
        pass_id: str,
        measurements: dict[str, tuple[float, float]],
        emergency_halt_boundaries: Optional[set[str]] = None,
    ) -> PassResult:
        """`measurements` maps boundary_id -> (d_s, d_m) for this single traversal of
        the pipeline. `emergency_halt_boundaries` lets a caller force a guardrail-style
        Emergency Halt on a boundary regardless of its distance scores (e.g. an
        ontology impossible-state was detected at that stage) -- matches TB-02's
        "Emergency Halt on guardrail violation" being independent of the SPC/threshold
        trip path.
        """
        emergency_halt_boundaries = emergency_halt_boundaries or set()
        records = []
        for b in self.boundaries:
            if b.boundary_id not in measurements:
                continue
            d_s, d_m = measurements[b.boundary_id]
            certified = d_s <= b.tau_s and d_m <= b.tau_m
            state = "emergency_halt" if b.boundary_id in emergency_halt_boundaries else self._state_for(b, d_s, d_m)
            fidelity = float(min(max(1.0 - d_m, 0.0), 1.0))
            seq = len(self.records)
            rec = MorphismEvaluationRecord(
                seq=seq,
                timestamp=time.time(),
                pass_id=pass_id,
                boundary_id=b.boundary_id,
                boundary_name=b.name,
                d_s=d_s,
                d_m=d_m,
                tau_s=b.tau_s,
                tau_m=b.tau_m,
                w_c=b.w_c,
                certified=certified,
                state=state,
                fidelity=fidelity,
            )
            self.records.append(rec)
            records.append(rec)

        if records:
            composed = float(np.prod([r.fidelity for r in records]))
            naive_avg = float(np.mean([r.fidelity for r in records]))
            all_certified = all(r.certified for r in records)
            worst = min(records, key=lambda r: r.fidelity).boundary_name
        else:
            composed = naive_avg = 1.0
            all_certified = True
            worst = None

        result = PassResult(
            pass_id=pass_id,
            records=records,
            composed_fidelity=composed,
            naive_avg_fidelity=naive_avg,
            all_certified=all_certified,
            worst_boundary=worst,
        )
        self.passes.append(result)
        return result

    def latest_state_by_boundary(self) -> dict[str, MorphismEvaluationRecord]:
        latest: dict[str, MorphismEvaluationRecord] = {}
        for r in self.records:
            latest[r.boundary_id] = r  # records are appended in order, so last wins
        return latest

    def uncertified_records(self) -> list[MorphismEvaluationRecord]:
        return [r for r in self.records if not r.certified]
