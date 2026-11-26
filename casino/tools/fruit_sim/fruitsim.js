// 5x3, 20 lines. 百搭 W on reels 2–4 expands to the whole reel and holds for a respin (a new W adds another respin).
// 3 转轮 X on reels 1, 3, 5 -> prize wheel (× total bet). Line pays are × line bet (= bet / 20).
function makeFruit(cfg, rnd) {
  const tables = cfg.REELS.map((w) => { const ks = Object.keys(w), tot = ks.reduce((s, k) => s + w[k], 0); return { ks, w, tot }; });
  const draw = (r) => { const t = tables[r]; let x = rnd() * t.tot; for (const k of t.ks) { if ((x -= t.w[k]) < 0) return k; } return t.ks[0]; };
  const newGrid = (held) => [0, 1, 2, 3, 4].map((r) => (held && held[r] ? ["W", "W", "W"] : [draw(r), draw(r), draw(r)]));
  function lines(g) {
    let win = 0; const hits = [];
    cfg.LINES.forEach((ln, li) => {
      const s0 = g[0][ln[0]]; if (s0 === "X" || s0 === "W") return;
      let n = 1; while (n < 5) { const s = g[n][ln[n]]; if (s === s0 || s === "W") n++; else break; }
      if (n >= 3) { const p = cfg.PAY[s0][n - 3] / 20; win += p; hits.push([li, n, s0, p]); }
    });
    return { win, hits };
  }
  // full spin -> total win in × bet
  function spin() {
    let g = newGrid(null), held = [0, 0, 0, 0, 0], total = 0, respins = 0;
    const sc = [0, 2, 4].filter((r) => g[r].includes("X")).length;
    const expand = () => { let n = 0; for (const r of [1, 2, 3]) if (!held[r] && g[r].includes("W")) { held[r] = 1; g[r] = ["W", "W", "W"]; n++; } return n; };
    let fresh = expand();
    total += lines(g).win;
    while (fresh) { respins++; g = newGrid(held); fresh = expand(); total += lines(g).win; }
    let wheel = 0;
    if (sc >= 3) { wheel = cfg.WHEEL[Math.floor(rnd() * cfg.WHEEL.length)]; total += wheel; }
    return { total, respins, sc, wheel };
  }
  return { spin, lines, newGrid };
}
module.exports = { makeFruit };
if (require.main === module) {
  const cfg = require("./fruitcfg.js");
  const N = +process.argv[2] || 2e6;
  const f = makeFruit(cfg, Math.random);
  let tot = 0, hit = 0, resp = 0, wheel = 0, wheelN = 0, big = 0, sq = 0;
  for (let i = 0; i < N; i++) { const r = f.spin(); tot += r.total; sq += r.total * r.total; if (r.total > 0) hit++; if (r.respins) resp++; if (r.wheel) { wheel += r.wheel; wheelN++; } if (r.total >= 20) big++; }
  console.log("RTP", (tot / N * 100).toFixed(2) + "%", "hit 1/" + (N / hit).toFixed(2), "respin 1/" + (N / resp).toFixed(1), "wheel 1/" + (N / wheelN).toFixed(0), "wheel part", (wheel / N * 100).toFixed(2) + "%", "≥20x 1/" + (N / big).toFixed(0), "sd", Math.sqrt(sq / N - (tot / N) ** 2).toFixed(2));
}
