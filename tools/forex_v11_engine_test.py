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
INPUTS = ["src/js/00-core/00-forex-policy.js", "src/js/10-domain/00-forex-engine.js"]
PROBE = r"""
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const sandbox={};vm.createContext(sandbox);
for(const name of process.argv.slice(1))vm.runInContext(fs.readFileSync(name,'utf8'),sandbox,{filename:name});
const p=sandbox.JPWForex.policy,e=sandbox.JPWForex.engine;
const rows=[];
function test(name,fn){try{fn();rows.push({name,result:'PASS'});}catch(error){rows.push({name,result:'PRODUCT_FAIL',error:String(error.stack||error)});}}
function close(actual,expected,tolerance=1e-9){assert.strictEqual(typeof actual,'number');assert(Math.abs(actual-expected)<=tolerance,`${actual} != ${expected}`);}
function state(r,status){assert.strictEqual(r.status,status);assert(Array.isArray(r.findings));}
function nullValue(r){assert.strictEqual(r.value,null);}
function plain(v){return JSON.parse(JSON.stringify(v));}
const order={side:'BUY',entryPrice:1.1,stopPrice:1,volume:.01,contractSize:100000,conversionRate:1,stopValid:true};
const pending=Object.assign({},order,{active:true,kind:'AMPLIFYING'});
const riskInput={positions:[order],pendingOrders:[pending],realizedResults:[-20,30],costs:[-5,8]};
test('registry: exactly 26 delegated parameters, semantic pending and source identity',()=>{
 assert.strictEqual(p.delegatedCount,26);assert.strictEqual(p.list().filter(x=>['DELEGATED_N3','PENDING_N3'].includes(x.authorityMode)).length,26);
 for(const id of ['P-10','P-14','P-17','P-18','P-23','P-24','P-30']){assert.strictEqual(p.get(id).value,null);assert.strictEqual(p.get(id).status,'PENDING');}
 assert.strictEqual(p.sources.statute.sha256,'2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769');
 assert.strictEqual(p.sources.annex.sha256,'6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23');
 assert.strictEqual(p.get('not-a-parameter'),null);assert.strictEqual(p.get('P-03').homologationStatus,'NOT_HOMOLOGATED');
});
test('registry: immutable active values, independent writable snapshot',()=>{
 assert(Object.isFrozen(p));assert(Object.isFrozen(p.phases));assert.throws(()=>{p.phases[0].maxLeverage=100;});
 const snapshot=p.snapshot();snapshot.items.find(x=>x.id==='P-03').value=99;assert.strictEqual(p.get('P-03').value,22);
 assert.strictEqual(p.get('P-12b').authorityMode,'MIRROR_N2');assert.strictEqual(p.get('P-29').authorityMode,'DERIVED_NON_N3');
 close(p.planning.referenceMonthlyReturn,.035);assert.deepStrictEqual(plain(p.planning.annualReferenceRange),[.35,.4]);
});
for(const [dd,expected] of [[0,1],[2,1],[2.000001,2],[6,2],[6.000001,3],[10,3],[10.000001,4],[14,4],[14.000001,5],[18,5],[18.000001,6],[21.999999,6]])test('phase exact boundary '+dd,()=>{const r=e.resolveAccountPhase({ddPercent:dd});state(r,'OK');assert.strictEqual(r.value,expected);assert.strictEqual(r.compulsoryClose,false);});
for(const dd of [22,22.000001,75,100,150])test('compulsory close precedes phases '+dd,()=>{const r=e.resolveAccountPhase({ddPercent:dd});state(r,'BLOCKED');nullValue(r);assert.strictEqual(r.compulsoryClose,true);});
test('phase invalid/absent is not genesis fallback',()=>{state(e.resolveAccountPhase({}),'PENDING_INPUT');for(const dd of [-1,NaN,Infinity,'2',null]){const r=e.resolveAccountPhase({ddPercent:dd});assert.notStrictEqual(r.status,'OK');nullValue(r);}});
for(const [equity,dd] of [[10000,0],[9800,2],[9400,6],[7800,22],[11000,0],[-100,101]])test('drawdown SI=10000 equity='+equity,()=>{close(e.computeDrawdown({si:10000,equity,netCashflow:0}).value,dd);});
test('drawdown neutralizes documented cashflow without changing SI',()=>{
 const r=e.computeDrawdown({si:10000,equity:10800,netCashflow:1000,cashflowAdjustmentRecorded:true});close(r.value,2);assert.strictEqual(r.si,10000);close(r.adjustedEquity,9800);
 close(e.computeDrawdown({si:10000,equity:9300,netCashflow:-500,cashflowAdjustmentRecorded:true}).value,2);
 state(e.computeDrawdown({si:10000,equity:10800,netCashflow:1000}),'PENDING_INPUT');state(e.computeDrawdown({si:10000,equity:9800}),'PENDING_INPUT');
 state(e.computeDrawdown({si:0,equity:100,netCashflow:0}),'NOT_COMPUTABLE');
});
for(const [equity,expected] of [[8000,2.5],[10000,2],[12000,2]])test('gross leverage equity='+equity,()=>{
 const r=e.computeLeverage({si:10000,equity,positions:[{volume:.1,contractSize:100000,conversionRate:1,side:'BUY'},{volume:.1,contractSize:100000,conversionRate:1,side:'SELL'}]});state(r,'OK');close(r.value,expected);close(r.grossNotional,20000);
});
test('leverage missing conversion/positions/equity is not zero',()=>{
 state(e.computeLeverage({si:10000,equity:10000}),'PENDING_INPUT');state(e.computeLeverage({si:10000,equity:10000,positions:[{volume:1,contractSize:100}]}),'PENDING_INPUT');state(e.computeLeverage({si:10000,equity:0,positions:[]}),'NOT_COMPUTABLE');close(e.computeLeverage({si:10000,equity:10000,positions:[]}).value,0);
});
const since='2026-09-14T00:00:00Z';
function hysteresis(dd,closes,previousPhase=3){return e.resolvePhaseReturnWithHysteresis({ddPercent:dd,previousPhase,since,confirmedH4Closes:closes});}
const h4=dd=>({closedAt:'2026-09-14T04:00:00Z',timeframe:'H4',ddPercent:dd});
test('hysteresis: insufficient margin even with H4 evidence',()=>{const r=hysteresis(5.6,[h4(5.6)]);assert.strictEqual(r.value,3);assert.strictEqual(r.transition,'HELD');});
test('hysteresis: margin without a close is insufficient',()=>{assert.strictEqual(hysteresis(5.5,[]).value,3);assert.strictEqual(hysteresis(5.5,[{...h4(5.5),timeframe:'H1'}]).value,3);});
test('hysteresis: confirmed exact margin returns, no pruning restoration',()=>{const r=hysteresis(5.5,[h4(5.5)]);assert.strictEqual(r.value,2);assert.strictEqual(r.transition,'CONFIRMED_RETURN');assert.strictEqual(r.restoresPrunedPositions,false);});
test('hysteresis: old favorable closes do not replace latest/current evidence',()=>{
 assert.strictEqual(hysteresis(5.5,[h4(5.5),{...h4(5.6),closedAt:'2026-09-14T08:00:00Z'}]).value,3);
 assert.strictEqual(hysteresis(5.5,[{...h4(5.5),closedAt:since}]).value,3);
 assert.strictEqual(e.resolvePhaseReturnWithHysteresis({ddPercent:5.5,previousPhase:3,confirmedH4Closes:[h4(5.5)]}).value,3);
});
test('hysteresis: malformed or contradictory closes cannot be silently skipped',()=>{
 for(const invalidClose of [{...h4(null),closedAt:'2026-09-14T08:00:00Z'},{...h4(5.5),timeframe:'H1'},{...h4(5.5),closedAt:'invalid'},h4(5.6)]){
  const r=hysteresis(5.5,[h4(5.5),invalidClose]);assert.strictEqual(r.value,3);assert.strictEqual(r.transition,'HELD');assert(r.missingEvidence.length>0);
 }
 assert.strictEqual(hysteresis(5.5,[h4(5.5),h4(5.5)]).value,2);
});
test('hysteresis: adverse crossing/gap immediate; current maximal DD never waits',()=>{assert.strictEqual(hysteresis(14.1,[],2).value,5);assert.strictEqual(hysteresis(2.1,[],1).value,2);assert.strictEqual(hysteresis(22,[],1).compulsoryClose,true);});
test('hysteresis: multilevel return applies crossed threshold margins',()=>{assert.strictEqual(hysteresis(1.5,[h4(1.5)],5).value,1);assert.strictEqual(hysteresis(1.8,[h4(1.8)],5).value,2);});
test('active grid: declared independent phase cannot increase account limit',()=>{
 const r=e.resolveActiveGridPhase({declaredPhase:2,accountPhase:4,structureKnown:true});state(r,'OK');assert.strictEqual(r.value,2);assert.strictEqual(r.limitsFromPhase,4);close(r.maxLeverage,1.4);assert.strictEqual(r.diverges,true);state(e.resolveActiveGridPhase({declaredPhase:2,accountPhase:4}),'PENDING_INPUT');
});
test('VRM ratio and missing long period do not assume normal',()=>{close(e.computeVRM({atrShort:1.2,atrLong:1}).value,1.2);state(e.computeVRM({atrShort:1.2,atrLong:0}),'NOT_COMPUTABLE');state(e.computeVRM({atrShort:1.2}),'PENDING_INPUT');});
for(const [vrm,regime,cap] of [[1.19999,'NORMAL',.5],[1.2,'TRANSITION',.25],[1.5,'TRANSITION',.25],[1.50001,'HIGH',.25]])test('VRM boundary '+vrm,()=>{
 const r=e.resolveVRMRegime({vrm});assert.strictEqual(r.value,regime);close(r.maxLeveragePerOrder,cap);assert.strictEqual(r.amplificationForbidden,regime==='TRANSITION');
});
test('effective genesis ceiling is VRM limited, not automatic 1x sizing',()=>{
 close(e.computeEffectiveLeverageLimit({phase:1,vrm:1,otherLimits:[]}).value,.5);close(e.computeEffectiveLeverageLimit({phase:1,vrm:1.2,otherLimits:[]}).value,.25);close(e.computeEffectiveLeverageLimit({phase:6,vrm:1,otherLimits:[]}).value,.4);close(e.computeEffectiveLeverageLimit({phase:2,vrm:1,otherLimits:[.2]}).value,.2);
 state(e.computeEffectiveLeverageLimit({phase:1,vrm:1}),'PENDING_INPUT');state(e.computeEffectiveLeverageLimit({phase:1,vrm:null,otherLimits:[]}),'PENDING_INPUT');
});
test('financial risk is execution-to-stop, nonnegative for long and short',()=>{
 close(e.computeFinancialRisk(order).value,100);close(e.computeFinancialRisk({...order,side:'SELL',stopPrice:1.2}).value,100);close(e.computeFinancialRisk({...order,stopPrice:1.2}).value,0);close(e.computeFinancialRisk({...order,side:'SELL',stopPrice:1}).value,0);
 close(e.computeFinancialRisk({...order,currentPrice:.2}).value,100);close(e.computeFinancialRisk({...order,conversionRate:2,volume:.02}).value,400);
});
test('invalid stop and missing contract do not fabricate risk zero',()=>{state(e.computeFinancialRisk({...order,stopValid:false}),'NOT_COMPUTABLE');state(e.computeFinancialRisk({...order,contractSize:undefined}),'PENDING_INPUT');state(e.computeFinancialRisk({...order,side:'UNKNOWN'}),'NOT_COMPUTABLE');});
test('admission stays blocked with factual risk known and recordability separate',()=>{
 const r=e.computeAdmissionRisk({...order,si:10000,phase:1});state(r,'BLOCKED');nullValue(r);close(r.financialRisk,100);close(r.financialRiskPercent,1);assert.strictEqual(r.canRecord,true);assert.strictEqual(r.executionEligibility,'BLOCKED');for(const id of ['P-14','P-18','P-17'])assert(r.findings.some(f=>f.code===id+'_PENDING'));
});
test('committed includes losses, negative costs, open and reserved, no positive offset',()=>{const r=e.computeCommittedOperationRisk(riskInput);close(r.value,225);close(r.realizedLosses,20);close(r.negativeCosts,5);close(r.openRisk,100);close(r.pendingRisk,100);});
test('aggregate includes amplifying pending (Annex D11 omission)',()=>{close(e.computeOpenAggregatePhaseRisk(riskInput).value,200);close(e.computeOpenAggregatePhaseRisk({...riskInput,pendingOrders:[{...pending,kind:'REDUCING'}]}).value,100);});
test('pending exclusivity: sum without proof; max only with audit evidence',()=>{
 const pair=[{...pending,exclusiveGroup:'oco'},{...pending,volume:.02,exclusiveGroup:'oco'}];close(e.computeOpenAggregatePhaseRisk({positions:[],pendingOrders:pair}).value,300);
 const verified=pair.map(x=>({...x,exclusivityVerified:true,exclusivityEvidence:'synthetic broker technical guarantee'}));close(e.computeOpenAggregatePhaseRisk({positions:[],pendingOrders:verified}).value,200);
 close(e.computeOpenAggregatePhaseRisk({positions:[],pendingOrders:pair.map(x=>({...x,active:false}))}).value,0);
});
test('unknown costs/results/pending remain unknown; explicit empty is zero',()=>{
 state(e.computeCommittedOperationRisk({positions:[],pendingOrders:[],realizedResults:[]}),'PENDING_INPUT');state(e.computeOpenAggregatePhaseRisk({positions:[]}),'PENDING_INPUT');state(e.computeOpenAggregatePhaseRisk({positions:[],pendingOrders:[{...pending,active:undefined}]}),'PENDING_INPUT');close(e.computeCommittedOperationRisk({positions:[],pendingOrders:[],realizedResults:[],costs:[]}).value,0);
});
test('partial close: loss consumes committed budget; positive result never funds it',()=>{
 const base={positions:[{...order,volume:.005}],pendingOrders:[],costs:[]};close(e.computeCommittedOperationRisk({...base,realizedResults:[-50]}).value,100);close(e.computeCommittedOperationRisk({...base,realizedResults:[200]}).value,50);
});
test('prudential remaining and missing buffer semantics',()=>{
 const r=e.computePrudentialCapacity({si:10000,ddPercent:6,committedRisk:225});state(r,'OK');close(r.ceiling,1600);close(r.value,1375);assert.strictEqual(r.bufferValue,null);assert.strictEqual(r.bufferStatus,'PENDING');assert.strictEqual(r.effectiveAdmissionCapacity,null);assert.strictEqual(r.executionEligibility,'BLOCKED');
 close(e.computePrudentialCapacity({si:10000,ddPercent:21,committedRisk:200}).value,0);state(e.computePrudentialCapacity({si:10000,ddPercent:22,committedRisk:0}),'BLOCKED');state(e.computePrudentialCapacity({si:10000,ddPercent:6}),'PENDING_INPUT');
});
test('stop multiple units and exact 3.5 ATR threshold',()=>{
 const r=e.computeStopAtrMultiple({stopPercent:3.5,atr:1,currentPrice:100});close(r.value,3.5);assert.strictEqual(r.meetsMinimum,true);assert.strictEqual(e.computeStopAtrMultiple({stopPercent:3.4999,atr:1,currentPrice:100}).meetsMinimum,false);close(e.computeMinimumStop({atr:2}).value,7);state(e.computeStopAtrMultiple({stopPercent:3.5,atr:0,currentPrice:100}),'NOT_COMPUTABLE');
});
test('FCR follows PDF nominal capital, explicitly distinct from SI',()=>{
 const r=e.computeFCRRequirement({capitalNominal:12000,si:10000});state(r,'OK');close(r.value,2640);assert.strictEqual(r.baseEqualsSI,false);assert.strictEqual(r.baseType,'MASTER_NOMINAL_CAPITAL');assert(r.findings.some(f=>f.code==='FCR_BASE_CONFLICT'));state(e.computeFCRRequirement({si:10000}),'PENDING_INPUT');close(e.computeFCRRequirement({capitalNominal:10000}).value,2200);
});
test('separate immutable scenario revision recalculates FCR; current/historical policy unchanged',()=>{
 const changed=Object.freeze({...p.get('P-03'),value:24,status:'PROPOSED',homologationStatus:'NOT_HOMOLOGATED'});
 const phases=Object.freeze(p.phases.map((phase,i)=>i===5?Object.freeze({...phase,ddMaxPercent:24}):phase));
 const scenario=Object.freeze({...p,version:'SYNTHETIC-SCENARIO-DD24',calculationMode:'SCENARIO',phases,get:id=>id==='P-03'?changed:p.get(id)});
 const projected=sandbox.JPWForex.createEngine(scenario).computeFCRRequirement({capitalNominal:12000,si:10000});
 state(projected,'OK');close(projected.value,2880);assert.strictEqual(projected.calculationMode,'SCENARIO');assert.strictEqual(projected.policyVersion,'SYNTHETIC-SCENARIO-DD24');
 assert.strictEqual(p.get('P-03').value,22);close(e.computeFCRRequirement({capitalNominal:12000}).value,2640);assert.strictEqual(p.operability,'BLOCKED');
 assert.throws(()=>sandbox.JPWForex.createEngine({ddMax:24}));assert.throws(()=>sandbox.JPWForex.createEngine(Object.freeze({...scenario,phases:p.phases})));
});
test('FEO: six historical months auxiliary sum does not become requirement',()=>{
 const r=e.computeFEORequirement({sixMonthExpenses:[100,120,90,110,100,80],si:10000});state(r,'PENDING_INPUT');nullValue(r);close(r.observedSixMonthTotal,600);state(e.computeFEORequirement({monthlyExpenses:100,si:10000}),'PENDING_INPUT');
});
test('FEO: explicit expense determination, never 21 percent fallback',()=>{
 const r=e.computeFEORequirement({sixMonthExpenseAmount:600,determinationRecorded:true,expensesApproved:true,si:10000});state(r,'OK');close(r.value,600);close(r.derivedPercent,6);assert.strictEqual(r.percentageDeterminesAmount,false);assert.strictEqual(r.governanceStatus,'UNRESOLVED_NOMINAL_HOMOLOGATION');
 state(e.computeFEORequirement({sixMonthExpenseAmount:600}),'PENDING_INPUT');state(e.computeFEORequirement({sixMonthExpenses:[100,120]}),'NOT_COMPUTABLE');close(e.computeFEORequirement({sixMonthExpenseAmount:0,determinationRecorded:true,expensesApproved:true}).value,0);
});
test('reserve status separates amount, deficit, liquidity and recorded verification',()=>{
 const requirement=e.computeFCRRequirement({capitalNominal:10000}),base={fund:'FCR',requirement,constituted:2200,liquidityDays:1,verificationRecorded:true,verifiedAt:'2026-09-14T12:00:00Z'};
 const r=e.computeReserveStatus(base);state(r,'OK');close(r.value.deficit,0);assert.strictEqual(r.doesNotAuthorizeCycle,true);
 state(e.computeReserveStatus({...base,constituted:2100}),'BLOCKED');state(e.computeReserveStatus({...base,liquidityDays:2}),'BLOCKED');state(e.computeReserveStatus({...base,verificationRecorded:false}),'BLOCKED');state(e.computeReserveStatus({...base,requirement:e.computeFEORequirement({})}),'PENDING_INPUT');
 state(e.computeReserveStatus({...base,requirement:{status:'OK',value:null,findings:[]}}),'NOT_COMPUTABLE');state(e.computeReserveStatus({...base,requirement:{status:'UNRECOGNIZED',value:1,findings:[]}}),'NOT_COMPUTABLE');
});
test('replication has formula but cannot activate factors from supplied inputs',()=>{
 const missing=e.computeReplicationFirewall({});state(missing,'BLOCKED');nullValue(missing);assert.strictEqual(missing.theoreticalCeiling,null);
 const r=e.computeReplicationFirewall({maxLossPercent:10,safetyMarginPercent:2});state(r,'BLOCKED');close(r.theoreticalCeiling,8/22);assert.strictEqual(r.replicationAllowed,false);nullValue(r);
});
test('firewall negative headroom has no admissible nonnegative factor, not a zero ceiling',()=>{
 const r=e.computeReplicationFirewall({maxLossPercent:10,safetyMarginPercent:12});
 state(r,'BLOCKED');nullValue(r);assert.strictEqual(r.theoreticalCeiling,null);
 assert.strictEqual(r.admissibleRange,null);assert.strictEqual(r.rangeStatus,'NO_NONNEGATIVE_SOLUTION');
 close(r.literalBound,-2/22);assert(r.findings.some(f=>f.code==='NO_ADMISSIBLE_REPLICATION_RANGE'));
 assert(r.findings.some(f=>f.code==='P-30_PENDING'));assert.strictEqual(r.replicationAllowed,false);
 const zero=e.computeReplicationFirewall({maxLossPercent:10,safetyMarginPercent:10});
 close(zero.literalBound,0);close(zero.theoreticalCeiling,0);assert.strictEqual(zero.rangeStatus,'ZERO_ONLY_DIAGNOSTIC');
 assert.deepStrictEqual(plain(zero.admissibleRange),[0,0]);assert.strictEqual(zero.replicationAllowed,false);
});
test('sizing trace records the binding order without fabricating a volume through pending parameters',()=>{
 const input=Object.freeze({volume:5,riskLimit:100,genesisRisk:100,otherLimits:[],phase:1,vrm:1,minimumLot:.01});
 const r=e.computeSizingTrace(input);state(r,'BLOCKED');nullValue(r);assert.strictEqual(r.finalVolume,null);
 assert.strictEqual(r.executionEligibility,'BLOCKED');assert.strictEqual(r.limitingStep,null);
 assert.deepStrictEqual(plain(r.steps.map(s=>s.id)),['ADMISSION_RISK','PHASE_LEVERAGE','VOLATILITY_REGIME','PRO_FORMA_BUDGET_AND_AGGREGATE']);
 assert.deepStrictEqual(plain(r.steps.map(s=>s.status)),['BLOCKED','NOT_EVALUATED','NOT_EVALUATED','NOT_EVALUATED']);
 for(const s of r.steps){assert.strictEqual(s.value,null);assert.strictEqual(s.unit,'LOTS');}
 for(const id of ['P-14','P-18'])assert(r.steps[0].findings.some(f=>f.code===id+'_PENDING'));
 assert.strictEqual(r.institutionMinimumCheck.status,'NOT_EVALUATED');assert.strictEqual(r.institutionMinimumCheck.roundingUpAllowed,false);
 assert.strictEqual(input.volume,5);assert.strictEqual(r.canRecord,true);
});
test('planning delegates exact assumptions and does not mutate source or ACTUAL',()=>{
 const a={initialBalanceUsd:100,defaultMonthlyReturn:.035};let count=0;
 const r=e.computePlanningProjection({assumptions:a,mode:'SCENARIO',projector:copy=>{count++;assert.deepStrictEqual(plain(copy),a);copy.initialBalanceUsd=900;return [{close:103.5}];}});
 state(r,'OK');assert.strictEqual(count,1);assert.strictEqual(a.initialBalanceUsd,100);assert.strictEqual(r.value[0].close,103.5);assert.strictEqual(r.source,'JPWFx');
 state(e.computePlanningProjection({assumptions:a,mode:'ACTUAL',projector:()=>[]}), 'NOT_COMPUTABLE');state(e.computePlanningProjection({assumptions:a,mode:'PLAN'}),'PENDING_INPUT');
});
test('pure calls preserve frozen synthetic inputs and policy identity',()=>{
 const freeze=o=>{Object.values(o).forEach(v=>{if(v&&typeof v==='object')freeze(v);});return Object.freeze(o);};
 const data=freeze(JSON.parse(JSON.stringify(riskInput))),before=JSON.stringify(data),policyBefore=JSON.stringify(p.snapshot());
 e.computeCommittedOperationRisk(data);e.computeOpenAggregatePhaseRisk(data);assert.strictEqual(JSON.stringify(data),before);assert.strictEqual(JSON.stringify(p.snapshot()),policyBefore);assert.strictEqual(Object.keys(sandbox).join(','),'JPWForex');
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
