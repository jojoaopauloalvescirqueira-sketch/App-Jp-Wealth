#!/usr/bin/env python3
"""JPW GENETRIX: navegação e pacote público, sem dados de conta."""

from hashlib import sha256
from http.server import SimpleHTTPRequestHandler
from io import BytesIO
import json
import base64
import re
import os
from pathlib import Path
import threading
from urllib.request import urlopen
from zipfile import ZipFile

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from browser_fixture_server import BrowserFixtureServer


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
MANIFEST = json.loads((ROOT / 'downloads/jpw-alavancagem-atual/manifest.json').read_text())
SOURCE = MANIFEST['downloads']['source']
ARCHIVE = ROOT / SOURCE['path']
COMPILED = MANIFEST['downloads']['compiled']
COMPILED_ARCHIVE = ROOT / COMPILED['path']
EVIDENCE_DIR = Path(os.environ['JPW_LEVERAGE_EVIDENCE_DIR']) if os.environ.get('JPW_LEVERAGE_EVIDENCE_DIR') else None
EXPECTED = {
    'README.md',
    'AGENTS.md',
    'MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5',
    'MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5',
    'MQL5/Include/JPWealth/JPW_NoCuda_Core.mqh',
    'MQL5/Include/JPWealth/JPW_NoCuda_Projection_Core.mqh',
    'MQL5/Include/JPWealth/JPW_NoCuda_Projection.mqh',
    'MQL5/Include/JPWealth/JPW_NoCuda_Store.mqh',
    'MQL5/Include/JPWealth/JPW_NoCuda_Terminal.mqh',
    'MQL5/Include/JPWealth/JPW_NoCuda_Render.mqh',
    'MQL5/Include/JPWealth/JPW_NoCuda_UI.mqh',
    'MQL5/Scripts/JPWealth/JPW_NoCuda_Core_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_NoCuda_Store_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_NoCuda_Projection_Tests.mq5',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Core.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Store.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Config.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Live.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Observer.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh',
    'MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh',
    'MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Profile_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Store_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Store_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Config_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Horizon_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Observer_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5',
    'MQL5/Scripts/JPWealth/JPW_Alavancagem_StopRisk_Tests.mq5',
}

EXPECTED.update("MQL5/Include/JPWealth/JPW_Alavancagem_" + name + ".mqh" for name in ['Actions', 'Coordinator', 'Diagnostics', 'Diagnostics_Core', 'Presentation', 'Samples', 'Store_Result', 'Version'])
EXPECTED.add("MQL5/Scripts/JPWealth/JPW_Alavancagem_Diagnostics_Tests.mq5")


EXPECTED.update("MQL5/Include/JPWealth/JPW_SignalCopy_" + name + ".mqh" for name in ("Types", "Core", "Terminal", "Controller", "UI"))
EXPECTED.add("MQL5/Scripts/JPWealth/JPW_SignalCopy_Tests.mq5")
EXPECTED.add("MQL5/Include/JPWealth/JPW_Alavancagem_Positions.mqh")
EXPECTED.add("MQL5/Scripts/JPWealth/JPW_Alavancagem_Positions_Tests.mq5")


FIBO_MEMBERS = {
    *("MQL5/Include/JPWealth/JPW_NoCuda_Fibo_" + name + ".mqh"
      for name in ("Core", "Terminal", "Store", "Sync", "Controller", "UI")),
    "MQL5/Include/JPWealth/JPW_UI_Focus.mqh",
    "MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Lab.mq5",
    "MQL5/Images/JPWealth/JPW_NoCuda_Logo.bmp",
    "MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo.provenance.md",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_100.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_125.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_150.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_200.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_100.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_125.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_150.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_200.bmp",

}
EXPECTED.update(FIBO_MEMBERS)
EXPECTED.add("MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Factor.mqh")
EXPECTED.add("MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Factor_Tests.mq5")
# Explicit additions approved for isolated1.17.0, original87members retained.
EXPECTED.update("MQL5/Include/JPWealth/JPW_Genetrix_"+name+".mqh" for name in
 ("Risk_Core","Risk_Terminal","Risk_Store","Ledger_Core","Ledger_Store","Ledger_Terminal","Ledger_Bridge","UI"))
EXPECTED.update("MQL5/Experts/JPWealth/JPW_Genetrix_"+name+".mq5" for name in ("Supervisor","Accountant"))
EXPECTED.update("MQL5/Scripts/JPWealth/JPW_Genetrix_"+name+"_Tests.mq5" for name in ("Risk","Ledger"))
EXPECTED.add("GENETRIX_7X_LEDGER.md")
# Explicit 1.18.0 additions retain all 100 previously distributed members.
EXPECTED.update("MQL5/Include/JPWealth/JPW_PersonalHistory_" + name + ".mqh"
                for name in ("Controller", "Core", "Export", "Store", "Terminal", "UI"))
EXPECTED.add("MQL5/Scripts/JPWealth/JPW_PersonalHistory_Tests.mq5")
EXPECTED.add("GENETRIX_PERSONAL_HISTORY.md")
# Explicit 1.20.0 inventory: 120 original candidate members + seven harness references.
EXPECTED.update("MQL5/Include/JPWealth/" + name for name in (
    "JPW_Genetrix_Monitor_Core.mqh", "JPW_Genetrix_Monitor_Status.mqh", "JPW_Genetrix_Monitor_UI.mqh",
    "JPW_Genetrix_Observer_Runtime.mqh", "JPW_Genetrix_Accountant_Runtime.mqh",
    "JPW_Genetrix_Ledger_Preparation.mqh", "JPW_UI_Design.mqh"))
EXPECTED.add("MQL5/Experts/JPWealth/JPW_Genetrix_Monitor.mq5")
EXPECTED.update(("GENETRIX_REPAIR_1_18_1.md", "GENETRIX_COMPILE_FIX_1_18_2.md",
                 "GENETRIX_UI_1_19_0.md", "GENETRIX_CORE_1_20_0.md"))
