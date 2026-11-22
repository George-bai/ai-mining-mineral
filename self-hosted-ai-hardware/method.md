# Method

`calculate.mjs` is the whole model; this file explains it. Sizes are decimal GB, bandwidth GB/s, speeds tokens/s. Cards
and RAM modules are sold in GiB, so both are converted (128 GiB of RAM is 137.4 GB) before they are compared.

## Memory

- **Whole-model stacks** (SGLang, vLLM, llama.cpp): weights + per stream (fixed state + context × KV bytes per token)
  + 1.6 GB per card for the runtime must fit the main cards' VRAM. KV per token: Qwen3.8-27B 32 KiB in FP8 (SGLang)
  or 64 KiB in F16 (llama.cpp) for its 16 full-attention layers, plus 0.16 GB of DeltaNet state per stream; Gemma 4
  26B-A4B 10/20 KiB for its 5 global layers plus a 1,024-token sliding window; Gemma 4 31B 80 KiB plus 0.8 GB.
- **Expert stacks** (Strata, Project Maya): the dense weights, the resident part of the context and 1.6 GB per card stay
  in VRAM; the rest of VRAM caches routed experts. Strata pins every expert in RAM and needs RAM ≥ experts + about
  10 GB; Maya keeps in RAM only the experts the cards do not hold, plus 16 GB for the system. The lookup tables (Qwen's
  n-gram table, DeepSeek's Engram) stay on the SSD. The context: Strata keeps a 64K window in VRAM and the rest of a
  longer context in pinned RAM (about 12.5 KB a token for Qwen3.8-Flash-Next); its DeepSeek engine keeps the whole cache
  in VRAM, about 1.3 KB a token per conversation (0.17 GB at 128K, 0.68 GB at 512K, 9.47 GB for seven more at 1M, in
  its `DEEPSEEK41.md`). Maya keeps a 32K window in VRAM and, once a context is longer than that, each stream's whole
  cache in pinned RAM (`SETTINGS.md`, v1.1.63): 544 bytes a token in each of GLM's 11 full-attention layers (5,984
  bytes a token; 0.78 GB at 128K, 6.3 GB at 1M per stream), about 1.1 KB a token for DeepSeek.
- The tools card's 16 GB never joins the pool. It takes a slot, 70 W and A$2,299.
- A configuration that is short of RAM would read experts from the SSD. It still runs, far slower; the calculator
  says so and does not estimate it.

## Writing speed (decode)

One stream, whole-model stacks:

    t = (bytes read per token + attention × context × KV bytes per token) / (card bandwidth × eff) + latency

Bytes read per token are the language weights (not the vision tower or an MTP block), times the active share for
Gemma 4 26B-A4B (15%). With tensor parallel (SGLang, vLLM) bandwidth grows by 0.75 per extra card; llama.cpp splits by
layers, so one stream gains nothing from a second card.

One stream, expert stacks:

    c = share of routed experts the free VRAM holds;  h = 1 − (1 − c)^β   (hot experts are asked for far more often)
    t = max(GPU time, CPU time) + latency;  GPU = (dense + routed per token × h) / (card bandwidth × eff)
                                            CPU = routed per token × (1 − h) / (RAM bandwidth × ramEff)
    speed = drafting gain / (t × (1 + longCtx × context / 1M))

Routed bytes per token = experts × (experts used ÷ experts per layer): 10/512 for Qwen3.8-Flash-Next, 8/288 for
GLM-5.3-Flash, 6/384 for DeepSeek-V4.1. The drafting gain is Strata's always-on MTP (with an extra term that grows when
every expert is in VRAM), Maya's MTP with two or more cards, and Maya's DSpark for DeepSeek on one card (64.5 → 72.3
tokens/s in issue 737). RAM bandwidth is the theoretical figure of the populated channels.

## Several streams

