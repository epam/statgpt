# Module 08: End-to-End Walkthrough

## What You'll Learn

- How to apply all modules in sequence to onboard a real dataset end-to-end
- The complete onboarding lifecycle: assessment → classification → configuration → indexing → testing
- How to make and document key configuration decisions at each step

This capstone exercise walks through onboarding a single dataset from scratch, applying every module in sequence. Use it to validate your understanding before onboarding real datasets independently.

---

## The Dataset: IMF EER (Effective Exchange Rates)

We'll onboard the IMF Effective Exchange Rates dataset — a real dataset that combines several interesting characteristics:

- A single indicator dimension with packed multi-concept values
- Packed structure that looks superficially similar to IMF ER's unpacked natural descriptions — a good test of Module 03b's decision algorithm
- Country dimension with standard naming
- Moderate complexity (not too simple, not overwhelming)

**Dataflow:** `IMF.STA:EER(3.0.0)` — Effective Exchange Rates

**What it provides:** Real and nominal effective exchange rates for countries, measuring the value of a country's currency relative to its trading partners.

---

## Step 1: Assess the Dataset (Module 02)

Before configuring anything, inspect the metadata through the Admin UI Dataset Wizard.

### Metadata Inspection

**Dimensions found:**

| Dimension ID | Concept Name | Sample Codelist Values |
|---|---|---|
| `INDICATOR` | Indicator | "Real effective exchange rate (REER), Index (2010=100) Adjusted by relative consumer prices", "Nominal effective exchange rate (NEER), Index (2010=100) Advanced economy trade partner weighted", "Nominal effective exchange rate (NEER), Index (2010=100) Weighted index" |
| `COUNTRY` | Reference area | "US" — United States, "DE" — Germany, "JP" — Japan, "GB" — United Kingdom |
| `FREQUENCY` | Frequency | "A" — Annual, "M" — Monthly |
| `TIME_PERIOD` | Time period | "2020", "2023-01", "2024-06" |

### Assessment Checklist

**Blockers:**
- [x] Code list items have meaningful, descriptive names — "Real effective exchange rate (REER), Index (2010=100) Adjusted by relative consumer prices" is clear
- [x] English localization is complete
- [x] API performance within thresholds (IMF SDMX 2.1 API — already validated for other IMF datasets)
- [x] Available Constraint endpoint functional

**Warnings:**
- None identified

**Business value:**
- Fills a gap: exchange rate data not covered by WEO or BOP
- Target users: economists, forex analysts, trade policy researchers
- Common queries: "What is the exchange rate of the euro?", "How has the yen depreciated?"

**Decision: PROCEED**

---

## Step 2: Classify Dimensions (Module 03a)

Apply the decision framework to each dimension:

| Dimension | Core Question | Classification | Reasoning |
|---|---|---|---|
| `INDICATOR` | Would an average person understand "Real effective exchange rate (REER), Index (2010=100) Adjusted by relative consumer prices"? **No** — requires knowledge of trade-weighted baskets and price deflation methods | **INDICATOR** | Domain-specific measurement concepts |
| `COUNTRY` | Would an average person understand "Germany"? **Yes** | **NON_INDICATOR** | Countries are universally understood |
| `FREQUENCY` | Would an average person understand "Annual"? **Yes** | **NON_INDICATOR** | Frequency is universally understood |
| `TIME_PERIOD` | Time dimension | **TIME_PERIOD** | Auto-detected |

**Named Entity types check:**
- `COUNTRY` → maps to existing "Country/Reference area" ✓
- `FREQUENCY` → maps to existing "Time frequency" ✓
- No new Named Entity types needed

---

## Step 3: Determine Packed/Unpacked + Required/Optional (Module 03b)

### Packed vs. Unpacked

Look at the INDICATOR codelist values:
- `"Real effective exchange rate (REER), Index (2010=100) Adjusted by relative consumer prices"`
- `"Nominal effective exchange rate (NEER), Index (2010=100) Advanced economy trade partner weighted"`
- `"Nominal effective exchange rate (NEER), Index (2010=100) Weighted index"`

