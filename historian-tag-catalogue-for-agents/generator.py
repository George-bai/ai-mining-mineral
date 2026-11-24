"""Builds the mock plant from config/plant.yaml: the asset tree (elements, attributes) and the PI points, with
the injected messiness. Deterministic: the same sites and concentrators give the same plant every time.

    python generator.py --sites 25 --concentrators 5      # prints the counts
"""
import argparse, hashlib, random, re, string
from pathlib import Path

import yaml

CONFIG = Path(__file__).parent / "config" / "plant.yaml"


def seed_of(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big")


def site_letters(i: int) -> str:
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = string.ascii_uppercase[r] + s
    return s


def build(sites: int = 3, concentrators: int = 1, config: Path = CONFIG) -> dict:
    cfg = yaml.safe_load(config.read_text())
    styles, unit_styles, faults = list(cfg["naming_styles"].items()), cfg["unit_styles"], cfg["faults"]
    root = f"\\\\{cfg['asset_server']}\\{cfg['asset_database']}"
    ent = f"{root}\\{cfg['enterprise']}"
    elements = [dict(path=ent, name=cfg["enterprise"], template="Enterprise", parent=None, description="")]
    attributes, points = [], {}

    def add_point(name, descriptor, unit, kind, code, linked, digital=False, health="ok"):
        points[name] = dict(name=name, descriptor=descriptor, unit=unit, kind=kind, code=code, linked=linked,
                            digital=digital, health=health)

    for si in range(sites):
        letters = site_letters(si)
        site_name, site_code = f"Site {letters}", f"S{letters}"
        style_name, style = styles[si % len(styles)]
        units = unit_styles[si % len(unit_styles)]
        spath = f"{ent}\\{site_name}"
        elements.append(dict(path=spath, name=site_name, template="Site", parent=ent, description=""))
        for ci in range(1, concentrators + 1):
            conc_name, conc_code = f"Concentrator {ci}", f"C{ci}"
            cpath = f"{spath}\\{conc_name}"
            elements.append(dict(path=cpath, name=conc_name, template="Concentrator", parent=spath, description=""))
            eq_count = {}
            for area_num, area_name, area_abbrev, equipment in cfg["concentrator"]:
                apath = f"{cpath}\\{area_name}"
                elements.append(dict(path=apath, name=area_name, template="Area", parent=cpath, description=f"Area {area_num}"))
                seq = 0
                for template, *names in equipment:
                    t = cfg["templates"][template]
                    for eq_name in names:
                        eq_count[t["abbrev"]] = eq_count.get(t["abbrev"], 0) + 1
                        eq_abbrev = f"{t['abbrev']}{eq_count[t['abbrev']]}"
                        epath = f"{apath}\\{eq_name}"
                        elements.append(dict(path=epath, name=eq_name, template=template, parent=apath, description=template))
                        for attr_name, attr_abbrev, kind, unit, code in t["attributes"]:
                            seq += 1
                            unit = units.get(unit, unit)
                            fields = dict(site=site_code, conc=conc_code, code=code, loop=f"{area_num // 100}{seq:03d}",
                                          loop_short=f"{seq:03d}", site_name=f"SITE{letters}", conc_name=f"CONC{ci}",
                                          area_abbrev=area_abbrev, area_num=area_num // 100, eq_abbrev=eq_abbrev,
                                          attr_abbrev=attr_abbrev)
                            point = style["point"].format(**fields)
                            if style_name == "legacy":
                                point = f"{site_code}{ci}:{point}"
                            desc = {"full": f"{conc_name} {eq_name} {attr_name}", "abbrev": f"{eq_abbrev} {attr_abbrev}",
                                    "none": ""}[style["descriptor"]]
                            digital = kind == "status"
                            apath_attr = f"{epath}|{attr_name}"
                            rng = random.Random(seed_of(point))
                            r = rng.random
                            health = "ok"
                            ref = point
                            if not digital:
                                x = r()
                                edges = [("broken_ref", faults["broken_ref"]), ("stale", faults["stale"]),
                                         ("no_data", faults["no_data"]), ("bad_quality", faults["bad_quality"])]
                                acc = 0.0
                                for h, f in edges:
                                    acc += f
                                    if x < acc:
                                        health = h
                                        break
                            if health == "broken_ref":
                                ref = point + "_OLD"   # the attribute still points at a point that was renamed
                            else:
                                add_point(point, desc, unit, kind, code, apath_attr, digital, health)
                            attributes.append(dict(path=apath_attr, element=epath, name=attr_name, unit=unit, kind=kind,
                                                   code=code, point=ref, variant="primary" if not digital else "status",
                                                   broken=health == "broken_ref"))
                            if digital:
                                continue
                            for variant, suffix in (("qc", "QC"), ("calc", "Calc")):
                                if r() < faults[f"{variant}_variant"]:
                                    vp = f"{point}.{suffix.upper()}"
                                    add_point(vp, f"{desc} {suffix}".strip(), unit, kind, code, f"{apath_attr} {suffix}")
                                    attributes.append(dict(path=f"{apath_attr} {suffix}", element=epath,
                                                           name=f"{attr_name} {suffix}", unit=unit, kind=kind, code=code,
                                                           point=vp, variant=variant, broken=False))
                            if r() < faults["alarm_point"]:
                                add_point(f"{point}.ALM", f"{desc} alarm".strip(), "", "alarm", code, None, digital=True)
                            if r() < faults["unlinked"]:
                                # a spare or old loop on the same equipment: in the archive, not in the asset tree
                                old = style["point"].format(**{**fields, "loop": f"{area_num // 100}{900 + seq:03d}",
                                                               "loop_short": f"{900 + seq:03d}",
                                                               "attr_abbrev": attr_abbrev + "2"})
                                if style_name == "legacy":
                                    old = f"{site_code}{ci}:{old}"
                                add_point(old, (desc + " spare").strip() if desc else "", unit, kind, code, None,
                                          health=rng.choice(["ok", "stale", "no_data"]))
    return dict(root=root, enterprise=ent, config=cfg, elements=elements, attributes=attributes, points=points)


def counts(plant: dict) -> dict:
    a, p = plant["attributes"], plant["points"].values()
    return {
        "elements": len(plant["elements"]),
        "attributes": len(a),
        "points": len(plant["points"]),
        "broken_ref": sum(x["broken"] for x in a),
        "variants_qc": sum(x["variant"] == "qc" for x in a),
        "variants_calc": sum(x["variant"] == "calc" for x in a),
        "alarm_points": sum(x["kind"] == "alarm" for x in p),
        "unlinked_points": sum(x["linked"] is None for x in p),
        "stale": sum(x["health"] == "stale" for x in p),
        "no_data": sum(x["health"] == "no_data" for x in p),
        "bad_quality": sum(x["health"] == "bad_quality" for x in p),
        # the catalogue's unit of search: every attribute plus every point not linked to one
        "tags": len(a) + sum(x["linked"] is None for x in p),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", type=int, default=3)
    ap.add_argument("--concentrators", type=int, default=1)
    args = ap.parse_args()
    for k, v in counts(build(args.sites, args.concentrators)).items():
        print(f"{k:16} {v:>8,}")
