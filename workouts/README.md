# Workouts für die Rolle

Strukturierte Einheiten für MyWhoosh im ZWO-Format. Die Dateien mit Sternchen sind von Hand
geschrieben, alle anderen erzeugt `werkzeug/make_workouts.py` — dort ändern, nicht hier.

## Welche Datei zu welcher Einheit

| Einheit im Plan | Datei | Dauer | Vorgabe | TSS |
|---|---|---|---|---|
| VO2max 30/15 2x10 (KW44) | `vo2max_30-15_2x10.zwo` | 48 min | 2 × 10 × 30/15 bei 325 W | 53 |
| VO2max 30/15 3x10 (KW45) | `vo2max_30-15_3x10.zwo` | 58:30 min | 3 × 10 × 30/15 bei 336 W | 72 |
| VO2max 30/15 3x13 (KW46, 48) | `vo2max_30-15_3x13.zwo` | 65:15 min | 3 × 13 × 30/15 bei 336 W | 85 |
| VO2max 30/15 3x13 (KW49–51) | `vo2max_30-15_3x13_340w.zwo` | 65:15 min | 3 × 13 × 30/15 bei 340 W | 87 |
| VO2max 30/15 3x13 (KW01–07) | `vo2max_30-15_3x13_345w.zwo` | 65:15 min | 3 × 13 × 30/15 bei 345 W | 88 |
| VO2max 5x4 min (KW03, 06) | `vo2max_5x4.zwo` | 66 min | 5 × 4 min bei 300 W | 80 |
| VO2max 2x4 min (KW04) | `vo2max_2x4.zwo` | 42 min | 2 × 4 min bei 285 W | 41 |
| Sweetspot 2x12 min | `sweetspot_2x12.zwo` | 54 min | 2 × 12 min bei 247 W | 56 |
| Sweetspot 2x15 min | `sweetspot_2x15.zwo` | 60 min | 2 × 15 min bei 247 W | 65 |
| Sweetspot 2x20 min | `sweetspot_2x20.zwo` | 70 min | 2 × 20 min bei 247 W | 79 |
| Sweetspot 3x15 min | `sweetspot_3x15.zwo` | 80 min | 3 × 15 min bei 247 W | 89 |
| Sweetspot 3x20 min | `sweetspot_3x20.zwo` | 95 min | 3 × 20 min bei 247 W | 110 |
| Schwelle 3x12 min | `schwelle_3x12.zwo` | 71 min | 3 × 12 min bei 263 W | 85 |
| Schwelle 3x15 min | `schwelle_3x15.zwo` | 80 min | 3 × 15 min bei 263 W | 100 |
| Schwelle 2x20 min | `schwelle_2x20.zwo` | 70 min | 2 × 20 min bei 263 W | 88 |
| Z2 Grundlage (60 min) | `z2_60min.zwo` | 60 min | 168–176 W im Wechsel | 38 |
| Z2 Grundlage (75 min) | `z2_75min.zwo` | 75 min | 168–176 W im Wechsel | 48 |
| Z2 Grundlage (90 min) | `z2_90min.zwo` | 90 min | 168–176 W im Wechsel | 58 |
| Recovery (50 min) | `locker_50min.zwo` | 50 min | 141 W | 22 |
| Recovery (60 min) | `locker_60min.zwo` | 60 min | 141 W | 26 |
| Long Endurance 2:30 | `lang_2h30.zwo` | 150 min | 171 W, alle 20 min 5 min bei 179 W | 98 |
| Long Endurance 2:45 | `lang_2h45.zwo` | 165 min | 171 W, alle 20 min 5 min bei 179 W | 108 |
| Long Endurance 3:00 | `lang_3h00.zwo` | 180 min | 171 W, alle 20 min 5 min bei 179 W | 119 |
| Long Endurance 3:15 | `lang_3h15.zwo` | 195 min | 171 W, alle 20 min 5 min bei 179 W | 129 |
| Long Endurance 3:30 | `lang_3h30.zwo` | 210 min | 171 W, alle 20 min 5 min bei 179 W | 139 |
| Openers | `openers.zwo` | 50 min | 3 × 1 min bei 298 W | 34 |
| TEST 2x20 min all-out | `test_2x20.zwo` | 90 min | 2 × 20 min maximal, Free Ride | – |
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
  „Gradient Feel“ auf 0 % stellen.
- **Hinweise:** Jede Datei blendet Ansagen ein: nächstes Intervall, Halbzeit, Trinken.

## FTP

Die Vorgaben stehen als Anteil der FTP in der Datei, gerechnet mit **271 W**. Sweetspot,
Schwelle und Grundlage wandern mit, wenn du die FTP in MyWhoosh änderst. Die 30/15, die
langen VO2max-Intervalle und die Öffner haben feste Wattzahlen: Nach einer FTP-Änderung in
`make_workouts.py` oben `FTP` anpassen, neu erzeugen und diese Dateien neu laden.
