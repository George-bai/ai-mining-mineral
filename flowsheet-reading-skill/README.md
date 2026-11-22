# Does a written skill help a local LLM read a whole plant flowsheet?

Code and data for article No. 08 at [eleticle.com](https://eleticle.com/articles/flowsheet-reading-skill/). It
follows [No. 06](../flowsheet-to-mermaid-local-llms/), in which two local models redrew four flowsheets as Mermaid
charts with no help.

Here the same two models, Qwen 3.8 27B and Qwen 3.8 Flash Next, read the two whole-plant drawings of No. 06 (Phoenix
mine mill and Twin Creeks mine) three times with a flowsheet-reading skill and three times without it. Each chart was
scored against an answer key of the drawing's units, streams and loops, and every chart was checked by hand.

**Finding.** On each drawing, all three Flash Next attempts with the skill found more streams than any attempt without it
on that drawing, and drew fewer wrong lines, in about twice the time. The 27B model was run twice (its first run shared
its server): each run found more streams with the skill on one drawing of the two, not the same one, with about as many
wrong lines, at ten to fifteen times the time.

## Result

Streams found of 90 scored streams per drawing, one number per attempt (repeats 1, 2, 3). A chart that is not valid
Mermaid counts as no chart; its score on a repaired copy (`repair.py`) is in brackets where the repair works.

| Model | Condition | Phoenix | Twin Creeks | Streams, of 540 | Valid charts | Wrong lines per valid chart | Minutes per attempt |
|---|---|---|---|---|---|---|---|
| Flash Next | no skill | 45, 52, 50 | no chart, 65, 62 | 274 | 5/6 | 32.2 | 7 to 16 |
| Flash Next | skill | 61, 66, 68 | 75, 77, 79 | 426 | 6/6 | 19.3 | 22 to 26 |
| 27B (rerun) | no skill | 26, 26, 26 | 37, 34, 37 | 186 | 6/6 | 32.8 | 1 to 2 |
| 27B (rerun) | skill | 37, 41, 37 | 34, 45, 50 | 244 | 6/6 | 34.8 | 12 to 44 |

Wrong lines per attempt (lines in the chart that are not a stream of the key, after pairing):

| Model | Condition | Phoenix | Twin Creeks |
|---|---|---|---|
| Flash Next | no skill | 38, 36, 37 | no chart, 25, 25 |
| Flash Next | skill | 29, 23, 23 | 14, 17, 10 |
| 27B (rerun) | no skill | 28, 36, 38 | 31, 35, 29 |
| 27B (rerun) | skill | 36, 41, 41 | 33, 29, 29 |

Loops closed, of 11 on Phoenix and 12 on Twin Creeks: Flash Next 0, 2, 4 and none, 7, 5 without the skill; 5, 4, 6 and
6, 7, 6 with it. 27B (rerun) 0, 1, 0 and 0, 0, 0 without; 1, 0, 1 and 0, 0, 2 with it. Every number per attempt, with the
items found, lines right and minutes, is in `results/results.json`.

**Flash Next.** Every skill attempt beats every no-skill attempt on both drawings, on streams and on wrong lines:

- Phoenix: 61 to 68 streams with the skill, 45 to 52 without; 23 to 29 wrong lines against 36 to 38.
- Twin Creeks: 75 to 79 against 62 to 65, plus one chart that does not draw; 10 to 17 wrong lines against 25.
- Time: 22 to 26 minutes an attempt against 7 to 16. The two conditions ran side by side on one server.
- The invalid chart (no skill, Twin Creeks, attempt 1) writes ten arrows as `--|label|`, which `repair.py` does not
  cover. Even if it had scored as well as the best no-skill Twin Creeks attempt (65), it would stay below the lowest
  skill attempt (75).

**27B, rerun.** More streams on Phoenix, level on Twin Creeks and on wrong lines, fifteen times slower:

- Phoenix: every skill attempt is above every no-skill one, 37 against 26 at the closest (37 to 41 against 26 in each).
- Twin Creeks: the ranges overlap, 34 to 50 against 34 to 37.
- Wrong lines: 34.8 per chart with the skill, 32.8 without.
- Time: 12 to 44 minutes an attempt against 1 to 2 (23.0 against 1.6 on average). Four of the six skill attempts were
  stopped once by the loop guard and restarted; their minutes include both tries.

Its first run gave the other drawing (see "The 27B, run twice"): with three attempts a condition, which drawing the 27B
gains on is not settled. Its total streams rose with the skill in both runs.

**Without the hand corrections** (the scorer alone, each `check.json` set aside), the same pattern holds. Flash Next:
Phoenix 58 to 61 against 45 to 49, Twin Creeks 70 to 73 against 58 to 60. 27B rerun: Phoenix 32 to 37 against 23 to 24;
Twin Creeks overlaps, 32 to 49 against 33 to 37 (first run: Twin Creeks 38 to 52 against 30 to 35, 31 repaired; Phoenix
overlaps, 24 to 36 against 22 to 28).

In the test no attempt was restarted, stopped by a guard or voided by a server fault. In the 27B rerun four skill attempts
were stopped once by the loop guard and restarted, and five attempts were voided because another client's requests ran on
the server during them, then run again alone (below).

## The 27B, run twice

**Why.** During the test, two stray development attempts of ours (27B, slide 41), stopped from outside at about 3:50 am
AEST on 16 Nov, kept running inside the fence and called the 27B's server until they were found and killed at 5:05 pm.
No turn failed, but every request ran slower. George chose a rerun. Before it started, the rule was written and committed
(`development.md`, "27B rerun on a quiet server"): the rerun replaces every 27B number, scores and minutes together,
whatever it shows; the first run is kept here, labelled; an attempt during which another client's request ran on the
server is void and is run again alone, once. Same frozen files, same server start, 16 Nov 2026, 7:15 to 11:14 pm AEST.

**Three readings, by the page's rule** (a gain only when every attempt with the skill beats every attempt without):

| Reading | Phoenix | Twin Creeks | Gain on |
|---|---|---|---|
| First run (shared server) | 26, 41, 36 against 26, 24, 30 | 52, 54, 40 against 36, 31, no chart (33) | Twin Creeks |
| Rerun, first 12 before the voids | 37, 33, 39 against 26, 26, 26 | 48, 45, 50 against 37, 35, 37 | both |
| Rerun as counted | 37, 41, 37 against 26, 26, 26 | 34, 45, 50 against 37, 34, 37 | Phoenix |

**The five void attempts** (other requests on the server during them: 1 to 18 small requests, about 70 s of server time in
all), hand-checked before they were voided, and their runs alone:

| Attempt | Void | Run alone |
|---|---|---|
| Skill, Twin Creeks, repeat 1 | 48 streams, 22 wrong lines, 19.2 min | 34, 33, 18.2 min |
| Skill, Phoenix, repeat 2 | 33, 40, 23.9 min | 41, 41, 44.2 min |
| No skill, Twin Creeks, repeat 2 | 35, 28, 3.1 min | 34, 35, 1.4 min |
| Skill, Twin Creeks, repeat 2 | 45, 33, 17.5 min | 45, 29, 12.1 min |
| Skill, Phoenix, repeat 3 | 39, 44, 24.6 min | 37, 41, 28.2 min |

**Quiet, checked.** The server's completed-request counter was read before and after; per attempt, the requests in the
router's log equal the model turns in the attempt's own log. Outside requests came from another client, at 7:49 to 8:49 pm
(28 small requests) and at 10:55 pm (6 requests, about 5 s of server time, during the run alone of skill, Phoenix, repeat
3, which stands by the rule). No request failed.

**Speed.** Median output per request, rerun against first run: 58.4 against 49.1 tokens a second with the skill, 59.6
against 50.6 without. The stray attempts had slowed every first-run request by about a sixth. Minutes per attempt are not
the clean comparison: the rerun's skill attempts looped more often until the loop guard stopped them (four of six,
against none in the first run, whose logs show the same loops ending in time).

