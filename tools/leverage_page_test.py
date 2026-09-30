#!/usr/bin/env python3
"""JPW Alavancagem Atual: navegação e pacote público, sem dados de conta."""

from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
import os
from pathlib import Path
import threading
from urllib.request import urlopen
from zipfile import ZipFile

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
MANIFEST = json.loads((ROOT / 'downloads/jpw-alavancagem-atual/manifest.json').read_text())
SOURCE = MANIFEST['downloads']['source']
ARCHIVE = ROOT / SOURCE['path']
EVIDENCE_DIR = Path(os.environ['JPW_LEVERAGE_EVIDENCE_DIR']) if os.environ.get('JPW_LEVERAGE_EVIDENCE_DIR') else None
EXPECTED = {
    'README.md',
    'AGENTS.md',
    'MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5',
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
    assert page.locator('#jpwLeveragePage h1').inner_text() == 'JPW Alavancagem Atual'
    assert 'Exemplo ilustrativo — não representa sua conta.' in page.locator('#jpwLeverageHow').inner_text()
    assert 'não recebe posições, equity, credenciais ou resultados' in page.locator('#jpwLeverageOverview').inner_text()
    assert 'nem lê ou distribui os registros locais' in page.locator('#jpwLeverageOverview').inner_text()
    assert MANIFEST['version'] == '1.10.1'
    for phrase in ('Cockpit 1.10.1', 'seis métricas', 'Stop risk',
                   'saldo atual é informativo', 'Saldo Inicial de Referência',
                   'P-21 canônico permanece PENDING'):
        assert phrase in MANIFEST['coverage']
    assert page.locator('[data-jpw-leverage-meta="version"]').inner_text() == MANIFEST['version']
    assert MANIFEST['validation']['mathematics']['detail'] in page.locator('[data-jpw-leverage-meta="mathematics"]').inner_text()
    assert MANIFEST['validation']['compilation']['detail'] in page.locator('[data-jpw-leverage-meta="compilation"]').inner_text()
    assert MANIFEST['validation']['terminal']['detail'] in page.locator('[data-jpw-leverage-meta="terminal"]').inner_text()
    assert page.locator('[data-jpw-leverage-download="source"]').is_enabled()
    assert page.locator('[data-jpw-leverage-meta="source-sha"]').inner_text() == SOURCE['sha256']
    assert page.locator('[data-jpw-leverage-download="compiled"]').is_disabled()
    assert MANIFEST['downloads']['compiled']['reason'] in page.locator('[data-jpw-leverage-meta="compiled-status"]').inner_text()
    assert page.evaluate("JPWNavigation.navigateLocal('tools','leverage')")
    assert page.evaluate("JPWNavigation.current().canonical") == 'tools-leverage'


def verify_guide(page):
    steps = page.locator('#jpwLeveragePage [data-leverage-step]')
    assert steps.count() == 7
    assert steps.evaluate_all("nodes=>nodes.map(n=>n.dataset.leverageStep)") == list('1234567')
    for step in steps.all():
        assert step.is_visible()
        assert step.locator('.leverage-result').is_visible()
        assert step.evaluate("n=>!n.closest('details')"), 'Essential steps must stay exposed'
    assert page.locator('.leverage-glossary dt').all_text_contents() == [
        'MetaTrader 5 (MT5)', 'MetaEditor', 'Indicador', 'Script',
        'Expert Advisor (EA)', 'Arquivos .mq5, .mqh e .ex5']
    assert 'Não substitua a pasta MQL5 inteira.' in page.locator('#jpwLeverageInstall').inner_text()
    rows = page.locator('.leverage-file-table tbody tr')
    expected_destinations = {
        'JPW_Alavancagem_Atual.mq5': 'MQL5/Indicators/JPWealth/',
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
        'JPW_Alavancagem_Observer.mq5': 'MQL5/Experts/JPWealth/ (necessário para Stop risk; opcional para as outras leituras)',
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
    assert {row.locator('th').inner_text(): row.locator('td').inner_text()
            for row in rows.all()} == expected_destinations
    assert 'não são compilados separadamente' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_Consultar_MDD.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_RaizN_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_RaizN_Store_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_RaizN_Config_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_RaizN_Live_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_RaizN_Horizon_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_RaizN_Factor_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_Observer_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_Observer.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_Panel_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'JPW_Alavancagem_StopRisk_Tests.mq5' in page.locator('#jpwLeverageCompile').inner_text()
    assert 'Allow Algo Trading / Permitir negociação algorítmica desmarcado' in page.locator('#jpwLeverageTests').inner_text()
    assert 'Experts' in page.locator('#jpwLeverageTests').inner_text()
    assert 'Não comprova a leitura dos contratos' in page.locator('#jpwLeverageTests').inner_text()
    assert '10.000 USC = US$ 100' in page.locator('#jpwLeverageUSC').inner_text()
    assert 'último equity informado pelo terminal' in page.locator('#jpwLeverageUse').inner_text()
    assert 'horário do servidor' in page.locator('#jpwLeverageUse').inner_text()
    assert page.locator('.leverage-quality dt').all_text_contents() == [
        'Current', 'Estimated', 'N/A']
    guide = page.locator('#jpwLeverageUse').inner_text()
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
    assert 'seis linhas pequenas e cinzas' in guide
    assert 'O Cockpit separa resumo, Stops, Raiz N' in guide
    cockpit = page.locator('#jpwLeverageCockpit').inner_text()
    assert page.locator('.leverage-page-nav a[href="#jpwLeverageCockpit"]').count() == 1
    for phrase in ('seis cartões', 'Estado dos dados', 'última captura registrada',
                   'LAST · NOT ACTIVE',
                   'não comprova que o EA está ativo agora', 'Cockpit → Ajustes',
                   'Restaurar padrão', 'gráfico atual', 'modelo/template do MT5',
                   'teste nativo isolado', 'Ocultar não desliga'):
        assert phrase in cockpit, phrase
    assert 'O indicador não salva nem sobrescreve modelos por conta própria' in cockpit
    assert page.locator('#jpwLeverageCockpit .leverage-cockpit-map dt').all_text_contents() == [
        'Visão geral', 'Stops', 'Raiz N', 'Sistema', 'Ajustes']
    stops = page.locator('#jpwLeverageStopRisk').inner_text()
    assert page.locator('.leverage-page-nav a[href="#jpwLeverageStopRisk"]').count() == 1
    for phrase in ('Saldo Inicial de Referência', 'saldo atual', 'OrderCalcProfit',
                   'max(0, −lucro hipotético)', 'reserva separada', 'Cockpit → Stops',
                   'execução → SL', 'mercado → SL', 'N/A protege contra total parcial',
                   'stop-limit não suportado', 'netting', 'mesma instalação/conta',
                   'Check Observer'):
        assert phrase in stops, phrase
    assert 'publicação pendente ou falha' in stops
    help_text = page.locator('#jpwLeverageHelp').inner_text()
    assert 'Amplie para ler a tabela' in help_text
    assert 'InpCockpitFontSize' in help_text
    viewer = page.locator('#jpwLeverageMDDViewer').inner_text()
    assert 'JPW_Alavancagem_Consultar_MDD' in viewer
    assert 'Navegador → Scripts → JPWealth' in viewer
    assert 'Algo Trading desmarcado' in viewer
    assert 'amostra vencedora em UTC do relógio do computador' in viewer
    assert 'não uma série temporal' in viewer
    assert 'DD / saldo atual ou estimado' in viewer
    assert 'não altera as seis linhas do gráfico' in viewer
    assert 'Ausência de registro não significa máximo zero' in viewer
    assert 'MDD pico-a-vale' in viewer
    assert 'Experts' in viewer and 'arquivos locais de log' in viewer
    assert page.locator('.leverage-page-nav a[href="#jpwLeverageMDDViewer"]').count() == 1
    genesis = page.locator('#jpwLeverageGenesis').inner_text()
    assert 'InpGenesisTicket=0' in genesis and 'Bid − SL' in genesis and 'SL − Ask' in genesis
    assert 'inferência' in genesis and 'não confirma execução' in genesis
    assert page.locator('.leverage-page-nav a[href="#jpwLeverageGenesis"]').count() == 1
    raiz = page.locator('#jpwLeverageRaizN').inner_text()
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
    assert 'JPW_Alavancagem_Observer.mq5' in raiz
    assert 'não envia ordens nem altera stops' in raiz
    assert 'Reconstructed' in raiz and 'preço da decisão humana' in raiz
    # Legacy scenarios are supplementary content in the new advanced disclosure.
    advanced = page.locator('#jpwLeverageRaizN details summary')
    advanced.focus()
    page.keyboard.press('Enter')
    assert advanced.evaluate("n=>n.parentElement.open")
    advanced_text = page.locator('#jpwLeverageRaizN details').inner_text()
    assert 'retrospectiva' in advanced_text and 'ticket' in advanced_text
    assert 'sem migração ou reescrita' in advanced_text
    page.keyboard.press('Enter')
    assert not advanced.evaluate("n=>n.parentElement.open")
    assert 'não escolhe stop' in raiz
    assert page.locator('.leverage-page-nav a[href="#jpwLeverageRaizN"]').count() == 1
    how = page.locator('#jpwLeverageHow').text_content()
    assert '100 × P / B' in how and '100 × max(0, B − E) / B' in how
    assert 'Crédito da conta é contexto' in how
    assert 'Em USC, B, E e P ficam na unidade original' in how
    assert 'Não é um MDD pico-a-vale' in how
    assert 'relógio do computador' in how
    assert 'O site não lê nem distribui o arquivo' in how
    assert 'fonte 8' in page.locator('#jpwLeverageUse .leverage-details').text_content()
    # The essential path stays in ordinary document flow; only extra explanations collapse.
    summary = page.locator('#jpwLeverageUSC summary')
    summary.focus()
    page.keyboard.press('Enter')
    assert summary.evaluate("n=>n.parentElement.open")
    assert summary.evaluate('n=>n===document.activeElement')
    assert 'MQL5/Files/JPWealth/Alavancagem/' in page.locator('#jpwLeverageUSC details').inner_text()
    page.keyboard.press('Enter')
    assert not summary.evaluate("n=>n.parentElement.open")
    first = page.locator('.leverage-page-nav a').first
    first.focus()
    page.keyboard.press('Tab')
    assert page.evaluate("document.activeElement.getAttribute('href')") == '#jpwLeverageDownloads'
    page.keyboard.press('Enter')
    assert page.url.endswith('#jpwLeverageDownloads')


def verify_guide_geometry(page, layout):
    original_theme = page.locator('html').get_attribute('data-theme')
    for width in (1440, 390, 320):
        page.set_viewport_size({'width': width, 'height': 900})
        for theme in ('light', 'dark'):
            page.evaluate("theme=>document.documentElement.dataset.theme=theme", theme)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (layout, width, theme)
            assert page.locator('[data-leverage-step]').count() == 7
            bad = page.locator('#jpwLeveragePage :is(.leverage-page-nav a,summary)').evaluate_all("""nodes=>nodes.filter(n=>{
              const r=n.getBoundingClientRect(); return r.height<43 || r.width<43;
            }).map(n=>n.textContent)""")
            assert not bad, (layout, width, theme, bad)
            assert page.locator('.leverage-file-table').evaluate("n=>n.scrollWidth<=n.clientWidth+1"), (layout, width, theme)
            for step in page.locator('[data-leverage-step]').all():
                assert step.is_visible()
                assert step.evaluate("n=>n.scrollWidth<=n.clientWidth+1"), (layout, width, theme)
            if EVIDENCE_DIR is not None and layout == 'sidebar':
                EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
                for section in ('Overview', 'Downloads', 'Install', 'Use'):
                    page.locator('#jpwLeverage' + section).screenshot(
                        path=str(EVIDENCE_DIR / f'guide-{section.lower()}-{width}-{theme}.png'))
                metrics = page.locator('#jpwLeveragePage [data-leverage-step]').evaluate_all("""nodes=>nodes.map(n=>({
                    step:n.dataset.leverageStep,width:n.getBoundingClientRect().width,
                    height:n.getBoundingClientRect().height,clientWidth:n.clientWidth,scrollWidth:n.scrollWidth
                }))""")
                (EVIDENCE_DIR / f'geometry-{width}-{theme}.json').write_text(
                    json.dumps({'layout': layout, 'width': width, 'theme': theme,
                                'package_sha256': SOURCE['sha256'], 'steps': metrics}, indent=2))
            print('PASS guide geometry', layout, width, theme, flush=True)
    page.evaluate("theme=>document.documentElement.dataset.theme=theme", original_theme)
    page.set_viewport_size({'width': 1440, 'height': 900})


def verify_archive(raw):
    assert len(raw) == SOURCE['bytes']
    assert sha256(raw).hexdigest() == SOURCE['sha256']
    with ZipFile(BytesIO(raw)) as bundle:
        names = set(bundle.namelist())
        assert EXPECTED <= names, names
        assert names == {Path(path).relative_to('mt5/jpw-alavancagem-atual').as_posix()
                         for path in MANIFEST['sourceFiles']}, names
        for name in names:
            assert bundle.read(name) == (ROOT / 'mt5/jpw-alavancagem-atual' / name).read_bytes(), name


def download_from_page(page):
    with page.expect_download() as pending:
        page.locator('[data-jpw-leverage-download="source"]').click()
    artifact = pending.value
    assert artifact.suggested_filename == SOURCE['filename']
    raw = Path(artifact.path()).read_bytes()
    verify_archive(raw)
    assert 'verificado' in page.locator('#jpwLeverageDownloadStatus').inner_text()


def main():
    assert SOURCE['available'] is True and ARCHIVE.is_file(), 'source package not built'
    verify_archive(ARCHIVE.read_bytes())
    server = ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
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
                    assert page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})') == before
                    assert not errors, errors
                    print('PASS', name, 'route, metadata, bytes and extraction', flush=True)
                    if name == 'HTTP':
                        count = []
                        page.on('download', lambda artifact: count.append(artifact.suggested_filename))
                        page.route('**/' + SOURCE['path'], lambda route: route.fulfill(status=404, body='missing'))
                        page.locator('[data-jpw-leverage-download="source"]').click()
                        page.wait_for_function("document.getElementById('jpwLeverageDownloadStatus').dataset.state==='error'")
                        assert 'não encontrado' in page.locator('#jpwLeverageDownloadStatus').inner_text()
                        assert not count
                        print('PASS HTTP missing package fails closed', flush=True)
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
                assert page.evaluate('JPWNavigation.current().canonical') == 'tools-calendar'
                page.locator('[data-shell-menu-toggle]').click()
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
                assert not errors, errors
                print('PASS PWA offline route and archive', flush=True)
            finally:
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
