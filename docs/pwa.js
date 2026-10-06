// Offline-Cache anmelden und die Installieren-Taste bedienen. Wird von allen Seiten geladen.
(() => {
  'use strict';

  const local = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || local)) {
    window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });
  }

  const btn = document.getElementById('install');
  if (!btn) return;
  let installEvent = null;
  window.addEventListener('beforeinstallprompt', ev => {
    ev.preventDefault();
    installEvent = ev;
    btn.hidden = false;
  });
  btn.addEventListener('click', async () => {
    if (!installEvent) return;
    installEvent.prompt();
    try { await installEvent.userChoice; } catch (e) { /* abgebrochen */ }
    installEvent = null;
    btn.hidden = true;
  });
  window.addEventListener('appinstalled', () => { btn.hidden = true; });
})();