**The first run's numbers** (in `results/qwen38-27b-first-run/`): streams 147 without the skill (180 with the repaired
copy) and 249 with it; wrong lines per valid chart 36.0 and 33.7; 1 to 5 and 14 to 28 minutes an attempt. Its Twin Creeks
wrong lines here are 1 or 2 lower than first published (35, 36, 34 repaired without the skill; 28, 27, 39 with it, now 34,
35, 33 and 27, 26, 37): a hand-check call written during the rerun (a 'Trash Screen' between the jaw crusher and the
radial stacker, where the drawing has none, pairs with nothing; `reference/README.md`) was applied to both runs. It moves
no stream count and no verdict.

## The skill

`flowsheet-reading/` is the skill, in the Agent Skills format: `SKILL.md` and four scripts. Pi, and
other agents that read that format, can load the folder as it is. It tells the model to read the drawing the
way an engineer does, piece by piece at full size, writing notes after every look:

1. Look at the whole drawing once and write an overview: areas, legend, where the feed enters and products leave.
2. Cut it into overlapping tiles with rulers in drawing pixels (`scripts/tile.py`).
3. Read every tile in order. Copy each label as written; zoom in (`scripts/zoom.py`, at most 60 zooms) wherever lines
   meet, cross, split or end, and on any small label.
