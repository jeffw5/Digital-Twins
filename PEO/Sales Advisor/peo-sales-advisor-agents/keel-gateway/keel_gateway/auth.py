"""Who is calling: authentication for the Keel Gateway.

Three kinds of caller:

* service - the agents host (or another Keel service) with the shared service token
  (KEEL_SERVICE_TOKEN). It may name the hosted agent it runs (X-Keel-Agent).
* user    - Microsoft 365 Copilot or Copilot Studio on behalf of a person, with an Entra ID
  access token for the gateway (KEEL_AUTH=entra). The agent comes from the URL path
  (/mcp/agents/<id>, fixed in each Copilot plugin manifest); the person, tenant and roles
  come only from the verified token.
* dev     - local development on a loopback address (KEEL_AUTH=dev): headers and the
  ?agent= query are trusted. The gateway refuses to start in dev mode on a public interface.

Anything else gets 401. Identity never comes from tool arguments a model can write.
"""
from __future__ import annotations

import hmac
import ipaddress
import json
import os
from dataclasses import dataclass, field
from typing import Any

PREFIX = "/mcp/agents/"


@dataclass
class Principal:
    kind: str                      # service | user | dev
    agent_id: str | None
    user: str | None = None
    tenant: str | None = None
    persona: str | None = None
    roles: list[str] = field(default_factory=list)
    admin: bool = False


class AuthError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def _loopback(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host == "localhost"


def mode() -> str:
    m = os.getenv("KEEL_AUTH")
    if m:
        return m
    return "dev" if _loopback(os.getenv("KEEL_HOST", "127.0.0.1")) else "entra"


def check_startup() -> None:
    if mode() == "dev" and not _loopback(os.getenv("KEEL_HOST", "127.0.0.1")):
        raise SystemExit("KEEL_AUTH=dev trusts request headers; it is only allowed on a loopback address.")
    if mode() == "entra" and not (os.getenv("KEEL_ENTRA_TENANT_ID") and os.getenv("KEEL_ENTRA_AUDIENCE")):
        raise SystemExit("KEEL_AUTH=entra needs KEEL_ENTRA_TENANT_ID and KEEL_ENTRA_AUDIENCE.")


def _same(a: str | None, b: str | None) -> bool:
    return bool(a) and bool(b) and hmac.compare_digest(a.encode(), b.encode())


_jwks_client: Any = None


def _verify_entra(token: str) -> dict[str, Any]:
    import jwt  # PyJWT, installed with mcp
    global _jwks_client
    tid, aud = os.environ["KEEL_ENTRA_TENANT_ID"], os.environ["KEEL_ENTRA_AUDIENCE"]
    issuer = os.getenv("KEEL_ENTRA_ISSUER", f"https://login.microsoftonline.com/{tid}/v2.0")
    jwks_file = os.getenv("KEEL_ENTRA_JWKS_FILE")  # tests and air-gapped deployments
    try:
        if jwks_file:
            header = jwt.get_unverified_header(token)
            keys = json.loads(open(jwks_file, encoding="utf-8").read())["keys"]
            jwk = next(k for k in keys if k.get("kid") == header.get("kid"))
            key = jwt.PyJWK(jwk).key
        else:
            if _jwks_client is None:
                _jwks_client = jwt.PyJWKClient(os.getenv("KEEL_ENTRA_JWKS_URL", f"https://login.microsoftonline.com/{tid}/discovery/v2.0/keys"))
            key = _jwks_client.get_signing_key_from_jwt(token).key
        return jwt.decode(token, key, algorithms=["RS256"], audience=aud, issuer=issuer)
    except Exception as e:  # noqa: BLE001 - any verification failure is a 401
        raise AuthError(401, "Invalid access token") from e


def authenticate(path: str, headers: dict[str, str], query: dict[str, str]) -> tuple[Principal, str]:
    """Return the caller and the path to route (/mcp/agents/<id> is routed to /mcp)."""
    agent_from_path = None
    if path.startswith(PREFIX):
        agent_from_path = path[len(PREFIX):].strip("/").split("/")[0].upper() or None
        path = "/mcp"
    auth = headers.get("authorization", "")
    token = auth[7:] if auth.lower().startswith("bearer ") else None
    admin = _same(token, os.getenv("KEEL_ADMIN_TOKEN"))
    if _same(token, os.getenv("KEEL_SERVICE_TOKEN")) or admin:
        return Principal("service", (headers.get("x-keel-agent") or agent_from_path or "").upper() or None,
                         user=headers.get("x-keel-user"), tenant=headers.get("x-keel-tenant"),
                         persona=headers.get("x-keel-persona"), admin=admin), path
    m = mode()
    if m == "entra":
        if not token:
            raise AuthError(401, "Bearer token required")
        claims = _verify_entra(token)
        required = os.getenv("KEEL_REQUIRED_ROLE", "SalesAdvisor.User")
        roles = list(claims.get("roles") or [])
        if required and required not in roles:
            raise AuthError(403, f"Role {required} required")
        if not agent_from_path:
            raise AuthError(404, "Use /mcp/agents/<agent-id>")
        return Principal("user", agent_from_path, user=claims.get("oid") or claims.get("sub"), tenant=claims.get("tid"), roles=roles), path
    if m == "dev":
        return Principal("dev", (headers.get("x-keel-agent") or agent_from_path or query.get("agent") or "").upper() or None,
                         user=headers.get("x-keel-user"), tenant=headers.get("x-keel-tenant") or query.get("tenant"),
                         persona=headers.get("x-keel-persona")), path
    raise AuthError(401, "Unauthenticated")


class AuthMiddleware:
    """ASGI middleware: authenticates /mcp and /governance requests and stores the caller in
    request.state.keel_principal. /healthz stays open."""

    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http" or scope["path"] == "/healthz":
            return await self.app(scope, receive, send)
        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        from urllib.parse import parse_qsl
        query = dict(parse_qsl(scope.get("query_string", b"").decode()))
        try:
            principal, path = authenticate(scope["path"], headers, query)
            if scope["path"].startswith("/governance") and principal.kind == "user":
                raise AuthError(403, "Governance routes are for Keel services only")
        except AuthError as e:
            body = json.dumps({"error": str(e)}).encode()
            await send({"type": "http.response.start", "status": e.status, "headers": [(b"content-type", b"application/json"), (b"www-authenticate", b"Bearer")]})
            await send({"type": "http.response.body", "body": body})
            return
        scope = dict(scope, path=path, raw_path=path.encode())
        scope.setdefault("state", {})
        scope["state"] = dict(scope["state"], keel_principal=principal)
        await self.app(scope, receive, send)
