// 5x3, 10 lines. 潜水员 W: wild on reels 2–5. 宝箱 M: carries a cash value (× bet), pays nothing by itself.
// 船舵 X scatter anywhere: 3/4/5 -> 10/15/20 free spins (+ 2/10/50× bet).
// Free spins: every 潜水员 collects all 宝箱 values on screen × level multiplier; every 4 divers -> next level
// (+10 spins, multiplier 1 -> 2 -> 3 -> 10).
function makeDiver(cfg, rnd) {
  const mk = (w) => { const ks = Object.keys(w); return { ks, w, tot: ks.reduce((s, k) => s + w[k], 0) }; };
  const B = cfg.BASE.map(mk), F = cfg.FREE.map(mk), mt = cfg.MONEY.reduce((s, m) => s + m[1], 0);
  const pick = (t) => { let x = rnd() * t.tot; for (const k of t.ks) { if ((x -= t.w[k]) < 0) return k; } return t.ks[0]; };
  const money = () => { let x = rnd() * mt; for (const m of cfg.MONEY) { if ((x -= m[1]) < 0) return m[0]; } return cfg.MONEY[0][0]; };
  const grid = (T) => T.map((t) => [0, 1, 2].map(() => { const s = pick(t); return s === "M" ? { s, v: money() } : { s }; }));
  function lines(g) {
    let win = 0; const hits = [];
    cfg.LINES.forEach((ln, li) => {
      const syms = ln.map((row, r) => g[r][ln[r]].s);
      let s0 = syms[0]; if (s0 === "M" || s0 === "X") return;
      // a run starting with wilds pays as the first real symbol, or as wilds if that pays more
      let n = 0, sym = null;
      for (let r = 0; r < 5; r++) { const s = syms[r]; if (s === "W") { n++; continue; } if (s === "M" || s === "X") break; if (!sym) { sym = s; n++; } else if (s === sym) n++; else break; }
      let wn = 0; while (wn < 5 && syms[wn] === "W") wn++;
      const pSym = sym && n >= 3 ? cfg.PAY[sym][n - 3] : 0, pW = wn >= 3 ? cfg.PAY.W[wn - 3] : 0;
      const p = Math.max(pSym, pW) / 10;
      if (p) { win += p; hits.push([li, pSym >= pW ? n : wn, pSym >= pW ? sym : "W", p]); }
    });
    return { win, hits };
  }
  const count = (g, s) => g.reduce((a, c) => a + c.filter((x) => x.s === s).length, 0);
  function free(n) {
    let left = n, total = 0, divers = 0, lvl = 0;
    while (left > 0) {
      left--;
      const g = grid(F);
      total += lines(g).win;
      const w = count(g, "W");
      if (w) {
        const cash = g.reduce((a, c) => a + c.filter((x) => x.s === "M").reduce((b, x) => b + x.v, 0), 0);
        total += cash * w * cfg.LEVELS[lvl];
        divers += w;
        while (lvl < cfg.LEVELS.length - 1 && divers >= (lvl + 1) * cfg.PER_LEVEL) { lvl++; left += cfg.LEVEL_SPINS; }
      }
    }
    return total;
  }
  function spin() {
    const g = grid(B);
    let total = lines(g).win;
    const sc = count(g, "X");
    let fs = 0;
    if (sc >= 3) { const k = Math.min(sc, 5); total += cfg.SCAT_PAY[k]; fs = free(cfg.SCAT[k]); total += fs; }
    return { total, fs, sc };
  }
  return { spin, lines, grid, free };
}
module.exports = { makeDiver };
if (require.main === module) {
  const cfg = require("./divercfg.js"), N = +process.argv[2] || 2e6, d = makeDiver(cfg, Math.random);
  let tot = 0, hit = 0, fsN = 0, fsTot = 0, big = 0;
  for (let i = 0; i < N; i++) { const r = d.spin(); tot += r.total; if (r.total) hit++; if (r.sc >= 3) { fsN++; fsTot += r.fs; } if (r.total >= 20) big++; }
  console.log("RTP", (tot / N * 100).toFixed(2) + "%", "hit 1/" + (N / hit).toFixed(2), "free 1/" + (N / fsN).toFixed(0), "free avg", (fsTot / fsN).toFixed(1) + "x", "free part", (fsTot / N * 100).toFixed(1) + "%", "≥20x 1/" + (N / big).toFixed(0));
}
