# Agent card: SHACL Publisher (AG-14)

| | |
|---|---|
| Purpose | Publish or reject candidate triples |
| Options | Publish · reject · hold |
| Reads | Candidate triples |
| Writes | Validated RDF, KGCL record |
| Family | Mapping & publishing · C5 · Mapping & publishing |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-3 |
| Hard trips | IS-4 |
| Fallback | Stop publishing; keep last Released graph |
| Tools | content_validate, content_publish |
| Triggers | com.insperity.keel.claims.bound, com.insperity.keel.mapping.approved |
| Emits | com.insperity.keel.content.published |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-010, GOV-017, GOV-018, EVT-012, AIG-003 |
| Constraints | CON-044, CON-045, CON-046, CON-001, CON-002, CON-003, CON-005, CON-006, CON-007, CON-013 |
| Calcs | CALC-032 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Ontology Steward |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
