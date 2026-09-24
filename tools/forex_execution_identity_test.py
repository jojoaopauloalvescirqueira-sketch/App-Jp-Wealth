#!/usr/bin/env python3
"""Synthetic contracts for broker identity and declared Raiz-N inputs.
Uses the real Forex command/validation layer in an isolated Node VM. The writer
stub records state and exercises refusal/UNKNOWN without real operator data.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
PROBE = r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const box={structuredClone,crypto,console,Date,addEventListener:()=>{},forexNewOperationPhases:()=>[{orders:[{id:'',par:'',tipo:'BUY',status:''}]}],
  jpWealthPersistenceEpoch:()=>1,jpWealthPersistenceOutcomeIsUnknown:()=>box.unknown,
  markJPWealthPersistenceOutcomeUnknown:()=>box.unknown=true,dgLogChange:()=>{}};
box.globalThis=box;vm.createContext(box);
for(const file of process.argv.slice(1))vm.runInContext(fs.readFileSync(file,'utf8'),box,{filename:file});
const fx=box.JPWForex,api=fx.state,results=[];
fx.orderInputs=()=>({});
box.operationValidateOrder=o=>o.brokerHash!=null&&typeof o.brokerHash!=='string'?'Invalid hash':null;
function test(name,fn){try{setup();fn();results.push({name,result:'PASS'});}catch(e){results.push({name,result:'PRODUCT_FAIL',error:String(e.stack||e)});}}
function setup(){box.unknown=false;box.writes=0;box.mode='normal';box.S={accounts:[{forexAccountId:'A',tipo:'MESTRE',platformCurrency:'USD'}],
 instruments:[{name:'EURUSD'}],dataGovernance:{changeLog:[]},forex:api.empty(),operationHistory:{schemaVersion:1,records:[]}};
 box.S.forex.accountContexts.accounts.A={accountId:'A',currentPeriodId:'P',periods:{P:{accountId:'A',periodId:'P',currency:'USD',startedAt:'2026-01-01',si:10000,openingBook:10000,
 phases:[{orders:[{id:'',par:'',tipo:'BUY',status:''}]}],ledger:[],ledgerEvents:[],activeOperation:null,revision:1}}};
 box.save=()=>{box.writes++;if(box.mode==='refuse')return false;if(box.mode==='unknown')return undefined;box.persisted=JSON.stringify(box.S);return true;};
 assert(api.supported());box.persisted=JSON.stringify(box.S);}
const rows=()=>box.S.forex.accountContexts.accounts.A.periods.P.phases[0].orders;
const record=(changes,reason='Synthetic identity fact')=>api.recordAccountOrders([{pi:0,oi:0,changes}],{accountId:'A',periodId:'P',reason,expectedEpoch:1});
const hash='0009007199254740993123456789-XyZ';
const fact={id:'INTERNAL-01',brokerHash:hash,par:'EURUSD',tipo:'BUY',status:'Aberta'};
const declaration=(delta={})=>({accountId:'A',periodId:'P',instrumentId:'EURUSD',expectedRevision:0,oneWeek:{n:25,f:1.5},twoWeeks:{n:50,f:2},declaredBy:'Synthetic operator',declaredAt:'2026-09-01T00:00:00Z',...delta});
const write=d=>api.recordExecutionDiagnostics(d,{reason:'Synthetic diagnostic declaration',expectedEpoch:1});
const snap=()=>JSON.stringify(box.S);
function ok(r){assert.strictEqual(r.ok,true,JSON.stringify(r));}
function refused(fn){const before=snap(),saved=box.persisted,writes=box.writes;const r=fn();assert.strictEqual(r.ok,false,JSON.stringify(r));assert.strictEqual(snap(),before);assert.strictEqual(box.persisted,saved);assert.strictEqual(box.writes,writes);return r;}
test('new open and closed require separate internal ID and opaque HASH',()=>{
 refused(()=>record({...fact,id:''}));refused(()=>record({...fact,brokerHash:''}));refused(()=>record({...fact,status:'Fechada',result:0,brokerHash:null}));
 ok(record(fact));assert.strictEqual(rows()[0].brokerHash,hash);assert.strictEqual(rows()[0].identityContractVersion,1);assert.notStrictEqual(rows()[0].orderId,hash);
});
test('new pending needs ID but HASH may wait until opening',()=>{
 refused(()=>record({...fact,id:'',brokerHash:null,status:'Pendente'}));ok(record({...fact,brokerHash:null,status:'Pendente'}));
 refused(()=>record({status:'Aberta'}));ok(record({status:'Aberta',brokerHash:hash}));assert.strictEqual(rows()[0].brokerHash,hash);
});
test('legacy factual record can correct and close without fabricated identity',()=>{
 rows()[0]={id:'OLD',par:'EURUSD',tipo:'BUY',status:'Aberta',recordStatus:'recorded',accountId:'A',periodId:'P',currency:'USD',operationId:'OLDOP',recordVersion:1};
 box.S.forex.accountContexts.accounts.A.periods.P.activeOperation={operationId:'OLDOP',recordContext:{accountId:'A',periodId:'P'}};
 ok(record({lote:1}));ok(record({status:'Fechada',result:0}));assert.strictEqual(rows()[0].brokerHash,undefined);assert.strictEqual(rows()[0].identityContractVersion,undefined);
});
test('HASH remains opaque across revision and serialized reload',()=>{
 ok(record(fact));ok(record({brokerHash:'000-SECOND'}));const r=rows()[0];assert.strictEqual(r.revisions[1].before.brokerHash,hash);assert.strictEqual(r.revisions[1].after.brokerHash,'000-SECOND');
 box.S=JSON.parse(box.persisted);assert(api.supported());assert.strictEqual(rows()[0].brokerHash,'000-SECOND');
});
test('new draft marker does not require IDs until confirmation',()=>{
 ok(api.addAccountOrderDraft({accountId:'A',periodId:'P',pi:0},{expectedEpoch:1}));assert.strictEqual(rows()[1].identityContractVersion,1);assert(api.supported());
});
test('numeric HASH and removal of required identity refused without writes',()=>{
 refused(()=>record({...fact,brokerHash:123}));ok(record(fact));refused(()=>record({brokerHash:null}));refused(()=>record({id:''}));
});
test('legacy absence and optional diagnostics never write on read',()=>{
 const before=snap(),count=box.writes;assert.strictEqual(api.executionDiagnostics({accountId:'A',periodId:'P',instrumentId:'EURUSD'}).status,'NOT_COMPUTABLE');assert.strictEqual(snap(),before);assert.strictEqual(box.writes,count);
});
test('diagnostic horizons are explicit independent and revisioned',()=>{
 ok(write(declaration({twoWeeks:null})));let d=api.executionDiagnostics({accountId:'A',periodId:'P',instrumentId:'EURUSD'});assert.strictEqual(d.value.oneWeek.n,25);assert.strictEqual(d.value.twoWeeks,null);
 const next=declaration({expectedRevision:1,twoWeeks:{n:60,f:1.7}});delete next.oneWeek;ok(write(next));d=api.executionDiagnostics({accountId:'A',periodId:'P',instrumentId:'EURUSD'});
 assert.strictEqual(d.revision,2);assert.strictEqual(d.value.oneWeek.n,25);assert.strictEqual(d.value.twoWeeks.n,60);assert.strictEqual(d.value.previous.twoWeeks,null);
 ok(write(declaration({expectedRevision:2,oneWeek:null,twoWeeks:null})));assert(api.supported());
});
test('diagnostic malformed values and stale identity are refused',()=>{
 for(const delta of [{oneWeek:{n:0,f:1}},{oneWeek:{n:2.5,f:1}},{oneWeek:{n:25,f:0}},{oneWeek:{n:25,f:NaN}},{declaredBy:''},{declaredAt:'2099-01-01'},{accountId:'B'},{periodId:'NO'},{instrumentId:'NO'},{expectedRevision:1}])refused(()=>write(declaration(delta)));
});
test('diagnostic revision/epoch conflicts preserve confirmed declaration',()=>{
 ok(write(declaration()));refused(()=>write(declaration()));refused(()=>api.recordExecutionDiagnostics(declaration({expectedRevision:1}),{reason:'Synthetic',expectedEpoch:0}));
});
test('writer refusal restores diagnostics and audit; retry is explicit',()=>{
 const before=snap();box.mode='refuse';const a=write(declaration());assert.strictEqual(a.ok,false);assert.strictEqual(snap(),before);assert.strictEqual(box.writes,1);
 box.mode='normal';ok(write(declaration()));assert.strictEqual(api.executionDiagnostics({accountId:'A',periodId:'P',instrumentId:'EURUSD'}).revision,1);
});
test('unknown writer outcome blocks blind repeat',()=>{
 box.mode='unknown';const a=write(declaration());assert.strictEqual(a.persistido,null);assert(box.unknown);const count=box.writes;const b=write(declaration({expectedRevision:1}));assert.strictEqual(b.ok,false);assert.strictEqual(box.writes,count);
});
test('order capture freezes declaration while current diagnostics evolve',()=>{
 ok(write(declaration()));ok(record(fact));const snapshot=JSON.stringify(rows()[0].calculationInputs.executionDiagnostics);
 ok(write(declaration({expectedRevision:1,oneWeek:{n:30,f:2}})));assert.strictEqual(JSON.stringify(rows()[0].calculationInputs.executionDiagnostics),snapshot);
 const history={ordersSnapshot:structuredClone(rows())};box.S.operationHistory.records.push(history);assert(api.validateExecutionExtensions(box.S));
 history.ordersSnapshot[0].calculationInputs.executionDiagnostics.accountId='OTHER';assert.strictEqual(api.validateExecutionExtensions(box.S),false);
});
test('backup validators accept absent extension and reject malformed added data',()=>{
 assert(api.validateExecutionExtensions(box.S));ok(write(declaration()));assert(api.supported(JSON.parse(JSON.stringify(box.S.forex))));
 const bad=structuredClone(box.S.forex);bad.executionDiagnostics.records[0].oneWeek.n=-1;assert.strictEqual(api.supported(bad),false);
 const duplicate=structuredClone(box.S.forex);duplicate.executionDiagnostics.records.push(structuredClone(duplicate.executionDiagnostics.records[0]));assert.strictEqual(api.supported(duplicate),false);
 const future=structuredClone(box.S.forex);future.executionDiagnostics.schemaVersion=99;assert.strictEqual(api.supported(future),false);
 box.S.operationHistory.records=[{ordersSnapshot:[{brokerHash:123}]}];assert.strictEqual(api.validateExecutionExtensions(box.S),false);
});
process.stdout.write(JSON.stringify(results));
"""

