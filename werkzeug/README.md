# Werkzeug

Die Skripte, mit denen der Trainingsplan erzeugt, als Markdown und HTML ausgegeben und in
intervals.icu eingetragen wird. Python 3, nur Standardbibliothek. **Alle Befehle aus diesem
Ordner heraus ausführen.**

## Den Plan ändern

Alle Wochen und Einheiten stehen in **`plan2.py`**. Dort ändern, dann der Reihe nach:

| Schritt | Befehl | Ergebnis |
|---|---|---|
| 1 | `python plan2.py` | `plan_data.json` — der Plan als Daten |
| 2 | `python export_md.py` | `../trainingsplan.md` |
| 2a | `python export_app.py` | `../docs/plan.html` und `../docs/analyse.html` — die Reiter der App |
| 3 | `python render_plan.py` | `_plan.json` — Plantabelle für den Bericht |
| 4 | `python assemble.py` | `../bericht/rennrad_analyse.html` |
| 5 | `python push_events.py --dry` | zeigt, was in intervals.icu passieren würde |
| 6 | `python push_events.py` | trägt den Plan in intervals.icu ein |

## Zugangsdaten für intervals.icu

`push_events.py` liest eine Datei `.env` in diesem Ordner:

```
ATHLETE=i378091
KEY=<dein intervals.icu-API-Key>
```

Den Key findest du in intervals.icu unter Settings → Developer Settings. **`.env` ist per
`.gitignore` ausgeschlossen und darf nie eingecheckt werden.**

## Was `push_events.py` genau tut

Vor dem Anlegen **löscht** es alle Einträge, deren `external_id` mit `claude-winter-` beginnt,
im Zeitraum 01.09.2026 bis 31.12.2027 — und legt den aktuellen Plan neu an. Eigene Einträge
ohne dieses Präfix bleiben unberührt. Deshalb immer zuerst `--dry`.

Die Wochentage verteilt es nach festem Muster: Kraft Mo/Fr, Key-Sessions Di/Do, Langfahrt Sa,
Rest auf Mi und So. Einheiten mit `tag=` in `plan2.py` (Tests, Rennen, Kursbesichtigung) sind
auf ihren Tag festgenagelt.

## Diagramme im Bericht

`gen_part1.py`, `gen_part2.py`, `gen_part3.py`, `gen_sens.py` und `gen_gap2.py` erzeugen die
Diagramme. Sie brauchen frisch aus intervals.icu abgerufene Rohdaten (`chartdata.json` und die
Aktivitäts- und Wellness-Daten), die **bewusst nicht** im Repo liegen.

Die fertig gerenderten Diagramme liegen als `_p1.json` bis `_p3.json` bei. Damit baut
`assemble.py` den Bericht auch ohne Rohdaten neu — solange sich an den Diagrammen nichts ändert.

Reihenfolge, falls die Diagramme neu gebaut werden: `gen_part1.py`, `gen_part2.py`,
`gen_part3.py`, dann `gen_sens.py` und `gen_gap2.py` (die beiden ergänzen `_p3.json`).

## Der Bericht

`assemble.py` setzt `template.html` mit dem Stylesheet und den Bausteinen aus `build.py`
zusammen. Texte des Berichts ändert man in `template.html`, Kennzahlen-Kacheln, Hebel,
Roadmap und Winterphasen in `build.py`.
