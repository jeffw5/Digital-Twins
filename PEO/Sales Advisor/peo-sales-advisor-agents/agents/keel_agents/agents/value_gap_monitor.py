"""AG-26 Value-Gap Monitor - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-26"
TRIGGERS = ["com.insperity.keel.schedule.daily"]
EMITS = ["com.insperity.keel.valuegap.detected"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Gap, no gap, or not enough data. Options: Gap · met · insufficient data. "
        f"Event data: {event.get('data')}"
    )
