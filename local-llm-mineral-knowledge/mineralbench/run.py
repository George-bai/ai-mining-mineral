"""Run the MineralBench core-domain tasks against one model endpoint (R = 3 rounds).

Usage:
  python3 -m mineralbench.run --model qwen38-27b --base-url http://<server>:8088 \
      --concurrency 8

Raw outputs, normalised outputs, sample-level scores and per-request latency are appended to
results/<model>.raw.jsonl, so an interrupted run resumes where it stopped.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from .executor import ChatClient
from .metrics import R_ROUNDS, TASK_ORDER
from .prompts import build_messages
from .scorers import score_sample

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH_DIR = os.path.join(HERE, "data", "bench")
RESULTS_DIR = os.path.join(HERE, "results")


TASK_FILES = {
    "Mineral-Term": ["mineral_term.jsonl", "Mineral-Term.jsonl"],
    "Mineral-Property": ["mineral_property.jsonl", "Mineral-Property.jsonl"],
    "Geo-NER": ["geo_ner.jsonl", "Geo-NER.jsonl"],
}


def load_bench(bench_dir: str = BENCH_DIR) -> dict[str, list[dict]]:
    out = {}
    for task in TASK_ORDER:
        for name in TASK_FILES.get(task, [f"{task}.jsonl"]):
            path = os.path.join(bench_dir, name)
            if os.path.exists(path):
                out[task] = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
                break
    return out


def completed_keys(raw_path: str) -> set[tuple]:
    keys = set()
    if os.path.exists(raw_path):
        for line in open(raw_path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                if r.get("error") is None:
                    keys.add((r["task"], r["sample_id"], r["round"]))
    return keys


def run(model: str, base_url: str, concurrency: int, out_dir: str,
        tasks: list[str], rounds: int = R_ROUNDS, limit: int | None = None,
        thinking: bool = False, ner_cue: str = "paper") -> None:
    os.makedirs(out_dir, exist_ok=True)
    bench = {t: s for t, s in load_bench().items() if t in tasks}
    if not bench:
        sys.exit("no benchmark files found in data/bench (run scripts/build_bench.py first)")
    if limit:
        bench = {t: s[:limit] for t, s in bench.items()}
    total_samples = sum(len(s) for s in bench.values())
    print(f"{model}: {total_samples} samples x {rounds} rounds over "
          f"{', '.join(f'{t}({len(s)})' for t, s in bench.items())}")

    client = ChatClient(base_url, model,
                        extra=({} if thinking else {"chat_template_kwargs": {"enable_thinking": False}}))
    raw_path = os.path.join(out_dir, f"{model}.raw.jsonl")
    done = completed_keys(raw_path)

    jobs = []
    # task-major ordering keeps each task's requests contiguous, which makes the per-task
    # wall-clock window (used for Efficiency, Sec. 3.3(4)) well defined.
    for task, samples in bench.items():
        for rnd in range(rounds):
            for s in samples:
                if (task, s["id"], rnd) not in done:
                    jobs.append((rnd, task, s))
    print(f"pending requests: {len(jobs)} (concurrency={concurrency})", flush=True)

    fh = open(raw_path, "a", encoding="utf-8")
    t0 = time.perf_counter()
    n_done = n_err = 0
    task_wall: dict[str, float] = {}

    def work(job):
        rnd, task, s = job
        return rnd, task, s, *client.chat(build_messages(s, ner_cue=ner_cue))

    try:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            for rnd, task, s, content, dt, err, usage in pool.map(work, jobs):
                score, norm = score_sample(s, content) if err is None else (0.0, "")
                if err is not None:
                    n_err += 1
                row = {
                    "model": model, "task": task, "sample_id": s["id"], "round": rnd,
                    "output": content, "normalized": norm, "score": score, "error": err,
                    "latency_s": round(dt, 4), "completion_tokens": usage.get("completion_tokens"),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "finish_reason": usage.get("finish_reason"),
                    "wall_s": round(time.perf_counter() - t0, 4),
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                task_wall[task] = task_wall.get(task, 0.0) + dt
                n_done += 1
                if n_done % 100 == 0:
                    el = time.perf_counter() - t0
                    print(f"  [{n_done}/{len(jobs)}] {el:.0f}s elapsed, {n_done/el:.2f} req/s"
                          f"{f', {n_err} errors' if n_err else ''}", flush=True)
    finally:
        fh.close()
    el = time.perf_counter() - t0
    print(f"done: {n_done} requests in {el:.1f}s wall ({n_done/el:.2f} req/s), errors={n_err}")
    summary = {"model": model, "base_url": base_url, "requests": n_done,
               "errors": n_err, "wall_s": round(el, 2), "rounds": rounds,
               "thinking_enabled": thinking, "ner_cue": ner_cue,
               "sampling": {"temperature": 0.7, "top_p": 0.95, "top_k": 50,
                            "repetition_penalty": 1.1, "max_tokens": 2048},
               "req_per_s_over_batch": round(n_done / el, 4),
               "task_cumulative_latency_s": {t: round(v, 2) for t, v in task_wall.items()}}
    with open(os.path.join(out_dir, f"{model}.runlog.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--out-dir", default=RESULTS_DIR)
    ap.add_argument("--tasks", default=",".join(TASK_ORDER))
    ap.add_argument("--rounds", type=int, default=R_ROUNDS)
    ap.add_argument("--limit", type=int, default=None, help="limit samples per task (smoke test)")
    ap.add_argument("--thinking", action="store_true",
                    help="keep the model's chain of thought enabled (default: disabled, because the "
                         "task prompts demand the core answer only and CoT exhausts the token budget)")
    ap.add_argument("--ner-cue", choices=["paper", "open"], default="paper",
                    help="Geo-NER answer cue: 'paper' reproduces Listing A-3 verbatim (ends with "
                         "Answer:[]), 'open' drops the priming brackets (sensitivity check)")
    a = ap.parse_args()
    run(a.model, a.base_url, a.concurrency, a.out_dir, a.tasks.split(","), a.rounds, a.limit,
        a.thinking, a.ner_cue)
