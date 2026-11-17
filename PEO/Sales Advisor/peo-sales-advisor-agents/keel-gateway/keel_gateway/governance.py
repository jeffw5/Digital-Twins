"""Policy enforcement point (PEP) for every tool call that reaches the Keel Gateway.

Each check cites the SSOT rule or constraint it enforces. In production the policy decision
comes from the Policy Decision Service (MS-01, OPA/Rego compiled from the SSOT); the local
checks below mirror that policy so the gateway can run on a laptop.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import Operation, Registry

CLOSED, HALF_OPEN, OPEN = "CLOSED", "HALF-OPEN", "OPEN"


@dataclass
class CallContext:
    agent_id: str | None          # from the authenticated caller (auth.py), never from tool arguments
    user: str | None              # Entra object ID for people; None for hosted agents
    persona: str | None
    tenant: str | None
    traceparent: str | None
    kind: str = "dev"             # service | user | dev
    roles: list[str] = field(default_factory=list)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Decision:
    allowed: bool
    reason: str
    rules: list[str]
    decision_id: str = field(default_factory=lambda: "pd-" + uuid.uuid4().hex[:12])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def payload_hash(action: str, payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "approval_id"}
    return hashlib.sha256(json.dumps({"action": action, "payload": body}, sort_keys=True, default=str).encode()).hexdigest()


def validate_args(schema: dict[str, Any], args: dict[str, Any]) -> str | None:
    """Check arguments against the tool's input schema (the low-level server does not)."""
    import jsonschema  # installed with mcp
    try:
        jsonschema.validate(args, schema)
    except jsonschema.ValidationError as e:
        return f"Invalid arguments: {e.message}"
    return None


class Breakers:
    """Per-agent MTBH circuit breaker (AIG-002, AIG-003, AIG-008, AIG-009, GOV-014, CON-046).

    MTBH = outputs / integrity faults. With enough evidence (at least the tier's open floor
    in outputs) the tier floors apply: HALF-OPEN below `floor`, OPEN below `open`. Before
    that, consecutive faults decide: 2 in a row is HALF-OPEN, 3 in a row is OPEN (AIG-002).
    A hard-trip signal (AIG-003, e.g. IS-5) or the owner's kill switch (AIG-009) opens the
    breaker at once; only the owner resets it after root cause. Only the agent runtime
    (an authenticated Keel service) reports outputs. Counts are in memory here; production
    keeps them in MS-12 over a rolling 30 days.
    """

    def __init__(self, registry: Registry):
        self.reg = registry
        self._lock = threading.Lock()
        self._s: dict[str, dict[str, Any]] = {}

    def _get(self, agent_id: str) -> dict[str, Any]:
        return self._s.setdefault(agent_id, {"outputs": 0, "faults": 0, "in_a_row": 0, "hard_trip": None, "last_fault": None})

    def state(self, agent_id: str) -> dict[str, Any]:
        a = self.reg.agent(agent_id)
        if not a:
            return {"agent_id": agent_id, "state": OPEN, "reason": "Unregistered agent (CON-044)"}
        tier = self.reg.tiers[a["tier"]]
        with self._lock:
            s = dict(self._get(a["id"]))
        mtbh = s["outputs"] / s["faults"] if s["faults"] else None
        evidence = s["outputs"] >= tier["open"]
        if s["hard_trip"]:
            st, why = OPEN, f"Opened by {s['hard_trip']}; owner reset required"
        elif s["in_a_row"] >= 3:
            st, why = OPEN, f"{s['in_a_row']} integrity faults in a row"
        elif mtbh is None:
            st, why = CLOSED, "No integrity faults"
        elif evidence and mtbh < tier["open"]:
            st, why = OPEN, f"MTBH {mtbh:.0f} below open floor {tier['open']}"
        elif evidence and mtbh < tier["floor"]:
            st, why = HALF_OPEN, f"MTBH {mtbh:.0f} below floor {tier['floor']}"
        elif s["in_a_row"] == 2:
            st, why = HALF_OPEN, "2 integrity faults in a row"
        elif not evidence:
            st, why = CLOSED, f"{s['faults']} fault(s) in {s['outputs']} outputs; MTBH floors apply from {tier['open']} outputs"
        else:
            st, why = CLOSED, f"MTBH {mtbh:.0f} at or above floor {tier['floor']}"
        return {"agent_id": a["id"], "tier": a["tier"], "state": st, "reason": why, "mtbh": mtbh,
                "outputs": s["outputs"], "faults": s["faults"], "fallback": a.get("fallback"),
                "floor": tier["floor"], "open_floor": tier["open"]}

    def report(self, agent_id: str, ok: bool, failed_signals: list[str] | None = None) -> dict[str, Any]:
        a = self.reg.agent(agent_id)
        if not a:
            raise KeyError(agent_id)
        failed = [str(x) for x in (failed_signals or [])]
        with self._lock:
            s = self._get(a["id"])
            s["outputs"] += 1
            if not ok or failed:
                s["faults"] += 1
                s["in_a_row"] += 1
                s["last_fault"] = {"at": _now(), "signals": failed}
                hard = [x for x in failed if x in a.get("hardTrip", [])]
                if hard:
                    s["hard_trip"] = hard[0]
            else:
                s["in_a_row"] = 0
        return self.state(a["id"])

    def fault(self, agent_id: str) -> None:
        """A blocked tool call by an authenticated hosted agent (AIG-007): a fault, never a hard trip."""
        a = self.reg.agent(agent_id)
        if a:
            with self._lock:
                s = self._get(a["id"])
                s["faults"] += 1
                s["in_a_row"] += 1
                s["last_fault"] = {"at": _now(), "signals": ["allow-list"]}

    def kill(self, agent_id: str, by: str) -> dict[str, Any]:
        """Owner's kill switch (AIG-009)."""
        if not self.reg.agent(agent_id):
            raise KeyError(agent_id)
        with self._lock:
            self._get(agent_id.upper())["hard_trip"] = f"kill switch by {by}"
        return self.state(agent_id)

    def reset(self, agent_id: str) -> dict[str, Any]:
        with self._lock:
            self._s.pop(agent_id.upper(), None)
        return self.state(agent_id)


