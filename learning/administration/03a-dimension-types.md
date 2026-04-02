# Module 03a: Dimension Types & Named Entities

> **This is a key module.** Dimension type classification is the most common source of configuration errors. Take time
> to understand the decision framework before configuring datasets.

## What You'll Learn

- The three dimension categories: INDICATOR, NON_INDICATOR, and TIME_PERIOD
- A decision framework for classifying dimensions (the part admins struggle with most)
- How dimension types map to dataset configuration fields in the Admin UI
- What Named Entity types are and how they relate to NON_INDICATOR dimensions
- How to handle special dimensions with large hierarchical code lists
- Concrete examples from IMF, Eurostat, ECB, BIS, and other agencies

---

## The Three Dimension Categories

Every dimension in a StatGPT dataset must be classified into one of three types:

### INDICATOR

Dimensions that describe **what is being measured** — the concept or metric.

Examples of indicator values:

- GDP, CPI, unemployment rate, population
- Balance of payments accounting entry (credit/debit)
- Price type (current prices, constant prices)
- Seasonal adjustment method
- Type of transformation (index, percent change)

**Key characteristic:** These are domain-specific concepts that typically require subject-matter knowledge to
understand.

> **Why it matters for search:** Values from INDICATOR dimensions are indexed in the search engine (embeddings +
> fulltext). When a user asks *"What was inflation?"*, the system searches the INDICATOR index to find matching concepts
> like "Consumer Price Index (CPI)". If a dimension is misclassified as NON_INDICATOR, its values won't be searchable —
> users looking for those concepts will get no results.

### NON_INDICATOR

Dimensions that describe **general, universally understood concepts** independent of the statistical domain.

Examples:

- Country / Reference area
- Frequency (annual, quarterly, monthly)
- Counterpart country
- Currency
- Unit of measure (in some contexts)

**Key characteristic:** An average person without domain expertise would understand what these concepts mean.

> **How StatGPT handles these:** NON_INDICATOR values are matched via Named Entity Recognition (NER), not search.
> The LLM extracts entities like "Germany" or "quarterly" directly from the user query and maps them to dimension
> values. This is why NON_INDICATOR dimensions must map to Named Entity types in the channel config — without that
> mapping, the system won't know to look for them.

### TIME_PERIOD

The temporal dimension. There is exactly one TIME_PERIOD dimension per dataset. It is typically configured explicitly
to set `defaultQueries` (default time ranges), though the system can identify it automatically from the SDMX structure.

---

## Consequences of Misclassification

Getting dimension types wrong has concrete, observable consequences:

| Misclassification             | What Goes Wrong                                                                                                                                                                                                               |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **INDICATOR → NON_INDICATOR** | Values not indexed for search. Users searching for those concepts get no results. The system tries NER instead, which is unreliable for domain-specific terms like "Chain linked volumes" or "Gross fixed capital formation". |
| **NON_INDICATOR → INDICATOR** | Values indexed unnecessarily, adding noise to search results. Named entities not recognized — "Germany" gets searched in the indicator index instead of being recognized as a country.                                        |

**Concrete example:** If you classify `COUNTRY` as INDICATOR in WEO, a query *"GDP of Germany"* searches for "Germany"
in the indicator index alongside "GDP". Germany won't match any indicator, causing the query to fail or return
unexpected results. Meanwhile, the NER step doesn't look for country entities in that dimension, so "Germany" is never
matched to the correct country code.

---

## How Dimension Types Map to the Admin UI Config

In the Admin UI, each dimension is configured explicitly with a `dimensionType` field in the `dimensions` map:

