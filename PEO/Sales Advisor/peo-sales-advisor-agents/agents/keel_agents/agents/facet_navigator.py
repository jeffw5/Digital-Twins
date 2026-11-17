"""AG-18 Facet Navigator - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-18"
TRIGGERS = ["com.insperity.keel.query.planned"]
EMITS = ["com.insperity.keel.facets.ranked"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: How to rank facets. Options: Facet orderings. "
        f"Event data: {event.get('data')}"
    )
