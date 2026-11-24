## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-10-01T00:00:00+10:00", "end": "2026-10-31T23:59:59+10:00", "mode": "interpolated", "interval": "15m"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv, math\nfrom collections import defaultdict\n\npath = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv\nfrom collections import defaultdict\n\npath = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv\nfrom collections import defaultdict\npath = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/2026112
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv\nfrom collections import defaultdict\npath = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/2026112
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv\npath = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-195737-821bdb.csv\"\ndef num(s):\n 
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv\npath = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-195737-821bdb.csv\"\ndef num(s):\n 
- `bash` {"command": "head -3 \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-195737-821bdb.csv\"; ls -la \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/\" | head"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv\npath = \"articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-195737-821bdb.csv\"\ndef num(s):\n 
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p2/3 && python3 << 'EOF'\nimport csv\nfrom collections import defaultdict\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nimport matplotlib.dates as mdates\nfrom datetime import datetime\n\npath = \"~/

## Answer

**Gold recovery at Site A, Concentrator 1 in October 2026: ≈ 71.2%**

**How it was calculated**
- There is no recovery tag in the historian, so I applied the site's two-product formula to the online analyser's Au assays: `recovery = 100 × c(f−t) / (f(c−t))`.
- **Running hours only** (site convention): kept 15-minute samples where SAG fresh feed rate ≥ 50 t/h — 2,272 of 2,976 samples, 568 h of 744 (76.3% of the month).
- Running-hour averages: feed **f = 6.65 g/t**, final concentrate **c = 43.55 g/t**, final tail **t = 2.14 g/t** → **recovery = 71.3%** (mass pull 10.9%). About 291,000 t processed at an average of 513 t/h.

**Data quality notes**
- The plant was **stopped 24–28 Oct** (feed rate ≈ 0); those days are excluded, as the analyser holds its last values while stopped.
- On the **29 Oct restart**, the first 4 running hours show analyser readings near zero (c ≈ 0.01 g/t) — a startup artifact. Excluding them changes the month only from 71.29% to 71.16%, so it doesn't matter either way.
- Daily recovery ranged from 62.5% (17 Oct) to 79.8% (2 Oct); the early-month days ran on higher-grade feed (f ≈ 8–9 g/t).

**Provenance**
| Tag | Point | Unit |
|---|---|---|
| `...\Concentrator 1\Flotation\Rougher Feed\|Au` | SA-C1-AT-3069 | g/t |
| `...\Flotation\Final Concentrate\|Au` | SA-C1-AT-3089 | g/t |
| `...\Flotation\Final Tail\|Au` | SA-C1-AT-3094 | g/t |
| `...\Grinding\SAG Mill\|Fresh Feed Rate` | SA-C1-WT-2001 | t/h |

All four tags are primary and healthy. Data: 1 Oct 00:00 – 31 Oct 23:45 AEST, interpolated at the analyser's 15-minute cycle (dataset `20261123-195737-821bdb`); month figure is the two-product formula on running-hour averages, not an average of daily recoveries.

Chart saved to `gold_recovery_oct_2026.png` in the current folder (daily recovery bars, running-hours line, shutdown shaded).
