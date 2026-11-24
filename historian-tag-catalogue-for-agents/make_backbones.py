"""Cut the hourly backbone files the mock reads from the two source files: only the columns config/backbones.yaml
names, in time order, blanks kept as they are.

    uv run python make_backbones.py --zyfra <gold_recovery_full.csv> [--plant <hourly.csv>]

Writes local/backbones/zyfra.csv, and local/backbones/plant.csv when the plant file is given. The Zyfra file is cited in
the README (where to fetch it); the plant file is private, so a reader runs without it and those tags are generated.
"""
import argparse, csv, math
from pathlib import Path

import yaml

HERE = Path(__file__).parent
OUT = HERE / "local" / "backbones"


def number(x: str) -> str:
    try:
        v = float(x)
        return "" if math.isnan(v) else repr(v)
    except ValueError:
        return ""  # spreadsheet errors such as #VALUE! are blanks


def cut(src: Path, time_col: str, cols: list[str], dst: Path):
    with src.open(newline="") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in cols if c not in rows[0]]
    if missing:
        raise SystemExit(f"{src}: no column {', '.join(missing)}")
    rows.sort(key=lambda r: r[time_col])
    with dst.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time"] + cols)
        for r in rows:
            w.writerow([r[time_col]] + [number(r[c]) for c in cols])
    print(f"{dst}: {len(rows)} hours, {len(cols)} columns")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zyfra", type=Path, required=True)
    ap.add_argument("--plant", type=Path)
    a = ap.parse_args()
    cfg = yaml.safe_load((HERE / "config" / "backbones.yaml").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    z = sorted({t[3] for t in cfg["zyfra"]["tags"]} | {cfg["zyfra"]["feed"]})
    p = sorted({t[3] for t in cfg["plant"]["tags"]})
    cut(a.zyfra, "date", z, OUT / "zyfra.csv")
    if a.plant:
        cut(a.plant, "time", p, OUT / "plant.csv")


if __name__ == "__main__":
    main()
