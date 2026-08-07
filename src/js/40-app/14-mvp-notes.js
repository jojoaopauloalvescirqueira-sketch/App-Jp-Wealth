// ============ NOTAS DO MVP — backlog interno de testes (N1) ============
// Registro interno de tarefas/bugs/funcionalidades/melhorias durante o período de
// amadurecimento do MVP. Não é log de auditoria financeira, não é notificação, não
// guarda dado de trading. Enums (MVP_NOTES_TYPES/STATUSES/PRIORITIES) e normalização
// de item vivem em 00-core/04-persistence.js (script cedo — migrate() precisa deles
// antes deste arquivo carregar).
const MVP_NOTES_TYPE_LABELS={task:'Tarefa', bug:'Bug', feature:'Funcionalidade', improvement:'Melhoria'};
const MVP_NOTES_STATUS_LABELS={open:'Aberta', in_progress:'Em andamento', done:'Concluída', discarded:'Descartada'};
const MVP_NOTES_PRIORITY_LABELS={low:'Baixa', medium:'Média', high:'Alta', critical:'Crítica'};
const MVP_NOTES_SCREEN_LABELS={dash:'Dashboard', exec:'Execution Board', params:'Parâmetros', motor:'Motor de Lote',
  contas:'Contas', check:'Checklist', contab:'Contabilidade', config:'Configurações'};

const mvpNotesUI={
  open:false, mode:'list', editingId:null,
  draft:null, draftOriginal:null, draftMeta:null, draftDirty:false,
  query:'', filterType:'all', filterStatus:'all', filterPriority:'all',
  activeFolder:'all', // 'all' | 'unfiled' | id de pasta — visões virtuais nunca persistidas
  opener:null, optionsReady:false, inertSnapshot:null
};

function mvpn(id){ return document.getElementById(id); }

// ---- leitura de contexto (tela/build) ----
function mvpNotesCurrentScreenId(){
  if(typeof settingsIsOpen==='function' && settingsIsOpen()) return 'config';
  const active=document.querySelector('.screen.active');
  return active ? active.id : '';
}
function mvpNotesScreenLabel(id){ return MVP_NOTES_SCREEN_LABELS[id] || 'Geral'; }
function mvpNotesCurrentBuildId(){ return typeof JP_WEALTH_BUILD_ID==='string' ? JP_WEALTH_BUILD_ID : ''; }
function mvpNotesFormatDate(iso){
  try{ return new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'short'}).format(new Date(iso)); }
  catch(e){ return String(iso||'—'); }
}

// ---- leitura/derivação de dados ----
function mvpNotesItems(){ return (S.mvpNotes && Array.isArray(S.mvpNotes.items)) ? S.mvpNotes.items : []; }
function mvpNotesActiveCount(){ return mvpNotesItems().filter(it=>it.status==='open'||it.status==='in_progress').length; }
function mvpNotesSorted(){ return [...mvpNotesItems()].sort((a,b)=>String(b.updatedAt||'').localeCompare(String(a.updatedAt||''))); }
function mvpNotesHaystack(item){
  return [item.title, item.description, MVP_NOTES_TYPE_LABELS[item.type], MVP_NOTES_STATUS_LABELS[item.status],
    mvpNotesScreenLabel(item.screenId), item.buildId, mvpNotesFolderLabel(item.folderId)].join(' ').toLocaleLowerCase('pt-BR');
}
function mvpNotesFiltered(){
  const q=mvpNotesUI.query.trim().toLocaleLowerCase('pt-BR');
  return mvpNotesSorted().filter(item=>{
    if(mvpNotesUI.activeFolder==='unfiled' && item.folderId!==null) return false;
    else if(mvpNotesUI.activeFolder!=='all' && mvpNotesUI.activeFolder!=='unfiled' && item.folderId!==mvpNotesUI.activeFolder) return false;
    if(mvpNotesUI.filterType!=='all' && item.type!==mvpNotesUI.filterType) return false;
    if(mvpNotesUI.filterStatus!=='all' && item.status!==mvpNotesUI.filterStatus) return false;
    if(mvpNotesUI.filterPriority!=='all' && item.priority!==mvpNotesUI.filterPriority) return false;
    if(q && !mvpNotesHaystack(item).includes(q)) return false;
    return true;
  });
}

