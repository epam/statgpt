# ⚠️ System Limitations

Constraints of the current StatGPT implementation.

## 📋 Summary

| #                                                      | Limitation                                                 | Area                | Impact                                                                          |
|--------------------------------------------------------|------------------------------------------------------------|---------------------|---------------------------------------------------------------------------------|
| [1](#-1-database-lock-during-reindexing)               | Index deletion holds a database lock during reindexing     | Indexing/operations | Index operations on a channel serialize; a contended job fails on lock timeout   |
| [2](#-2-only-codelist-backed-dimensions-are-supported) | Only codelist-backed (enumerated) dimensions are supported  | Dataset onboarding  | A dataset with a free-text dimension stays `offline`                            |

## 1. Database lock during reindexing

Reindexing deletes the previous index first, and that deletion takes the lock. It removes the dataset's metadata rows,
then clears the documents left without a metadata reference — one transaction over the channel's shared document tables,
guarded by a PostgreSQL advisory lock keyed on the `(channel, dataset)` pair.

Index-modifying operations on a channel therefore serialize:

| Operation                                          | Behaviour under contention                                                    |
|----------------------------------------------------|-------------------------------------------------------------------------------|
| **Recalculate all indexes** on a large channel     | Datasets queue at the database level; wall-clock time grows with channel size  |
| Reindex triggered while another reindex is running  | The second job waits for the lock                                             |
| Deduplication, import or export during a reindex   | Contends on the same document tables                                          |

The wait is bounded by a configurable advisory-lock timeout. A job that does not acquire the lock in time **fails**
rather than waiting indefinitely: the latest index version is marked failed, the previously completed version keeps
being served, no data is lost.

**Guidance:**

- Reindex one dataset at a time; prefer per-dataset **Recalculate indexes** over **Recalculate all indexes**.
- Do not run deduplication, import or export concurrently with a reindex on the same channel.
- Schedule full-channel reindexing outside peak query hours.
- On a lock timeout, retry the dataset once the running job has finished.

**See also:** [Module 06 — Indexing & Operations](../learning/administration/06-indexing-and-operations.md#known-limitations),
[Data Query Internals — Reindex lifecycle](./data-query-internals.md#reindex-lifecycle).

## 2. Only codelist-backed dimensions are supported

Every dimension must be **enumerated** — its representation (local, or the core representation of its concept) must
reference a codelist. The single `TIME_PERIOD` dimension is the only exception.

**Non-enumerated dimensions are not supported.** A free-text dimension is valid SDMX:

```xml
<structure:Dimension id="AREA_CODE" position="1">
  <structure:ConceptIdentity>
    <Ref id="AREA_CODE" class="Concept"/>
  </structure:ConceptIdentity>
  <structure:LocalRepresentation>
    <structure:TextFormat textType="String"/>
  </structure:LocalRepresentation>
</structure:Dimension>
```

StatGPT cannot construct it: there is no codelist to index against.

**Symptoms:**

| Where          | What you see                                                                                 |
|----------------|----------------------------------------------------------------------------------------------|
| Dataset status | `offline` — *"Failed to create dimensions from the loaded structure message."*                |
| Auto-update    | `FAILED`, no index version produced; repeats on every scheduled run                          |
| Backend log    | `ValueError` — a code list dimension could only be created from a `Codelist` type             |

Deterministic: it reproduces on every load. A throttled provider can return an empty codelist and produce a similar
"no codelist" error for a different reason — a retry that fails identically points to this limitation.

## 🔗 Related Documentation

- [SDMX Compatibility & Requirements](./sdmx-compatibility.md) — what a provider's metadata must satisfy
- [Data Query Internals](./data-query-internals.md) — the indexing pipeline in engineering detail
- [Admin Guide](../guides/admin-guide.md) — the Admin UI operations referenced above
- [Admin Learning Course](../learning/administration/README.md) — dataset onboarding end to end
