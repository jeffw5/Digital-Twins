"""AG-04 Identity Resolver - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-04"
TRIGGERS = ["com.insperity.keel.content.item.changed"]
EMITS = ["com.insperity.keel.identity.resolved"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Match to an existing URI or mint a new one. Options: Match · mint · hold for steward. "
        f"Event data: {event.get('data')}"
    )
