# -*- coding: utf-8 -*-
"""Wochenplan KW38/2026 - KW13/2027 als strukturierte Daten.
Eine Quelle fuer (a) die HTML-Tabelle und (b) die intervals.icu-Events."""
import json, io, os, re
from datetime import date, timedelta

FTP = 271


def tss(minutes, IF):
    return round(minutes / 60.0 * IF * IF * 100)


def S(name, minutes, IF, desc, typ="Ride", key=False, tag=None):
    d = {"name": name, "min": minutes, "if": IF, "tss": tss(minutes, IF),
         "desc": desc, "type": typ, "key": key}
    if tag: d["tag"] = tag
    return d


def KRAFT(minutes, desc):
    return {"name": "Krafttraining", "min": minutes, "if": None,
            "tss": 14 if minutes <= 45 else 28, "desc": desc,
            "type": "WeightTraining", "key": False}


# Bausteine
def z2(mins, extra=""):
    return S("Z2 Grundlage", mins, 0.68, ("Gleichmaessig Z2, NP unter 175 W." + extra).strip())


def lang(h, m=0, carbs=80, indoor=False):
    mins = h * 60 + m
    lbl = "%d:%02d" % (h, m)
    ort = "Indoor oder outdoor, egal" if indoor else "Outdoor wenn moeglich"
    return S("Long Endurance %s" % lbl, mins, 0.70,
             "Lange Z2-Fahrt, NP unter 175 W. %s. Verpflegung %d g Kohlenhydrate/h ab Stunde 2."
             % (ort, carbs))


def pz2h(mins=118):
    return S("Pendeln Z2", mins, 0.67,
             "Arbeitsweg, 55-61 km, rund 2 h. Gleichmaessig Z2, NP unter 185 W.")


def locker(mins=60):
    return S("Recovery", mins, 0.55, "Locker Z1. Kein Wattdruck, keine Anstiege.")


def vo2(reps, dauer, pct, mins=75, watt=None):
    if watt:   # Zielwatt aus dem 5-Min-Test vom 12.09.2026 (334 W)
        return S("VO2max %dx%d min" % (reps, dauer), mins, 0.88,
                 "Einfahren 20 min. %dx%d min bei %d-%d W, Pause 1:1 locker rollend. "
                 "Ausfahren 10 min. Kadenz 95-105. Die Zielwatt stammen aus dem 5-Min-Test "
                 "vom 12.09. (334 W)." % (reps, dauer, watt[0], watt[1]), key=True)
    return S("VO2max %dx%d min" % (reps, dauer), mins, 0.88,
             "Einfahren 20 min. %dx%d min bei %s %% FTP (%d-%d W), Pause 1:1 locker rollend. "
             "Ausfahren 10 min. Zielwatt nach dem 5-Min-Test anpassen." %
             (reps, dauer, pct, int(FTP * float(pct.split("-")[0]) / 100),
              int(FTP * float(pct.split("-")[-1]) / 100)), key=True)


LANG_W = (295, 305)   # 4- bis 5-Minuten-Intervalle


def r3015(saetze, wdh, watt=(330, 340), mins=75):
    mitte = (watt[0] + watt[1]) // 2      # 325, 335, 340 oder 345 W
    datei = "vo2max_30-15_%dx%d%s" % (saetze, wdh, "_%dw" % mitte if mitte > 336 else "")
    return S("VO2max 30/15 %dx%d" % (saetze, wdh), mins, 0.88,
             "Einfahren 20 min. %d Saetze mit je %d Wiederholungen: 30 s bei %d-%d W, dann 15 s "
             "bei 165 W weitertreten. 3 min Pause zwischen den Saetzen. Ausfahren 10 min. "
             "Im ERG-Modus, Kadenz 95-105. Der Satz ist zu Ende, wenn die Kadenz unter 85 faellt "
             "und du sie nicht mehr hochbekommst. Workout-Datei: workouts/%s.zwo"
             % (saetze, wdh, watt[0], watt[1], datei), key=True)


def ss(reps, dauer, mins=None):
    mins = mins or (25 + reps * dauer + (reps - 1) * 5)
    return S("Sweetspot %dx%d min" % (reps, dauer), mins, 0.85,
             "Einfahren 20 min. %dx%d min bei 88-94 %% FTP (238-255 W), 5 min Pause. "
             "Sollte sich zaeh, aber kontrollierbar anfuehlen - RPE 5-6." % (reps, dauer), key=True)


