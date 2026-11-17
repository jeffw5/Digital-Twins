"""Gateway tests: policy enforcement, breakers, Simplex gate and a real MCP round trip.

Run from the repository root:  python -m unittest discover -s keel-gateway/tests
"""
from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "keel-gateway"))
os.environ.setdefault("KEEL_REGISTRY", str(ROOT / "registry" / "agent-registry.json"))
_tmp = tempfile.mkdtemp()
os.environ["KEEL_AUDIT_PATH"] = os.path.join(_tmp, "audit.jsonl")
os.environ["KEEL_EVENTS_PATH"] = os.path.join(_tmp, "events.jsonl")

from keel_gateway.governance import CallContext, Governance  # noqa: E402
from keel_gateway.registry import load  # noqa: E402

REG = load()


def ctx(agent: str | None, persona: str | None = None, kind: str = "service", user: str | None = None) -> CallContext:
    return CallContext(agent_id=agent, user=user, persona=persona, tenant="t1", traceparent=None, kind=kind)


class PolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gov = Governance(REG)

    def test_unregistered_agent_denied(self) -> None:
        d = self.gov.authorize(ctx(None), REG.operations["content_get"], "content_get", {"uri": "urn:x"})
        self.assertFalse(d.allowed)
        self.assertIn("CON-044", d.rules)

    def test_allow_list(self) -> None:
        self.assertTrue(self.gov.authorize(ctx("AG-05"), REG.operations["content_get"], "content_get", {"uri": "urn:x"}).allowed)
        d = self.gov.authorize(ctx("AG-05"), REG.operations["content_publish"], "content_publish", {"jsonld": {}, "kgcl": ""})
        self.assertFalse(d.allowed)
        self.assertIn("CON-045", d.rules)

    def test_every_registered_tool_exists(self) -> None:
        for a in REG.agents.values():
            for t in a["tools"]:
                self.assertIn(t, REG.operations, f"{a['id']} lists unknown tool {t}")

    def test_simplex_gate(self) -> None:
        op = REG.operations["contract_send_for_signature"]
        # no agent holds this tool today; give AG-38 a temporary allow-list entry for the test
        REG.agents["AG-38"]["tools"].append("contract_send_for_signature")
        try:
            args = {"proposal_id": "p1"}
            d = self.gov.authorize(ctx("AG-38"), op, op.name, args | {"approval_id": "none"})
            self.assertFalse(d.allowed)
            self.assertIn("CON-028", d.rules)
            ap = self.gov.approvals.request(op.name, args, "test", "AG-38")
            with self.assertRaises(PermissionError):
                self.gov.approvals.grant(ap["approval_id"], "AG-38")  # requester cannot approve (CTL-013)
            with self.assertRaises(PermissionError):
                self.gov.approvals.grant(ap["approval_id"], "")       # approver identity required
            self.gov.approvals.grant(ap["approval_id"], "owner-1")
            other = {"proposal_id": "p2", "approval_id": ap["approval_id"]}
            self.assertFalse(self.gov.authorize(ctx("AG-38"), op, op.name, other).allowed)  # bound to its payload
            good = args | {"approval_id": ap["approval_id"]}
            self.assertTrue(self.gov.authorize(ctx("AG-38"), op, op.name, good).allowed)
            self.assertFalse(self.gov.authorize(ctx("AG-38"), op, op.name, good).allowed)   # single use
        finally:
            REG.agents["AG-38"]["tools"].remove("contract_send_for_signature")

    def test_allow_list_miss_is_a_fault_only_for_services(self) -> None:
        self.gov.authorize(ctx("AG-19", kind="dev"), REG.operations["content_publish"], "content_publish", {"jsonld": {}, "kgcl": ""})
        self.assertEqual(self.gov.breakers.state("AG-19")["faults"], 0)
        self.gov.authorize(ctx("AG-19"), REG.operations["content_publish"], "content_publish", {"jsonld": {}, "kgcl": ""})
        st = self.gov.breakers.state("AG-19")
        self.assertEqual(st["faults"], 1)
        self.assertEqual(st["state"], "CLOSED")  # never a hard trip

    def test_arguments_are_validated(self) -> None:
        d = self.gov.authorize(ctx("FD-01"), REG.operations["advisor_ask"], "advisor_ask", {"persona": "client_admin"})
        self.assertFalse(d.allowed)
        self.assertIn("Invalid arguments", d.reason)

    def test_decision_needs_confirmation_and_a_person(self) -> None:
        op = REG.operations["advisor_record_decision"]
        base = {"brief_id": "b", "option_id": "o", "rationale": "r"}
        self.assertFalse(self.gov.authorize(ctx("FD-01", kind="user", user="oid-1"), op, op.name, base | {"confirmed_by_person": False}).allowed)
        self.assertFalse(self.gov.authorize(ctx("FD-01"), op, op.name, base | {"confirmed_by_person": True}).allowed)  # a service is not a person
        self.assertTrue(self.gov.authorize(ctx("FD-01", kind="user", user="oid-1"), op, op.name, base | {"confirmed_by_person": True}).allowed)

    def test_persona_entitlement(self) -> None:
        op = REG.operations["advisor_ask"]
        q = {"question": "Are we eligible?"}
        self.assertTrue(self.gov.authorize(ctx("FD-01"), op, op.name, q | {"persona": "client_admin"}).allowed)
        d = self.gov.authorize(ctx("FD-01"), op, op.name, q | {"persona": "bpa"})   # not in the schema's persona list
        self.assertFalse(d.allowed)


class BreakerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gov = Governance(REG)

    def test_three_in_a_row_opens(self) -> None:
        b = self.gov.breakers
        self.assertEqual(b.state("AG-06")["state"], "CLOSED")
        b.report("AG-06", ok=False)
        self.assertEqual(b.state("AG-06")["state"], "CLOSED")
        b.report("AG-06", ok=False)
        self.assertEqual(b.state("AG-06")["state"], "HALF-OPEN")
        b.report("AG-06", ok=False)
        self.assertEqual(b.state("AG-06")["state"], "OPEN")

    def test_hard_trip_opens_and_blocks(self) -> None:
        b = self.gov.breakers
        b.report("AG-11", ok=False, failed_signals=["IS-5"])
        self.assertEqual(b.state("AG-11")["state"], "OPEN")
        d = self.gov.authorize(ctx("AG-11"), REG.operations["pdp_evaluate"], "pdp_evaluate", {"action": "read", "resource_uri": "u"})
        self.assertFalse(d.allowed)
        self.assertIn("CON-046", d.rules)
        self.assertEqual(b.reset("AG-11")["state"], "CLOSED")

    def test_mtbh_floor_with_evidence(self) -> None:
        b = self.gov.breakers
        tier = REG.tiers[REG.agents["AG-25"]["tier"]]  # tier 3
        for i in range(tier["open"] * 2):
            b.report("AG-25", ok=(i % 20 != 0))  # MTBH about 20, below the open floor
        self.assertEqual(b.state("AG-25")["state"], "OPEN")

    def test_half_open_blocks_writes_only(self) -> None:
        b = self.gov.breakers
        b.report("AG-14", ok=False)
        b.report("AG-14", ok=False)
        self.assertEqual(b.state("AG-14")["state"], "HALF-OPEN")
        self.assertTrue(self.gov.authorize(ctx("AG-14"), REG.operations["content_validate"], "content_validate", {"jsonld": {}}).allowed)
        self.assertFalse(self.gov.authorize(ctx("AG-14"), REG.operations["content_publish"], "content_publish", {"jsonld": {}, "kgcl": ""}).allowed)


