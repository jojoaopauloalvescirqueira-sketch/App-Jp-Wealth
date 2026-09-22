// Portable workspace: confirmed data stays in S; drafts never execute domain commands.
const JPW_WORKSPACE_KEYS=Object.freeze([
  'jpwealth_local_profile_v1','jpwealth_v9_icon_choice','jpwealth_v9_icon_theme',
  'jpw_fs','jpw_expl','jpw_rail','jpw_nav_submenu_rail','jpw_nav','jpw_nav_layout','jpw_nav_order','jpw_nav_glass_tint',
  'jpwealth.ui.widgetLayouts.v6','jpwealth.ui.widgetLayouts.v5','jpwealth.ui.widgetLayouts.v4',
  'jpwealth.ui.widgetLayouts.v3','jpwealth.ui.widgetLayout.v2',
  'jpwealth_notes_launcher_position_v1','jpwealth_notes_appearance_v1','jpwealth_galton_preferences_v1'
]);
const jpwWorkspaceEdited=new Map();
let jpwWorkspaceRestoring=false;
const jpwWorkspaceDraftProviders=new Map();
function jpwWorkspaceObject(value){return !!value&&typeof value==='object'&&!Array.isArray(value);}
function jpwWorkspaceCheckTree(value,depth=0){
  if(depth>30)throw new Error('Estrutura de preferências muito profunda.');
  if(value&&typeof value==='object')for(const key of Object.keys(value)){
    if(['__proto__','prototype','constructor'].includes(key))throw new Error('Campo não permitido nas preferências.');
    jpwWorkspaceCheckTree(value[key],depth+1);
  }
}
function jpwWorkspaceJpegHeader(bytes){
  if(bytes.length<4||bytes[0]!==255||bytes[1]!==216)throw new Error('JPEG inválido.');
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  for(let offset=2;offset+3<bytes.length;){
    if(bytes[offset++]!==255)break;
    while(offset<bytes.length&&bytes[offset]===255)offset++;
    const marker=bytes[offset++];
    if(marker===217||marker===218)break;
    if(marker===1||(marker>=208&&marker<=215))continue;
    const size=view.getUint16(offset);
    if(size<2||offset+size>bytes.length)break;
    if([192,193,194,195,197,198,199,201,202,203,205,206,207].includes(marker)){
      if(size<8)break;
      const height=view.getUint16(offset+3),width=view.getUint16(offset+5);
      if(width>0&&height>0)return {type:'image/jpeg',width,height};
      break;
    }
    offset+=size;
  }
  throw new Error('Dimensões JPEG indisponíveis.');
}
function jpwWorkspaceValidate(value){
  if(!jpwWorkspaceObject(value)||value.schemaVersion!==1||!jpwWorkspaceObject(value.preferences)||!Array.isArray(value.drafts))throw new Error('Formato de retomada incompatível.');
  const text=JSON.stringify(value);if(text.length>4000000)throw new Error('Retomada excede 4 MB.');
  jpwWorkspaceCheckTree(value);
  for(const [key,raw] of Object.entries(value.preferences)){
    if(!JPW_WORKSPACE_KEYS.includes(key)||!(raw===null||typeof raw==='string')||(raw&&raw.length>2000000))throw new Error('Preferência de retomada inválida.');
    if(raw===null)continue;
    if(key==='jpw_nav_glass_tint'&&!/^(?:0|[1-9]\d?|100)$/.test(raw))throw new Error('Transparência do Liquid Glass inválida.');
    if(key==='jpw_nav_submenu_rail'&&!['expanded','collapsed'].includes(raw))throw new Error('Largura da lateral em níveis inválida.');
    if(key==='jpwealth_local_profile_v1'){
      const profile=JSON.parse(raw);
      if(!jpwWorkspaceObject(profile)||profile.schemaVersion!==1||typeof profile.displayName!=='string'||[...profile.displayName].length>120||/[\u0000-\u001f\u007f-\u009f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]/.test(profile.displayName))throw new Error('Perfil no backup inválido.');
      const avatar=profile.avatarDataUrl;
      if(avatar!==null&&(typeof avatar!=='string'||avatar.length>204800||!/^data:image\/jpeg;base64,[A-Za-z0-9+/]+={0,2}$/.test(avatar)))throw new Error('Foto no backup inválida.');
      jpwWorkspaceCheckTree(profile);
      if(avatar!==null){
        const bytes=Uint8Array.from(atob(avatar.split(',')[1]),char=>char.charCodeAt(0));
        const header=jpwWorkspaceJpegHeader(bytes);
        if(header.type!=='image/jpeg'||header.width>256||header.height>256)throw new Error('Dimensões da foto inválidas.');
      }
    }else if(raw.length>100||key.includes('widget')||key.includes('notes_')||key.includes('galton')||key==='jpw_nav_order'){
      const parsed=JSON.parse(raw);jpwWorkspaceCheckTree(parsed);
      if(!jpwWorkspaceObject(parsed)&&!Array.isArray(parsed))throw new Error('Preferência estruturada inválida.');
    }
  }
  if(value.drafts.length>500)throw new Error('Muitos rascunhos para um único backup.');
  for(const item of value.drafts){
    if(!jpwWorkspaceObject(item)||typeof item.label!=='string'||item.label.length>300||typeof item.text!=='string'||item.text.length>1000000)throw new Error('Rascunho de retomada inválido.');
  }
  return structuredClone(value);
}
function jpwWorkspaceDrafts(){
  const drafts=(S?.workspaceRecovery?.drafts||[]).map(item=>({...item}));
  for(const [el,item] of jpwWorkspaceEdited){
    // Only live fields retain generic edits. Closed/discarded forms cannot return.
    if(!el.isConnected){jpwWorkspaceEdited.delete(el);continue;}
    if(el.closest('[hidden],dialog:not([open])'))continue;
    const text=el.type==='checkbox'||el.type==='radio'?String(el.checked):String(el.value);
    drafts.push({...item,text});
  }
  for(const provider of jpwWorkspaceDraftProviders.values())drafts.push(...provider());
  const execution=window.JPWForex?.executionBoardUI?.backupDrafts?.();
  if(execution)drafts.push({label:'Operação — edição não confirmada',text:JSON.stringify(execution)});
  return drafts.filter((item,index,all)=>all.findIndex(other=>other.label===item.label&&other.text===item.text)===index);
}
function jpwWorkspaceCapture(){
  if(S?.workspaceRecovery?.pending)return jpwWorkspaceValidate(S.workspaceRecovery.snapshot);
  const preferences={};
  for(const key of JPW_WORKSPACE_KEYS)preferences[key]=localStorage.getItem(key);
  return jpwWorkspaceValidate({schemaVersion:1,preferences,drafts:jpwWorkspaceDrafts()});
}
function jpwWorkspaceAdoptImport(){
  jpwWorkspaceEdited.clear();
  sessionResetAuxiliarySurfaces();
  for(const provider of jpwWorkspaceDraftProviders.values())provider(true);
  window.JPWForex?.executionBoardUI?.discard();
}

