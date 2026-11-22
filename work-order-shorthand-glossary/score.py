"""Scores every answer against MaintNorm's key, then applies the hand check.

    python3 score.py <notes.json> <answers folder> [--check check.json] [--sheet sheet.md] [--out results.json]

Per piece of shorthand in a note (prepare.shorthand), the script's first pass:
  right   the model's expansion (its "terms", else its plain text) carries every word of the key's meaning
  wrong   it expanded the shorthand to something else
  unsure  it listed the shorthand as unsure and gave no reading, or offered two readings ('repair or replace')
  kept    it left the shorthand as written, without saying it was unsure
Words are compared lower-case, without punctuation, singular and plural alike.
Per answer it flags, for the hand check, words that may add a diagnosis or say work was done.
check.json holds the hand check, made blind: the sheet (--sheet) shows each note's two answers as x and y, in an
order drawn from the note id, so the reader does not know which had the glossary. Keys are '<note id>|<x|y>' for an
answer's verdicts and '<note id>|<x|y>|<token index>' for a correction to one item's outcome, each with its reason;
'_answers' holds a digest of each answer read (its plain text, terms and unsure list), and a verdict or correction
is applied only to the answer it was made on: a fresh or changed answer counts as unchecked.
An answer's verdicts: meaning (the plain text says what the note says: nothing misread, dropped or added), diagnosis
(it states a cause, fault or condition the note does not), done (it says work was done and the note does not),
added (it adds a part, place, quantity or action that is not in the note). --final refuses to report while any
answer is missing, unparsed answers aside, or lacks a verdict.
"""
import argparse, hashlib, json, random, re
from pathlib import Path
from prepare import shorthand, HERE

WORD = re.compile(r"[a-z0-9']+")
DIAG = re.compile(r"\b(due to|caus\w*|because|likely|probabl\w*|suspect\w*|appear\w*|seem\w*|worn|wear|fail\w*|faulty|"
                  r"fault|broken|leak\w*|damag\w*|crack\w*|malfunction\w*|defect\w*|problem|issue)\b")
DONE = re.compile(r"\b(was|were|has been|have been|had been|been)\b|\b(complete[sd]?|finished|done|carried out|"
                  r"replaced|repaired|fixed|changed|installed|fitted|rectified|removed|adjusted|cleaned|serviced)\b")


def words(s):
    return [w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w
            for w in WORD.findall(s.lower().replace("-", " ").replace("/", " "))]


def has(meaning, text):
    m, t = words(meaning), set(words(text))
    return bool(m) and all(w in t for w in m)


def parse(content):
    s = (content or "").strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    try:
        return json.loads(s[s.index("{"): s.rindex("}") + 1])
    except ValueError:
        return None


def same_written(raw, written):
    r = raw.lower().strip(".,;:")
    return r == written.lower().strip(".,;:") or r in re.split(r"\s+", written.lower())


def first_pass(raw, meaning, ans):
    terms = [t for t in ans.get("terms") or [] if isinstance(t, dict) and same_written(raw, str(t.get("written", "")))]
    if terms:
        means = str(terms[0].get("means", ""))
        bare = re.sub(r"\([^)]*\)", "", means.lower())  # 'north-west (a location or area)' is one reading
        if re.search(r"\bor\b", bare) and not re.search(r"\bor\b", meaning.lower()):
            return "unsure", means  # 'repair or replace': two readings offered, the reader is not told which
        return ("right" if any(has(meaning, str(t.get("means", ""))) for t in terms) else "wrong"), means
    plain = str(ans.get("plain", ""))
    if any(same_written(raw, str(u)) for u in ans.get("unsure") or []):
        return "unsure", None
    if has(meaning, plain):
        return "right", "(in the plain text)"
    if raw.lower() in plain.lower():
        return "kept", None
    return "wrong", "(not in terms; plain text lacks the meaning)"


def flags(regex, plain, key_text):
    found = {m.group(0) for m in regex.finditer(plain.lower())}
    return sorted(f for f in found if f not in key_text.lower())


def digest(ans):
    """A short hash of what the hand check read: the answer's plain text, terms and unsure list."""
    a = ans or {}
    return hashlib.sha256(json.dumps([a.get("plain"), a.get("terms"), a.get("unsure")], ensure_ascii=False,
                                     sort_keys=True).encode()).hexdigest()[:16]


def labels(note_id):
    """{'x': condition, 'y': condition}, the same every time for a note."""
    return dict(zip("xy", random.Random(note_id).sample(["none", "glossary"], 2)))


