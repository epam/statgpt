# Module 06: Indexing, Deduplication & Operations

## What You'll Learn

- What indexing does and why it's needed
- When to reindex datasets — and how the system detects this automatically
- How to run and monitor indexing via the Admin UI
- How to validate indexing results using indicator counts
- What deduplication is and when to use it
- Auto-update — automatic detection and reindexing of upstream changes
- Cost awareness — indexing uses LLM tokens
- Channel import/export and job monitoring

---

## What Indexing Does

StatGPT uses multiple search strategies to find relevant indicators when a user asks a question:

- **Semantic search** — Finds indicators by meaning similarity (e.g., "economic growth" matches "GDP")
- **Keyword (fulltext) search** — Finds indicators by exact term matching (e.g., "CPI" matches "Consumer Price Index (CPI)")

Both strategies require a **search index** — a pre-computed representation of all code list items across the dataset's indicator dimensions. Indexing is the process of creating this representation.

### What Gets Indexed

For each dataset, the indexer processes:
- **Code list items** from all indicator dimensions — their IDs, names, and (optionally) descriptions

The indexer creates embeddings (vector representations) for semantic search and text entries for fulltext search. The `unpack` setting controls whether packed indicator names are decomposed into individual concepts before indexing (see [Module 03b](03b-indicator-configuration.md#packed-vs-unpacked-indicators)).

### Why Indexing Is Needed

Without indexing, StatGPT would have no way to match user queries to specific indicators. The search index is what enables a question like *"What was inflation in Germany?"* to find the indicator *"Consumer price index (CPI), All items"* in the CPI dataset.

---

## When to Reindex

StatGPT uses an **indexing hash** to automatically determine whether a configuration change requires reindexing.
When you save a dataset configuration, the system compares the hash of indexing-relevant fields against the last
indexed version. If the hash changed, the dataset status shows **NEEDS_REINDEX** — you must trigger reindexing
manually. If the hash is unchanged, the change is applied silently without reindexing.

### Changes That Require Reindexing

These fields are **indexing-relevant** — changing them alters the search index:

| Field Changed | Example | System Behavior |
|---------------|---------|-----------------|
| `dimensionType` on any dimension | Reclassifying INDICATOR ↔ NON_INDICATOR | Hash changes → `NEEDS_REINDEX` |
| `alias` on a dimension | Changing the country alias string | Hash changes → `NEEDS_REINDEX` |
| `virtual` dimension config | Adding or modifying a virtual dimension | Hash changes → `NEEDS_REINDEX` |
| `processorId` on SPECIAL dimension | Changing the LHCL processor reference | Hash changes → `NEEDS_REINDEX` |
| `subtype` on NON_INDICATOR | Changing REGION ↔ FREQUENCY | Hash changes → `NEEDS_REINDEX` |
| `indexer.indicator.unpack` | Switching packed ↔ unpacked | Hash changes → `NEEDS_REINDEX` |
| `indexer.indicator.superPrimary` | Switching primary concatenation from 1 to 3 dimensions | Hash changes → `NEEDS_REINDEX` |
| `indexer.indicator.annotations` | Adding or modifying indicator annotation config | Hash changes → `NEEDS_REINDEX` |
| Upstream code list items changed | Provider added/renamed/removed indicators | Detected by [auto-update](#auto-update) |
| Upstream SDMX structure changed | New dataflow version with different dimensions | Detected by [auto-update](#auto-update) |

### Changes That Do NOT Require Reindexing

These fields are **display-only** — changing them is applied immediately without reindexing:

| Field Changed | Example |
|---------------|---------|
| `isOfficial` | Toggling official status |
| `citation` (provider, url, description) | Updating attribution text |
| `pinnedColumns` | Reordering table columns |
| `isRequired` on a dimension | Changing required ↔ optional |
| `defaultQueries` on a dimension | Adjusting default time range |
| `allValues` on a dimension | Adding/changing the "all countries" value |
| `includeAttributes` | Adding/removing SDMX attributes |
| `useTitleFromSrc` | Switching title source |

### Changes That Never Need Reindexing

- Only observation values changed (data updates without structural changes)
- Channel configuration changed (agent settings, conversation starters, etc.)
- Glossary terms were added or modified

---

## Indexing via the Admin UI

### Reindexing a Single Dataset

1. Navigate to the channel detail page
2. Find the dataset in the list
3. Click the **Reindex** button for that dataset

### Reindexing All Datasets in a Channel

1. Navigate to the channel detail page
2. Click the **Reindex All** button at the top of the datasets list

This queues reindexing jobs for every dataset in the channel.

### Monitoring Indexing Status

Each dataset shows its indexing status in the "Status" column:

| Status | Meaning |
|--------|---------|
| **Not Started** | Dataset has never been indexed |
| **Queued** | Waiting in the queue for the indexing job to start |
| **In Progress** | Indexing is currently running |
| **Completed** | Successfully indexed — the dataset is searchable |
| **Failed** | Indexing failed — check the configuration or retry |

**If indexing fails:**
1. Check the dataset configuration for errors (invalid dimension settings, missing required fields)
2. Verify the data source is accessible
3. Try reindexing again — transient errors (network timeouts, API rate limits) may resolve on retry
4. If the problem persists, review the dataset's SDMX metadata for issues (see [Module 02](02-dataset-assessment.md))

---

## Deduplication

### What It Is

During indexing, some code list items may produce duplicate or near-duplicate entries in the search index. This can happen when:
- Multiple indicator dimensions have overlapping values
- Code list hierarchies produce parent and child items with similar embeddings
- Packed indicators generate similar unpacked components

Deduplication identifies and removes these redundant entries, keeping the index clean and improving search precision.

### When to Run It

Run deduplication:
- **After initial indexing** of a dataset
- **After reindexing** if you suspect duplicate entries are affecting search quality
- **When search results show noise** — extra, irrelevant indicators appearing in results

Deduplication is available as a separate operation in the Admin UI / CLI.

---

## Validating Indexing Results

After indexing completes with status **Completed**, verify that the right data was indexed.

### Per-Dataset Indicator Counts

The most reliable validation is checking per-dataset indicator counts via the **Available Datasets** tool in the chat
interface. This requires `includeIndicatorCount: true` in the Available Datasets tool configuration
(see [Module 05](05-data-sources-and-channels.md#available-datasets-tool)).

When enabled, the tool output includes:
- Per dataset: `* Number of indicators: {count}`
- Summary: `Total number of indicators: {sum}`

**What to check:**
- A dataset with **0 indicators** after indexing means something went wrong — check the dataset configuration
  (incorrect `dimensionType` on indicator dimensions, etc.)
- Compare the indicator count against the expected number of code list items in the indicator dimensions
- A significant drop in count after reindexing may indicate a configuration regression

### Channel-Wide Totals via Admin API

The admin API provides channel-wide aggregates:

```
GET /channels/{channel_id}/index-status?scope=latest_completed_versions
```

This returns total `indicator_dimensions_size` (indexed indicators) and `indicator_dimensions_duplicate_count`
(duplicates before deduplication) across all datasets in the channel.

---

## Cost Awareness

Indexing uses LLM tokens for embedding generation:

- Each code list item is sent to the embedding model to generate a vector representation
- Datasets with many indicator values (thousands of code list items) consume more tokens
- The embedding model is configured per channel (e.g., `text-embedding-3-large`)

**Cost factors:**
- Number of code list items across all indicator dimensions
- Whether `unpack: true` (may increase the number of indexed items for packed indicators)
- Reindexing the entire channel multiplies the cost by the number of datasets

**Best practices:**
- Reindex only the datasets that changed, not the entire channel
- Verify dataset configuration before indexing to avoid failed jobs that waste tokens
- Be aware that a full channel reindex can be expensive for channels with many large datasets

---

## Import/Export

### Exporting a Channel

Export creates a dump of a channel's configuration, datasets, and indexes:

1. Navigate to the channel context menu
2. Click **Export**
3. A job is created — monitor progress on the Jobs page
4. Download the export artifact when the job completes

Exports are useful for:
- Backing up a channel before making changes
- Moving a channel configuration between environments (dev → staging → production)
- Sharing configurations with other administrators

### Importing a Channel

Import loads a channel dump, creating or updating the channel, its datasets, and data sources:

1. Navigate to the Channels list page
2. Click **Import**
3. Upload the channel dump file
4. Configure import options:
   - **Remove channel with the same ID** — If enabled, deletes the existing channel before importing. If disabled, import fails if the channel already exists
   - **Update datasets** — If enabled, updates datasets to the version in the import file
   - **Update data sources** — If enabled, updates data sources to the version in the import file
5. Start the import

### Jobs Page

Both import and export operations create jobs:

1. Access the Jobs page from the channel context menu → **Jobs**
2. Review job status (Queued, In Progress, Completed, Failed)
3. Download artifacts (export dumps, import logs)

---

## Auto-Update

Auto-update automatically checks upstream SDMX data sources for changes and reindexes datasets when needed. This
eliminates the need to manually monitor provider releases and trigger reindexing.

### How It Works

The auto-update system runs as a batch job that:

1. **Discovers** all channels with auto-update enabled
2. **Resolves** each dataset's URN against the upstream SDMX registry (e.g., resolves `"latest"` to the current
   concrete version)
3. **Compares** the upstream structure and data against the last indexed version
4. **Acts** based on what changed — reindex, update config, or do nothing
5. **Deduplicates** any channels that had reindexed datasets (batch workflow only — individual API-triggered auto-updates require manual deduplication)

### Enabling Auto-Update

Auto-update is a **channel-level** opt-in. Set `allowAutoUpdate: true` on the Data Query tool configuration
(see [Module 05](05-data-sources-and-channels.md#data-query-tool)):

```yaml
dataQuery:
  type: DATA_QUERY
  details:
    allowAutoUpdate: true
```

**Important:** Auto-update only makes sense when datasets use `version: "latest"` in their URN. With pinned versions,
the resolved config never changes, and every auto-update run results in `NO_CHANGES`.

### Auto-Update Outcomes

Each dataset in an auto-update run produces one of these outcomes:

| Outcome | Meaning | Action Taken |
|---------|---------|--------------|
| `NO_CHANGES` | Upstream data and structure are identical to the last indexed version | Nothing |
| `CONFIG_UPDATED` | The resolved version pointer changed but the actual data is identical | Lightweight config-only version created (no reindex) |
| `REINDEX_TRIGGERED` | Upstream structure or data changed | Full reindex triggered, followed by deduplication |
| `CONFIG_INCOMPATIBLE` | The upstream version's config fails validation | Nothing — investigate the new version manually |
| `NO_COMPLETED_VERSION` | The dataset has never been successfully indexed | Nothing — index it manually first |

### Scheduling

The auto-update script does not have a built-in scheduler. It is invoked externally:

- **Production:** A Kubernetes CronJob (or similar scheduler) runs the admin container with `ADMIN_MODE=AUTO_UPDATE`
- **Manual trigger (per-dataset):** Admin API `POST /{channel_id}/datasets/{dataset_id}/versions/auto-update-jobs`
- **Development:** `make statgpt_auto_update`

The scheduling frequency depends on how often upstream providers publish new versions — nightly or weekly is typical.

---

## Operational Workflow Summary

Typical workflow when onboarding a new dataset:

1. **Assess** the dataset metadata (Module 02)
2. **Configure** the dataset in the Admin UI (Module 04)
3. **Add** the dataset to a channel (Module 05)
4. **Update channel** Named Entity types if new NON_INDICATOR dimensions were added (Module 03/05)
5. **Index** the dataset
6. **Monitor** indexing status until "Completed"
7. **Validate** — check indicator counts via Available Datasets tool or admin API
8. **Deduplicate** if needed
9. **Test** the dataset with representative queries (Module 07)
10. **Iterate** — fix configuration issues and reindex if test results are unsatisfactory

**Ongoing maintenance:** If the channel has `allowAutoUpdate: true` and datasets use `version: "latest"`, auto-update
handles upstream changes automatically. Otherwise, monitor provider releases and reindex manually when needed.

---

## Key Takeaways

- Indexing creates the search index that enables indicator discovery — without it, the dataset is not searchable
- The **indexing hash** automatically detects which config changes require reindexing — you don't have to guess
- Indexing-relevant fields (`dimensionType`, `alias`, `indexer.*`, etc.) trigger `NEEDS_REINDEX`; display-only fields (`citation`, `pinnedColumns`, `isRequired`) are applied silently
- **Validate** indexing results using indicator counts (`includeIndicatorCount: true`) — a count of 0 means something went wrong
- Deduplication cleans up redundant index entries — run it after indexing
- **Auto-update** (`allowAutoUpdate: true`) automatically detects upstream changes and reindexes when needed — pair it with `version: "latest"` in dataset URNs
- Indexing costs LLM tokens — reindex selectively, not the entire channel
- Import/Export enables channel portability between environments

---

## Check Your Understanding

Test your grasp of indexing and operations before moving on.

<details>
<summary><strong>1. You changed the <code>pinnedColumns</code> order in a dataset config and saved. Do you need to reindex?</strong></summary>

**Answer:** No. `pinnedColumns` is a display-only field — the indexing hash doesn't change, so the system applies it silently without reindexing. See the "Changes That Do NOT Require Reindexing" table above.

</details>

<details>
<summary><strong>2. You reclassified a dimension from <code>NON_INDICATOR</code> to <code>INDICATOR</code>. What happens when you save?</strong></summary>

**Answer:** The indexing hash changes because `dimensionType` is an indexing-relevant field. The dataset status shows **NEEDS_REINDEX**. You must trigger reindexing manually so the dimension's values get added to the search index.

</details>

<details>
<summary><strong>3. A channel has <code>allowAutoUpdate: true</code>, but one dataset uses <code>version: "21.0.0"</code> instead of <code>"latest"</code>. The provider releases version 22.0.0. Will auto-update detect this?</strong></summary>

**Answer:** No. With a pinned version, `resolve_config()` always returns `"21.0.0"` — the same as last time. The auto-update result will be `NO_CHANGES`. Change the URN to `version: "latest"` for auto-update to work.

</details>

<details>
<summary><strong>4. Indexing completed with status "Completed" for a new dataset, but users can't find any indicators from it. How do you diagnose this?</strong></summary>

**Answer:** Check the indicator count. Enable `includeIndicatorCount: true` on the Available Datasets tool, then trigger it in chat. If the dataset shows 0 indicators, the indexing technically succeeded but produced no index entries — likely due to missing or incorrect `dimensionType: "INDICATOR"` on indicator dimensions.

</details>

<details>
<summary><strong>5. An auto-update job for a WEO dataset returns <code>CONFIG_UPDATED</code>. What happened and what was the result?</strong></summary>

**Answer:** The resolved URN version changed (e.g., the provider published a new version of the dataflow), but the actual data structure and content are identical to the last indexed version. The system created a lightweight config-only version pointing to the existing index data — no reindex was triggered, no tokens were consumed.

</details>

---

**Previous:** [Module 05 — Data Sources & Channel Configuration](05-data-sources-and-channels.md) | **Next:** [Module 07 — Testing & Validation](07-testing-and-validation.md)
