# Can a local agent see that collector dose relates to recovery differently at each feed grade?

Questions, key, run script and every answer for the article at
https://eleticle.com/articles/local-agent-reagent-recovery-analysis/ (No. 20). It runs on No. 18's stand-in historian,
catalogue, MCP server and skill (`../historian-tag-catalogue-for-agents/`) with the agent set-up of No. 19
(`../local-agent-finds-historian-tags/`).

## Data

Site A, Concentrator 1's flotation tags in the stand-in follow Zyfra's hourly gold flotation record (15 Jan 2016 to
18 Aug 2018, 22,716 hours), not included here. To repeat the work, fetch
`datasets/gold_recovery_full.csv` from https://github.com/5hraddha/zyfra-gold-recovery-prediction at commit
`629470d8d6a1b151295f14b784964b442f79fd42` (SHA-256 `d477aa4d…151aa2`) and build No. 18's backbones from it.
The stand-in's clock puts the record's last hour at 22 Nov 2026, 23:00 (AEST). Collector dose is the stand-in's
`Flotation\Collector|Dose Rate` tag (unit mL/min in the stand-in; Zyfra does not publish its units), following
Zyfra's `rougher.input.floatbank10_xanthate`.

## Files

| File | What it is |
|---|---|
| `questions.yaml` | The two questions, asked in turn in one session |
| `make_key.py`, `key.json` | Our analysis through the same tool code, before any run: daily and hourly, as recorded and per tonne of feed, with a week-block bootstrap. The daily points themselves (Zyfra's values) are not published |
| `frozen.sha256` | Hashes taken before the runs, of the files as run, at their paths in our working repository (`articles/<slug>/public/`). Entries for files changed since no longer match: the published key (values or points removed, see the comments in the file), the scripts (only to find the other articles' folders in this repository's layout, 24 Nov 2026) and No. 18's `mcp_server.py` (a statistics fix, 24 Nov 2026) |
| `run.sh`, `models.json`, `prompt.md`, `answer.py` | The run: Pi 1.5.2, Qwen 3.8 27B, No. 18's MCP server over HTTP, a fresh fenced session per repeat, the second question with `--continue` |
| `answers/` | Each session's tool calls and answers, turn by turn (a call's arguments are cut at 400 characters and what the tools returned is not included, so these are an index of the calls, not a full trace) |
| `charts/` | The second run's charts as the agent saved them, one per session and question. Session 2's second answer put its three slopes only on its chart (`second-run-session2-question2.png`), which is what its verdict was read from; session 3's second chart is the one titled per tonne while plotting the flow. The scripts the agent wrote in that run are not published: they were written under the unpublished skill |
| `verdicts.yaml` | Each turn's verdict, the agent's numbers as it reported them, and the reason |

## Run it

The environment is No. 19's (its README, "Run it": the stand-in and catalogue of No. 18, the agent's Python as
`AGENT_ENV`, Pi 1.5.2, bubblewrap, the model server and its settings).

- **The key, without a model:** with the stand-in running and crawled,
  `../historian-tag-catalogue-for-agents/.venv/bin/python make_key.py`. Its tags follow Zyfra's public record, so it
  repeats from public inputs.
- **The first run:** `AGENT_ENV=<python environment> REPEATS=3 ./run.sh <run-name>`.
- **The second run** (`KIT=1 ./run.sh kit`) needs the analytical skill, which is not published (`SKILLS_DIR` points at
  it), so it can be read here but not repeated.

## Rules (fixed before the runs)

Turn 1 passes when the agent reads the four Site A, Concentrator 1 tags over the whole record, calculates recovery
by the two-product formula, reports a positive overall relationship with a number and saves a chart. Turn 2 passes
when it splits by rougher feed gold into three bands and reports the low band steeper than the high one on the
recorded dose (or, using dose per tonne and saying so, no clear difference), with a chart. A session passes when both
turns pass; the bar is two of three.

## Two runs

- **First run** (`answers/session<N>-question<M>.md`, `verdicts.yaml`): the questions as above. One session of three
  passed: session 1 calculated mass pull, (f − t)/(c − t), and called it recovery; session 3 built recovery from the
  pump flow tags, which the stand-in generates. All three found their strongest correlation, on recovery as each calculated it, in the low
  feed-grade third (correlations, not slopes). Two rules were written down after session 1 was read and before sessions 2 and 3 were:
  turn 2 needs recovery itself, and "steeper" needs a rate, not a correlation alone.
- **Second run** (`answers/second-run-*.md`, `verdicts-kit.yaml`), added because the first missed its bar, as that
  rule said: the same questions with No. 21's plant knowledge page and analytical skill (`KIT=1 run.sh kit`; the skill
  is not published). Three of three passed, within 0.01 of our hourly analysis (2.85, 1.72, 1.03): by design, since the
  skill follows the same procedure. In one session the band results were only on its chart, not in its message.

## What the key says

Over the whole record, daily: 3.34 percentage points of rougher recovery per mL/min of collector (r 0.47). By thirds
of feed gold: low 3.65, mid 2.06, high 1.10; low minus high 2.54, 95 % interval 0.64 to 4.56 (weeks resampled).
Hourly: 2.85, 1.72, 1.03. Per tonne of feed a difference between thirds is not shown (intervals span zero): dose
follows feed rate, so this is an association, not an effect of collector. In 2018 alone the order does not hold, and it does not hold in every shorter window (No. 18's development log).

## Licence

Code: MIT. Questions, key numbers, answers and verdicts: CC BY 4.0.
