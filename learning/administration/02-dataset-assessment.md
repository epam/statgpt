# Module 02: Assessing Datasets for Onboarding

## What You'll Learn

- Why assessment before configuration prevents costly rework
- How to inspect dataset metadata in the Admin UI
- What users experience when assessment is skipped
- SDMX metadata quality criteria that affect StatGPT performance
- API performance requirements and how to test them
- A go/no-go decision framework for onboarding
- How to evaluate business value for onboarding decisions

---

## Why Assessment Matters

Configuring a dataset in StatGPT involves significant effort — dimension classification, indexer settings, testing, and
validation. Assessing a dataset *before* starting configuration helps you:

- Identify metadata quality issues that would degrade search accuracy
- Understand the dataset structure to make correct dimension type decisions
- Determine whether the dataset's structure is compatible with StatGPT
- Evaluate whether the dataset provides enough value to justify onboarding

Skipping assessment often leads to rework when issues surface during testing.

## What Users Experience When Assessment Fails

In [Module 01](01-core-concepts.md), you saw what users experience when things work well — data tables, charts, and
cited responses. When assessment is skipped or done poorly, users see the consequences directly:

| Assessment Failure                    | User-Visible Consequence                                                                                                     |
|---------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| Generic or numeric code list names    | "No data found" for valid queries — the search index can't match natural language to meaningless codes                       |
| Duplicate names in code lists         | Wrong indicator selected silently, or confusing clarification prompts asking users to choose between identically-named items |
| Missing English localization          | Raw indicator codes (e.g., `IND_042`) shown instead of readable text in tables and responses                                 |
| Slow API responses                    | Long waits (10+ seconds), possible timeouts, and incomplete responses                                                        |
| Sparse data (many empty observations) | Tables full of empty cells that confuse users and undermine trust in the system                                              |

> **As you evaluate each criterion below, ask yourself: if this fails, what will the user see?**

## SDMX Metadata Quality Criteria

StatGPT relies heavily on SDMX metadata for indicator search and query construction. Poor metadata quality leads to poor
search results. Evaluate these criteria before onboarding:

### How to Inspect Metadata

Before assessing quality criteria, you need to know *where* to look. Three methods, in order of preference:

1. **Admin UI Dataset Wizard** — When adding a dataset (**Datasets > Add**), step 3 shows the dataset structure after
   you select a dataflow: dimensions, code lists, and sample values. You can cancel the wizard after reviewing — no need
   to finish adding the dataset. This is the primary inspection method for all admins.

2. **Provider's Data Explorer or similar tool** - Many SDMX providers have a web-based data explorer that shows metadata
   in a user-friendly way. This can be a good secondary method if the Admin UI doesn't show enough detail or if you want
   to see how the provider presents the data to users.

3. **SDMX API directly** — Advanced fallback: query the provider's REST API to browse full code lists and dataflow
   structures. Not normally needed, but useful for systematic testing or when the Admin UI doesn't show enough detail.

### 1. Meaningful, Complete Names and Descriptions

**What to check:**

- Do dataflow names and descriptions clearly indicate what data is available?
- Do code list items have human-readable names (not just codes)?
- Are descriptions provided for dimensions and concepts?

**Why it matters:** StatGPT uses names and descriptions for both semantic search (embedding similarity) and keyword
search (exact term matching). Vague or missing names mean users can't find the data.

**Good example:**

```
Code: LP
Name: "Population, Persons for countries / Index for country groups"
```

**Bad example:**

```
Code: IND_042
Name: "Indicator 42"
```

### 2. Meaningful Hierarchies in Code Lists

**What to check:**

- If code lists are hierarchical, do the hierarchies follow a logical structure?
- Are parent-child relationships consistent and non-contradictory?

