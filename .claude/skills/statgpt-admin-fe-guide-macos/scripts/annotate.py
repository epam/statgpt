#!/usr/bin/env python3
"""Annotate StatGPT admin screenshots with numbered badges + highlight boxes.

Usage:
    python annotate.py spec.json

Spec JSON schema:
{
  "src": "/abs/path/raw.png",
  "dst": "/abs/path/out.png",
  "scale": 2.0,                  # multiply all coords below by this (CSS px -> image px)
  "crop": [x, y, w, h],          # optional, in IMAGE px (applied before scale-based draw); omit for none
  "boxes": [
     {"xywh": [x, y, w, h], "n": 1, "color": "red"}      # highlight rect; n -> badge at top-left corner
  ],
  "badges": [
     {"xy": [x, y], "n": 2, "color": "red"}              # standalone numbered badge centered at xy
  ],
  "arrows": [
     {"from": [x, y], "to": [x, y], "color": "red"}
  ]
}
All coords (xywh / xy / from / to) are in CSS/logical px and get multiplied by "scale".
If you pass coords already in image px, set "scale": 1.
"""
import json, sys, math
from PIL import Image, ImageDraw, ImageFont

PALETTE = {
    "red":    (244, 63, 71),
    "blue":   (56, 132, 255),
    "green":  (52, 199, 89),
    "orange": (255, 149, 0),
    "purple": (175, 82, 222),
}
DEFAULT = PALETTE["red"]

FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]

def load_font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def col(name):
    if isinstance(name, (list, tuple)):
        return tuple(name)
    return PALETTE.get(name, DEFAULT)

def rounded_rect(draw, box, radius, outline, width):
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=width)

def draw_badge(img, cx, cy, n, color, r):
    """Filled circle with white number, centered at (cx,cy)."""
    d = ImageDraw.Draw(img)
    # subtle dark outline for contrast on light areas
    d.ellipse([cx-r-2, cy-r-2, cx+r+2, cy+r+2], fill=(255, 255, 255))
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
    font = load_font(int(r*1.25))
    txt = str(n)
    bb = d.textbbox((0, 0), txt, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.text((cx-tw/2-bb[0], cy-th/2-bb[1]), txt, fill=(255, 255, 255), font=font)

def draw_arrow(draw, p0, p1, color, width):
    draw.line([p0, p1], fill=color, width=width)
    # arrowhead
    ang = math.atan2(p1[1]-p0[1], p1[0]-p0[0])
    L = 18
    for da in (math.radians(28), -math.radians(28)):
        ex = p1[0] - L*math.cos(ang+da)
        ey = p1[1] - L*math.sin(ang+da)
        draw.line([(p1[0], p1[1]), (ex, ey)], fill=color, width=width)

def main():
    spec = json.load(open(sys.argv[1]))
    img = Image.open(spec["src"]).convert("RGB")
    if spec.get("crop"):
        x, y, w, h = spec["crop"]
        img = img.crop((x, y, x+w, y+h))
    s = float(spec.get("scale", 1))
    draw = ImageDraw.Draw(img)
    bw = max(4, int(round(4*s)))          # box border width
    br = max(16, int(round(16*s)))        # badge radius

    # Redactions: solid filled bars to mask sensitive content (e.g. emails).
    for rd in spec.get("redactions", []):
        x, y, w, h = [v*s for v in rd["xywh"]]
        fill = col(rd["color"]) if rd.get("color") else (70, 76, 88)
        draw.rectangle([x, y, x+w, y+h], fill=fill)

    for b in spec.get("boxes", []):
        x, y, w, h = [v*s for v in b["xywh"]]
        c = col(b.get("color"))
        rounded_rect(draw, [x, y, x+w, y+h], radius=int(8*s), outline=c, width=bw)
        if "n" in b:
            draw_badge(img, x, y, b["n"], c, br)
            draw = ImageDraw.Draw(img)

    for a in spec.get("arrows", []):
        draw_arrow(draw, tuple(v*s for v in a["from"]), tuple(v*s for v in a["to"]),
                   col(a.get("color")), bw)

    for bd in spec.get("badges", []):
        x, y = [v*s for v in bd["xy"]]
        draw_badge(img, x, y, bd["n"], col(bd.get("color")), br)
        draw = ImageDraw.Draw(img)

    img.save(spec["dst"])
    print("wrote", spec["dst"], img.size)

if __name__ == "__main__":
    main()
