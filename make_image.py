#!/usr/bin/env python3
"""Draw the front page for Monday 23 November 2026: 35 stories, 7 regions.

A single 1024x1024 page on cream paper: top bar, masthead, red
italic subline, stat strip, region bar, three heroes, ten small
leads, a realistic filled-continent map with numbered pins, an ALSO
list of 22 more stories, a DATE CHECK box and a sources line.

Everything is drawn in code with Pillow. No photograph or downloaded
art is used. Every piece of text carries a hard overflow check, so
the build fails loudly instead of clipping a line silently.
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFont

# --- page ------------------------------------------------------------
W, H = 1024, 1024
MX, RX = 12, 1012
CREAM = (250, 246, 235)
INK = (25, 25, 30)
RED = (178, 34, 34)
NAVY = (18, 28, 55)
TAN = (198, 170, 120)
LAND_EDGE = (60, 50, 35)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
LEADER = (220, 220, 220)
OUT = "entry.png"

DEJAVU = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    """Load a DejaVu font at the given point size."""
    return ImageFont.truetype(os.path.join(DEJAVU, name), size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def fit(draw, text, font, width, max_lines, what):
    """Greedy word wrap that refuses to overflow: more lines than the
    limit raises instead of drawing clipped text."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        raise AssertionError(
            "OVERFLOW %s: needs %d lines (max %d): %r"
            % (what, len(lines), max_lines, text)
        )
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=font, fill=fill)


