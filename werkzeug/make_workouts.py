# -*- coding: utf-8 -*-
"""Erzeugt die Workout-Dateien für die Rolle (ZWO, für MyWhoosh) in ../workouts
und dazu die Übersicht ../workouts/README.md.

Nur Standardbibliothek. Jede Einheit des Winterplans, die auf der Rolle gefahren wird,
bekommt eine Datei. Die Vorgaben stehen als Anteil der FTP in der Datei; Einheiten mit
festen Wattzahlen (30/15, 5x4, Öffner) werden hier über FTP umgerechnet. Ändert sich die
FTP in MyWhoosh, deshalb oben FTP anpassen und neu erzeugen.

    python make_workouts.py
"""
import io
import os
from xml.sax.saxutils import escape, quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'workouts')

FTP = 271           # muss zur FTP passen, die in MyWhoosh eingestellt ist
SWEETSPOT = 0.91    # Plan: 88-94 %
SCHWELLE = 0.97     # Plan: 96-100 %
LOCKER = 0.50       # Pausen zwischen den Intervallen
OFF_3015 = 165      # Watt in den 15 Sekunden der 30/15
TEST_ANNAHME = 1.07  # nur für die Lastschätzung des 2x20-Tests (rund 290 W)


def w(anteil):
    return int(round(anteil * FTP))


def anteil(watt):
    return watt / float(FTP)


# ---------- Bausteine ----------
def rampe(art, dauer, von, bis, hinweise=()):
    """art: 'Warmup' oder 'Cooldown'."""
    return {'t': 'rampe', 'art': art, 'dauer': dauer, 'von': von, 'bis': bis, 'hinweise': list(hinweise)}


def halten(dauer, p, hinweise=()):
    return {'t': 'halten', 'dauer': dauer, 'p': p, 'hinweise': list(hinweise)}


def wechsel(n, an, aus, p_an, p_aus):
    return {'t': 'wechsel', 'n': n, 'an': an, 'aus': aus, 'p_an': p_an, 'p_aus': p_aus}


def frei(dauer, hinweise=()):
    """Free Ride: MyWhoosh schaltet ERG aus und zeigt keine Vorgabe."""
    return {'t': 'frei', 'dauer': dauer, 'hinweise': list(hinweise)}


def einfahren(ansage, zusatz='Ab jetzt regelmäßig aus der Flasche trinken.', letzte='15 Sekunden.'):
    """20 Minuten: Rampe, 4 min ruhig, 3 Öffner, 90 s Sammlung."""
    return [
        rampe('Warmup', 600, 0.45, 0.70, [(10, 'Einfahren. 10 Minuten locker steigern.'),
                                          (300, 'Hälfte. Trittfrequenz 90–95.')]),
        halten(240, 0.70, [(10, 'Gleichmäßig bei %d W.' % w(0.70)), (120, zusatz)]),
        wechsel(3, 30, 60, 1.10, LOCKER),
        halten(90, LOCKER, [(5, ansage), (75, letzte)]),
    ]


