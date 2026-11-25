const reel = (w, s, c) => Object.assign(w ? { W: w } : {}, { D: 2, F: 3, H: 4, L: 4, A: 5, K: 5, Q: 6, J: 6, T: 6, S: s, C: c });
module.exports = {
  COUNTS: [reel(0, 1, 8), reel(2, 2, 8), reel(2, 2, 8), reel(2, 2, 8), reel(0, 1, 8)],
  PAY: { D: [2.5, 8, 25], F: [1.5, 5, 15], H: [1.2, 4, 12], L: [1, 2.5, 10], A: [0.5, 1.2, 5], K: [0.5, 1.2, 5], Q: [0.25, 0.75, 4], J: [0.25, 0.75, 4], T: [0.25, 0.75, 4] },
  COIN: [{ x: 1, w: 30 }, { x: 2, w: 25 }, { x: 3, w: 15 }, { x: 5, w: 10 }, { x: 8, w: 6 }, { x: 10, w: 4 }, { jp: "MINI", w: 3 }, { jp: "MINOR", w: 1.5 }, { jp: "MAJOR", w: 0.5 }],
  P_COIN: 0.03,
  FS: { 3: 8, 4: 12, 5: 20 },
  FS_MULT: 2,
  JP_BASE: { MINI: 10, MINOR: 25, MAJOR: 150, GRAND: 1000 },
  JP_GROW: { MAJOR: 0.01, GRAND: 0.02 },   // per spin, in multiples of the bet
};
