## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "final concentrate flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "solids mass flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "depth": 2}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Concentrate"}
- `mcp__historian__search_tags` {"query": "cyclone overflow flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "rougher feed pump flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__browse_asset` {"depth": 2, "path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Grinding"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Grinding\\Cyclone Cluster 1"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Conc Pump"}
- `mcp__historian__search_tags` {"query": "tail pump flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "final tail solids", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_timeseries` {"ids": ["149", "192", "174", "169", "197", "179"], "start": "2026-10-01", "end": "2026-11-01", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p2/2 && python3 - <<'EOF'\nimport csv, math\n\nf = \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-194827-5d6124.csv\"\nrows = list(csv.Di
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p2/2 && python3 - <<'EOF'\nimport csv\nf = \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-194827-5d6124.csv\"\nrows = list(csv.DictReader
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A", "limit": 15}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_timeseries` {"ids": ["175", "149", "169"], "interval": "1d", "mode": "summary", "start": "2026-10-01", "end": "2026-11-01", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p2/2 && MPLCONFIGDIR=/tmp python3 - <<'EOF'\nimport csv, datetime\nf = \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-195022-8990de.csv\"

## Answer

**Gold recovery at Site A, Concentrator 1 in October 2026: ≈ 72%** (grade-balance basis, 26 running days; the plant was down ~5 days around Oct 25–29).

## How it was calculated

There is **no recovery tag** in the catalogue, so I derived it from the gold assays. The straightforward mass-balance method (concentrate flow × solids × grade ÷ feed) is **not usable**: the flow/solids tags imply the concentrate carries ~40% of the feed solids, while the grades imply only ~7% — the two datasets don't reconcile, giving >100% recovery every day. The grade balance alone is self-consistent, so I used:

**Recovery = Gc × (Gf − Gt) / (Gf × (Gc − Gt))**

| Stream | Tag (point) | Oct mean |
|---|---|---|
| Feed | `…\Flotation\Rougher Feed\|Au` (SA-C1-AT-3069) | 5.28 g/t |
| Concentrate | `…\Flotation\Final Concentrate\|Au` (SA-C1-AT-3089) | 34.80 g/t |
| Tail | `…\Flotation\Final Tail\|Au` (SA-C1-AT-3094) | 1.66 g/t |

- **Monthly (time-weighted means):** 72.1%
- **Daily (26 running days):** average 72.4%, range 62–100%

## Provenance & caveats

- Window: 2026-10-01 → 2026-11-01, Australia/Brisbane, time-weighted daily averages (historian "now" is 2026-11-23, so "last month" = October).
- All three assay tags are primary, health `ok`.
- Not used: `Final Conc Pump|Flow` (SA-C1-FT-3110), `Tail Pump|Flow` (SA-C1-FT-3115) and the `|Solids` tags — inconsistent with the assays (see above). Worth flagging to the instrumentation team.
- "Rougher Feed" is the flotation feed (cyclone overflow), not the raw mill feed; if you want recovery against mill feed, there's no Au assay at that point in the catalogue.
- Chart: `gold_recovery_site_a_c1_oct2026.png` (in the current folder)
