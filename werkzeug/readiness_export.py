"""Tageswerte fuer das Readiness-Dashboard aus intervals.icu.

Schreibt eine JSON-Datei mit einer Zeile pro Tag (seit START):
date, rhr, sleep_h, sleep_score, ctl, atl, load, steps

Aufruf:  python3 readiness_export.py [ziel.json]
Braucht werkzeug/.env mit ATHLETE und KEY (wie push_events.py).
"""
import base64
import io
import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

HIER = os.path.dirname(os.path.abspath(__file__))
START = date(2026, 6, 1)


def env():
    with io.open(os.path.join(HIER, '.env'), encoding='utf-8') as f:
        return dict(l.strip().split('=', 1) for l in f if '=' in l)


def holen(pfad, e):
    url = "https://intervals.icu/api/v1/athlete/%s/%s" % (e['ATHLETE'], pfad)
    r = urllib.request.Request(url)
    r.add_header("Authorization", "Basic " + base64.b64encode(("API_KEY:%s" % e['KEY']).encode()).decode())
    r.add_header("User-Agent", "Mozilla/5.0 (training-plan-import)")
    r.add_header("Accept", "application/json")
    with urllib.request.urlopen(r, timeout=60) as x:
        return json.loads(x.read().decode())


def zahl(v, n=1):
    return None if v is None else round(float(v), n)


def main():
    ziel = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, 'readiness.json')
    e = env()
    heute = date.today()
    von, bis = START.isoformat(), heute.isoformat()
    well = holen("wellness?oldest=%s&newest=%s" % (von, bis), e)
    akt = holen("activities?oldest=%s&newest=%s" % (von, bis), e)

    last = defaultdict(float)
    for a in akt:
        last[a['start_date_local'][:10]] += a.get('icu_training_load') or 0

    zeilen = []
    for w in sorted(well, key=lambda w: w['id']):
        s = w.get('sleepSecs')
        zeilen.append({
            'date': w['id'],
            'rhr': w.get('restingHR'),
            'sleep_h': zahl(s / 3600 if s else None, 2),
            'sleep_score': zahl(w.get('sleepScore'), 0),
            'ctl': zahl(w.get('ctl')),
            'atl': zahl(w.get('atl')),
            'load': round(last.get(w['id'], 0)),
            'steps': w.get('steps'),
        })
    with io.open(ziel, 'w', encoding='utf-8') as f:
        json.dump(zeilen, f, ensure_ascii=False)
    print("%d Tage bis %s -> %s" % (len(zeilen), zeilen[-1]['date'] if zeilen else '-', ziel))


if __name__ == '__main__':
    main()
