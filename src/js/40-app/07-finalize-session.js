// ============ FINALIZAR SESSÃO — privacidade em computador de terceiros (N1/N2) ============
const SESSION_CHECKPOINT_KEY='jpwealth_session_checkpoint_v1';
const SESSION_WIPE_CHANNEL='jpwealth_session_events_v1';
const SESSION_WIPE_STORAGE_KEY='jpwealth_session_wipe_signal_v1';
const JP_WEALTH_AUX_STORAGE_KEYS=['jpw_rail','jpw_expl','jpw_fs','jpwealth_v9_icon_theme','jpwealth_v9_icon_choice','jpwealth_galton_preferences_v1',SESSION_WIPE_STORAGE_KEY];
// ---- ALD-C3-PRE-EPOCH · geração causal da base -----------------------------
// CONTROL PLANE, não data plane. Metadado compartilhado entre abas, sem PII e sem
// conteúdo financeiro. NÃO integra JP_WEALTH_AUX_STORAGE_KEYS, não entra em backup
// (dgBuildBackupBlob clona apenas S) e não é restaurada por importação — restaurar
// uma geração morta reabriria exatamente o replay que este protocolo fecha.
// Sobrevive a Finalizar Sessão; wipe e import ROTACIONAM seu valor.
//
// O problema que ela resolve: os dois transportes entregam a MESMA mensagem duas
// vezes, e o antigo dedup guardava um único token compartilhado pelos três tipos —
// um evento de outro tipo o sobrescrevia e liberava o anterior para reprocessamento.
// Medido: F → W → reentrega de F executava a finalização DEPOIS da limpeza total,
// regravando patrimônio numa base que o operador acabara de apagar. Relógio não
// resolve isso: Date.now() não é monotônico e empata no mesmo milissegundo. Geração
// resolve, porque é causal.
const BASE_EPOCH_STORAGE_KEY='jpwealth_base_epoch_v1';
// Sentinel determinístico e reservado. Todas as abas gravam o MESMO literal no
// bootstrap, então não existe disputa de identidade — o desenho aleatório teria uma
// janela em que duas abas se julgam de gerações diferentes. O formato (maiúsculas com
// hífens) não casa com UUID nem com hex de 32, então é impossível confundi-lo com uma
// geração rotacionada.
const BASE_EPOCH_SENTINEL='BASE-V0-LEGACY';
// DEDUPLICAÇÃO OPERACIONAL — não é mecanismo de segurança. A proteção patrimonial
// contra replay é da epoch; isto só evita executar duas vezes a mesma mensagem
// entregue pelos dois transportes. Não precisa persistir: está provado que aba nova
// não recebe replay histórico (nem BroadcastChannel nem storage fazem replay, e a
// chave de sinal é removida no mesmo tick).
const SESSION_SEEN_LIMIT=32;
let sessionSeenMessages=[];
// Contador do descarte explícito do protocolo legado — existe para que "mixed-build
// perde a sincronização do Finalizar Sessão" seja observável e testável, em vez de
// depender de omissão acidental do roteador.
let sessionLegacyProtocolDiscards=0;
function sessionMessageSeen(message){
  const id=(message&&message.type)+':'+(message&&message.token);
  if(sessionSeenMessages.indexOf(id)!==-1) return true;
  sessionSeenMessages.push(id);
  if(sessionSeenMessages.length>SESSION_SEEN_LIMIT) sessionSeenMessages.shift();
  return false;
}
function sessionEpochGenerate(){
  try{
    const c=(typeof crypto!=='undefined')?crypto:null;
    if(c && typeof c.randomUUID==='function') return c.randomUUID();
    if(c && typeof c.getRandomValues==='function'){
      const bytes=new Uint8Array(16); c.getRandomValues(bytes);
      return Array.prototype.map.call(bytes,b=>b.toString(16).padStart(2,'0')).join('');
    }
  }catch(e){}
  return null; // sem fonte criptográfica ⇒ geração indisponível ⇒ fail-closed
}
// undefined = storage indisponível · null = chave ausente · string = valor
function sessionEpochRead(){
  try{ return localStorage.getItem(BASE_EPOCH_STORAGE_KEY); }
  catch(e){ return undefined; }
}
// CONFIRMAÇÃO ESTRITA (B4): só há sucesso quando a releitura devolve EXATAMENTE o
// valor tentado. Um setItem transformado em no-op, sobrescrito no intervalo ou
// truncado NÃO é rotação concluída — devolver "o que ficou lá" fingia uma
// propriedade que a função não provava.
function sessionEpochWriteAndConfirm(valor){
  try{ localStorage.setItem(BASE_EPOCH_STORAGE_KEY,valor); }
  catch(e){ return null; }
  const lido=sessionEpochRead();
  return (lido===valor) ? valor : null;
}
// BOOTSTRAP é convergência, não autoridade: todas as abas gravam o MESMO sentinel;
// se a releitura mostrar outra coisa, é uma geração que outra aba acabou de firmar —
// ADOTAR é correto aqui, e SÓ aqui. Rotação (autoridade) usa a confirmação estrita.
function sessionEpochBootstrap(){
  try{ localStorage.setItem(BASE_EPOCH_STORAGE_KEY,BASE_EPOCH_SENTINEL); }
  catch(e){ return null; }
  const lido=sessionEpochRead();
  return (lido===undefined || lido===null || lido==='') ? null : lido;
}
function sessionEpochCurrent(){
  const lido=sessionEpochRead();
  if(lido===undefined) return null;
  if(lido!==null && lido!=='') return lido;
  return sessionEpochBootstrap();
}
function sessionEpochRotate(){
  const nova=sessionEpochGenerate();
  if(!nova) return null;
  return sessionEpochWriteAndConfirm(nova);
}
// Estabelece a geração ao receber wipe/import. Emissor NOVO já rotacionou no storage
// compartilhado — basta ler. Emissor LEGADO não participa do protocolo, então é ESTA
// aba que rotaciona. Devolve null quando não foi possível firmar geração alguma.
function sessionEpochEstablish(message){
  if(message && message.baseEpoch) return sessionEpochCurrent();
  return sessionEpochRotate();
}
// ---- Serialização cross-tab dos escritores do documento (DP-1) --------------
// Com Web Locks, o critical section da finalização/limpeza/importação roda
// SERIALIZADO entre abas cooperantes da mesma origem — é isso que fecha o TOCTOU
// identificado na pausa. Sem Web Locks o modo é DEGRADED: o corpo roda direto,
// protegido apenas pela guarda síncrona best-effort do save() (Camada 1) e pelo
// protocolo de geração; a race residual getItem→setItem permanece possível e NUNCA
// é anunciada como atomicidade (DP-3).
const JPW_STATE_WRITER_LOCK='jpwealth_state_writer_v1';
function sessionSerializationMode(){
  try{
    return (typeof navigator!=='undefined' && navigator.locks &&
            typeof navigator.locks.request==='function') ? 'weblocks' : 'degraded';
  }catch(e){ return 'degraded'; }
}
function sessionAcquireWriteLock(fn){
  if(sessionSerializationMode()==='weblocks'){
    return navigator.locks.request(JPW_STATE_WRITER_LOCK, ()=>fn({degraded:false}));
  }
  return Promise.resolve().then(()=>fn({degraded:true}));
}
// SEQLOCK LÓGICO sobre o documento principal: epoch → documento → epoch. Uma rotação
// entre as duas leituras produziria um snapshot pertencente a outra geração, e usá-lo
// seria misturar bases. Retry limitado; esgotado, aborta.
function sessionReadStable(opcoes){
  for(let tentativa=0; tentativa<3; tentativa++){
    const e1=sessionEpochCurrent();
    if(!e1) return { ok:false, erro:new Error('geração da base indisponível') };
    const doc=sessionPreserveLongitudinal(opcoes);
    if(!doc.ok) return doc;
    const e2=sessionEpochCurrent();
    if(e1===e2) return { ok:true, epoch:e1, valor:doc.valor, raw:(doc.raw===undefined?null:doc.raw) };
  }
  return { ok:false, erro:new Error('a geração da base mudou durante a leitura') };
}
let sessionCheckpointValue=null;
let sessionFinalizeEntry='safe';
// Snapshot do agregado persistido, capturado na ABERTURA do fluxo — antes de
// qualquer efeito colateral capaz de chamar save(). null = ainda não capturado.
let sessionPreservedAlladin=null;
// Geração da base no instante da captura. O ato só se completa se ela ainda for a
// corrente na confirmação — um wipe entre a abertura e o "APAGAR TUDO" mudaria a base
// sob o fluxo.
let sessionPreservedEpoch=null;
// Forma BRUTA do documento no instante da captura — é a revisão R da transação: o
// commit só prossegue se o disco ainda for byte-idêntico a ela (revalidação dentro
// do lock). null = chave ausente na captura (base virgem).
let sessionPreservedRaw=null;
let sessionFinalizeBackStep='safe';
let sessionFinalizeExportMeta=null;
let sessionFinalizeExportFingerprint=null;
let sessionFinalizeExportAcknowledged=false;
let sessionNoticeTimer=null;
let sessionCrossTabChannel=null;
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
// TIPO VERSIONADO, deliberadamente. Um build antigo roteia por cadeia if/else-if
// sobre três literais e IGNORA um tipo desconhecido — verificado executando o
// baseline. Isso é o que impede que uma aba antiga receba a finalização nova e rode
// o handler legado, que zerava S.alladin por omissão. Finalização remota NÃO
// atravessa versões do protocolo: fail-closed por desenho. Wipe e import, ao
// contrário, mantêm os tipos originais porque PRECISAM atravessar — ignorá-los
// deixaria uma aba operando sobre base que já não existe.
function sessionNotifyFinalized(epoch){
  const message={type:'jpwealth-session-finalized-v2',token:sessionWipeToken(),baseEpoch:epoch};
  sessionMessageSeen(message);
  if(sessionCrossTabChannel){
    try{ sessionCrossTabChannel.postMessage(message); }catch(e){}
  }
  try{
    localStorage.setItem(SESSION_WIPE_STORAGE_KEY,JSON.stringify(message));
    localStorage.removeItem(SESSION_WIPE_STORAGE_KEY);
  }catch(e){}
}
// FINALIZAÇÃO VINDA DE OUTRA ABA — contrato B3 do gate: nenhum caminho pode deixar
// esta aba PERMANENTEMENTE somente-leitura. Por isso:
//   1) toda validação capaz de abortar roda ANTES do bloqueio — descartar um replay
//      ou recusar um disco ilegível não exige tocar a aba;
//   2) a parte que muta roda em try/finally: qualquer saída sem conclusão devolve a
//      persistência ao operador (resume).
// A proteção contra "aba antiga ressuscita a base" deixou de depender do bloqueio
// permanente: o broadcast agora só é emitido DEPOIS de o documento final estar
// durável no disco, então qualquer save() desta aba com memória velha diverge do
// disco e é RECUSADO pela guarda de concorrência do save() (Camada 1). Em modo
// degraded (sem Web Locks) essa guarda é best-effort — limite declarado (DP-3).
function sessionHandleRemoteFinalization(message){
  if(!message || message.type!=='jpwealth-session-finalized-v2') return;
  if(sessionMessageSeen(message)) return;
  // CAUSALIDADE: só atua quem pertence à geração corrente. Uma finalização emitida
  // antes de um wipe carrega a geração antiga e é recusada, mesmo chegando depois.
  const geracao=sessionEpochCurrent();
  if(!geracao || !message.baseEpoch || message.baseEpoch!==geracao){
    showSessionNotice('Outra aba finalizou a sessão, mas o aviso pertence a uma geração anterior da base e foi descartado.');
    return;
  }
  // O emissor só difunde depois do commit confirmado, então o documento final JÁ É o
  // disco. Este handler não escreve a chave principal: ele ADOTA o documento via
  // load(). Disco ausente/ilegível aqui é anomalia real (ex.: limpeza externa) — a
  // aba segue utilizável e a guarda do save() impede que ela regrave memória velha.
  let bruto=null;
  try{ bruto=localStorage.getItem(LSKEY); }
  catch(e){
    showSessionNotice('Outra aba finalizou a sessão, mas o estado persistido não pôde ser lido nesta aba — recarregue a página para adotar a base finalizada.');
    return;
  }
  if(bruto===null || bruto===undefined || bruto===''){
    showSessionNotice('Outra aba finalizou a sessão, mas o documento final ainda não está visível nesta aba — recarregue a página para adotar a base finalizada.');
    return;
  }
  // Validação do documento AINDA antes do block (§9): um disco ilegível aqui não
  // pode empurrar esta aba para o modo de recuperação via load() — a aba segue
  // utilizável com o S atual, a guarda do save() impede regravar por cima do lixo,
  // e um reload posterior decide pelo caminho canônico.
  try{
    const doc=JSON.parse(bruto);
    if(!doc || typeof doc!=='object' || Array.isArray(doc)) throw new Error('documento inválido');
  }catch(e){
    showSessionNotice('Outra aba finalizou a sessão, mas o estado persistido não pôde ser lido com segurança nesta aba — recarregue a página para adotar a base finalizada.');
    return;
  }
  let bloqueou=false, concluiu=false;
  try{
    // block+resume: invalida a geração de persistência (JPW-FX-WIPE-RACE) para que
    // continuações assíncronas iniciadas com o S antigo desistam ao conferir o epoch.
    blockJPWealthPersistence(); bloqueou=true;
    sessionResetAuxiliarySurfaces();
    const report=clearJPWealthLocalData({removeAuxiliary:true,removeCorrupted:true,preserveMain:true});
    resumeJPWealthPersistence(); bloqueou=false;
    load();
    concluiu=true;
    window.__onbShown=true;
    clearSessionCheckpoint();
    closeModal();
    boot();
    window.__onbShown=false;
    initSessionCheckpoint();
    const aviso='Sessão finalizada em outra aba. Os dados operacionais do JP Wealth foram removidos deste navegador. Os Tickets — incluindo pastas, histórico de concluídos e preferências do painel — não foram apagados e continuam salvos.';
    showSessionNotice(report.ok?aviso:aviso+' Aviso: algumas chaves auxiliares não puderam ser removidas: '+report.failures.join(', ')+'.');
  }finally{
    if(bloqueou && !concluiu){
      resumeJPWealthPersistence();
      showSessionNotice('Outra aba finalizou a sessão, mas esta aba não conseguiu aplicar a finalização — recarregue a página para adotar a base finalizada.');
    }
  }
}
// ---- Difusão da Zona de Perigo entre abas ----
// A limpeza total era o único fluxo destrutivo que não avisava as outras abas: a base
// morria aqui e a PRIMEIRA gravação de uma aba antiga — que ainda tem o S completo em
// memória — ressuscitava o documento inteiro na chave recém-apagada. Uma exclusão que
// não se propaga não é exclusão.
//
// Reusa canal, fallback por `storage` e dedup por token da finalização, mas com tipo e
// handler próprios: a SEMÂNTICA das duas limpezas é diferente e não pode ser confundida.
// Finalizar Sessão remove auxiliares e cópias de recuperação; a Zona de Perigo preserva
// as duas, e o texto que o operador confirmou promete exatamente isso.
function sessionNotifyBaseWiped(epoch){
  const message={type:'jpwealth-base-wiped',token:sessionWipeToken(),baseEpoch:epoch};
  sessionMessageSeen(message);
  if(sessionCrossTabChannel){
    try{ sessionCrossTabChannel.postMessage(message); }catch(e){}
  }
  try{
    localStorage.setItem(SESSION_WIPE_STORAGE_KEY,JSON.stringify(message));
    localStorage.removeItem(SESSION_WIPE_STORAGE_KEY);
  }catch(e){}
}
function sessionHandleRemoteBaseWipe(message){
  if(!message || message.type!=='jpwealth-base-wiped') return;
  if(sessionMessageSeen(message)) return;
  // Mesma dança de epoch do fluxo local: invalida a geração ANTES de destruir, para que
  // nenhuma continuação assíncrona iniciada antes daqui regrave o que acabou de ser
  // apagado. O par block+resume deixa o epoch duas casas à frente.
  blockJPWealthPersistence();
  // EMENDA RATIFICADA: a geração precisa ser ESTABELECIDA antes de esta aba voltar a
  // ser gravável. Emissor novo já rotacionou no storage compartilhado; emissor legado
  // não participa do protocolo, então é esta aba que rotaciona. Não conseguindo firmar
  // geração alguma, a aba NÃO pode continuar como se estivesse causalmente protegida e
  // NÃO pode regravar a base obsoleta: permanece bloqueada até recarregar.
  const geracao=sessionEpochEstablish(message);
  if(!geracao){
    showSessionNotice('Outra aba apagou a base do JP Wealth. Esta aba foi bloqueada para gravação porque não foi possível estabelecer a nova geração da base — recarregue a página.');
    return;
  }
  const report=clearJPWealthLocalData({removeAuxiliary:false,removeCorrupted:false});
  if(!report.ok){
    // Nada foi apagado nesta aba: devolve a persistência exatamente como estava.
    resumeJPWealthPersistence();
    showSessionNotice('Outra aba apagou a base do JP Wealth, mas algumas chaves não puderam ser removidas neste navegador: '+report.failures.join(', '));
    return;
  }
  S=structuredClone(DEFAULTS);
  resumeJPWealthPersistence();
  if(typeof dgFsClearHandle==='function') dgFsClearHandle();
  window.__onbShown=false; // base vazia → o questionário de início volta, como no fluxo local
  closeModal();
  boot();
  if(typeof navigateToScreen==='function' && typeof DEFAULT_START_ROUTE!=='undefined') navigateToScreen(DEFAULT_START_ROUTE);
  showSessionNotice('A base do JP Wealth foi apagada em outra aba. Esta aba voltou ao estado inicial; preferências locais de interface e cópias de recuperação existentes foram preservadas.');
}
// ---- Difusão da IMPORTAÇÃO de backup entre abas ----
// Substituir o documento inteiro por outro é destruição da base tanto quanto a
// Zona de Perigo — e era o único fluxo dessa natureza que não avisava as demais
// abas. Sem aviso, a aba antiga mantém o S anterior em memória e a PRIMEIRA
// gravação dela ressuscita o documento inteiro por cima da base que o operador
// acabou de restaurar. O raciocínio já registrado em 05-wipe-all.js vale aqui
// palavra por palavra.
//
// A semântica, porém, é diferente das outras duas: aqui não se apaga nada — há
// um documento novo e legítimo na chave. Por isso a aba remota RECARREGA em vez
// de zerar, e nenhuma chave auxiliar é removida.
function sessionNotifyBaseImported(epoch){
  const message={type:'jpwealth-base-imported',token:sessionWipeToken(),baseEpoch:epoch};
  sessionMessageSeen(message);
  if(sessionCrossTabChannel){
    try{ sessionCrossTabChannel.postMessage(message); }catch(e){}
  }
  try{
    localStorage.setItem(SESSION_WIPE_STORAGE_KEY,JSON.stringify(message));
    localStorage.removeItem(SESSION_WIPE_STORAGE_KEY);
  }catch(e){}
}
function sessionHandleRemoteBaseImport(message){
  if(!message || message.type!=='jpwealth-base-imported') return;
  if(sessionMessageSeen(message)) return;
  // O par block+resume invalida a geração da persistência: qualquer continuação
  // assíncrona iniciada com o S antigo confere o epoch depois do await e desiste,
  // em vez de gravar o documento obsoleto sobre o importado.
  blockJPWealthPersistence();
  // EMENDA RATIFICADA: a geração precisa ser ESTABELECIDA antes de esta aba voltar a
  // ser gravável. Emissor novo já rotacionou no storage compartilhado; emissor legado
  // não participa do protocolo, então é esta aba que rotaciona. Não conseguindo firmar
  // geração alguma, a aba NÃO pode continuar como se estivesse causalmente protegida e
  // NÃO pode regravar a base obsoleta: permanece bloqueada até recarregar.
  const geracao=sessionEpochEstablish(message);
  if(!geracao){
    showSessionNotice('Outra aba substituiu a base do JP Wealth. Esta aba foi bloqueada para gravação porque não foi possível estabelecer a nova geração da base — recarregue a página.');
    return;
  }
  resumeJPWealthPersistence();
  load();
  window.__onbShown=true;
  closeModal();
  boot();
  window.__onbShown=false;
  if(typeof initSessionCheckpoint==='function') initSessionCheckpoint();
  showSessionNotice('Outra aba importou um backup completo. Esta aba foi recarregada com a base importada — nada do estado anterior foi mantido em memória.');
}
// Descarte EXPLÍCITO, nunca por omissão de tipo desconhecido: precisa deixar rastro
// e ser testável. Um build antigo não participa do protocolo de geração, então a
// finalização dele não pode ser executada aqui — sem clear, sem persistência, sem
// preservação, sem migração e sem executar parte alguma do handler v2.
function sessionHandleLegacyFinalization(){
  sessionLegacyProtocolDiscards++;
}
function sessionHandleRemoteMessage(message){
  if(!message) return;
  if(message.type==='jpwealth-session-finalized-v2') sessionHandleRemoteFinalization(message);
  else if(message.type==='jpwealth-session-finalized') sessionHandleLegacyFinalization(message);
  else if(message.type==='jpwealth-base-wiped') sessionHandleRemoteBaseWipe(message);
  else if(message.type==='jpwealth-base-imported') sessionHandleRemoteBaseImport(message);
}
function initSessionCrossTab(){
  if(typeof BroadcastChannel==='function'){
    try{
      sessionCrossTabChannel=new BroadcastChannel(SESSION_WIPE_CHANNEL);
      sessionCrossTabChannel.addEventListener('message',e=>sessionHandleRemoteMessage(e.data));
    }catch(e){ sessionCrossTabChannel=null; }
  }
  window.addEventListener('storage',e=>{
    if(e.key!==SESSION_WIPE_STORAGE_KEY || !e.newValue) return;
    try{ sessionHandleRemoteMessage(JSON.parse(e.newValue)); }catch(error){}
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
  // preserveMain (write-before-clear, B1): a finalização passou a GRAVAR o documento
  // final por cima da chave principal ANTES de qualquer limpeza — a chave nunca mais
  // é removida por este fluxo. Só a Zona de Perigo (que não passa preserveMain)
  // continua removendo LSKEY, porque lá a exclusão é o que o operador pediu.
  const keys=(options.preserveMain===true)?[]:[LSKEY];
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
// ---- ALD-C3-PRE · preservação da memória longitudinal do Alladin -----------
// ATOMICIDADE: a cópia é obtida ANTES de qualquer destruição. Nos dois fluxos de
// finalização, clearJPWealthLocalData() apaga o disco antes de o estado novo ser
// construído — uma cópia que falhasse ali dentro deixaria a sessão PARCIALMENTE
// finalizada, com o patrimônio já perdido. Falha de preservação = falha do ato
// inteiro, jamais finalização parcial.
//
// A FONTE É SEMPRE O ESTADO PERSISTIDO, NUNCA `S.alladin`. A memória de uma aba
// pode ser um retrato anterior a atos que o operador já confirmou em outra aba:
// saves comuns não são difundidos entre abas, e nada ressincroniza `S` fora do
// boot. Preservar da memória faria a finalização DESFAZER edições e RESSUSCITAR
// registros apagados. E o Alladin não tem ato de deleção (setRecordStatus só
// alterna ACTIVE/INACTIVE), então editar o agregado é hoje o único modo de
// eliminar um registro — justamente o ato que a memória obsoleta desfaria.
//
// JSON.parse devolve um grafo novo: sem aliasing, sem DataCloneError, e sem
// normalizar, migrar ou rebaixar versão — schema futuro atravessa
// estruturalmente intacto.
//
// CHAVE AUSENTE é a única assimetria entre os dois fluxos, e é fundamentada:
//   local  — a leitura acontece ANTES de qualquer destruição, e base virgem ou
//            recém-limpa legitimamente não tem LSKEY (verificado em Chromium).
//            Como todo save() bem-sucedido cria a chave, e aldMutate faz
//            rollback quando save() recusa, chave ausente ⇒ não existe
//            patrimônio comprometido ⇒ preservar nada não perde nada.
//   remoto — com write-before-clear o emissor nunca remove LSKEY e só difunde
//            depois do commit confirmado, então ausência aqui é ANOMALIA real
//            (limpeza externa, wipe legado em curso). Tratar como "nada a
//            preservar" gravaria DEFAULTS por cima do patrimônio, em silêncio
//            e com aviso de sucesso — por isso aborta.
//
// Em nenhum dos dois fluxos disco indisponível ou inválido autoriza fallback
// para S.alladin: abortar é preferível a ressuscitar ou a zerar.
function sessionPreserveLongitudinal(opcoes){
  const ausenteAborta = !!(opcoes && opcoes.ausenteAborta);
  let bruto=null;
  try{ bruto=localStorage.getItem(LSKEY); }
  catch(error){ return { ok:false, erro:error }; }
  if(bruto===null || bruto===undefined){
    return ausenteAborta
      ? { ok:false, erro:new Error('estado persistido ausente durante finalização em outra aba') }
      : { ok:true, valor:{}, raw:null };
  }
  let documento=null;
  try{ documento=JSON.parse(bruto); }
  catch(error){ return { ok:false, erro:error }; }
  if(!documento || typeof documento!=='object' || Array.isArray(documento)){
    return { ok:false, erro:new Error('estado persistido ilegível') };
  }
  if(documento.alladin===undefined) return { ok:true, valor:{}, raw:bruto };
  return { ok:true, valor:{ alladin:documento.alladin }, raw:bruto };
}
function renderSessionPreservationError(error){
  sessionModal('<h3>Não foi possível finalizar a sessão</h3>'+
    '<p class="modal-sub">Nada foi apagado. O encerramento foi interrompido antes de tocar nos seus dados, porque o estado persistido não pôde ser lido com segurança e o patrimônio não seria preservado.</p>'+
    '<div class="session-error" role="alert">Falha ao ler o estado persistido: '+esc((error&&error.message)||'erro não identificado')+'</div>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button></div>');
  sessionCancelBinding();
}
// `preservado` chega PRONTO do chamador (ver sessionPreserveLongitudinal).
function emptyJPWealthState(preservado){
  const empty=structuredClone(DEFAULTS);
  empty.params={...empty.params, saldoIni:0, saldoAtu:0, inicio:''};
  empty.accounts=[];
  empty.ledger=[];
  empty.ledgerArchive=[];
  empty.transitionLog=[];
  empty.cycleRealizado=0;
  // Explícito, ainda que o clone de DEFAULTS já traga os dois assim: a mesma
  // disciplina defensiva das linhas vizinhas. Se um dia DEFAULTS deixar de
  // nascer com operação nula, a Finalização de Sessão continua limpando o
  // ciclo de vida em vez de entregar uma sessão nova com operação fantasma.
  empty.activeOperation=null;
  empty.operationHistory=structuredClone(DEFAULTS.operationHistory);
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
  // Finanças Pessoais é memória LONGITUDINAL da vida financeira do operador,
  // não dado operacional do período de trading que se encerra aqui. Mesma
  // herança das notas — decisão humana registrada no congelamento do schema
  // v1 (PF-01, Bloco D): Finalizar Sessão não apaga, não recria vazio e não
  // modifica o agregado. Versões do app anteriores a esta linha zeravam o
  // agregado neste fluxo — risco residual documentado no contrato.
  empty.personalFinance=(S&&S.personalFinance)?structuredClone(S.personalFinance):structuredClone(DEFAULTS.personalFinance);
  // Alladin é PATRIMÔNIO — memória longitudinal por definição: um imóvel, um
  // instrumento cadastrado e uma conta de custódia não pertencem ao período de
  // trading que se encerra aqui. Mesma doutrina das duas linhas acima, e o
  // mesmo defeito que o agregado de Finanças Pessoais sofreu antes da correção
  // do PF-01: até esta linha, Finalizar Sessão zerava o cadastro patrimonial.
  //
  // A cópia vem EXCLUSIVAMENTE do chamador. Esta função NÃO consulta S.alladin por
  // conta própria: um fallback interno clonaria DEPOIS de clearJPWealthLocalData() já
  // ter apagado o disco — exatamente a "recuperação após o início da destruição" que a
  // atomicidade proíbe — e, pior, tornaria o parâmetro indetectável (chamar sem
  // argumento continuaria preservando, mascarando qualquer defeito de fiação).
  // Sem preservado, o estado sai vazio; a preservação é ato explícito do fluxo.
  // Zona de Perigo continua apagando — lá a exclusão é o que o operador pediu.
  const alladinPreservado = preservado ? preservado.alladin : undefined;
  if(alladinPreservado!==undefined) empty.alladin=alladinPreservado;
  return empty;
}
// COMMIT DURÁVEL do estado finalizado (B1+B2, substitui persistNotesAfterSessionWipe).
// Write-before-clear: o documento final SUBSTITUI a chave principal — nada foi
// removido antes, então uma falha aqui deixa o documento ANTERIOR intacto no disco.
// A escrita é verificada por read-back EXATO da string gravada; falha silenciosa
// (quota, setItem no-op, eviction) vira {ok:false} explícito — jamais um catch vazio
// seguido de aviso de sucesso. Aplica a MESMA política de segredo do save(): a senha
// de investidor nunca vai ao armazenamento. Sucesso declara a forma nova à guarda de
// concorrência (jpWealthAdoptPersistedRaw) para os fluxos seguintes desta aba.
function sessionCommitFinalizedState(estado){
  // Guarda A-005: escrita direta na chave principal jamais pode rodar em modo de
  // recuperação — regravaria o banco problemático com o estado provisório.
  if(typeof jpWealthLoadRecoveryActive==='function' && jpWealthLoadRecoveryActive()){
    return { ok:false, erro:new Error('banco em modo de recuperação — gravação direta recusada') };
  }
  let payload;
  try{ payload=JSON.stringify(estado,(k,v)=>k==='investorPassword'?'':v); }
  catch(e){ return { ok:false, erro:e }; }
  try{ localStorage.setItem(LSKEY,payload); }
  catch(e){ return { ok:false, erro:e }; }
  let lido=null;
  try{ lido=localStorage.getItem(LSKEY); }
  catch(e){ return { ok:false, erro:e }; }
  if(lido!==payload){
    return { ok:false, erro:new Error('a releitura do documento gravado divergiu da escrita') };
  }
  if(typeof jpWealthAdoptPersistedRaw==='function') jpWealthAdoptPersistedRaw(payload);
  return { ok:true, payload };
}
function showSessionNotice(message){
  const el=$('sessionNotice'); if(!el) return;
  el.textContent=message; el.classList.add('show');
  clearTimeout(sessionNoticeTimer);
  sessionNoticeTimer=setTimeout(()=>el.classList.remove('show'),8000);
}
function resetSessionFinalizeEphemeralState(){
  sessionPreservedAlladin=null;
  sessionPreservedEpoch=null;
  sessionPreservedRaw=null;
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
    // BACKUP AUTORITATIVO (decisão do gate): a cópia oferecida antes do ato destrutivo
    // representa o DOCUMENTO PERSISTIDO capturado na abertura (revisão R), não o S
    // desta aba — que pode ser um retrato anterior ao trabalho de outra aba. Se a base
    // mudar enquanto o operador está no seletor, a revalidação de R dentro do lock
    // aborta o commit e exige novo export: o arquivo nunca fica órfão da base final.
    let estadoAutoritativo=null;
    if(sessionPreservedRaw!==null){
      try{ estadoAutoritativo=JSON.parse(sessionPreservedRaw); }catch(e){ estadoAutoritativo=null; }
    }
    const meta=await exportFullBackup({quiet:true, estadoFonte:estadoAutoritativo});
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
    '<p class="session-warning">Exceção: os Tickets (tarefas, bugs, funcionalidades e melhorias registradas no painel de Tickets), as pastas em que estão organizados, o histórico de concluídos e as preferências do painel não são apagados por esta ação — permanecem armazenados neste navegador.</p>'+
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
  // CAPTURA PRÉ-EFEITO: o disco autoritativo é lido AQUI, antes de qualquer coisa
  // que possa gravá-lo. O caminho 'changed' exporta o backup, e
  // dgRegisterExportSuccess() (30-accounting/01-daily-ledger.js) chama save(), que
  // regrava o documento INTEIRO a partir do S desta aba — que pode ser um retrato
  // anterior a atos já confirmados em outra aba. Ler o disco depois disso leria o
  // que esta própria aba acabou de sobrescrever, e a leitura "do disco" viraria
  // leitura da memória por via indireta. Ilegível aborta aqui: antes do export,
  // antes de qualquer save(), antes do clear e antes do broadcast.
  // Leitura ESTÁVEL (epoch → documento → epoch): sem geração confiável o ato é
  // recusado aqui — antes do export, antes de qualquer save(), antes do clear e antes
  // do broadcast. Não existe degradação para "finaliza só nesta aba".
  const preservado=sessionReadStable({ausenteAborta:false});
  if(!preservado.ok){ renderSessionPreservationError(preservado.erro); return; }
  sessionPreservedAlladin=preservado.valor;
  sessionPreservedEpoch=preservado.epoch;
  sessionPreservedRaw=(preservado.raw===undefined)?null:preservado.raw;
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
// TRANSAÇÃO DE FINALIZAÇÃO (Change Proposal V2 + DP-1/2/3).
// Fora do lock ficou só o que já aconteceu: captura na abertura (documento D e
// revisão R = raw) e a interação humana. TUDO que decide e muta roda dentro do
// critical section, serializado entre abas quando Web Locks existe:
//   reler o disco → ainda byte-idêntico a R? não → aborta (a base mudou; novo export)
//   geração ainda a da captura? não → aborta
//   bloquear persistência (invalida continuações assíncronas desta aba)
//   construir o documento final em memória
//   COMMIT write-before-clear: setItem + read-back exato — nada foi removido antes,
//     então falha aqui deixa o documento anterior INTACTO e o ato recusa sem sucesso
//   só então: limpeza de auxiliares (nunca a chave principal), broadcast, boot.
// Qualquer abort pós-block passa pelo finally e devolve a aba ao operador (resume):
// fail-closed não pode virar fail-permanently-read-only. No sucesso o bloqueio fica,
// como sempre ficou: reengajar onboarding/import é o que reabre a persistência.
// A função NUNCA rejeita — todo erro vira modal — então os chamadores de evento
// podem ignorar a Promise sem risco de rejeição silenciosa (DP-2).
async function finalizeJPWealthSession(){
  if(!sessionPreservedAlladin || !sessionPreservedEpoch){
    renderSessionPreservationError(new Error('a preservação não foi capturada na abertura do fluxo'));
    return;
  }
  let bloqueou=false, concluiu=false;
  try{
    await sessionAcquireWriteLock(async ()=>{
      // REVALIDAÇÃO DA REVISÃO dentro do lock — é isto que mata o TOCTOU: se outra
      // aba gravou depois da captura (inclusive o próprio save() do export desta aba
      // por cima de uma escrita alheia), o raw diverge e o ato recusa sem destruir.
      let atualRaw=null;
      try{ atualRaw=localStorage.getItem(LSKEY); }
      catch(e){ renderSessionPreservationError(e); return; }
      // O disco é aceito em exatamente dois casos: (a) continua byte-idêntico à
      // revisão R da captura; (b) é a ÚLTIMA ESCRITA LEGÍTIMA DESTA PRÓPRIA ABA —
      // o save() do export do ramo 'changed' grava depois da captura, e a guarda
      // de concorrência (Camada 1) só o deixa gravar sobre uma base que esta aba
      // conhecia. Qualquer outra forma é escrita de OUTRA aba: abortar, porque
      // finalizar agora gravaria uma versão antiga por cima do trabalho dela. No
      // caso perigoso (esta aba obsoleta), o save() do export é RECUSADO pela
      // Camada 1, o disco permanece na revisão R, e o ramo (a) preserva o
      // documento autoritativo capturado.
      const ultimaEscritaLocal=(typeof jpWealthLastPersistedRawGet==='function')?jpWealthLastPersistedRawGet():null;
      if(atualRaw!==sessionPreservedRaw && atualRaw!==ultimaEscritaLocal){
        renderSessionBaseChangedError();
        return;
      }
      if(sessionEpochCurrent()!==sessionPreservedEpoch){
        renderSessionPreservationError(new Error('a geração da base mudou durante o fluxo'));
        return;
      }
      blockJPWealthPersistence(); bloqueou=true;
      sessionResetAuxiliarySurfaces();
      const novoEstado=emptyJPWealthState(sessionPreservedAlladin);
      const commit=sessionCommitFinalizedState(novoEstado);
      if(!commit.ok){ renderSessionCommitError(commit.erro); return; }
      S=novoEstado;
      const report=clearJPWealthLocalData({removeAuxiliary:true,removeCorrupted:true,preserveMain:true});
      concluiu=true;
      // Broadcast SÓ depois de o documento final estar durável e confirmado: nenhuma
      // outra aba recebe "finalized" antes de existir estado a adotar (contrato §9 do
      // gate; alinha com sessionNotifyBaseWiped/Imported, que sempre emitiram depois).
      sessionNotifyFinalized(sessionPreservedEpoch);
      // JPW-HJFGDE §17: a base operacional morreu — a autorização local da pasta de
      // exportação morre junto. Fire-and-forget: sem metadados o handle é inerte.
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
      const aviso='Sessão finalizada. Os dados operacionais do JP Wealth foram removidos deste navegador. Os Tickets — incluindo pastas, histórico de concluídos e preferências do painel — não foram apagados e continuam salvos.';
      showSessionNotice(report.ok?aviso:aviso+' Aviso: algumas chaves auxiliares não puderam ser removidas: '+report.failures.join(', ')+'.');
    });
  }catch(error){
    renderSessionCommitError(error);
  }finally{
    if(bloqueou && !concluiu) resumeJPWealthPersistence();
  }
}
function renderSessionBaseChangedError(){
  sessionModal('<h3>Não foi possível finalizar a sessão</h3>'+
    '<p class="modal-sub">Nada foi apagado. Outra aba atualizou a base do JP Wealth depois que este fluxo foi aberto — finalizar agora gravaria uma versão antiga por cima do trabalho dela.</p>'+
    '<div class="session-error" role="alert">Feche este aviso e reabra o Finalizar Sessão: a base mais recente será lida de novo e uma nova exportação será exigida.</div>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Entendi</button></div>');
  sessionCancelBinding();
}
function renderSessionCommitError(error){
  sessionModal('<h3>Não foi possível finalizar a sessão</h3>'+
    '<p class="modal-sub">Nada foi apagado. O estado final não pôde ser gravado com confirmação neste navegador, então o encerramento foi interrompido com a base anterior intacta.</p>'+
    '<div class="session-error" role="alert">Falha ao gravar o estado final: '+esc((error&&error.message)||'erro não identificado')+'</div>'+
    '<div class="modal-actions"><button type="button" class="modal-btn cancel" id="sessionCancel">Cancelar</button></div>');
  sessionCancelBinding();
}
function bindFinalizeSession(){
  const b=$('finalizeSessionBtn');
  if(b) b.addEventListener('click',openFinalizeSessionFlow);
}
initSessionCrossTab();
bindFinalizeSession();
