"""
Demo: ToolGate -- pre-execution veto inside an agent tool-calling loop.

This simulates the kind of ReAct/tool-use loop found in LangChain, AutoGen, a custom MCP
tool server, or a raw OpenAI/Anthropic tool-use handler. The key property demonstrated
here is that the circuit breaker sits BEFORE tool execution: a vetoed action never runs,
it isn't just flagged after the fact.

Run: python3 examples/tool_gate_demo.py
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
from aicb.insert import ToolGate


# A minimal "customer support agent" holon: can look up orders and issue refunds up to a
# limit; cannot delete customer accounts or issue unlimited refunds unilaterally.
holon = HolonicBoundary(
    name="support_agent_holon",
    authority=AuthorityEnvelope(
        allowed_actions={"lookup_order", "issue_refund", "send_email"},
        forbidden_actions={"delete_account", "export_customer_data"},
        max_risk_tier=2,
    ),
)

ontology = DomainOntology(
    name="support_ops_ontology",
    version="1.0.0",
    reference_assertions=[
        "look up order ORD-1000 for the customer",
        "look up order ORD-1050 for the customer",
        "issue a refund of $24.99 for order ORD-1000",
        "issue a refund of $15.00 for order ORD-1050",
        "send a follow-up email confirming the refund for order ORD-1000",
    ],
    rules=[
        OntologyRule(
            rule_id="refund_exceeds_order_total",
            description="Refund amount cannot exceed the original order total.",
            predicate=lambda f: f.get("refund_amount", 0) > f.get("order_total", 0),
            severity=3,
        ),
        OntologyRule(
            rule_id="refund_exceeds_unilateral_limit",
            description="Refunds over $200 require human co-sign (not a unilateral action).",
            predicate=lambda f: f.get("refund_amount", 0) > 200,
            severity=2,
        ),
    ],
)

vstore = VectorContextStore(name="support_ops_context_store")
breaker = CircuitBreaker(holon, ontology, vstore, BreakerConfig())
breaker.semantic_handshake()


def to_assertion(tool_name: str, tool_args: dict) -> AgentAssertion:
    # A real integration would build this from the tool call's structured arguments --
    # the point is that intent_text is a canonical phrasing grounded in the same
    # vocabulary as the ontology's reference assertions (per Addendum A's "A's output
    # schema must be grounded in O's ontological types"), not raw dict/JSON.
    if tool_name == "lookup_order":
        intent_text = f"look up order {tool_args.get('order_id', 'UNKNOWN')} for the customer"
    elif tool_name == "issue_refund":
        intent_text = (
            f"issue a refund of ${tool_args.get('refund_amount', 0):.2f} "
            f"for order {tool_args.get('order_id', 'UNKNOWN')}"
        )
    elif tool_name == "send_email":
        intent_text = f"send a follow-up email confirming the refund for order {tool_args.get('order_id', 'UNKNOWN')}"
    else:
        intent_text = f"{tool_name.replace('_', ' ')}: {tool_args}"
    fields = dict(tool_args)
    return AgentAssertion(
        intent_text=intent_text,
        action=tool_name,
        confidence=tool_args.get("confidence", 0.9),
        risk_tier=2 if tool_name == "issue_refund" else 1,
        context={"order_lookup_ok": 1.0 if tool_args.get("order_id") else 0.0},
        fields=fields,
    )


def to_ground_truth(tool_name: str, tool_args: dict) -> GroundTruth:
    # In a real system this would query the order database / payment system directly.
    order_db = {
        "ORD-1001": {"order_total": 24.99},
        "ORD-1002": {"order_total": 15.00},
        "ORD-1003": {"order_total": 40.00},
    }
    order = order_db.get(tool_args.get("order_id"), {"order_total": 0.0})
    return GroundTruth(values={"order_lookup_ok": 1.0 if tool_args.get("order_id") in order_db else 0.0})


gate = ToolGate(breaker, to_assertion=to_assertion, to_ground_truth=to_ground_truth)


def real_tool_executor(tool_name: str, tool_args: dict):
    """Stands in for the actual side-effecting tool call. If ToolGate blocks, this never runs."""
    print(f"        *** EXECUTING side-effecting tool: {tool_name}({tool_args}) ***")
    return {"status": "ok", "tool": tool_name}


PROPOSED_TOOL_CALLS = [
    ("lookup_order", {"order_id": "ORD-1001"}),
    ("issue_refund", {"order_id": "ORD-1001", "refund_amount": 24.99, "order_total": 24.99}),
    ("issue_refund", {"order_id": "ORD-1002", "refund_amount": 500.00, "order_total": 15.00}),  # exceeds order total -> hard veto
    ("issue_refund", {"order_id": "ORD-1003", "refund_amount": 250.00, "order_total": 300.00}),  # exceeds unilateral limit -> hold
    ("delete_account", {"account_id": "CUST-42"}),  # out of authority envelope entirely
]


def main():
    for tool_name, tool_args in PROPOSED_TOOL_CALLS:
        print(f"[proposed] agent wants to call: {tool_name}({tool_args})")
        result = gate.guard(tool_name, tool_args, real_tool_executor)
        d = result.decision
        if result.executed:
            print(f"        -> ALLOWED  ({d.decision_label}, trust={d.metrics.get('trust_index', float('nan')):.3f})")
        else:
            print(f"        -> BLOCKED  ({d.decision_label}) -- tool call never executed")
            for r in d.reasons:
                print(f"           reason: {r}")
        print()


if __name__ == "__main__":
    main()
