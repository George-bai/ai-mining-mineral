## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__get_golden_tags` {"scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "kpi": "throughput"}
- `mcp__historian__search_tags` {"query": "Rougher Feed Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "Rougher Concentrate Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "Rougher Tail Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__get_timeseries` {"ids": ["149", "154", "159", "SA-C1-WT-2001"], "start": "2026-11-16T00:00:00+10:00", "end": "2026-11-23T00:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "python3 - <<'EOF'\nimport csv, math\n\nrows=[]\nwith open(\"articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-200422-eff664.csv\") as f:\n    for r in csv.DictReader(f):\n        rows.append(r)\nprint(\"columns:\", list(rows[0].keys()))\nEOF"}
- `bash` {"command": "python3 - <<'EOF'\nimport csv\n\nrows=[]\nwith open(\"articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-200422-eff664.csv\") as f:\n    for r in csv.DictReader(f):\n        f_=float(r['149|Average']); c=float(r['154|Average']); t=float(r['159|Average']); q=float(r['22|Average'])\
- `bash` {"command": "python3 - <<'EOF'\nimport csv, datetime\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\ntimes=[]; mp=[]\nwith open(\"rougher_mass_pull_clean.csv\") as f:\n    for r in csv.DictReader(f):\n        times.append(datetime.datetime.fromisoformat(r[\"time\"]))\n        mp.append(float(r[\"mp\"]))\n\nfig,ax=plt.subplots(figsize=(11,4.5))\nax.plot(times,mp,\".\
- `bash` {"command": "ls -la rougher_mass_pull_last_week.png"}

## Answer

**The rougher mass pull at Site A, Concentrator 1 last week was 33.2 %** (feed-tonne weighted, 16–23 Nov 2026, AEST).

**Definition & tags** (per site plant knowledge): mass pull = 100 × (f − t)/(c − t), computed per hour from the online analyser's Au assays, then the week's value weighted by feed tonnes:
- `...\Flotation\Rougher Feed|Au` (SA-C1-AT-3069), g/t
- `...\Flotation\Rougher Concentrate|Au` (SA-C1-AT-3074), g/t
- `...\Flotation\Rougher Tail|Au` (SA-C1-AT-3079), g/t
- `...\Grinding\SAG Mill|Fresh Feed Rate` (SA-C1-WT-2001), t/h — for running-hours and weighting

**Window & basis:** 2026-11-16 00:00 → 2026-11-23 00:00 (the seven days before the historian's clock), hourly time-weighted averages (168 hours read).

**Data quality:**
- Stopped hours (feed rate < 50 t/h): **0** — the plant ran all week (feed 471–634 t/h, ~91,300 t total).
- Screened out as analyser glitches (tail grade ≥ concentrate grade or mass pull outside 0–100 %): **5 hours**; 163 hours used.
- Check: plain mean of the 163 hours is 32.8 %, within 0.3 points of the weighted value, so the weighting makes little difference this week.

Chart saved as `rougher_mass_pull_last_week.png` in the current folder (hourly mass pull with the 33.2 % week value marked).
