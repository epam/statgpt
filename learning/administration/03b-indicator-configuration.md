# Module 03b: Indicator Configuration

> **Prerequisite:** This module requires [Module 03a — Dimension Types & Named Entities](03a-dimension-types.md). You should already understand how to classify dimensions as INDICATOR, NON_INDICATOR, or TIME_PERIOD before proceeding.

## What You'll Learn

- The concept of required vs. optional indicator dimensions
- The difference between packed and unpacked indicators and the `unpack` indexer setting
- Concrete examples from IMF, Eurostat, ECB, BIS, and other agencies
- How to apply these concepts in practice through exercises

---

## Required vs. Optional Indicator Dimensions

Once you've identified all INDICATOR dimensions, decide which are **required**:

- **Required** (`isRequired: true`) — Filtering by this dimension alone is enough to trigger
  a query against this dataset.
- **Optional** (no `isRequired`, or `isRequired: false`) — The dimension provides supplementary
  context, not sufficient on its own to trigger a query.

A dataset query is **only executed** when the user's query filters on at least one of the dataset's
required dimensions. Queries that don't match any required dimension are skipped.

### The Decision Question

> *"If the user's query specifies a filter for this dimension, should it be enough to trigger a query against this dataset?"*
>
> **Yes** → required. **No** → optional.

### Required — Filtering by This Dimension Produces a Sensible Query

- WEO: `INDICATOR` — *"What is [something] for Germany?"* filters on `INDICATOR`, and that alone is enough to query WEO. Required.
- CPI: `INDEX_TYPE` + `COICOP_1999` — filtering by either CPI vs. HICP or a product category is enough
  to trigger a query against this dataset. Both required.

### Optional — This Dimension Is Supplementary, Not Sufficient on Its Own

- CPI `TYPE_OF_TRANSFORMATION` — filtering only by transformation type
  should not be enough to trigger a query against this dataset. Optional.
- ECB BSI `ADJUSTMENT` — seasonal adjustment is a refinement, not essential for returning meaningful data. Optional.

### Rules

1. **Every dataset must have at least one indicator dimension with `isRequired: true`.**
2. The "main" indicator dimension is almost always required.
3. Supporting dimensions (like TYPE_OF_TRANSFORMATION) are often optional — the system can apply sensible defaults.

---

## Packed vs. Unpacked Indicators

Now that you understand dimension classification and required vs. optional, there's one more critical structural distinction: whether a dataset's indicator values are **packed** or **unpacked**. This determines the `unpack` indexer setting, which directly affects search quality.

### What Are Packed Indicators?

A **packed indicator** combines multiple concepts into a single value, typically separated by commas.

**Example — IMF WEO (packed):**
```
INDICATOR dimension values:
- "Gross domestic product, constant prices, Percent change"
- "Gross domestic product, current prices, U.S. dollars"
- "Inflation, average consumer prices, Percent change"
- "Volume of imports of goods and services, Percent change"
```

Each value in the INDICATOR dimension packs together:
- **What** is being measured (GDP, Inflation, Volume of imports)
- **How** it's measured (constant prices, current prices)
- **What unit** (Percent change, U.S. dollars)

### What Are Unpacked Indicators?

An **unpacked indicator** separates these concepts into individual dimensions.

**Example — IMF CPI (unpacked):**
```
INDEX_TYPE dimension values:
- "Consumer price index (CPI)"
- "Harmonised index of consumer prices (HICP)"

COICOP_1999 dimension values:
- "All items"
- "Food and non-alcoholic beverages"
- "Clothing and footwear"
- "Housing, water, electricity, gas and other fuels"

TYPE_OF_TRANSFORMATION dimension values:
- "Index"
- "Percentage change, previous period"
- "Weight"
```

Here, what is being measured is split across three separate indicator dimensions. No single dimension value contains comma-separated multi-concept strings.

### How to Identify Packed Indicators

Now that you know how to classify dimensions, identifying packed vs. unpacked is straightforward:

1. **Look at the indicator dimensions you classified** — focus on the "important" ones (those describing *what* is being measured, not *how*)
2. **Check their codelist values for comma-separated multi-concept strings:**
   - `"GDP, current prices, annual, USD"` — **Packed** (multiple concepts in one value)
   - `"Consumer price index (CPI)"` — **Unpacked** (single concept)
