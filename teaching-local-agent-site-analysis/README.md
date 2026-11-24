# What does a small local model need to analyse your site's data well?

Questions, key, the plant knowledge page, run script and every answer for the article at
https://eleticle.com/articles/teaching-local-agent-site-analysis/ (No. 21). Same data, model and tools as No. 20
(`../local-agent-reagent-recovery-analysis/`).

## Three conditions

| Condition | What the agent has beyond No. 18's tools and tag-finding skill |
|---|---|
| bare | nothing: the questions never say how recovery or mass pull is calculated, and no tag holds them |
| knowledge | `plant-knowledge/site-a-concentrator-1.md` appended to its system prompt: the flowsheet, the analyser streams, which assays make each number, the stop rule |
| skills | the same page plus Eleticle's analytical skill `site-analysis` and one line telling it to use the skill |

**The analytical skill is not open source and is not in this folder.** It is a written method for turning
historian data into numbers a metallurgist can trust: definitions first and asking when there is none, the right
resolution, running hours only, screening impossible hours, aggregating the way the plant does, checking what moves
with an input, splitting by conditions and testing a difference. It names no plant or stream. It was written on 23 Nov 2026
after the key was computed and follows the key's own procedure (hourly reads in chunks, screening impossible hours,
gold-weighted periods, thirds, a week-block bootstrap), so the skills condition tests whether the model follows the
site's method when it is written down, not whether the method was found independently. It was checked for mechanics on
two grinding questions (`dev.yaml`), never on the test questions. `run.sh` takes its folder from `SKILLS_DIR`; without it, the skills condition cannot run.

## Files

| File | What it is |
|---|---|
| `questions.yaml` | The four test questions |
| `make_key.py`, `key.json` | The key through the same tool code before any run (p1 uses No. 20's key) |
| `plant-knowledge/site-a-concentrator-1.md` | The plant knowledge page, as given to the agent |
| `frozen.sha256` | Hashes taken before the runs, of the files as run, at their paths in our working repository (`articles/<slug>/public/`). Entries for files changed since no longer match: the published key (values or points removed, see the comments in the file), the scripts (only to find the other articles' folders in this repository's layout, 24 Nov 2026) and No. 18's `mcp_server.py` (a statistics fix, 24 Nov 2026); the skill's hash is included, its text is not |
| `run.sh`, `models.json`, `prompt.md`, `answer.py` | The run |
| `dev.yaml` | The two development questions for the skill (grinding at Site C); never scored |
| `answers/` | Every attempt's tool calls and answer |
| `verdicts.yaml` | right, asked or wrong for each attempt, with the reason. `slip: true` marks four answers that met their question's rule and still hold an error we found (a slope given as 62 for 3.8, a window a day short twice, a reversed remark); they count as right |

## Run it

The environment is No. 19's (its README, "Run it": the stand-in and catalogue of No. 18, the agent's Python as
`AGENT_ENV`, Pi 1.5.2, bubblewrap, the model server and its settings).

- **The key, without a model:** with the stand-in running and crawled,
  `../historian-tag-catalogue-for-agents/.venv/bin/python make_key.py` (it reuses No. 20's reader). Its tags follow
  Zyfra's public record, so it repeats from public inputs.
- **Bare and plant knowledge:** `CONDITION=bare REPEATS=3 ./run.sh <run-name>` and `CONDITION=knowledge …`.
- **Knowledge and skill** (`CONDITION=skills`) needs the analytical skill, which is not published (`SKILLS_DIR` points
  at it), so that condition can be read here but not repeated.

## Rules (fixed before the runs)

p1: rougher streams and the two-product formula, overall relationship positive, low feed-grade third steeper than
high (or per tonne, said so, no clear difference). p2: rougher feed, final concentrate and final tail; running hours;
69.1 to 74.1 %. p3: rougher streams and the mass-pull formula; 31.1 to 36.0 %. p4: August 2026 by the plant's gold
recovery, feed grade within 0.3 of 5.9 g/t. Asked: no number given as the answer, the agent asks how the number is
defined. Asking counts above a wrong number.

## Licence

Code: MIT. Questions, key, plant knowledge page, answers and verdicts: CC BY 4.0.
