# A model predicts grinding throughput with R² = 0.962. What did it actually learn?

Code for the article at https://eleticle.com/articles/grinding-throughput-model-r2/.

A public Kaggle dataset, [Grinding Throughput in Mining Operations](https://www.kaggle.com/datasets/shaikrafisksk/grinding-throughput-in-mining-operations),
holds 5,000 rows: 14 ore and operating variables and a grinding throughput in t/h. An ordinary least-squares
regression on the 14 inputs predicts throughput with R² = 0.962. Yet every one of the file's 75,000 values,
throughput included, is reproduced exactly from NumPy's random-number generator seeded with 42: `recreate.py`
writes a file identical to the download, byte for byte. The regression learned the formula that made the file,
not a mill.

## What is here

| File | What it is |
|---|---|
| `recreate.py` | Rebuilds the whole file from seed 42, compares it with the download value by value, fits the regression and prints every number the article uses |

## Run it

Python 3, standard library only: NumPy's legacy generator (MT19937 seeded with an integer, 53-bit doubles,
polar-method normal draws) is written out in the script, so no NumPy is needed.

```bash
python3 recreate.py                                    # rebuild, fit, print
python3 recreate.py --csv Mining_Grinding_Throughput.csv   # also compare with the file downloaded from Kaggle
python3 recreate.py --write rebuilt.csv                # also write the rebuilt file
```

Its output, with the downloaded file (458,484 bytes, downloaded 9 Nov 2026, SHA-256
`300af0dbb609a193b5dfb025a4c73834745c93c191f7e0bd0a1532c00ededc5b`):

```text
inputs:     70,000 of 70,000 values match
throughput: 5,000 of 5,000 values match
R² on all rows 0.9619; five held-out folds 0.9584 to 0.9646, mean 0.9616
R² with the sine of feed size added 0.9781
shares of throughput variance: straight 96.10%, sine 1.68%, noise 2.19%
rows with throughput above feed rate: 1,732 of 5,000
largest correlation between two inputs: 0.030 (Grinding_Media_kg, Temperature_C)
stretch: 1.06995 t/h per recipe unit; sine ±5.35 t/h; noise sd 4.28 t/h
```

`sha256sum rebuilt.csv` gives the download's own hash: the rebuilt file is the same file.

## The recipe

1. `np.random.seed(42)` (the legacy generator).
2. For each input in file order, 5,000 draws of `np.random.uniform(lo, hi)`:

   | Input | Limits | | Input | Limits |
   |---|---|---|---|---|
   | Ore hardness, MPa | 80 to 180 | | Power consumption, kW | 650 to 1,300 |
   | Feed size, mm | 10 to 35 | | Grinding media, kg | 3,000 to 6,000 |
   | Ore density, t/m³ | 2.3 to 3.8 | | Temperature, °C | 30 to 50 |
   | Mill speed, rpm | 12 to 18 | | Vibration, mm/s | 2 to 6 |
   | Mill load, % | 60 to 90 | | Moisture, % | 2 to 7 |
   | Water flow, m³/h | 140 to 270 | | Mineral grade, % | 1.5 to 5 |
   | Feed rate, t/h | 180 to 380 | | Operating hours, h | 10 to 30 |

3. Noise: 5,000 draws of `np.random.normal(0, 4)`, continuing the same stream.
4. `s = −0.18·hardness + 25·density + 7.5·speed + 0.45·load + 0.08·water + 0.32·feed rate + 0.015·power
   + 0.004·media − 2·vibration − 1.5·moisture + 6·grade + 5·sin(feed size) + noise`, with the inputs unrounded
   and feed size in millimetres read as radians. Temperature and operating hours carry no weight.
5. Throughput = 170 + 180 · (s − min s) / (max s − min s): the lowest row is exactly 170.00 t/h, the highest
   exactly 350.00. In t/h every weight above is multiplied by 1.06995.
6. Every column rounded with `np.round(x, 3)` and then `np.round(x, 2)`.

## How it was found

- Every input has the kurtosis of a uniform distribution (−1.2) and lies between two round limits.
- Seed 42 with `np.random.uniform` matched about 95 % of the values in place; the rest sat within 0.0005 of a
  rounding half-point, and rounding to 3 places before 2 matched all 70,000.
- The regression's residuals correlated 0.76 with the next 5,000 normal draws of the same stream, and their
  mean by feed-size decile swung up and down: a sine of feed size. A regression on the 14 inputs, sin(feed size),
  cos(feed size) and those draws left residuals of standard deviation 0.0029 t/h, the size of rounding to
  2 places. Its weights divided by 1.06995 are the round numbers above, and the exact 170 and 350 at the
  ends of the throughput column point to the stretch.

This formula reproduces every value. It is one exact way to make the file; whether its author wrote it in
this form cannot be known.

## What the regression learned

The change in throughput across each input's range, in t/h, from the formula and from the regression:

| Input | Formula | Learned | | Input | Formula | Learned |
|---|---|---|---|---|---|---|
| Feed rate | 68.48 | 68.65 | | Power consumption | 10.43 | 10.49 |
| Mill speed | 48.15 | 47.74 | | Vibration | −8.56 | −8.38 |
| Ore density | 40.12 | 40.17 | | Moisture | −8.02 | −8.11 |
| Mineral grade | 22.47 | 22.76 | | Feed size | 0 (and a ±5.35 t/h sine) | 2.32 |
| Ore hardness | −19.26 | −19.60 | | Temperature | 0 | −0.26 |
| Mill load | 14.44 | 14.30 | | Operating hours | 0 | 0.29 |
| Grinding media | 12.84 | 12.76 | | Water flow | 11.13 | 11.13 |

R² is the share of throughput's variance a model reproduces. The straight-line part of the formula is 96.1 % of
it, the sine wave 1.7 % and the noise 2.2 %. On all rows the regression reaches 0.962 and a model that also knew the
sine 0.978. Replaying seed 42 reaches 1.000; so would a lookup table of these rows, but on rows not yet drawn only the
replay would.

## Checks a real mill would pass and this file fails

- **Mass balance.** In 1,732 rows throughput exceeds the feed rate. In the formula 1 t/h more feed adds
  0.34 t/h of throughput. Read as dry fresh feed and final circuit product, the two are equal at steady state;
  only internal streams, carrying the circulating load, run above the fresh feed.
- **Inputs that move together.** The largest correlation between any two inputs is 0.030. On a mill, water
  is usually ratioed to feed and power draw follows the charge and the speed.
- **Time.** No timestamps, so no test on later data is possible.

## Limits

This shows what a regression learns from this file. It says nothing about how a real mill behaves. The
dataset is not included here: it stays on Kaggle under its own licence (Apache 2.0 when downloaded), and
`recreate.py` rebuilds it.

## Licence

Code: MIT.
