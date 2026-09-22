#!/usr/bin/env python3
"""Execution Board fixed factual oracles: pure Node VM, synthetic state only.

Authority: CHG-FOREX-EXECUTION-BOARD-20260915 and CHG-FOREX-EXECUTION-TABLE-20260922.
Fixed examples: open 100,
separate 100-10=90, included 90=90, compensated 100-(-20)=120 and 100-150=-50.
No normative policy, finalization, or admission behavior is amended by this test.
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
          "src/js/10-domain/18-execution-board-model.js"]
PROBE = r"""
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const box={structuredClone,instrumentId:x=>String(x||'').toUpperCase().replace(/[^A-Z0-9]/g,''),QUOTE_CCY:{EURUSD:'USD',GBPUSD:'USD',USDJPY:'JPY',USDCAD:'CAD',AUDCAD:'CAD'}};
vm.createContext(box);for(const file of process.argv.slice(1))vm.runInContext(fs.readFileSync(file,'utf8'),box,{filename:file});
const fx=box.JPWForex,b=fx.executionBoard,checks=[];
const plain=x=>JSON.parse(JSON.stringify(x));
function test(name,fn){try{fn();checks.push({name,result:'PASS'});}catch(e){checks.push({name,result:'PRODUCT_FAIL',error:String(e.stack||e)});}}
function near(a,z){assert.strictEqual(typeof a,'number');assert(Math.abs(a-z)<1e-8,a+' != '+z);}
function missing(m){assert.notStrictEqual(m.status,'OK');assert.strictEqual(m.value,null);}
const order=(id,changes={})=>({accountId:'A',periodId:'P',currency:'USD',operationId:'OP',orderId:id,recordVersion:1,recordStatus:'recorded',
 par:'EURUSD',tipo:'BUY',role:'GENESIS',entry:1.1,sl:1,lote:.01,stopValidated:true,status:'Aberta',costBasis:'SEPARATE_FROM_RESULT',costs:0,...changes});
function fixture(orders=[]){
 const account={periodId:'P',currency:'USD',si:10000,equity:10000,netCashflow:0,usdToAccountRate:1,observedAt:'2026-09-15T12:00:00Z'};
 return {scope:{accountId:'A',periodId:'P',operationId:'OP'},account,accountRecord:{currency:'USD',satu:10100},
  phases:fx.policy.phases.map(p=>({policyVersion:fx.policy.version,orders:[]})),
  rows:orders.map((o,i)=>({pi:0,oi:i,order:o})),
  instruments:[{id:'EURUSD',name:'EURUSD',price:{value:1.25,source:'Synthetic',kind:'MANUAL'},contract:{contractSize:100000,source:'Synthetic'},
   conversion:{baseToAccountRate:1.25,quoteToAccountRate:1},atr:{short:1.2,long:1,timeframe:'H4',unit:'PRICE',source:'Synthetic'}}],
  normative:{accountId:'A',account,metrics:{committedRisk:{status:'OK',value:225,unit:'ACCOUNT_CURRENCY',findings:[]},
    prudentialCapacity:{status:'OK',value:1975,unit:'ACCOUNT_CURRENCY',findings:[]}},findings:[],executionEligibility:{status:'BLOCKED',canExecuteNormatively:false,canRecord:true}}};
}
function project(x){const before=JSON.stringify(x),result=b.project(x);assert.strictEqual(JSON.stringify(x),before,'projection mutated its input');return result;}
test('separate signed costs are added exactly once',()=>near(b.closedNetResult(order('c',{status:'Fechada',result:100,costs:-10})).value,90));
test('included costs are never charged twice',()=>near(b.closedNetResult(order('c',{status:'Fechada',result:90,costs:-10,costBasis:'INCLUDED_IN_RESULT'})).value,90));
test('included net result needs no guessed cost component',()=>near(b.closedNetResult(order('c',{status:'Fechada',result:90,costs:null,costBasis:'INCLUDED_IN_RESULT'})).value,90));
test('signed positive cost adjustment remains positive',()=>near(b.closedNetResult(order('c',{status:'Fechada',result:100,costs:5})).value,105));
for(const delta of [{costs:null},{costs:undefined},{costBasis:''},{costBasis:undefined},{costBasis:'UNKNOWN'},{result:null},{result:'20'},{costs:NaN}])
 test('missing/invalid closed component is not zero '+JSON.stringify(delta),()=>missing(b.closedNetResult(order('c',{status:'Fechada',result:0,...delta}))));
