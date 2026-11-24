## Tool calls

- `read` {"path": "articles/teaching-local-agent-site-analysis/local/runs/skills/condition/site-analysis/SKILL.md"}
- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "rougher feed gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher concentrate gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "rougher tail gold assay", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "composition"}
- `mcp__historian__search_tags` {"query": "SAG mill fresh feed rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1", "quantity": "rate"}
- `mcp__historian__get_timeseries` {"ids": ["149", "154", "159", "22"], "start": "2026-11-16T00:00:00+10:00", "end": "2026-11-23T00:00:00+10:00", "mode": "summary", "interval": "1h", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/skills/p3/2 && python3 << 'EOF'\nimport csv, math\n\nrows = []\nwith open(\"articles/teaching-local-agent-site-analysis/local/runs/skills/datasets/20261123-195235-5cb449.csv\"

## Answer

**The rougher mass pull at Site A, Concentrator 1 last week was 33.2 %** (feed-tonne weighted, 16–23 Nov 2026).

**Definition** — mass pull (%) = 100 × (f − t) / (c − t), with f, c, t the Au assays of the rougher feed, rougher concentrate and rougher tail, computed hourly and then weighted by feed tonnes across the week (the plant's method: metal balance over the period, not a mean of hourly pulls).

**Tags used** (all primary, healthy):
| Stream | Tag | Point |
|---|---|---|
| Feed (f) | `...\Flotation\Rougher Feed\|Au` | SA-C1-AT-3069 |
| Concentrate (c) | `...\Flotation\Rougher Concentrate\|Au` | SA-C1-AT-3074 |
| Tail (t) | `...\Flotation\Rougher Tail\|Au` | SA-C1-AT-3079 |
| Throughput | `...\Grinding\SAG Mill\|Fresh Feed Rate` | SA-C1-WT-2001 |

**Basis and screening**
- Window: 2026-11-16 00:00 → 2026-11-23 00:00 (AEST), hourly time-weighted averages from the historian (168 hours read).
- Running hours: feed rate was 471–634 t/h all week, so no stopped hours to drop (rule: < 50 t/h).
- Screened out 5 hours (all on the morning of 16 Nov) where the analyser glitched — concentrate Au read ~0.01–0.03 g/t or mass pull exceeded 100 %. 163 of 168 hours used, ~91,300 t of feed.
- Check: plain mean of the 163 hourly pulls is 32.8 % — within a point of the weighted figure, so no skew from low-throughput hours.
- Hourly pulls ranged 3.3 % to 63.0 %; the week's low pull hours sit on 16 Nov (the same period as the analyser glitches), so early-week pulls are the noisiest.

Chart saved: `rougher_mass_pull_last_week.png`
