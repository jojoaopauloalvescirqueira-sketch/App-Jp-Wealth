#!/usr/bin/env python3
"""First-access journeys on real JP Wealth sources and disposable profiles.

Only the public economic bootstrap is fixture data. The financial engine,
registration, period writer, Blob, FileReader and persistence are the app's.
Fault injection is limited to Storage when explicitly testing refused/unknown
writes. Does not use a personal browser, clear storage or change existing gates.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler
import json
from pathlib import Path
import subprocess
import threading
import traceback

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright
from browser_bootstrap_fixture import (
    assert_fixture_requests, install_bootstrap, wait_bootstrap,
)
from browser_fixture_server import BrowserFixtureServer
from notes_launcher_test import launch_options


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = (
    'index.html', 'build-id.js', 'src/styles/app.css',
    'src/js/00-core/04-persistence.js',
    'src/js/10-domain/01-risk-instruments.js',
    'src/js/10-domain/03-phase-transitions.js',
    'src/js/20-ui/28-fx-consolidated.js',
    'src/js/40-app/04-onboarding.js', 'src/js/40-app/06-boot.js',
    'src/js/40-app/24-fx-consolidated-import.js',
)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def hashes(root):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in SOURCE_PATHS if (root / name).exists()}


def financial_snapshot(page):
    return page.evaluate("""() => ({
      state: JSON.stringify(S), durable: localStorage.getItem(LSKEY),
      writes: window.__firstAccessWrites.filter(row=>row.key===LSKEY).length
    })""")


def instrument(page):
    page.evaluate("""() => {
      window.__firstAccessWrites = [];
      const set = Storage.prototype.setItem;
      Storage.prototype.setItem = function(key, value) {
        window.__firstAccessWrites.push({key, area:this===localStorage?'local':'session'});
        return set.call(this,key,value);
      };
    }""")


def assert_unchanged(page, before, label):
    after = financial_snapshot(page)
    old_state, new_state = json.loads(before['state']), json.loads(after['state'])
    changed = [key for key in old_state.keys() | new_state.keys()
               if old_state.get(key) != new_state.get(key)]
    diagnostic = {'stateKeys':changed, 'durableChanged':before['durable']!=after['durable'],
                  'writes':page.evaluate('window.__firstAccessWrites').copy()}
    assert after == before, label + ': navigation changed financial/durable state ' + json.dumps(diagnostic,ensure_ascii=False)


def active_step(page):
    return page.locator('#modalBox [data-onbstep].active').get_attribute('data-onbstep')


def legacy_open(page, mode='new'):
    # Explicitly exercise the preserved legacy entry, not the default welcome.
    page.evaluate("mode => { closeModal(); openOnboardingModal(mode); }", mode)
    page.locator('#obOperador').wait_for(state='visible')


def legacy_step(page, key):
    target = page.locator('[data-onbtab="' + key + '"]')
    if not target.is_visible() and page.locator('#obRailToggle').is_visible():
        page.locator('#obRailToggle').click()
    target.click()


def fill_legacy(page, password=True):
    page.locator('#obOperador').fill('Operador sintético')
    page.locator('#obSupervisor').fill('Supervisora sintética')
    page.locator('#obSaldo').fill('10000')
    page.locator('#obData').fill('2026-10-07')
    legacy_step(page, 'instit')
    page.locator('[data-obinsttype="broker"]').click()
    page.locator('[data-obbroker]').first.click()
    page.locator('#obBrokerLogin').fill('10000001')
    page.locator('#obBrokerServer').fill('SYNTHETIC-DEMO')
    page.locator('#obPlataforma').fill('MetaTrader 5')
    page.locator('#obAlav').fill('1:100')
    if password:
        # Secret is ephemeral synthetic input; never put it in receipts.
        page.locator('#obInvestorPassword').fill('SYNTHETIC-SESSION-ONLY')
    legacy_step(page, 'risk')
    page.locator('[data-obprof="base"]').click()
    page.locator('#obRiskProfileAccept').check()
    legacy_step(page, 'reserves')
    page.locator('#obReserveFcrCurrent').fill('2500')
    page.locator('#obReserveMonthlyExpenses').fill('100')
    page.locator('#obReserveFeoCurrent').fill('600')
    page.locator('#obReserveSegregation').check()
    if page.locator('#obReserveDeficitAccepted').is_visible():
        page.locator('#obReserveDeficitAccepted').check()
    legacy_step(page, 'cash')
    page.locator('#obCentralCashStatus').select_option('Sim.')
    page.locator('#obCentralCashCustody').select_option('Conta bancária institucional')
    page.locator('#obFcrLiquidity').select_option('D+0')
    page.locator('#obFeoLiquidity').select_option('D+0')
    page.locator('#obCashLedgerStatus').select_option('Livro-razão patrimonial ativo')
    page.locator('#obCentralCashPolicy').check()
    legacy_step(page, 'protect')
    page.locator('#obEpStatus').select_option('Não vou utilizar.')
    page.locator('#obEpRestrictive').check()
    page.locator('#obEpNoConfigAccepted').check()
    legacy_step(page, 'database')
    page.locator('#obDbResp').check()
    legacy_step(page, 'consent')
    page.locator('#obConsent').check()


def submit_legacy_review(page):
    page.locator('#modalConfirm').click()
    page.locator('#obSummaryAccept').wait_for(state='visible')
    page.locator('#obSummaryAccept').check()
    page.locator('#obSummaryConfirm').click()


def audit_layout(page):
    return page.evaluate("""() => {
      const box=document.getElementById('modalBox'),step=box.querySelector('[data-onbstep].active');
      const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};};
      const shown=e=>!!e.getBoundingClientRect().width && !!e.getBoundingClientRect().height;
      return {viewport:{width:innerWidth,height:innerHeight},box:rect(box),
        globalOverflow:document.documentElement.scrollWidth>innerWidth+1,
        dialog:box.getAttribute('role'),ariaModal:box.getAttribute('aria-modal'),
        fields:[...step.querySelectorAll('input:not([type=checkbox]),select')].filter(shown).map(e=>({id:e.id,rect:rect(e),font:getComputedStyle(e).fontSize})),
        actions:[...box.querySelectorAll('button')].filter(shown).map(e=>({id:e.id,text:e.innerText,rect:rect(e)}))};
    }""")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case', default='', help='Run case names containing this string.')
    parser.add_argument('--browser', choices=['bundled','system'], default='bundled',
                        help='Bundled Playwright Chromium by default; system executable is an explicit separate run.')
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    if out.exists():
        parser.error('Choose a new evidence directory; old attempts must be preserved.')
    out.mkdir(parents=True)
    (out / 'screenshots').mkdir()
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True).stdout.strip()
    report = {'root': str(root), 'head': head,
              'startedAt': datetime.now(timezone.utc).isoformat(),
              'before': hashes(root), 'cases': [],
              'scope': 'Real app sources, synthetic fields and disposable Chromium profiles; no user browser or data.'}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(root)))
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = 'http://127.0.0.1:' + str(server.server_port) + '/index.html'
    report['url'] = url

    def run(browser, name, callback, *, size=(1440, 900), touch=False):
        if args.case and args.case not in name:
            return
        record = {'name': name, 'pageerrors': [], 'dialogs': [], 'viewport': list(size)}
        context = page = None
        try:
            context = browser.new_context(service_workers='block',
                viewport={'width': size[0], 'height': size[1]}, has_touch=touch, is_mobile=touch)
            install_bootstrap(context)
            page = context.new_page()
            page.set_default_timeout(8000)
            page.on('pageerror', lambda error: record['pageerrors'].append(str(error)))
            def dialog(d):
                record['dialogs'].append({'type': d.type, 'message': d.message})
                if record.get('dismissConfirm') and d.type == 'confirm':
                    d.dismiss()
                else:
                    d.accept()
            page.on('dialog', dialog)
            page.goto(url, wait_until='domcontentloaded')
            wait_bootstrap(page)
            page.wait_for_timeout(450)
            instrument(page)
            record['observations'] = callback(page, context, record)
            assert_fixture_requests(context)
            assert not record['pageerrors'], record['pageerrors']
            record['status'] = 'PASS'
        except Exception as error:
            record.update(status='PRODUCT_FAIL' if isinstance(error, (AssertionError, PlaywrightTimeoutError)) else 'TEST_HARNESS_FAIL',
                          error=str(error), trace=traceback.format_exc())
            if page:
                try:
                    image_path = out / 'screenshots' / (name + '-failure.png')
                    page.screenshot(path=str(image_path))
                    record['screenshot'] = str(image_path)
                    record['visibleText'] = page.locator('#modalBox').inner_text()[:1600]
                except Exception:
                    pass
        finally:
            if context:
                context.close()
            report['cases'].append(record)
            print(name, record['status'], record.get('error', '')[:250], flush=True)

    def legacy_completion(page, context, record):
        legacy_open(page)
        fill_legacy(page)
        before = financial_snapshot(page)
        submit_legacy_review(page)
        page.wait_for_timeout(150)
        assert page.evaluate('S.onboarding.done'), 'Reviewed legacy setup refused its valid confirmed write'
        durable = page.evaluate("""() => {
          const raw=localStorage.getItem(LSKEY),disk=JSON.parse(raw),event=disk.transitionLog.find(r=>r.fase==='início de período');
          return {done:disk.onboarding.done,consent:disk.onboarding.consentAccepted,
            annual:disk.params.refA,ep:event?.resumo.equityProtector,objective:event?.resumo.objetivoAnual,
            secretAbsent:!raw.includes('SYNTHETIC-SESSION-ONLY'),institution:getSavedOnboardingStepStatus('instit'),
            writes:window.__firstAccessWrites.filter(r=>r.key===LSKEY).length,
            phases:disk.phases.length};
        }""")
        assert durable['done'] and durable['consent'] and durable['phases'] == 6
        assert durable['annual'] is None and durable['objective'] is None, 'Unavailable annual reference was fabricated'
        assert durable['ep'] == 7800, 'Existing finite protector reference changed'
        assert durable['secretAbsent'], 'Investor password leaked to persisted state'
        assert durable['writes'] == 1, 'Final confirmation must make exactly one document write'
        page.reload()
        wait_bootstrap(page)
        assert page.evaluate("S.onboarding.done && getSavedOnboardingStepStatus('instit')==='complete'"), 'Reload downgraded durable account identification because session password is absent'
        assert page.evaluate("!S.onboarding.investorPassword")
        page.evaluate("closeModal();openOnboardingModal('edit')")
        page.locator('#obOperador').wait_for(state='visible')
        assert page.locator('#obOperador').input_value() == 'Operador sintético'
        legacy_step(page, 'instit')
        assert page.locator('#obInvestorPassword').input_value() == ''
        legacy_step(page, 'risk')
        assert page.locator('[data-obprof]').count() > 0, 'Saved account cannot be reviewed without a session secret'
        return {'durable': durable, 'reviewBeforeWrite': before['durable'] != page.evaluate('localStorage.getItem(LSKEY)'), 'reload': True, 'editWithoutPassword': True}

    def legacy_validation(page, context, record):
        legacy_open(page)
        before = financial_snapshot(page)
        page.locator('#obStepNext').click()
        assert active_step(page) == 'ident', 'Next accepted an incomplete identification'
        errors = page.locator('#modalBox [aria-invalid="true"]')
        assert errors.count() > 0, 'Invalid fields lack an inline accessible state'
        assert page.locator('#obErrorSummary').is_visible(), 'Validation does not expose its linked error summary'
        assert page.evaluate("document.getElementById('modalBox').contains(document.activeElement)"), 'Validation focus escaped form'
        page.locator('#obOperador').fill('Operador sintético')
        page.locator('#obSupervisor').fill('Supervisora sintética')
        page.locator('#obSaldo').fill('10000')
        page.locator('#obData').fill('2026-10-07')
        page.locator('#obStepNext').click()
        assert active_step(page) == 'instit'
        page.locator('#obStepPrev').click()
        assert page.locator('#obOperador').input_value() == 'Operador sintético'
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.locator('#obOperador').input_value() == 'Operador sintético'
        assert_unchanged(page, before, 'Inline validation, next/back and resize')
        return {'inlineValidation': True, 'draftPreserved': True, 'navigationWrites': 0}

    def legacy_keyboard_and_close(page, context, record):
        legacy_open(page)
        page.locator('#obOperador').fill('Rascunho sintético')
        before = financial_snapshot(page)
        page.locator('#obOperador').focus()
        sequence = []
        for _ in range(32):
            page.keyboard.press('Tab')
            focus = page.evaluate("({id:document.activeElement.id,inForm:document.getElementById('modalBox').contains(document.activeElement)})")
            sequence.append(focus)
            assert focus['inForm'], 'Tab escaped modal: ' + str(focus)
        legacy_step(page, 'instit')
        page.locator('[data-obinsttype="broker"]').click()
        page.locator('[data-obbroker]').first.click()
        page.locator('#obBrokerLogin').fill('10000001')
        page.locator('#obInvestorPassword').fill('SYNTHETIC-DRAFT-SECRET')
        backup = page.evaluate("async () => await dgBuildBackupBlob(1,'synthetic-draft.json','2026-10-07T12:00:00Z').text()")
        assert 'SYNTHETIC-DRAFT-SECRET' not in backup, 'Draft backup included a session secret'
        # Closing deliberately suspends the form in RAM; it is not a request
        # to discard it, so this path does not need a destructive confirmation.
        page.keyboard.press('Escape')
        assert not page.locator('#modalOverlay').is_visible()
        page.evaluate('openOnboardingModal()')
        assert page.locator('#obOperador').input_value() == 'Rascunho sintético', 'RAM resume lost draft after leaving form'
        legacy_step(page, 'instit')
        assert page.locator('#obBrokerLogin').input_value() == '10000001'
        assert page.locator('#obInvestorPassword').input_value() == '', 'RAM resume retained a session secret'
        assert_unchanged(page, before, 'Suspending and resuming the RAM draft')
        return {'tabSequence': sequence, 'closePreservesRAM': True, 'ramResume': True,
                'passwordNotReopenedOrBackedUp':True,'writes': 0}

    def legacy_risk_states(page, context, record):
        legacy_open(page)
        before = financial_snapshot(page)
        legacy_step(page, 'risk')
        assert page.locator('#obRiskStepWrap').inner_text().strip(), 'Unavailable risk step is a blank page'
        assert 'institui' in page.locator('#obRiskStepWrap').inner_text().lower(), 'Unavailable step has no prerequisite explanation'
        legacy_step(page, 'ident')
        page.locator('#obOperador').fill('Operador sintético')
        page.locator('#obSupervisor').fill('Supervisora sintética')
        page.locator('#obSaldo').fill('10000')
        page.locator('#obData').fill('2026-10-07')
        legacy_step(page, 'instit')
        page.locator('[data-obinsttype="broker"]').click()
        page.locator('[data-obbroker]').first.click()
        for selector, value in [('#obBrokerLogin','10000001'),('#obBrokerServer','SYNTHETIC-DEMO'),('#obPlataforma','MetaTrader 5'),('#obAlav','1:100')]:
            page.locator(selector).fill(value)
        legacy_step(page, 'risk')
        text = page.locator('#obRiskStepWrap').inner_text()
        assert 'undefined' not in text and 'quadrifás' not in text.lower(), 'Active six-phase matrix has obsolete/undefined text'
        page.locator('[data-obprof="longevity"]').click()
        text = page.locator('#obRiskStepWrap').inner_text()
        assert 'pend' in text.lower(), 'Pending satellite profile is not explained'
        # The UI must not turn missing participation into a nominal zero.
        assert 'Participação 0%' not in text and 'Participação: 0%' not in text
        assert_unchanged(page, before, 'Risk previews')
        return {'pendingExplicit': True, 'noUndefined': True, 'noImplicitPasswordGate': True, 'writes': 0}

    def legacy_touch_font_and_labels(page, context, record):
        legacy_open(page)
        page.locator('#obOperador').fill('Rascunho touch')
        before = financial_snapshot(page)
        measures = []
        for scale in ['0', '2']:
            page.evaluate("scale => document.documentElement.dataset.fs=scale", scale)
            page.wait_for_timeout(30)
            measured = audit_layout(page)
            assert not measured['globalOverflow']
            for item in measured['fields']:
                assert item['rect']['h'] >= 47.9, ('touch target',item)
                assert float(item['font'].removesuffix('px')) >= (19.9 if scale=='2' else 15.9), ('font preference',item)
            for control in ['obClose','obStepPrev','obStepNext']:
                target = page.locator('#' + control)
                if target.is_visible():
                    rect = target.bounding_box()
                    assert rect['width'] >= 47.9 and rect['height'] >= 47.9, ('touch action',control,rect)
            labels = page.locator('#obOperador,#obSupervisor,#obSaldo,#obData').evaluate_all('els=>els.filter(e=>e.type!=="hidden").map(e=>({id:e.id,labels:[...e.labels].map(l=>l.innerText)}))')
            assert all(item['labels'] for item in labels), labels
            assert page.locator('#obOperador').input_value() == 'Rascunho touch'
            measures.append({'fontPreference':scale,'labels':labels,**measured})
        assert_unchanged(page, before, 'Touch adaptation and font preference presentation')
        path = out / 'screenshots' / 'legacy-touch-enlarged-font.png'
        page.screenshot(path=str(path))
        return {'measurements':measures,'screenshot':str(path),'noFinancialWrite':True}

    def legacy_viewports(page, context, record):
        legacy_open(page)
        page.locator('#obOperador').fill('Rascunho preservado')
        observations = []
        before = financial_snapshot(page)
        for layout in ['sidebar', 'topbar', 'glass', 'submenu']:
            page.evaluate('layout => mountNavigationLayout(layout)', layout)
            for width, height in [(1440,900),(1024,600),(390,844),(320,640)]:
                page.set_viewport_size({'width': width, 'height': height})
                for theme in ['light', 'dark']:
                    page.evaluate("theme => { S.theme=theme;applyTheme(); }", theme)
                    measured = audit_layout(page)
                    assert not measured['globalOverflow'], (layout,width,theme,'page overflow')
                    assert measured['box']['x'] >= -1 and measured['box']['right'] <= width + 1, (layout,width,theme,'dialog overflow')
                    assert measured['box']['y'] >= -1 and measured['box']['bottom'] <= height + 1, (layout,width,theme,'dialog height overflow')
                    assert measured['dialog'] == 'dialog' and measured['ariaModal'] == 'true'
                    persistent_actions = [item for item in measured['actions'] if item['id'] in ['obClose','obStepPrev','obStepNext']]
                    assert all(item['rect']['y']>=-1 and item['rect']['bottom']<=height+1 for item in persistent_actions), (layout,width,theme,'header/footer action outside viewport',persistent_actions)
                    if width <= 390:
                        text_fields = [x for x in measured['fields'] if x['id'] in ['obOperador','obSupervisor','obSaldo','obData']]
                        assert all(x['rect']['w'] >= width - 120 for x in text_fields), (width,'fields remain narrow',text_fields)
                    assert page.locator('#obOperador').input_value() == 'Rascunho preservado'
                    observations.append({'layout':layout,'theme':theme,**measured})
        # Layout/theme preference actions are explicit synthetic setup; only the
        # unchanged onboarding financial draft and durable financial document
        # are asserted here. No claim that preferences themselves write nothing.
        assert page.evaluate('localStorage.getItem(LSKEY)') == before['durable']
        path = out / 'screenshots' / 'legacy-mobile-layout.png'
        page.screenshot(path=str(path))
        return {'measurements': observations, 'screenshot': str(path), 'draftPreserved': True}

    def welcome_buttons(page):
        assert page.locator('#jpwWelcome').count() == 1, 'Fresh first access did not show the welcome'
        for control in ['jpwWelcomeStart', 'jpwWelcomeRestore', 'jpwWelcomeExplore', 'jpwWelcomeClose']:
            assert page.locator('#' + control).is_visible(), 'Missing welcome action: ' + control
        text = page.locator('#jpwWelcome').inner_text().lower()
        assert 'navegador' in text and 'backup' in text, 'Welcome does not explain local storage and recovery'

    def welcome_explore(page, context, record):
        welcome_buttons(page)
        before = financial_snapshot(page)
        page.locator('#jpwWelcomeExplore').click()
        assert not page.locator('#modalOverlay').is_visible()
        assert_unchanged(page, before, 'Explore without preparation')
        assert page.evaluate('!S.onboarding.done && !S.onboarding.consentAccepted')
        assert page.evaluate('Object.keys(S.forex.accountContexts?.accounts||{}).length') == 0
        page.evaluate('JPWFirstAccess.open()')
        welcome_buttons(page)
        assert_unchanged(page, before, 'Reopen welcome')
        return {'threePaths': True, 'exploreWrites': 0, 'preparationNotImplied': True, 'consentNotImplied': True}

    def welcome_manual_registration(page, context, record):
        welcome_buttons(page)
        before = financial_snapshot(page)
        initial_count = page.evaluate('S.accounts.length')
        page.locator('#jpwWelcomeStart').click()
        page.locator('#jpwWelcomeForex').wait_for(state='visible')
        assert_unchanged(page, before, 'Choosing the first task')
        page.locator('#jpwWelcomeForex').click()
        page.locator('#fxcwNext').wait_for(state='visible')
        assert_unchanged(page, before, 'Opening current account writer')
        technical_events = page.evaluate('window.__firstAccessWrites')
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-name').fill('Conta nova sintética')
        page.locator('#fxcr-login').fill('40004004')
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-platform').select_option('MetaTrader 5')
        page.locator('#fxcr-currency').fill('USD')
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-profileKey').select_option('base')
        page.locator('#fxcwNext').click()
        assert_unchanged(page, before, 'Reviewing unconfirmed account registration')
        page.locator('#fxcRegistrationSave').click()
        page.locator('#fxcwSuccess').wait_for(state='visible')
        registered = page.evaluate("""() => ({count:S.accounts.length,
          contexts:Object.keys(S.forex.accountContexts?.accounts||{}).length,
          receipts:S.fxConsolidated.receipts.length,onboarding:S.onboarding.done,
          consent:S.onboarding.consentAccepted,
          writes:window.__firstAccessWrites.filter(r=>r.key===LSKEY).length,
          account:S.accounts.find(a=>a.platformLogin==='40004004')?.forexAccountId})""")
        assert registered['count'] == initial_count + 1 and registered['account']
        assert registered['contexts'] == 0 and registered['receipts'] == 0
        assert not registered['onboarding'] and not registered['consent']
        assert registered['writes'] == 1, 'Account registration is not a single separate confirmation'
        page.locator('#fxcwPrepare').click()
        page.locator('#fxcSetupDialog').wait_for(state='visible')
        assert page.locator('#fxcs-si').input_value() == '', 'New period inferred SI from a balance'
        page.locator('#fxcs-start').fill('2026-10-07')
        page.locator('#fxcs-si').fill('10000')
        page.locator('#fxcs-confirm-period').check()
        page.locator('#fxcs-save-period').click()
        page.locator('#fxcSetupObservationForm').wait_for(state='visible')
        period = page.evaluate("""accountId => {
          const account=S.forex.accountContexts.accounts[accountId],period=Object.values(account.periods)[0];
          return {count:Object.keys(account.periods).length,si:period.si,currency:period.currency,
            phases:period.phases.length,observation:!!S.forex.accounts[accountId],
            writes:window.__firstAccessWrites.filter(r=>r.key===LSKEY).length,
            done:S.onboarding.done,consent:S.onboarding.consentAccepted};
        }""", registered['account'])
        assert period['count'] == 1 and period['si'] == 10000 and period['currency'] == 'USD' and period['phases'] == 6
        assert not period['observation'] and not period['done'] and not period['consent']
        assert period['writes'] == 2, 'Account and period did not remain two explicit confirmations'
        page.locator('#fxcs-close').click()
        page.reload()
        wait_bootstrap(page)
        assert page.evaluate("id => !!S.accounts.find(a=>a.forexAccountId===id) && Object.keys(S.forex.accountContexts.accounts[id].periods).length===1", registered['account'])
        return {'registration':registered, 'period':period, 'reload':True, 'noAutomaticObservationOrConsent':True,
                'technicalStorageEventsBeforeConfirmation':technical_events}

    def welcome_backup_validation(page, context, record):
        welcome_buttons(page)
        before = financial_snapshot(page)
        page.locator('#jpwWelcomeRestore').click()
        partial = {'tipo':'jpwealth_partial_audit','params':{'saldoIni':9999},'contas':[]}
        page.locator('#jpwWelcomeFile').set_input_files({'name':'synthetic-partial.json','mimeType':'application/json','buffer':json.dumps(partial).encode()})
        page.wait_for_timeout(300)
        assert_unchanged(page, before, 'Refusing a partial audit as complete backup')
        assert page.evaluate('!S.onboarding.done && !S.onboarding.consentAccepted')
        if not page.locator('#jpwWelcomeFile').count():
            page.evaluate('JPWFirstAccess.open()')
        # Generate an actual complete format with the app, then reset only the
        # synthetic marker through its writer to distinguish successful restore.
        payload = page.evaluate("""async () => {
          S.syntheticFirstAccessBackup={marker:'source',version:1};if(save()!==true)throw Error('Synthetic save failed');
          return await dgBuildBackupBlob(1,'synthetic-complete.json','2026-10-07T12:00:00Z').text();
        }""")
        page.evaluate("S.syntheticFirstAccessBackup={marker:'destination',version:1};if(save()!==true)throw Error('Synthetic destination save failed')")
        page.locator('#jpwWelcomeFile').set_input_files({'name':'synthetic-complete.json','mimeType':'application/json','buffer':payload.encode()})
        page.wait_for_function("S.syntheticFirstAccessBackup?.marker==='source'&&!S.workspaceRecovery?.pending")
        assert page.evaluate('!S.onboarding.done && !S.onboarding.consentAccepted'), 'Restoring a backup accepted a new normative consent'
        page.reload()
        wait_bootstrap(page)
        assert page.evaluate("S.syntheticFirstAccessBackup.marker==='source'")
        return {'partialRefusedWithoutWrite':True, 'actualCompleteFormatRestored':True, 'reload':True, 'consentNotImplied':True}

    def legacy_storage_refused_retry(page, context, record, failure='quota'):
        legacy_open(page)
        fill_legacy(page)
        before = page.evaluate('localStorage.getItem(LSKEY)')
        page.evaluate("""failure => {
          window.__firstAccessStorageSet = Storage.prototype.setItem;
          Storage.prototype.setItem = function(key,value) {
            if(key===LSKEY){
              if(failure==='quota')throw new DOMException('Synthetic quota refusal','QuotaExceededError');
              return;
            }
            return window.__firstAccessStorageSet.call(this,key,value);
          };
        }""", failure)
        submit_legacy_review(page)
        assert page.evaluate('localStorage.getItem(LSKEY)') == before
        assert page.evaluate('!S.onboarding.done')
        assert page.locator('#modalOverlay').is_visible()
        assert not page.evaluate('jpWealthPersistenceOutcomeIsUnknown()'), 'Known quota refusal incorrectly became unknown'
        page.evaluate('() => { Storage.prototype.setItem=window.__firstAccessStorageSet; }')
        # Use the still-open final review; neither rebuilding nor retyping is a
        # substitute for preserving the user's reviewed draft after refusal.
        assert page.locator('#obSummaryConfirm').is_visible()
        page.locator('#obSummaryConfirm').click()
        assert page.evaluate('S.onboarding.done && JSON.parse(localStorage.getItem(LSKEY)).onboarding.done')
        return {'failure':failure, 'refusedBeforeWrite':True, 'draftRetry':True, 'noFalseSuccess':True}

    def legacy_storage_unknown_no_retry(page, context, record):
        legacy_open(page)
        fill_legacy(page)
        page.evaluate("""() => {
          window.__firstAccessStorageSet=Storage.prototype.setItem;
          window.__firstAccessStorageGet=Storage.prototype.getItem;
          window.__firstAccessHasWritten=false;
          Storage.prototype.setItem=function(key,value){
            const result=window.__firstAccessStorageSet.call(this,key,value);
            if(key===LSKEY)window.__firstAccessHasWritten=true;
            return result;
          };
          Storage.prototype.getItem=function(key){
            if(key===LSKEY&&window.__firstAccessHasWritten)throw new Error('Synthetic post-write readback interruption');
            return window.__firstAccessStorageGet.call(this,key);
          };
        }""")
        submit_legacy_review(page)
        assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()'), 'Readback interrupted after writing was not UNKNOWN'
        writes = page.evaluate('window.__firstAccessWrites.filter(r=>r.key===LSKEY).length')
        page.evaluate('() => { Storage.prototype.getItem=window.__firstAccessStorageGet; }')
        durable = page.evaluate('JSON.parse(localStorage.getItem(LSKEY)).onboarding.done')
        assert durable, 'Synthetic possible write did not really reach storage'
        confirm = page.locator('#obSummaryConfirm')
        if confirm.is_visible() and not confirm.is_disabled():
            confirm.click()
        assert page.evaluate('window.__firstAccessWrites.filter(r=>r.key===LSKEY).length') == writes, 'UNKNOWN allowed a blind duplicate write'
        assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()')
        return {'unknownExplicit':True, 'possibleWriteObserved':True, 'writesBeforeRetry':writes, 'duplicateWritePrevented':True}

    def legacy_cross_tab(page, context, record):
        legacy_open(page)
        fill_legacy(page)
        other = context.new_page()
        other.goto(url, wait_until='domcontentloaded')
        wait_bootstrap(other)
        durable = other.evaluate("""() => {
          S.syntheticConcurrentChange={owner:'second-tab',version:1};
          if(save()!==true)throw Error('Synthetic second-tab writer refused');
          return localStorage.getItem(LSKEY);
        }""")
        page.wait_for_timeout(150)
        if page.locator('#modalConfirm').is_visible():
            page.locator('#modalConfirm').click()
            if page.locator('#obSummaryAccept').is_visible():
                page.locator('#obSummaryAccept').check()
                page.locator('#obSummaryConfirm').click()
        assert page.evaluate('localStorage.getItem(LSKEY)') == durable, 'First tab overwrote a newer confirmed document'
        assert page.evaluate('!S.onboarding.done'), 'Stale first tab announced setup completion'
        if page.locator('#obOperador').count():
            assert page.locator('#obOperador').input_value() == 'Operador sintético'
        return {'newerWriteRetained':True, 'staleSetupRefused':True, 'draftNotPromoted':True}

    def legacy_restore_invalidates_ram(page, context, record):
        # The backup is built before the draft and contains the same confirmed
        # financial state. Context identity must still change on restoration.
        payload = page.evaluate("async () => await dgBuildBackupBlob(1,'synthetic-same-state.json','2026-10-07T12:00:00Z').text()")
        legacy_open(page)
        page.locator('#obOperador').fill('Rascunho anterior à restauração')
        page.keyboard.press('Escape')
        old_epoch = page.evaluate('sessionEpochRead()')
        before_barrier_epoch = page.evaluate('jpWealthPersistenceEpoch()')
        page.evaluate('JPWFirstAccess.open()')
        page.locator('#jpwWelcomeFile').set_input_files({'name':'synthetic-same-state.json','mimeType':'application/json','buffer':payload.encode()})
        page.wait_for_function('old => sessionEpochRead()!==old && !S.workspaceRecovery?.pending', arg=old_epoch)
        legacy_open(page)
        assert page.locator('#obOperador').input_value() != 'Rascunho anterior à restauração', 'Same-state restore reopened a draft from the previous generation'
        assert page.evaluate('!S.onboarding.done && !S.onboarding.consentAccepted')
        return {'sameConfirmedStateRestore':True,'generationChanged':True,'oldRAMDraftNotReused':True,'noConsentPromotion':True,
                'baseGenerationBefore':old_epoch,'baseGenerationAfter':page.evaluate('sessionEpochRead()'),
                'barrierEpochBefore':before_barrier_epoch,'barrierEpochAfter':page.evaluate('jpWealthPersistenceEpoch()')}

    def legacy_stale_summary_refused(page, context, record):
        legacy_open(page)
        fill_legacy(page)
        before = financial_snapshot(page)
        page.locator('#modalConfirm').click()
        page.locator('#obSummaryAccept').check()
        page.evaluate('window.__obsoleteSummaryButton=document.getElementById("obSummaryConfirm")')
        legacy_step(page, 'ident')
        page.locator('#obOperador').fill('Operador revisado sintético')
        # Replay an already-created DOM callback after its review was replaced.
        # This is the real event handler, not a substitute financial/writer API.
        page.evaluate('() => { window.__obsoleteSummaryButton.click(); }')
        assert page.evaluate('!S.onboarding.done'), 'Obsolete reviewed payload was accepted after the draft changed'
        assert_unchanged(page, before, 'Obsolete summary confirmation')
        legacy_step(page, 'consent')
        page.locator('#modalConfirm').click()
        assert not page.locator('#obSummaryAccept').is_checked(), 'New review inherited a previous acceptance'
        page.locator('#obSummaryAccept').check()
        page.locator('#obSummaryConfirm').click()
        assert page.evaluate("S.onboarding.done && S.onboarding.operador==='Operador revisado sintético'")
        return {'staleRealCallbackRefused':True,'acceptanceNotReused':True,'freshReviewConfirmed':True}

    def legacy_session_end_invalidates_ram(page, context, record):
        legacy_open(page)
        page.locator('#obOperador').fill('Rascunho antes do fim da sessão')
        page.keyboard.press('Escape')
        old_generation = page.evaluate('sessionEpochRead()')
        page.locator('#finalizeSessionBtn').click()
        backup_path = None
        if page.locator('#sessionExport').is_visible():
            with page.expect_download() as info:
                page.locator('#sessionExport').click()
            backup_path = out / 'session-generated-synthetic-backup.json'
            info.value.save_as(str(backup_path))
            payload = json.loads(backup_path.read_text())
            assert page.evaluate('payload => !!JPWBackup.inspect(payload)', payload), 'Generated safety backup did not pass its actual format inspector'
            page.locator('#sessionExportAcknowledged').check()
            page.locator('#sessionExportContinue').click()
        else:
            page.locator('#sessionHasCopy').click()
        page.locator('#sessionProceed').click()
        page.locator('#sessionDeletePhrase').fill('ENCERRAR SESSÃO')
        page.locator('#sessionDeleteConfirm').click()
        page.wait_for_function("document.getElementById('sessionNotice').textContent.includes('Sessão finalizada')")
        legacy_open(page)
        assert page.locator('#obOperador').input_value() != 'Rascunho antes do fim da sessão', 'Finalized session reopened its old RAM draft'
        assert page.evaluate('!S.onboarding.done && !S.onboarding.consentAccepted')
        return {'sessionEndedThroughRealUI':True,'oldDraftNotReused':True,
                'generationBefore':old_generation,'generationAfter':page.evaluate('sessionEpochRead()'),
                'actualSafetyBackup':str(backup_path) if backup_path else None}

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**(launch_options() if args.browser=='system' else {'headless':True}))
            report['browser'] = browser.version
            report['browserSelection'] = args.browser
            run(browser, 'welcome-three-paths-explore-zero-write', welcome_explore)
            run(browser, 'welcome-current-registration-separate-period-reload', welcome_manual_registration)
            run(browser, 'welcome-complete-backup-and-partial-rejection', welcome_backup_validation)
            run(browser, 'legacy-complete-real-confirmation-reload-edit', legacy_completion)
            run(browser, 'legacy-mobile-complete-real-confirmation-reload-edit', legacy_completion, size=(390,844), touch=True)
            run(browser, 'legacy-inline-validation-next-back-resize', legacy_validation)
            run(browser, 'legacy-keyboard-suspend-and-ram-resume', legacy_keyboard_and_close)
            run(browser, 'legacy-risk-unavailable-and-pending', legacy_risk_states)
            run(browser, 'legacy-storage-refused-review-retry', legacy_storage_refused_retry)
            run(browser, 'legacy-storage-noop-review-retry', partial(legacy_storage_refused_retry,failure='noop'))
            run(browser, 'legacy-storage-unknown-no-blind-retry', legacy_storage_unknown_no_retry)
            run(browser, 'legacy-two-tabs-newer-write-not-overwritten', legacy_cross_tab)
            run(browser, 'legacy-same-state-restore-invalidates-ram', legacy_restore_invalidates_ram)
            run(browser, 'legacy-stale-summary-real-callback-refused', legacy_stale_summary_refused)
            run(browser, 'legacy-session-end-invalidates-ram', legacy_session_end_invalidates_ram)
            run(browser, 'legacy-four-layouts-themes-viewports', legacy_viewports)
            run(browser, 'legacy-touch-font-preference-and-labels', legacy_touch_font_and_labels, size=(390,844), touch=True)
            browser.close()
    except BaseException as error:
        report['runtimeFailure'] = {'type':type(error).__name__,'message':str(error),'trace':traceback.format_exc()}
        raise
    finally:
        server.shutdown()
        server.server_close()
        report['after'] = hashes(root)
        report['sourcesUnchanged'] = report['before'] == report['after']
        report['counts'] = dict(Counter(row['status'] for row in report['cases']))
        report['limitations'] = [
            {'name':'Native browser zoom 200%', 'status':'NOT_RUN', 'reason':'Viewport reflow is measured separately; no headless browser-chrome zoom evidence.'},
            {'name':'Safari and screen reader', 'status':'NOT_RUN', 'reason':'No independent native environment executed by this suite.'},
        ]
        report['result'] = ('ENVIRONMENT_ERROR' if not report['sourcesUnchanged'] or report.get('runtimeFailure') else
                            'PASS' if report['cases'] and all(row['status']=='PASS' for row in report['cases']) else
                            'PRODUCT_FAIL' if any(row['status']=='PRODUCT_FAIL' for row in report['cases']) else
                            'TEST_HARNESS_FAIL')
        (out / 'receipt.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(report['result'], 'receipt:', out / 'receipt.json', flush=True)
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
