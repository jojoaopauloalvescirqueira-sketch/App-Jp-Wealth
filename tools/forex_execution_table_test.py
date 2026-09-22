#!/usr/bin/env python3
"""Execution table UI: explicit writes, RAM previews, diagnostics and geometry.
Disposable browser contexts and synthetic facts only. No product or real profile
writes. Screenshots support, but never replace, behavioral and numeric assertions.
"""
import argparse
import base64
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import tempfile
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options, settle

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['index.html', 'build-id.js', 'src/js/manifest.json', 'src/styles/app.css', 'src/js/20-ui/30-execution-board.js',
           'src/js/10-domain/18-execution-board-model.js', 'src/js/10-domain/00-forex-state.js',
           'src/js/10-domain/11-operation-lifecycle.js', 'src/js/20-ui/13-exec-views.js']
HASH = '0009007199254740993123456789-ABC'
SEED = r'''() => {
  closeModal();window.__onbShown=true;window.confirm=()=>true;
  const instruments=structuredClone(S.instruments);
  S=structuredClone(DEFAULTS);migrate();S.instruments=instruments;S.onboarding.done=true;
  S.accounts=[{forexAccountId:'TABLE-A',nome:'Conta sintética da tabela',tipo:'MESTRE',platformCurrency:'USD',platform:'MT5',platformLogin:'TEST-001'}];
  S.forex=JPWForex.state.empty();S.operationHistory={schemaVersion:2,records:[]};
  if(save()!==true)throw Error('Synthetic seed refused');
  const api=JPWForex.state;
  const require=r=>{if(!r?.ok)throw Error(JSON.stringify(r));return r;};
  require(api.recordAccountPeriod({accountId:'TABLE-A',startedAt:'2026-09-01',currency:'USD',si:10000,openingBook:12000,source:'Synthetic opening balance',activateCurrentPeriod:true},{reason:'Synthetic UI fixture'}));
  require(api.selectOperationalAccount('TABLE-A'));
  const scope=api.operationalSelection(),at='2026-09-22T12:00:00Z';
  require(api.recordAccountFacts({accountIndex:0,periodId:scope.periodId,si:10000,equity:12000,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',source:'Synthetic equity observation',observedAt:at},{reason:'Synthetic observation'}));
  require(api.recordInstrumentContext({...scope,instrumentId:'EURUSD',expectedRevision:0,componentChanges:{
    price:{value:1.3,source:'Synthetic market price',observedAt:at},
    atr:{short:.002,long:.001,timeframe:'H4',unit:'PRICE',source:'Synthetic H4 ATR',observedAt:at},
    contract:{contractSize:100000,source:'Synthetic contract',observedAt:at},
    conversion:{baseToAccountRate:1.2,quoteToAccountRate:1,source:'Synthetic conversion',observedAt:at}
  }},{reason:'Synthetic instrument references',expectedEpoch:jpWealthPersistenceEpoch()}));
  render();JPWNavigation.navigate('forex-operation');renderPhases();
  return scope;
}'''

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

class Server(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True

def source_hashes():
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}

def field(page, key):
    return page.locator(f'[data-p="0"][data-o="0"][data-f="{key}"]')

def persisted(page):
    return page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),local:JSON.stringify(Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)])))})')

def order(page):
    return page.evaluate('JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases[0].orders[0]')

def projection(page):
    return page.evaluate('JPWForex.executionBoard.read()')

def near(actual, expected):
    assert isinstance(actual, (int, float)) and abs(actual-expected) < 1e-8, (actual, expected)

def set_field(page, key, value):
    control=field(page,key)
    control.evaluate("e=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;}")
    if isinstance(value,bool): control.set_checked(value)
    elif control.evaluate('e=>e.tagName') == 'SELECT': control.select_option(str(value))
    else: control.fill(str(value))
    settle(page)

def ready(page):
    wait_bootstrap(page)
    page.wait_for_function("typeof S==='object' && !!S && typeof render==='function' && typeof $==='function' && !!JPWForex?.executionBoardUI")
    settle(page)

