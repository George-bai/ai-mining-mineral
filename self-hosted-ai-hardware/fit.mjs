// Fits each stack's few constants to the first-hand runs in anchors.json and writes calibration.mjs.
// Run from this folder: node fit.mjs   (Node 20+, no dependencies). It also writes fit-report.json: every run's
// measured and fitted speed, so anyone can see where the model is close and where it is not.
import { readFileSync, writeFileSync } from 'node:fs';
import { models } from './catalog.mjs';
import { memory, decodeOne, prefill } from './calculate.mjs';

import { cards, AMD, lane } from './cards.mjs';


// Packs that appear in runs but are not offered on the page (sizes from their GGUF headers or the stacks' own docs).
const T = (id, stack, experts, dense, used, active, more = {}) => ({ id, stack, kind: 'tiered', experts, dense, used, active, table: 0,
  kvVramGB32k: stack === 'strata' && used > 0.019 ? 0.56 : 0.05, kvRamToken: 1000, ramExtra: stack === 'strata' ? 10 : 16, ...more });
// the same cache and prefill inputs as the offered packs of these models (catalog.mjs)
const GLM = { kvVramGB32k: 0.196, kvRamToken: 5984 }, DS_STRATA = { kvVramToken: 1300, kvRamToken: 0, slots: 8, restInRam: true };
const extra = [
  T('glm-maya-l', 'maya', 148.504, 7.806, 8 / 288, 18, GLM), T('glm-maya-s24', 'maya', 88.653, 6.039, 8 / 288, 18, GLM),
  T('qn-strata-q20', 'strata', 33.974, 3.639, 10 / 512, 6), T('qn-strata-iq2xs', 'strata', 35.455, 3.76, 10 / 512, 6),
  T('qn-strata-iq4xs', 'strata', 59.5, 4.8, 10 / 512, 6), T('qn-strata-q8', 'strata', 128.3, 4.8, 10 / 512, 6, { ramExtra: 16 }),
  T('ds-strata-175', 'strata', 114.556, 5.943, 6 / 384, 16, DS_STRATA), T('ds-strata-q8', 'strata', 288.8, 16.8, 6 / 384, 16, DS_STRATA),
  T('ds-maya-ista200', 'maya', 132.073, 5.943, 6 / 384, 16, { draft1: 1.12 }), T('ds-maya-q8', 'maya', 288.8, 16.8, 6 / 384, 16, { draft1: 1.12 })
];
const profiles = Object.fromEntries([...models.flatMap((m) => m.profiles.map((p) => [p.id, p])), ...extra.map((p) => [p.id, p])]);
// whole-model servers: any model on any of the three stacks; each run carries its own weight size
for (const m of models.filter((x) => x.profiles.some((p) => p.kind === 'resident'))) {
  const base = m.profiles.find((p) => p.kind === 'resident');
  const fp16kv = base.stack === 'llamacpp' ? base.kvToken : base.kvToken * 2;
  for (const [stack, key] of [['vllm', 'vllm'], ['sglang', 'sglang'], ['llamacpp', 'llama']]) {
    const id = `${base.id.split('-')[0]}-${key}`;
    if (!profiles[id]) profiles[id] = { ...base, id, stack, blackwell: false, kvToken: stack === 'llamacpp' ? fp16kv : fp16kv / 2 };
  }
}

