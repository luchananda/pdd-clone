#!/usr/bin/env python3
"""Chart set v6 for the Space Luisa home page. Reuses nea_log.py helpers.
Usage: /usr/bin/python3 nea_charts_v6.py OUTDIR
"""
import sys, os, math, json, datetime as dt, urllib.request, urllib.parse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nea_log as N
from PIL import Image, ImageDraw, ImageFont

W, H = N.W, N.H
GOLD, WHITE, BLACK = N.GOLD, N.WHITE, N.BLACK
LIGHT_GRAY = (200, 200, 200, 255)
EN = dict(
    bub_title='Distance vs Velocity and Size', d3_title='Size vs Distance vs Velocity - 3D plot',
    disp_title='Diameter vs Distance', leg_pha='PHA', leg_rock='Other NEA',
    leg_dot='Dotted line = velocity', leg_box='Box = axes', leg_unc='Size range',
    x_size='Object Size (km)', y_dist='Lunar Distance (LD | km)', z_vel='Relative Velocity (km/s)',
    x_dist='Lunar Distance (LD | Km | log)', y_vel='Relative Velocity (km/s)',
    x_size_log='Object Size (km | log)', y_dist_log='Lunar Distance (LD | km | log)',
)


def sci(v, dec=1):
    """Scientific notation with one decimal, e.g. 3.8×10^5."""
    if v == 0:
        return '0'
    e = int(math.floor(math.log10(abs(v))))
    return f"{v / 10 ** e:.{dec}f}×10^{e}"


def sci_E(v, dec=1):
    """E^exponent form requested for figure 4/4, e.g. 1.3E^6."""
    if v == 0:
        return '0'
    e = int(math.floor(math.log10(abs(v))))
    return f"{v / 10 ** e:.{dec}f}E^{e}"


def dotted(d, p0, p1, color, width=2, dash=6, gap=6):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    if L == 0:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    t = 0.0
    while t < L:
        a, b = t, min(L, t + dash)
        d.line([x0 + ux * a, y0 + uy * a, x0 + ux * b, y0 + uy * b], fill=color, width=width)
        t += dash + gap


def top20(rows):
    return sorted(rows, key=lambda r: r['ld'])[:20]


