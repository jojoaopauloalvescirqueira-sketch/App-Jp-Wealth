#!/usr/bin/env python3
"""Contrato do segundo nivel do Execution Board (faixa compartilhada).

Cobre a "Verificacao minima" de docs/architecture/NAVIGATION-HIERARCHY.md
aplicada ao Execution Board e as exigencias de equivalencia, navegacao, estado
e nao regressao da tarefa: o Painel Operacional e o proprio #execWidgetGrid
realocado, nunca uma copia, e alternar de workspace nao desmonta nem reseta
estado operacional.

Nenhuma fixture usa dado real: o teste nao cria ordem, nao fecha mes, nao
importa backup e nao toca credencial. As unicas escritas sao marcadores
sinteticos em propriedades de DOM, feitas sem disparar eventos, justamente
para provar identidade de no sem alterar o estado financeiro persistido.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

EXPECTED_VIEWS = ["overview", "panel", "nocoda", "pivots"]
EXPECTED_LABELS = ["Visão Geral", "Painel Operacional", "Estudos NoCoda", "Estudos dos Pivots"]
# Ids dos containers, na mesma ordem de EXPECTED_VIEWS.
EXPECTED_CONTAINERS = ["execOverview", "execWidgetGrid", "execNocoda", "execPivots"]
# Os quatro widgets do Painel Operacional. Comparados como CONJUNTO: a ordem em
# runtime pertence ao motor de grade (13-dashboard-layout.js reparenteia no boot
# conforme o padrao ou a preferencia gravada) e o operador pode reorganiza-la.
# Travar a ordem aqui transformaria uma personalizacao legitima em falha.
EXPECTED_CARDS = sorted(["exec-clearance", "exec-metrics-banners", "exec-phase-grids", "exec-lifo-monitor"])


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


def prepare_page(browser, url, viewport=None):
    context = browser.new_context(viewport=viewport or {"width": 1440, "height": 900})
    context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    observed = {"pageerror": [], "console": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.on(
        "console",
        lambda msg: observed["console"].append(msg.text) if msg.type == "error" else None,
    )
    # Nenhuma requisicao sai da maquina. Origens externas recebem um stub inerte
    # em vez de abort: abortar geraria ERR_FAILED no console e tornaria inutil a
    # assercao de "zero erro de console", que e parte do contrato verificado.
    page.route(
        "**/*",
        lambda route: route.continue_()
        if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url)
    page.wait_for_function("() => window.JPWExec && window.JPWExec.ui")
    return context, page, observed


def open_exec_submenu(page):
    page.click("#execNavTrigger")
    page.wait_for_function("() => execNavTrigger.getAttribute('aria-expanded') === 'true'")


def run_structure(page):
    """Estrutura em fluxo: sem overlay, sem sombra flutuante, altura zero fechada."""
    contract = page.evaluate(
        """() => ({
          directTrigger: document.querySelector('#nav > #execNavTrigger') !== null,
          panelOutsideNav: document.querySelector('#nav #execNavSubmenu') === null,
          structuralOrder: document.querySelector('header').nextElementSibling?.id === 'navSubShell'
            && navSubShell.nextElementSibling?.id === 'gdContextRow',
          sharedShell: document.querySelectorAll('.nav-sub-shell').length === 1,
          panelsInShell: [...document.querySelectorAll('#navSubShell .nav-sub-menu')].map(el => el.id),
          keys: [...document.querySelectorAll('#execNavSubmenu [data-nav-sub-view]')]
            .map(el => el.dataset.navSubView),
          labels: [...document.querySelectorAll('#execNavSubmenu .nav-sub-item-title')]
            .map(el => el.textContent.trim()),
          closedHeight: navSubShell.getBoundingClientRect().height,
          closedClipHeight: document.querySelector('#navSubShell .nav-sub-clip')
            .getBoundingClientRect().height,
          borderBottom: parseFloat(getComputedStyle(navSubShell).borderBottomWidth) || 0,
          position: getComputedStyle(navSubShell).position,
          shadow: getComputedStyle(navSubShell).boxShadow
        })"""
    )
    assert contract["directTrigger"], "acionador deixou de ser filho direto de #nav (quebra Classic/Pill/Kinetic)"
    assert contract["panelOutsideNav"], "painel do segundo nivel entrou dentro de #nav"
    assert contract["structuralOrder"], f"faixa fora da ordem header -> faixa -> contexto: {contract}"
    assert contract["sharedShell"], "existe mais de uma faixa; o contrato preve uma so, compartilhada"
    assert contract["panelsInShell"] == ["execNavSubmenu", "fxplanNavSubmenu"], contract["panelsInShell"]
    assert contract["keys"] == EXPECTED_VIEWS, f"ordem/chaves dos destinos: {contract['keys']}"
    assert contract["labels"] == EXPECTED_LABELS, f"rotulos ou ordem divergentes: {contract['labels']}"
    # "Altura efetiva zero" = nenhuma caixa de conteudo. A faixa mantem a
    # border-bottom transparente que anima para visivel ao abrir; o que precisa
    # estar realmente colapsado e o clipe interno (grid-template-rows:0fr).
    assert contract["closedClipHeight"] == 0, (
        f"conteudo da faixa nao colapsou quando fechada: {contract['closedClipHeight']}"
    )
    assert contract["closedHeight"] <= contract["borderBottom"], (
        f"faixa fechada ocupa {contract['closedHeight']}px alem da borda de {contract['borderBottom']}px"
    )
    assert contract["position"] in ("static", "relative"), f"faixa posicionada: {contract['position']}"
    assert contract["shadow"] in ("none", ""), f"faixa com sombra elevada: {contract['shadow']}"


def run_displacement(page):
    """Expandir desloca fisicamente contexto e conteudo — nao sobrepoe."""
    before = page.evaluate(
        """() => ({
          context: gdContextRow.getBoundingClientRect().top,
          main: appMain.getBoundingClientRect().top
        })"""
    )
    open_exec_submenu(page)
    page.wait_for_timeout(420)
    after = page.evaluate(
        """() => ({
          context: gdContextRow.getBoundingClientRect().top,
          main: appMain.getBoundingClientRect().top,
          shellHeight: navSubShell.getBoundingClientRect().height,
          shellBottom: navSubShell.getBoundingClientRect().bottom,
          contextTop: gdContextRow.getBoundingClientRect().top,
          docWidth: document.documentElement.scrollWidth,
          winWidth: window.innerWidth
        })"""
    )
    assert after["shellHeight"] > 40, f"faixa aberta sem altura util: {after}"
    assert after["context"] > before["context"] + 20, f"contexto nao foi deslocado: {before} -> {after}"
    assert after["main"] > before["main"] + 20, f"conteudo nao foi deslocado: {before} -> {after}"
    assert after["shellBottom"] <= after["contextTop"] + 1, "faixa sobrepoe a faixa de contexto"
    assert after["docWidth"] <= after["winWidth"] + 2, f"overflow horizontal: {after}"


def run_initial_destination(page):
    """Entrar no modulo abre a Visao Geral; apenas um workspace fica visivel."""
    state = page.evaluate(
        """() => ({
          view: window.JPWExec.ui.getView(),
          screens: [...document.querySelectorAll('.screen.active')].map(el => el.id),
          nestedScreens: document.querySelectorAll('#exec .screen').length,
          visible: ['execOverview','execWidgetGrid','execNocoda','execPivots']
            .filter(id => !document.getElementById(id).hidden),
          inert: ['execOverview','execWidgetGrid','execNocoda','execPivots']
            .filter(id => document.getElementById(id).inert),
          current: document.querySelector('#execNavSubmenu [data-nav-sub-view="overview"]')
            ?.getAttribute('aria-current')
        })"""
    )
    assert state["view"] == "overview", f"destino inicial nao e a Visao Geral: {state}"
    assert state["screens"] == ["exec"], f"modulo ativo incorreto: {state['screens']}"
    assert state["nestedScreens"] == 0, "workspace virou .screen aninhada — quebra .screen.active/closest"
    assert state["visible"] == ["execOverview"], f"mais de um workspace visivel: {state['visible']}"
    assert state["inert"] == ["execWidgetGrid", "execNocoda", "execPivots"], f"inert incorreto: {state['inert']}"
    assert state["current"] == "page", "destino ativo sem aria-current"


def run_panel_equivalence(page):
    """Painel Operacional e o #execWidgetGrid original — realocado, nao copiado."""
    page.click('#execNavSubmenu [data-nav-sub-view="panel"]')
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'panel'")
    facts = page.evaluate(
        """() => {
          const grid = document.getElementById('execWidgetGrid');
          const ids = [...document.querySelectorAll('#exec [id]')].map(el => el.id);
          return {
            grids: document.querySelectorAll('#execWidgetGrid').length,
            gridParent: grid.parentElement.id,
            cards: [...grid.children].map(el => el.dataset.layoutCard).filter(Boolean),
            directChildren: grid.querySelectorAll(':scope > [data-layout-card]').length,
            duplicateIds: ids.length - new Set(ids).size,
            operational: ['ecTitle','ecFase','ecDD','ecRisco','ecAlav','phaseContainer',
                          'execLifoMonitor','statusBanner','quarantineBanner','downgradeBanner',
                          'mVRM','iAtr55','lLote','lRisco','archiveOpBtn']
              .filter(id => document.getElementById(id) === null),
            visible: ['execOverview','execWidgetGrid','execNocoda','execPivots']
              .filter(id => !document.getElementById(id).hidden)
          };
        }"""
    )
    assert facts["grids"] == 1, "o Painel Operacional foi duplicado"
    assert facts["gridParent"] == "exec", f"grade saiu de section#exec: {facts['gridParent']}"
    assert sorted(facts["cards"]) == EXPECTED_CARDS, f"widgets do painel mudaram: {facts['cards']}"
    assert facts["directChildren"] == 4, (
        f"widgets deixaram de ser filhos diretos do grid ({facts['directChildren']}) — "
        "13-dashboard-layout.js le apenas ':scope > [data-layout-card]'"
    )
    assert facts["duplicateIds"] == 0, "IDs duplicados dentro de #exec"
    assert not facts["operational"], f"superficies operacionais ausentes: {facts['operational']}"
    assert facts["visible"] == ["execWidgetGrid"], f"workspace visivel incorreto: {facts['visible']}"


