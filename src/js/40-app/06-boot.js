// ============ BOOT ============
function boot(){
  applyTheme(); applyRailState(); bindRailToggle(); applyFontScale(); startHeaderClock();
  renderThemeSeg(); renderFsSeg(); renderExplSeg(); renderAppIconConfig(); renderConfigQuarantine(); renderConfigOnboarding(); renderMEIConfig();
  renderParams(); renderMotor(); renderContas(); renderDash(); renderCheck();
  renderLedger(); renderPhases(); render();
  // A-002: badge/visibilidade das Notas entram no ciclo global — sem isto, importar um
  // backup ou executar a Zona de Perigo (que substituem S e chamam boot()) deixava o
  // header com a contagem e a preferência showHeaderIcon anteriores. Guarda de
  // existência: boot() é o script 34 e 14-mvp-notes.js só carrega como 41 — na PRIMEIRA
  // execução (linha final deste arquivo) a função ainda não existe, e o próprio módulo
  // de Notas se renderiza ao carregar (initMvpNotes); aqui cobre todos os boots seguintes.
  if(typeof renderMvpNotesHeader==='function') renderMvpNotesHeader();
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