def table(page): return page.locator('#ebPhase-0 .eb-table-scroll:has(.eb-order-table)')

def run(page, artifacts, results, skip_matrix=False):
    scope=page.evaluate(SEED);settle(page)
    assert page.locator('#executionBoard').is_visible()
    before=persisted(page)
    summary=page.locator('#executionBoardRisk').inner_text()
    values=dict(id='INTERNAL-001',par='EURUSD',tipo='BUY',role='GENESIS',lote='0.2',entry='1.2',sl='1.17',tp='1.26',
                status='Aberta',costs='0',costBasis='SEPARATE_FROM_RESULT',stopValidated=True)
    for key,value in values.items():set_field(page,key,value)
    assert persisted(page)==before, 'Typing wrote confirmed state'
    assert page.locator('#executionBoardRisk').inner_text()==summary, 'Draft changed confirmed totals'
    page.locator('[data-eb-save-row="0:0"]').click();settle(page)
    assert persisted(page)==before, 'Missing HASH was accepted'
    assert 'HASH' in page.locator('#ebError-0-0').inner_text()
    assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
    set_field(page,'brokerHash',HASH)
    assert field(page,'brokerHash').input_value()==HASH
    assert persisted(page)==before
    page.locator('[data-eb-save-row="0:0"]').click();settle(page)
    first=order(page)
    assert first['id']=='INTERNAL-001' and first['brokerHash']==HASH
    assert first['accountId']=='TABLE-A' and first['periodId']==scope['periodId']
    assert first['status']=='Aberta' and first['role']=='GENESIS' and first['stopValidated'] is True
    assert first['costBasis']=='SEPARATE_FROM_RESULT' and first['recordVersion']==1
    assert len(first['revisions'])==1 and not page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
    m=projection(page)
    near(m['capital']['stopoutEquity']['value'],7800)
    near(m['operational']['exposure']['value'],600)
    near(m['operational']['exposure']['percent'],5)
    near(m['operational']['leverage']['value'],2)
    near(m['rows'][0]['atrMultiple']['value'],15)
    assert '7.800' in page.locator('[data-eb-metric="hardStop"] strong').inner_text()
    assert '600' in page.locator('[data-eb-metric="totalExposure"] strong').inner_text()
    results.append('PASS: save by row, missing HASH refusal, exact long textual HASH, account/period and financial projections')

    saved=persisted(page);summary=page.locator('#executionBoardRisk').inner_text()
    set_field(page,'sl','1.192')
    assert page.locator('[data-eb-row="0:0"] [data-eb-calc="atrMultiple"]').inner_text()=='4×'
    assert 'não salva' in page.locator('[data-eb-preview="0:0"]').inner_text()
    assert persisted(page)==saved and page.locator('#executionBoardRisk').inner_text()==summary
    assert not page.evaluate("JPWNavigation.navigate('forex-history')")
    assert page.locator('#executionBoardDialog').is_visible()
    page.locator('#ebLeaveStay').click();settle(page)
    assert page.evaluate("JPWNavigation.current().child==='forex-operation'")
    assert field(page,'sl').input_value()=='1.192' and persisted(page)==saved
    page.locator('[data-eb-cancel-row="0:0"]').click();settle(page)
    assert order(page)==first and persisted(page)==saved
    assert field(page,'sl').input_value()=='1.17'
    assert page.evaluate("JPWNavigation.navigate('forex-history')")
    assert page.locator('#execHistory').is_visible() and not page.locator('#executionBoard').is_visible()
    assert page.evaluate('S.operationHistory.records.length')==0, 'Open operation leaked into final history'
    assert persisted(page)==saved
    assert page.evaluate("JPWNavigation.navigate('forex-operation')")
    results.append('PASS: entry-stop ATR preview without persistence/totals, cancel, real draft guard and independent History')

    page.locator('#ebInstrumentSelect').select_option('EURUSD')
    page.locator('[data-eb-diagnostics]').click()
    for key in ['oneWeekN','oneWeekF','twoWeeksN','twoWeeksF']:
        assert page.locator(f'#ebDiagnosticForm [name="{key}"]').input_value()==''
    page.locator('#ebDiagnosticForm [name="oneWeekN"]').fill('25')
    page.locator('#ebDiagnosticForm [name="declaredBy"]').fill('Synthetic operator')
    page.locator('#ebDiagnosticForm [name="reason"]').fill('Synthetic one-week declaration')
    page.locator('#ebDiagnosticForm [type="submit"]').click();settle(page)
    assert 'juntos' in page.locator('#ebDiagnosticError').inner_text() and persisted(page)==saved
    page.locator('#ebDiagnosticForm [name="oneWeekF"]').fill('1.5')
    page.locator('#ebDiagnosticForm [type="submit"]').click();settle(page)
    assert not page.locator('#executionBoardDialog').is_visible()
    diag=page.evaluate("JPWForex.state.executionDiagnostics({...JPWForex.state.operationalSelection(),instrumentId:'EURUSD'})")
    assert diag['value']['oneWeek']=={'n':25,'f':1.5} and diag['value']['twoWeeks'] is None
    m=projection(page);instrument=next(x for x in m['instruments'] if x['id']=='EURUSD')
    near(instrument['rootN']['oneWeek']['value'],.015)
    near(m['rows'][0]['rootN']['oneWeek']['percent'],1.25)
    assert instrument['rootN']['twoWeeks']['value'] is None
    assert order(page)==first, 'Diagnostic changed an executed stop or order'
    confirmed=persisted(page)
    page.locator('[data-eb-diagnostics]').click()
    page.locator('#ebDiagnosticForm [name="twoWeeksN"]').fill('100')
    page.locator('#ebDiagnosticForm [name="twoWeeksF"]').fill('2')
    page.locator('#ebDiagnosticCancel').click();settle(page)
    assert persisted(page)==confirmed, 'Cancelled diagnostics persisted'
    page.reload();ready(page);page.evaluate("window.__onbShown=true;window.confirm=()=>true;JPWNavigation.navigate('forex-operation')");settle(page)
    assert order(page)['brokerHash']==HASH
    assert page.evaluate("JPWForex.state.executionDiagnostics({...JPWForex.state.operationalSelection(),instrumentId:'EURUSD'}).value.oneWeek.n")==25
    assert page.evaluate("JPWForex.state.executionDiagnostics({...JPWForex.state.operationalSelection(),instrumentId:'EURUSD'}).value.twoWeeks===null")
    page.locator('#ebInstrumentSelect').select_option('EURUSD')
    page.locator('[data-eb-diagnostics]').click()
    assert page.locator('#ebDiagnosticForm [name="oneWeekF"]').input_value()=='1.5'
    assert page.locator('#ebDiagnosticForm [name="twoWeeksN"]').input_value()==''
    page.locator('#ebDiagnosticForm [name="twoWeeksN"]').fill('100')
    page.locator('#ebDiagnosticForm [name="twoWeeksF"]').fill('2')
    page.locator('#ebDiagnosticForm [name="reason"]').fill('Synthetic second horizon')
    page.locator('#ebDiagnosticForm [type="submit"]').click();settle(page)
    instrument=next(x for x in projection(page)['instruments'] if x['id']=='EURUSD')
    near(instrument['rootN']['twoWeeks']['value'],.04)
    assert order(page)['sl']==1.17
    results.append('PASS: independent N/F horizons, no defaults, invalid pair refusal, cancelled changes, reload and exact HASH')

    # Real key events preserve focus order and do not implicitly commit a draft.
    before=persisted(page)
    field(page,'id').focus()
    for key in ['brokerHash','par','tipo','role']:
        page.keyboard.press('Tab')
        assert page.evaluate('document.activeElement.dataset.f')==key
        assert page.evaluate("document.activeElement.matches(':focus-visible')&&!document.activeElement.closest('[hidden],[inert]')")
    page.keyboard.press('Shift+Tab')
    assert page.evaluate('document.activeElement.dataset.f')=='tipo'
    field(page,'sl').focus();page.keyboard.press('ControlOrMeta+A');page.keyboard.type('1.169');page.keyboard.press('Tab')
    assert field(page,'sl').input_value()=='1.169' and persisted(page)==before
    details=page.locator('[data-eb-detail="0:0"]')
    details.evaluate('e=>e.open=true')
    page.locator('[data-eb-reason="0:0"]').fill('Synthetic refused correction')
    page.evaluate('() => {window.__tableSave=save;save=()=>false;}')
    try:
        page.locator('[data-eb-save-row="0:0"]').click();settle(page)
        assert persisted(page)==before, 'Refused write leaked a draft into confirmed state'
        assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
        assert field(page,'sl').input_value()=='1.169' and page.locator('#ebError-0-0').inner_text().strip()
    finally:
        page.evaluate('() => {save=window.__tableSave;}')
    # The competing accepted correction uses the real writer, not a direct S edit.
    result=page.evaluate("operationRecordOrder(0,0,{tp:1.28},{reason:'Synthetic competing correction'})")
    assert result['ok'], result
    concurrent=persisted(page)
    page.locator('[data-eb-save-row="0:0"]').click();settle(page)
    assert persisted(page)==concurrent, 'Stale draft overwrote a newer confirmed version'
    assert 'versão confirmada mudou' in page.locator('#ebError-0-0').inner_text()
    assert field(page,'sl').input_value()=='1.169' and page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
    page.locator('[data-eb-cancel-row="0:0"]').click();settle(page)
    assert field(page,'sl').input_value()=='1.17' and field(page,'tp').input_value()=='1.28'
    assert persisted(page)==concurrent
    results.append('PASS: real Tab/Shift+Tab/text keys and focus-visible; refused write and concurrent revision preserve draft and confirmed data')

    if page.locator('#dgBannerClose').is_visible():page.locator('#dgBannerClose').click()
    for width in [1440,390]:
        page.set_viewport_size({'width':width,'height':1000 if width>900 else 844})
        page.evaluate("document.documentElement.dataset.theme='light';window.scrollTo({top:0,behavior:'instant'})")
        settle(page);page.screenshot(path=str(artifacts/f'board-top-{width}.png'))
        for region in ['executionBoardAccount','executionBoardRisk','executionBoardInstruments']:
            page.locator('#'+region).scroll_into_view_if_needed();settle(page)
            page.screenshot(path=str(artifacts/f'board-{region}-{width}.png'))
    results.append('PASS: separate desktop/mobile context, summary and instrument captures')

    if skip_matrix:
        results.append('NOT_RUN: viewport matrix omitted explicitly; prior matrix receipt is separate')
        return

    # Each viewport retains a real table, with internal horizontal scrolling.
    # Position is checked after a horizontal movement, not inferred from CSS alone.
    page.evaluate("() => {for(let n=0;n<7;n++){const r=operationAddDraft(0);if(!r.ok)throw Error(r.error);}render();renderPhases();}")
    if page.locator('#dgBannerClose').is_visible():page.locator('#dgBannerClose').click()
    before=persisted(page)
    for width in [1440,1280,1024,900,768,390,320]:
        page.set_viewport_size({'width':width,'height':1000 if width>900 else 844})
        for theme in ['light','dark']:
            page.evaluate("t=>{document.documentElement.dataset.theme=t;document.getElementById('ebPhase-0').open=true;}",theme)
            settle(page)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), (width,theme,'document overflow')
            geometry=table(page).evaluate('''e=>{
              const row=e.querySelector('.eb-order-row'),head=e.querySelector('thead tr:last-child th');
              e.scrollTop=0;e.scrollLeft=350;
              const headTop=head.getBoundingClientRect().top;e.scrollTop=110;
              return {vertical:e.scrollTop>0,headerMovement:Math.abs(head.getBoundingClientRect().top-headTop),overflow:e.scrollWidth>e.clientWidth,kind:getComputedStyle(row).display,
                cells:[...row.children].map(c=>getComputedStyle(c).display),
                head:getComputedStyle(head).position,id:getComputedStyle(row.firstElementChild).position,
                second:getComputedStyle(row.children[1]).position,
                edge:Math.abs(row.firstElementChild.getBoundingClientRect().left-e.getBoundingClientRect().left)};
            }''')
            assert geometry['overflow'] and geometry['kind']=='table-row', (width,theme,geometry)
            assert set(geometry['cells'])=={'table-cell'}, (width,theme,geometry)
            assert geometry['vertical'] and geometry['headerMovement']<3 and geometry['head']=='sticky' and geometry['id']=='sticky' and geometry['edge']<3, (width,theme,geometry)
            if width<=767:assert geometry['second']=='static', (width,theme,geometry)
            page.locator('#ebPhase-0').scroll_into_view_if_needed();settle(page)
            page.screenshot(path=str(artifacts/f'table-{width}-{theme}.png'))
    assert persisted(page)==before, 'Resize/theme/scroll changed confirmed financial state'
    results.append('PASS: 1440/1280/1024/900/768/390/320, two themes, table cells, contained overflow and actual sticky headers/ID')

