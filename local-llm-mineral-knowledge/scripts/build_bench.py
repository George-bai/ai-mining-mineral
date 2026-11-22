"""Build the Mineral-Term and Mineral-Property task files from the Mindat-derived raw data.

Mineral-Term   : definition -> term                      (paper Table 2, Mindat glossary)
Mineral-Property: "For the mineral X, what is its <prop>?" -> canonical property value
                  (paper Table 2 example: Actinolite / element_list -> "O, Si, Mg, Ca, Fe, H")

Sample counts follow Table 1 of the paper: 200 Mineral-Term, 576 Mineral-Property.
Selection is random from the validated candidate pool with seed 42.
"""
from __future__ import annotations

import collections
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "bench")
SEED = 42

# Properties used for the Mineral-Property task. The paper names element_list explicitly; the
# remaining fields are the canonical Mindat property columns.
PROPERTY_PRIORITY = [
    "element_list", "hardness", "crystal_system", "specific_gravity", "luster", "streak",
    "cleavage", "colour",
]


def read_jsonl(path: str):
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8"):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def clean_term_entry(row: dict) -> dict | None:
    term = (row.get("term") or "").strip()
    definition = re.sub(r"\s+", " ", (row.get("definition") or "")).strip()
    if not (2 <= len(term) <= 60) or len(definition) < 40:
        return None
    if definition.lower().startswith(("see ", "see also", "same as", "synonym of")):
        return None
    if not re.search(r"[a-z]", term, re.I):
        return None
    return {"term": term, "definition": definition}


def stratified_by_initial(pool: list[dict], n: int, seed: int) -> list[dict]:
    """Water-filling allocation over initial letters: equal shares, capped by availability."""
    rnd = random.Random(seed)
    by: dict[str, list] = collections.defaultdict(list)
    for e in pool:
        by[e["term"][0].lower()].append(e)
    for v in by.values():
        rnd.shuffle(v)
    letters = sorted(by)
    chosen, remaining = [], n
    while remaining > 0 and any(by[k] for k in letters):
        live = [k for k in letters if by[k]]
        share = max(1, remaining // len(live))
        for k in live:
            if remaining <= 0:
                break
            take = min(share, len(by[k]), remaining)
            chosen.extend(by[k][:take])
            del by[k][:take]
            remaining -= take
    return chosen


def build_term(n: int = 200) -> None:
    rows = read_jsonl(os.path.join(RAW, "mindat_glossary.jsonl"))
    if not rows:
        print("Mineral-Term: no data/raw/mindat_glossary.jsonl yet - skipping")
        return
    seen, pool = set(), []
    for r in rows:
        e = clean_term_entry(r)
        if not e:
            continue
        key = e["term"].lower()
        if key in seen:
            continue
        seen.add(key)
        pool.append(e)
    # keep definitions that are reasonably self-contained term definitions
    # The archived glossary is crawled in URL (alphabetical) order, so the pool is heavily
    # weighted to a/b/c. Sampling uniformly would inherit that artefact, so the 200 samples are
    # allocated across initial letters by water-filling: every letter gets an equal share of the
    # remaining budget, capped by how many entries that letter has.
    random.seed(SEED)
    chosen = stratified_by_initial(pool, n, SEED)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "mineral_term.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for i, e in enumerate(sorted(chosen, key=lambda e: e["term"].lower())):
            sample = {
                "id": f"term-{i:04d}",
                "type": "Mineral-Term",
                "input": {"question": e["definition"]},
                "answer": e["term"],
                "meta": {"source": "Mindat glossary", "term": e["term"]},
            }
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    letters = collections.Counter(e["term"][0].lower() for e in chosen)
    print(f"Mineral-Term: {len(pool)} valid candidates -> wrote {len(chosen)} samples "
          f"over {len(letters)} initial letters: "
          + " ".join(f"{k}{v}" for k, v in sorted(letters.items())))


def property_value_ok(prop: str, value) -> str | None:
    if value is None:
        return None
    s = re.sub(r"\s+", " ", str(value)).strip()
    if not s or s.lower() in ("none", "n/a", "-", "?", "unknown"):
        return None
    if prop in ("hardness", "specific_gravity"):
        nums = [float(m) for m in re.findall(r"\d+(?:\.\d+)?", s)]
        if not nums or any(n <= 0 or n > 1000 for n in nums):
            return None
        if len(s) > 60:
            return None
    if len(s) > 200:
        return None
    return s


def build_property(n: int = 576) -> None:
    rows = read_jsonl(os.path.join(RAW, "mindat_minerals.jsonl"))
    by_prop: dict[str, list[dict]] = {}
    seen_pairs = set()
    for r in rows:
        name = (r.get("name") or "").strip()
        if not (2 <= len(name) <= 60):
            continue
        for prop in PROPERTY_PRIORITY:
            val = property_value_ok(prop, r.get(prop))
            if not val:
                continue
            key = (name.lower(), prop)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            by_prop.setdefault(prop, []).append({"name": name, "prop": prop, "value": val})
    # Balanced selection: round-robin over properties until n samples are drawn.
    random.seed(SEED)
    pools = {p: random.sample(v, len(v)) for p, v in by_prop.items()}
    chosen: list[dict] = []
    while len(chosen) < n and any(pools.values()):
        for p in PROPERTY_PRIORITY:
            if pools.get(p):
                chosen.append(pools[p].pop())
                if len(chosen) >= n:
                    break
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "mineral_property.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for i, c in enumerate(chosen):
            sample = {
                "id": f"prop-{i:04d}",
                "type": "Mineral-Property",
                "input": {"question": f"For the mineral {c['name']}, what is its {c['prop']}?"},
                "answer": c["value"],
                "meta": {"source": "Mindat mineral species", "mineral": c["name"],
                         "property": c["prop"]},
            }
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    dist = {}
    for c in chosen:
        dist[c["prop"]] = dist.get(c["prop"], 0) + 1
    print(f"Mineral-Property: candidates {sum(len(v) for v in by_prop.values())} "
          f"-> wrote {len(chosen)} samples; per-property: {json.dumps(dist, sort_keys=True)}")


if __name__ == "__main__":
    n_term = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    n_prop = int(sys.argv[2]) if len(sys.argv) > 2 else 576
    build_term(n_term)
    build_property(n_prop)
