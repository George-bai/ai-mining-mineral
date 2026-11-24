# Local AI in mining and mineral processing: code and data

The open part of the articles at [eleticle.com](https://eleticle.com): the scripts, the results and the
data that each article reports, so the work can be checked and repeated. Each folder belongs to one
article and has its own README.

| No. | Article | Read it |
|---|---|---|
| 05 | [How should you clean plant sensor data?](sensor-data-outlier-removal/) | https://eleticle.com/articles/sensor-data-outlier-removal/ |
| 06 | [Can a local LLM read a mineral processing plant flowsheet?](flowsheet-to-mermaid-local-llms/) | https://eleticle.com/articles/flowsheet-to-mermaid-local-llms/ |
| 07 | [What hardware does a mineral-processing site need to self-host LLMs and expert models?](self-hosted-ai-hardware/) | https://eleticle.com/articles/self-hosted-ai-hardware/ |
| 08 | [Does a written skill help a local LLM read a whole plant flowsheet?](flowsheet-reading-skill/) | https://eleticle.com/articles/flowsheet-reading-skill/ |
| 09 | [A model predicts grinding throughput with R² = 0.962. What did it actually learn?](grinding-throughput-model-r2/) | https://eleticle.com/articles/grinding-throughput-model-r2/ |
| 10 | [What does a local LLM know about minerals?](local-llm-mineral-knowledge/) | https://eleticle.com/articles/local-llm-mineral-knowledge/ |
| 11 | [Can a local model put the right assay into the right database field?](assay-certificate-database-fields/) | https://eleticle.com/articles/assay-certificate-database-fields/ |
| 12 | [Can a local AI assistant tell which size fraction carries the most copper?](copper-size-fraction-local-assistant/) | https://eleticle.com/articles/copper-size-fraction-local-assistant/ |
| 13 | [Does a site glossary help a local LLM read maintenance work orders?](work-order-shorthand-glossary/) | https://eleticle.com/articles/work-order-shorthand-glossary/ |
| 14 | [How does SAG2 find cited answers in a mine’s records, offline?](sag2-offline-evidence-search/) | https://eleticle.com/articles/sag2-offline-evidence-search/ |
| 15 | [Which local model finds the whole answer in a mine’s reports?](offline-search-technical-records/) | https://eleticle.com/articles/offline-search-technical-records/ |
| 16 | [Does searching a site’s own work orders help a local LLM as much as a glossary?](work-order-shorthand-past-notes/) | https://eleticle.com/articles/work-order-shorthand-past-notes/ |
| 17 | [How should a local agent get access to your site’s historian?](local-agent-site-data-access/) | https://eleticle.com/articles/local-agent-site-data-access/ |
| 18 | [How can a local agent find the right tag among 50,000?](historian-tag-catalogue-for-agents/) | https://eleticle.com/articles/historian-tag-catalogue-for-agents/ |
| 19 | [Can a local 27B model find the right historian tags from a plain question?](local-agent-finds-historian-tags/) | https://eleticle.com/articles/local-agent-finds-historian-tags/ |
| 20 | [Can a local agent see that collector dose relates to recovery differently at each feed grade?](local-agent-reagent-recovery-analysis/) | https://eleticle.com/articles/local-agent-reagent-recovery-analysis/ |
| 21 | [What does a small local model need to analyse your site’s data well?](teaching-local-agent-site-analysis/) | https://eleticle.com/articles/teaching-local-agent-site-analysis/ |

## Data

| Folder | What it is |
|---|---|
| [`data/feed-rate-raw-style-v1`](data/feed-rate-raw-style-v1/) | A mill feed rate tag (belt weigher, t/h) over 4 days as irregular historian-style records, with labelled inserted faults and events. 6 traces of about 33,700 records. |
| [`data/maintnorm-v1`](data/maintnorm-v1/) | 12,000 real maintenance work order texts from three Australian mining companies (4,000 each, mostly heavy mobile equipment), every token paired with its normalised form; asset numbers, numbers, dates and names masked. |

In `data/feed-rate-raw-style-v1` only the hourly averages are real (anonymised, date-shifted and scaled). The
records inside each hour are generated, and every fault and event is inserted and labelled. `data/maintnorm-v1`
holds no records: its README names the upstream repository and commit, the hashes of the files used and the
command that fetches them.

## Licence

Code is under the MIT licence ([LICENSE](LICENSE)). Data and results are under CC BY 4.0
([LICENSE-DATA.md](LICENSE-DATA.md)), except third-party material, which keeps its own licence: the work-order
notes and glossaries derived from MaintNorm are under MIT, © 2024 NLP-TLP Group. Original lecture PDFs and source images are not included. Model-generated transcriptions of them, and
the renderings of those, are included; the licences here grant no rights in underlying third-party
material. Each article says where its sources came from.

## Where to start, how to cite, how to report a problem

Start with `sensor-data-outlier-removal/` for an example that needs only Python, or with
`flowsheet-to-mermaid-local-llms/` to look through the model outputs and the procedure behind them.
When citing this work, cite the article and give this repository's address, the commit, and the dataset
or run you used. Report errors through [GitHub Issues](https://github.com/George-bai/ai-mining-mineral/issues).
