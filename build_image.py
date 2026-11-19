#!/usr/bin/env python3
"""Render entry.png: 'The World in a Day' - the world news of Thursday
19 November 2026 in one 1024x1024 infographic poster.

Everything is drawn in code with PIL (no external images), so the picture
is fully our own work. Stories chosen from the day's reporting across
Reuters/AP/AFP and major front pages:

  TOP   Trump, Xi and Putin hold a first-ever trilateral summit in
        Shenzhen, with the Ukraine war and nuclear arms on the table.
  LAW   The ICJ at The Hague rules on the Rohingya genocide case
        (The Gambia v. Myanmar).
  SEA   Three oil tankers catch fire after striking mines east of the
        Strait of Hormuz; the IEA calls the Middle East crisis the
        gravest threat energy security has ever faced.
  AIR   COP31 in Antalya: ministers try to unblock the climate talks.
  LAND  Bangladesh: unrest in 28 districts, ex-leader Yunus's family
        home set on fire, troops deployed.
  PLUS  GTA VI launches after a 13-year wait; a Van Gogh sells for
        $190.4M, an artist record; Ukraine strikes the Crimea Bridge.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# palette - broadsheet cream, ink black, wire-service red
CREAM = (248, 244, 234)
INK = (20, 24, 29)
RED = (179, 32, 44)
WHITE = (255, 255, 255)

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)


def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, text, fnt, fill, max_w, leading=1.18):
    for line in wrap(text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * leading)
    return y


# ---------------------------------------------------------------- icons
def icon_scales(cx, cy, s, col):
    """Scales of justice centred at (cx, cy), s = half-width."""
    d.line([cx, cy - s, cx, cy + s], fill=col, width=7)
    d.line([cx - s, cy - int(s * 0.72), cx + s, cy - int(s * 0.72)], fill=col, width=7)
    d.ellipse([cx - 9, cy - s - 9, cx + 9, cy - s + 9], fill=col)
    for sx in (-1, 1):
        px = cx + sx * s
        py = cy - int(s * 0.72)
        d.line([px, py, px - int(s * 0.42), cy + int(s * 0.45)], fill=col, width=5)
        d.line([px, py, px + int(s * 0.42), cy + int(s * 0.45)], fill=col, width=5)
        d.arc([px - int(s * 0.42), cy + int(s * 0.18), px + int(s * 0.42),
               cy + int(s * 0.72)], start=0, end=180, fill=col, width=6)
    d.line([cx - int(s * 0.55), cy + s, cx + int(s * 0.55), cy + s], fill=col, width=8)


def icon_tanker(cx, cy, s, col, flame):
    """Oil tanker side view with a flame above the deck."""
    hull_y = cy + int(s * 0.28)
    d.polygon([(cx - s, hull_y - int(s * 0.18)), (cx + s, hull_y - int(s * 0.18)),
               (cx + int(s * 0.78), hull_y + int(s * 0.34)),
               (cx - int(s * 0.78), hull_y + int(s * 0.34))], fill=col)
    d.rectangle([cx - int(s * 0.88), hull_y - int(s * 0.34),
                 cx + int(s * 0.30), hull_y - int(s * 0.18)], fill=col)
    d.rectangle([cx + int(s * 0.52), hull_y - int(s * 0.52),
                 cx + int(s * 0.80), hull_y - int(s * 0.18)], fill=col)
    for i in range(3):
        d.line([cx - s, cy + int(s * 0.62) + i * 9, cx + s,
                cy + int(s * 0.62) + i * 9], fill=col, width=3)
    icon_flame(cx - int(s * 0.28), hull_y - int(s * 0.58), int(s * 0.40), flame)


def _bezier(p0, p1, p2, p3, n=14):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def _flame_pts(cx, cy, s):
    """Classic flame outline around centre (cx, cy), height ~2s."""
    tip = (cx + s * 0.18, cy - s)
    pts = []
    pts += _bezier(tip, (cx - s * 0.62, cy - s * 0.42),
                   (cx - s * 0.58, cy + s * 0.28), (cx - s * 0.34, cy + s * 0.72))
    pts += _bezier((cx - s * 0.34, cy + s * 0.72), (cx - s * 0.12, cy + s * 1.0),
                   (cx + s * 0.30, cy + s * 1.0), (cx + s * 0.46, cy + s * 0.66))
    pts += _bezier((cx + s * 0.46, cy + s * 0.66), (cx + s * 0.66, cy + s * 0.30),
                   (cx + s * 0.34, cy - s * 0.02), (cx + s * 0.16, cy + s * 0.30))
    pts += _bezier((cx + s * 0.16, cy + s * 0.30), (cx + s * 0.05, cy - s * 0.10),
                   (cx + s * 0.30, cy - s * 0.55), tip)
    return pts


def icon_flame(cx, cy, s, col):
    """A bold flame: outer teardrop in col, amber core."""
    d.polygon(_flame_pts(cx, cy, s), fill=col)
    core = _flame_pts(cx, cy + s * 0.34, s * 0.52)
    d.polygon(core, fill=(255, 176, 66))


def icon_thermo(cx, cy, s, col):
    """Thermometer: tube, bulb and mercury."""
    d.rounded_rectangle([cx - int(s * 0.20), cy - s, cx + int(s * 0.20),
                         cy + int(s * 0.42)], radius=int(s * 0.20), outline=col, width=8)
    d.ellipse([cx - int(s * 0.42), cy + int(s * 0.28), cx + int(s * 0.42),
               cy + int(s * 1.10)], outline=col, width=8)
    d.rectangle([cx - int(s * 0.09), cy - int(s * 0.30), cx + int(s * 0.09),
                 cy + int(s * 0.55)], fill=RED)
    d.ellipse([cx - int(s * 0.24), cy + int(s * 0.46), cx + int(s * 0.24),
               cy + int(s * 0.94)], fill=RED)
    for i in range(3):
        yy = cy - int(s * 0.72) + i * int(s * 0.34)
        d.line([cx + int(s * 0.20), yy, cx + int(s * 0.48), yy], fill=col, width=6)


def icon_flags(x, y, w):
    """Three stylised flags stacked: US, China, Russia (each w x 34)."""
    fh, gap = 34, 9
    # US: red/white stripes + navy canton
    for i in range(6):
        d.rectangle([x, y + i * fh // 6, x + w, y + (i + 1) * fh // 6],
                    fill=(178, 34, 52) if i % 2 == 0 else (245, 245, 245))
    d.rectangle([x, y, x + w * 0.42, y + fh // 2], fill=(60, 59, 110))
    d.rectangle([x, y, x + w, y + fh], outline=INK, width=3)
    # China: red field, one gold star
    y2 = y + fh + gap
    d.rectangle([x, y2, x + w, y2 + fh], fill=(222, 41, 16))
    cx, cy, r = x + 22, y2 + fh // 2, 10
    star = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        star.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(star, fill=(255, 222, 0))
    d.rectangle([x, y2, x + w, y2 + fh], outline=INK, width=3)
    # Russia: white / blue / red
    y3 = y2 + fh + gap
    d.rectangle([x, y3, x + w, y3 + fh // 3], fill=(245, 245, 245))
    d.rectangle([x, y3 + fh // 3, x + w, y3 + 2 * fh // 3], fill=(0, 57, 166))
    d.rectangle([x, y3 + 2 * fh // 3, x + w, y3 + fh], fill=(213, 43, 30))
    d.rectangle([x, y3, x + w, y3 + fh], outline=INK, width=3)


# ---------------------------------------------------------------- masthead
MX = 36  # page margin
d.line([MX, 30, W - MX, 30], fill=INK, width=3)
f_title = font(SERIF_B, 64)
t = "THE WORLD IN A DAY"
d.text(((W - d.textlength(t, font=f_title)) / 2, 40), t, font=f_title, fill=INK)
d.line([MX, 122, W - MX, 122], fill=INK, width=3)

# date bar - the day, unmissable
d.rectangle([MX, 134, W - MX, 192], fill=INK)
f_date = font(SANS_B, 37)
t = "THURSDAY · 19 NOVEMBER 2026"
d.text(((W - d.textlength(t, font=f_date)) / 2, 145), t, font=f_date, fill=CREAM)

# ---------------------------------------------------------------- hero
HY, HH = 208, 238
d.rectangle([MX, HY, W - MX, HY + HH], fill=(233, 238, 247))
d.rectangle([MX, HY, MX + 10, HY + HH], fill=(27, 58, 120))
hx = MX + 34
f_kick = font(SANS_B, 23)
d.text((hx, HY + 18), "TOP STORY · SHENZHEN, CHINA", font=f_kick, fill=RED)
f_hero = font(SERIF_B, 49)
d.text((hx, HY + 52), "Trump, Xi & Putin Hold", font=f_hero, fill=INK)
d.text((hx, HY + 108), "First Trilateral Summit", font=f_hero, fill=INK)
f_sub = font(SANS, 24)
text_block(hx, HY + 172,
           "An unprecedented three-power meeting — the war in Ukraine "
           "and nuclear arms top the agenda.",
           f_sub, (52, 58, 66), 640)
icon_flags(W - MX - 158, HY + 56, 136)

# ---------------------------------------------------------------- panels
panels = [
    ("THE HAGUE · WORLD COURT", (43, 58, 143), (233, 235, 247),
     "ICJ Rules on Rohingya Genocide Case",
     "UN top court delivers judgment in The Gambia v. Myanmar.",
     icon_scales),
    ("STRAIT OF HORMUZ · ENERGY", (194, 81, 10), (251, 238, 226),
     "Three Tankers Ablaze After Striking Mines",
     "IEA: the gravest threat energy security has ever faced.",
     icon_tanker),
    ("ANTALYA · COP31 CLIMATE SUMMIT", (14, 122, 95), (226, 242, 236),
     "Climate Talks Go Down to the Wire",
     "Ministers scramble to rescue a final deal.",
     icon_thermo),
    ("BANGLADESH · UNREST", (163, 22, 33), (249, 232, 234),
     "Unrest Sweeps 28 Districts",
     "Ex-leader Yunus's family home set ablaze; troops deploy.",
     icon_flame),
]

PW = (W - 2 * MX - 16) // 2
PH = 216
rows_y = [458, 690]
f_pk = font(SANS_B, 20)
f_ph = font(SERIF_B, 30)
f_ps = font(SANS, 20)

for i, (kick, accent, tint, head, sub, icon) in enumerate(panels):
    px = MX + (i % 2) * (PW + 16)
    py = rows_y[i // 2]
    d.rectangle([px, py, px + PW, py + PH], fill=tint)
    d.rectangle([px, py, px + PW, py + 7], fill=accent)
    tx = px + 22
    d.text((tx, py + 18), kick, font=f_pk, fill=accent)
    yy = text_block(tx, py + 48, head, f_ph, INK, PW - 142, leading=1.12)
    text_block(tx, yy + 4, sub, f_ps, (52, 58, 66), PW - 142, leading=1.15)
    icx, icy = px + PW - 62, py + PH // 2 + 8
    if icon is icon_tanker:
        icon(icx, icy, 46, accent, RED)
    elif icon is icon_flame:
        icon(icx, icy - 16, 42, accent)
    elif icon is icon_thermo:
        icon(icx, icy - 14, 40, accent)
    else:
        icon(icx, icy, 39, accent)

# ---------------------------------------------------------------- ticker
TY = 922
d.rectangle([MX, TY, W - MX, 1002], fill=INK)
f_tk = font(SANS_B, 20)
d.text((MX + 20, TY + 9), "ALSO TODAY", font=f_tk, fill=(255, 176, 66))
text_block(MX + 20, TY + 36,
           "GTA VI launches after a 13-year wait · Van Gogh sells for "
           "$190.4M, an artist record · Ukraine strikes the Crimea Bridge again",
           font(SANS, 20), CREAM, W - 2 * MX - 40, leading=1.15)

img.save(OUT, optimize=True)
print(OUT, os.path.getsize(OUT), "bytes")
