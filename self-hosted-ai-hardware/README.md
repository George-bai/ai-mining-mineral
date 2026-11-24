# What hardware does a mineral-processing site need to self-host LLMs and expert models?

The code and data behind the article's calculator. Prices, versions and runs as of **15 November 2026**, Australia.
Budget: **A$100,000 including GST** for the whole machine: main card(s) for the language model, a separate
RTX PRO 2000 Blackwell 16 GB for vision, embeddings and reranking, the host, and power and network kit.

## What is measured and what is estimated

- **Measured:** 2,732 first-hand speed records were collected from GitHub (Strata and Project Maya issues, docs and
  release notes, community repositories), the LocalMaxxing public API and X. 1,010 of them, on comparable hardware and default settings, pass the checks in `evidence.md`. After the outlier pass, 784 one-stream runs feed the speed fits (555 writing and 363 reading speeds; 45 of the writing speeds at 128K or longer) and 120 multi-stream records are kept as concurrency evidence. `anchors.json` publishes 1,680: every GitHub and X record with its conditions, and
  the 753 LocalMaxxing runs the fit uses (fitted runs, outliers and concurrency sweeps) with the run link and the
  numbers used, without usernames or notes.
- **Estimated:** every speed the page shows. The model places each quantised file's dense weights, routed experts and
  lookup tables in VRAM, RAM or SSD and reads them at each part's speed, with a few constants per stack fitted to the
  runs (`fit.mjs`, `calibration.mjs`). The page shows the closest measured runs beside every estimate.
- **Priced:** Australian retail listings including GST, opened on 15 November 2026 (`hardware.md`). Not quotes.

## How close the estimates are

Each stack's constants are fitted to its runs, then checked on machines the fit had not seen: the runs are split into
five groups by machine (card, count and host), and each group is predicted from a fit to the other four. The band the
page shows is the 10th to 90th percentile of measured ÷ estimated on those held-out runs, at least ±15%. A stack with
fewer than eight held-out runs, or runs from fewer than three machines, gets at least ±30%, widened to what its
held-out runs show. Reading speed is fitted only to one-stream runs with prompts of 1,024 tokens or more.

<!-- accuracy -->
| Stack | Writing runs | Gap, fitted | Gap, held out (machines) | Band shown | Reading runs | Gap, fitted | Gap, held out (machines) | Band shown |
|---|---:|---:|---:|---|---:|---:|---:|---|
| Strata | 224 | 16% | 18% (56) | 0.68–1.42 × | 117 | 30% | 38% (35) | 0.33–1.46 × |
| Project Maya | 128 | 27% | 34% (36) | 0.61–1.79 × | 114 | 47% | 63% (34) | 0.40–2.01 × |
| vLLM | 77 | 7% | 9% (12) | 0.78–1.38 × | 68 | 35% | 35% (6) | 0.58–1.68 × |
| SGLang | 6 | 0% | 20% (1) | 0.70–1.74 × | 14 | 2% | 128% (1) | 0.70–2.88 × |
| llama.cpp | 120 | 6% | 8% (21) | 0.83–1.15 × | 50 | 46% | 85% (5) | 0.35–2.26 × |
<!-- /accuracy -->

A gap is how far the median run is off, as a ratio either way: exp(median of |log(measured ÷ estimated)|) − 1, so
35% means the median run is 1.35 times faster or slower than estimated. The page shows the same measure. Every run's measured and fitted value is
in `fit-report.json`. Runs more than 2.5× from a first fit are listed there as outliers and left out of the second fit,
mostly mislabelled harness rows.

## The three starting machines (one stream, 128K context)

