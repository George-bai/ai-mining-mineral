## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "Rougher Feed Au assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "Final Concentrate Au assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "Final Tail Au assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-10-01", "end": "2026-10-31", "mode": "summary", "interval": "1h", "summaries": ["Average", "Total"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/2 && python3 - <<'EOF'\nimport csv, math\n\nrows = list(csv.DictReader(open('articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-19
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/2 && python3 - <<'EOF'\nimport csv, math\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nimport matplotlib.dates as mdates\nfrom datetime import datetime\n\nrows = list(csv.DictReader(open('~/git/a
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/2 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport csv\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nimport matplotlib.dates as mdates\nfrom datetime import datetime\n\nrows = list(csv.DictReader(open('/home

## Answer

## Gold recovery, Site A Concentrator 1 — October 2026: **70.6%**

**How it was calculated** (the site's method — running hours only, two-product formula on the analyser's Au assays):

| Stream | Tag (point) | Mass-weighted Au |
|---|---|---|
| Feed (f) | `...\Flotation\Rougher Feed\|Au` (SA-C1-AT-3069) | 6.54 g/t |
| Concentrate (c) | `...\Flotation\Final Concentrate\|Au` (SA-C1-AT-3089) | 44.58 g/t |
| Tail (t) | `...\Flotation\Final Tail\|Au` (SA-C1-AT-3094) | 2.14 g/t |

- **Recovery** = 100 × c(f−t) / f(c−t) = **70.6%**; mass pull = 10.4% of feed to concentrate.
- Running hours only: 532 of 720 hourly intervals in October had the SAG **Fresh Feed Rate** (SA-C1-WT-2001) ≥ 50 t/h; the 99 stopped intervals were excluded (≈11,400 t processed while running).
- Grades are mass-weighted (each hour's assay weighted by that hour's feed tonnage), so a high-grade running day counts for more.

**Provenance**
- Tags: the three Au assays above plus `...\Grinding\SAG Mill\|Fresh Feed Rate` (SA-C1-WT-2001, t/h) — all primary, health `ok`.
- Window: 2026-10-01 to 2026-10-30 23:00 AEST (last complete hour available; historian's "now" is 23 Nov 2026).
- Basis: time-weighted 1-hour summaries from the historian (dataset `20261123-194609-8f5f72`), recovery computed per hour then aggregated on tonnage.

**Chart:** saved as `gold_recovery_oct_2026.png` in the current folder — hourly recovery (top) with the monthly 70.6% line, and fresh feed rate with the 50 t/h stop threshold (bottom).
