// Dated inputs for the hardware calculator, checked 15 November 2026 (Brisbane).
// File sizes are decimal GB, read from each pinned file set's GGUF headers (routed experts / dense / lookup table).
// Prices are AUD including GST unless a note says otherwise. Sources and reasoning: README.md, models.md, stacks.md, hardware.md.
export const checked = '2026-11-15';
export const BUDGET = 100000;

const hf = (repo, rev) => `https://huggingface.co/${repo}/tree/${rev}`;

export const stacks = {
  strata: {name: 'Strata', method: 'Expert cache: every expert in RAM, the busiest in VRAM', version: '0.2.13 · engine 0.1.59', url: 'https://github.com/Niko1221/Strata/releases/tag/v0.2.13',
    tiered: true, slots: 8, slotsPerGpu: true, vendors: ['nvidia', 'amd'],
    note: 'Experts in RAM, the most-used ones cached in VRAM, the lookup table on the SSD. MTP drafting is on by default.'},
  maya: {name: 'Project Maya', method: 'Expert tiers across VRAM, RAM and SSD', version: '1.1.63', url: 'https://github.com/mw00/project-maya/releases/tag/v1.1.63',
    tiered: true, slots: 8, vendors: ['nvidia', 'amd'],
    note: 'Experts tiered across VRAM, RAM and SSD. Native MTP or DSpark drafting where it helps; the non-commercial DFlash2 drafter is left off.'},
  sglang: {name: 'SGLang', method: 'Whole model in VRAM, batching server', version: '0.5.19', url: 'https://github.com/sgl-project/sglang', tiered: false, slots: 64, tensorParallel: true,
    vendors: ['nvidia'], blackwell: true, note: 'Whole model in VRAM; continuous batching. NVFP4 needs a Blackwell card.'},
  vllm: {name: 'vLLM', method: 'Whole model in VRAM, batching server', version: '0.33.0', url: 'https://github.com/vllm-project/vllm/releases/tag/v0.33.0', tiered: false, slots: 64, tensorParallel: true,
    vendors: ['nvidia'], blackwell: true, note: 'Whole model in VRAM; continuous batching. NVFP4 needs a Blackwell card.'},
  llamacpp: {name: 'llama.cpp', method: 'Whole model in VRAM, GGUF runner', version: 'pinned build', url: 'https://github.com/ggml-org/llama.cpp', tiered: false, slots: 16,
    vendors: ['nvidia', 'amd'], note: 'Whole model in VRAM, split by layers across cards. The broad option for non-Blackwell and AMD cards.'}
};

