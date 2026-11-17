"""AG-07 Persona & Job-Step Tagger - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-07"
TRIGGERS = ["com.insperity.keel.content.classified"]
EMITS = ["com.insperity.keel.content.tagged"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which personas and job steps an item serves. Options: Persona × job-step candidates. "
        f"Event data: {event.get('data')}"
    )
