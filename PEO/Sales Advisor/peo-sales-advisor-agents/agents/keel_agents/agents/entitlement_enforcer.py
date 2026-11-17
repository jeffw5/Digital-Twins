"""AG-11 Entitlement Enforcer - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-11"
TRIGGERS = ["com.insperity.keel.brief.drafted"]
EMITS = ["com.insperity.keel.brief.entitled"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Allow, redact or deny each part for a persona. Options: Allow · redact · deny. "
        f"Event data: {event.get('data')}"
    )
