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
INPUTS = ["src/js/00-core/00-forex-policy.js", "src/js/10-domain/00-forex-engine.js", "src/js/10-domain/02-risk-calculations.js", "src/js/10-domain/01-risk-instruments.js"]
PROBE = r"""
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const sandbox={structuredClone,QUOTE_CCY:{EURUSD:'USD'},quoteToUSD:()=>1,usdPerBase:()=>1,
 instFor:()=>({name:'EURUSD',cpl:100000}),quarantineActive:()=>false};vm.createContext(sandbox);
const files=process.argv.slice(1);for(const name of files.slice(0,2))vm.runInContext(fs.readFileSync(name,'utf8'),sandbox,{filename:name});
const fx=sandbox.JPWForex;fx.state={supported:()=>sandbox.isSupported,recordContext:function(target){
 if(arguments.length&&(!target||!target.accountId||!target.periodId))return {accountId:null,periodId:null,accountInputs:null,marketInputs:null};
 const f=sandbox.S.forex,id=target?target.accountId:f.activeAccountId,a=f.accounts[id];
 const account=a&&(!target||a.periodId===target.periodId)?a:null;
 return {accountId:account?id:null,periodId:account?account.periodId:null,accountInputs:account,marketInputs:null};}};
vm.runInContext(fs.readFileSync(files[2],'utf8'),sandbox,{filename:files[2]});
vm.runInContext(fs.readFileSync(files[3],'utf8'),sandbox,{filename:files[3]});
const rows=[];function test(name,fn){try{reset();fn();rows.push({name,result:'PASS'});}catch(error){rows.push({name,result:'PRODUCT_FAIL',error:String(error.stack||error)});}}
function reset(){sandbox.isSupported=true;sandbox.S={instruments:[{name:'EURUSD',cpl:100000,preco:1}],accounts:[{forexAccountId:'A',tipo:'MESTRE'},{forexAccountId:'B',tipo:'MESTRE'}],phases:[{orders:[]}],forex:{schemaVersion:1,activeAccountId:'A',accounts:{A:{si:10000,equity:9700,netCashflow:0,currency:'USD',periodId:'A1',capitalNominal:12000,observedAt:'2026-09-14T12:00:00Z'}},h4Closes:[],market:null,reserves:null},activeOperation:null};}
const order=()=>({accountId:'A',periodId:'A1',currency:'USD',par:'EURUSD',tipo:'BUY',entry:1.1,sl:1,lote:.01,stopValidated:true,status:'Aberta',costs:0,costBasis:'SEPARATE_FROM_RESULT'});
function read(){const before=JSON.stringify(sandbox.S),r=fx.readModel();assert.strictEqual(JSON.stringify(sandbox.S),before);return r;}
function unknown(r){assert.notStrictEqual(r.status,'OK');assert.strictEqual(r.value,null);}
function close(a,b){assert(Math.abs(a-b)<1e-8,a+' != '+b);}
test('absent account does not imply known zero risk/commitment',()=>{sandbox.S.forex.activeAccountId=null;const m=read().metrics;unknown(m.aggregateRisk);unknown(m.committedRisk);});
test('account with explicitly empty record set yields factual zero',()=>{const m=read().metrics;close(m.aggregateRisk.value,0);close(m.committedRisk.value,0);});
test('pending active missing remains unknown, not inactive',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Pendente',amplifiesExposure:true}];unknown(read().metrics.aggregateRisk);unknown(read().metrics.committedRisk);});
test('pending explicit inactive may contribute zero',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Pendente',amplifiesExposure:true,pendingActive:false}];close(read().metrics.aggregateRisk.value,0);});
test('pending explicit active amplifier contributes full risk',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Pendente',amplifiesExposure:true,pendingActive:true}];close(read().metrics.aggregateRisk.value,100);});
test('unbound historical order is retained but not reconciled to selected account',()=>{const o=order();delete o.accountId;sandbox.S.phases[0].orders=[o];const m=read();unknown(m.metrics.aggregateRisk);unknown(m.metrics.leverage);assert.strictEqual(m.orders.total,1);});
test('currency or period mismatch cannot become reconciled current risk',()=>{for(const delta of [{currency:'EUR'},{periodId:'A0'},{periodId:null},{currency:null}]){sandbox.S.phases[0].orders=[{...order(),...delta}];unknown(read().metrics.aggregateRisk);}});
test('current recorded risk does not claim prior admission snapshot',()=>{sandbox.S.phases[0].orders=[order()];const m=read().metrics;close(m.aggregateRisk.value,100);unknown(m.admissionRisk);assert.notStrictEqual(m.admissionRisk.admissionBasis,'PRE_EXECUTION_SNAPSHOT');assert(m.admissionRisk.findings.some(f=>f.code==='ADMISSION_SNAPSHOT_MISSING'));});
test('two conflicting nominal capitals require explicit reconciliation',()=>{sandbox.S.forex.reserves={accountId:'A',periodId:'A1',currency:'USD',capitalNominal:1000};const m=read().metrics.fcrRequirement;unknown(m);assert(m.findings.some(f=>f.code==='FCR_NOMINAL_CONFLICT'));});
test('matching explicit nominal capital preserves FCR arithmetic',()=>{sandbox.S.forex.reserves={accountId:'A',periodId:'A1',currency:'USD',capitalNominal:12000};close(read().metrics.fcrRequirement.value,2640);});
test('future unsupported aggregate is not interpreted using current policy',()=>{sandbox.isSupported=false;sandbox.S.forex.market={atrShort:2,atrLong:1};const m=read();unknown(m.metrics.aggregateRisk);unknown(m.metrics.vrm);assert.strictEqual(m.canRecord,false);});
test('reserve observations from another period/currency do not fund current compliance',()=>{sandbox.S.forex.reserves={accountId:'A',periodId:'A0',currency:'EUR',capitalNominal:12000,fcrConstituted:5000,feoConstituted:5000,verificationRecorded:true,verifiedAt:'2026-09-14T12:00:00Z',fcrLiquidityDays:1,feoLiquidityDays:1};const m=read();assert.strictEqual(m.reserves.totalConstituted,null);unknown(m.metrics.fcrStatus);assert(m.findings.some(f=>f.code==='RESERVE_CONTEXT_UNRESOLVED'));assert(m.reserves.unmatchedObservation);});
test('explicit unknown account/period never falls back to selected account',()=>{unknown(fx.readModel(null).metrics.drawdown);unknown(fx.readModel({accountId:'MISSING',periodId:'A1'}).metrics.drawdown);unknown(fx.readModel({accountId:'A',periodId:'A0'}).metrics.drawdown);});
test('explicit recorded other account returns its phase, not selected phase',()=>{sandbox.S.forex.accounts.B={...sandbox.S.forex.accounts.A,periodId:'B1',equity:8500};const m=fx.readModel({accountId:'B',periodId:'B1'});assert.strictEqual(m.accountId,'B');close(m.metrics.drawdown.value,15);assert.strictEqual(m.accountPhase.value,5);});
test('order risk and notional keep recorded USD context when BRL account selected',()=>{sandbox.S.forex.accounts.B={...sandbox.S.forex.accounts.A,currency:'BRL',usdToAccountRate:5,periodId:'B1'};sandbox.S.forex.activeAccountId='B';close(sandbox.orderRisk(order()),100);close(sandbox.orderNotional(order()),1000);});
test('order risk and notional use explicit BRL context, not selected USD',()=>{sandbox.S.forex.accounts.B={...sandbox.S.forex.accounts.A,currency:'BRL',usdToAccountRate:5,periodId:'B1'};const o={...order(),accountId:'B',periodId:'B1',currency:'BRL'};close(sandbox.orderRisk(o),500);close(sandbox.orderNotional(o),5000);});
test('order adapters reject missing account/period/currency instead of current fallback',()=>{for(const delta of [{accountId:null},{periodId:null},{currency:null},{currency:'BRL'},{accountId:'MISSING'}]){const o={...order(),...delta};assert.strictEqual(sandbox.orderRisk(o),null);assert.strictEqual(sandbox.orderNotional(o),null);}});
test('legacy Active and unclassified populated order cannot silently imply zero exposure',()=>{for(const status of ['Active','']){sandbox.S.phases[0].orders=[{...order(),status}];const m=read();unknown(m.metrics.aggregateRisk);unknown(m.metrics.leverage);assert.strictEqual(m.orders.total,1);assert(m.findings.some(f=>f.code==='ORDER_STATUS_UNRESOLVED'));}});
test('explicit filled draft is not an operational fact and is never promoted on read',()=>{sandbox.S.phases[0].orders=[{...order(),status:'',recordStatus:'draft'}];const m=read();close(m.metrics.aggregateRisk.value,0);assert.strictEqual(m.orders.total,0);});

function moneyProjection(){sandbox.activeRiskMatrix=()=>Array.from({length:6},(_,i)=>({nome:'F'+(i+1),alav:1}));sandbox.activeProfileFator=()=>1;sandbox.activeMDDLimit=()=>.22;fx.state.read=()=>fx.readModel();return sandbox.compute();}
test('draft conflicting with operational or legacy status stays visible and unresolved',()=>{for(const status of ['Aberta','Fechada','Pendente','Active']){sandbox.S.phases[0].orders=[{...order(),status,recordStatus:'draft',result:100}];const m=read();unknown(m.metrics.aggregateRisk);unknown(m.metrics.committedRisk);unknown(m.metrics.leverage);assert.strictEqual(m.orders.total,1);assert(m.findings.some(f=>f.code==='ORDER_STATUS_UNRESOLVED'));assert.strictEqual(moneyProjection().netOp,null);}});
test('unknown nonempty order status does not disappear as no exposure',()=>{sandbox.S.phases[0].orders=[{...order(),status:'UNRECOGNIZED_LEGACY'}];const m=read();unknown(m.metrics.aggregateRisk);assert.strictEqual(m.orders.total,1);});
test('voided fact is not resurrected by status conflict handling',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Aberta',recordStatus:'voided'}];const m=read();assert.strictEqual(m.orders.total,0);close(m.metrics.aggregateRisk.value,0);});
test('money projection refuses unreconciled historical currency instead of selected USD',()=>{for(const delta of [{currency:'BRL'},{currency:null},{accountId:null},{periodId:'A0'}]){sandbox.S.phases[0].orders=[{...order(),status:'Fechada',result:100,...delta}];const c=moneyProjection();assert.strictEqual(c.netOp,null);assert.strictEqual(c.resultadoBrutoPositivoFactual,null);}});
test('known closed zero remains factual zero in matching monetary context',()=>{sandbox.S.phases[0].orders=[{...order(),status:'Fechada',result:0}];assert.strictEqual(moneyProjection().netOp,0);});
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
