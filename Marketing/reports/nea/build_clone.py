#!/usr/bin/env python3
"""Clone of the live Planetary Defense Daily front page with our two Space Watch blocks (Close approaches, Impact risk) in place of the paper's own Space watch band.
Fetches the live page, makes its links absolute (so story pages, pictures, search and the newsletter stay on Newsroom Floor), swaps the band, and writes site/index.html.
Usage: build_clone.py [OUT_DIR]   (default ../../../site)"""
import sys, os, re, json, shutil, urllib.request, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'site'); os.makedirs(os.path.join(OUT, 'charts'), exist_ok=True)
LIVE = 'https://planetary-defense-daily.newsroomfloor.com'
mock = open(os.path.join(HERE, '..', 'home', 'pdd-home-v8.html'), encoding='utf-8').read()
live = urllib.request.urlopen(urllib.request.Request(LIVE + '/', headers={'User-Agent': 'Mozilla/5.0 (clone-builder)'}), timeout=60).read().decode('utf-8')
# --- our band: the Space Watch section of the mock-up
a = mock.index('<section id="space-watch">'); b = mock.index('</section>\n<section><p class="kicker">Adver', a) if '</section>\n<section><p class="kicker">Adver' in mock[a:] else mock.index('</section>', a)
band = mock[a:b] + '</section>'
import html as _h, math
log = json.load(open(os.path.join(HERE, 'nea_log.json')))
today = datetime.date.today()
rows = [r for r in log['rows'] if today <= datetime.date.fromisoformat(r['approach_date']) <= today + datetime.timedelta(days=6)]
rows = sorted(rows, key=lambda r: r['miss_ld'])[:15]
def fdt(r):
    try: d = datetime.datetime.strptime(r['approach_utc'], '%Y-%b-%d %H:%M'); return d.strftime('%b-%d %H:%M'), d.isoformat()
    except Exception: return r['approach_utc'], r['approach_utc']
tr = ''
for r in rows:
    t, iso = fdt(r); dmid = math.sqrt(r['diam_min_m'] * r['diam_max_m']) / 1000; fs = datetime.date.fromisoformat(r['first_seen'])
    tr += (f'<tr><td data-v="{iso}">{t}</td><td class="nw"><a href="{_h.escape(r["jpl_url"])}" target="_blank" rel="noopener">{_h.escape(r["designation"])}</a></td>'
           f'<td class="n" data-v="{r["miss_ld"]:.3f}">{r["miss_ld"]:.2f}</td><td class="n" data-v="{dmid:.4f}">{r["diam_min_m"]:.0f}–{r["diam_max_m"]:.0f}</td>'
           f'<td class="n" data-v="{r["H_mag"]}">{float(r["H_mag"]):.1f}</td><td data-v="{r["first_seen"]}">{fs.strftime("%b-%d")}</td><td class="n" data-v="{r["rel_velocity_kms"]:.3f}">{r["rel_velocity_kms"]:.1f}</td></tr>')
head1 = '<thead><tr><th>Closest (UTC)</th><th>Object (JPL)</th><th class="n">LD</th><th class="n">Size (m)</th><th class="n">Abs. mag. (H)</th><th>First seen</th><th class="n">Velocity (km/s)</th></tr></thead>'
sen = json.load(open(os.path.join(HERE, 'sentry15.json'))); tr2 = ''
for i, r in enumerate(sen, 1):
    ld = '—' if r.get('dist_au') is None else f"{r['dist_au'] * 389.17:.1f}"
    rg = str(r.get('range') or int(r['year'])).replace('-', '–'); a_, _, b_ = rg.partition('–'); rg = a_ if (not b_ or a_ == b_) else rg
    tr2 += (f'<tr><td class="n" data-v="{i}">{i}</td><td class="nw" data-v="{_h.escape(r["des"])}"><a href="https://cneos.jpl.nasa.gov/sentry/details.html#?des={_h.escape(r["des"])}" target="_blank" rel="noopener">{_h.escape(r["des"])}</a></td>'
            f'<td class="nw" data-v="{int(r["year"])}">{rg}</td><td class="n" data-v="{r["ip"]:.3e}">{r["ip"]:.1e}</td><td class="n" data-v="{r["ps"]}">{r["ps"]:.2f}</td><td class="n" data-v="{r["ts"]}">{r["ts"]}</td><td class="n" data-v="{(r["dist_au"] or 0) * 389.17:.2f}">{ld}</td></tr>')
