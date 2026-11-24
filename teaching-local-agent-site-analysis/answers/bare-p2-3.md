## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 10}
- `mcp__historian__search_tags` {"query": "mass flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate", "limit": 10}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "depth": 2}
- `mcp__historian__search_tags` {"query": "mass flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "flow", "limit": 15}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed", "depth": 1}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Concentrate", "depth": 1}
- `mcp__historian__get_golden_tags` {"scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery percent", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A", "limit": 10}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Conc Pump", "depth": 1}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Tail Pump", "depth": 1}
- `mcp__historian__search_tags` {"query": "mass flow rate solids", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__search_tags` {"query": "Final Conc Pump flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation"}
- `mcp__historian__search_tags` {"query": "Tail Pump flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation"}
- `mcp__historian__search_tags` {"query": "solids percent", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "quantity": "composition", "limit": 10}
- `mcp__historian__get_timeseries` {"ids": ["192", "174", "169", "197", "179", "175"], "start": "2026-10-01T00:00:00+10:00", "end": "2026-10-31T23:59:59+10:00", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p2/3 && python3 - <<'EOF'\nimport csv, math\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf = \"articles/teaching-local-agent-site-analy
- `bash` {"command": "ls -la articles/teaching-local-agent-site-analysis/local/runs/bare/p2/3/gold_recovery_siteA_c1_oct2026.png"}

## Answer

**Gold recovery at Site A, Concentrator 1 in October 2026: ≈ 95.5%** (mass-balance estimate; the catalogue has no direct recovery tag).

**How it was derived** — recovery = Au in final concentrate ÷ (Au in final concentrate + Au in final tail), with each stream's Au mass flow = slurry flow × solids mass fraction × Au grade (solids density assumed 2.7 t/m³, which cancels in the ratio):

| Tag | Point | Unit | Oct mean |
|---|---|---|---|
| Final Conc Pump\|Flow | SA-C1-FT-3110 | m³/h | 527.9 |
| Final Concentrate\|Solids | SA-C1-AT-3093 | % | 5.49 |
| Final Concentrate\|Au | SA-C1-AT-3089 | g/t | 34.80 |
| Tail Pump\|Flow | SA-C1-FT-3115 | m³/h | 483.1 |
| Final Tail\|Solids | SA-C1-AT-3098 | % | 5.65 |
| Final Tail\|Au | SA-C1-AT-3094 | g/t | 1.66 |

All six tags are primary variants, health **ok**. Basis: time-weighted daily averages (1 d interval) over 1 Oct – 31 Oct 2026 (Australia/Brisbane), dataset `20261123-200635-12027e`. Monthly result: ~45.5 kg/h of Au to concentrate vs ~2.2 kg/h to tail.

**Caveats:**
- This is an estimate, not a plant-reported figure — no "recovery" tag exists in the catalogue (searched concentrator and Site A scopes).
- Daily recovery ranged ~94–96%, with a couple of days at ~100% where the tail Au assay was near zero (likely assay gaps), so treat the month as ≈ 95–96%.
- "Last month" was taken as October 2026, since the historian's current time is 2026-11-23.

**Chart:** saved as `gold_recovery_siteA_c1_oct2026.png` in the current folder (daily recovery with the October total line).
