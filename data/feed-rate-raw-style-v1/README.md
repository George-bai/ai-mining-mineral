# Feed rate tag as raw-style records, version 1

A mill feed rate tag (belt weigher, t/h) over 4 days, as the irregular records a historian archive
holds. Used in the article [How to clean plant sensor data?](https://eleticle.com/articles/sensor-data-outlier-removal/).

**What is real and what is not:**

| Part | Source |
|---|---|
| The hourly averages | **Real.** 96 consecutive hours of mill feed rate from a working plant, with the site anonymised, the dates shifted and the values scaled. They are in `hourly-real.csv` |
| The records inside each hour | **Generated.** Built so that every untouched hour averages to its real value (within 1 t/h) |
| Faults and events | **Inserted**, and labelled in the `event` column |

Anything shown from this data must say so: real hourly averages, generated records, inserted faults.

## Files

| File | What it is |
|---|---|
| `generate.py` | The generator. Standard library only; `python3 generate.py` rewrites everything below, identically every time |
| `traces/seed<n>-<variant>.csv` | 6 traces, about 33,700 records and 1.5 MB each: seed 1 in four variants, seeds 2 and 3 as base |
| `events.json` | For every trace: record count, and each event's kind, record count, first and last second |
| `hourly-real.csv` | The 96 real hourly averages the traces are built on. `generate.py` starts from this file |

## How the records are made

1. **True rate.** A straight line through the centres of the real hours, plus slow process variation
   (standard deviation 18 t/h, memory of about 3 minutes), then shifted hour by hour so each hour's mean
   equals the real hourly average.
2. **Inserted events** multiply the true rate (table below).
3. **Reading.** True rate plus measurement noise (4 t/h standard deviation at 1,000 t/h, scaled with
   load). A stopped belt reads exactly 0. Faults then overwrite the reading.
4. **Historian exception test.** The instrument is scanned every 5 seconds. A scan is recorded when it
   differs from the last record by more than 7.5 t/h (0.5 % of span), when 10 minutes have passed, or
   when the belt starts or stops; the scan before a change is recorded too. This gives irregular records:
   about 10 seconds apart on average while running, 10 minutes apart while the value is flat.

Instrument span: 0 to 1,500 t/h. Shifts are 12 hours, counted from the first record.

## Columns

| Column | Meaning |
|---|---|
| `time` | Shifted date and time, to the second |
| `seconds` | Seconds from the first record |
| `true_tph` | The true rate at that moment, with inserted events, without noise or faults. The answer key |
| `reading_tph` | What the tag recorded. **This is the column to treat as plant data** |
| `belt_running` | 1 when the belt runs, 0 when stopped (kept in the same file for simplicity) |
| `event` | Event name, or empty. The answer key; a real export has no such column |

## Faults and events

Hours are counted from the first record.

| Event | Kind | Hours | What happens |
|---|---|---|---|
| `spikes` | Fault | 0 to 12 | Single records far above span. See variants |
| `surge` | Inserted event | 20.0 to 20.5 | True rate × 1.25 |
| `trip` | Inserted event | 30.0 to 31.02 | To zero in 1 min, stopped 40 min (belt off), 20-min ramp back |
| `shutdown and start-up` | Inserted event | 40.0 to 46.92 | 10-min ramp down, stopped 6 h (belt off), 30-min ramp up to 110 %, 15 min back to 100 % |
| `zero drift` | Fault | 58.0 to 59.0 | Feed stops, belt keeps running empty; the weigher reads about −8 t/h. True rate is 0 |
| `empty running belt` | Inserted event | 58.0 to 59.0 | Clean control only: the same hour, reading exactly 0 |
| `failed transmitter` | Fault | 64.0 to 64.25 | Reads −37.5 t/h (−2.5 % of span, the NAMUR NE43 fault level) while the true rate is normal |

Hours 72 to 96 hold no fault and no inserted event.

## Variants

| Variant | Spikes in the first shift |
|---|---|
| `base` | Five single records: 100,000 t/h in hour 3; 180,000, 420,000 and 1,000,000 in hour 7; 650,000 in hour 10 |
| `1-spike` | One: 100,000 t/h in hour 3 |
| `50-spikes` | Fifty, at random scans, between 100,000 and 1,000,000 t/h: just over 1 % of the shift's records |
| `clean-control` | None, and no other fault. Inserted events only |

## Limits: read before reusing

- Only the hourly averages are real. How the rate moves inside an hour, and every fault, is a recipe.
- The source data holds only hours inside a feed-rate band, so the real part has no stops; the stops
  here are inserted.
- The exception test is a plain deadband. Real historians add a compression test with its own settings.
- No status or quality column, no frozen value, no calibration step, no communication loss.
- Spike sizes and durations are illustrative values, not measured faults.
- Flat faults have few records (the failed transmitter has 3), because a flat value passes the exception
  test only every 10 minutes. Rules that count records see them as small; time-weighted totals do not.

## Licence

Code: MIT. Data: CC BY 4.0.