def schwelle(reps, dauer, mins=None):
    mins = mins or (25 + reps * dauer + (reps - 1) * 5)
    return S("Schwelle %dx%d min" % (reps, dauer), mins, 0.87,
             "Einfahren 20 min. %dx%d min bei 96-100 %% FTP (260-271 W), 5 min Pause. "
             "Ausfahren 10 min." % (reps, dauer), key=True)


def berg(reps, dauer):
    mins = 30 + reps * dauer + (reps - 1) * 6
    return S("Schwelle am Berg %dx%d min" % (reps, dauer), mins, 0.87,
             "%dx%d min bei 95-100 %% FTP an einem echten Anstieg, nicht in der Ebene. "
             "Abfahrten bewusst fahren: Blickführung, Linie, Bremspunkte." % (reps, dauer), key=True)


K_AA = "Gewoehnungsphase: 2-3 Saetze x 12-15 Wdh., 50-60 % der Maximallast, volle Amplitude. " \
       "Kniebeuge, rumaenisches Kreuzheben, einbeinig, Waden, Rumpf. Gewichte mitschreiben."
K_UE = "Uebergang: 3-4 Saetze x 8-12 Wdh., 70-80 %. Last deutlich hoch."
K_MAX = "Maximalkraft: 3-4 Saetze x 4-6 Wdh., 85-90 %. Volle Pausen 3-4 min zwischen den Saetzen."
K_ERH = "Erhalt: 3 Saetze x 4-5 Wdh., 85 %. Reduzieren, nicht weglassen."

W = []  # (isoyear, week, phase, [sessions], fokus)


ROLLE = ((2026, 44), (2027, 12))   # Wochen, in denen auf der Rolle gefahren wird
WORKOUTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workouts")


def rolle_datei(s):
    """Name der Workout-Datei aus make_workouts.py zu einer Einheit, sonst None."""
    n = s["name"]
    m = re.match(r"(Sweetspot|Schwelle) (\d+)x(\d+) min$", n)
    if m:
        return "%s_%sx%s" % (m.group(1).lower(), m.group(2), m.group(3))
    m = re.match(r"VO2max (\d+)x(\d+) min$", n)
    if m:
        return "vo2max_%sx%s" % (m.group(1), m.group(2))
    m = re.match(r"Long Endurance (\d+):(\d\d)$", n)
    if m:
        return "lang_%sh%s" % (m.group(1), m.group(2))
    if n == "Z2 Grundlage":
        return "z2_%dmin" % s["min"]
    if n == "Recovery":
        return "locker_%dmin" % s["min"]
    return {"Openers": "openers", "TEST 2x20 min all-out": "test_2x20",
            "5-Minuten-Retest": "5min_maximaltest"}.get(n)


def add(y, w, ph, sess, fokus):
    if ROLLE[0] <= (y, w) <= ROLLE[1]:
        for s in sess:   # im Winter steht bei jeder Radeinheit, welche Datei auf die Rolle gehoert
            d = rolle_datei(s) if s["type"] == "Ride" and ".zwo" not in s["desc"] else None
            if d and os.path.exists(os.path.join(WORKOUTS, d + ".zwo")):
                vor = "Auf der Rolle" if d.startswith("lang_") else "Workout-Datei"
                s["desc"] += " %s: workouts/%s.zwo" % (vor, d)
    W.append((y, w, ph, sess, fokus))