// Main document is the durable restore journal. Partial projection is recoverable,
// never acknowledged as complete. Old backups do not carry a journal or preferences.
function jpwWorkspaceResume(){
  const pending=S?.workspaceRecovery;
  if(!pending?.pending)return true;
  if(jpwWorkspaceRestoring)return false;
  jpwWorkspaceRestoring=true;
  try{
    const snapshot=jpwWorkspaceValidate(pending.snapshot);
    if(jpWealthPersistenceOutcomeIsUnknown())throw new Error('Resultado de gravação desconhecido.');
    const expected=jpWealthLastPersistedRawGet();
    for(const [key,value] of Object.entries(snapshot.preferences)){
      if(localStorage.getItem(LSKEY)!==expected)throw new Error('A base mudou durante a retomada.');
      if(value===null)localStorage.removeItem(key);else localStorage.setItem(key,value);
      if(localStorage.getItem(key)!==value)throw new Error('Preferência não confirmada: '+key);
    }
    const previous=S.workspaceRecovery;
    S.workspaceRecovery={schemaVersion:1,pending:false,drafts:snapshot.drafts};
    if(save()!==true||localStorage.getItem(LSKEY)!==jpWealthLastPersistedRawGet()){
      S.workspaceRecovery=previous;
      throw new Error('Não foi possível confirmar a retomada.');
    }
    return true;
  }catch(error){
    blockJPWealthPersistence();
    const show=()=>{
      let box=document.getElementById('workspaceRestoreWarning');
      if(!box){box=document.createElement('div');box.id='workspaceRestoreWarning';box.setAttribute('role','alert');document.body.prepend(box);}
      box.textContent='Restauração incompleta. Preserve o arquivo de backup. Confira o armazenamento e recarregue para retomar a aplicação das preferências. '+error.message;
    };
    if(document.body)show();else document.addEventListener('DOMContentLoaded',show,{once:true});
    return false;
  }finally{jpwWorkspaceRestoring=false;}
}
function jpwWorkspaceCaptureField(event){
  const el=event.target;
  if(!(el instanceof HTMLInputElement||el instanceof HTMLTextAreaElement||el instanceof HTMLSelectElement)||el.closest('#workspaceDraftDialog'))return;
  if(el.closest('#settingsProfileForm,#mvpNotesDrawer,#ebObservationForm')||el.hasAttribute('data-eb-field'))return;
  const identity=[el.id,el.name,el.autocomplete,el.type,...Object.keys(el.dataset)].join(' ');
  if(/password|senha|secret|token|credential|pin|file|hidden|search|filter|session/i.test(identity))return;
  const label=(el.labels?.[0]?.textContent||el.getAttribute('aria-label')||el.id||el.name||Object.entries(el.dataset).map(([k,v])=>k+':'+v).join(' ')).trim().slice(0,300);
  if(!label)return;
  const text=el.type==='checkbox'||el.type==='radio'?String(el.checked):String(el.value);
  jpwWorkspaceEdited.set(el,{label,text});
}
function jpwWorkspaceShowDrafts(){
  let dialog=document.getElementById('workspaceDraftDialog');
  if(dialog)dialog.remove();
  dialog=document.createElement('dialog');dialog.id='workspaceDraftDialog';
  const title=document.createElement('h3');title.id='workspaceDraftTitle';title.textContent='Rascunhos recuperados';dialog.setAttribute('aria-labelledby',title.id);dialog.append(title);
  const hint=document.createElement('p');hint.textContent='Conteúdo em edição guardado no backup. Revise e copie para o formulário correspondente. Estes rascunhos não registram operações automaticamente.';dialog.append(hint);
  for(const item of S?.workspaceRecovery?.drafts||[]){
    const label=document.createElement('label');label.textContent=item.label;
    const area=document.createElement('textarea');area.readOnly=true;area.value=item.text;area.rows=4;label.append(area);dialog.append(label);
  }
  const close=document.createElement('button');close.type='button';close.textContent='Fechar';close.className='modal-btn confirm';close.onclick=()=>dialog.close();
  const actions=document.createElement('div');actions.className='workspace-draft-actions';actions.append(close);dialog.append(actions);
  const clear=document.createElement('button');clear.type='button';clear.textContent='Excluir rascunhos recuperados';clear.className='reset-btn';
  clear.onclick=()=>{
    if(!confirm('Excluir os rascunhos recuperados? Os registros confirmados não serão alterados.'))return;
    const previous=S.workspaceRecovery,previousRaw=jpWealthLastPersistedRawGet();
    S.workspaceRecovery={schemaVersion:1,pending:false,drafts:[]};
    try{
      const expected=JSON.stringify(S,(k,v)=>k==='investorPassword'?'':v);
      const saved=save(),actual=localStorage.getItem(LSKEY);
      if(saved!==true||actual!==expected){
        S.workspaceRecovery=previous;
        if(actual===previousRaw)jpWealthAdoptPersistedRaw(previousRaw);
        else markJPWealthPersistenceOutcomeUnknown('Exclusão de rascunhos sem confirmação.');
        alert('Exclusão não confirmada. Recarregue e confira os rascunhos antes de tentar novamente.');return;
      }
      dialog.close();jpwWorkspaceRender();
    }catch(error){
      S.workspaceRecovery=previous;markJPWealthPersistenceOutcomeUnknown('Não foi possível conferir os rascunhos.');
      alert('Exclusão não confirmada. Recarregue e confira os rascunhos antes de tentar novamente.');
    }
  };actions.append(clear);
  document.body.append(dialog);dialog.showModal();close.focus();
}
function jpwWorkspaceRender(){
  if(S?.workspaceRecovery?.pending)return;
  let button=document.getElementById('workspaceDraftsButton');
  const count=S?.workspaceRecovery?.drafts?.length||0;
  if(!count){button?.remove();return;}
  if(!button){button=document.createElement('button');button.id='workspaceDraftsButton';button.type='button';button.className='reset-btn';button.onclick=jpwWorkspaceShowDrafts;document.body.append(button);}
  button.textContent='Rascunhos recuperados ('+count+')';
}
document.addEventListener('input',jpwWorkspaceCaptureField,true);
document.addEventListener('change',jpwWorkspaceCaptureField,true);
document.addEventListener('DOMContentLoaded',jpwWorkspaceRender);
