// ============ FINANÇAS PESSOAIS · WORKSPACES DO MÓDULO (PF-01 — apresentação) ============
// Superfície estritamente visual do segundo nível de Finanças Pessoais: decide
// qual workspace de section#finpes está visível, e nada além disso. Não
// calcula, não persiste e não conhece o domínio — o núcleo vive em
// 10-domain/12-personal-finance.js e os renderizadores chegarão com PF-02+.
//
// A troca é `hidden` + `inert` sobre nós que permanecem MONTADOS (padrão
// 13-exec-views.js). O estado de visão é efêmero por contrato
// (NAVIGATION-HIERARCHY.md): não entra em S, localStorage, backup nem schema —
// e NAVEGAR JAMAIS ESCREVE NO ESTADO, doutrina que em Finanças Pessoais é
// também a fronteira da materialização de mês (abrir um mês não o cria).

const FINPES_VIEWS = [
  ['overview', 'finpesOverview'],
  ['mensal', 'finpesMensal'],
  ['dividas', 'finpesDividas'],
  ['comparativo', 'finpesComparativo'],
  ['cenarios', 'finpesCenarios']
];
const FINPES_DEFAULT_VIEW = 'overview';
let finpesView = FINPES_DEFAULT_VIEW;
// Marca de escolha explícita: navegar para o módulo e escolher a visão
// acontecem no mesmo gesto quando o clique parte da faixa (ver 13-exec-views).
let finpesViewExplicit = false;

// Face visível do sentinela de unidade monetária (Bloco C). O banner
// #finpesUnitNotice vive estático no HTML; aqui só se decide sua visibilidade.
// O bloqueio é do MÓDULO: nada aqui toca o restante do JP Wealth.
function finpesApplyUnitNotice() {
  const el = document.getElementById('finpesUnitNotice');
  if (!el) return;
  const bloqueio = (typeof pfWriteBlockReason === 'function') ? pfWriteBlockReason() : null;
  el.hidden = !bloqueio;
}

function finpesApplyView(view) {
  FINPES_VIEWS.forEach(([key, id]) => {
    const el = document.getElementById(id);
    if (!el) return;
    const active = key === view;
    el.hidden = !active;
    el.inert = !active;
  });
  finpesApplyUnitNotice();
}

// Workspaces montados ao entrar (padrão EXEC_VIEW_RENDERERS): o Orçamento
// Mensal deriva tudo do estado vivo e repinta a cada entrada. Repintar não
// grava nada — render jamais escreve (contrato PF).
const FINPES_VIEW_RENDERERS = {
  overview: () => { if (window.JPWFinOverview && typeof window.JPWFinOverview.render === 'function') window.JPWFinOverview.render(); },
  mensal: () => { if (window.JPWFinBudget && typeof window.JPWFinBudget.render === 'function') { window.JPWFinBudget.render(); if (typeof window.JPWFinBudget.checkPending === 'function') window.JPWFinBudget.checkPending(); } },
  dividas: () => { if (window.JPWFinDebts && typeof window.JPWFinDebts.render === 'function') window.JPWFinDebts.render(); },
  comparativo: () => { if (window.JPWFinComparison && typeof window.JPWFinComparison.render === 'function') window.JPWFinComparison.render(); },
  cenarios: () => { if (window.JPWFinScenarios && typeof window.JPWFinScenarios.render === 'function') window.JPWFinScenarios.render(); },
};

function finpesSetView(view) {
  finpesView = view;
  finpesApplyView(view);
  // Montagem DEPOIS de tirar o hidden (medidas e foco — ver 13-exec-views).
  const render = FINPES_VIEW_RENDERERS[view];
  if (typeof render === 'function') render();
}

function finpesSelectView(view) {
  if (!FINPES_VIEWS.some(([key]) => key === view)) return false;
  finpesViewExplicit = true;
  finpesSetView(view);
  return true;
}

function finpesGetView() { return finpesView; }

// Destino inicial: entrar em Finanças Pessoais vindo de outra tela abre a
// Visão Geral. Mesmo mecanismo do Execution Board — observar .active cobre
// todos os caminhos de entrada sem embrulhar navigateToScreen.
function finpesWatchModuleEntry() {
  const screen = document.getElementById('finpes');
  if (!screen || typeof MutationObserver !== 'function') return;
  let wasActive = screen.classList.contains('active');
  const observer = new MutationObserver(() => {
    const isActive = screen.classList.contains('active');
    if (isActive && !wasActive && !finpesViewExplicit) {
      finpesSetView(FINPES_DEFAULT_VIEW);
      if (typeof syncNavSubCurrent === 'function') syncNavSubCurrent('finpes');
    }
    finpesViewExplicit = false;
    wasActive = isActive;
  });
  observer.observe(screen, { attributes: true, attributeFilter: ['class'] });
}

finpesApplyView(finpesView);
finpesWatchModuleEntry();

// Superfície pública consumida pelo controlador da faixa compartilhada
// (40-app/11-operational-shell.js, NAV_SUBMENU_SURFACES). Só chaves de UI.
window.JPWFin = { ui: { selectView: finpesSelectView, getView: finpesGetView } };
