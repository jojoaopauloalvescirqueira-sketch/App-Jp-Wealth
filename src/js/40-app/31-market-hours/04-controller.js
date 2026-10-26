/* Ephemeral market-hours lifecycle. No account state, storage or live data feed. */
(function (global) {
  'use strict';
  let host=null, view=null, overview=null, catalog=null, snapshot=null, renderer=null, rendererFactory=null;
  let selectedVenueId='b3', desiredActive=false, disposed=false, loading=null, rendererLoading=null;
  let timer=null, signature='', observer=null, focused=true, catalogState='idle', rendererState='idle', loadingNote=null;
  let expanded=true, viewportObserver=null, mapInViewport=false, snapshotError=false, buildingView=false, contextVersion=0;
  let cameraTimer=null, cameraActive=false, cameraMode='reference', cameraDeadline=0, gestureHeld=false, pendingMarker=null, referenceMinute=null;
  const explorationMs=10000;
  function visibleHost() { return !!(host && host.isConnected && !host.closest('[hidden],[inert]')); }
  const markerByVenue=new Map(), cities=[];
  function slug(value) { return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''); }
  function live() { return !!(desiredActive && !disposed && catalog && !document.hidden && focused && visibleHost()); }
  function mapLive() { return !!(live() && expanded && view && view.mapVisible && mapInViewport && !snapshotError); }
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
    if(snapshot && view && expanded)view.render(snapshot,id);
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
  function renderSnapshot() {
    if(overview && !expanded)overview.render(snapshot,catalog);
    if(view && expanded)view.render(snapshot,selectedVenueId);
  }
  function nextDelay() {
    const now=snapshot.asOf;let delay=expanded ? 1000:60000-now%60000;
    function boundary(utc){if(Number.isFinite(utc) && utc>now)delay=Math.min(delay,utc-now);}
    snapshot.venues.forEach(venue=>{
      [venue.nextTransition,...(venue.groups || []).map(group=>group.nextTransition)].filter(Boolean).forEach(value=>{boundary(value.earliestUtc);boundary(value.latestUtc);});
      [venue.coverage,...(venue.groups || []).map(group=>group.coverage)].filter(Boolean).forEach(value=>{boundary(value.fromUtc);boundary(value.untilUtc);});
      if(venue.nextRegularOpen){boundary(venue.nextRegularOpen.earliestUtc);boundary(venue.nextRegularOpen.latestUtc);boundary(venue.nextRegularOpen.latestUtc-86400000);}
    });
    return Math.max(1,delay);
  }
  function tick(forceCamera=false) {
    clearTimer();if(!live())return;
    try {snapshot=global.JPWMarketSessions.at(catalog,Date.now());snapshotError=false;renderSnapshot();if(overview)overview.message('');updateRenderer();syncCamera(forceCamera);}
    catch(error){snapshotError=true;pauseCamera();const message='Calendário indisponível: '+error.message+(snapshot ? '. Exibindo a última referência; os horários podem estar desatualizados.':'');catalogMessage(message,true);if(renderer)renderer.setActive(false);return;}
    timer=setTimeout(tick,nextDelay());
  }
  function sync() {
    if(buildingView)return;
    clearTimer();
    if((!live() || !expanded) && view)view.closeHelp();
    const active=mapLive(),resumed=active&&!cameraActive;cameraActive=active;
    if(renderer)renderer.setActive(active);
    if(!active){pauseCamera();cancelRenderer();}
    if(host && (!visibleHost() || document.hidden || !focused))cancelCatalog();
    if(desiredActive && visibleHost() && !document.hidden && focused && catalogState==='cancelled')loadCatalog();
    if(live() && !snapshotError){tick(resumed);if(mapLive())loadRenderer();}
  }
  function visibility() { sync(); }
  function blur() { focused=false;contextVersion++;sync(); }
  function focus() { focused=true;sync(); }
  function catalogMessage(message,retry) {
    if(overview){overview.message(message,retry);return;}
    if(!loadingNote){
      loadingNote=document.createElement('div');loadingNote.className='mh-loading';
      const status=document.createElement('p');status.setAttribute('role','status');
      const button=document.createElement('button');button.type='button';button.dataset.mh='catalog-retry';button.textContent='Tentar carregar o calendário novamente';
      button.addEventListener('click',retryCalendar);loadingNote.append(status,button);host.append(loadingNote);
    }
    loadingNote.firstChild.textContent=message;loadingNote.lastChild.hidden=!retry;
  }
  function retryCalendar(event) {
    const initiator=event?.currentTarget,restoreFocus=initiator && document.activeElement===initiator;
    if(!catalog)return loadCatalog(restoreFocus ? initiator:null);
    snapshotError=false;sync();
    if(!snapshotError && loadingNote){loadingNote.remove();loadingNote=null;}
    if(restoreFocus && !snapshotError && live()){if(expanded && view)view.focusSelected();else if(overview)overview.toggle.focus({preventScroll:true});}
    return Promise.resolve(!snapshotError);
  }
  function ensureOverview() {
    if(overview)return;
    overview=global.JPWMarketHoursView.createOverview(host,()=>setExpanded(!expanded),id=>{
      setExpanded(true).then(accepted=>{if(accepted && live() && expanded){select(id,'summary');view.focusSelected();}});
    },retryCalendar);
    if(loadingNote){loadingNote.remove();loadingNote=null;}
    if(view){overview.toggle.setAttribute('aria-controls',view.root.id);const summary=view.root.querySelector?.('[data-mh="summary"]');if(summary)summary.dataset.mh='exploration-summary';}
    overview.setExpanded(expanded,!!view);
  }
  function ensureView() {
    if(view || !expanded || !catalog || !visibleHost() || disposed)return;
    buildingView=true;
    try{view=global.JPWMarketHoursView.create(host,catalog,select,retryRenderer,sync);}finally{buildingView=false;}
    view.root.dataset.mh='exploration';view.root.id='marketHoursExploration';
    if(overview){overview.toggle.setAttribute('aria-controls',view.root.id);overview.setExpanded(expanded);const summary=view.root.querySelector?.('[data-mh="summary"]');if(summary)summary.dataset.mh='exploration-summary';}
    mapInViewport=typeof global.IntersectionObserver!=='function';
    if(!mapInViewport){
      viewportObserver=new global.IntersectionObserver(entries=>{
        if(disposed || !view)return;
        const entry=entries.find(entry=>entry.target===view.globe);if(!entry)return;
        const visible=entry.isIntersecting && entry.intersectionRatio>0;
        if(visible!==mapInViewport){mapInViewport=visible;sync();}
      });
      viewportObserver.observe(view.globe);
    }
  }
  function setExpanded(value) {
    if(disposed || !host)return Promise.resolve(false);
    const next=!!value,returnFocus=!next && view && (view.containsFocus ? view.containsFocus():view.root.contains?.(document.activeElement));
    if(next!==expanded)contextVersion++;
    if(!next)ensureOverview();
    expanded=next;if(overview)overview.setExpanded(next,!!view);
    ensureView();
    if(view){if(view.setExpanded)view.setExpanded(next);else view.root.hidden=!next;}
    if(snapshot)renderSnapshot();
    if(returnFocus)overview.toggle.focus({preventScroll:true});
    sync();
    return catalog ? Promise.resolve(true):loading?.promise || loadCatalog();
  }
  function cancelCatalog() {
    const job=loading;if(!job)return;
    loading=null;catalogState='cancelled';job.controller.abort();
    if(!disposed)catalogMessage('Carregamento do calendário pausado.',true);
  }
  function loadCatalog(focusTarget=null) {
    if(disposed || catalog || loading || !visibleHost() || document.hidden || !focused)return loading?.promise || Promise.resolve(!!catalog);
    catalogState='loading';catalogMessage('Carregando calendário das bolsas…',!!focusTarget);
    const job={controller:new AbortController(),promise:null,contextVersion};loading=job;
    job.promise=Promise.resolve().then(()=>{
      if(loading!==job || job.controller.signal.aborted)return null;
      return global.JPWMarketHoursAssets.getCatalog({signal:job.controller.signal});
    }).then(raw=>{
      if(disposed || loading!==job || job.controller.signal.aborted || !visibleHost() || document.hidden || !focused)return false;
      const restoreFocus=focusTarget && focusTarget.isConnected && document.activeElement===focusTarget && !focusTarget.closest('[hidden],[inert]') && job.contextVersion===contextVersion;
      catalog=global.JPWMarketSessions.prepare(raw);cities.length=0;markerByVenue.clear();buildCities();
      if(!catalog.venues.some(v=>v.id===selectedVenueId))selectedVenueId=catalog.venues[0].id;
      catalogState='ready';ensureView();
      snapshot=global.JPWMarketSessions.at(catalog,Date.now());snapshotError=false;renderSnapshot();
      if(loadingNote){loadingNote.remove();loadingNote=null;}if(overview)overview.message('');
      if(restoreFocus){if(expanded && view)view.focusSelected();else if(overview)overview.toggle.focus({preventScroll:true});}
      sync();return true;
    }).catch(error=>{
      if(!disposed && loading===job && !job.controller.signal.aborted){catalogState=catalog ? 'ready':'error';snapshotError=!!catalog;catalogMessage('Calendário indisponível: '+error.message,true);}
      return false;
    }).then(value=>{if(loading===job)loading=null;return value;});
    return job.promise;
  }
  function mount(target,options) {
    if(disposed)return Promise.resolve(false);
    if(host){if(catalog)return Promise.resolve(true);return loading?.promise || loadCatalog();}
    if(!(target instanceof HTMLElement))return Promise.reject(Error('Host das bolsas ausente.'));
    host=target;
    expanded=options?.collapsed!==true;if(!expanded)ensureOverview();
    document.addEventListener('visibilitychange',visibility);global.addEventListener('blur',blur);global.addEventListener('focus',focus);
    observer=new MutationObserver(sync);
    for(let el=host;el;el=el.parentElement)observer.observe(el,{attributes:true,attributeFilter:['hidden','inert','class','data-theme','data-fs']});
    return loadCatalog();
  }
  function activate(target) {if(disposed)return;desiredActive=true;if(target && !view)mount(target);sync();}
  function deactivate() {desiredActive=false;contextVersion++;cancelCatalog();cancelRenderer();sync();}
  function dispose() {
    if(disposed)return;disposed=true;desiredActive=false;cancelCatalog();cancelRenderer();clearTimer();pauseCamera();
    if(observer)observer.disconnect();observer=null;if(viewportObserver)viewportObserver.disconnect();viewportObserver=null;
    document.removeEventListener('visibilitychange',visibility);global.removeEventListener('blur',blur);global.removeEventListener('focus',focus);
    if(renderer)renderer.dispose();renderer=null;
    if(view)view.dispose();if(overview)overview.dispose();else if(loadingNote)loadingNote.remove();loadingNote=null;overview=null;
    view=null;catalog=null;snapshot=null;rendererFactory=null;host=null;cities.length=0;markerByVenue.clear();
  }
  global.JPWMarketHours=Object.freeze({mount,setExpanded,activate,deactivate,dispose});
})(globalThis);
