#!/usr/bin/env python3
"""AUD-10: real controlled document navigation and exact offline/portable bytes."""
import argparse
import base64
import hashlib
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
import sys
import threading


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / 'tools'))
    from browser_fixture_server import BrowserFixtureServer
    from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
    from playwright.sync_api import sync_playwright

    class Quiet(SimpleHTTPRequestHandler):
        extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.md': 'text/plain;charset=utf-8'}
        def log_message(self, *_):
            pass

    sources = ['sw.js', 'tools/rebuild_monolith.py', 'README.md', 'CHANGELOG.md', 'build-id.js']
    hashes = {f: hashlib.sha256((root / f).read_bytes()).hexdigest() for f in sources}
    results = []
    def check(name, value, observed=None):
        results.append({'name': name, 'result': 'PASS' if value else 'PRODUCT_FAIL', 'observed': observed})

    server = BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(service_workers='allow', viewport={'width': 1440, 'height': 1000})
            install_bootstrap(context)
            page = context.new_page()
            page.goto(url + 'index.html', wait_until='load')
            wait_bootstrap(page)
            page.wait_for_function('navigator.serviceWorker.controller', timeout=30000)
            page.reload(wait_until='load')
            wait_bootstrap(page)
            page.evaluate("() => {window.__onbShown=true;closeModal();openSettingsModal('about');}")
            original = page.evaluate('localStorage.getItem(LSKEY)')
            for offline in (False, True):
                context.set_offline(offline)
                for name in ('README.md', 'CHANGELOG.md'):
                    with context.expect_page() as new_page:
                        page.locator('[data-settings-panel="about"] a[href="' + name + '"]').click()
                    popup = new_page.value
                    try:
                        popup.wait_for_load_state('load')
                        content = popup.locator('body').inner_text()
                        expected = (root / name).read_text()
                        check(('offline' if offline else 'online') + ' native link delivers ' + name,
                              content.strip() == expected.strip(),
                              {'url': popup.url, 'actual_sha256': hashlib.sha256(content.strip().encode()).hexdigest(),
                               'expected_sha256': hashlib.sha256(expected.strip().encode()).hexdigest(),
                               'contains_app_shell': popup.locator('#settingsModal').count() > 0})
                    finally:
                        popup.close()
                check(('offline' if offline else 'online') + ' document links preserve financial document',
                      page.evaluate('localStorage.getItem(LSKEY)') == original)
            context.set_offline(False)
            for name in ('README.md', 'CHANGELOG.md'):
                cached = page.evaluate("""async name => {
                    const cache=await caches.open('jp-wealth-'+JP_WEALTH_BUILD_ID);
                    const response=await cache.match(new URL(name,location.href).href);
                    return response ? await response.text() : null;
                }""", name)
                check('active build cache contains exact ' + name, cached == (root / name).read_text())
            assert_fixture_requests(context)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    portable = (root / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').read_text()
    for name in ('README.md', 'CHANGELOG.md'):
        encoded = base64.b64encode((root / name).read_bytes()).decode()
        check('portable delivers exact ' + name,
              'href="data:text/markdown;charset=utf-8;base64,' + encoded + '" download="' + name + '"' in portable)
    check('test preserves product sources', hashes == {f: hashlib.sha256((root / f).read_bytes()).hexdigest() for f in sources})
    report = {'root': str(root), 'environment': 'isolated Chromium; real SW/native Settings popup; synthetic economic bootstrap',
              'sources': hashes, 'cases': results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for item in results:
        print(item['result'] + ': ' + item['name'])
    return 0 if all(item['result'] == 'PASS' for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
