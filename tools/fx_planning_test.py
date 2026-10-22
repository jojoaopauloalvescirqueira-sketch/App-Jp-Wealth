#!/usr/bin/env python3
"""Compatibility entrypoint: independent reserve adapter and onboarding checks.

The retired JPWFx planning contract is mapped in the approved planning change.
Current planning engine/state/UI suites have their own gate entries and are not
recounted here. FCR/FEO expectations below remain unchanged.
"""
from http.server import SimpleHTTPRequestHandler
from browser_fixture_server import BrowserFixtureServer as ThreadingHTTPServer
from pathlib import Path
import os, threading
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*_args): pass

def serve():
    os.chdir(ROOT)
    server=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,f'http://127.0.0.1:{server.server_port}/index.html'

def prepare_page(browser,url,suppress_onboarding=True):
    context=browser.new_context(viewport={"width":1440,"height":900},service_workers='block')
    if suppress_onboarding:context.add_init_script('window.__onbShown=true;')
    context.add_init_script("localStorage.setItem('jpw_module_availability_v1',JSON.stringify({schemaVersion:1,modules:{alladin:'active','personal-finance':'active'}}));")
    install_bootstrap(context)
    page=context.new_page();observed={'pageerror':[]}
    page.on('pageerror',lambda error:observed['pageerror'].append(str(error)))
    page.goto(url);wait_bootstrap(page)
    page.wait_for_function("() => window.JPWPlanning && typeof reserveRequirementsCalc === 'function'")
    return context,page,observed

def assert_close(actual,expected,tolerance=1e-9,label='value'):
    assert actual is not None and abs(actual-expected)<=tolerance,(label,actual,expected)

def run_reserve_cases(page):
    # V10 characterization is retained verbatim in campaign evidence. V11 uses
    # explicit nominal capital and a documented six-month amount; no SI or
    # monthly*6 substitution, and quantitative coverage never says Regular.
    for nominal, fcr_current, six_month, feo_current in [
        (10000, 2200, 6000, 6000), (10000, 1800, 7300, 4500),
        (200000, 45000, 21000, 12000),
    ]:
        r = page.evaluate("""x => reserveRequirementsCalc({capitalNominal:x[0],si:9000,
            fcrCurrent:x[1],sixMonthExpenseAmount:x[2],feoCurrent:x[3],
            determinationRecorded:true,expensesApproved:true})""",
            [nominal, fcr_current, six_month, feo_current])
        assert_close(r['fcrReq'], nominal * .22, label='FCR V11 sobre nominal')
        assert_close(r['feoReq'], six_month, label='FEO explicitamente apurado')
        assert_close(r['fcrCoverage'], fcr_current / (nominal * .22) * 100)
        assert_close(r['feoCoverage'], feo_current / six_month * 100)
        assert_close(r['fcrDiff'], fcr_current - nominal * .22)
        assert_close(r['feoDiff'], feo_current - six_month)
        assert r['status'] == 'PENDING_GOVERNANCE'
        assert r['fcrStatus'] == ('Insuficiente' if fcr_current < nominal * .22 else 'Constituído — verificar governança')
        assert r['feoStatus'] == ('Insuficiente' if feo_current < six_month else 'Constituído — verificar governança')
        assert r['hasDeficit'] == (fcr_current < nominal * .22 or feo_current < six_month)
    legacy = page.evaluate("() => reserveRequirementsCalc({capital:10000,monthlyExpenses:1000,fcrCurrent:1500,feoCurrent:6000})")
    assert legacy['fcrReq'] is None and legacy['feoReq'] is None, 'legado não deve autorizar requisito V11'
    assert legacy['fcrStatus'] == legacy['feoStatus'] == 'Pendente'
    for flag in ['determinationRecorded','expensesApproved']:
        r = page.evaluate("flag=>reserveRequirementsCalc({capitalNominal:10000,sixMonthExpenseAmount:6000,determinationRecorded:true,expensesApproved:true,[flag]:false})", flag)
        assert r['feoReq'] is None and r['status'] == 'PENDING_GOVERNANCE'
    absent = page.evaluate("() => reserveRequirementsCalc({})")
    assert absent['fcrReq'] is None and absent['feoReq'] is None
    assert absent['fcrCoverage'] is None and absent['feoCoverage'] is None

def main():
    server,url=serve()
    try:
        with sync_playwright() as pw:
            options={'headless':True}
            if os.environ.get('JP_WEALTH_CHROMIUM'):options['executable_path']=os.environ['JP_WEALTH_CHROMIUM']
            browser=pw.chromium.launch(**options)
            context,page,observed=prepare_page(browser,url)
            run_reserve_cases(page)
            assert not observed['pageerror'],observed['pageerror']
            assert_fixture_requests(context);context.close()
            context,page,observed=prepare_page(browser,url,suppress_onboarding=False)
            page.wait_for_timeout(400)
            assert not observed['pageerror'],observed['pageerror']
            assert_fixture_requests(context);context.close();browser.close()
    finally:server.shutdown()
    print('PASS preserved reserve adapter cases and onboarding smoke; current planning suites counted separately')
if __name__=='__main__':main()
