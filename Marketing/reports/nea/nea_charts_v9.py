#!/usr/bin/env python3
"""Current chart set (v9): captions in the review page, E-notation with superscript exponents,
centred bottom legends, upper-case axis names (units kept as written), no overlapping labels.
Usage: /usr/bin/python3 nea_charts_v9.py OUTDIR
"""
import sys, os, math, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nea_log as N
import nea_charts_v6 as V6
from PIL import Image, ImageDraw, ImageFont
W, H = N.W, N.H
GOLD = (255, 199, 0, 255); WHITE = (255, 255, 255, 255); BLACK = (0, 0, 0, 255)
ORANGE = (234, 88, 12, 255); YELLOW = (255, 199, 0, 255)
PHA = N.PHA_EMOJI; ROCK = N.ROCK_EMOJI; COMET = '☄️'
HERE = os.path.dirname(os.path.abspath(__file__))
LD = N.LD_KM

def fnt(sz, bold=True):
    return ImageFont.truetype(N.FB if bold else N.FR, sz)

def tw(s, sz):
    return ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(s, font=fnt(sz))

def elabel(v, dec=1):
    """E-notation parts: 1.1E then the exponent as a superscript."""
    if v == 0:
        return [("0", "n")]
    return V6.e_parts(v) if dec == 1 else [(f"{v / 10 ** int(math.floor(math.log10(abs(v)))):.{dec}f}E", 'n'), (str(int(math.floor(math.log10(abs(v))))), 's')]

def km_parts(km):
    return elabel(km) + [(' km', 'n')]

def legend_centered(img, th, items, y, cx):
    """items: (kind, colour_or_None, text). kind in pha, rock, comet, rect, line, dot, box."""
    sz = 22; gap = 10; sep = 46; icon = 26
    widths = []
    for kind, col, txt in items:
        ik = icon + 6 if kind in ('pha', 'rock', 'comet') else 36
        widths.append(ik + gap + tw(txt, sz))
    total = sum(widths) + sep * (len(items) - 1)
    x = cx - total / 2; d = ImageDraw.Draw(img)
    for (kind, col, txt), w in zip(items, widths):
        if kind == 'pha': N.emoji(img, PHA, x + icon / 2, y, icon)
        elif kind == 'rock': N.emoji(img, ROCK, x + icon / 2, y, icon)
        elif kind == 'comet': N.emoji(img, COMET, x + icon / 2, y, icon)
        elif kind == 'rect': d.rectangle([x, y - 9, x + 18, y + 9], fill=col)
        elif kind == 'line': N.range_line(d, x, x + 34, y)
        elif kind == 'dot': d.ellipse([x + 4, y - 5, x + 14, y + 5], fill=col)
        ik = icon + 6 if kind in ('pha', 'rock', 'comet') else 36
        N.text(img, (x + ik + gap - 6, y - 12), txt, sz, th.fg)
        x += w + sep

def caption_block(img, th, lines, y):
    for i, t in enumerate(lines):
        N.text(img, (60, y + i * 28), t, 20, th.fg)

def title(img, th, t, sub):
    N.text(img, (60, 40), t, 34, th.fg); N.text(img, (60, 90), sub, 20, th.fg)

def axis_title_h(img, th, s, cx, y):
    N.text(img, (cx, y), s, 26, th.fg, anchor='mt')

def axis_title_v(img, th, s, cx, cy):
    N.text(img, (cx, cy), s, 26, th.fg, angle=90, anchor='cc')

def data_rows(snap_only=True):
    log = N.load_log()
    today = dt.date.today()
    rows = [r for r in log['rows'] if today <= dt.date.fromisoformat(r['approach_date']) <= today + dt.timedelta(days=6)]
    for r in rows:
        r['dmin_km'] = r['diam_min_m'] / 1000; r['dmax_km'] = r['diam_max_m'] / 1000
        r['dmid_km'] = math.sqrt(r['dmin_km'] * r['dmax_km']); r['ld'] = r['miss_ld']
    rows15 = sorted(rows, key=lambda r: r['ld'])[:15]
    return rows15, log

