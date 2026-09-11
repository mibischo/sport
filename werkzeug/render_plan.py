# -*- coding: utf-8 -*-
"""Rendert plan_data.json als HTML-Tabelle mit TSS je Einheit."""
import json, io
from datetime import date, timedelta

W = json.load(open('plan_data.json', encoding='utf-8'))

PHASE = {
  "aus":   ("Saisonausklang", "Sep 2026"),
  "auf":   ("Saisonaufbau — Umfang rauf, Schwelle statt VO2", "Apr 2027"),
  "spez":  ("Spezifisch — Renntempo und Kursarbeit", "Mai–Jun 2027"),
  "taper": ("Renntaper &amp; Dolomitenradrundfahrt", "Juni 2027"),
  "mess":  ("Übergang &amp; Messbasis", "Okt 2026"),
  "grund": ("Grundlage, Kraft und erste VO2-Reize", "Nov–Dez 2026"),
  "vo2":   ("Konzentrierter VO2-Block", "Jan–Feb 2027"),
  "str":   ("Übergang zur Straße — indoor geplant", "Mär 2027"),
}
ORDER = ["aus", "mess", "grund", "vo2", "str", "auf", "spez", "taper"]


def dt(y, w):
    a = date.fromisocalendar(y, w, 1)
    b = a + timedelta(days=6)
    return "%d.%d.–%d.%d." % (a.day, a.month, b.day, b.month)


def hm(mins):
    return "%d:%02d" % (mins // 60, mins % 60)


rows = []
seen = set()
last = None
for y, w, ph, sess, fok in W:
    real = ph if ph != "rec" else last
    if ph != "rec":
        last = ph
    if real not in seen:
        seen.add(real)
        t, sub = PHASE[real]
        rows.append('<tr class="phrow"><td colspan="4"><span class="pht">%s</span>'
                    '<span class="phs">%s</span></td></tr>' % (t, sub))

    rad = sum(s['min'] for s in sess if s['type'] == 'Ride')
    kra = sum(s['min'] for s in sess if s['type'] == 'WeightTraining')
    tot = sum(s['tss'] for s in sess)

    li = []
    for s in sess:
        badge = ' <span class="kk">KEY</span>' if s.get('key') else ''
        kraft = ' kraft' if s['type'] == 'WeightTraining' else ''
        li.append(
          '<li class="se%s"><div class="sh"><span class="sn">%s</span>%s'
          '<span class="sm">%s h</span><span class="st">%d TSS</span></div>'
          '<p class="sd">%s</p></li>'
          % (kraft, s['name'], badge, hm(s['min']), s['tss'], s['desc']))

    cls = ' class="recw"' if ph == "rec" else ''
    tag = '<span class="rtag">Entlastung</span>' if ph == "rec" else ''
    rows.append(
      '<tr%s><td class="n wkc"><b>KW&nbsp;%02d</b><span class="dt">%s</span>%s</td>'
      '<td class="n">%s<span class="dt">Rad</span></td>'
      '<td class="n">%s<span class="dt">Kraft</span></td>'
      '<td><ul class="sess">%s</ul><p class="fok"><b>%d TSS gesamt.</b> %s</p></td></tr>'
      % (cls, w, dt(y, w), tag, hm(rad), hm(kra) if kra else "—",
         "".join(li), tot, fok))

json.dump({'plan': "".join(rows)}, io.open('_plan.json', 'w', encoding='utf-8'),
          ensure_ascii=False)

th = sum(s['min'] for _, _, _, ss, _ in W for s in ss if s['type'] == 'Ride') / 60
tk = sum(s['min'] for _, _, _, ss, _ in W for s in ss if s['type'] == 'WeightTraining') / 60
tt = sum(s['tss'] for _, _, _, ss, _ in W for s in ss)
print("Zeilen: %d | Rad %.0f h | Kraft %.0f h | TSS %d" % (len(rows), th, tk, tt))
