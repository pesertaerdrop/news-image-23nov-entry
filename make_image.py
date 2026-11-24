"""Build the 23 November 2026 front page: one image, 1024x1024.

Layout follows the 21 November model (user: make it exactly like
that one): top bar, big masthead, red italic subline, six-box stat
strip, seven-segment region bar, three heroes, ten small leads, a
dark navy dot-grid world map with numbered pins beside a 22-item
ALSO list, a red DATE CHECK box, and a one-line sources line.

This session's fix: the red subline used to be drawn on top of the
masthead's descenders. The masthead is now set smaller (auto-fit
from size 56) so its lowest letter ends near y=97, the subline sits
at y=98 with clear cream above and below it, and every section
under it moves down 15px. DATE CHECK and the sources line do not
move, so the bottom margin stays the same.

Every text that is wrapped carries a hard check: if it needs more
lines than its box allows, or runs wider than its box, the build
fails with a clear OVERFLOW message instead of clipping silently.
"""
from __future__ import annotations

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
CREAM = (250, 246, 235)
INK = (0, 0, 0)
RED = (178, 34, 34)
NAVY = (18, 28, 55)
DOTTAN = (198, 170, 120)
WHITE = (255, 255, 255)
GREY = (117, 117, 117)

# ---------------------------------------------------------------- fonts
DEJAVU = "/usr/share/fonts/truetype/dejavu"
SERIF = DEJAVU + "/DejaVuSerif.ttf"
SERIF_BOLD = DEJAVU + "/DejaVuSerif-Bold.ttf"
SANS = DEJAVU + "/DejaVuSans.ttf"
SANS_BOLD = DEJAVU + "/DejaVuSans-Bold.ttf"


