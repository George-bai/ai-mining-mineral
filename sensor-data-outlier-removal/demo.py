#!/usr/bin/env python3
"""Clean a raw-style feed rate tag several ways and report what each way does.

The data is the shared dataset in data/feed-rate-raw-style-v1 (see its README): real hourly averages
(anonymised and scaled) with generated records, faults and events inside them. This shows how each rule
behaves on that data, not how real plants behave. Standard library only.
Run:  python3 demo.py <dataset folder> [output folder]     writes results.json and cleaned-base.csv
"""
import csv, json, math, statistics, sys
from bisect import bisect_right
from pathlib import Path

HOURS = 96
SHIFT = 12 * 3600
SPAN = 1500.0                # instrument span, t/h
LOW = -0.01 * SPAN           # below this a negative is a fault, not zero drift
GAP = 60                     # removed records are bridged when the good records around them are this close, seconds


def load(path):
    t, true, read, run, events = [], [], [], [], {}
    with open(path, newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            t.append(int(r["seconds"])); true.append(float(r["true_tph"])); read.append(float(r["reading_tph"]))
            run.append(int(r["belt_running"]))
            if r["event"]:
                events.setdefault(r["event"], []).append(i)
    return t, true, read, run, events


def rules(t, read):
    """Each rule's flags, and the thresholds it used. All rules look at records, not at time."""
    n = len(read)
    hard = [x > SPAN or x < LOW for x in read]
    p99, thr = [False] * n, []
    for s in range(0, HOURS * 3600, SHIFT):              # 10 x the 99th percentile of each 12-hour shift
        idx = [i for i in range(n) if s <= t[i] < s + SHIFT]
        shift = sorted(read[i] for i in idx)
        limit = 10 * shift[math.ceil(0.99 * len(shift)) - 1]
        thr.append(limit)
        for i in idx:
            p99[i] = read[i] > limit
    m, sd = statistics.fmean(read), statistics.pstdev(read)
    sigma = [abs(x - m) > 3 * sd for x in read]
    kept = [x for x, h in zip(read, hard) if not h]      # the same rule once the hard limit has been applied
    m2, sd2 = statistics.fmean(kept), statistics.pstdev(kept)
    sigma_after = [not h and abs(x - m2) > 3 * sd2 for x, h in zip(read, hard)]
    q1, _, q3 = statistics.quantiles(kept, n=4)          # the box-plot rule, also after the hard limit
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    iqr_after = [not h and not lo <= x <= hi for x, h in zip(read, hard)]
    return ({"hard limit": hard, "10 x p99": p99, "3-sigma on raw": sigma, "3-sigma after hard limit": sigma_after,
             "1.5 x IQR after hard limit": iqr_after},
            {"10 x p99 per shift": thr, "3-sigma on raw": [m - 3 * sd, m + 3 * sd],
             "3-sigma after hard limit": [m2 - 3 * sd2, m2 + 3 * sd2], "1.5 x IQR after hard limit": [lo, hi]})


def clean(t, read, run, hard):
    """Drop records outside the hard limit; set small negatives on a running belt to 0.

    ponytail: a negative no lower than LOW on a running belt is taken as zero drift on an empty belt. That holds
    in this dataset, where the only such records are the inserted empty-belt hour. A real tag needs evidence
    that the belt is empty (a belt-loaded signal, upstream feeder state) before a negative is set to zero.

    Returns the cleaned records as (seconds, value, known): known is False when the stretch up to the next
    record lost more than GAP seconds to dropped records, so it counts as missing, not interpolated.
    """
    out, repaired, dropped = [], 0, False
    for i in range(len(t)):
        if hard[i]:
            dropped = True
            continue
        x = read[i]
        if x < 0 and run[i]:
            x, repaired = 0.0, repaired + 1
        if out and dropped and t[i] - out[-1][0] > GAP:
            out[-1] = (out[-1][0], out[-1][1], False)
        out.append((t[i], x, True))
        dropped = False
    return out, repaired


def integrate(t, x, a, b, known=None):
    """Time-weighted integral of x over [a, b) with straight lines between records. Returns (integral, seconds covered)."""
    total = covered = 0.0
    i = max(bisect_right(t, a) - 1, 0)
    while i + 1 < len(t) and t[i] < b:
        t0, t1 = t[i], t[i + 1]
        if (known is None or known[i]) and t1 > a:
            lo, hi = max(t0, a), min(t1, b)
            at = lambda s: x[i] + (x[i + 1] - x[i]) * (s - t0) / (t1 - t0)
            total += (at(lo) + at(hi)) / 2 * (hi - lo)
            covered += hi - lo
        i += 1
    return total, covered


def states(t, run):
    out, started = [], -3600
    for i, r in enumerate(run):
        if r and i and not run[i - 1]:
            started = t[i]
        out.append("stopped" if not r else "starting" if t[i] - started < 3600 else "running")
    return out


def analyse(t, true, read, run, events):
    flags, thresholds = rules(t, read)
    cleaned, repaired = clean(t, read, run, flags["hard limit"])
    ct, cx, ck = zip(*cleaned)
    spikes = [t[i] for i in events.get("spikes", [])]

    def window(a, b):
        raw, span = integrate(t, read, a, b)             # span is b - a except in the last window, which ends at the last record
        tru, _ = integrate(t, true, a, b)
        cl, cov = integrate(ct, cx, a, b, ck)
        vals = [read[i] for i in range(bisect_right(t, a - 1), bisect_right(t, b - 1))]
        return {"true": tru / span, "raw": raw / span, "raw max": max(vals), "raw min": min(vals), "records": len(vals),
                "cleaned": cl / cov if cov else None, "coverage": cov / (b - a),
                "tonnes true": tru / 3600, "tonnes raw": raw / 3600, "tonnes cleaned": cl / 3600}

    hourly = [dict(hour=h, spikes=sum(h * 3600 <= s < (h + 1) * 3600 for s in spikes), **window(h * 3600, (h + 1) * 3600))
              for h in range(HOURS)]
    st = states(t, run)
    return {
        "records": len(t), "records in shift 1": sum(s < SHIFT for s in t),
        "event records": {k: len(v) for k, v in events.items()},
        "thresholds": thresholds,
        "share of each event's records flagged": {name: {rule: sum(f[i] for i in idx) / len(idx) for rule, f in flags.items()}
                                                  for name, idx in events.items()},
        "flagged in total": {rule: sum(f) for rule, f in flags.items()},
        "negatives repaired to zero": repaired,
        "state counts": {s: st.count(s) for s in ("running", "starting", "stopped")},
        "hourly": hourly, "shifts": [window(s, s + SHIFT) for s in range(0, HOURS * 3600, SHIFT)],
        "all 4 days": window(0, HOURS * 3600),
        "hours above span as averages": sum(h["raw"] > SPAN for h in hourly),
        "hours with a spike but average inside span": sum(h["spikes"] > 0 and h["raw"] <= SPAN for h in hourly),
    }, cleaned, st


def main(data, out):
    out.mkdir(parents=True, exist_ok=True)
    real = [float(r["real_hourly_average_tph"]) for r in csv.DictReader(open(data / "hourly-real.csv"))]
    results = {}
    for path in sorted((data / "traces").glob("*.csv")):
        t, true, read, run, events = load(path)
        res, cleaned, st = analyse(t, true, read, run, events)
        marked = {h for idx in events.values() for i in idx for h in [t[i] // 3600]}   # hours touched by a fault or inserted event
        res["largest gap between a record-built hourly average and the real one, untouched hours"] = max(
            abs(h["true"] - real[h["hour"]]) for h in res["hourly"] if h["hour"] not in marked)
        results[path.stem] = res
        if path.stem == "seed1-base":
            with open(out / "cleaned-base.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["seconds", "cleaned_tph", "known_until_next_record"])
                w.writerows((s, round(x, 2), int(k)) for s, x, k in cleaned)
    (out / "results.json").write_text(json.dumps(results, indent=1))

    # self-check on the base trace
    b = results["seed1-base"]
    s = b["share of each event's records flagged"]
    assert s["spikes"]["hard limit"] == 1 and s["failed transmitter"]["hard limit"] == 1
    assert all(s[e]["hard limit"] == 0 for e in ("surge", "trip", "shutdown and start-up", "zero drift"))
    assert abs(b["shifts"][0]["tonnes cleaned"] / b["shifts"][0]["tonnes true"] - 1) < 0.001
    c = results["seed1-clean-control"]
    assert c["flagged in total"]["hard limit"] == 0 and c["negatives repaired to zero"] == 0
    assert c["largest gap between a record-built hourly average and the real one, untouched hours"] < 2
    # integrate(): a line from 0 to 10 over 10 s has integral 50; half of it missing leaves 5 s covered
    assert integrate([0, 10], [0, 10], 0, 10) == (50.0, 10.0)
    assert integrate([0, 5, 10], [0, 5, 10], 0, 10, [True, False, True])[1] == 5
    print(f"wrote {out}/results.json and cleaned-base.csv from {len(results)} traces; self-check passed")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "out"))
