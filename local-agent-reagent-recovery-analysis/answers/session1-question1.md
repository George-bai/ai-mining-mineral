## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tailings gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__get_tag_details` {"ids": ["137", "149", "154", "159"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159"], "start": "2024-04-20", "end": "*", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/1 && python3 << 'EOF'\nimport csv, math\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nrows = list(csv.DictReader(open(\"articles/loc
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/1 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport csv, math, collections\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nrows = list(csv.DictReader(open(\".claude/worktree

## Answer

Chart saved to `collector_dose_vs_rougher_recovery.png` in the current folder.

## Answer

**There is a positive relationship: higher collector dose rates are associated with higher rougher gold recovery, but the effect is modest and noisy.**

- **Pearson correlation r ≈ 0.35** (861 daily points) — a real but weak-to-moderate positive association.
- **Binned means** show a clear upward trend: mean recovery rises from ~20–26% at 2.5–3.0 mL/min, through ~32–35% at 4.5–6.0 mL/min, to ~41–44% at 7.0–8.0 mL/min. The trend flattens slightly above ~7 mL/min (41.2% → 40.4% → 43.6%), suggesting diminishing returns at the top of the dose range.
- Overall mean: dose 5.8 mL/min, recovery 35.8%.

### How recovery was calculated
Rougher recovery is not a tag; it was computed daily from the three gold assays using the standard grade-only balance (mass balance F = C + T):

**Recovery = (Feed Au − Tail Au) / (Concentrate Au − Tail Au)**

Days where the dose was zero, the concentrate grade was ≤ tail grade, or the result fell outside 0–100% (assay timing mismatches) were excluded (22 of 947 days).

### Provenance
| Quantity | Tag (path → point) | Unit | Health |
|---|---|---|---|
| Collector dose rate | `…\Site A\Concentrator 1\Flotation\Collector\|Dose Rate` → `SA-C1-FT-3057` | mL/min | ⚠️ **stale** |
| Rougher feed Au | `…\Flotation\Rougher Feed\|Au` → `SA-C1-AT-3069` | g/t | ok |
| Rougher concentrate Au | `…\Flotation\Rougher Concentrate\|Au` → `SA-C1-AT-3074` | g/t | ok |
| Rougher tail Au | `…\Flotation\Rougher Tail\|Au` → `SA-C1-AT-3079` | g/t | ok |

- **Window:** all historian data, 2024-04-20 → 2026-11-22 (historian's earliest record to now), Australia/Brisbane time.
- **Basis:** summary mode, 1-day intervals, time-weighted daily averages.
- **Caveat:** the collector dose tag is flagged **stale** — its last record is 2026-11-13, ~10 days before the historian's current time (2026-11-23). I found no alternative collector dose tag (only its tank level and pump run status exist), so the analysis covers 2024-04-20 → 2026-11-13. If that flow meter is genuinely dead, the last ~10 days of recovery have no dose to pair with.
