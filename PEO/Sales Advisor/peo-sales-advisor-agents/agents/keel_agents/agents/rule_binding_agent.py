"""AG-13 Rule Binding Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-13"
TRIGGERS = ["com.insperity.keel.claims.scoped"]
EMITS = ["com.insperity.keel.claims.bound"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which SSOT rule a regulatory claim binds to. Options: Candidate rules. "
        f"Event data: {event.get('data')}"
    )
