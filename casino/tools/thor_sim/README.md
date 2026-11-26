# 雷神之锤 simulator

6×5 pay anywhere with tumbles. 雷球 (M) carry ×2–×500; when a winning tumble sequence ends, the 雷球 on screen add up
and multiply its win. 4+ 雷电盾徽 (S) pay 3/5/100× and give 15 free spins (own reels with more 雷球) where every winning
spin adds its 雷球 to a running total multiplier; 3+ 盾徽 in free spins give +5. Buy = 88× stake; ante = 1.25× stake with
1.24× the 盾徽 weight (no buy).

    node thorsim.js 3000000 base     # ~96%, free spins ~1 in 370
    node thorsim.js 3000000 ante     # ~95%, free spins ~1 in 175
    node thorsim.js 150000 buy       # ~96%, average ~84.5× stake

`thorcfg.js` must match `THC` in `casino/index.html`.