# ---------- Phase 0: Saisonausklang ----------
add(2026, 37, "mess", [
    S("Openers vor dem Test", 45, 0.66,
      "Freitag, indoor. 30 min locker mit 3x1 min bei 110 % FTP (300 W), je 3 min Pause. "
      "Kurz, macht die Beine wach, ermuedet nicht - genau das Muster, das du vor dem "
      "30-Min-Test am 04.09. gefahren bist. Es hat funktioniert.", key=False, tag=5),
    S("5-MINUTEN-MAXIMALTEST", 60, 0.82,
      "Samstag, indoor auf MyWhoosh, exakt gleiches Setup wie beim 30-Min-Test am 05.09.: "
      "gleiche Tageszeit, gleicher Luefter, gleiche Verpflegung. "
      "ABLAUF: 20 min einfahren inkl. 2x1 min Steigerung, 5 min locker, dann 5 MINUTEN "
      "ALLES, danach 15 min ausfahren. "
      "PACING: Die ersten 45-60 s bewusst ueber dem Zielschnitt anfahren, damit die "
      "Sauerstoffaufnahme schnell hochkommt, dann einpendeln, letzte Minute alles. "
      "Ein zu vorsichtiger Start kostet 10-15 Watt. "
      "ERWARTUNG 300-320 W: Aus deinen 7x4 min bei 278 W vom 27.08. ist deutlich mehr "
      "ableitbar als die 288 W deiner Kurve. "
      "DANACH: Verhaeltnis 5min/FTP bilden. Unter 1,15 heisst VO2max-limitiert - dann ist "
      "der Winterblock genau richtig. Ueber 1,25 hiesse schwellenlimitiert, dann baue ich um.",
      key=True, tag=6)],
    "Der 5-Minuten-Test wandert von KW40 hierher. Zwei Gruende: Beide Tests beschreiben "
    "dann DIESELBE Form - der 30-Min-Test war am 05.09., das sind sieben Tage Abstand, "
    "und das Verhaeltnis 5min/30min wird dadurch sauber vergleichbar. Und der ganze "
    "Winterblock haengt an dieser Zahl: je frueher sie steht, desto besser - misslingt "
    "der Test, bleibt Zeit fuer einen zweiten Versuch.")

# ---------- Herbst KW38-43: Volumen nutzen, solange das Licht haelt ----------
# Abendliche Heimfahrt ist bis rund 20.-24.10. moeglich; am 25.10. faellt durch die
# Zeitumstellung eine Stunde Abendlicht weg. Danach beginnt der Indoor-Winter.
def abend(mins=118):
    return S("Pendeln Z2 (Abendheimfahrt)", mins, 0.66,
             "Abends von der Arbeit heim, 55-61 km. Reines Z2, NP unter 180 W. "
             "Diese Fahrt kostet dich keine Familienzeit - sie ersetzt die Zugfahrt. "
             "Solange das Licht haelt, ist sie die billigste Form von Umfang, die es gibt.")


add(2026, 38, "auf", [
    ss(2, 20), lang(3, 0, carbs=80), abend(), pz2h(), KRAFT(40, K_AA), KRAFT(40, K_AA)],
    "Kraftstart und normale Aufbauwoche - keine Saisonpause. Du hattest Ende August drei "
    "Ruhetage am Stueck plus den Tag nach dem Test; erholt bist du. Die Kraft ist bewusst "
    "leicht: es geht um Bewegungsmuster und Sehnen, nicht um Last. Muskelkater in den ersten "
    "zwei Wochen ist normal. Ab der ersten Einheit die Gewichte mitschreiben.")

add(2026, 39, "auf", [
    ss(3, 15), lang(3, 15, carbs=80), abend(), pz2h(), KRAFT(45, K_AA), KRAFT(45, K_AA)],
    "Die urspruengliche Entlastungswoche ist gestrichen. Stattdessen Volumen, solange das "
    "Wetter mitspielt - jede Abendheimfahrt jetzt ist eine, die im November fehlt.")

add(2026, 40, "auf", [
    ss(3, 20), lang(3, 30, carbs=80), abend(), pz2h(), KRAFT(50, K_UE), KRAFT(50, K_UE)],
    "Winterlogistik-Woche: Rollentrainer, Luefter und Abo aufbauen und einmal in einer "
    "90-Minuten-Einheit testen - nicht erst im November. Dazu ftp_est_min_secs auf 720 "
    "setzen und die VO2-Zielwatt aus dem Testergebnis vom 12.09. eintragen.")

add(2026, 41, "auf", [
    schwelle(3, 12), lang(3, 30, carbs=80), abend(), pz2h(), KRAFT(50, K_UE), KRAFT(50, K_UE)],
    "Hoechste Herbstwoche. Erste Schwelleneinheit statt Sweetspot - der Uebergang in den "
    "Winterblock beginnt. Verpflegung ab jetzt auf jeder Fahrt ueber 2 h: 80 g/h.")

add(2026, 42, "rec", [
    ss(2, 15), lang(2, 30, carbs=80), pz2h(), locker(60), KRAFT(45, K_UE)],
    "Entlastung nach vier Aufbauwochen - jetzt ist sie verdient. Rund 65 % der "
    "Belastungswoche, keine harte Einheit.")

