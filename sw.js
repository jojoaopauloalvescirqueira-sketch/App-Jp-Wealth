importScripts('./build-id.js');
const CACHE_PREFIX = 'jp-wealth-';
const CACHE_NAME = `${CACHE_PREFIX}${JP_WEALTH_BUILD_ID}`;
const ICON_CACHE_VERSION = '20260803';
const PRECACHE_URLS = [
  './', './index.html', './build-id.js', './src/styles/app.css', './src/js/manifest.json',
  './src/js/00-core/01-risk-profiles.js', './src/js/00-core/02-platforms.js',
  './src/js/00-core/03-default-state.js', './src/js/00-core/04-persistence.js',
  './src/js/00-core/05-helpers.js', './src/js/10-domain/01-risk-instruments.js',
  './src/js/10-domain/02-risk-calculations.js', './src/js/20-ui/01-header-readout.js',
  './src/js/20-ui/02-sidebar.js', './src/js/20-ui/03-main-render.js',
  './src/js/20-ui/04-operational-clearance.js', './src/js/20-ui/05-execution-clearance.js',
  './src/js/10-domain/03-phase-transitions.js', './src/js/10-domain/04-stop-statistics.js',
  './src/js/20-ui/06-chart-terminal-chrome.js', './src/js/20-ui/07-chart-crosshair-tooltip.js',
  './src/js/20-ui/08-input-bindings.js', './src/js/30-accounting/01-daily-ledger.js',
  './src/js/10-domain/05-brokers-prop-firms.js', './src/js/30-accounting/02-accounting-engine.js',
  './src/js/30-accounting/03-mei-jp.js', './src/js/30-accounting/04-patrimonial-simulation.js',
  './src/js/40-app/01-navigation.js', './src/js/40-app/02-reset.js', './src/js/40-app/03-theme.js',
  './src/js/20-ui/09-contextual-help.js', './src/js/20-ui/10-font-scale.js',
  './src/js/10-domain/06-quarantine.js', './src/js/20-ui/11-phase-posture.js',
  './src/js/40-app/04-onboarding.js', './src/js/40-app/05-wipe-all.js',
  './src/js/40-app/06-app-icons.js', './src/js/40-app/07-finalize-session.js', './src/js/40-app/06-boot.js',
  './manifests/jp-wealth-flat-knight.webmanifest',
  './manifests/jp-wealth-relief-knight.webmanifest',
  './manifests/jp-wealth-marble-knight.webmanifest',
  './icons/flat-knight/favicon-16.png', './icons/flat-knight/favicon-32.png', './icons/flat-knight/favicon-48.png',
  './icons/flat-knight/apple-touch-icon.png', './icons/flat-knight/icon-180.png', './icons/flat-knight/icon-192.png', './icons/flat-knight/icon-512.png',
  './icons/relief-knight/favicon-16.png', './icons/relief-knight/favicon-32.png', './icons/relief-knight/favicon-48.png',
  './icons/relief-knight/apple-touch-icon.png', './icons/relief-knight/icon-180.png', './icons/relief-knight/icon-192.png', './icons/relief-knight/icon-512.png',
  './icons/marble-knight/favicon-16.png', './icons/marble-knight/favicon-32.png', './icons/marble-knight/favicon-48.png',
  './icons/marble-knight/apple-touch-icon.png', './icons/marble-knight/icon-180.png', './icons/marble-knight/icon-192.png', './icons/marble-knight/icon-512.png'
].flatMap(url=>url.startsWith('./icons/')?[url,`${url}?v=${ICON_CACHE_VERSION}`]:[url]);

self.addEventListener('install', event => {
  event.waitUntil((async()=>{
    const cache=await caches.open(CACHE_NAME);
    try { await cache.addAll(PRECACHE_URLS); }
    catch(error){ await caches.delete(CACHE_NAME); throw error; }
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', event => {
  if(event.request.method !== 'GET') return;
  const url=new URL(event.request.url);
  if(event.request.mode === 'navigate'){
    event.respondWith(fetch(event.request).then(async response=>{
      if(response && response.ok) (await caches.open(CACHE_NAME)).put('./index.html',response.clone());
      return response;
    }).catch(()=>caches.open(CACHE_NAME).then(cache=>cache.match('./index.html'))));
    return;
  }
  if(url.origin !== self.location.origin){ event.respondWith(fetch(event.request)); return; }
  event.respondWith(caches.open(CACHE_NAME).then(cache=>cache.match(event.request).then(cached=>cached||fetch(event.request))));
});
