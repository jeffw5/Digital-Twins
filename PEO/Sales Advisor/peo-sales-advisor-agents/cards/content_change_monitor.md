# Agent card: Content Change Monitor (AG-28)

| | |
|---|---|
| Purpose | Whether a delta is a material change |
| Options | Material · cosmetic · none |
| Reads | CMS, web, feed deltas |
| Writes | Change events (CloudEvents) |
| Family | Change & impact · C8 · Change & impact |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-3, IS-7 |
| Hard trips | none |
| Fallback | Periodic full diff |
| Tools | content_get |
| Triggers | com.insperity.keel.content.item.changed |
| Emits | com.insperity.keel.change.detected |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-016, EVT-012 |
| Constraints | CON-044, CON-045, CON-046, CON-038 |
| Calcs | CALC-035 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Semantic Governance Council |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
