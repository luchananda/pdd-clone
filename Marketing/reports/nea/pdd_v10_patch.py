#!/usr/bin/env python3
"""PDD mock-up v10 patch (run ONCE on pdd-home-v8.html): +3 pt text everywhere (except the footer bar), Space Watch closed on load with a 5x toggle,
sortable tables, the close-approach table with H, first seen and velocity plus its heading and description, full-width captions, bigger carousel controls."""
import re, os, sys, json, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import nea_charts_v11 as M
p = os.path.join(HERE, '..', 'home', 'pdd-home-v8.html'); s = open(p, encoding='utf-8').read()
assert 'id="v10-css"' not in s, 'already patched'
# 1. +4 px (= 3 pt) on every font size in the CSS and inline styles; the footer bar (v9c-css) keeps the size the owner chose
keep = re.search(r'<style id="v9c-css">.*?</style>', s, flags=re.S).group(0); s = s.replace(keep, '@@KEEP@@')
def bump_css(m):
    t = m.group(0)
    t = re.sub(r'font-size:(\d+(?:\.\d+)?)px', lambda x: f'font-size:{float(x.group(1)) + 4:g}px', t)
    t = re.sub(r'(font:[^;}"]*?)(\d+(?:\.\d+)?)px', lambda x: f'{x.group(1)}{float(x.group(2)) + 4:g}px', t)
    return t
s = re.sub(r'<style[^>]*>.*?</style>', bump_css, s, flags=re.S)
s = re.sub(r'style="[^"]*"', lambda m: re.sub(r'font-size:(\d+(?:\.\d+)?)px', lambda x: f'font-size:{float(x.group(1)) + 4:g}px', m.group(0)), s)
s = s.replace('@@KEEP@@', keep)
# 2. Space Watch closed on load
s = s.replace('<details open><summary>CLOSE APPROACHES', '<details><summary>CLOSE APPROACHES').replace('<details open><summary>IMPACT RISK', '<details><summary>IMPACT RISK')
# 3. close-approach table: + absolute magnitude, first seen, velocity; heading and description
rows, logd = M.data_rows(); rows = sorted(rows, key=lambda r: r['ld'])
upd = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(HERE, 'nea_log.json')), datetime.timezone.utc).strftime('%d %b %Y, %H:%M UTC')
def fdate(r):
    u = r.get('approach_utc') or r.get('approach_date') or ''
    try: d = datetime.datetime.fromisoformat(str(u).replace('Z', '+00:00')); return d.strftime('%b-%d %H:%M'), d.isoformat()
    except Exception: return str(u)[:16], str(u)
tr = ''
for r in rows:
    t, iso = fdate(r)
    tr += (f'<tr><td data-v="{iso}">{t}</td><td class="nw"><a href="{html.escape(r["jpl_url"])}" target="_blank" rel="noopener">{html.escape(r["designation"])}</a></td>'
           f'<td class="n" data-v="{r["ld"]:.3f}">{r["ld"]:.2f}</td><td class="n" data-v="{r["dmid_km"]:.4f}">{r["diam_min_m"]:.0f}–{r["diam_max_m"]:.0f} m</td>'
           f'<td class="n" data-v="{r["H_mag"]}">{float(r["H_mag"]):.1f}</td><td data-v="{r["first_seen"]}">{r["first_seen"]}</td><td class="n" data-v="{r["rel_velocity_kms"]:.3f}">{r["rel_velocity_kms"]:.1f} km/s</td></tr>')
head = '<thead><tr><th>Closest (UTC)</th><th>Object (JPL)</th><th class="n">LD</th><th class="n">Size</th><th class="n">Abs. magnitude (H)</th><th>First seen</th><th class="n">Velocity</th></tr></thead>'
MPCNEO = '<a href="https://www.minorplanetcenter.net/iau/NEO/toconfirm_tabular.html" target="_blank" rel="noopener">MPC NEO Confirmation page</a>'
desc = (f'<p class="tk">COMING NOT SO CLOSE!</p><p class="td">The 15 near-Earth asteroids that pass closest to Earth in the next 7 days, nearest first. LD is the distance in lunar distances (1 LD = 384,400 km, the Earth–Moon distance); Size is the estimated diameter range; the absolute magnitude H is the object’s brightness at a standard distance (the smaller H, the bigger the object); First seen is the date we first captured it; Velocity is its speed relative to Earth. '
        f'Data: {MPCNEO} and the <a href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html" target="_blank" rel="noopener">JPL Small-Body Database</a>, with close approaches from <a href="https://cneos.jpl.nasa.gov/ca/" target="_blank" rel="noopener">NASA/JPL CNEOS</a>, obtained through the <a href="https://api.nasa.gov/" target="_blank" rel="noopener">NASA NeoWs feed</a>. Refreshed automatically every 8 hours. Last updated: {upd}. Click a column heading to sort.</p>')