def run_state_preservation(page):
    """Alternar workspace nao desmonta o DOM nem reseta estado operacional.

    Duas provas independentes, porque falham por motivos diferentes:

    1. IDENTIDADE DE NO — marcadores em dataset, gravados sem disparar evento e
       portanto sem tocar S. Se a troca de visao recriasse o DOM, sumiriam.
    2. ESTADO REAL — um valor de ATR digitado pelo caminho normal da aplicacao,
       que passa pelos binds e e commitado em S. Escrever `.value` direto NAO
       serve para isto: sem evento o valor nunca chega a S e a primeira
       repintura o zera, o que mediria o render e nao a troca de workspace.

    O valor e sintetico e vive apenas no contexto efemero deste navegador.
    """
    page.evaluate(
        """() => {
          document.getElementById('execClearanceCard').dataset.probe = 'marcador';
          document.getElementById('phaseContainer').dataset.probe = 'grades';
          // O VRM fica sob disclosure; abrir e pre-requisito para digitar.
          const host = document.getElementById('iAtr55').closest('details');
          if (host) host.open = true;
        }"""
    )
    page.fill("#iAtr55", "0.00777")
    page.dispatch_event("#iAtr55", "change")
    committed = page.evaluate("() => document.getElementById('iAtr55').value")
    assert committed == "0.00777", f"pre-condicao falhou: ATR nao aceitou o valor ({committed})"

    page.click('#execNavSubmenu [data-nav-sub-view="overview"]')
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'overview'")
    page.click('#execNavSubmenu [data-nav-sub-view="pivots"]')
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'pivots'")
    page.click('#execNavSubmenu [data-nav-sub-view="panel"]')
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'panel'")

    kept = page.evaluate(
        """() => ({
          card: document.getElementById('execClearanceCard').dataset.probe,
          phases: document.getElementById('phaseContainer').dataset.probe,
          atr: document.getElementById('iAtr55').value,
          disclosure: document.getElementById('iAtr55').closest('details')?.open === true
        })"""
    )
    assert kept["card"] == "marcador" and kept["phases"] == "grades", (
        f"DOM do Painel Operacional foi recriado na troca de workspace: {kept}"
    )
    assert kept["atr"] == "0.00777", f"estado operacional perdido na troca de workspace: {kept}"
    assert kept["disclosure"], "disclosure aberto pelo usuario foi fechado pela troca de workspace"