def load(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- geometry
PAGE = 1024
MX = 12                      # left margin
RX = 1012                    # right edge (content ends here)
CW = RX - MX                 # content width = 1000

TOPBAR_Y = 14
MASTHEAD_Y = 32
MASTHEAD_START = 56
SUBLINE_Y = 98
STAT_Y0, STAT_Y1 = 120, 166
REGION_Y0, REGION_Y1 = 171, 186
DATE_Y0, DATE_Y1 = 930, 975
SOURCES_Y = 996

HERO_COLS = [(12, 340), (348, 676), (684, 1012)]
HERO_TITLE_Y0, HERO_TITLE_Y1 = 191, 214
HERO_ART_Y0, HERO_ART_Y1 = 215, 280
HERO_KICK_Y = 285
HERO_HEAD_Y = 299
HERO_SUB_Y = 345

# five small columns across the 1000px content width, 8px gutters
def small_cols():
    widths = [194, 194, 194, 193, 193]
    cols = []
    x = MX
    for w in widths:
        cols.append((x, x + w))
        x += w + 8
    return cols

SMALL_COLS = small_cols()
SMALL_ROWS = [
    # (title y0, title y1, art y0, art y1, kicker y, head y, sub y)
    (373, 392, 393, 453, 457, 470, 501),
    (521, 540, 541, 601, 605, 618, 649),
]

MAP_X0, MAP_X1 = 12, 412
MAP_Y0, MAP_Y1 = 695, 915
MAP_HEAD_Y = 673
MAP_CAP_Y = 920
ALSO_HEAD_Y = 673
ALSO_Y0 = 695
ALSO_PITCH = 20
ALSO_COLS = [(420, 280), (712, 298)]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


# ---------------------------------------------------------------- helpers
def wrap_lines(draw: ImageDraw.ImageDraw, text: str,
               font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Wrap text to max_w, one word at a time."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
        max_w: int, max_lines: int, what: str) -> list[str]:
    """Wrap text; FAIL loudly if it needs too many lines or one line
    is still too wide (a single long word). Never clip silently."""
    lines = wrap_lines(draw, text, font, max_w)
    if len(lines) > max_lines:
        raise AssertionError(
            "OVERFLOW %s: needs %d lines (max %d): %r"
            % (what, len(lines), max_lines, text))
    for ln in lines:
        if draw.textlength(ln, font=font) > max_w:
            raise AssertionError(
                "OVERFLOW %s: line too wide: %r" % (what, ln))
    return lines


def draw_lines(draw: ImageDraw.ImageDraw, lines: list[str], x: int, y: int,
               font: ImageFont.FreeTypeFont, fill, pitch: int) -> None:
    for i, ln in enumerate(lines):
        draw.text((x, y + i * pitch), ln, font=font, fill=fill)


def text_w(draw: ImageDraw.ImageDraw, text: str,
           font: ImageFont.FreeTypeFont) -> float:
    return draw.textlength(text, font=font)


def fit_size(text: str, path: str, start: int, max_w: int) -> int:
    """Largest font size (<= start) whose text fits max_w."""
    size = start
    while size > 8:
        f = load(path, size)
        if f.getlength(text) <= max_w:
            return size
        size -= 1
    return size


def italic_layer(text: str, font: ImageFont.FreeTypeFont, fill,
                 shear: float = 0.22) -> Image.Image:
    """Render text on its own layer, then shear it so it reads as
    italic. DejaVu Serif ships no italic face, so the slant is done
    geometrically; the layer is as tall as the font's bounding box."""
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + 4
    h = bbox[3] - bbox[1] + 4
    pad = int(h * shear) + 4
    layer = Image.new("RGBA", (w + pad, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((2 - bbox[0], 2 - bbox[1]), text, font=font, fill=fill)
    # shear: x' = x + shear * (bottom - y)
    layer = layer.transform(
        layer.size, Image.AFFINE,
        (1, -shear, shear * (h - 2), 0, 1, 0),
        resample=Image.BICUBIC)
    return layer


def region_widths(counts: list[int], total_w: int, minimum: int) -> list[int]:
    """Segment widths: every segment gets at least `minimum` px; the
    shortfall is taken proportionally from the segments above it, so
    the widths always add up to total_w."""
    total = sum(counts)
    raw = [c / total * total_w for c in counts]
    widths = [max(r, minimum) for r in raw]
    over = sum(widths) - total_w
    if over > 0:
        flex = [i for i, w in enumerate(widths) if w > minimum]
        flex_total = sum(counts[i] for i in flex)
        for i in flex:
            widths[i] -= over * counts[i] / flex_total
    widths = [int(round(w)) for w in widths]
    widths[-1] += total_w - sum(widths)
    return widths

# ---------------------------------------------------------------- data
# World map: dot grid. Columns are longitude -168..192 step 4 (91),
# rows are latitude 84..-56 step 4 (36). '1' = land (draw a dot),
# '.' = ocean. The pattern was measured from the 21 Nov model's map
# so the continents fall in the right places; pins sit on it.
LAND = [
    "..........................111111111111.....................................................",
    "..........................111111111111.....................................................",
    ".........................1111111111111...............11111111111111111111111111111111111...",
    "11111111111111111111111111111111111111..............111111111111111111111111111111111111...",
    "11111111111111111111111111111111111111..111111111111111111111111111111111111111111111111...",
    "11111111111111111111111111111111111111..111111111111111111111111111111111111111111111111...",
    "11111111111111111111111111111111111111..111111111111111111111111111111111111111111111111...",
    "1111111111111111111111111111111.........111111111111111111111111111111111111111111111111...",
    "111111111111111111111111111111..........111111111111111111111111111111111111111111111111...",
    "111111111111111111111111111111..........111111111111111111111111111111111111111111111111...",
    "111111111111111111111111111111..........111111111111111111111111111111111111111111111111...",
    "111111111111111111111111111111.........11111111111111111111111111111111111111111...........",
    "111111111111111111111111111111........11111111111111111111111111111111111111111............",
    "111111111111111111111111111111........11111111111111111111111111111111111111111............",
    "111111111111111111111111111111........1111111111111111111111111111111111111111.............",
    "111111111111111111111111111111........1111111111111111111111111111111111111111.............",
    "111111111111111111111111111111........1111111111111111111111111111111111111111.............",
    "1111111111111111111111111111111.......1111111111111111111111111111111111111111.............",
    "..............11111111111111111111....1111111111111111111111111111111111111111.............",
    "...............1111111111111111111....1111111111111111111111111111111111111111.............",
    ".....................1111111111111....1111111111111111111.......11111111111111.............",
    "......................111111111111....111111111111111111.........1111111111111.............",
    "......................111111111111....111111111111111111.........1111111111111.............",
    "......................111111111111....111111111111111111.........11111111111111............",
    "......................111111111111....111111111111111111.............111111111111..........",
    "......................111111111111....111111111111111111.............111111111111..........",
    "......................111111111111....111111111111111111.............111111111111..........",
    "......................111111111111....111111111111111111.............111111111111..........",
    "......................111111111111....111111111111111111.............111111111111..........",
    "......................111111111111....111111111111111111.............111111111111..........",
    "......................111111111111....111111111111111111.............111111111111..1111....",
    "......................111111111111...................................111111111111..111.....",
    "......................111111111111.................................................111.....",
    "......................111111111111.........................................................",
    "......................111111111111.........................................................",
    "......................111111111111.........................................................",
]
LON0, LON1 = -168, 192
LAT0, LAT1 = 84, -56

# Pins: (number, display x, display y, true x or None, true y or None).
# Display spots are nudged where neighbours crowd; a thin leader
# joins the pin to its true spot. All y values already include the
# +15 shift for the lowered map.
PINS = [
    (1, 63, 766, None, None),
    (2, 219, 774, None, None),
    (3, 232, 746, None, None),
    (4, 218, 755, 232, 769),
    (5, 154, 777, None, None),
    (6, 316, 833, None, None),
    (7, 186, 731, 195, 742),
    (8, 393, 887, None, None),
    (9, 202, 745, None, None),
    (10, 105, 770, 112, 763),
    (11, 216, 734, 206, 746),
    (12, 247, 780, 235, 776),
    (13, 233, 800, None, None),
]

# Region bar: (label, count, colour), in bar order.
REGIONS = [
    ("EUROPE", 8, (30, 80, 160)),
    ("MIDDLE EAST", 4, (150, 60, 60)),
    ("AMERICAS", 6, (180, 140, 40)),
    ("ASIA-PACIFIC", 10, (40, 130, 80)),
    ("AFRICA", 4, (160, 120, 50)),
    ("OCEANIA", 1, (60, 140, 140)),
    ("WORLD", 2, (117, 117, 117)),
]

# Stat strip: (big number, one-line caption).
STATS = [
    ("31%", "Huang's return lifts Nvidia"),
    ("153", "Drones fired at Ukraine"),
    ("7", "Sea drones sink a corvette"),
    ("24", "killed in Indonesia factory fire"),
    ("$61,327", "Bitcoin closes Monday"),
    ("4-0", "Liverpool beat Man Utd"),
]

SUBLINE = ("Nvidia brings back its chief \u00b7 Ukraine sinks a warship "
           "off Libya \u00b7 Russia fires 153 drones at Kyiv")
MASTHEAD = "Monday 23 November 2026"

# Heroes: (title bar, art kind, kicker, headline, sub).
HEROES = [
    ("HUANG IS BACK", "nvda",
     "1 SAN FRANCISCO \u00b7 TECHNOLOGY",
     "Nvidia brings back Huang as its chief",
     "Board reinstates the co-founder 11 days after he quit; "
     "Trump pressed for his return and shares soar 31%."),
    ("WARSHIP SUNK", "ship",
     "2 BENGHAZI, LIBYA \u00b7 WAR",
     "Ukraine sinks Russian warship off Libya",
     "Seven sea drones hit the corvette Merkury in port; a Ka-27 "
     "destroyed, Angara hit."),
    ("153 DRONES", "drones",
     "3 KYIV, UKRAINE \u00b7 WAR",
     "Russia fires 153 drones; Dymer toll hits 11",
     "Defences down 134, but strikes hit 11 sites; 11 dead in a "
     "ruined block in Dymer. (Air Force, Reuters)"),
]

# Small leads: (title bar, art kind, kicker, headline, sub).
SMALLS = [
    ("COP31 FALLOUT", "globe",
     "4 ANTALYA \u00b7 CLIMATE",
     "UN chief calls collapse \u2018deeply disappointing\u2019",
     "First COP failure since 2009; focus shifts to COP32 in "
     "Ethiopia. (UN, CNN)"),
    ("BITCOIN $61,327", "btc",
     "5 WORLD \u00b7 MARKETS",
     "Bitcoin holds $61,000 as Wall Street rallies",
     "Up from $55,130 two-year low; Nasdaq jumps 6.5% as ETFs bleed."),
    ("FIRE TOLL 24", "flame",
     "6 CIKANDE \u00b7 DISASTER",
     "Indonesia factory fire toll rises to 24",
     "Sweets-plant blaze kills 24; about 30 still missing as "
     "rescuers search."),
    ("REDS 4-0", "score",
     "7 LIVERPOOL \u00b7 FOOTBALL",
     "Liverpool thrash Man Utd 4-0",
     "Yoro sent off in 8 minutes; Wirtz scores, sets one up."),
    ("TEST DRAW", "cricket",
     "8 WELLINGTON \u00b7 CRICKET",
     "India\u2013NZ Test ends in a draw",
     "NZ finish 238/5 after India declare in a record 720/9; "
     "Pant 128, Rahul 136."),
    ("SANCTIONS 22", "stars",
     "9 BRUSSELS \u00b7 DIPLOMACY",
     "EU proposes 22nd Russia sanctions",
     "Banks, crypto and sport targeted; von der Leyen unveils the "
     "plan. (The Brief)"),
    ("IRAN SANCTIONS", "docs",
     "10 WASHINGTON \u00b7 DIPLOMACY",
     "US sanctions 20+ Iran shadow banks",
     "Iran\u2019s shadow banking. (Treasury)"),
    ("MERCURY SAFE", "planet",
     "11 DARMSTADT \u00b7 SPACE",
     "BepiColombo safe and on track, ESA says",
     "Eight-year trip ends in Mercury orbit; a software glitch cut "
     "the burn short."),
    ("UN STAFFER KILLED", "cross",
     "12 GAZA \u00b7 WAR",
     "UN staffer killed in Israeli strike on Gaza",
     "One killed, three hurt in the attack, the UN agency says. "
     "(Reports)"),
    ("DRONES HIT UN SITE", "xmark",
     "13 KHARTOUM \u00b7 WAR",
     "Drones hit homes, UN building in Khartoum",
     "Residential areas and a UN building struck in Sudan\u2019s "
     "capital. (Reports)"),
]

# ALSO: (number, region, brief). One line each, two columns.
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

DATE_TEXT = ("Left out as earlier news: the 186-drone raid on Ukraine "
             "(Sat 22 Nov); COP31\u2019s collapse itself (Sun 22 Nov \u2014 "
             "Monday brought the reactions); the Riemann proof "
             "(announced Fri 20 Nov); BepiColombo\u2019s Mercury arrival "
             "(Sat 21 Nov); the Cikande fire\u2019s first report (22 Nov); "
             "Peru\u2019s 6.7 quake (Fri 21 Nov).")

SOURCES_LEFT = ("Every story here happened, or was first reported, on "
                "Monday 23 November 2026. Sources: Reuters, AP, BBC, CNN, "
                "WSJ, ESA, UN, Treasury, CoinGecko.")
SOURCES_RIGHT = "Pictures: original, drawn in code."

# ---------------------------------------------------------------- artwork
# Every picture is drawn from code, inside its own box. Vertical
# positions are fractions of the box height h, so nothing can spill
# past the box edge (the 22 Nov ship-icon crash: a y+62 rectangle
# in a 60px box).

def hero_art(draw: ImageDraw.ImageDraw, kind: str,
             x0: int, y0: int, x1: int, y1: int) -> None:
    w = x1 - x0
    h = y1 - y0
    cx = x0 + w // 2
    if kind == "nvda":
        draw.rectangle([x0, y0, x1, y1], fill=(18, 77, 43))
        draw.rectangle([x0, y0 + int(h * 0.30), x1, y0 + int(h * 0.34)],
                       fill=(52, 143, 90))
        bw, bh = int(w * 0.34), int(h * 0.42)
        bx0, by0 = cx - bw // 2, y0 + (h - bh) // 2
        draw.rectangle([bx0, by0, bx0 + bw, by0 + bh],
                       outline=WHITE, width=2)
        f = load(SANS_BOLD, 22)
        t = "NVDA"
        draw.text((cx - draw.textlength(t, font=f) / 2,
                   by0 + bh // 2 - 11), t, font=f, fill=WHITE)
    elif kind == "ship":
        draw.rectangle([x0, y0, x1, y0 + int(h * 0.45)], fill=(214, 226, 235))
        draw.rectangle([x0, y0 + int(h * 0.45), x1, y1], fill=(43, 96, 150))
        draw.rectangle([x0, y0 + int(h * 0.45), x1, y0 + int(h * 0.48)],
                       fill=(120, 170, 210))
        # hull
        hx0, hx1 = x0 + int(w * 0.08), x0 + int(w * 0.72)
        hy = y0 + int(h * 0.58)
        draw.polygon([(hx0, hy), (hx1, hy), (hx1 - 14, hy + int(h * 0.22)),
                      (hx0 + 10, hy + int(h * 0.22))], fill=(25, 25, 30))
        # superstructure + mast
        draw.rectangle([hx0 + int(w * 0.18), hy - int(h * 0.20),
                        hx0 + int(w * 0.34), hy], fill=(25, 25, 30))
        draw.line([hx0 + int(w * 0.26), hy - int(h * 0.20),
                   hx0 + int(w * 0.26), hy - int(h * 0.38)],
                  fill=(25, 25, 30), width=3)
        # explosion
        ex, ey = x0 + int(w * 0.84), y0 + int(h * 0.34)
        for r, col in ((16, (255, 170, 40)), (10, (255, 210, 90)),
                       (5, (255, 240, 180))):
            draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)
        # drone
        dx, dy = x0 + int(w * 0.56), y0 + int(h * 0.18)
        draw.ellipse([dx - 12, dy - 3, dx + 12, dy + 3], fill=(25, 25, 30))
        draw.line([dx - 16, dy - 5, dx + 16, dy - 5], fill=(25, 25, 30),
                  width=2)
    else:  # drones
        draw.rectangle([x0, y0, x1, y1], fill=(16, 18, 38))
        draw.ellipse([x0 + int(w * 0.78), y0 + int(h * 0.12),
                      x0 + int(w * 0.98), y0 + int(h * 0.42)],
                     fill=(255, 170, 40))
        for i, (fx, fy) in enumerate(((0.16, 0.30), (0.42, 0.52),
                                      (0.62, 0.28))):
            dx = x0 + int(w * fx)
            dy = y0 + int(h * fy)
            for k in range(3):
                yy = dy + k * 7
                draw.line([dx, yy, dx + 26, yy], fill=(255, 205, 60),
                          width=4)
            draw.line([dx + 13, dy - 6, dx + 13, dy + 20],
                      fill=(255, 205, 60), width=2)


def small_art(draw: ImageDraw.ImageDraw, kind: str,
              x0: int, y0: int, x1: int, y1: int) -> None:
    w = x1 - x0
    h = y1 - y0
    cx = x0 + w // 2
    cy = y0 + h // 2
    if kind == "globe":
        draw.rectangle([x0, y0, x1, y1], fill=(210, 235, 220))
        draw.ellipse([x0 + int(w * 0.08), y0 + int(h * 0.12),
                      x0 + int(w * 0.48), y0 + int(h * 0.88)],
                     fill=(52, 130, 190))
        draw.ellipse([x0 + int(w * 0.20), y0 + int(h * 0.30),
                      x0 + int(w * 0.38), y0 + int(h * 0.58)],
                     fill=(90, 180, 110))
        # thermometer
        tx = x0 + int(w * 0.68)
        draw.rectangle([tx - 3, y0 + int(h * 0.15), tx + 3,
                        y0 + int(h * 0.85)], fill=(178, 34, 34))
        draw.ellipse([tx - 8, y0 + int(h * 0.68), tx + 8,
                      y0 + int(h * 0.92)], fill=(178, 34, 34))
        draw.rectangle([x0 + int(w * 0.58), y0 + int(h * 0.15),
                        x0 + int(w * 0.60), y0 + int(h * 0.85)],
                       fill=(120, 120, 120))
    elif kind == "btc":
        draw.rectangle([x0, y0, x1, y1], fill=(12, 12, 14))
        f = load(SANS_BOLD, 20)
        draw.text((x0 + 8, y0 + int(h * 0.10)), "BTC", font=f,
                  fill=(247, 183, 40))
        f2 = load(SANS_BOLD, 12)
        draw.text((x1 - 38, y0 + int(h * 0.12)), "-9%", font=f2,
                  fill=WHITE)
        bars = [(0.30, 22, (60, 180, 110)), (0.45, 34, (220, 70, 60)),
                (0.60, 14, (60, 180, 110)), (0.75, 28, (220, 70, 60))]
        base = y0 + int(h * 0.92)
        for fx, bh, col in bars:
            bx = x0 + int(w * fx)
            draw.rectangle([bx, base - bh, bx + 16, base], fill=col)
    elif kind == "flame":
        draw.rectangle([x0, y0, x1, y1], fill=(24, 16, 12))
        draw.polygon([(x0 + int(w * 0.10), y1 - 4),
                      (cx, y0 + int(h * 0.08)),
                      (x1 - int(w * 0.10), y1 - 4)],
                     fill=(230, 120, 30))
        draw.polygon([(x0 + int(w * 0.30), y1 - 4),
                      (cx, y0 + int(h * 0.38)),
                      (x1 - int(w * 0.30), y1 - 4)],
                     fill=(250, 200, 60))
    elif kind == "score":
        draw.rectangle([x0, y0, x1, y1], fill=(30, 140, 70))
        draw.ellipse([cx - 34, cy - 20, cx + 34, cy + 20], fill=WHITE)
        draw.polygon([(cx, cy - 14), (cx + 10, cy + 2), (cx + 3, cy + 2),
                      (cx + 3, cy + 14), (cx - 3, cy + 14), (cx - 3, cy + 2),
                      (cx - 10, cy + 2)], fill=INK)
        f = load(SANS_BOLD, 20)
        t = "4-0"
        draw.text((x1 - draw.textlength(t, font=f) - 10,
                   cy - 11), t, font=f, fill=WHITE)
    elif kind == "cricket":
        draw.rectangle([x0, y0, x1, y1], fill=(90, 170, 90))
        draw.rectangle([x0 + int(w * 0.42), y0 + int(h * 0.18),
                        x0 + int(w * 0.58), y0 + int(h * 0.82)],
                       fill=(222, 196, 150))
        draw.ellipse([x0 + int(w * 0.68), y0 + int(h * 0.62),
                      x0 + int(w * 0.82), y0 + int(h * 0.86)],
                     fill=(178, 34, 34))
        f = load(SANS_BOLD, 18)
        draw.text((x0 + 8, y0 + int(h * 0.10)), "720/9", font=f, fill=WHITE)
    elif kind == "stars":
        draw.rectangle([x0, y0, x1, y1], fill=(22, 38, 110))
        import math
        for k in range(12):
            a = 2 * math.pi * k / 12 - math.pi / 2
            sx = cx + int(30 * math.cos(a))
            sy = cy + int(30 * math.sin(a))
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2],
                         fill=(250, 210, 60))
        f = load(SANS_BOLD, 20)
        t = "22nd"
        draw.text((cx - draw.textlength(t, font=f) / 2, cy - 11), t,
                  font=f, fill=WHITE)
    elif kind == "docs":
        draw.rectangle([x0, y0, x1, y1], fill=(232, 230, 222))
        f = load(SANS_BOLD, 24)
        draw.text((x0 + 10, y0 + int(h * 0.28)), "US", font=f,
                  fill=(30, 80, 160))
        dx0 = x0 + int(w * 0.52)
        draw.rectangle([dx0, y0 + int(h * 0.14), x1 - 10,
                        y0 + int(h * 0.86)], fill=WHITE,
                       outline=(150, 150, 150))
        for i in range(4):
            yy = y0 + int(h * (0.28 + i * 0.16))
            draw.line([dx0 + 6, yy, x1 - 16, yy], fill=(150, 150, 150),
                      width=2)
    elif kind == "planet":
        draw.rectangle([x0, y0, x1, y1], fill=(10, 10, 16))
        draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26],
                     fill=(230, 140, 50))
        draw.ellipse([cx - 40, cy - 12, cx + 40, cy + 12],
                     outline=(140, 140, 140), width=2)
        f = load(SANS_BOLD, 15)
        t = "8 yrs"
        draw.text((x1 - draw.textlength(t, font=f) - 8,
                   y1 - int(h * 0.30)), t, font=f, fill=WHITE)
    elif kind == "cross":
        draw.rectangle([x0, y0, x1, y1], fill=(18, 20, 40))
        f = load(SANS_BOLD, 26)
        draw.text((x0 + 10, cy - 15), "UN", font=f, fill=WHITE)
        px = x1 - int(w * 0.28)
        draw.line([px - 12, cy - 12, px + 12, cy + 12], fill=RED, width=5)
        draw.line([px - 12, cy + 12, px + 12, cy - 12], fill=RED, width=5)
    else:  # xmark
        draw.rectangle([x0, y0, x1, y1], fill=(16, 16, 28))
        f = load(SANS_BOLD, 26)
        draw.text((x0 + 10, cy - 15), "UN", font=f, fill=WHITE)
        px = x1 - int(w * 0.30)
        for dy in (-10, 10):
            draw.line([px - 14, cy + dy - 8, px + 14, cy + dy + 8],
                      fill=RED, width=4)
            draw.line([px - 14, cy + dy + 8, px + 14, cy + dy - 8],
                      fill=RED, width=4)

