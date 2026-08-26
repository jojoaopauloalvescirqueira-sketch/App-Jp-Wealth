// ============ SHELL OPERACIONAL · NAVEGAÇÃO RESPONSIVA (N1) ============
// Camada estritamente de interface: controla a gaveta global no mobile e a
// faixa compartilhada dos níveis contextuais, com hover transitório, clique
// fixado, foco, Escape e clique externo. Forex encaminha filhos canônicos e
// visões locais pelo resolver; Finanças Pessoais mantém sua superfície pública.
// Estado ativo sempre deriva de JPWNavigation/current + UI, nunca de cópia local.
//
// A faixa é UMA só (#navSubShell) e apenas um módulo fica aberto por vez:
// selecionar outro módulo global é clique externo e fecha o anterior. Por isso
// basta um slot no grid do body, e o módulo aberto é distinguido por
// `aria-expanded="true"` no próprio acionador — não por atributo global na
// raiz, que acenderia todos os acionadores de uma vez.
//
// Para dar segundo nível a um módulo novo bastam três coisas, nenhuma delas
// neste arquivo além da última linha:
//   1. um botão `.tab.nav-sub-trigger` com id `<data-nav-surface>NavTrigger`;
//   2. um `<nav class="nav-sub-menu">` com id `<data-nav-surface>NavSubmenu` dentro
//      de #navSubShell, com botões `[data-nav-sub-view]`;
//   3. uma entrada em NAV_SUBMENU_SURFACES apontando para a superfície de UI.

const shellUI = { open: false, opener: null };
const navSubUI = { open: false, pinned: false, closeTimer: null, opener: null, screen: null };
const NAV_SUB_CLOSE_DELAY = 400;

// Contrato da superfície de módulo: `selectView(chave)` e `getView()`.
// O controlador não conhece as chaves — quem as valida é o próprio módulo.
const NAV_SUBMENU_SURFACES = {
  exec: () => (window.JPWExec && window.JPWExec.ui) || null,
  finpes: () => (window.JPWFin && window.JPWFin.ui) || null
};

function shellEl(sel) { return document.querySelector(sel); }

function navSubEls(screen) {
  const key = screen || navSubUI.screen;
  const trigger = key ? document.getElementById(key + 'NavTrigger') : null;
  const panel = key ? document.getElementById(key + 'NavSubmenu') : null;
  const shell = document.getElementById('navSubShell');
  const allItems=panel?[...panel.querySelectorAll('[data-nav-item],[data-nav-sub-view]')]:[];
  return {screen:key,trigger,panel,shell,allItems,
    items:allItems.filter(item=>!item.closest('[data-nav-context][hidden]'))};
}

function navSubSurface(screen) {
  const resolve = NAV_SUBMENU_SURFACES[screen || navSubUI.screen];
  return typeof resolve === 'function' ? resolve() : null;
}

function cancelNavSubClose() {
  if (navSubUI.closeTimer) clearTimeout(navSubUI.closeTimer);
  navSubUI.closeTimer = null;
}

// Monta o painel do módulo alvo e desmonta os demais. `hidden` só muda aqui:
// abrir e fechar a faixa não esconde o painel, senão a animação de recolher
// mostraria uma faixa vazia encolhendo.
function mountNavSubPanel(screen) {
  document.querySelectorAll('#navSubShell .nav-sub-menu').forEach(panel => {
    panel.hidden = panel.id !== screen + 'NavSubmenu';
  });
}

function syncNavSubContexts(screen) {
  if(screen!=='exec'||!window.JPWNavigation) return;
  const current=window.JPWNavigation.current();
  let any=false;
  document.querySelectorAll('#execNavSubmenu [data-nav-context]').forEach(group=>{
    const active=group.dataset.navContext===current.child;
    if(active) any=true;
    group.hidden=!active;
    group.inert=!active;
  });
  const host=document.querySelector('#execNavSubmenu .nav-sub-contexts');
  if(host){host.hidden=!any;host.inert=!any;}
}

