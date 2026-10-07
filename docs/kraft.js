// Krafttraining: Einheit mitschreiben, als Notiz kopieren, Verlauf zeigen.
// Gespeichert wird nur im Browser (localStorage).
(() => {
  'use strict';

  const KEY = 'kraft-log.v1';
  const MAX_SETS = 10;
  const SHOWN = 6;    // Einheiten in der Liste, bevor „Alle anzeigen“ erscheint
  const SPARK = 12;   // Punkte je Verlaufskurve
  const TYPES = { kg: 'mit Gewicht', bw: 'ohne Gewicht', time: 'auf Zeit' };

  // Vorgaben für den ersten Start. Danach gilt je Übung, was zuletzt gespeichert wurde.
  const DEF_EX = [
    { id: 'squat', name: 'Squat', type: 'kg', kg: 55, sets: 3, per: 10 },
    { id: 'rdl', name: 'RDL', type: 'kg', kg: 55, sets: 3, per: 10 },
    { id: 'squat-einbeinig', name: 'Squat einbeinig', type: 'kg', kg: 12, sets: 3, per: 10 },
    { id: 'liegestuetz', name: 'Liegestütz', type: 'bw', sets: 3, per: 12 },
    { id: 'plank', name: 'Plank', type: 'time', sets: 3, per: 60 }
  ];

  const $ = id => document.getElementById(id);
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const round2 = x => Math.round(x * 100) / 100;
  const toNum = t => parseFloat(String(t).replace(',', '.'));
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const norm = s => String(s).trim().toLowerCase();
  const pad = n => String(n).padStart(2, '0');
  const iso = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const today = () => iso(new Date());
  const asDate = s => new Date(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10));
  const WD = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
  const dShort = s => `${s.slice(8, 10)}.${s.slice(5, 7)}.`;
  const dLong = s => `${WD[asDate(s).getDay()]} ${s.slice(8, 10)}.${s.slice(5, 7)}.${s.slice(0, 4)}`;
  const isDate = s => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && iso(asDate(s)) === s;

  // ---------- Schreibweisen ----------
  const fmtKg = kg => String(round2(kg)).replace('.', ',');
  const fmtDur = s => (s % 60 === 0 ? `${s / 60}min` : `${s}s`);   // in der Notiz: 1min, 45s
  const clock = s => `${Math.floor(s / 60)}:${pad(s % 60)}`;
  const durText = s => (s < 60 ? `${s} s` : `${s % 60 === 0 ? s / 60 : clock(s)} min`);
  const setsOf = it => (it.type === 'time' ? it.secs : it.reps) || [];
  const total = it => setsOf(it).reduce((a, b) => a + b, 0);
  const weighted = it => it.type === 'kg' && it.kg > 0;

  // [10, 10, 9, 9] -> [{ v: 10, n: 2 }, { v: 9, n: 2 }]
  function runs(list) {
    const out = [];
    for (const v of list) {
      const last = out[out.length - 1];
      if (last && last.v === v) last.n += 1; else out.push({ v, n: 1 });
    }
    return out;
  }

  // Zeile der Notiz, so wie sie in intervals.icu steht: „Squat 55 3x10“
  function lineOf(it) {
    if (it.skip) return `${it.name} -`;
    const sets = runs(setsOf(it)).map(g => `${g.n}x${it.type === 'time' ? fmtDur(g.v) : g.v}`).join(' ');
    return weighted(it) ? `${it.name} ${fmtKg(it.kg)} ${sets}` : `${it.name} ${sets}`;
  }
  const noteOf = s => s.items.map(lineOf).join('\n') + (s.note ? `\n\n${s.note}` : '');

  // Dasselbe zum Lesen: „55 kg · 3 × 10“
  const setsText = it => runs(setsOf(it)).map(g => `${g.n} × ${it.type === 'time' ? durText(g.v) : g.v}`).join(', ');
  function sumOf(it) {
    if (it.skip) return 'ausgelassen';
    return weighted(it) ? `${fmtKg(it.kg)} kg · ${setsText(it)}` : setsText(it);
  }

  // Kennzahl für den Verlauf: Gewicht, sonst Summe der Wiederholungen oder Sekunden
  const metric = it => (weighted(it) ? it.kg : total(it));
  function metricParts(it, y) {
    if (weighted(it)) return [fmtKg(y), 'kg'];
    if (it.type !== 'time') return [String(y), 'Wdh.'];
    return y < 60 ? [String(y), 's'] : [y % 60 === 0 ? String(y / 60) : clock(y), 'min'];
  }
  function deltaText(it, diff) {
    const sign = diff > 0 ? '+' : '−', a = Math.abs(diff);
    if (weighted(it)) return `${sign}${fmtKg(a)} kg`;
    if (it.type !== 'time') return `${sign}${a} Wdh.`;
    return `${sign}${durText(a)}`;
  }

  // ---------- Notiz lesen ----------
  const SET = /^(\d{1,2})[x×](\d+(?:[.,]\d+)?)(min|s)?$/i;
  const WEIGHT = /^\d+(?:[.,]\d+)?(?:kg)?$/i;

  // „Squat 55 2x10 2x9“ -> Eintrag ohne id; null, wenn die Zeile keine Übung ist
  function parseLine(line) {
    const t = line.trim().split(/\s+/);
    if (t.length >= 2 && /^[-–—]$/.test(t[t.length - 1])) return { name: t.slice(0, -1).join(' '), skip: true };
    const first = t.findIndex(x => SET.test(x));
    if (first < 1 || !t.slice(first).every(x => SET.test(x))) return null;
    const hasKg = first >= 2 && WEIGHT.test(t[first - 1]);
    const sets = t.slice(first).map(x => SET.exec(x));
    const timed = sets.some(m => m[3]);
    const list = [];
    for (const m of sets) {
      const v = toNum(m[2]) * (timed && String(m[3]).toLowerCase() === 'min' ? 60 : 1);
      for (let i = 0; i < +m[1] && list.length < MAX_SETS; i++) list.push(Math.max(1, Math.round(v)));
    }
    if (!list.length) return null;
    const it = { name: t.slice(0, hasKg ? first - 1 : first).join(' '), skip: false, type: timed ? 'time' : hasKg ? 'kg' : 'bw' };
    if (timed) it.secs = list; else it.reps = list;
    if (hasKg && !timed) it.kg = toNum(t[first - 1]);
    return it;
  }

  // Datum am Zeilenanfang: 2026-10-07, 07.10.2026 oder Mi 07.10.26
  function dateOf(line) {
    let m = /^(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)/.exec(line), y, mo, d;
    if (m) { y = +m[1]; mo = +m[2]; d = +m[3]; } else {
      m = /^(?:[A-Za-zÄÖÜäöü]{2,10}[.,]?\s+)?(\d{1,2})\.(\d{1,2})\.(\d{4}|\d{2})(?!\d)/.exec(line);
      if (!m) return null;
      d = +m[1]; mo = +m[2]; y = +m[3] < 100 ? 2000 + +m[3] : +m[3];
    }
    const s = `${y}-${pad(mo)}-${pad(d)}`;
    return isDate(s) ? s : null;
  }

  function parseImport(text) {
    const out = [];
    let cur = null;
    for (const raw of String(text).split(/\r?\n/)) {
      const line = raw.trim();
      if (!line) continue;
      const entry = parseLine(line), date = entry ? null : dateOf(line);
      if (date) { cur = { date, items: [], note: '' }; out.push(cur); continue; }
      if (!cur) continue;
      if (entry) cur.items.push(entry); else cur.note += (cur.note ? '\n' : '') + line;
    }
    return out.filter(s => s.items.length);
  }

  // ---------- Speicher ----------
  function cleanEntry(x) {
    if (!x || typeof x !== 'object' || typeof x.name !== 'string' || !x.name.trim()) return null;
    const type = TYPES[x.type] ? x.type : 'bw';
    const list = (a, max) => (Array.isArray(a) ? a.map(Number).filter(v => isFinite(v) && v > 0).slice(0, MAX_SETS).map(v => clamp(Math.round(v), 1, max)) : []);
    const it = { id: String(x.id || ''), name: x.name.trim().slice(0, 40), type, skip: !!x.skip };
    if (type === 'kg') it.kg = clamp(round2(Number(x.kg) || 0), 0, 500);
    if (type === 'time') it.secs = list(x.secs, 3600); else it.reps = list(x.reps, 999);
    return it.skip || setsOf(it).length ? it : null;
  }
  function cleanSession(s) {
    if (!s || !isDate(s.date) || !Array.isArray(s.items)) return null;
    const items = s.items.map(cleanEntry).filter(Boolean);
    return items.length ? { date: s.date, items, note: typeof s.note === 'string' ? s.note.slice(0, 2000) : '' } : null;
  }
  const byDate = (a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0);

  function load() {
    let d = null;
    try { d = JSON.parse(localStorage.getItem(KEY)); } catch (e) { /* neu anfangen */ }
    d = d && typeof d === 'object' ? d : {};
    const seen = new Set();
    const exercises = (Array.isArray(d.exercises) ? d.exercises : DEF_EX)
      .map(x => (x && x.id && typeof x.name === 'string' && x.name.trim()
        ? { id: String(x.id), name: x.name.trim().slice(0, 40), type: TYPES[x.type] ? x.type : 'kg' } : null))
      .filter(x => x && !seen.has(x.id) && seen.add(x.id));
    const dates = new Set();
    const sessions = (Array.isArray(d.sessions) ? d.sessions : []).map(cleanSession)
      .filter(s => s && !dates.has(s.date) && dates.add(s.date)).sort(byDate);
    return { exercises, sessions, draft: d.draft };
  }
  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify({ v: 1, exercises: DB.exercises, sessions: DB.sessions, draft: E }));
    } catch (e) { /* privater Modus oder Speicher voll */ }
  }

  // ---------- Editor ----------
  // jüngster Eintrag einer Übung bis zu einem Datum; done: nur ausgeführte
  function lastEntry(ex, until, done) {
    for (let i = DB.sessions.length - 1; i >= 0; i--) {
      const s = DB.sessions[i];
      if (until && s.date > until) continue;
      const it = s.items.find(x => x.id === ex.id);
      if (it && (!done || (!it.skip && setsOf(it).length))) return it;
    }
    return null;
  }
  function blank(ex) {
    const d = DEF_EX.find(x => x.id === ex.id) || {};
    const n = d.sets || 3;
    return {
      skip: false, split: false, kg: d.kg || 20,
      reps: Array(n).fill(d.type !== 'time' && d.per ? d.per : 10),
      secs: Array(n).fill(d.type === 'time' && d.per ? d.per : 60)
    };
  }
  function fromEntry(ex, it, skip) {
    const v = blank(ex);
    if (it) {
      if (typeof it.kg === 'number') v.kg = it.kg;
      if (it.reps && it.reps.length) v.reps = it.reps.slice();
      if (it.secs && it.secs.length) v.secs = it.secs.slice();
    }
    v.skip = !!skip;
    const list = ex.type === 'time' ? v.secs : v.reps;
    v.split = list.some(x => x !== list[0]);
    return v;
  }
  // Werte für ein Datum: die gespeicherte Einheit, sonst je Übung der letzte Stand davor
  function editorFor(date) {
    const saved = DB.sessions.find(s => s.date === date);
    const items = {};
    for (const ex of DB.exercises) {
      const here = saved && saved.items.find(x => x.id === ex.id);
      const recent = lastEntry(ex, date, false);
      const values = here && !here.skip && setsOf(here).length ? here : lastEntry(ex, date, true);
      items[ex.id] = fromEntry(ex, values, saved ? !here || here.skip : !!(recent && recent.skip));
    }
    return { date, items, note: saved ? saved.note : '', dirty: false };
  }
  // Entwurf von heute weiterverwenden, sonst frisch aus dem Verlauf füllen
  function restore(draft) {
    const e = editorFor(today());
    if (!draft || draft.date !== e.date || !draft.items || typeof draft.items !== 'object') return e;
    for (const ex of DB.exercises) {
      const v = draft.items[ex.id];
      if (!v || typeof v !== 'object') continue;
      const list = (a, max) => (Array.isArray(a) ? a.map(Number).filter(x => isFinite(x) && x > 0).slice(0, MAX_SETS).map(x => clamp(Math.round(x), 1, max)) : []);
      const reps = list(v.reps, 999), secs = list(v.secs, 3600);
      if (reps.length) e.items[ex.id].reps = reps;
      if (secs.length) e.items[ex.id].secs = secs;
      if (isFinite(+v.kg)) e.items[ex.id].kg = clamp(round2(+v.kg), 0, 500);
      e.items[ex.id].skip = !!v.skip;
      e.items[ex.id].split = !!v.split;
    }
    if (typeof draft.note === 'string') e.note = draft.note.slice(0, 2000);
    e.dirty = !!draft.dirty;
    return e;
  }
  const listOf = (ex, v) => (ex.type === 'time' ? v.secs : v.reps);
  function entryOf(ex, v) {
    const it = { id: ex.id, name: ex.name, type: ex.type, skip: v.skip };
    if (ex.type === 'kg') it.kg = v.kg;
    if (ex.type === 'time') it.secs = v.secs.slice(); else it.reps = v.reps.slice();
    return it;
  }
  const sessionFromEditor = () => ({ date: E.date, items: DB.exercises.map(ex => entryOf(ex, E.items[ex.id])), note: E.note.trim() });
  function upsert(s) {
    DB.sessions = DB.sessions.filter(x => x.date !== s.date).concat([s]).sort(byDate);
  }

  // ---------- Zwischenablage ----------
  async function copy(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); return true; }
    } catch (e) { /* älterer Weg unten */ }
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand('copy');
      ta.remove();
      return ok;
    } catch (e) { return false; }
  }
  function status(el, kind, text) {
    el.className = `status ${kind}`;
    el.innerHTML = `<svg aria-hidden="true"><use href="#i-${kind}"/></svg><span></span>`;
    el.lastChild.textContent = text;
    el.hidden = false;
  }
  function clearStatus() {
    $('save-status').hidden = true;
    $('copy-fallback').hidden = true;
  }

  // ---------- Anzeige: Einheit ----------
  const stepper = (act, d, inner, less, more) =>
    `<button type="button" class="mini" data-act="${act}" data-d="-${d}" aria-label="${less}">−</button>${inner}` +
    `<button type="button" class="mini" data-act="${act}" data-d="${d}" aria-label="${more}">+</button>`;

  function exTemplate(ex) {
    const id = esc(ex.id), timed = ex.type === 'time';
    const kg = ex.type !== 'kg' ? '' : `<div class="ctrl" role="group" aria-label="Gewicht">
          <span class="label">Gewicht</span>
          <div class="ctrl-r">${stepper('kg', 1, '<label class="ct-g"><input class="ct-in" type="text" inputmode="decimal" data-f="kg" aria-label="Gewicht in Kilogramm"><small>kg</small></label>', 'Weniger Gewicht', 'Mehr Gewicht')}</div>
        </div>`;
    const per = timed
      ? stepper('per', 15, '<output class="ctrl-val wide" data-o="per"></output>', '15 Sekunden kürzer', '15 Sekunden länger')
      : stepper('per', 1, '<label class="ct-g"><input class="ct-in" type="text" inputmode="numeric" data-f="per" aria-label="Wiederholungen je Satz"></label>', 'Eine Wiederholung weniger', 'Eine Wiederholung mehr');
    return `<li class="ex" data-id="${id}">
      <button type="button" class="ex-head" data-act="open" aria-expanded="false" aria-controls="ex-${id}">
        <span class="ex-name">${esc(ex.name)}</span><span class="ex-sum"></span>
      </button>
      <div class="ex-body" id="ex-${id}" hidden>
        ${kg}
        <div class="ctrl" role="group" aria-label="Sätze">
          <span class="label">Sätze</span>
          <div class="ctrl-r">${stepper('sets', 1, '<output class="ctrl-val" data-o="sets"></output>', 'Ein Satz weniger', 'Ein Satz mehr')}</div>
        </div>
        <div class="ctrl" data-row="uni" role="group" aria-label="${timed ? 'Dauer je Satz' : 'Wiederholungen'}">
          <span class="label">${timed ? 'Dauer je Satz' : 'Wiederholungen'}</span>
          <div class="ctrl-r">${per}</div>
        </div>
        <div class="ctrl" data-row="split" role="group" aria-label="${timed ? 'Sekunden je Satz' : 'Wiederholungen je Satz'}" hidden>
          <span class="label">${timed ? 'Sekunden je Satz' : 'Wdh. je Satz'}</span>
          <div class="ex-sets"></div>
        </div>
        <div class="ex-opts">
          <button type="button" class="chip sm" data-act="split" aria-pressed="false">Sätze einzeln</button>
          <button type="button" class="chip sm" data-act="skip" aria-pressed="false">Auslassen</button>
        </div>
      </div>
    </li>`;
  }

  function syncEx(li, ex) {
    const v = E.items[ex.id], list = listOf(ex, v), q = sel => li.querySelector(sel);
    const isOpen = open === ex.id, timed = ex.type === 'time';
    const put = (inp, val) => { if (inp && inp !== document.activeElement) inp.value = val; };
    q('.ex-head').setAttribute('aria-expanded', String(isOpen));
    q('.ex-body').hidden = !isOpen;
    li.classList.toggle('skipped', v.skip);
    q('.ex-sum').textContent = sumOf(entryOf(ex, v));

    put(q('[data-f="kg"]'), fmtKg(v.kg));
    q('[data-o="sets"]').textContent = list.length;
    const [setsLess, setsMore] = li.querySelectorAll('[data-act="sets"]');
    setsLess.disabled = list.length <= 1;
    setsMore.disabled = list.length >= MAX_SETS;

    q('[data-row="uni"]').hidden = v.split;
    q('[data-row="split"]').hidden = !v.split;
    if (timed) q('[data-o="per"]').textContent = clock(list[0]); else put(q('[data-f="per"]'), list[0]);
    const box = q('.ex-sets');
    if (box.children.length !== list.length) {
      box.innerHTML = list.map((_, i) => `<input class="ct-in sm" type="text" inputmode="numeric" data-f="set" data-i="${i}" aria-label="Satz ${i + 1}">`).join('');
    }
    [...box.children].forEach((inp, i) => put(inp, list[i]));
    q('[data-act="split"]').setAttribute('aria-pressed', String(v.split));
    q('[data-act="skip"]').setAttribute('aria-pressed', String(v.skip));
  }

  function renderEditor() {
    const ul = $('exs');
    const sig = DB.exercises.map(x => `${x.id}:${x.type}:${x.name}`).join('|');
    if (ul.dataset.sig !== sig) {
      ul.innerHTML = DB.exercises.map(exTemplate).join('');
      ul.dataset.sig = sig;
    }
    DB.exercises.forEach((ex, i) => syncEx(ul.children[i], ex));

    const date = $('date'), note = $('note');
    if (date !== document.activeElement) date.value = E.date;
    if (note !== document.activeElement) note.value = E.note;
    const saved = DB.sessions.some(s => s.date === E.date);
    const before = DB.sessions.filter(s => s.date < E.date).pop();
    $('unit-note').textContent = saved
      ? 'Für diesen Tag ist schon eine Einheit gespeichert. Speichern überschreibt sie.'
      : E.dirty
        ? 'Geändert, noch nicht gespeichert.'
        : before
          ? `Werte von der letzten Einheit am ${dShort(before.date)} übernommen. Übung antippen, um etwas zu ändern.`
          : 'Übung antippen, um Gewicht, Sätze und Wiederholungen zu ändern.';
  }

  // ---------- Anzeige: Verlauf ----------
  // ausgeführte Einträge einer Übung, älteste zuerst, in der Art, die die Übung heute hat
  function seriesOf(ex) {
    const out = [];
    for (const s of DB.sessions) {
      const it = s.items.find(x => x.id === ex.id);
      if (it && !it.skip && it.type === ex.type && setsOf(it).length) out.push({ date: s.date, it, y: metric(it) });
    }
    // eine Kurve braucht eine Einheit: Gewicht oder Wiederholungen, nicht gemischt
    const last = out[out.length - 1];
    return (last ? out.filter(p => weighted(p.it) === weighted(last.it)) : out).slice(-SPARK);
  }

  function drawSpark(svg, pts, sel) {
    const w = Math.max(60, Math.round(svg.clientWidth || 160)), h = 44, px = 7, py = 8;
    const ys = pts.map(p => p.y), lo = Math.min(...ys), hi = Math.max(...ys);
    const X = i => (pts.length === 1 ? w - px : px + i * (w - 2 * px) / (pts.length - 1));
    const Y = y => (hi === lo ? h / 2 : h - py - (y - lo) * (h - 2 * py) / (hi - lo));
    const i = sel == null ? pts.length - 1 : sel;
    const path = pts.map((p, k) => `${k ? 'L' : 'M'}${X(k).toFixed(1)} ${Y(p.y).toFixed(1)}`).join('');
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    svg.innerHTML = `<line class="spark-base" x1="0" x2="${w}" y1="${h - 0.5}" y2="${h - 0.5}"/>` +
      (sel == null ? '' : `<line class="spark-cross" x1="${X(i).toFixed(1)}" x2="${X(i).toFixed(1)}" y1="0" y2="${h}"/>`) +
      (pts.length > 1 ? `<path class="spark-line" d="${path}"/>` : '') +
      `<circle class="spark-dot" cx="${X(i).toFixed(1)}" cy="${Y(pts[i].y).toFixed(1)}" r="4"/>`;
    return { w, px };
  }

  function readout(el, pts, sel) {
    if (sel == null) {
      const a = pts[0], b = pts[pts.length - 1];
      el.textContent = pts.length > 1 ? `${dShort(a.date)} bis ${dShort(b.date)} · ${pts.length} Einheiten` : `${dShort(b.date)} · 1 Einheit`;
      return;
    }
    el.innerHTML = '<b></b><span></span>';
    el.firstChild.textContent = sumOf(pts[sel].it);
    el.lastChild.textContent = ` · ${dLong(pts[sel].date)}`;
  }

  function renderTiles() {
    const box = $('tiles');
    const data = DB.exercises.map(ex => ({ ex, pts: seriesOf(ex) })).filter(d => d.pts.length);
    $('tiles-empty').hidden = data.length > 0;
    box.hidden = !data.length;
    box.innerHTML = data.map(({ ex, pts }) => {
      const last = pts[pts.length - 1], first = pts[0];
      const [val, unit] = metricParts(last.it, last.y);
      const diff = round2(last.y - first.y);
      const delta = pts.length < 2 ? '' : diff === 0 ? `unverändert seit ${dShort(first.date)}` : `${deltaText(last.it, diff)} seit ${dShort(first.date)}`;
      const label = `${ex.name}: ${pts.length === 1 ? '1 Einheit' : `${pts.length} Einheiten`}, zuletzt ${sumOf(last.it)} am ${dLong(last.date)}.` +
        (pts.length > 1 ? ' Pfeiltasten zeigen die einzelnen Einheiten.' : '');
      return `<figure class="tile" data-id="${esc(ex.id)}">
        <figcaption class="label">${esc(ex.name)}</figcaption>
        <p class="tile-val">${esc(val)}<small>${unit}</small></p>
        <p class="tile-sub">${esc(setsText(last.it))}${delta ? `<br>${esc(delta)}` : ''}</p>
        <svg class="spark" role="img" tabindex="0" aria-label="${esc(label)}"></svg>
        <p class="tile-read"></p>
      </figure>`;
    }).join('');

    data.forEach(({ pts }, n) => {
      const tile = box.children[n], svg = tile.querySelector('.spark'), read = tile.querySelector('.tile-read');
      let sel = null, geo = drawSpark(svg, pts, null);
      const show = i => { sel = i; geo = drawSpark(svg, pts, sel); readout(read, pts, sel); };
      const pick = ev => {
        const r = svg.getBoundingClientRect();
        const x = (ev.clientX - r.left) * geo.w / (r.width || geo.w);
        show(pts.length === 1 ? 0 : clamp(Math.round((x - geo.px) / ((geo.w - 2 * geo.px) / (pts.length - 1))), 0, pts.length - 1));
      };
      readout(read, pts, null);
      svg.redraw = () => { geo = drawSpark(svg, pts, sel); };
      svg.addEventListener('pointermove', ev => { if (ev.pointerType === 'mouse') pick(ev); });
      svg.addEventListener('pointerdown', ev => { pick(ev); svg.focus({ preventScroll: true }); });
      svg.addEventListener('pointerleave', ev => { if (ev.pointerType === 'mouse' && document.activeElement !== svg) show(null); });
      svg.addEventListener('focus', () => { if (sel == null) show(pts.length - 1); });
      svg.addEventListener('blur', () => show(null));
      svg.addEventListener('keydown', ev => {
        const cur = sel == null ? pts.length - 1 : sel;
        const next = { ArrowLeft: cur - 1, ArrowRight: cur + 1, Home: 0, End: pts.length - 1 }[ev.key];
        if (next == null) return;
        ev.preventDefault();
        show(clamp(next, 0, pts.length - 1));
      });
    });
  }

  // ---------- Anzeige: Einheiten ----------
  function renderSessions() {
    const all = DB.sessions.slice().reverse();
    const shown = showAll ? all : all.slice(0, SHOWN);
    $('sessions').innerHTML = shown.map(s => `<li class="sess" data-date="${s.date}">
      <b class="sess-head">${dLong(s.date)}</b>
      <p class="sess-lines">${esc(noteOf(s))}</p>
      <div class="sess-btns">
        <button type="button" class="chip sm" data-act="copy-s">Kopieren</button>
        <button type="button" class="chip sm" data-act="edit-s">Bearbeiten</button>
        <button type="button" class="chip sm" data-act="del-s">Löschen</button>
      </div>
    </li>`).join('');
    $('sessions-empty').hidden = all.length > 0;
    const more = $('more');
    more.hidden = all.length <= SHOWN;
    more.textContent = showAll ? 'Weniger anzeigen' : `Alle ${all.length} anzeigen`;
  }

  // ---------- Anzeige: Übungen ----------
  function renderManage() {
    $('manage-list').innerHTML = DB.exercises.map(ex => `<li data-id="${esc(ex.id)}">
      <input type="text" class="m-name" value="${esc(ex.name)}" maxlength="40" autocomplete="off" aria-label="Name der Übung">
      <select class="m-type" aria-label="Art von ${esc(ex.name)}">${Object.keys(TYPES).map(k => `<option value="${k}"${k === ex.type ? ' selected' : ''}>${TYPES[k]}</option>`).join('')}</select>
      <button type="button" class="chip sm" data-act="del-ex">Entfernen</button>
    </li>`).join('');
  }

  function renderAll() {
    renderEditor();
    renderTiles();
    renderSessions();
    renderManage();
  }

  // ---------- Bedienung ----------
  function changed() {
    E.dirty = true;   // ungespeicherte Eingaben überleben einen Datumswechsel
    clearStatus();
    save();
    renderEditor();
  }
  function uid(name) {
    let base = norm(name);
    for (const [a, b] of [['ä', 'ae'], ['ö', 'oe'], ['ü', 'ue'], ['ß', 'ss']]) base = base.split(a).join(b);
    base = base.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'uebung';
    let id = base, n = 2;
    while (DB.exercises.some(x => x.id === id)) id = `${base}-${n++}`;
    return id;
  }
  function addExercise(name, type) {
    const ex = { id: uid(name), name: name.trim().slice(0, 40), type: TYPES[type] ? type : 'kg' };
    DB.exercises.push(ex);
    if (E) E.items[ex.id] = blank(ex);
    return ex;
  }

  async function doSave() {
    const s = sessionFromEditor();
    const fresh = !DB.sessions.some(x => x.date === s.date);
    upsert(s);
    E.dirty = false;
    save();
    renderAll();
    const text = noteOf(s);
    const ok = await copy(text);
    const fb = $('copy-fallback');
    fb.value = text;
    fb.hidden = ok;
    status($('save-status'), ok ? 'ok' : 'warn', ok
      ? `${fresh ? 'Gespeichert' : 'Aktualisiert'} und kopiert. In intervals.icu bei der Einheit als Notiz einfügen.`
      : 'Gespeichert. Kopieren hat der Browser nicht erlaubt: den Text unten markieren und von Hand kopieren.');
  }

  // Einheiten aus Text übernehmen; unbekannte Übungen werden angelegt
  function doImport() {
    const parsed = parseImport($('import-text').value);
    const out = $('data-status');
    if (!parsed.length) {
      status(out, 'warn', 'Keine Einheit erkannt. Jede Einheit braucht eine Zeile mit dem Datum und darunter mindestens eine Übung, etwa „Squat 55 3x10“.');
      return;
    }
    let added = 0, replaced = 0;
    for (const p of parsed) {
      const items = p.items.map(e => {
        const ex = DB.exercises.find(x => norm(x.name) === norm(e.name)) || addExercise(e.name, e.type || 'kg');
        return cleanEntry({ ...e, id: ex.id, name: ex.name, type: e.skip ? ex.type : e.type });
      }).filter(Boolean);
      const s = cleanSession({ date: p.date, items, note: p.note });
      if (!s) continue;
      if (DB.sessions.some(x => x.date === s.date)) replaced += 1; else added += 1;
      upsert(s);
    }
    E = editorFor(E.date);
    save();
    renderAll();
    $('import-text').value = '';
    const n = added + replaced;
    status(out, 'ok', `${n === 1 ? '1 Einheit' : `${n} Einheiten`} übernommen${replaced ? `, davon ${replaced} ersetzt` : ''}.`);
  }

  async function doExport() {
    const out = $('data-status');
    if (!DB.sessions.length) { status(out, 'info', 'Noch keine Einheit gespeichert.'); return; }
    const text = DB.sessions.map(s => `${s.date}\n${noteOf(s)}`).join('\n\n');
    if (await copy(text)) {
      status(out, 'ok', `${DB.sessions.length === 1 ? '1 Einheit' : `${DB.sessions.length} Einheiten`} kopiert.`);
    } else {
      $('import-text').value = text;
      status(out, 'warn', 'Kopieren hat der Browser nicht erlaubt. Der Text steht im Feld unten.');
    }
  }

  document.addEventListener('click', ev => {
    const b = ev.target.closest('[data-act]');
    if (!b || b.disabled) return;
    const li = b.closest('.ex');
    const ex = li && DB.exercises.find(x => x.id === li.dataset.id);
    const v = ex && E.items[ex.id];
    const d = parseFloat(b.dataset.d);
    const sess = b.closest('.sess');
    const date = sess && sess.dataset.date;
    switch (b.dataset.act) {
      case 'open': open = open === ex.id ? null : ex.id; renderEditor(); return;
      case 'kg': v.kg = clamp(round2(v.kg + d * ((d > 0 ? v.kg >= 20 : v.kg > 20) ? 2.5 : 1)), 0, 500); break;
      case 'sets': {
        const list = listOf(ex, v);
        if (d > 0 && list.length < MAX_SETS) list.push(list[list.length - 1]);
        if (d < 0 && list.length > 1) list.pop();
        break;
      }
      case 'per': {
        const list = listOf(ex, v), timed = ex.type === 'time';
        list.fill(clamp(list[0] + d, timed ? 5 : 1, timed ? 3600 : 999));
        break;
      }
      case 'split': {
        v.split = !v.split;
        if (!v.split) { const list = listOf(ex, v); list.fill(list[0]); }
        break;
      }
      case 'skip': v.skip = !v.skip; break;
      case 'save': doSave(); return;
      case 'copy-s': {
        const s = DB.sessions.find(x => x.date === date);
        if (s) copy(noteOf(s)).then(ok => {
          b.textContent = ok ? 'Kopiert' : 'Nicht erlaubt';
          setTimeout(() => { b.textContent = 'Kopieren'; }, 1600);
        });
        return;
      }
      case 'edit-s': {
        E = editorFor(date);
        open = null;
        clearStatus();
        save();
        renderEditor();
        const calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        $('t-unit').scrollIntoView({ block: 'start', behavior: calm ? 'auto' : 'smooth' });
        return;
      }
      case 'del-s':
        if (!window.confirm(`Einheit vom ${dLong(date)} löschen?`)) return;
        DB.sessions = DB.sessions.filter(x => x.date !== date);
        save();
        renderAll();
        return;
      case 'more': showAll = !showAll; renderSessions(); return;
      case 'add-ex': {
        const name = $('new-name').value.trim();
        if (!name) { $('new-name').focus(); return; }
        if (DB.exercises.some(x => norm(x.name) === norm(name))) { $('new-name').select(); return; }
        open = addExercise(name, $('new-type').value).id;
        $('new-name').value = '';
        save();
        renderAll();
        return;
      }
      case 'del-ex': {
        const row = b.closest('li'), id = row && row.dataset.id;
        const gone = DB.exercises.find(x => x.id === id);
        if (!gone || !window.confirm(`„${gone.name}“ aus der Liste entfernen? Gespeicherte Einheiten bleiben unverändert.`)) return;
        DB.exercises = DB.exercises.filter(x => x.id !== id);
        delete E.items[id];
        if (open === id) open = null;
        save();
        renderAll();
        return;
      }
      case 'export': doExport(); return;
      case 'import': doImport(); return;
      default: return;
    }
    changed();
  });

  // Zahlen direkt eintippen: sofort mitrechnen, das Feld erst beim Verlassen glätten
  document.addEventListener('input', ev => {
    const el = ev.target;
    if (el.id === 'note') { E.note = el.value; E.dirty = true; clearStatus(); save(); return; }
    const li = el.closest('.ex');
    if (!li || !el.dataset.f) return;
    const ex = DB.exercises.find(x => x.id === li.dataset.id), v = E.items[ex.id], x = toNum(el.value);
    if (el.dataset.f === 'kg') {
      v.kg = clamp(isFinite(x) ? round2(x) : 0, 0, 500);
    } else {
      const list = listOf(ex, v), val = clamp(Math.round(isFinite(x) ? x : 0), 1, ex.type === 'time' ? 3600 : 999);
      if (el.dataset.f === 'per') list.fill(val); else list[+el.dataset.i] = val;
    }
    changed();
  });
  const isField = el => el.classList && el.classList.contains('ct-in');
  document.addEventListener('focusin', ev => { if (isField(ev.target)) ev.target.select(); });
  document.addEventListener('focusout', ev => { if (isField(ev.target)) setTimeout(renderEditor, 0); });
  document.addEventListener('keydown', ev => { if (ev.key === 'Enter' && isField(ev.target)) ev.target.blur(); });

  document.addEventListener('change', ev => {
    const el = ev.target;
    if (el.id === 'date') {
      const date = isDate(el.value) ? el.value : today();
      // gespeicherte Einheit laden; eigene, noch ungespeicherte Eingaben wandern mit auf den neuen Tag
      if (DB.sessions.some(s => s.date === date) || !E.dirty) E = editorFor(date); else E.date = date;
      open = null;
      clearStatus();
      save();
      renderEditor();
      return;
    }
    const row = el.closest('#manage-list li');
    const ex = row && DB.exercises.find(x => x.id === row.dataset.id);
    if (!ex) return;
    if (el.classList.contains('m-name')) {
      const name = el.value.trim().slice(0, 40);
      if (name && !DB.exercises.some(x => x !== ex && norm(x.name) === norm(name))) {
        ex.name = name;   // gilt auch rückwirkend, damit Verlauf und Notizen denselben Namen tragen
        DB.sessions.forEach(s => s.items.forEach(it => { if (it.id === ex.id) it.name = name; }));
      }
    } else if (el.classList.contains('m-type') && TYPES[el.value]) {
      ex.type = el.value;
      const v = E.items[ex.id], list = listOf(ex, v);
      v.split = list.some(x => x !== list[0]);
    } else {
      return;
    }
    save();
    renderAll();
  });

  let raf = 0;
  window.addEventListener('resize', () => {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => document.querySelectorAll('.spark').forEach(s => s.redraw && s.redraw()));
  });

  let open = null, showAll = false;
  const DB = load();
  let E = restore(DB.draft);
  delete DB.draft;
  renderAll();
  window.KraftLog = { get db() { return DB; }, get editor() { return E; }, parseImport, noteOf };
})();