**Why it matters:** StatGPT can use hierarchical structure to understand relationships between indicators (e.g., "Food
and non-alcoholic beverages" is a category under CPI).

### 3. Non-Duplicated Item Names in Code Lists

**What to check:**

- Are there code list items with identical names but different IDs?
- Are names unique enough to distinguish items when searching?

**Why it matters:** Duplicate names create ambiguity. When a user asks for "GDP" and there are three code list items all
named "GDP" with different IDs, the system cannot reliably select the correct one.

**Critical:** This is listed as a Critical-priority requirement in
the [SDMX Compatibility Guide](../../architecture/sdmx-compatibility.md).

### 4. English Localization

**What to check:**

- Are all structural metadata elements available in English?
- Are localizations consistent across structures (code lists, concepts, dataflows)?

**Why it matters:** StatGPT requires English localization as a minimum. Additional languages must be consistent across
all structures.

### 5. API Performance

**What to check:**

StatGPT makes multiple API calls during a single user query (structure lookups, availability checks, data fetches). Slow
responses at any step compound into poor user experience.

**Performance thresholds** (from
the [SDMX Compatibility Guide](../../architecture/sdmx-compatibility.md)):

| Endpoint Type            | Request Scenario                      | Max Latency |
|--------------------------|---------------------------------------|-------------|
| **Structure**            | Single structure (no reference stubs) | < 1 sec     |
| **Data**                 | 20 series                             | < 1 sec     |
| **Available Constraint** | 300 series                            | < 1 sec     |

**How to test:**

- **Quick gauge:** Use the Admin UI Dataset Wizard — if step 3 (structure loading) takes noticeably long, investigate
  further.
- **Systematic testing:** Query the provider's SDMX REST API directly for each endpoint type and measure response times.

**Interpretation:**

| Response Time        | Assessment                                                         |
|----------------------|--------------------------------------------------------------------|
| < 1 sec              | Pass                                                               |
| 1–2 sec              | Warning — document, proceed with caution                           |
| 2–5 sec              | Significant concern — test thoroughly, may degrade user experience |
| Consistently > 5 sec | **Blocker** — do not proceed until resolved with the provider      |

## Packed vs. Unpacked Indicators

During assessment, you'll notice that some datasets have codelist values with comma-separated multi-concept strings (
e.g., `"GDP, constant prices, Percent change"`) while others have single-concept values (e.g.,
`"Consumer price index (CPI)"`). This distinction — packed vs. unpacked — is critical for configuration but requires
understanding indicator dimensions first.

