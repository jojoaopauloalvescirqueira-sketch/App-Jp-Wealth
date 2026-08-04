#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import os
import socket
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

TEST_FX_RATES={
    'EURUSD':1.1413, 'GBPUSD':1.3303, 'AUDUSD':0.6893, 'NZDUSD':0.5681,
    'USDJPY':161.93, 'USDCHF':0.8069, 'USDCAD':1.4213, 'AUDCAD':0.9796,
}

def start_server():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f'http://127.0.0.1:{port}/'

def click_id(page, element_id):
    locator = page.locator('#' + element_id)
    assert locator.count() == 1, element_id
    locator.click()

def text(page, element_id):
    return page.locator('#' + element_id).inner_text()

def modal_text(page):
    return page.locator('#modalBox').inner_text().lower()

def prepare_page(browser, url):
    page = browser.new_page()
    observed={'console':[],'pageerror':[],'requestfailed':[]}
    page.jpwealth_observed=observed
    page.on('console',lambda message: observed['console'].append((message.type,message.text,message.location.get('url',''))))
    page.on('pageerror',lambda error: observed['pageerror'].append(str(error)))
    page.on('requestfailed',lambda request: observed['requestfailed'].append((request.url,request.failure)))
    page.route('**/dist/sw.js',lambda route: route.fulfill(
        status=200,
        content_type='application/javascript',
        body="self.addEventListener('install',event=>event.waitUntil(self.skipWaiting()));self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));",
    ))
    page.route('**/dist/icons/**',lambda route: route.continue_(
        url=route.request.url.replace('/dist/icons/','/icons/'),
    ))
    def fulfill_fx(route):
        parts=route.request.url.rstrip('/').split('/')
        pair=parts[-2]+parts[-1].split('?')[0]
        route.fulfill(
            status=200,
            content_type='application/json',
            body=json.dumps({'rate':TEST_FX_RATES.get(pair,1.0)}),
        )
    page.route('**/api.frankfurter.dev/**',fulfill_fx)
    page.goto(url, wait_until='load')
    page.wait_for_timeout(700)
    page.evaluate('''() => {
      window.alert=()=>{};
      window.confirm=()=>false;
      window.__onbShown=true;
      closeModal();
      window.URL.createObjectURL=()=> 'blob:jpwealth-test';
      window.URL.revokeObjectURL=()=>{};
      HTMLAnchorElement.prototype.click=function(){ window.__jpwealthDownload={filename:this.download}; };
    }''')
    return page

def assert_no_browser_errors(page):
    observed=page.jpwealth_observed
    console_errors=[entry for entry in observed['console'] if entry[0]=='error']
    assert not console_errors, {'console_errors':console_errors,'pageerrors':observed['pageerror'],'requestfailed':observed['requestfailed']}
    assert not observed['pageerror'], {'console':observed['console'],'pageerrors':observed['pageerror'],'requestfailed':observed['requestfailed']}

def close_checked(page):
    assert_no_browser_errors(page)
    page.close()

def assert_safe_copy_checkpoint(page):
    page.evaluate('''() => {
      S.onboarding={...S.onboarding, done:true, operador:'Operador Teste', supervisor:'Supervisor Teste'};
      S.accounts=[{nome:'Conta Privada Teste',tipo:'MESTRE',broker:'Teste',platform:'',platformLogin:'',investorPassword:'',perfil:'Base',sini:10000,satu:10000,perfilLocked:true}];
      S.ledger=[{data:'2026-01-31',resultado:100,saldo:10100,nota:'teste'}];
      save();
      markSessionCheckpoint();
    }''')

def complete_export_step(page):
    click_id(page, 'sessionExport')
    assert 'exportação iniciada' in modal_text(page)
    assert page.locator('#sessionExportAcknowledged').count() == 1
    assert not page.locator('#sessionExportContinue').is_enabled()
    page.locator('#sessionExportAcknowledged').check()
    assert page.locator('#sessionExportContinue').is_enabled()
    click_id(page, 'sessionExportContinue')
    assert 'confirmar encerramento' in modal_text(page)

def finish_with_phrase(page, phrase='APAGAR TUDO'):
    click_id(page, 'sessionProceed')
    assert page.locator('#sessionDeletePhrase').count() == 1
    button = page.locator('#sessionDeleteConfirm')
    page.locator('#sessionDeletePhrase').fill('APAGAR')
    assert not button.is_enabled()
    page.locator('#sessionDeletePhrase').fill('apagar tudo')
    assert not button.is_enabled()
    page.locator('#sessionDeletePhrase').fill('')
    assert not button.is_enabled()
    page.locator('#sessionDeletePhrase').fill('APAGAR TUDO ;')
    assert not button.is_enabled()
    page.locator('#sessionDeletePhrase').fill(phrase)
    assert button.is_enabled() == (phrase.strip() == 'APAGAR TUDO')
    if phrase.strip() == 'APAGAR TUDO':
        button.click()

