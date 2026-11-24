Do not read any files and do not search the web. Write from this description only.

You are a metallurgist and plant engineer at a mining company. Write 30 questions that people at the company would ask an assistant that can read the plant historian (the database of instrument readings). The questions are a test set for a tag search system, so write them as people really ask: short, informal, sometimes vague, sometimes with abbreviations, sometimes naming an instrument tag code they saw on a screen.

The company: "Example Mining", with 31 sites named Site A, Site B, ... Site Z, Site AA ... Site AE. Each site has up to five gold concentrators (Concentrator 1 to 5). Each concentrator has these areas and equipment:
- Crushing: a primary crusher (motor power, motor current, closed side setting, running or not); four conveyors CV-101 to CV-104, each with a belt weigher (tonnes per hour), belt speed, motor current, running or not.
- Grinding: a SAG mill (fresh feed rate, motor power, bearing pressure, mill speed, feed water, running, run hours); Ball Mill 1 and 2 (motor power, bearing pressure, discharge density, running, run hours); Cyclone Cluster 1 and 2 (feed pressure, feed density, feed flow, overflow density, number of cyclones open); four cyclone feed pumps; a process water flow meter.
- Flotation: rougher cells 1 to 6, scavenger cells 1 to 3, cleaner cells 1 to 3, recleaner cells 1 and 2 (each: air flow, pulp level, froth depth, agitator power); reagent dosing for collector, frother, depressant and activator (dose rate, tank level, pump running); an online analyser sampling rougher feed, rougher concentrate, rougher tail, cleaner concentrate, final concentrate and final tail (Au and Ag in g/t, Pb and S in %, solids %); pumps; two flotation blowers.
- Leach: leach tanks 1 to 8 (pH, dissolved oxygen, free cyanide, agitator power); cyanide and lime dosing; pumps.
- Tailings: a tailings thickener (underflow density, rake torque, bed level, flocculant dose); underflow pumps; return water flow.
- Utilities: power meters for the main incomer and the crushing, grinding, flotation and leach supplies (active power, energy, power factor); two plant air compressors; raw water flow; a process water tank level.

Different sites have different instrument naming conventions, and some show power in MW instead of kW, flows in L/s, pressures in bar. Each instrument has an ISA-style code on the DCS screens at some sites, for example a flow transmitter in the flotation area might be shown as FT-3104 at Site A concentrator 1.

Cover, with about this many of each:
- 8 plain questions naming the place and the measurement in different words ("SAG power at site D con 2 last week").
- 6 questions using synonyms or plant slang instead of the instrument name (throughput, tonnage, draw, amps, grade, tails, uptime, dosage).
- 4 questions that name an instrument code or tag as someone saw it on a screen (invent plausible ones in the style above, for sites A to E).
- 4 ambiguous questions that could mean several instruments or places ("what's the pressure at site B").
- 4 questions about several instruments of one kind in one place ("which leach tank at site C has the lowest pH").
- 4 questions asking for a variant: a QC'd or calculated value, or an alarm.
Do not ask about recovery, mass balance, costs, or anything the historian does not measure directly.

Output only YAML: a list of items with keys id (q01 to q30), type (plain, synonym, code, ambiguous, several, variant) and question.
