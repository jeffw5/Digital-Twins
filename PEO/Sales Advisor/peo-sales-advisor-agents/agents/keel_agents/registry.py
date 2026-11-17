"""Agent registry and generated instructions (both produced by the Agent Editor)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY: dict[str, Any] = json.loads(Path(os.getenv("KEEL_REGISTRY", ROOT / "registry" / "agent-registry.json")).read_text(encoding="utf-8"))
_BY_ID = {a["id"]: a for a in REGISTRY["agents"]}
INSTRUCTIONS_DIR = Path(__file__).resolve().parents[1] / "instructions"


def spec_for(agent_id: str) -> dict[str, Any]:
    try:
        return _BY_ID[agent_id.upper()]
    except KeyError:
        raise KeyError(f"{agent_id} is not registered (AIG-001)") from None


def instructions_for(spec: dict[str, Any]) -> str:
    return (INSTRUCTIONS_DIR / f"{spec['slug']}.md").read_text(encoding="utf-8")
