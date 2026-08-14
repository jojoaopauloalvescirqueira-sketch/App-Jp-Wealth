// ============ BOOT ============
function boot(){
  applyTheme(); applyRailState(); bindRailToggle(); applyFontScale(); applyNavStyle(); startHeaderClock();
  renderThemeSeg(); renderFsSeg(); renderExplSeg(); renderNavStyleSeg(); renderAppIconConfig(); renderConfigQuarantine(); renderConfigOnboarding(); renderMEIConfig();
  renderParams(); renderMotor(); renderContas(); renderDash(); renderCheck();
  renderLedger(); renderPhases(); render();
  // A-002: badge/visibilidade das Notas entram no ciclo global — sem isto, importar um
  // backup ou executar a Zona de Perigo (que substituem S e chamam boot()) deixava o
  // header com a contagem e a preferência showHeaderIcon anteriores. Guarda de
  // existência: boot() é o script 34 e 14-mvp-notes.js só carrega como 41 — na PRIMEIRA
  // execução (linha final deste arquivo) a função ainda não existe, e o próprio módulo
  // de Notas se renderiza ao carregar (initMvpNotes); aqui cobre todos os boots seguintes.
  if(typeof renderMvpNotesHeader==='function') renderMvpNotesHeader();
  // A-002, mesma doutrina: os workspaces do Execution Board montados sob demanda
  // (Estudos NoCoda e Estudos dos Pivots) só são desenhados ao ENTRAR neles, por
  // EXEC_VIEW_RENDERERS. Quem estivesse com um deles aberto quando S fosse
  // SUBSTITUÍDO — importação de backup, Zona de Perigo, finalização vinda de
  // outra aba — continuava vendo a tela do estado anterior, e pior: ela seguia
  // clicável, com os caminhos de ação morrendo em return silencioso porque o
  // estudo em foco já não existia. Repintar aqui fecha o ciclo para os dois.
  // Só o workspace VISÍVEL é redesenhado: montar num container `hidden` não
  // mede nada e o próprio execSetView() repinta na entrada seguinte.
  //
  // A guarda é o OBJETO window.JPWExec, e não `typeof execGetView==='function'`:
  // 13-exec-views.js é o script 61 e este boot é o 34, então na primeira
  // execução a declaração de função já está içada — o teste de tipo passaria —
  // mas o `let execView` que ela lê ainda está na zona morta temporal, e a
  // chamada estoura com "Cannot access 'execView' before initialization",
  // derrubando o boot inteiro. O objeto só passa a existir depois que o módulo
  // termina de avaliar, o que é exatamente a condição que se quer testar.
  if(window.JPWExec && window.JPWExec.ui && typeof window.JPWExec.ui.getView==='function'){
    const workspaceVisivel=window.JPWExec.ui.getView();
    if(workspaceVisivel==='pivots' && window.JPWPivotsUI && typeof window.JPWPivotsUI.render==='function') window.JPWPivotsUI.render();
    if(workspaceVisivel==='nocoda' && window.JPWNocodaUI && typeof window.JPWNocodaUI.render==='function') window.JPWNocodaUI.render();
  }
  // Governança de armazenamento (JPW-HJFGDE) — mesmo padrão de guarda: na PRIMEIRA
  // execução o módulo (16-storage-governance.js, script tardio) ainda não carregou e se
  // auto-renderiza ao carregar; aqui cobre os boots seguintes (import, wipe, finalize),
  // quando o status da pasta e o aviso de 30 dias precisam refletir a base recém-trocada.
  if(typeof renderDgStorageCard==='function') renderDgStorageCard();
  if(typeof renderDgBackupBanner==='function') renderDgBackupBanner();
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
