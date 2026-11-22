# Hosting stacks

Checked 15 November 2026 (Brisbane). The article page describes each stack by how it places the model; this file
names them. Each model is offered on the stacks that run it best; the calculator picks the fastest that fits the
chosen machine.

| Model | Offered on | Why |
|---|---|---|
| Qwen3.8-Flash-Next | Strata | Built for this model: experts in RAM, the busiest cached in VRAM, the n-gram table on the SSD, MTP drafting on. |
| GLM-5.3-Flash | Project Maya | An engine written for GLM-5.3-Flash with VRAM, RAM and SSD expert tiers and placement calibration. |
| DeepSeek-V4.1-Flash-1017 | Project Maya or Strata | Both have a DeepSeek engine (Strata's is ported from Maya's, MIT). Maya's own quants and ISTA-DAS sets differ in size. |
| Qwen3.8-27B | SGLang (Blackwell, NVFP4) or llama.cpp (any card) | A dense model that fits whole in VRAM: a batching server serves many streams; the expert stacks do not support it. |
| Gemma 4 26B-A4B | vLLM (Blackwell, NVFP4) or llama.cpp | As above. |
| Gemma 4 31B | llama.cpp | The NVFP4 checkpoint has no first-hand run to calibrate it (see models.md). |

## The stacks

