# -*- coding: utf-8 -*-
"""Assembles the final report. Uses @@TOKEN@@ substitution so literal % in prose is safe."""
import json, io, re

p1 = json.load(open('_p1.json', encoding='utf-8'))
p2 = json.load(open('_p2.json', encoding='utf-8'))
p3 = json.load(open('_p3.json', encoding='utf-8'))
pl = json.load(open('_plan.json', encoding='utf-8'))
C = dict(p1); C.update(p2); C.update(p3)

# reuse the CSS + component builders already written in build.py
src = io.open('build.py', encoding='utf-8').read()
ns = {}
# execute build.py only up to the HTML assembly (everything before `HTML = `)
head = src.split('HTML = """')[0]
exec(compile(head, 'build_head', 'exec'), ns)

CSS = ns['CSS']
STATS_NOW = ns['STATS_NOW']
STATS_YEAR = ns['STATS_YEAR']
lev_html = ns['lev_html']
ph_html = ns['ph_html']
rm_rows = ns['rm_rows']
act_html = ns['act_html']

TPL = io.open('template.html', encoding='utf-8').read()

REPL = {
    '@@CSS@@': CSS,
    '@@OETZ@@': C['oetz'],
    '@@FIT@@': C['fit'],
    '@@VOL@@': C['vol'],
    '@@PROG@@': C['prog'],
    '@@PC@@': C['pc'],
    '@@ZON@@': C['zon'],
    '@@GAP@@': C['gap'],
    '@@SENS@@': C['sens'],
    '@@STATS_NOW@@': STATS_NOW,
    '@@STATS_YEAR@@': STATS_YEAR,
    '@@LEVERS@@': lev_html,
    '@@PHASES@@': ph_html,
    '@@ROADMAP@@': rm_rows,
    '@@ACTS@@': act_html,
    '@@PLAN@@': pl['plan'],
}
out = TPL
for k, v in REPL.items():
    out = out.replace(k, v)

left = re.findall(r'@@[A-Z_]+@@', out)
if left:
    raise SystemExit('unresolved tokens: %r' % set(left))

io.open('../bericht/rennrad_analyse.html', 'w', encoding='utf-8').write(out)
print('written rennrad_analyse.html:', len(out), 'chars')
print('charts embedded:', sum(1 for k in REPL if k.startswith('@@') and 'svg' in REPL[k][:200]))
