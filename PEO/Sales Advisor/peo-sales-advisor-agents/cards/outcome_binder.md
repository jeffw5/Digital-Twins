# Agent card: Outcome Binder (AG-24)

| | |
|---|---|
| Purpose | Which desired outcome and metric card a decision binds to |
| Options | Candidate outcomes and cards |
| Reads | Decision records |
| Writes | Desired outcome + metric card links |
| Family | Value-gap monitoring · C7 · Value-gap monitoring |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-4 |
| Hard trips | none |
| Fallback | Record decision unbound and flagged |
| Tools | decision_get, metrics_definition |
| Triggers | com.insperity.keel.decision.recorded |
| Emits | com.insperity.keel.decision.bound |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-014, MET-014, DEC-006 |
| Constraints | CON-044, CON-045, CON-046, CON-025 |
| Calcs | CALC-021 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Value Realization Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
