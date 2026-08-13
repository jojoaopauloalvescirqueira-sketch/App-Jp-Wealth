// ============ SHELL OPERACIONAL · NAVEGAÇÃO RESPONSIVA (N1) ============
// Camada estritamente de interface: controla a gaveta global no mobile e o
// segundo nível estrutural de Planejamento, com hover transitório, clique
// fixado, foco, Escape e clique externo. Os módulos globais continuam usando
// os listeners de 01-navigation.js; o segundo nível encaminha apenas a visão
// interna para a superfície pública de UI do Planejamento.

const shellUI = { open: false, opener: null };
const fxNavUI = { open: false, pinned: false, closeTimer: null, opener: null };
const FX_NAV_CLOSE_DELAY = 400;

function shellEl(sel) { return document.querySelector(sel); }

function fxNavEls() {
  const trigger = document.getElementById('fxNavTrigger');
  const panel = document.getElementById('fxNavSubmenu');
  const shell = document.getElementById('fxNavSubmenuShell');
  return { trigger, panel, shell, items: panel ? [...panel.querySelectorAll('[data-fx-nav-view]')] : [] };
}

function cancelFxNavClose() {
  if (fxNavUI.closeTimer) clearTimeout(fxNavUI.closeTimer);
  fxNavUI.closeTimer = null;
}

function syncFxNavCurrent() {
  const { items } = fxNavEls();
  const current = window.JPWFx && window.JPWFx.ui && typeof window.JPWFx.ui.getView === 'function'
    ? window.JPWFx.ui.getView() : 'overview';
  items.forEach(item => {
    const active = item.dataset.fxNavView === current;
    item.classList.toggle('is-current', active);
    if (active) item.setAttribute('aria-current', 'page');
    else item.removeAttribute('aria-current');
    item.tabIndex = active ? 0 : -1;
  });
  return items.find(item => item.dataset.fxNavView === current) || items[0] || null;
}

function openFxNav(options) {
  const { trigger, panel, shell, items } = fxNavEls();
  if (!trigger || !panel || !shell) return;
  cancelFxNavClose();
  fxNavUI.open = true;
  if (options && options.pin) fxNavUI.pinned = true;
  fxNavUI.opener = (options && options.opener) || trigger;
  document.documentElement.setAttribute('data-fx-nav', 'open');
  if (fxNavUI.pinned) document.documentElement.setAttribute('data-fx-nav-pinned', 'true');
  trigger.setAttribute('aria-expanded', 'true');
  shell.classList.add('is-open');
  panel.setAttribute('aria-hidden', 'false');
  panel.inert = false;
  if (typeof navPillApplyGeometry === 'function') navPillApplyGeometry(trigger);
  const current = syncFxNavCurrent();
  if (options && options.focus === 'last') {
    const last = items[items.length - 1];
    if (last) { items.forEach(item => { item.tabIndex = item === last ? 0 : -1; }); last.focus(); }
  } else if (options && options.focus && current) current.focus();
}

function closeFxNav(options) {
  cancelFxNavClose();
  const { trigger, panel, shell, items } = fxNavEls();
  if (!trigger || !panel || !shell) return;
  const wasOpen = fxNavUI.open;
  fxNavUI.open = false;
  fxNavUI.pinned = false;
  document.documentElement.removeAttribute('data-fx-nav');
  document.documentElement.removeAttribute('data-fx-nav-pinned');
  trigger.setAttribute('aria-expanded', 'false');
  shell.classList.remove('is-open');
  panel.setAttribute('aria-hidden', 'true');
  panel.inert = true;
  items.forEach(item => { item.tabIndex = -1; });
  if (typeof scheduleNavPill === 'function') scheduleNavPill();
  const opener = fxNavUI.opener || trigger;
  fxNavUI.opener = null;
  if (wasOpen && options && options.restoreFocus && opener && document.contains(opener)) opener.focus();
}

function scheduleFxNavClose() {
  cancelFxNavClose();
  if (fxNavUI.pinned) return;
  fxNavUI.closeTimer = setTimeout(() => closeFxNav(), FX_NAV_CLOSE_DELAY);
}

