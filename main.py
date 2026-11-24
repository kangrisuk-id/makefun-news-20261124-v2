#!/usr/bin/env python3
"""
THE WORLD TODAY — Tuesday 24 November 2026 in one image.

Entry for make.fun bounty "news-image-20261124".
A deterministic Pillow program: it typesets a one-page newspaper front page
(masthead, stat strip, three illustrated leads, a markets panel with a real
gold-price line chart, a dot world map, six region panels and an ALSO TODAY
ticker) and writes it to /output/entry.png (or ./entry.png when run locally).

No network, no randomness: two runs write the same bytes.
Every story below was reported on Tuesday 24 November 2026; sources are
listed in NEWS_SOURCES.md.
"""

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 18  # page margin

PAPER = (247, 242, 232)
INK = (23, 23, 20)
RED = (176, 32, 24)
NAVY = (22, 50, 79)
TEAL = (24, 100, 92)
GOLD = (168, 116, 22)
MUTE = (108, 98, 82)
BAND = (237, 229, 207)
HAIR = (196, 186, 160)
WHITE = (255, 255, 255)

FONT_DIRS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
]


def font(name, size):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def serif(size):
    return font("DejaVuSerif-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def sansb(size):
    return font("DejaVuSans-Bold.ttf", size)


def sanso(size):
    return font("DejaVuSans-Oblique.ttf", size)


# ---------------------------------------------------------------- text utils

def tw(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, maxw):
    """Greedy word wrap by pixel width."""
    lines, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, s, f, maxw, lh, fill=INK, max_lines=None, align="left"):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(d, s, f, maxw)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        if align == "center":
            d.text((x + (maxw - tw(d, ln, f)) / 2, y), ln, font=f, fill=fill)
        else:
            d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def kicker(d, x, y, w, text, color):
    d.rectangle([x, y, x + w, y + 19], fill=color)
    d.text((x + 7, y + 3), text, font=sansb(11), fill=WHITE)
    return y + 19


def story(d, x, y, w, lead, text, fsize=10, lh=13):
    """One micro-story: bold lead-in followed by regular text, wrapped."""
    f_b, f_r = sansb(fsize), sans(fsize)
    # build wrapped lines with lead bold on first line(s)
    words = text.split()
    lines, cur, curw = [], [], 0.0
    leadw = tw(d, lead + " ", f_b)
    avail_first = w - leadw
    # simple approach: wrap full text at width w, then overlay lead bold
    full = lead + " " + text
    lines = wrap(d, full, f_r, w)
    yy = y
    # draw lead bold first, then the rest of line 1 after it, then other lines
    d.text((x, yy), lead, font=f_b, fill=INK)
    rest = lines[0][len(lead):].lstrip()
    d.text((x + leadw, yy), rest, font=f_r, fill=INK)
    yy += lh
    for ln in lines[1:]:
        d.text((x, yy), ln, font=f_r, fill=INK)
        yy += lh
    return yy


# ---------------------------------------------------------------- scenes

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(img, box, top, bottom):
    x0, y0, x1, y1 = box
    dd = ImageDraw.Draw(img)
    for i in range(y1 - y0):
        dd.line([x0, y0 + i, x1, y0 + i], fill=lerp(top, bottom, i / max(1, y1 - y0)))


