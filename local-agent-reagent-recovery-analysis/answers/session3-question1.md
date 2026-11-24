## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Concentrator 1 at Site A"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tailings gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher feed flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "rougher concentrate flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__search_tags` {"query": "rougher tail flow rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow"}
- `mcp__historian__get_tag_details` {"ids": ["137"]}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation", "depth": 2}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Feed"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Concentrate"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Tail"}
- `mcp__historian__search_tags` {"query": "rougher gold recovery", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Rougher Conc Pump"}
- `mcp__historian__browse_asset` {"path": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1\\Flotation\\Tail Pump"}
- `mcp__historian__search_tags` {"query": "rougher feed flow", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow", "limit": 15}
- `mcp__historian__search_tags` {"query": "cyclone product flow to flotation", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "flow", "limit": 15}
- `mcp__historian__get_tag_details` {"ids": ["Rougher Feed|Solids", "158", "163", "181", "197"]}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 10}
- `mcp__historian__search_tags` {"query": "rougher feed solids", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition", "limit": 5}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "153", "158", "163", "181", "197"], "start": "2024-04-20T12:00:00+10:00", "end": "*", "mode": "summary", "interval": "1d", "summaries": ["Average"]}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && python3 -c \"import pandas, matplotlib; print('ok')\" && head -3 articles/local-agent-reagent-recovery-analysis/local/runs/r1/datasets/20261123-193134-0b3033.csv
- `write` {"path": "collector_recovery.py", "content": "\"\"\"Rougher gold recovery vs collector dose rate, Site A Concentrator 1.\n\nRecovery is calculated (not a tag) from the rougher feed / concentrate / tail\ngold assays plus the stream flows and solids to build a mass balance:\n\n  C = Rougher Conc Pump flow (m3/h)      [181, SA-C1-FT-3100]\n  T = Tail Pump flow (m3/h)              [197, SA-C1-FT-3115]
- `edit` {"path": "collector_recovery.py", "edits": [{"oldText": "label=\"10-point bin mean\")", "newText": "label=\"dose-bin mean\")"}]}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && grep -n \"bin mean\" collector_recovery.py | cat -A | head"}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 collector_recovery.py"}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nexec(open('collector_recovery.py').read().split('# keep physically sensible rows')[0])\nprint(df[['time','dose','feed_au','conc_au','tail_au','feed_solids','conc_s
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nexec(open('collector_recovery.py').read().split('# keep physically sensible rows')[0])\nd = df.dropna()\nd = d.query(\"conc_flow>0 and tail_flow>0 and feed_au>0 an
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nexec(open('collector_recovery.py').read().split('# keep physically sensible rows')[0])\nd = df.dropna()\nd = d.query(\"conc_flow>0 and tail_flow>0 and feed_au>0 an
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nexec(open('collector_recovery.py').read().split('# keep physically sensible rows')[0])\nd = df.dropna().query(\"conc_flow>0 and tail_flow>0 and feed_au>0 and conc_
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nexec(open('collector_recovery.py').read().split('# keep physically sensible rows')[0])\nd = df.dropna().query(\"conc_flow>0 and tail_flow>0 and feed_au>0 and conc_
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nexec(open('collector_recovery.py').read().split('# keep physically sensible rows')[0])\nd = df.dropna().query(\"conc_flow>0 and tail_flow>0 and feed_au>0 and conc_
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 - <<'EOF'\nimport pandas as pd, numpy as np\nexec(open('collector_recovery.py').read().split('# keep physically sensible rows')[0])\nd = df.dropna().query(\"conc_flow>0 and tail_flow>0 and feed_au>0 and conc_
- `write` {"content": "\"\"\"Rougher gold recovery vs collector dose rate, Site A Concentrator 1.\n\nRecovery is calculated (not a tag). Standard tail-loss formula:\n\n    recovery = 1 - (Au in rougher tail) / (Au in rougher feed)\n             = 1 - (gt * T) / (gf * F)\n\nwhere gf, gc, gt are the rougher feed / concentrate / tail gold assays (g/t)\nand T, F are volumetric flows (m3/h):\n    T = Tail Pump f
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/3 && MPLCONFIGDIR=/tmp/mpl python3 collector_recovery.py"}
- `read` {"path": "collector_dose_vs_rougher_recovery.png"}

## Answer

Done. The chart is saved at `collector_dose_vs_rougher_recovery.png` (script: `collector_recovery.py`, dataset: `runs/r1/datasets/20261123-193134-0b3033.csv`).

## Relationship

**Higher collector dose → higher rougher gold recovery, with diminishing returns.** Over the full historian record (2024-04-20 → 2026-11-13, 880 usable days):

- Dose 1.4–4 mL/min: recovery ~78–85%
- Dose 4–6 mL/min: ~87–89%
- Dose 6–8.5 mL/min: ~90%, essentially flat above ~6 mL/min
- Pearson r = 0.55; overall mean recovery 88%

So the plant gains roughly 10–12 points of rougher gold recovery going from low (~1.5) to normal (~6 mL/min) collector dosing, but dosing above ~6 mL/min buys little extra recovery.

## How recovery was calculated

No recovery tag exists, so I computed it daily from the tail-loss mass balance:

**recovery = 1 − (gt × T) / (gf × F)**

| Quantity | Tag (point) | Unit |
|---|---|---|
| Collector dose rate | `Flotation\Collector\Dose Rate` (SA-C1-FT-3057) | mL/min |
| Rougher feed Au | `Flotation\Rougher Feed\Au` (SA-C1-AT-3069) | g/t |
| Rougher concentrate Au | `Flotation\Rougher Concentrate\Au` (SA-C1-AT-3074) | g/t |
| Rougher tail Au | `Flotation\Rougher Tail\Au` (SA-C1-AT-3079) | g/t |
| Concentrate flow T→C | `Flotation\Rougher Conc Pump\Flow` (SA-C1-FT-3100) | m³/h |
| Tail flow T | `Flotation\Tail Pump\Flow` (SA-C1-FT-3115) | m³/h |
| Feed flow F | **C + T** (steady-state balance) | m³/h |

Basis: daily time-weighted averages, 2024-04-20 → 2026-11-22 (all data the historian holds).

## Caveats (provenance)

- **Collector dose tag is `stale`** — last record 2026-11-13, ~10 days before the historian's current time (2026-11-23). No QC/calc variant exists; the relationship therefore covers data through 2026-11-13.
- **No direct rougher feed flow tag** exists in the catalogue, so feed flow = concentrate pump + tail pump flow.
- **Feed solids % tag is inconsistent** with the pump flows (measured ~35% vs ~20% implied by the balance), so I used volumetric flows for the T/F ratio rather than density-corrected mass flows. The gold assays themselves close the balance, and the volumetric tail-loss formula is the only variant that yields physically plausible recovery (a density-corrected concentrate-based formula gave 40% of days >100%).
- 67 of 947 days were excluded (missing values or zero flows/assays, e.g. shutdowns).
