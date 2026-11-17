"""AG-21 Brief Assembler - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-21"
TRIGGERS = ["com.insperity.keel.claims.selected"]
EMITS = ["com.insperity.keel.brief.drafted"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which statements and decision options to present, and in what order. Options: Decision options allowed by the rules, with effects and outcomes. "
        f"Event data: {event.get('data')}"
    )
