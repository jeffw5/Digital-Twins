# Agent card: Concept Mapping Agent (AG-12)

| | |
|---|---|
| Purpose | Which concept a claim or field maps to |
| Options | Exact · close · broad · related matches |
| Reads | Claims, facets, hr: and isp- concepts |
| Writes | Typed correspondences with scores |
| Family | Mapping & publishing · C5 · Mapping & publishing |
| Autonomy | Advise |
| Copilot surface | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-4, IS-6, IS-7 |
| Hard trips | none |
| Fallback | Mapping held as Candidate |
| Tools | content_get, ssot_search_rules, graph_query, run_concept_mapping_agent |
| Triggers | com.insperity.keel.claims.scoped |
| Emits | com.insperity.keel.mapping.proposed |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-009, GOV-006 |
| Constraints | CON-044, CON-045, CON-046, CON-010 |
| Calcs | CALC-034 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Ontology Steward |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
