// 5x3, 243 ways, wild on reels 2-4, scatter free spins, coin hold & spin with 4 jackpots
function makeEngine(cfg, rnd) {
  const { COUNTS, PAY, COIN, P_COIN, FS, FS_MULT } = cfg;
  const strips = COUNTS.map((cnt, r) => {
    const a = []; for (const k in cnt) for (let i = 0; i < cnt[k]; i++) a.push(k);
    let x = 7 + r * 13; for (let i = a.length - 1; i > 0; i--) { x = (x * 1103515245 + 12345) % 2147483648; const j = x % (i + 1); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  });
  const coinTotal = COIN.reduce((s, c) => s + c.w, 0);
  function coinValue() { let x = rnd() * coinTotal; for (const c of COIN) { if ((x -= c.w) < 0) return c; } return COIN[0]; }
  function spinGrid() {
    return strips.map((st) => { const s = Math.floor(rnd() * st.length); return [0, 1, 2].map((k) => st[(s + k) % st.length]); });
  }
  function evalWays(grid) {
    let win = 0; const hits = [];
    for (const sym in PAY) {
      let ways = 1, n = 0; const cells = [];
      for (let r = 0; r < 5; r++) {
        const rows = []; grid[r].forEach((g, i) => { if (g === sym || (g === "W" && r > 0)) rows.push(i); });
        if (!rows.length) break; ways *= rows.length; n++; rows.forEach((i) => cells.push([r, i]));
      }
      if (n >= 3) { const m = PAY[sym][n - 3] * ways; win += m; hits.push({ sym, n, ways, m, cells }); }
    }
    return { win, hits };
  }
  const count = (grid, s) => grid.reduce((t, col) => t + col.filter((g) => g === s).length, 0);
  function holdSpin(grid) {          // returns {mult, jackpots[]} in multiples of bet (jackpots separate)
    const locked = new Map(); let respins = 3; const log = [];
    grid.forEach((col, r) => col.forEach((g, i) => { if (g === "C") locked.set(r * 3 + i, coinValue()); }));
    while (respins > 0 && locked.size < 15) {
      let got = false;
      for (let p = 0; p < 15; p++) if (!locked.has(p) && rnd() < P_COIN) { locked.set(p, coinValue()); got = true; }
      respins = got ? 3 : respins - 1;
    }
    let mult = 0; const jps = [];
    for (const c of locked.values()) { if (c.jp) jps.push(c.jp); else mult += c.x; }
    if (locked.size === 15) jps.push("GRAND");
    return { mult, jps, locked };
  }
  return { strips, spinGrid, evalWays, count, holdSpin, coinValue };
}
module.exports = { makeEngine };
