"""AG-06 Content-Type Classifier - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-06"
TRIGGERS = ["com.insperity.keel.content.extracted"]
EMITS = ["com.insperity.keel.content.classified"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which content type an item is. Options: Content types above the confidence floor. "
        f"Event data: {event.get('data')}"
    )
