# Module 07: Testing & Validation

> **This is a key module.** Testing is essential for quality assurance. LLM-powered systems are non-deterministic — systematic testing is the only way to ensure consistent quality.

## What You'll Learn

- Why LLM non-determinism makes testing essential (not optional)
- The concept of ground truth for data queries
- How to design test cases that cover a dataset effectively
- Evaluation concepts: precision, recall, and how StatGPT trades off between them
- A manual verification workflow for validating results
- Example test cases from IMF datasets

---

## LLM Non-Determinism

### Why the Same Query Can Produce Different Results

StatGPT uses large language models at multiple stages of the query pipeline (indicator selection, dataset selection, dimension matching, etc.). LLMs are inherently non-deterministic:

- **Same prompt, different results** — Even with `temperature: 0` and a fixed `seed`, LLMs may produce slightly different outputs across runs due to infrastructure-level variability
- **Context sensitivity** — Conversation history affects results. The same question asked as a first message vs. after a series of related questions may yield different indicator selections
- **Model updates** — When the underlying LLM provider updates or patches models, behavior may change even with identical configuration

### What This Means for Admins

- A query that worked correctly yesterday might produce slightly different results today
- You cannot rely on a single test run to validate a dataset
- Systematic testing with defined ground truth is the only way to measure quality over time
- Occasional deviations from expected results are normal — evaluate patterns, not individual runs

---

## Ground Truth

### What Is Ground Truth?

In the context of StatGPT data queries, **ground truth** is the expected set of results for a given natural language query:

- **Expected dataset** — Which dataset should be queried
- **Expected indicators** — Which indicator dimension values should be selected
- **Expected dimensions** — Which non-indicator dimension values should match (country, etc.)

Ground truth defines what "correct" means for a specific query, enabling objective evaluation.

### Defining "Correct" When Results Can Vary

Because of LLM non-determinism, "correct" is not binary. Instead:
- A result that matches all ground truth items is **ideal**
- A result that matches most ground truth items with a few extras is **acceptable** (high recall, slightly lower precision)
- A result that misses key ground truth items is **problematic** (low recall)
- A result from a completely wrong dataset is a **failure**

### Test Case Structure

Test cases are maintained in YAML format. Here is a simplified structure:

```yaml
id: c48d7624-d376-48ca-b2d8-386999befb45
name: population_numbers_for_mexico
conversation:
  - role: user
    content: Could you give me the population numbers for Mexico?
    target:
      indicator_selection:
        - dataset_id: IMF.RES:WEO
          dimensions:
            - dimension_name: INDICATOR
              values:
                - id: LP
                  name: Population, Persons for countries / Index for country groups
            - dimension_name: COUNTRY
              values:
                - id: MEX
                  name: Mexico
```

Each test case specifies:
- **Query** — The natural language question
- **Expected dataset** — Which dataset should be matched (`dataset_id`)
- **Expected dimensions** — For each relevant dimension, the expected values (both ID and name)

> **Note:** This is a simplified view. The full test case schema includes additional fields (`id`, `name`, `tags`, `comments`) and supports multi-turn conversations. For the complete schema and automated evaluation methodology, see [Data Query Evaluation](../../evaluation/data_query.md).

---

## Test Case Categories

Design test cases across these categories to ensure thorough coverage:

### 1. Single Indicator Queries

The simplest and most common query type. One specific indicator for one or more countries.

> *"What was GDP of Germany in 2023?"*
> Expected: WEO dataset, INDICATOR = GDP-related item, COUNTRY = DEU

### 2. Multi-Indicator Queries

Queries asking for multiple related indicators simultaneously.

> *"GDP and unemployment in France over the last 5 years"*
> Expected: WEO dataset, INDICATOR = GDP + unemployment items, COUNTRY = FRA

### 3. Indicator Group Queries

Queries asking for a category of indicators rather than specific ones.

> *"Show me labor market indicators for Japan"*
> Expected: Relevant dataset, multiple labor-related INDICATOR items, COUNTRY = JPN

### 4. Synonym Queries

Queries using common terms that don't match indicator names exactly.

> *"How did inflation change in Brazil?"*
> Expected: CPI dataset (inflation → Consumer Price Index)

### 5. Complex/Ambiguous Queries

