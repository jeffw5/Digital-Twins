"""The Sales Advisor answer pipeline behind the advisor_ask tool.

Intent & RCB -> Federated Query Planner -> Facet Navigator -> Mapping Resolver ->
Precision Extractor -> Brief Assembler -> Entitlement Enforcer -> Grounding Guard.
Each step is a governed agent with its own breaker; if any step needs a person or falls
back, the pipeline stops and returns a held result with a BPA hand-off (EXT-012, DEC-010).
"""
from __future__ import annotations

from typing import Any

from .runtime import GovernedAgent

STEPS = ["AG-16", "AG-17", "AG-18", "AG-19", "AG-20", "AG-21", "AG-11", "AG-23"]


async def ask(persona: str, question: str, job_step: str | None = None, prospect_uri: str | None = None,
              make=GovernedAgent.from_registry) -> dict[str, Any]:
    context: dict[str, Any] = {"who": {"persona": persona, "prospect": prospect_uri}, "what": question,
                               "why": {"job_step": job_step}}
    trail: list[dict[str, Any]] = []
    carry: dict[str, Any] = {}
    for agent_id in STEPS:
        agent = make(agent_id)
        out = await agent.run(f"Persona question: {question}\nPrevious step output: {carry}", context)
        trail.append({"agent": agent_id, "option": out.get("option"), "needs_human": out.get("needs_human")})
        if out.get("needs_human") or out.get("option") == "fallback":
            # Nothing assembled before the hold is returned: a hold by AG-11 or AG-23 means it is not safe to show.
            return {"status": "held", "held_by": agent_id, "reason": out.get("notes"), "trail": trail,
                    "ai_disclosure": "AI-assembled. A BPA will follow up on this question (DEC-010)."}
        carry = out.get("outputs", {})
        context.setdefault("steps", {})[agent_id] = out.get("option")
    return {"status": "released", "brief": carry, "trail": trail,
            "ai_disclosure": "AI-assembled brief. Sources are listed; a BPA is available at every decision (DEC-010)."}
