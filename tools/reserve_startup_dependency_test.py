#!/usr/bin/env python3
"""Real HTTP startup regression for onboarding's shared reserve dependency.

Only the reserve script response is delayed. App scripts and calculations are
never replaced, errors are captured before navigation, and each load has fresh
synthetic browser storage. The canonical queue of 128 and normal deadlines stay
unchanged. External economic feeds use the established bootstrap fixtures.
"""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler
import json
import os
from pathlib import Path
import re
import threading
import time
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer

ROOT = Path(__file__).resolve().parents[1]
ENGINE = 'src/js/10-domain/00-forex-engine.js'
RESERVE = 'src/js/10-domain/07-reserve-requirements.js'
ONBOARDING = 'src/js/40-app/04-onboarding.js'
BOOT = 'src/js/40-app/06-boot.js'
PORTABLE = 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
RESERVE_SHA256 = '2c1a9d00cce4bda29e87be28398ae7fcd864e3c172f6df69b05246221a5d6a95'
DELAY_SECONDS = 1.2
TRACE = """(() => {
  window.__reserveStartupTrace = {errors: [], scripts: []};
  window.addEventListener('error', event => {
    __reserveStartupTrace.errors.push({message: event.message,
      stack: event.error && event.error.stack, at: performance.now()});
  });
  document.addEventListener('load', event => {
    if (event.target instanceof HTMLScriptElement && event.target.src) {
      __reserveStartupTrace.scripts.push({src: event.target.src,
        at: performance.now(), reserveType: typeof reserveRequirementsCalc});
    }
  }, true);
})();"""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def hashes(names):
    return {name: sha256((ROOT / name).read_bytes()) for name in names}


def check_sources():
    manifest = json.loads((ROOT / 'src/js/manifest.json').read_text())
    paths = [entry['path'] for entry in manifest['files']]
    index = (ROOT / 'index.html').read_text()
    tags = re.findall(r'<script\b([^>]*)\bsrc="([^"]+)"[^>]*></script>', index)
    declared = [path for _attributes, path in tags if path in paths]
    assert declared == paths, 'index and manifest must declare the same script sequence'
    assert [entry['order'] for entry in manifest['files']] == list(range(1, len(paths) + 1))
    assert paths.index(ENGINE) < paths.index(RESERVE) < paths.index(ONBOARDING) < paths.index(BOOT)
    for attributes, path in tags:
        if path in (ENGINE, RESERVE, ONBOARDING, BOOT):
            assert not re.search(r'\b(async|defer|type)\b', attributes), (path, attributes)
    reserve = (ROOT / RESERVE).read_bytes()
    assert sha256(reserve) == RESERVE_SHA256, 'reserve calculation bytes changed'
    assert next(entry for entry in manifest['files'] if entry['path'] == RESERVE)['sha256'] == RESERVE_SHA256
    # The official generator concatenates these dependency sources unchanged;
    # unrelated document links are deliberately embedded later by the generator.
    portable = (ROOT / PORTABLE).read_text()
    positions = []
    for path in (ENGINE, RESERVE, ONBOARDING, BOOT):
        source = (ROOT / path).read_text().rstrip()
        assert portable.count(source) == 1, ('portable dependency bytes differ', path)
        positions.append(portable.index(source))
    assert positions == sorted(positions), 'portable dependency order differs'
    return paths, {'manifestOrder': {path: paths.index(path) + 1
        for path in (ENGINE, RESERVE, ONBOARDING, BOOT)}, 'reserveSha256': sha256(reserve),
        'indexMatchesManifest': True, 'portableExactOrderedPayload': True}


class DelayedReserveHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        path = urlsplit(self.path).path.lstrip('/')
        if path == RESERVE:
            started = time.monotonic()
            delay = self.server.reserve_delay
            if delay:
                time.sleep(delay)
            super().do_GET()
            self.server.reserve_requests.append({'delaySeconds': delay,
                'elapsedSeconds': time.monotonic() - started})
            return
        super().do_GET()


