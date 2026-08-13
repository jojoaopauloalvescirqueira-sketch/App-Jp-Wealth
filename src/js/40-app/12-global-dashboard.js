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

  // Sequência estrutural do protótipo: aviso P1 → cockpit P1 → quatro cards P2.
  // Os mesmos nós são movidos, nunca clonados, para preservar IDs e listeners.
  const dashMain = gdEl('gdDashMain');
  const instPanel = dashMain && dashMain.querySelector(':scope > [data-layout-card="institutional-panel"]');
  if (dashMain && instPanel) {
    const clearanceCard = gdEl('mcClearanceCard');
    if (clearanceCard && clearanceCard.parentElement !== dashMain) instPanel.before(clearanceCard);
  }

  const onbBanner = gdEl('onboardingIncompleteBanner');
  if (dashMain && onbBanner && onbBanner.parentElement !== dashMain) dashMain.prepend(onbBanner);

  // O protótipo encerra a faixa P2 com Ações Rápidas, na mesma grade de
  // Status, VRM e Notícias. A personalização reafirma essa posição depois,
  // mas a relocação inicial garante a composição correta mesmo antes de uma
  // preferência de layout ser normalizada.
  const quickCard = gdEl('gdQuickCard');
  if (dashMain && quickCard && quickCard.parentElement !== dashMain) dashMain.append(quickCard);

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

/* ================== STATUS DO SISTEMA (JPW-789ABC) ================== */
// O espaço antes ocupado pelo painel institucional decorativo passa a mostrar
// estado operacional real. TODA linha é espelho de leitura — nenhum cálculo
// novo, nenhum estado paralelo, nenhuma escrita. As quatro fontes já existem:
//
//   persistência  jpWealthPersistenceFailure / jpWealthPersistenceIsBlocked()  (00-core/04)
//   backup        S.dataGovernance.backup.lastConfirmedAt                      (00-core/03)
//   frescor       S.instruments[].updated + staleInfo()                        (10-domain/04)
//   governança    getOnboardingCompletionState()                               (10-domain/01)
//
// staleInfo() é REUSADO em vez de reimplementado: os limiares de frescor
// (≤3 dias / ≤20 / 21+) são dele e continuam com dono único. Duplicá-los aqui
// criaria duas verdades sobre quando uma cotação deixa de ser confiável.

function gdSsRow(id, state, label, meta) {
  const row = gdEl(id); if (!row) return;
  row.dataset.state = state;
  const lbl = row.querySelector('[data-jpwss-lbl]'); if (lbl) lbl.textContent = label;
  const mt = row.querySelector('[data-jpwss-meta]'); if (mt) mt.textContent = meta || '';
}

