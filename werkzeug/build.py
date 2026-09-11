# -*- coding: utf-8 -*-
import json, io

p1 = json.load(open('_p1.json', encoding='utf-8'))
p2 = json.load(open('_p2.json', encoding='utf-8'))
p3 = json.load(open('_p3.json', encoding='utf-8'))
C = dict(p1); C.update(p2); C.update(p3)

CSS = r"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{
  --ground:#EDF0EE; --surface:#F7F9F7;
  --ink:#16201C; --ink-2:#33413A; --muted:#5C6B63; --faint:#8A968F;
  --rule:#D2DAD5; --rule-2:#BFC9C3;
  --accent:#1F6F5C; --accent-mid:#4E9280; --accent-wash:#1F6F5C1F;
  --signal:#A83C1B; --signal-wash:#A83C1B14;
  --brass:#B3862F;
  --disp:"Barlow Condensed","Arial Narrow",sans-serif;
  --body:"Source Serif 4",Georgia,serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#111714; --surface:#171F1B;
    --ink:#E6EDE8; --ink-2:#C3D0C8; --muted:#93A29A; --faint:#6E7C75;
    --rule:#2A3630; --rule-2:#3A4841;
    --accent:#5FBFA2; --accent-mid:#3E8E77; --accent-wash:#5FBFA226;
    --signal:#E08055; --signal-wash:#E0805520;
    --brass:#D6AA57;
  }
}
:root[data-theme="dark"]{
  --ground:#111714; --surface:#171F1B;
  --ink:#E6EDE8; --ink-2:#C3D0C8; --muted:#93A29A; --faint:#6E7C75;
  --rule:#2A3630; --rule-2:#3A4841;
  --accent:#5FBFA2; --accent-mid:#3E8E77; --accent-wash:#5FBFA226;
  --signal:#E08055; --signal-wash:#E0805520;
  --brass:#D6AA57;
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font-family:var(--body);
     font-size:17px;line-height:1.62;margin:0;-webkit-font-smoothing:antialiased}
.wrap{max-width:1220px;margin:0 auto;padding:0 32px 96px}
.col{max-width:68ch}
h1,h2,h3,.zy{font-family:var(--disp);text-wrap:balance}
h1{font-size:clamp(38px,6vw,68px);line-height:1.02;font-weight:700;letter-spacing:-.01em;margin:0 0 6px}
h2{font-size:clamp(25px,3vw,34px);font-weight:600;line-height:1.12;margin:0 0 14px;letter-spacing:.005em}
h3{font-size:20px;font-weight:600;margin:0 0 6px;letter-spacing:.01em}
p{margin:0 0 15px}
strong{font-weight:600}
.eyebrow{font-family:var(--mono);font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
         color:var(--muted);margin:0 0 12px}
.lede{font-size:20px;line-height:1.55;color:var(--ink-2)}
header.top{padding:58px 0 30px;border-bottom:2px solid var(--ink)}
.meta{display:flex;flex-wrap:wrap;gap:8px 26px;font-family:var(--mono);font-size:12px;
      color:var(--muted);margin-top:20px}
section{padding:46px 0;border-bottom:1px solid var(--rule)}
section:last-of-type{border-bottom:none}
.num{font-family:var(--mono);font-size:12px;color:var(--accent);letter-spacing:.1em;
     display:block;margin-bottom:6px}
figure{margin:26px 0 8px}
.chart{width:100%;height:auto;display:block;overflow:visible}
.chart .ax{font-family:var(--mono);font-size:12px;fill:var(--faint)}
.chart .val{font-family:var(--mono);font-size:12.5px;fill:var(--ink-2);font-weight:500}
.chart .pk{font-family:var(--disp);font-size:15.5px;font-weight:600;fill:var(--ink)}
.chart .pkm{font-family:var(--mono);font-size:11.5px;fill:var(--muted)}
.chart .mk{font-family:var(--mono);font-size:12px;fill:var(--signal)}
.chart .mkb{font-family:var(--mono);font-size:13px;font-weight:600;fill:var(--signal)}
.chart .zl{font-family:var(--mono);font-size:12.5px;fill:#FFFFFF;font-weight:500}
.chart .zy{font-size:16px;font-weight:600;fill:var(--ink)}
figcaption{font-family:var(--mono);font-size:12px;color:var(--muted);line-height:1.5;
           margin-top:10px;max-width:96ch}
@media (max-width:780px){
  .scroll::after{content:"→ seitwärts scrollbar";display:block;font-family:var(--mono);
                 font-size:10.5px;color:var(--faint);padding:5px 0 0;letter-spacing:.05em}
}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;
        scrollbar-width:thin;padding-bottom:2px}
.scroll>.chart{min-width:740px}
.scroll>table{min-width:600px}
.scroll>table.plan{min-width:640px}
.stats{display:grid;gap:1px;background:var(--rule);border:1px solid var(--rule);
       margin:30px 0 6px;grid-template-columns:repeat(4,1fr)}
.stats.s3{grid-template-columns:repeat(3,1fr)}
@media (max-width:900px){.stats,.stats.s3{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--surface);padding:15px 16px}
.stat dt{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
         color:var(--muted);margin-bottom:5px}
.stat dd{margin:0;font-family:var(--disp);font-size:29px;font-weight:600;line-height:1;
         font-variant-numeric:tabular-nums}
.stat .d{font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:5px;font-weight:400;
         display:block;line-height:1.4}
.up{color:var(--accent)}
.dn{color:var(--signal)}
.fix{border-left:3px solid var(--signal);background:var(--signal-wash);padding:14px 18px;margin:0 0 14px}
.fix h3{font-size:17px;margin-bottom:4px;color:var(--signal)}
.fix p{margin:0;font-size:15.5px;color:var(--ink-2)}
.fix p+p{margin-top:8px}
.levers{display:grid;gap:1px;background:var(--rule);border:1px solid var(--rule);margin:24px 0}
.lever{background:var(--surface);padding:22px 24px;display:grid;grid-template-columns:52px 1fr;gap:20px}
.lever .rank{font-family:var(--disp);font-size:40px;font-weight:700;color:var(--accent);line-height:.9}
.lever h3{margin-bottom:8px}
.lever p{font-size:15.5px;margin-bottom:9px;color:var(--ink-2)}
.lever .eff{font-family:var(--mono);font-size:12.5px;color:var(--accent);
            border-top:1px solid var(--rule);padding-top:9px;margin:0;line-height:1.5}
table{width:100%;border-collapse:collapse;font-size:14px;margin:8px 0}
th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
   color:var(--muted);font-weight:500;border-bottom:1px solid var(--rule-2)}
