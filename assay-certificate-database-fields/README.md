# Can a local model put the right assay into the right database field?

A certificate of analysis for a certified reference material (CRM) gives each element by several methods. OREAS 902
prints copper as 0.301 wt.% by four-acid digestion, 0.308 wt.% by aqua regia and 0.111 wt.% soluble in 5 %
sulphuric acid. A site's QAQC database keeps one expected value and one standard deviation (SD) per lab method, so each field takes one of
these numbers or none. A reader can copy every digit correctly and still file the wrong one.

Here three readers fill the same twelve database fields from seven public certificates, and a hand-built key says
what each field should hold. The article is at https://eleticle.com/articles/assay-certificate-database-fields/.

**A first test, not a benchmark:** seven certificates, one local model, three attempts per certificate and
instruction, one run of the rules.

## Result

Right fields out of 84 per attempt (7 certificates × 12 fields, 38 of which should stay empty):

| Reader | Attempt 1 | Attempt 2 | Attempt 3 | Left empty that should be filled | Wrong number filed |
|---|---|---|---|---|---|
| Model, fields defined (`prompt.md`) | 83 | 83 | 83 | 0 | 1 each attempt |
| Model, column names only (`prompt-columns.md`) | 70 | 68 | 70 | 0 | 14, 16, 14 |
| PDF text + rules (`rules.py`), one run | 55 | | | 20 | 9 |

No reader misread a number. Every one of the 56 wrong entries starts from a number printed on the certificate (as
printed, converted or halved), put in the wrong field, in the wrong unit, as the wrong statistic, or filed as certified
when the certificate calls it indicative or uncertified.

**Model, fields defined.** The same miss in all three attempts: on Rocklabs SE147 it halved the expanded uncertainty
(U = ±0.01 ppm, k = 2, page 1) and filed 0.005 ppm as the 1SD, three times too tight. The certificate prints the standard deviation of the
26 accepted laboratory sets, 0.015 ppm, on page 4, and says on page 5 that the expanded uncertainty must not be used to
set laboratory control limits. The model also caught a conflict inside OREAS 501d (its front-page summary gives aqua
regia gold as 0.230 ppm with the two gold SDs swapped; Tables 1 and 4 give 0.232) and took Table 1 in every attempt.

**Model, column names only.** In every attempt: AMIS0832's three copper SDs as 2s, not halved, and its uncertified
aqua regia gold (0.02 g/t) filed; CDN-CM-54's three ±2SD values filed as 1SD; OREAS 232b's copper in ppm (26.7) put
in the wt.% fields; OREAS 902's indicative fire assay gold (46.6 ppb) filed, as 0.0466 ppm twice and unconverted as
46.6 ppm once; SE147's U halved (twice) or used whole (once). In one attempt AMIS0832's acid-soluble copper (method
AS, 1.57 %) went into the cyanide-soluble field.

**Rules.** Written from OREAS 902's layout, they fill it exactly. Other OREAS certificates head the section
"4-Acid Digestion" instead of "4 Acid Digestion": on OREAS 905 four-acid copper is left empty, on OREAS 501d it lands in
the aqua regia field and on OREAS 232b in the cyanide-soluble field (the last header the rules recognised was the
gold's "Cyanide Leach"). On 501d and 232b the rules read the table of 95 % limits, whose second column is the lower
limit (of a confidence interval on 501d, of an expanded uncertainty on 232b), so seven SDs are lower limits. AMIS0832, CDN-CM-54 and SE147 lay out their tables differently, and
the rules find nothing in them.

**What a wrong SD does.** For a lab whose results scatter normally by the certificate's 1SD around a bias, with a
result failing outside ±3SD of the database's numbers (an illustration under that assumption: SE147's 0.015, for one,
is the spread of 26 laboratories' averages, not one laboratory's own scatter):

| Standard | Right 1SD | Filed 1SD (by) | Sound lab fails, right / filed | Lab 10 % high fails, right / filed |
|---|---|---|---|---|
| SE147, Au fire assay | 0.015 ppm | 0.005 (model, fields defined) | 0.3 % / 32 % | 88 % / 100 % |
| CDN-CM-54, Cu four-acid | 0.0075 % | 0.015 (model, names only) | 0.3 % / 0.0 % | 96 % / 11 % |
| OREAS 232b, Au fire assay | 0.037 ppm | 0.933 (rules) | 0.3 % / 0.0 % | 33 % / 0 % |

`control_chart.py` computes these from each certificate's own numbers (`python3 control_chart.py` prints the table); nothing is simulated.

## What is here

