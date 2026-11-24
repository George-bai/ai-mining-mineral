## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed Au assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate Au assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail Au assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_timeseries` {"ids": ["149", "154", "159", "22"], "start": "*-7d", "end": "*", "mode": "interpolated", "interval": "15m"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p3/2 && python3 - <<'EOF'\nimport csv, math\nrows=[]\nwith open('articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-194739-b29d89.csv
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p3/2 && python3 - <<'EOF'\nimport csv, statistics\nrows=[]\nwith open('articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-194739-b29d
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p3/2 && python3 - <<'EOF'\nimport csv\nrows=[]\nwith open('articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-194739-b29d89.csv') as 
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p3/2 && python3 - <<'EOF'\nimport csv, statistics\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nimport matplotlib.dates as mdates\nfrom datetime import datetime\nfrom collections import defaultdict\n\nrows=[]\nwi

## Answer

**Rougher mass pull, Site A Concentrator 1, 16–23 Nov 2026 (last 7 days): ≈ 33 % average** (median 31.7 %, 653 valid 15-minute samples).

It wasn't flat: it ran **43–46 % on 16–17 Nov**, then fell to **~19–25 % from 20 Nov onward** — driven by the rougher feed grade dropping from ~7 g/t Au to ~2 g/t Au (tail Au fell with it, concentrate held ~20 g/t), so a much smaller share of the feed reported to the rougher concentrate.

**Basis & exclusions**
- Running hours only: the mill never stopped in the window (SAG fresh feed rate min 310 t/h, always ≥ 50 t/h), so all 673 samples were in scope.
- Excluded 20 samples on 16 Nov 05:00–09:45 where the assays were physically impossible (concentrate grade below feed, then ~0 g/t — mass pull >100 % or undefined). These look like a bad analyser window, not plant behaviour.
- Mass pull = 100 × (f − t)/(c − t) per 15-min cycle, then averaged.

**Provenance**
| Quantity | Tag (point) | Unit |
|---|---|---|
| Feed Au (f) | `...\Site A\Concentrator 1\Flotation\Rougher Feed\|Au` (SA-C1-AT-3069) | g/t |
| Concentrate Au (c) | `...\Flotation\Rougher Concentrate\|Au` (SA-C1-AT-3074) | g/t |
| Tail Au (t) | `...\Flotation\Rougher Tail\|Au` (SA-C1-AT-3079) | g/t |
| Run filter | `...\Grinding\SAG Mill\|Fresh Feed Rate` (SA-C1-WT-2001) | t/h |

Window 2026-11-16 00:00 → 2026-11-23 00:00 (Australia/Brisbane), interpolated at 15 min (the analyser's native cycle). Chart saved as `rougher_mass_pull_last_week.png` in the current folder.