# ---------- Einheiten ----------
def intervalle(datei, name, plan, tag, n, minuten, p, pause=300, kadenz='85–95', aus=300, text=''):
    ziel, dauer = w(p), minuten * 60
    schritte = einfahren('Gleich Intervall 1/%d: %d min bei %d W.' % (n, minuten, ziel))
    for i in range(1, n + 1):
        h = [(5, 'Intervall %d/%d: %d min bei %d W. Trittfrequenz %s.' % (i, n, minuten, ziel, kadenz)),
             (dauer // 2, 'Hälfte.')]
        if dauer >= 900:
            h.append((dauer - 300, 'Noch 5 Minuten.'))
        h.append((dauer - 60, 'Noch 1 Minute.'))
        schritte.append(halten(dauer, p, h))
        if i < n:
            schritte.append(halten(pause, LOCKER, [
                (5, '%d Minuten locker. Trinken.' % (pause // 60)),
                (pause - 60, 'Noch 1 Minute, dann Intervall %d/%d.' % (i + 1, n))]))
    schritte.append(rampe('Cooldown', aus, 0.55, 0.40, [(5, 'Geschafft. Locker ausfahren.')]))
    return {'datei': datei, 'name': name, 'plan': plan, 'tags': [tag], 'schritte': schritte,
            'ziel': '%d × %d min bei %d W' % (n, minuten, ziel), 'text': text}


def sweetspot(n, minuten):
    return intervalle(
        'sweetspot_%dx%d' % (n, minuten), 'Sweetspot %dx%d' % (n, minuten),
        'Sweetspot %dx%d min' % (n, minuten), 'Sweetspot', n, minuten, SWEETSPOT,
        text=('Sweetspot: %d × %d Minuten bei %d W (%d %% der FTP), dazwischen 5 Minuten locker.\n'
              'Im ERG-Modus, Trittfrequenz 85–95. Soll sich zäh, aber kontrollierbar anfühlen (RPE 5–6).\n'
              'Flasche mit 40–60 g Kohlenhydraten, ab dem Einfahren trinken.'
              % (n, minuten, w(SWEETSPOT), round(SWEETSPOT * 100))))


def schwelle(n, minuten):
    return intervalle(
        'schwelle_%dx%d' % (n, minuten), 'Schwelle %dx%d' % (n, minuten),
        'Schwelle %dx%d min' % (n, minuten), 'Schwelle', n, minuten, SCHWELLE,
        text=('Schwelle: %d × %d Minuten bei %d W (%d %% der FTP), dazwischen 5 Minuten locker.\n'
              'Im ERG-Modus, Trittfrequenz 85–95. Hart, aber gleichmäßig durchzufahren (RPE 7).\n'
              'Wird ein Intervall im ERG-Modus zu schwer, die Trittfrequenz hoch halten; fällt sie\n'
              'unter 80 und kommt nicht mehr hoch, das Intervall beenden und locker weiterfahren.\n'
              'Flasche mit 40–60 g Kohlenhydraten, ab dem Einfahren trinken.'
              % (n, minuten, w(SCHWELLE), round(SCHWELLE * 100))))


def vo2_lang(n, minuten, p, plan):
    ziel = w(p)
    return intervalle(
        'vo2max_%dx%d' % (n, minuten), 'VO2max %dx%d' % (n, minuten), plan, 'VO2max',
        n, minuten, p, pause=minuten * 60, kadenz='95–105', aus=600,
        text=('VO2max mit langen Intervallen: %d × %d Minuten bei %d W, Pause gleich lang und locker.\n'
              'Im ERG-Modus, Trittfrequenz 95–105. Die erste Hälfte fühlt sich machbar an, die\n'
              'zweite zählt. Fällt die Kadenz unter 85 und kommt nicht mehr hoch, ist Schluss.\n'
              'Flasche mit 40–60 g Kohlenhydraten.' % (n, minuten, ziel)))


def r3015(saetze, wdh, watt, plan, zusatz=''):
    datei = 'vo2max_30-15_%dx%d%s' % (saetze, wdh, zusatz)
    schritte = einfahren('Gleich Satz 1: %d × 30/15 bei %d W. Trittfrequenz 95–105.' % (wdh, watt),
                         zusatz='Abbruch: Kadenz unter 85 und nicht mehr hochzubringen.',
                         letzte='15 Sekunden. In den Pausen weitertreten.')
    for k in range(1, saetze + 1):
        schritte.append(wechsel(wdh, 30, 15, anteil(watt), anteil(OFF_3015)))
        if k < saetze:
            schritte.append(halten(180, 0.45, [
                (5, 'Satz %d geschafft. 3 Minuten locker.' % k),
                (120, 'Noch 1 Minute. Trinken.'),
                (165, 'Gleich Satz %d: %d × 30/15 bei %d W.' % (k + 1, wdh, watt))]))
    schritte.append(rampe('Cooldown', 600, 0.60, 0.40, [(5, 'Geschafft. 10 Minuten locker ausfahren.')]))
    return {'datei': datei, 'name': 'VO2max 30/15 %dx%d, %d W' % (saetze, wdh, watt), 'plan': plan,
            'tags': ['VO2max', '30-15'], 'schritte': schritte,
            'ziel': '%d × %d × 30/15 bei %d W' % (saetze, wdh, watt),
            'text': ('30/15-Intervalle nach Rønnestad: %d Sätze mit je %d Wiederholungen.\n'
                     '30 Sekunden bei %d W, dann 15 Sekunden bei %d W weitertreten, nicht ausrollen.\n'
                     '3 Minuten Pause zwischen den Sätzen.\n\n'
                     'Im ERG-Modus fahren, Trittfrequenz 95–105. Die Rolle braucht rund 3 Sekunden\n'
                     'bis zur Vorgabe. Der Satz ist zu Ende, wenn die Kadenz unter 85 fällt und du sie\n'
                     'nicht mehr hochbekommst. Steigern erst, wenn alle Wiederholungen sauber waren.\n'
                     'Flasche mit 40–60 g Kohlenhydraten.\n\n'
                     'Die Vorgabe richtet sich nach der 5-Minuten-Bestleistung (334 W am 12.09.2026),\n'
                     'nicht nach der FTP.' % (saetze, wdh, watt, OFF_3015))}


def grundlage(minuten):
    schritte = [rampe('Warmup', 600, 0.45, 0.62, [(10, 'Einfahren, dann Z2 gleichmäßig. Trittfrequenz 85–95.')])]
    rest, k = minuten * 60 - 600 - 300, 0
    while rest > 0:
        d = min(600, rest)
        h = [(5, 'Trinken.')] if k % 2 == 1 else []
        schritte.append(halten(d, 0.65 if k % 2 else 0.62, h))
        rest -= d
        k += 1
    schritte.append(rampe('Cooldown', 300, 0.60, 0.45, [(5, 'Ausfahren.')]))
    return {'datei': 'z2_%dmin' % minuten, 'name': 'Z2 Grundlage %d min' % minuten,
            'plan': 'Z2 Grundlage (%d min)' % minuten, 'tags': ['Z2'], 'schritte': schritte,
            'ziel': '%d–%d W im Wechsel' % (w(0.62), w(0.65)),
            'text': ('Grundlage in Z2: 10-Minuten-Blöcke bei %d und %d W im Wechsel, damit es nicht\n'
                     'eintönig wird. Im ERG-Modus, Trittfrequenz 85–95. Der Schnitt bleibt unter 175 W.'
                     % (w(0.62), w(0.65)))}


def locker(minuten):
    schritte = [rampe('Warmup', 300, 0.40, 0.52, [(10, 'Locker. Kein Druck auf dem Pedal.')])]
    rest, k = minuten * 60 - 300 - 300, 0
    while rest > 0:
        d = min(600, rest)
        schritte.append(halten(d, 0.52, [(300, '1 Minute mit 100 Umdrehungen, dann wieder normal.')] if d > 360 else []))
        rest -= d
        k += 1
    schritte.append(rampe('Cooldown', 300, 0.50, 0.40, [(5, 'Ausrollen.')]))
    return {'datei': 'locker_%dmin' % minuten, 'name': 'Locker %d min' % minuten,
            'plan': 'Recovery (%d min)' % minuten, 'tags': ['Recovery'], 'schritte': schritte,
            'ziel': '%d W' % w(0.52),
            'text': ('Lockere Einheit in Z1 bei %d W. Im ERG-Modus, einfach treten.\n'
                     'Alle 10 Minuten eine Minute mit hoher Trittfrequenz.' % w(0.52))}


def lang(stunden, minuten):
    gesamt = (stunden * 60 + minuten) * 60
    schritte = [rampe('Warmup', 600, 0.45, 0.63, [(10, 'Einfahren, dann lange Z2. Flasche und Flask bereit?')])]
    rest = gesamt - 600 - 600
    while rest > 0:
        if rest >= 1200:
            schritte.append(halten(900, 0.63, [(300, 'Portion: 30 g Kohlenhydrate.')]))
            schritte.append(halten(300, 0.66, [(5, '30 Sekunden aus dem Sattel, dann 5 Minuten etwas mehr.')]))
            rest -= 1200
        else:
            schritte.append(halten(rest, 0.63, [(300, 'Portion: 30 g Kohlenhydrate.')] if rest > 360 else []))
            rest = 0
    schritte.append(rampe('Cooldown', 600, 0.60, 0.42, [(5, 'Geschafft. 10 Minuten ausfahren.')]))
    lbl = '%d:%02d' % (stunden, minuten)
    return {'datei': 'lang_%dh%02d' % (stunden, minuten), 'name': 'Lang Z2 %s' % lbl,
            'plan': 'Long Endurance %s' % lbl, 'tags': ['Z2', 'Lang'], 'schritte': schritte,
            'ziel': '%d W, alle 20 min 5 min bei %d W' % (w(0.63), w(0.66)),
            'text': ('Lange Fahrt in Z2 für Tage, an denen es draußen nicht geht: %d W, alle 20 Minuten\n'
                     'fünf Minuten bei %d W. Im ERG-Modus. Der Schnitt bleibt unter 175 W.\n'
                     'Verpflegung 90 g Kohlenhydrate pro Stunde: erste Portion nach 15 Minuten, dann alle\n'
                     '20 Minuten 30 g. Die Hinweise im Workout erinnern daran. Lüfter an, Handtuch bereit.'
                     % (w(0.63), w(0.66)))}


def oeffner():
    schritte = [
        rampe('Warmup', 600, 0.45, 0.60, [(10, 'Einfahren. Morgen ist der Test.')]),
        halten(1200, 0.60, [(10, '20 Minuten locker bei %d W.' % w(0.60)),
                            (1140, 'In 1 Minute: 3 × 1 min bei %d W, je 3 min Pause.' % w(1.10))]),
        wechsel(3, 60, 180, 1.10, LOCKER),
        rampe('Cooldown', 480, 0.55, 0.40, [(5, 'Das war es. Locker ausfahren, früh ins Bett.')]),
    ]
    # Dateiname ohne „oe“: export_md.py würde daraus im Plantext ein ö machen
    return {'datei': 'openers', 'name': 'Öffner vor dem Test', 'plan': 'Openers', 'tags': ['Test'],
            'schritte': schritte, 'ziel': '3 × 1 min bei %d W' % w(1.10),
            'text': ('Am Vortag eines Tests: 30 Minuten locker, dann 3 × 1 Minute bei %d W mit je 3 Minuten\n'
                     'Pause. Macht die Beine wach, ohne zu ermüden. Im ERG-Modus.' % w(1.10))}


def test_2x20():
    def versuch(nr, start):
        return frei(1200, [
            (1, 'TEST %d von 2. %s' % (nr, start)),
            (300, '5 Minuten. Ruhig bleiben, gleichmäßig.'),
            (600, 'Halbzeit. Halten oder leicht steigern.'),
            (900, 'Noch 5 Minuten.'),
            (1080, 'Noch 2 Minuten. Alles, was da ist.'),
            (1170, '30 Sekunden!')])
    schritte = [
        rampe('Warmup', 600, 0.45, 0.65, [(10, 'Einfahren. 10 Minuten locker steigern.')]),
        halten(180, 0.65, [(10, 'Gleichmäßig bei %d W.' % w(0.65))]),
        wechsel(2, 60, 90, 1.05, LOCKER),
        halten(120, LOCKER, [(5, 'Gleich Test 1. Der Abschnitt ist Free Ride: ERG geht von selbst aus.'),
                             (60, 'Gang wählen, in dem 285 W bei 90 Umdrehungen gehen.'),
                             (105, '15 Sekunden.')]),
        versuch(1, 'Start bei 280–285 W, nicht schneller.'),
        halten(600, 0.45, [(5, '10 Minuten locker. Trinken. Den Schnitt merken.'),
                           (480, 'Noch 2 Minuten, dann Test 2 als Free Ride.'),
                           (585, '15 Sekunden.')]),
        versuch(2, 'Starte wie beim ersten oder 3–5 W darunter.'),
        halten(600, LOCKER, [(5, 'Geschafft. Beide Schnittwerte notieren.')]),
        rampe('Cooldown', 600, 0.50, 0.35),
    ]
    return {'datei': 'test_2x20', 'name': 'Test 2x20 all-out', 'plan': 'TEST 2x20 min all-out',
            'tags': ['Test'], 'schritte': schritte, 'ziel': '2 × 20 min maximal, Free Ride',
            'text': ('Zwei Maximalversuche über 20 Minuten mit 10 Minuten lockerer Pause.\n'
                     'Die beiden Testabschnitte sind Free Ride: MyWhoosh schaltet ERG dort selbst aus und\n'
                     'zeigt keine Vorgabe. Vorher „Gradient Feel“ auf 0 % stellen, dann bleibt der\n'
                     'Widerstand gleichmäßig.\n\n'
                     'Gleichmäßig anfangen: Das erste Intervall soll nicht schneller sein als das zweite.\n'
                     'Erwartung 285–300 W im Intervall. FTP = Schnitt des besseren Intervalls × 0,95 bis 0,97.\n'
                     'Gleiches Setup wie beim 5-Minuten-Test: Tageszeit, Lüfter, Verpflegung.')}


def alle():
    return [
        r3015(2, 10, 325, 'VO2max 30/15 2x10 (KW44)'),
        r3015(3, 10, 336, 'VO2max 30/15 3x10 (KW45)'),
        r3015(3, 13, 336, 'VO2max 30/15 3x13 (KW46, 48)'),
        r3015(3, 13, 340, 'VO2max 30/15 3x13 (KW49–51)', '_340w'),
        r3015(3, 13, 345, 'VO2max 30/15 3x13 (KW01–07)', '_345w'),
        vo2_lang(5, 4, anteil(300), 'VO2max 5x4 min (KW03, 06)'),
        vo2_lang(2, 4, 1.05, 'VO2max 2x4 min (KW04)'),
        sweetspot(2, 12), sweetspot(2, 15), sweetspot(2, 20), sweetspot(3, 15), sweetspot(3, 20),
        schwelle(3, 12), schwelle(3, 15), schwelle(2, 20),
        grundlage(60), grundlage(75), grundlage(90),
        locker(50), locker(60),
        lang(2, 30), lang(2, 45), lang(3, 0), lang(3, 15), lang(3, 30),
        oeffner(), test_2x20(),
    ]


# ---------- Ausgabe ----------
ERSATZ = (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('Ä', 'Ae'), ('Ö', 'Oe'), ('Ü', 'Ue'), ('ß', 'ss'),
          ('ø', 'oe'), ('–', '-'), ('—', '-'), ('×', 'x'), ('„', '"'), ('“', '"'), ('”', '"'), ('’', "'"))


def ascii_de(text):
    """MyWhoosh bekommt reines ASCII, wie die von Hand geschriebenen Dateien."""
    for a, b in ERSATZ:
        text = text.replace(a, b)
    assert all(ord(c) < 128 for c in text), text
    return text


def zahl(x):
    s = '%.3f' % x
    return s[:-1] if s.endswith('0') else s


def dauer_text(s):
    return '%d min' % (s // 60) if s % 60 == 0 else ('%d s' % s if s < 60 else '%d:%02d min' % (s // 60, s % 60))


def hinweise_xml(schritt):
    out = []
    for versatz, text in schritt['hinweise']:
        assert 0 <= versatz < schritt['dauer'], (schritt, versatz)
        out.append('            <textevent timeoffset="%d" message=%s/>' % (versatz, quoteattr(ascii_de(text))))
    return out


def schritt_xml(s):
    t = s['t']
    if t == 'rampe':
        kopf = '<%s Duration="%d" PowerLow="%s" PowerHigh="%s" pace="0"' % (s['art'], s['dauer'], zahl(s['von']), zahl(s['bis']))
        hinweis = '%s: %s Rampe %d auf %d W' % ('Einfahren' if s['art'] == 'Warmup' else 'Ausfahren',
                                               dauer_text(s['dauer']), w(s['von']), w(s['bis']))
        ende = '</%s>' % s['art']
    elif t == 'halten':
        kopf = '<SteadyState Duration="%d" Power="%s" pace="0"' % (s['dauer'], zahl(s['p']))
        hinweis = '%s bei %d W' % (dauer_text(s['dauer']), w(s['p']))
        ende = '</SteadyState>'
    elif t == 'wechsel':
        return ['        <!-- %d x %s bei %d W / %s bei %d W -->' % (s['n'], dauer_text(s['an']), w(s['p_an']), dauer_text(s['aus']), w(s['p_aus'])),
                '        <IntervalsT Repeat="%d" OnDuration="%d" OffDuration="%d"' % (s['n'], s['an'], s['aus']),
                '                    OnPower="%s" OffPower="%s" pace="0"/>' % (zahl(s['p_an']), zahl(s['p_aus'])), '']
    else:
        kopf = '<FreeRide Duration="%d" FlatRoad="1"' % s['dauer']
        hinweis = '%s Free Ride, ERG aus' % dauer_text(s['dauer'])
        ende = '</FreeRide>'
    zeilen = ['        <!-- %s -->' % hinweis]
    h = hinweise_xml(s)
    if h:
        zeilen += ['        %s>' % kopf] + h + ['        %s' % ende]
    else:
        zeilen.append('        %s/>' % kopf)
    return zeilen + ['']


def sekunden(wk):
    """Vorgabe je Sekunde als Anteil der FTP, für Dauer und Lastschätzung."""
    out = []
    for s in wk['schritte']:
        if s['t'] == 'rampe':
            n = s['dauer']
            out += [s['von'] + (s['bis'] - s['von']) * i / float(max(1, n - 1)) for i in range(n)]
        elif s['t'] == 'halten':
            out += [s['p']] * s['dauer']
        elif s['t'] == 'wechsel':
            out += ([s['p_an']] * s['an'] + [s['p_aus']] * s['aus']) * s['n']
        else:
            out += [TEST_ANNAHME] * s['dauer']
    return out


def kennzahlen(wk):
    p = sekunden(wk)
    summe, lauf = [0.0], 0.0
    for v in p:
        lauf += v
        summe.append(lauf)
    glatt = [(summe[i] - summe[i - 30]) / 30.0 for i in range(30, len(summe))]
    np_ = (sum(x ** 4 for x in glatt) / len(glatt)) ** 0.25
    return {'min': len(p) / 60.0, 'schnitt': w(sum(p) / len(p)), 'np': w(np_), 'if': np_,
            'tss': len(p) / 3600.0 * np_ * np_ * 100}


def zwo(wk):
    k = kennzahlen(wk)
    text = wk['text'] + ('\n\nGesamtdauer %s. Die Wattwerte gelten für eine FTP von %d W in MyWhoosh.'
                         % (dauer_text(int(round(k['min'] * 60))), FTP))
    zeilen = ['<workout_file>', '    <author>Trainingsplan</author>',
              '    <name>%s</name>' % escape(ascii_de(wk['name'])),
              '    <description>%s</description>' % escape(ascii_de(text)),
              '    <sportType>bike</sportType>', '    <tags>']
    zeilen += ['        <tag name=%s/>' % quoteattr(ascii_de(t)) for t in wk['tags']]
    zeilen += ['    </tags>', '    <workout>', '']
    for s in wk['schritte']:
        zeilen += schritt_xml(s)
    zeilen += ['    </workout>', '</workout_file>', '']
    return '\n'.join(zeilen)


LIESMICH = """# Workouts für die Rolle

Strukturierte Einheiten für MyWhoosh im ZWO-Format. Die Dateien mit Sternchen sind von Hand
geschrieben, alle anderen erzeugt `werkzeug/make_workouts.py` — dort ändern, nicht hier.

## Welche Datei zu welcher Einheit

| Einheit im Plan | Datei | Dauer | Vorgabe | TSS |
|---|---|---|---|---|
%s
| 5-Minuten-Retest (KW08) | `5min_maximaltest.zwo` * | 53 min | 5 min maximal, Free Ride | – |
| Test der Rolle am 09.10.2026 | `rolle_erg-test_30-15.zwo` * | 50 min | 2 × 6 × 30/15 bei 250 W | 33 |

Die Langfahrten stehen im Plan mit „draußen, wenn möglich“; die Dateien `lang_*` sind für
Tage, an denen es nicht geht.

## In MyWhoosh laden

1. <https://workout.mywhoosh.com> öffnen und anmelden.
2. „Import Workout“, die Datei wählen, im Editor kurz prüfen.
3. „Export to MyWhoosh“. Die Einheit liegt dann in der App unter den eigenen Workouts.

Eigene Workouts kosten in MyWhoosh je einen Platz („Slot“), und davon gibt es ohne Abo nur
wenige. Löschen gibt den Platz zurück. Also jede Woche nur die Einheiten der Woche laden und
die alten löschen.

## Fahren

- **ERG-Modus:** Alle Einheiten sind dafür gebaut. Die Rolle braucht rund 3 Sekunden bis zur
  neuen Vorgabe.
- **Abbruchregel bei 30/15 und VO2max:** Der Satz ist zu Ende, wenn die Kadenz unter 85 fällt
  und nicht mehr hochkommt.
- **Tests:** Die Testabschnitte sind Free Ride, dort schaltet MyWhoosh ERG selbst aus. Vorher
  „Gradient Feel“ auf 0 %% stellen.
- **Hinweise:** Jede Datei blendet Ansagen ein: nächstes Intervall, Halbzeit, Trinken.

## FTP

Die Vorgaben stehen als Anteil der FTP in der Datei, gerechnet mit **%d W**. Sweetspot,
Schwelle und Grundlage wandern mit, wenn du die FTP in MyWhoosh änderst. Die 30/15, die
langen VO2max-Intervalle und die Öffner haben feste Wattzahlen: Nach einer FTP-Änderung in
`make_workouts.py` oben `FTP` anpassen, neu erzeugen und diese Dateien neu laden.
"""


def main():
    zeilen = []
    for wk in alle():
        k = kennzahlen(wk)
        pfad = os.path.join(OUT, wk['datei'] + '.zwo')
        io.open(pfad, 'w', encoding='ascii', newline='\n').write(zwo(wk))
        print('%-28s %6.1f min  Schnitt %3d W  NP %3d W  IF %.2f  TSS %3.0f' % (
            wk['datei'] + '.zwo', k['min'], k['schnitt'], k['np'], k['if'], k['tss']))
        zeilen.append('| %s | `%s.zwo` | %s | %s | %s |' % (
            wk['plan'], wk['datei'], dauer_text(int(round(k['min'] * 60))), wk['ziel'],
            '–' if any(s['t'] == 'frei' for s in wk['schritte']) else '%.0f' % k['tss']))
    io.open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8', newline='\n').write(
        LIESMICH % ('\n'.join(zeilen), FTP))
    print('%d Dateien und README.md in workouts/' % len(zeilen))


if __name__ == '__main__':
    main()
