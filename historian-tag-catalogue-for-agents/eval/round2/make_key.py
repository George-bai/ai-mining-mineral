"""Round 2's answer key, written from the generator's plant (31 sites x 5 concentrators), never from search output.
Counting rules as in round 1 (../round1/make_key.py). Writes key.yaml beside this file.

Round 2's "variant" questions ask for a checked or calculated reading (an average while running, a spike checked
against its neighbours). The agent does the calculation; the tags it needs exist, so they count as one tag or a
group. The code questions name tags in formats no site uses, so they count as "none" with named near matches; that
no point carries those codes is checked below.
"""
import re, sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent))
import generator  # noqa: E402

E = "\\\\EXAMPLE-AF\\Operations\\Example Mining\\"
P = generator.build(31, 5)
ATTR = {a["path"]: a for a in P["attributes"]}


def t(site, conc, rel):
    p = f"{E}Site {site}\\Concentrator {conc}\\{rel}"
    assert p in ATTR, f"not in the plant: {p}"
    return p


def every(site, concs, rels):
    return [t(site, c, r) for c in concs for r in rels]


ALL = range(1, 6)
LEACH_PH = [f"Leach\\Leach Tank {i}|pH" for i in range(1, 9)]
ASSAYS = ("Au", "Ag", "Pb", "S")