| File | What it is |
|---|---|
| `fields.json` | The twelve fields, each defined by analyte, method, unit and statistic, and the four filing rules |
| `prompt.md` | The instruction with every field defined and the rules ("fields defined") |
| `prompt-columns.md` | The instruction with the column names only ("names only") |
| `rules.py` | Ordinary PDF extraction: `pdftotext -layout` and rules written from OREAS 902, frozen before the other certificates were downloaded |
| `ask_model.py` | Sends a certificate's text and one instruction to an OpenAI-compatible endpoint; saves the fields, the reply, the reasoning, the time and the token counts |
| `certificates.tsv` | The seven certificates and where each was downloaded |
| `key.json` | The answer key: the right entry for every field, alternatives accepted where a certificate gives two defensible SDs, and where each value is printed |
| `score.py` | Scores every answer field by field: right, left empty, wrong number filed (a number the certificate prints), or misread (one it does not) |
| `check.json` | Hand corrections to the script's verdicts (none were needed; see its note) |
| `run.sh` | Runs the rules and the model on every certificate, then scores |
| `control_chart.py` | The share of a lab's results outside ±3SD for a given filed value and 1SD, by lab bias: the article's third figure |
| `results/run1/` | Every answer: `rules/`, `qwen38-27b/` (fields defined) and `qwen38-27b-columns/` (names only), `<certificate>.<attempt>.json`, and `scores.json` |

## Run it yourself

You need Python 3 (standard library only), `pdftotext` (poppler-utils) and an OpenAI-compatible endpoint serving a
model. Run from this folder:

```bash
# 1. Download the certificates (each producer's terms apply; keep them out of any public repository)
while read -r id url; do mkdir -p certs/$id && curl -sSL -o certs/$id/cert.pdf "$url"; done < certificates.tsv

# 2. Fields defined, then column names only; ENDPOINT and MODEL name your server
ENDPOINT=http://localhost:8000/v1 MODEL=my-model ./run.sh certs runs/mine 3
ENDPOINT=http://localhost:8000/v1 MODEL=my-model PROMPT=prompt-columns.md ./run.sh certs runs/mine 3
```

`run.sh` ends by writing `runs/mine/scores.json` and printing every entry not marked right. Producers revise their
certificates: a later revision can change a value, a page or a layout, so check the key against the version you
download.

## How it was run

| | |
|---|---|
| Model | Qwen 3.8 27B, `RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead`, revision `009632fef96dd349150baa780c984e62e70e91fe` (4-bit NVFP4 weights) |
| Serving | vLLM 0.27.1 across 2 × RTX 5080 (16 GB each) on one workstation: context 165,000 tokens, KV cache in FP8, at most 2 sequences at a time, shared with another client during the runs |
| Sampling | The server's defaults, nothing set by the request: temperature 0.6, top-p 0.95, top-k 20; thinking on at medium effort; at most 32,768 output tokens |
| Input | The whole certificate's text from `pdftotext -layout` (poppler) in one user message, after the instruction; no images, no tools |
| Attempts | Three per certificate and instruction, one at a time; 15 to 90 seconds each |
| Date | 20 November 2026, certificates downloaded the same day |

## How it was scored

The key was built by hand from each certificate before any model answer was read, except OREAS 902, whose first
model answer came first (its key follows its Table 1 line by line). For AMIS0832 either half of 2s or the stated
standard uncertainty counts as the 1SD (2s = 2 uc on that certificate). For SE147 the key's 1SD is the standard
deviation of the 26 accepted laboratory sets (page 4): the field asks for a 1SD and this is the one the certificate
prints. The certificate also encourages laboratories to set their own limits as their results build up; that refines
the record later and is no reason to leave it empty now. The rules left SE147's SD empty with its value, as part of
finding nothing on that certificate; counting an empty SD as right would make them 56 right and 19 empty.

`score.py` compares every field with the key (to a relative tolerance of 10⁻⁶) and checks whether a wrong number is
printed on the certificate in any unit (×10⁻⁷ to ×10⁷, or ×½ and ×2). Every entry it did not mark right was then
read beside the certificate; all its verdicts stood.

## Limits

- Seven certificates from four producers, all with a text layer. A scanned certificate needs reading from the
  image, which this test does not cover.
- One model, three attempts per condition. The 27B gave the same answer in every attempt on most fields; a different
  model, a quantisation or a newer revision can file differently.
- Twelve fields for copper and gold only. A real standards table holds more analytes and more methods (fusion, XRF,
  combustion, PhotonAssay, cyanide leach for gold), each another chance to file the wrong number.
- The rules were deliberately written once from one certificate, as a site might write them for its usual supplier.
  Rules written for each layout would do better on those layouts.
- The control-chart numbers assume a lab whose scatter equals the certificate's 1SD and a ±3SD rule; a site's own
  limits and rules differ.

## Sources

The certificates are not included: they belong to their producers. `certificates.tsv` links each one.

- OREAS 902, 905, 501d and 232b: Ore Research & Exploration Pty Ltd, https://www.oreas.com
- AMIS0832: African Mineral Standards, https://amis.co.za
- CDN-CM-54: CDN Resource Laboratories Ltd, https://cdnlabs.com
- SE147: Rocklabs, Scott Technology Ltd, https://scottautomation.com
- The database case quoted on the page: AMC Consultants (UK) Limited, *S-K 1300 Technical Report Summary: KCM
  Integrated Operations (Initial Assessment)*, 12 May 2026, section 8.5.1.1 and Table 8.1,
  https://www.sec.gov/Archives/edgar/data/2093018/000157587226000304/filename2.htm

## Licence

Code: MIT. Results (`results/`, `key.json`, `check.json`): CC BY 4.0, for what is ours in them. The values in the key
and in the answers are facts taken from the producers' certificates; this licence grants nothing over the
certificates themselves.
