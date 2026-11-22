#!/usr/bin/env python3
"""What a filed 1SD does to a QAQC control chart: the share of a lab's results on a reference material that fall
outside ±3SD of the database's numbers, for a lab whose results scatter normally by the certificate's 1SD around
its own bias. An illustration under that assumption, not a measurement. Standard library only.
Run it to print the article's table:  python3 control_chart.py"""
from math import erf, sqrt

PHI = lambda z: 0.5 * (1 + erf(z / sqrt(2)))


def fails(mu, sd_lab, mu_db, sd_db, bias, k=3):
    """Share of results outside mu_db ± k·sd_db, for results scattering by sd_lab around mu × (1 + bias)."""
    m = mu * (1 + bias)
    return PHI((mu_db - k * sd_db - m) / sd_lab) + 1 - PHI((mu_db + k * sd_db - m) / sd_lab)


# (standard, unit, certified value, certificate's 1SD, filed 1SD, who filed it)
CASES = {"tight": ("SE147 · gold, fire assay", "ppm", 0.623, 0.015, 0.005, "Model, fields defined"),
         "wide": ("CDN-CM-54 · copper, four-acid", "%", 0.356, 0.0075, 0.015, "Model, names only"),
         "never": ("OREAS 232b · gold, fire assay", "ppm", 0.946, 0.037, 0.933, "Rules")}

if __name__ == "__main__":
    assert abs(fails(1, 1, 1, 1, 0) - 0.0027) < 1e-4          # the ±3SD rule fails 0.27 % of a sound lab's results
    for t, u, mu, sd, fsd, who in CASES.values():
        print(f"{t}: sound lab {fails(mu, sd, mu, sd, 0):.1%} → {fails(mu, sd, mu, fsd, 0):.1%}; "
              f"10 % high {fails(mu, sd, mu, sd, .1):.0%} → {fails(mu, sd, mu, fsd, .1):.0%} ({who}, 1SD {fsd} {u})")
