#!/usr/bin/env python3
"""Write the article page's data.json: what its live panels draw, precomputed from the traces.

Run:  python3 page_data.py <dataset folder> <page folder>
"""
import csv, json, sys
from bisect import bisect_left
from pathlib import Path
import demo

COLS = 1200                                    # columns of the four-day panel


def main(data, page):
    real = [float(r["real_hourly_average_tph"]) for r in csv.DictReader(open(data / "hourly-real.csv"))]
    runs = {k: demo.load(data / "traces" / f"seed1-{k}.csv") for k in ("base", "1-spike", "50-spikes")}
    out = {"span": demo.SPAN, "real": [round(v, 1) for v in real[:12]], "variants": {}}

    for key, name in (("1-spike", "1"), ("base", "5"), ("50-spikes", "50")):
        t, true, read, run, events = runs[key]
        res, cleaned, _ = demo.analyse(t, true, read, run, events)
        flags, _ = demo.rules(t, read)
        s = res["shifts"][0]
        out["variants"][name] = {
            "records": res["records in shift 1"],
            "spikes": [[t[i], round(read[i])] for i in events["spikes"]],
            "p99": round(res["thresholds"]["10 x p99 per shift"][0]),
            "caught": {"hard": sum(flags["hard limit"][i] for i in events["spikes"]),
                       "p99": sum(flags["10 x p99"][i] for i in events["spikes"])},
            "hourly": [{"raw": round(h["raw"]), "clean": round(h["cleaned"]), "true": round(h["true"]), "spikes": h["spikes"]}
                       for h in res["hourly"][:12]],
            "shift": {k: round(s[k]) for k in ("raw", "cleaned", "true", "tonnes raw", "tonnes cleaned", "tonnes true")},
        }

    # the base trace carries every panel's records
    t, true, read, run, events = runs["base"]
    res, cleaned, states = demo.analyse(t, true, read, run, events)
    flags, thr = demo.rules(t, read)
    ct, cx, ck = zip(*cleaned)
    keep = [i for i in range(len(ct)) if ct[i] < demo.SHIFT]
    out["shift"] = {"t": [ct[i] for i in keep], "v": [round(cx[i]) for i in keep]}

    def window(a, b):
        raw = [[t[i], round(read[i], 1)] for i in range(len(t)) if a <= t[i] <= b]
        cl = [[ct[i], round(cx[i], 1), int(ck[i])] for i in range(len(ct)) if a <= ct[i] <= b]
        return {"from": a, "to": b, "raw": raw, "clean": cl}
    h58, h64 = res["hourly"][58], res["hourly"][64]
    out["negatives"] = {
        "drift": {**window(57.75 * 3600, 59.25 * 3600), "tonnes raw": round(h58["tonnes raw"], 1), "tonnes clean": round(h58["tonnes cleaned"], 1), "tonnes true": round(h58["tonnes true"], 1)},
        "failed": {**window(63.75 * 3600, 64.5 * 3600), "raw": window(63.75 * 3600, 64.5 * 3600)["raw"], "avg raw": round(h64["raw"]),
                   "avg clean": round(h64["cleaned"]), "avg true": round(h64["true"]), "coverage": round(h64["coverage"] * 100)},
    }

    # four days as columns: lowest and highest cleaned value, which rules flag it, plant state
    index = {s: i for i, s in enumerate(t)}
    in_event = {i for idx in events.values() for i in idx}
    total = demo.HOURS * 3600
    lo, hi, f3, fq, st = [], [], [], [], []
    code = {"running": 0, "starting": 1, "stopped": 2}
    for c in range(COLS):
        a, b = c * total / COLS, (c + 1) * total / COLS
        i0, i1 = bisect_left(ct, a), bisect_left(ct, b)
        if i0 == i1:                           # no record in this column: the line between its neighbours, unless that stretch is missing
            j = max(i0 - 1, 0)
            if not ck[j] or i0 >= len(ct):
                lo.append(None); hi.append(None); f3.append(0); fq.append(0); st.append(st[-1] if st else 0)
                continue
            mid = (a + b) / 2
            v = cx[j] + (cx[i0] - cx[j]) * (mid - ct[j]) / (ct[i0] - ct[j])
            vals, ids = [v], [index[ct[j]]]
        else:
            vals, ids = cx[i0:i1], [index[s] for s in ct[i0:i1]]
        lo.append(round(min(vals))); hi.append(round(max(vals)))
        f3.append(int(any(flags["3-sigma after hard limit"][i] for i in ids)))
        fq.append(int(any(flags["1.5 x IQR after hard limit"][i] for i in ids)))
        st.append(max(code[states[i]] for i in ids))
    count = lambda rule: {"flagged": sum(flags[rule]), "ordinary": sum(f and i not in in_event for i, f in enumerate(flags[rule]))}
    out["days"] = {
        "hours": demo.HOURS, "lo": lo, "hi": hi, "sigma": f3, "iqr": fq, "state": st, "records": len(ct),
        "limits": {"sigma": [round(v) for v in thr["3-sigma after hard limit"]], "iqr": [round(v) for v in thr["1.5 x IQR after hard limit"]]},
        "counts": {"sigma": count("3-sigma after hard limit"), "iqr": count("1.5 x IQR after hard limit")},
        "states": res["state counts"],
        "events": [["Low hour", 8.5], ["Surge", 20.25], ["Trip", 30.5], ["Shutdown", 43.5], ["Empty belt", 58.5]],
    }
    text = json.dumps(out, separators=(",", ":"))
    (page / "data.json").write_text(text)
    print(f"wrote data.json, {len(text) / 1024:.0f} KB")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
