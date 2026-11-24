## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "feed grade gold", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__get_golden_tags` {"scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery percentage", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A", "limit": 15}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "depth": 2}
- `mcp__historian__search_tags` {"query": "rougher feed flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "final concentrate flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "final tail flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "flow"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Grinding\\SAG Mill"}
- `mcp__historian__get_tag_details` {"ids": ["192", "197", "149", "153", "169", "174", "175", "179", "181"]}
- `mcp__historian__search_tags` {"query": "slurry density", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "density"}
- `mcp__historian__get_current_values` {"ids": ["192", "197", "149", "153", "169", "174", "175", "179"]}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Grinding\\SAG Mill"}
- `mcp__historian__search_tags` {"query": "recovery", "limit": 20}
- `mcp__historian__search_tags` {"query": "cyclone overflow flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Grinding", "quantity": "flow", "limit": 15}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "169", "174", "175", "179", "192", "197"], "start": "2026-01-01", "end": "2026-11-23", "mode": "summary", "interval": "1d", "summaries": ["Average", "Count"]}
- `bash` {"command": "head -5 \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"; wc -l \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"\nrows=list(csv.Di
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"\nrows=list(csv.Di
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"\nrows=list(csv.Di
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"\nrows=list(csv.Di
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"\nrows=list(csv.Di
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections, statistics\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"\nrows
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections, statistics\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195606-04340d.csv\"\nrows
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && python3 << 'EOF'\nimport csv, collections\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf=\"articles/teaching-local-agent-site-a
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/2 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport csv, collections\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf=\"articles/teach

## Answer

**Answer: January 2026** had the lowest gold recovery at Site A, Concentrator 1 — about **62 %** — with a feed grade of about **8.2 g/t Au** (mass-weighted; 8.0 g/t time-weighted).

**How the number was derived** (the catalogue has **no recovery tag** anywhere, so it was computed from a mass balance, not read off a single tag):

Recovery = Au in final concentrate ÷ Au in SAG fresh feed, per month (Σ daily Au mass, time-weighted daily averages, 1 Jan – 22 Nov 2026, Australia/Brisbane):

| Month | Recovery (conc basis) | Cross-check (tail basis) | Feed grade (g/t Au) |
|---|---|---|---|
| **Jan** | **62.1 %** ← lowest | 94.4 % | **8.2** |
| Feb | 62.8 % | 94.6 % | 9.7 |
| Mar | 63.9 % | 94.0 % | 9.9 |
| Apr | 67.2 % | 94.9 % | 8.9 |
| May | 66.2 % | 95.2 % | 9.0 |
| Jun | 67.7 % | 95.9 % | 8.5 |
| Jul | 78.3 % | 96.6 % | 7.5 |
| Aug | 91.0 % | 95.2 % | 5.8 |
| Sep | 70.6 % | 95.9 % | 6.4 |
| Oct | 71.1 % | 96.6 % | 6.4 |
| Nov* | 69.1 % | 96.0 % | 8.2 |

\* partial month (to 22 Nov, the historian's "now").

**Provenance** — all tags healthy (`ok`), primary variants:
- Feed rate: `SAG Mill|Fresh Feed Rate` — `SA-C1-WT-2001` (t/h, golden throughput tag)
- Feed grade: `Rougher Feed|Au` — `SA-C1-AT-3069` (g/t)
- Concentrate: `Final Concentrate|Au` — `SA-C1-AT-3089` (g/t) + `Final Concentrate|Solids` — `SA-C1-AT-3093` (%) + `Final Conc Pump|Flow` — `SA-C1-FT-3110` (m³/h)
- Cross-check: `Final Tail|Au` `SA-C1-AT-3094`, `Final Tail|Solids` `SA-C1-AT-3098`, `Tail Pump|Flow` `SA-C1-FT-3115`

**Caveats:**
- Dry concentrate mass was estimated as flow × solids % × **assumed slurry density 1.3 t/m³** (no t/m³ density tag exists; only % solids). At 1.0 t/m³ the monthly values drop ~15 points but the ranking is unchanged — January is still the lowest.
- The two methods disagree (conc basis 62–91 % vs tail basis 94–97 %): dry mass of concentrate + tail (~138 t/h) is only ~26 % of the SAG feed (~537 t/h), so the flow meters don't close a mass balance. I used the standard concentrate-basis definition as primary; on the tail basis the lowest month would be March (~94 %). Worth a metering check with the plant team.

Chart saved: `site_a_c1_au_recovery_2026.png` in the current folder (monthly recovery bars both bases + feed grade line).
