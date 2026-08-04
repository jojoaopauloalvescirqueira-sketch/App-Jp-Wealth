// ============ NAV ============
function navigateToScreen(t){
  const screenId=typeof t==='string'?t:t.dataset.screen;
  if(screenId==='config'){
    if(typeof openSettingsModal==='function') openSettingsModal('about',typeof t==='string'?$('headerConfigBtn'):t);
    return;
  }
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));
  if(typeof t!=='string'&&t.classList.contains('tab')) t.classList.add('active');
  const screen=$(screenId);
  if(!screen) return;
  screen.classList.add('active');
  window.scrollTo({top:0,behavior:'smooth'});
  maybeShowOnboardingNavReminder(screenId);
  if(screenId==='motor' && !fxAutoFetchedThisSession){
    fxAutoFetchedThisSession=true;
    updateFxRates(); // tentativa automática, silenciosa se offline (status visível, nunca falha em silêncio)
  }
}
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>navigateToScreen(t)));
$('fxUpdateBtn').addEventListener('click',()=>updateFxRates());
