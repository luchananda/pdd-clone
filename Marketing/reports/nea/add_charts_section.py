#!/usr/bin/env python3
"""Adds (or refreshes) the collapsible "All charts" section in the PDD home mock-up; copies the charts into home/charts/.
Enlarge-only viewer: no download links, right-click and drag disabled (screenshots cannot be prevented).
Usage: add_charts_section.py CHARTS_DIR"""
import sys, os, re, shutil, html, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from nea_captions import caption
src = sys.argv[1]; HOME = os.path.join(HERE, '..', 'home'); dst = os.path.join(HOME, 'charts'); os.makedirs(dst, exist_ok=True)
REJ = set(json.load(open(os.path.join(HERE, 'rejected.json')))) if os.path.exists(os.path.join(HERE, 'rejected.json')) else set()   # marked Rejected on the review page: never shown
files = sorted(f for f in os.listdir(src) if f.endswith('.png') and f not in REJ)
if os.path.abspath(src) != os.path.abspath(dst):
    for f in os.listdir(dst):                                   # charts of earlier sets (e.g. the rejected parallel-coordinates ones) are removed
        if f.endswith(('.png', '.json')): os.remove(os.path.join(dst, f))
    for f in os.listdir(src):
        if f.endswith(('.png', '.json')) and f[:-4] + '.png' not in REJ: shutil.copy(os.path.join(src, f), os.path.join(dst, f))
FAM = [('1-3-', 'Distance, velocity, size'), ('1-3c', None), ('1-3b', None), ('1-3d', None), ('2-3-3d', 'Size, distance, velocity'), ('2-3c', None), ('3-', None), ('3b', None), ('07', None), ('08', None), ('imp1', None), ('imp3b', None), ('imp3', None)]
def fam(f):
    for p, _ in FAM:
        if f.startswith(p) and not (p == '3-' and f.startswith('3b')) and not (p == 'imp3' and f.startswith('imp3b')): return p
    return f
groups = {}
for f in files: groups.setdefault(fam(f), []).append(f)
order = [p for p, _ in FAM]
groups = dict(sorted(groups.items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else 99))
def vlabel(f): return 'Transparent' if 'transparent' in f else ('Grid' if 'grid' in f else '')
cards = []
for p, fl in groups.items():
    title, cap = caption(fl[0])
    cap = cap.replace(' Dark background.', '').replace(' Transparent background (black text) for use on light pages.', '')
    def hot(f):
        hp = os.path.join(dst, f[:-4] + '.json')
        return f" data-hot='{html.escape(open(hp).read(), quote=True).replace(chr(39), '&#39;')}'" if os.path.exists(hp) else ''
    pics = ''.join(f'<div class="cpic{" ctr" if "transparent" in f else ""}" data-zoom="charts/{html.escape(f)}"{hot(f)}><img src="charts/{html.escape(f)}" alt="{html.escape(title)} {vlabel(f)}" loading="lazy" draggable="false"><i></i>{("<span>" + vlabel(f) + "</span>") if vlabel(f) else ""}</div>' for f in fl)
    cards.append(f'<figure class="cfig"><div class="cpics">{pics}</div><figcaption><b>{html.escape(title)}</b><br>{cap}</figcaption></figure>')
section = ('<!--CHARTS-START--><details id="all-charts"><summary>All charts · near-Earth asteroids and impact risk</summary><div class="dd" style="display:block">'
           '<p style="font-size:12px;color:var(--dim)">Click a chart to see it larger. The charts update automatically as new data arrives.</p>'
           '<div class="cgrid">' + ''.join(cards) + '</div></div></details><!--CHARTS-END-->')
