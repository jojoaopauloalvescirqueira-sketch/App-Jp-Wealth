#!/usr/bin/env python3
"""Scoped observations and daily-reference transactions; synthetic Node VM, no network.

Runs production state/controller/order recording with an explicit persistence
double. Browser writer/backup/finalization protocols retain their own focals.
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
    'src/js/00-core/00-forex-policy.js',
    'src/js/00-core/01-risk-profiles.js',
    'src/js/10-domain/00-forex-engine.js',
    'src/js/10-domain/00-forex-state.js',
    'src/js/10-domain/19-execution-market.js',
    'src/js/10-domain/11-operation-lifecycle.js',
]
PROBE = r"""
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto').webcrypto;
const files=process.argv.slice(1),checks=[];
const ISO='2026-09-15T20:00:00.000Z',OBS='2026-09-15T12:00:00.000Z';
class Clock extends Date{constructor(...args){super(...(args.length?args:[ISO]));}static now(){return Date.parse(ISO);}}
function env(){
  const handlers={};let saves=0,disk=null,mode='ok',epoch=1,unknown=false,blocked=false,calls=0;
  const c={structuredClone,Date:Clock,crypto,AbortController,setTimeout,clearTimeout,console,
    addEventListener:(name,fn)=>{handlers[name]=fn;},dispatchEvent:()=>{},forexNewOperationPhases:()=>[],
    jpWealthPersistenceEpoch:()=>epoch,jpWealthPersistenceIsBlocked:()=>blocked,
    jpWealthPersistenceOutcomeIsUnknown:()=>unknown,markJPWealthPersistenceOutcomeUnknown:()=>{unknown=true;},
    save:()=>{saves++;if(mode==='refuse')return false;if(mode==='throw')throw new Error('synthetic unknown');
      if(mode==='nonboolean')return undefined;disk=JSON.stringify(c.S);return true;},
    fetch:async url=>{calls++;const parts=url.match(/\/rate\/([A-Z]{3})\/([A-Z]{3})$/);assert(parts,'only approved daily endpoint');
      return {ok:true,status:200,json:async()=>({base:parts[1],quote:parts[2],date:'2026-09-15',rate:1.25})};},
    operationTouchAccountPhase:()=>{},operationOrderIsLive:o=>!!o&&['Aberta','Fechada','Pendente'].includes(o.status),
    instFor:name=>c.S.instruments.find(i=>i.name===name),
    operationOnOrderStatus:()=>{if(!c.S.activeOperation)c.S.activeOperation={operationId:'operation-synthetic',schemaVersion:1};},
    operationRecordId:()=> 'operation-synthetic',
    operationLiveOrders:()=>c.S.phases.flatMap((p,pi)=>p.orders.map((o,oi)=>({pi,oi,o}))).filter(x=>c.operationOrderIsLive(x.o))};
  c.window=c;vm.createContext(c);for(const file of files)vm.runInContext(fs.readFileSync(file,'utf8'),c,{filename:file});
  c.JPWForex.orderInputs=()=>({stopValid:true,contractSize:100000});
  c.S={accounts:[{forexAccountId:'A',tipo:'MESTRE'},{forexAccountId:'B',tipo:'SATELITE'}],
    forex:c.JPWForex.state.empty(),instruments:[{name:'EURUSD',preco:9,cpl:100000},{name:'GBPUSD',preco:8,cpl:100000}],
    phases:[{orders:[{par:'EURUSD',tipo:'BUY',status:'',lote:0,entry:0,sl:0,tp:0}]}],
    activeOperation:null,transitionLog:[],dataGovernance:{changeLog:[]},unrelated:{keep:'synthetic'}};
  c.S.forex.accounts={A:{periodId:'A1',currency:'USD',si:10000,equity:9700,source:'synthetic',observedAt:OBS},
    B:{periodId:'B1',currency:'USD',si:20000,equity:19000,source:'synthetic',observedAt:OBS}};
  c.S.forex.activeAccountId='A';c.S.forex.market={atrShort:99,atrLong:1,source:'legacy-global',observedAt:OBS};
  return {c,fx:c.JPWForex,handlers,get saves(){return saves},get disk(){return disk},get calls(){return calls},
    mode:v=>{mode=v},epoch:v=>{epoch=v},blocked:v=>{blocked=v},unknown:()=>unknown};
}
const scope=(extra={})=>({accountId:'A',periodId:'A1',instrumentId:'EURUSD',...extra});
const component=(key,value)=>key==='atr'?{short:value,long:.01,timeframe:'H4',unit:'PRICE',source:'synthetic manual',observedAt:OBS}:
  key==='contract'?{contractSize:value,source:'synthetic manual',observedAt:OBS}:{value,source:'synthetic manual',observedAt:OBS};
