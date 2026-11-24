"""Draw the Monday 23 November 2026 front page (news-image-20261123).

One image, 1024x1024, that sums up the day's world news: 35 stories
across 7 regions, three heroes, ten small leads and twenty-two more
briefs, a numbered world map, a DATE CHECK box and a single sources
line. The layout follows the 21 November front page exactly: a small
red top bar with a clear margin above it, a big serif masthead, a red
italic subline, a six-box stat strip, a seven-segment region bar, three
heroes, two rows of five small leads, a dark navy dot-grid map beside
the ALSO list, a closed red DATE CHECK box, and one sources line with
a clear margin below it. No text touches the edge of the picture.

Run: python3 make_image.py  -> writes entry.png next to this file.
The file is deterministic: two runs write identical bytes.
"""

from __future__ import annotations

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (250, 246, 235)
INK = (20, 20, 20)
RED = (178, 34, 34)
GREY = (110, 110, 105)
NAVY = (18, 28, 55)
LAND = (198, 170, 120)
PIN = (200, 30, 30)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_I = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Split text into lines that fit `width` pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- icons
# Every icon draws strictly inside its (x, y, w, h) box. Vertical
# positions are fractions of h so nothing can run past the box bottom.

def icon_chip(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(16, 90, 40))
    for i in range(5):
        yy = y + int(h * (0.15 + i * 0.17))
        draw.line([x + int(w * 0.06), yy, x + int(w * 0.94), yy],
                  fill=(40, 140, 70), width=2)
    cx0, cy0 = x + int(w * 0.36), y + int(h * 0.22)
    cx1, cy1 = x + int(w * 0.64), y + int(h * 0.78)
    draw.rectangle([cx0, cy0, cx1, cy1], fill=(30, 160, 80),
                   outline=(220, 240, 220), width=2)
    draw.rectangle([cx0 + 8, cy0 + 8, cx1 - 8, cy1 - 8], fill=(12, 60, 30))
    f = font(SANS_B, 15)
    tw = draw.textlength("NVDA", font=f)
    draw.text((x + (w - tw) / 2, y + h * 0.42), "NVDA", font=f,
              fill=(235, 245, 235))


def icon_ship(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(150, 190, 220))
    for i in range(3):
        wy = y + int(h * (0.82 + i * 0.06))
        draw.line([x + int(w * 0.05), wy, x + int(w * 0.95), wy],
                  fill=(90, 140, 190), width=2)
    # hull
    draw.polygon([(x + int(w * 0.14), y + int(h * 0.62)),
                  (x + int(w * 0.86), y + int(h * 0.62)),
                  (x + int(w * 0.76), y + int(h * 0.82)),
                  (x + int(w * 0.24), y + int(h * 0.82))],
                 fill=(150, 40, 40))
    # superstructure
    draw.rectangle([x + int(w * 0.42), y + int(h * 0.42),
                    x + int(w * 0.58), y + int(h * 0.62)],
                   fill=(225, 225, 215))
    # explosion
    ex, ey = x + int(w * 0.78), y + int(h * 0.28)
    for r, col in ((16, (240, 140, 30)), (10, (250, 200, 60)),
                   (5, (255, 240, 150))):
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)
    # drone
    dx, dy = x + int(w * 0.16), y + int(h * 0.22)
    draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(30, 30, 30))
    draw.line([dx - 12, dy, dx + 12, dy], fill=(30, 30, 30), width=2)


