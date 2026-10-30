// Necesario para que Chrome ofrezca "Instalar app". No guarda nada: todo se pide siempre a internet.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => e.respondWith(fetch(e.request)));
