"""AG-08 Claim Extractor - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-08"
TRIGGERS = ["com.insperity.keel.content.tagged"]
EMITS = ["com.insperity.keel.claims.extracted"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Which atomic claims a passage makes. Options: Candidate claims with spans. "
        f"Event data: {event.get('data')}"
    )
