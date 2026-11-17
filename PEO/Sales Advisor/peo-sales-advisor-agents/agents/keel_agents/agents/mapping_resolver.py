"""AG-19 Mapping Resolver - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-19"
TRIGGERS = ["com.insperity.keel.facets.ranked"]
EMITS = ["com.insperity.keel.paths.resolved"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which mappings and source fields to read. Options: Released mapping paths. "
        f"Event data: {event.get('data')}"
    )