HARNESS_MEMBERS = {
    "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md",
    "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.txt",
    "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.pdf",
    "harness/MANUAL_DE_ATIVACAO.md", "harness/contracts/ENG-AC01-12.json",
    "harness/contracts/TEMPLATES.md", "harness/REPOSITORY_INTEGRATION.md",
}
EXPECTED.update(HARNESS_MEMBERS)
assert len(EXPECTED) == 127
EXPECTED_EX5 = {name[:-4] + ".ex5" for name in EXPECTED if name.endswith(".mq5")}
assert len(EXPECTED_EX5) == 33
EXPECTED_COVERAGE = (
    "CANDIDATE 1.20.0 — Monitor Observer+Accountant; cálculo1.9.0. "
    "Compilação nativa33/33,0erros0avisos. Testes locais e limites nos recibos;"
    "0/3 sessões críticas MT5, instalação/aceiteNOT_RUN."
)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def boot(browser, target, layout='sidebar', width=1440, workers='block'):
    context = browser.new_context(viewport={'width': width, 'height': 900},
                                  service_workers=workers, accept_downloads=True)
    install_bootstrap(context)
    context.add_init_script("localStorage.setItem('jpw_nav_layout'," + json.dumps(layout) + ");window.__onbShown=true;")
    page = context.new_page()
    errors = []
    error_stacks = []
    request_failures = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('pageerror', lambda error: error_stacks.append(getattr(error, 'stack', str(error))))
    page.on('requestfailed', lambda request: request_failures.append({'url': request.url, 'failure': request.failure}))
    stage = 'navigate'
    try:
        page.goto(target)
        stage = 'bootstrap fixture'
        wait_bootstrap(page)
        stage = 'S.params / S.onboarding / JPWTools.ui readiness'
        page.wait_for_function("typeof S==='object' && !!S && !!S.params && !!S.onboarding && !!window.JPWTools?.ui")
    except Exception:
        # Observation only: do not retry, invoke application functions or change timeout.
        readiness = {'unavailable': 'document closed'}
        if not page.is_closed():
            try:
                readiness = page.evaluate("({url:location.href,readyState:document.readyState,state:typeof S,params:typeof S==='object'&&!!S&&!!S.params,onboarding:typeof S==='object'&&!!S&&!!S.onboarding,tools:!!window.JPWTools?.ui})")
            except Exception as diagnostic_error:
                readiness = {'capture_error': str(diagnostic_error)}
        print(json.dumps({'bootDiagnostic': {'target': target, 'layout': layout, 'stage': stage, 'first_pageerror': error_stacks[0] if error_stacks else None, 'pageerrors': error_stacks, 'request_failures': request_failures, 'readiness': readiness}}, ensure_ascii=False), flush=True)
        raise
    page.evaluate("window.__onbShown=true;closeModal();S.onboarding.done=true")
    return context, page, errors


def route_and_inspect(page):
    assert page.evaluate("JPWNavigation.navigate('tools-leverage')")
    assert page.evaluate("JPWNavigation.current().canonical") == 'tools-leverage'
    assert page.evaluate("JPWNavigation.current().localView.view") == 'leverage'
    assert page.locator('#jpwLeveragePage').is_visible()
    assert page.locator('#nocudaTool').is_hidden()
    assert page.locator('#execEcal').is_hidden()
    assert page.locator('#toolsNavSubmenu [data-nav-child="tools-leverage"]').get_attribute('aria-current') == 'page'
    assert page.locator('#jpwLeveragePage h1').text_content() == 'JPW GENETRIX'
    assert page.evaluate("JPWNavigation.children('tools').find(r=>r.id==='tools-leverage').label") == 'JPW GENETRIX — MT5'
    assert 'Exemplo ilustrativo — não representa sua conta.' in page.locator('#jpwLeverageHow').text_content()
    assert 'não recebe posições, equity, credenciais ou resultados' in page.locator('#jpwLeveragePage').text_content()
    assert 'nem lê ou distribui os registros locais' in page.locator('#jpwLeveragePage').text_content()
    assert MANIFEST['version'] == '1.20.0'
    assert MANIFEST['productName'] == 'JPW GENETRIX'
    assert 'Da origem da operação' in page.locator('#jpwLeverageOverview').text_content()
    assert 'medidas do Fibonacci importado permanecem indisponíveis' in page.locator('#jpwGenetrixDefinition').text_content()
    assert len(MANIFEST['sourceFiles']) == len(set(MANIFEST['sourceFiles'])) == 127
    assert MANIFEST['coverage'] == EXPECTED_COVERAGE
    native = MANIFEST['nativeArtifact']
    assert native['sourceFingerprint'] == MANIFEST['mqlSourceFingerprint']
    assert native['cpu'] == 'X64 Regular' and '6230' in native['compiler']
    assert native['evidence'] and len(native['artifacts']) == 33
    native_records = {Path(item['path']).relative_to('mt5/jpw-alavancagem-atual').as_posix(): item['sha256']
                      for item in native['artifacts']}
    assert set(native_records) == EXPECTED_EX5
    for name, expected_hash in native_records.items():
        assert re.fullmatch('[a-f0-9]{64}', expected_hash)
        assert sha256((ROOT/'mt5/jpw-alavancagem-atual'/name).read_bytes()).hexdigest() == expected_hash
    assert MANIFEST['genetrixCandidate']['native'] == 'COMPILATION_PASS_33_OF_33_RUNTIME_NOT_RUN'
    assert MANIFEST['downloads']['compiled']['available'] is True
    assert MANIFEST['validation']['compilation']['status'] == 'passed'
    assert '33/33' in MANIFEST['validation']['compilation']['detail']
    for kind in ('mathematics', 'terminal', 'clipboard'):
        assert MANIFEST['validation'][kind]['status'] == 'pending'
    assert MANIFEST['integration']['runtime'] == MANIFEST['integration']['installation'] == 'NOT_RUN'
    assert MANIFEST['integration']['complete_acceptance'] == 'INCONCLUSIVE'
    assert MANIFEST['integration']['historical_HIS_AC20'] == 'PRODUCT_FAIL_3_OF_3'
    limits = page.locator('[data-genetrix-panel="validation"]').text_content()
    for phrase in ('33 executáveis', '0/3', 'NOT_RUN', 'INCONCLUSIVE', 'HIS-AC20', 'PRODUCT_FAIL 3/3'):
        assert phrase in limits, phrase
    assert MANIFEST['validation']['clipboard']['detail'] in page.locator('[data-jpw-leverage-meta="clipboard"]').text_content()
    overview = page.locator('#jpwGenetrixArchitecture').text_content()
    for phrase in ('JPW_Genetrix_Monitor', 'Genetrix · Conta', 'NoCuda · Gráficos',
                   'Observer e Accountant', 'rollback', 'Supervisor 7x', 'outro gráfico'):
        assert phrase in overview, phrase
    assert 'Compilado · execução MT5 pendente' in page.locator('[data-jpw-leverage-meta="native-summary"]').text_content()
    assert set(page.locator('[data-jpw-leverage-meta="version"]').all_text_contents()) == {MANIFEST['version']}
    assert all(MANIFEST['validation']['mathematics']['detail'] in value for value in page.locator('[data-jpw-leverage-meta="mathematics"]').all_text_contents())
    assert all(MANIFEST['validation']['compilation']['detail'] in value for value in page.locator('[data-jpw-leverage-meta="compilation"]').all_text_contents())
    assert all(MANIFEST['validation']['terminal']['detail'] in value for value in page.locator('[data-jpw-leverage-meta="terminal"]').all_text_contents())
    assert page.locator('[data-jpw-leverage-download="source"]').is_enabled()
    assert set(page.locator('[data-jpw-leverage-meta="source-sha"]').all_text_contents()) == {SOURCE['sha256']}
    assert page.locator('[data-jpw-leverage-download="compiled"]').is_enabled()
    assert all(COMPILED['filename'] in value for value in page.locator('[data-jpw-leverage-meta="compiled-status"]').all_text_contents())
    assert page.evaluate("JPWNavigation.navigateLocal('tools','leverage')")
    assert page.evaluate("JPWNavigation.current().canonical") == 'tools-leverage'


