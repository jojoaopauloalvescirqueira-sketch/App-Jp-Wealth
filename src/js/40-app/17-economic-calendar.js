// ============ CALENDÁRIO ECONÔMICO — SEMANA CORRENTE (N1) ============
// UMA implementação, DOIS pontos de entrada (menu ⋯ do widget de Notícias e a
// folha do grupo Operação na Central). Consome exclusivamente o cache já
// sanitizado de 15-ff-news.js via ffNewsReadCache() — zero fetch, zero cache e
// zero sanitização próprios: o pipeline anti-XSS do widget continua sendo o
// único caminho de entrada de dado externo, e toda escrita de texto aqui é por
// textContent.
//
// ESCOPO SEMANAL É DECISÃO, NÃO LIMITAÇÃO DE CÓDIGO: a fonte
// (ff_calendar_thisweek) só publica a semana corrente e não tem o campo
// `actual`. Auditoria de 2026-08-11 — upstream sem semanas arbitrárias
// (HTTP 404 em lastweek/nextweek) e sem endpoint mensal. Por isso o título
// não diz "mês" e não existe coluna Realizado (uma coluna permanentemente
// "—" leria como defeito de carga, não como lacuna da fonte).
const ECAL_CURRENCIES=['USD','EUR','GBP','JPY'];
// var, não const — de propósito. No monólito os módulos são concatenados num
// único script clássico: a DECLARAÇÃO de ecalRenderIfOpen iça para o topo do
// arquivo inteiro, e o ffNewsRender() do módulo 15 (que roda no boot, antes
// desta linha) passa no typeof e a chama. Com const, ecalState estaria na zona
// morta temporal e o boot inteiro morreria em ReferenceError; com var, o nome
// existe como undefined e a guarda de ecalRenderIfOpen devolve em silêncio.
var ecalState={open:false, opener:null, filter:'all', menu:null, menuAnchor:null};

function ecalEl(id){ return document.getElementById(id); }

// ---- dados: leitura única do cache do widget ----
function ecalEvents(){
  const cache=(typeof ffNewsReadCache==='function')?ffNewsReadCache():null;
  if(!cache) return null;
  return {
    fetchedAt:cache.fetchedAt, generatedAt:cache.generatedAt,
    events:cache.events.map(e=>({...e, when:new Date(e.date)})).sort((a,b)=>a.when-b.when)
  };
}

function ecalDayKey(d){
  return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
}
function ecalDayLabel(d){
  // "ter · 12 ago" — mesma língua do restante do painel.
  return d.toLocaleDateString('pt-BR',{weekday:'short', day:'2-digit', month:'short'}).replace(/\./g,'');
}

function ecalRangeLabel(events){
  if(!events.length) return '';
  const a=events[0].when, b=events[events.length-1].when;
  const fmt=d=>d.toLocaleDateString('pt-BR',{day:'2-digit', month:'short'}).replace(/\./g,'');
  return 'Semana corrente da fonte · '+(ecalDayKey(a)===ecalDayKey(b)?fmt(a):fmt(a)+' – '+fmt(b));
}

// ---- render (textContent em todo dado externo — disciplina do widget) ----
// NÚCLEO PARAMETRIZADO POR RAIZ. Serve as duas instâncias visuais — o overlay
// #ecalOverlay e o workspace #execEcal do Execution Board — a partir da mesma
// leitura de cache e das mesmas regras. Não existe segundo calendário: existe
// uma função de render e dois lugares onde ela desenha.
//
// A resolução é por data-ecal-role DENTRO da raiz, nunca por getElementById:
// os 9 ids do overlay são globais e fixos, e o workspace deliberadamente não
// tem id interno algum. Fosse por id, a segunda superfície capturaria os nós da
// primeira — #exec precede o overlay no documento.
function ecalPart(root, role){ return root?root.querySelector('[data-ecal-role="'+role+'"]'):null; }

