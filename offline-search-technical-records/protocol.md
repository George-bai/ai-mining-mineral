# Plan: which local model finds the whole answer in a mine’s reports?

Protocol written 21 Nov 2026 (AEST) before any search run on the archive. Brief: `brief.md` (George's plan file).
Research behind it: Codex runs r1–r4 (SAG-Wiki, decision models, Cadia records, rerankers and measures), kept in the
session scratch folder and summarised here.

## The question this tests

Can SAG-Wiki, an open-source document search application, find the passages that answer a site engineer's question
in a mine's public technical records with **no network but loopback**, when its decision step (the model that judges
whether a passage is needed evidence) runs on this workstation? And does a local decision model put the whole answer
in front of the reader within the first five excerpts, from the edition asked for?

Only passages are tested. No answer prose is generated.

## The archive (five public records)

| id | Record | Source | Pages |
|---|---|---|---|
| newcrest-2021-12-quarterly | Newcrest quarterly report, December 2021 quarter (28 Jan 2022) | ASX PDF | 22 |
| newcrest-2022-03-quarterly | Newcrest quarterly report, March 2022 quarter (28 Apr 2022) | issuer archive PDF (s24.q4cdn.com) | 24 |
| newcrest-2022-06-quarterly | Newcrest quarterly report, June 2022 quarter (21 Jul 2022) | ASX PDF | 22 |
| newmont-cadia-trs-2024 | Newmont, Cadia Valley Operations technical report summary, Feb 2024 (filed 29 Feb 2024) | SEC EDGAR, Exhibit 96.6 | 266 printed + cover |
| newmont-cadia-trs-2026 | Newmont, Cadia Valley Operations technical report summary, Feb 2026 (filed 19 Feb 2026) | SEC EDGAR, Exhibit 96.2 | 240 printed + cover (first written 239; 241 pages indexed, counted after the run) |

URLs in `local/sources.json`. SHA-256 of the downloaded files: `newcrest-q4-2021.pdf` 48539c7f…7dda7,
`newcrest-q1-2022.pdf` 03994af1…2831, `newcrest-q2-2022.pdf` be55dc11…9756, `newmont-cadia-trs-2024.htm`
2b85c421…b2e8, `newmont-cadia-trs-2026.htm` 8858f75f…d4b7 (first written …b4d9, a typo) (full hashes in `public/README.md`). The SEC files were
fetched with a declared User-Agent naming George, as SEC's access policy requires (his choice, 21 Nov 2026).

**Reuse.** ASX's terms do not permit republishing its announcements; SEC filings are free to reuse with credit. The
public folder therefore holds the URLs, hashes and scripts, never the PDFs or their extracted text. The page quotes a
sentence or two per excerpt shown, attributed, for review.

## Text extraction (local, no model)

`public/prepare.py`: PDF pages through poppler's `pdftotext`, one page at a time; the SEC exhibits are page images
whose text sits in a hidden layer, split at each running header into printed pages ("Page 14-3"). One Markdown file
per record: `# <record label with date>` then `## Page N` per non-empty page; wrapped lines inside a paragraph joined,
nothing else changed. 576 non-empty pages, 174,481 words.

Why not SAG-Wiki's own PDF conversion: in 0.3.11 offline, `sag add` of a PDF failed with "needs the Docling document
component" (an optional download), and it indexes HTML as source text with the markup. Extracting the text ourselves
keeps every system on the same text.

## Two collections

- **Focused:** the 26 pages whose text names the plant (`(?i)(molybdenum|moly)\s+plant`), all five records.
- **Full:** all 576 pages.

## Systems (SAG-Wiki 0.3.11, the npm CLI current on 21 Nov 2026)

| Label | Search | Decision service on this machine |
|---|---|---|
| keyword | SAG-Wiki fast search over HTTP (`mode: fast`): SQLite FTS5 BM25, title 2, heading 2, body 1 | none |
| tinybert | SAG-Wiki deep search (SAG2) | `cross-encoder/ms-marco-TinyBERT-L2-v2` @81d1926f, through `decide.py` |
| minilm | deep | `cross-encoder/ms-marco-MiniLM-L6-v2` @233902d2, through `decide.py` |
| qwen-rr | deep | `Qwen/Qwen3-Reranker-0.6B` @e61197ed, official yes/no prompt, SAG-Wiki's criterion as the instruction |
| hindsight | deep | `hindsight-ai/hs-decide-1-flash` @e2c78902 (0.8B), its own `DecisionModel.answer()` |
| d1 | deep | `LiquidAI/d1-2B` @a6bce774 (1.9B), its own `system_one()`, PyTorch path (no C compiler for Triton) |
| knowline | deep | `PelaAI/KnowLine-4B-Gen5` @dba367c5, its own `knowline_server.py --backend hf` on the CPU |