// ---- pastas (schemaVersion 2) — entidade real e explícita; "Todas as Notas"/"Sem pasta"
// são visões virtuais (mvpNotesUI.activeFolder='all'/'unfiled'), nunca persistidas como pasta. ----
function mvpNotesFolders(){ return (S.mvpNotes && Array.isArray(S.mvpNotes.folders)) ? S.mvpNotes.folders : []; }
function mvpNotesFolderById(id){ return mvpNotesFolders().find(f=>f.id===id) || null; }
function mvpNotesFolderLabel(folderId){
  if(!folderId) return 'Sem pasta';
  const f=mvpNotesFolderById(folderId);
  return f ? f.name : 'Sem pasta'; // referência órfã (não deveria ocorrer após normalização) — trata como Sem pasta
}
function mvpNotesFolderItemCount(folderId){ return mvpNotesItems().filter(it=>it.folderId===folderId).length; }
function mvpNotesUnfiledCount(){ return mvpNotesItems().filter(it=>it.folderId===null).length; }
function mvpNotesAllCount(){ return mvpNotesItems().length; }
function mvpNotesFolderNameExists(name,excludeId){
  const n=name.trim().toLocaleLowerCase('pt-BR');
  return mvpNotesFolders().some(f=>f.id!==excludeId && f.name.toLocaleLowerCase('pt-BR')===n);
}
function mvpNotesCreateFolder(name){
  const now=new Date().toISOString();
  const folder={id:mvpNotesFolderId(), name, createdAt:now, updatedAt:now};
  S.mvpNotes.folders.push(folder);
  save(); renderMvpNotesHeader();
  return folder;
}
function mvpNotesRenameFolder(id,name){
  const folder=mvpNotesFolderById(id); if(!folder) return null;
  if(folder.name===name) return folder; // nada mudou -> updatedAt não se move
  folder.name=name; folder.updatedAt=new Date().toISOString();
  save(); renderMvpNotesHeader();
  return folder;
}
// Exclui só a pasta; as notas associadas são preservadas integralmente e realocadas para
// "Sem pasta" (folderId=null) — nunca há opção de excluir pasta+notas juntas nesta versão.
function mvpNotesDeleteFolder(id){
  S.mvpNotes.folders=mvpNotesFolders().filter(f=>f.id!==id);
  mvpNotesItems().forEach(it=>{ if(it.folderId===id) it.folderId=null; });
  if(mvpNotesUI.activeFolder===id) mvpNotesUI.activeFolder='unfiled';
  save(); renderMvpNotesHeader();
}
function mvpNotesEnsureActiveFolderValid(){
  const af=mvpNotesUI.activeFolder;
  if(af==='all' || af==='unfiled') return;
  if(!mvpNotesFolderById(af)) mvpNotesUI.activeFolder='unfiled';
}
function mvpNotesViewLabel(){
  if(mvpNotesUI.activeFolder==='all') return 'Todas as Notas';
  if(mvpNotesUI.activeFolder==='unfiled') return 'Sem pasta';
  const f=mvpNotesFolderById(mvpNotesUI.activeFolder);
  return f ? f.name : 'Todas as Notas';
}

// ---- persistência (CRUD) ----
function mvpNotesPersist(){ save(); renderMvpNotesHeader(); }
function mvpNotesCreate(draft){
  const now=new Date().toISOString();
  const item={
    id:mvpNotesId(), type:draft.type, title:draft.title.trim().slice(0,120),
    description:String(draft.description||'').slice(0,5000),
    priority:draft.priority, status:draft.status, folderId:draft.folderId||null,
    screenId:mvpNotesUI.draftMeta.screenId, buildId:mvpNotesUI.draftMeta.buildId,
    createdAt:now, updatedAt:now
  };
  S.mvpNotes.items.push(item);
  mvpNotesPersist();
  return item;
}
function mvpNotesUpdate(id,draft){
  const item=mvpNotesItems().find(it=>it.id===id);
  if(!item) return null;
  const folderId=draft.folderId||null;
  const changed=item.type!==draft.type || item.title!==draft.title.trim().slice(0,120) ||
    item.description!==String(draft.description||'').slice(0,5000) ||
    item.priority!==draft.priority || item.status!==draft.status || (item.folderId||null)!==folderId;
  item.type=draft.type; item.title=draft.title.trim().slice(0,120);
  item.description=String(draft.description||'').slice(0,5000);
  item.priority=draft.priority; item.status=draft.status; item.folderId=folderId;
  if(changed) item.updatedAt=new Date().toISOString(); // nada mudou → updatedAt não se move
  mvpNotesPersist();
  return item;
}
function mvpNotesDelete(id){
  S.mvpNotes.items=mvpNotesItems().filter(it=>it.id!==id);
  mvpNotesPersist();
}

