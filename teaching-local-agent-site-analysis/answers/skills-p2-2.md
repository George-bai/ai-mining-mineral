## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-10-01T00:00", "end": "2026-10-31T23:59", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p2/2 && python3 - <<'EOF'\nimport pandas as pd, numpy as np, matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf = \"articles/teaching-local-agent

## Answer

**Gold recovery at Site A, Concentrator 1 in October 2026 was 71.3 %** (metal-weighted, running hours only).

**How it was calculated**
- **Definition** (per site practice): R = 100 × c(f − t) / (f(c − t)), using the online Au assays — f = Rougher Feed, c = Final Concentrate, t = Final Tail.
- **Tags** (all primary, healthy):
  - `...\Grinding\SAG Mill|Fresh Feed Rate` (SA-C1-WT-2001, t/h) — running-hours gate
  - `...\Flotation\Rougher Feed|Au` (SA-C1-AT-3069, g/t)
  - `...\Flotation\Final Concentrate|Au` (SA-C1-AT-3089, g/t)
  - `...\Flotation\Final Tail|Au` (SA-C1-AT-3094, g/t)
- **Window:** 1 Oct – 31 Oct 2026 (previous calendar month on the historian's clock, now = 23 Nov 2026), hourly time-weighted averages, 744 hours read.
- **Cleaning:** 568 of 744 hours were running (fresh feed rate ≥ 50 t/h; 176 stopped hours dropped). Of the running hours, 24 were screened out as analyser glitches (recovery outside 0–100 % or tail grade ≥ concentrate grade), leaving 544 usable hours.
- **Weighting:** each hour's recovery weighted by gold in the feed (feed rate × feed grade) → **71.26 %**. The plain mean of the 544 hourly recoveries is 70.43 % — about 0.8 points lower, so the weighting matters slightly but both agree on ~71 %.
- ~291,000 t of fresh feed over the month.

Chart saved to `gold_recovery_oct2026.png` in the current folder (hourly recovery with the monthly weighted line).
