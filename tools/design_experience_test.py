#!/usr/bin/env python3
"""DESIGN01 D2–D4: presentation journeys over existing synthetic domain fixtures.

Expectations fixed before product patches. Missing baseline capabilities remain
PRODUCT_FAIL against the new requirement; --baseline never converts them to PASS.
No financial formula, external API, real profile, clipboard or Git write is used.
"""
import argparse
from collections import Counter
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import threading
import time

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]
AREAS = ('dashboard', 'forex', 'settings', 'alladin', 'charts', 'lab')
INPUTS = ['index.html', 'src/styles/app.css', 'src/js/20-ui/25-dash-macro.js',
          'src/js/20-ui/24-alladin-views.js', 'src/js/20-ui/07-chart-crosshair-tooltip.js',
          'src/js/40-app/09-settings-modal.js', 'src/js/20-ui/23-research-views.js',
          'src/js/40-app/18-galton-board/06-controller.js', 'build-id.js']

# Same public cadastro/ledger APIs and vocabulary as alladin_ui_ledger_test.py.
# Each mutation must be accepted before its record participates in an oracle.
ALLADIN_SEED = """() => {
  const C=JPWAlladin.cadastro,L=JPWAlladin.ledger;
  const need=r=>{if(!r||!r.ok||!r.recordId)throw Error('Fixture refused: '+JSON.stringify(r));return r.recordId};
  const account=need(C.addAccount({name:'Conta sintética',institution:'Laboratório',accountType:'BROKERAGE'}));
  const cash=need(C.addCashAccount({accountId:account,currency:'BRL'}));
  const cash2=need(C.addCashAccount({accountId:account,currency:'BRL'}));
  const deposit=need(L.addTransaction({eventType:'DEPOSIT',cashAccountId:cash,amount:100000,effectiveAt:'2026-01-10',note:'APORTE SINTÉTICO'}));
  const original=need(L.addTransaction({eventType:'ADJUSTMENT_CREDIT',cashAccountId:cash,amount:250,effectiveAt:'2026-01-12',reason:'AJUSTE-ORIGINAL'}));
  const transfer=need(L.addTransaction({eventType:'TRANSFER',sourceCashAccountId:cash,destinationCashAccountId:cash2,amount:1000,effectiveAt:'2026-01-14',flowScope:'INTERNAL'}));
  const reversal=need(L.reverseTransaction(original,{effectiveAt:'2026-01-18',reason:'ESTORNO-SINTÉTICO'}));
  const model=JPWAlladin.leitura.ledger();
  if(!model.available||model.transactions.length!==4)throw Error('Unexpected fixture ledger');
  return {account,cash,cash2,deposit,original,transfer,reversal};
}"""

