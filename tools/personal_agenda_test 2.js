/* Synthetic oracles for the authorized personal agenda contract, 2026-10-23.
 * Storage is isolated; persistence code is the actual canonical document writer.
 * The suite never opens a browser profile or reads real agenda/financial data. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {randomUUID}=require('node:crypto');
const root=path.resolve(__dirname,'..');
const file=process.env.JPW_AGENDA_SOURCE||path.join(root,'src/js/10-domain/19-personal-agenda.js');
const plain=value=>JSON.parse(JSON.stringify(value));
const task=(changes={})=>({kind:'task',title:'Tarefa sintética',notes:'Revisar com calma.',date:'2026-10-23',allDay:true,...changes});
const appointment=(changes={})=>({kind:'appointment',title:'Compromisso sintético',notes:'',date:'2026-10-23',allDay:false,startTime:'09:30',endDate:'2026-10-23',endTime:'10:30',timeZone:'America/Sao_Paulo',...changes});
function harness(initial={}){
  const storage={raw:JSON.stringify(initial),sets:0,reads:0,mode:'normal',getItem(){this.reads++;if(this.mode==='read-after'&&this.sets>this.failAfter)throw new Error('synthetic readback failure');return this.raw;},setItem(key,value){this.sets++;if(this.mode==='quota')throw new Error('synthetic quota');if(this.mode==='noop')return;if(this.mode==='diverge'){this.raw=JSON.stringify({foreign:'preserve'});return;}this.raw=value;}};
  class Clock extends Date{constructor(...args){super(...(args.length?args:['2026-10-23T12:00:00.000Z']));}static now(){return new Date('2026-10-23T12:00:00.000Z').getTime();}}
  const events=[],context=vm.createContext({console:{error(){}},structuredClone,Intl,Date:Clock,crypto:{randomUUID},initial:plain(initial),storage,CustomEvent,dispatchEvent:event=>{events.push(event.type);return true;}});
  vm.runInContext(`window=globalThis;let S=initial;const DEFAULTS=structuredClone(initial);const LSKEY='jpwealth_v9_state';let jpWealthSessionEpoch=0;let jpWealthPersistenceOutcomeUnknown=false;let jpWealthPersistenceBlocked=false;const jpWealthLoadRecovery={active:false};let jpWealthLastPersistedRaw=storage.raw;const localStorage=storage;
    function jpWealthPersistenceEpoch(){return jpWealthSessionEpoch;}
    function jpWealthPersistenceOutcomeIsUnknown(){return jpWealthPersistenceOutcomeUnknown;}
    function markJPWealthPersistenceOutcomeUnknown(){jpWealthPersistenceOutcomeUnknown=true;jpWealthSessionEpoch++;}
    function jpWealthAdoptPersistedRaw(value){jpWealthLastPersistedRaw=value;}
    function jpWealthPersistenceSetResult(status,reason,component){return {status,reason,component,ok:status==='CONFIRMED'};}
    function jpWealthPersistenceSafeFeedback(){}
    function dgLogChange(entity,action,id,label,target){if(target.dataGovernance?.changeLog)target.dataGovernance.changeLog.push({entity,action,id,label});}`,context);
  const source=fs.readFileSync(path.join(root,'src/js/00-core/04-persistence.js'),'utf8');
  const writer=source.slice(source.indexOf('function jpWealthPersistDocument('),source.indexOf('function save(){'));
  assert.ok(writer.includes('READBACK_MATCH'),'fixture loads actual confirmed writer and snapshot');
  vm.runInContext(writer,context);
  if(fs.existsSync(file))vm.runInContext(fs.readFileSync(file,'utf8'),context,{filename:file});
  return {api:context.JPWAgenda,context,storage,events,state:()=>plain(vm.runInContext('S',context)),setState(value){context.next=plain(value);vm.runInContext('S=next',context);},run:code=>vm.runInContext(code,context)};
}
function apiOf(h){assert.equal(typeof h.api?.queries?.prepare,'function','personal agenda exposes the authorized query/command API');return h.api;}
function prepare(h,id=null){return apiOf(h).queries.prepare({id});}
function save(h,input=task(),id=null){return apiOf(h).commands.save({input,token:prepare(h,id).token});}
function created(h,input=task()){const result=save(h,input);assert.equal(result.status,'CONFIRMED',JSON.stringify(result));return result.id;}
const tests=[];const test=(name,run)=>tests.push({name,run});
test('AGENDA-01 optional aggregate reads are pure and defensive',()=>{
  const h=harness({forex:{keep:1}}),api=apiOf(h),before=h.state(),raw=h.storage.raw;
  assert.deepEqual(plain(api.queries.snapshot()),{status:'OK',revision:0,items:[]});
  assert.deepEqual(plain(api.queries.range({from:'2026-10-01',to:'2026-10-31'})),{status:'OK',items:[]});
  assert.equal(prepare(h).ok,true);assert.equal(api.queries.previewEntry(task()).ok,true);
  assert.equal(h.storage.sets,0);assert.deepEqual(h.state(),before);assert.equal(h.storage.raw,raw);assert.equal('personalAgenda' in h.state(),false);
});
test('AGENDA-02 explicit create/update/completion/removal confirm one candidate each',()=>{
  const initial={forex:{keep:1},personalFinance:{keep:2},alladin:{keep:3},extension:{opaque:[1,'x']},dataGovernance:{changeLog:[]}};
  const h=harness(initial),api=apiOf(h),id=created(h),one=h.state().personalAgenda.items[0];
  assert.equal(one.kind,'task');assert.equal(one.date,'2026-10-23');assert.equal(one.completedAt,null);assert.equal(one.revision,1);assert.equal(one.allDay,true);assert.equal(one.startAt,null);assert.equal(one.timeZone,null);
  assert.equal(h.storage.sets,1);assert.deepEqual(JSON.parse(h.storage.raw),h.state());
  assert.equal(save(h,task({title:'Título corrigido'}),id).ok,true);
  assert.equal(api.commands.setCompleted({id,completed:true,token:prepare(h,id).token}).ok,true);
  assert.equal(api.queries.snapshot().items[0].completedAt,'2026-10-23T12:00:00.000Z');
  assert.equal(api.commands.setCompleted({id,completed:false,token:prepare(h,id).token}).ok,true);
  assert.equal(api.queries.snapshot().items[0].completedAt,null);
  assert.equal(api.commands.remove({id,token:prepare(h,id).token}).ok,true);assert.equal(h.storage.sets,5);assert.deepEqual(plain(api.queries.snapshot().items),[]);
  for(const key of ['forex','personalFinance','alladin','extension'])assert.deepEqual(h.state()[key],initial[key]);
});
test('AGENDA-03 previews validate fields without changing data or calling writer',()=>{
  const h=harness(),api=apiOf(h);
  for(const [input,field] of [[task({title:' '}),'title'],[task({date:'2026-02-30'}),'date'],[task({allDay:false}),'allDay'],[appointment({timeZone:'Mars/Olympus'}),'timeZone'],[appointment({startTime:'24:00'}),'startTime'],[appointment({endTime:'08:00'}),'endTime']]){
    const p=api.queries.previewEntry(input);assert.equal(p.ok,false,JSON.stringify(input));assert.ok(p.errors.some(e=>e.field===field&&typeof e.code==='string'&&typeof e.message==='string'),JSON.stringify(p));
  }
  assert.equal(api.queries.previewEntry(task({date:'2024-02-29'})).ok,true);assert.equal(h.storage.sets,0);
});
test('AGENDA-04 civil tasks stay dates and timed appointments preserve IANA instants',()=>{
  const h=harness(),api=apiOf(h);created(h,task({date:'2026-01-01'}));
  const p=api.queries.previewEntry(appointment());assert.equal(p.ok,true,JSON.stringify(p));assert.equal(p.entry.startAt,'2026-10-23T12:30:00.000Z');assert.equal(p.entry.endAt,'2026-10-23T13:30:00.000Z');assert.equal(p.entry.date,'2026-10-23');assert.equal(p.entry.timeZone,'America/Sao_Paulo');
  const edge=api.queries.previewEntry(appointment({date:'2026-01-01',startTime:'00:30',endDate:'2026-01-01',endTime:'01:00',timeZone:'Pacific/Kiritimati'}));assert.equal(edge.ok,true);assert.equal(edge.entry.startAt,'2025-12-31T10:30:00.000Z');
  assert.equal(api.queries.snapshot().items[0].date,'2026-01-01');
});
test('AGENDA-05 DST spring gap is refused with field-specific error',()=>{
  const h=harness(),api=apiOf(h),p=api.queries.previewEntry(appointment({date:'2026-03-08',startTime:'02:30',endDate:'2026-03-08',endTime:'04:00',timeZone:'America/New_York'}));
  assert.equal(p.ok,false);assert.ok(p.errors.some(e=>e.field==='startTime'&&e.code==='NONEXISTENT_TIME'));assert.equal(h.storage.sets,0);
});
test('AGENDA-06 DST fold requires exact explicit choice and stores chosen instant',()=>{
  const h=harness(),api=apiOf(h),input=appointment({date:'2026-11-01',startTime:'01:30',endDate:'2026-11-01',endTime:'02:30',timeZone:'America/New_York'}),p=api.queries.previewEntry(input);
  assert.equal(p.ok,false);const a=p.ambiguities.find(a=>a.field==='startAtChoice');assert.ok(a);assert.deepEqual(plain(a.options.map(o=>o.value)),['2026-11-01T05:30:00.000Z','2026-11-01T06:30:00.000Z']);
  for(const option of a.options)assert.ok(option.label&&option.label.includes('UTC'));
  assert.equal(api.queries.previewEntry({...input,startAtChoice:'2026-11-01T07:30:00.000Z'}).ok,false);
  const id=created(h,{...input,startAtChoice:a.options[1].value});assert.equal(api.queries.snapshot().items.find(i=>i.id===id).startAt,a.options[1].value);
});
test('AGENDA-07 end fold, half-hour DST and leap dates are independently resolved',()=>{
  const h=harness(),api=apiOf(h),input=appointment({date:'2026-11-01',startTime:'00:30',endDate:'2026-11-01',endTime:'01:30',timeZone:'America/New_York'});
  const p=api.queries.previewEntry(input);assert.equal(p.ok,false);assert.deepEqual(plain(p.ambiguities[0].options.map(o=>o.value)),['2026-11-01T05:30:00.000Z','2026-11-01T06:30:00.000Z']);assert.equal(p.ambiguities[0].field,'endAtChoice');
  const half=api.queries.previewEntry(appointment({date:'2026-04-05',startTime:'01:45',endDate:'2026-04-05',endTime:'02:30',timeZone:'Australia/Lord_Howe'}));assert.equal(half.ok,false);assert.deepEqual(plain(half.ambiguities[0].options.map(o=>o.value)),['2026-04-04T14:45:00.000Z','2026-04-04T15:15:00.000Z']);
});
test('AGENDA-08 range includes overnight appointments and excludes unrelated civil dates',()=>{
  const h=harness(),api=apiOf(h),id=created(h,appointment({date:'2026-10-23',startTime:'23:30',endDate:'2026-10-24',endTime:'01:00'}));created(h,task({date:'2026-10-25'}));
  assert.deepEqual(plain(api.queries.range({from:'2026-10-24',to:'2026-10-24'}).items.map(i=>i.id)),[id]);
  assert.equal(api.queries.range({from:'2026-10-26',to:'2026-10-25'}).status,'INVALID');
  const snap=api.queries.snapshot();snap.items[0].title='external mutation';assert.notEqual(api.queries.snapshot().items[0].title,'external mutation');
});
test('AGENDA-09 quota/no-op writer preserves old RAM and disk and invalidates attempted token',()=>{
  for(const mode of ['quota','noop']){
    const h=harness(),api=apiOf(h),id=created(h),token=prepare(h,id).token,before=h.state(),raw=h.storage.raw;h.storage.mode=mode;
    assert.equal(api.commands.save({input:task({title:'Changed'}),token}).status,'REFUSED');assert.deepEqual(h.state(),before);assert.equal(h.storage.raw,raw);
    h.storage.mode='normal';assert.equal(api.commands.save({input:task({title:'Changed'}),token}).status,'CONFLICT');
  }
});
test('AGENDA-10 uncertain readback keeps old RAM, blocks retry and preserves physical candidate',()=>{
  const h=harness(),api=apiOf(h),before=h.state(),token=prepare(h).token;h.storage.mode='read-after';h.storage.failAfter=h.storage.sets;
  assert.equal(api.commands.save({input:task(),token}).status,'UNKNOWN');assert.deepEqual(h.state(),before);assert.equal(JSON.parse(h.storage.raw).personalAgenda.items.length,1);
  const writes=h.storage.sets;h.storage.mode='normal';assert.equal(api.commands.save({input:task(),token}).status,'UNKNOWN');assert.equal(h.storage.sets,writes);
});
test('AGENDA-11 concurrent disk, stale item and foreign tokens never overwrite',()=>{
  const h=harness(),api=apiOf(h),a=created(h),b=created(h,task({title:'Other'})),old=prepare(h,a).token;
  assert.equal(api.commands.remove({id:b,token:old}).status,'CONFLICT');assert.equal(save(h,task({title:'Edited'}),a).ok,true);
  assert.equal(api.commands.remove({id:a,token:old}).status,'CONFLICT');
  const token=prepare(h,a).token,before=h.state();h.storage.raw=JSON.stringify({anotherTab:'preserve'});
  assert.equal(api.commands.remove({id:a,token}).status,'CONFLICT');assert.deepEqual(h.state(),before);assert.equal(h.storage.raw,JSON.stringify({anotherTab:'preserve'}));
});
test('AGENDA-12 adjacent unconfirmed financial RAM is never confirmed by agenda',()=>{
  const h=harness({forex:{record:1},personalFinance:{record:1},alladin:{record:1}}),api=apiOf(h),token=prepare(h).token;
  h.run('S.forex.record=2;S.personalFinance.record=3;S.alladin.record=4');
  assert.equal(api.commands.save({input:task(),token}).status,'CONFLICT');assert.equal(h.storage.sets,0);assert.equal(JSON.parse(h.storage.raw).forex.record,1);assert.equal(h.state().forex.record,2);
});
test('AGENDA-13 incompatible/future aggregate remains opaque and blocks mutation',()=>{
  for(const personalAgenda of [{schemaVersion:99,opaque:{keep:[1,'future']}},{schemaVersion:1,revision:0,items:'broken'},null]){
    const h=harness({personalAgenda}),api=apiOf(h),before=h.state();assert.equal(api.queries.snapshot().status,'INCOMPATIBLE');assert.equal(api.queries.range({from:'2026-10-01',to:'2026-10-31'}).status,'INCOMPATIBLE');assert.equal(prepare(h).ok,false);
    assert.equal(api.commands.save({input:task(),token:{}}).ok,false);assert.deepEqual(h.state(),before);assert.equal(h.storage.sets,0);
  }
});
test('AGENDA-14 compatible unknown fields survive item edits and root roundtrip',()=>{
  const h=harness(),api=apiOf(h),id=created(h),saved=h.state();saved.personalAgenda.extension={opaque:[1,'keep']};saved.personalAgenda.items[0].extension={keep:'item'};h.setState(saved);h.storage.raw=JSON.stringify(saved);h.context.adopted=h.storage.raw;h.run('jpWealthLastPersistedRaw=adopted');
  api.commands.resetContext();assert.equal(save(h,task({title:'Roundtrip'}),id).ok,true);
  const imported=harness(JSON.parse(h.storage.raw));assert.equal(imported.api.queries.snapshot().items[0].title,'Roundtrip');assert.deepEqual(imported.state().personalAgenda.extension,{opaque:[1,'keep']});assert.deepEqual(imported.state().personalAgenda.items[0].extension,{keep:'item'});
});
test('AGENDA-15 session/root replacement invalidates prepared commands without invalidating ordinary reads',()=>{
  const h=harness(),api=apiOf(h),id=created(h),token=prepare(h,id).token;assert.equal(api.commands.resetContext(),false);assert.equal(api.commands.setCompleted({id,completed:true,token}).ok,true);
  const next=prepare(h,id).token;api.commands.disposeForSession();assert.equal(api.commands.remove({id,token:next}).status,'CONFLICT');
  const replaced=prepare(h,id).token;h.setState(h.state());assert.equal(api.commands.remove({id,token:replaced}).status,'CONFLICT');
});
test('AGENDA-16 recovery, workspace and finalization gates refuse before writing',()=>{
  for(const statement of ['jpWealthLoadRecovery.active=true','jpWealthPersistenceBlocked=true','S.workspaceRecovery={pending:true}']){
    const h=harness(),api=apiOf(h),token=prepare(h).token;h.run(statement);const before=h.state();const r=api.commands.save({input:task(),token});assert.equal(r.ok,false);assert.deepEqual(h.state(),before);assert.equal(h.storage.sets,0);
  }
});
test('AGENDA-17 control and secret keys cannot enter explicit commands',()=>{
  const h=harness(),api=apiOf(h);
  for(const input of [task({password:'synthetic'}),task({token:'synthetic'}),JSON.parse('{"kind":"task","title":"X","date":"2026-10-23","allDay":true,"__proto__":{"x":1}}'),task({title:'x\u0000y'})])assert.equal(api.queries.previewEntry(input).ok,false);
  assert.equal(h.storage.sets,0);
});
test('AGENDA-18 all-day appointments are civil and completing them is refused',()=>{
  const h=harness(),api=apiOf(h),id=created(h,appointment({allDay:true,date:'2026-12-31'})),entry=api.queries.snapshot().items[0];assert.equal(entry.date,'2026-12-31');assert.equal(entry.startAt,null);assert.equal(entry.endAt,null);assert.equal(entry.timeZone,null);
  assert.equal(api.commands.setCompleted({id,completed:true,token:prepare(h,id).token}).status,'INVALID');assert.equal(h.storage.sets,1);
});
test('AGENDA-19 timed range uses viewing zone and midnight end is exclusive',()=>{
  const h=harness(),api=apiOf(h),id=created(h,appointment({date:'2026-10-23',startTime:'01:00',endDate:'2026-10-23',endTime:'03:00',timeZone:'UTC'})),civil=created(h,task({date:'2026-10-23'}));
  assert.deepEqual(plain(api.queries.range({from:'2026-10-22',to:'2026-10-22',timeZone:'America/Sao_Paulo'}).items.map(i=>i.id)),[id]);
  assert.deepEqual(plain(api.queries.range({from:'2026-10-23',to:'2026-10-23',timeZone:'America/Sao_Paulo'}).items.map(i=>i.id)),[civil]);
  assert.ok(api.queries.range({from:'2026-10-23',to:'2026-10-23',timeZone:'UTC'}).items.some(i=>i.id===id));
  assert.equal(api.queries.range({from:'2026-10-23',to:'2026-10-23',timeZone:'Mars/Olympus'}).status,'INVALID');
});
test('AGENDA-20 no-op completion still checks current durable document',()=>{
  const h=harness(),api=apiOf(h),id=created(h),token=prepare(h,id).token;h.storage.raw=JSON.stringify({anotherTab:'preserve'});
  assert.equal(api.commands.setCompleted({id,completed:false,token}).status,'CONFLICT');assert.equal(h.storage.raw,JSON.stringify({anotherTab:'preserve'}));assert.equal(h.storage.sets,1);
});
test('AGENDA-21 invalid range inputs return errors and numeric offsets are not IANA zones',()=>{
  const h=harness(),api=apiOf(h);assert.equal(api.queries.range(null).status,'INVALID');
  assert.equal(api.queries.previewEntry(appointment({timeZone:'+01:00'})).ok,false);assert.equal(h.storage.sets,0);
});
test('AGENDA-22 change event follows confirmed adoption and observer failure cannot change durable success',()=>{
  const h=harness(),api=apiOf(h);let adopted=false;
  h.context.dispatchEvent=event=>{h.events.push(event.type);adopted=h.state().personalAgenda.items.length===1;throw Error('synthetic observer failure');};
  const id=created(h);assert.equal(adopted,true);assert.deepEqual(h.events,['jpw-agenda-changed']);assert.equal(JSON.parse(h.storage.raw).personalAgenda.items[0].id,id);
  h.storage.mode='quota';assert.equal(save(h,task({title:'Refused'}),id).status,'REFUSED');assert.deepEqual(h.events,['jpw-agenda-changed']);
});
let failed=0;
for(const item of tests){try{item.run();process.stdout.write('PASS '+item.name+'\n');}catch(error){failed++;process.stdout.write('FAIL '+item.name+'\n'+error.stack+'\n');}}
process.stdout.write(JSON.stringify({total:tests.length,passed:tests.length-failed,failed})+'\n');process.exitCode=failed?1:0;
