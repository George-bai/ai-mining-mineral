## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-10-01T00:00", "end": "2026-10-31T23:59", "mode": "summary", "interval": "15m", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-10-01T00:00", "end": "2026-10-31T23:59", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/1 && python3 << 'EOF'\nimport csv, math\n\nrows=[]\nwith open('articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-193108-55b596.cs
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/1 && python3 << 'EOF'\nimport json, matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nfrom datetime import date\n\nd=json.load(open('recovery_data.json'))\ndaily=d['daily']\ndays=[date.fromisoformat(k) for k in sorted(dai
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/1 && MPLCONFIGDIR=/tmp python3 << 'EOF'\nimport json, matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nfrom datetime import date\n\nd=json.load(open('recovery_data.json'))\ndaily=d['daily']\ndays=[date.fromisoformat(k) f
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/1 && MPLCONFIGDIR=/tmp python3 << 'EOF'\nimport json, matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nfrom datetime import date\n\nd=json.load(open('recovery_data.json'))\ndaily=d['daily']\ndays=[date.fromisoformat(k) f

## Answer

**Gold recovery at Site A, Concentrator 1 in October 2026: ≈ 70.8%** (mass pull ≈ 10.5%).

**How it was calculated** — the site's two-product formula on the analyser's Au assays, running hours only:

- f (feed) = Rougher Feed Au, c (concentrate) = Final Concentrate Au, t (tail) = Final Tail Au
- recovery = 100 × c(f−t) / (f(c−t)), from the time-weighted October averages over running hours: f = 6.73, c = 45.23, t = 2.20 g/t
- Running hours: SAG **Fresh Feed Rate ≥ 50 t/h** — 544 of 744 hours ran; the plant was stopped ~Oct 24–29 (excluded, as are the analyser's held values while stopped)
- Cross-check: mean of the 544 hourly recovery values = 70.5%, consistent with the 70.8% from monthly averages

**Provenance**

| Tag | Point | Unit |
|---|---|---|
| `...\Concentrator 1\Flotation\Rougher Feed\|Au` | SA-C1-AT-3069 | g/t |
| `...\Flotation\Final Concentrate\|Au` | SA-C1-AT-3089 | g/t |
| `...\Flotation\Final Tail\|Au` | SA-C1-AT-3094 | g/t |
| `...\Grinding\SAG Mill\|Fresh Feed Rate` | SA-C1-WT-2001 | t/h |

All four healthy (primary variants). Window 2026-10-01 00:00 → 2026-10-31 23:59 (Australia/Brisbane), summary mode, 1-hour intervals, time-weighted averages (15-minute intervals were rejected by the historian as too many values, so hourly averages of the 15-minute analyser cycles were used).

**Chart:** `gold_recovery_oct_2026.png` in the current folder — daily recovery, ranging 62.5% (Oct 17) to 78.9% (Oct 3), with the mid-month shutdown shaded.
