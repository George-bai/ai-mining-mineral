"""No. 3's answer key, written from the generator's plant and, for the "across" questions, from the historian's own
summaries read through the same MCP tool code the agent uses. Never from an agent's output. Writes key.json.

    (mock running on :8711)  ../../historian-tag-catalogue-for-agents/public/.venv/bin/python make_key.py

Counting rules (fixed before any run, plan.md):
  read, compare, code  the agent reads every tag listed (get_timeseries or get_current_values on it)
  across               it reads the group and names the winner listed
  ambiguous            it asks which one, or lists at least two of the valid readings, instead of silently picking one
  any tag listed as unhealthy (in "flag") must be called not usable, with no value from it given as a reading
  unhealthy            it says the tag is not usable (the health listed) and gives no value from it as a reading
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).parent
PUB = HERE.parent.parent / "historian-tag-catalogue-for-agents" / "public"
sys.path.insert(0, str(PUB))
import generator  # noqa: E402

P = generator.build(31, 5)
ATTR = {a["path"]: a for a in P["attributes"]}
E = "\\\\EXAMPLE-AF\\Operations\\Example Mining\\"


def t(site, conc, rel):
    p = f"{E}Site {site}\\Concentrator {conc}\\{rel}"
    assert p in ATTR, p
    return p


def point(name):
    assert name in P["points"], name
    return f"\\\\EXAMPLE-PI\\{name}" if not P["points"][name]["linked"] else P["points"][name]["linked"]


AREAS = ("Crushing", "Grinding", "Flotation", "Leach")
KEY = {
    "t01": ("read", [t("B", 4, r"Leach\Leach Tank 8|pH")]),
    "t02": ("read", [t("AA", 2, r"Utilities\Main Incomer|Power Factor")]),
    "t03": ("read", [t("D", 1, r"Grinding\SAG Mill|Fresh Feed Rate")]),
    "t04": ("read", [t("U", 5, r"Tailings\Return Water|Flow")]),
    "t05": ("compare", [t("H", 3, r"Crushing\CV-103|Motor Current"), t("H", 3, r"Crushing\CV-103|Belt Weigher Rate")]),
    "t06": ("compare", [t("AC", 4, r"Grinding\Cyclone Cluster 2|Feed Pressure"), t("AC", 4, r"Grinding\Cyclone Cluster 2|Cyclones Open")]),
    "t07": ("compare", [t("F", 2, r"Flotation\Frother|Dose Rate"), t("F", 2, r"Flotation\Rougher Cell 1|Froth Depth")]),
    "t08": ("compare", [t("M", 5, r"Tailings\Tailings Thickener|Bed Level"), t("M", 5, r"Tailings\Tailings Thickener|Rake Torque")]),
    "t09": ("across", [t("T", 1, rf"Crushing\CV-10{i}|Motor Current") for i in range(1, 5)]),
    "t10": ("across", [t("W", 3, rf"Flotation\Rougher Cell {i}|Froth Depth") for i in range(1, 7)]),
    "t11": ("across", [t("L", 2, rf"Leach\Leach Tank {i}|Dissolved Oxygen") for i in range(1, 9)]),
    "t12": ("across", [t("O", 4, rf"Utilities\{a} Supply|Energy") for a in AREAS]),
    "t13": ("ambiguous", [t("J", c, rf"Grinding\{m}|Motor Power") for c in range(1, 6) for m in ("SAG Mill", "Ball Mill 1", "Ball Mill 2")]
            + [t("J", c, r"Utilities\Grinding Supply|Active Power") for c in range(1, 6)]),
    "t14": ("ambiguous", [t("N", 2, rf"Flotation\{s}|Au") for s in ("Rougher Feed", "Rougher Concentrate", "Rougher Tail",
                                                                    "Cleaner Concentrate", "Final Concentrate", "Final Tail")]),
    "t15": ("ambiguous", [a for a in ATTR if a.startswith(f"{E}Site Z\\") and ATTR[a]["kind"] == "flow"
                          and ATTR[a]["variant"] == "primary" and "Water" in a]),
    "t16": ("ambiguous", [a for a in ATTR if a.startswith(f"{E}Site AB\\") and ATTR[a]["variant"] == "primary"
                          and a.endswith(("|Level", "|Tank Level"))]),
    "t17": ("code", [point("SI-C3-AT-4023")]),
    "t18": ("code", [point("SITEC.CONC2.CRU.CV1.SPD")]),
    "t19": ("code", [point("SITEG.CONC5.CRU.CV4.RATE.QC")]),
    "t20": ("code", [point("SVC5_PP7_FLOW2")]),
    "t21": ("unhealthy", [t("X", 3, r"Flotation\Final Tail|Pb")]),
    "t22": ("unhealthy", [t("I", 2, r"Leach\Leach Tank 5|Agitator Power")]),
    "t23": ("unhealthy", [t("AE", 1, r"Flotation\Cleaner Cell 1|Agitator Power")]),
    "t24": ("unhealthy", [t("R", 5, r"Grinding\SAG Mill|Bearing Pressure")]),
}
# what the agent should find for each "across" question: (tool arguments, pick max or min)
ACROSS = {"t09": (dict(), "max", "current"), "t10": (dict(start="*-7d", end="*", interval="7d"), "max", "summary"),
          "t11": (dict(start="*-30d", end="*", interval="30d"), "min", "summary"),
          "t12": (dict(start="y", end="t", interval="1d"), "max", "energy")}


def main():
    import catalog, mcp_server as M  # noqa: E402  (reads the catalogue and the running mock)
    con = catalog.connect(str(M.CATALOG))
    ids = {r[1]: r[0] for r in con.execute("SELECT id, path FROM tags")}
    health = {r[0]: r[1] for r in con.execute("SELECT path, health FROM tags")}
    qs = {q["id"]: q for q in __import__("yaml").safe_load((HERE / "questions.yaml").read_text())}
    assert set(qs) == set(KEY)
    out = []
    for k, (typ, tags) in KEY.items():
        assert qs[k]["type"] == typ, k
        row = {"id": k, "type": typ, "question": qs[k]["question"], "tags": tags,
               "points": [P["points"].get(ATTR[p]["point"], {}).get("name", ATTR[p]["point"]) if p in ATTR else p.split("\\")[-1] for p in tags],
               "health": [health.get(p) for p in tags]}
        if typ in ("read", "compare", "code", "across"):
            row["flag"] = [p for p, h in zip(tags, row["health"]) if h != "ok"]  # an unhealthy tag the question happens to need: it must be flagged, as for "unhealthy"
        if typ == "unhealthy":
            assert row["health"][0] != "ok", k
        if k in ACROSS:
            args, pick, how = ACROSS[k]
            tid = [str(ids[p]) for p in tags]
            vals = {}
            if how == "current":
                for v in M.get_current_values(ids=tid):
                    vals[v["path"]] = v.get("value")
            else:
                r = M.get_timeseries(ids=tid, mode="summary", summaries=["Average"], **args)
                for s in r["tags"]:
                    vals[s["path"]] = s["mean"]
                if how == "energy":  # a counter: what it clocked up is last minus first; read both, keep both
                    r2 = M.get_timeseries(ids=tid, mode="interpolated", start="y", end="t", interval="1d")
                    csvp = Path(r2["file"]).read_text().splitlines()
                    head = csvp[0].split(",")
                    first, last = csvp[1].split(","), csvp[-1].split(",")
                    by_id = {p: str(ids[p]) for p in tags}
                    num = lambda r, p: float(r[head.index(f"{by_id[p]}|Value")] or "nan")
                    row["energy_counter"] = {p: num(last, p) - num(first, p) for p in tags}
                    # the same meters' active power, for an agent that reads power where a counter is blank
                    pw = [p.replace("|Energy", "|Active Power") for p in tags]
                    r3 = M.get_timeseries(ids=[str(ids[p]) for p in pw], mode="summary", start="y", end="t", interval="1d")
                    row["active_power_mean"] = {s["path"]: s["mean"] for s in r3["tags"]}
            ok = {p: v for p, v in vals.items() if v is not None and v == v}
            win = (max if pick == "max" else min)(ok, key=ok.get)
            row["values"], row["winner"] = vals, win
            if "energy_counter" in row:
                c = {p: v for p, v in row["energy_counter"].items() if v == v}
                row["winner_by_counter"] = max(c, key=c.get)
                row["winner_by_power"] = max(row["active_power_mean"], key=lambda p: row["active_power_mean"][p] or 0)
        out.append(row)
    # the full key (with the summary values, from the private plant set's averages) stays local; public keeps winners
    (HERE.parent / "local").mkdir(exist_ok=True)
    (HERE.parent / "local" / "key-full.json").write_text(json.dumps(out, indent=1))
    pub = [{k: v for k, v in r.items() if k not in ("values", "energy_counter", "active_power_mean")} for r in out]
    (HERE / "key.json").write_text(json.dumps(pub, indent=1))
    for r in out:
        print(r["id"], r["type"], len(r["tags"]), r["health"][:1], r.get("winner", "").split("Mining\\")[-1],
              r.get("winner_by_counter", "").split("Mining\\")[-1])


if __name__ == "__main__":
    main()
