/* Disponibilidade é preferência local de apresentação; não muda estado financeiro nem concede autoridade. */
(function(root){
  'use strict';
  if(root.JPWModuleAvailability)return;
  const KEY='jpw_module_availability_v1';
  const IDS=Object.freeze(['research','forex','personal-finance','alladin']);
  const DEFAULTS=Object.freeze({research:'active',forex:'active','personal-finance':'active',alladin:'frozen'});
  const listeners=new Set();
  const own=(object,key)=>Object.prototype.hasOwnProperty.call(object,key);
  const record=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
  let lastConfirmed=null;
  let current={raw:null,states:{...DEFAULTS},issues:[],document:null,valid:true,readable:false,confirmed:false,blocked:'read-error',reason:'init'};
  let listenerErrors=0;

  function inspect(raw){
    const result={valid:true,states:{...DEFAULTS},issues:[],document:null};
    const issue=code=>{result.valid=false;result.issues.push(code);};
    if(raw===null)return result;
    if(typeof raw!=='string'){issue('invalid-raw');return result;}
    try{result.document=JSON.parse(raw);}catch(error){issue('invalid-json');return result;}
    const doc=result.document;
    if(!record(doc)){issue('invalid-document');return result;}
    if(doc.schemaVersion!==1){issue('unsupported-version');return result;}
    if(Object.keys(doc).some(key=>key!=='schemaVersion'&&key!=='modules'))issue('unknown-document-field');
    if(!own(doc,'modules')||!record(doc.modules)){issue('invalid-modules');return result;}
    Object.keys(doc.modules).forEach(id=>{
      if(!IDS.includes(id)){issue('unknown-module:'+id);return;}
      const value=doc.modules[id];
      if(value!=='active'&&value!=='frozen'){issue('invalid-state:'+id);return;}
      result.states[id]=value;
    });
    return result;
  }

  // Strict import boundary: malformed and future values cannot enter restoration.
  function validate(raw){
    const result=inspect(raw);
    if(!result.valid)throw new Error('Disponibilidade de módulos inválida: '+result.issues.join(', '));
    return result;
  }

  function snapshot(){
    return Object.freeze({
      raw:current.raw,
      states:Object.freeze({...current.states}),
      issues:Object.freeze([...current.issues]),
      document:current.document===null?null:JSON.parse(JSON.stringify(current.document)),
      valid:current.valid,readable:current.readable,confirmed:current.confirmed,
      blocked:current.blocked,writable:current.readable&&current.valid&&!current.blocked,
      reason:current.reason,listenerErrors,
      lastConfirmedRaw:lastConfirmed?lastConfirmed.raw:null
    });
  }

  function notify(reason){
    current.reason=reason;
    const value=snapshot();
    // One failing presentation consumer must not hide the committed state from others.
    [...listeners].forEach(listener=>{
      try{listener(value,reason);}catch(error){
        listenerErrors+=1;
        if(root.console&&typeof root.console.error==='function')root.console.error('JPWModuleAvailability subscriber failed',error);
      }
    });
    return snapshot();
  }

  function adopt(raw,reason){
    const parsed=inspect(raw);
    current={...parsed,raw,readable:true,confirmed:parsed.valid,blocked:parsed.valid?'':'invalid-preference',reason};
    if(parsed.valid)lastConfirmed={raw,states:{...parsed.states}};
    return notify(reason);
  }

  function readFailure(reason,unknown){
    current={...current,states:{...(lastConfirmed?lastConfirmed.states:DEFAULTS)},
      readable:false,confirmed:false,blocked:unknown?'unknown':'read-error',
      issues:[...current.issues.filter(issue=>issue!=='read-error'),'read-error']};
    return notify(reason);
  }

  function reload(reason){
    const cause=reason||'reload';
    let raw;
    try{raw=root.localStorage.getItem(KEY);}catch(error){return readFailure(cause,current.blocked==='unknown');}
    return adopt(raw,cause);
  }

  function getState(id){return IDS.includes(id)?current.states[id]:'active';}
  // The route resolver still owns unknown destinations. Only the four module IDs are controlled here.
  function canAccess(id){return getState(id)!=='frozen';}

  function outcome(ok,reason,extra){return {ok,reason,...(extra||{}),snapshot:snapshot()};}

  function setState(id,state,options){
    if(!IDS.includes(id))return outcome(false,'invalid-module');
    if(state!=='active'&&state!=='frozen')return outcome(false,'invalid-state');
    if(current.blocked)return outcome(false,current.blocked);
    const expected=options&&own(options,'expectedRaw')?options.expectedRaw:current.raw;
    let before;
    try{before=root.localStorage.getItem(KEY);}catch(error){readFailure('write-preflight',false);return outcome(false,'read-error');}
    if(before!==expected||before!==current.raw){adopt(before,'conflict');return outcome(false,'conflict');}
    const parsed=inspect(before);
    if(!parsed.valid){adopt(before,'invalid-preference');return outcome(false,'invalid-preference');}
    if(parsed.states[id]===state)return outcome(true,'unchanged',{changed:false});
    const doc=parsed.document||{schemaVersion:1,modules:{}};
    const payload=JSON.stringify({schemaVersion:1,modules:{...doc.modules,[id]:state}});
    let writeThrew=false;
    try{root.localStorage.setItem(KEY,payload);}catch(error){writeThrew=true;}
    let after;
    try{after=root.localStorage.getItem(KEY);}catch(error){readFailure('write-unknown',true);return outcome(false,'unknown');}
    if(after===payload){adopt(after,'change');return outcome(true,'confirmed',{changed:true,writeThrew});}
    if(after===before){adopt(before,'write-refused');return outcome(false,'write-refused');}
    // A divergent read-back cannot establish which write won. Retain the last confirmed state.
    current={...current,states:{...(lastConfirmed?lastConfirmed.states:DEFAULTS)},confirmed:false,blocked:'unknown'};
    notify('write-unknown');
    return outcome(false,'unknown');
  }

  function subscribe(listener){
    if(typeof listener!=='function')throw new TypeError('O observador de disponibilidade deve ser uma função.');
    listeners.add(listener);
    return ()=>listeners.delete(listener);
  }

  root.JPWModuleAvailability=Object.freeze({KEY,IDS,DEFAULTS,inspect,validate,snapshot,getState,canAccess,reload,setState,subscribe});
  reload('init');
  if(typeof root.addEventListener==='function')root.addEventListener('storage',event=>{
    if(event.key!==KEY&&event.key!==null)return;
    // Do not treat sessionStorage events as this preference's localStorage update.
    if(event.storageArea){
      try{if(event.storageArea!==root.localStorage)return;}catch(error){readFailure('storage',current.blocked==='unknown');return;}
    }
    reload('storage');
  });
})(window);
