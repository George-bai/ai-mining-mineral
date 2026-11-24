## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final concentrate Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "final tail Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-01-01", "end": "2026-03-22", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-03-22", "end": "2026-06-10", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-06-10", "end": "2026-08-29", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-08-29", "end": "2026-11-23", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-08-29", "end": "2026-10-18", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-10-18", "end": "2026-11-23", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/3 && python3 << 'EOF'\nimport pandas as pd, numpy as np\n\nfiles = [\n \"articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-200527-feac7
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/3 && python3 << 'EOF'\nimport pandas as pd, numpy as np\n\nfiles = [\n \"articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-200527-feac7
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/3 && python3 << 'EOF'\nimport pandas as pd, matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nres = pd.read_csv(\"monthly_recovery_2026.csv\", index_col=0)\nres.index = pd.PeriodIndex(res.index)\nlabels = [str(m) for m i
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p4/3 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport pandas as pd, matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nres = pd.read_csv(\"monthly_recovery_2026.csv\", index_col=0)\nres.index = pd.PeriodIndex(res.index, fre

## Answer

**August 2026 had the lowest gold recovery of 2026 so far: 68.2 %, with a feed grade of 6.10 g/t Au.**

Chart saved to `recovery_2026.png` (monthly recovery bars + feed-grade line, August highlighted).

## How it was calculated

**Definition** (per site knowledge): gold recovery = two-product formula on the analyser's Au assays — feed = Rougher Feed Au, concentrate = Final Concentrate Au, tail = Final Tail Au. Running hours only (stopped when fresh feed rate < 50 t/h).

**Tags used** (all primary, health ok, Site A Concentrator 1):
| Role | Tag | Point |
|---|---|---|
| Feed Au (f) | `...\Flotation\Rougher Feed\|Au` | SA-C1-AT-3069 |
| Concentrate Au (c) | `...\Flotation\Final Concentrate\|Au` | SA-C1-AT-3089 |
| Tail Au (t) | `...\Flotation\Final Tail\|Au` | SA-C1-AT-3094 |
| Feed rate (q) | `...\Grinding\SAG Mill\|Fresh Feed Rate` | SA-C1-WT-2001 |

**Basis:** hourly time-weighted averages, 2026-01-01 00:00 to 2026-11-22 23:00 AEST (historian's now is 2026-11-23 00:00; November is partial, 22 days). 7,824 hours read; 7,088 running; 234 running hours screened out (recovery outside 0–100 % or tail ≥ concentrate grade — analyser glitches).

**Weighting:** each month's recovery is metal-out over metal-in — each hour's recovery weighted by metal in the feed (q × f), not the mean of hourly recoveries. Feed grade weighted by feed tonnes. For August the plain mean of screened hours is 65.9 % vs 68.2 % weighted — a 2.3-point difference, driven by a cluster of low-recovery hours at high feed rates; the weighted figure is the site's basis.

**All months (recovery %, feed grade g/t, running hours):**

| Month | Recovery | Feed grade | Hours |
|---|---|---|---|
| Jan | 69.7 | 8.35 | 693 |
| Feb | 71.1 | 9.76 | 649 |
| Mar | 71.9 | 10.16 | 696 |
| Apr | 70.0 | 9.96 | 480 |
| May | 75.4 | 9.39 | 596 |
| Jun | 73.3 | 8.59 | 716 |
| Jul | 72.5 | 7.69 | 621 |
| **Aug** | **68.2** | **6.10** | 654 |
| Sep | 71.1 | 6.37 | 707 |
| Oct | 71.5 | 6.69 | 555 |
| Nov (to 22nd) | 72.8 | 8.61 | 487 |

Caveat: August's low recovery coincides with the year's lowest feed grade (6.10 g/t) — low-grade feed typically depresses recovery, so the two are associated, not necessarily caused by each other.
