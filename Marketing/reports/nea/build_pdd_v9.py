#!/usr/bin/env python3
"""PDD mock-up v9: Space Watch pairs (carousel + table), side panel (map card, dark cumulative carousel, 3 ads), footer handles, collapsible captions.
Usage: build_pdd_v9.py CHARTS_DIR  (edits ../home/pdd-home-v8.html in place)"""
import sys, os, re, shutil, html, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from nea_captions2 import parts
src = sys.argv[1]; HOME = os.path.join(HERE, '..', 'home'); dst = os.path.join(HOME, 'charts')
NEED = {'close': ['3b-diameter-vs-distance-linear-dark.png', '2-3-3d-dark-grid.png', '1-3d-distance-velocity-size-linear-legends-dark.png'],
        'risk': ['imp3b-timeline-century-alert-dark.png', 'imp1-distance-torino-palermo-dark.png'],
        'cum': ['07-cumulative-log-dark.png', '08-cumulative-linear-dark.png']}
for f in os.listdir(dst):
    if f.endswith(('.png', '.json')): os.remove(os.path.join(dst, f))
for k in NEED.values():
    for f in k:
        for e in ('.png', '.json'):
            p = os.path.join(src, f[:-4] + e)
            if os.path.exists(p): shutil.copy(p, os.path.join(dst, f[:-4] + e))
E_ = lambda t: html.escape(t, quote=True)
def hot(f):
    hp = os.path.join(dst, f[:-4] + '.json')
    return f" data-hot='{E_(open(hp).read()).replace(chr(39), '&#39;')}'" if os.path.exists(hp) else ''
def carousel(files, extra='', auto=False):
    sl = ''
    for f in files:
        t, sm, body = parts(f)
        sl += (f'<figure class="slide"><div class="cpic" data-zoom="charts/{E_(f)}"{hot(f)}><img src="charts/{E_(f)}" alt="{E_(t)}" draggable="false"><i></i></div>'
               f'<figcaption><b>{html.escape(t)}</b><details class="capd"><summary>{sm}</summary>{body}</details></figcaption></figure>')
    return (f'<div class="carousel" data-carousel{" data-auto" if auto else ""}><div class="slides">{sl}</div>'
            '<div class="ctrl"><button onclick="step(this,-1)" aria-label="Previous chart">&#8249;</button><span class="pos"></span><button onclick="step(this,1)" aria-label="Next chart">&#8250;</button></div></div>')
p = os.path.join(HOME, 'pdd-home-v8.html'); s = open(p, encoding='utf-8').read()
s = s.replace('home mock-up v8', 'home mock-up v9')
s = re.sub(r'<!--CHARTS-START-->.*?<!--CHARTS-END-->', '', s, flags=re.S)                      # "All charts" section removed
# --- Space Watch: two dropdowns, plots paired with tables
blocks = re.findall(r'<details><summary>(?:Close approaches|Impact risk).*?</details>', s, flags=re.S)
tw = [re.search(r'(<div class="tw">.*)</div>\s*</div></details>', b, flags=re.S).group(1) + '</div>' for b in blocks]
t1, t2, src_p = tw[0], tw[1], ''
if not t1.rstrip().endswith('</div>'): t1 += '</div>'
a = s.index('<details><summary>Close approaches'); b = s.index('</section>', a)
sw = ('<details open><summary>CLOSE APPROACHES · TOP 15 NEXT 7 DAYS</summary><div class="dd2"><div>' + carousel(NEED['close']) + '</div><div>' + t1 + '</div></div></details>\n'
      '<details open><summary>IMPACT RISK</summary><div class="dd2 big"><div>' + t2 + src_p + '</div><div>' + carousel(NEED['risk']) + '</div></div></details>\n')
s = s[:a] + sw + s[b:]
s = s.replace('<h2>SPACE WATCH</h2>', '<h2>SPACE WATCH</h2>')
# --- section 5: five headlines as carousel tiles; section 6: subscribe banner
import datetime
news = json.load(open(os.path.join(HERE, 'news5.json')))
def stamp(x):
    d = datetime.datetime.fromisoformat(x['dt'].replace('Z', '+00:00')); return d.strftime('%d %b %Y · %H:%M UTC')
