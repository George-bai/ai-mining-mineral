# How should you clean plant sensor data?

Code and figures for the article at https://eleticle.com/articles/sensor-data-outlier-removal/.

One mill feed rate tag, cleaned several ways, to show that the right cleaning depends on what data you
were given (raw records or averages) and what it is for. In the main example, five bad readings in 4,571
hide a whole shift of feed rate on the raw trend, and one of them moves an hourly average by 137 t/h
while leaving it inside the instrument span.

**What is real and what is not.** The hourly averages are real: 96 consecutive hours from a working
plant, anonymised and scaled, and published with the right to do so. The records inside each hour are generated, and every fault and event is
inserted at a known position. The dataset and its full description are in
[`../data/feed-rate-raw-style-v1`](../data/feed-rate-raw-style-v1/README.md).

## What is here

| File | What it is |
|---|---|
| `demo.py` | Cleans the tag each way and reports what each rule does. Writes `results.json` and `cleaned-base.csv` |
| `figures.py` | Draws the article's four figures as SVG, each in a wide and a narrow layout |
| `page_data.py` | Builds the data the article page's live panels draw |
| `figures/` | The four figures as drawn for the article |

## Run it

Python 3, standard library only.

```bash
cd sensor-data-outlier-removal        # from the top of the repository
python3 demo.py ../data/feed-rate-raw-style-v1 out
python3 figures.py ../data/feed-rate-raw-style-v1 out/figures
```

## Limits

This shows how each rule behaves on this dataset, not how real plants behave. Only the hourly averages
are real; spike sizes and fault durations are example values. See the dataset's README before reusing it.

Two rules in `demo.py` hold for this dataset only (each is described in its docstring):

- A small negative on a running belt is set to zero. A running belt does not show an empty belt: on a real
  tag, use separate evidence of no load, such as a belt-loaded signal or the feeder stopped.
- Only a gap left by removed records counts as missing. A gap with no records at all is interpolated,
  however long, because historian silence is trusted as compression. On a real tag, mark outages from the
  historian's quality flags or an outage log.

## Licence

Code: MIT. Data: CC BY 4.0.