def verify_guide(page):
    steps = page.locator('#jpwLeveragePage [data-leverage-step]')
    assert steps.count() == 7
    assert steps.evaluate_all("nodes=>nodes.map(n=>n.dataset.leverageStep)") == list('1234567')
    for step in steps.all():
        area = step.evaluate("n=>n.closest('[data-genetrix-panel]').dataset.genetrixPanel")
        open_area(page, area)
        assert step.is_visible()
        assert step.locator('h2').is_visible()
        assert any(node.is_visible() for node in step.locator(':scope > p, :scope > ol, :scope > .leverage-editor-flow').all()), step.get_attribute('data-leverage-step')
        assert step.evaluate("n=>!n.closest('details')"), 'Essential steps must stay exposed'
    assert page.locator('.leverage-glossary dt').all_text_contents() == [
        'MetaTrader 5 (MT5)', 'MetaEditor', 'Indicador', 'Script',
        'Expert Advisor (EA)', 'Arquivos .mq5, .mqh e .ex5']
    assert 'documentação oficial MQL5 da MetaQuotes' in \
        page.locator('.leverage-official-ref').text_content()
    assert page.locator('.leverage-official-ref a').count() == 0
    assert page.locator('.leverage-editor-flow>div').count() == 3
    assert 'Compilar com F7' in page.locator('.leverage-editor-flow').text_content()
    assert page.locator('.leverage-folder-map strong').all_text_contents() == [
        'Indicators', 'Include', 'Scripts', 'Experts', 'Images']
    open_area(page, 'install')
    assert page.locator('.leverage-package--source [data-jpw-leverage-download="source"]').is_enabled()
    assert page.locator('.leverage-package--compiled [data-jpw-leverage-download="compiled"]').is_enabled()
    open_area(page, 'validation')
    validation = page.locator('[data-genetrix-panel="validation"]')
    assert validation.locator('[data-jpw-leverage-meta="version"]').text_content() == MANIFEST['version']
    assert SOURCE['filename'] in validation.locator('[data-jpw-leverage-meta="source-status"]').text_content()
    assert COMPILED['filename'] in validation.locator('[data-jpw-leverage-meta="compiled-status"]').text_content()
    validation_hash = validation.locator('.genetrix-validation-integrity > summary')
    validation_hash.focus(); page.keyboard.press('Enter')
    assert validation_hash.evaluate('n=>n.parentElement.open')
    assert validation.locator('[data-jpw-leverage-meta="source-sha"]').text_content() == SOURCE['sha256']
    page.keyboard.press('Enter')
    assert not validation_hash.evaluate('n=>n.parentElement.open')
    release = page.locator('.leverage-release-details summary')
    release.focus()
    page.keyboard.press('Enter')
    assert release.evaluate('n=>n.parentElement.open')
    assert MANIFEST['coverage'] in page.locator('.leverage-release-details').text_content()
    page.keyboard.press('Enter')
    assert not release.evaluate('n=>n.parentElement.open')
    open_area(page, 'install')
    integrity = page.locator('.leverage-package--source .leverage-package-integrity summary')
    integrity.click()
    assert SOURCE['sha256'] in page.locator('.leverage-package--source .leverage-package-integrity').text_content()
    integrity.click()
    assert 'Não substitua a pasta MQL5 inteira.' in page.locator('#jpwLeverageInstall').text_content()
    reveal_target(page, 'jpwLeverageInstall')
    page.locator('.leverage-file-table').evaluate("n=>{let a=n.parentElement;while(a){if(a.tagName==='DETAILS')a.open=true;a=a.parentElement;}}")
    rows = page.locator('.leverage-file-table tbody tr')
    expected_destinations = {
        'JPW_Alavancagem_Atual.mq5': 'MQL5/Indicators/JPWealth/',
        'JPW_NoCuda_Channels.mq5': 'MQL5/Indicators/JPWealth/',
        'JPW_NoCuda_Core.mqh': 'MQL5/Include/JPWealth/',
        'JPW_NoCuda_Projection_Core.mqh': 'MQL5/Include/JPWealth/',
        'JPW_NoCuda_Projection.mqh': 'MQL5/Include/JPWealth/',
        'JPW_NoCuda_Store.mqh': 'MQL5/Include/JPWealth/',
        'JPW_NoCuda_Terminal.mqh': 'MQL5/Include/JPWealth/',
        'JPW_NoCuda_Render.mqh': 'MQL5/Include/JPWealth/',
        'JPW_NoCuda_UI.mqh': 'MQL5/Include/JPWealth/',
        'JPW_NoCuda_Core_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_NoCuda_Store_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_NoCuda_Projection_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Core.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_MDD.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Terminal.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Profile.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Genesis_Core.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Genesis_Store.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_RaizN_Core.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_RaizN_Store.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_RaizN_Config.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_RaizN_Live.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_RaizN_Horizon.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_RaizN_Factor.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_RaizN_Observer.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Panel.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Cockpit.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_StopRisk_Core.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_StopRisk_Store.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_StopRisk_Terminal.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Observer_Presence.mqh': 'MQL5/Include/JPWealth/',
        'JPW_Alavancagem_Observer.mq5': 'MQL5/Experts/JPWealth/ · legado para rollback; não usar junto do Monitor',
        'JPW_Alavancagem_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Metrics_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Verificar_USC.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Profile_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Consultar_MDD.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Genesis_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Genesis_Store_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_RaizN_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_RaizN_Store_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_RaizN_Config_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_RaizN_Live_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_RaizN_Horizon_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_RaizN_Factor_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Observer_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_Panel_Tests.mq5': 'MQL5/Scripts/JPWealth/',
        'JPW_Alavancagem_StopRisk_Tests.mq5': 'MQL5/Scripts/JPWealth/',
    }
    expected_destinations.update({"JPW_Alavancagem_" + name + ".mqh": "MQL5/Include/JPWealth/"
                                  for name in ['Actions', 'Coordinator', 'Diagnostics', 'Diagnostics_Core', 'Presentation', 'Samples', 'Store_Result', 'Version']})
    expected_destinations["JPW_Alavancagem_Diagnostics_Tests.mq5"] = "MQL5/Scripts/JPWealth/"
    expected_destinations.update({"JPW_SignalCopy_"+name+".mqh":"MQL5/Include/JPWealth/" for name in ("Types", "Core", "Terminal", "Controller", "UI")})
    expected_destinations["JPW_SignalCopy_Tests.mq5"]="MQL5/Scripts/JPWealth/"
    expected_destinations["JPW_Alavancagem_Positions.mqh"]="MQL5/Include/JPWealth/"
    expected_destinations["JPW_Alavancagem_Positions_Tests.mq5"]="MQL5/Scripts/JPWealth/"
    expected_destinations.update({"JPW_NoCuda_Fibo_" + name + ".mqh": "MQL5/Include/JPWealth/"
                                  for name in ("Core", "Terminal", "Store", "Sync", "Controller", "UI")})
    expected_destinations["JPW_UI_Focus.mqh"] = "MQL5/Include/JPWealth/"
    expected_destinations["JPW_NoCuda_Fibo_Tests.mq5"] = "MQL5/Scripts/JPWealth/"
    expected_destinations["JPW_NoCuda_Fibo_Lab.mq5"] = "MQL5/Scripts/JPWealth/ · laboratório isolado"
    expected_destinations["JPW_NoCuda_Logo.bmp"] = "MQL5/Images/JPWealth/ · recurso incorporado na compilação"
    expected_destinations["JPW_Genetrix_Brand.mqh"] = "MQL5/Include/JPWealth/"
    expected_destinations.update({"JPW_Genetrix_Logo_"+theme+"_"+str(scale)+".bmp": "MQL5/Images/JPWealth/ · recurso incorporado na compilação" for theme in ("Light", "Dark") for scale in (100,125,150,200)})
    expected_destinations.update({"JPW_Genetrix_" + name + ".mqh": "MQL5/Include/JPWealth/"
                                  for name in ("Ledger_Bridge", "Ledger_Core", "Ledger_Store", "Ledger_Terminal",
                                               "Risk_Core", "Risk_Store", "Risk_Terminal", "UI")})
    expected_destinations.update({"JPW_Genetrix_" + name + ".mq5": "MQL5/Experts/JPWealth/"
                                  for name in ("Accountant", "Supervisor")})
    expected_destinations.update({"JPW_PersonalHistory_" + name + ".mqh": "MQL5/Include/JPWealth/"
                                  for name in ("Controller", "Core", "Export", "Store", "Terminal", "UI")})
    expected_destinations.update({name: "MQL5/Scripts/JPWealth/" for name in
                                  ("JPW_Genetrix_Ledger_Tests.mq5", "JPW_Genetrix_Risk_Tests.mq5",
                                   "JPW_PersonalHistory_Tests.mq5")})
    expected_destinations.update({name: "Referência no ZIP · não copiar para MQL5" for name in
                                  ("AGENTS.md", "GENETRIX_7X_LEDGER.md", "GENETRIX_PERSONAL_HISTORY.md", "README.md")})
    expected_destinations['JPW_Genetrix_Accountant.mq5'] = 'MQL5/Experts/JPWealth/ · legado para rollback; não usar junto do Monitor'
    expected_destinations['JPW_Genetrix_Supervisor.mq5'] = 'MQL5/Experts/JPWealth/ · opcional; outro gráfico; não armar nesta validação'
    expected_destinations['JPW_Genetrix_Monitor.mq5'] = 'MQL5/Experts/JPWealth/ · núcleo recomendado; gráfico de apoio dedicado'
    expected_destinations.update({name: 'MQL5/Include/JPWealth/' for name in (
        'JPW_Genetrix_Monitor_Core.mqh', 'JPW_Genetrix_Monitor_Status.mqh', 'JPW_Genetrix_Monitor_UI.mqh',
        'JPW_Genetrix_Observer_Runtime.mqh', 'JPW_Genetrix_Accountant_Runtime.mqh',
        'JPW_Genetrix_Ledger_Preparation.mqh', 'JPW_UI_Design.mqh')})
    expected_destinations.update({name: 'Referência no ZIP · não copiar para MQL5' for name in
        {'GENETRIX_REPAIR_1_18_1.md', 'GENETRIX_COMPILE_FIX_1_18_2.md', 'GENETRIX_UI_1_19_0.md',
         'GENETRIX_CORE_1_20_0.md'} | HARNESS_MEMBERS})
    assert len(expected_destinations) == rows.count() == 126
    assert {row.locator('th').text_content(): row.locator('td').text_content()
            for row in rows.all()} == expected_destinations
    assert 'não são compilados separadamente' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_Consultar_MDD.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_RaizN_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_RaizN_Store_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_RaizN_Config_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_RaizN_Live_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_RaizN_Horizon_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_RaizN_Factor_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_Observer_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_Observer.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_Panel_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_Alavancagem_StopRisk_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_NoCuda_Channels.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_NoCuda_Core_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_NoCuda_Store_Tests' in page.locator('#jpwLeverageTests').text_content()
    assert 'JPW_NoCuda_Projection_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    assert 'JPW_NoCuda_Projection_Tests' in page.locator('#jpwLeverageTests').text_content()
    assert 'Allow Algo Trading / Permitir negociação algorítmica desmarcado' in page.locator('#jpwLeverageTests').text_content()
    assert 'Experts' in page.locator('#jpwLeverageTests').text_content()
    assert 'Não comprova a leitura dos contratos' in page.locator('#jpwLeverageTests').text_content()
    assert '10.000 USC = US$ 100' in page.locator('#jpwLeverageUSC').text_content()
    assert 'último equity informado pelo terminal' in page.locator('#jpwLeverageUse').text_content()
    assert 'horário do servidor' in page.locator('#jpwLeverageUse').text_content()
    assert page.locator('#jpwLeverageUse .leverage-quality dt').all_text_contents() == [
        'Current', 'Estimated', 'N/A']
    guide = page.locator('#jpwLeverageUse').text_content()
    assert 'JPW: Leverage 2,75x · Current' in guide
    assert 'JPW: Leverage ≈2,75x · Estimated' in guide
    assert 'Floating P/L: +1,25%' in guide
    assert 'Genesis SL: 3,52%' in guide
    assert 'Raiz N diag. 1W: ≈3,29% · F1,5 · Estimated' in guide
    assert 'Raiz N diag. 2W: ≈4,65% · F1,5 · Estimated' in guide
    assert 'Cockpit → Raiz N' in guide and 'Cockpit → Stops' in guide
    assert 'Stop risk: 250 USC · 2,50% balance · Current' in guide
    assert 'InpUpdateSeconds' in guide and '30 segundos' in guide and '5 segundos' in guide
    assert 'não garante intervalos exatos' in guide
    assert 'DD / saldo: 3,00%' in guide and 'não é uma linha adicional' in guide
    assert 'sete linhas pequenas e cinzas' in guide
    assert 'O Cockpit separa resumo, Stops, Raiz N' in guide
    cockpit = page.locator('#jpwLeverageCockpit').text_content()
    assert page.locator('#jpwLeverageCockpit').count() == 1
    for phrase in ('sete cartões', 'Estado dos dados', 'última captura registrada',
                   'LAST · NOT ACTIVE',
                   'não comprova que o EA está ativo agora', 'Cockpit → Ajustes',
                   'Restaurar padrão', 'gráfico atual', 'modelo/template do MT5',
                   'teste nativo isolado', 'Ocultar não desliga'):
        assert phrase in cockpit, phrase
    assert 'O indicador não salva nem sobrescreve modelos por conta própria' in cockpit
    for phrase in ('1.13.0', '1040 × 760 px', 'aba ativa', 'controle em foco',
                   'preserva as fórmulas e os registros locais'):
        assert phrase in cockpit, phrase
    assert page.locator('#jpwLeverageCockpit .leverage-cockpit-map dt').all_text_contents() == [
        'Visão geral', 'Stops', 'Raiz N', 'Sistema', 'Histórico Pessoal', 'Ajustes']
    cockpit_guide = page.locator('#jpwLeverageCockpit').text_content()
    for phrase in ('tabela única', 'ticket completo', 'volume', 'Leverage individual', 'nocional bruto', 'equity', 'Operação', 'Conta', 'rolagem', 'Fechar', 'Esc', 'NOT_RUN'):
        assert phrase in cockpit_guide, phrase
    reveal_target(page, 'jpwLeverageSignalCopy')
    signal = page.locator('#jpwLeverageSignalCopy')
    assert signal.is_visible()
    assert page.locator('#jpwLeverageSignalCopy').count() == 1
    for phrase in ('Preparar mensagem', 'SL', 'TP', 'Raiz N', 'Estimated', 'Ctrl+C',
                   'NOT_RUN', 'MQL5/Files/JPWealth/SignalCopy/', 'não envia',
                   'pendente', 'conta', 'símbolo'):
        assert phrase in signal.text_content(), phrase
    assert 'JPW_SignalCopy_Tests.mq5' in page.locator('#jpwLeverageCompile').text_content()
    reveal_target(page, 'jpwLeverageNoCuda')
    channels = page.locator('#jpwLeverageNoCuda')
    assert channels.is_visible()
    assert page.locator('#jpwLeverageNoCuda').count() == 1
    for phrase in ('1.16.1', 'JPW_NoCuda_Channels', 'não precisa do EA observador',
                   'Canal de Fibonacci do próprio MT5', '65 níveis', '−4 a +4', '0,125',
                   'não desloca as âncoras', 'ajustes no período de referência',
                   'suspende a sincronização', 'última captura íntegra salva',
                   'Tick, zoom, rolagem e consulta não criam revisões',
                   '90% do gráfico', 'Compacta · Ampla · Maximizada',
                   'padrão 11', '9 a 24', 'UNVERIFIED_NATIVE', 'N/A', 'NOT_RUN',
                   'geometria importada, interação e prontidão operacional continuam pendentes',
                   'referência geométrica inclinada', 'se o canal for mantido',
                   'não prevê onde estará a cotação', '12h e média dos extremos podem diferir',
                   'AAAA.MM.DD', 'Data do servidor', 'Linha selecionada', 'Consultar dia'):
        assert phrase in channels.text_content(), phrase
    assert channels.locator('.leverage-daily-readings dt').all_text_contents() == [
        'Início · 00h', 'Meio do dia · 12h', 'Fim · 24h',
        'Média dos extremos', 'Faixa do dia']
    assert channels.locator('.leverage-cockpit-map dt').all_text_contents() == [
        'Canal', 'Agora', 'Projeção', 'Registro', 'Aparência']
    primary = channels.locator('details.genetrix-resource-detail > summary')
    primary.click()
    assert primary.evaluate('n=>n.parentElement.open')
    # Each disclosure remains reachable by keyboard and tests its own contract.
    disclosures = [
        ('Por que a linha 5', ('descrição visível', 'nível numérico',
          '1 → −1; 3 → −0,75; 5 → −0,50; 9 → 0; 17 → +1',
          'não limita o canal', 'correções posteriores no histórico', 'validação nativa pendente')),
        ('Quero continuar usando', ('modo manual legado', 'A → B → C', 'recolhe o painel',
          'barra encerrada', 'Close', 'Arrastar', 'não grava automaticamente',
          'C não é automaticamente um terceiro contato', 'Confirmar versão', 'Cancelar rascunho')),
        ('H1 e H4:', ('30 dias civis', '14 dias civis encerrados',
          'sete dias adicionais', 'Sem sessão', 'sem faixa', 'Estimated',
          '00/04/08/12/16/20', 'Não se divide uma contagem H1 por quatro',
          'Falta, barra extra', 'Cotação recente não valida calendário',
          'nada altera o calendário da Raiz N', 'feriados', 'horário de verão')),
        ('Arquivos adicionais', ('JPW_NoCuda_Fibo_Tests.mq5', 'JPW_NoCuda_Fibo_Lab.mq5',
          'JPW_NoCuda_Logo.bmp', 'MQL5/Images/JPWealth/', 'sem autoaprovação da geometria')),
    ]
    for title, phrases in disclosures:
        summary = channels.locator('details summary').filter(has_text=title)
        assert summary.count() == 1
        summary.focus()
        page.keyboard.press('Enter')
        assert summary.evaluate('n=>n.parentElement.open')
        detail = summary.locator('..').text_content()
        for phrase in phrases:
            assert phrase in detail, phrase
        page.keyboard.press('Enter')
        assert not summary.evaluate('n=>n.parentElement.open')
    assert 'Nocuda_Tool.mq5' in channels.text_content()
    assert 'não recebe migração automática' in channels.text_content()
    stops = page.locator('#jpwLeverageStopRisk').text_content()
    assert page.locator('#jpwLeverageStopRisk').count() == 1
    for phrase in ('Saldo Inicial de Referência', 'saldo atual', 'OrderCalcProfit',
                   'max(0, −lucro hipotético)', 'reserva separada', 'Cockpit → Stops',
                   'execução → SL', 'mercado → SL', 'N/A protege contra total parcial',
                   'stop-limit não suportado', 'netting', 'mesma instalação/conta',
                   'Check Observer'):
        assert phrase in stops, phrase
    assert 'publicação pendente ou falha' in stops
    help_text = page.locator('#jpwLeverageHelp').text_content()
    assert 'Amplie para ler a tabela' in help_text
    assert 'InpCockpitFontSize' in help_text
    viewer = page.locator('#jpwLeverageMDDViewer').text_content()
    assert 'JPW_Alavancagem_Consultar_MDD' in viewer
    assert 'Navegador → Scripts → JPWealth' in viewer
    assert 'Algo Trading desmarcado' in viewer
    assert 'amostra vencedora em UTC do relógio do computador' in viewer
    assert 'não uma série temporal' in viewer
    assert 'DD / saldo atual ou estimado' in viewer
    assert 'não altera as sete linhas do gráfico' in viewer
    assert 'Ausência de registro não significa máximo zero' in viewer
    assert 'MDD pico-a-vale' in viewer
    assert 'Experts' in viewer and 'arquivos locais de log' in viewer
    assert page.locator('#jpwLeverageMDDViewer').count() == 1
    genesis = page.locator('#jpwLeverageGenesis').text_content()
    assert 'InpGenesisTicket=0' in genesis and 'Bid − SL' in genesis and 'SL − Ask' in genesis
    assert 'inferência' in genesis and 'não confirma execução' in genesis
    assert page.locator('#jpwLeverageGenesis').count() == 1
    raiz = page.locator('#jpwLeverageRaizN').text_content()
    assert 'Raiz N diag. 1W: ≈3,29% · F1,5 · Estimated' in raiz
    assert 'Raiz N diag. 2W: ≈4,65% · F1,5 · Estimated' in raiz
    assert 'F 1,5/1,8' in raiz and 'Aplicar' in raiz and 'Cancelar' in raiz
    assert 'Dpreço = ATR × √N × F' in raiz
    assert 'D% = 100 × Dpreço / P0' in raiz
    assert '98,332% com F 1,5' in raiz and '99,593% com F 1,8' in raiz
    assert '2Φ(√(8/π) × F) − 1' in raiz
    assert '1W e 2W têm a mesma porcentagem' in raiz
    assert 'P-21 permanece PENDING' in raiz
    assert 'probabilidade remanescente de um SL real' in raiz
    assert 'última barra concluída' in raiz
    assert 'fechamentos H4 esperados' in raiz
    assert 'Não é o período 55 do ATR' in raiz
    assert '3,2863' in raiz and '3,9436' in raiz and 'sintético' in raiz
    assert '7 e 14 dias civis do servidor' in raiz
    assert 'último tick disponível do símbolo' in raiz
    assert 'sem alegar janela iniciada no presente verificado' in raiz
    assert 'calendário datado aprovado' in raiz and 'Estimated' in raiz
    assert 'Esta revisão não traz hash de calendário aprovado' in raiz
    assert 'JPW_Genetrix_Monitor' in raiz
    assert 'não envia ordens nem altera stops' in raiz
    assert 'Reconstructed' in raiz and 'preço da decisão humana' in raiz
    # Legacy scenarios are supplementary content in the new advanced disclosure.
    reveal_target(page, 'jpwLeverageRaizN')
    page.locator('#jpwLeverageRaizN details.genetrix-resource-detail > summary').click()
    advanced = page.locator('#jpwLeverageRaizN details summary').filter(has_text='Cenários declarados')
    advanced.focus()
    page.keyboard.press('Enter')
    assert advanced.evaluate("n=>n.parentElement.open")
    advanced_text = advanced.locator('..').text_content()
    assert 'retrospectiva' in advanced_text and 'ticket' in advanced_text
    assert 'sem migração ou reescrita' in advanced_text
    page.keyboard.press('Enter')
    assert not advanced.evaluate("n=>n.parentElement.open")
    assert 'não escolhe stop' in raiz
    assert page.locator('#jpwLeverageRaizN').count() == 1
    how = page.locator('#jpwLeverageHow').text_content()
    assert '100 × P / B' in how and '100 × max(0, B − E) / B' in how
    assert 'Crédito da conta é contexto' in how
    assert 'Em USC, B, E e P ficam na unidade original' in how
    assert 'Não é um MDD pico-a-vale' in how
    assert 'relógio do computador' in how
    assert 'O site não lê nem distribui o arquivo' in how
    assert 'fonte 8' in page.locator('#jpwLeverageUse').text_content()
    # The essential path stays in ordinary document flow; only extra explanations collapse.
    reveal_target(page, 'jpwLeverageUSC')
    summary = page.locator('#jpwLeverageUSC summary')
    summary.focus()
    page.keyboard.press('Enter')
    assert summary.evaluate("n=>n.parentElement.open")
    page.evaluate("window.dispatchEvent(new PopStateEvent('popstate'));window.dispatchEvent(new HashChangeEvent('hashchange'))")
    page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
    assert summary.evaluate('n=>n===document.activeElement'), 'Duplicate history events must not steal disclosure focus'
    assert 'MQL5/Files/JPWealth/Alavancagem/' in page.locator('#jpwLeverageUSC details').text_content()
    page.keyboard.press('Enter')
    assert not summary.evaluate("n=>n.parentElement.open")
    open_area(page, 'overview')



