"""Build the Geo-NER task from the OzROCK annotated corpus (Enkhsaikhan et al. 2021).

OzROCK EvaluationSet.txt is a CoNLL-style BIO corpus (Word <TAB> TrueLabel) whose label set is
MINERAL, ROCK, LOCATION, STRAT, ORE_DEPOSIT, TIMESCALE. Each sample becomes:

  input  = {"text": <source text>, "entity_types": [<categories present in that text>]}
  answer = {"<TYPE>": ["entity surface form", ...]}

200 samples are drawn at random (seed 42) from the valid documents, mirroring the paper's
procedure of removing invalid/duplicate/anomalous samples and then sampling randomly.
"""
from __future__ import annotations

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "data", "raw", "OzROCK_EvaluationSet.txt")
OUT = os.path.join(HERE, "data", "bench", "geo_ner.jsonl")
N_SAMPLES = 200
SEED = 42
TYPES = ["MINERAL", "ROCK", "LOCATION", "STRAT", "ORE_DEPOSIT", "TIMESCALE"]

_NO_SPACE_BEFORE = set(".,;:!?)]%")
_NO_SPACE_AFTER = set("([{")


def detokenize(tokens: list[str]) -> str:
    out = []
    for i, tok in enumerate(tokens):
        if i == 0:
            out.append(tok)
            continue
        prev = tokens[i - 1]
        if tok[0] in _NO_SPACE_BEFORE or prev[-1] in _NO_SPACE_AFTER or prev.endswith("."):
            out.append(tok)
        else:
            out.append(" " + tok)
    s = "".join(out)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def read_docs(path: str):
    blocks = [b for b in open(path, encoding="utf-8").read().split("\n\n") if b.strip()]
    for bi, block in enumerate(blocks):
        rows = []
        for line in block.strip().split("\n"):
            if not line.strip():
                continue
            word, _, label = line.rpartition("\t")
            if not word:  # tolerate space-separated variant
                parts = line.rsplit(None, 1)
                if len(parts) != 2:
                    continue
                word, label = parts
            else:
                label = label.strip()
            word = word.strip()
            if not word:
                continue
            rows.append((word, label))
        if rows and rows[0] == ("Word", "TrueLabel"):
            rows = rows[1:]
        if rows:
            yield bi, rows


def spans_from(rows):
    ents: dict[str, list[str]] = {}
    cur, ctype = [], None
    for word, label in rows + [("", "O")]:
        if label.startswith("B-"):
            if cur:
                ents.setdefault(ctype, []).append(" ".join(cur))
            cur, ctype = [word], label[2:]
        elif label.startswith("I-") and cur and label[2:] == ctype:
            cur.append(word)
        else:
            if cur:
                ents.setdefault(ctype, []).append(" ".join(cur))
            cur, ctype = [], None
    return {t: v for t, v in ents.items() if t in TYPES}


def main() -> None:
    docs = []
    seen = set()
    for bi, rows in read_docs(RAW):
        if len(rows) < 8 or len(rows) > 80:
            continue
        ents = spans_from(rows)
        if not ents:
            continue
        n_ents = sum(len(v) for v in ents.values())
        if n_ents < 1 or n_ents > 12:
            continue
        text = detokenize([w for w, _ in rows])
        if len(text) < 40 or text.lower() in seen:
            continue
        seen.add(text.lower())
        docs.append({"text": text, "ents": ents})
    print(f"valid OzROCK documents: {len(docs)}")
    random.seed(SEED)
    chosen = random.sample(docs, min(N_SAMPLES, len(docs)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    type_hist: dict[str, int] = {}
    with open(OUT, "w", encoding="utf-8") as f:
        for i, d in enumerate(chosen):
            types = [t for t in TYPES if t in d["ents"]]
            sample = {
                "id": f"geoner-{i:04d}",
                "type": "Geo-NER",
                "input": {"text": d["text"], "entity_types": types},
                "answer": {t: d["ents"][t] for t in types},
                "meta": {"source": "OzROCK EvaluationSet", "doc_index": None},
            }
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            for t in types:
                type_hist[t] = type_hist.get(t, 0) + len(d["ents"][t])
    print(f"wrote {len(chosen)} samples -> {OUT}")
    print("gold entity counts by type:", json.dumps(type_hist, sort_keys=True))
    with open(OUT, encoding="utf-8") as f:
        first = json.loads(f.readline())
    print("example:", json.dumps(first, ensure_ascii=False)[:500])


if __name__ == "__main__":
    sys.exit(main())
