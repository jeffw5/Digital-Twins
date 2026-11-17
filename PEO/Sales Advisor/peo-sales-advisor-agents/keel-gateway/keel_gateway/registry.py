"""Loads the agent registry exported by the Agent Editor (registry/agent-registry.json).

The registry is the single source of truth for which tools exist, which agent may call
which tool (CON-045), each agent's tier and breaker profile (AIG-001, AIG-002) and the
SSOT rules, constraints and calcs each one applies.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_DEFAULT = Path(__file__).resolve().parents[2] / "registry" / "agent-registry.json"


@dataclass(frozen=True)
class Operation:
    name: str
    service_id: str
    description: str
    input_schema: dict[str, Any]
    read_only: bool
    destructive: bool
    idempotent: bool
    simplex_gate: bool
    persona_output: bool = False


@dataclass
class Registry:
    raw: dict[str, Any]
    operations: dict[str, Operation] = field(default_factory=dict)
    agents: dict[str, dict[str, Any]] = field(default_factory=dict)
    services: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def tiers(self) -> dict[str, dict[str, Any]]:
        return self.raw["tiers"]

    def agent(self, agent_id: str | None) -> dict[str, Any] | None:
        return self.agents.get((agent_id or "").upper())

    def run_tool_name(self, agent: dict[str, Any]) -> str:
        return "run_" + agent["slug"]

    def allowed_tools(self, agent_id: str | None) -> set[str]:
        """Tools an agent may call: its registered tools, plus its own run tool when it
        is exposed in Copilot (surface 'both'), plus the run tools of agents it lists."""
        a = self.agent(agent_id)
        if not a:
            return set()
        allowed = set(a["tools"])
        if a.get("surface") == "both":
            allowed.add(self.run_tool_name(a))
        for other in a.get("delegates", []):
            o = self.agent(other)
            if o:
                allowed.add(self.run_tool_name(o))
        return allowed


def input_schema(op: dict[str, Any]) -> dict[str, Any]:
    """The same schema the code generator inlines into Copilot plugin manifests."""
    if op.get("inputSchema"):
        return op["inputSchema"]
    props: dict[str, Any] = {}
    req: list[str] = []
    for p in op["params"]:
        s: dict[str, Any] = {"type": p["type"], "description": p["description"]}
        if p.get("enum"):
            s["enum"] = p["enum"]
        if p["type"] == "array":
            s["items"] = {"type": p.get("items") or "string"}
        props[p["name"]] = s
        if p.get("required"):
            req.append(p["name"])
    schema: dict[str, Any] = {"type": "object", "properties": props}
    if req:
        schema["required"] = req
    return schema


def load(path: str | os.PathLike[str] | None = None) -> Registry:
    p = Path(path or os.getenv("KEEL_REGISTRY") or _DEFAULT)
    raw = json.loads(p.read_text(encoding="utf-8"))
    reg = Registry(raw=raw)
    for s in raw["services"]:
        reg.services[s["id"]] = s
        for op in s["operations"]:
            reg.operations[op["name"]] = Operation(
                name=op["name"], service_id=s["id"], description=op["description"],
                input_schema=input_schema(op), read_only=bool(op["readOnly"]),
                destructive=bool(op.get("destructive")), idempotent=bool(op.get("idempotent")),
                simplex_gate=bool(op.get("simplexGate")), persona_output=bool(op.get("personaOutput")),
            )
    for a in raw["agents"]:
        reg.agents[a["id"]] = a
    return reg
