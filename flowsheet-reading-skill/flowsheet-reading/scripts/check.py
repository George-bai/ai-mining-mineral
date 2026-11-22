"""Check a Mermaid flowchart of a flowsheet for the usual slips: boxes with no line in or out, boxes drawn
twice, lines Mermaid may not understand.    Usage: python3 check.py flowsheet.mmd
A light reading of Mermaid, not Mermaid itself: it points at places to look again, it does not prove the
chart right."""
import collections, re, sys

SHAPE = r'(\[\[.*?\]\]|\[\(.*?\)\]|\(\(.*?\)\)|\(\[.*?\]\)|\[".*?"\]|\(".*?"\)|\{".*?"\}|\[.*?\]|\(.*?\)|\{.*?\}|>.*?\])'
NODE = re.compile(r'([A-Za-z0-9_]+)\s*' + SHAPE)
ARROW = re.compile(r'\s*(?:<-->|-->|---|-\.->|-\.-|==>|===|--o|--x)\s*')
SKIP = re.compile(r'^\s*(flowchart|graph|subgraph|end\b|classDef|class |style |linkStyle|click |direction )')


def read(text):
    labels, edges, odd = {}, [], []
    for n, line in enumerate(text.splitlines(), 1):
        line = line.split("%%")[0].strip()
        if not line or SKIP.match(line):
            continue
        for m in NODE.finditer(line):
            label = re.sub(r'^[\[\(\{>"]+|[\]\)\}"]+$', "", m.group(2))
            labels[m.group(1)] = re.sub(r'\s+', " ", re.sub(r'<br\s*/?>', " ", label)).strip()
        if line.count('"') % 2 or '""' in line:
            odd.append((n, line + '   <- a " inside a label, or an empty label: write inches as "in", leave out empty |""|'))
            continue
        bare = NODE.sub(lambda m: m.group(1), line)
        bare = re.sub(r'\|[^|]*\|', "", bare)                    # A -->|text| B
        bare = re.sub(r'--\s+[^->]+?\s+-->', "-->", bare)         # A -- text --> B
        parts = [p.strip() for p in ARROW.split(bare)]
        if len(parts) == 1:
            ids = [p.strip() for p in parts[0].split("&")]
            if not all(re.fullmatch(r'[A-Za-z0-9_]+', i) for i in ids):
                odd.append((n, line))
            for i in ids:
                labels.setdefault(i, i)
            continue
        groups = [[i.strip() for i in p.split("&")] for p in parts]
        if not all(re.fullmatch(r'[A-Za-z0-9_]+', i) for g in groups for i in g):
            odd.append((n, line))
            continue
        for a, b in zip(groups, groups[1:]):
            edges += [(x, y) for x in a for y in b]
        for g in groups:
            for i in g:
                labels.setdefault(i, i)
    return labels, edges, odd


if __name__ == "__main__":
    labels, edges, odd = read(open(sys.argv[1]).read())
    ins, outs = collections.Counter(b for _, b in edges), collections.Counter(a for a, _ in edges)
    name = lambda i: f'{i} "{labels[i]}"'
    print(f"{len(labels)} boxes, {len(edges)} lines")
    alone = [i for i in labels if not ins[i] and not outs[i]]
    print("Boxes with no line at all (look again: every unit on a flowsheet is connected):",
          ", ".join(map(name, alone)) or "none")
    print("Boxes with lines out but none in (fine for feeds, water, reagents; otherwise look for the line in):",
          ", ".join(name(i) for i in labels if outs[i] and not ins[i]) or "none")
    print("Boxes with lines in but none out (fine for products, tailings, vents; otherwise look for the line out):",
          ", ".join(name(i) for i in labels if ins[i] and not outs[i]) or "none")
    dup = [l for l, c in collections.Counter(v.lower() for v in labels.values()).items() if c > 1]
    print("Labels used on more than one box (fine if the drawing repeats them; otherwise merge):", ", ".join(dup) or "none")
    for n, line in odd:
        print(f"Line {n} may not be valid Mermaid: {line}")
    sub = re.findall(r'^\s*subgraph\s+([A-Za-z0-9_]+)', open(sys.argv[1]).read(), flags=re.M)
    for i in sub:
        if i in labels:
            print(f'Subgraph id "{i}" is also a box id: Mermaid refuses this. Rename the subgraph (e.g. area_{i}).')
    # every unit in work/units.md ("id | label | ...") should be a box in the chart
    try:
        listed = [l.split("|")[0].strip(" -*`") for l in open("work/units.md") if "|" in l]
    except OSError:
        listed = []
    listed = [i for i in listed if re.fullmatch(r"[A-Za-z0-9_]+", i) and i.lower() not in ("id", "unit")]
    missing = [i for i in listed if i not in labels]
    if listed:
        print("Units in work/units.md that are not boxes in the chart (add them, or say why not):",
              ", ".join(missing) or "none")
