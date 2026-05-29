# Config sourcing, guide structure, and screenshot inventory

Read this before Phase 4 (rewriting the guide).

## Sourcing configuration YAML

The guide's YAML examples must be **real**, not invented, and in the **admin (camelCase) format** the
admin UI actually stores — which differs from the seed files.

- **Seed files** live in `statgpt-backend/configurations/clients/sample/` and are **snake_case**
  (`data_sources.yaml`, `datasets/*.yaml`, `channels.yaml`, `tools.yaml`, `glossaries/*.csv`). Use
  them for the *content* (ids, urls, descriptions, dimension lists, tool descriptions, glossary terms).
- **The admin stores camelCase.** Translate seed snake_case → admin camelCase. When unsure of the exact
  shape or a new field, the **live "Configure"/"Edit" editor is the source of truth** — read it with
  Monaco `getValue()` (see capture-pipeline.md). Abbreviate very long descriptions in the guide with
  a `# ...` comment; keep the structure faithful.

### Data source config (the `details` content shown in the Configuration editor)

Keys seen: `apiKey`, `locale`, `authConfig`, `rateLimits`, `sdmxConfig` (`id`, `url`, `name`,
`headers` per resource type, `supports`, `versions`, `dataContentType`), `authEnabled`, `sdmx1Source`,
`apiKeyHeader`, `attributesUrl`, `annotationsUrl`, `dataExplorerUrl`, `providerDiscovery`. The
connector (`SDMX21` / `QH_SDMX21` / `PROXY_SDMX30`) is chosen in the wizard's Properties step.

### Dataset config — the **`dimensions` map** is the headline schema

Old flat fields (`indicatorDimensions`, `countryDimension`, `countryDimensionAlias`,
`dimensionDefaultQueries`, `indicatorDimensionsRequiredForQuery`) are replaced by a **`dimensions:`
map**, one entry per dimension:

```yaml
dimensions:
  COUNTRY:      { dimensionType: NON_INDICATOR, subtype: REGION, alias: Country/Reference area,
                  isRequired: false, allValues: {id: ALL_COUNTRIES, name: "...", description: "..."} }
  FREQUENCY:    { dimensionType: NON_INDICATOR, subtype: FREQUENCY, isRequired: false }
  INDICATOR:    { dimensionType: INDICATOR, isRequired: true }
  TIME_PERIOD:  { dimensionType: TIME_PERIOD, isRequired: false,
                  defaultQueries: [ {values: ["-5y","+2y"], operator: between} ] }
```

`dimensionType` is `INDICATOR` / `NON_INDICATOR` / `TIME_PERIOD`. Plus: `urn` ({version, agencyId,
resourceId}), `indexer.indicator` ({unpack, annotations, superPrimary, useCodeListDescription}),
`indexer.description`, `citation` ({url, provider, description}), `updatedAt` (list of {field, source,
formats}), `isOfficial`, `pinnedColumns`, `useTitleFromSrc`, `includeAttributes`. Reference learning
Modules **03a** (dimension types), **03b** (indicators), **04** (dataset config).

### Channel config — new fields and the tool set

`locale`, `conversationStarters` ({introText, title, inputPlaceholder, buttons:[{title,text}]}),
`onboarding`, `namedEntityTypes`, `countryNamedEntityType`, `supremeAgent`
({name, domain, terminologyDomain, languageInstructions, llmModelConfig}),
`outOfScope` ({domain, useGeneralTopicsBlacklist, llmModelConfig}), `tokenUsage`
({debugOnly, stageName}). Tools: `availableDatasets`, **`datasetStructure` (`DATASET_STRUCTURE`, the
newer tool)**, `dataQuery`, `availableTerms`, `termDefinitions`. `dataQuery.details` now has
`allowAutoUpdate: true`, `hybridSearchConfig` ({namedEntitiesToRemove, prompts.relevancyPrompts}),
`indexerVersion`/`indicatorSelectionVersion: hybrid`, `llmModels` (per-stage), and a `mergedPythonCode`
attachment. Build this from `channels.yaml` + `tools.yaml`. Reference learning Module **05**.

## Guide structure (`guides/admin-guide.md`)

1. **Administrator App** + intro to the left nav.
2. **Concepts** — Data Source, Dataset, Channel, plus *index version* and *auto-update*.
3. **Data Sources** — list → add (Properties → Configuration) → edit/Configure. Data-source YAML.
4. **Datasets** — list + row menu → 4-step add wizard (Source → Provider → Dataflow → Configuration) →
   edit. The `dimensions` schema; link the learning course.
5. **Channels** — list (+ Import) + context menu → Configure (YAML) → **channel datasets page**
   (toolbar: Deduplicate statistics / Export / Recalculate all indexes ▾ / + Add) → per-dataset menu →
   **Versions** → **Auto update jobs** → indexing (Recalculate / Sequential vs Parallel / Deduplicate) →
   Glossary → Import/Export & Jobs.
6. **Audit Logs**.
7. Related resources / learning-course link.

Add a Table of Contents after the intro. Fix broken image links. Keep every cross-link resolvable
(this repo has `architecture/` and `learning/administration/` but **no** `deployment/` dir).

## Screenshot inventory (filenames → what the badges point to)

Adjust to scope. Each list/menu screen filtered to sample content.

- `ds-list` (Add, filter, row ⋯) · `ds-add-properties` (Name, connector, Next) ·
  `ds-add-config` (editor, Finish) · `ds-configure` (editor, Save)
- `datasets-list` (Add, filter, row ⋯) · `datasets-row-menu` (Edit/Delete) ·
  `dataset-add-source` / `dataset-add-provider` / `dataset-add-dataflow` (select + Next) ·
  `dataset-add-config` (the `dimensions` block, Finish) · `dataset-edit-config` (editor, Save)
- `channels-list` (Import, Add, row ⋯) · `channel-menu` (Configure/Glossary/Jobs/Delete/Export) ·
  `channel-configure` (editor, Save) · `channel-details` (toolbar: Deduplicate/Export/Recalculate/Add) ·
  `channel-dataset-menu` (Edit/Auto update jobs/Versions/Recalculate/Delete)
- `dataset-versions` (Status, Creation Reason) · `dataset-auto-update-jobs` (Result, Updated At) ·
  `channel-recalc-dropdown` (Sequential/Parallel) · `channel-deduplicate` (stats dialog)
- `glossary-page` (Add Term, Source/Domain) · `glossary-add-term` (Term/Definition/Source/Domain) ·
  `glossary-term-menu` (Edit/Delete — note: delete is immediate)
- `channel-import` (drop zone, the 3 toggles, Import) · `channel-jobs-download` (Type column +
  the Export/download row action — one shot covers the jobs list and the download)
- `audit-logs` (Action, Entity name; **redact the Initiated/email column**)

## Shipping (only if asked)

Branch (e.g. `feat/updated-admin-guide`); stage only `guides/admin-guide.md` + `guides/content/admin-guide/*.png`
(not stray local files); commit with a Conventional-Commits title (e.g. `docs: ...`); push; open a PR
against the repo's default branch using `.github/pull_request_template.md`. The repo enforces a
Conventional-Commits PR title. Don't delete now-orphaned old images without asking.