function renderSystemStatus() {
  if (document.documentElement.dataset.shell !== 'global-dashboard') return;
  if (!gdEl('jpwSsPersist')) return; // componente fora do DOM: nada a fazer

  // 1 · PERSISTÊNCIA — o risco nº 1 do projeto é perda silenciosa de dados,
  // então a falha de gravação (A-001) nunca é suprimida nem comprimida.
  // Sem carimbo de horário: `savedTag` é um selo transitório de 1200ms, não
  // guarda "salvo às hh:mm:ss" em lugar nenhum. Registrar esse horário exigiria
  // escrever dentro de save() — mudança N2, fora deste escopo e não autorizada.
  // A spec trata a meta da direita como o PRIMEIRO item comprimível; o que ela
  // proíbe suprimir é a linha e seu rótulo, que estão aqui.
  const falha = (typeof jpWealthPersistenceFailure === 'object' && jpWealthPersistenceFailure)
    ? jpWealthPersistenceFailure.active : false;
  const travado = (typeof jpWealthPersistenceIsBlocked === 'function') && jpWealthPersistenceIsBlocked();
  if (falha) {
    gdSsRow('jpwSsPersist', 'bad', 'Falha ao gravar neste navegador',
      jpWealthPersistenceFailure.kind === 'serialize' ? 'serialização' : 'armazenamento');
  } else if (travado) {
    gdSsRow('jpwSsPersist', 'warn', 'Gravação suspensa — recuperação pendente', '');
  } else {
    gdSsRow('jpwSsPersist', 'ok', 'Dados salvos neste navegador', '');
  }

  // 2 · BACKUP
  const bk = (S.dataGovernance && S.dataGovernance.backup) || {};
  if (bk.lastConfirmedAt) {
    const quando = (typeof dgFmtDateTime === 'function') ? dgFmtDateTime(bk.lastConfirmedAt) : '';
    gdSsRow('jpwSsBackup', 'ok', 'Backup confirmado', quando);
  } else {
    gdSsRow('jpwSsBackup', 'warn', 'Backup não confirmado', 'nunca');
  }

  // 3 · FRESCOR DAS COTAÇÕES — vale a PIOR das cotações, não a média nem a
  // melhor: o semáforo responde "posso confiar na grade agora?", e um único
  // instrumento defasado já compromete a resposta.
  const instrumentos = Array.isArray(S.instruments) ? S.instruments : [];
  if (instrumentos.length && typeof staleInfo === 'function' && typeof daysStale === 'function') {
    const pior = instrumentos.reduce((a, b) => daysStale(a.updated) >= daysStale(b.updated) ? a : b);
    const st = staleInfo(pior.updated);
    const estado = st.cls === 'fresh' ? 'ok' : (st.cls === 'warn' ? 'warn' : 'bad');
    gdSsRow('jpwSsQuotes', estado, 'Cotações de referência', st.label);
  } else {
    gdSsRow('jpwSsQuotes', 'warn', 'Cotações de referência', 'sem dados');
  }

  // 4 · GOVERNANÇA — reusa a MESMA severidade do banner de onboarding, para
  // que as duas superfícies nunca discordem sobre o estado do período.
  const btn = gdEl('jpwSsGovBtn');
  if (typeof getOnboardingCompletionState === 'function') {
    const gov = getOnboardingCompletionState();
    const estado = gov.severity === 'complete' ? 'ok' : (gov.severity === 'critical' ? 'bad' : 'warn');
    gdSsRow('jpwSsGov', estado, 'Governança do período', gov.completed + '/' + gov.total + ' seções');
    if (btn) btn.hidden = gov.complete;
  } else if (btn) btn.hidden = true;
}

// "Revisar ›" reusa o MESMO destino do banner de onboarding
// (openFirstIncompleteOnboarding) — nenhum fluxo novo de navegação.
document.addEventListener('click', event => {
  if (!event.target.closest('#jpwSsGovBtn')) return;
  if (typeof openFirstIncompleteOnboarding === 'function') openFirstIncompleteOnboarding();
});

// Primeira pintura. boot() roda render() na ordem 36 do manifest — antes deste
// arquivo (41) existir —, então aquele primeiro render pula o componente pelo
// guard de typeof em 03-main-render.js. Um macrotask resolve: setTimeout só
// entrega quando a thread principal termina de avaliar TODOS os <script>
// síncronos, inclusive 16-storage-governance.js (45), de onde vem dgFmtDateTime.
// Não é rAF de propósito — rAF não dispara em aba oculta, lição já paga duas
// vezes nesta base (ver a varredura dos gauges em 20-ui/03-main-render.js).
setTimeout(renderSystemStatus, 0);

// Links do rodapé novo com destino real dentro da Central de Configurações
// (Estatuto, Exportar Dados, Central de Configurações, Documentação) —
// reúso direto de openSettingsModal(categoria), já existente. "Log de
// Auditoria" reusa [data-dash-go], já cabeado em 10-dashboard-immersive.js.
// Registrado sem gate de flag porque o rodapé nasce com [hidden] e só perde
// o atributo sob data-shell="global-dashboard" — inatingível sem a flag.
document.addEventListener('click', event => {
  const btn = event.target.closest('[data-gd-settings]');
  if (btn && typeof openSettingsModal === 'function') openSettingsModal(btn.dataset.gdSettings, btn);
  const quick = event.target.closest('[data-dash-settings]');
  if (quick && typeof openSettingsModal === 'function') openSettingsModal(quick.dataset.dashSettings, quick);
});