The first three are rerankers: they see only the question and one passage. The last three are decision models built
for this protocol; they receive SAG-Wiki's request unchanged (question, kept evidence, criterion, candidate).
GPU models run on the 32 GB RTX 4080 SUPER (memory-modified; the retail card has 16 GB, noted 22 Nov 2026; about 7.5 GB free beside the services already on it). KnowLine needs about
13.6 GB on a GPU, more than is free, so it runs on the CPU (Threadripper 7960X). `decide.py` logs every request and
answer.

All SAG-Wiki settings are its defaults, except the decision endpoint (`sag config --url … --auth none`). Each excerpt
list is SAG-Wiki's own order, up to 10 (`-m 10` / `limit: 10`).

## Offline

Every run starts in a new user and network namespace (`unshare -rn`) holding only `lo`; `run.py` refuses to start if
it sees another interface or reaches 1.1.1.1 or 8.8.8.8, and records the interface list. Hugging Face libraries run
with `HF_HUB_OFFLINE=1`. Documents, weights and packages were fetched beforehand.

## Questions and key (`public/questions.json`, frozen)

SHA-256 `7f2ef0d76cd352c927adcd2072cd2b1c66937a653879585f8516b0cab3e59a21` (after both protocol checks; see below). Twelve questions written before any run:
the brief's question in three forms (q01 names both reports, q02 uses "moly plant" and no edition, q03 requires the
February 2026 design), one question these records cannot answer (q04, recovery on one shift), seven single-fact
questions and one two-part question about the same plant. Each fact names the pages that prove it and a phrase the
displayed excerpt must contain; `score.py --check-key` confirmed every phrase sits on exactly the pages listed, in the
full collection. One marker was corrected before freezing (packing: "bulk bags" also appears on pages 16-2 about
shipping, which do not say how the concentrate is dewatered).

## Outcomes

