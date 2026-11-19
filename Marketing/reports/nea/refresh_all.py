#!/usr/bin/env python3
"""Refresh the Planetary Defense Daily and Space Luisa home pages from NASA, JPL and MPC data.
Run it several times a day (see run_refresh_loop.sh). Writes into ../home/.

Steps: NeoWs feed -> nea_log.json/.xlsx, MPC recent circulars -> mpec_recent.json (+ JPL flags),
Horizons sky positions -> mpec_sky.json, sub-observer map points -> watch-data.json,
Sentry top 15 -> sentry15.json, charts (nea_charts_v7), then the page tables and lists.
"""
import sys, os, re, json, math, time, html, datetime as dt, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.join(HERE, '..', 'home')
sys.path.insert(0, HERE)
import nea_log as N
import nea_charts_v7 as C7
TODAY = dt.date.today()
NOW = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)


def get_json(u, t=60):
    return json.loads(urllib.request.urlopen(u, timeout=t).read().decode())


def get_text(u, t=60):
    return urllib.request.urlopen(u, timeout=t).read().decode('utf-8', 'ignore')


def log(msg):
    print(f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}] {msg}", flush=True)


# 1. close approaches (NeoWs) -> log
def step_neows():
    feed = N.fetch_feed((TODAY - dt.timedelta(days=7)).isoformat(), (TODAY + dt.timedelta(days=6)).isoformat())
    new = [N.normalize(o, TODAY.isoformat()) for o in feed]
    added = N.append_rows(new)
    N.write_xlsx(sorted(N.load_log()['rows'], key=lambda r: (not r['pha'], r['approach_date'], r['name'])), N.LOG_XLSX)
    log(f"NeoWs: {len(new)} rows, {added} new")


# 2. MPC recent circulars (last 2 days) with JPL flags
def step_mpec():
    raw = get_text('https://minorplanetcenter.net/mpec/RecentMPECs.html')
    text = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', '', raw, flags=re.S)))
    text = re.sub(r'\s+', ' ', text)
    ents = re.findall(r'MPEC (\d{4}-[A-Z]\d+) \((\d{4} \w+ \d+)\) ([^M]+?)(?= MPEC | DAILY| $)', text)
    old = {r['des']: r for r in json.load(open(os.path.join(HERE, 'mpec_recent.json')))} if os.path.exists(os.path.join(HERE, 'mpec_recent.json')) else {}
    recent = []
    for mid, date, des in ents:
        d = dt.datetime.strptime(date, '%Y %B %d').date()
        if d < TODAY - dt.timedelta(days=1) or 'DAILY' in des:
            continue
        r = {'mpec': mid, 'date': str(d), 'des': des.strip()}
        if r['des'] in old and 'neo' in old[r['des']]:
            r.update({k: old[r['des']][k] for k in ('neo', 'pha', 'H', 'discovery_date', 'discovery_site', 'fullname') if k in old[r['des']]})
        else:
            try:
                j = get_json('https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=' + urllib.parse.quote(r['des']) + '&discovery=1&phys-par=1')
                ob = j.get('object') or {}
                r['neo'] = ob.get('neo') in (True, 'Y'); r['pha'] = ob.get('pha') in (True, 'Y'); r['fullname'] = ob.get('fullname')
                disc = j.get('discovery') or {}; r['discovery_date'] = disc.get('date'); r['discovery_site'] = disc.get('location')
                for p in j.get('phys_par', []):
                    if p.get('name') == 'H': r['H'] = float(p['value'])
            except Exception as e:
                r['flags_error'] = str(e)[:60]
            time.sleep(0.2)
        recent.append(r)
    json.dump(recent, open(os.path.join(HERE, 'mpec_recent.json'), 'w'), indent=1)
    log(f"MPC: {len(recent)} designations in the last two days")
    return recent


