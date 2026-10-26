#!/usr/bin/env python3
"""Empty first-use contract, exercised against the real modular application.

The clean-boot cases never seed S, storage or a bootstrap state fixture. Public
network is blocked explicitly; this suite makes no assertions about live quotes.
Compatibility/recovery cases seed only synthetic documents, in disposable browser
contexts, after identifying them as such. No operator profile is opened.
"""
import argparse
import functools
import hashlib
import json
import os
import sys
import threading
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CHROME = '/Users/joaoalvescirqueira/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
SOURCES = ['src/js/00-core/03-default-state.js', 'src/js/00-core/04-persistence.js',
           'src/js/20-ui/07-chart-crosshair-tooltip.js', 'src/js/40-app/07-finalize-session.js',
           'src/js/30-accounting/01-daily-ledger.js', 'src/styles/app.css', 'index.html', 'build-id.js',
           'tools/empty_first_use_test.py']
MUTANTS = {
    'account-seed': ('src/js/00-core/03-default-state.js', [
        ('  profiles:riskProfilesForState(),\n  accounts:[],\n', "  profiles:riskProfilesForState(),\n  accounts:[{nome:'Synthetic unwanted seed',tipo:'MESTRE',sini:10000,satu:10240}],\n")]),
    'answered-checklist': ('src/js/00-core/03-default-state.js', [('v:null', 'v:2')]),
    'coerced-zero': ('src/js/00-core/03-default-state.js', [
        ('params:{saldoIni:null,saldoAtu:null,', 'params:{saldoIni:0,saldoAtu:0,')]),
    'classify-incomplete': ('src/js/20-ui/07-chart-crosshair-tooltip.js', [
        ('if(total===0||answered!==total){', 'if(false){')]),
    'reject-null-checklist': ('src/js/00-core/04-persistence.js', [
        ('item.v===null || Number.isInteger(item.v)', 'Number.isInteger(item.v)')]),
    'accept-missing-checklist': ('src/js/00-core/04-persistence.js', [
        ('item.v===null || Number.isInteger(item.v)', 'item.v==null || Number.isInteger(item.v)')]),
    'clipped-classification': ('src/styles/app.css', []),
}


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class Server(ThreadingHTTPServer):
    request_queue_size = 256


SNAPSHOT = """() => ({accounts:structuredClone(S.accounts),perf:structuredClone(S.perf),
 params:{saldoIni:S.params.saldoIni,saldoAtu:S.params.saldoAtu,inicio:S.params.inicio},
 atr55:S.atr55,atr660:S.atr660,expAlvo:S.expAlvo,loteMaster:S.loteMaster,
 period:structuredClone(S.period),reserveMasterCapital:S.onboarding.reserveMasterCapital,
 forex:structuredClone(S.forex),ledger:structuredClone(S.ledger),
 ledgerArchive:structuredClone(S.ledgerArchive),transitionLog:structuredClone(S.transitionLog),
 fxConsolidated:structuredClone(S.fxConsolidated),
 checklist:structuredClone(S.checklist),
 raw:localStorage.getItem(LSKEY),
 checkpoints:Object.fromEntries(Object.keys(sessionStorage).map(k=>[k,sessionStorage.getItem(k)]))})"""


def empty_assertions(s):
    assert s['accounts'] == [], 'Pre-created accounts: ' + repr([a.get('nome') for a in s['accounts']])
    assert s['perf'] == [], 'Demonstrative performance records remain'
    assert s['forex']['accounts'] == {} and s['forex']['activeAccountId'] is None, 'Operational account/context exists before confirmation'
    assert not s['forex'].get('accountContexts', {}).get('accounts'), 'A registered period exists before confirmation'
    for key in ('ledger', 'ledgerArchive', 'transitionLog'):
        assert s[key] == [], 'Financial history exists: ' + key
    assert s['fxConsolidated']['accounts'] == [] and s['fxConsolidated']['receipts'] == [], 'Consolidated financial history exists'


