// ريماكس العراق — يخلي التطبيق يفتح بسرعة، ويجيب أحدث نسخة من الموقع كل مرة
const CACHE = "remaxiq-v1";
self.addEventListener("install", e => { self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  e.respondWith(
    fetch(r).then(res => { const c = res.clone(); caches.open(CACHE).then(ca => ca.put(r, c)); return res; })
            .catch(() => caches.match(r).then(m => m || caches.match("/")))
  );
});
