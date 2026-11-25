const outer = { D: 2, F: 3, H: 4, L: 4, A: 5, K: 5, Q: 6, J: 6, T: 6, S: 1, C: 8 };
const mid = { W: 6, D: 2, F: 3, H: 4, L: 4, A: 5, K: 5, Q: 6, J: 6, T: 2, S: 2, C: 8 };
module.exports = {
  COUNTS: [outer, mid, mid, mid, outer],
  PAY: { D: [0.78, 2.4, 7.8], F: [0.48, 1.55, 4.8], H: [0.38, 1.25, 3.85], L: [0.29, 0.78, 3.1], A: [0.15, 0.38, 1.55], K: [0.15, 0.38, 1.55], Q: [0.075, 0.23, 1.25], J: [0.075, 0.23, 1.25], T: [0.075, 0.23, 1.25] },
  COIN: [{ x: 1, w: 30 }, { x: 2, w: 25 }, { x: 3, w: 15 }, { x: 5, w: 10 }, { x: 8, w: 6 }, { x: 10, w: 4 }, { jp: "MINI", w: 3 }, { jp: "MINOR", w: 1.5 }, { jp: "MAJOR", w: 0.5 }],
  P_COIN: 0.03,
  FS: { 3: 8, 4: 12, 5: 20 },
  FS_MULT: 2,
  JP_BASE: { MINI: 10, MINOR: 25, MAJOR: 150, GRAND: 1000 },
  JP_GROW: { MAJOR: 0.01, GRAND: 0.02 },
};
