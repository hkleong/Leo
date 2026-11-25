const outer = { D: 2, F: 3, H: 4, L: 4, A: 5, K: 5, Q: 6, J: 6, T: 6, S: 1, C: 10 };
const mid = { W: 6, D: 2, F: 3, H: 4, L: 4, A: 5, K: 5, Q: 6, J: 6, T: 2, S: 2, C: 10 };
module.exports = {
  COUNTS: [outer, mid, mid, mid, outer],
  PAY: { D: [0.86, 2.7, 8.7], F: [0.54, 1.73, 5.4], H: [0.42, 1.4, 4.3], L: [0.33, 0.87, 3.45], A: [0.17, 0.42, 1.73], K: [0.17, 0.42, 1.73], Q: [0.085, 0.26, 1.4], J: [0.085, 0.26, 1.4], T: [0.085, 0.26, 1.4] },
  COIN: [{ x: 0.3, w: 30 }, { x: 0.5, w: 25 }, { x: 1, w: 15 }, { x: 1.5, w: 10 }, { x: 2, w: 6 }, { x: 3, w: 4 }, { jp: "MINI", w: 1.05 }, { jp: "MINOR", w: 0.525 }, { jp: "MAJOR", w: 0.175 }],
  P_COIN: 0.03,
  FS: { 3: 8, 4: 12, 5: 20 },
  FS_MULT: 2,
  JP_BASE: { MINI: 10, MINOR: 25, MAJOR: 150, GRAND: 1000 },
  JP_GROW: { MAJOR: 0.01, GRAND: 0.02 },
};
