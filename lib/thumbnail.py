#!/usr/bin/env python3
"""videopress thumbnail — generate a high-CTR thumbnail.

Usage: python3 thumbnail.py "2-4 WORDS" [--bg image.jpg] [--out thumbnail.png]
       [--sub "smaller line"]

Rules (see docs/THUMBNAIL-GUIDE.md):
- 2-4 words max, bold, readable at 120px wide
- High contrast: white/yellow text, black stroke, dark scrim
- Face/emotion close-up background beats text-only
- Never more than one text block + optional sub-line
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

args = sys.argv[1:]
TEXT = args[0]
OUT = "thumbnail.png"
BG = None
SUB = None
i = 1
while i < len(args):
    if args[i] == "--bg" and i + 1 < len(args):
        BG = args[i + 1]; i += 2
    elif args[i] == "--out" and i + 1 < len(args):
        OUT = args[i + 1]; i += 2
    elif args[i] == "--sub" and i + 1 < len(args):
        SUB = args[i + 1]; i += 2
    else:
        i += 1

W, H = 1280, 720
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if BG and os.path.exists(BG):
    im = Image.open(BG).convert("RGB")
    # cover-crop to 16:9
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)))
    x = (im.width - W) // 2; y = (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
else:
    # fallback: dark gradient
    im = Image.new("RGB", (W, H), (18, 18, 24))
    im = im.filter(ImageFilter.GaussianBlur(8))

d = ImageDraw.Draw(im, "RGBA")
# dark scrim behind text for contrast
d.rectangle([0, H // 4, W, H * 3 // 4 + 40], fill=(0, 0, 0, 110))

def fit_font(text, max_w, start=170):
    size = start
    while size > 48:
        f = ImageFont.truetype(FONT, size)
        bb = d.textbbox((0, 0), text, font=f, stroke_width=max(3, size // 12))
        if bb[2] - bb[0] <= max_w:
            return f
        size -= 10
    return ImageFont.truetype(FONT, 48)

f = fit_font(TEXT, W - 160)
bb = d.textbbox((0, 0), TEXT, font=f, stroke_width=6)
tw, th = bb[2] - bb[0], bb[3] - bb[1]
x, y = (W - tw) // 2, (H - th) // 2 - (30 if SUB else 0)
# hard shadow + yellow-white text
d.text((x + 7, y + 7), TEXT, font=f, fill=(0, 0, 0, 255))
d.text((x, y), TEXT, font=f, fill=(255, 210, 40, 255),
       stroke_width=6, stroke_fill=(0, 0, 0, 255))

if SUB:
    fs = ImageFont.truetype(FONT, 54)
    bb2 = d.textbbox((0, 0), SUB, font=fs, stroke_width=3)
    sx = (W - (bb2[2] - bb2[0])) // 2
    d.text((sx + 3, y + th + 33), SUB, font=fs, fill=(0, 0, 0, 230))
    d.text((sx, y + th + 30), SUB, font=fs, fill=(255, 255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0, 255))

# small-size legibility check: downscale and warn
small = im.resize((120, 68))
im.save(OUT)
print(f"wrote {OUT} — check it at 120px wide before shipping")
