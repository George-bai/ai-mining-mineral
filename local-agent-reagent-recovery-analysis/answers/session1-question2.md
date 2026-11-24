## Tool calls

- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/1 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport csv, math, collections\nimport matplotlib\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\n\nrows = list(csv.DictReader(open(\".claude/worktree
- `bash` {"command": "cd articles/local-agent-reagent-recovery-analysis/local/runs/r1/c1/1 && MPLCONFIGDIR=/tmp/mpl python3 << 'EOF'\nimport csv, collections\nrows = list(csv.DictReader(open(\"articles/local-agent-reagent-recovery-analysis/local/runs/r1/d

## Answer

Chart saved to `collector_dose_vs_recovery_by_feed_grade.png` in the current folder.

## Yes — the relationship differs markedly by feed grade

Feed grade was split into tertiles of the daily rougher feed Au (from `SA-C1-AT-3069`): **low < 7.0 g/t, mid 7.0–9.0 g/t, high ≥ 9.0 g/t** (287 days each).

| Feed grade | n | Pearson r | Mean recovery | Dose–recovery shape |
|---|---|---|---|---|
| **Low** (< 7.0 g/t) | 287 | **0.26** | 27.4% | **Clear positive trend** — binned means climb steadily from ~20% at 2.5 mL/min to ~33% at 7.5 mL/min |
| **Mid** (7.0–9.0 g/t) | 287 | 0.17 | 35.1% | Nearly flat — ~31–38% across the whole dose range |
| **High** (≥ 9.0 g/t) | 287 | 0.15 | 45.0% | Flat at a high level — ~42–48% regardless of dose |

**Interpretation:**
- At **low feed grade**, collector dose genuinely matters: more collector lifts recovery by roughly 10–15 percentage points across the operating range. This is where dose changes buy recovery.
- At **mid and high feed grade**, recovery is essentially set by the feed itself (high-grade feed recovers well even at low dose) and adding collector buys little — the curve is flat. The apparent overall correlation (r ≈ 0.35) from the previous chart was substantially inflated by this: operators tend to dose more when feed grade is high, and high grade itself gives high recovery.
- The high-grade group also runs at a slightly higher average dose (6.3 vs 5.3 mL/min for low), so part of the overall positive association is just grade-driven dosing policy rather than a causal dose effect.

### Provenance
Same four tags as before (`SA-C1-FT-3057` dose — **stale**, last record 2026-11-13; `SA-C1-AT-3069/3074/3079` Au assays — ok), same dataset (2024-04-20 → 2026-11-22, daily time-weighted averages, recovery = (feed−tail)/(conc−tail), 0–100% filter). Only the dose tag's staleness caveat applies to the last ~10 days.
