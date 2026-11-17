# Agent card: RDF Structure Monitor (AG-30)

| | |
|---|---|
| Purpose | Whether a shape or graph change is breaking |
| Options | Breaking · compatible · none |
| Reads | Shape and graph diffs |
| Writes | Changed shapes, orphaned nodes |
| Family | Change & impact · C8 · Change & impact |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-3 |
| Hard trips | IS-4 |
| Fallback | Block publishing |
| Tools | content_validate, graph_query |
| Triggers | com.insperity.keel.content.published |
| Emits | com.insperity.keel.change.detected |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-010, EVT-012 |
| Constraints | CON-044, CON-045, CON-046, CON-013, CON-014 |
| Calcs | CALC-032 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Semantic Governance Council |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
