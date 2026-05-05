# Application MCP

MCP server hosted by the **Chat Backend** that exposes a channel's StatGPT tools (data query, RAG, glossary, web
search, …) over the [Model Context Protocol](https://modelcontextprotocol.io/), so DIAL applications and other
MCP-aware clients can invoke them under their own LLM control.

## 🎯 Scope

- **Does**: Exposes the same primitives the StatGPT supreme agent uses internally.
- **Does not**: Replace the supreme agent's `/chat/completions` endpoint, pick tools, or compose multi-tool answers.
- **Configuration**: Tools surfaced for `deployment_id=foo` come directly from `foo`'s channel YAML — no
  MCP-specific override.

## 🔌 Endpoint

| Property   | Value                                                  |
|------------|--------------------------------------------------------|
| Path       | `POST /api/v1/{deployment_id}/mcp` on Chat Backend     |
| Mounted in | `statgpt/app/application/app_factory.py`                |
| Transport  | `streamable-http`, `stateless_http=True`               |
| Bootstrap  | `statgpt/app/mcp/app.py`                                |
| Provider   | `statgpt/app/mcp/provider.py` (`ChannelToolProvider`)  |

`{deployment_id}` selects the channel; tools and config differ per channel. The endpoint is part of the Chat Backend
image — there is no separate enable flag. To make it reachable, register StatGPT as a DIAL Application (see
[Authentication & Authorization](#-authentication--authorization) below).

The server's `instructions=` field (sent to clients during MCP `initialize`) reads:

> *This server provides tools from the StatGPT platform for querying official statistics data, searching publications,
> looking up glossary terms, and more. Tools are channel-specific and depend on the deployment configuration.*

## ⚙️ Dynamic Tool Surface

On every `tools/list` and `tools/call`, `ChannelToolProvider`:

1. Reads `Authorization` + `api-key` from headers and builds an `AuthContext`.
2. Resolves `{deployment_id}` to a `ChannelServiceFacade` and loads `ChannelConfig`.
3. Wraps each `StatGptTool` in `_McpToolAdapter`, exposing it as an MCP tool.

The MCP tool **name** and **description** come from the channel YAML; the **parameter schema** comes from each tool's
`get_public_args_schema()`.

## 🛠️ Tools Catalog

Application MCP exposes whichever tools the channel YAML enables. The full tool catalog and per-tool semantics live
in [Architecture / Tools](./tools.md). The implementation maps each tool config to a class via
[`statgpt/common/schemas/enums.py::ToolTypes`](https://github.com/epam/statgpt-backend).

## 📝 Configuring the Tool Surface

Channel YAML excerpt (from
[`tools.yaml`](https://github.com/epam/statgpt-backend/blob/development/configurations/clients/sample/tools.yaml)):

```yaml
tools:
  - type: available_datasets
    name: "Available_Datasets"
    description: >-
      Provides a list of all available datasets … This tool does not accept any arguments.
    details:
      version: full
      include_indicator_count: true

  - type: data_query
    name: "Query_Data"
    description: >-
      Translates a natural-language question into an SDMX query and executes it.
    details:
      # ... model deployments, prompts, etc.
```

| Field         | Becomes                                                                   |
|---------------|---------------------------------------------------------------------------|
| `type`        | Implementation class (see [Architecture / Tools](./tools.md)).            |
| `name`        | MCP tool name surfaced via `tools/list`.                                  |
| `description` | MCP tool description fed to the calling LLM.                              |

Channel-level config (LLM models, glossaries, supreme-agent settings) lives in `channels.yaml` — see
[Admin Guide](../guides/admin-guide.md). The MCP server inherits from there automatically.

## 📦 Returning Data Resources

`DATA_QUERY` is the only tool emitting non-text results. In addition to a textual summary it returns one or more
`text/csv` resources via `data_query_artifact_to_resources()` (`statgpt/app/mcp/attachments.py`):

```
URI: statgpt://data_query/{path}/{timestamp}.csv
```

## 🔄 Sample MCP Exchanges

JSON-RPC over `streamable-http`. Headers populated by DIAL after the OAuth handshake — see
[Authentication & Authorization](#-authentication--authorization) below.

> **📝 Note**: The `inputSchema` payloads below are illustrative. The real schemas come from each tool's
> `get_public_args_schema()` and may include additional optional fields.

### `tools/list`

```http
POST /api/v1/statgpt-sample/mcp HTTP/1.1
Authorization: Bearer <user JWT>
api-key: <DIAL per-request key>
Content-Type: application/json

{ "jsonrpc": "2.0", "id": 1, "method": "tools/list" }
```

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "tools": [
      { "name": "Available_Datasets",
        "description": "Provides a list of all available datasets...",
        "inputSchema": { "type": "object", "properties": {}, "required": [] } },
      { "name": "Query_Data",
        "description": "Translates a natural-language question into an SDMX query...",
        "inputSchema": {
          "type": "object",
          "properties": { "query": { "type": "string" } },
          "required": ["query"] } }
    ]
  }
}
```

### `tools/call`

```http
POST /api/v1/statgpt-sample/mcp HTTP/1.1
Authorization: Bearer <user JWT>
api-key: <DIAL per-request key>
Content-Type: application/json

{ "jsonrpc": "2.0", "id": 2, "method": "tools/call",
  "params": {
    "name": "Query_Data",
    "arguments": { "query": "What is the IMF WEO projection for US GDP for the next 2 years?" } } }
```

```json
{
  "jsonrpc": "2.0", "id": 2,
  "result": {
    "content": [
      { "type": "text", "text": "Here is the IMF WEO projection for US GDP ..." },
      { "type": "resource",
        "resource": {
          "uri": "statgpt://data_query/imf-weo/{YYYYMMDDTHHMMSSZ}.csv",
          "mimeType": "text/csv",
          "text": "country,year,value\nUSA,2026,...\nUSA,2027,..." } }
    ]
  }
}
```

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
3. StatGPT MCP processes the call (see the next subsection).

### How Application MCP Consumes the Forwarded Auth

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

The MCP server runs with `stateless_http=True` (`statgpt/app/mcp/app.py`), so token freshness is established per
request from the headers; nothing is cached across calls.

## 📚 References

- [MCP Authorization specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) —
  the canonical OAuth 2.1 + PKCE discovery flow that DIAL implements in front of the StatGPT MCP endpoint.
- [DIAL Core applications.md](https://github.com/epam/ai-dial-core/blob/development/docs/dynamic-settings/applications.md) —
  Application config schema (`mcpEndpoint`, `forwardAuthToken`, …).
- [DIAL per-request keys](https://docs.dialx.ai/platform/core/per-request-keys) — how DIAL Core injects `api-key`
  headers on every proxied application call.
