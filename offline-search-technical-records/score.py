"""First-pass scoring of the search runs against questions.json; every list is then read by hand (check.json).

An excerpt is one passage as SAG-Wiki displays it, in its order; only the first 10 count. A fact is shown at rank r
when the excerpts ranked 1..r that come from one of the fact's pages together display every phrase listed for that
page. From the other edition of a strict fact it is "right fact, wrong edition" and earns nothing. A question is
complete at k when every fact it needs is shown by rank k. "Page" ranks record the first excerpt from a right page,
whether or not it displays the words.

python score.py --check-key <units.json> [--focused]   each page holds its phrases; reports any other page that holds them all;
                                                       fails on an empty file or, unless --focused, a missing evidence page
python score.py <runs folder> [<check.json>] [--questions <key>]   writes <runs folder>/scores.json and prints a summary
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
# --questions <file>: another key (questions-dated.json for the re-run of q01-q03); taken out of argv before the rest
KEY = sys.argv.pop(sys.argv.index("--questions") + 1) if "--questions" in sys.argv else HERE / "questions.json"
if "--questions" in sys.argv:
    sys.argv.remove("--questions")
Q = json.loads(Path(KEY).read_text())
QUESTIONS = {q["id"]: q for q in Q["questions"]}
CAP = 10


def norm(s):
    s = s.translate(str.maketrans({"–": "-", "—": "-", "−": "-", "’": "'", "‘": "'", "“": '"', "”": '"', "\xa0": " "}))
    return re.sub(r"\s+", " ", s).strip().lower()


def where(r):
    return Path(r["path"]).stem, (r.get("heading") or "").split(" / ")[-1]


def fact_ranks(fact, results, strict=None):
    """(first rank shown from an accepted page, first rank shown from the wrong edition, first rank on a right page)"""
    f = Q["facts"][fact]
    shown = wrong = page = None
    seen = {}
    for i, r in enumerate(results[:CAP], 1):
        doc, pg = where(r)
        for e in f["evidence"]:
            if (doc, pg) != (e["doc"], e["page"]):
                continue
            ok_edition = not strict or doc == strict
            if ok_edition and page is None:
                page = i
            text = seen[(doc, pg)] = seen.get((doc, pg), "") + " " + norm(r.get("content", ""))
            if all(norm(n) in text for n in e["need"]):
                if ok_edition and shown is None:
                    shown = i
                elif not ok_edition and wrong is None:
                    wrong = i
    return shown, wrong, page


def score_list(q, results, corrections=None):
    out = {"excerpts_returned": len(results), "excerpts": min(len(results), CAP), "shown": {}, "wrong_edition": {}, "page": {}, "partial": {}}
    for fact in q["needs"]:
        shown, wrong, page = fact_ranks(fact, results, q.get("strict", {}).get(fact))
        if corrections and fact in corrections:  # a hand correction; its reason is in check.json
            shown = corrections[fact]["shown"]
        out["shown"][fact], out["wrong_edition"][fact], out["page"][fact] = shown, wrong, page
        parts = [i for i, r in enumerate(results[:CAP], 1) if list(where(r)) in Q["facts"][fact].get("partial", [])]
        out["partial"][fact] = parts[0] if parts else None
    for k in (5, 10):
        out[f"complete@{k}"] = bool(q["needs"]) and all((out["shown"][f] or 99) <= k for f in q["needs"])
        out[f"pages@{k}"] = bool(q["needs"]) and all((out["page"][f] or 99) <= k for f in q["needs"])
    return out


def check_key(units_path, collection_may_lack_pages=False):
    units = json.loads(Path(units_path).read_text())
    if not units:
        print("BAD no pages in", units_path)
        return False
    text = {(u["doc"], u["unit"]): norm(u["text"]) for u in units}
    ok = True
    for name, f in Q["facts"].items():
        for e in f["evidence"]:
            t = text.get((e["doc"], e["page"]))
            if t is None:  # the focused collection holds only the pages naming the plant; the full one must hold all
                print(f"{'--' if collection_may_lack_pages else 'BAD'} {name:15s} {e['doc']} {e['page']} not in this collection")
                ok &= collection_may_lack_pages
                continue
            missing = [n for n in e["need"] if norm(n) not in t]
            others = [k for k, v in text.items() if k != (e["doc"], e["page"]) and all(norm(n) in v for n in e["need"])
                      and [k[0], k[1]] not in [[x["doc"], x["page"]] for x in f["evidence"]]]
            good = not missing and not others
            ok &= good
            print(f"{'ok ' if good else 'BAD'} {name:15s} {e['doc']} {e['page']}"
                  + (f"  missing {missing}" if missing else "") + (f"  also on {others}" if others else ""))
    return ok


def main():
    if sys.argv[1] == "--check-key":
        sys.exit(0 if check_key(sys.argv[2], "--focused" in sys.argv) else 1)
    runs = Path(sys.argv[1])
    corrections = json.loads(Path(sys.argv[2]).read_text())["corrections"] if len(sys.argv) > 2 else {}
    out, problems = {}, []
    # every planned run must be there: seven ways of searching, both collections, two repeats each (run_everything.sh)
    expected = {(s, c, r) for s in ("keyword", "tinybert", "minilm", "qwen-rr", "hindsight", "d1", "knowline")
                for c in ("full", "focused") for r in ("1", "2")}
    found = {p.parts[-3:] for p in runs.glob("*/*/*") if p.is_dir()}
    problems += [f"{s}/{c}/{r}: missing (planned, not run)" for s, c, r in sorted(expected - found)]
    for run in sorted(p for p in runs.glob("*/*/*") if p.is_dir()):  # <system>/<collection>/<repeat>
        system, coll, rep = run.parts[-3:]
        meta = json.loads((run / "run.json").read_text()) if (run / "run.json").exists() else None
        if meta is None:
            problems.append(f"{system}/{coll}/{rep}: no run.json (the run did not finish)")
            continue
        for mode in meta.get("modes", ["fast", "deep"]):
            files = {f.name.split(".")[0]: f for f in run.glob(f"q*.{mode}.json")}
            if set(files) != set(QUESTIONS):
                problems.append(f"{system}/{coll}/{rep} {mode}: missing {sorted(set(QUESTIONS) - set(files))}")
            for qid, f in sorted(files.items()):
                rec = json.loads(f.read_text())
                key = f"{system}|{coll}|{rep}|{mode}|{qid}|"
                c = {k[len(key):]: v for k, v in corrections.items() if k.startswith(key)}
                s = score_list(QUESTIONS[qid], rec["results"], c)
                s["seconds"] = rec["seconds"]
                out.setdefault(system, {}).setdefault(coll, {}).setdefault(rep, {}).setdefault(mode, {})[qid] = s
    if not out:
        print(f"PROBLEM no finished runs under {runs}")
        return 1
    (runs / "scores.json").write_text(json.dumps(out, indent=1))
    n = sum(1 for q in Q["questions"] if q["needs"])
    for system, colls in out.items():
        for coll, reps in sorted(colls.items()):
            for rep, modes in sorted(reps.items()):
                for mode, qs in modes.items():
                    c5, c10 = (sum(s[f"complete@{k}"] for s in qs.values()) for k in (5, 10))
                    p5 = sum(s["pages@5"] for s in qs.values())
                    print(f"{system:10s} {coll:8s} {rep} {mode}: complete@5 {c5:2d}/{n}  @10 {c10:2d}/{n}  right pages@5 "
                          f"{p5:2d}/{n}  median {median([s['seconds'] for s in qs.values()]):.1f} s"
                          f"  q04 excerpts {qs.get('q04', {}).get('excerpts_returned')}")
    for p in problems:
        print("PROBLEM", p)
    return 1 if problems else 0


def median(v):
    v = sorted(v)
    return (v[(len(v) - 1) // 2] + v[len(v) // 2]) / 2


if __name__ == "__main__":
    sys.exit(main())
