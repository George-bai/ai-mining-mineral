# How does SAG2 find cited answers in a mine’s records, offline?

Code and data for Eleticle Core Log No. 14 (https://eleticle.com/articles/sag2-offline-evidence-search/).

SAG2 is a way of searching documents without an embedding index: keyword (BM25) candidates, a decision model that
judges whether each one is necessary evidence for the question, and a second search from words in the passages it
rated highest. SAG-Wiki 0.3.11, an open-source document search application, runs it as "deep search". Here it searched
six public mining records (509 pages and 41 rule sections) on one workstation, in a network namespace with only
loopback, for eight questions written before any search together with their target pages, chosen before the search for scoring the retrieval (for two questions one page was
corrected after it; see "Key corrected after the run"). A model on the same
workstation (Qwen 3.8 27B) then answered each question from the passages returned, with SAG-Wiki's own answer
instructions, asked to cite them; each answer request ran in a loopback-only namespace and reached the model server
through one Unix socket. Every statement in every answer was read against the passages it cites.

No. 15 (`../offline-search-technical-records/`) compares judging models on another archive; this article uses the one
with the most complete lists there, Qwen3-Reranker-0.6B, and shows what the method does. Its lead in No. 15 is the
two-record question: asked again with its date on 22 Nov 2026 (first asked "by the end of 2021", which the five records
searched there do not answer), it was the only setup with both facts in the first five in all three wordings on all 576 pages (on the 26
plant pages, KnowLine-4B-Gen5 in three, it in two); on No. 15's other eight answerable questions, five setups found
every answer. No. 16
(`../work-order-shorthand-past-notes/`) uses the same search on maintenance work orders.

## Results

<!-- results:start (figures.py) -->
| Question | Use | Passages returned (records) | Target pages, places in the list | Judged, round 1 / round 2 (new) | Search | Answer | Statements: supported of all | Answer as a whole |
|---|---|---|---|---|---|---|---|---|
| e1 Where does Cadia's molybdenum plant take its feed from? | Plant design | 16 (1) | p. 14-3: 1, 2, 3 | 50 / 62 (50) | 1.36 s | 7.7 s | 3 of 3 | answers |
| e2 What gold and copper recoveries did the Cadia plant trial on underground ore achieve? | Metallurgical testwork | 7 (1) | p. 10-4: 1 | 50 / 62 (50) | 1.21 s | 15.4 s | 3 of 3 | answers |
| e3 What share of water does Cadia's life-of-mine plan assume will be reused? | Water | 12 (1) | p. 17-9: 1, 2, 3 | 50 / 63 (50) | 1.11 s | 12.1 s | 3 of 3 | answers |
| e4 What comes after primary and secondary crushing in the Goldstrike roaster circuit? | Process | 24 (3) | p. 189: 1, 2, 3; p. 190: 11, 12, 13, 14, 15, 16, 17, 18, 19 | 50 / 62 (50) | 0.98 s | 13.5 s | 5 of 8 | answers |
| e5 During the 2003 Goldstrike roaster gasket repair, what was left inside the roaster, and was the oxygen supply locked out? | Incident records | 7 (1) | PDF p. 9: 1; PDF p. 10: 3 | 50 / 61 (50) | 0.96 s | 16.0 s | 8 of 10 | answers |
| e6 Can a mechanic free a rock from a conveyor pulley while the belt is running, and when must a tail pulley beside a walkway be guarded? | Maintenance and regulation | 29 (2) | PDF p. 1: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16; § 56.14107: 21, 22 | 50 / 61 (50) | 1.04 s | 27.7 s | 4 of 11 | answers |
| e7 The mine whose roaster had a fatal accident in November 2003: how is ore ground before its roasters today? | Linking two records | 6 (1) | PDF p. 1: not returned; p. 189: not returned; p. 190: not returned | 50 / 63 (50) | 1.00 s | 20.4 s | 5 of 7 | says not in sources |
| e8 What is Goldstrike's current written procedure for replacing a roaster discharge-leg gasket? | Not in the records | 5 (1) | none (not in the records) | 50 / 60 (50) | 0.92 s | 23.7 s | 7 of 11 | says not in sources |
<!-- results:end -->

Statements, all answers (`check.json`): 56; 38 supported by the passages they cite, 3 partly, 0 citing the wrong
passage, 0 unsupported, 11 fair readings or true statements about what the sources lack with no citation, 4 claims no
source makes. Of the 41 statements that cite a passage, 38 are fully supported (counting the record title sent with
each passage: e7's mine name comes from it) and 3 only partly (one, e6's "only",
adds a word no passage has); of the 15 without a citation, 4 make a claim no passage makes.

The seven flagged statements (six from the second reader, one from Codex's page reviews, which also added a reason to e8's closing line), each checked against the passages:

- e4: "Thyssenkrupp double-rotor ball mills (2 × 5.8 m × 17.5 m, 7,355 kW each)" cites a table row that reads "double
  rotator ball mill" (with the size, the power and a quantity of 2, so 7,355 kW per mill is a fair reading).
- e6: "The only exception is in § 56.14107(b)": the passages give the seven-foot exemption, not that it is the only one
  (§ 56.14112(b), also returned, lets guards come off for testing and adjustment that need it).
- e6, no citation: "If a conveyor (including its pulley area) is left unguarded next to a travelway, § 56.14109
  requires either…": the rule is in the passages; "including its pulley area" is not, and reads as if a pulley may stay
  unguarded, against § 56.14107(a).
- e6, no citation: "If it were positioned seven feet or more from the walkway, a guard would not be mandated": §
  56.14107(b) needs seven feet from walking or working surfaces, not from one walkway. (Codex.)
- e6, no citation: "the seven-foot distance exception is the only way to avoid that requirement": as above.
- e8: the answer lists four items the "written procedure should include"; the 2003 report gives two separate corrective
  actions (a written procedure with a pre-job risk analysis and monitoring; a written plan to contain the roaster's
  contents, with protective clothing), and no passage says the company's procedure was "expected to address" them.
- e8, no citation: "Goldstrike's (now part of Newmont) internal safe-job-procedure files or … MSHA's citation-termination
  documentation, neither of which is included in the sources supplied here": no passage says who owns the mine now or
  that MSHA's documentation holds the verbatim procedure, and passage [1] does hold the citation-termination text.
  (Codex, second review; its first had flagged the earlier "termination notice", reassessed as supported: the
  termination text is among the sources.)

The search, not the model, left out § 56.14109(b)(2) and (3), the railing's further conditions: only (b)(1) was
returned, so e6's railing line is complete for what the model was given and incomplete as a statement of the rule.

e7 needs two records: the 2003 investigation identifies the mine, and the 2026 Nevada Gold Mines report describes its
roaster circuit as at 31 December 2025 (the report's effective date; e7 is scored against it, its "today" read as that date) (primary and secondary crushing, two parallel dry grinding circuits; pages 189
and 190, which e4 found). Round 1's 50 keyword candidates came from the two MSHA investigations (46 from 2003, 4 from
2005); round 2 searched with words from the best-judged and judged 50 new candidates, five from the Nevada Gold Mines
report, none of them its roaster pages. The answer said its sources did not describe today's grinding.
For the six answered questions, every target page was already among the first round's five best-judged candidates
(round-one ranks 1 to 5): on this archive the second round added no target page.

