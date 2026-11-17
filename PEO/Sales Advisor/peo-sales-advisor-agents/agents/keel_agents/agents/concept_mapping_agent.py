"""AG-12 Concept Mapping Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-12"
TRIGGERS = ["com.insperity.keel.claims.scoped"]
EMITS = ["com.insperity.keel.mapping.proposed"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which concept a claim or field maps to. Options: Exact · close · broad · related matches. "
        f"Event data: {event.get('data')}"
    )
