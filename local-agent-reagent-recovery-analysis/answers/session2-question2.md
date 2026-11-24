## Tool calls

- `write` {"path": "plot_collector_recovery_by_grade.py", "content": "import pandas as pd\nimport numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nCSV = \"articles/local-agent-reagent-recovery-analysis/local/runs/r1/datasets/20261123-192502-6532e2.csv\"\nOUT = \"collector_dose_vs_recovery_
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/2 && python3 plot_collector_recovery_by_grade.py"}
- `read` {"path": "collector_dose_vs_recovery_by_feed_grade.png"}

## Answer

Chart is saved as `collector_dose_vs_recovery_by_feed_grade.png` (script: `plot_collector_recovery_by_grade.py`) — three panels, one per feed-grade tercile, all on the same recovery axis.

## Summary of what the chart shows

| Band | Feed Au (g/t) | n | Dose range (mL/min) | r |
|---|---|---|---|---|
| **Low** | 0.7–7.1 | 293 | 0.0–8.5 | **0.53** |
| **Mid** | 7.1–8.9 | 292 | 2.8–8.2 | **0.32** |
| **High** | 8.9–13.0 | 293 | 3.0–8.3 | **0.20** |

- **Low grade:** steep dose response — recovery climbs from erratic low values at start-up doses (<3 mL/min) to ~85–88% at 6.5–8.5 mL/min. Collector is the limiting reagent here.
- **Mid grade:** positive but flatter, with more scatter.
- **High grade:** essentially flat — recovery holds in the high-70s to low-80s% across the dose range; extra collector buys little.

So the overall r ≈ 0.48 from the previous chart was driven mostly by low-grade days. At high feed grade, recovery is governed by other factors (grind, feed rate, etc.), not collector dose.

**Provenance & caveats (unchanged from before):** same dataset `runs/r1/datasets/20261123-192502-6532e2.csv`; tags SA-C1-FT-3057 (dose, ⚠️ stale after 2026-11-13), SA-C1-AT-3069/3074/3079 (rougher feed/concentrate/tail Au, all healthy); daily time-weighted averages, 2024-04-20 → 2026-11-13; recovery computed from the three-assay mass balance; tercile cut-points (7.08 / 8.89 g/t) computed on the 878 valid days; binned-mean lines (8 dose bins per panel) are the more reliable trend given day-level assay noise.
