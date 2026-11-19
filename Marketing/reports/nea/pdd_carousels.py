#!/usr/bin/env python3
"""Rebuild the three PDD carousels from the charts marked 'publish' on the review page (dark versions only). Usage: pdd_carousels.py CHARTS_DIR"""
import sys, os, re, shutil, html, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from nea_captions2 import parts
src = sys.argv[1]; HOME = os.path.join(HERE, '..', 'home'); dst = os.path.join(HOME, 'charts')
SETS = [['3-diameter-vs-distance-log-dark.png', '3b-diameter-vs-distance-linear-dark.png', '2-3-3d-dark-grid.png', '2-3d-3d-swapped-axes-dark.png', '1-3c-distance-velocity-size-log-legends-dark.png', '1-3d-distance-velocity-size-linear-legends-dark.png'],
        ['imp3b-timeline-century-alert-dark.png', 'imp1b-distance-torino-palermo-table-dark.png'],
        ['07-cumulative-log-dark.png', '08-cumulative-linear-dark.png']]
for f in os.listdir(dst):
    if f.endswith(('.png', '.json')): os.remove(os.path.join(dst, f))
for L in SETS:
    for f in L:
        for e in ('.png', '.json'): shutil.copy(os.path.join(src, f[:-4] + e), os.path.join(dst, f[:-4] + e))
E_ = lambda t: html.escape(t, quote=True)
def hot(f): return f" data-hot='{E_(open(os.path.join(dst, f[:-4] + '.json')).read()).replace(chr(39), '&#39;')}'"
def carousel(files, auto=False):
    sl = ''
    for f in files:
        t, sm, body = parts(f)
        sl += (f'<figure class="slide"><div class="cpic" data-zoom="charts/{E_(f)}"{hot(f)}><img src="charts/{E_(f)}" alt="{E_(t)}" draggable="false"><i></i></div>'
               f'<figcaption><b>{html.escape(t)}</b><details class="capd"><summary>{sm}</summary>{body}</details></figcaption></figure>')
    return (f'<div class="carousel" data-carousel{" data-auto" if auto else ""}><div class="slides">{sl}</div>'
            '<div class="ctrl"><button onclick="step(this,-1)" aria-label="Previous chart">&#8249;</button><span class="pos"></span><button onclick="step(this,1)" aria-label="Next chart">&#8250;</button></div></div>')
p = os.path.join(HOME, 'pdd-home-v8.html'); s = open(p, encoding='utf-8').read()
pat = re.compile(r'<div class="carousel" data-carousel[^>]*>.*?<div class="ctrl">.*?</div></div>', re.S)
ms = list(pat.finditer(s)); assert len(ms) == 3, len(ms)
for m, L, auto in reversed(list(zip(ms, SETS, (False, False, True)))): s = s[:m.start()] + carousel(L, auto) + s[m.end():]
# lightbox keeps each chart's own proportions (the table version is taller)
old = 'var h=null;try{h=z.dataset.hot?JSON.parse(z.dataset.hot):null}catch(x){}'
if old in s and 'aspectRatio' not in s:
    s = s.replace(old, old + 'var ww=(h&&h.w)||1200,hh=(h&&h.h)||900;im.style.aspectRatio=ww+"/"+hh;im.style.width="min(100%,calc((100vh - 32px)*"+(ww/hh)+"))";')
open(p, 'w', encoding='utf-8').write(s); print('carousels rebuilt', [len(L) for L in SETS])