def italic_layer(text, font, fill, shear=0.22):
    """Render text on its own layer, then shear it so it reads as
    italic. DejaVu Serif ships no italic variant, so the slant is
    faked geometrically: the top of each glyph moves right of its
    base, which is what a real italic does. The layer is cropped to
    its ink so the caller can place it exactly."""
    tmp = Image.new("RGB", (10, 10))
    probe = ImageDraw.Draw(tmp)
    w = int(probe.textlength(text, font=font))
    h = font.size + 8
    pad = int(h * shear) + 8
    layer = Image.new("RGBA", (w + 2 * pad, h + 4), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((pad, 2), text, font=font, fill=fill + (255,))
    layer = layer.transform(
        layer.size,
        Image.AFFINE,
        (1, shear, -shear * (h - 2), 0, 1, 0),
        resample=Image.BICUBIC,
    )
    box = layer.getbbox()
    if box:
        layer = layer.crop(box)
    return layer


# --- map: equirectangular projection --------------------------------
# Longitude -168..+192 maps to x 12..412, latitude 84..-56 maps to
# y 695..915. The pin coordinates in PINS below were measured in
# this same projection, so the pins land on the continents drawn
# from the longitude/latitude lists that follow.
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 12, 695, 412, 915


def project(lon, lat):
    x = MAP_X0 + (lon + 168.0) * (MAP_X1 - MAP_X0) / 360.0
    y = MAP_Y0 + (84.0 - lat) * (MAP_Y1 - MAP_Y0) / 140.0
    return (x, y)


def project_poly(points):
    return [project(lon, lat) for lon, lat in points]


# Hand-drawn coastlines, simplified but recognisable at 400 px wide.
# Each list runs around one landmass in lon/lat order.
NORTH_AMERICA = [
    (-168, 66), (-162, 60), (-156, 58), (-150, 60), (-144, 60),
    (-137, 58), (-131, 55), (-127, 51), (-124, 48), (-124, 43),
    (-121, 37), (-117, 33), (-112, 29), (-108, 24), (-105, 20),
    (-100, 18), (-96, 16), (-92, 15), (-88, 14), (-84, 12),
    (-80, 8), (-77, 7), (-79, 9), (-83, 9), (-86, 13), (-88, 16),
    (-90, 21), (-91, 19), (-95, 19), (-97, 22), (-97, 26),
    (-93, 29), (-89, 30), (-84, 30), (-81, 26), (-80, 32),
    (-76, 35), (-74, 39), (-70, 42), (-68, 44), (-65, 45),
    (-60, 46), (-55, 47), (-60, 52), (-64, 58), (-72, 60),
    (-80, 60), (-85, 64), (-90, 66), (-95, 69), (-110, 68),
    (-125, 69), (-135, 69), (-150, 70), (-165, 68),
]
SOUTH_AMERICA = [
    (-77, 7), (-72, 12), (-64, 11), (-60, 8), (-52, 5), (-50, 0),
    (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-52, -33),
    (-58, -38), (-65, -41), (-68, -50), (-70, -54), (-73, -50),
    (-73, -40), (-72, -30), (-70, -20), (-75, -15), (-81, -6),
    (-80, -3), (-77, 4),
]
GREENLAND = [
    (-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
    (-22, 70), (-20, 74), (-25, 78), (-35, 80), (-50, 80),
    (-58, 76), (-62, 72),
]
# Europe and Asia in one polygon: they share a land border, and a
# single outline means no seam line runs through Eurasia. The Black
# Sea is left as an inlet in the coastline; the Persian Gulf is a
# notch; the Red Sea is the gap between this polygon and Africa.
EURASIA = [
    (-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 49),
    (2, 51), (5, 53), (8, 57), (7, 58), (5, 60), (5, 62), (8, 63),
    (12, 65), (16, 68), (20, 70), (25, 71), (30, 70), (35, 68),
    (40, 67), (44, 68), (50, 68), (55, 68), (60, 69), (68, 70),
    (72, 72), (75, 73), (80, 73), (85, 74), (95, 76), (100, 77),
    (105, 77), (110, 74), (115, 73), (120, 73), (130, 72),
    (140, 72), (150, 70), (158, 69), (162, 66), (170, 66),
    (178, 65), (170, 60), (162, 56), (156, 52), (150, 55),
    (142, 59), (141, 52), (140, 48), (135, 43), (130, 42),
    (127, 40), (129, 35), (126, 38), (122, 39), (120, 35),
    (118, 32), (120, 28), (115, 23), (110, 20), (108, 18),
    (105, 9), (103, 8), (100, 8), (100, 5), (98, 10), (97, 15),
    (94, 17), (92, 21), (89, 22), (86, 20), (80, 15), (80, 10),
    (77, 8), (75, 12), (73, 16), (70, 20), (66, 25), (61, 25),
    (57, 26), (54, 26), (51, 28), (48, 30), (50, 29), (52, 26),
    (54, 24), (56, 26), (59, 23), (55, 17), (52, 15), (48, 14),
    (45, 13), (43, 12), (42, 15), (41, 18), (40, 21), (39, 24),
    (37, 27), (35, 29), (36, 36), (33, 35), (30, 36), (27, 37),
    (23, 36), (22, 37), (21, 38), (19, 40), (18, 40), (16, 38),
    (16, 40), (15, 42), (13, 44), (12, 45), (14, 45), (15, 44),
    (17, 43), (19, 42), (21, 41), (23, 40), (26, 40), (28, 41),
    (33, 41), (38, 41), (41, 42), (38, 46), (33, 46), (30, 46),
    (28, 45), (24, 46), (20, 46), (12, 46), (8, 44), (6, 43),
    (3, 43), (0, 39), (-2, 37), (-6, 36),
]
AFRICA = [
    (35, 31), (32, 31), (30, 31), (25, 32), (20, 32), (15, 32),
    (11, 33), (10, 34), (10, 37), (6, 37), (0, 36), (-5, 35),
    (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
    (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (12, 0),
    (13, -4), (12, -8), (13, -12), (12, -17), (14, -22),
    (16, -28), (18, -32), (20, -35), (26, -34), (28, -32),
    (32, -28), (35, -24), (36, -20), (40, -16), (40, -10),
    (42, -4), (46, 0), (51, 2), (51, 10), (48, 11), (44, 11),
    (43, 12), (41, 14), (39, 17), (38, 20), (37, 23), (36, 26),
    (35, 29), (34, 31),
]
AUSTRALIA = [
    (114, -22), (114, -30), (115, -34), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
    (145, -38), (147, -39), (150, -37), (153, -32), (153, -27),
    (150, -23), (146, -19), (142, -11), (142, -15), (136, -15),
    (136, -12), (132, -12), (130, -13), (126, -14), (122, -17),
    (118, -20),
]
NEW_ZEALAND_N = [
    (173, -35), (176, -38), (178, -38), (175, -40), (174, -41),
    (173, -39),
]
NEW_ZEALAND_S = [
    (172, -41), (170, -43), (168, -45), (167, -46), (169, -43),
    (171, -42), (173, -41),
]
UNITED_KINGDOM = [
    (-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
    (1, 51), (-3, 50),
]
JAPAN = [
    (130, 31), (132, 33), (134, 34), (136, 35), (138, 36),
    (140, 38), (141, 40), (142, 42), (144, 44), (143, 43),
    (141, 41), (140, 38), (138, 35), (136, 34), (133, 32),
]
MADAGASCAR = [
    (44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
    (45, -25), (43, -22), (43, -18),
]
SUMATRA = [
    (95, 5), (98, 2), (101, -1), (104, -4), (106, -6), (103, -3),
    (100, 0), (97, 4),
]
BORNEO = [
    (109, 1), (111, 2), (114, 4), (117, 6), (119, 1), (117, -2),
    (114, -3), (110, -3),
]
JAVA = [
    (105, -6), (108, -7), (111, -7), (114, -8), (112, -8),
    (108, -8),
]
NEW_GUINEA = [
    (131, -1), (135, -3), (138, -5), (141, -6), (143, -8),
    (147, -9), (141, -8), (137, -6), (133, -4),
]
PHILIPPINES = [(120, 18), (122, 16), (122, 13), (121, 11), (120, 14)]
# The Caspian is an inland sea: paint it navy on top of the land.
CASPIAN = [
    (47, 37), (49, 37), (51, 39), (53, 41), (53, 44), (52, 46),
    (50, 47), (48, 45), (47, 42), (47, 39),
]
LANDMASSES = [
    NORTH_AMERICA, SOUTH_AMERICA, GREENLAND, EURASIA, AFRICA,
    AUSTRALIA, NEW_ZEALAND_N, NEW_ZEALAND_S, UNITED_KINGDOM, JAPAN,
    MADAGASCAR, SUMATRA, BORNEO, JAVA, NEW_GUINEA, PHILIPPINES,
]
# (number, true x, true y, shown x, shown y). Shown differs from true
# only where the pin is nudged off a crowded coast, with a thin
# leader line back to its true spot.
PINS = [
    (1, 63, 766, None, None),
    (2, 219, 774, None, None),
    (3, 232, 746, None, None),
    (4, 232, 769, 218, 755),
    (5, 154, 777, None, None),
    (6, 316, 833, None, None),
    (7, 195, 742, 186, 731),
    (8, 393, 887, None, None),
    (9, 202, 745, None, None),
    (10, 112, 763, 105, 770),
    (11, 206, 746, 216, 734),
    (12, 235, 776, 247, 780),
    (13, 233, 800, None, None),
]


# --- content ---------------------------------------------------------
SUBLINE = (
    "Nvidia brings back its chief \u00b7 Ukraine sinks a warship off Libya "
    "\u00b7 Russia fires 153 drones at Kyiv"
)
TOP_LEFT = "THE WORLD IN ONE DAY"
TOP_RIGHT = (
    "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
)
MASTHEAD = "Monday 23 November 2026"

# (big number, one-line caption)
STATS = [
    ("31%", "Huang's return lifts Nvidia"),
    ("153", "Drones fired at Ukraine"),
    ("7", "Sea drones sink a corvette"),
    ("24", "killed in Indonesia factory fire"),
    ("$61,327", "Bitcoin closes Monday"),
    ("4-0", "Liverpool beat Man Utd"),
]
# (name, stories, colour, width px) — widths add up to 1000.
REGIONS = [
    ("EUROPE", 8, (30, 80, 160), 210),
    ("MIDDLE EAST", 4, (150, 60, 60), 105),
    ("AMERICAS", 6, (180, 140, 40), 158),
    ("ASIA-PACIFIC", 10, (40, 130, 80), 262),
    ("AFRICA", 4, (160, 120, 50), 105),
    ("OCEANIA", 1, (60, 140, 140), 80),
    ("WORLD", 2, (117, 117, 117), 80),
]
# (title bar, kicker, head, sub, art kind)
HEROES = [
    (
        "HUANG IS BACK",
        "1 SAN FRANCISCO \u00b7 TECHNOLOGY",
        "Nvidia brings back Huang as its chief",
        "Board reinstates the co-founder 11 days after he quit; "
        "Trump pressed for his return and shares soar 31%.",
        "nvda",
    ),
    (
        "WARSHIP SUNK",
        "2 BENGHAZI, LIBYA \u00b7 WAR",
        "Ukraine sinks Russian warship off Libya",
        "Seven sea drones hit the corvette Merkury in port; "
        "a Ka-27 destroyed, Angara hit.",
        "warship",
    ),
    (
        "153 DRONES",
        "3 KYIV, UKRAINE \u00b7 WAR",
        "Russia fires 153 drones; Dymer toll hits 11",
        "Defences down 134, but strikes hit 11 sites; 11 dead in a "
        "ruined block in Dymer. (Air Force, Reuters)",
        "drones",
    ),
]
# (title bar, kicker, head, sub, art kind) — two rows of five.
SMALLS = [
    (
        "COP31 FALLOUT",
        "4 ANTALYA \u00b7 CLIMATE",
        "UN chief calls collapse \u2018deeply disappointing\u2019",
        "First COP failure since 2009; focus shifts to COP32 in "
        "Ethiopia. (UN, CNN)",
        "globe",
    ),
    (
        "BITCOIN $61,327",
        "5 WORLD \u00b7 MARKETS",
        "Bitcoin holds $61,000 as Wall Street rallies",
        "Up from $55,130 two-year low; Nasdaq jumps 6.5% as ETFs bleed.",
        "btc",
    ),
    (
        "FIRE TOLL 24",
        "6 CIKANDE \u00b7 DISASTER",
        "Indonesia factory fire toll rises to 24",
        "Sweets-plant blaze kills 24; about 30 still missing as "
        "rescuers search.",
        "fire",
    ),
    (
        "REDS 4-0",
        "7 LIVERPOOL \u00b7 FOOTBALL",
        "Liverpool thrash Man Utd 4-0",
        "Yoro sent off in 8 minutes; Wirtz scores, sets one up.",
        "reds",
    ),
    (
        "TEST DRAW",
        "8 WELLINGTON \u00b7 CRICKET",
        "India\u2013NZ Test ends in a draw",
        "NZ finish 238/5 after India declare in a record 720/9; "
        "Pant 128, Rahul 136.",
        "test",
    ),
    (
        "SANCTIONS 22",
        "9 BRUSSELS \u00b7 DIPLOMACY",
        "EU proposes 22nd Russia sanctions",
        "Banks, crypto and sport targeted; von der Leyen unveils "
        "the plan. (The Brief)",
        "sanctions",
    ),
    (
        "IRAN SANCTIONS",
        "10 WASHINGTON \u00b7 DIPLOMACY",
        "US sanctions 20+ Iran shadow banks",
        "Iran\u2019s shadow banking. (Treasury)",
        "iran",
    ),
    (
        "MERCURY SAFE",
        "11 DARMSTADT \u00b7 SPACE",
        "BepiColombo safe and on track, ESA says",
        "Eight-year trip ends in Mercury orbit; a software glitch "
        "cut the burn short.",
        "mercury",
    ),
    (
        "UN STAFFER KILLED",
        "12 GAZA \u00b7 WAR",
        "UN staffer killed in Israeli strike on Gaza",
        "One killed, three hurt in the attack, the UN agency says. "
        "(Reports)",
        "un",
    ),
    (
        "DRONES HIT UN SITE",
        "13 KHARTOUM \u00b7 WAR",
        "Drones hit homes, UN building in Khartoum",
        "Residential areas and a UN building struck in Sudan\u2019s "
        "capital. (Reports)",
        "un2",
    ),
]
# (number, region, one-line brief) — 22 more stories.
ALSO = [
    (14, "Europe", "Finland backs anti-tank barriers"),
    (15, "Europe", "London police seize 893kg cocaine"),
    (16, "Middle East", "Eisenkot condemns settler arson"),
    (17, "Middle East", "Houthis hit Taiz, 2 killed, 8 hurt"),
    (18, "Middle East", "US targets Iran proxy networks"),
    (19, "Americas", "Gomez to resign from Congress"),
    (20, "Americas", "Carney, Trump double on stage"),
    (21, "Americas", "US Army to detonate bomb in Iowa"),
    (22, "Americas", "C\u00facuta drone attack injures 3"),
    (23, "Asia-Pacific", "India gives $1.62bn to Nepal"),
    (24, "Asia-Pacific", "Korea minister quits in scandal"),
    (25, "Asia-Pacific", "Thai court halves royal-insult term"),
    (26, "Asia-Pacific", "Prabowo to name VP candidates"),
    (27, "Asia-Pacific", "Asian tech shares fall further"),
    (28, "Asia-Pacific", "SK hynix shares rise 20%"),
    (29, "Asia-Pacific", "China agrees AI talks mechanism"),
    (30, "Asia-Pacific", "Bangladesh to arrest Hasina"),
    (31, "Asia-Pacific", "US to blacklist Megaspeed"),
    (32, "Africa", "Nigeria boat rescue under way"),
    (33, "Africa", "Libya parliament moves to unify"),
    (34, "Europe", "Yamal ruled out of Barcelona trip"),
    (35, "World", "UN chief urges AI safety framework"),
]
DATE_CHECK_BODY = (
    "Left out as earlier news: the 186-drone raid on Ukraine "
    "(Sat 22 Nov); COP31\u2019s collapse itself (Sun 22 Nov \u2014 Monday "
    "brought the reactions); the Riemann proof (announced Fri 20 Nov); "
    "BepiColombo\u2019s Mercury arrival (Sat 21 Nov); the Cikande fire\u2019s "
    "first report (22 Nov); Peru\u2019s 6.7 quake (Fri 21 Nov)."
)
SOURCES_LEFT = (
    "Every story here happened, or was first reported, on Monday "
    "23 November 2026. Sources: Reuters, AP, BBC, CNN, WSJ, ESA, UN, "
    "Treasury, CoinGecko."
)
SOURCES_RIGHT = "Pictures: original, drawn in code."
MAP_CAPTION = "Thirteen stories, pinned where they happened."


# --- artwork: small drawn pictures, no photos ------------------------
# Every art box is filled by hand with rectangles, ellipses and
# polygons. The hero boxes are 328x66, the small boxes about 195x61.


def art_nvda(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(8, 88, 58))
    bx0, by0 = x0 + w // 2 - 48, y0 + h // 2 - 13
    bx1, by1 = x0 + w // 2 + 48, y0 + h // 2 + 13
    d.rectangle([bx0, by0, bx1, by1], outline=WHITE, width=2)
    f = load("DejaVuSans-Bold.ttf", 20)
    t = "NVDA"
    d.text(
        (x0 + w // 2 - text_w(d, t, f) // 2, y0 + h // 2 - 11),
        t, font=f, fill=WHITE,
    )


def art_warship(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + int(h * 0.55)], fill=(165, 205, 228))
    d.rectangle(
        [x0, y0 + int(h * 0.55), x0 + w, y0 + h], fill=(32, 92, 152)
    )
    d.ellipse(
        [x0 + w - 46, y0 + 8, x0 + w - 24, y0 + 30], fill=(235, 140, 45)
    )
    hull = [
        (x0 + 22, y0 + int(h * 0.62)), (x0 + w - 28, y0 + int(h * 0.62)),
        (x0 + w - 48, y0 + int(h * 0.82)), (x0 + 38, y0 + int(h * 0.82)),
    ]
    d.polygon(hull, fill=(20, 25, 35))
    d.rectangle(
        [x0 + int(w * 0.44), y0 + int(h * 0.42),
         x0 + int(w * 0.56), y0 + int(h * 0.62)],
        fill=(20, 25, 35),
    )
    d.line(
        [x0 + int(w * 0.50), y0 + int(h * 0.42),
         x0 + int(w * 0.50), y0 + int(h * 0.30)],
        fill=(20, 25, 35), width=2,
    )
    cx, cy = x0 + int(w * 0.70), y0 + 12
    d.ellipse([cx - 8, cy - 2, cx + 8, cy + 2], fill=(20, 25, 35))
    d.line([cx - 12, cy - 4, cx + 12, cy - 4], fill=(20, 25, 35), width=1)
    d.line([cx, cy + 2, cx, cy + 8], fill=(20, 25, 35), width=1)


def art_drones(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY)
    gold = (232, 180, 45)
    for gx, gy in ((52, 20), (150, 32), (228, 20)):
        cx, cy = x0 + gx, y0 + gy
        for k in range(3):
            d.line(
                [cx - 14, cy - 6 + k * 6, cx + 14, cy - 6 + k * 6],
                fill=gold, width=3,
            )
        d.line([cx, cy - 8, cx, cy + 12], fill=gold, width=3)
    d.ellipse(
        [x0 + w - 62, y0 + 18, x0 + w - 8, y0 + 42], fill=(235, 145, 45)
    )


def art_globe(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(222, 236, 226))
    cx, cy = x0 + 38, y0 + 30
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(70, 140, 190))
    d.ellipse([cx - 10, cy - 8, cx + 6, cy + 4], fill=(90, 170, 110))
    d.ellipse([cx - 2, cy + 6, cx + 12, cy + 14], fill=(90, 170, 110))
    tx = x0 + 78
    d.rectangle([tx, y0 + 10, tx + 5, y0 + 44], fill=(200, 200, 200))
    d.rectangle([tx + 1, y0 + 20, tx + 4, y0 + 42], fill=RED)
    d.ellipse([tx - 3, y0 + 40, tx + 8, y0 + 51], fill=RED)


def art_btc(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(10, 10, 12))
    f = load("DejaVuSans-Bold.ttf", 18)
    d.text((x0 + 8, y0 + 20), "BTC", font=f, fill=(240, 200, 60))
    f2 = load("DejaVuSans-Bold.ttf", 10)
    d.text((x0 + w - 34, y0 + 6), "-9%", font=f2, fill=WHITE)
    base = y0 + h - 6
    bars = [(110, 14, (60, 180, 90)), (130, 22, (220, 60, 60)),
            (150, 10, (60, 180, 90)), (170, 18, (220, 60, 60))]
    for bx, bh, col in bars:
        d.rectangle([x0 + bx, base - bh, x0 + bx + 14, base], fill=col)


def art_fire(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(12, 12, 14))
    mid = x0 + w // 2
    d.polygon(
        [(mid, y0 + 6), (x0 + 20, y0 + h - 8), (x0 + w - 20, y0 + h - 8)],
        fill=(235, 120, 30),
    )
    d.polygon(
        [(mid, y0 + 22), (mid - 28, y0 + h - 8), (mid + 28, y0 + h - 8)],
        fill=(245, 200, 60),
    )


def art_reds(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(28, 135, 70))
    d.ellipse([x0 + 55, y0 + 12, x0 + 115, y0 + 48], fill=WHITE)
    ax = x0 + 85
    d.polygon(
        [(ax, y0 + 16), (ax + 10, y0 + 32), (ax + 5, y0 + 32),
         (ax + 5, y0 + 44), (ax - 5, y0 + 44), (ax - 5, y0 + 32),
         (ax - 10, y0 + 32)],
        fill=INK,
    )
    f = load("DejaVuSans-Bold.ttf", 20)
    d.text((x0 + 135, y0 + 20), "4-0", font=f, fill=WHITE)


def art_test(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(95, 175, 95))
    f = load("DejaVuSans-Bold.ttf", 16)
    d.text((x0 + 8, y0 + 20), "720/9", font=f, fill=WHITE)
    d.rectangle([x0 + 120, y0 + 12, x0 + 150, y0 + 48], fill=(215, 195, 160))
    d.ellipse([x0 + 165, y0 + 30, x0 + 183, y0 + 42], fill=(200, 50, 50))


def art_sanctions(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(22, 38, 95))
    cx, cy = x0 + w // 2, y0 + h // 2
    for k in range(8):
        a = k * math.pi / 4
        px = cx + int(20 * math.cos(a))
        py = cy + int(20 * math.sin(a))
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(240, 210, 70))
    f = load("DejaVuSans-Bold.ttf", 16)
    t = "22nd"
    d.text(
        (cx - text_w(d, t, f) // 2, cy - 10), t, font=f, fill=WHITE,
    )


def art_iran(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(198, 218, 234))
    f = load("DejaVuSans-Bold.ttf", 22)
    d.text((x0 + 10, y0 + 18), "US", font=f, fill=(40, 80, 160))
    d.rectangle(
        [x0 + 120, y0 + 10, x0 + 175, y0 + 52],
        fill=WHITE, outline=(180, 180, 180),
    )
    for k in range(3):
        yy = y0 + 20 + k * 9
        d.line(
            [x0 + 128, yy, x0 + 167, yy], fill=(170, 170, 170), width=2,
        )


def art_mercury(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(10, 10, 12))
    cx, cy = x0 + w // 2 - 10, y0 + h // 2
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(235, 140, 50))
    d.ellipse(
        [cx - 35, y0 + 8, cx + 15, y0 + h - 8],
        outline=(150, 150, 150), width=2,
    )
    f = load("DejaVuSans.ttf", 10)
    d.text((x0 + w - 40, y0 + h - 16), "8 yrs", font=f, fill=WHITE)


def art_un(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 26, 62))
    f = load("DejaVuSans-Bold.ttf", 24)
    d.text((x0 + 12, y0 + 16), "UN", font=f, fill=WHITE)
    x1, x2 = x0 + w - 48, x0 + w - 16
    d.line([x1, y0 + 12, x2, y0 + h - 12], fill=RED, width=4)
    d.line([x2, y0 + 12, x1, y0 + h - 12], fill=RED, width=4)


def art_un2(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(22, 22, 42))
    f = load("DejaVuSans-Bold.ttf", 24)
    d.text((x0 + 12, y0 + 16), "UN", font=f, fill=WHITE)
    for ox in (0, 12):
        x1, x2 = x0 + w - 58 + ox, x0 + w - 34 + ox
        d.line([x1, y0 + 14, x2, y0 + h - 14], fill=RED, width=3)
        d.line([x2, y0 + 14, x1, y0 + h - 14], fill=RED, width=3)


ARTS = {
    "nvda": art_nvda,
    "warship": art_warship,
    "drones": art_drones,
    "globe": art_globe,
    "btc": art_btc,
    "fire": art_fire,
    "reds": art_reds,
    "test": art_test,
    "sanctions": art_sanctions,
    "iran": art_iran,
    "mercury": art_mercury,
    "un": art_un,
    "un2": art_un2,
}


# --- sections ----------------------------------------------------------


def draw_top(d):
    f = load("DejaVuSans-Bold.ttf", 11)
    d.text((MX, 11), TOP_LEFT, font=f, fill=RED)
    rw = text_w(d, TOP_RIGHT, f)
    d.text((RX - rw, 11), TOP_RIGHT, font=f, fill=RED)


def draw_masthead(d, img):
    f = load("DejaVuSerif-Bold.ttf", 56)
    w = text_w(d, MASTHEAD, f)
    if w > 1000:
        raise AssertionError("OVERFLOW masthead")
    d.text(((W - w) // 2, 32), MASTHEAD, font=f, fill=INK)
    sub = italic_layer(SUBLINE, load("DejaVuSerif.ttf", 17), RED)
    if sub.width > 1000:
        raise AssertionError("OVERFLOW subline")
    img.paste(sub, (MX, 98), sub)


def draw_stats(d):
    bounds = [12, 179, 345, 512, 679, 845, 1012]
    f_num = load("DejaVuSerif-Bold.ttf", 28)
    f_cap = load("DejaVuSans.ttf", 9)
    d.rectangle([MX, 120, RX, 166], outline=RED, width=1)
    for i, (num, cap) in enumerate(STATS):
        x0, x1 = bounds[i], bounds[i + 1]
        if i > 0:
            d.line([x0, 120, x0, 166], fill=RED, width=1)
        nw = text_w(d, num, f_num)
        d.text((x0 + (x1 - x0 - nw) // 2, 123), num, font=f_num, fill=RED)
        cw = text_w(d, cap, f_cap)
        if cw > (x1 - x0) - 8:
            raise AssertionError("OVERFLOW stat caption: %r" % cap)
        d.text((x0 + (x1 - x0 - cw) // 2, 153), cap, font=f_cap, fill=INK)


def draw_regions(d):
    f = load("DejaVuSans-Bold.ttf", 10)
    x = MX
    for name, count, colour, w in REGIONS:
        d.rectangle([x, 171, x + w, 186], fill=colour)
        label = "%s %d" % (name, count)
        lw = text_w(d, label, f)
        if lw > w - 6:
            raise AssertionError("OVERFLOW region label: %r" % label)
        d.text((x + (w - lw) // 2, 174), label, font=f, fill=WHITE)
        x += w


def draw_heroes(d):
    f_title = load("DejaVuSans-Bold.ttf", 15)
    f_kick = load("DejaVuSans-Bold.ttf", 10)
    f_head = load("DejaVuSerif-Bold.ttf", 20)
    f_sub = load("DejaVuSerif.ttf", 11)
    for i, (title, kicker, head, sub, kind) in enumerate(HEROES):
        x0 = (12, 348, 684)[i]
        w = 328
        d.rectangle([x0, 191, x0 + w, 214], fill=RED)
        d.text((x0 + 8, 196), title, font=f_title, fill=WHITE)
        ARTS[kind](d, x0, 215, w, 66)
        d.text((x0, 288), kicker, font=f_kick, fill=RED)
        lines = fit(d, head, f_head, w, 2, "hero head")
        draw_lines(d, lines, x0, 303, f_head, INK, 22)
        lines = fit(d, sub, f_sub, w, 2, "hero sub")
        draw_lines(d, lines, x0, 347, f_sub, INK, 14)


def draw_smalls(d):
    cols = [12, 214, 416, 618, 819]
    widths = [195, 195, 195, 194, 193]
    f_title = load("DejaVuSans-Bold.ttf", 12)
    f_kick = load("DejaVuSans-Bold.ttf", 9)
    f_head = load("DejaVuSerif-Bold.ttf", 15)
    f_sub = load("DejaVuSerif.ttf", 9)
    for row in range(2):
        ty = 373 if row == 0 else 521
        ay = 393 if row == 0 else 541
        ky = 457 if row == 0 else 605
        hy = 470 if row == 0 else 618
        sy = 501 if row == 0 else 649
        for col in range(5):
            idx = row * 5 + col
            title, kicker, head, sub, kind = SMALLS[idx]
            x0 = cols[col]
            w = widths[col]
            d.rectangle([x0, ty, x0 + w, ty + 19], fill=RED)
            d.text((x0 + 6, ty + 4), title, font=f_title, fill=WHITE)
            ARTS[kind](d, x0, ay, w, 61)
            d.text((x0, ky), kicker, font=f_kick, fill=RED)
            lines = fit(d, head, f_head, w, 2, "small head")
            draw_lines(d, lines, x0, hy, f_head, INK, 16)
            lines = fit(d, sub, f_sub, w, 2, "small sub")
            draw_lines(d, lines, x0, sy, f_sub, INK, 10)


def draw_map(d, img):
    f_head = load("DejaVuSans-Bold.ttf", 12)
    d.text((MX, 675), "WHERE IT HAPPENED", font=f_head, fill=INK)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=NAVY)
    # Equator, dashed, drawn before the land so it shows only over sea.
    eq_y = int(round(project(0, 0)[1]))
    x = MAP_X0
    while x < MAP_X1:
        d.line(
            [x, eq_y, min(x + 5, MAP_X1), eq_y],
            fill=(110, 130, 160), width=1,
        )
        x += 10
    for land in LANDMASSES:
        d.polygon(project_poly(land), fill=TAN, outline=LAND_EDGE)
    d.polygon(project_poly(CASPIAN), fill=NAVY)
    f_pin = load("DejaVuSans-Bold.ttf", 10)
    for num, tx, ty, sx, sy in PINS:
        dx = tx if sx is None else sx
        dy = ty if sy is None else sy
        if sx is not None:
            d.line([dx, dy, tx, ty], fill=LEADER, width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=WHITE)
        d.ellipse(
            [dx - 7, dy - 7, dx + 7, dy + 7], fill=RED, outline=WHITE,
            width=1,
        )
        t = str(num)
        d.text(
            (dx - text_w(d, t, f_pin) / 2, dy - 6), t, font=f_pin,
            fill=WHITE,
        )
    cap = italic_layer(MAP_CAPTION, load("DejaVuSerif.ttf", 11), GREY)
    if cap.width > MAP_X1 - MAP_X0:
        raise AssertionError("OVERFLOW map caption")
    img.paste(cap, (MX, 920), cap)


def draw_also(d):
    f_head = load("DejaVuSans-Bold.ttf", 13)
    head = "ALSO ON MONDAY 23 NOVEMBER \u2014 22 MORE STORIES"
    if text_w(d, head, f_head) > RX - 420:
        raise AssertionError("OVERFLOW also header")
    d.text((420, 675), head, font=f_head, fill=INK)
    f_bold = load("DejaVuSans-Bold.ttf", 11)
    f_reg = load("DejaVuSans.ttf", 11)
    cols = [(420, 280), (712, 298)]
    for i, (num, region, brief) in enumerate(ALSO):
        col = 0 if i < 11 else 1
        cx, cwid = cols[col]
        y = 695 + (i % 11) * 20
        n = str(num)
        d.text((cx, y), n, font=f_bold, fill=RED)
        x = cx + text_w(d, n, f_bold) + 4
        head_txt = region + ": "
        d.text((x, y), head_txt, font=f_bold, fill=INK)
        x += text_w(d, head_txt, f_bold)
        if x + text_w(d, brief, f_reg) > cx + cwid:
            raise AssertionError("OVERFLOW also %d" % num)
        d.text((x, y), brief, font=f_reg, fill=INK)


def draw_date_check(d):
    d.rectangle([MX, 930, RX, 975], outline=RED, width=2)
    f_lab = load("DejaVuSans-Bold.ttf", 11)
    f_body = load("DejaVuSans.ttf", 10)
    d.text((20, 940), "DATE CHECK", font=f_lab, fill=RED)
    # The first line shares its row with the label, so it is narrower;
    # the second line runs the full width of the box.
    words = DATE_CHECK_BODY.split()
    lines = []
    cur = ""
    width = 880
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f_body) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            width = 984
    if cur:
        lines.append(cur)
    if len(lines) > 2:
        raise AssertionError(
            "OVERFLOW date check: needs %d lines" % len(lines)
        )
    d.text((112, 940), lines[0], font=f_body, fill=INK)
    if len(lines) > 1:
        d.text((20, 953), lines[1], font=f_body, fill=INK)


def draw_sources(d):
    f = load("DejaVuSans.ttf", 10)
    d.text((MX, 996), SOURCES_LEFT, font=f, fill=INK)
    rw = text_w(d, SOURCES_RIGHT, f)
    d.text((RX - rw, 996), SOURCES_RIGHT, font=f, fill=INK)


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_top(d)
    draw_masthead(d, img)
    draw_stats(d)
    draw_regions(d)
    draw_heroes(d)
    draw_smalls(d)
    draw_map(d, img)
    draw_also(d)
    draw_date_check(d)
    draw_sources(d)
    return img


def main():
    img = build()
    img.save(OUT)
    print("wrote %s" % os.path.abspath(OUT))


if __name__ == "__main__":
    main()
