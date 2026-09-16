// ============ CENTRAL DE CONFIGURAÇÕES (N1 / PERFIL LOCAL N2) ============
// Mantém os controles legados no mesmo DOM: apenas os transporta enquanto a central está aberta.
// Arquitetura de navegação: categorias declarativas na sidebar (algumas são grupos com subpáginas,
// 'general' e 'about' são páginas diretas). Todas as páginas — grupo ou folha — são registradas
// como [data-settings-panel] e alternadas por 'hidden', preservando o contrato já usado pelos
// testes (activateSettingsCategory(id) continua tornando o painel 'id' visível).

const SETTINGS_GROUPS=[
  {id:'general', label:'Geral', icon:'general'},
  {id:'appearance-interface', label:'Aparência e Interface', desc:'Tema, ícone, organização visual e editor.', icon:'appearance', children:['appearance','interface','editor']},
  {id:'method-governance', label:'Método e Governança', desc:'Estatuto operacional, parâmetros e calibração.', icon:'governance', children:['statute','parameters']},
  {id:'operations', label:'Operação', desc:'Parâmetros do ciclo e Checklist pré-trade.', icon:'operations', children:['tool-params','tool-check']},
  {id:'forex-preferences', label:'Forex', desc:'Preferências de consulta do Consolidado FX.', icon:'operations', children:['forex-consolidated']},
  {id:'knowledge', label:'Conhecimento', desc:'Material educacional e referências do método.', icon:'knowledge', children:['educational']},
  {id:'data-security', label:'Dados e Segurança', desc:'Backup, recuperação, armazenamento e integridade.', icon:'data', children:['backup','storage']},
  {id:'about', label:'Sobre', icon:'about'}
];
const SETTINGS_LEAVES={
  account:{label:'JP Wealth Account', group:null, desc:'Sua identidade local neste navegador.', terms:['perfil','conta local','nome de exibição','foto','avatar','galeria','JP Wealth Account']},
  about:{label:'Sobre', group:null, terms:['sobre','versão','build','offline','armazenamento','documentação','changelog']},
  appearance:{label:'Aparência', group:'appearance-interface', desc:'Tema e ícone do aplicativo.', terms:['tema','aparência','ícone','paleta','contraste']},
  interface:{label:'Interface', group:'appearance-interface', desc:'Tamanho do texto e instruções do sistema.', terms:['interface','fonte','tamanho','tipografia','sidebar','barra lateral','ajuda','instruções']},
  editor:{label:'Editor', group:'appearance-interface', desc:'Preferências de edição.', terms:['editor']},
  educational:{label:'Centro Educacional', group:'knowledge', desc:'Fundamentos, glossário e perguntas frequentes.', terms:['educacional','centro educacional','forex','pip','spread','glossário','perguntas frequentes']},
  statute:{label:'Estatuto Operacional', group:'method-governance', desc:'Estatuto V11.0 e Anexo Paramétrico Canônico vigentes.', terms:['estatuto','V11','anexo','diretrizes','artigos','pdf','governança']},
  parameters:{label:'Parâmetros e Calibração', group:'method-governance', desc:'Valores, limites, perfis e modelo estatístico.', terms:['parâmetros','calibração','mdd','drawdown','alavancagem','gênese','quarentena','mei']},
  'tool-params':{label:'Parâmetros', group:'operations', desc:'Motor Forex, observações da conta, política V11 e propostas locais.', terms:['parâmetros','saldo','ciclo','constantes','decisões','matriz','V11','seis fases','reservas','editor']},
  'tool-check':{label:'Checklist', group:'operations', desc:'Checklist pré-trade e pontuação do filtro.', terms:['checklist','pré-trade','pontuação','filtro','nocuda','setup']},
  'forex-consolidated':{label:'Conta padrão do Consolidado',group:'forex-preferences',desc:'Seleção analítica independente da conta operacional.',terms:['forex','consolidado','MT5','conta padrão','mestre','histórico']},
  backup:{label:'Backup e Recuperação', group:'data-security', desc:'Exportar, importar e restaurar o estado completo.', terms:['backup','exportar','importar','recuperação','reset','limpar','pasta padrão','pasta de armazenamento','sequência de exportação','backup confirmado','reautorizar pasta','alterações desde o backup']},
  storage:{label:'Armazenamento Local', group:'data-security', desc:'Informações sobre os dados salvos neste navegador.', terms:['armazenamento','local','schema','integridade','offline']}
};
const SETTINGS_GROUP_BY_ID=Object.fromEntries(SETTINGS_GROUPS.map(g=>[g.id,g]));

const SETTINGS_ICONS={
  account:'<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
  general:'<path d="M4 7h11M19 7h1M4 12h6M14 12h6M4 17h13M21 17h-1"/><circle cx="17" cy="7" r="2"/><circle cx="11" cy="12" r="2"/><circle cx="18" cy="17" r="2"/>',
  appearance:'<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/>',
  governance:'<path d="M4 19h16"/><path d="M6 19V9l6-4 6 4v10"/><path d="M10 19v-6h4v6"/>',
  operations:'<circle cx="12" cy="12" r="8"/><path d="M12 4v3M12 17v3M4 12h3M17 12h3"/><circle cx="12" cy="12" r="2"/>',
  knowledge:'<path d="M12 6c-1.8-1.2-4.2-1.6-6.5-1v12.5c2.3-.6 4.7-.2 6.5 1 1.8-1.2 4.2-1.6 6.5-1V5c-2.3-.6-4.7-.2-6.5 1Z"/><path d="M12 6v12.5"/>',
  probability:'<path d="M5 20h14M8 20v-4l4-2 4 2v4M12 14V8"/><circle cx="12" cy="5" r="2"/><circle cx="8" cy="11" r="1.5"/><circle cx="16" cy="11" r="1.5"/>',
  data:'<path d="M12 3c4 0 7 1.1 7 2.5S16 8 12 8s-7-1.1-7-2.5S8 3 12 3Z"/><path d="M5 5.5V12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V5.5"/><path d="M5 12v6.5c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V12"/>',
  about:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle cx="12" cy="7.5" r=".2" fill="currentColor" stroke-width="2.4"/>',
  calendar:'<rect x="4" y="5.5" width="16" height="15" rx="2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/><path d="M8 14h2M14 14h2M8 17.2h2"/>',
  back:'<path d="M14.5 5 7 12l7.5 7"/>',
  forward:'<path d="M9.5 5 17 12l-7.5 7"/>',
  chevron:'<path d="m9 6 6 6-6 6"/>'
};
function settingsIconSvg(name){ return `<svg viewBox="0 0 24 24" aria-hidden="true">${SETTINGS_ICONS[name]||''}</svg>`; }

const settingsState={
  open:false, active:'general', query:'', opener:null, legacyNodes:[], railParent:null, railNext:null,
  suspended:false, subdialogLauncher:null, observer:null, highlightTimer:null,
  navStack:['general'], navIndex:0, mobileListVisible:true
};
window.__settingsModalDebug={opens:0,observerInstances:0,focusTrapActive:false};

function settingsEl(id){ return document.getElementById(id); }

