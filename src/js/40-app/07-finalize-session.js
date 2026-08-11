// ============ FINALIZAR SESSÃO — privacidade em computador de terceiros (N1/N2) ============
const SESSION_CHECKPOINT_KEY='jpwealth_session_checkpoint_v1';
const SESSION_WIPE_CHANNEL='jpwealth_session_events_v1';
const SESSION_WIPE_STORAGE_KEY='jpwealth_session_wipe_signal_v1';
const JP_WEALTH_AUX_STORAGE_KEYS=['jpw_rail','jpw_expl','jpw_fs','jpwealth_v9_icon_theme','jpwealth_v9_icon_choice','jpwealth_galton_preferences_v1',SESSION_WIPE_STORAGE_KEY];
let sessionCheckpointValue=null;
let sessionFinalizeEntry='safe';
let sessionFinalizeBackStep='safe';
let sessionFinalizeExportMeta=null;
let sessionFinalizeExportFingerprint=null;
let sessionFinalizeExportAcknowledged=false;
let sessionNoticeTimer=null;
let sessionCrossTabChannel=null;
let sessionLastWipeToken=null;
if(!Number.isFinite(window.JP_WEALTH_SESSION_WIPE_EPOCH)) window.JP_WEALTH_SESSION_WIPE_EPOCH=0;

function sessionResetAuxiliarySurfaces(){
  // Invalida controladores que ainda retêm preferências auxiliares em memória.
  // O epoch impede regravação mesmo se um hook visual falhar durante o wipe.
  window.JP_WEALTH_SESSION_WIPE_EPOCH+=1;
  if(typeof handleGaltonSessionWipe==='function'){
    try{ handleGaltonSessionWipe(); }catch(error){}
  }
}

