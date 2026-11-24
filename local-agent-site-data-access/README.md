# How should a local agent get access to your site's historian?

Material for the article at https://eleticle.com/articles/local-agent-site-data-access/ (No. 17), the first of five
on a small local agent working on a site's own data. No experiment here: a review of what has been published, a
comparison of five ways to give an agent access, and the layout we recommend, which No. 18 builds.

## How it was done

Four research questions, each run once by Codex (gpt-6.2-astra, highest reasoning effort, web search, read-only) on
23 Nov 2026, primary sources preferred and publication dates checked. The prompts and the answers, with every
source, are in `research/`:

| File | Question |
|---|---|
| `q1-publications.md` | Published work, 2023 to 2026, on language-model agents reading industrial historian or time-series data: what access each had and what it measured |
| `q2-vendors.md` | What the historian vendors and industrial data platforms offer agents, and whether data stays on site |
| `q3-security.md` | Guidance on safe agent access to operational data: zones, read-only accounts, MCP and prompt injection, audit |
| `q4-findability.md` | How large tag lists are made findable: asset models, naming standards, search, and published evaluations |

A fifth Codex run checked each number and claim the page takes from a source against that source
(`research/verify.md`, with its prompt).

## The page's data

- `studies.json`: nine published studies in which an agent read plant or equipment records, each marked on four
  points as the publication reports them (local model, i.e. run on the user's own hardware rather than a cloud service; real records; read-only access; answers scored), with its
  own main result. Our reading; "unknown" means not reported or not verifiable, not "no".
- `options.json`: five ways to give a local agent historian data, each judged on four questions (can it change plant
  data, do readings leave the site, can it overload the historian, does it find the right tag), with the reason.

## Limits

What the searches turned up by 23 November 2026; vendor documents describe capability, not use; each study's number
is on its own questions and does not compare with another's.

## Licence

Text and data in this folder: CC BY 4.0. The research answers quote and link their sources, which keep their own
terms.
