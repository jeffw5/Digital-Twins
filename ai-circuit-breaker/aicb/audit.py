"""
Layer 5 - Underwriting Interface / Provenance Audit Trail.

A minimal, dependency-free stand-in for the PROV-O + SPARQL provenance model described
in the source docs. Every breaker decision is appended as a hash-chained record (each
entry's hash covers its own content + the previous entry's hash), giving a tamper-evident
log: any edit to a past entry breaks the chain from that point forward, which
`verify_chain()` can detect. This is the "Decision Traceability hash" referenced in the
design spec's Subsystem Connectivity & Calibration section.

Not a substitute for a real audit-grade store (e.g. an append-only ledger or WORM
storage) in production -- it demonstrates the *shape* of the audit contract any real
backend should satisfy: every decision traceable to the sensor readings, ontology
version, and metric values that produced it.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class AuditEntry:
    seq: int
    timestamp: float
    holon: str
    ontology_version: str
    action: str
    intent_text: str
    metrics: dict
    decision: str          # TRANSMIT | SOFT_ALERT | HOLD | HALT | LOCKOUT
    safe_state_level: int  # 0..3
    reasons: list
    excluded_from_training: bool
    prev_hash: str
    entry_hash: str = field(default="")

    def to_dict(self) -> dict:
        return asdict(self)


class AuditTrail:
    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def _compute_hash(self, entry_without_hash: dict, prev_hash: str) -> str:
        payload = json.dumps(entry_without_hash, sort_keys=True, default=str) + prev_hash
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def append(
        self,
        holon: str,
        ontology_version: str,
        action: str,
        intent_text: str,
        metrics: dict,
        decision: str,
        safe_state_level: int,
        reasons: list,
        excluded_from_training: bool,
    ) -> AuditEntry:
        prev_hash = self._entries[-1].entry_hash if self._entries else self.GENESIS_HASH
        seq = len(self._entries)
        base = dict(
            seq=seq,
            timestamp=time.time(),
            holon=holon,
            ontology_version=ontology_version,
            action=action,
            intent_text=intent_text,
            metrics=metrics,
            decision=decision,
            safe_state_level=safe_state_level,
            reasons=reasons,
            excluded_from_training=excluded_from_training,
            prev_hash=prev_hash,
        )
        entry_hash = self._compute_hash(base, prev_hash)
        entry = AuditEntry(entry_hash=entry_hash, **base)
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def verify_chain(self) -> bool:
        prev_hash = self.GENESIS_HASH
        for e in self._entries:
            base = {
                "seq": e.seq,
                "timestamp": e.timestamp,
                "holon": e.holon,
                "ontology_version": e.ontology_version,
                "action": e.action,
                "intent_text": e.intent_text,
                "metrics": e.metrics,
                "decision": e.decision,
                "safe_state_level": e.safe_state_level,
                "reasons": e.reasons,
                "excluded_from_training": e.excluded_from_training,
                "prev_hash": prev_hash,
            }
            expected = self._compute_hash(base, prev_hash)
            if expected != e.entry_hash:
                return False
            prev_hash = e.entry_hash
        return True

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(e.to_dict(), default=str) for e in self._entries)

    def tripped_epochs(self) -> list[AuditEntry]:
        return [e for e in self._entries if e.decision != "TRANSMIT"]

    def training_eligible_epochs(self) -> list[AuditEntry]:
        return [e for e in self._entries if not e.excluded_from_training]
