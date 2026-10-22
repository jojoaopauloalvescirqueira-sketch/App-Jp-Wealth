#!/usr/bin/env python3
"""Public daily-use journey; source guide and real browser, never MT5 proof."""
import argparse
import base64
import functools
from hashlib import sha256
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


def reset_download_page(page):
    """Every negative case gets a fresh lazy consumer; successful bytes are cached."""
    from browser_bootstrap_fixture import wait_bootstrap
    page.reload()
    wait_bootstrap(page)
    page.evaluate("window.__onbShown=true;closeModal();S.onboarding.done=true;JPWNavigation.navigate('tools-leverage')")
    page.locator('[data-genetrix-tab="install"]').click()
    page.locator('#genetrixInstallPanel details').evaluate_all('nodes=>nodes.forEach(n=>n.open=true)')


def verify_hosted_preview_delivery(page, root, release):
    """Real lazy preview despite transformed HTML; all negative guards use fresh consumers."""
    record = release['artifacts']['preview']
    raw = (root / record['path']).read_bytes()
    requests = []
    pattern = '**/' + record['path']
    descriptor = page.evaluate('window.JPW_DOWNLOAD_MANIFEST.payloads["leverage-preview"]')
    script = (root / descriptor['path']).read_text()
    envelope = json.loads(script.split(',',1)[1].removesuffix(');\n'))
    assert base64.b64decode(envelope['files']['leverage/preview']) == raw
    script_pattern = '**/' + descriptor['path']
    try:
        for mode in ('redirect307', 'injected-html'):
            def hosted(route):
                requests.append(route.request.url)
                if mode == 'redirect307':
                    route.fulfill(status=307, headers={'Location': record['path'][:-5]}, body='')
                else:
                    route.fulfill(status=200, content_type='text/html', body=raw+b'<script>/* hosting injection */</script>')
            page.route(pattern, hosted)
            reset_download_page(page)
            with page.expect_download() as pending:
                page.locator('[data-jpw-leverage-download="preview"]').click()
            artifact = pending.value
            assert artifact.suggested_filename == record['filename']
            assert Path(artifact.path()).read_bytes() == raw
            assert not requests, 'preview must never request the hosted HTML route'
            page.unroute(pattern)
        changed = bytearray(raw); changed[-1] ^= 1
        cases = [(None, 'incorporado ausente'), ('bad-mime', 'Metadados'),
                 (base64.b64encode(changed).decode(), 'Hash'),
                 (base64.b64encode(raw[:-1]).decode(), 'Tamanho')]
        page.route(pattern, hosted)
        for encoded, expected in cases:
            reset_download_page(page)
            refused = []
            handler = lambda artifact: refused.append(artifact.suggested_filename)
            page.on('download', handler)
            mutated = {**envelope, 'files': {}}
            if encoded == 'bad-mime':
                page.evaluate('window.JPW_DOWNLOAD_MANIFEST.resources["leverage/preview"].mime="text/plain"')
            elif encoded is not None:
                mutated['files']['leverage/preview'] = encoded
            sidecar = 'window.JPWDownloadAssets.register("leverage-preview",'+json.dumps(mutated)+');'
            page.route(script_pattern, lambda route, request=None, text=sidecar: route.fulfill(status=200,content_type='application/javascript',body=text))
            page.locator('[data-jpw-leverage-download="preview"]').click()
            page.wait_for_function("expected=>document.getElementById('jpwLeverageDownloadStatus').textContent.includes(expected)", arg=expected)
            assert not refused and not requests, 'invalid lazy preview must refuse without HTML network fallback'
            page.unroute(script_pattern)
            page.remove_listener('download', handler)
    finally:
        page.unroute(pattern)
        reset_download_page(page)
    print('PASS hosted preview: real lazy bytes despite 307/injection; missing/MIME/hash/size refused without HTML fallback',flush=True)


