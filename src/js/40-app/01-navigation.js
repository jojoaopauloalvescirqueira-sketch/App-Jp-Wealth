// ============ NAV ============
// Telas que migraram para a Central de Configurações (grupo "Operação"):
// qualquer navegação para elas — Ações Rápidas, CTAs, chamadas por string —
// abre a Central direto na subpágina equivalente. O gatilho de câmbio do
// Motor (1× por sessão) vive agora na abertura da subpágina, em
// 09-settings-modal.js (activateSettingsCategory).
const SCREEN_TO_SETTINGS_LEAF={params:'tool-params',motor:'tool-motor',check:'tool-check'};
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
