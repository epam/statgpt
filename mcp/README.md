# Application MCP

MCP server hosted by the **Chat Backend** that republishes a channel's StatGPT tools (data query, RAG, glossary, web
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

`{deployment_id}` selects the channel; tools and config differ per channel.

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

Tool types registerable in a channel
([`statgpt/common/schemas/enums.py::ToolTypes`](https://github.com/epam/statgpt-backend)):

| Tool type                | Implementation class        | Purpose                                                              |
|--------------------------|-----------------------------|----------------------------------------------------------------------|
| `AVAILABLE_DATASETS`     | `AvailableDatasetsTool`     | List datasets available to the channel.                              |
| `DATASETS_METADATA`      | `DatasetsMetadataTool`      | Metadata for a specific set of datasets.                             |
| `DATASET_STRUCTURE`      | `DatasetStructureTool`      | Dimensions and attributes of a dataset.                              |
| `AVAILABLE_PUBLICATIONS` | `AvailablePublicationsTool` | List publication types.                                              |
| `AVAILABLE_TERMS`        | `AvailableTermsTool`        | List glossary terms.                                                 |
| `TERM_DEFINITIONS`       | `TermDefinitionsTool`       | Look up glossary definitions.                                        |
| `DATA_QUERY`             | `DataQueryTool`             | Translate NL into SDMX, execute, return text + CSV resource.         |
| `FILE_RAG`               | `FileRagTool`               | RAG over publication content.                                        |
| `PLAIN_CONTENT`          | `PlainContentTool`          | Static content with env-var substitution.                            |
| `WEB_SEARCH`             | `WebSearchTool`             | Web search with summarized results.                                  |
| `WEB_SEARCH_AGENT`       | `WebSearchAgentTool`        | Web search routed through an agent.                                  |

Functional details → [Architecture / Tools](../architecture/tools.md).

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

| Field         | Becomes                                       |
|---------------|-----------------------------------------------|
| `type`        | Implementation class (Tools Catalog above).   |
| `name`        | MCP tool name surfaced via `tools/list`.      |
| `description` | MCP tool description fed to the calling LLM.  |

Channel-level config (LLM models, glossaries, supreme-agent settings) lives in `channels.yaml` — see
[Admin Guide](../guides/admin-guide.md). The MCP server inherits from there automatically.

## 📦 Returning Data Resources

`DATA_QUERY` is the only tool emitting non-text results. In addition to a textual summary it returns one or more
`text/csv` resources via `data_query_artifact_to_resources()` (`statgpt/app/mcp/attachments.py`):

```
URI: statgpt://data_query/{path}/{timestamp}.csv
```

## 🔐 Authentication

DIAL terminates auth and forwards `Authorization: Bearer <user JWT>` and `api-key: <per-request key>`.
`DialAuthCredentials.from_headers` (`statgpt/app/security/credentials.py`) is wrapped by `create_auth_context`
(`statgpt/app/security/auth_context.py`); the MCP provider calls it with the default `bearer_token_required=False`,
so the result is always a `UserAuthContext`:

- **Bearer present** — JWT is reused for callbacks into DIAL via `UserAuthContext.dial_access_token`.
- **Bearer absent** — `dial_access_token` is `None`; any tool that needs the JWT fails at use time, and a missing
  `api-key` raises `MissingApiKeyError` lazily during channel resolution.

`SystemUserAuthContext` is **not reached from MCP** — it requires `bearer_token_required=True` at the call site,
which `statgpt/app/mcp/provider.py` does not pass. Auth failures during channel resolution cause `tools/list` to
return an empty list and `tools/call` to error. Full flow → [auth.md](./auth.md).

## 🤖 End-to-End: LLM Client Walkthrough

1. **Operator** registers StatGPT in DIAL as a **DIAL Application** with `mcpEndpoint`.
   See [auth.md §1](./auth.md#1-registration-dial-application).
2. **MCP client** issues `tools/list` against DIAL. DIAL responds with `401 Unauthorized` + Protected Resource
   Metadata (RFC 9728) pointing at the IDP. The client runs OAuth 2.1 + PKCE directly against
   the IDP — DIAL is *not* in the OAuth path.
3. **Authenticated tool list.** Client retries `tools/list` with `Authorization: Bearer <user JWT>`. DIAL forwards
   the bearer plus its own `api-key: <per-request key>` to the StatGPT MCP endpoint.
4. **LLM** picks a tool (e.g. `Available_Datasets`), issues `tools/call`; DIAL forwards both headers.
5. For data questions the LLM picks `Query_Data`; the response includes text + CSV resource (above).
6. **Multi-tool reasoning is the client's job, not the MCP's.** For supreme-agent orchestration use the Chat Backend's
   `/chat/completions` instead.

For local-dev setups without DIAL, see the FastMCP HTTP-transport docs and the
[MCP authorization spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization).

## 🚀 Deployment

Part of the Chat Backend image; no enable flag. Reachable through DIAL by registering StatGPT as a **DIAL Application**
with the MCP endpoint URL set on the `mcpEndpoint` field. See [auth.md](./auth.md) for the full configuration and
auth model.

## 🔗 See Also

- [auth.md](./auth.md) — DIAL Application config, auth flow, MCP-spec relationship
- [Architecture / Tools](../architecture/tools.md)
- [Architecture / Services](../architecture/services.md)
