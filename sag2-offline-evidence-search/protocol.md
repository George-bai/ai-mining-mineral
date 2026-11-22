# Plan and record: SAG2 in SAG-Wiki, offline and cited, on mining records (No. 14)

Brief: `brief.md` (George, 21 Nov 2026). An introduction with worked examples, not a comparison: the comparison of
judging models is No. 15 (`../offline-search-technical-records/`), whose best judge this article uses.

## Before any search (21 Nov 2026, AEST)

- **Records:** six public records chosen for range across mining and mineral processing and for clean reuse terms
  (SEC exhibits and US government works): Newmont's Cadia technical report summary (Feb 2026), Nevada Gold Mines'
  technical report summary (May 2026), MSHA investigations MAI-2003-23 and MAI-2005-30 (Goldstrike), MSHA card BP-49,
  30 CFR 56 Subpart M (eCFR, 19 Nov 2026). `public/sources.json` holds URLs and SHA-256s. Text by `prepare.py`
  (No. 15's, with readers for the Nevada Gold Mines exhibit's page footers and the eCFR XML): 550 units, 148,827 words.
- **Questions:** eight, one per use (plant design, testwork, water, process, incident records, maintenance and
  regulation, linking two records, not in the records), written from the records' text with the pages that answer
  each (`public/examples.json`); e4 and e7 accept either of two pages; e8 has no answer in the records.
- **Search:** SAG-Wiki 0.3.11 deep search, defaults, judge Qwen3-Reranker-0.6B through `decide.py` (No. 15's winner),
  in a loopback-only namespace (`offline.sh`, `run.py`). One run.
- **Answer:** SAG-Wiki's own answer request (`answer.py`, `ANSWER_SYSTEM` unchanged), Qwen 3.8 27B on the same
  workstation through one Unix socket (`answer_offline.sh`), every returned passage sent, one answer per question.
- **Check:** every statement of every answer against the passages it cites; names of people in the MSHA reports
  withheld wherever text is shown.

## What happened

- 21 Nov, 15:48–15:49 AEST: the eight searches (`run.json`: interfaces `["lo"]`; index 0.57 s; 0.92–1.36 s a search).
- 21 Nov, 16:00–16:03 AEST: the eight answers (7.7–27.7 s each), all finished with `stop`.
- Hand check: Reader 1 (Claude, this session) found one problem: e8's owner. Reader 2 (a second Claude reader, statement by statement, without reader 1's verdicts) flagged six statements: e4's mill (its name; its objection to 'each' was withdrawn after Codex's fourth review, as the table's Number column gives 2), e6's 'only exception', 'including its pulley area' and 'only way', e8's merged recommendations and e8's closing line (the owner). Codex's page reviews added one statement, e6's 'seven feet or more from the walkway', and a further reason on e8's closing line (the citation-termination text it calls missing is in [1]); a flag on e8's 'termination notice' was raised and withdrawn. Each was checked against the passages. Seven statements stand flagged: 3 partly supported, 4 claims no source makes. `public/check.json`.
- e7: the search returned only the 2003 report's passages; round 2's 50 new candidates held no page of the 2026
  technical report's roaster circuit. The answer said its sources did not describe today's grinding.
- The comparison article was renumbered from No. 14 to No. 15 (George, 21 Nov); both go to staging together.

## No. 15 corrected (22 Nov 2026, AEST)

This article chose its judge, Qwen3-Reranker-0.6B, as the one that did best in No. 15. No. 15 has since corrected
the second half of its two-record question (the milestone it credits was reached in January 2022, not by the end of
2021), and its lead came all from that question: on No. 15's other eight answerable questions, five ways of searching
found every answer. The judge is described accordingly; the runs here are unchanged.

Update, 22 Nov 2026: No. 15 asked its two-record question again with the date and ran every setup again.
On all 576 pages, Qwen3-Reranker-0.6B was the only setup with both facts in the first five in all three wordings
(KnowLine 2, MiniLM 1, the rest none; on the 26 plant pages KnowLine 3, it 2), and its total stays 11 of 11 on all 576 pages. The choice of judge stands.
