# Local AI in mining and mineral processing: code and data

The open part of the articles at [eleticle.com](https://eleticle.com): the scripts, the results and the
data that each article reports, so the work can be checked and repeated. Each folder belongs to one
article and has its own README.

| No. | Article | Read it |
|---|---|---|
| 01 | [How to clean plant sensor data?](sensor-data-outlier-removal/) | https://eleticle.com/articles/sensor-data-outlier-removal/ |
| 02 | [Can a local LLM read a mineral processing plant flowsheet?](flowsheet-to-mermaid-local-llms/) | https://eleticle.com/articles/flowsheet-to-mermaid-local-llms/ |

## Data

| Folder | What it is |
|---|---|
| [`data/feed-rate-raw-style-v1`](data/feed-rate-raw-style-v1/) | A mill feed rate tag (belt weigher, t/h) over 4 days as irregular historian-style records, with labelled inserted faults and events. 6 traces of about 33,700 records. |

In that dataset only the hourly averages are real (anonymised, date-shifted and scaled). The records
inside each hour are generated, and every fault and event is inserted and labelled.

## Licence

Code is under the MIT licence ([LICENSE](LICENSE)). Data and results are under CC BY 4.0
([LICENSE-DATA.md](LICENSE-DATA.md)). Original lecture PDFs and source images are not included. Model-generated transcriptions of them, and
the renderings of those, are included; the licences here grant no rights in underlying third-party
material. Each article says where its sources came from.

## Where to start, how to cite, how to report a problem

Start with `sensor-data-outlier-removal/` for an example that needs only Python, or with
`flowsheet-to-mermaid-local-llms/` to look through the model outputs and the procedure behind them.
When citing this work, cite the article and give this repository's address, the commit, and the dataset
or run you used. Report errors through [GitHub Issues](https://github.com/George-bai/ai-mining-mineral/issues).
