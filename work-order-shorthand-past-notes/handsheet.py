"""The blind hand check: sheets of single answers under random ids, and the merge back into check.json.

    python3 handsheet.py make <notes.json> <answers folder> <No. 13 results.json> <out folder> [--readers 4]
    python3 handsheet.py merge <out folder> <answers folder> <check.json> [--blind-only | --as-read]

make: every answer of both versions (search, glossary rerun) plus 40 of No. 13's recorded glossary answers (all 17 it
judged meaning lost, 23 drawn from the rest, seed 16), each under a random four-digit id, shuffled, split into equal
sheets. A sheet shows the note, MaintNorm's key, the answer's plain text and unsure list, the script's flags and its
first pass per piece of shorthand; never the version. The map from id to note and version goes to <out>/map.json,
which no reader opens. Ids and order come from the operating system's random source, so nothing in the sheet
follows from the note id.

merge: each reader writes <out>/verdicts-<n>.txt, one entry per line, every item of its sheet read:
    r1234 meaning=0 diagnosis=1 | why       verdicts that differ from meaning=1 diagnosis=0 done=0 added=0
    r1234|3 wrong | why                     a corrected item outcome (right, wrong, unsure, kept)
    doubt r1234|3 | why                     the key itself looks wrong here (logged; the item stays scored on the key)
The merge maps ids back, writes check.json in score.py's form (keys '<note id>|<version>' and '...|<token index>',
'_answers' with a digest of each answer read, '_key_doubts'), and '_calibration': the readers' verdicts on No. 13's
archived answers beside No. 13's recorded ones. Then, unless --blind-only, it applies <out>/after-unblinding.txt, the
verdicts changed with the versions known (one line each, with its reason), and lists them under '_after_unblinding';
without that file it stops.
--as-read gives the readers' verdicts as first written, before the settlement made before unblinding. Each verdict
file must open with '# read <first id> to <last id>, all <n> entries' for its whole sheet, or the merge refuses it.
"""
import json, random, re, sys
from pathlib import Path
from score import CONDS, digest, parse, score

SYS = random.SystemRandom()


def entry(rid, r):
    out = [f"## {rid}", f"NOTE: {r['note']}", f"KEY:  {r['key']}", f"PLAIN: {r['plain']}"]
    if r.get("unsure"):
        out.append(f"   unsure: {r['unsure']}")
    if r.get("diag_flags") or r.get("done_flags"):
        out.append(f"   flags: diagnosis {r['diag_flags']} done {r['done_flags']}")
    for it in r["items"]:
        out.append(f"   {it['i']:>2} {it['raw']!r} = {it['meaning']!r} {it['script']}: {it['read']}")
    return "\n".join(out) + "\n"


