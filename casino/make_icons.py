"""Draw the app icons (a black and gold casino chip on black) into casino/icons/."""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FELT, FELT_HI, RAIL, BRASS = (12, 12, 13), (44, 42, 38), (11, 11, 12), (212, 175, 55)
RED, IVORY, INK = (22, 22, 24), (212, 175, 55), (18, 18, 18)

def font(size):
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def icon(size, chip_r=0.36, rounded=False):
    S = size * 4  # supersample
    im = Image.new("RGB", (S, S), FELT)
    d = ImageDraw.Draw(im)
    # soft radial light on the felt
    for i in range(60, 0, -1):
        t = i / 60
        c = tuple(int(FELT[k] + (FELT_HI[k] - FELT[k]) * (1 - t)) for k in range(3))
        r = S * 0.75 * t
        d.ellipse([S / 2 - r, S * 0.42 - r, S / 2 + r, S * 0.42 + r], fill=c)
    cx = cy = S / 2
    R = S * chip_r
    # shadow
    sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh).ellipse([cx - R, cy - R + S * 0.02, cx + R, cy + R + S * 0.02], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(S * 0.02))
    im.paste((0, 0, 0), (0, 0), sh)
    d = ImageDraw.Draw(im)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=RED)
    # edge stripes
    for k in range(8):
        a0 = k * 45 - 9
        d.pieslice([cx - R, cy - R, cx + R, cy + R], a0, a0 + 18, fill=IVORY)
    ri = R * 0.78
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=RED)
    rd = R * 0.70
    d.ellipse([cx - rd, cy - rd, cx + rd, cy + rd], outline=BRASS, width=int(S * 0.012))
    rc = R * 0.56
    d.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=(244, 236, 214))
    f = font(int(R * 0.9))
    d.text((cx, cy + R * 0.02), "♠", font=f, fill=INK, anchor="mm")
    im = im.resize((size, size), Image.LANCZOS)
    if rounded:
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=size * 0.2, fill=255)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0)); out.paste(im, (0, 0), m); return out
    return im

out = os.path.join(HERE, "icons")
os.makedirs(out, exist_ok=True)
icon(192).save(os.path.join(out, "icon-192.png"))
icon(512).save(os.path.join(out, "icon-512.png"))
icon(512, chip_r=0.30).save(os.path.join(out, "icon-maskable-512.png"))
icon(180).save(os.path.join(out, "apple-touch-icon.png"))
icon(32, chip_r=0.44).save(os.path.join(out, "favicon-32.png"))
print("ok")
