"""AG-35 Effect Estimator - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-35"
TRIGGERS = ["com.insperity.keel.causal.graph.updated"]
EMITS = ["com.insperity.keel.effect.estimated"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Size and interval of an effect. Options: Estimators and intervals. "
        f"Event data: {event.get('data')}"
    )
