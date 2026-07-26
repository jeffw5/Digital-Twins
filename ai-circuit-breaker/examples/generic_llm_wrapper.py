"""
Illustration: inserting the AI Circuit Breaker in front of ANY hosted LLM API.

This file is deliberately runnable with a fake client (no API key / network call needed
to see it work), but the shape of `call_llm()` is exactly what you'd write against a real
OpenAI/Anthropic/local-model client -- swap `FakeLLMClient` for the real SDK client and
nothing else about the integration changes. This is the point: the breaker only cares
about the (AgentAssertion, GroundTruth) pair the adapters produce, not what produced the
raw text.

Run: python3 examples/generic_llm_wrapper.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aicb import (
    AuthorityEnvelope,
    HolonicBoundary,
    OntologyRule,
    DomainOntology,
    VectorContextStore,
    AgentAssertion,
    GroundTruth,
    CircuitBreaker,
    BreakerConfig,
)
from aicb.insert import protect, CircuitBreakerTrip


# ---- A - Domain Agent (swap this for a real client; nothing else changes) ------------
class FakeLLMClient:
    """Pretend OpenAI/Anthropic-style client. Replace with:
        from anthropic import Anthropic
        client = Anthropic(api_key=...)
        client.messages.create(...)
    or
        from openai import OpenAI
        client = OpenAI(api_key=...)
        client.chat.completions.create(...)
    """

    def complete(self, prompt: str) -> str:
        if "unlimited access" in prompt.lower():
            return "Sure, I'll grant unlimited administrative access to all systems immediately."
        return "Schedule a routine maintenance window for the requested system."


client = FakeLLMClient()

# ---- H, O, V for a generic "IT operations assistant" deployment ----------------------
holon = HolonicBoundary(
    name="it_ops_assistant",
    authority=AuthorityEnvelope(
        allowed_actions={"schedule_maintenance", "restart_service", "acknowledge"},
        forbidden_actions={"grant_admin_access", "delete_user", "disable_firewall"},
        max_risk_tier=1,
    ),
)
ontology = DomainOntology(
    name="it_ops_ontology",
    version="1.0.0",
    reference_assertions=[
        "schedule a routine maintenance window for the requested system",
        "restart the background indexing service after a memory leak alert",
        "acknowledge the alert and monitor for recurrence",
    ],
    rules=[
        OntologyRule(
            rule_id="no_unbounded_access_grants",
            description="The assistant may never grant unlimited/unbounded access of any kind.",
            predicate=lambda f: f.get("grants_unlimited_access", False),
            severity=3,
        ),
    ],
)
vstore = VectorContextStore(name="it_ops_context_store")
breaker = CircuitBreaker(holon, ontology, vstore, BreakerConfig())
breaker.semantic_handshake()


def to_assertion(raw_text: str, prompt: str) -> AgentAssertion:
    grants_access = "admin access" in raw_text.lower() or "unlimited" in raw_text.lower()
    action = "grant_admin_access" if grants_access else "schedule_maintenance"
    return AgentAssertion(
        intent_text=raw_text,
        action=action,
        confidence=0.9,
        risk_tier=1,
        context={"request_is_routine": 0.0 if grants_access else 1.0},
        fields={"grants_unlimited_access": grants_access},
    )


def to_ground_truth(prompt: str) -> GroundTruth:
    # Deterministic ground truth: was this actually a routine, pre-approved request type?
    is_routine = "unlimited access" not in prompt.lower()
    return GroundTruth(values={"request_is_routine": 1.0 if is_routine else 0.0})


@protect(breaker, to_assertion=to_assertion, to_ground_truth=to_ground_truth, on_trip="raise")
def call_llm(prompt: str) -> str:
    return client.complete(prompt)


def main():
    prompts = [
        "Please schedule maintenance for the billing database this weekend.",
        "Please grant unlimited access to everyone on the platform team right now.",
    ]
    for p in prompts:
        print(f"prompt: {p!r}")
        try:
            result = call_llm(p)
            print(f"  -> ALLOWED: {result.output!r}")
            print(f"     trust metadata: {result.trust_metadata}")
        except CircuitBreakerTrip as trip:
            print(f"  -> VETOED: {trip}")
        print()


if __name__ == "__main__":
    main()