head2 = '<thead><tr><th class="n">#</th><th>Object</th><th>Impact year(s)</th><th class="n">Prob.</th><th class="n">Palermo</th><th class="n">Torino</th><th class="n">LD</th></tr></thead>'
tabs = list(re.finditer(r'<table class="sortable">.*?</table>', band, flags=re.S)); assert len(tabs) == 2
band = band[:tabs[0].start()] + '<table class="sortable">' + head1 + '<tbody>' + tr + '</tbody></table>' + band[tabs[0].end():tabs[1].start()] + '<table class="sortable">' + head2 + '<tbody>' + tr2 + '</tbody></table>' + band[tabs[1].end():]
band = re.sub(r'Last updated: [^.]*\.', 'Last updated: ' + datetime.datetime.utcnow().strftime('%d %b %Y, %H:%M UTC') + '.', band, count=1)
# --- side panel "Asteroids today": map, discovered list, rare finds, cumulative carousel, ads
wd = json.load(open(os.path.join(HERE, '..', 'home', 'watch-data.json')))
latest = max(p_['date'] for p_ in wd['pts']); newest = [p_ for p_ in wd['pts'] if p_['date'] == latest]
disc = ''.join(f'<li><span class="dot"></span><a href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr={_h.escape(p_["des"])}" target="_blank" rel="noopener">{_h.escape(p_["des"])}</a> <small><a href="https://minorplanetcenter.net/mpec/RecentMPECs.html" target="_blank" rel="noopener">MPC</a> · MPEC {_h.escape(p_["mpec"])}</small></li>' for p_ in newest)
aside = re.search(r'<aside class="side">(.*?)</aside>', mock, flags=re.S).group(1)
aside = re.sub(r'(<h3>Discovered today</h3>\s*<p[^>]*>).*?(</p>)', lambda m: m.group(1) + 'Designations announced on ' + datetime.date.fromisoformat(latest).strftime('%d %b %Y') + ' (MPC circulars).' + m.group(2), aside, count=1, flags=re.S)
aside = re.sub(r'<ul class="disc">.*?</ul>', '<ul class="disc">' + disc + '</ul>', aside, count=1, flags=re.S)
cut = aside.index('<div style="margin:0 0 16px">')
left, right = aside[:cut], aside[cut:]
band += ('<section id="asteroids-today"><p class="kicker">Asteroids today</p><h2>ASTEROIDS TODAY</h2><div class="sidegrid"><div>' + left + '</div><div>' + right + '</div></div></section>')
# --- css: only what the band needs, every rule scoped to #swx so the paper's own styles are untouched
def styles(ident):
    m = re.search(r'<style id="%s">(.*?)</style>' % ident, mock, flags=re.S); return m.group(1) if m else ''
base = re.search(r'<style>(.*?)</style>', mock, flags=re.S).group(1)
def rules(css):
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0: break
        depth, k = 1, j + 1
        while k < n and depth:
            depth += (css[k] == '{') - (css[k] == '}'); k += 1
        out.append((css[i:j].strip(), css[j + 1:k - 1])); i = k
    return out
def scope(css, keep=None):
    res = ''
    for sel, body in rules(css):
        if sel.startswith('@media'): res += sel + '{' + scope(body, keep) + '}'; continue
        if sel.startswith('@'): continue
        sels = [x.strip() for x in sel.split(',')]
        if keep: sels = [x for x in sels if re.search(keep, x)]
        if not sels: continue
        sels = [x if re.match(r'^(#mlb|#ocard|#clb|\.pcard|\.chs)', x) else ('#swx' if x in (':root', 'body') else '#swx ' + x) for x in sels]
        res += ','.join(sels) + '{' + body + '}'
    return res
