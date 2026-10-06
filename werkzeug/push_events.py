# -*- coding: utf-8 -*-
"""Legt den Wochenplan als geplante Workouts in intervals.icu an.
Alle Events bekommen external_id "claude-winter-..." und lassen sich damit
jederzeit geschlossen wieder entfernen.

  python push_events.py --dry          zeigt nur, was passieren wuerde
  python push_events.py                loescht alle Plan-Events und legt sie neu an
  python push_events.py --sync         aendert nur, was sich im Plan geaendert hat:
                                       nichts wird geloescht, Vergangenes und von Hand
                                       verschobene Termine bleiben, wie sie sind
  python push_events.py --sync --dry   zeigt die Aenderungen, ohne sie zu schreiben"""
import json, io, sys, time, base64, urllib.request, urllib.error
from datetime import date, timedelta

ENV = dict(l.strip().split('=', 1) for l in io.open('.env', encoding='utf-8') if '=' in l)
ATH, KEY = ENV['ATHLETE'], ENV['KEY']
BASE = "https://intervals.icu/api/v1/athlete/%s" % ATH
AUTH = base64.b64encode(("API_KEY:%s" % KEY).encode()).decode()
DRY = "--dry" in sys.argv
SYNC = "--sync" in sys.argv

W = json.load(open('plan_data.json', encoding='utf-8'))

# Mo=1 ... So=7
SLOT_KRAFT = [1, 5]
SLOT_KEY = [2, 4]
SLOT_LANG = [6]
SLOT_REST = [3, 7, 1, 5]   # Mi, So, dann Ausweichtage


def is_lang(s):
    n = s['name']
    return n.startswith('Long Endurance') or n.startswith('4-Stunden')


def belege(sess):
    """Ordnet jeder Einheit einen Wochentag zu (1=Mo ... 7=So). Nichts geht verloren."""
    frei = set(range(1, 8))
    plan = []

    def nimm(prefs):
        for d in prefs:
            if d in frei:
                frei.discard(d)
                return d
        for d in sorted(frei):
            frei.discard(d)
            return d
        return 7

    # fest verankerte Einheiten zuerst
    fix = [x for x in sess if x.get('tag')]
    for x in fix:
        d = int(x['tag'])
        if d in frei:
            frei.discard(d)
        plan.append((d, x))
    sess = [x for x in sess if not x.get('tag')]
    openers = [x for x in sess if x['name'].startswith('Openers')]
    rest_all = [x for x in sess if not x['name'].startswith('Openers')]
    kraft = [x for x in rest_all if x['type'] == 'WeightTraining']
    lang = [x for x in rest_all if x['type'] == 'Ride' and is_lang(x)]
    keys = [x for x in rest_all if x['type'] == 'Ride' and x.get('key') and not is_lang(x)]
    rest = [x for x in rest_all if x['type'] == 'Ride' and not x.get('key') and not is_lang(x)]

    # Keys zuerst, damit der Openers-Tag feststeht
    keytage = []
    for x in keys:
        t = nimm(SLOT_KEY)
        keytage.append(t)
        plan.append((t, x))
    # Openers direkt davor reservieren, BEVOR der Rest verteilt wird
    for x in openers:
        ziel = (min(keytage) - 1) if keytage else 1
        if ziel < 1 or ziel not in frei:
            ziel = nimm([d for d in (1, 3, 7, 4, 6) if d in frei] or sorted(frei))
        else:
            frei.discard(ziel)
        plan.append((ziel, x))
    for x in lang:
        plan.append((nimm(SLOT_LANG), x))
    for x in kraft:
        plan.append((nimm(SLOT_KRAFT), x))
    for x in rest:
        plan.append((nimm(SLOT_REST), x))
    return sorted(plan)


def req(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", "Basic " + AUTH)
    r.add_header("User-Agent", "Mozilla/5.0 (training-plan-import)")
    r.add_header("Accept", "*/*")
    if data:
        r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, timeout=45) as resp:
        body = resp.read().decode()
        return resp.status, (json.loads(body) if body.strip() else None)