const data = JSON.parse(readFileSync(new URL('./anchors.json', import.meta.url), 'utf8'));
const runs = data.runs;
for (const a of runs) delete a.outlier;   // outliers are decided afresh on every run
// The context a writing speed was measured at. decodeContext is an exact token count from the source. Where the source gives
// no count but states a length in words, that length is kept as decodeContextStated with its basis, and used wherever the
// context matters. Before 24 Nov 2026 such runs entered the fit as short prompts. A run with neither stays unknown, and each
// use below says what it then assumes. Every entry quotes the run's own notes in anchors.json.
const STATED = {
  // Strata: benchmark prompts of a stated nominal length
  'p1-details-pro5000-03': [8192, "'8K document' prompt"], 'p1-amdhip-p620-03': [8192, 'nominal 8K prompt'], 'p1-amdhip-p620-04': [32768, 'nominal 32K prompt'],
  'p1-amdhip-p620-05': [65536, 'nominal 64K prompt'], 'p1-quants-r9700-03': [6144, "'after 6K document' case"], 'p1-quants-r9700-06': [6144, "'after 6K document' case"],
  'p1-unsloth-3090-05': [131072, '128K prompt (nominal)'], 'p1-bench-dev5090-01': [1024, 'nominal 1k'], 'p1-bench-dev5090-02': [4096, 'nominal 4k'],
  'p1-bench-dev5090-03': [32768, 'nominal 32k'], 'p1-bench-dev5090-04': [131072, 'nominal 128k'], 'p1-bench-021-author-02': [4096, 'prompt-4k'],
  'p1-bench-021-author-03': [16384, 'prompt-16k'], 'p1-bench-021-author-06': [4096, 'prompt-4k'], 'p1-bench-021-author-07': [16384, 'prompt-16k'],
  'p1-iss4243-02': [4096, 'prompt-4k'], 'p1-iss4243-03': [16384, 'prompt-16k'], 'p1-iss5089-01': [8192, '8K, prompt lengths nominal'],
  'p1-iss5089-02': [32768, 'nominal 32K'], 'p1-iss5089-03': [65536, 'nominal 64K'], 'p1-iss5089-04': [102400, 'nominal 100K'],
  'p1-iss2038-01': [200000, 'one 200k-token prompt (as written)'], 'p1-iss2038-03': [200000, '200k solo'],
  // Maya: in-use reports that state the context in words (approximate)
  'p3-819-04': [179000, "'an 1850-token answer at 179K context'"], 'p3-394-live150k': [150000, "context '150K+' (at least)"],
  'p3-614-04': [100000, "'100k+ context' (at least)"], 'p3-332-01': [100000, "'~100K tokens of context'"],
  'p4-873-session': [382000, 'context grew 281,947 to 482,074 (midpoint)'],
  'p3-819-api-0cold': [10619, 'two prompts, 12,505 and 8,733 tokens (mean)'], 'p3-819-api-0warm': [10619, 'two prompts, 12,505 and 8,733 tokens (mean)'],
  'p3-819-api-1cold': [10619, 'two prompts, 12,505 and 8,733 tokens (mean)'], 'p3-819-api-1warm': [10619, 'two prompts, 12,505 and 8,733 tokens (mean)']
};
for (const a of runs) {
  delete a.decodeContextStated; delete a.decodeContextBasis;
  const m = /nominal prompt\s*(\d+)\s*K/i.exec(a.notes || ''), s = STATED[a.id] || (m && [+m[1] * 1024, m[0]]);
  if (!a.decodeContext && s) { a.decodeContextStated = s[0]; a.decodeContextBasis = s[1]; }
}
for (const id of Object.keys(STATED)) if (!runs.some((a) => a.id === id && a.decodeContextStated)) throw new Error(`STATED names ${id}, which is not a run without an exact context`);
const ctxOf = (a) => a.decodeContext || a.decodeContextStated;
// so are the checks below, so a change to the memory rules re-admits the runs they no longer exclude
const DERIVED = /^(RAM short|faster than the cards|needs about [\d.]+ GB of VRAM as modelled|harness import)/;
for (const a of runs) if (!a.fit && DERIVED.test(a.why || '')) { a.fit = true; delete a.why; }

function setup(a) {
  const [vram, bw, tensor, gen] = cards[a.gpu.card];
  let profile = profiles[a.profile];
  if (a.weights) profile = { ...profile, weights: a.weights, read: a.read || a.weights };
  if (a.experts === 5) profile = { ...profile, used: profile.used * 5 / 6 };   // five of six experts: five sixths of the routed bytes
  const platform = { ram: a.host.ram || 512, bw: a.host.ramBW, pcieGBs: lane[a.gpu.link || gen] * (a.gpu.lanes || 16) / 16 };
  return { profile, gpu: { vram, bw, tensor, vendor: AMD.has(a.gpu.card) ? 'amd' : 'nvidia' }, count: a.gpu.count, platform };
}

