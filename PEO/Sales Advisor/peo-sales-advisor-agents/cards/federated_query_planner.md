# Agent card: Federated Query Planner (AG-17)

| | |
|---|---|
| Purpose | How to scope and plan the query |
| Options | Query plans within the context bundle |
| Reads | Context bundle |
| Writes | SPARQL across content, CRM, SSOT |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-3, IS-5 |
| Hard trips | IS-5 |
| Fallback | Pre-approved query templates per job step |
| Tools | graph_query |
| Triggers | com.insperity.keel.rcb.created |
| Emits | com.insperity.keel.query.planned |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-011, GOV-024, TEC-001, GOD-001 |
| Constraints | CON-044, CON-045, CON-046, CON-011, CON-018 |
| Calcs | none |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
