"""AG-29 Semantic Change Monitor - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-29"
TRIGGERS = ["com.insperity.keel.ssot.rule.released"]
EMITS = ["com.insperity.keel.change.detected"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which concepts and rules a KGCL change touches. Options: Changed concepts and rules. "
        f"Event data: {event.get('data')}"
    )
