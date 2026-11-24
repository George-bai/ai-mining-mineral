## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "175"], "start": "2026-10-01T00:00", "end": "2026-11-01T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p2/1 && python3 - <<'EOF'\nimport csv, math\n\nrows=[]\nwith open('articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-193929-4b9072.csv') a
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p2/1 && python3 - <<'EOF'\nimport csv\nfrom datetime import datetime\nrows=[]\nwith open('articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/2026112
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p2/1 && python3 - <<'EOF'\nimport csv\nfrom datetime import datetime\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nimport matplotlib.dates as mdates\n\nrows=[]\nwith open('.clau

## Answer

**Gold recovery at Site A, Concentrator 1 in October 2026 was 71.3 %** (metal-weighted, running hours only, 1 Oct 00:00 – 31 Oct 23:00 AEST).

**How it was calculated**
- Definition (site's reported recovery): two-product formula on Au assays, recovery = 100 × c(f−t) / (f(c−t)), with f = Rougher Feed Au, c = Final Concentrate Au, t = Final Tail Au. Period recovery = metal out over metal in: each hour weighted by feed rate × feed grade (q·f).
- Tags (all primary, healthy):
  - `...\Grinding\SAG Mill|Fresh Feed Rate` (SA-C1-WT-2001, t/h) — also the running/stopped rule
  - `...\Flotation\Rougher Feed|Au` (SA-C1-AT-3069, g/t)
  - `...\Flotation\Final Concentrate|Au` (SA-C1-AT-3089, g/t)
  - `...\Flotation\Final Tail|Au` (SA-C1-AT-3094, g/t)
- Basis: hourly time-weighted averages from the historian (summary mode, 1 h interval).

**Hours**
- 744 hours in the window; 76 had no feed-rate value (scattered gaps, e.g. 2 Oct and 29 Oct) and were excluded.
- 100 hours stopped (feed rate < 50 t/h) — excluded per site practice.
- 24 running hours screened out as analyser glitches (recovery outside 0–100 % or tail grade ≥ concentrate grade).
- 544 hours used.

**Check:** the plain mean of the screened hourly recoveries is 70.4 %, within 1 point of the weighted 71.3 %, so the result is consistent.

**Caveat:** the 76 hours with a missing feed-rate tag (including ~24 h around 29 Oct) are excluded from both numerator and denominator; if those hours were representative, the month's number is unaffected in bias.

Chart saved: `gold_recovery_oct2026.png` (hourly recovery with the monthly weighted line).