def run_focus_and_keyboard(page):
    """Roving tabindex, setas, Home/End, Escape e destinos ocultos fora do foco."""
    # `inert` NAO zera a propriedade tabIndex: um botao dentro de um workspace
    # oculto continua reportando tabIndex 0. Medir tabIndex aqui daria um falso
    # negativo. A unica prova honesta e comportamental — tentar focar e conferir
    # que o foco nao assenta. Ha alvo real porque a ajuda contextual
    # (20-ui/09-contextual-help.js) injeta um button.note-i em cada <h2>,
    # inclusive nos workspaces novos.
    blocked = page.evaluate(
        """() => {
          const probe = document.querySelector('#execOverview button, #execPivots button');
          if (!probe) return {found: false, took: null};
          probe.focus();
          return {found: true, took: document.activeElement === probe, hidden: !!probe.closest('[hidden]')};
        }"""
    )
    assert blocked["found"], "sem alvo focavel dentro de workspace oculto — a assercao seria vazia"
    assert blocked["hidden"], "pre-condicao falhou: o alvo nao esta dentro de workspace oculto"
    assert not blocked["took"], "workspace oculto continua na ordem de foco (inert nao aplicado)"

    other = page.evaluate(
        """() => [...document.querySelectorAll('#fxplanNavSubmenu [data-nav-sub-view]')]
             .filter(el => el.tabIndex >= 0).length"""
    )
    assert other == 0, "painel do outro modulo continua tabulavel"

    page.focus("#execNavTrigger")
    page.keyboard.press("ArrowDown")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == "panel", (
        "ArrowDown nao levou ao destino ativo"
    )
    page.keyboard.press("ArrowDown")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == "nocoda"
    page.keyboard.press("Home")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == EXPECTED_VIEWS[0]
    page.keyboard.press("End")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == EXPECTED_VIEWS[-1]
    page.keyboard.press("ArrowRight")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == EXPECTED_VIEWS[0], "setas nao circulam"
    page.keyboard.press("Escape")
    assert page.evaluate("() => document.activeElement.id") == "execNavTrigger", "Escape nao devolveu foco"
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "false"