// kind 'tiered': dense weights + KV in VRAM, experts cached in VRAM and held in RAM, lookup table on SSD.
// kind 'resident': the whole quantised model in VRAM.
// Profiles are listed largest file first, the least compressed; answer quality is compared only where published (models.md).
// used = share of routed expert bytes read per token (top-k / experts per layer). active = billions of parameters per token.
// GLM cache: 544 bytes a token in each of its 11 full-attention layers (Maya SETTINGS.md, GLM5-FLASH.md, v1.1.63).
// DeepSeek on Strata: about 1.3 KB a token of VRAM per conversation (0.17 GB at 128K, 0.68 GB at 512K; DEEPSEEK41.md) and at
// most 8 conversations per engine, on one card or two. DeepSeek's card gives 8B active parameters
// for reading a prompt and 16B for writing; active stays 16, as a refit with 8 predicted held-out prompt speeds worse (method.md).
// heads = [attention, KV] heads of the pinned checkpoints' configs: a tensor-parallel split must divide them.
export const models = [
  {id: 'qwen27', short: 'Qwen 27B', name: 'Qwen3.8-27B', size: '27B dense', context: 262144, heads: [24, 4], licence: 'Apache-2.0', source: 'https://huggingface.co/Qwen/Qwen3.8-27B',
    profiles: [
      {id: 'qwen27-sglang', label: '4-bit NVFP4 · 24 GB', stack: 'sglang', quant: 'NVFP4 · RadixArk, BF16 head', kind: 'resident', weights: 23.749, read: 18.0, active: 27,
        kvToken: 32768, stateGB: 0.16, blackwell: true, source: hf('RadixArk/Qwen3.8-27B-NVFP4-BF16-LMHead', '009632fef96dd349150baa780c984e62e70e91fe')},
      {id: 'qwen27-llama', label: '4-bit GGUF · 17 GB', stack: 'llamacpp', quant: 'UD-Q4_K_M · Unsloth GGUF', kind: 'resident', weights: 16.564, active: 27,
        kvToken: 65536, stateGB: 0.16, source: hf('unsloth/Qwen3.8-27B-GGUF', '4af51b3542f775b0a8e4b310bfb3f17e01c306c9')}
    ]},
  {id: 'gemma26', short: 'Gemma 26B', name: 'Gemma 4 26B-A4B', size: '25.2B MoE · 3.8B active', context: 262144, heads: [16, 8], licence: 'Apache-2.0', source: 'https://huggingface.co/google/gemma-4-26B-A4B-it',
    profiles: [
      {id: 'gemma26-vllm', label: '4-bit NVFP4 · 19 GB', stack: 'vllm', quant: 'NVFP4 · NVIDIA', kind: 'resident', weights: 18.788, read: 17.6, active: 3.8, activeShare: 0.151,
        kvToken: 10240, stateGB: 0.1, blackwell: true, source: hf('nvidia/Gemma-4-26B-A4B-NVFP4', 'a19cfe00be84568a6867111c9a68c9c44fdcffe6')},
      {id: 'gemma26-llama', label: '4-bit GGUF · 17 GB', stack: 'llamacpp', quant: 'UD-Q4_K_M · Unsloth GGUF', kind: 'resident', weights: 16.948, active: 3.8, activeShare: 0.151,
        kvToken: 20480, stateGB: 0.2, source: hf('unsloth/gemma-4-26B-A4B-it-GGUF', 'c099eb48e663fd284577b04978a94ffccb261841')}
    ]},
  {id: 'gemma31', short: 'Gemma 31B', name: 'Gemma 4 31B', size: '30.7B dense', context: 262144, licence: 'Apache-2.0', source: 'https://huggingface.co/google/gemma-4-31B-it',
    profiles: [
      {id: 'gemma31-llama', label: '4-bit GGUF · 18 GB', stack: 'llamacpp', quant: 'Q4_K_M · Unsloth GGUF', kind: 'resident', weights: 18.324, active: 30.7,
        kvToken: 81920, stateGB: 0.8, source: hf('unsloth/gemma-4-31B-it-GGUF', 'c1ac76e99d5513b141e8adde7288b85c3f9c32ec')}
    ]},
  {id: 'qwen-next', short: 'Qwen Flash', name: 'Qwen3.8-Flash-Next', size: '125B MoE · 6B active', context: 262144, licence: 'Qwen Community 1.0', source: 'https://huggingface.co/Qwen/Qwen3.8-Flash-Next',
    profiles: [
      {id: 'qn-strata-q4', label: '4-bit · 82 GB + 29 GB table', stack: 'strata', quant: 'UD-Q4_K_XL · Unsloth GGUF', kind: 'tiered', experts: 76.99, dense: 4.8, table: 28.8, used: 10 / 512, active: 6,
        kvVramGB32k: 0.56, kvRamToken: 12500, ramExtra: 16, source: hf('unsloth/Qwen3.8-Flash-Next-GGUF', 'f5d175de2cf7f720d45d6064019a81fcf056e986')},
      {id: 'qn-strata-iq3s', label: '3-bit · 55 GB + 29 GB table', stack: 'strata', quant: 'IQ3_S · ISTA-DASLab GSQ-RCO', kind: 'tiered', experts: 50.292, dense: 4.514, table: 28.8, used: 10 / 512, active: 6,
        kvVramGB32k: 0.56, kvRamToken: 12500, ramExtra: 10, source: hf('ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF', 'ed59f92082b1e93c0e96d60a8b11aab089b52f09')},
      {id: 'qn-strata-iq3xxs', label: '3-bit, smaller · 47 GB + 29 GB table', stack: 'strata', quant: 'IQ3_XXS · ISTA-DASLab GSQ-RCO', kind: 'tiered', experts: 42.913, dense: 4.116, table: 28.8, used: 10 / 512, active: 6,
        kvVramGB32k: 0.56, kvRamToken: 12500, ramExtra: 10, source: hf('ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF', 'ed59f92082b1e93c0e96d60a8b11aab089b52f09')}
    ]},
  {id: 'glm', short: 'GLM Flash', name: 'GLM-5.3-Flash', size: '320B MoE · 18B active', context: 1048576, licence: 'MIT', source: 'https://huggingface.co/zai-org/GLM-5.3-Flash',
    profiles: [
      {id: 'glm-maya-m', label: '3-bit mixed · 116 GB', stack: 'maya', quant: 'Maya-M', kind: 'tiered', experts: 108.188, dense: 7.806, table: 0, used: 8 / 288, active: 18,
        kvVramGB32k: 0.196, kvRamToken: 5984, ramExtra: 16, source: hf('peasantsmith/GLM-5.3-Flash-Maya-GGUF', '5ca1df1d2436bd1ab270b169c5ea6c47aad23641')},
      {id: 'glm-maya-s', label: '2–3-bit mixed · 96 GB', stack: 'maya', quant: 'Maya-S', kind: 'tiered', experts: 88.653, dense: 7.806, table: 0, used: 8 / 288, active: 18,
        kvVramGB32k: 0.196, kvRamToken: 5984, ramExtra: 16, source: hf('peasantsmith/GLM-5.3-Flash-Maya-GGUF', '5ca1df1d2436bd1ab270b169c5ea6c47aad23641')},
      {id: 'glm-maya-xs', label: '2-bit mixed · 73 GB', stack: 'maya', quant: 'Maya-XS', kind: 'tiered', experts: 67.363, dense: 6.039, table: 0, used: 8 / 288, active: 18,
        kvVramGB32k: 0.196, kvRamToken: 5984, ramExtra: 16, source: hf('peasantsmith/GLM-5.3-Flash-Maya-GGUF', '5ca1df1d2436bd1ab270b169c5ea6c47aad23641')}
    ]},
  {id: 'deepseek', short: 'DeepSeek Flash', name: 'DeepSeek-V4.1-Flash-1017', size: '552B MoE · 16B active', context: 1048576, licence: 'MIT', source: 'https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017',
    profiles: [
      {id: 'ds-maya-s', draft1: 1.12, label: '2–3-bit mixed · 178 GB + 162 GB table', stack: 'maya', quant: 'Maya-S', kind: 'tiered', experts: 169.02, dense: 8.833, table: 161.619, used: 6 / 384, active: 16,
        kvVramGB32k: 0.04, kvRamToken: 1100, ramExtra: 16, source: hf('peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF', '928ffcc3b0497f1d2f356d87ed17a1b8641bd382')},
      {id: 'ds-strata-225', label: '2.25 bits · 155 GB + 111 GB table', stack: 'strata', quant: '2.25 bpw · ISTA-DAS GSQ-RCO', kind: 'tiered', experts: 149.06, dense: 5.943, table: 110.595, used: 6 / 384, active: 16,
        kvVramToken: 1300, kvRamToken: 0, ramExtra: 10, slots: 8, source: hf('ISTA-DASLab/DeepSeek-V4.1-Flash-1017-GSQ-RCO-GGUF', '65d53bc8be65123e255ff02f3ded958b6dbf54fd')},
      {id: 'ds-strata-200', label: '2.00 bits · 138 GB + 111 GB table', stack: 'strata', quant: '2.00 bpw · ISTA-DAS GSQ-RCO', kind: 'tiered', experts: 132.073, dense: 5.943, table: 110.595, used: 6 / 384, active: 16,
        kvVramToken: 1300, kvRamToken: 0, ramExtra: 10, slots: 8, source: hf('ISTA-DASLab/DeepSeek-V4.1-Flash-1017-GSQ-RCO-GGUF', '65d53bc8be65123e255ff02f3ded958b6dbf54fd')},
      {id: 'ds-maya-xs', draft1: 1.12, label: '1–2-bit mixed · 117 GB + 162 GB table', stack: 'maya', quant: 'Maya-XS v2', kind: 'tiered', experts: 109.566, dense: 6.933, table: 161.619, used: 6 / 384, active: 16,
        kvVramGB32k: 0.04, kvRamToken: 1100, ramExtra: 16, source: hf('peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF', '928ffcc3b0497f1d2f356d87ed17a1b8641bd382')}
    ]}
];

