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
import json
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

EXPECTED_VIEWS = ["overview", "panel", "ecal", "nocoda", "pivots", "motor"]
EXPECTED_LABELS = ["Visão Geral", "Painel Operacional", "Calendário Econômico",
                   "Estudos NoCoda", "Estudos dos Pivots", "Motor de Lote"]
# Ids dos containers, na mesma ordem de EXPECTED_VIEWS. O Motor de Lote usa o
# proprio #motorWidgetGrid migrado de Configuracoes — nao um container novo.
EXPECTED_CONTAINERS = ["execOverview", "execWidgetGrid", "execEcal", "execNocoda",
                       "execPivots", "motorWidgetGrid"]
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
    # A lista de containers vem de EXPECTED_CONTAINERS, nao de literais inline.
    # Ate esta tarefa a constante existia mas NUNCA era referenciada, e as duas
    # varreduras abaixo repetiam os ids a mao: quem acrescentasse um destino e
    # atualizasse so a constante teria um teste verde sem cobrir o container
    # novo. Injetar a constante fecha essa divergencia na origem.
    containers = json.dumps(EXPECTED_CONTAINERS)
    state = page.evaluate(
        """() => ({
          view: window.JPWExec.ui.getView(),
          screens: [...document.querySelectorAll('.screen.active')].map(el => el.id),
          nestedScreens: document.querySelectorAll('#exec .screen').length,
          visible: %s.filter(id => !document.getElementById(id).hidden),
          inert: %s.filter(id => document.getElementById(id).inert),
          current: document.querySelector('#execNavSubmenu [data-nav-sub-view="overview"]')
            ?.getAttribute('aria-current')
        })""" % (containers, containers)
    )
    assert state["view"] == "overview", f"destino inicial nao e a Visao Geral: {state}"
    assert state["screens"] == ["exec"], f"modulo ativo incorreto: {state['screens']}"
    assert state["nestedScreens"] == 0, "workspace virou .screen aninhada — quebra .screen.active/closest"
    assert state["visible"] == ["execOverview"], f"mais de um workspace visivel: {state['visible']}"
    assert state["inert"] == [c for c in EXPECTED_CONTAINERS if c != "execOverview"], f"inert incorreto: {state['inert']}"
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
            visible: %s.filter(id => !document.getElementById(id).hidden)
          };
        }""" % json.dumps(EXPECTED_CONTAINERS)
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
    # Vizinho seguinte de "panel" na ordem do submenu — deriva de EXPECTED_VIEWS
    # para nao voltar a travar um destino especifico por literal.
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == EXPECTED_VIEWS[
        EXPECTED_VIEWS.index("panel") + 1
    ]
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


def run_economic_calendar(page):
    """Calendario Economico: UM dominio, DUAS instancias visuais.

    O overlay #ecalOverlay e o workspace #execEcal leem o MESMO cache e usam a
    MESMA funcao de render, parametrizada por raiz. O que este teste protege e
    justamente o que a revisao adversarial apontou como sem cobertura: que
    selecionar o destino pinta o workspace (e nao a raiz errada), que os ids do
    overlay nao foram duplicados, e que o bind dos filtros nao se multiplica.
    """
    # Cache determinístico ANTES de entrar no destino: o teste nao pode depender
    # da rede nem do feed publico. Mesma forma que ffNewsReadCache() sanitiza.
    page.evaluate(
        """() => {
          const dia = new Date(); dia.setHours(12, 0, 0, 0);
          localStorage.setItem('jpwealth.ui.ffNews.v1', JSON.stringify({
            fetchedAt: Date.now(),
            payload: {version: 1, generated_at: '2026-08-17T12:00:00Z', events: [
              {title: 'JPW Teste USD', country: 'USD', date: dia.toISOString(),
               impact: 'High', forecast: '1.0', previous: '0.9'},
              {title: 'JPW Teste EUR', country: 'EUR', date: dia.toISOString(),
               impact: 'High', forecast: '2.0', previous: '1.9'}
            ]}
          }));
        }"""
    )
    page.click("#execNavTrigger")
    page.wait_for_function("() => execNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.click('#execNavSubmenu [data-nav-sub-view="ecal"]')
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'ecal'")

    fatos = page.evaluate(
        """() => {
          const ws = document.getElementById('execEcal');
          const ov = document.getElementById('ecalOverlay');
          const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
          const papeis = [...ws.querySelectorAll('[data-ecal-role]')]
            .map(el => el.dataset.ecalRole).sort();
          return {
            visivel: !ws.hidden,
            // O workspace nao pode ter id interno: os 9 do overlay sao globais.
            idsInternos: ws.querySelectorAll('[id]').length,
            duplicados: ids.length - new Set(ids).size,
            papeis,
            // Pintou no lugar certo? O corpo do workspace tem eventos e o do
            // overlay continua vazio (ninguem abriu o modal).
            itensWorkspace: ws.querySelectorAll('.ecal-item').length,
            itensOverlay: ov.querySelectorAll('.ecal-item').length,
            overlayAberto: ov.classList.contains('show'),
            // O chip de moeda nao pode mais usar a classe do Dashboard.
            chipsDashboard: ws.querySelectorAll('.gd-news-cur').length,
            chipsProprios: ws.querySelectorAll('.ecal-cur').length
          };
        }"""
    )
    assert fatos["visivel"], "selecionar o destino nao exibiu #execEcal"
    assert fatos["duplicados"] == 0, "a segunda instancia duplicou ids no documento"
    assert fatos["idsInternos"] == 0, (
        f"workspace ganhou id interno ({fatos['idsInternos']}) — colide com o overlay"
    )
    assert fatos["papeis"] == ["body", "empty", "filters", "freshness", "range"], (
        f"papeis do workspace incompletos: {fatos['papeis']}"
    )
    assert fatos["itensWorkspace"] == 2, (
        f"workspace nao pintou os eventos do cache: {fatos['itensWorkspace']} — "
        "se for 0 com o overlay preenchido, o render recebeu a raiz errada"
    )
    assert fatos["itensOverlay"] == 0, "render do workspace vazou para o overlay"
    assert not fatos["overlayAberto"], "entrar no workspace abriu o modal"
    assert fatos["chipsDashboard"] == 0, "calendario ainda usa .gd-news-cur do Dashboard"
    assert fatos["chipsProprios"] == 2, f"chips proprios ausentes: {fatos['chipsProprios']}"

    # Filtro da instancia: recorte de VIEW, nao do dominio.
    page.click('#execEcal [data-ecal-cur="USD"]')
    filtrado = page.evaluate(
        """() => ({
          itens: document.querySelectorAll('#execEcal .ecal-item').length,
          pressionado: document.querySelector('#execEcal [data-ecal-cur="USD"]')
            .getAttribute('aria-pressed')
        })"""
    )
    assert filtrado["itens"] == 1, f"filtro de moeda nao recortou: {filtrado['itens']}"
    assert filtrado["pressionado"] == "true", "aria-pressed nao acompanhou o filtro"

    # Ida e volta nao multiplica listener: se o bind dos filtros fosse
    # registrado a cada render, um unico clique dispararia N vezes e o
    # contador de itens divergiria depois de varias entradas.
    #
    # A troca usa a API publica, e nao cliques no submenu: a faixa contextual
    # nao permanece aberta entre as iteracoes, e clicar num destino com a faixa
    # recolhida faz o <header> interceptar o ponteiro. O alvo deste laco e o
    # ciclo montar/desmontar do workspace, nao a navegacao — que ja foi
    # exercitada por clique real na entrada deste teste.
    for _ in range(3):
        page.evaluate("() => window.JPWExec.ui.selectView('panel')")
        page.wait_for_function("() => window.JPWExec.ui.getView() === 'panel'")
        page.evaluate("() => window.JPWExec.ui.selectView('ecal')")
        page.wait_for_function("() => window.JPWExec.ui.getView() === 'ecal'")
    page.click('#execEcal [data-ecal-cur="all"]')
    estavel = page.evaluate("() => document.querySelectorAll('#execEcal .ecal-item').length")
    assert estavel == 2, f"apos 3 idas e voltas o workspace divergiu: {estavel}"

    # Fonte unica: o overlay, aberto pela API publica, mostra os MESMOS eventos.
    page.evaluate("() => window.JPWEcal.open()")
    page.wait_for_function("() => ecalOverlay.classList.contains('show')")
    mesmos = page.evaluate(
        """() => ({
          overlay: [...document.querySelectorAll('#ecalOverlay .ecal-title')].map(e => e.textContent),
          workspace: [...document.querySelectorAll('#execEcal .ecal-title')].map(e => e.textContent)
        })"""
    )
    assert mesmos["overlay"] == mesmos["workspace"], (
        f"as duas superficies divergiram: {mesmos}"
    )
    page.evaluate("() => window.JPWEcal.close()")


def run_motor_migration(page):
    """O Motor de Lote migrou de Configuracoes para ca — uma so implementacao."""
    # 1. Alcancavel pelo submenu do Execution Board.
    page.click("#execNavTrigger")
    page.wait_for_function("() => execNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.click('#execNavSubmenu [data-nav-sub-view="motor"]')
    page.wait_for_function("() => window.JPWExec.ui.getView() === 'motor'")

    estrutura = page.evaluate(
        """() => {
          const grid = document.getElementById('motorWidgetGrid');
          return {
            grids: document.querySelectorAll('#motorWidgetGrid').length,
            pai: grid.parentElement.id,
            visivel: !grid.hidden,
            sectionMotor: document.getElementById('motor') !== null,
            // Conteudo operacional intacto, pelos ids que o renderizador usa.
            ids: ['fxUpdateBtn','fxFetchStatus','mExpAlvo','motorBody','profileBody']
              .filter(id => document.getElementById(id) === null),
            linhas: document.querySelectorAll('#motorBody tr').length,
            perfis: document.querySelectorAll('#profileBody tr').length,
            // Atributos vestigiais do motor de layout nao podem voltar: a regra
            // de edicao escopada por TELA congelaria estes controles.
            layoutCards: document.querySelectorAll('#motorWidgetGrid [data-layout-card]').length
          };
        }"""
    )
    assert estrutura["grids"] == 1, "o Motor de Lote foi duplicado"
    assert estrutura["pai"] == "exec", f"grade do Motor fora de section#exec: {estrutura['pai']}"
    assert estrutura["visivel"], "workspace do Motor nao ficou visivel ao ser selecionado"
    assert not estrutura["sectionMotor"], "a section#motor hospedeira continuou existindo"
    assert not estrutura["ids"], f"superficies do Motor ausentes: {estrutura['ids']}"
    assert estrutura["linhas"] > 0, "tabela de instrumentos vazia — renderMotor() nao alcancou o no migrado"
    assert estrutura["perfis"] > 0, "tabela de perfis de risco vazia"
    assert estrutura["layoutCards"] == 0, (
        "cards do Motor voltaram a ter data-layout-card — a regra "
        "html[data-layout-editing] .screen.active [data-layout-card] > * os congelaria"
    )

    # 2. Os controles respondem no lugar novo: os listeners ligados por id no
    #    boot sobrevivem ao no ter mudado de pai.
    page.fill("#mExpAlvo", "0.55")
    page.dispatch_event("#mExpAlvo", "input")
    assert page.evaluate("() => S.expAlvo") == 0.55, "o input de exposicao-alvo parou de gravar"
    page.fill("#mExpAlvo", "0.4")
    page.dispatch_event("#mExpAlvo", "input")

    # 3. Sumiu da Central, sem sobra em nenhuma das cinco estruturas.
    central = page.evaluate(
        """() => ({
          folha: typeof SETTINGS_LEAVES['tool-motor'],
          emGrupo: SETTINGS_GROUPS.some(g => (g.children || []).includes('tool-motor')),
          descMenciona: SETTINGS_GROUPS.some(g => /Motor de Lote/i.test(g.desc || '')),
          transporte: Object.keys(SETTINGS_SCREEN_GRIDS),
          rotaLegada: typeof SCREEN_TO_SETTINGS_LEAF['motor'],
          painel: document.querySelector('[data-settings-slot="tool-motor"]') !== null
        })"""
    )
    assert central["folha"] == "undefined", "folha tool-motor continua registrada"
    assert not central["emGrupo"], "tool-motor continua em children de um grupo"
    assert not central["descMenciona"], "descricao de grupo ainda menciona Motor de Lote"
    assert "tool-motor" not in central["transporte"], (
        "transporte de DOM ainda mapeia tool-motor — restoreLegacySettingsNodes() "
        "arrancaria o grid de dentro de #exec ao fechar a Central"
    )
    assert central["rotaLegada"] == "undefined", "SCREEN_TO_SETTINGS_LEAF ainda desvia motor"
    assert not central["painel"], "painel tool-motor continua no DOM"

    # 4. Abrir e FECHAR a Central nao pode mover o grid — era o risco principal.
    page.evaluate("() => openSettingsModal('about')")
    page.wait_for_timeout(200)
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    depois = page.evaluate(
        "() => ({pai: document.getElementById('motorWidgetGrid').parentElement.id, grids: document.querySelectorAll('#motorWidgetGrid').length})"
    )
    assert depois == {"pai": "exec", "grids": 1}, (
        f"o ciclo abrir/fechar da Central moveu a grade do Motor: {depois}"
    )

    # 5. A Acao Rapida do Dashboard leva ao workspace, e nao a lugar nenhum.
    page.click('#nav .tab[data-screen="dash"]')
    page.wait_for_function("() => document.querySelector('.screen.active')?.id === 'dash'")
    page.evaluate("() => navigateToScreen('motor')")
    rota = page.evaluate(
        """() => ({
          tela: document.querySelector('.screen.active')?.id || null,
          view: window.JPWExec.ui.getView(),
          telasAtivas: document.querySelectorAll('.screen.active').length
        })"""
    )
    assert rota == {"tela": "exec", "view": "motor", "telasAtivas": 1}, (
        f"navigateToScreen('motor') nao caiu no workspace: {rota}"
    )

    # 6. O NoCoda continua consumindo a mesma fonte canonica de instrumentos.
    fonte = page.evaluate(
        """() => {
          const cat = instrumentCatalog();
          const linhas = [...document.querySelectorAll('#motorBody tr td:first-child')]
            .map(td => instrumentId(td.textContent));
          return {
            catalogo: cat.length,
            todosNoMotor: cat.every(i => linhas.includes(i.id)),
            semLista: typeof window.NOCODA_INSTRUMENTS === 'undefined'
          };
        }"""
    )
    assert fonte["catalogo"] > 0, "catalogo de instrumentos vazio"
    assert fonte["todosNoMotor"], "Motor e catalogo divergiram — deixaram de compartilhar a fonte"
    assert fonte["semLista"], "surgiu uma lista paralela de instrumentos"


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
            run_economic_calendar(page)
            run_motor_migration(page)
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
