"""Writes verdicts.yaml from the verdicts recorded by hand below, after reading every attempt's tool calls and answer
beside the key (../local/sheet-r1.md). The page quotes the start of six answers; those quotes are cut from the
answers here, markdown removed. Also copies each attempt's answer.md to answers/ and attempts.json beside it.

    python3 write_verdicts.py ../local/runs/r1
"""
import json, re, shutil, sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
WHY = {  # the reason a pass passed, by question, as read (every repeat the same unless noted in NOTES)
    "t01": "Read Leach Tank 8 pH at Site B, Concentrator 4 and gave its latest value with the tag.",
    "t02": "Read the main incomer’s power factor at Site AA, Concentrator 2 around noon on 22 Nov.",
    "t03": "Read the SAG fresh feed rate at Site D, Concentrator 1 for 22 Nov and saved a chart.",
    "t04": "Read the tailings return water flow at Site U, Concentrator 5 for 30 days and saved a chart.",
    "t05": "Read both CV-103 tags and said the motor current tag is stale, with no data for the day; charted the rate.",
    "t06": "Read both cluster 2 tags and said the feed pressure tag is stale, with no values last week; charted the count.",
    "t07": "Read the frother dose rate and rougher cell 1 froth depth since 12 Nov and charted them together.",
    "t08": "Read the thickener bed level and rake torque for the last shift and charted them together.",
    "t09": "Read all four belts’ motor currents and named CV-102, the key’s winner.",
    "t10": "Read all six roughers’ froth depth for the week and named cell 6, the key’s winner (cell 4 within 1 mm).",
    "t11": "Read all eight tanks’ dissolved oxygen for 30 days and named tank 5, the key’s winner.",
    "t12": "Said grinding’s energy counter has no data and worked out grinding’s energy from its power tag: grinding the most.",
    "t13": "Set out several mill power readings across the five concentrators instead of picking one, and flagged the broken one.",
    "t14": "Listed all six gold analyser streams for the day instead of picking one.",
    "t15": "Listed the raw water flow of each concentrator and flagged the dead one.",
    "t16": "Listed the process water tank level of each concentrator over the weekend.",
    "t17": "Found the point by its code and read it at noon on 22 Nov.",
    "t18": "Found the point by its code and charted the last shift.",
    "t19": "Found the QC point by its code and read it, as asked.",
    "t20": "Found the spare point outside the asset tree by its code and read it.",
    "t21": "Said the final tail Pb tag is broken and offered the rougher tail Pb as an indication only.",
    "t22": "Said the leach tank 5 agitator power tag is broken; gave no number for it.",
    "t23": "Said the agitator power tag is stale and gave its last value as of 19 Nov, not as a live reading.",
    "t24": "Said the primary bearing pressure tag is stale with no values in the window and used its healthy Calc copy instead.",
}
NOTES = {  # anything a repeat did differently, as read
    "t12/3": ("Named flotation “by far the most” among the readable counters and said grinding’s counter has no data, "
              "pointing to the main incomer. A pass by the rule fixed before the run (the key’s winner among readable counters, "
              "the dead tag called out), but misleading: grinding’s power tag shows about three times flotation’s energy."),
    "t15/2": "Estimated the dead concentrator’s flow from its totaliser, labelled as an estimate.",
    "t22/2": "Showed the other tanks’ agitator power instead.",
    "t13/1": ("Set out several mill power readings across the five concentrators instead of picking one, and flagged the broken one. "
              "With the historian’s clock at midnight, it took 22 Nov as “this morning” without saying so; the other two sessions said why."),
    "t14/3": "Led with the final concentrate grade, then listed all six streams and asked whether the feed grade was meant.",
}
FAILS = {  # by the letter of the rule "a key tag marked unhealthy must be called out" (README, Rules), applied after Codex's check
    "t16/1": "Listed the five process water tank levels but never mentioned the stale collector tank level and the empty cyanide tank level among the tank levels it could mean.",
    "t16/2": "Same: the stale and empty reagent tank levels not mentioned.",
    "t16/3": "Same: the stale and empty reagent tank levels not mentioned.",
    "t13/3": "Listed each concentrator’s grinding supply power, but said “no tags were unusable” while Concentrator 1’s Ball Mill 2 power tag is broken.",
}
TOOLMEAN = {  # found 24 Nov 2026: the answer quotes the mean No. 18's get_timeseries returned, which mixed summary columns
    "t03/1": "Its daily mean of 339.8 t/h is the tool’s, which averaged the count, minimum and maximum in with the hourly averages; the hourly averages give 446.5.",
    "t04/1": "Its mean of 588.6 m³/h is the tool’s mixed mean; the daily averages give 624.3.",
    "t10/2": "Its froth depth means (333.8; about 455 for cells 2 to 6) are the tool’s mixed means; the averages give 314.3 and about 517.",
    "t11/2": "Its dissolved oxygen means are the tool’s mixed means, 1 to 8 % above the averages (tank 5: 3.98 against 3.70).",
    "t11/3": "Its dissolved oxygen means are the tool’s mixed means, 1 to 8 % above the averages (tank 5: 3.98 against 3.70).",
    "t19/1": "Its mean of 330.0 t/h is the tool’s mixed mean; the averages give 379.5.",
    "t19/3": "Its mean of 314.7 t/h is the tool’s mixed mean; the averages give 379.5.",
}


def clean(t, n=420):
    t = t.replace("\\|", "|").replace("|", " · ")
    t = re.sub(r"[*`#>]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + " …"


def main(run):
    run = Path(run)
    att = json.loads((run / "attempts.json").read_text())
    out = {}
    for k in sorted(att):
        q = k.split("/")[0]
        out[k] = {"pass": k not in FAILS, "why": " ".join(filter(None, [FAILS.get(k) or NOTES.get(k) or WHY[q], TOOLMEAN.get(k)])), "quote": clean(att[k]["answer"])}
    (HERE / "verdicts.yaml").write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120))
    shutil.copy(run / "attempts.json", HERE / "attempts.json")
    (HERE / "answers").mkdir(exist_ok=True)
    for k in att:
        q, r = k.split("/")
        shutil.copy(run / q / r / "answer.md", HERE / "answers" / f"{q}-{r}.md")
    print(len(out), sum(v["pass"] for v in out.values()))


if __name__ == "__main__":
    main(sys.argv[1])
