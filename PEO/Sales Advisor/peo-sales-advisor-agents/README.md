# PEO Sales Advisor agents for Copilot

Generated from the agent registry (`registry/agent-registry.json`), which is edited in the Agent Editor (https://claude.ai/artifact/XaWZRRxCDcC4gg7Y4s8nv6). Download a fresh copy from there after a change is released, rather than hand-editing generated files.

## What runs where

```
Microsoft 365 Copilot / Teams          Copilot Studio            Event broker (CloudEvents)
  declarative agents (copilot/)          agents (copilot-studio/)          |
            \                               |                             v
             +-------- MCP (Streamable HTTP, OAuth) --------+     agents host (agents/)
                                    |                               Agent Framework + Foundry
                              Keel Gateway  <------- MCP (X-Keel-Agent) --------+
              allow-lists, breakers, Simplex gate, audit, CloudEvents
                                    |
                     25 Sales Advisor microservices (KEEL_MS_xx_URL)
```

- **8 declarative agents** for Microsoft 365 Copilot (`copilot/`): the PEO Sales Advisor front door and the advisory agents people talk to.
- **38 hosted agents** on Microsoft Agent Framework with Foundry models (`agents/`): they run on events or when a Copilot agent calls `run_<agent>`.
- **Keel Gateway** (`keel-gateway/`): an MCP server (Entra ID for people, a service token for hosted agents) exposing 44 microservice operations plus the run tools. It enforces every agent's tool allow-list (CON-045), breaker state (CON-046), persona entitlements (CON-019), the Simplex gate (CON-028) and human confirmation of decisions, logs every call (CTL-007) and emits CloudEvents (EVT-001).
- **Copilot Studio guides** (`copilot-studio/`) for building the same agents in Copilot Studio.
- **Agent cards** (`cards/`) for every agent (AIG-011).

## Run locally
```bash
cd keel-gateway && pip install -e . && python -m keel_gateway.server        # MCP at http://127.0.0.1:8080/mcp
cd agents && pip install -e . && python -m keel_agents.host                   # needs FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_MODEL
python -m unittest discover -s keel-gateway/tests && python -m unittest discover -s agents/tests
python scripts/smoke.py      # gateway + agents host + offline model, driven over MCP like Copilot
```
Without service URLs the gateway answers from labelled stubs, so Copilot and the agents can be exercised end to end first. `docker compose -f infra/docker-compose.yml up` starts both services.

## Agents

| ID | Agent | Family | Tier | Autonomy | Runs as |
|---|---|---|---|---|---|
| FD-01 | PEO Sales Advisor | Front door | T1 | Advise | Declarative agent in Microsoft 365 Copilot |
| AG-01 | SharePoint Delta Agent | Ingestion & identity | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-02 | Web Crawl Agent | Ingestion & identity | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-03 | Feed Listener Agent | Ingestion & identity | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-04 | Identity Resolver | Ingestion & identity | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-05 | Format Extractor | Ingestion & identity | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-06 | Content-Type Classifier | AI fabric enrichment | T2 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-07 | Persona & Job-Step Tagger | AI fabric enrichment | T1 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-08 | Claim Extractor | AI fabric enrichment | T1 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-09 | Jurisdiction & Validity Miner | AI fabric enrichment | T1 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-10 | PII & Sensitivity Detector | AI fabric enrichment | T1 | Act (block only) | Hosted agent (Agent Framework on Foundry) |
| AG-11 | Entitlement Enforcer | AI fabric enrichment | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-12 | Concept Mapping Agent | Mapping & publishing | T2 | Advise | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| AG-13 | Rule Binding Agent | Mapping & publishing | T1 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-14 | SHACL Publisher | Mapping & publishing | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-15 | Mapping Drift Sentinel | Mapping & publishing | T3 | Act (flag) | Hosted agent (Agent Framework on Foundry) |
| AG-16 | Intent & RCB Agent | Faceted search & assembly | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-17 | Federated Query Planner | Faceted search & assembly | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-18 | Facet Navigator | Faceted search & assembly | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-19 | Mapping Resolver | Faceted search & assembly | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-20 | Precision Extractor | Faceted search & assembly | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-21 | Brief Assembler | Faceted search & assembly | T1 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-22 | Machine Package Agent | Faceted search & assembly | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-23 | Grounding Guard (MTBH) | Faceted search & assembly | T1 | Act (block) | Hosted agent (Agent Framework on Foundry) |
| AG-24 | Outcome Binder | Value-gap monitoring | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-25 | Job-Step Telemetry Agent | Value-gap monitoring | T3 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-26 | Value-Gap Monitor | Value-gap monitoring | T2 | Advise | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| AG-27 | Decision Impact Tracker | Value-gap monitoring | T2 | Advise | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| AG-28 | Content Change Monitor | Change & impact | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-29 | Semantic Change Monitor | Change & impact | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-30 | RDF Structure Monitor | Change & impact | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-31 | Impact Analyzer | Change & impact | T1 | Advise | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| AG-32 | Incremental Refresh Service | Change & impact | T2 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-33 | Cache Invalidation Agent | Change & impact | T1 | Act | Hosted agent (Agent Framework on Foundry) |
| AG-34 | Causal Graph Builder | Causal analysis | T3 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-35 | Effect Estimator | Causal analysis | T2 | Advise | Hosted agent (Agent Framework on Foundry) |
| AG-36 | Risk & Opportunity Ranker | Causal analysis | T2 | Advise | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| AG-37 | Counterfactual Explainer | Causal analysis | T2 | Advise | Hosted agent plus a declarative agent in Microsoft 365 Copilot |
| AG-38 | Action Proposer | Causal analysis | T1 | Advise (human gate) | Hosted agent plus a declarative agent in Microsoft 365 Copilot |

## Governance
Rules, constraints and calcs referenced here live in the SSOT and are edited in the SSOT Editor (https://claude.ai/artifact/BzAWvkVadS2h1mmUAMqNHR). Changes to agents follow the same Draft → Candidate → Approved → Released workflow in the Agent Editor; author, approver and deployer are different people (CTL-013), and promotion needs passing decision-question probes (GOD-006, CON-048).