td.n{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}
.yr{font-family:var(--disp);font-size:19px;font-weight:700;color:var(--accent)}
.phase{display:grid;grid-template-columns:140px 1fr;gap:22px;padding:20px 0;
       border-top:1px solid var(--rule)}
.phase:last-of-type{border-bottom:1px solid var(--rule)}
.phase .when{font-family:var(--mono);font-size:12.5px;color:var(--accent);font-weight:500;line-height:1.5}
.phase h3{font-size:18px}
.phase p{font-size:15.5px;margin-bottom:8px;color:var(--ink-2)}
.phase .goal{font-family:var(--mono);font-size:12.5px;color:var(--ink);background:var(--accent-wash);
             padding:8px 12px;line-height:1.55;margin:0}
ol.acts{list-style:none;counter-reset:a;padding:0;margin:20px 0 0}
ol.acts li{counter-increment:a;position:relative;padding:0 0 20px 50px;margin-bottom:20px;
           border-bottom:1px solid var(--rule)}
ol.acts li:last-child{border-bottom:none;margin-bottom:0;padding-bottom:0}
ol.acts li::before{content:counter(a,decimal-leading-zero);position:absolute;left:0;top:1px;
                   font-family:var(--mono);font-size:13px;color:var(--accent);font-weight:600}
ol.acts h3{font-size:17px;margin-bottom:5px}
ol.acts p{font-size:15.5px;margin:0;color:var(--ink-2)}
ul.plain{padding-left:20px;margin:0 0 15px}
ul.plain li{margin-bottom:9px;color:var(--ink-2)}
.verdict{background:var(--surface);border:1px solid var(--rule-2);padding:26px 30px;margin:24px 0}
.verdict .pct{font-family:var(--disp);font-size:52px;font-weight:700;color:var(--brass);
              line-height:1;margin-bottom:2px}
.verdict .pl{font-family:var(--mono);font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;
             color:var(--muted);margin-bottom:16px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:34px}
/* Wochenplan */
table.plan{font-size:14px}
table.plan td{padding:13px 12px;vertical-align:top}
tr.phrow td{background:var(--ink);padding:9px 14px;border:none}
.pht{font-family:var(--disp);font-size:19px;font-weight:600;color:var(--ground);letter-spacing:.01em}
.phs{font-family:var(--mono);font-size:11px;color:var(--ground);opacity:.72;margin-left:12px;
     letter-spacing:.08em;text-transform:uppercase}
tr.recw{background:var(--accent-wash)}
.rtag{display:block;font-family:var(--mono);font-size:9.5px;letter-spacing:.09em;
      text-transform:uppercase;color:var(--accent);margin-top:5px}
.wkc{min-width:104px}
.dt{display:block;font-family:var(--mono);font-size:10.5px;color:var(--muted);
    font-weight:400;margin-top:3px;letter-spacing:.02em}
ul.sess{list-style:none;padding:0;margin:0}
li.se{border-bottom:1px dotted var(--rule);padding:0 0 7px;margin-bottom:7px}
li.se:last-child{border-bottom:none;padding-bottom:0;margin-bottom:0}
li.se.kraft .sn{color:var(--muted)}
.sh{display:flex;flex-wrap:wrap;align-items:baseline;gap:5px 9px}
.sn{font-family:var(--disp);font-size:16.5px;font-weight:600;color:var(--ink);letter-spacing:.01em}
.sm{font-family:var(--mono);font-size:12px;color:var(--ink-2);font-variant-numeric:tabular-nums}
.st{font-family:var(--mono);font-size:12px;color:var(--accent);font-weight:600;
    font-variant-numeric:tabular-nums;margin-left:auto}
.kk{font-family:var(--mono);font-size:9px;letter-spacing:.1em;background:var(--accent);
    color:var(--ground);padding:1px 5px;border-radius:2px;vertical-align:1px}
.sd{margin:3px 0 0;font-size:13.5px;line-height:1.45;color:var(--ink-2)}
.fok{margin:9px 0 0;font-size:13.5px;color:var(--ink-2);line-height:1.5;
     border-top:1px solid var(--rule);padding-top:8px}
