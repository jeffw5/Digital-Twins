"""
Closes the Training & Feedback (human-in-the-loop) loop: applies a batch of Trustee
review decisions -- either exported from the dashboard's HITL tab, or the built-in
sample below -- and regenerates the dashboard so the correction is actually visible in
the system, not just recorded as a comment.

Why "replay" instead of "load a saved breaker"?  This prototype's CircuitBreaker is an
in-memory object, not something persisted to disk between runs -- exactly like a real
system's live process state. The realistic way to apply a correction after the fact is
the same pattern event-sourced systems use: replay the deterministic decision log to
rebuild state, then apply the new review events on top. `pipeline_review_demo.run_scenarios`
is deterministic in the sense that matters here -- the same scenarios always land on the
same audit sequence numbers -- so a `hitl_decisions.json` exported from one run's
dashboard is still valid against a fresh replay.

What actually changes when a review is applied:
  - CONFIRM_HALLUCINATION    : no system state change beyond the permanent HTDR record.
  - FALSE_POSITIVE_OVERRIDE  : the epoch moves from "purged" to "training-eligible" in
                               `effective_recursive_learning_batch()` -- SOP-03's
                               exclusion filter is overridden for that specific epoch.
  - CORRECTED_LABEL          : the corrected intent text is written into the ontology's
                               reference_assertions -- literally changing what the
                               breaker considers "known-good" going forward (Ontology
                               Enhancement from a human correction).
  - ESCALATE                 : routes to the holon's escalation topology; recorded, no
                               other state change in this prototype.

Run:
  python3 examples/apply_hitl_review.py                       # uses the built-in sample
  python3 examples/apply_hitl_review.py path/to/hitl_decisions.json   # uses an exported file
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pipeline_review_demo as pipe
from aicb import dashboard, console


# A sample decision batch matching the shape the dashboard's "Export Review Decisions
# (JSON)" button produces. Used when no file path is given on the command line, so this
# script is runnable standalone as a demonstration of the format.
SAMPLE_DECISIONS = [
    {
        "audit_seq": None,  # filled in below by name lookup
        "scenario_name_hint": "hallucination-01",
        "trustee_id": "j.wallk",
        "action": "confirm_hallucination",
        "note": "Confirmed: unrelated marketing text, no grounding in telemetry. Correct trip.",
        "corrected_intent_text": "",
        "corrected_action": "",
    },
    {
        "audit_seq": None,
        "scenario_name_hint": "normal-03",
        "trustee_id": "j.wallk",
        "action": "false_positive_override",
        "note": "Reviewed: this was a routine, well-grounded reroute request that only got excluded because it arrived while the breaker was in SOP-02 lockout from the unrelated hallucination cluster. The action itself was never at fault. Returning to training set.",
        "corrected_intent_text": "",
        "corrected_action": "",
    },
    {
        "audit_seq": None,
        "scenario_name_hint": "context-ungrounded-01",
        "trustee_id": "j.wallk",
        "action": "corrected_label",
        "note": "AI proceeded as if the link were up. Correct behavior was to hold the reroute and flag for confirmation given the sensor disagreement.",
        "corrected_intent_text": "hold the reroute of traffic from node 2 to node 9 pending link recovery confirmation",
        "corrected_action": "hold_for_confirmation",
    },
]


def _resolve_sample_audit_seqs(decisions: list[dict], breaker) -> list[dict]:
    """Map each sample decision's scenario-name hint to the actual audit seq produced by
    this replay (keeps the sample self-documenting without hardcoding seq numbers that
    would silently go stale if SCENARIOS changes).
    """
    by_name = {e.intent_text: e.seq for e in breaker.audit.entries}
    # SCENARIOS names are "short-hint: full description" -- match on the short hint.
    name_to_intent = {s["name"].split(":", 1)[0]: s["agent_output"]["intent_text"] for s in pipe.SCENARIOS}
    resolved = []
    for d in decisions:
        hint = d.get("scenario_name_hint")
        d = dict(d)
        if hint and d.get("audit_seq") is None:
            intent = name_to_intent.get(hint)
            d["audit_seq"] = by_name.get(intent)
        d.pop("scenario_name_hint", None)
        resolved.append(d)
    return resolved


def load_decisions(path: str | None, breaker) -> list[dict]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return _resolve_sample_audit_seqs(SAMPLE_DECISIONS, breaker)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None

    print("Replaying deterministic scenario set to rebuild breaker state...")
    breaker, morphism_chain = pipe.build_system()
    breaker.semantic_handshake()
    pipe.run_scenarios(breaker, morphism_chain)

    decisions = load_decisions(path, breaker)
    print(f"\nApplying {len(decisions)} Trustee review decision(s) "
          f"({'from ' + path if path else 'built-in sample'}):\n")

    before = breaker.effective_recursive_learning_batch()

    for d in decisions:
        if d.get("audit_seq") is None:
            print(f"  SKIP: could not resolve audit_seq for decision {d}")
            continue
        htdr = breaker.review_flagged_event(
            audit_seq=d["audit_seq"],
            trustee_id=d.get("trustee_id", "unknown_trustee"),
            action=d["action"],
            note=d.get("note", ""),
            corrected_intent_text=d.get("corrected_intent_text", ""),
            corrected_action=d.get("corrected_action", ""),
        )
        print(f"  HTDR #{htdr.seq}: {d.get('trustee_id')} -> {htdr.action.value} on audit #{d['audit_seq']}")
        if d["action"] == "corrected_label":
            print(f"           ontology reference_assertions now: {len(breaker.ontology.reference_assertions)} "
                  f"(added: \"{d.get('corrected_intent_text', '')}\")")

    after = breaker.effective_recursive_learning_batch()

    print("\nSOP-03 recursive learning batch, before vs. after review:")
    print(f"  training_eligible: {before['eligible_count']} -> {after['eligible_count']}")
    print(f"  purged_excluded:   {before['purged_count']} -> {after['purged_count']}")

    print(f"\nHTDR chain valid: {breaker.review_log.verify_chain()}")
    print(f"Decision audit chain valid (untouched by review): {breaker.audit.verify_chain()}")

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "trust_dashboard.html"))
    dashboard.write(breaker, out_path, title="AI Circuit Breaker -- Trust Metrology Dashboard (Reviewed)")
    print(f"\nDashboard regenerated with review history applied: {out_path}")

    console_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "governance_console.html"))
    console.write(breaker, console_path, title="AI Circuit Breaker -- Governance Console (Reviewed)")
    print(f"Governance Console regenerated with review history applied: {console_path}")


if __name__ == "__main__":
    main()
