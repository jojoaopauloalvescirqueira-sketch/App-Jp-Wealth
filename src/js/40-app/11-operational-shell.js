// ============ SHELL OPERACIONAL · NAVEGAÇÃO RESPONSIVA (N1) ============
// Camada estritamente de interface: controla a gaveta global no mobile e a
// faixa compartilhada do segundo nível, com hover transitório, clique fixado,
// foco, Escape e clique externo. Os módulos globais continuam usando os
// listeners de 01-navigation.js; o segundo nível apenas encaminha a chave de
// visão para a superfície pública de UI do módulo — nunca toca domínio.
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
  return {
    screen: key, trigger, panel, shell,
    items: panel ? [...panel.querySelectorAll('[data-nav-sub-view]')] : []
  };
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

function syncNavSubCurrent(screen) {
  const { items } = navSubEls(screen);
  const surface = navSubSurface(screen);
  const current = surface && typeof surface.getView === 'function' ? surface.getView() : null;
  items.forEach(item => {
    const active = item.dataset.navSubView === current;
    item.classList.toggle('is-current', active);
    if (active) item.setAttribute('aria-current', 'page');
    else item.removeAttribute('aria-current');
    item.tabIndex = active ? 0 : -1;
  });
  const found = items.find(item => item.dataset.navSubView === current);
  // Sem visão correspondente (módulo ainda não carregado) o primeiro item
  // continua alcançável por Tab — a faixa nunca fica sem ponto de entrada.
  if (!found && items[0]) items[0].tabIndex = 0;
  return found || items[0] || null;
}

function openNavSub(screen, options) {
  const target = screen || navSubUI.screen;
  const { trigger, panel, shell, items } = navSubEls(target);
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
  document.documentElement.setAttribute('data-nav-sub', 'open');
  if (navSubUI.pinned) document.documentElement.setAttribute('data-nav-sub-pinned', 'true');
  trigger.setAttribute('aria-expanded', 'true');
  shell.classList.add('is-open');
  panel.setAttribute('aria-hidden', 'false');
  panel.inert = false;
  if (typeof navPillApplyGeometry === 'function') navPillApplyGeometry(trigger);
  const current = syncNavSubCurrent(target);
  if (options && options.focus === 'last') {
    const last = items[items.length - 1];
    if (last) { items.forEach(item => { item.tabIndex = item === last ? 0 : -1; }); last.focus(); }
  } else if (options && options.focus && current) current.focus();
}

// Retira o estado de aberto de um módulo sem mexer na faixa: usado ao trocar
// de módulo e como parte do fechamento.
function collapseNavSubPanel(screen) {
  const { trigger, panel, items } = navSubEls(screen);
  if (trigger) trigger.setAttribute('aria-expanded', 'false');
  if (panel) { panel.setAttribute('aria-hidden', 'true'); panel.inert = true; }
  items.forEach(item => { item.tabIndex = -1; });
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
      const { panel, items } = navSubEls(screen);
      if (!panel) return;
      items.forEach(item => { item.tabIndex = -1; });
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
    const item = event.target.closest('[data-nav-sub-view]');
    if (item) { selectNavSubView(item.dataset.navSubView); return; }
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