a = s.index('<div class="dd2"><div>' ); a = s.index('<div class="tw">', a); b = s.index('</div></div></details>', a)
s = s[:a] + desc + '<div class="tw"><table class="sortable">' + head + '<tbody>' + tr + '</tbody></table>' + s[b:]
# impact table: description + sortable
s = s.replace('<div class="dd2 big"><div><div class="tw"><table>', '<div class="dd2 big"><div><p class="td">The objects with the highest impact risk on JPL’s Sentry list, ranked by cumulative Palermo value. Prob. is the impact probability; the Palermo and Torino scales rate the risk (Palermo below −2 is no cause for concern; Torino 0 means no hazard); LD is the closest-approach distance in lunar distances. Data: <a href="https://cneos.jpl.nasa.gov/sentry/" target="_blank" rel="noopener">JPL Sentry risk table</a>, refreshed automatically every 8 hours. Click a column heading to sort.</p><div class="tw"><table class="sortable">')
# 4. full-width captions under each Space Watch block
s = re.sub(r'(<div class="dd2[^"]*">.*?)(</div></details>)', lambda m: m.group(1) + '<div class="capwide"></div>' + m.group(2) if 'capwide' not in m.group(1) else m.group(0), s, flags=re.S)
s = s.replace("function show(c,i){const s=c.querySelectorAll('.slide');const n=(i+s.length)%s.length;s.forEach((x,k)=>x.classList.toggle('on',k===n));c.dataset.i=n;c.querySelector('.pos').textContent=(n+1)+' / '+s.length;}",
              "function show(c,i){const s=c.querySelectorAll('.slide');const n=(i+s.length)%s.length;s.forEach((x,k)=>x.classList.toggle('on',k===n));c.dataset.i=n;c.querySelector('.pos').textContent=(n+1)+' / '+s.length;const w=c.closest('.dd2');if(w){const cw=w.querySelector('.capwide'),fc=s[n].querySelector('figcaption');if(cw&&fc)cw.innerHTML=fc.innerHTML}}")
# 5. css + sorting js
css = ('<style id="v10-css">body{font-size:20px}details>summary::after{font-size:5em;line-height:.4;vertical-align:middle;font-weight:400}'
       '.dd2 .slide figcaption{display:none}.capwide{grid-column:1/-1;border-top:1px solid var(--rule);padding-top:12px}.capwide b{font-size:20px}'
       '.dd2 .ctrl{margin-top:12px}.dd2 .ctrl button{font-size:46px;line-height:1;padding:2px 26px 8px;border-width:2px;border-radius:8px}.dd2 .ctrl .pos{font-size:34px;font-weight:700;color:var(--ink)}'
       '.tk{font:900 30px/1.1 "Playfair Display",Georgia,serif;color:var(--acc);margin:0 0 8px;letter-spacing:.02em}.td{font-size:17px;line-height:1.5;margin:0 0 12px;color:var(--ink2)}.td a{color:var(--ai)}'
       'table.sortable{font-size:19px}table.sortable th{cursor:pointer;user-select:none;white-space:normal;vertical-align:bottom}table.sortable th:hover{color:var(--ink)}table.sortable th.asc::after{content:" ▲";color:var(--acc)}table.sortable th.desc::after{content:" ▼";color:var(--acc)}table.sortable th,table.sortable td{padding:8px 10px}</style>')
sj = ('<script id="v10-js">(function(){document.querySelectorAll("table.sortable").forEach(function(t){var th=t.querySelectorAll("thead th");th.forEach(function(h,i){h.addEventListener("click",function(){var asc=!h.classList.contains("asc");th.forEach(function(x){x.classList.remove("asc","desc")});h.classList.add(asc?"asc":"desc");'
      'var tb=t.tBodies[0],rs=[].slice.call(tb.rows);function v(r){var c=r.cells[i],x=c.dataset.v!==undefined?c.dataset.v:c.textContent.trim().replace(/,/g,"");var n=parseFloat(x);return(!isNaN(n)&&/^[-+]?[\\d.]/.test(x)&&!/^\\d{4}-\\d\\d-\\d\\d/.test(x))?n:x}'
      'rs.sort(function(a,b){var x=v(a),y=v(b);var r=(typeof x=="number"&&typeof y=="number")?x-y:String(x).localeCompare(String(y));return asc?r:-r});rs.forEach(function(r){tb.appendChild(r)})})})});'
      'document.querySelectorAll("[data-carousel]").forEach(function(c){var k=(+c.dataset.i||0);if(window.show)show(c,k)})})();</script>')
s = s.replace('</head>', css + '</head>', 1)
k = s.rindex('</body>') if '</body>' in s else len(s); s = s[:k] + sj + s[k:]
open(p, 'w', encoding='utf-8').write(s); print('patched', len(s))
