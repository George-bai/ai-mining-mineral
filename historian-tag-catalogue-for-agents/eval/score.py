"""Score the catalogue's search and the plain keyword baseline on a frozen question set, once.

    uv run python eval/score.py <catalogue.sqlite> <round folder, e.g. eval/round2>

The round folder holds test-questions.yaml and key.yaml; results.jsonl, scores.json and scores.md are written there.
Rules (fixed before round 2, 23 Nov 2026; the counting of each question is in eval/make_key.py):
  headline   questions that have a real tag ("one" and "several"): recall@5, recall@10, MRR, and paired wins and
             losses between the two methods at 10
  none       questions with no matching tag: share with a named near match in the top 10, and share whose top
             result is an exact point name (should be none)
  ambiguous  precision@10 (share of the top 10 that is a valid reading) and share with any valid reading in the top 10
"""
import hashlib, json, subprocess, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import catalog  # noqa: E402

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def score(counts_as: str, expected: list[str], got: list[str], k: int) -> float:
    hits = [p for p in expected if p in got[:k]]
    return len(hits) / len(expected) if counts_as == "several" else float(bool(hits))


def rr(expected: list[str], got: list[str]) -> float:
    ranks = [got.index(p) + 1 for p in expected if p in got]
    return 1 / min(ranks) if ranks else 0.0


def mean(xs):
    xs = list(xs)
    return round(sum(xs) / len(xs), 3) if xs else None


def main(db: str, round_dir: str):
    rd = Path(round_dir)
    con = catalog.connect(db)
    key = yaml.safe_load((rd / "key.yaml").read_text())
    rows = []
    for q in key:
        row = {k: q[k] for k in ("id", "type", "counts_as", "question")}
        for m, r in (("enriched", catalog.search(con, q["question"], limit=10)),
                     ("baseline", catalog.baseline(con, q["question"], 10))):
            got = [x["path"] for x in r]
            row[m] = {"top10": [(x["path"], x["point"]) for x in r], "at5": score(q["counts_as"], q["tags"], got, 5),
                      "at10": score(q["counts_as"], q["tags"], got, 10), "rr": rr(q["tags"], got),
                      "precision10": sum(p in q["tags"] for p in got) / 10,
                      "top_is_exact_name": bool(r) and "exact point name" in r[0].get("why", "")}
        rows.append(row)
    M = ("enriched", "baseline")
    head = [r for r in rows if r["counts_as"] in ("one", "several")]
    none = [r for r in rows if r["counts_as"] == "none"]
    amb = [r for r in rows if r["counts_as"] == "ambiguous"]
    out = {
        "headline": {m: {"n": len(head), "recall_at5": mean(r[m]["at5"] for r in head),
                         "recall_at10": mean(r[m]["at10"] for r in head), "mrr": mean(r[m]["rr"] for r in head)} for m in M},
        "paired_at10": {"enriched_better": sum(r["enriched"]["at10"] > r["baseline"]["at10"] for r in head),
                        "baseline_better": sum(r["enriched"]["at10"] < r["baseline"]["at10"] for r in head),
                        "same": sum(r["enriched"]["at10"] == r["baseline"]["at10"] for r in head)},
        "none": {m: {"n": len(none), "near_match_at10": mean(r[m]["at10"] for r in none),
                     "top_is_exact_name": mean(float(r[m]["top_is_exact_name"]) for r in none)} for m in M},
        "ambiguous": {m: {"n": len(amb), "precision_at10": mean(r[m]["precision10"] for r in amb),
                          "any_valid_at10": mean(r[m]["at10"] for r in amb)} for m in M},
        "by_type": {t: {m: {"n": sum(r["type"] == t for r in rows), "at10": mean(r[m]["at10"] for r in rows if r["type"] == t)}
                        for m in M} for t in sorted({r["type"] for r in rows})},
        "provenance": {"catalogue": sha(db), "catalog.py": sha(ROOT / "catalog.py"),
                       "enrichment.yaml": sha(ROOT / "config" / "enrichment.yaml"),
                       "test-questions.yaml": sha(rd / "test-questions.yaml"), "key.yaml": sha(rd / "key.yaml"),
                       "git": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                                             cwd=ROOT).stdout.strip() + " (files uncommitted)"},
    }
    (rd / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (rd / "scores.json").write_text(json.dumps(out, indent=1))
    h, p = out["headline"], out["paired_at10"]
    md = ["| | Enriched search | Plain keyword baseline |", "|---|---|---|",
          f"| Questions with a real tag ({h['enriched']['n']}): recall@5 / recall@10 / MRR | "
          f"{h['enriched']['recall_at5']} / {h['enriched']['recall_at10']} / {h['enriched']['mrr']} | "
          f"{h['baseline']['recall_at5']} / {h['baseline']['recall_at10']} / {h['baseline']['mrr']} |",
          f"| Paired at 10 | better on {p['enriched_better']} | better on {p['baseline_better']} (same on {p['same']}) |",
          f"| No such tag ({out['none']['enriched']['n']}): near match in top 10 / top result an exact name | "
          f"{out['none']['enriched']['near_match_at10']} / {out['none']['enriched']['top_is_exact_name']} | "
          f"{out['none']['baseline']['near_match_at10']} / {out['none']['baseline']['top_is_exact_name']} |",
          f"| Ambiguous ({out['ambiguous']['enriched']['n']}): precision@10 / any valid in top 10 | "
          f"{out['ambiguous']['enriched']['precision_at10']} / {out['ambiguous']['enriched']['any_valid_at10']} | "
          f"{out['ambiguous']['baseline']['precision_at10']} / {out['ambiguous']['baseline']['any_valid_at10']} |"]
    md += [f"| Type {t} ({v['enriched']['n']}): recall@10 | {v['enriched']['at10']} | {v['baseline']['at10']} |"
           for t, v in out["by_type"].items()]
    (rd / "scores.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
