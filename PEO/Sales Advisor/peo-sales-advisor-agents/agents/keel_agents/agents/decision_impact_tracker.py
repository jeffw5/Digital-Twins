"""AG-27 Decision Impact Tracker - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-27"
TRIGGERS = ["com.insperity.keel.decision.bound","com.insperity.keel.crm.stage.changed"]
EMITS = ["com.insperity.keel.impact.estimated"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which downstream effects a decision caused. Options: Candidate effect attributions. "
        f"Event data: {event.get('data')}"
    )
