"""Score each chart against the answer key of its drawing.

Usage: python3 score.py <keys-folder> <runs-folder>
  Finds every mermaid.json (from render.py) under <runs-folder>, takes the drawing from the folder name
  (p39, p37, ...), scores it against <keys-folder>/<drawing>*.yaml and writes score.json beside it.
  Every chart is also checked by hand: the reader looks at the chart beside the key, and where the automatic
  pairing got a box wrong (a name written differently, two units drawn as one box, one unit split in two),
  writes the right pairing and the reason into check.json beside mermaid.json:
    {"checked": "<who, date>", "pairing": {"<chart box id>": {"to": ["<key id>", ...], "why": "..."}},
     "notes": ["..."]}
  An empty "to" marks a box as matching nothing. score.json records whether and by whom a chart was checked.
       python3 score.py show <chart folder>   prints a chart beside its key for that check
       python3 score.py test                  runs the self-check.

How a chart is scored (the rules of the keys are in reference/README.md):
1. Each box in the chart is paired with the key items whose label (or plain name) it matches best. A box
   that matches several items with the same label is settled by its neighbours; inputs and outputs with
   the same label (six "REAGENTS") may stay paired with the whole set.
2. Junctions and carriers in the key, and boxes that match nothing, are passed through on both sides:
   A -> sump -> B counts as A -> B.
3. Streams found: key streams (sure ones only) that the chart has. Lines right: chart lines that are in the
   key. Lines that match only an unsure stream count neither way. Loops found: key loops whose every step
   the chart has.
"""
import difflib, json, os, re, subprocess, sys
from pathlib import Path

import yaml

PASS = {"junction", "carrier"}


NOISE = {"UNLABELLED", "UNLABELED", "LABEL", "LABELLED", "LABELED"}   # charts write "(unlabelled)" into a box's label


def words(s):
    s = re.sub(r"[^A-Z0-9]+", " ", (s or "").upper().replace("&", " AND ")).split()
    return [w[:-1] if len(w) > 3 and w.endswith("S") and not w.endswith("SS") else w for w in s if w not in NOISE]


def sim(box, item):
    full = words(box)
    # The same label, word for word (counts included): above every near match, so "APRON FEEDERS (4)" is never
    # tied with "APRON FEEDER"; boxes and items that share one label still tie with each other.
    if item["label"] and full == words(item["label"]):
        return 1.05
    # In the word-overlap tests a bare number is left out ("Cyclone (1)" only tells repeats apart); the
    # whole-label comparison keeps it, so "ROUGHER FLOTATION 2" still differs from "ROUGHER FLOTATION 1".
    b = [w for w in full if not w.isdigit()] or full
    best = 0.0
    for text in (item["label"], item["name"]):
        k = words(text)
        if not k or not b:
            continue
        r = difflib.SequenceMatcher(None, " ".join(full), " ".join(k)).ratio()
        # one label holds the other (a box may add tonnages, or shorten); against a plain-words name, only if
        # the box names the same kind of thing (the name's last word): "BALL MILLS (upper)" is not "upper ball
        # mill cyclones"
        if (set(k) <= set(b) or set(b) <= set(k)) and (text == item["label"] or k[-1] in b):
            r = max(r, 0.7 + 0.3 * len(set(b) & set(k)) / len(set(b) | set(k)))
        best = max(best, r)
    # An unlabelled unit can only be named generically: a box "Screen" may well be the unlabelled screen. The
    # key names an unlabelled unit with its type last ("refractory SAG discharge screen").
    n = words(item["name"])
    if not item["label"] and item["kind"] not in PASS and b and set(b) <= set(n) and n[-1] in b:
        best = max(best, 0.97)
    return best


def collapse(nodes, edges, passthrough):
    """Edges between non-pass-through nodes, following paths through pass-through ones.
    edges: {(a, b): sure}; returns {(a, b): sure} where sure means some all-sure path exists."""
    out = {}
    nxt = {}
    for (a, b), sure in edges.items():
        nxt.setdefault(a, []).append((b, sure))
    for start in nodes:
        if start in passthrough:
            continue
        stack, seen = [(start, True)], set()
        while stack:
            u, sure = stack.pop()
            for v, s in nxt.get(u, []):
                ok = sure and s
                if v in passthrough:
                    if (v, ok) not in seen:
                        seen.add((v, ok))
                        stack.append((v, ok))
                elif v != start:
                    out[(start, v)] = out.get((start, v), False) or ok
    return out