// Preferência por navegador, incluída no workspace do backup, fora dos schemas
// financeiros. Uma escrita explícita contém nome e foto juntos; leitura é pura.
const SETTINGS_PROFILE_KEY='jpwealth_local_profile_v1';
const SETTINGS_PROFILE_MAX_FILE=5*1024*1024;
const SETTINGS_PROFILE_MAX_PIXELS=16*1000*1000;
const SETTINGS_PROFILE_MAX_AVATAR=200*1024;
const settingsProfileState={
  confirmed:{displayName:'',avatarDataUrl:null},draft:{displayName:'',avatarDataUrl:null},
  raw:null,envelope:{},blocked:null,note:'',status:'info',editing:false,
  token:0,epoch:0,busy:false,saving:false,reader:null
};
function settingsProfileEpoch(){ return Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0; }
function settingsProfileNameValid(value){
  return typeof value==='string'&&Array.from(value).length<=120&&!/[\u0000-\u001f\u007f-\u009f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]/.test(value);
}
function settingsProfileImageHeader(bytes){
  const bad=()=>{ throw new Error('Escolha uma imagem PNG, JPEG ou WebP válida.'); };
  if(!(bytes instanceof Uint8Array)||bytes.length<12) return bad();
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  const text=(start,count)=>String.fromCharCode(...bytes.subarray(start,start+count));
  let type,width,height;
  if(bytes[0]===137&&text(1,3)==='PNG'&&bytes[4]===13&&bytes[5]===10&&bytes[6]===26&&bytes[7]===10){
    if(bytes.length<33||text(12,4)!=='IHDR'||view.getUint32(8)!==13) return bad();
    type='image/png';width=view.getUint32(16);height=view.getUint32(20);
    // APNG é recusado: o perfil aceita uma imagem estática, sem quadros ocultos.
    for(let offset=8;offset+12<=bytes.length;){
      const size=view.getUint32(offset); if(size>bytes.length-offset-12) return bad();
      if(text(offset+4,4)==='acTL') throw new Error('Escolha uma imagem estática, sem animação.');
      if(text(offset+4,4)==='IEND') break;
      offset+=12+size;
    }
  }else if(bytes[0]===255&&bytes[1]===216){
    type='image/jpeg';
    let offset=2;
    while(offset+3<bytes.length){
      if(bytes[offset++]!==255) return bad();
      while(offset<bytes.length&&bytes[offset]===255) offset++;
      const marker=bytes[offset++];
      if(marker===217||marker===218) break;
      if(marker===1||(marker>=208&&marker<=215)) continue;
      if(offset+2>bytes.length) return bad();
      const size=view.getUint16(offset); if(size<2||offset+size>bytes.length) return bad();
      if([192,193,194,195,197,198,199,201,202,203,205,206,207].includes(marker)){
        if(size<8) return bad();
        height=view.getUint16(offset+3);width=view.getUint16(offset+5);break;
      }
      offset+=size;
    }
  }else if(text(0,4)==='RIFF'&&text(8,4)==='WEBP'){
    type='image/webp';
    if(view.getUint32(4,true)+8!==bytes.length) return bad();
    let frameWidth=0,frameHeight=0;
    for(let offset=12;offset+8<=bytes.length;){
      const size=view.getUint32(offset+4,true),start=offset+8,kind=text(offset,4);
      if(size>bytes.length-start) return bad();
      if(kind==='ANIM'||kind==='ANMF') throw new Error('Escolha uma imagem estática, sem animação.');
      if(kind==='VP8X'){
        if(size<10) return bad();
        if(bytes[start]&2) throw new Error('Escolha uma imagem estática, sem animação.');
        width=1+bytes[start+4]+(bytes[start+5]<<8)+(bytes[start+6]<<16);
        height=1+bytes[start+7]+(bytes[start+8]<<8)+(bytes[start+9]<<16);
      }else if(kind==='VP8 '){
        if(size<10||bytes[start+3]!==157||bytes[start+4]!==1||bytes[start+5]!==42) return bad();
        frameWidth=view.getUint16(start+6,true)&16383;frameHeight=view.getUint16(start+8,true)&16383;
      }else if(kind==='VP8L'){
        if(size<5||bytes[start]!==47) return bad();
        frameWidth=1+bytes[start+1]+((bytes[start+2]&63)<<8);
        frameHeight=1+(bytes[start+2]>>6)+(bytes[start+3]<<2)+((bytes[start+4]&15)<<10);
      }
      offset=start+size+(size&1);
    }
    // O canvas VP8X não pode encobrir um frame de outras dimensões. Confira
    // ambos antes da decodificação, para que o limite de pixels seja real.
    if(!frameWidth||!frameHeight||(width&&(width!==frameWidth||height!==frameHeight))) return bad();
    width=frameWidth;height=frameHeight;
  }else return bad();
  if(!width||!height) return bad();
  if(width*height>SETTINGS_PROFILE_MAX_PIXELS) throw new Error('A imagem deve ter até 16 megapixels.');
  return {type,width,height};
}
function settingsProfileAvatarValid(value){
  if(value===null) return true;
  if(typeof value!=='string'||value.length>SETTINGS_PROFILE_MAX_AVATAR||!/^data:image\/jpeg;base64,[A-Za-z0-9+/]+={0,2}$/.test(value)) return false;
  try{
    const binary=atob(value.slice(value.indexOf(',')+1));
    const header=settingsProfileImageHeader(Uint8Array.from(binary,char=>char.charCodeAt(0)));
    return header.type==='image/jpeg'&&header.width<=256&&header.height<=256;
  }catch(error){ return false; }
}
function settingsProfileRead(){
  const empty={displayName:'',avatarDataUrl:null};
  let raw=null;
  try{ raw=localStorage.getItem(SETTINGS_PROFILE_KEY); }
  catch(error){ return {raw,value:empty,envelope:{},blocked:'read',note:'Não foi possível ler o perfil. O conteúdo salvo foi preservado; recarregue a página para tentar novamente.'}; }
  if(raw===null) return {raw,value:empty,envelope:{},blocked:null,note:''};
  try{
    const parsed=JSON.parse(raw);
    if(!parsed||typeof parsed!=='object'||Array.isArray(parsed)||parsed.schemaVersion!==1||
       !settingsProfileNameValid(parsed.displayName)||(parsed.avatarDataUrl!==null&&typeof parsed.avatarDataUrl!=='string')) throw new Error('incompatible');
    return {raw,value:{displayName:parsed.displayName,avatarDataUrl:parsed.avatarDataUrl},envelope:parsed,blocked:null,
      note:settingsProfileAvatarValid(parsed.avatarDataUrl)?'':'A foto salva está indisponível. Escolha outra foto ou remova-a antes de salvar; o conteúdo original permanece intacto.'};
  }catch(error){ return {raw,value:empty,envelope:{},blocked:'invalid',note:'O perfil salvo não pôde ser reconhecido. Nada foi sobrescrito; recarregue após recuperar o conteúdo local.'}; }
}
function settingsProfileCancelAsync(){
  settingsProfileState.token++;settingsProfileState.busy=false;settingsProfileState.saving=false;
  const reader=settingsProfileState.reader;settingsProfileState.reader=null;
  if(reader&&reader.readyState===1){ try{reader.abort();}catch(error){} }
}
function settingsProfileReload(){
  if(settingsProfileState.blocked==='session'){renderSettingsProfile();return;}
  settingsProfileCancelAsync();
  const read=settingsProfileRead();
  Object.assign(settingsProfileState,{confirmed:{...read.value},draft:{...read.value},raw:read.raw,envelope:read.envelope,
    blocked:read.blocked,note:read.note,status:read.blocked?'blocked':read.note?'error':'info',epoch:settingsProfileEpoch(),editing:false,saving:false});
  renderSettingsProfile();
}
function settingsProfileDirty(){
  const {confirmed,draft}=settingsProfileState;
  return confirmed.displayName!==draft.displayName||confirmed.avatarDataUrl!==draft.avatarDataUrl;
}
function settingsProfileSetStatus(message,state){
  settingsProfileState.note=message;settingsProfileState.status=state;
  const status=settingsEl('settingsProfileStatus');
  if(status){status.textContent=message;status.dataset.state=state;}
}
function settingsProfileInitials(name){
  const parts=name.trim().split(/\s+/u).filter(Boolean);
  if(!parts.length) return 'JP';
  return (Array.from(parts[0])[0]+(parts.length>1?Array.from(parts[parts.length-1])[0]:'')).toLocaleUpperCase('pt-BR');
}
function renderSettingsProfileAvatar(element,profile){
  if(!element) return;
  const initials=settingsProfileInitials(profile.displayName);
  element.replaceChildren(document.createTextNode(initials));
  if(!profile.avatarDataUrl||!settingsProfileAvatarValid(profile.avatarDataUrl)) return;
  const picture=document.createElement('img');picture.alt='';picture.draggable=false;
  picture.addEventListener('error',()=>{
    if(picture.parentNode!==element) return;
    element.replaceChildren(document.createTextNode(initials));
    if(element.id==='settingsAccountAvatar'&&settingsState.active==='account') settingsProfileSetStatus('A foto está indisponível. Escolha outra foto ou remova-a; o conteúdo salvo foi preservado.','error');
  },{once:true});
  picture.src=profile.avatarDataUrl;element.replaceChildren(picture);
}
function renderSettingsProfile(){
  const state=settingsProfileState,name=state.confirmed.displayName.trim()||'Seu perfil';
  const rowName=settingsEl('settingsProfileName');if(rowName) rowName.textContent=name;
  const row=settingsEl('settingsProfileBtn');if(row) row.setAttribute('aria-label','JP Wealth Account — '+name);
  renderSettingsProfileAvatar(settingsEl('settingsProfileAvatar'),state.confirmed);
  renderSettingsProfileAvatar(settingsEl('headerProfileAvatar'),state.confirmed);
  const headerProfile=settingsEl('headerProfileBtn');
  if(headerProfile){
    headerProfile.setAttribute('aria-label','Abrir configurações do perfil — '+name);
    headerProfile.title='Abrir perfil — '+name;
  }
  renderSettingsProfileAvatar(settingsEl('settingsAccountAvatar'),state.draft);
  const heading=settingsEl('settingsAccountHeading');if(heading) heading.textContent=state.draft.displayName.trim()||'Seu perfil';
  const input=settingsEl('settingsProfileNameInput');
  if(input){ if(input.value!==state.draft.displayName) input.value=state.draft.displayName;input.disabled=!!state.blocked||state.saving; }
  const disabled=!!state.blocked||state.saving;
  const save=settingsEl('settingsProfileSaveBtn');if(save) save.disabled=disabled||state.busy||!settingsProfileDirty();
  const choose=settingsEl('settingsProfileChoosePhotoBtn');if(choose) choose.disabled=disabled;
  const remove=settingsEl('settingsProfileRemovePhotoBtn');if(remove) remove.disabled=disabled||(!state.draft.avatarDataUrl&&!state.busy);
  const cancel=settingsEl('settingsProfileCancelBtn');if(cancel) cancel.disabled=state.blocked==='unknown'||state.saving||(!settingsProfileDirty()&&!state.busy&&state.blocked!=='conflict');
  renderSettingsProfileGallery();
  settingsProfileSetStatus(state.note,state.status);
}
function beginSettingsProfileDraft(){
  if(settingsProfileState.blocked==='unknown') {renderSettingsProfile();return;}
  settingsProfileReload();settingsProfileState.editing=true;
}
function cancelSettingsProfileDraft(){
  settingsProfileCancelAsync();
  if(settingsProfileState.blocked==='unknown'){renderSettingsProfile();return;}
  settingsProfileReload();
}
function settingsProfileGalleryPanel(){
  const groups=[...new Set(SETTINGS_PROFILE_AVATARS.map(avatar=>avatar.group))];
  return `<details id="settingsProfileGallery" class="settings-avatar-gallery">
    <summary><span>Galeria do JP Wealth<small>19 retratos para escolher</small></span></summary>
    <div class="settings-avatar-filters">
      <label for="settingsProfileAvatarSearch">Buscar por nome<input id="settingsProfileAvatarSearch" type="search" placeholder="Buscar retrato" autocomplete="off" spellcheck="false"></label>
      <label for="settingsProfileAvatarGroup">Grupo<select id="settingsProfileAvatarGroup"><option value="all">Todos os grupos</option>${groups.map(group=>`<option value="${settingsEsc(group)}">${settingsEsc(group)}</option>`).join('')}</select></label>
    </div>
    <p id="settingsProfileAvatarCount" class="settings-avatar-count" role="status" aria-live="polite"></p>
    <div class="settings-avatar-results">
      ${groups.map((group,index)=>`<section class="settings-avatar-group" data-avatar-group="${settingsEsc(group)}" aria-labelledby="settingsAvatarGroup${index}"><h5 id="settingsAvatarGroup${index}">${settingsEsc(group)}</h5><div class="settings-avatar-grid">${SETTINGS_PROFILE_AVATARS.filter(avatar=>avatar.group===group).map(avatar=>`<button type="button" class="settings-avatar-choice" data-profile-avatar="${settingsEsc(avatar.id)}" aria-label="Usar retrato de ${settingsEsc(avatar.name)}" aria-pressed="false"><span class="settings-avatar-picture"><img src="${avatar.avatarDataUrl}" alt="" width="72" height="72" loading="lazy" decoding="async" draggable="false"><span class="settings-avatar-check" aria-hidden="true">✓</span></span><span>${settingsEsc(avatar.name)}</span></button>`).join('')}</div></section>`).join('')}
      <p id="settingsProfileAvatarEmpty" class="note" hidden>Nenhum retrato encontrado. Tente outro nome ou grupo.</p>
    </div>
    <p id="settingsProfileAvatarSelection" class="settings-avatar-selection" aria-live="polite"></p>
  </details>`;
}
function renderSettingsProfileGallery(){
  const gallery=settingsEl('settingsProfileGallery');if(!gallery) return;
  const state=settingsProfileState;
  const normalize=value=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const query=normalize(settingsEl('settingsProfileAvatarSearch').value.trim());
  const group=settingsEl('settingsProfileAvatarGroup').value;
  let count=0;
  gallery.querySelectorAll('[data-profile-avatar]').forEach(button=>{
    const avatar=SETTINGS_PROFILE_AVATARS.find(item=>item.id===button.dataset.profileAvatar);
    const visible=(group==='all'||avatar.group===group)&&normalize(avatar.name).includes(query);
    button.hidden=!visible;if(visible) count++;
    button.disabled=!!state.blocked||state.saving;
    button.setAttribute('aria-pressed',String(state.draft.avatarDataUrl===avatar.avatarDataUrl));
  });
  gallery.querySelectorAll('[data-avatar-group]').forEach(section=>{section.hidden=!section.querySelector('[data-profile-avatar]:not([hidden])');});
  settingsEl('settingsProfileAvatarEmpty').hidden=count>0;
  const counter=settingsEl('settingsProfileAvatarCount');
  const result=`${count} ${count===1?'retrato disponível':'retratos disponíveis'}`;
  if(counter.textContent!==result) counter.textContent=result;
  const selected=SETTINGS_PROFILE_AVATARS.find(avatar=>avatar.avatarDataUrl===state.draft.avatarDataUrl);
  const selection=settingsEl('settingsProfileAvatarSelection');
  const label=selected?`Selecionado: ${selected.name}.`:'Escolha um retrato para ver a prévia no seu perfil.';
  if(selection.textContent!==label) selection.textContent=label;
}
function selectSettingsProfileAvatar(id){
  const state=settingsProfileState;
  if(state.blocked||state.saving||state.epoch!==settingsProfileEpoch()) return;
  const avatar=SETTINGS_PROFILE_AVATARS.find(item=>item.id===id);
  if(!avatar||!settingsProfileAvatarValid(avatar.avatarDataUrl)) return;
  // Invalida um upload anterior que ainda possa terminar depois da escolha.
  settingsProfileCancelAsync();state.editing=true;
  state.draft.avatarDataUrl=avatar.avatarDataUrl;
  settingsProfileSetStatus(`Prévia de ${avatar.name}. Salve o perfil para confirmar a foto.`,'dirty');
  renderSettingsProfile();
}
function settingsAccountPanel(){
  return `<form id="settingsProfileForm" class="settings-account-form" novalidate>
    <section class="settings-account-group" aria-label="Identidade local">
      <div class="settings-account-row"><label for="settingsProfileNameInput">Nome de exibição</label><input id="settingsProfileNameInput" type="text" autocomplete="off" spellcheck="false" aria-describedby="settingsProfileNameHelp"><p class="note" id="settingsProfileNameHelp">Até 120 caracteres. Deixe vazio para usar Seu perfil.</p></div>
      <div class="settings-account-row"><span>Foto do perfil</span><div class="settings-account-photo-actions"><input id="settingsProfilePhotoInput" type="file" accept="image/png,image/jpeg,image/webp" hidden><button type="button" class="reset-btn" id="settingsProfileChoosePhotoBtn">Escolher foto</button><button type="button" class="reset-btn" id="settingsProfileRemovePhotoBtn">Remover foto</button></div><p class="note">PNG, JPEG ou WebP estático. Até 5 MiB e 16 megapixels.</p></div>
    </section>
    ${settingsProfileGalleryPanel()}
    <p class="settings-account-privacy">Seu nome e sua foto ficam neste navegador e são incluídos no backup completo. A foto não é enviada a servidores. Finalizar sessão mantém o perfil salvo.</p>
    <p id="settingsProfileStatus" role="status" aria-live="polite" data-state="info"></p>
    <div class="settings-account-actions"><button type="button" class="reset-btn" id="settingsProfileCancelBtn">Cancelar</button><button type="submit" class="reset-btn settings-account-save" id="settingsProfileSaveBtn">Salvar perfil</button></div>
  </form>`;
}
function settingsProfileReadFile(file){
  return new Promise((resolve,reject)=>{
    const reader=new FileReader();settingsProfileState.reader=reader;
    reader.onload=()=>resolve(new Uint8Array(reader.result));
    reader.onerror=()=>reject(new Error('Não foi possível ler a imagem. A foto anterior foi mantida.'));
    reader.onabort=()=>reject(new Error('Leitura cancelada.'));
    reader.readAsArrayBuffer(file);
  });
}
async function settingsProfileRaster(bytes,header){
  const url=URL.createObjectURL(new Blob([bytes],{type:header.type}));
  const picture=new Image();
  try{
    await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(new Error('Não foi possível abrir a imagem.')),10000);
      picture.onload=()=>{clearTimeout(timer);resolve();};
      picture.onerror=()=>{clearTimeout(timer);reject(new Error('Não foi possível abrir a imagem. A foto anterior foi mantida.'));};
      picture.src=url;
    });
    const width=picture.naturalWidth,height=picture.naturalHeight;
    if(!width||!height||width*height>SETTINGS_PROFILE_MAX_PIXELS) throw new Error('A imagem deve ter até 16 megapixels.');
    const edge=Math.min(width,height),size=Math.min(256,edge),canvas=document.createElement('canvas');
    canvas.width=size;canvas.height=size;
    const context=canvas.getContext('2d');if(!context) throw new Error('Não foi possível preparar a foto neste navegador.');
    context.fillStyle='#ffffff';context.fillRect(0,0,size,size);
    context.drawImage(picture,(width-edge)/2,(height-edge)/2,edge,edge,0,0,size,size);
    // Canvas gera um novo raster: nenhum EXIF, nome de arquivo ou URL original
    // integra a preferência. O limite inclui o prefixo/base64 persistido.
    const raster=canvas.toDataURL('image/jpeg',0.86);
    if(!settingsProfileAvatarValid(raster)) throw new Error('Não foi possível preparar uma foto compacta. Escolha outra imagem.');
    return raster;
  }finally{ picture.onload=null;picture.onerror=null;picture.src='';URL.revokeObjectURL(url); }
}
async function selectSettingsProfilePhoto(file){
  if(!file||settingsProfileState.blocked||settingsProfileState.saving) return;
  settingsProfileCancelAsync();
  settingsProfileState.editing=true;
  const token=settingsProfileState.token,epoch=settingsProfileState.epoch;
  const current=()=>token===settingsProfileState.token&&epoch===settingsProfileEpoch()&&settingsProfileState.editing;
  try{
    if(file.size<=0||file.size>SETTINGS_PROFILE_MAX_FILE) throw new Error('Escolha uma imagem de até 5 MiB.');
    if(!['image/png','image/jpeg','image/webp'].includes(file.type)) throw new Error('Escolha uma imagem PNG, JPEG ou WebP.');
    settingsProfileState.busy=true;settingsProfileSetStatus('Preparando a foto…','busy');renderSettingsProfile();
    const bytes=await settingsProfileReadFile(file);if(!current()) return;
    const header=settingsProfileImageHeader(bytes);
    if(header.type!==file.type) throw new Error('O conteúdo não corresponde ao formato da imagem.');
    const raster=await settingsProfileRaster(bytes,header);if(!current()) return;
    settingsProfileState.draft.avatarDataUrl=raster;
    settingsProfileSetStatus('Prévia não salva. Salve o perfil para confirmar a foto.','dirty');
  }catch(error){
    if(current()) settingsProfileSetStatus(error&&error.message||'Não foi possível preparar a foto. A anterior foi mantida.','error');
  }finally{
    if(current()){settingsProfileState.busy=false;settingsProfileState.reader=null;renderSettingsProfile();}
  }
}
async function saveSettingsProfile(){
  const state=settingsProfileState;
  if(state.blocked||state.busy||state.saving||!settingsProfileDirty()) return;
  if(!settingsProfileNameValid(state.draft.displayName)) {settingsProfileSetStatus('Use até 120 caracteres no nome, sem caracteres de controle.','error');return;}
  if(!settingsProfileAvatarValid(state.draft.avatarDataUrl)) {settingsProfileSetStatus('A foto está indisponível. Substitua ou remova a foto antes de salvar.','error');return;}
  const token=state.token,epoch=state.epoch;
  const candidate={displayName:state.draft.displayName.trim(),avatarDataUrl:state.draft.avatarDataUrl};
  const payload=JSON.stringify({...state.envelope,schemaVersion:1,...candidate});
  const current=()=>token===state.token&&epoch===settingsProfileEpoch();
  state.saving=true;renderSettingsProfile();
  const write=()=>{
    if(!current()) return;
    let before;
    try{before=localStorage.getItem(SETTINGS_PROFILE_KEY);}
    catch(error){state.blocked='read';settingsProfileSetStatus('Não foi possível conferir o perfil salvo. Nenhuma gravação foi tentada; recarregue a página.','blocked');return;}
    if(before!==state.raw){state.blocked='conflict';settingsProfileSetStatus('O perfil mudou em outra aba. Nada foi gravado; cancele para conferir o perfil atual.','blocked');return;}
    try{localStorage.setItem(SETTINGS_PROFILE_KEY,payload);}catch(error){/* A releitura determina o desfecho desta tentativa. */}
    let after;
    try{after=localStorage.getItem(SETTINGS_PROFILE_KEY);}catch(error){}
    if(after===payload){
      state.raw=payload;state.envelope=JSON.parse(payload);state.confirmed={...candidate};state.draft={...candidate};
      settingsProfileSetStatus('Perfil salvo neste navegador.','success');return;
    }
    if(after===before){settingsProfileSetStatus('Não foi possível salvar. O perfil anterior foi mantido e a prévia continua disponível para tentar novamente ou cancelar.','error');return;}
    state.blocked='unknown';
    settingsProfileSetStatus('Não foi possível confirmar a gravação. A prévia foi preservada; novas alterações estão bloqueadas. Recarregue para conferir o perfil armazenado.','blocked');
  };
  try{
    // Compartilha o lock existente com a limpeza, sem mudar seu protocolo.
    // Sem Web Locks, permanece a guarda síncrona e a limitação de concorrência
    // documentada do navegador; não se promete transação entre abas.
    if(typeof sessionAcquireWriteLock==='function') await sessionAcquireWriteLock(write);else write();
  }catch(error){if(current()) settingsProfileSetStatus('Não foi possível iniciar a gravação. A prévia foi mantida.','error');}
  finally{if(current()){state.saving=false;renderSettingsProfile();}}
}
function settingsProfileStorageChanged(event){
  if(event.key!==SETTINGS_PROFILE_KEY) return;
  const state=settingsProfileState;
  settingsProfileCancelAsync();
  if(event.newValue===null){
    // Outra aba removeu o perfil: descartar a cópia pessoal em memória também.
    settingsProfileReload();return;
  }
  if(state.blocked==='unknown') return;
  if(settingsProfileDirty()){
    state.blocked='conflict';settingsProfileSetStatus('O perfil mudou em outra aba. Cancele a prévia para conferir o perfil atual.','blocked');renderSettingsProfile();
  }else settingsProfileReload();
}
function handleSettingsProfileSessionWipe(){
  settingsProfileCancelAsync();
  Object.assign(settingsProfileState,{confirmed:{displayName:'',avatarDataUrl:null},draft:{displayName:'',avatarDataUrl:null},raw:null,envelope:{},
    blocked:'session',note:'O encerramento invalidou a edição do perfil nesta sessão. Recarregue para conferir o perfil salvo antes de continuar.',status:'blocked',editing:false,saving:false,epoch:settingsProfileEpoch()});
  const file=settingsEl('settingsProfilePhotoInput');if(file) file.value='';
  renderSettingsProfile();
}
function bindSettingsProfileEditor(){
  const form=settingsEl('settingsProfileForm');if(!form||form.dataset.bound) return;
  form.dataset.bound='true';
  form.addEventListener('submit',event=>{event.preventDefault();saveSettingsProfile();});
  settingsEl('settingsProfileNameInput').addEventListener('input',event=>{
    settingsProfileState.draft.displayName=event.target.value;settingsProfileState.editing=true;
    settingsProfileSetStatus(settingsProfileNameValid(event.target.value)?'Prévia não salva. Salve o perfil para confirmar o nome.':'Use até 120 caracteres no nome, sem caracteres de controle.',settingsProfileNameValid(event.target.value)?'dirty':'error');renderSettingsProfile();
  });
  settingsEl('settingsProfileChoosePhotoBtn').addEventListener('click',()=>settingsEl('settingsProfilePhotoInput').click());
  settingsEl('settingsProfileAvatarSearch').addEventListener('input',renderSettingsProfileGallery);
  settingsEl('settingsProfileAvatarSearch').addEventListener('keydown',event=>{
    // Buscar dentro do formulário não é uma confirmação do rascunho.
    if(event.key==='Enter') event.preventDefault();
  });
  settingsEl('settingsProfileAvatarGroup').addEventListener('change',renderSettingsProfileGallery);
  settingsEl('settingsProfileGallery').addEventListener('click',event=>{
    const choice=event.target.closest('[data-profile-avatar]');
    if(choice) selectSettingsProfileAvatar(choice.dataset.profileAvatar);
  });
  settingsEl('settingsProfilePhotoInput').addEventListener('change',event=>{
    const file=event.target.files&&event.target.files[0];event.target.value='';selectSettingsProfilePhoto(file);
  });
  settingsEl('settingsProfileRemovePhotoBtn').addEventListener('click',()=>{
    settingsProfileCancelAsync();settingsProfileState.draft.avatarDataUrl=null;settingsProfileState.editing=true;
    settingsProfileSetStatus('Prévia sem foto. Salve o perfil para confirmar a remoção.','dirty');renderSettingsProfile();
  });
  settingsEl('settingsProfileCancelBtn').addEventListener('click',()=>{cancelSettingsProfileDraft();settingsProfileState.editing=true;});
  renderSettingsProfile();
}
function settingsIsOpen(){ return settingsState.open; }
function settingsEsc(v){ return esc(String(v||'')); }
function settingsLeafLabel(id){ return (SETTINGS_LEAVES[id]&&SETTINGS_LEAVES[id].label) || (SETTINGS_GROUP_BY_ID[id]&&SETTINGS_GROUP_BY_ID[id].label) || id; }
function settingsPageTitleFor(id){
  if(id==='general') return 'Geral';
  if(SETTINGS_GROUP_BY_ID[id]) return SETTINGS_GROUP_BY_ID[id].label;
  return settingsLeafLabel(id);
}
function settingsTopLevelFor(id){
  if(id==='account') return 'account';
  if(id==='general'||id==='about'||SETTINGS_GROUP_BY_ID[id]) return id;
  const leaf=SETTINGS_LEAVES[id];
  return leaf?leaf.group:'general';
}

