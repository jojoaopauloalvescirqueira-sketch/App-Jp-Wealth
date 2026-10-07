// Shell de apresentação sobre o resolver existente. A composição é uma
// preferência por navegador; não participa do estado ou do backup financeiro.
const shellUI = { open:false, opener:null, inerted:[], overflow:'', forexSubHome:null };
let shellNavigationIntent=null,shellNavigationSerial=0;
const navSubUI = { open:false, pinned:false, screen:null, collapsed:null, opener:null };
const submenuUI = { level:1, surface:null, context:null, openers:[], temporary:false, direction:'forward' };
// var permite que o bootstrap do bundle portátil consulte a prontidão sem TDZ.
var sidebarControllerReady=false;
// Disclosure da lateral é apresentação transitória. A rota continua sendo a
// única fonte da seleção; nenhum hover passa pelo resolver ou pelo domínio.
const sidebarUI = { route:null, pinned:null, preview:null, overlay:false, overlayPinned:false,
  suppressed:null, target:null, pointer:null, paintedAt:null, mobile:null, pointerDown:false,
  hoverTimer:null, leaveTimer:null, closeTimer:null };
const SIDEBAR_TIMING=Object.freeze({open:400,leave:300,motion:180});
const SUBMENU_CONTEXTS=new Set(['forex-management-accounts','forex-planning','research-forex']);
const SUBMENU_TITLES=Object.freeze({
  exec:'Forex',finpes:'Finanças Pessoais',research:'Research',tools:'Ferramentas e Serviços',
  'forex-management-accounts':'Contas e Períodos','forex-planning':'Planejamento patrimonial','research-forex':'Forex'
});
const NAV_SUBMENU_SURFACES = {
  exec:()=>window.JPWExec&&window.JPWExec.ui,
  finpes:()=>window.JPWFin&&window.JPWFin.ui,
  research:()=>window.JPWResearch&&window.JPWResearch.ui,
  tools:()=>window.JPWTools&&window.JPWTools.ui
};
function shellEl(sel){return document.querySelector(sel);}
function shellMobile(){return window.matchMedia('(max-width:900px)').matches;}
function shellTopbar(){return document.documentElement.getAttribute('data-navigation')==='topbar';}
function shellGlass(){return document.documentElement.getAttribute('data-navigation')==='glass';}
function shellSubmenu(){return document.documentElement.getAttribute('data-navigation')==='submenu';}
function shellHorizontal(){return shellTopbar()||shellGlass();}
function shellCompact(){return shellGlass()?window.matchMedia('(max-width:1179px)').matches:shellMobile();}
function shellMenuRoot(){return shellGlass()?document.querySelector('body > header'):document.getElementById(shellTopbar()?'nav':'appSidebar');}
function shellModalOpen(){return !!document.querySelector('#settingsOverlay.show,#mvpNotesOverlay.show');}
function shellSidebar(){return document.documentElement.getAttribute('data-navigation')==='sidebar';}
function sidebarBlocked(){
  return !!document.querySelector('#settingsOverlay.show,#mvpNotesOverlay.show,#modalOverlay.show,#alladinModalOverlay.show,#ecalOverlay.show,dialog[open]');
}
function sidebarCollapsed(){return !shellMobile()&&document.documentElement.getAttribute('data-rail')==='collapsed';}
function sidebarPrimary(surface){return document.querySelector('#nav > [data-nav-surface="'+surface+'"]');}
function sidebarSurfaceForRoute(current){
  return shellModuleAvailable(current.primary)?({forex:'exec','personal-finance':'finpes',research:'research',tools:'tools'})[current.primary]||null:null;
}
function sidebarClearTimers(){
  clearTimeout(sidebarUI.hoverTimer);clearTimeout(sidebarUI.leaveTimer);clearTimeout(sidebarUI.closeTimer);
  sidebarUI.hoverTimer=null;sidebarUI.leaveTimer=null;sidebarUI.closeTimer=null;sidebarUI.target=null;
}
function sidebarMoveRailToOwner(){
  const rail=document.getElementById('railToggle');
  if(!rail||rail.closest('#settingsRailSlot'))return;
  const owner=shellSidebar()?document.querySelector('.sidebar-heading'):document.getElementById('appSidebar');
  if(rail.parentElement!==owner){
    if(shellSidebar())owner.append(rail);
    else owner.insertBefore(rail,owner.querySelector('.sidebar-footer'));
  }
}
function sidebarMeasure(){
  if(!shellSidebar())return;
  const aside=document.getElementById('appSidebar'),header=document.querySelector('body > header');
  if(!aside||!header)return;
  // O header pode quebrar em linhas e sair do viewport durante a rolagem.
  const top=Math.max(0,Math.min(innerHeight,header.getBoundingClientRect().bottom));
  const height=Math.max(0,innerHeight-top);
  aside.style.setProperty('--sidebar-available-height',height+'px');
  aside.style.setProperty('--sidebar-overlay-top',top+'px');
  aside.style.setProperty('--sidebar-overlay-height',height+'px');
}
function sidebarMarkCurrent(){
  const current=window.JPWNavigation.current(),active=sidebarSurfaceForRoute(current);
  document.querySelectorAll('#navSubShell [data-nav-item],#navSubShell [data-nav-sub-view],#navLocalSlot [data-nav-item]').forEach(item=>{
    const panel=item.closest('.nav-sub-menu'),host=item.closest('.nav-sub-contexts');
    const owner=(panel?.id.replace('NavSubmenu','')||host?.id.replace('NavContexts',''));
    const on=owner===active&&(item.dataset.navChild?item.dataset.navChild===current.child:
      item.dataset.navRoute?navSubRouteIsCurrent(item,current):
      item.dataset.navLocalView?!!current.localView&&item.dataset.navLocalSurface===current.localView.surface&&item.dataset.navLocalView===current.localView.view:
      item.dataset.navSubView===navSubSurface(active)?.getView());
    item.classList.toggle('is-current',on);
    if(on)item.setAttribute('aria-current','page');else item.removeAttribute('aria-current');
    item.tabIndex=0; // disclosure navigation: todos os destinos visíveis recebem Tab.
  });
  document.querySelectorAll('#nav > .tab').forEach(tab=>{
    if(tab.dataset.navSurface)tab.removeAttribute('aria-current');
    tab.tabIndex=0;
  });
}
function sidebarPaint(options={}){
  if(!shellSidebar())return;
  const root=document.documentElement,shell=document.getElementById('navSubShell');
  const surface=sidebarUI.preview||sidebarUI.pinned;
  const visible=!!surface&&!sidebarBlocked()&&(!sidebarCollapsed()||sidebarUI.overlay);
  const previous=navSubUI.open?navSubUI.screen:null;
  clearTimeout(sidebarUI.closeTimer);sidebarUI.closeTimer=null;
  root.removeAttribute('data-sidebar-closing');
  if(sidebarUI.overlay&&sidebarCollapsed()&&!sidebarBlocked())root.setAttribute('data-sidebar-overlay','true');
  else root.removeAttribute('data-sidebar-overlay');
  if(visible)root.setAttribute('data-sidebar-group',surface);else root.removeAttribute('data-sidebar-group');
  navSubUI.screen=visible?surface:null;navSubUI.open=visible;
  document.querySelectorAll('[data-nav-expand]').forEach(btn=>{btn.hidden=true;btn.setAttribute('aria-expanded','false');});
  document.querySelectorAll('#nav > .tab').forEach(tab=>{
    const group=tab.dataset.navSurface,opened=visible&&group===surface;
    tab.classList.toggle('sidebar-group-open',opened);
    if(group){tab.setAttribute('aria-expanded',String(opened));tab.setAttribute('aria-controls',group+'NavSubmenu');}
    else{tab.removeAttribute('aria-expanded');tab.removeAttribute('aria-controls');}
    tab.removeAttribute('aria-haspopup');
  });
  const motion=matchMedia('(prefers-reduced-motion:reduce)').matches?0:SIDEBAR_TIMING.motion;
  const closing=previous&&!visible&&!options.immediate&&motion>0&&!sidebarBlocked();
  document.querySelectorAll('.nav-sub-menu').forEach(panel=>{
    const on=visible&&panel.id===surface+'NavSubmenu';
    const fading=closing&&panel.id===previous+'NavSubmenu';
    panel.hidden=!(on||fading);panel.inert=!on;panel.setAttribute('aria-hidden',String(!on));
  });
  if(visible){
    const parent=sidebarPrimary(surface);
    if(parent&&parent.nextElementSibling!==shell)parent.after(shell);
  }
  shell.hidden=!(visible||closing);shell.inert=!visible;shell.classList.toggle('is-open',visible);
  if(visible)root.setAttribute('data-nav-sub','open');else root.removeAttribute('data-nav-sub');
  if(closing){
    root.setAttribute('data-sidebar-closing','true');
    sidebarUI.closeTimer=setTimeout(()=>{
      root.removeAttribute('data-sidebar-closing');shell.hidden=true;
      document.querySelectorAll('.nav-sub-menu').forEach(panel=>{panel.hidden=true;});
      sidebarUI.closeTimer=null;
    },motion);
  }
  // A assinatura de seleção e o N3 não são atualizados pelo grupo explorado.
  sidebarMarkCurrent();sidebarMoveRailToOwner();sidebarMeasure();
  sidebarUI.paintedAt=sidebarUI.pointer&&{...sidebarUI.pointer};
}
function sidebarSyncRoute(){
  const current=window.JPWNavigation.current();
  const stamp=JSON.stringify([current.canonical,current.primary,current.child,current.localView]);
  if(sidebarUI.route!==stamp){
    sidebarClearTimers();sidebarUI.route=stamp;sidebarUI.pinned=sidebarSurfaceForRoute(current);
    sidebarUI.preview=null;sidebarUI.overlay=false;sidebarUI.overlayPinned=false;sidebarUI.suppressed=null;
  }
  syncNavSubContexts(sidebarSurfaceForRoute(current));
  sidebarPaint({immediate:true});syncShellLocation();syncForexContext();syncShellViewport();
}
function sidebarCancelExploration(options={}){
  sidebarClearTimers();sidebarUI.preview=null;sidebarUI.overlay=false;sidebarUI.overlayPinned=false;
  if(options.clearPin)sidebarUI.pinned=null;
  if(shellSidebar())sidebarPaint({immediate:!!options.immediate});
  else{
    document.documentElement.removeAttribute('data-sidebar-overlay');
    document.documentElement.removeAttribute('data-sidebar-group');
    document.documentElement.removeAttribute('data-sidebar-closing');
    document.querySelectorAll('#nav > .tab').forEach(tab=>tab.classList.remove('sidebar-group-open'));
  }
}
function sidebarFocusInPanel(){return !!document.activeElement?.closest('#navSubShell');}
function sidebarEndPreview(){
  if(sidebarFocusInPanel()||sidebarBlocked())return;
  sidebarUI.preview=null;
  if(!sidebarUI.overlayPinned){sidebarUI.overlay=false;}
  sidebarPaint();
}
function sidebarScheduleLeave(){
  clearTimeout(sidebarUI.hoverTimer);sidebarUI.hoverTimer=null;sidebarUI.target=null;
  clearTimeout(sidebarUI.leaveTimer);
  sidebarUI.leaveTimer=setTimeout(sidebarEndPreview,SIDEBAR_TIMING.leave);
}
function sidebarOpenSurface(surface,options={}){
  if(!shellSidebar()||sidebarBlocked()||!Object.prototype.hasOwnProperty.call(NAV_SUBMENU_SURFACES,surface)||!shellModuleAvailable(submenuPrimaryForSurface(surface)))return false;
  sidebarClearTimers();sidebarUI.suppressed=null;
  if(options.pin){sidebarUI.pinned=surface;sidebarUI.preview=null;}
  else sidebarUI.preview=surface;
  if(sidebarCollapsed()){sidebarUI.overlay=true;sidebarUI.overlayPinned=!!options.pin;}
  sidebarPaint();
  if(options.focus){
    const panel=document.getElementById(surface+'NavSubmenu');
    const items=[...panel.querySelectorAll('[data-nav-item],[data-nav-sub-view]')].filter(shellFocusAvailable);
    (options.focus==='last'?items[items.length-1]:items[0])?.focus();
  }
  return true;
}
function sidebarToggleSurface(control){
  const surface=control.dataset.navSurface;
  if(!shellRequireModule(control.dataset.primary,control))return true;
  if(sidebarUI.pinned===surface&&!sidebarUI.preview&&navSubUI.open){
    sidebarUI.suppressed=surface;sidebarCancelExploration({clearPin:true});
  }else sidebarOpenSurface(surface,{pin:true});
  return true;
}
function sidebarHandleKey(event){
  if(!shellSidebar()||sidebarBlocked())return false;
  const primary=event.target.closest('#nav > .tab'),item=event.target.closest('#navSubShell [data-nav-item],#navSubShell [data-nav-sub-view]');
  const local=event.target.closest('#navLocalSlot');
  if(event.key==='Escape'&&!shellMobile()&&(sidebarUI.overlay||sidebarUI.preview||navSubUI.open)){
    const parent=sidebarPrimary(navSubUI.screen),inPanel=!!item;
    const restorePin=!!sidebarUI.preview||sidebarUI.overlay;
    event.preventDefault();sidebarUI.suppressed=sidebarUI.preview||sidebarUI.pinned;
    // Focar antes de ocultar evita foco perdido no corpo da página.
    if(inPanel&&parent)parent.focus({preventScroll:true});
    sidebarCancelExploration({clearPin:!restorePin});return true;
  }
  if(primary?.dataset.navSurface&&event.key==='ArrowRight'){
    event.preventDefault();sidebarOpenSurface(primary.dataset.navSurface,{pin:true,focus:true});return true;
  }
  if(item&&event.key==='ArrowLeft'){
    event.preventDefault();sidebarPrimary(navSubUI.screen)?.focus({preventScroll:true});return true;
  }
  if(!(primary||item||local)||!['ArrowDown','ArrowUp','Home','End'].includes(event.key))return false;
  const region=local||item?.closest('.nav-sub-menu')||document.getElementById('nav');
  const items=[...region.querySelectorAll('.tab,[data-nav-item],[data-nav-sub-view]')].filter(shellFocusAvailable);
  if(!items.length)return false;
  let index=items.indexOf(document.activeElement);
  if(event.key==='Home')index=0;else if(event.key==='End')index=items.length-1;
  else index=(index+(event.key==='ArrowDown'?1:-1)+items.length)%items.length;
  event.preventDefault();items[index].focus();return true;
}
function initSidebarExploration(){
  const aside=document.getElementById('appSidebar'),nav=document.getElementById('nav');
  sidebarControllerReady=true;
  sidebarUI.mobile=shellMobile();
  nav.addEventListener('pointermove',event=>{
    if(!shellSidebar()||shellMobile()||sidebarBlocked()||event.pointerType==='touch'||!matchMedia('(hover:hover) and (pointer:fine)').matches)return;
    const point={x:event.clientX,y:event.clientY},last=sidebarUI.pointer;sidebarUI.pointer=point;
    if(last&&point.x===last.x&&point.y===last.y)return;
    // Reflow abaixo do cursor não é uma nova intenção. Só movimento real
    // suficiente depois da abertura habilita exploração de outro grupo.
    if(sidebarUI.paintedAt&&Math.hypot(point.x-sidebarUI.paintedAt.x,point.y-sidebarUI.paintedAt.y)<4)return;
    clearTimeout(sidebarUI.leaveTimer);
    const parent=event.target.closest('#nav > .tab');
    if(!parent){clearTimeout(sidebarUI.hoverTimer);sidebarUI.target=null;return;}
    const surface=parent.dataset.navSurface||null;
    if(sidebarUI.suppressed&&sidebarUI.suppressed!==surface)sidebarUI.suppressed=null;
    if(sidebarUI.suppressed===surface&&surface)return;
    if(!shellModuleAvailable(parent.dataset.primary)||sidebarFocusInPanel())return;
    if(sidebarUI.target===parent)return;
    clearTimeout(sidebarUI.hoverTimer);sidebarUI.target=parent;
    sidebarUI.hoverTimer=setTimeout(()=>{
      sidebarUI.hoverTimer=null;
      if(!shellSidebar()||shellMobile()||sidebarBlocked()||!parent.matches(':hover')||sidebarUI.target!==parent||sidebarFocusInPanel())return;
      sidebarUI.target=null;
      if(surface)sidebarOpenSurface(surface);
      else if(sidebarCollapsed()){sidebarUI.preview=null;sidebarUI.overlay=true;sidebarPaint();}
      else sidebarEndPreview();
    },SIDEBAR_TIMING.open);
  });
  nav.addEventListener('pointerleave',()=>{
    if(!shellSidebar()||sidebarBlocked())return;
    sidebarUI.suppressed=null;sidebarScheduleLeave();
  });
  aside.addEventListener('pointerenter',()=>{if(shellSidebar())clearTimeout(sidebarUI.leaveTimer);});
  aside.addEventListener('pointerleave',()=>{
    if(shellSidebar()&&!sidebarBlocked()){
      sidebarUI.suppressed=null;sidebarUI.pointer=null;sidebarUI.paintedAt=null;
      sidebarScheduleLeave();
    }
  });
  aside.addEventListener('focusin',()=>{
    if(!shellSidebar()||sidebarBlocked())return;
    clearTimeout(sidebarUI.leaveTimer);
    // Foco produzido pelo pointerdown não pode mover o alvo antes do click.
    if(sidebarCollapsed()&&!sidebarUI.overlay&&!sidebarUI.pointerDown){sidebarUI.overlay=true;sidebarPaint();}
  });
  aside.addEventListener('focusout',()=>{
    setTimeout(()=>{
      if(!shellSidebar()||aside.contains(document.activeElement)||sidebarBlocked())return;
      if(sidebarUI.overlay)sidebarCancelExploration();else sidebarEndPreview();
    },0);
  });
  document.addEventListener('pointerdown',event=>{
    sidebarUI.pointerDown=aside.contains(event.target);
    if(shellSidebar()&&!sidebarBlocked()&&sidebarUI.overlay&&!aside.contains(event.target))sidebarCancelExploration({immediate:true});
  });
  document.addEventListener('pointerup',()=>setTimeout(()=>{sidebarUI.pointerDown=false;},0));
  document.addEventListener('pointercancel',()=>{sidebarUI.pointerDown=false;});
  let lastBlocked=false;
  const observeModal=()=>{
    const blocked=sidebarBlocked();
    if(blocked===lastBlocked)return;lastBlocked=blocked;
    // Uma confirmação pode recusar a navegação. Suspender a apresentação sem
    // destruir sua seleção; uma rota aceita já invalida o contexto anterior.
    sidebarClearTimers();
    if(shellSidebar()){sidebarPaint({immediate:true});sidebarMoveRailToOwner();sidebarMeasure();}
  };
  const observer=new MutationObserver(observeModal);
  const modalSelector='#settingsOverlay,#mvpNotesOverlay,#modalOverlay,#alladinModalOverlay,#ecalOverlay,dialog';
  const observedModals=new WeakSet();
  const attachModals=host=>{
    const nodes=[...(host.matches?.(modalSelector)?[host]:[]),...host.querySelectorAll(modalSelector)];
    nodes.forEach(el=>{
      if(observedModals.has(el))return;observedModals.add(el);
      observer.observe(el,{attributes:true,attributeFilter:['class','open']});
    });
    observeModal();
  };
  // O parser e os guards podem acrescentar dialogs depois da inicialização.
  // Observar apenas filhos diretos do body evita monitorar árvores financeiras.
  new MutationObserver(records=>records.forEach(record=>record.addedNodes.forEach(node=>{
    if(node.nodeType===Node.ELEMENT_NODE)attachModals(node);
  }))).observe(document.body,{childList:true});
  attachModals(document);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>attachModals(document),{once:true});
  const header=document.querySelector('body > header');
  if(header&&typeof ResizeObserver==='function')new ResizeObserver(sidebarMeasure).observe(header);
  window.addEventListener('scroll',sidebarMeasure,{passive:true});
}
// Retorno das superfícies do cabeçalho: não selecionar nós ocultos pela cápsula
// nem disputar um novo diálogo/acionador que já assumiu o foco.
function shellFocusAvailable(element){
  if(!element?.isConnected || element===document.body ||
    element.matches(':disabled,[aria-disabled="true"]') ||
    element.closest('[hidden],[inert],[aria-hidden="true"]') || !element.getClientRects().length)return false;
  const style=getComputedStyle(element),rect=element.getBoundingClientRect();
  return rect.width>0 && rect.height>0 && style.visibility!=='hidden' && style.visibility!=='collapse';
}
function shellRestoreHeaderFocus(opener,isCurrent=()=>true){
  const activeAtRequest=document.activeElement;
  requestAnimationFrame(()=>{
    if(!isCurrent() || document.querySelector('#modalOverlay.show,#settingsOverlay.show,#mvpNotesOverlay.show,dialog[open]') ||
      (shellUI.open && shellCompact() && !shellGlass()))return;
    let target=shellFocusAvailable(opener)?opener:null;
    if(!target && ['headerConfigBtn','headerProfileBtn','headerNotificationsBtn','finalizeSessionBtn'].includes(opener?.id)){
      const toggle=shellEl('[data-shell-menu-toggle]');
      target=shellCompact() && shellFocusAvailable(toggle)?toggle:document.getElementById('brandHomeBtn');
    }
    if(!shellFocusAvailable(target))return;
    const active=document.activeElement;
    if(active!==activeAtRequest && active!==opener && active!==target && shellFocusAvailable(active))return;
    target.focus({preventScroll:true});
  });
}
function mountNavigationLayout(value){
  if(!NAV_LAYOUTS.includes(value))return;
  const previous=document.documentElement.getAttribute('data-navigation');
  sidebarCancelExploration({immediate:true});
  closeShellMenu({restoreFocus:false});
  document.documentElement.setAttribute('data-navigation',value);
  if(value!=='sidebar')sidebarCancelExploration({immediate:true});
  const topbar=shellTopbar(),glass=shellGlass(),submenu=shellSubmenu(),horizontal=topbar||glass,nav=document.getElementById('nav');
  const stage=document.getElementById('submenuNavStage'),levelHeading=document.getElementById('submenuLevelHeading');
  if(submenu){
    if(previous!=='submenu')submenuResetExploration();
    stage.hidden=false;levelHeading.hidden=false;stage.append(nav);
  }else{
    nav.hidden=false;stage.hidden=true;levelHeading.hidden=true;
    document.querySelectorAll('.nav-sub-level-primary').forEach(level=>{level.hidden=false;level.inert=false;});
    if(horizontal)document.getElementById('gdTopbarNavSlot').append(nav);
    else document.querySelector('.sidebar-heading').after(nav);
  }
  const shell=document.getElementById('navSubShell');
  if(submenu)stage.append(shell);
  else if(glass)document.querySelector('body > header').append(shell);
  else if(topbar)document.getElementById('gdContextRow').before(shell);
  else nav.append(shell);
  document.querySelectorAll('.nav-sub-contexts').forEach(host=>{
    const key=host.id.replace('NavContexts','');
    document.getElementById(submenu||horizontal?key+'NavSubmenu':'navLocalSlot').append(host);
  });
  // O botão é o mesmo nos dois menus. Não mover o rail: a Central pode tê-lo emprestado.
  nav.querySelectorAll(':scope > .tab').forEach(btn=>btn.setAttribute('aria-label',btn.querySelector('.lbl').textContent.trim()));
  const close=document.getElementById('sidebarClose');
  if(topbar)nav.prepend(close);else document.querySelector('.sidebar-heading').append(close);
  const toggle=shellEl('[data-shell-menu-toggle]'),actions=document.getElementById('headerActions'),brand=document.getElementById('brandHomeBtn');
  if(glass)brand.after(toggle);else actions.prepend(toggle);
  if(typeof renderRailToggle==='function')renderRailToggle();
  sidebarMoveRailToOwner();
  renderNavLayoutChoice();syncNavSubState();syncShellViewport();
}
function navSubSurface(screen){const f=NAV_SUBMENU_SURFACES[screen||navSubUI.screen];return f?f():null;}
function navSubEls(screen){
  const key=screen||navSubUI.screen;
  const panel=document.getElementById(key+'NavSubmenu');
  const trigger=shellHorizontal()?document.getElementById(key+'NavTrigger'):shellEl('[data-nav-expand="'+key+'"]');
  const local=document.getElementById(key+'NavContexts');
  const allItems=[...new Set([...(panel?panel.querySelectorAll('[data-nav-item],[data-nav-sub-view]'):[]),
    ...(local?local.querySelectorAll('[data-nav-item]'):[])])];
  return {screen:key,trigger,panel,shell:document.getElementById('navSubShell'),allItems,
    items:allItems.filter(i=>!i.closest('[hidden],[inert]'))};
}
function navSubRouteIsCurrent(item,current){
  if(!item.dataset.navRoute||!window.JPWNavigation)return false;
  const r=window.JPWNavigation.resolve(item.dataset.navRoute);
  return r.accepted&&current.canonical===r.canonical&&current.screen===r.screen&&
    (!r.localView?!current.localView:!!current.localView&&r.localView.surface===current.localView.surface&&r.localView.view===current.localView.view);
}
function syncNavSubContexts(screen){
  const current=window.JPWNavigation.current();
  document.querySelectorAll('.nav-sub-contexts').forEach(host=>{
    let any=false;
    host.querySelectorAll('[data-nav-context]').forEach(group=>{
      const on=host.id===screen+'NavContexts'&&group.dataset.navContext===current.child;
      group.hidden=!on;group.inert=!on;any=any||on;
    });
    host.hidden=!any;host.inert=!any;
  });
}
function syncNavSubCurrent(screen){
  if(!window.JPWNavigation)return null;
  syncNavSubContexts(screen);
  const current=window.JPWNavigation.current(),surface=navSubSurface(screen);
  const view=surface&&surface.getView();
  const {allItems}=navSubEls(screen);
  allItems.forEach(item=>{
    const on=item.dataset.navChild?item.dataset.navChild===current.child:
      item.dataset.navRoute?navSubRouteIsCurrent(item,current):
      item.dataset.navLocalView?!!current.localView&&item.dataset.navLocalSurface===current.localView.surface&&item.dataset.navLocalView===current.localView.view:
      item.dataset.navSubView===view;
    item.classList.toggle('is-current',on);
    if(on)item.setAttribute('aria-current','page');else item.removeAttribute('aria-current');
    item.tabIndex=on?0:-1;
  });
  // Um ponto de Tab por nível, sem misturar N2 e N3 nas setas.
  const panel=document.getElementById(screen+'NavSubmenu');
  const groups=[panel&&panel.querySelector('.nav-sub-level-primary')||panel,
    ...document.querySelectorAll('.nav-sub-contexts [data-nav-context]:not([hidden])')].filter(Boolean);
  groups.forEach(group=>{
    const items=[...group.querySelectorAll('[data-nav-item],[data-nav-sub-view]')];
    if(!items.some(i=>i.tabIndex===0)&&items[0])items[0].tabIndex=0;
  });
  return panel&&panel.querySelector('[aria-current="page"]');
}
function syncShellLocation(){
  if(!window.JPWNavigation)return;
  const c=window.JPWNavigation.current();
  document.documentElement.dataset.activePrimary=c.primary||'';
  const primary=document.querySelector('#nav > .tab[data-primary="'+c.primary+'"]');
  const parts=[primary?primary.querySelector('.lbl').textContent.trim():'Dashboard'];
  const child=c.child&&document.querySelector('[data-nav-child="'+c.child+'"] .nav-sub-item-title');
  if(child)parts.push(child.textContent.trim());
  let local=null;
  if(c.primary==='personal-finance')local=document.querySelector('#finpesNavSubmenu [aria-current="page"] .nav-sub-item-title');
  else if(c.primary==='alladin')local=document.querySelector('#alladinTabs [aria-pressed="true"]');
  else local=document.querySelector('.nav-sub-contexts [data-nav-context]:not([hidden]) [aria-current="page"] .nav-sub-item-title');
  if(local&&parts[parts.length-1]!==local.textContent.trim())parts.push(local.textContent.trim());
  const el=document.getElementById('shellLocation'),text=parts.join(' / ');
  if(el&&el.textContent!==text)el.textContent=text;
  syncForexAreasTrigger();
  syncForexAdvisory();
}
// O lembrete conserva nó, ações e política de backup; só muda de composição.
function syncForexAdvisory(){
  const slot=document.getElementById('forexAdvisorySlot');
  if(!slot||!window.JPWNavigation)return;
  const current=window.JPWNavigation.current();
  const active=current.primary==='forex'&&current.screen!=='fxplan';
  slot.hidden=!active;
  const banner=document.getElementById('dgBackupBanner');
  if(!banner)return;
  const host=active?slot:document.body;
  if(banner.parentNode===host)return;
  const focused=banner.contains(document.activeElement)?document.activeElement:null;
  host.append(banner);
  if(focused?.isConnected&&!focused.closest('[hidden],[inert]'))focused.focus({preventScroll:true});
}
// Acionador compacto do mesmo N2. Nenhuma rota, campo ou preferência é copiada.
function syncForexAreasTrigger(){
  const button=document.getElementById('forexAreasToggle');
  if(!button||!window.JPWNavigation)return;
  const current=window.JPWNavigation.current(),label=document.getElementById('forexAreasCurrent');
  const actions=document.getElementById('forexTaskActions');
  if(actions)actions.hidden=current.primary!=='forex';
  button.hidden=current.primary!=='forex'||!shellMobile();
  const child=window.JPWNavigation.children('forex').find(route=>route.id===current.child);
  if(label)label.textContent=child?.label||'Desempenho';
  button.setAttribute('aria-expanded',String(shellUI.open&&!document.getElementById('execNavSubmenu')?.hidden));
}
function openForexAreas(opener,options){
  if(!shellMobile()||!shellRequireModule('forex',opener))return;
  if(shellSidebar())sidebarOpenSurface('exec',{pin:true});
  else if(shellSubmenu())submenuOpenSurface(document.getElementById('execNavTrigger'));
  else{navSubUI.collapsed=null;syncNavSubState();}
  if(shellTopbar()){
    const shell=document.getElementById('navSubShell');
    // No superior o N2 mora fora da gaveta. Emprestar o próprio nó inclui
    // seus destinos no isolamento e no ciclo de Tab já existentes.
    if(!shellUI.forexSubHome)shellUI.forexSubHome={parent:shell.parentNode,next:shell.nextSibling};
    document.getElementById('nav').append(shell);
  }
  openShellMenu(opener);syncShellViewport();
  const items=[...document.querySelectorAll('#execNavSubmenu .nav-sub-level-primary [data-nav-item]')].filter(shellFocusAvailable);
  (options?.focus==='last'?items[items.length-1]:items.find(item=>item.getAttribute('aria-current')==='page')||items[0])?.focus({preventScroll:true});
}
// The existing readout belongs to Forex. Navigation only changes its
// presentation; the normal render still owns phase and calculated metrics.
function syncForexContext(){
  const row=document.getElementById('gdContextRow');
  if(!row||!window.JPWNavigation)return;
  const current=window.JPWNavigation.current();
  const active=current.primary==='forex'&&current.screen!=='fxplan';
  row.hidden=!active;row.inert=!active;
  if(active&&typeof renderHeaderReadout==='function')renderHeaderReadout();
}
function submenuResetExploration(){
  submenuUI.level=1;submenuUI.surface=null;submenuUI.context=null;submenuUI.openers=[];
  submenuUI.temporary=false;submenuUI.direction='back';
}
function submenuPrimaryForSurface(surface){
  return ({exec:'forex',finpes:'personal-finance',research:'research',tools:'tools'})[surface]||null;
}
function shellModuleAvailable(primary){
  return !primary||window.JPWModuleAvailability?.canAccess(primary)!==false;
}
function shellRequireModule(primary,opener){
  if(shellModuleAvailable(primary))return true;
  window.JPWModuleAvailabilityUI?.deny(primary,opener);return false;
}
function submenuVisibleItems(){
  const available=item=>!item.closest('[hidden],[inert]')&&shellModuleAvailable(item.dataset.primary);
  if(submenuUI.level===1)return [...document.querySelectorAll('#nav > .tab')].filter(available);
  const panel=document.getElementById(submenuUI.surface+'NavSubmenu');
  if(!panel)return [];
  const group=submenuUI.level===3
    ?panel.querySelector('[data-nav-context="'+CSS.escape(submenuUI.context)+'"]')
    :(panel.querySelector('.nav-sub-level-primary')||panel);
  return group?[...group.querySelectorAll(':scope > [data-nav-item],:scope > [data-nav-sub-view]')].filter(available):[];
}
function submenuMarkCurrent(){
  if(!window.JPWNavigation)return;
  const current=window.JPWNavigation.current();
  document.querySelectorAll('#navSubShell [data-nav-item],#navSubShell [data-nav-sub-view]').forEach(item=>{
    const on=item.dataset.navChild?item.dataset.navChild===current.child:
      item.dataset.navLocalView?!!current.localView&&item.dataset.navLocalSurface===current.localView.surface&&item.dataset.navLocalView===current.localView.view:
      item.dataset.navSubView?!!current.localView&&current.localView.surface==='finpes'&&item.dataset.navSubView===current.localView.view:false;
    item.classList.toggle('is-current',on);
    if(on)item.setAttribute('aria-current','page');else item.removeAttribute('aria-current');
  });
}
function syncSubmenuRailPresentation(){
  const root=document.documentElement;
  if(!shellSubmenu()){root.removeAttribute('data-submenu-temporary');return;}
  const temporary=submenuUI.temporary&&root.getAttribute('data-submenu-rail')==='collapsed'&&!shellMobile();
  if(temporary)root.setAttribute('data-submenu-temporary','true');else root.removeAttribute('data-submenu-temporary');
}
function syncSubmenuPresentation(){
  if(!shellSubmenu())return;
  // Uma aba pode congelar o grupo explorado sem mudar a página ativa. Recolher
  // apenas a exploração não abandona formulário nem chama render de domínio.
  if(submenuUI.level>1&&!shellModuleAvailable(submenuPrimaryForSurface(submenuUI.surface)))submenuResetExploration();
  const root=document.documentElement,nav=document.getElementById('nav'),shell=document.getElementById('navSubShell');
  const title=document.getElementById('submenuLevelTitle'),back=document.getElementById('submenuNavBack');
  root.setAttribute('data-submenu-level',String(submenuUI.level));
  root.setAttribute('data-submenu-direction',submenuUI.direction);
  nav.hidden=submenuUI.level!==1;nav.inert=submenuUI.level!==1;
  shell.hidden=submenuUI.level===1;shell.inert=submenuUI.level===1;shell.classList.toggle('is-open',submenuUI.level!==1);
  document.querySelectorAll('#nav > .tab').forEach(tab=>{
    const group=tab.dataset.navSurface;
    if(group){tab.setAttribute('aria-haspopup','true');tab.setAttribute('aria-controls',group+'NavSubmenu');tab.setAttribute('aria-expanded',String(submenuUI.level>1&&submenuUI.surface===group));}
    else{tab.removeAttribute('aria-haspopup');tab.removeAttribute('aria-controls');tab.removeAttribute('aria-expanded');}
  });
  document.querySelectorAll('.nav-sub-menu').forEach(panel=>{
    const on=submenuUI.level>1&&panel.id===submenuUI.surface+'NavSubmenu';
    panel.hidden=!on;panel.inert=!on;panel.setAttribute('aria-hidden',String(!on));
    const primary=panel.querySelector('.nav-sub-level-primary');
    if(primary){primary.hidden=!on||submenuUI.level!==2;primary.inert=!on||submenuUI.level!==2;}
    const contexts=panel.querySelector('.nav-sub-contexts');
    if(contexts){
      const showContexts=on&&submenuUI.level===3;contexts.hidden=!showContexts;contexts.inert=!showContexts;
      contexts.querySelectorAll('[data-nav-context]').forEach(group=>{
        const show=showContexts&&group.dataset.navContext===submenuUI.context;
        group.hidden=!show;group.inert=!show;
      });
    }
  });
  const label=submenuUI.level===1?'Navegação':SUBMENU_TITLES[submenuUI.level===3?submenuUI.context:submenuUI.surface]||'Navegação';
  if(title)title.textContent=label;
  if(back){
    back.hidden=submenuUI.level===1;back.setAttribute('aria-label',submenuUI.level===3?'Voltar para '+(SUBMENU_TITLES[submenuUI.surface]||'destinos'):'Voltar para os módulos');
  }
  submenuMarkCurrent();
  const visible=submenuVisibleItems();
  visible.forEach(item=>{
    const group=item.dataset.navChild&&SUBMENU_CONTEXTS.has(item.dataset.navChild);
    if(group){item.setAttribute('aria-haspopup','true');item.setAttribute('aria-expanded',String(submenuUI.level===3&&submenuUI.context===item.dataset.navChild));}
    else{item.removeAttribute('aria-haspopup');item.removeAttribute('aria-expanded');}
  });
  let tabbable=visible.find(item=>item.getAttribute('aria-current')==='page')||visible[0];
  visible.forEach(item=>item.tabIndex=item===tabbable?0:-1);
  syncSubmenuRailPresentation();
  syncShellLocation();syncForexContext();syncShellViewport();
}
function submenuOpenSurface(control,options){
  const surface=control&&control.dataset.navSurface;if(!surface)return false;
  if(!shellRequireModule(submenuPrimaryForSurface(surface),control))return false;
  submenuUI.level=2;submenuUI.surface=surface;submenuUI.context=null;submenuUI.openers=[control];submenuUI.direction='forward';
  if(document.documentElement.getAttribute('data-submenu-rail')==='collapsed'&&!shellMobile())submenuUI.temporary=true;
  syncSubmenuPresentation();
  if(options?.focus){const target=submenuVisibleItems()[0];if(target)target.focus();}
  return true;
}
function submenuOpenContext(item,options){
  const context=item&&item.dataset.navChild;if(!SUBMENU_CONTEXTS.has(context))return false;
  if(!shellRequireModule(submenuPrimaryForSurface(submenuUI.surface),item))return false;
  submenuUI.level=3;submenuUI.context=context;submenuUI.openers[1]=item;submenuUI.direction='forward';syncSubmenuPresentation();
  if(options?.focus){const target=submenuVisibleItems()[0];if(target)target.focus();}
  return true;
}
function submenuBack(options){
  if(submenuUI.level===1)return false;
  const opener=submenuUI.level===3?submenuUI.openers[1]:submenuUI.openers[0];
  submenuUI.direction='back';
  if(submenuUI.level===3){submenuUI.level=2;submenuUI.context=null;submenuUI.openers.length=1;}
  else{submenuResetExploration();}
  syncSubmenuPresentation();
  if(options?.restoreFocus&&opener?.isConnected&&!opener.closest('[hidden],[inert]'))opener.focus();
  return true;
}
function submenuRailPreferenceChanged(next){
  if(next==='collapsed')submenuResetExploration();else submenuUI.temporary=false;
  syncSubmenuPresentation();
}
function shellHandlePrimaryIntent(control){
  if(shellSidebar()&&control?.dataset?.navSurface)return sidebarToggleSurface(control);
  if(!shellSubmenu()||!control?.dataset?.navSurface)return false;
  submenuOpenSurface(control,{focus:true});return true;
}
function syncNavSubState(){
  if(!window.JPWNavigation)return;
  if(shellSidebar()){sidebarSyncRoute();return;}
  if(shellSubmenu()){
    syncSubmenuPresentation();
    if(typeof scheduleNavPill==='function')scheduleNavPill();
    return;
  }
  const c=window.JPWNavigation.current();
  const key=shellModuleAvailable(c.primary)?({forex:'exec','personal-finance':'finpes',research:'research',tools:'tools'})[c.primary]||null:null;
  if(key!==navSubUI.screen){navSubUI.collapsed=null;navSubUI.screen=key;}
  navSubUI.open=!!key&&navSubUI.collapsed!==key;
  const shell=document.getElementById('navSubShell');
  document.querySelectorAll('[data-nav-expand]').forEach(btn=>{
    const active=btn.dataset.navExpand===key;
    btn.hidden=shellHorizontal()||!active;btn.setAttribute('aria-expanded',String(active&&navSubUI.open));
    const primary=document.getElementById(btn.dataset.navExpand+'NavTrigger');
    const label=primary.querySelector('.lbl').textContent.trim();
    btn.setAttribute('aria-label',(active&&navSubUI.open?'Recolher':'Expandir')+' destinos de '+label);
    if(shellHorizontal()){primary.setAttribute('aria-expanded',String(active&&navSubUI.open));primary.setAttribute('aria-controls',btn.dataset.navExpand+'NavSubmenu');}
    else {primary.removeAttribute('aria-expanded');primary.removeAttribute('aria-controls');}
    if(!shellHorizontal()&&active&&shell&&btn.nextElementSibling!==shell)btn.after(shell);
  });
  document.querySelectorAll('.nav-sub-menu').forEach(panel=>{
    const on=panel.id===key+'NavSubmenu'&&navSubUI.open;
    panel.hidden=!on;panel.inert=!on;panel.setAttribute('aria-hidden',String(!on));
  });
  if(shell){shell.hidden=!navSubUI.open;shell.classList.toggle('is-open',navSubUI.open);}
  if(navSubUI.open)document.documentElement.setAttribute('data-nav-sub','open');
  else document.documentElement.removeAttribute('data-nav-sub');
  if(key)syncNavSubCurrent(key);else syncNavSubContexts(null);
  syncShellLocation();
  syncForexContext();
  syncShellViewport();
  if(typeof scheduleNavPill==='function')scheduleNavPill();
}
function openNavSub(screen,options){
  if(shellSidebar()){sidebarOpenSurface(screen,{pin:true,focus:options?.focus});return;}
  if(!shellRequireModule(submenuPrimaryForSurface(screen),navSubEls(screen).trigger))return;
  if(screen!==navSubUI.screen)return;
  navSubUI.collapsed=null;syncNavSubState();
  const {trigger,panel}=navSubEls(screen);navSubUI.opener=trigger;
  if(options&&options.focus&&panel){
    const level=panel.querySelector('.nav-sub-level-primary')||panel;
    const items=[...level.querySelectorAll('[data-nav-item],[data-nav-sub-view]')].filter(item=>!item.closest('[hidden],[inert]'));
    const target=options.focus==='last'?items[items.length-1]:level.querySelector('[aria-current="page"]')||items[0];
    if(target){items.forEach(i=>i.tabIndex=i===target?0:-1);target.focus();}
  }
}
function closeNavSub(options){
  if(shellSidebar()){
    const parent=sidebarPrimary(navSubUI.screen);
    if(options?.restoreFocus&&parent)parent.focus({preventScroll:true});
    sidebarUI.suppressed=sidebarUI.preview||sidebarUI.pinned;
    sidebarCancelExploration({clearPin:true});return;
  }
  const {trigger}=navSubEls();navSubUI.collapsed=navSubUI.screen;syncNavSubState();
  if(options&&options.restoreFocus&&trigger){
    const target=shellHorizontal()&&shellCompact()&&!shellUI.open?shellEl('[data-shell-menu-toggle]'):trigger;
    target.focus();
  }
}
function selectNavSubView(view){
  if(navSubUI.screen&&window.JPWNavigation)window.JPWNavigation.navigateLocal(navSubUI.screen,view);
}
function shellFocusCurrentScreen(){
  if(!window.JPWNavigation)return;
  window.JPWNavigation.focusCurrentScreen();
  // A faixa superior mobile pode ocupar mais de uma tela antes do conteúdo.
  if(shellHorizontal()&&shellCompact()){
    const el=document.activeElement,r=el.getBoundingClientRect();
    if(r.bottom>innerHeight||r.top<0)el.scrollIntoView({block:'nearest'});
  }
}
// A intenção pertence à interação; o resolver continua sendo a única autoridade
// de aceite. Guards assíncronos retomam a mesma conclusão sem repetir navegação.
function shellAwaitNavigation(requested,complete){
  const intent={requested,complete,opener:document.activeElement};shellNavigationIntent=intent;return intent;
}
function shellTrackNavigationGuard(intent){
  if(shellNavigationIntent!==intent)return;
  const dialog=document.querySelector('dialog[open]');
  if(!dialog){shellNavigationIntent=null;return;}
  dialog.addEventListener('close',()=>{
    if(shellNavigationIntent!==intent)return;
    shellNavigationIntent=null;
    // A lateral suspende N2 enquanto o dialog está aberto. Seu observer deve
    // repintá-lo antes de devolver o foco após Permanecer/Escape.
    requestAnimationFrame(()=>{
      if(sidebarBlocked()||shellFocusAvailable(document.activeElement))return;
      if(shellFocusAvailable(intent.opener))intent.opener.focus({preventScroll:true});
      else if(!shellUI.open)shellFocusCurrentScreen();
    });
  },{once:true});
}
function shellFinishNavigation(){
  if(shellSubmenu()&&submenuUI.temporary){submenuResetExploration();syncSubmenuPresentation();}
  syncNavSubState();
  if(shellUI.open)closeShellMenu({restoreFocus:false});
  shellFocusCurrentScreen();
}
function shellNavigationApplied(plan,target){
  const intent=shellNavigationIntent?.requested===plan.requested?shellNavigationIntent:null;
  if(intent)shellNavigationIntent=null;
  const primary=target instanceof HTMLElement&&target.matches('#nav > .tab,.brand-home[data-route]');
  if(!intent&&!primary)return;
  const serial=++shellNavigationSerial,current=window.JPWNavigation.current();
  // O evento close do dialog restaura seu acionador. Concluir no próximo frame
  // deixa o foco final com o destino aceito, inclusive após descarte/salvamento.
  requestAnimationFrame(()=>{
    const active=window.JPWNavigation.current();
    if(serial!==shellNavigationSerial||active.requested!==current.requested||active.screen!==current.screen||sidebarBlocked())return;
    if(intent){intent.complete();return;}
    navSubUI.collapsed=null;syncNavSubState();
    if(shellUI.open&&shellGlass()&&navSubUI.screen)return;
    shellFinishNavigation();
  });
}
function selectNavSubItem(item){
  if(!item||!window.JPWNavigation)return false;
  if(shellSubmenu()&&submenuUI.level===2&&SUBMENU_CONTEXTS.has(item.dataset.navChild))return submenuOpenContext(item,{focus:true});
  const requested=item.dataset.navChild||item.dataset.navRoute||
    (item.dataset.navLocalSurface?item.dataset.navLocalSurface+':'+item.dataset.navLocalView:'finpes:'+item.dataset.navSubView);
  const intent=shellAwaitNavigation(requested,shellFinishNavigation);
  let accepted=false;
  if(item.dataset.navChild)accepted=window.JPWNavigation.navigate(item.dataset.navChild);
  else if(item.dataset.navRoute)accepted=window.JPWNavigation.navigate(item.dataset.navRoute);
  else if(item.dataset.navLocalSurface)accepted=window.JPWNavigation.navigateLocal(item.dataset.navLocalSurface,item.dataset.navLocalView);
  else if(item.dataset.navSubView)accepted=window.JPWNavigation.navigateLocal('finpes',item.dataset.navSubView);
  shellTrackNavigationGuard(intent);
  return accepted;
}
function syncShellViewport(){
  const sidebar=document.getElementById('appSidebar'),nav=document.getElementById('nav');if(!sidebar||!nav)return;
  const mobile=shellMobile(),topbar=shellTopbar(),glass=shellGlass(),horizontal=topbar||glass,compact=shellCompact(),blocked=shellModalOpen();
  const subShell=document.getElementById('navSubShell');
  sidebar.inert=horizontal||(mobile&&!shellUI.open);
  nav.inert=blocked||(horizontal&&compact&&!shellUI.open);
  if(subShell){
    subShell.inert=blocked||subShell.hidden||(glass&&compact&&!shellUI.open);
    if(glass&&compact&&!shellUI.open)subShell.setAttribute('aria-hidden','true');
    else if(!subShell.hidden)subShell.removeAttribute('aria-hidden');
  }
  [sidebar,nav].forEach(el=>{
    const modal=!glass&&compact&&el===shellMenuRoot();
    if(modal){el.setAttribute('role','dialog');el.setAttribute('aria-modal','true');}
    else {el.removeAttribute('role');el.removeAttribute('aria-modal');}
    if(el===nav&&blocked)el.setAttribute('aria-hidden','true');
    else if(modal)el.setAttribute('aria-hidden',String(!shellUI.open));
    else el.removeAttribute('aria-hidden');
  });
  const toggle=shellEl('[data-shell-menu-toggle]');if(toggle)toggle.setAttribute('aria-controls',glass?'gdTopbarNavSlot':topbar?'nav':'appSidebar');
  syncForexAreasTrigger();
  if(typeof scheduleNavPill==='function')scheduleNavPill();
}
function openShellMenu(opener){
  if(shellUI.open||!shellCompact()||shellModalOpen())return;
  const root=shellMenuRoot();if(!root)return;
  shellUI.open=true;shellUI.opener=opener||shellEl('[data-shell-menu-toggle]');
  document.documentElement.setAttribute('data-shell-menu','open');
  shellEl('[data-shell-menu-toggle]').setAttribute('aria-expanded','true');
  shellEl('[data-shell-menu-toggle]').setAttribute('aria-label','Fechar menu de telas');
  if(shellGlass()){
    document.getElementById('sidebarBackdrop').hidden=true;
    shellUI.inerted=[];shellUI.overflow=document.body.style.overflow;
    syncShellViewport();
    const active=[...document.querySelectorAll('#nav > .tab')].filter(item=>!item.closest('[hidden],[inert]'));
    (active.find(item=>item.classList.contains('active'))||active[0]||shellEl('[data-shell-menu-toggle]')).focus();
    return;
  }
  document.getElementById('sidebarBackdrop').hidden=false;
  shellUI.overflow=document.body.style.overflow;document.body.style.overflow='hidden';
  const header=document.querySelector('body > header');
  let targets=[...document.body.children].filter(el=>el!==(shellTopbar()?header:root)&&el.id!=='sidebarBackdrop'&&!['SCRIPT','STYLE','DIALOG'].includes(el.tagName));
  // No superior a gaveta está no header: isolar seus irmãos, nunca o ancestral do diálogo.
  if(shellTopbar())targets.push(...[...header.children].filter(el=>el.id!=='gdTopbarNavSlot'));
  shellUI.inerted=targets.map(el=>[el,el.inert]);shellUI.inerted.forEach(([el])=>el.inert=true);
  syncShellViewport();
  const active=shellSubmenu()&&submenuUI.level>1
    ?document.getElementById('submenuNavBack')
    :[...document.querySelectorAll('#nav > .tab')].find(item=>item.classList.contains('active')&&!item.closest('[hidden],[inert]'));
  (active||document.getElementById('sidebarClose')).focus();
}
function closeShellMenu(options){
  if(!shellUI.open)return;
  shellUI.open=false;document.documentElement.removeAttribute('data-shell-menu');
  const btn=shellEl('[data-shell-menu-toggle]');btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-label','Abrir menu de telas');
  document.getElementById('sidebarBackdrop').hidden=true;
  shellUI.inerted.forEach(([el,was])=>el.inert=was);shellUI.inerted=[];
  const focusBeforeReturn=document.activeElement;
  if(shellUI.forexSubHome){
    const {parent,next}=shellUI.forexSubHome;
    parent.insertBefore(document.getElementById('navSubShell'),next?.parentNode===parent?next:null);
    shellUI.forexSubHome=null;
  }
  document.body.style.overflow=shellUI.overflow;syncShellViewport();
  if(!sidebarBlocked()&&document.activeElement!==focusBeforeReturn&&shellFocusAvailable(focusBeforeReturn))focusBeforeReturn.focus({preventScroll:true});
  const opener=shellUI.opener;shellUI.opener=null;
  if((!options||options.restoreFocus!==false)&&shellFocusAvailable(opener))opener.focus();
}
function shellMoveFocus(event){
  const group=event.target.closest('[data-nav-context],.nav-sub-level-primary,.nav-sub-menu');if(!group)return;
  const items=[...group.querySelectorAll('[data-nav-item],[data-nav-sub-view]')].filter(i=>!i.closest('[hidden],[inert]'));
  if(!items.length)return;
  let index=items.indexOf(document.activeElement);
  if(event.key==='Home')index=0;else if(event.key==='End')index=items.length-1;
  else if(['ArrowDown','ArrowRight'].includes(event.key))index=(index+1)%items.length;
  else if(['ArrowUp','ArrowLeft'].includes(event.key))index=(index-1+items.length)%items.length;
  else return;
  event.preventDefault();items.forEach((i,n)=>i.tabIndex=n===index?0:-1);items[index].focus();
}
function submenuMoveFocus(event){
  const items=submenuVisibleItems();if(!items.length)return false;
  let index=items.indexOf(document.activeElement);
  if(event.key==='Home')index=0;else if(event.key==='End')index=items.length-1;
  else if(event.key==='ArrowDown')index=(index+1)%items.length;
  else if(event.key==='ArrowUp')index=(index-1+items.length)%items.length;
  else return false;
  event.preventDefault();items.forEach((item,n)=>item.tabIndex=n===index?0:-1);items[index].focus();return true;
}
function initOperationalShell(){
  const sidebar=document.getElementById('appSidebar');if(!sidebar||sidebar.dataset.ready)return;
  sidebar.dataset.ready='true';
  // A governança cria o aviso depois deste script e pode recriá-lo após uma
  // recarga. Observar só a adição direta evita vigiar conteúdo financeiro.
  new MutationObserver(records=>{
    if(records.some(record=>[...record.addedNodes].some(node=>node.nodeType===Node.ELEMENT_NODE&&node.id==='dgBackupBanner')))
      syncForexAdvisory();
  }).observe(document.body,{childList:true});
  document.querySelectorAll('#navSubShell .nav-sub-contexts').forEach(host=>{
    host.id=host.closest('.nav-sub-menu').id.replace('NavSubmenu','NavContexts');

  });
  initNavLayoutChoice();
  if(typeof initNavOrderChoice==='function')initNavOrderChoice();
  initSidebarExploration();
  const alladinTabs=document.getElementById('alladinTabs');
  if(alladinTabs)new MutationObserver(syncShellLocation).observe(alladinTabs,{subtree:true,attributes:true,attributeFilter:['aria-pressed']});
  document.addEventListener('click',event=>{
    const forexNotes=event.target.closest('#forexNotesToggle');
    if(forexNotes){if(typeof openMvpNotesDrawer==='function')openMvpNotesDrawer(forexNotes);return;}
    const forexAreas=event.target.closest('#forexAreasToggle');
    if(forexAreas){shellUI.open?closeShellMenu():openForexAreas(forexAreas);return;}
    const toggle=event.target.closest('[data-shell-menu-toggle]');
    if(toggle){shellUI.open?closeShellMenu():openShellMenu(toggle);return;}
    if(event.target.closest('#sidebarClose,#sidebarBackdrop')){closeShellMenu();return;}
    if(event.target.closest('#submenuNavBack')&&shellSubmenu()){submenuBack({restoreFocus:true});return;}
    const expander=event.target.closest('[data-nav-expand]');
    if(expander){navSubUI.open?closeNavSub():openNavSub(expander.dataset.navExpand);return;}
    const item=event.target.closest('[data-nav-item],[data-nav-sub-view]');
    if(item){selectNavSubItem(item);return;}
    if(shellUI.open&&event.target.closest('#headerActions .header-action')){closeShellMenu({restoreFocus:false});return;}
    if(shellUI.open&&shellGlass()&&!event.target.closest('body > header,dialog'))closeShellMenu();
  });
  document.addEventListener('keydown',event=>{
    if(sidebarBlocked())return;
    if(sidebarHandleKey(event))return;
    if(shellSubmenu()){
      const primary=event.target.closest('#nav > .tab');
      const item=event.target.closest('#navSubShell [data-nav-item],#navSubShell [data-nav-sub-view]');
      if((primary||item)&&submenuMoveFocus(event))return;
      if(primary&&event.key==='ArrowRight'&&primary.dataset.navSurface){event.preventDefault();submenuOpenSurface(primary,{focus:true});return;}
      if(item&&event.key==='ArrowRight'&&submenuUI.level===2&&SUBMENU_CONTEXTS.has(item.dataset.navChild)){event.preventDefault();submenuOpenContext(item,{focus:true});return;}
      if((item||event.target.closest('#submenuNavBack'))&&['ArrowLeft','Escape'].includes(event.key)&&submenuUI.level>1){event.preventDefault();submenuBack({restoreFocus:true});return;}
      if(event.key==='Escape'&&submenuUI.level>1&&event.target.closest('#appSidebar')){event.preventDefault();submenuBack({restoreFocus:true});return;}
      if(event.key==='Escape'&&submenuUI.level===1&&submenuUI.temporary){event.preventDefault();submenuResetExploration();syncSubmenuPresentation();return;}
    }
    if(event.key==='Escape'&&shellUI.open){event.preventDefault();closeShellMenu();return;}
    if(shellUI.open&&!shellGlass()&&event.key==='Tab'){
      const focusable=[...shellMenuRoot().querySelectorAll('button,[tabindex="0"]')].filter(el=>!el.disabled&&!el.closest('[hidden],[inert]')&&el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden'&&el.tabIndex>=0);
      const first=focusable[0],last=focusable[focusable.length-1];
      if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    }
    const expander=event.target.closest(shellHorizontal()?'.nav-sub-trigger':'[data-nav-expand]');
    if(expander&&['ArrowDown','ArrowUp'].includes(event.key)){
      event.preventDefault();
      const key=expander.dataset.navExpand||expander.id.replace('NavTrigger','');
      if(!shellRequireModule(submenuPrimaryForSurface(key),expander))return;
      const layout=document.documentElement.getAttribute('data-navigation'),compact=shellCompact();
      const focus=event.key==='ArrowUp'?'last':true;
      const complete=()=>{
        // Uma preferência/breakpoint alterado enquanto o diálogo estava aberto
        // não deve reabrir a composição anterior nem focar um controle oculto.
        if(document.documentElement.getAttribute('data-navigation')!==layout||shellCompact()!==compact){shellFinishNavigation();return;}
        if(shellTopbar()&&shellMobile()&&key==='exec'){openForexAreas(expander,{focus});return;}
        if(shellTopbar()&&shellUI.open)closeShellMenu({restoreFocus:false});
        openNavSub(key,{focus});
      };
      const primary=submenuPrimaryForSurface(key);
      if(shellHorizontal()&&window.JPWNavigation.current().primary!==primary){
        const intent=shellAwaitNavigation(window.JPWNavigation.resolve(expander).requested,complete);
        expander.click();shellTrackNavigationGuard(intent);return;
      }
      complete();return;
    }
    if(event.key==='Escape'&&navSubUI.open&&event.target.closest('#navSubShell')){event.preventDefault();closeNavSub({restoreFocus:true});return;}
    shellMoveFocus(event);
  });
  window.addEventListener('resize',()=>{
    if(shellSidebar()){
      const mobile=shellMobile();
      if(sidebarUI.mobile!==mobile){sidebarCancelExploration({immediate:true});sidebarUI.mobile=mobile;}
      sidebarMeasure();
    }
    if(shellUI.open&&!shellCompact())closeShellMenu({restoreFocus:false});syncShellViewport();
  });
  syncNavSubState();syncShellViewport();
}
initOperationalShell();
