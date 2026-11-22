# Plan: the work-order test again, with the search that won No. 15 (No. 16)

Protocol written 21 Nov 2026 (AEST) before any held-out note was searched or sent to the model for this article
(a pilot searched three company-A notes to check the pipeline; no model answer was made). Brief: `brief.md`.

## Question

No. 13 found that a 50-line glossary built from a company's own work orders helped a local LLM read held-out notes
(meaning kept 283 of 300 with it, 228 without). The glossary is fixed: it covers the 50 most used forms and nothing
else (59–82 % of the shorthand in new notes). No. 15 found that SAG-Wiki's deep search with Qwen3-Reranker-0.6B put
the whole answer in the first five passages most often, offline. **Does that search, run over the same company's
earlier work orders, help the model read a note as much as the glossary, or more?**

## What is searched

Per company, the 3,200 notes of MaintNorm's train split (the notes No. 13's glossary was built from; no val or test
note): `index.py` writes one Markdown file per company, one heading per note as typed, and under it "Means: ..." with
the annotator's reading (masked asset numbers, numbers and dates put back as typed). That is a site's history of work
orders with a planner's reading of each, the same source the glossary used.

## The search (No. 15's winner, unchanged)

SAG-Wiki 0.3.11 deep search, Qwen3-Reranker-0.6B through `decide.py`, SAG-Wiki's defaults, in a loopback-only
namespace (`offline.sh`, `run.py`), one company's folder per run. Query: "What does this work order mean? <note as
typed>". All passages SAG-Wiki returns (its default limit, 10) go to the model, in its order. Search results are
saved before any model call; they are not looked at for tuning.

## The model (No. 13's, unchanged)

Qwen 3.8 27B (`RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead`, vLLM 0.27.1 on 2 × RTX 5080), the same server instance that
produced No. 13's answers (container up since 19 Nov 2026), No. 13's `prompt.md`, no sampling settings sent (server
defaults: temperature 0.6, top-p 0.95, top-k 20), thinking on, one answer per note and version, two at a time.

Versions:
- **search** (new): the prompt's glossary slot holds "Earlier work orders from this site, found by searching its own
  records, and what each meant. The same shorthand can mean something else at another site." and the passages as
  "typed = means" lines.
- **glossary, second run** (new): No. 13's glossary version again, the same day as the search version, to show how
  much a run varies and to compare search with glossary under the same conditions.
- No. 13's two recorded versions (none, glossary) are reported beside them, as recorded.

## Notes

No. 13's 300 held-out notes (`notes-test.json`, 100 per company, seeded, each with shorthand, none repeating a train
or val note), unchanged.

## Scoring

No. 13's `score.py` first pass (each piece of shorthand right, wrong, unsure or kept against MaintNorm's key) and No.
13's hand-check rules (`../work-order-shorthand-glossary/plan.md`: meaning kept, diagnosis added, said done, other
addition), on every new answer. The hand check is blind: the readers (Claude subagents) see each note with two
answers labelled x and y in an order drawn from the note id (search and glossary second run) and do not know which is
which. Calibration: No. 13's recorded verdicts for its glossary answers are compared with the readers' verdicts on the
same-day glossary rerun only where the two answers are identical in plain text; otherwise disagreements are reported.

Also counted without a model: **search coverage**, the share of the 508 pieces of shorthand in the 300 notes whose
written form appears, with the key's meaning, in at least one passage the search returned for that note (No. 13's
glossary covered 72 % (A), 82 % (B), 59 % (C) of the test split's shorthand with 50 lines).

## Outcomes

Primary: notes whose meaning was kept, of 300, search against the same-day glossary run (paired by note: how many
only with search, only with the glossary; exact McNemar). Then: shorthand read right/wrong; diagnoses added; work
said done; additions; per company; search coverage; and how the same-day glossary run compares with No. 13's (283).

## Limits known before the run

One model, one answer per note and version, sampled; one annotator's key; MaintNorm public since 2024 (the model may
have seen the notes). The search corpus carries the annotator's reading of every earlier note, which a real site
would have to build; the glossary needed only 50 lines of it.

## Changes after the protocol review (Codex, 21 Nov 2026, before any model answer was made)