footer{padding:38px 0 0;font-family:var(--mono);font-size:12px;color:var(--faint);line-height:1.65}
@media (max-width:560px){
  .wrap{padding:0 12px 48px}
  body{font-size:15.5px}
  .lede{font-size:17.5px}
  .verdict{padding:18px 16px}
  .verdict .pct{font-size:40px}
  .lever{padding:16px 15px}
  .fix{padding:12px 13px}
  ol.acts li{padding-left:34px}
}
@media (max-width:820px){
  .wrap{padding:0 18px 60px}
  .two{grid-template-columns:1fr;gap:22px}
  .lever{grid-template-columns:1fr;gap:8px}
  .lever .rank{font-size:30px}
  .phase{grid-template-columns:1fr;gap:8px}
  body{font-size:16px}
}
@media (prefers-reduced-motion:reduce){*{animation:none !important;transition:none !important}}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
</style>
"""

def stat(label, value, detail, cls=""):
    c = ' class="%s"' % cls if cls else ""
    return ('<div class="stat"><dt>%s</dt><dd%s>%s</dd>'
            '<span class="d">%s</span></div>') % (label, c, value, detail)

STATS_NOW = "".join([
    stat("Alter", "35", "Jahrgang 1990<br>beim Zielversuch 39–40", "up"),
    stat("Fitness CTL", "65,6", "Peak 73,0 am 30.08.<br>TSB +6,6 — frisch"),
    stat("FTP", "271 W", "30-Min-Test 05.09.2026<br>MyWhoosh indoor"),
    stat("Gewicht", "76,5 kg", "von 81,0 kg im Mai<br>&minus;4,5 kg in der Saison"),
    stat("Leistung", "3,54 W/kg", "sub-8 verlangt ≈5,0<br>Lücke +41 %", "dn"),
    stat("Ruhepuls", "51", "Tiefstwert der Aufzeichnung<br>Februar noch 60", "up"),
    stat("Längste Fahrt", "3,6 h", "Ötztaler dauert 8 h<br>null Fahrten über 4 h", "dn"),
    stat("Wettkämpfe", "0", "in 598 Aktivitäten<br>keine Rennerfahrung", "dn"),
])

STATS_YEAR = "".join([
    stat("Radstunden", "172", "2025: 78 h<br>+119 %", "up"),
    stat("Kilometer", "4.627", "2025: 1.811<br>+155 %", "up"),
    stat("Höhenmeter", "31.142", "2025: 15.922<br>6,8 hm/km", "up"),
    stat("Trainingslast", "8.623", "TSS gesamt<br>2025: 3.786", "up"),
    stat("Einheiten", "115", "in 25 Wochen<br>Median 6,5 h/Woche"),
    stat("Wettkämpfe", "0", "in 598 Aktivitäten<br>keine Rennreferenz", "dn"),
])

ROADMAP = [
    ("2027", "36", "305–315 W", "4,12–4,26", "74 kg", "85–90", "550–590 h", "8:45–9:00",
     "Den 10,5-h-Block von 6 auf 20 Wochen verlängern — Saisonschnitt 13 h. Erste 5-Stunden-Fahrt. "
     "Zwei Marathons als Wettkampf. Abfahrtstechnik als eigenes Trainingsziel."),
    ("2028", "37", "330–340 W", "4,55–4,69", "72,5 kg", "95–100", "620–660 h", "8:20–8:40",
     "Erstteilnahme Ötztaler als Erfahrungsfahrt — Massenstart, Verpflegung über 8 h, "
     "Timmelsjoch-Abfahrt bei Kälte und Müdigkeit. Langfahrten auf 6 h. Zeit ist Nebensache."),
    ("2029", "38", "345–355 W", "4,86–5,00", "71 kg", "100–105", "650–700 h", "8:10–8:30",
     "Erster ernsthafter Zielversuch. Drei Fahrten über 6 h, eine Distanzsimulation über "
     "220 km. Durability-Test: 20 min all-out nach 2.500 kJ, Ziel unter 10 % Abfall."),
    ("2030", "39", "355–365 W", "5,07–5,21", "70 kg", "100–105", "650–700 h", "8:05–8:20",
     "Zweiter Zielversuch mit vollem Taper. Renngewicht steht, ab hier wird nicht mehr "
     "abgenommen. Bei Verfehlen dritter Versuch 2031 mit 40 — physiologisch unproblematisch."),
]
rm_rows = "".join(
    '<tr><td class="yr">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td>'
    '<td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td>'
    '<td>%s</td></tr>' % r
    for r in ROADMAP)

PHASES = [
    ("Okt 2026", "KW 40–44 · 6–7 h",
     "Messbasis reparieren, Kraft anfahren",
     "Bevor der Block startet, brauchst du die Zahl, auf die er sich bezieht: <strong>5-Minuten-Maximaltest</strong>, indoor, eigener Tag, Openers am Vortag. Ohne ihn sind alle VO2-Vorgaben geraten — deine 288 W sind ein Testartefakt. Sonst: 85 % Z1/Z2, eine Sweetspot-Einheit, Kraft zweimal wöchentlich technikorientiert anfahren. Rollentrainer, Lüfter und Abo jetzt aufbauen und einmal in einer 90-Minuten-Einheit testen, nicht erst im November.",
     "CTL Ende Oktober 47–49 · 5-Minuten-Wert dokumentiert, Erwartung 300–320 W · Gewicht 76–78 kg"),
    ("Nov–Dez 2026", "KW 44–52 · 8 h",
     "Zwei Qualitätseinheiten, Maximalkraft, Langfahrtprogression",
     "Key 1 ist VO2 in kleiner Dosis — 3&times;4 min zum Einstieg, bis KW50 auf 4&times;5 min. Key 2 ist Sweetspot (2&times;20 → 3&times;20), ab Dezember Schwelle 3&times;12. Dazu die Kraft in der Maximalkraftphase mit 4–6 Wiederholungen und die Langfahrt progressiv 2:30 → 3:30 mit 80 g Kohlenhydraten pro Stunde. Das ist die dichteste Phase des Winters: zwei harte Radeinheiten plus zweimal schweres Heben. Wenn etwas weichen muss, ist es die lockere Stunde — nie eine Key-Session.",
     "CTL Ende Dezember 44–46 (Vorjahr: 13,7) · Belastungswochen 376–388 TSS auf dem Rad · keine Lücke über vier Tage · längste Fahrt 3:30 h · Gewicht 75–76 kg"),
    ("Jan–Feb 2027", "KW 1–8 · 8 h",
     "Der konzentrierte VO2-Block — jetzt werden beide Keys VO2",
     "Acht Wochen, in denen die zweite Qualitätseinheit von Schwelle auf VO2 wechselt. Das ist die Steigerung, auf die November und Dezember hinarbeiten — und der eigentliche Fortschritt gegenüber 2026, wo nur 3 von 25 Wochen überhaupt zwei harte Einheiten hatten und im ganzen Jahr 4,3 Stunden Z5 zusammenkamen. Format 4–5&times;4–5 min bei 105–115 %, ab KW5 30/15 nach Rønnestad aufbauend von 2&times;10 auf 3&times;13 Wiederholungen. Alles indoor — kein Wind, keine Kreuzungen, kein Ein-Grad-Start. Kraft auf einmal pro Woche reduzieren und <strong>kein Kaloriendefizit</strong>: Intensitätsblock und Defizit vertragen sich nicht.",
     "Mindestens 10 VO2-Einheiten mit je 16–20 min über 105 % · CTL 45–48 gehalten · Februar-Mindeststandard 16 Trainingstage (2026: null) · 5-Minuten-Retest Ende Februar, Ziel +15–25 W"),
    ("Mär 2027", "KW 9–13 · 8–10 h",
     "Schwelle und die erste 4-Stunden-Fahrt — indoor geplant, outdoor als Bonus",
     "Der März ist in Kärnten kein verlässlicher Straßenmonat: 2026 waren es zwei Outdoor-Fahrten, 2025 keine, und deine erste Ausfahrt des Jahres war der 28.03. Deshalb ist dieser Block <strong>indoor geplant</strong> — jede Einheit, die das Wetter draußen erlaubt, ist ein Gewinn, aber nichts hängt davon ab. Intensität von VO2 zurück auf Schwelle und Sweetspot; sobald es draußen geht, wandern die Intervalle an einen echten Anstieg. Der 20-Minuten-Test draußen mit dem SRAM ist nicht an den März gebunden: wenn das Wetter nicht mitspielt, rückt er in die erste brauchbare Aprilwoche.",
     "Erste Fahrt über 4:00 h und 2.600 kJ · CTL Ende März 48–49 (Vorjahr: 3,9) · 20-Min-Test outdoor sobald das Wetter es zulässt"),
    ("Apr–Jun 2027", "Übergang · 10 → 13 h",
     "Die Umfangsrampe — nicht höher, sondern länger",
     "Die Aufgabe ist nicht, eine neue Spitzenwoche zu fahren — 14,1 h stehen bereits in deinen Daten. Sie ist, den <strong>Block</strong> zu verlängern: dein bestes 6-Wochen-Mittel lag bei 10,5 h und 559 TSS, und die CTL war dabei noch im Anstieg. Genau dieses Niveau über zwanzig statt sechs Wochen zu halten, bringt die CTL von 73 auf 85–90 — ohne dass eine einzige Woche härter wird als das, was du im August schon gefahren bist. Steigerung trotzdem maximal +10–15 % pro Woche, fixer 3:1-Rhythmus, Entlastungswoche steht im Kalender bevor der Block anfängt.",
     "Kernsaison-Schnitt 13 h/Woche über mindestens 20 Wochen · CTL-Peak 85–90 · Gewicht 74 kg · Defizit maximal 0,25 kg/Woche und nie im selben Block wie eine Umfangssteigerung"),
]
ph_html = "".join(
    '<div class="phase"><div class="when">%s<br><span style="color:var(--muted)">%s</span></div>'
    '<div><h3>%s</h3><p>%s</p><p class="goal">%s</p></div></div>' % p for p in PHASES)

LEVERS = [
    ("Winterkontinuität — CTL nie unter 45",
     "Der einzige Hebel, der deine Jahresprogression verdoppelt, ohne eine einzige zusätzliche Sommerstunde. 2026 hast du im Sommer +65 W eFTP aufgebaut; von Saisonpeak zu Saisonpeak blieben netto +34 W übrig. Der Rest ging über den Winter verloren. Beim Gewicht dasselbe Muster: in der Saison &minus;0,20 kg pro Woche, netto über 13 Monate statistisch null.",
     "Verbindliche Untergrenze Oktober bis März: vier Radtage pro Woche à mindestens 45 Minuten, mindestens 300 TSS auf dem Rad (Kraft zählt bei deiner 0-%-Einstellung nicht in die Fitness). Indoor zählt voll — im Herbst 2025 kamen 100 % deiner Rad-TSS von der Rolle, das Verhalten ist da. Statt Abbruch eine Eskalationsregel: wenn der 7-Tage-Ruhepuls 3 bpm über dem 28-Tage-Mittel liegt oder der Schlaf fünf Tage unter 7 h fällt, Last halbieren — aber die Frequenz halten.",
     "Netto-Jahresprogression steigt von +34 W auf +45–55 W. Über vier Jahre rund 50–80 W Unterschied — mehr als jeder Trainingsinhalt, den man diskutieren könnte."),
    ("Dauer und Verpflegung als eigenes Ziel",
     "Deine größte Fahrt aller Zeiten sind 2.120 kJ über 3,1 Stunden. Der Ötztaler verlangt rund 5.400–6.000 kJ. Das ist Faktor 2,6 — und es ist kein Nebenprodukt von FTP-Training. Darm, Sitzfleisch, Pacing und Fettstoffwechsel über sechs Stunden trainieren sich nur, wenn man sechs Stunden fährt. Genau deshalb braucht es mehrere Saisons und nicht ein Vorbereitungsjahr.",
     "Feste kJ-Progression statt Stundenzählerei: größte Einzelfahrt von 2.120 kJ (2026) auf 3.000 (2027), 4.000 (2028), 5.000 (2029), 5.500 (2030). Verpflegung nach Regel statt nach Gefühl: unter 90 Minuten nichts, ab zwei Stunden mindestens 80 g/h, ab drei Stunden und auf allen Intensitätseinheiten 90–100 g/h mit Glukose-Fruktose-Mischung.",
     "Ohne diese Schiene brichst du nach Modellrechnung am Jaufen oder im ersten Drittel Timmelsjoch ein — unabhängig davon, wie hoch die FTP steht."),
    ("Kletterdichte, Abfahrt und Gruppe — der Inhalt, nicht der Umfang",
     "Zwei Zahlen: dein Training 2026 hatte 6,8 Höhenmeter pro Kilometer, der Ötztaler hat 24,2. Und bei identischer Form — 350 W bei 70 kg — reicht die modellierte Zielzeit von 7:17 bis 9:14, je nachdem wie du fährst. Zwei Stunden Spanne ohne ein Watt Unterschied. Sicheres Abfahren ist bis zu 20 Minuten wert, Gruppenanschluss am Brenner 12, kurze Labestopps 9, Pacing-Disziplin am Berg nochmal 10.",
     "Erstens: eine Pendelrichtung über Bleiberg statt durchs Tal — rund 450 Höhenmeter für kaum Zusatzzeit, bei drei Doppeltagen 1.350 hm pro Woche. Zweitens: ab dem Frühjahr jede Abfahrt bewusst fahren statt herunterrollen, und regelmäßig in einer Gruppe, weil Windschattenfahren nichts mit Alleinfahren zu tun hat. Drittens: die Verpflegung so üben, dass du an den Labestationen Flaschen tauschst statt zu stehen. Du bist 2011 bis 2015 Bergrennen und Marathons gefahren — das sind eingeschlafene Fertigkeiten, keine fehlenden. Sie kommen schneller zurück, als sie beim ersten Mal gekommen sind.",
     "Die Kletterdichte ist der größte inhaltliche Hebel, die Ausführung 20 bis 25 Minuten — zusammen mehr, als ein ganzes Jahr Formaufbau bringt. Und beides kostet keine einzige zusätzliche Trainingsstunde."),
]
lev_html = "".join(
    '<div class="lever"><div class="rank">%d</div><div><h3>%s</h3><p>%s</p><p>%s</p>'
    '<p class="eff">%s</p></div></div>' % (i + 1, l[0], l[1], l[2], l[3])
    for i, l in enumerate(LEVERS))

ACTS = [
    ("Messbasis reparieren — 30 Minuten Aufwand",
     "In den intervals.icu-Sport-Settings <code>ftp_est_min_secs</code> von 180 auf 720 Sekunden setzen. Sechs von elf eFTP-Sprüngen stammen aus Drei-Minuten-Bergsprints, nicht aus Schwellenarbeit. Und die <code>[Garmin HR] Non-cycling load</code>-Einträge aus der Radfitnesskurve nehmen: 34 Einträge, 2.124 TSS — im Januar 2026 waren das 100 % deiner Monatslast."),
    ("Frischer 5-Minuten-Maximaltest",
     "Indoor auf MyWhoosh, exakt dasselbe Setup wie am 05.09., an einem eigenen Tag mit Openers am Vortag. Das ist die wertvollste Einzelmessung, die du machen kannst: die Kurve zwischen drei und fünfzehn Minuten ist leer, W&prime; hängt an einem einzigen 100-Sekunden-Wert, und ohne diesen Punkt ist jede VO2-Vorgabe für den Winter geraten. Erwartungswert 300–320 W — aus deinen 7&times;4 min bei 278 W am 27.08. ist deutlich mehr als 288 W ableitbar."),
    ("Winter verbindlich machen, bevor Oktober anfängt",
     "Rollentrainer, Lüfter und Abo aufbauen und einmal in einer 90-Minuten-Einheit testen. Mindeststandard schriftlich fixieren und bis 31.03.2027 in den Kalender eintragen. Dein Bruchpunkt liegt historisch beim Übergang November/Dezember, nicht im Februar — im Februar ist es längst zu spät."),
    ("Zwei Anmeldungen erledigen",
     "Die Ötztaler-Verlosung ist gedächtnislos, es gibt keine Warteliste, die sich ansammelt — ab jetzt jedes Jahr anmelden, unabhängig davon, ob das Jahr sportlich passt. Wirst du 2027 gezogen: fahren, aber als reine Erfahrungsfahrt ohne jede Zeitambition. Dazu ein reales Zielrennen für Juni 2027 fixieren. Ohne Zieltermin gibt es nichts zu periodisieren — 2026 lief ohne einen einzigen Wettkampf."),
    ("Waage und Blutbild",
     "WLAN-Waage, täglich nüchtern, gesteuert wird ausschließlich über den 7-Tage-Mittelwert. 17 Messungen in 399 Tagen mit einer 217-Tage-Lücke sind für ein mehrjähriges Gewichtsprojekt unbrauchbar — und W/kg ist der Nenner der gesamten Ötztaler-Rechnung. Dazu ein Blutbild: Ferritin, Transferrinsättigung, Vitamin D, TSH mit fT3. Der Februar 2026 gehört geklärt, bevor der nächste Winter anfängt."),
]
act_html = "".join('<li><h3>%s</h3><p>%s</p></li>' % a for a in ACTS)

HTML = """<title>Zurück aufs Rennrad</title>
%s
<div class="wrap">

