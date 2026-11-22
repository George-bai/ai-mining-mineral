"""MineralBench metric definitions (paper Sec. 3.3) and hyper-parameters (Sec. 4.2).

Rounds R = 3; alpha_IC = 0.5; gamma_GS = 0.5; gamma_ST = 2.0.
Task weights: general tasks 1, core domain tasks 2.
Composite metric weights: Acc 2, IC 1, ST 1, Eff 1.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

R_ROUNDS = 3
ALPHA_IC = 0.5
GAMMA_GS = 0.5
GAMMA_ST = 2.0

TASK_WEIGHTS_DEFAULT = {
    "ARC-Challenge": 1, "Math": 1, "MMLU-Sci": 1,
    "Mineral-Term": 2, "Mineral-Property": 2, "Geo-NER": 2,
}
METRIC_WEIGHTS = {"Acc": 2, "IC": 1, "ST": 1, "Eff": 1}

# Inference settings, Table 4 of the paper.
INFERENCE = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 50,
    "repetition_penalty": 1.1,
    "max_tokens": 2048,
    "max_retries": 2,
}

TASK_ORDER = ["Mineral-Term", "Mineral-Property", "Geo-NER"]


# ----------------------------------------------------------------------------------
# sample -> metric records
# ----------------------------------------------------------------------------------
def sample_scores(records: list[dict]) -> dict[str, dict[str, float]]:
    """records: rows with model, task, sample_id, round, score. -> {(model,task): {sid: mean}}"""
    acc: dict[tuple, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        acc[(r["model"], r["task"])][r["sample_id"]].append(r["score"])
    return {k: {sid: sum(v) / len(v) for sid, v in d.items()} for k, d in acc.items()}


def task_accuracy(mean_scores: dict[str, float]) -> float:
    if not mean_scores:
        return 0.0
    return sum(mean_scores.values()) / len(mean_scores) * 100.0


def inter_round_consistency(round_norms: list[list[str]]) -> float:
    """IC_q = alpha*ECR_q + (1-alpha)*SCR_q for one sample (list of rounds of normalised output)."""
    r = len(round_norms)
    if r < 2:
        return 1.0
    ecr = max(Counter(round_norms).values()) / r
    total, pairs = 0.0, 0
    for i in range(r):
        for j in range(i + 1, r):
            a, b = set(round_norms[i].split()), set(round_norms[j].split())
            if not a and not b:
                s = 1.0
            elif not a or not b:
                s = 0.0
            else:
                s = len(a & b) / len(a | b)
            total += s
            pairs += 1
    scr = total / pairs if pairs else 1.0
    return ALPHA_IC * ecr + (1 - ALPHA_IC) * scr


def task_ic(ic_by_sample: list[float]) -> float:
    return (sum(ic_by_sample) / len(ic_by_sample) * 100.0) if ic_by_sample else 0.0


def stdev(xs: list[float]) -> float:
    if not xs:
        return 0.0
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def general_stability(accs: list[float]) -> tuple[float, float, float]:
    """-> (mu, sigma, GS = mu - gamma_GS*sigma)"""
    mu = sum(accs) / len(accs) if accs else 0.0
    sigma = stdev(accs)
    return mu, sigma, mu - GAMMA_GS * sigma


def auxiliary_stability(sigma: float) -> float:
    return 100.0 - GAMMA_ST * sigma


def weighted_task_metric(task_vals: dict[str, float], weights: dict[str, int]) -> float:
    num = sum(task_vals[t] * weights.get(t, 1) for t in task_vals)
    den = sum(weights.get(t, 1) for t in task_vals)
    return num / den if den else 0.0


def efficiency(completed: dict[str, tuple[int, float]]) -> tuple[float, dict[str, float]]:
    """completed: task -> (K requests, wall seconds). Overall Eff = sum K / sum tau (req/s)."""
    per_task = {t: (k / tau if tau > 0 else 0.0) for t, (k, tau) in completed.items()}
    tot_k = sum(k for k, _ in completed.values())
    tot_tau = sum(tau for _, tau in completed.values())
    return (tot_k / tot_tau if tot_tau > 0 else 0.0), per_task


def normalize_efficiency(raw: dict[str, float]) -> dict[str, float]:
    """Eff_norm = 100 / (1 + log10(max Eff / Eff_m)); the fastest model scores 100."""
    mx = max(raw.values()) if raw else 0.0
    out = {}
    for m, e in raw.items():
        if e <= 0:
            out[m] = 0.0
        else:
            out[m] = 100.0 / (1.0 + math.log10(mx / e))
    return out


def composite(acc: float, ic: float, st: float, eff_norm: float) -> float:
    w = METRIC_WEIGHTS
    return (w["Acc"] * acc + w["IC"] * ic + w["ST"] * st + w["Eff"] * eff_norm) / sum(w.values())


def oracle(models: list[str], mean_by_model_task: dict[tuple, dict[str, float]],
           tasks: list[str], weights: dict[str, int]) -> dict[str, float]:
    """Oracle_t = mean over samples of max over models of the round-averaged score (paper Sec. 3.3(6))."""
    out = {}
    for t in tasks:
        per_model = [mean_by_model_task.get((m, t), {}) for m in models]
        sids = set().union(*[set(d) for d in per_model]) if per_model else set()
        if not sids:
            out[t] = 0.0
            continue
        tot = 0.0
        for sid in sids:
            tot += max((d.get(sid, 0.0) for d in per_model), default=0.0)
        out[t] = tot / len(sids) * 100.0
    out["_weighted"] = weighted_task_metric({t: out[t] for t in tasks}, weights)
    return out
