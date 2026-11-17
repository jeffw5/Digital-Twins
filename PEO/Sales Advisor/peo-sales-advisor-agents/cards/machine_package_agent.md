# Agent card: Machine Package Agent (AG-22)

| | |
|---|---|
| Purpose | What goes into the JSON-LD package |
| Options | Claims and fields for the receiving system |
| Reads | Extracted claims |
| Writes | JSON-LD package for CRM, quoting, other agents |
| Family | Faceted search & assembly · C6 · Faceted search & assembly |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-1 |
| Hard trips | IS-4 |
| Fallback | No package; manual hand-off |
| Tools | content_get, events_publish |
| Triggers | com.insperity.keel.brief.released |
| Emits | com.insperity.keel.package.created |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-013, GOV-021, EVT-010 |
| Constraints | CON-044, CON-045, CON-046, CON-021, CON-038 |
| Calcs | none |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Sales Advisor Product Owner |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
