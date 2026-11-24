"""Pick, from the generator's plant, the tag codes and the unhealthy tags the question writer is given, so that the
code and broken-tag questions name things that exist. Seeded; writes material.json beside this file.

    ../../historian-tag-catalogue-for-agents/public/.venv/bin/python make_material.py
"""
import json, random, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "historian-tag-catalogue-for-agents" / "public"))
import generator  # noqa: E402

P = generator.build(31, 5)
R = random.Random(20261124)
pts = P["points"]
place = lambda path: path.split("Example Mining\\")[1].replace("|", " · ")

# point codes a person could have seen on a screen: healthy primary points, some linked to the asset tree, some not
linked = [p for p in pts.values() if p["linked"] and p["health"] == "ok" and not p["digital"]]
spare = [p for p in pts.values() if not p["linked"] and p["health"] == "ok" and not p["digital"]]
codes = [{"point": p["name"], "is": place(p["linked"])} for p in R.sample(linked, 4)]
codes += [{"point": p["name"], "is": p["descriptor"] + " (not in the asset tree)"} for p in R.sample(spare, 2)]

# primary readings whose point is broken, stale, empty or bad: a person asks for them without knowing
bad = []
for a in P["attributes"]:
    if a["variant"] != "primary":
        continue
    h = "broken_ref" if a["broken"] else pts.get(a["point"], {}).get("health", "ok")
    if h != "ok":
        bad.append({"reading": place(a["path"]), "health": h})
picked = []
for h in ("broken_ref", "stale", "no_data", "bad_quality"):
    picked += R.sample([b for b in bad if b["health"] == h], 2)

(HERE / "material.json").write_text(json.dumps({"codes": codes, "unhealthy": picked}, indent=1))
print(json.dumps({"codes": codes, "unhealthy": picked}, indent=1))