// ---- botão do header + card de Configurações ----
function renderMvpNotesHeader(){
  const btn=mvpn('headerNotesBtn');
  if(btn) btn.hidden=!(S.mvpNotes && S.mvpNotes.showHeaderIcon!==false);
  const count=mvpNotesActiveCount();
  const badge=mvpn('headerNotesBadge');
  if(badge){
    badge.hidden=count<=0;
    badge.textContent=count>99?'99+':String(count);
  }
  if(btn) btn.setAttribute('aria-label', count>0 ? `Abrir notas do MVP — ${count} ${count===1?'item ativo':'itens ativos'}` : 'Abrir notas do MVP');
  renderMvpNotesSettingsCard();
}
function renderMvpNotesSettingsCard(){
  const seg=mvpn('mvpNotesVisibilitySeg'); if(!seg) return;
  const showing=!(S.mvpNotes && S.mvpNotes.showHeaderIcon===false);
  seg.querySelectorAll('button').forEach(b=>b.classList.toggle('on', (b.dataset.mvpNotesVisibility==='show')===showing));
  const countEl=mvpn('mvpNotesSettingsCount');
  if(countEl){
    const total=mvpNotesItems().length, active=mvpNotesActiveCount();
    countEl.textContent=total===0 ? 'Nenhuma nota registrada ainda.' : `${total} nota${total===1?'':'s'} registrada${total===1?'':'s'} · ${active} ativa${active===1?'':'s'}.`;
  }
}
function bindMvpNotesSettingsCard(){
  const seg=mvpn('mvpNotesVisibilitySeg');
  if(seg) seg.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{
    S.mvpNotes.showHeaderIcon=b.dataset.mvpNotesVisibility==='show';
    save(); renderMvpNotesHeader();
  }));
  const openBtn=mvpn('mvpNotesOpenFromSettingsBtn');
  if(openBtn) openBtn.addEventListener('click',()=>{
    settingsMarkSubdialogLauncher(openBtn);
    openMvpNotesDrawer(openBtn);
  });
}

// ---- opções fixas dos selects (filtros + editor) ----
function mvpNotesBuildOptions(){
  if(mvpNotesUI.optionsReady) return;
  const fillFilter=(id,map,allLabel)=>{
    const el=mvpn(id); if(!el) return;
    el.innerHTML=`<option value="all">${allLabel}</option>`+Object.keys(map).map(k=>`<option value="${k}">${esc(map[k])}</option>`).join('');
  };
  fillFilter('mvpNotesFilterType',MVP_NOTES_TYPE_LABELS,'Todos os tipos');
  fillFilter('mvpNotesFilterStatus',MVP_NOTES_STATUS_LABELS,'Todos os status');
  fillFilter('mvpNotesFilterPriority',MVP_NOTES_PRIORITY_LABELS,'Todas as prioridades');
  mvpNotesUI.optionsReady=true;
}

// ---- lista ----
function mvpNotesCardHTML(item){
  const preview=esc(item.description||'').replace(/\n+/g,' ').trim();
  // A pasta só aparece no card na visão "Todas as Notas" (item 11): dentro de uma pasta
  // específica repetir o próprio nome em cada card é redundante; em "Sem pasta" o contexto
  // já basta.
  const folderLine=mvpNotesUI.activeFolder==='all'
    ? `<div class="mvpn-card-folder">${esc(mvpNotesFolderLabel(item.folderId))}</div>` : '';
  return `<button type="button" class="mvpn-card" data-mvp-note-id="${esc(item.id)}" data-status="${esc(item.status)}" data-priority="${esc(item.priority)}" data-type="${esc(item.type)}">
    <div class="mvpn-card-top">
      <span class="mvpn-badge mvpn-badge-type">${esc(MVP_NOTES_TYPE_LABELS[item.type]||item.type)}</span>
      <span class="mvpn-badge mvpn-badge-priority">${esc(MVP_NOTES_PRIORITY_LABELS[item.priority]||item.priority)}</span>
      <span class="mvpn-badge mvpn-badge-status">${esc(MVP_NOTES_STATUS_LABELS[item.status]||item.status)}</span>
    </div>
    <div class="mvpn-card-title">${esc(item.title)}</div>
    ${folderLine}
    ${preview?`<div class="mvpn-card-preview">${preview}</div>`:''}
    <div class="mvpn-card-meta">
      <span>${esc(mvpNotesScreenLabel(item.screenId))}</span><span aria-hidden="true">·</span>
      <span>${item.buildId?('build '+esc(item.buildId)):'build não informado'}</span><span aria-hidden="true">·</span>
      <span>atualizado em ${esc(mvpNotesFormatDate(item.updatedAt))}</span>
    </div>
  </button>`;
}
function renderMvpNotesList(){
  mvpNotesEnsureActiveFolderValid();
  renderMvpNotesFolderNav();
  const titleEl=mvpn('mvpNotesViewTitle'); if(titleEl) titleEl.textContent=mvpNotesViewLabel();
  const host=mvpn('mvpNotesList'); if(!host) return;
  const total=mvpNotesItems().length, items=mvpNotesFiltered();
  if(total===0){
    host.innerHTML=`<p class="mvpn-empty">Nenhuma nota registrada. Use "Nova nota" para registrar tarefas, bugs, funcionalidades ou melhorias do MVP.</p>`;
  }else if(items.length===0){
    host.innerHTML=`<p class="mvpn-empty">Nenhuma nota encontrada para estes filtros.</p>`;
  }else{
    host.innerHTML=items.map(mvpNotesCardHTML).join('');
  }
  host.querySelectorAll('[data-mvp-note-id]').forEach(card=>card.addEventListener('click',()=>{
    const id=card.dataset.mvpNoteId;
    mvpNotesConfirmDiscardIfDirty(()=>openMvpNotesEditor(id));
  }));
  const headCount=mvpn('mvpNotesHeadCount');
  if(headCount){
    const active=mvpNotesActiveCount();
    headCount.textContent=active===0?'Nenhum item ativo':`${active} ${active===1?'item ativo':'itens ativos'}`;
  }
}