Written by `build-page.mjs` from the calculator. Each model runs as the largest quantised version that
fits the machine and keeps 20 tokens per second, else the fastest that fits (the page's own rule). Prices include the
tools card and the power and network kit; the 10GbE card is left out where the board has 10GbE (Small, Large). They
are the 15 November listings: on 22 November e365 listed the Max-Q at A$27,999 on backorder, A$3,000 more a card,
which makes Medium A$46,568 and Large A$85,906.

<!-- machines -->
| | Small | Medium | Large |
|---|---|---|---|
| Main cards | 1 × PRO 4500 32 GB | 1 × PRO 6000 Max-Q 96 GB | 2 × PRO 6000 Max-Q 96 GB |
| Host | DDR5 desktop, 128 GB | Used EPYC server, 256 GB ECC | Threadripper PRO, 256 GB ECC |
| Price incl. GST | A$16,675 | A$43,568 | A$79,906 |
| Qwen3.8-27B | 32 (23–56), 4-bit NVFP4 · 24 GB | 58 (40–101), 4-bit NVFP4 · 24 GB | 88 (61–153), 4-bit NVFP4 · 24 GB |
| Gemma 4 26B-A4B | 72 (56–99), 4-bit NVFP4 · 19 GB | 113 (89–156), 4-bit NVFP4 · 19 GB | 151 (118–208), 4-bit NVFP4 · 19 GB |
| Gemma 4 31B | 27 (22–31), 4-bit GGUF · 18 GB | 48 (40–56), 4-bit GGUF · 18 GB | 48 (40–56), 4-bit GGUF · 18 GB |
| Qwen3.8-Flash-Next | 59 (40–84), 4-bit · 82 GB + 29 GB table | 196 (134–277), 4-bit · 82 GB + 29 GB table | 177 (121–251), 4-bit · 82 GB + 29 GB table |
| GLM-5.3-Flash | 30 (18–54), 3-bit mixed · 116 GB | 56 (34–101), 3-bit mixed · 116 GB | 83 (50–148), 3-bit mixed · 116 GB |
| DeepSeek-V4.1-Flash-1017 | 26 (18–37), 2.25 bits · 155 GB + 111 GB table | 61 (37–108), 2–3-bit mixed · 178 GB + 162 GB table | 80 (48–142), 2–3-bit mixed · 178 GB + 162 GB table |
<!-- /machines -->

## Files

| File | What it is |
|---|---|
| `models.md` | The six models, the quantised files offered (pinned revisions), their expert/dense/table split, what is altered |
| `stacks.md` | Strata, Project Maya, SGLang, vLLM, llama.cpp: versions, placement, drafting, concurrency, context; the measured comparison |
| `hardware.md` | Card prices, every host's parts list with sources, physical fit, power and the budget ceiling |
| `method.md` | The model, the fit, the concurrency and context rules, and the limits |
| `evidence.md` | Where the runs come from, what was kept and left out, and the corrections to the earlier draft |
| `catalog.mjs`, `calculate.mjs`, `draw.mjs` | The page's catalogue, model and figures (identical to the page's copies) |
| `calibration.mjs` | The fitted constants (written by `fit.mjs`) |
| `anchors.json` | The published first-hand records, with `fit`, `why` and `outlier` marks; refitting from it gives the same constants |
| `fit-report.json` | Measured against fitted, per run |
| `cards.mjs` | Specifications of every card that appears in the runs |
| `stack-comparison.json` | The measured pairs drawn in section 03 |
| `fit.mjs`, `build-page.mjs` | Rebuild the fit and the page's data and static figures |
| `check.mjs` | The calculator's answers on the cases of the 22 November review |

## Rebuilding

```sh
node fit.mjs          # refits calibration.mjs from anchors.json and writes fit-report.json
node build-page.mjs   # writes data.json and the static figures, and the tables in README.md and hardware.md
node check.mjs        # checks the calculator on the review cases listed in it
```

In the authoring repository `build-page.mjs` writes into the article's `page/` folder and fills the page's static
numbers; in this folder on its own it writes `data.json` and the figures into `out/`.

Node 20 or newer, no dependencies. The page's code lives in the article's `page/` folder and is copied here.
`check.mjs` runs here on its own; the authoring repository's own tests, which are not published, run it too and also
check that the copies match and the page's words.

## Limits

- Speeds are for the stacks' default settings: Strata's MTP drafting, Maya's MTP (two or more cards) and DSpark
  (DeepSeek); the whole-model servers without a drafter. Altered settings (Turbo, five-of-six experts, abliteration,
  the non-commercial DFlash2 drafter) are left out.
- Most runs use short questions. Reading speed, long contexts and many users at once have fewer runs; test the site's
  own documents and load before buying.
- Answer quality after quantisation is not measured here; see the quant publishers' own comparisons in `models.md`.
- Prices are listed retail prices on one day, whether or not the item was in stock; freight, assembly and installation
  are not included. Stock and quantity limits are noted in `hardware.md`.
- SGLang's runs all come from one user's RTX PRO 6000 Server Edition, reported on LocalMaxxing. They are used as
  reported; with one machine nothing can be held out, so its band is the wider fixed one. Its held-out gaps in the
  table are predictions made without any of its own runs: they say nothing about other machines.
- LocalMaxxing's terms (updated 4 October 2026) leave ownership with the submitters and grant no licence to
  redistribute the run data. Its runs are therefore cited one by one: only those the fit uses, with the run link and the
  numbers used. The full pull of 1,805 runs is not published.

## Licence

Code: MIT. Compiled data and text: CC BY 4.0. Source posts, model cards and retailer pages keep their own terms.
