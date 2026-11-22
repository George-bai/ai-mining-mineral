# Answer keys for the two test drawings

An answer key lists what is really on a drawing: its units, its streams and its main loops. Each model's
chart is scored against it. It is made before any test run and frozen; it is never changed to suit a
result.

Made by two readers working apart, Claude and Codex, from the cropped figures in
`data/flowsheets-anderson-v1/local/figures/` (George, 15 Nov 2026: "work with codex to get the
reference answer and both of you need to do a double check"). How they were made is under "Procedure";
the record of every disagreement and how it was settled is in `log.md`.

| File | Drawing |
|---|---|
| `p39-phoenix-mine-mill.yaml` | Slide 39, Phoenix mine mill |
| `p37-twin-creeks-mine.yaml` | Slide 37, Twin Creeks mine ("Sage Mill Flowsheet") |

## What counts

**Items.** Every item has an `id` (lower case, letters, digits and `_`), a `label` exactly as written
on the drawing (empty if the item has none), a `name` in plain words, an `area` and a `kind`:

| Kind | What it is | Examples |
|---|---|---|
| `unit` | A piece of equipment, a vessel, a stockpile, a pond or a process step, drawn as a symbol or box | Mill, cyclones, flotation cells, thickener, tank, filter, stockpile, tailings pond |
| `input` | Something fed in from outside the drawing, shown as a label with an arrow in. Each labelled arrow is its own item. An unlabelled source is not an item | Reagents, water, lime, cyanide, flocculant, air, steam, natural gas, mined ore |
| `output` | Where a stream leaves the drawing: a label with an arrow out, or a destination drawn with no line leaving it | Concentrate to market, to refinery, to atmosphere, vent, a carbon bin |
| `junction` | An unlabelled pump box, sump, launder, distributor or splitter where lines join or split | The box under a mill that several lines run into |
| `carrier` | A conveyor or vehicle that has its own label | Radial stacker, front end loader |

- **Not items:** pumps, conveyors, pipes, valves, feeders and vehicles without a label of their own.
  They only carry a stream from one item to the next; the stream runs through them.
- **Scoring passes through junctions and carriers:** a chart may draw A → sump → B or A → B, and both
  count as the stream from A to B.
- **A row of identical vessels under one label** (a tank train, "Cells (6)") is one unit; write the
  count in `count`. Streams between the vessels of the row are not listed.
- **An unlabelled unit** that is clearly equipment (a cyclone, a tank with an agitator) is listed with
  `label: ""` and a `name` saying what it is.
- Words written on the drawing that are not item labels (tonnages, grades, stream names such as
  "(LOADED CARBON)") are not items. Stream names go in the stream's `label`; tonnages and grades are
  left out.
- **Labels** keep the drawing's spelling, capitals and punctuation; a line break becomes one space.
  Where the text is blurred, write the word a careful reader reads, and mark it unsure if that word is
  not certain.

**Streams.** One per drawn line from one item to another, in the direction of its arrow. A line that
splits gives one stream per branch; lines that join give one stream each. `label` holds any words
written on the line. An input whose arrow joins a line goes to the item that line ends at. A transfer
that the drawing shows only by a picture (a loader beside a pile) and not by a line is unsure. Two or more
drawn lines between the same two items (parallel branches, a header feeding several inlets of one unit)
are one stream in the key: a chart needs only one line between them.

**Unsure.** `unsure: true` on any item or stream that cannot be read with confidence: a blurred label,
a line that cannot be followed through a crossing, an arrow whose direction cannot be seen. Unsure
entries are not scored: a chart neither gains nor loses for them. Say why in `note`.

**Loops.** The plant's main recycle paths, each a list of item ids that starts and ends on the same
item, with a `name` saying what it does in the process (for example "cyclone underflow back to the
ball mill"). Every step of a loop must be a stream in the key.

## Pairing repeated labels when scoring

When a chart has several boxes with the same label (two BALL MILL, three CYCLONE), each is paired with a
key item by this order of evidence, the same for every chart and both conditions:

1. **What the chart says about the box**: a position or role in its label, id or subgraph that identifies
   one key item ("upper", "left", "regrind", "sand", "pyrrhotite", "nickel"). A bare number ("CYCLONE 2",
   `BM1`) is the model's own numbering and does not count.
2. **What the box receives**: if one of its incoming lines comes from a box already paired without doubt,
   and that line identifies one key item (the ball mill fed by the rod mill is the primary ball mill).
3. **The scorer's tie-break**: the candidate whose lines agree best with the key.

A box that matches no key item (a stream label drawn as a box, a unit not on the drawing) is paired with
nothing and its lines run through it. This includes a box whose label matches but whose own position or
role in the chart names a unit the drawing does not have: two "Cyclones" placed under the SAG screen, where
the drawing has a sump and no cyclones, are paired with nothing, not with the ball mill cyclones.

Added 16 Nov 2026, before the test runs (they narrow the plan's wording "a box that holds two items is paired with
both"), applied alike to every chart of both conditions:

- **A box whose label names two items** ("WATER LIME", "TK-28 (UNIT CELLS AND CLEANERS)") pairs with both.
- **One box standing for several units that share a label** (one "INSIDE DRUM FILTERS" box for the nickel and the copper
  filters; one "MAGNETIC SEPARATORS" for two separators; one "BALL MILLS" for three mills) pairs with one of them, the one
  the scorer chooses by its lines, never chosen by hand; the others count as missed, since the chart merged them.
- **A box given a role the drawing does not have** (a "Cyclone" where the drawing has a sump) pairs with nothing when the
  chart has another box for the item that sits there; when it is the chart's only box for that item and is wired as that
  item (two "SAG cyclones" in closed circuit with the ball mills and feeding the roughers), it pairs with that item by
  rule 1 or 2.
- **A stream label drawn as a box** ("Bulk Ni-Cu Conc.", "GOLD BEARING SLUDGE", "Scats") pairs with nothing; its lines
  run through it.

Added 16 Nov 2026, during the hand checks of the test charts. They write down calls already made, applied alike to
both conditions:

- **One item drawn as two boxes** (the CIL tanks as "Carbon-in-Leach" and "OIL Tank (7)"; the flash vessels and a
  "Vessel" below them; the carbon wash screen as "Screen" and "Carbon Wash"): both boxes pair with that item.
- **A stream label drawn as a box where the chart has no box for the item it comes from**, wired as that item (a "Lime"
  box feeding the tower mill, with no lime silo box): it pairs with that item by rule 1 or 2, as for a role the drawing
  does not have. Where the chart has its own box for the item, the label box pairs with nothing.

Added 16 Nov 2026, 8:45 pm AEST, during the hand checks of the 27B rerun, before its last Twin Creeks charts were scored.
It applies the rule above on a role the drawing does not have; the first run's checks had kept these boxes as the scorer
paired them:

- **A "Trash Screen" box fed only by the jaw crusher or the radial stacker** (Twin Creeks' oxide crushing line, which has
  no trash screen on the drawing) pairs with nothing; its lines run through. Applied to all 12 charts of the 27B rerun and,
  as a dated correction, to the six 27B Twin Creeks charts of its first run. No Flash Next chart has such a box: all its
  trash screens are fed by cyclones or mills.

## Format

```yaml
drawing: p39-phoenix-mine-mill
items:
  - {id: ball_mill, label: "BALL MILLS", name: ball mills, kind: unit, area: grinding}
  - {id: reag_1, label: "REAGENTS", name: reagents to flotation, kind: input, area: flotation}
  - {id: cip, label: "CIP", name: carbon-in-pulp tanks, kind: unit, area: leach, count: 7}
streams:
  - {from: ball_mill, to: cyclones}
  - {from: cip, to: carbon_bin, label: "", unsure: true, note: line lost at the crossing near x=1500}
loops:
  - {name: cyclone underflow back to the ball mill, path: [ball_mill, cyclones, ball_mill]}
```

Optional fields: `count`, `unsure` (default false), `note`.

## Procedure

1. **Items.** Each reader lists the items alone, without seeing the other's list. The two lists are
   lined up by label; every difference is looked at again on the drawing by both, at full zoom; the
   agreed list gets fixed ids.
2. **Streams.** Each reader lists the streams alone, over the agreed ids. The two lists are compared
   line by line; every difference is looked at again by both.
3. **Loops.** Each proposes the main loops; they agree on the list.
4. **Double check.** Each reader, separately, reads the whole agreed key against the drawing once more
   and reports anything wrong. Every report is settled in `log.md`.
5. **Frozen** before any test run: the SHA-256 of each file is recorded in `log.md`.
