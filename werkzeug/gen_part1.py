# -*- coding: utf-8 -*-
import json
D=json.load(open('chartdata.json',encoding='utf-8'))

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ---------- 1. OETZTALER HOEHENPROFIL ----------
PTS=[(0,1368,'Sölden'),(27,820,'Ötz'),(45.5,2020,'Kühtai'),(75.5,600,'Innsbruck'),
     (113.5,1377,'Brenner'),(128.5,948,'Sterzing'),(144,2094,'Jaufenpass'),
     (164,693,'St. Leonhard'),(192.7,2509,'Timmelsjoch'),(227,1368,'Sölden')]
W,H=1120,300; ML,MR,MT,MB=52,18,30,54
iw,ih=W-ML-MR,H-MT-MB
def px(k): return ML+iw*k/227
def py(m): return MT+ih*(1-(m-500)/2100)
prof=" ".join(f"{px(k):.1f},{py(m):.1f}" for k,m,_ in PTS)
area=f"M {px(0):.1f},{py(500):.1f} L "+" L ".join(f"{px(k):.1f},{py(m):.1f}" for k,m,_ in PTS)+f" L {px(227):.1f},{py(500):.1f} Z"
grid="".join(f'<line x1="{ML}" y1="{py(a):.1f}" x2="{W-MR}" y2="{py(a):.1f}" stroke="var(--rule)" stroke-width="1"/>'
             f'<text x="{ML-8}" y="{py(a)+4:.1f}" text-anchor="end" class="ax">{a}</text>' for a in (500,1000,1500,2000,2500))
kmt="".join(f'<line x1="{px(k):.1f}" y1="{MT+ih}" x2="{px(k):.1f}" y2="{MT+ih+5}" stroke="var(--rule)" stroke-width="1"/>'
            f'<text x="{px(k):.1f}" y="{MT+ih+19:.1f}" text-anchor="middle" class="ax">{k}</text>' for k in (0,50,100,150,200,227))
peaks=""
for k,m,n in PTS:
    if n in ('Kühtai','Brenner','Jaufenpass','Timmelsjoch'):
        peaks+=(f'<circle cx="{px(k):.1f}" cy="{py(m):.1f}" r="3.5" fill="var(--accent)"/>'
                f'<text x="{px(k):.1f}" y="{py(m)-11:.1f}" text-anchor="middle" class="pk">{n}</text>'
                f'<text x="{px(k):.1f}" y="{py(m)-1:.1f}" text-anchor="middle" class="pkm">{m} m</text>')
OETZ=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Höhenprofil Ötztaler Radmarathon: 227 km, 5500 Höhenmeter, vier Pässe">
{grid}{kmt}
<path d="{area}" fill="var(--accent-wash)"/>
<polyline points="{prof}" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linejoin="round"/>
{peaks}
<text x="{ML}" y="16" class="ax">Höhe m ü. A.</text>
<text x="{W-MR}" y="{MT+ih+40:.1f}" text-anchor="end" class="ax">Kilometer</text>
</svg>'''

# ---------- 2. FITNESS CTL/ATL ----------
F=D['fitness']; W2,H2=1120,300; ML2,MR2,MT2,MB2=46,16,22,42
iw2,ih2=W2-ML2-MR2,H2-MT2-MB2
n=len(F); mx=80
def fx(i): return ML2+iw2*i/(n-1)
def fy(v): return MT2+ih2*(1-v/mx)
ctl=" ".join(f"{fx(i):.1f},{fy(d['ctl']):.1f}" for i,d in enumerate(F))
atl=" ".join(f"{fx(i):.1f},{fy(d['atl']):.1f}" for i,d in enumerate(F))
ctla=f"M {ML2},{fy(0):.1f} L "+" L ".join(f"{fx(i):.1f},{fy(d['ctl']):.1f}" for i,d in enumerate(F))+f" L {fx(n-1):.1f},{fy(0):.1f} Z"
g2="".join(f'<line x1="{ML2}" y1="{fy(v):.1f}" x2="{W2-MR2}" y2="{fy(v):.1f}" stroke="var(--rule)" stroke-width="1"/>'
           f'<text x="{ML2-7}" y="{fy(v)+4:.1f}" text-anchor="end" class="ax">{v}</text>' for v in (0,20,40,60,80))
idx={d['d']:i for i,d in enumerate(F)}
marks=""
for day,lab,dy in [('2025-12-11','letzte Radfahrt 11.12.',-6),('2026-03-28','Wiedereinstieg 28.03.',-6),('2026-08-30','CTL-Peak 73,0',-6)]:
    if day in idx:
        x=fx(idx[day])
        marks+=(f'<line x1="{x:.1f}" y1="{MT2}" x2="{x:.1f}" y2="{MT2+ih2}" stroke="var(--signal)" stroke-width="1" stroke-dasharray="3 3"/>'
                f'<text x="{x+5:.1f}" y="{MT2+12+dy:.1f}" class="mk">{lab}</text>')
# winter shading
if '2025-12-11' in idx and '2026-03-28' in idx:
    x0,x1=fx(idx['2025-12-11']),fx(idx['2026-03-28'])
    marks=f'<rect x="{x0:.1f}" y="{MT2}" width="{x1-x0:.1f}" height="{ih2}" fill="var(--signal-wash)"/>'+marks
    marks+=f'<text x="{(x0+x1)/2:.1f}" y="{MT2+ih2-10:.1f}" text-anchor="middle" class="mkb">107 Tage ohne Rad</text>'
mlab=""
seen=set()
for i,d in enumerate(F):
    ym=d['d'][:7]
    if ym not in seen and d['d'][8:10]=='01':
        seen.add(ym)
        if ym[5:] in ('01','04','07','10'):
            mlab+=f'<text x="{fx(i):.1f}" y="{MT2+ih2+18:.1f}" text-anchor="middle" class="ax">{ym[5:]}/{ym[2:4]}</text>'
FIT=f'''<svg viewBox="0 0 {W2} {H2}" class="chart" role="img" aria-label="Fitness-Verlauf CTL und ATL von Juni 2025 bis September 2026">
{g2}{marks}
<path d="{ctla}" fill="var(--accent-wash)"/>
<polyline points="{atl}" fill="none" stroke="var(--muted)" stroke-width="1.2" opacity="0.75"/>
<polyline points="{ctl}" fill="none" stroke="var(--accent)" stroke-width="2.4"/>
{mlab}
<text x="{ML2}" y="12" class="ax">CTL / ATL</text>
</svg>'''
open('_p1.json','w',encoding='utf-8').write(json.dumps({'oetz':OETZ,'fit':FIT},ensure_ascii=False))
print("part1 ok", len(OETZ), len(FIT))