def open_area(page, area):
    page.locator('[data-genetrix-tab="' + area + '"]').click()
    page.locator('[data-genetrix-panel="' + area + '"]').wait_for(state='visible')
    assert page.locator('[data-genetrix-panel]:visible').count() == 1
    for node in page.locator('[data-genetrix-panel]').all():
        assert node.evaluate('n=>n.hidden===n.inert')


def reveal_target(page, target):
    page.evaluate("id=>location.hash=id", target)
    page.locator('#' + target).wait_for(state='visible')
    page.wait_for_function("id=>document.activeElement.id===id", arg=target)
    page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')


def verify_navigation_contract(page):
    # Exercise real controls/controller; no direct changes to application state.
    state_before = page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})')
    assert page.locator('[data-genetrix-tab]').all_text_contents() == ['Visão geral', 'Instalar', 'Recursos', 'Validação', 'Ajuda']
    page.evaluate("history.replaceState(null,'',location.pathname)")
    # Original URL has no fragment: Back must restore overview instead of Install.
    page.locator('[data-genetrix-tab="install"]').click()
    page.go_back()
    page.wait_for_function("JPWTools.genetrix.getView()==='overview'")
    assert not page.evaluate('location.hash')
    page.locator('[data-genetrix-tab="overview"]').focus()
    for key, area in [('ArrowRight','install'),('End','help'),('Home','overview'),('ArrowLeft','help'),('ArrowRight','overview')]:
        page.keyboard.press(key)
        assert page.locator('[data-genetrix-tab="'+area+'"]').get_attribute('aria-selected') == 'true'
        assert page.evaluate('document.activeElement.dataset.genetrixTab') == area
        assert page.locator('[data-genetrix-panel]:visible').count() == 1
    page.locator('[data-genetrix-open="install"]').first.click()
    assert page.locator('[data-genetrix-panel="install"]').is_visible()
    open_area(page, 'overview')
    page.locator('[data-genetrix-open="resources"]').first.click()
    assert page.locator('[data-genetrix-panel="resources"]').is_visible()
    legacy = ['jpwLeverageOverview','jpwGenetrixDefinition','jpwLeverageDownloads','jpwLeverageInstall','jpwLeverageCompile','jpwLeverageTests','jpwLeverageUSC','jpwLeverageUse','jpwLeverageCockpit','jpwLeverageSignalCopy','jpwLeverageNoCuda','jpwLeverageStopRisk','jpwLeverageGenesis','jpwLeverageRaizN','jpwLeverageMDDViewer','jpwLeverageHow','jpwLeverageHelp']
    for target in legacy:
        reveal_target(page,target)
        assert page.evaluate("id=>{let n=document.getElementById(id);for(;n;n=n.parentElement){if(n.tagName==='DETAILS'&&!n.open)return false;}return true;}",target)
        assert page.evaluate("JPWNavigation.current().canonical") == 'tools-leverage'
    open_area(page,'overview'); open_area(page,'install')
    page.go_back()
    page.wait_for_function("JPWTools.genetrix.getView()==='overview'")
    page.go_forward()
    page.wait_for_function("JPWTools.genetrix.getView()==='install'")
    assert page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})') == state_before
    reveal_target(page,'jpwLeverageNoCuda')
    page.reload();wait_bootstrap(page)
    page.wait_for_function("document.activeElement.id==='jpwLeverageNoCuda'")
    assert page.locator('#jpwLeverageNoCuda').is_visible()
    state_after_reload = page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})')
    before_unknown = page.evaluate("JSON.stringify({view:JPWTools.genetrix.getView(),route:JPWNavigation.current().canonical})")
    for fragment in ('#unknown-genetrix','#jpwLeverageNoCuda%20','#%3Cscript%3E','#jpwLeverageNoCuda[onclick]'):
        page.evaluate('hash=>location.hash=hash',fragment)
        page.wait_for_timeout(60)
        assert page.evaluate("JSON.stringify({view:JPWTools.genetrix.getView(),route:JPWNavigation.current().canonical})") == before_unknown
    assert page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})') == state_after_reload
    illustration = page.locator('#jpwLeveragePage').text_content()
    assert 'Prévia ilustrativa · dados fictícios' in illustration
    # The Genetrix wordmark must be the original red asset, including offline/portable.
    image = page.locator('[data-genetrix-brand]')
    assert image.count() == 1
    encoded = image.get_attribute('src')
    assert encoded.startswith('data:image/png;base64,')
    assert base64.b64decode(encoded.split(',',1)[1]) == (ROOT/'assets/jp-wealth-brand-red.png').read_bytes()
    assert image.evaluate('n=>n.complete&&n.naturalWidth>0')
    print('PASS five tabs, keyboard,17legacy IDs,history,unknown hashes,original logo andno writes',flush=True)
    open_area(page,'overview')


