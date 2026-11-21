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
def etype(p_): return 'Atmospheric entry' if p_.get('impact') else ('Potentially hazardous (PHA)' if p_.get('pha') else 'Near-Earth object')
drows = ''.join(f'<tr class="dr"><td class="nw" data-v="{_h.escape(p_["des"])}"><a href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr={_h.escape(p_["des"])}" target="_blank" rel="noopener">{_h.escape(p_["des"])}</a></td><td data-v="{_h.escape(etype(p_))}">{etype(p_)}</td><td data-v="{p_["date"]}">{datetime.date.fromisoformat(p_["date"]).strftime("%b-%d")}</td><td data-v="{_h.escape(p_["mpec"])}">{_h.escape(p_["mpec"])}</td><td class="n" data-v="{p_["lat"]:.3f}">{p_["lat"]:.1f}°, {p_["lon"]:.1f}°</td></tr>' for p_ in sorted(wd['pts'], key=lambda q: q['date'], reverse=True))
dnote = f'<p class="td">Designations announced in the Minor Planet Center’s circulars (MPECs), located with JPL data; last updated {_h.escape(wd["time"])}, refreshed automatically every 8 hours. Click a column heading to sort.</p>'
dtab = dnote + '<div class="tw"><table class="sortable dtab"><thead><tr><th>Discovered</th><th>Type</th><th>Announced</th><th>MPEC</th><th class="n">Over now</th></tr></thead><tbody>' + drows + '</tbody></table></div>'
aside = re.search(r'<aside class="side">(.*?)</aside>', mock, flags=re.S).group(1)
mapbit = aside[:aside.index('<h3>Discovered today</h3>')]
cumcar = re.search(r'<div class="carousel" data-carousel data-auto>.*?<div class="ctrl">.*?</div></div>', aside, flags=re.S).group(0)
rare = aside[aside.index('<div style="margin:0 0 16px">'):aside.index('<h3>Cumulative NEAs</h3>')] if '<div style="margin:0 0 16px">' in aside else ''
ads = aside[aside.index('<div class="sads">'):]
rare_img = re.search(r'<img class="ad-img" src="([^"]+)"', rare).group(1) if rare else ''
os.makedirs(os.path.join(OUT, 'img'), exist_ok=True); shutil.copy(os.path.join(HERE, '..', 'home', 'ad-images', 'nrf-icon.png'), os.path.join(OUT, 'img', 'nrf-icon.png'))
XSVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M18.2 2H21l-6.5 7.4L22 22h-6l-4.7-6.1L5.8 22H3l7-8L2 2h6.1l4.2 5.6L18.2 2zm-1 18h1.6L7 3.8H5.3L17.2 20z"/></svg>'
tiles = [('<img src="' + rare_img + '" alt="Rare finds">', 'Rare finds', 'Hand-picked space finds.', 'https://relics.luisafernanda.space/', 'Shop Rare finds', 'Sponsored · affiliate link'),
         ('<img src="' + LIVE + '/logo/planetary-defense-daily/dark" alt="Planetary Defense Daily">', 'Subscribe', 'The daily briefing in your inbox.', LIVE + '/#subscribe', 'Subscribe', 'Ad'),
         ('<img src="img/nrf-icon.png" alt="Newsroom Floor">', 'Newsroom Floor', 'Build and check your own AI newspaper.', 'https://newsroomfloor.com', 'Visit Newsroom Floor', 'Ad'),
         ('<span class="xl">' + XSVG + '</span>', 'Follow us on X', 'New stories and charts as they land.', 'https://x.com/newtons_in_laws', 'Follow @newtons_in_laws', 'Ad')]
ad4 = '<div class="ad4">' + ''.join(f'<a class="tile" href="{h}" target="_blank" rel="noopener"><span class="tg">{tg}</span><span class="ti">{im}</span><b>{t}</b><span class="tt">{tx}</span><span class="tb">{cta}</span></a>' for im, t, tx, h, cta, tg in tiles) + '</div>'
astblock = ('<details><summary>ASTEROIDS TODAY</summary>'
            '<div class="dd2 ast"><div>' + mapbit + '</div><div>' + dtab + '</div></div>'
            '<div class="dd2 cum"><div class="capwide cap-open"></div><div>' + cumcar + '</div></div>'
            + ad4 + '</details>')
