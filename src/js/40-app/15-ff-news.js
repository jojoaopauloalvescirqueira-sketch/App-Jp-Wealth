// ============ NOTÍCIAS DE ALTO IMPACTO (FOREX FACTORY) — N1 ============
// Widget informativo do Dashboard: eventos de impacto Alto do dia, nas moedas
// que cobrem os mercados operados (EURUSD, USDJPY, GBPUSD, S&P 500, Gold →
// USD/EUR/JPY/GBP). Fonte: JSON publicado pelo repositório público
// jp-wealth-news-feed (GitHub Action busca o Forex Factory do lado do
// servidor — o feed original não envia CORS e limita requisições por IP).
// Nada aqui toca S, save() ou qualquer regra financeira: é leitura de dado
// público com cache próprio em localStorage, fora do formato de backup.
const FF_NEWS_DEFAULT_URL='https://raw.githubusercontent.com/jojoaopauloalvescirqueira-sketch/jp-wealth-news-feed/main/ff-high-impact.json';
const FF_NEWS_CACHE_KEY='jpwealth.ui.ffNews.v1';
// Override de fonte sem rebuild (ex.: migração futura para Netlify Functions):
// localStorage.setItem('jpwealth.ui.ffNews.sourceUrl', 'https://…')
const FF_NEWS_URL_OVERRIDE_KEY='jpwealth.ui.ffNews.sourceUrl';
const FF_NEWS_MAX_AGE_MS=30*60*1000;
const FF_NEWS_POLL_MS=5*60*1000;
// Tique de re-render (contagem regressiva do próximo evento e reclassificação
// passado/próximo). Não faz fetch — o consumo da fonte segue no ciclo de 5 min.
const FF_NEWS_TICK_MS=60*1000;
// Janela de iminência: a menos de 15 min o realce muda para a cor de perigo,
// a mesma já usada pelo termômetro High.
const FF_NEWS_IMMINENT_MS=15*60*1000;
const FF_NEWS_CURRENCIES=['USD','EUR','JPY','GBP'];
let ffNewsInFlight=false;
let ffNewsLastError=false;
let ffNewsCacheWriteFailed=false;
let ffNewsCacheReadFailed=false;
let ffNewsDomainTimers=[];
let ffNewsDomainOnlineBound=false;