def icon_drones(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(14, 18, 42))
    # moon
    mx, my = x + int(w * 0.84), y + int(h * 0.28)
    draw.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=(240, 180, 80))
    # buildings
    for i, (bx, bw, bh) in enumerate([(0.04, 0.16, 0.55), (0.24, 0.14, 0.75),
                                      (0.42, 0.18, 0.6), (0.64, 0.14, 0.8),
                                      (0.82, 0.14, 0.5)]):
        bx0 = x + int(w * bx)
        by0 = y + h - int(h * bh)
        draw.rectangle([bx0, by0, bx0 + int(w * bw), y + h],
                       fill=(28, 30, 55))
        for wy in range(by0 + 8, y + h - 6, 12):
            for wx in range(bx0 + 4, bx0 + int(w * bw) - 4, 10):
                draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(240, 200, 90))
    # drones
    for fx, fy in [(0.2, 0.18), (0.5, 0.12), (0.68, 0.24)]:
        dx, dy = x + int(w * fx), y + int(h * fy)
        draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(240, 240, 240))
        draw.line([dx - 10, dy, dx + 10, dy], fill=(240, 240, 240), width=2)


def icon_globe(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(220, 235, 220))
    cx, cy, r = x + int(w * 0.3), y + int(h * 0.5), int(h * 0.36)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 190),
                 outline=(30, 80, 140), width=2)
    draw.ellipse([cx - int(r * 0.45), cy - int(r * 0.55),
                  cx + int(r * 0.35), cy + int(r * 0.1)], fill=(90, 170, 90))
    draw.ellipse([cx - int(r * 0.2), cy + int(r * 0.3),
                  cx + int(r * 0.55), cy + int(r * 0.75)], fill=(90, 170, 90))
    # thermometer
    tx = x + int(w * 0.68)
    draw.rectangle([tx - 3, y + int(h * 0.15), tx + 3, y + int(h * 0.7)],
                   fill=(200, 200, 200), outline=(120, 120, 120), width=1)
    draw.ellipse([tx - 8, y + int(h * 0.66), tx + 8, y + int(h * 0.86)],
                 fill=(200, 40, 40))
    draw.rectangle([tx - 3, y + int(h * 0.45), tx + 3, y + int(h * 0.7)],
                   fill=(200, 40, 40))


def icon_btc(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 20, 20))
    f = font(SANS_B, 16)
    draw.text((x + 8, y + 4), "BTC", font=f, fill=(240, 190, 60))
    bars = [(0.45, (40, 160, 70)), (0.6, (200, 60, 60)), (0.75, (40, 160, 70)),
            (0.9, (200, 60, 60))]
    for i, (frac, col) in enumerate(bars):
        bx = x + int(w * (0.12 + i * 0.2))
        top = y + int(h * frac)
        draw.rectangle([bx, top, bx + int(w * 0.14), y + int(h * 0.92)],
                       fill=col)
    f2 = font(SANS_B, 11)
    draw.text((x + int(w * 0.62), y + int(h * 0.06)), "-9%",
              font=f2, fill=(240, 240, 240))


def icon_fire(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 22, 18))
    draw.polygon([(x + int(w * 0.5), y + int(h * 0.12)),
                  (x + int(w * 0.82), y + int(h * 0.88)),
                  (x + int(w * 0.18), y + int(h * 0.88))],
                 fill=(240, 120, 30))
    draw.polygon([(x + int(w * 0.5), y + int(h * 0.38)),
                  (x + int(w * 0.68), y + int(h * 0.88)),
                  (x + int(w * 0.32), y + int(h * 0.88))],
                 fill=(250, 200, 60))


def icon_ball(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 130, 60))
    cx, cy, r = x + int(w * 0.32), y + int(h * 0.5), int(h * 0.34)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 245, 245),
                 outline=(20, 20, 20), width=2)
    draw.polygon([(cx, cy - 8), (cx + 8, cy + 2), (cx + 4, cy + 10),
                  (cx - 4, cy + 10), (cx - 8, cy + 2)], fill=(20, 20, 20))
    f = font(SANS_B, 20)
    draw.text((x + int(w * 0.6), y + int(h * 0.32)), "4-0", font=f,
              fill=(255, 255, 255))


