"""Counts made without a model: what each version put in front of the model for each piece of shorthand, the prompt
sizes, and the test notes that repeat a training note once asset numbers are set aside.

    python3 coverage.py <maintnorm>/data <search folder> <answers folder> [--out coverage.json]

Covered (the same rule for both versions): the piece's form (prepare.shorthand's key: lower case, digits dropped)
appears with the key's meaning in one place. Glossary: the form is one of the company's 50 keys and the key's meaning
is among that entry's meanings (No. 13's 'glossary_agrees'). Search: one returned passage holds a word of the earlier
note as typed with that form, and that passage's 'Means' line holds every word of the key's meaning (score.has).
Near-duplicate: the note's text, lower case, with every token the key masks as an asset number (<id>) removed, equals
a training note's text treated the same way.
"""
import argparse, json, re, statistics
from pathlib import Path
from prepare import COMPANIES, HERE, read, shorthand
from score import has


def key(token):
    k = re.sub(r"\d+", "", token.lower())
    return k if re.search(r"[a-z&#@]", k) else token.lower()


def passages(search, note):
    rec = json.loads((Path(search) / note["company"] / f"{note['id']}.deep.json").read_text(encoding="utf-8"))
    out = []
    for r in rec["results"]:
        typed = r["heading"].split(" / ", 1)[1] if " / " in r["heading"] else r["heading"]
        out.append(({key(t) for t in typed.split()}, r["content"].strip().removeprefix("Means:").strip()))
    return out


def bare(note_tokens):
    return " ".join(raw.lower() for raw, norm in note_tokens if norm != "<id>")


ID = re.compile(r"(?<![A-Za-z])[A-Za-z]{1,3}\d+")


def bare_broad(note_tokens):
    """As bare(), and asset numbers inside a token the key marks with <id> removed too ('BT0391-C/out' -> '-c/out');
    added after the run, at Codex's page review, beside the protocol's count."""
    out = [ID.sub("", raw.lower()) if "<id>" in norm else raw.lower() for raw, norm in note_tokens if norm != "<id>"]
    return " ".join(w for w in out if w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("search"); ap.add_argument("answers"); ap.add_argument("--out")
    a = ap.parse_args()
    notes = json.loads((HERE / "notes-test.json").read_text(encoding="utf-8"))
    gloss = {c: {e["key"]: e["means"] for e in json.loads((HERE / "glossary" / f"{c}.json").read_text())} for c in "ABC"}
    trained = {c: read(Path(a.data) / f / "train.norm") for c, f in COMPANIES.items()}
    train = {c: {bare(n) for n in t} for c, t in trained.items()}
    train_broad = {c: {bare_broad(n) for n in t} for c, t in trained.items()}
    items, near, near_broad, sizes = [], [], [], {"search": [], "glossary": []}
    for n in notes:
        found = passages(a.search, n)
        for i, (raw, norm) in enumerate(n["tokens"]):
            s = shorthand(raw, norm)
            if not s:
                continue
            k, meaning = s
            g = k in gloss[n["company"]] and meaning.lower() in [m.lower() for m in gloss[n["company"]][k]]
            hit = [j + 1 for j, (forms, means) in enumerate(found) if k in forms and has(meaning, means)]
            items.append({"id": n["id"], "company": n["company"], "i": i, "raw": raw, "meaning": meaning,
                          "glossary": g, "search": bool(hit), "search_places": hit})
        if bare(n["tokens"]) in train[n["company"]]:
            near.append(n["id"])
        if bare_broad(n["tokens"]) in train_broad[n["company"]]:
            near_broad.append(n["id"])
        for v in sizes:
            f = Path(a.answers) / v / f"{n['id']}.json"
            if f.exists():
                sizes[v].append(len(json.loads(f.read_text(encoding="utf-8"))["prompt"]))
    count = lambda sel: {"n": len(sel), "glossary": sum(x["glossary"] for x in sel), "search": sum(x["search"] for x in sel),
                         "both": sum(x["glossary"] and x["search"] for x in sel),
                         "only_search": sum(x["search"] and not x["glossary"] for x in sel),
                         "only_glossary": sum(x["glossary"] and not x["search"] for x in sel)}
    out = {"items": count(items), "by_company": {c: count([x for x in items if x["company"] == c]) for c in "ABC"},
           "prompt_chars_median": {v: statistics.median(s) if s else None for v, s in sizes.items()},
           "prompt_chars_range": {v: [min(s), max(s)] if s else None for v, s in sizes.items()},
           "near_duplicates": {"n": len(near), "ids": near}, "near_duplicates_broad": {"n": len(near_broad), "ids": near_broad},
           "per_item": items}
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_item",)} | {"near_duplicates": len(near), "near_duplicates_broad": len(near_broad)}, indent=1))


if __name__ == "__main__":
    assert key("POS7") == "pos" and key("1/4") == "1/4"
    main()
