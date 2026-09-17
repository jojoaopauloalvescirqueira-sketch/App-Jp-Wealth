#!/usr/bin/env python3
"""Synthetic account preparation: separate, acknowledged period/fact writes.

Uses disposable browser contexts and existing fixture writer fault injection.
Never reads a user profile or rewrites application sources.
"""
import argparse, hashlib, json, sys, threading, traceback
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from fx_consolidated_storage_test import SEED, Quiet
from notes_launcher_test import launch_options
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['src/js/20-ui/28-fx-consolidated.js','src/js/40-app/24-fx-consolidated-import.js']
SETUP=r"""() => {
 S.forex=JPWForex.state.empty();S.accounts[0].platformCurrency='USD';save();__fcs.writes=0;
 window.__setupReport=()=>({...__report(),summary:{balance:12345.67,equity:12200.25}});
 window.__setup=()=>JPWFXConsolidated.beginAccountSetup('fx_A',__setupReport());
 window.__period=(draft,extra={})=>JPWFXConsolidated.saveSetupPeriod(draft.token,{startedAt:'2026-01-01',currency:'USD',si:10000,openingBook:null,source:'Synthetic confirmed initial capital',reason:'Synthetic setup',activateCurrentPeriod:true,confirmPeriod:true,...extra});
 window.__observation=(draft,extra={})=>JPWFXConsolidated.saveSetupObservation(draft.token,{equity:12200.25,observedAt:'2026-01-31T12:00:00Z',source:'Synthetic report manually reviewed',reason:'Synthetic observation',netCashflow:0,cashflowAdjustmentRecorded:true,confirmObservation:true,...extra});
}"""
CASES={
 'read-cancel-no-write-no-si-inference':r"""async()=>{
  const before=__snap(),p=__setup();__assert(p.ok&&p.suggestions.balance===12345.67&&p.suggestions.equity===12200.25,'Suggestions absent');
  __assert(!('si' in p.suggestions),'Balance became SI');JPWFXConsolidated.cancelAccountSetup();
  const r=await __period(p);__assert(!r.ok&&__same(before,__snap()),'Cancelled setup wrote');return r;
 }""",
 'confirmed-period-observation-and-backup':r"""async()=>{
  const p=__setup(),a=await __period(p);__assert(a.ok&&a.persistido&&a.period.si===10000&&a.period.openingBook===null,'Period facts corrupted');
  __assert(!S.forex.accounts.fx_A&&a.period.phases.length===6,'Period inferred equity or missing phases');
  const b=await __observation(p);__assert(b.ok&&b.persistido,'Observation failed: '+JSON.stringify(b));
  __assert(S.forex.accounts.fx_A.periodId===a.periodId&&S.forex.accounts.fx_A.equity===12200.25&&S.forex.accounts.fx_A.si===10000,'Observation context differs');
  const count=__fcs.writes,repeated=await __observation(p);__assert(!repeated.ok&&__fcs.writes===count,'Repeated confirmation duplicated');
  const backup=JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-01-31T12:00:00Z').text()),restored=normalizeImportedState(backup);
  __assert(__same(restored.forex,S.forex),'Backup lost setup context');return {a,b,writes:count};
 }""",
 'unknown-si-and-existing-period-pure-selection':r"""async()=>{
  let p=__setup(),a=await __period(p,{si:null});__assert(a.ok&&a.period.si===null,'Unknown SI overwritten');
  let b=await __observation(p);__assert(!b.ok&&!S.forex.accounts.fx_A,'Unknown SI used for observation');
  p=__setup();const before=__snap();a=await __period(p,{periodId:a.periodId});
  __assert(a.ok&&!a.persistido&&__same(before,__snap()),'Period selection wrote or duplicated');return {a,b};
 }""",
 'identity-mismatch-other-account-unmodified':r"""async()=>{
  const before=__snap(),p=JPWFXConsolidated.beginAccountSetup('fx_B',__setupReport());
  __assert(!p.ok&&__same(before,__snap()),'Report connected to unrelated account');
  const a=await __period(__setup());__assert(a.ok&&!S.forex.accountContexts.accounts.fx_B,'Other account affected');return p;
 }""",
 'quota-noop-and-partial-step-recovery':r"""async()=>{
  const p=__setup(),before=__snap();__fcs.mode='quota';let r=await __period(p);
  __assert(!r.ok&&r.persistido===false&&__same(before.forex,S.forex)&&before.raw===__snap().raw,'Quota changed state');
  __fcs.mode='noop';r=await __period(p);__assert(!r.ok&&r.persistido===false&&__same(before.forex,S.forex),'Silent refusal announced success');
  __fcs.mode='normal';const period=await __period(p);__assert(period.ok,'Period retry failed');
  const confirmed=__snap();__fcs.mode='quota';r=await __observation(p);
  __assert(!r.ok&&__same(confirmed.forex,S.forex)&&confirmed.raw===__snap().raw,'Failed observation erased confirmed period');
  __fcs.mode='normal';r=await __observation(p);__assert(r.ok&&Object.keys(S.forex.accountContexts.accounts.fx_A.periods).length===1,'Observation retry duplicated period');return r;
 }""",
 'queued-cancel-and-stale-context':r"""async()=>{
  const p=__setup(),lock=sessionAcquireWriteLock;let execute;sessionAcquireWriteLock=fn=>new Promise(resolve=>execute=()=>resolve(fn()));
  const promise=__period(p);JPWFXConsolidated.cancelAccountSetup();execute();let r=await promise;sessionAcquireWriteLock=lock;
  __assert(!r.ok&&__fcs.writes===0,'Queued cancellation wrote');
  const q=__setup();S.forex.auditLog.push({fixture:'concurrent'});const before=__snap();r=await __period(q);
  __assert(!r.ok&&__same(before,__snap()),'Changed Forex state accepted');return r;
 }""",
 'epoch-and-observation-dates':r"""async()=>{
  const p=__setup();sessionEpochRotate();let r=await __period(p);__assert(!r.ok&&__fcs.writes===0,'Old epoch wrote');
  const q=__setup(),a=await __period(q);__assert(a.ok,'Fresh setup failed');const before=__snap();
  for(const observedAt of ['2025-12-31T12:00:00Z','2999-01-01T00:00:00Z']){r=await __observation(q,{observedAt});__assert(!r.ok&&__same(before,__snap()),'Invalid observation date wrote');}
  return r;
 }""",
 'unknown-write-no-retry':r"""async()=>{
  const p=__setup();save=()=>{__fcs.realSave();throw Error('Synthetic interruption after write');};
  const first=await __period(p),writes=__fcs.writes,second=await __period(p);
  __assert(first.persistido===null&&second.persistido===null&&__fcs.writes===writes,'Unknown outcome blindly retried');return {first,second};
 }"""
}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--case',default='');args=ap.parse_args()
 if args.out.exists():ap.error('Choose a new evidence path')
 root=args.root.resolve();hashes=lambda:{s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in SOURCES}
 report={'root':str(root),'before':hashes(),'cases':[]}
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
 def run(browser,name,source=None,callback=None):
  if args.case and args.case not in name:return
  record={'name':name,'pageerrors':[]};context=None
  try:
   context=browser.new_context(service_workers='block',viewport={'width':1440,'height':1000});install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
   page=context.new_page();page.on('pageerror',lambda e:record['pageerrors'].append(str(e)));page.goto(url);wait_bootstrap(page);page.evaluate(SEED);page.evaluate(SETUP)
   record['observations']=page.evaluate(source) if source else callback(page,context)
   assert_fixture_requests(context);assert not record['pageerrors'],record['pageerrors'];record['status']='PASS'
  except Exception as e:record.update(status='PRODUCT_FAIL' if isinstance(e,AssertionError) or 'PRODUCT_ASSERTION:' in str(e) else 'TEST_HARNESS_FAIL',error=str(e),trace=traceback.format_exc())
  finally:
   if context:context.close()
   report['cases'].append(record);print(name,record['status'],record.get('error','')[:200],flush=True)
 def ui(page,context):
  page.evaluate("JPWFXConsolidatedUI.openAccountSetup({accountId:'fx_A',report:__setupReport()})")
  assert page.locator('#fxcs-si').input_value()=='' and page.locator('#fxcs-book').input_value()==''
  before=page.evaluate('__snap()');page.keyboard.press('Escape');assert page.evaluate('__snap()')==before
  page.evaluate("JPWFXConsolidatedUI.openAccountSetup({accountId:'fx_A',report:__setupReport()})")
  for width in [390,768,1440]:
   page.set_viewport_size({'width':width,'height':844})
   assert page.locator('#fxcSetupDialog').evaluate('el=>el.scrollWidth<=el.clientWidth+2&&el.getBoundingClientRect().left>=0')
  page.locator('#fxcs-start').fill('2026-01-01');page.locator('#fxcs-si').fill('10000');page.locator('#fxcs-confirm-period').check();page.locator('#fxcs-save-period').click()
  page.locator('#fxcSetupObservationForm').wait_for(state='visible');assert page.locator('#fxcs-equity').input_value()=='12200.25'
  assert page.locator('#fxcs-observed').input_value()==''
  page.locator('#fxcs-observed').fill('2026-01-31T12:00');page.locator('#fxcs-confirm-observation').check();page.locator('#fxcs-save-observation').click()
  page.wait_for_function("document.getElementById('fxcSetupStatus').textContent.startsWith('Observação financeira salva')")
  page.locator('#fxcs-open-orders').click();assert not page.locator('#fxcSetupDialog').is_visible();assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='fx_A'
  page.reload();wait_bootstrap(page);assert page.evaluate('S.forex.accounts.fx_A.equity===12200.25&&Object.values(S.forex.accountContexts.accounts.fx_A.periods)[0].phases.length===6')
  return {'initialCapitalIndependent':True,'mobile':True,'reload':True,'phases':6}
 def manual(page,context):
  page.evaluate('JPWFXConsolidatedUI.openAccountSetup()');page.locator('#fxcr-name').fill('Conta fictícia nova');page.locator('#fxcr-platform').select_option('MetaTrader 5');page.locator('#fxcr-login').fill('40004');page.locator('#fxcr-currency').fill('USD');page.locator('#fxcRegistrationSave').click()
  page.locator('#fxcSetupDialog').wait_for(state='visible');assert page.evaluate('S.accounts.length===4&&S.fxConsolidated.receipts.length===0')
  page.keyboard.press('Escape');assert page.evaluate('S.accounts.length===4&&Object.keys(S.forex.accountContexts?.accounts||{}).length===0')
  return {'registrationPreserved':True,'periodNotCreatedOnCancel':True}
 def import_ui(page,context):
  source='<!doctype html><html lang="pt"><title>MetaTrader 5 Account History Report</title><table><tr><td>Account:</td><td>10001</td></tr><tr><td>Company:</td><td>Synthetic Broker</td></tr><tr><td>Currency:</td><td>USD</td></tr><tr><th>Deals</th></tr><tr><th>Time</th><th>Deal</th><th>Symbol</th><th>Type</th><th>Direction</th><th>Volume</th><th>Price</th><th>Order</th><th>Commission</th><th>Fee</th><th>Swap</th><th>Profit</th></tr><tr><td>2026.01.01 12:00:00</td><td>100</td><td>EURUSD</td><td>buy</td><td>in</td><td>1</td><td>1</td><td>200</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><th>Summary</th></tr><tr><td>Balance:</td><td>1.234</td></tr><tr><td>Equity:</td><td>1.234</td></tr></table></html>'
  page.evaluate("JPWFXConsolidatedUI.openImport({accountId:'fx_A'})")
  page.locator('#fxcFile').set_input_files({'name':'synthetic-ambiguous.html','mimeType':'text/html','buffer':source.encode()})
  page.locator('#fxcAnalyze').click();page.wait_for_function("document.getElementById('fxcPreview').textContent.includes('separador decimal')")
  assert page.locator('#fxcConfirmImport').count()==0 and page.evaluate('S.fxConsolidated.receipts.length===0')
  page.locator('#fxcNumberFormat').select_option('decimal-dot');page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
  assert '1.234' in page.locator('#fxcPreview').inner_text()
  for control,value in [('#fxcDateOrder','dmy'),('#fxcNumberFormat','decimal-comma')]:
   page.locator(control).select_option(value)
   assert page.locator('#fxcConfirmImport').count()==0
   page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
  page.locator('#fxcNumberFormat').select_option('decimal-dot');page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
  page.locator('#fxcImportTo').fill('2026-01-31');page.locator('#fxcImportTo').dispatch_event('change');assert page.locator('#fxcConfirmImport').count()==0
  page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
  page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click();page.locator('#fxcPrepareAccount').wait_for()
  assert page.evaluate('S.fxConsolidated.receipts.length===1&&!S.forex.accounts.fx_A&&Object.keys(S.forex.accountContexts?.accounts||{}).length===0')
  before=page.evaluate('__snap()');page.locator('#fxcPrepareAccount').click();page.locator('#fxcSetupDialog').wait_for(state='visible')
  assert page.locator('#fxcs-si').input_value()=='' and page.locator('#fxcs-book').input_value()==''
  page.keyboard.press('Escape');assert page.evaluate('__snap()')==before
  page.locator('#fxcOpenImport').click();page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for();page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click();page.locator('#fxcPrepareAccount').wait_for()
  assert page.evaluate('S.fxConsolidated.receipts.length===1')
  return {'formatReview':True,'separatePreparation':True,'duplicateIdempotent':True}
 def cross_tab(page,context):
  page.evaluate('window.__pendingSetup=__setup()');other=context.new_page();other.goto(url);wait_bootstrap(other)
  raw=other.evaluate("()=>{S.accounts[0].nome='Synthetic second tab';if(save()!==true)throw Error('Fixture failed');return localStorage.getItem(LSKEY)}")
  result=page.evaluate('__period(__pendingSetup)');assert not result['ok'];assert page.evaluate('localStorage.getItem(LSKEY)')==raw
  return result
 def reset_draft(page,context):
  page.evaluate("JPWFXConsolidatedUI.openAccountSetup({accountId:'fx_A'})")
  before=page.evaluate('__snap()');page.evaluate('JPWFXConsolidated.reset()')
  assert not page.locator('#fxcSetupDialog').is_visible() and page.evaluate('__snap()')==before
  return {'closedOnSessionReset':True,'noWrite':True}
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(**launch_options())
   for name,source in CASES.items():run(browser,name,source=source)
   run(browser,'ui-reviewed-period-observation-responsive-reload',callback=ui);run(browser,'ui-manual-registration-separate-period',callback=manual);run(browser,'ui-format-review-import-prepare-duplicate',callback=import_ui);run(browser,'cross-tab-preparation-refused',callback=cross_tab);run(browser,'ui-session-reset-closes-setup-draft',callback=reset_draft);browser.close()
 finally:
  server.shutdown();server.server_close();report['after']=hashes();report['sourcesUnchanged']=report['before']==report['after'];report['result']='PASS' if report['cases'] and all(r['status']=='PASS' for r in report['cases']) and report['sourcesUnchanged'] else 'PRODUCT_FAIL'
  args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report['result'])
 return 0 if report['result']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
