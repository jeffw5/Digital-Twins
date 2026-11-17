# Agent card: Semantic Change Monitor (AG-29)

| | |
|---|---|
| Purpose | Which concepts and rules a KGCL change touches |
| Options | Changed concepts and rules |
| Reads | Ontology and SSOT KGCL stream |
| Writes | Changed concepts and rule versions |
| Family | Change & impact · C8 · Change & impact |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-3 |
| Hard trips | none |
| Fallback | Freeze the serving ontology version |
| Tools | ssot_get_rule, ssot_search_rules |
| Triggers | com.insperity.keel.ssot.rule.released |
| Emits | com.insperity.keel.change.detected |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, GOV-003, GOV-018, EVT-012 |
| Constraints | CON-044, CON-045, CON-046, CON-014, CON-015, CON-016 |
| Calcs | none |
| Model | standard (Foundry deployment set by environment) |
| Owner | Semantic Governance Council |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
