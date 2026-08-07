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
  filterFolder:'all', filterPeriod:'all', // exclusivos da visão Concluído (pasta original / período de conclusão)
  activeFolder:'all', // 'all' | 'unfiled' | 'done' | id de pasta — visões virtuais nunca persistidas
  stage:'folders', // navegação mobile em camadas: 'folders' | 'list' | 'editor' (desktop ignora)
  filtersSheetOpen:false, // bottom sheet de filtros (mobile)
  opener:null, optionsReady:false, inertSnapshot:null,
  resize:null // gesto de resize em andamento {startX,startW} — nunca persiste durante pointermove
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
function mvpNotesDoneCount(){ return mvpNotesItems().filter(it=>it.status==='done').length; }
function mvpNotesIsDoneView(){ return mvpNotesUI.activeFolder==='done'; }
function mvpNotesSorted(){ return [...mvpNotesItems()].sort((a,b)=>String(b.updatedAt||'').localeCompare(String(a.updatedAt||''))); }
// Concluído ordena pelo carimbo de conclusão (mais recente primeiro); fallback updatedAt
// cobre só o caso teórico de completedAt ausente — a normalização já o garante em 'done'.
function mvpNotesSortedByCompletion(){
  return [...mvpNotesItems()].sort((a,b)=>
    String(b.completedAt||b.updatedAt||'').localeCompare(String(a.completedAt||a.updatedAt||'')));
}
function mvpNotesHaystack(item){
  // O ticket entra na busca: colar de volta o código copiado (JPW-XXXXXX) localiza a nota
  // — é o caminho de volta do agente de IA para o app.
  return [item.ticket, item.title, item.description, MVP_NOTES_TYPE_LABELS[item.type], MVP_NOTES_STATUS_LABELS[item.status],
    mvpNotesScreenLabel(item.screenId), item.buildId, mvpNotesFolderLabel(item.folderId)].join(' ').toLocaleLowerCase('pt-BR');
}

