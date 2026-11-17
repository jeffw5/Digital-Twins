"""AG-32 Incremental Refresh Service - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-32"
TRIGGERS = ["com.insperity.keel.impact.assessed"]
EMITS = ["com.insperity.keel.refresh.started"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which stages to re-run. Options: Stage subsets. "
        f"Event data: {event.get('data')}"
    )
