# Agent card: Mapping Resolver (AG-19)

| | |
|---|---|
| Purpose | Which mappings and source fields to read |
| Options | Released mapping paths |
| Reads | Facets + mapping graph |
| Writes | Source fields and RDF nodes to read |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-3 |
| Hard trips | IS-4 |
| Fallback | Use mappings pinned in the baseline |
| Tools | graph_query, content_get |
| Triggers | com.insperity.keel.facets.ranked |
| Emits | com.insperity.keel.paths.resolved |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, GOV-006, EXT-009 |
| Constraints | CON-044, CON-045, CON-046, CON-010, CON-011 |
| Calcs | CALC-034 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