# --- 0. Events aus dem Plan bauen ---
events = []
for y, w, ph, sess, fok in W:
    for tag, s in belege(sess):
        d = date.fromisocalendar(y, w, tag)
        desc = s['desc']
        if s['type'] == 'Ride' and s['if']:
            desc += "\n\nGeplant: %d min, IF %.2f, %d TSS." % (s['min'], s['if'], s['tss'])
        desc += "\n[Winterplan KW%02d]" % w
        events.append({
            "category": "WORKOUT",
            "start_date_local": d.isoformat() + "T00:00:00",
            "type": s['type'],
            "name": s['name'],
            "description": desc,
            "moving_time": s['min'] * 60,
            "icu_training_load": s['tss'],
            "external_id": "claude-winter-%dw%02d-%d" % (y, w, tag),
        })

print("Zu erstellen: %d Events, %s bis %s"
      % (len(events), events[0]['start_date_local'][:10], events[-1]['start_date_local'][:10]))

# --- 1. vorhandene Plan-Events holen ---
st, alt = req("GET", BASE + "/events?oldest=2026-09-01&newest=2027-12-31")

# --- 1a. --sync: nur Geaendertes nachziehen, nichts loeschen ---
if SYNC:
    def norm(v):
        return " ".join(v.split()) if isinstance(v, str) else v
    FELDER = ("name", "description", "moving_time", "icu_training_load", "type")
    heute = date.today().isoformat()
    vorhanden = {e.get("external_id"): e for e in (alt or [])
                 if str(e.get("external_id", "")).startswith("claude-winter-")}
    neu = geaendert = gleich = 0
    for e in events:
        if e["start_date_local"][:10] < heute:
            continue
        v = vorhanden.get(e["external_id"])
        if v is None:
            neu += 1
            print("  + %s  %s" % (e["start_date_local"][:10], e["name"]))
            if not DRY:
                req("POST", BASE + "/events", e)
                time.sleep(0.06)
            continue
        diff = [k for k in FELDER if norm(v.get(k)) != norm(e[k])]
        if not diff:
            gleich += 1
            continue
        geaendert += 1
        print("  ~ %s  %s  ->  %s  (%s)" % (v["start_date_local"][:10], v.get("name"), e["name"], ", ".join(diff)))
        if not DRY:
            req("PUT", "%s/events/%s" % (BASE, v["id"]), dict((k, e[k]) for k in FELDER))
            time.sleep(0.06)
    print("%s%d geaendert, %d neu, %d unveraendert (ab %s)"
          % ("[dry] " if DRY else "", geaendert, neu, gleich, heute))
    raise SystemExit(0)

# --- 2. alte claude-winter-Events entfernen (Idempotenz) ---
weg = [e for e in (alt or []) if str(e.get('external_id', '')).startswith('claude-winter-')]
if weg and not DRY:
    for e in weg:
        try:
            req("DELETE", "%s/events/%s" % (BASE, e['id']))
        except Exception:
            pass
    print("%d vorhandene claude-winter-Events entfernt" % len(weg))
elif weg:
    print("[dry] %d vorhandene claude-winter-Events wuerden entfernt" % len(weg))

if DRY:
    print("\n--- Beispielwoche KW46 ---")
    TAG = "MoDiMiDoFrSaSo"
    for e in events:
        if "w46" in e['external_id']:
            t = int(e['external_id'][-1])
            print("  %s %s  %-26s %3d min  TSS %3d  [%s]"
                  % (TAG[(t-1)*2:t*2], e['start_date_local'][:10], e['name'],
                     e['moving_time'] // 60, e['icu_training_load'], e['type']))
    raise SystemExit(0)

# --- 3. anlegen ---
ok = err = 0
fehler = []
for i, e in enumerate(events, 1):
    try:
        st, _ = req("POST", BASE + "/events", e)
        ok += 1
    except urllib.error.HTTPError as ex:
        err += 1
        fehler.append("%s %s -> %s %s" % (e['start_date_local'][:10], e['name'],
                                          ex.code, ex.read().decode()[:120]))
    except Exception as ex:
        err += 1
        fehler.append("%s %s -> %s" % (e['start_date_local'][:10], e['name'], ex))
    if i % 25 == 0:
        print("  ... %d/%d" % (i, len(events)))
    time.sleep(0.06)

print("\nAngelegt: %d   Fehler: %d" % (ok, err))
for f in fehler[:10]:
    print("  !", f)
