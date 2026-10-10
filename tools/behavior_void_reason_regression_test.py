#!/usr/bin/env python3
"""Explicit void reasons survive confirmation, quota refusal and real UNKNOWN.

Real local document writer and disposable synthetic account periods. UNKNOWN is
an injected one-shot read-back fault after an actual localStorage write. No save
or command replacement, authorization relaxation, or financial arithmetic fork.
"""
import argparse
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
import time
import traceback
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_execution_table_test import SEED, Server, Quiet, ready
from notes_launcher_test import launch_options
ROOT=Path(__file__).resolve().parents[1]
REASON='Duplicidade sintética identificada — manter trilha factual'
SOURCES=['src/js/10-domain/11-operation-lifecycle.js','src/js/10-domain/00-forex-state.js','src/js/00-core/04-persistence.js','build-id.js']
def hashes(root):return {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCES}
def setup(page):
    page.evaluate(SEED)
    page.evaluate("""() => {
      window.alert=()=>{};window.confirm=()=>true;
      window.__yes=r=>{if(!r?.ok)throw Error(JSON.stringify(r));return r;};
      window.__scope=JPWForex.state.operationalSelection();
      window.__p=()=>S.forex.accountContexts.accounts[__scope.accountId].periods[__scope.periodId];
      __yes(operationAddDraft(0));__yes(operationAddDraft(0));
      __yes(operationRecordOrder(0,0,{id:'VOID-SYNTHETIC',brokerHash:'SYNTHETIC-VOID-9007199254740993',par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:1,entry:1.1,sl:1.09,tp:1.2,costs:0,costBasis:'SEPARATE_FROM_RESULT',stopValidated:true,status:'Fechada',result:100},{reason:'Synthetic recorded fact'}));
      window.__voidWrites=0;const set=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===LSKEY)__voidWrites++;return set.call(this,k,v);};
    }""")
def snapshot(page):return page.evaluate("({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),writes:__voidWrites})")
def void(page):return page.evaluate('reason=>operationVoidOrder(0,0,reason)',REASON)
def confirmed_reason(page):
    r=page.evaluate("""() => {const o=__p().phases[0].orders[0],saved=JSON.parse(localStorage.getItem(LSKEY)).forex.accountContexts.accounts[__scope.accountId].periods[__scope.periodId].phases[0].orders[0];return {o,saved}}""")
    assert r['o']==r['saved'],r
    assert r['o']['recordStatus']=='voided' and r['o']['recordVersion']==2,r
    assert r['o']['voidReason']==REASON and r['o']['revisions'][1]['reason']==REASON,{'memoryReason':r['o']['voidReason'],'revisionReason':r['o']['revisions'][1]['reason'],'savedReason':r['saved']['voidReason']}
    assert r['o']['revisions'][1]['before']['recordStatus']=='recorded',r
    return {'reason':r['o']['voidReason'],'version':2}
def confirmed(page):
    r=void(page);assert r['ok'] and r['persistido'] is True,r
    return confirmed_reason(page)
def quota(page):
    before=snapshot(page)
    fill=page.evaluate("""() => {let low=0,high=6*1024*1024,error;while(high-low>1){const n=Math.floor((low+high)/2);try{localStorage.setItem('__synthetic_void_quota__','q'.repeat(n));low=n;}catch(e){high=n;error=e.name}}return {error,characters:low}}""")
    refused=void(page);after=snapshot(page)
    assert fill['error']=='QuotaExceededError' and not refused['ok'] and refused['persistido'] is False,(fill,refused)
    assert before['state']==after['state'] and before['raw']==after['raw'],(before,after)
    page.evaluate("localStorage.removeItem('__synthetic_void_quota__')")
    retry=void(page);assert retry['ok'] and retry['persistido'] is True,retry
    return {'quota':fill,'refused':refused,'confirmed':confirmed_reason(page)}
def unknown(page):
    page.evaluate("""() => {window.__actualGet=Storage.prototype.getItem;window.__faultAfterWrite=false;const set=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){const r=set.call(this,k,v);if(this===localStorage&&k===LSKEY)__faultAfterWrite=true;return r;};
      Storage.prototype.getItem=function(k){if(this===localStorage&&k===LSKEY&&__faultAfterWrite){__faultAfterWrite=false;throw Error('Synthetic one-shot void readback unavailable')}return __actualGet.call(this,k);};
    }""")
    result=void(page);assert not result['ok'] and result['persistido'] is None,result
    assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()')
    reason=confirmed_reason(page)
    before=snapshot(page);repeat=void(page);after=snapshot(page)
    assert not repeat['ok'] and repeat['persistido'] is None and before==after,(repeat,before,after)
    return {'unknown':result,'repeatBlocked':True,'actualDiskCandidate':reason}
def history(page):
    r=void(page);assert r['ok'],r
    confirmed_reason(page)
    before=page.evaluate('JSON.stringify(S)')
    preview=page.evaluate("""() => operationBuildSnapshot(__p().activeOperation,{defenseCount:0,openedAtManual:'2026-09-01T00:00:00Z'})""")
    assert before==page.evaluate('JSON.stringify(S)') and preview['ok'],preview
    assert preview['record']['ordersSnapshot'][0]['voidReason']==REASON,preview
    page.evaluate("""() => {
      __yes(operationRecordOrder(0,1,{id:'CLOSED-SYNTHETIC',brokerHash:'SYNTHETIC-CLOSED-9007199254740993',par:'EURUSD',tipo:'BUY',role:'OTHER',lote:1,entry:1.1,sl:1.09,tp:1.2,costs:0,costBasis:'SEPARATE_FROM_RESULT',stopValidated:true,status:'Fechada',result:10},{reason:'Synthetic second closure'}));
      openFinalizeOperationModal();
    }""")
    r=page.evaluate('finalizeOperation({defenseCount:0,openedAtManual:"2026-09-01T00:00:00Z"})');assert r['ok'],r
    h=page.evaluate('JSON.parse(localStorage.getItem(LSKEY)).operationHistory.records[0]')
    assert h['netResult']==10 and len(h['ordersSnapshot'])==2,h
    assert h['ordersSnapshot'][0]['recordStatus']=='voided' and h['ordersSnapshot'][0]['voidReason']==REASON and h['ordersSnapshot'][0]['revisions'][1]['reason']==REASON,h
    return {'historyNet':10,'voidedFactualReason':REASON,'confirmedSnapshotRows':2}
CASES=[confirmed,quota,unknown,history]
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);p.add_argument('--case');a=p.parse_args();root=a.root.resolve();start=time.monotonic();report={'inputs_before':hashes(root),'cases':[]}
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch_options())
        for test in CASES:
          if a.case and a.case!=test.__name__:continue
          context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',reduced_motion='reduce');install_bootstrap(context);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));row={'name':test.__name__}
          try:
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html');ready(page);setup(page);row['build']=page.evaluate('JP_WEALTH_BUILD_ID');row['evidence']=test(page);assert not errors,errors;assert_fixture_requests(context);row['result']='PASS'
          except Exception as e:row.update(result='PRODUCT_FAIL' if isinstance(e,AssertionError) else 'TEST_HARNESS_FAIL',detail=str(e),traceback=traceback.format_exc())
          finally:context.close();report['cases'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        browser.close()
    finally:
      server.shutdown();server.server_close();report['inputs_after']=hashes(root);report['source_unchanged']=report['inputs_before']==report['inputs_after'];report['durationSeconds']=time.monotonic()-start;a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report['source_unchanged'] and all(r['result']=='PASS' for r in report['cases']) else 1
if __name__=='__main__':raise SystemExit(main())