The **full archive is the primary collection**; the focused set (chosen by the plant's name) is the easy case.

- **Primary: complete evidence@5.** The first five excerpts, in the order shown, together display every fact the
  question needs: for some page listed for that fact, the excerpts from that page display all of its phrases (and from
  the named edition where the question names one). Only the first 10 displayed excerpts count, in both modes (deep
  search can display more than 10 source ranges for 10 chunks). An excerpt that shows
  the right sentence from the other edition counts as "right fact, wrong edition", not as the fact.
- Complete evidence@10; right pages@5 (an excerpt from a right page among the first five, whether or not it displays
  the words); first rank of each fact; excerpts returned; seconds per question.
- **q04 (no answer exists):** excerpts returned, and the recovery figures they display (life-of-mine forecasts,
  recovery models, testwork) that a reader could mistake for a shift figure. A list of zero excerpts is the honest
  result.

Scored by script (`score.py`, rules tested in `test_score.py`), then every excerpt list read by hand beside the key,
blind to the system (lists shuffled and relabelled); any correction goes in
`public/check.json` with its reason, applied by the script. Unchecked numbers are not published.

## Repeats

Each system runs twice per collection, each time from a new empty index and a new decision process, to show whether
the lists repeat. KnowLine (CPU) runs once per collection if two take too long; that is stated.

## Limits known before the run

One archive, one site, twelve questions written by one person who had read the pages (a field trial needs unseen
questions from a metallurgist). Public records, possibly in a model's training data. SAG-Wiki defaults only. One
machine.

## Protocol review (Codex, gpt-6.2-astra xhigh, read-only, 21 Nov 2026, before any run on these questions)

"Hold launch" until: `run.py` read the questions list (it would have failed on the file's note); `score.py` kept fast
and deep apart and reported any missing question instead of shrinking the denominator; the key named every phrase
that must be visible (a single marker passed a reagents excerpt that cut the list, and "suite of consumable products"
also opens the concentrators' sentence); both modes capped at 10 displayed excerpts; q05, q08, q09 and q12 worded so
the keyed pages are the only full answers (four pages give only the year 2022 for commissioning; p. 22-6 gives a
5,000 t/a ramp-up target, not the design capacity); the full archive primary; the index checked ready with all five
records. All done before launch. Kept: complete evidence@5 in displayed order as the primary measure, the loopback
namespace as the offline control, KnowLine's server inside the same namespace, q04 reported apart.

Also changed after a timing pilot on a question outside the set: d1-2B ran out of GPU memory on SAG-Wiki's default
32,000-token decision batches beside the services already on the card, so its runs set SAG-Wiki's own per-batch budget
(`jev_context_tokens`) to 16,000. KnowLine's server refuses more than 64 questions a request, which SAG-Wiki does not
read as a batch limit, so `decide.py` sends larger batches to it in parts of 64 with the same state.

Second check (Codex, same settings, before launch): "Hold" for five defects, all fixed before launch: scores and hand
corrections keyed by mode as well as question; a run without `run.json` reported as a problem; the raw excerpt count
kept beside the capped count; a true median; "dried" required on the four packing pages; the index checked against
the five expected file names; KnowLine's readiness wait gives up if its server dies, and `run.py`'s exit code is kept.
Launched 21 Nov 2026 after these fixes without a third check.

## During the runs (21 Nov 2026, AEST)

- 11:22–11:30: keyword and the five GPU setups, both collections, twice each. Every repeat list was identical to the
  first, excerpt for excerpt (144 pairs).
- KnowLine's first attempt (11:30) failed on its first question with "model connection failed" before any list was
  recorded: SAG-Wiki waits 120 s for a decision request (`timeout_secs`), retries for 600 s in all, and sends up to 20
  batches at once, while KnowLine on the CPU takes about 110 s for one batch of 50 candidates. Restarted at 11:42 with
  SAG-Wiki's own settings `timeout_secs` 3600, `jev_concurrency` 2 and `retry_total_secs` 14400 (`run.py
  --sag-settings`, which replaced the narrower `--jev-context` used for d1's 16,000-token batches; same effect).
  KnowLine runs once per collection, as planned for a slow system.
- Hand check: the 137 distinct lists of the keyword and GPU runs (288 runs) went to four readers (Claude subagents)
  in shuffled order without the setup's name, with the key and the rules; 172 fact judgements, all equal to the
  script's. Two borderline calls, the same both ways: the summary pages 1-19 (2026) and 1-20 (2024) say "the rougher
  tails" rejoin the Blayney pipeline without "copper-rich"; the key accepts them. I re-read the q01–q03 lists myself.
- KnowLine second attempt (11:42, 2 batches at a time, its server's default 16 scoring threads): one batch of 50 in
  107 s, then nothing for 14 minutes; two batches with 16 threads each, every thread using all 24 cores, starved one
  another. Stopped before any list was recorded and restarted at 11:58 with `jev_concurrency` 1 and
  `knowline_server.py --workers 1` (one forward pass at a time, using every core): 50 candidates in 66 s.
- KnowLine third attempt, stopped at 12:14: the first batch (50 candidates, no evidence kept yet) took 66 s; the
  second, in the expansion round with the kept evidence in every prompt, had not finished after 15 minutes. Its model
  log says its linear-attention layers run on a slow reference implementation (no `causal_conv1d` or
  `flash-linear-attention` kernels, which are GPU code). Twelve questions on two collections would take days. KnowLine
  is reported as tried and not compared; it needs a free GPU of about 14 GB, as the brief's next site-GPU trial
  proposes. No KnowLine list exists, so nothing of it is scored.
- George's go-ahead (21 Nov 2026, after the first staging): "Stop the speech recognition model for your experiment but
  bring it back after your testing." The `qwen3-asr` container (vLLM, Qwen3-ASR-1.7B, GPU 2) was stopped at 12:52:40
  and started again at 13:30:20 AEST by the same script that ran KnowLine, with its original command; it answered
  `/v1/models` again and the card returned to about 24.8 GB in use. KnowLine ran on GPU 2 (`knowline_server.py --device
  cuda`), same SAG-Wiki settings as the CPU attempt, each collection twice: 47 s median a question, peak 22,106 MiB for
  its process, repeats identical (24 of 24 lists).
- 21 Nov 2026, after the KnowLine runs: George chose a new title, "Which local model finds the whole answer in a mine’s reports?" (option 2 of six offered), in place of
  "Can a mine search its own technical records offline?". The address stays /articles/offline-search-technical-records/.

## Renumbered (21 Nov 2026, AEST)

George asked for an introduction to SAG2 and SAG-Wiki to come first: it is No. 14 (`../sag2-offline-evidence-search/`),
and this comparison is No. 15. Nothing else changed. No. 16 (`../work-order-shorthand-past-notes/`) uses this
article's best judge on maintenance work orders.

## Corrected after staging (22 Nov 2026, AEST)

A staging review (Codex, `reviews/staging-articles-14-16-2026-11-22.md`) found that the key's
"filtered-2021" fact misdates its milestone. Checked by a Codex research run (read-only, web): Newcrest's half-year
results presentation of 17 Feb 2022 (slide 11) and its BMO presentation of 28 Feb 2022 (slide 10) date filtered
molybdenum concentrate production to January 2022; Cadia's annual environmental management report 2021-22 (section
4.2.3) has concentrate first fed in December 2021 and the first bulk bag on 27 January 2022; the December-quarter
report (released 28 January 2022) gives no date. So no record in the archive answers "what had been achieved by the
end of 2021". Corrected: the fact's wording (id kept), the timeline (filtered concentrate from January 2022), the
section 01 lede, the findings' wording and the winner claim (Qwen3-Reranker-0.6B's lead comes all from q01-q03; on the
other eight answerable questions five setups tied at 8 of 8). The runs and scores are unchanged. Also: "checked by
hand" now says Claude readers; `score.py` refuses an empty runs folder, an empty key file and (unless `--focused`) a
missing evidence page; `run_everything.sh` exits non-zero and logs the count when a run fails. Not done without
George's decision: rewording q01-q03 and running all seven setups again (KnowLine needs the speech service paused).

## Re-run of the two-record question, dated (planned 22 Nov 2026, AEST, before any search with the new wordings)

George asked for it on 22 Nov, after the correction above. Questions `q13`-`q15` (`public/questions-dated.json`)
repeat q01-q03 word for word except the second half's date: "what had been achieved ... by the end of 2021" becomes
"what does the [December 2021] quarterly report say had been achieved", so the half asks for what the record says.
Each keeps its original's form (naming both reports; site shorthand, now naming the quarterly to carry the date;
requiring the 2026 edition). Key: the same two facts and pages as q01-q03 (`feed`, strict to the 2026 edition in q13
and q15; `filtered-2021`, the December-quarter report's page 3 passage).

Run exactly as the original runs: the same seven setups, settings, SAG-Wiki 0.3.11, models and revisions, both
collections, each twice from a fresh index, offline (`run_all.sh` with `questions-dated.json`), into a separate runs
folder so the recorded runs stay as they are. The speech-recognition service on the GPU is stopped only while KnowLine
runs and started again straight after (George's go-ahead, 22 Nov). Scored by `score.py --questions
questions-dated.json`; every distinct list read blind by Claude readers (`handsheet.py`), as before.

Reported: per setup, whole answer in the first five for q13-q15, all 576 pages and the 26 plant pages; with the other
eight answerable questions (seven single-fact, and q12's two dates; "eight single-fact" before the run, corrected after
it), the setup totals of 11. q01-q03 stay in the repository as recorded and are no longer reported
as the two-record result.

### What happened (22 Nov 2026, AEST)

Codex reviewed the plan before any run (`Go`; it asked that a change in score be credited to the named, dated report,
not the date alone, and that the recorded runs be protected: done, with a separate `local/dated` folder). Runs: the six
setups 10:48 to 10:52; the speech service stopped 10:52:36, KnowLine 10:52 to 11:01, the service started again
11:01:13; 28 runs, none failed, every run's interfaces `["lo"]`, repeats identical. Blind check of the 42 distinct
lists by two Claude readers: all 84 "shown" judgements agreed with `score.py`; "wrong_edition" differs by definition
only. Result, whole answer in the first five, all 576 pages, of 3: Qwen3-Reranker 3, KnowLine 2, MiniLM 1, the rest 0
(26 plant pages: KnowLine 3, Qwen3-Reranker 2, MiniLM 1, Hindsight 1, the rest 0). With the other eight answerable
questions, of 11: Qwen3-Reranker 11, MiniLM 9, KnowLine 9, keyword, TinyBERT and Hindsight 8, d1-2B 7.
