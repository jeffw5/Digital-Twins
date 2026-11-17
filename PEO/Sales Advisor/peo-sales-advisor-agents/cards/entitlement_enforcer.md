# Agent card: Entitlement Enforcer (AG-11)

| | |
|---|---|
| Purpose | Allow, redact or deny each part for a persona |
| Options | Allow · redact · deny |
| Reads | Labels + persona roles |
| Writes | Allow / redact / deny per part |
| Family | AI fabric enrichment · C4 · AI fabric enrichment |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-5, IS-3 |
| Hard trips | IS-5 |
| Fallback | Deny every non-public part (fail closed) |
| Tools | pep_check_response, pdp_evaluate |
| Triggers | com.insperity.keel.brief.drafted |
| Emits | com.insperity.keel.brief.entitled |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-006, TEC-001, TEC-021, AIG-003 |
| Constraints | CON-044, CON-045, CON-046, CON-018, CON-019 |
| Calcs | CALC-038 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Knowledge Engineering Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
