// Shell lateral: apresentação sobre o resolver existente. Nenhuma rota,
// preferência de navegação ou informação financeira é criada aqui.
const shellUI = { open:false, opener:null, inerted:[], overflow:'' };
const navSubUI = { open:false, pinned:false, screen:null, collapsed:null, opener:null };
const NAV_SUBMENU_SURFACES = {
  exec:()=>window.JPWExec&&window.JPWExec.ui,
  finpes:()=>window.JPWFin&&window.JPWFin.ui,
  research:()=>window.JPWResearch&&window.JPWResearch.ui
};
function shellEl(sel){return document.querySelector(sel);}
function shellMobile(){return window.matchMedia('(max-width:900px)').matches;}
function navSubSurface(screen){const f=NAV_SUBMENU_SURFACES[screen||navSubUI.screen];return f?f():null;}
function navSubEls(screen){
  const key=screen||navSubUI.screen;
  const panel=document.getElementById(key+'NavSubmenu');
  const trigger=shellEl('[data-nav-expand="'+key+'"]');
  const local=document.getElementById(key+'NavContexts');
  const allItems=[...(panel?panel.querySelectorAll('[data-nav-item],[data-nav-sub-view]'):[]),
    ...(local?local.querySelectorAll('[data-nav-item]'):[])];
  return {screen:key,trigger,panel,shell:document.getElementById('navSubShell'),allItems,
    items:allItems.filter(i=>!i.closest('[hidden]'))};
}
function navSubRouteIsCurrent(item,current){
  if(!item.dataset.navRoute||!window.JPWNavigation)return false;
  const r=window.JPWNavigation.resolve(item.dataset.navRoute);
  return r.accepted&&current.canonical===r.canonical&&current.screen===r.screen&&
    (!r.localView?!current.localView:!!current.localView&&r.localView.surface===current.localView.surface&&r.localView.view===current.localView.view);
}
function syncNavSubContexts(screen){
  const current=window.JPWNavigation.current();
  document.querySelectorAll('#navLocalSlot .nav-sub-contexts').forEach(host=>{
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
  const groups=[panel,...document.querySelectorAll('#navLocalSlot [data-nav-context]:not([hidden])')].filter(Boolean);
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
  else local=document.querySelector('#navLocalSlot [data-nav-context]:not([hidden]) [aria-current="page"] .nav-sub-item-title');
  if(local&&parts[parts.length-1]!==local.textContent.trim())parts.push(local.textContent.trim());
  const el=document.getElementById('shellLocation'),text=parts.join(' / ');
  if(el&&el.textContent!==text)el.textContent=text;
}
function syncNavSubState(){
  if(!window.JPWNavigation)return;
  const c=window.JPWNavigation.current();
  const key=({forex:'exec','personal-finance':'finpes',research:'research'})[c.primary]||null;
  if(key!==navSubUI.screen){navSubUI.collapsed=null;navSubUI.screen=key;}
  navSubUI.open=!!key&&navSubUI.collapsed!==key;
  const shell=document.getElementById('navSubShell');
  document.querySelectorAll('[data-nav-expand]').forEach(btn=>{
    const active=btn.dataset.navExpand===key;
    btn.hidden=!active;btn.setAttribute('aria-expanded',String(active&&navSubUI.open));
    const primary=document.getElementById(btn.dataset.navExpand+'NavTrigger');
    const label=primary.querySelector('.lbl').textContent.trim();
    btn.setAttribute('aria-label',(active&&navSubUI.open?'Recolher':'Expandir')+' destinos de '+label);
    if(active&&shell&&btn.nextElementSibling!==shell)btn.after(shell);
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
  if(typeof scheduleNavPill==='function')scheduleNavPill();
}
function openNavSub(screen,options){
  if(screen!==navSubUI.screen)return;
  navSubUI.collapsed=null;syncNavSubState();
  const {trigger,panel}=navSubEls(screen);navSubUI.opener=trigger;
  if(options&&options.focus&&panel){
    const items=[...panel.querySelectorAll('[data-nav-item],[data-nav-sub-view]')];
    const target=options.focus==='last'?items[items.length-1]:panel.querySelector('[aria-current="page"]')||items[0];
    if(target){items.forEach(i=>i.tabIndex=i===target?0:-1);target.focus();}
  }
}
function closeNavSub(options){
  const {trigger}=navSubEls();navSubUI.collapsed=navSubUI.screen;syncNavSubState();
  if(options&&options.restoreFocus&&trigger)trigger.focus();
}
function selectNavSubView(view){
  if(navSubUI.screen&&window.JPWNavigation)window.JPWNavigation.navigateLocal(navSubUI.screen,view);
}
function selectNavSubItem(item){
  if(!item||!window.JPWNavigation)return;
  if(item.dataset.navChild)window.JPWNavigation.navigate(item.dataset.navChild);
  else if(item.dataset.navRoute)window.JPWNavigation.navigate(item.dataset.navRoute);
  else if(item.dataset.navLocalSurface)window.JPWNavigation.navigateLocal(item.dataset.navLocalSurface,item.dataset.navLocalView);
  else if(item.dataset.navSubView)selectNavSubView(item.dataset.navSubView);
  syncNavSubState();
  if(shellUI.open)closeShellMenu({restoreFocus:false});
  window.JPWNavigation.focusCurrentScreen();
}
function syncShellViewport(){
  const sidebar=document.getElementById('appSidebar');if(!sidebar)return;
  const modal=shellMobile();sidebar.inert=modal&&!shellUI.open;
  if(modal){sidebar.setAttribute('role','dialog');sidebar.setAttribute('aria-modal','true');sidebar.setAttribute('aria-hidden',String(!shellUI.open));}
  else {sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal');sidebar.removeAttribute('aria-hidden');}
  if(typeof scheduleNavPill==='function')scheduleNavPill();
}
function openShellMenu(opener){
  if(shellUI.open||!shellMobile())return;
  const sidebar=document.getElementById('appSidebar');if(!sidebar)return;
  shellUI.open=true;shellUI.opener=opener||shellEl('[data-shell-menu-toggle]');
  document.documentElement.setAttribute('data-shell-menu','open');
  shellEl('[data-shell-menu-toggle]').setAttribute('aria-expanded','true');
  shellEl('[data-shell-menu-toggle]').setAttribute('aria-label','Fechar menu de telas');
  document.getElementById('sidebarBackdrop').hidden=false;
  shellUI.overflow=document.body.style.overflow;document.body.style.overflow='hidden';
  shellUI.inerted=[...document.body.children].filter(el=>el!==sidebar&&el.id!=='sidebarBackdrop'&&!['SCRIPT','STYLE'].includes(el.tagName)).map(el=>[el,el.inert]);
  shellUI.inerted.forEach(([el])=>el.inert=true);
  syncShellViewport();
  const active=sidebar.querySelector('#nav > .tab.active');(active||document.getElementById('sidebarClose')).focus();
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
  const group=event.target.closest('[data-nav-context],.nav-sub-menu');if(!group)return;
  const items=[...group.querySelectorAll('[data-nav-item],[data-nav-sub-view]')].filter(i=>!i.closest('[hidden]'));
  if(!items.length)return;
  let index=items.indexOf(document.activeElement);
  if(event.key==='Home')index=0;else if(event.key==='End')index=items.length-1;
  else if(['ArrowDown','ArrowRight'].includes(event.key))index=(index+1)%items.length;
  else if(['ArrowUp','ArrowLeft'].includes(event.key))index=(index-1+items.length)%items.length;
  else return;
  event.preventDefault();items.forEach((i,n)=>i.tabIndex=n===index?0:-1);items[index].focus();
}
function initOperationalShell(){
  const sidebar=document.getElementById('appSidebar');if(!sidebar||sidebar.dataset.ready)return;
  sidebar.dataset.ready='true';
  document.querySelectorAll('#navSubShell .nav-sub-contexts').forEach(host=>{
    host.id=host.closest('.nav-sub-menu').id.replace('NavSubmenu','NavContexts');
    document.getElementById('navLocalSlot').append(host);
  });
  const shell=document.getElementById('navSubShell');document.getElementById('nav').append(shell);
  const alladinTabs=document.getElementById('alladinTabs');
  if(alladinTabs)new MutationObserver(syncShellLocation).observe(alladinTabs,{subtree:true,attributes:true,attributeFilter:['aria-pressed']});
  document.addEventListener('click',event=>{
    const toggle=event.target.closest('[data-shell-menu-toggle]');
    if(toggle){shellUI.open?closeShellMenu():openShellMenu(toggle);return;}
    if(event.target.closest('#sidebarClose,#sidebarBackdrop')){closeShellMenu();return;}
    const expander=event.target.closest('[data-nav-expand]');
    if(expander){navSubUI.open?closeNavSub():openNavSub(expander.dataset.navExpand);return;}
    const item=event.target.closest('[data-nav-item],[data-nav-sub-view]');
    if(item){selectNavSubItem(item);return;}
    if(event.target.closest('#nav > .tab')){
      navSubUI.collapsed=null;
      syncNavSubState();
      if(shellUI.open)closeShellMenu({restoreFocus:false});
      if(window.JPWNavigation)window.JPWNavigation.focusCurrentScreen();
    }
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&shellUI.open){event.preventDefault();closeShellMenu();return;}
    if(shellUI.open&&event.key==='Tab'){
      const focusable=[...sidebar.querySelectorAll('button,[tabindex="0"]')].filter(el=>!el.disabled&&!el.closest('[hidden],[inert]')&&el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden'&&el.tabIndex>=0);
      const first=focusable[0],last=focusable[focusable.length-1];
      if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    }
    const expander=event.target.closest('[data-nav-expand]');
    if(expander&&['ArrowDown','ArrowUp'].includes(event.key)){
      event.preventDefault();openNavSub(expander.dataset.navExpand,{focus:event.key==='ArrowUp'?'last':true});return;
    }
    if(event.key==='Escape'&&navSubUI.open&&event.target.closest('#navSubShell')){event.preventDefault();closeNavSub({restoreFocus:true});return;}
    shellMoveFocus(event);
  });
  window.addEventListener('resize',()=>{if(shellUI.open&&!shellMobile())closeShellMenu({restoreFocus:false});syncShellViewport();});
  syncNavSubState();syncShellViewport();
}
initOperationalShell();
