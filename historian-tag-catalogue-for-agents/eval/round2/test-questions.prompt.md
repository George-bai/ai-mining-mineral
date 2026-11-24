Do not read any files and do not search the web. Write from this description only.

You are a metallurgist and plant engineer at a mining company. Write 60 questions that people at the company would ask an assistant that can read the plant historian (the database of instrument readings). Write them the way people at a mine actually ask, in your own words.

The company: "Example Mining", with 31 sites named Site A, Site B, ... Site Z, Site AA ... Site AE. Each site has five gold concentrators, Concentrator 1 to Concentrator 5. Each concentrator has these areas and equipment:
- Crushing: a primary crusher (motor power, motor current, closed side setting, running or not); four conveyors CV-101 to CV-104, each with a belt weigher (tonnes per hour), belt speed, motor current, running or not.
- Grinding: a SAG mill (fresh feed rate, motor power, bearing pressure, mill speed, feed water, running, run hours); Ball Mill 1 and 2 (motor power, bearing pressure, discharge density, running, run hours); Cyclone Cluster 1 and 2 (feed pressure, feed density, feed flow, overflow density, number of cyclones open); four cyclone feed pumps; a process water flow meter.
- Flotation: rougher cells 1 to 6, scavenger cells 1 to 3, cleaner cells 1 to 3, recleaner cells 1 and 2 (each: air flow, pulp level, froth depth, agitator power); reagent dosing for collector, frother, depressant and activator (dose rate, tank level, pump running); an online analyser sampling rougher feed, rougher concentrate, rougher tail, cleaner concentrate, final concentrate and final tail (Au and Ag in g/t, Pb and S in %, solids %); pumps; two flotation blowers.
- Leach: leach tanks 1 to 8 (pH, dissolved oxygen, free cyanide, agitator power); cyanide and lime dosing; pumps.
- Tailings: a tailings thickener (underflow density, rake torque, bed level, flocculant dose); underflow pumps; return water flow.
- Utilities: power meters for the main incomer and the crushing, grinding, flotation and leach supplies (active power, energy, power factor); two plant air compressors; raw water flow; a process water tank level.
Instruments have tag codes on the control-system screens.

Write about this many of each kind:
- 16 questions naming a place and a measurement.
- 12 questions that use the words people use on site rather than the instrument's name.
- 8 questions that name an instrument by a tag code someone saw on a screen.
- 8 questions that could mean several instruments or places.
- 8 questions about several instruments of one kind in one place.
- 8 questions asking for a checked, calculated or alarm version of a reading.
Spread the questions over many different sites and concentrators and over all areas. Do not ask about recovery, mass balance, costs, or anything the historian does not measure directly.

Output only YAML: a list of items with keys id (q01 to q60), type (plain, synonym, code, ambiguous, several, variant) and question.
