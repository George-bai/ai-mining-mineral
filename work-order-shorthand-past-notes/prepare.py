"""Builds each site's glossary from its own training notes and draws the held-out notes the model reads.

    python3 prepare.py <maintnorm>/data

Writes glossary/<A|B|C>.txt (the 50 most frequent shorthand forms in that company's train split, with the meanings
MaintNorm's annotator gave them), notes-test.json (100 notes per company from its test split, each with at least
one piece of shorthand and none repeating an earlier train or val note) and notes-dev.json (12 per company from the val split, for trying the prompt).
No test note is read to build a glossary. Standard library only.
"""
import collections, json, random, re, sys
from pathlib import Path

HERE = Path(__file__).parent
COMPANIES = {"A": "company_a", "B": "company_b", "C": "company_c"}
SIZE, SHARE, PER_TEST, PER_DEV, SEED = 50, 0.2, 100, 12, 11
MASK = re.compile(r"<(id|num|date|sensitive)>")


def read(path):
    """A .norm file: one 'raw<TAB>normalised' token per line, a blank line between notes."""
    notes, cur = [], []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.strip():
            raw, norm = line.split("\t")
            cur.append((raw, norm))
        elif cur:
            notes.append(cur)
            cur = []
    if cur:
        notes.append(cur)
    return notes


def shorthand(raw, norm):
    """(key, meaning) when a token is shorthand, else None. Masks (asset numbers, numbers, dates, names), case-only
    changes and merged tokens are not shorthand. Digits are dropped from the key, so 'pos1' and 'pos2' are 'pos'
    and '1000h' is 'h' = 'hour'."""
    if not norm or norm.lower() == raw.lower() or MASK.fullmatch(norm):
        return None
    key = re.sub(r"\d+", "", raw.lower())
    if not re.search(r"[a-z&#@]", key):  # '1/4' = quarter keeps its digits
        key = raw.lower()
    meaning = re.sub(r"\s+", " ", MASK.sub("", norm)).strip()
    if not meaning or not (meaning[0].isalnum() and meaning[-1].isalnum()) or key == meaning.lower():
        return None  # '- inspect': part of the token was masked, so the key would be wrong
    return key, meaning


def glossary(train):
    uses = collections.defaultdict(collections.Counter)
    for note in train:
        for raw, norm in note:
            s = shorthand(raw, norm)
            if s:
                uses[s[0]][s[1]] += 1
    keys = sorted(uses, key=lambda k: (-sum(uses[k].values()), k))[:SIZE]
    entries = []
    for k in keys:
        total = sum(uses[k].values())
        means = [m for m, n in uses[k].most_common(2) if n >= SHARE * total]
        entries.append({"key": k, "means": means, "uses": total})
    return entries


def note_record(company, split, i, note):
    return {"id": f"{company}-{split}-{i:03d}", "company": company, "split": split, "index": i,
            "text": " ".join(raw for raw, _ in note), "tokens": note}


def main(data):
    data = Path(data)
    (HERE / "glossary").mkdir(exist_ok=True)
    test, dev = [], []
    for c, folder in COMPANIES.items():
        g = glossary(read(data / folder / "train.norm"))
        lines = [f"{e['key']} = {', or '.join(e['means'])}" for e in g]
        (HERE / "glossary" / f"{c}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        (HERE / "glossary" / f"{c}.json").write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
        earlier = {" ".join(r for r, _ in n).lower() for s in ("train", "val") for n in read(data / folder / f"{s}.norm")}
        for split, per, out in (("test", PER_TEST, test), ("val", PER_DEV, dev)):
            notes = read(data / folder / f"{split}.norm")
            # a test note whose text repeats an earlier note (ignoring case) is not unseen: left out
            ok = [i for i, n in enumerate(notes) if any(shorthand(r, m) for r, m in n)
                  and (split != "test" or " ".join(r for r, _ in n).lower() not in earlier)]
            for i in sorted(random.Random(f"{SEED}-{c}-{split}").sample(ok, per)):
                out.append(note_record(c, split, i, notes[i]))
    (HERE / "notes-test.json").write_text(json.dumps(test, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (HERE / "notes-dev.json").write_text(json.dumps(dev, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(test)} test notes, {len(dev)} dev notes, glossaries of {SIZE}")


if __name__ == "__main__":
    assert shorthand("REPL", "replace") == ("repl", "replace")
    assert shorthand("1000h", "<num> hour") == ("h", "hour")
    assert shorthand("1/4", "quarter") == ("1/4", "quarter") and shorthand("QR-inspect", "<id> - inspect") is None
    assert shorthand("CR871", "<id>") is None and shorthand("TYRE", "tyre") is None
    main(sys.argv[1])