// Shared public economic snapshot. Storage, requests and lifecycle stay outside
// JPWEconomicCalendar's synchronous, financial-state-free query model.
(function initCalendarFeed(root){
  if(root.JPWCalendarFeed)return;
  const MAX_BYTES=8000000,MAX_ROWS=12000,MAX_SOURCE_AGE=2*60*60*1000;
  const currencies=['USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY'];
  const impacts=['high','medium','low','unclassified'],states=['scheduled','published','cancelled'];
  const copy=value=>JSON.parse(JSON.stringify(value));
  const object=value=>value&&typeof value==='object'&&!Array.isArray(value);
  const date=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value+'T00:00:00Z'))&&new Date(value+'T00:00:00Z').toISOString().slice(0,10)===value;
  const instant=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$/.test(value)&&date(value.slice(0,10))&&Number.isFinite(Date.parse(value));
  const url=value=>{try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&!!u.hostname;}catch(_){return false;}};
  let current=null,cacheText=null,cacheEnvelope=null,disposed=false,request=0,revision=0,controller=null;
  function validate(payload){
    if(!object(payload)||JSON.stringify(payload).length>MAX_BYTES)return null;
    if(payload.version===1){
      if(!Array.isArray(payload.events)||payload.events.length>MAX_ROWS)return null;
      // Compatibility v1 is deliberately limited. It never establishes broad
      // currency/impact/month coverage, even when the GET just succeeded.
      const events=payload.events.filter(e=>object(e)&&typeof e.title==='string'&&e.title.length<=600&&typeof e.country==='string'&&typeof e.date==='string'&&Number.isFinite(Date.parse(e.date))&&e.impact==='High'&&FF_NEWS_CURRENCIES.includes(e.country));
      return {...copy(payload),events:copy(events)};
    }
    if(payload.schemaVersion!==2||!instant(payload.collectedAt)||!instant(payload.packagePublishedAt)||!(payload.sourcePublishedAt===null||instant(payload.sourcePublishedAt))||Date.parse(payload.collectedAt)>Date.now()+5*60*1000)return null;
    if(!Array.isArray(payload.currencies)||!payload.currencies.length||payload.currencies.some(v=>!currencies.includes(v))||new Set(payload.currencies).size!==payload.currencies.length||!Array.isArray(payload.sources)||!Array.isArray(payload.events)||payload.events.length>MAX_ROWS||!Array.isArray(payload.coverage))return null;
    const ids=new Set(),sourceIds=new Set(),sourceCurrencies=new Map(),zones=new Set();
    for(const source of payload.sources){if(!object(source)||typeof source.id!=='string'||sourceIds.has(source.id)||typeof source.name!=='string'||!url(source.url)||(!currencies.includes(source.currency)||!payload.currencies.includes(source.currency)))return null;sourceIds.add(source.id);sourceCurrencies.set(source.id,source.currency);}
    for(const e of payload.events){
      if(!object(e)||typeof e.id!=='string'||!e.id||e.id.length>300||ids.has(e.id)||typeof e.title!=='string'||!e.title.trim()||e.title.length>600||!currencies.includes(e.currency)||(!sourceIds.has(e.sourceId)||sourceCurrencies.get(e.sourceId)!==e.currency||!payload.currencies.includes(e.currency))||!impacts.includes(e.impact)||!date(e.date)||!url(e.sourceUrl)||!states.includes(e.status)||!instant(e.reviewedAt)||!((e.precision==='date'&&e.at===null)||(e.precision==='instant'&&instant(e.at))))return null;
      if(e.observationStatus!==undefined&&!['present','not-in-latest'].includes(e.observationStatus))return null;
      if(!zones.has(e.timeZone)){try{new Intl.DateTimeFormat('en',{timeZone:e.timeZone});zones.add(e.timeZone);}catch(_){return null;}}
      ids.add(e.id);
    }
    for(const row of payload.coverage){if(!object(row)||(!sourceIds.has(row.sourceId)||sourceCurrencies.get(row.sourceId)!==row.currency||!payload.currencies.includes(row.currency))||!currencies.includes(row.currency)||!date(row.from)||!date(row.to)||row.from>row.to||!['confirmed','partial','pending','stale','unavailable'].includes(row.status)||!instant(row.reviewedAt)||(row.validUntil!==undefined&&!instant(row.validUntil)))return null;}
    return copy(payload);
  }
  function sourceStamp(payload){return payload?.schemaVersion===2?payload.collectedAt:(typeof payload?.generated_at==='string'&&instant(payload.generated_at)?payload.generated_at:null);}
  function adopt(envelope){if(current!==envelope)revision++;current=envelope;return current;}
  function read(){
    let raw;try{raw=localStorage.getItem(FF_NEWS_CACHE_KEY);ffNewsCacheReadFailed=false;}catch(_){ffNewsCacheReadFailed=true;return null;}
    if(raw===null){cacheText=null;cacheEnvelope=null;adopt(null);return null;}
    if(raw===cacheText&&cacheEnvelope)return adopt(cacheEnvelope);
    try{const parsed=JSON.parse(raw);if(!object(parsed)||typeof parsed.fetchedAt!=='number'||!Number.isFinite(parsed.fetchedAt)||parsed.fetchedAt<0){ffNewsCacheReadFailed=true;return null;}
      const payload=validate(parsed.payload);if(!payload){ffNewsCacheReadFailed=true;return null;}
      cacheText=raw;cacheEnvelope={fetchedAt:parsed.fetchedAt,payload};return adopt(cacheEnvelope);
    }catch(_){ffNewsCacheReadFailed=true;return null;}
  }
  function write(payload){
    const clean=validate(payload);if(!clean||disposed)return false;
    const envelope={fetchedAt:Date.now(),payload:clean},raw=JSON.stringify(envelope);
    try{localStorage.setItem(FF_NEWS_CACHE_KEY,raw);}catch(_){ffNewsCacheWriteFailed=true;return false;}
    ffNewsCacheWriteFailed=false;cacheText=raw;cacheEnvelope=envelope;adopt(envelope);return true;
  }
  function legacy(payload){
    const clean=validate(payload);if(!clean)return null;
    const events=clean.schemaVersion===2?clean.events.filter(e=>String(e.sourceId).startsWith('ff-')&&e.precision==='instant'&&FF_NEWS_CURRENCIES.includes(e.currency)&&e.impact==='high'&&e.observationStatus!=='not-in-latest'&&e.status!=='cancelled').map(e=>({title:e.title,country:e.currency,date:e.at,forecast:typeof e.forecast==='string'?e.forecast:'',previous:typeof e.previous==='string'?e.previous:''})):clean.events.map(e=>({title:e.title,country:e.country,date:e.date,forecast:typeof e.forecast==='string'?e.forecast:'',previous:typeof e.previous==='string'?e.previous:''}));
    return {generatedAt:sourceStamp(clean)||'',collectedAt:sourceStamp(clean),mode:clean.schemaVersion===2?'normalized':'legacy-partial',events};
  }
  function snapshot(){return current?copy({...current,revision,mode:current.payload.schemaVersion===2?'normalized':'legacy-partial'}):null;}
  function status(){const at=sourceStamp(current?.payload);return {mode:current?(current.payload.schemaVersion===2?'normalized':'legacy-partial'):'unavailable',collectedAt:at,packagePublishedAt:current?.payload?.packagePublishedAt||null,sourcePublishedAt:current?.payload?.sourcePublishedAt||null,stale:!at||Date.now()-Date.parse(at)>MAX_SOURCE_AGE,fetchFailed:ffNewsLastError,readFailed:ffNewsCacheReadFailed,writeFailed:ffNewsCacheWriteFailed,disposed};}
  function notify(){if(disposed)return;try{root.dispatchEvent(new CustomEvent('jpw-economic-calendar-updated'));}catch(_){} }
  function finish(){ffNewsInFlight=false;controller=null;const b=document.getElementById('gdNewsRefreshBtn');if(b)b.disabled=false;ffNewsRenderAll();notify();}
  async function refresh(force=false){
    if(disposed||ffNewsInFlight)return false;
    const cached=read();if(!force&&cached&&Date.now()-cached.fetchedAt<FF_NEWS_MAX_AGE_MS)return false;
    const generation=++request;ffNewsInFlight=true;const b=document.getElementById('gdNewsRefreshBtn');if(b)b.disabled=true;
    const s=document.getElementById('gdNewsStatus');if(s)s.textContent='Atualizando…';
    try{
      const endpoint=ffNewsSourceUrl();if(!url(endpoint))throw new Error('Fonte pública inválida');
      controller=typeof AbortController==='function'?new AbortController():null;
      const response=await fetch(endpoint,{cache:'no-store',...(controller?{signal:controller.signal}:{})});
      if(!response.ok)throw new Error('HTTP '+response.status);
      const payload=await response.json();if(disposed||generation!==request||endpoint!==ffNewsSourceUrl())return false;
      if(!validate(payload))throw new Error('Carga pública inválida');
      const saved=write(payload);ffNewsLastError=false;return saved;
    }catch(_){if(!disposed&&generation===request)ffNewsLastError=true;return false;}
    finally{if(!disposed&&generation===request)finish();}
  }
  function disposeForSession(){disposed=true;++request;controller?.abort();controller=null;ffNewsInFlight=false;ffNewsDomainTimers.forEach(id=>clearInterval(id));ffNewsDomainTimers=[];}
  // Only an accepted surface entry resumes a disposed session. Refresh and
  // queued network callbacks never reactivate this controller by themselves.
  function resumeForSession(){if(!disposed)return false;disposed=false;++request;read();initFfNewsDomain();return true;}
  root.JPWCalendarFeed=Object.freeze({snapshot,status,refresh,read,write,legacy,validate,disposeForSession,resumeForSession});
  root.addEventListener('storage',event=>{if(event.key===FF_NEWS_CACHE_KEY&&!disposed){read();ffNewsRenderAll();notify();}});
  read();
})(window);

