## Tool calls

- `read` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "collector dose rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_tag_details` {"ids": ["137", "149", "154", "159", "22"]}
- `mcp__historian__search_tags` {"query": "collector", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-04-20", "end": "2024-07-09", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-07-09", "end": "2024-09-27", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-09-27", "end": "2024-12-16", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2024-12-16", "end": "2025-03-06", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-03-06", "end": "2025-05-25", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-05-25", "end": "2025-08-13", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-08-13", "end": "2025-11-01", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2025-11-01", "end": "2026-01-20", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-01-20", "end": "2026-04-10", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-04-10", "end": "2026-06-29", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-06-29", "end": "2026-09-17", "mode": "summary", "interval": "1h"}
- `mcp__historian__get_timeseries` {"ids": ["137", "149", "154", "159", "22"], "start": "2026-09-17", "end": "*", "mode": "summary", "interval": "1h"}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 -c \"import pandas, matplotlib, numpy; print('ok')\" && ls articles/local-agent-reagent-recovery-analysis/local/runs/kit/datasets/"}
- `write` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1/analyze.py", "content": "import os, glob, json\nimport numpy as np\nimport pandas as pd\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nos.environ.setdefault(\"MPLCONFIGDIR\", \"/tmp/mpl\")\nDS = \"~/
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 analyze.py"}
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 - <<'EOF'\nimport os\nos.environ[\"MPLCONFIGDIR\"]=\"/tmp/mpl\"\nimport numpy as np, pandas as pd, glob\nDS=\"articles/local-agent-reagent-recovery-anal
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 - <<'EOF'\nimport os\nos.environ[\"MPLCONFIGDIR\"]=\"/tmp/mpl\"\nimport numpy as np, pandas as pd, glob\nDS=\"articles/local-agent-reagent-recovery-anal
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 - <<'EOF'\nimport os\nos.environ[\"MPLCONFIGDIR\"]=\"/tmp/mpl\"\nimport numpy as np, pandas as pd, glob\nDS=\"articles/local-agent-reagent-recovery-anal
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 - <<'EOF'\nimport os\nos.environ[\"MPLCONFIGDIR\"]=\"/tmp/mpl\"\nimport numpy as np, pandas as pd, glob\nDS=\"articles/local-agent-reagent-recovery-anal
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 - <<'EOF'\nimport os\nos.environ[\"MPLCONFIGDIR\"]=\"/tmp/mpl\"\nimport numpy as np, pandas as pd, glob\nDS=\"articles/local-agent-reagent-recovery-anal
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 - <<'EOF'\nimport os\nos.environ[\"MPLCONFIGDIR\"]=\"/tmp/mpl\"\nimport numpy as np, pandas as pd, glob\nDS=\"articles/local-agent-reagent-recovery-anal
- `edit` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1/analyze.py", "edits": [{"oldText": "d[\"week\"] = d[\"time\"].dt.to_period(\"W\")\nweeks = d.groupby(\"week\")\nrng = np.random.default_rng(42)\nB = 1000\ndiffs = np.empty(B)\nfor i in range(B):\n    sel = rng.integers(0, len(weeks), len(weeks))\
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1 && python3 analyze.py 2>/dev/null"}
- `read` {"path": "articles/local-agent-reagent-recovery-analysis/local/runs/kit/c1/1/collector_vs_rougher_recovery.png"}

## Answer

**Answer:** Over the full historian record (2024‑04‑20 → 2026‑11‑22), higher collector dose rate is associated with higher rougher gold recovery — a least‑squares slope of **≈ +2.4 percentage points of recovery per mL/min (r = 0.33)** — but this is an association, not a demonstrated effect: the dose rate tracks throughput (corr with feed rate 0.57), and the relationship is much weaker when feed grade is high.

**Chart:** saved as `collector_vs_rougher_recovery.png` in the current folder (4 panels: dose rate vs recovery, dose per tonne vs recovery, by feed‑grade thirds, and dose rate vs feed rate).

**How it was calculated**

| Item | Detail |
|---|---|
| Rougher recovery | Not a tag. Hourly: `100 × c(f−t) / (f(c−t))` with f = Rougher Feed Au (`SA-C1-AT-3069`), c = Rougher Concentrate Au (`SA-C1-AT-3074`), t = Rougher Tail Au (`SA-C1-AT-3079`), all g/t, 1 h time‑weighted averages |
| Collector dose rate | `SA-C1-FT-3057` (Flotation\Collector\|Dose Rate), mL/min |
| Running hours | SAG Fresh Feed Rate (`SA-C1-WT-2001`) ≥ 50 t/h |
| Hours | 22,728 read → 20,689 running → **1,842 screened out** (recovery outside 0–100 %, tail grade ≥ concentrate grade, or missing values) → **18,847 used** |
| Overall rougher recovery | 85.8 % (metal‑in‑weighted, Σq·f·R/Σq·f); plain mean 84.9 % — difference < 1 point |

**Relationships**

- **Dose rate vs recovery:** slope +2.43 pp per mL/min, r = 0.33 (n = 18,847).
- **Confounding:** dose rate correlates 0.57 with feed rate, so part of the apparent benefit is just "bigger plant, more reagent". On **dose per tonne** (mL/t) the association weakens to r = 0.16 (slope +6.1 pp per mL/t). I report the dose‑rate form, as that is what the plant controls.
- **By feed grade thirds** (cuts 7.26 and 9.19 g/t Au):
  - low grade: slope +2.86 pp per mL/min, r = 0.32 (n = 6,283)
  - mid grade: slope +1.72, r = 0.28 (n = 6,282)
  - high grade: slope +1.03, r = 0.22 (n = 6,282)
  - High‑minus‑low slope difference = **−1.83 pp per mL/min, 95 % CI [−3.08, −0.68]** (block bootstrap, whole weeks, 1,000 draws) — the interval excludes zero, so the data do show a materially weaker dose–recovery association at high feed grade.

**Caveats**

- The collector dose rate tag is flagged **stale**: its last record is 2026‑11‑13, so the final ~10 days of the window have no collector data (those hours were dropped as missing). No QC/calc alternative exists in the catalogue; it is the only collector dose tag.
- This is an observational association. Dose rate is set by operators in response to grade, throughput and mill behaviour, so the slope should not be read as "the effect of" changing the collector dose.
