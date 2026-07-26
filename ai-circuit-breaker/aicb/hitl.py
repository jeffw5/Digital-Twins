"""
Layer 5 - Human Trustee: training and feedback (human-in-the-loop) review.

Implements the Human Trustee Decision Record (HTDR) from TB-06's provenance mapping
("Every HT action ... Permanent ... DoDD 3000.09 SS4(c)") and the review workflow that
lets a Trustee dig into a specific flagged/tripped AI action and make a correction.

Design choice: the original audit trail (aicb.audit.AuditTrail) is a hash-chained,
append-only, tamper-evident log -- exactly the property you want for "what did the
system actually do and when." That means it must never be mutated after the fact, even
by a human reviewer overriding a decision. So HITL review is modeled as a SEPARATE
append-only log (HTDR) that REFERENCES an original audit entry by sequence number,
rather than editing it. The two logs are joined at read time (see
`CircuitBreaker.effective_recursive_learning_batch`) to compute the current, reviewed
state of the system without ever rewriting history. This is the same pattern real
regulated systems use: corrections are new events, not edits.

Three review actions map onto the three things a Trustee can conclude about a flagged
epoch, and onto what the source doc calls "digging into a specific AI fault and making
a correction":

  CONFIRM_HALLUCINATION   The breaker was right to trip. The epoch stays purged from
                           training data (SOP-03 holds). No system state changes other
                           than the permanent record that a human confirmed it.

  FALSE_POSITIVE_OVERRIDE The breaker tripped on something that was, on human review,
                           actually fine (e.g. an overly tight threshold, a legitimate
                           edge case the ontology didn't cover yet). The epoch is
                           returned to the training-eligible pool.

  CORRECTED_LABEL         The AI's output was wrong, but the Trustee knows what the
                           CORRECT action/intent should have been. That corrected intent
                           is written into the ontology as a new reference assertion
                           (Ontology Enhancement / positive learning from a human
                           correction) -- the actual "make corrections" mechanism.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum


class ReviewAction(str, Enum):
    CONFIRM_HALLUCINATION = "confirm_hallucination"
    FALSE_POSITIVE_OVERRIDE = "false_positive_override"
    CORRECTED_LABEL = "corrected_label"
    ESCALATE = "escalate"


@dataclass
class HTDR:
    """Human Trustee Decision Record."""

    seq: int
    timestamp: float
    trustee_id: str
    audit_seq: int              # which original AuditEntry.seq this review is about
    action: ReviewAction
    note: str = ""
    corrected_intent_text: str = ""
    corrected_action: str = ""
    escalation_target: str = ""
    prev_hash: str = ""
    entry_hash: str = field(default="")

    def to_dict(self) -> dict:
        d = dict(
            seq=self.seq, timestamp=self.timestamp, trustee_id=self.trustee_id,
            audit_seq=self.audit_seq, action=self.action.value, note=self.note,
            corrected_intent_text=self.corrected_intent_text,
            corrected_action=self.corrected_action,
            escalation_target=self.escalation_target,
            prev_hash=self.prev_hash, entry_hash=self.entry_hash,
        )
        return d


class ReviewLog:
    """Append-only, hash-chained HTDR log -- the same tamper-evidence guarantee as the
    main audit trail, kept as a physically separate chain so review actions are always
    distinguishable from the original AI/breaker decisions they reference.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self._entries: list[HTDR] = []

    def record(
        self,
        trustee_id: str,
        audit_seq: int,
        action: ReviewAction,
        note: str = "",
        corrected_intent_text: str = "",
        corrected_action: str = "",
        escalation_target: str = "",
    ) -> HTDR:
        prev_hash = self._entries[-1].entry_hash if self._entries else self.GENESIS_HASH
        seq = len(self._entries)
        base = dict(
            seq=seq, timestamp=time.time(), trustee_id=trustee_id, audit_seq=audit_seq,
            action=action.value, note=note, corrected_intent_text=corrected_intent_text,
            corrected_action=corrected_action, escalation_target=escalation_target,
            prev_hash=prev_hash,
        )
        payload = json.dumps(base, sort_keys=True, default=str) + prev_hash
        entry_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        entry = HTDR(
            seq=seq, timestamp=base["timestamp"], trustee_id=trustee_id, audit_seq=audit_seq,
            action=action, note=note, corrected_intent_text=corrected_intent_text,
            corrected_action=corrected_action, escalation_target=escalation_target,
            prev_hash=prev_hash, entry_hash=entry_hash,
        )
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> list[HTDR]:
        return list(self._entries)

    def for_audit_seq(self, audit_seq: int) -> list[HTDR]:
        return [e for e in self._entries if e.audit_seq == audit_seq]

    def latest_action_for(self, audit_seq: int) -> ReviewAction | None:
        matches = self.for_audit_seq(audit_seq)
        return matches[-1].action if matches else None

    def verify_chain(self) -> bool:
        prev_hash = self.GENESIS_HASH
        for e in self._entries:
            base = dict(
                seq=e.seq, timestamp=e.timestamp, trustee_id=e.trustee_id, audit_seq=e.audit_seq,
                action=e.action.value, note=e.note, corrected_intent_text=e.corrected_intent_text,
                corrected_action=e.corrected_action, escalation_target=e.escalation_target,
                prev_hash=prev_hash,
            )
            payload = json.dumps(base, sort_keys=True, default=str) + prev_hash
            expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            if expected != e.entry_hash:
                return False
            prev_hash = e.entry_hash
        return True
