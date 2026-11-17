# Agent card: Persona & Job-Step Tagger (AG-07)

| | |
|---|---|
| Purpose | Which personas and job steps an item serves |
| Options | Persona × job-step candidates |
| Reads | Content + isp-sal job map |
| Writes | servesPersona, supportsJobStep |
| Family | AI fabric enrichment · C4 · AI fabric enrichment |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-2, IS-6, IS-7 |
| Hard trips | none |
| Fallback | Tags stay Candidate; item not served |
| Tools | content_get, advisor_job_steps |
| Triggers | com.insperity.keel.content.classified |
| Emits | com.insperity.keel.content.tagged |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-002 |
| Constraints | CON-044, CON-045, CON-046, CON-004 |
| Calcs | CALC-033 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Knowledge Engineering Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
