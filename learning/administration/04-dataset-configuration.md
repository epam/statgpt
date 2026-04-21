# Module 04: Configuring a Dataset

## What You'll Learn

- The Admin UI workflow for adding a dataset
- The complete dataset configuration YAML — field by field
- How to fill each field with correct values
- Annotated examples: IMF WEO, IMF BOP, Eurostat NAMA_10_GDP
- Virtual dimensions for single-country datasets
- Common mistakes and how to avoid them

---

> **Prerequisite:** This module assumes a Data Source already exists. To set up a new Data Source, see [Module 05 — Data Sources](05-data-sources-and-channels.md).

## Admin UI Workflow

Adding a dataset in the StatGPT Admin UI follows a wizard:

1. **Navigate** to the "Datasets" tab and click "Add"
2. **Select the Data Source** from the table (e.g., the IMF SDMX 2.1 data source) and click "Next"
3. **Select the Dataflow** from the list of available dataflows in that data source — this selects the URN
4. **Fill in the configuration YAML** and save

The URN is selected in step 3 (you don't type it manually), but it appears in the configuration YAML for reference. The rest of the configuration is what you need to reason about and fill in.

---

## Configuration YAML — Field by Field

Below is the complete set of fields you'll fill in the Admin UI YAML editor. We'll walk through each one.

### `urn` — Dataset Identifier

The SDMX URN of the dataflow. This is pre-filled from your selection in the wizard.

```yaml
urn:
  agency_id: "IMF.RES"
  resource_id: "WEO"
  version: "latest"
```

Format: an object with `agency_id`, `resource_id`, and `version` fields.

The `version` field defaults to `"latest"`, which tells StatGPT to always track the current published version of the
dataflow. The system resolves `"latest"` to a concrete version (e.g., `"9.0.0"`) at indexing time and stores it
internally. Pinned versions like `"9.0.0"` are supported but not recommended — they require manual updates when the
provider releases a new version. Using `"latest"` also enables
[auto-update](06-indexing-and-operations.md#auto-update) to automatically detect upstream changes.

### `citation` — Data Source Attribution

Tells users where the data comes from:

```yaml
citation:
  provider: IMF.RES                                       # Data provider name or ID
  url: https://data.imf.org/en/datasets/IMF.RES:WEO      # Link to the dataset's web page
  description: &weo_description >                          # Description of the dataset
    The World Economic Outlook (WEO) database contains selected macroeconomic
    data series from the statistical appendix of the World Economic Outlook
    report...
```

**`description` field decision:**

```
Source dataflow has a meaningful description?
├── Yes → set `citation.description: null` (this will fetch the description from the source on each access)
│         `indexer.description`: do not set to `null`, copy the source description verbatim
└── No / Missing / Vague →
          Write a custom description
          citation.description: &anchor > "Your description..."
          indexer.description: *anchor (reuse via YAML anchor)
```

**Key rules:**
- Citation and indexer description decisions are **independent** — citation controls user-facing attribution, indexer controls what gets searched
- Both paths must result in a **non-empty `indexer.description`**
- When `citation.description: null`, do NOT use a YAML anchor pointing to the null citation description
  (the anchor resolves to `null`, making indexer description empty)
- When you write a custom citation description, use a YAML anchor (e.g., `&weo_description`) so you can reuse the same text in `indexer.description`

> **Multi-agency datasets:** For datasets that aggregate data from multiple providers, `citation` supports additional
> fields: `providerTemplate` (a template string with `{n_agencies}` and `{agencies_sample}` placeholders) and
> `providerAgencies` (a list of `{id, count, name}` objects). These are advanced — most single-agency datasets only
> need `provider`, `url`, and `description`.

### `isOfficial`

```yaml
isOfficial: false
```

Set to `true` for official national-level data sources (e.g., a national statistics office). Official datasets are prioritized in answers for country-specific queries. Most international organization datasets (IMF, World Bank, Eurostat) are `false`.

### `useTitleFromSrc`

```yaml
useTitleFromSrc: true
```

- `true` — Use the dataflow title from the SDMX source metadata
- `false` — Use a custom title (you provide it when creating the dataset in the UI)

Set to `true` when the source dataflow has a good, descriptive title. Set to `false` when you need to override with something clearer.

### `dimensions` — Unified Dimension Configuration

The `dimensions` field is a map where each key is a dimension ID and each value configures that dimension's type and behavior. This is where you declare which dimensions are indicators, which is the country dimension, which is the time dimension, etc.

```yaml
dimensions:
  INDICATOR:
    dimensionType: "INDICATOR"
    isRequired: true
  COUNTRY:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
  FREQUENCY:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
  TIME_PERIOD:
    dimensionType: "TIME_PERIOD"
    defaultQueries:
      - values: ["-5y", "+2y"]
        operator: "between"
```

#### Per-Dimension Fields

| Field | Description |
|-------|-------------|
| `dimensionType` | **Required.** One of: `"INDICATOR"`, `"NON_INDICATOR"`, `"TIME_PERIOD"`, `"SPECIAL"`. See [Module 03a](03a-dimension-types.md). |
| `isRequired` | For INDICATOR dimensions only. Set to `true` if the user's query must filter on this dimension. At least one INDICATOR dimension must be required. |
| `subtype` | For NON_INDICATOR dimensions. `"REGION"` for the country/region dimension, `"FREQUENCY"` for the frequency dimension. |
| `alias` | For the country dimension (`subtype: "REGION"`). A human-readable alias that unifies country dimension names across datasets in a channel (e.g., `"Country/Reference area"`). |
| `allValues` | For the country dimension. A synthetic value representing "all countries" for star-queries. Object with `id`, `name`, and `description`. |
| `defaultQueries` | Default query filters applied when the user doesn't specify a value. Can be set on any dimension. Array of objects with `values` and `operator`. |
| `processorId` | For SPECIAL dimensions only. References a processor configured by the system administrator at the channel/tool level (e.g., `"KVED"` for NACE/ISIC/KVED hierarchies). |
| `virtual` | For virtual dimensions (see [Virtual Dimensions](#virtual-dimensions)). Object with `name`, `description`, and `value` (containing `id`, `name`, `description`). |

#### `dimensionType` Values

| Value | Usage |
|-------|-------|
| `"INDICATOR"` | Dimensions describing what is being measured. Values are indexed for search. |
| `"NON_INDICATOR"` | General, universally understood dimensions (country, frequency, currency). Matched via NER. |
| `"TIME_PERIOD"` | The temporal dimension. Exactly one per dataset. |
| `"SPECIAL"` | Dimensions with large hierarchical code lists (NACE, ISIC, KVED) that need a specialized processor. Must also have `processorId`. |

#### `defaultQueries` Operators

| Operator | Use Case | Example |
|----------|----------|---------|
| `between` | Continuous range (typically TIME_PERIOD) | `values: ["2020", "2025"]` |
| `in` | Non-contiguous value list | `values: ["A", "Q"]` |
| `equals` | Single default value | `values: ["A"]` |

**Common patterns:**
- **TIME_PERIOD range:** `values: ["2020", "2025"], operator: between` — last ~5 years
- **TIME_PERIOD with forecasts** (e.g., WEO): include future years in the range
- **Relative expressions:** `values: ["-5y", "now"]` — dynamic range
- **Frequency filter:** `values: ["A", "Q"], operator: in` — restrict to annual and quarterly by default
- **Single value:** `values: ["A"], operator: equals` — default to annual frequency

#### Special Dimensions — Large Hierarchical Classifications

Some indicator dimensions use very large hierarchical code lists (hundreds or thousands of items) — for example, NACE economic activity codes, ISIC industry codes, or KVED codes. Standard search indexing can't handle these effectively. Setting `dimensionType: "SPECIAL"` with a `processorId` configures a specialized LLM-powered processor to navigate these hierarchies.

```yaml
dimensions:
  NACE:
    dimensionType: "SPECIAL"
    processorId: "KVED"
```

**When to use:** When a dimension uses an industry/activity classification system like NACE, ISIC, or KVED with a deep hierarchy.

**Important notes:**
- The `processorId` must reference a processor that exists in the channel's tool configuration. If it doesn't match, special dimension search fails silently. Verify with your system administrator.
- Most datasets don't need SPECIAL dimensions — omit them entirely if no dimensions have large hierarchical code lists.

See [Module 03a — Special Dimensions](03a-dimension-types.md#special-dimensions) for the conceptual explanation.

### `includeAttributes` — SDMX Attributes in Agent Context

Lists SDMX attributes to include alongside data when presenting results to the AI agent:

```yaml
includeAttributes:
  - SCALE       # e.g., "Millions", "Billions"
  - UNIT        # e.g., "US Dollars", "Percent"
  - PUBLISHER   # Publishing organization
  - SOURCE      # Data source reference
```

These give the agent context about the data values (units, scale, source) so it can describe results accurately. Set to `null` if no relevant attributes exist.

### `pinnedColumns` — Column Display Order

Defines which columns appear in the data table and their order, from **least important to most important** (left to right):

```yaml
pinnedColumns:
  - FREQUENCY_Name
  - COUNTRY_Name
  - INDICATOR_Name
```

**Rules:**
- List ALL dataset dimensions except TIME_PERIOD
- Append `_Name` to each dimension ID (e.g., `INDICATOR` → `INDICATOR_Name`)
- Case must match the actual dimension ID (e.g., `freq_Name` for Eurostat, `FREQUENCY_Name` for IMF)
- Order from least to most important — the main indicator dimension typically goes last

### `updatedAt` — Last Updated Timestamp

Optional. Configures how to determine when the dataset was last updated. Supports multiple sources checked in order:

```yaml
updatedAt:
  - source: "attribute"
    field: "UPDATED"
    formats: ["%d.%m.%Y", "%Y-%m-%d"]
  - source: "annotation"
    field: "lastUpdatedAt"
```

| Field | Description |
|-------|-------------|
| `source` | Where to look: `"annotation"` (SDMX annotation), `"attribute"` (SDMX attribute), or `"citation"` (citation metadata) |
| `field` | The annotation ID, attribute ID, or citation field to read |
| `formats` | Optional. Date format strings for parsing (Python `strftime` format) |

Multiple entries are checked in order — the first one that returns a value is used.

### `indexer` — Search Index Configuration

Controls how the dataset is indexed for semantic and keyword search:

```yaml
indexer:
  indicator:
    unpack: true                   # true for packed indicators, false for unpacked
  description: *weo_description    # Dataset description for indexing (must be non-empty)
```

| Field | Description |
|-------|-------------|
| `indicator.unpack` | `true` for packed indicators (comma-separated multi-concept values like "GDP, current prices, USD"). `false` for unpacked. See [Module 03b](03b-indicator-configuration.md#packed-vs-unpacked-indicators). |
| `indicator.superPrimary` | Advanced. Default `false`. When `true` (only applies when `unpack: false`), the primary indicator label is concatenated from the first 3 indicator dimensions instead of just the first one. |
| `indicator.annotations` | Advanced. Optional object with a `description` field specifying an SDMX annotation name to use as the indicator description in the index. |
| `description` | **Must be a non-empty string.** If citation description is `null`, copy the dataflow description from the source metadata here. If you wrote a custom citation description, reference it with a YAML anchor (`*weo_description`). |

> **Indexing-relevant vs. display-only fields:** Some fields affect the search index and require reindexing when
> changed: `dimensionType`, `alias`, `virtual`, `processorId`, `subtype`, and all `indexer.*` fields. Others are
> display-only and can be changed without reindexing: `isRequired`, `defaultQueries`, `allValues`, `isOfficial`,
> `citation`, `pinnedColumns`, `includeAttributes`. The system detects this automatically — see
> [Module 06](06-indexing-and-operations.md#when-to-reindex).

---

## Complete Annotated Example: IMF WEO

```yaml
urn:
  agency_id: "IMF.RES"
  resource_id: "WEO"
  version: "latest"                    # Always track the current published version
citation:
  url: https://data.imf.org/en/datasets/IMF.RES:WEO
  provider: IMF.RES
  description: &weo_description >
    The World Economic Outlook (WEO) database contains selected macroeconomic
    data series from the statistical appendix of the World Economic Outlook
    report, which presents the IMF staff's analysis and projections of economic
    developments at the global level, in major country groups and in many
    individual countries. The WEO is released in April and September/October
    each year. Use this database to find data on national accounts, gross
    domestic product (GDP), inflation, unemployment rates, balance of payments,
    fiscal indicators, trade for countries and country groups (aggregates), and
    commodity prices whose data are reported by the IMF. Data are available from
    1980 to the present, and projections are given for the next two years.
    Additionally, medium-term projections are available for selected indicators.
    For some countries, data are incomplete or unavailable for certain years.
isOfficial: false                      # IMF is international, not a national agency
useTitleFromSrc: true                  # Source dataflow title is good
updatedAt:                             # How to determine when data was last updated
  - source: "attribute"
    field: "UPDATE_DATE"
    formats: ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]
  - source: "annotation"
    field: "lastUpdatedAt"
  - source: "citation"
    field: "last_updated"
dimensions:
  INDICATOR:
    dimensionType: "INDICATOR"
    isRequired: true                   # Required — queries need an indicator
  COUNTRY:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
    allValues:
      id: "ALL_COUNTRIES"
      name: "All countries - must be selected when query explicitly asks for all countries"
      description: "Special value to query all countries"
  FREQUENCY:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
  TIME_PERIOD:
    dimensionType: "TIME_PERIOD"
    defaultQueries:
      - values: ["-5y", "+2y"]
        operator: "between"
includeAttributes:
  - SCALE
  - UNIT
  - PUBLISHER
  - SOURCE
pinnedColumns:
  - FREQUENCY_Name                     # Least important (usually "Annual")
  - COUNTRY_Name                       # Country context
  - INDICATOR_Name                     # Most important — what's being measured
indexer:
  indicator:
    unpack: true                       # Packed indicators: "GDP, current prices, Percent change"
  description: *weo_description        # Reuse citation description via YAML anchor
```

**Key decisions:**
- `version: "latest"` — always tracks the current published WEO version
- `unpack: true` — WEO indicator values pack multiple concepts into one string
- Single indicator dimension, marked as required
- `isOfficial: false` — IMF is an international organization
- Description uses a YAML anchor so it can be shared between `citation` and `indexer`
- `allValues` on COUNTRY enables star-queries like "global GDP"
- `updatedAt` checks three sources in order for the last-updated date

---

## Second Example: IMF BOP (Multiple Indicator Dimensions)

```yaml
urn:
  agency_id: "IMF.STA"
  resource_id: "BOP"
  version: "latest"                    # Always track the current published version
citation:
  url: https://data.imf.org/en/datasets/IMF.STA:BOP
  provider: IMF.STA
  description: &bop_description >
    The Balance of Payments (BOP) is a statistical statement that summarizes
    transactions between residents and nonresidents during a period. It consists
    of the goods and services account, the primary income account, the secondary
    income account, the capital account, and the financial account.
isOfficial: false
useTitleFromSrc: true
updatedAt:
  - source: "attribute"
    field: "UPDATE_DATE"
    formats: ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]
  - source: "annotation"
    field: "lastUpdatedAt"
  - source: "citation"
    field: "last_updated"
dimensions:
  INDICATOR:
    dimensionType: "INDICATOR"
    isRequired: true                   # Main indicator — required
  BOP_ACCOUNTING_ENTRY:
    dimensionType: "INDICATOR"
    isRequired: true                   # Credit vs. Debit — also required
  COUNTRY:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
    allValues:
      id: "ALL_COUNTRIES"
      name: "All countries - must be selected when query explicitly asks for all countries"
      description: "Special value to query all countries"
  FREQUENCY:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
  TIME_PERIOD:
    dimensionType: "TIME_PERIOD"
    defaultQueries:
      - values: ["-5y", "now"]
        operator: "between"
  UNIT:
    dimensionType: "NON_INDICATOR"     # Values like "US Dollars" are universally understood
includeAttributes:
  - SCALE
  - UNIT
  - PUBLISHER
  - SOURCE
pinnedColumns:
  - FREQUENCY_Name
  - COUNTRY_Name
  - BOP_ACCOUNTING_ENTRY_Name
  - INDICATOR_Name                     # Main indicator last (most important)
indexer:
  indicator:
    unpack: true
  description: *bop_description
```

**Key differences from WEO:**
- Two required indicator dimensions — both INDICATOR and BOP_ACCOUNTING_ENTRY are essential
- UNIT is explicitly `dimensionType: "NON_INDICATOR"` — its values (currencies, percentages) are universally understood
- No forecast data, so default time range ends at `"now"` instead of future years

---

## Third Example: Eurostat NAMA_10_GDP (Different Agency)

```yaml
urn:
  agency_id: "ESTAT"
  resource_id: "NAMA_10_GDP"
  version: "latest"                    # Always track the current published version
citation:
  provider: Eurostat (ESTAT)
  url: https://ec.europa.eu/eurostat/cache/metadata/en/nama10_esms.htm
  description: null                    # Source metadata has a meaningful description
isOfficial: false
useTitleFromSrc: false                 # Custom title: "GDP and main components"
dimensions:
  na_item:
    dimensionType: "INDICATOR"
    isRequired: true                   # National accounts item — main indicator, required
  unit:
    dimensionType: "INDICATOR"         # Measurement methodology — domain-specific
  geo:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
  freq:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
  TIME_PERIOD:
    dimensionType: "TIME_PERIOD"
    defaultQueries:
      - values: ["2014-01-01", "2024-12-31"]
        operator: "between"
includeAttributes: null                # No relevant attributes
pinnedColumns:
  - freq_Name                          # Lowercase to match dimension IDs
  - geo_Name
  - na_item_Name
  - unit_Name
indexer:
  indicator:
    unpack: false                      # Unpacked: each value is a single concept
  description: >                       # Custom indexer description (since citation desc is null)
    National accounts indicator (ESA 2010) - a coherent and consistent set of
    macroeconomic indicators, which provide an overall picture of the economic
    situation and are widely used for economic analysis and forecasting, policy
    design and policy making
```

**Key contrasts with IMF datasets:**
- **Lowercase dimension IDs** (`na_item`, `unit`, `geo`, `freq`) — Eurostat convention
- **`unit` is INDICATOR** with `dimensionType: "INDICATOR"` — its values describe measurement methodology (e.g., "Chain linked volumes"), not simple currencies
- **`citation.description: null`** — the source metadata is good, so StatGPT fetches it directly. But `indexer.description` must still be non-empty, so a custom description is provided there
- **`unpack: false`** — each indicator value is a single concept
- **`useTitleFromSrc: false`** — a custom title is used for clarity
- **Fixed date range** in default queries instead of relative expressions
- **`pinnedColumns`** use lowercase to match actual dimension IDs

---

## Virtual Dimensions

Some datasets only cover a single country and have no country dimension in their SDMX structure. A **virtual dimension** adds a synthetic dimension with a fixed value, making the dataset discoverable for country-based queries.

In the `dimensions` map, configure the virtual dimension inline using the `virtual` field:

```yaml
dimensions:
  COUNTRY:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
    virtual:
      name: "Country"
      description: "Country"
      value:
        id: "USA"
        name: "United States"
        description: "United States"
  FREQUENCY:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
  # ... other dimensions ...
```

| Virtual Field | Description |
|---------------|-------------|
| `name` | Display name for the virtual dimension |
| `description` | Description of the virtual dimension |
| `value.id` | The fixed code value (e.g., `"USA"`) |
| `value.name` | Human-readable name for the fixed value |
| `value.description` | Description of the fixed value |

**Example: FRB FOR (US Federal Reserve — Household Debt Service Ratios)**

This dataset only contains US data. Without a virtual COUNTRY dimension with a fixed value of "USA", a query like *"What is the household debt service ratio for the US?"* wouldn't match this dataset — there's no country dimension to match against.

The virtual dimension is configured directly in the `dimensions` map alongside all other dimension settings.

---

## Common Mistakes and How to Avoid Them

| Mistake | Impact | Prevention |
|---------|--------|-----------|
| Wrong `unpack` setting | Search misses relevant indicators or returns noise | Check code list values for comma-separated multi-concept strings (see [Module 03b](03b-indicator-configuration.md#packed-vs-unpacked-indicators)) |
| All indicator dimensions marked `isRequired: true` | Queries get rejected unnecessarily | Only mark dimensions as required if omitting them makes queries meaningless |
| No required indicator dimensions | Validation fails | At least one INDICATOR dimension must have `isRequired: true` |
| Wrong pinned column order | Data table is hard to read | Order from least to most important; main indicator should be last |
| Incorrect `_Name` suffix casing in pinnedColumns | Column not shown in output | Match exact dimension ID + `_Name` (case-sensitive: `freq_Name` not `FREQ_Name`) |
| Empty `indexer.description` | Indexing fails | Must be a non-empty string — copy from source or write custom |
| `citation.description: null` but also `indexer.description` referencing it | Empty indexer description | When citation is null, write the indexer description independently |
| Missing `dimensionType` on a dimension | Dimension not processed correctly | Every dimension in the `dimensions` map must have a `dimensionType` |
| Forgetting a dimension | Queries miss relevant data or fail | Ensure all dimensions from the DSD are accounted for in the `dimensions` map |
| Country dimension `alias` doesn't match channel's `countryNamedEntityType` | Country recognition fails | Use the same string as the channel's country named entity type |
| `processorId` on SPECIAL dimension doesn't match channel config | Special dimension search fails silently — no error, just no results | Verify the `processorId` exists in the channel's tool configuration before saving |
---

## Key Takeaways

- Dataset configuration is entered as a single YAML in the Admin UI per dataset
- The URN is selected from a table; everything else you fill in manually
- The `dimensions` map is the core of the config — each dimension gets a `dimensionType` and optional settings like `isRequired`, `subtype`, `alias`, `defaultQueries`
- Key decisions per dataset: which dimensions are INDICATOR, which are required, packed vs. unpacked, description source
- Use the `citation.description` / `indexer.description` anchor pattern to avoid duplicating text
- Different agencies use different naming conventions — `alias` on the country dimension and consistent values unify them
- Virtual dimensions enable single-country datasets to participate in country-based queries — configured inline via the `virtual` field
- Always validate: at least one required indicator dimension (`isRequired: true`), non-empty indexer description, correct column casing
- SPECIAL dimensions enable LLM-powered search for large hierarchical classifications (NACE, ISIC, KVED) — set `dimensionType: "SPECIAL"` with `processorId`
- Default queries (`defaultQueries`) are set directly on each dimension, not in a separate top-level field

---

## Check Your Understanding

**1. A dataset's source metadata has a meaningful description. What do you set for `citation.description` and `indexer.description`?**

<details>
<summary>Answer</summary>

`citation.description: null` — StatGPT fetches it from the source on each access. `indexer.description:` copy the source description text verbatim (write it independently, don't use a YAML anchor pointing to the null citation).
</details>

**2. You configure `pinnedColumns` as `["INDICATOR_Name", "COUNTRY_Name", "FREQUENCY_Name"]`. What's wrong?**

<details>
<summary>Answer</summary>

Order is least→most important (left to right), with the main indicator last. Should be `["FREQUENCY_Name", "COUNTRY_Name", "INDICATOR_Name"]` — frequency is least important, the main indicator goes last as the most important column.
</details>

**3. A dataset has a single indicator dimension with values like "Exports of goods and services, Percent of GDP". What `unpack` setting do you use?**

<details>
<summary>Answer</summary>

`unpack: true` — the values are comma-separated multi-concept strings packing what is measured ("Exports of goods and services") with a unit ("Percent of GDP").
</details>

**4. You set `citation.description: null` and `indexer.description: *some_anchor`. What happens?**

<details>
<summary>Answer</summary>

The YAML anchor resolves to `null`, making `indexer.description` empty. Indexing will fail because `indexer.description` must be a non-empty string. When citation is null, write the indexer description independently — don't use an anchor pointing to the null value.
</details>

**5. A Eurostat dataset has dimensions `geo`, `freq`, `na_item`, `unit`, `TIME_PERIOD`. You write `pinnedColumns: ["FREQ_Name", "GEO_Name", "NA_ITEM_Name", "UNIT_Name"]`. What's wrong?**

<details>
<summary>Answer</summary>

Case mismatch. Eurostat uses lowercase dimension IDs, so the `_Name` suffix must follow the exact casing: `freq_Name`, `geo_Name`, `na_item_Name`, `unit_Name`. Using uppercase (`FREQ_Name`, `GEO_Name`) won't match the actual dimension IDs, and those columns won't appear in the output.
</details>

**6. An FRB dataset only covers the US and has no country dimension in its SDMX structure. A user asks "What is the household debt ratio for the US?" and gets no results. What's missing?**

<details>
<summary>Answer</summary>

A virtual country dimension. In the `dimensions` map, add a COUNTRY dimension with `dimensionType: "NON_INDICATOR"`, `subtype: "REGION"`, and a `virtual` field specifying a fixed value of "USA":

```yaml
COUNTRY:
  dimensionType: "NON_INDICATOR"
  subtype: "REGION"
  alias: "Country/Reference area"
  virtual:
    name: "Country"
    description: "Country"
    value:
      id: "USA"
      name: "United States"
      description: "United States"
```

Without this, there's no country dimension to match "US" against, so the dataset is invisible to country-based queries.
</details>

---

## Practical Exercises

### Exercise 1: Configure an OECD Employment Dataset from Scratch

You're onboarding a new dataset. The Admin UI wizard shows:

**Dataflow:** `OECD:EMP(1.0.0)` — Employment by economic activity

**Dimensions:**

| Dimension ID | Concept Name | Sample Codelist Values |
|---|---|---|
| `MEASURE` | Measure | "Employment", "Unemployment rate", "Labour force participation rate" |
| `ACTIVITY` | Economic activity | "Agriculture, forestry and fishing", "Manufacturing", "Services", "Total" |
| `REF_AREA` | Reference area | "USA", "DEU", "JPN", "FRA", ... |
| `FREQ` | Frequency | "A", "Q" |
| `TIME_PERIOD` | Time period | "2015", "2020", "2023-Q1" |

**Additional info:**
- Source description is meaningful: "Employment indicators by economic activity, covering employment levels, unemployment rates, and labour force participation across OECD countries"
- Provider attributes available: `UNIT_MEASURE`, `DECIMALS`

**Your task:** Write the complete dataset configuration YAML.

<details>
<summary><strong>Solution</strong></summary>

**Dimension classification:**
- `MEASURE` → INDICATOR (required) — describes what is being measured
- `ACTIVITY` → INDICATOR (optional) — economic activity classifications require domain knowledge ("Agriculture, forestry and fishing" is a classification, not a universally understood concept). Optional because queries like "What is the unemployment rate?" are still meaningful without specifying an activity
- `REF_AREA` → NON_INDICATOR (country, `subtype: "REGION"`)
- `FREQ` → NON_INDICATOR (`subtype: "FREQUENCY"`)
- `TIME_PERIOD` → TIME_PERIOD

**Packed/Unpacked:** `unpack: false` — each value is a single concept ("Employment", "Manufacturing"). No comma-separated multi-concept strings.

**Citation description:** `null` — the source description is meaningful, so StatGPT fetches it directly.

**Indexer description:** Copy the source description independently (can't anchor to null citation).

```yaml
urn:
  agency_id: "OECD"
  resource_id: "EMP"
  version: "latest"
citation:
  provider: OECD
  url: https://data-explorer.oecd.org/
  description: null                        # Source has a meaningful description
isOfficial: false                          # OECD is international, not a national agency
useTitleFromSrc: true                      # Source title is descriptive
dimensions:
  MEASURE:
    dimensionType: "INDICATOR"
    isRequired: true                       # Required — "unemployment rate" vs. "employment" matters
  ACTIVITY:
    dimensionType: "INDICATOR"             # Economic activity — domain-specific classification
                                           # Not required — queries work without specifying an activity
  REF_AREA:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
  FREQ:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
  TIME_PERIOD:
    dimensionType: "TIME_PERIOD"
    defaultQueries:
      - values: ["2018", "2025"]
        operator: "between"
includeAttributes:
  - UNIT_MEASURE
pinnedColumns:
  - FREQ_Name                              # Least important
  - REF_AREA_Name                          # Country context
  - ACTIVITY_Name                          # Economic activity
  - MEASURE_Name                           # Most important — what's being measured
indexer:
  indicator:
    unpack: false                          # Single-concept values
  description: >                           # Independent copy (citation is null)
    Employment indicators by economic activity, covering employment levels,
    unemployment rates, and labour force participation across OECD countries
```

**Key decisions explained:**
- `ACTIVITY` is INDICATOR, not NON_INDICATOR — "Agriculture, forestry and fishing" is a classification code, not a universally understood concept like a country name
- `ACTIVITY` is optional (no `isRequired: true`) — a query for "unemployment rate in Germany" is meaningful even without specifying an activity sector
- `DECIMALS` omitted from `includeAttributes` — decimal precision is metadata for display, not useful context for the AI agent
- `indexer.description` written independently since `citation.description` is null

</details>

### Exercise 2: Diagnose a Broken CPI Configuration

A colleague configured a Eurostat CPI dataset but users report problems. Find and fix all errors:

```yaml
urn:
  agency_id: "ESTAT"
  resource_id: "PRC_HICP_MIDX"
  version: "latest"
citation:
  provider: Eurostat (ESTAT)
  url: https://ec.europa.eu/eurostat/cache/metadata/en/prc_hicp_esms.htm
  description: null
isOfficial: false
useTitleFromSrc: true
dimensions:
  coicop:
    dimensionType: "INDICATOR"
    isRequired: true
  unit:
    dimensionType: "INDICATOR"
    isRequired: true
  index_type:
    isRequired: true                       # Missing dimensionType!
  geo:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
  TIME_PERIOD:
    dimensionType: "TIME_PERIOD"
    defaultQueries:
      - values: ["2019-01-01", "2024-12-31"]
        operator: "between"
includeAttributes: null
pinnedColumns:
  - FREQ_Name
  - GEO_Name
  - COICOP_Name
  - UNIT_Name
indexer:
  indicator:
    unpack: false
  description: *cpi_desc
```

**Your task:** Find all configuration errors, explain their impact, and provide the fix.

<details>
<summary><strong>Solution</strong></summary>

**Error 1: `index_type` is missing `dimensionType`**

The `index_type` dimension has `isRequired: true` but no `dimensionType` field. Every dimension in the `dimensions` map must have a `dimensionType`. Since index type values (CPI vs. HICP) are domain-specific, it should be `"INDICATOR"`.

Fix:
```yaml
  index_type:
    dimensionType: "INDICATOR"
    isRequired: true
```

**Error 2: Missing `freq` dimension**

The `pinnedColumns` reference `FREQ_Name`, but there's no `freq` dimension in the `dimensions` map. Eurostat datasets have a frequency dimension that needs to be configured.

Fix — add to the `dimensions` map:
```yaml
  freq:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
```

**Error 3: `pinnedColumns` use wrong casing**

Eurostat uses lowercase dimension IDs (`geo`, `freq`, `coicop`, `unit`), but `pinnedColumns` uses uppercase (`FREQ_Name`, `GEO_Name`, `COICOP_Name`, `UNIT_Name`). Column names are case-sensitive — these won't match.

Fix:
```yaml
pinnedColumns:
  - freq_Name
  - geo_Name
  - coicop_Name
  - unit_Name
  - index_type_Name
```
(Also add `index_type_Name` since it's an indicator dimension.)

**Error 4: `indexer.description: *cpi_desc` resolves to `null`**

`citation.description` is `null`, and `*cpi_desc` is presumably a YAML anchor pointing to it. The anchor resolves to `null`, making `indexer.description` empty. Indexing will fail.

Fix: Write the indexer description independently:
```yaml
indexer:
  description: >
    Harmonised Index of Consumer Prices (HICP) - monthly data providing
    comparable measures of inflation across EU member states
```

</details>

---

**Previous:** [Module 03b — Indicator Configuration](03b-indicator-configuration.md) | **Next:** [Module 05 — Data Sources & Channel Configuration](05-data-sources-and-channels.md)