def assert_empty_after_finalize(page):
    page.wait_for_timeout(500)
    facts = page.evaluate('''() => ({
      notice: document.querySelector('#sessionNotice')?.textContent || '',
      modalOpen: document.querySelector('#modalOverlay')?.classList.contains('show') || false,
      accounts: S.accounts.length,
      ledger: S.ledger.length,
      operator: S.onboarding.operador,
      supervisor: S.onboarding.supervisor,
      phasesWithData: S.phases.some(ph=>ph.orders.some(o=>o.id||o.status||o.par||o.lote)),
      performance: Array.isArray(S.perf) ? S.perf.length : -1,
      localState: localStorage.getItem('jpwealth_v9_state'),
      sessionCheckpoint: sessionStorage.getItem('jpwealth_session_checkpoint_v1'),
      body: document.body.innerText
    })''')
    assert 'Sessão finalizada. Os dados locais do JP Wealth foram removidos deste navegador.' in facts['notice'], facts
    assert facts['modalOpen'] is False, facts
    assert facts['localState'] is None, facts
    assert facts['sessionCheckpoint'], facts
    assert facts['accounts'] == 0 and facts['ledger'] == 0, facts
    assert facts['operator'] == '' and facts['supervisor'] == '', facts
    assert facts['phasesWithData'] is False and facts['performance'] == 0, facts
    assert 'Operador Teste' not in facts['body'] and 'Conta Privada Teste' not in facts['body'], facts

def run_source_surface(browser, base_url):
    page = prepare_page(browser, base_url + 'index.html')
    assert page.locator('#finalizeSessionBtn').count() == 1
    page.wait_for_timeout(1000)
    page.evaluate('''async () => {
      S=emptyJPWealthState();
      await updateFxRates();
      save();
      markSessionCheckpoint();
    }''')
    checkpoint_before_reload = page.evaluate("sessionStorage.getItem('jpwealth_session_checkpoint_v1')")
    page.reload(wait_until='load')
    page.wait_for_timeout(700)
    page.evaluate('''() => { window.__onbShown=true; closeModal(); }''')
    assert page.evaluate("sessionStorage.getItem('jpwealth_session_checkpoint_v1')") == checkpoint_before_reload
    assert page.evaluate('sessionHasChanges()') is False
    page.evaluate('''() => { S.instruments[0].preco += 1; save(); }''')
    assert page.evaluate('sessionHasChanges()') is True
    click_id(page, 'finalizeSessionBtn')
    assert 'existem alterações posteriores ao último backup' in modal_text(page)
    click_id(page, 'sessionCancel')
    close_checked(page)