// runs whose host could not hold the experts read them from the SSD: kept as evidence, not fitted
for (const a of runs) {
  if (!a.fit || !profiles[a.profile] || profiles[a.profile].kind !== 'tiered' || !a.host.ram || !cards[a.gpu.card]) continue;
  const c = setup(a), m = memory({ ...c, context: ctxOf(a) || 8192, streams: 1 });
  if (m.ramShort > 2) { a.fit = false; a.why = `RAM short by about ${Math.round(m.ramShort)} GB for this pack beside these cards: experts came from the SSD`; }
}

// whole-model runs faster than the cards' memory can feed without a drafter or a batch: mislabelled, kept as evidence only
for (const a of runs) {
  const pr = profiles[a.profile];
  if (!a.fit || !pr || pr.kind !== 'resident' || !a.decode || !cards[a.gpu.card]) continue;
  const tp = pr.stack === 'llamacpp' ? 1 : a.gpu.count;
  if (a.decode * (a.read || a.weights || pr.read || pr.weights) * (pr.activeShare || 1) > 0.95 * cards[a.gpu.card][1] * tp) {
    a.fit = false; a.why = 'faster than the cards\' memory bandwidth allows without drafting or batching: probably mislabelled';
  }
  if (/NInfer|tokSTotal=1[0-9]{3}/.test(`${a.notes} ${a.limitations}`)) { a.fit = false; a.why = a.why || 'harness import or another engine under this label'; }
}

// whole-model runs that could not fit in VRAM as modelled (their KV or offload settings must differ): evidence only
for (const a of runs) {
  const pr = profiles[a.profile];
  if (!a.fit || !pr || pr.kind !== 'resident' || !cards[a.gpu.card]) continue;
  const c = setup(a), m = memory({ ...c, context: ctxOf(a) || a.prefillPrompt || 4096, streams: a.streams || 1 });
  if (m.vramShort > 0) { a.fit = false; a.why = `needs about ${m.vramUsed.toFixed(1)} GB of VRAM as modelled against ${m.vram.toFixed(1)} GB: its cache or offload settings differ`; }
}

// A small Nelder-Mead in log space, so every constant stays positive.
function minimise(f, x0, iters = 3000) {
  const n = x0.length; let s = [x0, ...x0.map((_, i) => x0.map((v, j) => v + (i === j ? 0.5 : 0)))], fs = s.map(f);
  for (let it = 0; it < iters; it++) {
    const o = fs.map((v, i) => i).sort((a, b) => fs[a] - fs[b]); s = o.map((i) => s[i]); fs = o.map((i) => fs[i]);
    const c = x0.map((_, j) => s.slice(0, n).reduce((t, p) => t + p[j], 0) / n), at = (t) => c.map((v, j) => v + t * (s[n][j] - v));
    const r = at(-1), fr = f(r);
    if (fr < fs[0]) { const e = at(-2), fe = f(e); [s[n], fs[n]] = fe < fr ? [e, fe] : [r, fr]; }
    else if (fr < fs[n - 1]) { s[n] = r; fs[n] = fr; }
    else { const k = at(0.5), fk = f(k); if (fk < fs[n]) { s[n] = k; fs[n] = fk; } else { s = s.map((p) => p.map((v, j) => s[0][j] + 0.5 * (v - s[0][j]))); fs = s.map(f); } }
  }
  return s[0];
}
const quantile = (xs, q) => { const v = [...xs].sort((a, b) => a - b), i = (v.length - 1) * q; return v[Math.floor(i)] + (v[Math.ceil(i)] - v[Math.floor(i)]) * (i % 1); };
const median = (xs) => quantile(xs, 0.5);