**This topic is covered
in [Module 03b — Indicator Configuration](03b-indicator-configuration.md#packed-vs-unpacked-indicators)**, where
you'll learn the decision algorithm after understanding dimension classification.

For now during assessment, simply note whether you see multi-concept comma-separated values in the codelist — you'll
need this observation in Module 03.

## Annotations and Attributes

### Annotations

Some SDMX providers use annotations to add metadata beyond the standard fields:

- **Last updated date** — useful for showing data freshness (configured via `updatedAt`)
- **Additional context** — descriptions, notes, methodology references

Check if the data source supports annotations and whether they provide useful information.

### Attributes

SDMX attributes attach additional information to data observations or series:

- **UNIT** — Unit of measure (e.g., "US Dollars", "Percent")
- **SCALE** — Scale of the values (e.g., "Millions", "Billions")
- **SOURCE** — Data source reference
- **PUBLISHER** — Publishing organization

Relevant attributes should be included via the `includeAttributes` configuration field so the AI agent has context about
the data it presents.

## Empty Observations

Check whether the dataset has many empty (null) observations for certain dimension combinations.

**How to detect:** During assessment, try querying common dimension combinations — for example, request GDP data for a
few major countries over recent years. If many cells come back empty, the dataset may be sparse.

**User impact:** Tables full of empty cells confuse users and undermine trust. A user asking "What is the GDP of
Germany?" expects a clean table, not rows of missing values.

**Severity:** This is a Warning-tier issue, not a Blocker. Sparse data doesn't prevent onboarding but should be
documented and tested thoroughly during [Module 07 — Testing and Validation](07-testing-and-validation.md).

## Assessment Decision Framework

The criteria above tell you *what* to check. This framework tells you *what to do* with the results.

### Blockers (do NOT proceed)

These issues will cause fundamental failures in the user experience. If any Blocker is present, **stop and escalate to
the data provider** before investing configuration effort.

- Generic or numeric code list names with no meaningful labels (e.g., "Indicator 42", "Code_001")
- Missing English localization on code lists — indicator codes will appear as raw IDs
- API consistently exceeding 5x performance thresholds (> 5 sec responses)
- Available Constraint endpoint doesn't work or returns errors

### Warnings (proceed with caution, document)

These issues degrade quality but don't prevent onboarding. Document them and plan extra testing.

- Some duplicate names (< 10% of code list items)
- Borderline API performance (1–2 sec responses)
- Sparse data in some dimension combinations
- Hierarchies partially inconsistent

### Nice-to-Have (proceed, note for future improvement)

These are desirable but not required. Note them for future enhancement.

- Code list descriptions would help search quality but are missing
- No last-updated annotations (data freshness won't be shown)
- Some non-essential attributes missing (e.g., SOURCE, PUBLISHER)

### Decision Logic

```
All Blockers pass + business value confirmed → PROCEED to configuration
Any Blocker fails → STOP, document the issue, escalate to the provider
Warnings present → PROCEED, document warnings, plan extra testing in Module 07
```

## Business Value Assessment

Before investing effort in onboarding, consider:

### Main Purpose

- What questions can users answer with this dataset?
- Does it fill a gap not covered by existing datasets?

### Target Users

- Who will query this data? Economists? Journalists? General public?
- How technical is the expected user base?

### Potential Frequently Asked Questions

- What are the most likely queries users will make?
- Are the key indicators well-represented in the code lists?
- Can users find what they expect using common terms (e.g., "inflation" should map to CPI)?

### Overlap with Existing Datasets

- Does this dataset overlap with already-onboarded datasets?
- If so, which should take priority for overlapping queries?
- **Overlapping datasets can both be onboarded** if they serve different use cases. For example, the IMF channel has
  both ANEA (annual national accounts) and QNEA (quarterly national accounts) — same underlying data at different
  frequencies. ANEA serves annual comparison queries while QNEA serves recent-trend queries.
- Use the `isOfficial` flag to mark national-level or authoritative sources. Official datasets are prioritized in
  dataset selection when queries match multiple datasets.

## Assessment Checklist

Before proceeding to configuration, verify the following items organized by severity:

### Blockers (must ALL pass)

- [ ] Code list items have meaningful, descriptive names (not generic codes)
- [ ] English localization is complete and consistent across structures
- [ ] Structure endpoint responds in < 1 sec (single structure)
- [ ] Data endpoint responds in < 1 sec (20 series)
- [ ] Available Constraint endpoint responds in < 1 sec (300 series)
- [ ] Available Constraint endpoint is functional (returns valid results)

### Warnings (document if any fail)

- [ ] No duplicate names within code lists (or minimal duplicates, < 10%)
- [ ] Hierarchies (if any) are logically structured and consistent
- [ ] Data is reasonably dense (not mostly empty observations)
- [ ] API performance is consistently within thresholds (no intermittent slowdowns)

### Required Understanding (must determine before configuration)

- [ ] You've noted whether codelist values contain comma-separated multi-concept strings (
  see [Module 03b](03b-indicator-configuration.md#packed-vs-unpacked-indicators))
- [ ] You've reviewed the dataset's dimensions and codelist values (classification is covered
  in [Module 03a](03a-dimension-types.md))
- [ ] Relevant attributes are available (UNIT, SCALE, etc.)
- [ ] The dataset provides clear business value for the target audience
- [ ] You've checked for overlap with existing datasets

## Key Takeaways

- Always assess metadata quality before starting configuration — it prevents rework
- **Always inspect metadata through the Admin UI wizard before assessing** — don't guess at quality, look at actual code
  list values
- Good code list names are critical — StatGPT cannot find data that isn't described clearly in the metadata
- **Use the three-tier decision framework** (Blockers / Warnings / Nice-to-Have) to make clear go/no-go decisions
- Consider business value and user needs to prioritize onboarding efforts
- Note codelist value patterns during assessment — you'll use them for dimension classification and indexer settings
  in [Module 03a](03a-dimension-types.md)

## Check Your Understanding

Test your grasp of the assessment concepts before moving on.

<details>
<summary><strong>1. You need to assess a new World Bank dataset. Where do you start inspecting the metadata?</strong></summary>

**Answer:** Start with the **Admin UI Dataset Wizard**. Go to Datasets > Add, select the World Bank data source, browse
available dataflows, and select the one you want to assess. Step 3 of the wizard shows the dataset structure —
dimensions, code lists, and sample values. You can cancel the wizard after reviewing without actually adding the
dataset.

</details>

<details>
<summary><strong>2. During assessment, you find that 15% of code list items share duplicate names. Should you proceed with onboarding?</strong></summary>

**Answer:** This is in the **Warning tier** (> 10% duplicates is concerning). Proceed with caution — document the
duplicates, plan extra testing in [Module 07](07-testing-and-validation.md) to verify that search accuracy is
acceptable, and consider whether the provider can improve the metadata.

</details>

<details>
<summary><strong>3. Users report that "inflation in France" returns no results. You inspect the dataset and see codelist values like <code>IND_042</code> (Name: "Indicator 42"), <code>IND_043</code> (Name: "Indicator 43"). What went wrong?</strong></summary>

**Answer:** **Code list quality** (Criterion 1 — Meaningful, Complete Names). The indicator codelist has generic
labels (`"Indicator 42"`) instead of descriptive ones (`"Consumer Price Index"` or
`"Inflation, average consumer prices"`). The search index can't match "inflation" to `"Indicator 42"` — there's no
semantic or keyword overlap. This is a **Blocker** — do not proceed until the provider adds meaningful names.

</details>

<details>
<summary><strong>4. The Available Constraint endpoint takes 3 seconds for 300 series. What's your assessment?</strong></summary>

**Answer:** This exceeds the < 1 sec threshold. It falls in the **Warning tier** (1–5 sec range) — document it and
proceed, but monitor for degradation. If it consistently exceeds 5 seconds, it becomes a **Blocker** that should be
escalated to the data provider.

</details>

<details>
<summary><strong>5. The IMF has both ANEA (annual) and QNEA (quarterly) national accounts datasets with overlapping data. Should you onboard both?</strong></summary>

**Answer:** **Yes** — they serve different use cases. ANEA is better for long-term annual comparisons (e.g., "GDP growth
over the last 10 years"), while QNEA serves recent-trend queries (e.g., "quarterly GDP change in 2024"). Document the
overlap in both dataset descriptions so the agent can select the right one based on the user's query.

</details>

## Practical Exercises

Apply the assessment checklist to real dataset metadata. These exercises test your ability to evaluate datasets for
onboarding — quality, performance, and business value.

### Exercise 1: Assess a Dataset with Quality Issues

You open the Admin UI Dataset Wizard and inspect a dataset from a new provider. Here's what you see:

**Dataflow:** "National Accounts Data" (no further description)

**Dimensions:**

| Dimension ID  | Concept Name   | Sample Codelist Values                                                                                                                                       |
|---------------|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `IND`         | Indicator      | "GDP_C" (Name: "Gross Domestic Product, current prices"), "GDP_K" (Name: "GDP constant"), "IND_003" (Name: "Indicator 3"), "IND_004" (Name: "Trade balance") |
| `REF_AREA`    | Reference area | "US" (Name: "United States"), "DE" (Name: "Germany"), "JP" (Name: "Japan")                                                                                   |
| `FREQ`        | Frequency      | "A" (Name: "Annual"), "Q" (Name: "Quarterly")                                                                                                                |
| `TIME_PERIOD` | Time period    | "2020", "2021", "2022", "2023"                                                                                                                               |

**Performance:** Structure endpoint: ~0.8 sec. Data endpoint (20 series): ~1.5 sec. Available Constraint (300 series): ~
0.9 sec.

**Your task:** Apply the decision framework. Is this a go, no-go, or conditional proceed?

<details>
<summary><strong>Solution</strong></summary>

**Blockers identified:**

- **Mixed code list quality:** "IND_003" with name "Indicator 3" is a generic label — a Blocker for that item. However,
  most items have meaningful names ("Gross Domestic Product, current prices", "Trade balance").
- **Verdict:** This is a **borderline Blocker**. If only a few items have generic names, you might proceed but those
  items won't be findable by users. If the generic items represent important indicators, this is a hard Blocker.

**Warnings identified:**

- **Data endpoint at 1.5 sec** exceeds the < 1 sec threshold — Warning tier. Document this and test whether it degrades
  user experience under load.
- **Abbreviated code list name:** "GDP constant" is incomplete — should specify "constant prices" in which currency/base
  year. This could lead to user confusion.

**Nice-to-Have:**

- Dataflow description is vague ("National Accounts Data") — better description would help dataset selection.

**Recommendation:** Escalate to the provider about the generic code names ("IND_003", "Indicator 3") and the incomplete
name "GDP constant". If the provider can fix these, proceed with caution on the borderline performance. Document the 1.5
sec data endpoint response time.

</details>

### Exercise 2: Assess Overlapping Datasets for Business Value

Your channel already has **IMF WEO** (World Economic Outlook) onboarded. A stakeholder requests onboarding **IMF ANEA
** (Annual National Accounts Estimates). You inspect ANEA and find:

**IMF WEO (already onboarded):**

- 45 macroeconomic indicators (GDP, inflation, trade, fiscal, etc.)
- 194 countries, annual frequency
- Forecasts included (up to 5 years ahead)

**IMF ANEA (candidate):**

- ~100 national accounts indicators (GDP components, expenditure, income, savings)
- 194 countries, annual frequency
- Historical data only (no forecasts)
- All assessment criteria pass (no Blockers, no Warnings)

**Your task:** Should you onboard ANEA? Both? Neither? Justify using the business value framework.

<details>
<summary><strong>Solution</strong></summary>

**Onboard both** — they serve different use cases despite overlap:

- **WEO** covers broad macroeconomic indicators with forecasts — best for questions like "What is the GDP forecast for
  Brazil?" or "Compare inflation across G7 countries"
- **ANEA** provides detailed national accounts breakdowns — best for questions like "What is the share of government
  consumption in GDP for Germany?" or "How has gross capital formation changed over the last decade?"

**Key differences:**

- ANEA has more granular GDP components that WEO doesn't cover
- WEO has forecasts that ANEA doesn't
- Overlap exists for headline GDP figures, but ANEA provides more detailed decomposition

**Recommendation:** Onboard ANEA. Document the overlap in both dataset descriptions
so the agent can select the right dataset based on query specificity. For example,
WEO: "provides broad macroeconomic indicators and forecasts",
ANEA: "provides detailed national accounts components and breakdowns".

</details>

---

**Previous:** [Module 01 — Core Concepts & Entity Relationships](01-core-concepts.md) | **Next:** [Module 03a — Dimension Types & Named Entities](03a-dimension-types.md)
