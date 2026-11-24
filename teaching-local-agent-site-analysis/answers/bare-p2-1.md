## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold grade feed", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "final tail flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "feed flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "depth": 2}
- `mcp__historian__search_tags` {"query": "rougher feed pump slurry", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "cyclone underflow flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Grinding", "depth": 2}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "depth": 2}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "192", "197"], "start": "2026-10-01", "end": "2026-10-31", "mode": "summary", "interval": "1d", "summaries": ["Average", "Count"]}
- `bash` {"command": "head -5 \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-192949-dcad46.csv\"; wc -l \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-192949-dcad46.csv\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p2/1 && python3 - <<'EOF'\nimport csv, math\nf=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-192949-dcad46.csv\"\nrows=list(csv.DictRead
- `mcp__historian__get_timeseries` {"ids": ["153", "174", "179"], "start": "2026-10-01", "end": "2026-10-31", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p2/1 && python3 - <<'EOF'\nimport csv, statistics\nf1=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-192949-dcad46.csv\"\nf2=\"~/
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p2/1 && python3 - <<'EOF'\nimport csv, statistics\nf1=\"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-192949-dcad46.csv\"\nf2=\"~/

## Answer

**Gold recovery at Site A, Concentrator 1 — October 2026: ≈ 71%** (71.5% by month mass balance; 70.8% mean of the 24 valid daily values).

**How it was calculated**

The historian has no single "recovery" tag, so I built it from the mass balance of the flotation circuit, on a dry-mass basis (grades are g/t dry solids):

Recovery = (final-concentrate flow × conc. solids % × conc. Au grade) ÷ (feed flow × feed solids % × feed Au grade)

where feed flow = final tail flow + final concentrate flow (steady-state balance; there is no direct rougher-feed flow meter in the catalogue).

**Tags used** (all primary, health ok, under `\\EXAMPLE-AF\Operations\Example Mining\Site A\Concentrator 1\Flotation`):

| Tag | Point | Unit |
|---|---|---|
| Rougher Feed\|Au | SA-C1-AT-3069 | g/t |
| Rougher Feed\|Solids | SA-C1-AT-3073 | % |
| Final Concentrate\|Au | SA-C1-AT-3089 | g/t |
| Final Concentrate\|Solids | SA-C1-AT-3093 | % |
| Final Conc Pump\|Flow | SA-C1-FT-3110 | m³/h |
| Tail Pump\|Flow | SA-C1-FT-3115 | m³/h |

**Basis:** time-weighted daily averages, 2026-10-01 → 2026-10-30 (AEST), from historian data (historian "now" is 2026-11-23, so "last month" = October).

**Caveats:**
- Oct 24–29 show near-zero feed Au grade (likely a shutdown or analyser gap) — excluded from the daily average, and they contribute essentially no gold to the month total, so the month figure is unaffected.
- Feed flow is derived from the two product streams, not measured directly; if you'd prefer recovery referenced to plant (crusher) feed, I'd need a feed flow tag that isn't in the catalogue.

**Chart:** saved as `gold_recovery_oct2026.png` in the current folder (daily recovery, red bands mark the excluded Oct 24–29 days, dashed line = month mass-balance value).
