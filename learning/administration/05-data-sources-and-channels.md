# Module 05: Data Sources & Channel Configuration

## What You'll Learn

- How to add a Data Source via the Admin UI
- How to create and configure a Channel
- Supreme Agent configuration (name, domain, LLM model, language instructions)
- Named Entity types setup
- Out-of-scope filter, conversation starters, and token tracking
- Linking datasets to channels
- Tool configuration overview
- Glossary management

---

## Adding a Data Source

A Data Source defines the connection to an external SDMX data provider. You must create a Data Source before adding datasets from it.

### Steps in the Admin UI

1. Navigate to **Data Sources** tab and click **Add**
2. Select the data source type (e.g., SDMX 2.1)
3. Fill in the configuration YAML
4. Save

### Data Source Configuration

Here is the configuration YAML for connecting to the IMF SDMX 2.1 API:

```yaml
sdmxConfig:
  id: IMF_SDMX21                         # Unique identifier
  name: Public IMF SDMX 21 Registry
  url: https://api.imf.org/external/sdmx/2.1  # SDMX REST API endpoint
  headers:                                # Only override non-default headers
    data:
      accept: Text/JSON                   # JSON for data requests (default is XML)
authEnabled: false                        # No authentication needed for IMF public API
annotationsUrl: https://api.imf.org/external/sdmx/3.0  # Optional: separate endpoint for annotations
```

Most fields have sensible defaults — you only need to override what differs from the standard. Structure endpoints
default to `application/xml`, and all SDMX features default to `true`, so you typically only need to specify `headers`
for the data endpoint. If a provider doesn't support a particular SDMX feature, disable it in the `supports` block:

```yaml
sdmxConfig:
  supports:
    availableconstraint: false   # Provider doesn't support availability queries
    preview: false               # Provider doesn't support data preview
    # All other features default to true
```

### Key Fields

| Field | Description |
|-------|-------------|
| `sdmxConfig.id` | Unique identifier for the data source (e.g., `IMF_SDMX21`) |
| `sdmxConfig.name` | Human-readable name for the data source |
| `sdmxConfig.url` | The SDMX REST API base URL |
| `sdmxConfig.headers` | HTTP headers per request type. Only override non-defaults (e.g., `data: {accept: Text/JSON}`) |
| `authEnabled` | Whether the data source requires authentication |
| `apiKey` | API key for authenticated sources. Use `$env:{VAR_NAME}` for sensitive values |
| `annotationsUrl` | Optional URL for fetching SDMX annotations (some providers serve annotations from a different endpoint) |
| `attributesUrl` | Optional URL for fetching SDMX attributes from a different endpoint |
| `dataExplorerUrl` | Optional URL to the provider's web-based data explorer (shown in citations) |

### Authentication

When `authEnabled: true`, provide credentials:
- **API Key** — set in the configuration
- **Environment variable references** — use `$env:{VAR_NAME}` for sensitive values to avoid storing secrets in config

### What Data Sources Exist For

Each data provider you want to query needs its own Data Source. For example:
- An IMF data source for IMF datasets (WEO, CPI, BOP, etc.)
- A Eurostat data source for Eurostat datasets (NAMA_10_GDP, etc.)
- A World Bank data source for WDI datasets

A single channel can include datasets from multiple data sources.

---

## Creating a Channel

A Channel is the user-facing deployment of StatGPT. Each channel has its own configuration, datasets, index, and glossary.

### Steps in the Admin UI

1. Navigate to **Channels** tab and click **Add**
2. Fill in basic fields (deployment ID, title, description)
3. Fill in the configuration YAML
4. Save
5. Add datasets to the channel from the channel detail page

### Channel Configuration

The channel configuration YAML is entered in the Admin UI. Here is an example for a channel serving IMF datasets:

