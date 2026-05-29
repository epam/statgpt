---
name: statgpt-admin-fe-guide-macos
description: >-
  Refresh or rewrite the StatGPT Administrator Guide (guides/admin-guide.md and its annotated
  screenshots under guides/content/admin-guide/) to match the StatGPT Admin frontend. Use this
  whenever the user asks to update, refresh, re-screenshot, or fix the admin guide; to document
  new admin-UI features (data sources, datasets, channels, index versions, auto-update jobs,
  indexing/deduplication, glossary, import/export, audit logs); or to regenerate its images —
  even when phrased loosely ("the admin guide is outdated", "add screenshots to the admin guide",
  "re-do the admin docs") or by just pasting the admin frontend URL. It captures sample-only,
  annotated screenshots (numbered badges + highlight boxes), sources config YAML from the
  statgpt-backend sample configs in admin (camelCase) format, and links the admin learning course.
compatibility: >-
  macOS (uses `screencapture`); the claude-in-chrome MCP with a logged-in admin session;
  Screen Recording permission granted; a python with Pillow installed.
---

# StatGPT Admin Frontend Guide Updater

This skill regenerates the **StatGPT Administrator Guide** — `guides/admin-guide.md` plus its
annotated screenshots in `guides/content/admin-guide/` — so the prose, the configuration YAML, and
the images all match the current Admin frontend. It exists because doing this by hand is fiddly:
screenshots leak non-sample content, the Chrome debugging banner corrupts captures, badge
placement is easy to get wrong, and the config format in the guide must match what the admin
actually stores (not the snake_case seed files).

The output is a rewritten guide with numbered-step prose whose numbers line up with numbered badges
on each screenshot, plus a set of clean, sample-only annotated PNGs.

## Step 0 — Gather the three inputs

This skill is **driven by three inputs**. Ask for any that aren't already given, then confirm them
back before doing work:

1. **Scope** — what to refresh. Either a *full refresh* (every section + new features) or a
   *targeted* update (named sections, or "just the new X feature"). Scope decides which screens you
   capture and which parts of the guide you rewrite. Don't silently expand scope.
2. **Environment URL** — the admin frontend base URL to capture from
   (e.g. `https://statgpt-admin-frontend.aks.dev.dial.parts`). Everything is captured live from
   here through the claude-in-chrome MCP.
3. **Limitations** — hard constraints for this run. The defaults below are non-negotiable unless the
   user explicitly relaxes one; the user may add more (e.g. "don't touch the channel X").

## Hard constraints (the defaults — honor unless the user overrides)

These protect a **public** docs repo and a **shared** environment. Re-read them before each capture.

- **Sample content only.** Every screenshot must show *only* sample entities. Filter every list to
  the sample data source (e.g. `IMF_SDMX21`), the sample channel (e.g. **StatGPT Sample**), and the
  "**- Sample**" datasets. Never let other orgs' content appear (e.g. QH_UAT_SWRE, STATGPT_SDMX30_PROXY,
  SwissRe, GTDC, Global Data). If a screen can't be filtered to sample-only (e.g. an "Add datasets to
  channel" picker that lists everything and has no source filter), **don't screenshot it** — describe
  it in prose instead. Confirm the exact sample identifiers for the target environment up front.
- **Redact PII.** Audit logs and similar screens show real user emails. Mask those columns with a
  redaction bar before the image leaves your hands (see `references/annotation.md`).
- **No deletions of any content.** To document a delete action, open the confirm dialog and Cancel.
  Beware: some delete actions have **no confirmation dialog** (e.g. glossary terms delete
  immediately). If you trigger one by accident, **restore the item immediately** from the seed
  configs and tell the user.
- **You may modify / reindex / deduplicate / add SAMPLE content only** — never other channels/sources.
  Don't create duplicate sources/datasets/channels when illustrating "Add"; fill the form for the
  screenshot, then Cancel.
- **Documents page is out of scope** unless the user says otherwise.
- **No git commits or pushes** unless the user asks. When they do, branch first, stage *only* the
  guide + its images (not stray local files), and follow the repo's PR conventions.

## Workflow

Work in a scratch dir (e.g. `/tmp/statgpt-admin-guide/{raw,annotated,specs}`) and only copy
finished images into the repo at the end. Track progress with a task list.

### Phase 1 — Explore and map changes

