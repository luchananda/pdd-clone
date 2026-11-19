#!/usr/bin/env python3
"""Chart set v7: impact-risk plots (20 objects), cumulative 08 with new colours, transparent variants.
Usage: /usr/bin/python3 nea_charts_v7.py OUTDIR
"""
import sys, os, math, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nea_log as N
import nea_charts_v6 as V6
from PIL import Image, ImageDraw
W, H = N.W, N.H
HERE = os.path.dirname(os.path.abspath(__file__))
COMET = '☄️'
ORANGE = (234, 88, 12, 255)
YELLOW = (255, 199, 0, 255)
YELLOW_T = (212, 160, 0, 255)


def load_sentry():
    rows = json.load(open(os.path.join(HERE, 'sentry15.json')))
    rows.sort(key=lambda r: -r['ps'])
    rows = rows[:15]
    for i, r in enumerate(rows):
        r['num'] = i + 1
    top3 = {r['des'] for r in sorted(rows, key=lambda r: -r['ip'])[:3]}
    for r in rows:
        r['comet'] = r['des'] in top3
    return rows


def impact_dual(objs, out, style):
    """Distance (LD, log) on X. Left axis: Torino 0-10. Right axis: Palermo. Size = circle around each object."""
    th = N.Theme(style); fg = th.fg
    L, R, T, B = 200, 1000, 170, 620
    pts = [o for o in objs if o.get('dist_au') is not None]
    img, d = N.frame(th, 'Distance vs Torino (left) and Palermo (right)',
                     f"{len(pts)} of the top 15 Palermo objects have a close-approach distance · dot = Torino, emoji = Palermo", L, R, T, B)
    ld = [o['dist_au'] * 389.17 for o in pts]
    ax_x = N.Ax(min(ld) * 0.8, max(ld) * 1.2, L, R, True)
    ax_l = N.Ax(0, 10, B, T, False)
    ax_r = N.Ax(-12, 2, B, T, False)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=fg, width=2)
        N.text(img, (x, B + 14), f"{v:g}", 20, fg, angle=45, anchor='tr')
    for v in range(0, 11):
        y = ax_l.f(v); d.line([L - 8, y, L, y], fill=fg, width=2)
        N.text(img, (L - 12, y), f"{v}", 20, fg, anchor='rm')
    for v in range(-12, 3, 2):
        y = ax_r.f(v); d.line([R, y, R + 8, y], fill=fg, width=2)
        N.text(img, (R + 12, y), f"{v}", 20, fg, anchor='lm')
    for o, x_ld in zip(pts, ld):
        x = ax_x.f(x_ld); yt = ax_l.f(o['ts']); yp = ax_r.f(o['ps'])
        d.line([x, yt, x, yp], fill=fg, width=1)
        rad = 6 + 3 * math.sqrt(o.get('diam_km', 0.01) * 1000)
        d.ellipse([x - rad, yp - rad, x + rad, yp + rad], outline=fg, width=1)
        d.ellipse([x - 4, yt - 4, x + 4, yt + 4], fill=fg)
        ch = COMET if o['comet'] else (N.PHA_EMOJI if o.get('pha') else N.ROCK_EMOJI)
        N.emoji(img, ch, x, yp, 30)
        N.text(img, (x + 18, yp - 26), str(o['num']), 18, fg)
    N.text(img, (L - 110, (T + B) // 2), 'Torino scale (0–10)', 24, fg, angle=90, anchor='cc')
    N.text(img, (R + 110, (T + B) // 2), 'Palermo scale', 24, fg, angle=90, anchor='cc')
    N.text(img, ((L + R) // 2, B + 150), 'Lunar distance (LD, log)', 26, fg, anchor='mt')
    # legend (one line)
    lx, ly = 200, 820
    N.emoji(img, N.PHA_EMOJI, lx, ly, 26); N.text(img, (lx + 20, ly - 11), 'PHA', 18, fg)
    N.emoji(img, N.ROCK_EMOJI, lx + 90, ly, 26); N.text(img, (lx + 110, ly - 11), 'Other NEA', 18, fg)
    N.emoji(img, COMET, lx + 230, ly, 26); N.text(img, (lx + 250, ly - 11), 'Top 3 probability', 18, fg)
    d.ellipse([lx + 420, ly - 5, lx + 430, ly + 5], fill=fg)
    N.text(img, (lx + 438, ly - 11), 'Torino', 18, fg)
    N.text(img, (lx + 530, ly - 11), 'Circle radius = size', 18, fg)
    img.save(out)


def impact_date(objs, out, style):
    th = N.Theme(style); fg = th.fg
    L, R, T, B = 200, 1000, 170, 620
    img, d = N.frame(th, 'Impact date vs probability · top 15 by Palermo',
                     '15 objects · probability (left, log) · diameter (right, log) · numbers = Palermo rank', L, R, T, B)
    yrs = [o['year'] for o in objs]; ips = [o['ip'] for o in objs]; dias = [o.get('diam_km', 0.01) for o in objs]
    ax_x = N.Ax(min(yrs) - 5, max(yrs) + 5, L, R, False)
    ax_p = N.Ax(min(ips) / 3, max(ips) * 3, B, T, True)
    ax_d = N.Ax(min(dias) / 2, max(dias) * 2, B, T, True)
    for v in ax_x.ticks():
        x = ax_x.f(v); d.line([x, B, x, B + 8], fill=fg, width=2)
        N.text(img, (x, B + 14), f"{v:.0f}", 20, fg, angle=45, anchor='tr')
    for e in range(-12, 0):
        v = 10 ** e
        if ax_p.lo <= v <= ax_p.hi:
            y = ax_p.f(v); d.line([L - 8, y, L, y], fill=fg, width=2)
            V6.place_rich(img, (L - 12, y), V6.e_parts(v), 20, fg, angle=0, anchor='rm')
    for e in range(-4, 2):
        v = 10 ** e
        if ax_d.lo <= v <= ax_d.hi:
            y = ax_d.f(v); d.line([R, y, R + 8, y], fill=fg, width=2)
            V6.place_rich(img, (R + 12, y), V6.e_parts(v), 20, fg, angle=0, anchor='lm')
    for o in objs:
        x, y = ax_x.f(o['year']), ax_p.f(o['ip'])
        yd = ax_d.f(o.get('diam_km', 0.01))
        d.ellipse([R - 3, yd - 3, R + 3, yd + 3], fill=fg)
        N.text(img, (R - 12, yd), str(o['num']), 16, fg, anchor='rm')
        ch = COMET if o['comet'] else (N.PHA_EMOJI if o.get('pha') else N.ROCK_EMOJI)
        N.emoji(img, ch, x, y, 30)
        N.text(img, (x + 18, y - 26), str(o['num']), 18, fg)
    N.text(img, ((L + R) // 2, B + 150), 'Impact year', 26, fg, anchor='mt')
    N.text(img, (L - 120, (T + B) // 2), 'Impact probability (log)', 24, fg, angle=90, anchor='cc')
    N.text(img, (R + 150, (T + B) // 2), 'Diameter (km, log)', 24, fg, angle=90, anchor='cc')
    lx, ly = 200, 820
    N.emoji(img, N.PHA_EMOJI, lx, ly, 26); N.text(img, (lx + 20, ly - 11), 'PHA', 18, fg)
    N.emoji(img, N.ROCK_EMOJI, lx + 90, ly, 26); N.text(img, (lx + 110, ly - 11), 'Other NEA', 18, fg)
    N.emoji(img, COMET, lx + 230, ly, 26); N.text(img, (lx + 250, ly - 11), 'Top 3 probability', 18, fg)
    img.save(out)


def cum08(rows, out, style, start='2026-11-01', end='2026-11-16'):
    th = N.Theme(style); fg = th.fg
    yel = YELLOW if style == 'dark' else YELLOW_T
    days, d0, d1 = [], dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    while d0 <= d1:
        days.append(d0); d0 += dt.timedelta(days=1)
    seen, seen_p, tot, pha = set(), set(), [], []
    for day in days:
        for r in rows:
            if r['approach_date'] == day.isoformat():
                seen.add(r['neo_id'])
                if r['pha']:
                    seen_p.add(r['neo_id'])
        tot.append(len(seen)); pha.append(len(seen_p))
    L, R, T, B = 200, 1040, 160, 600
    img, d = N.frame(th, 'Cumulative NEAs since first capture',
                     f"{start} to {end} · distinct NEAs by close-approach date · logarithmic scale", L, R, T, B)
    top = max(tot + [1])
    ax_y = N.Ax(1, top * 1.2, B, T, True); ax_x = N.Ax(0, len(days) - 1, L, R, False)
    N.gridlines(img, th, ax_x, ax_y, L, R, T, B)
    for i, day in enumerate(days):
        x = ax_x.f(i); d.line([x, B, x, B + 6], fill=fg, width=2)
        N.text(img, (x + 4, B + 12), day.strftime('%b %d'), 22, fg, angle=45, anchor='tr')
    for v in ax_y.ticks():
        y = ax_y.f(v); d.line([L - 8, y, L, y], fill=fg, width=2)
        N.text(img, (L - 12, y), f"{v:g}", 26, fg, anchor='rm')
    for series, col in ((tot, yel), (pha, ORANGE)):
        pts = [(ax_x.f(i), ax_y.f(max(v, 1))) for i, v in enumerate(series)]
        d.line(pts, fill=col, width=4)
        for x, y in pts:
            d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col, outline=fg)
    N.text(img, ((L + R) // 2, B + 130), 'Close-approach date', 28, fg, anchor='mt')
    N.text(img, (60, (T + B) // 2), 'Cumulative NEAs', 28, fg, angle=90, anchor='cc')
    ly = 820   # moved up three lines from the previous position
    d.rectangle([260, ly - 10, 280, ly + 10], fill=yel)
    N.text(img, (292, ly - 12), f"All NEAs ({tot[-1]})", 22, fg)
    d.rectangle([700, ly - 10, 720, ly + 10], fill=ORANGE)
    N.text(img, (732, ly - 12), f"PHA ({pha[-1]})", 22, fg)
    img.save(out)


def main():
    out_dir = sys.argv[1]; os.makedirs(out_dir, exist_ok=True)
    objs = load_sentry()
    log = N.load_log()
    today = dt.date.today()
    snap = [r for r in log['rows'] if today <= dt.date.fromisoformat(r['approach_date']) <= today + dt.timedelta(days=6)]
    for r in snap:
        r['dmin_km'] = r['diam_min_m'] / 1000; r['dmax_km'] = r['diam_max_m'] / 1000
        r['dmid_km'] = math.sqrt(r['dmin_km'] * r['dmax_km']); r['ld'] = r['miss_ld']
    rows20 = sorted(snap, key=lambda r: r['ld'])[:15]
    V6.fig1(rows20, os.path.join(out_dir, '1-3-distance-velocity-size-log-dark.png'), 'dark')
    V6.fig1(rows20, os.path.join(out_dir, '1-3-distance-velocity-size-log-transparent.png'), 'transparent')
    V6.fig2(rows20, 'dark', os.path.join(out_dir, '2-3-3d-dark.png'))
    V6.fig2(rows20, 'transparent', os.path.join(out_dir, '2-3-3d-transparent.png'))
    V6.fig2(rows20, 'grid', os.path.join(out_dir, '2-3-3d-dark-grid.png'))
    V6.fig4(rows20, os.path.join(out_dir, '3-3-diameter-vs-distance-log-transparent.png'))
    for style in ('dark', 'transparent'):
        impact_dual(objs, os.path.join(out_dir, f'imp1-distance-torino-palermo-{style}.png'), style)
        impact_date(objs, os.path.join(out_dir, f'imp2-date-probability-diameter-{style}.png'), style)
    cum08(log['rows'], os.path.join(out_dir, '08-cumulative-linear-transparent.png'), 'transparent')
    cum08(log['rows'], os.path.join(out_dir, '08-cumulative-linear-dark.png'), 'dark')
    print('\n'.join(sorted(f for f in os.listdir(out_dir) if f.endswith('.png'))))


if __name__ == '__main__':
    main()
