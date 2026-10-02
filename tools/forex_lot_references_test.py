#!/usr/bin/env python3
"""Fixed oracles for the two theoretical lot references; synthetic inputs only.

Authority: CHG-JPW-LOT-REFERENCES-20261001. The production policy, engine,
instrument identity helper and Execution Board projection run in a Node VM.
No DOM, persistence, broker order, policy activation or alternate calculator.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ["src/js/00-core/00-forex-policy.js", "src/js/10-domain/00-forex-engine.js",
          "src/js/10-domain/01-risk-instruments.js",
          "src/js/10-domain/18-execution-board-model.js"]
PROBE = r"""
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const box={structuredClone};
vm.createContext(box);
for(const file of process.argv.slice(1))vm.runInContext(fs.readFileSync(file,'utf8'),box,{filename:file});
const fx=box.JPWForex,b=fx.executionBoard,checks=[];
const fields=['initialNormal','initialRestrictive','currentNormal','currentRestrictive'];
function test(name,fn){try{fn();checks.push({name,result:'PASS'});}catch(e){checks.push({name,result:'PRODUCT_FAIL',error:String(e.stack||e)});}}
function near(actual,expected){assert.strictEqual(typeof actual,'number');assert(Number.isFinite(actual));assert(Math.abs(actual-expected)<1e-10,actual+' != '+expected);}
function unavailable(m){assert(m,'reference output missing');assert.notStrictEqual(m.status,'OK');assert.strictEqual(m.value,null);assert.strictEqual(m.baseValue,null);}
function fixture(){
 const account={periodId:'P',currency:'USD',si:10000,equity:8000,netCashflow:0,source:'Synthetic account observation',observedAt:'2026-10-01T12:00:00Z'};
 return {scope:{accountId:'A',periodId:'P',operationId:null},account,accountRecord:{currency:'USD',satu:15000},
  phases:fx.policy.phases.map(()=>({orders:[],policyVersion:fx.policy.version})),rows:[],
  instruments:[{id:'EURUSD',name:'EURUSD',price:{value:1.25,source:'Synthetic quote',kind:'MANUAL',observedAt:'2026-10-01T11:00:00Z'},
   contract:{contractSize:100000,source:'Synthetic contract',observedAt:'2026-10-01T10:00:00Z'},
   conversion:{baseToAccountRate:1.25,quoteToAccountRate:1,source:'Synthetic conversion',observedAt:'2026-10-01T11:00:00Z'},
   atr:{short:.002,long:.004,timeframe:'H4',unit:'PRICE',source:'Synthetic ATR'}}]};
}
function project(x){
 const before=JSON.stringify(x),policyBefore=JSON.stringify(fx.policy.snapshot()),m=b.project(x);
 assert.strictEqual(JSON.stringify(x),before,'projection changed its inputs');
 assert.strictEqual(JSON.stringify(fx.policy.snapshot()),policyBefore,'projection changed policy');
 return m;
}
function references(x){return project(x).instruments[0];}
test('SI10000 equity8000 notional125000 separates initial .04/.02 and current .032/.016',()=>{
 const i=references(fixture());near(i.initialNormal.value,.04);near(i.initialRestrictive.value,.02);
 near(i.currentNormal.value,.032);near(i.currentRestrictive.value,.016);
 near(i.initialNormal.baseValue,10000);near(i.currentNormal.baseValue,8000);
});
test('equity above SI cannot enlarge current cap',()=>{
 const x=fixture();x.account.equity=15000;const i=references(x);
 near(i.initialNormal.value,.04);near(i.currentNormal.value,.04);near(i.currentRestrictive.value,.02);
 near(i.currentNormal.baseValue,10000);
});
test('equal SI and equity produce equal values with distinct meanings',()=>{
 const x=fixture();x.account.equity=10000;const i=references(x);
 near(i.initialNormal.value,i.currentNormal.value);near(i.initialRestrictive.value,i.currentRestrictive.value);
 assert.strictEqual(i.initialNormal.baseKind,'SI');assert.strictEqual(i.currentNormal.baseKind,'MIN_SI_EQUITY');
 assert.strictEqual(i.initialNormal.calculationMode,'THEORETICAL_INITIAL_REFERENCE');
 assert.strictEqual(i.currentNormal.calculationMode,'THEORETICAL_CURRENT_CAP');
});
for(const equity of [null,undefined,0,-100,'8000',NaN,Infinity])test('initial availability is independent of invalid equity '+String(equity),()=>{
 const x=fixture();x.account.equity=equity;const i=references(x);
 near(i.initialNormal.value,.04);near(i.initialRestrictive.value,.02);
 unavailable(i.currentNormal);unavailable(i.currentRestrictive);unavailable(i.normal);unavailable(i.restrictive);
});
for(const si of [null,undefined,0,-100,'10000',NaN,Infinity])test('invalid SI never borrows equity or book '+String(si),()=>{
 const x=fixture();x.account.si=si;const i=references(x);fields.forEach(k=>unavailable(i[k]));
});
test('absent account never borrows book balance',()=>{const x=fixture();x.account=null;const i=references(x);fields.forEach(k=>unavailable(i[k]));});
for(const [field,value] of [['contractSize',null],['contractSize',0],['contractSize',-1],['contractSize','100000'],['baseToAccountRate',null],['baseToAccountRate',0],['baseToAccountRate',-1],['baseToAccountRate','1.25']])test('invalid identified denominator '+field+' '+String(value),()=>{
 const x=fixture();const ins=x.instruments[0];(field==='contractSize'?ins.contract:ins.conversion)[field]=value;
 const i=references(x);fields.forEach(k=>{assert(i[k]);assert.notStrictEqual(i[k].status,'OK');assert.strictEqual(i[k].value,null);});
 assert.notStrictEqual(i.notionalPerLot.status,'OK');assert.strictEqual(i.notionalPerLot.value,null);
});
test('nonfinite contract-conversion product never fabricates a zero reference',()=>{
 const x=fixture();x.instruments[0].contract.contractSize=1e308;x.instruments[0].conversion.baseToAccountRate=1e308;
 const i=references(x);fields.forEach(k=>{assert.notStrictEqual(i[k].status,'OK');assert.strictEqual(i[k].value,null);});
 assert.strictEqual(i.notionalPerLot.value,null);
});
test('notional conversion is distinct from quote conversion used for stop risk',()=>{
 const x=fixture();x.instruments[0].conversion.quoteToAccountRate=null;const i=references(x);
 near(i.initialNormal.value,.04);near(i.currentNormal.value,.032);
});
test('USD and USC equivalent observations yield the same lots without contract scaling',()=>{
 const usd=references(fixture()),x=fixture();x.account.currency='USC';x.account.si=1000000;x.account.equity=800000;x.accountRecord.currency='USC';
 x.instruments[0].conversion.baseToAccountRate=125;x.instruments[0].conversion.quoteToAccountRate=100;const usc=references(x);
 fields.forEach(k=>near(usc[k].value,usd[k].value));near(usc.notionalPerLot.value,12500000);
 assert.strictEqual(usc.notionalPerLot.currency,'USC');assert.strictEqual(usc.initialNormal.source.account.currency,'USC');
});
test('current aliases retain exact compatibility values',()=>{
 const i=references(fixture());near(i.normal.value,i.currentNormal.value);near(i.restrictive.value,i.currentRestrictive.value);
 assert.strictEqual(i.normal.baseKind,'MIN_SI_EQUITY');assert.strictEqual(i.restrictive.calculationMode,'THEORETICAL_CURRENT_CAP');
});
test('subminimum references remain theoretical and unrounded',()=>{
 const x=fixture();x.account.si=1234;x.account.equity=1000;const i=references(x);
 near(i.initialNormal.value,.004936);near(i.currentNormal.value,.004);near(i.initialRestrictive.value,.002468);
 fields.forEach(k=>{assert.strictEqual(i[k].lotMinimumEvaluated,false);assert.strictEqual(i[k].theoreticalOnly,true);assert.strictEqual(i[k].executionEligibility,'BLOCKED');});
});
test('valid initial source includes exact scope base contract conversion and parameter',()=>{
 const i=references(fixture()),s=i.initialNormal.source;
 assert.strictEqual(s.account.accountId,'A');assert.strictEqual(s.account.periodId,'P');assert.strictEqual(s.account.source,'Synthetic account observation');
 assert.strictEqual(s.account.observedAt,'2026-10-01T12:00:00Z');assert.strictEqual(s.instrumentId,'EURUSD');
 assert.strictEqual(s.contract.source,'Synthetic contract');assert.strictEqual(s.conversion.source,'Synthetic conversion');
 assert.strictEqual(s.parameter.id,'P-12b');assert.strictEqual(s.parameter.hostNorm,fx.policy.get('P-12b').hostNorm);
 assert.strictEqual(i.initialNormal.provenance.instrumentId,'EURUSD');assert.strictEqual(i.currentNormal.source.account.currency,'USD');
});
test('horizons and ATR changes never change either lot reference',()=>{
 const x=fixture(),before=references(x);x.instruments[0].atr=null;
 x.instruments[0].diagnostics={accountId:'A',periodId:'P',instrumentId:'EURUSD',oneWeek:{n:30,f:1.25},twoWeeks:{n:55,f:2}};
 const after=references(x);fields.forEach(k=>near(after[k].value,before[k].value));
});
test('both references never activate pending policy or sizing authorization',()=>{
 const m=project(fixture());fields.forEach(k=>assert.strictEqual(m.instruments[0][k].executionEligibility,'BLOCKED'));
 for(const id of ['P-14','P-17','P-18','P-21','P-30'])assert.strictEqual(fx.policy.get(id).value,null);
 assert.strictEqual(m.executionEligibility.status,'BLOCKED');assert.strictEqual(m.executionEligibility.canExecuteNormatively,false);
 assert.strictEqual(m.risk.sizingTrace.finalVolume,null);assert.strictEqual(m.risk.sizingTrace.executionEligibility,'BLOCKED');
});
const failed=checks.filter(x=>x.result!=='PASS');
console.log(JSON.stringify({checks,counts:{total:checks.length,passed:checks.length-failed.length,failed:failed.length},result:failed.length?'PRODUCT_FAIL':'PASS'}));
process.exitCode=failed.length?1:0;
"""


def run(root):
    paths = [root / name for name in INPUTS]
    before = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in zip(INPUTS, paths)}
    bundled = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
    node = shutil.which("node") or (str(bundled) if bundled.is_file() else None)
    if not node:
        raise RuntimeError("Existing Node runtime unavailable")
    completed = subprocess.run([node, "-e", PROBE, *map(str, paths)], cwd=root, text=True, capture_output=True)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"result": "PRODUCT_FAIL", "stdout": completed.stdout}
    after = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in zip(INPUTS, paths)}
    payload.update(root=str(root), inputs_before=before, inputs_after=after, source_unchanged=before == after,
                   returncode=completed.returncode, stderr=completed.stderr,
                   environment="Node VM; real production sources; no DOM/storage/network capabilities",
                   test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if before != after or completed.returncode:
        payload["result"] = "PRODUCT_FAIL"
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out and args.out.exists():
        parser.error("Evidence already exists; choose a new path")
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
