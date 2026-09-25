#!/usr/bin/env python3
"""Tema inicial: cenários sintéticos, navegador e armazenamento isolados."""
import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from dashboard_macro_test import launch_browser


ROOT = Path(__file__).resolve().parents[1]
PATHS = ('index.html', 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class Server(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True


def main():
    for path in PATHS:
        markup = (ROOT / path).read_text()
        css_marker = '<style>' if path != 'index.html' else '<link rel="stylesheet"'
        assert markup.index('data-theme="light"') < markup.index("saved.theme==='dark'") < markup.index(css_marker)
    server = Server(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            try:
                for path in PATHS:
                    for os_theme in ('light', 'dark'):
                        context = browser.new_context(color_scheme=os_theme, service_workers='block')
                        install_bootstrap(context)
                        page = context.new_page()
                        page.goto(f'http://127.0.0.1:{server.server_port}/{path}')
                        wait_bootstrap(page)
                        assert page.evaluate('S.theme') == 'light'
                        assert page.evaluate('document.documentElement.dataset.theme') == 'light'
                        assert page.locator('#themeSeg [data-theme-val="light"]').evaluate('e=>e.classList.contains("on")')
                        assert page.evaluate('matchMedia("(prefers-color-scheme: dark)").matches') == (os_theme == 'dark')
                        assert page.evaluate('getComputedStyle(document.documentElement).colorScheme') == 'light'
                        persisted = page.evaluate('localStorage.getItem("jpwealth_v9_state")')
                        assert persisted is None or page.evaluate('JSON.parse(localStorage.getItem("jpwealth_v9_state")).theme') == 'light'
                        context.close()

                    context = browser.new_context(service_workers='block')
                    install_bootstrap(context)
                    page = context.new_page()
                    url = f'http://127.0.0.1:{server.server_port}/{path}'
                    page.goto(url)
                    wait_bootstrap(page)
                    page.evaluate('''()=>{
                        S.onboarding.done=true;
                        S.theme='dark';
                        S.mei.notes='synthetic theme sentinel';
                        if(!save())throw Error('Could not create synthetic saved state');
                    }''')
                    before = page.evaluate('localStorage.getItem("jpwealth_v9_state")')
                    before_style = []
                    if path == 'index.html':
                        def observe_style(route):
                            before_style.append(page.evaluate('document.documentElement.dataset.theme'))
                            route.continue_()
                        page.route('**/src/styles/app.css', observe_style)
                    page.reload()
                    wait_bootstrap(page)
                    if path == 'index.html':
                        assert before_style == ['dark'], before_style
                    assert page.evaluate('S.theme') == 'dark'
                    assert page.evaluate('document.documentElement.dataset.theme') == 'dark'
                    assert page.evaluate('getComputedStyle(document.documentElement).colorScheme') == 'dark'
                    assert page.locator('#themeSeg [data-theme-val="dark"]').evaluate('e=>e.classList.contains("on")')
                    assert page.evaluate('S.mei.notes') == 'synthetic theme sentinel'
                    assert page.evaluate('localStorage.getItem("jpwealth_v9_state")') == before

                    page.locator('#themeSeg [data-theme-val="light"]').evaluate('e=>e.click()')
                    assert page.evaluate('S.theme') == 'light'
                    assert page.evaluate('document.documentElement.dataset.theme') == 'light'
                    assert page.evaluate('JSON.parse(localStorage.getItem("jpwealth_v9_state")).theme') == 'light'
                    page.reload()
                    wait_bootstrap(page)
                    assert page.evaluate('S.theme') == 'light'
                    assert page.locator('#themeSeg [data-theme-val="light"]').evaluate('e=>e.classList.contains("on")')

                    # The existing backup normalizer must fill a missing key,
                    # accept a valid choice, and reject an invalid value before a write.
                    result = page.evaluate('''()=>{
                        const state=structuredClone(S), raw=localStorage.getItem(LSKEY);
                        const old=structuredClone(state);delete old.theme;
                        const imported=normalizeImportedState(old);
                        const chosen=structuredClone(state);chosen.theme='dark';
                        const importedDark=normalizeImportedState(chosen);
                        const bad=structuredClone(state);bad.theme='system';
                        let rejected=false;
                        try{normalizeImportedState(bad)}catch(e){rejected=true}
                        return {old:imported.theme,dark:importedDark.theme,rejected,
                            theme:S.theme,rawSame:localStorage.getItem(LSKEY)===raw,
                            sentinel:S.mei.notes};
                    }''')
                    assert result['old'] == 'light' and result['dark'] == 'dark', result
                    assert result['rejected'] and result['theme'] == 'light' and result['rawSame'], result
                    assert result['sentinel'] == 'synthetic theme sentinel', result

                    invalid = page.evaluate('''()=>{
                        const bad=structuredClone(S);bad.theme='system';
                        const raw=JSON.stringify(bad);localStorage.setItem(LSKEY,raw);return raw;
                    }''')
                    page.reload()
                    wait_bootstrap(page)
                    assert page.evaluate('jpWealthLoadRecoveryActive()')
                    assert page.evaluate('document.documentElement.dataset.theme') == 'light'
                    assert page.evaluate('localStorage.getItem(LSKEY)') == invalid
                    assert page.evaluate('save()') is False
                    context.close()
                    print('PASS theme defaults, saved choices, selector, backup, recovery:', path, flush=True)

                # A denied storage read must use the existing recovery barrier.
                context = browser.new_context(service_workers='block')
                install_bootstrap(context)
                context.add_init_script('''(()=>{
                    const original=Storage.prototype.getItem;
                    Storage.prototype.getItem=function(key){
                        if(key==='jpwealth_v9_state')throw new DOMException('synthetic denial','SecurityError');
                        return original.call(this,key);
                    };
                })()''')
                page = context.new_page()
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
                wait_bootstrap(page)
                assert page.evaluate('jpWealthLoadRecoveryActive()')
                assert page.evaluate('document.documentElement.dataset.theme') == 'light'
                assert page.evaluate('save()') is False
                context.close()
                print('PASS unreadable storage enters recovery', flush=True)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
