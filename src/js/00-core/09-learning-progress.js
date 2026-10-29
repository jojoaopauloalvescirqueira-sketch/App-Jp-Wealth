// Progresso local de aprendizagem. Sem dados financeiros e sem recuperação
// automática: um documento incompatível só pode ser removido por restart.
(function(){
  'use strict';
  const KEY='jpwealth_learning_guide_v1';
  const own=(object,key)=>Object.prototype.hasOwnProperty.call(object,key);
  const blocked=new Set(['__proto__','prototype','constructor']);
  function plain(value){
    if(!value||typeof value!=='object'||Array.isArray(value))return false;
    const prototype=Object.getPrototypeOf(value);
    // Aceita também objetos simples de outro realm e mapas sem protótipo.
    if(prototype===null)return true;
    const constructor=Object.getOwnPropertyDescriptor(prototype,'constructor');
    return Object.getPrototypeOf(prototype)===null&&constructor&&own(constructor,'value')&&
      typeof constructor.value==='function'&&constructor.value.prototype===prototype&&
      Function.prototype.toString.call(constructor.value)===Function.prototype.toString.call(Object);
  }
  function keys(value,allowed){
    if(!plain(value))return false;
    const names=Reflect.ownKeys(value);
    return names.length===allowed.length&&names.every(name=>typeof name==='string'&&
      allowed.includes(name)&&own(Object.getOwnPropertyDescriptor(value,name),'value'));
  }
  function registry(catalog){
    if(!catalog||catalog.version!==1||!Array.isArray(catalog.tracks))return null;
    const tracks=new Map(),steps=new Map();
    for(const track of catalog.tracks){
      if(!track||typeof track.id!=='string'||!track.id||blocked.has(track.id)||
        tracks.has(track.id)||!Array.isArray(track.steps))return null;
      tracks.set(track.id,true);
      for(const step of track.steps){
        if(!step||typeof step.id!=='string'||!step.id||blocked.has(step.id)||steps.has(step.id))return null;
        steps.set(step.id,track.id);
      }
    }
    // Retired IDs remain valid records, never visible lessons or new credits.
    if(catalog.retiredSteps!==undefined){
      if(!Array.isArray(catalog.retiredSteps))return null;
      for(const item of catalog.retiredSteps){
        if(!item||typeof item.id!=='string'||!item.id||blocked.has(item.id)||steps.has(item.id)||!tracks.has(item.trackId)||steps.get(item.replacementId)!==item.trackId)return null;
        steps.set(item.id,item.trackId);
      }
    }
    const previousOwners=new Map();
    if(catalog.movedSteps!==undefined){
      if(!Array.isArray(catalog.movedSteps))return null;
      for(const item of catalog.movedSteps){
        if(!item||!tracks.has(item.trackId)||!tracks.has(item.previousTrackId)||item.trackId===item.previousTrackId||steps.get(item.id)!==item.trackId||previousOwners.has(item.id))return null;
        previousOwners.set(item.id,item.previousTrackId);
      }
    }
    return {tracks,steps,previousOwners};
  }
  function empty(catalog){
    return {schemaVersion:2,mode:'journey',catalogVersion:catalog?.version,trackId:null,stepId:null,paused:true,steps:{}};
  }
  const failure=(reason,raw)=>({ok:false,reason,document:null,...(raw===undefined?{}:{raw})});
  function validate(value,catalog){
    const ids=registry(catalog);
    const legacy=plain(value)&&Object.getOwnPropertyDescriptor(value,'schemaVersion')?.value===1;
    if(!ids||!keys(value,legacy?['schemaVersion','catalogVersion','trackId','stepId','paused','steps']:['schemaVersion','mode','catalogVersion','trackId','stepId','paused','steps'])||
      (!legacy&&(value.schemaVersion!==2||!['journey','track'].includes(value.mode)))||value.catalogVersion!==catalog.version||typeof value.paused!=='boolean'||
      !plain(value.steps))return failure('incompatible');
    if(value.trackId===null||value.stepId===null){
      if(value.trackId!==null||value.stepId!==null)return failure('incompatible');
    }else if(typeof value.trackId!=='string'||typeof value.stepId!=='string'||
      !ids.tracks.has(value.trackId)||(ids.steps.get(value.stepId)!==value.trackId&&ids.previousOwners.get(value.stepId)!==value.trackId))return failure('incompatible');
    const records={};
    for(const id of Reflect.ownKeys(value.steps)){
      const descriptor=Object.getOwnPropertyDescriptor(value.steps,id);
      if(typeof id!=='string'||blocked.has(id)||!ids.steps.has(id)||!own(descriptor,'value'))return failure('incompatible');
      const record=descriptor.value;
      if(!keys(record,['orientation','practice'])||!['seen','skipped'].includes(record.orientation)||
        ![null,'confirmed'].includes(record.practice)||
        (record.practice==='confirmed'&&record.orientation!=='seen'))return failure('incompatible');
      records[id]={orientation:record.orientation,practice:record.practice};
    }
    return {ok:true,reason:'confirmed',document:{schemaVersion:2,mode:legacy?(value.trackId===null?'journey':'track'):value.mode,catalogVersion:catalog.version,
      trackId:value.trackId,stepId:value.stepId,paused:value.paused,steps:records}};
  }
  function inspect(raw,catalog){
    if(!registry(catalog))return failure('incompatible');
    if(raw===null)return {ok:true,reason:'missing',document:empty(catalog)};
    if(typeof raw!=='string')return failure('incompatible');
    try{return validate(JSON.parse(raw),catalog);}catch(_){return failure('incompatible');}
  }
  function stored(){
    try{
      const storage=window.localStorage;
      if(!storage||typeof storage.getItem!=='function')return failure('storage-unavailable');
      const raw=storage.getItem(KEY);
      if(raw!==null&&typeof raw!=='string')return failure('storage-unavailable');
      return {ok:true,storage,raw};
    }catch(_){return failure('storage-unavailable');}
  }
  function read(catalog){
    const current=stored();
    if(!current.ok)return current;
    return {...inspect(current.raw,catalog),raw:current.raw};
  }
  function expectation(options){
    return options&&own(options,'expectedRaw')&&
      own(Object.getOwnPropertyDescriptor(options,'expectedRaw'),'value')&&
      (options.expectedRaw===null||typeof options.expectedRaw==='string');
  }
  function write(document,catalog,options){
    if(!expectation(options))return failure('refused');
    let candidate;
    try{candidate=validate(document,catalog);}catch(_){return failure('incompatible');}
    if(!candidate.ok)return candidate;
    const before=stored();
    if(!before.ok)return before;
    if(before.raw!==options.expectedRaw)return {...inspect(before.raw,catalog),ok:false,reason:'concurrent-change',raw:before.raw};
    const existing=inspect(before.raw,catalog);
    if(!existing.ok)return {...existing,raw:before.raw};
    const raw=JSON.stringify(candidate.document);
    // A exceção não determina o resultado: alguns hosts lançam após gravar.
    try{before.storage.setItem(KEY,raw);}catch(_){}
    const after=stored();
    if(!after.ok)return {...candidate,ok:false,reason:'unknown'};
    if(after.raw===raw)return {...candidate,raw};
    return {...candidate,ok:false,reason:after.raw===before.raw?'refused':'unknown',raw:after.raw};
  }
  function reset(catalog,options){
    if(!expectation(options))return failure('refused');
    if(!registry(catalog))return failure('incompatible');
    const before=stored();
    if(!before.ok)return before;
    if(before.raw!==options.expectedRaw)return {...inspect(before.raw,catalog),ok:false,reason:'concurrent-change',raw:before.raw};
    try{before.storage.removeItem(KEY);}catch(_){}
    const after=stored();
    if(!after.ok)return failure('unknown');
    if(after.raw===null)return {ok:true,reason:'confirmed',document:empty(catalog),raw:null};
    return failure(after.raw===before.raw?'refused':'unknown',after.raw);
  }
  window.JPWLearningProgress=Object.freeze({KEY,empty,inspect,read,write,reset});
})();
