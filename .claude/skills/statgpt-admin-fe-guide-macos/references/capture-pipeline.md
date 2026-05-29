# Capture pipeline — calibration, the banner, and coordinate spaces

Read this before Phase 2. These are the non-obvious things that otherwise cost a lot of rework.

## Why macOS `screencapture`, not the MCP screenshot

The claude-in-chrome MCP screenshot is returned inline and is fine for *driving* the UI, but it is
not a clean file you can annotate, and `save_to_disk` does not reliably write a local file you can
read. The pixel-perfect, file-on-disk method is macOS `screencapture -R<region>`, which the bundled
`cap.sh` wraps. This needs **Screen Recording permission** granted to the terminal/app; if
`screencapture` errors with "could not create image from display", that permission is missing —
ask the user to grant it (System Settings → Privacy & Security → Screen Recording) and retry.

## ⚠️ The Chrome debugging banner (the main gotcha)

After *any* CDP command (any MCP `computer`/`navigate`/`javascript_tool` call — **including a
`window.innerHeight` check**), Chrome shows a **"Claude started debugging this browser  [Cancel] ✕"**
infobar. It:

- appears a fraction of a second after the CDP command,
- **persists** and only auto-dismisses after an idle period with no CDP commands (observed: still
  there at ~7s, gone by ~15–30s),
- while present, **shifts page content down ~46px**, which breaks any fixed capture region and looks
  unprofessional.

Consequences:

- **Never run a CDP command immediately before capturing.** `cap.sh` polls with *pure* screencapture
  (no CDP) until the banner clears, so it never re-triggers it. Make your last MCP action a `hover`,
  then call `cap.sh`.
- **Do NOT click the banner's Cancel/✕** — that can detach the debugger and disconnect the MCP. Just
  let it time out (cap.sh waits for you).
- If the MCP disconnects, the user re-runs `/chrome` and you reload the tools via ToolSearch.

How `cap.sh` detects "clear": it screenshots only the top 28px strip and measures mean brightness.
The banner is light (bright); the dark "StatGPT ADMIN" app bar is dark. When mean brightness < 90 it
captures the full region. It prints `OK ...` on a clean grab, or `WARN ...` if the banner persisted
past ~45s (then investigate / wait longer / inspect the image).

## Window calibration (re-derive every session — the window moves)

The capture region is a fixed rectangle `X,Y,W,H` passed to `screencapture -R`. It must frame the
viewport from the top of the "StatGPT ADMIN" app bar down through the content, with **no browser
chrome** and **no banner**. The values are environment- and session-specific (monitor layout,
window position). To derive them:

1. Get window geometry via `javascript_tool`:
   `({sx:screenX, sy:screenY, ow:outerWidth, oh:outerHeight, iw:innerWidth, ih:innerHeight, dpr:devicePixelRatio})`
2. The content top is roughly `screenY + (outerHeight - innerHeight) - ~48`. (Empirically the app bar
   sat ~48px above the naive `screenY + chromeHeight`; in one session `-922` worked where the naive
   value was `-873`. Negative coords are fine — the window was on a secondary monitor.)
3. Width ≈ innerWidth; height ≈ innerHeight minus a few px so you don't catch the window's bottom edge.
4. **Calibrate by capturing and viewing**: grab the candidate region, view it, and adjust until the
   top edge sits exactly at the app bar and nothing is cut. Then lock it and **don't move/resize the
   window** for the rest of the session.

Pass the locked region to cap.sh via `CAP_REGION="X,Y,W,H"`. (The default baked into cap.sh is just
an example from one session — always recalibrate.)

Set `CAP_PYBIN` to a python that has Pillow (e.g. a backend `.venv/bin/python`); cap.sh uses it for
the brightness probe, and you'll use the same interpreter for `annotate.py`.

## Two coordinate spaces — don't mix them

- **MCP clicks/inline screenshots** use the inline-screenshot space (e.g. ~1546×795). Use these
  coords to *drive* the UI (clicks, hovers, types).
- **macOS captures** are the real viewport size (e.g. 1600×812). **Measure annotation coordinates
  from the actual captured PNG**, never from MCP coords — the two spaces have slightly different
  aspect ratios, so scaling between them (especially vertically) is unreliable.

## Capture protocol (per screenshot)

1. `browser_batch`: navigate/click/type to the target state. Filter lists to sample content.
2. Final MCP action: `hover` to a neutral empty spot (e.g. lower sidebar, or an empty modal area) so
   the cursor isn't over content. Context menus stay open across the hover + cap.sh wait.
3. `CAP_REGION=... CAP_PYBIN=... scripts/cap.sh /tmp/.../raw/<name>.png` (no CDP in between).
4. Read the PNG. Confirm: banner-free, full app bar visible, only sample content, cursor parked.

## Extracting authoritative config while a modal is open

The admin stores camelCase config; the seed files are snake_case. To capture the *exact* admin
format, open a "Configure"/"Edit" modal and read the Monaco editor value via `javascript_tool`:
`monaco.editor.getModels().map(m=>m.getValue())` — pick the model containing the config. Long values
get truncated in tool output; slice the string (`t.slice(0,3700)`, then from `t.indexOf('\ndimensions:')`,
etc.) and reassemble. This is how you confirm new fields without guessing.