function selectFxNavView(view) {
  if (typeof navigateToScreen === 'function') navigateToScreen('fxplan');
  if (window.JPWFx && window.JPWFx.ui && typeof window.JPWFx.ui.selectView === 'function') {
    window.JPWFx.ui.selectView(view);
  }
  syncFxNavCurrent();
  if (shellUI.open) closeShellMenu({ restoreFocus: false });
}

function moveFxNavFocus(direction) {
  const { items } = fxNavEls();
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
  const { trigger: fxTrigger, panel: fxPanel, items: fxItems } = fxNavEls();
  if (fxTrigger && fxPanel) {
    fxItems.forEach(item => { item.tabIndex = -1; });
    const finePointer = window.matchMedia('(hover:hover) and (pointer:fine)');
    const hoverCapable = () => finePointer.matches && !window.matchMedia('(max-width:900px)').matches;
    const globalNav = fxTrigger.closest('#nav');
    fxTrigger.addEventListener('pointerenter', () => { if (hoverCapable()) openFxNav({ opener: fxTrigger }); });
    if (globalNav) {
      globalNav.addEventListener('pointerenter', () => { if (fxNavUI.open) cancelFxNavClose(); });
      globalNav.addEventListener('pointerleave', event => {
        if (hoverCapable() && !fxPanel.contains(event.relatedTarget)) scheduleFxNavClose();
      });
    }
    fxPanel.addEventListener('pointerenter', cancelFxNavClose);
    fxPanel.addEventListener('pointerleave', event => {
      if (hoverCapable() && !(globalNav && globalNav.contains(event.relatedTarget))) scheduleFxNavClose();
    });
    fxTrigger.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown') {
        event.preventDefault(); openFxNav({ opener: fxTrigger, focus: true });
      } else if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault(); openFxNav({ opener: fxTrigger, focus: true, pin: true });
      } else if (event.key === 'ArrowUp') {
        event.preventDefault(); openFxNav({ opener: fxTrigger, focus: 'last' });
      } else if (event.key === 'Escape' && fxNavUI.open) {
        event.preventDefault(); closeFxNav({ restoreFocus: true });
      }
    });
    fxPanel.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') { event.preventDefault(); moveFxNavFocus(1); }
      else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') { event.preventDefault(); moveFxNavFocus(-1); }
      else if (event.key === 'Home') { event.preventDefault(); moveFxNavFocus('first'); }
      else if (event.key === 'End') { event.preventDefault(); moveFxNavFocus('last'); }
      else if (event.key === 'Escape') { event.preventDefault(); closeFxNav({ restoreFocus: true }); }
    });
  }

  document.addEventListener('click', event => {
    const toggle = event.target.closest('[data-shell-menu-toggle]');
    if (toggle) { shellUI.open ? closeShellMenu() : openShellMenu(toggle); return; }
    const fxTriggerHit = event.target.closest('#fxNavTrigger');
    if (fxTriggerHit) {
      openFxNav({ opener: fxTriggerHit, focus: shellUI.open, pin: true });
      if (shellUI.open) closeShellMenu({ restoreFocus: false });
      return;
    }
    const fxItem = event.target.closest('[data-fx-nav-view]');
    if (fxItem) { selectFxNavView(fxItem.dataset.fxNavView); return; }
    if (fxNavUI.open && !event.target.closest('#fxNavSubmenu')) closeFxNav();
    // Selecionar outro destino global fecha somente a gaveta mobile — sem
    // devolver foco, porque a navegação já levou o usuário para outra tela.
    if (shellUI.open && event.target.closest('#nav .tab:not(#fxNavTrigger)')) { closeShellMenu({ restoreFocus: false }); return; }
    // Clique fora do painel e fora do botão fecha.
    if (shellUI.open && !event.target.closest('#nav')) closeShellMenu({ restoreFocus: false });
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && fxNavUI.open) { event.preventDefault(); closeFxNav({ restoreFocus: true }); return; }
    if (event.key === 'Escape' && shellUI.open) { event.preventDefault(); closeShellMenu(); }
  });

  // Abertura transitória não atravessa mudança de breakpoint; a abertura
  // fixada sobrevive ao resize e apenas adapta sua composição responsiva.
  window.addEventListener('resize', () => {
    if (fxNavUI.open && !fxNavUI.pinned) closeFxNav();
    if (shellUI.open) closeShellMenu({ restoreFocus: false });
  });
}
initOperationalShell();
