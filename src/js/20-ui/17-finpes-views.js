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
// Inline financial commands still commit on change. Only their repaint waits
// until the browser has completed Tab or the pointer gesture, so replacing
// the form cannot swallow the next click or move focus to BODY.
const finpesInlineRefreshes = new Map();
let finpesInlinePointerDown = false;
function finpesInlineIdentity(el){
  if(!el) return null;
  return Array.from(el.attributes).filter(a=>/^data-f[abcegin]-/.test(a.name) && a.name!=='data-fi-rule')
    .map(a=>[a.name,a.value]);
}
function finpesScheduleInlineRefresh(root, render){
  if(!root) return;
  const pending=finpesInlineRefreshes.get(root);
  if(pending) clearTimeout(pending.timer);
  const task={timer:null,render};
  const flush=()=>{
    if(finpesInlinePointerDown) return;
    finpesInlineRefreshes.delete(root);
    if(!root.isConnected) return;
    const active=document.activeElement, own=root.contains(active);
    const identity=own?finpesInlineIdentity(active):null;
    const draft=own&&'value' in active?{value:active.value,dirty:active.value!==active.defaultValue,
      start:active.selectionStart,end:active.selectionEnd,direction:active.selectionDirection}:null;
    const ghost=own&&active.dataset.fgRule?{rule:active.dataset.fgRule,field:active.dataset.fgCampo}:null;
    const scrolls=[];
    for(let node=active;own&&node;node=node.parentElement) if(node.scrollTop||node.scrollLeft) scrolls.push([node.id,node.scrollTop,node.scrollLeft]);
    task.render();
    if(!own || !identity?.length || document.activeElement.closest('dialog[open],.modal.show')) return;
    let target=Array.from(root.querySelectorAll('input,select,button,textarea')).find(el=>identity.every(([name,value])=>el.getAttribute(name)===value));
    if(!target&&ghost) target=Array.from(root.querySelectorAll('[data-fi-rule][data-fi-campo]'))
      .find(el=>el.dataset.fiRule===ghost.rule&&el.dataset.fiCampo===ghost.field);
    if(!target||target.disabled||target.closest('[hidden],[inert]')) return;
    target.focus({preventScroll:true});
    if(draft&&draft.dirty) target.value=draft.value;
    if(draft&&typeof draft.start==='number'&&typeof target.setSelectionRange==='function')
      try{target.setSelectionRange(draft.start,draft.end,draft.direction);}catch(_){}
    for(const [id,top,left] of scrolls){const el=id&&document.getElementById(id);if(el){el.scrollTop=top;el.scrollLeft=left;}}
  };
  task.flush=flush;
  finpesInlineRefreshes.set(root,task);
  task.timer=setTimeout(flush,0);
}
document.addEventListener('pointerdown',()=>{finpesInlinePointerDown=true;},true);
function finpesInlineEndPointer(){
  finpesInlinePointerDown=false;
  for(const task of finpesInlineRefreshes.values()){clearTimeout(task.timer);task.timer=setTimeout(task.flush,0);}
}
document.addEventListener('pointerup',finpesInlineEndPointer,true);
document.addEventListener('pointercancel',finpesInlineEndPointer,true);
window.addEventListener('blur',finpesInlineEndPointer);
