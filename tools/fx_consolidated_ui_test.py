#!/usr/bin/env python3
"""Consolidado: real DOM navigation/import fixtures; assertions determine exit code."""
import argparse, hashlib, json, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
import notes_launcher_test as launcher
from fx_consolidated_pdf_test import synthetic_pdf

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output'); args=parser.parse_args()
    results=[];observations={}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(**launcher.launch_options())
            context=browser.new_context(service_workers='block',viewport={'width':1440,'height':1000})
            context.add_init_script('window.__onbShown=true;')
            install_bootstrap(context); page=context.new_page()
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html'); wait_bootstrap(page)
            page.evaluate("""() => {window.__onbShown=true;closeModal();S.onboarding.done=true;
              S.accounts=[{forexAccountId:'fixture-A',nome:'Conta Mestre sintética',tipo:'MESTRE',broker:'Demo Broker',platform:'MT5',platformLogin:'10001',currency:'USD',sini:1000,satu:1000},
              {forexAccountId:'fixture-B',nome:'Conta B sintética',tipo:'PRÓPRIA',broker:'Demo Broker',platform:'MT5',platformLogin:'10002',currency:'USD',sini:2000,satu:2000}];
              S.forex.activeAccountId='fixture-B';S.fxConsolidated=JPWFXConsolidated.emptyState();
              S.operationHistory={schemaVersion:DEFAULTS.operationHistory.schemaVersion,records:[{operationId:'manual-A',accountId:'fixture-A',periodId:'period-A',currency:'USD',netResult:25,openedAt:'2026-01-01T10:00:00Z',closedAt:'2026-01-02T10:00:00Z',ordersSnapshot:[]}]};
              S.forex.accounts={'fixture-A':{currency:'USD'},'fixture-B':{currency:'USD'}};migrate();window.__fxBefore=JSON.stringify(S);navNavigate('forex-consolidated');} """)
            def test(name, fn):
                try: fn(); results.append({'name':name,'pass':True})
                except Exception as error: results.append({'name':name,'pass':False,'error':str(error)})
            def require(value):
                assert value
            test('Consolidado is the first Forex destination',lambda:require(page.evaluate("NAV_FOREX_CHILDREN.map(x=>x.id).join(',')==='forex-consolidated,forex-planning,forex-operation,forex-reconciliation,forex-account,forex-reserves'")))
            test('default resolves Mestre without operational switch or writes',lambda:require(page.evaluate("document.querySelector('#fxcAccount').value==='fixture-A' && S.forex.activeAccountId==='fixture-B' && JSON.stringify(S)===window.__fxBefore")))
            test('four accessible tabs',lambda:require(page.locator('#fxconsolidated [role=tab]').count()==4))
            page.locator('#fxcManual').click()
            test('manual source has captured result and no storage writes',lambda:require(page.evaluate("document.querySelector('#fxconsolidated').textContent.includes('25') && JSON.stringify(S)===window.__fxBefore")))
            for tab in ['history','statistics','risks','account']:
                page.locator(f'#fxcTab-{tab}').click()
                test('tab '+tab,lambda tab=tab:require(page.locator(f'#fxcPanel-{tab}').is_visible()))
            page.locator('#fxcTab-account').focus();page.keyboard.press('ArrowRight')
            test('keyboard moves tab and focus',lambda:require(page.locator('#fxcTab-history').evaluate("el=>el===document.activeElement&&el.getAttribute('aria-selected')==='true'")))
            for _ in range(3):
                page.evaluate("navNavigate('dashboard');navNavigate('forex-consolidated')")
            test('repeat navigation keeps one UI and state',lambda:require(page.locator('#fxcAccount').count()==1 and page.evaluate("JSON.stringify(S)===window.__fxBefore")))
            for width,theme in [(1440,'light'),(390,'light'),(1440,'dark'),(390,'dark')]:
                page.set_viewport_size({'width':width,'height':1000});page.evaluate('(t)=>document.documentElement.dataset.theme=t',theme)
                test(f'contained at {width} {theme}',lambda:require(page.locator('#fxconsolidated').evaluate('el=>el.scrollWidth<=el.clientWidth+2')))
            page.set_viewport_size({'width':1440,'height':1000});page.evaluate("document.documentElement.dataset.theme='light'")
            page.evaluate("""() => {S.accounts[0].platformLogin='900001';S.accounts[0].broker='Synthetic Broker';S.accounts[0].server='Synthetic-Demo';
              if(save()!==true)throw Error('Seed save refused');sessionEpochCurrent();markSessionCheckpoint();
              window.__fxRaw=localStorage.getItem(LSKEY);window.__fxOp=JSON.stringify(S.forex);JPWFXConsolidated.reset();navNavigate('forex-consolidated');}""")
            page.locator('#fxcOpenImport').click()
            page.locator('#fxcFile').set_input_files(str(ROOT/'tools/fixtures/mt5-consolidated/classic-en.html'))
            page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
            test('HTML upload previews without writing',lambda:require(page.evaluate("localStorage.getItem(LSKEY)===__fxRaw&&S.fxConsolidated.receipts.length===0&&document.querySelector('#fxcPreview').textContent.includes('900001')")))
            page.locator('#fxcConfirmImport').click()
            test('identity checkbox required',lambda:require(page.evaluate("S.fxConsolidated.receipts.length===0&&document.querySelector('#fxcStatus').textContent.includes('Confirme')")))
            page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click()
            page.wait_for_function("S.fxConsolidated.receipts.length===1")
            test('confirmed HTML writes once without changing operational Forex',lambda:require(page.evaluate("S.fxConsolidated.accounts[0].deals.length===8&&JSON.stringify(S.forex)===__fxOp&&document.querySelector('#fxcImport').hidden")))
            test('ledger projection displayed with provenance',lambda:require(page.evaluate("document.querySelector('#fxcCoverage').textContent.includes('Última importação:')&&document.querySelector('#fxcPanel-account').textContent.includes('85')&&document.querySelector('#fxcIdentity .fxc-chart svg')!==null")))
            if args.output:
                shots=Path(args.output).parent
                page.screenshot(path=str(shots/'consolidated-account-light.png'),full_page=True)
                page.locator('#fxcTab-statistics').click();page.screenshot(path=str(shots/'consolidated-statistics-light.png'),full_page=True)
                page.locator('#fxcTab-account').click()
                page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(shots/'consolidated-account-mobile.png'),full_page=True)
                page.set_viewport_size({'width':1440,'height':1000});page.evaluate("document.documentElement.dataset.theme='dark'");page.screenshot(path=str(shots/'consolidated-account-dark.png'),full_page=True)
                page.evaluate("document.documentElement.dataset.theme='light'")
            page.evaluate('window.__fxRaw=localStorage.getItem(LSKEY)')
            page.locator('#fxcOpenImport').click();page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
            page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click()
            page.wait_for_function("document.querySelector('#fxcImport').hidden")
            test('repeat via UI does not write or duplicate',lambda:require(page.evaluate("S.fxConsolidated.receipts.length===1&&localStorage.getItem(LSKEY)===__fxRaw")))
            page.locator('#fxcOpenImport').click()
            page.locator('#fxcFile').set_input_files(str(ROOT/'tools/fixtures/mt5-consolidated/classic-pt.html'));page.locator('#fxcAnalyze').click()
            page.wait_for_function("!document.querySelector('#fxcAnalyze').disabled")
            test('wrong report account has no confirmation control',lambda:require(page.locator('#fxcConfirmImport').count()==0 and page.evaluate('localStorage.getItem(LSKEY)===__fxRaw')))
            page.locator('#fxcCancelImport').click()
            test('cancel returns focus to import trigger',lambda:require(page.locator('#fxcOpenImport').evaluate('el=>el===document.activeElement')))
            page.locator('#fxcPreferences').click();page.locator('#fxcDefaultAccount').wait_for(state='visible')
            page.locator('#fxcDefaultAccount').select_option('fixture-B');page.locator('#fxcSaveDefault').click()
            page.wait_for_function("S.fxConsolidated.defaultAccountId==='fixture-B'")
            test('Settings explicit preference save',lambda:require(page.locator('#fxcDefaultStatus').inner_text()=='Preferência salva.'))
            page.evaluate('window.__fxAfter=localStorage.getItem(LSKEY)');saved=page.evaluate('window.__fxAfter')
            page.reload();wait_bootstrap(page);page.evaluate("navNavigate('forex-consolidated')")
            test('reload preserves preference and stored import',lambda:require(page.evaluate("document.querySelector('#fxcAccount').value==='fixture-B'&&S.fxConsolidated.accounts[0].deals.length===8")))
            after_reload=page.evaluate('localStorage.getItem(LSKEY)')
            def differences(a,b,path=''):
                if isinstance(a,dict) and isinstance(b,dict):
                    return sum((differences(a.get(k),b.get(k),path+'/'+k) for k in set(a)|set(b)),[])
                return [] if a==b else [path]
            observations['reload_changed_paths']=differences(json.loads(saved),json.loads(after_reload))
            observations['consolidated_unchanged_on_reload']=json.loads(saved).get('fxConsolidated')==json.loads(after_reload).get('fxConsolidated')
            # Boot refreshes the existing instrument fixture; require the exact
            # analytical preference, histories and account facts to survive it.
            # Raw document differences remain in observations, not hidden.
            test('reload preserves exact preference, histories and accounts',lambda:require(all(json.loads(saved).get(k)==json.loads(after_reload).get(k) for k in ['fxConsolidated','operationHistory','accounts'])))
            page.locator('#fxcAccount').select_option('fixture-A');page.locator('#fxcTab-history').click()
            test('orders inventory separate from deals',lambda:require(page.locator('#fxcPanel-history').inner_text().find('Ordens registradas')>=0))
            page.evaluate("S.operationHistory.records.push({operationId:'unassigned-synthetic',currency:'USD',netResult:12345});JPWFXConsolidated.render()")
            page.locator('#fxcManual').click();page.locator('#fxcAccount').select_option('unassigned')
            test('unassigned history visible without financial totals',lambda:require(page.locator('#fxcPanel-history').inner_text().find('unassigned-synthetic')>=0 and page.evaluate("JPWFXConsolidated.project(S.fxConsolidated,S.operationHistory.records,{source:'manual',accountId:'unassigned'}).metrics.netProfit.value===null")))
            page.evaluate("S.operationHistory.records=[{operationId:'historic-BRL-1',accountId:'fixture-A',currency:'BRL',netResult:25,closedAt:'2026-01-01T10:00:00Z'},{operationId:'historic-BRL-2',accountId:'fixture-A',currency:'BRL',netResult:75,closedAt:'2026-01-02T10:00:00Z'}];JPWFXConsolidated.render()")
            page.locator('#fxcAccount').select_option('fixture-A');page.locator('#fxcTab-account').click()
            test('historical currency never comes from current account',lambda:require(page.evaluate("document.querySelector('#fxcPanel-account .fxc-months').textContent.includes('100 BRL')&&document.querySelector('#fxcPanel-account .fxc-chart').textContent.includes('100 BRL')&&document.querySelector('#fxcBars').textContent.includes('100 BRL')")))
            page.locator('#fxcMt5').click();page.locator('#fxcAccount').select_option('fixture-A');page.locator('#fxcTab-history').click()
            page.evaluate("S.fxConsolidated.accounts[0].deals.find(r=>r.ticket==='102').commission=null;S.fxConsolidated.accounts[0].deals.find(r=>r.ticket==='102').netResult=null;JPWFXConsolidated.render()")
            row=page.locator('#fxcPanel-history tbody tr').filter(has=page.locator('td:nth-child(2)',has_text='102')).first
            test('unknown net result never falls back to gross profit',lambda:require(row.locator('td').nth(4).inner_text()=='—'))
            page.evaluate("S.accounts.push({forexAccountId:'fixture-PDF',nome:'Conta PDF sintética',tipo:'PRÓPRIA',platformLogin:'900004',platform:'MetaTrader 5',broker:'Synthetic Broker Ltd.',sini:1000,satu:1030});S.forex.accounts['fixture-PDF']={currency:'USD'};migrate();save();markSessionCheckpoint();JPWFXConsolidated.render()")
            page.locator('#fxcAccount').select_option('fixture-PDF');page.locator('#fxcOpenImport').click()
            page.locator('#fxcFile').set_input_files({'name':'summary-synthetic.pdf','mimeType':'application/pdf','buffer':synthetic_pdf(login='900004')})
            page.locator('#fxcImportFrom').fill('2026-01-01');page.locator('#fxcImportTo').fill('2026-01-31');page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
            test('PDF preview has no artificial transactions',lambda:require(page.evaluate("S.fxConsolidated.accounts.every(a=>a.id!=='fixture-PDF')&&document.querySelector('#fxcPreview').textContent.includes('900004')")))
            page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click();page.wait_for_function("S.fxConsolidated.accounts.some(a=>a.id==='fixture-PDF')")
            test('PDF confirms summary with no deals',lambda:require(page.evaluate("S.fxConsolidated.accounts.find(a=>a.id==='fixture-PDF').deals.length===0&&S.fxConsolidated.accounts.find(a=>a.id==='fixture-PDF').summaries[0].values.netProfit===80")))
            page.evaluate("S.operationHistory={schemaVersion:99,records:[{operationId:'future-opaque',accountId:'fixture-A',currency:'USD',netResult:12345}]};window.__futureRaw=JSON.stringify(S.operationHistory);JPWFXConsolidated.render()")
            page.locator('#fxcManual').click();page.locator('#fxcAccount').select_option('fixture-A')
            test('future history stays opaque and unmodified',lambda:require(page.evaluate("JSON.stringify(S.operationHistory)===__futureRaw&&document.querySelector('#fxcCoverage').textContent.includes('Versão do histórico não suportada')&&!document.querySelector('#fxconsolidated').textContent.includes('12.345')&&!document.querySelector('#fxconsolidated').textContent.includes('future-opaque')")))
            test('no unapproved requests',lambda:assert_fixture_requests(context))
            browser.close()
    finally: server.shutdown()
    report={'source_sha256':hashlib.sha256((ROOT/'src/js/20-ui/28-fx-consolidated.js').read_bytes()).hexdigest(),'observations':observations,'results':results,'passed':sum(x['pass'] for x in results),'total':len(results)}
    if args.output: Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0 if results and all(x['pass'] for x in results) else 1

if __name__=='__main__':raise SystemExit(main())