<header class="top">
  <p class="eyebrow">Trainingsanalyse · intervals.icu i378091 · Stand 7. September 2026</p>
  <h1>Zurück aufs Rennrad</h1>
  <p class="lede col">Ein Comeback-Jahr, ausgewertet gegen ein Ziel, das vier Jahre entfernt liegt:
  der Ötztaler Radmarathon unter acht Stunden. 598 Aktivitäten, 1.436 Tage Wellness-Historie,
  und die unbequeme Frage, woran es wirklich hängt.</p>
  <div class="meta">
    <span>598 Aktivitäten</span><span>2013–2026</span>
    <span>172 Radstunden in 2026</span><span>Hermagor, Kärnten</span>
  </div>
</header>

<section>
  <span class="num">DAS ZIEL</span>
  <h2>227 Kilometer, 5.500 Höhenmeter, vier Pässe</h2>
  <div class="scroll">%s</div>
  <figcaption>Höhenprofil des Ötztaler Radmarathons. Die vier Anstiege verteilen sich sehr
  ungleich: Kühtai, Jaufenpass und Timmelsjoch sind mit zusammen 62,7 km und 4.166 hm die
  eigentliche Arbeit (Schnitt 6,6 %%), während der Brenner über 38 km nur 780 hm steigt — ein
  Ziehweg, den man in der Gruppe fährt. Auf die 121 Abfahrtskilometer entfällt kaum Leistung,
  aber viel Zeit.</figcaption>
  <div class="col" style="margin-top:26px">
  <p>Für acht Stunden brauchst du auf den drei Steilanstiegen eine VAM von rund 1.040 Höhenmetern
  pro Stunde. Bei 70 kg sind das etwa <strong>260 Watt am Berg</strong>, gehalten über vier Stunden
  reine Kletterzeit, verteilt über einen achtstündigen Tag. Rechnet man realistisch 15 bis 20 Minuten
  Standzeit an den Labestationen ein, verlangt sub-8 rund <strong>345 bis 360 Watt FTP bei 70 kg</strong>
  — also 4,9 bis 5,1 W/kg.</p>
  <p>Dein selbst gesetztes Ziel von 350 W bei 70 kg ist damit ungefähr richtig kalibriert und liegt
  eher am unteren Rand. Es sollte nicht abgesenkt werden.</p>
  </div>
