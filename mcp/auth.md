# 🔐 MCP Authentication & Authorization

[Application MCP](./README.md) is wired into AI DIAL as a **DIAL Application**. StatGPT itself runs no OAuth flow.
DIAL Core acts as the MCP-spec authorization-server discovery layer in front of the MCP endpoint, points clients at
the configured IDP, and forwards the resulting bearer + per-request key on every proxied tool call.

## 🧩 1. Registration: DIAL Application

StatGPT is registered with DIAL as a **DIAL Application**. A DIAL Application can declare both a chat-completion
endpoint and an MCP endpoint side-by-side; DIAL Core proxies traffic to either through its routing layer.

Authoritative DIAL docs:

- Application administration UI / fields → [docs.dialx.ai entities-applications](https://docs.dialx.ai/tutorials/admin/entities-applications)
  (the page explicitly defines "Chat Endpoint" and "MCP Endpoint" as Application properties).
- Application config schema → [DIAL Core applications.md](https://github.com/epam/ai-dial-core/blob/development/docs/dynamic-settings/applications.md)
- Per-request keys → [docs.dialx.ai per-request-keys](https://docs.dialx.ai/platform/core/per-request-keys).

Relevant fields on the StatGPT Application:

| Field                       | Value                                                  | Effect                                                                                                                         |
|-----------------------------|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `mcpEndpoint`               | `https://<chat-backend>/api/v1/{deployment_id}/mcp`    | The MCP endpoint DIAL Core proxies to.                                                                                         |
| `endpoint` (chat completion)| (separate StatGPT chat endpoint)                        | Listed for completeness; not relevant to MCP traffic.                                                                          |
| `forwardAuthToken`          | `true`                                                  | DIAL forwards the caller's `Authorization: Bearer …` header to the application unchanged on every proxied call.                |
| `accessibleByPerRequestKey` | `true`                                                  | Enables DIAL's per-request key forwarding in the `api-key` header.                                                             |

There is no per-application OAuth client config (no `client_id`, no `redirect_uri`, no DIAL-side signin endpoint).
DIAL's job is discovery + forwarding, not running OAuth itself.

## 🔁 2. Auth Flow

The flow is just the canonical [MCP authorization spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
discovery dance, with two architectural details:

- **DIAL plays the resource-server-front role.** It returns the 401 + `WWW-Authenticate`, hosts
  `/.well-known/oauth-protected-resource` (RFC 9728), and points clients at the IDP via the `authorization_servers`
  field. StatGPT MCP itself has no `/.well-known` endpoints and does not return 401s — it never sees a request
  without a bearer.
- **DIAL is not in the OAuth path.** The OAuth 2.1 + PKCE handshake happens directly between the MCP client and the
  IDP (Keycloak, Entra ID, …). DIAL holds no PKCE verifier, no authorization code, no refresh token, no per-app
  client credentials.

After the client has a bearer:

1. Client → DIAL: `tools/call` with `Authorization: Bearer <user JWT>`.
2. DIAL → StatGPT MCP: same call, with the bearer forwarded (because `forwardAuthToken=true`) and an additional
   `api-key: <per-request key>` header.
3. StatGPT MCP processes the call (see §3).

## 🪪 3. How Application MCP Consumes the Forwarded Auth

`DialAuthCredentials.from_headers` (`statgpt/app/security/credentials.py`) reads `api-key` and
`Authorization: Bearer …`. `create_auth_context` (`statgpt/app/security/auth_context.py`) is invoked by the MCP
provider with the default `bearer_token_required=False`, which means it always returns a `UserAuthContext`:

| Context                 | When                                          | Notes                                                                                                                                                                                                              |
|-------------------------|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `UserAuthContext`       | Always (on the MCP entry path)                 | If a bearer is present the JWT is reused for callbacks into DIAL via `UserAuthContext.dial_access_token`. If absent, `dial_access_token` is `None` and any tool that needs the JWT will fail at use time.        |
| `SystemUserAuthContext` | Not reached from MCP                           | Would require `bearer_token_required=True` at the call site, which `statgpt/app/mcp/provider.py` does not pass. Reserved for chat-completion / DIAL-SDK paths that opt in to that flag.                            |

Subsequent failures are lazy: a missing `api-key` raises `MissingApiKeyError` when first dereferenced; an
authentication or authorization error during channel resolution causes `_list_tools` to swallow it and return an
empty tool list (`tools/call` errors).

## 📜 4. Relationship to the MCP Authorization Specification

At the wire level StatGPT's MCP authorization is **spec-compliant** — a spec-compliant MCP client (one that
implements the discovery dance described in
[MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)) works against the
StatGPT MCP endpoint without modification. The architectural twist is that the OAuth resource-server role is **split
across two HTTP participants**:

| Role                                                | Who handles it                  |
|-----------------------------------------------------|---------------------------------|
| Returns `401 Unauthorized` with `WWW-Authenticate`  | DIAL                            |
| Hosts `/.well-known/oauth-protected-resource` (RFC 9728) | DIAL                       |
| Validates and uses the presented bearer             | StatGPT MCP (after DIAL forwards it) |
| Acts as the OAuth authorization server              | The IDP (Keycloak, Entra ID, …) |

This split is invisible to MCP clients — they see one logical resource server that behaves correctly under
[RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728), and run their handshake against whatever
`authorization_servers` URL DIAL advertised.

### Why this split

- **Single IDP across the platform** — DIAL Core terminates discovery for every DIAL Application; StatGPT MCP
  doesn't reimplement RFC 9728 / RFC 8414 endpoints.
- **Smaller StatGPT auth surface** — StatGPT processes never run the OAuth dance, so they cannot leak codes,
  PKCE verifiers, or client secrets.
- **One audit / per-request-key enforcement layer** — DIAL Core handles both, consistent with how it handles every
  other DIAL Application.

## 🔁 5. Refresh Tokens & Session Lifecycle

Refresh tokens are **owned by the MCP client** and live in its OAuth session against the IDP. DIAL is not in the
refresh path:

- When the client's access token expires, the client runs the refresh-token grant directly against the IDP and gets
  a new access token.
- The new bearer is presented to DIAL on the next call; DIAL forwards it, same as before.
- StatGPT MCP never sees refresh tokens — it only ever sees a current access token in the `Authorization` header.
- If the IDP rejects a refresh (session revoked, etc.), the client gets a fresh 401 from DIAL on its next call and
  the discovery dance starts over from §2 step 1.

The MCP server runs with `stateless_http=True` (`statgpt/app/mcp/app.py`), so token freshness is established per
request from the headers; nothing is cached across calls.

## 📚 6. Authoritative References

### Model Context Protocol

- Protocol home: <https://modelcontextprotocol.io/>
- Authorization specification: <https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization>
- Security best practices: <https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices>
- FastMCP framework: <https://gofastmcp.com/>

### OAuth / IETF (referenced by MCP)

- OAuth 2.1 (IETF draft): <https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13>
- RFC 9728 — Protected Resource Metadata: <https://datatracker.ietf.org/doc/html/rfc9728>
- RFC 8414 — Authorization Server Metadata: <https://datatracker.ietf.org/doc/html/rfc8414>
- RFC 7591 — Dynamic Client Registration: <https://datatracker.ietf.org/doc/html/rfc7591>
- RFC 8707 — Resource Indicators: <https://datatracker.ietf.org/doc/html/rfc8707>

### AI DIAL

- Homepage: <https://dialx.ai>
- Documentation: <https://docs.dialx.ai/>
- Applications administration: <https://docs.dialx.ai/tutorials/admin/entities-applications>
- Application config schema (DIAL Core): <https://github.com/epam/ai-dial-core/blob/development/docs/dynamic-settings/applications.md>
- Per-request keys: <https://docs.dialx.ai/platform/core/per-request-keys>
- JWT auth & access control: <https://docs.dialx.ai/tutorials/devops/auth-and-access-control/jwt>

### Internal (this repo)

- [README.md](./README.md) — Application MCP details
- [Admin Azure Auth Guide](../guides/admin-azure-auth-guide.md)
