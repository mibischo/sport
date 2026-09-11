# -*- coding: utf-8 -*-
import json
D=json.load(open('chartdata.json',encoding='utf-8'))
out={}

# ---------- 3. MONATSVOLUMEN ----------
M=D['monate']; W,H=1120,270; ML,MR,MT,MB=46,16,20,52
iw,ih=W-ML-MR,H-MT-MB
mx=46.0; bw=iw/len(M)*0.62
bars=""
for i,m in enumerate(M):
    x=ML+iw*(i+0.5)/len(M)-bw/2
    h=ih*m['h']/mx; y=MT+ih-h
    ih_=ih*m['indoor_h']/mx
    bars+=f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="var(--accent)" rx="1"/>'
    if m['indoor_h']>0.05:
        bars+=f'<rect x="{x:.1f}" y="{MT+ih-ih_:.1f}" width="{bw:.1f}" height="{ih_:.1f}" fill="var(--brass)" rx="1"/>'
    bars+=f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" class="val">{m["h"]:.0f}</text>'
    lab=m['m'][5:]+'/'+m['m'][2:4]
    bars+=f'<text x="{x+bw/2:.1f}" y="{MT+ih+16:.1f}" text-anchor="middle" class="ax">{lab}</text>'
g="".join(f'<line x1="{ML}" y1="{MT+ih-ih*v/mx:.1f}" x2="{W-MR}" y2="{MT+ih-ih*v/mx:.1f}" stroke="var(--rule)" stroke-width="1"/>'
          f'<text x="{ML-7}" y="{MT+ih-ih*v/mx+4:.1f}" text-anchor="end" class="ax">{v}</text>' for v in (0,10,20,30,40))
# gap marker Jan/Feb 2026 missing from data
out['vol']=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Radstunden pro Monat, Juni 2025 bis September 2026">
{g}{bars}
<text x="{ML}" y="12" class="ax">Radstunden je Monat — <tspan fill="var(--brass)">Messing = Indoor</tspan></text>
<text x="{W-MR}" y="{MT+ih+40:.1f}" text-anchor="end" class="ax">Jan + Feb 2026 fehlen vollständig: null Radeinheiten</text>
</svg>'''

# ---------- 4. PROGRESSION eFTP / Gewicht / RHR ----------
P=[p for p in D['progression'] if p['m']>='2025-08']
W,H=1120,280; ML,MR,MT,MB=48,52,22,46
iw,ih=W-ML-MR,H-MT-MB
n=len(P)
def x(i): return ML+iw*i/(n-1)
def ye(v): return MT+ih*(1-(v-190)/95)      # eFTP 190..285
def yg(v): return MT+ih*(1-(v-74)/9)        # kg 74..83
def yr(v): return MT+ih*(1-(v-48)/16)       # rhr 48..64
g="".join(f'<line x1="{ML}" y1="{ye(v):.1f}" x2="{W-MR}" y2="{ye(v):.1f}" stroke="var(--rule)" stroke-width="1"/>'
          f'<text x="{ML-7}" y="{ye(v)+4:.1f}" text-anchor="end" class="ax">{v}</text>' for v in (200,220,240,260,280))
eft=[(x(i),ye(p['eftp'])) for i,p in enumerate(P) if p['eftp']]
gw=[(x(i),yg(p['gewicht'])) for i,p in enumerate(P) if p['gewicht']]
rh=[(x(i),yr(p['rhr'])) for i,p in enumerate(P) if p['rhr']]
def poly(pts,col,w,dash=""):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a,b in pts)}" fill="none" stroke="{col}" stroke-width="{w}"{d}/>'
def dots(pts,col):
    return "".join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3" fill="{col}"/>' for a,b in pts)
xl="".join(f'<text x="{x(i):.1f}" y="{MT+ih+16:.1f}" text-anchor="middle" class="ax">{p["m"][5:]}/{p["m"][2:4]}</text>' for i,p in enumerate(P))
# winter band
wi=[i for i,p in enumerate(P) if '2025-12'<=p['m']<='2026-03']
band=f'<rect x="{x(wi[0]):.1f}" y="{MT}" width="{x(wi[-1])-x(wi[0]):.1f}" height="{ih}" fill="var(--signal-wash)"/>' if wi else ""
out['prog']=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Entwicklung von eFTP, Gewicht und Ruhepuls">
{g}{band}
{poly(eft,'var(--accent)',2.4)}{dots(eft,'var(--accent)')}
{poly(gw,'var(--signal)',1.8,'5 3')}{dots(gw,'var(--signal)')}
{poly(rh,'var(--brass)',1.8,'2 3')}{dots(rh,'var(--brass)')}
{xl}
<text x="{ML}" y="12" class="ax">eFTP Watt (links)</text>
<text x="{W-MR+7}" y="{MT+12}" class="ax" fill="var(--signal)">kg</text>
<text x="{W-MR+7}" y="{MT+28}" class="ax" fill="var(--brass)">Ruhepuls</text>
<text x="{x(len(P)-1):.1f}" y="{ye(266)-11:.1f}" text-anchor="end" class="val">268 W</text>
</svg>'''