def browser_roundtrip():
    from functools import partial
    from http.server import ThreadingHTTPServer
    import threading
    from playwright.sync_api import sync_playwright
    import notes_launcher_test as fixture
    from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
    class FixtureServer(ThreadingHTTPServer):
        request_queue_size=128
        daemon_threads=True
    server=FixtureServer(('127.0.0.1',0),partial(fixture.Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(**fixture.launch_options())
            def fresh():
                ctx=browser.new_context(service_workers='block');install_bootstrap(ctx)
                page=ctx.new_page();page.on('dialog',lambda dialog:dialog.accept())
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page)
                page.wait_for_function("typeof $==='function' && typeof render==='function' && typeof importFullBackupFile==='function' && !!window.JPWForex?.state?.recordExecutionDiagnostics")
                page.evaluate('closeModal();window.__onbShown=true;window.confirm=()=>true');return ctx,page
            a,first=fresh()
            payload=first.evaluate('''async()=>{
              const instruments=structuredClone(S.instruments);S=structuredClone(DEFAULTS);migrate();S.instruments=instruments;
              S.onboarding.done=true;S.executionIdentityProbe='synthetic';S.accounts=[{forexAccountId:'IDENTITY-A',nome:'Synthetic',tipo:'MESTRE',platformCurrency:'USD'}];
              S.forex=JPWForex.state.empty();const api=JPWForex.state;
              const period=api.recordAccountPeriod({accountId:'IDENTITY-A',startedAt:'2026-01-01',currency:'USD',si:10000,openingBook:10000,source:'Synthetic',activateCurrentPeriod:true},{reason:'Synthetic'});
              if(!period.ok)throw Error(period.error);const scope=api.operationalSelection();
              const d=api.recordExecutionDiagnostics({...scope,instrumentId:'EURUSD',expectedRevision:0,oneWeek:{n:25,f:1.5},twoWeeks:null,declaredBy:'Synthetic',declaredAt:'2026-09-01T00:00:00Z'},{reason:'Synthetic',expectedEpoch:jpWealthPersistenceEpoch()});
              if(!d.ok)throw Error(d.error);
              const o=api.recordAccountOrders([{pi:0,oi:0,changes:{id:'MANUAL-1',brokerHash:'0009007199254740993123456789',par:'EURUSD',tipo:'BUY',status:'Aberta',lote:.01,entry:1.1,sl:1.09}}],{...scope,reason:'Synthetic',expectedEpoch:jpWealthPersistenceEpoch()});
              if(!o.ok)throw Error(o.error);
              return JSON.parse(await dgBuildBackupBlob(12,'synthetic.json','2026-09-22T00:00:00Z').text());
            }''')
            first.reload();wait_bootstrap(first)
            assert first.evaluate("JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases[0].orders[0].brokerHash")=='0009007199254740993123456789'
            b,second=fresh()
            second.evaluate('data=>importFullBackupFile(new File([JSON.stringify(data)],"synthetic.json",{type:"application/json"}))',payload)
            second.wait_for_function("S.executionIdentityProbe==='synthetic'",timeout=10000)
            assert second.evaluate("JPWForex.state.executionDiagnostics({...JPWForex.state.operationalSelection(),instrumentId:'EURUSD'}).value.oneWeek.n")==25
            assert second.evaluate("JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases[0].orders[0].brokerHash")=='0009007199254740993123456789'
            checks=second.evaluate('''payload=>{
              const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),results=[];
              for(const change of [p=>p.state.forex.executionDiagnostics.records[0].oneWeek.n=0,
                p=>Object.values(p.state.forex.accountContexts.accounts['IDENTITY-A'].periods)[0].phases[0].orders[0].brokerHash=123,
                p=>p.state.forex.executionDiagnostics.schemaVersion=99]){
                const malformed=structuredClone(payload);change(malformed);let rejected=false;
                try{normalizeImportedState(malformed);}catch(e){rejected=true;}
                results.push(rejected&&JSON.stringify(S)===before&&localStorage.getItem(LSKEY)===raw);
              }
              const old=structuredClone(payload);delete old.state.forex.executionDiagnostics;
              const order=Object.values(old.state.forex.accountContexts.accounts['IDENTITY-A'].periods)[0].phases[0].orders[0];
              delete order.brokerHash;delete order.identityContractVersion;delete order.calculationInputs.executionDiagnostics;order.revisions=[];
              const restored=normalizeImportedState(old);results.push(!('executionDiagnostics' in restored.forex)&&JSON.stringify(S)===before);
              return results;
            }''',payload)
            assert all(checks),checks
            # Finalize through the real contextual writer and explicit review UI.
            # No hand-built ordersSnapshot can satisfy this end-to-end oracle.
            captured=second.evaluate('''()=>{
              const api=JPWForex.state,scope=api.operationalSelection(),context=api.accountContext(scope);
              const order=context.value.phases[0].orders[0];
              const diagnostic=structuredClone(order.calculationInputs.executionDiagnostics);
              const operationId=context.value.activeOperation.operationId;
              const closed=api.recordAccountOrders([{pi:0,oi:0,orderId:order.orderId,
                expectedVersion:order.recordVersion,changes:{status:'Fechada',result:125,costs:-5,
                  costBasis:'SEPARATE_FROM_RESULT'}}],{...scope,reason:'Synthetic confirmed closure',
                expectedEpoch:jpWealthPersistenceEpoch(),expectedRevision:context.revision});
              if(!closed.ok)throw Error(closed.error);
              if(JSON.stringify(api.accountContext(scope).value.phases[0].orders[0].calculationInputs.executionDiagnostics)!==JSON.stringify(diagnostic))
                throw Error('Closing rewrote the captured diagnostic');
              if(!JPWNavigation.navigate('forex-operation'))throw Error('Execution Board navigation refused');
              return {scope,operationId,diagnostic,brokerHash:order.brokerHash};
            }''')
            before_review=second.evaluate('({state:JSON.stringify(S),disk:localStorage.getItem(LSKEY)})')
            second.evaluate('JPWOperation.openReview()')
            assert second.locator('#finalDefenses').is_visible()
            assert second.locator('#finalConfirm').is_visible()
            assert second.evaluate('({state:JSON.stringify(S),disk:localStorage.getItem(LSKEY)})')==before_review
            second.locator('#finalDefenses').fill('0')
            second.locator('#finalConfirm').fill('FECHADO')
            second.locator('#modalConfirm').click()
            second.wait_for_function('S.operationHistory.records.length===1')
            finalized=second.evaluate('''captured=>{
              const context=JPWForex.state.accountContext(captured.scope).value,record=S.operationHistory.records[0];
              if(context.activeOperation!==null||record.operationId!==captured.operationId||record.ordersSnapshot.length!==1)
                throw Error('Finalization did not retain the selected operation identity');
              const order=record.ordersSnapshot[0];
              if(order.brokerHash!==captured.brokerHash||order.identityContractVersion!==1||record.netResult!==120||
                JSON.stringify(order.calculationInputs.executionDiagnostics)!==JSON.stringify(captured.diagnostic))
                throw Error('Finalized snapshot differs from the confirmed HASH, costs or diagnostic');
              return JSON.stringify(record);
            }''',captured)

            def verify_history(page):
                before=page.evaluate('({state:JSON.stringify(S),disk:localStorage.getItem(LSKEY)})')
                assert page.evaluate("JPWNavigation.navigate('forex-history')")
                assert page.evaluate("JPWExec.ui.getView()==='history'&&execHistory.parentElement.id==='exec'&&!contab.contains(execHistory)&&contab.hidden&&executionBoard.hidden")
                row=page.locator('[data-hist-id="'+captured['operationId']+'"]')
                row.focus();page.keyboard.press('Enter')
                detail=page.locator('[data-hist-detail="'+captured['operationId']+'"]')
                assert detail.is_visible()
                assert captured['brokerHash'] in detail.inner_text()
                assert page.evaluate('operationCopyProjection(S.operationHistory.records[0])').find(captured['brokerHash'])>=0
                assert page.evaluate('({state:JSON.stringify(S),disk:localStorage.getItem(LSKEY)})')==before

            verify_history(second)
            second.evaluate('''({captured,finalized})=>{
              const api=JPWForex.state,target={...captured.scope,instrumentId:'EURUSD'};
              const current=api.executionDiagnostics(target);
              const revised=api.recordExecutionDiagnostics({...target,expectedRevision:current.revision,
                oneWeek:{n:30,f:2},twoWeeks:{n:60,f:2.5},declaredBy:'Synthetic revised scenario',
                declaredAt:new Date().toISOString()},{reason:'Synthetic later diagnostic revision',
                expectedEpoch:jpWealthPersistenceEpoch()});
              if(!revised.ok)throw Error(revised.error);
              if(api.executionDiagnostics(target).revision!==2||JSON.stringify(S.operationHistory.records[0])!==finalized)
                throw Error('Current N/F revision changed finalized history');
            }''',{'captured':captured,'finalized':finalized})
            second.reload();wait_bootstrap(second)
            assert second.evaluate('JSON.stringify(S.operationHistory.records[0])')==finalized
            assert second.evaluate('JPWForex.state.executionDiagnostics({...JPWForex.state.operationalSelection(),instrumentId:"EURUSD"}).value.oneWeek.n')==30
            verify_history(second)
            finalized_backup=second.evaluate('''async()=>JSON.parse(await dgBuildBackupBlob(12,
              'synthetic-finalized.json','2026-09-22T00:00:00Z').text())''')
            c,third=fresh()
            third.evaluate('data=>importFullBackupFile(new File([JSON.stringify(data)],"synthetic-finalized.json",{type:"application/json"}))',finalized_backup)
            third.wait_for_function('S.operationHistory.records.length===1')
            assert third.evaluate('JSON.stringify(S.operationHistory.records[0])')==finalized
            assert third.evaluate('''()=>{const d=JPWForex.state.executionDiagnostics({...JPWForex.state.operationalSelection(),instrumentId:'EURUSD'});
              return d.revision===2&&d.value.oneWeek.n===30&&d.value.oneWeek.f===2&&
                S.operationHistory.records[0].ordersSnapshot[0].calculationInputs.executionDiagnostics.revision===1;
            }''')
            verify_history(third)
            a.close();b.close();c.close();browser.close()
            print('PASS browser writer/reload/Blob-FileReader backup roundtrip and pre-write rejection')
            print('PASS real closure/review/finalization, independent History HASH, immutable diagnostic snapshot after N/F revision, reload and finalized backup roundtrip')
    finally:server.shutdown();server.server_close()

def main():
    files=['src/js/00-core/00-forex-policy.js','src/js/00-core/01-risk-profiles.js','src/js/10-domain/00-forex-state.js']
    run=subprocess.run([NODE,'-e',PROBE,*[str(ROOT/f) for f in files]],text=True,capture_output=True)
    if run.returncode:
        print(run.stderr);return 1
    results=json.loads(run.stdout)
    for row in results:print(row['result'],row['name'],row.get('error',''))
    passed=results and all(r['result']=='PASS' for r in results)
    if passed and '--browser' in sys.argv:browser_roundtrip()
    return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