def run_hover_and_pin(page):
    """Hover transitorio com travessia e delay; clique fixa e resiste."""
    page.hover("#execNavTrigger")
    page.wait_for_function("() => execNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.hover("#execNavSubmenu")
    page.wait_for_timeout(120)
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "true", (
        "travessia acionador -> faixa fechou cedo"
    )
    page.hover("#appMain")
    page.wait_for_timeout(200)
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "true", "delay menor que 300 ms"
    page.wait_for_timeout(420)
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "false", (
        "faixa transitoria nao fechou apos 400 ms"
    )

    page.click("#execNavTrigger")
    assert page.evaluate("() => document.documentElement.dataset.navSubPinned") == "true"
    page.hover("#appMain")
    page.wait_for_timeout(600)
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "true", "pointerleave fechou faixa fixada"
    page.set_viewport_size({"width": 1280, "height": 860})
    page.wait_for_timeout(120)
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "true", "resize fechou faixa fixada"
    page.click("#execNavTrigger")
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "true", "novo clique alternou faixa fixada"
    page.click('#execNavSubmenu [data-nav-sub-view="panel"]')
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "true", "clique interno fechou a faixa"
    page.click("#appMain")
    page.wait_for_timeout(120)
    assert page.get_attribute("#execNavTrigger", "aria-expanded") == "false", "clique externo nao fechou"
    page.set_viewport_size({"width": 1440, "height": 900})


def run_module_switch(page):
    """Trocar de modulo fecha o anterior: nunca dois acionadores expandidos."""
    page.click("#execNavTrigger")
    page.wait_for_function("() => execNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.click("#fxplanNavTrigger")
    page.wait_for_function("() => fxplanNavTrigger.getAttribute('aria-expanded') === 'true'")
    state = page.evaluate(
        """() => ({
          expanded: [...document.querySelectorAll('.nav-sub-trigger')]
            .filter(el => el.getAttribute('aria-expanded') === 'true').map(el => el.id),
          mounted: [...document.querySelectorAll('#navSubShell .nav-sub-menu')]
            .filter(el => !el.hidden).map(el => el.id),
          screens: [...document.querySelectorAll('.screen.active')].map(el => el.id)
        })"""
    )
    assert state["expanded"] == ["fxplanNavTrigger"], f"dois acionadores expandidos: {state['expanded']}"
    assert state["mounted"] == ["fxplanNavSubmenu"], f"painel do modulo anterior segue montado: {state['mounted']}"
    assert state["screens"] == ["fxplan"], state["screens"]

    # Voltar ao Execution Board vindo de outro modulo reabre na Visao Geral.
    page.click("#execNavTrigger")
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'overview'")
    back = page.evaluate(
        """() => ({
          view: window.JPWExec.ui.getView(),
          current: document.querySelector('#execNavSubmenu [data-nav-sub-view="overview"]')
            ?.getAttribute('aria-current')
        })"""
    )
    assert back == {"view": "overview", "current": "page"}, f"retorno ao modulo nao abriu a Visao Geral: {back}"


def run_no_regression(page):
    """As cinco abas globais continuam ativando suas proprias telas."""
    tabs = page.evaluate("() => [...document.querySelectorAll('#nav .tab[data-screen]')].map(el => el.dataset.screen)")
    assert tabs == ["dash", "exec", "contas", "contab", "fxplan"], f"abas globais mudaram: {tabs}"
    for screen in tabs:
        page.click(f'#nav .tab[data-screen="{screen}"]')
        active = page.evaluate("() => document.querySelector('.screen.active')?.id")
        assert active == screen, f"aba {screen} nao ativou a tela homonima (ativa: {active})"
    # Fecha a faixa deixada aberta pelo ultimo clique em acionador.
    page.keyboard.press("Escape")


def run_themes(page):
    """Tres tons distintos em claro e escuro, sem cor isolada."""
    page.click("#execNavTrigger")
    page.wait_for_timeout(420)
    for theme in ("dark", "light"):
        page.evaluate("t => document.documentElement.dataset.theme = t", theme)
        page.wait_for_timeout(120)
        tones = page.evaluate(
            """() => ({
              header: getComputedStyle(document.querySelector('header')).backgroundColor,
              band: getComputedStyle(navSubShell).backgroundColor,
              context: getComputedStyle(gdContextRow).backgroundColor
            })"""
        )
        assert tones["band"] not in ("rgba(0, 0, 0, 0)", "transparent"), f"faixa sem fundo no tema {theme}: {tones}"
        assert tones["band"] != tones["header"], f"faixa igual ao header no tema {theme}: {tones}"
    page.evaluate("() => document.documentElement.dataset.theme = 'dark'")
    page.keyboard.press("Escape")


def run_mobile(browser, url):
    """Mobile: sem overlay, sem sidebar, sem overflow; toque abre a faixa."""
    context, page, observed = prepare_page(browser, url, viewport={"width": 390, "height": 844})
    # Abaixo de 900px o #nav e uma gaveta: o acionador so existe depois de
    # abri-la. Tocar o modulo fecha a gaveta e abre a faixa contextual no fluxo
    # vertical — sem overlay e sem sidebar, conforme o contrato.
    page.click("[data-shell-menu-toggle]")
    page.click("#execNavTrigger")
    page.wait_for_function("() => execNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.wait_for_timeout(420)
    assert page.evaluate("() => document.documentElement.dataset.shellMenu") is None, (
        "gaveta global continuou aberta sobre a faixa contextual"
    )
    facts = page.evaluate(
        """() => ({
          position: getComputedStyle(navSubShell).position,
          height: navSubShell.getBoundingClientRect().height,
          docWidth: document.documentElement.scrollWidth,
          winWidth: window.innerWidth,
          items: [...document.querySelectorAll('#execNavSubmenu [data-nav-sub-view]')]
            .map(el => Math.round(el.getBoundingClientRect().height))
        })"""
    )
    assert facts["position"] in ("static", "relative"), f"faixa vira overlay no mobile: {facts['position']}"
    assert facts["height"] > 40, f"faixa sem altura no mobile: {facts}"
    assert facts["docWidth"] <= facts["winWidth"] + 2, f"overflow horizontal no mobile: {facts}"
    assert all(h >= 44 for h in facts["items"]), f"alvo de toque abaixo de 44px: {facts['items']}"
    page.click('#execNavSubmenu [data-nav-sub-view="panel"]')
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'panel'")
    assert not observed["pageerror"], f"pageerror no mobile: {observed['pageerror']}"
    context.close()


def main():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            run_structure(page)
            run_displacement(page)
            run_initial_destination(page)
            run_panel_equivalence(page)
            run_state_preservation(page)
            run_focus_and_keyboard(page)
            run_hover_and_pin(page)
            run_module_switch(page)
            run_no_regression(page)
            run_themes(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            assert not observed["console"], f"erro de console: {observed['console']}"
            context.close()
            run_mobile(browser, url)
            browser.close()
    finally:
        server.shutdown()
    print("EXEC SUBMENU TEST PASS")


if __name__ == "__main__":
    main()
