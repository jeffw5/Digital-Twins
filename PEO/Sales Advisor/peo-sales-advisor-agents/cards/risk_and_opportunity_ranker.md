# Agent card: Risk & Opportunity Ranker (AG-36)

| | |
|---|---|
| Purpose | How to rank risks and opportunities |
| Options | Rankings by effect × exposure |
| Reads | Effects × exposure |
| Writes | Ranked risks and opportunities |
| Family | Causal analysis · C8 · Causal analysis |
| Autonomy | Advise |
| Copilot surface | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-3 |
| Hard trips | none |
| Fallback | Unranked list |
| Tools | metrics_query, qbd_get_baseline, run_risk_and_opportunity_ranker |
| Triggers | com.insperity.keel.effect.estimated |
| Emits | com.insperity.keel.ranking.updated |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-015, QBD-003 |
| Constraints | CON-044, CON-045, CON-046 |
| Calcs | CALC-020, CALC-030 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Analytics Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
