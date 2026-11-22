#!/usr/bin/env python3
"""Score the stored runs twice, by the script and after the hand check, and write results/summary.json.

Inputs, all in this folder: results/rows.jsonl (one row per request), results/keys.json (the answer key) and
check.json (every grade the hand check changed, with its reason, the entity matches it added, and the keys left
out of every grade because they name no value, "excluded").
Standard library only. Run from this folder:  python3 score.py
"""
import json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = [json.loads(l) for l in open(HERE / "results/rows.jsonl")]
KEYS = json.loads((HERE / "results/keys.json").read_text())
CHECK = json.loads((HERE / "check.json").read_text())
MODELS, TASKS = ["qwen38-27b", "qwen38-next-flash"], ["Mineral-Term", "Mineral-Property", "Geo-NER"]
ALPHA_IC, GAMMA_GS, GAMMA_ST = 0.5, 0.5, 2.0            # the paper's section 4.2
W_ACC, W_IC, W_ST, W_EFF = 2, 1, 1, 1                   # the paper's Table 6

regrade = {(a["q"], a["answer"]): a["hand"] for a in CHECK["answers"] if "hand" in a}
alias = {(n["q"], n["label"], n["pred"]): n["gold"] for n in CHECK["ner"] if "pred" in n}
EXCLUDED = {e["q"] for e in CHECK["excluded"]}           # a key that names nothing to grade against: in no score


def f1(pred, gold):
    p = {(t, e) for t, s in pred.items() for e in s}
    g = {(t, e) for t, s in gold.items() for e in s}
    if not g:
        return 1.0 if not p else 0.0
    tp = len(p & g)
    return 0.0 if not p or not tp else 2 * tp / (len(p) + len(g))


def hand(r):
    if r["task"] != "Geo-NER":
        return float(regrade.get((r["q"], r["answer"]), r["script"]))
    pred = {t: {alias.get((r["q"], t, s), s) for s in spans} for t, spans in json.loads(r["answer"]).items()}
    return f1(pred, KEYS[r["q"]]["gold"])


for r in ROWS:                                           # the script's F1 is recomputed exactly before any alias is added
    if r["task"] == "Geo-NER":
        assert abs(f1({t: set(s) for t, s in json.loads(r["answer"]).items()}, KEYS[r["q"]]["gold"]) - r["script"]) < 1e-9, r
    r["hand"] = hand(r)


def ic(answers):                                          # inter-round consistency of one question, section 3.3
    ecr = max(Counter(answers).values()) / len(answers)
    pairs = [(a, b) for i, a in enumerate(answers) for b in answers[i + 1:]]
    jac = lambda a, b: 1.0 if not a and not b else (len(a & b) / len(a | b) if a and b else 0.0)
    return ALPHA_IC * ecr + (1 - ALPHA_IC) * sum(jac(set(a.split()), set(b.split())) for a, b in pairs) / len(pairs)


def per_question(rows, field):
    by = defaultdict(list)
    for r in rows:
        if r["q"] not in EXCLUDED:
            by[r["q"]].append(r[field])
    return {q: sum(v) / len(v) for q, v in by.items()}


def run_summary(run):
    rows = [r for r in ROWS if r["run"] == run]
    tasks = [t for t in TASKS if any(r["task"] == t for r in rows)]
    out, eff = {}, {}
    for m in MODELS:
        mr = [r for r in rows if r["model"] == m]
        s = {"acc": {}, "ic": {}}
        for t in tasks:
            tr = [r for r in mr if r["task"] == t]
            s["acc"][t] = {k: 100 * statistics.fmean(per_question(tr, k).values()) for k in ("script", "hand")}
            rounds = defaultdict(dict)
            for r in tr:
                rounds[r["q"]][r["round"]] = r["answer"]
            s["ic"][t] = 100 * statistics.fmean(ic([v[k] for k in sorted(v)]) for v in rounds.values())
        for k in ("script", "hand"):
            accs = [s["acc"][t][k] for t in tasks]
            mu, sd = statistics.fmean(accs), statistics.pstdev(accs)
            s[k] = {"acc": mu, "gs": mu - GAMMA_GS * sd, "st": 100 - GAMMA_ST * sd}
        s["ic_m"] = statistics.fmean(s["ic"].values())
        s["latency_s"] = statistics.fmean(r["latency_s"] for r in mr)
        s["tokens"] = statistics.fmean(r["completion_tokens"] or 0 for r in mr)
        s["requests"] = len(mr)
        ner = [r for r in mr if r["task"] == "Geo-NER"]
        if ner:
            s["empty_ner_pct"] = 100 * sum(1 for r in ner if not json.loads(r["answer"])) / len(ner)
        eff[m] = len(mr) / sum(r["latency_s"] for r in mr)      # Eff = K / cumulative request time
        out[m] = s
    for m in MODELS:                                          # Eff_norm = 100 / (1 + log10(max Eff / Eff_m))
        s = out[m]
        s["eff_req_s"], s["eff_norm"] = eff[m], 100 / (1 + math.log10(max(eff.values()) / eff[m]))
        for k in ("script", "hand"):
            s[k]["composite"] = (W_ACC * s[k]["acc"] + W_IC * s["ic_m"] + W_ST * s[k]["st"] + W_EFF * s["eff_norm"]) / (W_ACC + W_IC + W_ST + W_EFF)
    # the oracle: for each question, the better model's round-averaged score
    orc = {}
    for t in tasks:
        pq = [per_question([r for r in rows if r["model"] == m and r["task"] == t], "hand") for m in MODELS]
        orc[t] = 100 * statistics.fmean(max(d[q] for d in pq) for q in pq[0])
    out["oracle_hand"] = {**orc, "acc": statistics.fmean(orc.values())}
    return out


summary = {run: run_summary(run) for run in ("main", "open_cue")}

# Mineral-Property and Geo-NER broken down: by property, and by entity label (hand-checked)
main = [r for r in ROWS if r["run"] == "main"]
props = sorted({KEYS[r["q"]]["property"] for r in main if r["task"] == "Mineral-Property"})
summary["by_property"] = {m: {p: 100 * statistics.fmean(per_question(
    [r for r in main if r["model"] == m and r["task"] == "Mineral-Property" and KEYS[r["q"]]["property"] == p], "hand").values())
    for p in props} for m in MODELS}
summary["check"] = {"answers_read": CHECK["read"]["answers"], "regraded": sum(a["hand"] != a["script"] for a in CHECK["answers"]),
                    "up": sum(a["hand"] > a["script"] for a in CHECK["answers"]),
                    "down": sum(a["hand"] < a["script"] for a in CHECK["answers"]),
                    "ner_samples": CHECK["read"]["ner_samples"], "ner_matches_added": len(alias), "excluded": sorted(EXCLUDED)}
(HERE / "results/summary.json").write_text(json.dumps(summary, indent=1) + "\n")

for run in ("main", "open_cue"):
    for m in MODELS:
        s = summary[run][m]
        print(f"{run:9} {m:18} " + "  ".join(f"{t[:12]} {v['script']:5.1f}→{v['hand']:5.1f}" for t, v in s["acc"].items())
              + f"  | mean {s['script']['acc']:.1f}→{s['hand']['acc']:.1f}  composite {s['hand']['composite']:.1f}  {s['latency_s']:.1f} s")
print("by property:", {m: {p: round(v, 1) for p, v in d.items()} for m, d in summary["by_property"].items()})
print("check:", summary["check"])
