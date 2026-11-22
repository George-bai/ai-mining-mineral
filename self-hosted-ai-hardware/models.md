# Models and quantised files

Checked 15 November 2026 (Brisbane). Only quantised files are offered: the original weights of these models are too
large for a site machine. Sizes are decimal GB. For every GGUF pack the split into routed experts, dense weights and
lookup tables was read from the files' own headers (tensor offsets, by HTTP range request; no weights downloaded).
That split is what the calculator places in VRAM, RAM or SSD.

## The six models

| Model | Size | Native context | Licence | Card |
|---|---|---:|---|---|
| Qwen3.8-27B | 27B dense (16 full-attention + 48 DeltaNet layers) | 262,144 | Apache-2.0 | [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) |
| Gemma 4 26B-A4B | 25.2B mixture of experts, 3.8B active | 262,144 | Apache-2.0 | [google/gemma-4-26B-A4B-it](https://huggingface.co/google/gemma-4-26B-A4B-it) |
| Gemma 4 31B | 30.7B dense | 262,144 | Apache-2.0 | [google/gemma-4-31B-it](https://huggingface.co/google/gemma-4-31B-it) |
| Qwen3.8-Flash-Next | 125B mixture of experts, 6B active, plus a 51B n-gram table and a 4B MTP block | 262,144 (1M with YaRN, not offered) | Qwen Community 1.0 | [Qwen/Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) |
| GLM-5.3-Flash | 320B mixture of experts, 18B active; 288 experts per layer, 8 used | 1,048,576 | MIT | [zai-org/GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) |
| DeepSeek-V4.1-Flash-1017 | 552B mixture of experts plus a 196B Engram table; 8B active reading, 16B writing; 384 experts per layer, 6 used | 1,048,576 | MIT | [deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) |

DeepSeek-V4.1-Flash-1017 is the newest DeepSeek Flash on 15 November 2026 (published 17 October; the only later
commit adds a chat template). Gemma 4 also has E2B, E4B and an encoder-free 12B; they are small enough for the tools
card and are not sized here.

## The files offered on the page

| Model | Stack | File set (pinned revision) | Routed experts | Dense | Lookup table | Per token reads |
|---|---|---|---:|---:|---:|---|
| Qwen3.8-27B | SGLang | [RadixArk NVFP4, BF16 head](https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead/tree/009632fef96dd349150baa780c984e62e70e91fe) | — | 23.749 (whole model) | — | all weights |
| Qwen3.8-27B | llama.cpp | [Unsloth UD-Q4_K_M](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/4af51b3542f775b0a8e4b310bfb3f17e01c306c9) | — | 16.564 | — | all weights |
| Gemma 4 26B-A4B | vLLM | [NVIDIA NVFP4](https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4/tree/a19cfe00be84568a6867111c9a68c9c44fdcffe6) | — | 18.788 | — | about 15% |
| Gemma 4 26B-A4B | llama.cpp | [Unsloth UD-Q4_K_M](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/tree/c099eb48e663fd284577b04978a94ffccb261841) | — | 16.948 | — | about 15% |
| Gemma 4 31B | llama.cpp | [Unsloth Q4_K_M](https://huggingface.co/unsloth/gemma-4-31B-it-GGUF/tree/c1ac76e99d5513b141e8adde7288b85c3f9c32ec) | — | 18.324 | — | all weights |
| Qwen3.8-Flash-Next | Strata | [ISTA-DASLab GSQ-RCO IQ3_S](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) | 50.292 | 4.514 | 28.800 | 10 of 512 experts |
| Qwen3.8-Flash-Next | Strata | ISTA-DASLab GSQ-RCO IQ3_XXS (same revision) | 42.913 | 4.116 | 28.800 | 10 of 512 |
| Qwen3.8-Flash-Next | Strata | [Unsloth UD-Q4_K_XL](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/f5d175de2cf7f720d45d6064019a81fcf056e986) | 76.99 (71.7 GiB) | about 4.8 | 28.800 | 10 of 512 |
| GLM-5.3-Flash | Project Maya | [Maya-S (v2, IQ2_XXS mix)](https://huggingface.co/peasantsmith/GLM-5.3-Flash-Maya-GGUF/tree/5ca1df1d2436bd1ab270b169c5ea6c47aad23641) | 88.653 | 7.806 | — | 8 of 288 |
| GLM-5.3-Flash | Project Maya | Maya-M (IQ2_S mix, same revision) | 108.188 | 7.806 | — | 8 of 288 |
| GLM-5.3-Flash | Project Maya | Maya-XS (IQ1_S mix, same revision) | 67.363 | 6.039 | — | 8 of 288 |
| DeepSeek-V4.1-Flash-1017 | Project Maya | [Maya-XS v2](https://huggingface.co/peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF/tree/928ffcc3b0497f1d2f356d87ed17a1b8641bd382) | 109.566 | 6.933 | 161.619 | 6 of 384 |
| DeepSeek-V4.1-Flash-1017 | Project Maya | Maya-S (same revision) | 169.020 | 8.833 | 161.619 | 6 of 384 |
| DeepSeek-V4.1-Flash-1017 | Strata | [ISTA-DAS GSQ-RCO 2.00 bpw (IQ2_XXS)](https://huggingface.co/ISTA-DASLab/DeepSeek-V4.1-Flash-1017-GSQ-RCO-GGUF/tree/65d53bc8be65123e255ff02f3ded958b6dbf54fd) | 132.073 | 5.943 | 110.595 (IQ4_NL Engram) | 6 of 384 |
| DeepSeek-V4.1-Flash-1017 | Strata | ISTA-DAS GSQ-RCO 2.25 bpw (IQ2_XS, same revision) | 149.060 | 5.943 | 110.595 | 6 of 384 |

"Dense" includes the token embedding. The lookup tables (Qwen's n-gram table, DeepSeek's Engram) stay on the SSD in
both stacks and are read a few rows per token: they need disk space, not RAM.

## What is altered and what is not

- Every pack above keeps all of its model's experts (expert counts in the headers match the originals: 512, 288,
  384). They are quantisations, not pruned or retrained models.
- Left out of the page: ISTA-DAS Coder packs (half the experts removed), abliterated and "Derisked" weight edits,
  CYBER-FROST, and Swift 1.5 (a fine-tune). Runs on Derisked, abliterated and Swift files are still used to fit
  speed, because their tensors and sizes match the originals; they are marked in `anchors.json`.
- Both Maya repositories added a refusal-ablation direction file on 12 November 2026; Maya's switch for it is off by
  default and must stay off for unaltered answers. Maya's Turbo and Strata's "Faster" (five of six DeepSeek experts)
  change the computation and are treated as altered settings.
- The non-commercial DFlash2 drafter (CC BY-NC-ND 4.0) is excluded; MTP and DSpark drafting are part of the model
  releases and are used where the stack turns them on by default.

## Answer quality, as the quantisers report it

Speed is what the calculator estimates; these are the quantisers' own scores against the original weights, not
checked here. GLM-5.3-Flash ([Maya README](https://huggingface.co/peasantsmith/GLM-5.3-Flash-Maya-GGUF/blob/main/README.md),
against FP8): ARC-Challenge 71.0 for the original, 69.0 for Maya-M, 68.2 for Maya-S and 61.5 for Maya-XS; the
five-test average keeps 97.9%, 97.9% and 92.4%. DeepSeek-V4.1-Flash-1017 ISTA-DAS 2.00 and 2.25 bpw keep 100% and 99.8%
of the task average ([card](https://huggingface.co/ISTA-DASLab/DeepSeek-V4.1-Flash-1017-GSQ-RCO-GGUF#results));
Qwen3.8-Flash-Next IQ3_XXS keeps 99.4%. No comparable figures were found for the other packs.

## Not offered, and why

- Gemma 4 31B NVFP4 (`nvidia/Gemma-4-31B-IT-NVFP4`): 32.6 GB on disk and tested by NVIDIA on H100 with eight-way
  tensor parallel; not a small-site option.
- Qwen3.8-27B or Gemma on Strata or Maya: neither stack supports them.
- DeepSeek-V4.1 Unsloth UD-Q4_K_XL on llama.cpp: its 202.8 GB lookup table is MXFP8, which mainline llama.cpp does not
  support yet (llama.cpp issue 31385, open on 15 November 2026: "loads now, but outputs gibberish").
- GLM-5.3-Flash and DeepSeek NVFP4 checkpoints for vLLM/SGLang: validated on datacenter Blackwell (B200/GB300) at
  sizes of 198 to 429 GB, beyond a single-site budget.
