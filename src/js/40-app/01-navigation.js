// ============ NAVEGAÇÃO SEMÂNTICA (NAV-01 · N1) ============
// O contrato público global tem exatamente cinco rotas canônicas. Forex expõe
// seis filhos e Research cinco; owner semântico, filho, section física e visão
// local são dimensões separadas. Navegação é estado efêmero de UI; este módulo
// não persiste preferência, tela ou visão local.

const NAV_FOREX_CHILDREN=Object.freeze([
  Object.freeze({id:'forex-overview',label:'Visão Geral',primary:'forex',child:'forex-overview',screen:'exec',localView:Object.freeze({surface:'exec',view:'overview'}),aliases:Object.freeze(['exec'])}),
  Object.freeze({id:'forex-preparation',label:'Preparação',primary:'forex',child:'forex-preparation',screen:'check',localView:null,aliases:Object.freeze([])}),
  Object.freeze({id:'forex-account',label:'Conta',primary:'forex',child:'forex-account',screen:'contas',localView:null,aliases:Object.freeze([])}),
  Object.freeze({id:'forex-operation',label:'Operação',primary:'forex',child:'forex-operation',screen:'exec',localView:Object.freeze({surface:'exec',view:'panel'}),aliases:Object.freeze([])}),
  Object.freeze({id:'forex-reconciliation',label:'Apuração',primary:'forex',child:'forex-reconciliation',screen:'contab',localView:null,aliases:Object.freeze([])}),
  Object.freeze({id:'forex-planning',label:'Planejamento',primary:'forex',child:'forex-planning',screen:'fxplan',localView:Object.freeze({surface:'fxplan',view:'overview'}),aliases:Object.freeze([])})
]);

const NAV_RESEARCH_CHILDREN=Object.freeze([
  Object.freeze({id:'research-forex',label:'Forex',primary:'research',child:'research-forex',screen:'research',localView:Object.freeze({surface:'research',view:'calendar'}),aliases:Object.freeze([])}),
  Object.freeze({id:'research-stocks-br',label:'Ações',primary:'research',child:'research-stocks-br',screen:'research',localView:Object.freeze({surface:'research',view:'stocks-br'}),aliases:Object.freeze([])}),
  Object.freeze({id:'research-stocks-global',label:'Stocks',primary:'research',child:'research-stocks-global',screen:'research',localView:Object.freeze({surface:'research',view:'stocks-global'}),aliases:Object.freeze([])}),
  Object.freeze({id:'research-reits',label:'REITs',primary:'research',child:'research-reits',screen:'research',localView:Object.freeze({surface:'research',view:'reits'}),aliases:Object.freeze([])}),
  Object.freeze({id:'research-others',label:'Others',primary:'research',child:'research-others',screen:'research',localView:Object.freeze({surface:'research',view:'others'}),aliases:Object.freeze([])})
]);

const NAV_CANONICAL_ROUTES=Object.freeze([
  Object.freeze({id:'dashboard',primary:'dashboard',screen:'dash',localView:null,aliases:Object.freeze(['dash'])}),
  NAV_FOREX_CHILDREN[0],
  Object.freeze({id:'personal-finance',primary:'personal-finance',screen:'finpes',localView:Object.freeze({surface:'finpes',view:'overview'}),aliases:Object.freeze(['finpes'])}),
  NAV_RESEARCH_CHILDREN[0],
  Object.freeze({id:'alladin',primary:'alladin',screen:'alladin',localView:null,aliases:Object.freeze([])})
]);

