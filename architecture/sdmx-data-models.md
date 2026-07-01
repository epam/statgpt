# SDMX Data Models & StatGPT Support

This document describes the SDMX data-model patterns StatGPT encounters across providers and
which of them StatGPT supports. It complements the [SDMX Compatibility](./sdmx-compatibility.md)
requirements.

## Overview

Across SDMX providers there are three data models. StatGPT supports only the **conventional
(multi-indicator dataflow)** model — where the indicator is a dimension inside one broad
dataflow, which is what StatGPT's indicator search resolves and filters within (see
[Data Query & Hybrid Search](./data-query-hybrid-search.md)). The **shared DSD** and
**indicator-per-dataflow** models — where the indicator is instead encoded by *which dataflow
(or table)* you pick — are **not supported yet**.

| # | Data model | Indicator is selected by… | Example providers | Supported |
|---|------------|---------------------------|-------------------|:---------:|
| 1 | **Conventional (multi-indicator dataflow)** | a dimension *inside* one broad dataflow | IMF, BIS | ✅ Yes |
| 2 | **Shared DSD** | *which dataflow* (one DSD split across many per-country / per-table dataflows) | OECD | ❌ Not yet |
| 3 | **Indicator-per-dataflow (dedicated DSD per dataset)** | *which dataflow* (one narrow table = one DSD) | Eurostat, ISTAT, ABS, ILO | ❌ Not yet |

---

## 1. Conventional (multi-indicator dataflow) — ✅ Supported

A dataset is a **single broad dataflow that holds many indicators**.

**Shape:**

- A relatively small number of dataflows.
- Each dataflow exposes a broad indicator/measure dimension whose code list holds the
  individual indicators.
- One DSD may back one or several such broad dataflows.

**Examples:** IMF, BIS.

**Why it works:** the indicator index is populated from the codes on the broad indicator
dimension, and query resolution is a filter *within* a dataflow — exactly the flow StatGPT
implements.

---

## 2. Shared DSD — ❌ Not supported yet

One rich DSD is **deliberately partitioned into many semantically-distinct dataflows** —
typically one dataflow per country or per sub-table. The DSD is shared; the dataflows are
narrow slices of it.

**Shape:**

- One DSD backs many dataflows (mean dataflows-per-DSD well above 1); a large share of
  dataflows ride a shared DSD.
- Each dataflow is a narrow slice of the shared structure — typically one country or one
  sub-table — not a broad indicator dataflow.

**Example: OECD**

- ~1,536 dataflows over ~413 distinct DSDs (mean ≈ 3.65 dataflows per DSD); ~82% of dataflows
  ride a shared DSD.
- Naming encodes the DSD in every dataflow id: `DSD_<name>@DF_<name>` (~96% of dataflows).
- The sharing is almost always one structure split by country or sub-table:

| DSD | # dataflows | Example dataflows |
|-----|-------------|-------------------|
| `OECD.TAD.ADM:DSD_FFS` (fossil-fuel support) | 53 | `DSD_FFS@DF_FFS_ARG`, `…_ARM`, `…_AUS` (per country) |
| `OECD.CTP.TPS:DSD_REV_OECD` (tax revenue) | 39 | `DSD_REV_OECD@DF_REVAUS`, `…_AUT`, … (per country) |
| `OECD.SDD.NAD:DSD_NAMAIN10` (national accounts) | 35 | `DSD_NAMAIN10@DF_TABLE1`, `…_EXPENDITURE`, … (per table) |

---

## 3. Indicator-per-dataflow (dedicated DSD per dataset) — ❌ Not supported yet

Each dataset is **one narrow table — effectively one indicator — published as its own
dataflow with its own dedicated DSD**, producing thousands of dataflows. The indicator is
determined by *which* dataflow is chosen, not by a dimension within one.

**Shape:**

- Thousands of dataflows, each with its own dedicated DSD — a near-1:1 dataflow-to-DSD ratio,
  often with `dataflow-id == DSD-id`.
- Each dataflow is a narrow table; there is no broad indicator dataflow to select and filter.
- The dataset-specific axis is usually a domain indicator dimension that is not consistent
  across datasets.

**Example: Eurostat**

- ~8,245 dataflows over ~7,698 distinct DSDs, in near-perfect 1:1 — ~100% of base datasets
  have `dataflow-id == DSD-id` (e.g. dataflow `NAMA_10_GDP` → DSD `NAMA_10_GDP`).
- The one genuinely dataset-specific axis is a domain indicator dimension (`na_item`,
  `indic_is`, `indic_bt`, …), which is not consistent across datasets.
- Plus ~547 `$DV_` "data-view" dataflows (pre-saved filtered views) that reference their
  parent dataset's DSD (e.g. `ISOC_CI_AC_I$DV_1043`).

**Other providers with this model:**

| Provider | Shape |
|----------|-------|
| **Eurostat** | ~8,245 dataflows, one dedicated DSD per dataset (`dataflow-id == DSD-id`), + `$DV_` views |
| **ISTAT** | ~810 real datasets, one DSD each, but ~78% of its ~4,876 dataflows are `_DF_..._N` saved-view variants of a parent dataset |
| **ABS** | ~1,223 dataflows, dedicated DSD ~1:1 (`dataflow-id == DSD-id`) |
| **ILO** | ~1,208 dataflows ↔ 1,208 DSDs, strict 1:1 (`DF_<X>` → DSD `<X>`) |

---

## Summary

| Data model | Example providers | Supported |
|------------|-------------------|:---------:|
| Conventional (multi-indicator dataflow) | IMF, BIS | ✅ |
| Shared DSD | OECD | ❌ |
| Indicator-per-dataflow (dedicated DSD per dataset) | Eurostat, ISTAT, ABS, ILO | ❌ |
