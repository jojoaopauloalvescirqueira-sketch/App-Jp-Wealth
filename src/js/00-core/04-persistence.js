// ============ PERSISTÊNCIA (localStorage) ============
const LSKEY='jpwealth_v9_state';
let S;
let jpWealthPersistenceBlocked=false;
let jpWealthSessionEpoch=0;
function jpWealthPersistenceIsBlocked(){ return jpWealthPersistenceBlocked; }
function jpWealthPersistenceEpoch(){ return jpWealthSessionEpoch; }
function blockJPWealthPersistence(){
  jpWealthPersistenceBlocked=true;
  jpWealthSessionEpoch++;
}
function resumeJPWealthPersistence(){
  // NÃO libera jpWealthPersistenceOutcomeUnknown, e isso é o ponto inteiro da
  // outra barreira: ela existe porque uma gravação posterior pode destruir
  // exatamente o estado que estamos tentando preservar. Um portão genérico
  // reaberto por importação ou onboarding não pode decidir isso.
  jpWealthPersistenceBlocked=false;
  jpWealthSessionEpoch++;
}

// ---- DESFECHO INDETERMINADO DE GRAVAÇÃO -----------------------------------
// Barreira SEPARADA do portão genérico. Erguida quando uma gravação pode ter
// ocorrido e não foi possível provar nem que ocorreu nem que não ocorreu —
// tipicamente: setItem talvez tenha executado e a leitura de volta lançou, ou o
// documento voltou ilegível.
//
// Enquanto ela estiver de pé, NADA grava. O motivo não é excesso de cautela: se
// o disco contém a finalização e a memória for sobrescrita por um save()
// posterior, a finalização persistida desaparece — memória e disco discordando
// sobre se uma operação financeira foi formalmente encerrada é a pior classe de
// defeito que este sistema pode produzir.
//
// A flag NÃO é persistida: persisti-la exigiria justamente a gravação que está
// vetada. É barreira de sessão; o desempate é humano, com o disco à vista.
let jpWealthPersistenceOutcomeUnknown=false;
function jpWealthPersistenceOutcomeIsUnknown(){ return jpWealthPersistenceOutcomeUnknown; }
function markJPWealthPersistenceOutcomeUnknown(motivo){
  jpWealthPersistenceOutcomeUnknown=true;
  jpWealthSessionEpoch++;
  if(typeof console!=='undefined' && console.error){
    console.error('[persistência] DESFECHO INDETERMINADO — novas gravações bloqueadas:', motivo);
  }
}
// ---- MODO DE RECUPERAÇÃO DE CARREGAMENTO (A-005) --------------------------------
// Quando o banco salvo não pode ser carregado com segurança (leitura falhou, JSON
// inválido ou migração lançou), o app abre com DEFAULTS APENAS COMO ESTADO PROVISÓRIO
// de diagnóstico: a chave principal fica intocada, uma cópia bruta é preservada e TODA
// gravação fica vetada até decisão explícita do operador. A flag é própria (não o
// bloqueio genérico) de propósito, como defesa em profundidade: openOnboardingModal()
// chama resumeJPWealthPersistence() e reabriria o portão genérico — sem esta flag, o
// primeiro save() destruiria o banco original. (importFullBackupFile() também reabria
// o portão ANTES da validação; hoje é transacional e só o reabre com candidato
// validado e confirmado, mas a flag continua cobrindo qualquer fluxo futuro.)
const jpWealthLoadRecovery={active:false, kind:null, raw:null, recoveryKey:null, lastError:null};
function jpWealthLoadRecoveryActive(){ return jpWealthLoadRecovery.active; }
function jpWealthFindExistingRecoveryKey(raw){
  // Dedupe seguro (igualdade exata de string): evita uma cópia idêntica nova a cada
  // recarregamento com o mesmo banco problemático. Conteúdo diferente = chave nova.
  try{
    for(let i=0;i<localStorage.length;i++){
      const k=localStorage.key(i);
      if(k && k.startsWith(LSKEY+'_corrompido_') && localStorage.getItem(k)===raw) return k;
    }
  }catch(e){}
  return null;
}
function enterLoadRecoveryMode(kind, raw, error){
  // O bloqueio vem ANTES de qualquer outra coisa: nenhum caminho síncrono ou
  // assíncrono posterior (updateFxRates→save no boot, timers, binds) pode escrever.
  blockJPWealthPersistence();
  jpWealthLoadRecovery.active=true;
  jpWealthLoadRecovery.kind=kind;
  jpWealthLoadRecovery.raw=(raw!=null)?String(raw):null;
  jpWealthLoadRecovery.lastError=error||null;
  jpWealthLoadRecovery.recoveryKey=null;
  if(jpWealthLoadRecovery.raw!=null){
    const existing=jpWealthFindExistingRecoveryKey(jpWealthLoadRecovery.raw);
    if(existing){ jpWealthLoadRecovery.recoveryKey=existing; }
    else{
      const key=LSKEY+'_corrompido_'+Date.now();
      try{ localStorage.setItem(key, jpWealthLoadRecovery.raw); jpWealthLoadRecovery.recoveryKey=key; }
      catch(e){ console.error('JP Wealth: não foi possível gravar a cópia de recuperação — o conteúdo original permanece na chave principal (intocada) e em memória para download.', e); }
    }
  }
  console.error('JP Wealth: o banco salvo não pôde ser carregado com segurança (motivo: '+kind+'). Gravações bloqueadas até decisão do operador.'+(jpWealthLoadRecovery.recoveryKey?' Cópia de recuperação: '+jpWealthLoadRecovery.recoveryKey:''), error);
  renderLoadRecoveryWarning();
}
function load(){
  let raw=null, readError=null;
  try{ raw=localStorage.getItem(LSKEY); }catch(e){ readError=e; }
  if(readError){
    enterLoadRecoveryMode('leitura', null, readError);
  } else if(raw){
    let parsed=null, parseError=null;
    try{ parsed=JSON.parse(raw); }catch(e){ parseError=e; }
    if(parseError || !parsed || typeof parsed!=='object'){
      // Antes, JSON inválido caía silenciosamente em DEFAULTS SEM cópia e SEM bloqueio —
      // o caminho mais destrutivo de todos: o primeiro save() apagava o original.
      enterLoadRecoveryMode('json-invalido', raw, parseError||new Error('conteúdo não é um objeto JSON'));
    } else {
      try{ S=parsed; migrate(); return; }
      catch(e){ enterLoadRecoveryMode('migracao', raw, e); }
    }
  }
  S=structuredClone(DEFAULTS); // provisório: em recuperação, serve só para diagnóstico
}
// ---- Notas do MVP: enums fixos e normalização (14-mvp-notes.js consome os mesmos
// arrays). Definidos aqui — script cedo — porque migrate() roda em load() (06-boot.js)
// antes de 14-mvp-notes.js sequer carregar; a UI só lê estes valores depois. ----
const MVP_NOTES_TYPES=['task','bug','feature','improvement'];
const MVP_NOTES_STATUSES=['open','in_progress','done','discarded'];
const MVP_NOTES_PRIORITIES=['low','medium','high','critical'];
// Geometria canônica do painel de Notas (v3) — fonte ÚNICA, consumida tanto pela
// normalização do estado (abaixo) quanto pelo motor de resize (14-mvp-notes.js). Faixa
// persistível e máximo funcional são o mesmo número: o estado nunca guarda largura que a
// interface não saiba renderizar.
// v5: o painel passa a acomodar TRÊS colunas (pastas | notas | editor). A ordem de
// declaração importa: o mínimo do drawer é DERIVADO dos mínimos das colunas (mais abaixo),
// nunca um número escolhido à mão.
// Painéis internos: faixa e padrão de cada coluna redimensionável. O editor não tem
// largura própria — recebe o espaço restante.
const MVP_NOTES_FOLDERS_MIN=150, MVP_NOTES_FOLDERS_MAX=320, MVP_NOTES_FOLDERS_DEFAULT=190;
// LIST_MIN medido na interface real (v5): abaixo de 240px o campo de busca cai para menos
// de 110px e o placeholder "Buscar notas..." trunca — a busca permanente da Fase C deixa de
// ser utilizável antes de qualquer overflow acontecer. 240 é o menor valor que a mantém legível.
const MVP_NOTES_LIST_MIN=240, MVP_NOTES_LIST_MAX=520, MVP_NOTES_LIST_DEFAULT=300;
// O editor NÃO tem largura persistida — recebe o resto. Mas tem um piso funcional: com a
// barra medida (Trace ID 57 + Salvar 83 + copiar 30 + inspector 30 + folgas 40 + padding 36)
// o conteúdo fixo ocupa ~316px; abaixo disso o título ao vivo desaparece por completo.
const MVP_NOTES_EDITOR_MIN=320;
// Largura que cada separador interno OCUPA no layout. O elemento tem 9px de área de toque
// com margens de -2px de cada lado (.mvpn-pane-handle no CSS), então consome 5px de fluxo.
// Medido no navegador: 9 + (-2) + (-2) = 5.
const MVP_NOTES_PANE_HANDLE=5;
// Chrome estrutural do drawer: tudo que fica entre a largura externa e o espaço útil das
// colunas. Medido na interface real — border-left de 1px, box-sizing:border-box, sem
// padding no drawer nem no corpo (drawer 980 → corpo 979). É UM pixel, não dois: usar 2
// aqui furava a invariante em exatamente 1px na largura mínima, roubando-o da Lista.
const MVP_NOTES_DRAWER_CHROME=1;
// Espaço horizontal que o corpo do drawer oferece às TRÊS colunas, dado um drawer de
// largura `drawerW`: descontados o chrome estrutural e os dois separadores.
function mvpNotesPaneSpace(drawerW){
  return Math.max(0, Math.round(drawerW) - MVP_NOTES_DRAWER_CHROME - (MVP_NOTES_PANE_HANDLE*2));
}
// Mínimo do drawer em modo desktop — DERIVADO, nunca arbitrado: é a menor largura em que
// as três colunas cabem simultaneamente nos seus pisos funcionais.
//
//   drawerMin = pastasMin + listaMin + editorMin + 2*separador + chrome
//             =   150     +   240    +    320    +     10      +   1     = 721
//
// Confirmado por medição: em 721px o editor mede exatamente 320px; em 720px cai para 319.
// O valor anterior (700) era herdado de uma estimativa e permitia editor de 299px — o
// próprio piso que este módulo declara. Alterar qualquer mínimo de coluna recalcula este
// número sozinho, e a invariante continua valendo sem ninguém precisar lembrar.
const MVP_NOTES_DRAWER_MIN=MVP_NOTES_FOLDERS_MIN+MVP_NOTES_LIST_MIN+MVP_NOTES_EDITOR_MIN
                          +(MVP_NOTES_PANE_HANDLE*2)+MVP_NOTES_DRAWER_CHROME;
