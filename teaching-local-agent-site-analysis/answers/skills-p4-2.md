## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-01-01", "end": "2026-02-20", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-02-20", "end": "2026-04-11", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-04-11", "end": "2026-06-01", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-06-01", "end": "2026-07-21", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-07-21", "end": "2026-09-09", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-09-09", "end": "2026-10-29", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-10-29", "end": "2026-11-23", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/2 && python3 << 'EOF'\nimport pandas as pd, numpy as np\n\nfiles = [\n \"articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-195408-334f0
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/2 && python3 << 'EOF'\nimport pandas as pd, numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nres = pd.read_csv(\"recovery_monthly_2026.csv\")\nhr = pd.read_csv(\"recovery_hourly_2026.csv\", parse_dat

## Answer

**August 2026 had the lowest gold recovery: 67.9 %**, with a **feed grade of 6.10 g/t Au** — also the lowest feed grade of the year so far.

Monthly detail (metal-weighted recovery, running hours only):

| Month | Recovery (%) | Plain mean (%) | Feed grade (g/t) | Hours (of window) |
|---|---|---|---|---|
| Jan | 69.7 | 69.4 | 8.35 | 693 |
| Feb | 71.1 | 71.0 | 9.76 | 649 |
| Mar | 71.9 | 71.8 | 10.16 | 696 |
| Apr | 70.0 | 69.2 | 9.88 | 485 |
| May | 75.4 | 75.4 | 9.39 | 596 |
| Jun | 73.3 | 73.2 | 8.59 | 716 |
| Jul | 72.5 | 71.5 | 7.69 | 621 |
| **Aug** | **67.9** | 65.9 | **6.10** | 657 |
| Sep | 71.1 | 70.3 | 6.37 | 707 |
| Oct | 71.6 | 71.0 | 6.69 | 555 |
| Nov* | 72.8 | 72.3 | 8.61 | 487 |

\* November is partial (to 22 Nov 23:00, historian clock).

**Definition & provenance**
- Recovery = 100·c(f−t)/(f(c−t)) per the site's two-product formula, from the online analyser's Au assays: feed = `Flotation\Rougher Feed|Au` (SA-C1-AT-3069), concentrate = `Flotation\Final Concentrate|Au` (SA-C1-AT-3089), tail = `Flotation\Final Tail|Au` (SA-C1-AT-3094), all g/t, health ok.
- Running hours: SAG `Fresh Feed Rate` (SA-C1-WT-2001, t/h); hours < 50 t/h dropped (736 of 7,824 hours read).
- Screened out: 226 hours with an impossible result (recovery outside 0–100 % or tail grade ≥ concentrate grade) — analyser glitches, excluded per site practice.
- Monthly recovery is metal out over metal in: each hour weighted by feed rate × feed grade (not the mean of hourly recoveries; the plain mean is shown as a check — closest divergence is August, 67.9 vs 65.9, worth noting but not changing the ranking).
- Basis: hourly time-weighted averages, 1 h interval, window 2026-01-01 00:00 → 2026-11-22 23:00 (Australia/Brisbane).

Chart saved as `recovery_2026_monthly.png` (with `recovery_monthly_2026.csv` and `recovery_hourly_2026.csv` alongside).

One caveat: August's low recovery coincides with the year's lowest feed grade, so the two are correlated in the data — this identifies the month, not a cause.