# --- Close approaches: chart caption right under the chart (a closed dropdown, title and one-liner on the same line, max 17 lines), table as a closed dropdown with its title
ci = band.index('<details><summary>CLOSE APPROACHES'); cj = band.index('<details><summary>IMPACT RISK')
blk = band[ci:cj]
blk = blk.replace('<div class="capwide"></div>', '', 1)
blk = re.sub(r'(<div class="ctrl">.*?</div></div>)(</div>)', r'\1<div class="capwide cap-left"></div>\2', blk, count=1, flags=re.S)
blk = re.sub(r'<figcaption><b>([^<]*)</b><details class="capd"><summary>(.*?)</summary>', r'<figcaption><details class="capd"><summary><span class="stext"><b class="ct1">\1</b> \2</span></summary>', blk, flags=re.S)
m = re.search(r'<p class="tk">(.*?)</p>(<p class="td">.*?</p>)(<div class="tw">.*?</div>)', blk, flags=re.S)
blk = blk[:m.start()] + '<div class="ca-desc"><p class="tk">' + m.group(1) + '</p>' + m.group(2) + '</div><details class="tdd"><summary><span class="stext"><b class="ct1">Table:</b> the 15 closest asteroids, next 7 days</span></summary>' + m.group(3) + '</details>' + blk[m.end():]
blk = blk.replace('<div class="dd2">', '<div class="dd2 ca">', 1)
band = band[:ci] + blk + band[cj:]
# --- Impact risk: same treatment (description kept + 2 more lines, table as a closed dropdown with its title, chart caption under the chart)
ii = band.index('<details><summary>IMPACT RISK'); tail = '</section>'
blk2 = band[ii:band.rindex(tail)]
blk2 = blk2.replace('<div class="capwide"></div>', '', 1)
blk2 = re.sub(r'(<div class="ctrl">.*?</div></div>)(</div>)', r'\1<div class="capwide cap-left"></div>\2', blk2, count=1, flags=re.S)
blk2 = re.sub(r'<figcaption><b>([^<]*)</b><details class="capd"><summary>(.*?)</summary>', r'<figcaption><details class="capd"><summary><span class="stext"><b class="ct1">\1</b> \2</span></summary>', blk2, flags=re.S)
m2 = re.search(r'(<p class="td">.*?)(</p>)(<div class="tw">.*?</div>)', blk2, flags=re.S)
extra = ' The list runs from the highest cumulative Palermo value down, and “Impact year(s)” is the span of years in which Sentry finds possible impacts for each object. Prob. adds up the chance of all those possible impacts, and LD is how close the object passes Earth, from NASA/JPL CNEOS.'
blk2 = blk2[:m2.start()] + '<div class="ca-desc">' + m2.group(1) + extra + m2.group(2) + '</div><details class="tdd"><summary><span class="stext"><b class="ct1">Table:</b> the 15 objects with the highest impact risk</span></summary>' + m2.group(3) + '</details>' + blk2[m2.end():]
blk2 = blk2.replace('<div class="dd2 big">', '<div class="dd2 big ca ci">', 1)
band = band[:ii] + blk2 + band[band.rindex(tail):]
band = band.replace('<details><summary>CLOSE APPROACHES', astblock + '<details><summary>CLOSE APPROACHES', 1)
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
css = css.replace('5em', '3.5em').replace('#swx #swx', '#swx') + '#swx .cap-left{grid-column:auto!important;border-top:0!important;padding-top:10px;max-height:calc(17 * 1.55 * 17px);overflow-y:auto}#swx .capd>summary{font-size:17px!important;line-height:1.55}#swx .capd>summary b.ct1{font-size:20px;color:#eef2fa}#swx .dd2 .slide figcaption{display:none}#swx .dd2.ca>div{display:contents}#swx .dd2.ca .carousel{grid-column:1;grid-row:1;align-self:start}#swx .dd2.ca .cap-left{grid-column:1;grid-row:2}#swx .dd2.ca .ca-desc{grid-column:2;grid-row:1}#swx .dd2.ca details.tdd{grid-column:2;grid-row:2;align-self:start}#swx .dd2.ca .cap-left{align-self:start;padding-top:0!important}#swx .dd2.ca details.tdd b.ct1{font-size:20px;color:#eef2fa}#swx .dd2.ca.ci .ca-desc{grid-column:1;grid-row:1}#swx .dd2.ca.ci details.tdd{grid-column:1;grid-row:2}#swx .dd2.ca.ci .carousel{grid-column:2;grid-row:1}#swx .dd2.ca.ci .cap-left{grid-column:2;grid-row:2}#swx .dd2.ca details.tdd,#swx .dd2.ca .capd{margin:0;background:none;border:0;border-top:1px solid #2c3b57;border-radius:0}#swx .dd2.ca .cap-left{max-height:none;overflow:visible}#swx .dd2.ca .cap-left .capd{max-height:calc(17 * 1.55 * 17px);overflow-y:auto}#swx .dd2.ca summary{display:flex!important;justify-content:space-between;align-items:flex-start;gap:14px;padding:12px 0!important;font-size:17px!important;line-height:1.55!important;letter-spacing:0!important;text-transform:none!important;font-weight:400!important;color:#cbd5e6!important;cursor:pointer}#swx .dd2.ca summary::after{content:"+"!important;float:none!important;font-size:30px!important;line-height:.9!important;color:#de7c7c!important;flex:0 0 auto}#swx .dd2.ca details[open]>summary::after{content:"\\2212"!important}#swx .dd2.ca details.tdd .tw{padding:0 0 12px}#swx details.tdd>summary{padding:12px 14px!important;letter-spacing:0!important;text-transform:none!important}#swx details.tdd>summary{display:flex!important;justify-content:space-between;align-items:center;gap:12px}#swx details.tdd>summary::after{font-size:1.6em;line-height:.5;float:none}#swx details.tdd .tk{font:900 26px/1.1 "Playfair Display",Georgia,serif;color:#de7c7c}#swx details.tdd .tsub{display:block;font-size:15px;font-weight:400;color:#a2afc6;margin-top:2px}#swx details.tdd .td,#swx details.tdd .tw{padding:0 14px 14px}#swx .dd2 .ctrl button{font-size:28px!important;padding:0 18px 4px!important;border-width:1px!important}#swx .dd2 .ctrl .pos{font-size:22px!important}#swx .ad4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;padding:0 16px 16px}@media(max-width:900px){#swx .ad4{grid-template-columns:repeat(2,minmax(0,1fr))}}#swx .ad4 .tile{position:relative;display:flex;flex-direction:column;align-items:center;text-align:center;gap:8px;background:#16233a;border:1px solid #2c3b57;border-radius:6px;padding:26px 12px 14px;text-decoration:none;color:#cbd5e6}#swx .ad4 .tile:hover{border-color:#de7c7c}#swx .ad4 .tg{position:absolute;top:6px;right:10px;font-size:11px;font-style:italic;color:#8d98ad}#swx .ad4 .ti{display:flex;align-items:center;justify-content:center;height:84px}#swx .ad4 .ti img{max-height:84px;max-width:100%;width:auto;border-radius:10px;object-fit:contain}#swx .ad4 .xl{width:84px;height:84px;border-radius:14px;background:#000;color:#fff;display:flex;align-items:center;justify-content:center}#swx .ad4 .xl svg{width:44px;height:44px}#swx .ad4 b{font:700 20px "Playfair Display",Georgia,serif;color:#eef2fa}#swx .ad4 .tt{font-size:15px;line-height:1.35}#swx .ad4 .tb{background:#de7c7c;color:#0b1526;font-weight:700;font-size:14px;padding:7px 12px;border-radius:4px}#swx .dd2.cum .capwide{grid-column:auto;border-top:0;padding-top:0}#swx .dd2.cum .capwide>b:first-child{font-size:24px;display:block;margin-bottom:6px}#swx .dd2.cum .capwide .capd b{font-size:inherit}#swx .dd2.cum .capwide summary{display:none}#swx .dd2.cum .capwide .capd[open]>summary{display:none}#swx .dtab td,#swx .dtab th{font-size:15px}#swx .sidegrid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:22px}@media(max-width:900px){#swx .sidegrid{grid-template-columns:1fr}}#swx .side h3{font:700 24px "Playfair Display",Georgia,serif;color:#eef2fa;margin:14px 0 8px}#swx .disc{list-style:none;padding:0;margin:0 0 16px}#swx .disc li{padding:7px 0;border-bottom:1px solid #2c3b57}#swx .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#8ab7ea;margin-right:7px}'
css += '#swx h2{font:900 30px "Playfair Display",Georgia,serif;color:#eef2fa;border-bottom:1px solid #2c3b57;padding-bottom:8px;margin:0 0 14px}#swx .kicker{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#de7c7c;margin:0 0 8px}'
# --- js: carousels, sorting, chart lightbox
def script(ident):
    m = re.search(r'<script id="%s">(.*?)</script>' % ident, mock, flags=re.S); return m.group(1) if m else ''
