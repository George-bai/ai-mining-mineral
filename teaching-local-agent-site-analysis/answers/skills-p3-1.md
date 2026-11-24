## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__get_timeseries` {"ids": ["22", "149", "154", "159"], "start": "2026-11-16T00:00:00+10:00", "end": "2026-11-23T00:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p3/1 && python3 - <<'EOF'\nimport csv, math\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nrows = list(csv.DictReader(open(\"articles/t

## Answer

**The rougher mass pull at Site A, Concentrator 1 last week (16–23 Nov 2026) was 33.2 %** (feed-tonne-weighted, running hours only).

**Definition & tags** — mass pull (%) = 100 × (f − t)/(c − t), from the plant knowledge, using the Au assays of:
| Tag | Point | Unit |
|---|---|---|
| `...\Flotation\Rougher Feed\|Au` (f) | SA-C1-AT-3069 | g/t |
| `...\Flotation\Rougher Concentrate\|Au` (c) | SA-C1-AT-3074 | g/t |
| `...\Flotation\Rougher Tail\|Au` (t) | SA-C1-AT-3079 | g/t |
| `...\Grinding\SAG Mill\|Fresh Feed Rate` (running-hours rule & weighting) | SA-C1-WT-2001 | t/h |

All four are primary, healthy tags.

**Basis**
- Window: 2026-11-16 00:00 → 2026-11-23 00:00 (AEST), per the historian's clock; hourly time-weighted averages (168 hours read).
- Running hours: 0 hours stopped (feed never fell below 50 t/h; min 471 t/h).
- Screening: 5 hours dropped as analyser glitches (tail grade ≥ concentrate grade or a mass pull outside 0–100 %), leaving 163 usable hours.
- Weighting: each hour's mass pull weighted by feed tonnes (Σq·MP/Σq) = **33.15 %**; the plain mean of the 163 hours is 32.82 % — a 0.3-point difference, so the two agree.
- Hourly values ranged from 3.3 % to 63.0 %.

**Chart:** `rougher_mass_pull_last_week.png` (current folder) — hourly mass pull with the weighted average and plain mean marked.
