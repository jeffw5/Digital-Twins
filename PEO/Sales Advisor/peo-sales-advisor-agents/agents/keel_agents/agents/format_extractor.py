"""AG-05 Format Extractor - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-05"
TRIGGERS = ["com.insperity.keel.identity.resolved"]
EMITS = ["com.insperity.keel.content.extracted"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: How to segment text, tables and notes. Options: Segmentations and table structures. "
        f"Event data: {event.get('data')}"
    )
