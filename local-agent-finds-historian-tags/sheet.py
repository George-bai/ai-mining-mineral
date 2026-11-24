"""A reading sheet per attempt, for scoring by hand beside the key: the tags the agent read (catalogue paths and
health), the key's tags, whether a chart was saved, tool calls, seconds and the final answer. Also writes
attempts.json, the facts the scorer and the page use. Nothing here decides pass or fail; verdicts.yaml does.

    ../../historian-tag-catalogue-for-agents/public/.venv/bin/python sheet.py ../local/runs/r1 > ../local/sheet-r1.md
"""
import json, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).parent
CAT = HERE.parent.parent / "historian-tag-catalogue-for-agents" / "public" / "local" / "catalog" / "catalog.sqlite"
READS = ("mcp__historian__get_timeseries", "mcp__historian__get_current_values")


def attempt(d: Path, tags):
    calls, text, reads = [], "", []
    for line in (d / "events.jsonl").read_text().splitlines():
        e = json.loads(line)
        if e.get("type") == "tool_execution_start":
            calls.append(e.get("toolName"))
            if e.get("toolName") in READS:
                for i in e.get("args", {}).get("ids", []):
                    reads.append(str(i))
        elif e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant":
            t = "".join(c.get("text", "") for c in e["message"]["content"] if c.get("type") == "text").strip()
            text = t or text
    read_paths = []
    for i in reads:
        r = tags.get(i) or tags.get(("point", i)) or tags.get(("path", i))
        read_paths.append(r["path"] if r else f"(not in catalogue: {i})")
    return {"calls": len(calls), "tools": calls, "read": sorted(set(read_paths)), "png": sorted(p.name for p in d.glob("*.png")),
            "seconds": float((d / "seconds.txt").read_text()), "answer": text,
            "stopped": (d / "stderr.txt").read_text().strip()[-200:] if (d / "stderr.txt").exists() else ""}


def main(run):
    con = sqlite3.connect(CAT)
    tags = {}
    for i, path, point, health in con.execute("SELECT id, path, point, health FROM tags"):
        r = {"path": path, "health": health}
        tags[str(i)], tags[("point", point)], tags[("path", path)] = r, r, r
    key = {k["id"]: k for k in json.loads((HERE / "key.json").read_text())}
    out = {}
    for qd in sorted(Path(run).glob("t*")):
        for rd in sorted(qd.iterdir()):
            if not (rd / "seconds.txt").exists():  # still running
                continue
            a = attempt(rd, tags)
            out[f"{qd.name}/{rd.name}"] = a
            k = key[qd.name]
            print(f"\n## {qd.name}/{rd.name} · {k['type']} · {a['seconds']} s · {a['calls']} calls · charts {a['png']}\n")
            print(f"**Q:** {k['question']}\n")
            print("**Key:** " + "; ".join(p.split('Mining\\')[-1] + (f" [{h}]" if h != "ok" else "") for p, h in zip(k["tags"][:8], k["health"][:8]))
                  + (" …" if len(k["tags"]) > 8 else "") + (f"  winner: {k['winner'].split('Mining\\')[-1]}" if k.get("winner") else ""))
            print("\n**Read:** " + "; ".join(p.split('Mining\\')[-1] + ("" if p in k["tags"] else " (not in key)") for p in a["read"]))
            print("\n**Answer:**\n\n> " + a["answer"].replace("\n", "\n> ")[:2500])
            if a["stopped"]:
                print(f"\n**stderr:** {a['stopped']}")
    (Path(run) / "attempts.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
