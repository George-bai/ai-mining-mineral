# Does a site glossary help a local LLM read maintenance work orders?

Code and data for Eleticle Core Log No. 13 (https://eleticle.com/articles/work-order-shorthand-glossary/).

A local LLM (Qwen 3.8 27B, on two 16 GB graphics cards) read 300 real, held-out mining maintenance work orders
twice: once with no help, once with a 50-line glossary built from 3,200 other work orders of the same company. Every answer was
scored against MaintNorm's key, then checked, blind to which version it came from.

| | Without the glossary | With the glossary |
|---|---|---|
| Notes whose meaning came through (checked) | 228 of 300 | 283 of 300 |
| Shorthand read right | 437 of 508 (86.0 %) | 492 of 508 (96.9 %) |
| Shorthand read wrong | 58 | 8 |
| ... of it listed in the glossary (370 pieces) | 47 | 0 |
| ... of it not listed (138 pieces) | 11 | 8 |
| Service intervals such as `1000H` read as a clock time | 14 | 0 |
| Answers that invented a diagnosis | 4 | 0 |
| Answers that said the work was done | 0 | 0 |
| Answers that added a part or task | 2 | 0 |
| Median time per note | 17.8 s | 14.8 s |

Paired by note, 65 notes kept their meaning only with the glossary and 10 only without it (exact McNemar test,
two-sided p ≈ 5 × 10⁻¹¹). The difference in shorthand read right is 10.8 points, 95 % interval 8.1 to 13.7 (2,000
bootstrap draws of whole notes within each company, Python `random.Random(1)`, the 50th and 1,950th of the sorted
differences). Per company, notes whose meaning came through: A 83 → 95,
B 63 → 97, C 82 → 91.

In four answers the model applied a glossary line where it does not fit: `quick = Kwik` (from
"quick tip" → "Kwik Tip", a bucket tip brand) turned two "quick fill" connectors into "Kwik fill"; `no = number`
turned "no a/c fans" into "Number air conditioner fans"; `lock = lockout` turned a bucket "tooth lock" into a
"tooth lockout". A fifth may be one: `temp = temperature` gave "temperature repair" for `TEMP REP` on a leak, which
reads as a temporary repair; MaintNorm's key also says temperature, so it is scored right (see "Key doubts").

## The data

[MaintNorm](https://github.com/nlp-tlp/maintnorm) (Bikaun, Hodkiewicz and Liu, *Proceedings of the Ninth Workshop on
Noisy and User-generated Text*, W-NUT 2024, pages 68–78, https://aclanthology.org/2024.wnut-1.7), commit
`e98ca406f7afffbb0ab3243aa7c922f3b64bc7c8`: 12,000 maintenance work order texts from three Australian mining and
mineral processing companies, A, B and C, 4,000 each, split 3,200 train / 400 val / 400 test. One annotator paired every
token with its normalised form; asset numbers, numbers, dates and names are masked in the key and replaced with mock
values in the raw text. MIT licence, "Copyright (c) [2024] [NLP-TLP Group]"; the notes and glossaries in this folder
are derived from it under that licence.

- **Shorthand** (`prepare.shorthand`): a token whose normalised form differs by more than case and is not only a mask.
  Abbreviations, misspellings and run-together words all count. Digits are dropped from the key, so `pos2` is `pos`
  and `1000h` is `h` = hour, unless nothing but punctuation would be left (`1/4` = quarter).
- **Glossary** (`prepare.glossary`, `glossary/A.txt` …): per company, from its train split only, the 50 shorthand
  forms used most often with the annotator's meaning; a second meaning is listed when it has at least 20 % of the
  uses. No hand editing. 18 shorthand forms appear in all three glossaries (17 with the same meaning: `insp` is
  inspect at A, inspection at B and C); 23, 19 and 26 are one company's own.
- **Notes** (`notes-test.json`): per company, 100 notes drawn at random (seed `11-<company>-test`) from its test split
  among notes with at least one piece of shorthand, leaving out any whose text repeats a train or val note of the
  same company. 508 pieces of shorthand in all. `notes-dev.json` holds the 36 val notes the prompt was tried on.

## How it was run

| | |
|---|---|
| Model | `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead` (4-bit NVFP4 weights) as `qwen38-27b` (`server.json`) |
| Server | vLLM 0.27.1 (its `/version` on the day) on 2 × RTX 5080 (16 GB each), context 165,000 tokens; thinking on, the default |
| Sampling | none sent, so the server's defaults apply: temperature 0.6, top-p 0.95, top-k 20 and at most 2 sequences as configured for Core Log No. 08, not inspected again; `max_tokens` 16,000 |
| Requests | one per note and version, two at a time, the versions alternating; 20 Nov 2026, 1:18 to 2:46 pm AEST |
| Prompt | `prompt.md`; with the glossary, the block in `run.py` inserted, the only difference |

All 600 answers parsed as JSON; none was cut off.

The prompt was tried on the val notes only, twice; a protocol review (by a second model, before any test note was
sent) added the "keep numbers" and "make doubt visible" lines, the leave-out of repeated notes, 100 notes instead of
60, the blind check and the meaning verdict. The protocol, its changes and the SHA-256 of every frozen file are in
`../plan.md` in the private working repository; the frozen hashes:

| File | SHA-256 |
|---|---|
| `prompt.md` | `7377f1adcc069606cbd4f18e6293de4eac2c51988b21f3de6d26247d602eb14d` |
| `glossary/A.txt` | `8a7d236b782b3f66bc43f277e5e49612b08c7a56ee860311926411294ee01409` |
| `glossary/B.txt` | `694d48348f8c92372a3f1da166fbf6d01054cc0726c83d5cf7e6c3243d3b0cd2` |
| `glossary/C.txt` | `a25a0d2d12303e5a686e78ffd855281e8d1881dc87eebb5e6cd2b2f6a43af36f` |
| `notes-test.json` | `83ed88052980b4b9b6ddd60aa73c66522c2f44c20cc741239e8f6bf21c819030` |

## How it was scored

1. **Script** (`score.py`): per piece of shorthand, right (the model's expansion holds every word of the key's
   meaning, singular and plural alike), wrong, unsure (listed as unsure, or two readings offered such as "repair or
   replace") or kept (left as written, unflagged).
2. **Read**, every answer, blind: `score.py --sheet` shows each note's two answers as x and y in an order drawn from
   the note id. Rules, fixed before the run: what the plain-English text tells the reader is what is scored; a
   synonym is right ("air conditioning" for air conditioner, "inspect" for inspection, "center" for centre); a
   different thing, action, side or interval is wrong (`1000H` as 10:00, `u/s` as upstream); an everyday form that
   already says it is right (`cab`, `#6`). Each answer also gets four verdicts: **meaning kept** (nothing misread,
   dropped or added; shorthand left visibly unread does not break it: 6 of the 283 kept with the glossary and 10 of
   the 228 without still hold a piece marked unsure or kept as written), **diagnosis** (a fault, cause or failed part with no counterpart in the note; a misreading of
   the note's own words is counted under meaning), **done** (says work was done when the note does not), **added** (a
   part, place or task not in the note). The diagnosis rule was first applied unevenly: a re-check after the page
   review, made with the versions known, added three diagnoses (A-test-122, A-test-127, C-test-101), all without the
   glossary. A second review changed five meaning verdicts, again with the versions known, to apply the rule as
   written: `A-test-110`, both answers ("Replace the converter shaft" for the shaft's universal joints, UNIS split
   off), `C-test-188` without the glossary (asset 526 read as a quantity, "Audit 526 air fittings"), `B-test-211`
   without it (asset WK1566 made "Work order 1566") and `B-test-363` with it (the asset number dropped). Every other
   verdict was made blind.
3. `check.txt` holds every correction and verdict with its reason; `check.py` turns it into `check.json`, giving every
   answer in a block read in full an explicit verdict, and keeps a digest of each answer read (its plain text, terms
   and unsure list). `score.py` applies a verdict only to the answer it was made on, and `--final` refuses to report
   while any answer lacks one, so the verdicts here never pass to a fresh run's answers.
   `results.json` is the result: every answer's text, items, outcomes and verdicts, and the summary.

### Key doubts

Two of the key's readings look wrong; both stay scored on the key, in both versions alike.

- `A-test-267`, "TEMP REP TO TRANS DROP BOX LEAK": keyed "temperature repair"; on a leak it reads as a temporary
  repair. Re-keyed, the answer without the glossary ("temporary repair") would gain a right item and the one with it
  ("temperature repair") would lose one: wrong readings of listed shorthand with the glossary 0 → 1, without 47 → 46.
  The meaning verdicts already judge it as temporary.
- `A-test-387`, "REPA INTER FACE": keyed "internal face"; "interface", which both answers gave, is as likely.

## Repeat it

You need Python 3.10 or later (standard library only), MaintNorm, and an OpenAI-compatible chat endpoint.

```bash
git clone https://github.com/nlp-tlp/maintnorm.git && git -C maintnorm checkout e98ca406f7afffbb0ab3243aa7c922f3b64bc7c8
python3 prepare.py maintnorm/data                    # glossary/, notes-test.json, notes-dev.json (identical to these)
python3 run.py notes-test.json runs/test --url http://<host>:<port>/v1/chat/completions --model <model id>
python3 score.py notes-test.json runs/test --check check.json --sheet sheet.md --out results.json
```

With another model or run, the check starts again: read `sheet.md`, write your own `check.txt`, then
`python3 check.py check.txt check.json runs/test` and `python3 score.py ... --check check.json --final`.

## Limits

One model, one answer per note and version, sampled (a second run would differ in places). One annotator's key, and
two of its readings in doubt. Three companies' notes, mostly heavy mobile equipment, short texts only; a site's own
glossary would be checked by its planners rather than taken from counts alone.
The split is MaintNorm's, not by date, so "held out" means held out from the glossary and the prompt: MaintNorm has
been public since 2024, and the model may have met these notes in training; its effect on this comparison is unknown.

Two later checks, from Core Log No. 16 (`../work-order-shorthand-past-notes/`): 47 test notes equal a train note
once the tokens the key masks as asset numbers are removed, 55 by a broader check (`near_duplicates_broad` in its
`coverage.json`); without the 55, meaning kept 193 → 230 of 245 (15.1 points, against 18.3 on all 300). The glossary
version, run again on 21 Nov 2026 with the same prompt and server, kept 273 of 300 (20 notes changed verdict; read
by other readers).

## Files

| File | What it is |
|---|---|
| `prepare.py` | Builds the glossaries and draws the notes |
| `prompt.md`, `run.py` | The instruction and the runner |
| `score.py`, `check.py` | The script's scoring, the blind sheet and the check |
| `glossary/` | Each company's 50 lines, as text and with counts |
| `notes-test.json`, `notes-dev.json` | The notes read, each token with MaintNorm's normalised form |
| `check.txt`, `check.json` | The check: every correction and verdict, with its reason |
| `results.json` | Every answer, scored |
| `server.json` | The model list the server returned on the day |

Code: MIT. Data derived from MaintNorm: MIT, © 2024 NLP-TLP Group.
