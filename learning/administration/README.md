# StatGPT Admin Learning Materials: Dataset Onboarding

> **Disclaimer:** StatGPT is actively evolving. We do our best to keep these materials up-to-date, but some details (field names, UI workflows, default values) may lag behind the latest release. When in doubt, refer to the Admin UI itself as the source of truth. If you spot an inconsistency, please open an issue or submit a correction.

## Purpose

These learning materials guide StatGPT administrators through the process of onboarding new datasets. After completing all modules, you will be able to independently assess, configure, index, and validate new SDMX datasets in StatGPT.

## Audience

- StatGPT administrators responsible for adding and managing datasets
- Technical staff involved in channel configuration and maintenance
- Data source providers preparing datasets for StatGPT integration

## Prerequisites

- Access to the StatGPT Admin UI
- Basic understanding of statistics and economics terminology
- Familiarity with YAML configuration format
- (Optional) Familiarity with SDMX concepts — covered in Module 01

## Modules

| Module | Title | Description |
|--------|-------|-------------|
| [01](01-core-concepts.md) | Core Concepts & Entity Relationships | StatGPT's three core entities (Data Source, Dataset, Channel), how they relate, and an introduction to SDMX |
| [02](02-dataset-assessment.md) | Assessing Datasets for Onboarding | Evaluating SDMX metadata quality, identifying packed vs. unpacked indicator patterns (explained fully in Module 03b), and assessing business value |
| [03a](03a-dimension-types.md) | Dimension Types & Named Entities | **Key module** — Classifying dimensions as INDICATOR, NON_INDICATOR, or TIME_PERIOD, and configuring Named Entity types |
| [03b](03b-indicator-configuration.md) | Indicator Configuration | Required vs. optional indicators, packed vs. unpacked, and concrete multi-agency examples |
| [04](04-dataset-configuration.md) | Configuring a Dataset | Field-by-field walkthrough of the dataset configuration YAML, with annotated IMF and multi-agency examples |
| [05](05-data-sources-and-channels.md) | Data Sources & Channel Configuration | Adding data sources, creating channels, configuring the supreme agent, tools, and glossary |
| [06](06-indexing-and-operations.md) | Indexing, Deduplication & Operations | Running and monitoring indexes, deduplication, auto-update, import/export, validating indexing results, and cost awareness |
| [07](07-testing-and-validation.md) | Testing & Validation | **Key module** — LLM non-determinism, ground truth, test case design, precision/recall evaluation, and manual verification |
| [08](08-end-to-end-walkthrough.md) | End-to-End Walkthrough | Capstone exercise — onboard a dataset from assessment through testing, applying all modules in sequence |

## Primary Examples

These materials use **IMF datasets** as the primary examples (WEO, BOP, CPI, and others from the IMF SDMX 2.1 API). Secondary examples cover **Eurostat**, **World Bank**, **OECD**, **ECB**, **BIS**, and **FRB** to illustrate multi-agency patterns and data modeling differences.

## Additional Resources

- [Quick-Reference Card](quick-reference.md) — One-page decision trees, YAML template, and onboarding checklist
- [StatGPT Public Admin Guide](../../guides/admin-guide.md) — UI screenshots and step-by-step instructions
- [SDMX Compatibility & Requirements](../../architecture/sdmx-compatibility.md) — technical requirements for data sources
- [StatGPT Architecture Overview](../../architecture/overview.md) — system-level architecture
- [Data Query Evaluation Methodology](../../evaluation/data_query.md) — detailed evaluation metrics
