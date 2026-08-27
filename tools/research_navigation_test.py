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
    context = browser.new_context(viewport=viewport)
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
      '#researchNavSubmenu [data-nav-context="research-forex"] [data-nav-local-view]')]
      .map(el => el.dataset.navLocalView)""")
    assert n3 == RESEARCH_FOREX_VIEWS
    assert page.locator('#researchNavSubmenu [data-nav-context]:not([data-nav-context="research-forex"])').count() == 0

    assert page.locator("#nav > #researchNavTrigger").count() == 1
    assert page.locator("#nav #researchNavSubmenu").count() == 0
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
    assert page.locator("#research #galtonBoardRoot, #research [data-settings-child='galton-board']").count() == 0


def assert_atomic_and_storage(page):
    assert page.evaluate("() => JPWNavigation.navigateLocal('research', 'nocoda')") is True
    page.click("#researchNavTrigger")
    page.locator('#researchNavSubmenu [data-nav-local-view="nocoda"]').focus()
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
    page.wait_for_function("() => researchNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.wait_for_function("() => JPWResearch.ui.getView() === 'calendar'")
    assert page.locator('#researchNavSubmenu [data-nav-child="research-forex"]').get_attribute("aria-current") == "page"
    assert page.locator('#researchNavSubmenu [data-nav-local-view="calendar"]').get_attribute("aria-current") == "page"

    page.click('#researchNavSubmenu [data-nav-child="research-stocks-br"]')
    assert page.evaluate("() => JPWResearch.ui.getView()") == "stocks-br"
    context = page.locator('#researchNavSubmenu [data-nav-context="research-forex"]')
    assert context.is_hidden()
    assert context.evaluate("el => el.inert") is True

    page.click('#researchNavSubmenu [data-nav-child="research-forex"]')
    assert page.evaluate("() => JPWResearch.ui.getView()") == "calendar"
    assert not context.is_hidden()
    assert context.evaluate("el => el.inert") is False
    page.click('#researchNavSubmenu [data-nav-local-view="pivots"]')
    assert page.evaluate("() => JPWResearch.ui.getView()") == "pivots"

    if mobile:
        page.click("[data-shell-menu-toggle]")
    page.focus("#researchNavTrigger")
    page.keyboard.press("ArrowDown")
    assert page.evaluate("() => document.activeElement.dataset.navChild") == "research-forex"
    page.keyboard.press("End")
    assert page.evaluate("() => document.activeElement.dataset.navLocalView") == "pivots"
    page.keyboard.press("Home")
    assert page.evaluate("() => document.activeElement.dataset.navChild") == "research-forex"
    page.keyboard.press("Escape")
    focus = page.evaluate("""() => ({
      id:document.activeElement.id,
      insideHiddenSubmenu:!!document.activeElement.closest?.('#researchNavSubmenu')
    })""")
    if mobile:
        assert not focus["insideHiddenSubmenu"], ("mobile focus trapped", focus)
    else:
        assert focus["id"] == "researchNavTrigger", ("focus return", focus)
    assert page.get_attribute("#researchNavTrigger", "aria-expanded") == "false"

    layout = page.evaluate("""mobile => ({
      activeScreens:[...document.querySelectorAll('#appMain > .screen.active')].map(el=>el.id),
      overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
      visibleResearch:[...document.querySelectorAll('#research > [data-research-view]')]
        .filter(el=>!el.hidden).map(el=>el.id),
      targets:[...document.querySelectorAll(mobile
        ? '#nav > .tab, #researchNavSubmenu button'
        : '#researchNavSubmenu button')]
        .filter(el=>{const r=el.getBoundingClientRect();return r.width>0&&r.height>0})
        .map(el=>({label:el.textContent.trim(),width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}))
    })""", mobile)
    assert layout["activeScreens"] == ["research"], layout
    assert layout["visibleResearch"] == ["execPivots"], layout
    assert layout["overflow"] <= 1, (viewport, theme, layout)
    assert layout["targets"] and all(item["width"] >= 44 and item["height"] >= 44 for item in layout["targets"]), layout


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
                    assert_registry_and_dom(page)
                    assert_routes_aliases_and_empty_states(page)
                    assert_atomic_and_storage(page)
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
