#!/usr/bin/env python3
"""Chart set v10: built on v9 helpers, applies the owner's per-chart comments (18 Nov).
Rules kept: E-notation with superscript exponent (never x10^n), axis names upper-case, nothing overlapping,
legend centred under the plot, PHA shown in a legend only when the data has a PHA (re-checked on every run),
tick dates adapt to the amount of data. Usage: /usr/bin/python3 nea_charts_v10.py OUTDIR
"""
import sys, os, math, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nea_log as N
import nea_charts_v6 as V6
import nea_charts_v9 as V9
from nea_charts_v9 import (fnt, tw, elabel, data_rows, load_sentry, place_numbers, fig_parallel,
                           GOLD, WHITE, BLACK, ORANGE, YELLOW, PHA, ROCK, COMET, LD, W, H)
from PIL import Image, ImageDraw

TX = 74           # x centre of every left-hand axis title: lines up with the first letter of the chart title

# size classes shared by every chart that colours by object size (pastel, semi transparent)
SIZE_CLASSES = [("a few metres (< 10 m)", (120, 190, 255)),
                ("tens of metres (10–100 m)", (130, 220, 160)),
                ("hundreds of metres (100 m–1 km)", (255, 215, 120)),
                ("a kilometre or more", (255, 150, 170))]
def size_color(km):
    m = km * 1000
    return SIZE_CLASSES[0][1] if m < 10 else SIZE_CLASSES[1][1] if m < 100 else SIZE_CLASSES[2][1] if m < 1000 else SIZE_CLASSES[3][1]

def num(v):
    """Plain number between 0.01 and 10 000, otherwise E-notation parts (exponent as superscript)."""
    if v == 0 or 1e-2 <= abs(v) < 1e4:
        return [(f"{v:g}", 'n')]
    return elabel(v)

def legend(img, th, items, y, cx):
    """Centred legend. kinds: pha rock comet rect line dot dots box."""
    sz = 22; gap = 10; sep = 46; icon = 26
    ik = lambda k: icon + 6 if k in ('pha', 'rock', 'comet') else 36
    widths = [ik(k) + gap + tw(t, sz) for k, c, t in items]
    x = cx - (sum(widths) + sep * (len(items) - 1)) / 2; d = ImageDraw.Draw(img)
    for (kind, col, txt), w in zip(items, widths):
        if kind == 'pha': N.emoji(img, PHA, x + icon / 2, y, icon)
        elif kind == 'rock': N.emoji(img, ROCK, x + icon / 2, y, icon)
        elif kind == 'comet': N.emoji(img, COMET, x + icon / 2, y, icon)
        elif kind == 'rect': d.rectangle([x, y - 9, x + 18, y + 9], fill=col)
        elif kind == 'line': N.range_line(d, x, x + 34, y)
        elif kind == 'dot': d.ellipse([x + 4, y - 5, x + 14, y + 5], fill=col)
        elif kind == 'dots': V6.dotted(d, (x, y), (x + 30, y), col, 2, 5, 5)
        elif kind == 'swatch': d.ellipse([x, y - 10, x + 20, y + 10], fill=col[:3] + (150,), outline=col[:3] + (255,), width=2)
        N.text(img, (x + ik(kind) + gap - 6, y - 12), txt, sz, th.fg)
        x += w + sep

def rot_rich(img, xy, parts, size, color, angle):
    """Rotated E-notation text whose first character starts exactly at xy."""
    layer = V6.rich(parts, size, color); w, h = layer.size
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC); rw, rh = rot.size
    c, s_ = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    sx_, sy_ = rw / 2 - w / 2 * c, rh / 2 + w / 2 * s_
    img.alpha_composite(rot, (max(0, int(xy[0] - sx_)), max(0, int(xy[1] - sy_))))

def neas(rows):
    items = [('pha', None, 'Potentially hazardous (PHA)')] if any(r['pha'] for r in rows) else []
    return items + [('rock', None, 'NEA (not flagged hazardous)' if items else 'NEA')]

def ticks_every(lo, hi, step):
    v = math.ceil(lo / step) * step; out = []
    while v <= hi + 1e-9:
        out.append(v); v += step
    return out