def run_dist_suite(browser, url):
    page = prepare_page(browser, url)
    page.evaluate('''() => {
      S.onboarding={...S.onboarding, done:true, operador:'Operador Teste', supervisor:'Supervisor Teste'};
      S.accounts=[{nome:'Conta Privada Teste',tipo:'MESTRE',broker:'Teste',platform:'',platformLogin:'',investorPassword:'',perfil:'Base',sini:10000,satu:10000,perfilLocked:true}];
      S.ledger=[{data:'2026-01-31',resultado:100,saldo:10100,nota:'teste'}];
      save();
      localStorage.setItem('outra_aplicacao','preservar');
      localStorage.setItem('jpwealth_v9_state_corrompido_teste','raw');
      localStorage.setItem('jpw_rail','collapsed');
      localStorage.setItem('jpw_expl','on');
      localStorage.setItem('jpw_fs','2');
      localStorage.setItem('jpwealth_v9_icon_theme','marble-knight');
      markSessionCheckpoint();
      S.instruments[0].preco += 1;
      save();
      window.__checkpointOps=[];
      const originalRemove=Storage.prototype.removeItem;
      const originalSet=Storage.prototype.setItem;
      Storage.prototype.removeItem=function(key){
        if(this===sessionStorage && key==='jpwealth_session_checkpoint_v1') window.__checkpointOps.push(['remove',key]);
        return originalRemove.call(this,key);
      };
      Storage.prototype.setItem=function(key,value){
        if(this===sessionStorage && key==='jpwealth_session_checkpoint_v1') window.__checkpointOps.push(['set',key]);
        return originalSet.call(this,key,value);
      };
    }''')
    click_id(page, 'finalizeSessionBtn')
    changed_modal=modal_text(page)
    assert 'existem alterações posteriores ao último backup' in changed_modal
    assert page.locator('#sessionProceed').count() == 0
    click_id(page, 'sessionCancel')
    assert page.evaluate("localStorage.getItem('jpwealth_v9_state')") is not None

    click_id(page, 'finalizeSessionBtn')
    complete_export_step(page)
    click_id(page, 'sessionCancel')
    page.evaluate("S.params.saldoIni=22222; save()")
    click_id(page, 'finalizeSessionBtn')
    assert 'existem alterações posteriores ao último backup' in modal_text(page)
    click_id(page, 'sessionCancel')

    click_id(page, 'finalizeSessionBtn')
    complete_export_step(page)
    local_keys = page.evaluate("Object.keys(localStorage)")
    assert 'outra_aplicacao' in local_keys and 'jpwealth_v9_state_corrompido_teste' in local_keys
    finish_with_phrase(page, 'APAGAR TUDO ')
    assert page.evaluate("localStorage.getItem('outra_aplicacao')") == 'preservar'
    assert page.evaluate("localStorage.getItem('jpwealth_v9_state')") is None
    assert page.evaluate("localStorage.getItem('jpwealth_v9_state_corrompido_teste')") is None
    for key in ('jpw_rail', 'jpw_expl', 'jpw_fs', 'jpwealth_v9_icon_theme'):
        assert page.evaluate(f"localStorage.getItem('{key}')") is None, key
    checkpoint_ops=page.evaluate('window.__checkpointOps')
    assert ['remove','jpwealth_session_checkpoint_v1'] in checkpoint_ops, checkpoint_ops
    assert ['set','jpwealth_session_checkpoint_v1'] in checkpoint_ops, checkpoint_ops
    assert_empty_after_finalize(page)
    assert page.evaluate("save()") is False
    assert page.evaluate("localStorage.getItem('jpwealth_v9_state')") is None
    close_checked(page)

    page = prepare_page(browser, url)
    assert_safe_copy_checkpoint(page)
    click_id(page, 'finalizeSessionBtn')
    assert 'finalizar sessão neste computador' in modal_text(page)
    click_id(page, 'sessionHasCopy')
    assert 'confirmar encerramento' in modal_text(page)
    finish_with_phrase(page)
    assert_empty_after_finalize(page)
    close_checked(page)

    page = prepare_page(browser, url)
    assert_safe_copy_checkpoint(page)
    click_id(page, 'finalizeSessionBtn')
    click_id(page, 'sessionExportNow')
    assert 'exportação iniciada' in modal_text(page)
    page.locator('#sessionExportAcknowledged').check()
    click_id(page, 'sessionExportContinue')
    assert 'confirmar encerramento' in modal_text(page)
    finish_with_phrase(page)
    assert_empty_after_finalize(page)
    close_checked(page)

    page = prepare_page(browser, url)
    assert_safe_copy_checkpoint(page)
    click_id(page, 'finalizeSessionBtn')
    click_id(page, 'sessionHasCopy')
    click_id(page, 'sessionProceed')
    page.locator('#sessionDeletePhrase').fill('APAGAR TUDO')
    click_id(page, 'sessionCancel')
    assert page.evaluate("localStorage.getItem('jpwealth_v9_state')") is not None
    close_checked(page)

    page = prepare_page(browser, url)
    page.evaluate('fxAutoFetchedThisSession=true')
    backup_state = page.evaluate('''async () => {
      S=emptyJPWealthState();
      await updateFxRates();
      return structuredClone(S);
    }''')
    backup_state['params']['saldoIni'] = 12345
    backup_state['params']['saldoAtu'] = 12345
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fixture:
        fixture.write(json.dumps({'tipo':'jpwealth_full_backup','versao':'V9.1','state':backup_state}))
        fixture_path = fixture.name
    try:
        page.evaluate("window.confirm=()=>true")
        page.locator('#importFullBackupInput').set_input_files(fixture_path)
        page.wait_for_timeout(500)
        assert page.evaluate('sessionHasChanges()') is False
        page.reload(wait_until='load')
        page.wait_for_timeout(700)
        page.evaluate('''() => { window.__onbShown=true; closeModal(); }''')
        import_diff = page.evaluate('''() => {
          const checkpoint=JSON.parse(sessionStorage.getItem('jpwealth_session_checkpoint_v1'));
          return Object.keys(S).filter(key=>JSON.stringify(sessionStableValue(S[key]))!==JSON.stringify(sessionStableValue(checkpoint[key])));
        }''')
        assert page.evaluate('sessionHasChanges()') is False, import_diff
        page.evaluate("S.params.saldoIni=33333; save()")
        assert page.evaluate('sessionHasChanges()') is True
    finally:
        Path(fixture_path).unlink(missing_ok=True)
    close_checked(page)

    page = prepare_page(browser, url)
    assert_safe_copy_checkpoint(page)
    page.evaluate('''() => {
      window.__fxResolvers=[];
      window.fetch=()=>new Promise(resolve=>window.__fxResolvers.push(resolve));
      void updateFxRates();
    }''')
    assert page.evaluate('window.__fxResolvers.length') == 8
    click_id(page, 'finalizeSessionBtn')
    click_id(page, 'sessionHasCopy')
    finish_with_phrase(page)
    page.evaluate('''() => {
      window.__fxResolvers.forEach(resolve=>resolve({ok:true,json:async()=>({rate:999})}));
    }''')
    page.wait_for_timeout(500)
    assert_empty_after_finalize(page)
    close_checked(page)

    page_a = prepare_page(browser, url)
    page_a.evaluate('''() => {
      ['jpwealth_v9_state','jpwealth_v9_state_corrompido_teste','jpw_rail','jpw_expl','jpw_fs','jpwealth_v9_icon_theme'].forEach(k=>localStorage.removeItem(k));
      sessionStorage.clear();
    }''')
    page_a.reload(wait_until='load')
    page_a.wait_for_timeout(700)
    page_a.evaluate('''() => { window.__onbShown=true; closeModal(); }''')
    page_b = prepare_page(browser, url)
    page_b.evaluate('''() => {
      S.onboarding={...S.onboarding, done:true, operador:'Operador Aba B', supervisor:'Supervisor B'};
      S.accounts=[{nome:'Conta Aba B',tipo:'MESTRE',broker:'Teste',platform:'',platformLogin:'',investorPassword:'',perfil:'Base',sini:10000,satu:10000,perfilLocked:true}];
      save();
      markSessionCheckpoint();
    }''')
    page_a.reload(wait_until='load')
    page_a.wait_for_timeout(700)
    page_a.evaluate('''() => { window.__onbShown=true; closeModal(); }''')
    click_id(page_a, 'finalizeSessionBtn')
    complete_export_step(page_a)
    finish_with_phrase(page_a)
    page_b.wait_for_timeout(500)
    assert page_b.evaluate("localStorage.getItem('jpwealth_v9_state')") is None
    assert page_b.evaluate("S.onboarding.operador") == ''
    assert page_b.evaluate("save()") is False
    assert page_b.evaluate("localStorage.getItem('jpwealth_v9_state')") is None
    assert 'Operador Aba B' not in page_b.locator('body').inner_text()
    close_checked(page_a)
    close_checked(page_b)

