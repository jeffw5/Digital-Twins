# Agent card: Incremental Refresh Service (AG-32)

| | |
|---|---|
| Purpose | Which stages to re-run |
| Options | Stage subsets |
| Reads | Impact set |
| Writes | Re-run only affected stages |
| Family | Change & impact · C8 · Change & impact |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-3, IS-4 |
| Hard trips | none |
| Fallback | Full rebuild |
| Tools | saga_start, saga_status |
| Triggers | com.insperity.keel.impact.assessed |
| Emits | com.insperity.keel.refresh.started |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-016, GOV-023, EVT-003 |
| Constraints | CON-044, CON-045, CON-046, CON-041 |
| Calcs | CALC-031 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Semantic Governance Council |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