</section>

<section>
  <span class="num">STANDORT</span>
  <h2>Wo du heute stehst</h2>
  <dl class="stats">%s</dl>
  <div class="col" style="margin-top:26px">
  <p>Der sauberste Vergleich, den die Daten hergeben, ist Gerät gegen Gerät auf derselben Plattform:
  <strong>20 Minuten mit 249 W am 13.09.2025, 281 W am 05.09.2026</strong>. Das sind +12,9 % in
  zwölf Monaten bei einem Kilo weniger. Unabhängig davon belegt der Efficiency Factor die aerobe
  Anpassung innerhalb der Saison: Monatsmedian 1,02 im April auf 1,28 im August, bei praktisch
  gleicher Durchschnittsleistung und einer von 147,6 auf 140,2 gefallenen Herzfrequenz.</p>
  <p>Das ist ein gelungenes erstes Comeback-Jahr. Kein Scherbenhaufen — und auch keine Basis,
  von der aus sub-8 in Reichweite wäre.</p>
  </div>
</section>

<section>
  <span class="num">KORREKTUREN</span>
  <h2>Was die Daten <em>nicht</em> sagen</h2>
  <p class="col">Fünf Befunde, die auf den ersten Blick dramatisch aussehen und bei genauer Prüfung
  verschwinden. Sie stehen hier, weil du ihnen sonst in intervals.icu wieder begegnest — und weil
  drei davon in meiner eigenen ersten Auswertung standen.</p>
  <div class="col">
  <div class="fix"><h3>Die CTL ist nicht auf 9,7 kollabiert</h3>
    <p>Das ist die Vorwärtsprojektion von intervals.icu in einen leeren Kalender. 90 Einträge in
    der Wellness-Datei liegen nach deinem letzten Trainingstag. Real stehst du am 07.09. bei
    <strong>CTL 65,6 mit TSB +6,6</strong> — frisch und in Form.</p></div>
  <div class="fix"><h3>Deine 5-Minuten-Leistung ist keine Schwäche</h3>
    <p>Die auffällig flache Kurve zwischen 5 und 30 Minuten (288 / 284 / 283 / 281 / 277 W) stammt
    vollständig aus <em>einer</em> Fahrt: dem 30-Minuten-Test vom 05.09. Eine gleichmäßige
    Dauerbelastung erzeugt zwangsläufig eine flache Kurve. Die 288 W sind das beste
    Fünf-Minuten-Fenster innerhalb eines Tests — kein Maximalwert.</p>
    <p>Dass du am 29.08. <strong>462 W über zwei Minuten</strong> gefahren bist, spricht für einen
    echten Fünf-Minuten-Wert um 300–320 W. Auch der VO2max-Schätzwert von 50,0 hängt an diesem
    Artefakt und ist zu niedrig.</p></div>
  <div class="fix"><h3>Kein Durability-Einbruch bei 60 Minuten</h3>
    <p>Der scheinbare Absturz von 277 W auf 223 W vergleicht zwei verschiedene Fahrten. Der
    60-Minuten-Wert ist die beste Stunde einer 2,5-stündigen Trainingsfahrt, kein Maximaleffort.
    Deine Ermüdungsresistenz ist nicht schlecht — sie ist <em>ungetestet</em>.</p></div>
  <div class="fix"><h3>Der Z3-Anstieg ist großteils ein Zonenartefakt</h3>
    <p>110 von 115 Radfahrten in 2026 wurden gegen eine hinterlegte FTP von 236 W ausgewertet,
    während deine reale FTP im August längst darüber lag. Die Z2/Z3-Grenze saß damit bei 177 statt
    199 Watt — 22 Watt zu tief. Ein erheblicher Teil der 27,7 als Z3 gezählten Stunden ist bei
    korrekter FTP schlicht Z2. Der Sprung von 9,7 auf 17,2 % taugt nicht als Begründung, die
    Intensitätsverteilung umzustellen.</p></div>
  <div class="fix"><h3>Deine Vorgeschichte ist unprüfbar, nicht widerlegt</h3>
    <p>Alle 375 Aktivitäten vor 2023 sind leere Strava-Platzhalter mit dem Vermerk
    <em>&bdquo;STRAVA activities are not available via the API&ldquo;</em> — kein Gewicht, keine Watt,
    kein Feld außer dem Datum. Deine Angabe von 64 kg und 300 W ist daraus weder belegbar noch
    widerlegbar. Was bleibt: 91 Aktivitäten in 2014, 186 in 2015. Die Vorgeschichte ist plausibel,
    nur nicht messbar — und als Planungsanker deshalb unbrauchbar.</p></div>
  </div>