def pair(key, graph):
    """Pair each chart box with a set of key item ids (empty set: matches nothing)."""
    items = key["items"]
    m, sims = {}, {}
    for n in graph["nodes"]:
        scores = [(sim(n["label"] or n["id"], it), it) for it in items]
        top = max(s for s, _ in scores)
        m[n["id"]] = {it["id"] for s, it in scores if top >= 0.6 and s >= top - 0.03}
        sims.update({(n["id"], it["id"]): s for s, it in scores})
    byid = {it["id"]: it for it in items}
    order = {it["id"]: i for i, it in enumerate(items)}
    node = {n["id"]: n for n in graph["nodes"]}
    # 1. Inputs and outputs that share a label may stay paired with the set (one "Reagents" box standing for
    #    several reagent arrows). Every other box with several candidates is open.
    open_ = {}
    for u, cands in m.items():
        if len(cands) < 2:
            continue
        if all(byid[c]["kind"] in ("input", "output") for c in cands) and len({" ".join(words(byid[c]["label"])) for c in cands}) == 1:
            continue
        # equal labels are ordered as the key lists them, so the result never depends on Python's set order
        open_[u] = sorted(cands, key=lambda c: (-sims[(u, c)], order[c]))
        m[u] = {open_[u][0]}
    # 2. Boxes with several candidates of near-equal label (four boxes all labelled "BALL MILL") are told apart
    #    by their lines, the way a person would: start from boxes whose pairing is certain and work outwards,
    #    each time pairing the open box whose lines to already-settled boxes agree best with the key. Then the
    #    chart's own words for where the box sits (its id and group heading, counting only words that tell the
    #    candidates apart), then the label. Only near-equal labels get here, so wiring never overrides a label.
    ctxs = {}
    for u, cands in open_.items():
        ctx = set(words(u + " " + node[u]["group"]))
        cw = {c: set(words(c + " " + byid[c]["area"] + " " + byid[c]["name"])) for c in cands}
        common = set.intersection(*cw.values())
        ctxs.update({(u, c): len(ctx & (cw[c] - common)) for c in cands})
    kpass = {i for i, it in byid.items() if it["kind"] in PASS}
    kc = collapse(byid, {(s["from"], s["to"]): True for s in key["streams"]}, kpass)
    through = {u for u, ids in m.items() if not ids or all(byid[i]["kind"] in PASS for i in ids)}
    gc = collapse(list(node), {(e["from"], e["to"]): True for e in graph["edges"]}, through)
    outs, ins = {}, {}
    for a, b in gc:
        outs.setdefault(a, []).append(b); ins.setdefault(b, []).append(a)
    settled = set(m) - set(open_)
    taken = {c for u in settled for c in m[u]}
    def agree(u, c):
        return (sum(any((c, b) in kc for b in m[v]) for v in outs.get(u, []) if v in settled)
                + sum(any((a, c) in kc for a in m[w]) for w in ins.get(u, []) if w in settled))
    while open_:
        # the tied box with the strongest evidence goes first; a candidate already taken counts a little less
        u, c = max(((u, c) for u, tied in open_.items() for c in tied),
                   key=lambda uc: (agree(*uc) - 0.5 * (uc[1] in taken), ctxs[uc], sims[uc], -open_[uc[0]].index(uc[1])))
        m[u] = {c}
        settled.add(u); taken.add(c); del open_[u]
    return m


