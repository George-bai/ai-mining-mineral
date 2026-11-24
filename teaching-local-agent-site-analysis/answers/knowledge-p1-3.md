## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "limit": 15}
- `mcp__historian__get_tag_details` {"ids": ["137"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "*", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "*", "mode": "summary", "interval": "6h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20T12:00:00+10:00", "end": "*", "mode": "summary", "interval": "12h", "summaries": ["Average"]}
- `bash` {"command": "python3 -c \"import pandas, numpy, matplotlib, scipy; print('ok')\" 2>&1; head -3 articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets/20261123-195419-6be850.csv"}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/3 && MPLCONFIGDIR=/tmp MPLBACKEND=Agg python3 << 'EOF'\nimport pandas as pd, numpy as np\nfrom scipy import stats\n\nf = \"articles/teaching-local-agent-site-anal
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/3 && MPLCONFIGDIR=/tmp MPLBACKEND=Agg python3 << 'EOF'\nimport pandas as pd, numpy as np\nfrom scipy import stats\n\nf = \"articles/teaching-local-agent-site-anal
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/3 && MPLCONFIGDIR=/tmp MPLBACKEND=Agg python3 << 'EOF'\nimport pandas as pd, numpy as np\nfrom scipy import stats\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nrun = pd.read_csv(\"collector_recovery_data.c
- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/knowledge/p1/3/collector_dose_vs_rougher_recovery.png"}

## Answer

## Collector dose rate vs rougher gold recovery — Site A, Concentrator 1

**Short answer:** there is a strong positive relationship in the raw dose-rate tag (r ≈ +0.41), but most of it is a throughput artifact — the dosing pump's flow scales with mill feed rate. Per tonne of ore, the collector dose is essentially uncorrelated with rougher recovery. The raw relationship *is* different by feed grade: strongest at low grade, weakest at high grade.

### What the data shows (2024-04-20 → 2026-11-13, running hours only)

| Basis | All data | Low grade (<7.1 g/t Au) | Mid (7.1–9.0) | High (>9.0) |
|---|---|---|---|---|
| Dose rate (mL/min) vs recovery, Pearson r | **+0.405** | **+0.515** (slope +4.7 %/mL·min⁻¹) | +0.305 (+3.1) | +0.125 (+1.3) |
| Dose per tonne (mL/t) vs recovery, r | +0.093 | −0.124 | +0.082 | +0.044 |

- Recovery climbs from ~70% at doses below ~2 mL/min to ~88–90% at 7–8.7 mL/min (binned means, all data).
- The raw dose rate correlates with fresh feed rate (r = +0.68) and grade (r = +0.35); recovery also rises with grade (r = +0.37) and feed rate (r = +0.26). Controlling for feed rate, the dose–recovery correlation is still +0.33, so a genuine collector effect remains — but a substantial share of the raw +0.41 is "bigger mill → bigger pump flow → (coincidentally) better recovery".
- Per tonne, the relationship is flat in every grade band: the plant's recovery is not being bought by extra collector per tonne in this record.

### Provenance

- **Tags** (all primary, healthy):
  - `...\Flotation\Collector|Dose Rate` (SA-C1-FT-3057, mL/min) — **health is `stale`: last record 2026-11-13 20:58 AEST, ~10 days before the historian's now (2026-11-23). It is the only collector dose tag in the catalogue (no QC/calc variant), so I used it; the analysis window ends where its data ends.**
  - `...\Flotation\Rougher Feed|Au` (SA-C1-AT-3069), `Rougher Concentrate|Au` (SA-C1-AT-3074), `Rougher Tail|Au` (SA-C1-AT-3079), all g/t
  - `...\Grinding\SAG Mill|Fresh Feed Rate` (SA-C1-WT-2001, t/h) — golden throughput tag
- **Window:** historian's earliest record (2024-04-20 12:00) to 2026-11-13, in **12-hour time-weighted averages** (1h/6h exceeded the historian's interval limit). 1,738 complete rows → 1,731 with feed ≥ 50 t/h (stopped periods excluded, per site practice) → 1,707 after dropping 24 rows with non-physical recovery (0–100% filter).
- **Recovery:** two-product formula `100·c(f−t)/(f(c−t))` on rougher feed/concentrate/tail Au — the site's rougher gold recovery.
- **Grade bands:** terciles of the running-hours feed grade (cut points 7.12 and 9.02 g/t Au).

### Files saved in the current folder
- `collector_dose_vs_rougher_recovery.png` — two panels: dose rate (left) and dose per tonne (right) vs rougher recovery, coloured by grade band with per-band fit lines
- `collector_recovery_data.csv` — the cleaned 1,707-row dataset (time, dose, f/c/t, feed, recovery, dose per tonne, grade band)
