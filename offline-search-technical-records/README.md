# Which local model finds the whole answer in a mine’s reports?

Code and data for Eleticle Core Log No. 15 (https://eleticle.com/articles/offline-search-technical-records/).

Five public records on Cadia's molybdenum plant (576 pages) were indexed in SAG-Wiki 0.3.11, an open-source document
search application, on one workstation whose indexing, search and model scoring could connect only within it. Twelve questions were asked by keyword search
and by deep search, where a local model judges each candidate passage. A question counts when the first five
excerpts SAG-Wiki displays hold its whole answer, from the pages the key names. Every list was then read by Claude
readers, blind to the setup.

**Corrected 22 Nov 2026: the first filtered concentrate.** q01-q03 ask what had been achieved at the plant "by the end of 2021",
and the key credited the December-quarter report's page 3 passage (in our words: commissioning continuing, a filtered
molybdenum concentrate already produced) as saying it had happened by then. That report was released on 28 January 2022, and Newcrest's half-year
results presentation (17 Feb 2022, slide 11) dates the start of filtered-concentrate production to January 2022; the
Cadia annual environmental management report for 2021-22 (section 4.2.3) has concentrate first fed to the plant in
December 2021 and the first bulk bag on 27 January 2022. No record in this archive says what had been achieved by 31
December 2021, so the second half of q01-q03, as worded, has no answer here. The key's fact keeps its id
(`filtered-2021`) and now says what the passage does; the runs and scores are unchanged, and they measure finding that
passage. **Re-run with the date, 22 Nov 2026.** `questions-dated.json` asks
q01-q03 again as q13-q15, changing only the date phrase: "what does the [December 2021] quarterly report say had been
achieved" (q14 and q15 now name the quarterly, a clue keyword search can use; the change is to a named, dated
report, not the date alone). Every setup ran again, as before (same settings, offline, both collections, twice, the
repeats identical; the speech service on the GPU stopped 10:52 to 11:01 AEST for KnowLine), into
`local/dated/runs`, and every distinct list (42) was read blind, split between two Claude readers (21 lists each, none
read twice): all 84 judgements of where each fact first shows agreed with `score.py`; the place of the 2024 edition's
copy differs in 10 lists only by definition (the script records it even after the 2026 page, the readers only before),
which changes no score (`check.json`, `dated_lists`, `dated_note`). Whole answer in the first five, all 576 pages, of 3:
Qwen3-Reranker 3, KnowLine 2, MiniLM 1, keyword, TinyBERT, Hindsight and d1-2B 0 (6 of 21 searches; first asked, 7);
on the 26 plant pages, KnowLine 3, Qwen3-Reranker 2. KnowLine's lists for q14 on all pages held both records in the
first five but the quarterly's milestone page only at place 7: the count is of the keyed passages, not the records.
With the eight other answerable questions, of 11: Qwen3-Reranker 11, MiniLM 9, KnowLine 9, keyword 8, TinyBERT 8,
Hindsight 8, d1-2B 7. The page and the tables below show q13-q15 in the places of q01-q03; the summary keeps q01-q03
as first asked.

<!-- summary:start (figures.py) -->
| Setup | Whole answer in the first five, all 576 pages (of 11) | The 26 plant pages (of 11) | The two-record question, three dated wordings (q13-q15), all pages (of 3) | As first asked (q01-q03, no answer in the records as worded), all pages (of 3) | Median time a question, all pages, first run | Runs |
|---|---|---|---|---|---|---|
| Keyword | 8 | 8 | 0 | 1 | 10 ms | 2 per collection, identical |
| TinyBERT | 8 | 8 | 0 | 1 | 110 ms | 2 per collection, identical |
| MiniLM | 9 | 9 | 1 | 0 | 140 ms | 2 per collection, identical |
| Qwen3-Reranker | 11 | 10 | 3 | 3 | 1.1 s | 2 per collection, identical |
| Hindsight | 8 | 6 | 0 | 0 | 2.7 s | 2 per collection, identical |
| d1-2B | 7 | 6 | 0 | 0 | 3.7 s | 2 per collection, identical |
| KnowLine | 9 | 10 | 2 | 2 | 46.7 s | 2 per collection, identical |
<!-- summary:end -->

## The records

