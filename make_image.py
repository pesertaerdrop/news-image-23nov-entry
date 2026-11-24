"""Draw the front page for news-image-20261123.

One page, 1024x1024, summing up Monday 23 November 2026: 35 stories
across 7 regions, 3 big heroes, 10 small leads, a dark-navy dot-grid
world map with numbered pins, 22 more briefs, and a DATE CHECK footer.

Everything is drawn from code with Pillow. No network, no randomness,
no clock: running this file twice writes byte-identical PNGs.

Layout follows the 21 November front page (the model the reader asked
for): top bar, big date masthead, subline, six-number stat strip,
region bar, three heroes, two rows of five small leads, map + ALSO
briefs at the bottom, DATE CHECK box, sources line.
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER = (250, 246, 235)
INK = (22, 22, 22)
RED = (178, 34, 34)
GREY = (110, 105, 95)
NAVY = (16, 28, 54)
NAVY_DOT = (198, 170, 120)
GREEN = (34, 120, 60)
ORANGE = (214, 110, 30)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_cache: dict = {}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont,
         max_w: int) -> list[str]:
    """Split text into lines that fit max_w pixels."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
               fnt: ImageFont.FreeTypeFont, max_w: int, leading: int,
               fill: tuple = INK, max_lines: int = 99) -> int:
    """Draw wrapped text; return the y just below the last line."""
    lines = wrap(draw, text, fnt, max_w)[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# --- small-lead icons (all fit inside the 60px art box) --------------------
# Every icon gets (draw, x, y, w, h) and must draw only inside
# [x, x+w] x [y, y+h]. Vertical positions use fractions of h so they
# can never overflow the box (the 22 Nov ship icon crashed by drawing
# to y+62 inside a 60px box).


def icon_climate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 214))
    cx, cy, r = x + w // 2 - 30, y + h // 2, 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 140, 200))
    d.ellipse([cx - 12, cy - 16, cx + 4, cy - 2], fill=(90, 180, 110))
    d.ellipse([cx - 2, cy + 6, cx + 14, cy + 18], fill=(90, 180, 110))
    tx = x + w - 52
    d.rectangle([tx, y + 8, tx + 8, y + h - 14], fill=(255, 255, 255),
                outline=RED, width=2)
    d.ellipse([tx - 5, y + h - 18, tx + 13, y + h - 2], fill=RED)
    d.rectangle([tx + 2, y + 12, tx + 6, y + h - 22], fill=RED)


def icon_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 24, 28))
    d.text((x + 10, y + 6), "BTC", font=font(SANS_B, 20), fill=(240, 150, 30))
    d.text((x + 82, y + 12), "-9%", font=font(SANS, 11), fill=(200, 200, 200))
    bars = [18, 30, 22, 38, 26, 44]
    bw = 16
    bx = x + 12
    base = y + h - 6
    for i, bh in enumerate(bars):
        col = (60, 180, 90) if i % 2 == 0 else (200, 60, 60)
        d.rectangle([bx + i * (bw + 6), base - bh, bx + i * (bw + 6) + bw, base],
                    fill=col)


def icon_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 30, 26))
    cx = x + w // 2
    d.polygon([(cx, y + 6), (cx + 26, y + h - 14), (cx + 8, y + h - 14),
               (cx + 16, y + h - 26), (cx - 10, y + h - 14),
               (cx - 26, y + h - 14)], fill=(240, 120, 30))
    d.polygon([(cx, y + 22), (cx + 14, y + h - 14), (cx - 14, y + h - 14)],
              fill=(250, 200, 60))


def icon_football(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 140, 70))
    cx, cy, r = x + w // 2, y + h // 2, 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
              outline=(20, 20, 20), width=2)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(20, 20, 20))
    for ang in (30, 150, 270):
        import math
        px = cx + int(16 * math.cos(math.radians(ang)))
        py = cy + int(16 * math.sin(math.radians(ang)))
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(20, 20, 20))
    d.text((x + w - 52, y + h - 20), "4-0", font=font(SANS_B, 18),
           fill=(255, 255, 255))


