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

const MVP_NOTES_POLICY_LABELS={blocked:'Bloqueada', analysis_only:'Somente análise', autonomous_allowed:'Implementação autorizada'};
// Instrução que fecha o Trace Reference, dependente da política. NENHUMA delas autoriza
// commit, push, merge ou deploy — isso segue governado pelo processo do projeto.
const MVP_NOTES_POLICY_INSTRUCTION={
  blocked:'Esta nota está BLOQUEADA para implementação por IA.\nNão altere código com base nesta nota.\nVocê pode apenas reportar que a implementação está bloqueada.',
  analysis_only:'Esta nota permite SOMENTE ANÁLISE.\nVocê pode investigar, reproduzir, diagnosticar e propor um plano.\nNão altere código.',
  autonomous_allowed:'Esta nota AUTORIZA IMPLEMENTAÇÃO TÉCNICA dentro do escopo descrito.\nAntes de alterar:\n1. confirme o contexto;\n2. reproduza;\n3. determine causa raiz;\n4. limite alterações ao ticket.\n\nEsta autorização NÃO inclui commit, push, merge ou deploy.'
};
// Explicação curta exibida no inspector — legível sem depender de cor.
const MVP_NOTES_POLICY_HINT={
  blocked:'A IA não está autorizada a implementar esta nota.',
  analysis_only:'A IA pode investigar, reproduzir, diagnosticar e propor solução, mas não alterar o código automaticamente.',
  autonomous_allowed:'A IA pode implementar tecnicamente esta nota dentro do escopo descrito. Isso NÃO autoriza commit, push, merge ou deploy — essas ações continuam exigindo autorização separada.'
};

