## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__get_tag_details` {"ids": ["137", "22", "149", "154", "159"]}
- `mcp__historian__get_timeseries` {"ids": ["137"], "start": "*-14d", "end": "*", "mode": "summary", "interval": "1d", "summaries": ["Average", "Count"]}
- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-193328-e6d49f.csv"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-04-20", "end": "2024-07-10", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-07-09", "end": "2024-09-28", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-09-27", "end": "2024-12-17", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "start": "2024-12-16", "end": "2025-03-07", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2025-03-06", "end": "2025-05-26"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2025-05-25", "end": "2025-08-14"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2025-08-13", "end": "2025-11-02"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2025-11-01", "end": "2026-01-21"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2026-01-20", "end": "2026-04-11"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2026-04-10", "end": "2026-06-30"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2026-06-29", "end": "2026-09-18"}
- `mcp__historian__get_timeseries` {"ids": ["137", "22", "149", "154", "159"], "mode": "summary", "interval": "1h", "summaries": ["Average"], "start": "2026-09-17", "end": "2026-11-23"}
- `bash` {"command": "python3 -c \"import pandas, numpy, matplotlib; print('ok')\" 2>&1 | tail -1"}
- `write` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p1/1/analyze_collector_recovery.py", "content": "#!/usr/bin/env python3\n\"\"\"Collector dose rate vs rougher gold recovery, Site A Concentrator 1, all historian data.\n\nTags (hourly time-weighted averages, Australia/Brisbane):\n  137 Collector|Dose 
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/1 && python3 analyze_collector_recovery.py"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/1 && python3 - <<'EOF'\nimport glob, pandas as pd\nfiles = sorted(glob.glob(\"../datasets/20261123-1934*.csv\") + glob.glob(\"../datasets/20261123-1935*.csv\"))\ndf = pd.concat([pd.read_csv(f, parse_dates=[\"time\"]) for f in files])\ndf = df
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p1/1 && python3 - <<'EOF'\nimport glob, pandas as pd\nfiles = sorted(glob.glob(\"../../datasets/20261123-1934*.csv\") + glob.glob(\"../../datasets/20261123-1935*.csv\"))\ndf = pd.concat([pd.read_csv(f, parse_dates=[\"time\"]) for f in files])\nd
- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/p1/1/collector_vs_rougher_recovery.png"}

## Answer

**Answer — Site A, Concentrator 1, 2024-04-20 → 2026-11-13 (all data the historian has for the collector tag):**

Rougher gold recovery rises with collector dose rate — about **+70 percentage points per mL/min** overall (r = 0.33, n = 18,847 running hours) — and the slope is genuinely steeper at high feed grade: **65 pp per mL/min (low) → 74 (mid) → 82 (high)**. The high-vs-low slope difference (17.3 pp per mL/min) has a block-bootstrap 95 % CI of **[10.3, 24.9]**, which does not span zero, so the difference is shown by the data.

**Caveats**
- This is an **association, not "the effect of" the collector**: the dose rate follows throughput (corr with feed rate 0.58). On **dose per tonne** (mL/t) the overall relationship is much weaker (80 pp per mL/t but r = 0.16) — most of the raw correlation is the plant running faster with more reagent, not the reagent itself.
- The collector tag (SA-C1-FT-3057) is the **only collector dose-rate tag** and the catalogue marks it **stale**: its data ends 2026-11-13 20:00, so the last ~10 days are excluded. The nearest alternatives (Collector|Tank Level, Pump Run Status) are not dose rates, so none was usable.

**Definition & data**
- Rougher recovery (%) = 100·c(f−t)/(f(c−t)), from Rougher Feed|Au (SA-C1-AT-3069), Rougher Concentrate|Au (SA-C1-AT-3074), Rougher Tail|Au (SA-C1-AT-3079), g/t.
- Collector|Dose Rate (SA-C1-FT-3057, mL/min); SAG Mill|Fresh Feed Rate (SA-C1-WT-2001, t/h) for running hours (≥50 t/h) and dose/tonne.
- Hourly time-weighted averages, all five tags read in the same calls so rows align in time.
- Hours: 22,728 read → 20,689 running → 1,842 screened out (stopped, missing values, recovery outside 0–100 %, or tail ≥ concentrate) → 18,847 used.
- Feed-grade cut points (thirds of running hours): **7.26 / 9.19 g/t**. Per-third: low 6.16 g/t mean (R̄ 81.5 %), mid 8.15 (R̄ 84.4 %), high 10.48 (R̄ 88.8 %); slopes 65.0 / 74.0 / 82.3 pp per mL/min, r = 0.32 / 0.28 / 0.22, n ≈ 6,280 each.
- Context: overall rougher recovery over the window is 85.8 % metal-weighted (84.9 % plain mean — the 0.9-point gap is within a point, so weighting barely matters here).
- Bootstrap: 1,000 draws resampling whole weeks; CI on the high-minus-low slope difference.

**Files in the current folder**
- `collector_vs_rougher_recovery.png` — two panels: recovery vs dose rate and vs dose per tonne, points coloured by feed-grade third, fitted lines per third plus the overall line.
- `analyze_collector_recovery.py` — the full analysis script.