4. List the units, with repeats kept apart by position.
5. Trace the streams: follow the ore from feed to product and tailings, then water, solutions, reagents, carbon and
   gas, then every recycle.
6. Write the Mermaid chart: one box per unit, one line per stream, only what is drawn.
7. Check it (`scripts/check.py`): units with no line in or out, units missing from the chart, lines that may not be
   valid Mermaid.

`scripts/next.py` leads: it names the one step to do now and will not move on while a step is undone. The scripts need
Python 3 and Pillow.

**How it was made.** Written and tuned only on other drawings: slides 41, 47 and 48 of the same lecture, and the
process flowsheets (Figure 17-1) of two public technical reports, the 2024 NI 43-101 reports for Macraes (OceanaGold)
and Detour Lake (Agnico Eagle). Each development drawing had its own answer key. Those drawings and keys are not
published. Six versions, one change at a time, each scored on the development drawings and checked by hand:

| Version | What changed |
|---|---|
| v1 | Seven steps, with `tile.py` and `check.py`. Four reading orders tried for step 5: follow the ore, area by area, unit by unit, tile by tile |
| v2 | Rulers in drawing pixels on every tile and a notes file with a section per tile; `zoom.py`; units noted with their positions; lines leaving a tile noted and joined; streams written unit by unit, so each shows at both ends |
| v3 | Inches written as `in`, and `check.py` flags a quote inside a label, after one inch mark broke a whole chart |
| v4 | `next.py` leads the steps and refuses to skip one; `zoom.py` refuses a region already zoomed, after the 27B ran one zoom 830 times |
| v5 | Zoom on every junction, crossing and small label before writing a tile's lines; every stream needs both ends in the notes; at most 60 zooms |
| v6 | `zoom.py` gives a region already shown back once, then closes it with the next step, and allows zooming out |

Follow the ore is the reading order in the frozen skill. Two guards were added to the harness on the way, the same in
both conditions: `loop-guard.ts` and one restart in `run.sh` for a run that ends with no chart.

On the five development drawings (two attempts each, ten per model), v6 against two no-skill rounds:

| Model | Streams, v6 | Streams, no skill | Wrong lines, v6 | Wrong lines, no skill | Minutes, v6 |
|---|---|---|---|---|---|
| Flash Next | 414 | 382 and 397 | 85 | 106 and 129 | 20 to 32 |
| 27B | 297 | 218 and 251 | 170 | 172 and 180 | 5 to 58 |

The 27B minutes of round 10 were measured with the same two stray attempts on its server (see "The 27B, run twice"). On those smaller
drawings Flash Next's streams were only just above its two no-skill rounds; its fewer
wrong lines held. On the test drawings its stream gain is larger than its spread between repeats.

George stopped the tuning on 16 Nov 2026 ("Stop here and run tests"). v6 was frozen at 10:52 am AEST with the whole
harness (hashes below), and the test runs started at 10:53 am AEST.

## What is here

