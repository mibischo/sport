# -*- coding: utf-8 -*-
import json
W,H=1120,272; ML,MR,MT,MB=158,164,52,44
iw,ih=W-ML-MR,H-MT-MB
S=[('heute 09/2026','271 W · 76,5 kg',3.54,'ist'),
   ('2027','310 W · 74 kg',4.19,'plan'),
   ('2028','335 W · 72,5 kg',4.62,'plan'),
   ('2029','350 W · 71 kg',4.93,'plan'),
   ('2030','360 W · 70 kg',5.14,'plan')]
mxv=5.9
bh=ih/len(S)*0.60
LO,HI=4.33,5.21   # sub-8 bei optimierter bzw. durchschnittlicher Ausfuehrung
xlo,xhi=ML+iw*LO/mxv, ML+iw*HI/mxv
band=(f'<rect x="{xlo:.1f}" y="{MT-14}" width="{xhi-xlo:.1f}" height="{ih+22}" fill="var(--brass)" opacity="0.16"/>'
      f'<line x1="{xlo:.1f}" y1="{MT-14}" x2="{xlo:.1f}" y2="{MT+ih+8}" stroke="var(--brass)" stroke-width="1.5" stroke-dasharray="4 3"/>'
      f'<line x1="{xhi:.1f}" y1="{MT-14}" x2="{xhi:.1f}" y2="{MT+ih+8}" stroke="var(--brass)" stroke-width="1.5" stroke-dasharray="4 3"/>'
      f'<text x="{(xlo+xhi)/2:.1f}" y="{MT-32}" text-anchor="middle" class="mkb" fill="var(--brass)">SUB-8-KORRIDOR</text>'
      f'<text x="{(xlo+xhi)/2:.1f}" y="{MT-20}" text-anchor="middle" class="ax" fill="var(--brass)">je nach Ausführung</text>'
      f'<text x="{xlo:.1f}" y="{MT+ih+22:.1f}" text-anchor="middle" class="ax" fill="var(--brass)">4,33 — optimiert</text>'
      f'<text x="{xhi:.1f}" y="{MT+ih+22:.1f}" text-anchor="middle" class="ax" fill="var(--brass)">5,21 — durchschnittlich</text>')
bars=""
for i,(lab,sub,v,kind) in enumerate(S):
    y=MT+ih*(i+0.5)/len(S)-bh/2
    w=iw*v/mxv
    col='var(--accent)' if kind=='ist' else 'var(--accent-mid)'
    bars+=(f'<rect x="{ML}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/>'
           f'<text x="{ML-12}" y="{y+bh*0.44:.1f}" text-anchor="end" class="zy">{lab}</text>'
           f'<text x="{ML-12}" y="{y+bh*0.92:.1f}" text-anchor="end" class="ax">{sub}</text>'
           f'<text x="{ML+w+9:.1f}" y="{y+bh*0.70:.1f}" class="val">{v:.2f}</text>')
svg=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Watt pro Kilogramm heute und in den Zieljahren, gegen den Korridor für Ötztaler unter acht Stunden">
{band}{bars}
<text x="{ML}" y="{MT+ih+38:.1f}" class="ax">Watt pro Kilogramm</text>
</svg>'''
d=json.load(open('_p3.json',encoding='utf-8')); d['gap']=svg
json.dump(d,open('_p3.json','w',encoding='utf-8'),ensure_ascii=False)
print("gap chart neu",len(svg))
