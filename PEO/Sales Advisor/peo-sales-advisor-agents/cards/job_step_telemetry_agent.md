# Agent card: Job-Step Telemetry Agent (AG-25)

| | |
|---|---|
| Purpose | How to attribute events to job steps |
| Options | Job-step attributions |
| Reads | Advisor sessions, CRM events |
| Writes | Time, reuse, satisfaction per job step |
| Family | Value-gap monitoring · C7 · Value-gap monitoring |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T3 · half-open below 200, open below 50 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-3, IS-9 |
| Hard trips | none |
| Fallback | Mark metrics stale |
| Tools | metrics_query |
| Triggers | com.insperity.keel.advisor.session.ended, com.insperity.keel.schedule.hourly |
| Emits | com.insperity.keel.telemetry.recorded |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-015, MET-013 |
| Constraints | CON-044, CON-045, CON-046, CON-022 |
| Calcs | CALC-001, CALC-002, CALC-006, CALC-010 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Value Realization Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