// Destinos legados. Saber resolvê-los não os promove a rotas primárias: as três
// ferramentas analíticas pertencem semanticamente a Research / Forex.
const NAV_COMPATIBILITY_TARGETS=Object.freeze({
  contas:Object.freeze({canonical:'forex-account',child:'forex-account',screen:'contas',primary:'forex'}),
  contab:Object.freeze({canonical:'forex-reconciliation',child:'forex-reconciliation',screen:'contab',primary:'forex'}),
  fxplan:Object.freeze({canonical:'forex-planning',child:'forex-planning',screen:'fxplan',primary:'forex',localView:Object.freeze({surface:'fxplan',view:'@current'})}),
  motor:Object.freeze({canonical:'forex-operation',child:'forex-operation',screen:'exec',primary:'forex',localView:Object.freeze({surface:'exec',view:'motor'})}),
  history:Object.freeze({canonical:'forex-reconciliation',child:'forex-reconciliation',screen:'exec',primary:'forex',localView:Object.freeze({surface:'exec',view:'history'})}),
  check:Object.freeze({canonical:'forex-preparation',child:'forex-preparation',screen:'check',primary:'forex'}),
  'tool-check':Object.freeze({action:'settings',leaf:'tool-check'}),
  ecal:Object.freeze({canonical:'research-forex',child:'research-forex',screen:'research',primary:'research',localView:Object.freeze({surface:'research',view:'calendar'})}),
  nocoda:Object.freeze({canonical:'research-forex',child:'research-forex',screen:'research',primary:'research',localView:Object.freeze({surface:'research',view:'nocoda'})}),
  pivots:Object.freeze({canonical:'research-forex',child:'research-forex',screen:'research',primary:'research',localView:Object.freeze({surface:'research',view:'pivots'})}),
  params:Object.freeze({action:'settings',leaf:'tool-params'}),
  config:Object.freeze({action:'settings',leaf:'about'})
});

const NAV_LOCAL_SURFACES=Object.freeze({
  exec:Object.freeze({screen:'exec',primary:'forex',views:Object.freeze(['overview','panel','motor','history']),resolve:()=>window.JPWExec&&window.JPWExec.ui}),
  finpes:Object.freeze({screen:'finpes',primary:'personal-finance',views:Object.freeze(['overview','mensal','dividas','comparativo','cenarios']),resolve:()=>window.JPWFin&&window.JPWFin.ui}),
  fxplan:Object.freeze({screen:'fxplan',primary:'forex',views:Object.freeze(['overview','planning','actuals','table']),resolve:()=>window.JPWFx&&window.JPWFx.ui}),
  research:Object.freeze({screen:'research',primary:'research',views:Object.freeze(['calendar','nocoda','pivots','stocks-br','stocks-global','reits','others']),resolve:()=>window.JPWResearch&&window.JPWResearch.ui})
});

const NAV_ROUTE_BY_ID=Object.freeze(Object.fromEntries(
  [...NAV_CANONICAL_ROUTES,...NAV_FOREX_CHILDREN,...NAV_RESEARCH_CHILDREN].map(route=>[route.id,route])));
const NAV_ROUTE_BY_ALIAS=Object.freeze(Object.fromEntries(NAV_CANONICAL_ROUTES.flatMap(route=>route.aliases.map(alias=>[alias,route]))));
let navCurrent={canonical:'dashboard',requested:'dashboard',source:'canonical',primary:'dashboard',child:null,screen:'dash',localView:null};
let navLastResult={accepted:true,reason:null};

function navPublicRoute(route){
  return {id:route.id,label:route.label||null,primary:route.primary,child:route.child||null,screen:route.screen,
    localView:route.localView?{surface:route.localView.surface,view:route.localView.view}:null,
    aliases:[...route.aliases]};
}

function navPublicResolution(plan){
  if(!plan.accepted) return {accepted:false,requested:plan.requested,reason:plan.reason};
  return {accepted:true,requested:plan.requested,source:plan.source,
    canonical:plan.canonical||null,primary:plan.primary||null,child:plan.child||null,screen:plan.screen||null,
    localView:plan.localView?{surface:plan.localView.surface,view:plan.localView.view}:null,
    action:plan.action||null,leaf:plan.leaf||null};
}

