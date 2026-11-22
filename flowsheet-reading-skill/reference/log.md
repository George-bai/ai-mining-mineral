# How the answer keys were made

The record of every difference between the two readers, Claude and Codex, and how it was settled.
Procedure and rules: `README.md`. Codex ran as `codex exec` (Codex CLI 0.169.0, its configured model),
in a folder holding only the drawing and the rules, so neither reader saw the other's work before the
comparison.

## Stage 1: items (15 Nov 2026)

Both readers listed the items alone. Claude: 79 items on Phoenix, 83 on Twin Creeks. Codex: 78 and 84.
Every label matched between the two lists (after line breaks were removed). The differences were all
about what kind of item something is, or whether it is an item at all:

| Drawing | Difference | Settled | Why |
|---|---|---|---|
| Phoenix | CARBON BIN: Claude unit, Codex output | Output | No line leaves it; rule added: a dead-end destination is an output |
| Phoenix | Box before the tailings pond with CARO'S ACID: Claude unit, Codex junction | Junction | Drawn as a plain box like the other sumps |
| Phoenix | Unlabelled well below FRESH WATER: Claude input, Codex not listed | Not an item | Rule added: inputs must be labelled. Its stream is not scored |
| Twin Creeks | Radial Stacker: Claude unit, Codex not listed (a conveyor) | Kind `carrier` | It is a conveyor, but labelled; a chart that names it should not lose for it. Rule added: labelled conveyors and vehicles are carriers, passed through in scoring |
| Twin Creeks | Front End Loader: Codex unit (unsure), Claude not listed | Kind `carrier` | Same rule |
| Twin Creeks | Unlabelled loader by the oxide stockpile: Codex unit (unsure), Claude not listed | Not an item | Unlabelled vehicle |
| Twin Creeks | Two thickener overflow boxes: Claude unit, Codex junction | Junction | Pump boxes |
| Twin Creeks | Ore Blend Stockpiles: Codex count 3, Claude no count | Count 3 | Three piles are drawn |

Rules added to `README.md` at this stage: the `carrier` kind; inputs must be labelled; dead-end
destinations are outputs; line breaks in labels become spaces; blurred text is written as a careful
reader reads it; an input joining a line goes to the item that line ends at; a transfer shown only by a
picture is unsure. Codex was given the settlements with the stage 2 task and asked to object with
evidence if it disagreed.

Agreed items: 78 on Phoenix, 84 on Twin Creeks.

## Stage 2: streams (15 Nov 2026)

Both readers listed the streams alone, over the agreed item ids. Codex worked from its own enlarged crops
of the drawing; its log shows it read no file outside its folder.

| Drawing | Claude | Codex | Same from → to pairs |
|---|---|---|---|
| Phoenix | 99 | 99 | all 99 |
| Twin Creeks | 101 | 101 (118 records, branches kept apart) | all 101 |

The only differences were three unsure flags, all accepted: a transfer the drawing shows only by a
picture or by adjoining equipment, with no line, is unsure under the rules.

| Drawing | Stream | Settled |
|---|---|---|
| Phoenix | `cu_stockpile → conc_to_market` | Unsure: loader and truck, no line |
| Phoenix | `first_cleaner → cleaner_scavenger` | Unsure: the banks adjoin, no arrow between them |
| Twin Creeks | `rom_refractory_ore → ore_blend_stockpiles` | Unsure: truck beside the piles, no line |

## Stage 3: loops

The two lists of loops were joined and duplicates removed. A loop that runs through an unsure stream is
itself unsure and is not scored.

## Stage 4: double check (15 Nov 2026)

**Claude** listed every item's inputs and outputs from the agreed key and compared each against the
drawing again. No new error found.

**Codex** read the whole key against the drawing again in a fresh session, area by area, and reported 14
findings:

| Drawing | Finding | Settled |
|---|---|---|
| Twin Creeks | Nine places where two drawn lines join the same two items (two heater vents, two kiln feeds, the autoclave feed header, ...) are one stream in the key | No change to the keys. Rule added to `README.md`: parallel lines between the same two items are one stream, since a chart needs only one line between them. Scores count item pairs, so the number of drawn lines does not change any score |
| Phoenix | Same, for the reagent line that splits to both rougher banks | As above |
| Twin Creeks | Five notes containing commas were read by YAML as stray extra fields | Fixed: moved back into the notes. A format slip from writing the key, not a reading error |
| Phoenix | Label is `CLEANER/ SCAVENGER FLOTATION` under the rule that a line break becomes a space | Accepted |
| Phoenix | The split between 2 leach tanks and 5 CIP tanks is readable: carbon moves only between tanks 3 to 7 | Accepted: `leach` is no longer unsure |
| Phoenix | A recycle is missing from the loops: rougher concentrate through flotation gravity, cleaner gravity and cyanidation, with the residue back to grinding | Accepted: loop added |

## Frozen, 15 Nov 2026, before any test run

| File | Items | Streams (unsure) | Loops (unsure) | SHA-256 |
|---|---|---|---|---|
| `p39-phoenix-mine-mill.yaml` | 78 | 99 (3) | 13 (2) | `5991c8dd0ef53d3faeb72650dddf48515f8ae997c3a021a0746db61239c7ee31` |
| `p37-twin-creeks-mine.yaml` | 84 | 101 (4) | 12 (0) | `33a4324722922fb8688d3cce7346f4ee7191a90370b70ae5b5776f2239fa4b76` |

The scorer (`public/score.py`) passes junctions and carriers through, so after that the scored counts
are 90 streams and 11 loops on Phoenix, 90 streams and 12 loops on Twin Creeks.

## Development drawings

The skill is developed on two other drawings from the same lecture, slide 41 (a copper mine process flow
sheet) and slide 48 (Lynn Lake copper-nickel mill). Their keys were made the same way, with both readers
reading the whole drawing alone (items and streams together): on slide 41 the two keys agreed on every
stream, and Codex's choice to keep the two ball mill circuits apart was adopted; on slide 48 they agreed
on every stream, and the unsure flags were settled together. These keys stay in `local/` with the
drawings and are not published.

## Checked at the skill's freeze, 16 Nov 2026, 10:52 am AEST

Both keys hash as recorded above; nothing in them changed during development. Rules for pairing repeated labels, a box
naming two items, one box for several units, a role the drawing does not have and stream labels drawn as boxes were
added to `README.md` before the test runs.