// Máximo generoso; a renderização o limita à viewport (min(…, 80vw, …) no CSS) sem
// reescrever o valor salvo. Padrão confortável para as três colunas.
const MVP_NOTES_DRAWER_MAX=1600, MVP_NOTES_DRAWER_DEFAULT=980;
// Ajuste de RENDERIZAÇÃO — nunca de persistência.
//
// Duas larguras podem ser válidas isoladamente e não caberem JUNTAS (320 + 520 num drawer
// de 980 não deixa espaço para o editor). Quem resolve isso é esta função, no momento de
// desenhar, e o resultado NÃO volta para o estado: a preferência do operador é dele, e um
// drawer temporariamente estreito não é motivo para apagá-la. Assim que houver espaço de
// novo, o desenho volta sozinho ao que ele havia escolhido.
//
// Estratégia determinística: preserva os mínimos, reduz primeiro a Lista, depois as Pastas,
// e só então o editor cederia. Chamada com a largura RENDERIZADA do drawer neste instante
// (não a persistida), porque é o que de fato existe na tela.
function mvpNotesFitPanes(folders,list,drawerW){
  const espaco=mvpNotesPaneSpace(drawerW);
  let f=Math.min(Math.max(Math.round(folders),MVP_NOTES_FOLDERS_MIN),MVP_NOTES_FOLDERS_MAX);
  let l=Math.min(Math.max(Math.round(list),MVP_NOTES_LIST_MIN),MVP_NOTES_LIST_MAX);
  let excesso=(f+l+MVP_NOTES_EDITOR_MIN)-espaco;
  if(excesso<=0) return {folders:f,list:l};
  const cortaLista=Math.min(excesso,l-MVP_NOTES_LIST_MIN); l-=cortaLista; excesso-=cortaLista;
  if(excesso>0){ const cortaPastas=Math.min(excesso,f-MVP_NOTES_FOLDERS_MIN); f-=cortaPastas; excesso-=cortaPastas; }
  // Sobrou excesso: as duas colunas já estão no mínimo e o editor absorveria a diferença.
  // Com MVP_NOTES_DRAWER_MIN derivado dos três pisos, este ramo é INALCANÇÁVEL em desktop
  // (espaço mínimo = 710 = 150+240+320). Fica como rede de segurança para geometrias
  // degeneradas — o corpo tem overflow:hidden, nada vaza e nada fica negativo.
  return {folders:f,list:l};
}
function mvpNotesId(){ return 'mvpn_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }
function mvpNotesFolderId(){ return 'mvpnf_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }
// ---- código de rastreio (v4) ----------------------------------------------------
// Identificador curto e legível de cada nota (JPW-XXXXXX), feito para SAIR do app: ser
// colado num agente de IA, citado em mensagem de commit ou em nome de branch. Alfabeto
// sem caracteres ambíguos (nada de 0/O, 1/I/L, U) — sobrevive a ser lido em voz alta e
// digitado à mão. É DERIVADO do id interno por hash determinístico: o mesmo id sempre
// produz o mesmo código, em qualquer navegador e a qualquer momento, então uma nota
// antiga recebe na migração exatamente o código que teria se o campo já existisse.
const MVP_NOTES_TICKET_ALPHABET='23456789ABCDEFGHJKMNPQRSTVWXYZ';
const MVP_NOTES_TICKET_RE=/^JPW-[23456789ABCDEFGHJKMNPQRSTVWXYZ]{6}$/;
function mvpNotesTicketFromSeed(seed){
  // FNV-1a de 32 bits, uma passada por posição (semente + índice): determinístico, sem
  // Date/Math.random, e bem distribuído entre as 6 posições.
  let out='';
  for(let i=0;i<6;i++){
    let h=0x811c9dc5;
    const s=String(seed)+'#'+i;
    for(let j=0;j<s.length;j++){ h^=s.charCodeAt(j); h=Math.imul(h,0x01000193)>>>0; }
    out+=MVP_NOTES_TICKET_ALPHABET[h%MVP_NOTES_TICKET_ALPHABET.length];
  }
  return 'JPW-'+out;
}
function mvpNotesTicketIsValid(t){ return typeof t==='string' && MVP_NOTES_TICKET_RE.test(t); }
// Um ticket JÁ PERSISTIDO e válido é imutável: nunca é recalculado, nem quando o id muda
// por deduplicação. Só quem chega sem ticket (nota antiga, backup v1/v2/v3) recebe um
// derivado do id. Colisão é improvável mas não impossível: re-deriva com sufixo até achar
// livre — dois códigos iguais tornariam falsa a rastreabilidade prometida.
// IMPORTANTE: `seenTickets` precisa chegar aqui JÁ PRÉ-CARREGADO com todos os tickets
// válidos do lote (ver mvpNotesNormalizeState). Sem essa reserva prévia, um ticket
// derivado para a nota A poderia ocupar o código que a nota B já tinha persistido, e B
// — válida e imutável — seria forçada a mudar.
function mvpNotesResolveTicket(rawTicket,id,seenTickets,reserved){
  if(mvpNotesTicketIsValid(rawTicket)){
    // Conflito entre dois tickets persistidos iguais: o primeiro a aparecer mantém o
    // código; o segundo é rebaixado a derivado (não há como saber qual era "o certo").
    if(!seenTickets.has(rawTicket)){ seenTickets.add(rawTicket); return rawTicket; }
  }
  let ticket=mvpNotesTicketFromSeed(id), attempt=0;
  while(seenTickets.has(ticket) || (reserved && reserved.has(ticket))){ attempt++; ticket=mvpNotesTicketFromSeed(id+'~'+attempt); }
  seenTickets.add(ticket);
  return ticket;
}
// ---- política de implementação por IA (v5) --------------------------------------
// Diz o que um agente pode fazer com a nota. NUNCA autoriza commit, push, merge ou
// deploy — essas permissões seguem governadas pelo processo do projeto, fora da nota.
// O padrão é o cauteloso: analisar sim, alterar código não.
const MVP_NOTES_AI_POLICIES=['blocked','analysis_only','autonomous_allowed'];
const MVP_NOTES_AI_POLICY_DEFAULT='analysis_only';

// ---- conteúdo e título derivado (v5) ---------------------------------------------
// A nota passa a ter UM corpo de texto (content). O título deixa de ser campo editável
// e vira a primeira linha não vazia do conteúdo — persistido ainda assim, para busca,
// backup e para não recalcular a cada render de lista.
function mvpNotesDeriveTitle(content){
  const linhas=String(content||'').split('\n');
  for(const l of linhas){ const t=l.trim(); if(t) return t.slice(0,120); }
  return '';
}
// Migração v≤4 → v5: title e description viram um único content, nesta ordem e sem
// perder um caractere. Um backup antigo com título "X" e descrição "Y" produz "X\nY".
function mvpNotesMigrateContent(raw){
  if(typeof raw.content==='string' && raw.content) return raw.content.slice(0,20000);
  const titulo=String(raw.title||'').trim();
  const desc=String(raw.description||'');
  if(titulo && desc.trim()) return (titulo+'\n'+desc).slice(0,20000);
  return (titulo || desc).slice(0,20000);
}

// ---- pastas (schemaVersion 2; ordem manual em v5) — normalizadas ANTES dos itens:
// mvpNotesNormalizeItem() precisa do conjunto de IDs válidos/ambíguos resultante para
// reconciliar item.folderId. ----
function mvpNotesNormalizeFolders(rawList){
  const seenIds=new Set();
  const ambiguousIds=new Set(); // ID original que apareceu mais de uma vez no backup — uma
  // nota que referenciava esse ID não tem como saber qual das duas pastas era a pretendida.
  const folders=[];
  (Array.isArray(rawList)?rawList:[]).forEach(raw=>{
    if(!raw || typeof raw!=='object') return;
    const name=String(raw.name||'').trim();
    if(!name) return; // pasta sem nome não é preservada — não existe "pasta vazia de nome"
    let id=String(raw.id||'').trim();
    if(!id){ id=mvpNotesFolderId(); }
    else if(seenIds.has(id)){
      ambiguousIds.add(id); // preserva o primeiro ID válido; a duplicata recebe ID novo
      id=mvpNotesFolderId();
    }
    seenIds.add(id);
    const createdAt=(typeof raw.createdAt==='string'&&raw.createdAt)?raw.createdAt:new Date().toISOString();
    const updatedAt=(typeof raw.updatedAt==='string'&&raw.updatedAt)?raw.updatedAt:createdAt;
    // position (v5): ordem manual escolhida pelo operador. Número finito qualquer é
    // aceito na entrada; a reindexação abaixo o converte em inteiros contíguos 0..n-1.
    const rawPos=Number(raw.position);
    folders.push({id, name:name.slice(0,80), position:Number.isFinite(rawPos)?rawPos:Number.MAX_SAFE_INTEGER, createdAt, updatedAt});
  });
  // Ordena pela posição declarada (pastas sem posição — backups v≤4 — vão para o fim,
  // preservando entre si a ordem original do array) e reindexa contíguo. Assim a ordem
  // é sempre densa e determinística, e mover uma pasta nunca deixa buracos.
  folders.forEach((f,i)=>{ f.__seq=i; });
  folders.sort((a,b)=> a.position-b.position || a.__seq-b.__seq);
  folders.forEach((f,i)=>{ f.position=i; delete f.__seq; });
  return {folders, validIds:seenIds, ambiguousIds};
}
function mvpNotesResolveFolderId(rawFolderId,validIds,ambiguousIds){
  const id=String(rawFolderId||'').trim();
  if(!id) return null; // ausente = Sem pasta
  if(ambiguousIds.has(id)) return null; // referência ambígua = Sem pasta, nunca inventa vínculo
  if(!validIds.has(id)) return null; // pasta inexistente = Sem pasta
  return id;
}
function mvpNotesNormalizeItem(raw,seenIds,validFolderIds,ambiguousFolderIds,seenTickets,reservedTickets){
  if(!raw || typeof raw!=='object') return null;
  // v5: o conteúdo é a fonte da verdade e o título é derivado dele. Backups v≤4 têm
  // title+description e são fundidos aqui (mvpNotesMigrateContent) sem perda.
  const content=mvpNotesMigrateContent(raw);
  const title=mvpNotesDeriveTitle(content);
  if(!title) return null; // nota sem nenhum texto não é preservada — nada a rastrear
  let id=String(raw.id||'').trim();
  if(!id || seenIds.has(id)) id=mvpNotesId(); // impede ID ausente/duplicado
  seenIds.add(id);
  const createdAt=(typeof raw.createdAt==='string'&&raw.createdAt)?raw.createdAt:new Date().toISOString();
  const updatedAt=(typeof raw.updatedAt==='string'&&raw.updatedAt)?raw.updatedAt:createdAt;
  const status=MVP_NOTES_STATUSES.includes(raw.status)?raw.status:'open';
  // completedAt: só existe enquanto status==='done'. Migração determinística de notas
  // antigas concluídas sem o campo: usa updatedAt (último toque conhecido ≈ momento em
  // que foi marcada concluída) — nunca inventa data nova. Fora de 'done' é sempre null,
  // mesmo que o backup traga um valor: a visão Concluído é derivada do status, e um
  // completedAt órfão viraria estado fantasma.
  let completedAt=(typeof raw.completedAt==='string'&&raw.completedAt)?raw.completedAt:null;
  if(status==='done' && !completedAt) completedAt=updatedAt;
  if(status!=='done') completedAt=null;
  return {
    id,
    ticket:mvpNotesResolveTicket(raw.ticket,id,seenTickets,reservedTickets),
    type:MVP_NOTES_TYPES.includes(raw.type)?raw.type:'task',
    content,
    title, // derivado de content — nunca editado por si só
    // Política de IA: só os três estados conhecidos entram. Qualquer valor estranho
    // (backup adulterado, versão futura) cai no padrão cauteloso, JAMAIS em
    // autonomous_allowed — um erro de leitura não pode virar autorização.
    aiImplementationPolicy:MVP_NOTES_AI_POLICIES.includes(raw.aiImplementationPolicy)?raw.aiImplementationPolicy:MVP_NOTES_AI_POLICY_DEFAULT,
    priority:MVP_NOTES_PRIORITIES.includes(raw.priority)?raw.priority:'medium',
    status,
    folderId:mvpNotesResolveFolderId(raw.folderId,validFolderIds,ambiguousFolderIds),
    screenId:String(raw.screenId||''),
    // buildId e sourceRevision são conceitos DISTINTOS e nenhum deriva do outro:
    //   buildId        = impressão digital de CONTEÚDO (sha256 de index/css/js/sw/ícones,
    //                    ver tools/rebuild_monolith.py). Dois commits que não alterem
    //                    esses arquivos geram o MESMO buildId; árvore suja gera um
    //                    buildId que não corresponde a commit algum.
    //   sourceRevision = revisão Git que originou o build. Hoje o app NÃO tem como
    //                    conhecê-la (nenhum passo de build injeta SHA), então fica null
    //                    e a interface diz "não disponível". Jamais inventado nem
    //                    derivado do buildId. Se um dia o build passar a definir
    //                    JP_WEALTH_SOURCE_REVISION, notas novas o capturam sozinhas.
    buildId:String(raw.buildId||''),
    sourceRevision:(typeof raw.sourceRevision==='string' && raw.sourceRevision) ? raw.sourceRevision : null,
    createdAt,
    updatedAt,
    completedAt
  };
}
function mvpNotesNormalizeState(){
  if(!S.mvpNotes || typeof S.mvpNotes!=='object') S.mvpNotes=structuredClone(DEFAULTS.mvpNotes);
  // Histórico do schema deste módulo:
  //   v1 = notas soltas, sem pastas (items[] apenas);
  //   v2 = pastas reais (folders[]) + item.folderId;
  //   v3 = item.completedAt (carimbo de conclusão) + ui{} (preferências persistidas do
  //        painel, hoje drawerWidth) + a visão virtual "Concluído", derivada de
  //        status==='done' e NUNCA gravada em folders[];
  //   v4 = item.ticket (código curto de rastreio JPW-XXXXXX, derivado do id por hash
  //        determinístico e IMUTÁVEL depois de persistido) + item.sourceRevision
  //        (revisão Git de origem, hoje sempre null — ver comentário no item);
  //   v5 = item.content (corpo único; title vira DERIVADO da primeira linha e
  //        description é absorvida sem perda) + item.aiImplementationPolicy +
  //        folder.position (ordem manual) + ui.foldersPaneWidth/notesPaneWidth.
  // A migração é idempotente e sem perda: backups v1..v4 sobem para v5 aqui (v1 ganha
  // folders:[] e todas as notas caem em "Sem pasta"; v2 ganha completedAt derivado e ui
  // com o padrão; v1..v3 ganham ticket derivado do id, sempre o mesmo; v≤4 tem
  // title+description fundidos em content e recebe política de IA no padrão cauteloso e
  // posição de pasta pela ordem vigente). Rodar de novo sobre um estado já v5 não altera
  // mais nada — todas as derivações são funções puras do dado já normalizado.
  S.mvpNotes.schemaVersion=5;
  S.mvpNotes.showHeaderIcon=S.mvpNotes.showHeaderIcon!==false; // padrão true; só desliga com false explícito
  // Preferências de interface do módulo (v3) — viajam no estado principal, logo entram no
  // backup/importação e sobrevivem a Finalizar Sessão como o resto de S.mvpNotes.
  // REGRA (v5/Fase D): estas três larguras são PREFERÊNCIAS. A normalização valida cada uma
  // na sua própria faixa e nada além disso; a geometria que cabe na tela é decidida no
  // desenho por mvpNotesFitPanes(), sem nunca reescrever o que está guardado aqui.
  // drawerWidth: faixa canônica única (MVP_NOTES_DRAWER_MIN..MAX) — o estado nunca guarda
  // valor impossível. Valor fora da faixa é APARADO (preserva a intenção do operador),
  // não descartado; só valor ausente/não-numérico cai no padrão. A viewport ainda limita
  // a renderização ao vivo (min(persistido, 80vw, MAX) no CSS/motor de resize) sem
  // reescrever o valor guardado — telas menores não destroem a preferência.
  if(!S.mvpNotes.ui || typeof S.mvpNotes.ui!=='object') S.mvpNotes.ui={};
  // null/''/booleano são AUSÊNCIA, não "zero": sem esta guarda Number(null)===0 seria
  // finito e cairia no mínimo (420) em vez do padrão — divergindo de undefined (460).
  // Mesma regra para as três larguras: ausência (null/''/booleano/undefined) cai no
  // padrão; valor fora da faixa é APARADO, nunca descartado.
  const larguraValida=(bruto,min,max,padrao)=>{
    const n=(bruto===null || bruto==='' || typeof bruto==='boolean') ? NaN : Number(bruto);
    return Number.isFinite(n) ? Math.min(Math.max(Math.round(n),min),max) : padrao;
  };
  S.mvpNotes.ui.drawerWidth=larguraValida(S.mvpNotes.ui.drawerWidth,MVP_NOTES_DRAWER_MIN,MVP_NOTES_DRAWER_MAX,MVP_NOTES_DRAWER_DEFAULT);
  S.mvpNotes.ui.foldersPaneWidth=larguraValida(S.mvpNotes.ui.foldersPaneWidth,MVP_NOTES_FOLDERS_MIN,MVP_NOTES_FOLDERS_MAX,MVP_NOTES_FOLDERS_DEFAULT);
  S.mvpNotes.ui.notesPaneWidth=larguraValida(S.mvpNotes.ui.notesPaneWidth,MVP_NOTES_LIST_MIN,MVP_NOTES_LIST_MAX,MVP_NOTES_LIST_DEFAULT);
  // E PARA por aqui, deliberadamente: cada preferência é validada isoladamente, nunca a
  // combinação. Um estado 721/190/300 é legítimo — significa "gosto de 190 e 300, hoje meu
  // painel está no mínimo". Reduzir 190/300 para 150/240 aqui apagaria a escolha do operador
  // por causa de uma condição passageira, e ao alargar o painel de novo não haveria o que
  // restaurar. Quem faz as três colunas caberem é mvpNotesFitPanes(), no desenho.
  // Estado v1 (sem folders) chega aqui com S.mvpNotes.folders===undefined — normaliza para []
  // e cada nota, sem folderId prévio, resolve para null (Sem pasta) abaixo. Sem tela de
  // migração: o operador só vê o resultado (tudo em "Sem pasta") ao abrir o painel.
  const {folders,validIds,ambiguousIds}=mvpNotesNormalizeFolders(S.mvpNotes.folders);
  S.mvpNotes.folders=folders;
  const seenIds=new Set(), seenTickets=new Set();
  const rawItems=Array.isArray(S.mvpNotes.items)?S.mvpNotes.items:[];
  // Duas passadas: primeiro RESERVA todo ticket válido já persistido, depois normaliza.
  // Assim um código derivado nunca rouba o código imutável de outra nota do mesmo lote.
  const reserved=new Set();
  rawItems.forEach(it=>{ if(it && typeof it==='object' && mvpNotesTicketIsValid(it.ticket)) reserved.add(it.ticket); });
  S.mvpNotes.items=rawItems
    .map(item=>mvpNotesNormalizeItem(item,seenIds,validIds,ambiguousIds,seenTickets,reserved))
    .filter(Boolean);
}
// ---- Governança da base de dados (JPW-HJFGDE) ------------------------------------
// Constantes e normalização do agregado S.dataGovernance. A lógica de filesystem vive
// em 06-storage-fs.js (IndexedDB + File System Access); aqui ficam só as regras de
// ESTADO: schema, sequência de exportação, backups confirmados e auditoria resumida.
const DG_SCHEMA_VERSION=1;
const DG_RESPONSIBILITY_VERSION=1; // versão do texto do termo de responsabilidade
const DG_BACKUP_DUE_DAYS=30;       // aviso de backup após N dias sem confirmação (§10)
// Teto do changeLog: auditoria RESUMIDA, não histórico infinito. 400 entradas cobrem
// meses de operação real e mantêm o custo no localStorage desprezível; poda pela frente
// (mais antigas saem primeiro). O resumo "N alterações desde o backup" continua correto
// enquanto o log não podar entradas posteriores a lastConfirmedAt — com 400 de folga,
// isso exigiria 400 alterações sem nenhum backup, exatamente o cenário que o aviso de
// 30 dias existe para impedir.
const DG_CHANGELOG_MAX=400;
function dgId(){ return 'dg_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }
// Nome progressivo de exportação (§8): legível, determinístico, ordenável.
//   JP_WEALTH_DB_000042_2026-08-08_0026.json
// .json é a extensão real já usada pelo backup completo. Sequência com 6 dígitos
// preserva ordenação lexicográfica até 999999; data/hora local do operador (o backup é
// um artefato humano — a hora que ele vê no relógio é a que procura depois no Finder).
function dgExportFileName(seq,when){
  const t=when instanceof Date?when:new Date();
  const pad=n=>String(n).padStart(2,'0');
  return 'JP_WEALTH_DB_'+String(Math.max(1,Math.round(seq))).padStart(6,'0')
    +'_'+t.getFullYear()+'-'+pad(t.getMonth()+1)+'-'+pad(t.getDate())
    +'_'+pad(t.getHours())+pad(t.getMinutes())+'.json';
}
// Registra um evento no log resumido. NÃO chama save(): quem muta o estado é quem
// persiste — todos os pontos instrumentados já chamam save() logo depois, e o log entra
// na mesma gravação. label é o texto humano do detalhamento cronológico (§11).
// `alvo` opcional: escreve num estado CANDIDATO em vez da global. Existe para
// que uma transação possa montar o log de auditoria dentro do próprio candidato
// e persistir tudo numa gravação só — que é exatamente a doutrina enunciada
// acima. Sem ele, um fluxo transacional só teria a opção de registrar DEPOIS do
// save(), e o evento nunca chegaria ao disco. Omitido, o comportamento é o de
// sempre: muta a global.
function dgLogChange(entity,action,recordId,label,alvo){
  const st=alvo||S;
  if(!st.dataGovernance || !Array.isArray(st.dataGovernance.changeLog)) return;
  st.dataGovernance.changeLog.push({
    id:dgId(), ts:new Date().toISOString(),
    entity:String(entity||''), action:String(action||''),
    recordId:recordId==null?'':String(recordId), label:String(label||''),
  });
  if(st.dataGovernance.changeLog.length>DG_CHANGELOG_MAX){
    st.dataGovernance.changeLog=st.dataGovernance.changeLog.slice(-DG_CHANGELOG_MAX);
  }
}
// Alterações desde o último backup CONFIRMADO (§11). Sem confirmação nunca feita,
// tudo que está no log conta. Retorna as entradas em ordem cronológica.
function dgChangesSinceLastBackup(){
  const dg=S.dataGovernance||{};
  const since=dg.backup&&dg.backup.lastConfirmedAt?dg.backup.lastConfirmedAt:'';
  const log=Array.isArray(dg.changeLog)?dg.changeLog:[];
  return since?log.filter(e=>e.ts>since):log.slice();
}
// Dias inteiros desde o último backup confirmado; null = nunca confirmado.
function dgBackupAgeDays(){
  const dg=S.dataGovernance||{};
  const iso=dg.backup&&dg.backup.lastConfirmedAt;
  if(!iso) return null;
  const t=Date.parse(iso);
  if(!Number.isFinite(t)) return null;
  return Math.floor((Date.now()-t)/86400000);
}
// Aviso devido (§10): 30 dias desde a última confirmação. "Nunca confirmado" só cobra
// depois que existe o que proteger — base com atividade (onboarding concluído) e alguma
// alteração registrada; senão o aviso nasceria junto com a base vazia, e intrusão é
// exatamente o que o §18 pede para evitar.
function dgBackupDue(){
  const age=dgBackupAgeDays();
  if(age!==null) return age>=DG_BACKUP_DUE_DAYS;
  return !!(S.onboarding&&S.onboarding.done) && dgChangesSinceLastBackup().length>0;
}
// Confirmação explícita de backup em dia (§9/§10): SÓ por gesto do operador, nunca como
// efeito colateral de exportar. Registra o momento e a sequência coberta.
function dgConfirmBackup(){
  if(!S.dataGovernance) return;
  S.dataGovernance.backup.lastConfirmedAt=new Date().toISOString();
  S.dataGovernance.backup.lastConfirmedExportSequence=S.dataGovernance.export.lastSequence||0;
  dgLogChange('backup','confirmed','','Backup confirmado pelo operador');
  save();
}
// Normalização do agregado — mesma disciplina do resto do migrate(): base antiga sem o
// agregado já recebeu DEFAULTS acima; aqui valida forma campo a campo, sem perda e sem
// inventar dado. Um termo nunca aceito continua não aceito; uma sequência absurda vira 0
// (nunca "some" um arquivo já exportado — o número só cresce a partir do que há).
function dgNormalizeState(){
  if(!S.dataGovernance || typeof S.dataGovernance!=='object' || Array.isArray(S.dataGovernance)){
    S.dataGovernance=structuredClone(DEFAULTS.dataGovernance);
  }
  const dg=S.dataGovernance;
  for(const k in DEFAULTS.dataGovernance){ if(!(k in dg)) dg[k]=structuredClone(DEFAULTS.dataGovernance[k]); }
  dg.schemaVersion=DG_SCHEMA_VERSION;
  if(!dg.responsibility || typeof dg.responsibility!=='object') dg.responsibility=structuredClone(DEFAULTS.dataGovernance.responsibility);
  dg.responsibility.accepted=dg.responsibility.accepted===true;
  dg.responsibility.acceptedAt=dg.responsibility.accepted?String(dg.responsibility.acceptedAt||''):'';
  dg.responsibility.version=Number.isFinite(+dg.responsibility.version)&&+dg.responsibility.version>0?Math.round(+dg.responsibility.version):DG_RESPONSIBILITY_VERSION;
  if(!dg.storage || typeof dg.storage!=='object') dg.storage=structuredClone(DEFAULTS.dataGovernance.storage);
  dg.storage.configured=dg.storage.configured===true;
  dg.storage.folderName=String(dg.storage.folderName||'');
  dg.storage.folderDisplayPath=String(dg.storage.folderDisplayPath||'');
  dg.storage.configuredAt=String(dg.storage.configuredAt||'');
  // metadado sem nome de pasta é metadado vazio — não existe "configurado" sem pasta
  if(dg.storage.configured && !dg.storage.folderName) dg.storage.configured=false;
  if(!dg.export || typeof dg.export!=='object') dg.export=structuredClone(DEFAULTS.dataGovernance.export);
  const seq=+dg.export.lastSequence;
  dg.export.lastSequence=Number.isFinite(seq)&&seq>0?Math.round(seq):0;
  dg.export.lastExportAt=String(dg.export.lastExportAt||'');
  dg.export.lastExportFile=String(dg.export.lastExportFile||'');
  if(!dg.backup || typeof dg.backup!=='object') dg.backup=structuredClone(DEFAULTS.dataGovernance.backup);
  dg.backup.lastConfirmedAt=String(dg.backup.lastConfirmedAt||'');
  const cseq=+dg.backup.lastConfirmedExportSequence;
  dg.backup.lastConfirmedExportSequence=Number.isFinite(cseq)&&cseq>0?Math.round(cseq):0;
  dg.changeLog=(Array.isArray(dg.changeLog)?dg.changeLog:[])
    .filter(e=>e&&typeof e==='object'&&typeof e.ts==='string'&&e.ts)
    .map(e=>({id:String(e.id||dgId()), ts:e.ts, entity:String(e.entity||''),
      action:String(e.action||''), recordId:String(e.recordId||''), label:String(e.label||'')}))
    .slice(-DG_CHANGELOG_MAX);
}
// ---- FRONTEIRA DE CONFIANÇA: metadata estrutural não é dado do operador ------------
// Nenhuma tela do app escreve o rótulo/classe de uma fase nem o nome de um instrumento:
// são catálogo fechado, nascem em DEFAULTS e só de lá. Um backup, porém, é arquivo
// externo — e migrate() é o ponto único por onde passam tanto o load() do localStorage
// quanto a importação (normalizeImportedState). Reconstruir o catálogo aqui, a partir da
// fonte oficial, é o que impede um arquivo adulterado de plantar marcação nesses campos
// e vê-la interpretada pelos templates de renderização e regravada no localStorage.
// Dados do operador — ordens, preços, tetos, banimentos, saldos — não são tocados.
const PHASE_STRUCTURAL_KEYS=['title','cls','faseNome','ddtxt','alavtxt'];
function canonicalizeStructuralMetadata(){
  if(Array.isArray(S.phases)){
    S.phases.forEach((ph,i)=>{
      // Base legítima nunca tem uma quinta grade (o app não cria fase); se vier uma,
      // ela herda a metadata da última fase conhecida em vez de manter string arbitrária.
      const ref=DEFAULTS.phases[Math.min(i,DEFAULTS.phases.length-1)];
      if(!ph || typeof ph!=='object'){
        // Ordens vazias de propósito: a metadata é restaurada, mas nenhuma operação
        // fictícia dos DEFAULTS entra numa base real.
        S.phases[i]={...structuredClone(ref), orders:[]};
        return;
      }
      PHASE_STRUCTURAL_KEYS.forEach(k=>{ ph[k]=ref[k]; });
      if(!Array.isArray(ph.orders)) ph.orders=[];
    });
  }
  // Ticker é sempre alfanumérico maiúsculo — a mesma normalização que o app já aplica a
  // `o.par` antes de comparar instrumentos. Todo nome legítimo (EURUSD, US500) atravessa
  // intacto; o que não é ticker deixa de ser marcação.
  if(Array.isArray(S.instruments)){
    S.instruments.forEach(ins=>{
      if(ins && typeof ins==='object') ins.name=String(ins.name||'').toUpperCase().replace(/[^A-Z0-9]/g,'');
    });
  }
  // Matriz Quadrifásica: catálogo fechado pela MESMA razão das fases acima — nenhuma tela
  // do app escreve ddmin/ddmax/alav. O card em Parâmetros é somente-leitura (tbody vazio
  // preenchido por render, sem input), enquanto pMDD/pAlarm/pGenRisk ao lado SÃO editáveis:
  // a matriz é justamente o que a interface nega ao operador.
  //
  // A guarda adiante valida a FORMA (4 linhas, campos numéricos) e por isso deixava passar
  // qualquer VALOR vindo de arquivo. Um backup com ddmax:0.99/alav:99 atravessava e passava
  // a definir a fase vigente, o teto de risco e o teto de alavancagem — compute(),
  // phaseTetoRisco() e o veredito de coerência leem daqui. O terminal exibiria "COERENTE"
  // com exposição muito além do limite estatutário.
  //
  // Isto NÃO altera parâmetro normativo: reconstrói a matriz a partir da fonte oficial
  // (DEFAULTS, que expressa o Estatuto) em vez de aceitar a do arquivo. Nenhum valor novo
  // é introduzido e nenhum dado do operador é tocado — ordens, preços, tetos por
  // instrumento, banimentos e saldos seguem intactos.
  if(Array.isArray(S.matrix)) S.matrix=structuredClone(DEFAULTS.matrix);
}
// ---- Planejamento FX: guarda ESTRUTURAL do agregado no boot ----
// migrate() roda em load() (06-boot.js) antes dos módulos 05-fx-planning/**
// carregarem — mesmo motivo pelo qual mvpNotes/dg normalizam aqui. Este guard
// garante só a FORMA do envelope (schemaVersion, plan objeto|null, auditLog
// array, poda em 400 como o dg changeLog); nada além disso é apagado ou
// inventado — campos desconhecidos atravessam intactos (STATE-SCHEMA.md §3).
// A normalização PROFUNDA (meses, premissas, aportes) acontece em cópia na
// camada de acesso (05-fx-planning/03-fx-state.js), que só roda após a carga
// completa e nunca grava a versão limpa de volta sem mutação explícita.
function fxPlanningNormalizeState(){
  if(!S.fxPlanning || typeof S.fxPlanning!=='object' || Array.isArray(S.fxPlanning))
    S.fxPlanning=structuredClone(DEFAULTS.fxPlanning);
  const fx=S.fxPlanning;
  if(!Number.isFinite(+fx.schemaVersion) || +fx.schemaVersion<1) fx.schemaVersion=1;
  if(fx.plan!==null && (typeof fx.plan!=='object' || Array.isArray(fx.plan))) fx.plan=null;
  if(fx.plan && (!fx.plan.baseline || typeof fx.plan.baseline!=='object' || Array.isArray(fx.plan.baseline))) fx.plan=null; // sem baseline não há plano válido
  if(fx.plan){
    if(!fx.plan.current || typeof fx.plan.current!=='object' || Array.isArray(fx.plan.current)) fx.plan.current=structuredClone(fx.plan.baseline);
    if(!fx.plan.actuals || typeof fx.plan.actuals!=='object' || Array.isArray(fx.plan.actuals)) fx.plan.actuals={};
    if(!Array.isArray(fx.plan.contributions)) fx.plan.contributions=[];
    if(!Array.isArray(fx.plan.revisions)) fx.plan.revisions=[];
  }
  if(!Array.isArray(fx.auditLog)) fx.auditLog=[];
  if(fx.auditLog.length>400) fx.auditLog=fx.auditLog.slice(-400);
}
// Estudos NoCoda: guarda ESTRUTURAL de boot. Vive aqui, e não no módulo da
// feature, porque migrate() roda dentro de load() antes de qualquer script
// tardio existir — o mesmo motivo dos três normalizadores acima.
//
// A guarda é deliberadamente conservadora: descarta apenas o que tem FORMA
// errada e preserva campos desconhecidos dentro de cada estudo, conforme
// STATE-SCHEMA.md §3. Não valida a matemática das âncoras — um estudo
// numericamente incoerente é problema da camada de cálculo, que simplesmente
// não produz geometria; apagá-lo aqui destruiria entrada do operador em
// silêncio, no caminho que também atende backup importado.
function nocodaNormalizeState(){
  if(!S.nocoda || typeof S.nocoda!=='object' || Array.isArray(S.nocoda))
    S.nocoda=structuredClone(DEFAULTS.nocoda);
  const nc=S.nocoda;
  if(!Number.isFinite(+nc.schemaVersion) || +nc.schemaVersion<1) nc.schemaVersion=1;
  if(!nc.studies || typeof nc.studies!=='object' || Array.isArray(nc.studies)) nc.studies={};
  for(const key of Object.keys(nc.studies)){
    const study=nc.studies[key];
    // Chave fora da forma canônica de instrumentId() não é descartada: é
    // REALOCADA para a chave canônica, para não perder memória técnica de uma
    // base gravada com espaçamento ou caixa diferente.
    const canonical=String(key).toUpperCase().replace(/[^A-Z0-9]/g,'');
    if(!study || typeof study!=='object' || Array.isArray(study)){ delete nc.studies[key]; continue; }
    for(const anchorKey of ['anchor1','anchor2','anchor3']){
      const a=study[anchorKey];
      if(!a || typeof a!=='object' || Array.isArray(a)) study[anchorKey]={datetime:'', price:null};
    }
    if(canonical && canonical!==key){
      if(!(canonical in nc.studies)) nc.studies[canonical]=study;
      delete nc.studies[key];
    } else if(!canonical){ delete nc.studies[key]; }
  }
}
// Estudos dos Pivots: identidade dos registros. Mesmo formato dos ids do app
// (prefixo + tempo em base 36 + sufixo aleatório) — nenhum esquema novo.
function pivotStudyId(){ return 'pvs_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }
function pivotRecordId(){ return 'pv_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }
// Estudos dos Pivots: guarda ESTRUTURAL de boot, pelo mesmo motivo dos quatro
// normalizadores acima — migrate() roda dentro de load() antes de qualquer
// script tardio existir, e é também o caminho por onde passa backup importado.
//
// Conservadora por contrato: descarta apenas o que não tem FORMA de registro e
// preserva campos desconhecidos (STATE-SCHEMA.md §3). NÃO valida a matemática
// nem o critério de correção — pivot incoerente simplesmente não produz
// derivados e fica fora da estatística; apagá-lo aqui destruiria memória
// técnica do operador em silêncio. Timeframe fora de H1/H4 também sobrevive:
// deixa de contar nas sínteses por timeframe, e nada mais.
// ---- Operação Única: identidade, ciclo de vida e histórico (Camada 1) ----
// Mesma forma dos geradores de id já existentes no arquivo. Não precisa ser
// determinístico; precisa ser PERMANENTE — gerado uma vez, persistido, jamais
// recalculado a partir de campo mutável.
function operationRecordId(){ return 'op_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8); }

// Índice de fase CONHECIDO, ou null. Existe porque a coerção numérica destrói a
// distinção que este campo carrega: `+null === 0`, `Number.isFinite(0) === true`
// e `0 < 0` é falso, então toda guarda escrita com `+valor` deixava um
// DESCONHECIDO virar "Fase 1 observada" — uma afirmação sobre o passado que
// ninguém fez. Só number finito conta como conhecido; null, undefined, string
// de backup adulterado e negativo devolvem null.
function operationPhaseIdxOrNull(v){
  if(typeof v!=='number' || !Number.isFinite(v) || v<0) return null;
  return Math.min(3, Math.floor(v));
}

// Carimba um evento de transição com a identidade da operação VIVA no ato, e
// com a Fase da Grade efetivamente atingida.
//
// O vínculo é criado no INSTANTE da transição, quando a identidade é conhecida.
// Não existe migração retroativa: atribuir operationId a evento antigo por
// inferência — janela temporal, ordem dos eventos, proximidade do openedAt —
// fabricaria uma associação que ninguém observou. Evento legado fica sem
// vínculo e, por isso, fora de qualquer derivação escopada.
//
// Sem operação viva, `null`: vínculo ausente é melhor que vínculo inventado.
//
// gridPhase é EXPLÍCITO em vez de derivado do campo `fase`, que é heterogêneo —
// numérico no destravamento por questionário, texto no downgrade e no stop
// quantitativo. Ler string para descobrir fase seria adivinhação, e o caminho
// do stop destrava fase sem nunca escrever um número.
function operationStampTransition(ev, gridPhaseIdx){
  if(!ev || typeof ev!=='object') return ev;
  const op=S.activeOperation;
  ev.operationId=(op && typeof op.operationId==='string' && op.operationId)?op.operationId:null;
  const idx=operationPhaseIdxOrNull(gridPhaseIdx);
  if(idx!==null) ev.gridPhase=idx;
  return ev;
}

// Sonda da Fase da Conta VIGENTE. Distingue TRÊS desfechos, e a distinção é o
// ponto todo — antes, um `catch` mudo fundia os dois últimos:
//
//   {ok:true,  idx:0..3}  fase estabelecida
//   {ok:true,  idx:null}  NÃO APLICÁVEL — estado insuficiente ou legado. É
//                         fluxo normal, tratado por verificação explícita, e
//                         nunca por exceção.
//   {ok:false, erro}      falha INESPERADA do próprio mecanismo. Não é ausência
//                         de dado: é defeito, e defeito não pode ser descartado.
//
// As precondições são checadas ANTES de chamar compute() justamente para que o
// try não vire muleta de fluxo normal: params ausente e matriz malformada são
// estados legítimos de base legada, e o helper os trata sozinho.
function accountPhaseProbe(){
  if(typeof compute!=='function') return {ok:true, idx:null};
  if(!S.params || typeof S.params!=='object') return {ok:true, idx:null};
  if(!Array.isArray(S.matrix) || !S.matrix.length) return {ok:true, idx:null};
  try{
    const c=compute();
    if(!c || !c.fase || typeof c.fase.nome!=='string') return {ok:true, idx:null};
    const idx=S.matrix.findIndex(m=>m && m.nome===c.fase.nome);
    // compute() TEVE sucesso e devolveu uma fase que nao existe na matriz
    // normativa. Isso nao e "nao aplicavel" — e inconsistencia entre o calculo
    // e a matriz. Devolver {ok:true, idx:null} aqui empacotava um defeito real
    // junto de "ainda nao ha dados", e a lacuna sumia sem deixar marca.
    if(idx<0) return {ok:false, erro:'fase computada ("'+String(c.fase.nome)+'") ausente de S.matrix'};
    return {ok:true, idx};
  }catch(e){
    return {ok:false, erro:String((e && e.message) || e)};
  }
}

// Compatibilidade de leitura para quem só quer o índice.
function currentAccountPhaseIdx(){ const p=accountPhaseProbe(); return p.ok?p.idx:null; }

// Captura PROSPECTIVA e MONOTÔNICA da maior Fase da Conta atingida.
//
// Chamada de dentro de save() — o menor ponto autoritativo do projeto. Não é
// render (que nunca deve gravar estado) e não é um listener por tela: é o único
// lugar por onde TODA mutação persistida passa, incluindo caminhos que nenhuma
// enumeração de call sites cobriria. O máximo passa a refletir estados que o
// sistema efetivamente comprometeu ao disco.
//
// ESTE CAMPO NÃO É TELEMETRIA. A Fase da Conta máxima é memória prospectiva:
// se não for capturada no instante em que ocorre, é irreconstruível depois. Por
// isso a política de falha tem de separar duas coisas que um `catch` mudo
// fundiria:
//
//   não aplicável  -> a sonda devolve idx:null e nada acontece. Fluxo normal.
//   defeito        -> a falha é GRAVADA na própria entidade e vai ao console.
//
// save() prossegue nos dois casos, e isso é deliberado: derrubar a persistência
// do estado financeiro por causa de um campo derivado trocaria uma lacuna de
// evidência por perda de dado do operador — troca ruim. Mas o sistema não pode
// declarar que capturou o que não capturou. `phaseCaptureFault` fica na
// operação, viaja para o snapshot da Camada 2 e torna a lacuna AUDITÁVEL em vez
// de silenciosa.
//
// A marca não é limpa por um sucesso posterior: se a captura falhou uma vez, o
// máximo pode estar subestimado para sempre, e apagar a evidência disso seria
// exatamente o tipo de mentira que este projeto combate.
function operationTouchAccountPhase(){
  const op=S.activeOperation;
  if(!op || typeof op!=='object' || Array.isArray(op)) return;
  const probe=accountPhaseProbe();
  if(!probe.ok){
    op.phaseCaptureFault={at:new Date().toISOString(), reason:probe.erro};
    if(typeof console!=='undefined' && console.error){
      console.error('[operação] captura da Fase da Conta falhou:', probe.erro);
    }
    return;
  }
  if(probe.idx==null) return;
  // Desconhecido não é -1 nem 0: é ausência. A primeira captura estabelece o
  // valor qualquer que ele seja, inclusive Fase 1 — e daí em diante só sobe.
  const antes=operationPhaseIdxOrNull(op.maxAccountPhaseReached);
  if(antes===null || probe.idx>antes) op.maxAccountPhaseReached=probe.idx;
}

// Carimba a transição de status de uma ordem e, quando for a Gênese abrindo
// pela primeira vez, faz NASCER a Operação Única.
//
// Chamado pelos pontos que realmente mutam o status — o grid e o modal de
// fechamento — e nunca por render: timestamp recalculado a cada repintura não
// seria evidência, seria ruído.
//
// A Gênese é identificada por POSIÇÃO (fase 1, linha 1), a mesma regra que
// genesisOrder() já usa e que checkPhaseCap() aplica normativamente ao teto do
// Art. 8.6. Não é taxonomia nova: é a que o app já executa.
//
// Carimba UMA vez. Reabrir uma ordem não reescreve a abertura original, e
// fechar de novo não move o fechamento — proveniência não se sobrescreve.
function operationOnOrderStatus(o, statusDepois, pi, oi){
  if(!o || typeof o!=='object') return;
  const agora=new Date().toISOString();
  // Capturado ANTES dos carimbos: uma ordem que ja tem carimbo ja pertencia a
  // operacao. Sem essa distincao, re-sinalizar a mesma ordem — o que acontece a
  // cada re-render — pareceria a chegada de uma tese nova.
  const jaPertencia = !!(o.openedAt || o.closedAt);
  if(statusDepois==='Aberta' && !o.openedAt) o.openedAt=agora;
  if(statusDepois==='Fechada' && !o.closedAt) o.closedAt=agora;
  // A identidade nasce AQUI, na camada de ciclo de vida — nunca na finalização.
  // Se fosse criada lá, uma tentativa que falhasse (conflito de instrumento,
  // persistência recusada) deixaria efeito colateral no estado de entrada, e a
  // tentativa seguinte geraria OUTRO id: a Operação Única mudaria de identidade
  // em função de quantas vezes o operador tentou encerrá-la.
  //
  // A abertura da Gênese é o caso normativo e o único com proveniência
  // automática. Qualquer outra ordem tornando-se operacional sem entidade viva
  // também faz a operação nascer — é uma operação real —, mas com abertura
  // DESCONHECIDA, que o operador informa na finalização.
  // FAIL-SAFE. Uma entidade viva que nao tem NENHUMA ordem operacional por tras
  // dela e orfa: a operacao que ela representava deixou de existir. Reutiliza-la
  // transferiria operationId, openedAt e proveniencia para uma tese nova — e o
  // registro imutavel afirmaria que a nova operacao abriu na data da anterior,
  // com captura automatica. A identidade antiga e DESCARTADA, com registro
  // auditavel; jamais herdada.
  //
  // A contagem exclui a ordem que esta nascendo agora: ela e a primeira da tese
  // nova, e nao evidencia da anterior.
  // So se aplica a uma ordem NOVA. E nao se aplica a operacao adotada de legado,
  // cujas ordens podem nao ter carimbo nenhum: ali a ausencia de carimbo e
  // esperada e nao indica orfandade.
  if(S.activeOperation && !jaPertencia && !S.activeOperation.adoptedLegacyAt
     && (statusDepois==='Aberta' || statusDepois==='Fechada')
     && typeof operationLiveOrders==='function'){
    const outras=operationLiveOrders().filter(x=>x && x.o!==o).length;
    if(outras===0){
      const orfa=S.activeOperation.operationId;
      if(typeof dgLogChange==='function'){
        dgLogChange('operation','orphan_discarded', orfa,
          'Identidade órfã descartada: nenhuma ordem operacional a sustentava');
      }
      if(typeof console!=='undefined' && console.error){
        console.error('[operação] identidade órfã descartada (sem ordens operacionais):', orfa);
      }
      S.activeOperation=null;
    }
  }
  if((statusDepois==='Aberta' || statusDepois==='Fechada') && !S.activeOperation){
    const genese = statusDepois==='Aberta' && pi===0 && oi===0;
    S.activeOperation={
      schemaVersion:1,
      operationId:operationRecordId(),
      openedAt: genese?agora:null,
      openedAtSource: genese?'genesis_transition':null,
      maxAccountPhaseReached:null
    };
  }
  // CAPTURA DA FASE DA CONTA — por ultimo, com o ciclo de vida ja RESOLVIDO.
  //
  // Ela rodava antes do fail-safe, sobre a entidade CORRENTE. Quando o fail-safe
  // descartava uma orfa e uma tese nova nascia no mesmo ato, a captura tinha ido
  // para a entidade descartada, e a recem-nascida saia sem observacao do proprio
  // instante em que nasceu. Se o pico da fase estivesse ali e a conta recuasse
  // antes do proximo ato confirmado, o maximo daquela operacao o perdia — nao
  // uma afirmacao falsa, mas uma subestimacao silenciosa.
  //
  // Aqui a captura opera sempre sobre a entidade que PERMANECE viva depois do
  // ato: a preexistente, ou a que acabou de nascer.
  if(S.activeOperation && (statusDepois==='Aberta' || statusDepois==='Fechada')){
    operationTouchAccountPhase();
  }
}

function operationNormalizeState(){
  // activeOperation: null é estado legítimo ("nenhuma operação em curso").
  // Qualquer coisa que não seja objeto simples vira null em vez de virar {}:
  // objeto vazio seria uma operação fantasma sem identidade nem abertura.
  const op=S.activeOperation;
  if(op===null || op===undefined || typeof op!=='object' || Array.isArray(op)){
    S.activeOperation=null;
  }else{
    if(!Number.isFinite(+op.schemaVersion) || +op.schemaVersion<1) op.schemaVersion=1;
    // Identidade ausente é REPARADA, não descartada: uma operação viva de antes
    // desta versão recebe id uma única vez e o mantém dali em diante.
    if(typeof op.operationId!=='string' || !op.operationId) op.operationId=operationRecordId();
    // openedAt desconhecido permanece null. Nunca Date.now(): inventar a
    // abertura de uma operação legada seria falsificar proveniência.
    if(typeof op.openedAt!=='string' || !op.openedAt) op.openedAt=null;
    const fontesAbertura=['genesis_transition','manual_legacy'];
    if(!fontesAbertura.includes(op.openedAtSource)) op.openedAtSource=op.openedAt?'manual_legacy':null;
    op.maxAccountPhaseReached=operationPhaseIdxOrNull(op.maxAccountPhaseReached);
    // Marca de captura degradada: preservada se tiver forma válida, descartada
    // se vier deformada. Nunca inventada.
    const f=op.phaseCaptureFault;
    if(!f || typeof f!=='object' || Array.isArray(f) || typeof f.reason!=='string') delete op.phaseCaptureFault;
  }
  // ADOÇÃO DE OPERAÇÃO LEGADA. Uma operação iniciada antes desta versão tem
  // grades preenchidas e nenhuma entidade. Sem adotá-la, ela atravessaria toda
  // a sua vida sem identidade e sem capturar a Fase da Conta — e o Histórico
  // receberia um registro cego justamente da primeira operação finalizada.
  //
  // A adoção cria identidade e COMEÇA a capturar daqui em diante. Não inventa o
  // passado: openedAt fica null e a proveniência fica indefinida até que o
  // operador informe a data na finalização (aí vira manual_legacy).
  if(!S.activeOperation && Array.isArray(S.phases)){
    const viva=S.phases.some(ph=>Array.isArray(ph && ph.orders) && ph.orders.some(
      o=>o && (o.status==='Aberta' || o.status==='Fechada' || o.status==='Migrada')));
    if(viva){
      S.activeOperation={
        schemaVersion:1,
        operationId:operationRecordId(),
        openedAt:null,
        openedAtSource:null,
        maxAccountPhaseReached:null,
        adoptedLegacyAt:new Date().toISOString()
      };
    }
  }
  // operationHistory: envelope com lista append-only.
  if(!S.operationHistory || typeof S.operationHistory!=='object' || Array.isArray(S.operationHistory))
    S.operationHistory=structuredClone(DEFAULTS.operationHistory);
  const h=S.operationHistory;
  if(!Number.isFinite(+h.schemaVersion) || +h.schemaVersion<1) h.schemaVersion=1;
  if(!Array.isArray(h.records)) h.records=[];
  h.records=h.records.filter(r=>r && typeof r==='object' && !Array.isArray(r));
  // Id duplicado quebraria a idempotência da finalização: o teste "já existe no
  // histórico?" viraria ambíguo. Colisão é reescrita, o registro nunca é
  // descartado — histórico é evidência.
  const vistos=new Set();
  h.records.forEach(r=>{
    if(typeof r.operationId!=='string' || !r.operationId || vistos.has(r.operationId)) r.operationId=operationRecordId();
    vistos.add(r.operationId);
    if(!Number.isFinite(+r.schemaVersion) || +r.schemaVersion<1) r.schemaVersion=1;
    if(!Array.isArray(r.ordersSnapshot)) r.ordersSnapshot=[];
  });
}

function pivotStudiesNormalizeState(){
  if(!S.pivotStudies || typeof S.pivotStudies!=='object' || Array.isArray(S.pivotStudies))
    S.pivotStudies=structuredClone(DEFAULTS.pivotStudies);
  const ps=S.pivotStudies;
  if(!Number.isFinite(+ps.schemaVersion) || +ps.schemaVersion<1) ps.schemaVersion=1;
  if(!Array.isArray(ps.studies)) ps.studies=[];
  // Ids duplicados quebrariam edição e exclusão (o alvo viraria ambíguo).
  // Colisão é reescrita com id novo em vez de o registro ser descartado.
  const seenStudy=new Set();
  ps.studies=ps.studies.filter(st=>st && typeof st==='object' && !Array.isArray(st));
  ps.studies.forEach(st=>{
    if(typeof st.id!=='string' || !st.id || seenStudy.has(st.id)) st.id=pivotStudyId();
    seenStudy.add(st.id);
    // Mesma identidade canônica das ordens e dos Estudos NoCoda.
    st.instrumentId=String(st.instrumentId==null?'':st.instrumentId).toUpperCase().replace(/[^A-Z0-9]/g,'');
    st.periodStart=String(st.periodStart==null?'':st.periodStart);
    st.periodEnd=String(st.periodEnd==null?'':st.periodEnd);
    if(typeof st.createdAt!=='string') st.createdAt='';
    if(typeof st.updatedAt!=='string') st.updatedAt=st.createdAt;
    if(!Array.isArray(st.pivots)) st.pivots=[];
    st.pivots=st.pivots.filter(pv=>pv && typeof pv==='object' && !Array.isArray(pv));
    const seenPivot=new Set();
    st.pivots.forEach(pv=>{
      if(typeof pv.id!=='string' || !pv.id || seenPivot.has(pv.id)) pv.id=pivotRecordId();
      seenPivot.add(pv.id);
      pv.timeframe=String(pv.timeframe==null?'':pv.timeframe).toUpperCase();
      pv.startDatetime=String(pv.startDatetime==null?'':pv.startDatetime);
      pv.endDatetime=String(pv.endDatetime==null?'':pv.endDatetime);
      pv.notes=String(pv.notes==null?'':pv.notes);
      if(typeof pv.createdAt!=='string') pv.createdAt='';
      if(typeof pv.updatedAt!=='string') pv.updatedAt=pv.createdAt;
    });
  });
}
// ---- S.params: o denominador de tudo ----------------------------------------
// O laço genérico de migrate() só repõe chaves de PRIMEIRO nível. Com `params`
// presente no arquivo, nenhuma sub-chave faltante era reposta — e params era o
// único agregado numérico central sem laço por chave (onboarding, mei e
// dataGovernance já tinham o seu).
//
// A consequência não era um número feio, era um veredito falso: sem saldoIni,
// compute() faz dd=0 (guarda `p.saldoIni>0 ? … : 0`) e tetoRisco=NaN, logo
// `excesso>0` é falso e o parecer cai no ramo mais permissivo — o terminal
// exibia "FASE 1 — OPERACIONAL NORMAL / 🟢 COERENTE" com risco aberto real de
// US$ 5.000. O mesmo valia para vrmN/vrmHV ausentes, que faziam o regime de
// volatilidade cair sempre em NORMAL.
//
// NENHUM PARÂMETRO NORMATIVO É ALTERADO aqui: os limiares estatutários voltam a
// vir de DEFAULTS, que é onde o Estatuto está expresso, em vez de ficarem
// `undefined`. Saldo, saldo atual e data de início são DADO DO OPERADOR e não
// são inventados — na ausência de saldoIni utilizável o estado é tratado como
// corrompido e roteado para o modo de recuperação A-005, que preserva a base,
// bloqueia gravação e avisa. Fabricar um saldo seria pior que falhar.
const PARAMS_DADOS_DO_OPERADOR=['saldoIni','saldoAtu','inicio'];
function paramsNormalizeState(){
  if(!S.params || typeof S.params!=='object' || Array.isArray(S.params))
    S.params=structuredClone(DEFAULTS.params);
  for(const k in DEFAULTS.params){
    if(PARAMS_DADOS_DO_OPERADOR.includes(k)) continue;
    const ref=DEFAULTS.params[k], atual=S.params[k];
    if(!(k in S.params)){ S.params[k]=structuredClone(ref); continue; }
    // Repõe apenas o que tem TIPO errado; valor legítimo do operador atravessa.
    if(typeof ref==='number' && !(typeof atual==='number' && Number.isFinite(atual))) S.params[k]=ref;
    else if(typeof ref==='string' && typeof atual!=='string') S.params[k]=ref;
  }
  if(!(typeof S.params.saldoIni==='number' && Number.isFinite(S.params.saldoIni)))
    throw new Error('Estado sem saldo inicial numérico: o denominador de drawdown e do teto de risco não existe.');
  if(!(typeof S.params.saldoAtu==='number' && Number.isFinite(S.params.saldoAtu))) S.params.saldoAtu=S.params.saldoIni;
  if(typeof S.params.inicio!=='string') S.params.inicio=String(S.params.inicio==null?'':S.params.inicio);
}
function migrate(){ // garante chaves novas se schema evoluir
  for(const k in DEFAULTS){ if(!(k in S)) S[k]=structuredClone(DEFAULTS[k]); }
  paramsNormalizeState(); // antes de tudo: compute() e os tetos leem daqui
  canonicalizeStructuralMetadata(); // antes de tudo que lê ins.name/fase abaixo
  mvpNotesNormalizeState(); // legado sem mvpNotes já recebeu DEFAULTS.mvpNotes acima; aqui valida a forma
  dgNormalizeState(); // governança da base (JPW-HJFGDE): mesma regra — defaults acima, forma aqui
  fxPlanningNormalizeState(); // Planejamento FX: guarda estrutural (forma aqui, profundidade na camada de acesso)
  nocodaNormalizeState(); // Estudos NoCoda: mesma regra — mapa instrumentId -> estudo vigente
  pivotStudiesNormalizeState(); // Estudos dos Pivots: mesma regra — lista histórica de estudos por período
  operationNormalizeState(); // Operação Única: identidade da operação viva + envelope do histórico
  // migração por-instrumento: estados salvos antes desta versão não têm 'updated'/'banned'.
  // Sem isso, bloqueios normativos como XAUUSD e US500 seriam perdidos silenciosamente em contas já em uso.
  if(Array.isArray(S.instruments)){
    const us500Ref=DEFAULTS.instruments.find(d=>d.name==='US500');
    if(us500Ref && !S.instruments.some(ins=>ins.name==='US500')) S.instruments.push(structuredClone(us500Ref));
    S.instruments.forEach(ins=>{
      const ref=DEFAULTS.instruments.find(d=>d.name===ins.name);
      if(!('updated' in ins)) ins.updated = '2000-01-01'; // desconhecido = tratar como não confiável
      if(ref && ref.banned && (ins.name==='US500' || !('banned' in ins))){
        ins.banned=true; ins.banReason=ref.banReason; // reaplica o bloqueio, não assume liberação
      }
      // sessões antigas podem não ter cpl/teto/preco — sem isso o renderMotor quebra o boot inteiro
      if(ref){
        if(!(typeof ins.cpl==='number' && ins.cpl>0)) ins.cpl=ref.cpl;
        if(typeof ins.teto!=='number') ins.teto=ref.teto;
        if(!(typeof ins.preco==='number' && ins.preco>0)) ins.preco=ref.preco;
      }
      // estados salvos pela versão anterior gravaram preco=1.00 nos pares de base USD
      // (semântica antiga de "nocional"); o nocional agora é derivado, então 1.00 é só
      // uma cotação obviamente errada — restaura a referência até o próximo fetch.
      if(ref && ['USDJPY','USDCHF','USDCAD'].includes(ins.name) && ins.preco===1) ins.preco=ref.preco;
    });
  }
  if(Array.isArray(S.accounts)){
    S.accounts.forEach(a=>{
      // conta salva antes desta versão já tinha perfil escolhido -> trava por padrão,
      // não deixa a mudança de schema abrir uma exceção que ninguém pediu.
      if(!('perfilLocked' in a)) a.perfilLocked = !!a.perfil;
      if(a.perfil) a.perfil=normalizeRiskProfileName(a.perfil);
      if(!('platform' in a)) a.platform='';
      if(!('platformLogin' in a)) a.platformLogin='';
      if(!('investorPassword' in a)) a.investorPassword='';
      a.platform=normalizePlatformName(a.platform);
      a.platformLogin=String(a.platformLogin||'');
      // POLÍTICA DE SEGREDO: estados/backups antigos podem trazer a senha em texto
      // claro — a estrutura é aceita, mas o segredo é DESCARTADO no carregamento e
      // nunca reescrito no armazenamento. Sem eco, sem changeLog, sem console.
      a.investorPassword='';
      const br=brokerFor(a.broker);
      if(br) a.broker=br.name;
    });
  }
  // matriz de fases: compute() e phaseTetoRisco() assumem 4 linhas com ddmin/ddmax/alav numéricos.
  // O loop genérico acima só recria a matriz se ela estiver AUSENTE — um backup corrompido/truncado
  // (ex.: matrix:[] ou linha sem ddmax) passaria e derrubaria o boot em m[2].ddmax. Restaura o que faltar.
  if(!Array.isArray(S.matrix) || S.matrix.length!==DEFAULTS.matrix.length){
    S.matrix=structuredClone(DEFAULTS.matrix);
  } else {
    S.matrix.forEach((row,i)=>{
      const ref=DEFAULTS.matrix[i];
      if(!row || typeof row!=='object'
        || typeof row.ddmin!=='number' || typeof row.ddmax!=='number' || typeof row.alav!=='number'){
        S.matrix[i]=structuredClone(ref);
      } else if(typeof row.nome!=='string'){ row.nome=ref.nome; }
    });
  }
  if(!('riskPinHash' in S)) S.riskPinHash=null;
  if(!Array.isArray(S.phaseUnlocked)) S.phaseUnlocked=[true,false,false,false];
  if(!Array.isArray(S.transitionLog)) S.transitionLog=[];
  if(typeof S.protocolBreaches!=='number') S.protocolBreaches=0;
  if(typeof S.cycleRealizado!=='number') S.cycleRealizado=0;
  if(!('quarantine' in S)) S.quarantine=null;
  if(!Array.isArray(S.ledger)) S.ledger=[];
  if(!Array.isArray(S.ledgerArchive)) S.ledgerArchive=[];
  if(!S.period || typeof S.period!=='object') S.period={nome:'',profile:'base'};
  S.period.profile=normalizeRiskProfileKey(S.period.profile||'base');
  S.profiles=riskProfilesForState();
  const activeProfile=getActiveRiskProfile(S.period.profile);
  S.params.refM=activeProfile.mensal; S.params.refA=activeProfile.anual;
  S.params.fw=1; // V10: remove multiplicador fixo; aplica saldo normalizado × fator de perfil
  if(S.theme!=='dark' && S.theme!=='light') S.theme='dark'; // Mission Control: escuro é a experiência principal; escolha salva do usuário é respeitada
  if(!S.acct || typeof S.acct!=='object') S.acct={diasSemana:4.5, mesesAno:10.5};
  if(typeof S.acct.diasSemana!=='number') S.acct.diasSemana=4.5;
  if(typeof S.acct.mesesAno!=='number') S.acct.mesesAno=10.5;
  // MEI-JP: migração defensiva para backups anteriores, sem tocar nas estruturas existentes.
  if(!S.mei || typeof S.mei!=='object') S.mei=structuredClone(DEFAULTS.mei);
  else {
    for(const k in DEFAULTS.mei){ if(!(k in S.mei)) S.mei[k]=structuredClone(DEFAULTS.mei[k]); }
    S.mei.version='1.0';
    S.mei.enabled=S.mei.enabled!==false;
    S.mei.sourceMode='auto';
    S.mei.simulationCount=[1000,2000,5000,10000].includes(+S.mei.simulationCount)?+S.mei.simulationCount:5000;
    S.mei.horizonMonths=[12,24,60,120].includes(+S.mei.horizonMonths)?+S.mei.horizonMonths:60;
    S.mei.confidenceLevel=Math.max(.5,Math.min(.99,+S.mei.confidenceLevel||.90));
    S.mei.seedMode=S.mei.seedMode==='fixed'?'fixed':'random';
    S.mei.fixedSeed=String(S.mei.fixedSeed||'');
    // Revisão metodológica v1.0: predominância empírica exige ≥36 retornos válidos.
    // Estados antigos (24) são elevados para 36 — é revisão de política institucional,
    // não preferência do usuário; 24 observações voltam a ser estágio híbrido avançado.
    S.mei.minimumHistoricalMonths=Math.max(36,Math.round(+S.mei.minimumHistoricalMonths||36));
    S.mei.hybridStartMonths=Math.max(2,Math.round(+S.mei.hybridStartMonths||6));
    S.mei.empiricalStartMonths=Math.max(36,Math.max(S.mei.hybridStartMonths+1,Math.round(+S.mei.empiricalStartMonths||36)));
    if(!S.mei.cid || typeof S.mei.cid!=='object') S.mei.cid=structuredClone(DEFAULTS.mei.cid);
    RISK_PROFILES.forEach(p=>{
      const v=S.mei.cid[p.key];
      const n=typeof v==='string' ? Number(v.replace(',','.')) : +v;
      S.mei.cid[p.key]=(v===''||v==null||!Number.isFinite(n))?'':Math.max(0,Math.min(1,n));
    });
    // Preserva registros legados, mesmo se incompletos: o operador deve poder corrigi-los na interface.
    // A camada de cálculo filtra somente as observações válidas, sem apagar dados do backup.
    // Correção 5 (fluxos externos): registros antigos migram com aportes=0, retiradas=0
    // (fluxo líquido 0) e equity inicial informativa vazia — nenhum registro é perdido.
    S.mei.history=Array.isArray(S.mei.history)?S.mei.history.filter(r=>r&&typeof r==='object').map((r,i)=>({
      id:String(r.id||('mei_legacy_'+i+'_'+Date.now())), date:String(r.date||''),
      startingEquity:(r.startingEquity===''||r.startingEquity==null||!Number.isFinite(+r.startingEquity))?'':Number(r.startingEquity),
      endingEquity:Number(r.endingEquity),
      contributions:Number.isFinite(+r.contributions)?Math.max(0,+r.contributions):0,
      withdrawals:Number.isFinite(+r.withdrawals)?Math.max(0,+r.withdrawals):0,
      notes:String(r.notes||'')
    })):[];
    S.mei.lastCalibrationAt=String(S.mei.lastCalibrationAt||'');
    S.mei.notes=String(S.mei.notes||'');
  }
  if(!(typeof S.stopF==='number' && S.stopF>0)) S.stopF=1.8;
  if(typeof S.atrPctManual!=='number') S.atrPctManual=0;
  if(!S.onboarding || typeof S.onboarding!=='object') S.onboarding=structuredClone(DEFAULTS.onboarding);
  else {
    const br=brokerFor(S.onboarding.corretora);
    if(br) S.onboarding.corretora=br.name;
    for(const k in DEFAULTS.onboarding){ if(!(k in S.onboarding)) S.onboarding[k]=DEFAULTS.onboarding[k]; }
    S.onboarding.brokerLogin=String(S.onboarding.brokerLogin||'');
    // Mesma política do bloco de contas: segredo de leitura nunca sobrevive ao load.
    S.onboarding.investorPassword='';
    S.onboarding.brokerServer=String(S.onboarding.brokerServer||'');
    S.onboarding.moedaBase=normalizeAccountCurrency(S.onboarding.moedaBase);
    S.onboarding.propDailyDrawdown=String(S.onboarding.propDailyDrawdown||'');
    S.onboarding.propMaxDrawdown=String(S.onboarding.propMaxDrawdown||'');
    S.onboarding.propTrailingRule=String(S.onboarding.propTrailingRule||'');
    S.onboarding.propTrailingDescription=String(S.onboarding.propTrailingDescription||'');
    S.onboarding.propProfitTarget=String(S.onboarding.propProfitTarget||'');
    S.onboarding.propMinTradingDays=String(S.onboarding.propMinTradingDays||'');
    S.onboarding.propAbsenceRules=String(S.onboarding.propAbsenceRules||'');
    S.onboarding.restrictiveRuleAccepted=Boolean(S.onboarding.restrictiveRuleAccepted);
    // Capital nominal da Conta Mestre não tem mais entrada própria: o Saldo de Início do
    // Período (S.params.saldoIni) é a fonte única. Reconcilia aqui para que backups/estados
    // legados com valor divergente nunca sobrevivam a um load — o campo persiste só por
    // compatibilidade de formato do backup, nunca é lido como fonte de verdade em runtime.
    S.onboarding.reserveMasterCapital=String(S.params.saldoIni||0);
    S.onboarding.reserveFcrRequired=String(S.onboarding.reserveFcrRequired||'');
    S.onboarding.reserveFcrCurrent=String(S.onboarding.reserveFcrCurrent||'');
    S.onboarding.reserveFcrStatus=String(S.onboarding.reserveFcrStatus||'');
    S.onboarding.reserveMonthlyExpenses=String(S.onboarding.reserveMonthlyExpenses||'');
    S.onboarding.reserveFeoRequired=String(S.onboarding.reserveFeoRequired||'');
    S.onboarding.reserveFeoCurrent=String(S.onboarding.reserveFeoCurrent||'');
    S.onboarding.reserveFeoStatus=String(S.onboarding.reserveFeoStatus||'');
    S.onboarding.reserveFcrCoveragePct=String(S.onboarding.reserveFcrCoveragePct||'');
    S.onboarding.reserveFeoCoveragePct=String(S.onboarding.reserveFeoCoveragePct||'');
    S.onboarding.reserveFeoMonthsCovered=String(S.onboarding.reserveFeoMonthsCovered||'');
    S.onboarding.reserveSegregationAccepted=Boolean(S.onboarding.reserveSegregationAccepted);
    S.onboarding.reserveDeficitAccepted=Boolean(S.onboarding.reserveDeficitAccepted);
    S.onboarding.reserveNotes=String(S.onboarding.reserveNotes||'');
    S.onboarding.centralCashStatus=String(S.onboarding.centralCashStatus||'');
    S.onboarding.centralCashCustody=String(S.onboarding.centralCashCustody||'');
    S.onboarding.centralCashCustodyOther=String(S.onboarding.centralCashCustodyOther||'');
    S.onboarding.centralCashMainPct=String(S.onboarding.centralCashMainPct||'');
    S.onboarding.centralCashAgilePct=String(S.onboarding.centralCashAgilePct||'');
    S.onboarding.centralCashLiquidityPct=String(S.onboarding.centralCashLiquidityPct||'');
    S.onboarding.centralCashExternalPct=String(S.onboarding.centralCashExternalPct||'');
    S.onboarding.centralCashOtherPct=String(S.onboarding.centralCashOtherPct||'');
    S.onboarding.centralCashCompositionMode=String(S.onboarding.centralCashCompositionMode||'percentual');
    S.onboarding.centralCashCompositionTotal=String(S.onboarding.centralCashCompositionTotal||'');
    S.onboarding.centralCashTraceabilityScore=String(S.onboarding.centralCashTraceabilityScore||'');
    S.onboarding.fcrLiquidity=String(S.onboarding.fcrLiquidity||'');
    S.onboarding.feoLiquidity=String(S.onboarding.feoLiquidity||'');
    S.onboarding.cashLedgerStatus=String(S.onboarding.cashLedgerStatus||'');
    S.onboarding.centralCashPolicyAccepted=Boolean(S.onboarding.centralCashPolicyAccepted);
    S.onboarding.centralCashNoAccepted=Boolean(S.onboarding.centralCashNoAccepted);
    S.onboarding.centralCashNotes=String(S.onboarding.centralCashNotes||'');
    S.onboarding.epStatus=String(S.onboarding.epStatus||'');
    S.onboarding.epPlatform=String(S.onboarding.epPlatform||'');
    S.onboarding.epPlatformOther=String(S.onboarding.epPlatformOther||'');
    S.onboarding.epReference=String(S.onboarding.epReference||'');
    S.onboarding.epDailyLimit=String(S.onboarding.epDailyLimit||'');
    S.onboarding.epMaxDrawdown=String(S.onboarding.epMaxDrawdown||'');
    S.onboarding.epStatuteMatch=String(S.onboarding.epStatuteMatch||'');
    S.onboarding.epRestrictiveAccepted=Boolean(S.onboarding.epRestrictiveAccepted);
    S.onboarding.epPropDailyEnabled=String(S.onboarding.epPropDailyEnabled||'');
    S.onboarding.epPropDailyBase=String(S.onboarding.epPropDailyBase||'');
    S.onboarding.epPropDailyNotes=String(S.onboarding.epPropDailyNotes||'');
    S.onboarding.epTestStatus=String(S.onboarding.epTestStatus||'');
    S.onboarding.epNoConfigAccepted=Boolean(S.onboarding.epNoConfigAccepted);
    S.onboarding.epNotes=String(S.onboarding.epNotes||'');
    S.onboarding.summaryAccepted=Boolean(S.onboarding.summaryAccepted);
  }
  // estado antigo COM atividade (ordens/fechamentos/log) = período já em andamento:
  // não abrir o questionário de início por cima — confirmar sobrescreveria saldoIni/inicio.
  if(!S.onboarding.done){
    const temAtividade=(Array.isArray(S.transitionLog)&&S.transitionLog.length>0)
      ||(Array.isArray(S.ledger)&&S.ledger.length>0)
      ||(Array.isArray(S.phases)&&S.phases.some(ph=>Array.isArray(ph.orders)&&ph.orders.some(o=>o&&o.status)));
    if(temAtividade) S.onboarding.done=true;
  }
  // migração de ordens: versões anteriores usavam 'Active' ou inferiam status pela presença
  // de lote/entry/sl. Agora o status é explícito (Aberta/Fechada) e passou a ser o único
  // critério para contar risco — sem isso, ordens já preenchidas silenciosamente sumiriam do cálculo.
  if(Array.isArray(S.phases)){
    S.phases.forEach(ph=>{
      if(!Array.isArray(ph.orders)) return;
      ph.orders.forEach(o=>{
        if(o.status==='Active') o.status='Aberta';
        else if(!o.status && o.lote>0 && o.entry>0 && o.sl>0) o.status='Aberta'; // dado preenchido = presumir aberta
      });
    });
  }
}
let saveTimer;
// ---- FALHA DE GRAVAÇÃO (A-001) ----------------------------------------------
// Estado de EXECUÇÃO apenas: vive fora de S, nunca é serializado, nunca entra no
// backup e não altera schemaVersion. Um estado de falha persistido seria mentira —
// descreve o navegador de agora, não a base do operador.
// kind: 'storage' (setItem lançou — o estado É serializável, o backup funciona) ou
// 'serialize' (JSON.stringify lançou — o backup usa a MESMA serialização e tende a
// falhar junto; o aviso não pode prometer o que não pode cumprir).
const jpWealthPersistenceFailure={active:false, kind:null, count:0, lastError:null, recoveryTimer:null};
function persistenceAlertEl(){ return document.getElementById('persistenceAlert'); }
function persistenceRecoveryEl(){ return document.getElementById('persistenceRecovery'); }
// Os dois avisos (recuperação A-005 e falha de gravação A-001) são nós fixos distintos e
// ambos ancoram em top:72px — quando o de recuperação está visível, o do A-001 desce para
// logo abaixo dele. Nós e timers separados de propósito: o "Gravação restabelecida" do
// A-001 limpa APENAS #persistenceAlert; nenhum timer jamais toca o aviso de recuperação,
// que só sai por decisão do operador (precedência do estado de recuperação).
function layoutPersistenceBanners(){
  const alertEl=persistenceAlertEl(); if(!alertEl) return;
  const rec=persistenceRecoveryEl();
  if(rec && rec.innerHTML.trim()!==''){ alertEl.style.top=(72+rec.offsetHeight+10)+'px'; }
  else{ alertEl.style.top=''; }
}
// ---- ações do modo de recuperação (A-005) ----
function persistenceRecoveryDownload(){
  // Texto BRUTO original, sem normalizar e sem reserializar o S provisório; não passa
  // por save(). Mesmo padrão Blob+<a download> das exportações existentes (não há helper
  // genérico no projeto para reutilizar).
  const raw=jpWealthLoadRecovery.raw;
  if(raw==null){ alert('O conteúdo original não pôde ser lido do armazenamento — não há cópia para baixar.'); return; }
  const t=new Date(), pad=n=>String(n).padStart(2,'0');
  const nome='jpwealth_recuperacao_'+t.getFullYear()+'-'+pad(t.getMonth()+1)+'-'+pad(t.getDate())+'_'+pad(t.getHours())+'-'+pad(t.getMinutes())+'-'+pad(t.getSeconds())+'.json';
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([raw],{type:'application/json'}));
  a.download=nome; a.click(); URL.revokeObjectURL(a.href);
}
function persistenceRecoveryImport(){
  // Reutiliza o fluxo real de importação (validação + confirmação + gravação); o input
  // vive no host legado de Configurações e aceita click programático vindo deste gesto.
  const input=document.getElementById('importFullBackupInput');
  if(input){ input.click(); return; }
  if(typeof openSettingsModal==='function'){ openSettingsModal('backup', document.getElementById('persistenceRecoveryImportBtn')); return; }
  alert('Abra Configurações → Dados e Segurança → Backup e Recuperação para importar um backup.');
}
// Encerramento comum às duas decisões legítimas (importação validada / base vazia aceita):
// libera a flag SÓ para a tentativa de gravação e a rearma se a gravação falhar — a chave
// principal problemática nunca é substituída sem uma escrita comprovadamente bem-sucedida.
function jpWealthResolveRecoveryAndSave(){
  if(!jpWealthLoadRecovery.active) return save();
  jpWealthLoadRecovery.active=false;
  const ok=save();
  if(ok) clearLoadRecoveryWarning();
  else jpWealthLoadRecovery.active=true;
  return ok;
}
function persistenceRecoveryAcceptEmpty(){
  const msg='Substituir o banco problemático por uma base vazia?\n\n'+
    '• A chave principal atual será sobrescrita pela base vazia;\n'+
    '• A cópia de recuperação'+(jpWealthLoadRecovery.recoveryKey?' ('+jpWealthLoadRecovery.recoveryKey+')':'')+' continuará preservada neste navegador;\n'+
    '• Esta ação NÃO recupera os dados antigos.';
  if(!confirm(msg)) return;
  resumeJPWealthPersistence();
  const ok=jpWealthResolveRecoveryAndSave();
  if(!ok){
    // A escrita falhou (o A-001 já pintou a falha de armazenamento): rearma o bloqueio
    // genérico também; o banco problemático segue intacto e o aviso de recuperação segue.
    blockJPWealthPersistence();
    alert('A base vazia não pôde ser gravada — nada foi apagado. O modo de recuperação continua ativo; verifique o armazenamento do navegador.');
    return;
  }
  boot(); // reabre a interface como início normal (inclusive questionário de início)
}
function renderLoadRecoveryWarning(){
  const el=persistenceRecoveryEl(); if(!el) return;
  const key=jpWealthLoadRecovery.recoveryKey;
  const temRaw=jpWealthLoadRecovery.raw!=null;
  el.className='persistence-alert persistence-recovery is-failure';
  // innerHTML substitui os botões inteiros a cada render — sem listeners acumulados.
  el.innerHTML='<p class="persistence-alert-title">O banco de dados não pôde ser carregado com segurança</p>'+
    '<p class="persistence-alert-text">O conteúdo original foi preservado e as gravações foram bloqueadas para impedir que ele seja substituído. '+
    'O aplicativo está exibindo uma base provisória vazia. Não registre novos dados antes de escolher uma opção de recuperação.'+
    (key?' Cópia de recuperação: <code>'+key+'</code>.':(temRaw?' A cópia de recuperação não pôde ser gravada — use o download abaixo.':' O armazenamento não pôde ser lido; não há conteúdo para baixar.'))+'</p>'+
    '<div class="persistence-alert-actions">'+
      (temRaw?'<button type="button" class="reset-btn persistence-alert-btn" id="persistenceRecoveryDownloadBtn">Baixar cópia de recuperação</button>':'')+
      '<button type="button" class="reset-btn persistence-alert-btn" id="persistenceRecoveryImportBtn">Restaurar um backup válido</button>'+
      '<button type="button" class="reset-btn persistence-alert-btn" id="persistenceRecoveryResetBtn">Começar com base vazia</button>'+
    '</div>';
  const dl=document.getElementById('persistenceRecoveryDownloadBtn');
  if(dl) dl.addEventListener('click',persistenceRecoveryDownload);
  const imp=document.getElementById('persistenceRecoveryImportBtn');
  if(imp) imp.addEventListener('click',persistenceRecoveryImport);
  const rst=document.getElementById('persistenceRecoveryResetBtn');
  if(rst) rst.addEventListener('click',persistenceRecoveryAcceptEmpty);
  layoutPersistenceBanners();
}
function clearLoadRecoveryWarning(){
  // raw e recoveryKey ficam em memória de propósito (transparência/último recurso);
  // a cópia no localStorage NUNCA é removida por este código.
  jpWealthLoadRecovery.kind=null;
  jpWealthLoadRecovery.lastError=null;
  const el=persistenceRecoveryEl();
  if(el){ el.className='persistence-alert persistence-recovery'; el.innerHTML=''; }
  layoutPersistenceBanners();
}
// exportFullBackup() vive em 30-accounting/01-daily-ledger.js (script 18) e a Central
// em 09-settings-modal.js (script 36) — ambos carregam DEPOIS deste arquivo (script 4).
// Por isso a checagem de existência acontece no clique, não na criação do aviso.
function persistenceAlertExportBackup(){
  // Serializa o S em memória: não depende de nenhuma gravação anterior ter dado certo,
  // que é exatamente a razão de existir este botão. exportFullBackup() é async
  // (JPW-HJFGDE) e reporta as próprias falhas — inclusive a de serialização — com
  // alert interno, sem nunca rejeitar; o try/catch abaixo cobre apenas os ramos
  // síncronos restantes deste função.
  try{
    if(typeof exportFullBackup==='function'){ exportFullBackup(); return; }
    if(typeof openSettingsModal==='function'){ openSettingsModal('backup', persistenceAlertEl()); return; }
    alert('Abra Configurações → Dados e Segurança → Backup e Recuperação para exportar a base antes de fechar esta página.');
  }catch(e){
    console.error('JP Wealth: a exportação do backup também falhou.', e);
    alert('A exportação também falhou — os dados em memória não puderam ser serializados. Antes de fechar a página, anote manualmente os registros mais recentes (ordens, fechamentos, notas).');
  }
}
function renderPersistenceFailureWarning(){
  const el=persistenceAlertEl(); if(!el) return;
  clearTimeout(jpWealthPersistenceFailure.recoveryTimer);
  el.className='persistence-alert is-failure';
  const serialize=jpWealthPersistenceFailure.kind==='serialize';
  // innerHTML substitui o nó do botão inteiro a cada render, então o listener antigo
  // morre junto — não há como acumular listeners duplicados.
  el.innerHTML=serialize
    ? '<p class="persistence-alert-title">Falha ao preparar os dados para gravação</p>'+
      '<p class="persistence-alert-text">As alterações não puderam ser convertidas para gravação — o problema está nos dados em memória, não no armazenamento. '+
      'Não recarregue nem feche esta página: alterações recentes podem ser perdidas e a exportação de backup pode falhar pelo mesmo motivo. '+
      'Tente exportar mesmo assim e, se a exportação falhar, anote manualmente os registros mais recentes.</p>'+
      '<div class="persistence-alert-actions"><button type="button" class="reset-btn persistence-alert-btn" id="persistenceAlertBackupBtn">Tentar exportar backup</button></div>'
    : '<p class="persistence-alert-title">Falha ao salvar os dados</p>'+
      '<p class="persistence-alert-text">O navegador não conseguiu gravar as alterações no armazenamento local. '+
      'Não recarregue nem feche esta página antes de exportar um backup, pois alterações recentes podem ser perdidas.</p>'+
      '<div class="persistence-alert-actions"><button type="button" class="reset-btn persistence-alert-btn" id="persistenceAlertBackupBtn">Exportar backup agora</button></div>';
  const btn=document.getElementById('persistenceAlertBackupBtn');
  if(btn) btn.addEventListener('click',persistenceAlertExportBackup);
  layoutPersistenceBanners();
}
function setPersistenceFailureState(error,kind){
  kind=kind==='serialize'?'serialize':'storage';
  jpWealthPersistenceFailure.count++;
  jpWealthPersistenceFailure.lastError=error||null;
  // Repinta na transição saudável→falha E quando o TIPO muda (storage⇄serialize) — o
  // aviso precisa refletir a causa atual. Falha repetida do mesmo tipo não repinta:
  // o role="alert" reanunciaria o mesmo texto no leitor de tela a cada tecla.
  if(jpWealthPersistenceFailure.active && jpWealthPersistenceFailure.kind===kind) return;
  jpWealthPersistenceFailure.active=true;
  jpWealthPersistenceFailure.kind=kind;
  renderPersistenceFailureWarning();
}
function clearPersistenceFailureState(){
  if(!jpWealthPersistenceFailure.active) return; // caminho saudável: custo zero
  jpWealthPersistenceFailure.active=false;
  jpWealthPersistenceFailure.kind=null;
  jpWealthPersistenceFailure.count=0;
  jpWealthPersistenceFailure.lastError=null;
  const el=persistenceAlertEl(); if(!el) return;
  el.className='persistence-alert is-recovered';
  el.innerHTML='<p class="persistence-alert-title">Gravação restabelecida</p>'+
    '<p class="persistence-alert-text">As alterações voltaram a ser salvas neste navegador.</p>';
  layoutPersistenceBanners();
  clearTimeout(jpWealthPersistenceFailure.recoveryTimer);
  jpWealthPersistenceFailure.recoveryTimer=setTimeout(()=>{
    if(jpWealthPersistenceFailure.active) return; // falhou de novo enquanto esperava
    const cur=persistenceAlertEl(); if(!cur) return;
    cur.className='persistence-alert'; cur.innerHTML=''; // :empty volta a esconder
    layoutPersistenceBanners();
  },6000);
}
// Apaga um "salvo" ainda no ar de uma gravação anterior bem-sucedida: sua janela é de
// 1200ms, então uma falha logo em seguida deixaria selo verde e aviso de erro na tela
// ao mesmo tempo, dizendo coisas opostas.
function hideStaleSavedTag(){
  const stale=document.getElementById('savedTag');
  if(stale){ clearTimeout(saveTimer); stale.classList.remove('show'); }
}
function save(){
  // Recuperação de carregamento (A-005) tem precedência sobre tudo: mesmo que algum
  // fluxo reabra o portão genérico (importFullBackupFile e openOnboardingModal chamam
  // resumeJPWealthPersistence), nada grava enquanto o operador não decidir.
  if(jpWealthLoadRecovery.active) return false;
  // Precede o portão genérico: este não é reaberto por resumeJPWealthPersistence.
  if(jpWealthPersistenceOutcomeUnknown) return false;
  if(jpWealthPersistenceBlocked) return false;
  // AQUI NAO SE CAPTURA A FASE DA CONTA. save() e chamado a cada TECLA nos campos
  // numericos da grade, e um valor meio digitado produz uma Fase da Conta
  // transitoria: digitar "1.09" passa por "1", cujo risco joga a conta para a
  // Fase 4. Como a captura e monotonica, aquele pico era gravado como maximo
  // OBSERVADO e nunca mais descia — o registro imutavel afirmava uma fase que a
  // conta jamais atingiu.
  //
  // Persistir o valor corrente e uma coisa; afirmar historia e outra. A captura
  // passou para os atos semanticamente CONFIRMADOS: edicao comprometida de campo
  // (evento 'change', depois das guardas e das reversoes), resultado informado,
  // ordem tornando-se operacional, destravamento de fase confirmado, e
  // finalizacao. Todos chamam operationTouchAccountPhase() explicitamente.
  // Serialização e gravação em trys separados: são falhas de natureza diferente. Se o
  // stringify lança (ciclo, BigInt), o armazenamento está saudável mas o backup — que
  // usa a MESMA serialização — tende a falhar junto; o aviso precisa dizer isso em vez
  // de prometer uma exportação que não vai funcionar.
  let payload;
  try{
    // POLÍTICA DE SEGREDO: a senha de investidor NUNCA vai para armazenamento
    // persistente. O replacer cobre accounts[].investorPassword, onboarding e qualquer
    // site futuro que use o mesmo nome de campo — em memória o valor continua íntegro
    // durante a sessão; no disco a chave grava sempre vazia.
    payload=JSON.stringify(S,(k,v)=>k==='investorPassword'?'':v);
  }catch(e){
    console.error('JP Wealth: falha ao preparar (serializar) o estado para gravação.', e);
    hideStaleSavedTag();
    setPersistenceFailureState(e,'serialize');
    return false;
  }
  // try estreito, cobrindo só a gravação: qualquer exceção posterior (ex.: #savedTag
  // ausente) não deve ser relatada como falha de armazenamento.
  try{
    localStorage.setItem(LSKEY,payload);
  }catch(e){
    console.error('JP Wealth: falha ao gravar o estado no armazenamento local.', e);
    hideStaleSavedTag();
    setPersistenceFailureState(e,'storage');
    return false;
  }
  clearPersistenceFailureState();
  const t=document.getElementById('savedTag');
  if(t){
    t.classList.add('show');
    clearTimeout(saveTimer); saveTimer=setTimeout(()=>t.classList.remove('show'),1200);
  }
  return true;
}