| File | What it is |
|---|---|
| `flowsheet-reading/` | The skill (MIT) |
| `prompt.md` | The whole instruction, the same in both conditions. With the skill it is preceded by `/skill:flowsheet-reading` |
| `models.json` | Two example model endpoints in Pi's format. Copy it and put in your own addresses and model names |
| `run.sh` | Runs each model on each drawing, with the skill or without, each attempt fenced in (see below) |
| `interleave.sh` | Runs the conditions in turn for each repeat and drawing, so any drift in a server falls on both |
| `image-limit.ts` | Pi extension: at most two images per request (the drawing and the newest), as both servers accept |
| `loop-guard.ts` | Pi extension: stops a model that repeats one call or sweeps a zoom box, and nudges one that stops before writing the chart. The same in both conditions |
| `render.py` | Draws each chart with Mermaid 11.4.0 in headless Chrome; writes `mermaid.svg` and `mermaid.json` (the chart as Mermaid's own parser reads it) |
| `repair.py` | For a chart that does not parse: a copy with quote marks and brackets in labels fixed. Reported beside the result, never as it |
| `score.py` | Scores each chart against its key; `show` prints a chart beside its key for the hand check; `test` checks the scorer |
| `reference/` | The two answer keys, their rules (`README.md`) and the record of how they were made and settled (`log.md`) |
| `results/` | `<condition>/<model>/<drawing>/<repeat>/`: the chart (`flowsheet.mmd`, `mermaid.svg`, `mermaid.json`), its score (`score.json`), the hand check (`check.json`) and the time (`seconds.txt`). `repaired/` holds a repaired copy where one was made. `results.json` has one row per attempt. The 27B's rows are its rerun; `qwen38-27b-first-run/<condition>/<drawing>/<repeat>/` holds its first run, with its own `results.json` |

## Run it yourself

You need: two OpenAI-compatible endpoints serving vision models; Node 22.19 or later and [Pi](https://pi.dev/) 1.5.2
(`npm install -g --ignore-scripts @earendil-works/pi-coding-agent@1.5.2`); bubblewrap (`bwrap`), which `run.sh` uses to
fence each attempt in; Python 3 with Pillow and PyYAML; and Google Chrome with internet access for `render.py`, which
loads Mermaid from jsDelivr. The drawings are built by No. 06's `prepare.sh` from the lecture PDF (link under Sources).
Run everything from this folder.

```bash
# 1. The drawings: slides 39 and 37, cropped to the figure
../flowsheet-to-mermaid-local-llms/prepare.sh Flowsheets.pdf drawings

# 2. Both conditions, interleaved, three repeats. MODELS lists provider/model from your copy of models.json
MODELS_JSON=my-models.json MODELS=qwen27b/qwen38-27b REPEATS=3 ./interleave.sh test noskill flowsheet-reading -- \
  drawings/figures/p39-phoenix-mine-mill.png drawings/figures/p37-twin-creeks-mine.png

# 3. Draw, repair what does not parse, score
for r in ../local/runs/test-noskill ../local/runs/test-flowsheet-reading; do
  python3 render.py $r && python3 repair.py $r && python3 render.py $r && python3 score.py reference $r
done
```

`score.py test` and `score.py show` look for the keys one folder up (`../reference`, as in the article's working
folder). From this repository, link them there first: `ln -s flowsheet-reading-skill/reference ../reference`.

**The fence.** `run.sh` starts each attempt in bubblewrap: its own `/tmp`, home read-only, other repositories and runs
out of sight, and the folder above this one hidden whole (in this repository, the repository itself, with this folder's
`reference/`, `results/` and README). The attempt sees its own folder and Pi's config, writable, and the two extensions
and, with the skill, `flowsheet-reading/`, read-only; the model endpoints stay reachable. The answer keys were outside
the fence during the runs. Pi starts with a clean configuration: no skills except the one given, no context files, no
extensions but the two above, no prompt templates, offline.

A run writes the drawing, your model configuration and Pi's raw logs (which hold the drawing) into `../local/`. Keep
them out of any commit. To stop a run early, kill the process group of `run.sh` (or `interleave.sh`), then check that no
`pi` process is left: killing only the fence leaves Pi running.

## How it was run

| | |
|---|---|
| Agent software | Pi coding agent 1.5.2 in print mode, Node 24.22.3. Standard tools (read, bash, edit, write) |
| Qwen 3.8 27B | `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead` (4-bit NVFP4 weights; the revision of No. 06, not read again), served with vLLM 0.27.1 on 2 × RTX 5080 (16 GB each): GPU memory 0.92, context 165,000 tokens, the FP8 FlashInfer kernel off, 120-second step timeout, at most 2 sequences, default sampling temperature 0.6, top-p 0.95, top-k 20. Pi: 96,000-token window, 32,768 output tokens. One attempt at a time. First run with two stray development attempts of ours calling the same server; rerun with the server to itself but for a few requests from another client (see "The 27B, run twice") |
| Qwen 3.8 Flash Next | The server of No. 06 (its README gives the files, the serving software and the settings), not inspected again: context 262,144 tokens as reported on the day, its own defaults. Pi: 262,144-token window, 32,768 output tokens. Two attempts at a time, the two conditions of one drawing and repeat side by side |
| Sampling | None sent by the runs |
| Input | The cropped drawing (200 dpi) attached to the instruction |
| Dates | Development 15 and 16 Nov 2026. Test runs 16 Nov 2026, 10:53 am to about 2:50 pm AEST; 27B rerun 7:15 to 11:14 pm AEST |

Times compare the complete setups (model, weights, server and hardware together), not the models alone.

**Frozen before the test** (SHA-256, 16 Nov 2026, 10:52 am AEST; unchanged after the runs but for `run.sh`, below the table):

| File | SHA-256 |
|---|---|
| `flowsheet-reading/SKILL.md` | `80580cb2c31217ff132fe402a5a4153c60caedb67be5b7bff87accc1d6ae77cd` |
| `flowsheet-reading/scripts/check.py` | `de18006f54e2b250cffb16114171ced70d797be82639c71beb9a37db3604fa76` |
| `flowsheet-reading/scripts/next.py` | `bb8618d0d5df6dd91fb786faa7e1fa03aeb78cadd1c6691194ea17b5e3002a84` |
| `flowsheet-reading/scripts/tile.py` | `c9dfcf760bc7b314bbad60ed11952e4b24a1dede300b06a969cbe0550af084ec` |
| `flowsheet-reading/scripts/zoom.py` | `07d4d237867925441cd1bfae06334270a74a0a46cc73632cdd0c35733b3b7d7e` |
| `prompt.md` | `8c7737fc852cb06146a8b0a57e5fb3238bf8e339a709abbb413c25581728df9f` |
| `run.sh` | `549af2b3511db7b15b108ae7d047db0145bda5476335d3939804976794122661` |
| `interleave.sh` | `fc94f377069bf8c0a5715275c29ab14bf1eaefa811f36f832e5bf93435ddc889` |
| `image-limit.ts` | `0c6cda30dc509608208c4768590b2ceeaffccf0d7f79c0a3b52a502256b76b94` |
| `loop-guard.ts` | `6d62c903a4a34a1a2480eb6b8e88dc05c85af03840d41fb905841331114beb88` |
| `score.py` | `87ad869c51b34498b87b278103086eb05011b67885364783f4b371f6ac000c2f` |
| `render.py` | `be2ccc9a3608644bcb21bb9f0e8f3cdfdafde90cf01100afee90ccafff657e13` |
| `repair.py` | `ec1493915464aaeaacdfce56effef32d800dd137066e505552b4e83330cab708` |
| `reference/p39-phoenix-mine-mill.yaml` | `5991c8dd0ef53d3faeb72650dddf48515f8ae997c3a021a0746db61239c7ee31` |
| `reference/p37-twin-creeks-mine.yaml` | `33a4324722922fb8688d3cce7346f4ee7191a90370b70ae5b5776f2239fa4b76` |
| drawing `p39-phoenix-mine-mill.png` | `d50ef5e3e75808ff4b263d40dc5d5b687eda3d33e0ea83ab038c1089ada6b071` |
| drawing `p37-twin-creeks-mine.png` | `0fc9dd2744da71739676fe1711c7f1f244479950f1d6a23026250f964b9f3c9a` |

`run.sh` here is not the frozen file; the hash above is the one the runs used. On 20 Nov 2026 its fence was narrowed, so
that a rerun from this repository, where the keys and results sit beside it, cannot read them. The frozen fence showed
this whole folder, read-only (it held neither `reference/` nor `results/` then), and with no skill laid an empty folder
over `flowsheet-reading/`. Nothing else in `run.sh` changed.

`models.json` here differs from the file the runs used only in its endpoint addresses.

## Scoring

**The answer keys** (`reference/`) list each drawing's units, inputs, outputs, junctions and carriers, its streams and
its main loops. Two readers, Claude and Codex, listed each drawing apart; every difference was looked at again on the
drawing and settled, and each reader then checked the agreed key once more. The keys were frozen before any test run.
What cannot be read with confidence is marked unsure and not scored. Phoenix: 90 scored streams and 11 loops; Twin
Creeks: 90 and 12.

**The scorer** (`score.py`) pairs each box of a chart with key items by its label, then, for repeated labels, by the
chart's own words for where the box sits and by its lines. Junctions, carriers and boxes that match nothing are passed
through, so A → sump → B counts as A → B. Streams found: key streams the chart has. Wrong lines: chart lines that are no
key stream. Loops found: key loops whose every step the chart has.

**The hand check.** Every chart was read beside its key and the drawing. Where the scorer paired a box wrongly, the
right pairing and the reason are written in its `check.json`, by the rules in `reference/README.md` (some dated: they
were written down as the checks went on, and applied alike to both conditions). Every box whose label is not exactly its
key item's, or that pairs with nothing or with several items, and every box paired with a repeated key label, was read
with its lines. In the test charts 18 pairings in 12 charts were set this way after a first pass had missed labels that
are only the start of the key's ('Lime' against Lime Silo); six charts moved by 1 or 2 streams. The 27B rerun's 12
charts were checked afresh by the same rules, also reading every key item paired with two boxes; one call was written down
during those checks and applied to both 27B runs (above).

**Rules fixed before the test.** A chart that is not valid Mermaid as delivered counts as no chart; its repaired score
is reported beside it. An attempt that ends on a server fault is void and run again (none was). A run with no chart
caused by the model counts, after the one restart `run.sh` gives both conditions (none was needed in the test; four
in the 27B rerun, all with the skill, each writing a chart on its restart). For the 27B rerun, written before it started:
it replaces every 27B number, and an attempt that had another client's request on the server is void and run again alone,
once.

**What the models could see.** No attempt read an answer key or another attempt's files. Two Flash Next attempts
without the skill (Phoenix, repeats 1 and 2) listed the folder from inside the fence and read the harness files both
conditions can see (`prompt.md`, `run.sh`, `image-limit.ts`, `render.py`, `loop-guard.ts`, the top of `score.py`); the
skill folder was empty to them and the keys were not there. Both stand. Without them, the one no-skill Phoenix attempt
left (50) is still below the lowest skill attempt (61).

## Limits

- Two drawings from one lecture, three attempts per model and condition. Enough to see Flash Next's gap, not to rank
  smaller differences.
- One frozen skill, one key per drawing. The keys and the hand checks are careful readings, not ground truth from the
  plants.
- On the smaller development drawings Flash Next's streams were only just above its no-skill runs; on these two the gap is clear.
- Flash Next's two conditions ran side by side on one server and slowed each other: the minutes compare the two
  conditions, not what the server can do alone.
- Two local models, the ones available on the day; not a survey.
- **The 27B, run twice.** Its first run shared the server with two stray development attempts of ours (each request about
  a sixth slower; no turn failed). The rerun's verdict differs from the first run's on both drawings, and one voided
  attempt alone would have changed it again: three attempts a condition do not settle the 27B per drawing. Its rise in
  total streams with the skill holds in both runs.
- The Twin Creeks drawing is 749 × 548 pixels in the PDF; its smallest labels are blurred at any zoom.

## Sources

The drawings are slides 39 and 37 of: Anderson, C. G. *Mineral Processing Flowsheets* (Lecture 6). Colorado School of
Mines. https://www.researchgate.net/publication/318502393_Flowsheets

They are not included here: they belong to their authors, and the original source of each drawing is not stated on the
slides. The article shows them with approval. No. 06's `prepare.sh` rebuilds them from the PDF.

## Licence

Code, including the skill: MIT. Results and answer keys (the files in `results/` and `reference/`): CC BY 4.0, for what
is ours in them. Each chart is a model's reading of a third-party drawing, and each key a reading by us; this licence
grants nothing over the drawings themselves, whose rights stay with their owners.
