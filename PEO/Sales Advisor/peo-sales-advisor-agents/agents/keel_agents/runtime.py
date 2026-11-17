"""Governed runtime for the Sales Advisor agents, built on Microsoft Agent Framework
with a Microsoft Foundry model.

Each agent:
  1. is registered (AIG-001): its spec, tools, rules and breaker profile come from the registry;
  2. checks its circuit breaker before it runs (CON-046) and runs its fallback when OPEN;
  3. reaches data and services only through the Keel Gateway's MCP endpoint, limited to its
     own allow-list (CON-045) - the gateway enforces the same list server-side;
  4. returns the JSON output contract, which is checked for integrity signals (AIG-008);
  5. reports the outcome to the breaker and emits its CloudEvent (EVT-001).

Environment:
  FOUNDRY_PROJECT_ENDPOINT   Foundry project endpoint
  FOUNDRY_MODEL              model deployment for 'standard' agents
  FOUNDRY_REASONING_MODEL    model deployment for 'reasoning' (tier-1) agents; defaults to FOUNDRY_MODEL
  KEEL_GATEWAY_URL           e.g. https://keel-gateway.internal (MCP at /mcp)
  KEEL_GATEWAY_TOKEN         bearer token the gateway accepts from the agent host (optional)
  KEEL_OFFLINE_MODEL=1       deterministic stand-in model for smoke tests (no Foundry calls)
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import urllib.request
from pathlib import Path
from typing import Any, Awaitable, Callable

from . import contract
from .registry import REGISTRY, instructions_for, spec_for

log = logging.getLogger("keel_agents")
GATEWAY = os.getenv("KEEL_GATEWAY_URL", "http://127.0.0.1:8080").rstrip("/")
ModelRunner = Callable[[dict[str, Any], str], Awaitable[str]]


# ------------------------------------------------------------------ gateway (governance routes)
def _http(method: str, path: str, body: dict[str, Any] | None = None, agent_id: str | None = None) -> Any:
    headers = {"Content-Type": "application/json"}
    if agent_id:
        headers["X-Keel-Agent"] = agent_id
    if os.getenv("KEEL_GATEWAY_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["KEEL_GATEWAY_TOKEN"]
    req = urllib.request.Request(GATEWAY + path, method=method, headers=headers,
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 - operator-configured URL
        return json.loads(r.read().decode() or "null")


class Gateway:
    async def breaker(self, agent_id: str) -> dict[str, Any]:
        return await asyncio.to_thread(_http, "GET", f"/governance/breaker/{agent_id}", None, agent_id)

    async def report(self, agent_id: str, ok: bool, failed: list[str]) -> dict[str, Any]:
        return await asyncio.to_thread(_http, "POST", f"/governance/breaker/{agent_id}/report", {"ok": ok, "failed_signals": failed}, agent_id)

    async def emit(self, agent_id: str, type_: str, subject: str, data: dict[str, Any]) -> Any:
        return await asyncio.to_thread(_http, "POST", "/governance/events", {"type": type_, "subject": subject, "data": data}, agent_id)


# ------------------------------------------------------------------ model runner (Agent Framework)
async def agent_framework_runner(spec: dict[str, Any], prompt: str) -> str:
    """Run one turn with Microsoft Agent Framework: a Foundry chat client plus the Keel
    Gateway as a Streamable HTTP MCP tool restricted to this agent's allow-list."""
    from agent_framework import Agent, MCPStreamableHTTPTool  # pip install agent-framework-foundry
    from agent_framework.foundry import FoundryChatClient
    from azure.identity.aio import DefaultAzureCredential

    model = os.getenv("FOUNDRY_REASONING_MODEL") if spec.get("model") == "reasoning" else None
    model = model or os.environ["FOUNDRY_MODEL"]
    headers = {"X-Keel-Agent": spec["id"]}
    if os.getenv("KEEL_GATEWAY_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["KEEL_GATEWAY_TOKEN"]
    mcp_kwargs: dict[str, Any] = dict(name="keel-gateway", url=GATEWAY + "/mcp", header_provider=lambda _kw: headers)
    async with DefaultAzureCredential() as cred:
        client = FoundryChatClient(project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], model=model, credential=cred)
        try:
            tool = MCPStreamableHTTPTool(**mcp_kwargs, allowed_tools=list(spec["tools"]))
        except TypeError:  # older builds without allowed_tools; the gateway still enforces the list
            tool = MCPStreamableHTTPTool(**mcp_kwargs)
        async with tool as mcp_server, Agent(client=client, name=spec["slug"], instructions=instructions_for(spec)) as agent:
            result = await agent.run(prompt, tools=mcp_server)
            return getattr(result, "text", str(result))


