# Agent card: PEO Sales Advisor (FD-01)

| | |
|---|---|
| Purpose | Answer a persona's decision question with a cited brief and the options the rules allow |
| Options | Brief · held result with BPA hand-off · clarifying question |
| Reads | Persona question, job step, prospect |
| Writes | Cited brief, recorded decision (with confirmation) |
| Family | Front door · C6 · Persona experience in Microsoft 365 Copilot |
| Autonomy | Advise |
| Copilot surface | Declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-2, IS-5, IS-7, IS-9 |
| Hard trips | IS-5 |
| Fallback | Return cited passages only and hand off to the BPA |
| Tools | advisor_ask, advisor_job_steps, ssot_get_rule, metrics_definition, census_validate, quote_request, quote_get, consent_check, proposal_draft, advisor_record_decision |
| Triggers | on request |
| Emits | com.insperity.keel.advisor.question.asked, com.insperity.keel.decision.recorded |
| Rules | EXT-006, EXT-012, EXT-013, DEC-002, DEC-003, DEC-005, DEC-010, DEC-011, SAL-001, SAL-002, SAL-003, SAL-004, SAL-005, SAL-006, SAL-011, GOV-015 |
| Constraints | CON-019, CON-026, CON-027, CON-028, CON-030, CON-031, CON-036, CON-044, CON-045, CON-046 |
| Calcs | CALC-001, CALC-003, CALC-023 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
