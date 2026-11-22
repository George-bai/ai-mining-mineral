// The calculator's answers on the cases of the pre-publication review of 22 November 2026. Run from this folder:
// node check.mjs   (Node 20+, no dependencies). It stops at the first case that fails.
import assert from 'node:assert/strict';
import { models, gpus, platforms, machines, BUDGET } from './catalog.mjs';
import { calculate } from './calculate.mjs';

const G = (id) => gpus.find((g) => g.id === id), P = (id) => platforms.find((p) => p.id === id), M = (id) => models.find((m) => m.id === id);
const pack = (m, id) => M(m).profiles.find((p) => p.id === id);
const run = (over) => calculate({ model: M('glm'), profile: pack('glm', 'glm-maya-m'), gpu: G('maxq'), count: 1, platform: P('sp3-256'), context: 131072, streams: 1, target: 20, ...over });
const near = (x, y, tol, what) => assert.ok(Math.abs(x - y) <= tol, `${what}: ${x} against ${y}`);

// 1. Qwen3.8-27B GGUF on one RTX 3090, one stream at 128K: the 1.6 GB runtime reserve makes it 1.1 GB short of VRAM,
// and the longest context that fits is 108K
const q = run({ model: M('qwen27'), profile: pack('qwen27', 'qwen27-llama'), gpu: G('3090'), platform: P('am5-128') });
near(q.memory.weights + q.memory.kv + q.memory.reserve, 26.914, 0.001, '3090: weights, context and reserve');
assert.equal(q.memory.reserve, 1.6);
near(q.memory.vramShort, 1.144, 0.001, '3090: VRAM short');
assert.equal(q.valid, false); assert.equal(q.builds, true);
assert.equal(q.maxContext, 108 * 1024, '3090: longest context that fits');

// 2. GLM-5.3-Flash on the Medium machine at 128K: about 56 tokens/s for one stream, 12 each for eight; a ninth request
// waits in a queue rather than making the machine fail
const one = run({}), eight = run({ streams: 8 }), nine = run({ streams: 9 });
near(one.decode.mid, 55.7, 0.5, 'one stream'); near(eight.decode.mid, 12.4, 0.5, 'eight streams');
assert.equal(nine.valid, true, nine.problems.join(' '));
assert.equal(nine.active, 8); assert.equal(nine.queued, 1);
assert.equal(nine.decode.mid, eight.decode.mid, 'the queued request does not slow the eight being written');
assert.ok(nine.notes.some((t) => /1 more waits in a queue/.test(t)));

// 3. DeepSeek-V4.1-Flash-1017 on Strata, one stream at 128K beside 128 GB of DDR5: RAM holds only the experts the cards
// do not hold, plus the engine and system. The reviewer's run of the stack's own planner gave 116.8 GB and 65.1 GB.
for (const [gpu, id, planner] of [['pro4500', 'ds-strata-200', 116.8], ['maxq', 'ds-strata-225', 65.1]]) {
  const r = run({ model: M('deepseek'), profile: pack('deepseek', id), gpu: G(gpu), platform: P('am5-128') }), m = r.memory;
  assert.equal(r.valid, true, `${gpu} ${id}: ${r.problems.join(' ')}`);
  near(m.ramExperts, pack('deepseek', id).experts - m.cache, 1e-9, `${gpu} ${id}: experts in RAM`);
  near(m.ramUsed, planner, 3, `${gpu} ${id}: RAM against the planner`);
}

// 4. Prices: the 15 November example, and the same machines at the Max-Q's 22 November listing (A$27,999)
const price = (id) => { const mc = machines.find((x) => x.id === id); return run({ gpu: G(mc.gpu), count: mc.count, platform: P(mc.platform) }); };
assert.equal(price('medium').price, 43568); assert.equal(price('medium').later.total, 46568);
assert.equal(price('large').price, 79906, 'Large: the board has 10GbE, so no network card');
assert.equal(price('large').later.total, 85906);
assert.equal(price('small').price, 16675, 'Small: the board has 10GbE, so no network card');
const three = run({ model: M('gemma26'), profile: pack('gemma26', 'gemma26-llama'), count: 3, platform: P('sp3-512'), context: 65536 });
assert.equal(three.price, 99116, 'four cards leave the server no slot for a network card');
assert.ok(three.price <= BUDGET && three.later.total > BUDGET, 'three Max-Q cards on the 512 GB server pass A$100,000 at the later price');

console.log('check.mjs: every review case holds');
