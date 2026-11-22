"""Blind hand-check sheets: every distinct excerpt list (first 10 excerpts) under a random ID, without the system,
collection or repeat, in a random order, split into batches for readers. The ID-to-run map is written apart.

python handsheet.py <runs folder> <out folder> [batches] [id prefix, default L]
Writes <out>/map.json (not for readers) and <out>/sheet-<n>.md.
"""
import hashlib, json, random, sys
from pathlib import Path

HERE = Path(__file__).parent
# --questions <file>: another key (questions-dated.json for the re-run of q01-q03); taken out of argv before the rest
KEY = sys.argv.pop(sys.argv.index("--questions") + 1) if "--questions" in sys.argv else HERE / "questions.json"
if "--questions" in sys.argv:
    sys.argv.remove("--questions")
Q = json.loads(Path(KEY).read_text())
QUESTIONS = {q["id"]: q for q in Q["questions"]}


def main():
    runs, out = Path(sys.argv[1]), Path(sys.argv[2])
    batches = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    prefix = sys.argv[4] if len(sys.argv) > 4 else "L"
    out.mkdir(parents=True, exist_ok=True)
    lists = {}
    for f in sorted(runs.glob("*/*/*/q*.*.json")):
        rec = json.loads(f.read_text())
        rows = [(Path(r["path"]).stem, (r.get("heading") or "").split(" / ")[-1], r.get("content", "")) for r in rec["results"][:10]]
        key = hashlib.sha256(json.dumps([rec["question"], rows]).encode()).hexdigest()
        system, coll, rep = f.parts[-4:-1]
        lists.setdefault(key, {"question": rec["question"], "rows": rows, "runs": []})["runs"].append(
            f"{system}|{coll}|{rep}|{rec['mode']}|{rec['question']}")
    keys = sorted(lists)
    random.Random(21112026).shuffle(keys)
    ids = {k: f"{prefix}{i + 1:03d}" for i, k in enumerate(keys)}
    (out / "map.json").write_text(json.dumps({ids[k]: lists[k]["runs"] for k in keys}, indent=1))
    per = -(-len(keys) // batches)
    for b in range(batches):
        md = []
        for k in keys[b * per:(b + 1) * per]:
            L, q = lists[k], QUESTIONS[lists[k]["question"]]
            md += [f"## {ids[k]} · {q['id']}: {q['text']}", ""]
            if not q["needs"]:
                md += ["Needs: nothing; these records hold no shift-level recovery. Note any excerpt a reader could mistake for one.", ""]
            for fact in q["needs"]:
                f = Q["facts"][fact]
                pages = "; ".join(f"{e['doc']} {e['page']}" for e in f["evidence"])
                strict = q.get("strict", {}).get(fact)
                md += [f"- **{fact}**: {f['says']} Accepted pages: {pages}." + (f" Edition required: {strict} only." if strict else "")]
            md += ["", "| # | record | page | displayed text |", "|---|---|---|---|"]
            for i, (doc, page, text) in enumerate(L["rows"], 1):
                md.append(f"| {i} | {doc} | {page} | {' '.join(text.split()).replace('|', '/')} |")
            md += [""]
        (out / f"sheet-{b + 1}.md").write_text("\n".join(md))
    print(f"{len(keys)} distinct lists from {sum(len(v['runs']) for v in lists.values())} runs, {batches} sheets")


if __name__ == "__main__":
    main()
