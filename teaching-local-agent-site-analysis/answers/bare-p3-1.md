## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__get_golden_tags` {"scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "kpi": "throughput"}
- `mcp__historian__search_tags` {"query": "rouser mass pull", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rouser", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "depth": 2}
- `mcp__historian__search_tags` {"query": "rougher feed mass flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "rougher mass", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation"}
- `mcp__historian__search_tags` {"query": "mass pull", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Concentrate"}
- `mcp__historian__search_tags` {"query": "mass flow rate tonnes per hour", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation"}
- `mcp__historian__search_tags` {"query": "mass pull", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A"}
- `mcp__historian__search_tags` {"query": "rougher pull"}
- `mcp__historian__search_tags` {"query": "mass flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow", "limit": 20}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Grinding\\Cyclone Cluster 1"}
- `mcp__historian__search_tags` {"query": "t/h tonnes per hour", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 20}
- `mcp__historian__get_tag_details` {"ids": ["SA-C1-WT-2001", "SA-C1-FT-3100"]}
- `mcp__historian__get_timeseries` {"ids": ["22"], "start": "*-7d", "end": "t", "mode": "summary", "interval": "1h", "summaries": ["Average", "Minimum", "Maximum"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p3/1 && python3 -c \"\nimport csv, datetime\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nrows = list(csv.DictReader(open('articles/teachi

## Answer

**Caveat first:** the catalogue has **no tag literally named "rougher mass pull"** — I searched for "mass pull", "rougher mass", "mass flow" and browsed the Rougher Feed/Concentrate streams (they only carry assay tags: Pb, S, Solids, Au, Ag). The closest mass-flow measurement is the **SAG mill fresh feed rate**, which at steady state is the mass pull into the rougher. I've charted that; if you meant something else (e.g. the rougher concentrate pump flow, `SA-C1-FT-3100`, m³/h — volumetric, not mass), tell me and I'll pull it instead.

## Site A, Concentrator 1 — mass pull, last week

- **Time-weighted average: ~560 t/h** (559.7 t/h per the historian)
- Hourly range: ~471–634 t/h (overall min 308 / max 656 t/h, including brief low points)
- Window: 2026-11-16 00:00 → 2026-11-23 00:00 AEST (7 days, 168 hourly averages)

**Provenance**
- Tag: `\\EXAMPLE-AF\Operations\Example Mining\Site A\Concentrator 1\Grinding\SAG Mill|Fresh Feed Rate`, point `SA-C1-WT-2001`, unit t/h, health ok (golden throughput tag)
- Basis: summary mode, 1 h intervals, time-weighted average
- Dataset: `.../bare/datasets/20261123-193558-70c23b.csv`

**Chart saved:** `rougher_mass_pull_SA_C1_last_week.png` in the current folder.
