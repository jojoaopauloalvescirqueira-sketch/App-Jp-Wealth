#!/usr/bin/env python3
"""Full audited closure receipts retain voided/migrated facts without summing them."""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap,assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from dashboard_macro_test import launch_browser
from behavior_account_phase_capture_regression_test import SETUP
ROOT=Path(__file__).resolve().parents[1]
PREPARE=r"""kind=>{
 const api=JPWForex.state,scope=__phaseScope('PHASE-A');api.selectOperationalContext(scope.accountId,scope.periodId);
 const corrected=api.recordAccountOrders([{pi:0,oi:0,changes:{costs:-2,costBasis:'SEPARATE_FROM_RESULT'}}],{...scope,reason:'Synthetic signed cost correction'});
 const oi=__phasePeriod('PHASE-A').phases[0].orders.length,add=api.addAccountOrderDraft({...scope,pi:0},{});
 const recorded=api.recordAccountOrders([{pi:0,oi,changes:{id:'AUDIT-'+kind,brokerHash:'SYNTHETIC-'+kind,par:'EURUSD',tipo:'BUY',role:'DEFENSE',lote:.01,entry:1.1,sl:1,tp:1.2,status:'Fechada',result:999,costs:-10,costBasis:'SEPARATE_FROM_RESULT'}}],{...scope,reason:'Synthetic audited fact'});
 const adjusted=kind==='Migrada'?api.recordAccountOrders([{pi:0,oi,changes:{status:'Migrada'}}],{...scope,reason:'Synthetic migration fact'}):operationVoidOrder(0,oi,'Synthetic duplicate identified');
 const allVoided=kind==='all-voided'?operationVoidOrder(0,0,'Synthetic original duplicate identified'):null;
 const ready=operationCanFinalize(),preflight=operationPreflight();JPWOperation.openReview();
 const snapshot=operationBuildSnapshot(operationFinalizeReview.op,{defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
 window.__traceReceipt=structuredClone(snapshot.record);window.__traceOther=JSON.stringify(__phasePeriod('PHASE-B'));
 return {corrected,add,recorded,adjusted,allVoided,ready,preflight,snapshot};
}"""
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*_):pass

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--artifact',type=Path,required=True);a=ap.parse_args();a.artifact.parent.mkdir(parents=True,exist_ok=True)
 server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(a.root)));threading.Thread(target=server.serve_forever,daemon=True).start();rows=[]
 def check(name,passed,facts):
  row={'name':name,'status':'PASS'if passed else'PRODUCT_FAIL','observations':facts};rows.append(row);print(json.dumps({'name':name,'status':row['status']},ensure_ascii=False),flush=True)
 with sync_playwright()as pw:
  browser=launch_browser(pw)
  for kind in ('voided','Migrada','all-voided')+tuple('forgery-'+n for n in ('price','cost','version','reason','drop','net','currency','scope','epoch','revision','open','missing-result')):
   ctx=browser.new_context(service_workers='block');install_bootstrap(ctx);ctx.add_init_script('window.__onbShown=true;');page=ctx.new_page();errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
   try:
    page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page);page.evaluate(SETUP);prepared=page.evaluate(PREPARE,'voided' if kind.startswith('forgery-') else kind)
    assert all(prepared[k]['ok']for k in ('corrected','add','recorded','adjusted'))and prepared['snapshot']['ok'],prepared
    if not kind.startswith('forgery-'):
     expected_net=0 if kind=='all-voided' else 3
     check(kind+' complete review preserves both audited rows and canonical net',prepared['ready']['ok']and prepared['preflight']['estado']=='ready'and len(prepared['snapshot']['record']['ordersSnapshot'])==2 and prepared['snapshot']['record']['netResult']==expected_net,prepared)
     closed=page.evaluate(r"""()=>{
      const r=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'}),record=S.operationHistory.records.at(-1)||null;
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),writes=__phaseWriteCount;
      const duplicate=JPWForex.state.finalizeAccountOperation(__traceReceipt,{...__phaseScope('PHASE-A'),reason:'Synthetic duplicate receipt'});
      return {r,record,disk:JSON.parse(localStorage.getItem(LSKEY)).operationHistory.records.at(-1)||null,exactRows:JSON.stringify(record?.ordersSnapshot)===JSON.stringify(__traceReceipt.ordersSnapshot),otherSame:__traceOther===JSON.stringify(__phasePeriod('PHASE-B')),duplicate,noDuplicateWrite:before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY)&&writes===__phaseWriteCount};
     }""")
     check(kind+' confirmed finalization retains exact full trace without counting excluded result',closed['r']['ok']and closed['exactRows']and closed['record']['netResult']==expected_net and closed['disk']==closed['record']and closed['otherSame'],closed)
     check(kind+' duplicate receipt never writes or appends twice',closed['r']['ok'] and not closed['duplicate']['ok']and closed['noDuplicateWrite'],closed)
     expected=page.evaluate('structuredClone(S.operationHistory.records)');page.reload();wait_bootstrap(page);check(kind+' exact immutable history survives reload',closed['r']['ok'] and page.evaluate('structuredClone(S.operationHistory.records)')==expected,{'history':expected})
    else:
     rejected=page.evaluate(r"""name=>{
      const api=JPWForex.state,scope=__phaseScope('PHASE-A'),receipt=structuredClone(__traceReceipt);
      const changes={price:r=>r.ordersSnapshot[1].entry+=.0001,cost:r=>r.ordersSnapshot[1].costs-=1,version:r=>r.ordersSnapshot[1].recordVersion+=1,reason:r=>r.ordersSnapshot[1].voidReason='Forged reason',drop:r=>r.ordersSnapshot.pop(),net:r=>r.netResult=1002,currency:r=>r.ordersSnapshot[0].currency='BRL',scope:r=>r.accountId='PHASE-B'};
      if(changes[name])changes[name](receipt);
      if(name==='open'){
       const opened=api.recordAccountOrders([{pi:0,oi:0,changes:{status:'Aberta',result:null}}],{...scope,reason:'Synthetic open position guard'});if(!opened.ok)throw Error(JSON.stringify(opened));
      }
      // Imported corruption is an adversarial input, never established by a valid command.
      if(name==='missing-result')__phasePeriod('PHASE-A').phases[0].orders[0].result=null;
      const options={...scope,reason:'Synthetic adversarial '+name,expectedRevision:api.accountContext(scope).revision,expectedEpoch:jpWealthPersistenceEpoch()};
      if(name==='epoch')options.expectedEpoch+='-stale';
      if(name==='revision')options.expectedRevision-=1;
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),writes=__phaseWriteCount;
      const result=api.finalizeAccountOperation(receipt,options);
      return {name,result,same:before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY)&&writes===__phaseWriteCount,writerAttempts:__phaseWriteCount-writes,history:S.operationHistory.records};
     }""",kind.removeprefix('forgery-'))
     check('strict receipt guard '+rejected['name'],not rejected['result']['ok']and rejected['result']['persistido']is False and rejected['same'],rejected)
    assert_fixture_requests(ctx);check(kind+' zero uncaught script errors',not errors,errors)
   finally:ctx.close()
  browser.close()
 server.shutdown();server.server_close();counts={s:sum(r['status']==s for r in rows)for s in ('PASS','PRODUCT_FAIL')};out={'root':str(a.root.resolve()),'sourceHash':hashlib.sha256((a.root/'src/js/10-domain/00-forex-state.js').read_bytes()).hexdigest(),'testHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'summary':counts,'results':rows,'scope':'Real fact/void/migration commands, reviewed canonical finalization, exact history/disk/reload. All contributing net, price/cost/version/reason/scope/epoch/revision/duplicate/open/missing-result guards retained; synthetic data only.'};a.artifact.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'summary':counts,'artifact':str(a.artifact)}));return 1 if counts['PRODUCT_FAIL'] else 0
if __name__=='__main__':raise SystemExit(main())
