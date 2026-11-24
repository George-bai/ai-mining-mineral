## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__get_tag_details` {"ids": ["137"]}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "limit": 15}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-04-20T12:00", "end": "2024-07-09T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-07-09T12:00", "end": "2024-09-27T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-09-27T12:00", "end": "2024-12-15T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-12-15T12:00", "end": "2025-03-05T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2025-03-05T12:00", "end": "2025-05-24T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2025-05-24T12:00", "end": "2025-08-09T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2025-08-09T12:00", "end": "2025-10-27T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2025-10-27T12:00", "end": "2026-01-14T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2026-01-14T12:00", "end": "2026-04-04T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2026-04-04T12:00", "end": "2026-06-23T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2026-06-23T12:00", "end": "2026-09-08T12:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2026-09-08T12:00", "end": "*", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "head -3 articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-195745-a8e430.csv; python3 -c \"import pandas, numpy, matplotlib; print('ok')\""}
- `write` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3/analysis.py", "content": "import glob, os\nimport numpy as np\nimport pandas as pd\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nfiles = sorted(glob.glob(\".claude/worktrees/
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3 && python3 analysis.py"}
- `edit` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3/analysis.py", "edits": [{"oldText": "20261123-1958*.csv", "newText": "20261123-195*.csv"}, {"oldText": "d.R = np.where(den > 0, 100 * d.c * (d.f - d.t) / den, np.nan)\n# screen impossible results\nbad = (d.R < 0) | (d.R > 100) | (d.t >= d.c) | (d
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3 && python3 analysis.py"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3 && python3 - <<'EOF'\nimport glob\nimport numpy as np, pandas as pd\nfiles = sorted(glob.glob(\"articles/teaching-local-agent-site-analysis/local/runs/skills/datas
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3 && python3 - <<'EOF'\nimport glob\nimport pandas as pd\nfiles = sorted(glob.glob(\"articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3 && sed -i 's/d\\.R = /d[\"R\"] = /; s/d\\.dose_t = /d[\"dose_t\"] = /; s/d\\.R\\b/d[\"R\"]/g; s/d\\.dose_t\\b/d[\"dose_t\"]/g; s/d\\.R\\b/d[\"R\"]/g' analysis.py && grep -n 'd\\[\"R\"\\]\\|d\\[\"dose_t\"\\]' analysis.py | head -30"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3 && python3 analysis.py 2>&1 | grep -v matplotlib"}
- `edit` {"edits": [{"newText": "d[\"week\"] = ((d.time - d.time.min()).dt.days // 7).astype(\"int64\")", "oldText": "d[\"week\"] = (d.time.dt.floor(\"W\") // pd.Timedelta(days=7)).astype(\"int64\")"}], "path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3/analysis.py"}
- `edit` {"edits": [{"newText": "ax.set_title(f\"Rougher Au recovery vs collector dose rate\\ncollector data {d.time.min().date()} - {d.time.max().date()} (tag has no data Jan-Nov 2026), n = {n} running hours\")", "oldText": "ax.set_title(f\"Rougher Au recovery vs collector dose rate\\nall data {d.time.min().date()} - {d.time.max().date()}, n = {n} running hours\")"}], "path": "~/git/ai-minin
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3 && python3 analysis.py 2>&1 | grep -v -i matplotlib"}
- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p1/3/collector_vs_rougher_recovery.png"}

## Answer

Chart saved. Here's the full answer:

## Relationship: collector dose vs rougher gold recovery

**Over all usable data (20 Apr 2024 – 31 Dec 2025), rougher gold recovery rises with collector dose, but weakly: about +1.5 percentage points per mL/min (r = 0.20), or +9.0 pp per mL/t of ore (r = 0.26) on a dose-per-tonne basis — and it is clearly different by feed grade: the response is essentially flat at low grade and positive at mid and high grade.**

### By feed grade (thirds at 7.27 / 9.02 g/t, dose per tonne)

| Feed grade | n (hours) | Slope (pp per mL/t) | r |
|---|---|---|---|
| Low (< 7.27 g/t) | 4,212 | **−2.1** (flat) | −0.04 |
| Mid (7.27–9.02 g/t) | 4,211 | **+3.7** | 0.11 |
| High (> 9.02 g/t) | 4,212 | **+4.6** | 0.23 |

Block bootstrap (1,000 draws of whole weeks) on the low-minus-high slope difference: **−6.8 pp/(mL/t), 95 % CI [−12.4, −1.0]** — it does not span zero, so the difference between low and high grade is shown by the data.

### Definition and tags
- **Rougher recovery (hourly)** = 100 × c(f−t) / f(c−t), with f = Rougher Feed Au (`...\Flotation\Rougher Feed|Au`, SA-C1-AT-3069), c = Rougher Concentrate Au (SA-C1-AT-3074), t = Rougher Tail Au (SA-C1-AT-3079), all g/t.
- **Collector dose rate** = `...\Flotation\Collector|Dose Rate` (SA-C1-FT-3057, mL/min); **dose per tonne** = dose rate ÷ SAG Fresh Feed Rate (SA-C1-WT-2001, t/h) × 60, in mL/t.
- Overall rougher recovery in the window: **83.3 %** metal-weighted (Σ q·f·R / Σ q·f) vs 82.7 % plain mean of screened hours (< 1 pt apart).

### Hours and screening
- Window: 2024-04-20T12:00 → 2026-11-23 (all historian data), hourly time-weighted averages, 22,716 hours read.
- 20,689 running hours (feed ≥ 50 t/h); 498 hours screened out (recovery outside 0–100 % or tail grade ≥ concentrate grade); **12,635 usable hours**.

### Caveats
- **The collector tag has no data from 1 Jan 2026 to 13 Nov 2026** (health "stale"; last value 31 Dec 2025, single record 13 Nov 2026), so "all the data" for this relationship actually covers Apr 2024 – Dec 2025 only. 7,094 running hours were dropped for missing collector values.
- The pump flow follows throughput (corr with feed rate = 0.49), so the raw mL/min relationship is partly a throughput effect; I report the **dose-per-tonne** form as the primary one.
- This is an **association**, not "the effect of" the collector — other variables (grade itself, grind, frother) move with it.

Chart: `collector_vs_rougher_recovery.png` in the current folder (scatter vs raw dose, vs dose/tonne, by grade third, and the time series showing the 2026 collector gap). Analysis script: `analysis.py`.
