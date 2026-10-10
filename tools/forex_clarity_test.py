#!/usr/bin/env python3
"""Forex task/identity/draft contracts with reusable two-account synthetic fixture.
No operator profile, real export, financial rule or saved preference is touched.
"""
import argparse
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_execution_table_test import SEED as TABLE_SEED, Server, Quiet, ready, settle, set_field, field, persisted, projection, order, prepare_drafts
from notes_launcher_test import launch_options

ROOT = Path(__file__).resolve().parents[1]
# Reusable by baseline/candidate captures: only pre-existing domain commands.
SEED = TABLE_SEED.replace('  return scope;', '''  S.accounts.push({forexAccountId:'TABLE-B',nome:'Conta B sintética',tipo:'PRÓPRIA',platformCurrency:'USD',platform:'MT5',platformLogin:'TEST-002'});
  if(save()!==true)throw Error('Synthetic second account refused');
  require(api.recordAccountPeriod({accountId:'TABLE-B',startedAt:'2026-08-01',currency:'USD',si:5000,openingBook:5000,source:'Synthetic second opening',activateCurrentPeriod:true},{reason:'Synthetic second account'}));
  require(api.selectOperationalContext(scope.accountId,scope.periodId));render();
  return scope;''')
OWNED = ['src/js/20-ui/'+name+'.js' for name in ('01-header-readout','13-exec-views','16-operation-history','26-forex-engine-views','28-fx-consolidated','30-execution-board','31-forex-accounts')]+['src/js/30-accounting/05-fx-planning/05-fx-ui.js']

def seed(page):
    scope=page.evaluate(SEED);settle(page);prepare_drafts(page);return scope

def populate_example_order(page, broker_hash=None):
    """Reusable baseline/candidate UI commands; saves only when caller clicks Save."""
    page.evaluate("JPWNavigation.navigate('forex-operation')");settle(page)
    values=dict(id='CLARITY-001',par='EURUSD',tipo='BUY',role='GENESIS',lote='0.2',entry='1.2',sl='1.17',tp='1.26',status='Aberta',costs='0',costBasis='SEPARATE_FROM_RESULT',stopValidated=True)
    if broker_hash is not None:values['brokerHash']=broker_hash
    for key,value in values.items():set_field(page,key,value)

def save_example_order(page):
    populate_example_order(page,'0009007199254740993123456789-ABC')
    page.locator('[data-eb-save-row="0:0"]').click();settle(page)
    return order(page)

def assert_control_targets(page,scope):
    controls=page.locator(scope).evaluate(r'''root=>[...root.querySelectorAll('button,input,select,textarea,summary')].filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden'&&!e.closest('[hidden],[inert]')).map(e=>{
      const box=e.matches('input[type=checkbox],input[type=radio]'),target=box?e.closest('label'):e,r=target?.getBoundingClientRect(),c=e.getBoundingClientRect();
      return {id:e.id||e.dataset.f||e.textContent.trim().slice(0,60),compact:!!e.closest('#ebOrderTable,#phaseContainer .eb-order-table'),checkbox:box,height:r?.height||0,width:r?.width||0,boxHeight:c.height,font:parseFloat(getComputedStyle(e).fontSize)};
    })''')
    assert controls,scope
    for control in controls:
        minimum=36 if control['compact'] and page.locator('#ebOrderScroll').evaluate('e=>e.clientWidth>=768') else 44
        assert control['height']>=minimum and control['width']>=minimum,(scope,control)
        if control['checkbox']:assert control['boxHeight']<=24,(scope,control)
    return controls

