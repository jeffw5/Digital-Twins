# Agent card: Precision Extractor (AG-20)

| | |
|---|---|
| Purpose | Which claims answer the job step |
| Options | Keep · drop per claim |
| Reads | RDF nodes, claims, spans |
| Writes | Only the claims that answer the job step |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-2, IS-7, IS-8 |
| Hard trips | none |
| Fallback | Return top cited passages, no synthesis |
| Tools | content_get, ssot_get_rule |
| Triggers | com.insperity.keel.paths.resolved |
| Emits | com.insperity.keel.claims.selected |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-007, EXT-008, EXT-012 |
| Constraints | CON-044, CON-045, CON-046, CON-003, CON-005, CON-012 |
| Calcs | CALC-023 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