def icon_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 130, 60))
    d.rectangle([x + w // 2 - 8, y + 8, x + w // 2 + 8, y + h - 8],
                fill=(190, 150, 90), outline=(120, 85, 40), width=2)
    d.ellipse([x + w - 44, y + h - 26, x + w - 20, y + h - 2],
              fill=(200, 40, 40), outline=(255, 255, 255), width=2)
    d.text((x + 10, y + 8), "720/9", font=font(SANS_B, 16),
           fill=(255, 255, 255))


def icon_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 150))
    cx, cy = x + w // 2, y + h // 2
    import math
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        px = cx + int(20 * math.cos(ang))
        py = cy + int(20 * math.sin(ang))
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(250, 210, 60))
    d.text((x + w - 46, y + h - 20), "22nd", font=font(SANS_B, 14),
           fill=(255, 255, 255))


def icon_seal(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 235, 230))
    d.rectangle([x + 14, y + 8, x + w - 60, y + h - 8], fill=(255, 255, 255),
                outline=(40, 40, 40), width=2)
    for i in range(3):
        ly = y + 16 + i * 12
        d.line([x + 22, ly, x + w - 68, ly], fill=(120, 120, 120), width=2)
    cx, cy, r = x + w - 34, y + h // 2, 16
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.text((cx - 8, cy - 7), "US", font=font(SANS_B, 11), fill=(255, 255, 255))


def icon_space(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 22, 48))
    cx, cy, r = x + w // 2 - 20, y + h // 2, 16
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(210, 120, 60))
    d.ellipse([cx - r - 14, cy - 4, cx + r + 14, cy + 4], outline=(200, 200, 200),
              width=2)
    for sx, sy in ((x + 14, y + 10), (x + w - 18, y + 12), (x + w - 30, y + h - 12)):
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    d.text((x + w - 58, y + h - 20), "8 yrs", font=font(SANS_B, 13),
           fill=(255, 255, 255))


def icon_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 205, 195))
    d.rectangle([x + 16, y + h - 30, x + 60, y + h - 6], fill=(120, 110, 95))
    d.rectangle([x + 70, y + h - 40, x + 110, y + h - 6], fill=(90, 82, 72))
    d.rectangle([x + 120, y + h - 24, x + w - 16, y + h - 6], fill=(140, 130, 115))
    d.rectangle([x + w - 52, y + 8, x + w - 12, y + 34], fill=(255, 255, 255),
                outline=RED, width=2)
    d.rectangle([x + w - 38, y + 12, x + w - 26, y + 30], fill=RED)
    d.rectangle([x + w - 44, y + 18, x + w - 20, y + 24], fill=RED)


def icon_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 34, 44))
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 26, cy - 6, cx + 26, cy + 6], fill=(180, 180, 180))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(220, 60, 60))
    for ax, ay in ((cx - 30, cy - 14), (cx + 30, cy - 14),
                   (cx - 30, cy + 14), (cx + 30, cy + 14)):
        d.ellipse([ax - 8, ay - 3, ax + 8, ay + 3], fill=(120, 120, 120))
        d.line([ax, ay, cx, cy], fill=(150, 150, 150), width=2)


# --- hero art (110px tall) ---------------------------------------------------


def art_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 40, 20))
    for i in range(6):
        d.line([x + 10, y + 12 + i * 16, x + w - 10, y + 12 + i * 16],
               fill=(40, 110, 60), width=1)
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 52, cy - 34, cx + 52, cy + 34], fill=(118, 185, 0),
                outline=(220, 240, 200), width=3)
    d.rectangle([cx - 30, cy - 18, cx + 30, cy + 18], fill=(20, 60, 26))
    d.text((cx - 24, cy - 11), "NVDA", font=font(SANS_B, 16),
           fill=(255, 255, 255))
    for px in range(cx - 44, cx + 45, 11):
        d.line([px, cy - 44, px, cy - 34], fill=(220, 240, 200), width=3)
        d.line([px, cy + 34, px, cy + 44], fill=(220, 240, 200), width=3)


