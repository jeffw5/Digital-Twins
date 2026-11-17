"""AG-16 Intent & RCB Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-16"
TRIGGERS = ["com.insperity.keel.advisor.question.asked"]
EMITS = ["com.insperity.keel.rcb.created"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which job step and context a question belongs to. Options: Intents, job steps, WHO…WHY values. "
        f"Event data: {event.get('data')}"
    )
