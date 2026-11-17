# Agent card: Feed Listener Agent (AG-03)

| | |
|---|---|
| Purpose | Accept, normalize or reject a feed item |
| Options | Accept · normalize · reject · hold |
| Reads | Regulatory and firmographic feeds |
| Writes | Normalized feed items |
| Family | Ingestion & identity · C3 · Ingestion & identity |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-9 |
| Hard trips | none |
| Fallback | Queue items for a steward |
| Tools | identity_resolve, ssot_search_rules |
| Triggers | com.insperity.keel.feed.item.received |
| Emits | com.insperity.keel.content.item.changed |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-005, EXT-008, CTL-005, CTL-008 |
| Constraints | CON-044, CON-045, CON-046, CON-009, CON-038 |
| Calcs | CALC-035 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Content Operations Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
