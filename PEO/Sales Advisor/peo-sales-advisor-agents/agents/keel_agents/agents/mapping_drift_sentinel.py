"""AG-15 Mapping Drift Sentinel - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-15"
TRIGGERS = ["com.insperity.keel.schema.changed","com.insperity.keel.schedule.daily"]
EMITS = ["com.insperity.keel.mapping.drift.detected"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Whether a mapping is degraded or broken. Options: OK · degraded · broken. "
        f"Event data: {event.get('data')}"
    )