function ffNewsSourceUrl(){
  try{ return localStorage.getItem(FF_NEWS_URL_OVERRIDE_KEY) || FF_NEWS_DEFAULT_URL; }
  catch(_){ return FF_NEWS_DEFAULT_URL; }
}

// Revalida a carga mesmo vinda do alimentador já filtrado — se o repositório
// público for editado à mão ou servido truncado, lixo não chega à tela.
function ffNewsSanitizeEvents(payload){return window.JPWCalendarFeed.legacy(payload);}
function ffNewsReadCache(){
  const cached=window.JPWCalendarFeed.read();if(!cached)return null;
  const clean=ffNewsSanitizeEvents(cached.payload);return clean?{fetchedAt:cached.fetchedAt,...clean}:null;
}
function ffNewsWriteCache(payload){const saved=window.JPWCalendarFeed.write(payload);if(saved)window.dispatchEvent(new CustomEvent('jpw-economic-calendar-updated'));return saved;}

// Estado técnico da tentativa, sem payload paralelo nem alteração do cache antigo.
function ffNewsCacheIssue(){
  if(ffNewsCacheReadFailed) return 'Cache indisponível — não foi possível ler o armazenamento.';
  if(ffNewsCacheWriteFailed) return 'Cache não atualizado — não foi possível gravar no armazenamento.';
  return '';
}

function ffNewsIsToday(date){
  const now=new Date();
  return date.getFullYear()===now.getFullYear() && date.getMonth()===now.getMonth() && date.getDate()===now.getDate();
}

