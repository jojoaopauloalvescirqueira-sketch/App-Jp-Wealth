// ============ SHELL OPERACIONAL · MENU MOBILE (N1 — apresentação) ============
// Camada estritamente de interface. Abre e fecha o painel de destinos em telas
// estreitas, com Escape, clique fora e devolução de foco ao acionador.
//
// Não navega por conta própria: os destinos continuam sendo os mesmos botões
// .tab[data-screen], cujos listeners são os de 01-navigation.js. Este módulo
// apenas fecha o painel depois que a navegação existente acontece.

const shellUI = { open: false, opener: null };

function shellEl(sel) { return document.querySelector(sel); }

function openShellMenu(opener) {
  const nav = document.getElementById('nav');
  const toggle = shellEl('[data-shell-menu-toggle]');
  if (!nav || shellUI.open) return;
  shellUI.open = true;
  shellUI.opener = opener || toggle;
  document.documentElement.setAttribute('data-shell-menu', 'open');
  if (toggle) toggle.setAttribute('aria-expanded', 'true');
  const first = nav.querySelector('.tab');
  if (first) first.focus();
}

function closeShellMenu(options) {
  if (!shellUI.open) return;
  shellUI.open = false;
  document.documentElement.removeAttribute('data-shell-menu');
  const toggle = shellEl('[data-shell-menu-toggle]');
  if (toggle) toggle.setAttribute('aria-expanded', 'false');
  const opener = shellUI.opener;
  shellUI.opener = null;
  if (!options || options.restoreFocus !== false) {
    if (opener && document.contains(opener)) opener.focus();
  }
}

function initOperationalShell() {
  document.addEventListener('click', event => {
    const toggle = event.target.closest('[data-shell-menu-toggle]');
    if (toggle) { shellUI.open ? closeShellMenu() : openShellMenu(toggle); return; }
    // Selecionar um destino fecha o painel — sem devolver foco ao acionador,
    // porque a navegação já levou o usuário para a tela escolhida.
    if (shellUI.open && event.target.closest('#nav .tab')) { closeShellMenu({ restoreFocus: false }); return; }
    // Clique fora do painel e fora do botão fecha.
    if (shellUI.open && !event.target.closest('#nav')) closeShellMenu({ restoreFocus: false });
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && shellUI.open) { event.preventDefault(); closeShellMenu(); }
  });

  // Trocar de tela por qualquer caminho encerra o painel.
  window.addEventListener('resize', () => { if (shellUI.open) closeShellMenu({ restoreFocus: false }); });
}
initOperationalShell();