function navSubRouteIsCurrent(item,current){
  if(!window.JPWNavigation||!item.dataset.navRoute) return false;
  const resolved=window.JPWNavigation.resolve(item.dataset.navRoute);
  if(!resolved.accepted||current.canonical!==resolved.canonical||current.screen!==resolved.screen) return false;
  if(!resolved.localView) return !current.localView;
  return !!current.localView&&current.localView.surface===resolved.localView.surface&&
    current.localView.view===resolved.localView.view;
}

function syncNavSubCurrent(screen) {
  syncNavSubContexts(screen);
  const {items}=navSubEls(screen);
  const surface=navSubSurface(screen);
  const currentNav=window.JPWNavigation?window.JPWNavigation.current():null;
  const currentView=surface&&typeof surface.getView==='function'?surface.getView():null;
  items.forEach(item => {
    const active=item.dataset.navChild?(currentNav&&item.dataset.navChild===currentNav.child):
      (item.dataset.navRoute?navSubRouteIsCurrent(item,currentNav):
      (item.dataset.navLocalView?(currentNav&&currentNav.localView&&
        item.dataset.navLocalSurface===currentNav.localView.surface&&
        item.dataset.navLocalView===currentNav.localView.view):
      item.dataset.navSubView===currentView));
    item.classList.toggle('is-current', active);
    if (active) item.setAttribute('aria-current', 'page');
    else item.removeAttribute('aria-current');
    item.tabIndex = active ? 0 : -1;
  });
  const found=items.find(item=>item.classList.contains('is-current'));
  // Sem visão correspondente (módulo ainda não carregado) o primeiro item
  // continua alcançável por Tab — a faixa nunca fica sem ponto de entrada.
  if (!found && items[0]) items[0].tabIndex = 0;
  return found || items[0] || null;
}

function syncNavSubState(){
  if(navSubUI.screen) syncNavSubCurrent(navSubUI.screen);
}

function openNavSub(screen, options) {
  const target = screen || navSubUI.screen;
  const {trigger,panel,shell}=navSubEls(target);
  if (!trigger || !panel || !shell) return;
  // Trocar de módulo com a faixa já aberta: o anterior perde estado de aberto
  // antes de o novo assumir, para não restar dois acionadores expandidos.
  if (navSubUI.screen && navSubUI.screen !== target) collapseNavSubPanel(navSubUI.screen);
  cancelNavSubClose();
  navSubUI.open = true;
  navSubUI.screen = target;
  if (options && options.pin) navSubUI.pinned = true;
  navSubUI.opener = (options && options.opener) || trigger;
  mountNavSubPanel(target);
  const current=syncNavSubCurrent(target);
  const {items}=navSubEls(target);
  document.documentElement.setAttribute('data-nav-sub', 'open');
  if (navSubUI.pinned) document.documentElement.setAttribute('data-nav-sub-pinned', 'true');
  trigger.setAttribute('aria-expanded', 'true');
  shell.classList.add('is-open');
  panel.setAttribute('aria-hidden', 'false');
  panel.inert = false;
  if (typeof navPillApplyGeometry === 'function') navPillApplyGeometry(trigger);
  if (options && options.focus === 'last') {
    const last = items[items.length - 1];
    if (last) { items.forEach(item => { item.tabIndex = item === last ? 0 : -1; }); last.focus(); }
  } else if (options && options.focus && current) current.focus();
}

// Retira o estado de aberto de um módulo sem mexer na faixa: usado ao trocar
// de módulo e como parte do fechamento.
function collapseNavSubPanel(screen) {
  const {trigger,panel,allItems}=navSubEls(screen);
  if (trigger) trigger.setAttribute('aria-expanded', 'false');
  if (panel) { panel.setAttribute('aria-hidden', 'true'); panel.inert = true; }
  allItems.forEach(item => { item.tabIndex = -1; });
}