| id | Record | Pages | SHA-256 of the file used |
|---|---|---|---|
| newcrest-2021-12-quarterly | Newcrest, quarterly report for the quarter ended 31 Dec 2021 (28 Jan 2022), [ASX PDF](https://announcements.asx.com.au/asxpdf/20220128/pdf/455cvnlbn3cp01.pdf) | 22 | `48539c7fc9fcf749848cda8b4b871308961816d204d596cd932fed1ebe57dda7` |
| newcrest-2022-03-quarterly | Newcrest, quarter ended 31 Mar 2022 (28 Apr 2022), [issuer archive PDF](https://s24.q4cdn.com/382246808/files/doc_downloads/Newcrest/quarterly/22/220428_Newcrest-Mar-2022-Quarterly-Report.pdf) | 24 | `03994af17c580e6c007422f62bd9dd4c959d35f16c0b86fb82d1d949acbb2831` |
| newcrest-2022-06-quarterly | Newcrest, quarter ended 30 Jun 2022 (21 Jul 2022), [ASX PDF](https://www.asx.com.au/asxpdf/20220721/pdf/45c17j041vvb1d.pdf) | 22 | `be55dc111394fe916cc286a21212c7fd970cf3c27107b05b12c5834ff5759756` |
| newmont-cadia-trs-2024 | Newmont, Cadia Valley Operations technical report summary, Feb 2024, Exhibit 96.6 (filed 29 Feb 2024), [SEC](https://www.sec.gov/Archives/edgar/data/1164727/000116472724000016/exhibit966-cadiaoperatio.htm) | 267 indexed (printed pages and cover) | `2b85c421d9668d89a0aa365afd871c03e4bedfc5bd5915ce723dbb26d83db2e8` |
| newmont-cadia-trs-2026 | Newmont, Cadia Valley Operations technical report summary, Feb 2026, Exhibit 96.2 (filed 19 Feb 2026), [SEC](https://www.sec.gov/Archives/edgar/data/1164727/000116472726000010/q425ex962cadia.htm) | 241 indexed (printed pages and cover) | `8858f75f2d77d8b7fbdbd14191fdd9e26ea8e73a4ac4061464da8db95c39d4b7` |

The records are not copied here: ASX's terms do not allow its announcements to be republished, and the SEC exhibits
are large. `sources.json` lists them; `prepare.py` turns the downloaded files into the text that was searched. SEC
EDGAR serves scripted downloads only to a User-Agent that names a contact (its access policy); the browser save of the
page works as well.

**Text** (`prepare.py`, no model, no network): PDF pages through poppler's `pdftotext` one page at a time; the SEC
exhibits are page images with their text in a hidden layer, split at each running header ("… Date: February 2026
Page 14-3") into printed pages. One Markdown file per record: `# <record>`, then `## Page N` for each non-empty page,
wrapped lines inside a paragraph joined. 576 non-empty pages, 174,481 words. SAG-Wiki's own PDF conversion was not
used: offline, version 0.3.11 refused the PDFs ("needs the Docling document component", an optional download), and it
indexes HTML as source text with its markup.

**Collections.** *Full*: all 576 pages, the primary test. *Focused*: the 26 pages whose text names the plant
(`(?i)(molybdenum|moly)\s+plant`).

## The setups

SAG-Wiki CLI `@zleap-ai/sag` 0.3.11 from npm (the newest published on 21 Nov 2026; source tag `v0.3.11`, commit
`1583ded`). Settings are its defaults except where stated.

| Setup | Search | What judges the passages | Where it ran |
|---|---|---|---|
| Keyword | fast search over SAG-Wiki's HTTP API: SQLite FTS5 BM25 (title 2, heading 2, body 1) | nothing | CPU |
| TinyBERT | deep search (SAG2) | `cross-encoder/ms-marco-TinyBERT-L2-v2` @`81d1926f`, 4.4 M parameters, Apache-2.0 | GPU |
| MiniLM | deep | `cross-encoder/ms-marco-MiniLM-L6-v2` @`233902d2`, 22.7 M, Apache-2.0 | GPU |
| Qwen3-Reranker | deep | `Qwen/Qwen3-Reranker-0.6B` @`e61197ed`, 0.6 B, Apache-2.0; its yes/no prompt with SAG-Wiki's criterion as the instruction | GPU |
| Hindsight | deep | `hindsight-ai/hs-decide-1-flash` @`e2c78902`, 0.8 B, Apache-2.0; its own `DecisionModel.answer()` | GPU |
| d1-2B | deep, decision batches 16,000 tokens | `LiquidAI/d1-2B` @`a6bce774`, 1.9 B, LFM Open License v1.0; its own `system_one()` on its plain-PyTorch path | GPU |
| KnowLine | deep, request timeout 3,600 s, one batch at a time | `PelaAI/KnowLine-4B-Gen5` @`dba367c5`, 4 B, Apache-2.0; its own `knowline_server.py --backend hf` | GPU, speech service paused |

**Deep search** (SAG2): SAG-Wiki takes keyword candidates (on all 576 pages, a median of 112 judgements a question over both rounds, 110 to 115; first batches of 19 to 50), asks the decision service
whether each one is necessary evidence for the question, expands the search with terms from the passages it kept,
and asks again. The decision service is `decide.py`: it speaks SAG-Wiki's protocol (`POST /v1/systemone`; the
request's `state` holds the question and the evidence kept so far, each `questions` entry is one candidate with
SAG-Wiki's criterion) and answers each candidate with a probability. Rerankers see only the question and the
candidate's text. The three decision models were built for this protocol and receive SAG-Wiki's request unchanged.

**Adjustments, all through SAG-Wiki's own settings** (`run.py --sag-settings`): d1-2B ran out of GPU memory on the
default 32,000-token decision batches beside the services already on the card (about 7.5 GB of 32 GB free), so its
batches were set to 16,000 tokens. KnowLine's publisher gives about 13.6 GB of GPU memory, more than was free, so it was first tried on the CPU: the first attempt failed on SAG-Wiki's 120 s request timeout with 20 batches in parallel; the second, with two batches of 16 scoring threads, starved the cores; the third (`timeout_secs` 3,600, `retry_total_secs` 14,400, one batch at a time, `--workers 1`) judged its first 50 candidates in 66 s, but the next 50, carrying the evidence kept so far, had not finished after 15 minutes (its linear-attention layers fall back to a slow reference implementation without GPU kernels). No list was recorded. With George's go-ahead the card's speech-recognition service (a separate container) was stopped from 12:52 to 13:30 AEST, and KnowLine ran on the GPU with the same settings (one decision batch at a time, 3,600 s timeout); its process peaked at 22,106 MiB (21.6 GiB). KnowLine's server takes at most 64 questions a request and SAG-Wiki does not
read its refusal as a batch limit, so `decide.py` sends it larger batches in parts of 64 with the same state; d1-2B's
model code uses Triton kernels when Triton is installed, and this machine has no C compiler for Triton, so `decide.py`
lets it fall back to its own PyTorch code.

**Hardware.** One workstation: AMD Threadripper 7960X (24 cores), 123 GB RAM, the GPU setups on an RTX 4080 SUPER
memory-modified to 32 GB (the retail card has 16 GB; up to 32,133 MiB were in use on it during the runs), shared with a speech-recognition service and other work (about 7.5 GB free; KnowLine ran while the speech service was stopped). Python 3.12, torch 2.15.0+cu132,
transformers 5.23.0, sentence-transformers 6.3.0.

**Offline.** `offline.sh` starts every run in a new user and network namespace (`unshare -rn`) holding only loopback;
`run.py` refuses to start if it sees another interface or can reach 1.1.1.1 or 8.8.8.8, and records the interface
list (`runs.json`: `"interfaces": ["lo"]` in every run). SAG-Wiki, the decision service and the models all ran inside
it, with `HF_HUB_OFFLINE=1`. Documents, weights and packages were fetched beforehand.

## The questions and how they were scored

`questions.json` was written before any run on these questions, after reading the pages that name the plant, then
revised after a protocol review and frozen (SHA-256 `7f2ef0d76cd352c927adcd2072cd2b1c66937a653879585f8516b0cab3e59a21`).
That key, as run, is `questions-as-run.json`; `questions.json` is the same key with the corrected explanation of
`filtered-2021` (22 Nov, SHA-256 `b726696a9d010f6f8da3ce472621cb7282bd1208e5db1f423e9b22e7c94ca3e8`): the question text, the required phrases and the scores are the same.
`runs.json` names each batch's key file and its SHA-256.
Twelve questions: the brief's question, "where does the moly plant get its feed, and what had been achieved by the end
of 2021?", in three wordings (q01 names both reports, q02 uses site shorthand, q03 requires the February 2026 edition);
q04, one shift's molybdenum recovery, which these records cannot answer; seven questions on one fact each (q05–q11) and
one on two dates (q12).

Each fact lists the pages that prove it and, for each page, the phrases that must be visible. **A fact is shown at
rank r** when the excerpts ranked 1..r from one of its pages together display all of that page's phrases. Where a
question names an edition, the same sentence from the other edition counts as "right fact, wrong edition", not as the
fact. **Complete@5**: every fact the question needs is shown by rank 5; only the first 10 displayed excerpts ever
count. An excerpt is one passage as SAG-Wiki displays it (fast search: matched sentences; deep search: one source
range of a chosen chunk, so table rows can be separate excerpts). `score.py` scores, `test_score.py` tests its rules,
`score.py --check-key` confirms that every page holds its phrases and that no other page holds them all.

**By hand.** `handsheet.py` writes every distinct list (first 10 excerpts) under a random id, without the setup, in
shuffled order. Five readers (Claude subagents), one per batch of 24 to 35 lists, judged each fact's first rank by
the key's descriptions; every disagreement with the script was to be re-read and recorded in `check.json`. There were
none: 159 distinct lists in 161 readings (two KnowLine lists repeated lists already read, and got the same verdicts), 202
judgements, all equal. The author also re-read the first six passages of every q02 and
q03 list on all 576 pages for the first six setups. `check.json` holds every list's verdicts and the runs that
produced it.

**Repeats.** Every setup ran each collection twice, each time from an empty index and a new decision
process. Every repeat list was identical to the first, excerpt for excerpt.

**Protocol review.** Before launch, Codex (gpt-6.2-astra, read-only) reviewed the protocol twice; both times it held
the launch, for defects in the runner and scorer, a key phrase that could pass a cut-off list, and four questions with
other honest answers. All were fixed before any run on these questions. `protocol.md` records the plan and the changes.

<!-- tables:start (figures.py) -->
## Results

### All 576 pages: rank at which each fact is first shown (– not in the first ten; w: only the other edition, at that rank)

| Setup | q01 | q02 | q03 | q05 | q06 | q07 | q08 | q09 | q10 | q11 | q12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Keyword | –, 1 | –, 1 | –, 1 | **2** | **2** | **1** | **1** | **1** | **4** | **1** | **2, 3** |
| TinyBERT | –, 1 | 9, 1 | 3, – | **1** | **2** | **1** | **1** | **1** | **2** | **1** | **1, 2** |
| MiniLM | –, 2 | **2, 1** | 3, – | **1** | **2** | **1** | **1** | **2** | **2** | **1** | **1, 2** |
| Qwen3-Reranker | **1, 3** | **3, 1** | **3, 1** | **1** | **2** | **1** | **1** | **1** | **2** | **2** | **1, 2** |
| Hindsight | 1, – | 1, – | 2, – | **1** | **2** | **1** | **4** | **1** | **2** | **1** | **1, 2** |
| d1-2B | –, 10 | 1, – | –, – | 7 | **1** | **1** | **1** | **2** | **2** | **1** | **4, 3** |
| KnowLine | **1, 3** | 1, 7 | **2, 4** | **1** | **1** | **1** | **2** | **2** | **2** | **2** | 1, 10 |

Bold: the whole answer in the first five. Two numbers: feed route then filtered concentrate (q01–q03, here the dated re-run q13–q15), commissioning quarter then first shipment (q12).

### The 26 pages naming the plant: rank at which each fact is first shown (– not in the first ten; w: only the other edition, at that rank)

| Setup | q01 | q02 | q03 | q05 | q06 | q07 | q08 | q09 | q10 | q11 | q12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Keyword | –, 7 | –, 8 | –, 8 | **2** | **2** | **2** | **1** | **1** | **5** | **1** | **1, 3** |
| TinyBERT | –, – | 7, 2 | 3, – | **1** | **2** | **1** | **1** | **1** | **2** | **1** | **1, 2** |
| MiniLM | 2, – | **3, 1** | 2, – | **1** | **2** | **1** | **1** | **2** | **2** | **1** | **1, 2** |
| Qwen3-Reranker | **2, 4** | –, – | **3, 1** | **1** | **2** | **1** | **1** | **1** | **2** | **3** | **1, 2** |
| Hindsight | 2, – | **3, 1** | 2, – | – | – | **1** | **5** | **1** | **2** | **1** | 1, – |
| d1-2B | 2, – | 10, 8 | 2, – | **1** | – | **1** | **1** | **2** | **2** | **1** | 1, 8 |
| KnowLine | **2, 4** | **4, 2** | **2, 5** | **1** | – | **1** | **1** | **3** | **2** | **2** | **2, 1** |

Bold: the whole answer in the first five. Two numbers: feed route then filtered concentrate (q01–q03, here the dated re-run q13–q15), commissioning quarter then first shipment (q12).

### q04, one shift's recovery (no answer in these records), all 576 pages

| Setup | Excerpts returned | Of the first ten, showing a molybdenum recovery figure (none for a shift) |
|---|---|---|
| Keyword | 10 | 0 (ranks –) |
| TinyBERT | 13 | 2 (ranks 6, 8) |
| MiniLM | 13 | 2 (ranks 6, 7) |
| Qwen3-Reranker | 11 | 2 (ranks 9, 10) |
| Hindsight | 13 | 3 (ranks 2, 4, 5) |
| d1-2B | 27 | 6 (ranks 1, 2, 3, 5, 6, 8) |
| KnowLine | 77 | 0 (ranks –) |
<!-- tables:end -->

## Limits

One site's public records and twelve questions written by one person who had read the pages; a field test needs a
metallurgist's unseen questions, with the evidence they need named by a second person before the run. SAG-Wiki's
defaults except d1-2B's 16,000-token decision batches and, for KnowLine, a 3,600 s request timeout, a 14,400 s retry
allowance (default 600) and one decision batch at a time (default 20 in parallel); one version of SAG-Wiki. Public records, which the models may have seen in training. Each setup is one
model and one set of weights; the ranking of setups here is for this archive and these questions. Passages only: no
answer text was generated. The hand check was done by Claude, not by a metallurgist.

## Repeat it

You need Linux with unprivileged user namespaces, Node.js 18+, Python 3.12, poppler-utils, and a CUDA GPU (the rerankers,
Hindsight and d1-2B ran with about 7.5 GB free, d1-2B on CUDA only; KnowLine's process peaked at 21.6 GiB, after
the card's speech service was stopped).

```bash
export LOCAL=$PWD/local && mkdir -p $LOCAL/sources
# download the five records listed in sources.json into $LOCAL/sources/ (file names as in sources.json), check the SHA-256s
python3 prepare.py sources.json $LOCAL/sources $LOCAL/corpus-full
python3 prepare.py sources.json $LOCAL/sources $LOCAL/corpus-focused --only '(?i)(molybdenum|moly)\s+plant'
# the SEC pages can differ byte for byte between downloads: check the extracted text against text_sha256 (pdftotext 26.01.0)
npm install --prefix $LOCAL/sag-cli @zleap-ai/sag@0.3.11
uv venv --python 3.12 $LOCAL/.venv && VIRTUAL_ENV=$LOCAL/.venv uv pip install torch transformers sentence-transformers torchvision pillow requests
# download the six models at the revisions above into $LOCAL/hf (HF_HOME), and install hs-decide-1-flash's serving/ package
python3 score.py --check-key $LOCAL/units.json
export CUDA_VISIBLE_DEVICES=0                # your GPU's index (these runs used 2); run_all.sh falls back to 2 if unset
./run_everything.sh                          # every setup, both collections, twice
python3 score.py $LOCAL/runs check.json      # scores.json beside the runs
# the dated re-run of q01-q03 (q13-q15): its own folder, linked to the same models, software and text, its own runs/
export DATED=$LOCAL/dated && mkdir -p $DATED
for x in hf .venv sag-cli corpus-full corpus-focused; do ln -s $LOCAL/$x $DATED/$x; done
for s in keyword tinybert minilm qwen-rr hindsight d1 knowline; do for c in full focused; do for r in 1 2; do
  LOCAL=$DATED ./run_all.sh $s $c $r $PWD/questions-dated.json || echo "FAILED $s $c $r"; done; done; done
python3 score.py $DATED/runs check.json --questions questions-dated.json
```

## Files

| File | What it is |
|---|---|
| `sources.json`, `prepare.py` | The five records, the SHA-256 of each extracted text (`text_sha256`, both collections), and the text extraction |
| `questions.json`, `questions-as-run.json`, `questions-dated.json` | The twelve questions and the key (corrected; as run); q01-q03 asked again with their date (q13-q15) |
| `offline.sh`, `run.py`, `run_all.sh`, `run_everything.sh` | One offline run; every run |
| `decide.py`, `check_decide.py` | The local decision service for SAG-Wiki, and its smoke check |
| `score.py`, `test_score.py`, `handsheet.py` | Scoring, its tests, the blind hand-check sheets |
| `runs.json` | Both batches of runs (`batch`, `key`: the first, with `questions.json`; the dated re-run of q01-q03 as q13-q15, with `questions-dated.json`), every list as record, page, line range, a hash of each excerpt's text and its character start and end in `prepare.py`'s text (an excerpt can be shorter than its lines), with each run's settings and decision traffic |
| `results.json`, `check.json` | The scores per setup, collection and question; the hand check |
| `protocol.md` | The plan, the reviews and what happened during the runs |

Code: MIT. The records belong to their publishers and are not included.