function navResolve(target){
  const requested=typeof target==='string'?target:
    (target&&target.dataset?(target.dataset.route||target.dataset.screen):null);
  if(!requested) return {accepted:false,requested:null,reason:'missing-target'};
  const canonical=NAV_ROUTE_BY_ID[requested];
  if(canonical) return {accepted:true,requested,source:'canonical',canonical:canonical.id,
    primary:canonical.primary,child:canonical.child||null,screen:canonical.screen,localView:canonical.localView};
  const aliased=NAV_ROUTE_BY_ALIAS[requested];
  if(aliased) return {accepted:true,requested,source:'alias',canonical:aliased.id,
    primary:aliased.primary,child:aliased.child||null,screen:aliased.screen,localView:aliased.localView};
  const compatibility=NAV_COMPATIBILITY_TARGETS[requested];
  if(compatibility) return {accepted:true,requested,source:'compatibility',canonical:compatibility.canonical||null,
    primary:compatibility.primary||null,child:compatibility.child||null,screen:compatibility.screen||null,
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
    primary:plan.primary,child:plan.child||null,screen:plan.screen,localView};
  navLastResult={accepted:true,reason:null};
  if(typeof scheduleNavPill==='function') scheduleNavPill();
  window.scrollTo({top:0,behavior:'smooth'});
  if(typeof maybeShowOnboardingNavReminder==='function') maybeShowOnboardingNavReminder(plan.screen);
  if(typeof syncNavSubState==='function') syncNavSubState();
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
    (surfaceId==='exec'&&(view==='panel'||view==='motor')?'forex-operation':
    (surfaceId==='exec'&&view==='history'?'forex-reconciliation':
    (surfaceId==='fxplan'?'forex-planning':
    (surfaceId==='finpes'&&view==='overview'?'personal-finance':
    (surfaceId==='research'&&(view==='calendar'||view==='nocoda'||view==='pivots')?'research-forex':
    (surfaceId==='research'&&view==='stocks-br'?'research-stocks-br':
    (surfaceId==='research'&&view==='stocks-global'?'research-stocks-global':
    (surfaceId==='research'&&view==='reits'?'research-reits':
    (surfaceId==='research'&&view==='others'?'research-others':null)))))))));
  const child=canonical&&(canonical.startsWith('forex-')||canonical.startsWith('research-'))?canonical:null;
  const plan={accepted:true,requested:surfaceId+':'+view,source:canonical?'local':'compatibility',
    canonical,primary:descriptor.primary,child,screen:descriptor.screen,localView:{surface:surfaceId,view}};
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
  children:primary=>primary==='forex'?NAV_FOREX_CHILDREN.map(navPublicRoute):
    (primary==='research'?NAV_RESEARCH_CHILDREN.map(navPublicRoute):[]),
  resolve:target=>navPublicResolution(navResolve(target)),
  navigate:navNavigate,
  navigateLocal:navNavigateLocal,
  current:()=>({canonical:navCurrent.canonical,requested:navCurrent.requested,source:navCurrent.source,
    primary:navCurrent.primary,child:navCurrent.child,screen:navCurrent.screen,
    localView:navCurrent.localView?{...navCurrent.localView}:null}),
  focusCurrentScreen:navFocusCurrentScreen
});

// A marca entra no MESMO seletor dos primarios: um segundo caminho de navegacao
// seria uma segunda verdade sobre o que "ir para o dashboard" significa, e as
// duas divergiriam na primeira mudanca de rota. Enter e Espaco vem de graca
// porque o elemento e um <button>.
document.querySelectorAll('#nav > .tab[data-route], .brand-home[data-route]').forEach(control=>
  control.addEventListener('click',()=>navigateToScreen(control)));
navSelectPrimary('dashboard');
const fxUpdateButton=document.getElementById('fxUpdateBtn');
if(fxUpdateButton) fxUpdateButton.addEventListener('click',()=>updateFxRates());
