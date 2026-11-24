---
name: historian-tags
description: Find the right historian tags for a question about the plant and read their data through the historian MCP tools, with the provenance of every number. Use when a question needs plant measurements (power, flow, feed rate, pressure, density, levels, assays, run status) from the historian.
---

# Finding and reading historian tags

The historian holds tens of thousands of tags. Never list them: search the catalogue, read only the few tags you
chose, and say where each number came from.

## Steps

0. **Clock.** Call `catalog_status` once: `historian_now` is the historian's current time and `historian_earliest`
   its first record. Relative times (`*-30d`, `y`, `t`) count from `historian_now`; convert dates the user names
   against it, not against your own idea of today. "All the data" means from `historian_earliest`.
1. **Place.** Resolve the place in the question with `find_assets` ("Site B concentrator 2", "ball mill 2 at
   site c"). Use the path it returns as `scope` from here on.
2. **Known tags.** For throughput, power, energy or raw water, call `get_golden_tags` with that scope first.
3. **Search.** Call `search_tags` with a short query in plain words and the scope; add `quantity` when the
   question names one (power, flow, rate, pressure, density, level, composition, current, speed, status,
   duration). Read each result's `why`, `health` and `unit`.
   - Nothing fits: widen the scope to the parent (power is often metered at the concentrator's supply or main
     incomer, not at each motor), or try other words for the same thing.
   - A point name in the question (`SB-C2-PT-2004`, `SBC1_BM2_PWR`): search for it as written; it may be a point
     that is not in the asset tree.
4. **Ask when unsure.** If the top candidates are close and differ in place or meaning (two pressures, three
   concentrators), list them and ask the user which one, unless the question already decides it.
5. **Read.** Call `get_timeseries` in `summary` mode (time-weighted) with an interval that gives tens to hundreds
   of values: 1h for a day or a week, 1d for a month or more. Use `recorded` only for short windows when the raw
   records matter. Use `get_current_values` for "now".
6. **Analyse.** Use the summary it returns, or open the dataset file it names (CSV, one column per tag and
   summary, times in the site's time zone) with code for charts and further work.
7. **Answer with provenance:** the tags (path and point name), units, time window and basis (time-weighted
   average, interpolated or raw), and any tag you could not use and why.

## Rules

- Prefer a total (a main incomer, a feed rate at the mill) to summing its parts.
- Prefer healthy primary tags. Use a QC, Calc or alarm variant only when the user asks for it.
- A tag whose health is `stale`, `no_data`, `bad_quality` or `broken_ref` is not data: say so, and offer the
  nearest healthy alternative.
- Keep units consistent; `get_timeseries` converts kW and MW, m3/h and L/s, kPa and bar when you ask with `units`.
- Never invent a tag name. If the catalogue has no tag for what the user asks, say so plainly.
