/* Ephemeral market-hours lifecycle. No account state, storage or live data feed. */
(function (global) {
  'use strict';
  let host=null, view=null, catalog=null, snapshot=null, renderer=null, rendererFactory=null;
  let selectedVenueId='b3', desiredActive=false, disposed=false, loading=null, rendererLoading=null;
  let timer=null, signature='', observer=null, focused=true, catalogState='idle', rendererState='idle', loadingNote=null;
  let cameraTimer=null, cameraActive=false, cameraMode='reference', cameraDeadline=0, gestureHeld=false, pendingMarker=null, referenceMinute=null;
  const explorationMs=10000;
  function visibleHost() { return !!(host && host.isConnected && !host.closest('[hidden],[inert]')); }
  const markerByVenue=new Map(), cities=[];
  function slug(value) { return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''); }
  function live() { return !!(desiredActive && !disposed && view && !document.hidden && focused && visibleHost()); }
  function mapLive() { return live() && view.mapVisible; }
  function theme() { return document.documentElement.dataset.theme==='dark' ? 'dark':'light'; }
  function buildCities() {
    catalog.venues.forEach(v=>{
      let city=cities.find(c=>c.city===v.city && c.country===v.country);
      if(!city){city={id:'city-'+slug(v.city),city:v.city,country:v.country,lat:v.lat,lng:v.lng,venueIds:[]};if(cities.some(c=>c.id===city.id))city.id+='-'+slug(v.country);cities.push(city);}
      city.venueIds.push(v.id);markerByVenue.set(v.id,city.id);
    });
  }
  function markerData() {
    const css=getComputedStyle(view.root);
    return cities.map(city=>{
      const statuses=city.venueIds.map(id=>snapshot.venues.find(v=>v.id===id));
      const phase=statuses.some(s=>s.phase==='unknown') ? 'unknown':statuses.every(s=>s.phase===statuses[0].phase) ? statuses[0].phase:'mixed';
      const token=phase==='continuous' ? '--good':phase==='closed' || phase==='unknown' ? '--ink-dim':'--warn';
      return {id:city.id,venueIds:city.venueIds.slice(),lat:city.lat,lng:city.lng,label:city.city+' '+(phase==='unknown' ? '?':phase==='closed' ? '○':phase==='continuous' ? '●':'◐'),phase,color:css.getPropertyValue(token).trim() || '#526071'};
    });
  }
  function updateRenderer() {
    if(!renderer || !snapshot || !mapLive())return;
    const next=JSON.stringify([snapshot.venues.map(v=>[v.id,v.phase]),selectedVenueId,theme()]);
    if(next===signature)return;
    signature=next;renderer.update({markers:markerData(),selectedMarkerId:markerByVenue.get(selectedVenueId),theme:theme()});
  }
  function clearCameraTimer() { if(cameraTimer!==null){clearTimeout(cameraTimer);cameraTimer=null;} }
  function pauseCamera() { clearCameraTimer();gestureHeld=false; }
  function cameraMotion(animate) { return !!(animate && !matchMedia('(prefers-reduced-motion: reduce)').matches); }
  function noonLocation(now) {
    const utc=new Date(now),hour=utc.getUTCHours()+utc.getUTCMinutes()/60+utc.getUTCSeconds()/3600+utc.getUTCMilliseconds()/3600000;
    return {lat:0,lng:((180-15*hour+180)%360+360)%360-180};
  }
  function syncCamera(force=false,animate=false) {
    clearCameraTimer();if(!renderer || !mapLive())return;
    if(cameraMode==='manual'){
      if(gestureHeld)return;
      const remaining=cameraDeadline-performance.now();
      if(remaining>0){
        if(pendingMarker){renderer.focusMarker(pendingMarker,{animate:cameraMotion(true)});pendingMarker=null;}
        cameraTimer=setTimeout(()=>{cameraTimer=null;syncCamera(false,true);},remaining);return;
      }
      cameraMode='reference';cameraDeadline=0;pendingMarker=null;force=true;
    }
    const now=Date.now(),minute=Math.floor(now/60000);
    if(force || minute!==referenceMinute){
      renderer.focusLocation(noonLocation(now),{animate:cameraMotion(animate)});referenceMinute=minute;
    }
  }
  function interaction(event) {
    if(!renderer || !mapLive() || !event || !['start','end','key'].includes(event.type))return;
    if(event.type==='end' && !gestureHeld)return;
    cameraMode='manual';pendingMarker=null;cameraDeadline=performance.now()+explorationMs;
    if(event.type==='start')gestureHeld=true;
    if(event.type==='end')gestureHeld=false;
    syncCamera();
  }
  function select(id,source) {
    if(disposed || !catalog || !catalog.venues.some(v=>v.id===id))return;
    selectedVenueId=id;
    if(source!=='marker'){
      cameraMode='manual';gestureHeld=false;cameraDeadline=performance.now()+explorationMs;pendingMarker=markerByVenue.get(id);
    }
    if(snapshot)view.render(snapshot,id);
    updateRenderer();
    if(source!=='marker')syncCamera();
  }
  function createRenderer() {
    if(!mapLive() || renderer || !rendererFactory || rendererState==='error')return;
    try {
      const factory=rendererFactory;
      rendererState='ready';view.globeStatus('');
      renderer=factory.create(view.globe,{markers:markerData(),selectedMarkerId:markerByVenue.get(selectedVenueId),declutterLabels:true,look:{arcs:false,glowStrength:0.22},motion:{autoRotate:false,drag:true},
        onSelectMarker(event){if(!mapLive() || !event)return;const city=cities.find(c=>c.id===event.markerId);if(city)select(city.venueIds.includes(selectedVenueId) ? selectedVenueId:city.venueIds[0],'marker');},
        onInteraction:interaction,
        onError(){rendererError();}});
      signature='';updateRenderer();renderer.setActive(mapLive());syncCamera(true);
    }catch(error){if(renderer){renderer.dispose();renderer=null;}rendererError();}
  }
  function rendererError() {
    pauseCamera();
    rendererState='error';
    if(view)view.globeStatus('Globo indisponível. A tabela e os detalhes continuam disponíveis.',true);
  }
  function cancelRenderer() {
    const job=rendererLoading;if(!job)return;
    rendererLoading=null;rendererState='cancelled';job.controller.abort();
  }
  function retryRenderer() {
    if(disposed || !mapLive() || rendererLoading)return;
    if(renderer){renderer.dispose();renderer=null;}
    rendererState='idle';signature='';view.globeStatus('Carregando globo local…');loadRenderer();
  }
  function loadRenderer() {
    if(rendererLoading || !mapLive() || rendererState==='error')return;
    if(rendererFactory){createRenderer();return;}
    const job={controller:new AbortController(),promise:null};rendererLoading=job;rendererState='loading';
    job.promise=Promise.resolve().then(()=>{
      if(rendererLoading!==job || job.controller.signal.aborted)return null;
      return global.JPWMarketHoursAssets.getRenderer({signal:job.controller.signal});
    }).then(factory=>{
      if(disposed || rendererLoading!==job || job.controller.signal.aborted || !mapLive())return;
      if(!factory || typeof factory.create!=='function')throw Error('Renderer local inválido');
      rendererFactory=factory;rendererState='ready';createRenderer();
    }).catch(()=>{if(!disposed && rendererLoading===job && !job.controller.signal.aborted)rendererError();})
      .then(()=>{if(rendererLoading===job)rendererLoading=null;});
  }
  function clearTimer() { if(timer!==null){clearTimeout(timer);timer=null;} }
  function tick(forceCamera=false) {
    clearTimer();if(!live())return;
    try {snapshot=global.JPWMarketSessions.at(catalog,Date.now());view.render(snapshot,selectedVenueId);updateRenderer();syncCamera(forceCamera);}
    catch(error){pauseCamera();view.globeStatus('Calendário indisponível: '+error.message);if(renderer)renderer.setActive(false);return;}
    let delay=1000;
    snapshot.venues.forEach(v=>{if(v.nextTransition && v.nextTransition.earliestUtc>snapshot.asOf)delay=Math.min(delay,v.nextTransition.earliestUtc-snapshot.asOf);});
    timer=setTimeout(tick,Math.max(25,delay));
  }
  function sync() {
    clearTimer();
    if(!live() && view)view.closeHelp();
    const active=mapLive(),resumed=active&&!cameraActive;cameraActive=active;
    if(renderer)renderer.setActive(active);
    if(!active){pauseCamera();cancelRenderer();}
    if(host && !visibleHost())cancelCatalog();
    if(desiredActive && visibleHost() && catalogState==='cancelled')loadCatalog();
    if(live()){tick(resumed);if(mapLive())loadRenderer();}
  }
  function visibility() { sync(); }
  function blur() { focused=false;sync(); }
  function focus() { focused=true;sync(); }
  function catalogMessage(message,retry) {
    if(!loadingNote){
      loadingNote=document.createElement('div');loadingNote.className='mh-loading';
      const status=document.createElement('p');status.setAttribute('role','status');
      const button=document.createElement('button');button.type='button';button.dataset.mh='catalog-retry';button.textContent='Tentar carregar o calendário novamente';
      button.addEventListener('click',()=>loadCatalog(true));loadingNote.append(status,button);host.append(loadingNote);
    }
    loadingNote.firstChild.textContent=message;loadingNote.lastChild.hidden=!retry;
  }
  function cancelCatalog() {
    const job=loading;if(!job)return;
    loading=null;catalogState='cancelled';job.controller.abort();
    if(!disposed)catalogMessage('Carregamento do calendário pausado.',true);
  }
  function loadCatalog(restoreFocus=false) {
    if(disposed || view || loading || !visibleHost())return loading?.promise || Promise.resolve(!!view);
    catalogState='loading';catalogMessage('Carregando calendário das bolsas…',false);
    const job={controller:new AbortController(),promise:null};loading=job;
    job.promise=Promise.resolve().then(()=>{
      if(loading!==job || job.controller.signal.aborted)return null;
      return global.JPWMarketHoursAssets.getCatalog({signal:job.controller.signal});
    }).then(raw=>{
      if(disposed || loading!==job || job.controller.signal.aborted || !visibleHost())return false;
      catalog=global.JPWMarketSessions.prepare(raw);cities.length=0;markerByVenue.clear();buildCities();
      if(!catalog.venues.some(v=>v.id===selectedVenueId))selectedVenueId=catalog.venues[0].id;
      const nextView=global.JPWMarketHoursView.create(host,catalog,select,retryRenderer,sync);
      snapshot=global.JPWMarketSessions.at(catalog,Date.now());nextView.render(snapshot,selectedVenueId);view=nextView;
      loadingNote.remove();loadingNote=null;catalogState='ready';
      if(restoreFocus)view.focusSelected();
      sync();return true;
    }).catch(error=>{
      if(!disposed && loading===job && !job.controller.signal.aborted){catalogState='error';catalogMessage('Calendário indisponível: '+error.message,true);}
      return false;
    }).then(value=>{if(loading===job)loading=null;return value;});
    return job.promise;
  }
  function mount(target) {
    if(disposed)return Promise.resolve(false);
    if(host){if(view)return Promise.resolve(true);return loading?.promise || loadCatalog();}
    if(!(target instanceof HTMLElement))return Promise.reject(Error('Host das bolsas ausente.'));
    host=target;
    document.addEventListener('visibilitychange',visibility);global.addEventListener('blur',blur);global.addEventListener('focus',focus);
    observer=new MutationObserver(sync);
    for(let el=host;el;el=el.parentElement)observer.observe(el,{attributes:true,attributeFilter:['hidden','inert','class','data-theme','data-fs']});
    return loadCatalog();
  }
  function activate(target) {if(disposed)return;desiredActive=true;if(target && !view)mount(target);sync();}
  function deactivate() {desiredActive=false;cancelCatalog();cancelRenderer();sync();}
  function dispose() {
    if(disposed)return;disposed=true;desiredActive=false;cancelCatalog();cancelRenderer();clearTimer();pauseCamera();
    if(observer)observer.disconnect();observer=null;
    document.removeEventListener('visibilitychange',visibility);global.removeEventListener('blur',blur);global.removeEventListener('focus',focus);
    if(renderer)renderer.dispose();renderer=null;
    if(view)view.dispose();else if(loadingNote)loadingNote.remove();loadingNote=null;
    view=null;catalog=null;snapshot=null;rendererFactory=null;host=null;cities.length=0;markerByVenue.clear();
  }
  global.JPWMarketHours=Object.freeze({mount,activate,deactivate,dispose});
})(globalThis);
