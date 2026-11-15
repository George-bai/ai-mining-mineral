"""Crop each slide image in <pages> to its white figure, into <figures>.   Usage: python3 crop.py <pages> <figures>"""
import sys
from pathlib import Path
from PIL import Image

pages, figures = Path(sys.argv[1]), Path(sys.argv[2])
figures.mkdir(parents=True, exist_ok=True)
for page in sorted(pages.glob("*.png")):
    im = Image.open(page).convert("RGB")
    w, h = im.size
    # The slide is a grey band with white page margins above and below; the figure is the white block inside it.
    grey = [y for y in range(h) if im.getpixel((w // 2, y))[0] < 200 or im.getpixel((5, y))[0] < 200]
    band = im.crop((0, grey[0], w, grey[-1] + 1))
    white = band.point(lambda v: 255 if v > 235 else 0).convert("L").point(lambda v: 255 if v == 255 else 0)
    px, (bw, bh) = white.load(), band.size
    # ponytail: a row or column belongs to the figure when over 30 % of it is white; fine for these slides, not for a figure on a white slide.
    rows = [y for y in range(bh) if sum(px[x, y] > 0 for x in range(0, bw, 4)) > 0.3 * bw / 4]
    # The slide template's footer strip is partly white too: it sits in the last 60 rows of the band.
    rows = [y for y in rows if y < bh - 60]
    cols = [x for x in range(bw) if sum(px[x, y] > 0 for y in range(rows[0], rows[-1], 4)) > 0.3 * (rows[-1] - rows[0]) / 4]
    box = (cols[0], rows[0], cols[-1] + 1, rows[-1] + 1)
    assert box[2] - box[0] > 500 and box[3] - box[1] > 500, (page.name, box)
    band.crop(box).save(figures / page.name)
    print(page.name, box, band.crop(box).size)