function buildSettingsMenu(){
  const menu=settingsEl('settingsMenu'), select=settingsEl('settingsMobileCategory');
  if(!menu||menu.dataset.ready) return;
  SETTINGS_GROUPS.forEach(item=>{
    const button=document.createElement('button');
    button.type='button'; button.className='settings-menu-item'; button.dataset.settingsCategory=item.id;
    button.setAttribute('aria-current','false');
    button.innerHTML=`<span class="settings-menu-symbol" data-settings-color="${item.icon}">${settingsIconSvg(item.icon)}</span><span>${settingsEsc(item.label)}</span>`;
    button.addEventListener('click',()=>settingsNavigateTopLevel(item.id));
    menu.append(button);
    const option=document.createElement('option'); option.value=item.id; option.textContent=item.label; select.append(option);
  });
  select.addEventListener('change',()=>settingsNavigateTopLevel(select.value));
  // Calendário Econômico — AÇÃO de nível superior, não categoria: abre o
  // diálogo compartilhado (17-economic-calendar.js) em um passo, como o
  // requisito pede ("Configurações → Calendário Econômico"). Sem
  // data-settings-category de propósito: não é página navegável, não entra na
  // pilha de navegação nem no <select> mobile (cujo change navega categorias),
  // e a contagem de categorias do contrato de testes permanece intacta. O
  // clique é tratado por delegação em 17-economic-calendar.js (mesmo id que
  // marca o lançador do subdiálogo); aqui só se constrói a linha.
  const launch=document.createElement('button');
  launch.type='button'; launch.id='ecalOpenFromSettingsBtn';
  launch.className='settings-menu-item settings-menu-launch';
  launch.setAttribute('aria-haspopup','dialog');
  launch.innerHTML=`<span class="settings-menu-symbol" data-settings-color="calendar">${settingsIconSvg('calendar')}</span><span>Calendário Econômico</span>`;
  menu.append(launch);
  menu.dataset.ready='true';
}

