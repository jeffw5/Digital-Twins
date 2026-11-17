"""AG-37 Counterfactual Explainer - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-37"
TRIGGERS = ["com.insperity.keel.ranking.updated"]
EMITS = ["com.insperity.keel.counterfactual.explained"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which what-if to explain. Options: What-if narratives. "
        f"Event data: {event.get('data')}"
    )
