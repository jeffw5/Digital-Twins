# Agent card: Web Crawl Agent (AG-02)

| | |
|---|---|
| Purpose | Fetch, skip or store a page and its changed blocks |
| Options | Fetch · skip (robots or licence) · store diff |
| Reads | Allow-listed URLs, robots.txt |
| Writes | Page snapshots and block diffs |
| Family | Ingestion & identity · C3 · Ingestion & identity |
| Autonomy | Act |
| Copilot surface | Hosted agent (Agent Framework on Foundry); reached through the Keel Gateway |
| Tier and breaker | T2 · half-open below 500, open below 100 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-4, IS-3 |
| Hard trips | IS-4 |
| Fallback | Freeze last good snapshot; mark stale |
| Tools | identity_resolve, content_get |
| Triggers | com.insperity.keel.schedule.crawl |
| Emits | com.insperity.keel.content.item.changed |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, EXT-004, EXT-005, CTL-005, CTL-008 |
| Constraints | CON-044, CON-045, CON-046, CON-008, CON-009 |
| Calcs | CALC-035 |
| Model | standard (Foundry deployment set by environment) |
| Owner | Content Operations Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
