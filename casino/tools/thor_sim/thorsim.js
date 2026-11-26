// 6x5 pay anywhere, tumbles; 雷球 multipliers sum at the end of a tumble sequence (only if it won).
// 4+ 雷电盾徽 → 15 free spins where every winning spin adds its 雷球 to a running total multiplier.
const COLS = 6, ROWS = 5;
function makeThor(cfg, rnd, ante) {
  const w = { ...cfg.W }; if (ante) w.S *= cfg.ANTE_S;
  const wf = { ...cfg.W, M: cfg.FS_M };                   // free spins use their own reels: more 雷球
  const ks = Object.keys(w), mt = cfg.MULTS.reduce((a, m) => a + m[1], 0);
  const mult = () => { let x = rnd() * mt; for (const m of cfg.MULTS) { if ((x -= m[1]) < 0) return m[0]; } return 2; };
  let cur = w;
  const tot = (o) => ks.reduce((a, k) => a + o[k], 0); const TB = tot(w), TF = tot(wf);
  const draw = () => { let x = rnd() * (cur === w ? TB : TF); for (const k of ks) { if ((x -= cur[k]) < 0) return k === "M" ? { k, v: mult() } : { k }; } return { k: ks[0] }; };
  const pay = (k, n) => { const p = cfg.PAY[k]; if (!p || n < 8) return 0; return n >= 12 ? p[2] : n >= 10 ? p[1] : p[0]; };
  const newGrid = () => Array.from({ length: COLS }, () => Array.from({ length: ROWS }, () => draw()));
  // one spin: returns { win (before multipliers), msum, stars }
  function spin(grid) {
    let g = grid || newGrid(), win = 0;
    for (;;) {
      const cnt = {}; g.forEach((c) => c.forEach((x) => { cnt[x.k] = (cnt[x.k] || 0) + 1; }));
      const ws = []; let w0 = 0; for (const k in cnt) { const p = pay(k, cnt[k]); if (p) { w0 += p; ws.push(k); } }
      if (!w0) break; win += w0;
      g = g.map((col) => { const keep = col.filter((x) => !ws.includes(x.k)); while (keep.length < ROWS) keep.unshift(draw()); return keep; });
    }
    let msum = 0, stars = 0; g.forEach((c) => c.forEach((x) => { if (x.k === "M") msum += x.v; if (x.k === "S") stars++; }));
    return { win, msum, stars };
  }
  function free(n) {
    let left = n, total = 0, acc = 0; cur = wf;
    while (left > 0) { left--; const r = spin(); if (r.win) { acc += r.msum; total += r.win * (acc || 1); } if (r.stars >= 3) left += cfg.FS_RE; }
    cur = w; return total;
  }
  function base() {
    const r = spin(); let w = r.win * (r.win && r.msum ? r.msum : 1);
    if (r.stars >= 4) { w += cfg.SCAT_PAY[Math.min(r.stars, 6)]; w += free(cfg.FS); }
    return { w, fs: r.stars >= 4 };
  }
  // bought feature: a spin guaranteed to show 4 雷电盾徽, then the free spins
  function buy() { const r = spin(); return r.win * (r.win && r.msum ? r.msum : 1) + cfg.SCAT_PAY[Math.max(4, Math.min(r.stars, 6))] + free(cfg.FS); }
  return { base, buy, free, spin };
}
module.exports = { makeThor };
if (require.main === module) {
  const cfg = require("./thorcfg.js"), N = +process.argv[2] || 1e6, mode = process.argv[3] || "base";
  const B = makeThor(cfg, Math.random, mode === "ante");
  if (mode === "buy") { let t = 0; for (let i = 0; i < N; i++) t += B.buy(); console.log("BUY RTP", (t / N / cfg.BUY * 100).toFixed(2) + "%  avg", (t / N).toFixed(1) + "x"); }
  else { let t = 0, hit = 0, fs = 0, big = 0; for (let i = 0; i < N; i++) { const r = B.base(); t += r.w; if (r.w) hit++; if (r.fs) fs++; if (r.w >= 20) big++; }
    const cost = mode === "ante" ? cfg.ANTE : 1;
    console.log(mode.toUpperCase(), "RTP", (t / N / cost * 100).toFixed(2) + "%  hit 1/" + (N / hit).toFixed(2) + "  FS 1/" + Math.round(N / fs) + "  20x+ 1/" + Math.round(N / big)); }
}
