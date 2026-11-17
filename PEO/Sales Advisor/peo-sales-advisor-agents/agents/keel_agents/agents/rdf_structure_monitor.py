"""AG-30 RDF Structure Monitor - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-30"
TRIGGERS = ["com.insperity.keel.content.published"]
EMITS = ["com.insperity.keel.change.detected"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Whether a shape or graph change is breaking. Options: Breaking · compatible · none. "
        f"Event data: {event.get('data')}"
    )
