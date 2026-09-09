#!/usr/bin/env python3
"""Relocation + v6 compatibility, real controls and synthetic isolated storage.

Optional --baseline-root is an immutable git archive of the recorded BASE_SHA.
No real browser profile, external API, preference reset or migration is used.
"""
import argparse
import copy
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright
from dashboard_macro_test import launch_browser

ROOT = Path(__file__).resolve().parents[1]
KEY = "jpwealth.ui.widgetLayouts.v6"
IDS = ["onboarding-alert", "news-high-impact", "quick-actions",
       "operational-clearance", "vrm", "institutional-panel"]
MOVED = {"onboarding-alert", "operational-clearance", "vrm", "news-high-impact"}
PREF = {"version": 6, "extra": {"keep": "synthetic"}, "screens": {
    "dash": {"note": "preserve", "widgets": [
        {"id": name, "zone": "main", "size": "full" if name in
         {"onboarding-alert", "operational-clearance"} else "compact",
         "order": i * 10 + 7, "note": name} for i, name in enumerate(IDS)]},
    "future-surface": {"opaque": [1, 2, 3]}}}


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve(root):
    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                 functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/index.html"


def open_page(browser, url, raw=None):
    context = browser.new_context(viewport={"width": 1440, "height": 1000},
                                  service_workers="block")
    context.add_init_script("""
      window.__onbShown = true;
      window.__layoutWrites = [];
      const originalSet = Storage.prototype.setItem;
      const originalRemove = Storage.prototype.removeItem;
      Storage.prototype.setItem = function(k,v) {
        if (k.includes('widgetLayout')) {
          window.__layoutWrites.push(['set',k]);
          if(window.__failLayoutWrite) throw new DOMException('Synthetic quota','QuotaExceededError');
        }
        return originalSet.call(this,k,v);
      };
      Storage.prototype.removeItem = function(k) {
        if(k.includes('widgetLayout')) window.__layoutWrites.push(['remove',k]);
        return originalRemove.call(this,k);
      };
    """)
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("**/*", lambda route: route.continue_()
               if route.request.url.startswith(url.rsplit("/", 1)[0])
               else route.fulfill(status=200, content_type="application/json", body="{}"))
    page.goto(url)
    page.wait_for_function("typeof dashLayoutBoot === 'function' && window.JPWNavigation && typeof S === 'object'")
    if raw is not None:
        page.evaluate("([k,v]) => localStorage.setItem(k,v)", [KEY, raw])
        page.reload()
    page.wait_for_function("window.JPWNavigation && typeof dashLayoutBoot === 'function'")
    return context, page, errors


def stored(page):
    return page.evaluate("k=>localStorage.getItem(k)", KEY)


def go(page, destination):
    page.evaluate("d=>navigateToScreen(d)", destination)
    page.wait_for_timeout(100)


def controls(page):
    page.evaluate("() => openSettingsModal('interface')")
    page.locator("#dashLayoutCustomizeBtn").click()
    # Existing modal restores its opener on rAF. Wait for focus handoff before
    # sending a keyboard gesture; do not race that transition in automation.
    page.evaluate("() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")


def swap(page, widget, direction="up"):
    button = page.locator(f'[data-layout-card="{widget}"] > .dash-layout-menu-btn')
    button.press("Enter")
    page.locator(f'#jpPopoverActive [data-action="{direction}"]').click()
    assert page.evaluate("id=>document.activeElement.dataset.layoutCard===id", widget)


def values(page):
    # Runtime fixtures only: no financial storage save. Cover pending, populated,
    # drawdown and quarantine with exactly the same inputs in both builds.
    return page.evaluate("""() => {
      const initial = JSON.stringify(S);
      const output = [];
      for (const state of ['pending', 'populated', 'drawdown', 'quarantine']) {
        S = JSON.parse(initial);
        if(state !== 'pending') { S.onboarding.done=true; S.params.saldoIni=10000; }
        if(state === 'drawdown') S.cycleRealizado=-1500;
        if(state === 'quarantine') S.quarantine={ativa:true,inicio:'2026-09-01',fim:'2099-09-30'};
        render();
        const ids=['mcClearanceTitle','mcClearanceSub','mcFactFase','mcFactDD',
          'mcFactRisco','mcFactAlav','gdVrmValue','gdVrmRegime','mcClearanceReasons'];
        output.push({state, clearance:getOperationalClearance(),
          text:Object.fromEntries(ids.map(id=>[id,document.getElementById(id)?.textContent]))});
      }
      S=JSON.parse(initial); render();
      return output;
    }""")