def verify_load(browser, server, url, delay, portable=False):
    server.reserve_delay = delay
    request_start = len(server.reserve_requests)
    context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
    context.add_init_script(TRACE)
    install_bootstrap(context)
    # Unavailable quote fixture avoids the separate daily-reference writer;
    # this test uses a virgin document and does not seed or save a financial state.
    context.route('https://api.frankfurter.dev/v2/rate/**', lambda route:
        route.fulfill(status=200, content_type='application/json', body='{}'))
    events = {'pageerror': [], 'console': [], 'requestfailed': [], 'scripts': []}
    row = {'delaySeconds': delay, 'portable': portable, 'events': events}
    try:
        page = context.new_page()
        page.on('pageerror', lambda error: events['pageerror'].append(str(error)))
        page.on('console', lambda message: events['console'].append(
            {'type': message.type, 'text': message.text}))
        page.on('requestfailed', lambda request: events['requestfailed'].append(
            {'url': request.url, 'failure': request.failure}))

        def script_response(response):
            path = urlsplit(response.url).path.lstrip('/')
            if path in (RESERVE, ONBOARDING, BOOT):
                events['scripts'].append({'path': path, 'status': response.status,
                    'sha256': sha256(response.body())})

        page.on('response', script_response)
        page.goto(url + (PORTABLE if portable else ''), wait_until='load')
        wait_bootstrap(page)
        page.locator('#modalOverlay.show #obOperador').wait_for(state='visible')
        before = page.evaluate('({state: JSON.stringify(S), persisted: localStorage.getItem(LSKEY)})')
        assert page.evaluate('typeof reserveRequirementsCalc') == 'function'
        assert page.evaluate('Object.keys(S.forex?.accountContexts?.accounts || {}).length') == 0
        assert page.evaluate('S.dataGovernance.responsibility.accepted') is False
        page.locator('#obOperador').fill('Operador sintético de regressão')
        page.locator('#obSaldo').fill('10000')
        page.locator('[data-onbtab="reserves"]').click()
        page.locator('#obReserveFcrCurrent').fill('1500')
        page.locator('#obReserveMonthlyExpenses').fill('100')
        page.locator('#obReserveFeoCurrent').fill('600')
        row['onboarding'] = {'activeStep': page.locator('.onb-step.active').get_attribute('data-onbstep'),
            'fcrCurrent': page.locator('#obReserveFcrCurrent').input_value(),
            'feoCurrent': page.locator('#obReserveFeoCurrent').input_value(),
            'fcrStatus': page.locator('#obReserveFcrStatus').input_value(),
            'feoStatus': page.locator('#obReserveFeoStatus').input_value()}
        assert row['onboarding'] == {'activeStep': 'reserves', 'fcrCurrent': '1500',
            'feoCurrent': '600', 'fcrStatus': 'Pendente', 'feoStatus': 'Pendente'}, row
        # No nominal-capital/approved-expense facts exist: UI drafts must preserve
        # explicit pending requirements and must not manufacture financial facts.
        after = page.evaluate('({state: JSON.stringify(S), persisted: localStorage.getItem(LSKEY)})')
        assert before == after, 'editing an unsaved onboarding draft changed durable/domain state'
        row['draftPreservesState'] = True
        page.keyboard.press('Escape')
        assert not page.locator('#modalOverlay').evaluate('(element) => element.classList.contains("show")')
        row['trace'] = page.evaluate('__reserveStartupTrace')
        row['reserveRequests'] = server.reserve_requests[request_start:]
        if not portable:
            assert len(row['reserveRequests']) == 1, row
            assert row['reserveRequests'][0]['elapsedSeconds'] >= delay, row
            observed = {entry['path']: entry for entry in events['scripts']}
            assert set(observed) == {RESERVE, ONBOARDING, BOOT}, row
            for path, response in observed.items():
                assert response['status'] == 200 and response['sha256'] == sha256((ROOT / path).read_bytes()), row
            trace_paths = [urlsplit(entry['src']).path.lstrip('/') for entry in row['trace']['scripts']]
            assert trace_paths.index(RESERVE) < trace_paths.index(ONBOARDING) < trace_paths.index(BOOT), row
            assert all(entry['reserveType'] == 'function' for entry in row['trace']['scripts']
                if urlsplit(entry['src']).path.lstrip('/') in (RESERVE, ONBOARDING, BOOT)), row
        assert_fixture_requests(context)
        assert not row['trace']['errors'] and not events['pageerror'], row
        assert not [entry for entry in events['console'] if entry['type'] == 'error'], row
        assert not events['requestfailed'], row
        return row
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--browser-executable', default=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
    args = parser.parse_args()
    paths, source_checks = check_sources()
    names = ['index.html', 'src/js/manifest.json', 'build-id.js', PORTABLE,
        'tools/reserve_startup_dependency_test.py', *paths]
    before = hashes(names)
    receipt = {'root': str(ROOT), 'sourceChecks': source_checks, 'sourcesBefore': before, 'loads': []}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(DelayedReserveHandler, directory=str(ROOT)))
    server.reserve_delay = 0
    server.reserve_requests = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    receipt['httpQueueSize'] = server.request_queue_size
    try:
        with sync_playwright() as playwright:
            launch = {'headless': True}
            chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
            executable = args.browser_executable or (str(chrome) if chrome.is_file() else None)
            if executable:
                launch['executable_path'] = executable
            browser = playwright.chromium.launch(**launch)
            receipt['browserVersion'] = browser.version
            try:
                for delay in (0, DELAY_SECONDS, DELAY_SECONDS, DELAY_SECONDS):
                    receipt['loads'].append(verify_load(browser, server, url, delay))
                receipt['loads'].append(verify_load(browser, server, url, 0, portable=True))
            finally:
                browser.close()
        receipt['sourcesAfter'] = hashes(names)
        assert receipt['sourcesAfter'] == before, 'sources changed during verification'
        receipt['sourcesStable'] = True
        receipt['outcome'] = 'PASS'
        print('PASS: ordered index/manifest/portable; 1 normal and 3 delayed HTTP startups; '
            '1 portable startup; onboarding interactions, pending facts and errors checked')
    except Exception as error:
        receipt['outcome'] = 'PRODUCT_FAIL'
        receipt['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        server.shutdown()
        server.server_close()
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
