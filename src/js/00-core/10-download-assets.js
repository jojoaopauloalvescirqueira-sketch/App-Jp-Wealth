// Public build-pinned assets. No request, JSON parsing or decoding before an action.
(function(){
  'use strict';
  const jobs=new Map(),cache=new Map();let sequence=0;
  const fail=message=>new Error(message),abort=()=>new DOMException('Download cancelado.','AbortError');
  function entry(id){
    const m=window.JPW_DOWNLOAD_MANIFEST,e=m?.resources?.[id],p=m?.payloads?.[e?.payload];
    if(m?.schemaVersion!==1||m.buildId!==JP_WEALTH_BUILD_ID||!e||!p||
      !/^leverage\/(dailySource|source|compiled|nativeKit|nativePin|preview)$/.test(id)||
      !/^downloads\/[A-Za-z0-9._/-]+$/.test(e.path)||e.path.includes('..')||
      e.filename!==e.path.split('/').pop()||!/^[A-Za-z0-9._-]+$/.test(e.filename)||!Number.isSafeInteger(e.bytes)||e.bytes<=0||
      !/^[a-f0-9]{64}$/.test(e.sha256)||e.mime!==(id==='leverage/preview'?'text/html':id==='leverage/nativePin'?'application/json':id.startsWith('leverage/')?'application/zip':e.mime)||typeof e.mime!=='string'||
      !/^src\/vendor\/downloads\/[a-z-]+-payload\.js$/.test(p.path)||p.elementId!=='jpw-download-payload-'+e.payload)
      throw fail('Metadados do arquivo inválidos.');
    return {e,p,m};
  }
  async function verify(id,bytes){
    const {e}=entry(id);if(bytes.length!==e.bytes)throw fail('Tamanho do arquivo diferente do manifesto.');
    const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
    if(digest!==e.sha256)throw fail('Hash do arquivo diferente do manifesto.');return bytes;
  }
  function validateEnvelope(id,envelope){
    if(envelope?.schemaVersion!==1||envelope.buildId!==JP_WEALTH_BUILD_ID||envelope.id!==id||!envelope.files||typeof envelope.files!=='object')throw fail('Payload incompatível com este build.');
    return envelope;
  }
  function group(id,p){
    if(jobs.has(id))return jobs.get(id).promise;
    const node=document.getElementById(p.elementId);
    const job={token:String(++sequence),script:null};
    let timer;
    job.promise=new Promise((resolve,reject)=>{
      job.resolve=value=>{clearTimeout(timer);resolve(value);};job.reject=error=>{clearTimeout(timer);reject(error);};
      if(node){try{if(node.type!=='application/json')throw fail('Payload inerte inválido.');job.resolve(validateEnvelope(id,JSON.parse(node.textContent)));}catch(error){job.reject(error);}return;}
      const script=document.createElement('script');job.script=script;script.src=(location.href?new URL(p.path,location.href).href:p.path);script.dataset.jpwDownloadToken=job.token;
      script.onerror=()=>job.reject(fail('Não foi possível carregar o arquivo.'));
      timer=setTimeout(()=>job.reject(fail('Tempo de carregamento excedido.')),15000);
      document.head.appendChild(script);
    });
    jobs.set(id,job);
    job.promise.catch(()=>{if(jobs.get(id)===job)jobs.delete(id);}).finally(()=>{job.script?.remove();});
    return job.promise;
  }
  async function load(id){
    const {e,p}=entry(id),node=document.getElementById(p.elementId);let bytes,attempt;
    try{
    if(node||location.protocol==='file:'||id==='leverage/preview'){
      const pending=group(e.payload,p);attempt=jobs.get(e.payload);const envelope=await pending,encoded=envelope.files[id];
      if(typeof encoded!=='string'||!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(encoded))throw fail('Arquivo incorporado ausente ou inválido.');
      bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));
    }else{
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
      try{const response=await fetch((location.href?new URL(e.path,location.href).href:e.path),{signal:controller.signal,redirect:'error'});if(!response.ok)throw fail('Arquivo não encontrado.');bytes=new Uint8Array(await response.arrayBuffer());}finally{clearTimeout(timer);}
    }
    return await verify(id,bytes);
    }catch(error){if(attempt&&jobs.get(e.payload)===attempt)jobs.delete(e.payload);throw error;}
  }
  function getBytes(id,{signal}={}){
    if(signal?.aborted)return Promise.reject(abort());
    try{entry(id);}catch(error){return Promise.reject(error);}
    if(!cache.has(id)){const promise=load(id);cache.set(id,promise);promise.catch(()=>{if(cache.get(id)===promise)cache.delete(id);});}
    return new Promise((resolve,reject)=>{
      const cancel=()=>{signal?.removeEventListener('abort',cancel);reject(abort());};signal?.addEventListener('abort',cancel,{once:true});
      cache.get(id).then(bytes=>{signal?.removeEventListener('abort',cancel);if(signal?.aborted)reject(abort());else resolve(bytes.slice());},error=>{signal?.removeEventListener('abort',cancel);reject(error);});
    });
  }
  window.JPWDownloadAssets=Object.freeze({getBytes,async getText(id,options){return new TextDecoder().decode(await getBytes(id,options));},
    register(id,envelope){const job=jobs.get(id),script=document.currentScript;
      if(!job||script!==job.script||script?.dataset.jpwDownloadToken!==job.token)return false;
      try{job.resolve(validateEnvelope(id,envelope));}catch(error){job.reject(error);}return true;}
  });
})();
