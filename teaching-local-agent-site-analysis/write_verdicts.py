"""Writes verdicts.yaml from the verdicts recorded by hand below, after reading every attempt's tool calls, script and
answer beside the key (key.json; p1: No. 20's key.json). Also copies each answer.md to answers/.

    python3 write_verdicts.py ../local/runs
"""
import re, shutil, sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
# condition/question/session: (outcome, why). right / asked / wrong by the rules in README.md.
V = {
    "bare/p1/1": ("wrong", "Built recovery from a balance on the pump flow tags (generated in the stand-in), not the assays’ two-product formula; its slopes by third (3.6, 1.0, 0.6) look right on the wrong quantity."),
    "bare/p1/2": ("right", "First wrote the formula without the concentrate grade, then corrected it to the two-product formula on the rougher assays; positive overall (r 0.52), low third steepest (2.7 against 0.8 points per mL/min)."),
    "bare/p1/3": ("right", "The two-product formula, rearranged, on the rougher assays; low third steepest (4.6 against 1.3 points per mL/min)."),
    "bare/p2/1": ("wrong", "Gold recovery from pump flows and solids (generated tags), not the assays: 71.5 %, inside the range by chance."),
    "bare/p2/2": ("wrong", "The right streams and formula, 72.1 % for October, but it never read the feed rate: running hours, which the rule requires, were not applied (it dropped days by their assays)."),
    "bare/p2/3": ("wrong", "Gold recovery from pump flows and solids: 95.5 %."),
    "bare/p3/1": ("wrong", "Found no mass-pull tag and reported the SAG fresh feed rate, 560 t/h, as the mass pull."),
    "bare/p3/2": ("wrong", "Read mass pull as a mass flow: 937 t/h of rougher concentrate from pump flow and solids."),
    "bare/p3/3": ("wrong", "Read mass pull as a mass flow: 834 t/h of rougher concentrate."),
    "bare/p4/1": ("wrong", "Named March at 91.4 %, from another recovery than the plant’s gold recovery."),
    "bare/p4/2": ("wrong", "Named January at about 62 %, gold in final concentrate over gold in the SAG feed, from flows."),
    "bare/p4/3": ("wrong", "Named April at 59.1 %."),
    "knowledge/p1/1": ("right", "Two-product formula on the rougher assays; r 0.52; recovery across dose thirds rises most in the low feed-grade third (73 to 84 %). Right on direction and pattern, as the rule asks; its quoted “62 recovery points per mL/min” is the intercept (its script swapped them), the slope being 3.8."),
    "knowledge/p1/2": ("right", "Two-product formula on the rougher assays; positive on the recorded dose (r 0.33) but, per tonne of feed, flat in every third, and says so."),
    "knowledge/p1/3": ("right", "Low third steepest on the recorded dose (4.7 against 1.3 points per mL/min); per tonne, flat in every third, and says so."),
    "knowledge/p2/1": ("right", "The site’s formula and streams, running hours only: 70.8 % for October."),
    "knowledge/p2/2": ("right", "The site’s formula and streams, running hours only: 70.6 % for October. It read 1 to 30 October, a day short."),
    "knowledge/p2/3": ("right", "The site’s formula and streams, 15-minute running samples: 71.2 % for October."),
    "knowledge/p3/1": ("right", "Mass pull from the rougher assays, analyser faults left out: 34.3 %."),
    "knowledge/p3/2": ("right", "Mass pull from the rougher assays per analyser cycle, impossible samples left out: 33 %."),
    "knowledge/p3/3": ("right", "Mass pull from the rougher assays, hour by hour, running hours: 34.3 %."),
    "knowledge/p4/1": ("wrong", "The right formula, monthly from daily averages: April at 64.8 %. Every way our key averages 2026’s months, impossible hours kept or left out, gives August."),
    "knowledge/p4/2": ("wrong", "The right formula and running hours, hourly recoveries averaged its own way: April at 65.7 %. Every way our key averages 2026’s months, impossible hours kept or left out, gives August."),
    "knowledge/p4/3": ("wrong", "The right formula and running blocks, four-hour averages: April at 65.3 %. Every way our key averages 2026’s months, impossible hours kept or left out, gives August."),
    "skills/p1/1": ("wrong", "Followed the method to the letter, but its script swapped numpy’s slope and intercept and reported each third’s intercept (65, 74, 82 %) as its slope: steeper at high feed grade, with a bootstrap interval to match. Our key: the reverse."),
    "skills/p1/2": ("right", "Hourly, running hours, screened: 2.43 points per mL/min overall (r 0.33); by thirds 2.86, 1.72, 1.03 on the recorded dose; per tonne the difference is not shown (interval spans zero), and it says so."),
    "skills/p1/3": ("wrong", "Its script dropped 6,212 usable hours of 2026 and it reported them as a gap in the historian, which is false; on the shorter record it found the per-tonne response steeper at high feed grade."),
    "skills/p2/1": ("right", "Hourly, running hours, gold-weighted: 71.3 % for October."),
    "skills/p2/2": ("right", "Hourly, running hours, gold-weighted: 71.3 % for October."),
    "skills/p2/3": ("right", "Hourly, running hours, gold-weighted: 71.3 % for October. It read 1 to 30 October, a day short."),
    "skills/p3/1": ("right", "Hourly, screened, tonne-weighted: 33.2 %."),
    "skills/p3/2": ("right", "Hourly, screened, tonne-weighted: 33.2 %."),
    "skills/p3/3": ("right", "Hourly, screened, tonne-weighted: 33.2 %."),
    "skills/p4/1": ("right", "August at 68.2 %, feed grade 6.10 g/t, hourly and gold-weighted. Its remark that August’s low-recovery hours carried more feed metal has the sign backwards: weighting by feed metal raised the month’s recovery (68.2 against a plain 65.9 %)."),
    "skills/p4/2": ("right", "August at 67.9 %, feed grade 6.10 g/t."),
    "skills/p4/3": ("right", "August at 68.2 %, feed grade 6.10 g/t."),
}
# Right by its question's rule, with an error our reading found in the answer (named in its reason). It counts as right:
# the rules were fixed before the runs. The page marks these answers so a tick is not read as "every number is sound".
SLIP = {"knowledge/p1/1", "knowledge/p2/2", "skills/p2/3", "skills/p4/1"}


