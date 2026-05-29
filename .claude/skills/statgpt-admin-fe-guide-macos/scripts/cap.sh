#!/bin/bash
# cap.sh — capture the StatGPT Admin viewport with macOS `screencapture`,
# waiting out the Chrome "Claude started debugging this browser" infobar
# (which shifts page content down and ruins a fixed-region capture).
#
# It polls the top strip of the viewport with PURE screencapture (no CDP, so
# it never re-triggers the banner) until that strip goes dark — i.e. the dark
# "StatGPT ADMIN" app bar is showing rather than the bright banner — then grabs
# the frame. See references/capture-pipeline.md for why this matters.
#
# Usage: cap.sh /abs/out.png
# Env (override per session — the defaults are example values, NOT universal):
#   CAP_REGION : screencapture -R value "X,Y,W,H" for the viewport region.
#                Re-derive this every session; the window moves. See the
#                calibration steps in references/capture-pipeline.md.
#   CAP_PYBIN  : a python interpreter with Pillow installed (brightness probe).

OUT="$1"
REGION="${CAP_REGION:--219,-922,1600,812}"
PYBIN="${CAP_PYBIN:-python3}"

IFS=',' read -r RX RY RW _RH <<< "$REGION"
PROBE="$(dirname "$OUT")/_probe_top.png"

for i in $(seq 1 45); do
  screencapture -x -t png -R"${RX},${RY},${RW},28" "$PROBE"
  bright=$("$PYBIN" -c "from PIL import Image,ImageStat;print(int(ImageStat.Stat(Image.open('$PROBE').convert('L')).mean[0]))")
  if [ "$bright" -lt 90 ]; then
    screencapture -x -t png -R"$REGION" "$OUT"
    echo "OK $OUT (clear, bright=$bright, ~${i}s)"; exit 0
  fi
  sleep 1
done
screencapture -x -t png -R"$REGION" "$OUT"
echo "WARN $OUT (banner may still be present, bright=$bright) — inspect before using"