css = ('<style id="charts-css">.cgrid{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr))}.cfig{margin:0;min-width:0}'
       '.cpics{display:flex;gap:8px;flex-wrap:wrap}.cpic{position:relative;flex:1 1 140px;min-width:0;border:1px solid var(--rule);border-radius:6px;overflow:hidden;cursor:zoom-in;-webkit-user-select:none;user-select:none;background:#000}'
       '.cpic.ctr{background:repeating-conic-gradient(#d9d9de 0 25%,#fff 0 50%) 0 0/16px 16px}.cpic img{width:100%;display:block;pointer-events:none;-webkit-user-drag:none}.cpic i{position:absolute;inset:0}'
       '.cpic span{position:absolute;left:6px;bottom:6px;font:11px/1 sans-serif;background:rgba(0,0,0,.7);color:#fff;padding:3px 7px;border-radius:9px}'
       '.cfig figcaption{font-size:13px;line-height:1.5;margin-top:8px}.cfig figcaption a{color:var(--acc)}'
       '#clb{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;z-index:99;align-items:center;justify-content:center;padding:16px}#clb.on{display:flex}'
       '#clbi{position:relative;width:min(100%,calc((100vh - 32px)*1.3333));aspect-ratio:4/3;background-repeat:no-repeat;background-position:center;background-size:100% 100%}'
       '.chs{position:absolute;transform:translate(-50%,-50%);aspect-ratio:1;border-radius:50%;border:2px solid transparent;background:transparent;padding:0;cursor:pointer}.chs:hover,.chs:focus{border-color:#ffc904}'
       '.pcard{position:absolute;z-index:60;width:min(360px,72%);box-sizing:border-box;background:rgba(196,167,255,.6);color:#000;border:2px solid #fff;border-radius:14px;padding:14px 18px 12px;font:14px/1.45 -apple-system,Helvetica,Arial,sans-serif;text-shadow:0 0 5px rgba(255,255,255,.55);-webkit-backdrop-filter:blur(5px);backdrop-filter:blur(5px);box-shadow:0 8px 28px rgba(0,0,0,.5)}.pcard .nl{text-decoration:none!important}.pcard .ct{display:block;font-size:28px;font-weight:800;line-height:1.1;color:#000;text-decoration:underline;text-underline-offset:4px;text-decoration-thickness:2px}.pcard .cs{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin:4px 0 8px}.pcard table,.pcard tr,.pcard td{border:0!important;background:none!important;font-size:14px;line-height:1.45;color:#000;box-shadow:none}.pcard table{border-collapse:collapse;width:100%}.pcard td{padding:2px 0;vertical-align:top}.pcard td:first-child{font-weight:700;padding-right:12px;white-space:nowrap}.pcard .cl{margin-top:9px;padding-top:7px;border-top:1px solid rgba(0,0,0,.4)}.pcard a{color:#000;font-weight:700}</style>')
lb = '<div id="clb" role="dialog" aria-label="Chart, enlarged"><div id="clbi"></div></div>'
js = ('<script id="charts-js">(function(){var lb=document.getElementById("clb"),im=document.getElementById("clbi");'
      'document.addEventListener("contextmenu",function(e){if(e.target.closest&&(e.target.closest(".cpic")||e.target.closest("#clb")))e.preventDefault()});'
      'document.addEventListener("dragstart",function(e){if(e.target.closest&&e.target.closest(".cpic"))e.preventDefault()});'
      'function showCard(box,p){var o=box.querySelector(".pcard");if(o)o.remove();var c=document.createElement("div");c.className="pcard";c.innerHTML=p.h;box.appendChild(c);'
      'var w=box.clientWidth,h=box.clientHeight,cw=c.offsetWidth,ch=c.offsetHeight,px=p.x*w,py=p.y*h,g=Math.max(p.r*w,14)+14,l=(px+g+cw<=w-6)?px+g:px-g-cw;'
      'if(l<6)l=Math.max(6,Math.min(w-cw-6,px-cw/2));c.style.left=l+"px";c.style.top=Math.min(Math.max(py-ch/2,6),Math.max(6,h-ch-6))+"px"}'
      'function close(){lb.classList.remove("on");im.innerHTML=""}'
      'document.addEventListener("click",function(e){var z=e.target.closest&&e.target.closest(".cpic");if(z){im.style.backgroundImage="url(\\""+z.dataset.zoom+"\\")";im.innerHTML="";'
      'var h=null;try{h=z.dataset.hot?JSON.parse(z.dataset.hot):null}catch(x){}(h&&h.pts||[]).forEach(function(p){var b=document.createElement("button");b.className="chs";b.title=p.t;b.setAttribute("aria-label",p.t);b.style.left=(p.x*100)+"%";b.style.top=(p.y*100)+"%";b.style.width=(p.r*200)+"%";'
      'b.addEventListener("click",function(ev){ev.stopPropagation();showCard(im,p)});im.appendChild(b)});lb.classList.add("on");return}'
      'if(e.target.closest&&e.target.closest(".pcard"))return;if(e.target.closest&&e.target.closest("#clb")){var c=im.querySelector(".pcard");if(c&&!e.target.closest(".chs")){c.remove();return}close()}});'
      'document.addEventListener("keydown",function(e){if(e.key==="Escape")close()})})();</script>')
p = os.path.join(HOME, 'pdd-home-v8.html'); s = open(p, encoding='utf-8').read()
# the old carousels inside the two Space Watch dropdowns are replaced by this section
s = re.sub(r'<div class="carousel" data-carousel>.*?<div class="ctrl">.*?</div></div>', '', s, flags=re.S)
s = re.sub(r'<!--CHARTS-START-->.*?<!--CHARTS-END-->', '', s, flags=re.S)
s = re.sub(r'<style id="charts-css">.*?</style>', '', s, flags=re.S); s = re.sub(r'<div id="clb".*?</div></div>', '', s, flags=re.S); s = re.sub(r'<script id="charts-js">.*?</script>', '', s, flags=re.S)
i = s.index('<section id="space-watch">'); j = s.index('</section>', i)
s = s[:j] + section + s[j:]
s = s.replace('</head>', css + '</head>', 1) if '</head>' in s else css + s
k = s.rindex('</body>') if '</body>' in s else len(s)
s = s[:k] + lb + js + s[k:]
open(p, 'w', encoding='utf-8').write(s)
print(len(files), 'charts in', len(groups), 'groups; page', len(s), 'bytes')
