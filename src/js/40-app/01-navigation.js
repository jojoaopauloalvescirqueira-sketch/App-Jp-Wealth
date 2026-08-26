// ============ NAVEGAÇÃO SEMÂNTICA (NAV-01 · N1) ============
// O contrato público tem exatamente cinco rotas canônicas. IDs físicos e
// destinos antigos continuam resolvíveis somente pela camada de compatibilidade
// e nunca aparecem em JPWNavigation.routes(). Navegação é estado efêmero de UI:
// este módulo não persiste preferência, tela ou visão local.

const NAV_CANONICAL_ROUTES=Object.freeze([
  Object.freeze({id:'dashboard',primary:'dashboard',screen:'dash',localView:null,aliases:Object.freeze(['dash'])}),
  Object.freeze({id:'forex-overview',primary:'forex',screen:'exec',localView:Object.freeze({surface:'exec',view:'overview'}),aliases:Object.freeze(['exec'])}),
  Object.freeze({id:'personal-finance',primary:'personal-finance',screen:'finpes',localView:Object.freeze({surface:'finpes',view:'overview'}),aliases:Object.freeze(['finpes'])}),
  Object.freeze({id:'research-forex',primary:'research',screen:'research',localView:null,aliases:Object.freeze([])}),
  Object.freeze({id:'alladin',primary:'alladin',screen:'alladin',localView:null,aliases:Object.freeze([])})
]);

// Destinos transitórios/legados. Saber resolvê-los não os promove a rotas da
// nova IA. `contas`, por exemplo, continua sendo a section física #contas e
// pertence visualmente ao primário Forex, mas `forex-account` ainda não existe.
const NAV_COMPATIBILITY_TARGETS=Object.freeze({
  contas:Object.freeze({screen:'contas',primary:'forex'}),
  contab:Object.freeze({screen:'contab',primary:'forex'}),
  fxplan:Object.freeze({screen:'fxplan',primary:'forex',localView:Object.freeze({surface:'fxplan',view:'@current'})}),
  motor:Object.freeze({screen:'exec',primary:'forex',localView:Object.freeze({surface:'exec',view:'motor'})}),
  params:Object.freeze({action:'settings',leaf:'tool-params'}),
  check:Object.freeze({action:'settings',leaf:'tool-check'}),
  config:Object.freeze({action:'settings',leaf:'about'})
});

const NAV_LOCAL_SURFACES=Object.freeze({
  exec:Object.freeze({screen:'exec',primary:'forex',views:Object.freeze(['overview','panel','ecal','nocoda','pivots','motor','history']),resolve:()=>window.JPWExec&&window.JPWExec.ui}),
  finpes:Object.freeze({screen:'finpes',primary:'personal-finance',views:Object.freeze(['overview','mensal','dividas','comparativo','cenarios']),resolve:()=>window.JPWFin&&window.JPWFin.ui}),
  fxplan:Object.freeze({screen:'fxplan',primary:'forex',views:Object.freeze(['overview','planning','actuals','table']),resolve:()=>window.JPWFx&&window.JPWFx.ui})
});

const NAV_ROUTE_BY_ID=Object.freeze(Object.fromEntries(NAV_CANONICAL_ROUTES.map(route=>[route.id,route])));
const NAV_ROUTE_BY_ALIAS=Object.freeze(Object.fromEntries(NAV_CANONICAL_ROUTES.flatMap(route=>route.aliases.map(alias=>[alias,route]))));
let navCurrent={canonical:'dashboard',requested:'dashboard',source:'canonical',primary:'dashboard',screen:'dash',localView:null};
let navLastResult={accepted:true,reason:null};

function navPublicRoute(route){
  return {id:route.id,primary:route.primary,screen:route.screen,
    localView:route.localView?{surface:route.localView.surface,view:route.localView.view}:null,
    aliases:[...route.aliases]};
}

function navPublicResolution(plan){
  if(!plan.accepted) return {accepted:false,requested:plan.requested,reason:plan.reason};
  return {accepted:true,requested:plan.requested,source:plan.source,
    canonical:plan.canonical||null,primary:plan.primary||null,screen:plan.screen||null,
    localView:plan.localView?{surface:plan.localView.surface,view:plan.localView.view}:null,
    action:plan.action||null,leaf:plan.leaf||null};
}

function navResolve(target){
  const requested=typeof target==='string'?target:
    (target&&target.dataset?(target.dataset.route||target.dataset.screen):null);
  if(!requested) return {accepted:false,requested:null,reason:'missing-target'};
  const canonical=NAV_ROUTE_BY_ID[requested];
  if(canonical) return {accepted:true,requested,source:'canonical',canonical:canonical.id,
    primary:canonical.primary,screen:canonical.screen,localView:canonical.localView};
  const aliased=NAV_ROUTE_BY_ALIAS[requested];
  if(aliased) return {accepted:true,requested,source:'alias',canonical:aliased.id,
    primary:aliased.primary,screen:aliased.screen,localView:aliased.localView};
  const compatibility=NAV_COMPATIBILITY_TARGETS[requested];
  if(compatibility) return {accepted:true,requested,source:'compatibility',canonical:null,
    primary:compatibility.primary||null,screen:compatibility.screen||null,
    localView:compatibility.localView||null,action:compatibility.action||null,leaf:compatibility.leaf||null};
  return {accepted:false,requested,reason:'unknown-target'};
}

