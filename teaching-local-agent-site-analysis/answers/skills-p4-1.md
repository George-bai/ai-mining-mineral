## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-01-01", "end": "2026-03-01", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-03-01", "end": "2026-04-30", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-04-30", "end": "2026-06-29", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-06-29", "end": "2026-08-28", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-08-28", "end": "2026-10-27", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-10-27", "end": "2026-11-23", "mode": "summary", "interval": "1h"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/1 && python3 -c \"import pandas, matplotlib; print('ok')\""}
- `write` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p4/1/analyze.py", "content": "import os\nimport pandas as pd\nimport numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nos.environ.setdefault(\"MPLCONFIGDIR\", \"/tmp/mpl\")\n\nfiles = [\n    \"20261123-194310-
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/datasets && head -2 20261123-194310-c47fb7.csv"}
- `edit` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p4/1/analyze.py", "edits": [{"oldText": "df.columns = [\"time\", \"feed_rate\", \"f_au\", \"c_au\", \"t_au\"]", "newText": "df.columns = [\"time\", \"f_au\", \"c_au\", \"t_au\", \"feed_rate\"]"}]}
- `edit` {"edits": [{"newText": "df.columns = [\"time\", \"f_au\", \"c_au\", \"t_au\", \"feed_rate\"]\ntotal_hours = len(df)\n\n# Hours with a missing value in any of the four tags\nmissing = int(df[[\"f_au\", \"c_au\", \"t_au\", \"feed_rate\"]].isna().any(axis=1).sum())\ndf = df.dropna(subset=[\"f_au\", \"c_au\", \"t_au\", \"feed_rate\"])", "oldText": "df.columns = [\"time\", \"f_au\", \"c_au\", \"t_au\",
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/1 && MPLCONFIGDIR=/tmp/mpl python3 analyze.py"}
- `bash` {"command": "ls -la articles/teaching-local-agent-site-analysis/local/runs/skills/p4/1/*.png"}

## Answer

**August 2026 had the lowest gold recovery at Site A, Concentrator 1: 68.2 %**, with a feed grade of **6.10 g/t Au** that month.

Chart saved: `recovery_2026_ytd.png` (in the current folder).

**How it was calculated**
- **Definition** (site's own, from plant knowledge): gold recovery = 100·c(f−t)/(f(c−t)), where f = Rougher Feed Au, c = Final Concentrate Au, t = Final Tail Au. Monthly recovery = metal out over metal in (each hour weighted by feed metal, q·f), not the mean of hourly recoveries. Feed grade weighted by feed tonnes.
- **Tags** (all healthy, primary variants, scope `\\EXAMPLE-AF\Operations\Example Mining\Site A\Concentrator 1`):
  - `Grinding\SAG Mill|Fresh Feed Rate` (SA-C1-WT-2001, t/h)
  - `Flotation\Rougher Feed|Au` (SA-C1-AT-3069, g/t)
  - `Flotation\Final Concentrate|Au` (SA-C1-AT-3089, g/t)
  - `Flotation\Final Tail|Au` (SA-C1-AT-3094, g/t)
- **Window**: 2026-01-01 00:00 → 2026-11-22 23:00 (AEST; historian "now" is 2026-11-23 00:00, so November is partial, 1–23 Nov). Hourly time-weighted averages.
- **Hours**: 7,824 read; 407 dropped for a missing value in one of the four tags; 332 stopped (feed rate < 50 t/h, excluded per site practice); 226 screened as impossible (recovery outside 0–100 % or tail grade ≥ concentrate grade); 6,859 running, valid hours used (August: 654).
- **Check**: the plain mean of August's hourly recoveries is 65.9 %, about 2.2 points below the metal-weighted 68.2 % — the weighted figure is the site's basis, but the gap means August's low-recovery hours also carried higher feed metal.

Monthly results (recovery % / feed grade g/t): Jan 69.7/8.35, Feb 71.1/9.76, Mar 71.9/10.16, Apr 70.0/9.88, May 75.4/9.39, Jun 73.3/8.59, Jul 72.5/7.69, **Aug 68.2/6.10**, Sep 71.1/6.38, Oct 71.5/6.69, Nov 72.8/8.61. August's dip coincides with the year's lowest feed grade — worth noting as an association; low-grade feed often recovers differently, but this data alone doesn't establish a cause.