// ---- navegação de pastas (sidebar desktop / seletor+gerenciar em mobile) ----
function mvpNotesFolderRowHTML(id,name,count,manageable){
  const active=mvpNotesUI.activeFolder===id;
  return `<div class="mvpn-folder-row">
    <button type="button" class="mvpn-folder-btn" data-mvp-folder="${esc(id)}" ${active?'aria-current="page"':''}>
      <span class="mvpn-folder-name" title="${esc(name)}">${esc(name)}</span>
      <span class="mvpn-folder-count">${count}</span>
    </button>
    ${manageable?`<details class="mvpn-folder-kebab">
      <summary aria-label="Mais ações para a pasta ${esc(name)}">⋯</summary>
      <div class="mvpn-folder-kebab-menu">
        <button type="button" data-mvp-folder-rename="${esc(id)}">Renomear</button>
        <button type="button" data-mvp-folder-delete="${esc(id)}">Excluir</button>
      </div>
    </details>`:''}
  </div>`;
}
function renderMvpNotesFolderNav(){
  const folders=mvpNotesFolders();
  const rows=[
    {id:'all', name:'Todas as Notas', count:mvpNotesAllCount()},
    {id:'unfiled', name:'Sem pasta', count:mvpNotesUnfiledCount()}
  ];
  const navHost=mvpn('mvpNotesFolderNavList');
  if(navHost){
    const staticHTML=rows.map(r=>mvpNotesFolderRowHTML(r.id,r.name,r.count,false)).join('');
    const folderHTML=folders.length
      ? `<div class="mvpn-folder-group-label">Pastas</div>`+folders.map(f=>mvpNotesFolderRowHTML(f.id,f.name,mvpNotesFolderItemCount(f.id),true)).join('')
      : '';
    navHost.innerHTML=staticHTML+folderHTML;
    bindMvpNotesFolderNavEvents(navHost);
  }
  const sel=mvpn('mvpNotesFolderMobileSelect');
  if(sel){
    const optionHTML=r=>`<option value="${esc(r.id)}">${esc(r.name)} (${r.count})</option>`;
    sel.innerHTML=rows.map(optionHTML).join('')
      +folders.map(f=>optionHTML({id:f.id,name:f.name,count:mvpNotesFolderItemCount(f.id)})).join('');
    sel.value=mvpNotesUI.activeFolder;
  }
}
function bindMvpNotesFolderNavEvents(host){
  host.querySelectorAll('[data-mvp-folder]').forEach(btn=>btn.addEventListener('click',()=>{
    mvpNotesSwitchFolder(btn.dataset.mvpFolder);
  }));
  host.querySelectorAll('[data-mvp-folder-rename]').forEach(btn=>btn.addEventListener('click',()=>{
    const details=btn.closest('details'); if(details) details.open=false;
    mvpNotesHandleRenameFolder(btn.dataset.mvpFolderRename);
  }));
  host.querySelectorAll('[data-mvp-folder-delete]').forEach(btn=>btn.addEventListener('click',()=>{
    const details=btn.closest('details'); if(details) details.open=false;
    mvpNotesHandleDeleteFolder(btn.dataset.mvpFolderDelete);
  }));
}
// Trocar de pasta preserva busca e os 3 filtros (item 12) — só re-renderiza a lista; a
// mesma proteção de rascunho não salvo das demais ações de pasta (item 14) se aplica aqui.
function mvpNotesSwitchFolder(target){
  const previous=mvpNotesUI.activeFolder;
  mvpNotesConfirmDiscardIfDirty(()=>{
    mvpNotesUI.activeFolder=target;
    renderMvpNotesMode('list');
  });
  // Descarte cancelado (confirm()===false): activeFolder não mudou, mas o <select> mobile
  // nativo já exibia visualmente a nova opção escolhida antes deste handler rodar —
  // resincroniza o valor exibido com o estado real, senão select e app divergem.
  if(mvpNotesUI.activeFolder===previous) renderMvpNotesFolderNav();
}
function mvpNotesPromptFolderName(defaultValue){
  const raw=prompt('Nome da pasta', defaultValue||'');
  if(raw===null) return null; // cancelado
  return raw.trim().slice(0,80);
}
function mvpNotesHandleNewFolder(){
  mvpNotesConfirmDiscardIfDirty(()=>{
    const name=mvpNotesPromptFolderName('');
    if(name===null) return;
    if(!name){ alert('Informe um nome para a pasta.'); return; }
    if(mvpNotesFolderNameExists(name,null) && !confirm(`Já existe uma pasta chamada "${name}". Deseja criar outra pasta com o mesmo nome?`)) return;
    const folder=mvpNotesCreateFolder(name);
    mvpNotesUI.activeFolder=folder.id;
    renderMvpNotesMode('list');
  });
}
function mvpNotesHandleRenameFolder(id){
  mvpNotesConfirmDiscardIfDirty(()=>{
    const folder=mvpNotesFolderById(id); if(!folder) return;
    const name=mvpNotesPromptFolderName(folder.name);
    if(name===null) return;
    if(!name){ alert('Informe um nome para a pasta.'); return; }
    if(name!==folder.name && mvpNotesFolderNameExists(name,id) && !confirm(`Já existe uma pasta chamada "${name}". Deseja renomear mesmo assim?`)) return;
    mvpNotesRenameFolder(id,name);
    renderMvpNotesMode('list');
  });
}
function mvpNotesHandleDeleteFolder(id){
  mvpNotesConfirmDiscardIfDirty(()=>{
    const folder=mvpNotesFolderById(id); if(!folder) return;
    const count=mvpNotesFolderItemCount(id);
    const msg=count>0
      ? `A pasta "${folder.name}" contém ${count} nota${count===1?'':'s'}. Ao excluir a pasta, ${count===1?'essa nota será movida':'essas notas serão movidas'} para "Sem pasta". Deseja continuar?`
      : `Deseja excluir a pasta "${folder.name}"?`;
    if(!confirm(msg)) return;
    mvpNotesDeleteFolder(id);
    renderMvpNotesMode('list');
  });
}
// Classe .open, não atributo hidden: em desktop o painel fica sempre visível por CSS, e
// hidden vencido por !important manteria o atributo no DOM — o filtro [hidden] do focus
// trap passaria a excluir a sidebar inteira mesmo visível e tabulável.
function mvpNotesSetFolderManageOpen(open){
  const el=mvpn('mvpNotesFolderManage'), btn=mvpn('mvpNotesManageFoldersBtn');
  if(el) el.classList.toggle('open', open);
  if(btn) btn.setAttribute('aria-expanded', String(open));
}
function mvpNotesToggleFolderManage(){
  const el=mvpn('mvpNotesFolderManage'); if(!el) return;
  mvpNotesSetFolderManageOpen(!el.classList.contains('open'));
}