function settingsCategoryHero(id,description){
  const item=SETTINGS_GROUP_BY_ID[id]||SETTINGS_LEAVES[id]||{};
  const icon=item.icon||(SETTINGS_GROUP_BY_ID[item.group]||{}).icon||(id==='account'?'account':'general');
  const desc=description||item.desc||(id==='general'?'Escolha como o JP Wealth funciona, protege seus dados e organiza suas preferências.':'Informações sobre o aplicativo e suas referências.');
  if(id==='account') return '<div class="settings-category-hero settings-account-hero" data-settings-hero="account"><span class="settings-profile-avatar settings-account-avatar" id="settingsAccountAvatar" aria-hidden="true">JP</span><h4 class="settings-hero-title" id="settingsAccountHeading">Seu perfil</h4><p class="settings-account-label">JP Wealth Account</p><p class="settings-hero-description">Personalize sua identidade neste navegador.</p></div>';
  return `<div class="settings-category-hero" data-settings-hero="${settingsEsc(id)}"><span class="settings-hero-icon" data-settings-color="${settingsEsc(icon)}" aria-hidden="true">${settingsIconSvg(icon)}</span><h4 class="settings-hero-title">${settingsEsc(settingsPageTitleFor(id))}</h4><p class="settings-hero-description">${settingsEsc(desc)}</p></div>`;
}
function createSettingsPanel(id,html){
  const panel=document.createElement('section'); panel.className='settings-panel'; panel.dataset.settingsPanel=id; panel.hidden=true; panel.innerHTML=html;
  // O texto introdutório original passa ao hero; os controles e avisos restantes
  // conservam os mesmos nós, IDs, listeners e semântica.
  const lead=panel.firstElementChild?.matches('p.settings-lead')?panel.firstElementChild:null;
  const description=lead?.textContent; if(lead) lead.remove();
  panel.insertAdjacentHTML('afterbegin',settingsCategoryHero(id,description));
  settingsEl('settingsContent').append(panel); return panel;
}