add(2026, 43, "auf", [
    schwelle(3, 12), lang(3, 30, carbs=80), abend(), pz2h(), KRAFT(50, K_MAX), KRAFT(50, K_MAX)],
    "Letzte Woche mit Abendlicht - am 25.10. ist Zeitumstellung, danach faellt die "
    "Heimfahrt weg. Nutz sie aus. Ab KW44 laeuft der Winterblock indoor, und die Rolle "
    "muss dann stehen und getestet sein.")

# ---------- Phase 2: Grundlage, 2 Keys ----------
GR = [(44, r3015(2, 10, (320, 330)), ss(2, 20), lang(2, 30),
       "Blockstart mit zwei Qualitaetseinheiten. VO2-Dosis bewusst klein — es geht um den Reiz, "
       "nicht um den Block. Die VO2-Einheiten laufen ab jetzt als 30/15 nach Roennestad. "
       "Ab hier gilt: vier Radtage pro Woche, nie weniger."),
      (45, r3015(3, 10), ss(3, 15), lang(2, 45),
       "Ein Satz mehr bei den 30/15. Langfahrt waechst um 15 min pro Woche."),
      (46, r3015(3, 13), ss(3, 20), lang(3, 0),
       "Erste 3-Stunden-Fahrt des Winters. Kraft ist jetzt bei Maximallast — zusammen mit zwei "
       "harten Radeinheiten die dichteste Woche bisher. Wenn etwas weichen muss, ist es die "
       "lockere Stunde, nie eine Key-Session."),
      (48, r3015(3, 13), ss(3, 20), lang(3, 0),
       "Wiederaufnahme. Vergleiche die Herzfrequenz der 3-h-Fahrt mit KW46 — sie sollte tiefer liegen."),
      (49, r3015(3, 13, (335, 345)), schwelle(3, 12), lang(3, 15),
       "30/15: Umfang halten, Zielwatt um 5 W anheben. Key 2 wechselt von Sweetspot auf Schwelle."),
      (50, r3015(3, 13, (335, 345)), schwelle(3, 12), lang(3, 30),
       "Historische Bruchstelle: letztes Jahr endete hier die Saison. Diese Woche wird nicht verhandelt.")]
for w, k1, k2, lg, fok in GR:
    add(2026, w, "grund", [k1, k2, lg, locker(60), KRAFT(55, K_MAX), KRAFT(55, K_MAX)], fok)
add(2026, 47, "rec", [ss(2, 12), z2(90), z2(75), locker(60), KRAFT(45, K_MAX)],
    "Entlastungswoche: Intensitaet runter, Volumen nur moderat. Rund 65 % der Belastungswoche - "
    "tiefer waere kontraproduktiv, weil die CTL sonst staerker faellt, als der Block sie aufbaut.")
add(2026, 51, "grund", [r3015(3, 13, (335, 345)), schwelle(3, 12), lang(3, 0), locker(60),
                        KRAFT(55, K_MAX), KRAFT(55, K_MAX)],
    "Letzte volle Belastungswoche des Grundlagenblocks (14.-20.12.). Danach kommt die "
    "Weihnachtsentlastung - und in der Woche darauf der Test.")
add(2026, 52, "rec", [ss(2, 12), z2(90), z2(75), locker(60), KRAFT(45, K_MAX)],
    "Weihnachtsentlastung (21.-27.12.). Die Entlastungswoche liegt bewusst hier: Sie faellt "
    "mit den Feiertagen zusammen, statt gegen sie zu kaempfen - und sie macht dich frisch "
    "fuer den Test in der Folgewoche. Eine kurze Sweetspot-Einheit haelt die Schaerfe.")