const start = {
  strata: { amd: 1, eff: 1, lat: 4, beta: 3, ramEff: 0.65, single: 1.5, multi: 1.5, full: 0.3, longCtx: 0.4, kappaResident: 0.45, kappaGpus: 0.67, pa: 0.03, pb: 2, pScale: 0.3, pLen: 4e6 },
  maya: { amd: 1, eff: 0.5, lat: 4, beta: 6, ramEff: 0.4, single: 1, multi: 1.6, longCtx: 0.4, kappaResident: 0.5, kappaGpus: 0, pa: 0.02, pb: 2, pScale: 0.3, pLen: 4e6 },
  sglang: { amd: 1, eff: 0.7, lat: 3, attention: 1.5, tpGain: 0.75, kappa: 0.2, pa: 0.004, pScale: 0.85, pLen: 2e5 },
  vllm: { amd: 1, eff: 0.7, lat: 3, attention: 1.5, tpGain: 0.75, kappa: 0.2, pa: 0.004, pScale: 0.85, pLen: 2e5 },
  llamacpp: { amd: 1, eff: 0.7, lat: 3, attention: 3, tpGain: 0, kappa: 0.35, pa: 0.008, pScale: 0.5, pLen: 1e5 }
};
const free = {
  decode: { strata: ['lat', 'beta', 'longCtx', 'single', 'multi', 'full'], maya: ['eff', 'lat', 'multi', 'longCtx', 'ramEff'], sglang: ['eff', 'lat', 'attention'], vllm: ['eff', 'lat', 'attention'], llamacpp: ['eff', 'lat', 'attention'] },
  prefill: { strata: ['pa', 'pb', 'pScale', 'amd'], maya: ['pa', 'pb', 'pScale', 'amd'], sglang: ['pa', 'pLen'], vllm: ['pa', 'pLen', 'pScale'], llamacpp: ['pa', 'pLen', 'pScale', 'amd'] }
};
const bounded = (k) => (k.single ?? 1) <= 4 && (k.full ?? 0) <= 3 && (k.ramEff ?? 0.5) <= 1 && (k.ramEff ?? 0.5) >= 0.05 && (k.beta ?? 1) >= 0.5 && (k.beta ?? 1) <= 30 && k.eff <= 1 && (k.pScale ?? 0) <= 1 && (k.multi ?? 1) <= 4 && (k.longCtx ?? 0) <= 4 && (k.attention ?? 1) <= 6 && (k.amd ?? 1) >= 0.5 && (k.amd ?? 1) <= 6 && (k.pLen ?? 1e5) >= 2e4;

// a run with no stated context is taken as a short prompt (method.md gives the sensitivity to that)
const pd = (a, kk) => { const c = setup(a), ctx = ctxOf(a) || 1024; return decodeOne({ ...c, context: ctx, m: memory({ ...c, context: ctx, streams: 1 }), k: kk }); };
const pp = (a, kk) => { const c = setup(a); return prefill({ ...c, context: a.prefillPrompt, m: memory({ ...c, context: a.prefillPrompt, streams: 1 }), k: kk }); };
const OUT = Math.log(2.5);
const readable = (a) => a.prefill && a.prefillPrompt >= 1024 && a.streams === 1;

/** Fit one stack's constants to a set of runs: writing speed on one-stream runs, reading speed on one-stream cold prompts.
 *  Two passes: fit, set aside runs more than 2.5x from that fit as outliers, fit again. */
function fitStack(stack, set, base) {
  const k = { ...start[stack], ...base };
  // reading speed only from prompts of 1,024 tokens or more: shorter ones measure start-up latency, not throughput
  const dec = set.filter((a) => a.decode && a.streams === 1), pre = set.filter(readable);
  const fit = (keys, xs, pred, field) => {
    if (xs.length <= keys.length) return;
    const x = minimise((v) => { const kk = { ...k }; keys.forEach((key, i) => (kk[key] = Math.exp(v[i]))); if (!bounded(kk)) return 1e9;
      return xs.reduce((t, a) => t + Math.log(pred(a, kk) / a[field]) ** 2, 0); }, keys.map((key) => Math.log(k[key])));
    keys.forEach((key, i) => (k[key] = +Math.exp(x[i]).toPrecision(4)));
  };
  fit(free.decode[stack], dec, pd, 'decode');
  const outDec = new Set(dec.filter((a) => Math.abs(Math.log(a.decode / pd(a, k))) > OUT));
  fit(free.decode[stack], dec.filter((a) => !outDec.has(a)), pd, 'decode');
  fit(free.prefill[stack], pre, pp, 'prefill');
  const outPre = new Set(pre.filter((a) => Math.abs(Math.log(a.prefill / pp(a, k))) > OUT));
  fit(free.prefill[stack], pre.filter((a) => !outPre.has(a)), pp, 'prefill');
  return { k, dec, pre, outDec, outPre };
}

