## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Concentrator 1 at Site A"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate", "limit": 10}
- `mcp__historian__search_tags` {"query": "rougher gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 10}
- `mcp__historian__search_tags` {"query": "feed grade gold", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition", "limit": 10}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 10}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 10}
- `mcp__historian__get_tag_details` {"ids": ["137", "149", "154", "159"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159"], "start": "2024-04-20", "end": "*", "mode": "summary", "interval": "1d", "summaries": ["Average", "Count"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/2 && head -3 articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-194324-7d53e4.csv && python3 -c \"import pandas, matplotlib; print('ok')\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/2 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, numpy as np\ndf = pd.read_csv('articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/2
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/2 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, numpy as np\ndf = pd.read_csv('dose_recovery_daily.csv', parse_dates=['time'])\nd = df.copy()\nd['rec'] = d.c*(d.f-d.t)/(d.f*(d.c-d.t))*100\nprint('rec range:', round(d.rec.min()
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/2 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, numpy as np, matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nd = pd.read_csv('dose_recovery_daily.csv', parse_dates=['time'])\nd = d[(d.rec>0)&(d.rec<100)]\nq
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/2 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, numpy as np, matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nd = pd.read_csv('dose_recovery_daily.csv', parse_dates=['time'])\nd = d.drop(columns=[c for c in 
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/2 && head -1 dose_recovery_daily.csv && python3 -c \"\nimport pandas as pd\nd=pd.read_csv('dose_recovery_daily.csv')\nprint(list(d.columns)); print(d.dtypes)\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p1/2 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, numpy as np, matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nd = pd.read_csv('dose_recovery_daily.csv', parse_dates=['time'])\nd['rec'] = d['c']*(d['f']-d['t'

## Answer

Chart saved: `collector_dose_vs_rougher_recovery.png` (plus the daily working file `dose_recovery_daily.csv`).

## Answer

**Yes, there is a clear positive relationship, and yes, it is different across feed grades — but with an important caveat about the dose tag.**

**Overall (2024-04-20 → 2026-11-13, 861 valid days):** rougher gold recovery rises with collector dose rate — Pearson r = 0.52 (Spearman 0.44). Binned by dose: ~62–70% recovery at ≤3.4 mL/min, ~80% at 3.4–5.1, ~85% at 5.1–6.8, and ~88% at 6.8–8.5 mL/min. The low-dose end is sparse (only 30 days below 3.4 mL/min, mostly early 2024).

**By feed grade tercile (rougher feed Au, cuts at 7.0 and 9.0 g/t):**

| Grade band | n | r (dose–recovery) | Slope |
|---|---|---|---|
| Low (0.9–7.0 g/t) | 287 | **0.57** | ~+2.7 %/(mL/min) |
| Mid (7.0–9.0 g/t) | 287 | 0.30 | ~+1.4 %/(mL/min) |
| High (9.0–12.7 g/t) | 287 | 0.26 | ~+0.8 %/(mL/min) |

So the dose–recovery response is **strongest at low feed grade** and flattens at high grade, where recovery sits near 86–90% almost regardless of dose (likely near the ceiling of what the rougher can achieve). Note also that dose and grade are themselves correlated (operators tend to dose higher on higher-grade feed), so part of the overall r = 0.52 is grade-driven; the within-grade numbers are the cleaner read on the reagent effect.

**Provenance**
- **Collector dose rate:** `Site A\Concentrator 1\Flotation\Collector|Dose Rate` (SA-C1-FT-3057), mL/min. ⚠️ Catalogue health is **stale** — last record 2026-11-13, ~10 days before historian now (2026-11-23). No healthy alternative exists (only tank level and pump status tags are live for the collector), so I used its full history; the analysis window therefore ends 2026-11-13.
- **Rougher gold recovery:** no recovery tag exists in the catalogue, so I computed it daily from three healthy primary analyser tags — Rougher Feed|Au (SA-C1-AT-3069), Rougher Concentrate|Au (SA-C1-AT-3074), Rougher Tail|Au (SA-C1-AT-3079), all g/t — using the standard grade-balance formula R = c(f−t)/(f·(c−t))·100. 6 days with non-closing balances (recovery outside 0–100%) were excluded.
- **Basis:** daily time-weighted averages from `get_timeseries` (summary mode, 1d interval, Australia/Brisbane), dataset `20261123-194324-7d53e4`.