carousel_js = re.search(r'<script>\s*(function show\(c,i\).*?)</script>', mock, flags=re.S).group(1)
mapjs = re.search(r'<script>\s*(const WATCH=.*?)</script>', mock, flags=re.S).group(1)
mapjs = re.sub(r'const WATCH=\{.*?\n\};?\n', lambda m: 'const WATCH=' + json.dumps(wd) + ';\n', mapjs, count=1, flags=re.S)
carousel_js = carousel_js.replace('cw.innerHTML=fc.innerHTML}}', 'cw.innerHTML=fc.innerHTML;if(cw.classList.contains("cap-open")){var dd=cw.querySelector("details");if(dd)dd.open=true}}}')
js = carousel_js + '\n' + script('v10-js') + '\n' + script('charts-js')
inject_libs = '<script src="d3.min.js"></script><script src="topojson-client.min.js"></script>'
v9 = script('v9-js').replace(".disc li", ".disc li,.dtab tr.dr").replace('7000', '10000')
mapblock = '<script id="swx-map">' + mapjs + '</script><script id="swx-v9">' + v9 + '</script>'
lb2 = '<div id="mlb" onclick="if(event.target===this)this.classList.remove(\'on\')"></div><div id="ocard"></div>'
lb = '<div id="clb" role="dialog" aria-label="Chart, enlarged"><div id="clbi"></div></div>'

