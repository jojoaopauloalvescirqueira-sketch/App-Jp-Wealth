#!/usr/bin/env python3
"""NAV-01..NAV-03 — contrato da navegacao semantica.

Prova que a API publica expoe somente as cinco rotas canonicas, enquanto a
fachada legada continua resolvendo destinos fisicos sem promovê-los ao contrato
canônico. Navegação é UI pura: não grava storage, não salva estado financeiro e
a navegacao nao le nem altera o dominio patrimonial do Alladin.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

CANONICAL = [
    ("dashboard", "dash", "dashboard", None),
    ("forex-overview", "exec", "forex", "overview"),
    ("personal-finance", "finpes", "personal-finance", "overview"),
    ("research-forex", "research", "research", "calendar"),
    ("alladin", "alladin", "alladin", None),
]
FOREX_CHILDREN = [
    ("forex-overview", "exec", "overview"),
    ("forex-preparation", "check", None),
    ("forex-account", "contas", None),
    ("forex-operation", "exec", "panel"),
    ("forex-reconciliation", "contab", None),
    ("forex-planning", "fxplan", "overview"),
]
RESEARCH_CHILDREN = [
    ("research-forex", "research", "calendar"),
    ("research-stocks-br", "research", "stocks-br"),
    ("research-stocks-global", "research", "stocks-global"),
    ("research-reits", "research", "reits"),
    ("research-others", "research", "others"),
]
LEGACY = ["dash", "exec", "contas", "contab", "fxplan", "finpes",
          "motor", "history", "check", "tool-check", "ecal", "nocoda",
          "pivots", "params", "config"]
PRIMARY = [
    ("01", "Dashboard", "dashboard", "dashboard"),
    ("02", "Forex", "forex-overview", "forex"),
    ("03", "Finanças Pessoais", "personal-finance", "personal-finance"),
    ("04", "Research", "research-forex", "research"),
    ("05", "Alladin", "alladin", "alladin"),
]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


def launch_browser(playwright):
    candidates = [
        os.environ.get("JP_WEALTH_CHROMIUM", ""),
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        str(Path.home() / "Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
    ]
    executable = next((item for item in candidates if item and Path(item).exists()), None)
    options = {"headless": True, "args": ["--no-sandbox"]}
    if executable:
        options["executable_path"] = executable
    return playwright.chromium.launch(**options)


def boot(browser, url, viewport=None):
    context = browser.new_context(viewport=viewport or {"width": 1440, "height": 900})
    context.add_init_script("""
      window.__onbShown = true;
      window.__navStorageOps = [];
      for (const method of ['setItem', 'removeItem', 'clear']) {
        const original = Storage.prototype[method];
        Storage.prototype[method] = function(...args) {
          window.__navStorageOps.push([method, ...args.map(String)]);
          return original.apply(this, args);
        };
      }
    """)
    page = context.new_page()
    observed = {"pageerror": [], "console": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.on("console", lambda msg: observed["console"].append(msg.text) if msg.type == "error" else None)
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function("""() => window.JPWNavigation
      && typeof window.JPWNavigation.navigate === 'function'
      && window.JPWExec?.ui && window.JPWFin?.ui && window.JPWFx?.ui
      && window.JPWResearch?.ui""")
    page.evaluate("() => { window.alert=()=>{}; window.__navStorageOps=[]; closeModal(); }")
    return context, page, observed


def storage_snapshot(page):
    return page.evaluate("""() => Object.keys(localStorage).sort()
      .map(key => [key, localStorage.getItem(key)])""")


def assert_registry(page):
    routes = page.evaluate("() => window.JPWNavigation.routes()")
    assert [route["id"] for route in routes] == [item[0] for item in CANONICAL], routes
    flat = json.dumps(routes, ensure_ascii=False)
    assert not any(legacy in [route["id"] for route in routes] for legacy in LEGACY), flat
    children = page.evaluate("() => window.JPWNavigation.children('forex')")
    assert [child["id"] for child in children] == [item[0] for item in FOREX_CHILDREN], children
    research = page.evaluate("() => window.JPWNavigation.children('research')")
    assert [child["id"] for child in research] == [item[0] for item in RESEARCH_CHILDREN], research
    assert page.evaluate("() => window.JPWNavigation.children('dashboard')") == []
    assert page.evaluate("() => window.JPWNavigation.children('inexistente')") == []
    resolved = page.evaluate("""targets => targets.map(target => ({
      target, result: window.JPWNavigation.resolve(target)
    }))""", [item[0] for item in CANONICAL] + LEGACY)
    assert all(item["result"] and item["result"].get("accepted") for item in resolved), resolved
    assert page.evaluate("() => window.JPWNavigation.resolve('rota-inexistente').accepted") is False

    # NAV2-H: a superfície e a ação de Settings possuem identidades explícitas.
    check_contract = page.evaluate("""() => ({
      surface: JPWNavigation.resolve('check'),
      settings: JPWNavigation.resolve('tool-check')
    })""")
    assert check_contract["surface"]["canonical"] == "forex-preparation", check_contract
    assert check_contract["surface"]["child"] == "forex-preparation", check_contract
    assert check_contract["surface"]["screen"] == "check", check_contract
    assert check_contract["surface"]["action"] is None, check_contract
    assert check_contract["settings"]["action"] == "settings", check_contract
    assert check_contract["settings"]["leaf"] == "tool-check", check_contract
    assert check_contract["settings"]["primary"] is None, check_contract
    assert check_contract["settings"]["child"] is None, check_contract


def assert_primary_dom(page):
    items = page.evaluate("""() => [...document.querySelectorAll('#nav > .tab[data-route]')].map(button => ({
      n: button.querySelector('.n')?.textContent.trim(),
      label: button.querySelector('.lbl')?.textContent.trim(),
      route: button.dataset.route,
      primary: button.dataset.primary
    }))""")
    assert [(item["n"], item["label"], item["route"], item["primary"]) for item in items] == PRIMARY, items
    assert page.locator("#nav > .tab[data-screen]").count() == 0
    assert page.locator("#fxplanNavSubmenu").count() == 0
    assert page.locator("section#research").count() == 1
    assert page.locator("#nav > #researchNavTrigger").count() == 1
    assert page.locator("#researchNavSubmenu").count() == 1
    assert page.locator("section#alladin").count() == 1
    # ALD-05-S1: SUBSTITUICAO DE CONTRATO, nao remocao de cobertura.
    #
    # Ate aqui o contrato era "a section Alladin nao exibe conteudo economico" —
    # correto enquanto o ledger nao tinha superficie. A slice ALD-05-S1 encerra
    # isso DELIBERADAMENTE: os read-models publicados (transactions, saldo,
    # posicoes) passam a ser projetados em tres destinos proprios.
    #
    # O contrato novo e mais forte, nao mais fraco:
    #   (1) os QUATRO destinos cadastrais continuam congelados em rotulo e ordem;
    #   (2) a proibicao economica continua valendo INTEGRALMENTE neles — agora
    #       com risco real de vazamento, porque existe conteudo economico no
    #       MESMO section;
    #   (3) os tres destinos economicos sao nomeados e verificados aqui, e o
    #       comportamento fail-closed deles tem suite propria
    #       (tools/alladin_ui_ledger_test.py, E11/E12/E13).
    tabs = page.locator("section#alladin #alladinTabs button[data-alladin-view]")
    assert tabs.count() == 7
    rotulos = [tabs.nth(i).inner_text().strip() for i in range(7)]
    assert rotulos[:4] == ["Instrumentos", "Bens", "Contas", "Caixa"], \
        f"destinos CADASTRAIS divergem do congelado: {rotulos[:4]}"
    assert rotulos[4:] == ["Lançamentos", "Saldos", "Posições"], \
        f"destinos ECONOMICOS divergem do contrato ALD-05-S1: {rotulos[4:]}"
    # A varredura economica passa a ser POR PAINEL CADASTRAL: varrer a section
    # inteira proibiria exatamente o que a slice entrega, e afrouxar globalmente
    # deixaria o cadastro sem guarda nenhuma.
    for painel in ("instruments", "assets", "accounts", "cashAccounts"):
        page.evaluate("(v) => JPWAlladinUI.selectView(v)", painel)
        texto = page.locator(f"section#alladin [data-alladin-panel='{painel}']").inner_text()
        for economico in ("R$", "US$", "0,00", "%", "saldo", "patrimônio", "quantidade"):
            assert economico not in texto, \
                f"conteudo economico vazou para o painel cadastral {painel}: {economico}"
    page.evaluate("() => JPWAlladinUI.selectView('instruments')")
    assert page.locator("section#alladin input, section#alladin form").count() == 0, \
        "a superficie ALD-05-S1 e read-only: nenhum formulario na section"


def assert_brand_home_navigation(page):
    """A marca do cabecalho e o caminho de volta ao Dashboard.

    Caracterizacao do contrato inteiro: semantica do controle, nome acessivel
    que descreve o DESTINO, alvo de toque, e as tres formas de acionamento —
    clique, Enter e Espaco. As duas ultimas so sao gratuitas porque o elemento e
    um <button> de verdade; se alguem devolve-lo a <div>, elas param de existir
    sem que nenhum estilo mude, e este teste e quem percebe.
    """
    brand = page.locator("#brandHomeBtn")
    assert brand.count() == 1, "a marca do cabecalho nao e um controle unico"
    semantica = brand.evaluate("""el => ({
      tag: el.tagName, type: el.getAttribute('type'),
      route: el.dataset.route, rotulo: el.getAttribute('aria-label'),
      titulo: el.getAttribute('title'),
      altura: Math.round(el.getBoundingClientRect().height),
      cursor: getComputedStyle(el).cursor,
      imgDecorativa: el.querySelector('img.gd-logo')?.getAttribute('alt') === '',
      wordmarkOculto: el.querySelector('.wordmark')?.getAttribute('aria-hidden') === 'true',
    })""")
    assert semantica["tag"] == "BUTTON", f"a marca precisa ser <button>: {semantica}"
    assert semantica["type"] == "button", f"sem type=button o controle pode submeter: {semantica}"
    assert semantica["route"] == "dashboard", f"rota canonica errada: {semantica}"
    assert semantica["rotulo"] == "Ir para o Dashboard", f"nome acessivel: {semantica}"
    assert semantica["titulo"] == "Ir para o Dashboard", f"title: {semantica}"
    assert semantica["altura"] >= 44, f"alvo de toque menor que 44px: {semantica}"
    assert semantica["cursor"] == "pointer", f"cursor nao indica acao: {semantica}"
    # o nome acessivel descreve o destino; a imagem e o wordmark nao repetem a marca
    assert semantica["imgDecorativa"], f"a logo deveria ser decorativa (alt=''): {semantica}"
    assert semantica["wordmarkOculto"], f"o wordmark deveria sair da arvore a11y: {semantica}"

    # as tres formas de acionamento, sempre partindo de LONGE do dashboard
    for rotulo, acionar in (
        ("clique", lambda: page.locator("#brandHomeBtn").click()),
        ("Enter",  lambda: (page.locator("#brandHomeBtn").focus(), page.keyboard.press("Enter"))),
        ("Espaco", lambda: (page.locator("#brandHomeBtn").focus(), page.keyboard.press(" "))),
    ):
        page.evaluate("() => JPWNavigation.navigate('research-others')")
        antes = active_state(page)
        assert antes["screen"] != "dash", f"[{rotulo}] o caso nao prova nada: ja estava no dashboard"
        storage_antes = storage_snapshot(page)
        acionar()
        page.wait_for_timeout(120)
        depois = active_state(page)
        assert depois["screen"] == "dash", f"[{rotulo}] nao chegou a tela fisica dash: {depois}"
        assert depois["activeScreens"] == ["dash"], f"[{rotulo}] mais de uma tela ativa: {depois}"
        assert depois["primary"] == "dashboard", f"[{rotulo}] primario errado: {depois}"
        assert depois["ariaCurrent"] == "dashboard", f"[{rotulo}] aria-current errado: {depois}"
        assert depois["current"]["canonical"] == "dashboard", f"[{rotulo}] rota canonica: {depois}"
        # navegacao e UI pura: nem a marca escapa dessa regra
        assert storage_snapshot(page) == storage_antes, f"[{rotulo}] a navegacao escreveu no storage"


def active_state(page):
    return page.evaluate("""() => ({
      screen: document.querySelector('#appMain > .screen.active')?.id || null,
      activeScreens: [...document.querySelectorAll('#appMain > .screen.active')].map(el => el.id),
      primary: document.querySelector('#nav > .tab.active')?.dataset.primary || null,
      ariaCurrent: document.querySelector('#nav > .tab[aria-current="page"]')?.dataset.primary || null,
      current: window.JPWNavigation.current()
    })""")


def assert_canonical_navigation(page):
    for route, screen, primary, local_view in CANONICAL:
        accepted = page.evaluate("route => window.JPWNavigation.navigate(route)", route)
        assert accepted is True, route
        state = active_state(page)
        assert state["activeScreens"] == [screen], (route, state)
        assert state["primary"] == primary and state["ariaCurrent"] == primary, (route, state)
        assert state["current"]["canonical"] == route, (route, state)
        if screen == "exec":
            assert page.evaluate("() => window.JPWExec.ui.getView()") == local_view
        if screen == "finpes":
            assert page.evaluate("() => window.JPWFin.ui.getView()") == local_view
        if screen == "research":
            assert page.evaluate("() => window.JPWResearch.ui.getView()") == local_view

    page.evaluate("() => window.JPWExec.ui.selectView('motor')")
    page.click('#nav > .tab[data-route="forex-overview"]')
    assert page.evaluate("() => window.JPWExec.ui.getView()") == "overview"
    page.evaluate("() => window.JPWFin.ui.selectView('cenarios')")
    page.click('#nav > .tab[data-route="personal-finance"]')
    assert page.evaluate("() => window.JPWFin.ui.getView()") == "overview"


def assert_forex_children_and_compatibility(page):
    """NAV2-A..J: defaults, aliases, parent/child e compatibilidade invisível."""
    for route, screen, local_view in FOREX_CHILDREN:
        # A rota canônica deve aplicar o default em toda entrada, inclusive após
        # uma visão local diferente ter sido escolhida.
        if route == "forex-operation":
            page.evaluate("() => JPWExec.ui.selectView('motor')")
        if route == "forex-planning":
            page.evaluate("() => JPWFx.ui.selectView('actuals')")
        assert page.evaluate("route => JPWNavigation.navigate(route)", route) is True
        state = active_state(page)
        assert state["screen"] == screen and state["primary"] == "forex", (route, state)
        assert state["current"]["canonical"] == route, (route, state)
        assert state["current"]["child"] == route, (route, state)
        if local_view:
            surface = "fxplan" if screen == "fxplan" else "exec"
            actual = page.evaluate("surface => surface === 'fxplan' ? JPWFx.ui.getView() : JPWExec.ui.getView()", surface)
            assert actual == local_view, (route, actual)

    # NAV2-C/E/G: compatibilidade preserva owner e informa o filho canônico.
    page.evaluate("() => JPWFx.ui.selectView('table')")
    aliases = [
        ("motor", "exec", "forex-operation", "motor"),
        ("history", "exec", "forex-reconciliation", "history"),
        ("fxplan", "fxplan", "forex-planning", "table"),
    ]
    for target, screen, child, view in aliases:
        assert page.evaluate("target => JPWNavigation.navigate(target)", target) is True
        state = active_state(page)
        assert state["screen"] == screen and state["primary"] == "forex", (target, state)
        assert state["current"]["child"] == child, (target, state)
        assert state["current"]["canonical"] == child, (target, state)
        assert state["current"]["localView"]["view"] == view, (target, state)

    # NAV2-H: `check` abre a superfície de Preparação, nunca Settings.
    assert page.evaluate("() => JPWNavigation.navigate('check')") is True
    check_state = active_state(page)
    assert check_state["screen"] == "check" and check_state["primary"] == "forex", check_state
    assert check_state["current"]["child"] == "forex-preparation", check_state
    assert not page.locator("#settingsOverlay").is_visible()

    # NAV3-D/G: aliases historicos pertencem a Research/Forex e nunca deixam
    # Exec/Forex falsamente ativos.
    for target, view in (("ecal", "calendar"), ("nocoda", "nocoda"), ("pivots", "pivots")):
        assert page.evaluate("target => JPWNavigation.navigate(target)", target) is True
        state = active_state(page)
        assert state["screen"] == "research" and state["primary"] == "research", (target, state)
        assert state["current"]["canonical"] == "research-forex", (target, state)
        assert state["current"]["child"] == "research-forex", (target, state)
        assert state["current"]["localView"] == {"surface": "research", "view": view}, (target, state)


def assert_compatibility_and_atomic_refusal(page):
    # N1-B/NAV2: fachada legada preservada e ligada ao filho canônico.
    page.evaluate("() => navigateToScreen('contas')")
    state = active_state(page)
    assert state["activeScreens"] == ["contas"], state
    assert state["primary"] == "forex", state
    assert state["current"]["child"] == "forex-account", state
    assert "forex-account" not in [route["id"] for route in page.evaluate("() => JPWNavigation.routes()")]
    assert "forex-account" in [route["id"] for route in page.evaluate("() => JPWNavigation.children('forex')")]

    # N1-C: a recusa é validada antes de qualquer efeito observável.
    assert page.evaluate("() => JPWNavigation.navigateLocal('finpes', 'cenarios')") is True
    page.locator('#finpesNavSubmenu [data-nav-sub-view="cenarios"]').focus()
    page.evaluate("() => { window.__navStorageOps=[]; }")
    before_storage = storage_snapshot(page)
    before = page.evaluate("""() => ({
      screen: document.querySelector('#appMain > .screen.active')?.id,
      primary: document.querySelector('#nav > .tab.active')?.dataset.primary,
      view: JPWFin.ui.getView(),
      focus: document.activeElement?.outerHTML,
      current: JPWNavigation.current()
    })""")
    refused = page.evaluate("() => JPWNavigation.navigate('rota-inexistente')")
    after = page.evaluate("""() => ({
      screen: document.querySelector('#appMain > .screen.active')?.id,
      primary: document.querySelector('#nav > .tab.active')?.dataset.primary,
      view: JPWFin.ui.getView(),
      focus: document.activeElement?.outerHTML,
      current: JPWNavigation.current(),
      storageOps: window.__navStorageOps
    })""")
    assert refused is False
    assert after["screen"] == before["screen"]
    assert after["primary"] == before["primary"]
    assert after["view"] == before["view"]
    assert after["focus"] == before["focus"]
    assert after["current"] == before["current"]
    assert after["storageOps"] == []
    assert storage_snapshot(page) == before_storage


def assert_storage_and_alladin_isolation(page):
    result = page.evaluate("""() => {
      const storageBefore = Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]);
      const stateBefore = JSON.stringify(S);
      const alladinBefore = JSON.stringify(S.alladin);
      window.__navStorageOps = [];
      let saves = 0;
      const saveOriginal = window.save;
      window.save = function(){ saves++; return saveOriginal.apply(this, arguments); };
      for (const route of JPWNavigation.routes().map(item => item.id)) JPWNavigation.navigate(route);
      for (const route of JPWNavigation.children('forex').map(item => item.id)) JPWNavigation.navigate(route);
      for (const route of JPWNavigation.children('research').map(item => item.id)) JPWNavigation.navigate(route);
      navigateToScreen('contas');
      JPWNavigation.navigateLocal('exec', 'motor');
      JPWNavigation.navigate('history');
      JPWNavigation.navigate('check');
      JPWNavigation.navigateLocal('research', 'nocoda');
      JPWNavigation.navigate('pivots');
      JPWNavigation.navigate('alladin');
      window.save = saveOriginal;
      return {
        stateEqual: stateBefore === JSON.stringify(S),
        alladinEqual: alladinBefore === JSON.stringify(S.alladin),
        saves,
        storageOps: window.__navStorageOps,
        storageEqual: JSON.stringify(storageBefore) === JSON.stringify(
          Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))
      };
    }""")
    assert result == {
        "stateEqual": True,
        "alladinEqual": True,
        "saves": 0,
        "storageOps": [],
        "storageEqual": True,
    }, result


def assert_keyboard_and_mobile(browser, url, desktop_page):
    research = desktop_page.locator('#nav > .tab[data-route="research-forex"]')
    research.focus()
    research.press("Enter")
    assert active_state(desktop_page)["screen"] == "research"

    context, page, observed = boot(browser, url, {"width": 390, "height": 844})
    try:
        page.evaluate("() => JPWNavigation.navigate('research-forex')")
        page.click('[data-shell-menu-toggle]')
        sizes = page.evaluate("""() => [...document.querySelectorAll('#nav > .tab[data-route]')]
          .map(el => el.getBoundingClientRect().height)""")
        assert len(sizes) == 5 and min(sizes) >= 44, sizes
        page.click('#nav > .tab[data-route="alladin"]')
        state = active_state(page)
        assert state["screen"] == "alladin" and state["primary"] == "alladin", state
        geometry = page.evaluate("""() => ({
          doc: document.documentElement.scrollWidth,
          win: window.innerWidth,
          focusInside: document.getElementById('alladin').contains(document.activeElement)
        })""")
        assert geometry["doc"] <= geometry["win"] + 2, geometry
        assert geometry["focusInside"], geometry
        assert not observed["pageerror"], observed
        assert not observed["console"], observed
    finally:
        context.close()


def assert_static_isolation():
    for path in [
        ROOT / "src/js/40-app/01-navigation.js",
        ROOT / "src/js/40-app/11-operational-shell.js",
    ]:
        text = path.read_text(encoding="utf-8")
        for forbidden in ("localStorage", "sessionStorage", "indexedDB", "S.alladin", "JPWAlladin"):
            assert forbidden not in text, f"{path}: acoplamento proibido {forbidden}"


def main():
    assert_static_isolation()
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            context, page, observed = boot(browser, url)
            try:
                assert_registry(page)
                assert_primary_dom(page)
                assert_brand_home_navigation(page)
                assert_canonical_navigation(page)
                assert_forex_children_and_compatibility(page)
                assert_compatibility_and_atomic_refusal(page)
                assert_storage_and_alladin_isolation(page)
                assert_keyboard_and_mobile(browser, url, page)
                assert not observed["pageerror"], observed
                assert not observed["console"], observed
            finally:
                context.close()
                browser.close()
    finally:
        server.shutdown()
    print("NAVIGATION IA TEST PASS — NAV1..NAV3, primários/filhos, compatibilidade, storage e Alladin isolados")


if __name__ == "__main__":
    main()