// ---- editor ----
function mvpNotesDraftFromItem(item){
  return {type:item.type, title:item.title, description:item.description, priority:item.priority, status:item.status, folderId:item.folderId||null};
}
function mvpNotesDraftFromForm(){
  return {
    type:mvpn('mvpNoteType').value, title:mvpn('mvpNoteTitle').value,
    description:mvpn('mvpNoteDescription').value,
    priority:mvpn('mvpNotePriority').value, status:mvpn('mvpNoteStatus').value,
    folderId:mvpn('mvpNoteFolder').value||null
  };
}
function mvpNotesDraftEqual(a,b){
  return a.type===b.type && a.title.trim()===b.title.trim() && a.description===b.description &&
    a.priority===b.priority && a.status===b.status && (a.folderId||null)===(b.folderId||null);
}
function mvpNotesEditorHTML(isNew,meta){
  const optList=(map,selected)=>Object.keys(map).map(k=>`<option value="${k}" ${k===selected?'selected':''}>${esc(map[k])}</option>`).join('');
  return `
    <div class="mvpn-editor-head">
      <h3>${isNew?'Nova nota':'Editar nota'}</h3>
      <button type="button" class="mvpn-editor-back reset-btn" id="mvpNoteCancelBtn">${isNew?'Cancelar':'Voltar à lista'}</button>
    </div>
    <div class="field"><label for="mvpNoteType">Tipo</label>
      <select id="mvpNoteType">${optList(MVP_NOTES_TYPE_LABELS,mvpNotesUI.draft.type)}</select>
    </div>
    <div class="field"><label for="mvpNoteTitle">Título</label>
      <input type="text" id="mvpNoteTitle" maxlength="120" value="${esc(mvpNotesUI.draft.title)}" placeholder="Ex.: corrigir alinhamento do card X">
      <span class="mvpn-hint">Obrigatório, até 120 caracteres.</span>
    </div>
    <div class="field"><label for="mvpNoteDescription">Descrição</label>
      <textarea id="mvpNoteDescription" rows="6" maxlength="5000" placeholder="Detalhes, passos para reproduzir, contexto...">${esc(mvpNotesUI.draft.description)}</textarea>
      <span class="mvpn-hint">Opcional, até 5.000 caracteres. Texto simples — nenhum HTML é interpretado.</span>
    </div>
    <div class="mvpn-editor-row">
      <div class="field"><label for="mvpNotePriority">Prioridade</label>
        <select id="mvpNotePriority">${optList(MVP_NOTES_PRIORITY_LABELS,mvpNotesUI.draft.priority)}</select>
      </div>
      <div class="field"><label for="mvpNoteStatus">Status</label>
        <select id="mvpNoteStatus">${optList(MVP_NOTES_STATUS_LABELS,mvpNotesUI.draft.status)}</select>
      </div>
    </div>
    <div class="field"><label for="mvpNoteFolder">Pasta</label>
      <select id="mvpNoteFolder">
        <option value="" ${!mvpNotesUI.draft.folderId?'selected':''}>Sem pasta</option>
        ${mvpNotesFolders().map(f=>`<option value="${esc(f.id)}" ${f.id===mvpNotesUI.draft.folderId?'selected':''}>${esc(f.name)}</option>`).join('')}
      </select>
    </div>
    <dl class="mvpn-meta-facts">
      <dt>Tela</dt><dd>${esc(mvpNotesScreenLabel(meta.screenId))}</dd>
      <dt>Build</dt><dd>${meta.buildId?esc(meta.buildId):'não informado'}</dd>
      <dt>Criada em</dt><dd>${meta.createdAt?esc(mvpNotesFormatDate(meta.createdAt)):'ao salvar'}</dd>
      <dt>Atualizada em</dt><dd>${meta.updatedAt?esc(mvpNotesFormatDate(meta.updatedAt)):'ao salvar'}</dd>
    </dl>
    <p class="mvpn-editor-err" id="mvpNoteErr" hidden></p>
    <div class="mvpn-editor-actions">
      ${isNew?'':'<button type="button" class="reset-btn mvpn-danger" id="mvpNoteDeleteBtn">Excluir nota</button>'}
      <button type="button" class="reset-btn mvpn-primary" id="mvpNoteSaveBtn">${isNew?'Criar nota':'Salvar alterações'}</button>
    </div>`;
}
function bindMvpNotesEditor(isNew,id){
  ['mvpNoteType','mvpNoteTitle','mvpNoteDescription','mvpNotePriority','mvpNoteStatus','mvpNoteFolder'].forEach(fid=>{
    const el=mvpn(fid); if(!el) return;
    el.addEventListener('input',()=>{ mvpNotesUI.draftDirty=!mvpNotesDraftEqual(mvpNotesDraftFromForm(),mvpNotesUI.draftOriginal); });
    el.addEventListener('change',()=>{ mvpNotesUI.draftDirty=!mvpNotesDraftEqual(mvpNotesDraftFromForm(),mvpNotesUI.draftOriginal); });
  });
  const cancelBtn=mvpn('mvpNoteCancelBtn');
  if(cancelBtn) cancelBtn.addEventListener('click',()=>mvpNotesConfirmDiscardIfDirty(()=>renderMvpNotesMode('list')));
  const saveBtn=mvpn('mvpNoteSaveBtn');
  if(saveBtn) saveBtn.addEventListener('click',()=>{
    const draft=mvpNotesDraftFromForm();
    const title=draft.title.trim();
    const err=mvpn('mvpNoteErr');
    if(!title){
      if(err){ err.textContent='Informe um título para a nota.'; err.hidden=false; }
      mvpn('mvpNoteTitle').focus();
      return;
    }
    if(err) err.hidden=true;
    if(isNew) mvpNotesCreate(draft); else mvpNotesUpdate(id,draft);
    mvpNotesUI.draftDirty=false;
    renderMvpNotesMode('list');
  });
  const deleteBtn=mvpn('mvpNoteDeleteBtn');
  if(deleteBtn) deleteBtn.addEventListener('click',()=>{
    const item=mvpNotesItems().find(it=>it.id===id); if(!item) return;
    if(!confirm(`Excluir a nota "${item.title}"? Esta ação não pode ser desfeita.`)) return;
    mvpNotesDelete(id);
    mvpNotesUI.draftDirty=false;
    renderMvpNotesMode('list');
  });
}
function openMvpNotesEditor(id){
  const isNew=!id;
  const item=isNew?null:mvpNotesItems().find(it=>it.id===id);
  if(!isNew && !item) return;
  mvpNotesUI.editingId=isNew?null:id;
  // Nova nota dentro de uma pasta específica herda essa pasta (itens 7/10); em "Todas as
  // Notas" ou "Sem pasta" (visões virtuais) o padrão é null — o operador escolhe no editor.
  const defaultFolderId=(mvpNotesUI.activeFolder!=='all' && mvpNotesUI.activeFolder!=='unfiled') ? mvpNotesUI.activeFolder : null;
  mvpNotesUI.draft=isNew ? {type:'task', title:'', description:'', priority:'medium', status:'open', folderId:defaultFolderId} : mvpNotesDraftFromItem(item);
  mvpNotesUI.draftOriginal={...mvpNotesUI.draft};
  mvpNotesUI.draftDirty=false;
  mvpNotesUI.draftMeta=isNew
    ? {screenId:mvpNotesCurrentScreenId(), buildId:mvpNotesCurrentBuildId(), createdAt:'', updatedAt:''}
    : {screenId:item.screenId, buildId:item.buildId, createdAt:item.createdAt, updatedAt:item.updatedAt};
  renderMvpNotesMode('editor');
}
function renderMvpNotesMode(mode){
  mvpNotesUI.mode=mode;
  const toolbar=mvpn('mvpNotesToolbar'), list=mvpn('mvpNotesList'), editor=mvpn('mvpNotesEditor');
  if(mode==='editor'){
    if(toolbar) toolbar.hidden=true;
    if(list) list.hidden=true;
    if(editor){
      editor.hidden=false;
      const isNew=!mvpNotesUI.editingId;
      editor.innerHTML=mvpNotesEditorHTML(isNew,mvpNotesUI.draftMeta);
      bindMvpNotesEditor(isNew,mvpNotesUI.editingId);
      // Foco síncrono, não via requestAnimationFrame: o campo é estático (só o hidden do
      // contêiner muda), já está pronto para foco no mesmo tick — depender de rAF é frágil
      // em abas sem repaint ativo (verificado: rAF pode nunca disparar nesse cenário).
      const t=mvpn('mvpNoteTitle'); if(t) t.focus();
    }
  }else{
    if(toolbar) toolbar.hidden=false;
    if(list){ list.hidden=false; renderMvpNotesList(); }
    if(editor){ editor.hidden=true; editor.innerHTML=''; }
    mvpNotesUI.editingId=null; mvpNotesUI.draft=null; mvpNotesUI.draftOriginal=null; mvpNotesUI.draftDirty=false;
  }
}
function mvpNotesConfirmDiscardIfDirty(proceed){
  if(mvpNotesUI.mode==='editor' && mvpNotesUI.draftDirty){
    if(!confirm('Existem alterações não salvas nesta nota. Deseja descartá-las?')) return;
  }
  proceed();
}

