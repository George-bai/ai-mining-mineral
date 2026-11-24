"""No. 4's answer key: our own analysis of collector dose against rougher gold recovery at Site A, Concentrator 1,
read through the same MCP tool code the agent uses (No. 2's server), before any agent run. Writes key.json.

    (mock on :8711)  ../../historian-tag-catalogue-for-agents/public/.venv/bin/python make_key.py

Rougher recovery (%) = 100 c (f - t) / (f (c - t)), from the rougher feed (f), rougher concentrate (c) and rougher
tail (t) gold assays: the two-product formula. Read at two resolutions over all the data the historian has:
daily (time-weighted daily averages, one call) and hourly (time-weighted, in 80-day calls). Hours or days with the
feed under 50 t/h (stopped) and recoveries outside 0-100 % are left out. Feed-grade bands: thirds of rougher feed Au.
Slope: least squares, recovery (percentage points) per unit of collector. Interval on the low-minus-high slope
difference: bootstrap over whole weeks (1,000 draws, seed 7). Both forms of dose: the tag as recorded (a flow,
mL/min) and per tonne of feed (mL/min per t/h).
"""
import json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
PUB = HERE.parent.parent / "historian-tag-catalogue-for-agents" / "public"
sys.path.insert(0, str(PUB))
import catalog, mcp_server as M  # noqa: E402

E = "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\"
TAGS = {"f": "Flotation\\Rougher Feed|Au", "c": "Flotation\\Rougher Concentrate|Au", "t": "Flotation\\Rougher Tail|Au",
        "x": "Flotation\\Collector|Dose Rate", "q": "Grinding\\SAG Mill|Fresh Feed Rate"}


def read(ids, start, end, interval):
    r = M.get_timeseries(ids=list(ids.values()), start=start, end=end, mode="summary", interval=interval)
    lines = Path(r["file"]).read_text().splitlines()
    head = lines[0].split(",")
    col = {k: head.index(f"{i}|Average") for k, i in ids.items()}
    out = {k: [] for k in ids}
    out["time"] = []
    for ln in lines[1:]:
        v = ln.split(",")
        out["time"].append(v[0])
        for k in ids:
            out[k].append(float(v[col[k]]) if v[col[k]] else np.nan)
    return {k: np.array(v) if k != "time" else v for k, v in out.items()}


def slope(x, y):
    return float(np.polyfit(x, y, 1)[0]) if len(x) > 2 else float("nan")


def analyse(d, per_tonne=False, floor=0.0):
    f, c, t, x, q = d["f"], d["c"], d["t"], d["x"], d["q"]
    with np.errstate(all="ignore"):
        rec = 100 * c * (f - t) / (f * (c - t))
    dose = x / q if per_tonne else x
    ok = np.isfinite(rec) & np.isfinite(dose) & np.isfinite(f) & (q >= 50) & (rec > floor) & (rec <= 100)
    rec, dose, f = rec[ok], dose[ok], f[ok]
    weeks = np.array([w for w, k in zip(d["week"], ok) if k])
    cut = np.quantile(f, [1 / 3, 2 / 3])
    band = np.where(f < cut[0], "low", np.where(f < cut[1], "mid", "high"))
    res = {"n": int(ok.sum()), "overall_slope": slope(dose, rec), "overall_r": float(np.corrcoef(dose, rec)[0, 1]),
           "cuts_g_t": [round(float(v), 3) for v in cut], "mean_recovery": float(rec.mean()), "bands": {}}
    for b in ("low", "mid", "high"):
        m = band == b
        res["bands"][b] = {"n": int(m.sum()), "slope": slope(dose[m], rec[m]), "r": float(np.corrcoef(dose[m], rec[m])[0, 1]),
                           "mean_recovery": float(rec[m].mean()), "mean_dose": float(dose[m].mean())}
    rng, uw, diffs = np.random.default_rng(7), np.unique(weeks), []
    idx = {w: np.flatnonzero(weeks == w) for w in uw}
    for _ in range(1000):
        s = np.concatenate([idx[w] for w in rng.choice(uw, len(uw))])
        bl, bh = s[band[s] == "low"], s[band[s] == "high"]
        diffs.append(slope(dose[bl], rec[bl]) - slope(dose[bh], rec[bh]))
    res["low_minus_high"] = {"estimate": res["bands"]["low"]["slope"] - res["bands"]["high"]["slope"],
                             "ci95": [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))]}
    res["scatter"] = {"dose": np.round(dose, 3).tolist(), "recovery": np.round(rec, 3).tolist(), "band": band.tolist()} \
        if not per_tonne and len(rec) < 2000 else None
    return res


def main():
    con = catalog.connect(str(M.CATALOG))
    ids = {k: str(con.execute("SELECT id FROM tags WHERE path = ?", (E + p,)).fetchone()[0]) for k, p in TAGS.items()}
    st = M.catalog_status()
    first, now = st["historian_earliest"], st["historian_now"]
    daily = read(ids, first, now, "1d")
    hourly = {k: [] for k in list(ids) + ["time"]}
    t0 = np.datetime64(first[:19])
    while t0 < np.datetime64(now[:19]):
        t1 = min(t0 + np.timedelta64(80, "D"), np.datetime64(now[:19]))
        part = read(ids, str(t0) + "+10:00", str(t1) + "+10:00", "1h")
        for k in hourly:
            hourly[k] += list(part[k])
        t0 = t1
    hourly = {k: np.array(v) if k != "time" else v for k, v in hourly.items()}
    for d in (daily, hourly):
        d["week"] = [np.datetime64(s[:10], "W").astype(int) for s in d["time"]]
    key = {"tags": {k: E + p for k, p in TAGS.items()}, "window": [first, now], "formula": "100 c (f - t) / (f (c - t))"}
    for name, d in (("daily", daily), ("hourly", hourly)):
        key[name] = {"recorded": analyse(d), "per_tonne": analyse(d, per_tonne=True),
                     "recorded_recovery_over_40": analyse(d, floor=40.0)}
    # the daily points are Zyfra's values (not republished): they go to the gitignored local folder for the page's figure
    scatter = {f"{n}/{f}": key[n][f].pop("scatter") for n in ("daily", "hourly") for f in list(key[n]) if key[n][f].get("scatter")}
    for n in ("daily", "hourly"):
        for f in key[n]:
            key[n][f].pop("scatter", None)
    (HERE.parent / "local").mkdir(exist_ok=True)
    (HERE.parent / "local" / "key-scatter.json").write_text(json.dumps(scatter))
    (HERE / "key.json").write_text(json.dumps(key, indent=1))
    for name in ("daily", "hourly"):
        for form in ("recorded", "per_tonne", "recorded_recovery_over_40"):
            r = key[name][form]
            print(name, form, r["n"], "overall", round(r["overall_slope"], 3), "r", round(r["overall_r"], 2), "cuts", r["cuts_g_t"],
                  {b: round(v["slope"], 3) for b, v in r["bands"].items()},
                  "low-high", round(r["low_minus_high"]["estimate"], 2), [round(v, 2) for v in r["low_minus_high"]["ci95"]])


if __name__ == "__main__":
    main()
