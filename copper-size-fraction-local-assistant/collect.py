"""Collect a run into results/<run>/: for each attempt, the model's final answer (answer.md), its thinking and every
Python or shell command it ran with what came back, in order (steps.md), and results.json with time, turns, tokens and tool calls.
Usage: python3 collect.py ../local/runs/run1"""
import json, shutil, sys
from pathlib import Path

here, run = Path(__file__).parent, Path(sys.argv[1]).resolve()
NAMES = {"qwen27b__qwen38-27b": "Qwen 3.8 27B", "flashnext__qwen38-next-flash": "Qwen 3.8 Flash Next"}
rows = []
for model in [m for m in NAMES if (run / m).is_dir()]:
    for att in sorted((run / model).iterdir(), key=lambda d: int(d.name)):
        answer, steps, tools, turns, tin, tout, stop = "", [], {}, 0, 0, 0, None
        for line in open(att / "events.jsonl"):
            try: e = json.loads(line)
            except ValueError: continue
            m = e.get("message") or {}
            if e.get("type") != "message_end": continue
            if m.get("role") == "assistant":
                u = m.get("usage") or {}
                turns, stop = turns + 1, m.get("errorMessage") or m.get("stopReason")
                tin += u.get("input", 0) + u.get("cacheRead", 0); tout += u.get("output", 0)
                text = "".join(p.get("text", "") for p in m.get("content") or [] if p.get("type") == "text").strip()
                if text: answer = text          # the last text the model wrote is its answer
                for p in m.get("content") or []:
                    if p.get("type") == "thinking" and p.get("thinking", "").strip():
                        steps.append(f"### thinking\n\n{p['thinking'].strip()}\n")
                    if p.get("type") == "text" and p.get("text", "").strip():
                        steps.append(f"### reply\n\n{p['text'].strip()}\n")
                    if p.get("type") == "toolCall":
                        tools[p["name"]] = tools.get(p["name"], 0) + 1
                        args = p.get("arguments") or {}
                        steps.append(f"### {p['name']}\n\n```\n{args.get('command') or json.dumps(args, indent=1)}\n```\n")
            if m.get("role") == "toolResult":
                out = "".join(p.get("text", "") for p in m.get("content") or [] if p.get("type") == "text")
                steps.append(f"Result:\n\n```\n{out.strip()}\n```\n")
        dest = here / "results" / run.name / model / att.name
        shutil.rmtree(dest, ignore_errors=True); dest.mkdir(parents=True)
        (dest / "answer.md").write_text(answer + "\n")
        (dest / "steps.md").write_text("\n".join(steps) + "\n")
        rows.append({"model": model, "model_name": NAMES[model], "attempt": int(att.name),
                     "seconds": int((att / "seconds.txt").read_text()), "turns": turns, "tool_calls": tools,
                     "tokens_in": tin, "tokens_out": tout, "ended": stop})
(here / "results" / run.name / "results.json").write_text(json.dumps(rows, indent=1) + "\n")
for r in rows:
    print(f'{r["model_name"]:20} #{r["attempt"]}  {r["seconds"]:4} s  turns {r["turns"]:2}  tools {r["tool_calls"]}  out {r["tokens_out"]:6}  {r["ended"]}')