// ---- abertura/fechamento do drawer (foco, trap, inert — mesmo padrão da Central) ----
function mvpNotesFocusables(root){
  // offsetParent!==null exclui o conteúdo de <details> fechados (menu "⋯" de cada pasta,
  // painel "Gerenciar pastas" em mobile) — sem isto o wrap do Tab poderia pular para um
  // botão invisível em vez do primeiro/último elemento realmente visível do drawer.
  // <summary> entra explicitamente: tem tabIndex 0 nativo mas nenhum atributo tabindex,
  // então o seletor [tabindex] não o alcança — sem ele o trap calcularia primeiro/último
  // ignorando os menus "⋯" das pastas, que estão na ordem natural do Tab.
  return [...root.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])')]
    .filter(el=>!el.closest('[hidden]'))
    .filter(el=>el.offsetParent!==null || el===document.activeElement);
}
function mvpNotesTrapFocus(event){
  if(!mvpNotesUI.open || event.key!=='Tab') return;
  const list=mvpNotesFocusables(mvpn('mvpNotesDrawer')); if(!list.length) return;
  const first=list[0], last=list[list.length-1];
  if(event.shiftKey && document.activeElement===first){ event.preventDefault(); last.focus(); }
  else if(!event.shiftKey && document.activeElement===last){ event.preventDefault(); first.focus(); }
}
// Isolamento acessível: os quatro irmãos de nível superior que ficam FORA do drawer/overlay
// — <header> (todas as ações do topo, inclusive o próprio botão que abre o drawer), #nav
// (abas de tela), #appMain (todo o conteúdo operacional da tela ativa) e .foot-note. Nunca
// um clear cego: captura o valor real de .inert/aria-hidden de cada um ANTES de tocar
// (outro mecanismo — a própria Central, quando já aberta por baixo — pode já os ter assim
// por razão própria) e restaura exatamente esse valor ao fechar, nunca um "false"/remoção
// incondicional. Roda sempre, esteja a Central aberta por baixo ou não: cobre inclusive o
// que a suspensão da Central (suspendSettingsForSubdialog, abaixo) não cobre sozinha —
// aquela função só torna #settingsModal inert, nunca tocou <header>/#appMain.
function mvpNotesInertTargets(){
  return [document.querySelector('header'), document.querySelector('#nav'), document.querySelector('#appMain'), document.querySelector('.foot-note')].filter(Boolean);
}
function mvpNotesApplyInert(){
  mvpNotesUI.inertSnapshot=mvpNotesInertTargets().map(el=>({el, inert:el.inert, ariaHidden:el.getAttribute('aria-hidden')}));
  mvpNotesUI.inertSnapshot.forEach(({el})=>{ el.inert=true; el.setAttribute('aria-hidden','true'); });
}
function mvpNotesRestoreInert(){
  const snapshot=mvpNotesUI.inertSnapshot; if(!snapshot) return;
  snapshot.forEach(({el,inert,ariaHidden})=>{
    el.inert=inert;
    if(ariaHidden===null) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden',ariaHidden);
  });
  mvpNotesUI.inertSnapshot=null;
}
// Consultado ao vivo em cada chamada (nunca guardado em flag) — se guardássemos "a Central
// estava aberta quando abri" num booleano capturado na abertura, um fechamento da Central
// por qualquer outro caminho enquanto o drawer segue aberto deixaria esse booleano obsoleto.
function mvpNotesSettingsOpen(){ return typeof settingsIsOpen==='function' && settingsIsOpen(); }
function openMvpNotesDrawer(opener){
  mvpNotesBuildOptions();
  mvpNotesUI.open=true;
  mvpNotesUI.opener=opener||document.activeElement||mvpn('headerNotesBtn');
  mvpNotesUI.query=''; mvpNotesUI.filterType='all'; mvpNotesUI.filterStatus='all'; mvpNotesUI.filterPriority='all';
  mvpNotesUI.activeFolder='all'; // cada abertura começa em "Todas as Notas", mesmo padrão dos filtros
  const search=mvpn('mvpNotesSearch'); if(search) search.value='';
  ['mvpNotesFilterType','mvpNotesFilterStatus','mvpNotesFilterPriority'].forEach(id=>{ const el=mvpn(id); if(el) el.value='all'; });
  mvpNotesSetFolderManageOpen(false); // painel "Gerenciar pastas" começa recolhido em mobile
  // A Central usa #modalOverlay como sinal para suspender seu próprio focus trap
  // (initSettingsSubdialogObserver, 09-settings-modal.js); nosso drawer tem overlay
  // próprio, então o MutationObserver dela nunca vê esta abertura — sem isto, os dois
  // focus traps disputariam Tab ao mesmo tempo quando aberto via "Abrir Notas".
  if(mvpNotesSettingsOpen() && typeof suspendSettingsForSubdialog==='function') suspendSettingsForSubdialog();
  mvpn('mvpNotesOverlay').classList.add('show');
  mvpn('mvpNotesOverlay').setAttribute('aria-hidden','false');
  mvpNotesApplyInert();
  renderMvpNotesMode('list');
  // Foco síncrono, não via requestAnimationFrame: dependência de rAF é frágil em abas sem
  // repaint ativo (verificado nesta sessão: rAF pode nunca disparar nesse cenário, deixando
  // o foco preso fora do diálogo modal — inaceitável para a isolação acessível pedida).
  const closeBtn=mvpn('mvpNotesCloseBtn'); if(closeBtn) closeBtn.focus();
}
function closeMvpNotesDrawerNow(){
  mvpNotesUI.open=false;
  mvpn('mvpNotesOverlay').classList.remove('show');
  mvpn('mvpNotesOverlay').setAttribute('aria-hidden','true');
  mvpNotesRestoreInert();
  const opener=mvpNotesUI.opener; mvpNotesUI.opener=null;
  if(typeof restoreSettingsAfterSubdialog==='function') restoreSettingsAfterSubdialog();
  if(opener && document.contains(opener) && !mvpNotesSettingsOpen()) opener.focus();
}
function closeMvpNotesDrawer(){
  mvpNotesConfirmDiscardIfDirty(closeMvpNotesDrawerNow);
}

