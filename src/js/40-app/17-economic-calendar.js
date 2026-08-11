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
function ecalRender(){
  const body=ecalEl('ecalBody'), empty=ecalEl('ecalEmpty'), fresh=ecalEl('ecalFreshness'), range=ecalEl('ecalRange');
  if(!body||!empty||!fresh||!range) return;
  body.textContent='';
  const data=ecalEvents();
  if(!data){
    range.textContent='';
    fresh.textContent='';
    empty.textContent='Sem dados — verifique a conexão e use ↻ no widget de Notícias.';
    empty.hidden=false;
    return;
  }
  const stampSrc=data.generatedAt?new Date(data.generatedAt):new Date(data.fetchedAt);
  fresh.textContent='Dados de '+(isNaN(stampSrc.getTime())?'—':stampSrc.toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}));
  range.textContent=ecalRangeLabel(data.events);
  const filtered=data.events.filter(e=>ecalState.filter==='all'||e.country===ecalState.filter);
  if(!filtered.length){
    empty.textContent=ecalState.filter==='all'
      ? 'A fonte não lista eventos de alto impacto para a semana corrente.'
      : 'Sem eventos de alto impacto em '+ecalState.filter+' nesta semana.';
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
    cur.className='gd-news-cur';
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

// Chamado por ffNewsRender() ao fim de cada ciclo do widget: se o calendário
// estiver aberto quando um fetch/tick atualizar o cache, a tela acompanha —
// sem isso, dado novo só apareceria fechando e reabrindo.
function ecalRenderIfOpen(){ if(!ecalState || !ecalState.open) return; ecalRender(); }

function ecalSetFilter(cur){
  // §16 do ticket: abre sempre em Todas; a troca vale só enquanto aberto.
  ecalState.filter=ECAL_CURRENCIES.includes(cur)?cur:'all';
  document.querySelectorAll('#ecalFilters button').forEach(b=>{
    const on=b.dataset.ecalCur===ecalState.filter;
    b.classList.toggle('on',on);
    b.setAttribute('aria-pressed',String(on));
  });
  ecalRender();
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
  el.setAttribute('aria-label','Opções de Notícias de Alto Impacto');
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
  const more=document.getElementById('gdNewsMoreBtn');
  if(more) more.addEventListener('click',()=>ecalOpenMenu(more));
  const close=ecalEl('ecalCloseBtn');
  if(close) close.addEventListener('click',closeEconomicCalendar);
  const overlay=ecalEl('ecalOverlay');
  if(overlay) overlay.addEventListener('click',e=>{ if(e.target===overlay) closeEconomicCalendar(); });
  const filters=ecalEl('ecalFilters');
  if(filters) filters.addEventListener('click',e=>{
    const b=e.target.closest('button[data-ecal-cur]'); if(b) ecalSetFilter(b.dataset.ecalCur);
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
