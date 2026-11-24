# How can a local agent find the right tag among 50,000?

Code for the article at https://eleticle.com/articles/historian-tag-catalogue-for-agents/ (No. 18).

A mock historian with a mineral-processing asset tree, a read-only connector, a crawler that builds a searchable
tag catalogue, and an MCP server a local agent uses to find the tags a question needs and read only those. The
agent never loads the tag list: it searches the catalogue, gets a short ranked list with the reason each tag
matched, and then reads data for the few it chose.

**What is real and what is not.** The company, its 31 sites and 155 concentrators, the naming conventions and the
injected faults are generated. The flotation tags follow real hourly averages from a gold flotation plant (Zyfra's
data, not included here), and so do the crushing belts and the mill feed; the mill powers,
cyclone densities, leach and tailings tags follow real hourly averages from a second plant (anonymised); the values inside each hour are generated around them, so each hour
averages to the real value. The other tags are generated, moving with the real feed rate. Without the backbone
files (`make_backbones.py`), every tag is generated. The mock is ours,
written to the request and response shapes of the PI Web API; it is not the vendor's and is not linked to it.

## Parts

| File | What it does |
|---|---|
| `config/plant.yaml` | The plant: equipment templates, areas, four naming conventions, unit habits, injected faults |
| `generator.py` | Builds the asset tree and the PI points from it, deterministically |
| `values.py` | Tag values on demand: 5-second scans, the historian's exception test, analyser holds, run states |
| `mock_api.py` | The mock web API: read-only, Basic or token auth, paging, `selectedFields`, streams, streamsets, GET-only batch, fault injection |
| `connector.py` | The only code that talks to the historian: GET only, retries, URL-sized chunks, a concurrency limit |
| `crawler.py` | Reads the asset tree, points and last values; writes the catalogue; swaps it in atomically; reports the diff |
| `config/enrichment.yaml` | The site's vocabulary: aliases, abbreviations, instrument codes, units, synonyms, golden tags |
| `catalog.py` | The SQLite catalogue (FTS5), the ranked search with reasons, and a plain keyword baseline |
| `mcp_server.py` | The agent's tools: `catalog_status`, `find_assets`, `browse_asset`, `search_tags`, `get_golden_tags`, `get_tag_details`, `get_current_values`, `get_timeseries`; dataset files; guardrails; audit log |
| `skill/historian-tags/SKILL.md` | The method the agent follows with those tools |
| `tests/test_system.py` | Mock contract, read-only guard, retries, crawl counts against the generator, search |

## The search test

`eval/round1/` is a development round: its questions were seeded by our own prompt (an example in it used the
abbreviation the search did not yet read), so the search rules were fixed after it, each with a unit test, and a new
set of questions was written for `eval/round2/` by a writer given only a description of the plant. Round 2 is the
result; both rounds' questions, keys, key checks and scores are here. It was scored on a catalogue built with both
backbone files; a reader with only the Zyfra file gets generated values for the second plant's tags, so a few health
flags (stale or no data from real blanks) differ, and a rescore can differ slightly. `eval/diagnostics.py` holds the
checks run after scoring (the baseline given the same place filter; the stop-list letters). Run `uv run python eval/score.py
<catalogue> eval/round2` to score a catalogue.

Other numbers on the page: `eval/crawl-report.json` is the crawl that built the scored catalogue (counts, health,
requests, seconds); `eval/tokens.py` counts the tokens of the whole tag list and of three search answers with the 27B
model's own tokenizer (its server's tokenize call, no generation) into `eval/tokens.json`. The figures are drawn from
these files by the article's page script.

## Changed after round 2

- **Energy counters** (23 Nov 2026, evening): each meter's energy tag now integrates that meter's active power hour by
  hour (sampled every 15 minutes) instead of counting at a fixed rate. Search and the scored catalogue are not
  affected (search does not rank on values); No. 19's question about the most energy used needed it. Tests: 12 pass.
- **`get_timeseries` statistics** (24 Nov 2026, after two external reviews): the per-tag mean, minimum and maximum it
  returns had been taken over every summary column requested together (Average with Minimum, Maximum, Total, StdDev
  or Count), Count and Total were converted with the tag's unit, and bad-quality values were kept. Now each column has
  its own statistics and unit (the first summary requested leads, the rest under `other_summaries`; `column_units` in
  the provenance: a Count is a number of samples, a Total is the unit times days), Count is never converted, a
  conversion the units do not allow is refused with a note, and bad-quality values are left out and counted in
  `notes`. Nos. 19 to 21 ran on the earlier version; seven of No. 19's 72 answers quoted a mean from it that was 1 to
  24 % off (its README lists them). The dataset files kept each summary column apart. Test: `tests/test_timeseries.py`.
