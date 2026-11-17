"""Agent runtime tests with a fake model and a fake gateway (no Foundry access needed).

Run from the repository root:  python -m unittest discover -s agents/tests
"""
from __future__ import annotations

import asyncio
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents"))

from keel_agents import contract, pipeline  # noqa: E402
from keel_agents.registry import REGISTRY, instructions_for, spec_for  # noqa: E402
from keel_agents.runtime import GovernedAgent, subscribers  # noqa: E402


class FakeGateway:
    def __init__(self, state: str = "CLOSED"):
        self.state, self.reports, self.events = state, [], []

    async def breaker(self, agent_id):
        return {"state": self.state, "reason": "test"}

    async def report(self, agent_id, ok, failed):
        self.reports.append((agent_id, ok, failed))
        return {"state": self.state}

    async def emit(self, agent_id, type_, subject, data):
        self.events.append((agent_id, type_))


def runner_returning(obj):
    async def run(spec, prompt):
        return "```json\n" + json.dumps(obj) + "\n```"
    return run


def good_output(spec):
    opts = contract.enumerable_options(spec)
    return {"decision": spec["decision"], "option": opts[0] if opts else "done", "options_considered": opts or ["done"],
            "confidence": 0.9, "outputs": {}, "citations": [{"uri": "urn:x", "span": "s1"}],
            "rules_applied": spec["rules"][:1], "needs_human": False, "notes": ""}


class RegistryTests(unittest.TestCase):
    def test_every_hosted_agent_has_instructions_and_task(self) -> None:
        from keel_agents.agents import TASKS
        for a in REGISTRY["agents"]:
            if a["surface"] == "declarative":
                continue
            self.assertIn(a["id"], TASKS)
            text = instructions_for(a)
            self.assertIn(a["id"], text)
            self.assertIn("Output contract", text)

    def test_event_chain_is_connected(self) -> None:
        emitted = {e for a in REGISTRY["agents"] for e in a["emits"]}
        external = ("schedule.", "com.microsoft.graph.", "feed.item.received", "advisor.question.asked", "advisor.session.ended",
                    "crm.stage.changed", "schema.changed", "mapping.approved", "ssot.rule.released", "brief.released")
        for a in REGISTRY["agents"]:
            for t in a["triggers"]:
                self.assertTrue(t in emitted or any(x in t for x in external), f"{a['id']} waits for {t}, which nothing emits")

    def test_subscribers(self) -> None:
        self.assertIn("AG-04", subscribers("com.insperity.keel.content.item.changed"))


class ContractTests(unittest.TestCase):
    def test_good_output_passes(self) -> None:
        spec = spec_for("AG-23")
        self.assertEqual(contract.check(spec, good_output(spec)), [])

    def test_missing_citation_fails_grounding(self) -> None:
        spec = spec_for("AG-08")  # watches IS-1
        out = good_output(spec) | {"citations": []}
        self.assertIn("IS-1", contract.check(spec, out))

    def test_dropped_option_fails_completeness(self) -> None:
        spec = spec_for("AG-15")  # options: OK · degraded · broken
        out = good_output(spec)
        out["options_considered"] = out["options_considered"][:1]
        spec = dict(spec, signals=spec["signals"] + ["IS-2"])
        self.assertIn("IS-2", contract.check(spec, out))

    def test_stray_rule_fails_conformance(self) -> None:
        spec = spec_for("AG-14")
        out = good_output(spec) | {"rules_applied": ["PAY-005"]}
        self.assertIn("IS-4", contract.check(spec, out))


class MalformedOutputTests(unittest.TestCase):
    def test_wrong_types_are_faults_not_crashes(self) -> None:
        spec = spec_for("AG-08")
        for bad in ({"citations": "urn:x"}, {"outputs": "x"}, {"rules_applied": "EXT-007"}, {"citations": ["urn:x"]}):
            self.assertEqual(contract.check(spec, good_output(spec) | bad), ["IS-4"])

    def test_runner_exception_reports_fault_and_hides_output(self) -> None:
        spec = spec_for("AG-11")
        gw = FakeGateway()

        async def boom(s, p):
            raise RuntimeError("model unavailable")
        out = asyncio.run(GovernedAgent(spec, runner=boom, gateway=gw).run("check"))
        self.assertTrue(out["needs_human"])
        self.assertEqual(gw.reports[-1], ("AG-11", False, ["IS-4"]))
        self.assertNotIn("rejected_output", out["outputs"])


class RuntimeTests(unittest.TestCase):
    def test_run_reports_ok_and_emits(self) -> None:
        spec = spec_for("AG-06")
        gw = FakeGateway()
        out = asyncio.run(GovernedAgent(spec, runner=runner_returning(good_output(spec)), gateway=gw).run("classify"))
        self.assertFalse(out["needs_human"])
        self.assertEqual(gw.reports[-1], ("AG-06", True, []))
        self.assertEqual(gw.events[-1][1], spec["emits"][0])

    def test_open_breaker_runs_fallback_without_model(self) -> None:
        spec = spec_for("AG-11")
        called = []

        async def runner(s, p):
            called.append(1)
            return "{}"
        out = asyncio.run(GovernedAgent(spec, runner=runner, gateway=FakeGateway("OPEN")).run("check"))
        self.assertEqual(called, [])
        self.assertTrue(out["needs_human"])
        self.assertIn(spec["fallback"], out["notes"])

    def test_failed_check_reports_fault(self) -> None:
        spec = spec_for("AG-08")
        gw = FakeGateway()
        out = asyncio.run(GovernedAgent(spec, runner=runner_returning(good_output(spec) | {"citations": []}), gateway=gw).run("extract"))
        self.assertTrue(out["needs_human"])
        self.assertEqual(gw.reports[-1][1], False)
        self.assertEqual(gw.events, [])

    def test_half_open_forces_human(self) -> None:
        spec = spec_for("AG-26")
        out = asyncio.run(GovernedAgent(spec, runner=runner_returning(good_output(spec)), gateway=FakeGateway("HALF-OPEN")).run("gaps"))
        self.assertTrue(out["needs_human"])


class PipelineTests(unittest.TestCase):
    def test_pipeline_releases_or_holds(self) -> None:
        def make(agent_id):
            spec = spec_for(agent_id)
            return GovernedAgent(spec, runner=runner_returning(good_output(spec)), gateway=FakeGateway())
        res = asyncio.run(pipeline.ask("client_admin", "Are we eligible?", "CA-J1.2", make=make))
        self.assertEqual(res["status"], "released")
        self.assertEqual([t["agent"] for t in res["trail"]], pipeline.STEPS)

        def make_held(agent_id):
            spec = spec_for(agent_id)
            gw = FakeGateway("OPEN" if agent_id == "AG-23" else "CLOSED")
            return GovernedAgent(spec, runner=runner_returning(good_output(spec)), gateway=gw)
        res = asyncio.run(pipeline.ask("client_admin", "Are we eligible?", make=make_held))
        self.assertEqual(res["status"], "held")
        self.assertEqual(res["held_by"], "AG-23")
        self.assertNotIn("partial", res)  # nothing assembled before a hold is returned


if __name__ == "__main__":
    unittest.main()
