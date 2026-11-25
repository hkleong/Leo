# 宝石瀑布 RTP simulation

`gemcfg.js` holds the same symbol weights, pays, multiplier ladder and free-spin settings as the 宝石瀑布 game in `casino/index.html` (`GMC`).

    node gemsim.js 3000000 ./gemcfg.js 11

Two runs of 3,000,000 spins: RTP 96.1% / 96.4%; a win every 3.33 spins, free spins every ~175 spins, 20x+ wins every ~125 spins.