# 3. sky positions (Horizons) at the current time
def step_sky(recent):
    out = []
    start = NOW.strftime('%Y-%b-%d %H:%M'); stop = (NOW + dt.timedelta(minutes=1)).strftime('%Y-%b-%d %H:%M')
    for r in recent:
        p = {'format': 'json', 'COMMAND': f"'{r['des']};'", 'OBJ_DATA': 'NO', 'MAKE_EPHEM': 'YES', 'EPHEM_TYPE': 'OBSERVER',
             'CENTER': "'500@399'", 'START_TIME': f"'{start}'", 'STOP_TIME': f"'{stop}'", 'STEP_SIZE': "'1 min'",
             'QUANTITIES': "'1'", 'ANG_FORMAT': 'DEG', 'CSV_FORMAT': 'YES'}
        try:
            j = get_json('https://ssd.jpl.nasa.gov/api/horizons.api?' + urllib.parse.urlencode(p))
            soe = j['result'].split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()[0]
            parts = [x.strip() for x in soe.split(',')]
            out.append(dict(r, ra=float(parts[3]), dec=float(parts[4])))
        except Exception:
            pass
        time.sleep(0.3)
    json.dump(out, open(os.path.join(HERE, 'mpec_sky.json'), 'w'), indent=1)
    log(f"sky: {len(out)} positions")
    return out


# 4. world-map points: where each object is overhead now, and the day/night boundary
def gmst_deg(t):
    JD = (t - dt.datetime(2000, 1, 1, 12, tzinfo=dt.timezone.utc)).total_seconds() / 86400 + 2451545.0
    return (280.46061837 + 360.98564736629 * (JD - 2451545.0)) % 360, JD - 2451545.0


def step_watch(sky, sentry_set):
    g, n = gmst_deg(NOW)
    wrap = lambda a: ((a + 180) % 360) - 180
    L = (280.460 + 0.9856474 * n) % 360; gs = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = math.radians(L + 1.915 * math.sin(gs) + 0.020 * math.sin(2 * gs)); eps = math.radians(23.439)
    dec_sun = math.degrees(math.asin(math.sin(eps) * math.sin(lam)))
    ra_sun = math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360
    data = {'time': NOW.strftime('%Y-%m-%d %H:%M UTC'), 'sun': {'lat': dec_sun, 'lon': wrap(ra_sun - g)},
            'pts': [{'des': o['des'], 'mpec': o['mpec'], 'date': o['date'], 'pha': bool(o.get('pha')),
                     'neo': bool(o.get('neo')), 'impact': o['des'] in sentry_set,
                     'lat': o['dec'], 'lon': wrap(o['ra'] - g)} for o in sky]}
    json.dump(data, open(os.path.join(HOME, 'watch-data.json'), 'w'), indent=1)
    return data


# 5. Sentry top 15 by Palermo (JPL), with H, close-approach distance
def step_sentry():
    """Sentry summary table (one row per object, cumulative Palermo and impact probability, impact years as a range); top 15 by cumulative Palermo."""
    sent = get_json('https://ssd-api.jpl.nasa.gov/sentry.api', t=180)['data']
    best = [o for o in sent if o.get('ps_cum') not in (None, '') and o.get('ip') not in (None, '')]
    top = sorted(best, key=lambda o: float(o['ps_cum']), reverse=True)[:15]
    rows = []
    for o in top:
        rng = str(o.get('range') or '')
        y0 = int(rng.split('-')[0]) if rng[:4].isdigit() else None
        info = {'des': o['des'], 'ps': float(o['ps_cum']), 'ts': int(o.get('ts_max') or 0), 'ip': float(o['ip']),
                'date': rng, 'range': rng, 'year': float(y0) if y0 else None, 'dist_au': None, 'H': float(o['h']) if o.get('h') else None,
                'diam_km': float(o['diameter']) if o.get('diameter') else None, 'n_imp': o.get('n_imp'), 'v_inf': o.get('v_inf')}
        try:
            ob = get_json('https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=' + urllib.parse.quote(o['des']))
            info['pha'] = ((ob.get('object') or {}).get('pha') in (True, 'Y'))
        except Exception: pass
        try:
            c = get_json('https://ssd-api.jpl.nasa.gov/cad.api?des=' + urllib.parse.quote(o['des']) + '&date-min=' + TODAY.isoformat() + '&date-max=2200-01-01&dist-max=1')
            d = [float(r[4]) for r in c['data']] if c.get('data') else []
            info['dist_au'] = min(d) if d else None
        except Exception: pass
        if info['diam_km'] is None and info['H'] is not None:
            info['diam_km'] = 1329 / math.sqrt(0.14) * 10 ** (-info['H'] / 5)
        rows.append(info); time.sleep(0.2)
    json.dump(rows, open(os.path.join(HERE, 'sentry15.json'), 'w'), indent=1)
    log(f"Sentry: top {len(rows)} by cumulative Palermo")
    return rows


