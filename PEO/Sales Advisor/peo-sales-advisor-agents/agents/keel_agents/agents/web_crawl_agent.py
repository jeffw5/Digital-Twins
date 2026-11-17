"""AG-02 Web Crawl Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-02"
TRIGGERS = ["com.insperity.keel.schedule.crawl"]
EMITS = ["com.insperity.keel.content.item.changed"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Fetch, skip or store a page and its changed blocks. Options: Fetch · skip (robots or licence) · store diff. "
        f"Event data: {event.get('data')}"
    )
