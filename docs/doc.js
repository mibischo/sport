// Trainingsplan: aktuelle Kalenderwoche markieren und beim Öffnen dorthin springen.
(() => {
  'use strict';

  // ISO-Kalenderwoche von heute, als "JJJJ-WW" wie im Attribut data-week
  const today = new Date();
  const t = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));
  t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));   // Donnerstag dieser Woche bestimmt das Jahr
  const year = t.getUTCFullYear();
  const week = Math.ceil(((t - Date.UTC(year, 0, 1)) / 86400000 + 1) / 7);
  const key = `${year}-${String(week).padStart(2, '0')}`;

  const weeks = [...document.querySelectorAll('section.week')];
  weeks.forEach(s => { if (s.dataset.week < key) s.classList.add('past'); });
  const now = weeks.find(s => s.dataset.week === key);
  if (!now) return;

  now.classList.add('now');
  now.querySelector('h2').insertAdjacentHTML('beforeend', ' <span class="pill now-pill">Diese Woche</span>');
  const btn = document.getElementById('jump-week');
  if (btn) {
    btn.hidden = false;
    btn.addEventListener('click', () => now.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }
  if (!location.hash) now.scrollIntoView({ block: 'start' });
})();
