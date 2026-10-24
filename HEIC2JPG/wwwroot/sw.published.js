// The SDK generates content hashes during publish.
importScripts('./service-worker-assets.js');
const CACHE_PREFIX = 'heic2jpg-';
const CACHE_NAME = `${CACHE_PREFIX}${self.assetsManifest.version}`;
// Only the two Bootstrap bundles referenced by index.html are used; skip the other variants.
const usedBootstrap = new Set(['lib/bootstrap/dist/css/bootstrap.min.css', 'lib/bootstrap/dist/js/bootstrap.bundle.min.js']);
const assets = self.assetsManifest.assets
    .filter(asset => !/\.(?:map|md)$/.test(asset.url) && !asset.url.endsWith('_headers'))
    .filter(asset => !asset.url.startsWith('lib/bootstrap/') || usedBootstrap.has(asset.url))
    .map(asset => ({ ...asset, url: new URL(asset.url, self.registration.scope).href }));
const knownURLs = new Set(assets.map(asset => asset.url));
const indexURL = new URL('index.html', self.registration.scope).href;

self.addEventListener('install', event => {
    event.waitUntil((async () => {
        const alreadyExisted = await caches.has(CACHE_NAME);
        try {
            const cache = await caches.open(CACHE_NAME);
            // Reject partial/stale deployments before activating an offline cache.
            await cache.addAll(assets.map(asset => new Request(asset.url, {
                integrity: asset.hash, cache: 'no-cache'
            })));
        } catch (error) {
            if (!alreadyExisted) await caches.delete(CACHE_NAME);
            throw error;
        }
        // Wait for existing clients to close or explicitly accept the update.
    })());
});

self.addEventListener('message', event => {
    if (event.data?.type !== 'APPLY_UPDATE') return;
    event.waitUntil((async () => {
        const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
        if (clients.filter(client => client.url.startsWith(self.registration.scope)).length > 1) {
            event.source?.postMessage({ type: 'CLOSE_OTHER_TABS' });
            return;
        }
        await self.skipWaiting();
    })());
});

self.addEventListener('activate', event => {
    event.waitUntil((async () => {
        for (const name of await caches.keys()) {
            if (name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME) await caches.delete(name);
        }
    })());
});

self.addEventListener('fetch', event => {
    const request = event.request;
    if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
    // Only assets in this release's manifest are cached.
    if (knownURLs.has(request.url)) {
        event.respondWith(caches.open(CACHE_NAME).then(async cache =>
            (await cache.match(request)) || fetch(request)));
    } else if (request.mode === 'navigate') {
        event.respondWith(caches.open(CACHE_NAME).then(async cache => {
            const cached = await cache.match(indexURL);
            // Evicted/cleared cache: fall back to the network instead of failing the navigation.
            if (!cached) return fetch(request);
            // Hosts such as Cloudflare Pages redirect /index.html to /; browsers reject a
            // redirected response for a navigation, so serve an unredirected copy.
            if (!cached.redirected) return cached;
            return new Response(cached.body, {
                status: cached.status, statusText: cached.statusText, headers: cached.headers
            });
        }));
    }
});