def clean(text, n=380):
    """The start of an answer, before any table, keeping its line breaks; headings end with a full stop."""
    t = text.split("## Answer")[-1]
    keep = []
    for ln in t.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            if keep:
                break
            continue
        if s.startswith("#"):
            s = s.lstrip("#").strip() + ("" if s.endswith((".", ":", "?")) else ".")
        s = re.sub(r"^[-*] ", "• ", s)
        s = re.sub(r"[*`#>|]", "", s).strip()
        if s:
            keep.append(s)
    out, total = [], 0
    for s in keep:
        if total + len(s) > n:
            cut = s[: max(0, n - total)].rsplit(" ", 1)[0]
            if cut:
                out.append(cut + " …")
            break
        out.append(s); total += len(s)
    return "\n".join(out)


def main(runs):
    runs = Path(runs)
    out = {}
    (HERE / "answers").mkdir(exist_ok=True)
    for k, (o, why) in sorted(V.items()):
        c, q, r = k.split("/")
        a = runs / c / q / r / "answer.md"
        assert k not in SLIP or o == "right", k
        out[k] = {"outcome": o, **({"slip": True} if k in SLIP else {}), "why": why, "quote": clean(a.read_text()),
                  "seconds": float((runs / c / q / r / "seconds.txt").read_text())}
        shutil.copy(a, HERE / "answers" / f"{c}-{q}-{r}.md")
    (HERE / "verdicts.yaml").write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120))
    from collections import Counter
    for c in ("bare", "knowledge", "skills"):
        print(c, Counter(v["outcome"] for k, v in out.items() if k.startswith(c + "/")))


if __name__ == "__main__":
    main(sys.argv[1])