Adopted from the review (`reviews/codex-protocol-review-work-order-shorthand-past-notes-2026-11-21.md`): the scorer reads the versions `search` and `glossary`; the index fills masked
quantities and identifiers back from the typed note (`2000H` keeps its 2000; corpus rebuilt and every search run again
on it); `ask.py` reads the search results by company; an answer without usable plain text keeps no meaning, and stays
in the 300; prompt sizes and the 508 pieces' coverage are reported for both versions under one rule.

## The hand check, settled before any answer was read (21 Nov 2026, AEST)

- **Blind by single answers, not pairs:** every answer of both versions, plus 40 of No. 13's recorded glossary
  answers (all 17 it judged meaning lost, 23 drawn from the rest with seed 16), each under a random four-digit id from
  the operating system's random source, shuffled, split into four sheets (`handsheet.py`). A sheet never shows the
  version; the map stays in `local/hand/map.json` until every sheet is read. No. 13 published its x/y mapping, so its
  scheme is not reused.
- **Readers:** four Claude readers, one sheet each, with `handrules.md` (No. 13's rules, gathered unchanged in
  substance). Their verdicts are merged by `handsheet.py merge` into `check.json`, which `score.py` applies.
- **Calibration:** the readers' meaning verdicts on the 40 archived answers are reported beside No. 13's recorded
  ones, before the versions are unblinded.
