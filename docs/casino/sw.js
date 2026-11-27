// Offline support for the 俱乐部 home-screen app.
// Bump VERSION whenever index.html changes so installed copies pick up the update.
const VERSION = "gbc-0.18.7-cabinet-test";
const CORE = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "icons/favicon-32.png",
  "cabinet-test.css", "art/dragon-idle.webp", "art/thor-idle.webp", "art/dragon-reward-24.webp", "art/thor-reward-24.webp",
  ...["dragon", "thor", "gems", "fruit", "diver", "slots"].map((name) => "art/cabinets/" + name + ".webp"),
  ...["gems", "fruit", "diver", "slots"].map((name) => "art/cabinets/" + name + "-mascot.webp")];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // music streams straight from the network (it is large and uses range requests)
  if (url.pathname.includes("/music/")) return;
  // Pages: network first so updates arrive, cached copy when offline
  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then((r) => { const cp = r.clone(); caches.open(VERSION).then((c) => c.put("index.html", cp)); return r; })
      .catch(() => caches.match("index.html")));
    return;
  }
  // Fonts and our own files: cache first, refresh in the background
  if (url.origin === location.origin || /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) {
    e.respondWith(caches.open(VERSION).then((c) => c.match(req).then((hit) => {
      const net = fetch(req).then((r) => { if (r && (r.ok || r.type === "opaque")) c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    })));
  }
});
