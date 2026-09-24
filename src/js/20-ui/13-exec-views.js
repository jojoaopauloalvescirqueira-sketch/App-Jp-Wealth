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

// Chave de visão -> id do container. O Painel Operacional mantém o #execWidgetGrid
// original; History reutiliza #execHistory como workspace independente.
const EXEC_VIEWS = [
  ['panel', 'execWidgetGrid'],
  ['accounting', 'contab'],
  ['history', 'execHistory'],
  // Contas preserva o mesmo #contas e o mesmo renderer cadastral. Tornou-se
  // apenas uma visão local entre Painel e Motor, sem cópia ou nova fonte de dados.
  ['accounts', 'contas'],
  // Motor de Lote: o container e o proprio #motorWidgetGrid migrado de
  // Configuracoes, nao um wrapper novo. renderMotor() ja o desenha no boot e o
  // redesenha por mudanca de dado — nao ha render on-demand a fazer aqui.
  ['motor', 'motorWidgetGrid']
];
// Workspaces cujo conteúdo depende de estado vivo são montados ao entrar.
const EXEC_VIEW_RENDERERS = {
  // Ledger e histórico têm fontes vivas; consultar não altera os fatos.
  accounts: () => { window.JPWForex?.accountsUI?.render(); },
  accounting: () => { if (typeof renderLedger === 'function') renderLedger(); },
  history: () => { if (window.JPWHistoryUI?.render) window.JPWHistoryUI.render(); }
};
const EXEC_DEFAULT_VIEW = 'panel';
let execView = EXEC_DEFAULT_VIEW;
// Marca de escolha explícita do usuário. Existe porque navegar para o módulo e
// escolher a visão acontecem no mesmo gesto quando o clique parte da faixa: sem
// ela, o destino inicial atropelaria a escolha que acabou de ser feita.
let execViewExplicit = false;

function execApplyView(view) {
  // A tabela e o painel legado compartilham o mesmo destino, sem desmontar nós.
  const board = document.getElementById('executionBoard');
  if (board) { board.hidden = view !== 'panel'; board.inert = view !== 'panel'; }
  EXEC_VIEWS.forEach(([key, id]) => {
    const el = document.getElementById(id);
    if (!el) return;
    const active = key === view;
    el.hidden = !active;
    el.inert = !active;
  });
}

// Compatibilidade com consumidores antigos: History agora tem destino próprio.
function execToggleHistory(open){
  return window.JPWNavigation?.navigateLocal('exec',open?'history':'accounting')===true;
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
  if(view==='overview') return window.JPWNavigation?.navigate('forex-overview')===true;
  // Compatibilidade de API: consumidores legados não recuperam ownership Exec.
  // O shim delega ao resolver canônico e não altera `execView`.
  const researchView={ecal:'calendar',nocoda:'nocoda',pivots:'pivots'}[view];
  if(researchView&&window.JPWNavigation&&typeof window.JPWNavigation.navigateLocal==='function'){
    return window.JPWNavigation.navigateLocal('research',researchView);
  }
  if (!EXEC_VIEWS.some(([key]) => key === view)) return false;
  if(view!==execView&&execView==='panel'&&window.JPWForex?.executionBoardUI&&!JPWForex.executionBoardUI.guardNavigation({screen:'exec',localView:{view}},()=>execSelectView(view)))return false;
  if(view!==execView&&execView==='accounts'&&window.JPWForex?.accountsUI?.guardNavigation&&!JPWForex.accountsUI.guardNavigation({screen:'exec',localView:{view}},()=>execSelectView(view)))return false;
  execViewExplicit = true;
  execSetView(view);
  return true;
}

function execGetView() { return execView; }

// Destino inicial do módulo: entrar no Execution Board vindo de outra tela abre
// o Painel Operacional. Observar a classe .active cobre TODOS os caminhos de entrada —
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


// Contexto expandido é somente apresentação. O nó completo e as preferências
// dos widgets permanecem os mesmos; não há escrita nem cópia do estado.
function fxSetContextExpanded(expanded){
  const overview=document.getElementById('execOverview'),root=document.getElementById('fxconsolidated');
  if(!overview||!root||!root.contains(overview)) return false;
  overview.hidden=!expanded;overview.inert=!expanded;
  root.classList.toggle('fx-context-expanded',!!expanded);
  const button=document.getElementById('fxContextToggle');
  button.setAttribute('aria-expanded',String(!!expanded));
  button.textContent=expanded?'Recolher contexto':'Ver contexto completo';
  return true;
}

// Um único checklist, movido para uma janela nativa. Os listeners/valores e a
// gravação durante o preenchimento pertencem ao renderer original.
let fxChecklistDialog=null,fxChecklistOpener=null;
function fxCanOpenChecklist(){
  return !document.getElementById('modalOverlay')?.classList.contains('show') &&
    !document.querySelector('dialog[open]:not(#forexChecklistDialog)');
}
function fxOpenChecklist(opener=document.activeElement){
  if(!fxCanOpenChecklist()) return false;
  if(fxChecklistDialog?.open){document.getElementById('forexChecklistClose').focus();return true;}
  const grid=document.getElementById('checkWidgetGrid');if(!grid)return false;
  if(!fxChecklistDialog){
    fxChecklistDialog=document.createElement('dialog');fxChecklistDialog.id='forexChecklistDialog';
    fxChecklistDialog.className='fx-checklist-dialog';fxChecklistDialog.setAttribute('aria-labelledby','forexChecklistTitle');
    fxChecklistDialog.innerHTML='<header class="fx-checklist-heading"><div><h2 id="forexChecklistTitle">Checklist pré-trade</h2><p>As respostas são gravadas durante o preenchimento. Fechar mantém as respostas.</p></div><button type="button" id="forexChecklistClose">Fechar</button></header><div id="forexChecklistBody"></div>';
    document.body.append(fxChecklistDialog);
    document.getElementById('forexChecklistClose').addEventListener('click',()=>fxChecklistDialog.close());
    fxChecklistDialog.addEventListener('cancel',event=>{event.preventDefault();fxChecklistDialog.close();});
    fxChecklistDialog.addEventListener('keydown',event=>{if(event.key==='Escape')event.stopPropagation();});
    fxChecklistDialog.addEventListener('close',()=>{
      document.getElementById('check').append(document.getElementById('checkWidgetGrid'));
      if(typeof restoreSettingsAfterSubdialog==='function')restoreSettingsAfterSubdialog();
      const target=fxChecklistOpener;fxChecklistOpener=null;
      requestAnimationFrame(()=>{if(target?.isConnected&&!target.closest('[inert],[hidden]')&&target.getClientRects().length)target.focus({preventScroll:true});});
    });
  }
  fxChecklistOpener=opener;
  document.getElementById('forexChecklistBody').append(grid);
  if(typeof settingsMarkSubdialogLauncher==='function')settingsMarkSubdialogLauncher(opener);
  if(typeof suspendSettingsForSubdialog==='function')suspendSettingsForSubdialog();
  fxChecklistDialog.showModal();document.getElementById('forexChecklistClose').focus();
  return true;
}
document.getElementById('execChecklistBtn')?.addEventListener('click',event=>fxOpenChecklist(event.currentTarget));
