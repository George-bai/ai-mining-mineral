"""Builds what SAG-Wiki searches for each company (fixed after the run; index_as_run.py is the builder the run used): its own earlier work orders, the 3,200 notes of MaintNorm's train
split that No. 13's glossary was built from, each with what MaintNorm's annotator says it means.

    python3 index.py <maintnorm>/data <out folder>

Writes <out>/<A|B|C>/notes.md: one heading per note (the note as typed) and one line under it, "Means: ...", the
annotator's reading with the masked asset numbers, numbers and dates put back as typed. No test or val note is read.
Standard library only.
"""
import collections, re, sys
from pathlib import Path
from prepare import COMPANIES, read, MASK


ID = re.compile(r"(?<![A-Za-z])[A-Za-z]{1,3}\d+")   # an asset number as typed: XH531, AI9714, #GS690


CAPTURE = {"num": r"(\d+(?:\.\d+)?)", "date": r"(\d[\d/.\-]*\d|\d)", "id": "(.+?)", "sensitive": "(.+?)"}


def fill(raw, norm):
    """A reading with masks inside it, filled from the typed token. The reading's own words are lined up with the
    token (spaces and case ignored) and each mask takes the text between them, a number or date only digits:
    'engineV1' with 'engine <id>' gives 'engine V1', '7897-3Week' with '<id> - <num> week' gives '7897 - 3 week',
    'KD208-24/04/10' with '<id> - <date>' gives 'KD208 - 24/04/10'. Where they cannot be lined up, the run's rule
    (index_as_run.py) applies: <id> the typed asset number, <num> and <date> one run of digits each, <sensitive> the
    typed name; a mask with nothing left to fill it stays as the mask, unresolved."""
    parts = re.split(r"(<(?:id|num|date|sensitive)>)", norm)
    pattern = "".join(CAPTURE[p[1:-1]] if MASK.fullmatch(p) else re.escape(p.replace(" ", "")) for p in parts)
    m = re.fullmatch(pattern, raw.replace(" ", ""), re.I)
    if m:
        found = iter(m.groups())
        def take(mask):
            text = next(found)
            run = re.search(r"[A-Z]{1,3}\d+[A-Za-z0-9]*$", text) if mask == "<id>" else None
            # a typo run into the asset number ('driverriveTR37b'): the number is the capitalised run at the end
            return run[0] if run and text[:run.start()].isalpha() and text[:run.start()].islower() else text
        return "".join(take(p) if MASK.fullmatch(p) else p for p in parts)
    words = set(re.findall(r"[a-z]+", MASK.sub(" ", norm.lower())))
    ids = ID.findall(raw) or re.findall(r"\d+", raw) or [w for w in re.findall(r"[A-Za-z]+", raw) if w.lower() not in words]
    nums, names = re.findall(r"\d+", raw), re.findall(r"[A-Za-z]+", raw)
    def one(m):
        pool = {"id": ids, "num": nums, "date": nums}.get(m[1], names)
        return pool.pop(0) if pool else m[0]
    return MASK.sub(one, norm)


def meaning(note):
    """The annotator's reading with the masks filled from the note as typed: a masked token is the typed token, a
    mask inside a reading ('2000H' -> '<num> hour', 'AI9714-Inspect' -> '<id> - inspect') is filled by fill(), and
    a token merged into a masked one ('BYF 89' -> '<id>', '') stays with it. Other merged tokens ('AIR CON' ->
    'air conditioner', '') add nothing."""
    out, after_mask = [], False
    for raw, norm in note:
        if MASK.fullmatch(norm):
            out.append(raw)
            after_mask = True
        elif not norm:
            if after_mask:
                out[-1] += " " + raw
        elif MASK.search(norm):
            out.append(fill(raw, norm))
            after_mask = bool(re.search(r"<(?:id|sensitive)>\s*$", norm))  # 'PARTS/NIGEL THOMAS': the surname follows
        else:
            out.append(norm)
            after_mask = False
    return " ".join(out)


def problems(note):
    """A reading must not gain a number the note did not have, nor lose the digits of an asset number as typed
    (expansions such as POS4 -> position 4 keep them). The few it finds are the annotator's own readings."""
    typed, read = " ".join(r for r, _ in note), meaning(note)
    gained = collections.Counter(re.findall(r"\d+", read)) - collections.Counter(re.findall(r"\d+", typed))
    lost = [i for i in ID.findall(typed) if re.sub(r"\D", "", i) not in read]
    return (["gained " + " ".join(gained)] if gained else []) + (["lost " + " ".join(lost)] if lost else [])


def main(data, out):
    for c, folder in COMPANIES.items():
        notes = read(Path(data) / folder / "train.norm")
        lines = [f"# Company {c}: earlier work orders and what they mean", ""]
        for note in notes:
            typed = " ".join(raw for raw, _ in note)
            lines += [f"## {typed}", "", f"Means: {meaning(note)}", ""]
        (Path(out) / c).mkdir(parents=True, exist_ok=True)
        (Path(out) / c / "notes.md").write_text("\n".join(lines), encoding="utf-8")
        left = sum(bool(MASK.search(meaning(n))) for n in notes)
        bad = [(" ".join(r for r, _ in n), problems(n)) for n in notes if problems(n)]
        assert left <= 1, f"{c}: {left} readings still hold a mask"  # XF3996- (B): a second asset number the note does not hold
        for b in bad[:8]:
            print("  check:", b)
        print(f"  {len(bad)} readings flagged")
        print(c, len(notes), "notes")


if __name__ == "__main__":
    assert fill("engineV1", "engine <id>") == "engine V1" and fill("7897-3Week", "<id> - <num> week") == "7897 - 3 week"
    assert fill("KD208-24/04/10", "<id> - <date>") == "KD208 - 24/04/10" and fill("2000H", "<num> hour") == "2000 hour"
    assert fill("lines6ats", "lines <num>") == "lines 6" and fill("XF3996-", "<id> - <id> - repair") == "XF3996 - <id> - repair"
    assert meaning([("PARTS/NIGEL", "parts / <sensitive>"), ("THOMAS", "")]).endswith("NIGEL THOMAS")
    assert fill("driverriveTR37b", "driver <id>") == "driver TR37b" and fill("&e", "and <id>") == "and e" and meaning([("N0", "number <num>"), ("s", "")]) == "number 0"
    main(*sys.argv[1:3])
