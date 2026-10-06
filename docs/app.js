(() => {
  'use strict';

  const KEY = 'fueling-rechner.v2';

  const WEATHER = {
    cool: { name: 'Kühl', adj: 'kühles', hint: 'unter 15 °C', ml: 500 },
    mild: { name: 'Mild', adj: 'mildes', hint: '15 bis 25 °C', ml: 650 },
    hot: { name: 'Heiß', adj: 'heißes', hint: 'über 25 °C', ml: 850 }
  };
  const RATES = [[50, 'Locker'], [70, 'Mittel'], [90, 'Key · Lang'], [100, 'Rennen']];
  const DURATIONS = [90, 120, 180, 240, 300, 360];
  const INTERVALS = [15, 20, 30];
  const BOTTLE_SIZES = [500, 750, 1000];
  const FLASK_SIZES = [150, 300];
  const MAX_BOTTLES = 3, MAX_FLASKS = 3, MAX_REFILLS = 8;

  const NA_MG_PER_G_SALT = 393.4;   // mg Natrium in 1 g Kochsalz
  const CITRATE_PER_SALT = 1.678;   // g Trinatriumcitrat-Dihydrat mit dem Natrium von 1 g Kochsalz
  const CARB_ML_PER_G = 0.62;       // ml, die 1 g gelöste Kohlenhydrate einnimmt
  const WARN_MAX = 0.2;             // g/ml über alles: darüber zu konzentriert
  const ADJ_STEP = 10;
  const NEAR = 7.5;                 // so viele Gramm Abweichung gelten noch als Ziel erreicht

  const DEF = {
    durationMin: 180, rate: 90, weather: 'mild', interval: 20, power: null,
    flasks: 'auto',   // 'auto' oder feste Zahl
    refills: 'auto',  // 'auto' oder feste Zahl
    manual: null,     // null = Vorschlag der Automatik, sonst Gramm je Behälter: { f0: 180, b0: 90, ... }
    kit: { bottles: 2, flaskCount: 1, bottleSizes: [750, 750, 750], flaskSizes: [300, 300, 300], refillSizes: [] },
    mix: { fru: 0.8, salt: 1, saltType: 'nacl', de: 15 },
    limits: { flask: 0.6, bottleSolo: 0.15, bottleMax: 0.2, okMax: 0.15 }
  };

  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const r5 = x => Math.round(x / 5) * 5;
  const r10 = x => Math.round(x / 10) * 10;
  const floor5 = x => Math.floor(x / 5 + 1e-9) * 5;
  const num = (x, d) => (typeof x === 'number' && isFinite(x) ? x : d);
  const nearest = (list, x) => list.reduce((a, b) => (Math.abs(b - x) < Math.abs(a - x) ? b : a));

  const bSize = (K, i) => K.bottleSizes[i] || 750;
  const fSize = (K, i) => K.flaskSizes[i] || 300;
  const rSize = (K, i) => K.refillSizes[i] || bSize(K, 0);
  // Höchstmenge je Behälter: Flask als Konzentrat, Flasche bis 0,25 g/ml
  const limOf = (kind, ml, L) => (kind === 'flask' ? floor5(L.flask * ml) : r5(ml * 0.25));
  const kindOf = id => ({ f: 'flask', b: 'bottle', r: 'refill' }[id[0]]);

  function sanitize(s) {
    s.durationMin = clamp(Math.round(num(s.durationMin, 180) / 15) * 15, 30, 720);
    s.rate = clamp(r5(num(s.rate, 90)), 20, 130);
    if (!WEATHER[s.weather]) s.weather = 'mild';
    if (!INTERVALS.includes(s.interval)) s.interval = 20;
    s.power = s.power ? clamp(Math.round(num(+s.power, 0)), 0, 600) || null : null;

    const k = s.kit, m = s.mix, l = s.limits;
    k.bottles = clamp(Math.round(num(+k.bottles, 2)), 1, MAX_BOTTLES);
    k.flaskCount = clamp(Math.round(num(+k.flaskCount, 1)), 0, MAX_FLASKS);
    const sizes = (arr, n, list, dflt) => Array.from({ length: n }, (_, i) =>
      (Array.isArray(arr) && arr[i] != null ? nearest(list, num(+arr[i], dflt || list[0])) : dflt));
    k.bottleSizes = sizes(k.bottleSizes, MAX_BOTTLES, BOTTLE_SIZES, 750);
    k.flaskSizes = sizes(k.flaskSizes, MAX_FLASKS, FLASK_SIZES, 300);
    k.refillSizes = sizes(k.refillSizes, MAX_REFILLS, BOTTLE_SIZES, null);

    m.fru = clamp(num(+m.fru, 0.8), 0, 1.25);
    m.salt = clamp(Math.round(num(+m.salt, 1) * 2) / 2, 0, 3);
    if (m.saltType !== 'citrate') m.saltType = 'nacl';
    m.de = [6, 12, 15, 19].includes(+m.de) ? +m.de : 15;
    l.flask = clamp(num(+l.flask, 0.6), 0.3, 0.7);
    l.bottleSolo = clamp(num(+l.bottleSolo, 0.15), 0.06, 0.2);
    l.bottleMax = clamp(num(+l.bottleMax, 0.2), Math.max(0.1, l.bottleSolo), 0.3);
    l.okMax = clamp(num(+l.okMax, 0.15), 0.06, 0.2);

    if (s.manual && typeof s.manual === 'object') {
      const clean = {};
      for (const [id, g] of Object.entries(s.manual)) {
        if (/^[fbr]\d$/.test(id)) clean[id] = clamp(Math.round(num(+g, 0)), 0, 400);
      }
      s.manual = clean;
    } else {
      s.manual = null;
    }
    // beim Selbstfüllen sind die Anzahlen immer feste Zahlen
    const count = (v, max, prefix) => {
      if (v === 'auto') return s.manual ? Object.keys(s.manual).filter(id => id[0] === prefix).length : 'auto';
      return clamp(Math.round(num(+v, 0)), 0, max);
    };
    s.flasks = count(s.flasks, MAX_FLASKS, 'f');
    s.refills = count(s.refills, MAX_REFILLS, 'r');
    return s;
  }

  function load() {
    let s = {};
    try { s = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { s = {}; }
    return sanitize({
      ...DEF, ...s,
      kit: { ...DEF.kit, ...(s.kit || {}) },
      mix: { ...DEF.mix, ...(s.mix || {}) },
      limits: { ...DEF.limits, ...(s.limits || {}) }
    });
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* privater Modus: ohne Speichern weiter */ }
  }

  // Osmolalität in mOsm je kg Wasser, ideal gerechnet (Salz zerfällt vollständig)
  function osmolality(carbs, saltEq, ml, mix) {
    const waterKg = (ml - carbs * CARB_ML_PER_G) / 1000;
    if (!(waterKg > 0) || (!carbs && !saltEq)) return 0;
    const malto = carbs / (1 + mix.fru);
    const fru = carbs - malto;
    let mmol = fru / 180.16 * 1000 + malto / (18000 / mix.de) * 1000;
    mmol += mix.saltType === 'citrate'
      ? saltEq * CITRATE_PER_SALT / 294.1 * 1000 * 4
      : saltEq / 58.44 * 1000 * 2;
    return mmol / waterKg;
  }

  // Vorschlag der Automatik: erst Flask, der Rest nach Volumen auf Flaschen und Nachfüllungen
  function suggest(S, hours, target, weather) {
    const K = S.kit, L = S.limits;
    const sum = a => a.reduce((x, y) => x + y, 0);

    const build = nFl => {
      const caps = Array.from({ length: nFl }, (_, i) => limOf('flask', fSize(K, i), L));
      const capSum = sum(caps);
      const share = capSum ? Math.min(1, target / capSum) : 0;
      const flaskG = caps.map(c => Math.min(c, r5(c * share)));
      let rest = target - sum(flaskG);
      if (rest < 2.5) rest = 0;

      const carried = sum(flaskG.map(g => g / L.flask)) + sum(Array.from({ length: K.bottles }, (_, i) => bSize(K, i)));
      let refills = S.refills;
      if (refills === 'auto') {
        // so viele Nachfüllungen, bis Wetter-Richtwert (gerundet) und Zielkonzentration erreicht sind
        refills = 0;
        let vol = carried;
        while (refills < MAX_REFILLS) {
          const next = rSize(K, refills);
          const forWeather = hours * weather.ml - vol >= next / 2;
          const forConc = target / L.okMax - vol > next * 0.05;
          if (!forWeather && !forConc) break;
          vol += next;
          refills += 1;
        }
      }

      let water = nFl > 0 && K.bottles >= 2 ? 1 : 0;   // eine Flasche bleibt Wasser, wenn eine Flask dabei ist
      const slotsFor = w => {
        const a = [];
        for (let i = 0; i < K.bottles - w; i++) a.push({ id: 'b' + i, ml: bSize(K, i), start: true });
        for (let i = 0; i < refills; i++) a.push({ id: 'r' + i, ml: rSize(K, i), start: false });
        return a;
      };
      const volOf = (slots, k) => sum(slots.slice(0, k).map(s => s.ml));
      const pick = slots => {                           // so wenige Flaschen wie nötig, je bis zur Grenze „allein“
        for (let k = 1; k <= slots.length; k++) if (rest <= volOf(slots, k) * L.bottleSolo * 1.02) return k;
        return slots.length;
      };

      let slots = slotsFor(water);
      let k = rest ? pick(slots) : 0;
      // lieber die Wasserflasche opfern als überkonzentrieren
      if (rest && water && rest / volOf(slots, k) > L.bottleMax * 1.005) {
        water = 0;
        slots = slotsFor(0);
        k = pick(slots);
      }

      const vol = k ? volOf(slots, k) : 0;
      const carbs = {};
      flaskG.forEach((g, i) => { carbs['f' + i] = g; });
      slots.slice(0, k).forEach(s => {
        const x = rest * s.ml / vol;
        const solo = L.bottleSolo * s.ml;
        const v = r5(x);
        carbs[s.id] = v > solo + 0.01 && x <= solo * 1.02 ? floor5(solo) : v;   // nicht knapp über die Grenze runden
      });
      return {
        nFl, refills, water, carbs,
        conc: vol ? rest / vol : 0,
        powder: slots.slice(0, k).filter(s => !s.start).length
      };
    };

    if (S.flasks !== 'auto') return build(S.flasks);
    const soloStart = sum(Array.from({ length: K.bottles }, (_, i) => bSize(K, i))) * L.bottleSolo;
    let n = K.flaskCount > 0 && target > soloStart * 1.02 ? 1 : 0;
    let p = build(n);
    // weitere Flask nur, wenn sie überkonzentrierte Flaschen oder mehrfaches Anmischen erspart
    while (n > 0 && n < K.flaskCount && (p.conc > L.bottleSolo * 1.02 || p.powder >= 2)) {
      n += 1;
      p = build(n);
    }
    return p;
  }

  function compute(S) {
    const K = S.kit, L = S.limits, M = S.mix;
    const hours = S.durationMin / 60;
    const target = S.rate * hours;
    const warnMax = Math.max(WARN_MAX, L.okMax + 0.03);
    const weather = WEATHER[S.weather];
    const manual = !!S.manual;

    let nFl, refills, gramsOf;
    if (manual) {
      nFl = S.flasks;
      refills = S.refills;
      gramsOf = id => S.manual[id] || 0;
    } else {
      const p = suggest(S, hours, target, weather);
      nFl = p.nFl;
      refills = p.refills;
      gramsOf = id => p.carbs[id] || 0;
    }

    const cs = [];
    for (let i = 0; i < nFl; i++) cs.push({ id: 'f' + i, kind: 'flask', name: nFl > 1 ? `Flask ${i + 1}` : 'Flask', cap: fSize(K, i) });
    for (let i = 0; i < K.bottles; i++) cs.push({ id: 'b' + i, kind: 'bottle', name: `Flasche ${i + 1}`, cap: bSize(K, i) });
    for (let i = 0; i < refills; i++) cs.push({ id: 'r' + i, kind: 'refill', name: `Nachfüllen ${i + 1}`, cap: rSize(K, i) });

    for (const c of cs) {
      c.lim = limOf(c.kind, c.cap, L);
      c.carbs = clamp(Math.round(gramsOf(c.id)), 0, c.lim);
      c.malto = Math.round(c.carbs / (1 + M.fru));
      c.fru = c.carbs - c.malto;
      c.saltEq = c.carbs / 90 * M.salt;
      c.ml = c.kind === 'flask' ? Math.min(c.cap, r10(c.carbs / L.flask)) : c.cap;
      c.conc = c.ml ? c.carbs / c.ml : 0;
      c.water = Math.max(0, r10(c.ml - c.carbs * CARB_ML_PER_G));
      c.osmo = osmolality(c.carbs, c.saltEq, c.ml, M);
    }

    const sum = f => cs.reduce((a, c) => a + f(c), 0);
    const planned = sum(c => c.carbs);                  // eingepackt
    const fluid = sum(c => c.ml);                       // alles, was dabei ist oder nachgefüllt wird
    const carbVol = sum(c => (c.carbs > 0 ? c.ml : 0)); // muss getrunken werden, sonst fehlen Kohlenhydrate
    const saltEq = sum(c => c.saltEq);
    // sinnvolle Trinkmenge: Wetter-Richtwert oder was die Kohlenhydrate brauchen, höchstens was da ist
    const drinkMl = Math.max(carbVol, Math.min(fluid, Math.max(weather.ml * hours, planned / L.okMax)));
    const conc = fluid ? planned / fluid : 0;           // wenn alles getrunken wird
    const state = planned <= 0 ? 'empty' : conc <= L.okMax * 1.03 ? 'ok' : conc <= warnMax * 1.03 ? 'warn' : 'bad';
    const extraMl = Math.max(0, Math.ceil((planned / L.okMax - fluid) / 50) * 50);
    const fluidPerHour = fluid / hours;
    const flaskCarbs = sum(c => (c.kind === 'flask' ? c.carbs : 0));
    const refillPowder = cs.filter(c => c.kind === 'refill' && c.carbs > 0).length;

    const hints = [];
    if (!manual && planned < target - NEAR) {
      hints.push(['bad', `In diese Aufteilung passen nur ${n0(planned)} g statt ${n0(target)} g. Plane mehr Nachfüllungen, größere Flaschen oder eine Flask ein.`]);
    }
    const tooStrong = cs.filter(c => c.kind !== 'flask' && c.conc > L.bottleMax * 1.02).map(c => c.name);
    if (tooStrong.length) {
      hints.push(['bad', `${tooStrong.join(' und ')} ${tooStrong.length > 1 ? 'sind' : 'ist'} zu konzentriert. Auf mehr Flaschen verteilen, öfter nachfüllen oder eine Flask dazunehmen.`]);
    }
    if (fluidPerHour < weather.ml * 0.8) {
      hints.push(['warn', `Wenig Flüssigkeit für ${weather.adj} Wetter: ${n0(r10(fluidPerHour))} ml pro Stunde, Richtwert ${weather.ml}. Plane eine Nachfüllung mehr ein.`]);
    }
    if (refillPowder) {
      hints.push(['info', refillPowder > 1
        ? `Pulver für ${refillPowder} Nachfüllungen abgewogen in Beuteln mitnehmen.`
        : 'Pulver für die Nachfüllung abgewogen im Beutel mitnehmen.']);
    }
    if (S.rate > 90) hints.push(['info', 'Mehr als 90 g pro Stunde vorher im Training testen.']);

    // Eine Portion je Takt, ausgedrückt in Millilitern der jeweiligen Quelle
    const dose = S.rate * S.interval / 60;
    const seen = new Set();
    const portions = [];
    for (const c of cs) {
      if (!c.carbs) continue;
      const key = (c.kind === 'flask' ? 'f' : 'b' + c.cap + ':') + c.carbs;
      if (c.kind === 'flask' ? seen.has('f') : seen.has(key)) continue;
      seen.add(c.kind === 'flask' ? 'f' : key);
      portions.push({ flask: c.kind === 'flask', carbs: c.carbs, cap: c.cap, ml: dose / c.conc });
    }

    return {
      hours, target, cs, planned, fluid, drinkMl, saltEq, conc, state, extraMl, fluidPerHour, warnMax, manual,
      nFl, refills, hints, dose, portions, flaskCarbs,
      drinkPerHour: drinkMl / hours,
      sodiumPerHour: saltEq * NA_MG_PER_G_SALT / hours,
      kcal: planned * 4,
      osmoAll: osmolality(planned, saltEq, fluid, M)
    };
  }

  // ---------- Darstellung ----------
  const $ = id => document.getElementById(id);
  const fmt0 = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 });
  const fmt1 = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const fmt2 = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const n0 = x => fmt0.format(x);
  const n1 = x => fmt1.format(x);
  const n2 = x => fmt2.format(x);
  const nSalt = x => (Math.abs(x - Math.round(x)) < 0.05 ? n0(x) : n1(x));
  const hm = min => { const t = Math.round(min); return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`; };
  const ico = name => `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
  const chip = (act, v, label, extra = '') =>
    `<button type="button" class="chip" data-act="${act}" data-v="${v}"${extra} aria-pressed="false">${label}</button>`;
  const press = (root, val) => root.querySelectorAll('.chip').forEach(b =>
    b.setAttribute('aria-pressed', String(b.dataset.v === String(val))));

  function saltText(saltEq, mix) {
    if (saltEq < 0.05) return '';
    return mix.saltType === 'citrate'
      ? `${nSalt(saltEq * CITRATE_PER_SALT)} g Natriumcitrat`
      : `${nSalt(saltEq)} g Salz`;
  }
  function recipe(malto, fru, saltEq, mix) {
    const parts = [`${n0(malto)} g Maltodextrin`];
    if (fru > 0) parts.push(`${n0(fru)} g Fruktose`);
    const s = saltText(saltEq, mix);
    if (s) parts.push(s);
    return parts.map(t => `<span class="nb">${t}</span>`).join(' + ');
  }
  function fraction(x) {
    const list = [[1, 'die ganze Flasche'], [3 / 4, '¾ der Flasche'], [2 / 3, '⅔ der Flasche'], [1 / 2, 'die halbe Flasche'],
      [1 / 3, 'ein Drittel der Flasche'], [1 / 4, 'ein Viertel der Flasche'], [1 / 5, 'ein Fünftel der Flasche'], [1 / 6, 'ein Sechstel der Flasche']];
    for (const [v, t] of list) if (Math.abs(x - v) / v <= 0.08) return t;
    return '';
  }

  // Zeilen der Packliste: Gerüst nur neu bauen, wenn sich die Behälter ändern.
  // Sonst an Ort und Stelle auffrischen, damit Eingabefelder und Tasten erhalten bleiben.
  function rowTemplate(c) {
    const sizes = c.kind === 'flask' ? FLASK_SIZES : BOTTLE_SIZES;
    const icon = c.kind === 'flask' ? 'flask' : c.kind === 'refill' ? 'refill' : 'bottle';
    return `<li class="ct" data-id="${c.id}">
      <span class="ct-ico">${ico(icon)}</span>
      <div class="ct-top">
        <span class="ct-name"></span>
        <span class="ct-amt">
          <button type="button" class="mini" data-act="adj" data-id="${c.id}" data-d="-${ADJ_STEP}">−</button>
          <label class="ct-g"><input class="ct-in" type="number" inputmode="numeric" min="0" step="5" data-id="${c.id}"><small>g</small></label>
          <button type="button" class="mini" data-act="adj" data-id="${c.id}" data-d="${ADJ_STEP}">+</button>
        </span>
      </div>
      <div class="ct-body">
        <div class="chips seg tight sizes" role="group">${sizes.map(v => chip('size', v, `${v} ml`, ` data-id="${c.id}"`)).join('')}</div>
        <p class="ct-rec"></p>
        <p class="ct-meta"></p>
        <p class="tag" hidden></p>
      </div>
    </li>`;
  }
  function syncRow(li, c) {
    const L = S.limits;
    const q = sel => li.querySelector(sel);
    const carb = c.carbs > 0;
    q('.ct-ico').className = `ct-ico ${carb ? 'carb' : 'water'}`;
    q('.ct-name').textContent = c.name;
    const [minus, plus] = li.querySelectorAll('[data-act="adj"]');
    minus.disabled = c.carbs <= 0;
    plus.disabled = c.carbs >= c.lim;
    minus.setAttribute('aria-label', `${c.name}: ${ADJ_STEP} Gramm weniger`);
    plus.setAttribute('aria-label', `${c.name}: ${ADJ_STEP} Gramm mehr`);
    const inp = q('.ct-in');
    inp.max = c.lim;
    inp.setAttribute('aria-label', `${c.name}: Gramm Kohlenhydrate`);
    if (inp !== document.activeElement) inp.value = c.carbs;
    q('.sizes').setAttribute('aria-label', `Größe ${c.name}`);
    press(q('.sizes'), c.cap);

    let meta, tag = '', bad = false;
    if (carb) {
      if (c.kind === 'flask') meta = `Mit etwa ${n0(c.water)} ml Wasser auf ${n0(c.ml)} ml auffüllen · ${n2(c.conc)} g/ml`;
      else if (c.kind === 'refill') meta = `Pulver im Beutel, unterwegs mit ${n0(c.cap)} ml Wasser mischen · ${n2(c.conc)} g/ml`;
      else meta = `Mit Wasser auf ${n0(c.cap)} ml auffüllen · ${n2(c.conc)} g/ml`;
      if (c.kind !== 'flask' && c.conc > L.bottleMax * 1.02) { tag = 'Zu konzentriert'; bad = true; }
      else if (c.kind !== 'flask' && c.conc > L.bottleSolo * 1.02) tag = 'Konzentriert: nur mit Wasser daneben trinken';
    } else if (c.kind === 'flask') {
      meta = 'Bleibt leer';
    } else if (c.kind === 'refill') {
      meta = `Unterwegs ${n0(c.cap)} ml Wasser nachfüllen`;
    } else {
      meta = `${n0(c.cap)} ml Wasser`;
    }
    const rec = q('.ct-rec');
    rec.hidden = !carb;
    rec.innerHTML = carb ? recipe(c.malto, c.fru, c.saltEq, S.mix) : '';
    q('.ct-meta').textContent = meta;
    const t = q('.tag');
    t.hidden = !tag;
    t.className = `tag${bad ? ' bad' : ''}`;
    t.innerHTML = tag ? `${ico(bad ? 'bad' : 'warn')}${tag}` : '';
  }
  function renderRows(cs) {
    const ul = $('containers');
    const sig = cs.map(c => c.id).join(',');
    if (ul.dataset.sig !== sig) {
      ul.innerHTML = cs.map(rowTemplate).join('');
      ul.dataset.sig = sig;
    }
    cs.forEach((c, i) => syncRow(ul.children[i], c));
  }

  function buildStatic() {
    $('dur-chips').innerHTML = DURATIONS.map(d => chip('set-dur', d, hm(d))).join('');
    $('rate-chips').innerHTML = RATES.map(([v, n]) => chip('set-rate', v, `<span>${n}</span><small>${v} g/h</small>`)).join('');
    $('weather-chips').innerHTML = Object.entries(WEATHER).map(([k, w]) => chip('weather', k, w.name)).join('');
    $('int-chips').innerHTML = INTERVALS.map(i => chip('interval', i, `${i} min`)).join('');
  }

  let R = null;

  function render() {
    R = compute(S);
    const L = S.limits, M = S.mix;

    // Fahrt
    $('dur').innerHTML = `${hm(S.durationMin)}<small>h</small>`;
    press($('dur-chips'), S.durationMin);
    $('rate').innerHTML = `${n0(S.rate)}<small>g/h</small>`;
    press($('rate-chips'), S.rate);
    press($('weather-chips'), S.weather);
    $('weather-note').textContent = `${WEATHER[S.weather].hint}: Richtwert ${WEATHER[S.weather].ml} ml Flüssigkeit pro Stunde.`;

    // Bedarf
    $('total').textContent = n0(R.target);
    $('total-sub').textContent = `${n0(S.rate)} g pro Stunde über ${hm(S.durationMin)} h`;

    // Eingepackt
    const diff = R.target - R.planned;
    const done = Math.abs(diff) < NEAR;
    let ps;
    if (!R.manual) ps = done ? ['ok', 'Alles verteilt.'] : ['warn', `${n0(diff)} g ohne Platz.`];
    else if (done) ps = ['ok', 'Ziel erreicht.'];
    else if (diff > 0) ps = ['info', `Es fehlen ${n0(diff)} g.`];
    else ps = ['info', `${n0(-diff)} g zu viel.`];
    $('packed').dataset.state = ps[0];
    $('packed-val').textContent = n0(R.planned);
    $('packed-target').textContent = n0(R.target);
    $('packed-fill').style.width = `${clamp(R.target ? R.planned / R.target : 0, 0, 1) * 100}%`;
    const bar = $('packed-bar');
    bar.setAttribute('aria-valuemax', Math.round(R.target));
    bar.setAttribute('aria-valuenow', Math.round(Math.min(R.planned, R.target)));
    bar.setAttribute('aria-valuetext', `${n0(R.planned)} von ${n0(R.target)} Gramm`);
    $('packed-status').innerHTML = `${ico(ps[0] === 'ok' ? 'ok' : ps[0] === 'warn' ? 'warn' : 'info')}<span>${ps[1]}</span>`;
    $('btn-suggest').setAttribute('aria-pressed', String(!R.manual));

    // Zähler
    $('bt-val').textContent = S.kit.bottles;
    $('fl-val').textContent = R.nFl;
    $('rf-val').textContent = R.refills;
    $('fl-auto').hidden = R.manual;
    $('rf-auto').hidden = R.manual;
    $('fl-auto').setAttribute('aria-pressed', String(S.flasks === 'auto'));
    $('rf-auto').setAttribute('aria-pressed', String(S.refills === 'auto'));
    const citrate = M.saltType === 'citrate';
    $('l-salt').textContent = `${citrate ? 'Natriumcitrat' : 'Salz'} je 90 g KH`;
    $('salt-val').textContent = M.salt > 0 ? `${nSalt(M.salt * (citrate ? CITRATE_PER_SALT : 1))} g` : 'ohne';
    const range = { bottles: [S.kit.bottles, 1, MAX_BOTTLES], flasks: [R.nFl, 0, MAX_FLASKS], refills: [R.refills, 0, MAX_REFILLS] };
    document.querySelectorAll('[data-act="step"]').forEach(b => {
      const [cur, min, max] = range[b.dataset.k];
      b.disabled = +b.dataset.d < 0 ? cur <= min : cur >= max;
    });
    document.querySelectorAll('[data-act="salt"]').forEach(b => {
      b.disabled = +b.dataset.d < 0 ? M.salt <= 0 : M.salt >= 3;
    });

    // Behälter
    renderRows(R.cs);
    const tm = R.cs.reduce((a, c) => a + c.malto, 0);
    const tf = R.cs.reduce((a, c) => a + c.fru, 0);
    const startMl = R.cs.reduce((a, c) => a + (c.kind === 'refill' ? 0 : c.ml), 0);
    const liters = ml => n2(ml / 1000).replace(/0$/, '');
    $('mix-total').innerHTML =
      (R.planned > 0 ? `<b>Zum Abwiegen gesamt:</b> ${recipe(tm, tf, R.saltEq, M)}<br>` : '') +
      `<b>Flüssigkeit:</b> ${liters(startMl)} l am Start` +
      (R.fluid > startMl ? `, ${liters(R.fluid - startMl)} l zum Nachfüllen` : '');
    $('hints').innerHTML = R.hints.map(([lvl, text]) =>
      `<li class="${lvl}">${ico(lvl === 'bad' ? 'bad' : lvl === 'warn' ? 'warn' : 'info')}<span>${text}</span></li>`).join('');

    // Kontrolle
    const scaleMax = Math.max(0.25, R.warnMax * 1.25);
    const pos = v => `${clamp(v / scaleMax, 0, 1) * 100}%`;
    $('meter-block').dataset.state = R.state;
    $('conc-val').textContent = `${n2(R.conc)} g/ml`;
    $('meter-fill').style.width = pos(R.conc);
    $('tick-ok').style.left = pos(L.okMax);
    $('tick-warn').style.left = pos(R.warnMax);
    $('scale-ok').style.left = pos(L.okMax);
    $('scale-ok').textContent = n2(L.okMax);
    $('scale-warn').style.left = pos(R.warnMax);
    $('scale-warn').textContent = n2(R.warnMax);
    $('meter').setAttribute('aria-label',
      `Konzentration ${n2(R.conc)} Gramm pro Milliliter. Zielbereich bis ${n2(L.okMax)}, Grenze bei ${n2(R.warnMax)}.`);
    const statusText = {
      empty: 'Noch keine Kohlenhydrate eingepackt.',
      ok: '<b>Passt.</b> Genug Flüssigkeit für die Kohlenhydrate dabei.',
      warn: `<b>An der Grenze.</b> Mit ${n0(R.extraMl)} ml mehr Wasser liegst du im Zielbereich.`,
      bad: `<b>Zu konzentriert.</b> Plane mindestens ${n0(R.extraMl)} ml mehr Wasser ein.`
    }[R.state];
    $('status').innerHTML = `${ico({ empty: 'info', ok: 'ok', warn: 'warn', bad: 'bad' }[R.state])}<span>${statusText}</span>`;
    $('tile-fluid').textContent = n0(r10(R.drinkPerHour));
    $('tile-na').textContent = R.saltEq > 0 ? n0(r10(R.sodiumPerHour)) : '0';
    $('tile-kcal').textContent = n0(r10(R.kcal));
    $('sr-summary').textContent =
      `Bedarf ${n0(R.target)} Gramm Kohlenhydrate, eingepackt ${n0(R.planned)} Gramm.`;

    // Unterwegs
    press($('int-chips'), S.interval);
    $('go-main').textContent = `Alle ${S.interval} Minuten eine Portion mit ${n0(R.dose)} g`;
    $('portions').innerHTML = R.portions.map(q => {
      if (q.flask) return `<li><b>${n0(r5(q.ml))} ml</b><span>aus der Flask</span></li>`;
      const fr = fraction(q.ml / q.cap);
      return `<li><b>${n0(r10(q.ml))} ml</b><span>aus einer ${n0(q.cap)}-ml-Flasche mit ${n0(q.carbs)} g${fr ? ` – ${fr}` : ''}</span></li>`;
    }).join('');
    let note = `Erste Portion in den ersten 15 Minuten. Dazu Wasser nach Durst, über alles mindestens ${n0(r10(R.drinkPerHour))} ml pro Stunde.`;
    if (R.flaskCarbs > 0) note += ` ${R.nFl > 1 ? 'Die Flasks decken' : 'Die Flask deckt'} ${hm(R.flaskCarbs / S.rate * 60)} h.`;
    if (R.planned > 0 && diff >= NEAR) note += ` Eingepackt ist genug für ${hm(R.planned / S.rate * 60)} h.`;
    $('go-note').textContent = note;

    // Details
    const rows = R.cs.filter(c => c.carbs > 0).map(c =>
      `<tr><td>${c.name}</td><td>${n0(c.carbs)} g</td><td>${n2(c.conc)}</td><td>≈ ${n0(r10(c.osmo))}</td></tr>`);
    rows.push(`<tr><td>Alles zusammen</td><td>${n0(R.planned)} g</td><td>${n2(R.conc)}</td><td>≈ ${n0(r10(R.osmoAll))}</td></tr>`);
    $('osmo-rows').innerHTML = rows.join('');
    let energy = `Die eingepackten Kohlenhydrate liefern etwa ${n0(r10(R.kcal))} kcal.`;
    if (S.power) {
      const kj = S.power * S.durationMin * 60 / 1000;
      energy += ` Bei ${n0(S.power)} W leistest du rund ${n0(r10(kj))} kJ Arbeit; das entspricht grob ebenso vielen kcal Verbrauch. Die Kohlenhydrate decken davon etwa ${n0(R.kcal / kj * 100)} %.`;
    }
    $('energy-note').textContent = energy;
    $('rules').innerHTML = [
      `Flask als Konzentrat mit ${n2(L.flask)} g/ml.`,
      `Flasche als alleiniges Getränk bis ${n2(L.bottleSolo)} g/ml, mit Wasser daneben bis ${n2(L.bottleMax)} g/ml.`,
      `Über alles: Kohlenhydrate geteilt durch die gesamte Flüssigkeit aus Flaschen, Nachfüllungen und Flask, also wenn du alles trinkst. Bis ${n2(L.okMax)} g/ml passt es, bis ${n2(R.warnMax)} ist es an der Grenze.`,
      'Mindestens trinken: der Wetter-Richtwert oder so viel, wie die Kohlenhydrate brauchen. Höchstens, was dabei ist, und nie weniger als die Flaschen, in denen Kohlenhydrate sind.',
      'Vorschlag: erst die Flask, der Rest auf Flaschen und Nachfüllungen. So viele Nachfüllungen, dass Wetter-Richtwert und Zielkonzentration erreicht werden.',
      '1 g Kochsalz enthält 393 mg Natrium; 1,7 g Natriumcitrat liefern dieselbe Menge.'
    ].map(t => `<li>${t}</li>`).join('');

    // Einstellungen: Felder nachführen, außer das gerade bearbeitete
    document.querySelectorAll('[data-set]').forEach(el => {
      if (el === document.activeElement) return;
      const [a, b] = el.dataset.set.split('.');
      el.value = S[a][b];
    });
    const pw = $('power');
    if (pw !== document.activeElement) pw.value = S.power || '';

    save();
  }

  // ---------- Bedienung ----------
  // Vom Vorschlag zum Selbstfüllen: aktuelle Mengen und Anzahlen einfrieren
  function enterManual() {
    if (S.manual) return;
    S.manual = {};
    R.cs.forEach(c => { S.manual[c.id] = c.carbs; });
    S.flasks = R.nFl;
    S.refills = R.refills;
  }
  // Mengen von Behältern vergessen, die es nicht mehr gibt
  function prune() {
    if (!S.manual) return;
    const count = { f: S.flasks, b: S.kit.bottles, r: S.refills };
    for (const id of Object.keys(S.manual)) if (+id.slice(1) >= count[id[0]]) delete S.manual[id];
  }

  document.addEventListener('click', ev => {
    const b = ev.target.closest('[data-act]');
    if (!b || b.disabled) return;
    const d = parseFloat(b.dataset.d);
    switch (b.dataset.act) {
      case 'dur': S.durationMin = clamp(S.durationMin + d, 30, 720); break;
      case 'set-dur': S.durationMin = +b.dataset.v; break;
      case 'rate': S.rate = clamp(S.rate + d, 20, 130); break;
      case 'set-rate': S.rate = +b.dataset.v; break;
      case 'weather': S.weather = b.dataset.v; break;
      case 'interval': S.interval = +b.dataset.v; break;
      case 'salt': S.mix.salt = clamp(S.mix.salt + d, 0, 3); break;
      case 'auto': if (!S.manual) S[b.dataset.k] = 'auto'; break;
      case 'step': {
        const k = b.dataset.k;
        if (k === 'bottles') S.kit.bottles = clamp(S.kit.bottles + d, 1, MAX_BOTTLES);
        else S[k] = clamp((k === 'flasks' ? R.nFl : R.refills) + d, 0, k === 'flasks' ? MAX_FLASKS : MAX_REFILLS);
        prune();
        break;
      }
      case 'size': {
        const id = b.dataset.id, i = +id.slice(1), v = +b.dataset.v;
        const sizes = { f: S.kit.flaskSizes, b: S.kit.bottleSizes, r: S.kit.refillSizes }[id[0]];
        sizes[i] = v;
        if (S.manual && S.manual[id] != null) S.manual[id] = Math.min(S.manual[id], limOf(kindOf(id), v, S.limits));
        break;
      }
      case 'adj': {
        const c = R.cs.find(x => x.id === b.dataset.id);
        if (!c) return;
        enterManual();
        S.manual[c.id] = clamp(c.carbs + d, 0, c.lim);
        break;
      }
      case 'suggest': S.manual = null; S.flasks = 'auto'; S.refills = 'auto'; break;
      case 'clear':
        enterManual();
        R.cs.forEach(c => { S.manual[c.id] = 0; });
        break;
      case 'reset-all':
        if (!window.confirm('Alle Einstellungen und Eingaben zurücksetzen?')) return;
        S = sanitize(JSON.parse(JSON.stringify(DEF)));
        break;
      default: return;
    }
    render();
  });

  // Gramm direkt eintippen: sofort mitrechnen, das Feld selbst erst beim Verlassen glätten
  const rowsEl = $('containers');
  rowsEl.addEventListener('input', ev => {
    const el = ev.target;
    if (!el.classList.contains('ct-in')) return;
    const c = R.cs.find(x => x.id === el.dataset.id);
    if (!c) return;
    enterManual();
    S.manual[c.id] = clamp(Math.round(parseFloat(String(el.value).replace(',', '.')) || 0), 0, c.lim);
    render();
  });
  rowsEl.addEventListener('focusin', ev => { if (ev.target.classList.contains('ct-in')) ev.target.select(); });
  rowsEl.addEventListener('focusout', ev => { if (ev.target.classList.contains('ct-in')) setTimeout(render, 0); });
  rowsEl.addEventListener('keydown', ev => { if (ev.key === 'Enter' && ev.target.classList.contains('ct-in')) ev.target.blur(); });

  document.addEventListener('change', ev => {
    const el = ev.target;
    if (el.id === 'power') {
      S.power = el.value ? +el.value : null;
    } else if (el.dataset && el.dataset.set) {
      const [a, b] = el.dataset.set.split('.');
      const v = el.tagName === 'SELECT' && isNaN(+el.value) ? el.value : parseFloat(String(el.value).replace(',', '.'));
      if (typeof v === 'number' && !isFinite(v)) { render(); return; }
      S[a][b] = v;
    } else {
      return;
    }
    sanitize(S);
    render();
  });

  let S = load();
  buildStatic();
  render();
  window.FuelingRechner = { compute, get state() { return S; }, defaults: DEF };

  // ---------- PWA ----------
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || local)) {
    window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });
  }
  let installEvent = null;
  const installBtn = $('install');
  window.addEventListener('beforeinstallprompt', ev => {
    ev.preventDefault();
    installEvent = ev;
    installBtn.hidden = false;
  });
  installBtn.addEventListener('click', async () => {
    if (!installEvent) return;
    installEvent.prompt();
    try { await installEvent.userChoice; } catch (e) { /* abgebrochen */ }
    installEvent = null;
    installBtn.hidden = true;
  });
  window.addEventListener('appinstalled', () => { installBtn.hidden = true; });
})();