KEY = {
    "q01": ("one", [t("A", 2, r"Crushing\Primary Crusher|Closed Side Setting")]),
    "q02": ("one", [t("M", 5, r"Crushing\CV-104|Belt Speed")]),
    "q03": ("one", [t("AB", 1, r"Grinding\SAG Mill|Fresh Feed Rate")]),
    "q04": ("several", [t("D", 4, r"Grinding\Ball Mill 2|Discharge Density"),  # Codex key check: the stop time too
                        t("D", 4, r"Grinding\Ball Mill 2|Run Status")]),
    "q05": ("one", [t("P", 3, r"Grinding\Cyclone Cluster 1|Cyclones Open")]),
    "q06": ("one", [t("V", 2, r"Flotation\Rougher Cell 6|Air Flow")]),
    "q07": ("one", [t("AE", 5, r"Flotation\Final Concentrate|Ag")]),
    "q08": ("one", [t("G", 1, r"Flotation\Frother|Tank Level")]),
    "q09": ("one", [t("W", 4, r"Leach\Leach Tank 3|Dissolved Oxygen")]),
    "q10": ("one", [t("R", 5, r"Leach\Leach Tank 8|Free Cyanide")]),
    "q11": ("one", [t("E", 3, r"Tailings\Tailings Thickener|Rake Torque")]),
    "q12": ("one", [t("AC", 1, r"Tailings\Return Water|Flow")]),
    "q13": ("one", [t("H", 4, r"Utilities\Grinding Supply|Power Factor")]),
    "q14": ("one", [t("T", 2, r"Utilities\Process Water Tank|Level")]),
    "q15": ("one", [t("Y", 3, r"Flotation\Recleaner Cell 2|Agitator Power")]),
    "q16": ("one", [t("K", 5, r"Utilities\Raw Water|Flow")]),
    "q17": ("one", [t("B", 3, r"Crushing\Primary Crusher|Closed Side Setting")]),
    "q18": ("one", [t("S", 1, r"Crushing\CV-102|Belt Weigher Rate")]),
    "q19": ("one", [t("F", 4, r"Grinding\Ball Mill 1|Run Hours")]),
    "q20": ("one", [t("Z", 2, r"Grinding\SAG Mill|Feed Water Flow")]),
    "q21": ("one", [t("L", 5, r"Flotation\Cleaner Cell 1|Froth Depth")]),
    "q22": ("one", [t("X", 3, r"Flotation\Final Tail|Au")]),
    "q23": ("one", [t("AA", 2, r"Flotation\Collector|Pump Run Status")]),
    "q24": ("one", [t("U", 4, r"Leach\Leach Tank 6|Dissolved Oxygen")]),
    "q25": ("one", [t("N", 1, r"Tailings\Tailings Thickener|Underflow Density")]),
    "q26": ("one", [t("AD", 5, r"Tailings\Tailings Thickener|Flocculant Dose")]),
    "q27": ("one", [t("C", 2, r"Utilities\Process Water Tank|Level")]),
    "q28": ("one", [t("Q", 3, r"Utilities\Main Incomer|Active Power")]),
    "q29": ("none", [t("I", 5, r"Crushing\CV-103|Motor Current")]),
    "q30": ("none", [t("J", 2, r"Grinding\SAG Mill|Mill Speed")]),
    "q31": ("none", [t("O", 4, r"Grinding\Cyclone Cluster 2|Feed Pressure")]),
    "q32": ("none", [t("AB", 3, r"Flotation\Rougher Cell 4|Air Flow")]),
    "q33": ("none", [t("E", 1, r"Flotation\Final Tail|Au")]),
    "q34": ("none", [t("V", 5, r"Leach\Leach Tank 7|pH")]),
    "q35": ("none", [t("AA", 4, r"Tailings\Tailings Thickener|Bed Level")]),
    "q36": ("none", [t("M", 2, r"Utilities\Main Incomer|Energy")]),
    "q37": ("ambiguous", every("A", [3], [r"Grinding\SAG Mill|Motor Power", r"Grinding\Ball Mill 1|Motor Power",
                                         r"Grinding\Ball Mill 2|Motor Power", r"Utilities\Grinding Supply|Active Power"])),
    "q38": ("ambiguous", every("Q", [4], [rf"Grinding\Cyclone Cluster {i}|{a}" for i in (1, 2)
                                         for a in ("Feed Density", "Overflow Density")])),
    "q39": ("ambiguous", every("N", ALL, [rf"Flotation\Rougher Cell {i}|Air Flow" for i in range(1, 7)])),
    "q40": ("ambiguous", every("X", [2], [rf"Flotation\{s}|{a}" for s in ("Rougher Tail", "Final Tail")
                                         for a in ASSAYS + ("Solids",)])),  # Codex key check: solids too
    "q41": ("ambiguous", every("AA", [3], [rf"{area}\{r}|Pump Run Status" for area, rs in
                                          (("Flotation", ("Collector", "Frother", "Depressant", "Activator")),
                                           ("Leach", ("Cyanide", "Lime"))) for r in rs])),
    "q42": ("ambiguous", every("U", [5], LEACH_PH)),
    "q43": ("ambiguous", every("G", [4], [rf"Crushing\CV-10{i}|Run Status" for i in range(1, 5)])),
    "q44": ("ambiguous", every("Y", ALL, [r"Tailings\Tailings Thickener|Bed Level"])),
    "q45": ("several", every("C", [1], [rf"Crushing\CV-10{i}|Belt Weigher Rate" for i in range(1, 5)])),
    "q46": ("several", every("P", [5], [rf"Grinding\Ball Mill {i}|Run Hours" for i in (1, 2)])),
    "q47": ("several", every("AE", [2], [rf"Grinding\Cyclone Cluster {i}|Feed Pressure" for i in (1, 2)])),
    "q48": ("several", every("H", [3], [rf"Flotation\Rougher Cell {i}|Froth Depth" for i in range(1, 7)])),
    "q49": ("several", every("R", [1], [rf"Flotation\{r}|Tank Level" for r in ("Collector", "Frother", "Depressant", "Activator")])),
    "q50": ("several", every("S", [4], LEACH_PH)),
    "q51": ("several", every("D", [2], [rf"Utilities\{a} Supply|Active Power" for a in ("Crushing", "Grinding", "Flotation", "Leach")])),
    "q52": ("several", every("W", [5], [rf"Flotation\Scavenger Cell {i}|Agitator Power" for i in (1, 2, 3)])),
    "q53": ("several", [t("J", 2, r"Grinding\SAG Mill|Fresh Feed Rate"),  # Codex key check: the running time too
                        t("J", 2, r"Grinding\SAG Mill|Run Status")]),
    "q54": ("several", every("AC", [1], [r"Crushing\CV-104|Belt Weigher Rate", r"Crushing\CV-104|Belt Speed",
                                         r"Crushing\CV-104|Motor Current"])),
    "q55": ("one", [t("O", 3, r"Leach\Leach Tank 7|pH")]),
    "q56": ("one", [t("K", 5, r"Utilities\Flotation Supply|Energy")]),
    "q57": ("one", [t("AD", 4, r"Tailings\Tailings Thickener|Rake Torque")]),
    "q58": ("one", [t("I", 2, r"Flotation\Rougher Feed|Au")]),
    "q59": ("one", [t("F", 3, r"Utilities\Main Incomer|Active Power")]),
    "q60": ("several", every("Z", [4], [r"Crushing\CV-101|Run Status", r"Crushing\CV-101|Belt Weigher Rate"])),
}

CODES = {"q29": "CV103-II", "q30": "SAG01-SI", "q31": "CY02-PIT", "q32": "RGH04-FIT-AIR", "q33": "AIT-FINALTAIL-AU",
         "q34": "LT07-AIT-PH", "q35": "TH01-LIT", "q36": "INC01-KWH"}
for q, code in CODES.items():  # no point carries these codes, in any site's convention
    assert not [n for n in P["points"] if code.lower() in n.lower()], code

if __name__ == "__main__":
    qs = {q["id"]: q for q in yaml.safe_load((HERE / "test-questions.yaml").read_text())}
    assert set(qs) == set(KEY), set(qs) ^ set(KEY)
    for k, code in CODES.items():
        assert code in qs[k]["question"], k
    out = [{"id": k, "question": qs[k]["question"], "type": qs[k]["type"], "counts_as": c, "tags": v}
           for k, (c, v) in KEY.items()]
    (HERE / "key.yaml").write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=200))
    from collections import Counter
    print(Counter(c for c, _ in KEY.values()), sum(len(v) for _, v in KEY.values()), "tags")
