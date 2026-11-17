"""AG-03 Feed Listener Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-03"
TRIGGERS = ["com.insperity.keel.feed.item.received"]
EMITS = ["com.insperity.keel.content.item.changed"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Accept, normalize or reject a feed item. Options: Accept · normalize · reject · hold. "
        f"Event data: {event.get('data')}"
    )
