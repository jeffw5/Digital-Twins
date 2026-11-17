# Agent card: Identity Resolver (AG-04)

| | |
|---|---|
| Purpose | Match to an existing URI or mint a new one |
| Options | Match · mint · hold for steward |
| Reads | Item IDs, URLs, company names |
| Writes | Canonical URIs, prov links |
| Family | Ingestion & identity · C3 · Ingestion & identity |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-3, IS-6, IS-8 |
| Hard trips | none |
| Fallback | Mint provisional URIs; hold all merges |
| Tools | identity_resolve, identity_mint |
| Triggers | com.insperity.keel.content.item.changed |
| Emits | com.insperity.keel.identity.resolved |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-001, GOV-007, GOD-010 |
| Constraints | CON-044, CON-045, CON-046, CON-001, CON-002 |
| Calcs | CALC-036 |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Content Operations Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