def art_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(150, 190, 220))
    for wx in range(x + 8, x + w - 8, 26):
        d.line([wx, y + h - 8, wx + 12, y + h - 8], fill=(255, 255, 255), width=2)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(70, 120, 170))
    d.polygon([(x + 24, y + h - 34), (x + w - 24, y + h - 34),
               (x + w - 44, y + h - 12), (x + 44, y + h - 12)],
              fill=(120, 40, 40))
    d.rectangle([x + w // 2 - 14, y + h - 62, x + w // 2 + 14, y + h - 34],
                fill=(220, 220, 210))
    d.rectangle([x + w // 2 - 4, y + h - 78, x + w // 2 + 4, y + h - 62],
                fill=(60, 60, 60))
    d.polygon([(x + w - 96, y + 6), (x + w - 66, y + 34), (x + w - 120, y + 34)],
              fill=(240, 140, 40))
    d.ellipse([x + w - 112, y - 2, x + w - 76, y + 34], fill=(250, 90, 30))
    d.ellipse([x + w - 100, y + 8, x + w - 88, y + 24], fill=(250, 200, 60))
    d.ellipse([x + 34, y + 12, x + 50, y + 28], fill=(40, 40, 40))
    d.line([x + 42, y + 28, x + 64, y + 50], fill=(40, 40, 40), width=2)
    d.ellipse([x + 90, y + 8, x + 104, y + 22], fill=(40, 40, 40))


def art_drones(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 24, 48))
    for bx, bh, bw in ((x + 8, 44, 46), (x + 62, 60, 40), (x + 110, 38, 52),
                       (x + 170, 52, 44), (x + 222, 40, 48), (x + 278, 56, 40)):
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(8, 12, 26))
        for wy in range(y + h - bh + 8, y + h - 6, 12):
            d.rectangle([bx + 6, wy, bx + 14, wy + 5], fill=(250, 200, 80))
    for dx, dy in ((x + 40, y + 16), (x + 120, y + 10), (x + 200, y + 20),
                   (x + 260, y + 12), (x + 300, y + 26)):
        d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(255, 255, 255))
        d.line([dx, dy, dx + 18, dy + 10], fill=(200, 200, 200), width=1)
    d.ellipse([x + w - 60, y + 8, x + w - 20, y + 48], fill=(250, 170, 60))


# --- the map: dark navy dot-grid + numbered pins ------------------------------

LAND_BOXES = [
    # North America
    (-168, -55, 50, 72), (-125, -66, 25, 50), (-117, -83, 8, 32),
    (-58, -20, 60, 84),
    # South America
    (-78, -50, -5, 12), (-75, -35, -20, -5), (-73, -53, -55, -20),
    # Europe
    (-11, 25, 36, 60), (5, 30, 55, 70), (20, 40, 45, 60), (-5, 2, 50, 58),
    # Africa
    (-10, 35, 15, 32), (8, 42, -5, 15), (12, 35, -35, -5), (43, 50, -25, -12),
    # Asia
    (35, 60, 12, 42), (50, 90, 35, 55), (60, 180, 50, 77),
    (75, 135, 20, 53), (68, 90, 8, 35), (95, 110, 5, 28),
    (95, 141, -11, 6), (130, 146, 31, 45),
    # Australia + New Zealand
    (113, 154, -39, -11), (166, 178, -47, -34),
]


def on_land(lon: float, lat: float) -> bool:
    for lo0, lo1, la0, la1 in LAND_BOXES:
        if lo0 <= lon <= lo1 and la0 <= lat <= la1:
            return True
    return False


# (number, lon, lat, dx, dy) — dx/dy nudge the pin off its true spot with a
# thin leader line, so close neighbours (Brussels/Darmstadt, New York/
# Washington, Benghazi/Antalya/Gaza) do not cover each other.
PINS = [
    (1, -122.4, 37.8, 0, 0),
    (2, 20.1, 32.1, 0, 0),
    (3, 30.5, 50.4, 0, 0),
    (4, 30.7, 36.9, -14, -14),
    (5, -74.0, 40.7, 0, 0),
    (6, 106.2, -6.2, 0, 0),
    (7, -3.0, 53.4, -9, -11),
    (8, 174.8, -41.3, 0, 0),
    (9, 4.35, 50.85, 0, 0),
    (10, -77.0, 38.9, -7, 7),
    (11, 8.65, 49.87, 10, -12),
    (12, 34.5, 31.5, 12, 4),
    (13, 32.5, 15.6, 0, 0),
]


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    lon0, lon1 = -170.0, 190.0
    lat0, lat1 = -60.0, 85.0
    mw, mh = x1 - x0, y1 - y0

    def px(lon):
        return x0 + (lon - lon0) / (lon1 - lon0) * mw

    def py(lat):
        return y0 + (lat1 - lat) / (lat1 - lat0) * mh

    lon = -170.0
    while lon <= 190.0:
        lat = -58.0
        while lat <= 84.0:
            if on_land(lon, lat):
                cx, cy = px(lon), py(lat)
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=NAVY_DOT)
            lat += 4.0
        lon += 4.0
    for num, lon, lat, dx, dy in PINS:
        tx, ty = px(lon), py(lat)
        cx, cy = tx + dx, ty + dy
        if dx or dy:
            d.line([tx, ty, cx, cy], fill=(220, 220, 220), width=1)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=font(SANS_B, 10))
        d.text((cx - tw / 2, cy - 7), t, font=font(SANS_B, 10),
               fill=(255, 255, 255))


