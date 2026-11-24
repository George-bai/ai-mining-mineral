## Tool calls

- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nCSV = \"articles/local-agent-reagent-recovery-analysis/local/runs/r1/datasets/20261123
- `write` {"content": "\"\"\"Rougher gold recovery vs collector dose rate, split by rougher feed gold grade.\n\nSame data and recovery formula as collector_recovery.py:\n    recovery = 100 * (1 - gt*T / (gf*F)),  F = C + T\nFeed grade bands = tertiles of the rougher feed Au assay:\n    low  < 7.08 g/t | mid 7.08-8.88 g/t | high > 8.88 g/t\n\"\"\"\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotli
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 collector_recovery_by_grade.py"}

## Answer

Chart saved: `collector_dose_vs_recovery_by_feed_grade.png` (script: `collector_recovery_by_grade.py`, same dataset as before).

## Yes — the relationship is clearly different at each feed grade

Feed grade bands are the tertiles of the rougher feed Au assay (880 days, ~293 each):

| Band | n | Mean feed Au | Mean recovery | r (dose vs recovery) |
|---|---|---|---|---|
| Low (< 7.08 g/t) | 294 | 5.8 g/t | 84.9% | **0.62** |
| Mid (7.08–8.88 g/t) | 293 | 7.9 g/t | 88.7% | 0.38 |
| High (> 8.88 g/t) | 293 | 10.3 g/t | 90.1% | 0.28 |

Reading the panels:

- **Low grade:** collector dose matters most. Recovery climbs from ~75–80% at ~1.5 mL/min to ~88–90% at 6–8 mL/min — a spread of ~10–15 points. Under-dosing the collector costs the most on low-grade feed.
- **Mid grade:** still a clear positive trend but weaker; ~84% at low dose rising to ~89–90% at high dose.
- **High grade:** recovery is high (~90%) and nearly flat across the whole dose range — the extra collector is doing little. The plant is already recovering most of the gold, so the marginal benefit of more collector is small.

**Interpretation:** the positive dose–recovery relationship seen overall (r = 0.55) is driven mainly by low-grade feed days. At high feed grade, recovery is already near its ceiling, so dose changes barely move it. Practically: on low-grade feed, maintaining the higher end of the collector dose range (~6–8 mL/min) is worth ~10 points of rougher recovery; on high-grade feed, there's little recovery to gain from extra collector (though concentrate grade would fall, which this analysis doesn't cover).

Same caveats as before: collector dose tag stale after 2026-11-13; feed flow = rougher conc pump + tail pump flow (no direct feed flow tag); volumetric-flow tail-loss formula, daily time-weighted averages.
