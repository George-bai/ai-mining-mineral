"""No. 5's answer key for questions p2 to p4 (p1 uses No. 4's key), read through No. 2's MCP tool code before any
run. Writes key.json.

    (mock on :8711)  ../../historian-tag-catalogue-for-agents/public/.venv/bin/python make_key.py

Hourly time-weighted averages; running hours only (fresh feed 50 t/h or more), as the plant knowledge says. Hours whose recovery or mass pull is
impossible (outside 0 to 100 %, an analyser glitch) are left out of the key's value ("screened"). The key's
value is the site's way: gold recovery over a period = concentrate gold over feed gold, i.e. hourly recoveries
weighted by feed gold (feed rate x feed grade); mass pull weighted by feed tonnes. Alternatives an agent may use are
kept beside it (plain mean of hourly values; the formula on the period's average assays; stopped hours kept in).
"""
import json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "local-agent-reagent-recovery-analysis" / "public"))
from make_key import E, M, catalog, read  # noqa: E402  (No. 4's reader: same tool code, same tags)

TAGS = {"f": "Flotation\\Rougher Feed|Au", "rc": "Flotation\\Rougher Concentrate|Au", "rt": "Flotation\\Rougher Tail|Au",
        "fc": "Flotation\\Final Concentrate|Au", "ft": "Flotation\\Final Tail|Au", "q": "Grinding\\SAG Mill|Fresh Feed Rate"}


def two(f, c, t):
    with np.errstate(all="ignore"):
        return 100 * c * (f - t) / (f * (c - t)), 100 * (f - t) / (c - t)


def numbers(d, conc, tail):
    f, c, t, q = d["f"], d[conc], d[tail], d["q"]
    rec, mp = two(f, c, t)
    fin = np.isfinite(rec) & np.isfinite(q) & np.isfinite(f)
    run = fin & (q >= 50)
    ok = run & (rec >= 0) & (rec <= 100) & (mp >= 0) & (mp <= 100)   # screened: impossible hours left out
    w = q * f
    out = {"hours": int(fin.sum()), "running_hours": int(run.sum()), "screened_hours": int(ok.sum()),
           "recovery_screened_gold_weighted": float(np.sum((w * rec)[ok]) / np.sum(w[ok])),
           "recovery_screened_plain_mean": float(np.mean(rec[ok])),
           "mass_pull_screened_tonne_weighted": float(np.sum((q * mp)[ok]) / np.sum(q[ok])),
           "mass_pull_screened_plain_mean": float(np.mean(mp[ok])),
           "recovery_gold_weighted": float(np.sum((w * rec)[run]) / np.sum(w[run])),
           "recovery_plain_mean": float(np.mean(rec[run])),
           "recovery_from_mean_assays": float(two(np.mean(f[run]), np.mean(c[run]), np.mean(t[run]))[0]),
           "recovery_gold_weighted_with_stops": float(np.sum((w * rec)[fin]) / np.sum(w[fin])),
           "recovery_plain_mean_with_stops": float(np.mean(rec[fin])),
           "mass_pull_tonne_weighted": float(np.sum((q * mp)[run]) / np.sum(q[run])),
           "mass_pull_plain_mean": float(np.mean(mp[run])),
           "mass_pull_from_mean_assays": float(two(np.mean(f[run]), np.mean(c[run]), np.mean(t[run]))[1]),
           "feed_grade_tonne_weighted": float(np.sum((q * f)[run]) / np.sum(q[run])),
           "feed_grade_plain_mean": float(np.mean(f[run]))}
    return {k: round(v, 3) if isinstance(v, float) else v for k, v in out.items()}


def main():
    con = catalog.connect(str(M.CATALOG))
    ids = {k: str(con.execute("SELECT id FROM tags WHERE path = ?", (E + p,)).fetchone()[0]) for k, p in TAGS.items()}
    now = M.catalog_status()["historian_now"]        # 2026-11-23T00:00:00+10:00
    key = {"tags": {k: E + p for k, p in TAGS.items()}, "historian_now": now}
    d = read(ids, "2026-10-24T00:00:00+10:00", now, "1h")
    key["p2_last_30_days"] = numbers(d, "fc", "ft")
    d = read(ids, "2026-10-01T00:00:00+10:00", "2026-11-01T00:00:00+10:00", "1h")
    key["p2_october_2026"] = numbers(d, "fc", "ft")
    d = read(ids, "2026-11-16T00:00:00+10:00", now, "1h")
    key["p3_last_7_days"] = numbers(d, "rc", "rt")
    months = {}
    for y, m in [(2025, 11), (2025, 12)] + [(2026, i) for i in range(1, 12)]:
        a = f"{y}-{m:02d}-01T00:00:00+10:00"
        b = f"{y + (m == 12)}-{m % 12 + 1:02d}-01T00:00:00+10:00" if (y, m) != (2026, 11) else now
        months[f"{y}-{m:02d}"] = numbers(read(ids, a, b, "1h"), "fc", "ft")
    key["p4_months"] = months
    in2026 = {k: v for k, v in months.items() if k.startswith("2026")}  # the question asks about 2026 so far
    for how in ("recovery_screened_gold_weighted", "recovery_screened_plain_mean", "recovery_gold_weighted",
                "recovery_plain_mean", "recovery_from_mean_assays"):
        key[f"p4_lowest_2026_{how}"] = min(in2026, key=lambda k: in2026[k][how])
    (HERE / "key.json").write_text(json.dumps(key, indent=1))
    for k in ("p2_last_30_days", "p2_october_2026", "p3_last_7_days"):
        print(k, key[k])
    for k, v in months.items():
        print(k, v["running_hours"], v["screened_hours"], v["recovery_screened_gold_weighted"], v["recovery_screened_plain_mean"], v["recovery_gold_weighted"], v["recovery_plain_mean"], v["recovery_from_mean_assays"], v["feed_grade_tonne_weighted"])
    print({k: v for k, v in key.items() if k.startswith("p4_lowest")})


if __name__ == "__main__":
    main()