# 1. bubbles: distance vs velocity and size
def fig_bubbles(rows, style, out, log=True):
    th = N.Theme(style); L, R, T, B = 150, 810, 160, 640
    img, d = N.frame(th, 'DISTANCE VS VELOCITY AND SIZE', f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · {'LOGARITHMIC' if log else 'LINEAR'} SCALE", L, R, T, B)
    lo = min(r['ld'] for r in rows) * 0.8 if log else 0; hi = max(r['ld'] for r in rows) * 1.15
    ax_x = N.Ax(lo, hi, L, R, log)
    ax_y = N.Ax(min(r['rel_velocity_kms'] for r in rows) * 0.8 if log else 0, max(r['rel_velocity_kms'] for r in rows) * 1.15, B, T, log)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    xt = ticks_every(lo, hi, 10)
    if len(xt) < 3: xt = ax_x.ticks()
    last_km = -999
    for v in xt:                       # LD (no decimals) with km on the line below, no units in the ticks
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 12), f"{v:.0f}", 20, th.fg, anchor='mt')
        if x - last_km >= 52:          # km only where it fits without touching its neighbour
            V6.place_rich(img, (x, B + 56), elabel(v * LD), 18, th.fg, angle=0, anchor='cc'); last_km = x
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([L - 8, y, L, y], fill=th.fg, width=2)
        N.text(img, (L - 12, y), f"{v:g}", 20, th.fg, anchor='rm')
    ordered = sorted(rows, key=lambda r: (not r['pha'], -r['dmid_km']))
    nm = {r['key']: i + 1 for i, r in enumerate(ordered)}
    bub = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
    for r in sorted(rows, key=lambda r: r['pha']):
        x, y = ax_x.f(r['ld']), ax_y.f(r['rel_velocity_kms'])
        rad = 8 + 1.6 * math.sqrt(r['dmid_km'] * 1000)
        col = th.pha if r['pha'] else th.other
        bd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col[:3] + (70,), outline=col, width=2)
    img.alpha_composite(bub); dd = ImageDraw.Draw(img); placed = []
    for r in sorted(rows, key=lambda r: r['pha']):
        x, y = ax_x.f(r['ld']), ax_y.f(r['rel_velocity_kms'])
        N.emoji(img, PHA if r['pha'] else ROCK, x, y - 4, 26)
    for r in sorted(rows, key=lambda r: r['pha']):
        x, y = ax_x.f(r['ld']), ax_y.f(r['rel_velocity_kms'])
        lx, ly = x + 16, y - 22
        while any(abs(lx - px) < 22 and abs(ly - py) < 20 for px, py in placed): ly -= 20
        placed.append((lx, ly))
        dd.text((lx, ly), str(nm[r['key']]), font=fnt(16), fill=WHITE, anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, 255))
    ty = B + 84
    N.text(img, ((L + R) // 2, ty), 'LUNAR DISTANCE (LD | km)' + (' · LOG' if log else ''), 26, th.fg, anchor='mt')
    N.text(img, (TX, (T + B) // 2), 'RELATIVE VELOCITY (km/s)', 26, th.fg, angle=90, anchor='cc')
    legend(img, th, neas(rows), ty + 30 + 54, (L + R) // 2)
    # side list: same height as the plot, down to the x-axis title
    x0 = 850; bottom = ty + 30
    N.text(img, (x0, T - 14), ('PHA FIRST · ' if any(r['pha'] for r in rows) else 'LARGEST FIRST · ') + 'SIZE · LD', 22, th.fg)
    step = (bottom - (T + 34)) / len(ordered)
    for i, r in enumerate(ordered):
        y = T + 34 + i * step
        N.emoji(img, PHA if r['pha'] else ROCK, x0 + 9, int(y) + 10, 16)
        V6.place_rich(img, (x0 + 28, int(y) + 10), [(f"{nm[r['key']]}. {r['designation']}  ", 'n')] + elabel(r['dmid_km']) + [(f" km · {r['ld']:.1f} LD", 'n')], 16, th.fg, anchor='lc')
    img.save(out)

# 2. 3D
def fig_3d(rows, style, out, grid=False):
    th = N.Theme(style); dark = style == 'dark'
    line = GOLD if dark else BLACK
    grid_col = (95, 95, 95, 255) if dark else (170, 170, 170, 255)
    img = Image.new('RGBA', (W, H), th.bg); d = ImageDraw.Draw(img)
    N.text(img, (60, 40), 'SIZE VS DISTANCE VS VELOCITY', 34, th.fg)
    N.text(img, (60, 90), f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · LINEAR SCALE", 20, th.fg)
    xlo, xhi = 0.0, max(0.35, max(r['dmid_km'] for r in rows) * 1.05); ylo, yhi = -2.0, 200.0
    zlo = math.floor(min(r['rel_velocity_kms'] for r in rows)); zhi = 24.0
    ox, sx, oy, sy = 180, 560, 700, 400
    nu = lambda v: min(1.0, max(0.0, (v - xlo) / (xhi - xlo)))
    nv = lambda v: (v - ylo) / (yhi - ylo)
    nw = lambda v: (v - zlo) / (zhi - zlo)
    P = lambda u, v, w: (ox + u * sx + v * 0.28 * sx, oy - w * sy - v * 0.22 * sy)
    xt = [round(0.05 * k, 2) for k in range(1, 8) if 0.05 * k <= xhi + 1e-9]
    yt = [ylo + 30 * k for k in range(8) if ylo + 30 * k <= yhi + 1e-9]
    zt = [zlo + 5 * k for k in range(6) if zlo + 5 * k <= zhi + 1e-9]
    if grid:
        for v in xt:
            V6.dotted(d, P(nu(v), 0, 0), P(nu(v), 1, 0), grid_col, 1, 2, 6); V6.dotted(d, P(nu(v), 0, 0), P(nu(v), 0, 1), grid_col, 1, 2, 6)
        for v in yt:
            V6.dotted(d, P(0, nv(v), 0), P(1, nv(v), 0), grid_col, 1, 2, 6); V6.dotted(d, P(0, nv(v), 0), P(0, nv(v), 1), grid_col, 1, 2, 6)
            V6.dotted(d, P(1, nv(v), 0), P(1, nv(v), 1), grid_col, 1, 2, 6)
        for v in zt:
            V6.dotted(d, P(0, 0, nw(v)), P(1, 0, nw(v)), grid_col, 1, 2, 6); V6.dotted(d, P(0, 0, nw(v)), P(0, 1, nw(v)), grid_col, 1, 2, 6)
            V6.dotted(d, P(1, 0, nw(v)), P(1, 1, nw(v)), grid_col, 1, 2, 6)
    corners = [(u, v, w) for u in (0, 1) for v in (0, 1) for w in (0, 1)]
    for a in corners:
        for b in corners:
            if a < b and sum(abs(p - q) for p, q in zip(a, b)) == 1:
                d.line([P(*a), P(*b)], fill=line, width=2)
    for v in xt:
        x, y = P(nu(v), 0, 0); d.line([x, y, x, y + 10], fill=line, width=2)
        N.text(img, (x, y + 16), f"{v:g}", 20, th.fg, anchor='mt')
    ang = math.degrees(math.atan2(0.22 * sy, 0.28 * sx))      # direction of the depth axis on the page
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nrm = (sa, ca)                                             # unit vector pointing down-right, away from the box
    for v in yt:                                               # LD | km, laid along the axis, clear of the line
        x, y = P(1, nv(v), 0); d.line([x, y, x + 8 * nrm[0], y + 8 * nrm[1]], fill=line, width=2)
        parts = [(f"{v:.0f}", 'n')] if v <= 0 else [(f"{v:.0f} | ", 'n')] + elabel(v * LD)
        rot_rich(img, (x + 8 * nrm[0] + 8, y + 8 * nrm[1] + 6), parts, 17, th.fg, 270)
    for v in zt:
        x, y = P(0, 0, nw(v)); d.line([x, y, x - 10, y], fill=line, width=2)
        V6.place_rich(img, (x - 16, y), num(v), 20, th.fg, angle=0, anchor='rm')
    for r in sorted(rows, key=lambda r: -nv(r['ld'])):
        u, v, w = nu(r['dmid_km']), nv(r['ld']), nw(r['rel_velocity_kms'])
        x0, y0 = P(u, v, 0); x1, y1 = P(u, v, w)
        V6.dotted(d, (x0, y0), (x1, y1), line, 2, 5, 5)
        N.emoji(img, PHA if r['pha'] else ROCK, x1, y1, 44 if r['pha'] else 30)
    x, y = P(0.5, 0, 0); N.text(img, (x, y + 56), 'OBJECT SIZE (km)', 26, th.fg, anchor='mt')
    cx, cy = P(1, 0.5, 0)                                      # axis title parallel to the axis, about as far as the X title
    N.text(img, (cx + 150 * nrm[0], cy + 150 * nrm[1]), 'LUNAR DISTANCE (LD | km)', 24, th.fg, angle=ang, anchor='cc')
    N.text(img, (TX, P(0, 0, 0.5)[1] - 40), 'RELATIVE VELOCITY (km/s)', 24, th.fg, angle=90, anchor='cc')
    items = neas(rows)
    items = [(k, c, 'NEA' if k == 'rock' else 'PHA') for k, c, t in items] + [('dots', line, 'Velocity')]
    legend(img, th, items, 140, 640)
    img.save(out)

# 3. diameter vs distance (LD left, km right)
def fig_diameter(rows, style, out, log=True):
    th = N.Theme(style); L, R, T, B = 150, 1000, 160, 640
    img, d = N.frame(th, 'DIAMETER VS DISTANCE', f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · {'LOGARITHMIC' if log else 'LINEAR'} SCALE", L, R, T, B)
    xhi = max(0.35, max(r['dmax_km'] for r in rows) * 1.02)
    ax_x = N.Ax(min(r['dmin_km'] for r in rows) * 0.7 if log else 0, xhi, L, R, log)
    ax_y = N.Ax(min(r['ld'] for r in rows) * 0.8 if log else 0, max(r['ld'] for r in rows) * 1.15, B, T, log)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 14), f"{v:g}", 20, th.fg, anchor='mt')
    for v in ax_y.ticks():
        y = ax_y.f(v)
        if v <= 0: continue
        d.line([L - 8, y, L, y], fill=th.fg, width=2); d.line([R, y, R + 8, y], fill=th.fg, width=2)
        N.text(img, (L - 12, y), f"{v:g}", 20, th.fg, anchor='rm')
        V6.place_rich(img, (R + 14, y), elabel(v * LD), 20, th.fg, anchor='lm')
    for r in rows: N.range_line(d, ax_x.f(r['dmin_km']), ax_x.f(r['dmax_km']), ax_y.f(r['ld']))
    for r in sorted(rows, key=lambda r: r['pha']):
        N.emoji(img, PHA if r['pha'] else ROCK, ax_x.f(r['dmid_km']), ax_y.f(r['ld']), 30 if r['pha'] else 20)
    ty = B + 66
    N.text(img, ((L + R) // 2, ty), 'OBJECT SIZE (km)' + (' · LOG' if log else ''), 26, th.fg, anchor='mt')
    N.text(img, (TX, (T + B) // 2), 'LUNAR DISTANCE (LD)', 26, th.fg, angle=90, anchor='cc')
    N.text(img, (R + 112, (T + B) // 2), 'LUNAR DISTANCE (km)', 26, th.fg, angle=90, anchor='cc')
    legend(img, th, neas(rows) + [('line', None, 'Size uncertainty range')], ty + 30 + 54, (L + R) // 2)
    img.save(out)

# 4. cumulative: tick dates adapt to the number of days
def fig_cumulative(logd, style, out, start='2026-11-01', end=None, log=True):
    th = N.Theme(style); fg = th.fg
    yel = YELLOW if style == 'dark' else (212, 160, 0, 255)
    end = end or dt.date.today().isoformat()
    days, d0, d1 = [], dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    while d0 <= d1:
        days.append(d0); d0 += dt.timedelta(days=1)
    seen, seen_p, tot, pha = set(), set(), [], []
    for day in days:
        for r in logd['rows']:
            if r['approach_date'] == day.isoformat():
                seen.add(r['neo_id'])
                if r['pha']: seen_p.add(r['neo_id'])
        tot.append(len(seen)); pha.append(len(seen_p))
    L, R, T, B = 220, 1060, 160, 620
    img, d = N.frame(th, 'CUMULATIVE NEAs SINCE FIRST CAPTURE', f"{start} to {end} · DISTINCT NEAs BY CLOSE-APPROACH DATE · {'LOGARITHMIC' if log else 'LINEAR'} SCALE", L, R, T, B)
    top = max(tot + [1])
    ax_y = N.Ax(1, top * 1.2, B, T, True) if log else N.Ax(0, top * 1.1, B, T, False); ax_x = N.Ax(0, len(days) - 1, L, R, False)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    step = max(1, math.ceil(len(days) / 16))                   # keeps every date readable as the series grows
    for i, day in enumerate(days):
        x = ax_x.f(i)
        if (len(days) - 1 - i) % step: continue
        d.line([x, B, x, B + 6], fill=fg, width=2)
        N.text(img, (x + 4, B + 12), day.strftime('%b %d'), 20, fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([L - 8, y, L, y], fill=fg, width=2)
        N.text(img, (L - 12, y), f"{v:g}", 24, fg, anchor='rm')
    for series, col in ((tot, yel), (pha, ORANGE)):
        pts = [(ax_x.f(i), ax_y.f(max(v, 1) if log else v)) for i, v in enumerate(series)]
        d.line(pts, fill=col, width=4)
        for x, y in pts: d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col, outline=fg)
    ty = B + 100
    N.text(img, ((L + R) // 2, ty), 'CLOSE-APPROACH DATE', 26, fg, anchor='mt')
    N.text(img, (L - 108, (T + B) // 2), 'CUMULATIVE NEAs (count)', 26, fg, angle=90, anchor='cc')
    legend(img, th, [('rect', yel, f'All NEAs ({tot[-1]})'), ('rect', ORANGE, f'PHA ({pha[-1]})')], ty + 30 + 54, (L + R) // 2)
    img.save(out)

# 5. impact: Torino / Palermo, circles filled by size class
def impact_dual(objs, style, out):
    th = N.Theme(style); fg = th.fg; L, R, T, B = 200, 1000, 170, 600
    pts = [o for o in objs if o.get('dist_au') is not None]
    img, d = N.frame(th, 'DISTANCE VS TORINO AND PALERMO SCALES', f"{len(pts)} OF THE TOP 15 PALERMO OBJECTS HAVE A CLOSE-APPROACH DISTANCE", L, R, T, B)
    ldv = [o['dist_au'] * 389.17 for o in pts]
    ax_x = N.Ax(min(ldv) * 0.8, max(ldv) * 1.2, L, R, True)
    ax_l = N.Ax(0, 10, B, T, False); ax_r = N.Ax(-12, 2, B, T, False)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=fg, width=2)
        N.text(img, (x, B + 14), f"{v:g}", 20, fg, angle=45, anchor='tr')
    for v in range(0, 11):
        y = ax_l.f(v); d.line([L - 8, y, L, y], fill=fg, width=2); N.text(img, (L - 12, y), f"{v}", 20, fg, anchor='rm')
    for v in range(-12, 3, 2):
        y = ax_r.f(v); d.line([R, y, R + 8, y], fill=fg, width=2); N.text(img, (R + 12, y), f"{v}", 20, fg, anchor='lm')
    fill = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fill); labels = []
    for o, x_ld in zip(pts, ldv):
        x = ax_x.f(x_ld); yp = ax_r.f(o['ps']); rad = 6 + 3 * math.sqrt(o.get('diam_km', 0.01) * 1000)
        c = size_color(o.get('diam_km', 0.01))
        fd.ellipse([x - rad, yp - rad, x + rad, yp + rad], fill=c + (110,), outline=c + (255,), width=2)
    img.alpha_composite(fill); d = ImageDraw.Draw(img)
    for o, x_ld in zip(pts, ldv):
        x = ax_x.f(x_ld); yt = ax_l.f(o['ts']); yp = ax_r.f(o['ps'])
        d.line([x, yt, x, yp], fill=fg, width=1); d.ellipse([x - 4, yt - 4, x + 4, yt + 4], fill=fg)
        N.emoji(img, COMET if o['comet'] else (PHA if o.get('pha') else ROCK), x, yp, 30)
        labels.append((min(x + 20, R - 34), max(yp - 30, T + 14), str(o['num'])))
    place_numbers(img, labels)
    ty = B + 112
    N.text(img, (TX, (T + B) // 2), 'TORINO SCALE (0–10)', 24, fg, angle=90, anchor='cc')
    N.text(img, (R + 110, (T + B) // 2), 'PALERMO SCALE', 24, fg, angle=90, anchor='cc')
    N.text(img, ((L + R) // 2, ty), 'LUNAR DISTANCE (LD, log)', 26, fg, anchor='mt')
    items = ([('pha', None, 'PHA')] if any(o.get('pha') for o in pts) else []) + [('rock', None, 'NEA'), ('comet', None, 'Top 3 probability'), ('dot', fg, 'Torino')]
    legend(img, th, items, ty + 30 + 54, (L + R) // 2)
    legend(img, th, [('swatch', c + (255,), n) for n, c in SIZE_CLASSES[:2]], ty + 30 + 100, (L + R) // 2)
    legend(img, th, [('swatch', c + (255,), n) for n, c in SIZE_CLASSES[2:]], ty + 30 + 140, (L + R) // 2)
    img.save(out)

def impact_date(objs, style, out):
    th = N.Theme(style); fg = th.fg; L, R, T, B = 200, 1000, 170, 600
    img, d = N.frame(th, 'IMPACT DATE VS PROBABILITY AND DIAMETER', '15 OBJECTS · TOP 15 BY PALERMO · NUMBERS = PALERMO RANK', L, R, T, B)
    yrs = [o['year'] for o in objs]; ips = [o['ip'] for o in objs]; dias = [o.get('diam_km', 0.01) for o in objs]
    ax_x = N.Ax(min(yrs) - 40, max(yrs) + 5, L, R, False)
    ax_p = N.Ax(min(ips) / 3, max(ips) * 3, B, T, True); ax_d = N.Ax(min(dias) / 2, max(dias) * 2, B, T, True)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=fg, width=2); N.text(img, (x, B + 14), f"{v:.0f}", 20, fg, angle=45, anchor='tr')
    for e in range(-12, 0):
        v = 10 ** e
        if ax_p.lo <= v <= ax_p.hi:
            y = ax_p.f(v); d.line([L - 8, y, L, y], fill=fg, width=2); V6.place_rich(img, (L - 12, y), elabel(v), 20, fg, anchor='rm')
    for e in range(-4, 2):
        v = 10 ** e
        if ax_d.lo <= v <= ax_d.hi:
            y = ax_d.f(v); d.line([R, y, R + 8, y], fill=fg, width=2); V6.place_rich(img, (R + 12, y), num(v), 20, fg, anchor='lm')
    labels = []
    for o in objs:
        x, y = ax_x.f(o['year']), ax_p.f(o['ip']); yd = ax_d.f(o.get('diam_km', 0.01))
        d.ellipse([R - 3, yd - 3, R + 3, yd + 3], fill=fg)
        N.emoji(img, COMET if o['comet'] else (PHA if o.get('pha') else ROCK), x, y, 30)
        labels.append((min(x + 18, R - 34), max(y - 26, T + 14), str(o['num'])))
    place_numbers(img, labels)
    ty = B + 112
    N.text(img, ((L + R) // 2, ty), 'IMPACT YEAR', 26, fg, anchor='mt')
    N.text(img, (TX, (T + B) // 2), 'IMPACT PROBABILITY (log)', 24, fg, angle=90, anchor='cc')
    N.text(img, (R + 110, (T + B) // 2), 'DIAMETER (km, log)', 24, fg, angle=90, anchor='cc')
    items = ([('pha', None, 'PHA')] if any(o.get('pha') for o in objs) else []) + [('rock', None, 'NEA'), ('comet', None, 'Top 3 probability')]
    legend(img, th, items, ty + 30 + 54, (L + R) // 2)
    img.save(out)

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    rows, logd = data_rows(); sent = load_sentry()
    for style in ('dark', 'transparent'):
        fig_bubbles(rows, style, os.path.join(out, f'1-3-distance-velocity-size-log-{style}.png'), True)
        fig_bubbles(rows, style, os.path.join(out, f'1-3b-distance-velocity-size-linear-{style}.png'), False)
        fig_cumulative(logd, style, os.path.join(out, f'07-cumulative-log-{style}.png'), log=True)
        fig_cumulative(logd, style, os.path.join(out, f'08-cumulative-linear-{style}.png'), log=False)
        fig_3d(rows, style, os.path.join(out, f'2-3-3d-{style}.png'))
        fig_diameter(rows, style, os.path.join(out, f'3-diameter-vs-distance-log-{style}.png'), True)
        fig_diameter(rows, style, os.path.join(out, f'3b-diameter-vs-distance-linear-{style}.png'), False)
        V9.legend_centered = lambda img, th, items, y, cx: legend(img, th, neas(rows), y, cx)
        fig_parallel(rows, style, os.path.join(out, f'4-parallel-log-{style}.png'), True)
        fig_parallel(rows, style, os.path.join(out, f'4b-parallel-linear-{style}.png'), False)
        impact_dual(sent, style, os.path.join(out, f'imp1-distance-torino-palermo-{style}.png'))
        impact_date(sent, style, os.path.join(out, f'imp2-date-probability-diameter-{style}.png'))
    fig_3d(rows, 'dark', os.path.join(out, '2-3-3d-dark-grid.png'), grid=True)
    print(len(os.listdir(out)), 'charts')

if __name__ == '__main__':
    main()