function aboutPanel(){
  const build=typeof JP_WEALTH_BUILD_ID==='string'?JP_WEALTH_BUILD_ID:'não informado';
  return `<p class="settings-lead">Ferramenta de gestão, registro e controle de risco. O sistema não fornece sinais, não prevê resultados e não transforma expectativas estatísticas em garantias.</p><dl class="settings-facts"><dt>Aplicativo</dt><dd>JP Wealth Risk Terminal</dd><dt>Versão</dt><dd>1 beta</dd><dt>Build</dt><dd><code>${settingsEsc(build)}</code></dd><dt>Armazenamento</dt><dd>Local neste navegador.</dd><dt>Funcionamento</dt><dd>Disponível offline após a instalação completa da aplicação.</dd></dl><div class="settings-links"><a href="docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf" target="_blank" rel="noopener">Estatuto V11.0 (PDF)</a><a href="docs/normative/ANEXO_PARAMETRICO_CANONICO.md" target="_blank" rel="noopener">Anexo Paramétrico Canônico</a><a href="CHANGELOG.md" target="_blank" rel="noopener">Changelog</a><a href="README.md" target="_blank" rel="noopener">Documentação do projeto</a></div><p class="note">Dados técnicos não disponíveis no código vigente não são inferidos nesta tela.</p>`;
}

function educationPanel(){
  const groups=[['comece','Começar por aqui'],['fundamentos','Fundamentos do Forex'],['estrutura','Estrutura do mercado'],['pares','Pares e cotações'],['execucao','Execução e custos'],['risco','Risco e alavancagem'],['historia','História do mercado cambial']];
  return `<p class="settings-lead">Referência local, curta e curada. Não substitui o Estatuto Operacional nem os Parâmetros e Calibração.</p>${groups.map(([key,label])=>`<section class="education-section"><h4>${label}</h4>${EDUCATIONAL_CONTENT.filter(x=>x.category===key).map(educationArticle).join('')}</section>`).join('')}<section class="education-section"><h4>Glossário</h4><div class="education-glossary">${EDUCATIONAL_GLOSSARY.map(term=>`<button type="button" data-education-term="${settingsEsc(term)}">${settingsEsc(term)}</button>`).join('')}</div></section><section class="education-section"><h4>Perguntas frequentes</h4>${EDUCATIONAL_FAQ.map(([q,a],i)=>`<details id="education-faq-${i}"><summary>${settingsEsc(q)}</summary><p>${settingsEsc(a)}</p></details>`).join('')}</section>`;
}
function educationArticle(item){ return `<article class="education-article" id="education-${item.id}" data-education-id="${item.id}"><h5>${settingsEsc(item.title)}</h5><p><b>Definição.</b> ${settingsEsc(item.definition)}</p><p><b>Exemplo simples.</b> ${settingsEsc(item.example)}</p><p><b>Risco ou limitação.</b> ${settingsEsc(item.risk)}</p><p><b>Relação com o JP Wealth.</b> ${settingsEsc(item.jpWealth)}</p></article>`; }

function settingsStorageFacts(){
  const facts=[];
  facts.push(['Tipo de armazenamento','localStorage neste navegador']);
  let readState='Nenhum dado salvo ainda neste navegador';
  try{
    const raw=localStorage.getItem('jpwealth_v9_state');
    if(raw){ JSON.parse(raw); readState='Dado salvo é legível e está em formato JSON válido'; }
  }catch(e){ readState='Dado salvo existe, mas não está em formato JSON válido'; }
  facts.push(['Leitura do estado salvo',readState]);
  if(typeof S!=='undefined'&&S&&Array.isArray(S.accounts)) facts.push(['Contas configuradas',String(S.accounts.length)]);
  const offline=(typeof navigator!=='undefined'&&'serviceWorker' in navigator&&navigator.serviceWorker.controller)?'Ativo neste carregamento':'Não confirmado nesta sessão';
  facts.push(['Funcionamento offline',offline]);
  return facts;
}
function storagePanel(){
  const rows=settingsStorageFacts().map(([k,v])=>`<dt>${settingsEsc(k)}</dt><dd>${settingsEsc(v)}</dd>`).join('');
  return `<p class="settings-lead">Informações que o próprio aplicativo consegue verificar sobre os dados salvos neste navegador. Nenhum valor operacional é exibido aqui.</p><dl class="settings-facts">${rows}</dl><p class="note">Se pouca informação estiver disponível, é porque o sistema não a mede — nenhum dado é inventado nesta tela.</p>`;
}

function settingsNavCard(id,label,desc){
  return `<button type="button" class="settings-nav-card" data-nav-to="${settingsEsc(id)}"><span class="cp-settings-symbol" aria-hidden="true">${settingsIconSvg((SETTINGS_GROUP_BY_ID[id]||SETTINGS_GROUP_BY_ID[settingsTopLevelFor(id)]||{}).icon||'general')}</span><span class="settings-nav-card-text"><span class="settings-nav-card-title">${settingsEsc(label)}</span>${desc?`<span class="settings-nav-card-desc">${settingsEsc(desc)}</span>`:''}</span><span class="settings-nav-card-chev" aria-hidden="true">${settingsIconSvg('chevron')}</span></button>`;
}
function generalPanel(){
  const card=id=>{const g=SETTINGS_GROUP_BY_ID[id];return settingsNavCard(g.id,g.label,'');};
  return `<div class="cp-settings-collections"><section><h4>Preferências e dados</h4><div class="settings-nav-list">${card('appearance-interface')}${card('data-security')}</div></section><section><h4>Método e apoio</h4><div class="settings-nav-list">${card('method-governance')}${card('operations')}${card('knowledge')}</div></section></div>`;
}
function groupPanel(group){
  const cards=group.children.map(leafId=>settingsNavCard(leafId,SETTINGS_LEAVES[leafId].label,SETTINGS_LEAVES[leafId].desc)).join('');
  return `<p class="settings-lead">${settingsEsc(group.desc||'')}</p><div class="settings-nav-list">${cards}</div>`;
}

