// ============ NAV ============
// Telas que vivem na Central de Configurações (grupo "Operação"): qualquer
// navegação para elas — Ações Rápidas, CTAs, chamadas por string — abre a
// Central direto na subpágina equivalente.
//
// O gatilho de câmbio do Motor (1× por sessão) NÃO vive aqui e nunca viveu na
// Central: está em 40-app/06-boot.js, incondicional no boot. O ramo que existia
// em 09-settings-modal.js era código morto — 06-boot.js carrega antes e a flag
// nunca é resetada — e saiu junto com a migração do Motor.
const SCREEN_TO_SETTINGS_LEAF={params:'tool-params',check:'tool-check'};
// Destinos que deixaram de ser tela própria e viraram workspace de um módulo.
// Sem este desvio, navigateToScreen('motor') limparia .active de todas as telas
// e sairia no `if(!screen) return` sem ativar nenhuma — o app ficaria sem tela
// visível. Mesma forma do mapa acima, que este substitui para o Motor de Lote.
const SCREEN_TO_MODULE_VIEW={motor:{screen:'exec',view:'motor'}};
function navigateToScreen(t){
  const screenId=typeof t==='string'?t:t.dataset.screen;
  if(screenId==='config'){
    if(typeof openSettingsModal==='function') openSettingsModal('about',typeof t==='string'?$('headerConfigBtn'):t);
    return;
  }
  if(SCREEN_TO_SETTINGS_LEAF[screenId]){
    const opener=typeof t==='string'?(document.activeElement instanceof HTMLElement?document.activeElement:undefined):t;
    if(typeof openSettingsModal==='function') openSettingsModal(SCREEN_TO_SETTINGS_LEAF[screenId],opener);
    return;
  }
  const moduleView=SCREEN_TO_MODULE_VIEW[screenId];
  if(moduleView){
    navigateToScreen(moduleView.screen);
    if(window.JPWExec&&window.JPWExec.ui&&typeof window.JPWExec.ui.selectView==='function')
      window.JPWExec.ui.selectView(moduleView.view);
    return;
  }
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));
  const activeTab=typeof t==='string'
    ? document.querySelector('.tab[data-screen="'+CSS.escape(screenId)+'"]')
    : (t.classList.contains('tab')?t:null);
  if(activeTab) activeTab.classList.add('active');
  const screen=$(screenId);
  if(!screen) return;
  screen.classList.add('active');
  // Ponto único de troca de aba: o destaque deslizante da navegação em pílula é
  // reposicionado aqui, e não no clique, para cobrir também as chamadas por
  // string (CTAs e Ações Rápidas). Guarda de existência porque 12-nav-style.js
  // é módulo de apresentação e pode não estar carregado num monólito reduzido.
  if(typeof scheduleNavPill==='function') scheduleNavPill();
  window.scrollTo({top:0,behavior:'smooth'});
  maybeShowOnboardingNavReminder(screenId);
}
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>navigateToScreen(t)));
$('fxUpdateBtn').addEventListener('click',()=>updateFxRates());
