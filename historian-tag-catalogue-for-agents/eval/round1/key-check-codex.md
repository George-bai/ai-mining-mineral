**29 OK, 1 CHANGE.** All 30 `counts_as` values fit the questions. Only q20 needs a tag correction. All 276 tag entries currently in the key exist in `plant-attributes.tsv` and link to the stated PI point.

For q20, each suffix in the table completes the path `\\EXAMPLE-AF\Operations\Example Mining\Site {S}\Concentrator 2\`, where `{S}` takes each of the 31 site names A through Z and AA through AE.

| ID | Verdict | `counts_as` | Check or exact correction |
|---|---|---|---|
| q01 | OK | one | Site D con 2 SAG Mill Motor Power is the requested reading, in MW. |
| q02 | OK | one | Site AA con 1 Primary Crusher Closed Side Setting, in mm. |
| q03 | OK | one | Site F con 3 CV-103 Belt Speed, in m/s. |
| q04 | OK | one | Site M con 1 Cyclone Cluster 2 Feed Pressure, in kPa. |
| q05 | OK | one | Site H con 2 Cleaner Cell 3 Froth Depth, in mm. |
| q06 | OK | one | Site AE con 1 Return Water Flow is recorded in the requested L/s. |
| q07 | OK | one | Site K con 4 Main Incomer Power Factor. |
| q08 | OK | one | Site P con 2 Leach Tank 7 Dissolved Oxygen, in ppm. |
| q09 | OK | one | Site J con 2 CV-101 Belt Weigher Rate measures the requested tonnage rate in t/h. |
| q10 | OK | one | Site R con 1 Primary Crusher Motor Current gives the requested amps. |
| q11 | OK | one | Site AB con 3 Final Tail Au gives gold grade in g/t. |
| q12 | OK | one | Site L con 1 Ball Mill 2 Run Hours is the accumulated-hours reading. |
| q13 | OK | one | Site U con 2 Frother Dose Rate, in mL/min. |
| q14 | OK | one | Site Y con 1 SAG Mill Motor Power is the right tag. Divide its kW reading by 1,000 to express it in MW. |
| q15 | OK | none | No point name contains `FT-3104`. Both near matches make sense on the specified flotation screen. `SA-C1-PT-3104` matches the number, and `SA-C1-FT-3105` measures flow on the same cleaner feed pump. |
| q16 | OK | none | No point name contains `PIT-2201`. `SBC2_CYC1_PRES` and `SBC2_CYC2_PRES` are the two cyclone-cluster feed pressures on Site B con 2. |
| q17 | OK | none | No point name contains `LT-6102`. `SITEC.CONC1.UTL.TK1.LVL` is the process water tank level at the specified location. |
| q18 | OK | none | No point name contains `AIT-4103`. The eight Site E con 3 leach-tank pH readings are sensible near matches for the named screen. |
| q19 | OK | ambiguous | All 105 primary Site B pressure readings are present, 21 per concentrator across all five. |
| q20 | **CHANGE** | ambiguous | Keep the 93 existing paths. At **each of the 31 sites**, add `Grinding\SAG Mill\|Feed Water Flow`, `Grinding\Process Water\|Totalised Flow`, `Tailings\Return Water\|Totalised Flow`, and `Utilities\Raw Water\|Totalised Flow`. The SAG feed is a water-use rate, and “how much” also admits a volume reading from each of the three named water streams. **124 additions, 217 AF paths total.** |
| q21 | OK | ambiguous | All 12 primary grade readings are present. Rougher, cleaner and final concentrate each have Au, Ag, Pb and S assays. Solids percentage measures slurry composition rather than elemental grade. |
| q22 | OK | ambiguous | All 15 mill Run Status tags are present. Each of Site AC’s five concentrators has one SAG mill and two ball mills. |
| q23 | OK | several | All eight Site C con 1 leach-tank pH readings are present for the lowest-pH comparison. |
| q24 | OK | several | All six Site V con 2 rougher-cell Air Flow readings are present. |
| q25 | OK | several | All four Site G con 3 Run Status tags are present for CV-101 through CV-104. |
| q26 | OK | several | Both Site AD con 1 ball-mill Discharge Density readings are present. |
| q27 | OK | none | Site A con 1 Final Tail Au has no QC attribute or QC point. The primary Au point `SA-C1-AT-3094` is the appropriate near match. |
| q28 | OK | none | Site T con 2 SAG Fresh Feed Rate has no Calc or 15-minute moving-average attribute or point. The SAG Calc attribute at this location is for **feed water flow**. The primary feed-rate point `ST2:2WT001`, in t/h, is the appropriate near match. |
| q29 | OK | none | Site Z con 1 Tailings Thickener has no rake-torque alarm attribute or point, including among unlinked points. The measured torque `SZC1_TH1_TORQ` is the appropriate near match. |
| q30 | OK | none | Site W con 3 Process Water Tank has no low-level alarm attribute or point, including among unlinked points. The measured level `SITEW.CONC3.UTL.TK1.LVL` is the appropriate near match. |

**Systematic findings**

- The q20 selector requires the attribute name `Flow` on three named assets. That excludes both the SAG mill’s `Feed Water Flow` and every `Totalised Flow` meter across all 31 sites.
- One of the 124 additions has a catalogue defect. The Site E con 2 `Grinding\Process Water|Totalised Flow` AF path exists, but its reference `SE-C2-FQ-2049_OLD` is marked broken and the point is absent. It counts under the stated AF-path rule. The other 123 additions resolve to PI points.