def score(key, graph, check=None):
    m = pair(key, graph)
    for u, fix in ((check or {}).get("pairing") or {}).items():
        m[u] = set(fix["to"])
    kind = {it["id"]: it["kind"] for it in key["items"]}
    unsure_item = {it["id"] for it in key["items"] if it.get("unsure")}
    kpass = {i for i, k in kind.items() if k in PASS}
    kedges = {}
    for s in key["streams"]:
        e = (s["from"], s["to"])
        kedges[e] = kedges.get(e, False) or not s.get("unsure")
    kc = collapse(kind, kedges, kpass)
    kc = {e: sure and not (set(e) & unsure_item) for e, sure in kc.items()}

    gpass = {u for u, ids in m.items() if not ids or all(kind[i] in PASS for i in ids)}
    gedges = {(e["from"], e["to"]): True for e in graph["edges"] if e["from"] != e["to"]}
    gc = collapse([n["id"] for n in graph["nodes"]], gedges, gpass)
    boxes = {}   # which chart boxes drew each line, for the hand check
    for u, v in gc:
        if m[u] != m[v]:
            boxes.setdefault((frozenset(m[u]), frozenset(m[v])), []).append((u, v))
    lines = set(boxes)

    def has(a, b):
        return any(a in A and b in B for A, B in lines)

    sure = [e for e, s in kc.items() if s]
    found = [e for e in sure if has(*e)]
    right, wrong, reversed_ = 0, [], 0
    for A, B in lines:
        hits = [(a, b) for a in A for b in B if (a, b) in kc]
        if any(kc[h] for h in hits):
            right += 1
        elif not hits:
            wrong.append((sorted(A), sorted(B), sorted(boxes[(A, B)])))
            reversed_ += any((b, a) in kc for a in A for b in B)
    scored_items = [i for i, k in kind.items() if k not in PASS and i not in unsure_item]
    paired = set().union(*m.values()) if m else set()
    loops = []
    for lp in key.get("loops", []):
        if lp.get("unsure"):
            continue
        path = [p for p in lp["path"] if p not in kpass]
        steps = [(a, b) for a, b in zip(path, path[1:]) if a != b]
        loops.append({"name": lp["name"], "found": all(has(a, b) for a, b in steps)})
    return {
        "items_found": sum(i in paired for i in scored_items), "items_total": len(scored_items),
        "extra_boxes": sum(1 for u, ids in m.items() if not ids),
        "streams_found": len(found), "streams_total": len(sure),
        "lines_right": right, "lines_wrong": len(wrong), "lines_reversed": reversed_,
        "loops_found": sum(l["found"] for l in loops), "loops_total": len(loops),
        "missing_streams": sorted(set(sure) - set(found)), "wrong_lines": sorted(wrong), "loops": loops,
        "missing_items": sorted(i for i in scored_items if i not in paired),
        "pairing": {u: sorted(ids) for u, ids in m.items()},
        "checked_by_hand": (check or {}).get("checked"),
        "hand_pairings": len((check or {}).get("pairing") or {}),
    }


def key_as_graph(key, drop=()):
    """The key drawn as a chart: one box per item, one line per stream. Used by the self-check."""
    return {"nodes": [{"id": "n_" + it["id"], "label": it["label"] or it["name"], "group": it["area"]} for it in key["items"]],
            "edges": [{"from": "n_" + s["from"], "to": "n_" + s["to"], "label": ""} for s in key["streams"]
                      if (s["from"], s["to"]) not in drop]}


