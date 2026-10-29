#!/usr/bin/env python3
"""Hedge Prop: synthetic real-browser integration; headless, no user profiles."""
import argparse
from functools import partial
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import tempfile
import threading
import traceback
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from notes_launcher_test import Quiet, launch_options, settle, instrument, snapshot, unchanged

ROOT = Path(__file__).resolve().parents[1]


def boot(browser, url, workers='block', viewport=None):
    context = browser.new_context(viewport=viewport or {'width': 1280, 'height': 900},
                                  service_workers=workers, reduced_motion='reduce', has_touch=True)
    install_bootstrap(context, {'USDBRL': 5})
    context.add_init_script('window.__onbShown=true')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(url)
    wait_bootstrap(page)
    page.evaluate('closeModal()')
    page.evaluate('async()=>{await JPWMarket.usdBrl.refresh(false)}')
    return context, page, errors


def route(page):
    assert page.evaluate("JPWNavigation.navigate('tools-prop-firms')"), 'Hedge route is absent or refuses independent access'
    assert page.locator('#hedgePropRoot').is_visible(), 'Hedge route has no visible independent host'


def field(page, name):
    return page.locator('[data-hedge-field="' + name + '"]')


def action(page, name):
    return page.locator('[data-hedge-action="' + name + '"]')


def money(text):
    number = re.search(r'\d+(?:\.\d{3})*(?:,\d+)?', text)
    assert number, ('missing numeric money', text)
    sign = -1 if any(mark in text[:number.start()] for mark in ('-', '\N{MINUS SIGN}')) else 1
    return sign * float(number.group().replace('.', '').replace(',', '.'))


def values(page, expected):
    for name, value in expected.items():
        actual = money(page.locator('[data-hedge-value="' + name + '"]').inner_text())
        assert math.isclose(actual, value, abs_tol=.011), (name, actual, value)


ONE = {'hedgeCapitalUSD': 2920.20, 'capitalIncludingFeeUSD': 4120.20, 'fundedTargetUSD': 2896.55, 'multipleIncludingFee':3.43}
TWO = {'hedgeCapitalUSD': 3793.55, 'capitalIncludingFeeUSD': 4993.55, 'fundedTargetUSD': 3870.97, 'multipleIncludingFee':4.16}


def blanks(page):
    inputs = page.locator('#hedgePropRoot input[data-hedge-field]')
    assert inputs.count() >= 7, 'Required parameters absent'
    assert inputs.evaluate_all('ns=>ns.every(n=>n.value==="")'), 'No example or cost may be silently prefilled'


def mode(page, value):
    page.locator('[data-hedge-mode="' + str(value) + '"]').click()


def costs(page, stages):
    if page.locator('#hedgePropCosts').get_attribute('open') is None:
        page.locator('#hedgePropCosts summary').click()
    assert page.locator('#hedgePropCosts').get_attribute('open') is not None
    for i in range(stages + 1):
        for outcome in ['passUSD', 'failUSD']:
            field(page, f'costs.{i}.{outcome}').fill('0')


def rounding(page, report):
    mode(page,1);action(page,'example').click();costs(page,1)
    field(page,'costs.0.failUSD').fill('0,005')
    actual=page.locator('[data-hedge-cost-path="failure-1"]').inner_text()
    assert actual=='−US$ 0,01', ('Half-cent deficit must keep negative sign after rounding',actual)
    report['checks'].append('half-cent-negative-cost-displays-signed-deficit')
    action(page,'clear').click()
    page.locator('#hedgePropCosts').evaluate('n=>n.open=false')


def lifecycle(page, report):
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    page.evaluate('''()=>{JPWPropFirms.disposeForSession();Object.defineProperty(document,'hidden',{configurable:true,get:()=>true})}''')
    try:
        assert page.evaluate("JPWNavigation.navigate('tools-prop-firms')")
        page.evaluate('JPWPropFirms.disposeForSession()')
        assert page.locator('#hedgePropRoot').count()==0
        page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
        settle(page)
        assert page.locator('#hedgePropRoot').count()==0, 'A visibility observer resurrected disposed simulation after a hidden accepted entry'
    finally:
        page.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))")
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    route(page);blanks(page)
    report['checks'].append('hidden-entry-disposal-visibility-no-resurrection-new-accepted-entry')


