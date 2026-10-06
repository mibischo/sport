// Offline-Cache für den Fueling-Rechner.
// Bei jeder Änderung an den Dateien VERSION erhöhen, damit alte Caches verschwinden.
const VERSION = 'v5';
const CACHE = `fueling-${VERSION}`;
const ASSETS = [
  './',
  'index.html',
  'plan.html',
  'analyse.html',
  'style.css',
  'app.js',
  'doc.js',
  'pwa.js',
  'manifest.webmanifest',
  'icons/favicon.svg',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-maskable-512.png',
  'icons/apple-touch-icon.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('fueling-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Sofort aus dem Cache antworten und im Hintergrund auffrischen:
// die App startet auch ohne Netz, eine neue Version ist beim nächsten Öffnen da.
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = (await cache.match(req, { ignoreSearch: true }))
      || (req.mode === 'navigate' ? await cache.match('./') : undefined);
    const fresh = fetch(req)
      .then(res => {
        if (res && res.ok && res.type === 'basic') cache.put(req, res.clone());
        return res;
      })
      .catch(() => undefined);
    if (cached) {
      event.waitUntil(fresh);
      return cached;
    }
    return (await fresh) || new Response('Offline', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  })());
});
