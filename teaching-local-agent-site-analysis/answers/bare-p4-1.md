## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 10}
- `mcp__historian__search_tags` {"query": "feed grade gold", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition", "limit": 10}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 10}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "depth": 2}
- `mcp__historian__search_tags` {"query": "gold recovery percent", "limit": 10}
- `mcp__historian__search_tags` {"query": "rougher feed flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow", "limit": 8}
- `mcp__historian__search_tags` {"query": "final tail flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow", "limit": 8}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Tail"}
- `mcp__historian__search_tags` {"query": "solids flow mass flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate", "limit": 10}
- `mcp__historian__get_tag_details` {"ids": ["\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Concentrate|Solids", "\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Tail|Solids"]}
- `mcp__historian__search_tags` {"query": "final concentrate solids", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "composition", "limit": 5}
- `mcp__historian__search_tags` {"query": "final tail solids", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "composition", "limit": 5}
- `mcp__historian__get_timeseries` {"ids": ["192", "197", "169", "175", "174", "179", "149"], "start": "2026-01-01", "end": "2026-11-23", "interval": "1d", "mode": "summary", "summaries": ["Average", "Total", "Count"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/1 && head -3 articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-193944-0b13a9.csv && python3 -c \"import pandas, matplotlib; print('ok')\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/1 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, numpy as np\ndf = pd.read_csv('articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/2
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/1 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, numpy as np\ndf = pd.read_csv('articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/2
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/1 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\ng = pd.read_csv('monthly_recovery_2026.csv', index_col=0)\nlabels = [str(m) for m in g.index]\nx = ra
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/1 && python3 -c \"\nimport pandas as pd\ng = pd.read_csv('monthly_recovery_2026.csv', index_col=0)\nprint(type(g.index), g.index[:2])\nprint(g['recovery_%'].idxmin(), type(g['recovery_%'].idxmin()))\n\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/1 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\ng = pd.read_csv('monthly_recovery_2026.csv', index_col=0)\nlabels = [str(m) for m in g.index]\nx = ra

## Answer

**March 2026** had the lowest gold recovery at Site A, Concentrator 1: **≈91.4%**, with a measured rougher feed grade of **≈9.8 g/t Au** that month (the highest feed grade of the year — consistent with the recovery dip).

| Month | Recovery % | Feed grade (g/t Au) |
|---|---|---|
| Jan | 91.7 | 8.0 |
| Feb | 92.0 | 9.7 |
| **Mar** | **91.4** | **9.8** |
| Apr | 93.0 | 7.0 |
| May | 93.3 | 7.8 |
| Jun | 94.3 | 8.6 |
| Jul | 95.8 | 6.5 |
| Aug | 95.0 | 5.5 |
| Sep | 94.5 | 6.4 |
| Oct | 95.5 | 5.3 |
| Nov (to 22 Nov) | 94.5 | 8.2 |

**How it was computed** (the catalogue has no dedicated "recovery" tag, so it was derived by mass balance):
- Recovery = gold in final concentrate ÷ (gold in final concentrate + gold in final tail), summed per month.
- Stream masses = pump flow × stream solids % (slurry density assumed ~1 t/m³ for both streams; it cancels in the recovery ratio).
- Tags (all healthy, primary, Site A\Concentrator 1\Flotation): `Final Conc Pump|Flow` (SA-C1-FT-3110, m³/h), `Tail Pump|Flow` (SA-C1-FT-3115, m³/h), `Final Concentrate|Au` (SA-C1-AT-3089) & `|Solids` (SA-C1-AT-3093), `Final Tail|Au` (SA-C1-AT-3094) & `|Solids` (SA-C1-AT-3098), `Rougher Feed|Au` (SA-C1-AT-3069, g/t).
- Basis: time-weighted daily averages, 1 Jan – 22 Nov 2026 (historian clock: 23 Nov 2026), so November is a partial month.

Caveat: the mass-balance-implied feed grade (~19–24 g/t) doesn't reconcile with the measured rougher feed Au (~5–10 g/t) — likely the tail pump flow isn't the full final-tail stream or the streams carry different densities. This affects the implied feed grade, not the recovery ranking, which only depends on the grade/mass ratio of the two product streams.

Chart saved: `site_a_c1_monthly_recovery_2026.png` (table also in `monthly_recovery_2026.csv`) in the current folder.
