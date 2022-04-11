console.log('Load Service Worker');
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('fox-store').then((cache) => cache.addAll([
      '/',
      '/js/pwa.js',
      '/css/mod_bootstrap.css',
      '/css/general.css',
    ])),
  );
});

self.addEventListener('fetch', (e) => {
  console.log(e.request.url);
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request)),
  );
});
