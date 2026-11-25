const { makeEngine } = require('./engine.js'); const cfg = require('./cfg.js');
let seed = 2024; const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
const E = makeEngine(cfg, rnd); const N = +process.argv[2];
const jp = { ...cfg.JP_BASE }; let paid = 0, base = 0, fs = 0, hs = 0, ft = 0, ht = 0, hits = 0, big = 0; const jc = {};
const hold = (g) => { ht++; const h = E.holdSpin(g); let w = h.mult; for (const j of h.jps) { w += jp[j]; jc[j] = (jc[j] || 0) + 1; if (cfg.JP_GROW[j]) jp[j] = cfg.JP_BASE[j]; } hs += w; return w; };
for (let i = 0; i < N; i++) {
  jp.MAJOR += cfg.JP_GROW.MAJOR; jp.GRAND += cfg.JP_GROW.GRAND;
  const g = E.spinGrid(); let w = E.evalWays(g).win; base += w; if (E.count(g, "C") >= 6) w += hold(g);
  const sc = E.count(g, "S"); if (sc >= 3) { ft++; let left = cfg.FS[Math.min(sc, 5)]; while (left-- > 0) { const fg = E.spinGrid(); let fw = E.evalWays(fg).win * cfg.FS_MULT; const s2 = E.count(fg, "S"); if (s2 >= 3) left += cfg.FS[Math.min(s2, 5)]; if (E.count(fg, "C") >= 6) fw += hold(fg); fs += fw; w += fw; } }
  if (w > 0) hits++; if (w >= 20) big++; paid += w;
}
console.log(`RTP ${(paid / N * 100).toFixed(2)}% | base ${(base / N * 100).toFixed(1)} free ${(fs / N * 100).toFixed(1)} hold+jackpots ${(hs / N * 100).toFixed(1)}`);
console.log(`hit rate 1 in ${(N / hits).toFixed(2)} | 20x+ wins 1 in ${Math.round(N / big)} | free spins 1 in ${Math.round(N / ft)} | hold&spin 1 in ${Math.round(N / ht)} | jackpots hit ${JSON.stringify(jc)}`);