function buildSettingsContent(){
  const content=settingsEl('settingsContent'); if(!content||content.dataset.ready) return;
  createSettingsPanel('general',generalPanel());
  createSettingsPanel('account',settingsAccountPanel());
  SETTINGS_GROUPS.filter(g=>g.children).forEach(g=>createSettingsPanel(g.id,groupPanel(g)));
  createSettingsPanel('about',aboutPanel());
  createSettingsPanel('appearance','<p class="settings-lead">Escolha o tema e a aparência de leitura para este navegador.</p><div data-settings-slot="appearance"></div>');
  createSettingsPanel('interface','<p class="settings-lead">Organização, legibilidade e ajuda contextual. Preferências existentes são preservadas.</p><div class="settings-rail-row"><div><h4>Barra lateral</h4><p class="note">Escolha se a barra de navegação permanece expandida ou recolhida neste navegador.</p></div><div id="settingsRailSlot"></div></div><div data-settings-slot="interface"></div>');
  createSettingsPanel('editor','<p class="settings-lead">Preferências de edição e de apresentação da interface neste navegador.</p><div data-settings-slot="editor"></div>');
  createSettingsPanel('educational',educationPanel());
  createSettingsPanel('statute','<p class="settings-lead">Consulte o Estatuto V11.0 e o Anexo JPW-ANNEX-T03. O motor financeiro legado ainda não foi adaptado; esta referência documental não homologa seus cálculos.</p><p class="settings-links"><a href="docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf" target="_blank" rel="noopener">Estatuto V11.0 (PDF)</a><a href="docs/normative/ANEXO_PARAMETRICO_CANONICO.md" target="_blank" rel="noopener">Anexo Paramétrico Canônico</a></p><div data-settings-slot="statute"></div>');
  createSettingsPanel('parameters','<p class="settings-lead">Controles existentes, com os valores, unidades, validações e persistência originais.</p><section class="settings-safe-period" id="settingsPeriodSummary"><h4>Período Operacional</h4><p>Os dados do período são mantidos pelo questionário de início. Esta central não mostra valores pessoais ou credenciais.</p><button type="button" class="reset-btn" id="settingsReviewPeriodBtn">Revisar dados do período</button></section><div data-settings-slot="period"></div><div data-settings-slot="parameters"></div>');
  createSettingsPanel('tool-params','<p class="settings-lead">Motor Forex versionado. Registros explícitos, parâmetros normativos e estados de elegibilidade são apresentados separadamente.</p><div data-settings-slot="tool-params"></div>');
  createSettingsPanel('tool-check','<p class="settings-lead">Respostas, pontuação e critérios do checklist pré-trade. As respostas são gravadas durante o preenchimento.</p><button type="button" id="settingsOpenChecklist" aria-haspopup="dialog" aria-controls="forexChecklistDialog">Abrir checklist pré-trade</button>');
  settingsEl('settingsOpenChecklist')?.addEventListener('click',event=>fxOpenChecklist(event.currentTarget));
  createSettingsPanel('backup','<p class="settings-lead">O backup completo guarda seus dados, perfil com foto, preferências e rascunhos para revisão. Após importar, recarregue para aplicar toda a aparência. Senhas de investidor não são incluídas.</p><div data-settings-slot="backup"></div>');
  createSettingsPanel('storage',storagePanel());
  createSettingsPanel('forex-consolidated',window.JPWFXConsolidated?.settingsMarkup?window.JPWFXConsolidated.settingsMarkup():'<p>Consolidado indisponível neste carregamento.</p>');
  content.addEventListener('click',settingsContentClick,true);
  content.dataset.ready='true';
  bindSettingsProfileEditor();
}

function settingsContentClick(event){
  const navCard=event.target.closest('[data-nav-to]');
  if(navCard){ settingsNavigate(navCard.dataset.navTo,{push:true,focus:true}); return; }
  const review=event.target.closest('#settingsReviewPeriodBtn');
  if(review){ settingsMarkSubdialogLauncher(review); openOnboardingModal('edit'); return; }
  const launch=event.target.closest('#chooseAppIconBtn, #importFullBackupBtn, #wipeAllBtn');
  if(launch) settingsMarkSubdialogLauncher(launch);
  const term=event.target.closest('[data-education-term]');
  if(term){ const item=EDUCATIONAL_CONTENT.find(x=>x.title.toLowerCase()===term.dataset.educationTerm.toLowerCase()||x.keywords.some(k=>k.toLowerCase()===term.dataset.educationTerm.toLowerCase())); if(item) settingsRevealElement(`education-${item.id}`); }
}

// A busca permanece na sidebar. Transportar os nós reais também preserva
// sessões cujo shell ainda contenha o slot anterior; não cria cópia nem listener.
function moveSettingsSearchToSidebar(){
  const slot=settingsEl('settingsSidebarSearchSlot'), input=settingsEl('settingsSearch');
  if(!slot||!input||input.parentElement===slot) return;
  const label=document.querySelector('label.settings-search-label[for="settingsSearch"]');
  if(label){ label.classList.add('sr-only'); slot.append(label); }
  slot.append(input);
  const results=settingsEl('settingsSearchResults');
  if(results) slot.append(results);
}

// Telas operacionais que migraram da navegação superior para o grupo
// "Operação": o grid inteiro de cada tela é transportado (nunca clonado —
// IDs, listeners e estado interno preservados) para o slot do painel
// enquanto a central está aberta, e devolvido à <section> hospedeira ao
// fechar — exatamente o contrato dos nós legados do #config.
const SETTINGS_SCREEN_GRIDS={
  'tool-params':{grid:'paramsWidgetGrid',host:'params'}
};
function moveLegacySettingsNodes(){
  const host=settingsEl('config'); if(!host) return;
  if(!settingsState.legacyNodes.length) settingsState.legacyNodes=[...host.children].filter(node=>node.matches('[data-settings-category]'));
  settingsState.legacyNodes.forEach(node=>{
    const category=node.dataset.settingsCategory, slot=settingsEl('settingsContent').querySelector(`[data-settings-slot="${category}"]`);
    if(slot) slot.append(node);
  });
  Object.entries(SETTINGS_SCREEN_GRIDS).forEach(([leafId,cfg])=>{
    const grid=settingsEl(cfg.grid), slot=settingsEl('settingsContent').querySelector(`[data-settings-slot="${leafId}"]`);
    if(grid&&slot&&grid.parentElement!==slot) slot.append(grid);
  });
  const rail=settingsEl('railToggle');
  if(rail&&rail.parentElement!==settingsEl('settingsRailSlot')){ settingsState.railParent=rail.parentElement; settingsState.railNext=rail.nextSibling; settingsEl('settingsRailSlot').append(rail); }
}
function restoreLegacySettingsNodes(){
  const host=settingsEl('config'); if(!host) return;
  settingsState.legacyNodes.forEach(node=>host.append(node));
  Object.values(SETTINGS_SCREEN_GRIDS).forEach(cfg=>{
    const grid=settingsEl(cfg.grid), screenHost=settingsEl(cfg.host);
    if(grid&&screenHost&&grid.parentElement!==screenHost) screenHost.append(grid);
  });
  const rail=settingsEl('railToggle');
  if(rail&&settingsState.railParent){ settingsState.railParent.insertBefore(rail,settingsState.railNext); }
}

// Primitiva de baixo nível preservada: torna o painel 'id' visível, esconde os demais.
// Mantida com este nome e assinatura para compatibilidade com chamadas diretas existentes.
function activateSettingsCategory(id,options={}){
  if(settingsRedirectResearchLab(id)) return;
  const exists=document.querySelector(`[data-settings-panel="${id}"]`);
  const targetId=exists?id:'general';
  if(targetId==='forex-consolidated'&&window.JPWFXConsolidated?.bindSettings)window.JPWFXConsolidated.bindSettings();
  if(settingsState.active==='account'&&targetId!=='account') cancelSettingsProfileDraft();
  if(targetId==='account'&&settingsState.active!=='account') beginSettingsProfileDraft();
  if(settingsState.active==='editor'&&targetId!=='editor'&&typeof cancelNavOrderPreview==='function') cancelNavOrderPreview();
  if(targetId==='editor'&&typeof beginNavOrderPreview==='function') beginNavOrderPreview();
  if(settingsState.active==='interface'&&targetId!=='interface'&&typeof mvpNotesCancelAppearance==='function')mvpNotesCancelAppearance();
  if(targetId==='interface'&&typeof mvpNotesBeginAppearance==='function')mvpNotesBeginAppearance();
  settingsState.active=targetId;
  document.querySelectorAll('[data-settings-panel]').forEach(panel=>panel.hidden=panel.dataset.settingsPanel!==targetId);
  const select=settingsEl('settingsMobileCategory'); if(select) select.value=settingsTopLevelFor(targetId);
  settingsUpdateSidebarActive(targetId);
  settingsUpdatePageHeader(targetId);
  if(targetId==='backup' && typeof renderDgStorageCard==='function') renderDgStorageCard();
  if(options.focus) settingsEl('settingsContent').focus({preventScroll:true});
}