# --- the stories ----------------------------------------------------------------

HEROES = [
    {
        "label": "HUANG IS BACK",
        "art": art_chip,
        "place": "1 SAN FRANCISCO · TECHNOLOGY",
        "cert": "REPORTED",
        "head": "Nvidia brings back Huang as its chief",
        "sub": "Board reinstates the co-founder 11 days after he quit; Trump pressed for his return and shares soar 31%. (Reuters, WSJ)",
    },
    {
        "label": "WARSHIP SUNK",
        "art": art_ship,
        "place": "2 BENGHAZI, LIBYA · WAR",
        "cert": "REPORTED",
        "head": "Ukraine sinks Russian warship off Libya",
        "sub": "Seven sea drones hit the corvette Merkury in port; a Ka-27 helicopter is destroyed and the cargo ship Angara is hit. (CNN, Reuters)",
    },
    {
        "label": "153 DRONES",
        "art": art_drones,
        "place": "3 KYIV, UKRAINE · WAR",
        "cert": "REPORTED",
        "head": "Russia fires 153 drones; Dymer toll hits 11",
        "sub": "Defences down 134, but strikes land at 11 sites; rescuers pull 11 dead from a ruined block in Dymer. (Air Force, Reuters)",
    },
]

SMALLS = [
    {"label": "COP31 FALLOUT", "art": icon_climate,
     "place": "4 ANTALYA · CLIMATE",
     "head": "UN chief calls the collapse 'deeply disappointing'",
     "sub": "First COP failure since 2009; focus shifts to COP32 in Ethiopia. (UN, CNN)"},
    {"label": "BITCOIN: $61,327", "art": icon_bitcoin,
     "place": "5 WORLD · MARKETS",
     "head": "Bitcoin holds $61,000 as Wall Street rallies",
     "sub": "Up from a $55,130 two-year low; Nasdaq jumps 6.5% as ETFs bleed $1.8bn. (CoinDesk)"},
    {"label": "FIRE TOLL 24", "art": icon_fire,
     "place": "6 CIKANDE · DISASTER",
     "head": "Indonesia factory fire toll rises to 24",
     "sub": "Sweets-plant blaze kills 24; about 30 still missing as rescuers search. (Reuters)"},
    {"label": "REDS 4-0", "art": icon_football,
     "place": "7 LIVERPOOL · FOOTBALL",
     "head": "Liverpool thrash Man Utd 4-0",
     "sub": "Yoro sent off in 8 minutes on Pochettino's debut; Wirtz scores and sets one up. (Reports)"},
    {"label": "TEST DRAW", "art": icon_cricket,
     "place": "8 WELLINGTON · CRICKET",
     "head": "India–NZ Test ends in a draw",
     "sub": "NZ finish 238/5 after India declare at a record 720/9; Pant hits 128. (Reports)"},
    {"label": "SANCTIONS 22", "art": icon_eu,
     "place": "9 BRUSSELS · DIPLOMACY",
     "head": "EU proposes 22nd Russia sanctions package",
     "sub": "Banks, crypto and sport targeted; von der Leyen unveils the plan. (Reports)"},
    {"label": "IRAN SANCTIONS", "art": icon_seal,
     "place": "10 WASHINGTON · DIPLOMACY",
     "head": "US sanctions 20+ Iranian shadow-banking entities",
     "sub": "Treasury targets networks it links to Iran's shadow banking. (Treasury)"},
    {"label": "MERCURY: SAFE", "art": icon_space,
     "place": "11 DARMSTADT · SPACE",
     "head": "BepiColombo safe and on track, ESA says",
     "sub": "Eight-year trip ends in Mercury orbit; a software glitch cut the burn short. (ESA, Reuters)"},
    {"label": "UN STAFFER KILLED", "art": icon_gaza,
     "place": "12 GAZA · WAR",
     "head": "UN staffer killed in Israeli strike on Gaza",
     "sub": "One killed, three hurt in the attack, the UN agency says. (Reports)"},
    {"label": "DRONES HIT UN SITE", "art": icon_drone,
     "place": "13 KHARTOUM · WAR",
     "head": "Drones hit homes and UN building in Khartoum",
     "sub": "Residential areas and a UN building struck in Sudan's capital. (Reports)"},
]

