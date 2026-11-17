# Agent card: Counterfactual Explainer (AG-37)

| | |
|---|---|
| Purpose | Which what-if to explain |
| Options | What-if narratives |
| Reads | Ranked findings |
| Writes | Plain-language what-if for owners |
| Family | Causal analysis · C8 · Causal analysis |
| Autonomy | Advise |
| Copilot surface | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-8 |
| Hard trips | none |
| Fallback | Table only, no narrative |
| Tools | metrics_query, decision_get, run_counterfactual_explainer |
| Triggers | com.insperity.keel.ranking.updated |
| Emits | com.insperity.keel.counterfactual.explained |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-015, GOD-004 |
| Constraints | CON-044, CON-045, CON-046 |
| Calcs | CALC-022 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Analytics Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