function navSurface(surfaceId){
  const descriptor=NAV_LOCAL_SURFACES[surfaceId];
  return descriptor&&typeof descriptor.resolve==='function'?descriptor.resolve():null;
}

function navCanApply(plan){
  if(!plan.accepted) return false;
  if(plan.action==='settings') return typeof openSettingsModal==='function';
  if(!plan.screen||!document.getElementById(plan.screen)) return false;
  if(plan.primary&&!document.querySelector('#nav > .tab[data-primary="'+CSS.escape(plan.primary)+'"]')) return false;
  if(plan.localView){
    const descriptor=NAV_LOCAL_SURFACES[plan.localView.surface];
    const surface=navSurface(plan.localView.surface);
    const view=plan.localView.view==='@current'&&surface&&typeof surface.getView==='function'
      ? surface.getView():plan.localView.view;
    if(!descriptor||!surface||typeof surface.selectView!=='function'||!descriptor.views.includes(view)) return false;
  }
  return true;
}

function navSelectPrimary(primary){
  document.querySelectorAll('#nav > .tab[data-primary]').forEach(tab=>{
    const active=tab.dataset.primary===primary;
    tab.classList.toggle('active',active);
    if(active) tab.setAttribute('aria-current','page');
    else tab.removeAttribute('aria-current');
  });
}

function navApply(plan,target){
  if(!navCanApply(plan)){
    navLastResult={accepted:false,reason:plan.accepted?'unavailable-target':plan.reason};
    return false;
  }
  if(plan.action==='settings'){
    const opener=typeof target==='string'
      ?(document.activeElement instanceof HTMLElement?document.activeElement:undefined):target;
    openSettingsModal(plan.leaf,opener);
    navLastResult={accepted:true,reason:null};
    return true;
  }
  const localView=plan.localView?{surface:plan.localView.surface,view:plan.localView.view}:null;
  if(localView&&localView.view==='@current'){
    const surface=navSurface(localView.surface);
    localView.view=surface.getView();
  }
  document.querySelectorAll('#appMain > .screen').forEach(screen=>screen.classList.remove('active'));
  document.getElementById(plan.screen).classList.add('active');
  navSelectPrimary(plan.primary);
  if(localView) navSurface(localView.surface).selectView(localView.view);
  navCurrent={canonical:plan.canonical||null,requested:plan.requested,source:plan.source,
    primary:plan.primary,screen:plan.screen,localView};
  navLastResult={accepted:true,reason:null};
  if(typeof scheduleNavPill==='function') scheduleNavPill();
  window.scrollTo({top:0,behavior:'smooth'});
  if(typeof maybeShowOnboardingNavReminder==='function') maybeShowOnboardingNavReminder(plan.screen);
  return true;
}

// Fachada legada preservada. A resolução/validação inteira acontece antes da
// remoção de qualquer classe; alvo desconhecido falha fechado e sem drift.
function navigateToScreen(target){
  const plan=navResolve(target);
  return navApply(plan,target);
}

function navNavigate(target){
  navLastResult={accepted:false,reason:'not-applied'};
  // Chama a fachada global corrente para atravessar wrappers visuais existentes.
  navigateToScreen(target);
  return navLastResult.accepted===true;
}

function navNavigateLocal(surfaceId,view){
  const descriptor=NAV_LOCAL_SURFACES[surfaceId];
  const surface=navSurface(surfaceId);
  if(!descriptor||!descriptor.views.includes(view)||!surface||typeof surface.selectView!=='function') return false;
  const canonical=surfaceId==='exec'&&view==='overview'?'forex-overview':
    (surfaceId==='finpes'&&view==='overview'?'personal-finance':null);
  const plan={accepted:true,requested:surfaceId+':'+view,source:canonical?'canonical':'compatibility',
    canonical,primary:descriptor.primary,screen:descriptor.screen,localView:{surface:surfaceId,view}};
  navLastResult={accepted:false,reason:'not-applied'};
  navApply(plan,surfaceId);
  if(typeof syncActiveScreen==='function') syncActiveScreen();
  return navLastResult.accepted===true;
}

function navFocusCurrentScreen(){
  const screen=document.querySelector('#appMain > .screen.active');
  if(!screen) return false;
  const target=screen.querySelector('[data-route-focus],h1,h2');
  if(!target) return false;
  if(!target.hasAttribute('tabindex')) target.setAttribute('tabindex','-1');
  target.focus({preventScroll:true});
  return document.activeElement===target;
}

window.JPWNavigation=Object.freeze({
  routes:()=>NAV_CANONICAL_ROUTES.map(navPublicRoute),
  resolve:target=>navPublicResolution(navResolve(target)),
  navigate:navNavigate,
  navigateLocal:navNavigateLocal,
  current:()=>({canonical:navCurrent.canonical,requested:navCurrent.requested,source:navCurrent.source,
    primary:navCurrent.primary,screen:navCurrent.screen,
    localView:navCurrent.localView?{...navCurrent.localView}:null}),
  focusCurrentScreen:navFocusCurrentScreen
});

document.querySelectorAll('#nav > .tab[data-route]').forEach(tab=>
  tab.addEventListener('click',()=>navigateToScreen(tab)));
navSelectPrimary('dashboard');
const fxUpdateButton=document.getElementById('fxUpdateBtn');
if(fxUpdateButton) fxUpdateButton.addEventListener('click',()=>updateFxRates());
