## Tool calls

- `read` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T00:00", "end": "2024-07-09T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-07-09T00:00", "end": "2024-09-27T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-09-27T00:00", "end": "2024-12-16T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-12-16T00:00", "end": "2025-03-06T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-03-06T00:00", "end": "2025-05-25T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-05-25T00:00", "end": "2025-08-13T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-08-13T00:00", "end": "2025-11-01T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-11-01T00:00", "end": "2026-01-20T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-01-20T00:00", "end": "2026-04-10T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-04-10T00:00", "end": "2026-06-29T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-06-29T00:00", "end": "2026-09-17T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-09-17T00:00", "end": "2026-11-23T00:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/3 && python3 -c \"import pandas, numpy, matplotlib; print('ok')\" && ls articles/local-agent-reagent-recovery-analysis/local/runs/kit/datasets/ | head"}
- `write` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/3/analyze.py", "content": "import os\nimport numpy as np\nimport pandas as pd\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nos.environ.setdefault(\"MPLCONFIGDIR\", \"/tmp/mpl\")\n\nDS = \"~/git/ai-min
- `edit` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/3/analyze.py", "edits": [{"oldText": "thirds = []\nfor lo, hi, lab in [(0, cuts[0], \"low\"), (cuts[0], cuts[1], \"mid\"), (cuts[1], 1e9, \"high\")]:\n    m = (s[F] > lo) & (s[F] <= hi) if lab != \"low\" else (s[F] <= cuts[0])\n    m = (s[F] > lo) 
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 analyze.py"}
- `read` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/3/collector_vs_rougher_recovery.png"}

## Answer

**Bottom line:** over all the historian's data (2024‑04‑20 → 2026‑11‑13), collector dose rate shows only a weak association with rougher gold recovery. In the raw flow form the fit is +2.43 percentage points per mL/min (r = 0.33), but that is largely an artifact of throughput: the collector pump flow tracks the SAG fresh feed rate (r = 0.58). On **dose per tonne** (mL/t) — the form that removes throughput — the association is much weaker: +0.37 percentage points per mL/t, r = 0.16. Split by feed grade, the slopes are near zero in every third (low −0.01, mid +0.13, high +0.06 pp per mL/t); the difference between the low- and high-grade thirds is not statistically real (block-bootstrap 95 % interval −0.37 to +0.28, spans zero). In short: at this site, within the observed range (roughly 0–10 mL/min, 0–70 mL/t), collector dose rate does not show a meaningful relationship with rougher gold recovery.

**Definition and tags**
- Rougher recovery (%) = 100·c·(f−t)/(f·(c−t)), computed hourly from:
  - f: `...\Flotation\Rougher Feed|Au` (SA‑C1‑AT‑3069, g/t)
  - c: `...\Flotation\Rougher Concentrate|Au` (SA‑C1‑AT‑3074, g/t)
  - t: `...\Flotation\Rougher Tail|Au` (SA‑C1‑AT‑3079, g/t)
- Collector: `...\Flotation\Collector|Dose Rate` (SA‑C1‑FT‑3057, mL/min)
- Throughput: `...\Grinding\SAG Mill|Fresh Feed Rate` (SA‑C1‑WT‑2001, t/h)

**Data handling**
- Window: 2024‑04‑20 12:00 to 2026‑11‑22 (historian's full range), hourly time‑weighted averages, 22 728 hours read.
- 3 009 hours missing at least one tag (mostly the collector tag, which has gaps) → dropped.
- Running hours only (feed ≥ 50 t/h): 19 597 hours; 750 hours screened out as impossible (recovery outside 0–100 % or tail ≥ concentrate); **18 847 hours used**.
- Whole-period rougher recovery (metal‑in‑weighted): **85.8 %**; plain mean of screened hours 84.9 % (within a point, so no weighting surprise).

**Caveats**
- This is an association, not an effect: dose rate is set by operators in response to grade, throughput and other conditions.
- The collector tag is flagged `stale` (last value 2026‑11‑13), so the last ~10 days are excluded; it is the only collector tag in the catalogue, so it was used for the full history.
- Chart saved to `collector_vs_rougher_recovery.png` in this folder (left: recovery vs dose rate in mL/min; right: recovery vs dose per tonne by feed‑grade third, cuts 7.26 / 9.19 g/t).