function ecalRenderRoot(root, filter){
  const body=ecalPart(root,'body'), empty=ecalPart(root,'empty'),
        fresh=ecalPart(root,'freshness'), range=ecalPart(root,'range');
  if(!body||!empty||!fresh||!range) return;
  body.textContent='';
  const data=ecalEvents();
  if(!data){
    range.textContent='';
    fresh.textContent='';
    empty.textContent='Sem dados — verifique a conexão e use ↻ no Calendário Econômico do Dashboard.';
    empty.hidden=false;
    return;
  }
  const stampSrc=data.generatedAt?new Date(data.generatedAt):new Date(data.fetchedAt);
  fresh.textContent='Dados de '+(isNaN(stampSrc.getTime())?'—':stampSrc.toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}));
  // Escrita CONDICIONAL: este nó é aria-live="polite" nas duas instâncias, e o
  // setter de textContent troca o nó de texto mesmo quando a string é idêntica.
  // Como o tique de 1 min repinta a superfície visível, escrever sempre faria o
  // leitor de tela reanunciar o mesmo intervalo indefinidamente, por cima da
  // leitura em curso. O anúncio deve acontecer quando o rótulo MUDA.
  const rangeLabel=ecalRangeLabel(data.events);
  if(range.textContent!==rangeLabel) range.textContent=rangeLabel;
  const filtered=data.events.filter(e=>filter==='all'||e.country===filter);
  if(!filtered.length){
    empty.textContent=filter==='all'
      ? 'A fonte não lista eventos de alto impacto para a semana corrente.'
      : 'Sem eventos de alto impacto em '+filter+' nesta semana.';
    empty.hidden=false;
    return;
  }
  empty.hidden=true;
  const now=Date.now();
  const todayKey=ecalDayKey(new Date());
  let currentKey=null, dayWrap=null, list=null;
  for(const e of filtered){
    const key=ecalDayKey(e.when);
    if(key!==currentKey){
      currentKey=key;
      dayWrap=document.createElement('section');
      dayWrap.className='ecal-day'+(key===todayKey?' ecal-day-today':'');
      const h=document.createElement('h3');
      h.className='ecal-day-title';
      h.textContent=ecalDayLabel(e.when)+(key===todayKey?' · hoje':'');
      list=document.createElement('div');
      list.className='ecal-day-list';
      dayWrap.append(h,list);
      body.append(dayWrap);
    }
    const row=document.createElement('div');
    row.className='ecal-item'+(e.when.getTime()<now?' ecal-item-past':'');
    const time=document.createElement('time');
    time.className='ecal-time';
    time.dateTime=e.date;
    time.textContent=e.when.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
    const cur=document.createElement('span');
    // .ecal-cur, não .gd-news-cur: a classe do widget é namespaced sob
    // html[data-shell="global-dashboard"] e amarrava o calendário ao Dashboard.
    // Declarações idênticas, dono correto (app.css).
    cur.className='ecal-cur';
    cur.textContent=e.country;
    const title=document.createElement('span');
    title.className='ecal-title';
    title.textContent=e.title;
    const nums=document.createElement('span');
    nums.className='ecal-nums';
    const mk=(label,val)=>{
      const w=document.createElement('span'); w.className='ecal-num';
      const l=document.createElement('span'); l.className='ecal-num-label'; l.textContent=label;
      const v=document.createElement('span'); v.className='ecal-num-value'; v.textContent=val||'—';
      w.append(l,v); return w;
    };
    nums.append(mk('Consenso',e.forecast), mk('Anterior',e.previous));
    row.append(time,cur,title,nums);
    list.append(row);
  }
}

// ---- instância 1: o overlay, com seus dois pontos de entrada intocados ----
function ecalRender(){ ecalRenderRoot(ecalEl('ecalOverlay'), ecalState.filter); }

// ---- instância 2: o workspace canônico do Execution Board ----
// Estado de APRESENTAÇÃO próprio. O filtro de moeda é recorte da view, não
// verdade do domínio: os eventos são compartilhados, qual subconjunto cada
// superfície exibe não é — e compartilhá-lo faria a escolha numa tela mudar a
// outra pelas costas do operador. `var` pela mesma razão de ecalState, acima.
var ecalWsState={filter:'all'};
function ecalWsRoot(){ return document.getElementById('execEcal'); }
function ecalRenderWorkspace(){ ecalRenderRoot(ecalWsRoot(), ecalWsState.filter); }

function ecalSyncFilters(root, filter){
  const box=ecalPart(root,'filters'); if(!box) return;
  box.querySelectorAll('button[data-ecal-cur]').forEach(b=>{
    const on=b.dataset.ecalCur===filter;
    b.classList.toggle('on',on);
    b.setAttribute('aria-pressed',String(on));
  });
}

function ecalSetFilter(cur){
  // §16 do ticket: abre sempre em Todas; a troca vale só enquanto aberto.
  ecalState.filter=ECAL_CURRENCIES.includes(cur)?cur:'all';
  ecalSyncFilters(ecalEl('ecalOverlay'), ecalState.filter);
  ecalRender();
}
function ecalWsSetFilter(cur){
  // O workspace é superfície permanente: o filtro dele persiste na sessão em
  // vez de voltar a Todas, ao contrário do overlay, que reabre sempre limpo.
  ecalWsState.filter=ECAL_CURRENCIES.includes(cur)?cur:'all';
  ecalSyncFilters(ecalWsRoot(), ecalWsState.filter);
  ecalRenderWorkspace();
}

