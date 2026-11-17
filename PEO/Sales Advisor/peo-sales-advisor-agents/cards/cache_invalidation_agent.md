# Agent card: Cache Invalidation Agent (AG-33)

| | |
|---|---|
| Purpose | Withdraw, flag or keep a served brief |
| Options | Withdraw · flag · keep |
| Reads | Impact set |
| Writes | Stale briefs withdrawn or flagged |
| Family | Change & impact · C8 · Change & impact |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-9 |
| Hard trips | none |
| Fallback | Withdraw every brief in the impact set (fail closed) |
| Tools | content_get, events_publish |
| Triggers | com.insperity.keel.impact.assessed |
| Emits | com.insperity.keel.brief.withdrawn |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-005, EXT-016 |
| Constraints | CON-044, CON-045, CON-046, CON-005 |
| Calcs | CALC-031 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Semantic Governance Council |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
