"""AG-31 Impact Analyzer - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-31"
TRIGGERS = ["com.insperity.keel.change.detected"]
EMITS = ["com.insperity.keel.impact.assessed"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which questions, briefs and decisions a change affects. Options: Candidate impact sets. "
        f"Event data: {event.get('data')}"
    )