Drive the admin UI with the claude-in-chrome MCP (load the deferred `mcp__claude-in-chrome__*`
tools via ToolSearch first; call `tabs_context_mcp` to get the tab id). Walk the target scope's
screens and compare against the current `guides/admin-guide.md`: note new nav items, renamed/added
buttons, changed wizards, new columns, and new pages. Produce a short map of what changed so the
rewrite and the screenshot list are grounded in the live UI, not assumptions.

### Phase 2 — Capture sample-only screenshots

This is the part with the sharp edges. **Read `references/capture-pipeline.md` before starting** —
it covers window calibration, the debugging-banner problem, and the two coordinate spaces. The loop
per screenshot:

1. Drive the UI to the target state via MCP (`browser_batch` of clicks/types/navigate). **Filter
   every list to sample content** before capturing.
2. Make the **final MCP action a `hover` to a neutral, empty spot** so the cursor (which
   `screencapture` includes) isn't covering content.
3. Capture with the bundled banner-aware script — **no CDP command between the hover and this**:
   ```
   CAP_REGION=<X,Y,W,H> CAP_PYBIN=<python-with-pillow> \
     scripts/cap.sh /tmp/statgpt-admin-guide/raw/<name>.png
   ```
4. **View the PNG** (Read it) and confirm it's banner-free and shows only sample content.

Capture the set of screens your scope needs (list pages, add wizards, edit/config modals, context
menus, per-dataset Versions / Auto update jobs pages, indexing dialogs, glossary, import modal,
jobs, audit logs). `references/config-and-structure.md` has the canonical screen inventory and
suggested filenames.

### Phase 3 — Annotate (numbered badges + highlight boxes)

Style is **numbered badges + rounded highlight boxes** (numbers match the numbered prose steps),
with **redaction bars** for PII. Use the bundled annotator:

```
<python-with-pillow> scripts/annotate.py spec.json
```

The spec is JSON with `src`, `dst`, optional `crop`, and `boxes` / `badges` / `redactions` arrays.
**Coordinates are measured from the actual captured PNG**, and getting this right is the single
biggest source of rework — **read `references/annotation.md`**, especially the part about *not*
trusting downscaled previews (measure from clean, full-resolution crops). Verify every rendered
annotation by viewing it; box columns to their *full* visible height; keep badges off the content
they label.

### Phase 4 — Rewrite the guide

Rewrite the in-scope parts of `guides/admin-guide.md`:

- Match the new UI: structure, nav, wizards, new pages and columns.
- Numbered prose steps that **correspond to the badges** in each referenced screenshot.
- **Configuration YAML in admin (camelCase) format**, sourced from the `statgpt-backend` sample
  configs — *do not invent values*. The seed files are snake_case; the admin stores camelCase. See
  `references/config-and-structure.md` for the field mapping (data source, the dataset `dimensions`
  map, channel + tools). When in doubt, the live "Configure"/"Edit" editor is the source of truth —
  read it via Monaco `getValue()`.
- When covering dataset configuration, **link the admin learning course**
  (`../learning/administration/README.md`, esp. Modules 03a/03b/04/05/06).
- Add a table of contents; fix any broken image links; keep every cross-link resolvable.

### Phase 5 — Review and (if asked) ship

Verify all referenced images exist; flag now-orphaned old images (don't delete files you didn't
create without asking). If the user asks to ship: branch, stage only the guide + images, commit
with a Conventional-Commits title, push, and open a PR with the repo's template.

## Key paths

- Guide: `guides/admin-guide.md`; images: `guides/content/admin-guide/`.
- Sample configs (source of truth for YAML): `statgpt-backend/configurations/clients/sample/`
  (`data_sources.yaml`, `datasets/*.yaml`, `channels.yaml`, `tools.yaml`, `glossaries/*.csv`).
- Learning course: `learning/administration/` (README + numbered modules).
- Bundled `scripts/cap.sh` (capture) and `scripts/annotate.py` (annotate).

## References (read when you reach the relevant phase)

- `references/capture-pipeline.md` — window calibration, the Chrome debugging banner, coordinate
  spaces, and the capture protocol. **Read before Phase 2.**
- `references/annotation.md` — the annotator spec, coordinate measurement (and the downscaled-preview
  trap), badge/box/redaction conventions. **Read before Phase 3.**
- `references/config-and-structure.md` — seed→admin config field mapping, the guide's section
  structure, the screenshot inventory, and learning-course links. **Read before Phase 4.**
