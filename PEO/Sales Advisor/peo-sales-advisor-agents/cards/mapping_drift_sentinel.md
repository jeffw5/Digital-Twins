# Agent card: Mapping Drift Sentinel (AG-15)

| | |
|---|---|
| Purpose | Whether a mapping is degraded or broken |
| Options | OK · degraded · broken |
| Reads | Source schemas, mapping graph |
| Writes | Broken or degraded mappings |
| Family | Mapping & publishing · C5 · Mapping & publishing |
| Autonomy | Act (flag) |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T3 · half-open below 200, open below 50 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-7, IS-6 |
| Hard trips | none |
| Fallback | Daily full mapping regression run |
| Tools | graph_query, content_validate |
| Triggers | com.insperity.keel.schema.changed, com.insperity.keel.schedule.daily |
| Emits | com.insperity.keel.mapping.drift.detected |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, GOV-006, EXT-009, EVT-012 |
| Constraints | CON-044, CON-045, CON-046, CON-011 |
| Calcs | CALC-034 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Ontology Steward |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