tiles = ''.join(f'<a class="nt" href="https://planetary-defense-daily.newsroomfloor.com/story/{x["id"]}" target="_blank" rel="noopener"><img src="{x["img"]}" alt="" draggable="false"><h3>{html.escape(x["title"])}</h3><small>By {html.escape(x["author"])} · {stamp(x)}</small></a>' for x in news)
sec5 = ('<section id="headlines"><p class="kicker">More stories</p><h2>More from the desk</h2><div class="ntw"><button class="nb l" aria-label="Previous headlines" onclick="document.getElementById(\'nstrip\').scrollBy({left:-320,behavior:\'smooth\'})">&#8249;</button>'
        f'<div class="nstrip" id="nstrip">{tiles}</div><button class="nb r" aria-label="Next headlines" onclick="document.getElementById(\'nstrip\').scrollBy({{left:320,behavior:\'smooth\'}})">&#8250;</button></div></section>\n'
        '<section id="subscribe"><div class="banner subw"><h3>Subscribe</h3><p>Get Planetary Defense Daily in your inbox: the day’s top stories, the close approaches and the impact-risk watch.</p><a class="btn" href="#">Subscribe</a></div></section>\n')
a = s.index('<section><p class="kicker">More stories</p>'); b = s.index('</section>', a) + len('</section>')
s = s[:a] + sec5.rstrip() + s[b:]
# --- side panel
a = s.index('<aside class="side">'); b = s.index('</aside>', a) + len('</aside>')
side = s[a:b]
disc = re.search(r'<h3>Discovered today</h3>.*?</ul>', side, flags=re.S).group(0)
disc = re.sub(r'<small>Source: ', '<small>', disc)
disc = disc.replace('<h3>Discovered today</h3>', '<h3>Discovered today</h3>')
X = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M18.2 2H21l-6.5 7.4L22 22h-6l-4.7-6.1L5.8 22H3l7-8L2 2h6.1l4.2 5.6L18.2 2zm-1 18h1.6L7 3.8H5.3L17.2 20z"/></svg>'
GH = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.3-3.4-1.3-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.4 1.1 3 .8.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.6 9.6 0 0 1 5 0c1.9-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.900-2.300 4.700-4.600 5 .4.3.7.9.7 1.900v2.800c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/></svg>'
ads = ('<div class="sads"><div class="sad"><span class="spons">Ad</span><h4>Subscribe</h4><p>Get the daily briefing in your inbox.</p><a class="btn" href="#">Subscribe</a></div>'
       '<div class="sad"><span class="spons">Ad</span><h4>Newsroom Floor</h4><p>Where AI newsrooms are built and checked.</p><a class="btn" href="https://newsroomfloor.com" target="_blank" rel="noopener">Visit Newsroom Floor</a></div>'
       f'<div class="sad"><span class="spons">Ad</span><h4>Follow on X</h4><p>New stories and charts as they land.</p><a class="btn" href="https://x.com/newtons_in_laws" target="_blank" rel="noopener">{X} Follow @newtons_in_laws</a></div></div>')
new_side = ('<aside class="side">\n  <h3 style="margin-top:6px">Asteroids today · map <button id="mapbig" class="mb" aria-label="Enlarge the map">Enlarge ⤢</button></h3>'
            '<svg id="pdd-map" viewBox="0 0 960 500" style="width:100%;height:auto;display:block;border-radius:6px;border:1px solid var(--rule);cursor:zoom-in" role="img" aria-label="World map of recently discovered objects"></svg>'
            '<div class="map-key" style="font-size:12px;color:var(--dim);margin:6px 0 10px">🪨 Other NEO · 💥 PHA · ☄️ Will enter Earth\'s atmosphere · shaded = night · click a dot for its card</div>\n  '
            + disc + '\n  <h3>Cumulative NEAs</h3>' + carousel(NEED['cum'], auto=True) + '\n  ' + ads + '\n</aside>')
