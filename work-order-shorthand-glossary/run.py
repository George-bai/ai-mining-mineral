"""Asks the model to read each note twice: without the site glossary and with it.

    python3 run.py <notes.json> <out folder> [--url URL] [--model ID] [--jobs 2]

One request per note and condition, through an OpenAI-compatible chat endpoint. The prompt is prompt.md; the
glossary block is the only difference between the two conditions. No sampling settings are sent: the server's own
apply. Each answer is saved as <out>/<condition>/<note id>.json (the reply, the model's reasoning, tokens, seconds).
A note already answered with the same prompt is skipped, so an interrupted run can be started again; an answer
made with another prompt stops the run. The server's model list is saved as <out>/server.json. The conditions alternate in the
queue, so both meet the same server load. Standard library only.
"""
import argparse, json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
GLOSSARY = ("\nSite glossary: shorthand from this site's earlier work orders and what it means here. "
            "The same shorthand can mean something else at another site.\n\n{lines}")


def prompt(note, glossary):
    block = GLOSSARY.format(lines=glossary) if glossary else ""
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
    ap.add_argument("notes"); ap.add_argument("out")
    ap.add_argument("--url", default="http://localhost:8088/v1/chat/completions")
    ap.add_argument("--model", default="qwen38-27b")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    notes = json.loads(Path(a.notes).read_text(encoding="utf-8"))
    glossaries = {c: (HERE / "glossary" / f"{c}.txt").read_text(encoding="utf-8") for c in "ABC"}
    jobs = []
    for i, n in enumerate(notes):
        conds = ["none", "glossary"] if i % 2 == 0 else ["glossary", "none"]
        for c in conds:
            f = Path(a.out) / c / f"{n['id']}.json"
            if not f.exists():
                jobs.append((n, c, f))
            elif json.loads(f.read_text(encoding="utf-8"))["prompt"] != prompt(n, glossaries[n["company"]] if c == "glossary" else None):
                raise SystemExit(f"{f} was made with another prompt or glossary: use a new out folder")
    Path(a.out).mkdir(parents=True, exist_ok=True)
    models = json.load(urllib.request.urlopen(a.url.replace("/chat/completions", "/models"), timeout=30))
    (Path(a.out) / "server.json").write_text(json.dumps(models, indent=1) + "\n", encoding="utf-8")

    def one(job):
        n, c, f = job
        text = prompt(n, glossaries[n["company"]] if c == "glossary" else None)
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