def score(notes, answers, check, seen=None):
    glossary = {c: {e["key"]: e["means"] for e in json.loads((HERE / "glossary" / f"{c}.json").read_text())} for c in "ABC"}
    rows = []
    for n in notes:
        key_text = " ".join(m for _, m in n["tokens"])
        for label, cond in sorted(labels(n["id"]).items()):
            f = Path(answers) / cond / f"{n['id']}.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text(encoding="utf-8"))
            ans = parse(r["content"])
            read_this = (seen or {}).get(f"{n['id']}|{label}") == digest(ans)  # the hand check is of this very answer
            row = {"id": n["id"], "company": n["company"], "label": label, "condition": cond, "note": n["text"], "key": key_text,
                   "parsed": ans is not None, "finish": r.get("finish"), "seconds": r["seconds"],
                   "tokens": (r.get("usage") or {}).get("completion_tokens"), "terms": (ans or {}).get("terms"), "unsure": (ans or {}).get("unsure"),
                   "plain": (ans or {}).get("plain"), "items": []}
            for i, (raw, norm) in enumerate(n["tokens"]):
                s = shorthand(raw, norm)
                if not s:
                    continue
                k, meaning = s
                outcome, read = first_pass(raw, meaning, ans) if ans else ("wrong", "(no answer)")
                fix = check.get(f"{n['id']}|{label}|{i}") if read_this else None
                row["items"].append({"i": i, "raw": raw, "meaning": meaning, "in_glossary": k in glossary[n["company"]],
                                     "glossary_agrees": meaning.lower() in [m.lower() for m in glossary[n["company"]].get(k, [])],
                                     "script": outcome, "outcome": fix["outcome"] if fix else outcome, "read": read,
                                     "why": fix["why"] if fix else None})
            plain = str(row["plain"] or "")
            row["diag_flags"], row["done_flags"] = flags(DIAG, plain, key_text), flags(DONE, plain, key_text)
            v = check.get(f"{n['id']}|{label}") if read_this else None
            row["checked"] = v is not None and all(k in v for k in ("meaning", "diagnosis", "done", "added"))
            v = v or {}
            row["meaning"], row["diagnosis"], row["done"], row["added"] = (v.get("meaning"), v.get("diagnosis"),
                                                                         v.get("done"), v.get("added"))
            row["verdict_why"] = v.get("why")
            rows.append(row)
    return rows


def summary(rows):
    out = {}
    for cond in ("none", "glossary"):
        rs = [r for r in rows if r["condition"] == cond]
        items = [it | {"company": r["company"]} for r in rs for it in r["items"]]
        def count(sel):
            c = {k: 0 for k in ("right", "wrong", "unsure", "kept")}
            for it in sel:
                c[it["outcome"]] += 1
            return c | {"n": len(sel)}
        out[cond] = {"answers": len(rs), "unparsed": sum(not r["parsed"] for r in rs),
                     "cut_off": sum(r["finish"] != "stop" for r in rs), "unchecked": sum(not r["checked"] for r in rs),
                     "meaning_kept": sum(r["meaning"] is True for r in rs),
                     "items": count(items),
                     "in_glossary": count([it for it in items if it["in_glossary"]]),
                     "not_in_glossary": count([it for it in items if not it["in_glossary"]]),
                     "by_company": {c: count([it for it in items if it["company"] == c]) for c in "ABC"},
                     "notes_all_right": sum(all(it["outcome"] == "right" for it in r["items"]) for r in rs),
                     "diagnosis": sum(r["diagnosis"] is True for r in rs), "done": sum(r["done"] is True for r in rs),
                     "added": sum(r["added"] is True for r in rs),
                     "median_seconds": sorted(r["seconds"] for r in rs)[len(rs) // 2] if rs else None}
    return out


def sheet(rows):
    by = {}
    for r in rows:
        by.setdefault(r["id"], []).append(r)
    out = []
    for nid, rs in by.items():
        out.append(f"## {nid}\nNOTE: {rs[0]['note']}\nKEY:  {rs[0]['key']}\n")
        for r in rs:
            out.append(f"[{r['label']}] PLAIN: {r['plain']}")
            if r["unsure"]:
                out.append(f"      unsure: {r['unsure']}")
            if r["diag_flags"] or r["done_flags"]:
                out.append(f"   flags: diagnosis {r['diag_flags']} done {r['done_flags']}")
            for it in r["items"]:
                mark = "" if it["outcome"] == "right" else "  <<"
                out.append(f"   {it['i']:>2} {it['raw']!r} = {it['meaning']!r} {'G' if it['in_glossary'] else '-'} "
                           f"{it['outcome']}: {it['read']}{mark}")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notes"); ap.add_argument("answers")
    ap.add_argument("--check"); ap.add_argument("--sheet"); ap.add_argument("--out")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    notes = json.loads(Path(a.notes).read_text(encoding="utf-8"))
    check = json.loads(Path(a.check).read_text(encoding="utf-8")) if a.check and Path(a.check).exists() else {}
    seen = check.get("_answers", {})
    check = {k: v for k, v in check.items() if not k.startswith("_")}
    rows = score(notes, a.answers, check, seen)
    if a.final:
        missing = 2 * len(notes) - len(rows)
        unchecked = [f"{r['id']}|{r['label']}" for r in rows if not r["checked"]]
        if missing or unchecked:
            raise SystemExit(f"not final: {missing} answers missing, {len(unchecked)} without a verdict, e.g. {unchecked[:3]}")
    if a.sheet:
        Path(a.sheet).write_text(sheet(rows), encoding="utf-8")
    s = summary(rows)
    if a.out:
        Path(a.out).write_text(json.dumps({"summary": s, "answers": rows}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    assert has("air conditioner", "Air-conditioners") and not has("left hand", "left")
    assert first_pass("REPL", "replace", {"terms": [{"written": "REPL", "means": "replace"}]})[0] == "right"
    assert first_pass("stut", "stud", {"terms": [{"written": "stut", "means": "strut"}]})[0] == "wrong"
    assert first_pass("hyd", "hydraulic", {"plain": "hyd hose", "unsure": ["hyd"]})[0] == "unsure"
    main()