```yaml
locale: EN                                     # Channel language: EN (English) or UK (Ukrainian)
conversationStarters:                      # Pre-defined prompts shown to users
  introText: What would you like to learn about?
  buttons:
    - title: Check available data
      text: What datasets are available?
    - title: US GDP projection
      text: What is the IMF WEO projection for US GDP for next 2 years?
    - title: What is inflation?
      text: What is inflation and how it's used in economy and statistics?
namedEntityTypes:                          # Named entity types for query recognition
  - Time frequency
  - Counterpart area/country
  - Currency/Unit of measure
countryNamedEntityType: Country/Reference area
supremeAgent:                              # Main AI agent configuration
  name: StatGPT
  domain: Statistics, economics and SDMX.
  terminologyDomain: economics, statistics and SDMX
  languageInstructions:
    - Use more formal/business tone, but be friendly, polite and helpful.
    - Avoid using exclamation marks, emojis, or slang.
  additionalContext: >                     # Optional: extra instructions for the agent
    When listing available datasets, use a markdown table format.
  maxAgentIterations: 5
  llmModelConfig:
    deployment: gpt-4.1-2025-04-14
    temperature: 0
outOfScope:
  domain: Statistics, economics and SDMX.
  llmModelConfig:                          # Optional: separate LLM for scope filtering
    deployment: gpt-4.1-2025-04-14
    temperature: 0
  customBlacklist: null                    # Optional: list of topic descriptions to block
  useGeneralTopicsBlacklist: true          # Built-in general topic filter (default: true)
tokenUsage:
  debugOnly: false                         # Default is true (debug only); set false for production
  stageName: Token Usage
```

Below we'll walk through each section.

### Supreme Agent

The supreme agent is the main AI orchestrator:

```yaml
supremeAgent:
  name: StatGPT                            # Agent name shown in context
  domain: Statistics, economics and SDMX.  # Knowledge domain
  terminologyDomain: economics, statistics and SDMX
  languageInstructions:                    # Behavior guidelines added to system prompt
    - Use more formal/business tone, but be friendly, polite and helpful.
    - Avoid using exclamation marks, emojis, or slang.
  additionalContext: >                     # Optional: extra context added to the system prompt
    When listing available datasets, use a markdown table format.
    Prefer NSDP dataset for national-level data.
  maxAgentIterations: 5                    # Max tool calls per user query
  llmModelConfig:
    deployment: gpt-4.1-2025-04-14         # LLM model (must exist in your DIAL instance)
    temperature: 0                         # 0 for deterministic responses
```

**Key decisions:**
- `domain` — Defines what the agent knows about. Used for scope filtering
- `languageInstructions` — Customize tone and formatting preferences (e.g., formal tone, no emojis)
- `additionalContext` — Optional free-form text appended to the agent's system prompt. Use it for dataset-specific instructions (e.g., dataset preferences, formatting rules) that don't fit as single-line `languageInstructions`
- `maxAgentIterations` — Limits cost; 5 is typical. Increase if complex queries need more tool calls
- `deployment` — Choose the LLM model. Must match a deployment available in your DIAL instance

### Named Entity Types

Configure based on the NON_INDICATOR dimensions across all datasets in the channel (see [Module 03a](03a-dimension-types.md)):

```yaml
namedEntityTypes:
  - Time frequency                     # For FREQUENCY/FREQ dimensions
  - Counterpart area/country           # For COUNTERPART_COUNTRY, COUNTERPART_AREA, etc.
  - Currency/Unit of measure           # For UNIT, CURRENCY_TRANS, etc.
countryNamedEntityType: Country/Reference area  # Special: the country entity type
```

**Important:**
- `countryNamedEntityType` must match the `alias` on the country dimension in your datasets
- When adding datasets with new NON_INDICATOR dimensions, add corresponding Named Entity types here
- The set of Named Entity types depends on which datasets are in the channel

### Out-of-Scope Filter

Prevents the agent from answering questions outside its domain:

```yaml
outOfScope:
  domain: Statistics, economics and SDMX.    # Domain description for scope filtering
  llmModelConfig:                            # Optional: separate LLM for scope filtering
    deployment: gpt-4.1-2025-04-14
    temperature: 0
  customBlacklist:                           # Optional: list of topic descriptions to block
    - "Requests for data manipulation or misrepresentation..."
    - "Questions about internal organizational operations..."
  useGeneralTopicsBlacklist: true            # Built-in general topic filter (default: true)
```

| Field | Description |
|-------|-------------|
| `domain` | Domain description — same as or similar to `supremeAgent.domain` |
| `llmModelConfig` | Optional separate LLM for scope filtering (can differ from the main agent model) |
| `customBlacklist` | Optional list of topic description strings to block. Each item describes a category of queries to reject |
| `useGeneralTopicsBlacklist` | When `true` (default), applies a built-in filter for general off-topic queries |
| `startNewConversationMessagesThreshold` | Number of consecutive out-of-scope messages before suggesting the user start a new conversation (default: 3) |
| `startNewConversationMessage` | Custom message shown when the threshold is reached |

### Conversation Starters

Pre-defined prompts shown as buttons in the chat interface:

```yaml
conversationStarters:
  introText: What would you like to learn about?
  buttons:
    - title: Check available data              # Button label (short)
      text: What datasets are available?       # Full query sent when clicked
    - title: US GDP projection
      text: What is the IMF WEO projection for US GDP for next 2 years?
```