| Dimension Type              | How You Configure It                                                                        |
|-----------------------------|---------------------------------------------------------------------------------------------|
| **INDICATOR**               | `dimensionType: "INDICATOR"` on the dimension                                               |
| **INDICATOR (required)**    | Also set `isRequired: true` on the dimension                                                |
| **SPECIAL**                 | `dimensionType: "SPECIAL"` with `processorId` on the dimension                              |
| **NON_INDICATOR (country)** | `dimensionType: "NON_INDICATOR"` with `subtype: "REGION"` and `alias`                       |
| **NON_INDICATOR (frequency)** | `dimensionType: "NON_INDICATOR"` with `subtype: "FREQUENCY"`                              |
| **NON_INDICATOR (other)**   | `dimensionType: "NON_INDICATOR"` (no subtype needed)                                        |
| **TIME_PERIOD**             | `dimensionType: "TIME_PERIOD"` with optional `defaultQueries`                               |

**Example — IMF WEO:**

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

This tells StatGPT:

- `INDICATOR` is an indicator dimension (and it's required)
- `COUNTRY` is the country/region dimension (NON_INDICATOR with `subtype: "REGION"`)
- `FREQUENCY` is explicitly NON_INDICATOR with `subtype: "FREQUENCY"`
- `TIME_PERIOD` is the time dimension with a default range

---

## Decision Framework

This is where administrators struggle the most. For each dimension in the dataset, you typically have three pieces of
information to work with:

- **Dimension ID** — the technical identifier (e.g., `SECTOR`, `REF_AREA`, `COICOP_1999`)
- **Concept name** — the human-readable label (e.g., "Sector", "Reference area", "Classification of Individual
  Consumption by Purpose")
- **Codelist values** — the actual values the dimension can take (e.g., "Households", "Germany", "01 - Food and
  non-alcoholic beverages")

The dimension ID and concept name give you a starting hint, but **always check the codelist values** — they are the most
reliable input for classification. The same dimension name (e.g., `UNIT`) can require different classification depending
on what values it actually contains.

### The Core Question

> **"Would an average person understand this concept without domain knowledge?"**

- **Yes** → NON_INDICATOR (country, frequency, currency, counterpart area)
- **No** → INDICATOR (GDP component, price type, adjustment method, sector classification)

### Step-by-Step Checklist

For each dimension in the dataset:

1. **Is it the time dimension?**
    - If yes → `dimensionType: "TIME_PERIOD"`. Configure `defaultQueries` if needed. Done.

2. **Is it the country/region dimension?**
    - If yes → `dimensionType: "NON_INDICATOR"` with `subtype: "REGION"`. Add an `alias` if the dimension ID is not
      self-explanatory. Done.

3. **Is it a frequency dimension?**
    - If yes → `dimensionType: "NON_INDICATOR"` with `subtype: "FREQUENCY"`. Done.

4. **Check the Named Entity types for the channel.**
    - Does this dimension map to an existing Named Entity type (e.g., "Counterpart area/country", "Currency/Unit of
      measure")?
    - If yes → NON_INDICATOR. Done.

5. **Apply the core question — using all three inputs.**
    - Start with the concept name for a first impression, but **always check the codelist values**.
    - Would a non-expert understand what these codelist values represent?
    - If the values describe *what is being measured* or *how it's measured* → INDICATOR (`dimensionType: "INDICATOR"`)
    - If the values describe a general concept (age groups, gender, geographic regions) → NON_INDICATOR (`dimensionType: "NON_INDICATOR"`)

6. **When in doubt, lean toward INDICATOR.**
    - It's better to classify a borderline dimension as INDICATOR than NON_INDICATOR. Incorrect NON_INDICATOR
      classification can cause the system to misinterpret user queries.

### Grey Areas and How to Resolve Them

| Dimension ID             | Concept name                  | Codelist values (sample)                                                       | Classification | Reasoning                                                     |
|--------------------------|-------------------------------|--------------------------------------------------------------------------------|----------------|---------------------------------------------------------------|
| `UNIT`                   | Unit of measure (IMF BOP)     | `USD` — US Dollars, `PC_GDP` — Percent of GDP                                  | NON_INDICATOR  | Currency/unit concepts are universally understood             |
| `SECTOR`                 | Sector (IMF FSIC)             | `DT` — Core FSI: Deposit Takers, `OFC` — Additional FSI: Other Financial Corps | INDICATOR      | Financial sector classifications require domain knowledge     |
| `COUNTERPART_COUNTRY`    | Counterpart country (IMF DIP) | `US` — United States, `DE` — Germany, `JP` — Japan                             | NON_INDICATOR  | Countries are universally understood                          |
| `TYPE_OF_TRANSFORMATION` | Transformation (IMF CPI)      | `IX` — Index, `PC_CP_A_PT` — Percentage change, prev. year                     | INDICATOR      | Describes how the indicator is computed/presented             |
| `ADJUSTMENT`             | Adjustment (ECB BSI)          | `Y` — Working day and seasonally adjusted, `N` — Neither adjusted              | INDICATOR      | Statistical adjustment methods require expertise              |
| `ACCOUNTING_ENTRY`       | Accounting entry (BIS)        | `F` — Net flows, `S` — Stocks                                                  | NON_INDICATOR  | General accounting concepts; understandable without expertise |

### Common Mistakes

1. **Classifying UNIT as INDICATOR in all cases.** UNIT is often NON_INDICATOR — the key is whether the values are
   universally understood (USD, EUR, Percent → NON_INDICATOR) vs. domain-specific.

2. **Classifying sector/industry dimensions as NON_INDICATOR.** Dimensions like SECTOR, NACE, or COICOP describe
   domain-specific classifications and should generally be INDICATOR.

3. **Forgetting to check Named Entity types.** Before classifying any dimension as NON_INDICATOR, verify it maps to a
   Named Entity type in the channel config.

---

## Named Entity Types

### What Are Named Entity Types?

Named Entity types are categories of real-world entities that StatGPT can recognize in user queries. They are configured
per channel and used during the Named Entity Recognition step of query processing.

When a user asks *"What was GDP of Germany in 2023?"*, the system recognizes:

- "Germany" as a **Country/Reference area** entity
- "2023" as a time period

This recognition relies on the channel's Named Entity type configuration.

### How NER Works in Practice

During query processing, the LLM receives the list of Named Entity types configured for the channel. For each user
query, it extracts entities and categorizes them:

- User: *"quarterly GDP for Germany in euros"*
- NER extracts:
    - "Germany" → Country/Reference area
    - "quarterly" → Time frequency
    - "euros" → Currency/Unit of measure
- These extracted entities are then matched to specific code list values in each dataset

**If a Named Entity type is missing from the channel config**, the NER step won't know to look for those entities. The
dimension may still work through default queries or LLM reasoning, but recognition is less reliable and may fail for
unusual values.

### Standard Named Entity Types

Most channels use these standard types:

| Named Entity Type          | Description                                                               | Example Dimension IDs                             |
|----------------------------|---------------------------------------------------------------------------|---------------------------------------------------|
| `Country/Reference area`   | Countries and regions (configured as `countryNamedEntityType` in channel) | COUNTRY, REF_AREA, geo                            |
| `Time frequency`           | Data frequency (annual, quarterly, monthly)                               | FREQUENCY, FREQ, freq                             |
| `Counterpart area/country` | The "other" country in bilateral data                                     | COUNTERPART_COUNTRY, COUNTERPART_AREA, COUNT_AREA |
| `Currency/Unit of measure` | Currency and measurement units                                            | UNIT, CURRENCY_TRANS, UNIT_MEASURE                |

### How NON_INDICATOR Dimensions Map to Named Entity Types

Every NON_INDICATOR dimension (except country and frequency, which are handled specially) should map to a Named Entity
type in the channel configuration.

**Process:**

1. Classify a dimension as NON_INDICATOR
2. Check if an existing Named Entity type in the channel covers it
3. If not, **add a new Named Entity type** to the channel config

It's perfectly normal to add new Named Entity types when onboarding datasets with dimensions that don't fit existing
types.

### When to Add New Named Entity Types

If you classify a dimension as NON_INDICATOR but no existing Named Entity type matches it, add one. For example:

- The BIS Debt Securities dataset has `CONSOLIDATION` and `EXPENDITURE` as NON_INDICATOR dimensions
- If no existing Named Entity type covers these, you might add types like "Consolidation basis" or "Expenditure type"

**Example channel Named Entity types for an IMF-focused channel:**

```yaml
namedEntityTypes:
  - Time frequency
  - Counterpart area/country
  - Currency/Unit of measure
countryNamedEntityType: Country/Reference area
```

### The allValues Pattern

Some datasets support star-queries where users ask *"for all countries"* or *"global GDP"*. This is configured via
`allValues` on the country dimension — a synthetic value that represents "all countries" in the query:

```yaml
COUNTRY:
  dimensionType: "NON_INDICATOR"
  subtype: "REGION"
  alias: "Country/Reference area"
  allValues:
    id: "ALL_COUNTRIES"
    name: "All countries - must be selected when query explicitly asks for all countries"
    description: "Special value to query all countries"
```

When a user asks *"What is global GDP?"*, the system selects the `ALL_COUNTRIES` value instead of listing individual
countries. This is covered in detail in [Module 04](04-dataset-configuration.md) — mentioned here because it affects
how the country NON_INDICATOR dimension operates.

---

## Special Dimensions

### What Are Special Dimensions?

Some dimensions don't fit cleanly into the INDICATOR or NON_INDICATOR processing paths. **Special dimensions** are an
extensibility mechanism — they allow pluggable processors to handle edge cases without reworking the core dimension type
system.

Currently, one subtype of special dimension exists: **Large Hierarchical Code Lists (LHCL)**. The architecture is
designed so that new processor types can be added in the future to handle other edge cases, keeping the system agile
without requiring changes to the fundamental INDICATOR / NON_INDICATOR framework.

### The LHCL Use Case: Why NACE/ISIC/KVED Need Special Treatment

The primary use case today involves economic activity classification systems:

- **NACE** — the EU standard for classifying economic activities
- **ISIC** — the UN equivalent (International Standard Industrial Classification)
- **KVED** — Ukraine's national adaptation of NACE

These dimensions sit at an awkward intersection. The underlying concept — economic activity — isn't truly
domain-specific. A layperson understands "manufacturing" or "agriculture". But the *classifications themselves* create
problems for both standard processing paths:

- **Too large for standard indicator indexing.** These code lists contain hundreds to thousands of items (NACE Rev. 2
  has ~600+ codes across 4 levels). When indexed alongside regular indicators, semantically similar items crowd the
  embedding space — "Manufacture of food products", "Manufacture of beverages", "Manufacture of tobacco products" all
  cluster together, making it hard for vector search to pick the right one.
- **Too hierarchical for flat search.** Standard indicator search treats all values equally. But NACE codes have a
  parent-child structure (e.g., "C - Manufacturing" → "C10 - Manufacture of food products" → "C10.1 - Processing and
  preserving of meat"). The right level of specificity depends on the user's query, and flat search loses this
  structure.
- **Too numerous for NER.** Standard Named Entity Recognition can handle dimensions with tens of values (countries,
  frequencies), but not thousands of nuanced classification codes.

Result: these dimensions need a specialized processor that combines search with LLM reasoning.

### How the LHCL Processor Works

The LHCL processor uses a **two-phase approach** — vector search to narrow candidates, then LLM selection to pick the
right ones:

1. **Vector search** retrieves the top ~50 candidates (configurable via `top_k`) from the full code list using semantic
   similarity. This narrows thousands of codes to a manageable candidate set.
2. **LLM selection** receives the candidate list and the user's query, then selects the most relevant codes. The LLM
   picks the right level of specificity — for example, choosing "C - Manufacturing" for a broad query vs.
   "C10 - Manufacture of food products" for a specific one.
3. **Grounding** ensures no hallucination — the LLM can only select from the retrieved candidates. Any IDs not present
   in the candidate set are automatically discarded.

The processor's prompt is configured per channel (by the system administrator) and guides the LLM's domain-specific
selection logic — for example, instructing it to prefer more specific codes when multiple overlapping categories match.

### Example: How a Query Flows Through the LHCL Processor

**User query:** *"What is the GDP contribution of manufacturing in Ukraine?"*

1. The system identifies that the dataset has a NACE dimension configured with a special processor
2. **Vector search** retrieves ~50 KVED codes semantically related to "manufacturing" from the code list
3. **LLM selection** reviews the candidates and selects "C - Manufacturing" (or a more specific sub-category like
   "C10 - Manufacture of food products" if the query warrants it)
4. The selected code is added to the SDMX query alongside other dimension filters (indicator, country, time period)

### Admin Configuration

In the `dimensions` map, declare the special dimension with `dimensionType: "SPECIAL"` and a `processorId`:

```yaml
dimensions:
  NACE:
    dimensionType: "SPECIAL"
    processorId: "KVED"
```

**Key points:**

- Setting `dimensionType: "SPECIAL"` tells the system to route this dimension through a specialized processor instead
  of the standard indicator search pipeline.
- The `processorId` must match a processor configured in the channel's tool configuration by the system administrator.
  If it doesn't match, special dimension search fails silently — no error, just no results for that dimension.
- Most datasets don't need SPECIAL dimensions — omit them entirely if no dimensions have large hierarchical code lists.

See [Module 04](04-dataset-configuration.md#special-dimensions--large-hierarchical-classifications) for field-by-field
details and common mistakes.

---

## Key Takeaways

- Every dimension must be one of three core types (**INDICATOR**, **NON_INDICATOR**, **TIME_PERIOD**) or the special extensibility type **SPECIAL**
- The core question: *"Would an average person understand this concept?"* — Yes means NON_INDICATOR, No means INDICATOR
- **Misclassification has concrete consequences:** INDICATOR as NON_INDICATOR = values not searchable; NON_INDICATOR as
  INDICATOR = entities not recognized by NER
- In the Admin UI, each dimension is explicitly configured with `dimensionType` in the `dimensions` map, along with
  settings like `isRequired`, `subtype`, `alias`, and `defaultQueries`
- Every NON_INDICATOR dimension must map to a Named Entity type — add new types when needed
- **Special dimensions** (e.g., NACE, ISIC, KVED) use a dedicated LHCL processor with vector search + LLM selection —
  set `dimensionType: "SPECIAL"` with `processorId`
- The same dimension name can be classified differently across datasets depending on its code list values
- When in doubt, classify as INDICATOR
- Different agencies use different dimension IDs for the same concept — use `alias` on the country dimension to unify them

---

## Check Your Understanding

Test your grasp of dimension classification before moving on. Each question presents what you'd actually see in the Admin UI — dimension ID, concept name, and sample codelist values.

<details>
<summary><strong>1. Classify this dimension: <code>CURRENCY_TRANS</code> (Concept: "Transaction currency") with codelist values <code>EUR</code> — Euro, <code>USD</code> — US Dollar, <code>GBP</code> — Pound Sterling. INDICATOR or NON_INDICATOR?</strong></summary>

**Answer:** NON_INDICATOR. Apply the core question: *"Would an average person understand this concept?"* — yes, everyone
knows what currencies are. Set `dimensionType: "NON_INDICATOR"` and map it to the "Currency/Unit of measure" Named Entity
type so that NER can recognize currency mentions in user queries like "trade flows in euros."

</details>

<details>
<summary><strong>2. Classify this dimension: <code>ADJUSTMENT</code> (Concept: "Seasonal adjustment") with codelist values <code>Y</code> — Working day and seasonally adjusted, <code>N</code> — Neither seasonally nor working day adjusted, <code>S</code> — Seasonally adjusted. INDICATOR or NON_INDICATOR?</strong></summary>

**Answer:** INDICATOR. Seasonal adjustment is a statistical method — most users don't know the difference between
"seasonally adjusted" and "working day adjusted," or why it matters. These values describe *how the data was processed*,
which requires domain expertise to interpret. Set `dimensionType: "INDICATOR"`. If you mistakenly set this to
NON_INDICATOR, the adjustment values would never appear in indicator search results, and users searching for
"seasonally adjusted GDP" wouldn't find the right series.

</details>

<details>
<summary><strong>3. This one is tricky. Classify <code>ACCOUNTING_ENTRY</code> (Concept: "Accounting entry", BIS dataset) with codelist values <code>F</code> — Net flows, <code>S</code> — Stocks. Check the grey areas table in this module if you're unsure.</strong></summary>

**Answer:** NON_INDICATOR. Despite sounding financial, "net flows" and "stocks" are general accounting concepts that an
average person can understand without specialized training — flows are changes over a period, stocks are totals at a point
in time. This is one of the grey area cases where the dimension ID sounds domain-specific but the actual codelist values
are accessible. See the grey areas table above for more examples of cases where intuition can mislead you.

</details>

<details>
<summary><strong>4. A Eurostat dataset has a dimension <code>ACTIVITY</code> (Concept: "Economic activity") with 615 codelist values organized in a deep hierarchy: <code>A</code> — Agriculture, forestry and fishing → <code>A01</code> — Crop and animal production → <code>A011</code> — Growing of non-perennial crops → <code>A0111</code> — Growing of cereals. What dimension type should this be?</strong></summary>

**Answer:** SPECIAL with a `processorId`. With 600+ values in a deep hierarchical classification (NACE Rev. 2), standard
INDICATOR indexing would create an enormous search space where keyword and semantic search struggle to navigate the
hierarchy. Instead, set `dimensionType: "SPECIAL"` and assign the `processorId` of the LHCL (Large Hierarchical Code List)
processor configured in the channel's tool settings. The LHCL processor uses vector search combined with LLM selection to
navigate the hierarchy effectively. If you classified this as INDICATOR, users searching for "manufacturing output" would
get poor results because the flat indicator index can't capture the parent-child relationships in the NACE tree.

</details>

<details>
<summary><strong>5. You classify <code>COUNTERPART_AREA</code> (Concept: "Counterpart country") as NON_INDICATOR — the values are country codes like <code>US</code>, <code>DE</code>, <code>JP</code>. The channel currently has these Named Entity types: Country/Reference area, Time frequency, Currency/Unit of measure. What must you do next?</strong></summary>

**Answer:** Add a new Named Entity type to the channel configuration — something like "Counterpart area/country." Every
NON_INDICATOR dimension must map to a Named Entity type so that NER can recognize mentions in user queries. The existing
"Country/Reference area" type is already used by the main `REF_AREA` or `COUNTRY` dimension, so `COUNTERPART_AREA` needs
its own type. If you skip this step, NER won't extract counterpart country mentions from queries like "bilateral trade
with Japan," and the dimension filter won't be applied.

</details>

<details>
<summary><strong>6. A colleague configured <code>COUNTRY</code> (values: <code>US</code>, <code>DE</code>, <code>FR</code>, <code>JP</code>) as INDICATOR instead of NON_INDICATOR. Users now report that "GDP of Germany" returns no results or wrong results. What went wrong?</strong></summary>

**Answer:** Two things broke simultaneously. First, because COUNTRY is marked as INDICATOR, the NER system doesn't look
for country entities in that dimension — so "Germany" in the user's query is never recognized as a country filter.
Instead, "Germany" gets treated as a search term in the indicator index, where it matches nothing (indicator values are
things like "Gross domestic product" or "Consumer prices," not country names). Second, the actual country codes (US, DE,
FR) are now polluting the indicator search index with entries that aren't real indicators. The fix: change COUNTRY to
`dimensionType: "NON_INDICATOR"` with `subtype: "REGION"`, map it to the "Country/Reference area" Named Entity type, and
reindex the dataset.

</details>

---

**Previous:** [Module 02 — Assessing Datasets for Onboarding](02-dataset-assessment.md) | **Next:** [Module 03b — Indicator Configuration](03b-indicator-configuration.md)