def journeys(page, report):
    blanks(page)
    assert page.locator('#hedgePropStatus').inner_text().strip()
    assert page.locator('[data-hedge-value="capitalIncludingFeeUSD"]').inner_text().strip()=='—'
    # Navigate via the actual Tools submenu, including the preceding/succeeding
    # menu entries; no injected click handlers or replacement route registry.
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    page.locator('#toolsNavTrigger').click()
    page.locator('[data-nav-child="tools-prop-firms"]').click()
    assert page.locator('#hedgePropRoot').is_visible()
    ordered=page.locator('#toolsNavSubmenu [data-nav-child]').evaluate_all('ns=>ns.map(n=>n.dataset.navChild)')
    assert ordered.index('tools-prop-firms') < ordered.index('tools-minigames'), ordered
    assert page.evaluate("JPWModuleAvailability.setState('forex','frozen').ok")
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    route(page)
    report['checks'].append('real-tools-menu-order-and-independent-frozen-forex')
    # The real shell may have its own reads. Only the independent tool's edit
    # interval is instrumented; synthetic financial state is compared in full.
    instrument(page)
    before = snapshot(page)
    requests = []
    page.on('request', lambda request: requests.append(request.url))
    mode(page, 1)
    action(page, 'example').focus();page.keyboard.press('Enter')
    assert action(page,'example').evaluate('e=>e===document.activeElement'), 'Keyboard example lost focus'
    values(page, ONE)
    assert field(page, 'nominalUSD').input_value() == '200000'
    assert 'pend' in page.locator('[data-hedge-cost-path="funded-success"]').text_content().lower()
    costs(page, 1)
    assert abs(money(page.locator('[data-hedge-cost-path="funded-success"]').inner_text())) < .011
    # Costs by mutually exclusive path: pass cost is never charged on failure
    # at the same stage, and future stage costs are not charged retroactively.
    field(page, 'costs.0.passUSD').fill('11')
    field(page, 'costs.0.failUSD').fill('17')
    field(page, 'costs.1.passUSD').fill('23')
    field(page, 'costs.1.failUSD').fill('29')
    values(page, ONE)
    for path, expected in [('failure-1', -17), ('funded-success', -34), ('funded-stop', -40)]:
        actual = money(page.locator(f'[data-hedge-cost-path="{path}"]').inner_text())
        assert abs(actual - expected) < .011, (path, actual, expected)
    field(page, 'costs.1.passUSD').fill('')
    assert 'pend' in page.locator('[data-hedge-cost-path="funded-success"]').inner_text().lower()
    assert abs(money(page.locator('[data-hedge-cost-path="failure-1"]').inner_text()) + 17) < .011
    report['checks'].append('one-stage-oracle-costs-exclusive-paths-missing-vs-zero')
    # Typing changes the existing node, including cursor position, never a full
    # render replacing the active input. Text input supports pt-BR decimals.
    fee = field(page, 'feeUSD')
    fee.fill('1200');fee.focus()
    handle = fee.element_handle()
    if fee.get_attribute('type') != 'number':
        fee.evaluate('e=>e.setSelectionRange(2,2)')
        fee.press('0')
        assert fee.evaluate('e=>e.selectionStart') == 3, 'Edit reset the cursor'
    else:
        fee.press('ArrowLeft');fee.press('0')
    assert handle.evaluate('e=>e.isConnected && document.activeElement===e'), 'Calculation replaced focused input'
    fee.fill('1200')
    mode(page, 2);blanks(page)
    action(page, 'example').click();values(page, TWO)
    costs(page,2)
    for i,(passed,failed) in enumerate([(11,17),(23,29),(31,37)]):
        field(page,f'costs.{i}.passUSD').fill(str(passed))
        field(page,f'costs.{i}.failUSD').fill(str(failed))
    for path,expected in [('failure-1',-17),('failure-2',-40),('funded-success',-65),('funded-stop',-71)]:
        actual=money(page.locator(f'[data-hedge-cost-path="{path}"]').inner_text())
        assert abs(actual-expected)<.011,(path,actual,expected)
    values(page,TWO)
    report['checks'].append('two-stage-costs-each-exclusive-path-independent-ideal-oracle')
    mode(page, 1);values(page, ONE)
    assert field(page, 'costs.0.passUSD').input_value() == '11', 'Mode change lost independent draft'
    mode(page, 2);values(page, TWO)
    action(page, 'clear').click();blanks(page)
    mode(page, 1);values(page, ONE)
    report['checks'].append('input-node-focus-cursor-independent-modes-clear')
    # Missing, zero and invalid values have different financial meanings.
    for name, bad in [('nominalUSD', '0'), ('feeUSD', '-1'), ('payoutPercent', '0'),
                      ('payoutPercent', '101'), ('drawdownPercent', '0'), ('refundUSD', '1201')]:
        action(page, 'example').click();field(page, name).fill(bad)
        status = page.locator('#hedgePropStatus').inner_text().lower()
        assert field(page,name).get_attribute('aria-invalid')=='true', (name,bad,status)
        assert not page.locator('[data-hedge-value="capitalIncludingFeeUSD"]').inner_text().strip().startswith('US$'), 'Invalid input still advertises a budget'
    action(page, 'example').click();field(page, 'refundUSD').fill('0')
    assert 'invál' not in page.locator('#hedgePropStatus').inner_text().lower()
    field(page, 'feeUSD').fill('0');field(page, 'refundUSD').fill('0')
    values(page, {'hedgeCapitalUSD': 0, 'capitalIncludingFeeUSD': 0, 'fundedTargetUSD': 0})
    field(page, 'feeUSD').fill('')
    assert page.locator('[data-hedge-value="capitalIncludingFeeUSD"]').inner_text().strip()=='—'
    action(page, 'example').click()
    page.locator('#hedgePropHelp summary').focus();page.keyboard.press('Enter')
    assert page.locator('#hedgePropHelp').get_attribute('open') is not None
    allowed={'https://ftmo.com/en/forbidden-trading-practices/','https://www.thetradingpit.com/general-terms-and-conditions',
             'https://ftmo.com/en/faq/is-the-entry-fee-refunded/','https://cortextradings.com/hedge-prop-firm/'}
    external=set()
    for link in page.locator('#hedgePropRoot a').all():
        href=link.get_attribute('href')
        if href.startswith('#'):
            assert href in ('#hedgePropHelp','#hedgePropSources')
        else:
            external.add(href)
            assert href in allowed,('Unapproved external source',href)
            assert 'noopener' in (link.get_attribute('rel') or '')
    assert external==allowed
    assert not requests, ('Hedge requested network', requests)
    unchanged(page, before, 'Hedge inputs, modes, details, costs and reset')
    report['checks'].append('invalid-missing-zero-links-only-no-state-storage-network-writes')
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    route(page);values(page, ONE)
    page.evaluate('JPWPropFirms.disposeForSession()')
    assert page.evaluate("JPWNavigation.navigate('dashboard')")
    route(page);blanks(page)
    page.reload();wait_bootstrap(page);page.evaluate('closeModal()');route(page);blanks(page)
    report['checks'].append('navigation-ram-only-session-disposal-reload')


