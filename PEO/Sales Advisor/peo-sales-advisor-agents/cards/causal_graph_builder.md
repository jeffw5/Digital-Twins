# Agent card: Causal Graph Builder (AG-34)

| | |
|---|---|
| Purpose | Which causal edges to assert |
| Options | Candidate edges with assumptions |
| Reads | Changes, gaps, decisions, outcomes |
| Writes | Causal DAG with assumptions |
| Family | Causal analysis · C8 · Causal analysis |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T3 · half-open below 200, open below 50 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-6, IS-8 |
| Hard trips | none |
| Fallback | Correlational view, labelled |
| Tools | metrics_query, decision_get |
| Triggers | com.insperity.keel.schedule.weekly |
| Emits | com.insperity.keel.causal.graph.updated |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-015 |
| Constraints | CON-044, CON-045, CON-046 |
| Calcs | CALC-022 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Analytics Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
