## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_tag_details` {"ids": ["137"]}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow", "limit": 15}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Collector", "depth": 1}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "*", "mode": "summary", "interval": "15m", "summaries": ["Average", "Count"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "2024-05-20T12:00:00+10:00", "mode": "summary", "interval": "15m", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "*", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "2024-05-01T12:00:00+10:00", "mode": "summary", "interval": "15m", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "2024-08-28T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "2024-06-19T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-06-19T12:00:00+10:00", "end": "2024-09-17T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-06-19T12:00:00+10:00", "end": "2024-09-02T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-09-02T12:00:00+10:00", "end": "2024-11-16T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-11-16T12:00:00+10:00", "end": "2025-01-30T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-01-30T12:00:00+10:00", "end": "2025-04-15T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-04-15T12:00:00+10:00", "end": "2025-06-29T12:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "mode": "summary", "interval": "1h", "start": "2025-06-29T12:00:00+10:00", "end": "2025-09-12T12:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "mode": "summary", "interval": "1h", "start": "2025-09-12T12:00:00+10:00", "end": "2025-11-26T12:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "mode": "summary", "interval": "1h", "start": "2025-11-26T12:00:00+10:00", "end": "2026-02-09T12:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "mode": "summary", "interval": "1h", "start": "2026-02-09T12:00:00+10:00", "end": "2026-04-25T12:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "mode": "summary", "interval": "1h", "start": "2026-04-25T12:00:00+10:00", "end": "2026-07-09T12:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "mode": "summary", "interval": "1h", "start": "2026-07-09T12:00:00+10:00", "end": "2026-09-22T12:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "mode": "summary", "interval": "1h", "start": "2026-09-22T12:00:00+10:00", "end": "*", "summaries": ["Average"]}
- `bash` {"command": "ls articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/ && head -3 articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-194119-a442c7.csv && python3 -c \"import pandas, matplotlib, 
- `write` {"path": "articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/2/analyse_collector_recovery.py", "content": "\"\"\"Collector dose rate vs rougher gold recovery, Site A Concentrator 1.\n\nData: 13 hourly time-weighted average chunks from the historian (2024-04-20 .. 2026-11-13).\nRougher recovery from the tw
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/2 && python3 analyse_collector_recovery.py"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/2 && python3 -c \"\nimport pandas as pd\nfrom scipy import stats\ndf = pd.read_csv('collector_recovery_hourly.csv')\np = stats.pearsonr(df.feed_rate_tph, df.dose_mL_min); print('feed rate vs dose rate: r=%.3f p=%.1e' % (p.statistic, p.pval
- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/2/collector_dose_vs_rougher_recovery.png"}
- `bash` {"command": "ls -la articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/2/collector_dose_vs_rougher_recovery.png"}

## Answer

## Answer

**Bottom line:** the apparent positive relationship between collector dose rate and rougher gold recovery is mostly a throughput artefact. Once the dose is normalised per tonne of ore, the relationship is essentially flat — and it stays flat in all three feed-grade bands.

### What the data shows (2024-04-20 → 2026-11-13, running hours only, n = 18,847 hourly samples)

| | Dose rate (mL/min) | Dose per tonne (mL/t) |
|---|---|---|
| **Overall** | Pearson r = **+0.33** (p < 10⁻³⁰⁰) | Pearson r = **+0.16** |
| **Low grade** (≤ 7.26 g/t Au, mean 6.16) | r = +0.32 | r = **−0.00** (p = 0.75) |
| **Mid grade** (7.26–9.19 g/t, mean 8.15) | r = +0.28 | r = +0.06 |
| **High grade** (> 9.19 g/t, mean 10.48) | r = +0.22 | r = +0.05 |

- Dose rate tracks the SAG fresh feed rate tightly (r = 0.58): the dosing pump's setpoint scales with throughput, so "dose rate" is largely a proxy for feed rate, not for metallurgical dosing.
- Recovery rises with feed grade (81.5 % → 84.4 % → 88.8 % across the terciles), so within each band the dose-rate–recovery slope is partly just grade.
- Per tonne, the plant runs ~0.70 mL/t at low grade, 0.76 mid, 0.88 high — a modest grade-driven increase — but within a band, changing the dose per tonne buys essentially no recovery: the binned means are flat (±1–2 %) in all three bands.

**So: no, the relationship is not meaningfully different at high, mid or low feed grade — in every band, recovery is insensitive to collector dose per tonne within the range the plant actually operates (roughly 0.4–1.5 mL/t).** The raw dose-rate correlation looks stronger at low grade (r ≈ +0.32) than high grade (r ≈ +0.22), but that is the throughput/grade confound, not a real dose effect.

### Provenance

- **Tags** (Site A, Concentrator 1, all primary variants):
  - Collector dose rate: `...\Flotation\Collector|Dose Rate` (SA-C1-FT-3057, mL/min) — ⚠️ health **stale** (last record 2026-11-13 20:58; no healthy alternative exists in the catalogue, so the analysis ends there, ~10 days before the historian's current time)
  - Rougher Feed Au (SA-C1-AT-3069), Rougher Concentrate Au (SA-C1-AT-3074), Rougher Tail Au (SA-C1-AT-3079), all g/t, health ok
  - SAG Mill Fresh Feed Rate (SA-C1-WT-2001, t/h, health ok, golden throughput tag)
- **Basis:** time-weighted 1-hour averages from the historian (15-min analyser cycles averaged to the hour), 2024-04-20 12:00 to 2026-11-13 20:00 AEST. Stopped periods excluded per site rule (feed rate < 50 t/h: 2,027 of 22,716 hours removed); samples with missing values or non-physical assays (c ≤ t, recovery outside 0–100 %) dropped, leaving 18,847.
- **Rougher recovery** computed per the site's two-product formula: 100·c·(f−t)/(f·(c−t)) on the rougher feed/concentrate/tail Au assays.
- **Grade bands:** terciles of running-hour feed grade (≤7.26, 7.26–9.19, >9.19 g/t Au).

### Files in the current folder

- `collector_dose_vs_rougher_recovery.png` — left: dose rate (mL/min) vs recovery, colour-coded by grade band with binned means; right: same relationship normalised to mL/t per band
- `collector_recovery_hourly.csv` — the hourly working dataset (all 5 tags + computed recovery, dose/tonne, grade band)
- `analyse_collector_recovery.py` — the analysis script
