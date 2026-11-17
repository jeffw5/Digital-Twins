"""AG-23 Grounding Guard (MTBH) - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-23"
TRIGGERS = ["com.insperity.keel.brief.entitled"]
EMITS = ["com.insperity.keel.brief.released","com.insperity.keel.brief.held"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Pass, hold or block a draft brief. Options: Pass · hold for review · block. "
        f"Event data: {event.get('data')}"
    )
