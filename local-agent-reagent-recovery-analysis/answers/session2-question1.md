## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tailings gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__get_tag_details` {"ids": ["137"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159"], "start": "2024-04-20T12:00:00+10:00", "end": "*", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `write` {"path": "plot_collector_recovery.py", "content": "import pandas as pd\nimport numpy as np\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nCSV = \"articles/local-agent-reagent-recovery-analysis/local/runs/r1/datasets/20261123-192502-6532e2.csv\"\nOUT = \"collector_dose_vs_rougher_recovery.p
- `edit` {"path": "plot_collector_recovery.py", "edits": [{"oldText": "df[\"recovery\"] = R.where(valid)", "newText": "df[\"recovery\"] = (R * 100).where(valid)  # percent"}]}
- `read` {"path": "plot_collector_recovery.py"}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/2 && python3 plot_collector_recovery.py"}
- `edit` {"path": "plot_collector_recovery.py", "edits": [{"oldText": "binned[\"x\"] = binned.index.mid", "newText": "binned[\"x\"] = binned.index.categories.mid"}]}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/2 && grep -n \"categories\" plot_collector_recovery.py && python3 plot_collector_recovery.py"}
- `read` {"path": "collector_dose_vs_rougher_recovery.png"}

## Answer

Chart saved to `collector_dose_vs_rougher_recovery.png` (script: `plot_collector_recovery.py`).

## Relationship

Over the full historian record (2024-04-20 → 2026-11-13, 878 valid daily points), collector dose rate and rougher gold recovery are **moderately positively correlated (Pearson r ≈ 0.48)**, with a clear shape:

- **~4.2–5.0 mL/min:** recovery ~79–82%
- **~5.7–6.4 mL/min:** ~86%
- **~6.4–8.5 mL/min:** ~87–88% — the curve **flattens out**; pushing dose above ~6.5 mL/min buys little extra recovery
- Days at very low dose (<3.5 mL/min, only ~30 points) show erratic, very low recovery — consistent with start-up/shutdown periods rather than normal operation

So the plant's normal operating window (4–8.5 mL/min) sits on the rising-then-plateau part of the curve; the data suggests a dose of roughly 6–7 mL/min captures most of the achievable recovery.

## Provenance

| Quantity | Tag (point) | Unit | Health |
|---|---|---|---|
| Collector dose rate | `…\Site A\Concentrator 1\Flotation\Collector\|Dose Rate` (SA-C1-FT-3057) | mL/min | ⚠️ **stale** — last value 2026-11-13; no healthy alternative exists in the catalogue (only tank level and pump status for the collector are live) |
| Rougher feed Au | `…\Rougher Feed\|Au` (SA-C1-AT-3069) | g/t | ok |
| Rougher concentrate Au | `…\Rougher Concentrate\|Au` (SA-C1-AT-3074) | g/t | ok |
| Rougher tail Au | `…\Rougher Tail\|Au` (SA-C1-AT-3079) | g/t | ok |

- **Window:** all available data, 2024-04-20T12:00 to 2026-11-22 (AEST), daily time-weighted averages (947 intervals).
- **Recovery is calculated, not a tag:** from the closed mass balance of the three assays, C/F = (a_feed − a_tail)/(a_conc − a_tail), so recovery = a_conc·(a_feed − a_tail) / (a_feed·(a_conc − a_tail)). 69 days dropped for invalid balances (e.g. zero feed assay).
- Dataset: `runs/r1/datasets/20261123-192502-6532e2.csv`.

**Caveats:** the dose-rate tag has had no data for ~10 days (stale), and recovery is derived from time-averaged daily assays, so day-level scatter includes assay/balance noise; the binned-mean line is the more reliable read of the trend.
