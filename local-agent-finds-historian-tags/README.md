# Can a local 27B model find the right historian tags from a plain question?

Code, questions, key and every answer for the article at
https://eleticle.com/articles/local-agent-finds-historian-tags/ (No. 19). It runs on No. 18's stand-in historian,
catalogue, MCP server and skill (`../historian-tag-catalogue-for-agents/`).

## What was run

- **Model:** Qwen 3.8 27B (4-bit weights, `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead`) served on this machine with an
  OpenAI-compatible API on port 8088 (`models.json`).
- **Agent:** the Pi agent harness 1.5.2, a fresh session per attempt, No. 18's skill loaded with
  `/skill:historian-tags`, No. 18's MCP server over streamable HTTP with an API key, and one added line
  (`prompt.md`). Python 3.12 with pandas 3.1.1, numpy, matplotlib 3.11.2, scipy 1.18.1 for charts.
- **Fence:** each attempt in bubblewrap: the repositories, keys and other attempts hidden; the attempt's folder
  writable; the run's dataset files, the agent's Python and the skill read-only (`run.sh`).
- **Stand-in:** No. 18's mock historian with 31 sites × 5 concentrators (50,594 tags), clock at 23 Nov 2026 00:00
  (AEST); No. 18's catalogue as scored there. One change to No. 18 before these runs: energy counters integrate their
  meter's power (No. 18's README).

## Files

| File | What it is |
|---|---|
| `questions.yaml`, `questions.prompt.md` | The 24 questions, written by Codex (gpt-6.2-astra, xhigh) from a plant description, and its prompt |
| `make_material.py`, `material.json` | The six point codes and eight unhealthy tags the question writer was given, picked by a seeded script |
| `make_key.py`, `key.json` | The key: tags from the plant generator; for "across" questions, the winners from the historian's own summaries read through the same tool code |
| `frozen.sha256` | Hashes taken before the runs, of the files as run, at their paths in our working repository (`articles/<slug>/public/`). Entries for files changed since no longer match: the published key (values or points removed, see the comments in the file), the scripts (only to find the other articles' folders in this repository's layout, 24 Nov 2026) and No. 18's `mcp_server.py` (a statistics fix, 24 Nov 2026) |
| `run.sh`, `models.json`, `prompt.md`, `answer.py` | The run |
| `sheet.py` | Builds the reading sheet and `attempts.json` (tags read, tool calls, seconds, charts) from the event logs |
| `attempts.json` | Every attempt's facts |
| `answers/` | Every attempt's tool calls and final answer (`<question>-<repeat>.md`) |
| `verdicts.yaml` | Pass or fail for each attempt, read by hand beside the key, with the reason |
| `dev.yaml` | Two of No. 18's development questions used only to check the harness; never scored |

## Rules (fixed before the runs)

read, compare, code: reads every key tag and reports its values, with a chart when asked. across: names the key's
winner for the window it states. ambiguous: asks which one, or lists at least two valid readings, instead of
silently picking one. unhealthy: says the tag cannot be used and gives no value from it as a reading. Any key tag
marked unhealthy must be called out. Bar: the median repeat passes 18 of 24, and no invented tag.

After Codex's check of the verdicts, the last rule was applied by the letter to the vague questions' candidate tags
too: four answers fail by it (`FAILS` in `write_verdicts.py`). Before that the count was 72 of 72.

## Limits

One model and one stand-in historian whose names are tidier than most sites'; 20 of 24 questions name a site (the four code questions give only a code); three
repeats; one reader of the answers. Values in the answers come from the stand-in: real hourly averages (Zyfra's
and a private plant's) with generated records, not published as data here.

## Means quoted from our tool

No. 18's `get_timeseries` returned a per-tag mean, minimum and maximum taken over every summary column the agent
asked for together (Average with Minimum, Maximum or Count). Seven answers quoted such a mean where it was 1 to 24 %
off the averages: t03/1, t04/1, t10/2, t11/2, t11/3, t19/1, t19/3 (each verdict says by how much). The rules score
tags, not values, and the winners named in t10 and t11 are the same on the averages, so no verdict changes. The tool
is fixed since (No. 18's README, 24 Nov 2026); these runs used the earlier version.

## Licence

Code: MIT. Questions, key, answers and verdicts: CC BY 4.0.
