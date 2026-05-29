# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is the **StatGPT documentation repository** — Markdown, images, and draw.io diagrams only. There is **no application code, build step, or test suite here.** Docs render directly on GitHub; nothing is compiled or served by a static-site generator.

The product itself lives in sibling repositories. The backend is mounted as a **second working directory** at `../statgpt-backend` (Python / FastAPI / LangChain — the admin and chat backends, SDMX handling, the agent). When documenting a feature, treat that repo as the implementation source of truth. The other components (admin & portal frontends, SDMX proxy, Helm chart) are external GitHub repos linked from `README.md`.

StatGPT is an AI "talk-to-your-data" platform for official SDMX statistics, built on the AI DIAL platform. Its agent uses **tool-calling** (not code generation) and **grounds** every answer in real query results to prevent hallucination.

## Validation

There is no build or test. The only CI check is formatting hygiene, run by `.github/workflows/pr.yml` on PRs to `main`:

```bash
pip install pre-commit && pre-commit install   # one-time setup
pre-commit run --all-files                      # check / auto-fix everything
```

Hooks (`.pre-commit-config.yaml`): `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `mixed-line-ending`. A red CI is almost always a missing final newline or trailing whitespace — run the command above and commit the result.

## Contributing

- **PRs target `main`** and are squash-merged. PR **titles must follow [Conventional Commits](https://www.conventionalcommits.org/)** — enforced by the `pr-title-check` workflow.
- Reference an issue in the PR (`fixes #123`); contributions are made under the **MIT license** — this is a public repo.
- `CONTRIBUTING.md` covers the broader multi-repo branching/release process and the coding principles the whole project follows.

## Documentation layout

Each area has its own `README.md` index — read it first.

| Area | Purpose |
|------|---------|
| `architecture/` | Technical design. Intended read order: `overview.md` → `services.md` → `agent.md` → `tools.md`. `sdmx-compatibility.md` and `mcp.md` are specialized topics. |
| `guides/` | Task-oriented guides: `admin-guide.md`, `admin-azure-auth-guide.md`, `gtdc-portal-guide.md`. |
| `learning/administration/` | Structured 8-module course on **dataset onboarding** for admins (IMF datasets as the primary examples) plus `quick-reference.md`. The deepest treatment of dimension / indicator / dataset configuration. |
| `evaluation/` | `data_query.md` — methodology for evaluating SDMX data-query quality (ground truth, precision/recall). |

These areas overlap intentionally and **cross-link with relative paths** (e.g. the learning course points into `guides/` and `architecture/`). When you move or rename a doc, fix the inbound links yourself — there is no link-checker in CI.

## Conventions

- **Images** live under `<area>/content/<doc-name>/` (e.g. `guides/content/admin-guide/`); reference them with relative paths.
- **Architecture diagrams** are SVGs exported from the single editable source `architecture/content/diagrams.drawio`. Edit the `.drawio` in draw.io and re-export — do not hand-edit the SVGs.
- **Public-repo content rules:** screenshots must show **sample content only** (the sample data source / channel / "- Sample" datasets) and **PII must be redacted**. Never commit other orgs' data or real user emails.
- Architecture docs use emoji section headers and Markdown tables; match the style of the file you are editing.

## Domain model (keep terminology consistent across docs)

- **Core entities:** **Data Source → Dataset → Channel.** A channel bundles datasets + tools + glossary and is what an end user talks to.
- **Components:** Chat Backend (DIAL app), Admin Backend (FastAPI + Alembic), Admin & Portal Frontends (React/Next.js), SDMX Proxy (Spring Boot — unified SDMX 3.0 facade over upstream registries), all deployed via the Helm chart. Built on **AI DIAL** for auth, rate limits, model access, and file storage.
- **Agent tools:** Available Datasets, Data Query (natural language → SDMX), Available Publications + Publications RAG, Glossary Terms/Definitions, Web Search. Channel tools are also exposed to external AI agents over **MCP**.
