## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "Rougher Feed Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "Final Concentrate Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "Final Tail Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG Mill Fresh Feed Rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-01-01", "end": "2026-11-23", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"end": "2026-11-23", "interval": "1d", "ids": ["149", "169", "175", "22"], "mode": "summary", "start": "2026-01-01", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/1 && python3 - <<'EOF'\nimport csv, datetime, math\n\nf = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-193604-686536.csv\"
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/1 && python3 - <<'EOF'\nimport csv, datetime\n\nf = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-193604-686536.csv\"\nrows
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/1 && python3 - <<'EOF'\nimport csv, datetime\n\nf = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-193604-686536.csv\"\nrows
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/1 && python3 - <<'EOF'\nimport json\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\ndata = json.load(open(\"monthly_recovery_2026.json\"))\nmonths = [d[\"month\"] for d in data]\nrec = [d[\"recovery\"] for d

## Answer

**April 2026 had the lowest gold recovery: 64.8%, with a feed grade of 8.44 g/t Au.**

Monthly results (Jan–Nov 2026, running hours only — days with SAG fresh feed rate < 50 t/h excluded, 20 such days dropped):

| Month | Feed Au (g/t) | Conc Au (g/t) | Tail Au (g/t) | Recovery |
|---|---|---|---|---|
| Jan | 8.01 | 41.92 | 2.84 | 69.2% |
| Feb | 9.70 | 43.38 | 3.35 | 71.0% |
| Mar | 9.77 | 41.34 | 3.38 | 71.3% |
| **Apr** | **8.44** | **39.16** | **3.45** | **64.8%** |
| May | 8.98 | 42.26 | 2.71 | 74.6% |
| Jun | 8.56 | 44.33 | 2.69 | 73.0% |
| Jul | 7.49 | 43.50 | 2.44 | 71.5% |
| Aug | 5.81 | 44.07 | 2.13 | 66.6% |
| Sep | 6.40 | 43.78 | 2.07 | 71.0% |
| Oct | 6.18 | 40.55 | 1.97 | 71.6% |
| Nov* | 8.15 | 41.73 | 2.68 | 71.7% |

*Nov is partial (to 22 Nov, historian's current time 23 Nov 2026).

April's low came from both a weaker concentrate grade (39.2 g/t, lowest of the year) and the highest tail grade (3.45 g/t) — only 25 of 30 April days were running.

**Provenance**
- Tags (all healthy, primary): `Flotation\Rougher Feed|Au` (SA-C1-AT-3069), `Flotation\Final Concentrate|Au` (SA-C1-AT-3089), `Flotation\Final Tail|Au` (SA-C1-AT-3094), `Grinding\SAG Mill|Fresh Feed Rate` (SA-C1-WT-2001), all under `\\EXAMPLE-AF\Operations\Example Mining\Site A\Concentrator 1`.
- Basis: time-weighted daily averages (2026-01-01 → 2026-11-22, Australia/Brisbane), monthly averages of running days, recovery from the two-product formula 100·c(f−t)/(f(c−t)) with f/c/t = rougher feed / final concentrate / final tail Au.
- Chart: `site_a_c1_monthly_recovery_2026.png` in the current folder.
