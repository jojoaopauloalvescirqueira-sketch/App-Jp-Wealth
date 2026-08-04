// ============ NAV ============
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  $(t.dataset.screen).classList.add('active');
  window.scrollTo({top:0,behavior:'smooth'});
  maybeShowOnboardingNavReminder(t.dataset.screen);
  if(t.dataset.screen==='motor' && !fxAutoFetchedThisSession){
    fxAutoFetchedThisSession=true;
    updateFxRates(); // tentativa automática, silenciosa se offline (status visível, nunca falha em silêncio)
  }
}));
$('fxUpdateBtn').addEventListener('click',()=>updateFxRates());