def check_browser(root, evidence, interface_fixture=False):
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
            if interface_fixture:
                # Explicit isolated contract fixture: do not regenerate shared build outputs.
                kinds = {'nativeKit':'Kit_Windows_Stoikus_Janelas_R5.zip', 'nativePin':'root-pin-R5.json', 'preview':'Previa_Stoikus_Janelas_R5.html'}
                release = {'revision':'R5', 'candidate':'1.23.0-interface', 'archiveVariant':'', 'state':'SOURCE_ONLY_NATIVE_PENDING',
                           **{key:'NOT_RUN' for key in ('nativeCompilation','nativeRuntime','humanAcceptance','windowsX64')}, 'artifacts':{}}
                for kind, filename in kinds.items():
                    path = 'downloads/jpw-alavancagem-atual/' + filename
                    raw = (root/path).read_bytes()
                    release['artifacts'][kind] = {'available':True,'path':path,'filename':filename,'bytes':len(raw),'sha256':sha256(raw).hexdigest()}
                context.add_init_script("let releaseManifest;Object.defineProperty(window,'JPW_LEVERAGE_MANIFEST',{configurable:true,get(){return releaseManifest;},set(value){releaseManifest={...value,version:'1.23.0',interfaceRelease:" + json.dumps(release) + "};}});")
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
            kit = panel.locator('[data-stoikus-native-kit]')
            assert kit.is_visible(), 'R5 sealed compilation must be first in installation'
            assert kit.evaluate("n=>n.compareDocumentPosition(document.getElementById('genetrixPreparation')) & Node.DOCUMENT_POSITION_FOLLOWING")
            expected_phases = ['jpwStoikusNativeKit','genetrixPreparation','jpwLeverageCompile','jpwLeverageInstall','jpwLeverageDailyStart','jpwLeverageUse']
            sequence = panel.locator('[data-stoikus-native-sequence] a')
            assert sequence.evaluate_all("ns=>ns.map(n=>n.getAttribute('href').slice(1))") == expected_phases
            assert panel.locator('.stoikus-phase').evaluate_all('ns=>ns.map(n=>n.id)') == expected_phases
            # Compare every command with the independently sealed kit, never with a second web copy.
            from zipfile import ZipFile
            selected=page.evaluate('window.JPW_LEVERAGE_MANIFEST.interfaceRelease')
            native_path=selected['artifacts']['nativeKit']['path'] if selected else 'downloads/jpw-alavancagem-atual/Kit_Windows_Stoikus_Janelas_R5.zip'
            with ZipFile(root/native_path) as native_kit:
                sealed_guide = native_kit.read('LEIA-PRIMEIRO.md').decode()
            commands = re.findall(r'```powershell\n(.*?)```', sealed_guide, re.S)
            assert len(commands) == 5
            assert [v.rstrip() for v in panel.locator('pre').all_text_contents()] == [v.rstrip() for v in commands]
            for command_block in panel.locator('pre').all():
                if command_block.is_hidden():
                    command_details = command_block.locator('xpath=ancestor::details[1]')
                    command_details.locator(':scope > summary').focus(); page.keyboard.press('Enter')
                    assert command_block.is_visible()
                    page.keyboard.press('Enter')
                    assert command_block.is_hidden()
            assert 'Compilar com F7' not in panel.inner_text(), 'An unreceipted compilation path displaced the sealed flow'
            assert 'não executa o MT5' in page.locator('#jpwStoikusInterface').text_content(), 'Preview must remain explicitly separate from native MT5 execution'
            assert 'somente os quatro' in panel.inner_text() and 'não recompile nela' in panel.inner_text()
            assert 'dados fictícios' in kit.text_content().lower() and 'não compila, não instala' in kit.text_content()
            metadata = page.evaluate('window.JPW_LEVERAGE_MANIFEST')
            for kind in ('nativeKit', 'nativePin', 'preview'):
                button = kit.locator('[data-jpw-leverage-download="'+kind+'"]')
                assert button.count() == 1
                if kind == 'preview':
                    preview_disclosure = kit.locator('details').filter(has=page.locator('[data-jpw-leverage-download="preview"]')).first
                    preview_disclosure.locator(':scope > summary').focus(); page.keyboard.press('Enter')
                assert button.is_visible()
                assert button.is_enabled() == bool(metadata.get('interfaceRelease'))
            if metadata.get('interfaceRelease'):
                artifacts = metadata['interfaceRelease']['artifacts']
                # An injected base must not redirect local verified downloads.
                page.evaluate("()=>{const base=document.createElement('base');base.href='https://untrusted.invalid/';document.head.append(base);}")
                for kind, record in artifacts.items():
                    button = kit.locator('[data-jpw-leverage-download="'+kind+'"]')
                    with page.expect_download() as pending:
                        button.click()
                    artifact = pending.value
                    raw = Path(artifact.path()).read_bytes()
                    assert artifact.suggested_filename == record['filename']
                    assert len(raw) == record['bytes'] and sha256(raw).hexdigest() == record['sha256']
                page.evaluate("document.querySelector('base').remove()")
                verify_hosted_preview_delivery(page, root, metadata['interfaceRelease'])
                refused = []
                page.on('download', lambda artifact: refused.append(artifact.suggested_filename))
                for kind, record in artifacts.items():
                    if kind == 'preview': continue  # embedded-only; separate refusal checks above
                    raw = (root/record['path']).read_bytes()
                    changed = bytearray(raw); changed[-1] ^= 1
                    for code, body, expected in ((404,b'missing','não encontrado'),(200,bytes(changed),'Hash'),(200,raw[:-1],'Tamanho')):
                        reset_download_page(page)
                        page.route('**/' + record['path'], lambda route, request=None, status=code, data=body: route.fulfill(status=status, body=data))
                        kit.locator('[data-jpw-leverage-download="'+kind+'"]') .click()
                        page.wait_for_function("expected=>document.getElementById('jpwLeverageDownloadStatus').textContent.includes(expected)", arg=expected)
                        assert not refused, ('corrupt R5 artifact was downloaded',kind)
                        page.unroute('**/' + record['path'])
                print('PASS real R5 kit/pin/preview downloads; malicious base ignored; network kit/pin missing, same-size corruption and truncation refused',flush=True)
            page.locator('#jpwLeveragePage details').evaluate_all('nodes=>nodes.forEach(n=>n.open=false)')
            assert page.locator('[data-genetrix-tab]').count() == 5
            for area in ('overview','resources','validation','help','install'):
                page.locator('[data-genetrix-tab="'+area+'"]').click()
                assert page.locator('[data-genetrix-panel="'+area+'"]').is_visible()
                assert page.locator('[data-genetrix-tab="'+area+'"]').get_attribute('aria-selected') == 'true'
            overview = page.locator('#jpwStoikusInterface').text_content()
            for phrase in ('10 pt', 'Histórico', 'conta inteira', 'Selecionar canal', 'UNVERIFIED_NATIVE'):
                assert phrase in overview, phrase
            controls = page.locator('#jpwLeverageCockpit').text_content()
            for phrase in ('Compacto/Completo', '0%', '30%', '100%', 'Conta · restaurar', '280', '480', '720 × 520', '680 × 500'):
                assert phrase in controls, phrase
            primary = panel.locator('[data-jpw-leverage-download="dailySource"]')
            assert primary.count() == 1 and not primary.is_visible(), 'Duplicate source package must stay optional; it is already inside the kit'
            source_disclosure = panel.locator('details').filter(has=page.locator('[data-jpw-leverage-download="dailySource"]')).first
            source_disclosure.locator(':scope > summary').focus(); page.keyboard.press('Enter')
            assert primary.is_visible()
            roles = panel.locator('[data-stoikus-daily-roles]')
            panel.locator('details').filter(has=page.locator('[data-stoikus-daily-roles]')).first.locator(':scope > summary').focus(); page.keyboard.press('Enter')
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
            assert tests.is_visible() and 'SDK' in tests.inner_text() and 'não fazem parte dos quatro EX5' in tests.inner_text()
            page.keyboard.press('Enter')
            optional_inputs = panel.locator('details').filter(has=page.locator('[data-stoikus-inputs="account"]')).first
            if not optional_inputs.evaluate('n=>n.open'): optional_inputs.locator(':scope > summary').click()
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
            preview_disclosure = kit.locator('details').filter(has=page.locator('[data-jpw-leverage-download="preview"]')).first
            if not preview_disclosure.evaluate('n=>n.open'):
                preview_disclosure.locator(':scope > summary').click()
            for width in (1440, 390, 320):
                page.set_viewport_size({'width': width, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('overflow', width)
                for integrity in kit.locator('.leverage-package-integrity').all():
                    integrity.locator('summary').click()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('R5 hashes overflow', width)
                kit.screenshot(path=str(evidence / f'kit-{width}.png'))
                for integrity in kit.locator('.leverage-package-integrity').all():
                    integrity.locator('summary').click()
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
    parser.add_argument('--interface-fixture', action='store_true', help='Explicit temporary R5 metadata injection; no generated-file writes')
    parser.add_argument('--evidence', type=Path, default=Path('/private/tmp/jpw-stoikus-usability-evidence-20261013/site/candidate'))
    args = parser.parse_args()
    if not args.browser_only:
        check_guide(args.root)
    if not args.docs_only:
        check_browser(args.root, args.evidence, args.interface_fixture)


if __name__ == '__main__':
    main()
