#!/usr/bin/env python3
"""Builds the chart review page (artifact): current charts with captions + links, Approve / Publish / Reject, comments,
enlarge-only viewer (no download controls). Usage: gen_review.py CHARTS_DIR PAGE_OUT FILES_JSON"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nea_captions import caption
charts_dir, out, files_json = sys.argv[1:4]
REJ = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rejected.json'))))
now = sorted(f for f in os.listdir(charts_dir) if f.endswith('.png') and f not in REJ and 'transparent' not in f)   # dark versions only
files = json.load(open(files_json))
approved = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else []
items = []
for f in now:
    t, c = caption(f)
    st = ' · transparent background' if 'transparent' in f else (' · with grid' if 'grid' in f else '')
    it = {'key': 'v13/' + f, 'group': 'now', 'title': f"{t}{st}", 'desc': c}
    hp = os.path.join(charts_dir, f[:-4] + '.json')
    if os.path.exists(hp): it['hot'] = json.load(open(hp))
    items.append(it)
for f in approved:
    g = f.split('/')[0]; base = os.path.basename(f)[:-4]
    items.append({'key': f, 'group': 'approved', 'title': re.sub(r'[-_]', ' ', base) + ' (approved earlier)', 'desc': f'Approved in the {g} set. Kept here as approved; the new version above replaces it once you approve that one.'})
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'review_template.html')).read()
aud = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audit.json')))
open(out, 'w').write(tpl.replace('/*ITEMS*/', 'const ITEMS=' + json.dumps(items) + ';').replace('/*AUDIT*/', 'const AUDIT=' + json.dumps(aud) + ';'))
json.dump(['v13/' + f for f in now] + approved, open(files_json, 'w'))
print(len(now), 'current;', len(approved), 'approved')
