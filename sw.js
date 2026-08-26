importScripts('./build-id.js');
const CACHE_PREFIX = 'jp-wealth-';
const CACHE_NAME = `${CACHE_PREFIX}${JP_WEALTH_BUILD_ID}`;
const ICON_CACHE_VERSION = '20260806';
const PRECACHE_URLS = [
  './', './index.html', './build-id.js', './src/styles/app.css', './src/js/manifest.json',
  './assets/jp-wealth-logo.png',
  './src/js/00-core/01-risk-profiles.js', './src/js/00-core/02-platforms.js',
  './src/js/00-core/03-default-state.js', './src/js/00-core/04-persistence.js',
  './src/js/00-core/05-helpers.js', './src/js/00-core/06-storage-fs.js',
  './src/js/10-domain/01-risk-instruments.js',
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
  './src/js/10-domain/06-quarantine.js', './src/js/20-ui/11-phase-posture.js', './src/js/20-ui/12-nav-style.js',
  './src/js/40-app/04-onboarding.js', './src/js/40-app/05-wipe-all.js',
  './src/js/40-app/06-app-icons.js', './src/js/40-app/07-finalize-session.js', './src/js/40-app/06-boot.js',
  './src/js/40-app/08-educational-content.js', './src/js/40-app/09-settings-modal.js',
  './src/js/40-app/10-dashboard-immersive.js', './src/js/40-app/11-operational-shell.js',
  './src/js/40-app/12-global-dashboard.js', './src/js/40-app/13-dashboard-layout.js',
  './src/js/40-app/14-mvp-notes.js', './src/js/40-app/15-ff-news.js',
  './src/js/40-app/16-storage-governance.js', './src/js/40-app/17-economic-calendar.js',
  './src/vendor/planck/planck-1.5.0.min.js',
  './src/js/40-app/18-galton-board/01-config.js', './src/js/40-app/18-galton-board/02-rng.js',
  './src/js/40-app/18-galton-board/03-statistics.js', './src/js/40-app/18-galton-board/04-physics.js',
  './src/js/40-app/18-galton-board/05-renderer.js', './src/js/40-app/18-galton-board/06-controller.js',
  './src/js/10-domain/07-reserve-requirements.js',
  './src/js/10-domain/08-usd-brl-quote.js',
  './src/js/30-accounting/05-fx-planning/01-fx-model.js', './src/js/30-accounting/05-fx-planning/02-fx-engine.js',
  './src/js/30-accounting/05-fx-planning/03-fx-state.js',
  './src/js/30-accounting/05-fx-planning/04-fx-charts.js', './src/js/30-accounting/05-fx-planning/05-fx-ui.js',
  './src/js/20-ui/13-exec-views.js',
  './src/js/10-domain/09-nocoda-geometry.js',
  './src/js/20-ui/14-nocoda-studies.js',
  './src/js/10-domain/10-pivot-studies.js',
  './src/js/20-ui/15-pivot-studies.js',
  './src/js/10-domain/11-operation-lifecycle.js',
  './src/js/10-domain/12-personal-finance.js',
  './src/js/20-ui/17-finpes-views.js',
  './src/js/20-ui/18-finpes-budget.js',
  './src/js/20-ui/19-finpes-debts.js',
  './src/js/20-ui/20-finpes-comparison.js',
  './src/js/20-ui/21-finpes-scenarios.js',
  './src/js/20-ui/22-finpes-overview.js',
  './src/js/10-domain/13-alladin.js',
  './src/js/20-ui/23-research-views.js',
  './src/js/20-ui/16-operation-history.js',
  './manifests/jp-wealth.webmanifest',
  './assets/pwa-icon-primary.png', './assets/pwa-icon-secondary.png'
].flatMap(url=>url.startsWith('./assets/pwa-icon-')?[url,`${url}?v=${ICON_CACHE_VERSION}`]:[url]);

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
    // Uma navegacao controlada precisa permanecer no MESMO build do controller.
    // Se buscasse o HTML novo na rede enquanto scripts/CSS continuam cache-first
    // no cache antigo, o cliente de descoberta executaria uma mistura de versoes.
    // O HTML antigo ja chama registration.update(), portanto ele descobre o worker
    // novo sem precisar executar o documento novo antes da ativacao normal.
    event.respondWith(caches.open(CACHE_NAME).then(async cache=>{
      const cached=await cache.match('./index.html');
      return cached||fetch(event.request);
    }));
    return;
  }
  if(url.origin !== self.location.origin){ event.respondWith(fetch(event.request)); return; }
  event.respondWith(caches.open(CACHE_NAME).then(cache=>cache.match(event.request).then(cached=>cached||fetch(event.request))));
});
