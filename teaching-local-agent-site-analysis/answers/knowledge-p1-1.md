## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "limit": 15}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-04-20", "end": "2026-11-23", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-04-20", "end": "2026-11-23", "interval": "6h", "mode": "summary", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-04-20", "end": "2026-11-23", "interval": "1d", "mode": "summary", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/1 && python3 -c \"import pandas, matplotlib, numpy; print('ok')\" 2>&1; head -3 articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/1 && cat > analyze.py <<'EOF'\nimport pandas as pd, numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf = \"articles/tea
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/1 && cat > chart.py <<'EOF'\nimport pandas as pd, numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nd = pd.read_csv(\"rougher_dose_recovery_daily.csv\", parse_dates=[\"time\"])\ncolors = {\"low\":\
- `edit` {"path": "chart.py", "edits": [{"oldText": "    ax.plot(m.index, m.values, \"-o\", color=colors[b], ms=5, lw=2, alpha=0.9)", "newText": "    ax.plot(m.index.map(lambda i: i.center), m.values, \"-o\", color=colors[b], ms=5, lw=2, alpha=0.9)"}]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/1 && MPLCONFIGDIR=/tmp/mpl python3 chart.py && ls -la collector_dose_vs_rougher_recovery.png"}
- `edit` {"path": "chart.py", "edits": [{"oldText": "i.center", "newText": "i.mid"}]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/1 && MPLCONFIGDIR=/tmp/mpl python3 chart.py && ls -la collector_dose_vs_rougher_recovery.png"}
- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/1/collector_dose_vs_rougher_recovery.png"}

## Answer

Chart saved: `collector_dose_vs_rougher_recovery.png` (plus `rougher_dose_recovery_daily.csv` with the daily working data).

## Answer

**Yes, there is a real positive relationship — but most of it is carried by feed grade, and the dose–recovery relationship does differ by grade band.**

**Overall (all running days, Apr 2024 – Nov 2026, 861 usable days):**
- Collector dose rate vs rougher gold recovery: **r = 0.52** (regression ≈ 62 recovery points per mL/min across the observed 4.4–7.2 mL/min range; recovery 74–93%, mean 84%).
- But dose **per tonne** (dose ÷ feed rate) vs recovery is only **r = 0.10**, while feed grade (Rougher Feed Au) vs recovery is r = 0.53 and feed grade vs dose is r = 0.38. So much of the apparent dose effect is that high-grade days run higher dose rates *and* recover better.

**By feed grade (terciles of Rougher Feed Au: low < 7.0, mid 7.0–9.0, high > 9.0 g/t):**

| Band | n | avg dose (mL/min) | avg recovery | r(dose, rec) | Recovery, low→high dose tercile |
|---|---|---|---|---|---|
| Low grade | 287 | 5.31 | 79.1% | **0.57** | 73.3 → 84.1 → 84.2 |
| Mid grade | 287 | 5.94 | 84.4% | 0.30 | 82.4 → 83.9 → 86.7 |
| High grade | 287 | 6.25 | 88.8% | 0.26 | 87.9 → 87.9 → 89.9 |

- **Low grade:** the strongest dose–recovery relationship (r = 0.57) — going from the lowest to the highest dose tercile lifts recovery ~11 points (73 → 84%), and the recovery gain is essentially all in the low→mid dose step.
- **Mid grade:** moderate (r = 0.30), ~4 points across the dose range.
- **High grade:** weakest (r = 0.26), ~2 points — recovery is high regardless of dose, so dose has little visible leverage there.

Interpretation: at low feed grade, collector dose is where the recovery swings happen; at high grade the rougher is already recovering well and dose changes buy little. (Correlation, not controlled experiment — dose and grade both co-vary with ore and operating conditions.)

**Provenance**
- Tags (all primary, Site A Concentrator 1): Collector|Dose Rate `SA-C1-FT-3057` (mL/min); SAG Mill|Fresh Feed Rate `SA-C1-WT-2001` (t/h); Rougher Feed|Au `SA-C1-AT-3069`, Rougher Concentrate|Au `SA-C1-AT-3074`, Rougher Tail|Au `SA-C1-AT-3079` (g/t).
- Window: 2024-04-20 (historian's earliest record) to 2026-11-22, daily time-weighted averages (historian rejected 1h/6h intervals as too many summary intervals, so stop exclusion is at day level: days with average feed < 50 t/h excluded — 2 days; 19 days with invalid two-product recovery dropped, 861 usable).
- Recovery = 100·c(f−t)/(f(c−t)) from the same day's rougher feed/concentrate/tail Au, per the site's two-product method.
- Caveat: the collector dose rate tag is currently **stale** (last value 2026-11-13, ~10 days ago; no QC/calc variant exists), so the most recent 10 days of dose are missing — immaterial for a 2.6-year study, but worth flagging to the instrument team.