Each stream keeps 1 / (1 + κ(n − 1)) of the one-stream speed. For the whole-model servers κ is the median of matched
sweep pairs: a run with n streams counts only against a one-stream run from the same sweep, on the same cards and
drafter, at a context within a quarter of its own (`k.sweeps` in `calibration.mjs` gives the number of pairs). It is
0.35 for llama.cpp (a published 5090 sweep), and for the expert stacks
κ = κ₀ + (1 − κ₀)(1 − h): about 0.45-0.5 when every expert is in VRAM (Strata's 2 × A6000 and 4 × R9700 sweeps, Maya on
2 × PRO 5000), approaching 1 when most experts run on the CPU, where extra slots buy waiting time and no speed
(Strata's RTX 5070 sweep). The maximum streams shown is the largest n that keeps the reader's target speed, fits in
memory and stays within the stack's slots (8 per card for Strata's Qwen engine, 8 per engine for its DeepSeek engine
on one card or two, 8 for Maya). A machine that cannot be built (cards, slots, width, power or a head split the
software refuses) shows no capacity at all. The curve on the page recomputes
memory, the expert cache and contention at every stream count, and marks the counts that no longer fit.

Each card's PCIe link is the slower of the card and its slot: 13, 26 or 52 GB/s for PCIe 3, 4 or 5 x16, halved when
two cards share a desktop's CPU lanes (x8/x8). Cards wider than two slots are refused in pairs: no checked board and
case takes two of them beside the tools card. The batching servers split each layer's attention heads evenly across
the cards: Gemma 4 26B-A4B has 16 heads (8 KV) and Qwen3.8-27B 24 (4 KV), so neither runs on three cards (vLLM 0.33.0
checks the heads; the KV heads must divide the split); the GGUF runner splits by layers and can. Power is checked
against 90% of the host's power supply.

## Reading speed (prefill)

    t = pa × active parameters × (AMD factor) / (tensor index × cards^pScale) + pb × (1 − c) × experts / (PCIe × cards)
    speed = 1 / (t × (1 + context / pLen))

The tensor index is the card's dense FP16 tensor throughput with FP16 accumulate (half its dense INT8 rate), used only
as a relative figure. AMD cards read prompts slower than that index suggests in these stacks; the fit gives a factor
for each stack (`amd` in `calibration.mjs`). DeepSeek's model card gives 8B active parameters for reading a prompt and
16B for writing. The calculator keeps 16B for both: refitted with 8B for reading, the held-out reading gap grew from
30% to 34% for Strata and from 48% to 54% for Maya (20 Nov 2026), so 16B stays as the fitted cost index, not as a
count of the parameters used. Reading speed is the least certain output: see the held-out gaps in the
README.

## Fitting

`fit.mjs` minimises the squared log error between each run and the model, per stack, with a Nelder-Mead search:
writing speed on runs with one stream; reading speed on one-stream cold-prompt runs with prompts of 1,024 tokens or
more (shorter prompts measure start-up, not reading). Runs from a single user's machine are used as reported.

The band comes from held-out runs, not the fitted ones. The runs are split into five groups by machine (card, count
and host); each group is predicted by a fit to the other four, and the page's band is the 10th to 90th percentile of
measured ÷ estimated on those predictions, at least ±15%. With fewer than eight held-out runs, or runs from fewer than
three machines, the band is at least ±30% and widened to what the held-out runs show: an unvalidated band.

Fixed rather than fitted: RAM efficiency
0.65 for Strata (its own measurement: the CPU pool reads at 84-97% of measured RAM bandwidth), Maya's hit-rate exponent
β = 6 (the data cannot separate values from 2 to 30; median gap 23-27% across that range), and the concurrency values
above. A run more than 2.5× from the first fit is an outlier: listed, not used in the second fit.

Before fitting, a run is kept as evidence only (`fit: false` with a reason) when it ran on a card outside this
article (pre-Ampere, datacenter, unified-memory), mixed cards or a helper APU; used a non-default drafter or Turbo;
had capped clocks; had too little RAM for its pack (experts from the SSD); needed more VRAM than its cards have for a
whole-model stack (some layers or cache must have been offloaded, which the record does not say); or was faster than
the cards' memory allows without a drafter or batching (mislabelled).

## What it leaves out

Answer quality; the tools card's own load; queueing and network time; images in prompts; prefix-cache hits (all
reading speeds are for cold prompts); thermal throttling in a hot site room; NUMA effects on two-socket hosts.
