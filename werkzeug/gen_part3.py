# -*- coding: utf-8 -*-
import json
D=json.load(open('chartdata.json',encoding='utf-8'))
out={}
Z=D['zonen']
ZC=['#5B8DB8','#3E8E6E','#C9A227','#D9812C','#C0522A','#A33A2E','#7A2E3C']
ZN=['Z1 Recovery','Z2 Endurance','Z3 Tempo','Z4 Threshold','Z5 VO2max','Z6 Anaerob','Z7 Neuro']

# ---------- ZONEN: gestapelte Balken ----------
W,H=1120,190; ML,MR,MT=150,20,34
iw=W-ML-MR
rows=""
for j,y in enumerate(['2025','2026']):
    yy=MT+j*62; pct=Z[y]['pct']; std=Z[y]['std']
    xc=ML; seg=""
    for i,p in enumerate(pct):
        w=iw*p/100
        seg+=f'<rect x="{xc:.1f}" y="{yy}" width="{max(w,0):.1f}" height="34" fill="{ZC[i]}"/>'
        if p>=4.5:
            seg+=f'<text x="{xc+w/2:.1f}" y="{yy+21:.1f}" text-anchor="middle" class="zl">{p:.0f}%</text>'
        xc+=w
    tot=sum(std)
    rows+=(f'<text x="{ML-12}" y="{yy+15:.1f}" text-anchor="end" class="zy">{y}</text>'
           f'<text x="{ML-12}" y="{yy+29:.1f}" text-anchor="end" class="ax">{tot:.0f} h mit Power</text>{seg}')
leg=""; lx=ML
for i,nme in enumerate(ZN):
    leg+=f'<rect x="{lx}" y="{MT+130}" width="9" height="9" fill="{ZC[i]}"/><text x="{lx+13}" y="{MT+139}" class="ax">{nme}</text>'
    lx+=len(nme)*5.6+26
out['zon']=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Verteilung der Trainingszeit auf Leistungszonen, 2025 gegen 2026">
{rows}{leg}
</svg>'''

# ---------- W/kg GAP ----------
W,H=1120,250; ML,MR,MT,MB=150,150,30,40
iw,ih=W-ML-MR,H-MT-MB
STAGES=[('heute 09/2026','271 W · 76,5 kg',3.54,'ist'),
        ('Ziel 2027','300 W · 74 kg',4.05,'plan'),
        ('Ziel 2028','320 W · 72,5 kg',4.41,'plan'),
        ('Ziel 2029','335 W · 71 kg',4.72,'plan'),
        ('Ziel 2030','350 W · 70 kg',5.00,'plan'),
        ('Ötztaler sub-8','≈345–360 W · 70 kg',4.93,'ziel')]
mxv=5.4
bh=ih/len(STAGES)*0.62
bars=""
for i,(lab,sub,v,kind) in enumerate(STAGES):
    y=MT+ih*(i+0.5)/len(STAGES)-bh/2
    w=iw*v/mxv
    col={'ist':'var(--accent)','plan':'var(--accent-mid)','ziel':'var(--brass)'}[kind]
    bars+=(f'<rect x="{ML}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/>'
           f'<text x="{ML-12}" y="{y+bh*0.45:.1f}" text-anchor="end" class="zy">{lab}</text>'
           f'<text x="{ML-12}" y="{y+bh*0.9:.1f}" text-anchor="end" class="ax">{sub}</text>'
           f'<text x="{ML+w+9:.1f}" y="{y+bh*0.68:.1f}" class="val">{v:.2f} W/kg</text>')
# sub-8 threshold line
tx=ML+iw*4.93/mxv
bars+=(f'<line x1="{tx:.1f}" y1="{MT-6}" x2="{tx:.1f}" y2="{MT+ih+6}" stroke="var(--brass)" stroke-width="1.5" stroke-dasharray="4 3"/>')
gap=ML+iw*3.54/mxv
bars+=(f'<line x1="{gap:.1f}" y1="{MT+ih+10}" x2="{tx:.1f}" y2="{MT+ih+10}" stroke="var(--signal)" stroke-width="1"/>'
       f'<text x="{(gap+tx)/2:.1f}" y="{MT+ih+26:.1f}" text-anchor="middle" class="mkb" fill="var(--signal)">Lücke: +39 % W/kg</text>')
out['gap']=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Watt pro Kilogramm heute, geplante Jahresziele und die Anforderung für Ötztaler unter acht Stunden">
{bars}
</svg>'''
open('_p3.json','w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False))
print("part3 ok",{k:len(v) for k,v in out.items()})