SETUP = """theme => {
  window.__onbShown=true;closeModal();
  S.theme=theme;applyTheme();S.params.saldoIni=10000;S.params.saldoAtu=10200;
  S.params.inicio='2026-01-01';
  S.ledger=[{data:'2026-01-03',saldo:10123,resultado:123,nota:'fixture'},
            {data:'2026-01-17',saldo:10200,resultado:77,nota:'fixture'}];
  S.onboarding={...S.onboarding,done:false};render();renderDash();
  JPWNavigation.navigate('dashboard');
}"""
SNAPSHOT = """() => ({state:JSON.stringify(S),
  storage:JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)])),
  saves:window.__designSaves||0})"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class Checks:
    def __init__(self, case):
        self.case = case
        self.items = []

    def check(self, name, passed, detail=None):
        item = {'name': name, 'result': 'PASS' if passed else 'PRODUCT_FAIL', 'detail': detail}
        self.items.append(item)
        print(f"{item['result']} {self.case} {name}", flush=True)
        return bool(passed)

    def unavailable(self, name):
        self.items.append({'name': name, 'result': 'NOT_RUN', 'detail': 'Required capability absent; dependent interaction not attempted.'})


def navigate(page, route):
    if not page.evaluate('(r)=>JPWNavigation.navigate(r)', route):
        raise AssertionError('Public navigation refused ' + route)


def dashboard(page, c):
    for key, route, primary in [('forex','forex-overview','forex'),
                                ('personal-finance','personal-finance','personal-finance'),
                                ('research','research-forex','research'),('alladin','alladin','alladin')]:
        navigate(page,'dashboard')
        card=page.locator(f'[data-dm-card="{key}"]')
        cta=card.locator('.dm-cta')
        c.check('dashboard CTA in header '+key, cta.count()==1 and cta.evaluate('(e)=>!!e.closest(".dm-card-head")'))
        c.check('dashboard CTA retains destination '+key, cta.get_attribute('data-dm-route')==route)
        cta.focus();page.keyboard.press('Enter')
        c.check('dashboard keyboard CTA navigates '+key, page.evaluate('JPWNavigation.current().primary')==primary)
    navigate(page,'dashboard')
    c.check('dashboard lower widgets remain two',page.evaluate("() => [...document.querySelectorAll('#gdDashMain [data-layout-card]')].map(e=>e.dataset.layoutCard).sort()") == ['institutional-panel','quick-actions'])


def forex(page,c):
    navigate(page,'forex-overview')
    result=page.evaluate("""() => {
      const quick=document.getElementById('execOverviewQuickNav');
      return ['onboardingIncompleteBanner','mcClearanceCard'].map(id=>{
        const e=document.getElementById(id),a=e.getBoundingClientRect(),b=quick.getBoundingClientRect();
        return {id,owner:!!e.closest('#fxOverviewWidgets'),before:!!(e.compareDocumentPosition(quick)&Node.DOCUMENT_POSITION_FOLLOWING),top:a.top,bottom:a.bottom,quickTop:b.top};
      });
    }""")
    for row in result:
        c.check('Forex readiness precedes secondary tools '+row['id'],row['owner'] and row['before'] and row['bottom']<=row['quickTop']+1,row)
    c.check('Forex context shown',page.locator('#gdContextRow').is_visible())
    for route in ['research-probability-lab','dashboard']:
        navigate(page,route)
        c.check('Forex context absent '+route,not page.locator('#gdContextRow').is_visible())


def settings(page,c):
    navigate(page,'dashboard')
    page.locator('#headerConfigBtn').click()
    search=page.locator('#settingsSearch')
    size=search.bounding_box()
    c.check('Settings readable search width',size['width']>=min(240,page.viewport_size['width']-80),size)
    search.fill('backup')
    choices=page.locator('#settingsSearchResults [data-settings-result]')
    c.check('Settings search matches real destination',choices.count()>0)
    if choices.count():
        choices.first.focus();page.keyboard.press('Enter')
        c.check('Settings result opens correct page','Backup' in page.locator('#settingsPageTitle').inner_text() or 'Base de Dados' in page.locator('#settingsPageTitle').inner_text())
        c.check('Settings result transfers focus to content',page.evaluate("document.activeElement.id==='settingsContent'||document.getElementById('settingsContent').contains(document.activeElement)"))
    page.keyboard.press('Escape')
    c.check('Settings Escape closes',not page.locator('#settingsOverlay').is_visible())
    page.wait_for_function("document.activeElement.id==='headerConfigBtn'")
    c.check('Settings focus returns to opener',page.locator('#headerConfigBtn').evaluate('(e)=>e===document.activeElement'))


def ledger_rows(page):
    # alladinTabela has a header tr without thead; Chromium places it in tbody.
    # Select data rows, as the established ledger regression does with slice(1).
    return page.locator('#alladinLedger tr:has(td):visible').all_text_contents()


def alladin(page,c):
    navigate(page,'alladin')
    page.evaluate("JPWAlladinUI.selectView('ledger')")
    before=page.evaluate(SNAPSHOT)
    model=page.evaluate('JPWAlladin.leitura.ledger()')
    original_rows=ledger_rows(page)
    c.check('Alladin complete fixture read-model available',model['available'] and len(original_rows)==len(model['transactions'])==4,{'available':model['available'],'rows':len(original_rows),'transactions':len(model['transactions'])})
    c.check('Alladin dates remain in canonical order',all(tx['effectiveAt'] in row and tx['recordedAt'] in row for tx,row in zip(model['transactions'],original_rows)))
    query=page.locator('#alladinLedgerSearch')
    if not c.check('Alladin visual search available',query.count()==1):
        c.unavailable('Alladin filter interactions');return
    query.fill('2026-01-12')
    rows=ledger_rows(page)
    c.check('Alladin filter only selected presentation row',len(rows)==1 and '2026-01-12' in rows[0],rows)
    c.check('Alladin reversal outside filter still disables original',page.locator('#alladinLedger [data-ald-tx-reverse]:visible').count()==0 and 'Estornado' in page.locator('#alladinLedger').inner_text())
    query.fill('2026-01-10')
    c.check('Alladin eligible original retains exact reverse identity',page.locator('#alladinLedger [data-ald-tx-reverse]:visible').count()==1 and page.locator('#alladinLedger [data-ald-tx-reverse]:visible').get_attribute('data-ald-tx-reverse')==page.evaluate('__designFixture.deposit'))
    query.fill('SEM-CORRESPONDÊNCIA-SINTÉTICA')
    text=page.locator('#alladinLedger').inner_text()
    c.check('Alladin filtered empty is not absent history',len(ledger_rows(page))==0 and 'Nenhum lançamento registrado.' not in text and 'indisponíveis' not in text.lower(),text)
    query.fill('')
    c.check('Alladin clearing filter restores all original rows',ledger_rows(page)==original_rows)
    query.fill('2026-01-14')
    c.check('Alladin ambiguous cash labels preserve both IDs',all(page.evaluate('__designFixture.'+k) in page.locator('#alladinLedger tbody').inner_text() for k in ['cash','cash2']))
    query.fill('')
    c.check('Alladin navigation/search have zero financial or storage writes',page.evaluate(SNAPSHOT)==before)
    # Corrupt an unmatched record only in this disposable browser memory. It
    # must prevent the entire projection, not disappear behind a valid filter.
    query.fill('2026-01-10')
    corrupt=page.evaluate("""() => {
      window.__designGoodAlladin=JSON.stringify(S.alladin);
      S.alladin.transactions.find(t=>t.transactionId===__designFixture.transfer).amount='INVALID';
      const model=JPWAlladin.leitura.ledger();JPWAlladinUI.selectView('ledger');return model.available;
    }""")
    c.check('Alladin fixture invalidates full envelope',corrupt is False)
    c.check('Alladin unmatched corruption blocks filtered projection',not ledger_rows(page) and 'indisponíveis' in page.locator('#alladinLedger').inner_text().lower())
    page.evaluate("() => {S.alladin=JSON.parse(__designGoodAlladin);JPWAlladinUI.selectView('ledger')}")


def charts(page,c):
    navigate(page,'forex-overview')
    before=page.evaluate(SNAPSHOT)
    svg=page.locator('#chMoney')
    c.check('Forex chart keyboard focusable',svg.get_attribute('tabindex')=='0')
    inspector=svg.locator('..').locator('.chart-inspector')
    if not c.check('Forex chart has visible data inspector',inspector.count()==1):
        c.unavailable('Forex chart keyboard/touch inspection');return
    select=inspector.get_by_role('combobox',name='Observação do gráfico')
    reading=inspector.locator('.chart-reading')
    c.check('Forex chart inspector text exposed',reading.get_attribute('role')=='status' and reading.is_visible())
    options=select.locator('option').all_text_contents()
    c.check('Forex chart multiple observations available',len(options)>1)
    svg.focus();page.keyboard.press('Home')
    first=select.input_value();page.keyboard.press('ArrowRight')
    c.check('Forex chart ArrowRight changes selected observation',select.input_value()!=first)
    page.keyboard.press('End');last=select.input_value()
    end_text=reading.inner_text()
    expected_last=page.evaluate('fmtMoney(10200)')
    c.check('Forex future projection retains actual last-real date and value',
            '17/01/2026' in end_text and expected_last in end_text,end_text)
    page.keyboard.press('ArrowLeft')
    c.check('Forex chart ArrowLeft from end changes selection',select.input_value()!=last)
    # A sparse real series is inspected alongside a denser projection: each
    # real label must retain the date of its actual point, not the cursor day.
    select.select_option(index=min(1,len(options)-1))
    text=reading.inner_text()
    c.check('Forex chart reading identifies series and real values','Real' in text or 'real' in text,text)
    labels=page.evaluate("() => [S.params.inicio,...ledgerSorted().map(e=>e.data)].flatMap(d=>[d,d.slice(8,10)+'/'+d.slice(5,7)+'/'+d.slice(0,4),d.slice(8,10)+'/'+d.slice(5,7)])")
    c.check('Forex chart real observation includes actual series date',any(label in text for label in labels),text)
    svg.focus();page.keyboard.press('Home');touch_before=select.input_value()
    svg.scroll_into_view_if_needed();box=svg.bounding_box()
    page.touchscreen.tap(box['x']+box['width']*.7,box['y']+box['height']*.5)
    c.check('Forex chart touch changes selected observation',select.input_value()!=touch_before)
    c.check('Forex chart touch leaves readable feedback',bool(reading.inner_text().strip()) and reading.is_visible())
    page.evaluate('renderDashCharts();renderDashCharts()')
    c.check('Forex repeated render has one inspector per chart',page.locator('#dashCharts .chart-inspector').count()==1 and page.locator('#dashRiskDetail .chart-inspector').count()==1)
    rebound=page.evaluate("""() => {
      const original=bindChartCrosshair,configs=new Map();
      // Capture the existing renderer's exact configurations, without copying
      // its calculations or inventing a second financial source.
      try{
        bindChartCrosshair=(svg,cfg)=>{configs.set(svg.id,cfg);return original(svg,cfg)};
        renderDashCharts();
      }finally{bindChartCrosshair=original;}
      const svg=document.getElementById('chMoney'),cfg=configs.get('chMoney');
      original(svg,cfg);original(svg,cfg);
      return {inspectors:svg.parentNode.querySelectorAll('.chart-inspector').length,
        tips:svg.parentNode.querySelectorAll('.chart-tip').length};
    }""")
    c.check('Forex same-SVG rebind has one inspector and tooltip',rebound=={'inspectors':1,'tips':1},rebound)
    svg.focus();page.keyboard.press('Home');page.keyboard.press('ArrowRight')
    c.check('Forex same-SVG rebind has one keyboard handler',select.evaluate('(e)=>e.selectedIndex')==1)
    c.check('Forex chart inspection does not save or alter state',page.evaluate(SNAPSHOT)==before)


def lab(page,c):
    navigate(page,'research-probability-lab')
    root=page.locator('#researchGaltonSlot [data-galton-root]')
    c.check('Lab has one instance',root.count()==1 and page.locator('[data-galton-root]').count()==1)
    order=root.evaluate("e=>{const a=e.querySelector('.galton-controls'),b=e.querySelector('.galton-stage');return {before:!!(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING),bottom:a.getBoundingClientRect().bottom,top:b.getBoundingClientRect().top}}")
    c.check('Lab controls precede canvas in DOM and view',order['before'] and order['bottom']<=order['top']+1,order)
    root.locator('[data-galton-add="10"]').focus();page.keyboard.press('Enter')
    c.check('Lab keyboard adds exactly ten',root.locator('[data-galton-staged]').inner_text()=='10')
    root.locator('[data-galton-action="execute"]').click()
    page.wait_for_function("document.querySelector('[data-galton-root]').__galtonController.snapshot().spawnedCount>0")
    page.evaluate("window.__designLab=document.querySelector('[data-galton-root]').__galtonController")
    before=page.evaluate(SNAPSHOT)
    navigate(page,'dashboard')
    paused=page.evaluate("() => ({same:document.querySelector('[data-galton-root]').__galtonController===__designLab,destroyed:__designLab.destroyed,active:__designLab.active,paused:__designLab.manualPaused,raf:__designLab.raf,snapshot:JSON.stringify(__designLab.snapshot())})")
    c.check('Lab module exit preserves paused simulation',paused['same'] and not paused['destroyed'] and not paused['active'] and paused['paused'] and paused['raf']==0,paused)
    navigate(page,'research-probability-lab')
    c.check('Lab return requires explicit Continue',root.locator('[data-galton-action="pause"]').inner_text()=='Continuar' and page.evaluate('__designLab.manualPaused&&__designLab.raf===0'))
    c.check('Lab return retains balls and results',page.evaluate('JSON.stringify(__designLab.snapshot())')==paused['snapshot'])
    root.locator('[data-galton-action="pause"]').click()
    c.check('Lab Continue resumes same controller',page.evaluate("document.querySelector('[data-galton-root]').__galtonController===__designLab&&!__designLab.manualPaused"))
    root.locator('[data-galton-action="reset"]').click()
    c.check('Lab Reset clears transient simulation',page.evaluate("() => {const s=__designLab.snapshot();return s.activeCount===0&&s.queuedCount===0&&s.settledCount===0&&__designLab.staged===0}"))
    c.check('Lab flow preserves financial state/storage',page.evaluate(SNAPSHOT)==before)
    # Existing finalization lifecycle API, not a claim of manual modal testing.
    page.evaluate('handleGaltonSessionWipe()')
    c.check('Lab finalization lifecycle releases previous instance',page.evaluate('__designLab.destroyed&&__designLab.engine===null&&__designLab.raf===0'))
    c.check('Lab recreated instance works',page.evaluate("() => {const n=document.querySelector('[data-galton-root]').__galtonController;return n!==__designLab&&!n.destroyed}"))
    c.check('Lab never displays Forex context',not page.locator('#gdContextRow').is_visible())


def run(args):
    identity={'root':str(args.root),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.root,text=True).strip(),
              'product_inputs_sha256':{f:hashlib.sha256((args.root/f).read_bytes()).hexdigest() for f in INPUTS},
              'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'baseline_observation':args.baseline,'started_at':time.time(),
              'zoom_limit':'Additional zoom case is CSS zoom 200%, not browser-native zoom or physical device proof.'}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(args.root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    reports=[]
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('JP_WEALTH_CHROMIUM'):opts['executable_path']=os.environ['JP_WEALTH_CHROMIUM']
            browser=pw.chromium.launch(**opts)
            cases=[(width,theme,1) for width in args.widths for theme in args.themes]
            if args.zoom:cases.append((1440,'light',2))
            for width,theme,zoom in cases:
                name=f'{width}-{theme}-zoom{zoom}'
                c=Checks(name);reports.append({'case':name,'assertions':c.items})
                context=browser.new_context(viewport={'width':width,'height':1000},has_touch=True,service_workers='block',reduced_motion='reduce')
                install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
                page=context.new_page();errors=[];console=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
                try:
                    page.goto(f'http://127.0.0.1:{server.server_port}/index.html?galtonDebug=1');wait_bootstrap(page)
                    page.evaluate(SETUP,theme)
                    page.evaluate('window.__designFixture=('+ALLADIN_SEED+')()')
                    page.evaluate("() => {window.__designSaves=0;const original=save;save=function(...a){__designSaves++;return original.apply(this,a)}}")
                    if zoom!=1:page.evaluate('(z)=>document.documentElement.style.zoom=String(z)',zoom)
                    c.check('reduced motion fixture active',page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))
                    for area in args.areas:
                        try:
                            globals()[area](page,c)
                            c.check(area+' no document horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                            if args.screenshots:
                                args.screenshots.mkdir(parents=True,exist_ok=True)
                                page.screenshot(path=str(args.screenshots/f'{name}-{area}.png'),full_page=False)
                        except Exception as exc:
                            c.items.append({'name':area+' interrupted','result':'PRODUCT_FAIL' if isinstance(exc,AssertionError) else 'TEST_HARNESS_FAIL','detail':str(exc)})
                            print(f'FAIL {name} {area}: {exc}',flush=True)
                    c.check('no uncaught page errors',not errors,errors)
                    c.check('no console errors',not console,console)
                    assert_fixture_requests(context)
                except Exception as exc:
                    c.items.append({'name':'setup/environment','result':'ENVIRONMENT_ERROR','detail':str(exc)})
                finally:context.close()
            browser.close()
    finally:server.shutdown()
    summary=Counter(item['result'] for report in reports for item in report['assertions'])
    inputs_after={f:hashlib.sha256((args.root/f).read_bytes()).hexdigest() for f in INPUTS}
    if inputs_after!=identity['product_inputs_sha256']:
        reports.append({'case':'identity','assertions':[{'name':'inputs changed during run','result':'ENVIRONMENT_ERROR','detail':inputs_after}]})
        summary['ENVIRONMENT_ERROR']+=1
    result={**identity,'finished_at':time.time(),'product_inputs_after_sha256':inputs_after,'cases':reports,'summary':dict(summary),
            'result':'PASS' if set(summary)=={'PASS'} else 'NOT_PASS'}
    if args.output:args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'result':result['result'],'summary':result['summary']},ensure_ascii=False),flush=True)
    return 0 if result['result']=='PASS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--baseline',action='store_true')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--screenshots',type=Path)
    parser.add_argument('--widths',type=lambda s:[int(x) for x in s.split(',')],default=[320,390,768,1440])
    parser.add_argument('--themes',type=lambda s:s.split(','),default=['light','dark'])
    parser.add_argument('--areas',type=lambda s:s.split(','),default=list(AREAS))
    parser.add_argument('--zoom',action='store_true')
    options=parser.parse_args()
    if set(options.areas)-set(AREAS):parser.error('unknown area')
    raise SystemExit(run(options))
