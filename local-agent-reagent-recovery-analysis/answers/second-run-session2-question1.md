## Tool calls

- `read` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_tag_details` {"ids": ["137", "149", "154", "159", "22"]}
- `mcp__historian__search_tags` {"query": "collector dose", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "limit": 15}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00", "end": "2024-07-09T12:00", "interval": "1h", "mode": "summary", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-07-09T12:00", "end": "2024-09-27T12:00", "interval": "1h", "mode": "summary", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-09-27T12:00", "end": "2025-01-05T12:00", "interval": "1h", "mode": "summary", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-01-05T12:00", "end": "2025-03-25T12:00", "interval": "1h", "mode": "summary", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2024-09-27T12:00", "end": "2024-12-12T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2024-12-12T12:00", "end": "2025-02-26T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2025-02-26T12:00", "end": "2025-05-13T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2025-05-13T12:00", "end": "2025-07-29T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2025-07-29T12:00", "end": "2025-10-13T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2025-10-13T12:00", "end": "2026-01-28T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2026-01-28T12:00", "end": "2026-04-14T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2026-04-14T12:00", "end": "2026-07-01T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2025-10-13T12:00", "end": "2025-12-01T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2025-12-01T12:00", "end": "2026-01-28T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2026-07-01T12:00", "end": "2026-08-15T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2026-08-15T12:00", "end": "2026-10-01T12:00"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "interval": "1h", "mode": "summary", "summaries": ["Average"], "start": "2026-10-01T12:00", "end": "2026-11-23T00:00"}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2 && head -3 articles/local-agent-reagent-recovery-analysis/local/runs/kit/datasets/20261123-201838-8b8f68.csv && python3 -c \"import pandas, numpy, matplotlib; prin
- `write` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2/analysis.py", "content": "import pandas as pd\nimport numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\nimport glob, json\n\nDS = \".claude/worktrees/advisor-fable-a2dc
- `edit` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2/analysis.py", "edits": [{"oldText": "    lo = big[big[:, 1] <= q1]\n    hi = big[big[:, 1] > q2]\n    if len(lo) > 3 and len(hi) > 3:\n        sl_lo = np.polyfit(lo[:, 1], lo[:, 2], 1)[0]\n        sl_hi = np.polyfit(hi[:, 1], hi[:, 2], 1)[0]", "n
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2 && MPLCONFIGDIR=/tmp python3 analysis.py", "timeout": 300}
- `edit` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2/analysis.py", "edits": [{"oldText": "weeks = d.groupby(pd.Grouper(freq=\"7D\", origin=\"start\"))", "newText": "weeks = d.groupby(d[\"time\"].dt.floor(\"7D\"))"}]}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2 && MPLCONFIGDIR=/tmp python3 analysis.py", "timeout": 300}
- `edit` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2/analysis.py", "edits": [{"oldText": "blocks = [g.to_numpy() for _, g in weeks]", "newText": "blocks = [g[[\"dose\", \"rec\"]].to_numpy(float) for _, g in weeks]"}]}
- `edit` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2/analysis.py", "edits": [{"oldText": "    lo = big[big[:, 1] <= q1]\n    hi = big[big[:, 1] > q2]\n    if len(lo) > 3 and len(hi) > 3:\n        sl_lo = np.polyfit(lo[:, 1], lo[:, 6], 1)[0]\n        sl_hi = np.polyfit(hi[:, 1], hi[:, 6], 1)[0]", "n
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2 && MPLCONFIGDIR=/tmp python3 analysis.py", "timeout": 300}
- `bash` {"command": "ls -la articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/2/*.png"}

## Answer

**Result:** Over all the data (2024-04-20 → 2026-11-13, running hours only), higher collector dose rate is associated with higher rougher gold recovery — about **2.4 percentage points of recovery per mL/min** of collector (r = 0.33 hourly; 2.6 pp per mL/min, r = 0.40 on daily points) — but the association is weak and is largely carried by the low-to-mid dose range; in the top dose third the trend is flat, and the block-bootstrap 95 % interval on the high-minus-low slope difference (−4.2 to −0.1 pp per mL/min) does not support a positive effect at high doses.

## Definition and tags

Rougher gold recovery, per hour: 100 × c(f−t) / (f(c−t)), with all grades in g/t from:

| Tag | Point | Unit |
|---|---|---|
| `...\Flotation\Collector\|Dose Rate` | SA-C1-FT-3057 | mL/min |
| `...\Flotation\Rougher Feed\|Au` (f) | SA-C1-AT-3069 | g/t |
| `...\Flotation\Rougher Concentrate\|Au` (c) | SA-C1-AT-3074 | g/t |
| `...\Flotation\Rougher Tail\|Au` (t) | SA-C1-AT-3079 | g/t |
| `...\Grinding\SAG Mill\|Fresh Feed Rate` (running rule, weighting) | SA-C1-WT-2001 | t/h |

All primary variants, hourly time-weighted averages, window 2024-04-20 12:00 → 2026-11-23 (full historian history; the collector tag's last record is 2026-11-13 20:00, so the final 10 days have no dose data and are excluded).

## Hours

- 22,716 hours in window; 20,689 running (feed ≥ 50 t/h); 1,842 running hours screened out as analyser glitches (recovery outside 0–100 % or tail grade ≥ concentrate grade); **18,847 hours used**.
- Overall rougher recovery over the window: **85.8 %** metal-weighted (metal out / metal in, each hour weighted by feed rate × feed grade); plain mean of hourly recoveries 84.9 % (difference < 1 point).

## The relationship

- Hourly scatter (n = 18,847): slope 2.43 pp per mL/min, r = 0.33. Daily points (n = 870): slope 2.61 pp per mL/min, r = 0.40.
- **Confounding:** collector dose rate correlates moderately with throughput (r = 0.58 with fresh feed rate), so part of the apparent effect is the reagent following feed rate. On dose per tonne (mL/t, mean 0.78), the association is weaker still (r = 0.16, 6.1 pp per mL/t).
- **By dose third** (cut points 5.62 and 6.50 mL/min): low (n = 6,283) slope 2.83, r = 0.24, mean recovery 81.8 %; mid (n = 6,295) slope 2.50, r = 0.09, mean 85.4 %; high (n = 6,269) slope 0.88, r = 0.06, mean 87.4 %.
- **Is the high-dose effect real?** Block bootstrap on whole weeks (1,000 draws): 95 % CI for (high − low) slope difference is **−4.2 to −0.1 pp per mL/min** — it does not show a positive effect at high doses; the association is not demonstrated there.

This is an association, not a demonstrated effect of the reagent.

**Caveats:** the Collector|Dose Rate tag is the only variant in the catalogue (no QC/calc) and is flagged stale (no records after 2026-11-13); the last 10 days of the window are therefore excluded from the analysis.

**Chart:** `collector_vs_rougher_recovery.png` in the current folder (daily points with least-squares line and tercile boundaries). Analysis script: `analysis.py`.