css += ('@media(max-width:760px){'
  '#swx{font-size:17px!important;padding:6px 10px 18px!important}'
  '#swx .dd2,#swx .dd2.big,#swx .dd2.ca,#swx .dd2.ci,#swx .dd2.ast,#swx .dd2.cum,#swx .sidegrid{grid-template-columns:minmax(0,1fr)!important;gap:12px!important;padding:0 10px 12px!important}'
  '#swx .dd2.ca .carousel,#swx .dd2.ca .cap-left,#swx .dd2.ca .ca-desc,#swx .dd2.ca details.tdd,#swx .dd2.ca.ci .carousel,#swx .dd2.ca.ci .cap-left,#swx .dd2.ca.ci .ca-desc,#swx .dd2.ca.ci details.tdd{grid-column:1!important;grid-row:auto!important}'
  '#swx .dd2.cum .capwide{order:2}'
  '#swx .ad4{grid-template-columns:minmax(0,1fr)!important;padding:0 10px 12px!important}'
  '#swx #space-watch>details>summary,#swx details>summary{font-size:15px!important;letter-spacing:.06em!important;padding:12px 12px!important}'
  '#swx #space-watch>details>summary::after{font-size:2.4em!important}'
  '#swx h2{font-size:24px!important}'
  '#swx .tk{font-size:22px!important}'
  '#swx .td,#swx .dd2.big p,#swx .dd2.big .ca-desc p{font-size:15px!important;line-height:1.5!important}'
  '#clb{overflow:auto!important;align-items:flex-start!important;justify-content:flex-start!important;padding:8px!important}#clbi{width:900px!important;max-width:none!important;flex:0 0 auto}'
  '#swx .tw{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}'
  '#swx table.sortable th,#swx table.sortable td{font-size:13px!important;padding:5px 5px!important;white-space:nowrap}'
  '#swx .dd2 .ctrl button{font-size:24px!important;padding:0 16px 3px!important}'
  '#swx .dd2 .ctrl .pos{font-size:18px!important}'
  '#swx .capd>summary{font-size:15px!important}#swx .capd>summary b.ct1{font-size:17px!important}'
  '#swx .dd2.cum .capwide>b:first-child{font-size:19px!important}'
  '#swx .side h3,#swx .dd2.ast h3{font-size:20px!important}'
  '#swx .mb{float:none!important;display:inline-block;margin:4px 0}'
  '#swx #pdd-map{height:auto!important}'
  '#swx .ad4 .tile{flex-direction:row;text-align:left;align-items:center;flex-wrap:wrap;padding:22px 12px 12px}'
  '#swx .ad4 .ti{height:64px;flex:0 0 64px}#swx .ad4 .ti img,#swx .ad4 .xl{max-height:64px;width:64px;height:64px}'
  '#swx .ad4 b{flex:1 1 calc(100% - 80px)}#swx .ad4 .tt{flex:1 1 100%}'
  '}')
# --- sizes: every font 2 pt (2.67 px) smaller, and the band wider (almost edge to edge)
def _px(m): return m.group(1) + '%.1fpx' % max(9.0, float(m.group(2)) - 2.67)
css = re.sub(r'(font-size:)(\d+(?:\.\d+)?)px', _px, css)
css = re.sub(r'(font:(?:\s*(?:italic|normal|bold|\d{3}))*\s*)(\d+(?:\.\d+)?)px', _px, css)
css += '#swx{box-sizing:border-box;width:min(1560px,97vw)!important;max-width:none!important;position:relative;left:50%;transform:translateX(-50%);font-size:18.3px!important}'
if os.environ.get('PREVIEW_OPEN'): band = band.replace('<details', '<details open')
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
