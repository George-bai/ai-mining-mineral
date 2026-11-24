"""Tag values, computed on demand and never stored: a deterministic function of the tag and the time.

Tags named in config/backbones.yaml follow a real hourly average (local/backbones/*.csv, cut by make_backbones.py);
the values inside each hour are generated around it, so every hour's time-weighted mean equals the real value.
Other tags are generated, driven by their concentrator's real feed rate. Without the backbone files every tag is
generated. The mock's clock is fixed (MOCK_NOW), so every run sees the same history.
"""
import csv, hashlib, math, os
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).parent
SCAN = 5.0          # seconds between scans
MAX_GAP = 600.0     # the exception test records at least every 10 minutes
ANALYSER_CYCLE = 900.0
NOW = datetime.fromisoformat(os.environ.get("MOCK_NOW", "2026-11-23T00:00:00+10:00")).timestamp()
BACKBONES = Path(os.environ.get("MOCK_BACKBONES", HERE / "local" / "backbones"))

# kind: base unit, mean, standard deviation, low, high, recipe
KINDS = {
    "feed_rate":        ("t/h", 950, 80, 0, 1500, "continuous"),
    "power":            ("kW", 900, 90, 0, 20000, "continuous"),
    "current":          ("A", 180, 15, 0, 600, "continuous"),
    "gap":              ("mm", 150, 3, 100, 200, "continuous"),
    "speed":            ("rpm", 10, 0.3, 0, 15, "continuous"),
    "speed_pct":        ("%", 75, 6, 0, 100, "continuous"),
    "pressure":         ("kPa", 120, 10, 0, 6000, "continuous"),
    "flow":             ("m3/h", 600, 60, 0, 5000, "continuous"),
    "density":          ("%", 55, 4, 0, 80, "continuous"),
    "count":            ("", 8, 1, 0, 12, "integer"),
    "air_flow":         ("m3/h", 1400, 120, 0, 4000, "continuous"),
    "level":            ("%", 50, 5, 0, 100, "continuous"),
    "froth_depth":      ("mm", 180, 20, 0, 600, "continuous"),
    "reagent_flow":     ("mL/min", 400, 40, 0, 2000, "continuous"),
    "assay_au":         ("g/t", 3.0, 0.5, 0, 200, "analyser"),
    "assay_ag":         ("g/t", 8.0, 1.2, 0, 500, "analyser"),
    "assay_pct":        ("%", 2.0, 0.3, 0, 60, "analyser"),
    "torque_pct":       ("%", 25, 4, 0, 100, "continuous"),
    "ph":               ("pH", 10.5, 0.15, 0, 14, "analyser"),
    "dissolved_oxygen": ("ppm", 8, 1, 0, 30, "analyser"),
    "cyanide":          ("ppm", 250, 30, 0, 1000, "analyser"),
    "power_factor":     ("", 0.92, 0.02, 0, 1, "continuous"),
    "status":           ("", 1, 0, 0, 1, "status"),
    "alarm":            ("", 0, 0, 0, 1, "status"),
    "run_hours":        ("h", 1, 0, 0, 0, "counter"),
    "energy":           ("MWh", 1, 0, 0, 0, "counter"),
    "volume":           ("m3", 1, 0, 0, 0, "counter"),
}
SCALE_BY_TEMPLATE = {"SAG Mill": 12, "Ball Mill": 7, "Crusher": 0.4, "Flotation Cell": 0.15, "Leach Tank": 0.12,
                     "Blower": 0.6, "Air Compressor": 0.2, "Slurry Pump": 0.3}
CONVERT = {("kW", "MW"): 0.001, ("m3/h", "L/s"): 1 / 3.6, ("kPa", "bar"): 0.01}
STOPPING = {"power", "current", "flow", "speed", "speed_pct", "feed_rate", "air_flow"}
DRIVEN = STOPPING | {"pressure", "torque_pct", "density", "level"}
FEATURED = ("Site A", "Concentrator 1")
HMAX = 22716  # hours of history: the length of the Zyfra record; nothing is archived before that
EARLIEST = NOW - HMAX * 3600


def now() -> float:
    return NOW


def _seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big")


