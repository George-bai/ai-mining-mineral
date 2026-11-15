# Can a local LLM read a mineral processing plant flowsheet?

Two local language models were each given four mineral processing flowsheets and one instruction: redraw
this as a Mermaid flowchart. This folder contains the procedure, the final Mermaid file from each reported attempt, the rendered
SVGs, the measured numbers and the review notes. It is enough to repeat the procedure on your own
models; it does not pin down every setting of the two used here. The article is at https://eleticle.com/articles/flowsheet-to-mermaid-local-llms/.

**A first test, not a benchmark:** one attempt per model and drawing in the reported run, following earlier
exploratory runs, judged by eye and checked by a second reviewer. There is no
reference answer yet, so there are verdicts and no scores.

## Result

| Drawing | Qwen 3.8 27B | Qwen 3.8 Flash Next |
|---|---|---|
| Simple circuit (5 units) | Correct. 7 boxes, 9 lines, 15 s | Correct. 7 boxes, 9 lines, 21 s |
| Block diagram | Correct. 19 boxes, 21 lines, 26 s | Correct. 20 boxes, 22 lines, 23 s |
| Phoenix mine mill (about 40 units) | Poor connections. 62 boxes, 60 lines, 154 s | Partial. 66 boxes, 88 lines, 812 s |
| Twin Creeks mine (about 60 units) | Poor connections. 72 boxes, 70 lines, 78 s | Partial. 74 boxes, 98 lines, 882 s |

- **Correct:** every unit and stream matches the drawing.
- **Partial:** most labels right and several of the plant's real loops recovered, with reading and
  routing errors that a check against the drawing finds.
- **Poor connections:** most units found, most lines wrong.

On the two plant flowsheets the 27B model looked at the drawing, opened it once more, and wrote a chart
drawn largely in single file. Flash Next cut the drawing into pieces with a shell command, read 26 to 32
of them, and recovered more of the plant's loops, with some lines still routed wrongly.

| | Phoenix | Twin Creeks |
|---|---|---|
| Input tokens, Flash Next against 27B | 138 times | 153 times |
| Elapsed time, Flash Next against 27B | 5.3 times | 11.3 times |

Input tokens are summed over every request, so they count the same conversation many times.
Box and line counts describe a chart; they do not show that its connections are right.

The notes behind each verdict are in [`results/run3/review.json`](results/run3/review.json).

## What is here

| File | What it is |
|---|---|
| `prompt.md` | The whole instruction given to the model |
| `models.json` | Two example model endpoints, in Pi's format. Copy it and put in your own addresses and model names |
| `image-limit.ts` | A Pi extension: keeps at most two images in any request (the drawing and the newest), and tells the model when one was dropped |
| `prepare.sh`, `crop.py` | Build the four test drawings from the lecture PDF: one slide each, cropped to the figure |
| `run.sh` | Runs every model on every drawing. One folder of output per model and drawing |
| `render.py` | Draws each Mermaid file as SVG with headless Chrome, and counts its boxes and lines |
| `collect.py` | Gathers a run into `results/`: Mermaid files, SVGs and `results.json` |
| `results/run3/` | The run the article reports: `<model>/<drawing>/flowsheet.mmd` and `.svg`, `results.json` (time, requests, tokens, extra images read, boxes, lines, and every step with the second its result came back) and `review.json` (verdicts and notes) |

## Run it yourself

