"""Agent host: runs the agents for events and for Copilot.

  POST /events                 CloudEvents 1.0 (structured JSON, e.g. from Event Grid) ->
                               every agent subscribed to the event type runs in the background
  POST /agents/{agent_id}/run  {"request": str, "context": {}} -> the agent's checked output
                               (the gateway's run_<agent> tools call this for Copilot)
  POST /pipelines/advisor      advisor_ask: the governed answer pipeline
  GET  /healthz

Run:  python -m keel_agents.host      (KEEL_AGENTS_HOST, KEEL_AGENTS_PORT; default 127.0.0.1:8090)
Every route except /healthz needs KEEL_HOST_TOKEN as a bearer token (the gateway's
KEEL_SERVICE_TOKEN). Without a token the host only starts on a loopback address with
KEEL_DEV=1. Events are deduplicated by id and at most KEEL_MAX_RUNS agents run at once.
"""
from __future__ import annotations

import asyncio
import hmac
import ipaddress
import logging
import os
from collections import OrderedDict
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import pipeline
from .agents import TASKS
from .registry import REGISTRY
from .runtime import GovernedAgent, subscribers

log = logging.getLogger("keel_agents.host")
_background: set[asyncio.Task[Any]] = set()
_seen: OrderedDict[str, None] = OrderedDict()
_slots = asyncio.Semaphore(int(os.getenv("KEEL_MAX_RUNS", "8")))


def _loopback(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host == "localhost"


def check_startup() -> None:
    if not os.getenv("KEEL_HOST_TOKEN"):
        if not (os.getenv("KEEL_DEV") == "1" and _loopback(os.getenv("KEEL_AGENTS_HOST", "127.0.0.1"))):
            raise SystemExit("Set KEEL_HOST_TOKEN (or KEEL_DEV=1 on a loopback address for local development).")


def _authorized(req: Request) -> bool:
    tok = os.getenv("KEEL_HOST_TOKEN")
    if not tok:
        return os.getenv("KEEL_DEV") == "1"
    got = req.headers.get("authorization", "")
    return hmac.compare_digest(got.encode(), ("Bearer " + tok).encode())


async def _body(req: Request) -> dict[str, Any] | None:
    try:
        b = await req.json()
    except ValueError:
        return None
    return b if isinstance(b, dict) else None


async def _run_limited(agent_id: str, text: str, ctx: dict[str, Any], subject: str) -> None:
    async with _slots:
        try:
            await GovernedAgent.from_registry(agent_id).run(text, ctx, subject=subject)
        except Exception:  # noqa: BLE001 - background runs must not die silently
            log.exception("agent %s failed on %s", agent_id, subject)


async def events(req: Request) -> JSONResponse:
    if not _authorized(req):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    ev = await _body(req)
    if not ev or ev.get("specversion") != "1.0" or not isinstance(ev.get("type"), str) or not ev.get("id"):
        return JSONResponse({"error": "CloudEvents 1.0 envelope required (EVT-001)"}, status_code=400)
    if ev["id"] in _seen:
        return JSONResponse({"accepted": ev["id"], "duplicate": True, "agents": []}, status_code=202)
    _seen[ev["id"]] = None
    while len(_seen) > 10000:
        _seen.popitem(last=False)
    started = []
    for agent_id in subscribers(ev["type"]):
        task = TASKS.get(agent_id)
        if not task:
            continue
        ctx = {"event": {k: ev.get(k) for k in ("type", "subject", "tenant", "persona", "correlationid")}}
        t = asyncio.create_task(_run_limited(agent_id, task(ev), ctx, str(ev.get("subject", ""))))
        _background.add(t)
        t.add_done_callback(_background.discard)
        started.append(agent_id)
    return JSONResponse({"accepted": ev["id"], "agents": started}, status_code=202)


async def run_agent(req: Request) -> JSONResponse:
    if not _authorized(req):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    body = await _body(req)
    if body is None or not isinstance(body.get("request"), str):
        return JSONResponse({"error": "body must be {request: str, context: object}"}, status_code=400)
    try:
        agent = GovernedAgent.from_registry(req.path_params["agent_id"])
    except KeyError as e:
        return JSONResponse({"error": str(e)}, status_code=404)
    ctx = body.get("context") if isinstance(body.get("context"), dict) else {}
    async with _slots:
        return JSONResponse(await agent.run(body["request"], ctx))


async def advisor(req: Request) -> JSONResponse:
    if not _authorized(req):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    b = await _body(req)
    if b is None or not isinstance(b.get("persona"), str) or not isinstance(b.get("question"), str):
        return JSONResponse({"error": "body must include persona and question"}, status_code=400)
    return JSONResponse(await pipeline.ask(b["persona"], b["question"], b.get("job_step"), b.get("prospect_uri")))


async def healthz(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True, "agents": len(REGISTRY["agents"])})


app = Starlette(routes=[
    Route("/events", events, methods=["POST"]),
    Route("/agents/{agent_id}/run", run_agent, methods=["POST"]),
    Route("/pipelines/advisor", advisor, methods=["POST"]),
    Route("/healthz", healthz),
])


def main() -> None:
    import uvicorn
    check_startup()
    uvicorn.run(app, host=os.getenv("KEEL_AGENTS_HOST", "127.0.0.1"), port=int(os.getenv("KEEL_AGENTS_PORT", "8090")))


if __name__ == "__main__":
    main()