def run(browser, url, artifacts, baseline=None):
    raw = json.dumps(PREF, ensure_ascii=False)
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "synthetic-layout-v6.json").write_text(raw)
    ctx, page, errors = open_page(browser, url, raw)
    output = values(page)
    assert [v["clearance"]["status"] for v in output] == ["pending", "clear", "blocked", "blocked"]
    assert output[0]["text"]["mcFactDD"] != output[2]["text"]["mcFactDD"]
    if baseline:
        bc, bp, be = open_page(browser, baseline, raw)
        assert bp.evaluate("!!dashLayoutValidateScreenWidgets('dash', JSON.parse(localStorage.getItem(JP_WIDGET_STORAGE_KEY_V6)).screens.dash.widgets)")
        assert output == values(bp), "Operational baseline/candidate values differ"
        assert not be, be
        bc.close()
    (artifacts / "operational-values.json").write_text(json.dumps(output, indent=2, ensure_ascii=False))
    assert page.evaluate("!!dashLayoutValidateScreenWidgets('dash', JSON.parse(localStorage.getItem(JP_WIDGET_STORAGE_KEY_V6)).screens.dash.widgets)")
    assert page.locator("#gdDashMain > [data-layout-card]").evaluate_all("(els)=>els.map(e=>e.dataset.layoutCard)") == ["quick-actions", "institutional-panel"]
    assert page.locator("#fxOverviewWidgets > [data-layout-card]").evaluate_all("(els)=>els.map(e=>e.dataset.layoutCard)") == [i for i in IDS if i in MOVED]
    page.evaluate("window.__cards = [...document.querySelectorAll('#fxOverviewWidgets > [data-layout-card]')]")
    for _ in range(4):
        go(page, "forex-overview")
        assert page.locator("#mcClearanceCard").is_visible()
        go(page, "dash")
        assert page.locator("#dashMacro").is_visible()
    assert page.evaluate("window.__cards.every(e=>e.isConnected && (!e.id || document.querySelectorAll('#'+e.id).length===1))")
    assert stored(page) == raw
    assert page.evaluate("window.__layoutWrites") == []
    page.reload()
    page.wait_for_function("typeof dashLayoutBoot === 'function'")
    assert stored(page) == raw
    assert page.evaluate("window.__layoutWrites") == []
    page.locator("#dmTools").evaluate("(e)=>e.open=true")
    controls(page)
    swap(page, "institutional-panel")
    page.locator("#dashLayoutDoneBtn").click()
    saved = json.loads(stored(page))
    assert saved["extra"] == PREF["extra"]
    assert saved["screens"]["future-surface"] == PREF["screens"]["future-surface"]
    assert saved["screens"]["dash"]["note"] == "preserve"
    for original in PREF["screens"]["dash"]["widgets"]:
        current = next(w for w in saved["screens"]["dash"]["widgets"] if w["id"] == original["id"])
        if original["id"] in MOVED:
            assert current == original, (current, original)
        else:
            assert {k:v for k,v in current.items() if k != "order"} == {k:v for k,v in original.items() if k != "order"}
    assert page.evaluate("window.__layoutWrites") == [["set", KEY]]
    page.reload()
    page.wait_for_function("typeof dashLayoutBoot === 'function'")
    assert page.locator("#gdDashMain > [data-layout-card]").evaluate_all("(els)=>els.map(e=>e.dataset.layoutCard)") == ["institutional-panel", "quick-actions"]
    # No-op session and cancelled real edit cannot rewrite storage.
    before = stored(page)
    page.locator("#dmTools").evaluate("(e)=>e.open=true")
    controls(page)
    page.locator("#dashLayoutDoneBtn").click()
    controls(page)
    swap(page, "quick-actions")
    page.once("dialog", lambda d: d.accept())
    page.locator("#dashLayoutCancelBtn").click()
    assert stored(page) == before
    assert page.evaluate("window.__layoutWrites") == []
    # Forex uses the same existing controls; edits cannot return widgets to dash.
    go(page, "forex-overview")
    controls(page)
    swap(page, "vrm")
    go(page, "dash")
    go(page, "forex-overview")
    page.locator("#dashLayoutDoneBtn").click()
    assert page.locator("#gdDashMain > [data-layout-card]").count() == 2
    assert page.locator("#fxOverviewWidgets > [data-layout-card]").count() == 4
    forex_saved = stored(page)
    page.reload()
    go(page, "forex-overview")
    assert stored(page) == forex_saved
    # Buttons are exercised through actual DOM events, after repeated navigation.
    page.locator('#mcClearanceCard [data-dash-go="forex-operation"]').click()
    assert page.locator("#execWidgetGrid").is_visible()
    go(page, "forex-overview")
    page.locator("#mcClearanceAction").click()
    assert page.locator("#dashMethodology").evaluate("(e)=>e.open")
    page.locator("#onbBannerBtn").click()
    assert page.locator("#modalOverlay").is_visible()
    page.evaluate("()=>closeModal()")
    # Count requests caused by one refresh gesture, without calling live APIs.
    page.evaluate("""() => {window.__refreshes=0; const f=window.fetch;
      window.fetch=function(...args){window.__refreshes++;return f.apply(this,args);};}""")
    page.locator("#gdNewsRefreshBtn").click()
    page.wait_for_function("!document.getElementById('gdNewsRefreshBtn').disabled")
    assert page.evaluate("window.__refreshes") == 1
    page.locator("#gdNewsMoreBtn").click()
    assert page.locator("#ecalNewsMenu").is_visible()
    page.locator("#ecalNewsMenu [role=menuitem]").click()
    assert page.locator("#ecalOverlay").is_visible()
    page.keyboard.press("Escape")
    assert page.locator("#gdNewsMoreBtn").evaluate("(e)=>e===document.activeElement")
    for width in [1440, 390]:
        page.set_viewport_size({"width": width, "height": 1000 if width > 400 else 844})
        for theme in ["dark", "light"]:
            page.evaluate("t=>document.documentElement.dataset.theme=t", theme)
            for destination, name in [("dash", "dashboard"), ("forex-overview", "forex")]:
                go(page, destination)
                page.locator("#dmTools").evaluate("(e)=>e.open=true")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1"), (width,theme,name)
                page.screenshot(path=str(artifacts / f"{name}-{width}-{theme}.png"), full_page=True)
    assert not errors, errors
    ctx.close()
    # Existing restore control is scoped to the visible surface, never both.
    # Synthetic preferences only; this is not a reset used to solve compatibility.
    for target in ["dash", "forex-overview"]:
        for in_session in [True, False]:
            c, p, e = open_page(browser, url, raw)
            go(p, target)
            if in_session:
                controls(p)
                button = "#dashLayoutRestoreBtn"
            else:
                p.evaluate("()=>openSettingsModal('interface')")
                button = "#dashLayoutResetBtn"
            p.once("dialog", lambda d: d.accept())
            p.locator(button).click()
            if in_session:
                p.locator("#dashLayoutDoneBtn").click()
            result = json.loads(stored(p))
            untouched = MOVED if target == "dash" else {"institutional-panel", "quick-actions"}
            for original in PREF["screens"]["dash"]["widgets"]:
                if original["id"] in untouched:
                    assert next(w for w in result["screens"]["dash"]["widgets"] if w["id"] == original["id"]) == original
            p.reload()
            p.wait_for_function("typeof dashLayoutBoot === 'function'")
            if target == "dash":
                assert p.locator("#gdDashMain > [data-layout-card]").evaluate_all("(els)=>els.map(e=>e.dataset.layoutCard)") == ["institutional-panel", "quick-actions"]
            else:
                assert p.locator("#fxOverviewWidgets > [data-layout-card]").evaluate_all("(els)=>els.map(e=>e.dataset.layoutCard)") == ["onboarding-alert", "operational-clearance", "vrm", "news-high-impact"]
            assert not e, e
            c.close()
    # Do not introduce a new save contract for other, unmoved screens.
    # Their pre-existing legacy normalization must not alter the raw dash group.
    for legacy in ["exec-vrm", "exec-lifo-monitor"]:
        c, p, e = open_page(browser, url, raw)
        exec_widgets = p.evaluate("JP_WIDGET_DEFAULTS.exec")
        if legacy == "exec-vrm":
            exec_widgets.append({"id": legacy, "zone": "main", "size": "full", "order": 6})
        else:
            exec_widgets = [w for w in exec_widgets if w["id"] not in {"exec-consolidado", "exec-monitor"}]
            exec_widgets.append({"id": legacy, "zone": "main", "size": "full", "order": 1})
        legacy_pref = copy.deepcopy(PREF)
        legacy_pref["screens"]["exec"] = {"widgets": exec_widgets}
        p.evaluate("([k,v])=>localStorage.setItem(k,v)", [KEY,json.dumps(legacy_pref)])
        p.reload()
        go(p,"forex-operation")
        controls(p)
        p.locator('[data-layout-card="exec-consolidado"] > .dash-layout-menu-btn').press("Enter")
        p.locator('#jpPopoverActive [data-size="full"]').click()
        p.locator("#dashLayoutDoneBtn").click()
        assert not p.locator("#dashLayoutBar").is_visible()
        assert json.loads(stored(p))["screens"]["dash"] == PREF["screens"]["dash"]
        assert not e, e
        c.close()
    # Existing validator allows ties: preserve their stable order across save/reload.
    for orders in [[0]*6, [0, 1, 1, 1, 2, 2]]:
        tied = copy.deepcopy(PREF)
        for w, order in zip(tied["screens"]["dash"]["widgets"], orders):
            w["order"] = order
        c, p, e = open_page(browser, url, json.dumps(tied))
        assert p.evaluate("!!dashLayoutValidateScreenWidgets('dash', JSON.parse(localStorage.getItem(JP_WIDGET_STORAGE_KEY_V6)).screens.dash.widgets)")
        p.locator("#dmTools").evaluate("(e)=>e.open=true")
        controls(p)
        swap(p, "institutional-panel")
        p.locator("#dashLayoutDoneBtn").click()
        result = json.loads(stored(p))
        for original in tied["screens"]["dash"]["widgets"]:
            if original["id"] in MOVED:
                assert next(w for w in result["screens"]["dash"]["widgets"] if w["id"] == original["id"]) == original
        p.reload()
        p.wait_for_function("typeof dashLayoutBoot === 'function'")
        assert p.locator("#gdDashMain > [data-layout-card]").evaluate_all("(els)=>els.map(e=>e.dataset.layoutCard)") == ["institutional-panel", "quick-actions"]
        assert not e, e
        c.close()
    # Absent and malformed/invalid v6 remain byte-identical on navigation/reload.
    invalids = [None, "{", json.dumps({"version": 7, "screens": {}})]
    duplicate = copy.deepcopy(PREF)
    duplicate["screens"]["dash"]["widgets"][1]["id"] = IDS[0]
    invalids.append(json.dumps(duplicate))
    invalids.extend(json.dumps({"version": 6, "screens": {"dash": value}}) for value in [None, False, 0, ""])
    for raw_case in invalids:
        c, p, e = open_page(browser, url, raw_case)
        for target in ["forex-overview", "dash"]:
            go(p, target)
        p.reload()
        p.wait_for_function("typeof dashLayoutBoot === 'function'")
        assert stored(p) == raw_case
        assert p.evaluate("window.__layoutWrites") == []
        p.locator("#dmTools").evaluate("(e)=>e.open=true")
        controls(p)
        swap(p, "quick-actions")
        p.locator("#dashLayoutDoneBtn").click()
        if raw_case is None:
            assert json.loads(stored(p))["version"] == 6
            assert len(json.loads(stored(p))["screens"]["dash"]["widgets"]) == 6
        else:
            assert stored(p) == raw_case
            assert p.locator("#dashLayoutBarLabel").evaluate("(e)=>e.classList.contains('dash-layout-bar-error')")
        assert not e, e
        c.close()
    # Failed explicit write leaves preference and edit session available.
    c, p, e = open_page(browser, url, json.dumps(PREF))
    p.locator("#dmTools").evaluate("(e)=>e.open=true")
    controls(p)
    swap(p, "institutional-panel")
    before = stored(p)
    p.evaluate("window.__failLayoutWrite=true")
    p.locator("#dashLayoutDoneBtn").click()
    assert stored(p) == before
    assert p.locator("#dashLayoutBar").is_visible()
    assert "Não foi possível salvar" in p.locator("#dashLayoutBarLabel").inner_text()
    c.close()
    print("PASS relocation/v6: baseline parity, projection, navigation/reload zero-write, explicit save, preservation, cancel, absent/invalid/quota, controls and viewport evidence")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--artifacts", type=Path, default=ROOT / "tools/.artifacts/dashboard-forex-relocation")
    args = parser.parse_args()
    server, url = serve(ROOT)
    baseline_server, baseline = serve(args.baseline_root) if args.baseline_root else (None, None)
    try:
        with sync_playwright() as pw:
            browser = launch_browser(pw)
            run(browser, url, args.artifacts, baseline)
            browser.close()
    finally:
        server.shutdown()
        if baseline_server:
            baseline_server.shutdown()


if __name__ == "__main__":
    main()