**Strata** ([Niko1221/Strata](https://github.com/Niko1221/Strata), MIT). App and Terminal 0.2.13, released 9 November
2026, with Control and engines 0.1.59 (0.2.13.1 the same day added Control 0.1.59.1, an Intel Arc set-up fix).
Families: Qwen3.8-Flash-Next, DeepSeek-V4.1-Flash-1017, Qwen3.6-35B-A3B. NVIDIA RTX 20 to 50 series, AMD RDNA3/RDNA4
including the Radeon AI PRO R9700 (Linux), Intel Arc (Linux), Apple Silicon.
- Placement (Qwen): every expert pinned in RAM; attention, DeltaNet, shared experts, head, MTP layer and the KV cache in
  VRAM, with the rest of VRAM an adaptive expert cache; the 28.8 GB n-gram table on the SSD. It fits when RAM is at
  least the experts plus about 10 GB ([MODELS.md](https://github.com/Niko1221/Strata/blob/v0.2.13/docs/MODELS.md)).
  From 64K the KV cache keeps its most-read part in VRAM and streams the rest from pinned RAM.
- Placement (DeepSeek): routed experts in VRAM as far as they fit, the rest computed on the CPU from RAM; dense
  weights split across cards; the Engram table on the SSD. Its planner budgets RAM for only the experts the cards do
  not hold, plus 9 GB for the engine and system (`strata_control/dsv41_fit.py` at d2f0964); short of that, the CPU
  reads some experts from the SSD and runs slower.
- Drafting: MTP on by default for Qwen ("1.6-1.8x sooner"); DSpark for DeepSeek where it measures a gain.
- Concurrency: one request at a time by default; `parallel` 2 to 8 slots, more on a layer split (8 per pipeline
  group). The DeepSeek engine takes at most 8 on one card or two: "A number above 8 is run as 8"
  ([DEEPSEEK41.md](https://github.com/Niko1221/Strata/blob/v0.2.13/docs/DEEPSEEK41.md#L150-L168)), where each extra
  conversation adds about 0.17 GB of VRAM at 128K and 0.68 GB at 512K. With experts mostly in RAM, slots buy waiting time, not throughput; with every expert in VRAM, four R9700
  cards served 32 requests at 369.6 tokens/s in total against 67.9 for one
  ([BATCHING.md](https://github.com/Niko1221/Strata/blob/v0.2.13/docs/BATCHING.md)).
- Context: Qwen up to 262,144; DeepSeek 8K by default, up to 1M on request, tested to 256K.
- Settings treated as altered: DeepSeek "Faster" (five of six experts per word; the default on cards of 16 GiB or less
  in total and on single R9700 cards). The calculator assumes all six.

**Project Maya** ([mw00/project-maya](https://github.com/mw00/project-maya), MIT). v1.1.63, released 14 November 2026.
GLM-5.3, GLM-5.3-Flash, DeepSeek-V4.1-Flash-1017 and MiniMax-M3.1-Flash, each with its own engine; Qwen3.8-Flash-Next
only as two third-party files. NVIDIA from V100/RTX 20, AMD, Windows; Metal experimental.
- Placement: the most-used experts in VRAM, the next in RAM, the rest read from the NVMe SSD, moved as the conversation
  changes. Memory guide: VRAM + RAM of 128 GB recommended for Maya-S, 160 GB for Maya-M, 88 GB for Maya-XS; DeepSeek
  Maya-XS 128 GB, Maya-S 224 GB, with the Engram tables always on the SSD
  ([MEMORY.md](https://github.com/mw00/project-maya/blob/main/docs/MEMORY.md)).
- Drafting: one GPU decodes without drafting; two or more use the model's own MTP block (GLM: 43.7 → 70.1 tokens/s
  on 4 × RTX 3090 in issue 349). DeepSeek keeps a per-slot DSpark drafter. The DFlash2 drafter is non-commercial
  (CC BY-NC-ND 4.0) and is left out here.
- Concurrency: `--parallel` 1 to 8; GLM decodes without DFlash2 above one slot. KV in INT8, 544 bytes a token in each
  of GLM's 11 full-attention layers; each conversation's whole cache lives in pinned RAM with 32K positions of it in
  VRAM ([SETTINGS.md](https://github.com/mw00/project-maya/blob/v1.1.63/docs/SETTINGS.md#L165-L166)).
- Context: up to 1M for GLM and DeepSeek.
- Settings treated as altered: Turbo (changes routing), the refusal-ablation switch.

**SGLang** 0.5.19 and **vLLM** 0.33.0 (released 2 November 2026). Whole model in VRAM with continuous batching; NVFP4
needs Blackwell (SM120: RTX 5090, RTX PRO 4500/5000/6000). SGLang's Qwen3.8-27B cookbook runs the RadixArk NVFP4
checkpoint single-GPU on RTX PRO 6000 and RTX 5090 (`--attention-backend flashinfer` on SM120) and recommends MTP
3/1/4. vLLM's Gemma 4 26B-A4B recipe validates NVIDIA's NVFP4 checkpoint on RTX PRO 6000 at TP1 with a specific
image. The calculator fits these servers without a drafter (most first-hand runs with a drafter are hard to compare);
MTP adds roughly 1.5 to 2 times for one stream and less under load.

**llama.cpp** (pin a tested build). Splits a GGUF model by layers across cards; CUDA, ROCm/HIP, Vulkan, SYCL. The broad
option for the dense models on non-Blackwell and AMD cards. For the big mixture-of-experts models with experts in RAM
(`--n-cpu-moe`) it is far slower than the expert stacks; see the comparison below.

## The measured comparison on the page

`stack-comparison.json` holds the two pairs drawn in section 03, with their conditions:

1. Qwen3.8-Flash-Next UD-Q4_K_XL on one Radeon AI PRO R9700 (225 W) and an EPYC 7452 with 8 channels of DDR4-2400,
   measured by Strata's author: Strata 63-88 tokens/s writing (story to code, MTP on), 1,110-1,320 reading a 32K
   prompt; llama.cpp 8bb3cf0d2 with `--n-cpu-moe 38-48`, 18-20 writing, 198-257 reading a 4K prompt.
2. GLM-5.3-Flash on R9700 cards, two community machines: Maya-S on 2 × R9700 (Core i5-13500, 96 GB DDR5), 45.2 tokens/s
   and 848 reading 8K ([issue 942](https://github.com/mw00/project-maya/issues/942)); llama.cpp IQ2_XXS on 3 × R9700
   (Ryzen 9 5950X, 64 GB), 15.3 tokens/s without drafting and 189 reading 2,107 tokens
   ([LocalMaxxing run](https://www.localmaxxing.com/en/runs/cmthqr0uw02bkp401m642nj76)).

Where every expert fits in VRAM the gap narrows: llama.cpp runs Qwen3.8-27B within 7% of the fitted bandwidth model.

## On a site network

Both expert stacks bind to 127.0.0.1 by default and offer API keys for a LAN bind; put TLS in a reverse proxy. Maya
checks for updates and can fetch models and image URLs; an air-gapped site needs those turned off. Neither provides
role-based multi-tenant access control: put the machine behind the site's own gateway.
