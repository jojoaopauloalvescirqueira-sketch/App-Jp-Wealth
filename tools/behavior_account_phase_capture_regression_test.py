#!/usr/bin/env python3
"""Real account-period fact transactions preserve observed operation phase peaks."""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from dashboard_macro_test import launch_browser

ROOT = Path(__file__).resolve().parents[1]
FILES = ('src/js/00-core/04-persistence.js', 'src/js/10-domain/00-forex-state.js')
SETUP = r"""() => {
 closeModal();S.onboarding.done=true;
 S.accounts=[{forexAccountId:'PHASE-A',nome:'Synthetic phase A',tipo:'MESTRE',platformCurrency:'USD'},
 {forexAccountId:'PHASE-B',nome:'Synthetic phase B',tipo:'PRÓPRIA',platformCurrency:'USD'}];
 S.forex=JPWForex.state.empty();S.activeOperation=null;
 const api=JPWForex.state, yes=value=>{if(!value.ok)throw Error(JSON.stringify(value));return value;};
 for(const accountId of ['PHASE-A','PHASE-B'])yes(api.recordAccountPeriod({accountId,startedAt:'2026-09-01',currency:'USD',si:10000,openingBook:10000,source:'Synthetic phase test',activateCurrentPeriod:true},{reason:'Explicit synthetic period'}));
 window.__phaseScope=id=>({accountId:id,periodId:S.forex.accountContexts.accounts[id].currentPeriodId});
 window.__phasePeriod=id=>S.forex.accountContexts.accounts[id].periods[__phaseScope(id).periodId];
 window.__phaseObserve=(id,equity,at)=>api.recordAccountFacts({accountIndex:id==='PHASE-A'?0:1,periodId:__phaseScope(id).periodId,si:10000,equity,netCashflow:0,currency:'USD',source:'Synthetic confirmed equity',observedAt:at},{reason:'Explicit synthetic observation',preserveSelection:true});
 yes(__phaseObserve('PHASE-A',10000,'2026-09-12T00:00:00Z'));yes(__phaseObserve('PHASE-B',10000,'2026-09-12T00:00:00Z'));
 window.__phaseRecord=(id)=>api.recordAccountOrders([{pi:0,oi:0,changes:{id:id+'-FACT',brokerHash:'SYNTHETIC-'+id,par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:.01,entry:1.1,sl:1,tp:1.2,status:'Fechada',result:5,costs:0,costBasis:'INCLUDED_IN_RESULT'}}],{...__phaseScope(id),reason:'Explicit synthetic operation fact'});
 yes(__phaseRecord('PHASE-A'));yes(__phaseRecord('PHASE-B'));yes(api.selectOperationalContext('PHASE-B',__phaseScope('PHASE-B').periodId));
 window.__phaseWriteCount=0;window.__phaseNativePut=Storage.prototype.setItem;window.__phaseNativeGet=Storage.prototype.getItem;
 Storage.prototype.setItem=function(key,value){if(this===localStorage&&key===LSKEY)__phaseWriteCount++;return __phaseNativePut.call(this,key,value);};
 render();return {birthA:__phasePeriod('PHASE-A').activeOperation.maxAccountPhaseReached??null,birthB:__phasePeriod('PHASE-B').activeOperation.maxAccountPhaseReached??null,selected:api.operationalSelection(),global:S.activeOperation};
}"""

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--artifact',type=Path,required=True)
    args=parser.parse_args();args.artifact.parent.mkdir(parents=True,exist_ok=True)
    server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(args.root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    rows=[]
    def check(name,ok,observations):
        rows.append({'name':name,'status':'PASS' if ok else 'PRODUCT_FAIL','observations':observations})
    with sync_playwright() as pw:
      browser=launch_browser(pw)
      for scenario in ('peak-recovery','refusal-retry','unknown','capture-fault'):
       context=browser.new_context(service_workers='block');install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
       page=context.new_page();errors=[];console=[];page.on('pageerror',lambda error:errors.append(str(error)));page.on('console',lambda msg:console.append(msg.text) if msg.type=='error' else None)
       try:
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page);birth=page.evaluate(SETUP)
        if scenario=='peak-recovery':
         check('recorded operation captures its own known birth phase',birth['birthA']==birth['birthB']==0 and birth['global'] is None,birth)
         result=page.evaluate(r"""() => {
          const api=JPWForex.state,beforeB=JSON.stringify(__phasePeriod('PHASE-B'));
          const peak=__phaseObserve('PHASE-A',8000,'2026-09-12T04:00:00Z'),maxAtPeak=__phasePeriod('PHASE-A').activeOperation.maxAccountPhaseReached??null;
          const h4a=api.recordH4({ddPercent:0,closedAt:'2026-09-12T08:00:00Z',source:'Synthetic H4'},{target:__phaseScope('PHASE-A'),reason:'Explicit H4 close'});
          const h4b=api.recordH4({ddPercent:0,closedAt:'2026-09-12T12:00:00Z',source:'Synthetic H4'},{target:__phaseScope('PHASE-A'),reason:'Explicit H4 close'});
          const recovery=__phaseObserve('PHASE-A',10000,'2026-09-12T16:00:00Z'),maxAfterRecovery=__phasePeriod('PHASE-A').activeOperation.maxAccountPhaseReached??null;
          const current=api.read(__phaseScope('PHASE-A')).accountPhase.value,selected=api.operationalSelection();
          const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),writes=__phaseWriteCount;
          for(let i=0;i<3;i++){api.read(__phaseScope('PHASE-A'));api.accountContext(__phaseScope('PHASE-A'));render();}
          const pure=before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY)&&writes===__phaseWriteCount;
          const bSame=beforeB===JSON.stringify(__phasePeriod('PHASE-B'));
          api.selectOperationalContext('PHASE-A',__phaseScope('PHASE-A').periodId);JPWOperation.openReview();
          const finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
          return {peak,h4a,h4b,recovery,maxAtPeak,maxAfterRecovery,current,selected,pure,bSame,finalized,history:S.operationHistory.records.map(r=>({accountId:r.accountId,max:r.maxAccountPhaseReached,integrity:r.maxAccountPhaseIntegrity})),disk:JSON.parse(localStorage.getItem(LSKEY)).operationHistory.records.map(r=>r.maxAccountPhaseReached)};
         }""")
         valid=all(result[k]['ok'] for k in ('peak','h4a','h4b','recovery'))
         check('DD20 percent peak survives recovery to phase1',valid and result['current']==1 and result['maxAtPeak']==result['maxAfterRecovery']==5,result)
         check('explicit observation A preserves operational B and its operation',result['selected']['accountId']=='PHASE-B' and result['bSame'],result)
         check('phase consultation and rendering never capture or write facts',result['pure'],result)
         check('confirmed finalization preserves peak5 in immutable history and disk',result['finalized']['ok'] and result['history']==[{'accountId':'PHASE-A','max':5,'integrity':'observed'}] and result['disk']==[5],result)
         expected=page.evaluate('structuredClone(S.operationHistory.records)');page.reload();wait_bootstrap(page)
         check('reload preserves exact captured history',page.evaluate('structuredClone(S.operationHistory.records)')==expected,{'expected':expected})
        elif scenario=='refusal-retry':
         result=page.evaluate(r"""() => {
          const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),put=Storage.prototype.setItem;
          Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===LSKEY)throw new DOMException('Synthetic quota refusal','QuotaExceededError');return put.call(this,k,v);};
          const refused=__phaseObserve('PHASE-A',8000,'2026-09-12T04:00:00Z');Storage.prototype.setItem=put;
          const rollback=before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY),retry=__phaseObserve('PHASE-A',8000,'2026-09-12T04:00:00Z');
          return {refused,rollback,retry,max:__phasePeriod('PHASE-A').activeOperation.maxAccountPhaseReached??null,diskMax:JSON.parse(localStorage.getItem(LSKEY)).forex.accountContexts.accounts['PHASE-A'].periods[__phaseScope('PHASE-A').periodId].activeOperation.maxAccountPhaseReached??null};
         }""")
         check('physical refusal rolls back observation and prospective phase together',not result['refused']['ok'] and result['refused']['persistido'] is False and result['rollback'],result)
         check('explicit retry captures peak once in confirmed RAM and disk',result['retry']['ok'] and result['max']==result['diskMax']==5,result)
        elif scenario=='unknown':
         result=page.evaluate(r"""() => {
          const put=Storage.prototype.setItem,get=Storage.prototype.getItem;let armed=false;
          Storage.prototype.setItem=function(k,v){const r=put.call(this,k,v);if(this===localStorage&&k===LSKEY)armed=true;return r;};
          Storage.prototype.getItem=function(k){if(this===localStorage&&k===LSKEY&&armed)throw new DOMException('Synthetic post-write read failure','SecurityError');return get.call(this,k);};
          const unknown=__phaseObserve('PHASE-A',8000,'2026-09-12T04:00:00Z');Storage.prototype.setItem=put;Storage.prototype.getItem=get;
          const candidate=JSON.stringify(S),raw=get.call(localStorage,LSKEY),writes=__phaseWriteCount;
          const retry=__phaseObserve('PHASE-A',10000,'2026-09-12T16:00:00Z');
          return {unknown,retry,blocked:jpWealthPersistenceOutcomeIsUnknown(),same:candidate===JSON.stringify(S)&&raw===get.call(localStorage,LSKEY)&&writes===__phaseWriteCount,max:__phasePeriod('PHASE-A').activeOperation.maxAccountPhaseReached??null,physicalWrites:writes};
         }""")
         check('post-write UNKNOWN preserves candidate peak and refuses blind retry',not result['unknown']['ok'] and result['unknown']['persistido'] is None and result['blocked'] and not result['retry']['ok'] and result['same'] and result['max']==5 and result['physicalWrites']==1,result)
        else:
         result=page.evaluate(r"""() => {
          const read=JPWForex.state.read;JPWForex.state.read=()=>{throw Error('Synthetic phase reader defect');};
          const degraded=__phaseObserve('PHASE-A',8000,'2026-09-12T04:00:00Z');JPWForex.state.read=read;
          const fault=structuredClone(__phasePeriod('PHASE-A').activeOperation.phaseCaptureFault||null);
          const retry=__phaseObserve('PHASE-A',8000,'2026-09-12T08:00:00Z');
          return {degraded,retry,fault,faultPreserved:JSON.stringify(fault)===JSON.stringify(__phasePeriod('PHASE-A').activeOperation.phaseCaptureFault||null),max:__phasePeriod('PHASE-A').activeOperation.maxAccountPhaseReached??null,bFault:__phasePeriod('PHASE-B').activeOperation.phaseCaptureFault||null};
         }""")
         check('capture defect stays visible after a later successful observation',result['degraded']['ok'] and result['retry']['ok'] and result['fault'] is not None and result['faultPreserved'] and result['max']==5 and result['bFault'] is None,result)
        assert_fixture_requests(context);check(scenario+' has no uncaught script errors',not errors,{'errors':errors,'console_errors':console})
       finally:context.close()
      browser.close()
    server.shutdown();server.server_close()
    counts={s:sum(r['status']==s for r in rows)for s in ('PASS','PRODUCT_FAIL')}
    out={'root':str(args.root.resolve()),'files':{f:hashlib.sha256((args.root/f).read_bytes()).hexdigest()for f in FILES},'testHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'summary':counts,'results':rows,'scope':'Real account-period commands, nominal synthetic bootstrap, actual physical writer refusal/readback UNKNOWN injection and guarded finalization; no formulas/schema changed.'}
    args.artifact.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'summary':counts,'artifact':str(args.artifact)}));return 1 if counts['PRODUCT_FAIL'] else 0
if __name__=='__main__':raise SystemExit(main())
