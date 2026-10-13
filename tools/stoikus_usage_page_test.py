#!/usr/bin/env python3
"""Public daily-use journey; source guide and real browser, never MT5 proof."""
import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
import re
import threading

from browser_fixture_server import BrowserFixtureServer


def check_guide(root):
    guide_path = root / 'mt5/jpw-alavancagem-atual/STOIKUS_USO_DIARIO.md'
    assert guide_path.is_file(), 'Daily guide is missing from the package sources'
    guide = guide_path.read_text()
    for name, count in (('JPW_Alavancagem_Atual', 12), ('JPW_NoCuda_Channels', 5), ('JPW_Stoikus_Monitor', 3)):
        files = list((root / 'mt5/jpw-alavancagem-atual/MQL5').rglob(name + '.mq5'))
        assert len(files) == 1
        inputs = re.findall(r'^input\s+\w+\s+(Inp\w+)\s*=\s*([^;]+);\s*//\s*([^\n]+)', files[0].read_text(), re.M)
        assert len(inputs) == count
        for identifier, default, label in inputs:
            assert re.search(r'\|\s*`' + identifier + r'`\s*\|', guide), (name, identifier, 'input missing from public table')
            assert label in guide, (name, label, 'displayed MT5 label missing from guide')
    for shortname in ('Stoikus · Cockpit', 'Stoikus · NoCuda Channels'):
        assert shortname in guide, ('Ctrl+I displays indicator shortnames', shortname)
    assert 'conta demo na mesma instalação' in guide
    for phrase in ('gráfico de apoio', 'gráfico de trabalho', 'JPW_Stoikus_Abrir_Paineis', 'Experts',
                   'false', 'vazio', 'PERIOD_CURRENT', 'H1', 'UNVERIFIED_NATIVE', 'MQL5/Files', 'NOT_RUN'):
        assert phrase in guide, ('public guide missing', phrase)
    print('PASS daily guide: two charts, all 20 inputs, uncertainty and preserved data', flush=True)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def check_browser(root, evidence):
    from playwright.sync_api import sync_playwright
    from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
    server = BrowserFixtureServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    evidence.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
            install_bootstrap(context)
            context.add_init_script("localStorage.setItem('jpw_nav_layout','sidebar');window.__onbShown=true;")
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
            wait_bootstrap(page)
            page.evaluate("window.__onbShown=true;closeModal();S.onboarding.done=true;JPWNavigation.navigate('tools-leverage')")
            before = page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})')
            page.locator('[data-genetrix-tab="install"]').click()
            panel = page.locator('#genetrixInstallPanel')
            panel.screenshot(path=str(evidence / 'install-desktop.png'))
            page.screenshot(path=str(evidence / 'install-first-screen-desktop.png'))
            (evidence / 'install-observed.txt').write_text(panel.inner_text())
            primary = panel.locator('[data-jpw-leverage-download="dailySource"]')
            assert primary.count() == 1 and primary.is_visible(), 'Daily download is not exposed in the first installation path'
            roles = panel.locator('[data-stoikus-daily-roles]')
            assert roles.is_visible() and roles.locator('tbody tr').count() == 4, 'Three daily roles and a one-shot opener must be exposed'
            assert panel.locator('[data-stoikus-isolated-install]').is_visible(), 'Isolation must be defined in the daily path'
            assert all(p.is_hidden() for p in panel.locator('[data-stoikus-legacy-install] p').all()), 'Legacy details must not displace the daily roles'
            start = panel.locator('#jpwLeverageDailyStart')
            assert start.is_visible() and 'JPW_Stoikus_Abrir_Paineis' in start.inner_text()
            assert 'apoio' in start.inner_text() and 'trabalho' in start.inner_text()
            assert 'Stoikus · Cockpit' in start.inner_text() and 'Stoikus · NoCuda Channels' in start.inner_text()
            table = panel.locator('.genetrix-file-disclosure .leverage-file-table')
            assert not table.is_visible(), 'Engineering inventory must not dominate installation'
            tests = panel.locator('#jpwLeverageTests')
            assert not tests.is_visible(), 'Synthetic tests must be inside engineering disclosure'
            disclosure = panel.locator('[data-stoikus-engineering-tests] > summary')
            disclosure.focus(); page.keyboard.press('Enter')
            assert tests.is_visible() and 'Experts' in tests.inner_text()
            page.keyboard.press('Enter')
            for component, count in (('account', 12), ('nocuda', 5), ('monitor', 3)):
                details = panel.locator('[data-stoikus-inputs="' + component + '"]')
                details.locator('summary').focus(); page.keyboard.press('Enter')
                assert details.locator('tbody tr').count() == count
                assert details.locator('table').is_visible()
                filename = {'account':'JPW_Alavancagem_Atual', 'nocuda':'JPW_NoCuda_Channels', 'monitor':'JPW_Stoikus_Monitor'}[component]
                source = next((root/'mt5/jpw-alavancagem-atual/MQL5').rglob(filename+'.mq5')).read_text()
                labels = re.findall(r'^input\s+\w+\s+Inp\w+\s*=\s*[^;]+;\s*//\s*([^\n]+)', source, re.M)
                assert details.locator('tbody th > strong').all_text_contents() == labels, ('public labels differ from MT5',component)
                page.keyboard.press('Enter')
            for width in (1440, 390, 320):
                page.set_viewport_size({'width': width, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('overflow', width)
                panel.screenshot(path=str(evidence / f'install-{width}.png'))
                panel.evaluate("n=>n.scrollIntoView({block:'start'})")
                page.screenshot(path=str(evidence / f'install-first-screen-{width}.png'))
                start.evaluate("n=>n.scrollIntoView({block:'start'})")
                page.screenshot(path=str(evidence / f'start-{width}.png'))
                for component in ('account','nocuda','monitor'):
                    inputs = panel.locator('[data-stoikus-inputs="'+component+'"]')
                    inputs.locator('summary').click()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('input overflow',component,width)
                    inputs.evaluate("n=>n.scrollIntoView({block:'start'})")
                    page.screenshot(path=str(evidence / f'inputs-{component}-{width}.png'))
                    inputs.locator('summary').click()
            page.locator('[data-genetrix-tab="help"]').click()
            help_panel = page.locator('#genetrixHelpPanel')
            (evidence / 'help-observed.txt').write_text(help_panel.inner_text())
            page.locator('[data-stoikus-help="panels"] > summary').focus(); page.keyboard.press('Enter')
            assert 'Ctrl+I' in page.locator('[data-stoikus-help="panels"]').inner_text()
            page.locator('[data-stoikus-help="monitor"] > summary').click()
            assert 'false' in page.locator('[data-stoikus-help="monitor"]').inner_text()
            inputs_help = page.locator('.genetrix-help-item').filter(has=page.locator('a[href="#jpwLeverageUse"]'))
            inputs_help.locator(':scope > summary').click()
            help_link = inputs_help.get_by_role('link', name='Voltar ao uso e às tabelas de Entradas')
            for width in (1440, 390, 320):
                page.set_viewport_size({'width': width, 'height': 900})
                help_link.scroll_into_view_if_needed()
                rect = help_link.bounding_box()
                assert rect and rect['width'] >= 44 and rect['height'] >= 44, ('help touch target', width, rect)
                help_link.focus()
                assert help_link.evaluate('n=>n===document.activeElement')
            page.keyboard.press('Enter')
            page.wait_for_function("document.activeElement.id==='jpwLeverageUse'")
            assert page.locator('#genetrixInstallPanel').is_visible()
            assert page.evaluate("JPWNavigation.current().canonical") == 'tools-leverage'
            assert page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})') == before
            assert not errors, errors
            (evidence / 'result.json').write_text(json.dumps({'browser': 'PASS', 'mt5': 'NOT_RUN', 'root': str(root)}, indent=2))
            print('PASS real browser: daily path, keyboard disclosures, input tables, help, mobile and no writes', flush=True)
            context.close(); browser.close()
    finally:
        server.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--docs-only', action='store_true')
    parser.add_argument('--browser-only', action='store_true')
    parser.add_argument('--evidence', type=Path, default=Path('/private/tmp/jpw-stoikus-usability-evidence-20261013/site/candidate'))
    args = parser.parse_args()
    if not args.browser_only:
        check_guide(args.root)
    if not args.docs_only:
        check_browser(args.root, args.evidence)


if __name__ == '__main__':
    main()
