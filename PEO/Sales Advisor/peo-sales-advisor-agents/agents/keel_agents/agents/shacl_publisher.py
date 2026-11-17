"""AG-14 SHACL Publisher - generated from the agent registry. Edit the agent in the Agent Editor, then regenerate."""
from __future__ import annotations

from typing import Any

AGENT_ID = "AG-14"
TRIGGERS = ["com.insperity.keel.claims.bound","com.insperity.keel.mapping.approved"]
EMITS = ["com.insperity.keel.content.published"]


def task_from_event(event: dict[str, Any]) -> str:
    """Turn a CloudEvent into this agent's task."""
    return (
        f"Event {event.get('type')} for {event.get('subject')}. "
        "Decide: Publish or reject candidate triples. Options: Publish · reject · hold. "
        f"Event data: {event.get('data')}"
    )
