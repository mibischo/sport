# Fueling-Rechner

Kleine Web-App mit drei Reitern. Sie läuft ohne Server, ohne Konto und nach dem ersten Öffnen
auch ohne Netz.

- **Fueling** (Startseite): Dauer und Gramm pro Stunde eingeben, heraus kommen Packliste,
  Mischung je Behälter und der Takt für unterwegs.
- **Trainingsplan:** der Wochenplan aus `trainingsplan.md`. Die aktuelle Woche ist markiert,
  die Seite springt beim Öffnen dorthin.
- **Analyse:** die Saisonanalyse aus `analyse.md`.

## Was sie rechnet

- **Bedarf:** Stunden × Gramm pro Stunde.
- **Packliste:** Flaschen (500, 750 oder 1000 ml), Flasks (150 oder 300 ml), Nachfüllungen und Riegel mit frei wählbaren Gramm Kohlenhydraten. Die Automatik schlägt eine Verteilung vor; trägst du selbst Gramm ein, zeigt „Eingepackt“ laufend, wie viel vom Bedarf schon verteilt ist.
- **Mischung:** Maltodextrin, Fruktose und Salz je Behälter, dazu die Summe zum Abwiegen.
- **Konzentration:** Gramm Kohlenhydrate pro Milliliter über alles. Bis 0,15 passt es, bis 0,20 ist es an der Grenze.
- **Unterwegs:** eine Portion je Takt, ausgedrückt in Millilitern aus Flask oder Flasche oder als Stück vom Riegel.
- **Details:** geschätzte Osmolalität je Behälter und Energie, auf Wunsch gegen die Arbeit in kJ.

Alle Zahlen sind Richtwerte. Mischverhältnis, Natriumquelle und Grenzen stehen unter
„Einstellungen“; gespeichert wird nur im Browser des Geräts.

## Veröffentlichung

Die App wird aus diesem Repository über GitHub Pages ausgeliefert: <https://mibischo.github.io/sport/>

GitHub Pages liefert die App aus dem Branch `main` aus. Unter **Settings → Pages** steht bei
„Build and deployment“ die Quelle **Deploy from a branch**; für den Ordner gibt es zwei
Möglichkeiten:

- **`/docs`** (empfohlen): Nur die App wird als Webseite veröffentlicht, die Adresse ist
  <https://mibischo.github.io/sport/>.
- **`/ (root)`**: Das ganze Repository wird als Webseite ausgeliefert, auch der Bericht unter
  `bericht/`. Die App liegt dann unter `…/sport/docs/`; die `index.html` im Hauptverzeichnis
  leitet von der Startadresse dorthin weiter.

Nach einem Push ist die neue Fassung in ein bis zwei Minuten online.

Die leere Datei `.nojekyll` sorgt dafür, dass GitHub die Dateien unverändert ausliefert. Die
App nutzt nur relative Pfade und läuft deshalb unter jeder Adresse.

## Installieren

- **Android / Chrome:** Seite öffnen, dann „Installieren“ oben rechts oder im Browser-Menü.
- **iPhone / Safari:** Teilen-Symbol, dann „Zum Home-Bildschirm“.
- **Desktop / Chrome, Edge:** Installieren-Symbol in der Adressleiste.

## Ändern und aktualisieren

| Datei | Inhalt |
|---|---|
| `index.html` | Fueling-Rechner, Aufbau der Seite |
| `app.js` | Rechnung und Bedienung des Rechners; Vorgaben stehen oben in `DEF` |
| `plan.html`, `analyse.html` | Trainingsplan und Analyse — **erzeugt**, nicht von Hand ändern |
| `doc.js` | markiert im Trainingsplan die aktuelle Woche |
| `style.css` | Aussehen aller Seiten, hell und dunkel |
| `pwa.js`, `sw.js` | Installieren-Taste und Offline-Cache |
| `manifest.webmanifest`, `icons/` | Name, Farben und Symbole der installierten App |

Trainingsplan und Analyse entstehen aus den Markdown-Dateien im Hauptverzeichnis. Nach einer
Änderung an `trainingsplan.md` oder `analyse.md` im Ordner `werkzeug/` neu erzeugen:

```bash
python export_app.py
```

Nach jeder Änderung in `sw.js` die Zeile `const VERSION = 'v6'` hochzählen. Installierte
Geräte holen sich die neue Fassung beim nächsten Öffnen und zeigen sie beim übernächsten.

## Lokal ausprobieren

```bash
python -m http.server 8791
```

Dann `http://localhost:8791` öffnen. Über `file://` funktioniert die Offline-Funktion nicht.
