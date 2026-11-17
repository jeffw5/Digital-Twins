# Agent card: Effect Estimator (AG-35)

| | |
|---|---|
| Purpose | Size and interval of an effect |
| Options | Estimators and intervals |
| Reads | DAG + observed outcomes |
| Writes | Effect size with interval |
| Family | Causal analysis · C8 · Causal analysis |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-3, IS-6 |
| Hard trips | none |
| Fallback | Direction only, no effect size |
| Tools | metrics_query |
| Triggers | com.insperity.keel.causal.graph.updated |
| Emits | com.insperity.keel.effect.estimated |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-015 |
| Constraints | CON-044, CON-045, CON-046, CON-022 |
| Calcs | CALC-022 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Analytics Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
