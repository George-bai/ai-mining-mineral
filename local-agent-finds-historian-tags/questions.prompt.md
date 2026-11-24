Do not read any files and do not search the web. Write from this description only.

You are a metallurgist or plant engineer at a mining company. Write 24 requests that people at the company would type to an assistant that can read the plant historian (the database of instrument readings) and draw charts. Write them the way people at a mine actually ask, in your own words: short, sometimes informal, sometimes with site shorthand.

The company: "Example Mining", with 31 sites named Site A, Site B, ... Site Z, Site AA ... Site AE. Each site has five gold concentrators, Concentrator 1 to Concentrator 5. Each concentrator has these areas and equipment:
- Crushing: a primary crusher (motor power, motor current, closed side setting, running or not); four conveyors CV-101 to CV-104, each with a belt weigher (tonnes per hour), belt speed, motor current, running or not.
- Grinding: a SAG mill (fresh feed rate, motor power, bearing pressure, mill speed, feed water, running, run hours); Ball Mill 1 and 2 (motor power, bearing pressure, discharge density, running, run hours); Cyclone Cluster 1 and 2 (feed pressure, feed density, feed flow, overflow density, number of cyclones open); four cyclone feed pumps; a process water flow meter.
- Flotation: rougher cells 1 to 6, scavenger cells 1 to 3, cleaner cells 1 to 3, recleaner cells 1 and 2 (each: air flow, pulp level, froth depth, agitator power); reagent dosing for collector, frother, depressant and activator (dose rate, tank level, pump running); an online analyser on rougher feed, rougher concentrate, rougher tail, cleaner concentrate, final concentrate and final tail (Au and Ag in g/t, Pb and S in %, solids %); pumps; two flotation blowers.
- Leach: leach tanks 1 to 8 (pH, dissolved oxygen, free cyanide, agitator power); cyanide and lime dosing; pumps.
- Tailings: a tailings thickener (underflow density, rake torque, bed level, flocculant dose); underflow pumps; return water flow.
- Utilities: power meters for the main incomer and the crushing, grinding, flotation and leach supplies (active power, energy, power factor); two plant air compressors; raw water flow; a process water tank level.

Write exactly four of each kind, each naming a time window in everyday words (now, yesterday, last week, the past month, since a date in November 2026):
- read: one reading at one place; two of the four also ask for a chart.
- compare: two readings at one place to look at together (for example a rate against a power), with a chart.
- across: several pieces of equipment of one kind at one place, asking which is highest, lowest or most.
- ambiguous: a request that could mean several instruments or places, as people really ask (for example naming a site and a measurement but not which concentrator or which unit).
- code: a request naming one of these point codes, as seen on a control-room screen, without saying what it is. Use four different ones:
- `SI-C3-AT-4023`: Site I\Concentrator 3\Leach\Leach Tank 6 · Free Cyanide
- `SA-C1-LT-5003`: Site A\Concentrator 1\Tailings\Tailings Thickener · Bed Level
- `SITEC.CONC2.CRU.CV1.SPD`: Site C\Concentrator 2\Crushing\CV-101 · Belt Speed
- `SITEG.CONC5.CRU.CV4.RATE.QC`: Site G\Concentrator 5\Crushing\CV-104 · Belt Weigher Rate QC
- `SVC5_PP7_FLOW2`: PP7 FLOW spare (not in the asset tree)
- `SRC1_BL1_AIR2`: BL1 AIR spare (not in the asset tree)
- unhealthy: a request for one of these readings, in plain words, without suggesting anything is wrong with it. Use four different ones, each a different site:
- Site X, Concentrator 3, Flotation, Final Tail · Pb
- Site I, Concentrator 2, Leach, Leach Tank 5 · Agitator Power
- Site AE, Concentrator 1, Flotation, Cleaner Cell 1 · Agitator Power
- Site R, Concentrator 5, Grinding, SAG Mill · Bearing Pressure
- Site S, Concentrator 2, Flotation, Rougher Conc Pump · Speed
- Site Y, Concentrator 1, Flotation, Depressant · Dose Rate
- Site K, Concentrator 5, Grinding, Ball Mill 1 · Run Hours
- Site E, Concentrator 3, Crushing, CV-104 · Belt Weigher Rate

Spread the requests over many sites and concentrators and over all areas. Do not ask about recovery, mass balance, costs, or anything the historian does not measure directly.

Output only YAML: a list of items with keys id (t01 to t24), type (read, compare, across, ambiguous, code, unhealthy) and question.
