# -*- coding: utf-8 -*-
"""Exportiert den Trainingsplan aus plan_data.json als GitHub-lesbares Markdown."""
import json, io, re, os
from datetime import date, timedelta

W = json.load(open('plan_data.json', encoding='utf-8'))
OUT = os.path.join('..', 'trainingsplan.md')

PHASE = {
    "aus": "Saisonausklang", "mess": "Übergang & Messbasis", "auf": "Aufbau",
    "grund": "Grundlage, Kraft und erste VO2-Reize", "vo2": "Konzentrierter VO2-Block",
    "str": "Übergang zur Straße", "spez": "Spezifisch — Renntempo und Kursarbeit",
    "taper": "Renntaper & Dolomitenradrundfahrt", "rec": "Entlastung",
}
TAG = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]



_KEEP = re.compile(r'(?<=[qaeQAE])ue|ae(?=ro)|Ae(?=ro)')
def _umlaut(t):
    out=[]; i=0
    while i < len(t):
        two=t[i:i+2]
        if two in ('ae','oe','ue','Ae','Oe','Ue'):
            prev=t[i-1] if i>0 else ''
            nxt=t[i+2:i+4]
            keep=False
            if two.lower()=='ue' and prev.lower() in ('q','a','e'): keep=True   # Frequenz, Sauer, neue
            if two.lower()=='ae' and nxt.lower()=='ro': keep=True               # aerob, Aeroad
            if not keep:
                out.append({'ae':'ä','oe':'ö','ue':'ü','Ae':'Ä','Oe':'Ö','Ue':'Ü'}[two]); i+=2; continue
        out.append(t[i]); i+=1
    r=''.join(out)
    return r.replace('Rönnestad','Rønnestad').replace('Roennestad','Rønnestad')


def clean(t):
    t = re.sub(r'<[^>]+>', '', t)
    for a, b in (('&times;', '×'), ('&amp;', '&'), ('&nbsp;', ' '), ('&rarr;', '→'),
                 ('&minus;', '−'), ('&bdquo;', '„'), ('&ldquo;', '“')):
        t = t.replace(a, b)
    # Umlaute aus der ASCII-Schreibweise der Plan-Datei zuruecksetzen
    for a, b in (('Ueber', 'Über'), ('ueber', 'über'), ('Aenderung', 'Änderung'),
                 ('aendern', 'ändern'), ('Gewoehnung', 'Gewöhnung'), ('Saetze', 'Sätze'),
                 ('fuer', 'für'), ('Fuer', 'Für'), ('koennen', 'können'), ('muessen', 'müssen'),
                 ('Luefter', 'Lüfter'), ('Verpflegung', 'Verpflegung'), ('Rueckweg', 'Rückweg'),
                 ('zurueck', 'zurück'), ('Hoechst', 'Höchst'), ('hoechst', 'höchst'),
                 ('Staerke', 'Stärke'), ('staerker', 'stärker'), ('laenger', 'länger'),
                 ('Laenge', 'Länge'), ('naechst', 'nächst'), ('gehoert', 'gehört'),
                 ('Muedigkeit', 'Müdigkeit'), ('muede', 'müde'), ('ermuedet', 'ermüdet'),
                 ('frueher', 'früher'), ('Frueh', 'Früh'), ('frueh', 'früh'),
                 ('Erhaelt', 'Erhält'), ('erhaelt', 'erhält'), ('haelt', 'hält'),
                 ('Haelfte', 'Hälfte'), ('waere', 'wäre'), ('haette', 'hätte'),
                 ('Zielschnitt', 'Zielschnitt'), ('Ausfahren', 'Ausfahren'),
                 ('rumaenisch', 'rumänisch'), ('Uebergang', 'Übergang'),
                 ('taeglich', 'täglich'), ('regelmaessig', 'regelmäßig'),
                 ('Regelmaessigkeit', 'Regelmäßigkeit'), ('Gleichmaessig', 'Gleichmäßig'),
                 ('gleichmaessig', 'gleichmäßig'), ('anfuehlen', 'anfühlen'),
                 ('zaeh', 'zäh'), ('Maerz', 'März'), ('Kaernten', 'Kärnten'),
                 ('Oetztaler', 'Ötztaler'), ('Taeglich', 'Täglich'), ('spaeter', 'später'),
                 ('Schaerfe', 'Schärfe'), ('schaerfe', 'schärfe'), ('Fruehjahr', 'Frühjahr'),
                 ('muss', 'muss'), ('Loesung', 'Lösung'), ('moeglich', 'möglich'),
                 ('Moeglich', 'Möglich'), ('Schaetzer', 'Schätzer'), ('Rueck', 'Rück')):
        t = t.replace(a, b)
    t = _umlaut(t)
    t = re.sub(r'\((\d+)-\1 W\)', r'(\1 W)', t)
    return t.strip()