def geometry(page):
    # Reuse the official measurement implementation, including inner text/SVG.
    # Runtime import avoids the root visual suite's optional import of this module.
    from ui_visual_quality_test import centered
    data = page.locator('#hedgePropRoot').evaluate('''root=>{
      const visible=n=>!!n.getClientRects().length&&!n.closest('[hidden],[inert]');
      const controls=Array.from(root.querySelectorAll('button,input,summary,.hp-section-head>a')).filter(visible);
      const rect=n=>{const r=n.getBoundingClientRect(),p=n.closest('.hp-field')?.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,tag:n.tagName,field:n.dataset.hedgeField||null,fieldTop:p?.top,fieldBottom:p?.bottom}};
      return {viewport:innerWidth,root:rect(root),overflow:document.documentElement.scrollWidth>innerWidth,
        controls:controls.map(rect),bad:controls.filter(n=>{const r=n.getBoundingClientRect();return r.width<44||r.height<44||r.right>innerWidth+.25||r.x<-.25}).map(rect)};
    }''')
    assert not data['overflow'], ('horizontal document overflow', data)
    assert not data['bad'], ('44px target or viewport containment', data['bad'])
    for button in page.locator('#hedgePropRoot button:visible').all():
        centered(button)
    # Inputs in each shared visual row align at the same baseline within2px.
    grouped = {}
    for control in data['controls']:
        if control['tag'] == 'INPUT':
            assert control['y']>=control['fieldTop']-.25 and control['bottom']<=control['fieldBottom']+.25,('input escaped semantic field',control)
            row = next((k for k in grouped if abs(k-control['fieldTop']) <= 2), control['fieldTop'])
            grouped.setdefault(row, []).append(control)
    for row in grouped.values():
        assert max(n['y'] for n in row)-min(n['y'] for n in row) <= 2, ('input row baseline exceeds2CSSpx', row)
    return data


