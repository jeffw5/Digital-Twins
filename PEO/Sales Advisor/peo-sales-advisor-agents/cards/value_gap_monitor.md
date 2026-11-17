# Agent card: Value-Gap Monitor (AG-26)

| | |
|---|---|
| Purpose | Gap, no gap, or not enough data |
| Options | Gap · met · insufficient data |
| Reads | Telemetry vs targets |
| Writes | Gaps per persona job step |
| Family | Value-gap monitoring · C7 · Value-gap monitoring |
| Autonomy | Advise |
| Copilot surface | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-6, IS-7 |
| Hard trips | none |
| Fallback | Show raw metrics, no verdict |
| Tools | metrics_query, metrics_definition, advisor_job_steps, run_value_gap_monitor |
| Triggers | com.insperity.keel.schedule.daily |
| Emits | com.insperity.keel.valuegap.detected |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-015 |
| Constraints | CON-044, CON-045, CON-046, CON-022 |
| Calcs | CALC-014, CALC-015, CALC-016, CALC-017 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Value Realization Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
