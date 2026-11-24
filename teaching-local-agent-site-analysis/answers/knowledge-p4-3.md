## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-01-01", "end": "*", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["22"], "start": "2026-01-01", "end": "*", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175"], "start": "2026-01-01", "end": "*", "mode": "summary", "interval": "2h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["22"], "start": "2026-01-01", "end": "*", "mode": "summary", "interval": "2h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175"], "start": "2026-01-01", "end": "*", "mode": "summary", "interval": "4h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["22"], "start": "2026-01-01", "end": "*", "mode": "summary", "interval": "4h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/3 && python3 << 'EOF'\nimport csv, statistics\nfrom collections import defaultdict\n\ndef load(path, col):\n    rows = {}\n    with open(path) as fh:\n        for r in csv.DictReader(fh):\n            v = r.get(col, '')\n            if v n
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/3 && python3 << 'EOF'\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nrec = [69.28, 70.96, 71.45, 65.27, 74.78, 72.98, 71.54, 66.91, 71.02, 71.07, 71.72]\nfg  = [8.132, 9.788, 9.963, 8.722, 9.347, 8.564, 7.579

## Answer

**April 2026** had the lowest gold recovery so far in 2026: **65.3%**, with a feed grade of **8.7 g/t Au** that month.

## Monthly results (Jan–Nov 2026, running hours only)

| Month | Gold recovery | Feed grade (Au) |
|---|---|---|
| Jan | 69.3% | 8.13 g/t |
| Feb | 71.0% | 9.79 g/t |
| Mar | 71.5% | 9.96 g/t |
| **Apr** | **65.3%** | **8.72 g/t** |
| May | 74.8% | 9.35 g/t |
| Jun | 73.0% | 8.56 g/t |
| Jul | 71.5% | 7.58 g/t |
| Aug | 66.9% | 5.85 g/t |
| Sep | 71.0% | 6.40 g/t |
| Oct | 71.1% | 6.55 g/t |
| Nov (to 22nd) | 71.7% | 8.34 g/t |

August was a close second (66.9%) but at a much lower feed grade (5.85 g/t).

## How it was calculated

- **Tags** (all primary, healthy, Site A Concentrator 1):
  - Feed (f): `...\Flotation\Rougher Feed|Au` (SA-C1-AT-3069, g/t)
  - Concentrate (c): `...\Flotation\Final Concentrate|Au` (SA-C1-AT-3089, g/t)
  - Tail (t): `...\Flotation\Final Tail|Au` (SA-C1-AT-3094, g/t)
  - Running check: `...\Grinding\SAG Mill|Fresh Feed Rate` (SA-C1-WT-2001, t/h)
- **Window:** 1 Jan 2026 → 22 Nov 2026 (historian "now" is 23 Nov 2026), 4-hour time-weighted averages (1h/2h intervals exceeded the historian's value limit).
- **Running hours only:** rows where fresh feed rate < 50 t/h were excluded (93 of 1,890 4-hour blocks), since the analyser holds its last values while stopped.
- **Recovery:** two-product formula 100 × c(f−t) / (f(c−t)), applied to each month's time-weighted f, c, t averages; feed grade is the month's time-weighted rougher-feed Au.

Chart saved as **`recovery_2026.png`** in the current folder.
