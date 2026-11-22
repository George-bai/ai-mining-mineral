// Builds what the article page loads: data.json (the first-hand runs shown beside each estimate) and the static
// SVG figures shown before the script runs or without it. Run from this folder after fit.mjs: node build-page.mjs
// In the repository it writes into ../page/ and fills that page's static numbers; in the exported folder alone it
// writes the same data.json and figures into ./out/.
import { readFileSync, writeFileSync, copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { models, gpus, platforms, machines, stacks } from './catalog.mjs';
import { calculate } from './calculate.mjs';
import { curveSVG, memorySVG, tiersSVG, stackSVG } from './draw.mjs';
import { cards } from './cards.mjs';
import { calibration } from './calibration.mjs';

const inRepo = existsSync(new URL('../page/index.html', import.meta.url));
const page = new URL(inRepo ? '../page/' : './out/', import.meta.url);
mkdirSync(page, { recursive: true });
// the page's code lives in page/ and is copied here for the public folder; only the fitted constants travel the other way
if (inRepo) copyFileSync(new URL('calibration.mjs', import.meta.url), new URL('calibration.mjs', page));

// data.json: up to 40 fitted runs per offered pack, newest first, with what a reader needs to judge them
const names = { '3090': 'RTX 3090', '3090ti': 'RTX 3090 Ti', '4090': 'RTX 4090', '4090-48': 'RTX 4090 48 GB', '4080s-32': 'RTX 4080 SUPER 32 GB', '5090': 'RTX 5090',
  '5080': 'RTX 5080', '5070ti': 'RTX 5070 Ti', '5070': 'RTX 5070', '5060ti': 'RTX 5060 Ti', '3060': 'RTX 3060', 'a4000': 'RTX A4000', 'a6000': 'RTX A6000',
  'pro4000': 'RTX PRO 4000', 'pro4500': 'RTX PRO 4500', 'pro5000': 'RTX PRO 5000 48 GB', 'pro5000-72': 'RTX PRO 5000 72 GB', 'pro6000': 'RTX PRO 6000',
  'pro6000s': 'RTX PRO 6000 Server', 'maxq': 'RTX PRO 6000 Max-Q', 'r9700': 'Radeon AI PRO R9700', '7900xtx': 'RX 7900 XTX', '9070': 'RX 9070', '9070xt': 'RX 9070 XT' };
const offered = new Set(models.flatMap((m) => m.profiles.map((p) => p.id)));
const packs = Object.fromEntries(models.flatMap((m) => m.profiles.map((p) => [p.id, p])));
// a run of the pack's own quantised file (or the same quantisation) ranks above a run of another file fitted with it
const same = (q, p) => q.includes(p.quant.split(' ')[0]) || q.includes(p.source.split('/').slice(3, 5).join('/'));
const quantLabel = (q) => q.replace(/\(([\w.-]+)\/[\w.-]+\)/, '($1)');
const anchors = JSON.parse(readFileSync(new URL('./anchors.json', import.meta.url), 'utf8')).runs;
const pick = anchors.filter((a) => a.fit && offered.has(a.profile) && a.decode && a.streams === 1 && cards[a.gpu.card] && !a.outlier)
  .sort((a, b) => String(b.date).localeCompare(String(a.date)));
const per = {};
const runs = [];
for (const a of pick) {
  if ((per[a.profile] = (per[a.profile] || 0) + 1) > 40) continue;
  const draft = (a.drafting || '').split(':')[0].toLowerCase();
  // the Server Edition keeps its own id: its bandwidth (1,597 GB/s) is not the Workstation's (1,792)
  runs.push({ p: a.profile, card: a.gpu.card === 'pro6000' ? 'ws6000' : a.gpu.card, vendor: ['r9700', '7900xtx', '9070', '9070xt'].includes(a.gpu.card) ? 'amd' : 'nvidia',
    q: quantLabel(a.quant), same: same(a.quant, packs[a.profile]),
    n: a.gpu.count, vram: cards[a.gpu.card][0] * a.gpu.count, d: +(+a.decode).toFixed(1), f: a.prefill ? Math.round(a.prefill) : null, ctx: a.decodeContext || null,
    g: `${a.gpu.count > 1 ? `${a.gpu.count} × ` : ''}${names[a.gpu.card]}`, h: [a.host.cpu, a.host.ram ? `${a.host.ram} GB` : null].filter(Boolean).join(', ') || 'host not stated',
    dr: draft === 'none' ? 'no drafting' : draft === 'mtp' ? 'MTP drafting' : draft === 'dspark' ? 'DSpark drafting' : '', u: a.url,
    who: a.measured_by === 'author' ? 'stack author' : (a.kind === 'localmaxxing' ? 'LocalMaxxing' : a.url.includes('x.com') ? 'X' : 'GitHub') });
}
writeFileSync(new URL('data.json', page), JSON.stringify({ checked: '2026-11-15', runs }));

// static figures: the Medium machine with GLM-5.3-Flash at 128K, one stream, as the page opens
const state = { model: 'glm', machine: 'medium', context: 131072, streams: 1, target: 20 };
// the same rule as the page: the largest pack that fits and keeps 20 tok/s, else the fastest that fits
const at = (mc, m, extra = {}) => {
  const g = gpus.find((x) => x.id === mc.gpu), pf = platforms.find((x) => x.id === mc.platform);
  const scored = m.profiles.filter((p) => stacks[p.stack].vendors.includes(g.vendor) && (!p.blackwell || g.blackwell))
    .map((p) => ({ p, r: calculate({ model: m, profile: p, gpu: g, count: mc.count, platform: pf, context: 131072, streams: 1, target: 20, ...extra }) }));
  return scored.find((x) => x.r.valid && x.r.decode.mid >= 20) || scored.filter((x) => x.r.valid).sort((a, b) => b.r.decode.mid - a.r.decode.mid)[0] || scored[0];
};
const mc = machines.find((x) => x.id === state.machine), m0 = models.find((x) => x.id === state.model), first = at(mc, m0);
for (const wide of [true, false]) {
  const w = wide ? 'wide' : 'narrow';
  writeFileSync(new URL(`fig-curve-${w}.svg`, page), curveSVG({ curve: first.r.curve, target: state.target, maxStreams: first.r.maxStreams, wide }));
  writeFileSync(new URL(`fig-memory-${w}.svg`, page), memorySVG({ m: first.r.memory, kind: first.p.kind, wide }));
  const tiers = machines.map((x) => ({ name: x.name, card: x.card, host: x.host, price: at(x, m0).r.price,
    rows: models.map((m) => { const b = at(x, m); return { short: m.short, mid: b.r.valid ? b.r.decode.mid : 0, why: b.r.memory.vramShort > 0 ? 'too big for VRAM' : b.r.memory.ramShort > 0 ? 'too big for RAM' : 'does not run' }; }) }));
  writeFileSync(new URL(`fig-tiers-${w}.svg`, page), tiersSVG({ tiers, wide }));
  writeFileSync(new URL(`fig-stack-${w}.svg`, page), stackSVG({ pairs: JSON.parse(readFileSync(new URL('./stack-comparison.json', import.meta.url), 'utf8')).pairs, wide }));
}
// the page without its script: the Medium machine's numbers written into the HTML, so they cannot drift from the calculator
const n0 = (x) => Math.round(x).toLocaleString('en-AU'), rng = (b) => `${n0(b.lo)}–${n0(b.hi)}`, r = first.r;
// what the speed fits used: one-stream writing and reading speeds outside the outliers, and the runs behind them
const used = JSON.parse(readFileSync(new URL('./fit-report.json', import.meta.url), 'utf8')).fitted.filter((x) => !x.outlier);
const byId = new Map(anchors.map((a) => [a.id, a]));
const writes = used.filter((x) => x.what === 'decode'), reads = used.filter((x) => x.what === 'prefill');
const fitted = new Set(used.map((x) => x.id)).size, long = writes.filter((x) => (byId.get(x.id).decodeContext || 0) >= 131072).length;
const passed = anchors.filter((a) => a.fit).length, multi = anchors.filter((a) => a.fit && a.streams > 1).length;
const fits = `After the outlier pass, ${n0(fitted)} one-stream runs feed the speed fits (${n0(writes.length)} writing and ${n0(reads.length)} reading speeds; ${long} of the writing speeds at 128K or longer) and ${multi} multi-stream records are kept as concurrency evidence.`;

// tables in the public Markdown, written between <!-- name --> markers so they always match the calculator
const block = (file, name, md) => {
  const u = new URL(file, import.meta.url), s = readFileSync(u, 'utf8'), re = new RegExp(`(<!-- ${name} -->)[\\s\\S]*?(<!-- /${name} -->)`);
  if (!re.test(s)) throw new Error(`${file} has no <!-- ${name} --> block`);
  writeFileSync(u, s.replace(re, (m, a, b) => `${a}\n${md}\n${b}`));
};
// a gap as the factor the median run is off by, either way, as a percentage: exp(median |log ratio|) - 1
const pct = (x) => (x == null ? '—' : `${Math.round((Math.exp(x) - 1) * 100)}%`), x2 = (lo, hi) => `${lo.toFixed(2)}–${hi.toFixed(2)} ×`;
block('README.md', 'accuracy', ['| Stack | Writing runs | Gap, fitted | Gap, held out (machines) | Band shown | Reading runs | Gap, fitted | Gap, held out (machines) | Band shown |',
  '|---|---:|---:|---:|---|---:|---:|---:|---|',
  ...Object.entries(calibration).map(([s, k]) => { const h = k.runs.heldOut;
    return `| ${stacks[s].name} | ${k.runs.decode} | ${pct(k.runs.medianError.decode)} | ${pct(h.medianError.decode)} (${h.machines.decode}) | ${x2(k.decodeLo, k.decodeHi)} | ${k.runs.prefill} | ${pct(k.runs.medianError.prefill)} | ${pct(h.medianError.prefill)} (${h.machines.prefill}) | ${x2(k.prefillLo, k.prefillHi)} |`; })].join('\n'));
const cell = (b) => (b.r.valid ? `${n0(b.r.decode.mid)} (${rng(b.r.decode)}), ${b.p.label}` : 'does not fit');
block('README.md', 'machines', [`| | ${machines.map((x) => x.name).join(' | ')} |`, `|---|${machines.map(() => '---').join('|')}|`,
  `| Main cards | ${machines.map((x) => x.card).join(' | ')} |`, `| Host | ${machines.map((x) => x.host).join(' | ')} |`,
  `| Price incl. GST | ${machines.map((x) => `A$${n0(at(x, m0).r.price)}`).join(' | ')} |`,
  ...models.map((m) => `| ${m.name} | ${machines.map((x) => cell(at(x, m))).join(' | ')} |`)].join('\n'));
// the ceiling: model-independent checks only (price, slots, card width, power), so the smallest model at 64K stands in
const small = models.find((m) => m.id === 'gemma26');
const ceiling = platforms.flatMap((pf) => [2, 3].map((count) => ({ pf, count, r: at({ gpu: 'maxq', count, platform: pf.id }, small, { context: 65536 }).r })));
const later = gpus.find((g) => g.id === 'maxq').later, crossed = ceiling.filter((x) => x.r.valid && x.r.later.total > 100000);
block('hardware.md', 'ceiling', ['| Host | 2 × Max-Q | 3 × Max-Q |', '|---|---|---|', ...platforms.map((pf) => `| ${pf.name} | ${ceiling.filter((x) => x.pf === pf).map(({ r }) =>
  r.valid ? `A$${n0(r.price)}, fits${r.notes.length ? ` (${r.notes.join(' ')})` : ''}` : `A$${n0(r.price)}: ${r.problems.join(' ')}`).join(' | ')} |`),
  '', `At the Max-Q's ${later.date} listing (A$${n0(later.price)} at e365, ${later.stock}), these machines that fit at the 15 November price would pass A$100,000: ${crossed.map((x) => `${x.count} × Max-Q with the ${x.pf.name} (A$${n0(x.r.later.total)})`).join('; ')}.`].join('\n'));
// the fitted-run count in the notes, from the same rule as the page's
const ramShort = anchors.filter((a) => /^RAM short/.test(a.why || '')).length;
for (const [file, re, text] of [
  ['README.md', /[\d,]+ of them, on comparable hardware[\s\S]*?(?:fit the model|concurrency evidence)\./, `${n0(passed)} of them, on comparable hardware and default settings, pass the checks in \`evidence.md\`. ${fits}`],
  ['evidence.md', /[\d,]+ records pass the checks below[\s\S]*?(?:fit the model|concurrency evidence)\./, `${n0(passed)} records pass the checks below. ${fits}`],
  ['evidence.md', /(?<=\| RAM too small for the pack, so experts came from the SSD \| )[\d,]+/, String(ramShort)]]) {
  const u = new URL(file, import.meta.url), s = readFileSync(u, 'utf8');
  if (!re.test(s)) throw new Error(`${file}: run count not found (${re})`);
  writeFileSync(u, s.replace(re, () => text));
}
if (!inRepo) { console.log(`data.json and figures written to out/ (${runs.length} runs; ${first.p.id}, ${Math.round(r.decode.mid)} tok/s, A$${Math.round(r.price)})`); process.exit(0); }
// function replacements throughout, so a '$' in the text (A$24,999) is never read as a group reference
const set = (html, id, text) => html.replace(new RegExp(`(id="${id}"[^>]*>)[^<]*(<)`), (m, a, b) => a + text + b);
let html = readFileSync(new URL('index.html', page), 'utf8');
html = set(html, 'price', `A$${n0(r.price)}`);
html = set(html, 'parts', `${mc.count} × ${gpus.find((g) => g.id === mc.gpu).short} A$${n0(r.parts.gpus)} · tools card A$${n0(r.parts.tools)} · host A$${n0(r.parts.host)} · power and network A$${n0(r.parts.site)}`);
html = set(html, 'price-date', r.dated);
html = set(html, 'decode', rng(r.decode));
html = set(html, 'prefill', rng(r.prefill));
html = set(html, 'prefill-note', `tokens/s · a full 128K prompt in ${rng(r.readSeconds)} s`);
html = set(html, 'max-streams', String(r.maxStreams));
// the limits list: each stack's held-out median gap, from the fit, so the range cannot drift from calibration.mjs. A stack
// measured on fewer than three machines is named apart: its held-out gap says nothing about other machines.
const gap = (k, key) => Math.round((Math.exp(k.runs.heldOut.medianError[key]) - 1) * 100);
const gaps = (key) => { const v = Object.values(calibration).filter((k) => k.runs.heldOut.machines[key] >= 3).map((k) => gap(k, key)); return `${Math.min(...v)}–${Math.max(...v)}%`; };
const few = Object.values(calibration).filter((k) => k.runs.heldOut.machines.prefill < 3);
if (few.length !== 1) throw new Error(`the limits list names one stack measured on one machine, not ${few.length}`);
html = html.replace(/(<ul class="stats limits" id="limit-list">\s*<li>)[\s\S]*?(<\/li>)/, (m, a, b) => `${a}<b>${gaps('decode')}</b><span>median miss of the estimated writing speed per stack, on machines the fit had not seen; ${gaps('prefill')} for reading. One stack was measured on one machine only (${gap(few[0], 'prefill')}% for reading). The range beside each estimate covers about eight in ten such runs. All one stream; more streams are extrapolated</span>${b}`);
html = set(html, 'streams-note', `each about 20 tok/s or more at 128K, mid estimate; ${r.maxStreamsLo} at the low end`);
html = set(html, 'max-context', `${Math.round(r.maxContext / 1024)}K`);
html = html.replace(/(<p class="static-note">)[^<]*(<)/, (m, a, b) => `${a}The ${mc.name} machine (${mc.spec}) running ${m0.name}, one stream at 128K context. The calculator needs JavaScript.${b}`);
html = html.replace(/(<p class="label basis" id="basis">)[^<]*(<)/, (m, a, b) => `${a}Calculator · six quantised models · Australian prices incl. GST · speeds fitted to ${n0(fitted)} first-hand runs${b}`);
html = html.replace(/(<li><span class="label">Measured<\/span>)[\s\S]*?(<\/li>)/, (m, a, b) => `${a}<b>${n0(fitted)} first-hand runs</b>One stream each: ${n0(writes.length)} writing and ${n0(reads.length)} reading speeds, only ${long} of them writing at 128K or more. From GitHub, X and the LocalMaxxing leaderboard, each with its hardware and settings.${b}`);
html = html.replace(/(<li id="finding"><span class="label">[^<]*<\/span>)[\s\S]*?(<\/li>)/, (m, a, b) => `${a}An <mark>A$${n0(r.price)}</mark> machine with one 96&nbsp;GB card, plus a 16&nbsp;GB tools card, runs GLM-5.3-Flash, a 320-billion-parameter model, at an estimated ${n0(r.decode.mid)} tokens per second (${rng(r.decode)}) for one 128K-token conversation: its experts live in RAM as well as on the card.${b}`);
const alt = (re, text) => { html = html.replace(re, (m, a) => `${a}${text}"`); };
alt(/(<img src="fig-curve-wide\.svg"[^>]*alt=")[^"]*"/, `Each stream writes about ${n0(r.curve[0].mid)} tokens per second alone, falling as more run at once; at the middle of the range ${r.maxStreams} keep 20 tokens per second each, at its low end ${r.maxStreamsLo}.`);
alt(/(<img src="fig-memory-wide\.svg"[^>]*alt=")[^"]*"/, `VRAM holds the dense weights, the context and ${n0(r.memory.cache)} GB of experts; RAM holds the rest of the experts.`);
alt(/(<img src="fig-tiers-wide\.svg"[^>]*alt=")[^"]*"/, 'Estimated writing speed of each model on the Small, Medium and Large machines at 128K context.');
alt(/(<img src="fig-stack-wide\.svg"[^>]*alt=")[^"]*"/, 'Measured: on one computer, an expert-cache stack with its default drafting wrote three to five times faster than a general GGUF runner without drafting; on two different machines, three times.');
writeFileSync(new URL('index.html', page), html);
console.log(`data.json: ${runs.length} runs; static figures for ${mc.name} with ${m0.name}: ${first.p.id}, ${Math.round(first.r.decode.mid)} tok/s, A$${Math.round(first.r.price)}`);