function settingsUpdateSidebarActive(id){
  const topId=settingsTopLevelFor(id);
  document.querySelectorAll('#settingsMenu [data-settings-category]').forEach(button=>{
    const on=button.dataset.settingsCategory===topId; button.classList.toggle('active',on); button.setAttribute('aria-current',on?'page':'false');
  });
  const profile=settingsEl('settingsProfileBtn');
  if(profile){ profile.classList.toggle('active',id==='account'); profile.setAttribute('aria-current',id==='account'?'page':'false'); }
}
function settingsUpdatePageHeader(id){
  const titleEl=settingsEl('settingsPageTitle'); if(titleEl) titleEl.textContent=settingsPageTitleFor(id);
  const backBtn=settingsEl('settingsBackBtn'), fwdBtn=settingsEl('settingsForwardBtn');
  if(backBtn) backBtn.disabled=settingsState.navIndex<=0;
  if(fwdBtn) fwdBtn.disabled=settingsState.navIndex>=settingsState.navStack.length-1;
}

// Navegação de alto nível: gerencia pilha de histórico interno, visão mobile e cabeçalho da página.
// Não usa history.pushState nem altera a URL — todo o estado é interno ao modal.
function settingsRenderCurrent(options={}){
  const id=settingsState.navStack[settingsState.navIndex];
  const modal=settingsEl('settingsModal');
  if(modal) modal.classList.toggle('settings-mobile-detail',!settingsState.mobileListVisible);
  activateSettingsCategory(id,{focus:options.focus});
  if(id==='tool-params'&&window.JPWForex&&JPWForex.ui)JPWForex.ui.render();
}
function settingsNavigate(id,options={}){
  if(settingsRedirectResearchLab(id)) return;
  const push=options.push!==false;
  if(push){
    if(settingsState.navStack[settingsState.navIndex]!==id){
      settingsState.navStack=settingsState.navStack.slice(0,settingsState.navIndex+1);
      settingsState.navStack.push(id);
      settingsState.navIndex=settingsState.navStack.length-1;
    }
  }else{
    settingsState.navStack[settingsState.navIndex]=id;
  }
  settingsState.mobileListVisible=false;
  settingsRenderCurrent({focus:options.focus});
  if(options.reveal) settingsRevealElement(options.reveal);
  if(settingsState.active==='tool-check') fxOpenChecklist(settingsEl('settingsOpenChecklist'));
}
function settingsNavigateTopLevel(id){
  settingsState.mobileListVisible=false;
  settingsNavigate(id,{push:true,focus:true});
}
function settingsGoBack(){
  if(settingsState.navIndex>0){
    settingsState.navIndex--;
    if(settingsState.navIndex===0){
      // topo da pilha: no mobile, voltar ao topo significa voltar à lista de categorias,
      // não exibir a página 'general' em tela cheia (a lista é o ponto de partida real).
      settingsState.mobileListVisible=true;
      const modal=settingsEl('settingsModal'); if(modal) modal.classList.remove('settings-mobile-detail');
      settingsRenderCurrent({focus:false});
      settingsEl('settingsSearch').focus({preventScroll:true});
      return;
    }
    settingsRenderCurrent({focus:true}); return;
  }
  if(!settingsState.mobileListVisible){ settingsState.mobileListVisible=true; const modal=settingsEl('settingsModal'); if(modal) modal.classList.remove('settings-mobile-detail'); settingsEl('settingsSearch').focus({preventScroll:true}); }
}
function settingsGoForward(){
  if(settingsState.navIndex<settingsState.navStack.length-1){ settingsState.navIndex++; settingsState.mobileListVisible=false; settingsRenderCurrent({focus:true}); }
}
function settingsNavigateToLeaf(leafId,options={}){
  if(settingsRedirectResearchLab(leafId)) return;
  const leaf=SETTINGS_LEAVES[leafId];
  settingsState.navStack=['general'];
  if(leaf&&leaf.group) settingsState.navStack.push(leaf.group);
  settingsState.navStack.push(leafId);
  settingsState.navIndex=settingsState.navStack.length-1;
  settingsState.mobileListVisible=false;
  settingsRenderCurrent({focus:options.focus});
  if(options.reveal) settingsRevealElement(options.reveal);
  if(settingsState.active==='tool-check') fxOpenChecklist(settingsEl('settingsOpenChecklist'));
}

