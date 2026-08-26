#!/usr/bin/env python3
"""NAV-01 — contrato da fundacao semantica de navegacao.

Prova que a API publica expoe somente as cinco rotas canonicas, enquanto a
fachada legada continua resolvendo destinos fisicos sem promovê-los ao contrato
canônico. Navegação é UI pura: não grava storage, não salva estado financeiro e
o placeholder Alladin não lê nem altera o domínio patrimonial.
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
    ("research-forex", "research", "research", None),
    ("alladin", "alladin", "alladin", None),
]
LEGACY = ["dash", "exec", "contas", "contab", "fxplan", "finpes",
          "motor", "check", "params", "config"]
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
      && window.JPWExec?.ui && window.JPWFin?.ui && window.JPWFx?.ui""")
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
    assert "forex-account" not in flat, flat
    resolved = page.evaluate("""targets => targets.map(target => ({
      target, result: window.JPWNavigation.resolve(target)
    }))""", [item[0] for item in CANONICAL] + LEGACY)
    assert all(item["result"] and item["result"].get("accepted") for item in resolved), resolved
    assert page.evaluate("() => window.JPWNavigation.resolve('rota-inexistente').accepted") is False


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
    assert page.locator("section#alladin").count() == 1
    alladin_text = page.locator("section#alladin").inner_text().strip().splitlines()
    assert [line.strip() for line in alladin_text if line.strip()] == [
        "Alladin",
        "Módulo patrimonial em desenvolvimento.",
        "As funcionalidades ainda não estão disponíveis.",
    ], alladin_text
    forbidden = page.locator("section#alladin").inner_text()
    assert "R$" not in forbidden and "0,00" not in forbidden
    assert page.locator("section#alladin input, section#alladin form, section#alladin [data-layout-card]").count() == 0


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

    page.evaluate("() => window.JPWExec.ui.selectView('motor')")
    page.click('#nav > .tab[data-route="forex-overview"]')
    assert page.evaluate("() => window.JPWExec.ui.getView()") == "overview"
    page.evaluate("() => window.JPWFin.ui.selectView('cenarios')")
    page.click('#nav > .tab[data-route="personal-finance"]')
    assert page.evaluate("() => window.JPWFin.ui.getView()") == "overview"


def assert_compatibility_and_atomic_refusal(page):
    # N1-B: fachada legada preservada, sem promover a conta a rota canônica.
    page.evaluate("() => navigateToScreen('contas')")
    state = active_state(page)
    assert state["activeScreens"] == ["contas"], state
    assert state["primary"] == "forex", state
    assert "forex-account" not in [route["id"] for route in page.evaluate("() => JPWNavigation.routes()")]

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
      navigateToScreen('contas');
      JPWNavigation.navigateLocal('exec', 'motor');
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
                assert_canonical_navigation(page)
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
    print("NAVIGATION IA TEST PASS — N1-A/N1-B/N1-C, cinco rotas, compatibilidade, storage e Alladin isolados")


if __name__ == "__main__":
    main()