# ---- KW53/2026: Testwoche vor dem VO2-Block (2026 hat 53 ISO-Wochen!) ----
add(2026, 53, "mess", [
    S("Openers", 50, 0.68,
      "Am Vortag des Tests. 30 min locker, dann 3x1 min bei 110 % FTP (300 W) mit je 3 min "
      "Pause, ausfahren. Macht die Beine wach, ohne zu ermueden.", key=False),
    S("TEST 2x20 min all-out", 90, 0.90,
      "Der zweite echte Test des Winters. Einfahren 20 min inkl. 2x1 min Steigerung. "
      "Dann 2x20 min ALLES, 10 min lockere Pause dazwischen. Gleichmaessig anfangen - "
      "das erste Intervall soll nicht schneller sein als das zweite. Indoor, MyWhoosh, "
      "gleiches Setup wie der 5-Min-Test. "
      "ZWECK: Der 20-Minuten-Punkt deiner Powerkurve stammt bisher als Nebenprodukt aus "
      "dem 30-Min-Test. Hier bekommst du einen echten Maximalwert und eine unabhaengige "
      "FTP-Bestaetigung - mit diesem Wert laeuft der ganze VO2-Block im Januar und Februar. "
      "AUSWERTUNG: FTP = Schnitt des besseren Intervalls x 0,95 bis 0,97. Erwartung "
      "285-300 W im Intervall, also FTP 275-290.", key=True),
    lang(2, 30), z2(75), locker(60), KRAFT(45, K_MAX)],
    "Testwoche zwischen den Jahren (28.12.-03.01.). Bewusst hier: nach der Weihnachtswoche "
    "bist du frisch (TSB projiziert +8 bis +12), aber noch nicht abgestumpft. Am Blockende "
    "waere der TSB bei -20 gewesen - dort misst man Muedigkeit, nicht Form.")

# ---------- Phase 3: VO2-Block ----------
VO = [(1, r3015(3, 13, (340, 350)), schwelle(3, 12), lang(2, 30),
       "VO2-Block. Die 30/15 bleiben das Hauptformat. Zielwatt nur anheben, wenn in der Woche "
       "davor alle Wiederholungen sauber waren."),
      (2, r3015(3, 13, (340, 350)), schwelle(3, 12), lang(2, 30),
       "Gleiche Einheit wie in KW01. Wenn der letzte Satz nicht mehr auf Zielwatt geht, war die Vorgabe zu hoch."),
      (3, r3015(3, 13, (340, 350)), vo2(5, 4, "", watt=LANG_W), lang(2, 45),
       "Beide Keys jetzt VO2 — die haerteste Woche des Blocks. Eine Einheit 30/15, eine mit "
       "langen Intervallen: die liegen naeher am 5-Min-Test und zeigen den Fortschritt direkter."),
      (5, r3015(3, 13, (340, 350)), schwelle(3, 15), lang(2, 45),
       "Nach der Entlastung wieder 30/15, die Schwelle waechst auf 3x15 min."),
      (6, r3015(3, 13, (340, 350)), vo2(5, 4, "", watt=LANG_W), lang(2, 45),
       "Februar. Letztes Jahr null Trainingstage in diesem Monat. Mindestziel: 16."),
      (7, r3015(3, 13, (340, 350)), schwelle(3, 15), lang(3, 0),
       "Hoechste Belastung des Winters. Danach kommt nichts Haerteres mehr bis April.")]
for w, k1, k2, lg, fok in VO:
    add(2027, w, "vo2", [k1, k2, lg, z2(60), locker(50), KRAFT(45, K_ERH)], fok)
add(2027, 4, "rec", [vo2(2, 4, "105"), z2(90), z2(75), locker(60), KRAFT(45, K_ERH)],
    "Entlastung. Kein harter Reiz — die Anpassung passiert genau jetzt.")
add(2027, 8, "rec",
    [S("5-Minuten-Retest", 60, 0.82,
       "Gleiches Setup, gleiche Tageszeit, Openers am Vortag. Ziel: +15-25 W gegenueber dem Test "
       "vom 12.09. (334 W).",
       key=True),
     z2(90), z2(75), locker(60), KRAFT(45, K_ERH)],
    "Entlastung plus Retest. Misst, was der VO2-Block gebracht hat.")

# ---------- Phase 4: Uebergang Strasse ----------
add(2027, 9, "str", [schwelle(2, 20), lang(3, 0, indoor=True), z2(90), locker(60), KRAFT(45, K_ERH)],
    "Intensitaet von VO2 zurueck auf Schwelle. Noch komplett indoor planbar — Maerz ist in "
    "Kaernten unzuverlaessig (2026: zwei Outdoor-Fahrten, 2025: null).")
add(2027, 10, "str", [schwelle(3, 15), lang(3, 30, indoor=True), z2(90), locker(60), KRAFT(45, K_ERH)],
    "Jede Ausfahrt, die das Wetter hergibt, wird outdoor gefahren — aber nichts haengt davon ab.")
