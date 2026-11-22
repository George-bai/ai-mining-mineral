// The calculator's model: where each byte lives and how fast it moves, with per-stack constants fitted to first-hand runs.
// Sizes GB (decimal; cards and RAM modules are sold in GiB and converted), bandwidth GB/s, speeds tokens/s. The fitted constants and their errors are in calibration.mjs (built by fit.mjs).
import { BUDGET, stacks, toolsGpu, siteKit } from './catalog.mjs';
import { calibration } from './calibration.mjs';

const GiB = 1.073741824;            // GB per GiB
const RESERVE = 1.6;                // GB per card held back for the runtime, CUDA/HIP context and buffers
const SYSTEM_RAM = 16;              // GB of RAM kept for the OS, the tools card's services and file cache

/** Memory layout for one configuration. Returns the expert-cache share c and what is short, if anything. */
export function memory({ profile, gpu, count, platform, context, streams }) {
  const vram = gpu.vram * GiB * count;
  const ram = platform.ram * GiB;
  if (profile.kind === 'resident') {
    const kv = streams * (profile.stateGB + context * profile.kvToken / 1e9);
    const used = profile.weights + kv + RESERVE * count;
    return { vram, ram, weights: profile.weights, kv, cache: 0, c: 1, vramUsed: used, vramShort: Math.max(0, used - vram),
      ramUsed: SYSTEM_RAM, ramShort: Math.max(0, SYSTEM_RAM - ram), ssd: 0 };
  }
  // Strata keeps a 64K window of the cache in VRAM and the rest of a long context in pinned RAM; its DeepSeek engine keeps the
  // whole cache in VRAM (kvVramToken, measured up to 1M). Maya keeps a 32K window in VRAM and, once a context is longer than
  // that, every stream's whole cache in pinned RAM (SETTINGS.md, v1.1.63).
  const maya = profile.stack === 'maya';
  const kvVram = streams * (profile.kvVramToken ? context * profile.kvVramToken / 1e9 : profile.kvVramGB32k * Math.min(maya ? 1 : 2, context / 32768));
  const kvRam = streams * (maya ? (context > 32768 ? context : 0) : Math.max(0, context - 65536)) * profile.kvRamToken / 1e9;
  const fixed = profile.dense + kvVram + RESERVE * count;
  const cache = Math.max(0, vram - fixed);
  const c = Math.min(1, cache / profile.experts);
  // Strata pins every expert in RAM; Maya keeps in RAM only the experts the cards do not hold.
  const expertsInRam = profile.stack === 'strata' ? profile.experts : profile.experts * (1 - c);
  const ramUsed = expertsInRam + kvRam + profile.ramExtra;
  return { vram, ram, weights: profile.dense, kv: kvVram, kvRam, cache: Math.min(cache, profile.experts), c,
    vramUsed: fixed + Math.min(cache, profile.experts), vramShort: Math.max(0, fixed + 1 - vram),
    ramUsed, ramExperts: expertsInRam, ramSystem: profile.ramExtra, ramShort: Math.max(0, ramUsed - ram), ssd: profile.table };
}

/** Hot experts are asked for far more often than cold ones, so a VRAM cache holding share c of them serves more than c of the reads. */
export const hits = (c, k) => 1 - Math.pow(1 - c, k.beta);

/** Decode speed of one stream (tokens/s) at a given context, before the error band. */
export function decodeOne({ profile, gpu, count, platform, context, m, k = calibration[profile.stack] }) {
  if (profile.kind === 'resident') {
    const bw = gpu.bw * (stacks[profile.stack].tensorParallel ? 1 + k.tpGain * (count - 1) : 1);
    const read = (profile.read || profile.weights) * (profile.activeShare || 1) + k.attention * context * profile.kvToken / 1e9;
    return 1 / (read / (bw * k.eff) + k.lat / 1000);
  }
  const h = hits(m.c, k);                                   // share of routed expert reads served from VRAM
  const routed = profile.experts * profile.used;            // GB of routed experts per token
  const gpuTime = (profile.dense + routed * h) / (gpu.bw * k.eff);
  const cpuTime = routed * (1 - h) / (platform.bw * k.ramEff);
  const long = 1 + k.longCtx * context / 1048576;           // sparse attention: a slow drift with context
  // drafting verifies several tokens per pass over the weights: Strata always, Maya's MTP with two or more cards,
  // Maya's DSpark for DeepSeek also on one card (profile.draft1)
  const draft = (count > 1 ? k.multi : (profile.draft1 || k.single))
    * (1 + (k.full || 0) * Math.pow(m.c, 8));              // with every expert in VRAM a verify pass costs little more than one token
  return draft / ((Math.max(gpuTime, cpuTime) + k.lat / 1000) * long);
}

