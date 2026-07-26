"""
Lightweight sanity tests (plain asserts, no pytest dependency required -- run directly
with `python3 tests/test_breaker.py`, or with pytest if available).
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
from aicb.metrics import semantic_anomaly_score, contextual_relevancy_index, mtbh
from aicb.vectorize import embed, cosine_similarity


def make_breaker(**config_overrides) -> CircuitBreaker:
    holon = HolonicBoundary(
        name="test_holon",
        authority=AuthorityEnvelope(allowed_actions={"do_thing"}, forbidden_actions={"forbidden_thing"}, max_risk_tier=2),
    )
    ontology = DomainOntology(
        name="test_ontology",
        reference_assertions=["do the normal thing with normal parameters"],
        rules=[
            OntologyRule("impossible_value", "value must be >= 0", lambda f: f.get("value", 0) < 0, severity=3)
        ],
    )
    vstore = VectorContextStore(name="test_store")
    config = BreakerConfig(**config_overrides)
    return CircuitBreaker(holon, ontology, vstore, config)


def test_embed_deterministic():
    a1 = embed("reroute traffic")
    a2 = embed("reroute traffic")
    assert (a1 == a2).all(), "embedding must be deterministic"
    assert abs(float((a1 ** 2).sum()) ** 0.5 - 1.0) < 1e-6, "embedding must be L2-normalized"


def test_semantic_anomaly_score_bounds():
    v1 = embed("do the normal thing")
    v2 = embed("do the normal thing")
    sa_same = semantic_anomaly_score(v1, v2)
    assert sa_same < 1e-6, f"identical text should have ~0 anomaly, got {sa_same}"

    v3 = embed("xyz completely unrelated gibberish quantum toaster")
    sa_diff = semantic_anomaly_score(embed("do the normal thing"), v3)
    assert sa_diff > sa_same


def test_contextual_relevancy_perfect_match():
    cr = contextual_relevancy_index({"a": 1.0, "b": 0.5}, {"a": 1.0, "b": 0.5})
    assert abs(cr - 1.0) < 1e-9


def test_contextual_relevancy_penalizes_mismatch():
    cr = contextual_relevancy_index({"a": 1.0}, {"a": 0.0})
    assert cr < 0.5


def test_mtbh_no_hallucinations():
    hours = mtbh(3600 * 10, 0)
    assert abs(hours - 10.0) < 1e-9


def test_normal_action_passes():
    b = make_breaker()
    b.semantic_handshake()
    assertion = AgentAssertion(
        intent_text="do the normal thing with normal parameters",
        action="do_thing",
        confidence=0.95,
        context={"x": 1.0},
        fields={"value": 5},
    )
    gt = GroundTruth(values={"x": 1.0})
    decision = b.evaluate(assertion, gt)
    assert decision.passed, decision.reasons


def test_out_of_scope_action_hard_trips():
    b = make_breaker()
    b.semantic_handshake()
    assertion = AgentAssertion(intent_text="do a forbidden thing", action="forbidden_thing", confidence=0.99)
    gt = GroundTruth(values={})
    decision = b.evaluate(assertion, gt)
    assert not decision.passed
    assert decision.safe_state.name == "LEVEL3_HALT"
    assert decision.excluded_from_training


def test_ontology_violation_trips():
    b = make_breaker()
    b.semantic_handshake()
    assertion = AgentAssertion(
        intent_text="do the normal thing with normal parameters",
        action="do_thing",
        confidence=0.9,
        fields={"value": -5},
    )
    gt = GroundTruth(values={})
    decision = b.evaluate(assertion, gt)
    assert not decision.passed
    assert any("impossible_value" in r for r in decision.reasons)


def test_semantic_hallucination_trips():
    b = make_breaker()
    b.semantic_handshake()
    assertion = AgentAssertion(
        intent_text="launch a spaceship to mars using the toaster oven",
        action="do_thing",
        confidence=0.99,
        context={"x": 1.0},
        fields={"value": 1},
    )
    gt = GroundTruth(values={"x": 1.0})
    decision = b.evaluate(assertion, gt)
    assert not decision.passed
    assert decision.metrics["semantic_anomaly_score"] >= b.config.sa_ceiling


def test_context_ungrounded_trips():
    b = make_breaker()
    b.semantic_handshake()
    assertion = AgentAssertion(
        intent_text="do the normal thing with normal parameters",
        action="do_thing",
        confidence=0.9,
        context={"x": 1.0},
        fields={"value": 1},
    )
    gt = GroundTruth(values={"x": 0.0})  # ground truth strongly disagrees
    decision = b.evaluate(assertion, gt)
    assert not decision.passed


def test_triple_trip_lockout():
    b = make_breaker(triple_trip_count=3, triple_trip_window_seconds=600)
    b.semantic_handshake()
    bad = AgentAssertion(intent_text="gibberish nonsense unrelated text", action="do_thing", confidence=0.99, fields={"value": 1})
    gt = GroundTruth(values={})
    last_decision = None
    for _ in range(4):
        last_decision = b.evaluate(bad, gt)
    assert b.locked_out
    assert last_decision.decision_label == "LOCKOUT"


def test_lockout_blocks_even_normal_requests_until_resumed():
    b = make_breaker(triple_trip_count=2, triple_trip_window_seconds=600)
    b.semantic_handshake()
    bad = AgentAssertion(intent_text="gibberish nonsense unrelated text", action="do_thing", confidence=0.99, fields={"value": 1})
    gt = GroundTruth(values={})
    b.evaluate(bad, gt)
    b.evaluate(bad, gt)
    assert b.locked_out

    good = AgentAssertion(intent_text="do the normal thing with normal parameters", action="do_thing", confidence=0.95, context={"x": 1.0}, fields={"value": 1})
    good_gt = GroundTruth(values={"x": 1.0})
    decision = b.evaluate(good, good_gt)
    assert not decision.passed
    assert decision.decision_label == "LOCKOUT"

    b.resume_from_lockout(trustee_id="tester")
    assert not b.locked_out
    decision2 = b.evaluate(good, good_gt)
    assert decision2.passed


def test_audit_chain_is_tamper_evident():
    b = make_breaker()
    b.semantic_handshake()
    good = AgentAssertion(intent_text="do the normal thing with normal parameters", action="do_thing", confidence=0.95, context={"x": 1.0}, fields={"value": 1})
    b.evaluate(good, GroundTruth(values={"x": 1.0}))
    assert b.audit.verify_chain()
    # tamper with an entry
    b.audit.entries[0].decision = "TRANSMIT_TAMPERED"
    # entries property returns a shallow copy of the list but dataclass objects are shared;
    # mutate the actual stored entry to simulate tampering
    b.audit._entries[0].decision = "TRANSMIT_TAMPERED"
    assert not b.audit.verify_chain()


def test_sop03_exclusion_filter():
    b = make_breaker()
    b.semantic_handshake()
    good = AgentAssertion(intent_text="do the normal thing with normal parameters", action="do_thing", confidence=0.95, context={"x": 1.0}, fields={"value": 1})
    bad = AgentAssertion(intent_text="do a forbidden thing", action="forbidden_thing", confidence=0.99)
    b.evaluate(good, GroundTruth(values={"x": 1.0}))
    b.evaluate(bad, GroundTruth(values={}))
    batch = b.recursive_learning_batch()
    assert batch["eligible_count"] == 1
    assert batch["purged_count"] == 1


def run_all():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_") and callable(obj)]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed out of {len(tests)}")
    return failed == 0


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