function ffNewsStatusText(cache){
  const issue=ffNewsCacheIssue();
  if(!cache) return issue ? 'Sem dados · '+issue : ffNewsLastError ? 'Sem dados — verifique a conexão.' : ffNewsInFlight?'Sem dados — carregando calendário econômico…':'Sem dados — atualize o calendário econômico.';
  const gen=cache.generatedAt ? new Date(cache.generatedAt) : null;
  const stamp=(gen && !isNaN(gen.getTime()))
    ? gen.toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})
    : new Date(cache.fetchedAt).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
  const stale=!gen||isNaN(gen.getTime())||Date.now()-gen.getTime()>2*60*60*1000;
  return (issue ? issue+' · dados anteriores de ' : ffNewsLastError ? 'Sem conexão · dados de ' : stale?'Dados desatualizados de ':'Dados de ')+stamp+(cache.mode==='legacy-partial'?' · Feed legado: quatro moedas, alto impacto.':'');
}

// Rótulo curto da contagem: "agora" no minuto do evento, minutos até 1h,
// depois horas compactas ("em 1h05"). Nunca negativo — evento passado deixa
// de ser "próximo" na seleção, não aqui.
function ffNewsCountdownLabel(ms){
  const min=Math.floor(ms/60000);
  if(min<1) return 'agora';
  if(min<60) return 'em '+min+' min';
  const h=Math.floor(min/60), m=min%60;
  return 'em '+h+'h'+(m?String(m).padStart(2,'0'):'');
}

// Linha-resumo "Próximo · <evento> · contagem" acima da tabela. Construída só
// com textContent — mesma disciplina anti-injeção do restante do widget.
function ffNewsRenderNext(next,now){
  const el=document.getElementById('gdNewsNext');
  if(!el) return;
  el.textContent='';
  el.classList.remove('gd-news-next-imminent');
  if(!next){ el.hidden=true; return; }
  const ms=next.when.getTime()-now;
  const label=document.createElement('span');
  label.className='gd-news-next-label';
  label.textContent='Próximo';
  const title=document.createElement('strong');
  title.className='gd-news-next-title';
  title.textContent=next.title;
  const cur=document.createElement('span');
  cur.className='gd-news-cur';
  cur.textContent=next.country;
  const count=document.createElement('span');
  count.className='gd-news-next-count';
  count.textContent=ffNewsCountdownLabel(ms);
  if(ms<=FF_NEWS_IMMINENT_MS) el.classList.add('gd-news-next-imminent');
  el.append(label,title,cur,count);
  el.hidden=false;
}

function ffNewsRender(){
  const list=document.getElementById('gdNewsList');
  const empty=document.getElementById('gdNewsEmpty');
  const status=document.getElementById('gdNewsStatus');
  if(!list || !empty || !status) return;
  const cache=ffNewsReadCache();
  status.textContent=ffNewsStatusText(cache);
  list.textContent='';
  const today=(cache?cache.events:[])
    .map(e=>({...e, when:new Date(e.date)}))
    .filter(e=>ffNewsIsToday(e.when))
    .sort((a,b)=>a.when-b.when);
  empty.hidden=!(cache && today.length===0);
  const now=Date.now();
  // O próximo evento é o primeiro ainda não ocorrido (>= now: complementar ao
  // critério de passado abaixo, que usa < now — nenhum evento fica sem classe).
  const next=today.find(e=>e.when.getTime()>=now)||null;
  ffNewsRenderNext(next,now);
  for(const e of today){
    const tr=document.createElement('tr');
    tr.className='gd-news-item'
      +(e.when.getTime()<now?' gd-news-item-past':'')
      +(next && e===next?' gd-news-item-next':'');
    const tdTime=document.createElement('td');
    const time=document.createElement('time');
    time.className='gd-news-time';
    time.dateTime=e.date;
    time.textContent=e.when.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
    tdTime.append(time);
    const tdCur=document.createElement('td');
    const cur=document.createElement('span');
    cur.className='gd-news-cur';
    cur.textContent=e.country;
    tdCur.append(cur);
    // Termômetro de impacto — mesma linguagem dos medidores horizontais do
    // app (.gd-gauge). Hoje só chegam eventos High (filtro na origem e na
    // sanitização); os níveis medium/low já têm classe prevista caso o
    // filtro seja ampliado no futuro.
    const tdImpact=document.createElement('td');
    tdImpact.className='gd-news-imp';
    const meter=document.createElement('span');
    meter.className='gd-news-impact gd-news-impact-high';
    meter.setAttribute('role','img');
    meter.setAttribute('aria-label','Impacto alto');
    meter.title='Impacto alto';
    const fill=document.createElement('span');
    fill.className='gd-news-impact-fill';
    meter.append(fill);
    tdImpact.append(meter);
    const tdTitle=document.createElement('td');
    tdTitle.className='gd-news-title';
    tdTitle.textContent=e.title;
    const tdPrev=document.createElement('td');
    tdPrev.className='gd-news-num';
    tdPrev.textContent=e.forecast||'—';
    const tdAnt=document.createElement('td');
    tdAnt.className='gd-news-num';
    tdAnt.textContent=e.previous||'—';
    tr.append(tdTime,tdCur,tdImpact,tdTitle,tdPrev,tdAnt);
    list.append(tr);
  }
}