def verify_guide_geometry(page, layout):
    original_theme = page.locator('html').get_attribute('data-theme')
    for width in (1440, 390, 320):
        page.set_viewport_size({'width': width, 'height': 900})
        for theme in ('light', 'dark'):
            page.evaluate("theme=>document.documentElement.dataset.theme=theme", theme)
            page.locator('#jpwLeveragePage details').evaluate_all('nodes=>nodes.forEach(n=>n.open=false)')
            for area in ('overview', 'install', 'resources', 'validation', 'help'):
                open_area(page, area)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (layout, width, theme, area)
                assert page.locator('[data-leverage-step]').count() == 7
                bad = page.locator('#jpwLeveragePage :is(button,a,summary)').evaluate_all("""nodes=>nodes.filter(n=>{
                  const r=n.getBoundingClientRect(); return r.width>0&&r.height>0&&(r.height<44||r.width<44);
                }).map(n=>({text:n.textContent,width:n.offsetWidth,height:n.offsetHeight}))""")
                assert not bad, (layout, width, theme, area, bad)
                assert not page.locator('[data-genetrix-panel]:visible').evaluate("n=>n.scrollWidth>n.clientWidth+1"), (layout, width, theme, area)
                assert page.locator('#jpwLeveragePage :is(.genetrix-resource-facts dd,.genetrix-evidence-flow p,.leverage-validation dd,.genetrix-limit,.genetrix-scope-note)').evaluate_all("nodes=>nodes.every(n=>parseFloat(getComputedStyle(n).fontSize)>=16)"), (layout,width,theme,'body16px')
                if EVIDENCE_DIR is not None and layout == 'sidebar':
                    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
                    page.locator('#jpwLeveragePage').screenshot(path=str(EVIDENCE_DIR / f'{area}-{width}-{theme}.png'))
            open_area(page, 'install')
            page.locator('.leverage-file-table').evaluate("n=>{let a=n.parentElement;while(a){if(a.tagName==='DETAILS')a.open=true;a=a.parentElement;}}")
            assert page.locator('.leverage-file-table').evaluate("n=>n.scrollWidth<=n.clientWidth+1"), (layout,width,theme)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            print('PASS five-area geometry', layout, width, theme, flush=True)
    page.evaluate("theme=>document.documentElement.dataset.theme=theme", original_theme)
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.evaluate("document.documentElement.style.zoom='2'")
    for area in ('overview','install','resources','validation','help'):
        open_area(page,area)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (layout,area,'200%')
        assert not page.locator('[data-genetrix-panel]:visible').evaluate('n=>n.scrollWidth>n.clientWidth+1'), (layout,area,'200%')
        if EVIDENCE_DIR is not None and layout=='sidebar':
            page.locator('#jpwLeveragePage').screenshot(path=str(EVIDENCE_DIR/f'{area}-zoom200.png'))
    page.evaluate("document.documentElement.style.zoom=''")
    open_area(page, 'overview')
    print('PASS200percent reflow',layout,flush=True)


