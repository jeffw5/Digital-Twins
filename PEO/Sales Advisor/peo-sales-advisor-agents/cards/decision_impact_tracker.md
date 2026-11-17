# Agent card: Decision Impact Tracker (AG-27)

| | |
|---|---|
| Purpose | Which downstream effects a decision caused |
| Options | Candidate effect attributions |
| Reads | Decisions + downstream events |
| Writes | Effect on later decisions and stage moves |
| Family | Value-gap monitoring · C7 · Value-gap monitoring |
| Autonomy | Advise |
| Copilot surface | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-6, IS-8 |
| Hard trips | none |
| Fallback | Associations only, labelled non-causal |
| Tools | decision_get, metrics_query, run_decision_impact_tracker |
| Triggers | com.insperity.keel.decision.bound, com.insperity.keel.crm.stage.changed |
| Emits | com.insperity.keel.impact.estimated |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-014, EXT-015, DEC-006 |
| Constraints | CON-044, CON-045, CON-046, CON-025 |
| Calcs | CALC-021 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Value Realization Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
