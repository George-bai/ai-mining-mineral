"""Our own answer to the question the assistant was asked, worked from Table 1 of Habibi et al. (2025), Minerals 15(10),
1018, https://doi.org/10.3390/min15101018 (CC BY 4.0). Standard library only.   Run: python3 check.py
The numbers on the article page come from results() below."""

# Table 1: fraction code, mass %, Cu ppm, as printed. Row order as printed: coarsest first.
TABLE = [("CTS+106", 8.6, 2250), ("CTS+75", 7.7, 1864), ("CTS+53", 10.1, 1265), ("CTS+C1", 13.1, 1390),
         ("CTS+C3", 13.8, 775), ("CTS+C5", 5.2, 860), ("CTS-C5", 33.3, 1084)]


def results(missing_ppm=None, part_of=None):
    """Copper carried by each fraction (mass % x ppm). The table's masses add to 91.8 %, and the paper does not say what
    the rest is. Three readings of it: left out (the default: shares are of the reported copper); missing_ppm, one more
    fraction of its own at that grade; part_of, mass that belongs to that fraction, at its grade."""
    mass = sum(m for _, m, _ in TABLE)
    units = {f: m * cu for f, m, cu in TABLE}
    gap = round(100 - mass, 6)
    if missing_ppm is not None:
        units["missing"] = gap * missing_ppm
    if part_of is not None:
        units[part_of] += gap * dict((f, cu) for f, _, cu in TABLE)[part_of]
    total = sum(units.values())
    return {
        "mass_sum": round(mass, 6), "missing_mass": gap,
        "richest": max(TABLE, key=lambda r: r[2])[0],
        "largest": max(units, key=units.get),
        "share": {f: 100 * u / total for f, u in units.items()},
        # grade of the reported fractions together, scaled to their own mass (the 91.8 %)
        "head_reported": sum(m * cu for _, m, cu in TABLE) / mass,
        # the grade of the missing mass, as a fraction of its own, at which it carries as much copper as the largest
        "breakeven_ppm": max(m * cu for _, m, cu in TABLE) / gap,
    }


if __name__ == "__main__":
    r = results()
    print(f"mass sums to {r['mass_sum']} %, {r['missing_mass']} % not reported")
    print(f"richest by grade: {r['richest']}; carries the most copper: {r['largest']}")
    for f, m, cu in sorted(TABLE, key=lambda t: -t[1] * t[2]):
        print(f"  {f:8} {m:5.1f} %  {cu:5} ppm  {m * cu:8.1f} %·ppm  {r['share'][f]:5.1f} % of the reported copper")
    print(f"grade of the reported 91.8 %: {r['head_reported']:.0f} ppm Cu")
    print(f"as a fraction of its own, the missing {r['missing_mass']} % would have to grade {r['breakeven_ppm']:.0f} ppm to match CTS-C5")
    for g in (0, 1084, 1263, 2250, 4402, 4500):
        s = results(g)
        print(f"  a fraction of its own at {g:4} ppm: largest {s['largest']:8}  CTS-C5 {s['share']['CTS-C5']:4.1f} %  CTS+106 {s['share']['CTS+106']:4.1f} %")
    for f in ("CTS+106", "CTS-C5"):
        s = results(part_of=f)
        print(f"  part of {f}: largest {s['largest']:8}  CTS-C5 {s['share']['CTS-C5']:4.1f} %  CTS+106 {s['share']['CTS+106']:4.1f} %")
    # the checks that fail if the table or the arithmetic changes
    assert r["mass_sum"] == 91.8 and r["richest"] == "CTS+106" and r["largest"] == "CTS-C5"
    assert round(r["share"]["CTS-C5"], 1) == 31.1 and round(r["share"]["CTS+106"], 1) == 16.7
    assert round(r["head_reported"]) == 1263 and round(r["breakeven_ppm"]) == 4402
    assert results(4401)["largest"] == "CTS-C5" and results(4403)["largest"] == "missing"
    s = results(part_of="CTS+106")
    assert s["largest"] == "CTS+106" and round(s["share"]["CTS+106"], 1) == 28.1 and round(s["share"]["CTS-C5"], 1) == 26.9
    assert round(results(part_of="CTS-C5")["share"]["CTS-C5"], 1) == 36.0 and round(results(2250)["share"]["CTS-C5"], 1) == 26.9
