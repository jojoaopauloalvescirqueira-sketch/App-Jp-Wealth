// Build-pinned public market resources. No transport/parse/execute before entry.
(function(){
  'use strict';
  const jobs=new Map(),encoder=new TextEncoder();let sequence=0,payloadJob=null;
  const paths=Object.freeze({catalog:'src/data/market-hours/calendar-v1.json',renderer:'src/vendor/aisol-dot-globe/aisol-globe.iife.js'});
  const abort=()=>new DOMException('Carregamento cancelado.','AbortError');
  function manifest(id){
    const m=window.JPW_MARKET_HOURS_MANIFEST,e=m?.resources?.[id];
    if(typeof JP_WEALTH_BUILD_ID!=='string'||m?.schemaVersion!==1||m.buildId!==JP_WEALTH_BUILD_ID||!Object.hasOwn(paths,id)||
      !e||e.path!==paths[id]||!Number.isSafeInteger(e.bytes)||e.bytes<=0||e.bytes>10000000||!/^[a-f0-9]{64}$/.test(e.sha256)||
      m.payload?.path!=='src/vendor/market-hours/runtime-payload.js'||m.payload.elementId!=='jpw-market-hours-payload')
      throw Error('Recursos de Bolsas Globais incompatíveis com este build.');
    return {m,e};
  }
  function checkEnvelope(value){
    const {m}=manifest('catalog');
    if(value?.schemaVersion!==1||value.buildId!==m.buildId||!value.files||typeof value.files.catalog!=='string'||typeof value.files.renderer!=='string')
      throw Error('Pacote local de Bolsas Globais inválido.');
    return value;
  }
  function getPayload(){
    if(payloadJob)return payloadJob.promise;
    const {m}=manifest('catalog'),node=document.getElementById(m.payload.elementId);
    const job={token:String(++sequence),script:null,timer:null,resolve:null,reject:null};payloadJob=job;
    job.promise=new Promise((resolve,reject)=>{
      job.resolve=resolve;job.reject=reject;
      if(node){try{if(node.type!=='application/json')throw Error('Pacote incorporado não é JSON inerte.');resolve(checkEnvelope(JSON.parse(node.textContent)));}catch(error){reject(error);}return;}
      const script=document.createElement('script');job.script=script;script.src=m.payload.path;script.dataset.jpwMarketToken=job.token;
      script.onerror=()=>reject(Error('Não foi possível abrir o pacote local de Bolsas Globais.'));
      job.timer=setTimeout(()=>reject(Error('Tempo de carregamento excedido. Tente novamente.')),15000);document.head.append(script);
    });
    job.promise.catch(()=>{if(payloadJob===job)payloadJob=null;}).finally(()=>{clearTimeout(job.timer);job.script?.remove();});
    return job.promise;
  }
  async function bytes(id,job){
    const {e}=manifest(id);let value;
    if(location.protocol==='file:'||document.getElementById('jpw-market-hours-payload')){
      const payload=await getPayload();value=encoder.encode(payload.files[id]);
    }else{
      let expired=false;const timer=setTimeout(()=>{expired=true;job.controller.abort();},15000);
      try{const response=await fetch(e.path,{signal:job.controller.signal,cache:'default'});if(!response.ok)throw Error('Recurso de Bolsas Globais indisponível ('+response.status+').');value=new Uint8Array(await response.arrayBuffer());}
      catch(error){if(expired)throw Error('Tempo de carregamento excedido. Tente novamente.');throw error;}
      finally{clearTimeout(timer);}
    }
    if(job.cancelled)throw abort();
    if(value.byteLength!==e.bytes)throw Error('Tamanho do recurso de Bolsas Globais divergente.');
    if(!crypto?.subtle)throw Error('Este navegador não permite verificar os recursos locais.');
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',value)),n=>n.toString(16).padStart(2,'0')).join('');
    if(job.cancelled)throw abort();
    // Recheck the build after asynchronous transport/digest as well.
    if(manifest(id).e.sha256!==e.sha256||hash!==e.sha256)throw Error('Integridade do recurso de Bolsas Globais não confirmada.');
    return value;
  }
  function execute(source){
    let error=null;const onError=event=>{error=event.error||Error(event.message);};
    const script=document.createElement('script');script.textContent=source;script.dataset.jpwMarketRuntime='';
    window.addEventListener('error',onError);try{document.head.append(script);}finally{window.removeEventListener('error',onError);script.remove();}
    if(error)throw error;
    const api=window.JPWAisolGlobeRuntime;
    if(!api||typeof api.create!=='function'||typeof api.threeVersion!=='string'||!/^[a-f0-9]{64}$/.test(api.sourceSHA256))throw Error('Motor Aisol local incompatível.');
    return api;
  }
  function getJob(id){
    manifest(id);if(jobs.has(id))return jobs.get(id);
    const job={controller:new AbortController(),users:new Set(),cancelled:false,settled:false,promise:null};jobs.set(id,job);
    job.promise=Promise.resolve().then(async()=>{
      if(job.cancelled)throw abort();
      const data=await bytes(id,job);if(job.cancelled)throw abort();
      const text=new TextDecoder('utf-8',{fatal:true}).decode(data);
      if(id==='catalog'){
        if(typeof window.JPWMarketSessions?.prepare!=='function')throw Error('Motor de sessões não está disponível.');
        return window.JPWMarketSessions.prepare(JSON.parse(text));
      }
      return execute(text);
    });
    job.promise.then(()=>{job.settled=true;},()=>{job.settled=true;if(jobs.get(id)===job)jobs.delete(id);});
    return job;
  }
  function consume(id,{signal}={}){
    if(signal?.aborted)return Promise.reject(abort());
    let job;try{job=getJob(id);}catch(error){return Promise.reject(error);}
    return new Promise((resolve,reject)=>{
      const user={};job.users.add(user);let done=false;
      const release=()=>{signal?.removeEventListener('abort',cancel);job.users.delete(user);};
      const cancel=()=>{if(done)return;done=true;release();reject(abort());
        if(!job.users.size&&!job.settled){job.cancelled=true;job.controller.abort();if(jobs.get(id)===job)jobs.delete(id);}};
      signal?.addEventListener('abort',cancel,{once:true});
      job.promise.then(value=>{if(done)return;done=true;release();if(signal?.aborted)reject(abort());else resolve(value);},error=>{if(done)return;done=true;release();reject(error);});
      if(signal?.aborted)cancel();
    });
  }
  window.JPWMarketHoursAssets=Object.freeze({
    getCatalog:options=>consume('catalog',options),getRenderer:options=>consume('renderer',options),
    register(envelope){const job=payloadJob,script=document.currentScript;
      if(!job||script!==job.script||script?.dataset.jpwMarketToken!==job.token)return false;
      try{job.resolve(checkEnvelope(envelope));}catch(error){job.reject(error);}return true;}
  });
})();
