"""AG-33 Cache Invalidation Agent - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-33"
TRIGGERS = ["com.insperity.keel.impact.assessed"]
EMITS = ["com.insperity.keel.brief.withdrawn"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Withdraw, flag or keep a served brief. Options: Withdraw · flag · keep. "
        f"Event data: {event.get('data')}"
    )
