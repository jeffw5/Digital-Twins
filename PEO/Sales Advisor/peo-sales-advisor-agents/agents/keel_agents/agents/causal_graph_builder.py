"""AG-34 Causal Graph Builder - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-34"
TRIGGERS = ["com.insperity.keel.schedule.weekly"]
EMITS = ["com.insperity.keel.causal.graph.updated"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which causal edges to assert. Options: Candidate edges with assumptions. "
        f"Event data: {event.get('data')}"
    )
