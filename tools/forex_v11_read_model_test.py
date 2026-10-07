#!/usr/bin/env python3
"""Pure V11 contract tests. Synthetic inputs, Node VM, no browser/storage/network.

Oracles fixed before implementation: PDF V11 pp32/36/51/54/66/69-72/86-91;
Anexo JPW-ANNEX-T03 and campaign reference-oracles-before-implementation.json.
An arithmetic PASS is not financial homologation or permission to execute.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
INPUTS = [
    "src/js/00-core/00-forex-policy.js",
    "src/js/10-domain/00-forex-engine.js",
    "src/js/00-core/01-risk-profiles.js",
    "src/js/10-domain/01-risk-instruments.js",
    "src/js/10-domain/00-forex-state.js",
    "src/js/10-domain/02-risk-calculations.js",
    "src/js/10-domain/18-execution-board-model.js"
]
PROBE = r"""
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
// Only host dependencies are doubles. State, conversions, policy and arithmetic
// are the production implementations; a write during any case is an error.
const sandbox={structuredClone,crypto:require('crypto').webcrypto,quarantineActive:()=>false,
 emptyOrders:n=>Array.from({length:n},()=>({id:'',par:'',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,result:null,status:''})),
 jpWealthPersistenceEpoch:()=>1,jpWealthPersistenceOutcomeIsUnknown:()=>sandbox.__unknown,addEventListener:()=>{},save:()=>{sandbox.__writes++;throw Error('Read-only test attempted persistence');}};
sandbox.__writes=0;vm.createContext(sandbox);
const files=process.argv.slice(1);for(const name of files)vm.runInContext(fs.readFileSync(name,'utf8'),sandbox,{filename:name});
const fx=sandbox.JPWForex;
const rows=[];function test(name,fn){try{reset();fn();assert.strictEqual(sandbox.__writes,0);rows.push({name,result:'PASS'});}catch(error){rows.push({name,result:'PRODUCT_FAIL',error:String(error.stack||error)});}}
function instrumentObservation(accountId,periodId,currency,rate){return {id:'synthetic-'+accountId,recordedAt:'2026-09-14T12:00:00Z',accountId,periodId,currency,instrumentId:'EURUSD',revision:1,
 price:{value:1,source:'synthetic manual',sourceKind:'MANUAL',observedAt:'2026-09-14T12:00:00Z'},
 contract:{contractSize:100000,source:'synthetic contract',sourceKind:'MANUAL',observedAt:'2026-09-14T12:00:00Z'},
 conversion:{quoteToAccountRate:rate,baseToAccountRate:rate,source:'synthetic conversion',sourceKind:'MANUAL',observedAt:'2026-09-14T12:00:00Z'}};}
// Canonical recorded periods are supplied explicitly. Existing legacy order
// scenarios retain the production read bridge through their captured identity;
// no selected account is inferred onto unbound history or written during reads.
function fixturePeriod(accountId,periodId,currency){return {accountId,periodId,currency,startedAt:'2026-09-01',si:10000,openingBook:10000,
 phases:[],activeOperation:null,ledger:[],ledgerEvents:[],revision:1};}
function reset(){sandbox.__writes=0;sandbox.__unknown=false;sandbox.S={instruments:[{name:'EURUSD',cpl:100000,preco:1}],accounts:[{forexAccountId:'A',tipo:'MESTRE'},{forexAccountId:'B',tipo:'SATELITE'}],phases:[{orders:[]}],forex:fx.state.empty(),activeOperation:{operationId:'synthetic-legacy-operation',recordContext:{accountId:'A',periodId:'A1',accountInputs:{currency:'USD'}}},period:{profile:'base'}};
 const f=sandbox.S.forex;f.activeAccountId='A';f.accounts={A:{si:10000,equity:9700,netCashflow:0,currency:'USD',periodId:'A1',capitalNominal:12000,observedAt:'2026-09-14T12:00:00Z'}};
 f.instrumentContexts={schemaVersion:1,records:[instrumentObservation('A','A1','USD',1),instrumentObservation('B','B1','BRL',5)]};
 f.accountContexts.accounts={A:{accountId:'A',currentPeriodId:'A1',periods:{A1:fixturePeriod('A','A1','USD')}},B:{accountId:'B',currentPeriodId:'B1',periods:{B1:fixturePeriod('B','B1','BRL')}}};
 assert.strictEqual(fx.state.supported(),true);assert.strictEqual(fx.state.selectOperationalContext('A','A1').ok,true);}
