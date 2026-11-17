# Sales Advisor agents (Microsoft Agent Framework + Foundry)

Every agent in the registry that runs on its own is here. Each one is a `GovernedAgent`:

1. its spec comes from `registry/agent-registry.json` and its instructions from `instructions/<agent>.md` (both generated);
2. it checks its breaker before running and runs its fail-closed fallback when the breaker is OPEN;
3. it uses a Foundry model through `FoundryChatClient` and reaches data only through the Keel Gateway's MCP endpoint, limited to its allow-list;
4. its JSON output is checked for integrity signals (`keel_agents/contract.py`); failures are reported to the breaker and replaced with the fallback;
5. it emits its CloudEvent, which triggers the next agent.

## Run

```bash
pip install -e .
export FOUNDRY_PROJECT_ENDPOINT=https://<project>.services.ai.azure.com FOUNDRY_MODEL=<deployment> KEEL_GATEWAY_URL=http://127.0.0.1:8080
az login            # DefaultAzureCredential
python -m keel_agents.host      # POST /events, POST /agents/{id}/run, POST /pipelines/advisor
```

Send it events from Event Grid (CloudEvents 1.0 schema, push delivery to `/events`). The gateway's `run_<agent>` tools and `advisor_ask` call it when `KEEL_AGENTS_HOST_URL` is set on the gateway. Set the same secret as `KEEL_HOST_TOKEN` here and `KEEL_SERVICE_TOKEN` on the gateway.

## Test without Foundry

```bash
python -m unittest discover -s tests        # fake model and fake gateway
```

## Files

| Path | Generated? | What |
|---|---|---|
| `keel_agents/runtime.py` | no | governed runtime, Agent Framework runner |
| `keel_agents/contract.py` | no | output contract and integrity checks |
| `keel_agents/pipeline.py` | no | the advisor_ask pipeline (AG-16 → AG-23) |
| `keel_agents/host.py` | no | HTTP host for events and Copilot calls |
| `keel_agents/agents/*.py` | yes | per-agent triggers, events and task text |
| `instructions/*.md` | yes | per-agent system instructions |