def missing_assertions(s):
    assert s['params'] == {'saldoIni': None, 'saldoAtu': None, 'inicio': ''}, 'Missing balance/date became a financial fact: ' + repr(s['params'])
    assert all(s[k] is None for k in ('atr55', 'atr660', 'expAlvo', 'loteMaster')), 'Unobserved market/position inputs are prefilled'
    assert s['period'].get('nome') == '' and s['period'].get('profile') == '', 'No period may imply a chosen profile'
    assert s['reserveMasterCapital'] == '', 'Reserve capital derived from a default balance'


def unanswered_assertions(s):
    answers = [i['v'] for g in s['checklist'] for i in g['items']]
    assert answers and all(v is None for v in answers), 'Checklist already answered: ' + repr(answers)


def aggregate_cases(cases):
    """Preserve case taxonomy; no selected cases never constitutes a result."""
    counts = {status: 0 for status in ('PASS', 'PRODUCT_FAIL', 'ENVIRONMENT_ERROR', 'TEST_HARNESS_FAIL')}
    for case in cases:
        status = case.get('status')
        counts[status if status in counts else 'TEST_HARNESS_FAIL'] += 1
    if not cases:
        return 'TEST_HARNESS_FAIL', counts
    for status in ('PRODUCT_FAIL', 'ENVIRONMENT_ERROR', 'TEST_HARNESS_FAIL'):
        if counts[status]:
            return status, counts
    return 'PASS', counts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--only', default='')
    ap.add_argument('--mutant', choices=list(MUTANTS), default=None)
    args = ap.parse_args()
    if args.out.exists():
        ap.error('Choose a new evidence file; prior results are preserved')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    artifacts = args.out.parent / (args.out.stem + '-artifacts')
    artifacts.mkdir(exist_ok=False)
    root = args.root.resolve()
    mutant_source = None
    if args.mutant:
        mutant_path, substitutions = MUTANTS[args.mutant]
        mutant_source = (root / mutant_path).read_text()
        for before, after in substitutions:
            count = mutant_source.count(before)
            valid = count >= 1 if args.mutant == 'answered-checklist' else count == 1
            if not valid:
                ap.error('TEST_HARNESS_FAIL: mutation anchor drift: ' + repr((before, count)))
            mutant_source = mutant_source.replace(before, after, 1)
        if args.mutant == 'clipped-classification':
            mutant_source += '\n#forexChecklistDialog #chClass{white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}\n'
    report = {'root': str(root), 'contract': 'CHG-JPW-EMPTY-FIRST-USE-TESTS-20261024',
              'network': 'Public requests aborted; no live quote coverage claimed',
              'stateFixtureBeforeCleanBoot': False, 'mutant': args.mutant,
              'sources': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in SOURCES if (root / p).is_file()},
              'cases': []}
    server = Server(('127.0.0.1', 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/index.html'

    def boot(browser, record, seed=None, width=1440, dark=False):
        context = browser.new_context(service_workers='block', viewport={'width': width, 'height': 1000},
                                      timezone_id='America/Sao_Paulo', reduced_motion='reduce',
                                      color_scheme='dark' if dark else 'light')
        record['blockedPublic'] = []
        record['localAssetFailures'] = []
        record['pageerrors'] = []
        record['sourceMutations'] = []

        def route(request_route):
            request = request_route.request
            parsed = urlsplit(request.url)
            if args.mutant and parsed.path.endswith('/' + MUTANTS[args.mutant][0]):
                path = MUTANTS[args.mutant][0]
                record['sourceMutations'].append({'path': path, 'mutant': args.mutant})
                request_route.fulfill(status=200, content_type='text/css' if path.endswith('.css') else 'application/javascript', body=mutant_source)
                return
            if parsed.scheme not in ('http', 'https') or parsed.hostname in ('127.0.0.1', 'localhost', '::1'):
                request_route.continue_()
            else:
                record['blockedPublic'].append(request.url)
                request_route.abort('blockedbyclient')
        context.route('**/*', route)
        if seed is not None:
            context.add_init_script('localStorage.setItem("jpwealth_v9_state",' + json.dumps(seed) + ');')
        page = context.new_page()
        page.set_default_timeout(12000)
        page.on('pageerror', lambda e: record['pageerrors'].append(str(e)))
        page.on('requestfailed', lambda r: record['localAssetFailures'].append({'url': r.url, 'failure': r.failure})
                if urlsplit(r.url).hostname in ('127.0.0.1', 'localhost', '::1') else None)
        page.goto(url, wait_until='load')
        page.wait_for_function("typeof S!=='undefined' && typeof renderCheck==='function' && !!window.JPWNavigation && typeof ffNewsInFlight!=='undefined' && !ffNewsInFlight")
        page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
        # The production welcome is scheduled 350 ms after boot. Observe it;
        # never suppress it with __onbShown, which would bypass first-use UI.
        if seed is None:
            page.locator('#jpwWelcomeClose').wait_for(state='visible')
        if page.locator('#jpwWelcomeClose').is_visible():
            page.locator('#jpwWelcomeClose').click()
        record['build'] = page.evaluate("typeof JP_WEALTH_BUILD_ID==='undefined'?null:JP_WEALTH_BUILD_ID")
        return page, context

    def go(page, title):
        target = page.get_by_role('button', name=title, exact=True)
        if not target.count() or not target.first.is_visible():
            page.locator('#execNavTrigger').click()
        page.get_by_role('button', name=title, exact=True).first.click()
        page.evaluate('()=>new Promise(r=>requestAnimationFrame(r))')

    def checklist(page):
        go(page, 'Operação')
        page.locator('#execChecklistBtn').click()
        page.locator('#forexChecklistBody .seg').first.wait_for()

    def run(browser, ident, name, callback, seed=None):
        if args.only and args.only not in ident + ' ' + name:
            return
        record = {'id': ident, 'name': name}
        context = None
        try:
            page, context = boot(browser, record, seed=seed)
            record['observation'] = callback(page, context)
            if args.mutant:
                assert record['sourceMutations'], 'TEST_HARNESS_FAIL: source mutant was never loaded'
            assert not record['localAssetFailures'], record['localAssetFailures']
            assert not record['pageerrors'], record['pageerrors']
            record['status'] = 'PASS'
        except Exception as exc:
            failure = ('TEST_HARNESS_FAIL' if 'TEST_HARNESS_FAIL:' in str(exc) else
                       'PRODUCT_FAIL' if isinstance(exc, AssertionError) or 'PRODUCT_ASSERTION:' in str(exc) else 'TEST_HARNESS_FAIL')
            record.update(status=failure,
                          error=str(exc), trace=traceback.format_exc())
        finally:
            if context:
                try:
                    page = context.pages[0]
                    record['finalSnapshot'] = page.evaluate(SNAPSHOT)
                    page.screenshot(path=str(artifacts / (ident + '.png')))
                except Exception:
                    pass
                context.close()
            report['cases'].append(record)
            print(ident, record['status'], record.get('error', '')[:240], flush=True)
            args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    def clean(page, _):
        s = page.evaluate(SNAPSHOT)
        empty_assertions(s)
        unanswered_assertions(s)
        return s

    def missing(page, _):
        s = page.evaluate(SNAPSHOT)
        missing_assertions(s)
        return s

    def navigation(page, _):
        before = page.evaluate(SNAPSHOT)
        routes = ['Desempenho', 'Contas e Períodos', 'Operação', 'Contabilidade', 'Reservas', 'Histórico de operações']
        for title in routes:
            go(page, title)
            after = page.evaluate(SNAPSHOT)
            empty_assertions(after)
            assert after['raw'] == before['raw'], 'Read-only navigation wrote main state: ' + title
        go(page, 'Contas e Períodos')
        assert 'Nenhuma conta cadastrada' in page.locator('body').inner_text(), 'Missing account empty-state guidance'
        assert page.locator('#fxAccountsCreate').is_visible(), 'Account creation action absent'
        return {'routes': routes, 'mainRawUnchanged': True}

    def reload_empty(page, _):
        before = page.evaluate(SNAPSHOT)
        page.reload(wait_until='load')
        page.wait_for_function("typeof S!=='undefined' && !!window.JPWNavigation")
        after = page.evaluate(SNAPSHOT)
        empty_assertions(after)
        missing_assertions(after)
        unanswered_assertions(after)
        assert before['raw'] == after['raw'], 'Reload wrote a financial document'
        for raw in after['checkpoints'].values():
            assert 'Jp Wealth MAM' not in raw and 'Swissquote I' not in raw, 'Checkpoint retains demo accounts'
        return {'before': before, 'after': after}

    def check_unanswered(page, _):
        checklist(page)
        assert page.locator('#forexChecklistBody .seg button.on').count() == 0, 'No answer may be selected before input'
        assert page.locator('#chScore').inner_text().strip() == '—', 'Incomplete checklist shows numeric score'
        label = page.locator('#chClass').inner_text()
        assert 'Não concluído' in label and '0 de 15' in label, 'Missing explicit unanswered progress: ' + label
        assert 'setup válido' not in label and 'PROIBIDO OPERAR' not in label, 'Unanswered checklist classified as an actual result'
        return {'score': page.locator('#chScore').inner_text(), 'label': label}

    def check_partial_complete(page, _):
        checklist(page)
        rows = page.locator('#forexChecklistBody .seg')
        total = rows.count()
        rows.first.locator('[data-v="0"]').click()
        assert page.evaluate('S.checklist[0].items[0].v') == 0, 'Explicit zero not stored as an answer'
        assert page.locator('#chScore').inner_text().strip() == '—', 'Partial checklist classified'
        assert f'1 de {total}' in page.locator('#chClass').inner_text(), 'Partial progress wrong'
        for i in range(total):
            rows.nth(i).locator('[data-v="2"]').click()
        assert page.locator('#chScore').inner_text().strip() == str(total * 2), 'Complete score formula changed'
        assert 'SETUP A+' in page.locator('#chClass').inner_text(), 'Complete threshold changed'
        for i in range(total):
            rows.nth(i).locator('[data-v="0"]').click()
        assert page.locator('#chScore').inner_text().strip() == '0', 'Explicit all-zero score hidden as absence'
        assert 'PROIBIDO OPERAR' in page.locator('#chClass').inner_text(), 'Zero threshold changed'
        return {'items': total, 'completeScores': [total * 2, 0]}

    def empty_checklist(page, _):
        page.evaluate('S.checklist=[];renderCheck()')
        assert page.locator('#chScore').inner_text().strip() == '—', 'Empty checklist produces a score'
        assert 'Não concluído' in page.locator('#chClass').inner_text(), 'Empty checklist treated as complete'
        return {'score': page.locator('#chScore').inner_text(), 'label': page.locator('#chClass').inner_text()}

    def visual_classification(page, _):
        before = page.evaluate(SNAPSHOT)
        go(page, 'Operação')
        observations = []
        for width in (320, 390):
            page.set_viewport_size({'width': width, 'height': 1000})
            for layout in ('sidebar', 'topbar', 'glass', 'submenu'):
                page.evaluate('layout=>mountNavigationLayout(layout)', layout)
                for theme in ('light', 'dark'):
                    page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
                    page.locator('#execChecklistBtn').click()
                    page.locator('#chClass').scroll_into_view_if_needed()
                    measured = page.evaluate("""() => {
                      const e=document.getElementById('chClass'),b=e.getBoundingClientRect(),s=getComputedStyle(e);
                      const range=document.createRange();range.selectNodeContents(e);
                      const rects=[...range.getClientRects()].map(r=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom}));
                      const close=document.getElementById('forexChecklistClose'),c=close.getBoundingClientRect(),d=document.getElementById('forexChecklistDialog');
                      return {text:e.textContent,scroll:e.scrollWidth,client:e.clientWidth,scrollHeight:e.scrollHeight,clientHeight:e.clientHeight,
                        whiteSpace:s.whiteSpace,textOverflow:s.textOverflow,overflow:s.overflow,box:{left:b.left,right:b.right,top:b.top,bottom:b.bottom},rects,
                        dialog:{scroll:d.scrollWidth,client:d.clientWidth},pageOverflow:document.documentElement.scrollWidth>innerWidth+2,
                        close:{left:c.left,right:c.right,top:c.top,bottom:c.bottom,width:c.width,height:c.height,disabled:close.disabled},viewport:{width:innerWidth,height:innerHeight}};
                    }""")
                    measured.update(width=width, layout=layout, theme=theme)
                    observations.append(measured)
                    assert measured['text'] == 'Não concluído — 0 de 15 respostas', 'Incomplete progress text changed'
                    assert measured['scroll'] <= measured['client'] + 2, 'Classification clipped horizontally: ' + repr(measured)
                    assert measured['scrollHeight'] <= measured['clientHeight'] + 2, 'Classification clipped vertically: ' + repr(measured)
                    b = measured['box']
                    assert all(r['left'] >= b['left'] - 2 and r['right'] <= b['right'] + 2 and r['top'] >= b['top'] - 2 and r['bottom'] <= b['bottom'] + 2 for r in measured['rects']), 'Classification text extends beyond its box: ' + repr(measured)
                    assert measured['dialog']['scroll'] <= measured['dialog']['client'] + 2 and not measured['pageOverflow'], 'Checklist/page has horizontal overflow'
                    c = measured['close']
                    assert not c['disabled'] and c['width'] >= 44 and c['height'] >= 44 and c['left'] >= -2 and c['right'] <= width + 2 and c['top'] >= -2 and c['bottom'] <= 1002, 'Close control inaccessible: ' + repr(measured)
                    page.screenshot(path=str(artifacts / f'EMPTY-VISUAL-01-{width}-{layout}-{theme}.png'))
                    page.locator('#forexChecklistClose').click()
        after = page.evaluate(SNAPSHOT)
        for key in ('accounts', 'forex', 'params', 'checklist', 'raw'):
            assert after[key] == before[key], 'Visual consultation changed financial state: ' + key
        return observations

    def cancel_account(page, _):
        go(page, 'Contas e Períodos')
        before = page.evaluate(SNAPSHOT)
        page.locator('#fxAccountsCreate').click()
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-name').fill('Synthetic cancelled account')
        page.locator('#fxcr-login').fill('000999')
        page.locator('#fxcRegistrationCancel').click()
        after = page.evaluate(SNAPSHOT)
        assert after == before, 'Opening/typing/cancelling account changed financial facts or main storage'
        empty_assertions(after)
        return {'cancelledWithoutFinancialMutation': True}

    def prepare_registration(page, name='Synthetic deliberate account', login='000987'):
        go(page, 'Contas e Períodos')
        page.locator('#fxAccountsCreate').click()
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-name').fill(name)
        page.locator('#fxcr-login').fill(login)
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-platform').select_option('MetaTrader 5')
        page.locator('#fxcr-currency').fill('USD')
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-profileKey').select_option('base')
        page.locator('#fxcwNext').click()

    def create_and_reload(page, _):
        before = page.evaluate(SNAPSHOT)
        prepare_registration(page)
        assert page.evaluate(SNAPSHOT) == before, 'Typing/review created a registration before confirmation'
        page.locator('#fxcRegistrationSave').click()
        # The workspace's deliberate registration returns to account consultation;
        # it does not open a period writer automatically.
        page.wait_for_function('S.accounts.length===1 && !document.getElementById("fxcRegistrationDialog").open')
        saved = page.evaluate(SNAPSHOT)
        assert len(saved['accounts']) == 1 and saved['accounts'][0]['nome'] == 'Synthetic deliberate account', 'Explicit save did not create exactly one account'
        assert saved['accounts'][0]['sini'] is None and saved['accounts'][0]['satu'] is None, 'New registration invented an observed balance of zero'
        assert saved['forex']['accounts'] == {} and not saved['forex'].get('accountContexts', {}).get('accounts'), 'Registration silently created observations/periods'
        assert saved['raw'] is not None, 'Registration was not persisted'
        page.reload(wait_until='load')
        page.wait_for_function("typeof S!=='undefined' && !!window.JPWNavigation")
        reloaded = page.evaluate(SNAPSHOT)
        assert reloaded['accounts'] == saved['accounts'] and reloaded['forex'] == saved['forex'], 'Reload changed saved registration/context'
        assert reloaded['params']['saldoIni'] is None, 'Registration inferred global capital'
        return {'oneExplicitRegistration': True, 'noPeriodOrObservations': True, 'reloadPreserved': True}

    def conflict(page, context):
        prepare_registration(page, 'Synthetic stale draft', '001111')
        other = context.new_page()
        other.goto(url, wait_until='load')
        other.wait_for_function("typeof S!=='undefined' && !!window.JPWNavigation")
        # This case deliberately confirms a separate synthetic document in the
        # second tab. It never changes the source or substitutes a writer.
        raw = other.evaluate("""() => {
          S.checklist[0].items[0].v=0;
          if(save()!==true)throw Error('TEST_HARNESS_FAIL: second-tab explicit save refused');
          return localStorage.getItem(LSKEY);
        }""")
        page.locator('#fxcRegistrationSave').click()
        page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
        assert page.evaluate('localStorage.getItem(LSKEY)') == raw, 'Stale registration overwrote second-tab document'
        assert page.evaluate('S.accounts.length') == 0, 'Stale registration created an account'
        assert page.locator('#fxcRegistrationDialog').is_visible(), 'Conflict discarded the form'
        assert page.locator('#fxcr-name').input_value() == 'Synthetic stale draft', 'Conflict lost typed draft'
        return {'concurrentRawPreserved': True, 'draftRetained': True}

    def null_zero_validation(page, _):
        return page.evaluate("""() => {
          const original=structuredClone(S), results=[];
          const accepts=doc=>{try{const n=normalizeImportedState(doc);return {ok:true,state:n}}catch(e){return {ok:false,error:String(e)}}};
          const nil=structuredClone(original);nil.params.saldoIni=null;nil.params.saldoAtu=null;
          nil.checklist.forEach(g=>g.items.forEach(i=>i.v=null));
          let r=accepts(nil);if(!r.ok||r.state.params.saldoIni!==null||r.state.checklist[0].items[0].v!==null)throw Error('PRODUCT_ASSERTION: documented null not accepted/preserved '+JSON.stringify(r));
          const zero=structuredClone(original);zero.params.saldoIni=0;zero.params.saldoAtu=0;zero.checklist.forEach(g=>g.items.forEach(i=>i.v=0));
          r=accepts(zero);if(!r.ok||r.state.params.saldoIni!==0||r.state.checklist[0].items[0].v!==0)throw Error('PRODUCT_ASSERTION: explicit zero not preserved');
          for(const bad of [undefined,'',false,true,0.5,-1,3]){
            const d=structuredClone(original);if(bad===undefined)delete d.checklist[0].items[0].v;else d.checklist[0].items[0].v=bad;
            r=accepts(d);if(r.ok)throw Error('PRODUCT_ASSERTION: malformed checklist accepted '+String(bad));results.push({value:String(bad),refused:true});
          }
          for(const bad of [undefined,'',false,true,'10000',{},[]]){
            const d=structuredClone(original);if(bad===undefined)delete d.params.saldoIni;else d.params.saldoIni=bad;
            r=accepts(d);if(r.ok)throw Error('PRODUCT_ASSERTION: malformed/missing balance accepted '+String(bad));results.push({balance:String(bad),refused:true});
          }
          if(JSON.stringify(S)!==JSON.stringify(original))throw Error('PRODUCT_ASSERTION: import validation changed live S');
          return {nullAndZeroDistinct:true,malformed:results};
        }""")

    def legacy_and_roundtrip(page, _):
        return page.evaluate("""async() => {
          const initial=JSON.stringify(S), legacy=structuredClone(S);
          legacy.params.saldoIni=10000;legacy.params.saldoAtu=10240;legacy.params.inicio='2026-05-25';
          legacy.accounts=[{nome:'Jp Wealth MAM',tipo:'MESTRE',broker:'Hantec Markets',platform:'',platformLogin:'',investorPassword:'',perfil:'Base',sini:10000,satu:10240,perfilLocked:true},
            {nome:'Synthetic explicitly recorded zero',tipo:'PRÓPRIA',broker:'',platform:'',platformLogin:'',investorPassword:'',perfil:'Base',sini:0,satu:0,perfilLocked:true}];
          legacy.perf=[{mes:'Jan',ret:.012,dd:.01}];legacy.period={nome:'Synthetic saved period',profile:'base'};
          legacy.checklist.forEach(g=>g.items.forEach(i=>i.v=1));
          const imported=normalizeImportedState(legacy);
          if(imported.accounts[0]?.nome!=='Jp Wealth MAM'||imported.accounts[0]?.sini!==10000||imported.perf[0]?.ret!==.012||imported.checklist[0].items[0].v!==1)throw Error('PRODUCT_ASSERTION: existing saved facts deleted/replaced');
          if(imported.accounts[1]?.sini!==0||imported.accounts[1]?.satu!==0)throw Error('PRODUCT_ASSERTION: existing explicit zero erased');
          // The backup contract requires an explicitly confirmed durable base.
          // This write is part of this isolated compatibility case only.
          if(save()!==true)throw Error('TEST_HARNESS_FAIL: explicit synthetic empty save refused');
          const confirmed=JSON.stringify(S);
          const raw=JSON.parse(await dgBuildBackupBlob(1,'synthetic-empty.json','2026-10-24T12:00:00Z').text());
          const restored=normalizeImportedState(raw);
          if(restored.params.saldoIni!==null||restored.params.saldoAtu!==null||restored.accounts.length||restored.checklist.some(g=>g.items.some(i=>i.v!==null)))throw Error('PRODUCT_ASSERTION: new empty backup lost absence');
          if(JSON.stringify(S)!==confirmed)throw Error('PRODUCT_ASSERTION: backup/query changed live state');
          return {oldFactsPreserved:true,newBackupNullPreserved:true};
        }""")

    def catalog(page, _):
        return page.evaluate("""() => {
          if(!S.instruments.length||!S.profiles.length||!S.matrix.length)throw Error('PRODUCT_ASSERTION: policy/catalog was removed');
          if(!S.instruments.some(i=>i.name==='US500'&&i.banned)||!S.instruments.some(i=>i.name==='XAUUSD'&&i.banned))throw Error('PRODUCT_ASSERTION: prohibition lost');
          if(S.mvpNotes.items.length||S.mvpNotes.folders.length||Object.keys(S.nocoda.studies).length||S.pivotStudies?.items?.length)throw Error('PRODUCT_ASSERTION: another module precreated personal records');
          return {instruments:S.instruments.length,profiles:S.profiles.length,phases:S.matrix.length,consent:S.onboarding.consentAccepted};
        }""")

    def corrupt(page, _):
        raw = page.evaluate('localStorage.getItem(LSKEY)')
        result = page.evaluate('save()')
        assert result is False, 'Corrupt base permits write'
        assert page.evaluate('localStorage.getItem(LSKEY)') == raw, 'Recovery replaced original raw'
        assert page.evaluate("jpWealthLoadRecovery && jpWealthLoadRecovery.active"), 'Recovery not active'
        return {'rawPreserved': True, 'writeRefused': True}

    def malformed_recovery(page, _):
        original = page.evaluate('structuredClone(S)')
        cases = []
        missing = json.loads(json.dumps(original))
        del missing['params']['saldoIni']
        malformed = json.loads(json.dumps(original))
        malformed['checklist'][0]['items'][0]['v'] = False
        for name, state in [('missing-balance', missing), ('boolean-answer', malformed)]:
            raw = json.dumps(state, ensure_ascii=False)
            page.evaluate('(raw)=>localStorage.setItem("jpwealth_v9_state",raw)', raw)
            page.reload(wait_until='load')
            page.wait_for_function("typeof jpWealthLoadRecovery!=='undefined' && jpWealthLoadRecovery.active")
            assert page.evaluate('save()') is False, name + ' permitted a write'
            assert page.evaluate('localStorage.getItem(LSKEY)') == raw, name + ' replaced incompatible original'
            assert page.evaluate('jpWealthLoadRecovery.raw') == raw, name + ' lost recovery material'
            cases.append({'case': name, 'recovery': True, 'rawPreserved': True})
        return cases

    try:
        with sync_playwright() as pw:
            executable = os.environ.get('JP_WEALTH_CHROMIUM') or (CHROME if Path(CHROME).exists() else None)
            browser = pw.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))
            cases = [
                ('EMPTY-BOOT-01', 'clean boot has no accounts history or answers', clean),
                ('EMPTY-BOOT-02', 'absent financial inputs stay null and profile unchosen', missing),
                ('EMPTY-NAV-01', 'real Forex navigation stays empty without writes', navigation),
                ('EMPTY-RELOAD-01', 'reload and checkpoint do not restore demonstrations', reload_empty),
                ('EMPTY-CHECK-01', 'unanswered checklist has no score classification', check_unanswered),
                ('EMPTY-CHECK-02', 'partial complete and explicit zero answers', check_partial_complete),
                ('EMPTY-CHECK-03', 'empty checklist never counts as complete', empty_checklist),
                ('EMPTY-VISUAL-01', 'complete classification and accessible close at320/390 in four layouts and two themes', visual_classification),
                ('EMPTY-CANCEL-01', 'typing and cancelling new account creates no facts', cancel_account),
                ('EMPTY-CREATE-01', 'one explicit registration persists without inferred period', create_and_reload),
                ('EMPTY-CONFLICT-01', 'stale registration preserves second-tab document and draft', conflict),
                ('EMPTY-IMPORT-01', 'explicit null zero and malformed values distinguished', null_zero_validation),
                ('EMPTY-BACKUP-01', 'legacy saved facts preserved and new null backup roundtrip', legacy_and_roundtrip),
                ('EMPTY-CATALOG-01', 'catalogs and prohibitions remain available', catalog),
                ('EMPTY-RECOVERY-02', 'missing balance and malformed answer enter raw-preserving recovery', malformed_recovery),
            ]
            for ident, name, callback in cases:
                run(browser, ident, name, callback)
            run(browser, 'EMPTY-RECOVERY-01', 'corrupt storage preserved and writes refused', corrupt, seed='{synthetic invalid JSON')
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    report['result'], report['counts'] = aggregate_cases(report['cases'])
    report['selectedCases'] = len(report['cases'])
    report['failurePrecedence'] = ['PRODUCT_FAIL', 'ENVIRONMENT_ERROR', 'TEST_HARNESS_FAIL']
    if not report['cases']:
        report['selectionError'] = 'No cases matched --only=' + repr(args.only)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(report['result'], flush=True)
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