async def offline_runner(spec: dict[str, Any], prompt: str) -> str:
    """Deterministic stand-in for the model (KEEL_OFFLINE_MODEL=1): picks the first option and
    cites a placeholder, so the governed flow can be smoke-tested without Foundry. Its output
    is labelled offline and must never be shown to a persona."""
    opts = contract.enumerable_options(spec)
    return json.dumps({
        "decision": spec["decision"], "option": opts[0] if opts else "offline", "options_considered": opts or ["offline"],
        "confidence": 0.5, "outputs": {"offline": True}, "citations": [{"uri": "urn:keel:offline", "span": "none"}],
        "rules_applied": spec["rules"][:1], "needs_human": False, "notes": "Offline model: not a real answer.",
    })


def default_runner() -> ModelRunner:
    return offline_runner if os.getenv("KEEL_OFFLINE_MODEL") == "1" else agent_framework_runner


# ------------------------------------------------------------------ governed agent
class GovernedAgent:
    def __init__(self, spec: dict[str, Any], runner: ModelRunner | None = None, gateway: Gateway | None = None):
        self.spec = spec
        self.runner = runner or default_runner()
        self.gateway = gateway or Gateway()

    @classmethod
    def from_registry(cls, agent_id: str, **kw: Any) -> "GovernedAgent":
        return cls(spec_for(agent_id), **kw)

    def prompt(self, request: str, context: dict[str, Any] | None = None) -> str:
        return (f"{request}\n\nContext bundle (WHO, WHAT, WHEN, WHERE, WHY): {json.dumps(context or {}, default=str)}\n\n"
                "Return only the JSON output contract described in your instructions.")

    async def run(self, request: str, context: dict[str, Any] | None = None, subject: str = "") -> dict[str, Any]:
        sid = self.spec["id"]
        br = await self.gateway.breaker(sid)
        if br.get("state") == "OPEN":
            return contract.fallback(self.spec, f"Breaker OPEN: {br.get('reason')}.")
        try:
            text = await self.runner(self.spec, self.prompt(request, context))
            out = contract.parse(text)
            failed = contract.check(self.spec, out)
        except Exception as e:  # noqa: BLE001 - model, tool or parsing failure: count it and fail closed
            log.warning("%s run failed: %s", sid, e)
            out, failed = {}, ["IS-4"]
        state = await self.gateway.report(sid, ok=not failed, failed=failed)
        if failed:
            # The rejected output is never returned: it may hold exactly what the check blocked (e.g. IS-5).
            res = contract.fallback(self.spec, f"Integrity check failed on {', '.join(failed)}.")
            res["outputs"]["rejected_output_hash"] = hashlib.sha256(json.dumps(out, sort_keys=True, default=str).encode()).hexdigest()
            return res
        if br.get("state") == "HALF-OPEN" or state.get("state") == "HALF-OPEN":
            out["needs_human"] = True  # CON-046: advise only while half-open
            out["notes"] = (str(out.get("notes", "")) + " Breaker half-open: a person must approve.").strip()
        for etype in self.spec.get("emits", [])[:1]:
            await self.gateway.emit(sid, etype, subject or f"urn:keel:agent:{sid}", {"output": out})
        return out


def subscribers(event_type: str) -> list[str]:
    return [a["id"] for a in REGISTRY["agents"] if event_type in a.get("triggers", [])]