def icon_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(120, 170, 90))
    # bat
    draw.polygon([(x + int(w * 0.42), y + int(h * 0.15)),
                  (x + int(w * 0.52), y + int(h * 0.12)),
                  (x + int(w * 0.58), y + int(h * 0.55)),
                  (x + int(w * 0.48), y + int(h * 0.58))],
                 fill=(220, 190, 140), outline=(120, 80, 40), width=2)
    # ball
    bx, by = x + int(w * 0.78), y + int(h * 0.68)
    draw.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(200, 30, 30))
    f = font(SANS_B, 13)
    draw.text((x + int(w * 0.6), y + int(h * 0.1)), "720/9", font=f,
              fill=(255, 255, 255))


def icon_eu(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 50, 140))
    import math
    cx, cy, r = x + int(w * 0.38), y + int(h * 0.5), int(h * 0.32)
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + int(r * math.cos(a)), cy + int(r * math.sin(a))
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(250, 210, 60))
    f = font(SANS_B, 14)
    draw.text((x + int(w * 0.68), y + int(h * 0.38)), "22nd", font=f,
              fill=(255, 255, 255))


def icon_doc(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 235, 230))
    draw.rectangle([x + int(w * 0.14), y + int(h * 0.14),
                    x + int(w * 0.62), y + int(h * 0.86)],
                   fill=(255, 255, 255), outline=(60, 60, 60), width=2)
    for i in range(4):
        ly = y + int(h * (0.28 + i * 0.14))
        draw.line([x + int(w * 0.2), ly, x + int(w * 0.56), ly],
                  fill=(120, 120, 120), width=2)
    f = font(SANS_B, 13)
    draw.text((x + int(w * 0.68), y + int(h * 0.4)), "US", font=f,
              fill=(178, 34, 34))


def icon_planet(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(16, 18, 40))
    cx, cy, r = x + int(w * 0.42), y + int(h * 0.5), int(h * 0.3)
    draw.ellipse([cx - int(r * 1.5), cy - 3, cx + int(r * 1.5), cy + 3],
                 fill=(200, 200, 200))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(230, 140, 60),
                 outline=(250, 190, 110), width=2)
    draw.ellipse([cx - int(r * 0.4), cy - int(r * 0.4),
                  cx - int(r * 0.1), cy - int(r * 0.1)], fill=(200, 110, 40))
    f = font(SANS_B, 11)
    draw.text((x + int(w * 0.72), y + int(h * 0.62)), "8 yrs", font=f,
              fill=(240, 240, 240))


def icon_cross(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(225, 225, 220))
    # buildings
    for i, (bx, bw, bh) in enumerate([(0.08, 0.24, 0.5), (0.38, 0.26, 0.68),
                                      (0.7, 0.22, 0.42)]):
        draw.rectangle([x + int(w * bx), y + h - int(h * bh),
                        x + int(w * (bx + bw)), y + h],
                       fill=(140, 135, 125))
    # red cross sign
    cx, cy = x + int(w * 0.78), y + int(h * 0.3)
    draw.rectangle([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 255, 255),
                   outline=(178, 34, 34), width=2)
    draw.rectangle([cx - 3, cy - 10, cx + 3, cy + 10], fill=(178, 34, 34))
    draw.rectangle([cx - 10, cy - 3, cx + 10, cy + 3], fill=(178, 34, 34))


def icon_drone2(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 32, 48))
    for fx, fy in [(0.3, 0.35), (0.68, 0.6)]:
        dx, dy = x + int(w * fx), y + int(h * fy)
        draw.line([dx - 14, dy - 10, dx + 14, dy + 10],
                  fill=(200, 200, 200), width=3)
        draw.line([dx - 14, dy + 10, dx + 14, dy - 10],
                  fill=(200, 200, 200), width=3)
        draw.ellipse([dx - 6, dy - 6, dx + 6, dy + 6], fill=(220, 60, 60))
    f = font(SANS_B, 11)
    draw.text((x + int(w * 0.08), y + int(h * 0.08)), "UN", font=f,
              fill=(240, 240, 240))


# ------------------------------------------------------------------ map
# Dark navy dot-grid world map. Land is a list of lon/lat boxes; a dot
# is drawn on every 4-degree grid point that falls on land.

