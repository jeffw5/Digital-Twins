"""Keel Gateway: the one governed door between Copilot (Microsoft 365 Copilot declarative
agents, Copilot Studio, Agent Framework agents in Foundry) and the Sales Advisor
microservices.

* MCP (Streamable HTTP) at /mcp/agents/<agent-id> (Copilot) or /mcp (hosted agents with the
  service token). Every microservice operation is a tool; agents exposed in Copilot also get
  a run_<agent> tool that invokes the hosted agent.
* Every caller is authenticated (auth.py); every call passes the policy enforcement point in
  governance.py, is written to the audit log and, for writes, emits a CloudEvent.
* /governance/* routes are for Keel services only (breaker reports, events, approvals); they
  are not MCP tools, so a model can never call them.

Run:  python -m keel_gateway.server        (KEEL_HOST, KEEL_PORT; default 127.0.0.1:8080)
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import mcp.types as T
from mcp.server.lowlevel import Server
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import auth
from .backends import Backends
from .governance import CallContext, Governance
from .registry import Registry, load

log = logging.getLogger("keel_gateway")

INSTRUCTIONS = (
    "Governed tools for the PEO Sales Advisor. Every call is checked against the SSOT: the calling agent's "
    "tool allow-list, its circuit-breaker state, persona entitlements and the Simplex gate for binding actions. "
    "Denied calls return the rule IDs that denied them."
)


def _tool_objects(reg: Registry) -> list[T.Tool]:
    tools: list[T.Tool] = []
    for op in reg.operations.values():
        tools.append(T.Tool(
            name=op.name, title=op.name.replace("_", " ").capitalize(), description=op.description, inputSchema=op.input_schema,
            annotations=T.ToolAnnotations(read_only_hint=op.read_only, destructive_hint=op.destructive,
                                          idempotent_hint=op.idempotent, open_world_hint=False),
        ))
    for a in reg.agents.values():
        if a.get("surface") == "both":
            tools.append(T.Tool(
                name=reg.run_tool_name(a), title=f"Run {a['name']}",
                description=f"Ask the hosted {a['name']} ({a['id']}) to do its job: {a['decision']}. It runs under its circuit breaker and returns its decision, options considered, citations and whether a person must decide.",
                inputSchema={"type": "object", "properties": {
                    "request": {"type": "string", "description": "What you want the agent to do, in plain words"},
                    "context": {"type": "object", "description": "Optional context: persona, job step, prospect URI, period"}},
                    "required": ["request"]},
                annotations=T.ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=False, open_world_hint=False),
            ))
    return tools


def _principal(req: Request | None) -> auth.Principal | None:
    if req is None:
        return None
    return getattr(req.state, "keel_principal", None)


def _ctx(req: Request | None) -> CallContext:
    p = _principal(req)
    trace = req.headers.get("traceparent") if req is not None else None
    if p is None:  # in-process use without the auth middleware: no identity, so everything is denied
        return CallContext(agent_id=None, user=None, persona=None, tenant=None, traceparent=trace, kind="none")
    return CallContext(agent_id=p.agent_id, user=p.user, persona=p.persona, tenant=p.tenant, traceparent=trace, kind=p.kind, roles=p.roles)


def build_server(reg: Registry | None = None) -> tuple[Server, Governance, Backends, Registry]:
    reg = reg or load()
    gov = Governance(reg)
    be = Backends(reg)
    all_tools = _tool_objects(reg)

    async def on_list_tools(ctx: Any, params: Any) -> T.ListToolsResult:
        c = _ctx(getattr(ctx, "request", None))
        allowed = reg.allowed_tools(c.agent_id)  # least privilege: only the caller's allow-list (CON-045)
        return T.ListToolsResult(tools=[t for t in all_tools if t.name in allowed])

    async def on_call_tool(ctx: Any, params: T.CallToolRequestParams) -> T.CallToolResult:
        c = _ctx(getattr(ctx, "request", None))
        name, args = params.name, dict(params.arguments or {})
        op = reg.operations.get(name)
        if not op and not (name.startswith("run_") and any(reg.run_tool_name(a) == name for a in reg.agents.values())):
            from .governance import Decision
            d = Decision(False, f"Unknown tool {name}", ["CON-045"])
            gov.audit(c, name, args, d, None)
            return _error(f"Unknown tool {name}.")
        decision = gov.authorize(c, op, name, args)
        if not decision.allowed:
            gov.audit(c, name, args, decision, None)
            return _error(f"Denied: {decision.reason} Rules: {', '.join(decision.rules)}. Policy decision {decision.decision_id}.")
        try:
            if name == "simplex_request_approval":
                result: Any = gov.approvals.request(args["action"], args.get("payload") or {}, args.get("rationale", ""), c.user or c.agent_id or "unknown")
            elif name == "simplex_status":
                result = gov.approvals.get(args["approval_id"]) or {"approval_id": args["approval_id"], "status": "unknown"}
            elif name == "breaker_state":
                result = gov.breakers.state(args["agent_id"])
            else:
                result = await be.call(c, name, args)
        except Exception:  # noqa: BLE001 - never crash or leak backend details to the model
            log.exception("tool %s failed (correlation %s)", name, c.correlation_id)
            gov.audit(c, name, args, decision, {"error": "backend failure"})
            return _error(f"{name} could not complete. Correlation ID {c.correlation_id}.")
        gov.audit(c, name, args, decision, result)
        if op and not op.read_only:
            gov.emit(c, "com.insperity.keel.tool." + name, f"urn:keel:tool:{name}", {"decision_id": decision.decision_id, "result": result})
        return T.CallToolResult(content=[T.TextContent(type="text", text=json.dumps(result, default=str))],
                                structured_content=result if isinstance(result, dict) else {"result": result})

    server = Server("keel-gateway", version=reg.raw["meta"]["version"], instructions=INSTRUCTIONS,
                    on_list_tools=on_list_tools, on_call_tool=on_call_tool)
    return server, gov, be, reg


def _error(text: str) -> T.CallToolResult:
    return T.CallToolResult(content=[T.TextContent(type="text", text=text)], is_error=True)


def _service(req: Request) -> auth.Principal | None:
    p = _principal(req)
    return p if p and p.kind in ("service", "dev") else None


def _admin(req: Request) -> auth.Principal | None:
    p = _principal(req)
    return p if p and (p.admin or p.kind == "dev") else None


async def _json(req: Request) -> dict[str, Any]:
    try:
        body = await req.json()
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


def create_app():
    auth.check_startup()
    server, gov, _be, reg = build_server()

    async def healthz(_: Request) -> JSONResponse:
        return JSONResponse({"ok": True, "agents": len(reg.agents), "tools": len(reg.operations), "auth": auth.mode()})

    async def breaker_get(req: Request) -> JSONResponse:
        if not _service(req):
            return JSONResponse({"error": "service token required"}, status_code=403)
        return JSONResponse(gov.breakers.state(req.path_params["agent_id"]))

    async def breaker_report(req: Request) -> JSONResponse:
        p = _service(req)
        agent_id = req.path_params["agent_id"].upper()
        if not p or (p.kind == "service" and not p.admin and p.agent_id != agent_id):  # an agent reports only its own outputs
            return JSONResponse({"error": "only the agent's runtime may report its outputs"}, status_code=403)
        body = await _json(req)
        signals = body.get("failed_signals") or []
        if not isinstance(signals, list):
            return JSONResponse({"error": "failed_signals must be a list"}, status_code=400)
        try:
            return JSONResponse(gov.breakers.report(agent_id, bool(body.get("ok")), signals))
        except KeyError:
            return JSONResponse({"error": "unregistered agent (CON-044)"}, status_code=404)

    async def breaker_kill(req: Request) -> JSONResponse:
        p = _admin(req)
        if not p:  # owner kill switch (AIG-009)
            return JSONResponse({"error": "owner token required"}, status_code=403)
        try:
            return JSONResponse(gov.breakers.kill(req.path_params["agent_id"], p.user or "owner"))
        except KeyError:
            return JSONResponse({"error": "unregistered agent (CON-044)"}, status_code=404)

    async def breaker_reset(req: Request) -> JSONResponse:
        if not _admin(req):  # owner reset after root cause (AIG-003)
            return JSONResponse({"error": "owner token required"}, status_code=403)
        return JSONResponse(gov.breakers.reset(req.path_params["agent_id"]))

    async def events(req: Request) -> JSONResponse:
        p = _service(req)
        if not p:
            return JSONResponse({"error": "service token required"}, status_code=403)
        body = await _json(req)
        if not isinstance(body.get("type"), str) or not body["type"].startswith("com.insperity.keel."):
            return JSONResponse({"error": "type must be a com.insperity.keel.* CloudEvents type"}, status_code=400)
        a = reg.agent(p.agent_id)
        if p.kind == "service" and not p.admin and (not a or body["type"] not in a.get("emits", [])):
            return JSONResponse({"error": "agents may emit only their registered event types"}, status_code=403)
        return JSONResponse(gov.emit(_ctx(req), body["type"], str(body.get("subject", "")), body.get("data") if isinstance(body.get("data"), dict) else {}), status_code=202)

    async def approval_grant(req: Request) -> JSONResponse:
        p = _admin(req)
        if not p:
            return JSONResponse({"error": "approver token required"}, status_code=403)
        approver = p.user or ""  # the approver's identity comes from the authenticated caller, not the body
        try:
            return JSONResponse(gov.approvals.grant(req.path_params["approval_id"], approver))
        except PermissionError as e:
            return JSONResponse({"error": str(e)}, status_code=409)
        except KeyError:
            return JSONResponse({"error": "unknown approval"}, status_code=404)

    routes = [
        Route("/healthz", healthz),
        Route("/governance/breaker/{agent_id}", breaker_get, methods=["GET"]),
        Route("/governance/breaker/{agent_id}/report", breaker_report, methods=["POST"]),
        Route("/governance/breaker/{agent_id}/kill", breaker_kill, methods=["POST"]),
        Route("/governance/breaker/{agent_id}/reset", breaker_reset, methods=["POST"]),
        Route("/governance/events", events, methods=["POST"]),
        Route("/governance/approvals/{approval_id}/grant", approval_grant, methods=["POST"]),
    ]
    hosts = [h.strip() for h in os.getenv("KEEL_ALLOWED_HOSTS", "").split(",") if h.strip()]
    security = TransportSecuritySettings(enable_dns_rebinding_protection=bool(hosts), allowed_hosts=hosts, allowed_origins=[]) if hosts else None
    app = server.streamable_http_app(streamable_http_path="/mcp", stateless_http=True, json_response=True,
                                     host=os.getenv("KEEL_HOST", "127.0.0.1"), transport_security=security, custom_starlette_routes=routes)
    app.state.governance = gov
    return auth.AuthMiddleware(app)


def main() -> None:
    import uvicorn
    uvicorn.run(create_app(), host=os.getenv("KEEL_HOST", "127.0.0.1"), port=int(os.getenv("KEEL_PORT", "8080")))


if __name__ == "__main__":
    main()
