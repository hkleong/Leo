# 龙腾财宝 RTP simulation

`cfg.js` holds the same reels, pays, coin values and jackpot settings as the 龙腾财宝 game in `casino/index.html` (`MGC`).

    node final.js 6000000

Current settings (6 wilds on reels 2–4, 10 coins per reel, 5% coin chance per open cell on each respin, coins 0.25–2.5× the stake), two runs of 6,000,000 spins:
RTP 97.5% / 96.6%; a win every 2.63 spins, hold & spin every ~31 spins (8.4 coins locked on average), GRAND about 1 in 18,000 spins.
