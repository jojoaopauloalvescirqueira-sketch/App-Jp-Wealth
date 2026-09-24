// Shell de apresentação sobre o resolver existente. A composição é uma
// preferência por navegador; não participa do estado ou do backup financeiro.
const shellUI = { open:false, opener:null, inerted:[], overflow:'' };
const navSubUI = { open:false, pinned:false, screen:null, collapsed:null, opener:null };
const submenuUI = { level:1, surface:null, context:null, openers:[], temporary:false, direction:'forward' };
const SUBMENU_CONTEXTS=new Set(['forex-management-accounts','forex-planning','research-forex']);
const SUBMENU_TITLES=Object.freeze({
  exec:'Forex',finpes:'Finanças Pessoais',research:'Research',tools:'Ferramentas e Serviços',
  'forex-management-accounts':'Contas e Período','forex-planning':'Planejamento','research-forex':'Forex'
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
  closeShellMenu({restoreFocus:false});
  document.documentElement.setAttribute('data-navigation',value);
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
}
// The existing readout belongs to Forex. Navigation only changes its
// presentation; the normal render still owns phase and calculated metrics.
function syncForexContext(){
  const row=document.getElementById('gdContextRow');
  if(!row||!window.JPWNavigation)return;
  const active=window.JPWNavigation.current().primary==='forex';
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
  if(!shellSubmenu()||!control?.dataset?.navSurface)return false;
  submenuOpenSurface(control,{focus:true});return true;
}
function syncNavSubState(){
  if(!window.JPWNavigation)return;
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
function selectNavSubItem(item){
  if(!item||!window.JPWNavigation)return false;
  if(shellSubmenu()&&submenuUI.level===2&&SUBMENU_CONTEXTS.has(item.dataset.navChild))return submenuOpenContext(item,{focus:true});
  let accepted=false;
  if(item.dataset.navChild)accepted=window.JPWNavigation.navigate(item.dataset.navChild);
  else if(item.dataset.navRoute)accepted=window.JPWNavigation.navigate(item.dataset.navRoute);
  else if(item.dataset.navLocalSurface)accepted=window.JPWNavigation.navigateLocal(item.dataset.navLocalSurface,item.dataset.navLocalView);
  else if(item.dataset.navSubView)accepted=window.JPWNavigation.navigateLocal('finpes',item.dataset.navSubView);
  if(!accepted)return false;
  if(shellSubmenu()&&submenuUI.temporary){submenuResetExploration();syncSubmenuPresentation();}
  syncNavSubState();
  if(shellUI.open)closeShellMenu({restoreFocus:false});
  shellFocusCurrentScreen();
  return true;
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
  let targets=[...document.body.children].filter(el=>el!==(shellTopbar()?header:root)&&el.id!=='sidebarBackdrop'&&!['SCRIPT','STYLE'].includes(el.tagName));
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
  document.body.style.overflow=shellUI.overflow;syncShellViewport();
  const opener=shellUI.opener;shellUI.opener=null;
  if((!options||options.restoreFocus!==false)&&opener&&opener.isConnected)opener.focus();
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
  document.querySelectorAll('#navSubShell .nav-sub-contexts').forEach(host=>{
    host.id=host.closest('.nav-sub-menu').id.replace('NavSubmenu','NavContexts');

  });
  initNavLayoutChoice();
  if(typeof initNavOrderChoice==='function')initNavOrderChoice();
  const alladinTabs=document.getElementById('alladinTabs');
  if(alladinTabs)new MutationObserver(syncShellLocation).observe(alladinTabs,{subtree:true,attributes:true,attributeFilter:['aria-pressed']});
  document.addEventListener('click',event=>{
    const toggle=event.target.closest('[data-shell-menu-toggle]');
    if(toggle){shellUI.open?closeShellMenu():openShellMenu(toggle);return;}
    if(event.target.closest('#sidebarClose,#sidebarBackdrop')){closeShellMenu();return;}
    if(event.target.closest('#submenuNavBack')&&shellSubmenu()){submenuBack({restoreFocus:true});return;}
    const expander=event.target.closest('[data-nav-expand]');
    if(expander){navSubUI.open?closeNavSub():openNavSub(expander.dataset.navExpand);return;}
    const item=event.target.closest('[data-nav-item],[data-nav-sub-view]');
    if(item){selectNavSubItem(item);return;}
    if(event.target.closest('#nav > .tab')){
      if(!shellModuleAvailable(event.target.closest('#nav > .tab').dataset.primary))return;
      if(shellSubmenu()&&event.target.closest('#nav > .tab').dataset.navSurface)return;
      navSubUI.collapsed=null;
      syncNavSubState();
      if(shellUI.open&&shellGlass()&&navSubUI.screen)return;
      if(shellUI.open)closeShellMenu({restoreFocus:false});
      shellFocusCurrentScreen();
      return;
    }
    if(shellUI.open&&event.target.closest('#brandHomeBtn,#headerActions .header-action')){closeShellMenu({restoreFocus:false});return;}
    if(shellUI.open&&shellGlass()&&!event.target.closest('body > header'))closeShellMenu();
  });
  document.addEventListener('keydown',event=>{
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
      // Em mobile superior o N2 fica no fluxo, fora da gaveta.
      if(shellTopbar()&&shellUI.open)closeShellMenu({restoreFocus:false});
      if(shellHorizontal()&&key!==navSubUI.screen)expander.click();
      openNavSub(key,{focus:event.key==='ArrowUp'?'last':true});return;
    }
    if(event.key==='Escape'&&navSubUI.open&&event.target.closest('#navSubShell')){event.preventDefault();closeNavSub({restoreFocus:true});return;}
    shellMoveFocus(event);
  });
  window.addEventListener('resize',()=>{if(shellUI.open&&!shellCompact())closeShellMenu({restoreFocus:false});syncShellViewport();});
  syncNavSubState();syncShellViewport();
}
initOperationalShell();