def verify_archive(raw):
    assert len(raw) == SOURCE['bytes']
    assert sha256(raw).hexdigest() == SOURCE['sha256']
    with ZipFile(BytesIO(raw)) as bundle:
        listed_names = bundle.namelist()
        names = set(listed_names)
        assert len(listed_names) == len(names) == 127
        assert EXPECTED == names, names
        assert names == {Path(path).relative_to('mt5/jpw-alavancagem-atual').as_posix()
                         for path in MANIFEST['sourceFiles']}, names
        for name in names:
            assert bundle.read(name) == (ROOT / 'mt5/jpw-alavancagem-atual' / name).read_bytes(), name


def verify_compiled_archive(raw):
    assert len(raw) == COMPILED['bytes']
    assert sha256(raw).hexdigest() == COMPILED['sha256']
    native = {Path(item['path']).relative_to('mt5/jpw-alavancagem-atual').as_posix(): item['sha256']
              for item in MANIFEST['nativeArtifact']['artifacts']}
    assert set(native) == EXPECTED_EX5
    with ZipFile(BytesIO(raw)) as bundle:
        names = bundle.namelist()
        assert len(names) == len(set(names)) == 34
        assert set(names) == EXPECTED_EX5 | {'README.md'}
        assert bundle.read('README.md') == (ROOT/'mt5/jpw-alavancagem-atual/README.md').read_bytes()
        for name in EXPECTED_EX5:
            content = bundle.read(name)
            assert len(content) >= 1024
            assert sha256(content).hexdigest() == native[name]
            assert content == (ROOT/'mt5/jpw-alavancagem-atual'/name).read_bytes()


