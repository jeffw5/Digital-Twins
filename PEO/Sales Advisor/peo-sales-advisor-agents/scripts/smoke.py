"""End-to-end smoke test: gateway + agents host with the offline model, driven over MCP the
way Copilot drives it. No Foundry or Microsoft 365 access needed.

    python scripts/smoke.py
"""
from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def wait(url: str) -> None:
    for _ in range(100):
        try:
            urllib.request.urlopen(url, timeout=1)  # noqa: S310
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("did not start: " + url)


def post(url: str, body: dict, token: str) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
        return json.loads(r.read())


async def mcp(url: str, agent: str, tool: str, args: dict):
    import httpx2
    from mcp.client.session import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    async with httpx2.AsyncClient(timeout=60) as hc:
        async with streamable_http_client(f"{url}/mcp/agents/{agent}", http_client=hc) as st:
            async with ClientSession(st[0], st[1]) as s:
                await s.initialize()
                return await s.call_tool(tool, args)


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    gw_port, ag_port, token = free_port(), free_port(), "smoke-secret"
    env = os.environ | {"KEEL_REGISTRY": str(ROOT / "registry" / "agent-registry.json"), "KEEL_SERVICE_TOKEN": token, "KEEL_HOST_TOKEN": token,
                        "KEEL_AUDIT_PATH": str(tmp / "audit.jsonl"), "KEEL_EVENTS_PATH": str(tmp / "events.jsonl"), "KEEL_OFFLINE_MODEL": "1", "KEEL_GATEWAY_TOKEN": token}
    gw = subprocess.Popen([sys.executable, "-m", "keel_gateway.server"], cwd=ROOT / "keel-gateway",
                          env=env | {"KEEL_PORT": str(gw_port), "KEEL_AGENTS_HOST_URL": f"http://127.0.0.1:{ag_port}",
                                     "KEEL_EVENT_SINK_URL": f"http://127.0.0.1:{ag_port}/events"})
    ag = subprocess.Popen([sys.executable, "-m", "keel_agents.host"], cwd=ROOT / "agents",
                          env=env | {"KEEL_AGENTS_PORT": str(ag_port), "KEEL_GATEWAY_URL": f"http://127.0.0.1:{gw_port}"})
    try:
        wait(f"http://127.0.0.1:{gw_port}/healthz")
        wait(f"http://127.0.0.1:{ag_port}/healthz")
        url = f"http://127.0.0.1:{gw_port}"
        r = asyncio.run(mcp(url, "FD-01", "advisor_ask", {"persona": "client_admin", "question": "Are we eligible given our states?", "job_step": "CA-J1.2"}))
        brief = json.loads(r.content[0].text)
        print("advisor_ask ->", brief["status"], [t["agent"] for t in brief["trail"]])
        assert brief["status"] == "released", brief
        r = asyncio.run(mcp(url, "AG-26", "run_value_gap_monitor", {"request": "Which Client Admin job steps are furthest from target?"}))
        print("run_value_gap_monitor ->", json.loads(r.content[0].text)["option"])
        r = asyncio.run(mcp(url, "FD-01", "content_publish", {"jsonld": {}, "kgcl": ""}))
        print("FD-01 content_publish ->", r.content[0].text[:90])
        assert r.is_error
        acc = post(f"http://127.0.0.1:{ag_port}/events", {"specversion": "1.0", "id": "e1", "source": "urn:test", "type": "com.insperity.keel.content.item.changed", "subject": "urn:doc:1", "data": {}}, token)
        print("event content.item.changed ->", acc["agents"])
        time.sleep(4)
        events = [json.loads(x)["type"] for x in (tmp / "events.jsonl").read_text().splitlines()]
        audit = (tmp / "audit.jsonl").read_text().splitlines()
        print(f"{len(events)} CloudEvents emitted, {len(audit)} audit lines")
        assert "com.insperity.keel.identity.resolved" in events
        assert "com.insperity.keel.content.extracted" in events, "event chain did not continue through the sink"
        print("SMOKE TEST PASSED")
        return 0
    finally:
        for p in (gw, ag):
            p.terminate()
            p.wait(timeout=10)


if __name__ == "__main__":
    sys.exit(main())
