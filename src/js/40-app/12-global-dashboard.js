// ============ GLOBAL DASHBOARD — SHELL COMPARTILHADO (N1) ============
// Fidelidade ao Claude Design aprovado (Auditoria visual JP Wealth /
// "Dashboard Claro" e telas irmãs). Escopado por um atributo NOVO e
// independente, data-shell="global-dashboard", em cima de data-ui-version
// "tesla-inspired" — os dois seguem removíveis de forma independente:
// - sem data-shell: volta ao shell da Fase A/B0 (Tesla-inspired).
// - sem data-ui-version também: volta ao terminal legado original.
//
// Só reposiciona nós já existentes no DOM (mesmo padrão de
// moveLegacySettingsNodes/relocateSettingsSearchForRedesign). Nenhum ID,
// listener ou contrato de renderização é alterado — só a posição de alguns
// elementos e a exibição do rodapé novo.

function gdEl(id) { return document.getElementById(id); }

function relocateGlobalDashboardShell() {
  if (document.documentElement.dataset.shell !== 'global-dashboard') return;

  // Navegação: #nav nasce como irmão de <header> (compatibilidade legada) e
  // é transportado para dentro da barra de marca sob a flag nova.
  const nav = gdEl('nav'), navSlot = gdEl('gdTopbarNavSlot');
  if (nav && navSlot && nav.parentElement !== navSlot) navSlot.append(nav);

  // Leituras de contexto (Perfil/Período/Equity/DD + salvo/relógio/fase):
  // nascem dentro de <header> (linha única legada) e migram para a segunda
  // faixa do cabeçalho de 2 linhas do design aprovado.
  const header = document.querySelector('header'), contextRow = gdEl('gdContextRow');
  if (header && contextRow && !contextRow.dataset.ready) {
    header.querySelectorAll(':scope > .hdr-readout, :scope > .hdr-sep, :scope > .header-status').forEach(node => contextRow.append(node));
    contextRow.dataset.ready = 'true';
  }

  // Rodapé global — só existe (visualmente) sob esta flag.
  const footer = gdEl('gdFooter');
  if (footer) footer.hidden = false;

  // Grid executivo do Dashboard: o card de Clearance nasce dentro do slide 0
  // do carrossel (mantém o contrato de renderOperationalClearance) e entra no
  // topo de gdHeroRow, ao lado do painel institucional estático. A faixa de
  // 4 métricas nasce no slide 1, hoje inatingível sob esta flag (o carrossel
  // do modo imersivo foi aposentado, sem controles para trocar de slide) — e
  // passa a ficar logo abaixo de gdHeroRow. Ambos são só reposicionados —
  // nenhum ID, listener ou valor muda.
  const heroRow = gdEl('gdHeroRow');
  if (heroRow) {
    const clearanceCard = gdEl('mcClearanceCard');
    if (clearanceCard && clearanceCard.parentElement !== heroRow) heroRow.prepend(clearanceCard);
    const metricStrip = gdEl('mcMetricStrip');
    if (metricStrip && metricStrip.previousElementSibling !== heroRow) heroRow.after(metricStrip);
  }

  // Alerta real de onboarding: reposicionado (não clonado) para a coluna
  // lateral do Dashboard, entre "Perfil e Contexto" e "Ações Rápidas". O
  // mesmo elemento, o mesmo estado (S.onboarding) e o mesmo renderizador
  // (renderOnboardingIncompleteBanner) continuam sendo a única fonte — só
  // muda onde ele vive no DOM. Sem esta flag, permanece no topo de <main>
  // (comportamento legado, visível em todas as telas).
  const dashSide = gdEl('gdDashSide'), quickCard = gdEl('gdQuickCard'), onbBanner = gdEl('onboardingIncompleteBanner');
  if (dashSide && quickCard && onbBanner && onbBanner.parentElement !== dashSide) {
    dashSide.insertBefore(onbBanner, quickCard);
  }

  // Modo imersivo aposentado (Etapa 1): o herói antigo (.jp-hero) ainda existe
  // no DOM — carrossel, setas, pontos, atalhos de teclado por seta — mas sob
  // esta flag não tem mais nenhum descendente focável (Clearance e a faixa
  // de métricas já saíram dele; o resto é display:none ou [hidden]). `inert`
  // é o reforço explícito: garante que ele nunca dispute foco, teclado ou
  // clique, mesmo que o conteúdo mude no futuro. Não é remoção — é reversível
  // (some junto com a flag) e não apaga nenhum código legado.
  const hero = document.querySelector('.jp-hero');
  if (hero) hero.inert = true;
}
relocateGlobalDashboardShell();

// Links do rodapé novo com destino real dentro da Central de Configurações
// (Estatuto, Exportar Dados, Central de Configurações, Documentação) —
// reúso direto de openSettingsModal(categoria), já existente. "Log de
// Auditoria" reusa [data-dash-go], já cabeado em 10-dashboard-immersive.js.
// Registrado sem gate de flag porque o rodapé nasce com [hidden] e só perde
// o atributo sob data-shell="global-dashboard" — inatingível sem a flag.
document.addEventListener('click', event => {
  const btn = event.target.closest('[data-gd-settings]');
  if (btn && typeof openSettingsModal === 'function') openSettingsModal(btn.dataset.gdSettings, btn);
});
