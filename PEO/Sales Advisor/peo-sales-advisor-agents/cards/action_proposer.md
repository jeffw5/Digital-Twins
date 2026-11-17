# Agent card: Action Proposer (AG-38)

| | |
|---|---|
| Purpose | Which action to propose to a human owner |
| Options | Actions including “do nothing” |
| Reads | Findings + owners |
| Writes | Draft KGCL or backlog item for a human |
| Family | Causal analysis · C8 · Causal analysis |
| Autonomy | Advise (human gate) |
| Copilot surface | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| Tier and breaker | T1 · half-open below 2000, open below 500 outputs between faults, or 3 faults in a row |
| Integrity signals | IS-1, IS-2, IS-4 |
| Hard trips | none |
| Fallback | Findings sent without a proposal |
| Tools | ssot_propose_change, simplex_request_approval, simplex_status, run_action_proposer |
| Triggers | com.insperity.keel.ranking.updated |
| Emits | com.insperity.keel.action.proposed |
| Rules | AIG-001, AIG-002, AIG-007, AIG-008, CTL-007, EVT-001, GOV-015, DEC-002, DEC-004, AIG-006 |
| Constraints | CON-044, CON-045, CON-046, CON-026, CON-028 |
| Calcs | none |
| Model | reasoning (Foundry deployment set by environment) |
| Owner | Analytics Lead |
| Version | 1.0.0 (Proposed) |

Data use: tenant and prospect data are never used to train or fine-tune models (CTL-010). Evaluation: decision-question probes nightly and on change (AIG-004, QBD-001).