add(2027, 11, "str", [ss(3, 20), lang(3, 30, carbs=90, indoor=True), z2(90), locker(60), KRAFT(45, K_ERH)],
    "Hoechstes Wochenvolumen des Winters. Sobald es draussen geht: Intervalle an den Berg verlegen.")
add(2027, 12, "rec", [ss(2, 15), z2(90), z2(75), locker(60), KRAFT(45, K_ERH)],
    "Entlastung vor der ersten 4-Stunden-Fahrt.")
add(2027, 13, "str",
    [S("4-Stunden-Fahrt", 240, 0.70,
       "Das Winterziel: erste Fahrt ueber 4 h und 2.600 kJ deiner Aufzeichnung. Outdoor wenn "
       "das Wetter es zulaesst, sonst geteilt indoor/outdoor. Volles Verpflegungsprotokoll "
       "90 g Kohlenhydrate/h. Ab Stunde 3 auf Decoupling achten.", key=True),
     berg(2, 20), z2(90), locker(60)],
    "Wenn das Wetter mitspielt: zusaetzlich der 20-Min-Test draussen am Berg mit dem SRAM, um "
    "die Trainer-FTP gegenzupruefen. Wenn nicht, wandert der Test in die erste brauchbare "
    "Aprilwoche — er ist nicht an den Maerz gebunden.")

W.sort(key=lambda x: (x[0], x[1]))
json.dump(W, io.open('plan_data.json', 'w', encoding='utf-8'), ensure_ascii=False)

th = sum(s['min'] for _, _, _, ss_, _ in W for s in ss_ if s['type'] == 'Ride') / 60
tk = sum(s['min'] for _, _, _, ss_, _ in W for s in ss_ if s['type'] == 'WeightTraining') / 60
tt = sum(s['tss'] for _, _, _, ss_, _ in W for s in ss_)
print("Wochen: %d | Einheiten: %d" % (len(W), sum(len(x[3]) for x in W)))
print("Rad %.0f h | Kraft %.0f h | TSS %d" % (th, tk, tt))
print("Schnitt/Woche: Rad %.1f h, TSS %d -> CTL_eq %d" % (th/len(W), tt/len(W), tt/len(W)/7))
print("\nBeispielwoche KW46:")
for y, w, ph, sess, fok in W:
    if (y, w) == (2026, 46):
        for s in sess:
            print("   %-26s %3d min  TSS %3d  %s" % (s['name'], s['min'], s['tss'], s['type']))
        print("   SUMME: %d min Rad, TSS %d" %
              (sum(s['min'] for s in sess if s['type'] == 'Ride'), sum(s['tss'] for s in sess)))

# =====================================================================
# FRUEHJAHRSBLOCK KW14-KW23/2027 - Ziel: Dolomitenradrundfahrt 13.06.2027
# Grundbaustein ist die reale Pendeleinheit: 55-61 km, rund 2:00 h, IF 0,67.
# Alle Wochentagseinheiten sind so gebaut - die Intervalle liegen IN der Fahrt.
# =====================================================================
K_SAI = ("Saisonkraft: 1x/Woche, 3 Saetze x 5 Wdh. bei 85 %. Erhaelt die Winterarbeit, "
         "kostet kaum Erholung. Ab KW21 ganz weglassen.")


def pz2(mins=118):
    return S("Pendeln Z2", mins, 0.67,
             "Arbeitsweg, 55-61 km. Gleichmaessig Z2, NP unter 185 W. Nicht schneller werden, "
             "nur weil es bergab geht - das ist die Einheit, die den Umfang traegt.")


def pkey(was, IF, detail, mins=118):
    return S("Pendeln + %s" % was, mins, IF,
             "Arbeitsweg mit der Qualitaetsarbeit darin. %s Rest der Fahrt Z2. "
             "Vorteil gegenueber der Rolle: Die Intervalle liegen mitten in einer "
             "Zweistundenfahrt statt am Anfang - das ist naeher am Rennen." % detail,
             key=True)


def doppel(detail):
    return S("Doppelpendeln Z2", 236, 0.66,
             "Beide Richtungen an einem Tag, rund 115-120 km. %s "
             "Das ist der billigste Weg zu Volumen: Du ersetzt die Zugfahrt, "
             "nicht die Familienzeit." % detail)