s = s[:a] + new_side + s[b:]
# --- footer
a = s.index('<div class="fcols">'); b = s.index('</footer>')
s = s[:a] + (f'<div class="fcols"><div><b>Newsroom Floor</b><br><a href="https://newsroomfloor.com" target="_blank">newsroomfloor.com</a></div>'
             f'<div><b>@newtons_in_laws</b><br><a class="soc" href="https://x.com/newtons_in_laws" target="_blank" rel="noopener">{X} X</a> <a class="soc" href="https://github.com/newtons_in_laws" target="_blank" rel="noopener">{GH} GitHub</a></div></div>\n') + s[b:]
# --- css
css = ('<style id="v9-css">aside{position:static!important;max-height:none!important;overflow:visible!important}'
       '.dd2{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:18px;padding:0 16px 16px}.dd2>div{min-width:0}@media (max-width:900px){.dd2{grid-template-columns:1fr}}'
       '.big table{font-size:15px}.big th,.big td{padding:8px 10px}.big p{font-size:14px!important}'
       '.slide .cpic{border:1px solid var(--rule);border-radius:6px;overflow:hidden;cursor:zoom-in;position:relative;background:#000}.slide .cpic i{position:absolute;inset:0}'
       'details.capd{background:none;border:0;border-radius:0;margin:6px 0 0}details.capd>summary{padding:0;font:13px/1.5 "Helvetica Neue",Helvetica,Arial,sans-serif;font-weight:400;letter-spacing:0;text-transform:none;color:var(--ink2)}'
       'details.capd>summary::after{content:" ▾";float:none;color:var(--acc)}details.capd[open]>summary::after{content:" ▴"}.capd p{margin:8px 0 0;font-size:13px;line-height:1.55;color:var(--ink2)}.capd a{color:var(--ai)}'
       '.sads{display:grid;gap:12px;margin-top:6px}.sad{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:14px;position:relative;text-align:center}.sad h4{margin:0 0 4px;font:700 17px "Playfair Display",Georgia,serif;color:var(--ink)}.sad p{margin:0 0 10px;font-size:13px;color:var(--ink2)}'
       '.ntw{position:relative}.nstrip{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:thin;padding-bottom:6px}.nt{flex:0 0 min(300px,80%);scroll-snap-align:start;background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:10px;text-decoration:none;color:inherit}.nt img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:4px;display:block;margin-bottom:8px}.nt h3{font-size:17px;line-height:1.25;margin:0 0 6px}.nt small{color:var(--dim);font-size:12px}.nb{position:absolute;top:35%;z-index:2;width:34px;height:34px;border-radius:50%;border:1px solid var(--rule);background:var(--card2);color:var(--ink);font-size:22px;cursor:pointer}.nb.l{left:-8px}.nb.r{right:-8px}.subw{max-width:none}.subw p{max-width:60ch;margin:0 auto 12px}'
       '.ic{width:1em;height:1em;vertical-align:-.12em}.soc{margin-right:14px}.mb{float:right;font:12px sans-serif;background:none;border:1px solid var(--rule);color:var(--ink);border-radius:4px;padding:2px 8px;cursor:pointer}'
       '#mlb{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;z-index:98;align-items:center;justify-content:center;padding:16px;flex-direction:column}#mlb.on{display:flex}#mlb svg{width:min(100%,calc((100vh - 40px)*1.92));height:auto;border-radius:6px;cursor:default}'
       '#ocard{position:fixed;z-index:120;left:50%;bottom:22px;transform:translateX(-50%);width:min(380px,calc(100vw - 24px));box-sizing:border-box;background:rgba(255,201,4,.82);color:#000;border:2px solid #fff;border-radius:14px;padding:14px 18px 12px;font:14px/1.45 -apple-system,Helvetica,Arial,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.5);display:none}#ocard.on{display:block}'
       '#ocard .ct{display:block;font-size:28px;font-weight:800;line-height:1.1;color:#000;text-decoration:underline;text-underline-offset:4px}#ocard .cs{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin:4px 0 8px}#ocard td{padding:2px 12px 2px 0;vertical-align:top;border:0;white-space:normal}#ocard td:first-child{font-weight:700;white-space:nowrap}#ocard table{width:100%;font-size:14px}#ocard a{color:#000;font-weight:700}#ocard .x{position:absolute;top:6px;right:10px;cursor:pointer;font-size:20px;background:none;border:0}</style>')