# 1. bubble chart: distance vs velocity and size (log)
def fig_bubbles(rows, style, out, log=True):
    th = N.Theme(style); L, R, T, B = 230, 840, 160, 560
    img, d = N.frame(th, 'DISTANCE VS VELOCITY AND SIZE', f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · {'LOGARITHMIC' if log else 'LINEAR'} SCALE", L, R, T, B)
    ax_x = N.Ax(min(r['ld'] for r in rows) * 0.8 if log else 0, max(r['ld'] for r in rows) * 1.15, L, R, log)
    ax_y = N.Ax(min(r['rel_velocity_kms'] for r in rows) * 0.8 if log else 0, max(r['rel_velocity_kms'] for r in rows) * 1.15, B, T, log)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 14), f"{v:.1f}", 20, th.fg, angle=45, anchor='tr')
        V6.place_rich(img, (x, B + 64), elabel(v * LD) + [(' km', 'n')], 20, th.fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([L - 8, y, L, y], fill=th.fg, width=2)
        N.text(img, (L - 12, y), f"{v:.1f}", 20, th.fg, anchor='rm')
    ordered = sorted(rows, key=lambda r: (not r['pha'], -r['dmid_km']))
    num = {r['key']: i + 1 for i, r in enumerate(ordered)}
    bub = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
    for r in sorted(rows, key=lambda r: r['pha']):
        x, y = ax_x.f(r['ld']), ax_y.f(r['rel_velocity_kms'])
        rad = 8 + 1.6 * math.sqrt(r['dmid_km'] * 1000)
        col = th.pha if r['pha'] else th.other
        bd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col[:3] + (70,), outline=col, width=2)
    img.alpha_composite(bub)
    dd = ImageDraw.Draw(img)
    placed = []
    for r in sorted(rows, key=lambda r: r['pha']):
        x, y = ax_x.f(r['ld']), ax_y.f(r['rel_velocity_kms'])
        N.emoji(img, PHA if r['pha'] else ROCK, x, y - 4, 26)
        lx, ly = x + 16, y - 22                     # number sits up and to the right of its object
        while any(abs(lx - px) < 22 and abs(ly - py) < 20 for px, py in placed):
            ly -= 20
        placed.append((lx, ly))
        dd.text((lx, ly), str(num[r['key']]), font=fnt(16), fill=WHITE, anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, 255))
    N.text(img, ((L + R) // 2, B + 150), 'LUNAR DISTANCE (LD | km | log)' if log else 'LUNAR DISTANCE (LD | km)', 26, th.fg, anchor='mt')
    N.text(img, (L - 64, (T + B) // 2), 'RELATIVE VELOCITY (km/s)', 26, th.fg, angle=90, anchor='cc')
    x0 = 880
    N.text(img, (x0, 146), 'PHA FIRST · SIZE km · LD', 18, th.fg)
    y = T + 8
    for r in ordered:
        N.emoji(img, PHA if r['pha'] else ROCK, x0 + 9, int(y) + 9, 15)
        N.text(img, (x0 + 26, int(y)), f"{num[r['key']]}. {r['designation']}  {r['dmid_km']:.3f} km · {r['ld']:.1f} LD", 15, th.fg)
        y += 16.5
    legend_centered(img, th, [('pha', None, 'Potentially hazardous (PHA)'), ('rock', None, 'Other NEA')], 850, (L + R) // 2)
    img.save(out)

# 2. 3D size, distance, velocity (linear)
def fig_3d(rows, style, out, grid=False):
    th = N.Theme(style); dark = style == 'dark'
    line = GOLD if dark else BLACK
    grid_col = (95, 95, 95, 255) if dark else (170, 170, 170, 255)
    img = Image.new('RGBA', (W, H), th.bg); d = ImageDraw.Draw(img)
    N.text(img, (60, 40), 'SIZE VS DISTANCE VS VELOCITY · 3D', 34, th.fg)
    N.text(img, (60, 90), f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · LINEAR SCALE", 20, th.fg)
    xlo, xhi = 0.0, 0.6; ylo, yhi = -2.0, 200.0
    zlo, zhi = min(r['rel_velocity_kms'] for r in rows), 24.0
    ox, sx, oy, sy = 200, 560, 700, 400
    nu = lambda v: min(1.0, max(0.0, (v - xlo) / (xhi - xlo)))
    nv = lambda v: (v - ylo) / (yhi - ylo)
    nw = lambda v: (v - zlo) / (zhi - zlo)
    P = lambda u, v, w: (ox + u * sx + v * 0.28 * sx, oy - w * sy - v * 0.22 * sy)
    xt = [round(0.1 * k, 1) for k in range(1, 7)]
    yt = [ylo + 30 * k for k in range(8) if ylo + 30 * k <= yhi + 1e-9]
    zt = [zlo + 5 * k for k in range(6) if zlo + 5 * k <= zhi + 1e-9]
    if grid:
        for v in xt:
            V6.dotted(d, P(nu(v), 0, 0), P(nu(v), 1, 0), grid_col, 1, 2, 6)
            V6.dotted(d, P(nu(v), 0, 0), P(nu(v), 0, 1), grid_col, 1, 2, 6)
        for v in yt:
            V6.dotted(d, P(0, nv(v), 0), P(1, nv(v), 0), grid_col, 1, 2, 6)
            V6.dotted(d, P(0, nv(v), 0), P(0, nv(v), 1), grid_col, 1, 2, 6)
            V6.dotted(d, P(1, nv(v), 0), P(1, nv(v), 1), grid_col, 1, 2, 6)
        for v in zt:
            V6.dotted(d, P(0, 0, nw(v)), P(1, 0, nw(v)), grid_col, 1, 2, 6)
            V6.dotted(d, P(0, 0, nw(v)), P(0, 1, nw(v)), grid_col, 1, 2, 6)
            V6.dotted(d, P(1, 0, nw(v)), P(1, 1, nw(v)), grid_col, 1, 2, 6)
    corners = [(u, v, w) for u in (0, 1) for v in (0, 1) for w in (0, 1)]
    for a in corners:
        for b in corners:
            if a < b and sum(abs(p - q) for p, q in zip(a, b)) == 1:
                d.line([P(*a), P(*b)], fill=line, width=2)
    for v in xt:
        x, y = P(nu(v), 0, 0); d.line([x, y, x, y + 10], fill=line, width=2)
        N.text(img, (x, y + 16), f"{v:.1f}", 20, th.fg, anchor='mt')
    for v in yt:
        x, y = P(1, nv(v), 0); d.line([x, y, x + 10, y], fill=line, width=2)
        parts = [(f"{v:.0f}", 'n')] if v <= 0 else [(f"{v:.0f} | ", 'n')] + elabel(v * LD)
        V6.place_rich(img, (x + 8, y), parts, 17, th.fg, angle=90, anchor='lc')
    for v in zt:
        x, y = P(0, 0, nw(v)); d.line([x, y, x - 10, y], fill=line, width=2)
        V6.place_rich(img, (x - 16, y), elabel(v), 20, th.fg, angle=0, anchor='rm')
    for r in sorted(rows, key=lambda r: -nv(r['ld'])):
        u, v, w = nu(r['dmid_km']), nv(r['ld']), nw(r['rel_velocity_kms'])
        x0, y0 = P(u, v, 0); x1, y1 = P(u, v, w)
        V6.dotted(d, (x0, y0), (x1, y1), line, 2, 5, 5)
        N.emoji(img, PHA if r['pha'] else ROCK, x1, y1, 44 if r['pha'] else 30)
    x, y = P(0.5, 0, 0); N.text(img, (x, y + 60), 'OBJECT SIZE (km)', 26, th.fg, anchor='mt')
    x, y = P(1, 0.5, 0); ang = math.degrees(math.atan2(0.22 * sy, 0.28 * sx))
    N.text(img, (960, 812), 'LUNAR DISTANCE (LD | km)', 24, th.fg, angle=ang, anchor='cc')
    x, y = P(0, 0.5, 0.5); N.text(img, (40, y - 60), 'RELATIVE VELOCITY (km/s)', 24, th.fg, angle=90, anchor='cc')
    lx, ly = 560, 122
    N.emoji(img, PHA, lx, ly, 26); N.text(img, (lx + 20, ly - 11), 'PHA', 18, th.fg)
    N.emoji(img, ROCK, lx + 100, ly, 26); N.text(img, (lx + 120, ly - 11), 'Other NEA', 18, th.fg)
    V6.dotted(d, (lx + 230, ly), (lx + 260, ly), line, 2, 5, 5)
    N.text(img, (lx + 268, ly - 11), 'Dotted line = velocity', 18, th.fg)
    d.rectangle([lx + 510, ly - 6, lx + 524, ly + 8], outline=line, width=2)
    N.text(img, (lx + 532, ly - 11), 'Box = axes', 18, th.fg)
    img.save(out)

# 3. diameter vs distance (log, transparent)
def fig_diameter(rows, style, out):
    th = N.Theme(style); L, R, T, B = 250, 940, 160, 600
    img, d = N.frame(th, 'DIAMETER VS DISTANCE', f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · LOGARITHMIC SCALE", L, R, T, B)
    ax_x = N.Ax(min(r['dmin_km'] for r in rows) * 0.7, max(r['dmax_km'] for r in rows) * 1.2, L, R, True)
    ax_y = N.Ax(min(r['ld'] for r in rows) * 0.8, max(r['ld'] for r in rows) * 1.15, B, T, True)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 14), f"{v:g}", 22, th.fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([R, y, R + 8, y], fill=th.fg, width=2)
        N.text(img, (R + 14, y - 14), f"{v:g} LD", 24, th.fg, anchor='lm')
        V6.place_rich(img, (R + 14, y + 14), elabel(v * LD) + [(' km', 'n')], 24, th.fg, angle=0, anchor='lc')
    for r in rows:
        N.range_line(d, ax_x.f(r['dmin_km']), ax_x.f(r['dmax_km']), ax_y.f(r['ld']))
    for r in sorted(rows, key=lambda r: r['pha']):
        N.emoji(img, PHA if r['pha'] else ROCK, ax_x.f(r['dmid_km']), ax_y.f(r['ld']), 30 if r['pha'] else 20)
    N.text(img, ((L + R) // 2, B + 118), 'OBJECT SIZE (km | log)', 28, th.fg, anchor='mt')
    N.text(img, (R + 190, (T + B) // 2), 'LUNAR DISTANCE (LD | km | log)', 26, th.fg, angle=90, anchor='cc')
    legend_centered(img, th, [('pha', None, 'Potentially hazardous (PHA)'), ('rock', None, 'Other NEA'), ('line', None, 'Size uncertainty range')], 860, (L + R) // 2)
    img.save(out)

# 4. cumulative (log)
def fig_cumulative(logd, style, out, start='2026-11-01', end='2026-11-18', log=True):
    th = N.Theme(style); fg = th.fg
    yel = YELLOW if style == 'dark' else (212, 160, 0, 255)
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
    L, R, T, B = 200, 1040, 160, 600
    img, d = N.frame(th, 'CUMULATIVE NEAs SINCE FIRST CAPTURE', f"{start} to {end} · DISTINCT NEAs BY CLOSE-APPROACH DATE · {'LOGARITHMIC' if log else 'LINEAR'} SCALE", L, R, T, B)
    top = max(tot + [1])
    ax_y = N.Ax(1, top * 1.2, B, T, True) if log else N.Ax(0, top * 1.1, B, T, False); ax_x = N.Ax(0, len(days) - 1, L, R, False)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for i, day in enumerate(days):
        x = ax_x.f(i); d.line([x, B, x, B + 6], fill=fg, width=2)
        N.text(img, (x + 4, B + 12), day.strftime('%b %d'), 22, fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([L - 8, y, L, y], fill=fg, width=2)
        N.text(img, (L - 12, y), f"{v:g}", 26, fg, anchor='rm')
    for series, col in ((tot, yel), (pha, ORANGE)):
        pts = [(ax_x.f(i), ax_y.f(max(v, 1) if log else v)) for i, v in enumerate(series)]
        d.line(pts, fill=col, width=4)
        for x, y in pts: d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col, outline=fg)
    N.text(img, ((L + R) // 2, B + 130), 'CLOSE-APPROACH DATE', 28, fg, anchor='mt')
    N.text(img, (60, (T + B) // 2), 'CUMULATIVE NEAs (count)', 28, fg, angle=90, anchor='cc')
    legend_centered(img, th, [('rect', yel, f'All NEAs ({tot[-1]})'), ('rect', ORANGE, f'PHA ({pha[-1]})')], 860, (L + R) // 2)
    img.save(out)

# 5/6. impact plots
def place_numbers(img, items, size=18):
    """items: list of (x, y, text). Moves a label up whenever it would touch one already placed."""
    d = ImageDraw.Draw(img); placed = []
    for x, y, t in items:
        w = tw(t, size) + 4; h = size + 4
        for _ in range(8):   # keep the number on its own row: slide right, then only if needed step up
            if not any(abs((x + w / 2) - (px + pw / 2)) < (w + pw) / 2 and abs(y - py) < (h + ph) / 2 for px, py, pw, ph in placed):
                break
            x += w * 0.6
        while any(abs((x + w / 2) - (px + pw / 2)) < (w + pw) / 2 and abs(y - py) < (h + ph) / 2 for px, py, pw, ph in placed):
            y -= h
        placed.append((x, y, w, h))
        d.text((x, y), t, font=fnt(size), fill=WHITE, anchor='lm', stroke_width=2, stroke_fill=(0, 0, 0, 255))

def load_sentry():
    rows = json.load(open(os.path.join(HERE, 'sentry15.json')))
    rows.sort(key=lambda r: -r['ps'])
    for i, r in enumerate(rows): r['num'] = i + 1
    top3 = {r['des'] for r in sorted(rows, key=lambda r: -r['ip'])[:3]}
    for r in rows: r['comet'] = r['des'] in top3
    return rows

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
        y = ax_l.f(v); d.line([L - 8, y, L, y], fill=fg, width=2)
        N.text(img, (L - 12, y), f"{v}", 20, fg, anchor='rm')
    for v in range(-12, 3, 2):
        y = ax_r.f(v); d.line([R, y, R + 8, y], fill=fg, width=2)
        N.text(img, (R + 12, y), f"{v}", 20, fg, anchor='lm')
    labels = []
    for o, x_ld in zip(pts, ldv):
        x = ax_x.f(x_ld); yt = ax_l.f(o['ts']); yp = ax_r.f(o['ps'])
        d.line([x, yt, x, yp], fill=fg, width=1)
        rad = 6 + 3 * math.sqrt(o.get('diam_km', 0.01) * 1000)
        d.ellipse([x - rad, yp - rad, x + rad, yp + rad], outline=fg, width=1)
        d.ellipse([x - 4, yt - 4, x + 4, yt + 4], fill=fg)
        N.emoji(img, COMET if o['comet'] else (PHA if o.get('pha') else ROCK), x, yp, 30)
        labels.append((x + 20, yp - 30, str(o['num'])))
    place_numbers(img, labels)
    N.text(img, (L - 110, (T + B) // 2), 'TORINO SCALE (0–10)', 24, fg, angle=90, anchor='cc')
    N.text(img, (R + 110, (T + B) // 2), 'PALERMO SCALE', 24, fg, angle=90, anchor='cc')
    N.text(img, ((L + R) // 2, B + 150), 'LUNAR DISTANCE (LD, log)', 26, fg, anchor='mt')
    legend_centered(img, th, [('pha', None, 'PHA'), ('rock', None, 'Other NEA'), ('comet', None, 'Top 3 probability'), ('dot', fg, 'Torino'), ('box', fg, 'Circle radius = size')], 830, (L + R) // 2)
    img.save(out)

def impact_date(objs, style, out):
    th = N.Theme(style); fg = th.fg; L, R, T, B = 200, 1000, 170, 600
    img, d = N.frame(th, 'IMPACT DATE VS PROBABILITY AND DIAMETER', '15 OBJECTS · TOP 15 BY PALERMO · NUMBERS = PALERMO RANK', L, R, T, B)
    yrs = [o['year'] for o in objs]; ips = [o['ip'] for o in objs]; dias = [o.get('diam_km', 0.01) for o in objs]
    ax_x = N.Ax(min(yrs) - 40, max(yrs) + 5, L, R, False)
    ax_p = N.Ax(min(ips) / 3, max(ips) * 3, B, T, True)
    ax_d = N.Ax(min(dias) / 2, max(dias) * 2, B, T, True)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=fg, width=2)
        N.text(img, (x, B + 14), f"{v:.0f}", 20, fg, angle=45, anchor='tr')
    for e in range(-12, 0):
        v = 10 ** e
        if ax_p.lo <= v <= ax_p.hi:
            y = ax_p.f(v); d.line([L - 8, y, L, y], fill=fg, width=2)
            V6.place_rich(img, (L - 12, y), elabel(v), 20, fg, angle=0, anchor='rm')
    for e in range(-4, 2):
        v = 10 ** e
        if ax_d.lo <= v <= ax_d.hi:
            y = ax_d.f(v); d.line([R, y, R + 8, y], fill=fg, width=2)
            V6.place_rich(img, (R + 12, y), elabel(v), 20, fg, angle=0, anchor='lm')
    labels = []
    for o in objs:
        x, y = ax_x.f(o['year']), ax_p.f(o['ip'])
        yd = ax_d.f(o.get('diam_km', 0.01))
        d.ellipse([R - 3, yd - 3, R + 3, yd + 3], fill=fg)
        N.emoji(img, COMET if o['comet'] else (PHA if o.get('pha') else ROCK), x, y, 30)
        labels.append((x + 18, y - 26, str(o['num'])))
    place_numbers(img, labels)
    N.text(img, ((L + R) // 2, B + 150), 'IMPACT YEAR', 26, fg, anchor='mt')
    N.text(img, (L - 130, (T + B) // 2), 'IMPACT PROBABILITY (log)', 24, fg, angle=90, anchor='cc')
    N.text(img, (R + 160, (T + B) // 2), 'DIAMETER (km, log)', 24, fg, angle=90, anchor='cc')
    legend_centered(img, th, [('pha', None, 'PHA'), ('rock', None, 'Other NEA'), ('comet', None, 'Top 3 probability')], 830, (L + R) // 2)
    img.save(out)

def fig_dispersion(rows, style, out, log=True):
    th = N.Theme(style); L, R, T, B = 250, 940, 160, 600
    img, d = N.frame(th, 'DIAMETER VS DISTANCE', f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · {'LOGARITHMIC' if log else 'LINEAR'} SCALE", L, R, T, B)
    ax_x = N.Ax(min(r['dmin_km'] for r in rows) * 0.7 if log else 0, max(r['dmax_km'] for r in rows) * 1.2, L, R, log)
    ax_y = N.Ax(min(r['ld'] for r in rows) * 0.8 if log else 0, max(r['ld'] for r in rows) * 1.15, B, T, log)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 14), f"{v:g}", 22, th.fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([R, y, R + 8, y], fill=th.fg, width=2)
        N.text(img, (R + 14, y - 14), f"{v:g} LD", 22, th.fg, anchor='lm')
        if v > 0: V6.place_rich(img, (R + 14, y + 12), elabel(v * LD) + [(' km', 'n')], 22, th.fg, angle=0, anchor='lc')
    for r in rows:
        N.range_line(d, ax_x.f(r['dmin_km']), ax_x.f(r['dmax_km']), ax_y.f(r['ld']))
    for r in sorted(rows, key=lambda r: r['pha']):
        N.emoji(img, PHA if r['pha'] else ROCK, ax_x.f(r['dmid_km']), ax_y.f(r['ld']), 30 if r['pha'] else 20)
    N.text(img, ((L + R) // 2, B + 118), 'OBJECT SIZE (km | log)' if log else 'OBJECT SIZE (km)', 28, th.fg, anchor='mt')
    N.text(img, (R + 190, (T + B) // 2), 'LUNAR DISTANCE (LD | km | log)' if log else 'LUNAR DISTANCE (LD | km)', 26, th.fg, angle=90, anchor='cc')
    legend_centered(img, th, [('pha', None, 'Potentially hazardous (PHA)'), ('rock', None, 'Other NEA'), ('line', None, 'Size uncertainty range')], 860, (L + R) // 2)
    img.save(out)

def fig_parallel(rows, style, out, log=True):
    th = N.Theme(style); L, R, T, B = 120, 1080, 200, 690
    img, d = N.frame(th, 'PARALLEL COORDINATES · SIZE, DISTANCE, VELOCITY', f"{len(rows)} CLOSEST NEAs · NEXT 7 DAYS · {'LOGARITHMIC' if log else 'LINEAR'} SCALE", L, R, T, B)
    tf = (lambda v: math.log10(v)) if log else (lambda v: v)
    itf = (lambda v: 10 ** v) if log else (lambda v: v)
    cols = [('SIZE (km)', [tf(r['dmid_km']) for r in rows], 240, lambda v: [(f"{itf(v):.3g}", 'n')]),
            ('DISTANCE (LD | km)', [tf(r['ld']) for r in rows], 600, lambda v: [(f"{itf(v):.3g} | ", 'n')] + elabel(itf(v) * LD)),
            ('VELOCITY (km/s)', [tf(r['rel_velocity_kms']) for r in rows], 960, lambda v: [(f"{itf(v):.3g}", 'n')])]
    norms = []
    for name, vals, x, fmt in cols:
        lo, hi = min(vals), max(vals); span = (hi - lo) or 1
        norms.append(lambda v, lo=lo, span=span: (v - lo) / span)
        d.line([x, T, x, B], fill=th.fg, width=3)
        N.text(img, (x, T - 62), name, 24, th.fg, anchor='mm')
        V6.place_rich(img, (x + 14, B + 18), fmt(lo), 20, th.fg, angle=0, anchor='lc')
        V6.place_rich(img, (x + 14, T - 16), fmt(hi), 20, th.fg, angle=0, anchor='lc')
    for i, r in sorted(enumerate(rows), key=lambda t: t[1]['pha']):
        pts = [(x, B - norms[k](vals[i]) * (B - T)) for k, (name, vals, x, fmt) in enumerate(cols)]
        d.line(pts, fill=th.pha if r['pha'] else th.other, width=3)
        N.emoji(img, PHA if r['pha'] else ROCK, pts[0][0], pts[0][1], 26)
    legend_centered(img, th, [('pha', None, 'Potentially hazardous (PHA)'), ('rock', None, 'Other NEA')], 850, (L + R) // 2)
    img.save(out)

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    rows, logd = data_rows()
    sent = load_sentry()
    for style in ('dark', 'transparent'):
        fig_bubbles(rows, style, os.path.join(out, f'1-3-distance-velocity-size-log-{style}.png'), True)
        fig_bubbles(rows, style, os.path.join(out, f'1-3b-distance-velocity-size-linear-{style}.png'), False)
        fig_cumulative(logd, style, os.path.join(out, f'07-cumulative-log-{style}.png'), log=True)
        fig_cumulative(logd, style, os.path.join(out, f'08-cumulative-linear-{style}.png'), log=False)
        fig_3d(rows, style, os.path.join(out, f'2-3-3d-{style}.png'))
        fig_dispersion(rows, style, os.path.join(out, f'3-diameter-vs-distance-log-{style}.png'), True)
        fig_dispersion(rows, style, os.path.join(out, f'3b-diameter-vs-distance-linear-{style}.png'), False)
        fig_parallel(rows, style, os.path.join(out, f'4-parallel-log-{style}.png'), True)
        fig_parallel(rows, style, os.path.join(out, f'4b-parallel-linear-{style}.png'), False)
        impact_dual(sent, style, os.path.join(out, f'imp1-distance-torino-palermo-{style}.png'))
        impact_date(sent, style, os.path.join(out, f'imp2-date-probability-diameter-{style}.png'))
    fig_3d(rows, 'dark', os.path.join(out, '2-3-3d-dark-grid.png'), grid=True)
    print('\n'.join(sorted(os.listdir(out))))

if __name__ == '__main__':
    main()