vars_ = '#swx{--bg:#0b1526;--card:#16233a;--card2:#121e33;--ink:#eef2fa;--ink2:#cbd5e6;--dim:#a2afc6;--rule:#2c3b57;--acc:#de7c7c;--ai:#8ab7ea;color:var(--ink2);font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:21px;max-width:1100px;margin:0 auto;padding:8px 16px 24px}'
KEEP = r'^(\.side|\.disc|\.dot|\.sads|\.sad|\.spons|\.aff|\.banner|\.ad-img|\.mb|\.ic|\.sidegrid|\.map-key|details|summary|\.dd|\.tw|table|th|td|\.carousel|\.slides|\.slide|\.ctrl|\.kicker|h2|\.btn|\.cpic|\.cfig|\.capd|\.capwide|\.tk|\.td|\.big|\.pos|section|a|img|\.nw|\.n|p)'
css = vars_ + scope(base, KEEP) + scope(styles('charts-css'), r'^(\.cpic|\.cfig|\.cpics)') + scope(styles('v9-css')) + scope(styles('v10-css')) + scope(styles('v11-css'))
css += styles('charts-css')                                           # lightbox and object cards (#clb, .chs, .pcard) are page-level
css = css.replace('#swx #swx', '#swx') + '#swx .sidegrid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:22px}@media(max-width:900px){#swx .sidegrid{grid-template-columns:1fr}}#swx .side h3{font:700 24px "Playfair Display",Georgia,serif;color:#eef2fa;margin:14px 0 8px}#swx .disc{list-style:none;padding:0;margin:0 0 16px}#swx .disc li{padding:7px 0;border-bottom:1px solid #2c3b57}#swx .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#8ab7ea;margin-right:7px}'
css += '#swx h2{font:900 30px "Playfair Display",Georgia,serif;color:#eef2fa;border-bottom:1px solid #2c3b57;padding-bottom:8px;margin:0 0 14px}#swx .kicker{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#de7c7c;margin:0 0 8px}'
# --- js: carousels, sorting, chart lightbox
def script(ident):
    m = re.search(r'<script id="%s">(.*?)</script>' % ident, mock, flags=re.S); return m.group(1) if m else ''
carousel_js = re.search(r'<script>\s*(function show\(c,i\).*?)</script>', mock, flags=re.S).group(1)
mapjs = re.search(r'<script>\s*(const WATCH=.*?)</script>', mock, flags=re.S).group(1)
mapjs = re.sub(r'const WATCH=\{.*?\n\};?\n', lambda m: 'const WATCH=' + json.dumps(wd) + ';\n', mapjs, count=1, flags=re.S)
js = carousel_js + '\n' + script('v10-js') + '\n' + script('charts-js')
inject_libs = '<script src="d3.min.js"></script><script src="topojson-client.min.js"></script>'
mapblock = '<script id="swx-map">' + mapjs + '</script><script id="swx-v9">' + script('v9-js') + '</script>'
lb2 = '<div id="mlb" onclick="if(event.target===this)this.classList.remove(\'on\')"></div><div id="ocard"></div>'
lb = '<div id="clb" role="dialog" aria-label="Chart, enlarged"><div id="clbi"></div></div>'
inject_head = '<style id="swx-css">' + css + '</style>'
inject_body = lb + lb2 + inject_libs + '<script id="swx-js">' + js + '</script>' + mapblock
# --- the live page with absolute links
def absolutize(h):
    h = re.sub(r'''((?:src|href|action|poster|data-cb|data-src)=")/(?!/)''', r'\1' + LIVE + '/', h)
    h = re.sub(r'''((?:src|href|action)=')/(?!/)''', r"\1" + LIVE + '/', h)
    h = re.sub(r'''url\((['"]?)/(?!/)''', r'url(\1' + LIVE + '/', h)
    h = re.sub(r'''(fetch\(['"])/''', r'\1' + LIVE + '/', h)
    h = re.sub(r'''srcset="([^"]+)"''', lambda m: 'srcset="' + re.sub(r'(^|,\s*)/(?!/)', lambda x: x.group(1) + LIVE + '/', m.group(1)) + '"', h)
    return h
page = absolutize(live)
i = page.index('<section class="pspace"'); j = page.index('</section>', i) + len('</section>')
page = page[:i] + '<div id="swx">' + band + '</div>' + page[j:]
page = page.replace('</head>', inject_head + '</head>', 1)
k = page.rindex('</body>'); page = page[:k] + inject_body + page[k:]
page = page.replace('<head>', '<head><base target="_self">', 1) if False else page
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
for f in os.listdir(os.path.join(HERE, '..', 'home', 'charts')):
    if f.endswith('.png'): shutil.copy(os.path.join(HERE, '..', 'home', 'charts', f), os.path.join(OUT, 'charts', f))
for f_ in ('d3.min.js', 'topojson-client.min.js'): shutil.copy(os.path.join(HERE, '..', 'home', f_), os.path.join(OUT, f_))
print('clone written', len(page), 'bytes;', datetime.datetime.utcnow().isoformat(timespec='minutes'), 'UTC')