# ---------------------------------------------------------------- build
def build() -> Image.Image:
    img = Image.new("RGB", (PAGE, PAGE), CREAM)
    d = ImageDraw.Draw(img)

    # ---- top bar
    f_top = load(SANS_BOLD, 13)
    left = "THE WORLD IN ONE DAY"
    right = ("35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED "
             "MONDAY 23 NOVEMBER 2026")
    if text_w(d, left, f_top) + text_w(d, right, f_top) > CW - 20:
        raise AssertionError("OVERFLOW top bar")
    d.text((MX, TOPBAR_Y), left, font=f_top, fill=RED)
    d.text((RX - text_w(d, right, f_top), TOPBAR_Y), right, font=f_top,
           fill=RED)

    # ---- masthead (smaller this session, centred so the narrower
    # title still sits balanced; its lowest letter ends near y=97)
    size = fit_size(MASTHEAD, SERIF_BOLD, MASTHEAD_START, CW)
    f_mast = load(SERIF_BOLD, size)
    mw = f_mast.getlength(MASTHEAD)
    d.text(((PAGE - mw) / 2, MASTHEAD_Y), MASTHEAD, font=f_mast, fill=INK)

    # ---- subline: red italic, clearly BELOW the masthead now
    f_sub = load(SERIF, 17)
    layer = italic_layer(SUBLINE, f_sub, RED)
    if layer.width > CW:
        raise AssertionError("OVERFLOW subline too wide")
    img.paste(layer, (MX, SUBLINE_Y), layer)

    # ---- stat strip
    f_num = load(SANS_BOLD, 30)
    f_cap = load(SANS, 10)
    edges = [12, 175, 342, 509, 676, 843, 1010]
    for i, (num, cap) in enumerate(STATS):
        x0, x1 = edges[i], edges[i + 1]
        d.rectangle([x0, STAT_Y0, x1, STAT_Y1], outline=RED, width=2)
        nw = text_w(d, num, f_num)
        d.text((x0 + (x1 - x0 - nw) / 2, STAT_Y0 + 4), num, font=f_num,
               fill=RED)
        fit(d, cap, f_cap, (x1 - x0) - 10, 1, "stat caption %s" % num)
        cw = text_w(d, cap, f_cap)
        d.text((x0 + (x1 - x0 - cw) / 2, STAT_Y1 - 13), cap, font=f_cap,
               fill=INK)

    # ---- region bar
    counts = [c for _, c, _ in REGIONS]
    widths = region_widths(counts, CW, 80)
    f_reg = load(SANS_BOLD, 11)
    x = MX
    for (label, count, col), w in zip(REGIONS, widths):
        d.rectangle([x, REGION_Y0, x + w, REGION_Y1], fill=col)
        text = "%s %d" % (label, count)
        if text_w(d, text, f_reg) > w - 4:
            raise AssertionError("OVERFLOW region label %s" % text)
        tw = text_w(d, text, f_reg)
        d.text((x + (w - tw) / 2, REGION_Y0 + 2), text, font=f_reg,
               fill=WHITE)
        x += w

    # ---- heroes
    f_htitle = load(SANS_BOLD, 16)
    f_kick = load(SANS_BOLD, 11)
    f_hhead = load(SERIF_BOLD, 20)
    f_hsub = load(SERIF, 11)
    for (title, kind, kicker, head, sub), (x0, x1) in zip(HEROES,
                                                          HERO_COLS):
        d.rectangle([x0, HERO_TITLE_Y0, x1, HERO_TITLE_Y1], fill=RED)
        if text_w(d, title, f_htitle) > (x1 - x0) - 16:
            raise AssertionError("OVERFLOW hero title %s" % title)
        d.text((x0 + 8, HERO_TITLE_Y0 + 4), title, font=f_htitle,
               fill=WHITE)
        hero_art(d, kind, x0, HERO_ART_Y0, x1, HERO_ART_Y1)
        if text_w(d, kicker, f_kick) > (x1 - x0):
            raise AssertionError("OVERFLOW hero kicker %s" % kicker)
        d.text((x0, HERO_KICK_Y), kicker, font=f_kick, fill=RED)
        lines = fit(d, head, f_hhead, x1 - x0, 2, "hero head")
        draw_lines(d, lines, x0, HERO_HEAD_Y, f_hhead, INK, 22)
        lines = fit(d, sub, f_hsub, x1 - x0, 2, "hero sub")
        draw_lines(d, lines, x0, HERO_SUB_Y, f_hsub, INK, 14)

    # ---- small leads, two rows of five
    f_stitle = load(SANS_BOLD, 13)
    f_skick = load(SANS_BOLD, 10)
    f_shead = load(SERIF_BOLD, 15)
    f_ssub = load(SERIF, 9)
    for row, (ty0, ty1, ay0, ay1, ky, hy, sy) in enumerate(SMALL_ROWS):
        for col in range(5):
            idx = row * 5 + col
            title, kind, kicker, head, sub = SMALLS[idx]
            x0, x1 = SMALL_COLS[col]
            d.rectangle([x0, ty0, x1, ty1], fill=RED)
            if text_w(d, title, f_stitle) > (x1 - x0) - 12:
                raise AssertionError("OVERFLOW small title %s" % title)
            d.text((x0 + 6, ty0 + 3), title, font=f_stitle, fill=WHITE)
            small_art(d, kind, x0, ay0, x1, ay1)
            if text_w(d, kicker, f_skick) > (x1 - x0):
                raise AssertionError("OVERFLOW small kicker %s" % kicker)
            d.text((x0, ky), kicker, font=f_skick, fill=RED)
            lines = fit(d, head, f_shead, x1 - x0, 2, "small head %d" % (idx + 1))
            draw_lines(d, lines, x0, hy, f_shead, INK, 16)
            lines = fit(d, sub, f_ssub, x1 - x0, 2, "small sub %d" % (idx + 1))
            draw_lines(d, lines, x0, sy, f_ssub, INK, 10)

    # ---- map (drawn on its own layer so edge dots clip cleanly)
    f_maphead = load(SANS_BOLD, 13)
    d.text((MX, MAP_HEAD_Y), "WHERE IT HAPPENED", font=f_maphead, fill=INK)
    map_w, map_h = MAP_X1 - MAP_X0, MAP_Y1 - MAP_Y0
    layer = Image.new("RGB", (map_w, map_h), NAVY)
    md = ImageDraw.Draw(layer)
    n_lat = len(LAND)
    n_lon = len(LAND[0])
    for i, row in enumerate(LAND):
        lat = LAT0 - 4 * i
        y = (LAT0 - lat) / (LAT0 - LAT1) * map_h
        for j, ch in enumerate(row):
            if ch != "1":
                continue
            lon = LON0 + 4 * j
            x = (lon - LON0) / (LON1 - LON0) * map_w
            md.ellipse([x - 2, y - 2, x + 2, y + 2], fill=DOTTAN)
    f_pin = load(SANS_BOLD, 10)
    for num, px, py, tx, ty in PINS:
        rx, ry = px - MAP_X0, py - MAP_Y0
        if tx is not None:
            rtx, rty = tx - MAP_X0, ty - MAP_Y0
            md.line([rx, ry, rtx, rty], fill=(220, 220, 220), width=1)
            md.ellipse([rtx - 2, rty - 2, rtx + 2, rty + 2],
                       fill=WHITE)
        md.ellipse([rx - 7, ry - 7, rx + 7, ry + 7], fill=RED,
                   outline=WHITE, width=1)
        t = str(num)
        tw = md.textlength(t, font=f_pin)
        md.text((rx - tw / 2, ry - 6), t, font=f_pin, fill=WHITE)
    img.paste(layer, (MAP_X0, MAP_Y0))
    f_cap = load(SERIF, 11)
    cap = "Each number is the story with that number on this page."
    cap_layer = italic_layer(cap, f_cap, (90, 90, 90))
    if cap_layer.width > map_w:
        raise AssertionError("OVERFLOW map caption")
    img.paste(cap_layer, (MX, MAP_CAP_Y), cap_layer)

    # ---- ALSO list
    f_ahead = load(SANS_BOLD, 13)
    ahead = "ALSO ON MONDAY 23 NOVEMBER \u2014 22 MORE STORIES"
    if text_w(d, ahead, f_ahead) > RX - ALSO_COLS[0][0]:
        raise AssertionError("OVERFLOW also header")
    d.text((ALSO_COLS[0][0], ALSO_HEAD_Y), ahead, font=f_ahead, fill=INK)
    f_abold = load(SANS_BOLD, 11)
    f_areg = load(SANS, 11)
    for i, (num, region, brief) in enumerate(ALSO):
        col = 0 if i < 11 else 1
        cx, cwid = ALSO_COLS[col]
        y = ALSO_Y0 + (i % 11) * ALSO_PITCH
        n = str(num)
        d.text((cx, y), n, font=f_abold, fill=RED)
        x = cx + text_w(d, n, f_abold) + 4
        head_txt = "%s: " % region
        d.text((x, y), head_txt, font=f_abold, fill=INK)
        x += text_w(d, head_txt, f_abold)
        if x + text_w(d, brief, f_areg) > cx + cwid:
            raise AssertionError("OVERFLOW also %d" % num)
        d.text((x, y), brief, font=f_areg, fill=INK)

    # ---- DATE CHECK
    d.rectangle([MX, DATE_Y0, RX, DATE_Y1], outline=RED, width=2)
    f_dlabel = load(SANS_BOLD, 12)
    d.text((MX + 8, DATE_Y0 + 9), "DATE CHECK", font=f_dlabel, fill=RED)
    f_date = load(SANS, 11)
    label_w = text_w(d, "DATE CHECK", f_dlabel)
    tx = MX + 8 + label_w + 10
    lines = fit(d, DATE_TEXT, f_date, RX - tx - 8, 2, "date check")
    draw_lines(d, lines, int(tx), DATE_Y0 + 8, f_date, INK, 13)

    # ---- sources
    f_src = load(SANS, 10)
    lw = text_w(d, SOURCES_LEFT, f_src)
    rw = text_w(d, SOURCES_RIGHT, f_src)
    if lw > 800 or rw > 250 or (MX + lw) > (RX - rw - 10):
        raise AssertionError("OVERFLOW sources")
    d.text((MX, SOURCES_Y), SOURCES_LEFT, font=f_src, fill=INK)
    d.text((RX - rw, SOURCES_Y), SOURCES_RIGHT, font=f_src, fill=INK)

    return img


def main() -> None:
    img = build()
    if img.size != (1024, 1024) or img.mode != "RGB":
        raise AssertionError("bad canvas %s %s" % (img.size, img.mode))
    img.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