// Chamado por ffNewsRenderAll() ao fim de cada ciclo do domínio: se uma
// superfície estiver visível quando um fetch/tique atualizar o cache, ela
// acompanha — sem isso, dado novo só apareceria reabrindo.
function ecalRenderIfOpen(){
  if(ecalState && ecalState.open) ecalRender();
  // A guarda `if(ecalWsState)` NÃO é redundante: este arquivo é o script 46 e
  // 15-ff-news.js é o 44, que chama esta função durante a própria avaliação, no
  // monólito — a declaração está içada, o valor ainda não. Mesma razão do `var`
  // documentado no topo. Removê-la derruba o boot inteiro.
  if(!ecalWsState) return;
  const root=ecalWsRoot();
  if(!root || root.hidden) return;
  // `hidden` sozinho não basta. execApplyView() é o único a escrevê-lo e não
  // tem caminho de SAÍDA do módulo: sair do Execution Board para outra tela só
  // troca a classe .active, e .screen{display:none} esconde por CSS deixando
  // #execEcal com hidden=false. Sem esta segunda condição o tique de 1 min
  // reconstruiria o workspace inteiro dentro de uma subárvore invisível, para
  // sempre — cerca de 1.400 repinturas descartadas por dia de app aberto.
  if(!root.closest('.screen.active')) return;
  ecalRenderWorkspace();
}

// ---- foco: armadilha simples, mesmo contrato dos outros diálogos ----
function ecalFocusables(){
  return [...ecalEl('ecalModal').querySelectorAll('button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])')]
    .filter(el=>!el.closest('[hidden]'));
}
function ecalKeydown(event){
  if(!ecalState.open) return;
  // stopImmediatePropagation, não stopPropagation: o Escape global de
  // 06-boot.js (→ closeModal) está registrado no MESMO nó document, e
  // stopPropagation não bloqueia listeners do próprio nó.
  if(event.key==='Escape'){ event.stopImmediatePropagation(); closeEconomicCalendar(); return; }
  if(event.key!=='Tab') return;
  const list=ecalFocusables(); if(!list.length) return;
  const first=list[0], last=list[list.length-1];
  if(event.shiftKey && document.activeElement===first){ event.preventDefault(); last.focus(); }
  else if(!event.shiftKey && document.activeElement===last){ event.preventDefault(); first.focus(); }
}

// ---- entry point único (§10 do ticket) ----
function openEconomicCalendar(opener){
  if(ecalState.open) return;
  ecalState.open=true;
  ecalState.opener=(opener instanceof HTMLElement)?opener:null;
  // Central aberta? vira subdiálogo — mesmo contrato das Notas: a Central fica
  // inerte por baixo e devolve o foco ao lançador quando este diálogo fechar.
  if(typeof settingsIsOpen==='function' && settingsIsOpen() && typeof suspendSettingsForSubdialog==='function'){
    suspendSettingsForSubdialog();
  }
  ecalSetFilter('all');
  // Revalida em silêncio pelo pipeline do widget se o cache envelheceu — o
  // calendário nunca fala com a rede diretamente.
  if(typeof ffNewsFetch==='function') ffNewsFetch(false);
  const overlay=ecalEl('ecalOverlay');
  overlay.classList.add('show');
  overlay.setAttribute('aria-hidden','false');
  document.addEventListener('keydown',ecalKeydown,true);
  const close=ecalEl('ecalCloseBtn'); if(close) close.focus();
}

function closeEconomicCalendar(){
  if(!ecalState.open) return;
  ecalState.open=false;
  const overlay=ecalEl('ecalOverlay');
  overlay.classList.remove('show');
  overlay.setAttribute('aria-hidden','true');
  document.removeEventListener('keydown',ecalKeydown,true);
  const opener=ecalState.opener; ecalState.opener=null;
  // Se a Central estava suspensa por baixo, é ela quem devolve o foco ao
  // lançador (restaure primeiro; foca via subdialogLauncher). Fora dela, o
  // foco volta ao elemento que abriu — o botão ⋯ do widget.
  if(typeof restoreSettingsAfterSubdialog==='function' && typeof settingsIsOpen==='function' && settingsIsOpen()){
    restoreSettingsAfterSubdialog();
  } else if(opener && document.contains(opener)){
    opener.focus();
  }
}