// held-out check: runs are grouped by machine (cards and host) into five folds; each fold is predicted by a fit made
// without it. The page's bands come from these held-out ratios, not from the runs a fit has already seen.
// One computer written two ways in its owner's reports (same submitter, cards and RAM; project-maya #737 says its machine
// is #730's): aliased, so all of a machine's runs fall in one fold. The check after it stops a new spelling slipping by.
const SAME_CPU = { 'Ryzen 9 9950X3D (16c/32t, AVX-512)': 'Ryzen 9 9950X3D', 'EPYC 9354P (32C/64T)': 'EPYC 9354P (32C)', 'Ryzen 9 5900X (12c)': 'Ryzen 9 5900X (12 cores)' };
const machineOf = (a) => `${a.gpu.card}x${a.gpu.count}|${SAME_CPU[a.host.cpu] || a.host.cpu || '?'}|${a.host.ram || '?'}`;
{
  const seen = {};
  for (const a of runs.filter((x) => x.fit && x.host.cpu)) {
    const loose = `${a.by}|${a.gpu.card}x${a.gpu.count}|${a.host.ram}|${a.host.cpu.replace(/\(.*?\)/g, '').replace(/\s+/g, ' ').trim().toLowerCase()}`;
    (seen[loose] ||= new Set()).add(machineOf(a));
  }
  const split = Object.entries(seen).filter(([, v]) => v.size > 1);
  if (split.length) throw new Error(`One machine under two names (add it to SAME_CPU): ${split.map(([k, v]) => `${k}: ${[...v].join(' / ')}`).join('; ')}`);
}
const foldOf = (a) => [...machineOf(a)].reduce((h, ch) => (h * 31 + ch.charCodeAt(0)) >>> 0, 7) % 5;

