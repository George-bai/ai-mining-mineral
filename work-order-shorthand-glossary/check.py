"""Turns the hand check's notes into check.json, the file score.py applies.

    python3 check.py <check.txt> <check.json> <answers folder>

check.txt, written while reading the blind sheet (score.py --sheet), one entry per line:
    read A-test-000 A-test-024            every answer of these notes (by sheet order) has been read in full
    A-test-007|x meaning=0 added=1 | why   verdicts that differ from the default, and the reason
    A-test-007|x|3 wrong | why            a corrected item outcome (right, wrong, unsure, kept), and the reason
    doubt A-test-007|3 | why              the key itself looks wrong here (logged, the item stays scored on the key)
An answer in a block marked read gets meaning=1 diagnosis=0 done=0 added=0 unless a line says otherwise; an answer
outside every read block gets no verdict, so score.py --final refuses to report. The answers folder is the one the
sheet was made from: check.json keeps a digest of every answer read, so its verdicts never pass to another answer.
"""
import json, re, sys
from pathlib import Path
from score import digest, labels, parse


def convert(text, ids):
    check, doubts, read = {}, {}, set()
    for line in text.splitlines():
        if not line.strip():
            continue
        head, _, why = line.partition(" | ")
        parts = head.split()
        if parts[0] == "read":
            lo, hi = ids.index(parts[1]), ids.index(parts[2])
            read.update(ids[lo:hi + 1])
        elif parts[0] == "doubt":
            doubts[parts[1]] = why.strip()
        elif parts[0].count("|") == 2:
            assert parts[1] in ("right", "wrong", "unsure", "kept"), line
            check[parts[0]] = {"outcome": parts[1], "why": why.strip()}
        else:
            v = {k: v == "1" for k, v in (p.split("=") for p in parts[1:])}
            assert set(v) <= {"meaning", "diagnosis", "done", "added"}, line
            check.setdefault(parts[0], {}).update(v | {"why": why.strip()})
    for nid in read:
        for label in "xy":
            v = check.setdefault(f"{nid}|{label}", {})
            for k, d in (("meaning", True), ("diagnosis", False), ("done", False), ("added", False)):
                v.setdefault(k, d)
    for k in [k for k in check if k.count("|") == 1 and k.split("|")[0] not in read]:
        raise SystemExit(f"{k} has a verdict but its note is in no read block")
    return dict(sorted(check.items())) | {"_key_doubts": doubts, "_read": sorted(read)}


if __name__ == "__main__":
    ids = ["n1", "n2", "n3"]
    t = convert("read n1 n2\nn2|y meaning=0 added=1 | adds a part\nn2|y|4 wrong | strut for stud\n", ids)
    assert t["n1|x"] == {"meaning": True, "diagnosis": False, "done": False, "added": False}
    assert t["n2|y"]["meaning"] is False and t["n2|y"]["added"] is True and "n3|x" not in t
    assert t["n2|y|4"] == {"outcome": "wrong", "why": "strut for stud"}
    src, out, runs = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    notes = json.loads((Path(__file__).parent / "notes-test.json").read_text(encoding="utf-8"))
    t = convert(src.read_text(encoding="utf-8"), [n["id"] for n in notes])
    t["_answers"] = {f"{nid}|{lab}": digest(parse(json.loads((runs / cond / f"{nid}.json").read_text(encoding="utf-8"))["content"]))
                     for nid in t["_read"] for lab, cond in sorted(labels(nid).items())}
    out.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
