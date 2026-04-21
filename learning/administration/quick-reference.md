# Quick-Reference Card: Dataset Onboarding

A one-page reference for common decisions during dataset onboarding. For full explanations, see the linked modules.

---

## Dimension Classification Decision Tree

For each dimension in the dataset, follow this flowchart:

```
Is it the time dimension?
├── Yes → TIME_PERIOD (auto-detected; configure default queries)
└── No ↓

Is it the country/region dimension?
├── Yes → NON_INDICATOR (dimensionType: "NON_INDICATOR", subtype: "REGION", + alias)
└── No ↓

Is it a frequency dimension?
├── Yes → NON_INDICATOR (dimensionType: "NON_INDICATOR", subtype: "FREQUENCY")
└── No ↓

Does it map to an existing Named Entity type?
├── Yes → NON_INDICATOR
└── No ↓

Would an average person understand the codelist values?
├── Yes → NON_INDICATOR (add a new Named Entity type if needed)
└── No → INDICATOR (dimensionType: "INDICATOR")
```

When in doubt, classify as **INDICATOR**. See [Module 03a](03a-dimension-types.md).

---

## Packed vs. Unpacked Decision Rule

Look at the **important** indicator dimensions (the ones describing *what* is being measured):

| Codelist Values | Setting |
|---|---|
| Comma-separated multi-concept strings (e.g., `"GDP, constant prices, Percent change"`) | `unpack: true` |
| Single-concept values (e.g., `"Consumer price index (CPI)"`) | `unpack: false` |
| Commas in natural English (e.g., `"exchange rate, period average"`) | `unpack: false` |

**Quick test:** Does the comma separate independent concepts that could each be a separate dimension? If yes → packed. If it's natural English phrasing → not packed.

See [Module 03b](03b-indicator-configuration.md#packed-vs-unpacked-indicators).

---

## Required vs. Optional Indicator Dimensions

> *"If the user's query specifies a filter for this dimension, should it be enough to trigger a query against this dataset?"*

| Answer | Classification |
|---|---|
| **Yes** — filtering by this dimension alone produces a sensible query | Required (`isRequired: true`) |
| **No** — this dimension is supplementary, not sufficient on its own | Optional (`isRequired: false` or omitted) |

A dataset query is **only executed** when the user's query filters on at least one of the dataset's required dimensions. Queries that don't match any required dimension are skipped.

**Rules:** Only INDICATOR dimensions can be marked required. Every dataset must have at least one required indicator dimension.

See [Module 03b](03b-indicator-configuration.md#required-vs-optional-indicator-dimensions).

---

## Dataset YAML Template

```yaml
# --- Identity ---
urn:                                       # Pre-filled from wizard
  agency_id: "AGENCY.DEPT"
  resource_id: "DATAFLOW"
  version: "latest"                        # Recommended: always track current version
citation:
  provider: AGENCY.DEPT                    # Data provider
  url: https://...                         # Link to dataset page
  description: &ds_description >           # Use null if source has good description
    Dataset description text...

# --- Flags ---
isOfficial: false                          # true only for national statistics offices
useTitleFromSrc: true                      # false if you need a custom title

# --- Dimensions ---
dimensions:
  INDICATOR:
    dimensionType: "INDICATOR"
    isRequired: true                       # At least one indicator must be required
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
      - values: ["2020", "2025"]
        operator: "between"

# --- Timestamps ---
updatedAt:                                 # How to determine last updated date
  - source: "attribute"
    field: "UPDATE_DATE"
    formats: ["%Y-%m-%dT%H:%M:%S.%fZ"]
  - source: "annotation"
    field: "lastUpdatedAt"
  - source: "citation"
    field: "last_updated"

# --- Display ---
pinnedColumns:                             # Least → most important
  - FREQUENCY_Name
  - COUNTRY_Name
  - INDICATOR_Name                         # Main indicator last
includeAttributes:                         # SDMX attributes for agent context
  - SCALE
  - UNIT

# --- Indexing ---
indexer:
  indicator:
    unpack: false                          # true for packed indicators
    useCodeListDescription: false          # true if code list descriptions are meaningful
  description: *ds_description             # Must be non-empty
```

See [Module 04](04-dataset-configuration.md) for field-by-field details.

---

## Onboarding Checklist

### Phase 1: Assessment ([Module 02](02-dataset-assessment.md))

- [ ] **Blockers clear:** Meaningful code list names, English localization, API < 1 sec, Available Constraint works
- [ ] **Warnings documented:** Duplicates < 10%, borderline performance, sparse data
- [ ] **Business value confirmed:** Fills a gap, target users identified, FAQ coverage

### Phase 2: Dimension Classification ([Module 03a](03a-dimension-types.md))

- [ ] Every dimension in the `dimensions` map has a `dimensionType`
- [ ] Named Entity types added for all NON_INDICATOR dimensions
- [ ] Country dimension `alias` matches channel's `countryNamedEntityType`

### Phase 3: Indicator Configuration ([Module 03b](03b-indicator-configuration.md))

- [ ] At least one indicator dimension has `isRequired: true`
- [ ] Packed/unpacked determined; `unpack` set correctly
- [ ] `useCodeListDescription` set based on code list quality

### Phase 4: Dataset Configuration ([Module 04](04-dataset-configuration.md))

- [ ] All YAML fields filled (citation, dimensions, pinnedColumns, indexer)
- [ ] `indexer.description` is non-empty
- [ ] `pinnedColumns` ordered least → most important, correct `_Name` casing

### Phase 5: Data Source & Channel ([Module 05](05-data-sources-and-channels.md))

- [ ] Data Source exists for the provider
- [ ] Dataset linked to channel
- [ ] Channel Named Entity types updated if new NON_INDICATOR dimensions added

### Phase 6: Indexing ([Module 06](06-indexing-and-operations.md))

- [ ] Dataset indexed successfully (status: Finished)
- [ ] Deduplication run if needed

### Phase 7: Testing ([Module 07](07-testing-and-validation.md))

- [ ] Verify indicator counts via Available Datasets tool (non-zero for the new dataset)
- [ ] Test cases cover: single indicator, multi-indicator, synonyms, edge cases
- [ ] Ground truth defined for each test case
- [ ] Queries run 2-3 times to check variance
- [ ] Recall acceptable (all expected indicators found)
- [ ] Iterate if needed: fix config → reindex → retest

### Ongoing: Auto-Update ([Module 06](06-indexing-and-operations.md#auto-update))

- [ ] If channel has `allowAutoUpdate: true` and dataset uses `version: "latest"`, auto-update handles ongoing maintenance
