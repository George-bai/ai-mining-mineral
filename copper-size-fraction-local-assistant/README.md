# Can a local AI assistant tell which size fraction carries the most copper?

Code, prompt and results for the article at https://eleticle.com/articles/copper-size-fraction-local-assistant/.

Two local language models, each in a coding agent with a shell so it could run Python, were given Table 1 of a
published study of copper flotation tailings and asked one question: which size fraction carries the most
copper? Each model answered ten times. We worked the answer out ourselves (`check.py`), and all 20 replies were
read against it (`results/run1/review.json`).

**In short:** all 20 attempts named the fraction with the most of the reported copper (CTS−C5, the finest) and said that the richest fraction
(CTS+106) is a different one. None said that the 8.2 % of the sample missing from the table might hold copper.
Eleven of the twenty replies stated at least one wrong number or comparison, although every script behind them put
the fractions in the right order. Seventeen gave the finest fraction a size the table does not give.

## The table

Table 1 of Habibi, Cook, Ehrig, Ciobanu, Campo-Rodriguez and King (2025), *Minor and Trace Elements in Copper
Tailings: A Mineralogical and Geometallurgical Approach to Identify and Evaluate New Opportunities*, *Minerals*
15(10), 1018, https://doi.org/10.3390/min15101018, published under CC BY 4.0. Seven size fractions of one sample
of fresh flotation tailings from the Carrapateena processing plant, July 2024, assayed for major, minor and
trace elements. The table is reproduced in `prompt.md`, as the models received it.

Two separate readings of the publisher's page (20 Nov 2026) agree on every mass and copper value. The
paper does not state the screen sizes or the method behind the codes C1, C3 and C5, gives no measured head
grade and no copper distribution for this sample, and does not explain why the masses add to 91.8 %. Its
abstract calls the finest fraction −10 µm; section 4.1 calls CTS−C5 the finest fraction.

## Our answer (`check.py`)

| Fraction | Mass % | Cu, ppm | Mass × grade | Share of the reported copper |
|---|---|---|---|---|
| CTS+106 | 8.6 | 2,250 | 19,350 | 16.7 % |
| CTS+75 | 7.7 | 1,864 | 14,353 | 12.4 % |
| CTS+53 | 10.1 | 1,265 | 12,777 | 11.0 % |
| CTS+C1 | 13.1 | 1,390 | 18,209 | 15.7 % |
| CTS+C3 | 13.8 | 775 | 10,695 | 9.2 % |
| CTS+C5 | 5.2 | 860 | 4,472 | 3.9 % |
| CTS−C5 | 33.3 | 1,084 | 36,097 | **31.1 %** |
| Sum | 91.8 | | 115,953 | |

- **Richest by grade:** CTS+106, 2,250 ppm. **Carries the most copper:** CTS−C5.
- **The masses add to 91.8 %.** The other 8.2 % is not in the table, and the paper does not say what it is. The
  shares above are of the reported copper only. How the answer reads depends on what the missing mass is:
  - *A fraction of its own:* CTS−C5 stays the largest carrier unless it grades above 4,402 ppm (CTS−C5's
    36,097 ÷ 8.2), about twice the richest fraction. CTS−C5's share of the whole sample falls to 28.6 % at the
    reported fractions' average grade (1,263 ppm) and 26.9 % at the richest fraction's (2,250 ppm).
  - *Lost CTS+106 material, at that fraction's grade:* CTS+106 carries the most copper, 28.1 % against
    CTS−C5's 26.9 %. The answer changes.
  - *Lost fines, at CTS−C5's grade:* CTS−C5 carries 36.0 %.
  So 31.1 % is CTS−C5's share of the reported copper. Across the readings above (the missing mass added to a
  fraction at that fraction's grade, or a fraction of its own no richer than CTS+106), its share of the whole
  sample lies between 27 and 36 %. Other assumptions give other numbers: as CTS−C5 fines at 2,250 ppm, 40.6 %.
- **No head grade to check against.** 1,263 ppm is the reported fractions' own average, not an assay of the
  sample, so nothing here shows whether the missing mass carries copper.

```bash
python3 check.py      # standard library only; prints the numbers above and asserts them
```

## The test

