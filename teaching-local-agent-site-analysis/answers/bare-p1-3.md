## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "feed grade gold", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__get_tag_details` {"ids": ["137"]}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "depth": 2}
- `mcp__historian__search_tags` {"query": "gold recovery percent", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Collector"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Cell 1"}
- `mcp__historian__search_tags` {"query": "rougher recovery", "quantity": "composition", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "153", "154", "158", "159", "163"], "start": "2024-04-20T12:00", "end": "*", "mode": "summary", "interval": "1d", "summaries": ["Average", "Count"]}
- `bash` {"command": "head -5 articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-200236-d36ff7.csv; wc -l articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-200236-d36ff7.csv"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/3 && python3 -c \"import pandas, matplotlib, numpy; print('ok')\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/3 && cat > analyze.py <<'EOF'\nimport pandas as pd, numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf=\"articles/teaching-l
- `mcp__historian__search_tags` {"query": "recovery", "limit": 20}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/3 && cat > analyze.py <<'EOF'\nimport pandas as pd, numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf=\"articles/teaching-l
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/3 && MPLCONFIGDIR=/tmp python3 analyze.py"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/3 && sed -i 's/\"gt\"/\"gtail\"/; s/d\\.gt/d.gtail/g' analyze.py && MPLCONFIGDIR=/tmp python3 analyze.py"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/3 && cat > chart.py <<'EOF'\nimport pandas as pd, numpy as np\nimport matplotlib; matplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\nd=pd.read_csv(\"daily_recovery.csv\",parse_dates=[\"time\"]).dropna(subset=[\"dose\",\"rec\"])\nlo,hi=d.
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/3 && MPLCONFIGDIR=/tmp python3 -c \"\nimport pandas as pd,numpy as np\nd=pd.read_csv('daily_recovery.csv').dropna()\nk,b=np.polyfit(d.dose,d.rec,1); print('overall slope',round(k,3),'intercept',round(b,2))\" && ls -la collector_dose_vs_recovery

## Answer

**Answer: yes, there is a clear positive relationship, and it is strongest at low feed grade and weakest at high feed grade.**

## What I used (provenance)

| Quantity | Tag | Point | Unit | Basis |
|---|---|---|---|---|
| Collector dose rate | `...\Site A\Concentrator 1\Flotation\Collector\|Dose Rate` | SA-C1-FT-3057 | mL/min | daily time-weighted average |
| Feed grade (rougher feed Au) | `...\Flotation\Rougher Feed\|Au` | SA-C1-AT-3069 | g/t | daily time-weighted average |
| Rougher concentrate Au | `...\Flotation\Rougher Concentrate\|Au` | SA-C1-AT-3074 | g/t | daily time-weighted average |
| Rougher tail Au | `...\Flotation\Rougher Tail\|Au` | SA-C1-AT-3079 | g/t | daily time-weighted average |

- **Window:** all data the historian has — 2024-04-20 (earliest record) to 2026-11-13, 869 daily pairs.
- **Recovery:** the catalogue has **no recovery tag** (searched "recovery" plant-wide — nothing). I computed rougher gold recovery daily from the standard three-assay formula R = (Gf−Gt)/(Gc−Gt) × Gc/Gf using the three healthy primary analyser tags above. (A dry-solids mass balance was not usable: the solids tags imply the concentrate would weigh more than the feed, i.e. the circuit is water-diluted, so only the grade balance is self-consistent.) 20/889 days gave implausible recovery and were dropped.
- **Caveat:** the collector dose rate tag's health is **stale** (last record 2026-11-13, ~10 days before the historian's now of 2026-11-23). There is no healthy alternative for collector dosing, so I used its full available history and flagged the gap.

## Results

**Overall:** recovery rises with collector dose rate — correlation r = **+0.46**, linear fit ≈ **+4.1 % recovery per mL/min** (recovery averages 83.7 %; dose ranges 0–8.5 mL/min, mostly 5–7).

**By feed grade tercile (rougher feed Au):**

| Band | Feed grade | n | r (dose vs recovery) | Slope | Mean recovery |
|---|---|---|---|---|---|
| Low | ≤ 7.1 g/t | 290 | **+0.50** | **+4.6 %/(mL/min)** | 78.8 % |
| Mid | 7.1–8.9 g/t | 289 | +0.35 | +3.1 %/(mL/min) | 84.1 % |
| High | > 8.9 g/t | 290 | **+0.19** | **+1.3 %/(mL/min)** | 88.3 % |

**Interpretation:** the dose–recovery response is real but **not constant** — the benefit of adding collector is roughly **3–4× larger at low feed grade** than at high feed grade. At high grade the rougher is already recovering ~88 % and is near its ceiling, so extra collector buys little; at low grade (~5.9 g/t) recovery runs ~79 % and responds most strongly to dosing. This is consistent with over-dosing risk (reagent cost, poor selectivity) becoming the dominant trade-off as grade rises.

Chart saved: **`collector_dose_vs_recovery.png`** (scatter + fit per grade band). Working data: `daily_recovery.csv`, scripts `analyze.py` / `chart.py` in the same folder.
