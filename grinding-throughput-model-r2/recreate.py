#!/usr/bin/env python3
"""Rebuild every value of the Kaggle file Mining_Grinding_Throughput.csv from seed 42, fit the regression,
and show what it learned.

Standard library only. NumPy's legacy generator (MT19937, as np.random.seed(42) sets it up) is written out
below, so the draws come out bit for bit as NumPy gives them and no NumPy is needed.

  python3 recreate.py                         rebuild the file, fit the regression, print the numbers
  python3 recreate.py --csv FILE              also compare the rebuild with the downloaded file, value by value
  python3 recreate.py --write FILE            also write the rebuilt file
"""
import argparse
import csv
import math
import sys

N = 5000
# The fourteen inputs in file order, with the limits each is drawn between (found from the file: every value
# lies inside them, and with these limits and seed 42 every value is reproduced).
INPUTS = [
    ("Ore_Hardness_MPa", 80, 180), ("Feed_Size_mm", 10, 35), ("Ore_Density_t_m3", 2.3, 3.8),
    ("Mill_Speed_RPM", 12, 18), ("Mill_Load_Percentage", 60, 90), ("Water_Flow_Rate_m3_hr", 140, 270),
    ("Feed_Rate_tph", 180, 380), ("Power_Consumption_kW", 650, 1300), ("Grinding_Media_kg", 3000, 6000),
    ("Temperature_C", 30, 50), ("Vibration_Level_mm_s", 2, 6), ("Moisture_Content_Percentage", 2, 7),
    ("Mineral_Grade_Percentage", 1.5, 5), ("Operating_Hours", 10, 30),
]
NAMES = [c for c, _, _ in INPUTS]
TARGET = "Grinding_Throughput_TPH"
# The throughput recipe, before it is stretched to 170-350 t/h. Temperature and operating hours carry no weight;
# feed size enters only through a sine of its value in millimetres, read as radians.
WEIGHTS = {"Ore_Hardness_MPa": -0.18, "Ore_Density_t_m3": 25, "Mill_Speed_RPM": 7.5, "Mill_Load_Percentage": 0.45,
           "Water_Flow_Rate_m3_hr": 0.08, "Feed_Rate_tph": 0.32, "Power_Consumption_kW": 0.015,
           "Grinding_Media_kg": 0.004, "Vibration_Level_mm_s": -2, "Moisture_Content_Percentage": -1.5,
           "Mineral_Grade_Percentage": 6}
SINE, NOISE_SD, LOW, HIGH = 5, 4, 170, 350


class Legacy:
    """NumPy's legacy RandomState: MT19937 seeded by an integer, 53-bit doubles, polar normal draws."""

    def __init__(self, seed):
        mt = [seed & 0xFFFFFFFF]
        for i in range(1, 624):
            mt.append((1812433253 * (mt[-1] ^ (mt[-1] >> 30)) + i) & 0xFFFFFFFF)
        self.mt, self.i, self.spare = mt, 624, None

    def _int32(self):
        if self.i >= 624:
            mt = self.mt
            for k in range(624):
                y = (mt[k] & 0x80000000) | (mt[(k + 1) % 624] & 0x7FFFFFFF)
                mt[k] = mt[(k + 397) % 624] ^ (y >> 1) ^ (0x9908B0DF if y & 1 else 0)
            self.i = 0
        y = self.mt[self.i]
        self.i += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        return y ^ (y >> 18)

    def double(self):
        a, b = self._int32() >> 5, self._int32() >> 6
        return (a * 67108864.0 + b) / 9007199254740992.0

    def uniform(self, lo, hi, n):
        return [lo + (hi - lo) * self.double() for _ in range(n)]

    def normal(self, loc, scale, n):
        out = []
        for _ in range(n):
            if self.spare is None:                       # draw a pair, keep one for the next call
                while True:
                    x1, x2 = 2.0 * self.double() - 1.0, 2.0 * self.double() - 1.0
                    r2 = x1 * x1 + x2 * x2
                    if 0.0 < r2 < 1.0:
                        break
                f = math.sqrt(-2.0 * math.log(r2) / r2)
                self.spare, g = f * x1, f * x2
            else:
                g, self.spare = self.spare, None
            out.append(loc + scale * g)
        return out


def round2(x):
    """np.round(np.round(x, 3), 2): the file's values were rounded twice, to 3 places and then to 2."""
    return round(round(x * 1000) / 1000 * 100) / 100


def rebuild():
    """The file as seed 42 makes it, plus the unrounded parts of the throughput, in t/h."""
    rng = Legacy(42)
    raw = {c: rng.uniform(lo, hi, N) for c, lo, hi in INPUTS}
    noise = rng.normal(0, NOISE_SD, N)
    s = []
    for r in range(N):
        v = 0
        for c, w in WEIGHTS.items():
            v = v + w * raw[c][r]
        s.append(v + SINE * math.sin(raw["Feed_Size_mm"][r]) + noise[r])
    lo, hi = min(s), max(s)
    y = [LOW + (v - lo) / (hi - lo) * (HIGH - LOW) for v in s]
    k = (HIGH - LOW) / (hi - lo)                          # t/h per unit of the recipe before stretching
    rows = [[round2(raw[c][r]) for c in NAMES] + [round2(y[r])] for r in range(N)]
    parts = {"straight": [k * sum(w * raw[c][r] for c, w in WEIGHTS.items()) for r in range(N)],
             "sine": [k * SINE * math.sin(raw["Feed_Size_mm"][r]) for r in range(N)],
             "noise": [k * e for e in noise]}
    return rows, parts, k


