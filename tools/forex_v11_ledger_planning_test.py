#!/usr/bin/env python3
"""Synthetic Forex ledger/planning command contracts; local Node VM, no network."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
PATHS=['src/js/00-core/00-forex-policy.js','src/js/00-core/01-risk-profiles.js','src/js/00-core/03-default-state.js','src/js/10-domain/00-forex-engine.js','src/js/10-domain/00-forex-state.js','src/js/30-accounting/01-daily-ledger.js','src/js/30-accounting/05-fx-planning/01-fx-model.js','src/js/30-accounting/05-fx-planning/02-fx-engine.js','src/js/30-accounting/05-fx-planning/03-fx-state.js']
NODE=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const input=JSON.parse(fs.readFileSync(0,'utf8'));let unknown=false,writes=0,mode='true',disk=null,epoch=0,periodId=null;
const c={Date,Math,JSON,structuredClone,crypto:crypto.webcrypto,clearTimeout,setTimeout,addEventListener(){},
 hideStaleSavedTag(){},persistenceAlertEl(){return null;},layoutPersistenceBanners(){},
 jpWealthPersistenceEpoch(){return epoch;},
 jpWealthPersistenceOutcomeIsUnknown(){return unknown;},markJPWealthPersistenceOutcomeUnknown(){unknown=true;},
 save(){writes++;if(mode==='false')return false;if(mode==='throw')throw Error('synthetic');disk=JSON.stringify(c.S);epoch++;return mode==='undefined'?undefined:true;},
 dgLogChange(...a){c.S.dataGovernance.changeLog.push(a);},reserveRequirementsCalc(){return {};}};
c.window=c; // Browser/global identity only; account selection and commands are real modules.
vm.createContext(c);for(const p of input.paths)vm.runInContext(input.sources[p],c,{filename:p});
const run=s=>vm.runInContext(s,c),clone=x=>JSON.parse(JSON.stringify(x));
const eq=(a,b)=>assert.deepStrictEqual(clone(a),clone(b)),near=(a,b)=>assert(Math.abs(a-b)<1e-8,`${a} != ${b}`);
function seed(){
 unknown=false;mode='true';epoch++;c.S=run('structuredClone(DEFAULTS)');
 c.S.params={...c.S.params,saldoIni:1000,saldoAtu:1000,inicio:'2026-01-01'};
 c.S.accounts=[{forexAccountId:'account-A',nome:'Synthetic A',tipo:'MESTRE',platformCurrency:'USD'}];
 c.S.ledger=[];c.S.ledgerHistory={schemaVersion:1,events:[]};c.S.dataGovernance={changeLog:[]};
 c.S.fxPlanning={schemaVersion:1,plan:null,auditLog:[]};
 const prepared=c.JPWForex.state.recordAccountPeriod({accountId:'account-A',startedAt:'2026-01-01',currency:'USD',
  si:1000,openingBook:1000,source:'Synthetic fixture',activateCurrentPeriod:true},{reason:'Explicit fixture preparation'});
 assert(prepared.ok,prepared.error);periodId=c.S.forex.accountContexts.accounts['account-A'].currentPeriodId;
 assert(c.JPWForex.state.selectOperationalContext('account-A',periodId).ok);
 // Preparation is a confirmed baseline, not a write caused by the scenario under test.
 writes=0;disk=JSON.stringify(c.S);
}
const context=()=>({accountId:'account-A',periodId,complete:true});
const period=()=>c.S.forex.accountContexts.accounts['account-A'].periods[periodId];
const rows=()=>c.JPWLedger.rows();
const one=()=>{const r=rows();assert.equal(r.length,1);return r[0];};
const plan=()=>assert(run(`fxPlanCreate({name:'Synthetic',assumptions:{startMonth:'2026-01',horizonMonths:4,initialBalanceUsd:1000,defaultMonthlyReturn:.01}})`).ok);
const record=()=>run(`ledgerRecord({data:'2026-01-02',resultado:10,saldo:1010})`);
const actual=()=>assert(run(`fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:10,contributionsConfirmed:true})`).ok);
const series=()=>run('fxForecastTimeline(fxActivePlan())');
const tests=[];function test(name,fn){seed();fn();tests.push({name,status:'PASS'});}
test('baseline arithmetic',()=>{const r=run(`fxPlannedTimeline({startMonth:'2026-01',horizonMonths:4,initialBalanceUsd:1000,defaultMonthlyReturn:.01,monthOverrides:{'2026-03':-.02},plannedContributions:{'2026-01':{personalUsd:100,propUsd:0}}})`);[1110,1121.1,1098.678,1109.66478].forEach((v,i)=>near(r[i].close,v));});
test('legacy read is non-mutating',()=>{
 c.S.ledger=[{data:'2026-01-01',resultado:0,saldo:1000,extension:7}];const b=clone(c.S);
 const preview=c.JPWForex.state.legacyAccountPreview();
 assert.equal(preview.associations[0].status,'UNRECONCILED');eq(preview.source.ledger,c.S.ledger);
 assert.equal(rows().length,0);eq(c.S,b);assert.equal(writes,0);
});
test('zero, correction versions and before-after history',()=>{
 assert(run(`ledgerRecord({data:'2026-01-02',resultado:0,saldo:''})`).ok);let row=one();
 assert.equal(row.accountId,'account-A');assert.equal(row.periodId,periodId);assert.equal(row.resultado,0);
 assert(c.JPWLedger.correct(row.id,{data:row.data,resultado:10,saldo:1010},{reason:'broker correction',expectedVersion:1}).ok);
 row=one();assert.equal(row.version,2);assert.equal(period().ledgerEvents[1].before.resultado,0);
 assert.equal(period().ledgerEvents[1].after.resultado,10);assert.equal(c.S.ledger.length,0);assert.equal(c.S.ledgerHistory.events.length,0);
});
test('stale correction and missing reason',()=>{
 assert(record().ok);const row=one(),b=clone(c.S),n=writes;
 assert(!c.JPWLedger.correct(row.id,{data:row.data,resultado:99,saldo:1099},{reason:'stale',expectedVersion:0}).ok);
 assert(!c.JPWLedger.correct(row.id,{data:row.data,resultado:99,saldo:1099},{expectedVersion:1}).ok);
 eq(c.S,b);assert.equal(writes,n);
});
test('invalid date and absent result are not zero',()=>{for(const v of [null,'',' ',undefined,Infinity,NaN,true,false,[],{}])assert(!c.window.JPWLedger.record({data:'2026-01-02',resultado:v,saldo:1000}).ok);assert(!c.window.JPWLedger.record({data:'2026-02-30',resultado:0,saldo:1000}).ok);assert.equal(writes,0);});
test('void retains original audit',()=>{
 assert(record().ok);assert(c.JPWLedger.void(one().id,{reason:'duplicate',expectedVersion:1}).ok);
 assert.equal(rows().length,0);assert.equal(period().ledgerEvents[1].before.resultado,10);
 assert.equal(c.S.ledger.length,0);assert.equal(c.S.ledgerHistory.events.length,0);
});
test('ledger false rolls back all scoped state',()=>{const b=clone(c.S);mode='false';assert(!record().ok);eq(c.S,b);});
test('ledger unknown preserves attempt and blocks repeat',()=>{
 const persisted=disk;mode='throw';assert.equal(record().persistido,null);assert.equal(period().ledger.length,1);
 assert.equal(disk,persisted);const n=writes;
 assert(!run(`ledgerRecord({data:'2026-01-03',resultado:0,saldo:1010})`).ok);assert.equal(writes,n);
});
test('unknown history schema preserved',()=>{
 c.S.ledgerHistory={schemaVersion:9,opaque:'preserve'};
 c.S.forex.accountContexts={...clone(c.S.forex.accountContexts),schemaVersion:9,opaque:'preserve scoped future history'};
 const b=clone(c.S);assert(!record().ok);eq(c.S,b);assert.equal(writes,0);
});
test('row N changes suffix and preserves prefix/actual/baseline',()=>{plan();actual();const b=series(),base=clone(c.S.fxPlanning.plan.baseline),a=clone(c.S.fxPlanning.plan.actuals);assert(run(`fxPlanReviseFromMonth('2026-03',{rate:.02,personalUsd:100,propUsd:0},'March')`).ok);const r=series();eq(r.slice(0,2),b.slice(0,2));near(r[2].close,b[2].open*1.02+100);near(r[3].open,r[2].close);eq(c.S.fxPlanning.plan.baseline,base);eq(c.S.fxPlanning.plan.actuals,a);assert(!run(`fxPlanReviseFromMonth('2026-01',{rate:.9},'closed')`).ok);});
test('new revision reconstructs exact source after actual edit',()=>{
 plan();actual();const b=series();assert(run(`fxPlanReviseFromMonth('2026-03',{rate:.02},'revision')`).ok);
 const finalized=clone(c.S),n=writes;
 assert(!run(`fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:20,contributionsConfirmed:true})`).ok);
 assert(!run(`fxPlanReopenMonth('2026-01','')`).ok);eq(c.S,finalized);assert.equal(writes,n);
 assert(run(`fxPlanReopenMonth('2026-01','Correct documented realized result')`).ok);
 assert.equal(c.S.fxPlanning.plan.actuals['2026-01'].closureStatus,'REOPENED');
 assert(run(`fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:20,contributionsConfirmed:true})`).ok);
 assert.equal(c.S.fxPlanning.plan.actuals['2026-01'].closureStatus,'FINALIZED');
 eq(run('fxForecastAtRevision(fxActivePlan(),0)'),b);
 const history=c.S.fxPlanning.plan.actualHistory;
 eq(history.map(r=>r.action),['FINALIZED','REOPENED','REFINALIZED']);assert.equal(history[2].before.profitUsd,10);
 assert.equal(history[2].after.profitUsd,20);
});
test('explicit rebase preserves prefix and facts',()=>{plan();actual();const b=series(),base=clone(c.S.fxPlanning.plan.baseline),a=clone(c.S.fxPlanning.plan.actuals);assert(run(`fxPlanRebase('2026-03',2000,'future anchor')`).ok);const r=series();eq(r.slice(0,2),b.slice(0,2));near(r[2].open,2000);near(r[3].open,2020);eq(c.S.fxPlanning.plan.baseline,base);eq(c.S.fxPlanning.plan.actuals,a);assert(!run(`fxPlanRebase('2026-01',2000,'closed')`).ok);});
test('scenario leaves PLAN and ACTUAL unchanged',()=>{plan();actual();const b=series(),a=clone(c.S.fxPlanning.plan.actuals),cur=clone(c.S.fxPlanning.plan.current),r=run(`fxScenarioSave({name:'Cautious'})`);assert(r.ok);assert(c.window.JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:0},'flat',r.id).ok);const sc=c.S.fxPlanning.plan.scenarios[0],rows=c.window.JPWFx.engine.fxScenarioTimeline(run('fxActivePlan()'),sc);eq(rows[0],b[0]);near(rows[1].close,1010);eq(c.S.fxPlanning.plan.current,cur);eq(c.S.fxPlanning.plan.actuals,a);assert(c.window.JPWFx.state.fxScenarioDelete(r.id).ok);assert.equal(c.S.fxPlanning.plan.scenarioArchive.length,1);});
test('planning refusal rollback and UNKNOWN',()=>{plan();const b=clone(c.S);mode='false';assert(!run(`fxPlanRebase('2026-02',2000,'test')`).ok);eq(c.S,b);mode='throw';assert.equal(run(`fxPlanRebase('2026-02',2000,'test')`).persistido,null);const n=writes;assert(!run(`fxPlanRebase('2026-02',2000,'test')`).ok);assert.equal(writes,n);});
test('actual absence rejected, explicit zero accepted',()=>{
 plan();const b=clone(c.S),n=writes;
 assert(!run(`fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:null,contributionsConfirmed:true})`).ok);
 assert(!run(`fxPlanRecordActual('2026-01',{inputType:'rate',returnRate:'',contributionsConfirmed:true})`).ok);
 assert(!run(`fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:0})`).ok);eq(c.S,b);assert.equal(writes,n);
 assert(run(`fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:0,contributionsConfirmed:true})`).ok);
 assert.equal(c.S.fxPlanning.plan.actuals['2026-01'].profitUsd,0);
});
test('coercible objects and whitespace are not financial inputs',()=>{
 plan();const b=clone(c.S),n=writes;for(const v of [true,false,[],{},' ']){
  assert(!c.JPWFx.state.fxPlanRecordActual('2026-01',{inputType:'usd',profitUsd:v,contributionsConfirmed:true}).ok);
  assert(!c.JPWFx.state.fxPlanReviseFromMonth('2026-02',{rate:v},'invalid').ok);
 }eq(c.S,b);assert.equal(writes,n);
});
test('numeric legacy strings calculate in copy without concatenation',()=>{
 c.S.ledger=[{data:'2026-01-02',resultado:'10',saldo:'1010',referenceBalance:'1000',accountId:'account-A',periodId,currency:'USD'}];
 const legacy=clone(c.S.ledger),n=writes;assert.equal(rows().length,0);
 const preview=c.JPWForex.state.legacyAccountPreview();assert.equal(preview.associations[0].status,'PROVEN');
 eq(preview.source.ledger,legacy);assert.equal(writes,n);
 // Only an explicitly identified command can enter the current ledger; the legacy source stays immutable.
 assert(c.JPWLedger.record({data:'2026-01-02',resultado:'10',saldo:'1010'},{context:context()}).ok);
 assert.equal(one().resultado,10);assert.equal(one().saldo,1010);
 const b=clone(c.S),saved=writes,r=c.JPWLedger.monthlyActual('2026-01',context());
 assert.equal(r.status,'COMPLETE');assert.equal(r.profitUsd,10);eq(c.S,b);eq(c.S.ledger,legacy);assert.equal(writes,saved);
});
test('monthly provenance and completeness explicit',()=>{
 assert(record().ok);assert.equal(c.JPWLedger.monthlyActual('2026-01',{}).status,'PARTIAL');
 assert.equal(c.JPWLedger.monthlyActual('2026-01',{...context(),complete:false}).status,'PARTIAL');
 assert.equal(c.JPWLedger.monthlyActual('2026-01',context()).status,'COMPLETE');
});
test('import retains source, rejects overwrite/stale, explicit replace',()=>{
 plan();assert(record().ok);const row=one(),ctx=context();let p=c.JPWLedger.monthlyActual('2026-01',ctx);
 assert(c.JPWFx.state.fxPlanImportLedgerActual('2026-01',{...ctx,sourceVersion:p.source.version,contributionsConfirmed:true}).ok);
 eq(c.S.fxPlanning.plan.actuals['2026-01'].source,p.source);const finalized=clone(c.S),n=writes;
 assert(!c.JPWFx.state.fxPlanImportLedgerActual('2026-01',{...ctx,sourceVersion:p.source.version,contributionsConfirmed:true}).ok);
 eq(c.S,finalized);assert.equal(writes,n);
 assert(c.JPWLedger.correct(row.id,{data:'2026-01-02',resultado:15,saldo:1015},{reason:'corrected source',expectedVersion:1}).ok);
 const corrected=clone(c.S),nw=writes;
 assert(!c.JPWFx.state.fxPlanImportLedgerActual('2026-01',{...ctx,sourceVersion:p.source.version,replace:true,contributionsConfirmed:true}).ok);
 eq(c.S,corrected);assert.equal(writes,nw);
 assert(run(`fxPlanReopenMonth('2026-01','Reconcile explicitly corrected ledger source')`).ok);
 const reopened=clone(c.S),nr=writes;
 // Reopening does not make a stale source version valid.
 assert(!c.JPWFx.state.fxPlanImportLedgerActual('2026-01',{...ctx,sourceVersion:p.source.version,replace:true,contributionsConfirmed:true}).ok);
 eq(c.S,reopened);assert.equal(writes,nr);assert.equal(c.S.fxPlanning.plan.actuals['2026-01'].profitUsd,10);
 p=c.JPWLedger.monthlyActual('2026-01',ctx);
 assert(!c.JPWFx.state.fxPlanImportLedgerActual('2026-01',{...ctx,sourceVersion:p.source.version,contributionsConfirmed:true}).ok);
 assert(c.JPWFx.state.fxPlanImportLedgerActual('2026-01',{...ctx,sourceVersion:p.source.version,replace:true,contributionsConfirmed:true}).ok);
 assert.equal(c.S.fxPlanning.plan.actuals['2026-01'].profitUsd,15);
 assert.equal(c.S.fxPlanning.plan.actuals['2026-01'].closureStatus,'FINALIZED');eq(c.S.fxPlanning.plan.actuals['2026-01'].source,p.source);
});
test('inconsistent daily chain blocks import',()=>{
 plan();assert(run(`ledgerRecord({data:'2026-01-02',resultado:10,saldo:1020})`).ok);
 const ctx=context(),p=c.JPWLedger.monthlyActual('2026-01',ctx),b=clone(c.S),n=writes;
 assert.equal(p.status,'PARTIAL');
 assert(!c.JPWFx.state.fxPlanImportLedgerActual('2026-01',{...ctx,sourceVersion:p.source.version,contributionsConfirmed:true}).ok);
 eq(c.S,b);assert.equal(writes,n);
});
test('roundtrip preserves history and opaque extensions',()=>{
 plan();c.S.fxPlanning.plan.extension={opaque:[1,2]};assert(record().ok);actual();
 assert(run(`fxScenarioSave({name:'Saved'})`).ok);assert(run(`fxPlanRebase('2026-02',2000,'explicit')`).ok);
 const b=clone(c.S);c.S=JSON.parse(disk);eq(c.S,b);eq(run('fxActivePlan().extension'),{opaque:[1,2]});
 assert.equal(period().ledgerEvents.length,1);assert.equal(c.S.ledgerHistory.events.length,0);
 assert.equal(c.S.fxPlanning.plan.actualHistory.length,1);
});
test('future FX envelope refuses without normalization',()=>{c.S.fxPlanning={schemaVersion:9,opaque:'preserve'};const b=clone(c.S);assert(!run(`fxScenarioSave({name:'blocked'})`).ok);eq(c.S,b);assert.equal(writes,0);});
test('observed balance can be recorded without risk reference',()=>{
 c.S.params.saldoIni=null;period().si=null;period().openingBook=null;
 assert(c.JPWLedger.record({data:'2026-01-02',resultado:10,saldo:1010}).ok);
 assert.equal(one().referenceBalance,null);assert.equal(one().saldo,1010);
});
test('explicit legacy origin correction enables provenance',()=>{
 c.S.ledger=[{id:'legacy-unresolved',data:'2026-01-02',resultado:10,saldo:1010,referenceBalance:1000}];
 const legacy=clone(c.S.ledger),b=clone(c.S),n=writes;
 assert(!c.JPWLedger.correct('legacy-unresolved',{data:'2026-01-02',resultado:10,saldo:1010},
  {reason:'identified source',expectedVersion:0,reconcileContext:true,context:context()}).ok);
 eq(c.S,b);assert.equal(writes,n);assert.equal(rows().length,0);
 assert(c.JPWForex.state.confirmLegacyAccountSnapshot({reason:'Preserve unresolved legacy evidence',expectedEpoch:epoch}).ok);
 const snapshot=c.S.forex.accountContexts.legacy;
 assert.equal(snapshot.status,'UNRECONCILED');assert.equal(snapshot.associations[0].status,'UNRECONCILED');
 assert.equal(snapshot.source.ledger[0].accountId,undefined);eq(snapshot.source.ledger,legacy);assert.equal(rows().length,0);
 // A new explicitly identified observation can be corrected; it does not rewrite or reconcile the old evidence.
 assert(c.JPWLedger.record({data:'2026-01-02',resultado:10,saldo:1010,nota:'Explicit identified observation; legacy remains unresolved'},
  {context:context()}).ok);const row=one();assert.equal(row.accountId,'account-A');assert.equal(row.periodId,periodId);
 assert(c.JPWLedger.correct(row.id,{data:row.data,resultado:10,saldo:1010},{reason:'identified observation correction',expectedVersion:1}).ok);
 assert.equal(period().ledgerEvents[1].before.accountId,'account-A');eq(c.S.ledger,legacy);eq(snapshot.source.ledger,legacy);
});
test('empty monthly source is unavailable, not zero profit',()=>{
 const r=c.JPWLedger.monthlyActual('2026-01',context());assert.equal(r.status,'PARTIAL');assert.equal(r.profitUsd,null);
});
test('read projections and references never save',()=>{plan();const n=writes,b=JSON.stringify(c.S);run('fxActivePlan();fxOverviewLive();fxForecastTimeline(fxActivePlan());fxPlanningReferences();');assert.equal(writes,n);assert.equal(JSON.stringify(c.S),b);eq(run('fxPlanningReferences()'),{monthly:.035,annualRange:[.35,.4]});});
console.log(JSON.stringify({status:'PASS',tests},null,2));
'''
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--artifacts',type=Path);p.add_argument('--node',default=shutil.which('node') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'));a=p.parse_args()
    sources={p:(a.root/p).read_text() for p in PATHS}
    r=subprocess.run([a.node,'-e',NODE],input=json.dumps({'paths':PATHS,'sources':sources}),text=True,capture_output=True)
    if r.returncode:print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
    report=json.loads(r.stdout);report['sources']={p:hashlib.sha256(s.encode()).hexdigest() for p,s in sources.items()}
    if a.artifacts:a.artifacts.mkdir(parents=True,exist_ok=True);(a.artifacts/'ledger-planning-domain.json').write_text(json.dumps(report,indent=2))
    print(f"PASS {len(report['tests'])}/{len(report['tests'])} ledger/planning command contracts")
if __name__=='__main__':main()
