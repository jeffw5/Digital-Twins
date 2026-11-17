# Agent card: Claim Extractor (AG-08)

| | |
|---|---|
| Purpose | Which atomic claims a passage makes |
| Options | Candidate claims with spans |
| Reads | Tables and passages |
| Writes | Atomic claims with source span |
| Family | AI fabric enrichment · C4 · AI fabric enrichment |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-3, IS-8 |
| Hard trips | none |
| Fallback | Serve cited passages, no claims |
| Tools | content_get, content_validate |
| Triggers | com.insperity.keel.content.tagged |
| Emits | com.insperity.keel.claims.extracted |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-007, EXT-008 |
| Constraints | CON-044, CON-045, CON-046, CON-003, CON-012 |
| Calcs | CALC-037 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Knowledge Engineering Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
