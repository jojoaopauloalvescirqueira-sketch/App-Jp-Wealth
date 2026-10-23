"""Supplemental frozen-candidate notification behavior; synthetic contexts only.

This does not change or replace the permanent quality gate. It explicitly opens
and uses the notification centre in each distribution, rather than inferring its
behavior from build or Planning-only tests.
"""
from datetime import datetime, timezone
from functools import partial
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import tempfile
import shutil
import traceback

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools'))
import notification_center_test as h
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
BUILD = '8b0b231a1b0c41b7'
CHROME = '/Users/joaoalvescirqueira/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
FILES = ['index.html', 'build-id.js', 'sw.js',
         'src/js/40-app/18-notification-center.js',
         'src/js/30-accounting/06-planning/02-state.js',
         'src/js/30-accounting/06-planning/03-ui.js',
         'src/js/10-domain/18-execution-board-model.js',
         'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']


def identity():
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES}


def behavior(page, label, accounts):
    page.set_default_timeout(10000)
    h.instrument(page)
    before = h.snapshot(page)
    requests = []
    page.on('request', lambda request: requests.append(request.url))
    h.refresh(page)
    h.open_center(page)
    count = h.actionable_count_oracle(page)
    expected = ['planning:close:' + a['id'] + ':' + a['planId'] for a in accounts]
    assert all(item in h.ids(page) for item in expected), h.ids(page)
    row = page.locator('[data-notification-id="' + expected[1] + '"]')
    assert accounts[1]['name'] in row.inner_text()
    row.locator('summary').click()
    assert row.locator('details').evaluate('e=>e.open')
    h.refresh(page)
    assert row.locator('details').evaluate('e=>e.open'), 'Refresh lost the expanded diagnosis'
    assert h.actionable_count_oracle(page) == count
    page.screenshot(path=str(OUT / (label + '-notification.png')))
    page.locator('#notificationClose').click()
    page.locator('#headerNotificationsBtn').click()
    assert h.actionable_count_oracle(page) == count
    page.locator('#notificationArea').select_option('planning')
    assert set(h.ids(page)) == set(expected)
    row.locator('[data-notification-go]').click()
    page.wait_for_function("JPWNavigation.current().primary==='planning' && JPWPlanning.ui.getView()==='monthly'")
    assert page.locator('[data-pl-account]').input_value() == accounts[1]['id']
    assert page.locator('[data-pl-month]').input_value() == '2026-05'
    assert page.locator('[data-pl-grid-month="2026-05"]').is_visible()
    h.unchanged(page, before)
    assert requests == [], requests
    assert not page.notification_errors, page.notification_errors
    return {'active_causes': count, 'planning_causes': len(expected),
            'disclosure_preserved_after_refresh': True,
            'consult_does_not_resolve': True, 'filter_preserved_context': True,
            'explicit_account_and_prior_month': True,
            'financial_and_browser_storage_unchanged': True,
            'extra_requests': requests, 'page_errors': page.notification_errors}


def pwa_boot(browser, url):
    context = browser.new_context(viewport={'width': 1440, 'height': 900},
                                  timezone_id='UTC', service_workers='allow')
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true;window.__notificationXss=0')
    page = context.new_page()
    page.clock.set_fixed_time(h.NOW)
    page.notification_errors = []
    page.on('pageerror', lambda error: page.notification_errors.append(str(error)))
    page.on('dialog', lambda dialog: dialog.dismiss())
    page.goto(url, wait_until='load')
    wait_bootstrap(page)
    page.evaluate('closeModal()')
    page.wait_for_function('!!navigator.serviceWorker.controller', timeout=45000)
    page.wait_for_function("caches.keys().then(async keys=>{const key=keys.find(k=>k.startsWith('jp-wealth-'));return !!key && !!(await (await caches.open(key)).match('/src/js/40-app/18-notification-center.js'));})", timeout=45000)
    return context, page


def main():
    before = identity()
    server = h.ThreadingHTTPServer(('127.0.0.1', 0), partial(h.Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = 'http://127.0.0.1:' + str(server.server_port) + '/index.html'
    results = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=CHROME)
            for label, destination in [('http', url), ('modular-file', (ROOT / 'index.html').as_uri()),
                                       ('portable-file', (ROOT / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').as_uri()),
                                       ('pwa-offline', url)]:
                context = None
                isolated = None
                try:
                    if label == 'portable-file':
                        isolated = tempfile.TemporaryDirectory(prefix='jpw-notification-portable-')
                        portable = Path(isolated.name) / 'JP-Wealth.html'
                        shutil.copyfile(ROOT / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html', portable)
                        assert len(list(Path(isolated.name).iterdir())) == 1
                        destination = portable.as_uri()
                    if label == 'pwa-offline':
                        context, page = pwa_boot(browser, destination)
                    else:
                        context, page, _ = h.prepare(browser, destination)
                    accounts = h.seed_planning(page)
                    if label == 'pwa-offline':
                        context.set_offline(True)
                        context.unroute_all(behavior='wait')
                        page.reload(wait_until='load')
                        page.wait_for_function('window.JPWPlanning?.queries.pendingActions && window.JPWNotifications')
                        page.wait_for_function('!ffNewsInFlight')
                        page.evaluate('closeModal()')
                        assert page.evaluate('navigator.onLine') is False
                        assert page.evaluate('!!navigator.serviceWorker.controller')
                        assert page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 2
                    observed_build = page.evaluate('typeof JP_WEALTH_BUILD_ID!=="undefined"?JP_WEALTH_BUILD_ID:null')
                    # build-id.js uses the distribution's canonical public name.
                    declared = observed_build
                    assert observed_build == BUILD, {'expected': BUILD, 'observed': observed_build}
                    data = behavior(page, label, accounts)
                    data.update({'offline': label == 'pwa-offline', 'observed_build': observed_build,
                                 'declared_build': declared, 'url_scheme': destination.split(':', 1)[0],
                                 'isolated_single_html': label == 'portable-file'})
                    results.append({'mode': label, 'result': 'PASS', 'evidence': data})
                except Exception as error:
                    results.append({'mode': label, 'result': 'PRODUCT_FAIL' if isinstance(error, AssertionError) else 'TEST_HARNESS_FAIL',
                                    'evidence': str(error), 'traceback': traceback.format_exc()})
                finally:
                    if context:
                        context.close()
                    if isolated:
                        isolated.cleanup()
                print(json.dumps(results[-1], ensure_ascii=False), flush=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    after = identity()
    report = {'at_utc': datetime.now(timezone.utc).isoformat(), 'candidate_build': BUILD,
              'scope': 'Supplemental notification interaction in four distributions; synthetic contexts only',
              'source_before': before, 'source_after': after, 'source_unchanged': before == after,
              'results': results,
              'limits': ['Does not rerun all 30 notification or 20 efficiency cases in every distribution.',
                         'Does not replace the required FULL gate or demonstrate human understanding/accessibility acceptance.']}
    (OUT / 'distribution-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return int(before != after or len(results) != 4 or any(r['result'] != 'PASS' for r in results))


if __name__ == '__main__':
    raise SystemExit(main())
