"""AG-10 PII & Sensitivity Detector - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-10"
TRIGGERS = ["com.insperity.keel.content.extracted"]
EMITS = ["com.insperity.keel.content.labelled"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Whether an item holds PII and its label. Options: Labels · block · allow. "
        f"Event data: {event.get('data')}"
    )
