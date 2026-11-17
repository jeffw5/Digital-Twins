"""AG-20 Precision Extractor - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-20"
TRIGGERS = ["com.insperity.keel.paths.resolved"]
EMITS = ["com.insperity.keel.claims.selected"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which claims answer the job step. Options: Keep · drop per claim. "
        f"Event data: {event.get('data')}"
    )
