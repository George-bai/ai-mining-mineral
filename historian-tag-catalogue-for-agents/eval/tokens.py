"""Context cost: tokens of the whole tag list against one search answer, counted by the 27B model's own tokenizer
through its server's tokenize call (no generation). Writes eval/tokens.json.

    uv run python eval/tokens.py <catalogue.sqlite> [http://localhost:8088]

The whole list is one line per tag: path, point name and unit, tab-separated. A search answer is what the MCP server's
search_tags returns for a round-2 question (10 results, as JSON), for three questions.
"""
import json, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import catalog  # noqa: E402

QUESTIONS = ["q03", "q20", "q45"]


def tokens(server, text):
    req = urllib.request.Request(f"{server}/tokenize", data=json.dumps({"model": "qwen38-27b", "prompt": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    return d.get("count", len(d.get("tokens", [])))


def main(db, server="http://localhost:8088"):
    con = catalog.connect(db)
    rows = con.execute("SELECT path, point, unit FROM tags ORDER BY id").fetchall()
    whole = "\n".join(f"{p}\t{pt or ''}\t{u or ''}" for p, pt, u in rows)
    import yaml
    key = {q["id"]: q for q in yaml.safe_load((ROOT / "eval" / "round2" / "key.yaml").read_text())}
    answers = {q: json.dumps(catalog.search(con, key[q]["question"], limit=10), indent=2) for q in QUESTIONS}
    with urllib.request.urlopen(f"{server}/v1/models", timeout=30) as r:
        model = json.load(r)["data"][0]
    out = {"tags": len(rows), "whole_list": {"characters": len(whole), "tokens": tokens(server, whole)},
           "search_answers": {q: {"question": key[q]["question"], "characters": len(a), "tokens": tokens(server, a)}
                              for q, a in answers.items()},
           "model": model["id"], "weights": model.get("root"), "context_window": model.get("max_model_len")}
    (ROOT / "eval" / "tokens.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
