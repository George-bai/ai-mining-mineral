#!/usr/bin/env python3
"""Build raw-style records for a feed rate tag from real hourly averages. See README.md beside this file.

The hourly shape is real (anonymised and scaled; the 96 hours are in hourly-real.csv). The records
inside each hour, the faults and the events are generated here. Standard library only; same output every run.
Run:  python3 generate.py      (writes traces/*.csv, events.json and hourly-real.csv beside this file)
"""
import csv, json, math, random
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).parent
HOURS = 96                   # 4 days, 8 shifts of 12 hours
SCAN = 5                     # seconds between instrument scans, before the historian's exception test
PER_H = 3600 // SCAN
G = HOURS * PER_H
SPAN = 1500.0                # instrument span, t/h
EXC_DEV = 7.5                # exception deadband, t/h (0.5 % of span): a scan is recorded when it moves this far from the last record
EXC_MAX = 600                # ...or when this many seconds have passed
BASE_SPIKES = {3: [100_000], 7: [180_000, 420_000, 1_000_000], 10: [650_000]}  # hour -> values, t/h
KIND = {"spikes": "fault", "zero drift": "fault", "failed transmitter": "fault", "surge": "inserted event",
        "trip": "inserted event", "shutdown and start-up": "inserted event", "empty running belt": "inserted event"}
TRACES = [(1, "base"), (1, "1-spike"), (1, "50-spikes"), (1, "clean-control"), (2, "base"), (3, "base")]


def real_hours():
    """Read the 96 supplied hourly averages."""
    return [(datetime.fromisoformat(r["time"]), float(r["real_hourly_average_tph"])) for r in csv.DictReader(open(HERE / "hourly-real.csv"))]


def H(hours):
    return int(round(hours * PER_H))


def build(hourly, seed, variant):
    rng = random.Random(seed)
    means = [v for _, v in hourly]
    # true rate: a line through the hour centres, plus slow process variation, shifted so every hour's mean is the real one
    true, a, x = [], math.exp(-SCAN / 180), 0.0
    for k in range(G):
        c = k / PER_H - 0.5
        i = min(max(int(math.floor(c)), 0), HOURS - 2)
        x = a * x + rng.gauss(0, 18 * math.sqrt(1 - a * a))
        true.append(means[i] + (means[i + 1] - means[i]) * (c - i) + x)
    for h in range(HOURS):
        seg = slice(h * PER_H, (h + 1) * PER_H)
        off = means[h] - sum(true[seg]) / PER_H
        true[seg] = [v + off for v in true[seg]]

    run, events = [1] * G, {}

    def scale(start, factors, name, stopped=()):
        events[name] = set(range(start, start + len(factors)))
        for k, f in enumerate(factors):
            true[start + k] *= f
        for k in stopped:
            run[start + k] = 0

    per_min = 60 // SCAN
    ramp = lambda a, b, minutes: [a + (b - a) * (k + 1) / (minutes * per_min) for k in range(minutes * per_min)]
    scale(H(20), [1.25] * H(0.5), "surge")
    scale(H(30), ramp(1, 0, 1) + [0] * H(40 / 60) + ramp(0, 1, 20), "trip", stopped=range(per_min, per_min + H(40 / 60)))
    scale(H(40), ramp(1, 0, 10) + [0] * H(6) + ramp(0, 1.10, 30) + ramp(1.10, 1, 15), "shutdown and start-up",
          stopped=range(10 * per_min, 10 * per_min + H(6)))
    scale(H(58), [0] * H(1), "empty running belt")            # feed stops, belt keeps running

    read = [t + rng.gauss(0, 4) * t / 1000 for t in true]     # measurement noise scales with load; a stopped belt reads 0
    if variant != "clean-control":
        events["zero drift"] = events.pop("empty running belt")   # the weigher reads -8 t/h on the empty belt
        for k in events["zero drift"]:
            read[k] = -8 + rng.gauss(0, 1)
        events["failed transmitter"] = set(range(H(64), H(64.25)))
        for k in events["failed transmitter"]:
            read[k] = -0.025 * SPAN
        if variant == "base":
            placed = {h * PER_H + k: v for h, vals in BASE_SPIKES.items()
                      for k, v in zip(rng.sample(range(PER_H), len(vals)), vals)}
        elif variant == "1-spike":
            placed = {3 * PER_H + rng.randrange(PER_H): 100_000}
        else:
            placed = {k: 10 ** rng.uniform(5, 6) for k in rng.sample(range(H(12)), 50)}
        for k, v in placed.items():
            read[k] = v
        events["spikes"] = set(placed)

    # the historian's exception test: irregular records, more of them when the value moves
    keep, last = [0], 0
    for k in range(1, G):
        if abs(read[k] - read[last]) > EXC_DEV or (k - last) * SCAN >= EXC_MAX or run[k] != run[k - 1]:
            if keep[-1] != k - 1 and abs(read[k] - read[last]) > EXC_DEV:
                keep.append(k - 1)                             # the scan before the change is recorded too
            keep.append(k)
            last = k
    label = {k: e for e, idx in events.items() for k in idx}
    return [(k, true[k], read[k], run[k], label.get(k, "")) for k in keep]


def main():
    hourly = real_hours()
    start = hourly[0][0]
    (HERE / "traces").mkdir(exist_ok=True)
    with open(HERE / "hourly-real.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hour", "time", "real_hourly_average_tph"])
        w.writerows([h, t.isoformat(sep=" "), v] for h, (t, v) in enumerate(hourly))
    index = {}
    for seed, variant in TRACES:
        recs = build(hourly, seed, variant)
        name = f"seed{seed}-{variant}.csv"
        with open(HERE / "traces" / name, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time", "seconds", "true_tph", "reading_tph", "belt_running", "event"])
            for k, t, r, b, e in recs:
                w.writerow([(start + timedelta(seconds=k * SCAN)).isoformat(sep=" "), k * SCAN, round(t, 2), round(r, 2), b, e])
        ev = {}
        for k, *_, e in recs:
            if e:
                ev.setdefault(e, []).append(k * SCAN)
        index[name] = {"records": len(recs), "events": {e: {"kind": KIND[e], "records": len(s), "first_second": s[0],
                                                             "last_second": s[-1]} for e, s in ev.items()}}
    (HERE / "events.json").write_text(json.dumps(index, indent=1))
    print({n: v["records"] for n, v in index.items()})


if __name__ == "__main__":
    main()
