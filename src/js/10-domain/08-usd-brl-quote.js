// ============ REFERÊNCIA USD/BRL CORRENTE (JPW-FGDEKM) ============
// Fornece a taxa externa usada para converter PATRIMÔNIO PRESENTE em BRL.
// Existem três conceitos cambiais distintos no sistema e eles nunca se
// sobrescrevem:
//
//   PASSADO   valuationFxRate    taxa de avaliação registrada num mês fechado
//   PRESENTE  currentUsdBrlQuote referência externa corrente (este módulo)
//   FUTURO    projectedFxRate    premissa do usuário para projeções
//
// Fonte: Frankfurter (taxas de referência do BCE), o MESMO provedor já adotado
// em 10-domain/04-stop-statistics.js para os 8 pares operados. Sem chave, sem
// segredo, sem função serverless — por isso nada aqui precisa de Netlify.
//
// NATUREZA DO DADO: é taxa de REFERÊNCIA DIÁRIA, publicada uma vez por dia útil
// pelo BCE. Não é cotação spot intradiária e a interface não pode chamá-la de
// "ao vivo" ou "tempo real". Por isso `referenceDate` (a data econômica que o
// provedor devolve) e `fetchedAt` (quando nós consultamos) são grandezas
// separadas e ambas preservadas.
//
// O cache é técnico, de dado de mercado — mesmo padrão de 40-app/15-ff-news.js.
// Nunca entra em S.fxPlanning, nunca vira premissa do plano, nunca entra no
// baseline e não faz parte do formato de backup.

var USDBRL_CACHE_KEY='jpwealth.market.usdbrl.v1';
var USDBRL_ENDPOINT='https://api.frankfurter.dev/v2/rate/USD/BRL';
var USDBRL_SOURCE='Frankfurter · taxas de referência do BCE';
// TTL = "está na hora de tentar buscar referência mais nova", NÃO "o último
// valor virou inválido". Numa segunda-feira a referência de sexta continua
// sendo a última publicada e continua válida; o que expira é a nossa consulta.
var USDBRL_TTL_MS=6*60*60*1000;
var USDBRL_TIMEOUT_MS=6000;
// Após uma falha, espera antes de tentar de novo. Evita loop de retry contra
// 429/5xx e evita rajada quando a aba troca de visibilidade repetidamente.
var USDBRL_RETRY_COOLDOWN_MS=5*60*1000;

// Consulta em curso, compartilhada por todos os chamadores. Enquanto existir,
// refresh() devolve ESTA promessa em vez de disparar outra requisição: três
// chamadas concorrentes viram um fetch e três esperas pelo mesmo resultado.
var usdBrlPending=null;
var usdBrlLastAttemptAt=0;
var usdBrlLastError=null;
var usdBrlListeners=[];

// ---- Validação estrutural ---------------------------------------------------
// Protege integridade da resposta, não tenta prever mercado: nenhuma faixa
// econômica é imposta, apenas número finito e positivo do par esperado.
function usdBrlSanitize(payload){
  if(!payload || typeof payload!=='object') return null;
  var rate=payload.rate;
  if(typeof rate!=='number' || !isFinite(rate) || rate<=0) return null;
  if(payload.base && String(payload.base).toUpperCase()!=='USD') return null;
  if(payload.quote && String(payload.quote).toUpperCase()!=='BRL') return null;
  var ref=typeof payload.date==='string' && /^\d{4}-\d{2}-\d{2}$/.test(payload.date)
    ? payload.date : null;
  if(payload.date && !ref) return null;      // data presente porém inválida: recusa
  return {rate:rate, referenceDate:ref};
}

// ---- Cache técnico ----------------------------------------------------------
function usdBrlReadCache(){
  try{
    var raw=localStorage.getItem(USDBRL_CACHE_KEY);
    if(!raw) return null;
    var parsed=JSON.parse(raw);
    if(!parsed || typeof parsed!=='object' || typeof parsed.fetchedAt!=='number') return null;
    var clean=usdBrlSanitize(parsed.payload);
    if(!clean) return null;
    return {rate:clean.rate, referenceDate:clean.referenceDate,
            fetchedAt:parsed.fetchedAt, source:parsed.source||USDBRL_SOURCE};
  }catch(_){ return null; }
}
function usdBrlWriteCache(payload){
  try{
    localStorage.setItem(USDBRL_CACHE_KEY, JSON.stringify(
      {fetchedAt:Date.now(), source:USDBRL_SOURCE, payload:payload}));
  }catch(_){ /* cota cheia: segue em memória até a próxima consulta */ }
}

