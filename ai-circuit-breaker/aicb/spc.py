"""
Layer 3 - Statistical Control.

Turns raw metric measurements into verdicts using Statistical Process Control (SPC)
instead of guessed static thresholds where possible. Implements a subset of the Western
Electric rules for detecting drift in a metric's time series, per the abstract's "Layer
3, Statistical Control ... thresholds are data-derived through SPC rather than guessed."

During "cold start" (fewer than `min_subgroups` observations, default 25 per the
abstract's Phase I target), there isn't enough history for a meaningful control chart, so
callers should fall back to the static engineered thresholds in BreakerConfig. Once
past cold start, this module's `evaluate()` can additionally flag statistically
significant drift even when a value hasn't crossed the static (hard) threshold yet --
this is what powers the Level-1 "soft alert" tier.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SPCVerdict:
    metric: str
    value: float
    mean: float
    std: float
    z: float
    rule_triggered: str | None
    in_control: bool


def _zscores(values: list[float], mean: float, std: float) -> list[float]:
    if std <= 0:
        return [0.0 for _ in values]
    return [(v - mean) / std for v in values]


def western_electric_check(recent_values: list[float], mean: float, std: float) -> str | None:
    """Check a handful of Western Electric rules against the tail of a series.
    `recent_values` should be ordered oldest -> newest, most recent value last.
    Returns the name of the first triggered rule, or None if the process looks in control.
    """
    if std <= 0 or len(recent_values) == 0:
        return None

    z = _zscores(recent_values, mean, std)

    # Rule 1: any single point beyond 3 sigma
    if abs(z[-1]) > 3:
        return "rule1_beyond_3sigma"

    # Rule 2: 2 of the last 3 points beyond 2 sigma on the same side
    last3 = z[-3:]
    if len(last3) == 3:
        pos = sum(1 for v in last3 if v > 2)
        neg = sum(1 for v in last3 if v < -2)
        if pos >= 2 or neg >= 2:
            return "rule2_two_of_three_beyond_2sigma"

    # Rule 3: 4 of the last 5 points beyond 1 sigma on the same side
    last5 = z[-5:]
    if len(last5) == 5:
        pos = sum(1 for v in last5 if v > 1)
        neg = sum(1 for v in last5 if v < -1)
        if pos >= 4 or neg >= 4:
            return "rule3_four_of_five_beyond_1sigma"

    # Rule 4: 8 consecutive points on the same side of the mean
    last8 = z[-8:]
    if len(last8) == 8:
        if all(v > 0 for v in last8) or all(v < 0 for v in last8):
            return "rule4_eight_consecutive_same_side"

    return None


def evaluate(metric_name: str, history: list[float], current_value: float) -> SPCVerdict:
    """Evaluate `current_value` (already appended as the last element of `history`, or
    pass history WITHOUT current_value and this function will append it) against the
    control-chart state derived from `history`.
    """
    series = list(history)
    if not series or series[-1] != current_value:
        series = series + [current_value]

    if len(series) < 2:
        return SPCVerdict(metric_name, current_value, current_value, 0.0, 0.0, None, True)

    import numpy as np

    arr = np.array(series[:-1], dtype=np.float64)  # baseline excludes current point
    mean = float(arr.mean())
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    z = 0.0 if std <= 0 else (current_value - mean) / std

    rule = western_electric_check(series, mean, std)
    return SPCVerdict(
        metric=metric_name,
        value=current_value,
        mean=mean,
        std=std,
        z=z,
        rule_triggered=rule,
        in_control=(rule is None),
    )
