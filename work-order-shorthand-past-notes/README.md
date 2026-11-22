# Does searching a site’s own work orders help a local LLM as much as a glossary?

Code and data for Eleticle Core Log No. 16 (https://eleticle.com/articles/work-order-shorthand-past-notes/), which
follows No. 13 (`../work-order-shorthand-glossary/`) and uses the search setup with the most complete lists in No. 15
(`../offline-search-technical-records/`; its lead there is the two-record question, which it alone answered in all
three wordings when asked again with its date; on the other questions five setups tied).

No. 13 gave a local LLM (Qwen 3.8 27B) each company's fixed 50-line glossary, built from 3,200 of its work orders,
and read 300 held-out notes with and without it. Here the same model, server and prompt read the same 300 notes with
a third kind of help: SAG-Wiki's deep search, judged by Qwen3-Reranker-0.6B, run offline over the company's 3,200
other notes (MaintNorm's train split, which is not ordered by date), each with the annotator's reading, and the ten
passages it returned put where the glossary went. The glossary version was run again the same day. Every answer was
scored against MaintNorm's key, then read blind by hand. A note's **meaning is kept** when the plain-English reading
says what the note says: nothing misread, dropped or added (shorthand left visibly unread does not break it).

| | Search (21 Nov) | Glossary (21 Nov) | Glossary (No. 13, 20 Nov) | No help (No. 13, 20 Nov) |
|---|---|---|---|---|
| Notes whose meaning came through, adjudicated | **290** of 300 | 273 | 283 | 228 |
| … as the readers first judged, blind | 286 | 273 | | |
| … after the settlement made before unblinding | 287 | 273 | | |
| … company A / B / C (adjudicated) | 97 / 97 / 96 | 95 / 92 / 86 | 95 / 97 / 91 | 83 / 63 / 82 |
| Shorthand read right, of the 508 items scored under No. 13’s rules | 500 | 488 | 492 | 437 |
| Shorthand read wrong | 7 | 12 | 8 | 58 |
| Shorthand not read (unsure or kept) | 1 | 8 | 8 | 13 |
| Answers that invented a diagnosis / said work done | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 0 |
| Answers that added a part or word | 3 | 0 | 0 | 2 |
| Median time per note | 12.6 s (+ 0.6 s search) | 14.5 s | 14.8 s | 17.8 s |
| Prompt, median tokens | 578 | 621 | | |

The 508 scored items are the tokens No. 13's rule picks from those the key changes (it leaves out, for example, a
form joined to an asset number such as `BT0391-C/out`, and `PRESS/`); shorthand the key leaves as written, such as
`REPS` in A-test-105, is not scored either, so a model's "unsure" list can name more than the "not read" row counts.

**Paired, same day** (search against the glossary run on 21 Nov), adjudicated: 268 notes kept their meaning with both,
22 only with the search, 5 only with the glossary, 5 with neither; exact McNemar test, two-sided, p = 0.0015. As the
readers first judged, blind: 22 against 9, p = 0.029; after the settlement made before unblinding: 22 against 8,
p = 0.016. Leaving out the 47 near-duplicate notes (below): 244 against 229 of 253, 19 against 4, p = 0.0026; leaving
out the 55 of the broader check: 236 against 221 of 245, 19 against 4, p = 0.0026. Under the stricter readings Codex's
page reviews proposed and we did not adopt, with the blind readers' verdicts on the four answers set back by No. 13's
rulings (below): 286 against 264, 30 against 8, p = 0.0005; additions would then
be 3 with the search and 2 with the glossary, and glossary shorthand 487 right and 13 wrong (C-test-246's "motor and
blower"). Every stage points the same way.

**Against No. 13's glossary run** (20 Nov, the same notes, prompt and server instance): the search 290, that run 283;
13 notes only with the search, 6 only with that run, p = 0.17: not a clear difference.

**Run to run**: the glossary kept 273 notes on 21 Nov and 283 on 20 Nov; 5 only on 21 Nov, 15 only on 20 Nov,
p = 0.041; 20 notes changed verdict, every one with a different plain-English reading, while all 77 identical
plain-English readings got the same meaning verdict. Both sampling (one answer per note) and grading (different readers on the two days; on No.
13's archived answers these readers matched its verdicts 36 times in 40 as read, 37 after the settlement below) could
contribute; this comparison cannot separate them. On this run the search did
better than the glossary; whether it usually does, and by how much, is open.

**What each version put in front of the model** (`coverage.py`, no model): a piece of shorthand is supplied when its
form and the key's meaning appear in one place, a glossary line or one returned passage (a word of the other note
with that form, and every word of the meaning in its "Means" line). Of the 508 pieces: glossary 369, search 373, both
327, only the search 46, only the glossary 42. Per company (glossary / search, of A 157, B 203, C 148): 118 / 111,
162 / 164, 89 / 98.

**Borrowed words.** All three additions came with the search, each a word found in the other notes it returned:
`B-test-261` ("250hr Service" on LD3192) became "250 hour mechanical service for haul truck LD3192", from other
notes with the same asset number, "250H Mech Svce Haul Truck LD3192" (MaintNorm's asset numbers are mock values,
consistent within a company); `A-test-296` added "bucket" before "tooth lock" (another note: "Replace
Bucket Tooth Lock"); `C-test-336` added "nozzle" to the quick fill (another note: "REPLACE LEAKING QUICK FILL
NOZZLE"). And `A-test-285` ("BRAKE PACKS") became "brake pads", following another note the annotator read that way
("BRAKE PACS" = brake pads): a misreading, not an addition.

**Near-duplicates.** 47 of the 300 test notes equal a training note once the tokens the key masks as asset numbers are
removed (ignoring case); the search can find such a note itself. They are reported, not removed (sensitivity above).
A broader check, added after the run at Codex's page review, also removes asset numbers inside a token
(`BT0391-C/out`, where the key marks the token as holding an asset number): 55 notes (`near_duplicates_broad` in
`coverage.json`).

## The search

- **Index** (`index.py`): per company, MaintNorm's train split (not ordered by date: these are other notes of the same
  company, not necessarily earlier ones), the same 3,200 notes No. 13's glossary was built from;
  one Markdown file, one heading per note as typed, under it "Means: " and the annotator's reading, with masked asset
  numbers, numbers and dates put back as typed (`2000H` keeps its 2000; asset IDs keep their letters). No val or test
  note is read. Found after the run (Codex's page reviews): the builder as run (`index_as_run.py`, SHA-256
  `16eb176d…`) misfills masks in 11 of the 9,600 notes, where an asset number runs into a word, a number or date
  shares a token with one, or a name follows a slash (`engineV1` became "engine 1", `7897-3Week` "7897 - 7897 week",
  `KD208-24/04/10` "KD208 - 208", `PARTS/NIGEL THOMAS` "parts / PARTS"). One such passage reached the model:
  B-test-364's second, "engine 1" for engineV1; that note's search answer kept its meaning. `index.py`, for fresh
  runs, lines the annotator's words up with the typed token, fills each mask with the text between them (a number or
  date only with digits) and keeps a name's surname; rebuilt with it, the corpus differs from the run's in those 11
  notes only, each now read as typed, except `XF3996-`, whose key asks for a second asset number the note does not
  hold: that mask stays unresolved. Use `index_as_run.py` to reproduce this run. Of the 3,000 passages the model saw,
  two differ between the builders: B-test-364's second ("engine 1" for engineV1, the one change of substance) and
  A-test-209's fifth, where the run's builder dropped the "#" typed before an asset number.
- **SAG-Wiki 0.3.11** deep search with its default retrieval settings, Qwen3-Reranker-0.6B @`e61197ed` through
  `decide.py` (No. 15's), in a network namespace with only loopback (`offline.sh`, `run.py`; each run recorded
  interfaces `["lo"]`), one company's folder per run, 21 Nov 2026, 15:41 to 15:44 AEST. Query: "What does this work
  order mean? <note as typed>". Ten passages a note, every one; median 0.59 s a search.
- **Into the prompt** (`ask.py`): No. 13's `prompt.md`, its glossary slot holding (as sent; the notes are the
  company's other notes, not dated) "Earlier work orders from this site, found by searching its own records, and what each meant. The same shorthand can mean something else at another
  site." and the ten passages as `typed = means` lines, in SAG-Wiki's order.

## The model

`RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead` (4-bit weights), the same server instance as No. 13 (vLLM 0.27.1 on 2 × RTX
5080, up since 19 Nov 2026; `answers/server.json` in the private run folder), thinking on, no sampling settings sent
(the server's defaults: temperature 0.6, top-p 0.95, top-k 20), `max_tokens` 16,000; one answer per note and
version, two at a time, the versions alternating; 21 Nov 2026, 15:45 to 16:58 AEST. All 600 answers parsed; none was
cut off. Files frozen before the run (SHA-256): `prompt.md` `7377f1ad…`, `ask.py` `9cfe095a…`, `index.py`
`16eb176d…`, `notes-test.json` `83ed8805…` (No. 13's, unchanged).

## How it was scored

1. **Script** (`score.py`, No. 13's with the versions renamed): per piece of shorthand, right, wrong, unsure or kept
   against MaintNorm's key. An answer without usable plain text keeps no meaning and stays in the 300.
2. **By hand, blind** (`handsheet.py`, rules in `handrules.md`, No. 13's gathered unchanged in substance): every
   answer of both versions, plus 40 of No. 13's recorded glossary answers (all 17 it judged meaning lost, 23 drawn
   with seed 16), each under a random id from the operating system's random source, shuffled into four sheets of
   160 (made at 17:03 AEST); four Claude readers, one sheet each, never shown the version. Their files are
   `hand/verdicts-*.txt`.
3. **Settled before unblinding** (17:07 AEST): the readers split on three questions, each settled by No. 13's recorded verdict on
   the same note (a doubtful key costs meaning only when the answer's reading does not fit the note; `5H` read as
   hours loses it; an asset code kept whole but called a work order keeps it); four entries changed, each noted in
   the verdict files.
4. **Calibration**: on the 40 archived answers the readers matched No. 13's meaning verdicts 36 times as read, 37
   after the settlement (which changed one archived answer, 5H); the three left were answers No. 13 had judged lost
   and these readers kept (two "quick fill" made "Kwik fill", one "Connect Inspect" made two tasks).
5. **After unblinding** (from 17:08 AEST, versions known; every change in `hand/after-unblinding.txt` with its
   reason, applied by the merge): the "Kwik" rule, two glossary answers to meaning lost ("Connect Inspect" was already
   judged so); after Codex's first page review, REQ read as a request right with meaning kept (No. 13's ruling;
   B-test-237, both versions), the date 4/8/8 kept as typed right (C-test-214, both) and J4, an asset id, made
   "position J4" to meaning lost (B-test-340 glossary, the only such answer); after its third, No. 13's same-note
   rulings applied the other way as well, by a scan of all 600 answers for readings matching one No. 13 judged
   differently: B-test-397 and B-test-274 glossary, C-test-295 and A-test-329 search, each to meaning kept. Nine
   verdicts and four single readings in all. Not changed: readings No. 13 recorded as kept ("repairs" for the
   unresolved REPS, A-test-105; "Replace the cooling system pressurising", B-test-364; "rotor chamber", the note's own
   words, B-test-113), "Inactivate" for the unresolved Inact (C-test-270 search; No. 13 kept "Inactive" and "Inact",
   not this instruction, so it is kept as the blind reader judged it), the trailing REPORT left out (A-test-329
   search, kept by No. 13's ruling on its own answer, against the written rule on a dropped word), "number 3" moved
   into the asset label (C-test-374 glossary), "requests resealing" for req's (B-test-397 glossary, kept by No. 13's
   ruling against the written rule, as A-test-329), "A Purchase Order is required"
   for PO (B-test-215, read like "Maintenance is required" for Maint in C-test-266), "Input Over Voltage (IOV)" with
   the code kept visible (C-test-299), "The 8 and 8 track rollers", which may name two rollers 8 (C-test-100), and
   C-test-246's "motor and blower" item, the answer already judged meaning lost. The result under all of these is the
   "stricter readings" above. `handsheet.py merge --blind-only` gives the result after the settlement made before
   unblinding, and `--as-read` the readers' verdicts as first written; each verdict file must declare the whole sheet it
   covers, or the merge refuses it.
6. `handsheet.py merge` rebuilds every sheet entry from the answers on disk and refuses to run if any differs from
   what its reader saw (all 600 matched), maps the ids
   back into `check.json` (with a digest of each answer read, so a verdict applies only to that answer); `score.py --final` refuses to report while an answer lacks one. `results.json` is the result.

Key doubts, as in No. 13: `A-test-267` ("TEMP REP", keyed temperature, read as temporary), `A-test-387` ("INTER
FACE", keyed internal face, read as interface) and `C-test-214` ("5H", keyed as an asset, read as 5 hours) stay
scored on the key in both versions alike.

## Replay the published scoring

`answers/` holds the 600 recorded answers (with each prompt as sent and the server's model list); `hand/` the four
blind sheets, the readers' verdicts, the id map and the changes made after unblinding. From this folder:

```bash
(cd hand && sha256sum -c SHA256SUMS)   # the published grading files, unchanged
python3 handsheet.py merge hand answers check.json --as-read     && python3 score.py notes-test.json answers --check check.json --final   # as first read: 286 / 273
python3 handsheet.py merge hand answers check.json --blind-only  && python3 score.py notes-test.json answers --check check.json --final   # settled: 287 / 273
python3 handsheet.py merge hand answers check.json               && python3 score.py notes-test.json answers --check check.json --final --out results.json   # final: 290 / 273
```

A verdict file lists only the entries that differ from the defaults, so a reader's completeness rests on its first
line, `# read <first id> to <last id>, all <n> entries`; the merge refuses a file without it, and a file with no
verdict lines at all unless it says `# no entry differs from the defaults`. The final merge needs
`hand/after-unblinding.txt` (only `--blind-only` and `--as-read` run without it); a file with no changes must say
`# no verdict changed after unblinding`. `hand/SHA256SUMS` lists every grading file as published.

## Repeat it

You need Python 3.10 or later, MaintNorm, Node.js 18+ and SAG-Wiki for the search (see No. 15's README for the
judge's Python environment), Linux with unprivileged user namespaces, and an OpenAI-compatible chat endpoint.

```bash
git clone https://github.com/nlp-tlp/maintnorm.git && git -C maintnorm checkout e98ca406f7afffbb0ab3243aa7c922f3b64bc7c8
python3 index_as_run.py maintnorm/data local/corpus               # this run's corpus; index.py (fixed) for a fresh run
python3 -c "import json; n=json.load(open('notes-test.json'))
for c in 'ABC': json.dump([{'id': x['id'], 'text': 'What does this work order mean? ' + x['text']} for x in n if x['company'] == c], open(f'local/questions-{c}.json', 'w'))"
SAG=/path/to/sag QWEN=/path/to/Qwen3-Reranker-0.6B URL=http://127.0.0.1:8000/v1/chat/completions MODEL=your-model-id   # yours
for c in A B C; do
  ./offline.sh python run.py --sag "$SAG" --corpus local/corpus/$c --questions local/questions-$c.json \
    --out local/search/$c --modes deep --scorer "qwen3rr:$QWEN" --label qwen-rr --limit 10
done
python3 ask.py notes-test.json local/search local/answers --url "$URL" --model "$MODEL"
python3 coverage.py maintnorm/data local/search local/answers --out coverage.json
python3 handsheet.py make notes-test.json local/answers ../work-order-shorthand-glossary/results.json local/hand
# read the four sheets blind, write local/hand/verdicts-1..4.txt, then:
python3 handsheet.py merge local/hand local/answers check.json
python3 score.py notes-test.json local/answers --check check.json --out results.json --final
```

## Limits

One model, one answer per note and version, sampled; the glossary's run-to-run difference above is nearly as large as
the same-day gap between versions. One annotator's key, three readings in doubt. Both versions rest on the annotator's reading of the same
3,200 notes: the glossary's 50 lines were counted from them by a script, the search reads them all. A site would have
to write such readings; this test did not measure that work. its index carries that reader's
mistakes too ("BRAKE PACS" = brake pads). Three companies' notes, mostly heavy mobile equipment. The hand check was
made by AI readers (Claude), not a planner. MaintNorm has been public since 2024; the model may have met these notes.

## Files

| File | What it is |
|---|---|
| `index.py`, `index_as_run.py`, `offline.sh`, `run.py`, `decide.py` | The search corpus (fixed builder; the builder as run) and the offline search (No. 15's runner and judge) |
| `prompt.md`, `ask.py`, `glossary/` | The instruction, the runner, No. 13's glossaries |
| `score.py`, `handsheet.py`, `handrules.md`, `hand/` | Scoring, the blind sheets and their merge, the rules, the readers' verdicts |
| `coverage.py`, `coverage.json` | What each version supplied, prompt sizes, near-duplicates |
| `retrieved.json` | For each test note, the ten notes the search returned, in order, as MaintNorm training-split indices |
| `notes-test.json`, `prepare.py` | No. 13's 300 notes and how they were drawn |
| `check.json`, `results.json` | The hand check and every answer, scored |
| `answers/` | The 600 recorded answers, each with its prompt as sent |
| `protocol.md` | The plan, the reviews and what happened |

Code: MIT. Data derived from MaintNorm: MIT, © 2024 NLP-TLP Group.