LAND_BOXES = [
    (-168, -95, 55, 72), (-125, -66, 25, 49), (-117, -83, 8, 32),
    (-58, -20, 60, 84),
    (-80, -50, -5, 12), (-75, -55, -55, -5),
    (-10, 40, 36, 70), (-5, 2, 50, 59), (5, 30, 55, 70),
    (-18, 35, 15, 35), (10, 40, -35, 15), (43, 50, -25, -12),
    (40, 180, 50, 75), (45, 135, 35, 55), (68, 90, 8, 35),
    (95, 105, 5, 28), (95, 141, -10, 5), (130, 145, 31, 45),
    (113, 154, -39, -11), (166, 178, -47, -34),
]

# (story number, lon, lat, nudge_x_px, nudge_y_px)
PINS = [
    (1, -122, 37, 0, 0), (2, 20, 32, 0, 0), (3, 30, 50, 0, 0),
    (4, 30, 37, -14, -14), (5, -40, 30, 0, 0), (6, 106, -6, 0, 0),
    (7, -3, 53, -9, -11), (8, 175, -41, 0, 0), (9, 4, 51, 0, 0),
    (10, -77, 39, -7, 7), (11, 8, 50, 10, -12), (12, 34, 31, 12, 4),
    (13, 32, 15, 0, 0),
]


