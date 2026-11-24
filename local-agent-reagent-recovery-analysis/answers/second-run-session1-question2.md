## Tool calls

- `write` {"content": "import os\nos.environ[\"MPLCONFIGDIR\"] = \"/tmp/mpl\"\nimport numpy as np, pandas as pd, glob, json\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nDS = \"articles/local-agent-reagent-recovery-analysis/local/runs/kit/datasets\"\ndf = pd.concat([pd.read_csv(f) for f in sorted(g
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 analyze_grade.py 2>/dev/null"}

## Answer

**Yes — the relationship is different at each feed grade, and it weakens as feed grade rises.** Over the full record (2024‑04‑20 → 2026‑11‑22, same screened running hours as before: 18,847 used), the dose‑rate–recovery slope is about 2.8× steeper at low feed grade than at high feed grade:

| Feed grade (rougher feed Au) | n (hrs) | Slope (pp per mL/min) | r | Weighted rougher recovery |
|---|---|---|---|---|
| **Low** ≤ 7.26 g/t | 6,283 | **+2.86** | 0.32 | 82.2 % |
| **Mid** 7.26–9.19 g/t | 6,282 | **+1.72** | 0.28 | 84.7 % |
| **High** > 9.19 g/t | 6,282 | **+1.03** | 0.22 | 89.0 % |

**Is the difference real?** Block bootstrap (whole weeks, 1,000 draws) on the slope differences:

- high − low: **−1.83 pp per mL/min, 95 % CI [−3.08, −0.68]** → excludes zero; the weaker association at high grade is shown by the data.
- mid − low: −1.14, 95 % CI [−2.20, −0.22] → also excludes zero.
- high − mid: −0.69, 95 % CI [−1.64, +0.12] → spans zero; not distinguishable.

So the data support a monotone weakening: the collector dose rate is most strongly associated with rougher recovery when the feed is low grade, and least so when it is high grade.

**Chart:** saved as `collector_vs_recovery_by_feed_grade.png` in the current folder — three panels (low / mid / high grade), each with the hourly points, least‑squares line (slope, r, n) and the band's metal‑in‑weighted recovery; the title carries the pairwise slope differences and their CIs.

**Caveats (same basis as before)**

- Same tags and cleaning: recovery from Rougher Feed/Concentrate/Tail Au (`SA-C1-AT-3069/3074/3079`), collector dose rate `SA-C1-FT-3057` (stale since 2026‑11‑13), running hours = SAG feed rate ≥ 50 t/h, 1,842 hours screened out.
- Association, not effect: dose rate is operator‑set and tracks grade and throughput (mean dose rises across the bands, 5.75 → 6.32 mL/min), so part of the band‑to‑band difference reflects how operators respond to grade, not a proven causal dose–recovery response.
