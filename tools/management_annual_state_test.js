/* Approved management plan 2026-10-26. Synthetic accounts only.
 * Real Forex context/ledger commands run unchanged; persistence is injected.
 * Missing feature must fail the public behavior assertion before production. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {randomUUID}=require('node:crypto');
const ROOT=path.resolve(__dirname,'..'),STATE=process.env.JPW_MANAGEMENT_STATE_SOURCE||path.join(ROOT,'src/js/30-accounting/07-management/02-state.js');
const plain=x=>JSON.parse(JSON.stringify(x));
assert.ok(fs.existsSync(STATE),'Management annual public state/commands must exist');
const BASE={accountId:'a',periodId:'p',year:2026};
const CONFIG={...BASE,startDate:'2026-12-30',annualTarget:1,daysPerWeek:5,monthsPerYear:12,excludedDates:[]};
function harness(options={}){
  const control={calls:[],mode:'CONFIRMED',epoch:0,unknown:false,disk:null,clock:options.today||'2027-01-03'};
  class Clock extends Date{constructor(...args){super(...(args.length?args:[control.clock+'T12:00:00Z']));}static now(){return Date.parse(control.clock+'T12:00:00Z');}}
  const ctx=vm.createContext({console,structuredClone,crypto:Object.hasOwn(options,'crypto')?options.crypto:{randomUUID},Date:Clock,control,addEventListener(){},setTimeout,clearTimeout,
    jpWealthPersistenceEpoch:()=>control.epoch,jpWealthPersistenceOutcomeIsUnknown:()=>control.unknown,
    markJPWealthPersistenceOutcomeUnknown:()=>{control.unknown=true;control.epoch++;},
    dgLogChange(){},hideStaleSavedTag(){},
    jpWealthConfirmedStateSnapshot:()=>plain(control.disk),
    jpWealthPersistDocument(candidate,opt={}){
      control.calls.push({candidate:plain(candidate),options:plain(opt)});
      if(control.mode==='THROW')throw Error('writer interrupted');
      if(control.mode==='UNKNOWN'){control.unknown=true;return {status:'UNKNOWN'};}
      if(control.mode==='REFUSED'||control.mode==='CONFLICT')return {status:'REFUSED',reason:control.mode};
      control.disk=plain(candidate);return {status:'CONFIRMED',payload:JSON.stringify(candidate)};
    }});
  vm.runInContext('let S={accounts:[{forexAccountId:"a",nome:"Synthetic A"},{forexAccountId:"b",nome:"Synthetic B"}],unrelated:{preserve:true}}; window=globalThis;function save(){const r=jpWealthPersistDocument(S,{component:"state"});if(r.status==="UNKNOWN")throw Error("unknown");return r.status==="CONFIRMED";}',ctx);
  for(const f of ['src/js/00-core/00-forex-policy.js','src/js/00-core/01-risk-profiles.js','src/js/10-domain/00-forex-state.js'])vm.runInContext(fs.readFileSync(path.join(ROOT,f),'utf8'),ctx,{filename:f});
  vm.runInContext(`S.forex=JPWForex.state.empty();for(const a of ['a','b'])S.forex.accountContexts.accounts[a]={accountId:a,currentPeriodId:'p',periods:{p:{accountId:a,periodId:'p',startedAt:'2026-01-01',currency:'USD',si:1000,openingBook:1000,source:'synthetic',observedAt:'2026-01-01T00:00:00Z',riskProfileSnapshot:null,phases:[],ledger:[],ledgerEvents:[],activeOperation:null,revision:1}}};`,ctx);
  if(options.initial){ctx.extra=plain(options.initial);vm.runInContext('Object.assign(S,extra)',ctx);}
  control.disk=plain(vm.runInContext('S',ctx));
  const core=fs.readFileSync(path.join(ROOT,'src/js/00-core/04-persistence.js'),'utf8');
  const marker=core.indexOf('function jpwValidateManagementAnnual(');
  if(marker>=0)vm.runInContext(core.slice(marker,core.indexOf('function load(){',marker)),ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT,'src/js/30-accounting/07-management/01-engine.js'),'utf8'),ctx);
  vm.runInContext(fs.readFileSync(STATE,'utf8'),ctx,{filename:STATE});
  const api=ctx.JPWManagementAnnual;
  return {ctx,api,control,state:()=>plain(vm.runInContext('S',ctx)),eval:src=>vm.runInContext(src,ctx),sync(){control.disk=plain(vm.runInContext('S',ctx));},token:(target=BASE)=>api.queries.token(target)};
}
const tests=[];const test=(name,run)=>tests.push({name,run});
function saved(h,config=CONFIG){const r=h.api.commands.savePlan(config,{token:h.token(config),confirmOpening:true,reason:'Confirm synthetic plan'});assert.equal(r.status,'CONFIRMED',JSON.stringify(r));return r;}
function record(h,date,value,options={}){return h.api.commands.recordResult({target:BASE,date,value,...options},{token:h.token(),confirm:true,reason:'Synthetic result'});}
function confirmed(result){assert.equal(result.status,'CONFIRMED',JSON.stringify(result));return result;}
test('MANSTATE-01 absent optional aggregate remains absent on all queries',()=>{
 const h=harness(),before=h.state();for(const f of [()=>h.api.queries.context(BASE),()=>h.api.queries.token(BASE),()=>h.api.queries.listPlans(BASE),()=>h.api.queries.model(BASE),()=>h.api.queries.previewPlan(CONFIG)])f();
 assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,0);assert.equal('managementAnnual' in h.state(),false);
});
test('MANSTATE-02 preview derives confirmed opening; explicit save preserves whole document and canonical ledger',()=>{
 const h=harness();const p=h.api.queries.previewPlan({...CONFIG,initialBalance:999999});assert.equal(p.ok,true,JSON.stringify(p));assert.equal(p.config.initialBalance,1000);
 const before=h.state();saved(h);assert.equal(h.control.calls.length,1);assert.deepEqual(h.state().forex,before.forex);assert.deepEqual(h.state().unrelated,before.unrelated);
 const plans=h.api.queries.listPlans(BASE);assert.equal(plans.length,1);assert.equal(plans[0].config.initialBalance,1000);assert.equal(h.api.queries.model(BASE).ok,true);
});
test('MANSTATE-03 config confirmation token cannot authorize another target or later root generation',()=>{
 const h=harness(),token=h.token();assert.equal(h.api.commands.savePlan({...CONFIG,accountId:'b'},{token,confirmOpening:true,reason:'wrong target'}).status,'CONFLICT');
 h.api.invalidate();assert.equal(h.api.commands.savePlan(CONFIG,{token,confirmOpening:true,reason:'old generation'}).status,'CONFLICT');assert.equal(h.control.calls.length,0);
});
test('MANSTATE-04 same scope updates one config with history and no financial writes',()=>{
 const h=harness();saved(h);saved(h,{...CONFIG,annualTarget:.5});const plans=h.api.queries.listPlans(BASE);assert.equal(plans.length,1);assert.equal(plans[0].revision,2);assert.equal(plans[0].history.length,2);assert.equal(plans[0].config.annualTarget,.5);assert.equal(h.state().forex.accountContexts.accounts.a.periods.p.ledger.length,0);
});
test('MANSTATE-05 refused and unknown config writes preserve memory; stale authorization and retries refused',()=>{
 for(const mode of ['REFUSED','CONFLICT','UNKNOWN','THROW']){const h=harness(),token=h.token(),before=h.state();h.control.mode=mode;const r=h.api.commands.savePlan(CONFIG,{token,confirmOpening:true,reason:'failure'});assert.equal(r.status,mode==='CONFLICT'?'CONFLICT':mode==='REFUSED'?'REFUSED':'UNKNOWN');assert.deepEqual(h.state(),before);h.control.mode='CONFIRMED';const n=h.control.calls.length;assert.notEqual(h.api.commands.savePlan(CONFIG,{token,confirmOpening:true,reason:'retry'}).status,'CONFIRMED');assert.equal(h.control.calls.length,n);}
});
test('MANSTATE-06 incompatible/future envelope preserved and all writes blocked',()=>{
 for(const envelope of [null,{schemaVersion:99,preserve:'future'},{schemaVersion:1,revision:0,plans:'bad',audit:[]}]){const h=harness({initial:{managementAnnual:envelope}}),before=h.state();assert.equal(h.api.queries.model(BASE).ok,false);assert.equal(h.api.commands.savePlan(CONFIG,{token:h.token(),confirmOpening:true,reason:'invalid'}).status,'INVALID');assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,0);}
});
test('MANSTATE-07 canonical result zero remains explicit; no management duplicate; operational selection unchanged',()=>{
 const h=harness();saved(h);const selection=plain(h.ctx.JPWForex.state.operationalSelection());confirmed(record(h,'2026-12-30',0));const s=h.state(),ledger=s.forex.accountContexts.accounts.a.periods.p.ledger;assert.equal(ledger.length,1);assert.equal(ledger[0].resultado,0);assert.equal(ledger[0].saldo,1000);assert.equal(s.managementAnnual.plans[0].results,undefined);assert.deepEqual(plain(h.ctx.JPWForex.state.operationalSelection()),selection);
});
test('MANSTATE-08 result preview and failed validation never save; fractional monetary precision is preserved',()=>{
 const h=harness();saved(h);const before=h.state(),n=h.control.calls.length;const p=h.api.queries.previewResult({target:BASE,date:'2026-12-30',value:-10.12});assert.equal(p.ok,true);assert.equal(p.result,-10.12);assert.equal(p.closing,989.88);
 assert.equal(h.api.queries.previewResult({target:BASE,date:'2026-12-30',value:1.001}).ok,true);
 for(const value of [null,'',NaN,Infinity])assert.equal(h.api.queries.previewResult({target:BASE,date:'2026-12-30',value}).ok,false);
 assert.deepEqual(h.state(),before);assert.equal(h.control.calls.length,n);
});
test('MANSTATE-09 canonical correction preserves IDs and observed later balances',()=>{
 const h=harness();saved(h);confirmed(record(h,'2026-12-30',10));h.eval(`JPWForex.state.recordAccountLedger({action:'RECORDED',accountId:'a',periodId:'p',data:'2026-12-31',resultado:20,saldo:1300,nota:'observed'},{reason:'Observed fact'})`);
 const rows=h.state().forex.accountContexts.accounts.a.periods.p.ledger;confirmed(record(h,'2026-12-30',5,{id:rows[0].id}));const next=h.state().forex.accountContexts.accounts.a.periods.p.ledger;assert.equal(next[0].id,rows[0].id);assert.equal(next[0].resultado,5);assert.equal(next[1].saldo,1300);assert.ok(next[0].version>rows[0].version);
});
test('MANSTATE-10 account/period/epoch revisions reject stale confirmation; independent target supported',()=>{
 const h=harness();saved(h);const token=h.token();h.eval('S.forex.accountContexts.accounts.a.periods.p.revision++');h.sync();assert.equal(h.api.commands.recordResult({target:BASE,date:'2026-12-30',value:1},{token,confirm:true,reason:'stale'}).status,'CONFLICT');
 const t=h.token();h.control.epoch++;assert.equal(h.api.commands.recordResult({target:BASE,date:'2026-12-30',value:1},{token:t,confirm:true,reason:'epoch'}).status,'CONFLICT');
});
test('MANSTATE-11 declare no result is explicit and does not change scheduled projection or canonical ledger',()=>{
 const h=harness();saved(h);const before=h.api.queries.model(BASE).model;confirmed(h.api.commands.declareNoResult({target:BASE,date:'2026-12-30'},{token:h.token(),confirm:true,reason:'No realized result occurred'}));const after=h.api.queries.model(BASE).model;
 assert.equal(h.state().forex.accountContexts.accounts.a.periods.p.ledger.length,0);assert.deepEqual(plain(after.rows.map(r=>r.planned)),plain(before.rows.map(r=>r.planned)));assert.equal(h.state().managementAnnual.plans[0].declarations.length,1);
 assert.equal(record(h,'2026-12-30',0).status,'INVALID');
});
test('MANSTATE-12 existing financial record forbids contradictory no-result declaration',()=>{
 const h=harness();saved(h);confirmed(record(h,'2026-12-30',0));const before=h.state();assert.equal(h.api.commands.declareNoResult({target:BASE,date:'2026-12-30'},{token:h.token(),confirm:true,reason:'contradiction'}).status,'INVALID');assert.deepEqual(h.state(),before);
});
test('MANSTATE-13 annual close requires ended year and complete dates; snapshots immutable and reconference after correction',()=>{
 const h=harness();saved(h);assert.equal(h.api.queries.previewAnnualClose(BASE).ok,false);confirmed(record(h,'2026-12-30',10));confirmed(record(h,'2026-12-31',-1));const preview=h.api.queries.previewAnnualClose(BASE);assert.equal(preview.ok,true,JSON.stringify(preview));
 confirmed(h.api.commands.closeAnnual(BASE,{token:h.token(),confirm:true}));const snapshot=h.state().managementAnnual.plans[0].snapshots[0];assert.equal(h.api.queries.model(BASE).closureStatus,'CONFIRMED');
 const id=h.state().forex.accountContexts.accounts.a.periods.p.ledger[0].id;confirmed(record(h,'2026-12-30',20,{id}));assert.equal(h.api.queries.model(BASE).closureStatus,'RECONFIRM_REQUIRED');assert.deepEqual(h.state().managementAnnual.plans[0].snapshots[0],snapshot);
 const current=harness({today:'2026-12-30'});saved(current);assert.equal(current.api.commands.closeAnnual(BASE,{token:current.token(),confirm:true}).status,'INVALID');
});
test('MANSTATE-14 opening correction before start affects live actual and invalidates snapshot without moving planned baseline',()=>{
 const h=harness();h.eval(`JPWForex.state.recordAccountLedger({action:'RECORDED',accountId:'a',periodId:'p',data:'2026-12-29',resultado:50,saldo:null,nota:''},{reason:'Earlier actual'})`);saved(h);confirmed(record(h,'2026-12-30',0));confirmed(record(h,'2026-12-31',0));confirmed(h.api.commands.closeAnnual(BASE,{token:h.token(),confirm:true}));
 const first=h.state().forex.accountContexts.accounts.a.periods.p.ledger[0];h.eval(`JPWForex.state.recordAccountLedger({action:'CORRECTED',id:${JSON.stringify(first.id)},accountId:'a',periodId:'p',data:'2026-12-29',resultado:100,saldo:null,nota:''},{reason:'Prior opening correction'})`);
 const m=h.api.queries.model(BASE);assert.equal(m.closureStatus,'RECONFIRM_REQUIRED');assert.equal(m.plan.config.initialBalance,1050);assert.equal(m.model.rows[0].planned.opening,1050);assert.equal(m.model.rows[0].actual.opening,1100);
});
test('MANSTATE-15 confirmed source required; blank opening and unconfirmed RAM never saved',()=>{
 const h=harness();h.eval('S.forex.accountContexts.accounts.a.periods.p.openingBook=null');h.sync();assert.equal(h.api.queries.previewPlan(CONFIG).ok,false);h.eval('S.forex.accountContexts.accounts.a.periods.p.openingBook=1000');h.sync();const token=h.token();h.eval('S.unrelated.pending=true');assert.equal(h.api.commands.savePlan(CONFIG,{token,confirmOpening:true,reason:'not confirmed'}).status,'CONFLICT');assert.equal(h.control.calls.length,0);
});
test('MANSTATE-16 void uses real canonical history, preserves records in audit and original snapshots',()=>{
 const h=harness();saved(h);confirmed(record(h,'2026-12-30',2));const row=h.state().forex.accountContexts.accounts.a.periods.p.ledger[0];confirmed(h.api.commands.voidResult({target:BASE,id:row.id},{token:h.token(),confirm:true,reason:'Synthetic invalid original'}));const p=h.state().forex.accountContexts.accounts.a.periods.p;assert.equal(p.ledger.length,0);assert.equal(p.ledgerEvents.at(-1).action,'VOIDED');assert.equal(p.ledgerEvents.at(-1).before.id,row.id);
});
test('MANSTATE-17 early optional validator supports old backups and rejects malformed/future while retaining bytes',()=>{
 const h=harness();assert.equal(typeof h.ctx.jpwValidateManagementAnnual,'function');assert.doesNotThrow(()=>h.ctx.jpwValidateManagementAnnual({}));saved(h);assert.doesNotThrow(()=>h.ctx.jpwValidateManagementAnnual(h.state()));
 for(const managementAnnual of [null,{schemaVersion:2},{schemaVersion:1,revision:0,plans:[],audit:[],password:'forbidden'}]){const value={managementAnnual},before=JSON.stringify(value);assert.throws(()=>h.ctx.jpwValidateManagementAnnual(value));assert.equal(JSON.stringify(value),before);}
 const restored=harness({initial:h.state()});assert.equal(restored.api.queries.model(BASE).ok,true);assert.equal(restored.control.calls.length,0);
});
test('MANSTATE-18 unknown financial outcome blocks config and every command without blind retry',()=>{
 const h=harness();saved(h);h.control.mode='UNKNOWN';assert.equal(record(h,'2026-12-30',2).status,'UNKNOWN');const n=h.control.calls.length;h.control.mode='CONFIRMED';assert.equal(h.api.commands.savePlan(CONFIG,{token:h.token(),confirmOpening:true,reason:'retry'}).status,'UNKNOWN');assert.equal(h.control.calls.length,n);
});

test('MANSTATE-19 declarations can be explicitly revoked with history before a real result is entered',()=>{
 const h=harness();saved(h);confirmed(h.api.commands.declareNoResult({target:BASE,date:'2026-12-30'},{token:h.token(),confirm:true,reason:'No realized result'}));
 assert.equal(typeof h.api.commands.revokeNoResult,'function','A declaration needs an explicit correction path');
 confirmed(h.api.commands.revokeNoResult({target:BASE,date:'2026-12-30'},{token:h.token(),confirm:true,reason:'Later statement shows a result'}));
 assert.equal(h.state().managementAnnual.plans[0].declarations.length,0);assert.equal(h.state().managementAnnual.audit.at(-1).before.kind,'NO_RESULT');confirmed(record(h,'2026-12-30',1));
});
test('MANSTATE-20 reference constants remain editable reference-only metadata',()=>{
 const h=harness();saved(h,{...CONFIG,referenceYears:2,referenceDays:360});const p=h.api.queries.model(BASE);assert.equal(p.plan.config.referenceYears,2);assert.equal(p.plan.config.referenceDays,360);
 const base=harness();saved(base);assert.deepEqual(plain(p.model.rows.map(r=>r.planned)),plain(base.api.queries.model(BASE).model.rows.map(r=>r.planned)));
});

function actualWriterHarness(){
 const h=harness(),raw=JSON.stringify(h.state());h.control.expectedDiagnostics=[];h.ctx.console={...console,error:(...args)=>h.control.expectedDiagnostics.push(String(args[0]))};h.ctx.storage={raw,sets:0,mode:'normal',getItem(){if(this.mode==='read-after'&&this.sets)throw Error('synthetic readback failure');return this.raw;},setItem(k,v){this.sets++;if(this.mode==='quota')throw Error('synthetic quota');this.raw=v;}};
 h.ctx.jpWealthPersistenceSetResult=(status,reason,component)=>({status,reason,component});h.ctx.jpWealthPersistenceSafeFeedback=()=>{};
 vm.runInContext(`const LSKEY='synthetic';let jpWealthSessionEpoch=0;let jpWealthPersistenceOutcomeUnknown=false;let jpWealthPersistenceBlocked=false;const jpWealthLoadRecovery={active:false};let jpWealthLastPersistedRaw=${JSON.stringify(raw)};const localStorage=storage;`,h.ctx);
 h.ctx.jpWealthAdoptPersistedRaw=value=>{h.ctx.nextRaw=value;h.control.disk=JSON.parse(value);vm.runInContext('jpWealthLastPersistedRaw=nextRaw',h.ctx);};
 h.ctx.jpWealthPersistenceOutcomeIsUnknown=()=>h.control.unknown||h.eval('jpWealthPersistenceOutcomeUnknown');
 h.ctx.markJPWealthPersistenceOutcomeUnknown=()=>{h.control.unknown=true;h.control.epoch++;h.eval('jpWealthPersistenceOutcomeUnknown=true');};
 const source=fs.readFileSync(path.join(ROOT,'src/js/00-core/04-persistence.js'),'utf8');vm.runInContext(source.slice(source.indexOf('function jpWealthPersistDocument('),source.indexOf('function jpWealthConfirmedStateSnapshot(')),h.ctx);return h;
}
test('MANSTATE-21 real confirmed writer readback, quota, conflict and indeterminate outcomes',()=>{
 const accepted=actualWriterHarness();saved(accepted);assert.deepEqual(JSON.parse(accepted.ctx.storage.raw),accepted.state());confirmed(record(accepted,'2026-12-30',1.001));assert.deepEqual(JSON.parse(accepted.ctx.storage.raw),accepted.state());
 for(const mode of ['quota','conflict','read-after']){const h=actualWriterHarness(),before=h.state();if(mode==='conflict')h.ctx.storage.raw=JSON.stringify({...before,foreign:'other tab'});else h.ctx.storage.mode=mode;const r=h.api.commands.savePlan(CONFIG,{token:h.token(),confirmOpening:true,reason:'boundary'});assert.equal(r.status,mode==='quota'?'REFUSED':mode==='conflict'?'CONFLICT':'UNKNOWN');assert.deepEqual(h.state(),before);}
});
test('MANSTATE-22 a financially indeterminate write is never exposed as confirmed actual data by queries',()=>{
 const h=harness();saved(h);h.control.mode='UNKNOWN';assert.equal(record(h,'2026-12-30',777).status,'UNKNOWN');assert.equal(h.api.queries.model(BASE).ok,false,'Tentative RAM is not a confirmed ledger');assert.equal(h.api.queries.context(BASE).status,'UNKNOWN');
});

test('MANSTATE-23 account currency is preserved without conversion and query DTOs are defensive',()=>{
 const h=harness();h.eval("S.forex.accountContexts.accounts.a.periods.p.currency='EUR'");h.sync();saved(h);confirmed(record(h,'2026-12-30',1.001));const m=h.api.queries.model(BASE);assert.equal(m.plan.config.currency,'EUR');assert.equal(h.state().forex.accountContexts.accounts.a.periods.p.ledger[0].currency,'EUR');m.plan.config.initialBalance=99;assert.equal(h.api.queries.model(BASE).plan.config.initialBalance,1000);
});
test('MANSTATE-24 root replacement rejects prior review even when content is identical',()=>{
 const h=harness(),token=h.token();h.eval('S=structuredClone(S)');assert.equal(h.api.commands.savePlan(CONFIG,{token,confirmOpening:true,reason:'changed context'}).status,'CONFLICT');assert.equal(h.control.calls.length,0);
});
test('MANSTATE-25 repeated confirmation cannot duplicate a result or silently refresh its authorization',()=>{
 const h=harness();saved(h);const token=h.token(),input={target:BASE,date:'2026-12-30',value:3};confirmed(h.api.commands.recordResult(input,{token,confirm:true,reason:'one action'}));const count=h.control.calls.length;assert.equal(h.api.commands.recordResult(input,{token,confirm:true,reason:'duplicate'}).status,'CONFLICT');assert.equal(h.control.calls.length,count);assert.equal(h.state().forex.accountContexts.accounts.a.periods.p.ledger.length,1);
});

test('MANSTATE-26 optional inert notes are validated and preserved through canonical creation/correction',()=>{
 const h=harness();saved(h);confirmed(record(h,'2026-12-30',1,{note:'Fonte sintética'}));const row=h.state().forex.accountContexts.accounts.a.periods.p.ledger[0];assert.equal(row.nota,'Fonte sintética');confirmed(record(h,'2026-12-30',2,{id:row.id}));assert.equal(h.state().forex.accountContexts.accounts.a.periods.p.ledger[0].nota,'Fonte sintética');confirmed(record(h,'2026-12-30',3,{id:row.id,note:'Revisão manual'}));assert.equal(h.state().forex.accountContexts.accounts.a.periods.p.ledger[0].nota,'Revisão manual');
 for(const note of [null,12,'x'.repeat(501),'control\n'])assert.equal(h.api.queries.previewResult({target:BASE,date:'2026-12-31',value:0,note}).ok,false);
});
test('MANSTATE-27 imported history/snapshots cannot claim another identity or future revision',()=>{
 const h=harness();saved(h);const other=h.state();other.managementAnnual.plans[0].history[0].config.accountId='foreign-account';assert.throws(()=>h.ctx.jpwValidateManagementAnnual(other));
 confirmed(record(h,'2026-12-30',0));confirmed(record(h,'2026-12-31',0));confirmed(h.api.commands.closeAnnual(BASE,{token:h.token(),confirm:true}));const snapshot=h.state();snapshot.managementAnnual.plans[0].snapshots[0].planRevision=999;assert.throws(()=>h.ctx.jpwValidateManagementAnnual(snapshot));
});
test('MANSTATE-28 preview and save reject duplicate excluded dates consistently',()=>{
 const h=harness(),input={...CONFIG,excludedDates:['2026-01-05','2026-01-05']};assert.equal(h.api.queries.previewPlan(input).ok,false);assert.equal(h.api.commands.savePlan(input,{token:h.token(),confirmOpening:true,reason:'duplicates'}).status,'INVALID');assert.equal(h.control.calls.length,0);
});

test('MANSTATE-29 restored cross-family currency disagreement is unavailable even without ledger rows',()=>{
 const h=harness();saved(h);for(const date of ['2026-12-30','2026-12-31'])confirmed(h.api.commands.declareNoResult({target:BASE,date},{token:h.token(),confirm:true,reason:'No realized result'}));const before=h.state().managementAnnual;h.eval("S.forex.accountContexts.accounts.a.periods.p.currency='EUR'");h.sync();const model=h.api.queries.model(BASE);assert.equal(model.ok,false,'USD plan cannot present EUR period as the same currency');assert.match(model.errors.join(' '),/moeda/i);assert.equal(h.api.queries.previewAnnualClose(BASE).ok,false);assert.deepEqual(h.state().managementAnnual,before);
});

test('MANSTATE-30 context recovery is explicit confirmed-only, returns change flag and does not stale tokens on every render',()=>{
 const h=harness();saved(h);assert.equal(h.api.resetContext(),false);const token=h.token();assert.equal(h.api.resetContext(),false);confirmed(h.api.commands.recordResult({target:BASE,date:'2026-12-30',value:0},{token,confirm:true,reason:'unchanged verified context'}));
 const recovery=harness();saved(recovery);recovery.control.mode='UNKNOWN';assert.equal(recovery.api.commands.savePlan({...CONFIG,annualTarget:.5},{token:recovery.token(),confirmOpening:true,reason:'unknown'}).status,'UNKNOWN');recovery.control.unknown=false;recovery.control.mode='CONFIRMED';assert.equal(recovery.api.resetContext(),true);saved(recovery,{...CONFIG,annualTarget:.5});
 const tentative=harness();saved(tentative);tentative.control.mode='UNKNOWN';assert.equal(record(tentative,'2026-12-30',7).status,'UNKNOWN');tentative.control.unknown=false;assert.equal(tentative.api.resetContext(),false,'Tentative RAM cannot reauthorize itself');assert.equal(tentative.api.queries.model(BASE).status,'UNKNOWN');
});
test('MANSTATE-31 ordinary confirmed root replacements preserve UI drafts; a verified new epoch resets once',()=>{
 const h=harness();saved(h);const before=h.control.calls.length;h.eval('S=structuredClone(S)');h.sync();assert.equal(h.api.resetContext(),false,'A normal domain write does not request clearing UI drafts');
 h.control.epoch++;assert.equal(h.api.resetContext(),true,'A verified base/session epoch must reset ephemeral selection and drafts');assert.equal(h.api.resetContext(),false,'An already consumed epoch must not repeatedly reset');assert.equal(h.control.calls.length,before,'Context reset never writes');
 const unconfirmed=harness();saved(unconfirmed);unconfirmed.eval('S=structuredClone(S);S.unrelated.tentative=true');unconfirmed.control.epoch++;assert.equal(unconfirmed.api.resetContext(),false,'A new epoch alone cannot bless unconfirmed RAM');
});
test('MANSTATE-32 startup without randomUUID stays read-only and identities retain session isolation',()=>{
 for(const crypto of [{},undefined]){
  const h=harness({crypto}),other=harness({crypto}),before=h.state(),token=h.token();
  assert.match(token.session,/^management_session_\S+$/);assert.notEqual(token.session,other.token().session);
  assert.equal(h.api.queries.model(BASE).status,'NO_PLAN');assert.equal(h.control.calls.length,0);assert.deepEqual(h.state(),before);
  saved(h);const count=h.control.calls.length;
  assert.equal(h.api.commands.savePlan({...CONFIG,annualTarget:.5},{token:other.token(),confirmOpening:true,reason:'Foreign session cannot confirm'}).status,'CONFLICT');
  assert.equal(h.control.calls.length,count);assert.ok(h.state().managementAnnual.plans[0].id.startsWith('management_plan_'));
 }
});
let failures=0;for(const {name,run} of tests){try{run();console.log('PASS '+name);}catch(error){failures++;console.error('FAIL '+name+'\n'+error.stack);}}console.log(JSON.stringify({cases:tests.length,passed:tests.length-failures,failed:failures}));if(failures)process.exitCode=1;