Apply the decision algorithm from [Module 03b](03b-indicator-configuration.md#how-to-identify-packed-indicators). Each value packs together multiple independent concepts:
- **What** is being measured (REER vs. NEER)
- **Index specification** (Index, 2010=100)
- **Adjustment/weighting method** (relative consumer prices, advanced economy trade partner weighted)

**Don't confuse EER with ER.** Module 03b's [grey area section](03b-indicator-configuration.md#grey-area-semi-packed-indicators) discusses IMF **ER** (bilateral Exchange Rates), where values like `"US dollar exchange rate, period average"` are natural descriptions of single concepts → `unpack: false`. EER's values are structurally different — they combine genuinely separable concepts, similar to WEO's `"Gross domestic product, constant prices, Percent change"`.

**Decision: `unpack: true`** — these are packed multi-concept indicator values.

### Required vs. Optional

Only one indicator dimension (`INDICATOR`), so the decision is simple:

> *"Can the system return a meaningful answer without specifying an indicator?"*
> **No** — "What is [something] for Germany?" is meaningless without knowing which exchange rate.

**Decision: `INDICATOR` is required.**

---

## Step 4: Write the Dataset YAML (Module 04)

```yaml
urn:
  agency_id: "IMF.STA"
  resource_id: "EER"
  version: "latest"                    # Always track the current published version
citation:
  provider: "IMF Statistics Department (STA)"
  url: https://data.imf.org/en/datasets/IMF.STA:EER
  description: >
    The Effective Exchange Rate (EER) dataset includes annual, quarterly and
    monthly nominal and real effective exchange rates by economy. Nominal
    effective exchange rates (NEERs) measure the value of a country's currency
    in relation to a weighted average of the currency values of their major
    trading partners. Real effective exchange rates (REERs) adjust the NEER
    to account for a country's inflation rate in relation to the weighted
    inflation rate of their major trading partners.
isOfficial: false
useTitleFromSrc: true
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
    isRequired: true
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
includeAttributes:
  - SCALE
  - UNIT
  - PUBLISHER
  - SOURCE
pinnedColumns:
  - FREQUENCY_Name
  - COUNTRY_Name
  - INDICATOR_Name
indexer:
  indicator:
    unpack: true
```

**Key decisions documented:**
- `version: "latest"` — always tracks the current published EER version
- `unpack: true` — packed multi-concept values combining exchange rate type, index specification, and adjustment method
- `isOfficial: false` — IMF is international, not national
- `allValues` on COUNTRY — enables star-queries like "exchange rates for all countries"
- `updatedAt` — checks three sources in order for the last-updated date
- `pinnedColumns` ordered: FREQUENCY (least important) → COUNTRY → INDICATOR (most important)
- Each dimension explicitly configured with `dimensionType` in the `dimensions` map

---

## Step 5: Verify Data Source and Channel (Module 05)

### Data Source

The IMF SDMX 2.1 Data Source should already exist (used by WEO, BOP, CPI, etc.). No new data source needed.

### Channel Configuration

Check the channel's Named Entity types:
```yaml
namedEntityTypes:
  - Time frequency
  - Counterpart area/country
  - Currency/Unit of measure
countryNamedEntityType: Country/Reference area
```

- `countryNamedEntityType: Country/Reference area` matches our country dimension's `alias` ✓
- No new NON_INDICATOR dimensions requiring new Named Entity types ✓

**Link the dataset to the channel** via the channel detail page.

---

## Step 6: Index and Deduplicate (Module 06)

1. Navigate to the channel detail page
2. Find the EER dataset in the list
3. Click **Reindex**
4. Monitor status until **Finished**
5. Run **Deduplication** to clean up any near-duplicate entries

**Cost awareness:** EER has a relatively small indicator code list, so indexing cost is low compared to datasets like WEO or CPI.

**Ongoing maintenance:** If the channel has `allowAutoUpdate: true` and the dataset uses `version: "latest"`, the
auto-update system will automatically check for upstream changes to the EER dataset and reindex when needed. See
[Module 06 — Auto-Update](06-indexing-and-operations.md#auto-update).

---

## Step 7: Design Test Cases (Module 07)

The test case YAML shown below is simplified for readability. The full ground truth schema includes additional evaluation fields (`is_out_of_scope`, `tool_calls`, `query_normalization`, etc.) — see [Module 07](07-testing-and-validation.md) for the complete format.

### Test Case 1: Simple REER Query

```yaml
- role: user
  content: Give me REER adjusted by relative consumer prices for Armenia.
  target:
    indicator_selection:
      - dataset_id: IMF.STA:EER
        dimensions:
          - dimension_name: INDICATOR
            values:
              - id: REER_IX_RY2010_ACW_RCPI
                name: Real effective exchange rate (REER), Index (2010=100) Adjusted by relative consumer prices
          - dimension_name: COUNTRY
            values:
              - id: ARM
                name: Armenia, Republic of
```

**What to verify:** System selects the EER dataset and matches the REER CPI-based indicator by abbreviation.

### Test Case 2: Synonym Query

```yaml
- role: user
  content: How has the Japanese yen depreciated over the last 5 years?
  target:
    indicator_selection:
      - dataset_id: IMF.STA:EER
        dimensions:
          - dimension_name: INDICATOR
            values:
              - id: REER_IX_RY2010_ACW_RCPI
                name: Real effective exchange rate (REER), Index (2010=100) Adjusted by relative consumer prices
          - dimension_name: COUNTRY
            values:
              - id: JPN
                name: Japan
```

**What to verify:** "depreciated" maps to exchange rate concepts. The system might select nominal or real — both are acceptable.

### Test Case 3: Cross-Dataset Ambiguity

```yaml
- role: user
  content: What is the GDP of Germany?
  target:
    indicator_selection:
      - dataset_id: IMF.RES:WEO
        dimensions:
          - dimension_name: INDICATOR
            values:
              - name: Gross domestic product, current prices, U.S. dollars
```

**What to verify:** GDP query does NOT match the EER dataset — it should go to WEO.

### Test Case 4: NEER with Specific Weighting

```yaml
- role: user
  content: What is the value of the advanced economy trade partner weighted NEER of Norway?
  target:
    indicator_selection:
      - dataset_id: IMF.STA:EER
        dimensions:
          - dimension_name: INDICATOR
            values:
              - id: NEER_IX_RY2010_AEW
                name: Nominal effective exchange rate (NEER), Index (2010=100) Advanced economy trade partner weighted
          - dimension_name: COUNTRY
            values:
              - id: NOR
                name: Norway
```

**What to verify:** "advanced economy trade partner weighted NEER" precisely matches the specific NEER variant.

---

## Step 8: Run Tests and Iterate

### Execution

Run each test case 2-3 times in the chat interface:

| Test | Run 1 | Run 2 | Run 3 | Assessment |
|---|---|---|---|---|
| Simple REER | ✓ EER selected | ✓ EER selected | ✓ EER selected | Consistent |
| Synonym ("depreciated") | ✓ REER CPI | ✓ NEER weighted | ✓ REER CPI | Acceptable variance |
| Cross-dataset (GDP) | ✓ WEO selected | ✓ WEO selected | ✓ WEO selected | No false match |
| NEER specific weighting | ✓ Exact match | ✓ Exact match | ✓ Exact match | Ideal |

### Iteration Example

If test 2 consistently returns NEER instead of REER for depreciation queries, consider:
- Would the `unpack: true` setting improve or degrade search for these multi-concept indicator names?
- Are the indicator code list names descriptive enough to disambiguate REER from NEER?

Adjust configuration → reindex → retest until results are satisfactory.

---

## Key Takeaways

This walkthrough covered the complete onboarding lifecycle:

| Step | Module | Key Decision |
|---|---|---|
| Assessment | [02](02-dataset-assessment.md) | All blockers clear, business value confirmed |
| Dimension classification | [03a](03a-dimension-types.md) | INDICATOR (1), NON_INDICATOR (2), TIME_PERIOD (1) |
| Indicator configuration | [03b](03b-indicator-configuration.md) | `unpack: true`, INDICATOR required |
| Dataset YAML | [04](04-dataset-configuration.md) | Complete configuration with all required fields |
| Data Source & Channel | [05](05-data-sources-and-channels.md) | Existing data source, no new Named Entity types |
| Indexing | [06](06-indexing-and-operations.md) | Index + deduplicate |
| Testing | [07](07-testing-and-validation.md) | 4 test cases across categories |

- The onboarding lifecycle follows a consistent pattern regardless of the dataset
- Assessment (Module 02) prevents costly rework — always check metadata quality first
- Dimension classification and packed/unpacked decisions are the highest-impact configuration choices — EER and ER look similar but have different `unpack` settings
- Testing with multiple runs reveals LLM non-determinism — evaluate patterns, not individual results
- With `version: "latest"` and `allowAutoUpdate: true`, ongoing maintenance is automated

Use the [Quick-Reference Card](quick-reference.md) for a condensed checklist during future onboarding.

---

**Previous:** [Module 07 — Testing & Validation](07-testing-and-validation.md) | **Back to:** [Module Index](README.md)
