#!/usr/bin/env python3
"""NAV-03 — contrato estrutural e comportamental de Research.

Caracteriza ownership, N2/N3, aliases, empty states, isolamento de storage e
acessibilidade em navegador real. Usa somente estado sintético e bloqueia rede
externa com respostas inertes para que erro de ambiente não pareça erro do app.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

PRIMARY = ["dashboard", "forex-overview", "personal-finance", "research-forex", "alladin"]
RESEARCH_CHILDREN = [
    ("research-forex", "Forex", "calendar"),
    ("research-stocks-br", "Ações", "stocks-br"),
    ("research-stocks-global", "Stocks", "stocks-global"),
    ("research-reits", "REITs", "reits"),
    ("research-probability-lab", "Laboratório de Probabilidade", "probability-lab"),
    ("research-others", "Others", "others"),
]
RESEARCH_FOREX_VIEWS = ["calendar", "nocoda", "pivots"]
EXEC_VIEWS = ["overview", "panel", "motor", "history"]
WORKSPACES = ["execEcal", "execNocoda", "execPivots"]


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


def boot(browser, url, viewport):
    context = browser.new_context(viewport=viewport, service_workers="block")
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
    observed = {"pageerror": [], "console": [], "requestfailed": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.on("console", lambda msg: observed["console"].append(msg.text) if msg.type == "error" else None)
    page.on("requestfailed", lambda req: observed["requestfailed"].append(req.url))
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function("""() => window.JPWNavigation && window.JPWResearch?.ui
      && window.JPWExec?.ui && window.JPWFin?.ui && window.JPWFx?.ui""")
    page.evaluate("() => { window.alert=()=>{}; closeModal(); window.__navStorageOps=[]; }")
    return context, page, observed


def snapshot(page):
    return page.evaluate("""() => ({
      screen: document.querySelector('#appMain > .screen.active')?.id || null,
      primary: document.querySelector('#nav > .tab.active')?.dataset.primary || null,
      primaryAria: document.querySelector('#nav > .tab[aria-current="page"]')?.dataset.primary || null,
      current: JPWNavigation.current(),
      researchView: JPWResearch.ui.getView(),
      execView: JPWExec.ui.getView(),
      focus: document.activeElement?.outerHTML || null,
      storage: Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]),
      storageOps: window.__navStorageOps.slice()
    })""")


def assert_registry_and_dom(page):
    assert [item["id"] for item in page.evaluate("() => JPWNavigation.routes()")] == PRIMARY
    children = page.evaluate("() => JPWNavigation.children('research')")
    assert [(item["id"], item["label"], item["localView"]["view"]) for item in children] == RESEARCH_CHILDREN
    assert page.evaluate("() => JPWNavigation.children('research-forex')") == []

    n2 = page.evaluate("""() => [...document.querySelectorAll(
      '#researchNavSubmenu [data-nav-level="2"] [data-nav-child]')].map(el => ({
        id: el.dataset.navChild,
        label: el.querySelector('.nav-sub-item-title')?.textContent.trim()
      }))""")
    assert [(item["id"], item["label"]) for item in n2] == [item[:2] for item in RESEARCH_CHILDREN]
    n3 = page.evaluate("""() => [...document.querySelectorAll(
      '#navLocalSlot [data-nav-context="research-forex"] [data-nav-local-view]')]
      .map(el => el.dataset.navLocalView)""")
    assert n3 == RESEARCH_FOREX_VIEWS
    assert page.locator('#appSidebar [data-nav-context]').count() == 0
    assert page.locator('#navLocalSlot [data-nav-context^="research-"]:not([data-nav-context="research-forex"])').count() == 0

    assert page.locator("#nav > #researchNavTrigger").count() == 1
    assert page.locator("#appSidebar #nav #researchNavSubmenu").count() == 1
    for workspace in WORKSPACES:
        assert page.locator(f"#{workspace}").count() == 1, workspace
        assert page.locator(f"#research > #{workspace}").count() == 1, workspace
        assert page.locator(f"#exec > #{workspace}").count() == 0, workspace

    # Exec expõe somente as quatro views canônicas. Os aliases antigos podem
    # existir como shims, mas jamais mantêm Exec ativo ou criam estado paralelo.
    for view in EXEC_VIEWS:
        assert page.evaluate("view => JPWExec.ui.selectView(view)", view) is True
        assert page.evaluate("() => JPWExec.ui.getView()") == view
    for legacy, research_view in (("ecal", "calendar"), ("nocoda", "nocoda"), ("pivots", "pivots")):
        assert page.evaluate("legacy => JPWExec.ui.selectView(legacy)", legacy) is True
        state = snapshot(page)
        assert state["screen"] == "research" and state["primary"] == "research", state
        assert state["current"]["child"] == "research-forex", state
        assert state["researchView"] == research_view, state


def assert_routes_aliases_and_empty_states(page):
    for route, _label, view in RESEARCH_CHILDREN:
        page.evaluate("() => JPWResearch.ui.selectView('pivots')")
        assert page.evaluate("route => JPWNavigation.navigate(route)", route) is True
        state = snapshot(page)
        assert state["screen"] == "research" and state["primary"] == "research", (route, state)
        assert state["primaryAria"] == "research", (route, state)
        assert state["current"]["canonical"] == route and state["current"]["child"] == route, state
        assert state["researchView"] == view, (route, state)

    aliases = (("ecal", "calendar"), ("nocoda", "nocoda"), ("pivots", "pivots"))
    for alias, view in aliases:
        assert page.evaluate("alias => JPWNavigation.navigate(alias)", alias) is True
        state = snapshot(page)
        assert state["screen"] == "research" and state["primary"] == "research", (alias, state)
        assert state["current"]["canonical"] == "research-forex", state
        assert state["current"]["child"] == "research-forex", state
        assert state["current"]["localView"] == {"surface": "research", "view": view}, state
        assert not page.locator("#exec").evaluate("el => el.classList.contains('active')")

    empty_ids = ["researchStocksBr", "researchStocksGlobal", "researchReits", "researchOthers"]
    combined = "\n".join(page.locator(f"#{item}").inner_text() for item in empty_ids)
    assert not re.search(r"(?:R\$|US\$|\$|€|£|¥|\b\d+[.,]?\d*%|\b\d{2,}\b)", combined), combined
    for item in empty_ids:
        root = page.locator(f"#{item}")
        assert root.count() == 1
        assert root.locator("input, form, table, canvas, [data-layout-card], .metric").count() == 0
    assert "Brasil" in page.locator("#researchStocksBr").inner_text()
    assert "B3" in page.locator("#researchStocksBr").inner_text()
    assert page.locator("#researchProbabilityLab #galtonBoardRoot").count() == 1
    assert page.locator("#settingsModal [data-galton-root]").count() == 0


def assert_atomic_and_storage(page):
    assert page.evaluate("() => JPWNavigation.navigateLocal('research', 'nocoda')") is True
    page.click("#researchNavTrigger")
    page.locator('#navLocalSlot [data-nav-local-surface="research"][data-nav-local-view="nocoda"]').focus()
    page.evaluate("() => { window.__navStorageOps=[]; }")
    before = snapshot(page)
    assert page.evaluate("() => JPWNavigation.navigate('research-inexistente')") is False
    after = snapshot(page)
    assert after == before, json.dumps({"before": before, "after": after}, ensure_ascii=False)

    result = page.evaluate("""() => {
      const storageBefore = Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]);
      const stateBefore = JSON.stringify(S);
      const alladinBefore = JSON.stringify(S.alladin);
      window.__navStorageOps=[];
      let saves=0;
      const original=window.save;
      window.save=function(){saves++;return original.apply(this,arguments);};
      for(const route of JPWNavigation.children('research').map(item=>item.id)) JPWNavigation.navigate(route);
      for(const view of ['calendar','nocoda','pivots']) JPWNavigation.navigateLocal('research',view);
      for(const alias of ['ecal','nocoda','pivots']) JPWNavigation.navigate(alias);
      window.save=original;
      return {
        stateEqual:stateBefore===JSON.stringify(S),
        alladinEqual:alladinBefore===JSON.stringify(S.alladin),
        saves,
        storageOps:window.__navStorageOps,
        storageEqual:JSON.stringify(storageBefore)===JSON.stringify(
          Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))
      };
    }""")
    assert result == {"stateEqual": True, "alladinEqual": True, "saves": 0,
                      "storageOps": [], "storageEqual": True}, result


def assert_shell_and_accessibility(page, viewport, theme):
    page.evaluate("theme => { document.documentElement.dataset.theme=theme; }", theme)
    mobile = viewport["width"] <= 900
    if mobile:
        page.click("[data-shell-menu-toggle]")
    page.click("#researchNavTrigger")
    expander = '[data-nav-expand="research"]'
    page.wait_for_function("() => document.querySelector('[data-nav-expand=research]').getAttribute('aria-expanded') === 'true'")
    page.wait_for_function("() => JPWResearch.ui.getView() === 'calendar'")
    assert page.locator('#researchNavSubmenu [data-nav-child="research-forex"]').get_attribute("aria-current") == "page"
    assert page.locator('#navLocalSlot [data-nav-local-surface="research"][data-nav-local-view="calendar"]').get_attribute("aria-current") == "page"

    if mobile:
        assert page.evaluate("() => document.documentElement.dataset.shellMenu") is None
        assert page.evaluate("() => research.contains(document.activeElement)")
        page.click("[data-shell-menu-toggle]")
    page.click('#researchNavSubmenu [data-nav-child="research-stocks-br"]')
    assert page.evaluate("() => JPWResearch.ui.getView()") == "stocks-br"
    context = page.locator('#navLocalSlot [data-nav-context="research-forex"]')
    assert context.is_hidden()
    assert context.evaluate("el => el.inert") is True

    if mobile:
        page.click("[data-shell-menu-toggle]")
    page.click('#researchNavSubmenu [data-nav-child="research-forex"]')
    assert page.evaluate("() => JPWResearch.ui.getView()") == "calendar"
    assert not context.is_hidden()
    assert context.evaluate("el => el.inert") is False
    page.click('#navLocalSlot [data-nav-local-surface="research"][data-nav-local-view="pivots"]')
    assert page.evaluate("() => JPWResearch.ui.getView()") == "pivots"

    if mobile:
        page.click("[data-shell-menu-toggle]")
    page.focus(expander)
    page.keyboard.press("ArrowDown")
    assert page.evaluate("() => document.activeElement.dataset.navChild") == "research-forex"
    page.keyboard.press("End")
    assert page.evaluate("() => document.activeElement.dataset.navChild") == "research-others"
    page.keyboard.press("Home")
    assert page.evaluate("() => document.activeElement.dataset.navChild") == "research-forex"
    # Medir enquanto N2 esta aberto: alvos ocultos nao tornariam a prova util.
    targets = page.locator('#researchNavSubmenu [data-nav-child]').evaluate_all(
        "els => els.map(el=>({width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}))")
    assert len(targets) == len(RESEARCH_CHILDREN), targets
    assert all(item["width"] >= 44 and item["height"] >= 44 for item in targets), targets
    page.keyboard.press("Escape")
    focus = page.evaluate("""() => ({
      expander:document.activeElement.dataset.navExpand,
      toggle:document.activeElement.matches('[data-shell-menu-toggle]'),
      insideHiddenSubmenu:!!document.activeElement.closest?.('#researchNavSubmenu')
    })""")
    if mobile:
        assert not focus["insideHiddenSubmenu"] and focus["toggle"], ("mobile focus return", focus)
        assert page.evaluate("() => document.documentElement.dataset.shellMenu") is None
    else:
        assert focus["expander"] == "research", ("focus return", focus)
        assert page.get_attribute(expander, "aria-expanded") == "false"

    # N3 tem alcance proprio e continua disponivel com a lateral recolhida.
    assert context.is_visible()
    context.locator('[data-nav-local-view="calendar"]').focus()
    page.keyboard.press("End")
    assert page.evaluate("() => document.activeElement.dataset.navLocalView") == "pivots"
    page.keyboard.press("Home")
    assert page.evaluate("() => document.activeElement.dataset.navLocalView") == "calendar"

    layout = page.evaluate("""mobile => ({
      activeScreens:[...document.querySelectorAll('#appMain > .screen.active')].map(el=>el.id),
      overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
      visibleResearch:[...document.querySelectorAll('#research > [data-research-view]')]
        .filter(el=>!el.hidden).map(el=>el.id),
      targets:[...document.querySelectorAll('#navLocalSlot [data-nav-context="research-forex"] button')]
        .filter(el=>{const r=el.getBoundingClientRect();return r.width>0&&r.height>0})
        .map(el=>({label:el.textContent.trim(),width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}))
    })""", mobile)
    assert layout["activeScreens"] == ["research"], layout
    assert layout["visibleResearch"] == ["execPivots"], layout
    assert layout["overflow"] <= 1, (viewport, theme, layout)
    assert layout["targets"] and all(item["width"] >= 44 and item["height"] >= 44 for item in layout["targets"]), layout


def assert_calendar_refresh_guidance(page):
    # A mesma agenda atende workspace/modal; sua orientação deve alcançar o
    # único botão real de atualização, sem criar outra consulta ou dado em S.
    page.wait_for_function("() => !ffNewsInFlight")
    page.evaluate("() => { localStorage.removeItem(FF_NEWS_CACHE_KEY); JPWNavigation.navigate('ecal'); }")
    before = page.evaluate("JSON.stringify(S)")
    expected = "Forex → Visão Geral"
    workspace = page.locator('#execEcal [data-ecal-role="empty"]')
    assert workspace.is_visible()
    assert expected in workspace.inner_text(), workspace.inner_text()
    page.evaluate("() => JPWEcal.open()")
    overlay = page.locator('#ecalOverlay [data-ecal-role="empty"]')
    assert overlay.is_visible() and expected in overlay.inner_text(), overlay.inner_text()
    page.locator('#ecalCloseBtn').press('Escape')
    assert not page.locator('#ecalOverlay').is_visible()
    page.wait_for_function("() => !ffNewsInFlight")
    calls = []
    feed = {"version":1,"generated_at":"2026-09-10T00:00:00Z","events":[{
        "title":"Synthetic calendar event","country":"USD","date":"2026-09-10T15:00:00Z",
        "impact":"High","forecast":"1","previous":"0"}]}
    def reply(route):
        calls.append(route.request.url)
        route.fulfill(status=200, content_type='application/json', body=json.dumps(feed))
    page.route('**/ff-high-impact.json*', reply)
    page.evaluate("() => JPWNavigation.navigate('forex-overview')")
    button = page.locator('#gdNewsRefreshBtn')
    assert button.is_visible() and page.locator('#fxOverviewWidgets #gdNewsRefreshBtn').count()==1
    button.focus()
    button.press('Enter')
    page.wait_for_function("() => !ffNewsInFlight && ffNewsReadCache()?.events.length===1")
    assert len(calls)==1, calls
    for _ in range(3):
        page.evaluate("() => JPWNavigation.navigate('ecal')")
        assert 'Synthetic calendar event' in page.locator('#execEcal').inner_text()
        page.evaluate("() => JPWNavigation.navigate('dashboard')")
        page.evaluate("() => JPWNavigation.navigate('forex-overview')")
    assert len(calls)==1, 'navegação duplicou consulta'
    assert page.evaluate('JSON.stringify(S)')==before, 'agenda alterou estado financeiro'



def assert_lab_relocation(page):
    # A13: a preferência antiga, inclusive extensões, permanece byte-idêntica.
    old_pref=json.loads((ROOT/'data/samples/galton-preferences-v1.json').read_text())
    old_pref['a13SyntheticExtension']={'preserve':True}
    raw=json.dumps(old_pref,separators=(',',':'))
    page.evaluate("JPWNavigation.navigate('dashboard')")
    page.evaluate("raw=>localStorage.setItem('jpwealth_galton_preferences_v1',raw)",raw)
    before=page.evaluate("JSON.stringify(S)")
    rows=[]
    for mode in ['sidebar','topbar']:
        for width in [1440,390]:
            order=(['research','alladin','personal-finance','forex','dashboard'] if width==1440
                   else ['alladin','forex','dashboard','personal-finance','research'])
            page.evaluate('order=>applyNavOrder(order)',order)
            page.set_viewport_size({'width':width,'height':900 if width==1440 else 844})
            page.evaluate("mode=>mountNavigationLayout(mode)",mode)
            page.evaluate("JPWNavigation.navigate('research-forex')")
            if width<=900 and mode=='sidebar':
                page.locator('[data-shell-menu-toggle]').click()
            target=page.locator('[data-nav-child="research-probability-lab"]')
            target.focus();target.press('Enter')
            row=page.evaluate("""() => ({
              primary:JPWNavigation.current().primary,child:JPWNavigation.current().child,
              view:JPWResearch.ui.getView(),roots:document.querySelectorAll('[data-galton-root]').length,
              inResearch:!!document.querySelector('#researchGaltonSlot [data-galton-root]'),
              inSettings:!!document.querySelector('#settingsModal [data-galton-root]'),
              active:!!document.querySelector('[data-galton-root]')?.__galtonController?.active,
              focusInResearch:document.getElementById('research').contains(document.activeElement),
              title:document.getElementById('shellLocation').textContent,
              order:[...document.querySelectorAll('#nav > .tab[data-primary]')].map(el=>el.dataset.primary),
              forexVisible:!!document.getElementById('gdContextRow').getClientRects().length,
              overflow:document.documentElement.scrollWidth-innerWidth
            })""")
            print('A13_MODE_OBSERVATION '+json.dumps({'mode':mode,'width':width,**row},ensure_ascii=False),flush=True)
            assert row['primary']=='research' and row['child']=='research-probability-lab' and row['view']=='probability-lab',row
            assert row['roots']==1 and row['inResearch'] and not row['inSettings'] and row['active'] and row['focusInResearch'],row
            assert 'Laboratório de Probabilidade' in row['title'] and row['overflow']<=1,row
            assert row['order']==order and not row['forexVisible'],row
            rows.append({'mode':mode,'width':width,**row})
            left=page.evaluate("""() => {
              const c=document.querySelector('[data-galton-root]').__galtonController;
              JPWNavigation.navigate('dashboard');
              return {same:document.querySelector('[data-galton-root]').__galtonController===c,
                active:c.active,destroyed:c.destroyed,manualPaused:c.manualPaused,
                running:c.snapshot().running,raf:c.raf,observerActive:c.resizeObserverActive};
            }""")
            assert left=={'same':True,'active':False,'destroyed':False,'manualPaused':True,
                          'running':False,'raf':0,'observerActive':False},left
            assert page.evaluate("localStorage.getItem('jpwealth_galton_preferences_v1')")==raw

    page.set_viewport_size({'width':1440,'height':900})
    page.evaluate("mountNavigationLayout('sidebar')")
    for alias in ['probability-lab','galton-board']:
        assert page.evaluate("id=>JPWNavigation.navigate(id)",alias) is True
        assert page.evaluate("JPWNavigation.current().child")=='research-probability-lab'
    # As entradas antigas redirecionam; não deixam um laboratório oculto no modal.
    for entry in ["activateSettingsCategory('galton-board')", "openSettingsModal('probability-lab')",
                  "settingsNavigate('galton-board')", "settingsNavigateToLeaf('galton-board')"]:
        page.evaluate("JPWNavigation.navigate('dashboard');openSettingsModal('general')")
        assert page.locator('#settingsOverlay').is_visible()
        page.evaluate(entry)
        page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
        assert page.locator('#settingsOverlay').is_hidden(),entry
        assert page.evaluate("JPWNavigation.current().child")=='research-probability-lab',entry
        assert page.evaluate("document.getElementById('research').contains(document.activeElement)"),entry
        assert page.locator('#settingsModal [data-settings-panel="galton-board"], #settingsMenu [data-settings-category="probability-lab"]').count()==0
    assert page.evaluate("localStorage.getItem('jpwealth_galton_preferences_v1')")==raw
    assert page.evaluate("JSON.stringify(S)")==before
    page.evaluate("JPWNavigation.navigate('dashboard')")
    page.evaluate('applyNavOrder(NAV_ORDER_DEFAULT)')
    print('A13_RESEARCH_RELOCATION '+json.dumps(rows,ensure_ascii=False),flush=True)


def run():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            try:
                # Contratos de domínio/estado são provados uma vez no viewport
                # principal; layout e interação são repetidos nos dois tamanhos
                # e nos dois temas exigidos.
                context, page, observed = boot(browser, url, {"width": 1440, "height": 900})
                try:
                    assert_calendar_refresh_guidance(page)
                    assert_registry_and_dom(page)
                    assert_routes_aliases_and_empty_states(page)
                    assert_atomic_and_storage(page)
                    assert_lab_relocation(page)
                    assert_shell_and_accessibility(page, {"width": 1440, "height": 900}, "light")
                    assert not observed["pageerror"], observed
                    assert not observed["console"], observed
                    assert not observed["requestfailed"], observed
                finally:
                    context.close()

                for viewport, theme in [({"width": 1440, "height": 900}, "dark"),
                                        ({"width": 390, "height": 844}, "light"),
                                        ({"width": 390, "height": 844}, "dark")]:
                    context, page, observed = boot(browser, url, viewport)
                    try:
                        assert_shell_and_accessibility(page, viewport, theme)
                        assert not observed["pageerror"], observed
                        assert not observed["console"], observed
                        assert not observed["requestfailed"], observed
                    finally:
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    run()
    print("PASS research_navigation_test — R3-A..R3-I + browser desktop/mobile light/dark")
