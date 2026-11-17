# Agent card: Jurisdiction & Validity Miner (AG-09)

| | |
|---|---|
| Purpose | Which jurisdictions and dates apply |
| Options | Jurisdictions from the registry; date candidates |
| Reads | Content + registry |
| Writes | Jurisdictions, valid-from, valid-until |
| Family | AI fabric enrichment · C4 · AI fabric enrichment |
| Autonomy | Advise |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-4, IS-9 |
| Hard trips | none |
| Fallback | Item excluded from jurisdiction questions |
| Tools | content_get, identity_resolve |
| Triggers | com.insperity.keel.claims.extracted |
| Emits | com.insperity.keel.claims.scoped |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-005, GOD-010, GOV-007 |
| Constraints | CON-044, CON-045, CON-046, CON-005 |
| Calcs | CALC-035 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Knowledge Engineering Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