const order=()=>({accountId:'A',periodId:'A1',currency:'USD',par:'EURUSD',tipo:'BUY',entry:1.1,sl:1,lote:.01,stopValidated:true,status:'Aberta',costs:0,costBasis:'SEPARATE_FROM_RESULT'});
function read(...args){const before=JSON.stringify(sandbox.S),r=fx.readModel(...args);assert.strictEqual(JSON.stringify(sandbox.S),before);assert.strictEqual(sandbox.__writes,0);return r;}
function unknown(r){assert.notStrictEqual(r.status,'OK');assert.strictEqual(r.value,null);}
function close(a,b){assert(Math.abs(a-b)<1e-8,a+' != '+b);}
test('absent account does not imply known zero risk/commitment',()=>{sandbox.S.forex.activeAccountId=null;sandbox.S.accounts=[];const m=read().metrics;unknown(m.aggregateRisk);unknown(m.committedRisk);});
test('account with explicitly empty record set yields factual zero',()=>{const m=read().metrics;close(m.aggregateRisk.value,0);close(m.committedRisk.value,0);});
test('pending active missing remains unknown, not inactive',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Pendente',amplifiesExposure:true}];unknown(read().metrics.aggregateRisk);unknown(read().metrics.committedRisk);});
test('pending explicit inactive may contribute zero',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Pendente',amplifiesExposure:true,pendingActive:false}];close(read().metrics.aggregateRisk.value,0);});
test('pending explicit active amplifier contributes full risk',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Pendente',amplifiesExposure:true,pendingActive:true}];close(read().metrics.aggregateRisk.value,100);});
test('unbound historical order is retained but not reconciled to selected account',()=>{const o=order();delete o.accountId;sandbox.S.phases[0].orders=[o];const m=read();unknown(m.metrics.aggregateRisk);unknown(m.metrics.leverage);assert.strictEqual(m.orders.total,1);});
test('currency or period mismatch cannot become reconciled current risk',()=>{for(const delta of [{currency:'EUR'},{periodId:'A0'},{periodId:null},{currency:null}]){sandbox.S.phases[0].orders=[{...order(),...delta}];unknown(read().metrics.aggregateRisk);}});
test('current recorded risk does not claim prior admission snapshot',()=>{sandbox.S.phases[0].orders=[order()];const m=read().metrics;close(m.aggregateRisk.value,100);unknown(m.admissionRisk);assert.notStrictEqual(m.admissionRisk.admissionBasis,'PRE_EXECUTION_SNAPSHOT');assert(m.admissionRisk.findings.some(f=>f.code==='ADMISSION_SNAPSHOT_MISSING'));});
test('two conflicting nominal capitals require explicit reconciliation',()=>{sandbox.S.forex.reserves={accountId:'A',periodId:'A1',currency:'USD',capitalNominal:1000};const m=read().metrics.fcrRequirement;unknown(m);assert(m.findings.some(f=>f.code==='FCR_NOMINAL_CONFLICT'));});
test('matching explicit nominal capital preserves FCR arithmetic',()=>{sandbox.S.forex.reserves={accountId:'A',periodId:'A1',currency:'USD',capitalNominal:12000};close(read().metrics.fcrRequirement.value,2640);});
test('future unsupported aggregate is not interpreted using current policy',()=>{
 const variants=[()=>{sandbox.S.forex.schemaVersion=2;sandbox.S.forex.market={atrShort:2,atrLong:1};},
  ()=>{sandbox.S.forex.accountContexts={schemaVersion:9,opaque:{preserve:'synthetic-future'}};},
  ()=>{sandbox.S.forex.accountContexts={schemaVersion:1,revision:0,accounts:null};},
  ()=>{sandbox.S.forex.accountContexts={schemaVersion:1,revision:0,accounts:[]};}];
 for(const variant of variants)for(const unknownWrite of [false,true]){
  reset();variant();sandbox.__unknown=unknownWrite;const before=JSON.stringify(sandbox.S);
  const m=read(),selection=fx.state.operationalSelection(),profile=fx.state.accountProfileContext({accountId:'A',periodId:'A1'});
  unknown(m.metrics.aggregateRisk);unknown(m.metrics.vrm);assert.strictEqual(m.canRecord,false);
  assert.strictEqual(selection.accountId,null);assert.strictEqual(selection.periodId,null);assert.strictEqual(selection.reason,'FOREX_SCHEMA_UNSUPPORTED');
  assert.strictEqual(profile.status,'NOT_COMPUTABLE');assert.strictEqual(profile.current,null);assert.strictEqual(profile.period,null);
  assert.strictEqual(JSON.stringify(sandbox.S),before);assert.strictEqual(sandbox.__writes,0);assert.strictEqual(sandbox.__unknown,unknownWrite);
 }
});
test('reserve observations from another period/currency do not fund current compliance',()=>{
 for(const delta of [{periodId:'A0',currency:'EUR'},{periodId:'A1',currency:'EUR'}]){
  sandbox.S.forex.reserves={accountId:'A',...delta,capitalNominal:12000,fcrConstituted:5000,feoConstituted:5000,verificationRecorded:true,verifiedAt:'2026-09-14T12:00:00Z',fcrLiquidityDays:1,feoLiquidityDays:1};
  const preserved=JSON.stringify(sandbox.S.forex.reserves),m=read();assert.strictEqual(m.reserves.totalConstituted,null);unknown(m.metrics.fcrStatus);unknown(m.metrics.feoStatus);
  assert.strictEqual(JSON.stringify(sandbox.S.forex.reserves),preserved);
  if(delta.periodId==='A1'){assert(m.findings.some(f=>f.code==='RESERVE_CONTEXT_UNRESOLVED'));assert(m.reserves.unmatchedObservation);}
  else {assert.strictEqual(m.reserves.unmatchedObservation,null);assert.strictEqual(Object.keys(m.reserves.observations).length,0);}
 }
});
test('explicit unknown account/period never falls back to selected account',()=>{unknown(read(null).metrics.drawdown);unknown(read({accountId:'MISSING',periodId:'A1'}).metrics.drawdown);unknown(read({accountId:'A',periodId:'A0'}).metrics.drawdown);});
test('explicit recorded other account returns its phase, not selected phase',()=>{sandbox.S.forex.accounts.B={...sandbox.S.forex.accounts.A,periodId:'B1',equity:8500};const m=read({accountId:'B',periodId:'B1'});assert.strictEqual(m.accountId,'B');close(m.metrics.drawdown.value,15);assert.strictEqual(m.accountPhase.value,5);});
test('order risk and notional keep recorded USD context when BRL account selected',()=>{sandbox.S.forex.accounts.B={...sandbox.S.forex.accounts.A,currency:'BRL',usdToAccountRate:5,periodId:'B1'};sandbox.S.forex.activeAccountId='B';assert.strictEqual(fx.state.selectOperationalContext('B','B1').ok,true);close(sandbox.orderRisk(order()),100);close(sandbox.orderNotional(order()),1000);});
test('order risk and notional use explicit BRL context, not selected USD',()=>{sandbox.S.forex.accounts.B={...sandbox.S.forex.accounts.A,currency:'BRL',usdToAccountRate:5,periodId:'B1'};const o={...order(),accountId:'B',periodId:'B1',currency:'BRL'};close(sandbox.orderRisk(o),500);close(sandbox.orderNotional(o),5000);});
test('order adapters reject missing account/period/currency instead of current fallback',()=>{for(const delta of [{accountId:null},{periodId:null},{currency:null},{currency:'BRL'},{accountId:'MISSING'}]){const o={...order(),...delta};assert.strictEqual(sandbox.orderRisk(o),null);assert.strictEqual(sandbox.orderNotional(o),null);}});
test('legacy Active and unclassified populated order cannot silently imply zero exposure',()=>{for(const status of ['Active','']){sandbox.S.phases[0].orders=[{...order(),status}];const m=read();unknown(m.metrics.aggregateRisk);unknown(m.metrics.leverage);assert.strictEqual(m.orders.total,1);assert(m.findings.some(f=>f.code==='ORDER_STATUS_UNRESOLVED'));}});
test('explicit filled draft is not an operational fact and is never promoted on read',()=>{sandbox.S.phases[0].orders=[{...order(),status:'',recordStatus:'draft'}];const m=read();close(m.metrics.aggregateRisk.value,0);assert.strictEqual(m.orders.total,0);});

function moneyProjection(){const before=JSON.stringify(sandbox.S);const result=sandbox.compute();assert.strictEqual(JSON.stringify(sandbox.S),before);assert.strictEqual(sandbox.__writes,0);return result;}
test('draft conflicting with operational or legacy status stays visible and unresolved',()=>{for(const status of ['Aberta','Fechada','Pendente','Active']){sandbox.S.phases[0].orders=[{...order(),status,recordStatus:'draft',result:100}];const m=read();unknown(m.metrics.aggregateRisk);unknown(m.metrics.committedRisk);unknown(m.metrics.leverage);assert.strictEqual(m.orders.total,1);assert(m.findings.some(f=>f.code==='ORDER_STATUS_UNRESOLVED'));assert.strictEqual(moneyProjection().netOp,null);}});
test('unknown nonempty order status does not disappear as no exposure',()=>{sandbox.S.phases[0].orders=[{...order(),status:'UNRECOGNIZED_LEGACY'}];const m=read();unknown(m.metrics.aggregateRisk);assert.strictEqual(m.orders.total,1);});
test('voided fact is not resurrected by status conflict handling',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Aberta',recordStatus:'voided'}];const m=read();assert.strictEqual(m.orders.total,0);close(m.metrics.aggregateRisk.value,0);});
test('money projection refuses unreconciled historical currency instead of selected USD',()=>{for(const delta of [{currency:'BRL'},{currency:null},{accountId:null},{periodId:'A0'}]){sandbox.S.phases[0].orders=[{...order(),status:'Fechada',result:100,...delta}];const c=moneyProjection();assert.strictEqual(c.netOp,null);assert.strictEqual(c.resultadoBrutoPositivoFactual,null);}});
test('known closed zero remains factual zero in matching monetary context',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Fechada',result:0}];assert.strictEqual(moneyProjection().netOp,0);});
function scopedAtr(short=0,long=1){sandbox.S.forex.instrumentContexts.records[0].atr={short,long,timeframe:'H4',unit:'PRICE',source:'synthetic H4',sourceKind:'MANUAL',observedAt:'2026-09-14T12:00:00Z'};}
test('global ATR remains unassigned even with one declared genesis instrument',()=>{sandbox.S.forex.market={atrShort:2,atrLong:1};sandbox.S.phases[0].orders=[{...order(),role:'GENESIS'}];unknown(read().metrics.vrm);});
test('explicit genesis instrument scoped ATR preserves the zero VRM oracle',()=>{scopedAtr();sandbox.S.phases[0].orders=[{...order(),role:'GENESIS'}];close(read().metrics.vrm.value,0);});
test('ATR for another account period or instrument never substitutes the genesis observation',()=>{
 for(const changes of [{accountId:'C'},{periodId:'OLD'},{instrumentId:'GBPUSD'}]){reset();scopedAtr();Object.assign(sandbox.S.forex.instrumentContexts.records[0],changes);sandbox.S.phases[0].orders=[{...order(),role:'GENESIS'}];unknown(read().metrics.vrm);}
});
test('ambiguous or absent genesis cannot select one market observation silently',()=>{
 scopedAtr();sandbox.S.phases[0].orders=[{...order(),role:'OTHER'}];unknown(read().metrics.vrm);
 sandbox.S.phases[0].orders=[{...order(),role:'GENESIS'},{...order(),role:'GENESIS'}];unknown(read().metrics.vrm);
});
test('wrong ATR timeframe or unit remains not computable',()=>{
 for(const changes of [{timeframe:'D1'},{unit:'PERCENT'}]){reset();scopedAtr();Object.assign(sandbox.S.forex.instrumentContexts.records[0].atr,changes);sandbox.S.phases[0].orders=[{...order(),role:'GENESIS'}];unknown(read().metrics.vrm);}
});
const failed=rows.filter(r=>r.result!=='PASS');console.log(JSON.stringify({checks:rows,counts:{total:rows.length,passed:rows.length-failed.length,failed:failed.length},result:failed.length?'PRODUCT_FAIL':'PASS'}));process.exitCode=failed.length?1:0;
"""

def run(root=ROOT):
    paths = [root / name for name in INPUTS]
    before = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in zip(INPUTS, paths)}
    node = shutil.which("node")
    if not node:
        raise RuntimeError("ENVIRONMENT_ERROR: existing Node executable unavailable")
    completed = subprocess.run([node, "-e", PROBE, *map(str, paths)], text=True, capture_output=True, cwd=root)
    after = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in zip(INPUTS, paths)}
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"result": "PRODUCT_FAIL", "counts": None, "stdout": completed.stdout}
    payload.update({"root": str(root), "inputs_before": before, "inputs_after": after,
                    "source_unchanged": before == after, "returncode": completed.returncode,
                    "stderr": completed.stderr, "environment": "Node VM; no DOM, storage or network supplied",
                    "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    if before != after:
        payload["result"] = "PRODUCT_FAIL"
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out and args.out.exists():
        parser.error("Evidence exists; choose a new output instead of overwriting it")
    try:
        payload = run(args.root.resolve())
    except (OSError, RuntimeError) as error:
        payload = {"result": "ENVIRONMENT_ERROR", "error": str(error)}
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        with args.out.open("x") as output:
            output.write(serialized + "\n")
    print(serialized)
    return 0 if payload["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