def _noise(seed: int, k: np.ndarray) -> np.ndarray:
    """Unit-variance noise that depends only on (seed, k)."""
    x = (np.asarray(k).astype(np.int64).astype(np.uint64) * np.uint64(0x9E3779B97F4A7C15)) ^ np.uint64(seed & 0xFFFFFFFFFFFFFFFF)
    x ^= x >> np.uint64(31)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27)
    u = (x >> np.uint64(11)).astype(np.float64) / float(1 << 53)
    return (u - 0.5) * 3.46


def _slow(seed: int, t: np.ndarray) -> np.ndarray:
    """Slow variation: a daily cycle and shorter swings, unit variance."""
    rng = np.random.default_rng(seed % (2**32))
    periods = np.array([86400, 26300, 7600, 2200, 540])
    amps = np.array([0.6, 0.6, 0.6, 0.4, 0.2])
    phases = rng.uniform(0, 2 * np.pi, len(periods))
    out = sum(a * np.sin(2 * np.pi * t / p + ph) for a, p, ph in zip(amps, periods, phases))
    return out / math.sqrt((amps**2).sum() / 2)


# ---------- the real hourly backbones ----------
@lru_cache(None)
def backbones():
    """The mapping and the columns, or None without the Zyfra file. Without the plant file (a reader who fetched only
    the cited Zyfra data), the plant-set tags are generated."""
    if not (BACKBONES / "zyfra.csv").exists():
        return None
    cfg = yaml.safe_load((HERE / "config" / "backbones.yaml").read_text())
    sources = [s for s in ("zyfra", "plant") if (BACKBONES / f"{s}.csv").exists()]
    cols, n = {}, {"plant": 1}
    for s in sources:
        with (BACKBONES / f"{s}.csv").open() as f:
            r = list(csv.reader(f))
        n[s] = len(r) - 1
        for j, name in enumerate(r[0][1:], 1):
            cols[(s, name)] = np.array([float(x[j]) if x[j] else np.nan for x in r[1:]])
    rules = {}
    for s in sources:
        for area, eq, attr, col, group, *opt in cfg[s]["tags"]:
            rules[(area, eq, attr)] = dict(source=s, col=col, group=group, **(opt[0] if opt else {}))
    std = {k: float(np.nanstd(v)) for k, v in cols.items()}
    low = {k: float(np.nanmin(v)) for k, v in cols.items()}
    return dict(rules=rules, cols=cols, std=std, low=low, feed=cfg["zyfra"]["feed"], stop_below=cfg["zyfra"]["stop_below"],
                nz=n["zyfra"], np=n["plant"])


def location(element):
    """(site, concentrator, area, equipment) from an element path, or None."""
    parts = (element or "").split("\\")
    for i, p in enumerate(parts):
        if p.startswith("Site ") and i + 3 < len(parts) and parts[i + 1].startswith("Concentrator "):
            return p, parts[i + 1], parts[i + 2], parts[i + 3]
    return None


@lru_cache(None)
def circuit(site: str, conc: str) -> dict:
    """One concentrator's clock and scales: one Zyfra offset, one plant offset, one factor per group."""
    b = backbones()
    rng = np.random.default_rng(_seed(site, conc) % (2**32))
    featured = (site, conc) == FEATURED
    z_off = 0 if featured else int(rng.integers(24 * 7, b["nz"] - 24 * 7))
    p_off = int(rng.integers(0, b["np"]))
    feed = b["cols"][("zyfra", b["feed"])]
    zf = feed[(b["nz"] + np.arange(-HMAX, 0) + z_off) % b["nz"]]
    run = ~(zf < b["stop_below"])          # a blank feed hour counts as running
    return dict(featured=featured, z_off=z_off, p_off=p_off, run=run, cum=np.cumsum(run),
                feed_median=float(np.nanmedian(feed)), scales={})


def scale(site: str, conc: str, group: str) -> float:
    c = circuit(site, conc)
    if c["featured"]:
        return 1.0
    if group not in c["scales"]:
        c["scales"][group] = float(np.random.default_rng(_seed(site, conc, group) % (2**32)).uniform(0.9, 1.1))
    return c["scales"][group]


def _fold(H):
    """Older hours repeat the history: an index 0 .. HMAX-1 into the circuit arrays."""
    return (np.asarray(H) + HMAX) % HMAX


def hour_of(t):
    return np.floor((np.asarray(t) - NOW) / 3600).astype(np.int64)


