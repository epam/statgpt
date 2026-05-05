# Application MCP

Application MCP gives AI agents — Claude, Cursor, custom DIAL applications, and other MCP-aware LLM clients —
agentic access to a channel's StatGPT tools (data query, RAG, glossary, web search, …) over the
[Model Context Protocol](https://modelcontextprotocol.io/), so the agent can invoke those tools inside its own
reasoning loop.

## 🎯 Scope

- **Does**: Exposes the same primitives the StatGPT supreme agent uses internally.
- **Does not**: Replace the supreme agent's `/chat/completions` endpoint, pick tools, or compose multi-tool answers.
- **Configuration**: Tools surfaced for `deployment_id=foo` come directly from `foo`'s channel YAML — no MCP-specific override.

## 🔌 Endpoint

| Property   | Value                                                  |
|------------|--------------------------------------------------------|
| Path       | `POST /api/v1/{deployment_id}/mcp` on Chat Backend     |
| Transport  | HTTP streaming (`streamable-http`)                     |

`{deployment_id}` selects the channel; tools and config differ per channel. The endpoint is part of the Chat Backend
image — there is no separate enable flag. To make it reachable, register StatGPT as a DIAL Application (see
[Authentication & Authorization](#-authentication--authorization) below).

## 🛠️ Tools

Application MCP exposes whichever tools the channel YAML enables. The full tool catalog and per-tool semantics live in [Architecture / Tools](./tools.md).

## 🔐 Authentication & Authorization

Application MCP is wired into AI DIAL as a **DIAL Application**. StatGPT itself runs no OAuth flow. DIAL Core acts as
the MCP-spec authorization-server discovery layer in front of the MCP endpoint, points clients at the configured IDP,
and forwards the resulting bearer + per-request key on every proxied tool call.

### Registration: DIAL Application

StatGPT is registered with DIAL as a **DIAL Application**. A DIAL Application can declare both a chat-completion
endpoint and an MCP endpoint side-by-side; DIAL Core proxies traffic to either through its routing layer.

Authoritative DIAL docs:

- Application administration UI / fields → [docs.dialx.ai entities-applications](https://docs.dialx.ai/tutorials/admin/entities-applications).
- Application config schema → [DIAL Core applications.md](https://github.com/epam/ai-dial-core/blob/development/docs/dynamic-settings/applications.md).
- Per-request keys → [docs.dialx.ai per-request-keys](https://docs.dialx.ai/platform/core/per-request-keys).

Relevant fields on the StatGPT Application:

| Field              | Value                                                  | Effect                                                                                                          |
|--------------------|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `mcpEndpoint`      | `https://<chat-backend>/api/v1/{deployment_id}/mcp`    | The MCP endpoint DIAL Core proxies to.                                                                          |
| `forwardAuthToken` | `true`                                                  | DIAL forwards the caller's `Authorization: Bearer …` header to the application unchanged on every proxied call. |

There is no per-application OAuth client config (no `client_id`, no `redirect_uri`, no DIAL-side signin endpoint).
DIAL's job is discovery + forwarding, not running OAuth itself.

### Auth Flow

The flow follows the [MCP authorization spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
discovery flow, with two architectural details:

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
3. StatGPT MCP treats both headers as already-validated input — it does no token validation of its own. If neither
   header reaches the server, `tools/list` returns empty and `tools/call` errors.

### Relationship to the MCP Authorization Specification

At the wire level StatGPT's MCP authorization is **spec-compliant** — a spec-compliant MCP client (one that
implements the discovery flow described in
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

**Why this split:**

- **Single IDP across the platform** — DIAL Core terminates discovery for every DIAL Application; StatGPT MCP
  doesn't reimplement RFC 9728 / RFC 8414 endpoints.
- **Smaller StatGPT auth surface** — StatGPT processes never run the OAuth handshake, so they cannot leak codes,
  PKCE verifiers, or client secrets.
- **One audit / per-request-key enforcement layer** — DIAL Core handles both, consistent with how it handles every
  other DIAL Application.

### Refresh Tokens & Session Lifecycle

Refresh tokens are **owned by the MCP client** and live in its OAuth session against the IDP. DIAL is not in the
refresh path:

- When the client's access token expires, the client runs the refresh-token grant directly against the IDP and gets
  a new access token.
- The new bearer is presented to DIAL on the next call; DIAL forwards it, same as before.
- StatGPT MCP never sees refresh tokens — it only ever sees a current access token in the `Authorization` header.
- If the IDP rejects a refresh (session revoked, etc.), the client gets a fresh 401 from DIAL on its next call and
  the discovery flow starts over.

The MCP server is stateless — token freshness is established per request from the forwarded headers, with nothing
cached across calls.

## 📚 References

- [MCP Authorization specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) —
  the canonical OAuth 2.1 + PKCE discovery flow that DIAL implements in front of the StatGPT MCP endpoint.
- [DIAL Core applications.md](https://github.com/epam/ai-dial-core/blob/development/docs/dynamic-settings/applications.md) —
  Application config schema (`mcpEndpoint`, `forwardAuthToken`, …).
- [DIAL per-request keys](https://docs.dialx.ai/platform/core/per-request-keys) — how DIAL Core injects `api-key`
  headers on every proxied application call.