# ---------- 1/3: distance vs velocity and size (bubble, log, dark) ----------
def fig1(rows, out, style='dark'):
    th = N.Theme(style); L, R, T, B = 230, 840, 160, 560
    img, d = N.frame(th, EN['bub_title'], f"{len(rows)} closest NEAs · next 7 days · logarithmic scale · bubble area = mean size", L, R, T, B)
    ax_x = N.Ax(min(r['ld'] for r in rows) * 0.8, max(r['ld'] for r in rows) * 1.15, L, R, True)
    ax_y = N.Ax(min(r['rel_velocity_kms'] for r in rows) * 0.8, max(r['rel_velocity_kms'] for r in rows) * 1.15, B, T, True)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for v in ax_x.ticks():                                  # LD row and km row, ticks aligned to their labels
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 14), f"{v:.1f}", 20, th.fg, angle=45, anchor='tr')
        N.text(img, (x, B + 62), sci(v * N.LD_KM), 20, th.fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([L - 8, y, L, y], fill=th.fg, width=2)
        N.text(img, (L - 12, y), f"{v:.1f}", 20, th.fg, angle=45, anchor='rc')
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
    for r in sorted(rows, key=lambda r: r['pha']):
        x, y = ax_x.f(r['ld']), ax_y.f(r['rel_velocity_kms'])
        N.emoji(img, N.PHA_EMOJI if r['pha'] else N.ROCK_EMOJI, x, y - 4, 26)
        dd.text((x, y + 14), str(num[r['key']]), font=N.font(15), fill=WHITE, anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, 255))
    N.text(img, ((L + R) // 2, B + 150), EN['x_dist'], 28, th.fg, anchor='mt')
    N.text(img, (L - 64, (T + B) // 2), EN['y_vel'], 28, th.fg, angle=90, anchor='cc')
    x0 = 880
    N.text(img, (x0, 146), 'PHA first · size km · LD', 18, th.fg)
    y = T + 8
    for r in ordered:
        N.emoji(img, N.PHA_EMOJI if r['pha'] else N.ROCK_EMOJI, x0 + 9, int(y) + 9, 15)
        N.text(img, (x0 + 26, int(y)), f"{num[r['key']]}. {r['designation']}  {r['dmid_km']:.3f} km · {r['ld']:.1f} LD", 15, th.fg)
        y += 16.5
    N.legend(img, th, {'leg_pha': EN['leg_pha'], 'leg_rock': EN['leg_rock']}, 825)
    img.save(out)


# ---------- 2/3: 3D, linear axes ----------
def e_parts(v):
    """Value in E notation with the exponent as a superscript: 1.1E⁷ (no caret)."""
    e = int(math.floor(math.log10(abs(v))))
    return [(f"{v / 10 ** e:.1f}E", 'n'), (str(e), 's')]


def rich(parts, size, color, sup=0):
    f1, f2 = N.font(size), N.font(int(size * 0.62) + sup)
    probe = ImageDraw.Draw(Image.new('RGBA', (4, 4)))
    w = 8
    for t, m in parts:
        bb = probe.textbbox((0, 0), t, font=f2 if m == 's' else f1); w += bb[2] - bb[0]
    img = Image.new('RGBA', (w, int(size * 1.6)), (0, 0, 0, 0)); dd = ImageDraw.Draw(img)
    x = 4
    for t, m in parts:
        if m == 's':
            dd.text((x, 2), t, font=f2, fill=color)           # superscript: raised, smaller
            bb = probe.textbbox((0, 0), t, font=f2)
        else:
            dd.text((x, int(size * 0.35)), t, font=f1, fill=color)
            bb = probe.textbbox((0, 0), t, font=f1)
        x += bb[2] - bb[0]
    return img


def place_rich(img, xy, parts, size, color, angle=0, anchor='lc', sup=0):
    layer = rich(parts, size, color, sup)
    if angle:
        layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    rw, rh = layer.size; x, y = xy
    px, py = {'lc': (x, y - rh // 2), 'lm': (x, y - rh // 2), 'rm': (x - rw, y - rh // 2), 'cc': (x - rw // 2, y - rh // 2), 'tr': (x - rw, y), 'mt': (x - rw // 2, y)}[anchor]
    img.alpha_composite(layer, (max(0, int(px)), max(0, int(py))))


def fig2(rows, variant, out):
    dark = variant != 'transparent'
    th = N.Theme('dark' if dark else 'transparent')
    line = GOLD if dark else BLACK
    grid_col = (95, 95, 95, 255)
    img = Image.new('RGBA', (W, H), th.bg); d = ImageDraw.Draw(img)
    N.text(img, (60, 40), EN['d3_title'], 34, th.fg)
    N.text(img, (60, 90), f"{len(rows)} closest NEAs · next 7 days · linear scale", 20, th.fg)
    xlo, xhi = 0.0, 0.6
    ylo, yhi = -2.0, 200.0
    zlo, zhi = min(r['rel_velocity_kms'] for r in rows), 24.0
    ox, sx, oy, sy = 200, 560, 700, 400

    def nu(v): return min(1.0, max(0.0, (v - xlo) / (xhi - xlo)))
    def nv(v): return (v - ylo) / (yhi - ylo)
    def nw(v): return (v - zlo) / (zhi - zlo)

    def P(u, v, w):
        return ox + u * sx + v * 0.28 * sx, oy - w * sy - v * 0.22 * sy
    xt = [round(0.1 * k, 1) for k in range(1, 7)]                 # 0.1 ... 0.6
    yt = [ylo + 30 * k for k in range(8) if ylo + 30 * k <= yhi + 1e-9]
    zt = [zlo + 5 * k for k in range(6) if zlo + 5 * k <= zhi + 1e-9]
    if variant == 'grid':   # faint dotted grid lines at every tick of every axis, on the three inner faces
        for v in xt:
            dotted(d, P(nu(v), 0, 0), P(nu(v), 1, 0), grid_col, 1, 2, 6)     # floor
            dotted(d, P(nu(v), 0, 0), P(nu(v), 0, 1), grid_col, 1, 2, 6)     # left wall
        for v in yt:
            dotted(d, P(0, nv(v), 0), P(1, nv(v), 0), grid_col, 1, 2, 6)     # floor
            dotted(d, P(0, nv(v), 0), P(0, nv(v), 1), grid_col, 1, 2, 6)     # left wall
            dotted(d, P(1, nv(v), 0), P(1, nv(v), 1), grid_col, 1, 2, 6)     # right wall
        for v in zt:
            dotted(d, P(0, 0, nw(v)), P(1, 0, nw(v)), grid_col, 1, 2, 6)     # back wall
            dotted(d, P(0, 0, nw(v)), P(0, 1, nw(v)), grid_col, 1, 2, 6)     # left wall
            dotted(d, P(1, 0, nw(v)), P(1, 1, nw(v)), grid_col, 1, 2, 6)     # right wall
    corners = [(u, v, w) for u in (0, 1) for v in (0, 1) for w in (0, 1)]
    for a_ in corners:
        for b_ in corners:
            if a_ < b_ and sum(abs(p_ - q_) for p_, q_ in zip(a_, b_)) == 1:
                d.line([P(*a_), P(*b_)], fill=line, width=2)
    for v in xt:                                              # X: 0.1 ... 0.6, one decimal
        x, y = P(nu(v), 0, 0)
        d.line([x, y, x, y + 10], fill=line, width=2)
        N.text(img, (x, y + 16), f"{v:.1f}", 20, th.fg, anchor='mt')
    for v in yt:                                              # Y: distance, rotated 90, one space from the axis
        x, y = P(1, nv(v), 0)
        d.line([x, y, x + 10, y], fill=line, width=2)
        parts = [(f"{v:.0f}", 'n')] if v <= 0 else [(f"{v:.0f} | ", 'n')] + e_parts(v * N.LD_KM) + [(" km", 'n')]
        place_rich(img, (x + 8, y), parts, 20, th.fg, angle=90, anchor='lc')
    for v in zt:                                              # Z: velocity, E notation
        x, y = P(0, 0, nw(v))
        d.line([x, y, x - 10, y], fill=line, width=2)
        place_rich(img, (x - 16, y), e_parts(v), 20, th.fg, angle=0, anchor='rm')
    order = sorted(rows, key=lambda r: -nv(r['ld']))           # far (back) first
    for r in order:
        u, v, w = nu(r['dmid_km']), nv(r['ld']), nw(r['rel_velocity_kms'])
        x0, y0 = P(u, v, 0); x1, y1 = P(u, v, w)
        dotted(d, (x0, y0), (x1, y1), line, 2, 5, 5)
        N.emoji(img, N.PHA_EMOJI if r['pha'] else N.ROCK_EMOJI, x1, y1, 44 if r['pha'] else 30)
    x, y = P(0.5, 0, 0); N.text(img, (x, y + 60), EN['x_size'], 26, th.fg, anchor='mt')
    x, y = P(1, 0.5, 0)
    ang = math.degrees(math.atan2(0.22 * sy, 0.28 * sx))
    N.text(img, (960, 812), EN['y_dist'], 24, th.fg, angle=ang, anchor='cc')
    x, y = P(0, 0.5, 0.5); N.text(img, (40, y - 60), EN['z_vel'], 24, th.fg, angle=90, anchor='cc')
    lx, ly = 560, 122
    N.emoji(img, N.PHA_EMOJI, lx, ly, 26); N.text(img, (lx + 20, ly - 11), EN['leg_pha'], 18, th.fg)
    N.emoji(img, N.ROCK_EMOJI, lx + 100, ly, 26); N.text(img, (lx + 120, ly - 11), EN['leg_rock'], 18, th.fg)
    dotted(d, (lx + 230, ly), (lx + 260, ly), line, 2, 5, 5)
    N.text(img, (lx + 268, ly - 11), EN['leg_dot'], 18, th.fg)
    d.rectangle([lx + 510, ly - 6, lx + 524, ly + 8], outline=line, width=2)
    N.text(img, (lx + 532, ly - 11), EN['leg_box'], 18, th.fg)
    img.save(out)


# ---------- 4/4: diameter vs distance, log, transparent, bigger ticks, LD over E^n km ----------
def fig4(rows, out):
    th = N.Theme('transparent'); L, R, T, B = 250, 940, 160, 600
    img, d = N.frame(th, 'Diameter vs Distance', f"{len(rows)} closest NEAs · next 7 days · logarithmic scale", L, R, T, B)
    ax_x = N.Ax(min(r['dmin_km'] for r in rows) * 0.7, max(r['dmax_km'] for r in rows) * 1.2, L, R, True)
    ax_y = N.Ax(min(r['ld'] for r in rows) * 0.8, max(r['ld'] for r in rows) * 1.15, B, T, True)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 14), f"{v:g}", 22, th.fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([R, y, R + 8, y], fill=th.fg, width=2)
        N.text(img, (R + 14, y - 13), f"{v:g} LD", 26, th.fg, anchor='lm')
        N.text(img, (R + 14, y + 13), sci_E(v * N.LD_KM), 26, th.fg, anchor='lm')
    for r in rows:
        N.range_line(d, ax_x.f(r['dmin_km']), ax_x.f(r['dmax_km']), ax_y.f(r['ld']))
    for r in sorted(rows, key=lambda r: r['pha']):
        N.emoji(img, N.PHA_EMOJI if r['pha'] else N.ROCK_EMOJI, ax_x.f(r['dmid_km']), ax_y.f(r['ld']), 30 if r['pha'] else 20)
    N.text(img, ((L + R) // 2, B + 118), 'Object Size (km | log)', 28, th.fg, anchor='mt')
    N.text(img, (R + 190, (T + B) // 2), 'Lunar Distance (LD | km | log)', 26, th.fg, angle=90, anchor='cc')
    N.legend(img, th, {'leg_pha': EN['leg_pha'], 'leg_rock': EN['leg_rock'], 'leg_unc': EN['leg_unc']}, 850, unc=True)
    img.save(out)


# ---------- impact risk (Sentry) ----------
def sentry_objects(n=60):
    data = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentry_top.json')))
    return data[:n]


def impact_fig(objs, key, title, sub, ylabel, out, ylog=False, yrange=None):
    th = N.Theme('dark'); L, R, T, B = 230, 1000, 170, 620
    img, d = N.frame(th, title, sub, L, R, T, B)
    xs = [o['diam_km'] for o in objs]
    ax_x = N.Ax(min(xs) * 0.7, max(xs) * 1.3, L, R, True)
    lo, hi = yrange
    ax_y = N.Ax(lo, hi, B, T, ylog)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=th.fg, width=2)
        N.text(img, (x, B + 14), f"{v:g}", 20, th.fg, angle=45, anchor='tr')
    for v in (range(int(lo), int(hi) + 1) if not ylog else ax_y.ticks()):
        y = ax_y.f(v); d.line([L - 8, y, L, y], fill=th.fg, width=2)
        N.text(img, (L - 12, y), f"{v:g}", 20, th.fg, anchor='rm')
    for o in objs:
        x, y = ax_x.f(o['diam_km']), ax_y.f(o[key])
        col = th.pha if o['ts'] >= 1 else th.other
        emoji_ch = N.PHA_EMOJI if o['ts'] >= 1 else N.ROCK_EMOJI
        N.emoji(img, emoji_ch, x, y, 26)
    N.text(img, ((L + R) // 2, B + 118), 'Object Size (km | log)', 26, th.fg, anchor='mt')
    N.text(img, (L - 80, (T + B) // 2), ylabel, 24, th.fg, angle=90, anchor='cc')
    return img, d, ax_x, ax_y


def impact_charts(out_dir, objs):
    names = {}
    # 1: size vs Torino
    img, d, ax_x, ax_y = impact_fig(objs, 'ts', 'Size vs Torino scale · impact risk',
                                    f"{len(objs)} objects in the Sentry list · Torino scale 0–10", 'Torino scale', None, False, (0, 10))
    p = os.path.join(out_dir, 'imp1-size-torino.png'); img.save(p); names['imp1'] = p
    # 2: size vs Palermo
    img, d, ax_x, ax_y = impact_fig(objs, 'ps', 'Size vs Palermo scale · impact risk',
                                    f"{len(objs)} objects in the Sentry list · Palermo scale (log)", 'Palermo scale', None, False, (-12, 0))
    p = os.path.join(out_dir, 'imp2-size-palermo.png'); img.save(p); names['imp2'] = p
    # 3: impact date vs probability, top 10 labelled
    th = N.Theme('dark'); L, R, T, B = 230, 1000, 170, 620
    img, d = N.frame(th, 'Impact date vs probability · top 10', f"{len(objs)} objects · probability (log) · labels = top 10 by Palermo", L, R, T, B)
    yrs = [o['year'] for o in objs]; ps_ = [o['ip'] for o in objs]
    ax_x = N.Ax(min(yrs) - 2, max(yrs) + 2, L, R, False)
    ax_y = N.Ax(min(ps_) * 0.5, max(ps_) * 2, B, T, True)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    top10 = {o['des'] for o in sorted(objs, key=lambda o: -o['ps'])[:10]}
    for o in objs:
        x, y = ax_x.f(o['year']), ax_y.f(o['ip'])
        N.emoji(img, N.PHA_EMOJI if o['des'] in top10 else N.ROCK_EMOJI, x, y, 26 if o['des'] in top10 else 18)
        if o['des'] in top10:
            N.text(img, (x + 14, y - 10), o['des'], 18, th.fg)
    N.text(img, ((L + R) // 2, B + 90), 'Impact date (year)', 26, th.fg, anchor='mt')
    N.text(img, (L - 90, (T + B) // 2), 'Impact probability (log)', 24, th.fg, angle=90, anchor='cc')
    p = os.path.join(out_dir, 'imp3-date-probability-top10.png'); img.save(p); names['imp3'] = p
    return names


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    log = N.load_log()
    today = dt.date.today()
    snap = [r for r in log['rows'] if today <= dt.date.fromisoformat(r['approach_date']) <= today + dt.timedelta(days=6)]
    for r in snap:
        r['dmin_km'] = r['diam_min_m'] / 1000; r['dmax_km'] = r['diam_max_m'] / 1000
        r['dmid_km'] = math.sqrt(r['dmin_km'] * r['dmax_km']); r['ld'] = r['miss_ld']
    rows = top20(snap)
    made = []
    made.append(fig1(rows, os.path.join(out_dir, '1-3-distance-velocity-size-log-dark.png')))
    made.append(fig2(rows, 'dark', os.path.join(out_dir, '2-3-3d-dark.png')))
    made.append(fig2(rows, 'transparent', os.path.join(out_dir, '2-3-3d-transparent.png')))
    made.append(fig2(rows, 'grid', os.path.join(out_dir, '2-3-3d-dark-grid.png')))
    made.append(fig4(rows, os.path.join(out_dir, '4-4-diameter-vs-distance-log-transparent.png')))
    impact_charts(out_dir, sentry_objects())
    print('\n'.join(os.path.join(out_dir, f) for f in sorted(os.listdir(out_dir)) if f.endswith('.png')))


if __name__ == '__main__':
    main()
