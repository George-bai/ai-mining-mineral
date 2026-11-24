"""The answer key for eval/test-questions.yaml, written from the generator's plant (31 sites x 5 concentrators),
never from search output. Writes eval/key.yaml.

How each question counts (fixed before any scoring):
  one       one expected tag. Hit at k if it is in the top k; also gives the reciprocal rank.
  several   a group (all leach tank pH tags at one concentrator...). Score at k: the share of the group in the top k.
  ambiguous every reading the question could mean. Hit at k if any is in the top k; precision@10 is reported too.
  none      no tag matches (a code from another site's convention, a moving average, an alarm that does not exist).
            Hit at k if any of the named near matches is in the top k; whether the top result is an exact point name
            is reported separately (it should not be).
"""
from pathlib import Path

import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import generator  # noqa: E402

E = "\\\\EXAMPLE-AF\\Operations\\Example Mining\\"
P = generator.build(31, 5)
ATTR = {a["path"]: a for a in P["attributes"]}


def path(rel: str) -> str:
    p = E + rel
    assert p in ATTR, f"not in the plant: {rel}"
    return p


def point(name: str) -> str:
    assert name in P["points"], f"no point {name}"
    return P["points"][name]["linked"] or f"\\\\{P['config']['data_server']}\\{name}"


def where(pred) -> list[str]:
    return sorted(a["path"] for a in P["attributes"] if a["variant"] in ("primary", "status") and pred(a))


def at(site, conc=None):
    return lambda a: f"\\Site {site}\\" in a["path"] and (conc is None or f"\\Concentrator {conc}\\" in a["path"])


KEY = {
    "q01": ("one", [path(r"Site D\Concentrator 2\Grinding\SAG Mill|Motor Power")]),
    "q02": ("one", [path(r"Site AA\Concentrator 1\Crushing\Primary Crusher|Closed Side Setting")]),
    "q03": ("one", [path(r"Site F\Concentrator 3\Crushing\CV-103|Belt Speed")]),
    "q04": ("one", [path(r"Site M\Concentrator 1\Grinding\Cyclone Cluster 2|Feed Pressure")]),
    "q05": ("one", [path(r"Site H\Concentrator 2\Flotation\Cleaner Cell 3|Froth Depth")]),
    "q06": ("one", [path(r"Site AE\Concentrator 1\Tailings\Return Water|Flow")]),
    "q07": ("one", [path(r"Site K\Concentrator 4\Utilities\Main Incomer|Power Factor")]),
    "q08": ("one", [path(r"Site P\Concentrator 2\Leach\Leach Tank 7|Dissolved Oxygen")]),
    "q09": ("one", [path(r"Site J\Concentrator 2\Crushing\CV-101|Belt Weigher Rate")]),
    "q10": ("one", [path(r"Site R\Concentrator 1\Crushing\Primary Crusher|Motor Current")]),
    "q11": ("one", [path(r"Site AB\Concentrator 3\Flotation\Final Tail|Au")]),
    "q12": ("one", [path(r"Site L\Concentrator 1\Grinding\Ball Mill 2|Run Hours")]),
    "q13": ("one", [path(r"Site U\Concentrator 2\Flotation\Frother|Dose Rate")]),
    "q14": ("one", [path(r"Site Y\Concentrator 1\Grinding\SAG Mill|Motor Power")]),
    # code questions: no point has the code given; near matches as named
    "q15": ("none", [point("SA-C1-PT-3104"), point("SA-C1-FT-3105")]),
    "q16": ("none", [path(r"Site B\Concentrator 2\Grinding\Cyclone Cluster 1|Feed Pressure"),
                     path(r"Site B\Concentrator 2\Grinding\Cyclone Cluster 2|Feed Pressure")]),
    "q17": ("none", [path(r"Site C\Concentrator 1\Utilities\Process Water Tank|Level")]),
    "q18": ("none", [path(rf"Site E\Concentrator 3\Leach\Leach Tank {i}|pH") for i in range(1, 9)]),
    "q19": ("ambiguous", where(lambda a: at("B")(a) and a["kind"] == "pressure")),
    # Codex's key check (23 Nov 2026) added the SAG feed water and the three water meters' totalised flows
    "q20": ("ambiguous", where(lambda a: "\\Concentrator 2\\" in a["path"] and (
        (a["path"].split("\\")[-1].split("|")[0] in ("Raw Water", "Process Water", "Return Water")
         and a["name"] in ("Flow", "Totalised Flow"))
        or a["path"].endswith("\\SAG Mill|Feed Water Flow")))),
    "q21": ("ambiguous", where(lambda a: at("N", 1)(a) and a["kind"].startswith("assay")
                               and "Concentrate|" in a["path"])),
    "q22": ("ambiguous", where(lambda a: at("AC")(a) and a["name"] == "Run Status"
                               and any(m in a["path"] for m in ("\\SAG Mill|", "\\Ball Mill 1|", "\\Ball Mill 2|")))),
    "q23": ("several", [path(rf"Site C\Concentrator 1\Leach\Leach Tank {i}|pH") for i in range(1, 9)]),
    "q24": ("several", [path(rf"Site V\Concentrator 2\Flotation\Rougher Cell {i}|Air Flow") for i in range(1, 7)]),
    "q25": ("several", [path(rf"Site G\Concentrator 3\Crushing\CV-10{i}|Run Status") for i in range(1, 5)]),
    "q26": ("several", [path(rf"Site AD\Concentrator 1\Grinding\Ball Mill {i}|Discharge Density") for i in (1, 2)]),
    # variants: none of these exists in the generated plant; near matches are the primary tags
    "q27": ("none", [path(r"Site A\Concentrator 1\Flotation\Final Tail|Au")]),
    "q28": ("none", [path(r"Site T\Concentrator 2\Grinding\SAG Mill|Fresh Feed Rate")]),
    "q29": ("none", [path(r"Site Z\Concentrator 1\Tailings\Tailings Thickener|Rake Torque")]),
    "q30": ("none", [path(r"Site W\Concentrator 3\Utilities\Process Water Tank|Level")]),
}

# the variants really do not exist (checked against the generator, not assumed)
for rel in (r"Site A\Concentrator 1\Flotation\Final Tail|Au QC",):
    assert E + rel not in ATTR, rel
for prim in (KEY["q29"][1][0], KEY["q30"][1][0]):
    assert ATTR[prim]["point"] + ".ALM" not in P["points"], prim

if __name__ == "__main__":
    qs = {q["id"]: q for q in yaml.safe_load((Path(__file__).parent / "test-questions.yaml").read_text())}
    assert set(qs) == set(KEY)
    out = [{"id": k, "question": qs[k]["question"], "type": qs[k]["type"], "counts_as": c, "tags": v}
           for k, (c, v) in KEY.items()]
    (Path(__file__).parent / "key.yaml").write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=200))
    for o in out:
        print(o["id"], o["counts_as"], len(o["tags"]))