const calibration = {}, report = [];
const order = ['strata', 'maya', 'vllm', 'sglang', 'llamacpp'];   // vLLM before SGLang: SGLang starts from its decode constants
for (const stack of order) {
  // SGLang's few plain-decode runs start from vLLM's decode constants (the same kind of server)
  const base = stack === 'sglang' ? { eff: Math.min(0.95, calibration.vllm.eff), lat: calibration.vllm.lat, attention: Math.min(5, calibration.vllm.attention) } : {};
  const mine = runs.filter((a) => a.fit && profiles[a.profile]?.stack === stack && cards[a.gpu.card]);
  const { k, dec, pre, outDec, outPre } = fitStack(stack, mine, base);
  for (const a of outDec) a.outlier = 'decode';
  for (const a of outPre) a.outlier = a.outlier ? 'both' : 'prefill';

  const held = { decode: [], prefill: [], dm: new Set(), pm: new Set() };
  for (let f = 0; f < 5; f++) {
    const test = mine.filter((a) => foldOf(a) === f); if (!test.length) continue;
    const kf = fitStack(stack, mine.filter((a) => foldOf(a) !== f), base).k;
    for (const a of test.filter((x) => x.decode && x.streams === 1)) { held.decode.push(a.decode / pd(a, kf)); held.dm.add(machineOf(a)); }
    for (const a of test.filter(readable)) { held.prefill.push(a.prefill / pp(a, kf)); held.pm.add(machineOf(a)); }
  }

  // concurrency: how much each stream keeps against one stream alone, as kappa in 1 / (1 + kappa (n - 1)). A pair counts
  // only within one sweep, on the same cards and drafter, and at a context within a quarter of the one-stream run's.
  const groups = {};
  for (const a of runs.filter((x) => profiles[x.profile]?.stack === stack && cards[x.gpu.card] && !x.turbo && x.run_group && (x.decode || x.aggregate))) (groups[a.run_group] ||= []).push(a);
  const near = (x, y) => (!x && !y) || (x && y && Math.abs(x - y) <= 0.25 * Math.max(x, y));
  const kap = [];
  for (const g of Object.values(groups)) for (const a of g.filter((x) => x.streams > 1)) {
    const one = g.find((b) => b.streams === 1 && b.decode && b.gpu.card === a.gpu.card && b.gpu.count === a.gpu.count && b.drafting === a.drafting && near(ctxOf(b), ctxOf(a)));
    const per = a.aggregate ? a.aggregate / a.streams : a.decode;
    if (one && per) kap.push(Math.max(0, (one.decode / per - 1) / (a.streams - 1)));
  }
  // whole-model servers: the median of the matched pairs. Tiered stacks keep the values their authors measured with every
  // expert in VRAM (Strata: 2 x A6000 and 4 x R9700; Maya: 2 x PRO 5000): most community sweeps there spill experts into RAM.
  if (kap.length >= 3 && k.kappa !== undefined) k.kappa = +median(kap).toFixed(3);
  k.sweeps = kap.length;

  // bands: the 10th and 90th percentile of held-out measured / estimated, at least ±15%. Fewer than eight held-out runs, or
  // runs from fewer than three machines, get at least ±30%, widened to what the held-out runs show: an unvalidated band,
  // said so in method.md
  const q = (r, lo) => +quantile(r, lo ? 0.1 : 0.9).toFixed(3);
  const band = (r, lo, ms) => r.length >= 8 && ms.size >= 3 ? q(r, lo) : !r.length ? (lo ? 0.7 : 1.3) : lo ? Math.min(0.7, q(r, lo)) : Math.max(1.3, q(r, lo));
  k.decodeLo = Math.min(0.85, band(held.decode, true, held.dm)); k.decodeHi = Math.max(1.15, band(held.decode, false, held.dm));
  k.prefillLo = Math.min(0.85, band(held.prefill, true, held.pm)); k.prefillHi = Math.max(1.15, band(held.prefill, false, held.pm));
  const err = (r) => (r.length ? +median(r.map((x) => Math.abs(Math.log(x)))).toFixed(3) : null);
  const decIn = dec.filter((a) => !outDec.has(a)), preIn = pre.filter((a) => !outPre.has(a));
  k.runs = { decode: decIn.length, prefill: preIn.length, outliers: outDec.size + outPre.size,
    medianError: { decode: err(decIn.map((a) => a.decode / pd(a, k))), prefill: err(preIn.map((a) => a.prefill / pp(a, k))) },
    heldOut: { decode: held.decode.length, prefill: held.prefill.length, machines: { decode: held.dm.size, prefill: held.pm.size }, medianError: { decode: err(held.decode), prefill: err(held.prefill) } } };
  for (const b of ['decodeLo', 'decodeHi', 'prefillLo', 'prefillHi']) if (!Number.isFinite(k[b])) throw new Error(`${stack}: ${b} is not a number: a held-out estimate failed`);
  calibration[stack] = k;
  for (const a of dec) report.push({ id: a.id, stack, what: 'decode', measured: a.decode, fitted: +pd(a, k).toFixed(1), outlier: outDec.has(a) });
  for (const a of pre) report.push({ id: a.id, stack, what: 'prefill', measured: a.prefill, fitted: +pp(a, k).toFixed(0), outlier: outPre.has(a) });
}

writeFileSync(new URL('./calibration.mjs', import.meta.url),
  `// Written by fit.mjs from anchors.json. Do not edit by hand: change the runs or the model, then run node fit.mjs.\nexport const calibration = ${JSON.stringify(calibration, null, 1)};\n`);
writeFileSync(new URL('./fit-report.json', import.meta.url), JSON.stringify({ excluded: runs.filter((a) => !a.fit).length, fitted: report }, null, 0));
writeFileSync(new URL('./anchors.json', import.meta.url), JSON.stringify(data, null, 0));
for (const [s, k] of Object.entries(calibration)) console.log(s.padEnd(9), JSON.stringify(k.runs), 'band', k.decodeLo, k.decodeHi, '| prefill band', k.prefillLo, k.prefillHi, '| pairs', k.sweeps, '| kappa', k.kappa ?? k.kappaResident);
