#!/usr/bin/env python3
"""Approved Hedge redesign: synthetic UI/persistence journeys, real browser."""
import argparse,hashlib,json,threading,traceback
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from hedge_prop_browser_test import boot,route,field,action,mode,values,ONE,TWO,Quiet,launch_options
ROOT=Path(__file__).resolve().parents[1]
def run(args):
 args.out.mkdir(parents=True,exist_ok=True)
 report={'classification':'PRODUCT_FAIL','checks':[]}
 def record(name): report['checks'].append(name)
 with BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server,sync_playwright() as pw:
  threading.Thread(target=server.serve_forever,daemon=True).start()
  browser=pw.chromium.launch(**launch_options())
  context,page,errors=boot(browser,f'http://127.0.0.1:{server.server_port}/index.html')
  try:
   route(page)
   assert page.locator('[data-hedge-mode="instant"]').count()==1,'HEDGE-INSTANT-MODE: Instant must be selectable'
   assert page.locator('#hedgePropRoot input[type="range"]').count()>=7,'HEDGE-SLIDERS: linked numeric controls required'
   assert page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')") is None
   action(page,'example').click();values(page,ONE)
   record('one-phase-oracle-preserved')
   field(page,'feeUSD').fill('0');field(page,'refundUSD').fill('0')
   assert '−US$ 0,00' not in page.locator('#hedgePropFlow').inner_text(),'Zero accumulated expense must not advertise negative zero'
   action(page,'example').click()
   record('zero-fee-flow-does-not-advertise-negative-zero')
   slider=page.locator('[data-hedge-range="feeUSD"]');slider.focus();slider.press('ArrowRight')
   assert field(page,'feeUSD').input_value()=='1201','Keyboard slider must synchronize numeric field'
   fee=field(page,'feeUSD');fee.fill('1200,123456');fee.focus();handle=fee.element_handle();fee.evaluate('e=>e.setSelectionRange(5,5)');fee.press('0')
   assert handle.evaluate('e=>e===document.activeElement'),'Field replaced while typing'
   assert fee.input_value()=='1200,0123456','Numeric precision changed'
   assert slider.input_value()=='1200.0123456','Slider precision changed'
   assert page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')") is None,'Typing must not save'
   record('range-keyboard-numeric-precision-focus-no-write')
   action(page,'example').click()
   assert page.locator('.hp-diagram [data-hedge-stage]').count()==2
   assert page.locator('.hp-flow-outcome').count()>=4
   action(page,'save-plan').click()
   page.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('Plano confirmado e guardado')")
   saved=page.evaluate("JSON.parse(localStorage.getItem('jpwealth_hedge_guide_v1'))")
   assert saved['stage']=='planned' and saved['plan']['input']['feeUSD']==1200
   page.locator('#hedgePropGuideStage').select_option('phase1');action(page,'confirm-stage').click()
   page.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('Etapa confirmada')")
   saved=page.evaluate("JSON.parse(localStorage.getItem('jpwealth_hedge_guide_v1'))")
   assert saved['stage']=='phase1' and len(saved['milestones'])==2
   assert saved['milestones'][0]['stage']=='planned'
   record('explicit-plan-confirm-progress-history')
   page.reload();page.wait_for_function('window.JPWNavigation');route(page)
   assert 'Avaliação 1 em andamento' in page.locator('#hedgePropGuideCurrent').inner_text()
   assert field(page,'feeUSD').input_value()=='','Saved plan must not auto-apply RAM fields'
   action(page,'load-plan').click();values(page,ONE)
   record('reload-preserves-guide-explicit-resume')
   other=context.new_page();other.goto(page.url);other.wait_for_function('window.JPWNavigation');route(other)
   other.locator('#hedgePropGuideStage').select_option('funded');action(other,'confirm-stage').click()
   other.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('Etapa confirmada')")
   page.locator('#hedgePropGuideStage').select_option('payout-requested');action(page,'confirm-stage').click()
   page.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('Outra aba')")
   assert 'Outra aba' in page.locator('#hedgePropGuideStatus').inner_text()
   assert page.evaluate("JSON.parse(localStorage.getItem('jpwealth_hedge_guide_v1')).stage")=='funded'
   assert field(page,'feeUSD').input_value()=='1200'
   action(page,'verify-guide').click();other.close()
   record('two-tabs-stale-write-refused-preserves-draft')
   competitor=context.new_page();competitor.goto(page.url);competitor.wait_for_function('window.JPWNavigation');route(competitor)
   gate=context.new_page();gate.goto(page.url);gate.wait_for_function('window.JPWNavigation')
   gate.evaluate('''()=>{window.__lockHeld=false;window.__releaseLock=null;navigator.locks.request('jpwealth_state_writer_v1',()=>new Promise(resolve=>{window.__releaseLock=resolve;window.__lockHeld=true}));return true}''')
   gate.wait_for_function('window.__lockHeld===true')
   before_race=page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')")
   page.locator('#hedgePropGuideStage').select_option('phase1');action(page,'confirm-stage').click()
   assert page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')")==before_race,'Guide writer bypassed the shared state/import Web Lock'
   competitor.locator('#hedgePropGuideStage').select_option('payout-requested');action(competitor,'confirm-stage').click()
   gate.wait_for_function("async()=>{const q=await navigator.locks.query();return q.pending.filter(l=>l.name==='jpwealth_state_writer_v1').length===2}")
   assert action(page,'confirm-stage').is_disabled(),'In-flight confirmation must expose busy state'
   gate.evaluate('()=>{window.__releaseLock();return true}')
   page.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('Etapa confirmada')")
   competitor.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('Outra aba')")
   after_race=page.evaluate("JSON.parse(localStorage.getItem('jpwealth_hedge_guide_v1'))")
   before_doc=json.loads(before_race)
   assert after_race['revision']==before_doc['revision']+1
   assert after_race['milestones'][:-1]==before_doc['milestones'] and after_race['stage']=='phase1'
   assert after_race['milestones'][-1]['stage']=='phase1'
   record('shared-import-lock-serializes-two-tabs-no-lost-confirmed-milestone')
   gate.evaluate('''()=>{window.__lockHeld=false;navigator.locks.request('jpwealth_state_writer_v1',()=>new Promise(resolve=>{window.__releaseLock=resolve;window.__lockHeld=true}));return true}''')
   gate.wait_for_function('window.__lockHeld===true')
   before_cancel=page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')")
   page.locator('#hedgePropGuideStage').select_option('funded');action(page,'confirm-stage').click()
   gate.wait_for_function("async()=>{const q=await navigator.locks.query();return q.pending.filter(l=>l.name==='jpwealth_state_writer_v1').length===1}")
   page.evaluate('JPWPropFirms.disposeForSession()')
   gate.evaluate('()=>{window.__releaseLock();return true}')
   gate.wait_for_function("async()=>{const q=await navigator.locks.query();return !q.pending.some(l=>l.name==='jpwealth_state_writer_v1')&&!q.held.some(l=>l.name==='jpwealth_state_writer_v1')}")
   assert page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')")==before_cancel
   assert page.evaluate("JPWNavigation.navigate('dashboard')");route(page);action(page,'load-plan').click()
   gate.close();competitor.close()
   record('disposed-owner-cancels-queued-write-before-storage')
   page.screenshot(path=str(args.out/'one-phase-desktop.png'),full_page=True)
   mode(page,2);action(page,'example').click();values(page,TWO)
   assert page.locator('.hp-diagram [data-hedge-stage]').count()==3
   record('two-phase-oracle-and-flow')
   page.screenshot(path=str(args.out/'two-phase-desktop.png'),full_page=True)
   mode(page,'instant')
   assert page.locator('#hedgePropInstant').is_visible()
   assert not page.locator('#hedgePropCostFields').is_visible()
   assert not field(page,'drawdownPercent').is_visible()
   assert 'sem avaliação' in page.locator('#hedgePropInstant').inner_text().lower()
   assert page.locator('[data-hedge-value="hedgeCapitalUSD"]').inner_text()=='Não se aplica'
   record('instant-no-evaluation-hedge-bypass')
   page.locator('#hedgePropCatalog').select_option('ftmo-instant')
   page.locator('#hedgePropCatalogReading summary').click()
   assert '30%' in page.locator('#hedgePropCatalogReading').inner_text()
   assert 'não' in page.locator('#hedgePropCompliance').inner_text().lower()
   assert page.locator('#hedgePropSources').locator('a[href*="ftmo.com"]').count()>0
   assert saved['plan']['catalogId']=='custom'
   record('factual-catalog-not-auto-applied')
   field(page,'nominalUSD').fill('50000');field(page,'feeUSD').fill('169')
   page.once('dialog',lambda dialog:dialog.accept());action(page,'save-plan').click()
   page.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('Plano confirmado e guardado')")
   replacement=page.evaluate("JSON.parse(localStorage.getItem('jpwealth_hedge_guide_v1'))")
   assert replacement['plan']['mode']=='instant' and len(replacement['milestones'])==1
   assert replacement['plan']['input']=={'nominalUSD':50000,'feeUSD':169}
   record('explicit-replace-different-mode-after-confirmation')
   for width,height in [(1440,1000),(960,900),(390,844),(320,740)]:
    page.set_viewport_size({'width':width,'height':height})
    for theme in ['light','dark']:
     page.evaluate('(theme)=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}',theme)
     assert page.locator('#hedgePropRoot').evaluate('e=>e.scrollWidth<=e.clientWidth+2'),('overflow',width,theme)
     page.screenshot(path=str(args.out/f'instant-{width}-{theme}.png'),full_page=True)
   record('mobile-desktop-themes-no-root-overflow')
   page.add_init_script("Object.defineProperty(navigator,'locks',{configurable:true,value:undefined})")
   page.reload();page.wait_for_function('window.JPWNavigation');route(page)
   mode(page,1);action(page,'example').click()
   no_lock_raw=page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')")
   page.once('dialog',lambda dialog:dialog.accept());action(page,'save-plan').click()
   page.wait_for_function("document.querySelector('#hedgePropGuideStatus').textContent.includes('inicializador local')")
   assert page.evaluate("localStorage.getItem('jpwealth_hedge_guide_v1')")==no_lock_raw
   assert field(page,'feeUSD').input_value()=='1200'
   record('no-safe-lock-refuses-write-and-keeps-prior-and-draft')
   assert not errors,errors
   report['classification']='PASS'
  except Exception as error: report['failure']=str(error);report['traceback']=traceback.format_exc();page.screenshot(path=str(args.out/'failure.png'),full_page=True)
  finally: context.close();browser.close()
 (args.out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False));return 0 if report['classification']=='PASS' else 1
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);raise SystemExit(run(parser.parse_args()))
