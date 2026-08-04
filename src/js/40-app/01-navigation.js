// ============ NAV ============
function navigateToScreen(t){
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));
  if(t.classList.contains('tab')) t.classList.add('active');
  const screen=$(t.dataset.screen);
  if(!screen) return;
  screen.classList.add('active');
  window.scrollTo({top:0,behavior:'smooth'});
  maybeShowOnboardingNavReminder(t.dataset.screen);
  if(t.dataset.screen==='motor' && !fxAutoFetchedThisSession){
    fxAutoFetchedThisSession=true;
    updateFxRates(); // tentativa automática, silenciosa se offline (status visível, nunca falha em silêncio)
  }
}
document.querySelectorAll('.tab, .header-action[data-screen]').forEach(t=>t.addEventListener('click',()=>navigateToScreen(t)));
$('fxUpdateBtn').addEventListener('click',()=>updateFxRates());
