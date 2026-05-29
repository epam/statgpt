# Annotation — numbered badges, highlight boxes, redaction bars

Read this before Phase 3. The annotator itself is simple; getting coordinates right is the work.

## The annotator (`scripts/annotate.py`)

Run: `<python-with-pillow> scripts/annotate.py spec.json`

Spec JSON (all coords in the captured PNG's pixel space; use `"scale": 1`):

```json
{
  "src": "/tmp/.../raw/X.png",
  "dst": "/tmp/.../annotated/X.png",
  "scale": 1,
  "crop": [x, y, w, h],
  "redactions": [ {"xywh": [x, y, w, h]} ],
  "boxes":   [ {"xywh": [x, y, w, h], "n": 1, "color": "red"} ],
  "badges":  [ {"xy": [x, y], "n": 2, "color": "red"} ],
  "arrows":  [ {"from": [x, y], "to": [x, y], "color": "red"} ]
}
```

- **boxes** — rounded highlight rectangle; if `"n"` is set, a numbered badge is drawn at its
  top-left corner. This is the workhorse.
- **badges** — a standalone numbered badge centered at `xy` (use sparingly; a detached badge reads as
  disconnected — prefer attaching the number to a box).
- **redactions** — solid filled bar (default gray) drawn *first*, under everything. Use for PII.
- `crop` is applied before drawing; if you crop, the box coords are relative to the cropped image.
- Colors: `red` (default), `blue`, `green`, `orange`, `purple`. Fonts come from
  `/System/Library/Fonts/Supplemental/Arial*.ttf`.

## ⚠️ Measuring coordinates — the #1 source of rework

The numbers in your spec must land on real UI elements. The trap: when you Read a captured PNG, the
viewer often shows it at **half scale** (or otherwise downscaled), and at that size misalignments are
invisible — you'll think a box is on "Result" when it's actually a column off, or that a redaction
covers emails when it covers the *next* column. This burned multiple iterations in the original run.

**Rules that prevent it:**

1. **Measure from clean, full-resolution crops — not from the downscaled full image.** Crop the raw
   PNG to the region of interest with PIL and read pixel positions there. The most reliable form is a
   crop where displayed-x maps directly to file-x (i.e. `file_x = crop_x + x_offset`, no scaling):
   ```python
   from PIL import Image
   Image.open('raw/X.png').crop((x0, y0, x1, y1)).save('/tmp/_measure.png')  # NO resize
   ```
   Then `file_x = displayed_x + x0`. Avoid scaled crops for measurement — the scale math compounds
   reading errors.
2. **A ruler crop is great for nailing columns.** Draw labeled vertical/horizontal lines at known
   file coordinates onto a crop, then read where content falls between them:
   ```python
   from PIL import Image, ImageDraw
   c = Image.open('raw/X.png').crop((x0,y0,x1,y1)).convert('RGB'); d = ImageDraw.Draw(c)
   for fx in range(((x0//50)+1)*50, x1, 50):
       cx = fx-x0; d.line([(cx,0),(cx,c.height)], fill=(255,60,60)); d.text((cx+1,1), str(fx), fill=(255,255,0))
   c.save('/tmp/_ruler.png')
   ```
3. **Always verify the rendered annotation by viewing it** — and if it's a table/columns shot, verify
   with a *clean crop* of the box region, not just the full downscaled image. If a box looks even
   slightly off, re-measure from a clean crop and re-render. Trust the clean crop over the thumbnail.

## Conventions that look right

- **Tables/columns:** box a column to its **full visible height** (header through the last row). A box
  that stops partway down looks broken. If rows fill to the viewport bottom, extend the box there.
- **Action buttons (Save/Finish/Next):** wrap the button tightly; the badge sits at the top-left
  corner. Make sure the box doesn't drift onto the adjacent button (e.g. Cancel) or label the wrong
  thing.
- **Context menus:** box the whole menu *including the left-edge icons* — the menu background starts a
  bit left of the text. Verify icons are inside the box.
- **Don't cover content with badges.** A number sitting on a term name, a value, or the wrong column
  header reads as an error. Put badges on empty corners, headers, or gaps — not on the data they
  point to.
- **Match badge numbers to prose steps.** The numbers exist to map to the numbered steps in the guide
  text near that image. Keep them consistent (1,2,3… in the order the prose introduces them).

## Redacting PII (audit logs, etc.)

Audit-log screens include a column of real user emails. Measure that column precisely (ruler crop),
then add a `redactions` entry covering the *data cells* (leave the column header visible so it's clear
what was hidden). Verify by zooming into the rendered Initiated/email column — confirm no text
survives the bar. Non-PII identifiers (activity UUIDs, entity IDs) don't need redaction.

## Bolder annotations on hi-res images

The annotator defaults to a ~4px border and ~16px badge radius, which read well on ~1600px-wide
captures. If your viewport is much larger or smaller, adjust `bw`/`br` in `annotate.py`'s `main()`.