def selftest(keys):
    for f in sorted(Path(keys).glob("*.yaml")):
        key = yaml.safe_load(open(f))
        r = score(key, key_as_graph(key))
        assert r["streams_found"] == r["streams_total"] and not r["lines_wrong"], (f.name, r["missing_streams"], r["wrong_lines"])
        assert r["items_found"] == r["items_total"] and r["loops_found"] == r["loops_total"], (f.name, r["missing_items"], r["loops"])
        drop = next((s["from"], s["to"]) for s in key["streams"] if not s.get("unsure")
                    and key_item(key, s["from"])["kind"] not in PASS and key_item(key, s["to"])["kind"] not in PASS)
        r2 = score(key, key_as_graph(key, drop={drop}))
        assert r2["streams_found"] == r["streams_total"] - 1 and r2["missing_streams"] == [drop], (f.name, drop, r2["missing_streams"])
        print(f"{f.name}: the key scored against itself is perfect ({r['streams_total']} streams, {r['loops_total']} loops); one stream removed is missed")
    # Equal labels with no lines to tell them apart are paired by the scorer's own order, which must not change
    # from one run to the next (it once followed Python's set order, which changes with the hash seed).
    runs = [subprocess.run([sys.executable, __file__, "pairs", str(keys)], capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": seed}).stdout for seed in ("1", "2", "3")]
    assert runs[0] and runs[0] == runs[1] == runs[2], "pairing depends on the hash seed"
    print("pairing is the same under three hash seeds")


def pairs(keys):
    for f in sorted(Path(keys).glob("*.yaml")):
        key = yaml.safe_load(open(f))
        # boxes with neutral ids, no group and no lines: nothing but the scorer's own order tells equal labels apart
        g = {"nodes": [{"id": f"b{i}", "label": n["label"], "group": ""} for i, n in enumerate(key_as_graph(key)["nodes"])],
             "edges": []}
        print(f.name, json.dumps(sorted((u, sorted(v)) for u, v in pair(key, g).items())))


def show(chart):
    """Print a chart beside its key: every box with its pairing, the lines not in the key, the streams missed."""
    g = json.loads((chart / "mermaid.json").read_text())["graph"]
    r = json.loads((chart / "score.json").read_text())
    keys = Path(__file__).parent.parent / "reference"
    drawing = next(p.split("-")[0] for p in chart.parts if re.match(r"[pr]\d+-", p))
    kf = next(keys.glob(f"{drawing}-*.yaml"), None) or next((Path(__file__).parent.parent / "local/dev/keys").glob(f"{drawing}-*.yaml"))
    items = {it["id"]: it for it in yaml.safe_load(open(kf))["items"]}
    lab = {n["id"]: n["label"] for n in g["nodes"]}
    kl = lambda i: (items[i]["label"] or "(" + items[i]["name"] + ")") + f" [{i}]"
    print(f"== {chart}\n-- boxes and their pairing (* = several key items)")
    for u, ids in r["pairing"].items():
        print(f"  {'*' if len(ids) > 1 else ' '} {u:14} {lab[u][:40]!r:44} -> {', '.join(kl(i) for i in ids) or 'NOTHING'}")
    print("-- lines in the chart that are not in the key")
    for A, B, bx in r["wrong_lines"]:
        print(f"   {lab[bx[0][0]][:30]!r} -> {lab[bx[0][1]][:30]!r}   (key: {'/'.join(kl(a) for a in A)} -> {'/'.join(kl(b) for b in B)})")
    print("-- key streams the chart does not have")
    for a, b in r["missing_streams"]:
        print(f"   {kl(a)} -> {kl(b)}")
    print("-- items the chart does not have:", ", ".join(kl(i) for i in r["missing_items"]) or "none")


def key_item(key, i):
    return next(it for it in key["items"] if it["id"] == i)


if __name__ == "__main__":
    here = Path(__file__).parent
    if sys.argv[1] == "test":
        selftest(here.parent / "reference")
        sys.exit()
    if sys.argv[1] == "pairs":
        pairs(sys.argv[2])
        sys.exit()
    if sys.argv[1] == "show":
        show(Path(sys.argv[2]))
        sys.exit()
    keys, runs = Path(sys.argv[1]), Path(sys.argv[2])
    for mj in sorted(runs.rglob("mermaid.json")):
        info = json.loads(mj.read_text())
        drawing = next((p.split("-")[0] for p in mj.parts if re.match(r"[pr]\d+-", p)), None)
        kf = next(keys.glob(f"{drawing}-*.yaml"), None)
        if not info.get("ok") or not kf:
            continue
        ck = mj.with_name("check.json")
        r = score(yaml.safe_load(open(kf)), info["graph"], json.loads(ck.read_text()) if ck.exists() else None)
        mj.with_name("score.json").write_text(json.dumps(r, indent=1) + "\n")
        print(f"{str(mj.parent.relative_to(runs)):60} items {r['items_found']}/{r['items_total']}  streams {r['streams_found']}/{r['streams_total']}  "
              f"lines right {r['lines_right']} wrong {r['lines_wrong']}  loops {r['loops_found']}/{r['loops_total']}"
              + ("" if r["checked_by_hand"] else "  NOT CHECKED BY HAND"))
