## Tool calls

- `write` {"content": "import os\nimport numpy as np\nimport pandas as pd\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nos.environ.setdefault(\"MPLCONFIGDIR\", \"/tmp/mpl\")\n\nDS = \"articles/local-agent-reagent-recovery-analysis/local/runs/kit/datasets\"\nfiles = [\n    \"20261123-202451-0858e4.c
- `edit` {"edits": [{"oldText": "stats = {}\nfor lab, g in groups.items():\n    k, b, rr, nn = fit(g[\"dose_t\"], g[\"rec\"])\n    stats[lab] = (nn, k, rr, b)\n    print(f\"{lab}: n {nn}, slope {k:.4f} pp per mL/t, r {rr:.3f}, mean recovery {g['rec'].mean():.1f}%\")", "newText": "stats = {}\nfor lab, g in groups.items():\n    k, b, rr, nn = fit(g[COL], g[\"rec\"])\n    stats[lab] = (nn, k, rr, b)\n    kt, 
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 analyze_by_grade.py"}

## Answer

**Bottom line:** the relationship does *appear* to differ by feed grade in raw dose rate — steeper at low grade (2.86 pp per mL/min, r = 0.32) than at high grade (1.03 pp per mL/min, r = 0.22) — but that difference is a throughput artifact, not a real grade effect. On **dose per tonne** (which removes the throughput confound), the slope is essentially zero in every third: low −0.01, mid +0.13, high +0.06 percentage points per mL/t (r = −0.004, 0.06, 0.05). So at each feed grade, collector dose shows no meaningful relationship with rougher gold recovery.

**By feed-grade third** (cuts at the terciles of rougher feed Au: 7.26 and 9.19 g/t; running hours, screened, 2024‑04‑20 → 2026‑11‑13):

| Third | Feed grade (g/t) | n | Slope, mL/min | r | Slope, mL/t | r | Mean recovery |
|---|---|---|---|---|---|---|---|
| Low | ≤ 7.26 | 6 283 | +2.86 | 0.32 | −0.01 | −0.004 | 81.5 % |
| Mid | 7.26–9.19 | 6 282 | +1.72 | 0.28 | +0.13 | 0.06 | 84.4 % |
| High | > 9.19 | 6 282 | +1.03 | 0.22 | +0.06 | 0.05 | 88.8 % |

**Is the difference real?** Block bootstrap (1 000 weekly draws) on the raw-flow slopes: low − high = 0.68 to 3.08 pp per mL/min (excludes zero — the *apparent* difference is real), low − mid = 0.22 to 2.20 (excludes zero), mid − high = −0.12 to 1.64 (spans zero). But since the dose-per-tonne slopes are all near zero and indistinguishable, the graded pattern in the raw flow form comes from throughput: the collector pump flow follows the fresh feed rate (r = 0.58 overall), and low-grade periods ran at different throughput than high-grade periods.

**Caveats**
- This is an association, not an effect of the reagent; dose rate is set by operators in response to grade, throughput and other conditions.
- Same tags and screening as before: collector SA‑C1‑FT‑3057 (mL/min), rougher feed/concentrate/tail Au SA‑C1‑AT‑3069/3074/3079 (g/t), SAG fresh feed rate SA‑C1‑WT‑2001 (t/h); 18 847 running, screened hours used.
- Chart saved to `collector_vs_recovery_by_feed_grade.png` in this folder (three panels, one per feed-grade third, recovery vs collector dose rate with fit line).