// Main LLM cards. vram in GiB as sold; bw GB/s; tensor = dense FP16 tensor TFLOPS with FP16 accumulate (half the dense INT8 TOPS),
// used only as a relative prompt-speed index; slots = physical width. Prices verified 15 Nov 2026.
export const gpus = [
  {id: 'pro4500', name: 'RTX PRO 4500 Blackwell 32 GB', short: 'PRO 4500', vendor: 'nvidia', blackwell: true, vram: 32, bw: 896, tensor: 202, pcie: 5, watts: 200, width: 2,
    price: 6999, stock: 'Scorptec special, in stock', source: 'https://www.scorptec.com.au/product/graphics-cards/workstation'},
  {id: 'pro5000', name: 'RTX PRO 5000 Blackwell 48 GB', short: 'PRO 5000', vendor: 'nvidia', blackwell: true, vram: 48, bw: 1344, tensor: 258, pcie: 5, watts: 300, width: 2,
    price: 13999, stock: 'Scorptec, in stock', source: 'https://www.scorptec.com.au/product/graphics-cards/workstation/118878-900-5g153-2550-000'},
  {id: 'maxq', name: 'RTX PRO 6000 Blackwell Max-Q 96 GB', short: 'PRO 6000 Max-Q', vendor: 'nvidia', blackwell: true, vram: 96, bw: 1792, tensor: 439, pcie: 5, watts: 300, width: 2,
    price: 24999, stock: 'e365, no quantity limit stated (Scorptec A$25,999, one per household)', source: 'https://www.e365.com.au/product/nvidia-rtx-pro-6000-blackwell-max-q-96gb/'},
  {id: 'ws6000', name: 'RTX PRO 6000 Blackwell Workstation 96 GB', short: 'PRO 6000', vendor: 'nvidia', blackwell: true, vram: 96, bw: 1792, tensor: 500, pcie: 5, watts: 600, width: 2,
    price: 26153.6, stock: 'Zylax, no quantity limit stated', source: 'https://www.zylax.com.au/nvidia-rtx-pro-6000-blackwell-96gb-workstation-gddr7-graphics-card-900-5g144-2500-000'},
  {id: '5090', name: 'GeForce RTX 5090 32 GB', short: 'RTX 5090', vendor: 'nvidia', blackwell: true, vram: 32, bw: 1792, tensor: 419, pcie: 5, watts: 575, width: 3.5,
    price: 12999, stock: 'Scorptec, one per household', source: 'https://www.scorptec.com.au/product/graphics-cards/nvidia/116093-tuf-rtx5090-o32g-gaming'},
  {id: 'r9700', name: 'Radeon AI PRO R9700 32 GB', short: 'R9700', vendor: 'amd', vram: 32, bw: 640, tensor: 191, pcie: 5, watts: 300, width: 2,
    price: 2699, stock: 'Scorptec, in stock', source: 'https://www.scorptec.com.au/product/graphics-cards/workstation'},
  {id: '3090', name: 'GeForce RTX 3090 24 GB · refurbished', short: 'RTX 3090', vendor: 'nvidia', vram: 24, bw: 936, tensor: 142, pcie: 4, watts: 350, width: 3,
    price: 2969, stock: 'refurbished A$2,699; GST not stated, 10% added', source: 'https://mikepc.com.au/products/gigabyte-aorus-rtx-3090-24gb-graphics-card'}
];

