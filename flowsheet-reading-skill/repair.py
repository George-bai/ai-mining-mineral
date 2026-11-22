"""Development only: for every chart Mermaid could not parse, write repaired/flowsheet.mmd with only the quote
marks inside labels fixed (an inch mark " after a digit becomes " in", stray quotes go, empty |""| goes).
The original stays the delivered result (a failure); the copy shows what the model read.
Usage: python3 repair.py <runs-folder>"""
import json, re, sys
from pathlib import Path


def fix_label(text):
    inner = text.strip()
    inner = re.sub(r'(\d)"', r"\1 in", inner)          # 1/2" -> 1/2 in
    inner = inner.replace('"', "").strip()
    return inner


def repair(src):
    # a subgraph id equal to a box id is not valid Mermaid: give the subgraph its own id
    sub = set(re.findall(r'^\s*subgraph\s+([A-Za-z0-9_]+)', src, flags=re.M))
    boxes = set(re.findall(r'([A-Za-z0-9_]+)\s*[\[\(\{]', re.sub(r'^\s*subgraph.*$', '', src, flags=re.M)))
    for i in sub & boxes:
        src = re.sub(rf'^(\s*subgraph\s+){i}\b', rf'\1sg_{i}', src, flags=re.M)
    out = []
    for line in src.splitlines():
        # an unquoted box label holding quotes or brackets: quote it
        line = re.sub(r'([A-Za-z0-9_]+)\[(?!["\[])([^\]]*[()"\'][^\]]*)\]',
                      lambda m: f'{m.group(1)}["{fix_label(m.group(2))}"]', line)
        if line.count('"') % 2 or '""' in line or re.search(r'\|[^|"]*"[^|]*\|', line):
            line = re.sub(r'\|([^|]*)\|', lambda m: f'|"{fix_label(m.group(1))}"|' if fix_label(m.group(1)) else "", line)
            line = re.sub(r'\["(.*?)"\]', lambda m: f'["{fix_label(m.group(1))}"]', line)
            line = re.sub(r"\['(.*?)'\]", lambda m: f'["{fix_label(m.group(1))}"]', line)
        out.append(line)
    return "\n".join(out) + "\n"


for mj in sorted(Path(sys.argv[1]).rglob("mermaid.json")):
    if mj.parent.name == "repaired" or json.loads(mj.read_text()).get("ok"):
        continue
    (mj.parent / "repaired").mkdir(exist_ok=True)
    (mj.parent / "repaired" / "flowsheet.mmd").write_text(repair((mj.parent / "flowsheet.mmd").read_text()))
    print(mj.parent / "repaired")
