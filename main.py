#!/usr/bin/env python3
"""News-image entry for make.fun competition news-image-20261123.

Draws a dense newspaper front page summing up Monday 23 November 2026
in pure-stdlib Python: own rasterizer, own 5x7 bitmap font, own PNG
encoder (struct + zlib). No network, no randomness, no timestamps:
two runs write byte-identical bytes.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (185, 28, 28)
DARKRED = (140, 20, 20)
GREY = (110, 105, 95)
LIGHT = (255, 253, 247)
BLUE = (43, 95, 138)
GREEN = (46, 125, 50)
GOLD = (201, 162, 39)
SLATE = (201, 212, 216)
SLATE_D = (140, 155, 162)
ORANGE = (214, 110, 30)
TEAL = (0, 128, 128)
CREAM = (238, 232, 214)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font: each glyph is 7 rows of 5 bits, written as strings.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    '·': ("00000", "00000", "00000", "00000", "01100", "01100", "00000"),
    '•': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    '¥': ("10001", "10001", "01010", "11111", "00100", "00100", "00100"),
    '°': ("01100", "10010", "10010", "01100", "00000", "00000", "00000"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
}
NORM = {'–': '-', '—': '-', '−': '-', '’': "'", '‘': "'", '“': '"', '”': '"',
        '…': '.', ' ': ' '}


def norm_char(ch):
    ch = NORM.get(ch, ch)
    return ch if ch in FONT else '?'


def char_adv(scale):
    return 5 * scale + max(1, scale // 2)


def text_w(s, scale):
    s = ''.join(norm_char(c) for c in s)
    if not s:
        return 0
    return len(s) * char_adv(scale) - max(1, scale // 2)


def wrap(text, max_w, scale):
    """Greedy word wrap; returns list of lines, each <= max_w px."""
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            rows = FONT[norm_char(ch)]
            for ry in range(7):
                row = rows[ry]
                for rx in range(5):
                    if row[rx] == '1':
                        self.fill_rect(cx + rx * scale, y + ry * scale,
                                       scale, scale, c)
            cx += char_adv(scale)
        return cx

    def text_c(self, cx, y, s, scale, c):
        self.text(cx - text_w(s, scale) // 2, y, s, scale, c)

    def para(self, x, y, max_w, s, scale, c, leading, max_lines=None):
        lines = wrap(s, max_w, scale)
        if max_lines is not None:
            lines = lines[:max_lines]
        for ln in lines:
            self.text(x, y, ln, scale, c)
            y += leading
        return y, len(lines)


# --------------------------------------------------------- illustrations --
def nato_star(cv, cx, cy, r, c):
    """8-point compass star."""
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r // 3
        pts.append((int(cx + rr * math.cos(ang)),
                    int(cy + rr * math.sin(ang))))
    cv.poly(pts, c)


def draw_poland(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (222, 232, 238))

    def P(fx, fy):
        return (x + int(fx * w), y + int(fy * h))
    poly = [P(0.10, 0.35), P(0.28, 0.12), P(0.55, 0.10), P(0.80, 0.18),
            P(0.92, 0.35), P(0.88, 0.62), P(0.72, 0.85), P(0.45, 0.88),
            P(0.22, 0.78), P(0.08, 0.60)]
    cv.poly(poly, (245, 240, 224))
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        cv.line(a[0], a[1], b[0], b[1], INK, 2)
    # 3 red missile tracks from the east
    for k, fy in enumerate((0.28, 0.50, 0.70)):
        sx, sy = x + w - 4, y + int(fy * h)
        ex, ey = x + int((0.55 - k * 0.10) * w), y + int((fy + 0.06) * h)
        cv.line(sx, sy, ex, ey, RED, 3)
        cv.circle(ex, ey, 4, RED)
        cv.text(ex + 6, ey - 12, "Kh-101", 1, RED)
    nato_star(cv, x + 34, y + 22, 16, BLUE)
    cv.text(x + 8, y + h - 16, "POLAND", 1, INK)
    cv.text(x + w - 62, y + h - 16, "BRUSSELS", 1, BLUE)


def draw_flags_train(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (226, 236, 226))
    # Nepal flag: crimson double pennon, label beside it
    nx, ny = x + 16, y + 8
    cv.poly([(nx, ny), (nx + 30, ny + 9), (nx, ny + 18)], (220, 20, 60))
    cv.poly([(nx, ny + 18), (nx + 26, ny + 25), (nx, ny + 32)], (220, 20, 60))
    cv.text(nx + 36, ny + 12, "NEPAL", 1, INK)
    # India flag: three stripes + chakra, label beside it
    ix, iy = x + 110, y + 8
    cv.fill_rect(ix, iy, 52, 11, (255, 153, 51))
    cv.fill_rect(ix, iy + 11, 52, 11, LIGHT)
    cv.fill_rect(ix, iy + 22, 52, 11, (19, 136, 8))
    cv.circle(ix + 26, iy + 16, 5, BLUE, fill=False)
    cv.text(ix + 58, iy + 12, "INDIA", 1, INK)
    # caption line, then the train along the bottom
    cv.text_c(x + w // 2, y + 42, "JANAKPUR DHAM - AYODHYA · WEEKLY TRAIN",
              1, RED)
    tx, ty = x + 10, y + h - 20
    cv.fill_rect(tx, ty, w - 20, 14, BLUE)
    cv.fill_rect(tx, ty, w - 20, 3, (30, 70, 110))
    for i in range(6):
        wx = tx + 8 + i * 22
        cv.fill_rect(wx, ty + 5, 14, 7, (200, 225, 240))
    for i in range(5):
        wx = tx + 14 + i * 26
        cv.circle(wx, ty + 17, 3, INK)
    cv.hline(x + 4, ty + 21, w - 8, INK, 1)


def draw_chart(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, LIGHT)
    for gy in range(1, 4):
        yy = y + gy * h // 4
        for gx in range(x + 8, x + w - 8, 6):
            cv.set(gx, yy, (200, 195, 185))
    vals = [0.85, 0.78, 0.70, 0.60, 0.52, 0.45, 0.38, 0.34, 0.40, 0.48,
            0.55, 0.62, 0.68, 0.74]
    n = len(vals)
    bw = (w - 24) // n
    for i, v in enumerate(vals):
        cx0 = x + 12 + i * bw
        top = y + h - 14 - int(v * (h - 28))
        bot = y + h - 14 - int(vals[i - 1] * (h - 28)) if i else top + 8
        col = RED if i < 8 else GREEN
        cv.vline(cx0 + bw // 2, min(top, bot) - 4, abs(top - bot) + 8, col, 2)
        cv.fill_rect(cx0 + 1, min(top, bot), bw - 2,
                     max(4, abs(top - bot)), col)
    ax0, ay0 = x + 12 + 7 * bw, y + h - 14 - int(vals[7] * (h - 28))
    ax1, ay1 = x + w - 16, y + h - 14 - int(vals[-1] * (h - 28))
    cv.line(ax0, ay0, ax1, ay1, GREEN, 3)
    cv.line(ax1, ay1, ax1 - 10, ay1 + 2, GREEN, 3)
    cv.line(ax1, ay1, ax1 - 2, ay1 + 10, GREEN, 3)
    cv.text(x + 10, y + 6, "NASDAQ 100 FUTURES  +~2%", 1, GREEN)
    cv.text(x + 10, y + h - 14, "TAIWAN  -17%  FOR THE WEEK", 1, RED)


def draw_icon(cv, kind, x, y, w, h):
    """Small pictogram inside a card's icon strip."""
    if kind == 'castle':
        cv.poly([(x + w // 2, y + 2), (x + 6, y + 14), (x + w - 6, y + 14)],
                DARKRED)
        cv.fill_rect(x + 10, y + 14, w - 20, h - 16, DARKRED)
        cv.fill_rect(x + w // 2 - 3, y + 18, 6, h - 18, PAPER)
        cv.fill_rect(x + 4, y + 6, 8, 8, DARKRED)
        cv.fill_rect(x + w - 12, y + 6, 8, 8, DARKRED)
    elif kind == 'cricket':
        cv.fill_rect(x + 4, y + 4, w - 8, h - 8, GREEN)
        cv.hline(x + 4, y + h // 2, w - 8, LIGHT, 2)
        cv.circle(x + w // 2, y + h // 2 - 4, 4, LIGHT)
        cv.line(x + w - 14, y + 6, x + w - 6, y + h - 6, (180, 140, 90), 3)
    elif kind == 'plane':
        cv.fill_rect(x + 8, y + h // 2 - 3, w - 16, 6, BLUE)
        cv.poly([(x + w // 2 - 4, y + h // 2 - 3), (x + w // 2 + 10, y + 2),
                 (x + w // 2 + 14, y + h // 2 - 3)], BLUE)
        cv.poly([(x + w // 2 - 2, y + h // 2 + 3), (x + w // 2 + 8, y + h - 2),
                 (x + w // 2 + 12, y + h // 2 + 3)], BLUE)
        cv.poly([(x + w - 10, y + h // 2 - 3), (x + w - 2, y + h // 2 - 8),
                 (x + w - 2, y + h // 2 + 2)], BLUE)
    elif kind == 'bitcoin':
        cv.circle(x + w // 2, y + h // 2, min(w, h) // 2 - 2, ORANGE)
        cv.text(x + w // 2 - 5, y + h // 2 - 7, "B", 2, LIGHT)
    elif kind == 'doc':
        cv.fill_rect(x + w // 2 - 10, y + 3, 20, h - 6, LIGHT)
        cv.rect(x + w // 2 - 10, y + 3, 20, h - 6, INK, 1)
        for i in range(3):
            cv.hline(x + w // 2 - 7, y + 8 + i * 5, 14, INK, 1)
        cv.circle(x + w // 2 + 8, y + h - 8, 4, RED)
    elif kind == 'rocket':
        cv.poly([(x + w // 2, y + 2), (x + w // 2 - 7, y + 14),
                 (x + w // 2 + 7, y + 14)], (120, 125, 130))
        cv.fill_rect(x + w // 2 - 7, y + 14, 14, 8, (120, 125, 130))
        cv.poly([(x + w // 2 - 7, y + 22), (x + w // 2 - 12, y + h - 6),
                 (x + w // 2 - 2, y + h - 6)], RED)
        cv.poly([(x + w // 2 + 7, y + 22), (x + w // 2 + 12, y + h - 6),
                 (x + w // 2 + 2, y + h - 6)], RED)
        cv.circle(x + w // 2, y + h // 2 + 2, 3, ORANGE)
    elif kind == 'drop':
        cv.poly([(x + w // 2, y + 2), (x + w // 2 - 8, y + 14),
                 (x + w // 2 + 8, y + 14)], BLUE)
        cv.circle(x + w // 2, y + 16, 8, BLUE)
    elif kind == 'ribbon':
        cv.circle(x + w // 2, y + 7, 5, TEAL)
        cv.poly([(x + w // 2 - 4, y + 11), (x + w // 2 - 10, y + h - 3),
                 (x + w // 2 - 1, y + h - 3)], TEAL)
        cv.poly([(x + w // 2 + 4, y + 11), (x + w // 2 + 10, y + h - 3),
                 (x + w // 2 + 1, y + h - 3)], TEAL)
    elif kind == 'shield':
        cv.poly([(x + w // 2 - 9, y + 3), (x + w // 2 + 9, y + 3),
                 (x + w // 2 + 9, y + 14), (x + w // 2, y + h - 3),
                 (x + w // 2 - 9, y + 14)], BLUE)
        cv.text(x + w // 2 - 5, y + 7, "!", 2, LIGHT)
    elif kind == 'parliament':
        cv.poly([(x + 4, y + 8), (x + w // 2, y + 2), (x + w - 4, y + 8)],
                GOLD)
        for i in range(3):
            cv.fill_rect(x + 8 + i * 10, y + 10, 5, h - 13, INK)
        cv.hline(x + 4, y + h - 3, w - 8, INK, 2)


# ------------------------------------------------------------- content ----
LEADS = [
    {"num": 1, "kind": "poland",
     "headline": "NATO MEETS OVER POLAND",
     "body": "NATO's council meets in Brussels after Poland said the three "
             "objects that entered its airspace on Friday were Russian "
             "Kh-101 missiles.",
     "source": "Reuters"},
    {"num": 2, "kind": "flags",
     "headline": "NEPAL PM MEETS MODI",
     "body": "Nepal PM Shah meets PM Modi in New Delhi, his first foreign "
             "visit since March; the two flag off a weekly Janakpur-Ayodhya "
             "train.",
     "source": "MEA / IANS"},
    {"num": 3, "kind": "chart",
     "headline": "MARKETS BOUNCE, ASIA BRACES",
     "body": "US futures bounce at the open - Nasdaq 100 up ~2% - as Asia "
             "braces for more AI sell-off; Taiwan down 17% for the week, "
             "worst since 1990.",
     "source": "Reuters"},
]

# Card bodies carry their source in parentheses, wrapped to 3 lines max.
CARDS = [
    {"num": 4, "kind": "castle", "title": "SHURI CASTLE REOPENS",
     "body": "Shuri Castle hall reopens at noon. (AP)"},
    {"num": 5, "kind": "cricket", "title": "WELLINGTON TEST, DAY 5",
     "body": "NZ 139/4, trail India by 213. (ESPNcricinfo)"},
    {"num": 6, "kind": "plane", "title": "FIRST FLIGHT TO WESTERN SYDNEY",
     "body": "Wong lands on first flight. (pm.gov.au)"},
    {"num": 7, "kind": "bitcoin", "title": "BITCOIN HOLDS $61,000",
     "body": "Bitcoin $61,206, up 1.62%. (Finnhub)"},
    {"num": 8, "kind": "doc", "title": "EPSTEIN NOTES DEADLINE",
     "body": "Epstein notes deadline today. (USA Today)"},
    {"num": 9, "kind": "rocket", "title": "CYGNUS XL BRIEFING",
     "body": "NASA briefs Cygnus XL launch. (NASA)"},
    {"num": 10, "kind": "drop", "title": "FIJI DROUGHT",
     "body": "Fiji told to cut water use 30%. (Mai TV)"},
    {"num": 11, "kind": "ribbon", "title": "ASBESTOS KILLS 11 A DAY",
     "body": "Asbestos kills 11 a day. (Cancer Council)"},
    {"num": 12, "kind": "shield", "title": "MELBOURNE STABBINGS",
     "body": "Three stabbings: one dead, two hurt. (AAP)"},
    {"num": 13, "kind": "parliament", "title": "AUSTRALIA'S LAST SITTING WEEK",
     "body": "Final sitting week; gas on agenda. (Squiz)"},
]

ALSO = [
    (14, "Lebanon: scorched groves (Arab News)"),
    (15, "Saudi condemns Khartoum (Arab News)"),
    (16, "Saudi-Bulgaria AI talks (Saudi Press)"),
    (17, "AlUla dates top at SR1,350 (Arab News)"),
    (18, "Strokes up in Singapore (Straits Times)"),
    (19, "Girl arrests at 5-yr high (Straits Times)"),
    (20, "Artex AI hijacked (Straits Times)"),
    (21, "UNSW launches policy school (Medianet)"),
    (22, "JEE Main late-fee entry opens (Shiksha)"),
    (23, "Guru Nanak Jayanti today (ObserverVoice)"),
    (24, "Bromate in water (Times of India)"),
    (25, "Vent worms hold clues (Straits Times)"),
    (26, "Janakpur-Ayodhya train (News On AIR)"),
    (27, "Recycling in Singapore explained (CNA)"),
    (28, "Wesley Mission backs reform (Medianet)"),
    (29, "Cholesterol guesses studied (Medianet)"),
    (30, "Cikande fire search; 24 dead (Xinhua)"),
]

LEFT_OUT = [
    "COP31 talks collapse with no deal",
    "Cikande factory fire (fire 21 Nov)",
    "Democrats clinch 258 US House seats",
    'Mexico captures "El Chapo Isidro"',
    "Two tankers hit in Strait of Hormuz",
    "Miley Cyrus marries Maxx Morando",
    "Alcaraz wins first ATP Finals title",
    "Verstappen wins Las Vegas Grand Prix",
    "Russian warship sunk off Libya",
    "Liverpool thrash Man Utd 4-0",
]

STATS = [
    ("3", "Kh-101 in Poland"),
    ("Nasdaq 100", "futures +~2%"),
    ("Taiwan -17%", "worst week since 1990"),
    ("$61,206", "Bitcoin"),
    ("720/9", "India declared"),
    ("¥8.6bn", "Shuri Castle rebuild"),
]

STRIP = [
    "NATO Council meets in Brussels on Poland",
    "Nepal PM Shah meets Modi in New Delhi",
    "US futures bounce; Asia braces for sell-off",
    "Shuri Castle reopens in Okinawa",
]

TABS = [("EUROPE", 1), ("MIDDLE EAST", 4), ("ASIA-PACIFIC", 20),
        ("AMERICAS", 2), ("WORLD", 3)]

PINS = [(1, 490, 12), (2, 690, 22), (3, 120, 14), (4, 835, 22),
        (5, 925, 44), (6, 800, 32), (7, 200, 19), (8, 150, 25),
        (9, 135, 44), (10, 940, 23), (11, 830, 45), (12, 865, 40),
        (13, 890, 34)]


# -------------------------------------------------------------- layout ----
def build():
    cv = Canvas(W, H, PAPER)
    MX = 22
    CW = W - 2 * MX
    y = 0

    # --- masthead ---
    y = 8
    cv.text_c(W // 2, y, "THE WORLD IN ONE DAY", 2, RED)
    y += 18
    cv.hline(MX, y, CW, RED, 3)
    y += 8
    cv.text_c(W // 2, y, "MONDAY 23 NOVEMBER 2026", 4, INK)
    y += 35
    cv.hline(MX, y, CW, RED, 3)
    y += 8
    cv.text_c(W // 2, y,
              "30 STORIES · 5 REGIONS · EVERY STORY DATED 23 NOVEMBER 2026",
              2, INK)
    y += 18
    cv.hline(MX, y, CW, INK, 2)
    y += 5

    # --- sub-headline strip: 2 x 2, one line each ---
    strip_y0 = y
    cell_w = CW // 2
    for i, item in enumerate(STRIP):
        cx = MX + (i % 2) * cell_w
        cy = strip_y0 + (i // 2) * 14
        cv.fill_rect(cx + 2, cy + 3, 8, 8, RED)
        cv.text(cx + 16, cy, item, 2, INK)
    y = strip_y0 + 28 + 1
    cv.hline(MX, y, CW, GREY, 1)
    y += 5

    # --- six stat boxes ---
    stats_y0 = y
    bw = CW // 6
    for i, (val, lab) in enumerate(STATS):
        bx = MX + i * bw
        cv.fill_rect(bx + 1, stats_y0, bw - 3, 50, LIGHT)
        cv.rect(bx + 1, stats_y0, bw - 3, 50, GREY, 1)
        cv.text(bx + 6, stats_y0 + 4, val, 2, RED)
        cv.para(bx + 6, stats_y0 + 20, bw - 12, lab, 2, INK, 14,
                max_lines=2)
    y = stats_y0 + 50 + 5

    # --- region tabs ---
    tabs_y0 = y
    tab_text = "   ·   ".join("%s %d" % (name, n) for name, n in TABS)
    cv.fill_rect(MX, tabs_y0, CW, 20, INK)
    cv.text_c(W // 2, tabs_y0 + 3, tab_text, 2, LIGHT)
    y = tabs_y0 + 20 + 5

    # --- three large illustrated leads ---
    leads_y0 = y
    col_w = (CW - 20) // 3
    ill_h = 70
    lead_bottom = leads_y0
    for i, lead in enumerate(LEADS):
        lx = MX + i * (col_w + 10)
        cv.rect(lx, leads_y0, col_w, ill_h, INK, 1)
        if lead["kind"] == "poland":
            draw_poland(cv, lx + 1, leads_y0 + 1, col_w - 2, ill_h - 2)
        elif lead["kind"] == "flags":
            draw_flags_train(cv, lx + 1, leads_y0 + 1, col_w - 2, ill_h - 2)
        else:
            draw_chart(cv, lx + 1, leads_y0 + 1, col_w - 2, ill_h - 2)
        cv.circle(lx + 16, leads_y0 + 16, 12, RED)
        cv.text(lx + 12, leads_y0 + 9, str(lead["num"]), 2, LIGHT)
        hy = leads_y0 + ill_h + 6
        hy, _ = cv.para(lx, hy, col_w, lead["headline"], 3, INK, 23,
                         max_lines=2)
        hy += 2
        hy, _ = cv.para(lx, hy, col_w, lead["body"], 2, INK, 14,
                         max_lines=5)
        hy += 1
        cv.text(lx, hy, "(" + lead["source"] + ")", 2, GREY)
        hy += 14
        lead_bottom = max(lead_bottom, hy)
    y = lead_bottom + 5
    cv.hline(MX, y, CW, INK, 2)
    y += 5

    # --- ten numbered cards: 2 rows x 5 ---
    cards_y0 = y
    cw = (CW - 16) // 5
    ch = 100
    for row in range(2):
        for col in range(5):
            card = CARDS[row * 5 + col]
            assert len(wrap(card["title"], cw - 10, 2)) <= 2, card["title"]
            assert len(wrap(card["body"], cw - 10, 2)) <= 3, card["body"]
            cx = MX + col * (cw + 4)
            cy = cards_y0 + row * (ch + 6)
            cv.fill_rect(cx, cy, cw, ch, LIGHT)
            cv.rect(cx, cy, cw, ch, GREY, 1)
            cv.fill_rect(cx + 1, cy + 1, cw - 2, 24, CREAM)
            draw_icon(cv, card["kind"], cx + cw // 2 - 16, cy + 1, 32, 24)
            cv.circle(cx + 13, cy + 13, 10, RED)
            nlab = str(card["num"])
            if len(nlab) == 1:
                cv.text(cx + 9, cy + 6, nlab, 2, LIGHT)
            else:
                cv.text(cx + 8, cy + 10, nlab, 1, LIGHT)
            ty = cy + 26
            ty, _ = cv.para(cx + 5, ty, cw - 10, card["title"], 2, INK, 14,
                             max_lines=2)
            cv.para(cx + 5, ty + 1, cw - 10, card["body"], 2, INK, 14,
                    max_lines=3)
    y = cards_y0 + 2 * ch + 6 + 5

    # --- world map ---
    map_y0 = y
    cv.text(MX, map_y0, "WHERE IT HAPPENED", 2, RED)
    cv.text(MX + text_w("WHERE IT HAPPENED", 2) + 10, map_y0,
            "- NUMBERED PINS MATCH THE STORIES ABOVE", 2, GREY)
    map_y0 += 16
    map_h = 56
    cv.fill_rect(MX, map_y0, CW, map_h, (228, 236, 240))
    cv.rect(MX, map_y0, CW, map_h, SLATE_D, 1)

    def M(fx, fy):
        return (MX + int(fx * CW), map_y0 + int(fy * map_h))
    conts = [
        [(0.05, 0.15), (0.14, 0.05), (0.24, 0.10), (0.26, 0.30),
         (0.20, 0.42), (0.12, 0.40), (0.05, 0.28)],          # N America
        [(0.22, 0.48), (0.28, 0.45), (0.31, 0.58), (0.27, 0.85),
         (0.23, 0.80), (0.21, 0.60)],                        # S America
        [(0.44, 0.10), (0.50, 0.06), (0.53, 0.16), (0.50, 0.28),
         (0.45, 0.26), (0.43, 0.16)],                        # Europe
        [(0.45, 0.32), (0.52, 0.30), (0.55, 0.45), (0.52, 0.72),
         (0.47, 0.70), (0.44, 0.50)],                        # Africa
        [(0.55, 0.08), (0.72, 0.05), (0.86, 0.12), (0.88, 0.30),
         (0.80, 0.42), (0.66, 0.40), (0.58, 0.28), (0.54, 0.16)],
        # Asia
        [(0.82, 0.62), (0.88, 0.60), (0.90, 0.72), (0.85, 0.78),
         (0.81, 0.72)],                                      # Australia
    ]
    for poly in conts:
        pts = [M(fx, fy) for fx, fy in poly]
        cv.poly(pts, (168, 182, 190))
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            cv.line(a[0], a[1], b[0], b[1], SLATE_D, 1)
    for num, px, py in PINS:
        x, yy = MX + px, map_y0 + py
        cv.circle(x, yy, 10, RED)
        cv.circle(x, yy, 10, LIGHT, fill=False)
        lab = str(num)
        if len(lab) == 1:
            cv.text(x - 5, yy - 7, lab, 2, LIGHT)
        else:
            cv.text(x - text_w(lab, 1) // 2, yy - 3, lab, 1, LIGHT)
    y = map_y0 + map_h + 5

    # --- also on Monday: items 14-30, two columns ---
    also_y0 = y
    cv.text(MX, also_y0, "ALSO ON MONDAY 23 NOVEMBER", 2, RED)
    also_y0 += 16
    col2_w = (CW - 12) // 2
    for idx, (num, item) in enumerate(ALSO):
        assert text_w(item, 2) <= col2_w - 34, item
        col = idx // 9
        row = idx % 9
        ax = MX + col * (col2_w + 12)
        ay = also_y0 + row * 14
        cv.text(ax, ay, "%d." % num, 2, RED)
        cv.text(ax + 34, ay, item, 2, INK)
    y = also_y0 + 9 * 14 + 3
    cv.hline(MX, y, CW, INK, 2)
    y += 5

    # --- date check box ---
    box_y0 = y
    cv.text(MX, box_y0, "LEFT OUT - FIRST REPORTED SUNDAY 22 NOVEMBER",
            2, RED)
    box_y0 += 16
    for idx, item in enumerate(LEFT_OUT):
        assert text_w(item, 2) <= col2_w - 12, item
        col = idx // 5
        row = idx % 5
        ax = MX + col * (col2_w + 12)
        ay = box_y0 + row * 14
        cv.fill_rect(ax, ay + 3, 8, 8, RED)
        cv.text(ax + 12, ay, item, 2, INK)
    y = box_y0 + 5 * 14 + 2

    # --- footer ---
    cv.hline(MX, y, CW, INK, 2)
    y += 5
    cv.text_c(W // 2, y,
              "Every story here happened, or was first reported, on Monday "
              "23 November 2026", 2, INK)
    y += 15
    cv.text_c(W // 2, y,
              "Sources: Reuters, AP, Arab News, Straits Times, "
              "ESPNcricinfo, NASA, MEA/IANS, pm.gov.au", 2, GREY)
    y += 14
    cv.text_c(W // 2, y,
              "Cancer Council, Times of India, Finnhub, USA Today, "
              "Medianet, Shiksha, Xinhua, CNA, AAP.", 2, GREY)
    y += 14
    return cv, y


# -------------------------------------------------------------- png ------
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    cv, bottom = build()
    if bottom > H:
        raise SystemExit("layout overflow: bottom=%d > %d" % (bottom, H))
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    data = encode_png(cv)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)
    print("bottom=%d size=%d" % (bottom, len(data)))


if __name__ == "__main__":
    main()
