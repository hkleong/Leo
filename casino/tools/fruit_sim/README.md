# 水果转轮 simulator

5×3, 20 fixed lines. 百搭 (W) on reels 2–4 expands to the whole reel and holds while the other reels
respin; each new 百搭 gives another respin. Three 转轮 (X) on reels 1, 3, 5 spin the prize wheel (× bet).

    node fruitsim.js 5000000

`fruitcfg.js` must match `FRC` in `casino/index.html`. Current numbers: RTP about 96.4%,
a win every 2.7 spins, a 百搭 respin every 5.4 spins, the wheel every ~480 spins.
