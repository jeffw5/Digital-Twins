"""AG-17 Federated Query Planner - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-17"
TRIGGERS = ["com.insperity.keel.rcb.created"]
EMITS = ["com.insperity.keel.query.planned"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: How to scope and plan the query. Options: Query plans within the context bundle. "
        f"Event data: {event.get('data')}"
    )
