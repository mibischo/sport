# Fueling-Rechner

Kleine Web-App zum Planen der Verpflegung auf dem Rad: Dauer und Gramm pro Stunde eingeben,
heraus kommen Packliste, Mischung je Behälter und der Takt für unterwegs. Läuft ohne Server,
ohne Konto und nach dem ersten Öffnen auch ohne Netz.

## Was sie rechnet

- **Bedarf:** Stunden × Gramm pro Stunde.
- **Packliste:** Flaschen (500, 750 oder 1000 ml), Flasks (150 oder 300 ml) und Nachfüllungen. Die Automatik schlägt eine Verteilung vor; trägst du selbst Gramm ein, zeigt „Eingepackt“ laufend, wie viel vom Bedarf schon verteilt ist.
- **Mischung:** Maltodextrin, Fruktose und Salz je Behälter, dazu die Summe zum Abwiegen.
- **Konzentration:** Gramm Kohlenhydrate pro Milliliter über alles. Bis 0,15 passt es, bis 0,20 ist es an der Grenze.
- **Unterwegs:** eine Portion je Takt, ausgedrückt in Millilitern aus Flask oder Flasche.
- **Details:** geschätzte Osmolalität je Behälter und Energie, auf Wunsch gegen die Arbeit in kJ.

Alle Zahlen sind Richtwerte. Mischverhältnis, Natriumquelle und Grenzen stehen unter
„Einstellungen“; gespeichert wird nur im Browser des Geräts.

## Veröffentlichung

Die App wird aus diesem Repository über GitHub Pages ausgeliefert: <https://mibischo.github.io/sport/>

GitHub Pages liefert den Ordner `docs/` des Branches `main` direkt aus. Der Rest des
Repositories wird nicht als Webseite veröffentlicht. Der Ordner heißt `docs`, weil Pages neben
dem Hauptverzeichnis nur diesen Namen anbietet.

Einmalig nötig: im Repository unter **Settings → Pages** bei „Build and deployment“ als
Quelle **Deploy from a branch** wählen, Branch `main`, Ordner `/docs`. Danach genügt ein
Push; nach ein bis zwei Minuten ist die neue Fassung online.

Die leere Datei `.nojekyll` sorgt dafür, dass GitHub die Dateien unverändert ausliefert. Die
App nutzt nur relative Pfade und läuft deshalb unter jeder Adresse.

## Installieren

- **Android / Chrome:** Seite öffnen, dann „Installieren“ oben rechts oder im Browser-Menü.
- **iPhone / Safari:** Teilen-Symbol, dann „Zum Home-Bildschirm“.
- **Desktop / Chrome, Edge:** Installieren-Symbol in der Adressleiste.

## Ändern und aktualisieren

| Datei | Inhalt |
|---|---|
| `index.html` | Aufbau der Seite |
| `style.css` | Aussehen, hell und dunkel |
| `app.js` | Rechnung und Bedienung; Vorgaben stehen oben in `DEF` |
| `sw.js` | Offline-Cache |
| `manifest.webmanifest`, `icons/` | Name, Farben und Symbole der installierten App |

Nach jeder Änderung in `sw.js` die Zeile `const VERSION = 'v2'` hochzählen. Installierte
Geräte holen sich die neue Fassung beim nächsten Öffnen und zeigen sie beim übernächsten.

## Lokal ausprobieren

```bash
python -m http.server 8791
```

Dann `http://localhost:8791` öffnen. Über `file://` funktioniert die Offline-Funktion nicht.
