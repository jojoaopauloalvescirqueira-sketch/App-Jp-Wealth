// ============ EXECUTION BOARD · WORKSPACES DO MÓDULO (N1 — apresentação) ============
// Superfície estritamente visual do segundo nível do Execution Board: decide
// qual workspace de section#exec está visível, e nada além disso. Não calcula,
// não persiste, não conhece ordem, fase, risco, LIFO ou clearance, e não cria
// uma segunda fonte de verdade — os renderizadores existentes continuam donos
// integrais do conteúdo.
//
// A troca é `hidden` + `inert` sobre nós que permanecem MONTADOS. Nenhum estado
// operacional é desmontado: valores digitados e ainda não confirmados, foco,
// disclosures abertos e o DOM que renderPhases() reconstrói em #phaseContainer
// sobrevivem à ida e à volta. Por isso não existe re-render nesta troca.
//
// O estado é efêmero por contrato (docs/architecture/NAVIGATION-HIERARCHY.md):
// não entra em S, localStorage, backup, schema nem migração.

// Chave de visão -> id do container. O Painel Operacional é o #execWidgetGrid
// original: nenhum nó foi movido e nenhum id mudou na realocação.
const EXEC_VIEWS = [
  ['overview', 'execOverview'],
  ['panel', 'execWidgetGrid'],
  // Motor de Lote: o container e o proprio #motorWidgetGrid migrado de
  // Configuracoes, nao um wrapper novo. renderMotor() ja o desenha no boot e o
  // redesenha por mudanca de dado — nao ha render on-demand a fazer aqui.
  ['motor', 'motorWidgetGrid'],
  // Historico: memoria institucional das Operacoes Unicas finalizadas. Consumidor
  // somente leitura de S.operationHistory — nao recalcula fato historico algum a
  // partir das grades vivas.
  ['history', 'execHistory']
];
// Workspaces cujo conteúdo depende de estado vivo são montados ao entrar.
const EXEC_VIEW_RENDERERS = {
  // Repinta a cada entrada porque o conteudo depende de S.operationHistory, que
  // muda quando uma operacao e finalizada noutra parte do app.
  history: () => { if (window.JPWHistoryUI && typeof window.JPWHistoryUI.render === 'function') window.JPWHistoryUI.render(); }
};
const EXEC_DEFAULT_VIEW = 'overview';
let execView = EXEC_DEFAULT_VIEW;
// Marca de escolha explícita do usuário. Existe porque navegar para o módulo e
// escolher a visão acontecem no mesmo gesto quando o clique parte da faixa: sem
// ela, o destino inicial atropelaria a escolha que acabou de ser feita.
let execViewExplicit = false;

function execApplyView(view) {
  EXEC_VIEWS.forEach(([key, id]) => {
    const el = document.getElementById(id);
    if (!el) return;
    const active = key === view;
    el.hidden = !active;
    el.inert = !active;
  });
}

function execSetView(view) {
  execView = view;
  execApplyView(view);
  // A montagem vem DEPOIS de tirar o hidden: renderizar num container oculto
  // impediria qualquer medida futura e deixaria o foco em no invisivel.
  const render = EXEC_VIEW_RENDERERS[view];
  if (typeof render === 'function') render();
}

function execSelectView(view) {
  // Compatibilidade de API: consumidores legados não recuperam ownership Exec.
  // O shim delega ao resolver canônico e não altera `execView`.
  const researchView={ecal:'calendar',nocoda:'nocoda',pivots:'pivots'}[view];
  if(researchView&&window.JPWNavigation&&typeof window.JPWNavigation.navigateLocal==='function'){
    return window.JPWNavigation.navigateLocal('research',researchView);
  }
  if (!EXEC_VIEWS.some(([key]) => key === view)) return false;
  execViewExplicit = true;
  execSetView(view);
  return true;
}

function execGetView() { return execView; }

// Destino inicial do módulo: entrar no Execution Board vindo de outra tela abre
// a Visão Geral. Observar a classe .active cobre TODOS os caminhos de entrada —
// aba, Ações Rápidas, CTA do Dashboard, chamada por string — sem embrulhar
// navigateToScreen, que já carrega duas camadas de wrapper (10-dashboard-
// immersive.js e 13-dashboard-layout.js) cuja ordem não deve crescer.
//
// navigateToScreen remove .active de todas as .screen e recoloca na alvo dentro
// do mesmo bloco síncrono. As duas mutações chegam juntas em um único callback,
// então reabrir a faixa estando já no módulo não conta como entrada nova e não
// tira o usuário do Painel Operacional.
function execWatchModuleEntry() {
  const screen = document.getElementById('exec');
  if (!screen || typeof MutationObserver !== 'function') return;
  let wasActive = screen.classList.contains('active');
  const observer = new MutationObserver(() => {
    const isActive = screen.classList.contains('active');
    if (isActive && !wasActive && !execViewExplicit) {
      execSetView(EXEC_DEFAULT_VIEW);
      // A faixa pode já ter sincronizado o item ativo antes deste callback
      // (o clique é síncrono, este observador é microtarefa). Repintar o
      // destaque evita que ele fique apontando a visão anterior.
      if (typeof syncNavSubCurrent === 'function') syncNavSubCurrent('exec');
    }
    execViewExplicit = false;
    wasActive = isActive;
  });
  observer.observe(screen, { attributes: true, attributeFilter: ['class'] });
}

execApplyView(execView);
execWatchModuleEntry();

// Superfície pública consumida pelo controlador da faixa compartilhada
// (40-app/11-operational-shell.js, NAV_SUBMENU_SURFACES). Só chaves de UI.
window.JPWExec = { ui: { selectView: execSelectView, getView: execGetView } };
