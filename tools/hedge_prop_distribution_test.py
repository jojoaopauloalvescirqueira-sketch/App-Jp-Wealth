#!/usr/bin/env python3
"""Hedge Prop shipped bytes: HTTP, controlled offline PWA, file and portable.

Uses fresh disposable browser contexts and official generated artifacts. This
test never rebuilds artifacts or substitutes production script/style responses.
"""
import argparse
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import wait_bootstrap
from notes_launcher_test import Quiet, launch_options, instrument, snapshot, unchanged
from hedge_prop_browser_test import ROOT, boot, route, mode, action, blanks, values, ONE, TWO


def shipped(page, label, report):
    route(page);blanks(page)
    instrument(page);before=snapshot(page)
    for stages, expected in [(1,ONE),(2,TWO)]:
        mode(page,stages);action(page,'example').click();values(page,expected)
    assert page.locator('#hedgePropRoot').evaluate('e=>getComputedStyle(e).display')!='none'
    unchanged(page,before,label+' hypothetical simulation')
    page.reload();wait_bootstrap(page);page.evaluate('closeModal()');route(page);blanks(page)
    report['checks'].append({'id':label+'-shipped-oracles-and-ram-reload','classification':'PASS'})


def run(args):
    args.out.mkdir(parents=True,exist_ok=True)
    files=['index.html','src/js/manifest.json','src/styles/app.css','build-id.js','sw.js',
           'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html','tools/hedge_prop_browser_test.py','tools/hedge_prop_distribution_test.py']
    files += [str(path.relative_to(ROOT)) for path in (ROOT/'src/js/40-app/32-prop-firms').glob('*.js')]
    hash_sources=lambda:{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    report={'classification':'PRODUCT_FAIL','checks':[],'headless':True,'source_sha256':hash_sources()}
    with BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server,sync_playwright() as pw:
        threading.Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(**launch_options())
        url=f'http://127.0.0.1:{server.server_port}/index.html'
        try:
            for label,target in [('http',url),('file',(ROOT/'index.html').as_uri()),
                                 ('portable',(ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').as_uri())]:
                context,page,errors=boot(browser,target)
                try:
                    shipped(page,label,report)
                    assert not errors,(label,errors)
                finally:context.close()
            context,page,errors=boot(browser,url,workers='allow')
            try:
                page.wait_for_function('navigator.serviceWorker.controller',timeout=30000)
                page.wait_for_function('''async()=>{
                  const keys=await caches.keys(),key=keys.find(k=>k.startsWith('jp-wealth-'));
                  if(!key)return false;
                  const cache=await caches.open(key);
                  return !!(await cache.match('/index.html'))&&!!(await cache.match('/src/js/40-app/32-prop-firms/01-engine.js'));
                }''',timeout=30000)
                route(page);mode(page,1);action(page,'example').click();values(page,ONE)
                context.set_offline(True);page.reload();wait_bootstrap(page);page.evaluate('closeModal()')
                route(page);blanks(page)
                mode(page,2);action(page,'example').click();values(page,TWO)
                assert page.locator('#hedgePropRoot').is_visible()
                assert not errors,errors
                report['checks'].append({'id':'pwa-controlled-offline-new-scripts-route-oracle-ram-reset','classification':'PASS'})
            finally:context.close()
            report['classification']='PASS'
        except (AssertionError,PlaywrightError) as exc:
            report['failure']=str(exc)
        finally:browser.close()
    report['bytes_stable']=report['source_sha256']==hash_sources()
    if not report['bytes_stable']:
        report['classification']='TEST_HARNESS_FAIL'
        report['failure']='Candidate or test bytes changed during distribution checks; repeat on a frozen candidate'
    (args.out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
    return 0 if report['classification']=='PASS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=ROOT/'docs/validation/hedge-prop-20261027/browser-distribution')
    raise SystemExit(run(parser.parse_args()))