# 6. charts
def step_charts():
    if os.environ.get('SKIP_CHARTS'):
        log('charts skipped on this runner (macOS fonts are needed); last charts kept')
        return
    import subprocess, tempfile
    out = os.path.join(HERE, '_charts_out')
    subprocess.run([sys.executable, os.path.join(HERE, 'nea_charts_v11.py'), out], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'add_charts_section.py'), out], check=True)
    log('charts (v11) written to home/charts and the Charts section refreshed')


# 7. page content (tables and lists), keeping the approved layout
def e(x): return html.escape(str(x if x is not None else ''))


def dist_txt(r):
    return f"{r['dist_au']*389.17:.1f}" if r.get('dist_au') is not None else '—'


def replace_nth(pattern, repl_list, s, tag):
    matches = list(re.finditer(pattern, s, re.S))
    assert len(matches) >= len(repl_list), f"{tag}: found {len(matches)}"
    out, last = [], 0
    for m, new in zip(matches, repl_list):
        out.append(s[last:m.start()]); out.append(new); last = m.end()
    out.append(s[last:])
    return ''.join(out)


def step_pages(recent_all, sentry_rows, news_pdd, top3_pdd, close_rows):
    # PDD
    p = os.path.join(HOME, 'pdd-home-v8.html'); s = open(p, encoding='utf-8').read()
    top_html = ''.join(
        f'<article class="card">' + (f'<img src="{e(x["art"])}" alt="{e(x.get("art_caption"))}">' if x.get('art') else '<div class="noart">Image pending</div>')
        + f'<h3>{e(x["headline"])}</h3><p>{e(x["dek"])}</p><small>{x["sources"]} sources · {x["facts"]} facts</small></article>' for x in top3_pdd)
    s = re.sub(r'<div class="top3">.*?</div></section>', lambda m: f'<div class="top3">{top_html}</div></section>', s, count=1, flags=re.S)
    close_tb = ''.join(f'<tr><td>{e(r["approach_utc"][5:16])}</td><td class="nw"><a href="{e(r["jpl_url"])}" target="_blank">{e(r["designation"])}</a></td><td class="n">{r["miss_ld"]:.2f}</td><td class="n">{r["diam_min_m"]:.0f}–{r["diam_max_m"]:.0f} m</td></tr>' for r in close_rows)
    sen_tb = ''.join(f'<tr><td class="n">{i+1}</td><td class="nw"><a href="https://cneos.jpl.nasa.gov/sentry/details.html#?des={e(r["des"])}" target="_blank">{e(r["des"])}</a></td><td class="nw">{e(r["date"][:10])}</td><td class="n">{r["ip"]:.1e}</td><td class="n">{r["ps"]:.2f}</td><td class="n">{r["ts"]}</td><td class="n">{dist_txt(r)}</td></tr>' for i, r in enumerate(sentry_rows))
    s = replace_nth(r'<tbody>.*?</tbody>', [f'<tbody>{close_tb}</tbody>', f'<tbody>{sen_tb}</tbody>'], s, 'tbody')
    today_disc = [r for r in recent_all if r['date'] == TODAY.isoformat()]
    disc = ''.join(f'<li><span class="dot"></span><a href="https://minorplanetcenter.net/mpec/RecentMPECs.html" target="_blank">{e(r["des"])}</a> <small>Source: <a href="https://minorplanetcenter.net/mpec/RecentMPECs.html" target="_blank">MPC</a> · MPEC {e(r["mpec"])}</small></li>' for r in today_disc)
    s = re.sub(r'<ul class="disc">.*?</ul>', lambda m: f'<ul class="disc">{disc}</ul>', s, count=1, flags=re.S)
    news = ''.join(f'<li><a href="#">{e(x["headline"])}</a> <small>{x["day"]} · {x["sources"]} sources</small></li>' for x in news_pdd)
    s = re.sub(r'<ul class="news">.*?</ul>', lambda m: f'<ul class="news">{news}</ul>', s, count=1, flags=re.S)
    s = re.sub(r'<p class="updated">.*?</p>', '', s)
    s = re.sub(r'<p style="font-size:12px;color:#a2afc6;padding:0 24px">Updated[^<]*</p>', '', s)
    watch = open(os.path.join(HOME, 'watch-data.json'), encoding='utf-8').read()
    s = re.sub(r'const WATCH=\{.*?\};\n', lambda m: 'const WATCH=' + watch + ';\n', s, count=1, flags=re.S)
    s = s.replace('<footer>', f'<p style="font-size:12px;color:#a2afc6;padding:0 24px">Updated {NOW.strftime("%d %b %Y %H:%M UTC")}</p><footer>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    # Space Luisa: the recent list and the watch data
    p = os.path.join(HOME, 'sl-asteroids-today-v8.html'); s = open(p, encoding='utf-8').read()
    recent2 = [r for r in recent_all if r['date'] >= (TODAY - dt.timedelta(days=1)).isoformat()]
    lst = ''.join(f'<li><span class="dot"></span><a href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr={e(r["des"].replace(" ","%20"))}" target="_blank">{e(r["des"])}</a> <small>{e(r["date"])} · Source: <a href="https://minorplanetcenter.net/mpec/RecentMPECs.html" target="_blank">MPC</a> · MPEC {e(r["mpec"])}</small></li>' for r in sorted(recent2, key=lambda r: (r['date'], r['des']), reverse=True))
    s = re.sub(r'<ul class="disc">.*?</ul>', lambda m: f'<ul class="disc">{lst}</ul>', s, count=1, flags=re.S)
    watch = open(os.path.join(HOME, 'watch-data.json'), encoding='utf-8').read()
    s = re.sub(r'const WATCH=\{.*?\};\n', lambda m: 'const WATCH=' + watch + ';\n', s, count=1, flags=re.S)
    s = re.sub(r'Updated [^<]*UTC', '', s)
    s = s.replace('<details class="fold" id="asteroids-today">', f'<p style="font-size:12px;color:#a2afc6;margin:0 0 8px">Updated {NOW.strftime("%d %b %Y %H:%M UTC")} · refreshed several times a day</p><details class="fold" id="asteroids-today">', 1)
    open(p, 'w', encoding='utf-8').write(s)
    log('pages updated')


def step_pdd_content():
    sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'loop'))
    import nrfpdd
    st = nrfpdd.call('list_stories', {'status': 'air', 'limit': 100})['stories']
    cand = [x for x in st if x['day'] >= (TODAY - dt.timedelta(days=1)).isoformat()]
    top3 = sorted(cand, key=lambda x: (x['sources'], x['facts']), reverse=True)[:3]
    ids = {t['id'] for t in top3}
    others = [x for x in sorted(st, key=lambda x: x['published_at'], reverse=True) if x['id'] not in ids][:10]
    return top3, others


def main():
    os.makedirs(HOME, exist_ok=True)
    step_neows()
    recent = step_mpec()
    sky = step_sky(recent)
    sentry_rows = step_sentry()
    watch = step_watch(sky, {r['des'] for r in sentry_rows})
    step_charts()
    log_rows = N.load_log()['rows']
    today = TODAY
    close = sorted([r for r in log_rows if today <= dt.date.fromisoformat(r['approach_date']) <= today + dt.timedelta(days=6)], key=lambda r: r['miss_ld'])[:15]
    try:
        top3, others = step_pdd_content()
    except Exception as ex:
        log(f"PDD stories not refreshed: {ex}")
        top3, others = [], []
    if top3:
        step_pages(recent, sentry_rows, others, top3, close)
    else:
        log('kept the previous page content (no story data)')
    log('done')


if __name__ == '__main__':
    main()
