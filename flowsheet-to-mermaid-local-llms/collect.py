"""Collect a run into results/: each model's Mermaid file and rendered SVG, and results.json with the
measured numbers. The raw Pi logs stay out: they hold the drawings.   Usage: python3 collect.py ../local/runs/run3
Run render.py on the run first. Models and drawings are taken from the run's own folders."""
import collections, datetime, json, shutil, sys
from pathlib import Path

here, run = Path(__file__).parent, Path(sys.argv[1]).resolve()
# Known drawings and models get a short name and a title; anything else is collected under its folder name.
DRAWINGS = {"p23": ("simple-circuit", "Simple unit circuit", 23), "p53": ("block-diagram", "Block diagram", 53),
            "p39": ("phoenix", "Complex flowsheet", 39), "p37": ("twin-creeks", "Extremely complex flowsheet", 37)}
MODELS = {"qwen27b__qwen38-27b": "Qwen 3.8 27B", "flashnext__qwen38-next-flash": "Qwen 3.8 Flash Next",
          "qwen38-27b": "Qwen 3.8 27B", "qwen38-next-flash": "Qwen 3.8 Flash Next"}   # the last two: the folder names of the reported run
ORDER = list(DRAWINGS)
rows = []
(here / "results" / run.name).mkdir(parents=True, exist_ok=True)
models = sorted((d.name for d in run.iterdir() if d.is_dir() and d.name != "pi-agent"), key=lambda m: (list(MODELS).index(m) if m in MODELS else 99, m))
for model in models:
    folders = sorted((d for d in (run / model).iterdir() if d.is_dir()), key=lambda d: (ORDER.index(d.name.split("-")[0]) if d.name.split("-")[0] in ORDER else 99, d.name))
    for src in folders:
        slug, level, slide = DRAWINGS.get(src.name.split("-")[0], (src.name, "", None))
        tools, tokens_in, tokens_out, turns, stop, extra_images = collections.Counter(), 0, 0, 0, None, 0
        steps, t0 = [], 0
        for line in open(src / "events.jsonl"):
            try: e = json.loads(line)
            except ValueError: continue
            if e.get("type") == "session":
                t0 = datetime.datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).timestamp()
            if e.get("type") == "tool_execution_start":
                tools[e["toolName"]] += 1
            m = e.get("message") or {}
            if e.get("type") == "message_end" and m.get("role") == "toolResult":
                # one step per tool call, timed when its result came back; an image in the result is a zoomed look
                images = sum(1 for part in m.get("content") or [] if isinstance(part, dict) and part.get("type") == "image")
                extra_images += images
                name = m.get("toolName", "")
                kind = "look" if images else "write" if name in ("write", "edit") else "command" if name == "bash" else "read"
                steps.append([round(m["timestamp"] / 1000 - t0), kind])
            if e.get("type") == "message_end" and m.get("role") == "assistant":
                u = m.get("usage") or {}
                turns, stop = turns + 1, m.get("errorMessage") or m.get("stopReason")
                tokens_in += u.get("input", 0) + u.get("cacheRead", 0); tokens_out += u.get("output", 0)
        row = {"model": model, "model_name": MODELS.get(model, model), "drawing": slug, "level": level, "slide": slide,
               "seconds": int((src / "seconds.txt").read_text()), "turns": turns, "tool_calls": dict(tools),
               "extra_images": extra_images, "tokens_in": tokens_in, "tokens_out": tokens_out, "ended": stop,
               "wrote_file": (src / "flowsheet.mmd").exists(), "steps": steps}
        out = here / "results" / run.name / model / slug
        shutil.rmtree(out, ignore_errors=True)   # nothing from an earlier collection may outlive a failed attempt
        if row["wrote_file"]:
            out.mkdir(parents=True, exist_ok=True)
            shutil.copy(src / "flowsheet.mmd", out / "flowsheet.mmd")
            info = json.loads((src / "mermaid.json").read_text())   # from render.py
            row.update(renders=info["ok"], nodes=info.get("nodes"), lines=info.get("lines"),
                       width=info.get("width"), height=info.get("height"))
            if info["ok"]:
                shutil.copy(src / "mermaid.svg", out / "flowsheet.svg")
        rows.append(row)
text = json.dumps(rows, indent=1).replace("[\n    ", "[").replace(",\n    ", ", ").replace("\n   ]", "]")
(here / "results" / run.name / "results.json").write_text(text + "\n")
for r in rows:
    print(f'{r["model"]:18} {r["drawing"]:15} {r["seconds"]:4} s  turns {r["turns"]:3}  extra images {r["extra_images"]:2}  '
          f'in {r["tokens_in"]:8}  out {r["tokens_out"]:6}  nodes {r.get("nodes")}  lines {r.get("lines")}  {r["ended"]}')
# A step is timed from the session start, so none can fall outside the run.
assert all(0 <= t <= r["seconds"] + 2 for r in rows for t, _ in r["steps"]), "a step is timed outside its run"
