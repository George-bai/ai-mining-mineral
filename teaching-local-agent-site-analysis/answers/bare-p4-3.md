## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A"}
- `mcp__historian__search_tags` {"query": "recovery", "limit": 15}
- `mcp__historian__search_tags` {"query": "feed flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "concentrate flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "tailings flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "depth": 2}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Concentrate"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Final Tail"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "depth": 1}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175"], "start": "2026-01-01", "end": "2026-11-23", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/3 && python3 - <<'EOF'\nimport csv\nfrom collections import defaultdict\n\nf = \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-200932-3
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/3 && python3 - <<'EOF'\nimport csv\nfrom collections import defaultdict\n\nf = \"articles/teaching-local-agent-site-analysis/local/runs/bare/datasets/20261123-200932-3
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/bare/p4/3 && python3 - <<'EOF'\nimport csv\nfrom collections import defaultdict\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nf = \"articles/

## Answer

**April 2026** had the lowest gold recovery at Site A, Concentrator 1 — about **59.1%**, with a feed grade of **8.44 g/t Au** (monthly average).

Chart saved: `sa_c1_recovery_2026.png` (current folder).

### Monthly results (2026-01-01 → 2026-11-22, historian's "now" is 2026-11-23)

| Month | Feed grade (g/t Au) | Recovery (approx.) |
|---|---|---|
| Jan | 8.01 | 64.5% |
| Feb | 9.70 | 65.5% |
| Mar | 9.77 | 65.4% |
| **Apr** | **8.44** | **59.1% ← lowest** |
| May | 8.68 | 70.7% |
| Jun | 8.56 | 68.5% |
| Jul | 6.54 | 63.7% |
| Aug | 5.45 | 60.9% |
| Sep | 6.40 | 67.7% |
| Oct | 5.28 | 61.1% |
| Nov (to 22nd) | 8.15 | 67.1% |

### Provenance & caveats
- **No dedicated "recovery" tag exists** in the catalogue (searched the concentrator, Site A, and the whole catalogue). Recovery was therefore **derived**: `recovery ≈ 1 − (Final Tail Au ÷ Rougher Feed Au)`, the standard grade-ratio approximation, which is exact only if final-tail and feed mass flows are similar (concentrate mass is small, so it's a reasonable estimate, not a full mass balance — the catalogue has no flow tags on these analyser streams).
- Tags used (all primary, health `ok`, unit g/t):
  - Rougher Feed|Au — `SA-C1-AT-3069` (id 149)
  - Final Tail|Au — `SA-C1-AT-3094` (id 175)
  - Final Concentrate|Au — `SA-C1-AT-3089` (id 169, shown for context)
- Basis: time-weighted daily averages from the historian (dataset `20261123-200932-30a58f`), aggregated to calendar months; days with zero/missing readings (downtime) were excluded from the averages — April had only 25 of 31 days with data, which is worth keeping in mind.
- Timezone: Australia/Brisbane, per the historian.