// ---- Trace Reference (v4) ----
// Bloco autossuficiente para colar num agente de IA. O ticket sozinho NÃO dá acesso à
// nota: este app é client-side e as notas vivem apenas no localStorage deste navegador —
// não há API, servidor nem banco remoto para o agente consultar. Por isso o bloco carrega
// todo o contexto necessário, e termina com uma instrução explícita de investigação.
function mvpNotesSourceRevision(item){
  // Nunca inventa nem deriva do buildId (que é impressão digital de conteúdo, não commit).
  if(item && typeof item.sourceRevision==='string' && item.sourceRevision) return item.sourceRevision;
  if(typeof JP_WEALTH_SOURCE_REVISION==='string' && JP_WEALTH_SOURCE_REVISION) return JP_WEALTH_SOURCE_REVISION;
  return null;
}
function mvpNotesReferenceBlock(item){
  const rev=mvpNotesSourceRevision(item);
  const L=[
    'JP WEALTH — TRACE REFERENCE','',
    `Ticket: ${item.ticket}`,
    `Tipo: ${MVP_NOTES_TYPE_LABELS[item.type]||item.type}`,
    `Prioridade: ${MVP_NOTES_PRIORITY_LABELS[item.priority]||item.priority}`,
    `Status: ${MVP_NOTES_STATUS_LABELS[item.status]||item.status}`,'',
    'Título:', item.title,'',
    'Pasta:', mvpNotesFolderLabel(item.folderId),'',
    'Origem:',
    `Tela: ${mvpNotesScreenLabel(item.screenId)}`,
    `Build ID: ${item.buildId||'não disponível'}`,
    `Source Revision: ${rev||'não disponível'}`,'',
    'Criada:', mvpNotesFormatDate(item.createdAt),'',
    'Atualizada:', mvpNotesFormatDate(item.updatedAt)
  ];
  if(item.status==='done' && item.completedAt) L.push('','Concluída:', mvpNotesFormatDate(item.completedAt));
  L.push('','Descrição:', String(item.description||'').trim()||'(sem descrição)');
  L.push('','INSTRUÇÃO AO AGENTE','',
    `Investigue exclusivamente o problema associado ao ticket ${item.ticket}.`,'',
    'Antes de alterar código:',
    '1. confirme o contexto e a versão disponível;',
    '2. localize o componente relacionado;',
    '3. reproduza o problema;',
    '4. determine a causa raiz;',
    '5. informe os arquivos potencialmente afetados;',
    '6. não altere áreas não relacionadas;',
    '7. não faça commit, push ou merge sem autorização.');
  return L.join('\n');
}
// Cópia com dois caminhos: a API moderna (assíncrona, exige contexto seguro) e o
// fallback por textarea+execCommand, necessário quando o monólito portátil é aberto
// direto do disco (file://), onde navigator.clipboard costuma não existir.
function mvpNotesCopyText(text){
  if(navigator.clipboard && navigator.clipboard.writeText){
    return navigator.clipboard.writeText(text).catch(()=>mvpNotesCopyFallback(text));
  }
  return Promise.resolve(mvpNotesCopyFallback(text));
}
function mvpNotesCopyFallback(text){
  try{
    const ta=document.createElement('textarea');
    ta.value=text;
    ta.setAttribute('readonly','');
    ta.style.cssText='position:fixed; top:0; left:-9999px; opacity:0';
    document.body.appendChild(ta);
    ta.select();
    const ok=document.execCommand('copy');
    ta.remove();
    if(!ok) throw new Error('execCommand recusou a cópia');
    return true;
  }catch(e){ return Promise.reject(e); }
}
// Retorno visível E anunciável: o botão troca de rótulo por 1,6s e o texto muda dentro de
// um contêiner aria-live, para leitor de tela confirmar sem depender da cor do ícone.
function mvpNotesFlashCopyFeedback(btn,message,failed){
  const live=mvpn('mvpNotesCopyLive');
  if(live) live.textContent=message;
  if(!btn) return;
  btn.classList.toggle('mvpn-copy-failed',!!failed);
  btn.classList.add('mvpn-copy-done');
  clearTimeout(btn.__copyTimer);
  btn.__copyTimer=setTimeout(()=>{
    btn.classList.remove('mvpn-copy-done','mvpn-copy-failed');
    if(live) live.textContent='';
  },1600);
}
function mvpNotesHandleCopy(id,btn){
  const item=mvpNotesItems().find(it=>it.id===id); if(!item) return;
  mvpNotesCopyText(mvpNotesReferenceBlock(item))
    .then(()=>mvpNotesFlashCopyFeedback(btn,`Referência ${item.ticket} copiada.`,false))
    .catch(()=>mvpNotesFlashCopyFeedback(btn,'Não foi possível copiar automaticamente. Abra a nota e copie o texto manualmente.',true));
}
function mvpNotesCompletedWithinPeriod(item,period){
  if(period==='all') return true;
  const days={ '7d':7, '30d':30 }[period]; if(!days) return true;
  const ts=Date.parse(item.completedAt||item.updatedAt||'');
  if(!Number.isFinite(ts)) return false;
  return (Date.now()-ts)<=days*24*60*60*1000;
}
function mvpNotesFiltered(){
  const q=mvpNotesUI.query.trim().toLocaleLowerCase('pt-BR');
  const doneView=mvpNotesIsDoneView();
  const base=doneView?mvpNotesSortedByCompletion():mvpNotesSorted();
  return base.filter(item=>{
    if(doneView){
      // Visão virtual do sistema: derivada exclusivamente do status — folderId intocado.
      if(item.status!=='done') return false;
      if(mvpNotesUI.filterFolder!=='all'){
        if(mvpNotesUI.filterFolder==='unfiled'){ if(item.folderId!==null) return false; }
        else if(item.folderId!==mvpNotesUI.filterFolder) return false;
      }
      if(!mvpNotesCompletedWithinPeriod(item,mvpNotesUI.filterPeriod)) return false;
    }else{
      if(mvpNotesUI.activeFolder==='unfiled' && item.folderId!==null) return false;
      else if(mvpNotesUI.activeFolder!=='all' && mvpNotesUI.activeFolder!=='unfiled' && item.folderId!==mvpNotesUI.activeFolder) return false;
      // Pastas comuns e "Sem pasta" são backlog ativo: concluídas ficam fora POR PADRÃO
      // (elas vivem na visão Concluído). O filtro explícito de status "Concluída" é a
      // exceção deliberada — "por padrão" não significa "inacessível". "Todas as Notas"
      // permanece literalmente global (item 1.4).
      if(mvpNotesUI.activeFolder!=='all' && item.status==='done' && mvpNotesUI.filterStatus!=='done') return false;
      if(mvpNotesUI.filterStatus!=='all' && item.status!==mvpNotesUI.filterStatus) return false;
    }
    if(mvpNotesUI.filterType!=='all' && item.type!==mvpNotesUI.filterType) return false;
    if(mvpNotesUI.filterPriority!=='all' && item.priority!==mvpNotesUI.filterPriority) return false;
    if(q && !mvpNotesHaystack(item).includes(q)) return false;
    return true;
  });
}
// Contagem de filtros ativos (indicador "Filtros · N" no mobile) — busca não conta.
function mvpNotesActiveFilterCount(){
  let n=0;
  if(mvpNotesUI.filterType!=='all') n++;
  if(mvpNotesUI.filterPriority!=='all') n++;
  if(mvpNotesIsDoneView()){
    if(mvpNotesUI.filterFolder!=='all') n++;
    if(mvpNotesUI.filterPeriod!=='all') n++;
  }else if(mvpNotesUI.filterStatus!=='all') n++;
  return n;
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
// Contadores semânticos (item 1.5): pastas comuns e "Sem pasta" contam só o backlog
// ativo exibido nelas (status!=='done' — concluídas vivem na visão Concluído);
// "Todas as Notas" conta literalmente tudo; "Concluído" conta status==='done'.
function mvpNotesFolderItemCount(folderId){ return mvpNotesItems().filter(it=>it.folderId===folderId && it.status!=='done').length; }
function mvpNotesFolderTotalCount(folderId){ return mvpNotesItems().filter(it=>it.folderId===folderId).length; }
function mvpNotesUnfiledCount(){ return mvpNotesItems().filter(it=>it.folderId===null && it.status!=='done').length; }
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
  if(af==='all' || af==='unfiled' || af==='done') return;
  if(!mvpNotesFolderById(af)) mvpNotesUI.activeFolder='unfiled';
}
function mvpNotesViewLabel(){
  if(mvpNotesUI.activeFolder==='all') return 'Todas as Notas';
  if(mvpNotesUI.activeFolder==='unfiled') return 'Sem pasta';
  if(mvpNotesUI.activeFolder==='done') return 'Concluído';
  const f=mvpNotesFolderById(mvpNotesUI.activeFolder);
  return f ? f.name : 'Todas as Notas';
}