3. **Cross-check with the number of indicator dimensions:**
   - Packed datasets typically have **fewer indicator dimensions** (often just one) with many values each
   - Unpacked datasets typically have **multiple indicator dimensions**, each with fewer values

### Impact on Configuration

| Aspect | Packed | Unpacked |
|--------|--------|----------|
| Indexer `unpack` setting | `true` | `false` |
| Number of indicator dimensions | Usually 1-2 | Usually 2-4+ |
| Code list item length | Long, multi-concept strings | Short, single-concept strings |
| Example datasets | IMF WEO, IMF BOP, IMF ANEA | IMF CPI, Eurostat NAMA_10_GDP, ECB BSI |

**Setting `unpack: true`** tells the indexer to decompose packed indicator names into individual concepts during indexing, improving search accuracy. Setting it incorrectly degrades search quality.

### Real-World Examples

The following table shows actual datasets and their `unpack` settings. Study these to develop pattern recognition:

| Dataset | Provider | `unpack` | Key Evidence |
|---------|----------|----------|-------------|
| WEO | IMF | `true` | Values like "GDP, constant prices, Percent change" — multi-concept packed strings |
| BOP | IMF | `true` | Both INDICATOR and BOP_ACCOUNTING_ENTRY have multi-concept values combining what + how |
| ANEA | IMF | `true` | INDICATOR values are packed multi-concept strings |
| WDI | World Bank | `true` | Values like "GDP (current US$)" pack indicator + unit into one string |
| CPI | IMF | `false` | Each indicator dim has single-concept values — "Consumer price index (CPI)", "All items", "Index" |
| EER | IMF | `true` | Values like "Real effective exchange rate (REER), Index (2010=100) Adjusted by relative consumer prices" — packs type, index spec, and adjustment method |
| ER | IMF | `false` | Despite commas in values, they are natural descriptions (see [Grey Area](#grey-area-semi-packed-indicators) below) |
| NAMA_10_GDP | Eurostat | `false` | Single-concept values in each dimension |
| BSI | ECB | `false` | 7 indicator dims but each has single-concept values like "Loans", "Deposits" |
| TiVA | OECD | `false` | Single-concept values — trade measures and activity sectors |
| Debt Securities | BIS | `false` | 7 indicator dims with single-concept values |

### The Decision Algorithm

Follow this algorithm during manual configuration:

1. **Start with your indicator dimensions** — the dimensions you classified as INDICATOR in the steps above
2. **Among them, find the "important" ones** — those describing *what* is being measured, not *how* (e.g., INDICATOR is important; TYPE_OF_TRANSFORMATION is less important)
3. **Look at their codelist values** — inspect sample values
4. **If any important dim has comma-separated multi-concept values** → set `unpack: true`
   - Example: `"GDP, current prices, annual, USD"` — multiple concepts packed together
5. **If all values are single concepts** → set `unpack: false`
   - Example: `"Consumer price index (CPI)"` — one concept, even though it has parentheses

### Grey Area: Semi-Packed Indicators

Some datasets fall between the extremes. The rule of thumb:

> Look at the **important** indicator dimensions — the ones describing *what* is being measured (not *how*). If at least one important indicator dimension has values with multiple concepts packed together (often comma-separated), set `unpack: true`.

**Teaching case — IMF ER (Exchange Rates):**

The ER dataset's INDICATOR dimension contains values like:
- `"US dollar exchange rate, period average"`
- `"US dollar exchange rate, end of period"`
- `"SDR exchange rate, period average"`

These contain commas, which might suggest packing. But look more carefully: `"US dollar exchange rate, period average"` is a *natural description of a single concept* — the period-average exchange rate against the US dollar. The comma separates a noun phrase from a temporal clarifier, not two independent concepts.

Compare with WEO's `"Gross domestic product, constant prices, Percent change"` — here the commas separate three genuinely independent concepts (what, price basis, unit).

**Result:** ER uses `unpack: false`. The config confirms this with the comment `# No need to unpack`.

**Rule of thumb:** If the comma is part of natural English phrasing describing one thing, it's not packed. If the comma separates independent concepts that could each be a separate dimension, it's packed.

---

## Concrete Examples

### IMF WEO — Simple Structure

| Dimension   | Type                    | Required? | Reasoning                                   |
|-------------|-------------------------|-----------|---------------------------------------------|
| INDICATOR   | INDICATOR               | Yes       | Main (and only) indicator — always required |
| COUNTRY     | NON_INDICATOR (country) | —         | Countries are universally understood        |
| FREQUENCY   | NON_INDICATOR           | —         | Frequency is universally understood         |
| TIME_PERIOD | TIME_PERIOD             | —         | Time dimension                              |

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
```

WEO uses `unpack: true` — the INDICATOR values are packed multi-concept strings like "GDP, constant prices, Percent change".

### IMF BOP — Multiple Required Indicators + NON_INDICATOR UNIT

| Dimension            | Type                    | Required? | Reasoning                                                           |
|----------------------|-------------------------|-----------|---------------------------------------------------------------------|
| INDICATOR            | INDICATOR               | Yes       | Main indicator                                                      |
| BOP_ACCOUNTING_ENTRY | INDICATOR               | Yes       | Credit vs. Debit is essential context                               |
| COUNTRY              | NON_INDICATOR (country) | —         | Countries                                                           |
| FREQUENCY            | NON_INDICATOR           | —         | Frequency                                                           |
| UNIT                 | NON_INDICATOR           | —         | Values like "US Dollars", "Percent of GDP" — universally understood |
| TIME_PERIOD          | TIME_PERIOD             | —         | Time dimension                                                      |

```yaml
dimensions:
  INDICATOR:
    dimensionType: "INDICATOR"
    isRequired: true
  BOP_ACCOUNTING_ENTRY:
    dimensionType: "INDICATOR"
    isRequired: true
  COUNTRY:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
  FREQUENCY:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
  UNIT:
    dimensionType: "NON_INDICATOR"
```

BOP uses `unpack: true` — both INDICATOR and BOP_ACCOUNTING_ENTRY have multi-concept packed values like "Goods, debit" and "Credit, debit and balance".

### IMF CPI — Complex with Optional Indicators

| Dimension              | Type                    | Required? | Reasoning                                   |
|------------------------|-------------------------|-----------|---------------------------------------------|
| INDEX_TYPE             | INDICATOR               | Yes       | CPI vs HICP — essential                     |
| COICOP_1999            | INDICATOR               | Yes       | Product category — essential                |
| TYPE_OF_TRANSFORMATION | INDICATOR               | No        | Index vs. Percent change — optional context |
| COUNTRY                | NON_INDICATOR (country) | —         | Countries                                   |
| FREQUENCY              | NON_INDICATOR           | —         | Frequency                                   |
| TIME_PERIOD            | TIME_PERIOD             | —         | Time dimension                              |

```yaml
dimensions:
  INDEX_TYPE:
    dimensionType: "INDICATOR"
    isRequired: true
  COICOP_1999:
    dimensionType: "INDICATOR"
    isRequired: true
  TYPE_OF_TRANSFORMATION:
    dimensionType: "INDICATOR"             # Not required — optional refinement
  COUNTRY:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
  FREQUENCY:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
```

Note that TYPE_OF_TRANSFORMATION has `dimensionType: "INDICATOR"` but no `isRequired: true` —
making it optional.

CPI uses `unpack: false` — each indicator dimension has single-concept values like "Consumer price index (CPI)", "All items", "Index".

### Eurostat NAMA_10_GDP — Different Naming Conventions

| Dimension   | Type                    | Required? | Reasoning                                                                |
|-------------|-------------------------|-----------|--------------------------------------------------------------------------|
| na_item     | INDICATOR               | Yes       | National accounts item — main indicator                                  |
| unit        | INDICATOR               | No        | Measurement methodology (e.g., "Chain linked volumes") — domain-specific |
| geo         | NON_INDICATOR (country) | —         | Geographic area                                                          |
| freq        | NON_INDICATOR           | —         | Frequency                                                                |
| TIME_PERIOD | TIME_PERIOD             | —         | Time dimension                                                           |

```yaml
dimensions:
  na_item:
    dimensionType: "INDICATOR"
    isRequired: true
  unit:
    dimensionType: "INDICATOR"             # Not required — optional refinement
  geo:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
    alias: "Country/Reference area"
  freq:
    dimensionType: "NON_INDICATOR"
    subtype: "FREQUENCY"
```

**Contrast with IMF BOP:** In BOP, `UNIT` is NON_INDICATOR because its values are currencies and percentages. In
Eurostat NAMA_10_GDP, `unit` is INDICATOR because its values are economics measurement concepts like "Chain linked
volumes" and "Current prices". **The same concept can be classified differently across datasets depending on its actual
values.**

### ECB BSI — Many Dimensions

| Dimension       | Type                    | Required? | Reasoning                      |
|-----------------|-------------------------|-----------|--------------------------------|
| BS_ITEM         | INDICATOR               | Yes       | Balance sheet item             |
| BS_REP_SECTOR   | INDICATOR               | Yes       | Reporting sector               |
| DATA_TYPE       | INDICATOR               | Yes       | Data type                      |
| BS_COUNT_SECTOR | INDICATOR               | Yes       | Counterpart sector (financial) |
| ADJUSTMENT      | INDICATOR               | No        | Seasonal adjustment            |
| MATURITY_ORIG   | INDICATOR               | No        | Maturity                       |
| BS_SUFFIX       | INDICATOR               | No        | Balance sheet suffix           |
| REF_AREA        | NON_INDICATOR (country) | —         | Reference area                 |
| FREQ            | NON_INDICATOR           | —         | Frequency                      |
| COUNT_AREA      | NON_INDICATOR           | —         | Counterpart area               |
| CURRENCY_TRANS  | NON_INDICATOR           | —         | Currency                       |
| TIME_PERIOD     | TIME_PERIOD             | —         | Time dimension                 |

This dataset has 7 indicator dimensions (4 required, 3 optional) and 4 non-indicator dimensions. Despite the many indicator dimensions, BSI uses `unpack: false` — each dimension has single-concept values like "Loans", "Deposits", "Outstanding amounts".

### BIS Debt Securities — COUNTERPART dimensions as NON_INDICATOR

| Dimension          | Type                    | Required? | Reasoning             |
|--------------------|-------------------------|-----------|-----------------------|
| STO                | INDICATOR               | Yes       | Stock/flow concept    |
| REF_SECTOR         | INDICATOR               | Yes       | Reference sector      |
| INSTR_ASSET        | INDICATOR               | Yes       | Instrument/asset type |
| MATURITY           | INDICATOR               | No        | Maturity              |
| CURRENCY_DENOM     | INDICATOR               | No        | Currency denomination |
| VALUATION          | INDICATOR               | No        | Valuation method      |
| CUST_BREAKDOWN     | INDICATOR               | No        | Customer breakdown    |
| REF_AREA           | NON_INDICATOR (country) | —         | Reference area        |
| FREQ               | NON_INDICATOR           | —         | Frequency             |
| COUNTERPART_AREA   | NON_INDICATOR           | —         | Counterpart area      |
| COUNTERPART_SECTOR | NON_INDICATOR           | —         | Counterpart sector    |
| ADJUSTMENT         | NON_INDICATOR           | —         | Adjustment type       |
| CONSOLIDATION      | NON_INDICATOR           | —         | Consolidation basis   |
| ACCOUNTING_ENTRY   | NON_INDICATOR           | —         | Accounting entry      |
| EXPENDITURE        | NON_INDICATOR           | —         | Expenditure type      |
| UNIT_MEASURE       | NON_INDICATOR           | —         | Unit of measure       |
| PRICES             | NON_INDICATOR           | —         | Price type            |
| TRANSFORMATION     | NON_INDICATOR           | —         | Transformation type   |
| TIME_PERIOD        | TIME_PERIOD             | —         | Time dimension        |

Note: BIS classifies ADJUSTMENT as NON_INDICATOR while ECB BSI classifies it as INDICATOR — the classification depends
on the specific code list values in each dataset.

### Cross-Agency Dimension Naming Comparison

The same concept often has different dimension IDs across agencies:

| Concept        | IMF                   | Eurostat  | World Bank | OECD               | ECB          | BIS                |
|----------------|-----------------------|-----------|------------|--------------------|--------------|--------------------|
| Country        | `COUNTRY`             | `geo`     | `REF_AREA` | `REF_AREA`         | `REF_AREA`   | `REF_AREA`         |
| Frequency      | `FREQUENCY`           | `freq`    | `FREQ`     | `FREQ`             | `FREQ`       | `FREQ`             |
| Main indicator | `INDICATOR`           | `na_item` | `SERIES`   | `MEASURE`          | `BS_ITEM`    | `STO`              |
| Counterpart    | `COUNTERPART_COUNTRY` | —         | —          | `COUNTERPART_AREA` | `COUNT_AREA` | `COUNTERPART_AREA` |

This is why the `alias` field on the country dimension exists — it unifies different dimension names across datasets within a
channel (e.g., both `COUNTRY` and `geo` can be aliased to "Country/Reference area").

---

## Check Your Understanding

Classify each dimension using the information an admin actually sees — dimension ID, concept name, and codelist values.

**1. You see this dimension in a new dataset. INDICATOR or NON_INDICATOR?**

|                              |                                                                                                                                                |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **Dimension ID**             | `SECTOR`                                                                                                                                       |
| **Concept name**             | Institutional sector                                                                                                                           |
| **Codelist values (sample)** | `S1` — Total economy, `S11` — Non-financial corporations, `S121` — Central bank, `S128` — Insurance corporations, `S1311` — Central government |

<details>
<summary>Answer</summary>

INDICATOR. Don't be misled by the simple dimension ID `SECTOR`. The concept name "Institutional sector" hints at domain
specificity, but the codelist values confirm it — codes like `S121`, `S128`, `S1311` with labels like "Non-financial
corporations" and "Insurance corporations" require knowledge of the System of National Accounts (SNA) sector
classification. Set `dimensionType: "INDICATOR"` in the `dimensions` map.
</details>

**2. Users report searching for "unemployment" returns no results, but the dataset has an unemployment indicator. You
check the config and see:**

```yaml
dimensions:
  FREQ:
    dimensionType: "INDICATOR"
  COUNTRY:
    dimensionType: "NON_INDICATOR"
    subtype: "REGION"
```

The dataset dimensions are: `INDICATOR` (concept: "Subject"), `COUNTRY`, `FREQ`, `TIME_PERIOD`. What went wrong?

<details>
<summary>Answer</summary>

`INDICATOR` (the subject dimension with values like "Unemployment rate") is not in the `dimensions` map with `dimensionType: "INDICATOR"` — so its values
are never indexed for search. Meanwhile, `FREQ` is incorrectly configured as an indicator dimension. Fix: set `INDICATOR` to
`dimensionType: "INDICATOR"` with `isRequired: true`, change `FREQ` to `dimensionType: "NON_INDICATOR"` with `subtype: "FREQUENCY"`, and reindex the dataset.
</details>

**3. Classify this dimension:**

|                              |                                                                            |
|------------------------------|----------------------------------------------------------------------------|
| **Dimension ID**             | `UNIT_MEASURE`                                                             |
| **Concept name**             | Unit of measure                                                            |
| **Codelist values (sample)** | `USD` — US Dollar, `EUR` — Euro, `PC` — Percent, `PC_GDP` — Percent of GDP |

<details>
<summary>Answer</summary>

NON_INDICATOR. The concept name "Unit of measure" could go either way, but the codelist values are decisive —
currencies (USD, EUR) and basic units (Percent, Percent of GDP) are universally understood. Map it to the "Currency/Unit
of measure" Named Entity type.
</details>

**4. A CPI dataset has three indicator dimensions. An admin marked all three as required. You review:**

| Dimension ID             | Concept name   | Codelist values (sample)                                                                  | Required? |
|--------------------------|----------------|-------------------------------------------------------------------------------------------|-----------|
| `INDEX_TYPE`             | Index type     | `CPI` — Consumer Price Index, `HICP` — Harmonized Index of Consumer Prices                | Yes       |
| `COICOP_1999`            | COICOP 1999    | `011` — Food, `0451` — Electricity, `0722` — Passenger transport by air                   | Yes       |
| `TYPE_OF_TRANSFORMATION` | Transformation | `IX` — Index, `PC_CP_A_PT` — Percentage change over corresponding period of previous year | Yes       |

Should all three be required?

<details>
<summary>Answer</summary>

No — `TYPE_OF_TRANSFORMATION` should be optional. `INDEX_TYPE` is essential (CPI vs. HICP changes what data you get),
and `COICOP_1999` is essential (which product category?). But `TYPE_OF_TRANSFORMATION` is a refinement — the system can
default to "Index" (`IX`) and still return meaningful data. Apply the decision question: *"Can the system still return a
meaningful answer without it?"* — yes, so remove `isRequired: true` from TYPE_OF_TRANSFORMATION.
</details>

**5. You're onboarding a new dataset. Classify this dimension and decide what to do next:**

|                              |                                                                                                                       |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| **Dimension ID**             | `COUNTERPART_SECTOR`                                                                                                  |
| **Concept name**             | Counterpart institutional sector                                                                                      |
| **Codelist values (sample)** | `S1` — Total economy, `S11` — Non-financial corporations, `S12K` — Non-MMF investment funds, `S2` — Rest of the world |

The channel has these Named Entity types: `Country/Reference area`, `Time frequency`, `Currency/Unit of measure`,
`Counterpart area/country`.

<details>
<summary>Answer</summary>

INDICATOR. The codelist values use SNA sector codes (`S11`, `S12K`) that require domain knowledge — this is the same
classification system as question 1. Set `dimensionType: "INDICATOR"`. No Named Entity type mapping needed since it's not
NON_INDICATOR. If you mistakenly classified it as NON_INDICATOR, you'd also need to add a new Named Entity type like "
Counterpart sector" to the channel — but the codelist values clearly point to INDICATOR.
</details>

**6. Two datasets both have a dimension called `UNIT`. Classify each:**

**Dataset A:**

|                         |                                                          |
|-------------------------|----------------------------------------------------------|
| **Dimension ID**        | `UNIT`                                                   |
| **Concept name**        | Currency                                                 |
| **Codelist values**     | `USD` — US Dollar, `EUR` — Euro, `GBP` — Pound Sterling |

**Dataset B:**

|                              |                                                                                                                                                  |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **Dimension ID**             | `UNIT`                                                                                                                                           |
| **Concept name**             | Unit of measure                                                                                                                                  |
| **Codelist values (sample)** | `CLV15_MEUR` — Chain linked volumes (2015), million euro, `CP_MEUR` — Current prices, million euro, `PD15_EUR` — Price deflator (2015), euro |

<details>
<summary>Answer</summary>

Different classification despite the same dimension ID. Dataset A: NON_INDICATOR — concept name "Currency" confirms it,
and codelist values are universally understood currency codes. Dataset B: INDICATOR — "Chain linked volumes", "Price
deflator" are economics measurement concepts that require domain knowledge. This is why you must always check codelist
values, not just the dimension ID.
</details>

**7. An INDICATOR dimension has values like "Exports of goods and services, Percent of GDP". Packed or unpacked?**

<details>
<summary>Answer</summary>

**Packed.** The value combines what is being measured ("Exports of goods and services") with a unit/transformation ("Percent of GDP") — two independent concepts separated by a comma. Set `unpack: true`.
</details>

**8. An INDICATOR dimension has values like "US dollar exchange rate, period average". Packed or unpacked?**

<details>
<summary>Answer</summary>

**Unpacked** despite the comma. "US dollar exchange rate, period average" is a natural English description of a single concept — the period-average USD exchange rate. The comma separates a noun phrase from a temporal clarifier, not two independent concepts. Set `unpack: false`.
</details>

**9. A dataset has 7 indicator dimensions, each with single-concept values like "Loans", "Deposits", "Outstanding amounts". Is this packed because there are so many dimensions?**

<details>
<summary>Answer</summary>

**No — this is unpacked.** Many dimensions with single-concept values ≠ packing. Packed vs. unpacked is about the *structure of values*, not the *number of dimensions*. Each value describes one concept, so set `unpack: false`. This is exactly how ECB BSI works — 7 indicator dimensions, all unpacked.
</details>

---

## Key Takeaways

- **Required indicator dimensions** (`isRequired: true`) are those without which a query is meaningless; optional ones are refinements with
  sensible defaults
- At least one indicator dimension must have `isRequired: true`
- **Packed vs. unpacked** is the most important structural distinction for indicator dimensions — it determines the `unpack` indexer setting
- Packed indicators combine multiple concepts in comma-separated values → set `unpack: true`
- Unpacked indicators have single-concept values across multiple dimensions → set `unpack: false`
- Commas in natural English descriptions (e.g., "exchange rate, period average") do not indicate packing

---

## Practical Exercises

Apply dimension classification and packed/unpacked analysis to real dataset metadata. Each exercise shows what you'd see when inspecting a dataset — dimension IDs, concept names, and sample codelist values.

### Exercise 1: ECB BSI (Balance Sheet Items)

You open the Admin UI Dataset Wizard and select the ECB BSI dataflow. The structure step shows:

**Dimensions:**

| Dimension ID | Concept Name | Sample Codelist Values |
|---|---|---|
| `BS_ITEM` | Balance sheet item | "Loans", "Debt securities held", "Deposits", "Total assets/liabilities" |
| `ADJUSTMENT` | Adjustment indicator | "Neither seasonally nor working day adjusted", "Working day adjusted" |
| `BS_REP_SECTOR` | Balance sheet reporting sector | "Domestic (home or reference area)", "Monetary financial institutions" |
| `MATURITY_ORIG` | Original maturity | "Total", "Up to 1 year", "Over 1 year and up to 2 years" |
| `DATA_TYPE` | Data type | "Outstanding amounts", "New business", "Transactions" |
| `BS_COUNT_SECTOR` | Balance sheet counterpart sector | "Domestic (home or reference area)", "Non-financial corporations" |
| `BS_SUFFIX` | Series variation - Loss and impairment suffix | "Original maturity", "Residual maturity" |
| `REF_AREA` | Reference area | "AT", "BE", "DE", "FR", ... |
| `FREQ` | Frequency | "A", "M", "Q" |
| `CURRENCY_TRANS` | Currency of transaction | "EUR", "USD", "GBP" |
| `TIME_PERIOD` | Time period | "2020", "2021-Q1", "2023-06" |

**Your task:** Classify each dimension, determine packed/unpacked, and decide the `unpack` setting.

<details>
<summary><strong>Solution</strong></summary>

**Dimension classification:**
- **Indicator dims:** BS_ITEM, ADJUSTMENT, BS_REP_SECTOR, MATURITY_ORIG, DATA_TYPE, BS_COUNT_SECTOR, BS_SUFFIX — all describe aspects of *what* is being measured or *how* the measurement is characterized
- **Non-indicator dims:** REF_AREA (country/region), FREQ (frequency), CURRENCY_TRANS (currency context)
- **Time dim:** TIME_PERIOD

**Packed/Unpacked:** **Unpacked** (`unpack: false`). Look at the codelist values: "Loans", "Deposits", "Outstanding amounts", "Non-financial corporations" — each is a single concept. No comma-separated multi-concept strings. The 7 indicator dimensions may seem like a lot, but many dimensions with single-concept values ≠ packing. It means the dataset has a complex but well-structured dimensionality.

**Configuration notes:**
- 7 indicator dimensions means many possible combinations — plan thorough testing in [Module 07](07-testing-and-validation.md)
- All codelist values are descriptive English names (no generic codes) — no assessment Blockers

</details>

### Exercise 2: IMF BOP (Balance of Payments)

You open the Admin UI Dataset Wizard and select the IMF BOP dataflow. The structure step shows:

**Dimensions:**

| Dimension ID | Concept Name | Sample Codelist Values |
|---|---|---|
| `INDICATOR` | Indicator | "Goods, debit", "Current Account, Total, Net", "Financial Account, Direct Investment, Assets, Net Incurrence of Liabilities", "Services, Credit" |
| `BOP_ACCOUNTING_ENTRY` | BOP accounting entry | "Credit, debit and balance", "Supplementary items", "As a ratio to GDP" |
| `COUNTRY` | Reference area | "US", "DE", "JP", "FR", ... |
| `FREQUENCY` | Frequency | "A", "Q", "M" |
| `UNIT` | Unit | "US Dollars", "National Currency" |
| `TIME_PERIOD` | Time period | "2020", "2023-Q1", "2024-06" |

**Your task:** Classify each dimension, determine packed/unpacked, and decide the `unpack` setting.

<details>
<summary><strong>Solution</strong></summary>

**Dimension classification:**
- **Indicator dims:** INDICATOR, BOP_ACCOUNTING_ENTRY — both describe *what* is being measured
- **Non-indicator dims:** COUNTRY (region), FREQUENCY, UNIT (values like "US Dollars" are universally understood)
- **Time dim:** TIME_PERIOD

**Packed/Unpacked:** **Packed** (`unpack: true`). Look at the INDICATOR values:
- `"Goods, debit"` — packs the concept (Goods) with the accounting direction (debit)
- `"Financial Account, Direct Investment, Assets, Net Incurrence of Liabilities"` — packs multiple hierarchy levels and accounting concepts into one comma-separated string

BOP_ACCOUNTING_ENTRY also has multi-concept values like `"Credit, debit and balance"`.

Compare with the ECB BSI exercise: BSI's values like "Loans" and "Outstanding amounts" are each one concept. BOP's values like "Current Account, Total, Net" pack multiple concepts together.

**Configuration:**
```yaml
indexer:
  indicator:
    unpack: true
```

</details>

---

**Previous:** [Module 03a — Dimension Types & Named Entities](03a-dimension-types.md) | **Next:** [Module 04 — Configuring a Dataset](04-dataset-configuration.md)