function closeNavSub(options) {
  cancelNavSubClose();
  const shell = document.getElementById('navSubShell');
  const screen = navSubUI.screen;
  if (!shell || !screen) return;
  const wasOpen = navSubUI.open;
  navSubUI.open = false;
  navSubUI.pinned = false;
  document.documentElement.removeAttribute('data-nav-sub');
  document.documentElement.removeAttribute('data-nav-sub-pinned');
  shell.classList.remove('is-open');
  collapseNavSubPanel(screen);
  if (typeof scheduleNavPill === 'function') scheduleNavPill();
  const opener = navSubUI.opener || navSubEls(screen).trigger;
  navSubUI.opener = null;
  navSubUI.screen = null;
  if (wasOpen && options && options.restoreFocus && opener && document.contains(opener)) opener.focus();
}

function scheduleNavSubClose() {
  cancelNavSubClose();
  if (navSubUI.pinned) return;
  navSubUI.closeTimer = setTimeout(() => closeNavSub(), NAV_SUB_CLOSE_DELAY);
}

function selectNavSubView(view) {
  const screen = navSubUI.screen;
  if (!screen) return;
  if (window.JPWNavigation && typeof window.JPWNavigation.navigateLocal === 'function') {
    window.JPWNavigation.navigateLocal(screen, view);
  } else {
    if (typeof navigateToScreen === 'function') navigateToScreen(screen);
    const surface = navSubSurface(screen);
    if (surface && typeof surface.selectView === 'function') surface.selectView(view);
  }
  syncNavSubCurrent(screen);
  if (shellUI.open) closeShellMenu({ restoreFocus: false });
}

function selectNavSubItem(item){
  if(!item) return;
  if(item.dataset.navChild&&window.JPWNavigation){
    window.JPWNavigation.navigate(item.dataset.navChild);
  }else if(item.dataset.navRoute&&window.JPWNavigation){
    window.JPWNavigation.navigate(item.dataset.navRoute);
  }else if(item.dataset.navLocalSurface&&item.dataset.navLocalView&&window.JPWNavigation){
    window.JPWNavigation.navigateLocal(item.dataset.navLocalSurface,item.dataset.navLocalView);
  }else if(item.dataset.navSubView){
    selectNavSubView(item.dataset.navSubView);
  }
  syncNavSubState();
  if(shellUI.open) closeShellMenu({restoreFocus:false});
}

function moveNavSubFocus(direction) {
  const { items } = navSubEls();
  if (!items.length) return;
  const current = Math.max(0, items.indexOf(document.activeElement));
  const next = direction === 'first' ? 0
    : direction === 'last' ? items.length - 1
    : (current + direction + items.length) % items.length;
  items.forEach((item, index) => { item.tabIndex = index === next ? 0 : -1; });
  items[next].focus();
}

function openShellMenu(opener) {
  const nav = document.getElementById('nav');
  const toggle = shellEl('[data-shell-menu-toggle]');
  if (!nav || shellUI.open) return;
  shellUI.open = true;
  shellUI.opener = opener || toggle;
  document.documentElement.setAttribute('data-shell-menu', 'open');
  if (toggle) {
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Fechar menu de telas');
  }
  const first = nav.querySelector('.tab');
  if (first) first.focus();
}

function closeShellMenu(options) {
  if (!shellUI.open) return;
  shellUI.open = false;
  document.documentElement.removeAttribute('data-shell-menu');
  const toggle = shellEl('[data-shell-menu-toggle]');
  if (toggle) {
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Abrir menu de telas');
  }
  const opener = shellUI.opener;
  shellUI.opener = null;
  if (!options || options.restoreFocus !== false) {
    if (opener && document.contains(opener)) opener.focus();
  }
}

