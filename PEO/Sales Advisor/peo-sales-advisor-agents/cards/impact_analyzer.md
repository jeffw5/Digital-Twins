# Agent card: Impact Analyzer (AG-31)

| | |
|---|---|
| Purpose | Which questions, briefs and decisions a change affects |
| Options | Candidate impact sets |
| Reads | Change event + dependency graph |
| Writes | Affected assemblies, jobs, decisions |
| Family | Change & impact · C8 · Change & impact |
| Autonomy | Advise |
| Copilot surface | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-3 |
| Hard trips | none |
| Fallback | Widen impact to the whole job step |
| Tools | qbd_get_baseline, qbd_classify_change, probes_results, graph_query, run_impact_analyzer |
| Triggers | com.insperity.keel.change.detected |
| Emits | com.insperity.keel.impact.assessed |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-016, GOD-008, QBD-002 |
| Constraints | CON-044, CON-045, CON-046, CON-050 |
| Calcs | CALC-030 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Semantic Governance Council |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
