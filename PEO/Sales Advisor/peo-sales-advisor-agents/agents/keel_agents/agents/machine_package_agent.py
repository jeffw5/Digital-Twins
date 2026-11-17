"""AG-22 Machine Package Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-22"
TRIGGERS = ["com.insperity.keel.brief.released"]
EMITS = ["com.insperity.keel.package.created"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: What goes into the JSON-LD package. Options: Claims and fields for the receiving system. "
        f"Event data: {event.get('data')}"
    )
