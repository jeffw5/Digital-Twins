"""
Trustworthiness Metrology -- implements the measures defined in
"AI Circuit Breaker: Section 2 - Trustworthiness Metrology & Semantic Governance".

All functions are pure and side-effect free so they can be unit tested and reused
outside the breaker (e.g. for offline analysis of historical logs).
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from .vectorize import cosine_similarity


def semantic_anomaly_score(intent_vector: np.ndarray, ontology_centroid: np.ndarray) -> float:
    """Sa = 1 - cos(I, No)

    Quantifies logical divergence between the AI-proposed intent (I) and the centroid of
    the valid ontological state space (No). Output in [0, 2] theoretically for arbitrary
    vectors; clipped to [0, 1] here since both inputs are L2-normalized embeddings and in
    practice cosine similarity of semantically related text rarely goes negative enough
    to matter. Tolerance per spec: Sa < 0.15 (trip if >= 0.15).
    """
    sim = cosine_similarity(intent_vector, ontology_centroid)
    sa = 1.0 - sim
    return float(min(max(sa, 0.0), 1.0))


def contextual_relevancy_index(
    context_model: dict[str, float],
    sensor_ground_truth: dict[str, float],
    weights: Optional[dict[str, float]] = None,
) -> float:
    """Cr = sum_i( w_i * (1 - |Cm_i - Sgt_i|) )

    Evaluates whether the AI's internal situational model (Cm) is grounded in real-time
    environmental / sensor data (Sgt). Only keys present in BOTH dicts are scored; if a
    variable the ground truth tracks is entirely absent from the AI's context model, it
    is scored as maximally ungrounded (Cm_i treated as 0 distance-from-worst, i.e.
    contributes 0 to Cr) -- silently ignoring unknown context is exactly the failure mode
    this metric exists to catch.

    Weights default to uniform over the union of tracked variables. Output in [0, 1].
    Tolerance per spec: Cr > 0.85 (below forces Conservative Safe State); the ECG profile
    in the technical design doc uses a domain-specific CRI_Minimum of 0.60 -- thresholds
    are configurable per BreakerConfig, this function just computes the raw score.
    """
    all_keys = set(sensor_ground_truth.keys()) | set(context_model.keys())
    if not all_keys:
        return 1.0

    if weights is None:
        weights = {k: 1.0 / len(all_keys) for k in all_keys}
    else:
        total = sum(weights.get(k, 0.0) for k in all_keys)
        if total <= 0:
            weights = {k: 1.0 / len(all_keys) for k in all_keys}
        else:
            weights = {k: weights.get(k, 0.0) / total for k in all_keys}

    score = 0.0
    for k in all_keys:
        sgt = sensor_ground_truth.get(k)
        cm = context_model.get(k)
        if sgt is None or cm is None:
            # Missing ground truth or missing AI context both count as zero-grounding
            # contribution for that variable.
            contribution = 0.0
        else:
            contribution = 1.0 - abs(cm - sgt)
        score += weights[k] * contribution

    return float(min(max(score, 0.0), 1.0))


def mtbh(total_operational_seconds: float, hallucination_count: int) -> float:
    """MTBH = Tops / Nh, returned in hours.

    Primary longitudinal reliability metric. If Nh == 0, MTBH is reported as the full
    operational duration (i.e. "no hallucinations observed yet in Tops hours") rather
    than infinity, so it stays plottable on a dashboard.
    """
    hours = total_operational_seconds / 3600.0
    if hallucination_count <= 0:
        return hours
    return hours / hallucination_count


def human_ai_calibration_coefficient(ai_health_indicator: float, human_cognitive_load: float) -> float:
    """Ktrust = Hai / Lh

    Sensitivity multiplier for breaker thresholds. Lh is clamped away from zero to avoid
    a division blow-up when cognitive load telemetry is (momentarily) unavailable/zero;
    per spec, Ktrust < 0.5 (high stress + low AI health) triggers autonomous lockdown.
    """
    lh = max(human_cognitive_load, 1e-6)
    return float(ai_health_indicator / lh)


def value_drift_coefficient(current_vector: np.ndarray, baseline_vector: np.ndarray) -> float:
    """VDC: distance between the current agent behavior and the original, validated
    baseline intent, expressed as 1 - cosine similarity (same units as Sa so the two are
    directly comparable on the dashboard). Used for SOP-02's rolling drift check.
    """
    sim = cosine_similarity(current_vector, baseline_vector)
    return float(min(max(1.0 - sim, 0.0), 1.0))


def composite_trust_index(
    credibility: float,
    validity: float,
    viability: float,
    weights: tuple[float, float, float] = (0.35, 0.40, 0.25),
) -> float:
    """Overall Trust = Credibility*0.35 + Validity*0.40 + Viability*0.25 (Trust Metrology
    Dashboard weighting from the ECG technical design doc, generalized as the default).

    credibility: AI output accuracy relative to a review/consensus baseline, in [0,1].
    validity:    ontological consistency of AI output (1 - normalized rule-violation
                 severity), in [0,1].
    viability:   operational health of the sensing/context subsystem (derived from Cr
                 and any subsystem health flags), in [0,1].
    """
    wc, wv, wb = weights
    total_w = wc + wv + wb
    if total_w <= 0:
        wc, wv, wb, total_w = 0.35, 0.40, 0.25, 1.0
    score = (credibility * wc + validity * wv + viability * wb) / total_w
    return float(min(max(score, 0.0), 1.0))


def clamp01(x: float) -> float:
    if math.isnan(x):
        return 0.0
    return min(max(x, 0.0), 1.0)