// The separate card for vision, embeddings, reranking and small expert models. Its memory never joins the LLM pool.
export const toolsGpu = {name: 'RTX PRO 2000 Blackwell 16 GB', vram: 16, watts: 70, width: 2, price: 2299,
  source: 'https://www.umart.com.au/product/nvidia-rtx-pro-blackwell-2000-16g-workstation-graphics-card-900-5g195-2551-000-91371'};

// Hosts: everything except the GPUs (CPU, board, RAM, 4 TB NVMe, PSU, case, cooler), AUD incl. GST, 15 Nov 2026 (hardware.md).
// ram GB; bw = theoretical GB/s of the populated channels; gen = PCIe generation of the GPU slots; split = two cards share
// the CPU lanes at x8/x8; slots = cards the board
// and case take in all, the tools card included; watts = host draw at full load without the cards.
export const platforms = [
  {id: 'am4-128', name: '128 GB DDR4 · Ryzen 9 5950X desktop', short: 'The DDR4 desktop', mem: 'DDR4-3200, 2 channels', ecc: false, ram: 128, bw: 51.2, gen: 4, split: true, slots: 3, server: false, psu: 1250, watts: 230, price: 3926,
    note: 'ROG Strix X570-E (x8/x8 CPU slots, chipset x4), 4 x 32 GB DDR4-3200, Define 7 XL, 1,250 W. Four-DIMM 3200 operation to be qualified.'},
  {id: 'am5-128', name: '128 GB DDR5 · Ryzen 9 9950X desktop', short: 'The DDR5 desktop', mem: 'DDR5-5600, 2 channels', ecc: false, ram: 128, bw: 89.6, gen: 5, split: true, slots: 3, server: false, psu: 1250, watts: 250, price: 5916,
    note: 'ProArt X870E-Creator (x8/x8 CPU slots, chipset x4), 2 x 64 GB DDR5-5600 (out of stock on 15 Nov), Define 7 XL, 1,250 W.'},
  {id: 'am5-256', name: '256 GB DDR5 · Ryzen 9 9950X desktop', short: 'The DDR5 desktop with 256 GB', mem: 'DDR5-3600, 2 channels, 4 DIMMs', ecc: false, ram: 256, bw: 57.6, gen: 5, split: true, slots: 3, server: false, psu: 1250, watts: 260, price: 8346,
    note: 'As above with 4 x 64 GB. AMD rates four DIMMs at 3600 MT/s; ASUS lists up to 5200 with qualified kits.'},
  {id: 'trx50-128', name: '128 GB DDR5 ECC · Threadripper 9970X', short: 'The Threadripper workstation', mem: 'DDR5-4800 ECC, 4 channels', ecc: true, ram: 128, bw: 153.6, gen: 5, split: false, slots: 4, server: false, psu: 1600, outlet15: true, watts: 450, price: 17508,
    note: 'Derived from Scorptec Atlas R2R10690 (A$20,999 in stock) less its RTX PRO 4000, with a 1,600 W Seasonic and Meshify 2 XL. Pro WS TRX50-SAGE WIFI.'},
  {id: 'wrx90-256', name: '256 GB DDR5 ECC · Threadripper PRO 9965WX', short: 'The Threadripper PRO workstation', mem: 'DDR5-5600 ECC, 8 channels', ecc: true, ram: 256, bw: 358.4, gen: 5, split: false, slots: 4, server: false, psu: 1600, outlet15: true, watts: 480, price: 25833,
    note: 'Pro WS WRX90E-SAGE SE, 8 x 32 GB DDR5-5600 RDIMM (A$2,016 each), Meshify 2 XL, Seasonic PRIME PX-1600 (needs a 15 A outlet).'},
  {id: 'wrx90-512', name: '512 GB DDR5 ECC · Threadripper PRO 9965WX', short: 'The Threadripper PRO workstation with 512 GB', mem: 'DDR5-5600 ECC, 8 channels', ecc: true, ram: 512, bw: 358.4, gen: 5, split: false, slots: 4, server: false, psu: 1600, outlet15: true, watts: 490, price: 45361,
    note: 'As above with 8 x 64 GB DDR5-5600 RDIMM (A$4,457 each).'},
  {id: 'sp3-256', name: '256 GB DDR4 ECC · used EPYC 7443 server', short: 'The used EPYC server', mem: 'DDR4-3200 ECC, 8 channels', ecc: true, ram: 256, bw: 204.8, gen: 4, split: false, slots: 4, server: true, psu: 1500, watts: 330, price: 14700,
    note: 'Used EPYC 7443 with a Supermicro H12SSL-i (eBay from the UK, warranty unstated; GST not stated, 10% added), 8 x 32 GB DDR4-3200 RDIMM (new), SilverStone RM44 4U, 1,500 W.'},
  {id: 'sp3-512', name: '512 GB DDR4 ECC · used EPYC 7443 server', short: 'The used EPYC server with 512 GB', mem: 'DDR4-3200 ECC, 8 channels', ecc: true, ram: 512, bw: 204.8, gen: 4, split: false, slots: 4, server: true, psu: 1500, watts: 340, price: 20044,
    note: 'As above with 8 x 64 GB DDR4-3200 RDIMM; only one module was in stock at the price used.'}
];