| | |
|---|---|
| Models | Qwen 3.8 27B: `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead` (4-bit NVFP4 weights), served with vLLM 0.27.1 on 2 × RTX 5080, context 165,000 tokens. Qwen 3.8 Flash Next: endpoint `qwen38-next-flash`, context 262,144 tokens, two copies of the model behind one gateway on 4 × RTX 3090; the weights and server are those described for [article No. 06](../flowsheet-to-mermaid-local-llms/README.md), not re-checked for this run |
| Agent | [Pi](https://pi.dev) 1.5.2, its four built-in tools (read, bash, edit, write), print mode, a clean configuration folder: no skills, context files, extensions, prompt templates or MCP. Pi's thinking level was `off`, so it sent no reasoning setting; both models still thought before answering, as their servers do by default. No sampling settings were sent |
| Fence | Each attempt ran in bubblewrap: its own empty folder and `/tmp`, the home folder read-only, the repositories (with `check.py` and the article) hidden. The model endpoints stayed reachable. The models had no web tool. `run.sh` now hides the clone it sits in, wherever it is, so a rerun sees only the prompt, its tools and its own empty folder |
| Prompt | `prompt.md`: one sentence on what the table is, the question, "You can run Python on this machine. Give your answer in your final message.", then Table 1's three blocks of numbers as printed (42 columns), without its footnote. Nothing about grade against copper carried, nor about the 91.8 % |
| Attempts | Ten per model, one after another, on 20 Nov 2026 (AEST); the two models ran at the same time on their own servers. Every attempt ended on its own, in 12 to 75 s |

```bash
cp models.json my-models.json                    # put in your own endpoints and model names
MODELS_JSON=$PWD/my-models.json ./run.sh run1    # needs pi and bwrap; writes ../local/runs/run1/
python3 collect.py ../local/runs/run1            # writes results/run1/: answers, steps, results.json
```

## Results

`results/run1/<model>/<attempt>/answer.md` is each final reply; `steps.md` is everything before it in order
(thinking, each command the model ran, what came back); `results.json` has the time, turns, tool calls and
tokens. `review.json` is the reading of each reply against `check.py`:

| Check | Qwen 3.8 27B | Qwen 3.8 Flash Next |
|---|---|---|
| Ran Python on the table | 10 / 10 | 10 / 10 |
| Named CTS−C5 as carrying the most copper | 10 / 10 | 10 / 10 |
| Kept grade and copper carried apart (named CTS+106 as the richest) | 10 / 10 | 10 / 10 |
| Table arithmetic and comparisons in the reply right (sizes and whole-sample shares scored separately) | 5 / 10 | 4 / 10 |
| Said the masses add to 91.8 % | 0 / 10 | 9 / 10 |
| Said the missing 8.2 % may hold copper | 0 / 10 | 0 / 10 |
| Sized CTS−C5 only as the table does (no size in µm, not "the coarsest") | 1 / 10 | 1 / 10 |
| Made no mineral or recovery claim | 8 / 10 | 0 / 10 |

What the readings rest on:

- **Wrong numbers.** Each is listed in `review.json` with the correct value: a runner-up named wrongly (27B 5),
  36 % for 31 % (27B 9), "more than double" for 1.87 times (27B 6, 10; Flash Next 8), a range that leaves out
  CTS+C1 (27B 4), CTS−C5 called the coarsest fraction (27B 6), the three coarse fractions given 68.9 % of the
  copper instead of 40.1 % (Flash Next 10), grade said to fall "steadily" from CTS+106 to CTS+C3 when it rises
  at CTS+C1 (Flash Next 2), and others. Every script printed the fractions in the right order. Most errors came
  in the words, but not all: the 27B's attempt 5 printed mass × grade × 100 ÷ 91.8 labelled as a percentage
  (21,078 %), and the scripts of Flash Next 4 and 10 printed wrong sums for "the three coarse fractions" (58.5 %
  of the mass, which is all six `CTS+` fractions), which their replies repeated.
- **The 91.8 %.** Nine Flash Next replies mentioned it, as a reason to rescale the shares; the tenth (attempt 2)
  said only that its shares were "normalised to the seven fractions". Three stated a cause as fact ("analytical/processing loss", "sizing losses", "unsampled/loss"); the paper gives none. No 27B reply
  mentioned it, though it appeared in the 27B's own script output (attempt 1) and thinking (attempt 5: "No
  problem. The ranking is valid."). Every reply but one (27B 5) gave CTS−C5's share as a share of all the copper
  in the sample or the tailings: 31 %, or 36 % in 27B 9.
- **Sizes.** Sixteen replies said CTS−C5 is finer than 5 µm, one said finer than 45 µm, one called it the
  coarsest fraction. The table prints no sizes for C1, C3 or C5; the paper's abstract calls the finest fraction
  −10 µm.
- **Beyond the table.** Claims about which mineral holds the copper (liberated chalcopyrite; copper locked in,
  likely refractory; copper with silicate gangue; results "consistent with" fine chalcopyrite in the fines) or
  where it can be recovered. Hedged or not, bulk assays by size cannot show either, and the replies contradict
  one another. One Flash Next reply
  (attempt 5) also said cobalt, silver, iron and sulfur peak with copper in CTS+106; there iron and sulfur are
  the lowest of the seven.

## Limits

- One table, two models, ten attempts each, one prompt. This shows what these two models did with this table,
  not how they do on lab tables in general.
- The question was asked bare on purpose. A prompt that asks the model to check the data first may change
  the result; it was not tested here.
- The checks are our reading. A reply that said the shares are "normalised to the recovered mass" (Flash Next 8)
  came closest to the missing-copper point, but did not say the missing mass could hold copper, so it is
  scored no.
- The models' timings include sharing the servers with other work on the day; they are not speed measurements.

## Files

| File | What it is |
|---|---|
| `prompt.md` | The whole prompt, Table 1 included |
| `models.json` | Two example endpoints in Pi's format. Copy it and put in your own addresses and model names |
| `run.sh` | Runs each model on the prompt, fenced, ten attempts by default |
| `collect.py` | Turns a run's raw Pi logs into `results/<run>/` |
| `check.py` | Our answer from the table, with asserts on every number the article uses |
| `results/run1/` | The run the article reports: `results.json`, `review.json`, and each attempt's `answer.md` and `steps.md` |

## Licence

Code (`run.sh`, `collect.py`, `check.py`) under the MIT licence. Results under CC BY 4.0. Table 1, in
`prompt.md` and `check.py`, is from Habibi et al. (2025), © the authors, under CC BY 4.0; reproduced unchanged
apart from layout, with the footnote left out.