test('zero result and explicit separate zero costs are factual zero',()=>near(b.closedNetResult(order('c',{status:'Fechada',result:0,costs:0})).value,0));
test('voided and open rows do not yield closed results',()=>{missing(b.closedNetResult(order('x',{result:40})));missing(b.closedNetResult(order('x',{status:'Fechada',result:40,recordStatus:'voided'})));});
test('open100 and realized loss20 => compensated120',()=>{const m=project(fixture([order('a'),order('c',{status:'Fechada',result:-20,role:'DEFENSE'})]));near(m.risk.open.value,100);near(m.economics.compensatedAll.value,120);near(m.risk.committed.value,225);});
test('economic credit may be negative, never changes normative RC',()=>{const m=project(fixture([order('a'),order('c',{status:'Fechada',result:150,role:'DEFENSE'})]));near(m.economics.compensatedAll.value,-50);near(m.risk.committed.value,225);assert.strictEqual(m.executionEligibility.status,'BLOCKED');});
test('defenses and all closed orders are distinct totals',()=>{const m=project(fixture([order('a'),order('d',{status:'Fechada',result:20,role:'DEFENSE'}),order('x',{status:'Fechada',result:-10,role:'OTHER'})]));near(m.economics.closedNetDefenses.value,20);near(m.economics.closedNetAll.value,10);near(m.economics.compensatedDefenses.value,80);near(m.economics.compensatedAll.value,90);});
test('unclassified closed role is not silently outside defenses',()=>{const m=project(fixture([order('a'),order('d',{status:'Fechada',result:20,role:''})]));near(m.economics.closedNetAll.value,20);missing(m.economics.closedNetDefenses);missing(m.economics.compensatedDefenses);});
test('missing separate cost taints result and compensation, not known open risk',()=>{const m=project(fixture([order('a'),order('c',{status:'Fechada',result:20,costs:null})]));near(m.risk.open.value,100);missing(m.economics.closedNetAll);missing(m.economics.compensatedAll);});
test('normative unavailable remains unavailable despite economic net known',()=>{const x=fixture([order('c',{status:'Fechada',result:20,costBasis:'INCLUDED_IN_RESULT'})]);x.normative.metrics.committedRisk={status:'NOT_COMPUTABLE',value:null,findings:[{code:'COST_BASIS',message:'Normative input incomplete'}]};const m=project(x);near(m.economics.closedNetAll.value,20);missing(m.risk.committed);});
test('missing account never yields zero exposure',()=>{const x=fixture();x.account=null;const m=project(x);missing(m.risk.open);missing(m.economics.closedNetAll);missing(m.capital.si);});
for(const key of ['accountId','periodId','currency','operationId','orderId'])test('missing '+key+' keeps fact unresolved and total incomplete',()=>{const m=project(fixture([order('a',{[key]:null})]));assert.strictEqual(m.unresolved.length,1);missing(m.risk.open);missing(m.risk.committed);});
test('other identified accounts periods currencies operations do not mix',()=>{for(const delta of [{accountId:'B'},{periodId:'OTHER'},{currency:'EUR'},{operationId:'OTHER'}]){const m=project(fixture([order('a'),order('b',delta)]));near(m.risk.open.value,100);assert.strictEqual(m.ignored.length,1);}});
test('duplicate order ids do not silently deduplicate into a total',()=>{const m=project(fixture([order('a'),order('a')]));assert.strictEqual(m.unresolved.length,2);missing(m.risk.open);});
for(const status of ['Active','UNKNOWN'])test('unrecognized status '+status+' remains unresolved',()=>{const m=project(fixture([order('a',{status})]));missing(m.risk.open);assert.strictEqual(m.unresolved.length,1);});
test('draft with contradictory open state is unresolved',()=>missing(project(fixture([order('a',{recordStatus:'draft'})])).risk.open));
test('draft, migrated and voided do not create exposure',()=>{const m=project(fixture([order('d',{status:'',recordStatus:'draft'}),order('m',{status:'Migrada'}),order('v',{recordStatus:'voided'})]));near(m.risk.open.value,0);assert.strictEqual(m.ignored.length,3);});
test('stop at favorable side gives true zero risk only when validated',()=>{near(project(fixture([order('a',{sl:1.2})])).risk.open.value,0);missing(project(fixture([order('a',{sl:1.2,stopValidated:false})])).risk.open);});
test('amplifying pending is separated from open stops',()=>{const m=project(fixture([order('a'),order('p',{status:'Pendente',pendingActive:true,amplifiesExposure:true})]));near(m.risk.open.value,100);near(m.risk.aggregate.value,200);});
test('unclassified pending status does not become no risk',()=>{const m=project(fixture([order('p',{status:'Pendente'})]));missing(m.risk.aggregate);});
test('six normative phases use policy boundaries without risk budgets',()=>{const m=project(fixture());assert.strictEqual(m.phases.length,6);assert.deepStrictEqual(plain(m.phases.map(p=>p.ddMaxPercent)),[2,6,10,14,18,22]);m.phases.forEach(p=>missing(p.freeNormativeMargin));});
test('four legacy containers retain legacy identity and order locators',()=>{const x=fixture([order('a')]);x.phases=x.phases.slice(0,4);const m=project(x);assert(m.phases.every(p=>p.legacy));assert.strictEqual(m.phases[0].rows[0].oi,0);assert.strictEqual(m.phases[0].rows[0].order.orderId,'a');assert.strictEqual(m.phases[0].ddMaxPercent,null);});
test('multiple instruments add monetary notional but not heterogeneous lots',()=>{const x=fixture([order('a'),order('b',{par:'GBPUSD'})]);x.instruments.push({...x.instruments[0],id:'GBPUSD',name:'GBPUSD',conversion:{baseToAccountRate:1.5,quoteToAccountRate:1}});const m=project(x);near(m.risk.grossNotional.value,2750);missing(m.phases[0].metrics.lots);assert.strictEqual(m.phases[0].instruments.length,2);});
test('SI10000 price1.25 contract100000 => reference .04 and .02',()=>{const m=project(fixture()).instruments[0];near(m.normal.value,.04);near(m.restrictive.value,.02);assert.strictEqual(m.normal.executionEligibility,'BLOCKED');});
test('reference uses minimum of SI/equity and never rounds up',()=>{const x=fixture();x.account.equity=1000;const m=project(x).instruments[0];near(m.normal.value,.004);assert.strictEqual(m.normal.lotMinimumEvaluated,false);});
for(const edit of [i=>i.conversion.baseToAccountRate=null,i=>i.contract.contractSize=null])test('missing instrument denominator prevents sizing reference',()=>{const x=fixture();edit(x.instruments[0]);missing(project(x).instruments[0].normal);});
test('restriction remains visible with only theoretical reference',()=>{const x=fixture();x.instruments[0].banned=true;assert.strictEqual(project(x).instruments[0].operable,false);});
test('ATR belongs to each instrument; global other data cannot fill absence',()=>{const x=fixture();x.instruments[0].atr=null;x.market={atrShort:1,atrLong:1};missing(project(x).instruments[0].vrm);});
test('VRM boundary and root N pending remain documented',()=>{const i=project(fixture()).instruments[0];near(i.vrm.value,1.2);assert.strictEqual(i.regime.value,'TRANSITION');missing(i.rootN.oneWeek);missing(i.rootN.twoWeeks);missing(project(fixture()).phases[0].technicalProfit);});
test('DD and statutory equity threshold are distinct from book balance',()=>{const x=fixture();x.account.equity=9700;const m=project(x);near(m.capital.drawdown.value,3);near(m.capital.stopoutEquity.value,7800);near(m.capital.book.value,10100);missing(m.capital.floating);});
test('documented cashflow moves raw equity threshold, not SI',()=>{const x=fixture();x.account.netCashflow=1000;x.account.cashflowAdjustmentRecorded=true;near(project(x).capital.stopoutEquity.value,8800);x.account.cashflowAdjustmentRecorded=false;missing(project(x).capital.stopoutEquity);});
test('wrong currency book is unavailable rather than recast to account unit',()=>{const x=fixture();x.accountRecord.currency='EUR';missing(project(x).capital.book);});

