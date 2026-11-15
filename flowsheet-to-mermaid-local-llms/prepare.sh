#!/usr/bin/env bash
# Build the four test drawings from the lecture PDF. The PDF is not in this repository: download it from
# https://www.researchgate.net/publication/318502393_Flowsheets (Anderson, Mineral Processing Flowsheets).
# Usage: ./prepare.sh <Flowsheets.pdf> <folder>     Writes <folder>/pages/ (whole slides) and <folder>/figures/ (cropped).
# Needs pdftoppm (poppler-utils) and Python with Pillow.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
pdf=$1; out=$2
mkdir -p "$out/pages"
while read -r slide name; do
  pdftoppm -r 200 -f "$slide" -l "$slide" -png -singlefile "$pdf" "$out/pages/p$slide-$name"
done <<'LIST'
23 closed-circuit-size-reduction
53 kolwezi-cobalt-oxide-mill
39 phoenix-mine-mill
37 twin-creeks-mine
LIST
python3 "$here/crop.py" "$out/pages" "$out/figures"