# ---------------------------------------------------------------- least squares, standard library only
def mean(v): return sum(v) / len(v)
def var(v):
    m = mean(v)
    return sum((x - m) ** 2 for x in v) / len(v)
def corr(a, b):
    ma, mb = mean(a), mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


def solve(A, b):
    """Gaussian elimination with partial pivoting."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for j in range(c, n + 1):
                M[r][j] -= f * M[c][j]
    x = [0.0] * n
    for c in range(n - 1, -1, -1):
        x[c] = (M[c][n] - sum(M[c][j] * x[j] for j in range(c + 1, n))) / M[c][c]
    return x


def fit(X, y):
    """Ordinary least squares with an intercept. Columns are centred and scaled first, for a well-posed system."""
    p = len(X[0])
    cols = list(zip(*X))
    mu = [mean(c) for c in cols]
    sd = [math.sqrt(var(c)) or 1.0 for c in cols]
    Z = [[(row[j] - mu[j]) / sd[j] for j in range(p)] for row in X]
    my = mean(y)
    A = [[sum(z[i] * z[j] for z in Z) for j in range(p)] for i in range(p)]
    b = [sum(z[i] * (t - my) for z, t in zip(Z, y)) for i in range(p)]
    beta = [g / s for g, s in zip(solve(A, b), sd)]
    return beta, my - sum(bj * m for bj, m in zip(beta, mu))


def predict(model, X):
    beta, a = model
    return [a + sum(b * x for b, x in zip(beta, row)) for row in X]


def r2(y, yhat):
    m = mean(y)
    return 1 - sum((t - f) ** 2 for t, f in zip(y, yhat)) / sum((t - m) ** 2 for t in y)


def results(rows, parts, k):
    """Every number the article uses."""
    X, y = [r[:-1] for r in rows], [r[-1] for r in rows]
    model = fit(X, y)
    folds = []
    for f in range(5):                                    # five held-out folds: every fifth row
        tr = [i for i in range(N) if i % 5 != f]
        te = [i for i in range(N) if i % 5 == f]
        m = fit([X[i] for i in tr], [y[i] for i in tr])
        folds.append(r2([y[i] for i in te], predict(m, [X[i] for i in te])))
    with_sine = fit([row + [math.sin(row[1])] for row in X], y)
    total = var([a + b + c for a, b, c in zip(parts["straight"], parts["sine"], parts["noise"])])
    cols = list(zip(*X))
    pairs = [(abs(corr(cols[i], cols[j])), NAMES[i], NAMES[j]) for i in range(14) for j in range(i + 1, 14)]
    span = {c: hi - lo for c, lo, hi in INPUTS}
    return {
        "scale": k,
        "r2_all": r2(y, predict(model, X)),
        "r2_folds": folds,
        "r2_with_sine": r2(y, predict(with_sine, [row + [math.sin(row[1])] for row in X])),
        "share": {p: var(v) / total for p, v in parts.items()},
        "effect_recipe": {c: k * WEIGHTS.get(c, 0) * span[c] for c in NAMES},     # t/h across each input's range
        "effect_learned": {c: b * span[c] for c, b in zip(NAMES, model[0])},
        "weight_learned": dict(zip(NAMES, model[0])),
        "sine_amplitude": k * SINE, "noise_sd": k * NOISE_SD,
        "out_above_in": sum(1 for r in rows if r[-1] > r[NAMES.index("Feed_Rate_tph")]),
        "max_input_corr": max(pairs),
        "corr_with_throughput": {c: corr(cols[j], y) for j, c in enumerate(NAMES)},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--csv", help="the downloaded Mining_Grinding_Throughput.csv, to compare value by value")
    ap.add_argument("--write", help="write the rebuilt file here")
    a = ap.parse_args()
    rows, parts, k = rebuild()
    if a.write:
        with open(a.write, "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(NAMES + [TARGET])
            w.writerows(rows)
    if a.csv:
        with open(a.csv, newline="") as f:
            rd = csv.reader(f)
            assert next(rd) == NAMES + [TARGET], "unexpected header"
            got = [[float(x) for x in r] for r in rd]
        assert len(got) == N, f"{len(got)} rows"
        same = [sum(1 for r in range(N) if got[r][j] == rows[r][j]) for j in range(15)]
        print(f"inputs:     {sum(same[:14]):,} of {14 * N:,} values match")
        print(f"throughput: {same[14]:,} of {N:,} values match")
        if sum(same) != 15 * N:
            sys.exit("✗ the rebuild differs from the file")
    R = results(rows, parts, k)
    f = R["r2_folds"]
    print(f"R² on all rows {R['r2_all']:.4f}; five held-out folds {min(f):.4f} to {max(f):.4f}, mean {sum(f) / 5:.4f}")
    print(f"R² with the sine of feed size added {R['r2_with_sine']:.4f}")
    print("shares of throughput variance: " + ", ".join(f"{p} {v:.2%}" for p, v in R["share"].items()))
    print(f"rows with throughput above feed rate: {R['out_above_in']:,} of {N:,}")
    print(f"largest correlation between two inputs: {R['max_input_corr'][0]:.3f} ({R['max_input_corr'][1]}, {R['max_input_corr'][2]})")
    print(f"stretch: {k:.5f} t/h per recipe unit; sine ±{R['sine_amplitude']:.2f} t/h; noise sd {R['noise_sd']:.2f} t/h")
    print(f"{'input':30s} {'recipe t/h':>10s} {'learned t/h':>11s}   (change across the input's range)")
    for c in NAMES:
        print(f"{c:30s} {R['effect_recipe'][c]:10.2f} {R['effect_learned'][c]:11.2f}")


if __name__ == "__main__":
    main()