def scene_ship(img, box):
    """Sea drones strike a warship at a Libyan port at dawn."""
    x0, y0, x1, y1 = box
    vgrad(img, box, (24, 38, 66), (214, 116, 62))
    d = ImageDraw.Draw(img)
    w, h = x1 - x0, y1 - y0
    sea_y = y0 + int(h * 0.62)
    # sun
    d.ellipse([x0 + w * 0.70, y0 + h * 0.10, x0 + w * 0.70 + 26, y0 + h * 0.10 + 26],
              fill=(246, 196, 92))
    # port cranes silhouette (left)
    for cx in (0.03, 0.13):
        bx = x0 + w * cx
        d.rectangle([bx, sea_y - h * 0.42, bx + 4, sea_y], fill=(16, 22, 34))
        d.rectangle([bx, sea_y - h * 0.42, bx + w * 0.10, sea_y - h * 0.42 + 4], fill=(16, 22, 34))
        d.line([bx + w * 0.09, sea_y - h * 0.42, bx + w * 0.05, sea_y - h * 0.22], fill=(16, 22, 34), width=2)
    # warship hull + superstructure (centre-right)
    hx0, hx1 = x0 + w * 0.34, x0 + w * 0.94
    hy = sea_y - 4
    d.polygon([(hx0, hy), (hx1, hy), (hx1 - w * 0.05, hy + 10), (hx0 + w * 0.03, hy + 10)],
              fill=(86, 100, 122))
    d.rectangle([hx0 + w * 0.16, hy - 16, hx0 + w * 0.30, hy], fill=(86, 100, 122))
    d.rectangle([hx0 + w * 0.34, hy - 27, hx0 + w * 0.44, hy], fill=(96, 112, 134))
    d.line([hx0 + w * 0.39, hy - 27, hx0 + w * 0.39, hy - 44], fill=(60, 72, 92), width=3)
    d.line([hx0 + w * 0.30, hy - 40, hx0 + w * 0.48, hy - 40], fill=(60, 72, 92), width=2)
    # explosion at the stern, on the deck line, with a glow behind it
    ex, ey = hx0 + w * 0.045, hy - 14
    d.ellipse([ex - 34, ey - 22, ex + 34, ey + 22], fill=(198, 84, 40))
    for r, col in ((26, (240, 120, 40)), (17, (250, 176, 60)), (9, (255, 226, 130))):
        pts = []
        for k in range(12):
            ang = k * math.pi / 6
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((ex + rr * math.cos(ang), ey + rr * math.sin(ang) * 0.8))
        d.polygon(pts, fill=col)
    # smoke above the superstructure
    for i, (sx, sy, sr) in enumerate(((0.62, 0.10, 12), (0.67, 0.04, 16), (0.74, 0.01, 20))):
        d.ellipse([x0 + w * sx, y0 + h * sy, x0 + w * sx + sr * 2, y0 + h * sy + sr * 1.2],
                  fill=(70, 66, 66))
    # sea
    d.rectangle([x0, sea_y, x1, y1], fill=(18, 44, 66))
    rnd = random.Random(7)
    for _ in range(46):
        sx = x0 + rnd.uniform(4, w - 30)
        sy = sea_y + rnd.uniform(3, h * 0.34)
        d.line([sx, sy, sx + rnd.uniform(6, 20), sy], fill=(70, 120, 150), width=1)
    # three sea drones with wakes, heading for the ship
    for fx, fy in ((0.06, 0.74), (0.16, 0.84), (0.26, 0.70)):
        dx, dy = x0 + w * fx, y0 + h * fy
        d.polygon([(dx, dy), (dx + 26, dy + 3), (dx + 20, dy + 8), (dx + 4, dy + 7)], fill=(10, 14, 20))
        d.line([dx - 16, dy + 6, dx + 2, dy + 5], fill=(150, 190, 205), width=1)
        d.line([dx - 10, dy + 9, dx + 4, dy + 8], fill=(110, 150, 175), width=1)
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=INK, width=1)