function settingsSearchEntries(){
  const core=Object.entries(SETTINGS_LEAVES).flatMap(([id,leaf])=>[...leaf.terms,leaf.label].map(term=>({title:term,category:id})));
  const controls=[['Tema visual','appearance','#themeSeg'],['Marca do JP Wealth','appearance','#appIconConfig'],['Marca PWA','appearance','#appIconConfig'],['Ícone do app','appearance','#appIconConfig'],['Escala da fonte','interface','#fsSeg'],['Sidebar','interface','#settingsRailSlot'],['Ajuda contextual','interface','#explSeg'],['Estilo da navegação','editor','#navStyleSeg'],['Barra em pílula','editor','#navStyleSeg'],['MDD máximo','parameters','#pMDD'],['Ordem Gênese','parameters','#pGenLev'],['Período operacional','parameters','#settingsPeriodSummary'],['Exportar base completa','backup','#exportFullBackupBtn'],['Importar backup','backup','#importFullBackupBtn'],
    // Governança de armazenamento (JPW-HJFGDE) — cartão único, vários termos de entrada.
    ['Armazenamento da Base','backup','#dgStorageCard'],['Pasta padrão de exportação','backup','#dgStorageCard'],
    ['Confirmar backup','backup','#dgStorageCard'],['Reautorizar pasta','backup','#dgStorageCard'],
    // Notas do MVP (14-mvp-notes.js) — vários termos apontando para o mesmo card,
    // mesmo padrão de 'core' (multi-termo por entrada), já que aqui cada entrada só
    // casa com o próprio título.
    ['Tickets','interface','#mvpNotesSettingsCard'],['tickets','interface','#mvpNotesSettingsCard'],
    ['Notas do MVP','interface','#mvpNotesSettingsCard'],['notas','interface','#mvpNotesSettingsCard'],
    ['Aparência de Notas','interface','#mvpNotesSettingsCard'],['Densidade das notas','interface','#mvpNotesSettingsCard'],['Texto do editor de Notas','interface','#mvpNotesSettingsCard'],['Largura das notas','interface','#mvpNotesSettingsCard'],
    ['Bloco de notas','interface','#mvpNotesSettingsCard'],['Botão flutuante','interface','#mvpNotesSettingsCard'],['Mover notas','interface','#mvpNotesSettingsCard'],['Posição das notas','interface','#mvpNotesSettingsCard'],['Restaurar posição','interface','#mvpNotesSettingsCard'],
    ['tarefas','interface','#mvpNotesSettingsCard'],['bugs','interface','#mvpNotesSettingsCard'],
    ['funcionalidades','interface','#mvpNotesSettingsCard'],['melhorias','interface','#mvpNotesSettingsCard'],
    ['MVP','interface','#mvpNotesSettingsCard'],['ícone menu superior','interface','#mvpNotesSettingsCard'],
    ['backlog','interface','#mvpNotesSettingsCard']
  ].map(([title,category,selector])=>({title,category,selector}));
  const education=EDUCATIONAL_CONTENT.flatMap(item=>[item.title,...item.keywords].map(term=>({title:term,category:'educational',selector:`#education-${item.id}`})));
  return [...core,...controls,...education];
}
function settingsResultPath(category){
  const leaf=SETTINGS_LEAVES[category];
  if(!leaf) return settingsPageTitleFor(category);
  const group=leaf.group?SETTINGS_GROUP_BY_ID[leaf.group]:null;
  return group?`${group.label} › ${leaf.label}`:leaf.label;
}
function settingsSelectSearchResults(entries,query){
  const seen=new Set();
  return entries
    .filter(item=>`${item.title} ${item.path}`.toLocaleLowerCase('pt-BR').includes(query))
    .filter(item=>{
      const key=`${item.title}|${item.path}`;
      if(seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .sort((a,b)=>(b.selector?1:0)-(a.selector?1:0))
    .slice(0,18);
}
function renderSettingsSearch(){
  const root=settingsEl('settingsSearchResults'), query=settingsState.query.trim().toLocaleLowerCase('pt-BR'); if(!root) return;
  if(!query){ root.replaceChildren(); return; }
  const entries=settingsSearchEntries().map(item=>({...item,path:settingsResultPath(item.category)}));
  const results=settingsSelectSearchResults(entries,query);
  root.innerHTML=results.length?results.map((item,i)=>`<button type="button" data-settings-result="${i}"><b>${settingsEsc(item.title)}</b><span>${settingsEsc(item.path)}</span></button>`).join(''):'<p class="settings-no-results">Nenhuma configuração ou ajuda encontrada.</p>';
  root.querySelectorAll('[data-settings-result]').forEach((button,i)=>button.addEventListener('click',()=>{
    const item=results[i];
    settingsNavigateToLeaf(item.category,{focus:false,reveal:item.selector});
    root.replaceChildren();
    // A folha já está visível, inclusive no celular; a busca conserva o texto.
    if(settingsState.open&&!settingsState.suspended) settingsEl('settingsContent').focus({preventScroll:true});
  }));
}
function settingsRevealElement(selector){
  if(!selector) return;
  requestAnimationFrame(()=>{ const target=document.querySelector(selector); if(!target) return; target.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}); target.classList.add('settings-search-hit'); clearTimeout(settingsState.highlightTimer); settingsState.highlightTimer=setTimeout(()=>target.classList.remove('settings-search-hit'),2200); if(target.matches('details')) target.open=true; });
}

// A-003: os seletores antigos .topbar e #main não existem no DOM (os elementos reais são
// <header> e #appMain) — com a Central aberta, todo o cabeçalho e o conteúdo operacional
// da tela ativa permaneciam expostos à árvore de acessibilidade apesar do aria-modal.
// Corrigido com o mesmo padrão captura-e-restaura do drawer de Notas (mvpNotesApplyInert):
// nunca um clear cego — outro mecanismo pode ter posto inert/aria-hidden próprios nesses
// nós, e o fechamento restaura exatamente os valores capturados na abertura.
// document.querySelector('header') resolve para o <header> de topo do app (primeiro na
// ordem do documento); os <header> internos de modais/drawers vêm todos depois.
let settingsInertSnapshot=null;
function settingsInertTargets(){
  return [document.querySelector('header'),document.querySelector('#nav'),document.querySelector('#navSubShell'),document.querySelector('#appMain'),document.querySelector('.foot-note'),document.querySelector('#mvpNotesLauncher')].filter(Boolean);
}
function settingsSetAppInert(on){
  if(on){
    if(settingsInertSnapshot) return; // já aplicado — reaplicar sobrescreveria a captura original
    settingsInertSnapshot=settingsInertTargets().map(el=>({el, inert:el.inert, ariaHidden:el.getAttribute('aria-hidden')}));
    settingsInertSnapshot.forEach(({el})=>{ el.inert=true; el.setAttribute('aria-hidden','true'); });
  }else{
    const snapshot=settingsInertSnapshot; if(!snapshot) return;
    snapshot.forEach(({el,inert,ariaHidden})=>{
      el.inert=inert;
      if(ariaHidden===null) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden',ariaHidden);
    });
    settingsInertSnapshot=null;
    // O Editor pode ter movido a navegação entre o header e a lateral.
    if(typeof syncShellViewport==='function'&&document.getElementById('appSidebar')?.dataset.ready)syncShellViewport();
  }
}
// Compatibilidade de chamadas antigas: o destino passa a Research, sem painel
// oculto de Configurações nem restauração assíncrona do foco para o modal fechado.
function settingsRedirectResearchLab(id){
  if(id!=='probability-lab'&&id!=='galton-board') return false;
  if(!window.JPWNavigation) return true;
  if(settingsState.open) closeSettingsModal({restoreFocus:false});
  if(window.JPWNavigation.navigate('research-probability-lab')) window.JPWNavigation.focusCurrentScreen();
  return true;
}
function openSettingsModal(category='general', opener){
  if(settingsRedirectResearchLab(category)) return;
  if(typeof researchSetCovered==='function') researchSetCovered(true);
  buildSettingsMenu(); buildSettingsContent(); settingsState.opener=opener||document.activeElement||settingsEl('headerConfigBtn'); settingsState.open=true; settingsState.suspended=false;
  settingsState.navStack=['general']; settingsState.navIndex=0; settingsState.mobileListVisible=true;
  moveLegacySettingsNodes(); settingsEl('settingsOverlay').classList.add('show'); settingsEl('settingsOverlay').setAttribute('aria-hidden','false'); settingsSetAppInert(true);
  if(category&&category!=='general') settingsNavigate(category,{push:true,focus:false});
  else settingsRenderCurrent({focus:false});
  window.__settingsModalDebug.opens++;
  requestAnimationFrame(()=>{
    if(!settingsState.open||settingsState.suspended) return;
    const search=settingsEl('settingsSearch');
    (search&&search.getClientRects().length?search:settingsEl('settingsContent')).focus({preventScroll:true});
  });
}
function closeSettingsModal(options={}){
  if(!settingsState.open||settingsState.suspended) return;
  if(typeof cancelNavOrderPreview==='function') cancelNavOrderPreview();
  cancelSettingsProfileDraft();
  if(window.JPWForex&&JPWForex.state)JPWForex.state.lockEditor();
  if(typeof mvpNotesCancelAppearance==='function')mvpNotesCancelAppearance();
  settingsState.open=false; settingsEl('settingsOverlay').classList.remove('show'); settingsEl('settingsOverlay').setAttribute('aria-hidden','true'); settingsSetAppInert(false); restoreLegacySettingsNodes();
  if(typeof researchSetCovered==='function') researchSetCovered(false);
  const opener=settingsState.opener; settingsState.opener=null; if(options.restoreFocus!==false&&opener&&document.contains(opener)) requestAnimationFrame(()=>opener.focus());
}
function settingsMarkSubdialogLauncher(element){ settingsState.subdialogLauncher=element; }
function suspendSettingsForSubdialog(){
  if(!settingsState.open||settingsState.suspended) return; settingsState.suspended=true; settingsEl('settingsModal').inert=true; settingsEl('settingsModal').setAttribute('aria-hidden','true'); window.__settingsModalDebug.focusTrapActive=false;
}
function restoreSettingsAfterSubdialog(){
  if(!settingsState.open||!settingsState.suspended) return; settingsState.suspended=false; settingsEl('settingsModal').inert=false; settingsEl('settingsModal').removeAttribute('aria-hidden'); const target=settingsState.subdialogLauncher; settingsState.subdialogLauncher=null; if(target&&document.contains(target)) requestAnimationFrame(()=>target.focus());
}
function settingsFocusables(root){ return [...root.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])')].filter(el=>!el.closest('[hidden]')&&!el.closest('[inert]')&&el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden'); }
function settingsTrapFocus(event){
  if(!settingsState.open||settingsState.suspended||settingsEl('modalOverlay').classList.contains('show')||event.key!=='Tab') return; const list=settingsFocusables(settingsEl('settingsModal')); if(!list.length) return; window.__settingsModalDebug.focusTrapActive=true; const first=list[0],last=list[list.length-1]; if(event.shiftKey&&document.activeElement===first){ event.preventDefault(); last.focus(); } else if(!event.shiftKey&&document.activeElement===last){ event.preventDefault(); first.focus(); }
}
function initSettingsSubdialogObserver(){
  const overlay=settingsEl('modalOverlay'); if(!overlay||settingsState.observer) return;
  settingsState.observer=new MutationObserver(records=>{
    // A mesma instância também coordena o jogo coberto por Notas/gaveta móvel.
    // O focus trap legado continua reagindo apenas ao overlay que já observava.
    if(typeof researchSetCovered==='function') researchSetCovered(false);
    if(!settingsState.open||!records.some(record=>record.target===overlay)) return;
    if(overlay.classList.contains('show')) suspendSettingsForSubdialog(); else restoreSettingsAfterSubdialog();
  });
  settingsState.observer.observe(overlay,{attributes:true,attributeFilter:['class']});
  const appMain=settingsEl('appMain'); if(appMain) settingsState.observer.observe(appMain,{attributes:true,attributeFilter:['inert']});
  window.__settingsModalDebug.observerInstances++;
}

function initSettingsModal(){
  const gear=settingsEl('headerConfigBtn'); if(!gear) return;
  moveSettingsSearchToSidebar();
  settingsProfileReload();
  settingsEl('settingsProfileBtn')?.addEventListener('click',()=>settingsNavigate('account',{push:true,focus:true}));
  window.addEventListener('storage',settingsProfileStorageChanged);
  gear.addEventListener('click',()=>openSettingsModal('general',gear));
  const headerProfile=settingsEl('headerProfileBtn');
  headerProfile?.addEventListener('click',()=>openSettingsModal('account',headerProfile));
  settingsEl('settingsCloseBtn').addEventListener('click',closeSettingsModal);
  settingsEl('settingsBackBtn').addEventListener('click',settingsGoBack);
  settingsEl('settingsForwardBtn').addEventListener('click',settingsGoForward);
  settingsEl('settingsSearch').addEventListener('input',event=>{ settingsState.query=event.target.value; renderSettingsSearch(); });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&settingsState.open&&!settingsState.suspended&&!settingsEl('modalOverlay').classList.contains('show')){
      const search=settingsEl('settingsSearch');
      if(document.activeElement===search&&search.value){ event.preventDefault(); search.value=''; settingsState.query=''; renderSettingsSearch(); return; }
      event.preventDefault(); closeSettingsModal(); return;
    }
    settingsTrapFocus(event);
  },true);
  initSettingsSubdialogObserver();
}
initSettingsModal();

// Workspace backup captures only an actual unsaved profile, including its raster.
jpwWorkspaceDraftProviders.set('profile',(reset=false)=>{
  if(reset){settingsProfileCancelAsync();settingsProfileState.blocked=null;settingsProfileReload();return [];}
  if(settingsProfileState.busy)throw new Error('Aguarde o processamento da foto antes de exportar.');
  return settingsProfileDirty()?[{label:'Perfil — rascunho',text:JSON.stringify(settingsProfileState.draft)}]:[];
});