Queries that could match multiple datasets or require clarification.

> *"What are the economic indicators for Kenya?"*
> Expected: Could match WEO, BOP, or other datasets — system should ask for clarification or return the most relevant

---

## How to Think About Dataset Coverage

When creating test cases for a newly onboarded dataset, aim to cover:

### Indicator Dimensions
- At least one test case per indicator dimension
- For required indicator dimensions, test cases that exercise different values
- For optional indicator dimensions, test cases both with and without filtering on them

### Country/Region Dimension
- Test with specific countries (e.g., "USA", "Germany")
- Test with country groups or regions if applicable (e.g., "ASEAN countries", "Euro area")
- Test with "all countries" queries if the dataset supports star-queries

### Time Period Variations
- Explicit dates: *"GDP in 2023"*
- Relative periods: *"GDP over the last 5 years"*
- Ranges: *"GDP from 2015 to 2020"*
- Future (for forecast datasets): *"GDP projection for 2026"*

### Synonym Coverage
- Identify common synonyms for key indicators (inflation → CPI, economic growth → GDP growth)
- Create test cases using those synonyms instead of official indicator names

### Cross-Dataset Scenarios
- If the channel has multiple datasets, test queries that could match more than one
- Verify the system selects the most appropriate dataset

---

## Evaluation Concepts

### Precision and Recall

Two standard metrics measure the quality of indicator selection:

**Precision** — Of all indicators the system selected, how many were correct?

$$\text{Precision} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$$

- High precision = few irrelevant results (no noise)
- Low precision = many extra, unwanted indicators in the results

**Recall** — Of all correct indicators, how many did the system find?

$$\text{Recall} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$$

- High recall = all expected indicators found (nothing missed)
- Low recall = some expected indicators are missing from results

### StatGPT's Trade-Off

StatGPT is designed to **trade off slightly in favor of recall** over precision. This means:
- The system prefers to find all relevant indicators (even at the cost of some extra results)
- It's better to show the user a few extra indicators than to miss the ones they asked for
- Users can easily ignore irrelevant results, but missing data is a worse experience

### How to Interpret Results

| Scenario | Precision | Recall | Meaning |
|----------|-----------|--------|---------|
| Ideal | High | High | System found exactly the right indicators |
| Acceptable | Medium | High | System found all expected indicators plus some extras |
| Problematic | High | Low | System is precise but missed important indicators |
| Poor | Low | Low | System missed indicators and returned irrelevant ones |

### Practical Example

Target (ground truth) INDICATOR values: GDP, GDPPC

System selected: GDP, GDPPC, GDP_CONST

- **True Positives:** GDP, GDPPC (2 items — correctly selected)
- **False Positives:** GDP_CONST (1 item — selected but not in target)
- **False Negatives:** none (0 items — nothing missed)
- **Precision:** 2 / (2 + 1) = 0.67
- **Recall:** 2 / (2 + 0) = 1.0

This is an acceptable result — recall is perfect (nothing missed), precision is slightly lower because one extra indicator was included.

---

## Manual Verification Workflow

When testing a newly onboarded dataset, follow this workflow:

### Step 0: Verify Indexing

