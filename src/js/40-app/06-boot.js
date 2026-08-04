// ============ BOOT ============
function boot(){
  applyTheme(); applyRailState(); bindRailToggle(); applyFontScale(); startHeaderClock();
  renderThemeSeg(); renderFsSeg(); renderExplSeg(); renderAppIconConfig(); renderConfigQuarantine(); renderConfigOnboarding(); renderMEIConfig();
  renderParams(); renderMotor(); renderContas(); renderDash(); renderCheck();
  renderLedger(); renderPhases(); render();
  enhanceFieldNotes();
  // cotações ao vivo sempre que o programa abre (SET 4 do lote) — alimenta grade, ATR% e stop vivo
  if(!fxAutoFetchedThisSession){ fxAutoFetchedThisSession=true; updateFxRates(); }
  // questionário de início de período: primeiro a aparecer num painel recém-iniciado (SET 5b)
  if(!(S.onboarding&&S.onboarding.done) && !window.__onbShown){
    window.__onbShown=true;
    const bootEpoch=jpWealthPersistenceEpoch();
    setTimeout(()=>{
      if(jpWealthPersistenceIsBlocked() || bootEpoch!==jpWealthPersistenceEpoch()) return;
      openOnboardingModal();
    }, 350);
  }
}
$('modalOverlay').addEventListener('click',e=>{ if(e.target.id==='modalOverlay') closeModal(); });
document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeModal(); });
load(); if(typeof initSessionCheckpoint==='function') initSessionCheckpoint(); bindParams(); bindContab(); bindConfig(); bindAcct(); bindFieldNotes(); boot();