// ---- persistência (CRUD) ----
function mvpNotesPersist(){ save(); renderMvpNotesHeader(); }
function mvpNotesCreate(draft){
  const now=new Date().toISOString();
  const id=mvpNotesId();
  // Ticket derivado do id na criação, com o MESMO resolvedor da normalização (inclusive a
  // checagem de colisão contra os códigos já em uso) — criar uma nota e reimportá-la de um
  // backup produzem exatamente o mesmo código.
  const seenTickets=new Set(mvpNotesItems().map(it=>it.ticket).filter(Boolean));
  const item={
    id, ticket:mvpNotesResolveTicket(null,id,seenTickets),
    type:draft.type, title:draft.title.trim().slice(0,120),
    description:String(draft.description||'').slice(0,5000),
    priority:draft.priority, status:draft.status, folderId:draft.folderId||null,
    screenId:mvpNotesUI.draftMeta.screenId, buildId:mvpNotesUI.draftMeta.buildId,
    // Capturada só se o build realmente a expuser; hoje sempre null (ver 04-persistence.js).
    sourceRevision:(typeof JP_WEALTH_SOURCE_REVISION==='string' && JP_WEALTH_SOURCE_REVISION) ? JP_WEALTH_SOURCE_REVISION : null,
    createdAt:now, updatedAt:now,
    completedAt:draft.status==='done'?now:null // nota já criada concluída (raro, mas possível no editor)
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
  // Carimbo de conclusão: entra em 'done' → agora; sai de 'done' → null (reabrir zera o
  // histórico; concluir de novo gera carimbo novo); permanece em 'done' → intocado.
  // folderId NUNCA é alterado por transição de status — a visão Concluído é derivada,
  // e reabrir devolve a nota à pasta original automaticamente porque ela nunca saiu de lá.
  if(item.status!=='done' && draft.status==='done') item.completedAt=new Date().toISOString();
  else if(item.status==='done' && draft.status!=='done') item.completedAt=null;
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
  const period=mvpn('mvpNotesFilterPeriod');
  if(period) period.innerHTML=`<option value="all">Qualquer período</option><option value="7d">Concluídas nos últimos 7 dias</option><option value="30d">Concluídas nos últimos 30 dias</option>`;
  mvpNotesUI.optionsReady=true;
}

// ---- lista ----
function mvpNotesCardHTML(item){
  const preview=esc(item.description||'').replace(/\n+/g,' ').trim();
  // A pasta aparece no card nas visões globais "Todas as Notas" e "Concluído" (a pasta
  // ORIGINAL preservada — folderId nunca muda ao concluir): dentro de uma pasta específica
  // repetir o próprio nome em cada card é redundante; em "Sem pasta" o contexto já basta.
  const folderLine=(mvpNotesUI.activeFolder==='all'||mvpNotesIsDoneView())
    ? `<div class="mvpn-card-folder">${esc(mvpNotesFolderLabel(item.folderId))}</div>` : '';
  // O card é um <button>; o botão de copiar NÃO pode ser aninhado nele (HTML inválido,
  // com comportamento imprevisível de clique). Por isso os dois são IRMÃOS dentro de um
  // invólucro posicionado — o clique no card continua abrindo o editor como sempre.
  return `<div class="mvpn-card-wrap">
    <button type="button" class="mvpn-card" data-mvp-note-id="${esc(item.id)}" data-status="${esc(item.status)}" data-priority="${esc(item.priority)}" data-type="${esc(item.type)}">
      <div class="mvpn-card-top">
        <span class="mvpn-badge mvpn-badge-type">${esc(MVP_NOTES_TYPE_LABELS[item.type]||item.type)}</span>
        <span class="mvpn-badge mvpn-badge-priority">${esc(MVP_NOTES_PRIORITY_LABELS[item.priority]||item.priority)}</span>
        <span class="mvpn-badge mvpn-badge-status">${esc(MVP_NOTES_STATUS_LABELS[item.status]||item.status)}</span>
      </div>
      <div class="mvpn-card-title">${esc(item.title)}</div>
      ${folderLine}
      ${preview?`<div class="mvpn-card-preview">${preview}</div>`:''}
      <div class="mvpn-card-meta">
        <span class="mvpn-card-ticket">${esc(item.ticket||'')}</span><span aria-hidden="true">·</span>
        <span>${esc(mvpNotesScreenLabel(item.screenId))}</span><span aria-hidden="true">·</span>
        <span>${item.buildId?('build '+esc(item.buildId)):'build não informado'}</span><span aria-hidden="true">·</span>
        <span>${item.status==='done'&&item.completedAt
          ?('concluída em '+esc(mvpNotesFormatDate(item.completedAt)))
          :('atualizado em '+esc(mvpNotesFormatDate(item.updatedAt)))}</span>
      </div>
    </button>
    <button type="button" class="mvpn-card-copy" data-mvp-copy-id="${esc(item.id)}"
      title="Copiar referência ${esc(item.ticket||'')} para colar num agente de IA"
      aria-label="Copiar referência da nota ${esc(item.ticket||'')}: ${esc(item.title)}">
      <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/></svg>
      <span class="mvpn-copy-check" aria-hidden="true">✓</span>
    </button>
  </div>`;
}
// Sincroniza os controles de filtro com a visão ativa: em "Concluído" o filtro de status
// some (o status é implícito) e entram "Pasta original" + "Período de conclusão"; nas
// demais visões vale o trio original. "Tela de origem" e "Build" seguem cobertos pela
// busca textual (mvpNotesHaystack) — infraestrutura atual, sem selects novos para eles.
function mvpNotesSyncFilterControls(){
  const done=mvpNotesIsDoneView();
  const show=(id,visible)=>{ const el=mvpn(id); if(el) el.hidden=!visible; };
  show('mvpNotesFilterStatus',!done);
  show('mvpNotesFilterFolder',done);
  show('mvpNotesFilterPeriod',done);
  const folderSel=mvpn('mvpNotesFilterFolder');
  if(folderSel && done){
    folderSel.innerHTML=`<option value="all">Todas as pastas de origem</option><option value="unfiled">Sem pasta</option>`
      +mvpNotesFolders().map(f=>`<option value="${esc(f.id)}">${esc(f.name)}</option>`).join('');
    folderSel.value=mvpNotesUI.filterFolder;
    if(folderSel.value!==mvpNotesUI.filterFolder){ mvpNotesUI.filterFolder='all'; folderSel.value='all'; } // pasta excluída após escolher o filtro
  }
  const periodSel=mvpn('mvpNotesFilterPeriod');
  if(periodSel) periodSel.value=mvpNotesUI.filterPeriod;
  const fbtn=mvpn('mvpNotesFiltersBtn');
  if(fbtn){
    const n=mvpNotesActiveFilterCount();
    fbtn.textContent=n>0?`Filtros · ${n}`:'Filtros';
    fbtn.setAttribute('aria-label',n>0?`Abrir filtros — ${n} filtro${n===1?'':'s'} ativo${n===1?'':'s'}`:'Abrir filtros');
  }
}
function renderMvpNotesList(){
  mvpNotesEnsureActiveFolderValid();
  renderMvpNotesFolderNav();
  mvpNotesSyncFilterControls();
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
  host.querySelectorAll('[data-mvp-copy-id]').forEach(btn=>btn.addEventListener('click',()=>{
    mvpNotesHandleCopy(btn.dataset.mvpCopyId,btn);
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
  const system=id==='all'||id==='unfiled'||id==='done';
  const systemAttr=system?` data-mvp-system-view="true" aria-description="Visão do sistema"`:'';
  return `<div class="mvpn-folder-row${id==='done'?' mvpn-folder-row-done':''}">
    <button type="button" class="mvpn-folder-btn" data-mvp-folder="${esc(id)}"${systemAttr} ${active?'aria-current="page"':''}>
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
  // "Concluído" é visão do sistema (derivada de status==='done'): não renomeável, não
  // excluível, nunca persistida em folders[] — mesma família de "Todas as Notas"/"Sem pasta".
  const rows=[
    {id:'all', name:'Todas as Notas', count:mvpNotesAllCount()},
    {id:'unfiled', name:'Sem pasta', count:mvpNotesUnfiledCount()},
    {id:'done', name:'Concluído', count:mvpNotesDoneCount()}
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
// Trocar de pasta/visão preserva busca e filtros — só re-renderiza a lista; a mesma
// proteção de rascunho não salvo das demais ações de pasta se aplica aqui. Em mobile,
// escolher uma pasta avança a navegação em camadas para a Lista (estágio B).
function mvpNotesSwitchFolder(target){
  mvpNotesConfirmDiscardIfDirty(()=>{
    mvpNotesUI.activeFolder=target;
    mvpNotesUI.stage='list';
    renderMvpNotesMode('list');
  });
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
// ---- navegação mobile em camadas (Pastas → Lista → Editor) ----
// Um único DOM para os dois mundos: em desktop a sidebar e o conteúdo convivem lado a
// lado e o atributo data-mobile-stage é ignorado pelo CSS; abaixo do breakpoint (760px,
// o mesmo já usado pelo módulo) o atributo decide qual camada ocupa a tela inteira.
function mvpNotesIsMobile(){ return window.matchMedia('(max-width:760px)').matches; }
function mvpNotesApplyStage(){
  const drawer=mvpn('mvpNotesDrawer'); if(!drawer) return;
  drawer.dataset.mobileStage=mvpNotesUI.stage;
  const backBtn=mvpn('mvpNotesBackBtn'), title=mvpn('mvpNotesTitle');
  if(mvpNotesIsMobile()){
    if(title) title.textContent=mvpNotesUI.stage==='folders'?'Notas do MVP'
      :(mvpNotesUI.stage==='list'?mvpNotesViewLabel():(mvpNotesUI.editingId?'Editar nota':'Nova nota'));
    if(backBtn){
      backBtn.hidden=mvpNotesUI.stage==='folders';
      backBtn.setAttribute('aria-label',mvpNotesUI.stage==='editor'?`Voltar para ${mvpNotesViewLabel()}`:'Voltar para pastas');
    }
  }else{
    if(title) title.textContent='Notas do MVP';
    if(backBtn) backBtn.hidden=true;
  }
}
// Voltar contextual: Editor → Lista (com proteção de rascunho sujo), Lista → Pastas.
// No estágio Pastas o botão não existe (fechar é o X, como em desktop).
function mvpNotesGoBack(){
  if(mvpNotesUI.mode==='editor'){ mvpNotesConfirmDiscardIfDirty(()=>renderMvpNotesMode('list')); return; }
  if(mvpNotesUI.stage==='list'){
    mvpNotesUI.stage='folders';
    mvpNotesSetFiltersSheetOpen(false);
    mvpNotesApplyStage();
    const nav=mvpn('mvpNotesFolderNavList');
    const current=nav?nav.querySelector('[aria-current="page"]')||nav.querySelector('button'):null;
    if(current) current.focus();
  }
}
// ---- bottom sheet de filtros (mobile) ----
function mvpNotesSetFiltersSheetOpen(open){
  mvpNotesUI.filtersSheetOpen=open;
  const wrap=mvpn('mvpNotesFiltersWrap'), btn=mvpn('mvpNotesFiltersBtn');
  if(wrap) wrap.classList.toggle('open',open);
  if(btn) btn.setAttribute('aria-expanded',String(open));
  if(open){ const first=wrap?wrap.querySelector('select:not([hidden])'):null; if(first) first.focus(); }
  else if(btn && mvpNotesIsMobile() && document.activeElement && wrap && wrap.contains(document.activeElement)) btn.focus();
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
  // Trace ID somente leitura: exibido como texto, nunca como campo editável — o código é
  // atribuído pelo sistema e imutável. Em nota nova ainda não existe (nasce ao salvar).
  const traceRow=isNew
    ? `<div class="mvpn-trace-row"><span class="mvpn-trace-label">Trace ID</span><span class="mvpn-trace-pending">atribuído ao salvar</span></div>`
    : `<div class="mvpn-trace-row">
        <span class="mvpn-trace-label">Trace ID</span>
        <code class="mvpn-trace-code" id="mvpNoteTicket">${esc(meta.ticket||'')}</code>
        <button type="button" class="mvpn-card-copy mvpn-trace-copy" data-mvp-copy-id="${esc(mvpNotesUI.editingId||'')}"
          title="Copiar referência ${esc(meta.ticket||'')} para colar num agente de IA"
          aria-label="Copiar referência da nota ${esc(meta.ticket||'')}">
          <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/></svg>
          <span class="mvpn-copy-check" aria-hidden="true">✓</span>
        </button>
      </div>`;
  return `
    <div class="mvpn-editor-head">
      <h3>${isNew?'Nova nota':'Editar nota'}</h3>
      <button type="button" class="mvpn-editor-back reset-btn" id="mvpNoteCancelBtn">${isNew?'Cancelar':'Voltar à lista'}</button>
    </div>
    ${traceRow}
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
      ${meta.completedAt?`<dt>Concluída em</dt><dd>${esc(mvpNotesFormatDate(meta.completedAt))}</dd>`:''}
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
  // Copiar no editor: age só sobre a área de transferência — não salva, não altera a nota
  // e, portanto, não move updatedAt.
  const editorCopy=document.querySelector('.mvpn-trace-copy[data-mvp-copy-id]');
  if(editorCopy) editorCopy.addEventListener('click',()=>mvpNotesHandleCopy(editorCopy.dataset.mvpCopyId,editorCopy));
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
  // Nova nota dentro de uma pasta específica herda essa pasta; nas visões virtuais
  // ("Todas as Notas", "Sem pasta", "Concluído") o padrão é null — o operador escolhe no
  // editor. Criar a partir de "Concluído" NUNCA nasce concluída: status inicial é sempre
  // 'open' (Concluído não é destino de criação, é visão derivada).
  const defaultFolderId=(mvpNotesUI.activeFolder!=='all' && mvpNotesUI.activeFolder!=='unfiled' && mvpNotesUI.activeFolder!=='done') ? mvpNotesUI.activeFolder : null;
  mvpNotesUI.draft=isNew ? {type:'task', title:'', description:'', priority:'medium', status:'open', folderId:defaultFolderId} : mvpNotesDraftFromItem(item);
  mvpNotesUI.draftOriginal={...mvpNotesUI.draft};
  mvpNotesUI.draftDirty=false;
  mvpNotesUI.draftMeta=isNew
    ? {screenId:mvpNotesCurrentScreenId(), buildId:mvpNotesCurrentBuildId(), createdAt:'', updatedAt:'', completedAt:'', ticket:''}
    : {screenId:item.screenId, buildId:item.buildId, createdAt:item.createdAt, updatedAt:item.updatedAt, completedAt:item.completedAt||'', ticket:item.ticket||''};
  renderMvpNotesMode('editor');
}
function renderMvpNotesMode(mode){
  mvpNotesUI.mode=mode;
  const toolbar=mvpn('mvpNotesToolbar'), list=mvpn('mvpNotesList'), editor=mvpn('mvpNotesEditor');
  if(mode==='editor'){
    mvpNotesUI.stage='editor';
    mvpNotesSetFiltersSheetOpen(false);
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
    // Saída do editor volta ao estágio Lista; o estágio Pastas só é alcançado pelo botão
    // voltar (mvpNotesGoBack) ou na abertura do drawer em mobile.
    if(mvpNotesUI.stage==='editor') mvpNotesUI.stage='list';
    if(toolbar) toolbar.hidden=false;
    if(list){ list.hidden=false; renderMvpNotesList(); }
    if(editor){ editor.hidden=true; editor.innerHTML=''; }
    mvpNotesUI.editingId=null; mvpNotesUI.draft=null; mvpNotesUI.draftOriginal=null; mvpNotesUI.draftDirty=false;
  }
  mvpNotesApplyStage();
}
function mvpNotesConfirmDiscardIfDirty(proceed){
  if(mvpNotesUI.mode==='editor' && mvpNotesUI.draftDirty){
    if(!confirm('Existem alterações não salvas nesta nota. Deseja descartá-las?')) return;
  }
  proceed();
}

// ---- resize horizontal do drawer (desktop) ----
// O drawer permanece ancorado à direita (right:0); arrastar a borda esquerda muda só a
// largura, via variável CSS --mvpn-drawer-w no próprio elemento. Durante o gesto
// (pointermove) apenas o visual muda; save() acontece UMA vez, no fim (pointerup) —
// nunca a cada pixel. Abaixo do breakpoint mobile o handle não existe visualmente (CSS)
// e todos os handlers saem cedo: drawerWidth não governa a geometria mobile.
// Faixa canônica vem de 00-core/04-persistence.js (MVP_NOTES_DRAWER_MIN/MAX/DEFAULT) —
// não há segunda definição destes números. MVPN_DRAWER_WIDE é só o alvo do duplo clique.
const MVPN_DRAWER_WIDE=760;
// Máximo EFETIVO desta janela: nunca acima do máximo canônico, e ainda limitado a 80vw
// para o drawer jamais tomar a tela inteira em monitores estreitos. É um teto de
// renderização/gesto — não reescreve a preferência guardada (ver mvpNotesApplyDrawerWidth).
function mvpNotesDrawerMax(){ return Math.max(MVP_NOTES_DRAWER_MIN, Math.min(Math.round(window.innerWidth*0.8), MVP_NOTES_DRAWER_MAX)); }
function mvpNotesDrawerWidth(){
  const w=(S.mvpNotes && S.mvpNotes.ui) ? Number(S.mvpNotes.ui.drawerWidth) : NaN;
  return Number.isFinite(w)?w:MVP_NOTES_DRAWER_DEFAULT;
}
function mvpNotesClampWidth(w){ return Math.min(Math.max(Math.round(w),MVP_NOTES_DRAWER_MIN),mvpNotesDrawerMax()); }
// Guarda de persistência: o que vai ao estado respeita SÓ a faixa canônica (420–900),
// independente do tamanho da janela atual — abrir o painel num notebook estreito não pode
// encolher para sempre a largura escolhida num monitor grande.
function mvpNotesClampPersistable(w){ return Math.min(Math.max(Math.round(w),MVP_NOTES_DRAWER_MIN),MVP_NOTES_DRAWER_MAX); }
function mvpNotesApplyDrawerWidth(w){
  const d=mvpn('mvpNotesDrawer'); if(d) d.style.setProperty('--mvpn-drawer-w',w+'px');
  const h=mvpn('mvpNotesResizeHandle');
  if(h){
    h.setAttribute('aria-valuemin',String(MVP_NOTES_DRAWER_MIN));
    h.setAttribute('aria-valuemax',String(mvpNotesDrawerMax())); // teto efetivo desta janela
    h.setAttribute('aria-valuenow',String(w));
    h.setAttribute('aria-valuetext',`${w} pixels de largura`);
  }
}
function mvpNotesPersistDrawerWidth(w){
  if(!S.mvpNotes.ui || typeof S.mvpNotes.ui!=='object') S.mvpNotes.ui={};
  const v=mvpNotesClampPersistable(w); // estado nunca recebe valor fora da faixa canônica
  if(S.mvpNotes.ui.drawerWidth===v) return;
  S.mvpNotes.ui.drawerWidth=v;
  save();
}
function bindMvpNotesResize(){
  const h=mvpn('mvpNotesResizeHandle'); if(!h) return;
  h.addEventListener('pointerdown',e=>{
    if(mvpNotesIsMobile()) return;
    e.preventDefault();
    try{ h.setPointerCapture(e.pointerId); }catch(_){}
    mvpNotesUI.resize={startX:e.clientX, startW:mvpNotesClampWidth(mvpNotesDrawerWidth())};
  });
  h.addEventListener('pointermove',e=>{
    if(!mvpNotesUI.resize) return;
    mvpNotesApplyDrawerWidth(mvpNotesClampWidth(mvpNotesUI.resize.startW+(mvpNotesUI.resize.startX-e.clientX)));
  });
  h.addEventListener('pointerup',e=>{
    if(!mvpNotesUI.resize) return;
    const w=mvpNotesClampWidth(mvpNotesUI.resize.startW+(mvpNotesUI.resize.startX-e.clientX));
    mvpNotesUI.resize=null;
    mvpNotesApplyDrawerWidth(w);
    mvpNotesPersistDrawerWidth(w);
  });
  h.addEventListener('pointercancel',()=>{
    if(!mvpNotesUI.resize) return;
    mvpNotesUI.resize=null;
    mvpNotesApplyDrawerWidth(mvpNotesClampWidth(mvpNotesDrawerWidth())); // volta à última largura persistida
  });
  // Duplo clique alterna padrão ↔ ampliada (460 ↔ 760, sempre dentro dos limites vivos).
  h.addEventListener('dblclick',()=>{
    if(mvpNotesIsMobile()) return;
    const cur=mvpNotesClampWidth(mvpNotesDrawerWidth());
    const target=mvpNotesClampWidth(cur<MVPN_DRAWER_WIDE?MVPN_DRAWER_WIDE:MVP_NOTES_DRAWER_DEFAULT);
    mvpNotesApplyDrawerWidth(target);
    mvpNotesPersistDrawerWidth(target);
  });
  // Teclado: ← alarga (a borda esquerda anda para a esquerda), → estreita; Shift triplica
  // o passo. Cada tecla é um ajuste discreto — persistir por tecla é barato e correto.
  h.addEventListener('keydown',e=>{
    if(mvpNotesIsMobile()) return;
    const step=e.shiftKey?60:20;
    let w=null;
    if(e.key==='ArrowLeft') w=mvpNotesClampWidth(mvpNotesClampWidth(mvpNotesDrawerWidth())+step);
    else if(e.key==='ArrowRight') w=mvpNotesClampWidth(mvpNotesClampWidth(mvpNotesDrawerWidth())-step);
    else if(e.key==='Home') w=MVP_NOTES_DRAWER_MIN;
    else if(e.key==='End') w=mvpNotesDrawerMax();
    if(w===null) return;
    e.preventDefault();
    mvpNotesApplyDrawerWidth(w);
    mvpNotesPersistDrawerWidth(w);
  });
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
  mvpNotesUI.filterFolder='all'; mvpNotesUI.filterPeriod='all';
  mvpNotesUI.activeFolder='all'; // cada abertura começa em "Todas as Notas", mesmo padrão dos filtros
  // Mobile abre no estágio Pastas (navegação em camadas, Estado A); desktop mostra tudo
  // lado a lado — o estágio fica em 'list' e o CSS o ignora acima do breakpoint.
  mvpNotesUI.stage=mvpNotesIsMobile()?'folders':'list';
  mvpNotesSetFiltersSheetOpen(false);
  mvpNotesApplyDrawerWidth(mvpNotesClampWidth(mvpNotesDrawerWidth())); // largura lembrada (desktop)
  const search=mvpn('mvpNotesSearch'); if(search) search.value='';
  ['mvpNotesFilterType','mvpNotesFilterStatus','mvpNotesFilterPriority','mvpNotesFilterFolder','mvpNotesFilterPeriod'].forEach(id=>{ const el=mvpn(id); if(el) el.value='all'; });
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
  const folderFilter=mvpn('mvpNotesFilterFolder');
  if(folderFilter) folderFilter.addEventListener('change',e=>{ mvpNotesUI.filterFolder=e.target.value; renderMvpNotesList(); });
  const periodFilter=mvpn('mvpNotesFilterPeriod');
  if(periodFilter) periodFilter.addEventListener('change',e=>{ mvpNotesUI.filterPeriod=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesNewFolderBtn').addEventListener('click',mvpNotesHandleNewFolder);
  const backBtn=mvpn('mvpNotesBackBtn');
  if(backBtn) backBtn.addEventListener('click',mvpNotesGoBack);
  const filtersBtn=mvpn('mvpNotesFiltersBtn');
  if(filtersBtn) filtersBtn.addEventListener('click',()=>mvpNotesSetFiltersSheetOpen(!mvpNotesUI.filtersSheetOpen));
  const applyBtn=mvpn('mvpNotesFiltersApplyBtn');
  if(applyBtn) applyBtn.addEventListener('click',()=>mvpNotesSetFiltersSheetOpen(false)); // filtros aplicam ao vivo; Aplicar = fechar a folha
  const clearBtn=mvpn('mvpNotesFiltersClearBtn');
  if(clearBtn) clearBtn.addEventListener('click',()=>{
    mvpNotesUI.filterType='all'; mvpNotesUI.filterStatus='all'; mvpNotesUI.filterPriority='all';
    mvpNotesUI.filterFolder='all'; mvpNotesUI.filterPeriod='all';
    ['mvpNotesFilterType','mvpNotesFilterStatus','mvpNotesFilterPriority','mvpNotesFilterFolder','mvpNotesFilterPeriod'].forEach(id=>{ const el=mvpn(id); if(el) el.value='all'; });
    renderMvpNotesList();
  });
  bindMvpNotesResize();
  document.addEventListener('keydown',event=>{
    if(!mvpNotesUI.open) return;
    if(event.key==='Escape'){
      event.preventDefault();
      if(mvpNotesUI.filtersSheetOpen){ mvpNotesSetFiltersSheetOpen(false); return; }
      if(mvpNotesUI.mode==='editor'){ mvpNotesConfirmDiscardIfDirty(()=>renderMvpNotesMode('list')); return; }
      if(mvpNotesIsMobile() && mvpNotesUI.stage==='list'){ mvpNotesGoBack(); return; } // espelha o botão voltar
      closeMvpNotesDrawer();
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
