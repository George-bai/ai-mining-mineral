**57 OK, 3 CHANGE.** q04 and q53 each need a run-status tag. q40 is missing two analyser readings. All 149 paths currently in the key exist in the asset tree. q01 is the only one whose referenced PI point is missing.

| ID | Verdict | `counts_as` | Finding or exact correction |
|---|---|---|---|
| q01 | OK | one | The primary crusher’s `Closed Side Setting` is the correct AF search result. Its reference to `SA-C2-ZT-1003_OLD` is broken, so the tag cannot supply the 6 am value. |
| q02 | OK | one | CV-104 `Belt Speed` supplies the requested trend. |
| q03 | OK | one | SAG `Fresh Feed Rate` is the requested reading. |
| q04 | **CHANGE** | **one → several** | Keep `Discharge Density`. Add `\\EXAMPLE-AF\Operations\Example Mining\Site D\Concentrator 4\Grinding\Ball Mill 2\|Run Status`. The question gives no stop time. The status transition identifies when to take the preceding density reading. |
| q05 | OK | one | Cluster 1 `Cyclones Open` gives the count directly. |
| q06 | OK | one | Rougher Cell 6 `Air Flow` matches. |
| q07 | OK | one | Final Concentrate `Ag` is the silver analyser reading. |
| q08 | OK | one | Frother `Tank Level` matches. |
| q09 | OK | one | Leach Tank 3 `Dissolved Oxygen` supplies the trend. |
| q10 | OK | one | Leach Tank 8 `Free Cyanide` matches. |
| q11 | OK | one | Tailings Thickener `Rake Torque` supplies the four-hour history. |
| q12 | OK | one | Return Water `Flow` gives the rate at shift start. |
| q13 | OK | one | The minimum comes from the Grinding Supply `Power Factor` history. |
| q14 | OK | one | Successive Process Water Tank `Level` readings show whether the level is dropping. |
| q15 | OK | one | Recleaner Cell 2 `Agitator Power` matches. |
| q16 | OK | one | Raw Water `Flow` matches the incoming water rate. |
| q17 | OK | one | Primary Crusher `Closed Side Setting` measures how tight the crusher was set. |
| q18 | OK | one | CV-102 `Belt Weigher Rate` is measured in tonnes per hour. |
| q19 | OK | one | Ball Mill 1 `Run Hours` is the accumulated reading. |
| q20 | OK | one | SAG `Feed Water Flow` measures water added at the feed end. |
| q21 | OK | one | Cleaner Cell 1 `Froth Depth` matches “the first cleaner.” |
| q22 | OK | one | Final Tail `Au` gives the gold result for the last sample. |
| q23 | OK | one | The Collector `Pump Run Status` transition gives the restart time. |
| q24 | OK | one | Leach Tank 6 `Dissolved Oxygen` matches “DO.” |
| q25 | OK | one | Tailings Thickener `Underflow Density` measures the material leaving the bottom. |
| q26 | OK | one | Tailings Thickener `Flocculant Dose` measures the floc addition rate. |
| q27 | OK | one | Process Water Tank `Level` gives fullness at shift start. |
| q28 | OK | one | Main Incomer `Active Power` covers the whole concentrator. Its kW reading converts to MW. |
| q29 | OK | none | `CV103-II` is absent. `SI-C5-IT-1015`, CV-103 motor current, is a sensible near match. |
| q30 | OK | none | `SAG01-SI` is absent. `SJC2_SAG1_SPD` measures SAG mill speed. |
| q31 | OK | none | `CY02-PIT` is absent. `SITEO.CONC4.GRD.CYC2.PRES` measures Cluster 2 feed pressure. The same reading also has a `Calc` variant. |
| q32 | OK | none | `RGH04-FIT-AIR` is absent. `SAB3:3FT013` measures Rougher Cell 4 air flow. The separate `.ALM` point is an alarm. |
| q33 | OK | none | `AIT-FINALTAIL-AU` is absent. `SE-C1-AT-3094` is the Final Tail gold analyser point. |
| q34 | OK | none | `LT07-AIT-PH` is absent. `SVC5_LT7_PH` measures Leach Tank 7 pH. The same reading also has a `Calc` variant. |
| q35 | OK | none | `TH01-LIT` is absent. `SITEAA.CONC4.TLS.TH1.BED` measures thickener bed level. |
| q36 | OK | none | `INC01-KWH` is absent. `SM-C2-JQ-9002` is the Main Incomer energy meter. Its MWh reading converts to kWh. |
| q37 | OK | ambiguous | The three mill motor-power tags cover the individual mills. Grinding Supply `Active Power` covers the grinding-area interpretation. |
| q38 | OK | ambiguous | Both feed and overflow density are included for each of the two cyclone clusters. |
| q39 | OK | ambiguous | All 30 rougher air-flow tags are included, six cells at each of Site N’s five concentrators. |
| q40 | **CHANGE** | **ambiguous** | Keep the eight elemental readings. Add `\\EXAMPLE-AF\Operations\Example Mining\Site X\Concentrator 2\Flotation\Rougher Tail\|Solids` and `\\EXAMPLE-AF\Operations\Example Mining\Site X\Concentrator 2\Flotation\Final Tail\|Solids`. Both analysers report solids on the sample, and the question leaves the measurement open. The corrected set has 10 tags. |
| q41 | OK | ambiguous | The six `Pump Run Status` tags cover the four flotation reagents plus cyanide and lime in leach. |
| q42 | OK | ambiguous | The tank is unspecified, and all eight leach tank pH readings are included. |
| q43 | OK | ambiguous | The four conveyor `Run Status` tags cover the unspecified belt. |
| q44 | OK | ambiguous | All five Site Y concentrators’ thickener bed-level tags are included. |
| q45 | OK | several | All four named conveyors’ belt-weigher rates are included. |
| q46 | OK | several | Both ball mills’ run-hour counters are included. |
| q47 | OK | several | Both cyclone cluster feed-pressure tags are included. |
| q48 | OK | several | All six rougher cells’ froth-depth tags are included. |
| q49 | OK | several | The four tank-level tags correspond to the four named reagents. |
| q50 | OK | several | The eight pH tags are present in the requested tank order. |
| q51 | OK | several | Each of the four named supplies has its own `Active Power` tag. All four store MW, convertible to kW. |
| q52 | OK | several | All three scavenger cells’ agitator-power tags are included. |
| q53 | **CHANGE** | **one → several** | Keep `Fresh Feed Rate`. Add `\\EXAMPLE-AF\Operations\Example Mining\Site J\Concentrator 2\Grinding\SAG Mill\|Run Status`. The status history defines the running intervals over which to average feed. |
| q54 | OK | several | CV-104 belt-weigher rate, belt speed and motor current are exactly the three traces requested. |
| q55 | OK | one | The Leach Tank 7 pH history supplies both the threshold crossings and the duration below 10. |
| q56 | OK | one | Two readings of the same Flotation Supply `Energy` meter give consumption. Convert the MWh difference to kWh. |
| q57 | OK | one | The rake-torque history supplies the percentage and duration above 80%. |
| q58 | OK | one | The 2 am value and both neighbouring samples come from the same Rougher Feed `Au` point. |
| q59 | OK | one | Five-minute averages and their maximum can be calculated from Main Incomer `Active Power`. |
| q60 | OK | several | CV-101 `Run Status` and `Belt Weigher Rate` supply both conditions for counting minutes. |

**Systematic findings**

- All eight `none` codes had zero case-insensitive substring matches across all 50,251 PI point names, including unlinked points, and zero matches across all 47,369 AF paths. Checking QC, Calc, alarm and moving-average names preserved all eight verdicts. The same-reading variants found were the q31 and q34 Calc attributes and the q32 alarm point.
- q01 distinguishes tag-search scoring from reading availability. The stated rules accept the existing AF path. The other 148 keyed paths each resolve to a PI point that links back to that path.
- With the corrections, the key has **32 `one`, 12 `several`, 8 `ambiguous` and 8 `none`**.