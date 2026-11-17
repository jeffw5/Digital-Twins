"""Calls the microservice behind each tool.

Each service has a base URL in an environment variable named in the registry
(for example KEEL_MS_19_URL for the Quoting Service Adapter). The gateway POSTs the tool
arguments as JSON to {base}/ops/{tool}. When the variable is not set the gateway answers
from the stub responses below, so Copilot and the agents can be exercised end to end
before the services exist. Stub answers are labelled "stub": true.
"""
from __future__ import annotations

import json
import os
import urllib.request
import uuid
from datetime import date, timedelta
from typing import Any

import anyio

from .governance import CallContext
from .registry import Registry

TIMEOUT = float(os.getenv("KEEL_BACKEND_TIMEOUT", "30"))


def _post(url: str, body: dict[str, Any], headers: dict[str, str]) -> Any:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 - URLs come from operator config
        return json.loads(r.read().decode() or "null")


def _headers(ctx: CallContext) -> dict[str, str]:
    h = {"X-Keel-Agent": ctx.agent_id or "", "X-Correlation-Id": ctx.correlation_id}
    if ctx.persona:
        h["X-Keel-Persona"] = ctx.persona
    if ctx.traceparent:
        h["traceparent"] = ctx.traceparent
    token = os.getenv("KEEL_SERVICE_TOKEN")
    if token:
        h["Authorization"] = "Bearer " + token
    return h


class Backends:
    def __init__(self, registry: Registry):
        self.reg = registry

    async def call(self, ctx: CallContext, tool: str, args: dict[str, Any]) -> Any:
        if tool.startswith("run_"):
            return await self._run_agent(ctx, tool, args)
        op = self.reg.operations[tool]
        svc = self.reg.services[op.service_id]
        base = os.getenv(svc["baseUrlEnv"])
        if tool == "advisor_ask" and not base and os.getenv("KEEL_AGENTS_HOST_URL"):
            url = os.environ["KEEL_AGENTS_HOST_URL"].rstrip("/") + "/pipelines/advisor"
            return await anyio.to_thread.run_sync(_post, url, args, _headers(ctx))
        if base:
            return await anyio.to_thread.run_sync(_post, base.rstrip("/") + "/ops/" + tool, args, _headers(ctx))
        return stub(tool, args)

    async def _run_agent(self, ctx: CallContext, tool: str, args: dict[str, Any]) -> Any:
        agent = next((a for a in self.reg.agents.values() if "run_" + a["slug"] == tool), None)
        host = os.getenv("KEEL_AGENTS_HOST_URL")
        if not agent:
            raise KeyError(tool)
        if not host:
            return {"stub": True, "agent": agent["id"], "needs_human": True,
                    "notes": "KEEL_AGENTS_HOST_URL is not set, so the hosted agent did not run."}
        url = host.rstrip("/") + f"/agents/{agent['id']}/run"
        return await anyio.to_thread.run_sync(_post, url, {"request": args.get("request", ""), "context": args.get("context") or {}}, _headers(ctx))