def run(page,out,results):
    scope=seed(page)
    results.append('Synthetic layout setup: six explicit drafts via Add; anonymous zero slots removed only in disposable fixture; financial values unchanged')
    before=persisted(page)
    for route in ['forex-consolidated','forex-management-accounts','forex-operation','forex-history','forex-accounting','forex-planning','forex-reserves']:
        assert page.evaluate('(r)=>JPWNavigation.navigate(r)',route)
        settle(page)
        assert page.locator('#hdrPeriod').inner_text()=='01/09/2026',(route,page.locator('#hdrPeriod').inner_text())
        assert persisted(page)==before,('Read-only navigation changed state',route)
        assert_control_targets(page,'.screen.active')
    results.append('PASS: same operational period on seven Forex routes; navigation preserves confirmed state and storage')
    page.evaluate("JPWNavigation.navigate('forex-management-accounts')")
    assert page.evaluate("JPWForex.accountsUI.examine('TABLE-B')")
    assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='TABLE-A'
    assert page.evaluate('JPWForex.accountsUI.examination().accountId')=='TABLE-B'
    assert page.locator('#accountPeriodSelect').evaluate("e=>!!(e.compareDocumentPosition(document.getElementById('fxAccountsUse'))&Node.DOCUMENT_POSITION_FOLLOWING)")
    assert '2026-08-01' in page.locator('#fxAccountsUseHelp').inner_text()
    assert persisted(page)==before
    page.locator('#fxAccountsUse').click();settle(page)
    assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='TABLE-B'
    assert page.locator('#hdrPeriod').inner_text()=='01/08/2026'
    # Restore A by the existing explicit UI command, no fixture-only selector.
    page.evaluate("JPWNavigation.navigate('forex-management-accounts');JPWForex.accountsUI.examine('TABLE-A')")
    page.locator('#fxAccountsUse').click();settle(page)
    assert page.evaluate('JPWForex.state.operationalSelection().periodId')==scope['periodId']
    results.append('PASS: consult B preserves A; period precedes apply; explicit apply switches both identity and period')
    before=persisted(page)
    populate_example_order(page)
    assert persisted(page)==before
    page.locator('[data-eb-save-row="0:0"]').click();settle(page)
    assert 'HASH' in page.locator('#ebError-0-0').inner_text()
    assert persisted(page)==before
    set_field(page,'brokerHash','0009007199254740993123456789-ABC')
    page.locator('[data-eb-save-row="0:0"]').click();settle(page)
    first=order(page);m=projection(page)
    assert first['id']=='CLARITY-001' and first['recordVersion']==1 and first['accountId']=='TABLE-A' and first['periodId']==scope['periodId']
    for actual,expected in [(m['capital']['stopoutEquity']['value'],7800),(m['operational']['exposure']['value'],600),(m['operational']['leverage']['value'],2),(m['rows'][0]['atrMultiple']['value'],15)]:
        assert abs(actual-expected)<1e-8,(actual,expected)
    assert page.locator('[data-p="0"][data-o="0"][data-f="brokerHash"]').count()==1
    assert page.locator('#ebOrderScroll tr.eb-column-labels th').count()==20
    saved=persisted(page);set_field(page,'sl','1.192')
    assert persisted(page)==saved, 'Typing the stop changed confirmed state'
    actual=projection(page)['operational']['exposure']['value'];assert abs(actual-600)<1e-8,actual
    assert page.locator('[data-eb-row="0:0"] [data-eb-calc="atrMultiple"]').text_content()=='4×'
    assert page.locator('[data-eb-row="0:0"] [data-eb-calc="atrMultiple"]').inner_text()=='4×'
    assert not page.evaluate("JPWNavigation.navigate('forex-history')")
    page.locator('#ebLeaveStay').click();settle(page)
    assert field(page,'sl').input_value()=='1.192'
    # Quotes/metrics may repaint; input node and cursor are still the same.
    field(page,'sl').evaluate('e=>{window.__clarityInput=e;e.focus();e.setSelectionRange(2,3)}')
    page.evaluate('JPWForex.executionBoardUI.render()')
    assert field(page,'sl').evaluate('e=>e===window.__clarityInput&&e.selectionStart===2&&e.selectionEnd===3')
    page.locator('[data-eb-cancel-row="0:0"]').click();settle(page)
    assert order(page)==first and persisted(page)==saved
    page.locator('.eb-full-audit>summary').click()
    assert page.locator('.eb-audit-table thead th').count()==25
    assert page.locator('.eb-audit-table input,.eb-audit-table select').count()==0
    assert '0009007199254740993123456789-ABC' in page.locator('.eb-audit-table').inner_text()
    assert persisted(page)==saved
    results.append('PASS: unique controls, HASH refusal, exact saved identity and numeric projections, RAM preview/cancel/guard/focus, complete read-only audit')
    page.locator('.eb-full-audit>summary').click()
    page.locator('#ebDetail-0-0').evaluate('e=>e.open=false')
    field(page,'id').focus()
    for key in ['par','tipo','role','lote','entry','sl','tp']:
        page.keyboard.press('Tab');assert page.evaluate('document.activeElement.dataset.f')==key
        assert page.evaluate("document.activeElement.matches(':focus-visible')&&!document.activeElement.closest('[hidden],[inert]')")
    page.locator('[data-eb-open-detail="0:0"]').click()
    page.keyboard.press('Tab');assert page.evaluate('document.activeElement.dataset.f')=='brokerHash'
    page.locator('#ebDetail-0-0').evaluate('e=>e.open=false')
    assert persisted(page)==saved
    results.append('PASS: keyboard follows compact fields; Details exposes HASH in the same controller, without implicit save')
    measurements=[]
    for theme in ['light','dark']:
        page.evaluate("theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme;}",theme)
        for width in [1440,1024,390,320]:
            page.set_viewport_size({'width':width,'height':960 if width>900 else 844});settle(page)
            page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
            firstTable=page.locator('#ebOrderScroll')
            useful_width=firstTable.evaluate('e=>e.clientWidth')
            if useful_width<768:
                assert firstTable.evaluate('e=>e.scrollWidth<=e.clientWidth+2'),(theme,width,firstTable.evaluate('e=>({scroll:e.scrollWidth,client:e.clientWidth})'))
            else:
                assert firstTable.evaluate('e=>e.scrollWidth>e.clientWidth'),(theme,width,'Workbook horizontal scroll must remain local')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2')
            assert page.locator('[data-eb-row="0:0"]').evaluate("(e,width)=>getComputedStyle(e).display===(width<768?'grid':'table-row')",useful_width)
            for selector in ['[data-eb-save-row="0:0"]','[data-eb-cancel-row="0:0"]','[data-eb-open-detail="0:0"]']:
                box=page.locator(selector).bounding_box();assert box and box['height']>=(36 if useful_width>=768 else 48),(theme,width,selector,box)
            assert_control_targets(page,'#exec')
            page.locator('#ebDetail-0-0').evaluate('e=>e.open=true')
            assert_control_targets(page,'#exec')
            page.locator('#ebDetail-0-0').evaluate('e=>e.open=false')
            for selector in ['id','par','tipo','role','lote','entry','sl','tp','status']:
                assert field(page,selector).evaluate('(e,min)=>parseFloat(getComputedStyle(e).fontSize)>=min',14 if useful_width>=768 else 16),(theme,width,selector)
            heading=page.locator('#executionBoard').evaluate('e=>e.getBoundingClientRect().height')
            assert heading<=(140 if width==1440 else 240),(theme,width,heading)
            assert persisted(page)==saved
            measurements.append({'theme':theme,'viewport':width,'table':firstTable.evaluate('e=>({width:e.clientWidth,scroll:e.scrollWidth,top:e.getBoundingClientRect().top+scrollY})'),'headingHeight':page.locator('#executionBoard').evaluate('e=>e.getBoundingClientRect().height'),'contextTop':page.locator('#executionBoardAccount').evaluate('e=>e.getBoundingClientRect().top+scrollY'),'summaryTop':page.locator('#executionBoardRisk').evaluate('e=>e.getBoundingClientRect().top+scrollY'),'referencesTop':page.locator('#executionBoardInstruments').evaluate('e=>e.getBoundingClientRect().top+scrollY')})
            # Approved workbook reading order: context, confirmed summary, tools,
            # then the continuous grade. The former grade-before-tools assertion
            # belongs to the prior compact-table presentation.
            view=measurements[-1]
            assert view['contextTop']<view['summaryTop']<view['referencesTop']<view['table']['top'],view
            page.screenshot(path=str(out/f'operation-{theme}-{width}.png'),full_page=True)
            firstTable.screenshot(path=str(out/f'orders-{theme}-{width}.png'))
    (out/'measurements.json').write_text(json.dumps(measurements,ensure_ascii=False,indent=2))
    results.append('PASS: light/dark continuous workbook and mobile list at 1440/1024/390/320, 44px actions, contained desktop scroll without page/mobile overflow or state mutation')
    page.set_viewport_size({'width':1440,'height':960})
    page.evaluate("JPWNavigation.navigate('forex-planning')")
    # Exercise new selectors in the original form/binder without creating a plan.
    page.evaluate("()=>{const host=document.createElement('div');host.id='clarityLedgerHost';document.getElementById('fxPlanningRoot').append(host);host.innerHTML=fxpLedgerImportHTML({nextOpenMonth:'2026-09'});fxpBindLedgerImport(host)}")
    assert page.locator('#fxpLedgerAccount').evaluate("e=>e.tagName==='SELECT'")
    assert 'Conta B sintética' in page.locator('#fxpLedgerAccount').inner_text()
    assert '2026-09-01' in page.locator('#fxpLedgerPeriod').inner_text()
    page.locator('#fxpLedgerAccount').select_option('TABLE-B');settle(page)
    assert page.locator('#fxpLedgerPeriod').input_value()==''
    assert '2026-08-01' in page.locator('#fxpLedgerPeriod').inner_text()
    assert page.locator('#fxpLedgerImportBtn').is_disabled()
    assert persisted(page)==saved
    page.evaluate("document.getElementById('clarityLedgerHost').remove()")
    results.append('PASS: ACTUAL origin selectors display names/dates, retain IDs, invalidate preview on explicit account change, never write on selection')
    page.evaluate("JPWNavigation.navigate('forex-consolidated')")
    assert page.locator('#fxcNextAction').is_visible()
    page.locator('#fxcNextAction details').evaluate('e=>e.open=true')
    assert page.locator('#fxcNextAction [data-fxc-go="forex-operation"]').is_visible()
    before=persisted(page)
    page.locator('#fxcAccount').select_option('TABLE-B');settle(page)
    assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='TABLE-A'
    assert persisted(page)==before
    results.append('PASS: panorama next action and analytic selection remain independent of the operational context')
    audit_measurements=[]
    for width in [1440,1024,390,320]:
        page.set_viewport_size({'width':width,'height':960 if width>900 else 844})
        for theme in ['light','dark']:
            page.evaluate("theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme;}",theme)
            page.evaluate("JPWNavigation.navigate('forex-consolidated')");settle(page)
            if page.locator('#fxContextToggle').get_attribute('aria-expanded')=='true':page.locator('#fxContextToggle').click()
            controls=assert_control_targets(page,'#fxconsolidated')
            for selector in ['#fxcAccount','#fxcFrom','#fxcTo','#fxcSearch','#fxcOpenImport']:
                assert page.locator(selector).evaluate('e=>parseFloat(getComputedStyle(e).fontSize)>=16'),(width,theme,selector)
            geometry=page.evaluate("({action:document.getElementById('fxcNextAction').getBoundingClientRect().top+scrollY,context:document.getElementById('fxOperationalContext').getBoundingClientRect().top+scrollY})")
            if width<=1100:assert geometry['action']<geometry['context'],(width,theme,geometry)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2')
            page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
            page.screenshot(path=str(out/f'overview-audit-{theme}-{width}.png'))
            audit_measurements.append({'width':width,'theme':theme,'geometry':geometry,'controls':controls})
            assert persisted(page)==saved
    page.locator('#fxContextToggle').click();settle(page)
    assert page.locator('#fxconsolidated').evaluate("e=>e.classList.contains('fx-context-expanded')")
    assert page.locator('#fxOperationalContext').evaluate("e=>getComputedStyle(e).order==='-1'")
    assert_control_targets(page,'#fxconsolidated')
    page.locator('#fxContextToggle').click();settle(page)
    assert persisted(page)==saved
    (out/'audit-measurements.json').write_text(json.dumps(audit_measurements,ensure_ascii=False,indent=2))
    page.evaluate("JPWNavigation.navigate('forex-history');enhanceSectionExpl(document.getElementById('execHistory'));applyExplMode()")
    assert page.locator('#histEmptyMessage').is_visible() and 'Sem operações finalizadas' in page.locator('#histEmptyMessage').inner_text()
    assert not page.locator('#histEmptyMessage').evaluate("e=>e.classList.contains('expl')||e.hasAttribute('data-info')")
    assert_control_targets(page,'#execHistory')
    before=persisted(page)
    assert page.evaluate("JPWNavigation.navigate('forex-management-accounts')");settle(page)
    assert page.evaluate("JPWNavigation.current().child==='forex-management-accounts'") and persisted(page)==before
    page.evaluate("JPWNavigation.navigate('forex-history')")
    assert page.evaluate("JPWNavigation.navigate('forex-operation')");settle(page)
    assert page.evaluate("JPWNavigation.current().child==='forex-operation'") and persisted(page)==before
    results.append('PASS: audit findings reproduced and controlled: panorama before mobile context, real 44px targets/16px input text, visible empty-history reason/next steps without writes')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--css',type=Path);ap.add_argument('--portable',action='store_true');args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in OWNED}
    report={'classification':'NOT_RUN','source_sha256':before,'cases':[],'pageerrors':[],'css_injected':str(args.css) if args.css else None,'entry':'portable' if args.portable else 'source'}
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options());report['browser']=browser.version
            context=browser.new_context(viewport={'width':1440,'height':960},service_workers='block');context.add_init_script('window.__onbShown=true;');install_bootstrap(context)
            page=context.new_page();page.set_default_timeout(10000);page.on('pageerror',lambda e:report['pageerrors'].append(str(e)));page.on('dialog',lambda d:d.accept())
            entry='dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html' if args.portable else 'index.html'
            page.goto(f'http://127.0.0.1:{server.server_port}/{entry}');ready(page)
            if args.css:page.add_style_tag(content=args.css.read_text())
            run(page,args.out,report['cases']);assert not report['pageerrors'],report['pageerrors'];assert_fixture_requests(context)
            assert before=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in OWNED},'Owned candidate changed during focal'
            report['classification']='PASS';context.close();browser.close()
    except Exception as e:
        report['classification']='PRODUCT_FAIL';report['error']=str(e);report['traceback']=traceback.format_exc()
    finally:
        server.shutdown();server.server_close();(args.out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['classification']=='PASS' else 1)
if __name__=='__main__':main()