// ---- inicialização ----
function bindMvpNotesDrawer(){
  mvpn('headerNotesBtn').addEventListener('click',()=>openMvpNotesDrawer(mvpn('headerNotesBtn')));
  mvpn('mvpNotesCloseBtn').addEventListener('click',closeMvpNotesDrawer);
  mvpn('mvpNotesOverlay').addEventListener('click',e=>{ if(e.target.id==='mvpNotesOverlay') closeMvpNotesDrawer(); });
  mvpn('mvpNotesNewBtn').addEventListener('click',()=>mvpNotesConfirmDiscardIfDirty(()=>openMvpNotesEditor(null)));
  mvpn('mvpNotesSearch').addEventListener('input',e=>{ mvpNotesUI.query=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesFilterType').addEventListener('change',e=>{ mvpNotesUI.filterType=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesFilterStatus').addEventListener('change',e=>{ mvpNotesUI.filterStatus=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesFilterPriority').addEventListener('change',e=>{ mvpNotesUI.filterPriority=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesNewFolderBtn').addEventListener('click',mvpNotesHandleNewFolder);
  mvpn('mvpNotesFolderMobileSelect').addEventListener('change',e=>mvpNotesSwitchFolder(e.target.value));
  mvpn('mvpNotesManageFoldersBtn').addEventListener('click',mvpNotesToggleFolderManage);
  document.addEventListener('keydown',event=>{
    if(!mvpNotesUI.open) return;
    if(event.key==='Escape'){
      event.preventDefault();
      if(mvpNotesUI.mode==='editor') mvpNotesConfirmDiscardIfDirty(()=>renderMvpNotesMode('list'));
      else closeMvpNotesDrawer();
      return;
    }
    mvpNotesTrapFocus(event);
  },true);
}
function initMvpNotes(){
  mvpNotesBuildOptions();
  bindMvpNotesDrawer();
  bindMvpNotesSettingsCard();
  renderMvpNotesHeader();
}
initMvpNotes();
