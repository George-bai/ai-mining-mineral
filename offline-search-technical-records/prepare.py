"""Turns the public records into the searchable text, locally: one Markdown file per record, one heading per PDF page
or HTML section, and units.json listing every unit with its text (used to write the answer key and the focused set).

PDF text comes from poppler's pdftotext, one page at a time; HTML text from the SEC exhibits' own text layer (standard library only). Within a
paragraph, wrapped lines are joined; nothing else is changed. No network, no model.

python prepare.py <sources.json> <folder with the downloaded files> <out folder> [--only <regex>]
--only keeps just the pages whose text matches (the focused collection: '(?i)(molybdenum|moly) plant').
"""
import json, re, subprocess, sys
import html
from pathlib import Path


def paragraphs(text):
    out = []
    for block in re.split(r"\n\s*\n", text):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        p = lines[0]
        for l in lines[1:]:
            p = p[:-1] + l if p.endswith("-") and l[:1].islower() else p + " " + l
        out.append(p)
    return out


def pdf_units(path):
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout)[1])
    for n in range(1, pages + 1):
        text = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", str(n), "-l", str(n), path, "-"],
                              capture_output=True, text=True, check=True).stdout
        yield f"Page {n}", paragraphs(text)


HIDDEN = re.compile(r'<FONT size="1" style="font-size:1pt;color:white">(.*?)</FONT>', re.S)
HEADER = re.compile(r"Cadia Valley Operations\s+New South Wales, Australia\s+Technical Report Summary\s+"
                    r"Date:\s+\w+ \d{4}\s+Page\s+(\S+)")


def html_units(path):
    """The SEC exhibits are page images, each with its text in a hidden layer (Workiva). The running header on every
    page ("... Technical Report Summary Date: February 2026 Page 14-3") gives the printed page; it becomes the
    heading. Within the layer a paragraph break is three or more spaces; single line wraps are two."""
    t = HIDDEN.findall(Path(path).read_text(encoding="utf-8", errors="replace"))
    text = html.unescape(re.sub(r"<[^>]+>", " ", " ".join(t))).replace("\xa0", " ")
    parts = HEADER.split(text)  # [cover, page, text, page, text, ...]
    yield "Cover", paras(parts[0])
    for page, body in zip(parts[1::2], parts[2::2]):
        yield f"Page {page}", paras(body)


def paras(text):
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r" {3,}", text) if p.strip()]


def safe(p):
    # a line that Markdown would read as a heading or a code fence is kept as text
    return "\\" + p if re.match(r"\s{0,3}(#|```|~~~)", p) else p


def main():
    manifest, src, out = json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]), Path(sys.argv[3])
    only = re.compile(sys.argv[5]) if sys.argv[4:5] == ["--only"] else None
    out.mkdir(parents=True, exist_ok=True)
    units = []
    for d in manifest:
        f = src / d["file"]
        md = [f"# {d['label']}", ""]
        for name, paras in (pdf_units if f.suffix == ".pdf" else html_units)(str(f)):
            if not "".join(paras).strip() or only and not only.search("\n\n".join(paras)):
                continue
            md += [f"## {name}", "", *(safe(p) + "\n" for p in paras)]
            units.append({"doc": d["id"], "unit": name, "text": "\n\n".join(paras)})
        (out / f"{d['id']}.md").write_text("\n".join(md), encoding="utf-8")
    (out / "units.json" if only else out.parent / "units.json").write_text(json.dumps(units, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(manifest)} records, {len(units)} nonempty units")


if __name__ == "__main__":
    main()