def draw_map(draw, x, y, w, h):
    """Dark navy dot-grid map with numbered pins. Returns pin centres."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    lon0, lon1, lat0, lat1 = -168, 192, -58, 84
    def px(lon):
        return x + (lon - lon0) / (lon1 - lon0) * w
    def py(lat):
        return y + (lat1 - lat) / (lat1 - lat0) * h
    # dots every 4 degrees on land
    lon = lon0
    while lon <= lon1:
        lat = lat0
        while lat <= lat1:
            on_land = any(a <= lon <= b and c <= lat <= d
                          for a, b, c, d in LAND_BOXES)
            if on_land:
                cx, cy = px(lon), py(lat)
                draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=LAND)
            lat += 4
        lon += 4
    # pins
    f = font(SANS_B, 9)
    centres = {}
    for num, lo, la, nx, ny in PINS:
        cx, cy = px(lo) + nx, py(la) + ny
        centres[num] = (cx, cy)
        if nx or ny:
            draw.line([px(lo), py(la), cx, cy], fill=(220, 220, 220), width=1)
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=PIN,
                     outline=(255, 255, 255), width=1)
        t = str(num)
        tw = draw.textlength(t, font=f)
        draw.text((cx - tw / 2, cy - 5), t, font=f, fill=(255, 255, 255))
    return centres


# ------------------------------------------------------------------ data
STATS = [
    ("31%", "Nvidia shares jump on Huang's return"),
    ("153", "Russian drones fired overnight at Ukraine"),
    ("7", "sea drones sink Russian corvette off Libya"),
    ("24", "killed in Indonesia factory fire"),
    ("$61,327", "Bitcoin closes Monday"),
    ("4-0", "Liverpool beat Man Utd"),
]

REGIONS = [
    ("EUROPE", 8, (30, 80, 160)), ("MIDDLE EAST", 4, (150, 60, 60)),
    ("AMERICAS", 6, (180, 140, 40)), ("ASIA-PACIFIC", 10, (40, 130, 80)),
    ("AFRICA", 4, (160, 120, 50)), ("OCEANIA", 1, (60, 140, 140)),
    ("WORLD", 2, (110, 110, 110)),
]

HEROES = [
    dict(banner="HUANG IS BACK", art=icon_chip,
         loc="1 SAN FRANCISCO · TECHNOLOGY",
         head="Nvidia brings back Huang as its chief",
         sub="Board reinstates the co-founder 11 days after he quit; Trump "
             "pressed for his return and shares soar 31%. (Reuters, WSJ)"),
    dict(banner="WARSHIP SUNK", art=icon_ship,
         loc="2 BENGHAZI, LIBYA · WAR",
         head="Ukraine sinks Russian warship off Libya",
         sub="Seven sea drones hit the corvette Merkury in port; a Ka-27 "
             "helicopter is destroyed and the cargo ship Angara is hit. (CNN, WSJ)"),
    dict(banner="153 DRONES", art=icon_drones,
         loc="3 KYIV, UKRAINE · WAR",
         head="Russia fires 153 drones; Dymer toll hits 11",
         sub="Defences down 134, but strikes land at 11 sites; rescuers pull 11 "
             "dead from a ruined block in Dymer. (Air Force, Reuters)"),
]

SMALLS = [
    dict(banner="COP31 FALLOUT", art=icon_globe, loc="4 ANTALYA · CLIMATE",
         head="UN chief calls the collapse 'deeply disappointing'",
         sub="First COP failure since 2009; focus shifts to COP32 in Ethiopia. (UN, CNN)"),
    dict(banner="BITCOIN $61,327", art=icon_btc, loc="5 WORLD · MARKETS",
         head="Bitcoin holds $61,000 as Wall Street rallies",
         sub="Up from a $55,130 two-year low; Nasdaq jumps 6.5% as ETFs bleed $1.8bn."),
    dict(banner="FIRE TOLL 24", art=icon_fire, loc="6 CIKANDE · DISASTER",
         head="Indonesia factory fire toll rises to 24",
         sub="Sweets-plant blaze kills 24; about 30 still missing as rescuers search. (Reuters)"),
    dict(banner="REDS 4-0", art=icon_ball, loc="7 LIVERPOOL · FOOTBALL",
         head="Liverpool thrash Man Utd 4-0",
         sub="Yoro sent off in 8 minutes on Pochettino's debut; Wirtz scores and sets one up."),
    dict(banner="TEST DRAW", art=icon_cricket, loc="8 WELLINGTON · CRICKET",
         head="India-NZ Test ends in a draw",
         sub="NZ finish 238/5 after India declare in a record 720/9; Pant 128, Rahul 136."),
    dict(banner="SANCTIONS 22", art=icon_eu, loc="9 BRUSSELS · DIPLOMACY",
         head="EU proposes 22nd Russia sanctions package",
         sub="Banks, crypto and sport targeted; von der Leyen unveils the plan. (Reports)"),
    dict(banner="IRAN SANCTIONS", art=icon_doc, loc="10 WASHINGTON · DIPLOMACY",
         head="US sanctions 20+ Iranian shadow-banking entities",
         sub="Treasury targets networks it links to Iran's shadow banking. (Treasury)"),
    dict(banner="MERCURY: SAFE", art=icon_planet, loc="11 DARMSTADT · SPACE",
         head="BepiColombo safe and on track, ESA says",
         sub="Eight-year trip ends in Mercury orbit; a software glitch cut the burn short. (ESA)"),
    dict(banner="UN STAFFER KILLED", art=icon_cross, loc="12 GAZA · WAR",
         head="UN staffer killed in Israeli strike on Gaza",
         sub="One killed, three hurt in the attack, the UN agency says. (Reports)"),
    dict(banner="DRONES HIT UN SITE", art=icon_drone2, loc="13 KHARTOUM · WAR",
         head="Drones hit homes and UN building in Khartoum",
         sub="Residential areas and a UN building struck in Sudan's capital. (Reports)"),
]

ALSO_LEFT = [
    (14, "Europe: Finland backs anti-tank barriers"),
    (15, "Europe: London police seize 893kg cocaine"),
    (16, "Middle East: Eisenkot condemns settler arson"),
    (17, "Middle East: Houthis attack Taiz, 2 killed"),
    (18, "Middle East: US targets Iranian proxy networks"),
    (19, "Americas: Gomez to resign from Congress"),
    (20, "Americas: Carney shares stage with Trump double"),
    (21, "Americas: US Army to detonate toxic lead in Iowa"),
    (22, "Americas: Cucuta drone attack injures 3"),
    (23, "Asia-Pacific: India gives $1.62bn to Nepal"),
    (24, "Asia-Pacific: Korea minister quits over cheating"),
]
ALSO_RIGHT = [
    (25, "Asia-Pacific: Thai court halves royal-insult term"),
    (26, "Asia-Pacific: Prabowo to name VP candidates"),
    (27, "Asia-Pacific: Asian tech shares fall further"),
    (28, "Asia-Pacific: SK hynix shares rise 20%"),
    (29, "Asia-Pacific: China agrees AI talks mechanism"),
    (30, "Asia-Pacific: Bangladesh to arrest Hasina"),
    (31, "Asia-Pacific: US to blacklist Megaspeed"),
    (32, "Africa: Nigeria boat rescue under way"),
    (33, "Africa: Libya parliament moves to unify"),
    (34, "Europe: Yamal ruled out of Barcelona trip"),
    (35, "World: UN chief urges AI safety framework"),
]

DATE_CHECK = ("Left out as earlier news: the 186-drone raid on Ukraine "
              "(Sat 22 Nov); COP31's collapse itself (Sun 22 Nov — Monday "
              "brought the reactions); the Riemann proof (announced Fri 20 Nov); "
              "BepiColombo's Mercury arrival (Sat 21 Nov); the Cikande fire's "
              "first report (22 Nov); Peru's 6.7 quake (Fri 21 Nov).")


# ------------------------------------------------------------------ build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top bar: 11 px of clear paper above the text, exactly as 21 Nov
    f_top = font(SANS_B, 11)
    d.text((12, 11), "THE WORLD IN ONE DAY", font=f_top, fill=RED)
    right = "35 STORIES · 7 REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
    d.text((W - 12 - d.textlength(right, font=f_top), 11), right,
           font=f_top, fill=RED)

    # --- masthead
    f_mast = font(SERIF_B, 58)
    d.text((12, 24), "Monday 23 November 2026", font=f_mast, fill=INK)

    # --- subline (red italic)
    f_sub = font(SERIF_I, 14)
    sub = ("Nvidia brings back its chief · Ukraine sinks a warship off Libya "
           "· Russia fires 153 drones at Kyiv")
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, 90), sub,
           font=f_sub, fill=RED)

    # --- stat strip: six boxes, y 106..150
    f_num = font(SERIF_B, 22)
    f_cap = font(SANS, 8)
    x = 12
    bw = (W - 24 - 5 * 4) // 6
    for num, cap in STATS:
        d.rectangle([x, 106, x + bw, 150], outline=RED, width=1)
        d.text((x + 6, 110), num, font=f_num, fill=INK)
        lines = wrap(d, cap, f_cap, bw - 12)
        draw_lines(d, x + 6, 136, lines[:2], f_cap, GREY, 10)
        x += bw + 4

    # --- region bar: seven segments, y 156..171
    total = sum(n for _, n, _ in REGIONS)
    x = 12
    f_reg = font(SANS_B, 9)
    for name, n, col in REGIONS:
        seg = max(58, int((W - 24) * n / total))
        if x + seg > W - 12:
            seg = W - 12 - x
        d.rectangle([x, 156, x + seg, 171], fill=col)
        label = f"{name} {n}"
        tw = d.textlength(label, font=f_reg)
        d.text((x + (seg - tw) / 2, 159), label, font=f_reg,
               fill=(255, 255, 255))
        x += seg

    # --- heroes: banner y 176..200, art 200..265, loc 268, head 282, sub 328
    col_w = (W - 24 - 2 * 8) // 3
    f_ban = font(SANS_B, 13)
    f_loc = font(SANS_B, 10)
    f_head = font(SERIF_B, 20)
    f_hsub = font(SANS, 11)
    for i, hero in enumerate(HEROES):
        x = 12 + i * (col_w + 8)
        d.rectangle([x, 176, x + col_w, 200], fill=RED)
        d.text((x + 8, 181), hero["banner"], font=f_ban,
               fill=(255, 255, 255))
        hero["art"](d, x, 200, col_w, 65)
        d.text((x, 268), hero["loc"], font=f_loc, fill=RED)
        lines = wrap(d, hero["head"], f_head, col_w)
        draw_lines(d, x, 282, lines[:2], f_head, INK, 22)
        lines = wrap(d, hero["sub"], f_hsub, col_w)
        draw_lines(d, x, 328, lines[:2], f_hsub, INK, 13)

    # --- small leads: two rows of five
    # row 1: banner 358..378, art 378..438, loc 441, head 455, sub 480
    # row 2: banner 506..526, art 526..586, loc 589, head 603, sub 628
    sm_w = (W - 24 - 4 * 6) // 5
    f_sban = font(SANS_B, 11)
    f_sloc = font(SANS_B, 9)
    f_shead = font(SERIF_B, 13)
    f_ssub = font(SANS, 10)
    for row in range(2):
        base = 358 if row == 0 else 506
        for j in range(5):
            s = SMALLS[row * 5 + j]
            x = 12 + j * (sm_w + 6)
            d.rectangle([x, base, x + sm_w, base + 20], fill=RED)
            d.text((x + 6, base + 4), s["banner"], font=f_sban,
                   fill=(255, 255, 255))
            s["art"](d, x, base + 20, sm_w, 60)
            d.text((x, base + 83), s["loc"], font=f_sloc, fill=RED)
            lines = wrap(d, s["head"], f_shead, sm_w)
            draw_lines(d, x, base + 97, lines[:2], f_shead, INK, 14)
            lines = wrap(d, s["sub"], f_ssub, sm_w)
            draw_lines(d, x, base + 122, lines[:2], f_ssub, INK, 12)

    # --- bottom block titles, y 654..668
    f_sec = font(SANS_B, 11)
    d.text((12, 654), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    also_title = "ALSO ON MONDAY 23 NOVEMBER — 22 MORE STORIES"
    d.text((420, 654), also_title, font=f_sec, fill=INK)
    f_cap2 = font(SANS, 9)
    d.text((12, 668), "pins match story numbers", font=f_cap2, fill=GREY)

    # --- map: x 12..412, y 680..900 (dark navy dot-grid, 220 px tall)
    draw_map(d, 12, 680, 400, 220)
    f_cap3 = font(SANS_I, 9)
    d.text((12, 902),
           "Each number is the story with that number on this page.",
           font=f_cap3, fill=GREY)

    # --- ALSO: two columns, x 420..1012, y 680..900, 11 rows each
    f_also = font(SANS, 10)
    f_alnum = font(SANS_B, 10)
    for col, items in ((420, ALSO_LEFT), (724, ALSO_RIGHT)):
        y = 680
        for num, text in items:
            d.text((col, y), str(num), font=f_alnum, fill=RED)
            d.text((col + 24, y), text, font=f_also, fill=INK)
            y += 20

    # --- DATE CHECK box: top edge y 930, bottom edge y 975 (as 21 Nov)
    d.rectangle([12, 930, 1012, 975], outline=RED, width=2)
    f_dc = font(SANS_B, 10)
    f_dct = font(SANS, 10)
    d.text((20, 938), "DATE CHECK", font=f_dc, fill=RED)
    lines = wrap(d, DATE_CHECK, f_dct, 1012 - 20 - 110)
    draw_lines(d, 20 + 110, 938, lines[:3], f_dct, INK, 12)

    # --- sources: ONE line, y 996..1004, 19 px of clear paper below it
    f_src = font(SANS, 9)
    left = ("Every story here happened, or was first reported, on Monday 23 "
            "November 2026. Sources: Reuters, AP, BBC, CNN, WSJ, ESA, UN, "
            "Treasury, CoinGecko.")
    right = "Pictures: original, drawn in code."
    d.text((12, 996), left, font=f_src, fill=(60, 60, 60))
    d.text((W - 12 - d.textlength(right, font=f_src), 996), right,
           font=f_src, fill=(60, 60, 60))

    img.save(OUT)
    print(f"wrote {OUT}")
    return OUT


if __name__ == "__main__":
    build()
