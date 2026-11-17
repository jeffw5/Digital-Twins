"""AG-28 Content Change Monitor - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-28"
TRIGGERS = ["com.insperity.keel.content.item.changed"]
EMITS = ["com.insperity.keel.change.detected"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Whether a delta is a material change. Options: Material · cosmetic · none. "
        f"Event data: {event.get('data')}"
    )