def lang_mit(h, m, blocks, carbs=90):
    mins = h * 60 + m
    return S("Long Endurance %d:%02d + %s" % (h, m, blocks), mins, 0.74,
             "Lange Fahrt mit Belastung IM ermuedeten Zustand - der Kern der "
             "Rennvorbereitung. Erste Stunden ruhig Z2, dann %s ab Stunde 3. "
             "Verpflegung %d g Kohlenhydrate/h ab Stunde 1, nicht erst wenn der "
             "Hunger kommt." % (blocks, carbs), key=True)


add(2027, 14, "auf", [
    pkey("Schwelle 3x15 min", 0.79, "3x15 min bei 96-100 % FTP auf der Strecke, 5 min Pause."),
    pkey("VO2 4x4 min", 0.78, "4x4 min bei 105-110 % an den Anstiegen unterwegs."),
    lang(4, 0, carbs=90), pz2(), KRAFT(45, K_SAI)],
    "Saisonstart, das Pendeln laeuft wieder. Intensitaet von VO2 auf Schwelle. Beide "
    "Qualitaetseinheiten liegen im Arbeitsweg - sie kosten keine zusaetzliche Zeit.")

add(2027, 15, "auf", [
    pkey("Schwelle am Berg 3x15", 0.80, "Umweg ueber einen Anstieg, dort 3x15 min bei 96-100 %."),
    pkey("Sweetspot 3x20 min", 0.79, "3x20 min bei 88-94 % auf der Strecke."),
    lang_mit(4, 0, "2x20 min Sweetspot"), pz2(), KRAFT(45, K_SAI)],
    "Erste Langfahrt mit Belastung im ermuedeten Zustand.")

add(2027, 16, "auf", [
    pkey("Schwelle am Berg 2x25", 0.80, "2x25 min bei 95-100 % am laengsten Anstieg der Strecke."),
    pkey("VO2 5x4 min", 0.79, "5x4 min bei 105-110 % an den Anstiegen."),
    lang_mit(4, 30, "3x15 min Schwelle"), doppel("Beide Richtungen locker."),
    KRAFT(45, K_SAI)],
    "Erster Doppelpendeltag: 4 h an einem Werktag. Das ist neu und der eigentliche "
    "Schritt Richtung 15 Wochenstunden.")

add(2027, 17, "rec", [
    pkey("Sweetspot 2x15", 0.74, "Nur 2x15 min bei 88-92 %, sonst locker."),
    lang(2, 30, carbs=80), pz2(), locker(60), KRAFT(45, K_SAI)],
    "Entlastung bei rund 65 % der Belastungswoche - nicht tiefer, sonst faellt die CTL "
    "staerker, als der naechste Block sie aufbaut.")

add(2027, 18, "spez", [
    pkey("Renntempo 3x20", 0.80, "3x20 min bei 88-93 % - das ist Renntempo, nicht Schwelle."),
    pkey("Schwelle 3x12 min", 0.79, "3x12 min bei 96-100 % an den Anstiegen."),
    lang_mit(4, 30, "2x25 min Renntempo"), pz2(), KRAFT(45, K_SAI)],
    "Spezifischer Block. Renntempo heisst 88-93 % - genau das faehrst du am Gailberg "
    "im Rennen.")

add(2027, 19, "spez", [
    S("KURSBESICHTIGUNG Gailberg + Lesachtal", 240, 0.75,
      "Fahr die Rennstrecke ab, so weit es an einem Tag geht: Drautal, Gailbergsattel, "
      "Lesachtal Richtung Kartitscher Sattel. Nicht schnell - schauen. Wo sind die "
      "Steilstuecke, wo kann man rollen, welche Uebersetzung braucht es, wo stehen die "
      "Labestationen. Am Gailberg einmal 20 min auf Renntempo, sonst Z2.",
      key=True, tag=6),
    pkey("VO2 4x4 min", 0.79, "4x4 min bei 105-110 % an den Anstiegen."),
    pkey("Schwelle 2x20 min", 0.79, "2x20 min bei 96-100 %."),
    doppel("Beide Richtungen locker."), KRAFT(45, K_SAI)],
    "Kursbesichtigung vier Wochen vorher. Du kennst das Rennen - aber nicht mit diesen "
    "Beinen und nicht mit diesem Rad.")

