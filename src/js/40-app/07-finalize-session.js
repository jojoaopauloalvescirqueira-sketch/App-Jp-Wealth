// ============ FINALIZAR SESSÃO — privacidade em computador de terceiros (N1/N2) ============
const SESSION_CHECKPOINT_KEY='jpwealth_session_checkpoint_v1';
const SESSION_WIPE_CHANNEL='jpwealth_session_events_v1';
const SESSION_WIPE_STORAGE_KEY='jpwealth_session_wipe_signal_v1';
const JP_WEALTH_AUX_STORAGE_KEYS=['jpw_rail','jpw_expl','jpw_fs','jpwealth_v9_icon_theme',SESSION_WIPE_STORAGE_KEY];
let sessionCheckpointValue=null;
let sessionFinalizeEntry='safe';
let sessionFinalizeBackStep='safe';
let sessionFinalizeExportMeta=null;
let sessionFinalizeExportFingerprint=null;
let sessionFinalizeExportAcknowledged=false;
let sessionNoticeTimer=null;
let sessionCrossTabChannel=null;
let sessionLastWipeToken=null;

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
  S=emptyJPWealthState();
  window.__onbShown=true;
  clearSessionCheckpoint();
  closeModal();
  boot();
  window.__onbShown=false;
  initSessionCheckpoint();
  showSessionNotice('Sessão finalizada em outra aba. Os dados locais do JP Wealth foram removidos deste navegador.');
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
  empty.perf=[];
  empty.phases=empty.phases.map((phase,i)=>({...phase,orders:emptyOrders([5,4,3,2][i]||3)}));
  if(Array.isArray(empty.checklist)) empty.checklist=empty.checklist.map(group=>({...group,items:group.items.map(item=>({...item,v:0}))}));
  if(empty.mei){ empty.mei.history=[]; empty.mei.lastCalibrationAt=''; }
  return empty;
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
function beginSessionExport(){
  try{
    const meta=exportFullBackup();
    if(!meta || !meta.filename) throw new Error('O navegador não retornou o nome do arquivo exportado.');
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
  S=emptyJPWealthState();
  window.__onbShown=true;
  clearSessionCheckpoint();
  resetSessionFinalizeEphemeralState();
  closeModal();
  boot();
  window.__onbShown=false;
  initSessionCheckpoint();
  showSessionNotice('Sessão finalizada. Os dados locais do JP Wealth foram removidos deste navegador.');
}
function bindFinalizeSession(){
  const b=$('finalizeSessionBtn');
  if(b) b.addEventListener('click',openFinalizeSessionFlow);
}
initSessionCrossTab();
bindFinalizeSession();