def conc_running(loc, H) -> np.ndarray:
    H = np.asarray(H)
    if not backbones() or not loc:
        return np.ones(H.shape, bool)
    return circuit(loc[0], loc[1])["run"][_fold(H)]


def rule_of(tag: dict):
    """The backbone rule behind a tag; a QC or Calc variant follows its primary's."""
    b, loc = backbones(), location(tag.get("element"))
    if not b or not loc or not tag.get("attr"):
        return None
    attr = tag["attr"].removesuffix(" QC").removesuffix(" Calc")
    return b["rules"].get((loc[2], loc[3], attr))


def hourly(tag: dict, H) -> np.ndarray:
    """The real hourly values behind a tag for hours H (NaN where the source is blank). Tag must have a rule."""
    b, loc, rule = backbones(), location(tag["element"]), rule_of(tag)
    H = np.asarray(H)
    c = circuit(loc[0], loc[1])
    col = b["cols"][(rule["source"], rule["col"])]
    if rule["source"] == "zyfra":
        v = col[(b["nz"] + H + c["z_off"]) % b["nz"]]
    else:  # the plant set holds only running hours: it advances while the concentrator runs, and holds when stopped
        v = col[(c["p_off"] + c["cum"][_fold(H)] + 24 * rule.get("shift_days", 0)) % b["np"]]
        if tag["kind"] in STOPPING:
            v = np.where(c["run"][_fold(H)], v, 0.0)
    return v * rule.get("sign", 1) * rule.get("level", 1) * scale(loc[0], loc[1], rule["group"])


# ---------- values ----------
def _params(tag: dict):
    base_unit, mean, sd, lo, hi, recipe = KINDS[tag["kind"]]
    seed = _seed(tag["point"])
    k = SCALE_BY_TEMPLATE.get(tag.get("template"), 1) if tag["kind"] in ("power", "current") else 1
    rng = np.random.default_rng(seed % (2**32))
    return seed, rng, mean * k * rng.uniform(0.85, 1.15), sd * k, lo, hi * k, recipe, \
        CONVERT.get((base_unit, tag["unit"]), 1.0)


def equipment_running(tag: dict, t: np.ndarray) -> np.ndarray:
    """The equipment runs when its concentrator runs (real feed) and it is not in one of its own short stops."""
    on = conc_running(location(tag.get("element")), hour_of(t))
    day = np.floor(t / 86400).astype(np.int64)
    for d in np.unique(day):
        rng = np.random.default_rng(_seed(tag.get("element"), int(d)) % (2**32))
        if rng.random() < 0.1:
            start = d * 86400 + rng.uniform(0, 86400)
            on &= ~((t >= start) & (t < start + rng.uniform(3600, 8 * 3600)))
    return on


def _real(tag: dict, t: np.ndarray, conv: float) -> np.ndarray:
    """Raw-style values around real hourly means: each hour's time-weighted mean is its real value.
    Hours next to a stop or a blank stay flat, so no ramp runs below zero; real values are not clipped."""
    b, rule, loc = backbones(), rule_of(tag), location(tag["element"])
    t = t - 60.0 * rule.get("lag_min", 0)
    H = hour_of(t)
    hs = np.unique(H)
    n = len(hs)
    three = np.concatenate([hs - 1, hs, hs + 1])
    m3, run3 = hourly(tag, three), conc_running(loc, three)
    prev, cur, nxt = m3[:n], m3[n:2 * n], m3[2 * n:]
    stopped = ~run3[n:2 * n]
    flat = np.isnan(prev) | np.isnan(nxt) | ~run3[:n] | stopped | ~run3[2 * n:]
    colsd = b["std"][(rule["source"], rule["col"])] * rule.get("level", 1) * scale(loc[0], loc[1], rule["group"])
    seed = _seed(tag["point"])
    analyser = KINDS[tag["kind"]][5] == "analyser"
    plant_stops = rule["source"] == "plant" and tag["kind"] in STOPPING
    nonneg = b["low"][(rule["source"], rule["col"])] * rule.get("sign", 1) >= 0
    out = np.empty(t.shape)
    pos = np.searchsorted(hs, H)
    for i, h in enumerate(hs.tolist()):
        sel = pos == i
        ti, start, m = t[sel], NOW + h * 3600, cur[i]
        if np.isnan(m):
            out[sel] = np.nan
        elif stopped[i] and (plant_stops or not analyser):
            out[sel] = 0.0 if plant_stops else m   # a stopped hour: zero (plant set) or flat at its real value
        else:
            # variation inside the hour, smaller near zero so a column with no negatives gets none
            amp = colsd if not nonneg else min(colsd, abs(m) / 0.5)
            if analyser:  # one value per analyser cycle; the four cycles average to the hour
                nz = _noise(seed, h * 4 + np.arange(4))
                k = np.floor((ti - start) / ANALYSER_CYCLE).astype(int).clip(0, 3)
                out[sel] = m + 0.05 * amp * (nz - nz.mean())[k]
                continue
            grid = start + SCAN * np.arange(720)
            wig = lambda x: 0.08 * amp * _slow(seed, x) + 0.02 * amp * _noise(seed, np.floor(x / SCAN))
            w = wig(ti) - wig(grid).mean()
            a, c = prev[i], nxt[i]
            line = lambda x: np.where(x < 1800, a + (m - a) * (x + 1800) / 3600, m + (c - m) * (x - 1800) / 3600)
            corr = 0.0 if flat[i] else m - line(grid - start).mean()  # so the hour's scans average to the real value
            if flat[i] or (nonneg and min(a, c, m) + corr - 0.2 * amp < 0):
                out[sel] = m + w
            else:
                out[sel] = line(ti - start) + corr + w
    return out * conv


