---
name: flowsheet-reading
description: Read a process flowsheet image (a plant flowsheet, process flow diagram or block diagram) into its units and streams, and write it as a Mermaid flowchart. Use when asked to convert, transcribe or redraw a flowsheet or process drawing.
---

# Reading a flowsheet

Read the drawing the way an engineer does: piece by piece at full size, writing notes as you go, and
following every line from one end to the other. Never write the chart from a look at the whole drawing:
at that size small labels and crossing lines are lost.

Images you have looked at are dropped from the conversation after a while. **After every look, write
what you saw to the notes file before you look at anything else.** The chart is built from the notes.

Use the scripts in this skill's `scripts/` folder; do not write your own image code. Run them from the
folder that holds the drawing; they write into `work/`.

## How to work: let next.py lead

```bash
python3 <this skill>/scripts/next.py <drawing.png>
```

It tells you the one thing to do now. Do it, then run it again. It will not move on while a step is
undone (a tile with no notes, a missing file). Keep going until it says you are done. The steps below are
what it will ask of you; read them once now.

## 1. Look at the whole drawing once

Write `work/overview.md`: what the plant does; its process areas and where each sits (top left, middle
...); the legend if there is one (what each line colour or style means); where the feed comes in and
where products and wastes leave.

## 2. Cut it into tiles

`next.py` does this for you: tiles with rulers in drawing pixels, and `work/notes.md` with an empty
section for each tile.

## 3. Read every tile, in order

Look at each tile in turn, r0c0 first. Straight after each one, fill in its section of `work/notes.md`,
then go on to the next tile. Do every tile before doing anything else.

```
## r0c1 (x 484-1166, y 0-662)
units: BALL MILLS @ (620,230) | CYCLONES (unlabelled) @ (700,140) | ...
lines: CYCLONES -> ROUGHER FLOTATION 1 (overflow) | BALL MILLS -> sump @ (560,300) | line leaves right edge at y 410, going right | ...
```

- Copy every label exactly as written; `?` for a letter you cannot read.
- Give each unit its position from the rulers. When a label appears twice (two BALL MILL), the positions
  keep them apart.
- Equipment without a label that the lines pass through (cyclones, sumps, tanks where lines meet):
  note it by its type and position.
- Arrowheads give the direction. A line with no arrowhead takes the direction of the line it joins.
- A line that leaves the tile: note the edge and the ruler position where it leaves.
- Pumps, conveyors, pipes and valves are not units: the stream runs through them.

- Where two lines seem to continue through a junction, a gap or a crossing, zoom in: they may be two
  separate lines, or one line hopping over another.

Before writing a tile's lines, zoom in on every place where lines meet, cross, split or end, and on every
label too small to read for sure, and write down what you see. Each region once; the zoom script stops
after 60 zooms:

```bash
python3 <this skill>/scripts/zoom.py <drawing.png> <x0> <y0> <x1> <y1>
```

## 4. List the units

Write `work/units.md`, one line per unit: `id | label as written | position | area`. Merge units seen
twice where tiles overlap (same label, same position). Repeated labels get separate ids
(`ball_mill_upper`, `ball_mill_lower`). Include the inputs (reagents, water, air, ore) and the outputs
(products, tailings, vents) labelled on the drawing.

## 5. Trace the streams

**Follow the ore.** From where the feed comes in, follow the main solids or slurry line through each unit to the products and the tailings. Then follow each other circuit the same way: water, solutions, reagents, carbon, gas. Last, for each unit, ask whether anything comes back to it from further on (a recycle), and find that line in your notes.

First join the lines your notes say leave one tile and enter the next, by their ruler positions. Every
stream must have both ends in your notes; where one is missing, zoom in on that place and add it.

Write `work/streams.md`, one line per unit: `id | in from: ... | out to: ...`. Every stream must appear at
both of its ends: what one unit sends, another receives.

## 6. Write the chart

Write `flowsheet.mmd`, only Mermaid code:

```
flowchart TD
  subgraph grinding["Grinding"]
    sag["SAG MILL"]
    cyc["CYCLONES"]
  end
  sag -->|"discharge"| cyc
```

- One box per unit in `work/units.md`, with the label as written (unlabelled equipment by its type, such
  as "Cyclones" or "Sump"). One subgraph per process area.
- One line per stream in `work/streams.md`, in the direction of flow, with the words on the line if any.
- Never put a `"` inside a label: write inches as `in` (`"+1 1/2 in"`). A line with no words has no `|...|`.
- Draw only what is on the drawing. Process knowledge tells you where to look; it never decides what to
  draw. If you cannot see a line, leave it out.

## 7. Check

```bash
python3 <this skill>/scripts/check.py flowsheet.mmd
```

For each unit it lists with no line in or no line out that is not a feed or a product, and each unit
missing from the chart: look again at that place (zoom), then add what you missed or confirm there is
nothing. Fix any line it says may not be valid Mermaid.
