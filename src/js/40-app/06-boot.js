// ============ BOOT ============
// First access is presentation only. Account/period and backup writers remain canonical.
let jpwFirstAccessEmptyAtLoad=false;
let jpwFirstAccessFocusSession=null;
function jpwFirstAccessReleaseFocus({restore=true}={}){
  const session=jpwFirstAccessFocusSession;
  if(!session)return;
  jpwFirstAccessFocusSession=null;
  document.removeEventListener('keydown',session.keydown,true);
  document.removeEventListener('focusin',session.focusin,true);
  for(const [element,inert] of session.inerted)if(element.isConnected)element.inert=inert;
  for(const [name,value] of session.attributes){
    if(value===null)session.box.removeAttribute(name);else session.box.setAttribute(name,value);
  }
  if(restore)queueMicrotask(()=>{
    if(jpwFirstAccessFocusSession||document.querySelector('dialog[open]')||$('modalOverlay').classList.contains('show'))return;
    const target=session.opener;
    if(target?.isConnected&&!target.closest('[hidden],[inert]')&&target.getClientRects().length)target.focus({preventScroll:true});
    else window.JPWNavigation?.focusCurrentScreen();
  });
}
function jpwFirstAccessFocusModal(titleId,options={}){
  jpwFirstAccessReleaseFocus({restore:false});
  const overlay=$('modalOverlay'),box=$('modalBox'),title=document.getElementById(titleId);
  if(!overlay.classList.contains('show')||!title)return;
  const session={box,opener:options.opener||document.activeElement,inerted:[],attributes:[]};
  for(const name of ['role','aria-modal','aria-labelledby','tabindex'])session.attributes.push([name,box.getAttribute(name)]);
  box.setAttribute('role','dialog');box.setAttribute('aria-modal','true');box.setAttribute('aria-labelledby',titleId);box.setAttribute('tabindex','-1');
  for(const element of document.body.children){
    if(element===overlay||element.contains(overlay)||['SCRIPT','STYLE','LINK'].includes(element.tagName))continue;
    session.inerted.push([element,element.inert]);element.inert=true;
  }
  const visibleControls=()=>[...box.querySelectorAll('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(element=>
    !element.disabled&&!element.closest('[hidden],[inert]')&&element.getClientRects().length&&getComputedStyle(element).visibility!=='hidden');
  session.keydown=event=>{
    if(event.key!=='Tab'||event.defaultPrevented||document.querySelector('dialog[open]'))return;
    const controls=visibleControls();
    if(!controls.length){event.preventDefault();box.focus();return;}
    const index=controls.indexOf(document.activeElement);
    if(event.shiftKey&&(index<=0)||!event.shiftKey&&(index<0||index===controls.length-1)){
      event.preventDefault();controls[event.shiftKey?controls.length-1:0].focus();
    }
  };
  session.focusin=event=>{
    if(jpwFirstAccessFocusSession!==session||box.contains(event.target)||document.querySelector('dialog[open]'))return;
    (visibleControls()[0]||box).focus({preventScroll:true});
  };
  jpwFirstAccessFocusSession=session;
  document.addEventListener('keydown',session.keydown,true);
  document.addEventListener('focusin',session.focusin,true);
  title.setAttribute('tabindex','-1');title.focus({preventScroll:true});
}
function openFirstAccessWelcome(){
  if(jpWealthPersistenceIsBlocked()||document.querySelector('dialog[open]'))return false;
  if($('modalOverlay').classList.contains('show')&&closeModal()===false)return false;
  const box=$('modalBox');
  box.classList.add('jpw-welcome-modal');box.dataset.onboardingSession='welcome';
  box.innerHTML=`
    <section id="jpwWelcome" class="jpw-welcome">
      <header class="jpw-welcome-header"><img class="jpw-welcome-logo" src="${window.JPW_PORTABLE_IMAGES?.['assets/jp-wealth-brand-red.png']||'assets/jp-wealth-brand-red.png'}" alt="JP Wealth"><button type="button" id="jpwWelcomeClose" class="modal-btn cancel">Fechar</button></header>
      <div class="jpw-welcome-body">
        <section id="jpwWelcomeChoices"><h1 id="jpwWelcomeTitle">Bem-vindo ao JP Wealth.</h1><p>Organize sua gestão. Escolha por onde começar.</p>
          <div class="jpw-welcome-actions">
            <button type="button" id="jpwWelcomeStart" class="jpw-welcome-choice"><strong>Começar do zero</strong><span>Escolher a primeira tarefa e preparar seu contexto.</span></button>
            <button type="button" id="jpwWelcomeRestore" class="jpw-welcome-choice"><strong>Restaurar Backup Completo</strong><span>Conferir um arquivo antes de importar seus dados.</span></button>
            <button type="button" id="jpwWelcomeExplore" class="jpw-welcome-choice"><strong>Conhecer o app</strong><span>Consultar as áreas disponíveis, sem preparar uma operação.</span></button>
          </div>
        </section>
        <section id="jpwWelcomeTasks" hidden inert><h2 id="jpwWelcomeTasksTitle" tabindex="-1">Escolha sua primeira tarefa.</h2><p>Cada área terá seus próprios dados e confirmações.</p>
          <div class="jpw-welcome-actions">
            <button type="button" id="jpwWelcomeForex" class="jpw-welcome-choice"><strong>Preparar conta Forex</strong><span>Identificar uma conta, depois conferir seu período. Nenhuma senha é necessária.</span></button>
            <button type="button" id="jpwWelcomeFinance" class="jpw-welcome-choice"><strong>Organizar Finanças Pessoais</strong><span>Consultar orçamento, receitas e despesas.</span></button>
            <button type="button" id="jpwWelcomeNotes" class="jpw-welcome-choice"><strong>Começar pelas Notas</strong><span>Organizar seus registros e tarefas.</span></button>
          </div>
          <button type="button" id="jpwWelcomeBack" class="modal-btn cancel">Voltar</button>
        </section>
        <p id="jpwWelcomeStatus" role="status" aria-live="polite"></p>
        <aside class="jpw-welcome-note"><strong>Seus dados ficam neste navegador.</strong><p>O endereço local e o hospedado usam bases separadas. Mantenha um Backup Completo fora do navegador. A pasta de exportação guarda cópias; ela não substitui a base ativa.</p></aside>
        <input id="jpwWelcomeFile" type="file" accept=".json,application/json" hidden>
      </div>
    </section>`;
  const status=message=>{$('jpwWelcomeStatus').textContent=message;};
  const available=primary=>window.JPWModuleAvailability?.canAccess(primary)!==false;
  const leave=()=>{
    // No account preparation, consent or preference is written by dismissing this view.
    jpwFirstAccessEmptyAtLoad=false;
    return closeModal();
  };
  $('jpwWelcomeClose').onclick=leave;
  $('jpwWelcomeStart').onclick=()=>{
    $('jpwWelcomeChoices').hidden=true;$('jpwWelcomeChoices').inert=true;
    $('jpwWelcomeTasks').hidden=false;$('jpwWelcomeTasks').inert=false;
    status('');$('jpwWelcomeTasksTitle').focus({preventScroll:true});
  };
  $('jpwWelcomeBack').onclick=()=>{
    $('jpwWelcomeTasks').hidden=true;$('jpwWelcomeTasks').inert=true;
    $('jpwWelcomeChoices').hidden=false;$('jpwWelcomeChoices').inert=false;
    status('');$('jpwWelcomeStart').focus({preventScroll:true});
  };
  $('jpwWelcomeExplore').onclick=()=>{if(leave()!==false)window.JPWNavigation?.navigate('dashboard');};
  $('jpwWelcomeRestore').onclick=()=>$('jpwWelcomeFile').click();
  $('jpwWelcomeFile').onchange=event=>{
    const file=event.target.files?.[0];if(!file)return;
    if(leave()!==false)importFullBackupFile(file);
  };
  $('jpwWelcomeForex').onclick=()=>{
    if(!available('forex')){status('Forex está congelado. Você pode rever sua disponibilidade nas Configurações ou escolher outra área.');return;}
    if(!window.JPWFXConsolidatedUI?.openAccountRegistration){status('O cadastro ainda não está disponível. Tente novamente quando o app terminar de carregar.');return;}
    if(leave()===false)return;
    if(window.JPWNavigation?.navigate('forex-management-accounts')===true)
      window.JPWFXConsolidatedUI.openAccountRegistration({returnFocus:document.getElementById('fxAccountsCreate')});
  };
  $('jpwWelcomeFinance').onclick=()=>{
    if(!available('personal-finance')){status('Finanças Pessoais está congelado. Confira as Configurações ou escolha outra área.');return;}
    if(leave()!==false)window.JPWNavigation?.navigate('personal-finance');
  };
  $('jpwWelcomeNotes').onclick=()=>{
    if(leave()!==false){window.JPWNavigation?.navigate('dashboard');if(typeof openMvpNotesDrawer==='function')openMvpNotesDrawer(document.getElementById('headerNotesBtn'));}
  };
  $('modalOverlay').classList.add('show');jpwFirstAccessFocusModal('jpwWelcomeTitle');
  return true;
}
window.JPWFirstAccess=Object.freeze({open:openFirstAccessWelcome,focusModal:jpwFirstAccessFocusModal});

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
  // An empty browser starts with the app welcome, never a financial period writer.
  if(jpwFirstAccessEmptyAtLoad && !window.__onbShown){
    window.__onbShown=true;
    const bootEpoch=jpWealthPersistenceEpoch();
    setTimeout(()=>{
      if(jpWealthPersistenceIsBlocked() || bootEpoch!==jpWealthPersistenceEpoch()) return;
      openFirstAccessWelcome();
    }, 350);
  }
}
$('modalOverlay').addEventListener('click',e=>{ if(e.target.id==='modalOverlay') closeModal(); });
// Nested dialogs own a handled Escape. Closing an already hidden shared modal
// would also notify its observers and incorrectly release the Settings backdrop.
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'&&!e.defaultPrevented&&$('modalOverlay').classList.contains('show')) closeModal();
});
load();
jpwFirstAccessEmptyAtLoad=jpWealthLastPersistedRawGet()===null&&!jpWealthPersistenceIsBlocked();
if(S?.workspaceRecovery?.pending)jpwWorkspaceResume(); if(typeof initSessionCheckpoint==='function') initSessionCheckpoint(); bindParams(); bindContab(); bindConfig(); bindAcct(); bindFieldNotes(); boot();