def download_from_page(page, kind='source'):
    open_area(page, 'install')
    if kind == 'compiled':
        disclosure = page.locator('.genetrix-compiled-details')
        if not disclosure.evaluate('n=>n.open'):
            disclosure.locator(':scope > summary').click()
    record = SOURCE if kind == 'source' else COMPILED
    with page.expect_download() as pending:
        page.locator('[data-jpw-leverage-download="'+kind+'"]').click()
    artifact = pending.value
    assert artifact.suggested_filename == record['filename']
    raw = Path(artifact.path()).read_bytes()
    (verify_archive if kind == 'source' else verify_compiled_archive)(raw)
    assert 'verificado' in page.locator('#jpwLeverageDownloadStatus').text_content()


def main():
    assert SOURCE['available'] is True and ARCHIVE.is_file(), 'source package not built'
    verify_archive(ARCHIVE.read_bytes())
    assert COMPILED['available'] is True and COMPILED_ARCHIVE.is_file(), 'compiled package not built'
    verify_compiled_archive(COMPILED_ARCHIVE.read_bytes())
    # Same static bytes/assertions; existing bounded transport avoids dropped
    # bootstrap scripts under concurrent local loads. No retry or fallback.
    server = BrowserFixtureServer(('127.0.0.1', 0), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    targets = [
        ('HTTP', origin + '/index.html'),
        ('arquivo local', (ROOT / 'index.html').as_uri()),
        ('HTML portátil', (ROOT / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').as_uri()),
    ]
    try:
        with urlopen(origin + '/' + SOURCE['path']) as response:
            assert response.status == 200
            verify_archive(response.read())
        with urlopen(origin + '/' + COMPILED['path']) as response:
            assert response.status == 200
            verify_compiled_archive(response.read())
        with sync_playwright() as playwright:
            chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
            launch_options = {'executable_path': str(chrome)} if chrome.is_file() else {}
            browser = playwright.chromium.launch(
                headless=True, args=['--no-sandbox'], **launch_options)
            for name, target in targets:
                context, page, errors = boot(browser, target)
                try:
                    before = page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})')
                    route_and_inspect(page)
                    verify_guide(page)
                    download_from_page(page)
                    download_from_page(page, 'compiled')
                    assert page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})') == before
                    assert not errors, errors
                    print('PASS', name, 'route, metadata, bytes and extraction', flush=True)
                    if name == 'HTTP':
                        verify_navigation_contract(page)
                        count = []
                        page.on('download', lambda artifact: count.append(artifact.suggested_filename))
                        page.route('**/' + SOURCE['path'], lambda route: route.fulfill(status=404, body='missing'))
                        open_area(page, 'install')
                        page.locator('[data-jpw-leverage-download="source"]').click()
                        page.wait_for_function("document.getElementById('jpwLeverageDownloadStatus').dataset.state==='error'")
                        assert 'não encontrado' in page.locator('#jpwLeverageDownloadStatus').text_content()
                        assert not count
                        print('PASS HTTP missing package fails closed', flush=True)
                        page.unroute('**/' + SOURCE['path'])
                        tampered = bytearray(ARCHIVE.read_bytes()); tampered[-1] ^= 1
                        page.route('**/' + SOURCE['path'], lambda route: route.fulfill(status=200,body=bytes(tampered),content_type='application/zip'))
                        page.locator('[data-jpw-leverage-download="source"]').click()
                        page.wait_for_function("document.getElementById('jpwLeverageDownloadStatus').textContent.includes('Hash do pacote diferente')")
                        assert not count
                        print('PASS HTTP equal-size tampered ZIP refused by SHA-256',flush=True)
                        page.unroute('**/' + SOURCE['path'])
                        page.route('**/' + COMPILED['path'], lambda route: route.fulfill(status=404, body='missing'))
                        # Navigation coverage intentionally closed disclosures. Re-establish
                        # the negative case's visible UI precondition through its summary.
                        compiled_disclosure = page.locator('.genetrix-compiled-details')
                        if not compiled_disclosure.evaluate('n=>n.open'):
                            compiled_disclosure.locator(':scope > summary').click()
                        compiled_button = page.locator('[data-jpw-leverage-download="compiled"]')
                        assert compiled_button.is_visible() and compiled_button.is_enabled()
                        compiled_button.click()
                        page.wait_for_function("document.getElementById('jpwLeverageDownloadStatus').dataset.state==='error'")
                        assert 'não encontrado' in page.locator('#jpwLeverageDownloadStatus').text_content()
                        assert not count
                        page.unroute('**/' + COMPILED['path'])
                        changed = bytearray(COMPILED_ARCHIVE.read_bytes()); changed[-1] ^= 1
                        page.route('**/' + COMPILED['path'], lambda route: route.fulfill(status=200, body=bytes(changed), content_type='application/zip'))
                        compiled_button.click()
                        page.wait_for_function("document.getElementById('jpwLeverageDownloadStatus').textContent.includes('Hash do pacote diferente')")
                        assert not count
                        print('PASS HTTP native missing/tampered archive refused; no download', flush=True)
                finally:
                    context.close()
            for layout in ('sidebar', 'topbar', 'glass', 'submenu'):
                context, page, errors = boot(browser, origin + '/index.html', layout=layout)
                try:
                    page.locator('#toolsNavTrigger').click()
                    item = page.locator('#toolsNavSubmenu [data-nav-child="tools-leverage"]')
                    item.wait_for(state='visible')
                    if layout == 'topbar':
                        item.focus()
                        page.keyboard.press('Enter')
                    else:
                        item.click()
                    route_and_inspect(page)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), layout
                    verify_guide_geometry(page, layout)
                    assert page.evaluate('JPWNavigation.focusCurrentScreen()')
                    assert page.evaluate('document.activeElement.id') == 'jpwLeverageTitle'
                    assert not errors, errors
                    print('PASS layout', layout, 'menu route and focus', flush=True)
                finally:
                    context.close()
            context, page, errors = boot(browser, origin + '/index.html', width=390)
            try:
                page.locator('[data-shell-menu-toggle]').click()
                page.locator('#toolsNavTrigger').click()
                assert page.evaluate('JPWNavigation.current().canonical') == 'dashboard'
                assert page.get_attribute('html', 'data-shell-menu') == 'open'
                page.locator('#toolsNavSubmenu [data-nav-child="tools-leverage"]').click()
                route_and_inspect(page)
                assert page.locator('#sidebarBackdrop').is_hidden()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                assert not errors, errors
                print('PASS mobile drawer and responsive page', flush=True)
            finally:
                context.close()
            context, page, errors = boot(browser, origin + '/index.html', workers='allow')
            try:
                page.evaluate('navigator.serviceWorker.ready')
                page.reload()
                wait_bootstrap(page)
                page.wait_for_function('navigator.serviceWorker.controller!==null')
                context.set_offline(True)
                page.reload()
                wait_bootstrap(page)
                route_and_inspect(page)
                download_from_page(page)
                download_from_page(page, 'compiled')
                assert not errors, errors
                print('PASS PWA offline route and source/native archives', flush=True)
            finally:
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