function write(e,key='price',value=1.2,extra={}){
  return e.fx.state.recordInstrumentContext({...scope(),expectedRevision:0,componentChanges:{[key]:component(key,value)},...extra},
    {reason:'synthetic explicit observation',expectedEpoch:1});
}
function quote(rate=1.25,extra={}){return {base:'EUR',quote:'USD',rate,referenceDate:'2026-09-15',fetchedAt:ISO,source:'Frankfurter',sourceKind:'DAILY_REFERENCE',...extra};}
function direct(e,rate=1.25,extra={}){return e.fx.state.recordDailyReferences({quotes:{EURUSD:quote(rate)},expectedRevision:0,expectedEpoch:1,...extra});}
function rejected(r){assert.strictEqual(r.ok,false);assert.strictEqual(r.persistido,false);}
function missing(r){assert.strictEqual(r.status,'NOT_COMPUTABLE');assert.strictEqual(r.value,null);}
async function test(name,fn){let fixture;try{fixture=env();}catch(error){checks.push({name,result:'TEST_HARNESS_FAIL',error:String(error.stack||error)});return;}
  try{await fn(fixture);checks.push({name,result:'PASS'});}catch(error){checks.push({name,result:'PRODUCT_FAIL',error:String(error.stack||error)});}}
(async()=>{
await test('legacy global observations remain byte-identical and unassigned on read',e=>{
  const before=JSON.stringify(e.c.S);missing(e.fx.state.instrumentContext(scope()));
  assert.strictEqual(e.fx.state.recordContext().marketInputs,null);assert.strictEqual(e.fx.state.recordContext(scope()).marketInputs,null);
  assert.strictEqual(JSON.stringify(e.c.S),before);assert.strictEqual(e.saves,0);
});
await test('exact scope preserves separate accounts instruments and periods',e=>{
  assert(write(e).ok);missing(e.fx.state.instrumentContext(scope({accountId:'B',periodId:'B1'})));
  missing(e.fx.state.instrumentContext(scope({instrumentId:'GBPUSD'})));missing(e.fx.state.instrumentContext(scope({periodId:'A0'})));
  missing(e.fx.state.instrumentContext(scope({currency:'BRL'})));
  missing(e.fx.state.instrumentContext(null));assert.strictEqual(e.c.S.forex.activeAccountId,'A');
  assert.strictEqual(e.fx.state.instrumentContext(scope()).value.price.sourceKind,'MANUAL');
});
await test('component edits retain previous prices ATR source and revision history',e=>{
  assert(write(e).ok);assert(write(e,'atr',.012,{expectedRevision:1}).ok);
  const r=e.fx.state.instrumentContext(scope());assert.strictEqual(r.revision,2);assert.strictEqual(r.value.price.value,1.2);
  assert.strictEqual(r.value.previous.revision,1);assert.strictEqual(r.value.previous.atr,undefined);
  assert.strictEqual(e.fx.state.recordContext(scope()).marketInputs.atrShort,.012);
  r.value.price.value=999;assert.strictEqual(e.fx.state.instrumentContext(scope()).value.price.value,1.2);
});
await test('registration changed period duplicate and unknown instruments refuse atomically',e=>{
  for(const mutate of [()=>{e.c.S.accounts=[]},()=>{e.c.S.forex.accounts.A.periodId='A2'},()=>{e.c.S.accounts.push({forexAccountId:'A'})}]){
    const before=structuredClone(e.c.S);mutate();const altered=JSON.stringify(e.c.S);rejected(write(e));assert.strictEqual(JSON.stringify(e.c.S),altered);e.c.S=before;
  }
  rejected(write(e,'price',1,{instrumentId:'UNKNOWN'}));assert.strictEqual(e.saves,0);
});
await test('stale revision and epoch refuse without replacing observation',e=>{
  assert(write(e).ok);let before=JSON.stringify(e.c.S);rejected(write(e,'price',2));assert.strictEqual(JSON.stringify(e.c.S),before);
  e.epoch(2);rejected(write(e,'price',2,{expectedRevision:1}));assert.strictEqual(JSON.stringify(e.c.S),before);
});
await test('invalid zero negative future and malformed source observations refuse',e=>{
  for(const value of [0,-1,Infinity,NaN])rejected(write(e,'price',value));
  rejected(write(e,'price',1,{componentChanges:{price:{value:1,source:'x',observedAt:'2027-01-01'}}}));
  rejected(write(e,'atr',.1,{componentChanges:{atr:{short:.1,long:.2,timeframe:'D1',unit:'PRICE',source:'x',observedAt:OBS}}}));
  assert.strictEqual(e.saves,0);
});
await test('refused observation restores document and permits explicit retry',e=>{
  const before=JSON.stringify(e.c.S);e.mode('refuse');rejected(write(e));assert.strictEqual(JSON.stringify(e.c.S),before);
  e.mode('ok');assert(write(e).ok);assert.strictEqual(JSON.parse(e.disk).forex.instrumentContexts.records.length,1);
});
await test('unknown observation does not roll back or permit blind retry',e=>{
  e.mode('throw');const r=write(e);assert.strictEqual(r.persistido,null);assert(e.unknown());assert(e.c.S.forex.instrumentContexts);
  const before=e.saves;assert.strictEqual(write(e).persistido,null);assert.strictEqual(e.saves,before);
});
await test('future or malformed nested schemas remain intact and block writes',e=>{
  for(const value of [{schemaVersion:99,records:[]},{schemaVersion:1,records:[{}]}]){
    e.c.S.forex.instrumentContexts=value;const before=JSON.stringify(e.c.S);assert(!e.fx.state.supported());rejected(write(e));assert.strictEqual(JSON.stringify(e.c.S),before);
  }
  delete e.c.S.forex.instrumentContexts;e.c.S.forex.dailyReferences={schemaVersion:99,revision:0,quotes:{}};
  assert(!e.fx.state.supported());assert(!e.fx.state.supported(structuredClone(e.c.S.forex)));
});
await test('daily reference validation preserves pair date and positive-rate identity',e=>{
  for(const q of [quote(0),quote(-2),quote(1,{base:'GBP'}),quote(1,{referenceDate:'2026-02-30'}),quote(1,{referenceDate:'2026-09-16'}),quote(1,{source:'unrecognized'})])
    rejected(direct(e,1,{quotes:{EURUSD:q}}));
  assert.strictEqual(e.saves,0);assert(direct(e).ok);assert.strictEqual(e.fx.state.dailyReference('EURUSD').value.referenceDate,'2026-09-15');
});
await test('daily update is atomic and never overwrites manual values or global legacy',async e=>{
  assert(write(e,'atr',.012).ok);assert(write(e,'price',1.4,{expectedRevision:1}).ok);
  const global=JSON.stringify(e.c.S.instruments),manual=JSON.stringify(e.c.S.forex.instrumentContexts),legacy=JSON.stringify(e.c.S.forex.market);
  const count=e.saves,r=await e.fx.marketQuotes.update();assert(r.ok);assert.strictEqual(e.saves,count+1);assert.strictEqual(e.calls,8);
  assert.strictEqual(JSON.stringify(e.c.S.instruments),global);assert.strictEqual(JSON.stringify(e.c.S.forex.instrumentContexts),manual);
  assert.strictEqual(JSON.stringify(e.c.S.forex.market),legacy);assert.strictEqual(e.fx.marketQuotes.get().busy,false);
});
await test('same daily observation keeps raw revision audit and confirmation timestamp unchanged',e=>{
  assert(direct(e,1.25,{quotes:{EURUSD:quote(1.25,{fetchedAt:'2026-09-15T19:00:00.000Z'})}}).ok);
  const before=JSON.stringify(e.c.S),disk=e.disk,saves=e.saves;
  e.c.S=JSON.parse(before);const r=direct(e,1.25,{expectedRevision:1});
  assert(r.ok);assert.strictEqual(r.persistido,false);assert.strictEqual(r.unchanged,true);
  assert.strictEqual(JSON.stringify(e.c.S),before);assert.strictEqual(e.disk,disk);assert.strictEqual(e.saves,saves);
  assert.strictEqual(e.fx.state.dailyReference('EURUSD').value.fetchedAt,'2026-09-15T19:00:00.000Z');
});
await test('unchanged quote batch still enforces revision epoch and persistence barriers',e=>{
  assert(direct(e).ok);const before=JSON.stringify(e.c.S),saves=e.saves;
  rejected(direct(e));rejected(direct(e,1.25,{expectedRevision:1,expectedEpoch:2}));
  e.blocked(true);rejected(direct(e,1.25,{expectedRevision:1}));
  assert.strictEqual(JSON.stringify(e.c.S),before);assert.strictEqual(e.saves,saves);
});
await test('repeated controller update reports unchanged without new persistence',async e=>{
  assert((await e.fx.marketQuotes.update()).ok);const before=JSON.stringify(e.c.S),disk=e.disk,saves=e.saves;
  const r=await e.fx.marketQuotes.update();assert(r.ok);assert.strictEqual(r.persistido,false);assert.strictEqual(r.status,'UNCHANGED');
  assert.strictEqual(r.updated,0);assert.match(r.message,/nenhuma alteração/);assert.strictEqual(e.calls,16);
  assert.strictEqual(JSON.stringify(e.c.S),before);assert.strictEqual(e.disk,disk);assert.strictEqual(e.saves,saves);
});
await test('partial daily batch retains last confirmed failed pair',async e=>{
  assert(direct(e,1.8).ok);const original=e.c.fetch;e.c.fetch=async url=>url.endsWith('/EUR/USD')?{ok:false,status:429}:original(url);
  const r=await e.fx.marketQuotes.update();assert(r.ok);assert.strictEqual(r.status,'PARTIAL');assert.strictEqual(r.updated,7);assert.strictEqual(r.failed,1);
  assert.strictEqual(e.fx.state.dailyReference('EURUSD').value.rate,1.8);
});
await test('refused daily save keeps batch in RAM and retry performs no second fetch',async e=>{
  const before=JSON.stringify(e.c.S);e.mode('refuse');const r=await e.fx.marketQuotes.update();rejected(r);
  assert.strictEqual(JSON.stringify(e.c.S),before);assert.strictEqual(e.fx.marketQuotes.get().pendingCount,8);
  assert.strictEqual(e.fx.marketQuotes.get().canRetry,true);await e.fx.marketQuotes.update();assert.strictEqual(e.calls,8);
  e.mode('ok');assert((await e.fx.marketQuotes.retry()).ok);assert.strictEqual(e.calls,8);assert.strictEqual(e.fx.marketQuotes.get().pendingCount,0);
});
await test('daily unknown freezes retry and preserves possibly persisted candidate',async e=>{
  e.mode('nonboolean');const r=await e.fx.marketQuotes.update();assert.strictEqual(r.persistido,null);assert(e.unknown());
  const count=e.saves;await e.fx.marketQuotes.retry();assert.strictEqual(e.saves,count);assert(e.c.S.forex.dailyReferences);
});
await test('coalesced update does not duplicate parallel requests',async e=>{
  const a=e.fx.marketQuotes.update(),b=e.fx.marketQuotes.update();assert.strictEqual(a,b);await a;assert.strictEqual(e.calls,8);assert.strictEqual(e.saves,1);
});
await test('late result after epoch replacement cannot recreate financial state',async e=>{
  const original=e.c.fetch;let release;e.c.fetch=url=>new Promise(resolve=>{const prev=release;release=()=>{if(prev)prev();resolve(original(url));};});
  const p=e.fx.marketQuotes.update();e.epoch(2);e.c.S.forex=e.fx.state.empty();const before=JSON.stringify(e.c.S);release();await p;
  assert.strictEqual(e.saves,0);assert.strictEqual(JSON.stringify(e.c.S),before);assert.strictEqual(e.fx.marketQuotes.get().pendingCount,0);
});
await test('cancel aborts pending network and never records results',async e=>{
  e.c.fetch=()=>new Promise(()=>{});const p=e.fx.marketQuotes.update();e.fx.marketQuotes.cancel();await p;
  assert.strictEqual(e.saves,0);assert.strictEqual(e.fx.marketQuotes.get().status,'CANCELLED');
});
await test('timeout releases resources and reports failure without a state write',async e=>{
  e.c.setTimeout=(fn,ms)=>setTimeout(fn,ms===6000?20:ms);e.c.fetch=()=>new Promise(()=>{});
  const r=await e.fx.marketQuotes.update();assert.strictEqual(r.status,'FAILED');assert.strictEqual(r.failed,8);
  assert.strictEqual(e.saves,0);assert.strictEqual(e.fx.marketQuotes.get().busy,false);
});
await test('epoch replacement discards refused pending RAM and disables retry',async e=>{
  e.mode('refuse');await e.fx.marketQuotes.update();assert.strictEqual(e.fx.marketQuotes.get().pendingCount,8);
  e.epoch(2);e.c.S.forex=e.fx.state.empty();assert.strictEqual(e.fx.marketQuotes.get().pendingCount,0);
  assert.strictEqual(e.fx.marketQuotes.get().canRetry,false);const count=e.saves;rejected(await e.fx.marketQuotes.retry());assert.strictEqual(e.saves,count);
});
await test('bad network identity future date and zero produce explicit failures',async e=>{
  e.c.fetch=async()=>({ok:true,status:200,json:async()=>({base:'WRONG',quote:'USD',rate:0,date:'2026-02-30'})});
  const r=await e.fx.marketQuotes.update();assert.strictEqual(r.status,'FAILED');assert.strictEqual(r.failed,8);assert.strictEqual(e.saves,0);
});
await test('manual edit while references in flight keeps its own source and value',async e=>{
  const original=e.c.fetch;let release;e.c.fetch=url=>new Promise(resolve=>{const prev=release;release=()=>{if(prev)prev();resolve(original(url));};});
  const p=e.fx.marketQuotes.update();assert(write(e,'price',1.7).ok);release();await p;
  assert.strictEqual(e.fx.state.instrumentContext(scope()).value.price.value,1.7);assert.strictEqual(e.fx.state.dailyReference('EURUSD').value.rate,1.25);
});
await test('stale reference revision refuses rather than overwriting newer batch',async e=>{
  e.mode('refuse');await e.fx.marketQuotes.update();e.mode('ok');assert(direct(e,1.9).ok);
  rejected(await e.fx.marketQuotes.retry());assert.strictEqual(e.fx.state.dailyReference('EURUSD').value.rate,1.9);
});
await test('old provider date cannot replace a newer saved daily reference',e=>{
  assert(direct(e).ok);const before=JSON.stringify(e.c.S);rejected(direct(e,1,{expectedRevision:1,quotes:{EURUSD:quote(1,{referenceDate:'2026-09-14'})}}));
  assert.strictEqual(JSON.stringify(e.c.S),before);
});
await test('new operation captures chosen account and observational snapshots in one write',e=>{
  assert(write(e).ok);assert(direct(e).ok);e.c.S.forex.activeAccountId='B';const count=e.saves;
  const r=e.c.operationRecordOrders([{pi:0,oi:0,expectedVersion:0,orderId:null,changes:{status:'Aberta',lote:.01,entry:1.2,sl:1.1}}],{reason:'synthetic first fact',accountId:'A',periodId:'A1'});
  assert(r.ok,r.error);assert.strictEqual(e.saves,count+1);assert.strictEqual(e.c.S.forex.activeAccountId,'A');
  const o=e.c.S.phases[0].orders[0];assert.strictEqual(o.accountId,'A');assert.strictEqual(o.calculationInputs.instrumentObservation.price.value,1.2);
  const snapshot=JSON.stringify(o.calculationInputs);assert(write(e,'price',1.4,{expectedRevision:1}).ok);assert.strictEqual(JSON.stringify(o.calculationInputs),snapshot);
});
await test('existing operation cannot transfer by explicit selected scope',e=>{
  e.c.S.activeOperation={operationId:'existing',recordContext:{accountId:'A',periodId:'A1',accountInputs:e.c.S.forex.accounts.A}};
  const before=JSON.stringify(e.c.S);const r=e.c.operationRecordOrders([{pi:0,oi:0,changes:{status:'Aberta',lote:.01}}],{reason:'synthetic',accountId:'B',periodId:'B1'});
  rejected(r);assert.strictEqual(JSON.stringify(e.c.S),before);
});
await test('row version mismatch refuses before persistence',e=>{
  const r=e.c.operationRecordOrders([{pi:0,oi:0,expectedVersion:3,changes:{lote:.01}}],{reason:'synthetic'});assert.strictEqual(r.ok,false);assert.strictEqual(e.saves,0);
});
await test('refused first fact restores chosen account and snapshots atomically',e=>{
  e.c.S.forex.activeAccountId='B';e.mode('refuse');const before=JSON.stringify(e.c.S);
  rejected(e.c.operationRecordOrders([{pi:0,oi:0,changes:{status:'Aberta',lote:.01}}],{reason:'synthetic',accountId:'A',periodId:'A1'}));
  assert.strictEqual(JSON.stringify(e.c.S),before);
});
await test('JSON roundtrip retains unknown fields scope revisions references and unrelated data',e=>{
  assert(write(e).ok);assert(write(e,'atr',.012,{expectedRevision:1}).ok);assert(direct(e).ok);
  e.c.S.forex.instrumentContexts.extension={keep:true};const before=JSON.stringify(e.c.S),copy=JSON.parse(before);
  assert(e.fx.state.supported(copy.forex));e.c.S=copy;assert.strictEqual(JSON.stringify(e.c.S),before);
  assert.strictEqual(e.fx.state.instrumentContext(scope()).value.previous.price.value,1.2);
});
const failed=checks.filter(x=>x.result!=='PASS');console.log(JSON.stringify({checks,counts:{total:checks.length,passed:checks.length-failed.length,failed:failed.length},result:failed.length?'PRODUCT_FAIL':'PASS'}));process.exitCode=failed.length?1:0;
})().catch(error=>{console.error(error);process.exitCode=1;});
"""


def run(root=ROOT):
    paths = [root / name for name in INPUTS]
    before = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in zip(INPUTS, paths)}
    node = shutil.which('node')
    if not node:
        raise RuntimeError('ENVIRONMENT_ERROR: existing Node runtime unavailable')
    completed = subprocess.run([node, '-e', PROBE, *map(str, paths)], cwd=root, capture_output=True, text=True)
    after = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in zip(INPUTS, paths)}
    if before != after:
        raise RuntimeError('Inputs changed during focal test')
    result = json.loads(completed.stdout)
    result.update(root=str(root), source_hashes=before,
                  environment='Node VM; synthetic in-memory writer and intercepted fetch; no financial API',
                  test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if completed.stderr:
        result['stderr'] = completed.stderr
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out and args.out.exists():
        parser.error('Evidence exists; select a new path')
    result = run(args.root.resolve())
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['result'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