function initOperationalShell() {
  const navSubShell = document.getElementById('navSubShell');
  const globalNav = document.getElementById('nav');
  const triggers = globalNav ? [...globalNav.querySelectorAll('.nav-sub-trigger')] : [];

  if (navSubShell && triggers.length) {
    const finePointer = window.matchMedia('(hover:hover) and (pointer:fine)');
    const hoverCapable = () => finePointer.matches && !window.matchMedia('(max-width:900px)').matches;

    triggers.forEach(trigger => {
      const screen = trigger.dataset.navSurface;
      const {panel,allItems}=navSubEls(screen);
      if (!panel) return;
      allItems.forEach(item => { item.tabIndex = -1; });
      trigger.addEventListener('pointerenter', () => { if (hoverCapable()) openNavSub(screen, { opener: trigger }); });
      trigger.addEventListener('keydown', event => {
        if (event.key === 'ArrowDown') {
          event.preventDefault(); openNavSub(screen, { opener: trigger, focus: true });
        } else if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          if (window.JPWNavigation) window.JPWNavigation.navigate(trigger.dataset.route);
          openNavSub(screen, { opener: trigger, focus: true, pin: true });
        } else if (event.key === 'ArrowUp') {
          event.preventDefault(); openNavSub(screen, { opener: trigger, focus: 'last' });
        } else if (event.key === 'Escape' && navSubUI.open) {
          event.preventDefault(); closeNavSub({ restoreFocus: true });
        }
      });
    });

    globalNav.addEventListener('pointerenter', () => { if (navSubUI.open) cancelNavSubClose(); });
    globalNav.addEventListener('pointerleave', event => {
      if (hoverCapable() && !navSubShell.contains(event.relatedTarget)) scheduleNavSubClose();
    });
    navSubShell.addEventListener('pointerenter', cancelNavSubClose);
    navSubShell.addEventListener('pointerleave', event => {
      if (hoverCapable() && !globalNav.contains(event.relatedTarget)) scheduleNavSubClose();
    });
    navSubShell.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') { event.preventDefault(); moveNavSubFocus(1); }
      else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') { event.preventDefault(); moveNavSubFocus(-1); }
      else if (event.key === 'Home') { event.preventDefault(); moveNavSubFocus('first'); }
      else if (event.key === 'End') { event.preventDefault(); moveNavSubFocus('last'); }
      else if (event.key === 'Escape') { event.preventDefault(); closeNavSub({ restoreFocus: true }); }
    });
  }

  document.addEventListener('click', event => {
    const toggle = event.target.closest('[data-shell-menu-toggle]');
    if (toggle) { shellUI.open ? closeShellMenu() : openShellMenu(toggle); return; }
    const triggerHit = event.target.closest('.nav-sub-trigger');
    if (triggerHit) {
      openNavSub(triggerHit.dataset.navSurface, { opener: triggerHit, focus: shellUI.open, pin: true });
      if (shellUI.open) closeShellMenu({ restoreFocus: false });
      return;
    }
    const item=event.target.closest('[data-nav-item],[data-nav-sub-view]');
    if(item){selectNavSubItem(item);return;}
    if (navSubUI.open && !event.target.closest('#navSubShell')) closeNavSub();
    // Selecionar outro destino global fecha somente a gaveta mobile — sem
    // devolver foco, porque a navegação já levou o usuário para outra tela.
    if (shellUI.open && event.target.closest('#nav .tab:not(.nav-sub-trigger)')) {
      closeShellMenu({ restoreFocus: false });
      if (window.JPWNavigation) window.JPWNavigation.focusCurrentScreen();
      return;
    }
    // Clique fora do painel e fora do botão fecha.
    if (shellUI.open && !event.target.closest('#nav')) closeShellMenu({ restoreFocus: false });
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navSubUI.open) { event.preventDefault(); closeNavSub({ restoreFocus: true }); return; }
    if (event.key === 'Escape' && shellUI.open) { event.preventDefault(); closeShellMenu(); }
  });

  // Abertura transitória não atravessa mudança de breakpoint; a abertura
  // fixada sobrevive ao resize e apenas adapta sua composição responsiva.
  window.addEventListener('resize', () => {
    if (navSubUI.open && !navSubUI.pinned) closeNavSub();
    if (shellUI.open) closeShellMenu({ restoreFocus: false });
  });
}
initOperationalShell();