You need: two OpenAI-compatible endpoints serving vision models; Node 22.19 or later and
[Pi](https://pi.dev/) 1.5.2 (`npm install -g --ignore-scripts @earendil-works/pi-coding-agent@1.5.2`);
`pdftoppm` (poppler-utils); GNU `timeout` (coreutils); Python 3 with Pillow; and Google Chrome for the
rendering step, with internet access, because it loads Mermaid 11.4.0 from jsDelivr. Run everything from
this folder.

```bash
# 1. Download the lecture PDF (link under Sources), then build the drawings
./prepare.sh Flowsheets.pdf drawings

# 2. Copy models.json, put in your endpoints and model names, then run.
#    MODELS lists what to run, as provider/model from your file.
MODELS_JSON=my-models.json MODELS="qwen27b/qwen38-27b flashnext/qwen38-next-flash" ./run.sh myrun

# 3. Draw and collect
python3 render.py ../local/runs/myrun
python3 collect.py ../local/runs/myrun
```

`run.sh` gives each model 15 minutes per drawing, and starts Pi with a clean configuration: no skills,
no context files, and no extension except `image-limit.ts`. `collect.py` takes the models and drawings
from the run's own folders, so other model names need no change to it. Use a new run name for each
experiment: collecting a run again replaces what was collected for it before.

A run writes the drawings, your model configuration and Pi's raw logs (which contain the drawings) into
`drawings/` and `../local/`. The repository's `.gitignore` keeps them out of a commit; do not publish them.

## How it was run

| | |
|---|---|
| Agent software | Pi coding agent 1.5.2, print mode, standard tools (read, bash, edit, write) |
| Qwen 3.8 27B | `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead`, revision `009632fef96dd349150baa780c984e62e70e91fe` (4-bit NVFP4 weights). Served with vLLM 0.27.1 across 2 × RTX 5080 (16 GB each): context 200,000 tokens, temperature 0.6, top-p 0.95, top-k 20, thinking on at medium effort, at most 2 images per request |
| Qwen 3.8 Flash Next | The [GSQ-RCO GGUF release](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) of `Qwen/Qwen3.8-Flash-Next`, IQ3_S quantisation (mixed precision, averaging 3.5 bits per weight), with its BF16 vision projector. Served with Strata 0.1.48 as two copies of the model, each on 2 × RTX 3090 (24 GB each), behind one gateway: context 262,144 tokens, the engine's default sampling, at most 2 images per request |
| Input | One image (the cropped drawing, 200 dpi) attached to the instruction |
| Date | 14 November 2026 |

## What went wrong first

Kept here because each cost a run, and each would catch anyone repeating this.

1. **Pi waited for input that never came.** Started from a script with an open input pipe, `pi -p` waits
   for piped input. `run.sh` closes it (`< /dev/null`).
2. **The whole slide confused the reading.** Given the lecture slide with its title bar and footer, the
   27B model misread about a dozen labels on the Phoenix drawing. Cropped to the figure, it read them.
3. **Two images per request.** Both endpoints refuse a request with more than two images. Flash Next
   zooms by cropping and reading the crops back, each crop stays in the conversation, and the third image
   ended its run with no output. The 27B model never read more than one extra image, so it never met the
   limit. Pi 1.5.2 can declare such a limit (`inputLimits.images`) but does
   not act on it; `image-limit.ts` does.

## Limits

- One attempt per drawing. Earlier runs gave different outcomes for the same model and drawing.
- Verdicts are judgements by eye. Box and line counts, times and tokens are measured.
- All eight files are valid Mermaid. That is not the same as correct.
- The Twin Creeks drawing is 749 × 548 pixels in the PDF; its small labels are blurred at any zoom.
- The models are the two that were available on the day, not a survey of local models.

## Sources

The drawings are slides 23, 53, 39 and 37 of: Anderson, C. G. *Mineral Processing Flowsheets* (Lecture
6). Colorado School of Mines. https://www.researchgate.net/publication/318502393_Flowsheets

They are not included here: they belong to their authors, and the original source of each drawing is not
stated on the slides. The article shows them with approval. `prepare.sh` rebuilds them from the PDF.

## Licence

Code: MIT. Results (the Mermaid files, SVGs and JSON in `results/`): CC BY 4.0, for what is ours in
them. Each chart is a model's reading of a third-party drawing; this licence grants nothing over the
drawings themselves, whose rights stay with their owners.
