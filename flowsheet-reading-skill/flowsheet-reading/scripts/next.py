"""Say what to do next in reading a flowsheet, one step at a time, and refuse to move on while a step is
undone. Run it from the folder that holds the drawing, again after every step:
    python3 next.py <drawing.png>
It keeps no state of its own: it reads what is in work/."""
import re, subprocess, sys
from pathlib import Path

here = Path(__file__).parent
drawing = Path(sys.argv[1])
work = Path("work")
notes, overview, units, streams, chart = work / "notes.md", work / "overview.md", work / "units.md", work / "streams.md", Path("flowsheet.mmd")


def filled(text, min_chars=15):
    """True when a notes section holds more than its empty template."""
    body = re.sub(r"^(units|lines):\s*$", "", text, flags=re.M)
    body = re.sub(r"\b(units|lines):", "", body)
    return len(re.sub(r"\s", "", body)) >= min_chars


def say(text):
    print(text)
    sys.exit(0)


if not overview.exists() or not filled(overview.read_text(), 40):
    say(f"STEP 1. Look at the whole drawing once (read {drawing}). Write work/overview.md: what the plant does, its "
        "process areas and where each sits, the legend if any, where the feed comes in and where products and "
        "wastes leave. Then run next.py again.")

if not (work / "tiles").exists():
    subprocess.run([sys.executable, here / "tile.py", drawing, work], check=True)

sections = re.split(r"(?m)^(?=## r\d+c\d+)", notes.read_text())
sections = [s for s in sections if s.startswith("## r")]
for s in sections:
    name = s.split()[1]
    if not filled(s.split("\n", 1)[1] if "\n" in s else ""):
        say(f"STEP 3. Read work/tiles/{name}.png now. Before writing its lines, zoom.py every place on this tile "
            "where lines meet, cross, split or end, and every label too small to read for sure; read each zoom. Then "
            f"fill its section '## {name}' in work/notes.md: every unit with its label exactly as written and its "
            "position from the rulers, and every line with where it goes (or where it leaves the tile, with the "
            "ruler position). Then run next.py again.")

if not units.exists() or sum("|" in l for l in units.read_text().splitlines()) < 3:
    say("STEP 4. All tiles are in your notes. Write work/units.md, one line per unit: "
        "id | label as written | position | area. Merge units seen twice where tiles overlap (same label, same "
        "position); give repeated labels separate ids. Include labelled inputs and outputs. Then run next.py again.")

if not streams.exists() or sum("|" in l for l in streams.read_text().splitlines()) < 3:
    say("STEP 5. Trace the streams from your notes, in the order SKILL.md gives in its step 5. Join lines that leave "
        "one tile and enter the next by their ruler positions. For every stream, both of its ends must be in your "
        "notes; where one is not, zoom.py that place now and add it. Write work/streams.md, one line per unit: "
        "id | in from: ... | out to: ... Then run next.py again.")

if not chart.exists() or "-->" not in chart.read_text():
    say("STEP 6. Write flowsheet.mmd from work/units.md and work/streams.md, as SKILL.md step 6 says. "
        "Then run next.py again.")

report = subprocess.run([sys.executable, here / "check.py", chart], capture_output=True, text=True).stdout
print("STEP 7. The check says:\n" + report)
print("For each unit listed with no line in or out that is not a feed or a product, and each unit missing from the "
      "chart, look again at that place (zoom.py) and fix the chart or confirm. Fix every line it says may not be "
      "valid Mermaid. When nothing is left to fix, you are done.")
