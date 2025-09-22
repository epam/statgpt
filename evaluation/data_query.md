# Methodology for Evaluating Data Query

This document outlines the methodology for evaluating quality of transforming natural language queries into SDMX data queries, focusing on indicator selection.

## Data Query Evaluation Metrics (Indicator Selection Eval)

### Evaluation Approach

- **End-to-End Evaluation:**  
  We evaluate the final set of indicators (and other dimension terms) selected by the system in response to a data query. This measures the quality of the system’s indicator selection, reflecting the user experience in real-world data exploration scenarios.

- **Term Matching:**  
  The evaluation checks if the selected terms (indicators, countries, etc.) match the target terms specified in the test case. Each term is defined by both its ID and name.

- **Per-Dimension Analysis:**  
  Terms are grouped by their dimension (e.g., INDICATOR, COUNTRY). Evaluation is performed separately for each dimension.

### Sample Test Case

We maintain all test cases in YAML format. Below is an example of a test case for one of the IMF datasets.

```yaml
id: c48d7624-d376-48ca-b2d8-386999befb45
name: could_you_give_me_the_population_numbers_for_mexico
tags:
- imf
- weo
comments: ''
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

This test case specifies that for the query "Could you give me the population numbers for Mexico?", the expected 
indicators are "Population, Persons for countries / Index for country groups" (ID: LP) and the country is "Mexico" 
(ID: MEX) from the IMF WEO dataset.

### Metrics

- **True Positives (TP):**  
  Terms that are present in both the system’s selection and the target set.

- **False Positives (FP):**  
  Terms selected by the system but not present in the target set.

- **False Negatives (FN):**  
  Terms present in the target set but not selected by the system.

- **Precision:**  
  $$
  \text{Precision} = \frac{|\text{TP}|}{|\text{TP}| + |\text{FP}|}
  $$
  Measures the fraction of selected terms that are correct.

- **Recall:**  
  $$
  \text{Recall} = \frac{|\text{TP}|}{|\text{TP}| + |\text{FN}|}
  $$
  Measures the fraction of target terms that were successfully selected.

- **Macro-Averaged Metrics:**  
  Precision and recall are computed for each dimension, then averaged across all dimensions to obtain macro precision and macro recall.

### Test Case Metrics

- For each test case, the following are reported:
  - **Per-dimension precision and recall** (for each dimension such as INDICATOR, COUNTRY, etc.)
  - **Macro precision and recall** (averaged across all dimensions)
  - **Detailed breakdown** of true positives, false positives, and false negatives for each dimension

- If the target set for a dimension is absent, all selected terms are counted as false positives for that dimension.

### Excel Report

- **Overview Sheet:**  
  Each row corresponds to a single test case. Columns include:
  - `macro recall`: Macro-averaged recall across all dimensions
  - `macro precision`: Macro-averaged precision across all dimensions
  - `indicator selection details`: Detailed breakdown per dimension, including lists of true positives, false positives, and false negatives

- **Details in Excel Cell:**  
  For each dimension, the following format is used:

  ```
  [recall: 0.75, precision: 0.80]
  True Positives [2]
    * GDP: gross domestic product
    * GDPPC: GDP per capita
  False Negatives [0]
  False Positives [1]
    * GDP_CONST: gross domestic product constant prices
  ```

- **Dimensions Not in Target:**  
  If the system selects terms for dimensions not present in the target, these are listed separately under "dimensions not in target".

### Dataset Metrics

- **Aggregated Metrics:**  
  Macro precision and recall are averaged over all test cases in the dataset and reported in the "Statistics" sheet under "Data Query Metrics".

### Example

Suppose the target and selected terms for a test case are:

- **Target (INDICATOR):** GDP, GDPPC
- **Selected (INDICATOR):** GDP, GDPPC, GDP_CONST

Then:

- True Positives: GDP, GDPPC
- False Positives: GDP_CONST
- False Negatives: (none)

Precision = 2 / (2 + 1) = 0.67  
Recall = 2 / (2 + 0) = 1.0

### Notes

- The evaluation does not currently distinguish between an empty target and an absent target for a dimension.
- All metrics are computed using both the term ID and name for exact matching.
- The evaluation supports extensibility to other dimensions beyond indicators (e.g., COUNTRY).