def visual_matrix(page, report, out):
    route(page);mode(page, 2);action(page, 'example').click()
    matrix = []
    for layout in ['sidebar', 'topbar', 'submenu', 'glass']:
        for theme in ['light', 'dark']:
            page.evaluate('v=>{mountNavigationLayout(v.layout);document.documentElement.dataset.theme=v.theme;document.body.dataset.theme=v.theme}', {'layout':layout,'theme':theme})
            for width, height in [(320,700),(390,844),(700,600),(701,601),(1099,720),(1100,719),(1100,720),(1101,721),(1440,1000),(1440,480)]:
                report['current_matrix_case']={'layout':layout,'theme':theme,'width':width,'height':height}
                page.set_viewport_size({'width':width,'height':height});settle(page)
                geometry(page)
                page.locator('#hedgePropRoot details').evaluate_all('ns=>ns.forEach(n=>n.open=true)')
                geometry(page)
                field(page,'feeUSD').fill('-1');geometry(page)
                field(page,'feeUSD').fill('1200')
                page.locator('#hedgePropRoot details').evaluate_all('ns=>ns.forEach(n=>n.open=false)')
                matrix.append({'layout':layout,'theme':theme,'width':width,'height':height,'classification':'PASS'})
                if layout == 'sidebar' and width in (390,1440) and height > 600:
                    page.screenshot(path=str(out/f'{layout}-{theme}-{width}.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate("mountNavigationLayout('sidebar')")
    action(page,'clear').tap();blanks(page)
    action(page,'example').tap();values(page,TWO)
    report['checks'].append('touch-explicit-clear-and-example')
    report['matrix'] = matrix
    report['native_zoom'] = {'classification':'NOT_RUN','reason':'Requires user coordination for headful Chromium; CSS scale is not native zoom'}
    report['checks'].append('four-layouts-two-themes-ten-sizes-reduced-motion-44px-centering-overflow')


def native_zoom(pw, url, report, out):
    """Opt-in coordinated headful check; Chromium native preference, never CSS."""
    profile=Path(tempfile.mkdtemp(prefix='hedge-native200-',dir=out))
    (profile/'Default').mkdir()
    (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    options=launch_options()
    options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
    try:
        context=pw.chromium.launch_persistent_context(str(profile),**options)
        try:
            install_bootstrap(context,{'USDBRL':5});context.add_init_script('window.__onbShown=true')
            page=context.pages[0] if context.pages else context.new_page()
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(url);wait_bootstrap(page);page.evaluate('closeModal()');route(page)
            zoom=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom,dpr:devicePixelRatio})')
            assert abs(zoom['outer']/zoom['inner']-2)<.01 and zoom['css']=='1',('Native200% required; CSS scaling forbidden',zoom)
            cases=[]
            for layout in ['sidebar','topbar','submenu','glass']:
                for theme in ['light','dark']:
                    page.evaluate('v=>{mountNavigationLayout(v.layout);document.documentElement.dataset.theme=v.theme;document.body.dataset.theme=v.theme}',{'layout':layout,'theme':theme})
                    mode(page,2);action(page,'example').click();settle(page);geometry(page)
                    page.locator('#hedgePropRoot details').evaluate_all('ns=>ns.forEach(n=>n.open=true)');geometry(page)
                    field(page,'feeUSD').fill('-1');geometry(page);field(page,'feeUSD').fill('1200')
                    page.locator('#hedgePropRoot details').evaluate_all('ns=>ns.forEach(n=>n.open=false)')
                    values(page,TWO)
                    cases.append({'layout':layout,'theme':theme,'classification':'PASS','zoom':zoom})
                    if layout=='sidebar':page.screenshot(path=str(out/f'native200-{theme}.png'),full_page=True)
            assert not errors,errors
            report['native_zoom']={'classification':'PASS','cases':cases,'measurement':zoom}
        finally:context.close()
    finally:shutil.rmtree(profile)


def counterproofs(page, report):
    page.set_viewport_size({'width':1280,'height':900});settle(page)
    # Each mutation lives in a disposable browser page; reload restores the
    # product. Same positive assertions must reject representative defects.
    def rejected(label, mutation, assertion):
        page.reload();wait_bootstrap(page);page.evaluate('closeModal()');route(page);mode(page,1);action(page,'example').click()
        assertion()
        page.evaluate(mutation)
        try:
            assertion()
        except AssertionError:
            report.setdefault('counterproofs',[]).append({'id':label,'classification':'PASS','mutation_rejected':True})
            return
        raise AssertionError('Counterproof accepted defect: '+label)
    rejected('fee-omitted-from-capital', '''()=>{document.querySelector('[data-hedge-value="capitalIncludingFeeUSD"]').textContent='US$ 2.920,20'}''', lambda:values(page,ONE))
    rejected('horizontal-overflow', '''()=>{document.querySelector('#hedgePropRoot').style.minWidth='2500px'}''', lambda:geometry(page))
    rejected('inner-button-content-offset', '''()=>{const b=document.querySelector('[data-hedge-action="example"]');b.style.paddingLeft='35px';b.style.paddingRight='1px'}''', lambda:geometry(page))
    rejected('input-24px-displacement', '''()=>{document.querySelector('[data-hedge-field="nominalUSD"]').style.transform='translateY(24px)'}''', lambda:geometry(page))
    rejected('cost-input-24px-displacement', '''()=>{document.querySelector('#hedgePropCosts').open=true;document.querySelector('[data-hedge-field="costs.0.passUSD"]').style.transform='translateY(24px)'}''', lambda:geometry(page))


def guards(browser, url, report):
    from fx_consolidated_storage_test import SEED
    context,page,errors=boot(browser,url)
    try:
        page.evaluate(SEED)
        page.evaluate('''()=>{const r=JPWForex.state.recordAccountPeriod({accountId:'fx_A',startedAt:'2026-01-01',currency:'USD',si:10000,openingBook:10000,source:'Synthetic Hedge guard fixture',activateCurrentPeriod:true},{reason:'Synthetic Hedge guard fixture'});if(!r.ok)throw Error(r.error);JPWNavigation.navigate('management-reserves')}''')
        page.locator('#fxreserves [data-mg-account]').select_option('fx_A')
        period=page.evaluate('S.forex.accountContexts.accounts.fx_A.currentPeriodId')
        page.locator('#fxreserves [data-mg-period]').select_option(period)
        form=page.locator('#fxReserveFacts');form.evaluate("f=>f.closest('details').open=true")
        form.locator('[name=fcrConstituted]').fill('123');form.locator('[name=reason]').fill('Synthetic Hedge blocked transition')
        assert page.evaluate("JPWNavigation.navigate('tools-prop-firms')") is False, 'Hedge bypassed pending-work guard'
        page.locator('dialog.mg-dialog[open] [data-mg-action=guard-stay]').click()
        assert page.evaluate('JPWNavigation.current().canonical')=='management-reserves'
        assert form.locator('[name=fcrConstituted]').input_value()=='123'
        assert page.evaluate("JPWNavigation.navigate('tools-prop-firms')") is False
        page.locator('dialog.mg-dialog[open] [data-mg-action=guard-preserve]').click()
        assert page.locator('#hedgePropRoot').is_visible()
        assert not errors, errors
        report['checks'].append('pending-reserve-draft-stay-preserve-through-real-navigation-guard')
    finally:
        context.close()


def run(args):
    args.out.mkdir(parents=True, exist_ok=True)
    source_files = ['index.html','src/styles/app.css','src/js/40-app/01-navigation.js','src/js/40-app/07-finalize-session.js','src/js/20-ui/31-tools-services.js','src/js/manifest.json','tools/ui_visual_quality_test.py']
    source_files += [str(path.relative_to(ROOT)) for path in (ROOT/'src/js/40-app/32-prop-firms').glob('*.js')]
    hash_sources=lambda:{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in source_files}
    test_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result = {'classification': 'PRODUCT_FAIL', 'checks': [], 'headless': not args.native_zoom,
              'source_sha256':hash_sources(),'test_sha256':test_hash}
    with BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT))) as server, sync_playwright() as pw:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        browser = pw.chromium.launch(**launch_options())
        try:
            context, page, errors = boot(browser, f'http://127.0.0.1:{server.server_port}/index.html')
            route(page)
            result['checks'].append('independent-route')
            if not args.smoke:
                lifecycle(page,result)
                if not args.lifecycle_only:rounding(page,result)
            if not args.smoke and not args.rounding_only and not args.lifecycle_only:
                journeys(page, result)
                visual_matrix(page, result, args.out)
                counterproofs(page, result)
                guards(browser, f'http://127.0.0.1:{server.server_port}/index.html', result)
                if args.native_zoom:
                    native_zoom(pw,f'http://127.0.0.1:{server.server_port}/index.html',result,args.out)
            assert not errors, errors
            result['classification'] = 'PASS'
            context.close()
        except (AssertionError, PlaywrightError) as exc:
            result['failure'] = str(exc)
            result['traceback'] = traceback.format_exc()
        finally:
            browser.close()
    result['bytes_stable']=result['source_sha256']==hash_sources() and test_hash==hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if not result['bytes_stable']:
        result['classification']='TEST_HARNESS_FAIL'
        result['failure']='Candidate or test bytes changed while assertions were executing; repeat on a frozen candidate'
    (args.out / 'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['classification'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'docs/validation/hedge-prop-20261027/browser')
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--rounding-only', action='store_true')
    parser.add_argument('--lifecycle-only',action='store_true')
    parser.add_argument('--native-zoom',action='store_true',help='Coordinated headful Chromium native200%; do not invoke during uncoordinated operator work')
    raise SystemExit(run(parser.parse_args()))
