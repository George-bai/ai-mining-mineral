"""Enlarge one part of the drawing, with rulers in drawing coordinates, to look closely at a label or a line.
Usage: python3 zoom.py <drawing.png> <x0> <y0> <x1> <y1>      (drawing pixels, as on the tile rulers)
Writes work/zoom/z<n>.png. A region an earlier zoom already shows at full enlargement is not zoomed again:
the first time, the earlier zoom is given back; after that, the region is closed. Stops after LIMIT requests."""
import sys
from pathlib import Path
from PIL import Image

from tile import with_rulers

LIMIT = 60
FULL = 2.0   # an earlier zoom enlarged at least this much already shows its region as large as a zoom can


def scale(b):
    return min(2.5, 1400 / max(b[2] - b[0], b[3] - b[1]))   # as in tile.with_rulers


def inter(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def area(b):
    return (b[2] - b[0]) * (b[3] - b[1])


def shows(old, new):
    """The earlier zoom already shows the new region: the new box lies mostly inside it and it was enlarged
    fully (a smaller box gives no larger picture), or the two boxes are nearly the same."""
    i = inter(old, new)
    return (i > 0.8 * area(new) and scale(old) >= FULL) or i > 0.8 * (area(old) + area(new) - i)


src = Path(sys.argv[1])
x0, y0, x1, y1 = map(int, sys.argv[2:6])
im = Image.open(src).convert("RGB")
box = (max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1))
out = Path("work/zoom")
out.mkdir(parents=True, exist_ok=True)
log = out / "log.txt"
done = [l.split() for l in log.read_text().splitlines()] if log.exists() else []   # "z3.png x0 y0 x1 y1", "again z3.png ...", "empty - ..."
NEXT = "Write what you have in work/notes.md, then run next.py and do what it says."

if len(done) >= LIMIT:   # every request counts, empty ones too
    print(f"Zoom limit reached ({LIMIT}). {NEXT}")
    sys.exit(0)
if box[2] <= box[0] or box[3] <= box[1]:
    with open(log, "a") as f:
        f.write(f"empty - {x0} {y0} {x1} {y1}\n")
    print(f"Empty box {x0} {y0} {x1} {y1}: x1 must be more than x0 and y1 more than y0, inside the drawing "
          f"(0-{im.width} by 0-{im.height}). Nothing zoomed.")
    sys.exit(0)

crops = [(d[0], tuple(map(int, d[1:5]))) for d in done if d[0] not in ("again", "empty")]
for name, old in crops:
    if shows(old, box):
        served = sum(1 for d in done if d[0] == "again" and d[1] == name)
        with open(log, "a") as f:
            f.write(f"again {name} {' '.join(map(str, box))}\n")
        if served == 0:
            print(f"{out / name}\nAn earlier zoom already shows this region as large as a zoom can, so here it is "
                  f"again. Read it now, then write what it shows in work/notes.md before anything else.")
        else:
            print(f"This region is done: {out / name} shows it as large as a zoom can, and you have been given it "
                  f"again already. If it is still unclear, write 'unclear' for it in work/notes.md. {NEXT}")
        sys.exit(0)

name = f"z{len(crops) + 1}.png"
with_rulers(im, *box, f"zoom: drawing x {box[0]}-{box[2]}, y {box[1]}-{box[3]}").save(out / name)
with open(log, "a") as f:
    f.write(f"{name} {' '.join(map(str, box))}\n")
print(f"{out / name}\nRead it now, then write what it shows in work/notes.md before anything else.")
