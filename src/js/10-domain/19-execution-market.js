// Daily public references are not broker ticks, ATR observations or manual prices.
// Only confirmed batches enter S.forex; refused batches remain in RAM for retry.
(function(root){
  'use strict';
  const fx=root.JPWForex, pairs=Object.freeze({EURUSD:['EUR','USD'],GBPUSD:['GBP','USD'],
    AUDUSD:['AUD','USD'],NZDUSD:['NZD','USD'],USDJPY:['USD','JPY'],USDCHF:['USD','CHF'],
    USDCAD:['USD','CAD'],AUDCAD:['AUD','CAD']});
  let generation=0,inFlight=null,controller=null,pending=null;
  let view={status:'IDLE',message:'Referências diárias; não são cotações de execução.',updated:0,failed:0,failures:[]};
  const epoch=()=>jpWealthPersistenceEpoch();
  const blocked=()=>jpWealthPersistenceIsBlocked()||jpWealthPersistenceOutcomeIsUnknown();
  function get(){
    if(pending&&pending.expectedEpoch!==epoch()){pending=null;view={status:'STALE',message:'A base mudou; a atualização anterior foi descartada.',updated:0,failed:0,failures:[]};}
    return {...structuredClone(view),busy:!!inFlight,pendingCount:pending?Object.keys(pending.quotes).length:0,
      canRetry:!!pending&&!inFlight&&!blocked()&&pending.expectedEpoch===epoch()};
  }
  function notify(){
    if(typeof root.dispatchEvent==='function'&&typeof CustomEvent==='function')root.dispatchEvent(new CustomEvent('jpwealth:forex-quotes',{detail:get()}));
  }
  function setView(value){view=value;notify();return get();}
  function invalidated(token,expectedEpoch){return token!==generation||expectedEpoch!==epoch()||blocked();}
  function validate(data,base,quote,fetchedAt){
    if(!data||typeof data!=='object'||data.base!==base||data.quote!==quote||
      typeof data.rate!=='number'||!Number.isFinite(data.rate)||data.rate<=0||
      typeof data.date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(data.date))throw new Error('Identidade, taxa ou data ausente/inválida.');
    const at=Date.parse(data.date+'T00:00:00Z');
    if(!Number.isFinite(at)||new Date(at).toISOString().slice(0,10)!==data.date||data.date>fetchedAt.slice(0,10))
      throw new Error('Data civil inválida ou posterior à consulta.');
    return {base,quote,rate:data.rate,referenceDate:data.date,fetchedAt,source:'Frankfurter',sourceKind:'DAILY_REFERENCE'};
  }
  async function request(base,quote,signal){
    let timer,abortHandler;
    const cancellation=new Promise((_,reject)=>{
      abortHandler=()=>reject(new Error('Consulta cancelada.'));
      signal.addEventListener('abort',abortHandler,{once:true});
      timer=setTimeout(()=>reject(new Error('Tempo de consulta excedido.')),6000);
    });
    try{
      const query=(async()=>{
        const response=await fetch('https://api.frankfurter.dev/v2/rate/'+base+'/'+quote,{signal,cache:'no-store'});
        if(!response.ok)throw new Error('HTTP '+response.status);
        return validate(await response.json(),base,quote,new Date().toISOString());
      })();
      return await Promise.race([query,cancellation]);
    }finally{clearTimeout(timer);signal.removeEventListener('abort',abortHandler);}
  }
  function commitPending(){
    if(!pending)return {ok:false,persistido:false,error:'Nenhuma atualização pendente.'};
    if(pending.expectedEpoch!==epoch()){
      pending=null;setView({status:'STALE',message:'A base mudou; consulte novamente.',updated:0,failed:0,failures:[]});
      return {ok:false,persistido:false,error:view.message};
    }
    if(blocked()){
      setView({...view,status:jpWealthPersistenceOutcomeIsUnknown()?'UNKNOWN':'BLOCKED',message:'Confira a persistência antes de tentar gravar novamente.'});
      return {ok:false,persistido:jpWealthPersistenceOutcomeIsUnknown()?null:false,error:view.message};
    }
    const result=fx.state.recordDailyReferences(pending),count=Object.keys(pending.quotes).length,failures=pending.failures;
    if(result.ok){
      pending=null;
      if(result.unchanged)setView({status:'UNCHANGED',message:'Referências já confirmadas; nenhuma alteração.'+(failures.length?' '+failures.length+' pares sem atualização.':''),updated:0,failed:failures.length,failures});
      else setView({status:failures.length?'PARTIAL':'SAVED',message:count+' referências diárias gravadas'+(failures.length?'; '+failures.length+' pares sem atualização.':'.'),updated:count,failed:failures.length,failures});
    }else setView({status:result.persistido===null?'UNKNOWN':'REFUSED',message:result.error,updated:0,failed:failures.length,failures});
    return {...result,...get()};
  }
  function update(){
    if(inFlight)return inFlight;
    get();
    if(pending)return Promise.resolve({...get(),ok:false,persistido:false,error:'Confira a tentativa pendente; use Tentar novamente ou Cancelar.'});
    if(blocked()||!fx.state.supported())return Promise.resolve({...setView({status:'BLOCKED',message:'A base não está disponível para atualização.',updated:0,failed:0,failures:[]}),ok:false,persistido:false});
    const token=++generation,expectedEpoch=epoch(),expectedRevision=fx.state.dailyReferenceRevision();
    const activeController=new AbortController();controller=activeController;
    setView({status:'FETCHING',message:'Consultando referências diárias FX…',updated:0,failed:0,failures:[]});
    const task=(async()=>{
      const names=Object.keys(pairs),results=await Promise.allSettled(names.map(name=>request(...pairs[name],activeController.signal)));
      if(invalidated(token,expectedEpoch)){
        if(token===generation)setView({status:'STALE',message:'Atualização invalidada pela mudança da base ou da persistência.',updated:0,failed:0,failures:[]});
        return {ok:false,persistido:false,...get()};
      }
      const quotes={},failures=[];
      results.forEach((result,index)=>{
        const name=names[index];
        if(result.status==='fulfilled')quotes[name]=result.value;
        else failures.push({instrumentId:name,message:String(result.reason?.message||'Consulta indisponível.')});
      });
      if(!Object.keys(quotes).length)return {ok:false,persistido:false,...setView({status:'FAILED',message:'Não foi possível atualizar. As referências anteriores foram preservadas.',updated:0,failed:failures.length,failures})};
      pending={quotes,expectedEpoch,expectedRevision,failures};
      return commitPending();
    })();
    inFlight=task.finally(()=>{
      activeController.abort();
      if(token===generation){inFlight=null;controller=null;notify();}
    }).then(result=>({...result,...get()}));
    return inFlight;
  }
  function retry(){
    if(inFlight)return Promise.resolve({ok:false,persistido:false,error:'Uma consulta já está em andamento.',...get()});
    return Promise.resolve(commitPending());
  }
  function cancel(){
    generation++;if(controller)controller.abort();controller=null;inFlight=null;pending=null;
    return setView({status:'CANCELLED',message:'Atualização cancelada; dados confirmados preservados.',updated:0,failed:0,failures:[]});
  }
  fx.marketQuotes=Object.freeze({update,retry,cancel,get,pairs});
  root.addEventListener('pagehide',cancel);
})(globalThis);