ALSO = [
    (14, "Europe", "Finland backs anti-tank barriers"),
    (15, "Europe", "London police seize 893kg cocaine"),
    (16, "Middle East", "Eisenkot condemns settler arson"),
    (17, "Middle East", "Houthis attack Taiz, 2 killed"),
    (18, "Middle East", "US targets Iranian proxy networks"),
    (19, "Americas", "Gomez to resign from Congress"),
    (20, "Americas", "Carney shares stage with Trump double"),
    (21, "Americas", "US Army to detonate toxic lead in Iowa"),
    (22, "Americas", "C\u00facuta drone attack injures 3"),
    (23, "Asia-Pacific", "India gives $1.62bn to Nepal"),
    (24, "Asia-Pacific", "Korea minister quits over cheating"),
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

STATS = [
    ("31%", "Nvidia shares jump on Huang's return"),
    ("153", "Russian drones fired overnight at Ukraine"),
    ("7", "sea drones sink Russian corvette off Libya"),
    ("24", "killed in Indonesia factory fire"),
    ("$61,327", "Bitcoin closes Monday"),
    ("4-0", "Liverpool beat Man Utd"),
]

REGIONS = [
    ("EUROPE", 8, (30, 80, 160)),
    ("MIDDLE EAST", 4, (160, 60, 60)),
    ("AMERICAS", 6, (180, 140, 40)),
    ("ASIA-PACIFIC", 10, (40, 120, 80)),
    ("AFRICA", 4, (150, 110, 40)),
    ("OCEANIA", 1, (60, 140, 160)),
    ("WORLD", 2, (110, 110, 110)),
]

DATE_CHECK = ("Left out as earlier news: the 186-drone raid on Ukraine (Sat 22 Nov); "
              "COP31's collapse itself (Sun 22 Nov \u2014 Monday brought the reactions); "
              "the Riemann proof (announced Fri 20 Nov); BepiColombo's Mercury arrival "
              "(Sat 21 Nov); the Cikande fire's first report (22 Nov); Peru's 6.7 quake "
              "(Fri 21 Nov).")


# --- build -----------------------------------------------------------------------


def build() -> Image.Image:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 12
    rx = W - 12

    # top bar
    d.text((mx, 2), "THE WORLD IN ONE DAY", font=font(SANS_B, 11), fill=RED)
    right = "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
    d.text((rx - d.textlength(right, font=font(SANS_B, 11)), 2), right,
           font=font(SANS_B, 11), fill=RED)

    # masthead
    d.text((mx, 20), "Monday 23 November 2026", font=font(SERIF_B, 56), fill=INK)

    # subline
    d.text((mx, 92),
           "Nvidia brings back its chief \u00b7 Ukraine sinks a warship off Libya \u00b7 "
           "Russia fires 153 drones at Kyiv",
           font=font(SERIF, 15), fill=RED)

    # stat strip
    y0, y1 = 112, 170
    col_w = (rx - mx) / 6
    for i, (num, cap) in enumerate(STATS):
        cx = mx + i * col_w
        d.text((cx + 6, y0 + 2), num, font=font(SERIF_B, 30), fill=INK)
        text_block(d, cx + 6, y0 + 36, cap, font(SANS, 9), int(col_w) - 14, 11,
                   fill=GREY, max_lines=2)
        if i:
            d.line([cx, y0 + 4, cx, y1 - 6], fill=(200, 195, 185), width=1)
    d.line([mx, y1, rx, y1], fill=INK, width=1)

    # region bar (each segment gets a minimum width so short labels fit)
    y0, y1 = 172, 190
    total = sum(c for _, c, _ in REGIONS)
    min_w = 58.0
    extra = (rx - mx) - min_w * len(REGIONS)
    x = mx
    for name, count, col in REGIONS:
        seg_w = min_w + extra * count / total
        d.rectangle([x, y0, x + seg_w, y1], fill=col)
        label = f"{name} {count}"
        tw = d.textlength(label, font=font(SANS_B, 10))
        d.text((x + (seg_w - tw) / 2, y0 + 4), label, font=font(SANS_B, 10),
               fill=(255, 255, 255))
        x += seg_w

    # heroes: 3 columns
    hy = 196
    col_w = (rx - mx - 12) / 3
    for i, hero in enumerate(HEROES):
        hx = mx + i * (col_w + 6)
        d.rectangle([hx, hy, hx + col_w, hy + 22], fill=RED)
        d.text((hx + 8, hy + 4), hero["label"], font=font(SANS_B, 13),
               fill=(255, 255, 255))
        hero["art"](d, int(hx), hy + 22, int(col_w), 100)
        ly = hy + 122
        d.text((hx, ly), hero["place"], font=font(SANS_B, 10), fill=RED)
        cert = hero["cert"]
        d.text((hx + col_w - d.textlength(cert, font=font(SANS, 9)), ly),
               cert, font=font(SANS, 9), fill=GREY)
        text_block(d, hx, ly + 15, hero["head"], font(SANS_B, 17),
                   int(col_w), 20, max_lines=2)
        text_block(d, hx, ly + 57, hero["sub"], font(SANS, 10),
                   int(col_w), 13, max_lines=3)

    # small leads: 2 rows x 5
    scol_w = (rx - mx - 24) / 5
    for row in range(2):
        sy = 402 + row * 148
        for col in range(5):
            s = SMALLS[row * 5 + col]
            sx = mx + col * (scol_w + 6)
            d.rectangle([sx, sy, sx + scol_w, sy + 18], fill=RED)
            d.text((sx + 6, sy + 3), s["label"], font=font(SANS_B, 11),
                   fill=(255, 255, 255))
            s["art"](d, int(sx), sy + 18, int(scol_w), 60)
            ly = sy + 78
            d.text((sx, ly), s["place"], font=font(SANS_B, 9), fill=RED)
            text_block(d, sx, ly + 13, s["head"], font(SANS_B, 12),
                       int(scol_w), 15, max_lines=2)
            text_block(d, sx, ly + 45, s["sub"], font(SANS, 9),
                       int(scol_w), 12, max_lines=2)

    # bottom block: map (left) + ALSO (right)
    by = 700
    d.text((mx, by), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=INK)
    d.text((mx, by + 16), "pins match story numbers", font=font(SANS, 9),
           fill=GREY)
    draw_map(d, mx, by + 32, 400, by + 212)
    d.text((mx, by + 218),
           "Each number is the story with that number on this page.",
           font=font(SANS, 9), fill=GREY)

    ax = 412
    d.text((ax, by), "ALSO ON MONDAY 23 NOVEMBER \u2014 22 MORE STORIES",
           font=font(SANS_B, 12), fill=INK)
    col2_w = (rx - ax - 12) / 2
    for j, (num, region, text) in enumerate(ALSO):
        col = j // 11
        row = j % 11
        bx = ax + col * (col2_w + 12)
        byy = by + 20 + row * 19
        d.text((bx, byy), f"{num}", font=font(SANS_B, 10), fill=RED)
        d.text((bx + 22, byy), f"{region}: {text}", font=font(SANS, 9),
               fill=INK)

    # DATE CHECK box (red border, closed)
    dy0, dy1 = 944, 998
    d.rectangle([mx, dy0, rx, dy1], outline=RED, width=2)
    d.text((mx + 8, dy0 + 5), "DATE CHECK", font=font(SANS_B, 10), fill=RED)
    text_block(d, mx + 8, dy0 + 20, DATE_CHECK, font(SANS, 9), rx - mx - 16,
               12, max_lines=3)

    # footer
    d.text((mx, 1006),
           "Sources: Reuters, AP, BBC, CNN, WSJ, ESA, UN, Treasury, CoinDesk. "
           "Pictures: original, drawn in code. Every story here happened, or was "
           "first reported, on Monday 23 November 2026.",
           font=font(SANS, 8), fill=GREY)
    d.text((mx, 1016),
           "CERTAINTY: REPORTED = carried by the day's wires \u00b7 CLAIM = one "
           "side's account, labelled as such \u00b7 FORECAST = still to happen "
           "when drawn.",
           font=font(SANS, 8), fill=GREY)
    foot = "MONDAY 23 NOVEMBER 2026 \u00b7 ONE PAGE"
    d.text((rx - d.textlength(foot, font=font(SANS_B, 8)), 1016), foot,
           font=font(SANS_B, 8), fill=INK)

    return img


def main() -> int:
    img = build()
    img.save(OUT)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
