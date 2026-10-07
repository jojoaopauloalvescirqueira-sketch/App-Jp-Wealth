// ============ ARMAZENAMENTO EM PASTA (File System Access + IndexedDB) ============
// JPW-HJFGDE §4/§6: separação obrigatória entre METADADO LÓGICO (S.dataGovernance.storage,
// vive na base, viaja no backup) e DIRETÓRIO REAL + PERMISSÃO (FileSystemDirectoryHandle,
// vive SÓ neste navegador, em IndexedDB). Um caminho gravado como texto nunca concede
// acesso a nada; um backup importado em outra máquina informa qual pasta ERA usada, mas a
// reassociação exige novo gesto do operador.
//
// Suporte real (2026): showDirectoryPicker + handles persistíveis existem em Chrome/Edge
// desktop. Safari e Firefox NÃO os expõem — neles dgFsSupported() é false e toda a
// exportação usa o fallback tradicional de Downloads (§15), mantendo nomenclatura
// progressiva e controle de backup, com a interface dizendo isso honestamente.
//
// Nenhuma função aqui lança para o chamador: tudo resolve em objetos de resultado/estado.
// Esta base guarda somente permissões; o arquivo de evidências usa armazenamento próprio.
// localStorage segue sendo o lar do estado S.
const DG_FS_DB='jpwealth_fs';
const DG_FS_STORE='handles';
const DG_FS_KEY='exportDir';
let dgFsHandleCache; // undefined = nunca carregado; null = carregado e ausente
function dgFsSupported(){
  return typeof window!=='undefined' && typeof window.showDirectoryPicker==='function'
    && typeof indexedDB!=='undefined';
}
function dgFsOpenDb(){
  return new Promise((resolve,reject)=>{
    let rq,settled=false;
    const refuse=error=>{if(settled)return;settled=true;reject(error);};
    try{rq=indexedDB.open(DG_FS_DB,1);}catch(error){refuse(error);return;}
    rq.onupgradeneeded=()=>{if(!rq.result.objectStoreNames.contains(DG_FS_STORE))rq.result.createObjectStore(DG_FS_STORE);};
    rq.onsuccess=()=>{
      if(settled){rq.result.close();return;}
      settled=true;rq.result.onversionchange=()=>rq.result.close();resolve(rq.result);
    };
    rq.onerror=()=>refuse(rq.error||new Error('IndexedDB indisponível.'));
    rq.onblocked=()=>refuse(new Error('IndexedDB bloqueado por outra aba.'));
  });
}
function dgFsDbOp(mode,op){
  // Request success is provisional: an IndexedDB transaction can still abort.
  return dgFsOpenDb().then(db=>new Promise((resolve,reject)=>{
    let transaction,request,value,error=null,settled=false;
    const finish=(ok,failure)=>{if(settled)return;settled=true;db.close();ok?resolve(value):reject(failure||error||new Error('Transação IndexedDB abortada.'));};
    try{
      transaction=db.transaction(DG_FS_STORE,mode);
      transaction.oncomplete=()=>finish(!error,error);
      transaction.onabort=()=>finish(false,transaction.error);
      transaction.onerror=()=>{error=transaction.error||new Error('Transação IndexedDB falhou.');};
      request=op(transaction.objectStore(DG_FS_STORE));
      request.onsuccess=()=>{value=request.result;};
      request.onerror=()=>{error=request.error||new Error('Operação IndexedDB falhou.');};
    }catch(failure){
      try{transaction?.abort();}catch(_){}
      finish(false,failure);
    }
  }));
}
async function dgFsLoadHandle(){
  if(dgFsHandleCache!==undefined) return dgFsHandleCache;
  try{ dgFsHandleCache=(await dgFsDbOp('readonly',store=>store.get(DG_FS_KEY)))||null; }
  catch(e){ dgFsHandleCache=null; }
  return dgFsHandleCache;
}
async function dgFsStoreHandle(handle){
  await dgFsDbOp('readwrite',store=>store.put(handle,DG_FS_KEY));
  dgFsHandleCache=handle;
}
async function dgFsClearHandle(){
  try{await dgFsDbOp('readwrite',store=>store.delete(DG_FS_KEY));dgFsHandleCache=null;return true;}
  catch(error){return false;}
}
// 'granted' | 'prompt' | 'denied' — implementações sem queryPermission caem em 'prompt'
// (não presumir concessão que não se pode verificar).
async function dgFsQueryPermission(handle){
  try{
    if(typeof handle.queryPermission==='function') return await handle.queryPermission({mode:'readwrite'});
  }catch(e){}
  return 'prompt';
}
// Exige gesto do usuário (chamar de um handler de clique).
async function dgFsRequestPermission(handle){
  try{
    if(typeof handle.requestPermission==='function') return await handle.requestPermission({mode:'readwrite'});
  }catch(e){}
  return 'denied';
}
// Estado consolidado da pasta padrão (§6/§18). Combina metadado da base + handle local:
//   unsupported   — navegador sem File System Access API
//   unconfigured  — nenhuma pasta configurada nos metadados
//   authorized    — handle presente e permissão concedida
//   prompt        — handle presente; permissão expirou e precisa de reautorização (gesto)
//   denied        — permissão negada; reautorizar ou escolher outra pasta
//   missing       — metadado diz configurado, mas NÃO há handle neste navegador
//                   (base importada em outra máquina, ou armazenamento local limpo):
//                   oferecer "Localizar esta pasta" (§6.5)
// Divergência de nome (handle.name ≠ folderName) é tratada como 'missing': o handle local
// aponta para uma pasta que não é a que a base declara — reassociar é decisão do operador.
async function dgFsStatus(){
  if(!dgFsSupported()) return {state:'unsupported',handle:null};
  const configured=!!(S.dataGovernance&&S.dataGovernance.storage&&S.dataGovernance.storage.configured);
  const handle=await dgFsLoadHandle();
  if(!configured) return {state:'unconfigured',handle:null};
  if(!handle) return {state:'missing',handle:null};
  if(S.dataGovernance.storage.folderName && handle.name!==S.dataGovernance.storage.folderName){
    return {state:'missing',handle:null};
  }
  const perm=await dgFsQueryPermission(handle);
  if(perm==='granted') return {state:'authorized',handle};
  if(perm==='denied') return {state:'denied',handle};
  return {state:'prompt',handle};
}
// Seletor de pasta (§6): grava o handle em IndexedDB e os METADADOS na base, numa ordem
// que nunca deixa estado mentiroso — primeiro a credencial local, depois o metadado.
// Cancelamento do seletor NÃO corrompe nada (§17): retorna cancelled e o estado anterior
// permanece intacto. Chamar somente de gesto do usuário.
async function dgFsPickFolder(){
  if(!dgFsSupported())return {ok:false,status:'REFUSED',reason:'unsupported'};
  if(jpWealthPersistenceOutcomeIsUnknown())return {ok:false,status:'UNKNOWN',reason:'unknown',message:'Confira a recuperação antes de alterar a pasta.'};
  if(jpWealthLoadRecoveryActive()||jpWealthPersistenceIsBlocked())return {ok:false,status:'REFUSED',reason:'blocked'};
  const epoch=jpWealthPersistenceEpoch(),previousHandle=await dgFsLoadHandle();
  let handle;
  try{handle=await window.showDirectoryPicker({mode:'readwrite'});}
  catch(error){return {ok:false,status:'REFUSED',reason:error&&(error.name==='AbortError'||error.name==='NotAllowedError')?'cancelled':'error',message:error?.message||'Falha ao abrir o seletor de pasta.'};}
  if(epoch!==jpWealthPersistenceEpoch()||jpWealthPersistenceIsBlocked())return {ok:false,status:'REFUSED',reason:'context_changed'};
  try{await dgFsStoreHandle(handle);}
  catch(error){return {ok:false,status:'REFUSED',reason:'error',message:'A autorização da pasta não foi confirmada pelo navegador: '+(error?.message||'erro desconhecido')};}
  if(epoch!==jpWealthPersistenceEpoch()||jpWealthPersistenceIsBlocked()){
    try{if(previousHandle)await dgFsStoreHandle(previousHandle);else if(await dgFsClearHandle()!==true)throw new Error('Autorização local não removida.');}catch(_){}
    return {ok:false,status:'REFUSED',reason:'context_changed'};
  }
  const previous=structuredClone(S.dataGovernance.storage),log=structuredClone(S.dataGovernance.changeLog);
  let result;
  try{
    const st=S.dataGovernance.storage;
    st.configured=true;st.folderName=handle.name;st.folderDisplayPath=handle.name;st.configuredAt=new Date().toISOString();
    if(typeof dgLogChange==='function')dgLogChange('storage','configured',handle.name,'Pasta padrão de exportação configurada: '+handle.name);
    result=jpWealthPersistDocument(S,{component:'folder-metadata'});
  }catch(error){result={status:jpWealthPersistenceOutcomeIsUnknown()?'UNKNOWN':'REFUSED',erro:error};}
  if(result.status==='CONFIRMED')return {ok:true,status:'CONFIRMED',name:handle.name};
  if(result.status==='UNKNOWN')return {ok:false,status:'UNKNOWN',reason:'unknown',message:'A pasta foi escolhida, mas a confirmação dos metadados ficou desconhecida. Confira a recuperação; não repita às cegas.'};
  S.dataGovernance.storage=previous;S.dataGovernance.changeLog=log;
  let handleRestored=true;
  try{if(previousHandle)await dgFsStoreHandle(previousHandle);else if(await dgFsClearHandle()!==true)throw new Error('Autorização local não removida.');}
  catch(error){handleRestored=false;dgFsHandleCache=null;}
  return {ok:false,status:'REFUSED',reason:'metadata_refused',message:'Os metadados da pasta não foram gravados. A escolha não foi confirmada.'+(handleRestored?'':' A autorização local precisa ser reassociada.')};
}
// Verificação NÃO destrutiva de acesso (§6/§17): permissão + sondagem real de leitura.
// Uma pasta apagada do disco mantém handle e permissão válidos — só a sondagem revela
// (NotFoundError ao iterar). Nada é escrito.
async function dgFsVerifyAccess(){
  const {state,handle}=await dgFsStatus();
  if(state!=='authorized') return {ok:false,state};
  try{
    // basta tocar o iterador; pasta vazia resolve com done:true e também prova acesso
    await handle.entries().next();
    return {ok:true,state:'authorized'};
  }catch(e){
    return {ok:false,state:'invalid',message:e&&e.message?e.message:'A pasta não pôde ser lida.'};
  }
}
// Existe arquivo com este nome? (proteção física da exportação, §8.3)
async function dgFsFileExists(handle,name){
  try{ await handle.getFileHandle(name,{create:false}); return true; }
  catch(e){
    if(e && e.name==='NotFoundError') return false;
    throw e; // TypeMismatch/NotReadable/etc: o chamador decide — não fingir que não existe
  }
}
// Gravação efetiva. Só resolve depois de close() — antes disso NADA foi confirmado no
// disco, e o chamador não deve registrar sucesso (§8.2).
async function dgFsWriteFile(handle,name,blob){
  const fh=await handle.getFileHandle(name,{create:true});
  const w=await fh.createWritable();
  try{ await w.write(blob); }
  catch(e){ try{ await w.abort(); }catch(_){} throw e; }
  await w.close();
}
