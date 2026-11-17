"""AG-36 Risk & Opportunity Ranker - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-36"
TRIGGERS = ["com.insperity.keel.effect.estimated"]
EMITS = ["com.insperity.keel.ranking.updated"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: How to rank risks and opportunities. Options: Rankings by effect × exposure. "
        f"Event data: {event.get('data')}"
    )