def run_cache_test(browser, base_url):
    page = prepare_page(browser, base_url + 'index.html')
    keys=page.evaluate('''async () => {
      await caches.open('jp-wealth-old-audit');
      await caches.open('outra-aplicacao-cache-audit');
      const registration=await navigator.serviceWorker.register('./sw.js?audit='+Date.now(),{scope:'./'});
      await registration.update();
      for(let i=0;i<100;i++){
        const script=registration.active&&registration.active.scriptURL||'';
        if(registration.active&&registration.active.state==='activated'&&script.includes('audit=')) break;
        await new Promise(resolve=>setTimeout(resolve,50));
      }
      return await caches.keys();
    }''')
    assert 'jp-wealth-old-audit' not in keys, keys
    assert 'outra-aplicacao-cache-audit' in keys, keys
    assert 'jp-wealth-pwa-v9.1-icons-20260803-r3' in keys, keys
    close_checked(page)

def main():
    server, base_url = start_server()
    try:
        with sync_playwright() as playwright:
            candidates = [
                os.environ.get('JP_WEALTH_CHROMIUM', ''),
                '/usr/bin/chromium',
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            ]
            executable = next((path for path in candidates if path and Path(path).exists()), None)
            options = {'headless': True, 'args': ['--no-sandbox']}
            if executable:
                options['executable_path'] = executable
            browser = playwright.chromium.launch(**options)
            app_context = browser.new_context(service_workers='block')
            run_source_surface(app_context, base_url)
            run_dist_suite(app_context, base_url + 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')
            app_context.close()
            run_cache_test(browser, base_url)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('FINALIZE SESSION OK — fingerprint, gate assíncrono, reload, duas abas, caches externos, fonte/monólito e console/pageerror verificados.')

if __name__ == '__main__':
    main()