class Approvals:
    """Simplex action gate (GOV-015, DEC-004, CON-028). An approval covers one action with one
    exact payload, is used once, and is granted by an authenticated person other than the
    requester (CTL-013). Production approvals come from the Simplex Action Gate (MS-11)."""

    def __init__(self) -> None:
        self._a: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def request(self, action: str, payload: dict[str, Any], rationale: str, requested_by: str) -> dict[str, Any]:
        aid = "apr-" + uuid.uuid4().hex[:10]
        rec = {"approval_id": aid, "action": action, "payload": payload, "payload_hash": payload_hash(action, payload),
               "rationale": rationale, "requested_by": requested_by, "status": "pending", "requested_at": _now()}
        with self._lock:
            self._a[aid] = rec
        return dict(rec)

    def get(self, aid: str) -> dict[str, Any] | None:
        with self._lock:
            r = self._a.get(aid)
            return dict(r) if r else None

    def grant(self, aid: str, approver: str) -> dict[str, Any]:
        if not approver:
            raise PermissionError("An approver identity is required")
        with self._lock:
            a = self._a[aid]
            if approver == a.get("requested_by"):
                raise PermissionError("The requester cannot approve their own action (CTL-013)")
            if a["status"] != "pending":
                raise PermissionError(f"Approval is {a['status']}")
            a.update(status="approved", approver=approver, approved_at=_now())
            return dict(a)

    def consume(self, aid: str, action: str, args: dict[str, Any]) -> bool:
        """True once for an approved request whose action and payload match exactly."""
        with self._lock:
            a = self._a.get(aid)
            if not a or a["status"] != "approved" or a["action"] != action or a["payload_hash"] != payload_hash(action, args):
                return False
            a.update(status="used", used_at=_now())
            return True


