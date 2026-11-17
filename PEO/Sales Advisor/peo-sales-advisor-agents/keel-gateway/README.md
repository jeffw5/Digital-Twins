# Keel Gateway

The one governed door between Copilot and the Sales Advisor microservices. It is an MCP server (Streamable HTTP at `/mcp`) used by:

- Microsoft 365 Copilot declarative agents (`copilot/`), through a `RemoteMCPServer` plugin with OAuth, at `/mcp/agents/<agent-id>`;
- Copilot Studio agents, through Tools > Model Context Protocol, at the same per-agent URL;
- the hosted Agent Framework agents (`agents/`), at `/mcp` with the service token and `X-Keel-Agent`.

## Who may call (auth.py)

| Caller | Proves identity with | Agent comes from | Person comes from |
|---|---|---|---|
| Copilot / Copilot Studio (`KEEL_AUTH=entra`) | Entra ID access token for the gateway (issuer, audience, signature, expiry checked; `SalesAdvisor.User` app role required) | URL path `/mcp/agents/<id>` | token `oid` |
| Agents host | `KEEL_SERVICE_TOKEN` | `X-Keel-Agent` | none (agents are not people) |
| Owner / approver | `KEEL_ADMIN_TOKEN` | route | `X-Keel-User` |
| Local development (`KEEL_AUTH=dev`, loopback only) | nothing | header, path or `?agent=` | `X-Keel-User` |

Identity never comes from tool arguments. Without an agent the caller sees no tools. The gateway refuses to start in dev mode on a public interface, and in Entra mode without `KEEL_ENTRA_TENANT_ID` and `KEEL_ENTRA_AUDIENCE`.

## What every call goes through

| Check | Enforces |
|---|---|
| Caller is authenticated and names a registered agent | AIG-001, CON-044 |
| Tool is on the agent's allow-list (a miss by a hosted agent counts as a fault, never a hard trip) | AIG-007, CON-045 |
| Arguments match the tool's input schema | CON-045 |
| Breaker: OPEN blocks everything; HALF-OPEN allows reads only | AIG-002, CON-046 |
| Binding tools need an approved, single-use Simplex request bound to the exact payload, approved by someone other than the requester | GOV-015, DEC-004, CON-028, CTL-013 |
| Decisions are recorded only by an authenticated person who confirmed in chat | DEC-004, DEC-007 |
| Briefs only for the personas the agent serves | EXT-006, CON-019 |
| Audit line per call (HMAC chain with `KEEL_AUDIT_KEY`, continues across restarts), inputs by hash | CTL-007, GOV-022 |
| CloudEvent for every write | EVT-001 |

With `KEEL_MS_01_URL` set, production policy decisions come from the Policy Decision Service (OPA/Rego compiled from the SSOT); these local checks mirror that policy.

## Run

```bash
pip install -e .
KEEL_ADMIN_TOKEN=change-me python -m keel_gateway.server      # http://127.0.0.1:8080/mcp
python -m unittest discover -s tests                           # from this folder's parent: -s keel-gateway/tests
```

Each microservice is reached at the base URL in its environment variable (`KEEL_MS_01_URL` … `KEEL_MS_25_URL`, listed in `infra/.env.example`); the gateway POSTs tool arguments to `{base}/ops/{tool}`. Without a URL the tool answers from a labelled stub.

## Governance routes (not MCP tools, so no model can call them)

| Route | Use |
|---|---|
| `GET /governance/breaker/{agent}` | breaker state, MTBH and fallback (service token) |
| `POST /governance/breaker/{agent}/report` | an agent's runtime reports its own outputs (`ok`, `failed_signals`) |
| `POST /governance/breaker/{agent}/kill` | owner kill switch (AIG-009), `KEEL_ADMIN_TOKEN` |
| `POST /governance/breaker/{agent}/reset` | owner reset after root cause (AIG-003), `KEEL_ADMIN_TOKEN` |
| `POST /governance/events` | an agent's runtime emits its registered event types |
| `POST /governance/approvals/{id}/grant` | local Simplex approval (production: MS-11); `KEEL_ADMIN_TOKEN` + `X-Keel-User`, never the requester |

## Production notes

- Register the gateway in Entra ID (expose an API, add the `SalesAdvisor.User` app role), set `KEEL_AUTH=entra`, `KEEL_ENTRA_TENANT_ID`, `KEEL_ENTRA_AUDIENCE`, and register the same API as an OAuth client in Teams Developer Portal for the Copilot plugins (`MCP_DA_AUTH_ID`).
- Set `KEEL_ALLOWED_HOSTS` to the public host name(s) for DNS-rebinding protection behind your ingress.
- Keep secrets (`KEEL_SERVICE_TOKEN`, `KEEL_ADMIN_TOKEN`, `KEEL_AUDIT_KEY`) in Key Vault; prefer managed identities between the gateway and the agents host.
- Breaker counts, approvals and the audit chain are in memory or local files here; production keeps them in MS-12, MS-11 and MS-16 (append-only storage), with one writer per audit chain.