// ---- menu ⋯ do widget ----
// Reutiliza a linguagem visual do sistema de popovers (.jp-popover na camada
// #jpPopoverLayer), com estado próprio: acoplar ao dashLayoutState amarraria o
// calendário ao modo de edição do dashboard, que tem outro ciclo de vida.
function ecalCloseMenu(returnFocus){
  const m=ecalState.menu; if(!m) return;
  m.remove();
  ecalState.menu=null;
  document.removeEventListener('pointerdown',ecalMenuOutside,true);
  window.removeEventListener('resize',ecalCloseMenuNoFocus);
  window.removeEventListener('scroll',ecalCloseMenuNoFocus,true);
  const a=ecalState.menuAnchor; ecalState.menuAnchor=null;
  if(a){ a.setAttribute('aria-expanded','false'); a.removeAttribute('aria-controls'); if(returnFocus && document.contains(a)) a.focus(); }
}
function ecalCloseMenuNoFocus(){ ecalCloseMenu(false); }
function ecalMenuOutside(event){
  if(ecalState.menu && !ecalState.menu.contains(event.target) && event.target!==ecalState.menuAnchor) ecalCloseMenu(false);
}
function ecalOpenMenu(anchor){
  if(ecalState.menu){ ecalCloseMenu(true); return; }
  const layer=document.getElementById('jpPopoverLayer'); if(!layer) return;
  const el=document.createElement('div');
  el.className='jp-popover ecal-news-menu';
  el.id='ecalNewsMenu';
  el.setAttribute('role','menu');
  el.setAttribute('aria-label','Opções do Calendário Econômico');
  const item=document.createElement('button');
  item.type='button';
  item.setAttribute('role','menuitem');
  item.textContent='Calendário Econômico';
  item.addEventListener('click',()=>{ ecalCloseMenu(false); openEconomicCalendar(anchor); });
  el.append(item);
  el.addEventListener('keydown',event=>{
    if(event.key==='Escape'){ event.stopPropagation(); ecalCloseMenu(true); }
  });
  layer.append(el);
  // Posicionamento: mesma regra do menu de card (abaixo da âncora, alinhado à
  // direita, sempre dentro da viewport).
  const margin=8, r=anchor.getBoundingClientRect();
  let left=r.right-el.offsetWidth, top=r.bottom+margin;
  if(left<margin) left=margin;
  if(left+el.offsetWidth>window.innerWidth-margin) left=Math.max(margin,window.innerWidth-margin-el.offsetWidth);
  if(top+el.offsetHeight>window.innerHeight-margin){
    const above=r.top-margin-el.offsetHeight;
    top=above>=margin?above:Math.max(margin,window.innerHeight-margin-el.offsetHeight);
  }
  el.style.left=left+'px'; el.style.top=top+'px';
  ecalState.menu=el; ecalState.menuAnchor=anchor;
  anchor.setAttribute('aria-expanded','true');
  anchor.setAttribute('aria-controls','ecalNewsMenu');
  document.addEventListener('pointerdown',ecalMenuOutside,true);
  window.addEventListener('resize',ecalCloseMenuNoFocus);
  window.addEventListener('scroll',ecalCloseMenuNoFocus,true);
  item.focus();
}

function initEconomicCalendar(){
  const close=ecalEl('ecalCloseBtn');
  if(close) close.addEventListener('click',closeEconomicCalendar);
  const overlay=ecalEl('ecalOverlay');
  if(overlay) overlay.addEventListener('click',e=>{ if(e.target===overlay) closeEconomicCalendar(); });
  const filters=ecalEl('ecalFilters');
  if(filters) filters.addEventListener('click',e=>{
    const b=e.target.closest('button[data-ecal-cur]'); if(b) ecalSetFilter(b.dataset.ecalCur);
  });
  // Filtros do workspace: faixa estática no HTML, um único bind. O render
  // reconstrói apenas o corpo — a faixa não é recriada, então o listener não
  // se multiplica a cada entrada no workspace.
  const wsFilters=ecalPart(ecalWsRoot(),'filters');
  if(wsFilters) wsFilters.addEventListener('click',e=>{
    const b=e.target.closest('button[data-ecal-cur]'); if(b) ecalWsSetFilter(b.dataset.ecalCur);
  });
  // Lançador da Central por DELEGAÇÃO: o painel da folha é criado pela própria
  // Central depois deste módulo carregar, então um bind direto não o acharia.
  document.addEventListener('click',e=>{
    const b=e.target.closest && e.target.closest('#ecalOpenFromSettingsBtn');
    if(!b) return;
    if(typeof settingsMarkSubdialogLauncher==='function') settingsMarkSubdialogLauncher(b);
    openEconomicCalendar(b);
  });
}
initEconomicCalendar();

// ---- superfície pública ----
// O widget de Notícias chama openMenu() para o SEU botão ⋯. Antes era este
// módulo que ia buscar #gdNewsMoreBtn dentro do card do Dashboard — dependência
// na direção errada: o calendário não deve conhecer os nós do Dashboard.
window.JPWEcal={open:openEconomicCalendar, openMenu:ecalOpenMenu, close:closeEconomicCalendar};
// Contrato dos workspaces montados sob demanda (13-exec-views.js).
window.JPWEcalUI={render:ecalRenderWorkspace};