def make(notes_path, answers, archive_path, out, readers=4):
    notes = json.loads(Path(notes_path).read_text(encoding="utf-8"))
    rows = score(notes, answers, {}, {})
    assert len(rows) == len(CONDS) * len(notes), f"{len(rows)} answers, expected {len(CONDS) * len(notes)}"
    old = [r for r in json.loads(Path(archive_path).read_text(encoding="utf-8"))["answers"] if r["condition"] == "glossary"]
    lost = [r for r in old if r["meaning"] is False]
    rest = sorted((r for r in old if r["meaning"] is True), key=lambda r: r["id"])
    calib = lost + random.Random(16).sample(rest, 40 - len(lost))
    items = [(r, {"id": r["id"], "version": r["condition"]}) for r in rows] + \
            [(r, {"id": r["id"], "version": "archive13", "recorded": {k: r[k] for k in ("meaning", "diagnosis", "done", "added")}}) for r in calib]
    ids = SYS.sample(range(1000, 10000), len(items))
    SYS.shuffle(items)
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    mapping = {}
    size = -(-len(items) // readers)
    for k in range(readers):
        part = items[k * size:(k + 1) * size]
        text = []
        for (r, m), n in zip(part, ids[k * size:(k + 1) * size]):
            rid = f"r{n}"
            mapping[rid] = m | {"sheet": k + 1}
            text.append(entry(rid, r))
        (out / f"sheet-{k + 1}.md").write_text("\n".join(text), encoding="utf-8")
    (out / "map.json").write_text(json.dumps(mapping, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} items in {readers} sheets of up to {size}")


def parse_verdicts(text):
    v, fixes, doubts = {}, {}, {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        head, _, why = line.partition(" | ")
        parts = head.split()
        if parts[0] == "doubt":
            doubts[parts[1]] = why.strip()
        elif parts[0].count("|") == 1:
            assert parts[1] in ("right", "wrong", "unsure", "kept"), line
            fixes[parts[0]] = {"outcome": parts[1], "why": why.strip()}
        else:
            d = {k: x == "1" for k, x in (p.split("=") for p in parts[1:])}
            assert re.fullmatch(r"r\d{4}", parts[0]) and set(d) <= {"meaning", "diagnosis", "done", "added"}, line
            v.setdefault(parts[0], {}).update(d | {"why": why.strip()})
    return v, fixes, doubts


def after_unblinding(check, path):
    """Changes made with the versions known: '<note id>|<version> meaning=0 | why' or '<note id>|<version>|<i> right | why'."""
    done, text = [], Path(path).read_text(encoding="utf-8")
    if not any(l.strip() and not l.startswith("#") for l in text.splitlines()) and "# no verdict changed after unblinding" not in text:
        raise SystemExit(f"{path}: no changes listed; a file with none says '# no verdict changed after unblinding'")
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        head, _, why = line.partition(" | ")
        parts = head.split()
        key = parts[0]
        if key.count("|") == 2:
            assert parts[1] in ("right", "wrong", "unsure", "kept"), line
            check[key] = {"outcome": parts[1], "why": why.strip(), "after_unblinding": True}
        else:
            assert key in check, f"{key}: no blind verdict to change"
            d = {k: x == "1" for k, x in (p.split("=") for p in parts[1:])}
            check[key] = check[key] | d | {"why": why.strip(), "after_unblinding": True}
        done.append(line)
    return done


def first_reading(text):
    """The verdicts as the reader first wrote them: lines added by the settlement before unblinding dropped, lines it
    withdrew restored."""
    out = []
    for line in text.splitlines():
        m = re.match(r"# (r\d{4} meaning=0) withdrawn \(settled before unblinding", line)
        if m:
            out.append(f"{m[1]} | as first read")
        elif "(settled before unblinding" not in line or line.startswith("#"):
            out.append(line)
    return "\n".join(out)


def merge(out, answers, check_path, blind_only=False, as_read=False):
    out = Path(out)
    mapping = json.loads((out / "map.json").read_text(encoding="utf-8"))
    check, calib, doubts = {}, {}, {}
    for k in sorted({m["sheet"] for m in mapping.values()}):
        f = out / f"verdicts-{k}.txt"
        if not f.exists():
            raise SystemExit(f"{f} missing: every sheet must be read before the merge")
        text = f.read_text(encoding="utf-8")
        order = re.findall(r"^## (r\d{4})$", (out / f"sheet-{k}.md").read_text(encoding="utf-8"), re.M)
        head = re.match(r"# read (r\d{4}) to (r\d{4}), all (\d+) entries", text)
        if not head or (head[1], head[2], int(head[3])) != (order[0], order[-1], len(order)):
            raise SystemExit(f"{f}: its first line must say the reader read the whole sheet: "
                             f"'# read {order[0]} to {order[-1]}, all {len(order)} entries'")
        if not re.search(r"^r\d{4}", text, re.M) and "# no entry differs from the defaults" not in text:
            raise SystemExit(f"{f}: no verdict lines; a reader who found nothing to change writes "
                             "'# no entry differs from the defaults'")
        if as_read:
            text = first_reading(text)
        v, fixes, dd = parse_verdicts(text)
        for rid in [r for r, m in mapping.items() if m["sheet"] == k]:
            m = mapping[rid]
            verdict = {"meaning": True, "diagnosis": False, "done": False, "added": False} | v.get(rid, {})
            if m["version"] == "archive13":
                calib[rid] = {"note": m["id"], "recorded": m["recorded"], "readers": verdict}
                continue
            check[f"{m['id']}|{m['version']}"] = verdict | {"rid": rid}
            for key, fx in fixes.items():
                if key.split("|")[0] == rid:
                    check[f"{m['id']}|{m['version']}|{key.split('|')[1]}"] = fx | {"rid": rid}
            for key, why in dd.items():
                if key.split("|")[0] == rid:
                    doubts[f"{m['id']}|{key.split('|')[1]}"] = why
        unknown = [r for r in list(v) + [x.split("|")[0] for x in fixes] if r not in mapping or mapping[r]["sheet"] != k]
        if unknown:
            raise SystemExit(f"verdicts-{k}.txt names ids not on its sheet: {unknown[:5]}")
    # each sheet is the record of what its reader saw: the merge rebuilds every entry from the answers now on disk and
    # refuses to run if any differs (plain text, unsure list, flags, the reading of each piece of shorthand)
    shown = {}
    for f in sorted(out.glob("sheet-*.md")):
        for block in f.read_text(encoding="utf-8").split("\n## ")[0:]:
            block = block if block.startswith("## ") else "## " + block
            shown[block.split("\n", 1)[0][3:].strip()] = block.strip()
    notes = json.loads((Path(__file__).parent / "notes-test.json").read_text(encoding="utf-8"))
    rows = {(r["id"], r["condition"]): r for r in score(notes, answers, {}, {})}
    for rid, m in mapping.items():
        if m["version"] != "archive13" and entry(rid, rows[(m["id"], m["version"])]).strip() != shown[rid]:
            raise SystemExit(f"{rid} ({m['id']}|{m['version']}): the answer differs from the one its sheet showed")
    seen = {}
    for key in [k for k in check if k.count("|") == 1]:
        nid, ver = key.split("|")
        seen[key] = digest(parse(json.loads((Path(answers) / ver / f"{nid}.json").read_text(encoding="utf-8"))["content"]))
    agree = sum(c["recorded"]["meaning"] == c["readers"]["meaning"] for c in calib.values())
    if not blind_only and not (out / "after-unblinding.txt").exists():
        raise SystemExit(f"{out / 'after-unblinding.txt'} missing: the final result applies it; for the blind result use --blind-only")
    late = [] if blind_only else after_unblinding(check, out / "after-unblinding.txt")
    result = dict(sorted(check.items())) | {"_answers": seen, "_key_doubts": doubts, "_after_unblinding": late, "_calibration": {
        "items": calib, "meaning_agree": agree, "n": len(calib),
        "recorded_lost_read_lost": sum(c["recorded"]["meaning"] is False and c["readers"]["meaning"] is False for c in calib.values()),
        "recorded_lost": sum(c["recorded"]["meaning"] is False for c in calib.values())}}
    Path(check_path).write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{sum(1 for k in check if k.count('|') == 1)} verdicts, {len(calib)} calibration items, meaning agrees on {agree}")


if __name__ == "__main__":
    v, fx, dd = parse_verdicts("r1234 meaning=0 added=1 | adds a part\nr1234|3 wrong | strut\ndoubt r1234|3 | key odd\n")
    assert v["r1234"] == {"meaning": False, "added": True, "why": "adds a part"} and fx["r1234|3"]["outcome"] == "wrong"
    assert dd == {"r1234|3": "key odd"}
    if sys.argv[1] == "make":
        make(*sys.argv[2:6], **({"readers": int(sys.argv[7])} if "--readers" in sys.argv else {}))
    else:
        merge(*sys.argv[2:5], blind_only="--blind-only" in sys.argv or "--as-read" in sys.argv, as_read="--as-read" in sys.argv)
