#!/usr/bin/env python3
"""Forex journey contract: real DOM, synthetic accounts and existing network fixtures.
The same entry oracles can run against --root baseline; failures remain evidence.
"""
import argparse, hashlib, json, threading, traceback
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from fx_consolidated_storage_test import SEED, Quiet
from notes_launcher_test import launch_options
from dashboard_forex_relocation_test import PREF, IDS, MOVED, KEY, swap

ROOT=Path(__file__).resolve().parents[1]
EXPECTED=["forex-consolidated", "forex-management-accounts", "forex-operation", "forex-history", "forex-accounting", "forex-planning", "forex-reserves"]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--entry-only',action='store_true');args=ap.parse_args()
    result=[];observed={};args.output.parent.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(args.root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    def test(name,fn):
        try:fn();result.append({'name':name,'result':'PASS'})
        except Exception as e:result.append({'name':name,'result':'PRODUCT_FAIL','error':str(e)})
    def require(value,message='Contract assertion failed'):assert value,message
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options())
            ctx=browser.new_context(service_workers='block',viewport={'width':1440,'height':1000})
            ctx.add_init_script('window.__onbShown=true;');ctx.add_init_script('localStorage.setItem('+json.dumps(KEY)+','+json.dumps(json.dumps(PREF,ensure_ascii=False))+');');install_bootstrap(ctx);page=ctx.new_page();page.set_default_timeout(5000)
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page);page.evaluate(SEED)
            page.evaluate('''() => {
              for(const [accountId,currency,si] of [['fx_A','USD',10000],['fx_B','EUR',5000]]){
                const result=JPWForex.state.recordAccountPeriod({accountId,startedAt:'2026-09-01',currency,si,
                  openingBook:si,source:'Fixture sintética de jornada',activateCurrentPeriod:true},
                  {reason:'Fixture sintética de jornada'});
                if(!result.ok)throw Error(result.error);
              }
              JPWForex.state.selectOperationalAccount('fx_B');__fcs.writes=0;
            }''')
            page.evaluate('render();window.__journeyBefore=JSON.stringify(S);window.__journeyRaw=localStorage.getItem(LSKEY);window.__checkNode=document.querySelector("#checkWidgetGrid");window.__overviewNode=document.querySelector("#execOverview");')
            def go(target):require(page.evaluate('(t)=>JPWNavigation.navigate(t)',target));page.wait_for_timeout(60)
            test('seven destinations ordered',lambda:require(page.evaluate("JPWNavigation.children('forex').map(x=>x.id)")==EXPECTED))
            page.locator('#execNavTrigger').click()
            test('Forex default is Consolidado',lambda:require(page.evaluate("JPWNavigation.current().canonical==='forex-consolidated'&&document.querySelector('#fxconsolidated').classList.contains('active')")))
            go('forex-overview')
            test('legacy overview shows context in Consolidado',lambda:require(page.evaluate("JPWNavigation.current().screen==='fxconsolidated'&&document.querySelector('#fxconsolidated #execOverview')===__overviewNode&&!__overviewNode.hidden")))
            if not args.entry_only:
                go('forex-consolidated')
                if page.locator('#fxContextToggle').get_attribute('aria-expanded')=='true':page.locator('#fxContextToggle').click()
                test('labels distinguish analytic and operational accounts',lambda:require(page.locator('label',has=page.locator('#fxcAccount')).inner_text().startswith('Conta em análise') and 'Outra sintética' in page.locator('#fxOperationalSummary').inner_text(),str({'analytic':page.locator('label',has=page.locator('#fxcAccount')).inner_text(),'operational':page.locator('#fxOperationalSummary').inner_text()[:180]})))
                test('analytic Mestre differs from operational B',lambda:require(page.evaluate("document.querySelector('#fxcAccount').value==='fx_A'&&S.forex.activeAccountId==='fx_B'")))
                page.locator('#fxcManual').click();page.locator('#fxcFrom').fill('2026-01-01');page.locator('#fxcTab-history').click()
                page.evaluate('window.__filterNode=document.querySelector("#fxcFrom");window.__layoutBefore=localStorage.getItem(`jpwealth.ui.widgetLayouts.v6`);')
                for _ in range(3):page.locator('#fxContextToggle').click();page.locator('#fxContextToggle').click()
                test('context toggles preserve controls, filters and layout',lambda:require(page.evaluate("document.querySelector('#fxcFrom')===__filterNode&&__filterNode.value==='2026-01-01'&&document.querySelector('#fxcTab-history').getAttribute('aria-selected')==='true'&&localStorage.getItem(`jpwealth.ui.widgetLayouts.v6`)===__layoutBefore")))
                for target in EXPECTED*2:go(target)
                test('navigation leaves state/storage unchanged',lambda:require(page.evaluate('JSON.stringify(S)===__journeyBefore&&localStorage.getItem(LSKEY)===__journeyRaw&&__fcs.writes===0')))
                # A selected file/registration warning is also a live importer state.
                go('forex-consolidated');page.locator('#fxcOpenImport').click()
                page.locator('#fxcFile').set_input_files(str(args.root/'tools/fixtures/mt5-consolidated/classic-en.html'))
                page.locator('#fxcAnalyze').click();page.locator('#fxcRegister').wait_for()
                page.evaluate("window.__importBefore=document.querySelector('#fxcPreview').textContent;window.__importNode=document.querySelector('#fxcFile');")
                page.locator('#fxContextToggle').click();page.locator('#fxContextToggle').click()
                test('context preserves pending file and registration warning without importing',lambda:require(page.evaluate("__importNode===document.querySelector('#fxcFile')&&__importNode.files.length===1&&document.querySelector('#fxcPreview').textContent===__importBefore&&__fcs.writes===0")))
                page.locator('#fxcCancelImport').click()
                go('forex-operation')
                page.evaluate("execSetView('panel');JPWForex.executionBoardUI.render()")
                page.evaluate('document.querySelector("#phaseContainer details[data-phase=\\"0\\"]").open=true')
                # Existing order form remains mounted, even without a populated operation.
                draft=page.locator('#phaseContainer [data-p="0"][data-o="0"][data-f="id"]')
                if draft.count():draft.fill('Synthetic draft')
                page.evaluate('window.__opNodes=[...document.querySelectorAll("#exec input")];window.__opValues=__opNodes.map(e=>e.value);')
                trigger=page.locator('#execChecklistBtn');trigger.focus();page.keyboard.press('Enter');page.locator('#forexChecklistDialog').wait_for(state='visible')
                test('single checklist reused in dedicated modal',lambda:require(page.evaluate("document.querySelectorAll('#checkWidgetGrid').length===1&&document.querySelector('#forexChecklistDialog #checkWidgetGrid')===__checkNode&&!document.querySelector('#forexChecklistDialog #settingsMenu')")))
                page.locator('#forexChecklistDialog #checkContainer button[data-v="2"]').first.click()
                page.evaluate('window.__checkAnswers=JSON.stringify(S.checklist);window.__checkStored=localStorage.getItem(LSKEY);')
                page.keyboard.press('Escape');page.wait_for_timeout(100)
                test('close preserves answers, draft and restores trigger focus',lambda:require(page.evaluate("!document.querySelector('#forexChecklistDialog').open&&document.activeElement.id==='execChecklistBtn'&&JSON.stringify(S.checklist)===__checkAnswers&&localStorage.getItem(LSKEY)===__checkStored&&__opNodes.every((e,i)=>e.isConnected&&e.value===__opValues[i])")))
                for alias in ['check','forex-preparation']*2:
                    go(alias);page.locator('#forexChecklistClose').click();page.wait_for_timeout(50)
                test('legacy checklist opens Operation without duplicate nodes',lambda:require(page.evaluate("JPWNavigation.current().canonical==='forex-operation'&&document.querySelectorAll('#forexChecklistDialog').length===1&&document.querySelectorAll('#checkWidgetGrid').length===1&&JSON.stringify(S.checklist)===__checkAnswers")))
                page.locator('#headerConfigBtn').click();page.locator('#settingsSearch').fill('checklist');page.locator('[data-settings-result]').first.click();page.locator('#forexChecklistDialog').wait_for(state='visible')
                test('Settings suspended for the same checklist',lambda:require(page.evaluate("settingsState.open&&settingsState.suspended&&document.querySelector('#settingsModal').inert&&document.querySelector('#forexChecklistDialog #checkWidgetGrid')===__checkNode")))
                page.locator('#forexChecklistClose').click()
                # Native dialog.close queues its close event; the Settings state
                # and focus are restored in that event and a subsequent frame.
                # Wait for the same contract below, not a fixed scheduling delay.
                page.wait_for_function("settingsState.open&&!settingsState.suspended&&!document.querySelector('#settingsModal').inert&&document.activeElement.id==='settingsOpenChecklist'")
                test('Settings resumes focus and answers',lambda:require(page.evaluate("settingsState.open&&!settingsState.suspended&&!document.querySelector('#settingsModal').inert&&document.activeElement.id==='settingsOpenChecklist'&&JSON.stringify(S.checklist)===__checkAnswers")))
                page.evaluate('closeSettingsModal()')
                page.wait_for_function("!settingsState.open&&!document.querySelector('#settingsOverlay').classList.contains('show')")
                # The inline order draft must remain protected when the new Accounts
                # workspace or Motor is requested. Choosing discard is explicit and
                # lets the later history route remain a distinct accounting view.
                test('operation draft blocks local Accounts',lambda:require(page.evaluate("!JPWNavigation.navigate('contas')&&JPWExec.ui.getView()==='panel'&&document.querySelector('#executionBoardDialog')?.open")))
                page.locator('#ebLeaveStay').click()
                test('operation draft blocks local Motor',lambda:require(page.evaluate("!JPWNavigation.navigateLocal('exec','motor')&&JPWExec.ui.getView()==='panel'&&document.querySelector('#executionBoardDialog')?.open")))
                page.locator('#ebLeaveDiscard').click();page.wait_for_timeout(80)
                test('explicit discard completes requested Motor navigation',lambda:require(page.evaluate("JPWExec.ui.getView()==='motor'&&!document.querySelector('#executionBoardDialog').open")))
                go('history')
                test('operation history has independent workspace',lambda:require(page.evaluate("JPWNavigation.current().screen==='exec'&&JPWExec.ui.getView()==='history'&&document.querySelector('#execHistory').parentElement.id==='exec'&&document.querySelector('#contab').hidden&&document.querySelector('#executionBoard').hidden&&!document.querySelector('#execHistory').hidden")))
                go('forex-reconciliation');test('canonical accounting opens its own workspace',lambda:require(page.evaluate("JPWNavigation.current().screen==='exec'&&JPWExec.ui.getView()==='accounting'&&document.querySelector('#contab').closest('#exec')")))
                # Existing customized v6 preference: moved widgets retain identity/order.
                go('forex-overview')
                expected_order=[i for i in IDS if i in MOVED]
                test('customized v6 projection retained',lambda:require(page.locator('#fxOverviewWidgets > [data-layout-card]').evaluate_all('(els)=>els.map(e=>e.dataset.layoutCard)')==expected_order and page.evaluate('(k)=>localStorage.getItem(k)',KEY)==json.dumps(PREF,ensure_ascii=False)))
                page.locator('#headerConfigBtn').click();page.evaluate("settingsNavigate('interface')");page.locator('#dashLayoutCustomizeBtn').click();page.wait_for_timeout(100)
                swap(page,'vrm','up')
                draft_order=page.locator('#fxOverviewWidgets > [data-layout-card]').evaluate_all('(els)=>els.map(e=>e.dataset.layoutCard)')
                page.locator('#fxContextToggle').click();page.wait_for_timeout(60)
                test('collapsing while editing retains draft and clears hidden controls',lambda:require(draft_order!=expected_order and page.locator('#dashLayoutBar').is_visible() and not page.locator('#fxOverviewWidgets .dash-layout-menu-btn').count()))
                page.locator('#fxContextToggle').click();page.wait_for_timeout(60)
                test('expanding restores editable draft without saving',lambda:require(page.locator('#fxOverviewWidgets > [data-layout-card]').evaluate_all('(els)=>els.map(e=>e.dataset.layoutCard)')==draft_order and page.evaluate('(k)=>localStorage.getItem(k)',KEY)==json.dumps(PREF,ensure_ascii=False)))
                page.locator('#dashLayoutCancelBtn').click();page.wait_for_timeout(60)
                test('layout cancel restores original projection and preference',lambda:require(page.locator('#fxOverviewWidgets > [data-layout-card]').evaluate_all('(els)=>els.map(e=>e.dataset.layoutCard)')==expected_order and page.evaluate('(k)=>localStorage.getItem(k)',KEY)==json.dumps(PREF,ensure_ascii=False)))
                # Editor draft survives the real legacy Dashboard CTA -> native modal.
                # The checklist is not a separately editable widget surface.
                for action in ['cancel','done']:
                    go('forex-overview')
                    page.locator('#headerConfigBtn').click();page.evaluate("settingsNavigate('interface')");page.locator('#dashLayoutCustomizeBtn').click();page.wait_for_timeout(100)
                    swap(page,'vrm','up')
                    editor_order=page.locator('#fxOverviewWidgets > [data-layout-card]').evaluate_all('(els)=>els.map(e=>e.dataset.layoutCard)')
                    go('dashboard');page.locator('[data-dm-route="check"]').click();page.locator('#forexChecklistDialog').wait_for(state='visible')
                    test(f'Editor checklist is non-editable ({action})',lambda:require(page.evaluate("!document.querySelector('#forexChecklistDialog .dash-layout-menu-btn')&&dashLayoutState.editing&&dashLayoutState.activeScreenId!=='check'")))
                    page.locator('#forexChecklistClose').click();go('forex-overview')
                    test(f'Editor draft survives checklist ({action})',lambda:require(editor_order!=expected_order and page.locator('#fxOverviewWidgets > [data-layout-card]').evaluate_all('(els)=>els.map(e=>e.dataset.layoutCard)')==editor_order and page.evaluate('(k)=>localStorage.getItem(k)',KEY)==json.dumps(PREF,ensure_ascii=False)))
                    page.locator('#dashLayoutCancelBtn' if action=='cancel' else '#dashLayoutDoneBtn').click();page.wait_for_timeout(80)
                    test(f'Editor {action} completes after checklist',lambda:require(page.evaluate('!dashLayoutState.editing') and not page.locator('#dashLayoutBar').is_visible() and page.locator('#fxOverviewWidgets > [data-layout-card]').evaluate_all('(els)=>els.map(e=>e.dataset.layoutCard)')==(expected_order if action=='cancel' else editor_order)))
                    saved=json.loads(page.evaluate('(k)=>localStorage.getItem(k)',KEY))
                    test(f'Editor {action} preference contract',lambda:require(saved==PREF if action=='cancel' else saved['screens']['dash']!=PREF['screens']['dash'] and all(saved['screens'][k]==v for k,v in PREF['screens'].items() if k!='dash')))
                # Historical analytic account and absence never redefine operational identity.
                page.evaluate("window.__liveState=structuredClone(S);S.operationHistory.records.push({...S.operationHistory.records[0],operationId:'historical-only',accountId:'fx_H'});JPWFXConsolidated.render()")
                page.locator('#fxcAccount').select_option('fx_H')
                test('historical analytic account remains separate',lambda:require(page.evaluate("S.forex.activeAccountId==='fx_B'&&document.querySelector('#fxcAccount').value==='fx_H'") and 'Outra sintética' in page.locator('#fxOperationalSummary').inner_text()))
                page.evaluate("S.accounts=[];S.forex.activeAccountId='';JPWForex.ui.render();JPWFXConsolidated.render()")
                test('missing operational account explicit',lambda:require('Conta operacional' in page.locator('#fxOperationalSummary').inner_text() and 'Outra sintética' not in page.locator('#fxOperationalSummary').inner_text()))
                page.evaluate('S=__liveState;render()');go('forex-consolidated')
                if page.locator('#fxContextToggle').get_attribute('aria-expanded')=='true':page.locator('#fxContextToggle').click()
                for w,theme in [(1440,'light'),(1440,'dark'),(390,'light'),(390,'dark')]:
                    page.set_viewport_size({'width':w,'height':1000});page.evaluate('(t)=>document.documentElement.dataset.theme=t',theme)
                    test(f'contained {w} {theme}',lambda:require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')))
                    boxes=page.evaluate("['.fxc-workspace','#fxOperationalContext'].map(s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})")
                    test(f'context placement {w} {theme}',lambda:require(boxes[1]['x']>boxes[0]['x'] if w>1000 else boxes[1]['y']<boxes[0]['y']))
                    page.screenshot(path=str(args.output.parent/f'journey-{w}-{theme}.png'),full_page=True)
                    page.locator('#fxContextToggle').click();test(f'expanded contained {w} {theme}',lambda:require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')));page.screenshot(path=str(args.output.parent/f'expanded-{w}-{theme}.png'),full_page=True);page.locator('#fxContextToggle').click()
                    go('check');test(f'checklist contained {w} {theme}',lambda:require(page.locator('#forexChecklistDialog').evaluate('(e)=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight+1}')))
                    test(f'checklist heading and close visible {w} {theme}',lambda:require(page.locator('#forexChecklistTitle').evaluate('(e)=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}') and page.locator('#forexChecklistClose').evaluate('(e)=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')))
                    page.screenshot(path=str(args.output.parent/f'checklist-{w}-{theme}.png'))
                    page.locator('#forexChecklistClose').click();go('forex-consolidated')
                test('no browser errors',lambda:require(not errors,str(errors)))
                test('fixture network only',lambda:assert_fixture_requests(ctx))
                observed['pageerrors']=errors
            browser.close()
    except Exception as e:result.append({'name':'scenario completion','result':'PRODUCT_FAIL','error':str(e),'trace':traceback.format_exc()})
    finally:server.shutdown()
    paths=['index.html','src/js/manifest.json','build-id.js','src/styles/app.css']
    report={'root':str(args.root),'inputs':{s:hashlib.sha256((args.root/s).read_bytes()).hexdigest() for s in paths},'results':result,'observations':observed,'passed':sum(r['result']=='PASS' for r in result),'total':len(result)}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if result and all(x['result']=='PASS' for x in result) else 1
if __name__=='__main__':raise SystemExit(main())
