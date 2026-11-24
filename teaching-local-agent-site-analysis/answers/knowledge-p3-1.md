## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__get_golden_tags` {"scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "kpi": "throughput"}
- `mcp__historian__get_timeseries` {"ids": ["149", "154", "159", "SA-C1-WT-2001"], "start": "*-7d", "end": "*", "mode": "interpolated", "interval": "15m"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets && head -3 20261123-193315-1a9a24.csv && python3 -c \"import pandas, matplotlib; print('ok')\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets && python3 << 'EOF'\nimport pandas as pd, numpy as np\ndf = pd.read_csv('20261123-193315-1a9a24.csv', parse_dates=['time'])\nf, c, t, rate = df['149|Value'], df['154|Value'], df['159|Value'], df['22|Value']\nrun = rate >= 50\ndf['mas
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets && python3 << 'EOF'\nimport pandas as pd, numpy as np\ndf = pd.read_csv('20261123-193315-1a9a24.csv', parse_dates=['time'])\nf, c, t, rate = df['149|Value'], df['154|Value'], df['159|Value'], df['22|Value']\ndf['mass_pull'] = 100*(f-
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets && MPLCONFIGDIR=/tmp MPLBACKEND=Agg python3 << 'EOF'\nimport pandas as pd, numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\ndf = pd.read_csv('20261123-193315-1a9a24.csv', parse_dates=['time'])

## Answer

## Rougher mass pull, last week (16–22 Nov 2026): **≈ 34.3%**

Computed per 15-minute analyser cycle as **100 × (f − t) / (c − t)** from the Au assays, then averaged over the week.

**Tags used** (all primary, health ok, `...\Site A\Concentrator 1\Flotation\`):

| Stream | Point | Role |
|---|---|---|
| Rougher Feed \| Au (g/t) | SA-C1-AT-3069 | f |
| Rougher Concentrate \| Au (g/t) | SA-C1-AT-3074 | c |
| Rougher Tail \| Au (g/t) | SA-C1-AT-3079 | t |
| Grinding\SAG Mill \| Fresh Feed Rate (t/h) | SA-C1-WT-2001 | running-hours check |

**Basis:** interpolated 15-minute values, 16 Nov 00:00 – 22 Nov 23:45 (site time, Australia/Brisbane; "last week" relative to the historian clock at 23 Nov 00:00). 672 samples, all running — fresh feed rate never dropped below 310 t/h, so no stopped periods to exclude.

**Caveat:** 12 samples on 16 Nov, 07:00–09:45, had the rougher concentrate Au reading ~0.01 g/t (normally ~18 g/t) — a concentrate analyser fault making mass pull non-computable there. Those samples were excluded (660 valid).

Daily averages: 16 Nov 53.9% (high feed grade ~10.5 g/t that morning), 17 Nov 46.4%, 18 Nov 37.8%, 19 Nov 34.8%, 20 Nov 19.1%, 21 Nov 25.4%, 22 Nov 25.3%.

Chart saved to `rougher_mass_pull_week.png` in the current folder.
