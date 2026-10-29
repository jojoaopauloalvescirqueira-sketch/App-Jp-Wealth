#!/usr/bin/env python3
"""Management annual HTTP/file/portable/PWA and real backup preservation.
Only disposable Chromium profiles and explicit synthetic confirmed fixtures.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from notes_launcher_test import launch_options
from management_annual_ui_test import Quiet, seed, choose
ROOT=Path(__file__).resolve().parents[1]
NOW=datetime(2026,10,26,15,tzinfo=timezone.utc)

def boot(browser,url,workers='block'):
    context=browser.new_context(viewport={'width':1280,'height':900},service_workers=workers)
    install_bootstrap(context,{'USDBRL':5})
    context.add_init_script('window.__onbShown=true;')
    page=context.new_page();page.clock.set_fixed_time(NOW);errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(url);wait_bootstrap(page);page.evaluate('closeModal()')
    assert page.evaluate('!!window.JPWManagementAnnual?.commands && !!window.JPWManagement'), 'Distributed Management scripts missing'
    assert not errors,errors
    return context,page,errors

def fixture(page):
    scope=seed(page)
    result=page.evaluate('''t=>{
      const api=JPWManagementAnnual,config={...t,year:2026,startDate:'2026-10-01',annualTarget:.25,daysPerWeek:5,monthsPerYear:12,excludedDates:[]};
      let r=api.commands.savePlan(config,{token:api.queries.token(config),confirmOpening:true,reason:'Synthetic distribution plan'});if(!r.ok)throw Error(JSON.stringify(r));
      r=api.commands.recordResult({target:config,date:'2026-10-01',value:0},{token:api.queries.token(config),confirm:true,reason:'Explicit zero synthetic result'});if(!r.ok)throw Error(JSON.stringify(r));
      return {scope:config,aggregate:api.queries.snapshot(),ledger:JPWForex.state.accountLedger(t).value};
    }''',scope)
    assert page.evaluate("JPWNavigation.navigate('management-accounting')")
    choose(page,scope)
    assert page.locator('.mg-sheet .mg-day').count()>0
    assert page.locator('.mg-day[data-mg-date="2026-10-01"]').inner_text().find('Fechado')>=0
    return result

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);checks=[]
    def checked(name,condition):
        assert condition,name
        checks.append({'id':name,'classification':'PASS'});print('PASS '+name,flush=True)
    with BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server,sync_playwright() as pw:
        threading.Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(**launch_options());url=f'http://127.0.0.1:{server.server_port}/index.html'
        try:
            context,page,errors=boot(browser,url)
            checked('fresh-optional-domain-absent',page.evaluate('S.managementAnnual===undefined'))
            expected=fixture(page)
            page.reload();wait_bootstrap(page);page.evaluate('closeModal()')
            checked('HTTP-confirmed-reload',page.evaluate('JPWManagementAnnual.queries.snapshot()')==expected['aggregate'])
            page.evaluate("openSettingsModal('backup')")
            with page.expect_download() as pending:page.locator('#exportFullBackupBtn').click()
            backup=out/'synthetic-management-backup.json';pending.value.save_as(str(backup));payload=json.loads(backup.read_text())
            checked('Backup-Completo-confirmed-aggregate',payload['state']['managementAnnual']==expected['aggregate'])
            checked('Backup-canonical-real-results',len(payload['state']['forex']['accountContexts']['accounts'][expected['scope']['accountId']]['periods'][expected['scope']['periodId']]['ledger'])==1)
            restored,q,restore_errors=boot(browser,url)
            q.evaluate("openSettingsModal('backup');window.confirm=()=>true;window.alert=()=>{}")
            q.locator('#importFullBackupInput').set_input_files(str(backup))
            q.wait_for_function('S.managementAnnual?.plans?.length===1')
            checked('real-import-identities-history-preserved',q.evaluate('JPWManagementAnnual.queries.snapshot()')==expected['aggregate'])
            checked('finalization-preserves-optional-domain',q.evaluate('emptyJPWealthState(sessionPreserveLongitudinal().valor).managementAnnual')==expected['aggregate'])
            checked('future-domain-rejected-no-write',q.evaluate('''()=>{const data=structuredClone(S),before=localStorage.getItem(LSKEY);data.managementAnnual.schemaVersion=999;try{normalizeImportedState(data);return false}catch(_){return localStorage.getItem(LSKEY)===before}}'''))
            checked('old-backup-without-domain-valid',q.evaluate('''()=>{const data=structuredClone(S);delete data.managementAnnual;const n=normalizeImportedState(data);return n.managementAnnual===undefined}'''))
            checked('restore-no-page-errors',not errors and not restore_errors)
            restored.close();context.close()
            for label,path in [('file',ROOT/'index.html'),('portable',ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')]:
                c,p,e=boot(browser,path.as_uri());data=fixture(p)
                checked(label+'-scoped-styles',p.locator('.mg-summary').evaluate('n=>getComputedStyle(n).display')=='grid')
                p.reload();wait_bootstrap(p);p.evaluate('closeModal()')
                checked(label+'-confirmed-reload',p.evaluate('JPWManagementAnnual.queries.snapshot()')==data['aggregate'])
                checked(label+'-no-page-errors',not e);c.close()
            c,p,e=boot(browser,url,workers='allow');p.wait_for_function('navigator.serviceWorker.controller',timeout=30000)
            p.wait_for_function("caches.keys().then(async keys=>(await caches.open(keys.find(k=>k.startsWith('jp-wealth-')))).match('/src/js/30-accounting/07-management/03-ui.js').then(Boolean))",timeout=30000)
            expected=fixture(p);c.set_offline(True);p.reload();p.wait_for_function('window.JPWManagementAnnual?.queries')
            checked('PWA-offline-aggregate-preserved',p.evaluate('JPWManagementAnnual.queries.snapshot()')==expected['aggregate'])
            checked('PWA-offline-route',p.evaluate("JPWNavigation.navigate('management-accounting')"))
            choose(p,expected['scope']);checked('PWA-offline-table',p.locator('.mg-day').count()>0)
            checked('PWA-offline-no-page-errors',not e);c.close()
        finally:browser.close()
    (out/'results.json').write_text(json.dumps({'classification':'PASS','checks':checks,'fixture':'synthetic-only; actual Storage/FileReader/download/SW'},ensure_ascii=False,indent=2)+'\n')
    return 0
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('/private/tmp/jpw-portfolio-management-20261026/distribution'))
    raise SystemExit(run(parser.parse_args().out))
