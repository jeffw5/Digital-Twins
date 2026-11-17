"""Output contract and integrity signals for every agent (AIG-008, IS-1 to IS-9).

Pure Python with no model or network dependency, so it is unit-tested directly.
Every agent returns one JSON object:

    {"decision": str, "option": str, "options_considered": [str], "confidence": float,
     "outputs": {...}, "citations": [{"uri": str, "span": str}], "rules_applied": [str],
     "needs_human": bool, "notes": str}
"""
from __future__ import annotations

import json
import re
from typing import Any

REQUIRED = ("decision", "option", "options_considered", "confidence", "citations", "rules_applied", "needs_human")


def parse(text: str) -> dict[str, Any]:
    """Take the JSON object out of a model reply (tolerates a ```json fence)."""
    t = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object in the agent reply")
    return json.loads(t[start:end + 1])


def enumerable_options(spec: dict[str, Any]) -> list[str]:
    """Options written as 'A · B · C' in the registry are a closed list the agent must pick from."""
    parts = [p.strip().lower() for p in str(spec.get("options", "")).split("·")]
    return parts if len(parts) >= 2 and all(len(p) <= 40 for p in parts) else []


def check(spec: dict[str, Any], out: dict[str, Any], *, known_rules: set[str] | None = None) -> list[str]:
    """Return the integrity signals this output fails. Only signals the agent is registered
    for (signals + hard-trip signals) are evaluated; the rest belong to other checks."""
    watch = set(spec.get("signals", [])) | set(spec.get("hardTrip", []))
    failed: list[str] = []

    if not isinstance(out, dict) or any(k not in out for k in REQUIRED):
        return ["IS-4"]  # malformed output is a rule-conformance fault
    if (not isinstance(out.get("citations"), list) or not isinstance(out.get("rules_applied"), list)
            or not isinstance(out.get("options_considered"), list) or not isinstance(out.get("outputs", {}), dict)
            or not all(isinstance(c, dict) for c in out["citations"])):
        return ["IS-4"]

    if "IS-1" in watch and not out.get("needs_human") and not out.get("citations"):
        failed.append("IS-1")  # grounding: statements need sources
    if "IS-1" in watch and any(not c.get("uri") for c in out["citations"]):
        failed.append("IS-1")
    opts = enumerable_options(spec)
    if "IS-2" in watch and opts:
        considered = {str(o).strip().lower() for o in out.get("options_considered", [])}
        if not set(opts) <= considered:
            failed.append("IS-2")  # option completeness: none dropped silently
    if opts and str(out.get("option", "")).strip().lower() not in opts and not out.get("needs_human"):
        failed.append("IS-4")
    try:
        conf = float(out.get("confidence"))
        if not 0.0 <= conf <= 1.0:
            raise ValueError
    except (TypeError, ValueError):
        if "IS-6" in watch:
            failed.append("IS-6")
    allowed_rules = set(spec.get("rules", [])) | set(spec.get("constraints", [])) | set(spec.get("calcs", []))
    stray = [r for r in out.get("rules_applied", []) if r not in allowed_rules and (known_rules is None or r not in known_rules)]
    if "IS-4" in watch and stray:
        failed.append("IS-4")  # cites rules it is not registered to apply
    if "IS-5" in watch and out.get("outputs", {}).get("restricted_parts_served"):
        failed.append("IS-5")
    if "IS-9" in watch and out.get("outputs", {}).get("expired_items_used"):
        failed.append("IS-9")
    return sorted(set(failed))


def fallback(spec: dict[str, Any], reason: str) -> dict[str, Any]:
    """Fail-closed result when the breaker is open or the output fails a check."""
    return {
        "decision": spec.get("decision", ""), "option": "fallback", "options_considered": [],
        "confidence": 0.0, "outputs": {"fallback": spec.get("fallback")}, "citations": [],
        "rules_applied": ["AIG-002", "CON-046"], "needs_human": True,
        "notes": f"{reason} Fallback: {spec.get('fallback')}",
    }