METERS: dict = {}  # point name -> the tags a power meter measures; filled by the mock from its asset tree
ENERGY: dict = {}  # energy counter's point name -> the active power tag of the same meter; filled by the mock


@lru_cache(None)
def _energy_hours(point: str) -> np.ndarray:
    """MWh the meter has counted at the start of each hour since EARLIEST: its active power, sampled every 15 min."""
    pw = ENERGY[point]
    n = int(round((NOW - EARLIEST) / 3600))
    t = EARLIEST + (np.arange(n * 4) + 0.5) * 900
    kw = np.nan_to_num(scans(pw, t) / CONVERT.get(("kW", pw["unit"]), 1.0))
    return np.concatenate([[0.0], np.cumsum(kw.reshape(n, 4).mean(axis=1) / 1000)])


def scans(tag: dict, t: np.ndarray) -> np.ndarray:
    """Values at times t (seconds since the epoch). NaN where the source has no value or before the archive starts."""
    t = np.asarray(t, dtype=float)
    before = t < EARLIEST
    if before.any():
        out = np.full(t.shape, np.nan)
        if (~before).any():
            out[~before] = scans(tag, t[~before])
        return out
    seed, rng, mean, sd, lo, hi, recipe, conv = _params(tag)
    if tag["point"] in METERS:  # a supply meter reads the sum of its loads, plus 3 % losses
        kw = sum(np.nan_to_num(scans(m, t) / CONVERT.get(("kW", m["unit"]), 1.0)) for m in METERS[tag["point"]])
        return (1.03 * kw + 0.002 * mean * _noise(seed, np.floor(t / SCAN))) * conv
    if recipe == "status":
        if tag["kind"] == "alarm":
            return (_noise(seed, np.floor(t / 3600)) > 1.6).astype(float)
        return equipment_running(tag, t).astype(float)
    if recipe == "counter" and tag["point"] in ENERGY:  # an energy counter integrates its meter's power, hour by hour
        cum = _energy_hours(tag["point"])
        x = (t - EARLIEST) / 3600
        h = np.clip(np.floor(x).astype(int), 0, len(cum) - 2)
        mwh = rng.uniform(1e3, 5e4) + cum[h] + (x - h) * (cum[h + 1] - cum[h])
        return np.round(mwh, 3) * conv
    if recipe == "counter":
        rate = {"run_hours": 0.93 / 3600, "energy": mean / 3.6e6, "volume": 600 / 3600}[tag["kind"]]
        return np.round(rng.uniform(1e3, 5e4) + (t - 1.7e9) * rate, 2)  # ponytail: fixed rate, not integrated
    if rule_of(tag):
        return _real(tag, t, conv)
    if recipe == "analyser":
        k = np.floor(t / ANALYSER_CYCLE)
        v = mean + sd * (0.7 * _slow(seed, k * ANALYSER_CYCLE) + 0.5 * _noise(seed, k))
    else:
        v = mean + sd * (0.8 * _slow(seed, t) + 0.05 * _noise(seed, np.floor(t / SCAN)))
    loc = location(tag.get("element"))
    if backbones() and loc and tag["kind"] in DRIVEN:  # generated, but moving with the concentrator's real feed
        b, c = backbones(), circuit(loc[0], loc[1])
        feed = b["cols"][("zyfra", b["feed"])][(b["nz"] + hour_of(t) + c["z_off"]) % b["nz"]]
        v = v * np.nan_to_num(feed / c["feed_median"], nan=1.0).clip(0.2, 1.6) ** 0.6
    if recipe == "integer":
        v = np.round(v)
    if tag["kind"] in STOPPING and tag.get("stops", True):
        v = np.where(equipment_running(tag, t), v, 0.0)
    return np.clip(v, lo, hi) * conv