function sessionStableValue(value){
  if(Array.isArray(value)) return value.map(sessionStableValue);
  if(value && typeof value==='object'){
    const out={};
    Object.keys(value).sort().forEach(k=>{ out[k]=sessionStableValue(value[k]); });
    return out;
  }
  return value;
}
function sessionStateFingerprint(){
  const snapshot=structuredClone(S);
  // Preço e data entram deliberadamente: falso positivo de FX é preferível à perda silenciosa.
  // A senha de investidor sai do fingerprint pela mesma política que a tira do save():
  // ela é de sessão, nunca persiste — digitá-la não pode acusar "alterações não salvas"
  // de algo que, por desenho, jamais será salvo.
  if(Array.isArray(snapshot.accounts)) snapshot.accounts.forEach(a=>{ if(a) a.investorPassword=''; });
  if(snapshot.onboarding) snapshot.onboarding.investorPassword='';
  return JSON.stringify(sessionStableValue(snapshot));
}
function sessionCheckpointStorageGet(){
  try{ return sessionStorage.getItem(SESSION_CHECKPOINT_KEY); }catch(e){ return null; }
}
function sessionCheckpointStorageSet(value){
  try{ sessionStorage.setItem(SESSION_CHECKPOINT_KEY,value); }catch(e){}
}
function sessionCheckpointStorageRemove(){
  try{ sessionStorage.removeItem(SESSION_CHECKPOINT_KEY); }catch(e){}
}
function initSessionCheckpoint(){
  if(typeof S==='undefined' || !S) return;
  const current=sessionStateFingerprint();
  const saved=sessionCheckpointStorageGet();
  sessionCheckpointValue=saved || current;
  if(!saved) sessionCheckpointStorageSet(current);
}
function markSessionCheckpoint(){
  setSessionCheckpointValue(sessionStateFingerprint());
}
function setSessionCheckpointValue(value){
  sessionCheckpointValue=value;
  sessionCheckpointStorageSet(sessionCheckpointValue);
}
function sessionHasChanges(){
  if(sessionCheckpointValue===null) initSessionCheckpoint();
  return sessionCheckpointValue!==sessionStateFingerprint();
}
function clearSessionCheckpoint(){
  sessionCheckpointValue=null;
  sessionCheckpointStorageRemove();
}
function sessionWipeToken(){
  return Date.now().toString(36)+'_'+Math.random().toString(36).slice(2);
}
function sessionNotifyFinalized(){
  const message={type:'jpwealth-session-finalized',token:sessionWipeToken()};
  sessionLastWipeToken=message.token;
  if(sessionCrossTabChannel){
    try{ sessionCrossTabChannel.postMessage(message); }catch(e){}
  }
  try{
    localStorage.setItem(SESSION_WIPE_STORAGE_KEY,JSON.stringify(message));
    localStorage.removeItem(SESSION_WIPE_STORAGE_KEY);
  }catch(e){}
}
function sessionHandleRemoteFinalization(message){
  if(!message || message.type!=='jpwealth-session-finalized' || message.token===sessionLastWipeToken) return;
  sessionLastWipeToken=message.token;
  blockJPWealthPersistence();
  const report=clearJPWealthLocalData({removeAuxiliary:true,removeCorrupted:true});
  if(!report.ok){
    showSessionNotice('Outra aba finalizou a sessão, mas algumas chaves não puderam ser removidas: '+report.failures.join(', '));
    return;
  }
  sessionResetAuxiliarySurfaces();
  S=emptyJPWealthState();
  persistNotesAfterSessionWipe();
  window.__onbShown=true;
  clearSessionCheckpoint();
  closeModal();
  boot();
  window.__onbShown=false;
  initSessionCheckpoint();
  showSessionNotice('Sessão finalizada em outra aba. Os dados locais do JP Wealth foram removidos deste navegador. As Notas do MVP — incluindo pastas, histórico de concluídos e preferências do painel — não foram apagadas e continuam salvas.');
}
function initSessionCrossTab(){
  if(typeof BroadcastChannel==='function'){
    try{
      sessionCrossTabChannel=new BroadcastChannel(SESSION_WIPE_CHANNEL);
      sessionCrossTabChannel.addEventListener('message',e=>sessionHandleRemoteFinalization(e.data));
    }catch(e){ sessionCrossTabChannel=null; }
  }
  window.addEventListener('storage',e=>{
    if(e.key!==SESSION_WIPE_STORAGE_KEY || !e.newValue) return;
    try{ sessionHandleRemoteFinalization(JSON.parse(e.newValue)); }catch(error){}
  });
}
function localStorageKeys(){
  const keys=[];
  try{ for(let i=0;i<localStorage.length;i++){ const key=localStorage.key(i); if(key) keys.push(key); } }catch(e){}
  return keys;
}
function clearJPWealthLocalData(options={}){
  // Cinto central (A-005): em modo de recuperação, NADA remove a chave principal nem as
  // cópias _corrompido_ — nem Finalizar Sessão local, nem a finalização vinda de outra
  // aba (sessionHandleRemoteFinalization), nem a Zona de Perigo. Os chamadores já tratam
  // report.ok===false como interrupção antes de qualquer mutação de S ou regravação.
  if(typeof jpWealthLoadRecoveryActive==='function' && jpWealthLoadRecoveryActive()){
    return {ok:false, failures:['banco em modo de recuperação — o conteúdo original e as cópias estão protegidos até uma decisão de recuperação'], removedKeys:[]};
  }
  const removeAuxiliary=options.removeAuxiliary===true;
  const removeCorrupted=options.removeCorrupted===true;
  const keys=[LSKEY];
  if(removeCorrupted) localStorageKeys().filter(k=>k.startsWith(LSKEY+'_corrompido_')).forEach(k=>keys.push(k));
  if(removeAuxiliary) JP_WEALTH_AUX_STORAGE_KEYS.forEach(k=>keys.push(k));
  const failures=[];
  [...new Set(keys)].forEach(key=>{
    try{
      localStorage.removeItem(key);
      if(localStorage.getItem(key)!==null) failures.push(key);
    }catch(e){ failures.push(key); }
  });
  if(removeAuxiliary){
    try{
      sessionStorage.removeItem(SESSION_CHECKPOINT_KEY);
      if(sessionStorage.getItem(SESSION_CHECKPOINT_KEY)!==null) failures.push(SESSION_CHECKPOINT_KEY);
    }catch(e){ failures.push(SESSION_CHECKPOINT_KEY); }
  }
  return {ok:failures.length===0, failures, removedKeys:keys};
}
function emptyJPWealthState(){
  const empty=structuredClone(DEFAULTS);
  empty.params={...empty.params, saldoIni:0, saldoAtu:0, inicio:''};
  empty.accounts=[];
  empty.ledger=[];
  empty.ledgerArchive=[];
  empty.transitionLog=[];
  empty.cycleRealizado=0;
  empty.quarantine=null;
  empty.riskPinHash=null;
  empty.phaseUnlocked=[true,false,false,false];
  empty.period={nome:'',profile:'base'};
  empty.onboarding=structuredClone(DEFAULTS.onboarding);
  empty.onboarding.done=false;
  // Terceiro caminho de nascimento do estado (além de DEFAULTS fresco e migrate):
  // o clone herda o reserveMasterCapital derivado de DEFAULTS.params.saldoIni, mas
  // este estado vazio acabou de zerar saldoIni — reconciliar com a MESMA fórmula
  // canônica, senão o reload (migrate) reescreve e o checkpoint acusa falso dirty.
  empty.onboarding.reserveMasterCapital=String(empty.params.saldoIni||0);
  empty.perf=[];
  empty.phases=empty.phases.map((phase,i)=>({...phase,orders:emptyOrders([5,4,3,2][i]||3)}));
  if(Array.isArray(empty.checklist)) empty.checklist=empty.checklist.map(group=>({...group,items:group.items.map(item=>({...item,v:0}))}));
  if(empty.mei){ empty.mei.history=[]; empty.mei.lastCalibrationAt=''; }
  // Notas do MVP são um backlog acumulado ao longo de todo o período de testes,
  // não um dado operacional da sessão — sobrevivem a Finalizar Sessão (ao contrário
  // de ordens, ledger, onboarding etc., zerados acima). 'S' aqui ainda é o estado
  // anterior à troca (a reatribuição só ocorre no retorno desta função).
  empty.mvpNotes=(S&&S.mvpNotes)?structuredClone(S.mvpNotes):structuredClone(DEFAULTS.mvpNotes);
  return empty;
}
// clearJPWealthLocalData() acima de cada chamador já apagou a chave inteira, e save()
// normal fica bloqueado (jpWealthPersistenceBlocked) até o operador reengajar o
// onboarding ou importar backup — de propósito, para não ressuscitar dado limpo à toa.
// Sem isto, as notas ficariam só em memória e sumiriam se a aba fosse fechada antes
// desse reengajamento. Escrita direta, única e deliberada — não reabre o portão geral
// de save(); os demais campos gravados aqui já estão zerados, então persisti-los agora
// ou só depois produz o mesmo resultado observável.
function persistNotesAfterSessionWipe(){
  // Guarda A-005: escrita direta na chave principal jamais pode rodar em modo de
  // recuperação — regravaria o banco problemático com o estado provisório. Protege os
  // dois chamadores (fluxo local e finalização vinda de outra aba) num ponto só.
  if(typeof jpWealthLoadRecoveryActive==='function' && jpWealthLoadRecoveryActive()) return;
  try{ localStorage.setItem(LSKEY,JSON.stringify(S)); }catch(e){}
}
function showSessionNotice(message){
  const el=$('sessionNotice'); if(!el) return;
  el.textContent=message; el.classList.add('show');
  clearTimeout(sessionNoticeTimer);
  sessionNoticeTimer=setTimeout(()=>el.classList.remove('show'),8000);
}
function resetSessionFinalizeEphemeralState(){
  sessionFinalizeEntry='safe';
  sessionFinalizeBackStep='safe';
  sessionFinalizeExportMeta=null;
  sessionFinalizeExportFingerprint=null;
  sessionFinalizeExportAcknowledged=false;
}
function sessionModal(html){
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  box.classList.remove('onboarding-modal');
  box.innerHTML=html;
}
function sessionCancelBinding(){
  const b=$('sessionCancel');
  if(b) b.addEventListener('click',()=>{ resetSessionFinalizeEphemeralState(); closeModal(); });
}
function sessionFormatExportDate(iso){
  try{ return new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'medium'}).format(new Date(iso)); }
  catch(e){ return String(iso||''); }
}
function sessionExportError(error){
  sessionModal('<h3>Exportação não concluída</h3>'+
    '<p class="modal-sub">A base não será considerada protegida e a exclusão não pode prosseguir.</p>'+
    '<div class="session-error" role="alert">'+esc(error&&error.message?error.message:'Não foi possível iniciar a exportação.')+'</div>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button><button type="button" class="modal-btn confirm" id="sessionRetryExport">Tentar novamente</button></div>');
  sessionCancelBinding();
  $('sessionRetryExport').addEventListener('click',()=>beginSessionExport());
}
function renderSessionExportConfirmation(){
  const meta=sessionFinalizeExportMeta;
  sessionModal('<h3>Exportação iniciada</h3>'+
    '<p class="modal-sub">O backup completo foi preparado com a política existente de senhas de investidor.</p>'+
    '<div class="session-export-facts"><div><span>Arquivo</span><code>'+esc(meta.filename)+'</code></div>'+
    '<div><span>Data e hora</span><b>'+esc(sessionFormatExportDate(meta.exportedAt))+'</b></div></div>'+
    '<p class="session-warning">O navegador não consegue verificar fisicamente se o arquivo foi guardado. Localize o arquivo antes de continuar.</p>'+
    '<label class="session-check-row"><input type="checkbox" id="sessionExportAcknowledged" '+(sessionFinalizeExportAcknowledged?'checked':'')+'> <span>Confirmo que o download foi concluído e que localizei o arquivo de backup.</span></label>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button><button type="button" class="modal-btn confirm" id="sessionExportContinue" '+(sessionFinalizeExportAcknowledged?'':'disabled')+'>Continuar</button></div>');
  sessionCancelBinding();
  $('sessionExportAcknowledged').addEventListener('change',e=>{
    sessionFinalizeExportAcknowledged=e.target.checked;
    $('sessionExportContinue').disabled=!e.target.checked;
  });
  $('sessionExportContinue').addEventListener('click',()=>{
    if(!sessionFinalizeExportAcknowledged) return;
    setSessionCheckpointValue(sessionFinalizeExportFingerprint||sessionStateFingerprint());
    renderSessionDeleteConfirmation('export');
  });
}
async function beginSessionExport(){
  try{
    // exportFullBackup é async (JPW-HJFGDE): resolve o destino (pasta padrão autorizada
    // ou Downloads), aplica a nomenclatura progressiva e nunca lança nem faz fallback
    // silencioso. quiet: a confirmação visual deste fluxo é o próprio modal de sessão.
    const meta=await exportFullBackup({quiet:true});
    if(!meta) throw new Error('A exportação não foi concluída — nenhum arquivo foi gerado. Resolva o acesso à pasta padrão da base (ou exporte excepcionalmente para Downloads) e tente novamente.');
    if(!meta.filename) throw new Error('O navegador não retornou o nome do arquivo exportado.');
    sessionFinalizeExportMeta=meta;
    sessionFinalizeExportFingerprint=sessionStateFingerprint();
    sessionFinalizeExportAcknowledged=false;
    renderSessionExportConfirmation();
  }catch(e){ sessionExportError(e); }
}
function renderSessionDeleteConfirmation(previousStep){
  sessionFinalizeBackStep=previousStep||'safe';
  sessionModal('<h3>Confirmar encerramento</h3>'+
    '<p class="modal-sub">A próxima ação removerá deste navegador a base local do JP Wealth, os registros operacionais, a contabilidade, as configurações e os dados de acesso armazenados.</p>'+
    '<p class="session-warning">Exceção: as Notas do MVP (tarefas, bugs, funcionalidades e melhorias registradas no painel de Notas), as pastas em que estão organizadas, o histórico de concluídos e as preferências do painel não são apagados por esta ação — permanecem armazenados neste navegador.</p>'+
    '<div class="modal-q"><div class="ql">Tem certeza de que deseja prosseguir?</div></div>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionBack">Voltar</button><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button><button type="button" class="modal-btn confirm" id="sessionProceed">Sim, prosseguir</button></div>');
  $('sessionBack').addEventListener('click',()=>sessionFinalizeBackStep==='export'?renderSessionExportConfirmation():renderSessionSafeChoice());
  sessionCancelBinding();
  $('sessionProceed').addEventListener('click',renderSessionPhraseConfirmation);
}
function renderSessionPhraseConfirmation(){
  sessionModal('<h3>Confirmação irreversível</h3>'+
    '<p class="modal-sub">Para apagar a base local e finalizar a sessão, escreva exatamente:</p>'+
    '<div class="session-delete-phrase">APAGAR TUDO</div>'+
    '<label class="field session-phrase-field"><span>Frase de confirmação</span><input type="text" id="sessionDeletePhrase" value="" autocomplete="off" autocapitalize="characters" spellcheck="false"></label>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button><button type="button" class="modal-btn confirm" id="sessionDeleteConfirm" disabled>Finalizar e apagar dados</button></div>');
  sessionCancelBinding();
  const input=$('sessionDeletePhrase'), button=$('sessionDeleteConfirm');
  input.addEventListener('input',()=>{ button.disabled=input.value.trim()!=='APAGAR TUDO'; });
  button.addEventListener('click',()=>{ if(input.value.trim()==='APAGAR TUDO') finalizeJPWealthSession(); });
  input.focus();
}
function renderSessionChanged(){
  sessionModal('<h3>Existem alterações posteriores ao último backup</h3>'+
    '<p class="modal-sub">Esta sessão modificou a base do JP Wealth. Antes de remover os dados deste computador, exporte uma nova cópia atualizada.</p>'+
    '<div class="session-warning">Não é possível avançar diretamente para a exclusão enquanto existir alteração posterior ao checkpoint.</div>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button><button type="button" class="modal-btn confirm" id="sessionExport">Exportar base atual</button></div>');
  sessionCancelBinding();
  $('sessionExport').addEventListener('click',beginSessionExport);
}
function renderSessionSafeChoice(){
  sessionModal('<h3>Finalizar sessão neste computador</h3>'+
    '<p class="modal-sub">Nenhuma alteração posterior ao último ponto seguro foi identificada. Finalizar a sessão removerá a base local do JP Wealth deste navegador.</p>'+
    '<div class="modal-q"><div class="ql">Você possui uma cópia atual e acessível desta base de dados?</div></div>'+
    '<div class="modal-actions session-choice-actions"><button type="button" class="modal-btn confirm" id="sessionHasCopy">Sim, tenho uma cópia</button><button type="button" class="modal-btn cancel" id="sessionExportNow">Não tenho certeza — exportar agora</button><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button></div>');
  sessionCancelBinding();
  $('sessionHasCopy').addEventListener('click',()=>renderSessionDeleteConfirmation('safe'));
  $('sessionExportNow').addEventListener('click',beginSessionExport);
}
function openFinalizeSessionFlow(){
  // Guarda de entrada A-005: em modo de recuperação, Finalizar Sessão é interrompido
  // ANTES de qualquer modificação persistente. As confirmações normais deste fluxo não
  // valem como autorização para substituir ou apagar o banco problemático.
  if(typeof jpWealthLoadRecoveryActive==='function' && jpWealthLoadRecoveryActive()){
    sessionModal('<h3>Banco em modo de recuperação</h3>'+
      '<p class="modal-sub">O banco de dados deste navegador não pôde ser carregado com segurança e as gravações estão bloqueadas. Finalizar Sessão não pode ser executado agora — apagaria o conteúdo original preservado.</p>'+
      '<p class="session-warning">Use o aviso no topo da tela: baixe a cópia de recuperação, restaure um backup válido ou aceite começar com base vazia. Depois de uma dessas decisões, Finalizar Sessão volta a funcionar normalmente.</p>'+
      '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Entendi</button></div>');
    sessionCancelBinding();
    return;
  }
  window.__onbShown=true;
  sessionFinalizeEntry=sessionHasChanges()?'changed':'safe';
  sessionFinalizeExportMeta=null;
  sessionFinalizeExportFingerprint=null;
  sessionFinalizeExportAcknowledged=false;
  if(sessionFinalizeEntry==='changed') renderSessionChanged();
  else renderSessionSafeChoice();
}
function renderSessionCleanupError(report){
  sessionModal('<h3>Não foi possível finalizar a sessão</h3>'+
    '<p class="modal-sub">Nenhuma confirmação de sucesso foi apresentada. Alguns dados não puderam ser removidos.</p>'+
    '<div class="session-error" role="alert">Falha ao remover: '+esc(report.failures.join(', ')||'chave não identificada')+'</div>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button><button type="button" class="modal-btn confirm" id="sessionRetryCleanup">Tentar novamente</button></div>');
  sessionCancelBinding();
  $('sessionRetryCleanup').addEventListener('click',renderSessionPhraseConfirmation);
}
function finalizeJPWealthSession(){
  blockJPWealthPersistence();
  sessionNotifyFinalized();
  const report=clearJPWealthLocalData({removeAuxiliary:true,removeCorrupted:true});
  if(!report.ok){ renderSessionCleanupError(report); return; }
  sessionResetAuxiliarySurfaces();
  S=emptyJPWealthState();
  persistNotesAfterSessionWipe();
  // JPW-HJFGDE §17: a base morreu — a autorização local da pasta de exportação morre
  // junto (um handle órfão nunca deve reassociar sozinho uma base futura). Fire-and-
  // forget: falha aqui não pode travar a finalização, e sem metadados o handle é inerte.
  if(typeof dgFsClearHandle==='function') dgFsClearHandle();
  window.__onbShown=true;
  clearSessionCheckpoint();
  resetSessionFinalizeEphemeralState();
  closeModal();
  boot();
  // §12: aplicação sem base válida volta para a tela inicial canônica.
  if(typeof navigateToScreen==='function' && typeof DEFAULT_START_ROUTE!=='undefined') navigateToScreen(DEFAULT_START_ROUTE);
  window.__onbShown=false;
  initSessionCheckpoint();
  showSessionNotice('Sessão finalizada. Os dados locais do JP Wealth foram removidos deste navegador. As Notas do MVP — incluindo pastas, histórico de concluídos e preferências do painel — não foram apagadas e continuam salvas.');
}
function bindFinalizeSession(){
  const b=$('finalizeSessionBtn');
  if(b) b.addEventListener('click',openFinalizeSessionFlow);
}
initSessionCrossTab();
bindFinalizeSession();
