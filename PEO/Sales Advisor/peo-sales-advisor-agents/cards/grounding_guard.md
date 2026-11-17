# Agent card: Grounding Guard (MTBH) (AG-23)

| | |
|---|---|
| Purpose | Pass, hold or block a draft brief |
| Options | Pass · hold for review · block |
| Reads | Draft brief |
| Writes | Grounding score; trip below 0.80 |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Act (block) |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-6, IS-7 |
| Hard trips | none |
| Fallback | Hold every brief for human review (fail closed) |
| Tools | content_get, qbd_get_baseline |
| Triggers | com.insperity.keel.brief.entitled |
| Emits | com.insperity.keel.brief.released, com.insperity.keel.brief.held |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-012, GOV-014, DEC-009 |
| Constraints | CON-044, CON-045, CON-046, CON-030 |
| Calcs | CALC-023, CALC-024, CALC-029 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