// Fan-out de repintura das superfícies que consomem este cache. O widget do
// Dashboard e o Calendário Econômico são independentes: a ausência de um não
// pode impedir a repintura do outro.
//
// Antes desta separação a chamada do calendário ficava DENTRO de ffNewsRender(),
// depois do `return` que sai quando os nós do widget não existem — logo um fetch
// bem-sucedido gravava cache novo e o calendário aberto nunca acompanhava.
// Guarda de existência mantida: este arquivo carrega antes do 17, e no monólito
// reduzido o 17 pode faltar.
function ffNewsRenderAll(){
  ffNewsRender();
  if(typeof ecalRenderIfOpen==='function') ecalRenderIfOpen();
  if(window.JPWDashMacro) window.JPWDashMacro.schedule();
}

function ffNewsCacheStale(){
  const cache=ffNewsReadCache();
  return !cache || (Date.now()-cache.fetchedAt)>FF_NEWS_MAX_AGE_MS;
}

function ffNewsFetch(force){return window.JPWCalendarFeed.refresh(!!force);}

// Inicialização em DUAS partes, deliberadamente separadas.
//
// VIEW do widget: tudo que precisa do DOM do card do Dashboard. Continua
// condicionada à existência do card, como deve ser.
function initFfNewsWidget(){
  const card=document.querySelector('[data-layout-card="news-high-impact"]');
  if(!card) return;
  const btn=document.getElementById('gdNewsRefreshBtn');
  if(btn) btn.addEventListener('click',()=>ffNewsFetch(true));
  // Menu ⋯ → Calendário Econômico. O botão é deste card, então o bind é deste
  // módulo: antes o calendário procurava #gdNewsMoreBtn dentro do Dashboard.
  // A chamada é resolvida no clique, não agora — este arquivo é o script 44 e
  // o calendário é o 46, então window.JPWEcal ainda não existe neste ponto.
  const more=document.getElementById('gdNewsMoreBtn');
  if(more) more.addEventListener('click',()=>{
    if(window.JPWEcal && typeof window.JPWEcal.openMenu==='function') window.JPWEcal.openMenu(more);
  });
}

// DOMÍNIO: cache, rede, timers e 'online'. NÃO depende de nó algum do
// Dashboard — o Calendário Econômico consome este mesmo cache a partir do
// Execution Board, onde o card de Notícias pode não estar montado.
//
// Até esta separação, o `if(!card) return` de initFfNews() matava junto os dois
// intervalos, o listener 'online' e o fetch inicial: sem o card, nada
// revalidava e o calendário exibiria cache velho indefinidamente, em silêncio.
// Fonte e cadência existentes são compartilhadas pelo semanal e pelo mensal.
// A validade econômica depende da coleta da fonte, não da hora deste GET.
function initFfNewsDomain(){
  if(window.JPWCalendarFeed?.status().disposed||ffNewsDomainTimers.length)return;
  if(!ffNewsDomainOnlineBound){window.addEventListener('online',()=>ffNewsFetch(false));ffNewsDomainOnlineBound=true;}
  // Poll leve: re-render cobre a virada do dia; fetch só quando o cache
  // envelheceu e a aba está visível — respeita o rate-limit da fonte.
  ffNewsDomainTimers.push(setInterval(()=>{
    ffNewsRenderAll();
    if(document.visibilityState==='visible') ffNewsFetch(false);
  },FF_NEWS_POLL_MS));
  // Tique de 1 min só de render: mantém a contagem regressiva e a transição
  // próximo→passado precisas sem nenhum consumo adicional da fonte.
  ffNewsDomainTimers.push(setInterval(ffNewsRenderAll,FF_NEWS_TICK_MS));
  ffNewsRenderAll();
  ffNewsFetch(false);
}

initFfNewsWidget();
initFfNewsDomain();