</section>

<section>
  <span class="num">DER JAHRESVERLAUF</span>
  <h2>Ein Aufbau, der bei null anfangen musste</h2>
  <div class="scroll">%s</div>
  <figcaption>Fitness (CTL, gefüllte Fläche) und Ermüdung (ATL, dünne Linie), Juni 2025 bis
  September 2026. Die markierte Zone ist die Winterpause.</figcaption>
  <div class="col" style="margin-top:24px">
  <p>Zwischen dem 11. Dezember 2025 und dem 28. März 2026 liegen <strong>107 Tage ohne eine
  einzige Radfahrt</strong>, darin 47 Tage ganz ohne Aktivität. Deine CTL fiel von 32,7 auf 3,9.
  Der gesamte Aufbau 2026 — 22 zusammenhängende Wochen von CTL 3,9 auf 73,0, im Mittel +2,97 pro
  Woche — war Wiederaufbau von einem Punkt, an dem du im Dezember schon einmal warst.</p>
  <p>Das ist der teuerste Posten in deiner Bilanz. Im Sommer hast du +65 W eFTP aufgebaut; von
  Saisonhöhepunkt zu Saisonhöhepunkt blieben netto +34 W. Beim Gewicht ist der Effekt noch
  deutlicher: in der Saison verlierst du 0,20 kg pro Woche, über 13 Monate gerechnet ist der
  Trend statistisch nicht von null zu unterscheiden.</p>
  </div>
  <div class="scroll" style="margin-top:34px">%s</div>
  <figcaption>Radstunden je Monat. Januar und Februar 2026 fehlen in dieser Reihe vollständig,
  weil es in beiden Monaten keine einzige Radeinheit gab.</figcaption>
</section>

<section>
  <span class="num">ENTWICKLUNG</span>
  <h2>Form, Gewicht und Ruhepuls laufen zusammen</h2>
  <div class="scroll">%s</div>
  <figcaption>eFTP in Watt (durchgezogen, linke Achse), Gewicht (gestrichelt) und Ruhepuls
  (gepunktet). Die markierte Zone ist wieder der Winter — der eFTP-Abfall dort ist überwiegend
  Zerfallsalgorithmus, kein gemessener Formverlust: zwischen 13.09.2025 und 21.05.2026 gibt es
  keinen einzigen Wert, der den Schätzer heben könnte.</figcaption>
  <div class="col" style="margin-top:24px">
  <p>Die Abnahme selbst ist sauber gemacht. Minus 0,25 kg pro Woche bei gleichzeitig steigender
  Leistung, besserem Schlaf und fallendem Ruhepuls schließt eine relevante Unterversorgung für
  Mai bis September praktisch aus. Bei acht Stunden Schlafmedian über 344 Nächte hast du außerdem
  eine Erholungsbasis, die deutlich mehr Volumen tragen würde als du dir derzeit zumutest.</p>
  </div>
</section>

<section>
  <span class="num">LEISTUNGSPROFIL</span>
  <h2>Du kennst dein eigenes Profil noch nicht</h2>
  <div class="scroll">%s</div>
  <figcaption>Bestleistungen nach Dauer, logarithmische Zeitachse. Der markierte Bereich stammt
  vollständig aus dem 30-Minuten-Test — dort liegt kein zweiter Datenpunkt.</figcaption>
  <div class="col" style="margin-top:24px">
  <p>Du hast genau einen echten Maximalwert: 30 Minuten. Alles andere ist Beifang aus
  Trainingsfahrten. Damit sind MAP, VO2max und das Verhältnis von FTP zu MAP derzeit nicht
  bestimmbar — und jede VO2-Intervallvorgabe für den Winter wäre geraten. Ein einzelner
  Fünf-Minuten-Test schließt diese Lücke und korrigiert vier Größen auf einmal.</p>
  <p>Was die Daten schon zeigen: mit 554 W über eine Minute und 462 W über zwei Minuten hast du
  einen brauchbaren anaeroben Bereich. Für einen Alpenmarathon ist das die am wenigsten
  wichtige Eigenschaft — aber es spricht dafür, dass oben noch Luft ist.</p>
  </div>
  <div class="scroll" style="margin-top:34px">%s</div>
  <figcaption>Verteilung der Trainingszeit auf die Leistungszonen. Achtung: für 2026 gegen eine
  hinterlegte FTP von 236 W gerechnet — der Z3-Block ist dadurch zu groß, ein Teil davon ist
  real Z2.</figcaption>
</section>

