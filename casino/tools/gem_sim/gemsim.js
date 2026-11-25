// 6x5 cascading pay-anywhere slot: 8+ of a gem anywhere pays; winners shatter, gems fall, new ones drop.
// Cascade multiplier ladder per spin; 4+ stars -> free spins where the ladder carries over.
const COLS = 6, ROWS = 5;
function makeGem(cfg, rnd) {
  const syms = Object.keys(cfg.W), tot = syms.reduce((s, k) => s + cfg.W[k], 0);
  const draw = () => { let x = rnd() * tot; for (const k of syms) { if ((x -= cfg.W[k]) < 0) return k; } return syms[0]; };
  const payFor = (k, n) => { const p = cfg.PAY[k]; if (!p || n < 8) return 0; return n >= 12 ? p[2] : n >= 10 ? p[1] : p[0]; };
  // grid[c][r], r=0 is the top
  const newGrid = () => Array.from({ length: COLS }, () => Array.from({ length: ROWS }, draw));
  function evalGrid(g) {
    const cnt = {}; g.forEach((col) => col.forEach((k) => { cnt[k] = (cnt[k] || 0) + 1; }));
    let win = 0; const syms = [];
    for (const k in cnt) { const w = payFor(k, cnt[k]); if (w) { win += w; syms.push(k); } }
    return { win, syms };
  }
  function tumble(g, syms) {
    return g.map((col) => { const keep = col.filter((k) => !syms.includes(k)); while (keep.length < ROWS) keep.unshift(draw()); return keep; });
  }
  // one spin: returns { win, steps:[{grid, win, mult, syms}], stars, ladder }
  function spin(ladderStart) {
    let g = newGrid(), lad = ladderStart || 0, total = 0; const steps = [];
    for (;;) {
      const e = evalGrid(g);
      if (!e.win) { steps.push({ grid: g, win: 0, mult: 0, syms: [] }); break; }
      const mult = cfg.LADDER[Math.min(lad, cfg.LADDER.length - 1)];
      total += e.win * mult; steps.push({ grid: g, win: e.win * mult, mult, syms: e.syms });
      lad++; g = tumble(g, e.syms);
    }
    const stars = g.reduce((s, col) => s + col.filter((k) => k === "S").length, 0);
    return { win: total, steps, stars, ladder: lad };
  }
  return { spin, newGrid, evalGrid, tumble, draw, payFor };
}
module.exports = { makeGem, COLS, ROWS };
if (require.main === module) {
  const cfg = require(process.argv[3] || './gemcfg.js');
  let seed = +process.argv[4] || 99; const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
  const G = makeGem(cfg, rnd); const N = +process.argv[2] || 1e6;
  let paid = 0, base = 0, fs = 0, hits = 0, ft = 0, big = 0, maxW = 0, casc = 0;
  for (let i = 0; i < N; i++) {
    const r = G.spin(0); let w = r.win; base += w; casc += r.steps.length - 1;
    if (r.stars >= 4) { ft++; let left = cfg.FS, lad = 0; while (left-- > 0) { const f = G.spin(lad); lad = cfg.FS_KEEP ? f.ladder : 0; fs += f.win; w += f.win; if (f.stars >= 3) left += cfg.FS_RE; } }
    if (w > 0) hits++; if (w >= 20) big++; if (w > maxW) maxW = w; paid += w;
  }
  console.log(`RTP ${(paid / N * 100).toFixed(2)}% | base ${(base / N * 100).toFixed(1)} free ${(fs / N * 100).toFixed(1)} | hit 1/${(N / hits).toFixed(2)} | cascades/spin ${(casc / N).toFixed(2)} | FS 1/${Math.round(N / ft)} | 20x+ 1/${Math.round(N / big)} | max ${maxW.toFixed(0)}x`);
}
