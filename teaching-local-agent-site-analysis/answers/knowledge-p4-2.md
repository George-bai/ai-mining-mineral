## Tool calls

- `mcp__historian__catalog_status` {}
- `mcp__historian__find_assets` {"text": "Site A Concentrator 1"}
- `mcp__historian__search_tags` {"query": "Rougher Feed Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "Final Concentrate Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "Final Tail Au", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__search_tags` {"query": "SAG Mill Fresh Feed Rate", "scope": "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "start": "2026-01-01T00:00:00+10:00", "end": "2026-11-23T00:00:00+10:00", "mode": "summary", "interval": "15m", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-11-23T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-01-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-11-23T00:00:00+10:00", "interval": "2h", "mode": "summary", "start": "2026-01-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-02-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-01-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-03-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-02-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-04-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-03-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-05-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-04-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-06-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-05-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-07-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-06-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-08-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-07-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-09-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-08-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-10-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-09-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-11-01T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-10-01T00:00:00+10:00", "summaries": ["Average"]}
- `mcp__historian__get_timeseries` {"ids": ["149", "169", "175", "22"], "end": "2026-11-23T00:00:00+10:00", "interval": "1h", "mode": "summary", "start": "2026-11-01T00:00:00+10:00", "summaries": ["Average"]}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/datasets && ls 20261123-19512*.csv && head -3 20261123-195124-dedde7.csv"}
- `bash` {"command": "python3 -c \"import pandas, matplotlib; print('ok')\""}
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/2 && python3 << 'EOF'\nimport pandas as pd\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nfiles = {\n \"Jan\":\"20261123-195124-dedde7.csv\",\"Feb\":\"20261123-195128-049b44.csv\",\n \"Mar\":\"20261123-1951
- `bash` {"command": "cd articles/teaching-local-agent-site-analysis/local/runs/knowledge/p4/2 && python3 << 'EOF'\nimport pandas as pd\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nfiles = {\n \"Jan\":\"20261123-195124-dedde7.csv\",\"Feb\":\"20261123-195128-049b44.csv\",\n \"Mar\":\"20261123-1951

## Answer

**April 2026 had the lowest gold recovery so far this year: 65.7%, with a feed grade of 8.9 g/t Au.**

Monthly results (2026, running hours only):

| Month | Recovery (%) | Feed grade (g/t Au) |
|---|---|---|
| Jan | 69.3 | 8.2 |
| Feb | 71.0 | 9.8 |
| Mar | 71.5 | 10.0 |
| **Apr** | **65.7** | **8.9** |
| May | 74.9 | 9.5 |
| Jun | 73.0 | 8.6 |
| Jul | 71.8 | 7.7 |
| Aug | 66.9 | 5.9 |
| Sep | 71.1 | 6.4 |
| Oct | 71.3 | 6.6 |
| Nov* | 71.8 | 8.5 |

*November is partial (1–22 Nov, through the historian's current time of 2026-11-23).

April's dip was driven by the month's highest tail Au (3.56 g/t time-weighted) against a mid-range feed grade; August was a close second (66.9%) on a much lower feed grade.

**Provenance**
- Tags (all primary, healthy): Rougher Feed|Au `SA-C1-AT-3069`, Final Concentrate|Au `SA-C1-AT-3089`, Final Tail|Au `SA-C1-AT-3094` (g/t), and SAG Mill|Fresh Feed Rate `SA-C1-WT-2001` (t/h) under `\\EXAMPLE-AF\Operations\Example Mining\Site A\Concentrator 1`.
- Basis: time-weighted hourly averages (summary mode), 1 Jan – 22 Nov 2026, Australia/Brisbane time.
- Running hours only, per site practice: hours with fresh feed rate < 50 t/h were excluded (e.g. April: 559 of 632 hours running; the analyser holds last values when stopped, so stopped hours would have distorted the assays).
- Recovery computed from the monthly time-weighted f/c/t with the two-product formula: 100·c(f−t)/(f(c−t)).
- Chart saved as `siteA_c1_2026_monthly_recovery.png` in the current folder (worst month highlighted in red).