<section>
  <span class="num">DIE LÜCKE</span>
  <h2>Was zwischen dir und acht Stunden liegt</h2>
  <div class="scroll">%s</div>
  <figcaption>Watt pro Kilogramm: heute, die Jahresmeilensteine der Roadmap, und die Anforderung
  für sub-8 inklusive realistischer Standzeit.</figcaption>
  <div class="col" style="margin-top:24px">
  <p>Mit heutigem Stand — FTP 271 bei 76,5 kg — modelliert die Rechnung eine Ötztaler-Zeit von
  rund <strong>9:25 Stunden</strong>. Bis sub-8 fehlen etwa +75 bis +85 Watt bei gleichzeitig
  &minus;6,5 kg, also rund 39 % mehr W/kg.</p>
  <p>Das ist physiologisch nicht ausgeschlossen: +13 % im zweiten Comeback-Jahr sind belegt, und
  dein Schlaf trägt mehr Training als du machst. Der Engpass ist arithmetisch. Sub-8 verlangt eine
  Dauerbelastbarkeit von CTL 85–95; bei deiner Dichte von etwa 50 TSS pro Stunde sind das 12 bis 14
  Stunden pro Woche, ganzjährig, ab 2029. Dein Jahresmedian liegt bei 6,5 Stunden, und der
  Arbeitsweg bindet davon rund ein Viertel als nicht disponible Transportzeit.</p>
  <p><strong>Sub-8 scheitert nicht an der Physiologie und nicht an der Waage.</strong> Es
  entscheidet sich an der Frage, ob zwölf Stunden pro Woche in dein Leben passen.</p>
  </div>
</section>

<section>
  <span class="num">PRIORITÄTEN</span>
  <h2>Die drei Hebel, in dieser Reihenfolge</h2>
  <div class="levers">%s</div>
</section>

<section>
  <span class="num">WINTER 2026/27</span>
  <h2>Der Winter hat genau eine Aufgabe: die Basis halten</h2>
  <p class="col">Die CTL darf zu keinem Zeitpunkt unter 45 fallen — im letzten Winter waren es 3,9.
  Zielband 48 bis 58 durchgehend von Oktober bis März, Wintergewicht im Toleranzband 76–78 kg ohne
  Defizit, und am Ende des Winters eine Fahrt über vier Stunden: die erste deiner Aufzeichnung.
  Alles, was 2027 möglich ist, entscheidet sich zwischen dem 15. November und dem 15. März.</p>
  <p class="col"><strong>Wochenstruktur:</strong> 6,5–8 h in fünf bis sechs Einheiten, davon zwei
  bis vier indoor. Fixer 3:1-Rhythmus mit geplanter Entlastungswoche bei 55–65 %% der
  Belastungswoche. Mindeststandard, der nie unterschritten wird: vier Radtage à 45 Minuten und
  300 TSS pro Woche, auch in einer schlechten Woche. <em>Frequenz vor Stunden.</em></p>
  %s
</section>

<section>
  <span class="num">SAISON 2027</span>
  <h2>Das Jahr, in dem du lange fahren und Rennen fahren lernst</h2>
  <div class="col">
  <p>Nicht das Jahr des FTP-Rekords. Drei harte Zielgrößen: eine Fahrt über fünf Stunden und
  3.000 kJ mit 90 g Kohlenhydraten pro Stunde; mindestens zwei echte Alpenmarathons als Wettkampf
  gefahren; FTP zum Saisonende 295–305 W bei 74 kg. Alles davon ist bei 7–9 h pro Woche erreichbar.</p>
  <p>Der Ötztaler ist 2027 explizit kein Thema. Eine sub-8-Pacing-Strategie würde nach Modell
  spätestens am Jaufen kollabieren.</p>
  </div>
  <div class="scroll" style="margin-top:20px">
  <table>
    <thead><tr><th>Termin</th><th>Veranstaltung</th><th>Zweck</th></tr></thead>
    <tbody>
      <tr><td class="n">Winter 26/27</td><td><strong>Ötztaler — Losanmeldung</strong></td>
        <td>Nicht Teilnahme, nur Anmeldung. Die Verlosung ist gedächtnislos, es gibt keine
        Warteliste — ab jetzt jedes Jahr anmelden. Bei Losglück 2027: fahren als reine
        Erfahrungsfahrt, 9:20–9:45, ohne jede Ambition.</td></tr>
      <tr><td class="n">Frühsommer</td><td><strong>Glocknerkönig</strong><br>Großglockner, ca. 1,5 h Anfahrt</td>
        <td>Bergzeitfahren über rund 1.200 hm als Frühjahrs-Leistungstest. Kurz genug, dass es
        nicht überfordert — der erste echte Maximaleffort am Berg mit Startnummer. Kalibriert die
        FTP draußen und liefert einen VAM-Referenzwert.</td></tr>
      <tr><td class="n">Juni</td><td><strong>Dreiländergiro</strong><br>Nauders, ca. 4 h Anfahrt</td>
        <td>Empfohlenes Hauptrennen: 165 km und 3.000 hm sind bei deinem Volumen die passende erste
        echte Marathondistanz — deutlich mehr als alles bisher, aber ohne das Abbruchrisiko eines
        Ötztaler.</td></tr>
      <tr><td class="n">Sommer</td><td><strong>Granfondo Zoncolan</strong><br>Sutrio (IT), ca. 1 h über den Plöckenpass</td>
        <td>Der nächstgelegene ernsthafte Bergmarathon — ideal als Nebenrennen ohne Reiseaufwand.
        Testet Pacing über mehrere Anstiege und die Verpflegung im Rennstress.</td></tr>
      <tr><td class="n">Ende August</td><td><strong>Eigene Gailtal-Benchmarkrunde</strong><br>Nassfeld, Plöcken, Gailberg, Kreuzberg</td>
        <td>180–220 km und 4.000–5.000 hm vor der Haustür, jedes Jahr identisch gefahren, mit vollem
        Verpflegungsplan und protokolliertem Decoupling ab Stunde vier. Der eigentliche
        Fortschrittsmesser des Projekts — hängt nicht am Losglück. 2027 in reduzierter Form,
        ab 2028 voll.</td></tr>
    </tbody>
  </table>
  </div>
  <figcaption>Termine, Distanzen und Anmeldemodalitäten sind aus den Trainingsdaten nicht
  verifizierbar — vor der Planungsfreigabe beim jeweiligen Veranstalter prüfen.</figcaption>
</section>

<section>
  <span class="num">ROADMAP</span>
  <h2>Vier Jahre, in Zahlen</h2>
  <div class="scroll">
  <table>
    <thead><tr><th>Jahr</th><th>FTP</th><th>W/kg</th><th>Gewicht</th><th>CTL-Peak</th>
      <th>Jahresstunden</th><th>Ötztaler</th><th>Schwerpunkt</th></tr></thead>
    <tbody>%s</tbody>
  </table>
  </div>
  <figcaption>Die modellierten Ötztaler-Zeiten tragen eine Unsicherheit von etwa &plusmn;15 Minuten.
  Abfahrtstempo und Gruppenanschluss am Brenner sind darin die größten Unbekannten: allein fahren
  kostet dort 15 bis 25 Minuten.</figcaption>
