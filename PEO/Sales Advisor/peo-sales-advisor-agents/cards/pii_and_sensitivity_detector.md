# Agent card: PII & Sensitivity Detector (AG-10)

| | |
|---|---|
| Purpose | Whether an item holds PII and its label |
| Options | Labels · block · allow |
| Reads | All extracted text |
| Writes | PII findings, label recommendation |
| Family | AI fabric enrichment · C4 · AI fabric enrichment |
| Autonomy | Act (block only) |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-5, IS-6 |
| Hard trips | IS-5 |
| Fallback | Block the whole item (fail closed) |
| Tools | content_get |
| Triggers | com.insperity.keel.content.extracted |
| Emits | com.insperity.keel.content.labelled |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-003, TEC-005, TEC-006, AIG-003 |
| Constraints | CON-044, CON-045, CON-046, CON-006, CON-007, CON-024 |
| Calcs | CALC-038 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Knowledge Engineering Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