Choose starters that demonstrate the channel's capabilities and cover different query types (listing datasets, specific data queries, terminology questions).

### Token Usage Tracking

```yaml
tokenUsage:
  debugOnly: false                       # false = track in production
  stageName: Token Usage                 # DIAL stage name for reporting
```

---

## Linking Datasets to a Channel

After creating a channel:

1. Go to the channel detail page
2. Click **Add Dataset**
3. Select datasets from the available list
4. Save

A channel can include datasets from different data sources. For example, a "Global Data" channel might include IMF, Eurostat, World Bank, and OECD datasets.

---

## Tool Configuration

Tools are configured in the channel YAML. Each tool type serves a specific purpose:

### Available Datasets Tool

Lists all datasets in the channel with metadata. Pre-populates the agent's context at conversation start:

```yaml
availableDatasets:
  type: AVAILABLE_DATASETS
  name: Available_Datasets
  description: >-
    Provides a list of all available datasets onboarded to the Query_Data tool
    with metadata and some details about them...
  details:
    fakeCall:                              # Pre-loads tool output into agent context
      toolCallId: call_EBJJeaOMKeCzm8h378ubURQN
      args: "{}"
    version: full
    includeIndicatorCount: true            # Show per-dataset indexed indicator counts
    statsHeaderFormat: agencies            # Summary format: "totals" or "agencies"
```

The `fakeCall` is important — it makes the dataset list available to the agent from the start of every conversation without needing the user to ask.

