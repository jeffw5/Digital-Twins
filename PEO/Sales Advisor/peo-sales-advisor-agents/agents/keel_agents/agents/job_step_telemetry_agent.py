"""AG-25 Job-Step Telemetry Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-25"
TRIGGERS = ["com.insperity.keel.advisor.session.ended","com.insperity.keel.schedule.hourly"]
EMITS = ["com.insperity.keel.telemetry.recorded"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: How to attribute events to job steps. Options: Job-step attributions. "
        f"Event data: {event.get('data')}"
    )
