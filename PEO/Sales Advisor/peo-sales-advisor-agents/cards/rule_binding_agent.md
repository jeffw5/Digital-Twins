# Agent card: Rule Binding Agent (AG-13)

| | |
|---|---|
| Purpose | Which SSOT rule a regulatory claim binds to |
| Options | Candidate rules |
| Reads | Regulatory and benefits claims |
| Writes | boundToRule links to SSOT rules |
| Family | Mapping & publishing · C5 · Mapping & publishing |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-4, IS-8 |
| Hard trips | none |
| Fallback | Claim not served (EXT-008) |
| Tools | ssot_search_rules, ssot_get_rule |
| Triggers | com.insperity.keel.claims.scoped |
| Emits | com.insperity.keel.claims.bound |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-008, GOV-008, GOV-009 |
| Constraints | CON-044, CON-045, CON-046, CON-012 |
| Calcs | CALC-037 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Ontology Steward |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