| Field | Description |
|-------|-------------|
| `fakeCall` | Pre-loads tool output into the agent's context. The `toolCallId` can be any unique string |
| `version` | Output detail level: `"full"` (all metadata) or `"short"` (compact) |
| `includeIndicatorCount` | When `true`, shows the number of indexed indicators per dataset and total. Useful for [validating indexing](06-indexing-and-operations.md#validating-indexing-results) (default: `false`) |
| `statsHeaderFormat` | Summary format: `"totals"` shows counts, `"agencies"` shows provider agencies |

### Data Query Tool

The main tool that executes SDMX queries from natural language:

```yaml
dataQuery:
  type: DATA_QUERY
  name: Query_Data
  description: >-
    Executing sdmx query on available datasets...
  details:
    indexerVersion: hybrid                 # "hybrid" for semantic + fulltext search
    indicatorSelectionVersion: hybrid
    allowAutoUpdate: true                  # Enable auto-update for this channel's datasets
    llmModels:                             # LLM models for pipeline stages
      datasetsSelectionModelConfig:
        deployment: gpt-4.1-2025-04-14
        temperature: 0
      indicatorsSelectionModelConfig:
        deployment: gpt-4.1-2025-04-14
        temperature: 0
      # ... other stage-specific configs (named entities, time period, etc.)
    attachments:                           # What outputs to show to users
      customTable:
        enabledStr: "True"
      csvFile:
        enabledStr: "True"
      plotlyGraphs:
        enabledStr: "True"
      jsonQuery:
        enabledStr: "True"
      pythonCode:
        enabledStr: "True"
```

Key settings:
- `indexerVersion: hybrid` — Uses both semantic and fulltext search for indexing (recommended)
- `indicatorSelectionVersion: hybrid` — Uses both semantic and fulltext search for indicator selection at query time (recommended). Related to but distinct from `indexerVersion`
- `allowAutoUpdate` — When `true`, enables [auto-update](06-indexing-and-operations.md#auto-update) for datasets in this channel (default: `false`). Only useful when datasets use `version: "latest"` in their URN
- Each pipeline stage can use a different LLM model/temperature
- Attachments control what's shown to users (tables, CSV files, charts, query JSON, Python code). `enabledStr` uses a string (`"True"`/`"False"`) rather than a boolean to support `$env:{VAR_NAME}` environment variable references

### Dataset Structure Tool

Returns the full structure of a specific dataset — dimensions, attributes, types, sample values, and optionally provider
agencies:

```yaml
datasetStructure:
  type: DATASET_STRUCTURE
  name: Dataset_Structure
  description: >-
    Returns dimensions, attributes, types, and sample values for a dataset...
  details:
    includeProviderAgencies: true           # Include list of provider agencies in output
```

### Datasets Metadata Tool

Provides metadata about datasets and the channel. Used by external integrations:

```yaml
datasetsMetadata:
  type: DATASETS_METADATA
  name: Datasets_Metadata
  description: >-
    Provides metadata about datasets in the channel...
```

### Glossary Tools

Two tools for glossary access:

```yaml
availableTerms:
  type: AVAILABLE_TERMS
  name: Available_Terms
  description: >-
    Retrieve a comprehensive list of all terms currently available in the glossary...
  details:
    fakeCall:
      toolCallId: call_EBJJeaOMKeCzm8h378ubU003
      args: "{}"

termDefinitions:
  type: TERM_DEFINITIONS
  name: Term_Definitions
  description: >-
    Retrieve definitions for up to 10 requested terms...
  details:
    limit: 10
```

---

## Glossary Management

Each channel can have a glossary of term-definition pairs.

### Adding Terms via Admin UI

1. Select **Glossary** from the channel context menu
2. Click **Add Term**
3. Fill in:
   - **Term** — The term or phrase (e.g., "GDP")
   - **Definition** — Official definition
   - **Source** — Reference URL or document (e.g., "IMF", "World Bank")
   - **Domain** — Context area (e.g., "economics", "statistics")
4. Save

You can also edit and delete existing terms from the same page.

### Best Practices

- Include key statistical terms users are likely to ask about
- Use official definitions from the data provider when available
- Cover terms that appear in dataset indicator names (GDP, CPI, BOP, etc.)
- Keep definitions concise but complete

---

## Key Takeaways

- Data Sources define connections to SDMX providers — each provider needs its own Data Source
- Channels are user-facing deployments with agent, datasets, tools, and glossary
- The Supreme Agent configuration controls the LLM model, domain, and behavior instructions
- Named Entity types must cover all NON_INDICATOR dimensions across the channel's datasets — `countryNamedEntityType` must match the country dimension's `alias` in datasets
- Tools are configured per channel — Data Query, Available Datasets, Dataset Structure, and Glossary are the main ones
- `allowAutoUpdate` on the Data Query tool enables automatic dataset updates — see [Module 06](06-indexing-and-operations.md#auto-update)
- `includeIndicatorCount` on Available Datasets helps validate indexing results
- The glossary provides consistent terminology definitions for the AI agent

---

## Check Your Understanding

Test your grasp of data source and channel configuration before moving on.

<details>
<summary><strong>1. You onboard a new dataset that has a <code>COUNTERPART_COUNTRY</code> dimension classified as NON_INDICATOR. The channel's current Named Entity types are: Time frequency, Currency/Unit of measure. What happens if you don't update the channel config?</strong></summary>

**Answer:** The NER step won't know to look for counterpart country entities in user queries. The dimension may still
work through defaults or LLM reasoning, but recognition will be unreliable. Fix: add `"Counterpart area/country"` to
`namedEntityTypes` in the channel configuration.

</details>

<details>
<summary><strong>2. Your datasets use <code>alias: "Country/Reference area"</code> on the country dimension, but the channel has <code>countryNamedEntityType: "Country"</code>. What breaks?</strong></summary>

**Answer:** Country recognition fails — the system can't match the country Named Entity type to the dimension alias.
`countryNamedEntityType` and the country dimension's `alias` must be identical strings. In this case, set
`countryNamedEntityType: "Country/Reference area"` to match the dataset.

</details>

<details>
<summary><strong>3. You want to enable auto-update for a channel. Where in the YAML does <code>allowAutoUpdate</code> go?</strong></summary>

**Answer:** On the Data Query tool details: `dataQuery.details.allowAutoUpdate: true`. It's a channel-level setting on
the tool, not a per-dataset setting. This enables [auto-update](06-indexing-and-operations.md#auto-update) for all
datasets in the channel that use `version: "latest"` in their URN.

</details>

<details>
<summary><strong>4. You want to block queries about organizational governance while keeping the general topic filter active. Which fields do you configure?</strong></summary>

**Answer:** Set `outOfScope.customBlacklist` with a description like `"Questions about how organizations operate,
internal governance, and administrative processes..."`, and keep `outOfScope.useGeneralTopicsBlacklist: true` (the
default). Optionally configure a separate `outOfScope.llmModelConfig` for the scope filter.

</details>

<details>
<summary><strong>5. After onboarding, you want to verify indexing results from the chat interface. Which tool and field do you configure?</strong></summary>

**Answer:** Enable `includeIndicatorCount: true` on the Available Datasets tool details
(`availableDatasets.details.includeIndicatorCount: true`). After triggering Available Datasets in chat, it will show
per-dataset indicator counts — letting you verify that the expected number of indicators were indexed.

</details>

---

**Previous:** [Module 04 — Configuring a Dataset](04-dataset-configuration.md) | **Next:** [Module 06 — Indexing, Deduplication & Operations](06-indexing-and-operations.md)
