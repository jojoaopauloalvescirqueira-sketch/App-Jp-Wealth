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
// A ÚNICA base IndexedDB do projeto é esta; localStorage segue sendo o lar do estado S.
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
    let rq;
    try{ rq=indexedDB.open(DG_FS_DB,1); }
    catch(e){ reject(e); return; }
    rq.onupgradeneeded=()=>{ rq.result.createObjectStore(DG_FS_STORE); };
    rq.onsuccess=()=>resolve(rq.result);
    rq.onerror=()=>reject(rq.error||new Error('IndexedDB indisponível.'));
    rq.onblocked=()=>reject(new Error('IndexedDB bloqueado por outra aba.'));
  });
}
function dgFsDbOp(mode,op){
  // Uma transação curta por operação; o db fecha em seguida para nunca segurar bloqueio.
  return dgFsOpenDb().then(db=>new Promise((resolve,reject)=>{
    let rq;
    try{ rq=op(db.transaction(DG_FS_STORE,mode).objectStore(DG_FS_STORE)); }
    catch(e){ db.close(); reject(e); return; }
    rq.onsuccess=()=>{ db.close(); resolve(rq.result); };
    rq.onerror=()=>{ db.close(); reject(rq.error||new Error('Operação IndexedDB falhou.')); };
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
  try{ await dgFsDbOp('readwrite',store=>store.delete(DG_FS_KEY)); }catch(e){}
  dgFsHandleCache=null;
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
  if(!dgFsSupported()) return {ok:false,reason:'unsupported'};
  let handle;
  try{
    handle=await window.showDirectoryPicker({mode:'readwrite'});
  }catch(e){
    if(e && (e.name==='AbortError'||e.name==='NotAllowedError')) return {ok:false,reason:'cancelled'};
    return {ok:false,reason:'error',message:e&&e.message?e.message:'Falha ao abrir o seletor de pasta.'};
  }
  try{
    await dgFsStoreHandle(handle);
  }catch(e){
    return {ok:false,reason:'error',message:'A pasta foi escolhida, mas o navegador não conseguiu guardar a autorização (IndexedDB): '+(e&&e.message?e.message:'erro desconhecido.')};
  }
  const st=S.dataGovernance.storage;
  st.configured=true;
  st.folderName=handle.name;
  // A API não expõe o caminho completo por segurança; o nome da pasta é o que existe
  // para mostrar. Metadado de exibição, nunca credencial (§6.1).
  st.folderDisplayPath=handle.name;
  st.configuredAt=new Date().toISOString();
  if(typeof dgLogChange==='function') dgLogChange('storage','configured',handle.name,'Pasta padrão de exportação configurada: '+handle.name);
  save();
  return {ok:true,name:handle.name};
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
