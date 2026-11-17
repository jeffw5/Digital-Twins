# Agent card: Facet Navigator (AG-18)

| | |
|---|---|
| Purpose | How to rank facets |
| Options | Facet orderings |
| Reads | Query results |
| Writes | Ranked facets: stage, job, jurisdiction, product |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-3, IS-7 |
| Hard trips | none |
| Fallback | Static facet order |
| Tools | graph_facets |
| Triggers | com.insperity.keel.query.planned |
| Emits | com.insperity.keel.facets.ranked |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-011 |
| Constraints | CON-044, CON-045, CON-046, CON-018 |
| Calcs | none |
| Model | standard (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