const mvpNotesUI={
  open:false, selectedId:null,              // nota aberta no painel do editor
  draft:null, draftOriginal:null, draftDirty:false,
  query:'', filterType:'all', filterStatus:'all', filterPriority:'all',
  filterFolder:'all', filterPeriod:'all', filterPolicy:'all',
  activeFolder:'all', // 'all' | 'unfiled' | 'done' | id de pasta — visões virtuais nunca persistidas
  stage:'folders',    // navegação mobile em camadas: 'folders' | 'list' | 'editor' (desktop ignora)
  filtersOpen:false, inspectorOpen:false,
  opener:null, optionsReady:false, inertSnapshot:null,
  resize:null, paneResize:null, folderDrag:null,        // gesto em andamento {kind,startX,startW} — só persiste no pointerup
  dragFolderId:null   // pasta sendo arrastada na reordenação manual
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
// Ordenação natural (numeric-aware): "Bug 2" vem antes de "Bug 10", e acentuação/caixa
// não separam palavras iguais. É a ordem única das notas — elas não são arrastáveis.
function mvpNotesCompareNatural(a,b){
  return String(a.title||'').localeCompare(String(b.title||''),'pt-BR',{numeric:true,sensitivity:'base'});
}
function mvpNotesHaystack(item){
  // O ticket entra na busca: colar de volta o código copiado (JPW-XXXXXX) localiza a nota
  // — é o caminho de volta do agente de IA para o app. content cobre título e corpo,
  // já que o título é a primeira linha dele.
  return [item.ticket, item.content, MVP_NOTES_TYPE_LABELS[item.type], MVP_NOTES_STATUS_LABELS[item.status],
    MVP_NOTES_PRIORITY_LABELS[item.priority], MVP_NOTES_POLICY_LABELS[item.aiImplementationPolicy],
    mvpNotesScreenLabel(item.screenId), item.buildId, item.sourceRevision||'',
    mvpNotesFolderLabel(item.folderId)].join(' ').toLocaleLowerCase('pt-BR');
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
// ---- exportação individual em Markdown (JPW-9A78DE) --------------------------------
// Complementa — não substitui — o backup completo, a exportação da base e o Trace
// Reference. É uma cópia PORTÁTIL de uma nota, gerada no próprio navegador (Blob +
// <a download>, o mesmo mecanismo de exportFullBackup), sem backend, API ou servidor.
//
// Nada aqui escreve no estado: exportar é operação de leitura pura.
// Front matter só com metadados que EXISTEM no item — nenhum campo inventado.
function mvpNotesMarkdownSlug(texto){
  return String(texto||'')
    .normalize('NFD').replace(/[\u0300-\u036f]/g,'')   // acentos fora do nome do arquivo
    .toLowerCase()
    .replace(/[^a-z0-9]+/g,'-')                         // qualquer caractere inválido vira hífen
    .replace(/^-+|-+$/g,'')
    .slice(0,60).replace(/-+$/,'');
}
function mvpNotesMarkdownFilename(item){
  const slug=mvpNotesMarkdownSlug(item.title);
  return `${item.ticket||'JPW-NOTA'}-${slug||'nota'}.md`;
}
// Serialização de UM escalar de front matter. Função central: todo valor do YAML passa
// por aqui, nenhum é concatenado à mão.
//
// O estilo de aspas SIMPLES é escolha deliberada: seu único mecanismo de escape é dobrar
// a própria aspa (''), então dois-pontos, aspas duplas, barra invertida, &, #, [ ] { }
// e afins entram literalmente. Com aspas duplas seria preciso escapar barra invertida —
// uma pasta chamada "C:\temp" viraria "C:<TAB>emp", porque \t é tabulação no estilo duplo.
// O estilo simples elimina essa classe de corrupção sem biblioteca externa.
const MVPN_YAML_RESERVADO=/^(?:true|false|null|yes|no|on|off|y|n|~)$/i;
function mvpNotesYamlValor(v){
  if(v===null || v===undefined || v==='') return 'null';
  // Controles (quebra, tabulação, etc.) viram espaço: um escalar de front matter é uma linha.
  const t=String(v).replace(/[\u0000-\u001f\u007f]/g,' ').trim();
  if(t==='') return 'null';
  // Estilo simples (sem aspas) só para tokens inequívocos: começam por letra, não contêm
  // indicador YAML algum e não colidem com booleano/nulo. Qualquer outra coisa é citada —
  // inclusive números e datas, que sem aspas mudariam de tipo na leitura.
  if(/^[A-Za-z][A-Za-z0-9._-]*$/.test(t) && !MVPN_YAML_RESERVADO.test(t)) return t;
  return "'"+t.replace(/'/g,"''")+"'";
}
// A primeira linha da nota é o TÍTULO DO DOCUMENTO, então o arquivo exportado sempre
// abre com um único H1 — nunca com H2..H6. Se o operador escreveu o título já em sintaxe
// de heading, o marcador é removido e o texto vira o H1; qualquer outro texto recebe o
// prefixo "# ".
//
// Só conta como heading ATX válido: de 1 a 6 "#" SEGUIDOS DE ESPAÇO. Por isso
// "#SemEspaco" e "####### Sete" (sete marcadores não é heading) entram como texto do H1,
// exatamente como aparecem no título da nota.
//
// Isto é normalização de EXPORTAÇÃO: o title persistido não é tocado — uma nota cujo
// título é "## Exportar notas" continua com esse title na aplicação.
function mvpNotesMarkdownHeading(titulo){
  const t=String(titulo||'').trim();
  if(!t) return '';
  const m=t.match(/^#{1,6}\s+(\S.*)$/);
  return `# ${m?m[1].trim():t}`;
}
function mvpNotesMarkdown(item){
  const linhas=String(item.content||'').split('\n');
  const iTitulo=linhas.findIndex(l=>l.trim());
  // O título vira o cabeçalho H1; o corpo é o restante, sem repetir a primeira linha.
  const corpo=iTitulo<0?'':linhas.slice(iTitulo+1).join('\n').replace(/^\n+/,'');
  const fm=[
    'ticket: '+mvpNotesYamlValor(item.ticket),
    'type: '+mvpNotesYamlValor(MVP_NOTES_TYPE_LABELS[item.type]||item.type),
    'priority: '+mvpNotesYamlValor(MVP_NOTES_PRIORITY_LABELS[item.priority]||item.priority),
    'status: '+mvpNotesYamlValor(MVP_NOTES_STATUS_LABELS[item.status]||item.status),
    'folder: '+mvpNotesYamlValor(mvpNotesFolderLabel(item.folderId)),
    'ai_implementation_policy: '+mvpNotesYamlValor(item.aiImplementationPolicy),
    'screen: '+mvpNotesYamlValor(mvpNotesScreenLabel(item.screenId)),
    'build_id: '+mvpNotesYamlValor(item.buildId),
    // Source Revision segue a regra do módulo: não existe mecanismo confiável hoje, então
    // é null — jamais um SHA inventado a partir do build id.
    'source_revision: '+mvpNotesYamlValor(mvpNotesSourceRevision(item)),
    'created_at: '+mvpNotesYamlValor(item.createdAt),
    'updated_at: '+mvpNotesYamlValor(item.updatedAt),
    'completed_at: '+mvpNotesYamlValor(item.completedAt)
  ];
  // O título já pode vir escrito em Markdown pelo operador ("# Meu título"). Prefixar
  // outro "#" produziria "# # Meu título". A normalização vive AQUI, no gerador — a regra
  // do título interno da aplicação (primeira linha não vazia, literal) fica intocada.
  const titulo=item.title?mvpNotesMarkdownHeading(item.title):'';
  return ['---',...fm,'---','',titulo,'',corpo].join('\n').replace(/\n{3,}$/,'\n')+'\n';
}
// Rascunho sujo NÃO é exportado: um arquivo com metadados do estado salvo e corpo do
// rascunho seria uma combinação ambígua, e rastreabilidade não admite ambiguidade.
// Também não salvamos por conta própria — a decisão de gravar é sempre do operador.
function mvpNotesExportMarkdown(){
  const item=mvpNotesUI.selectedId?mvpNotesItems().find(i=>i.id===mvpNotesUI.selectedId):null;
  const live=mvpn('mvpNotesExportLive');
  if(!item){ if(live) live.textContent='Nenhuma nota selecionada para exportar.'; return null; }
  if(mvpNotesUI.draftDirty){
    alert('Existem alterações não salvas. Salve a nota antes de exportar.');
    if(live) live.textContent='Existem alterações não salvas. Salve a nota antes de exportar.';
    return null;
  }
  const nome=mvpNotesMarkdownFilename(item);
  const blob=new Blob([mvpNotesMarkdown(item)],{type:'text/markdown;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url;
  a.download=nome;
  a.rel='noopener';
  a.style.display='none';
  document.body.appendChild(a);
  a.click();
  // Revogar na volta ao laço de eventos, não na linha seguinte ao clique: alguns
  // navegadores ainda não leram o Blob nesse instante e o download sairia vazio.
  // A âncora temporária sai do DOM junto — não fica lixo pendurado no documento.
  setTimeout(()=>{ URL.revokeObjectURL(url); if(a.parentNode) a.remove(); },0);
  if(live) live.textContent='Nota exportada como Markdown.';
  return nome;
}
function mvpNotesReferenceBlock(item){
  const rev=mvpNotesSourceRevision(item);
  const L=[
    'JP WEALTH — TRACE REFERENCE','',
    `Ticket: ${item.ticket}`,
    `Tipo: ${MVP_NOTES_TYPE_LABELS[item.type]||item.type}`,
    `Prioridade: ${MVP_NOTES_PRIORITY_LABELS[item.priority]||item.priority}`,
    `Status: ${MVP_NOTES_STATUS_LABELS[item.status]||item.status}`,
    `Autorização IA: ${(MVP_NOTES_POLICY_LABELS[item.aiImplementationPolicy]||'').toLocaleUpperCase('pt-BR')}`,'',
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
  L.push('','CONTEÚDO DA NOTA:','', String(item.content||'').trim()||'(sem conteúdo)');
  // A instrução final depende da política de IA da nota: bloqueada, somente análise ou
  // implementação autorizada — cada uma com seu texto próprio (nunca a lista genérica).
  L.push('','INSTRUÇÃO AO AGENTE','',
    `Investigue exclusivamente o problema associado ao ticket ${item.ticket}.`,'',
    MVP_NOTES_POLICY_INSTRUCTION[item.aiImplementationPolicy]||MVP_NOTES_POLICY_INSTRUCTION.analysis_only);
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
// v5: concluídas NÃO saem mais da pasta de origem. Toda visão devolve a lista completa
// que lhe pertence; o agrupamento Ativas/Concluídas é feito no render (mvpNotesGrouped).
function mvpNotesFiltered(){
  const q=mvpNotesUI.query.trim().toLocaleLowerCase('pt-BR');
  const doneView=mvpNotesIsDoneView();
  return mvpNotesItems().filter(item=>{
    if(doneView){
      // Visão global do sistema: derivada só do status — folderId permanece intocado.
      if(item.status!=='done') return false;
      if(!mvpNotesCompletedWithinPeriod(item,mvpNotesUI.filterPeriod)) return false;
    }else if(mvpNotesUI.activeFolder==='unfiled'){
      if(item.folderId!==null) return false;
    }else if(mvpNotesUI.activeFolder==='all'){
      // "Todas as Notas" é o backlog ATIVO de todas as pastas — concluída sai daqui e
      // vive na visão "Concluído" (e continua dentro da própria pasta, ao pé da lista).
      // O dado não muda: status, folderId e completedAt seguem intocados.
      if(item.status==='done') return false;
    }else{
      if(item.folderId!==mvpNotesUI.activeFolder) return false;
    }
    // Filtro de pasta agora vale em qualquer visão (não só em Concluídas).
    if(mvpNotesUI.filterFolder!=='all'){
      if(mvpNotesUI.filterFolder==='unfiled'){ if(item.folderId!==null) return false; }
      else if(item.folderId!==mvpNotesUI.filterFolder) return false;
    }
    if(mvpNotesUI.filterStatus!=='all' && item.status!==mvpNotesUI.filterStatus) return false;
    if(mvpNotesUI.filterType!=='all' && item.type!==mvpNotesUI.filterType) return false;
    if(mvpNotesUI.filterPriority!=='all' && item.priority!==mvpNotesUI.filterPriority) return false;
    if(mvpNotesUI.filterPolicy!=='all' && item.aiImplementationPolicy!==mvpNotesUI.filterPolicy) return false;
    if(q && !mvpNotesHaystack(item).includes(q)) return false;
    return true;
  });
}
// Dois grupos, cada um em ordem natural crescente: as ativas primeiro, as concluídas
// depois do separador. A concluída continua na pasta de origem — só recua visualmente.
function mvpNotesGrouped(){
  const todas=mvpNotesFiltered();
  return {
    ativas: todas.filter(i=>i.status!=='done').sort(mvpNotesCompareNatural),
    concluidas: todas.filter(i=>i.status==='done').sort(mvpNotesCompareNatural)
  };
}
// Contagem de filtros ativos ("Filtros · N") — a busca não conta como filtro.
function mvpNotesActiveFilterCount(){
  let n=0;
  if(mvpNotesUI.filterType!=='all') n++;
  if(mvpNotesUI.filterPriority!=='all') n++;
  if(mvpNotesUI.filterPolicy!=='all') n++;
  if(mvpNotesUI.filterFolder!=='all') n++;
  if(mvpNotesIsDoneView()){
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
// "Todas as Notas" também conta só o backlog ativo; "Concluído" conta status==='done'.
function mvpNotesFolderItemCount(folderId){ return mvpNotesItems().filter(it=>it.folderId===folderId && it.status!=='done').length; }
function mvpNotesUnfiledCount(){ return mvpNotesItems().filter(it=>it.folderId===null && it.status!=='done').length; }
// Conta o mesmo que a visão exibe: só o backlog ativo. Antes contava literalmente tudo,
// o que agora divergiria da lista — mesma convenção já usada por "Sem pasta" e pelas pastas.
function mvpNotesAllCount(){ return mvpNotesItems().filter(it=>it.status!=='done').length; }
function mvpNotesFolderNameExists(name,excludeId){
  const n=name.trim().toLocaleLowerCase('pt-BR');
  return mvpNotesFolders().some(f=>f.id!==excludeId && f.name.toLocaleLowerCase('pt-BR')===n);
}
// ---- ordem manual das pastas (Fase E) ---------------------------------------------
// PASTAS têm ordem MANUAL (folder.position); NOTAS têm ordem NATURAL (título derivado).
// São semânticas diferentes e não se misturam em lugar nenhum.
//
// Fonte da verdade é sempre o estado: folders[] mantido na sequência escolhida, com
// position 0..n-1 contígua. O DOM é projeção disso — no drop lemos a sequência desejada,
// escrevemos no estado e re-renderizamos A PARTIR do estado (nunca o inverso).
// A normalização de carga (mvpNotesNormalizeFolders, 04-persistence.js) já garante
// posições únicas, inteiras e contíguas; aqui mantemos essa invariante viva em sessão.
function mvpNotesFoldersOrdered(){
  return mvpNotesFolders()
    .map((f,i)=>({f, i, p:Number.isFinite(Number(f.position))?Number(f.position):Number.MAX_SAFE_INTEGER}))
    .sort((a,b)=> a.p-b.p || a.i-b.i)   // desempate: ordem original do array
    .map(x=>x.f);
}
// Reescreve folders[] na ordem canônica e renumera 0..n-1. Depois disto, índice do array
// e position são a mesma coisa — o resto do módulo pode confiar na ordem do array.
function mvpNotesRenumberFolders(){
  const ordenadas=mvpNotesFoldersOrdered();
  ordenadas.forEach((f,i)=>{ f.position=i; });
  S.mvpNotes.folders=ordenadas;
  return ordenadas;
}
function mvpNotesFolderIndex(id){ return mvpNotesFoldersOrdered().findIndex(f=>f.id===id); }
// OPERAÇÃO CENTRAL — arraste, "Mover para cima" e "Mover para baixo" passam todos por aqui.
// Move a pasta `folderId` para `newIndex` (0-based, entre as pastas REAIS). Devolve true se
// algo mudou. Não toca em nota alguma, não muda a pasta ativa nem o rascunho.
function mvpNotesMoveFolder(folderId,newIndex){
  const lista=mvpNotesRenumberFolders();          // parte de um estado canônico
  const atual=lista.findIndex(f=>f.id===folderId);
  if(atual<0) return false;                        // pasta inexistente: ignora em silêncio
  const alvo=Math.min(Math.max(Math.round(Number(newIndex)),0),lista.length-1);
  if(!Number.isFinite(alvo) || alvo===atual) return false; // nada a fazer: nem save, nem anúncio
  const [movida]=lista.splice(atual,1);
  lista.splice(alvo,0,movida);
  lista.forEach((f,i)=>{ f.position=i; });
  S.mvpNotes.folders=lista;
  // folder.updatedAt NÃO se move aqui. Neste módulo esse carimbo significa "o conteúdo da
  // pasta mudou" — mvpNotesRenameFolder só o toca quando o nome realmente muda. Reordenar
  // é organização visual, não alteração da pasta. Nenhum timestamp de NOTA é tocado.
  save();
  mvpNotesRefreshFolderOrderViews();
  mvpNotesAnnounceFolderOrder(movida,alvo,lista.length);
  return true;
}
// Superfícies que exibem a ordem das pastas. Deliberadamente NÃO re-renderiza a lista de
// notas: reordenar pastas não altera resultado de busca, filtro, nota aberta nem rascunho.
function mvpNotesRefreshFolderOrderViews(){
  renderMvpNotesFolderNav();
  mvpNotesSyncFilterControls();        // select Pasta dos filtros segue a ordem manual
  mvpNotesSyncInspectorFolderOptions();// select Pasta do inspector idem, sem roubar foco
  renderMvpNotesHeader();
}
// Reconstrói apenas as opções de pasta do inspector, preservando a escolha do rascunho.
// Rebuild pontual em vez de re-render do inspector inteiro: não mexe no foco nem no draft.
function mvpNotesSyncInspectorFolderOptions(){
  const sel=mvpn('mvpNoteFolder'), d=mvpNotesUI.draft;
  if(!sel || !d) return;
  sel.innerHTML=`<option value="">Sem pasta</option>`
    +mvpNotesFoldersOrdered().map(f=>`<option value="${esc(f.id)}">${esc(f.name)}</option>`).join('');
  sel.value=d.folderId||'';
}
// Anúncio acessível — mover pasta não pode ser um evento só visual (o menu "⋯" é a via de
// teclado, e quem o usa precisa ouvir o resultado). Posições em base 1, como se lê na tela.
function mvpNotesAnnounceFolderOrder(folder,index,total){
  const live=mvpn('mvpNotesOrderLive');
  if(live) live.textContent=`Pasta ${folder.name} movida para a posição ${index+1} de ${total}.`;
}
function mvpNotesCreateFolder(name){
  const now=new Date().toISOString();
  // Nova pasta entra no FIM da lista — nunca reordena as existentes nem ordena alfabeticamente.
  const folder={id:mvpNotesFolderId(), name, position:mvpNotesFolders().length, createdAt:now, updatedAt:now};
  S.mvpNotes.folders.push(folder);
  mvpNotesRenumberFolders(); // garante contiguidade mesmo se o estado vier de backup antigo
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
  mvpNotesRenumberFolders(); // sobrou buraco na sequência: renumera as restantes (0..n-1)
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
  const content=String(draft.content||'').slice(0,20000);
  const item={
    id, ticket:mvpNotesResolveTicket(null,id,seenTickets),
    type:draft.type,
    content, title:mvpNotesDeriveTitle(content), // título sempre derivado, nunca digitado
    aiImplementationPolicy:MVP_NOTES_AI_POLICIES.includes(draft.aiImplementationPolicy)?draft.aiImplementationPolicy:MVP_NOTES_AI_POLICY_DEFAULT,
    priority:draft.priority, status:draft.status, folderId:draft.folderId||null,
    screenId:mvpNotesCurrentScreenId(), buildId:mvpNotesCurrentBuildId(),
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
  const content=String(draft.content||'').slice(0,20000);
  const policy=MVP_NOTES_AI_POLICIES.includes(draft.aiImplementationPolicy)?draft.aiImplementationPolicy:item.aiImplementationPolicy;
  const changed=item.type!==draft.type || item.content!==content ||
    item.priority!==draft.priority || item.status!==draft.status || (item.folderId||null)!==folderId ||
    item.aiImplementationPolicy!==policy;
  // Carimbo de conclusão: entra em 'done' → agora; sai de 'done' → null (reabrir zera o
  // histórico; concluir de novo gera carimbo novo); permanece em 'done' → intocado.
  // folderId NUNCA é alterado por transição de status — a visão Concluído é derivada,
  // e reabrir devolve a nota à pasta original automaticamente porque ela nunca saiu de lá.
  if(item.status!=='done' && draft.status==='done') item.completedAt=new Date().toISOString();
  else if(item.status==='done' && draft.status!=='done') item.completedAt=null;
  item.type=draft.type;
  item.content=content; item.title=mvpNotesDeriveTitle(content); // título rederivado a cada gravação
  item.aiImplementationPolicy=policy;
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
  fillFilter('mvpNotesFilterPolicy',MVP_NOTES_POLICY_LABELS,'Qualquer autorização de IA');
  const period=mvpn('mvpNotesFilterPeriod');
  if(period) period.innerHTML=`<option value="all">Qualquer período</option><option value="7d">Concluídas nos últimos 7 dias</option><option value="30d">Concluídas nos últimos 30 dias</option>`;
  mvpNotesUI.optionsReady=true;
}

// ---- lista ----
// Card enxuto, estilo Apple Notes: título derivado + prévia do corpo + uma linha discreta
// de contexto. Tipo/prioridade/status e todo o resto vivem no inspector, não aqui.
function mvpNotesCardHTML(item){
  // Prévia = o corpo SEM a primeira linha (que já é o título) — repetir seria ruído.
  const corpo=String(item.content||'').split('\n');
  const iTitulo=corpo.findIndex(l=>l.trim());
  const preview=esc(corpo.slice(iTitulo+1).join(' ').replace(/\s+/g,' ').trim());
  // A pasta aparece só nas visões globais (Todas as Notas / Concluídas): dentro de uma
  // pasta repetir o próprio nome em cada card é redundante.
  const mostraPasta=mvpNotesUI.activeFolder==='all'||mvpNotesIsDoneView();
  const selecionada=mvpNotesUI.selectedId===item.id;
  // O card é um <button>; o botão de copiar é IRMÃO dele no invólucro — nunca aninhado
  // (HTML inválido). O clique no card abre a nota no painel do editor, à direita.
  return `<div class="mvpn-card-wrap">
    <button type="button" class="mvpn-card" data-mvp-note-id="${esc(item.id)}"
      data-status="${esc(item.status)}" data-priority="${esc(item.priority)}" data-type="${esc(item.type)}"
      ${selecionada?'aria-current="true"':''}>
      <div class="mvpn-card-title">${esc(item.title)}</div>
      ${preview?`<div class="mvpn-card-preview">${preview}</div>`:''}
      <div class="mvpn-card-meta">
        <span>${esc(mvpNotesFormatDate(item.status==='done'&&item.completedAt?item.completedAt:item.updatedAt))}</span>
        ${mostraPasta?`<span aria-hidden="true">·</span><span class="mvpn-card-folder">${esc(mvpNotesFolderLabel(item.folderId))}</span>`:''}
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
// Os filtros são os mesmos em toda visão; só "Período de conclusão" é exclusivo da visão
// Concluídas (nas demais o período não teria sentido). O contador aparece no botão.
function mvpNotesSyncFilterControls(){
  const done=mvpNotesIsDoneView();
  const periodSel=mvpn('mvpNotesFilterPeriod');
  if(periodSel){ periodSel.hidden=!done; periodSel.value=mvpNotesUI.filterPeriod; }
  // Na visão Concluídas o status é implícito (done) — o select some para não oferecer
  // combinações semanticamente absurdas ("Concluídas com status Aberta").
  const statusSel=mvpn('mvpNotesFilterStatus');
  if(statusSel){ statusSel.hidden=done; if(done){ mvpNotesUI.filterStatus='all'; statusSel.value='all'; } }
  const folderSel=mvpn('mvpNotesFilterFolder');
  if(folderSel){
    folderSel.innerHTML=`<option value="all">Todas as pastas</option><option value="unfiled">Sem pasta</option>`
      +mvpNotesFoldersOrdered().map(f=>`<option value="${esc(f.id)}">${esc(f.name)}</option>`).join('');
    folderSel.value=mvpNotesUI.filterFolder;
    if(folderSel.value!==mvpNotesUI.filterFolder){ mvpNotesUI.filterFolder='all'; folderSel.value='all'; } // pasta excluída depois de virar filtro
  }
  const n=mvpNotesActiveFilterCount();
  const badge=mvpn('mvpNotesFiltersCount');
  if(badge){ badge.hidden=n===0; badge.textContent=String(n); }
  // "Limpar todos os filtros" só faz sentido havendo algo a limpar. Desabilitado de forma
  // acessível (disabled real, não só opacidade) — leitores de tela anunciam indisponível.
  const clearBtn=mvpn('mvpNotesFiltersClearBtn');
  if(clearBtn){
    clearBtn.disabled=n===0;
    clearBtn.setAttribute('aria-label', n===0
      ? 'Limpar todos os filtros — nenhum filtro ativo'
      : `Limpar todos os filtros — ${n} filtro${n===1?'':'s'} ativo${n===1?'':'s'}`);
  }
  const fbtn=mvpn('mvpNotesFiltersBtn');
  if(fbtn) fbtn.setAttribute('aria-label',n>0?`Filtrar notas — ${n} filtro${n===1?'':'s'} ativo${n===1?'':'s'}`:'Filtrar notas');
}
// Limpeza dos filtros — ação ÚNICA do módulo (JPW-RQPNMK). Zera todos os critérios
// estruturais e NADA mais: busca, visão/pasta ativa, nota aberta, rascunho e dados
// persistidos ficam exatamente como estavam. Não grava nada no estado da aplicação.
function mvpNotesClearAllFilters(){
  const havia=mvpNotesActiveFilterCount();
  mvpNotesUI.filterType='all'; mvpNotesUI.filterStatus='all'; mvpNotesUI.filterPriority='all';
  mvpNotesUI.filterFolder='all'; mvpNotesUI.filterPeriod='all'; mvpNotesUI.filterPolicy='all';
  ['mvpNotesFilterType','mvpNotesFilterStatus','mvpNotesFilterPriority','mvpNotesFilterFolder',
   'mvpNotesFilterPeriod','mvpNotesFilterPolicy'].forEach(id=>{ const el=mvpn(id); if(el) el.value='all'; });
  renderMvpNotesList();
  const live=mvpn('mvpNotesFiltersLive');
  if(live) live.textContent=havia>0?'Todos os filtros foram removidos.':'';
  return havia;
}
function renderMvpNotesList(){
  mvpNotesEnsureActiveFolderValid();
  renderMvpNotesFolderNav();
  mvpNotesSyncFilterControls();
  const titleEl=mvpn('mvpNotesViewTitle'); if(titleEl) titleEl.textContent=mvpNotesViewLabel();
  // O cabeçalho mobile é função do estágio + da visão ativa, e AMBOS podem ter acabado de
  // mudar (entrar numa pasta, renomeá-la, reordenar, excluir). Reaplicar aqui — a operação
  // é só atributo e texto — garante que nenhum título antigo fique preso no topo. Antes
  // disto, trocar de pasta no celular mudava o estado mas deixava a tela no estágio Pastas.
  mvpNotesApplyStage();
  const host=mvpn('mvpNotesList'); if(!host) return;
  const total=mvpNotesItems().length, {ativas,concluidas}=mvpNotesGrouped();
  if(total===0){
    host.innerHTML=`<p class="mvpn-empty">Nenhuma nota registrada. Use "+" para registrar tarefas, bugs, funcionalidades ou melhorias do MVP.</p>`;
  }else if(!ativas.length && !concluidas.length){
    const temBusca=!!mvpNotesUI.query.trim(), temFiltro=mvpNotesActiveFilterCount()>0;
    const msg=(temBusca&&temFiltro)?'Nenhuma nota corresponde à busca e aos filtros atuais.':'Nenhuma nota encontrada.';
    host.innerHTML=`<p class="mvpn-empty">${msg}</p>`;
  }else{
    // O separador só existe quando há concluídas na visão atual, com contador discreto.
    // Na visão global "Concluído" ele seria redundante: o título da vista já diz isso, e a
    // lista inteira é de concluídas — não há nada acima de que separá-las.
    const sep=(concluidas.length && !mvpNotesIsDoneView())
      ? `<div class="mvpn-group-sep"><span>Concluídas</span><span class="mvpn-group-count">${concluidas.length}</span></div>`
      : '';
    host.innerHTML=ativas.map(mvpNotesCardHTML).join('')+sep+concluidas.map(mvpNotesCardHTML).join('');
  }
  host.querySelectorAll('[data-mvp-note-id]').forEach(card=>card.addEventListener('click',()=>{
    mvpNotesSelectNote(card.dataset.mvpNoteId);
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
// `manageable` distingue pasta REAL de visão do sistema. Só a pasta real ganha alça de
// arraste, marcador de linha reordenável e os itens "Mover para cima/baixo" — "Todas as
// Notas", "Sem pasta" e "Concluído" não existem em folders[] e não são reordenáveis por
// construção, não por checagem defensiva.
function mvpNotesFolderRowHTML(id,name,count,manageable,ordem){
  const active=mvpNotesUI.activeFolder===id;
  const system=id==='all'||id==='unfiled'||id==='done';
  const systemAttr=system?` data-mvp-system-view="true" aria-description="Visão do sistema"`:'';
  const pos=ordem?ordem.index:0, total=ordem?ordem.total:0;
  // A alça é um afordance de ponteiro: quem usa teclado organiza pelo menu "⋯", que faz
  // exatamente a mesma operação. Por isso ela fica fora da ordem de tabulação em vez de
  // virar um ponto de foco que não responde ao teclado.
  const alca=manageable?`<span class="mvpn-folder-drag" data-mvp-folder-drag="${esc(id)}" aria-hidden="true" title="Arraste para reordenar">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M3 5h10M3 8h10M3 11h10"/></svg>
    </span>`:'';
  const podeSubir=manageable && pos>0, podeDescer=manageable && pos<total-1;
  return `<div class="mvpn-folder-row${id==='done'?' mvpn-folder-row-done':''}"${manageable?` data-mvp-folder-row="${esc(id)}"`:''}>
    ${alca}
    <button type="button" class="mvpn-folder-btn" data-mvp-folder="${esc(id)}"${systemAttr} ${active?'aria-current="page"':''}>
      <span class="mvpn-folder-name" title="${esc(name)}">${esc(name)}</span>
      <span class="mvpn-folder-count">${count}</span>
    </button>
    ${manageable?`<details class="mvpn-folder-kebab">
      <summary aria-label="Mais ações para a pasta ${esc(name)} — posição ${pos+1} de ${total}">⋯</summary>
      <div class="mvpn-folder-kebab-menu">
        ${podeSubir?`<button type="button" data-mvp-folder-up="${esc(id)}">Mover para cima</button>`:''}
        ${podeDescer?`<button type="button" data-mvp-folder-down="${esc(id)}">Mover para baixo</button>`:''}
        <button type="button" data-mvp-folder-rename="${esc(id)}">Renomear</button>
        <button type="button" data-mvp-folder-delete="${esc(id)}">Excluir</button>
      </div>
    </details>`:''}
  </div>`;
}
function renderMvpNotesFolderNav(){
  const folders=mvpNotesFoldersOrdered(); // ordem manual — a mesma em sidebar, filtros e inspector
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
      ? `<div class="mvpn-folder-group-label">Pastas</div>`
        +folders.map((f,i)=>mvpNotesFolderRowHTML(f.id,f.name,mvpNotesFolderItemCount(f.id),true,{index:i,total:folders.length})).join('')
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
  // Mover para cima/baixo: mesma operação central do arraste, disponível por teclado.
  // Como o menu vive na linha que será re-renderizada, o foco é devolvido ao "⋯" da pasta
  // movida — contexto previsível para mover várias posições em sequência.
  const mover=(id,delta)=>{
    const de=mvpNotesFolderIndex(id);
    if(de<0) return;
    if(mvpNotesMoveFolder(id,de+delta)) mvpNotesFocusFolderKebab(id);
  };
  host.querySelectorAll('[data-mvp-folder-up]').forEach(btn=>btn.addEventListener('click',()=>{
    const details=btn.closest('details'); if(details) details.open=false;
    mover(btn.dataset.mvpFolderUp,-1);
  }));
  host.querySelectorAll('[data-mvp-folder-down]').forEach(btn=>btn.addEventListener('click',()=>{
    const details=btn.closest('details'); if(details) details.open=false;
    mover(btn.dataset.mvpFolderDown,+1);
  }));
  bindMvpNotesFolderDrag(host);
}
// ---- arraste das pastas (Pointer Events, sem biblioteca) --------------------------
// Limiar de 4px para não transformar um clique simples em reordenação acidental; o alvo é
// calculado só entre as linhas de pastas REAIS, então não existe destino "antes de Todas as
// Notas". Durante o gesto nada é salvo e nenhuma nota é tocada: só classes de CSS mudam.
const MVPN_FOLDER_DRAG_LIMIAR=4;
function mvpNotesFolderRows(host){ return [...host.querySelectorAll('[data-mvp-folder-row]')]; }
// Índice do "vão" de inserção (0..n) sob o ponteiro: metade de cima da linha insere antes,
// metade de baixo insere depois.
function mvpNotesFolderDropSlot(host,clientY){
  const linhas=mvpNotesFolderRows(host);
  for(let i=0;i<linhas.length;i++){
    const r=linhas[i].getBoundingClientRect();
    if(clientY < r.top + r.height/2) return i;
  }
  return linhas.length;
}
// Indicador de destino: uma linha fina entre as pastas (não só opacidade — precisa dizer
// ONDE vai cair, não apenas que algo está sendo arrastado).
function mvpNotesFolderShowDrop(host,slot){
  const linhas=mvpNotesFolderRows(host);
  linhas.forEach(l=>l.classList.remove('mvpn-drop-before','mvpn-drop-after'));
  if(!linhas.length) return;
  if(slot<linhas.length) linhas[slot].classList.add('mvpn-drop-before');
  else linhas[linhas.length-1].classList.add('mvpn-drop-after');
}
function mvpNotesFolderDragCleanup(){
  const host=mvpn('mvpNotesFolderNavList');
  if(host){
    mvpNotesFolderRows(host).forEach(l=>l.classList.remove('mvpn-dragging','mvpn-drop-before','mvpn-drop-after'));
  }
  document.body.classList.remove('mvpn-folder-dragging');
  mvpNotesUI.folderDrag=null;
}
function bindMvpNotesFolderDrag(host){
  host.querySelectorAll('[data-mvp-folder-drag]').forEach(alca=>{
    alca.addEventListener('pointerdown',e=>{
      const id=alca.dataset.mvpFolderDrag;
      const de=mvpNotesFolderIndex(id);
      if(de<0) return;
      e.preventDefault();
      try{ alca.setPointerCapture(e.pointerId); }catch(_){}
      // Ainda NÃO é arraste: só intenção. Vira arraste ao passar do limiar (ver pointermove).
      mvpNotesUI.folderDrag={id, de, startY:e.clientY, slot:de, ativo:false, pointerId:e.pointerId};
    });
    alca.addEventListener('pointermove',e=>{
      const st=mvpNotesUI.folderDrag; if(!st || st.id!==alca.dataset.mvpFolderDrag) return;
      if(!st.ativo){
        if(Math.abs(e.clientY-st.startY)<MVPN_FOLDER_DRAG_LIMIAR) return;
        st.ativo=true;
        const linha=host.querySelector(`[data-mvp-folder-row="${CSS.escape(st.id)}"]`);
        if(linha) linha.classList.add('mvpn-dragging');
        document.body.classList.add('mvpn-folder-dragging');
      }
      st.slot=mvpNotesFolderDropSlot(host,e.clientY);
      mvpNotesFolderShowDrop(host,st.slot);
    });
    alca.addEventListener('pointerup',()=>{
      const st=mvpNotesUI.folderDrag; if(!st || st.id!==alca.dataset.mvpFolderDrag) return;
      const {id,de,slot,ativo}=st;
      mvpNotesFolderDragCleanup();
      if(!ativo) return;                       // foi um clique na alça, não um arraste
      const alvo=slot>de?slot-1:slot;          // o vão vira índice depois de retirar a pasta
      if(alvo===de) return;                    // soltou onde já estava: nada persiste
      mvpNotesMoveFolder(id,alvo);             // uma única escrita, aqui
    });
    // Gesto interrompido (Escape trata-se no keydown global): ordem volta ao estado anterior
    // simplesmente porque nada foi escrito — só limpamos as classes.
    alca.addEventListener('pointercancel',mvpNotesFolderDragCleanup);
    alca.addEventListener('lostpointercapture',()=>{
      if(mvpNotesUI.folderDrag) mvpNotesFolderDragCleanup();
    });
  });
}
// ---- menu "⋯" das pastas: semântica de menu contextual (JPW-YX2Z43) ---------------
// <details> nativo NÃO fecha ao clicar fora — abre e só fecha ao clicar de novo no
// próprio marcador. Para um menu de ações isso é errado: o operador clica em qualquer
// lugar esperando dispensá-lo. Aqui damos o comportamento esperado sem trocar o <details>
// por um dropdown próprio: um único listener, registrado uma vez na inicialização,
// escopado à lista de pastas das Notas.
function mvpNotesFecharMenusDePasta(exceto){
  const host=mvpn('mvpNotesFolderNavList'); if(!host) return false;
  let fechou=false;
  host.querySelectorAll('details.mvpn-folder-kebab[open]').forEach(d=>{
    if(d!==exceto){ d.open=false; fechou=true; }
  });
  return fechou;
}
function mvpNotesMenuDePastaAberto(){
  const host=mvpn('mvpNotesFolderNavList');
  return !!(host && host.querySelector('details.mvpn-folder-kebab[open]'));
}
// Registrado UMA vez (initMvpNotes → bindMvpNotesDrawer), nunca por abertura do drawer:
// a lista de pastas é re-renderizada com frequência, e ligar por linha acumularia
// handlers. Fase de captura para agir antes de qualquer stopPropagation dos cards.
function bindMvpNotesFolderMenuDismiss(){
  document.addEventListener('pointerdown',event=>{
    if(!mvpNotesMenuDePastaAberto()) return;
    const host=mvpn('mvpNotesFolderNavList'); if(!host) return;
    // Só nos importa o menu das PASTAS: inspector, filtros, editor e qualquer <details>
    // fora deste host seguem seu próprio comportamento.
    const dentroDeUmKebab=event.target instanceof Node
      ? event.target.closest && event.target.closest('.mvpn-folder-kebab')
      : null;
    // Clique no marcador de outra pasta: fecha os demais e deixa o nativo abrir aquele.
    mvpNotesFecharMenusDePasta(dentroDeUmKebab&&host.contains(dentroDeUmKebab)?dentroDeUmKebab:null);
  },true);
}
function mvpNotesFocusFolderKebab(id){
  const linha=mvpn('mvpNotesFolderNavList').querySelector(`[data-mvp-folder-row="${CSS.escape(id)}"]`);
  const alvo=linha?linha.querySelector('.mvpn-folder-kebab summary'):null;
  if(alvo) alvo.focus();
}
// Trocar de pasta/visão preserva busca e filtros — só re-renderiza a lista; a mesma
// proteção de rascunho não salvo das demais ações de pasta se aplica aqui. Em mobile,
// escolher uma pasta avança a navegação em camadas para a Lista (estágio B).
function mvpNotesSwitchFolder(target){
  mvpNotesConfirmDiscardIfDirty(()=>{
    mvpNotesUI.activeFolder=target;
    mvpNotesUI.stage='list';
    renderMvpNotesList();
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
    renderMvpNotesList();
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
    renderMvpNotesList();
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
    renderMvpNotesList();
  });
}
// ---- navegação mobile em camadas (Pastas → Lista → Editor) ----
// Um único DOM para os dois mundos: em desktop a sidebar e o conteúdo convivem lado a
// lado e o atributo data-mobile-stage é ignorado pelo CSS; abaixo do breakpoint (920px,
// o mesmo já usado pelo módulo) o atributo decide qual camada ocupa a tela inteira.
// Breakpoint único do módulo — precisa casar EXATAMENTE com o @media do app.css, senão o
// JS e o CSS discordam sobre qual mundo está na tela. Subiu de 760 para 920 na Fase D:
// abaixo disso as três colunas não cabem com seus mínimos medidos (ver o comentário do
// bloco mobile no CSS) e a navegação em camadas é a resposta honesta.
function mvpNotesIsMobile(){ return window.matchMedia('(max-width:920px)').matches; }
function mvpNotesApplyStage(){
  const drawer=mvpn('mvpNotesDrawer'); if(!drawer) return;
  drawer.dataset.mobileStage=mvpNotesUI.stage;
  const backBtn=mvpn('mvpNotesBackBtn'), title=mvpn('mvpNotesTitle');
  if(mvpNotesIsMobile()){
    if(title) title.textContent=mvpNotesUI.stage==='folders'?'Notas do MVP'
      :(mvpNotesUI.stage==='list'?mvpNotesViewLabel():(mvpNotesUI.selectedId?'Editar nota':'Nova nota'));
    if(backBtn){
      backBtn.hidden=mvpNotesUI.stage==='folders';
      // O destino do Voltar é dito por extenso, não só pela seta: da nota volta-se para a
      // VISÃO DE ORIGEM (pasta, "Todas as Notas" ou "Concluído"), não para uma pasta
      // inferida do folderId da nota. mvpNotesViewLabel() lê activeFolder, que a abertura
      // da nota nunca altera — a rota de volta é a de ida.
      const destino=mvpNotesUI.stage==='editor'?mvpNotesViewLabel():'Pastas';
      backBtn.setAttribute('aria-label',`Voltar para ${destino}`);
      backBtn.setAttribute('title',`Voltar para ${destino}`);
      const rotulo=mvpn('mvpNotesBackLabel');
      if(rotulo) rotulo.textContent=destino;
    }
  }else{
    if(title) title.textContent='Notas do MVP';
    if(backBtn) backBtn.hidden=true;
  }
}
// Voltar contextual: Editor → Lista (com proteção de rascunho sujo), Lista → Pastas.
// No estágio Pastas o botão não existe (fechar é o X, como em desktop).
function mvpNotesGoBack(){
  if(mvpNotesUI.stage==='editor'){ mvpNotesConfirmDiscardIfDirty(mvpNotesCloseEditor); return; }
  if(mvpNotesUI.stage==='list'){
    mvpNotesUI.stage='folders';
    mvpNotesSetFiltersOpen(false);
    mvpNotesApplyStage();
    const nav=mvpn('mvpNotesFolderNavList');
    const current=nav?nav.querySelector('[aria-current="page"]')||nav.querySelector('button'):null;
    if(current) current.focus();
  }
}
// ---- bottom sheet de filtros (mobile) ----
function mvpNotesSetFiltersOpen(open){
  mvpNotesUI.filtersOpen=open;
  const wrap=mvpn('mvpNotesFiltersWrap'), btn=mvpn('mvpNotesFiltersBtn');
  if(wrap) wrap.classList.toggle('open',open);
  if(btn) btn.setAttribute('aria-expanded',String(open));
  if(open){ const first=wrap?wrap.querySelector('select:not([hidden])'):null; if(first) first.focus(); }
  else if(btn && wrap && document.activeElement && wrap.contains(document.activeElement)) btn.focus();
}

// ---- seleção e edição (Apple Notes: lista à esquerda, nota à direita) ----
// O editor NUNCA substitui a lista: no desktop as três colunas convivem. Selecionar uma
// nota só troca o conteúdo do painel da direita e o destaque na lista.
function mvpNotesDraftFromItem(item){
  return {content:item.content||'', type:item.type, priority:item.priority, status:item.status,
    folderId:item.folderId||null, aiImplementationPolicy:item.aiImplementationPolicy};
}
// Rascunho de nota nova: herda a pasta ativa quando ela é uma pasta real; nas visões
// virtuais fica sem pasta. Criar a partir de "Concluídas" NUNCA nasce concluída — a
// visão é derivada do status, não um destino de criação.
function mvpNotesNewDraft(){
  const af=mvpNotesUI.activeFolder;
  const folderId=(af!=='all' && af!=='unfiled' && af!=='done') ? af : null;
  return {content:'', type:'task', priority:'medium', status:'open', folderId,
    aiImplementationPolicy:MVP_NOTES_AI_POLICY_DEFAULT};
}
function mvpNotesDraftEqual(a,b){
  return !!a && !!b && a.content===b.content && a.type===b.type && a.priority===b.priority &&
    a.status===b.status && (a.folderId||null)===(b.folderId||null) &&
    a.aiImplementationPolicy===b.aiImplementationPolicy;
}
function mvpNotesRecomputeDirty(){
  mvpNotesUI.draftDirty=!mvpNotesDraftEqual(mvpNotesUI.draft,mvpNotesUI.draftOriginal);
  const bar=mvpn('mvpNotesEditorBar');
  if(bar) bar.dataset.dirty=String(mvpNotesUI.draftDirty);
  const saveBtn=mvpn('mvpNotesSaveBtn');
  if(saveBtn) saveBtn.hidden=!mvpNotesUI.draftDirty;
}
// Título mostrado ao vivo enquanto se digita — derivado da mesma função que a persistência
// usa, então o que a lista mostrará depois de salvar é exatamente o que se vê agora.
function mvpNotesUpdateLiveTitle(){
  const el=mvpn('mvpNotesEditorTitle'); if(!el) return;
  const t=mvpNotesDeriveTitle(mvpNotesUI.draft?mvpNotesUI.draft.content:'');
  el.textContent=t||'Nova nota';       // placeholder VISUAL — nunca entra no conteúdo
  el.classList.toggle('mvpn-title-placeholder',!t);
}
// Pinta o painel da direita a partir do rascunho corrente (ou o estado vazio).
function renderMvpNotesEditor(){
  const bar=mvpn('mvpNotesEditorBar'), area=mvpn('mvpNoteContent'), vazio=mvpn('mvpNotesEditorEmpty');
  const temRascunho=!!mvpNotesUI.draft;
  if(bar) bar.hidden=!temRascunho;
  if(area) area.hidden=!temRascunho;
  if(vazio) vazio.hidden=temRascunho;
  if(!temRascunho) return;
  if(area && area.value!==mvpNotesUI.draft.content) area.value=mvpNotesUI.draft.content;
  const item=mvpNotesUI.selectedId?mvpNotesItems().find(i=>i.id===mvpNotesUI.selectedId):null;
  const ticketEl=mvpn('mvpNotesEditorTicket');
  if(ticketEl) ticketEl.textContent=item?(item.ticket||''):'nova nota';
  const copyBtn=mvpn('mvpNotesCopyRefBtn');
  if(copyBtn){ copyBtn.hidden=!item; if(item) copyBtn.dataset.mvpCopyId=item.id; }
  mvpNotesUpdateLiveTitle();
  mvpNotesRecomputeDirty();
}
// ---- inspector da nota (metadados sob demanda) ----
// Tudo que é administrativo/técnico vive aqui, fora do editor: o conteúdo fica em
// primeiro plano, como no Apple Notes. Abrir/fechar NUNCA altera a nota (nem updatedAt,
// nem dirty) — só os selects mudam o rascunho, e a gravação continua no botão Salvar.
function mvpNotesInspectorHTML(){
  const d=mvpNotesUI.draft;
  const item=mvpNotesUI.selectedId?mvpNotesItems().find(i=>i.id===mvpNotesUI.selectedId):null;
  const opt=(map,sel)=>Object.keys(map).map(k=>`<option value="${k}" ${k===sel?'selected':''}>${esc(map[k])}</option>`).join('');
  const folderOpts=`<option value="" ${!d.folderId?'selected':''}>Sem pasta</option>`
    +mvpNotesFoldersOrdered().map(f=>`<option value="${esc(f.id)}" ${f.id===d.folderId?'selected':''}>${esc(f.name)}</option>`).join('');
  const fato=(k,v)=>`<dt>${k}</dt><dd>${v}</dd>`;
  return `
    <div class="mvpn-inspector-head">
      <h4 id="mvpNotesInspectorTitle">Detalhes da nota</h4>
      <button type="button" class="mvpn-icon-btn" id="mvpNotesInspectorCloseBtn" aria-label="Fechar detalhes da nota" title="Fechar detalhes">✕</button>
    </div>
    <div class="field"><label for="mvpNoteType">Tipo</label><select id="mvpNoteType">${opt(MVP_NOTES_TYPE_LABELS,d.type)}</select></div>
    <div class="field"><label for="mvpNotePriority">Prioridade</label><select id="mvpNotePriority">${opt(MVP_NOTES_PRIORITY_LABELS,d.priority)}</select></div>
    <div class="field"><label for="mvpNoteStatus">Status</label><select id="mvpNoteStatus">${opt(MVP_NOTES_STATUS_LABELS,d.status)}</select></div>
    <div class="field"><label for="mvpNoteFolder">Pasta</label><select id="mvpNoteFolder">${folderOpts}</select></div>
    <div class="field"><label for="mvpNotePolicy">Autorização de implementação por IA</label>
      <select id="mvpNotePolicy">${opt(MVP_NOTES_POLICY_LABELS,d.aiImplementationPolicy)}</select>
      <span class="mvpn-hint" id="mvpNotePolicyHint">${esc(MVP_NOTES_POLICY_HINT[d.aiImplementationPolicy]||'')}</span>
    </div>
    ${item?`<dl class="mvpn-meta-facts">
      ${fato('Trace ID',`<code>${esc(item.ticket)}</code>`)}
      ${fato('Build ID',esc(item.buildId||'não disponível'))}
      ${fato('Source Revision',esc(mvpNotesSourceRevision(item)||'não disponível'))}
      ${fato('Tela de origem',esc(mvpNotesScreenLabel(item.screenId)))}
      ${fato('Criada em',esc(mvpNotesFormatDate(item.createdAt)))}
      ${fato('Atualizada em',esc(mvpNotesFormatDate(item.updatedAt)))}
      ${item.completedAt?fato('Concluída em',esc(mvpNotesFormatDate(item.completedAt))):''}
    </dl>
    <div class="mvpn-inspector-footer">
      <div class="mvpn-inspector-actions">
        <button type="button" class="reset-btn" id="mvpNoteExportMdBtn">Exportar como Markdown</button>
      </div>
      <div class="mvpn-inspector-danger">
        <button type="button" class="reset-btn mvpn-danger" id="mvpNoteDeleteBtn">Excluir nota</button>
      </div>
    </div>`:`<p class="mvpn-hint">Os dados técnicos (Trace ID, build, datas) aparecem depois de salvar a nota.</p>`}`;
}
function mvpNotesSetInspectorOpen(open){
  const insp=mvpn('mvpNotesInspector'), btn=mvpn('mvpNotesInspectorBtn');
  if(!insp) return;
  if(open && !mvpNotesUI.draft) return; // sem nota aberta, nada a inspecionar
  if(open && mvpNotesUI.filtersOpen) mvpNotesSetFiltersOpen(false); // uma superfície por vez
  mvpNotesUI.inspectorOpen=open;
  insp.classList.toggle('open',open);
  if(btn) btn.setAttribute('aria-expanded',String(open));
  if(open){
    insp.innerHTML=mvpNotesInspectorHTML();
    bindMvpNotesInspector();
    const first=insp.querySelector('select'); if(first) first.focus();
  }else{
    const tinhaFoco=insp.contains(document.activeElement);
    insp.innerHTML='';
    if(btn && tinhaFoco) btn.focus(); // Escape/fechar devolve o foco ao [•••]
  }
}
function bindMvpNotesInspector(){
  // Cada select altera SÓ o rascunho e recalcula o dirty — nada é salvo aqui. O botão
  // Salvar do editor persiste conteúdo + metadados como uma alteração única.
  const liga=(id,campo)=>{ const el=mvpn(id); if(!el) return;
    el.addEventListener('change',()=>{
      if(!mvpNotesUI.draft) return;
      mvpNotesUI.draft[campo]=(id==='mvpNoteFolder')?(el.value||null):el.value;
      if(id==='mvpNotePolicy'){ const h=mvpn('mvpNotePolicyHint'); if(h) h.textContent=MVP_NOTES_POLICY_HINT[el.value]||''; }
      mvpNotesRecomputeDirty();
    });
  };
  liga('mvpNoteType','type'); liga('mvpNotePriority','priority'); liga('mvpNoteStatus','status');
  liga('mvpNoteFolder','folderId'); liga('mvpNotePolicy','aiImplementationPolicy');
  const fechar=mvpn('mvpNotesInspectorCloseBtn');
  if(fechar) fechar.addEventListener('click',()=>mvpNotesSetInspectorOpen(false)); // rascunho permanece em memória
  const exp=mvpn('mvpNoteExportMdBtn');
  if(exp) exp.addEventListener('click',mvpNotesExportMarkdown); // leitura pura: não toca no estado
  const del=mvpn('mvpNoteDeleteBtn');
  if(del) del.addEventListener('click',()=>{
    const item=mvpNotesItems().find(i=>i.id===mvpNotesUI.selectedId); if(!item) return;
    if(!confirm(`Excluir a nota "${item.title}"? Esta ação não pode ser desfeita.`)) return;
    mvpNotesDelete(item.id);
    mvpNotesUI.draftDirty=false;
    mvpNotesSetInspectorOpen(false);
    mvpNotesCloseEditor();
  });
}

// Ponto único de entrada da seleção. Respeita o rascunho sujo antes de trocar de nota.
function mvpNotesSelectNote(id){
  if(mvpNotesUI.selectedId===id && mvpNotesUI.draft) return; // já aberta
  mvpNotesConfirmDiscardIfDirty(()=>{
    const item=mvpNotesItems().find(i=>i.id===id);
    if(!item) return;
    mvpNotesUI.selectedId=item.id;
    mvpNotesUI.draft=mvpNotesDraftFromItem(item);
    mvpNotesUI.draftOriginal={...mvpNotesUI.draft};
    mvpNotesUI.draftDirty=false;
    mvpNotesUI.stage='editor';   // mobile avança de camada; desktop ignora
    renderMvpNotesList();        // atualiza o destaque da nota selecionada
    renderMvpNotesEditor();
    if(mvpNotesUI.inspectorOpen) mvpNotesSetInspectorOpen(true); // atualiza para a nova nota
    mvpNotesApplyStage();
    if(!mvpNotesIsMobile()){ const a=mvpn('mvpNoteContent'); if(a) a.focus(); }
  });
}
function mvpNotesStartNewNote(){
  mvpNotesConfirmDiscardIfDirty(()=>{
    mvpNotesUI.selectedId=null;
    mvpNotesUI.draft=mvpNotesNewDraft();
    mvpNotesUI.draftOriginal={...mvpNotesUI.draft};
    mvpNotesUI.draftDirty=false;
    mvpNotesUI.stage='editor';
    renderMvpNotesList();
    renderMvpNotesEditor();
    mvpNotesApplyStage();
    const a=mvpn('mvpNoteContent'); if(a) a.focus();
  });
}
// Salvar: cria ou atualiza conforme haja nota selecionada. Nota sem nenhum texto não é
// persistida — não há o que rastrear, e o título derivado seria vazio.
function mvpNotesSaveDraft(){
  if(!mvpNotesUI.draft) return;
  if(!mvpNotesDeriveTitle(mvpNotesUI.draft.content)){
    const live=mvpn('mvpNotesCopyLive');
    if(live) live.textContent='Escreva ao menos uma linha: a primeira vira o título.';
    const a=mvpn('mvpNoteContent'); if(a) a.focus();
    return;
  }
  const salvo=mvpNotesUI.selectedId
    ? mvpNotesUpdate(mvpNotesUI.selectedId,mvpNotesUI.draft)
    : mvpNotesCreate(mvpNotesUI.draft);
  if(salvo){
    mvpNotesUI.selectedId=salvo.id;
    mvpNotesUI.draft=mvpNotesDraftFromItem(salvo);
    mvpNotesUI.draftOriginal={...mvpNotesUI.draft};
  }
  mvpNotesUI.draftDirty=false;
  renderMvpNotesList();
  renderMvpNotesEditor();
  if(mvpNotesUI.inspectorOpen) mvpNotesSetInspectorOpen(true); // fatos atualizados pós-gravação
}
// Fecha a nota aberta (usado pelo "voltar" do mobile). No desktop o painel volta ao
// estado vazio — as três colunas continuam onde estão.
function mvpNotesCloseEditor(){
  if(mvpNotesUI.inspectorOpen) mvpNotesSetInspectorOpen(false);
  mvpNotesUI.selectedId=null;
  mvpNotesUI.draft=null; mvpNotesUI.draftOriginal=null; mvpNotesUI.draftDirty=false;
  if(mvpNotesUI.stage==='editor') mvpNotesUI.stage='list';
  renderMvpNotesList();
  renderMvpNotesEditor();
  mvpNotesApplyStage();
}
function mvpNotesConfirmDiscardIfDirty(proceed){
  if(mvpNotesUI.draftDirty){
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
// Alvo "ampliado" do duplo clique na borda externa. Era 760 — menor que o próprio padrão
// v5 (980), o que tornava o duplo clique um no-op desde a mudança de faixa. 1360 é
// efetivamente amplo e continua dentro da faixa canônica (MVP_NOTES_DRAWER_MIN–1600).
const MVPN_DRAWER_WIDE=1360;
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
  // O drawer mudou de tamanho: as três colunas precisam caber de novo AGORA. Só reescreve
  // as duas variáveis CSS (sem render, sem save) — as preferências continuam intactas.
  if(d && mvpNotesUI.open) mvpNotesApplyPaneWidths();
  const h=mvpn('mvpNotesResizeHandle');
  if(h){
    h.setAttribute('aria-valuemin',String(MVP_NOTES_DRAWER_MIN));
    h.setAttribute('aria-valuemax',String(mvpNotesDrawerMax())); // teto efetivo desta janela
    h.setAttribute('aria-valuenow',String(w));
    h.setAttribute('aria-valuetext',`${w} pixels de largura`);
  }
}
// ---- geometria das três colunas (Fase D) -----------------------------------------
// Duas larguras persistidas (foldersPaneWidth, notesPaneWidth); o editor recebe o RESTO —
// não existe editorPaneWidth, para não haver estado redundante que possa divergir.
//
// Separação deliberada entre PREFERÊNCIA e RENDERIZAÇÃO:
//   preferência = o que o operador escolheu, guardado em S.mvpNotes.ui (faixa canônica);
//   renderização = o que cabe AGORA, calculado por mvpNotesFitPanes contra a largura real
//                  do drawer neste instante.
// Estreitar o drawer (ou a janela) muda só a renderização. A preferência sobrevive intacta
// e volta a valer assim que houver espaço de novo — nunca é reescrita por aperto temporário.
function mvpNotesPanePrefs(){
  const ui=(S.mvpNotes&&S.mvpNotes.ui)?S.mvpNotes.ui:{};
  const num=(v,padrao)=>{ const n=Number(v); return Number.isFinite(n)?n:padrao; };
  return {
    folders:Math.min(Math.max(Math.round(num(ui.foldersPaneWidth,MVP_NOTES_FOLDERS_DEFAULT)),MVP_NOTES_FOLDERS_MIN),MVP_NOTES_FOLDERS_MAX),
    list:Math.min(Math.max(Math.round(num(ui.notesPaneWidth,MVP_NOTES_LIST_DEFAULT)),MVP_NOTES_LIST_MIN),MVP_NOTES_LIST_MAX)
  };
}
// Largura que o drawer REALMENTE tem agora: o CSS aplica min(persistido, 80vw, viewport-32),
// então o valor guardado não serve para calcular o que cabe. Antes de o drawer estar visível
// (abertura) o rect é 0 — aí a melhor estimativa é a largura persistida já aparada.
function mvpNotesRenderedDrawerWidth(){
  const d=mvpn('mvpNotesDrawer');
  const r=d?d.getBoundingClientRect().width:0;
  return r>0?r:mvpNotesClampWidth(mvpNotesDrawerWidth());
}
// Larguras efetivamente renderizadas neste instante (preferências passadas pelo ajuste).
function mvpNotesRenderedPanes(){
  const prefs=mvpNotesPanePrefs();
  return mvpNotesFitPanes(prefs.folders,prefs.list,mvpNotesRenderedDrawerWidth());
}
// Limites VIVOS de cada separador: o máximo de uma coluna depende do que a outra está
// ocupando e do piso do editor. Garante a invariante pastas + lista + editor + separadores
// <= largura interna disponível, sempre.
function mvpNotesPaneLimits(){
  const espaco=mvpNotesPaneSpace(mvpNotesRenderedDrawerWidth());
  const atual=mvpNotesRenderedPanes();
  return {
    espaco,
    foldersMin:MVP_NOTES_FOLDERS_MIN,
    foldersMax:Math.max(MVP_NOTES_FOLDERS_MIN,Math.min(MVP_NOTES_FOLDERS_MAX,espaco-atual.list-MVP_NOTES_EDITOR_MIN)),
    listMin:MVP_NOTES_LIST_MIN,
    listMax:Math.max(MVP_NOTES_LIST_MIN,Math.min(MVP_NOTES_LIST_MAX,espaco-atual.folders-MVP_NOTES_EDITOR_MIN))
  };
}
// Escreve a geometria: só duas custom properties no drawer. Nenhum render de lista, editor
// ou pastas — redimensionar é barato por construção (ver o arraste, abaixo).
function mvpNotesWritePaneVars(folders,list){
  const d=mvpn('mvpNotesDrawer'); if(!d) return;
  d.style.setProperty('--mvpn-folders-w',Math.round(folders)+'px');
  d.style.setProperty('--mvpn-list-w',Math.round(list)+'px');
  mvpNotesSyncPaneHandleAria(folders,list);
}
// ARIA dos dois separadores acompanha a coluna ao vivo — valor e limites nunca congelam.
function mvpNotesSyncPaneHandleAria(folders,list){
  const espaco=mvpNotesPaneSpace(mvpNotesRenderedDrawerWidth());
  const fMax=Math.max(MVP_NOTES_FOLDERS_MIN,Math.min(MVP_NOTES_FOLDERS_MAX,espaco-Math.round(list)-MVP_NOTES_EDITOR_MIN));
  const lMax=Math.max(MVP_NOTES_LIST_MIN,Math.min(MVP_NOTES_LIST_MAX,espaco-Math.round(folders)-MVP_NOTES_EDITOR_MIN));
  const escreve=(el,min,max,valor,rotulo)=>{
    if(!el) return;
    el.setAttribute('aria-valuemin',String(min));
    el.setAttribute('aria-valuemax',String(max));
    el.setAttribute('aria-valuenow',String(Math.round(valor)));
    el.setAttribute('aria-valuetext',`${rotulo}: ${Math.round(valor)} pixels`);
  };
  escreve(mvpn('mvpNotesFoldersHandle'),MVP_NOTES_FOLDERS_MIN,fMax,folders,'Largura da coluna de pastas');
  escreve(mvpn('mvpNotesListHandle'),MVP_NOTES_LIST_MIN,lMax,list,'Largura da lista de notas');
}
// Aplica a geometria a partir das preferências (opcionalmente com um valor em teste durante
// o arraste). Chamada na abertura, ao mudar o drawer e ao redimensionar a janela.
function mvpNotesApplyPaneWidths(candidato){
  const prefs=mvpNotesPanePrefs();
  const f=(candidato&&candidato.folders!=null)?candidato.folders:prefs.folders;
  const l=(candidato&&candidato.list!=null)?candidato.list:prefs.list;
  const fit=mvpNotesFitPanes(f,l,mvpNotesRenderedDrawerWidth());
  mvpNotesWritePaneVars(fit.folders,fit.list);
  return fit;
}
// Persistência: uma escrita por ação discreta (fim do arraste, tecla, duplo clique) — nunca
// por pixel. Só a coluna tocada muda; a preferência da outra jamais é reescrita de carona.
function mvpNotesPersistPaneWidth(chave,valor){
  if(!S.mvpNotes.ui || typeof S.mvpNotes.ui!=='object') S.mvpNotes.ui={};
  const [min,max]=chave==='foldersPaneWidth'
    ? [MVP_NOTES_FOLDERS_MIN,MVP_NOTES_FOLDERS_MAX]
    : [MVP_NOTES_LIST_MIN,MVP_NOTES_LIST_MAX];
  const v=Math.min(Math.max(Math.round(valor),min),max);
  if(S.mvpNotes.ui[chave]===v) return;
  S.mvpNotes.ui[chave]=v;
  save();
}
function mvpNotesPersistDrawerWidth(w){
  if(!S.mvpNotes.ui || typeof S.mvpNotes.ui!=='object') S.mvpNotes.ui={};
  const v=mvpNotesClampPersistable(w); // estado nunca recebe valor fora da faixa canônica
  if(S.mvpNotes.ui.drawerWidth===v) return;
  S.mvpNotes.ui.drawerWidth=v;
  save();
}
// ---- separadores internos: Pastas | Lista e Lista | Editor (Fase D) ---------------
// Semântica das setas: a seta representa o MOVIMENTO FÍSICO do separador na tela.
//   separador 1 (Pastas | Lista):  → move para a direita, Pastas cresce | ← Pastas diminui
//   separador 2 (Lista | Editor):  → move para a direita, Lista  cresce | ← Lista  diminui
// Em ambos, quem cede espaço é a coluna à direita do separador — no segundo, o editor.
const MVPN_PANE_STEP=20, MVPN_PANE_STEP_SHIFT=60;
// Marca o gesto no documento: cursor de redimensionamento em toda a tela e seleção de texto
// suspensa enquanto se arrasta (senão o arraste seleciona o texto das notas por baixo).
// SEMPRE desfeito no fim, inclusive em pointercancel/lostpointercapture.
function mvpNotesSetResizingCursor(ativo){
  document.body.classList.toggle('mvpn-resizing',!!ativo);
}
function bindMvpNotesPaneResize(){
  const paineis=[
    {handle:'mvpNotesFoldersHandle', chave:'foldersPaneWidth', campo:'folders',
     min:()=>MVP_NOTES_FOLDERS_MIN, max:()=>mvpNotesPaneLimits().foldersMax, padrao:MVP_NOTES_FOLDERS_DEFAULT},
    {handle:'mvpNotesListHandle', chave:'notesPaneWidth', campo:'list',
     min:()=>MVP_NOTES_LIST_MIN, max:()=>mvpNotesPaneLimits().listMax, padrao:MVP_NOTES_LIST_DEFAULT}
  ];
  paineis.forEach(cfg=>{
    const h=mvpn(cfg.handle); if(!h) return;
    const aplica=valor=>{
      const atual=mvpNotesRenderedPanes();
      const f=cfg.campo==='folders'?valor:atual.folders;
      const l=cfg.campo==='list'?valor:atual.list;
      // Escrita direta das variáveis: o valor já vem aparado pelos limites vivos, então o
      // ajuste não tem nada a corrigir e o gesto não "escorrega" para a outra coluna.
      mvpNotesWritePaneVars(f,l);
      return valor;
    };
    const encerra=()=>{ mvpNotesUI.paneResize=null; mvpNotesSetResizingCursor(false); };
    h.addEventListener('pointerdown',e=>{
      if(mvpNotesIsMobile()) return;
      e.preventDefault();
      try{ h.setPointerCapture(e.pointerId); }catch(_){}
      // Limites capturados no início: durante o gesto a OUTRA coluna não muda, então os
      // limites também não — evita que o teto oscile no meio do arraste.
      const atual=mvpNotesRenderedPanes();
      mvpNotesUI.paneResize={campo:cfg.campo, startX:e.clientX, startW:atual[cfg.campo],
                             min:cfg.min(), max:cfg.max(), valor:atual[cfg.campo]};
      mvpNotesSetResizingCursor(true);
    });
    h.addEventListener('pointermove',e=>{
      const st=mvpNotesUI.paneResize; if(!st || st.campo!==cfg.campo) return;
      // Arrastar para a direita aumenta a coluna à esquerda do separador, nos dois casos.
      st.valor=aplica(Math.min(Math.max(st.startW+(e.clientX-st.startX),st.min),st.max));
    });
    h.addEventListener('pointerup',()=>{
      const st=mvpNotesUI.paneResize; if(!st || st.campo!==cfg.campo) return;
      const valor=st.valor; encerra();
      mvpNotesPersistPaneWidth(cfg.chave,valor); // UMA escrita, no fim do gesto
    });
    // Gesto interrompido (toque cancelado, captura roubada): estado limpo e geometria de
    // volta à preferência guardada — nunca fica resizing preso.
    const cancela=()=>{
      const st=mvpNotesUI.paneResize; if(!st || st.campo!==cfg.campo) return;
      encerra();
      mvpNotesApplyPaneWidths();
    };
    h.addEventListener('pointercancel',cancela);
    // O navegador solta a captura junto com o pointerup normal; só é cancelamento se o
    // gesto ainda estiver ativo aqui (o pointerup já teria limpado o estado).
    h.addEventListener('lostpointercapture',cancela);
    // Duplo clique restaura SÓ esta coluna ao padrão — a outra não é tocada.
    h.addEventListener('dblclick',()=>{
      if(mvpNotesIsMobile()) return;
      const alvo=Math.min(Math.max(cfg.padrao,cfg.min()),cfg.max());
      aplica(alvo);
      mvpNotesPersistPaneWidth(cfg.chave,alvo);
    });
    h.addEventListener('keydown',e=>{
      if(mvpNotesIsMobile()) return;
      const passo=e.shiftKey?MVPN_PANE_STEP_SHIFT:MVPN_PANE_STEP;
      const atual=mvpNotesRenderedPanes()[cfg.campo];
      const min=cfg.min(), max=cfg.max();
      let v=null;
      if(e.key==='ArrowRight') v=atual+passo;      // separador anda para a direita: cresce
      else if(e.key==='ArrowLeft') v=atual-passo;  // separador anda para a esquerda: diminui
      else if(e.key==='Home') v=min;
      else if(e.key==='End') v=max;
      if(v===null) return;
      e.preventDefault();
      const alvo=Math.min(Math.max(v,min),max);
      aplica(alvo);
      mvpNotesPersistPaneWidth(cfg.chave,alvo); // ação discreta: persistir por tecla é correto
    });
  });
}
function bindMvpNotesResize(){
  const h=mvpn('mvpNotesResizeHandle'); if(!h) return;
  h.addEventListener('pointerdown',e=>{
    if(mvpNotesIsMobile()) return;
    e.preventDefault();
    try{ h.setPointerCapture(e.pointerId); }catch(_){}
    mvpNotesUI.resize={startX:e.clientX, startW:mvpNotesClampWidth(mvpNotesDrawerWidth())};
    mvpNotesSetResizingCursor(true);
  });
  h.addEventListener('pointermove',e=>{
    if(!mvpNotesUI.resize) return;
    mvpNotesApplyDrawerWidth(mvpNotesClampWidth(mvpNotesUI.resize.startW+(mvpNotesUI.resize.startX-e.clientX)));
  });
  h.addEventListener('pointerup',e=>{
    if(!mvpNotesUI.resize) return;
    const w=mvpNotesClampWidth(mvpNotesUI.resize.startW+(mvpNotesUI.resize.startX-e.clientX));
    mvpNotesUI.resize=null;
    mvpNotesSetResizingCursor(false);
    mvpNotesApplyDrawerWidth(w);
    mvpNotesPersistDrawerWidth(w);
  });
  h.addEventListener('pointercancel',()=>{
    if(!mvpNotesUI.resize) return;
    mvpNotesUI.resize=null;
    mvpNotesSetResizingCursor(false);
    mvpNotesApplyDrawerWidth(mvpNotesClampWidth(mvpNotesDrawerWidth())); // volta à última largura persistida
  });
  // Duplo clique alterna padrão ↔ ampliada (980 ↔ 1360, sempre dentro dos limites vivos).
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
  mvpNotesUI.filterFolder='all'; mvpNotesUI.filterPeriod='all'; mvpNotesUI.filterPolicy='all';
  mvpNotesUI.selectedId=null; mvpNotesUI.draft=null; mvpNotesUI.draftOriginal=null; mvpNotesUI.draftDirty=false;
  mvpNotesUI.activeFolder='all'; // cada abertura começa em "Todas as Notas", mesmo padrão dos filtros
  // Mobile abre no estágio Pastas (navegação em camadas, Estado A); desktop mostra tudo
  // lado a lado — o estágio fica em 'list' e o CSS o ignora acima do breakpoint.
  mvpNotesUI.stage=mvpNotesIsMobile()?'folders':'list';
  mvpNotesSetFiltersOpen(false);
  mvpNotesApplyDrawerWidth(mvpNotesClampWidth(mvpNotesDrawerWidth())); // largura lembrada (desktop)
  mvpNotesApplyPaneWidths();
  const search=mvpn('mvpNotesSearch'); if(search) search.value='';
  ['mvpNotesFilterType','mvpNotesFilterStatus','mvpNotesFilterPriority','mvpNotesFilterFolder','mvpNotesFilterPeriod','mvpNotesFilterPolicy'].forEach(id=>{ const el=mvpn(id); if(el) el.value='all'; });
  // A Central usa #modalOverlay como sinal para suspender seu próprio focus trap
  // (initSettingsSubdialogObserver, 09-settings-modal.js); nosso drawer tem overlay
  // próprio, então o MutationObserver dela nunca vê esta abertura — sem isto, os dois
  // focus traps disputariam Tab ao mesmo tempo quando aberto via "Abrir Notas".
  if(mvpNotesSettingsOpen() && typeof suspendSettingsForSubdialog==='function') suspendSettingsForSubdialog();
  mvpn('mvpNotesOverlay').classList.add('show');
  mvpn('mvpNotesOverlay').setAttribute('aria-hidden','false');
  mvpNotesApplyInert();
  renderMvpNotesList();
  renderMvpNotesEditor();   // painel da direita começa no estado vazio
  mvpNotesApplyStage();
  // Agora o drawer tem geometria real (antes do .show o rect é 0): ajustar as três colunas
  // contra a largura efetivamente renderizada, já com o teto do CSS aplicado.
  mvpNotesApplyPaneWidths();
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
  mvpn('mvpNotesNewBtn').addEventListener('click',mvpNotesStartNewNote);
  mvpn('mvpNotesSearch').addEventListener('input',e=>{ mvpNotesUI.query=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesFilterType').addEventListener('change',e=>{ mvpNotesUI.filterType=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesFilterStatus').addEventListener('change',e=>{ mvpNotesUI.filterStatus=e.target.value; renderMvpNotesList(); });
  mvpn('mvpNotesFilterPriority').addEventListener('change',e=>{ mvpNotesUI.filterPriority=e.target.value; renderMvpNotesList(); });
  const folderFilter=mvpn('mvpNotesFilterFolder');
  if(folderFilter) folderFilter.addEventListener('change',e=>{ mvpNotesUI.filterFolder=e.target.value; renderMvpNotesList(); });
  const periodFilter=mvpn('mvpNotesFilterPeriod');
  if(periodFilter) periodFilter.addEventListener('change',e=>{ mvpNotesUI.filterPeriod=e.target.value; renderMvpNotesList(); });
  const policyFilter=mvpn('mvpNotesFilterPolicy');
  if(policyFilter) policyFilter.addEventListener('change',e=>{ mvpNotesUI.filterPolicy=e.target.value; renderMvpNotesList(); });
  // Editor de conteúdo único: cada tecla atualiza o rascunho, o título ao vivo e o
  // estado de "não salvo". A gravação continua explícita (botão Salvar), que é o que
  // sustenta a proteção contra descarte silencioso.
  const area=mvpn('mvpNoteContent');
  if(area) area.addEventListener('input',()=>{
    if(!mvpNotesUI.draft) return;
    mvpNotesUI.draft.content=area.value;
    mvpNotesUpdateLiveTitle();
    mvpNotesRecomputeDirty();
  });
  const saveBtn=mvpn('mvpNotesSaveBtn');
  if(saveBtn) saveBtn.addEventListener('click',mvpNotesSaveDraft);
  // Ctrl/Cmd+S salva sem tirar as mãos do teclado.
  if(area) area.addEventListener('keydown',e=>{
    if((e.metaKey||e.ctrlKey) && (e.key==='s'||e.key==='S')){ e.preventDefault(); mvpNotesSaveDraft(); }
  });
  const inspBtn=mvpn('mvpNotesInspectorBtn');
  if(inspBtn) inspBtn.addEventListener('click',()=>mvpNotesSetInspectorOpen(!mvpNotesUI.inspectorOpen));
  const copyRef=mvpn('mvpNotesCopyRefBtn');
  if(copyRef) copyRef.addEventListener('click',()=>{
    if(copyRef.dataset.mvpCopyId) mvpNotesHandleCopy(copyRef.dataset.mvpCopyId,copyRef);
  });
  mvpn('mvpNotesNewFolderBtn').addEventListener('click',mvpNotesHandleNewFolder);
  const backBtn=mvpn('mvpNotesBackBtn');
  if(backBtn) backBtn.addEventListener('click',mvpNotesGoBack);
  const filtersBtn=mvpn('mvpNotesFiltersBtn');
  if(filtersBtn) filtersBtn.addEventListener('click',()=>mvpNotesSetFiltersOpen(!mvpNotesUI.filtersOpen));
  const applyBtn=mvpn('mvpNotesFiltersApplyBtn');
  if(applyBtn) applyBtn.addEventListener('click',()=>mvpNotesSetFiltersOpen(false)); // aplicam ao vivo; Aplicar = fechar
  const clearBtn=mvpn('mvpNotesFiltersClearBtn');
  if(clearBtn) clearBtn.addEventListener('click',mvpNotesClearAllFilters);
  bindMvpNotesResize();
  bindMvpNotesPaneResize();
  bindMvpNotesFolderMenuDismiss();
  // Janela redimensionada: recalcular o que cabe, sem tocar nas preferências. Estreitar e
  // voltar a alargar devolve exatamente a geometria escolhida pelo operador.
  window.addEventListener('resize',()=>{
    if(!mvpNotesUI.open || mvpNotesIsMobile()) return;
    mvpNotesApplyDrawerWidth(mvpNotesClampWidth(mvpNotesDrawerWidth()));
  });
  // Clique fora fecha o popover de filtros (desktop) — o botão e o próprio painel são
  // as únicas áreas "dentro". Sem devolução de foco: o usuário já clicou noutro lugar.
  document.addEventListener('pointerdown',event=>{
    if(!mvpNotesUI.filtersOpen || mvpNotesIsMobile()) return;
    const wrap=mvpn('mvpNotesFiltersWrap'), fbtn=mvpn('mvpNotesFiltersBtn');
    if(wrap && !wrap.contains(event.target) && event.target!==fbtn && !fbtn.contains(event.target)){
      mvpNotesUI.filtersOpen=false;
      wrap.classList.remove('open');
      if(fbtn) fbtn.setAttribute('aria-expanded','false');
    }
  },true);
  document.addEventListener('keydown',event=>{
    if(!mvpNotesUI.open) return;
    if(event.key==='Escape'){
      event.preventDefault();
      // Arraste em curso é a camada mais interna: Escape cancela só ele, sem persistir nada.
      if(mvpNotesUI.folderDrag){ mvpNotesFolderDragCleanup(); return; }
      // Menu "⋯" aberto: Escape dispensa o menu, não a gaveta inteira (JPW-YX2Z43).
      if(mvpNotesFecharMenusDePasta(null)) return;
      if(mvpNotesUI.inspectorOpen){ mvpNotesSetInspectorOpen(false); return; }
      if(mvpNotesUI.filtersOpen){ mvpNotesSetFiltersOpen(false); return; }
      if(mvpNotesUI.stage==='editor'){ mvpNotesConfirmDiscardIfDirty(mvpNotesCloseEditor); return; }
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