def last_valid(tag: dict):
    """End of the newest hour with a value (tags on a real backbone); NOW for the others; None if none in 2000 h."""
    if not rule_of(tag):
        return NOW
    H = np.arange(-2000, 0)
    ok = np.flatnonzero(~np.isnan(hourly(tag, H)))
    return None if len(ok) == 0 else NOW + (int(H[ok[-1]]) + 1) * 3600


def deadband(tag: dict) -> float:
    seed, rng, mean, sd, lo, hi, recipe, conv = _params(tag)
    if recipe != "continuous":
        return 0.0
    rule = rule_of(tag)
    if rule:
        return 0.01 * backbones()["std"][(rule["source"], rule["col"])] * rule.get("level", 1) * conv
    return 0.1 * sd * conv


def recorded(tag: dict, start: float, end: float, max_count: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """What the archive holds between start and end: the exception test over 5-second scans."""
    out_t, out_v = [], []
    db = deadband(tag)
    end = min(end, NOW)
    t0 = math.ceil(max(start, EARLIEST) / SCAN) * SCAN
    last_t = last_v = None
    while t0 <= end and len(out_t) < max_count:
        t = t0 + SCAN * np.arange(int((min(end, t0 + 86400) - t0) // SCAN) + 1)
        prev = None
        for ti, vi in zip(t.tolist(), scans(tag, t).tolist()):
            if vi != vi:  # no value in the source for this hour
                prev = None
                continue
            if last_t is None or abs(vi - last_v) > db or ti - last_t >= MAX_GAP:
                if prev is not None and last_t is not None and prev[0] != last_t and abs(vi - last_v) > db:
                    out_t.append(prev[0]); out_v.append(prev[1])   # the scan before a change is kept too
                out_t.append(ti); out_v.append(vi)
                last_t, last_v = ti, vi
                if len(out_t) >= max_count:
                    break
            prev = (ti, vi)
        t0 = t[-1] + SCAN
    return np.array(out_t[:max_count]), np.array(out_v[:max_count])


def summary(tag: dict, start: float, end: float) -> dict:
    """Time-weighted statistics over [start, end), from the scans (60-second grid for windows over 7 days).
    Hours without a value are left out."""
    step = SCAN if end - start <= 7 * 86400 else 60.0
    t = np.arange(max(start, EARLIEST), min(end, NOW), step)
    if len(t) == 0:
        return {}
    v = scans(tag, t)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return {}
    return {"Average": float(v.mean()), "Minimum": float(v.min()), "Maximum": float(v.max()),
            "StdDev": float(v.std()), "Count": int(len(v)), "Range": float(v.max() - v.min()),
            "Total": float(v.mean() * len(v) * step / 86400)}  # PI's Total: per-day units for rates


def demo():
    tag = dict(kind="feed_rate", unit="t/h", point="X", element="E", template="SAG Mill", stops=False)
    t = np.arange(NOW - 3600, NOW, SCAN)
    assert np.array_equal(scans(tag, t), scans(tag, t)), "values must be deterministic"
    rt, rv = recorded(tag, NOW - 3600, NOW, 100000)
    assert len(rt) < len(t) and np.all(np.diff(rt) > 0) and np.all(np.diff(rt) <= MAX_GAP)
    print("values ok:", len(rt), "records in an hour;", "backbones loaded" if backbones() else "no backbones")


if __name__ == "__main__":
    demo()
