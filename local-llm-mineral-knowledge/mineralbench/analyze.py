"""Evaluator module: aggregate raw run records into the MineralBench metric set (Sec. 3.3).

Reads results/<model>.raw.jsonl and writes results/metrics.json + results/tables.md.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
from collections import defaultdict

from .metrics import (TASK_ORDER, TASK_WEIGHTS_DEFAULT, auxiliary_stability, composite,
                      efficiency, general_stability, inter_round_consistency, oracle,
                      normalize_efficiency, sample_scores, task_accuracy, task_ic,
                      weighted_task_metric)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(HERE, "results")


def load_raw(results_dir: str, models: list[str] | None = None) -> list[dict]:
    rows = []
    for fn in sorted(os.listdir(results_dir)):
        if not fn.endswith(".raw.jsonl"):
            continue
        model = fn[: -len(".raw.jsonl")]
        if models and model not in models:
            continue
        for line in open(os.path.join(results_dir, fn), encoding="utf-8"):
            if line.strip():
                rows.append(json.loads(line))
    return rows


def analyse(rows: list[dict], weights: dict[str, int] | None = None) -> dict:
    weights = weights or TASK_WEIGHTS_DEFAULT
    ok = [r for r in rows if r.get("error") is None]
    models = sorted({r["model"] for r in ok})
    tasks = [t for t in TASK_ORDER if any(r["task"] == t for r in ok)]

    # ---- per-sample round averages, Accuracy -------------------------------------------
    means = sample_scores(ok)                      # {(model, task): {sid: mean score}}
    acc_by_task = {m: {t: task_accuracy(means.get((m, t), {})) for t in tasks} for m in models}
    acc_weighted = {m: weighted_task_metric(acc_by_task[m], weights) for m in models}

    # ---- Inter-round Consistency --------------------------------------------------------
    norms: dict[tuple, dict[str, dict[int, str]]] = defaultdict(lambda: defaultdict(dict))
    for r in ok:
        norms[(r["model"], r["task"])][r["sample_id"]][r["round"]] = r.get("normalized", "")
    ic_by_task, ic_samples = {}, {}
    for m in models:
        ic_by_task[m] = {}
        for t in tasks:
            vals = []
            for sid, rounds in norms.get((m, t), {}).items():
                ordered = [rounds[k] for k in sorted(rounds)]
                if len(ordered) >= 2:
                    vals.append(inter_round_consistency(ordered))
            ic_by_task[m][t] = task_ic(vals)
            ic_samples[(m, t)] = vals

    # ---- Efficiency ----------------------------------------------------------------------
    # Paper Sec.3.3: Eff_t = K_t / tau_t, where tau_t is the *cumulative* time of the completed
    # requests. That is the paper-literal measure (concurrency-independent, comparable across
    # models run with different client parallelism). We also record raw wall-clock throughput.
    eff_raw, eff_task, latency, diag = {}, {}, {}, {}
    for m in models:
        per_task_counts, per_task_lat, per_task_wall = defaultdict(int), defaultdict(list), {}
        for t in tasks:
            trows = [r for r in ok if r["model"] == m and r["task"] == t]
            if not trows:
                continue
            per_task_counts[t] = len(trows)
            per_task_lat[t] = [r.get("latency_s", 0.0) for r in trows]
            lo = min(r.get("wall_s", 0.0) for r in trows)
            hi = max(r.get("wall_s", 0.0) for r in trows)
            per_task_wall[t] = max(hi - lo, 1e-9)
        tot_k = sum(per_task_counts.values())
        tot_tau = sum(sum(v) for v in per_task_lat.values())
        eff_raw[m] = tot_k / tot_tau if tot_tau else 0.0
        eff_task[m] = {t: (1.0 / statistics.fmean(v) if v else 0.0)
                       for t, v in per_task_lat.items()}
        all_lat = [x for v in per_task_lat.values() for x in v]
        throughput = tot_k / sum(per_task_wall.values()) if per_task_wall else 0.0
        latency[m] = {
            "mean_s": round(statistics.fmean(all_lat), 3) if all_lat else 0.0,
            "p50_s": round(statistics.median(all_lat), 3) if all_lat else 0.0,
            "p95_s": round(statistics.quantiles(all_lat, n=20)[18], 3) if len(all_lat) > 20 else 0.0,
            "cumulative_s_by_task": {t: round(sum(v), 1) for t, v in per_task_lat.items()},
            "wall_s_by_task": {t: round(v, 1) for t, v in per_task_wall.items()},
            "throughput_req_s_by_task": {t: round(per_task_counts[t] / per_task_wall[t], 3)
                                         for t in per_task_wall},
            "throughput_req_s_overall": round(throughput, 3),
        }
        all_rows = [r for r in rows if r["model"] == m]
        empty = sum(1 for r in all_rows if not (r.get("normalized") or "").strip())
        trunc = sum(1 for r in all_rows if r.get("finish_reason") == "length")
        diag[m] = {
            "requests": len(all_rows),
            "errors": sum(1 for r in all_rows if r.get("error")),
            "empty_or_unparseable": empty,
            "empty_rate_pct": round(100 * empty / max(len(all_rows), 1), 2),
            "finish_reason_length": trunc,
            "finish_reason_length_pct": round(100 * trunc / max(len(all_rows), 1), 2),
            "completion_tokens_mean": round(
                statistics.fmean([r.get("completion_tokens") or 0 for r in all_rows]), 1)
                if all_rows else 0,
        }

    # ---- GS / ST / normalised Efficiency / composite ------------------------------------
    model_metrics = {}
    for m in models:
        accs = [acc_by_task[m][t] for t in tasks]
        mu, sigma, gs = general_stability(accs)
        st = auxiliary_stability(sigma)
        model_metrics[m] = {
            "Acc_weighted": acc_weighted[m],
            "IC": weighted_task_metric(ic_by_task[m], weights),
            "mu": mu, "sigma": sigma, "GS": gs, "ST": st,
            "Acc_by_task": acc_by_task[m], "IC_by_task": ic_by_task[m],
            "Eff_req_s": eff_raw[m], "Eff_by_task_req_s": eff_task[m],
            "latency": latency[m], "diagnostics": diag[m],
        }
    eff_norm = normalize_efficiency({m: model_metrics[m]["Eff_req_s"] for m in models})
    for m in models:
        model_metrics[m]["Eff_norm"] = eff_norm[m]
        model_metrics[m]["Score_composite"] = composite(
            model_metrics[m]["Acc_weighted"], model_metrics[m]["IC"],
            model_metrics[m]["ST"], eff_norm[m])

    orc = oracle(models, means, tasks, weights)
    return {"models": models, "tasks": tasks, "weights": weights,
            "per_model": model_metrics, "oracle": orc}


def to_markdown(res: dict) -> str:
    models, tasks = res["models"], res["tasks"]
    lines = ["## Task Accuracy (0-100)", "",
             "| Model | " + " | ".join(tasks) + " | Weighted-Acc |",
             "|" + "---|" * (len(tasks) + 2)]
    for m in models:
        pm = res["per_model"][m]
        lines.append("| " + m + " | " + " | ".join(f"{pm['Acc_by_task'][t]:.2f}" for t in tasks)
                     + f" | **{pm['Acc_weighted']:.2f}** |")
    lines += ["", f"| Oracle (pool = {', '.join(models)}) | " +
              " | ".join(f"{res['oracle'][t]:.2f}" for t in tasks) +
              f" | **{res['oracle']['_weighted']:.2f}** |"]
    lines += ["", "## Multidimensional metrics", "",
              "| Model | Acc_m | IC_m | GS_m | ST_m | Eff (req/s) | Eff_norm | Score_composite |",
              "|---|---|---|---|---|---|---|---|"]
    for m in models:
        pm = res["per_model"][m]
        lines.append(f"| {m} | {pm['Acc_weighted']:.2f} | {pm['IC']:.2f} | {pm['GS']:.2f} | "
                     f"{pm['ST']:.2f} | {pm['Eff_req_s']:.3f} | {pm['Eff_norm']:.2f} | "
                     f"**{pm['Score_composite']:.2f}** |")
    lines += ["", "## Inter-round Consistency by task", "",
              "| Model | " + " | ".join(tasks) + " |", "|" + "---|" * (len(tasks) + 1)]
    for m in models:
        pm = res["per_model"][m]
        lines.append("| " + m + " | " + " | ".join(f"{pm['IC_by_task'][t]:.2f}" for t in tasks) + " |")
    lines += ["", "## Run diagnostics", "",
              "| Model | requests | errors | empty/unparseable | finish_reason=length | mean latency s |",
              "|---|---|---|---|---|---|"]
    for m in models:
        d = res["per_model"][m]["diagnostics"]
        lat = res["per_model"][m]["latency"]
        lines.append(f"| {m} | {d['requests']} | {d['errors']} | {d['empty_or_unparseable']} "
                     f"({d['empty_rate_pct']}%) | {d['finish_reason_length']} "
                     f"({d['finish_reason_length_pct']}%) | {lat['mean_s']} |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default=RESULTS)
    ap.add_argument("--models", default=None)
    a = ap.parse_args()
    rows = load_raw(a.results_dir, a.models.split(",") if a.models else None)
    if not rows:
        raise SystemExit("no raw results found")
    res = analyse(rows)
    with open(os.path.join(a.results_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    md = to_markdown(res)
    with open(os.path.join(a.results_dir, "tables.md"), "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
