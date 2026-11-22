# What does a local LLM know about minerals?

Two local language models answered the three mineral-domain tasks of a published test, MineralBench, three
times each: 976 questions rebuilt from the sources it names, 5,856 answers, and a side run of 1,200 more. A
script graded every answer, then every different answer was read beside its key by Claude, an AI reader ("the hand
check"). This folder holds the
test harness, every graded answer, the key, the hand-check rules and each correction with its reason, and the
script that turns them into the article's numbers. The article is at https://eleticle.com/articles/local-llm-mineral-knowledge/.

## Result

Scores out of 100 after the hand check, with the script's grade in brackets. Mineral-Term and
Mineral-Property: share of answers right. Geo-NER: entity-set F1 per answer, which balances entities missed
against entities wrongly added; it is not a share of answers right (an answer with every entity right and none
extra: 27B 153 of 600 and Flash Next 178 with the paper's prompt, 239 and 233 without its `[]`). Each question's three rounds are
averaged, then the questions. One property question, whose key names no value, is left out (see the hand
check).

| Model | Mineral-Term | Mineral-Property | Geo-NER | Mean (Weighted-Acc) |
|---|---|---|---|---|
| Qwen 3.8 27B | 51.2 (46.0) | 27.0 (24.9) | 53.0 (52.9) | 43.7 (41.2) |
| Qwen 3.8 Flash Next | 61.7 (53.7) | 41.6 (33.0) | 55.8 (55.7) | 53.0 (47.5) |
| Oracle (better of the two, per question) | 66.5 | 47.5 | 64.9 | 59.6 |

Mineral-Property by property, hand-checked:

| Property | 27B | Flash Next |
|---|---|---|
| streak | 55.6 | 68.5 |
| luster | 25.0 | 47.2 |
| hardness | 37.0 | 46.8 |
| crystal_system | 29.6 | 44.9 |
| colour | 13.6 | 39.4 |
| cleavage | 26.4 | 31.9 |
| element_list | 18.5 | 31.9 |
| specific_gravity | 10.2 | 21.8 |

The paper's other measures, computed as it defines them (section 3.3, weights from Tables 5 and 6), over the
three domain tasks only:

| Model | IC_m | GS_m | ST_m | Eff (req/s) | Eff_norm | Composite | Mean latency |
|---|---|---|---|---|---|---|---|
| Qwen 3.8 27B | 56.8 | 37.8 | 76.3 | 0.350 | 100.0 | 64.1 | 2.85 s |
| Qwen 3.8 Flash Next | 59.4 | 48.8 | 83.1 | 0.184 | 78.2 | 65.3 | 5.42 s |

GS and ST are spreads across tasks: over three tasks here, over six in the paper, so they do not compare with
its Table 8. Efficiency compares two deployments (model, weights, serving software and hardware, run at
different client concurrency), not two models.

**The prompt's ending.** The paper's entity prompt (its Listing A-3) ends with `Answer:[]`. A side run asked
the same 200 sentences with the ending cut to `Answer:`, everything else unchanged:

| Model | Geo-NER, ending `Answer:[]` | ending `Answer:` | Answers read as empty |
|---|---|---|---|
| Qwen 3.8 27B | 53.0 | 69.2 | 26.0 % → 5.2 % |
| Qwen 3.8 Flash Next | 55.8 | 67.9 | 17.0 % → 3.0 % |

The score rose on 102 of the 200 sentences for 27B and 101 for Flash Next, and fell on 40 and 33.

"Read as empty" counts answers from which the scorer kept no entity. Nearly all are empty brackets. A few wrote
something else: entities the scorer could not read (prose, a quoted or single-quoted list), entities under a label
the sentence did not ask for, which the scorer drops, or once a request for the missing text (Flash Next,
geoner-0041 round 2). With `Answer:[]`, 2 of 27B's 156 such answers (geoner-0003 round 0, geoner-0144 round 2)
and 8 of Flash Next's 102 (geoner-0145 and 0183 round 0; 0009, 0141 and 0188 round 1; 0006, 0041 and 0081 round
2); with `Answer:`, 1 of 31 (geoner-0189 round 1) and 1 of 18 (geoner-0016 round 1). Their scores stay as the
scorer gave them. In `results/rows.jsonl` every answer read as empty carries `"empty": "brackets"` (no entity
named) or `"text"` (one of these).

**Over time, beside the paper's thirteen models** (its Table 7, in `results/paper_tables.json`). When each model
first became public (weights or API, a preview included) and whether its weights are open, with sources, is in
`results/model_dates.json`. Only one of the paper's models, Qwen3-Max (API only, preview 5 Sep 2025), keeps its weights closed; the other seven it reached online
have open weights. Scores out of 100; the paper's from its own questions and script, the two here hand-checked
(script alone in brackets):

| Model | First public | Weights | Mineral-Property | Geo-NER |
|---|---|---|---|---|
| Qwen3-Max (paper) | 2025-09-05 | closed | 65.3 | 69.6 |
| DeepSeek V4 Pro (paper; best open on properties) | 2026-04-24 | open | 80.6 | 66.6 |
| DeepSeek V4 Flash (paper; best open on entities) | 2026-04-24 | open | 75.0 | 69.1 |
| Qwen3.5-27B, AWQ (paper) | 2026-02-24 | open | 20.8 | 34.7 |
| Qwen 3.8 27B (here) | 2026-08-14 | open | 27.0 (24.9) | 53.0 (52.9) |
| Qwen 3.8 Flash Next (here) | 2026-08-26 | open | 41.6 (33.0) | 55.8 (55.7) |

On properties the paper's five local models score 20.8 to 40.0 and its eight online models 56.1 to 80.6; on
Geo-NER 16.1 to 36.2 and 17.5 to 69.6. The two models here answered rebuilt questions graded by script and Claude, so their scores sit beside the
paper's, not in its ranking. In particular, Qwen 3.8 27B's scores here against Qwen3.5-27B's in the paper do not show
whether the newer model improved: the questions and the grading differ, and either can move a score more than that
gap. Running Qwen3.5-27B on these questions would answer it. A date marks when that model first became public: the
paper reached its online models through an API and does not say which revision it was served (Kimi K2 Instruct:
0711 or 0905; DeepSeek V4: the April preview or a later final release). In the
article's figure, dots that would touch (models released the same day) are moved a few pixels sideways.
Mineral-Term is left out: the scores here are much higher than any in the paper (its best model 31.0, its
all-model oracle 46.8), under different questions and grading, and nothing here separates those two causes.

## What was run

| | |
|---|---|
| Paper | Dan J., Li S., Yao H., Cong Y., Li B., Zhou H., *MineralBench: an evaluation benchmark of large language models for mineral resources*, Research Square preprint, 2026, [doi:10.21203/rs.3.rs-10717678/v1](https://doi.org/10.21203/rs.3.rs-10717678/v1), CC BY 4.0 |
| Tasks | The paper's three domain tasks, weight 2 each (its Table 5). The general tasks (ARC-Challenge, Math, MMLU-Sci) were not run |
| Qwen 3.8 27B | 2 × RTX 5080 (16 GB each) in a workstation; NVFP4 weights with a BF16 output layer; vLLM 0.27.1, tensor parallel 2 |
| Qwen 3.8 Flash Next | 4 × RTX 3090 (24 GB each) in a server; quantised weights; llama.cpp server with speculative decoding |
| Prompts | Listings A-2 (short answer) and A-3 (entities), word for word: `mineralbench/prompts.py` |
| Sampling | Temperature 0.7, top-p 0.95, top-k 50, repetition penalty 1.1, at most 2,048 tokens, 2 retries (its Table 4) |
| Rounds | 3 per question (its section 4.2), α_IC 0.5, γ_GS 0.5, γ_ST 2.0 |
| Thinking | Off (`chat_template_kwargs: {"enable_thinking": false}`): the prompts ask for "only the core answer" |
| Date | 9 Nov 2026 |

Client concurrency was 16 for 27B and 12 for Flash Next in the main run, so per-request latency includes
queueing on each server.

## The questions

The paper's question files are not public (the repository it names returned HTTP 404), so the three tasks
were rebuilt from the sources it names, at its sample counts (its Table 1):

- **Mineral-Term, 200:** a definition from Mindat's glossary, answered with the term. The glossary pages were
  read from the Internet Archive's copies, 2015 to 2026; 200 terms were drawn from a pool of 607, spread over
  initial letters (seed 42).
- **Mineral-Property, 576:** "For the mineral X, what is its *property*?", 72 for each of eight properties.
  Species and formulas from Mindat's open API (element lists are worked out from the formula, ordered by mass
  fraction, as the paper's example shows); crystal system, hardness, density, streak, colour and cleavage from
  Wikidata, where it holds them keyed to the Mindat ID; luster and the remaining gaps from webmineral.com.
- **Geo-NER, 200:** sentences from the OzROCK evaluation set (Enkhsaikhan et al., 2021; github.com/majiga/OzROCK),
  with its human-checked tags as the key: MINERAL, ROCK, LOCATION, STRAT, ORE_DEPOSIT, TIMESCALE. Only
  sentences with at least one tagged entity were drawn, and each prompt names the labels its key contains. That
  is an easier task than extracting from a report with no hint of what is in it.

`scripts/build_bench.py` and `scripts/build_geo_ner.py` build the three task files from those sources. The
source texts are not here: Mindat's definitions are Mindat's, and the OzROCK sentences come from their authors'
release. `results/keys.json` holds what the grading needs: the term, the property value, the entity spans.

The exact questions of this run come back, all 976 of them, from three input files in `data/raw/` (SHA-1):

| File the scripts read | What it must be | SHA-1 |
|---|---|---|
| `mindat_glossary.jsonl` | The cleaned 607-term glossary snapshot the run was drawn from (one `{"term", "definition"}` per line). A larger or later crawl gives a different sample | `1eaf02f222ed9303e4e0c05cf801d3cb331b1223` |
| `mindat_minerals.jsonl` | The 868-species property table | `8446d9fd0d581a8e89c48a86b6284130349c31c7` |
| `OzROCK_EvaluationSet.txt` | OzROCK's evaluation set as released | `84f45d977611a82d5e7318e812ca198bbb6b923b` |

With other versions of the first two, the scripts draw a new sample of the same shape (seed 42), not these questions.

## The hand check

Done by Claude, an AI reader, not a mineralogist. Rules: [`hand-check-rules.md`](hand-check-rules.md), written before
any answer was read. In short: the
answer is the first line the model wrote; terms count when they name the same concept (spelling variants and
accepted synonyms included); element lists count when the set of elements matches; hardness within 0.5 Mohs and
specific gravity within 3 %; luster, streak and colour when every value named is in the key; cleavage when the
quality matches; entities only by the same span, allowing case, plural, hyphen spacing, a leading article or a
possessive.

- Mineral-Term and Mineral-Property: all 3,274 distinct answers (each distinct pair of question and answer text,
  over both models and three rounds) were read. Geo-NER: every predicted span the script did not match, 484 spans
  in 138 of the 200 sentences, was read beside the key. 402 grades changed: 292 up, 110 down. 6 entity matches were added.
- Every change is in [`check.json`](check.json) with its reason. `score.py` applies them; nothing else changes a
  grade.
- The script's numeric check (`numeric_match`: 0.15 of 5 % of the key) matched within about ±0.75 % of the key,
  so "5" for a hardness of 5.5 scored 0. It could not read element names or formulas, and it gave credit for
  a value of the wrong property when the words overlapped (a hardness given as a crystal system). The hand
  check fixes these case by case.
- Where the key itself looked doubtful (18 questions, such as Diopside's specific gravity of 3.15 or a colour
  key that reads "Color", and 45 sentences with an entity left out of the OzROCK tags), the key was kept and the
  doubt recorded in `check.json` as `key_issue`.
- One of those keys names no value at all: Pseudograndreefite's colour is the word "Color". No answer can be
  graded against it, so `check.json` lists it under `excluded` and `score.py` leaves it out of every accuracy
  figure, script and hand-checked alike (575 property questions scored, not 576). Kept in, it gave Flash Next
  41.5 on properties and 27B 27.0. The other 17 doubtful keys are scored as they stand; without all 16
  doubtful property keys, Flash Next would score 42.6 and 27B 27.6.

## Files

| File | What it is |
|---|---|
| `results/rows.jsonl` | One row per request (7,056): run (`main` or `open_cue`), model, task, question id `q`, round, the graded answer as normalised by the evaluator, the script's grade, latency, tokens; on an entity answer read as empty, `empty`: `brackets` or `text` |
| `results/keys.json` | The key for every question |
| `check.json` | Every grade the hand check changed, with its reason; entity matches added; key doubts; the key left out (`excluded`) |
| `hand-check-rules.md` | The rules the hand check followed |
| `score.py` | Applies the check and writes `results/summary.json`. Python 3, standard library only |
| `results/summary.json` | Every number above, script and hand-checked |
| `results/paper_tables.json` | The paper's Tables 7 and 8 for its thirteen models |
| `results/model_dates.json` | Each model's first public release, open or closed weights, licence, parameters and sources |
| `mineralbench/` | The harness that ran the test: prompts, sampling, rounds, the script's scoring and the paper's metrics |
| `scripts/` | Build the task files from the sources above |

## Run it yourself

Recompute every number from the stored answers:

```bash
python3 score.py
```

Run the test on your own models: build the task files into `data/bench/` (the build scripts expect the
source data in `data/raw/`), then point the harness at any OpenAI-compatible endpoint:

```bash
python3 -m mineralbench.run --model <name> --base-url http://<server>:8088 \
        --tasks Mineral-Term,Mineral-Property,Geo-NER --concurrency 8
python3 -m mineralbench.run --model <name> --base-url http://<server>:8088 \
        --tasks Geo-NER --out-dir results_open --ner-cue open
python3 -m mineralbench.analyze
```

`analyze` gives the script's grades. Read the answers beside the key before trusting them.

## Licence

Code (`score.py`, `mineralbench/`, `scripts/`) under the MIT licence; results, key and check under CC BY 4.0.
The prompts in `mineralbench/prompts.py` are transcribed from the paper (CC BY 4.0; cite it). Mindat's
glossary, Wikidata, webmineral.com and OzROCK keep their own terms.
