/* Synthetic state/command contract. Source: approved planning plan/decision 2026-10-20.
 * The fake writer isolates command behavior; browser integration exercises the
 * real confirmed writer separately. No browser profile or real financial data. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {randomUUID}=require('node:crypto');
const root=path.resolve(__dirname,'..');
const moduleFile=process.env.JPW_PLANNING_STATE_SOURCE||path.join(root,'src/js/30-accounting/06-planning/02-state.js');
const engineFile=path.join(root,'src/js/30-accounting/06-planning/01-engine.js');
const plain=value=>JSON.parse(JSON.stringify(value));
const config=(changes={})=>({name:'Conta sintética',broker:'Corretora teste',login:'100',server:'Demo',
  startMonth:'2026-01',initialUsd:1000,profileId:'base',monthlyContributionUsd:200,
  goals:{adequate:null,ideal:{value:5000,currency:'USD'}},...changes});
const quote={rate:5,referenceDate:'2026-10-19',fetchedAt:'2026-10-20T12:00:00.000Z',source:'Frankfurter'};
function harness(initial={}){
  const control={calls:[],mode:'CONFIRMED',disk:plain(initial),beforeWrite:null,timelineCalls:0};
  class Clock extends Date{constructor(...args){super(...(args.length?args:['2026-10-20T12:00:00.000Z']));}static now(){return new Date('2026-10-20T12:00:00.000Z').getTime();}}
  const context=vm.createContext({console,structuredClone,crypto:{randomUUID},Date:Clock,initial:plain(initial),control,
    getCurrentUsdBrlQuote:()=>({...quote,status:'fresh'}),jpWealthPersistenceEpoch:()=>control.epoch||0,
    jpWealthPersistenceOutcomeIsUnknown:()=>!!control.unknown,
    markJPWealthPersistenceOutcomeUnknown:()=>{control.unknown=true;control.epoch=(control.epoch||0)+1;},
    dgLogChange:(entity,action,recordId,label,target)=>{if(target.dataGovernance?.changeLog)target.dataGovernance.changeLog.push({entity,action,recordId,label});},
    jpWealthPersistDocument:(candidate,options)=>{
      control.calls.push({candidate:plain(candidate),options});
      if(control.beforeWrite)control.beforeWrite(candidate);
      if(control.mode==='THROW')throw new Error('synthetic interrupted writer');
      if(control.mode==='UNKNOWN'){control.unknown=true;return {status:'UNKNOWN',reason:'READ_AFTER_WRITE'};}
      if(control.mode==='CONFLICT')return {status:'REFUSED',reason:'CONFLICT'};
      if(control.mode==='REFUSED')return {status:'REFUSED',reason:'WRITE_REFUSED'};
      control.disk=plain(candidate);return {status:'CONFIRMED',payload:JSON.stringify(candidate)};
    }});
  vm.runInContext('let S=initial; window=globalThis;',context);
  assert.ok(fs.existsSync(moduleFile),'planning commands module must exist');
  assert.ok(fs.existsSync(engineFile),'planning engine prerequisite must exist');
  const engineSource=fs.readFileSync(engineFile,'utf8');
  assert.equal(engineSource.split('function timeline(plan, options) {').length,2,'timeline probe has one exact entry point');
  vm.runInContext(engineSource.replace('function timeline(plan, options) {','function timeline(plan, options) { control.timelineCalls++;'),context,{filename:engineFile});
  vm.runInContext(fs.readFileSync(moduleFile,'utf8'),context,{filename:moduleFile});
  const api=context.JPWPlanning;
  assert.equal(typeof api?.commands?.execute,'function','commands.execute is available');
  return {api,control,context,state:()=>plain(vm.runInContext('S',context)),setState:value=>{context.next=plain(value);vm.runInContext('S=next',context);}};
}
function realWriterHarness(initial={}){
  const h=harness(initial),raw=JSON.stringify(initial),control=h.control;
  h.context.storage={raw,sets:0,mode:'normal',getItem(){
    if(this.mode==='read-after'&&this.sets)throw new Error('synthetic readback failure');return this.raw;
  },setItem(key,value){this.sets++;if(this.mode==='quota')throw new Error('synthetic quota');this.raw=value;}};
  h.context.jpWealthPersistenceSetResult=(status,reason,component)=>({status,reason,component,ok:status==='CONFIRMED'});
  h.context.jpWealthPersistenceSafeFeedback=()=>{};
  h.context.jpWealthAdoptPersistedRaw=value=>{h.context.acceptedRaw=value;};
  h.context.acceptedRaw=raw;
  vm.runInContext('const LSKEY="jpwealth_v9_state";let jpWealthSessionEpoch=0;let jpWealthPersistenceOutcomeUnknown=false;let jpWealthPersistenceBlocked=false;const jpWealthLoadRecovery={active:false};let jpWealthLastPersistedRaw=acceptedRaw;const localStorage=storage;',h.context);
  h.context.markJPWealthPersistenceOutcomeUnknown=()=>{control.unknown=true;vm.runInContext('jpWealthPersistenceOutcomeUnknown=true',h.context);};
  const persistence=fs.readFileSync(path.join(root,'src/js/00-core/04-persistence.js'),'utf8');
  const writer=persistence.slice(persistence.indexOf('function jpWealthPersistDocument('),persistence.indexOf('function jpWealthConfirmedStateSnapshot('));
  assert.ok(writer.includes('READBACK_MATCH'),'real writer extraction includes confirmation');vm.runInContext(writer,h.context);
  // The real helper adopts its known raw for the next CAS-style comparison.
  h.context.jpWealthAdoptPersistedRaw=value=>{h.context.nextRaw=value;vm.runInContext('jpWealthLastPersistedRaw=nextRaw',h.context);};
  return h;
}
function execute(h,type,payload,token){return h.api.commands.execute(type,payload,token||h.api.queries.token(payload?.accountId));}
function create(h,changes={}){const r=execute(h,'createAccount',config(changes));assert.equal(r.status,'CONFIRMED',JSON.stringify(r));return r.accountId;}
function ok(h,type,payload){const r=execute(h,type,payload);assert.equal(r.status,'CONFIRMED',JSON.stringify(r));return r;}
const tests=[];const test=(name,run)=>tests.push({name,run});
test('PLSTATE-01 absent aggregate reads empty without writing or creating it',()=>{
  const h=harness({forex:{untouched:true},fxPlanning:{opaque:['legacy']}});
  assert.deepEqual(plain(h.api.queries.snapshot()),{schemaVersion:1,revision:0,accounts:[],archive:[],audit:[],operations:[]});
  h.api.queries.view();h.api.queries.token();assert.equal(h.control.calls.length,0);
  assert.equal('patrimonialPlanning' in h.state(),false);
});
test('PLSTATE-02 create atomically clones full root and adopts only confirmed candidate',()=>{
  const initial={unknown:{keep:['x']},forex:{keep:1},personalFinance:{keep:2},alladin:{keep:3},fxPlanning:{keep:4},dataGovernance:{changeLog:[]}};
  const h=harness(initial);h.control.beforeWrite=()=>assert.deepEqual(h.state(),initial);
  const id=create(h);assert.equal(h.control.calls.length,1);assert.equal(h.control.calls[0].options.expectedEpoch,0);
  assert.equal(h.control.calls[0].options.component,'patrimonialPlanning');
  const saved=h.state();assert.equal(saved.patrimonialPlanning.accounts[0].id,id);
  for(const key of ['unknown','forex','personalFinance','alladin','fxPlanning'])assert.deepEqual(saved[key],initial[key]);
  assert.equal(saved.dataGovernance.changeLog.length,1);assert.equal(saved.patrimonialPlanning.operations.length,1);
  const copy=h.api.queries.account(id);copy.name='mutated';assert.equal(h.api.queries.account(id).name,'Conta sintética');
});
test('PLSTATE-03 refused writer preserves root and invalidates old draft token',()=>{
  const h=harness();const id=create(h);const token=h.api.queries.token(id),before=h.state();h.control.mode='REFUSED';
  assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:10},token).status,'REFUSED');
  assert.deepEqual(h.state(),before);h.control.mode='CONFIRMED';const count=h.control.calls.length;
  assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:10},token).status,'CONFLICT');
  assert.equal(h.control.calls.length,count);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:10});
});
test('PLSTATE-04 unknown and thrown writer preserve root and block retries',()=>{
  for(const mode of ['UNKNOWN','THROW']){const h=harness();const id=create(h),before=h.state();h.control.mode=mode;
    assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:10}).status,'UNKNOWN');
    assert.deepEqual(h.state(),before);const count=h.control.calls.length;h.control.mode='CONFIRMED';
    assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:10}).status,'UNKNOWN');assert.equal(h.control.calls.length,count);}
});
test('PLSTATE-05 revision account plan epoch and root replacement reject stale commands',()=>{
  const h=harness();const a=create(h),b=create(h);const ta=h.api.queries.token(a);
  assert.equal(execute(h,'recordResult',{accountId:b,month:'2026-01',usd:1},ta).status,'CONFLICT');
  const old=h.api.queries.token(a);ok(h,'recordResult',{accountId:a,month:'2026-01',usd:1});
  assert.equal(execute(h,'recordResult',{accountId:a,month:'2026-01',usd:2},old).status,'CONFLICT');
  const epoch=h.api.queries.token(a);h.control.epoch=1;assert.equal(execute(h,'recordResult',{accountId:a,month:'2026-01',usd:3},epoch).status,'CONFLICT');
  const reset=h.api.queries.token(a);h.setState(h.state());assert.equal(execute(h,'recordResult',{accountId:a,month:'2026-01',usd:3},reset).status,'CONFLICT');
});
test('PLSTATE-06 incompatible envelope is preserved and commands blocked',()=>{
  for(const patrimonialPlanning of [{schemaVersion:99,opaque:'future'},{schemaVersion:1,accounts:'broken'}]){
    const h=harness({patrimonialPlanning}),before=h.state();assert.deepEqual(plain(h.api.queries.snapshot()),patrimonialPlanning);
    assert.equal(execute(h,'createAccount',config()).status,'INVALID');assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,0);
  }
});
test('PLSTATE-07 result is absolute USD replacement with version history and negative balance rejection',()=>{
  const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:100});
  ok(h,'recordResult',{accountId:id,month:'2026-01',usd:50});const p=h.api.queries.account(id).plan;
  assert.equal(p.results['2026-01'].usd,50);assert.equal(p.results['2026-01'].previous.usd,100);assert.equal(p.results['2026-01'].revision,2);
  const before=h.state();assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:-1001}).status,'INVALID');assert.deepEqual(h.state(),before);
  const zero=create(h,{initialUsd:0});assert.equal(execute(h,'recordResult',{accountId:zero,month:'2026-01',usd:1}).status,'INVALID');
});
test('PLSTATE-08 multiple contribution withdrawal facts correct by ID and zero annuls',()=>{
  const h=harness(),id=create(h);ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:100,brl:500});
  ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:25,brl:130});
  const first=h.api.queries.account(id).plan.contributions[0];ok(h,'recordContribution',{accountId:id,id:first.id,month:'2026-01',usd:0,brl:0});
  const c=h.api.queries.account(id).plan.contributions;assert.equal(c.length,2);assert.equal(c[0].usd,0);assert.equal(c[0].previous.usd,100);
  ok(h,'recordWithdrawal',{accountId:id,month:'2026-01',usd:10});ok(h,'recordWithdrawal',{accountId:id,month:'2026-01',usd:5,brl:25});
  const before=h.state();for(const payload of [{usd:-10},{usd:1.001},{usd:10,brl:-1}])
    assert.equal(execute(h,'recordWithdrawal',{accountId:id,month:'2026-01',...payload}).status,'INVALID');
  assert.equal(execute(h,'recordContribution',{accountId:id,month:'2026-01',usd:1,brl:0}).status,'INVALID');assert.deepEqual(h.state(),before);
});
test('PLSTATE-09 finalize requires explicit facts and confirmed flows; USD works offline',()=>{
  const h=harness(),id=create(h);assert.equal(execute(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true}).status,'INVALID');
  ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});
  assert.equal(execute(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:false}).status,'INVALID');
  h.context.getCurrentUsdBrlQuote=()=>({rate:null,status:'unavailable'});
  ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
  const a=h.api.queries.account(id);assert.equal(a.plan.closures['2026-01'].confirmed,true);
  assert.equal(h.api.queries.view({accountId:id}).confirmed.balanceUsd,1000);assert.equal(a.plan.contributions.length,0);
});
test('PLSTATE-10 historical correction reopens dependent closures preserves absolute facts and reference',()=>{
  const h=harness(),id=create(h),ref=plain(h.api.queries.account(id).plan.reference);
  ok(h,'recordResult',{accountId:id,month:'2026-01',usd:100});ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:200,brl:1000});
  ok(h,'recordWithdrawal',{accountId:id,month:'2026-01',usd:50});ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
  ok(h,'recordResult',{accountId:id,month:'2026-02',usd:25});ok(h,'finalizeMonth',{accountId:id,month:'2026-02',confirmFlows:true});
  ok(h,'recordResult',{accountId:id,month:'2026-01',usd:150});const p=h.api.queries.account(id).plan;
  assert.equal(p.results['2026-02'].usd,25);assert.equal(p.closures['2026-01'].confirmed,false);assert.equal(p.closures['2026-02'].confirmed,false);
  assert.equal(p.closures['2026-02'].previous.confirmed,true);assert.deepEqual(plain(p.reference),ref);
  const rows=h.api.queries.view({accountId:id}).rows;assert.equal(rows[0].closeUsd,1300);assert.equal(rows[1].closeUsd,1325);
  assert.equal(h.api.queries.view({accountId:id}).confirmed.balanceUsd,null);
});
test('PLSTATE-11 known operation replay returns confirmed once while arbitrary IDs cannot replay',()=>{
  const h=harness(),id=create(h),token=h.api.queries.token(id),payload={accountId:id,month:'2026-01',usd:10};
  const result=execute(h,'recordResult',payload,token);assert.equal(result.status,'CONFIRMED');assert.ok(result.operationId);
  const count=h.control.calls.length;const replay=execute(h,'recordResult',{...payload,operationId:result.operationId},token);
  assert.equal(replay.status,'CONFIRMED');assert.equal(replay.operationId,result.operationId);assert.equal(h.control.calls.length,count);
  assert.equal(execute(h,'recordResult',{...payload,usd:11,operationId:result.operationId},token).status,'CONFLICT');
  assert.equal(execute(h,'recordResult',{...payload,operationId:'invented'}).status,'INVALID');assert.equal(h.control.calls.length,count);
});
test('PLSTATE-12 dedicated reset archives complete prior plan before atomic replacement and changes identity',()=>{
  const h=harness(),id=create(h),prior=h.api.queries.account(id).plan;ok(h,'recordResult',{accountId:id,month:'2026-01',usd:10});
  assert.equal(execute(h,'restartPlan',{accountId:id,config:config({initialUsd:2000}),confirmation:false}).status,'INVALID');
  // Native Reinicio.gs184–191 requires the dedicated archive/reset before a
  // form can change the start or capital of a plan which already has facts.
  assert.equal(execute(h,'restartPlan',{accountId:id,config:config({initialUsd:2000}),confirmation:true}).status,'INVALID');
  const r=ok(h,'resetAccount',{accountId:id,confirmation:h.api.queries.previewReset({accountId:id}).phrase});
  ok(h,'updateAccount',{accountId:id,config:config({initialUsd:2000})});
  const e=h.api.queries.snapshot();assert.notEqual(r.planId,prior.id);assert.equal(e.archive.length,1);
  assert.equal(e.archive[0].accountId,id);assert.equal(e.archive[0].plan.id,prior.id);assert.equal(e.archive[0].plan.results['2026-01'].usd,10);
  assert.equal(e.accounts[0].plan.initialUsd,2000);assert.equal(h.control.calls.at(-1).candidate.patrimonialPlanning.archive.length,1);
});
test('PLSTATE-13 projection stop and metadata update preserve original reference and confirmed facts',()=>{
  const h=harness(),id=create(h),ref=plain(h.api.queries.account(id).plan.reference);
  ok(h,'setProjection',{accountId:id,month:'2026-11',rate:0.04,contributionUsd:250});
  assert.equal(execute(h,'setProjection',{accountId:id,month:'2026-01',rate:0.04,contributionUsd:250}).status,'INVALID');
  ok(h,'applyStop',{accountId:id,stopAfter:'2026-12',impactLimit:1});
  ok(h,'updateAccount',{accountId:id,config:{name:'Renomeada'},replaceFuture:false});
  assert.equal(h.api.queries.view({accountId:id}).rows.find(r=>r.month==='2027-01').contributionUsd,0);
  ok(h,'updateAccount',{accountId:id,config:config({name:'Renomeada',monthlyContributionUsd:300}),replaceFuture:true});
  const p=h.api.queries.account(id).plan;assert.deepEqual(plain(p.reference),ref);assert.equal(h.api.queries.account(id).name,'Renomeada');
  assert.equal(p.startMonth,'2026-01');assert.equal(p.initialUsd,1000);
  // Explicit Reaplicar replaces editable future cells, including zeros from a
  // prior stop; ParadaAportes.gs82–89 and Projecoes.gs36–46 preserve that choice.
  const rows=h.api.queries.view({accountId:id}).rows;assert.equal(rows.find(r=>r.month==='2027-01').contributionUsd,300);
});
test('PLSTATE-14 BRL goal captures valid public reference and remains fixed',()=>{
  const h=harness(),id=create(h,{goals:{adequate:null,ideal:{value:10000,currency:'BRL'}}});
  const goal=h.api.queries.account(id).plan.goals.ideal;assert.equal(goal.usd,2000);assert.equal(goal.quote.rate,5);
  h.context.getCurrentUsdBrlQuote=()=>({...quote,rate:10});assert.equal(h.api.queries.account(id).plan.goals.ideal.usd,2000);
  h.context.getCurrentUsdBrlQuote=()=>({rate:5,status:'unavailable'});
  assert.equal(execute(h,'createAccount',config({goals:{adequate:null,ideal:{value:100,currency:'BRL'}}})).status,'INVALID');
});
test('PLSTATE-15 export-only legacy strips nested secrets and preserves unknown shapes',()=>{
  const legacy={schemaVersion:99,opaque:{keep:[1,'<img src=x>'],password:'synthetic',nested:[{investorPassword:'synthetic',token:'synthetic',custom:4}]}};
  const h=harness({fxPlanning:legacy});const x=plain(h.api.queries.legacy());assert.equal(x.source,'S.fxPlanning');assert.equal(x.exportOnly,true);
  assert.equal(x.value.opaque.nested[0].custom,4);assert.equal('password' in x.value.opaque,false);assert.equal('token' in x.value.opaque.nested[0],false);
  assert.deepEqual(h.state().fxPlanning,legacy);assert.equal(h.control.calls.length,0);
  assert.equal(execute(h,'createAccount',{...config(),password:'synthetic'}).status,'INVALID');
});
test('PLSTATE-16 archive explicit and read-only history keeps plan available without further financial edits',()=>{
  const h=harness(),id=create(h);assert.equal(execute(h,'archiveAccount',{accountId:id,confirmation:false}).status,'INVALID');
  ok(h,'archiveAccount',{accountId:id,confirmation:true});assert.equal(h.api.queries.account(id).active,false);
  assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:1}).status,'INVALID');
  assert.ok(h.api.queries.history(id).history.length);assert.equal(h.api.queries.view().accounts.length,0);
});
test('PLSTATE-17 real confirmed writer verifies synthetic storage and quota refuses before adoption',()=>{
  const initial={dataGovernance:{changeLog:[]},foreignExtension:{keep:true}};
  const h=realWriterHarness(initial);const id=create(h);assert.equal(h.context.storage.sets,1);
  assert.deepEqual(JSON.parse(h.context.storage.raw),h.state());assert.equal(h.state().patrimonialPlanning.accounts[0].id,id);
  const before=h.state(),raw=h.context.storage.raw;h.context.storage.mode='quota';
  assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:10}).status,'REFUSED');
  assert.deepEqual(h.state(),before);assert.equal(h.context.storage.raw,raw);
});
test('PLSTATE-18 real writer unknown after physical write retains old memory and vetoes retry',()=>{
  const h=realWriterHarness();h.context.storage.mode='read-after';const prior=h.state();
  const r=execute(h,'createAccount',config());assert.equal(r.status,'UNKNOWN');assert.equal(h.context.storage.sets,1);
  assert.equal(JSON.parse(h.context.storage.raw).patrimonialPlanning.accounts.length,1);assert.deepEqual(h.state(),prior);
  h.context.storage.mode='normal';assert.equal(execute(h,'createAccount',config()).status,'UNKNOWN');assert.equal(h.context.storage.sets,1);
});
test('PLSTATE-19 real writer refuses another tab state without changing disk memory or facts',()=>{
  const h=realWriterHarness();const id=create(h),before=h.state();h.context.storage.raw=JSON.stringify({anotherTab:'preserve'});
  const token=h.api.queries.token(id);assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:1},token).status,'CONFLICT');
  assert.equal(h.context.storage.sets,1);assert.equal(h.context.storage.raw,JSON.stringify({anotherTab:'preserve'}));assert.deepEqual(h.state(),before);
});
test('PLSTATE-20 correction that invalidates dependent month is rejected atomically',()=>{
  const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:100});
  ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:1000,brl:5000});const flow=h.api.queries.account(id).plan.contributions[0];
  ok(h,'recordWithdrawal',{accountId:id,month:'2026-01',usd:1500});ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
  ok(h,'recordResult',{accountId:id,month:'2026-02',usd:0});ok(h,'recordWithdrawal',{accountId:id,month:'2026-02',usd:500});
  ok(h,'finalizeMonth',{accountId:id,month:'2026-02',confirmFlows:true});const before=h.state(),count=h.control.calls.length;
  assert.equal(execute(h,'recordContribution',{accountId:id,id:flow.id,month:'2026-01',usd:500,brl:2500}).status,'INVALID');
  assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,count);
});
test('PLSTATE-21 finalized exchange snapshot survives current quote changes and read current month is explicit',()=>{
  const h=harness();h.context.JPWMarket={usdBrl:{getHistorical:()=>({...quote,referenceDate:'2026-01-30'})}};
  const id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
  h.context.getCurrentUsdBrlQuote=()=>({...quote,rate:10});const rows=h.api.queries.view({accountId:id}).rows;
  assert.equal(rows[0].closeBrl,5000);assert.equal(rows.find(row=>row.month==='2026-10').phase,'current');
  assert.equal(rows.find(row=>row.month==='2026-09').contributionUsd,0);
});
test('PLSTATE-23 historical closure never snapshots present quote or invents historical BRL',()=>{
  const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});
  ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
  assert.equal(h.api.queries.account(id).plan.closures['2026-01'].fxQuote,undefined);
  assert.equal(h.api.queries.view({accountId:id}).rows[0].closeBrl,null);
  const future=harness();future.context.JPWMarket={usdBrl:{getHistorical:()=>({...quote,referenceDate:'2026-02-02'})}};
  const other=create(future);ok(future,'recordResult',{accountId:other,month:'2026-01',usd:0});
  ok(future,'finalizeMonth',{accountId:other,month:'2026-01',confirmFlows:true});
  assert.equal(future.api.queries.account(other).plan.closures['2026-01'].fxQuote,undefined);
});
test('PLSTATE-22 roundtrip reload preserves extensions histories archive and idempotency references',()=>{
  const h=harness({unrelated:{text:'synthetic extension'}}),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:10});
  ok(h,'resetAccount',{accountId:id,confirmation:h.api.queries.previewReset({accountId:id}).phrase});
  ok(h,'updateAccount',{accountId:id,config:config({initialUsd:2000})});const saved=h.state();
  saved.patrimonialPlanning.extension={opaque:[1,'keep']};saved.patrimonialPlanning.accounts[0].extension='keep';
  const reloaded=harness(saved);assert.deepEqual(reloaded.state(),saved);const snapshot=plain(reloaded.api.queries.snapshot());
  assert.deepEqual(snapshot.extension,{opaque:[1,'keep']});assert.equal(snapshot.archive[0].plan.results['2026-01'].usd,10);
  const copy=plain(snapshot);copy.archive[0].plan.results['2026-01'].usd=99;assert.equal(reloaded.api.queries.history(id).archive[0].plan.results['2026-01'].usd,10);
});
test('PLSTATE-24 known restart replay uses original token and cannot replay after another restart',()=>{
  const h=harness(),id=create(h),token=h.api.queries.token(id),payload={accountId:id,config:config({initialUsd:2000}),confirmation:true};
  const first=execute(h,'restartPlan',payload,token);assert.equal(first.status,'CONFIRMED');const count=h.control.calls.length;
  const repeated=execute(h,'restartPlan',{...payload,operationId:first.operationId},token);
  assert.equal(repeated.status,'CONFIRMED');assert.equal(repeated.planId,first.planId);assert.equal(h.control.calls.length,count);
  ok(h,'restartPlan',{accountId:id,config:config({initialUsd:3000}),confirmation:true});
  assert.equal(execute(h,'restartPlan',{...payload,operationId:first.operationId},token).status,'CONFLICT');
});
test('PLSTATE-25 nonserializable malformed input returns INVALID without throwing or writing',()=>{
  const h=harness(),before=h.state();let result;
  assert.doesNotThrow(()=>{result=execute(h,'createAccount',{...config(),name:()=>{}});});
  assert.equal(result.status,'INVALID');assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,0);
});
test('PLSTATE-26 explicit reopen keeps USD facts and reopens dependent months with reason',()=>{
  const h=harness(),id=create(h);for(const month of ['2026-01','2026-02']){
    ok(h,'recordResult',{accountId:id,month,usd:10});ok(h,'finalizeMonth',{accountId:id,month,confirmFlows:true});
  }
  const facts=plain(h.api.queries.account(id).plan.results),before=h.state();
  assert.equal(execute(h,'reopenMonth',{accountId:id,month:'2026-01',reason:' '}).status,'INVALID');assert.deepEqual(h.state(),before);
  ok(h,'reopenMonth',{accountId:id,month:'2026-01',reason:'Conferência sintética'});const p=h.api.queries.account(id).plan;
  assert.deepEqual(plain(p.results),facts);assert.equal(p.closures['2026-01'].confirmed,false);assert.equal(p.closures['2026-02'].confirmed,false);
  assert.equal(p.closures['2026-02'].reason,'Conferência sintética');
  ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});assert.equal(h.api.queries.account(id).plan.closures['2026-01'].previous.previous.confirmed,true);
});
test('PLSTATE-27 real writer load workspace and session gates refuse before physical write',()=>{
  for(const mode of ['load','workspace','blocked']){
    const h=realWriterHarness(mode==='workspace'?{workspaceRecovery:{pending:true}}:{}),before=h.state();
    if(mode==='load')vm.runInContext('jpWealthLoadRecovery.active=true',h.context);
    if(mode==='blocked')vm.runInContext('jpWealthPersistenceBlocked=true',h.context);
    assert.equal(execute(h,'createAccount',config()).status,'REFUSED');assert.equal(h.context.storage.sets,0);assert.deepEqual(h.state(),before);
  }
});
test('PLSTATE-28 cannot adopt adjacent unconfirmed RAM through a planning command',()=>{
 const h=realWriterHarness({forex:{record:1},personalFinance:{record:1},alladin:{record:1}});
 h.context.jpWealthConfirmedStateSnapshot=()=>JSON.parse(h.context.nextRaw||h.context.acceptedRaw);
 const id=create(h),beforeSets=h.context.storage.sets;
 vm.runInContext('S.forex.record=2;S.personalFinance.record=3;S.alladin.record=4;',h.context);
 const before=h.state();const r=execute(h,'recordResult',{accountId:id,month:'2026-01',usd:20});
 assert.equal(r.status,'CONFLICT');assert.equal(h.context.storage.sets,beforeSets);assert.deepEqual(h.state(),before);
 const disk=JSON.parse(h.context.storage.raw);assert.equal(disk.forex.record,1);assert.equal(disk.personalFinance.record,1);assert.equal(disk.alladin.record,1);
});
test('PLSTATE-29 current closure snapshot contains effective flows, never forecast contribution',()=>{
 const h=harness();const id=create(h,{startMonth:'2026-10',monthlyContributionUsd:100});
 assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-10',usd:30}).ok,true);
 assert.equal(h.api.queries.view({accountId:id}).rows[0].contributionUsd,100);
 assert.equal(execute(h,'finalizeMonth',{accountId:id,month:'2026-10',confirmFlows:true}).ok,true);
 const closure=h.api.queries.account(id).plan.closures['2026-10'];
 assert.equal(closure.snapshot.contributionUsd,0);assert.equal(closure.snapshot.closeUsd,1030);assert.equal(h.api.queries.view({accountId:id}).confirmed.balanceUsd,1030);
});
test('PLSTATE-30 edit preview uses same preserved account candidate without writes',()=>{
 const h=harness();const id=create(h);execute(h,'recordResult',{accountId:id,month:'2026-01',usd:-500});
 execute(h,'setProjection',{accountId:id,month:'2026-11',rate:0,contributionUsd:88});execute(h,'applyStop',{accountId:id,stopAfter:'2026-11',impactLimit:1});
 const before=h.state(),calls=h.control.calls.length;
 const p=h.api.queries.previewAccount({accountId:id,config:{name:'Preview rename'}});
 assert.equal(p.ok,true,JSON.stringify(p));assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);
 assert.equal(execute(h,'updateAccount',{accountId:id,config:{name:'Preview rename'}}).ok,true);
 assert.deepEqual(plain(p.model.rows),plain(h.api.queries.view({accountId:id}).rows));
});
test('PLSTATE-31 new BRL goals require a recent consultation, USD remains offline',()=>{
 const h=harness();h.context.getCurrentUsdBrlQuote=()=>({...quote,referenceDate:'2026-10-17',fetchedAt:'2026-10-18T12:00:00.000Z'});
 const before=h.state();const r=execute(h,'createAccount',config({goals:{adequate:null,ideal:{value:1000,currency:'BRL'}}}));
 assert.equal(r.status,'INVALID');assert.equal(h.control.calls.length,0);assert.deepEqual(h.state(),before);
 assert.equal(execute(h,'createAccount',config()).ok,true);
});
test('PLSTATE-32 first planning write cannot confirm adjacent RAM before any saved base',()=>{
 const h=realWriterHarness({forex:{record:1}});h.context.storage.raw=null;h.context.acceptedRaw=null;
 vm.runInContext('jpWealthLastPersistedRaw=null;S.forex.record=2;',h.context);h.context.jpWealthConfirmedStateSnapshot=()=>null;
 assert.equal(execute(h,'createAccount',config()).status,'CONFLICT');assert.equal(h.context.storage.sets,0);assert.equal(h.state().forex.record,2);
});
test('PLSTATE-33 confirmed base adoption releases local unknown while invalidating old tokens',()=>{
 const h=realWriterHarness({});h.context.jpWealthConfirmedStateSnapshot=()=>JSON.parse(h.context.nextRaw||h.context.acceptedRaw);
 const id=create(h),old=h.api.queries.token(id);h.context.storage.sets=0;h.context.storage.mode='read-after';
 assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:50}).status,'UNKNOWN');
 const restored=JSON.parse(h.context.nextRaw||h.context.acceptedRaw);h.setState(restored);h.context.storage.raw=JSON.stringify(restored);h.context.storage.mode='normal';
 h.control.unknown=false;vm.runInContext('jpWealthPersistenceOutcomeUnknown=false;jpWealthLastPersistedRaw=storage.raw;',h.context);
 assert.equal(h.api.commands.resetContext(),true);
 assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:50},old).status,'CONFLICT');
 assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:50}).ok,true);
});
test('PLSTATE-34 ordinary boot context check preserves a live planning token',()=>{
 const h=realWriterHarness({});h.context.jpWealthConfirmedStateSnapshot=()=>JSON.parse(h.context.nextRaw||h.context.acceptedRaw);
 const id=create(h),token=h.api.queries.token(id);assert.equal(h.api.commands.resetContext(),false);
 assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:25},token).ok,true);
});
test('PLSTATE-35 empty ordinary boot cannot bless adjacent unsaved RAM',()=>{
 const h=realWriterHarness({forex:{record:1}});h.context.storage.raw=null;h.context.acceptedRaw=null;h.context.jpWealthConfirmedStateSnapshot=()=>null;
 vm.runInContext('jpWealthLastPersistedRaw=null;S.forex.record=2;',h.context);
 assert.equal(h.api.commands.resetContext(),false);assert.equal(execute(h,'createAccount',config()).status,'CONFLICT');assert.equal(h.context.storage.sets,0);
});
test('PLSTATE-36 verified exact empty defaults can be adopted after remote wipe',()=>{
 const h=realWriterHarness({forex:{record:1}});create(h);h.context.DEFAULTS={forex:{record:0}};
 h.context.storage.raw=null;h.context.acceptedRaw=null;h.context.nextRaw=null;h.context.jpWealthConfirmedStateSnapshot=()=>null;
 vm.runInContext('jpWealthLastPersistedRaw=null;',h.context);h.setState({forex:{record:0}});
 assert.equal(h.api.commands.resetContext(),true);assert.equal(execute(h,'createAccount',config()).ok,true);
});
test('PLSTATE-37 contribution stop refuses retroactive dates and impact over the reviewed limit without writing',()=>{
 const h=harness(),id=create(h),before=h.state(),count=h.control.calls.length;
 assert.equal(execute(h,'applyStop',{accountId:id,stopAfter:'2026-09',impactLimit:1}).status,'INVALID');
 assert.equal(execute(h,'applyStop',{accountId:id,stopAfter:'2026-10',impactLimit:0}).status,'INVALID');
 assert.equal(execute(h,'applyStop',{accountId:id,stopAfter:'2026-10'}).status,'INVALID');
 assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,count);
});
test('PLSTATE-38 first permitted stop applies exactly the simulated cashflows and keeps factual records and reference',()=>{
 const h=harness(),id=create(h);ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:75,brl:375});
 ok(h,'recordResult',{accountId:id,month:'2026-01',usd:25});ok(h,'setProjection',{accountId:id,month:'2026-12',rate:.04,contributionUsd:350});
 const before=h.api.queries.account(id).plan,found=h.api.engine.findContributionStop(before,{month:'2026-10',quote,impactLimit:.05});assert.ok(found);
 assert.equal(found.result.withinImpactLimit,true);ok(h,'applyStop',{accountId:id,stopAfter:found.stopAfter,impactLimit:.05});
 const after=h.api.queries.account(id).plan,rows=h.api.queries.view({accountId:id}).rows;
 assert.deepEqual(plain(rows),plain(found.result.rows));
 for(const key of ['reference','results','contributions','withdrawals','closures'])assert.deepEqual(plain(after[key]),plain(before[key]));
});
test('PLSTATE-39 stop materializes future zeroes and allows later deliberate projection edits',()=>{
 const h=harness(),id=create(h);ok(h,'setProjection',{accountId:id,month:'2026-12',rate:.04,contributionUsd:350});
 ok(h,'applyStop',{accountId:id,stopAfter:'2026-10',impactLimit:1});
 assert.equal(h.api.queries.account(id).plan.future['2026-12'].contributionUsd,0);
 assert.equal(h.api.queries.account(id).plan.future['2026-12'].rate,.04);
 ok(h,'setProjection',{accountId:id,month:'2026-12',rate:.04,contributionUsd:50});
 assert.equal(h.api.queries.view({accountId:id}).rows.find(r=>r.month==='2026-12').contributionUsd,50);
 ok(h,'applyStop',{accountId:id,stopAfter:'2026-11',impactLimit:1});
 assert.equal(h.api.queries.view({accountId:id}).rows.find(r=>r.month==='2026-12').contributionUsd,0);
});
// Native-source parity: Formulario.verified.gs:353–422, Reinicio.gs:6–48/131–149,
// Saques.gs:63–79. These cases exercise commands and the actual confirmed writer;
// native Google permissions/queue execution are intentionally outside this host.
test('PLSTATE-40 monthly flow preview uses the confirmed candidate rules without writing',()=>{
 const h=harness(),id=create(h),before=h.state(),count=h.control.calls.length;
 assert.equal(typeof h.api.queries.previewFlow,'function');
 const result=h.api.queries.previewFlow({accountId:id,month:'2026-01',kind:'result',usd:50});
 assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.rate,.05);assert.equal(result.row.resultUsd,50);
 const aporte=h.api.queries.previewFlow({accountId:id,month:'2026-01',kind:'contribution',usd:100,brl:510});
 assert.equal(aporte.ok,true);assert.equal(aporte.monthTotalUsd,100);assert.equal(aporte.paidRate,5.1);
 assert.equal(h.api.queries.previewFlow({accountId:id,month:'2026-01',kind:'withdrawal',usd:2000}).ok,false);
 assert.equal(h.api.queries.previewFlow({accountId:id,month:'2026-11',kind:'result',usd:1}).ok,false);
 assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,count);
 ok(h,'recordResult',{accountId:id,month:'2026-01',usd:50});
 assert.deepEqual(plain(result.row),plain(h.api.queries.view({accountId:id}).rows[0]));
});
test('PLSTATE-41 native form accepts independent positive goals and optional display name',()=>{
 const h=harness();const id=create(h,{name:'',goals:{adequate:{value:6000,currency:'USD'},ideal:{value:5000,currency:'USD'}}});
 assert.equal(h.api.queries.account(id).name,'Conta de investimento');
 assert.equal(h.api.queries.account(id).plan.goals.adequate.usd,6000);
 assert.equal(h.api.queries.account(id).plan.goals.ideal.usd,5000);
});
test('PLSTATE-42 native form allows fractional-cent premises while factual ledgers remain cents',()=>{
 const h=harness(),id=create(h,{initialUsd:1000.123,monthlyContributionUsd:200.456,goals:{adequate:null,ideal:{value:5000.123,currency:'USD'}}});
 const p=h.api.queries.account(id).plan;assert.equal(p.initialUsd,1000.123);assert.equal(p.monthlyContributionUsd,200.456);assert.equal(p.goals.ideal.usd,5000.12);
 const before=h.state();assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:1.001}).status,'INVALID');assert.deepEqual(h.state(),before);
});
test('PLSTATE-43 account reset previews counts and archives every fact before reapplying premises',()=>{
 const h=realWriterHarness({unrelated:{preserve:1}}),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:50});
 ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:100,brl:510});ok(h,'recordWithdrawal',{accountId:id,month:'2026-01',usd:20});
 ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});ok(h,'setProjection',{accountId:id,month:'2026-11',rate:.04,contributionUsd:300});
 const prior=plain(h.api.queries.account(id)),before=h.state(),sets=h.context.storage.sets;
 assert.equal(typeof h.api.queries.previewReset,'function');const preview=h.api.queries.previewReset({accountId:id,scope:'CONTA'});
 assert.equal(preview.ok,true);assert.equal(preview.phrase,'REINICIAR C001');assert.deepEqual(plain(preview.counts),{closed:1,contributions:1,results:1,withdrawals:1});
 assert.deepEqual(h.state(),before);assert.equal(h.context.storage.sets,sets);
 assert.equal(execute(h,'resetAccount',{accountId:id,confirmation:'REINICIAR'}).status,'INVALID');assert.equal(h.context.storage.sets,sets);
 const reset=ok(h,'resetAccount',{accountId:id,confirmation:preview.phrase});const after=h.api.queries.account(id),archive=h.api.queries.snapshot().archive;
 assert.notEqual(after.plan.id,prior.plan.id);assert.equal(reset.accountId,id);assert.equal(after.name,prior.name);
 assert.deepEqual(plain(archive.at(-1).plan),prior.plan);assert.equal(archive.at(-1).resetScope,'CONTA');
 assert.deepEqual(plain(after.plan.results),{});assert.deepEqual(plain(after.plan.contributions),[]);assert.deepEqual(plain(after.plan.withdrawals),[]);assert.deepEqual(plain(after.plan.closures),{});
 for(const k of ['startMonth','initialUsd','profileId','monthlyContributionUsd','goals'])assert.deepEqual(plain(after.plan[k]),prior.plan[k]);
 assert.deepEqual(plain(after.plan.reference.rows),prior.plan.reference.rows);assert.equal(after.plan.reference.createdAt,prior.plan.reference.createdAt);
 assert.equal(h.api.queries.view({accountId:id}).rows.find(r=>r.month==='2026-11').contributionUsd,200);
 assert.equal(h.context.storage.sets,sets+1);assert.deepEqual(JSON.parse(h.context.storage.raw),h.state());assert.deepEqual(h.state().unrelated,{preserve:1});
});
test('PLSTATE-44 reset all archives all active accounts and reuses the primary identity after configuration',()=>{
 const h=realWriterHarness(),a=create(h),b=create(h,{name:'Segunda sintética'});ok(h,'recordResult',{accountId:a,month:'2026-01',usd:10});ok(h,'recordContribution',{accountId:b,month:'2026-01',usd:50,brl:250});
 const before=h.api.queries.snapshot(),preview=h.api.queries.previewReset({accountId:b,scope:'TODAS'});assert.equal(preview.ok,true);assert.equal(preview.phrase,'REINICIAR TUDO');assert.equal(preview.targets.length,2);
 const r=ok(h,'resetAll',{accountId:b,confirmation:preview.phrase});assert.equal(r.requiresConfiguration,true);assert.equal(r.accountId,a);
 const pending=h.api.queries.snapshot();assert.equal(pending.accounts.filter(x=>x.active).length,0);assert.equal(pending.archive.length,2);
 for(const prior of before.accounts)assert.deepEqual(plain(pending.archive.find(x=>x.accountId===prior.id).plan),plain(prior.plan));
 const saved=h.state(),reload=realWriterHarness(saved);assert.equal(reload.api.queries.view().accounts.length,0);
 const id=create(reload,{name:'Novo plano sintético',startMonth:'2026-10',initialUsd:0});assert.equal(id,a);
 assert.equal(reload.api.queries.account(a).active,true);assert.equal(reload.api.queries.account(b).active,false);assert.equal(reload.api.queries.snapshot().archive.length,2);
 assert.notEqual(reload.api.queries.account(a).plan.id,before.accounts[0].plan.id);assert.deepEqual(plain(reload.api.queries.account(a).plan.results),{});
});
test('PLSTATE-45 reset uses fresh account token and replay cannot write twice or cross plans',()=>{
 const h=harness(),id=create(h),token=h.api.queries.token(id),payload={accountId:id,confirmation:'REINICIAR C001'};
 const first=execute(h,'resetAccount',payload,token);assert.equal(first.ok,true,JSON.stringify(first));const count=h.control.calls.length;
 const repeat=execute(h,'resetAccount',{...payload,operationId:first.operationId},token);assert.equal(repeat.ok,true);assert.equal(h.control.calls.length,count);
 assert.equal(execute(h,'resetAccount',payload,token).status,'CONFLICT');
 ok(h,'resetAccount',payload);assert.equal(execute(h,'resetAccount',{...payload,operationId:first.operationId},token).status,'CONFLICT');
});
test('PLSTATE-46 reset refuses or unknown preserve live facts and prohibit repeated physical writes',()=>{
 for(const mode of ['REFUSED','UNKNOWN']){
  const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:10});const before=h.state();h.control.mode=mode;
  const result=execute(h,'resetAccount',{accountId:id,confirmation:'REINICIAR C001'});assert.equal(result.status,mode);assert.deepEqual(h.state(),before);
  if(mode==='UNKNOWN'){const count=h.control.calls.length;h.control.mode='CONFIRMED';assert.equal(execute(h,'resetAccount',{accountId:id,confirmation:'REINICIAR C001'}).status,'UNKNOWN');assert.equal(h.control.calls.length,count);}
 }
});
test('PLSTATE-47 native start and capital changes require reset when any factual record exists',()=>{
 for(const type of ['recordResult','recordContribution','recordWithdrawal']){
  const h=harness(),id=create(h);ok(h,type,{accountId:id,month:'2026-01',usd:10,...(type==='recordContribution'?{brl:50}:{})});const before=h.state(),calls=h.control.calls.length;
  assert.equal(execute(h,'updateAccount',{accountId:id,config:{initialUsd:2000}}).status,'INVALID');
  assert.equal(execute(h,'updateAccount',{accountId:id,config:{startMonth:'2026-02'}}).status,'INVALID');
  assert.equal(execute(h,'restartPlan',{accountId:id,config:config(),confirmation:true}).status,'INVALID');assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);
 }
});
test('PLSTATE-48 reset all replay is idempotent until primary configuration changes the plan',()=>{
 const h=realWriterHarness(),a=create(h),b=create(h),token=h.api.queries.token(b),payload={accountId:b,confirmation:'REINICIAR TUDO'};
 const first=execute(h,'resetAll',payload,token);assert.equal(first.ok,true);const count=h.context.storage.sets;
 assert.equal(execute(h,'resetAll',{...payload,operationId:first.operationId},token).ok,true);assert.equal(h.context.storage.sets,count);
 assert.equal(execute(h,'resetAll',payload,token).status,'CONFLICT');assert.equal(h.context.storage.sets,count);
 assert.equal(create(h,{startMonth:'2026-10'}),a);
 assert.equal(execute(h,'resetAll',{...payload,operationId:first.operationId},token).status,'CONFLICT');
});
test('PLSTATE-49 native flow correction stays in its original month and preview equals corrected ledger sum',()=>{
 const h=harness(),id=create(h);ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:100,brl:500});ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:50,brl:255});
 const first=h.api.queries.account(id).plan.contributions[0],before=h.state(),calls=h.control.calls.length;
 assert.equal(h.api.queries.previewFlow({accountId:id,month:'2026-02',kind:'contribution',id:first.id,usd:75,brl:375}).ok,false);
 assert.equal(execute(h,'recordContribution',{accountId:id,month:'2026-02',id:first.id,usd:75,brl:375}).status,'INVALID');assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);
 const input={accountId:id,month:'2026-01',id:first.id,usd:75,brl:375},preview=h.api.queries.previewFlow({...input,kind:'contribution'});
 assert.equal(preview.ok,true);assert.equal(preview.monthTotalUsd,125);assert.equal(preview.paidRate,5);ok(h,'recordContribution',input);
 assert.equal(h.api.queries.view({accountId:id}).rows[0].contributionUsd,preview.monthTotalUsd);
});
test('PLSTATE-50 reset preserves opaque extensions and uses current income goals with the original financial reference',()=>{
 const h=harness(),id=create(h),document=h.state();document.patrimonialPlanning.accounts[0].extension={preserve:'account'};document.patrimonialPlanning.accounts[0].plan.extension={preserve:'plan'};h.setState(document);
 ok(h,'updateAccount',{accountId:id,config:{goals:{adequate:{value:7000,currency:'USD'},ideal:{value:4000,currency:'USD'}}}});
 const before=h.api.queries.account(id),reference=plain(before.plan.reference);ok(h,'resetAccount',{accountId:id,confirmation:'REINICIAR C001'});
 const after=h.api.queries.account(id),archived=h.api.queries.snapshot().archive.at(-1);
 assert.deepEqual(plain(archived.account.extension),{preserve:'account'});assert.deepEqual(plain(archived.plan.extension),{preserve:'plan'});
 assert.deepEqual(plain(after.extension),{preserve:'account'});assert.deepEqual(plain(after.plan.reference.rows),reference.rows);
 assert.deepEqual(plain(after.plan.reference.config),reference.config);assert.deepEqual(plain(after.plan.incomeBaselineGoals),plain(before.plan.goals));
 const model=h.api.queries.view({accountId:id});assert.equal(model.goals.ideal.initialUsd,4000);assert.equal(model.goals.ideal.goalChanged,false);
});
test('PLSTATE-51 projected cell accepts native fractional-cent entries while future facts remain forbidden',()=>{
 const h=harness(),id=create(h);ok(h,'setProjection',{accountId:id,month:'2026-11',rate:.01234,contributionUsd:123.4567});
 const p=h.api.queries.account(id).plan;assert.equal(p.future['2026-11'].contributionUsd,123.4567);
 assert.equal(h.api.queries.view({accountId:id}).rows.find(row=>row.month==='2026-11').contributionUsd,123.4567);
 const before=h.state();assert.equal(execute(h,'recordContribution',{accountId:id,month:'2026-11',usd:123.4567,brl:600}).status,'INVALID');assert.deepEqual(h.state(),before);
});
test('PLSTATE-52 first form can stop before a past-start plan while later edits cannot alter past contributions',()=>{
 const h=harness(),id=create(h,{stopAfter:'2025-12',stopImpactLimit:1}),p=h.api.queries.account(id).plan;
 assert.equal(p.stopAfter,'2025-12');assert.equal(p.future['2026-01'].contributionUsd,0);assert.equal(p.future['2026-10'].contributionUsd,0);
 assert.equal(p.reference.rows[0].contributionUsd,200);assert.equal(h.api.queries.view({accountId:id}).rows.find(row=>row.month==='2026-10').contributionUsd,0);
 const before=h.state();assert.equal(execute(h,'updateAccount',{accountId:id,config:{stopAfter:'2026-09',stopImpactLimit:1}}).status,'INVALID');assert.deepEqual(h.state(),before);
});
test('PLSTATE-53 explicit FX refresh reconverts only the requested unchanged BRL goal',()=>{
 const h=harness(),id=create(h,{goals:{adequate:{value:5000,currency:'BRL'},ideal:{value:10000,currency:'BRL'}}});
 const before=h.api.queries.account(id).plan.goals,nextQuote={...quote,rate:10};h.context.getCurrentUsdBrlQuote=()=>nextQuote;
 ok(h,'updateAccount',{accountId:id,config:{name:'No refresh'}});
 assert.equal(h.api.queries.account(id).plan.goals.ideal.usd,2000);
 ok(h,'updateAccount',{accountId:id,config:{goals:{adequate:plain(before.adequate),ideal:{value:10000,currency:'BRL',quote:nextQuote,refreshQuote:true}}}});
 const after=h.api.queries.account(id).plan.goals;assert.equal(after.ideal.usd,1000);assert.equal(after.ideal.quote.rate,10);
 assert.deepEqual(plain(after.adequate),plain(before.adequate));assert.equal(after.ideal.refreshQuote,undefined);
});
test('PLSTATE-54 quote changing after review is refused before a financial write',()=>{
 const h=harness(),id=create(h),before=h.state(),calls=h.control.calls.length;
 const reviewed={...quote,rate:5};h.context.getCurrentUsdBrlQuote=()=>({...quote,rate:10});
 const r=execute(h,'updateAccount',{accountId:id,config:{goals:{adequate:null,ideal:{value:10000,currency:'BRL',quote:reviewed,refreshQuote:true}}}});
 assert.equal(r.status,'INVALID');assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);
});

// Approved22/10/2026 closure diagnostics: additive read-only contract.
test('PLCLOSE-Q01 missing fact reports structured month without financial writes',()=>{
 const h=harness(),id=create(h),before=h.state(),calls=h.control.calls.length;
 const r=h.api.queries.previewFinalizeMonth({accountId:id,month:'2026-01'});
 assert.equal(r.ok,false);assert.equal(r.status,'INVALID');
 assert.ok(r.blockers.some(x=>x.code==='MISSING_RESULT'&&x.month==='2026-01'));
 assert.match(r.errors.join(' '),/resultado total/);assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);
 r.blockers[0].month='2099-01';assert.equal(h.api.queries.previewFinalizeMonth({accountId:id,month:'2026-01'}).blockers[0].month,'2026-01');
});
test('PLCLOSE-Q02 earliest previous unconfirmed month is explicit even with missing current result',()=>{
 const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
 const before=h.state(),r=h.api.queries.previewFinalizeMonth({accountId:id,month:'2026-04'});
 assert.ok(r.blockers.some(x=>x.code==='PREVIOUS_UNCONFIRMED'&&x.month==='2026-02'));
 assert.ok(r.blockers.some(x=>x.code==='MISSING_RESULT'&&x.month==='2026-04'));assert.deepEqual(h.state(),before);
});
test('PLCLOSE-Q03 explicit zero produces unchanged legacy preview fields and empty blockers',()=>{
 const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});
 const before=h.state(),calls=h.control.calls.length,r=h.api.queries.previewFinalizeMonth({accountId:id,month:'2026-01'});
 assert.equal(r.ok,true);assert.equal(r.status,'PREVIEW');assert.deepEqual(plain(r.errors),[]);assert.deepEqual(plain(r.blockers),[]);assert.equal(r.row.closeUsd,1000);
 assert.equal(r.row.contributionUsd,0);assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);
});
test('PLCLOSE-Q04 already finalized and future are distinguishable blockers',()=>{
 const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
 const before=h.state();for(const [month,code]of [['2026-01','ALREADY_FINALIZED'],['2026-11','FUTURE_MONTH']]){
  const r=h.api.queries.previewFinalizeMonth({accountId:id,month});assert.equal(r.ok,false);assert.ok(r.blockers.some(x=>x.code===code&&x.month===month));
 }assert.deepEqual(h.state(),before);
});
test('PLCLOSE-Q05 invalid context remains blocked and does not invent a month',()=>{
 const h=harness(),id=create(h),before=h.state();
 for(const payload of [{accountId:'missing',month:'2026-01'},{accountId:id,month:'bad'},{accountId:id,month:'2025-12'}]){
  const r=h.api.queries.previewFinalizeMonth(payload);assert.equal(r.ok,false);assert.ok(r.blockers.some(x=>x.code==='INVALID_CONTEXT'));assert.ok(r.errors.length);
 }assert.deepEqual(h.state(),before);
});
test('PLCLOSE-Q06 effective closure excludes projection and remains USD usable without FX',()=>{
 const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:-25});ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:20,brl:100});ok(h,'recordWithdrawal',{accountId:id,month:'2026-01',usd:5});
 h.context.getCurrentUsdBrlQuote=()=>({rate:null,status:'unavailable'});const r=h.api.queries.previewFinalizeMonth({accountId:id,month:'2026-01'});
 assert.equal(r.ok,true);assert.deepEqual(plain(r.blockers),[]);assert.equal(r.row.resultUsd,-25);assert.equal(r.row.contributionUsd,20);assert.equal(r.row.closeUsd,990);
});

for(const t of require('./planning_monthly_result_input_test.js').tests)test(t.name,t.run);

// Approved actionable-notification contract22/10/2026. This is a factual
// projection, not a second calculation of monthly balances or eligibility.
const pending=(h,options)=>{assert.equal(typeof h.api.queries.pendingActions,'function');return plain(h.api.queries.pendingActions(options));};
test('PLNOTICE-Q01 absent and retroactive empty plans produce no fabricated tasks',()=>{
 const empty=harness({untouched:{keep:true}}),before=empty.state();
 assert.deepEqual(pending(empty),{available:true,accounts:[],issues:[]});assert.deepEqual(empty.state(),before);
 const h=harness(),id=create(h),calls=h.control.calls.length,document=h.state();
 assert.deepEqual(pending(h),{available:true,accounts:[],issues:[]});assert.deepEqual(h.state(),document);assert.equal(h.control.calls.length,calls);
 assert.equal(h.api.queries.account(id).plan.startMonth,'2026-01');
});
test('PLNOTICE-Q02 explicit zero is a past fact and earlier empty months are a dependency not extra tasks',()=>{
 const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-04',usd:0});
 const r=pending(h),a=r.accounts[0];assert.equal(r.available,true);assert.equal(r.accounts.length,1);
 assert.equal(a.accountId,id);assert.equal(a.planId,h.api.queries.account(id).plan.id);assert.equal(a.name,'Conta sintética');
 assert.equal(a.count,1);assert.equal(a.firstMonth,'2026-01');assert.equal(a.dependencyMonth,'2026-01');
 assert.deepEqual(a.months,[{month:'2026-04',codes:['UNCONFIRMED_MONTH']}]);
});
test('PLNOTICE-Q03 nonzero current flows count once while annulled flows current and future facts do not',()=>{
 const h=harness(),id=create(h);ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:5,brl:25});
 const flow=h.api.queries.account(id).plan.contributions[0];ok(h,'recordContribution',{accountId:id,id:flow.id,month:'2026-01',usd:0,brl:0});
 ok(h,'recordContribution',{accountId:id,month:'2026-02',usd:5,brl:25});ok(h,'recordWithdrawal',{accountId:id,month:'2026-02',usd:1});
 ok(h,'recordResult',{accountId:id,month:'2026-10',usd:0});ok(h,'setProjection',{accountId:id,month:'2026-11',rate:.1,contributionUsd:500});
 const r=pending(h).accounts[0];assert.equal(r.count,1);assert.deepEqual(r.months,[{month:'2026-02',codes:['UNCONFIRMED_MONTH','MISSING_RESULT']}]);
 assert.equal(r.dependencyMonth,'2026-01');
 assert.equal(pending(h,{month:'2026-02'}).accounts.length,0);
 assert.deepEqual(pending(h,{month:'2026-03'}).accounts[0].months,r.months);
});
test('PLNOTICE-Q04 confirmed months disappear and invalidated closures remain factual',()=>{
 const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});ok(h,'finalizeMonth',{accountId:id,month:'2026-01',confirmFlows:true});
 assert.equal(pending(h).accounts.length,0);
 ok(h,'recordResult',{accountId:id,month:'2026-02',usd:0});ok(h,'finalizeMonth',{accountId:id,month:'2026-02',confirmFlows:true});
 ok(h,'recordResult',{accountId:id,month:'2026-01',usd:1});
 const a=pending(h).accounts[0];assert.equal(a.count,2);assert.equal(a.firstMonth,'2026-01');assert.equal(a.dependencyMonth,null);
 assert.ok(a.months.every(m=>m.codes.includes('CLOSURE_INVALIDATED')));
 const document=h.state();delete document.patrimonialPlanning.accounts[0].plan.results['2026-02'];h.setState(document);
 assert.deepEqual(pending(h).accounts[0].months[1],{month:'2026-02',codes:['UNCONFIRMED_MONTH','MISSING_RESULT','CLOSURE_INVALIDATED']});
});
test('PLNOTICE-Q05 inactive accounts and false closures without a confirmed predecessor are excluded',()=>{
 const h=harness(),a=create(h),b=create(h);ok(h,'recordResult',{accountId:a,month:'2026-01',usd:0});ok(h,'archiveAccount',{accountId:a,confirmation:true});
 const document=h.state();document.patrimonialPlanning.accounts[1].plan.closures['2026-01']={confirmed:false,confirmFlows:false,revision:1};h.setState(document);
 assert.equal(pending(h).accounts.length,0);assert.equal(h.api.queries.account(b).active,true);
});
test('PLNOTICE-Q06 incompatible shape malformed identity and duplicate flows are unavailable not healthy empty',()=>{
 const future=harness({patrimonialPlanning:{schemaVersion:99,opaque:'preserved'}}),before=future.state();
 assert.equal(pending(future).available,false);assert.ok(pending(future).issues.length);assert.deepEqual(future.state(),before);
 const h=harness(),id=create(h);ok(h,'recordContribution',{accountId:id,month:'2026-01',usd:5,brl:25});const valid=h.state();
 for(const corrupt of [d=>d.patrimonialPlanning.accounts.push(plain(d.patrimonialPlanning.accounts[0])),
   d=>d.patrimonialPlanning.accounts[0].plan.contributions.push(plain(d.patrimonialPlanning.accounts[0].plan.contributions[0])),
   d=>d.patrimonialPlanning.accounts[0].plan.startMonth='bad',
   d=>d.patrimonialPlanning.accounts[0].plan.results['2026-02']={usd:'0',revision:1},
   d=>d.patrimonialPlanning.accounts[0].plan.closures['2026-01']={confirmed:true,confirmFlows:false,revision:1},
   d=>d.patrimonialPlanning.accounts[0].plan.closures['2026-01']={confirmed:true,confirmFlows:true,revision:1},
   d=>{const p=d.patrimonialPlanning.accounts[0].plan;p.results['2026-02']={usd:0,revision:1};p.closures['2026-02']={confirmed:true,confirmFlows:true,revision:1};}]){
  const d=plain(valid);corrupt(d);h.setState(d);const r=pending(h);assert.equal(r.available,false);assert.ok(r.issues.length);assert.deepEqual(h.state(),d);
 }
 assert.equal(pending(h,{month:'not-a-month'}).available,false);
});
test('PLNOTICE-Q07 no timeline quote storage network or writes and returned values are detached',()=>{
 const h=harness(),id=create(h);ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});const before=h.state(),calls=h.control.calls.length;
 h.context.getCurrentUsdBrlQuote=()=>{throw Error('unexpected quote read');};
 h.context.fetch=()=>{throw Error('unexpected network');};h.context.localStorage={getItem(){throw Error('unexpected storage');},setItem(){throw Error('unexpected storage write');}};
 // The harness instruments the actual timeline entry, including calls made
 // internally by validateEnvelope, without changing the financial source.
 const timelineCalls=h.control.timelineCalls;
 const a=pending(h).accounts[0];a.months[0].codes.push('mutation');a.name='changed';
 assert.deepEqual(pending(h).accounts[0].months[0].codes,['UNCONFIRMED_MONTH']);assert.equal(pending(h).accounts[0].name,'Conta sintética');
 assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,calls);assert.equal(h.control.timelineCalls,timelineCalls);
});
test('PLNOTICE-Q08 only confirmed adoption invalidates planning and observer failure cannot change writer result',()=>{
 const h=harness(),invalidations=[];h.context.JPWNotifications={invalidate(...ids){invalidations.push(ids);throw Error('synthetic observer failure');}};
 const id=create(h);assert.deepEqual(invalidations,[['planning']]);
 h.control.mode='REFUSED';assert.equal(execute(h,'recordResult',{accountId:id,month:'2026-01',usd:0}).status,'REFUSED');assert.equal(invalidations.length,1);
 h.control.mode='CONFIRMED';ok(h,'recordResult',{accountId:id,month:'2026-01',usd:0});assert.equal(invalidations.length,2);assert.equal(h.api.queries.account(id).plan.results['2026-01'].usd,0);
});
test('PLNOTICE-Q09 accounts remain independent and unknown fields are preserved without a shared closure',()=>{
 const h=harness(),a=create(h,{name:'Primeira'}),b=create(h,{name:'Segunda'});
 ok(h,'recordResult',{accountId:a,month:'2026-01',usd:0});ok(h,'finalizeMonth',{accountId:a,month:'2026-01',confirmFlows:true});
 ok(h,'recordResult',{accountId:a,month:'2026-02',usd:0});ok(h,'recordResult',{accountId:b,month:'2026-04',usd:0});
 const d=h.state();d.patrimonialPlanning.accounts[0].extension={preserve:[1,'x']};d.patrimonialPlanning.accounts[1].plan.results['2026-11']={usd:10,revision:1};h.setState(d);
 const r=pending(h),first=r.accounts.find(x=>x.accountId===a),second=r.accounts.find(x=>x.accountId===b);
 assert.equal(r.accounts.length,2);assert.equal(first.firstMonth,'2026-02');assert.equal(first.dependencyMonth,null);assert.equal(first.count,1);
 assert.equal(second.firstMonth,'2026-01');assert.equal(second.dependencyMonth,'2026-01');assert.equal(second.count,1);assert.equal(second.months[0].month,'2026-04');
 assert.deepEqual(h.state(),d);
});
function notificationUI(h,options={}){
 const control={navigation:0,resume:null,guard:null};
 const document={activeElement:null,querySelector:()=>control.guard,getElementById:()=>null};
 Object.assign(h.context,{document,esc:String,getComputedStyle:()=>({display:'none'}),queueMicrotask,
  JPWNavigation:{navigateLocal(){control.navigation++;return false;},current:()=>({primary:'dashboard'})},
  JPWModuleAvailability:{canAccess:()=>true},...options});
 const uiFile=process.env.JPW_PLANNING_UI_SOURCE||path.join(root,'src/js/30-accounting/06-planning/03-ui.js');
 vm.runInContext(fs.readFileSync(uiFile,'utf8'),h.context);
 assert.equal(typeof h.api.ui.openMonthlyContext,'function');return control;
}
test('PLNOTICE-CTX01 invalid target and frozen module never navigate or write',async()=>{
 const h=harness(),id=create(h),planId=h.api.queries.account(id).plan.id,c=notificationUI(h),before=h.state(),calls=h.control.calls.length;
 for(const target of [{accountId:'missing',planId,month:'2026-01'},{accountId:id,planId:'old-plan',month:'2026-01'},{accountId:id,planId,month:'2025-12'}])assert.equal(await h.api.ui.openMonthlyContext(target),false);
 h.context.JPWModuleAvailability={canAccess:()=>false};assert.equal(await h.api.ui.openMonthlyContext({accountId:id,planId,month:'2026-01'}),false);
 assert.equal(c.navigation,0);assert.equal(h.control.calls.length,calls);assert.deepEqual(h.state(),before);
});
test('PLNOTICE-CTX02 changed planning identity after consent prevents contextual navigation',async()=>{
 const h=harness(),id=create(h),planId=h.api.queries.account(id).plan.id,c=notificationUI(h);
 h.context.JPWForex={executionBoardUI:{guardNavigation(_plan,resume){if(c.resume)return true;c.resume=resume;c.guard={open:true,addEventListener(){},removeEventListener(){}};return false;}}};
 const opening=h.api.ui.openMonthlyContext({accountId:id,planId,month:'2026-01'});assert.equal(c.navigation,0);assert.equal(typeof c.resume,'function');
 h.setState(h.state());c.guard.open=false;c.resume();assert.equal(await opening,false);assert.equal(c.navigation,0);
});
test('PLNOTICE-CTX03 cancellation of existing guard resolves false without choosing a context',async()=>{
 const h=harness(),id=create(h),planId=h.api.queries.account(id).plan.id,c=notificationUI(h),listeners={};
 h.context.JPWForex={executionBoardUI:{guardNavigation(_plan,resume){c.resume=resume;c.guard={open:true,addEventListener(type,fn){listeners[type]=fn;},removeEventListener(){}};return false;}}};
 const opening=h.api.ui.openMonthlyContext({accountId:id,planId,month:'2026-01'});c.guard.open=false;listeners.close();
 assert.equal(await opening,false);assert.equal(c.navigation,0);
});
test('PLNOTICE-CTX04 availability and epoch are checked again after consent and another dialog is respected',async()=>{
 for(const change of [h=>{h.context.JPWModuleAvailability={canAccess:()=>false};},h=>{h.control.epoch=1;}]){
  const h=harness(),id=create(h),planId=h.api.queries.account(id).plan.id,c=notificationUI(h);
  h.context.JPWForex={executionBoardUI:{guardNavigation(_plan,resume){if(c.resume)return true;c.resume=resume;c.guard={open:true,addEventListener(){},removeEventListener(){}};return false;}}};
  const opening=h.api.ui.openMonthlyContext({accountId:id,planId,month:'2026-01'});change(h);c.guard.open=false;c.resume();assert.equal(await opening,false);assert.equal(c.navigation,0);
 }
 const h=harness(),id=create(h),c=notificationUI(h);c.guard={open:true};assert.equal(await h.api.ui.openMonthlyContext({accountId:id,planId:h.api.queries.account(id).plan.id,month:'2026-01'}),false);assert.equal(c.navigation,0);
});

(async()=>{
 let failed=0;
 for(const t of tests){let timeout;try{
   await Promise.race([Promise.resolve().then(()=>t.run()),new Promise((_,reject)=>{timeout=setTimeout(()=>reject(Error('Test did not finish; an unresolved interaction is not PASS.')),5000);})]);
   console.log('PASS '+t.name);
  }catch(error){failed++;console.error('FAIL '+t.name+'\n'+error.stack);}finally{clearTimeout(timeout);}}
 console.log(JSON.stringify({suite:'planning_state',tests:tests.length,passed:tests.length-failed,failed}));
 process.exitCode=failed?1:0;
})();