def scene_chip(img, box):
    """A giant AI chip over a rising market line."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(13, 26, 43))
    rnd = random.Random(11)
    # circuit traces
    for _ in range(26):
        sx = x0 + rnd.uniform(0, w)
        sy = y0 + rnd.uniform(0, h)
        ex = sx + rnd.choice([-1, 1]) * rnd.uniform(14, 52)
        ey = sy + rnd.choice([-1, 1]) * rnd.uniform(10, 30)
        d.line([sx, sy, ex, sy, ex, ey], fill=(38, 84, 110), width=1)
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(64, 140, 160))
    # candlesticks bottom-left
    for i, (o, c) in enumerate(((0.62, 0.55), (0.55, 0.66), (0.66, 0.60), (0.60, 0.78), (0.78, 0.72), (0.72, 0.90))):
        bx = x0 + 14 + i * 20
        top = y0 + h * (1 - max(o, c)) - 8
        bot = y0 + h * (1 - min(o, c)) - 8
        col = (64, 200, 120) if c >= o else (220, 80, 70)
        d.rectangle([bx, top, bx + 11, bot], fill=col)
    # the chip
    cw, chh = int(w * 0.34), int(h * 0.58)
    cx0, cy0 = x0 + int(w * 0.56), y0 + int(h * 0.16)
    for gx in range(cx0 - 12, cx0 + cw + 13, 16):
        d.line([gx, cy0 - 8, gx, cy0], fill=(150, 170, 190), width=3)
        d.line([gx, cy0 + chh, gx, cy0 + chh + 8], fill=(150, 170, 190), width=3)
    for gy in range(cy0 + 4, cy0 + chh - 3, 16):
        d.line([cx0 - 8, gy, cx0, gy], fill=(150, 170, 190), width=3)
        d.line([cx0 + cw, gy, cx0 + cw + 8, gy], fill=(150, 170, 190), width=3)
    d.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + chh], 6, fill=(24, 52, 84), outline=(120, 190, 230), width=2)
    d.rounded_rectangle([cx0 + 12, cy0 + 10, cx0 + cw - 12, cy0 + chh - 10], 4, outline=(90, 160, 200), width=1)
    t = "AI"
    d.text((cx0 + (cw - tw(d, t, serif(26))) / 2, cy0 + chh / 2 - 17), t, font=serif(26), fill=(160, 220, 250))
    # rising arrow line
    pts = [(x0 + w * 0.06, y0 + h * 0.88), (x0 + w * 0.24, y0 + h * 0.74),
           (x0 + w * 0.40, y0 + h * 0.80), (x0 + w * 0.60, y0 + h * 0.52),
           (x0 + w * 0.80, y0 + h * 0.34), (x0 + w * 0.95, y0 + h * 0.16)]
    d.line(pts, fill=(64, 220, 130), width=3)
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 13, ay + 2), (ax - 2, ay + 12)], fill=(64, 220, 130))
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=INK, width=1)


def scene_factory(img, box):
    """A factory ablaze at dusk, rescue lights below."""
    x0, y0, x1, y1 = box
    vgrad(img, box, (30, 30, 52), (120, 62, 54))
    d = ImageDraw.Draw(img)
    w, h = x1 - x0, y1 - y0
    gy = y0 + int(h * 0.86)
    # factory block
    fx0, fx1 = x0 + w * 0.10, x0 + w * 0.88
    fy = y0 + int(h * 0.38)
    d.rectangle([fx0, fy, fx1, gy], fill=(22, 20, 26))
    # chimneys
    for cx in (0.22, 0.34):
        bx = x0 + w * cx
        d.rectangle([bx, fy - h * 0.26, bx + 13, fy], fill=(22, 20, 26))
    # smoke plumes
    for i, (sx, sy, sr) in enumerate(((0.24, 0.06, 15), (0.31, 0.02, 19), (0.37, 0.05, 13))):
        d.ellipse([x0 + w * sx, y0 + h * sy, x0 + w * sx + sr * 2, y0 + h * sy + sr], fill=(52, 48, 50))
    # windows (some lit)
    rnd = random.Random(3)
    for r in range(3):
        for c in range(9):
            wx = fx0 + 12 + c * (w * 0.078)
            wy = fy + 10 + r * 15
            col = (250, 190, 90) if rnd.random() < 0.55 else (52, 54, 66)
            d.rectangle([wx, wy, wx + 12, wy + 8], fill=col)
    # flames on the roof line
    for fx in (0.52, 0.60, 0.68, 0.76, 0.83):
        bx = x0 + w * fx
        fh = h * (0.20 + 0.10 * ((int(fx * 100) % 3) / 2))
        d.polygon([(bx, fy), (bx + 9, fy - fh * 0.55), (bx + 4, fy - fh * 0.30),
                   (bx + 13, fy - fh), (bx + 18, fy)], fill=(238, 110, 30))
        d.polygon([(bx + 4, fy), (bx + 10, fy - fh * 0.5), (bx + 15, fy)], fill=(252, 190, 70))
    # ground + rescue lights
    d.rectangle([x0, gy, x1, y1], fill=(14, 13, 16))
    for i, lx in enumerate((0.14, 0.30, 0.47, 0.63, 0.80)):
        col = (255, 60, 50) if i % 2 == 0 else (90, 160, 255)
        d.ellipse([x0 + w * lx, gy + 5, x0 + w * lx + 7, gy + 12], fill=col)
        d.rectangle([x0 + w * lx + 1, gy + 12, x0 + w * lx + 6, gy + 17], fill=(40, 40, 46))
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=INK, width=1)


# ---------------------------------------------------------------- world map

MAP_ROWS = [
    "     #######                                        ##########    ",
    "   ##########          ##              #######################   ",
    "  ############        ####           #########################   ",
    "   ##########          ##             #####################      ",
    "    ########                          #################  ##      ",
    "     ######                            ###############           ",
    "      ####        #                     #############            ",
    "      ###        ###                     ##########    #         ",
    "       ##         ##        #             ########               ",
    "       ##                            #     ######                ",
    "        #        ##                 ##      ####                 ",
    "                 ##                 ###      ##   #              ",
    "                 ###                ####       ###               ",
    "                  ###               #####       #                ",
    "                  ####               ###                         ",
    "                   ###               ##            #####         ",
    "                   ##                             ########       ",
    "                   ##                              ##  ###       ",
    "                   #                                                    ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
]
MARKERS = {  # (col, row, label) — approximate positions on the dot map
    (35, 10): "Benghazi",
    (36, 5): "Kyiv",
    (52, 14): "Banten",
    (13, 6): "New York",
    (19, 15): "Brasilia",
    (58, 18): "Wellington",
    (30, 6): "Lisbon",
    (34, 8): "Antalya",
    (38, 12): "Khartoum",
    (31, 6): "Geneva",
}


def draw_map(d, x, y, cw, chh):
    cols, rows = 62, 24
    dx, dy = cw / cols, chh / rows
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row[:cols]):
            if ch == "#":
                px, py = x + c * dx, y + r * dy
                d.ellipse([px, py, px + dx * 0.62, py + dy * 0.62], fill=(120, 132, 148))
    for (c, r), _label in MARKERS.items():
        px, py = x + c * dx, y + r * dy
        d.ellipse([px - 3, py - 3, px + 4, py + 4], fill=RED)
        d.ellipse([px - 1, py - 1, px + 2, py + 2], fill=WHITE)


# ---------------------------------------------------------------- markets

GOLD_SERIES = [  # XAU/USD daily closes, 9–24 Nov 2026 (Twelve Data)
    ("9 Nov", 4134.03), ("10 Nov", 4030.42), ("11 Nov", 3987.03),
    ("12 Nov", 3883.66), ("13 Nov", 3875.68), ("14 Nov", 3874.51),
    ("15 Nov", 3880.52), ("16 Nov", 3864.44), ("17 Nov", 3846.80),
    ("18 Nov", 3723.73), ("19 Nov", 3666.87), ("20 Nov", 3520.57),
    ("21 Nov", 3536.20), ("22 Nov", 3532.83), ("23 Nov", 3643.42),
    ("24 Nov", 3638.40),
]


def draw_chart(d, x, y, w, h):
    vals = [v for _, v in GOLD_SERIES]
    lo, hi = 3450, 4200
    px = lambda i: x + 34 + i * (w - 44) / (len(vals) - 1)
    py = lambda v: y + 6 + (hi - v) / (hi - lo) * (h - 22)
    # gridlines + y labels
    for gv in (3500, 3750, 4000):
        gy = py(gv)
        d.line([x + 34, gy, x + w - 8, gy], fill=HAIR, width=1)
        d.text((x + 2, gy - 5), f"{gv:,}", font=sans(8), fill=MUTE)
    pts = [(px(i), py(v)) for i, v in enumerate(vals)]
    d.polygon(pts + [(px(len(vals) - 1), y + h - 12), (px(0), y + h - 12)], fill=(214, 224, 236))
    d.line(pts, fill=NAVY, width=2)
    # min / max / last labels
    imin = min(range(len(vals)), key=lambda i: vals[i])
    d.ellipse([px(imin) - 3, py(vals[imin]) - 3, px(imin) + 3, py(vals[imin]) + 3], fill=RED)
    d.text((px(imin) - 26, py(vals[imin]) + 5), "3,521 low 20 Nov", font=sans(8), fill=RED)
    d.ellipse([px(0) - 3, py(vals[0]) - 3, px(0) + 3, py(vals[0]) + 3], fill=NAVY)
    d.text((px(0) - 4, py(vals[0]) - 13), "4,134 · 9 Nov", font=sans(8), fill=NAVY)
    lx, ly = pts[-1]
    d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=RED)
    d.text((lx - 62, ly - 14), "3,638 · 24 Nov", font=sansb(8), fill=RED)


# ---------------------------------------------------------------- page

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((M, 8), "TUESDAY · 24 NOVEMBER 2026", font=sansb(13), fill=RED)
    r = "ONE PAGE · THE WHOLE DAY"
    d.text((W - M - tw(d, r, sansb(11)), 10), r, font=sansb(11), fill=MUTE)
    t = "THE WORLD TODAY"
    d.text(((W - tw(d, t, serif(57))) / 2, 24), t, font=serif(57), fill=INK)
    sub = "31 stories · 7 regions · every item reported on Tuesday 24 November 2026"
    d.text(((W - tw(d, sub, sans(12))) / 2, 92), sub, font=sans(12), fill=MUTE)
    d.rectangle([M, 114, W - M, 117], fill=RED)
    d.line([M, 121, W - M, 121], fill=INK, width=1)

    # ---- stat strip
    y = 128
    d.rectangle([M, y, W - M, y + 46], fill=BAND)
    stats = [
        ("7", "sea drones sank\nthe Merkury"),
        ("24", "dead in the Java\nfactory fire"),
        ("34", "workers still\nmissing in Banten"),
        ("$450M", "Skubal's record\nMets contract"),
        ("12,000", "fans evacuated in\nManchester"),
        ("-1,484", "Sensex points lost\n(-1.77%) on the day"),
    ]
    cw = (W - 2 * M) / 6
    for i, (num, lab) in enumerate(stats):
        cx = M + i * cw
        if i:
            d.line([cx, y + 6, cx, y + 40], fill=HAIR, width=1)
        d.text((cx + (cw - tw(d, num, serif(23))) / 2, y + 2), num, font=serif(23), fill=NAVY)
        for j, ln in enumerate(lab.split("\n")):
            d.text((cx + (cw - tw(d, ln, sans(8))) / 2, y + 29 + j * 9), ln, font=sans(8), fill=MUTE)

    # ---- lead 1 (left, wide)
    y = 186
    lx, lw = M, 596
    kicker(d, lx, y, lw, "WAR AT SEA — BENGHAZI, LIBYA", RED)
    yy = block(d, lx, y + 25,
               "Ukraine's Sea Drones Sink a Russian Corvette in a Libyan Port",
               serif(27), lw, 33)
    scene_ship(img, (lx, yy + 4, lx + lw, yy + 122))
    yy += 130
    yy = block(d, lx, yy,
               "Seven Ukrainian maritime drones sank the Russian corvette Merkury at its "
               "berth in Benghazi, destroying a combat helicopter aboard; a second strike "
               "disabled the cargo ship Angara, used to move Russian weapons. President "
               "Zelensky confirmed the attack on Monday — Kyiv's war with Moscow spills "
               "onto North Africa's shore. Libya's eastern army says the port is secure "
               "again; the UN mission in Libya condemned the strikes.",
               sans(11), lw, 14.5)
    d.text((lx, yy + 1), "CNN · Le Monde · AP", font=sanso(9), fill=MUTE)

    # ---- lead 2 (right)
    lx2, lw2 = 626, W - M - 626
    kicker(d, lx2, y, lw2, "TECH — WALL STREET", NAVY)
    yy = block(d, lx2, y + 25,
               "Nvidia Board Brings Back Huang — and Stocks Surge",
               serif(23), lw2, 29)
    scene_chip(img, (lx2, yy + 4, lx2 + lw2, yy + 104))
    yy += 112
    yy = block(d, lx2, yy,
               "Nvidia's board unanimously reinstated Jensen Huang as chief executive "
               "and chairman, days after rejecting his offer to return. President Trump "
               "says he persuaded the board and vouched for Huang on security concerns; "
               "a leading Democrat vows a probe. Wall Street soared, clawing back more "
               "than half of last week's plunge.",
               sans(11), lw2, 14.5)
    d.text((lx2, yy + 1), "Associated Press", font=sanso(9), fill=MUTE)

    # ---- row 2: lead 3 | map | markets
    y = 492
    lx, lw = M, 386
    kicker(d, lx, y, lw, "DISASTER — BANTEN, INDONESIA", TEAL)
    yy = block(d, lx, y + 25,
               "Candy Factory Fire Kills 24; 34 Still Missing",
               serif(21), lw, 26)
    scene_factory(img, (lx, yy + 4, lx + lw, yy + 78))
    yy += 86
    yy = block(d, lx, yy,
               "A blaze tore through a candy factory in Banten province, killing at "
               "least 24 workers. Rescue teams picked through the wreckage on Tuesday "
               "for 34 colleagues still unaccounted for.",
               sans(11), lw, 14.5)
    d.text((lx, yy + 1), "AP · Times of India", font=sanso(9), fill=MUTE)

    # map
    mx, mw = 416, 248
    d.text((mx, y + 2), "WHERE IT HAPPENED", font=sansb(11), fill=NAVY)
    d.line([mx, y + 18, mx + mw, y + 18], fill=NAVY, width=1)
    draw_map(d, mx, y + 24, mw, 118)
    d.text((mx, y + 148),
           "Benghazi · Kyiv · Banten · New York · Brasilia · Wellington",
           font=sans(8), fill=MUTE)

    # markets
    kx, kw = 676, W - M - 676
    d.text((kx, y + 2), "MARKETS", font=sansb(11), fill=NAVY)
    d.text((kx, y + 17), "GOLD, $ PER OUNCE — DAILY CLOSE", font=sansb(9), fill=MUTE)
    draw_chart(d, kx, y + 32, kw, 104)
    yy = y + 142
    for line in (
        "SENSEX 82,435  -1,484 (-1.77%) · NIFTY 25,350  -451",
        "WALL ST surges as Nvidia leads the rally (AP)",
        "ASX 200 futures -0.6% · NZX 50 -1% in early trade",
    ):
        d.text((kx, yy), line, font=sans(9), fill=INK)
        yy += 12.5

    # ---- region panels, 3 x 2
    panels = [
        ("EUROPE", NAVY, [
            ("FINLAND —", "Russian cargo ship Sparta II burns in the Gulf of Finland after a drone strike."),
            ("LISBON —", "Thousands march through the capital in protest at the rising cost of living."),
            ("ARMENIA —", "Yerevan proposes a new constitution to advance peace talks with Azerbaijan."),
        ]),
        ("ASIA-PACIFIC", TEAL, [
            ("INDIA–NEPAL —", "Modi and PM Shah flag off the Ayodhya–Janakpur express; energy and trade deals follow."),
            ("CHINA —", "Beijing sets 2030 targets to expand elderly care and childcare across the country."),
            ("SEOUL —", "The president nominates a new foreign minister and a new intelligence chief."),
        ]),
        ("AMERICAS", GOLD, [
            ("WASHINGTON —", "An appeals court hands Trump a path to erase his hush-money conviction."),
            ("CONGRESS —", "Rep. Jimmy Gomez resigns after an ethics report finds evidence of misconduct."),
            ("BRASILIA —", "Bolsonaro is rushed to intensive care with an acute bowel obstruction."),
        ]),
        ("AFRICA", RED, [
            ("KHARTOUM —", "RSF drones kill four, damage a UN building and target the airport; the UAE condemns."),
            ("NIGERIA —", "A boat carrying mourners capsizes: 29 bodies recovered, 50 people pulled out alive."),
            ("DR CONGO —", "Fighting in Ituri traps Ebola response teams, the WHO warns."),
        ]),
        ("MIDDLE EAST & CLIMATE", NAVY, [
            ("HORMUZ —", "Iran says it brought down a US drone near the strait, state media report."),
            ("GAZA —", "An Oxfam study finds toxic contamination across almost all of the Strip's air, soil and water."),
            ("ANTALYA —", "COP31 ends without a fossil-fuel pact; the UN chief: 'no ambiguity in the science'."),
        ]),
        ("SPORT", TEAL, [
            ("GENEVA —", "The World Chess Championship opens: Gukesh defends his title against Sindarov."),
            ("FOOTBALL —", "FIFA names a US-led bid for the 2031 Women's World Cup and a UK-led bid for 2035."),
            ("BASEBALL —", "Pitcher Tarik Skubal agrees a record $450M, nine-year deal with the New York Mets."),
        ]),
    ]
    py = 706
    pw = (W - 2 * M - 20) / 3
    ph = 100
    for i, (name, color, items) in enumerate(panels):
        cx = M + (i % 3) * (pw + 10)
        cy = py + (i // 3) * (ph + 8)
        d.rectangle([cx, cy, cx + pw, cy + 16], fill=color)
        d.text((cx + 6, cy + 3), name, font=sansb(10), fill=WHITE)
        yy = cy + 21
        for lead, text in items:
            yy = story(d, cx + 2, yy, pw - 4, lead, text, fsize=9.5, lh=12.5) + 2.5

    # ---- also today ticker
    y = 928
    d.line([M, y, W - M, y], fill=INK, width=1)
    d.text((M, y + 5), "ALSO TODAY", font=sansb(10), fill=RED)
    also = ("KABUL — Taliban order women's names off Balkh documents, replaced by 'Bibi'  ·  "
            "DHAKA — Bangladesh vows to arrest Hasina if she returns  ·  "
            "YANGON — Junta calls ASEAN's decision 'unfair and unbalanced'  ·  "
            "PATNA — Modi opens an AI centre at IIT Patna  ·  "
            "PRINCETON — Chinese neuroscientist held by ICE after airport detention  ·  "
            "MANCHESTER — 12,000 fans evacuated from a Don Toliver concert  ·  "
            "ROME — Jeweller Paolo Bulgari dies at 89  ·  "
            "PALM SPRINGS — Miley Cyrus weds drummer Maxx Morando  ·  "
            "HARARE — Preacher Uebert Angel arrested during a service  ·  "
            "WELLINGTON — NZ hold India (9-720 dec) to a draw; Australia rise to 2nd in the Test standings")
    block(d, M + 86, y + 5, also, sans(9), W - 2 * M - 86, 12, fill=INK)

    # ---- footer
    y = 984
    d.line([M, y, W - M, y], fill=INK, width=1)
    block(d, M, y + 6,
          "DATE CHECK — every story above happened, or was first reported, on Tuesday 24 November 2026. "
          "Sources: AP, CNN, Le Monde, Reuters, NDTV, Times of India, PanaPress; gold: Twelve Data. "
          "Drawn by a program (main.py) — no photographs.",
          sans(8.5), W - 2 * M - 130, 11, fill=MUTE)
    r = "24.11.2026"
    d.text((W - M - tw(d, r, sansb(10)), y + 8), r, font=sansb(10), fill=RED)

    return img


def main():
    img = build()
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out is None:
        out = "/output/entry.png" if os.path.isdir("/output") else os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "entry.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    img.save(out, format="PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
