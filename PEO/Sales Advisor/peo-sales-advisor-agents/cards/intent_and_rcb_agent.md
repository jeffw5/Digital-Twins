# Agent card: Intent & RCB Agent (AG-16)

| | |
|---|---|
| Purpose | Which job step and context a question belongs to |
| Options | Intents, job steps, WHO…WHY values |
| Reads | Persona question + session |
| Writes | 5D context bundle (WHO…WHY) |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-6, IS-7 |
| Hard trips | none |
| Fallback | Ask the persona to confirm the job step |
| Tools | advisor_job_steps, identity_resolve |
| Triggers | com.insperity.keel.advisor.question.asked |
| Emits | com.insperity.keel.rcb.created |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, GOV-011, EXT-011, GOD-010 |
| Constraints | CON-044, CON-045, CON-046, CON-018 |
| Calcs | CALC-001 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