class AuditTests(unittest.TestCase):
    def test_hash_chain(self) -> None:
        gov = Governance(REG)
        Path(os.environ["KEEL_AUDIT_PATH"]).unlink(missing_ok=True)
        for t in ("content_get", "content_validate"):
            d = gov.authorize(ctx("AG-05"), REG.operations[t], t, {"uri": "u"})
            gov.audit(ctx("AG-05"), t, {"uri": "u"}, d, None)
        lines = Path(os.environ["KEEL_AUDIT_PATH"]).read_text().splitlines()
        import hashlib
        self.assertEqual(json.loads(lines[1])["prev"], hashlib.sha256(lines[0].encode()).hexdigest())
        self.assertNotIn('"u"', lines[0])  # inputs are logged by hash, not value


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class McpRoundTrip(unittest.TestCase):
    """Starts the gateway over HTTP and talks MCP to it, the way Copilot does."""

    @classmethod
    def setUpClass(cls) -> None:
        import uvicorn
        from keel_gateway.server import create_app
        os.environ["KEEL_SERVICE_TOKEN"] = "svc-test"
        os.environ["KEEL_ADMIN_TOKEN"] = "adm-test"
        cls.port = _free_port()
        cls.server = uvicorn.Server(uvicorn.Config(create_app(), host="127.0.0.1", port=cls.port, log_level="warning"))
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        for _ in range(100):
            if cls.server.started:
                break
            time.sleep(0.05)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.should_exit = True
        cls.thread.join(timeout=5)

    def _run(self, agent: str, fn, headers: dict | None = None, path: str | None = None):
        import httpx2
        from mcp.client.session import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async def go():
            async with httpx2.AsyncClient(timeout=30, headers=headers or {}) as hc:
                async with streamable_http_client(f"http://127.0.0.1:{self.port}{path or '/mcp/agents/' + agent}", http_client=hc) as st:
                    async with ClientSession(st[0], st[1]) as s:
                        await s.initialize()
                        return await fn(s)
        return asyncio.run(go())

    def _http(self, method: str, path: str, body: dict | None = None, token: str | None = None):
        import urllib.error
        import urllib.request
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = "Bearer " + token
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method=method, headers=h, data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"null")

    def test_tools_list_matches_generated_manifests(self) -> None:
        listed = self._run("FD-01", lambda s: s.list_tools())
        names = [t.name for t in listed.tools]
        self.assertEqual(sorted(names), sorted(REG.allowed_tools("FD-01")))
        gen = json.loads((ROOT / "registry" / "gateway-tools.json").read_text())["tools"]
        by = {t["name"]: t for t in gen}
        for t in listed.tools:
            self.assertEqual(t.model_dump(by_alias=True, exclude_none=True, mode="json"), by[t.name], t.name)

    def test_no_agent_sees_no_tools(self) -> None:
        listed = self._run("", lambda s: s.list_tools(), path="/mcp")
        self.assertEqual(listed.tools, [])

    def test_call_and_deny(self) -> None:
        r = self._run("FD-01", lambda s: s.call_tool("advisor_ask", {"persona": "client_admin", "question": "Are we eligible?"}))
        self.assertFalse(r.is_error)
        r = self._run("FD-01", lambda s: s.call_tool("content_publish", {"jsonld": {}, "kgcl": ""}))
        self.assertTrue(r.is_error)
        self.assertIn("CON-045", r.content[0].text)
        r = self._run("FD-01", lambda s: s.call_tool("no_such_tool", {}))
        self.assertTrue(r.is_error)

    def test_service_token_and_governance_routes(self) -> None:
        r = self._run("", lambda s: s.list_tools(), headers={"Authorization": "Bearer svc-test", "X-Keel-Agent": "AG-05"}, path="/mcp")
        self.assertEqual(sorted(t.name for t in r.tools), sorted(REG.allowed_tools("AG-05")))
        code, _ = self._http("POST", "/governance/breaker/AG-05/kill", {}, token="svc-test")
        self.assertEqual(code, 403)  # the service token is not the owner token
        code, _ = self._http("POST", "/governance/breaker/AG-05/report", {"ok": True}, token="svc-test")
        self.assertEqual(code, 403)  # no X-Keel-Agent: cannot report for AG-05
        code, body = self._http("POST", "/governance/events", {"type": "x"}, token="svc-test")
        self.assertEqual(code, 400)
        code, body = self._http("POST", "/governance/breaker/AG-05/kill", {}, token="adm-test")
        self.assertEqual((code, body["state"]), (200, "OPEN"))
        code, body = self._http("POST", "/governance/breaker/AG-05/reset", {}, token="adm-test")
        self.assertEqual(body["state"], "CLOSED")


class EntraAuthTests(unittest.TestCase):
    """Verifies Entra ID tokens the way Copilot presents them, using a local signing key."""

    @classmethod
    def setUpClass(cls) -> None:
        import jwt
        from cryptography.hazmat.primitives.asymmetric import rsa
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(cls.key.public_key()))
        jwk.update(kid="k1", use="sig", alg="RS256")
        path = os.path.join(_tmp, "jwks.json")
        Path(path).write_text(json.dumps({"keys": [jwk]}))
        cls.env = {"KEEL_AUTH": "entra", "KEEL_ENTRA_TENANT_ID": "tid-1", "KEEL_ENTRA_AUDIENCE": "api://keel-gateway", "KEEL_ENTRA_JWKS_FILE": path}

    def token(self, **over):
        import jwt
        claims = {"iss": "https://login.microsoftonline.com/tid-1/v2.0", "aud": "api://keel-gateway", "oid": "oid-123", "tid": "tid-1",
                  "roles": ["SalesAdvisor.User"], "exp": int(time.time()) + 600} | over
        return jwt.encode(claims, self.key, algorithm="RS256", headers={"kid": "k1"})

    def auth(self, token: str | None, path: str = "/mcp/agents/FD-01"):
        from keel_gateway import auth
        old = {k: os.environ.get(k) for k in self.env}
        os.environ.update(self.env)
        try:
            return auth.authenticate(path, {"authorization": "Bearer " + token} if token else {}, {})
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_valid_token(self) -> None:
        p, path = self.auth(self.token())
        self.assertEqual((p.kind, p.agent_id, p.user, path), ("user", "FD-01", "oid-123", "/mcp"))

    def test_rejections(self) -> None:
        from keel_gateway.auth import AuthError
        for bad in (None, self.token(aud="api://other"), self.token(roles=[]), self.token(exp=int(time.time()) - 10), self.token() + "x"):
            with self.assertRaises(AuthError):
                self.auth(bad)
        with self.assertRaises(AuthError):
            self.auth(self.token(), path="/mcp")  # Copilot callers must use /mcp/agents/<id>
        # identity headers are ignored for people: only the token counts
        p, _ = self.auth(self.token())
        self.assertIsNone(p.persona)


if __name__ == "__main__":
    unittest.main()