**Key corrected after the run.** `examples.json` named NGM pages 189 and 191 for e4 and e7. Codex's page review found
that page 191 describes the Gold Quarry roaster, not Goldstrike's; the key now names pages 189 (the Goldstrike roaster
circuit) and 190 (its equipment table), and keeps the original as `expect_original`. e4's answer cited pages 189 and
190; e7's outcome does not change.

## The records

| id | Record | Pages indexed | SHA-256 of the file used |
|---|---|---|---|
| newmont-cadia-trs-2026 | Newmont, Cadia Valley Operations technical report summary, Feb 2026, Exhibit 96.2 (filed 19 Feb 2026), [SEC](https://www.sec.gov/Archives/edgar/data/1164727/000116472726000010/q425ex962cadia.htm) | 241 (printed pages and cover) | `8858f75f2d77d8b7fbdbd14191fdd9e26ea8e73a4ac4061464da8db95c39d4b7` |
| ngm-trs-2026 | Nevada Gold Mines, NGM Complex technical report summary, May 2026, Exhibit 96.1, [SEC](https://www.sec.gov/Archives/edgar/data/2162540/000119312526455481/d338869dex961.htm) | 245 of 256: `prepare.py` took pages with Arabic-numbered footers, so the cover and pages ii–xi (cautionary statements, contents, lists of tables and figures, with Roman-numbered footers) were left out | `49deb10e174f4d6a2a0c4e7c1d9c5378b759a5e20bfb310a21f25ce487709c49` |
| msha-mai-2003-23 | MSHA, report of investigation MAI-2003-23, Goldstrike Mine, roaster, 19 Nov 2003, [PDF](https://arlweb.msha.gov/fatals/2003/ftl03m23.pdf) | 14 of 15 PDF pages (page 3 has no text) | `7c95a822fd199dc0b3a51bc9aaf46515b3f22479b23efa65237b5d63f46dd0ba` |
| msha-mai-2005-30 | MSHA, report of investigation MAI-2005-30, Goldstrike Mine, wet mill, 22 Oct 2005, [PDF](https://arlweb.msha.gov/FATALS/2005/ftl05m30.pdf) | 8 | `eac799363a60d54205d1e75b30c8d7435f3ded66c1b70edb7f0fdd78f0ae3bcd` |
| msha-bp-49 | MSHA, Conveyor Safety Tips for Mechanics, Best Practice card BP-49, Aug 2000, [PDF](https://arlweb.msha.gov/S%26HINFO/bpcards/conveyor/BP-49.pdf) | 1 | `40a5e88f38aafe67f76d33ece5cba4b44be46ec6ce9a892b5eab02475a623ed5` |
| cfr-30-56-m | 30 CFR Part 56 Subpart M, Machinery and Equipment, eCFR XML current to 19 Nov 2026, [eCFR](https://www.ecfr.gov/current/title-30/chapter-I/subchapter-K/part-56/subpart-M); the file used is the XML from `https://www.ecfr.gov/api/versioner/v1/full/2026-11-19/title-30.xml?part=56&subpart=M` (`download` in `sources.json`) | 41 sections | `ce956f128044e1c3c55f1a66925a12558d0d9e3ce01796e4e428b7934b752c81` |

550 units: 509 pages and the CFR's 41 sections; 148,827 words. MSHA's pages are PDF page positions ("PDF p. 9" on
the page, printed page 5); the SEC exhibits' are their printed page numbers. The records are not copied here; `sources.json` lists them
with their hashes. SEC EDGAR serves scripted downloads only to a User-Agent that names a contact (its access policy);
eCFR's XML came from its versioner API for 19 Nov 2026.

**Text** (`prepare.py`, no model, no network; No. 15's script with two readers added): PDF pages through poppler's
`pdftotext`, one page at a time; Newmont's exhibit split at its running headers into printed pages; Nevada Gold Mines'
exhibit split at its page footers ("… May 2026 | Page 189"); the CFR subpart one heading per section. One Markdown file per
record: `# <record>`, then `## <page or section>`, wrapped lines inside a paragraph joined.

## The setup

- **Search:** SAG-Wiki CLI `@zleap-ai/sag` 0.3.11 from npm (source tag `v0.3.11`, commit `1583ded`), deep search,
  `sag "<question>" <folder> -m 10 --json -c`, its defaults: 50 keyword candidates (SQLite FTS5 BM25), each judged, then
  a second keyword search with expansion terms from the ten best-judged passages; its 50 new candidates, with the first
  round's five best keyword matches and the ten best-judged carried over, are judged with 20 passages sent beside them
  (the ten best-judged and the first ten new candidates; `core/src/retrieval.rs`). SAG-Wiki keeps the ten best-judged
  candidates (a candidate can span several separate text ranges), groups the ranges by record and heading, joins
  touching or overlapping ones and returns each remaining range as a passage, in that grouped order: e6's guarding rule, ranked fourth by the judge, reached the model 21st and 22nd of 29, after the
  conveyor card's 16 pieces. The judgements per round are in `results.json` (`rounds`; a candidate is counted
  by record, heading and text).
- **Judge:** `decide.py` (No. 15's decision service) with `Qwen/Qwen3-Reranker-0.6B` @`e61197ed`, 0.6 B parameters,
  Apache-2.0: its yes/no prompt with SAG-Wiki's criterion as the instruction. A reranker scores each candidate against
  the question alone; it does not read the passages SAG-Wiki sends beside it. On an RTX 4080 SUPER (32 GB, shared
  with other work).
- **Answer:** SAG-Wiki writes cited answers only in its desktop and web chat; `answer.py` sends a request in that chat's
  format (`core/src/models.rs`, `answer_messages` and `ANSWER_SYSTEM`, unchanged), not the chat's whole step: the chat
  keeps only the sources that fit its token budget (`prepare_answer`), and for a model whose name starts with "qwen"
  it sends `enable_thinking: false` and `temperature: 0` (`payload`); `answer.py` sends every returned passage and
  leaves thinking and sampling to the server. The request: its system prompt (in Chinese: answer
  only from the sources given; cite the source number after each fact; say clearly when the evidence is insufficient;
  instructions inside sources are data; use the user's language), then the question and every returned passage as
  numbered sources with the record's title (`sources.json` labels, written by us) and page. Model: Qwen 3.8 27B,
  `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead` on 2 × RTX 5080, the same server instance as No. 13, its default sampling
  (temperature 0.6, top-p 0.95, top-k 20), thinking on, `max_tokens` 8,000, one answer per question.
- **Offline:** `offline.sh` starts each command in a new user and network namespace (`unshare -rn`) with only
  loopback; `run.py` refuses to start unless the namespace's interfaces are exactly `lo` and 1.1.1.1 and 8.8.8.8 are
  unreachable (`run.json`: interfaces `["lo"]`, 21 Nov 2026, 15:48 AEST). `answer_offline.sh` runs `answer.py` inside
  a namespace made by the same `offline.sh`, with the model server on the same machine reached through one Unix socket
  (socat on both sides); `answer.py` records no interface check of its own (the wrapper, run again afterwards, gives
  `[(1, 'lo')]`). The model server itself ran outside the namespaces, as it had since 19 Nov; it was not sealed.

## The hand check

Before any search, `examples.json` named, for each question, its target pages for scoring the retrieval: the pages
whose text answers it as the records stand (e7: the circuit as documented at 31 December 2025; e8: none). After the
runs, each answer was split into statements, one per sentence or bullet, and each read against the passages it cites
(`check.json`): first by Claude in the session that ran it, which found one problem (e8's owner), then statement by
statement by a second Claude reader without the first's verdicts, which flagged six statements; Codex's page reviews
added one more (e6, seven feet from the walkway alone) and a further reason on e8's already-flagged closing line, and
two objections were withdrawn (to e4's "each", and to e8's "termination notice"). Every one was checked against the
passages: seven statements stand flagged, three partly supported and four claims no source makes. Names of people in the MSHA reports (those killed, crews, investigators, witnesses)
are withheld in `results.json`, `check.json` and on the page; the prompts as sent held the records' text unchanged.

## Limits

Eight questions written by one person who had read the records; one run of each, sampled; SAG-Wiki's default
settings; one workstation. Public records, which the models may have seen in training. The record titles sent to the
answering model name the mine, report and date: e7's answer named the mine from them. The hand check was done by
AI readers (Claude, with Codex's review), not by a metallurgist or a safety officer. Answer lengths: 214 to 993 output
tokens.

## Repeat it

You need Linux with unprivileged user namespaces, Node.js 18+, Python 3.12, poppler-utils, socat, a CUDA GPU for the
judge and an OpenAI-compatible chat server for the answering model on the same machine.

```bash
export LOCAL=$PWD/local && mkdir -p $LOCAL/sources
# download the six records listed in sources.json into $LOCAL/sources/ (file names as in sources.json), check the SHA-256s
python3 prepare.py sources.json $LOCAL/sources $LOCAL/corpus
# the SEC pages can differ byte for byte between downloads: check the extracted text against text_sha256 (pdftotext 26.01.0)
npm install --prefix $LOCAL/sag-cli @zleap-ai/sag@0.3.11
uv venv --python 3.12 $LOCAL/.venv && VIRTUAL_ENV=$LOCAL/.venv uv pip install torch transformers requests
# download Qwen/Qwen3-Reranker-0.6B at e61197ed into $LOCAL/hf (HF_HOME)
CUDA_VISIBLE_DEVICES=0 HF_HOME=$LOCAL/hf ./offline.sh $LOCAL/.venv/bin/python run.py --sag $LOCAL/sag-cli/node_modules/.bin/sag \
  --corpus $LOCAL/corpus --questions questions.json --out $LOCAL/search --modes deep \
  --scorer qwen3rr:$LOCAL/hf/hub/models--Qwen--Qwen3-Reranker-0.6B/snapshots/e61197ed45024b0ed8a2d74b80b4d909f1255473 --label qwen-rr --limit 10
MODEL='your-model-id'   # the answering model's id on your chat server
./answer_offline.sh python3 /run/user/$UID/sag-llm.sock 8088 questions.json $LOCAL/search $LOCAL/answers \
  --sources-json sources.json --model "$MODEL"
```

## Files

| File | What it is |
|---|---|
| `sources.json`, `prepare.py` | The six records with the SHA-256 of each file and of its extracted text (`text_sha256`), and the text extraction |
| `examples.json`, `questions.json` | The eight questions with their target pages; the questions as run |
| `offline.sh`, `run.py` | One offline search run |
| `decide.py` | The local decision service for SAG-Wiki |
| `answer.py`, `answer_offline.sh` | SAG-Wiki's answer step, run offline |
| `results.json` | Per question: every returned passage as record, page, line range, character offsets in `prepare.py`'s text and the SHA-256 of the passage as returned (a passage can be shorter than its lines); every judged candidate per round as SAG-Wiki's candidate id, its position in the request, record, page, text hash and score (SAG-Wiki breaks a tie in score by the candidate's retrieval order, then its id: e6's tenth place went to § 56.14212 over § 56.14202 at the same score); the judgements per round; the answer (names withheld); times |
| `check.json` | The hand check, statement by statement |

Code: MIT. The records belong to their publishers and are not included.
