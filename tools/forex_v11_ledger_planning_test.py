#!/usr/bin/env python3
"""Synthetic Forex ledger/planning command contracts; local Node VM, no network."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
PATHS=['src/js/00-core/00-forex-policy.js','src/js/00-core/01-risk-profiles.js','src/js/00-core/03-default-state.js','src/js/10-domain/00-forex-engine.js','src/js/10-domain/00-forex-state.js','src/js/30-accounting/01-daily-ledger.js','src/js/30-accounting/06-planning/01-engine.js','src/js/30-accounting/06-planning/02-state.js']
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
const record=()=>run(`ledgerRecord({data:'2026-01-02',resultado:10,saldo:1010})`);
const tests=[];function test(name,fn){seed();fn();tests.push({name,status:'PASS'});}
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
test('ledger revision reaches the last safe integer then refuses without writes',()=>{
 assert(record().ok);period().ledger[0].version=Number.MAX_SAFE_INTEGER-1;
 assert(c.JPWForex.state.supported());
 const input={...context(),id:one().id,action:'CORRECTED',data:'2026-01-02',resultado:20,saldo:1020};
 assert(c.JPWForex.state.recordAccountLedger(input,{reason:'Last representable revision'}).ok);
 assert.equal(one().version,Number.MAX_SAFE_INTEGER);assert(c.JPWForex.state.supported());
 const before=JSON.stringify(c.S),persisted=disk,n=writes;
 const rejected=c.JPWForex.state.recordAccountLedger({...input,resultado:30,saldo:1030},{reason:'Counter exhausted'});
 assert.equal(rejected.ok,false);assert.equal(rejected.persistido,false);
 assert.equal(JSON.stringify(c.S),before);assert.equal(disk,persisted);assert.equal(writes,n);
 assert.equal(unknown,false);assert(c.JPWForex.state.supported());
});
for(const missing of ['absent','null'])test(`derived legacy ${missing} revision becomes a safe integer only on explicit correction`,()=>{
 assert(record().ok);
 assert(c.JPWLedger.record({data:'2026-01-03',resultado:5,saldo:''}).ok);
 const derived=period().ledger.find(r=>r.data==='2026-01-03');
 if(missing==='absent')delete derived.version;else derived.version=null;
 const untouched=JSON.stringify(c.S),n=writes;
 assert(c.JPWForex.state.supported());c.JPWForex.state.accountLedger(context());
 assert.equal(JSON.stringify(c.S),untouched);assert.equal(writes,n);
 const result=c.JPWForex.state.recordAccountLedger({...context(),id:period().ledger[0].id,
  action:'CORRECTED',data:'2026-01-02',resultado:20,saldo:1020},{reason:'Explicit earlier observation correction'});
 assert(result.ok,result.error);const after=period().ledger.find(r=>r.data==='2026-01-03');
 assert.equal(after.saldo,1025);assert.equal(after.version,1);assert(Number.isSafeInteger(after.version));
 assert(c.JPWForex.state.supported());assert.equal(writes,n+1);
 const audit=period().ledgerEvents.at(-1);assert.equal(audit.action,'BALANCE_RECALCULATED');
 assert.equal(Object.hasOwn(audit.before,'version'),missing!=='absent');
 if(missing==='null')assert.equal(audit.before.version,null);
 assert.equal(audit.after.version,1);eq(JSON.parse(disk),c.S);
});
test('exhausted derived revision rolls back earlier recalculations and all audit state',()=>{
 assert(record().ok);
 assert(c.JPWLedger.record({data:'2026-01-03',resultado:5,saldo:''}).ok);
 assert(c.JPWLedger.record({data:'2026-01-04',resultado:7,saldo:''}).ok);
 period().ledger.find(r=>r.data==='2026-01-04').version=Number.MAX_SAFE_INTEGER;
 assert(c.JPWForex.state.supported());const before=JSON.stringify(c.S),persisted=disk,n=writes;
 const result=c.JPWForex.state.recordAccountLedger({...context(),id:period().ledger[0].id,
  action:'CORRECTED',data:'2026-01-02',resultado:20,saldo:1020},{reason:'Recompute a chain with exhausted last revision'});
 assert.equal(result.ok,false);assert.equal(result.persistido,false);
 assert.equal(JSON.stringify(c.S),before);assert.equal(disk,persisted);assert.equal(writes,n);
 assert.equal(unknown,false);assert(c.JPWForex.state.supported());
});
test('an unchanged derived row at the maximum revision does not block another correction',()=>{
 assert(record().ok);
 assert(c.JPWLedger.record({data:'2026-01-03',resultado:5,saldo:''}).ok);
 period().ledger.find(r=>r.data==='2026-01-03').version=Number.MAX_SAFE_INTEGER;
 const n=writes,result=c.JPWForex.state.recordAccountLedger({...context(),id:period().ledger[0].id,
  action:'CORRECTED',data:'2026-01-02',resultado:10,saldo:1010,nota:'Only a note changed'},
  {reason:'Keep the unchanged derived observation'});
 assert(result.ok,result.error);assert.equal(writes,n+1);
 assert.equal(period().ledger.find(r=>r.data==='2026-01-03').version,Number.MAX_SAFE_INTEGER);
 assert(c.JPWForex.state.supported());
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