- **Limits before the request** (24 Nov 2026, after an external review): `get_timeseries` used to send a read and count
  what came back, and `recorded_days` was not applied, so a ten-year read at one second reached the historian before
  it was refused. The window is now checked first (`check_window`): too many intervals a tag, more than seven days of
  raw records, an end before the start, or a time or interval it cannot read are refused with nothing sent. Replayed
  on the 163 distinct windows the agents of Nos. 19 to 21 asked for: the 17 it refuses failed then too, after the
  request (16 over the interval limit, one with the interval written "15min"). A raw read that returns the most
  records a call gives now says the window may be cut short.
- **The clock** (24 Nov 2026, same review): the crawler took the newest sample it was given as "now", so if every
  tag had stopped a week ago, every tag looked fresh. Staleness is now measured on the server's own clock, read from
  its responses (the stand-in sends its fixed clock as `X-Historian-Time`; any server sends `Date`), and the crawl
  report keeps the newest sample apart (`newest_sample`). `historian_earliest` is the oldest record of one healthy
  tag, taken as where the archive starts. On the stand-in the two clocks agree, and a full re-crawl on 24 Nov 2026
  gave the same health counts as before.
- **Calls per minute** (24 Nov 2026): the server now refuses more than 60 tool calls a minute, all tools together
  (`config/settings.yaml`). The limits per call bound one read; this bounds how many. The runs of Nos. 19 to 21 were
  made before it.

## Data

- **Zyfra gold flotation data** (hourly, 15 Jan 2016 to 18 Aug 2018, 22,716 rows), not
  included. To repeat the work, fetch `datasets/gold_recovery_full.csv` from
  https://github.com/5hraddha/zyfra-gold-recovery-prediction at commit `629470d8d6a1b151295f14b784964b442f79fd42`
  (SHA-256 `d477aa4dadf6413561c78fddf368ce60c5891559db53cefed3526790db151aa2`), then
  `uv run python make_backbones.py --zyfra gold_recovery_full.csv`.
- **The second plant's hourly averages** are private and not included; without them those tags are generated. The
  method is open: `config/backbones.yaml` names the columns used, and `make_backbones.py` and `values.py` show how
  the values are built.

## Run it

Python 3.11 or later and [uv](https://docs.astral.sh/uv/). CPU only.

```bash
uv sync
MOCK_SITES=31 MOCK_CONCENTRATORS=5 uv run uvicorn mock_api:app --port 8711   # about 50,000 tags
uv run python crawler.py run                                               # builds local/catalog/catalog.sqlite
uv run python mcp_server.py                                                # the MCP server, over stdio
uv run pytest -q tests
```

The first crawl after the stand-in starts is slow: 48 minutes on our workstation (24 Nov 2026). Since 23 Nov 2026 each
energy counter integrates its meter's power, and the stand-in works every counter out the first time it is read.
A crawl after that takes 14 seconds (13.8 s on 24 Nov; the article's 14.5 s is `eval/crawl-report.json`, timed on
23 Nov). Both give the same 3,560 requests and the same health counts: 2,602 tags flagged of 50,594.

To connect an agent, register the server as a stdio MCP server running `uv run python mcp_server.py` in this
folder (for example `pi mcp add historian -- uv run python mcp_server.py`). For a shared server, run
`MCP_API_KEY=... uv run python mcp_server.py --http` and send the key as `X-API-Key`.

## Against a real historian

This is a stand-in shaped like the PI web API, not a tested vendor integration. To point it at a real server: give the
crawler the server's address, account and asset database (`--base-url`, `--auth`, `--user`, `--password`, `--database`;
it reads the first data server it is given), set `historian_url` and `historian_auth` in `config/settings.yaml` for the
tools (a read-only service account over HTTPS; Kerberos would be added in `connector.py`), fill
`config/enrichment.yaml` with the site's own naming conventions, and test all of it against that server before anyone
relies on it.

| Built here | Not built: a site adds and tests these (No. 17 recommends them) |
|---|---|
| A connector that only reads | Rights per user: the HTTP server has one shared key |
| Limits per call, checked before the historian is asked: tags, intervals a tag, days of raw records | The user's name, and allowed or refused, in the log |
| A cap on tool calls per minute | Network isolation and a one-way copy to read from |
| A log of every call: tool, arguments, items returned, time taken | A budget on the historian's own side |
| Staleness measured on the server's clock, not on the newest sample | Kerberos |

## Licence

Code: MIT. Data and results: CC BY 4.0.