def hm(m):
    return "%d:%02d" % (m // 60, m % 60)


def wk(y, w):
    a = date.fromisocalendar(y, w, 1)
    return "%d.%d.–%d.%d." % (a.day, a.month, (a + timedelta(6)).day, (a + timedelta(6)).month)


L = []
L.append("# Trainingsplan bis zur Dolomitenradrundfahrt 2027\n")
L.append("> Von KW 37/2026 bis zum Rennen am **Sonntag, 13. Juni 2027** (Lienz, 112 km / 1.870 hm).")
L.append("> Die Einheiten sind nicht fest auf Wochentage gelegt — Ausnahme sind Tests, "
         "Kursbesichtigung und Rennen.\n")
L.append("**Wochenstruktur** · Winter: Mo Kraft · Di Key · Mi locker · Do Key · Fr Kraft · Sa Langfahrt  ")
L.append("**Wochenstruktur** · ab April: Mo Kraft · Di Key · Mi Volumen · Do Key · **Fr frei** · Sa Langfahrt\n")
L.append("Zwei Regeln gelten immer: zwischen zwei harten Einheiten liegt mindestens ein Tag, "
         "und die Langfahrt kommt nicht direkt nach einer Key-Session.\n")

tot_h = sum(s['min'] for *_, ss, _ in W for s in ss if s['type'] == 'Ride') / 60
tot_k = sum(s['min'] for *_, ss, _ in W for s in ss if s['type'] == 'WeightTraining') / 60
tot_t = sum(s['tss'] for *_, ss, _ in W for s in ss)
L.append("| Wochen | Einheiten | Radstunden | Kraftstunden | TSS |")
L.append("|---|---|---|---|---|")
L.append("| %d | %d | %.0f h | %.0f h | %d |\n" %
         (len(W), sum(len(x[3]) for x in W), tot_h, tot_k, tot_t))

last = None
for y, w, ph, sess, fok in W:
    real = ph if ph != "rec" else last
    if ph != "rec":
        last = ph
    rad = sum(s['min'] for s in sess if s['type'] == 'Ride')
    kra = sum(s['min'] for s in sess if s['type'] == 'WeightTraining')
    tss = sum(s['tss'] for s in sess)
    head = "## KW %02d/%d · %s" % (w, y, wk(y, w))
    if ph == "rec":
        head += " · Entlastung"
    L.append(head + "\n")
    L.append("*%s* — Rad %s h · Kraft %s · **%d TSS**\n" %
             (PHASE.get(real, real), hm(rad), (hm(kra) + " h") if kra else "—", tss))
    L.append("| Einheit | Dauer | TSS | |")
    L.append("|---|---|---|---|")
    for s in sess:
        key = "**KEY**" if s.get('key') else ""
        if s.get('tag'):
            key = (key + " " if key else "") + "(%s)" % TAG[int(s['tag']) - 1]
        L.append("| %s | %s | %d | %s |" % (clean(s['name']), hm(s['min']), s['tss'], key))
    L.append("")
    L.append("> " + clean(fok) + "\n")
    details = [s for s in sess if s.get('key') or s.get('tag')]
    if details:
        L.append("<details><summary>Details zu den Schlüsseleinheiten</summary>\n")
        for s in details:
            L.append("**%s** — %s\n" % (clean(s['name']), clean(s['desc'])))
        L.append("</details>\n")

io.open(OUT, 'w', encoding='utf-8').write("\n".join(L))
print("geschrieben:", OUT, "(%d Zeilen)" % len(L))
