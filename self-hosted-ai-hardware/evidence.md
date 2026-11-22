# Evidence: the first-hand runs

2,732 speed records were collected, one per measured point (a sweep of prompt lengths or streams is several records
sharing `run_group`). Numbers are copied as published; unknown values are null. `anchors.json` publishes 1,680 of them:
every GitHub and X record, and the 753 LocalMaxxing runs the fit uses. Refitting from the published file gives
the same constants as refitting from all 2,732.

| Source | Records collected |
|---|---:|
| LocalMaxxing public API (`/api/speed-tests`, latest runs per model; 753 published) | 1,805 |
| Project Maya GitHub issues and README tables | 363 |
| Strata GitHub issues, docs, release notes and benchmark results | 504 |
| Community GitHub repositories | 47 |
| X posts (read through api.fxtwitter.com) | 13 |

GitHub and X records keep their authors' handles, as published there. LocalMaxxing rows carry the run link and the
numbers used, without the submitter's username or notes: the site's terms leave ownership with submitters and grant no
licence to redistribute the data, so each run is cited, not copied wholesale. Records by a stack's own author are
marked `measured_by: "author"`.

## What is used to fit, and what is kept as evidence only

983 records pass the checks below; 938 of them remain after the outlier pass and fit the model. The rest were set aside
for these reasons, counted by the first reason each record has (over all 2,732 collected; the GitHub and X ones stay
in the file with their reason in `why`):

| Reason | Records |
|---|---:|
| Card outside this article (pre-Ampere, cards without a mapped specification) | 1,134 |
| A drafter that is not the stack's default (or any drafter, for the whole-model servers) | 264 |
| Mixed cards, a helper APU, or unified memory | 154 |
| RAM too small for the pack, so experts came from the SSD | 50 |
| Datacenter card (H100, A100, L40S, A40) | 32 |
| Faster than the cards' memory allows without a drafter (mislabelled), capped clocks, two 8-core CPUs, a harness import or another engine under the label | 104 |
| More VRAM than the cards have for a whole-model stack, as modelled: unstated offload or cache settings | 8 |
| No speed figure, or the engine, quant or host not stated | 3 |

## Corrections carried over from the review of the first draft

- Project Maya `--bench` measures writing on three short questions (10-35 tokens) and reading on an 8K prompt. The
  first draft recorded the writing figures as 8K; here the prompt length is null or the real figure.
- Maya issue 172 (one RTX PRO 6000, Maya-M, 81 tokens/s) ran **without** drafting: the reporter corrected this in the
  issue. Maya decodes without drafting on one card and with the model's MTP block on two or more.
- Runs labelled "plain" that ran a drafter (MTP spec 4 in a committed config, DFlash2 recipes) are marked as drafted.
- Strata's DeepSeek "Faster" mode uses five of six experts per word and is the default on single R9700 cards; such runs
  are fitted with five sixths of the expert reads.
- A LocalMaxxing row's `batchSize`, `concurrency` and `tokSTotal` can describe a harness, not one stream; rows whose
  speed exceeds the memory bound or whose decode includes prompt time are excluded.

## Corrections from the prepublication audit (20 Nov 2026)

Each was checked against the stack's or model's own documents before it was changed.

- GLM's cache on Maya is 544 bytes a token **per layer**, in 11 layers, and the whole of it sits in pinned RAM once a
  context is longer than the 32K window. The calculator had 544 bytes in all, and only beyond 64K.
- Strata's DeepSeek engine takes at most 8 conversations on one card or two, not 8 per card, and its cache grows with
  context (about 1.3 KB a token in VRAM), where the calculator had stopped it at 64K.
- Three cards cannot split Gemma 4 26B-A4B's or Qwen3.8-27B's attention heads on the batching servers: refused.
- A machine that cannot be built no longer shows a stream count; the power message names the 90% limit it applies.
- RAM is converted from GiB like the cards' memory. The page's reading gap now covers every stack (30–82%), and the
  stream count says it is the middle of the range, with the count at the low end beside it.
- The runs shown beside an estimate now say which quantised file they used, rank the pack's own file and the nearest
  prompt length first, and link the run's own page.
- The refit after these changes leaves the three machines' figures and the page's headline unchanged.
- From a second review the same day: the used EPYC CPU and board, imported from the UK with no GST stated, carry the same
  10% GST provision as the refurbished 3090, so the Medium machine is A$43,568, not A$43,309; the RAM figure draws the
  calculated expert and system shares (Strata keeps 10 GB, Maya 16 GB) instead of a fixed 16 GB; the gaps are shown as
  the factor the median run is off by (35%, not a log gap of 30%); the automatic choice is called the largest version
  that keeps the speed, as no published quality comparison covers every file.

## The comparison on the page

Section 03 draws only measured numbers (`stack-comparison.json`): one computer measured by Strata's author, and two
community machines for GLM-5.3-Flash. Both pairs say how comparable they are.

## Gaps

- Few long-context and many-user runs for the expert stacks on 96 GB cards; reading speed has the widest bands.
- SGLang's plain runs all come from one user's RTX PRO 6000 Server Edition (LocalMaxxing). They are used as reported;
  with six writing runs its writing band is the default ±30%.
- No first-hand run combines the language model with real vision or embedding work on the tools card.