- **Coverage** (`coverage.py`, no model): a piece of shorthand is covered when its form and the key's meaning appear in
  one place: a glossary line, or one returned passage (a word of the earlier note with that form, and every word of the
  meaning in that passage's "Means" line). Near-duplicates: test notes equal to a training note once the tokens the
  key masks as asset numbers are removed, ignoring case; reported, not removed.

## Settled after reading, before unblinding (21 Nov 2026, 17:07 AEST)

The last answer came at 16:58 AEST; the sheets were made at 17:03. The four readers finished their sheets (160
entries each) and split on three questions; each was settled by No. 13's
recorded verdict on the same note, applied to every entry it touches, before `map.json` was opened:
- a doubtful key costs meaning only when the answer's reading does not fit the note: `INTER FACE` read as interface
  keeps it (one reader had marked it lost); `TEMP REP` read as temperature repair loses it, as the readers had it;
- `5H` (keyed as an asset) read as 5 hours loses meaning (two entries a reader had kept);
- an asset code kept whole but called a work order ("Work order WK1566") keeps meaning, as a numeric one does (one
  entry a reader had marked lost); a code changed ("Work order 1566") loses it.
Each change is a comment or line in `local/hand/verdicts-*.txt`, copied to `public/hand/`.

## After unblinding (21 Nov 2026, from 17:08 AEST; versions known)

Calibration: the readers' meaning verdicts agreed with No. 13's recorded ones on 37 of the 40 archived answers; all
three differences were answers No. 13 had judged meaning lost and the readers kept: two "quick fill" made "Kwik fill"
(a brand) and one "Connect Inspect" made two tasks. Both rules were then applied to every new answer they touch, in
both versions, by text search: "Kwik" for "quick" in two glossary answers (C-test-072, C-test-336), changed to meaning
lost; "Connect Inspect" in C-test-246, already judged so (glossary lost, search kept).

Codex's page review (17:13 to 17:19) raised further verdicts; each was checked against No. 13's ruling on the same note
and the rules, and the adopted ones applied to every answer the rule touches in both versions (text search), at 17:22:
REQ read as a request is right with meaning kept (No. 13's ruling; B-test-237, both versions); the date 4/8/8 kept as
typed is right (No. 13's ruling; C-test-214, both); J4, keyed as an asset id, made "position J4" loses meaning
(B-test-340 glossary; no other answer does this). Not adopted, because No. 13 recorded the same reading as kept:
"repairs" for the unresolved REPS (A-test-105), "Replace the cooling system pressurising" (B-test-364), "rotor chamber"
as the note writes it (B-test-113), "Inactive"/"Inactivate" for the unresolved Inact (C-test-270); and "A Purchase
Order is required" for PO (B-test-215), read like "Maintenance is required" for Maint (C-test-266), neither an
addition. All changes made with the versions known are in `public/hand/after-unblinding.txt`; `handsheet.py merge
--blind-only` reports without them. Blind: search 287, glossary 273 (22 against 8, p = 0.016); with them: 288 and
271 (24 against 7, p = 0.003). The calibration agreement, 37 of 40, counts one archived answer (5H) changed by the
settlement above; as read, 36 of 40.

Codex's second page review (finished 17:31 AEST) proposed seven more verdicts lost, with the versions known (five
glossary, two search). None was adopted: each is a reading No. 13 recorded as kept, the note's own words, or an
expansion that keeps the code visible; A-test-296's "Perform a lockout" is a misreading of LOCK (meaning already lost),
not an addition. The result under all seven is reported as a sensitivity check (286 against 266). The merge now refuses
to run if any answer differs from what its sheet showed; all 600 matched.

Codex's third page review pointed out that No. 13's same-note rulings had been applied only where they took meaning
away. All 600 new answers were then scanned for readings matching one No. 13 judged differently on the same note (word
overlap, then read): four matched and were set to No. 13's ruling, all to meaning kept (B-test-397 and B-test-274
glossary, C-test-295 and A-test-329 search); the other differences were different readings. The merge now rebuilds
each sheet entry from the answers on disk and refuses any that differ (all 600 matched). Adjudicated: search 290,
glossary 273 (22 against 5, p = 0.0015). C-test-100's glossary answer ("The 8 and 8 track rollers") was left as
read and added to the stricter readings (288 against 267).

Codex's fourth page review: a broader near-duplicate check (asset numbers inside tokens removed too) finds 57 notes;
without them, 234 against 219 of 243 (19 against 4). Narrowed at the fifth review to tokens the key marks as holding
an asset number (it had also erased W44 and No13): 55 notes; without them, 236 against 221 of 245 (19 against 4).
B-test-397 glossary ("requests resealing", kept by No. 13's ruling against the written rule) joins the stricter
readings: 287 against 265 (29 against 7, p = 0.0003). A-test-329 search (kept by No. 13's ruling against the written
rule on a dropped word) and C-test-374 glossary join the stricter readings: 287 against 266 (28 against 7).
Correction to the entry after the second review: No. 13 kept "Inactive" and "Inact" for C-test-270, not the search's
"Inactivate"; that answer stands as the blind reader judged it, and is in the stricter readings. The
day-to-day glossary difference is not assigned to readers: all 20 changed verdicts had different answer text, and all
77 word-for-word repeats got the same verdict.

Codex's sixth page review: the index's reconstruction garbles 7 of the 9,600 notes (an asset number run into a word,
or a number sharing a token with one); one such passage reached the model (B-test-364, "engine 1" for engineV1), whose
search answer kept its meaning. Disclosed; `index.py` kept as run. B-test-274 glossary and C-test-295 search, set back
to kept by No. 13's rulings, join the stricter readings with their blind verdicts: 286 against 264 (30 against 8).
The day-to-day note now says 77 identical plain-English readings (71 also identical in terms and unsure list).

Codex's seventh page review: the page states 290 against 273 as the final verdicts with the stricter 286 against 264
beside it. The builder as run is kept as `index_as_run.py`; `index.py` now aligns the annotator's words with the typed
token (all eight garbled tokens read correctly; the scan also found a date and a name case).

Codex's eighth page review: the fixed builder now takes only digits for a number or date, keeps a name's surname and
leaves an unmatched asset mask unresolved; rebuilt with it, the corpus differs from the run's in 11 notes, each read
as typed (one mask left unresolved). Of the 3,000 passages the model saw, only B-test-364's second differs in
substance (and A-test-209's in keeping a typed "#").

## No. 15 corrected (22 Nov 2026, AEST)

This article chose its judge, Qwen3-Reranker-0.6B, as the one that did best in No. 15. No. 15 has since corrected
the second half of its two-record question (the milestone it credits was reached in January 2022, not by the end of
2021), and its lead came all from that question: on No. 15's other eight answerable questions, five ways of searching
found every answer. The judge is described accordingly; the runs here are unchanged.

Update, 22 Nov 2026: No. 15 asked its two-record question again with the date and ran every setup again.
On all 576 pages, Qwen3-Reranker-0.6B was the only setup with both facts in the first five in all three wordings
(KnowLine 2, MiniLM 1, the rest none; on the 26 plant pages KnowLine 3, it 2), and its total stays 11 of 11 on all 576 pages. The choice of judge stands.
