const CACHE_NAME = 'my-chat-pwa-cache-v1';
const urlsToCache = [
    '/',
    '/staticfiles/css/style.css',
    '/staticfiles/css/login.css',
    '/staticfiles/js/jquery.min.js',
    '/staticfiles/js/loader.js',
    '/staticfiles/js/main.js',
    '/staticfiles/manifest.json',
    '/staticfiles/img/icon-192x192.png',
    '/staticfiles/img/icon-512x512.png',
    '/staticfiles/img/LOGO.png',
    '/staticfiles/img/LOGO_ICON.png',
    '/chat/1/',
    '/chat/',
    '/inicio/',
    '/login/',
    '/publicaciones/',
    '/contactos/',
    '/usuarios/',
    '/servicios/',
    '/solicitudes/',
    '/publicador/'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Cache abierta');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Eliminando caché antigua', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request).then(
          response => {
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            return response;
          }
        );
      })
      .catch(() => {
        console.log('Service Worker: Red y caché fallaron para', event.request.url);
      })
  );
});

// --- Opcional: Manejo de Notificaciones Push (más avanzado) ---
/*
self.addEventListener('push', event => {
    const data = event.data.json();
    console.log('Notificación Push recibida:', data);
    const options = {
        body: data.body,
        icon: '/static/images/icons/icon-192x192.png', // Un icono para la notificación
        badge: '/static/images/icons/badge.png' // Icono pequeño en Android
    };
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/') // Abre la URL asociada a la notificación
    );
});
*/