</section>

<section>
  <span class="num">URTEIL</span>
  <h2>Ist sub-8 realistisch?</h2>
  <div class="verdict">
    <div class="pct">25 %%</div>
    <p class="pl">Wahrscheinlichkeit sub-8 bis 2031</p>
    <p style="margin:0;max-width:62ch">Bis 2030 allein schätze ich rund 10 %%, bis 2031 etwa 20–25 %%.
    Und diese Wahrscheinlichkeit hängt fast vollständig an einer einzigen nicht-sportlichen
    Variable: dem verfügbaren Wochenbudget.</p>
  </div>
  <div class="two">
    <div>
      <h3>Mit dauerhaft 6–9 Stunden</h3>
      <p>Ist sub-8 nicht erreichbar. Dann liegt das realistische Ziel bei <strong>8:25 bis
      8:45</strong> — und das wäre für einen Fahrer, der heute bei 9:25 modelliert, ein
      ausgezeichnetes Ergebnis. Kommt der Winterabbruch auch nur zweimal wieder, ist das Thema
      rechnerisch erledigt, weil du dann jedes Jahr netto +34 statt +50 W kumulierst.</p>
    </div>
    <div>
      <h3>Mit 12–14 Stunden ab 2029</h3>
      <p>Bei gehaltenem Winter, 70–71 kg und aufgebauter Dauerkomponente wird sub-8 zu einer echten
      Chance für 2031. Sub-8 ist dann kein Comeback zu alter Form, sondern ein Neubau auf ein
      Niveau, das du nach Datenlage nie nachweisbar hattest.</p>
    </div>
  </div>
  <p class="col" style="margin-top:22px"><strong>Meine Empfehlung:</strong> primäres Ziel 2030 ist
  ein Finish unter 8:30 mit dokumentierter Ermüdungsresistenz. Sub-8 als Stretch-Ziel 2031 — mit
  einem harten Entscheidungspunkt Ende 2028.</p>
</section>

<section>
  <span class="num">NÄCHSTE 14 TAGE</span>
  <h2>Womit du anfängst</h2>
  <ol class="acts">%s</ol>
</section>

<section>
  <span class="num">GRENZEN DIESER ANALYSE</span>
  <h2>Was die Daten nicht hergeben</h2>
  <div class="col">
  <ul class="plain">
    <li><strong>Alter, Größe und Körperfettanteil fehlen vollständig.</strong> Ohne Alter ist die
    Frage, ob +80 W in vier Jahren realistisch sind, nicht seriös zu beantworten — der Unterschied
    zwischen 36 und 48 Jahren entscheidet über die halbe Roadmap. Ohne Körperfettmessung ist auch
    nicht entscheidbar, ob 70 kg ein gesundes Ziel oder bereits Substanzverlust ist: bei heute 20 %%
    Körperfett wären 70 kg entspannte 12,6 %%, bei 15 %% nur noch 7,1 %%.</li>
    <li><strong>Die Ursache des Winterausfalls ist unbekannt.</strong> Ruhepuls 58 statt 52 im
    Februar deutet eher auf Krankheit oder eine Lebensbelastung hin als auf fehlende Disziplin —
    aber das ist eine Vermutung auf dünner Basis. Der Schlafmedian von 5,4 h in jenem Monat beruht
    auf nur fünf aufgezeichneten Nächten und trägt nichts. Der ganze Winterplan steht oder fällt
    mit dieser Frage.</li>
    <li><strong>Das verfügbare Wochenbudget steht nirgends in den Daten.</strong> Der Median von
    6,5 h ist ein Ergebnis, keine Vorgabe. Ob 12–14 h ab 2029 überhaupt Platz im Leben haben, ist
    die einzige Frage, deren Antwort das Ötztaler-Urteil kippen kann.</li>
    <li><strong>Die Messkette ist dreifach gebrochen.</strong> SAXONAR 1031 bis 20.07.2026, SRAM
    1052 ab 22.07. (nach deiner Angabe innerhalb 1–2 %% übereinstimmend), und die gültige FTP von
    271 W stammt von einem dritten Gerät — dem MyWhoosh-Trainer, mit dem du draußen nie fährst.
    Ein Stufentest am Wechseldatum zeigt keinen messbaren Offset, der Formzuwachs ist also eher
    belegt als in Frage gestellt. Formal kalibriert ist trotzdem nichts.</li>
    <li><strong>Die Ermüdungsresistenz ist ungetestet.</strong> Im gesamten Datensatz gibt es
    keinen einzigen maximalen Effort nach hoher Belastung. Die guten Decoupling-Werte deiner
    Langfahrten stammen aus Fahrten unter 3,5 Stunden — komplett innerhalb des Glykogenfensters.
    Hitze über fünf Stunden ist null geprüft.</li>
    <li><strong>Die Kohlenhydratbilanz beruht auf einem Modellwert.</strong> Der von intervals.icu
    ausgewiesene Verbrauch impliziert bei dir einen Kohlenhydratanteil von rund 90 %% der Energie,
    was physiologisch zu hoch ist. Der reale Rennbedarf liegt eher bei 820–960 g als bei 1.250 g.
    Die Richtung der Empfehlung — 90 bis 110 g pro Stunde gegen heute 66 — bleibt trotzdem richtig.</li>
  </ul>
  </div>
</section>

<footer>
  Datenquelle: intervals.icu API, Athlet i378091, abgerufen am 07.09.2026 ·
  598 Aktivitäten (2013–2026), 1.436 Tage Wellness-Historie, Powerkurven über fünf Zeitfenster ·
  Ötztaler-Zeitmodell segmentweise gerechnet: Steilanstiege 62,7 km / 4.166 hm bei 6,6 %%,
  Brenner-Ziehweg 38 km / 780 hm, Abfahrten 121 km · CdA 0,32 · Crr 0,004 · Kletter-IF 0,80 ·
  Systemgewicht Fahrer + 9,5 kg
</footer>

</div>
""" % (CSS, C['oetz'], STATS_NOW, C['fit'], C['vol'], C['prog'], C['pc'], C['zon'], C['gap'],
       lev_html, ph_html, rm_rows, STATS_YEAR and "", act_html)

with io.open('rennrad_analyse.html', 'w', encoding='utf-8') as f:
    f.write(HTML)
print("written", len(HTML), "chars")
