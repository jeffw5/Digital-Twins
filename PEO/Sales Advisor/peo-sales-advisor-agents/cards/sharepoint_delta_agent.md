# Agent card: SharePoint Delta Agent (AG-01)

| | |
|---|---|
| Purpose | Which items changed and need reprocessing |
| Options | New · modified · moved · deleted · unchanged |
| Reads | Graph change notifications, delta tokens |
| Writes | Changed items + version history |
| Family | Ingestion & identity · C3 · Ingestion & identity |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-3, IS-7, IS-9 |
| Hard trips | none |
| Fallback | Nightly full enumeration replaces deltas |
| Tools | identity_resolve, identity_mint, content_get |
| Triggers | com.microsoft.graph.driveitem.changed, com.insperity.keel.schedule.nightly |
| Emits | com.insperity.keel.content.item.changed |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-001, GOV-007, EVT-012, EVT-005 |
| Constraints | CON-044, CON-045, CON-046, CON-001, CON-002 |
| Calcs | CALC-035 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Content Operations Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
