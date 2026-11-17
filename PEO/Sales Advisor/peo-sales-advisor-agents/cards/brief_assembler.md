# Agent card: Brief Assembler (AG-21)

| | |
|---|---|
| Purpose | Which statements and decision options to present, and in what order |
| Options | Decision options allowed by the rules, with effects and outcomes |
| Reads | Extracted claims + persona template |
| Writes | Brief with citations and access labels |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-2, IS-3, IS-5, IS-7, IS-9 |
| Hard trips | IS-5 |
| Fallback | Cited claim list and BPA hand-off; no recommendation |
| Tools | content_get, ssot_get_rule, metrics_definition, pdp_explain |
| Triggers | com.insperity.keel.claims.selected |
| Emits | com.insperity.keel.brief.drafted |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-006, EXT-012, EXT-013, DEC-002, DEC-003, DEC-005, DEC-010, DEC-011, SAL-001, SAL-002, SAL-003, SAL-006, SAL-007 |
| Constraints | CON-044, CON-045, CON-046, CON-008, CON-019, CON-026, CON-027, CON-031, CON-033, CON-034, CON-035, CON-036, CON-037 |
| Calcs | CALC-023, CALC-026 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