add(2027, 20, "spez", [
    pkey("Renntempo 2x30", 0.81, "2x30 min bei 88-93 % am laengsten Anstieg."),
    pkey("Schwelle 3x15 min", 0.79, "3x15 min bei 96-100 %."),
    lang_mit(5, 0, "3x20 min Renntempo"), doppel("Beide Richtungen locker."),
    KRAFT(45, K_SAI)],
    "Groesste Woche des Jahres und die erste Fuenf-Stunden-Fahrt deines Lebens. "
    "Danach geht der Umfang nur noch runter.")

add(2027, 21, "rec", [
    pkey("Sweetspot 2x15", 0.74, "Nur 2x15 min, sonst locker."),
    lang(2, 30, carbs=90), pz2(), locker(60)],
    "Entlastung bei rund 65 %. Kraft ab jetzt weglassen - die letzten drei Wochen "
    "gehoeren dem Rennen.")

add(2027, 22, "spez", [
    S("GAILBERG-BENCHMARK", 118, 0.80,
      "Auf dem Arbeitsweg ueber den Gailberg: das Segment Gailberg climb full "
      "(6,72 km / 357 hm) einmal all-out. Deine Referenz: 23:41 aus 2026, 16:09 aus 2015. "
      "Gut einfahren, dann alles, danach locker heimrollen. Das ist deine ehrlichste "
      "Standortbestimmung vor dem Rennen - und die Pacing-Zahl fuer den Renntag. "
      "Ziel 2027: unter 21:00.", key=True, tag=2),
    pkey("Schwelle 2x20 min", 0.78, "2x20 min bei 96-100 %."),
    lang(3, 30, carbs=90), pz2(), locker(60)],
    "Letzte richtige Belastungswoche - bewusst NICHT zu leicht. Wer zehn Tage vor dem "
    "Rennen schon tapert, steht frisch am Start, aber ohne Form.")

add(2027, 23, "taper", [
    S("Openers", 60, 0.70,
      "3x3 min bei Renntempo (88-93 % FTP), sonst locker. Kurze Runde, nicht die volle "
      "Pendelstrecke.", key=False, tag=2),
    S("Kurz und scharf", 60, 0.72,
      "45 min locker mit 5x2 min bei Renntempo. Haelt die Spritzigkeit, ohne zu ermueden. "
      "In der Rennwoche ist Nichtstun der haeufigste Fehler.", key=False, tag=3),
    S("Renn-Openers", 45, 0.68,
      "Freitag: 30 min locker mit 3x1 min bei 110 %. Danach Rad putzen, Kette schmieren, "
      "Startnummer holen.", key=False, tag=5),
    S("DOLOMITENRADRUNDFAHRT", 275, 0.82,
      "112 km / 1.870 hm, Start 09:15 Lienz. RENNPLAN: Die ersten 15 km im Drautal ruhig "
      "und im Windschatten - dort gewinnt man nichts und verliert alles. Gailbergsattel im "
      "eigenen Tempo bei 88-92 % FTP, nicht dem Feld nachfahren. Im Lesachtal in eine "
      "Gruppe einordnen. Kartitscher Sattel ist die Entscheidung: wenn noch etwas da ist, "
      "dann hier. VERPFLEGUNG: 90 g Kohlenhydrate/h ab der ersten Stunde, zwei Flaschen bis "
      "zur ersten Labe. ZIELZEIT 4:30-4:45 - aber die Zeit ist nicht der Zweck. Der Zweck "
      "ist, nach zwoelf Jahren wieder ein Rennen zu fahren und am Ende zu wissen, wie das "
      "geht.", key=True, tag=7)],
    "Renntaper. Volumen auf 40 %, Intensitaet kurz erhalten. Was jetzt fehlt, holst du "
    "nicht mehr auf - kaputtmachen kannst du es aber noch.")

# --- Neuausgabe nach dem Fruehjahrsblock ---
W.sort(key=lambda x: (x[0], x[1]))
json.dump(W, io.open('plan_data.json', 'w', encoding='utf-8'), ensure_ascii=False)
_th = sum(s['min'] for _, _, _, ss_, _ in W for s in ss_ if s['type'] == 'Ride') / 60
_tk = sum(s['min'] for _, _, _, ss_, _ in W for s in ss_ if s['type'] == 'WeightTraining') / 60
_tt = sum(s['tss'] for _, _, _, ss_, _ in W for s in ss_)
print("GESAMT: %d Wochen, %d Einheiten, Rad %.0f h, Kraft %.0f h, TSS %d"
      % (len(W), sum(len(x[3]) for x in W), _th, _tk, _tt))
