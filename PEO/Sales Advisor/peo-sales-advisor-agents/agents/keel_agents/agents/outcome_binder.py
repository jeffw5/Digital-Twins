"""AG-24 Outcome Binder - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-24"
TRIGGERS = ["com.insperity.keel.decision.recorded"]
EMITS = ["com.insperity.keel.decision.bound"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which desired outcome and metric card a decision binds to. Options: Candidate outcomes and cards. "
        f"Event data: {event.get('data')}"
    )
