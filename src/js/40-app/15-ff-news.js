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

function ffNewsSourceUrl(){
  try{ return localStorage.getItem(FF_NEWS_URL_OVERRIDE_KEY) || FF_NEWS_DEFAULT_URL; }
  catch(_){ return FF_NEWS_DEFAULT_URL; }
}

// Revalida a carga mesmo vinda do alimentador já filtrado — se o repositório
// público for editado à mão ou servido truncado, lixo não chega à tela.
function ffNewsSanitizeEvents(payload){
  if(!payload || typeof payload!=='object' || payload.version!==1 || !Array.isArray(payload.events)) return null;
  const events=[];
  for(const e of payload.events){
    if(!e || typeof e!=='object') continue;
    if(typeof e.title!=='string' || typeof e.country!=='string' || typeof e.date!=='string') continue;
    if(e.impact!=='High' || !FF_NEWS_CURRENCIES.includes(e.country)) continue;
    const when=new Date(e.date);
    if(isNaN(when.getTime())) continue;
    events.push({title:e.title, country:e.country, date:e.date,
      forecast:typeof e.forecast==='string'?e.forecast:'',
      previous:typeof e.previous==='string'?e.previous:''});
  }
  return {generatedAt:typeof payload.generated_at==='string'?payload.generated_at:'', events};
}

function ffNewsReadCache(){
  try{
    const raw=localStorage.getItem(FF_NEWS_CACHE_KEY);
    if(!raw) return null;
    const parsed=JSON.parse(raw);
    if(!parsed || typeof parsed!=='object' || typeof parsed.fetchedAt!=='number') return null;
    const clean=ffNewsSanitizeEvents(parsed.payload);
    if(!clean) return null;
    return {fetchedAt:parsed.fetchedAt, ...clean};
  }catch(_){ return null; }
}
function ffNewsWriteCache(payload){
  try{ localStorage.setItem(FF_NEWS_CACHE_KEY, JSON.stringify({fetchedAt:Date.now(), payload})); }
  catch(_){ /* cota cheia: segue só em memória até o próximo render */ }
}

function ffNewsIsToday(date){
  const now=new Date();
  return date.getFullYear()===now.getFullYear() && date.getMonth()===now.getMonth() && date.getDate()===now.getDate();
}

function ffNewsStatusText(cache){
  if(!cache) return ffNewsLastError ? 'Sem dados — verifique a conexão.' : 'Carregando notícias…';
  const gen=cache.generatedAt ? new Date(cache.generatedAt) : null;
  const stamp=(gen && !isNaN(gen.getTime()))
    ? gen.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})
    : new Date(cache.fetchedAt).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
  return (ffNewsLastError ? 'Sem conexão · dados de ' : 'Dados de ')+stamp;
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

function ffNewsCacheStale(){
  const cache=ffNewsReadCache();
  return !cache || (Date.now()-cache.fetchedAt)>FF_NEWS_MAX_AGE_MS;
}

function ffNewsFetch(force){
  if(ffNewsInFlight) return;
  if(!force && !ffNewsCacheStale()) return;
  const btn=document.getElementById('gdNewsRefreshBtn');
  const status=document.getElementById('gdNewsStatus');
  ffNewsInFlight=true;
  if(btn) btn.disabled=true;
  if(status) status.textContent='Atualizando…';
  fetch(ffNewsSourceUrl(),{cache:'no-store'})
    .then(r=>{ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
    .then(payload=>{
      if(!ffNewsSanitizeEvents(payload)) throw new Error('carga inválida');
      ffNewsWriteCache(payload);
      ffNewsLastError=false;
    })
    .catch(()=>{ ffNewsLastError=true; })
    .finally(()=>{
      ffNewsInFlight=false;
      if(btn) btn.disabled=false;
      ffNewsRender();
    });
}

function initFfNews(){
  const card=document.querySelector('[data-layout-card="news-high-impact"]');
  if(!card) return;
  const btn=document.getElementById('gdNewsRefreshBtn');
  if(btn) btn.addEventListener('click',()=>ffNewsFetch(true));
  window.addEventListener('online',()=>ffNewsFetch(false));
  // Poll leve: re-render cobre a virada do dia; fetch só quando o cache
  // envelheceu e a aba está visível — respeita o rate-limit da fonte.
  setInterval(()=>{
    ffNewsRender();
    if(document.visibilityState==='visible') ffNewsFetch(false);
  },FF_NEWS_POLL_MS);
  // Tique de 1 min só de render: mantém a contagem regressiva e a transição
  // próximo→passado precisas sem nenhum consumo adicional da fonte.
  setInterval(ffNewsRender,FF_NEWS_TICK_MS);
  ffNewsRender();
  ffNewsFetch(false);
}
initFfNews();
