# -*- coding: utf-8 -*-
import json
F=[("Abfahrten 50 statt 44 km/h",-20,"Abfahrten 38 statt 44 km/h",26,"Abfahrtstechnik"),
   ("Brenner in schneller Gruppe",-12,"Brenner allein gefahren",14,"Gruppenanschluss"),
   ("Kletter-IF 0,84 statt 0,80",-10,"Kletter-IF 0,75 statt 0,80",13,"Ermüdungsresistenz"),
   ("Standzeit 8 statt 17 min",-9,"Standzeit 30 statt 17 min",13,"Verpflegungslogistik")]
W,H=1120,270; ML,MR,MT,MB=178,178,42,34
iw,ih=W-ML-MR,H-MT-MB
mx=30.0
cx=ML+iw/2
rows=""
bh=ih/len(F)*0.54
for i,(gl,gv,bl,bv,cat) in enumerate(F):
    y=MT+ih*(i+0.5)/len(F)-bh/2
    wg=iw/2*abs(gv)/mx; wb=iw/2*bv/mx
    rows+=(f'<rect x="{cx-wg:.1f}" y="{y:.1f}" width="{wg:.1f}" height="{bh:.1f}" fill="var(--accent)" rx="1"/>'
           f'<rect x="{cx:.1f}" y="{y:.1f}" width="{wb:.1f}" height="{bh:.1f}" fill="var(--signal)" rx="1"/>'
           f'<text x="{cx-wg-8:.1f}" y="{y+bh*0.68:.1f}" text-anchor="end" class="val" fill="var(--accent)">&#8722;{abs(gv)} min</text>'
           f'<text x="{cx+wb+8:.1f}" y="{y+bh*0.68:.1f}" class="val" fill="var(--signal)">+{bv} min</text>'
           f'<text x="{ML-14}" y="{y+bh*0.68:.1f}" text-anchor="end" class="zy">{cat}</text>')
axis=(f'<line x1="{cx:.1f}" y1="{MT-10}" x2="{cx:.1f}" y2="{MT+ih+8}" stroke="var(--ink)" stroke-width="1.5"/>'
      f'<text x="{cx:.1f}" y="{MT-16}" text-anchor="middle" class="mkb" fill="var(--ink)">Referenz 8:08</text>'
      f'<text x="{cx-iw/4:.1f}" y="{MT+ih+26:.1f}" text-anchor="middle" class="ax">schneller</text>'
      f'<text x="{cx+iw/4:.1f}" y="{MT+ih+26:.1f}" text-anchor="middle" class="ax">langsamer</text>')
svg=f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Wie stark einzelne Ausführungsfaktoren die Ötztaler-Zeit verändern, bei gleichbleibender Form">
{axis}{rows}
</svg>'''
d=json.load(open('_p3.json',encoding='utf-8')); d['sens']=svg
json.dump(d,open('_p3.json','w',encoding='utf-8'),ensure_ascii=False)
print("sens chart ok",len(svg))