// Read-adapter fixtures follow accountContexts introduced before this candidate.
// The former legacy-global stub lacked operationalSelection/accountContext.
function installState(orders=[]){
 const phases=fx.policy.phases.map((p,i)=>({orders:i?[]:orders,policyVersion:fx.policy.version}));
 box.contexts={A:{P:{accountId:'A',periodId:'P',currency:'USD',si:10000,openingBook:10000,ledger:[],revision:1,
  activeOperation:orders.length?{operationId:'OP'}:null,phases:structuredClone(phases)}}};
 box.S={accounts:[{forexAccountId:'A',nome:'Synthetic Master',tipo:'MESTRE',currency:'USD',satu:10000}],forex:{activeAccountId:'B',accounts:{A:{periodId:'P',currency:'USD',si:10000,equity:10000,netCashflow:0,usdToAccountRate:1}}},
  activeOperation:null,phases,instruments:[{name:'EURUSD',preco:1.25,cpl:100000}]};
 fx.state={supported:()=>true,recordContext:q=>{const a=box.S.forex.accounts[q.accountId];return a&&a.periodId===q.periodId?{status:'OK',accountInputs:structuredClone(a)}:{status:'NOT_COMPUTABLE',accountInputs:null};},
  operationalSelection:()=>{const masters=box.S.accounts.filter(a=>a.tipo==='MESTRE'),accountId=masters.length===1?masters[0].forexAccountId:null;
   return {accountId,periodId:accountId?Object.keys(box.contexts[accountId]||{})[0]||null:null,reason:accountId?'UNIQUE_MASTER':'SELECTION_REQUIRED'};},
  accountContext:q=>{const value=box.contexts[q.accountId]?.[q.periodId];return {status:value?'OK':'NOT_COMPUTABLE',value:value?structuredClone(value):null};},
  newOperationPhases:()=>fx.policy.phases.map(p=>({orders:[],policyVersion:fx.policy.version})),
  read:q=>({accountId:q.accountId,account:box.S.forex.accounts[q.accountId],metrics:{},findings:[]}),instrumentContext:()=>({status:'NOT_COMPUTABLE',value:null}),dailyReference:()=>({status:'NOT_COMPUTABLE',value:null}),executionDiagnostics:()=>({status:'NOT_COMPUTABLE',value:null})};
 fx.orderInputs=()=>({conversionRate:1,notionalConversionRate:1.25});
}
function read(){const before=JSON.stringify(box.S),m=b.read();assert.strictEqual(JSON.stringify(box.S),before);return m;}
test('single Master is proposed without writing active account',()=>{installState();const m=read();assert.strictEqual(m.selection.reason,'UNIQUE_MASTER');assert.strictEqual(m.selection.accountId,'A');assert.strictEqual(box.S.forex.activeAccountId,'B');});
test('absent or ambiguous Master has no silent first-account fallback',()=>{installState();box.S.accounts[0].tipo='PRÓPRIA';assert.strictEqual(read().selection.accountId,null);box.S.accounts[0].tipo='MESTRE';box.S.accounts.push({forexAccountId:'B',tipo:'MESTRE'});assert.strictEqual(read().selection.accountId,null);});
test('unassigned contextual facts remain unresolved in selected period',()=>{installState([order('a',{accountId:null})]);const m=read();assert.strictEqual(m.selection.accountId,'A');assert.strictEqual(m.unresolved.length,1);missing(m.risk.open);});
test('explicit different account never borrows active operation from Master',()=>{installState([order('a')]);box.S.accounts.push({forexAccountId:'B',tipo:'PROPRIA'});const m=b.read({accountId:'B',periodId:'Q'});assert.strictEqual(m.selection.accountId,'B');assert.strictEqual(m.selection.lockedToOperation,false);assert.strictEqual(m.scope.operationId,null);missing(m.risk.open);});
test('legacy global orders are not attributed to an empty contextual period',()=>{installState();box.S.phases[0].orders=[order('legacy')];box.S.activeOperation={operationId:'LEGACY',policySnapshot:{policyVersion:'LEGACY_UNRESOLVED'}};const m=read();near(m.risk.open.value,0);assert.strictEqual(m.scope.operationId,null);assert.strictEqual(m.rows.length,0);});
test('manual price wins over daily reference; quote access never writes',()=>{installState();fx.state.instrumentContext=()=>({status:'OK',value:{price:{value:1.3,source:'Manual',observedAt:'2026-09-15T12:00:00Z'}}});fx.state.dailyReference=()=>({status:'OK',value:{rate:1.2,source:'Frankfurter',referenceDate:'2026-09-14'}});const m=read().instruments[0];near(m.price.value,1.3);assert.strictEqual(m.price.kind,'MANUAL');near(m.notionalPerLot.value,130000);});
test('daily quote has source date and is not realtime',()=>{installState();fx.state.dailyReference=()=>({status:'OK',value:{rate:1.2,source:'Frankfurter',referenceDate:'2026-09-14'}});const m=read().instruments[0];assert.strictEqual(m.price.kind,'DAILY_REFERENCE');assert.strictEqual(m.price.referenceDate,'2026-09-14');});
test('empty contextual operation retains its explicit identity',()=>{installState();box.contexts.A.P.activeOperation={operationId:'OP'};const m=b.read({accountId:'A',periodId:'P'});assert.strictEqual(m.scope.operationId,'OP');assert.strictEqual(m.selection.lockedToOperation,false);});
test('explicit unregistered account never falls back to Master',()=>{installState();const m=b.read({accountId:'UNKNOWN',periodId:'P'});assert.strictEqual(m.selection.accountId,null);assert.strictEqual(m.selection.reason,'ACCOUNT_NOT_REGISTERED');missing(m.risk.open);});
test('drawdown has percent unit and never currency',()=>{const x=fixture();x.account.equity=9700;const m=project(x).capital.drawdown;assert.strictEqual(m.unit,'DD_PERCENT');assert.strictEqual(m.currency,null);near(m.value,3);});
test('pending-only subtotal remains computable if unrelated open stop missing',()=>{const x=fixture([order('a',{sl:null}),order('p',{status:'Pendente',pendingActive:true,amplifiesExposure:true})]);const m=project(x);missing(m.risk.open);near(m.risk.pending.value,100);near(m.phases[0].metrics.pending.value,100);});
test('reported costs never charge included result again',()=>{const m=project(fixture([order('a',{costs:-2}),order('c',{status:'Fechada',costs:-10,costBasis:'INCLUDED_IN_RESULT',result:90})]));near(m.risk.costs.value,-12);near(m.economics.closedNetAll.value,90);near(m.economics.compensatedAll.value,10);near(m.phases[0].metrics.costs.value,-12);});
test('unknown included cost breakdown does not falsify cost zero or erase net',()=>{const m=project(fixture([order('c',{status:'Fechada',result:90,costs:null,costBasis:'INCLUDED_IN_RESULT'})]));missing(m.risk.costs);near(m.economics.closedNetAll.value,90);});
test('prudential remaining reuses exact normative status and value',()=>{const x=fixture(),m=project(x);near(m.risk.prudentialRemaining.value,1975);x.normative.metrics.prudentialCapacity={status:'PENDING_INPUT',value:null,findings:[]};missing(project(x).risk.prudentialRemaining);});
test('phase leverage ceiling is not per-order admission',()=>{const x=fixture();x.normative.accountPhase=fx.engine.resolveAccountPhase({ddPercent:3});const m=project(x);near(m.risk.leverageLimit.value,fx.policy.phases[1].maxLeverage);assert.strictEqual(m.executionEligibility.status,'BLOCKED');});
test('account capital has source time and scope; book does not borrow observed time',()=>{const x=fixture();x.account.source='Synthetic statement';const m=project(x);assert.strictEqual(m.capital.equity.source.source,'Synthetic statement');assert.strictEqual(m.capital.equity.provenance.observedAt,x.account.observedAt);assert.strictEqual(m.capital.si.provenance.accountId,'A');assert.strictEqual(m.capital.book.provenance.observedAt,null);missing(m.capital.periodResult);});
test('risk and instrument metric provenance carries scope and input sources',()=>{const m=project(fixture([order('a')]));assert.strictEqual(m.risk.open.provenance.periodId,'P');assert.strictEqual(m.risk.open.provenance.orders[0].orderId,'a');assert.strictEqual(m.instruments[0].normal.provenance.instrumentId,'EURUSD');assert.strictEqual(m.instruments[0].normal.provenance.price.source,'Synthetic');});
test('account identification never leaks password',()=>{installState();Object.assign(box.S.accounts[0],{platform:'MetaTrader 5',platformLogin:'000123',investorPassword:'NEVER_OUTPUT'});const m=read();assert.strictEqual(m.accountRecord.platform,'MetaTrader 5');assert.strictEqual(m.accountRecord.login,'000123');assert(!JSON.stringify(m).includes('NEVER_OUTPUT'));});
test('legacy catalogue price remains visible but does not become observed conversion',()=>{installState();const m=read().instruments[0];assert.strictEqual(m.price.kind,'LEGACY_REFERENCE');near(m.price.value,1.25);missing(m.notionalPerLot);assert.strictEqual(m.conversion.baseToAccountRate,null);near(m.conversion.quoteToAccountRate,1);});
test('cross conversion uses exact dated daily legs',()=>{installState();box.S.instruments=[{name:'AUDCAD',preco:9,cpl:100000},{name:'USDCAD',preco:9,cpl:100000}];fx.state.dailyReference=id=>({status:'OK',value:{rate:id==='AUDCAD'?.9:1.35,source:'Synthetic daily',referenceDate:'2026-09-14'}});const i=read().instruments[0];near(i.conversion.quoteToAccountRate,1/1.35);near(i.conversion.baseToAccountRate,.9/1.35);assert.strictEqual(i.conversion.legs.base.length,2);assert(i.conversion.legs.base.every(l=>l.referenceDate==='2026-09-14'));near(i.notionalPerLot.value,100000*.9/1.35);});
test('cross conversion never borrows missing daily leg from legacy price',()=>{installState();box.S.instruments=[{name:'AUDCAD',preco:9,cpl:100000},{name:'USDCAD',preco:1.35,cpl:100000}];fx.state.dailyReference=id=>id==='AUDCAD'?{status:'OK',value:{rate:.9,source:'Synthetic daily',referenceDate:'2026-09-14'}}:{status:'NOT_COMPUTABLE',value:null};const i=read().instruments[0];assert.strictEqual(i.conversion.quoteToAccountRate,null);missing(i.normal);});
test('manual pair observation wins over daily in cross conversion',()=>{installState();box.S.instruments=[{name:'AUDCAD',cpl:100000},{name:'USDCAD',cpl:100000}];fx.state.instrumentContext=q=>q.instrumentId==='AUDCAD'?{status:'OK',value:{price:{value:1.08,source:'Manual cross',observedAt:'2026-09-15T12:00:00Z'}}}:{status:'NOT_COMPUTABLE',value:null};fx.state.dailyReference=id=>({status:'OK',value:{rate:id==='AUDCAD'?.9:1.35,source:'Synthetic daily',referenceDate:'2026-09-14'}});const i=read().instruments[0];near(i.conversion.baseToAccountRate,.8);assert.strictEqual(i.conversion.legs.base[0].kind,'MANUAL');});
test('instrument input helper matches Board without readModel recursion',()=>{installState();fx.orderInputs=()=>{throw Error('forbidden recursion');};fx.state.dailyReference=()=>({status:'OK',value:{rate:1.2,source:'Synthetic daily',referenceDate:'2026-09-14'}});const scope={accountId:'A',periodId:'P'},input=b.instrumentInputs(box.S.instruments[0],box.S.forex.accounts.A,scope),i=read().instruments[0];near(input.contractSize,100000);near(input.conversionRate,1);near(input.notionalConversionRate,1.2);near(input.notionalConversionRate,i.conversion.baseToAccountRate);assert.strictEqual(input.provenance.accountId,'A');});
test('contextual operation without identifier cannot imply known empty exposure',()=>{installState();box.contexts.A.P.activeOperation={recordContext:{accountId:'A',periodId:'P'}};const m=read();missing(m.risk.open);assert.strictEqual(m.selection.lockedToOperation,false);});
test('non-H4 ATR cannot silently calculate stop ATR ratio',()=>{const x=fixture([order('a')]);x.instruments[0].atr.timeframe='D1';missing(project(x).rows[0].atrMultiple);});
test('foreign operation in same account buffers cannot borrow account RC as operation RC',()=>{
 const x=fixture([order('a'),order('b',{operationId:'OTHER'})]);
 const p={side:'BUY',entryPrice:1.1,stopPrice:1,volume:.01,contractSize:100000,conversionRate:1,stopValid:true};
 x.normative.metrics.committedRisk=fx.engine.computeCommittedOperationRisk({positions:[p,p],pendingOrders:[],realizedResults:[],costs:[0,0]});
 near(x.normative.metrics.committedRisk.value,200);
 x.normative.metrics.prudentialCapacity=fx.engine.computePrudentialCapacity({si:10000,ddPercent:3,committedRisk:200});
 near(x.normative.metrics.prudentialCapacity.value,1700);
 const m=project(x);near(m.risk.open.value,100);assert.strictEqual(m.complete,true);assert.strictEqual(m.normativeScopeComplete,false);
 missing(m.risk.committed);missing(m.risk.prudential);missing(m.risk.prudentialRemaining);missing(m.risk.operationBudget);
 assert(m.findings.some(f=>f.code==='BOARD_NORMATIVE_OPERATION_UNRESOLVED'));
});
test('foreign operation exposed only by canonical raw facts still blocks normative attribution',()=>{
 const x=fixture([order('a')]);x.normative.orders={raw:[order('a'),order('b',{operationId:'OTHER'})]};
 const m=project(x);near(m.risk.open.value,100);missing(m.risk.committed);assert.strictEqual(m.normativeScopeComplete,false);
});
test('dedicated account conversion .90 wins over EURUSD-derived .80',()=>{
 installState();Object.assign(box.S.forex.accounts.A,{currency:'EUR',usdToAccountRate:.9,source:'Account conversion A',observedAt:'2026-09-13T12:00:00Z'});
 fx.state.dailyReference=()=>({status:'OK',value:{rate:1.25,source:'Synthetic daily',referenceDate:'2026-09-14'}});
 const i=read().instruments[0],c=i.conversion;near(c.quoteToAccountRate,.9);near(c.baseToAccountRate,1);
 assert.strictEqual(c.selection.quote,'ACCOUNT_OBSERVATION');assert.strictEqual(c.legs.quote.at(-1).source,'Account conversion A');
 assert.strictEqual(c.legs.quote.at(-1).observedAt,'2026-09-13T12:00:00Z');near(c.alternatives.quote[0].value,.8);
 assert.strictEqual(c.alternatives.quote[0].legs[0].referenceDate,'2026-09-14');assert.strictEqual(c.alternatives.quote[0].selected,false);
 assert.strictEqual(c.alternatives.quote[0].differs,true);assert(c.reasons.length>0);
 const rates=b.instrumentInputs(box.S.instruments[0],box.S.forex.accounts.A,{accountId:'A',periodId:'P'});near(rates.conversionRate,.9);
});
test('instrument manual conversion remains ahead of account conversion',()=>{
 installState();Object.assign(box.S.forex.accounts.A,{currency:'EUR',usdToAccountRate:.9,source:'Account conversion',observedAt:'2026-09-13T12:00:00Z'});
 fx.state.instrumentContext=()=>({status:'OK',value:{conversion:{quoteToAccountRate:.88,baseToAccountRate:1.1,source:'Instrument conversion',observedAt:'2026-09-14T12:00:00Z'}}});
 const c=read().instruments[0].conversion;near(c.quoteToAccountRate,.88);near(c.baseToAccountRate,1.1);assert.strictEqual(c.selection.quote,'INSTRUMENT_OBSERVATION');
 assert.strictEqual(c.legs.quote[0].observedAt,'2026-09-14T12:00:00Z');
});
test('dedicated account conversion and time never leak between selected scopes',()=>{
 installState();Object.assign(box.S.forex.accounts.A,{currency:'EUR',usdToAccountRate:.9,source:'Account A',observedAt:'2026-09-12T12:00:00Z'});
 box.S.accounts.push({forexAccountId:'B',nome:'Synthetic B',tipo:'PROPRIA',currency:'EUR'});
 box.S.forex.accounts.B={...box.S.forex.accounts.A,periodId:'Q',usdToAccountRate:.92,source:'Account B',observedAt:'2026-09-13T12:00:00Z'};
 fx.state.dailyReference=()=>({status:'OK',value:{rate:1.25,source:'Synthetic daily',referenceDate:'2026-09-14'}});
 const before=JSON.stringify(box.S),a=b.read({accountId:'A',periodId:'P'}),bb=b.read({accountId:'B',periodId:'Q'});
 near(a.instruments[0].conversion.quoteToAccountRate,.9);near(bb.instruments[0].conversion.quoteToAccountRate,.92);
 assert.strictEqual(a.instruments[0].conversion.legs.quote.at(-1).observedAt,'2026-09-12T12:00:00Z');
 assert.strictEqual(bb.instruments[0].conversion.legs.quote.at(-1).observedAt,'2026-09-13T12:00:00Z');assert.strictEqual(JSON.stringify(box.S),before);
});
test('derived base notional uses dedicated USD-account leg and preserves both times',()=>{
 installState();box.S.instruments.push({name:'GBPUSD',cpl:100000});Object.assign(box.S.forex.accounts.A,{currency:'EUR',usdToAccountRate:.9,source:'Account A',observedAt:'2026-09-12T12:00:00Z'});
 fx.state.dailyReference=id=>({status:'OK',value:{rate:id==='GBPUSD'?1.5:1.25,source:'Synthetic daily',referenceDate:'2026-09-14'}});
 const i=read().instruments.find(x=>x.id==='GBPUSD');near(i.conversion.baseToAccountRate,1.35);near(i.notionalPerLot.value,135000);
 assert.strictEqual(i.conversion.legs.base[0].referenceDate,'2026-09-14');assert.strictEqual(i.conversion.legs.base.at(-1).observedAt,'2026-09-12T12:00:00Z');
 near(i.conversion.alternatives.base[0].value,1.2);
});
// Approved table readings use book balance; the normative SI/equity path stays distinct.
function tableFixture(){
 const x=fixture([order('open',{entry:1.1,sl:1.07,lote:.2}),
  order('def',{status:'Fechada',role:'DEFENSE',result:220,costs:-20}),
  order('other',{status:'Fechada',role:'OTHER',result:500}),
  order('pending',{status:'Pendente',pendingActive:true,amplifiesExposure:true})]);
 x.account.equity=9000;x.accountRecord.satu=12000;x.instruments[0].conversion.baseToAccountRate=1.2;
 return x;
}
test('approved table oracle: 600 and defense200 over book12000; normative bases unchanged',()=>{
 const m=project(tableFixture());near(m.operational.exposure.value,600);near(m.operational.exposure.percent,5);
 near(m.operational.compensated.value,400);near(m.operational.compensated.percent,10/3);
 near(m.operational.grossNotional.value,24000);near(m.operational.leverage.value,2);
 near(m.risk.leverage.value,24000/9000);near(m.risk.open.percent,6);
 near(m.risk.aggregate.value,700);near(m.risk.committed.value,225);near(m.risk.prudentialRemaining.value,1975);
 assert.strictEqual(m.operational.exposure.percentBasis,'BOOK_BALANCE');assert.strictEqual(m.risk.open.percentBasis,'SI');
 near(m.rows[0].operationalRisk.percent,5);near(m.phases[0].metrics.operational.exposure.percent,5);
 assert.strictEqual(m.executionEligibility.status,'BLOCKED');
});
test('gross account notional remains computable without SI or equity',()=>{
 const x=tableFixture();x.account.equity=null;x.account.si=null;const m=project(x);
 near(m.operational.grossNotional.value,24000);near(m.operational.leverage.value,2);
 near(m.operational.exposure.percent,5);missing(m.risk.leverage);assert.strictEqual(m.risk.open.percent,null);
});
for(const balance of [null,undefined,0,-100,'12000',NaN])test('invalid book never borrows SI/equity '+String(balance),()=>{
 const x=tableFixture();x.accountRecord.satu=balance;const m=project(x);
 near(m.operational.exposure.value,600);near(m.operational.compensated.value,400);near(m.operational.grossNotional.value,24000);
 assert.strictEqual(m.operational.exposure.percent,null);assert.strictEqual(m.operational.compensated.percent,null);missing(m.operational.leverage);
 near(m.risk.leverage.value,24000/9000);
});
test('book in another currency cannot become percentage denominator',()=>{
 const x=tableFixture();x.accountRecord.currency='EUR';const m=project(x);missing(m.operational.balance);missing(m.operational.leverage);assert.strictEqual(m.operational.exposure.percent,null);
});
test('compensated defense loss increases exposure and excess gain remains signed',()=>{
 for(const [net,want] of [[-200,800],[800,-200]]){const x=tableFixture();x.rows[1].order.result=net;x.rows[1].order.costs=0;const m=project(x);near(m.operational.compensated.value,want);near(m.operational.compensated.percent,want/120);}
});
test('unclassified closed role keeps defense compensation unresolved',()=>{const x=tableFixture();x.rows[2].order.role='';const m=project(x);missing(m.operational.compensated);near(m.operational.exposure.value,600);});
test('unknown stop preserves notional but never fabricates zero exposure',()=>{const x=tableFixture();x.rows[0].order.stopValidated=false;const m=project(x);missing(m.operational.exposure);missing(m.operational.compensated);near(m.operational.leverage.value,2);});
test('missing conversion taints notional but leaves quote-currency risk known',()=>{const x=tableFixture();x.instruments[0].conversion.baseToAccountRate=null;const m=project(x);missing(m.operational.grossNotional);missing(m.operational.leverage);near(m.operational.exposure.value,600);});
test('gross notional is summed across mixed instruments without netting directions',()=>{
 const x=tableFixture();x.rows=[{pi:0,oi:0,order:order('a',{lote:.1})},{pi:1,oi:0,order:order('b',{par:'GBPUSD',tipo:'SELL',sl:1.2,lote:.1})}];
 x.instruments.push({...x.instruments[0],id:'GBPUSD',name:'GBPUSD',conversion:{baseToAccountRate:1.5,quoteToAccountRate:1}});
 const m=project(x);near(m.operational.grossNotional.value,27000);near(m.operational.leverage.value,2.25);
});
test('ATR multiple and geometry use entry rather than current quote',()=>{
 const x=fixture([order('a',{entry:1.1,sl:1.08,tp:1.16})]);x.instruments[0].price.value=1.15;x.instruments[0].atr.short=.005;
 const r=project(x).rows[0];near(r.atrMultiple.value,4);near(r.geometry.stopDistance.value,.02);near(r.geometry.stopPercent.value,.02/1.1*100);
 near(r.geometry.targetDistance.value,.06);near(r.geometry.targetPercent.value,.06/1.1*100);near(r.geometry.rewardRisk.value,3);
 x.instruments[0].price.value=null;near(project(x).rows[0].atrMultiple.value,4);
});
test('zero stop distance is zero ATR multiple but undefined reward risk',()=>{
 const x=fixture([order('a',{entry:1.1,sl:1.1,tp:1.2})]);const r=project(x).rows[0];near(r.geometry.stopDistance.value,0);near(r.atrMultiple.value,0);missing(r.geometry.rewardRisk);
});
test('geometry absent input never coerces into zero',()=>{for(const field of ['entry','sl']){const x=fixture([order('a',{[field]:null})]);const r=project(x).rows[0];missing(r.geometry.stopDistance);missing(r.atrMultiple);}});
function addDiagnostic(x){x.instruments[0].atr.short=.002;x.instruments[0].diagnostics={accountId:'A',periodId:'P',instrumentId:'EURUSD',oneWeek:{n:25,f:1.5},twoWeeks:{n:100,f:2},revision:1};return x;}
test('root N approved oracle per horizon and entry; policy remains pending',()=>{
 const x=addDiagnostic(fixture([order('a',{entry:1.2})])),before=JSON.stringify(fx.policy.snapshot()),m=project(x);
 near(m.instruments[0].rootN.oneWeek.value,.015);near(m.rows[0].rootN.oneWeek.percent,1.25);
 near(m.instruments[0].rootN.twoWeeks.value,.04);near(m.rows[0].rootN.twoWeeks.percent,10/3);
 assert.strictEqual(m.rows[0].rootN.oneWeek.diagnosticOnly,true);assert.strictEqual(m.rows[0].rootN.oneWeek.calculationMode,'USER_DIAGNOSTIC');
 assert.strictEqual(m.rows[0].rootN.oneWeek.percentBasis,'ENTRY_PRICE');assert.strictEqual(m.rows[0].rootN.oneWeek.n,25);
 assert.strictEqual(fx.policy.get('P-21').value,null);assert.strictEqual(JSON.stringify(fx.policy.snapshot()),before);
});
test('root N horizons are independently absent without fallback',()=>{
 const x=addDiagnostic(fixture([order('a',{entry:1.2})]));delete x.instruments[0].diagnostics.oneWeek;const m=project(x);
 missing(m.rows[0].rootN.oneWeek);near(m.rows[0].rootN.twoWeeks.value,.04);
});
for(const pair of [{n:0,f:1.5},{n:-1,f:1.5},{n:1.5,f:1.5},{n:'25',f:1.5},{n:25,f:0},{n:25,f:-1},{n:25,f:Infinity},{n:25},{f:1.5}])test('invalid explicit root N input '+JSON.stringify(pair),()=>{
 const x=addDiagnostic(fixture([order('a')]));x.instruments[0].diagnostics.oneWeek=pair;missing(project(x).rows[0].rootN.oneWeek);
});
test('root N missing ATR or entry preserves unit-specific availability',()=>{
 const x=addDiagnostic(fixture([order('a',{entry:null})]));let m=project(x);near(m.rows[0].rootN.oneWeek.value,.015);assert.strictEqual(m.rows[0].rootN.oneWeek.percent,null);
 x.instruments[0].atr=null;m=project(x);missing(m.instruments[0].rootN.oneWeek);missing(m.rows[0].rootN.oneWeek);
});
test('diagnostic from another account period or instrument is never borrowed',()=>{
 for(const field of ['accountId','periodId','instrumentId']){const x=addDiagnostic(fixture([order('a')]));x.instruments[0].diagnostics[field]='OTHER';missing(project(x).rows[0].rootN.oneWeek);}
});
test('pure RAM preview exposes only diagnostics and leaves confirmed totals unchanged',()=>{
 const x=addDiagnostic(fixture([order('a',{entry:1.2,sl:1.18})])),m=project(x),before=JSON.stringify(m),o={...m.rows[0].order,entry:1.1,sl:1.09};
 const preview=b.previewOrder(o,m.instruments[0]);near(preview.atrMultiple.value,5);near(preview.rootN.oneWeek.percent,.015/1.1*100);
 assert.deepStrictEqual(Object.keys(preview).sort(),['atrMultiple','geometry','rootN']);assert.strictEqual(JSON.stringify(m),before);
});
test('draft display geometry is available without entry in confirmed exposure',()=>{
 const x=addDiagnostic(fixture([order('d',{entry:1.2,sl:1.18,status:'',recordStatus:'draft'})])),m=project(x);
 assert.strictEqual(m.rows.length,0);near(m.operational.exposure.value,0);near(m.displayRows[0].geometry.stopDistance.value,.02);missing(m.displayRows[0].operationalRisk);
});
test('book source uses current period ledger and not global account balance',()=>{
 installState();box.S.accounts[0].satu=999999;box.contexts.A.P.ledger=[{id:'l2',data:'2026-09-20',saldo:12000,updatedAt:'2026-09-20T12:00:00Z'},{id:'l1',data:'2026-09-19',saldo:11000}];
 const m=read();near(m.operational.balance.value,12000);assert.strictEqual(m.operational.balance.source.referenceDate,'2026-09-20');assert.strictEqual(m.operational.balance.source.ledgerId,'l2');
});
test('registered period balance and quotes allow factual reading before equity observation',()=>{
 installState([order('a')]);delete box.S.forex.accounts.A;
 fx.state.dailyReference=()=>({status:'OK',value:{rate:1.25,source:'Synthetic daily',referenceDate:'2026-09-14'}});
 const m=read();near(m.operational.grossNotional.value,1250);near(m.operational.leverage.value,.125);
 near(m.operational.exposure.value,100);near(m.operational.exposure.percent,1);
 missing(m.risk.leverage);missing(m.capital.equity);missing(m.risk.committed);assert.strictEqual(m.executionEligibility.status,'BLOCKED');
});
test('preview cannot borrow ATR or root N from another instrument',()=>{
 const m=project(addDiagnostic(fixture([order('a')]))),preview=b.previewOrder({...m.rows[0].order,par:'GBPUSD'},m.instruments[0]);
 missing(preview.atrMultiple);missing(preview.rootN.oneWeek);near(preview.geometry.stopDistance.value,.1);
});
test('operational denominator overflow stays unavailable instead of nonfinite percentage',()=>{
 const x=tableFixture();x.accountRecord.satu=Number.MIN_VALUE;const m=project(x);missing(m.operational.leverage);assert.strictEqual(m.operational.exposure.percent,null);
});
test('diagnostics lookup uses exact selected account period instrument without writes',()=>{
 installState([order('a',{entry:1.2})]);let asked;fx.state.executionDiagnostics=q=>{asked=q;return {status:'OK',value:{...q,oneWeek:{n:25,f:1.5},twoWeeks:null,revision:1}};};
 fx.state.instrumentContext=()=>({status:'OK',value:{atr:{short:.002,long:.004,timeframe:'H4',unit:'PRICE'}}});
 const m=read();near(m.rows[0].rootN.oneWeek.value,.015);assert.deepStrictEqual(plain(asked),{accountId:'A',periodId:'P',operationId:'OP',currency:'USD',instrumentId:'EURUSD'});
});
const failed=checks.filter(x=>x.result!=='PASS');console.log(JSON.stringify({checks,counts:{total:checks.length,passed:checks.length-failed.length,failed:failed.length},result:failed.length?'PRODUCT_FAIL':'PASS'}));process.exitCode=failed.length?1:0;
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
                   returncode=completed.returncode, stderr=completed.stderr, environment="Node VM; no DOM/storage/network capabilities",
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
