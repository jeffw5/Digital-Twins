"""AG-01 SharePoint Delta Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-01"
TRIGGERS = ["com.microsoft.graph.driveitem.changed","com.insperity.keel.schedule.nightly"]
EMITS = ["com.insperity.keel.content.item.changed"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which items changed and need reprocessing. Options: New · modified · moved · deleted · unchanged. "
        f"Event data: {event.get('data')}"
    )