/** Share of single-stream speed each stream keeps when n decode together: 1 / (1 + kappa (n - 1)). */
export function contention(profile, m, count, k = calibration[profile.stack]) {
  if (profile.kind === 'resident') return k.kappa;
  const resident = k.kappaResident / (1 + k.kappaGpus * (count - 1));   // more cards pipeline more slots
  return resident + (1 - resident) * (1 - hits(m.c, k));
}

/** Cold prompt-reading speed (tokens/s) for a prompt of the given length. */
export function prefill({ profile, gpu, count, platform, context, m, k = calibration[profile.stack] }) {
  const compute = k.pa * profile.active * (gpu.vendor === 'amd' ? k.amd : 1) / (gpu.tensor * Math.pow(count, k.pScale));
  const stream = profile.kind === 'tiered' ? k.pb * (1 - m.c) * profile.experts / (platform.pcieGBs * count) : 0;
  return 1 / ((compute + stream) * (1 + context / k.pLen));
}

const round = (x) => Math.round(x);

/** Everything the page shows for one configuration. */
export function calculate(cfg) {
  const { model, profile, gpu, count, platform, context, streams, target } = cfg;
  const problems = [], notes = [];
  // a problem with the machine itself (cards, slots, power) rather than with the workload: nothing is estimated
  let builds = true;
  const cannot = (msg) => { problems.push(msg); builds = false; };
  for (const [name, v, lo, hi] of [['GPU count', count, 1, 4], ['Streams', streams, 1, 64], ['Target speed', target, 1, 200], ['Context', context, 4096, 1048576]])
    if (!Number.isInteger(v) || v < lo || v > hi) problems.push(`${name} must be a whole number from ${lo} to ${hi}.`);
  if (problems.length) return { valid: false, problems, notes };

  const stack = stacks[profile.stack];
  const k = calibration[profile.stack];
  // the page never names the serving software: messages describe the set-up instead
  if (!stack.vendors.includes(gpu.vendor)) cannot(`This way of running ${model.name} does not run on ${gpu.vendor === 'amd' ? 'AMD' : 'these'} cards. Choose another card.`);
  if (profile.blackwell && !gpu.blackwell) cannot('NVFP4 weights need a Blackwell card. Choose a GGUF version for this card.');
  if (context > model.context) problems.push(`${model.name} reads at most ${Math.round(model.context / 1024)}K tokens.`);
  // a batching server splits each layer's heads evenly across the cards (vLLM 0.33.0 checks attention heads; the KV heads must
  // divide the split or be divided by it); a GGUF runner splits by layers instead
  if (stack.tensorParallel && count > 1 && model.heads) {
    const [h, kv] = model.heads;
    if (h % count || (kv >= count ? kv % count : count % kv)) cannot(`This way of running ${model.name} splits its ${h} attention heads evenly across the cards, so it cannot use ${count}. Choose 1 or 2 cards, or a GGUF version.`);
  }
  if (count + 1 > platform.slots) cannot(`${platform.short} takes ${platform.slots} cards in all, the tools card included.`);
  // cards wider than two slots: no checked board and case takes two of them beside the tools card (hardware.md)
  if (gpu.width > 2 && count > 1) cannot(`${count} × ${gpu.short} are too wide to fit side by side with the tools card on these boards.`);
  // the server case has eight openings: four dual-slot cards fill them, leaving none for the 10GbE card (hardware.md)
  if (platform.server && count + 1 === platform.slots) notes.push(`Four cards fill the server's eight openings, so the 10GbE card has no slot: it runs on the board's 1GbE.`);
  // each card's link: the slower of card and slot, halved where two cards share a desktop's CPU lanes (x8/x8)
  const link = { 3: 13, 4: 26, 5: 52 }[Math.min(gpu.pcie, platform.gen)] * (count > 1 && platform.split ? 0.5 : 1);
  const host = { ...platform, pcieGBs: link };

  // price
  const watts = gpu.watts * count + toolsGpu.watts + platform.watts;
  const kit = siteKit.find((x) => watts <= x.upTo) || siteKit[siteKit.length - 1];
  const parts = { gpus: gpu.price * count, tools: toolsGpu.price, host: platform.price, site: kit.price };
  const price = parts.gpus + parts.tools + parts.host + parts.site;
  if (price > BUDGET) problems.push(`A$${round(price).toLocaleString('en-AU')} is above the A$100,000 ceiling.`);
  if (watts > siteKit[siteKit.length - 1].upTo) cannot(`About ${round(watts)} W at full load: beyond one 15 A circuit and the largest UPS here.`);
  else if (watts > platform.psu * 0.9) cannot(`About ${round(watts)} W at full load is more than ${round(platform.psu * 0.9)} W, the 90% of this host's ${platform.psu} W power supply kept as its limit.`);
  if (watts > 1000 || platform.outlet15) notes.push(`${platform.outlet15 ? 'Its power supply' : `About ${round(watts)} W at full load: the UPS`} needs a 15 A outlet.`);

  const m = memory({ profile, gpu, count, platform, context, streams });
  if (m.vramShort > 0) problems.push(profile.kind === 'resident'
    ? `The model and ${streams > 1 ? streams + ' contexts' : 'its context'} need ${m.vramUsed.toFixed(0)} GB of VRAM; the cards have ${m.vram.toFixed(0)} GB.`
    : `The dense weights and ${streams > 1 ? streams + ' contexts' : 'context'} do not fit in ${m.vram.toFixed(0)} GB of VRAM.`);
  if (m.ramShort > 0) problems.push(`Needs about ${Math.ceil(m.ramUsed)} GB of RAM for the experts and system; this host's ${platform.ram} GiB is ${Math.floor(m.ram)} GB. It would read experts from the SSD and run far slower.`);
  const limit = profile.slots || (stack.slotsPerGpu ? stack.slots * count : stack.slots);
  if (stack.slots && streams > limit) problems.push(`This set-up answers at most ${limit} streams at once here; more requests wait in a queue.`);

  const valid = !problems.length;
  const band = (x) => ({ mid: x, lo: x * k.decodeLo, hi: x * k.decodeHi });
  // each stream's speed with n streams: memory, expert cache and contention recomputed for that n
  const at = (n) => {
    const mn = n === streams ? m : memory({ profile, gpu, count, platform, context, streams: n });
    const dn = decodeOne({ profile, gpu, count, platform, context, m: mn }) / (1 + contention(profile, mn, count) * (n - 1));
    return { n, ...band(dn), fits: !(mn.vramShort > 0 || mn.ramShort > 0) };
  };
  const d1 = at(1).mid, now = at(streams);
  const p = prefill({ profile, gpu, count, platform: host, context, m });
  const prompt = context - 1024;

  // the most streams that keep the target speed each and still fit: at the middle of the range and at its low end
  let maxStreams = 0, maxStreamsLo = 0;
  for (let n = 1; builds && n <= limit; n++) {
    const pn = at(n);
    if (!pn.fits || pn.mid < target) break;
    maxStreams = n;
    if (pn.lo >= target) maxStreamsLo = n;
  }
  // the longest context each of the chosen streams can hold, up to the model's limit
  let maxContext = 0;
  for (let c = 4096; c <= model.context; c += 4096) {
    const mc = memory({ profile, gpu, count, platform, context: c, streams });
    if (mc.vramShort > 0 || mc.ramShort > 0) break;
    maxContext = c;
  }

  return { valid, builds, problems, notes, price, parts, watts, memory: m, link,
    decode: band(now.mid), single: band(d1), aggregate: band(now.mid * streams),
    prefill: { mid: p, lo: p * k.prefillLo, hi: p * k.prefillHi },
    readSeconds: { mid: prompt / p, lo: prompt / (p * k.prefillHi), hi: prompt / (p * k.prefillLo) },
    curve: Array.from({ length: Math.min(limit, 16) }, (_, i) => at(i + 1)),
    maxStreams, maxStreamsLo, maxContext };
}