def native_zoom(pw, url, artifacts, results):
    profile=Path(tempfile.mkdtemp(prefix='execution-native-200-',dir=artifacts))
    (profile/'Default').mkdir()
    (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    options=launch_options();options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
    context=pw.chromium.launch_persistent_context(str(profile),**options)
    errors=[]
    try:
        context.add_init_script('window.__onbShown=true;');install_bootstrap(context)
        page=context.pages[0] if context.pages else context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
        page.bring_to_front()
        page.goto(url);ready(page);page.evaluate(SEED);settle(page)
        page.wait_for_function("document.visibilityState==='visible'")
        assert page.locator('#executionBoard').is_visible()
        ratio=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
        assert abs(ratio['outer']/ratio['inner']-2)<.01 and ratio['css']=='1', ('Native 200% not established',ratio)
        page.locator('#ebPhase-0').evaluate('e=>e.open=true')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert table(page).evaluate("e=>e.scrollWidth>e.clientWidth&&getComputedStyle(e.querySelector('.eb-order-row')).display==='table-row'")
        field(page,'id').focus();page.keyboard.press('Tab')
        assert page.evaluate("document.activeElement.dataset.f==='brokerHash'&&document.activeElement.matches(':focus-visible')")
        page.locator('#ebPhase-0').scroll_into_view_if_needed();settle(page)
        cdp=context.new_cdp_session(page)
        (artifacts/'table-native-200.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':False,'captureBeyondViewport':False})['data']))
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})");settle(page)
        (artifacts/'board-native-200.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':False,'captureBeyondViewport':False})['data']))
        assert not errors,errors
        assert_fixture_requests(context)
        results.append('PASS: native browser 200% zoom (outer/inner=2; CSS zoom=1), table/overflow/focus and dedicated screenshots')
    finally:
        context.close()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',type=Path,required=True);parser.add_argument('--skip-matrix',action='store_true');parser.add_argument('--native-zoom',action='store_true');args=parser.parse_args()
    args.artifacts.mkdir(parents=True,exist_ok=True)
    before=source_hashes();results=[];errors=[];report={'source_sha256':before,'results':results}
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options());report['browser']=browser.version
            context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
            context.add_init_script('window.__onbShown=true;');install_bootstrap(context)
            page=context.new_page();page.set_default_timeout(10000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('dialog',lambda d:d.accept())
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html');ready(page)
            run(page,args.artifacts,results,args.skip_matrix)
            assert not errors, errors
            assert_fixture_requests(context)
            context.close();browser.close()
            if args.native_zoom:native_zoom(pw,f'http://127.0.0.1:{server.server_port}/index.html',args.artifacts,results)
            assert before==source_hashes(), 'Candidate changed while the focal was running'
            report['result']='PASS'
    except BaseException as error:
        report['result']='FAIL — classification requires triage';report['error']=str(error);report['trace']=traceback.format_exc();raise
    finally:
        report['pageerrors']=errors
        (args.artifacts/'focal-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        server.shutdown()
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
