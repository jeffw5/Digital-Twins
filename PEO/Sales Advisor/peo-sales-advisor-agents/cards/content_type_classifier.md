# Agent card: Content-Type Classifier (AG-06)

| | |
|---|---|
| Purpose | Which content type an item is |
| Options | Content types above the confidence floor |
| Reads | Extracted text + layout |
| Writes | Content type with confidence |
| Family | AI fabric enrichment · C4 · AI fabric enrichment |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-6, IS-7 |
| Hard trips | none |
| Fallback | Leave unclassified for steward review |
| Tools | content_get |
| Triggers | com.insperity.keel.content.extracted |
| Emits | com.insperity.keel.content.classified |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-002, CTL-008 |
| Constraints | CON-044, CON-045, CON-046, CON-004 |
| Calcs | CALC-033 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Knowledge Engineering Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
