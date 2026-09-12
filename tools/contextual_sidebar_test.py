#!/usr/bin/env python3
"""Contextual sidebar: synthetic preferences, interaction and baseline parity.

CHG-CONTEXTUAL-SIDEBAR-20260909. No real profile, external request, migration,
reset or build is used. Existing v6 coverage remains in the separate relocation
test; this suite checks that the new shell never touches its opaque envelope.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from playwright.sync_api import sync_playwright
from dashboard_macro_test import launch_browser
from dashboard_forex_relocation_test import PREF, KEY as LAYOUT_KEY, serve


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "tools/.artifacts/contextual-sidebar"
UNKNOWN_KEY = "synthetic.sidebar.unknown"
UNKNOWN_RAW = '{ "keep" : [1, "opaque", false], "empty": null }\n'
LAYOUT_RAW = json.dumps(PREF, ensure_ascii=False, indent=1)
ROUTES = ["dashboard", "forex-overview", "forex-preparation", "forex-account",
          "forex-operation", "forex-reconciliation", "forex-planning",
          "personal-finance", "research-forex", "research-stocks-br",
          "research-stocks-global", "research-reits", "research-probability-lab", "research-others", "alladin"]


def settle(page):
    page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


def boot(browser, url, preferences=None, width=1440, read_failure=False):
    seed = {LAYOUT_KEY: LAYOUT_RAW, UNKNOWN_KEY: UNKNOWN_RAW}
    seed.update(preferences or {})
    context = browser.new_context(viewport={"width": width, "height": 1000},
                                  service_workers="block")
    context.add_init_script("""(() => {
      const seed = """ + json.dumps(seed, ensure_ascii=False) + """;
      // Seed once in an isolated origin. Reload must see actual prior writes,
      // rather than silently reseeding the original preference under test.
      if(!sessionStorage.getItem('__sidebarSyntheticSeeded')) {
        for(const [key,value] of Object.entries(seed)) localStorage.setItem(key,value);
        sessionStorage.setItem('__sidebarSyntheticSeeded','1');
      }
      window.__onbShown=true;
      window.__sidebarStorageOps=[];
      window.__sidebarReadFailure=""" + json.dumps(read_failure) + """;
      window.__sidebarWriteFailure=false;
      const get=Storage.prototype.getItem, set=Storage.prototype.setItem;
      const remove=Storage.prototype.removeItem;
      window.__sidebarRawStorage=() => Object.keys(localStorage).sort()
        .map(key=>[key,get.call(localStorage,key)]);
      Storage.prototype.getItem=function(key) {
        if(this===localStorage && window.__sidebarReadFailure
          && ['jpw_nav','jpw_rail'].includes(String(key)))
          throw new DOMException('Synthetic preference read unavailable','SecurityError');
        return get.call(this,key);
      };
      Storage.prototype.setItem=function(key,value) {
        if(this===localStorage) {
          window.__sidebarStorageOps.push(['set',String(key),String(value)]);
          if(window.__sidebarWriteFailure && ['jpw_nav','jpw_rail'].includes(String(key)))
            throw new DOMException('Synthetic preference quota','QuotaExceededError');
        }
        return set.call(this,key,value);
      };
      Storage.prototype.removeItem=function(key) {
        if(this===localStorage) window.__sidebarStorageOps.push(['remove',String(key)]);
        return remove.call(this,key);
      };
      // Record registrations on stable shell targets. Repeated module entry
      // must not accumulate another binding on these same nodes.
      window.__sidebarBindings=[];
      const add=EventTarget.prototype.addEventListener;
      EventTarget.prototype.addEventListener=function(type,listener,options) {
        window.__sidebarBindings.push({target:this,type:String(type)});
        return add.call(this,type,listener,options);
      };
    })();""")
    page = context.new_page()
    observed = {"pageerror": [], "console": [], "requestfailed": []}
    page.on("pageerror", lambda e: observed["pageerror"].append(str(e)))
    page.on("console", lambda m: observed["console"].append(m.text) if m.type == "error" else None)
    page.on("requestfailed", lambda r: observed["requestfailed"].append(r.url))
    origin = url.rsplit("/", 1)[0]
    page.route("**/*", lambda route: route.continue_()
               if route.request.url.startswith(origin + "/")
               else route.fulfill(status=200, content_type="application/json", body="{}"))
    page.goto(url, wait_until="load")
    page.wait_for_function("window.JPWNavigation && window.JPWExec?.ui && window.JPWFin?.ui && window.JPWResearch?.ui && window.JPWAlladinUI && typeof compute==='function'")
    settle(page)
    page.evaluate("() => {window.alert=()=>{}; closeModal();}")
    return context, page, observed


def assert_clean(observed):
    assert not any(observed.values()), observed


def raw_storage(page):
    return dict(page.evaluate("window.__sidebarRawStorage()"))


def preference_ops(page):
    keys = ["jpw_nav", "jpw_rail", LAYOUT_KEY, UNKNOWN_KEY]
    return page.evaluate("keys=>window.__sidebarStorageOps.filter(op=>keys.includes(op[1]))", keys)


def go(page, route):
    assert page.evaluate("route=>JPWNavigation.navigate(route)", route) is True, route
    settle(page)


def assert_opaque(page):
    raw = raw_storage(page)
    assert raw.get(LAYOUT_KEY) == LAYOUT_RAW, "shell changed the v6 envelope"
    assert raw.get(UNKNOWN_KEY) == UNKNOWN_RAW, "shell changed an unrelated browser key"


def expected_preferences(page, style, rail):
    expected_style = style if style in {"classic", "pill", "kinetic"} else "classic"
    expected_rail = "collapsed" if rail == "collapsed" else "expanded"
    assert page.get_attribute("html", "data-nav-style") == expected_style
    assert page.get_attribute("html", "data-rail") == expected_rail
    raw = raw_storage(page)
    assert raw.get("jpw_nav") == style
    assert raw.get("jpw_rail") == rail
    assert preference_ops(page) == [], preference_ops(page)
    assert_opaque(page)


def assert_style_presentation(page, style):
    # Initial load has an existing 300 ms pill measurement. Observe stable
    # behavior after it rather than racing that documented initial measurement.
    page.wait_for_timeout(400)
    actual = page.get_attribute("html", "data-nav-style")
    indicator = page.locator("#navPillIndicator")
    if actual == "classic":
        assert indicator.evaluate("el=>getComputedStyle(el).display") == "none"
        assert page.locator("#nav > .tab.active").evaluate("el=>parseFloat(getComputedStyle(el).borderLeftWidth)>0")
        return
    assert indicator.is_visible(), (style, "missing selected-page indicator")
    initial = indicator.evaluate("el=>el.style.transform")
    page.locator("#finpesNavTrigger").hover()
    settle(page)
    hovered = indicator.evaluate("el=>el.style.transform")
    assert (hovered != initial) == (actual == "kinetic"), (actual, initial, hovered)
    page.locator("#shellLocation").hover()
    settle(page)
    assert indicator.evaluate("el=>el.style.transform") == initial


def run_preferences(browser, url, evidence):
    cases = [(style, rail) for style in ["classic", "pill", "kinetic"]
             for rail in ["expanded", "collapsed"]]
    cases += [(None, None), ("  not-a-style ", "COLLAPSED"), ("", "")]
    outputs = []
    for style, rail in cases:
        pref = {k: v for k, v in [("jpw_nav", style), ("jpw_rail", rail)] if v is not None}
        context, page, observed = boot(browser, url, pref)
        try:
            expected_preferences(page, style, rail)
            assert_style_presentation(page, style)
            before = raw_storage(page)
            state = page.evaluate("JSON.stringify(S)")
            for _ in range(2):
                for route in ROUTES:
                    go(page, route)
            assert raw_storage(page) == before
            assert page.evaluate("JSON.stringify(S)") == state
            expected_preferences(page, style, rail)
            page.reload(wait_until="load")
            page.wait_for_function("window.JPWNavigation && window.JPWAlladinUI")
            settle(page)
            expected_preferences(page, style, rail)
            assert raw_storage(page) == before
            assert_clean(observed)
            outputs.append({"style": style, "rail": rail, "result": "PASS"})
        finally:
            context.close()
    evidence["preference_matrix"] = outputs


def open_style_controls(page):
    page.evaluate("() => openSettingsModal('editor')")
    page.locator("#navStyleSeg").wait_for(state="visible")
    settle(page)


def run_controls(browser, url, evidence):
    context, page, observed = boot(browser, url, {"jpw_nav": "classic", "jpw_rail": "expanded"})
    try:
        state = page.evaluate("JSON.stringify(S)")
        for style in ["pill", "kinetic", "classic"]:
            page.evaluate("window.__sidebarStorageOps=[]")
            open_style_controls(page)
            page.locator(f'#navStyleSeg [data-nav-val="{style}"]').click()
            assert preference_ops(page) == [["set", "jpw_nav", style]]
            assert raw_storage(page)["jpw_nav"] == style
            assert page.get_attribute("html", "data-nav-style") == style
            assert page.locator(f'#navStyleSeg [data-nav-val="{style}"]').evaluate("el=>el.classList.contains('on')")
            page.locator("#settingsCloseBtn").click()
            page.reload(wait_until="load")
            page.wait_for_function("window.JPWNavigation && window.JPWAlladinUI")
            settle(page)
            expected_preferences(page, style, "expanded")
        for rail in ["collapsed", "expanded"]:
            page.evaluate("window.__sidebarStorageOps=[]")
            page.locator("#railToggle").click()
            assert preference_ops(page) == [["set", "jpw_rail", rail]]
            assert raw_storage(page)["jpw_rail"] == rail
            page.reload(wait_until="load")
            page.wait_for_function("window.JPWNavigation && window.JPWAlladinUI")
            settle(page)
            expected_preferences(page, "classic", rail)
        assert page.evaluate("JSON.stringify(S)") == state
        assert_clean(observed)
        evidence["explicit_controls"] = "PASS: three styles and two rail transitions, one write per click, reload preserved"
    finally:
        context.close()


def run_failures(browser, url, evidence):
    pref = {"jpw_nav": "pill", "jpw_rail": "collapsed"}
    context, page, observed = boot(browser, url, pref, read_failure=True)
    try:
        before = raw_storage(page)
        assert preference_ops(page) == []
        for route in ["forex-overview", "personal-finance", "research-forex", "alladin", "dashboard"]:
            go(page, route)
        page.reload(wait_until="load")
        page.wait_for_function("window.JPWNavigation && window.JPWAlladinUI")
        settle(page)
        assert raw_storage(page) == before
        assert preference_ops(page) == []
        assert_opaque(page)
        assert_clean(observed)
        evidence["unavailable_read"] = "PASS: both presentation keys unavailable; app navigable, stored bytes retained"
    finally:
        context.close()
    context, page, observed = boot(browser, url, {"jpw_nav": "classic", "jpw_rail": "expanded"})
    try:
        before = raw_storage(page)
        state = page.evaluate("JSON.stringify(S)")
        page.evaluate("window.__sidebarWriteFailure=true; window.__sidebarStorageOps=[]")
        page.locator("#railToggle").click()
        assert preference_ops(page) == [["set", "jpw_rail", "collapsed"]]
        assert "Não foi possível salvar" in page.locator("#shellAnnouncement").inner_text()
        assert page.locator("#shellAnnouncement").get_attribute("aria-live") in {"polite", "assertive"}
        open_style_controls(page)
        page.locator('#navStyleSeg [data-nav-val="pill"]').click()
        assert preference_ops(page) == [["set", "jpw_rail", "collapsed"], ["set", "jpw_nav", "pill"]]
        notice = page.locator("#navStyleStatus")
        assert "Não foi possível salvar o estilo" in notice.inner_text()
        assert notice.is_visible() and notice.get_attribute("aria-live") == "polite"
        assert notice.evaluate("el=>!el.closest('[inert],[hidden],[aria-hidden=\"true\"]')"), "preference failure hidden behind modal isolation"
        assert raw_storage(page) == before
        page.locator("#settingsCloseBtn").click()
        go(page, "forex-overview")
        assert page.evaluate("JSON.stringify(S)") == state
        page.reload(wait_until="load")
        page.wait_for_function("window.JPWNavigation && window.JPWAlladinUI")
        settle(page)
        expected_preferences(page, "classic", "expanded")
        assert_clean(observed)
        evidence["unavailable_write"] = "PASS: rejected explicit writes preserve previous preferences and financial state"
    finally:
        context.close()


def operational_cases(page):
    return page.evaluate("""() => {
      const initial=JSON.stringify(S), results=[];
      for(const name of ['pending','populated','drawdown','quarantine']) {
        S=JSON.parse(initial);
        if(name!=='pending') {S.onboarding.done=true; S.params.saldoIni=10000;}
        if(name==='drawdown') S.cycleRealizado=-1500;
        if(name==='quarantine') S.quarantine={ativa:true,inicio:'2026-09-01',fim:'2099-09-30'};
        render();
        const ids=['mcClearanceTitle','mcClearanceSub','mcFactFase','mcFactDD',
          'mcFactRisco','mcFactAlav','gdVrmValue','gdVrmRegime','mcClearanceReasons'];
        results.push({name,compute:compute(),clearance:getOperationalClearance(),
          text:Object.fromEntries(ids.map(id=>[id,document.getElementById(id)?.textContent]))});
      }
      S=JSON.parse(initial); render();
      return results;
    }""")


def binding_snapshot(page):
    return page.evaluate("""() => {
      const stable=[window,document,nav,appSidebar,railToggle,
        ...document.querySelectorAll('#nav > .tab,[data-nav-expand]')];
      return window.__sidebarBindings.filter(record=>stable.includes(record.target))
        .map(record=>[record.target===window?'window':record.target===document?'document':
          record.target.id||record.target.dataset.navExpand,record.type]);
    }""")


def run_lifecycle(browser, url, evidence, baseline_url):
    context, page, observed = boot(browser, url)
    try:
        output = operational_cases(page)
        assert [entry["clearance"]["status"] for entry in output] == ["pending", "clear", "blocked", "blocked"]
        if baseline_url:
            bc, bp, be = boot(browser, baseline_url)
            try:
                assert output == operational_cases(bp), "compute/clearance/rendered operational values differ from immutable baseline"
                assert_clean(be)
            finally:
                bc.close()
            evidence["operational_baseline_parity"] = "PASS"
        else:
            evidence["operational_baseline_parity"] = "NOT_RUN: --baseline-root was not provided"
        evidence["operational_values"] = output
        go(page, "forex-operation")
        # These inputs are existing immediate-edit controls. Exercise the actual
        # input handler before taking the state snapshot; navigation must not
        # issue an additional write or replace those nodes.
        page.locator("#iAtr55").evaluate("el=>{const details=el.closest('details');if(details)details.open=true}")
        page.locator("#iAtr55").fill("0.00777")
        assert page.evaluate("S.atr55") == 0.00777
        page.evaluate("""() => {
          window.__sidebarNodeSentinels=['execClearanceCard','phaseContainer','iAtr55','motorWidgetGrid','fxOverviewWidgets']
            .map(id=>document.getElementById(id));
          window.__sidebarStorageOps=[];
        }""")
        initial_state = page.evaluate("JSON.stringify(S)")
        initial_raw = raw_storage(page)
        bindings = binding_snapshot(page)
        for _ in range(4):
            for route in ["motor", "pivots", "personal-finance", "alladin", "dashboard", "forex-operation"]:
                go(page, route)
        assert binding_snapshot(page) == bindings, "repeated entry accumulated stable shell listeners"
        assert page.evaluate("JSON.stringify(S)") == initial_state
        assert raw_storage(page) == initial_raw
        assert page.evaluate("window.__sidebarStorageOps") == []
        assert page.evaluate("window.__sidebarNodeSentinels.every(el=>el.isConnected && document.getElementById(el.id)===el)")
        assert page.locator("#iAtr55").input_value() == "0.00777"
        assert page.locator("#iAtr55").evaluate("el=>el.closest('details').open")
        assert page.evaluate("""() => {const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
          return ids.filter((id,index)=>ids.indexOf(id)!==index)}""") == []
        assert page.locator("#gdDashMain > [data-layout-card]").count() == 2
        assert page.locator("#fxOverviewWidgets > [data-layout-card]").count() == 4
        expected_contexts = {"forex-operation": "forex-operation", "motor": "forex-operation",
                             "forex-reconciliation": "forex-reconciliation", "forex-planning": "forex-planning",
                             "pivots": "research-forex"}
        for route, words in [("dashboard", ["Dashboard"]), ("forex-overview", ["Forex", "Visão Geral"]),
                             ("forex-operation", ["Forex", "Operação", "Painel"]),
                             ("forex-reconciliation", ["Forex", "Apuração"]), ("forex-planning", ["Forex", "Planejamento"]),
                             ("motor", ["Forex", "Operação", "Motor"]), ("research-stocks-br", ["Research", "Ações"]),
                             ("pivots", ["Research", "Forex", "Pivots"]), ("personal-finance", ["Finanças Pessoais", "Visão Geral"])]:
            go(page, route)
            location = page.locator("#shellLocation").inner_text()
            assert all(word in location for word in words), (route, words, location)
            visible_contexts = page.locator('#navLocalSlot [data-nav-context]').evaluate_all("""els=>els
              .filter(el=>el.getBoundingClientRect().width>0 && el.getBoundingClientRect().height>0)
              .map(el=>el.dataset.navContext)""")
            assert visible_contexts == ([expected_contexts[route]] if route in expected_contexts else []), (route, visible_contexts)
        go(page, "alladin")
        for view, label in [("instruments", "Instrumentos"), ("assets", "Bens"), ("accounts", "Contas"),
                            ("cashAccounts", "Caixa"), ("ledger", "Lançamentos"), ("balances", "Saldos"), ("positions", "Posições")]:
            page.locator(f'#alladinTabs [data-alladin-view="{view}"]').click()
            settle(page)
            location = page.locator("#shellLocation").inner_text()
            assert "Alladin" in location and label in location, (view, location)
        before = {"state": page.evaluate("JSON.stringify(S)"), "storage": raw_storage(page),
                  "route": page.evaluate("JPWNavigation.current()"), "location": page.locator("#shellLocation").inner_text()}
        assert page.evaluate("JPWNavigation.navigate('synthetic-invalid-route')") is False
        after = {"state": page.evaluate("JSON.stringify(S)"), "storage": raw_storage(page),
                 "route": page.evaluate("JPWNavigation.current()"), "location": page.locator("#shellLocation").inner_text()}
        assert after == before, "invalid destination changed the current context"
        assert_clean(observed)
        evidence["lifecycle"] = "PASS: stable nodes/bindings, ATR edit retained, invalid route atomic, contexts including Alladin"
    finally:
        context.close()


def drawer_open(page):
    page.locator("[data-shell-menu-toggle]").click()
    page.wait_for_function("document.documentElement.getAttribute('data-shell-menu')==='open'")
    settle(page)
    assert page.evaluate("appSidebar.contains(document.activeElement)")
    assert page.locator("#appSidebar").get_attribute("role") == "dialog"
    assert page.locator("#appSidebar").get_attribute("aria-modal") == "true"


def assert_drawer_closed(page, restore=False):
    page.wait_for_function("document.documentElement.getAttribute('data-shell-menu')!=='open'")
    settle(page)
    assert not page.locator("#appMain").evaluate("el=>el.inert")
    if restore:
        assert page.evaluate("document.activeElement.matches('[data-shell-menu-toggle]')")


def run_drawer(browser, url, evidence):
    context, page, observed = boot(browser, url, {"jpw_nav": "kinetic", "jpw_rail": "collapsed"}, width=390)
    try:
        before = raw_storage(page)
        drawer_open(page)
        assert page.locator("#appMain").evaluate("el=>el.inert")
        for key in ["Tab"] * 18 + ["Shift+Tab"] * 18:
            page.keyboard.press(key)
            assert page.evaluate("appSidebar.contains(document.activeElement)"), "focus escaped open mobile drawer"
        page.keyboard.press("Escape")
        assert_drawer_closed(page, restore=True)
        drawer_open(page)
        page.locator("#sidebarClose").click()
        assert_drawer_closed(page, restore=True)
        drawer_open(page)
        page.locator("#sidebarBackdrop").click(position={"x": 385, "y": 200})
        assert_drawer_closed(page, restore=True)
        drawer_open(page)
        page.locator("#execNavTrigger").click()
        assert_drawer_closed(page)
        assert "Forex" in page.locator("#shellLocation").inner_text()
        assert page.evaluate("!appSidebar.contains(document.activeElement) && document.activeElement!==document.body"), "selection did not focus content"
        assert page.evaluate("""() => {const r=document.activeElement.getBoundingClientRect();
          return r.top>=0&&r.bottom<=innerHeight}"""), "selection focused an offscreen content target"
        drawer_open(page)
        page.locator('#execNavSubmenu [data-nav-child="forex-operation"]').click()
        assert_drawer_closed(page)
        assert page.evaluate("JPWExec.ui.getView()") == "panel"
        assert page.evaluate("exec.contains(document.activeElement) && !document.activeElement.closest('[inert],[hidden]')"), "child selection did not focus visible content"
        drawer_open(page)
        page.set_viewport_size({"width": 1440, "height": 1000})
        assert_drawer_closed(page)
        assert page.get_attribute("html", "data-rail") == "collapsed"
        assert page.evaluate("!document.activeElement.closest('[inert],[hidden]')")
        page.set_viewport_size({"width": 390, "height": 844})
        settle(page)
        assert page.get_attribute("html", "data-shell-menu") != "open"
        assert raw_storage(page) == before
        assert preference_ops(page) == []
        assert_clean(observed)
        evidence["drawer"] = "PASS: Tab trap, Escape, close, backdrop, primary/child selection, resize and no preference writes"
    finally:
        context.close()


def run_visual(browser, url, evidence, capture, artifacts):
    context, page, observed = boot(browser, url, {"jpw_nav": "classic", "jpw_rail": "expanded"})
    screenshots = []
    try:
        browser_build = page.evaluate("JP_WEALTH_BUILD_ID")
        assert browser_build in (ROOT / "build-id.js").read_text()
        evidence["browser_build"] = browser_build
        for width in [1440, 1024, 390, 320]:
            page.set_viewport_size({"width": width, "height": 1000 if width > 900 else 844})
            for theme in ["dark", "light"]:
                page.evaluate("t=>document.documentElement.dataset.theme=t", theme)
                for route, label in [("dashboard", "dashboard"), ("forex-overview", "forex")]:
                    go(page, route)
                    assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), (width, theme, route, "overflow")
                    assert page.locator("#shellLocation").is_visible()
                    if width > 900:
                        assert page.locator("#appSidebar").is_visible()
                        assert page.evaluate("appSidebar.getBoundingClientRect().right<=appMain.getBoundingClientRect().left+1")
                    else:
                        drawer_open(page)
                        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
                        assert page.locator('#nav > .tab .lbl').evaluate_all("els=>els.every(el=>getComputedStyle(el).display!=='none' && el.getBoundingClientRect().width>0)")
                        targets = page.locator('#nav > .tab, #sidebarClose, [data-nav-expand]:not([hidden])').evaluate_all("els=>els.filter(e=>e.getBoundingClientRect().width>0).map(e=>({id:e.id,w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))")
                        assert targets and all(t["w"] >= 44 and t["h"] >= 44 for t in targets), targets
                        if capture and width == 390 and route == "forex-overview":
                            name = f"drawer-{width}-{theme}.png"
                            page.screenshot(path=str(artifacts / name), full_page=True)
                            screenshots.append(name)
                        page.keyboard.press("Escape")
                        assert_drawer_closed(page, restore=True)
                    if capture and width in [1440, 390]:
                        name = f"{label}-{width}-{theme}.png"
                        page.screenshot(path=str(artifacts / name), full_page=True)
                        screenshots.append(name)
        # Native app large-text preference exercises text enlargement without
        # storing it. Reflow at 320 CSS pixels covers the 1280-at-400% geometry;
        # this is not a claim of a complete browser zoom or WCAG audit.
        page.evaluate("document.documentElement.style.setProperty('--fs-scale','1.25')")
        go(page, "research-stocks-br")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.locator('#finpesNavTrigger .lbl').evaluate("el=>el.textContent='Finanças Pessoais — identificação sintética prolongada para testar quebra de linha'")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
        page.emulate_media(reduced_motion="reduce")
        page.evaluate("document.documentElement.setAttribute('data-nav-style','kinetic')")
        durations = page.locator('#navPillIndicator, #navPillSpecular').evaluate_all("els=>els.map(e=>getComputedStyle(e).transitionDuration)")
        assert all(all(float(v.strip().removesuffix('s')) <= .01 for v in d.split(',')) for d in durations), durations
        assert_clean(observed)
        evidence["visual_matrix"] = "PASS: 1440/1024/390/320 CSS px, light/dark, containment, mobile targets, text enlargement and reduced motion"
        evidence["screenshots"] = screenshots
        evidence["zoom_limit"] = "320 CSS px reflow and 125% app text tested; real browser zoom and screen-reader session not claimed"
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--artifacts", type=Path, default=ARTIFACTS)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--only", choices=["preferences", "controls", "failures", "lifecycle", "drawer", "visual"])
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    source_paths = ["index.html", "src/styles/app.css", "src/js/20-ui/02-sidebar.js",
                    "src/js/20-ui/12-nav-style.js", "src/js/40-app/01-navigation.js",
                    "src/js/40-app/11-operational-shell.js", "src/js/40-app/12-global-dashboard.js",
                    "src/js/manifest.json", "build-id.js", "tools/contextual_sidebar_test.py"]
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in source_paths}
    evidence = {"result": "RUNNING", "started_at_epoch": time.time(), "source_sha256": hashes,
                "build_file": (ROOT / "build-id.js").read_text().strip(),
                "baseline_root": str(args.baseline_root) if args.baseline_root else None,
                "only": args.only}
    server, url = serve(ROOT)
    baseline_server, baseline_url = serve(args.baseline_root) if args.baseline_root else (None, None)
    report = args.artifacts / (f"focal-{args.only}.json" if args.only else "focal-results.json")
    try:
        with sync_playwright() as pw:
            browser = launch_browser(pw)
            evidence["browser"] = browser.version
            try:
                runs = {
                    "preferences": lambda: run_preferences(browser, url, evidence),
                    "controls": lambda: run_controls(browser, url, evidence),
                    "failures": lambda: run_failures(browser, url, evidence),
                    "lifecycle": lambda: run_lifecycle(browser, url, evidence, baseline_url),
                    "drawer": lambda: run_drawer(browser, url, evidence),
                    "visual": lambda: run_visual(browser, url, evidence, args.capture, args.artifacts),
                }
                for name, run in runs.items():
                    if args.only and name != args.only:
                        continue
                    evidence["current_group"] = name
                    run()
                    print(f"PASS contextual sidebar: {name}", flush=True)
                assert hashes == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in source_paths}, "candidate changed while the test was running"
                evidence["result"] = "PASS"
                print("PASS contextual_sidebar_test — preferences, location, lifecycle, drawer and visual assertions for declared groups", flush=True)
            finally:
                browser.close()
    except Exception as error:
        evidence["result"] = "FAIL — classification requires triage"
        evidence["error"] = repr(error)
        raise
    finally:
        evidence["elapsed_seconds"] = round(time.time() - evidence["started_at_epoch"], 3)
        report.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")
        server.shutdown()
        if baseline_server:
            baseline_server.shutdown()


if __name__ == "__main__":
    main()