# ---------- 5. POWERKURVE ----------
PC=[p for p in D['powerkurve'] if p['all']]
import math
W,H=1120,300; ML,MR,MT,MB=52,20,22,48
iw,ih=W-ML-MR,H-MT-MB
lo,hi=math.log10(5),math.log10(10800)
def lx(s): return ML+iw*(math.log10(s)-lo)/(hi-lo)
def lyw(w): return MT+ih*(1-(w-150)/950)
pts=[(lx(p['s']),lyw(p['all'])) for p in PC if p['all']>=150]
g="".join(f'<line x1="{ML}" y1="{lyw(v):.1f}" x2="{W-MR}" y2="{lyw(v):.1f}" stroke="var(--rule)" stroke-width="1"/>'
          f'<text x="{ML-7}" y="{lyw(v)+4:.1f}" text-anchor="end" class="ax">{v}</text>' for v in (200,400,600,800,1000))
tk=[(5,'5s'),(30,'30s'),(60,'1min'),(300,'5min'),(1200,'20min'),(3600,'60min'),(10800,'3h')]
xt="".join(f'<line x1="{lx(s):.1f}" y1="{MT+ih}" x2="{lx(s):.1f}" y2="{MT+ih+5}" stroke="var(--rule)"/>'
           f'<text x="{lx(s):.1f}" y="{MT+ih+18:.1f}" text-anchor="middle" class="ax">{l}</text>' for s,l in tk)
# highlight the single-test region 300..2400s
x0,x1=lx(300),lx(2400)
band=(f'<rect x="{x0:.1f}" y="{MT}" width="{x1-x0:.1f}" height="{ih}" fill="var(--signal-wash)"/>'
      f'<text x="{(x0+x1)/2:.1f}" y="{MT+16:.1f}" text-anchor="middle" class="mkb">alles aus EINER Fahrt</text>'
      f'<text x="{(x0+x1)/2:.1f}" y="{MT+30:.1f}" text-anchor="middle" class="mk">30-Min-Test 05.09.2026</text>')
line=f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a,b in pts)}" fill="none" stroke="var(--accent)" stroke-width="2.4"/>'
ann=(f'<circle cx="{lx(120):.1f}" cy="{lyw(462):.1f}" r="4" fill="var(--brass)"/>'
     f'<text x="{lx(120):.1f}" y="{lyw(462)-10:.1f}" text-anchor="middle" class="val">462 W / 2 min</text>'
     f'<circle cx="{lx(300):.1f}" cy="{lyw(288):.1f}" r="4" fill="var(--signal)"/>'
     f'<text x="{lx(300)+8:.1f}" y="{lyw(288)+16:.1f}" class="val" fill="var(--signal)">288 W / 5 min — kein Maximalwert</text>')
out['pc']=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Powerkurve, Bestleistungen nach Dauer">
{g}{band}{xt}{line}{ann}
<text x="{ML}" y="12" class="ax">Watt</text>
</svg>'''
open('_p2.json','w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False))
print("part2 ok",{k:len(v) for k,v in out.items()})
