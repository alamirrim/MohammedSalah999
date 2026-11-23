#!/usr/bin/env python3
"""Generate channel profile picture (800x800) and banner (2560x1440, safe-area aware).

  python branding/make_branding.py "Midnight Twist"
"""
import colorsys
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = str(ROOT / "assets" / "fonts" / "Inter-Black.otf")
BG = (8, 8, 14)
YELLOW = (255, 242, 0)


def neon(hue):
    r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1)
    return int(r * 255), int(g * 255), int(b * 255)


def glow(img, radius):
    return Image.blend(img, img.filter(ImageFilter.GaussianBlur(radius)), 0.45)


def avatar(name, out):
    S = 800
    im = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(im)
    pad = 70
    d.ellipse([pad, pad, S - pad, S - pad], outline=neon(0.78), width=22)
    for i, (x, y, r) in enumerate([(300, 520, 70), (500, 470, 95), (390, 330, 55)]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=neon(0.12 + i * 0.3), outline="white", width=6)
    im = glow(im, 14)
    d = ImageDraw.Draw(im)
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    f = ImageFont.truetype(FONT, 300)
    d.text((S / 2, S / 2), initials, font=f, fill="white", anchor="mm", stroke_width=14, stroke_fill="black")
    im.save(out)


def banner(name, tagline, out):
    W, H = 2560, 1440
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # decorative balls + trails across the full width (only the centre is guaranteed visible)
    import random
    rnd = random.Random(7)
    for i in range(26):
        x, y = rnd.randint(0, W), rnd.randint(300, H - 300)
        if 650 < x < 1910 and 520 < y < 920:
            continue
        r = rnd.randint(20, 70)
        col = neon(rnd.random())
        for k in range(8):
            rr = r * (0.6 + k * 0.05)
            xx = x - k * 22
            d.ellipse([xx - rr, y - rr, xx + rr, y + rr], fill=tuple(int(c * (0.25 + k * 0.09)) for c in col))
        d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline="white", width=4)
    im = glow(im, 18)
    d = ImageDraw.Draw(im)
    # safe area for all devices: 1546x423 centred
    f1 = ImageFont.truetype(FONT, 170)
    f2 = ImageFont.truetype(FONT, 60)
    d.text((W / 2, H / 2 - 50), name.upper(), font=f1, fill="white", anchor="mm",
           stroke_width=10, stroke_fill="black")
    d.text((W / 2, H / 2 + 100), tagline, font=f2, fill=YELLOW, anchor="mm",
           stroke_width=6, stroke_fill="black")
    im.save(out)


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Midnight Twist"
    tagline = sys.argv[2] if len(sys.argv) > 2 else "A NEW STORY WITH A TWIST, EVERY DAY"
    avatar(name, ROOT / "branding" / "profile_picture.png")
    banner(name, tagline, ROOT / "branding" / "banner.png")
    print("wrote branding/profile_picture.png and branding/banner.png")