// ---- Leitura pública --------------------------------------------------------
// Contrato único que o resto do app enxerga. Nenhum consumidor conhece a URL,
// o formato do provedor ou a chave de cache.
//
//   status 'fresh'       consultamos dentro do TTL
//   status 'stale'       temos referência válida, mas a consulta envelheceu
//   status 'unavailable' nunca obtivemos referência alguma
//
// Em 'stale' o `rate` CONTINUA presente e utilizável — é a última referência
// publicada, e exibi-la com a data é o comportamento correto em fim de semana,
// feriado ou queda de rede. Quem consome decide como sinalizar.
function getCurrentUsdBrlQuote(){
  var c=usdBrlReadCache();
  if(!c) return {rate:null, referenceDate:null, fetchedAt:null,
                 source:USDBRL_SOURCE, status:'unavailable', pair:'USD/BRL'};
  var age=Date.now()-c.fetchedAt;
  return {rate:c.rate, referenceDate:c.referenceDate, fetchedAt:c.fetchedAt,
          source:c.source, status:age>USDBRL_TTL_MS?'stale':'fresh', pair:'USD/BRL'};
}
// Taxa para converter valor PRESENTE. Devolve null quando não há referência —
// jamais projectedFxRate, jamais 0. Quem chama exibe o estado, não um número
// inventado.
function currentUsdBrlRate(){
  var q=getCurrentUsdBrlQuote();
  return q.status==='unavailable'?null:q.rate;
}
function usdBrlIsLoading(){ return usdBrlPending!==null; }
function usdBrlLastFailure(){ return usdBrlLastError; }
function usdBrlOnChange(fn){ if(typeof fn==='function') usdBrlListeners.push(fn); }
function usdBrlNotify(){ usdBrlListeners.forEach(function(fn){ try{ fn(); }catch(_){}}); }

// ---- Consulta ---------------------------------------------------------------
function usdBrlShouldRefresh(){
  var q=getCurrentUsdBrlQuote();
  return q.status!=='fresh';
}
// force=true ignora TTL (botão manual), mas nunca ignora o cooldown de falha
// nem uma consulta já em curso: dois cliques não viram duas requisições.
//
// Idempotência: com consulta em andamento devolvemos a MESMA promessa, de modo
// que todo chamador aguarda a conclusão real em vez de receber de volta um
// estado intermediário. Sempre resolve (nunca rejeita) com o estado corrente —
// falha de rede é estado da cotação, não exceção para quem só quer exibir.
function usdBrlRefresh(force){
  if(usdBrlPending) return usdBrlPending;
  if(!force && !usdBrlShouldRefresh()) return Promise.resolve(getCurrentUsdBrlQuote());
  if(usdBrlLastError && (Date.now()-usdBrlLastAttemptAt)<USDBRL_RETRY_COOLDOWN_MS)
    return Promise.resolve(getCurrentUsdBrlQuote());
  usdBrlLastAttemptAt=Date.now();
  var ctrl=new AbortController();
  var timer=setTimeout(function(){ ctrl.abort(); }, USDBRL_TIMEOUT_MS);
  usdBrlPending=fetch(USDBRL_ENDPOINT,{signal:ctrl.signal,cache:'no-store'})
    .then(function(res){
      clearTimeout(timer);
      if(!res.ok) throw new Error('HTTP '+res.status);
      return res.json();
    })
    .then(function(payload){
      var clean=usdBrlSanitize(payload);
      if(!clean) throw new Error('resposta inválida');
      usdBrlWriteCache(payload);
      usdBrlLastError=null;
      return getCurrentUsdBrlQuote();
    })
    .catch(function(e){
      clearTimeout(timer);
      // Falha NÃO apaga o cache: a última referência válida continua servindo,
      // marcada pelo seu próprio estado. Erro nunca vira 0 nem premissa futura.
      usdBrlLastError=String((e&&e.message)||e||'falha desconhecida');
      return getCurrentUsdBrlQuote();
    })
    .finally(function(){
      // Libera a referência ANTES de notificar: o ouvinte repinta a tela, que
      // por sua vez chama refresh(false) — se a promessa ainda estivesse presa
      // aqui, ele receberia uma consulta já encerrada. Solto, quem decide é o
      // TTL (sucesso) ou o cooldown (falha), e nenhum dos dois abre requisição
      // nova neste instante. Roda também no caminho de erro.
      usdBrlPending=null;
      usdBrlNotify();
    });
  // Anúncio de "consultando" só agora: antes desta linha usdBrlPending ainda
  // era null e isLoading() responderia falso ao ouvinte que acabou de repintar.
  usdBrlNotify();
  return usdBrlPending;
}

window.JPWMarket=window.JPWMarket||{};
window.JPWMarket.usdBrl={
  get:getCurrentUsdBrlQuote, rate:currentUsdBrlRate, refresh:usdBrlRefresh,
  shouldRefresh:usdBrlShouldRefresh, isLoading:usdBrlIsLoading,
  lastFailure:usdBrlLastFailure, onChange:usdBrlOnChange,
  TTL_MS:USDBRL_TTL_MS, CACHE_KEY:USDBRL_CACHE_KEY
};

// Rede voltou: revalida se a consulta envelheceu. Sem polling — a cadência vem
// da entrada na tela, da volta à visibilidade, do TTL e do botão manual.
window.addEventListener('online',function(){ usdBrlRefresh(false); });