s = re.sub(r'<style id="v9-css">.*?</style>', '', s, flags=re.S)
s = s.replace('</head>', css + '</head>', 1)
# --- map: clickable dots, object card, enlarge
js = r'''<div id="mlb" onclick="if(event.target===this)this.classList.remove('on')"></div><div id="ocard"></div><script id="v9-js">(function(){
var oc=document.getElementById('ocard'),mlb=document.getElementById('mlb'),svg=document.getElementById('pdd-map');
function row(k,v){return v?'<tr><td>'+k+'</td><td>'+v+'</td></tr>':''}
function card(i){var o=WATCH.pts[i];if(!o)return;var ty=o.impact?'Will enter Earth’s atmosphere':(o.pha?'Potentially hazardous asteroid (PHA)':'Near-Earth object (NEO)');
 var q=encodeURIComponent(o.des);oc.innerHTML='<button class="x" aria-label="Close">×</button><a class="ct" target="_blank" rel="noopener" href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr='+q+'">'+o.des+'</a><div class="cs">'+ty+'</div><table>'+
 row('Announced',o.date)+row('MPEC',o.mpec)+row('Over now',o.lat.toFixed(2)+'°, '+o.lon.toFixed(2)+'°')+row('Groups',(o.neo?'NEO ':'')+(o.pha?'· PHA ':'')+(o.impact?'· atmospheric entry':''))+'</table>'+
 '<div style="margin-top:8px;border-top:1px solid rgba(0,0,0,.4);padding-top:6px"><a target="_blank" rel="noopener" href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr='+q+'">JPL Small-Body Database</a> · <a target="_blank" rel="noopener" href="https://minorplanetcenter.net/mpec/RecentMPECs.html">Minor Planet Center</a></div>';
 oc.classList.add('on');oc.querySelector('.x').onclick=function(e){e.stopPropagation();oc.classList.remove('on')}}
function wire(root){root.querySelectorAll('text').forEach(function(t,i){t.style.cursor='pointer';t.addEventListener('click',function(e){e.stopPropagation();card(i)})})}
function ready(){var n=svg.querySelectorAll('text').length;if(n<WATCH.pts.length){setTimeout(ready,200);return}wire(svg);
 var big=function(){var c=svg.cloneNode(true);c.removeAttribute('style');c.id='';mlb.innerHTML='';mlb.appendChild(c);wire(c);mlb.classList.add('on')};
 document.getElementById('mapbig').onclick=big;svg.addEventListener('click',big)}
ready();document.addEventListener('keydown',function(e){if(e.key==='Escape'){mlb.classList.remove('on');oc.classList.remove('on')}});
document.querySelectorAll('[data-auto]').forEach(function(c){setInterval(function(){if(!c.matches(':hover'))step(c.querySelector('.ctrl button:last-child'),1)},7000)});
document.querySelectorAll('.disc li').forEach(function(li){var a=li.querySelector('a'),d=a&&a.textContent.trim();var i=WATCH.pts.findIndex(function(o){return o.des===d});if(i>=0){a.addEventListener('click',function(e){e.preventDefault();card(i)})}})})();</script>'''
s = re.sub(r'<div id="mlb".*?</script>(?=\s*</body>|\s*$)', '', s, flags=re.S) if '<div id="mlb"' in s else s
k = s.rindex('</body>') if '</body>' in s else len(s)
s = s[:k] + js + s[k:]
s = s.replace("const pick=document.getElementById('pick');", "const pick=document.getElementById('pick')||document.createElement('select');")
open(p, 'w', encoding='utf-8').write(s)
print('ok', len(s))