// Power and network for the machine: an online double-conversion UPS sized to the load, a managed 10GbE switch and card.
export const siteKit = [
  {upTo: 1000, price: 1570, note: 'CyberPower OLS2000ERT2UA (1,800 W, 10 A plug) + MikroTik CRS304 + TP-Link TX401'},
  {upTo: 1600, price: 1885, note: 'CyberPower OLS3000ERT2UA (2,700 W, 15 A plug) + switch and card'},
  {upTo: 2400, price: 2685, note: 'CyberPower OLS3KERT2UH (3,000 W, 15 A plug) + switch and card; price from an indexed listing'}
];

export const machines = [
  {id: 'small', name: 'Small', sub: 'PRO 4500 · DDR5 desktop', card: '1 × PRO 4500 32 GB', host: 'DDR5 desktop, 128 GB', spec: 'PRO 4500 32 GB · DDR5 desktop, 128 GB', gpu: 'pro4500', count: 1, platform: 'am5-128'},
  {id: 'medium', name: 'Medium', sub: 'PRO 6000 Max-Q · EPYC', card: '1 × PRO 6000 Max-Q 96 GB', host: 'Used EPYC server, 256 GB ECC', spec: 'PRO 6000 Max-Q 96 GB · used EPYC, 256 GB ECC', gpu: 'maxq', count: 1, platform: 'sp3-256'},
  {id: 'large', name: 'Large', sub: '2 × PRO 6000 Max-Q', card: '2 × PRO 6000 Max-Q 96 GB', host: 'Threadripper PRO, 256 GB ECC', spec: '2 × PRO 6000 Max-Q · Threadripper PRO, 256 GB ECC', gpu: 'maxq', count: 2, platform: 'wrx90-256'}
];
