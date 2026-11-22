// SVG figures as strings, shared by the page script and the static-figure builder. Presentation attributes only (no CSS),
// so the same markup works inline and as a standalone file under the site's security policy. Text is never below 12 px.
const C = { ink: '#1A1816', mute: '#55504A', faint: '#8F8981', rule: '#DDD8D0', brand: '#B84F33', coral: '#F4A261', olive: '#606C38', sand: '#F5E6D3', paper: '#FAF9F7' };
const FONT = `font-family="'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"`;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const n0 = (x) => Math.round(x).toLocaleString('en-AU');
const f = (x) => +x.toFixed(1);
const text = (x, y, s, o = {}) => `<text x="${f(x)}" y="${f(y)}" font-size="${o.size || 12}" font-weight="${o.weight || 400}" fill="${o.fill || C.mute}" text-anchor="${o.anchor || 'start'}">${esc(s)}</text>`;
const svg = (w, h, title, desc, body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" ${FONT} font-size="12"><title>${esc(title)}</title><desc>${esc(desc)}</desc>${body}</svg>`;
const niceMax = (v) => { const steps = [10, 20, 25, 50, 100, 150, 200, 250, 300, 400, 500, 750, 1000]; return steps.find((s) => s >= v * 1.08) || Math.ceil(v / 500) * 500; };

/** Writing speed of each stream against the number of streams, with the error band and the reader's target. */
export function curveSVG({ curve, target, maxStreams, wide = true, width }) {
  const w = Math.round(width || (wide ? 520 : 340)), h = w >= 480 ? 200 : 196, L = 40, R = 14, T = 16, B = 34;
  // only the stream counts that fit in memory are drawn; the rest are marked as not fitting
  const N = curve.length, ok = curve.filter((p) => p.fits !== false), top = niceMax(Math.max(target, ...ok.map((p) => p.hi), 1));
  const X = (n) => L + (N === 1 ? 0.5 : (n - 1) / (N - 1)) * (w - L - R), Y = (v) => T + (1 - v / top) * (h - T - B);
  let body = '';
  for (const v of [0, top / 2, top]) body += `<line x1="${L}" x2="${w - R}" y1="${f(Y(v))}" y2="${f(Y(v))}" stroke="${C.rule}"/>` + text(L - 6, Y(v) + 4, n0(v), { anchor: 'end' });
  const ticks = N <= 8 ? curve.map((p) => p.n) : [1, 4, 8, 12, 16].filter((n) => n <= N);
  for (const n of ticks) body += text(X(n), h - B + 17, n, { anchor: 'middle' });
  body += text(L, h - 4, 'streams writing at once', { fill: C.faint });
  if (ok.length < N) {
    const xb = ok.length ? (X(ok.length) + X(ok.length + 1)) / 2 : L;
    body += `<rect x="${f(xb)}" y="${T}" width="${f(w - R - xb)}" height="${h - T - B}" fill="${C.ink}" fill-opacity="0.05"/>`;
    body += text(w - R - 4, T + 14, ok.length ? `more than ${ok.length} do not fit` : 'does not fit', { anchor: 'end', fill: C.mute });
  }
  if (ok.length) {
    const band = ok.map((p) => `${f(X(p.n))},${f(Y(p.hi))}`).join(' ') + ' ' + [...ok].reverse().map((p) => `${f(X(p.n))},${f(Y(p.lo))}`).join(' ');
    body += `<polygon points="${band}" fill="${C.coral}" fill-opacity="0.35"/>`;
    body += `<polyline points="${ok.map((p) => `${f(X(p.n))},${f(Y(p.mid))}`).join(' ')}" fill="none" stroke="${C.brand}" stroke-width="2.2" stroke-linejoin="round"/>`;
  }
  // the target's label sits under its line, or above it when the line runs close to the axis numbers
  const ty = Y(target) + 15 > h - B - 4 ? Y(target) - 5 : Y(target) + 15;
  body += `<line x1="${L}" x2="${w - R}" y1="${f(Y(target))}" y2="${f(Y(target))}" stroke="${C.ink}" stroke-dasharray="4 3"/>` + text(L + 4, ty, `${target} tok/s each`, { fill: C.ink, weight: 600 });
  if (maxStreams > 0 && maxStreams <= N) {
    const p = curve[maxStreams - 1], x = X(maxStreams), right = x > L + (w - L - R) * 0.55;
    body += `<circle cx="${f(x)}" cy="${f(Y(p.mid))}" r="5" fill="${C.brand}" stroke="#fff" stroke-width="1.5"/>`;
    body += text(right ? x - 8 : x + 8, Y(p.mid) - 9, `${maxStreams} at your speed`, { fill: C.brand, weight: 600, anchor: right ? 'end' : 'start' });
  }
  body += text(L, T - 4, 'tokens/s, each stream', { fill: C.faint });
  const last = ok[ok.length - 1];
  const desc = ok.length ? `Each stream writes ${n0(ok[0].mid)} tokens per second alone and ${n0(last.mid)} with ${last.n} together${ok.length < N ? `; more than ${last.n} do not fit in memory` : ''}. ${maxStreams} streams keep ${target} tokens per second each.` : 'This set-up does not fit in memory.';
  return svg(w, h, 'Writing speed of each stream as more run together', desc, body);
}

/** VRAM, RAM and SSD as three bars: what each holds and what is left; a mark at the capacity where the parts overrun it. */
export function memorySVG({ m, kind, wide = true, width }) {
  const w = Math.round(width || (wide ? 520 : 340)), row = 46, L = 48, R = 8, h = 3 * row + 6, bw = w - L - R;
  const GB = (x) => (x >= 100 ? n0(x) : (+x.toFixed(1)).toString());
  const rows = [
    { name: 'VRAM', total: m.vram, parts: kind === 'resident'
        ? [['weights', m.weights, C.ink], ['context', m.kv, C.coral], ['runtime', m.reserve || 0, C.faint]]
        : [['dense', m.weights, C.ink], ['context', m.kv, C.coral], ['runtime', m.reserve || 0, C.faint], ['experts', m.cache, C.olive]] },
    { name: 'RAM', total: m.ram, parts: kind === 'resident'
        ? [['system', 16, C.faint]]
        : [['experts', m.ramExperts, C.olive], ['context', m.kvRam || 0, C.coral], ['system', m.ramSystem, C.faint]] },
    { name: 'SSD', total: Math.max(m.ssd, 1), parts: m.ssd ? [['lookup table', m.ssd, C.mute]] : [] }
  ];
  let body = '';
  rows.forEach((r, i) => {
    const y = i * row + 4, scale = Math.max(r.total, r.parts.reduce((t, p) => t + p[1], 0));
    body += text(0, y + 12, r.name, { weight: 600, fill: C.ink });
    body += `<rect x="${L}" y="${y + 2}" width="${bw}" height="13" fill="${C.ink}" fill-opacity="0.07"/>`;
    let x = L;
    for (const [, v, col] of r.parts) { const pw = bw * v / scale; if (pw > 0.5) body += `<rect x="${f(x)}" y="${y + 2}" width="${f(pw)}" height="13" fill="${col}"/>`; x += pw; }
    if (scale > r.total + 0.5) body += `<rect x="${f(L + bw * r.total / scale)}" y="${y}" width="2" height="17" fill="${C.brand}"/>`;
    const used = r.parts.reduce((t, p) => t + p[1], 0);
    const label = r.name === 'SSD' ? (m.ssd ? `${GB(m.ssd)} GB lookup table, read a few rows per token` : 'model files only')
      : `${r.parts.filter((p) => p[1] > 0.05).map((p) => `${p[0]} ${GB(p[1])}`).join(' · ')} of ${GB(r.total)} GB${used > r.total + 0.5 ? ' · short' : ''}`;
    // on a phone the label starts at the left edge, under the row name, so the longest one still fits
    body += text(w < 480 ? 0 : L, y + 32, label, { fill: used > r.total + 0.5 ? C.brand : C.mute });
  });
  const desc = rows.map((r) => `${r.name} ${GB(r.total)} GB: ${r.parts.map((p) => `${p[0]} ${GB(p[1])} GB`).join(', ') || 'files only'}`).join('. ');
  return svg(w, h, 'Where the model lives', desc, body);
}

/** Three machines side by side: estimated writing speed of each model at 128K, or why it does not fit. */
export function tiersSVG({ tiers, wide = true }) {
  const cols = wide ? 3 : 1, colW = wide ? 216 : 340, gap = wide ? 20 : 0, rowH = 30, head = 78, panelH = head + tiers[0].rows.length * rowH + 8;
  const w = wide ? cols * colW + (cols - 1) * gap : colW, h = wide ? panelH : tiers.length * (panelH + 16);
  const top = niceMax(Math.max(...tiers.flatMap((t) => t.rows.map((r) => r.mid || 0))));
  let body = '';
  tiers.forEach((t, i) => {
    const x0 = wide ? i * (colW + gap) : 0, y0 = wide ? 0 : i * (panelH + 16);
    body += `<line x1="${x0}" x2="${x0 + colW}" y1="${y0 + 0.5}" y2="${y0 + 0.5}" stroke="${C.ink}"/>`;
    body += text(x0, y0 + 20, t.name, { size: 15, weight: 700, fill: C.ink }) + text(x0 + colW, y0 + 20, `A$${n0(t.price)}`, { anchor: 'end', weight: 600, fill: C.brand, size: 13 });
    body += text(x0, y0 + 40, t.card, { fill: C.mute }) + text(x0, y0 + 58, t.host, { fill: C.mute });
    t.rows.forEach((r, j) => {
      const y = y0 + head + j * rowH, bx = x0 + 104, bwid = colW - 104 - 30;
      body += text(x0, y + 11, r.short, { fill: C.ink });
      if (r.mid) {
        body += `<rect x="${bx}" y="${y + 1}" width="${f(bwid * r.mid / top)}" height="12" fill="${C.olive}"/>`;
        body += text(bx + bwid * r.mid / top + 5, y + 11, n0(r.mid), { fill: C.ink, weight: 600 });
      } else body += text(bx, y + 11, r.why, { fill: C.faint });
    });
  });
  const desc = tiers.map((t) => `${t.name}, A$${n0(t.price)}: ` + t.rows.map((r) => `${r.short} ${r.mid ? n0(r.mid) + ' tokens/s' : r.why}`).join(', ')).join('. ');
  return svg(w, h, 'Writing speed of each model on three machines, at 128K context', desc, body);
}

/** One box, two ways to run the same model: measured ranges side by side. */
export function stackSVG({ pairs, wide = true }) {
  const w = wide ? 640 : 340, L = wide ? 190 : 0, R = 64, rowH = wide ? 26 : 44, groupGap = 18;
  const h = pairs.length * (2 * rowH + groupGap + 20) + 6;
  let body = '', y = 6;
  for (const g of pairs) {
    const top = niceMax(Math.max(...g.rows.map((r) => r.hi)));
    body += text(0, y + 12, g.title, { weight: 700, fill: C.ink, size: 13 });
    y += 20;
    for (const r of g.rows) {
      const x0 = L, span = w - L - R, yy = y + (wide ? 4 : 2);
      if (wide) body += text(L - 10, yy + 11, r.name, { anchor: 'end', fill: C.ink });
      else body += text(0, yy + 11, r.name, { fill: C.ink });
      const by = wide ? yy : yy + 16;
      body += `<rect x="${x0}" y="${by}" width="${f(span * r.hi / top)}" height="13" fill="${r.main ? C.brand : C.faint}" fill-opacity="0.3"/>`;
      body += `<rect x="${x0}" y="${by}" width="${f(span * r.lo / top)}" height="13" fill="${r.main ? C.brand : C.faint}"/>`;
      body += text(x0 + span * r.hi / top + 6, by + 11, r.lo === r.hi ? n0(r.hi) : `${n0(r.lo)}–${n0(r.hi)}`, { fill: C.ink, weight: 600 });
      y += rowH;
    }
    y += groupGap;
  }
  const desc = pairs.map((g) => `${g.title}: ` + g.rows.map((r) => `${r.name} ${n0(r.lo)} to ${n0(r.hi)}`).join('; ')).join('. ');
  return svg(w, h, 'Two ways to run the same model on the same computer', desc, body);
}