Before running test queries, verify the dataset was indexed correctly. Use the Available Datasets tool in the chat
(with `includeIndicatorCount: true` — see [Module 06](06-indexing-and-operations.md#validating-indexing-results)) to
check that the dataset appears and has a non-zero indicator count. A count of 0 means the dataset is not searchable —
fix the configuration and reindex before proceeding with testing.

### Step 1: Run the Query

Open StatGPT (the chat interface for the channel) and type the test query.

### Step 2: Check the Dataset

Verify the system queried the expected dataset. The response should cite the data source.

### Step 3: Compare Indicators Against Ground Truth

Look at the indicators returned in the data table:
- **Are all expected indicators present?** If not, note which are missing (recall issue)
- **Are there unexpected extra indicators?** If so, note which (precision issue)

### Step 4: Check Dimension Values

Verify country, time period, and other dimension values match expectations.

### Step 5: Note Discrepancies

Record any differences between expected and actual results:
- Missing indicators → **Recall issue** → May need to adjust indexer config or check code list quality
- Extra indicators → **Precision issue** → Usually acceptable; may indicate indexer tuning needed
- Wrong dataset selected → **Dataset selection issue** → Check dataset descriptions and indicator overlap

### Step 6: Re-Run for Variance

Run the same query 2-3 times to understand the variance:
- If results are consistent across runs → Reliable
- If results vary significantly → Note the range of variation

### Step 7: Iterate

If test results are unsatisfactory:
1. Check the dataset configuration (dimension types, `unpack` setting, indexer description)
2. Review the code list metadata quality (see [Module 02](02-dataset-assessment.md))
3. Reindex the dataset after making changes
4. Re-test

---

## Creating Good Test Cases

### Start from the Dataset Structure

1. Look at the dataset's indicator code list items
2. For each major indicator category, write a query a real user might ask
3. Don't write test cases from the statistician's perspective — write them from the user's

### Think Like a User

- Users don't know indicator IDs or exact names
- Users use informal language: "economic growth" not "Gross domestic product, constant prices, Percent change"
- Users may use abbreviations: "GDP", "CPI", "BOP"
- Users ask in context: "How did China's economy perform?" not "Select INDICATOR=GDP WHERE COUNTRY=CHN"

### Include Edge Cases

- **Ambiguous terms** — "investment" could mean foreign direct investment, portfolio investment, or capital formation
- **Multiple possible datasets** — "trade data" could match IMTS, BOP, or TiVA
- **Synonyms** — "inflation" → CPI, "economic output" → GDP, "joblessness" → unemployment rate

### Include Synonym Coverage

For key indicators in the dataset, identify common synonyms and create test cases using them:

| Official Name | Common Synonyms |
|---------------|-----------------|
| Consumer Price Index (CPI) | inflation, cost of living, price level |
| Gross Domestic Product (GDP) | economic output, economic growth, national income |
| Unemployment rate | jobless rate, joblessness |
| Balance of Payments | trade balance, current account |

---

## Example Test Cases (IMF Datasets)

### WEO — Simple Single Indicator

```yaml
- role: user
  content: Could you give me the population numbers for Mexico?
  target:
    indicator_selection:
      - dataset_id: IMF.RES:WEO
        dimensions:
          - dimension_name: INDICATOR
            values:
              - id: LP
                name: Population, Persons for countries / Index for country groups
          - dimension_name: COUNTRY
            values:
              - id: MEX
                name: Mexico
```

### CPI — Synonym Query with Multiple Indicator Dimensions

```yaml
- role: user
  content: Can you give me the retail price index data for edible products
           and non-alcoholic drinkables in Ecuador?
  target:
    indicator_selection:
      - dataset_id: IMF.STA:CPI
        dimensions:
          - dimension_name: INDEX_TYPE
            values:
              - id: CPI
                name: Consumer price index (CPI)
          - dimension_name: COICOP_1999
            values:
              - id: CP01
                name: Food and non-alcoholic beverages
          - dimension_name: COUNTRY
            values:
              - id: ECU
                name: Ecuador
```

Note how the query uses "retail price index" (→ CPI), "edible products and non-alcoholic drinkables" (→ Food and non-alcoholic beverages), and "Ecuador" (→ ECU). Testing synonym handling is critical.

---

## Key Takeaways

- LLM non-determinism means the same query can produce different results — systematic testing is essential, not optional
- Ground truth defines expected results (dataset, indicators, dimensions) for each test query
- Design test cases across categories: single indicator, multi-indicator, synonyms, ambiguous, cross-dataset
- **Precision** measures noise (extra results), **recall** measures completeness (missing results)
- StatGPT favors recall — it's better to find all relevant data with some extras than to miss important indicators
- Run queries multiple times to understand variance
- Write test cases from the user's perspective using natural language, not statistician terminology
- Iterate: test → analyze discrepancies → fix config → reindex → retest

---

## Check Your Understanding

Test your grasp of testing and validation before moving on.

<details>
<summary><strong>1. A test case for "What is GDP of France?" expects dataset IMF.RES:WEO, INDICATOR values including "Gross domestic product, constant prices", COUNTRY=FRA. The system returns WEO with GDP, GDPPC, and GDP_CONST for FRA. Is this acceptable?</strong></summary>

**Answer:** Yes — this is acceptable. Recall is high because the expected GDP items were found. Precision is slightly lower because GDPPC and GDP_CONST are extras that weren't in the target. Since StatGPT favors recall, returning extra related indicators is expected behavior — it's better to surface all GDP-related indicators than to miss one the user might need.

</details>

<details>
<summary><strong>2. Your ground truth target indicators are GDP and CPI. The system returned only GDP. Which metric is low — precision or recall?</strong></summary>

**Answer:** Recall is low — CPI was missed (false negative). Precision is 1.0 because everything the system returned (GDP) was correct. This is a problematic result because StatGPT is designed to favor recall. A missed indicator means the user gets an incomplete answer. Investigate why CPI wasn't found — likely a synonym mapping or indicator classification issue.

</details>

<details>
<summary><strong>3. You run the same query 3 times and get slightly different indicator sets each time. Is this a bug?</strong></summary>

**Answer:** No — this is expected LLM non-determinism. Even with `temperature: 0`, results can vary due to infrastructure-level variability (floating-point non-determinism, batching differences). This is exactly why the module recommends running queries multiple times. Evaluate the pattern across runs — if the core indicators appear consistently and only peripheral ones vary, the system is working as intended. If core indicators appear and disappear unpredictably, that signals a real problem.

</details>

<details>
<summary><strong>4. You just onboarded a new CPI dataset. Name three categories of test cases you should write.</strong></summary>

**Answer:** (1) **Single indicator queries** — e.g., "What is CPI for Germany?" Tests basic indicator retrieval. (2) **Synonym queries** — e.g., "What is inflation in Brazil?" Tests whether "inflation" maps correctly to CPI indicators. (3) **Cross-dataset queries** — e.g., "What is GDP?" Tests that a GDP query does *not* match the CPI dataset and instead routes to the correct dataset (like WEO). Cross-dataset cases catch misclassification and overly broad indexer descriptions.

</details>

---

## Practical Exercises

### Exercise 1: Write a Ground Truth Test Case

Your channel has the IMF BOP (Balance of Payments) dataset with these indicator dimensions:

| Dimension | Required | Sample Codelist Values |
|-----------|----------|----------------------|
| `INDICATOR` | Yes | "Goods, credit", "Goods, debit", "Services, credit", "Services, debit", "Current Account, Total, Net" |
| `BOP_ACCOUNTING_ENTRY` | Yes | "Credit", "Debit", "Balance" |

A user asks: *"What is the trade balance for Japan?"*

**Your task:** Write the ground truth test case YAML following the format shown earlier in this module (the WEO and CPI examples).

<details>
<summary><strong>Solution</strong></summary>

```yaml
- role: user
  content: What is the trade balance for Japan?
  target:
    indicator_selection:
      - dataset_id: IMF.STA:BOP
        dimensions:
          - dimension_name: INDICATOR
            values:
              - name: Goods, credit
              - name: Goods, debit
              - name: Services, credit
              - name: Services, debit
          - dimension_name: BOP_ACCOUNTING_ENTRY
            values:
              - name: Balance
          - dimension_name: COUNTRY
            values:
              - id: JP
                name: Japan
```

**Key decisions:**

- **"Trade balance" maps to goods and services indicators.** Trade balance = exports minus imports of goods and services. That means four INDICATOR values (goods credit/debit, services credit/debit), not just one.
- **Accounting entry should be "Balance" (net).** The user asked for the *balance*, not the raw credit/debit flows.
- **Multiple INDICATOR values are expected.** A reader might be tempted to pick a single indicator, but trade balance is an aggregate concept spanning multiple BOP line items.
- **"Current Account, Total, Net" is also acceptable.** "Trade balance" is ambiguous — it could refer to the narrower goods-and-services balance or the broader current account. If your test case includes this value, that's a valid interpretation. This is a good example of where ground truth should document acceptable alternatives.

> **Note:** Real test cases include both `id` and `name` for each value (e.g., `id: LP`, `name: Population...`). This exercise omits IDs because you don't have access to the full BOP codelist — in practice, you'd look up the exact IDs from the dataset structure in the Admin UI.

</details>

---

**Previous:** [Module 06 — Indexing, Deduplication & Operations](06-indexing-and-operations.md) | **Next:** [Module 08 — End-to-End Walkthrough](08-end-to-end-walkthrough.md)
