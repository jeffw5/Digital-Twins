# PEO Sales Advisor in Microsoft 365 Copilot

A Microsoft 365 Agents Toolkit project for the declarative agent. It reaches the Sales Advisor only through the Keel Gateway (an MCP server), pinned to these tools: `advisor_ask`, `advisor_job_steps`, `ssot_get_rule`, `metrics_definition`, `census_validate`, `quote_request`, `quote_get`, `consent_check`, `proposal_draft`, `advisor_record_decision`.

## Deploy
1. Deploy the Keel Gateway and note its public `/mcp` URL (see `keel-gateway/README.md`).
2. In Teams Developer Portal, register an OAuth client for the gateway (Entra ID) and put its registration ID in `env/.env.dev` as `MCP_DA_AUTH_ID`. Set `KEEL_GATEWAY_MCP_URL` (ending in `/mcp`); the plugin calls `/mcp/agents/FD-01`. Users need the gateway's `SalesAdvisor.User` app role.
3. Open this folder in VS Code with the Microsoft 365 Agents Toolkit and run **Provision** (or `atk provision --env dev`). Then use the agent in Microsoft 365 Copilot.
4. Run the evaluations in `evals/prompts.json` with the toolkit before publishing to the tenant catalog (`atk publish`).

The pinned tool descriptions in `appPackage/ai-plugin.json` are copied verbatim from the gateway's `tools/list`. When you change tools in the Agent Editor, regenerate this project.
