"""Diagnostics on round 2, after its one scoring run: not results, and nothing here changes the frozen files.

1. Baseline with the enriched search's place filter (site and concentrator named in the question): how much of the
   gap is reading the place rather than the naming conventions.
2. Questions naming Site A or Site S, whose single letters the shared stop list drops.
"""
import json, re, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
import catalog, score as S  # noqa: E402


def baseline_with_place(con, q, k=10):
    loc = catalog.parse_location(q)
    words = [w for w in catalog.WORD.findall(q.lower()) if w not in catalog.STOP]
    if not words:
        return []
    where, args = "", [" OR ".join(f'"{w}"' for w in words)]
    for col in ("site", "concentrator"):
        if loc.get(col):
            where += f" AND lower(t.{col}) = ?"
            args.append(loc[col].lower())
    rows = con.execute("SELECT t.path FROM tags_raw_fts JOIN tags t ON t.id = tags_raw_fts.rowid WHERE tags_raw_fts MATCH ?"
                       + where + " ORDER BY bm25(tags_raw_fts) LIMIT ?", args + [k]).fetchall()
    return [r[0] for r in rows]


def main(db, rd):
    con = catalog.connect(db)
    key = yaml.safe_load((Path(rd) / "key.yaml").read_text())
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(rd) / "results.jsonl").read_text().splitlines()}
    head = [q for q in key if q["counts_as"] in ("one", "several")]
    placed = [S.score(q["counts_as"], q["tags"], baseline_with_place(con, q["question"]), 10) for q in head]
    print(f"DIAGNOSTIC 1, baseline with the place filter, questions with a real tag ({len(head)}): recall@10 "
          f"{sum(placed) / len(placed):.3f}   (scored: enriched {S.mean(res[q['id']]['enriched']['at10'] for q in head)}, "
          f"baseline {S.mean(res[q['id']]['baseline']['at10'] for q in head)})")
    print("DIAGNOSTIC 2, questions naming Site A or Site S:")
    for q in key:
        if re.search(r"\bSite [AS]\b", q["question"]):
            r = res[q["id"]]
            print(f"  {q['id']} {q['counts_as']:9} enriched@10 {r['enriched']['at10']:.2f} baseline@10 {r['baseline']['at10']:.2f}"
                  f"  baseline top1: {(r['baseline']['top10'] or [['-']])[0][0].split('Mining')[-1]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
