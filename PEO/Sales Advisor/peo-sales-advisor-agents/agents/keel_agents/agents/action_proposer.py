"""AG-38 Action Proposer - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-38"
TRIGGERS = ["com.insperity.keel.ranking.updated"]
EMITS = ["com.insperity.keel.action.proposed"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which action to propose to a human owner. Options: Actions including “do nothing”. "
        f"Event data: {event.get('data')}"
    )
