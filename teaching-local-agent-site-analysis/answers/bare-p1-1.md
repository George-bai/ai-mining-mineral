## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "feed grade gold", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 20}
- `mcp__historian__search_tags` {"query": "rougher mass flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow", "limit": 20}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "depth": 2}
- `mcp__historian__search_tags` {"query": "tail pump flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "181", "197", "153", "158", "163"], "start": "2024-04-20", "end": "2026-11-13", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `bash` {"command": "head -3 articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-192629-e555c0.csv; python3 -c \"import pandas, matplotlib, scipy; print('ok')\""}
- `write` {"path": "articles/teaching-local-agent-site-analysis/local/runs/bare/p1/1/analyse.py", "content": "import pandas as pd\nimport numpy as np\nfrom scipy import stats\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf = \".claude/worktrees/advisor-fable-a2
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/1 && MPLCONFIGDIR=/tmp python3 analyse.py"}
- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/bare/p1/1/collector_dose_vs_rougher_recovery.png"}

## Answer

## Answer

**Yes — collector dose rate is positively related to rougher gold recovery, but the relationship is much stronger at low feed grade than at mid or high grade.**

### The relationship (all data)
Over 870 usable days (2024-04-20 → 2026-11-12, daily time-weighted values):

| Feed-grade band | n | avg dose | avg recovery | Pearson r | Spearman ρ | slope |
|---|---|---|---|---|---|---|
| **All** | 870 | 5.80 mL/min | 88.8% | **0.54** | 0.41 | 2.5 pp per mL/min |
| **Low** (< 7.0 g/t Au) | 290 | 5.24 | 86.3% | **0.61** | 0.55 | 3.6 pp per mL/min |
| **Mid** (7.0–9.0 g/t) | 290 | 5.93 | 89.2% | 0.30 | 0.30 | 1.0 pp per mL/min |
| **High** (> 9.0 g/t) | 290 | 6.24 | 91.0% | 0.23 | 0.18 | 0.6 pp per mL/min |

Interpretation:
- **Low grade:** dose rate clearly drives recovery — each extra mL/min buys ~3.6 percentage points, and recovery varies most in this band.
- **Mid/high grade:** the effect flattens to ~0.6–1.0 pp per mL/min; recovery is already high (89–91%) and less sensitive to dose. The overall r = 0.54 is largely inflated by dose and grade being positively correlated (operators dose more collector on higher-grade feed), so the within-band numbers are the cleaner signal.

### Provenance
- **Collector dose rate** — `Site A\Concentrator 1\Flotation\Collector|Dose Rate` (point `SA-C1-FT-3057`, mL/min). ⚠️ This tag's health is **stale** (last record 2026-11-13; historian clock 2026-11-23). It is the only collector dose-rate tag in the catalogue — no healthy alternative exists — so the analysis covers the data that does exist, ending 2026-11-13.
- **Rougher gold recovery** — no recovery tag exists in the catalogue; computed from a daily mass balance: `recovery = 1 − (tail Au × tail mass) / (feed Au × feed mass)`, with feed mass = concentrate + tail mass (steady state), and mass flows from pump flow (m³/h) × slurry density from solids %.
  - Grades: `Rougher Feed|Au` (`SA-C1-AT-3069`), `Rougher Concentrate|Au` (`SA-C1-AT-3074`), `Rougher Tail|Au` (`SA-C1-AT-3079`), all g/t, health ok.
  - Flows: `Rougher Conc Pump|Flow` (`SA-C1-FT-3100`) and `Tail Pump|Flow` (`SA-C1-FT-3115`), m³/h, health ok.
  - Solids: `Rougher Feed|Solids` (`SA-C1-AT-3073`), `Rougher Concentrate|Solids` (`SA-C1-AT-3078`), `Rougher Tail|Solids` (`SA-C1-AT-3083`), %, health ok.
- **Basis:** summary mode, 1-day interval, time-weighted averages; units as recorded (no conversion needed). 937 days returned, 870 retained after dropping incomplete days, shutdown days (zero flow/grade/dose) and implausible recoveries (>120% or <0%).
- **Feed grade** = rougher feed Au grade; bands are daily tertiles (< 7.01 / 7.01–8.97 / > 8.97 g/t).

### Files
- Chart: `collector_dose_vs_rougher_recovery.png` (scatter by grade band with per-band fits and overall fit)
- Script: `analyse.py`
- Raw dataset: `runs/bare/datasets/20261123-192629-e555c0.csv`