# ---------------------------------------------------------------- stubs
def stub(tool: str, a: dict[str, Any]) -> Any:
    today = date.today()
    s: dict[str, Any] = {"stub": True}
    if tool == "pdp_evaluate":
        return s | {"decision_id": "pd-" + uuid.uuid4().hex[:8], "allowed": True, "rules": ["GOD-001"], "explanation": "Permitted for the stated purpose."}
    if tool == "pdp_explain":
        return s | {"decision_id": a.get("decision_id"), "rules": [{"id": "EXT-006", "version": "1.0.0"}], "explanation": "Persona entitlement allowed the part."}
    if tool == "pep_check_response":
        out = []
        for p in a.get("parts", []):
            label = (p or {}).get("label", "public")
            verdict = "deny" if label in ("internal_pricing", "margin", "win_loss") else "allow"
            out.append({"id": (p or {}).get("id"), "verdict": verdict, "rule": "EXT-006" if verdict == "deny" else None})
        return s | {"parts": out}
    if tool in ("ssot_get_rule",):
        return s | {"id": a.get("id"), "status": "Released", "version": "1.0.0", "as_of": a.get("as_of") or today.isoformat(),
                    "editor_url": "https://claude.ai/artifact/BzAWvkVadS2h1mmUAMqNHR#" + str(a.get("id"))}
    if tool == "ssot_search_rules":
        return s | {"results": [{"id": "PAY-002", "name": "State Exemption Salary Thresholds Override Federal", "jurisdiction": "State"}]}
    if tool == "ssot_propose_change":
        return s | {"change_id": "chg-" + uuid.uuid4().hex[:8], "status": "Draft", "target_id": a.get("target_id")}
    if tool == "identity_resolve":
        return s | {"uri": f"https://data.insperity.example/{a.get('kind')}/{uuid.uuid5(uuid.NAMESPACE_URL, str(a.get('key')))}", "match": "exact"}
    if tool == "identity_mint":
        return s | {"uri": f"https://data.insperity.example/{a.get('kind')}/{uuid.uuid4()}", "status": "provisional"}
    if tool == "graph_query":
        return s | {"result_id": "qr-" + uuid.uuid4().hex[:8], "rows": [], "template_id": a.get("template_id")}
    if tool == "graph_facets":
        return s | {"facets": [{"name": "job_step", "values": ["CA-J1.2", "CA-J1.3"]}, {"name": "jurisdiction", "values": ["US-TX", "US-CA"]}]}
    if tool == "content_get":
        return s | {"uri": a.get("uri"), "version": "3", "labels": ["public"], "valid_until": (today + timedelta(days=180)).isoformat(),
                    "spans": [{"id": "span-1", "text": "Sample governed passage."}]}
    if tool == "content_validate":
        return s | {"conforms": True, "violations": []}
    if tool == "content_publish":
        return s | {"published": True, "kgcl_id": "kgcl-" + uuid.uuid4().hex[:8]}
    if tool == "events_publish":
        return s | {"accepted": True, "id": str(uuid.uuid4())}
    if tool == "events_schema":
        return s | {"type": a.get("type"), "schema": {"type": "object"}}
    if tool == "schedule_deadline":
        return s | {"deadline_id": "dl-" + uuid.uuid4().hex[:8], "due": a.get("due")}
    if tool == "deadlines_list":
        return s | {"deadlines": []}
    if tool == "saga_start":
        return s | {"saga_id": "saga-" + uuid.uuid4().hex[:8], "status": "running"}
    if tool == "saga_status":
        return s | {"saga_id": a.get("saga_id"), "status": "completed"}
    if tool == "decision_record":
        return s | {"decision_id": "dec-" + uuid.uuid4().hex[:8], "immutable": True}
    if tool == "decision_get":
        return s | {"decision_id": a.get("decision_id"), "option_id": "proceed", "bound_outcomes": ["DO-CA-J1-2-1"]}
    if tool == "simplex_status":
        return s | {"approval_id": a.get("approval_id"), "status": "pending"}
    if tool == "breaker_state":
        return s | {"agent_id": a.get("agent_id"), "state": "CLOSED"}
    if tool == "probes_results":
        return s | {"scope": a.get("scope"), "passed": 4, "failed": 0, "regressed": []}
    if tool == "qbd_get_baseline":
        return s | {"question_id": a.get("question_id"), "fingerprint": "fp-baseline", "frozen": "2026-10-01"}
    if tool == "qbd_classify_change":
        return s | {"question_id": a.get("question_id"), "severity": "material" if a.get("upstream_change_id") else "breaking",
                    "risk_score": 4 if a.get("upstream_change_id") else 9, "route": "SME review" if a.get("upstream_change_id") else "withdraw brief; half-open lineage breakers"}
    if tool == "metrics_query":
        cells = [{"cell": "client_admin|CA-J1.3", "n": 42, "value": 13.5}, {"cell": "hr_specialist|HR-J1.2", "n": 3, "value": None}]
        for c in cells:
            if c["n"] < 5:
                c.update(value=None, suppressed=True, rule="MET-013")
        return s | {"calc_id": a.get("calc_id"), "grain": a.get("grain"), "cells": cells}
    if tool == "metrics_definition":
        return s | {"calc_id": a.get("calc_id"), "version": "1.0.0", "status": "Released"}
    if tool == "evidence_get":
        return s | {"control_id": a.get("control_id"), "period": a.get("period"), "evidence": []}
    if tool == "controls_status":
        return s | {"control_id": a.get("control_id"), "status": "passing"}
    if tool == "census_validate":
        return s | {"census_file_id": a.get("census_file_id"), "errors": [], "warnings": [{"row": 12, "field": "state", "message": "Worksite state missing; defaulted to HQ state"}]}
    if tool == "census_status":
        return s | {"intake_id": a.get("intake_id"), "status": "validated"}
    if tool == "quote_request":
        return s | {"quote_id": "q-" + uuid.uuid4().hex[:8], "binding": False, "valid_until": (today + timedelta(days=30)).isoformat(),
                    "label": "Indicative quote (SAL-005)"}
    if tool == "quote_get":
        return s | {"quote_id": a.get("quote_id"), "binding": False, "lines": [{"line": "Admin fee", "amount_range": [95, 140], "unit": "per employee per month", "source": "quote engine v4"}]}
    if tool == "consent_check":
        return s | {"contact_uri": a.get("contact_uri"), "channel": a.get("channel"), "consented": False, "rule": "SAL-004"}
    if tool == "proposal_draft":
        return s | {"proposal_id": "p-" + uuid.uuid4().hex[:8], "status": "draft", "requires": ["licensed producer review (SAL-001)", "PEO licence disclosure (SAL-006)"]}
    if tool == "contract_send_for_signature":
        return s | {"envelope_id": "env-" + uuid.uuid4().hex[:8], "status": "sent"}
    if tool == "retention_preview":
        return s | {"dataset": a.get("dataset"), "to_delete": 0, "to_deidentify": 0}
    if tool == "agent_status":
        return s | {"agent_id": a.get("agent_id"), "status": "registered"}
    if tool == "analytics_catalog":
        return s | {"metrics": [{"name": "advisor.persona.time_to_useful_answer", "calc_id": "CALC-001", "version": "1.0.0"}]}
    if tool == "advisor_job_steps":
        return s | {"persona": a.get("persona"), "note": "Job study: see registry evals and the PEO Buyer Personas artifact."}
    if tool == "advisor_ask":
        return s | {
            "brief_id": "brief-" + uuid.uuid4().hex[:8], "persona": a.get("persona"), "job_step": a.get("job_step"),
            "ai_disclosure": "AI-assembled brief. Sources are listed; a BPA is available at every decision (DEC-010).",
            "statements": [{"text": "Stub statement. Configure KEEL_AGENTS_HOST_URL to run the governed pipeline.", "citation": {"uri": "urn:stub", "span": "span-1"}}],
            "options": [{"id": "proceed", "label": "Proceed"}, {"id": "do_nothing", "label": "Do nothing for now"}],
            "grounding": None, "status": "stub",
        }
    if tool == "advisor_record_decision":
        return s | {"decision_id": "dec-" + uuid.uuid4().hex[:8], "brief_id": a.get("brief_id"), "option_id": a.get("option_id")}
    return s | {"tool": tool, "echo": a}
