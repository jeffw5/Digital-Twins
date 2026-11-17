"""AG-09 Jurisdiction & Validity Miner - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-09"
TRIGGERS = ["com.insperity.keel.claims.extracted"]
EMITS = ["com.insperity.keel.claims.scoped"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which jurisdictions and dates apply. Options: Jurisdictions from the registry; date candidates. "
        f"Event data: {event.get('data')}"
    )
