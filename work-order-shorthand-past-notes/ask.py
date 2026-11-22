"""Asks the model to read each note with the passages SAG-Wiki found among the site's earlier work orders, and again
with No. 13's glossary (a second run of that version, the same day, to show how much a run varies).

    python3 ask.py <notes.json> <search folder> <out folder> [--url URL] [--model ID] [--jobs 2]

No. 13's runner, unchanged but for the "search" version: prompt.md with the block below in place of the glossary,
listing every passage SAG-Wiki returned for the note (<search folder>/<company>/<note id>.deep.json, from run.py), each as the
earlier note as typed = what it means. No sampling settings are sent: the server's own apply. Each answer is saved as
<out>/<version>/<note id>.json with its prompt; a note already answered with the same prompt is skipped. The
versions alternate in the queue, so both meet the same server load. Standard library only.
"""
import argparse, json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
GLOSSARY = ("\nSite glossary: shorthand from this site's earlier work orders and what it means here. "
            "The same shorthand can mean something else at another site.\n\n{lines}")
SEARCH = ("\nEarlier work orders from this site, found by searching its own records, and what each meant. "
          "The same shorthand can mean something else at another site.\n\n{lines}")


def found(search, note):
    """The passages SAG-Wiki returned for the note, in its order: 'typed = means'."""
    rec = json.loads((Path(search) / note["company"] / f"{note['id']}.deep.json").read_text(encoding="utf-8"))
    lines = []
    for r in rec["results"]:
        typed = r["heading"].split(" / ", 1)[1] if " / " in r["heading"] else r["heading"]
        means = r["content"].strip().removeprefix("Means:").strip()
        lines.append(f"{typed} = {means}")
    return "\n".join(lines)


def prompt(note, block):
    return (HERE / "prompt.md").read_text(encoding="utf-8").replace("{glossary}", block).replace("{note}", note["text"])


def ask(url, model, text):
    body = json.dumps({"model": model, "max_tokens": 16000, "messages": [{"role": "user", "content": text}]}).encode()
    t = time.time()
    req = urllib.request.Request(url, body, {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=1800))
    m = r["choices"][0]["message"]
    return {"content": m.get("content"), "reasoning": m.get("reasoning_content") or m.get("reasoning"),
            "finish": r["choices"][0].get("finish_reason"), "usage": r.get("usage"), "seconds": round(time.time() - t, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notes"); ap.add_argument("search"); ap.add_argument("out")
    ap.add_argument("--url", default="http://localhost:8088/v1/chat/completions")
    ap.add_argument("--model", default="qwen38-27b")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    notes = json.loads(Path(a.notes).read_text(encoding="utf-8"))
    glossaries = {c: (HERE / "glossary" / f"{c}.txt").read_text(encoding="utf-8") for c in "ABC"}
    block = lambda n, c: (SEARCH.format(lines=found(a.search, n)) if c == "search"
                          else GLOSSARY.format(lines=glossaries[n["company"]]))
    jobs = []
    for i, n in enumerate(notes):
        for c in (["search", "glossary"] if i % 2 == 0 else ["glossary", "search"]):
            f = Path(a.out) / c / f"{n['id']}.json"
            if not f.exists():
                jobs.append((n, c, f))
            elif json.loads(f.read_text(encoding="utf-8"))["prompt"] != prompt(n, block(n, c)):
                raise SystemExit(f"{f} was made with another prompt: use a new out folder")
    Path(a.out).mkdir(parents=True, exist_ok=True)
    models = json.load(urllib.request.urlopen(a.url.replace("/chat/completions", "/models"), timeout=30))
    (Path(a.out) / "server.json").write_text(json.dumps(models, indent=1) + "\n", encoding="utf-8")

    def one(job):
        n, c, f = job
        text = prompt(n, block(n, c))
        r = {"id": n["id"], "condition": c, "note": n["text"], "model": a.model, "prompt": text,
             "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **ask(a.url, a.model, text)}
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return f"{n['id']} {c} {r['seconds']} s {r['finish']}"

    with ThreadPoolExecutor(a.jobs) as pool:
        for line in pool.map(one, jobs):
            print(line, flush=True)


if __name__ == "__main__":
    main()