class Governance:
    def __init__(self, registry: Registry):
        self.reg = registry
        self.breakers = Breakers(registry)
        self.approvals = Approvals()
        self.audit_path = Path(os.getenv("KEEL_AUDIT_PATH", "keel-audit.jsonl"))
        self.events_path = Path(os.getenv("KEEL_EVENTS_PATH", "keel-events.jsonl"))
        self._audit_key = (os.getenv("KEEL_AUDIT_KEY") or "").encode()
        self._audit_lock = threading.Lock()
        self._prev_hash = self._last_hash()

    # ---------- policy ----------
    def authorize(self, ctx: CallContext, op: Operation | None, tool: str, args: dict[str, Any]) -> Decision:
        agent = self.reg.agent(ctx.agent_id)
        if not agent:
            return Decision(False, "Calls must come from a registered agent.", ["AIG-001", "CON-044"])
        if tool not in self.reg.allowed_tools(agent["id"]):
            if ctx.kind == "service":  # only an authenticated hosted agent's own mistakes count against its breaker
                self.breakers.fault(agent["id"])
            return Decision(False, f"{tool} is not on {agent['id']}'s tool allow-list.", ["AIG-007", "CON-045"])
        if op:
            bad = validate_args(op.input_schema, args)
            if bad:
                return Decision(False, bad, ["CON-045"])
        br = self.breakers.state(agent["id"])
        read_only = op.read_only if op else True
        if br["state"] == OPEN:
            return Decision(False, f"{agent['id']} breaker is OPEN ({br['reason']}). Fallback: {agent.get('fallback')}", ["AIG-002", "CON-046"])
        if br["state"] == HALF_OPEN and not read_only:
            return Decision(False, f"{agent['id']} breaker is HALF-OPEN: advise only; a person must approve writes.", ["AIG-002", "CON-046"])
        if op and op.persona_output:  # output written for a persona (EXT-006): only the personas this agent serves
            if args.get("persona") not in agent.get("personas", []):
                return Decision(False, f"{agent['id']} produces output only for {', '.join(agent.get('personas', [])) or 'no persona'}.", ["EXT-006", "CON-019"])
        if tool == "advisor_record_decision":
            if args.get("confirmed_by_person") is not True:
                return Decision(False, "Ask the person to confirm the decision in chat before recording it.", ["DEC-004", "DEC-007", "CON-028"])
            if ctx.kind != "dev" and not ctx.user:
                return Decision(False, "Only an authenticated person can record a decision.", ["DEC-004", "CON-028"])
        if op and op.simplex_gate:  # checked last: consuming the approval must be the final step
            if not self.approvals.consume(str(args.get("approval_id", "")), tool, args):
                return Decision(False, "Binding action needs an approved, unused Simplex request for this exact action and payload.", ["GOV-015", "DEC-004", "CON-028"])
        return Decision(True, "Permitted", ["GOD-001", "GOV-012"])

    # ---------- evidence ----------
    def _last_hash(self) -> str:
        try:
            with self.audit_path.open("rb") as f:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - 16384))
                lines = f.read().decode("utf-8", "ignore").strip().splitlines()
            return self._digest(lines[-1]) if lines else "0" * 64
        except FileNotFoundError:
            return "0" * 64

    def _digest(self, line: str) -> str:
        if self._audit_key:
            return hmac.new(self._audit_key, line.encode(), hashlib.sha256).hexdigest()
        return hashlib.sha256(line.encode()).hexdigest()

    def audit(self, ctx: CallContext, tool: str, args: dict[str, Any], decision: Decision, result: Any | None) -> None:
        """Action log (CTL-007, GOV-022): each line carries the digest of the previous line
        (HMAC with KEEL_AUDIT_KEY when set) and the chain continues across restarts; inputs
        and outputs are logged by hash only. In production, ship lines to an append-only store
        (for example immutable Blob storage) and run one writer per chain."""
        rec = {
            "at": _now(), "agent": ctx.agent_id, "caller": ctx.kind, "user": ctx.user, "persona": ctx.persona, "tenant": ctx.tenant,
            "tool": tool, "allowed": decision.allowed, "reason": decision.reason, "rules": decision.rules,
            "decision_id": decision.decision_id, "correlation_id": ctx.correlation_id, "traceparent": ctx.traceparent,
            "input_hash": hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest(),
            "output_hash": hashlib.sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest() if result is not None else None,
        }
        with self._audit_lock:
            rec["prev"] = self._prev_hash
            line = json.dumps(rec, sort_keys=True)
            self._prev_hash = self._digest(line)
            with self.audit_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def emit(self, ctx: CallContext, type_: str, subject: str, data: dict[str, Any]) -> dict[str, Any]:
        """CloudEvents 1.0 envelope with the SSOT extensions (EVT-001)."""
        ev = {
            "specversion": "1.0", "id": str(uuid.uuid4()), "source": "urn:insperity:keel-gateway",
            "type": type_, "subject": subject, "time": _now(), "datacontenttype": "application/json",
            "tenant": ctx.tenant, "persona": ctx.persona, "correlationid": ctx.correlation_id,
            "traceparent": ctx.traceparent, "agent": ctx.agent_id, "data": data,
        }
        with self._audit_lock:
            with self.events_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ev) + "\n")
        sink = os.getenv("KEEL_EVENT_SINK_URL")  # the agents host /events locally; Event Grid in production
        if sink:
            threading.Thread(target=_deliver, args=(sink, ev), daemon=True).start()
        return ev


def _deliver(url: str, ev: dict[str, Any]) -> None:
    import urllib.request
    headers = {"Content-Type": "application/cloudevents+json"}
    if os.getenv("KEEL_SERVICE_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["KEEL_SERVICE_TOKEN"]
    try:
        urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(ev).encode(), headers=headers, method="POST"), timeout=10)  # noqa: S310
    except OSError:
        pass  # the broker retries in production; locally the JSONL file keeps the event
