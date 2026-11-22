"""Cut a flowsheet image into overlapping, enlarged tiles with rulers in drawing coordinates, and start the
notes file with one empty section per tile.
Usage: python3 tile.py <drawing.png> <work-folder>       Needs Python 3 with Pillow.
Writes <work-folder>/tiles/r<row>c<col>.png and, if it does not exist yet, <work-folder>/notes.md."""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

MARGIN = 34   # white border for the rulers


def with_rulers(im, x0, y0, x1, y1, title):
    """Enlarge the part (x0, y0)-(x1, y1) of im to at most 1400 pixels and draw rulers in drawing pixels."""
    part = im.crop((x0, y0, x1, y1))
    scale = min(2.5, 1400 / max(part.width, part.height))
    part = part.resize((round(part.width * scale), round(part.height * scale)), Image.LANCZOS)
    page = Image.new("RGB", (part.width + MARGIN, part.height + 2 * MARGIN), "white")
    page.paste(part, (MARGIN, 2 * MARGIN))
    d = ImageDraw.Draw(page)
    font = ImageFont.load_default(size=15)
    d.text((MARGIN, 4), title, fill="red", font=font)
    step = 50 if (x1 - x0) < 500 else 100
    for x in range(math.ceil(x0 / step) * step, x1 + 1, step):          # top ruler: drawing x
        px = MARGIN + round((x - x0) * scale)
        d.line((px, 2 * MARGIN - 8, px, 2 * MARGIN), fill="red")
        d.text((px + 2, MARGIN + 4), str(x), fill="red", font=font)
    for y in range(math.ceil(y0 / step) * step, y1 + 1, step):          # left ruler: drawing y
        py = 2 * MARGIN + round((y - y0) * scale)
        d.line((MARGIN - 8, py, MARGIN, py), fill="red")
        d.text((1, py + 2), str(y), fill="red", font=font)
    return page


if __name__ == "__main__":
    src, work = Path(sys.argv[1]), Path(sys.argv[2])
    (work / "tiles").mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    W, H = im.size
    cols, rows = max(1, math.ceil(W / 700)), max(1, math.ceil(H / 700))   # about 700 pixels of drawing per tile
    tw, th = math.ceil(W / cols), math.ceil(H / rows)
    ov = int(0.12 * min(tw, th))                                         # tiles overlap, so nothing is cut in half
    print(f"{W} x {H} pixels -> {rows} rows x {cols} columns of tiles. Rulers show drawing pixels.")
    sections = []
    for r in range(rows):
        for c in range(cols):
            x0, y0 = max(0, c * tw - ov), max(0, r * th - ov)
            x1, y1 = min(W, (c + 1) * tw + ov), min(H, (r + 1) * th + ov)
            name = work / "tiles" / f"r{r}c{c}.png"
            with_rulers(im, x0, y0, x1, y1, f"tile r{r}c{c}: drawing x {x0}-{x1}, y {y0}-{y1}").save(name)
            print(f"{name}  x {x0}-{x1}  y {y0}-{y1}")
            sections.append(f"## r{r}c{c} (x {x0}-{x1}, y {y0}-{y1})\nunits:\nlines:\n")
    notes = work / "notes.md"
    if not notes.exists():
        notes.write_text("# Tile notes: fill in each section right after looking at its tile\n\n" + "\n".join(sections))
        print(f"{notes}: one empty section per tile, waiting for your notes")
