# Agent card: Format Extractor (AG-05)

| | |
|---|---|
| Purpose | How to segment text, tables and notes |
| Options | Segmentations and table structures |
| Reads | PPTX, DOCX, PDF, HTML, spreadsheets |
| Writes | Text, tables, slide notes with spans |
| Family | Ingestion & identity · C3 · Ingestion & identity |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-3 |
| Hard trips | none |
| Fallback | Raw text flagged “unstructured” |
| Tools | content_get, content_validate |
| Triggers | com.insperity.keel.identity.resolved |
| Emits | com.insperity.keel.content.extracted |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-004, EXT-007, CTL-008 |
| Constraints | CON-044, CON-045, CON-046, CON-003, CON-008 |
| Calcs | CALC-036 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Content Operations Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
