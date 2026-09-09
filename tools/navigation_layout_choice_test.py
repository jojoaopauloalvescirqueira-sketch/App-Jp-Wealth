#!/usr/bin/env python3
"""Navigation composition choice: isolated preferences and real interactions.

CHG-NAVIGATION-LAYOUT-CHOICE-20260909. The lateral default and optional
topbar share existing route/content nodes. No real profile, external API,
reset, migration, build, or Git mutation is used by this focal suite.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright
from dashboard_macro_test import launch_browser
from dashboard_forex_relocation_test import serve
from contextual_sidebar_test import LAYOUT_KEY, LAYOUT_RAW, UNKNOWN_KEY, UNKNOWN_RAW


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "tools/.artifacts/navigation-layout-choice"
KEY = "jpw_nav_layout"
PORTABLE = "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html"
PROTECTED = [KEY, "jpw_nav", "jpw_rail", LAYOUT_KEY, UNKNOWN_KEY]
SOURCES = ["index.html", "src/styles/app.css", "src/js/20-ui/12-nav-style.js",
           "src/js/40-app/11-operational-shell.js", "src/js/40-app/12-global-dashboard.js",
           "src/js/40-app/09-settings-modal.js", "src/js/40-app/14-mvp-notes.js",
           "src/js/manifest.json", "build-id.js",
           PORTABLE, "tools/navigation_layout_choice_test.py"]


def settle(page):
    page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


def boot(browser, url, preference=None, width=1440, style="classic", rail="expanded", read_failure=False):
    seed = {LAYOUT_KEY: LAYOUT_RAW, UNKNOWN_KEY: UNKNOWN_RAW,
            "jpw_nav": style, "jpw_rail": rail}
    if preference is not None:
        seed[KEY] = preference
    context = browser.new_context(viewport={"width": width, "height": 1000 if width > 900 else 844},
                                  service_workers="block")
    context.add_init_script("""(() => {
      const seed=""" + json.dumps(seed, ensure_ascii=False) + """;
      if(!sessionStorage.getItem('__navigationChoiceSeeded')) {
        for(const [k,v] of Object.entries(seed)) localStorage.setItem(k,v);
        sessionStorage.setItem('__navigationChoiceSeeded','1');
      }
      window.__onbShown=true;
      window.__nlOps=[];
      window.__nlReadFailure=""" + json.dumps(read_failure) + """;
      window.__nlWriteFailure=false;
      const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
      const remove=Storage.prototype.removeItem,clear=Storage.prototype.clear;
      window.__nlRaw=()=>Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,get.call(localStorage,k)]));
      Storage.prototype.getItem=function(k){
        if(this===localStorage && String(k)==='jpw_nav_layout' && window.__nlReadFailure)
          throw new DOMException('Synthetic unavailable read','SecurityError');
        return get.call(this,k);
      };
      Storage.prototype.setItem=function(k,v){
        if(this===localStorage){
          window.__nlOps.push(['set',String(k),String(v),document.documentElement?.dataset.navigation]);
          if(String(k)==='jpw_nav_layout' && window.__nlWriteFailure)
            throw new DOMException('Synthetic unavailable write','QuotaExceededError');
        }
        return set.call(this,k,v);
      };
      Storage.prototype.removeItem=function(k){
        if(this===localStorage)window.__nlOps.push(['remove',String(k)]);
        return remove.call(this,k);
      };
      Storage.prototype.clear=function(){
        if(this===localStorage)window.__nlOps.push(['clear']);
        return clear.call(this);
      };
      window.__nlBindings=[];
      const add=EventTarget.prototype.addEventListener;
      EventTarget.prototype.addEventListener=function(type,fn,options){
        window.__nlBindings.push({target:this,type:String(type)});
        return add.call(this,type,fn,options);
      };
    })();""")
    page = context.new_page()
    page.set_default_timeout(12000)
    observed = {"pageerror": [], "console": [], "requestfailed": []}
    page.on("pageerror", lambda e: observed["pageerror"].append(str(e)))
    page.on("console", lambda m: observed["console"].append(m.text) if m.type == "error" else None)
    page.on("requestfailed", lambda r: observed["requestfailed"].append(r.url))
    origin = urlsplit(url)
    prefix = f"{origin.scheme}://{origin.netloc}/"
    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(prefix)
               else route.fulfill(status=200, content_type="application/json", body="{}"))
    if urlsplit(url).path == '/' + PORTABLE:
        # The existing portable HTTP fixtures mount the repository's REAL
        # assets beside dist (finalize_session_test / persistence_failure_test).
        # Keep all console/error assertions: this supplies assets, not stubs.
        page.route('**/dist/assets/**', lambda route: route.continue_(
            url=route.request.url.replace('/dist/assets/', '/assets/')))
    page.goto(url, wait_until="load")
    ready(page)
    page.evaluate("() => {window.alert=()=>{}; closeModal();}")
    return context, page, observed


def ready(page):
    page.wait_for_function("window.JPWNavigation && window.JPWExec?.ui && window.JPWResearch?.ui && window.JPWFin?.ui && window.JPWAlladinUI && typeof compute==='function'")
    settle(page)


def raw(page):
    return page.evaluate("window.__nlRaw()")


def ops(page):
    return page.evaluate("keys=>window.__nlOps.filter(r=>r[0]==='clear'||keys.includes(r[1]))", PROTECTED)


def mode(page):
    return page.get_attribute("html", "data-navigation")


def go(page, route):
    assert page.evaluate("r=>JPWNavigation.navigate(r)", route) is True, route
    settle(page)


def clean(observed):
    assert not any(observed.values()), observed


def finish_context(context):
    # Preserve the original diagnostic BEFORE browser cleanup. A stalled
    # browser close must not hide an assertion or timeout from the operator.
    if sys.exc_info()[0] is not None:
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
    context.close()


def protected_opaque(page):
    current = raw(page)
    assert current[LAYOUT_KEY] == LAYOUT_RAW, "v6 layout preference changed"
    assert current[UNKNOWN_KEY] == UNKNOWN_RAW, "unrelated preference changed"


def assert_structure(page, expected):
    assert mode(page) == expected
    result = page.evaluate("""expected=>{
      const n=document.getElementById('nav'),s=document.getElementById('navSubShell');
      const host=id=>document.getElementById(id);
      return {
        navParent:n.parentElement.id,
        shellAtBody:s.parentElement===document.body,
        shellBeforeContext:!!(s.compareDocumentPosition(host('gdContextRow'))&Node.DOCUMENT_POSITION_FOLLOWING),
        shellInSidebar:!!s.closest('#appSidebar'),
        execParent:host('execNavContexts').parentElement.id,
        researchParent:host('researchNavContexts').parentElement.id,
        primaryCount:n.querySelectorAll(':scope > .tab[data-route]').length,
        duplicateIds:[...document.querySelectorAll('[id]')].map(e=>e.id).filter((id,i,a)=>a.indexOf(id)!==i),
        dash:[...document.querySelectorAll('#gdDashMain > [data-layout-card]')].map(e=>e.dataset.layoutCard).sort(),
        forex:[...document.querySelectorAll('#fxOverviewWidgets > [data-layout-card]')].map(e=>e.dataset.layoutCard).sort()
      };
    }""", expected)
    assert result["navParent"] == ("appSidebar" if expected == "sidebar" else "gdTopbarNavSlot"), result
    assert result["primaryCount"] == 5 and result["duplicateIds"] == [], result
    if expected == "sidebar":
        assert result["shellInSidebar"] and result["execParent"] == result["researchParent"] == "navLocalSlot", result
    else:
        assert result["shellAtBody"] and result["shellBeforeContext"], result
        assert result["execParent"] == "execNavSubmenu" and result["researchParent"] == "researchNavSubmenu", result
        assert not page.locator('[data-nav-expand]').evaluate_all("els=>els.some(e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden')")
    assert result["dash"] == ["institutional-panel", "quick-actions"], result
    assert result["forex"] == ["news-high-impact", "onboarding-alert", "operational-clearance", "vrm"], result
    protected_opaque(page)


def editor(page):
    page.evaluate("() => openSettingsModal('editor')")
    page.locator("#navLayoutSeg").wait_for(state="visible")
    settle(page)
    assert_layout_selection_visual(page, mode(page))


def assert_layout_selection_visual(page, selected):
    # aria-pressed alone cannot prove the visible choice. The existing
    # segmented control uses .on, and its selected colors must differ.
    styles = page.locator('#navLayoutSeg [data-nav-layout]').evaluate_all("""els=>els.map(el=>{
      const c=getComputedStyle(el);
      return {layout:el.dataset.navLayout,on:el.classList.contains('on'),
        background:c.backgroundColor,color:c.color};
    })""")
    active = [item for item in styles if item['layout'] == selected]
    others = [item for item in styles if item['layout'] != selected]
    assert len(active) == 1 and active[0]['on'], (selected, styles, 'selected layout has no visible .on state')
    assert others and all(not item['on'] for item in others), styles
    assert all((item['background'], item['color']) != (active[0]['background'], active[0]['color'])
               for item in others), (selected, styles, 'selected and unselected layout colors are identical')


def assert_document_flow(page, case):
    positions = page.evaluate("""() => {
      const footer=document.getElementById('gdFooter').getBoundingClientRect();
      const main=document.getElementById('appMain').getBoundingClientRect();
      return {footerTop:footer.top,footerHeight:footer.height,mainBottom:main.bottom};
    }""")
    assert positions['footerHeight'] > 0, (case, positions, 'global footer is absent')
    assert positions['footerTop'] >= positions['mainBottom'] - 1, (case, positions, 'footer precedes or overlaps main content')


def assert_settings_isolation(page):
    assert page.locator("#settingsModal").is_visible()
    assert page.locator('#navLayoutSeg').evaluate("el=>!el.closest('[inert],[hidden],[aria-hidden=\"true\"]')")
    # Programmatic focus must also be refused behind the modal, including the
    # N2 container moved OUT of #nav while Settings stays open.
    assert page.evaluate("""() => {
      const previous=document.activeElement;
      const targets=[...document.querySelectorAll('#nav > .tab,#navSubShell button,#navLocalSlot button')];
      const escaped=targets.some(el=>{el.focus();return document.activeElement===el;});
      previous.focus();return !escaped;
    }"""), "background navigation became focusable through an open Settings modal"


def choose(page, expected):
    previous = mode(page)
    page.evaluate("window.__nlOps=[]")
    page.locator(f'#navLayoutSeg [data-nav-layout="{expected}"]').click()
    settle(page)
    assert ops(page) == [["set", KEY, expected, previous]], ops(page)
    assert raw(page)[KEY] == expected
    assert_structure(page, expected)
    assert_layout_selection_visual(page, expected)
    assert_settings_isolation(page)


def run_preferences(browser, url, evidence):
    cases = [None, "sidebar", "topbar", "", "TOPBAR", " topbar ", "future-layout", '{"mode":"topbar"}']
    evidence["preferences"] = []
    for preference in cases:
        context, page, observed = boot(browser, url, preference, style="kinetic", rail="collapsed")
        try:
            expected = preference if preference in {"sidebar", "topbar"} else "sidebar"
            assert_structure(page, expected)
            before = raw(page)
            state = page.evaluate("JSON.stringify(S)")
            for _ in range(2):
                for route in ["forex-overview", "motor", "personal-finance", "pivots", "alladin", "dashboard"]:
                    go(page, route)
            assert page.evaluate("JSON.stringify(S)") == state
            assert raw(page) == before and ops(page) == [], ops(page)
            page.reload(wait_until="load")
            ready(page)
            assert_structure(page, expected)
            assert raw(page) == before and ops(page) == [], ops(page)
            assert page.get_attribute("html", "data-nav-style") == "kinetic"
            assert page.get_attribute("html", "data-rail") == "collapsed"
            clean(observed)
            evidence["preferences"].append({"stored": preference, "presented": expected, "result": "PASS"})
        finally:
            finish_context(context)


def run_failures(browser, url, evidence):
    context, page, observed = boot(browser, url, "topbar", read_failure=True)
    try:
        before = raw(page)
        assert_structure(page, "sidebar")
        for route in ["forex-overview", "pivots", "dashboard"]:
            go(page, route)
        page.reload(wait_until="load")
        ready(page)
        assert_structure(page, "sidebar")
        assert raw(page) == before and ops(page) == []
        clean(observed)
    finally:
        finish_context(context)
    for initial, target in [("sidebar", "topbar"), ("topbar", "sidebar")]:
        context, page, observed = boot(browser, url, initial)
        try:
            editor(page)
            before = raw(page)
            state = page.evaluate("JSON.stringify(S)")
            page.evaluate("window.__nlOps=[];window.__nlWriteFailure=true")
            page.locator(f'#navLayoutSeg [data-nav-layout="{target}"]').click()
            settle(page)
            assert ops(page) == [["set", KEY, target, initial]], ops(page)
            assert_structure(page, initial)
            assert_layout_selection_visual(page, initial)
            status = page.locator("#navLayoutStatus")
            assert status.is_visible() and status.get_attribute("role") == "status"
            assert status.inner_text().strip(), "write rejection was not announced"
            assert status.evaluate("el=>!el.closest('[inert],[hidden],[aria-hidden=\"true\"]')")
            assert raw(page) == before and page.evaluate("JSON.stringify(S)") == state
            assert_settings_isolation(page)
            page.locator("#settingsCloseBtn").click()
            settle(page)
            page.reload(wait_until="load")
            ready(page)
            assert_structure(page, initial)
            assert raw(page) == before
            clean(observed)
        finally:
            finish_context(context)
    evidence["failures"] = "PASS: denied read preserves bytes; denied writes in either direction keep the prior presentation and announce in Editor"


def current_snapshot(page):
    return page.evaluate("""() => ({
      state:JSON.stringify(S),compute:compute(),clearance:getOperationalClearance(),
      current:JPWNavigation.current(),exec:JPWExec.ui.getView(),finpes:JPWFin.ui.getView(),
      research:JPWResearch.ui.getView(),fxplan:window.JPWFx?.ui?.getView(),
      nocoda:{selected:ncSelectedId,draft:ncDraft,dirty:ncDirty},
      pivots:{instrument:pvInstrumentId,study:pvStudyId,newOpen:pvNewStudyOpen,
        newDraft:pvNewStudyDraft,formOpen:pvFormOpen,draft:pvDraft,filters:pvFilters,sort:pvSort},
      inputs:[...document.querySelectorAll('#exec input,#exec textarea,#research input,#research textarea')]
        .map(e=>({id:e.id,value:e.value,checked:e.checked})),
      details:[...document.querySelectorAll('#exec details,#research details')].map(e=>e.open)
    })""")


def bindings(page):
    return page.evaluate("""() => {
      const stable=[window,document,...document.querySelectorAll('#nav,#appSidebar,#navSubShell,#railToggle,#navLayoutSeg button,#nav > .tab,[data-nav-expand]')];
      return window.__nlBindings.filter(r=>stable.includes(r.target)).map(r=>[
        r.target===window?'window':r.target===document?'document':r.target.id||r.target.dataset.navLayout||r.target.dataset.navExpand,r.type]);
    }""")


def guard_content_calls(page):
    page.evaluate("""() => {
      window.__nlForbiddenCalls=[];window.__nlOriginalCalls={};
      for(const name of ['boot','render','navApply','renderNocodaStudies','renderPivotStudies',
        'finpesOverviewRender','finpesBudgetRender','finpesDebtsRender','finpesComparisonRender',
        'finpesScenariosRender','alladinRender']) {
        if(typeof window[name]!=='function')continue;
        const original=window[name];window.__nlOriginalCalls[name]=original;
        window[name]=function(){window.__nlForbiddenCalls.push(name);return original.apply(this,arguments);};
      }
    }""")


def run_lifecycle(browser, url, evidence):
    context, page, observed = boot(browser, url)
    try:
        # Existing controls create unsaved technical drafts. No save is invoked.
        go(page, "nocoda")
        page.locator("#ncDate1").fill("2026-08-01T10:00")
        page.locator("#ncPrice1").fill("1.12345")
        go(page, "pivots")
        page.locator("#pvNewStudyBtn").click()
        page.locator("#pvPeriodStart").fill("2026-08-01")
        page.locator("#pvPeriodEnd").fill("2026-08-31")
        for route in ["pivots", "forex-operation", "nocoda"]:
            go(page, route)
            editor(page)
            before = current_snapshot(page)
            storage_before = raw(page)
            page.evaluate("""() => {
              window.__nlNodes=[...document.querySelectorAll('#nav,#appSidebar,#navSubShell,#execNavContexts,#researchNavContexts,#railToggle,#sidebarClose,#exec input,#research input,#fxOverviewWidgets,#mcClearanceCard')];
            }""")
            prior_bindings = bindings(page)
            guard_content_calls(page)
            for target in ["topbar", "sidebar"] * 3:
                choose(page, target)
                assert current_snapshot(page) == before, (route, target, "content/context changed during layout switch")
                assert page.evaluate("window.__nlForbiddenCalls") == [], page.evaluate("window.__nlForbiddenCalls")
                assert page.evaluate("window.__nlNodes.every(e=>e.isConnected&&(!e.id||document.getElementById(e.id)===e))")
                assert bindings(page) == prior_bindings, "switching added a stable-node listener"
                assert {k: v for k, v in raw(page).items() if k != KEY} == {k: v for k, v in storage_before.items() if k != KEY}
            page.evaluate("() => {for(const [k,v] of Object.entries(window.__nlOriginalCalls))window[k]=v}")
            page.locator("#settingsCloseBtn").click()
            settle(page)
            assert current_snapshot(page) == before
            assert page.locator("#railToggle").evaluate("e=>e.parentElement.id==='appSidebar'")
            assert not page.locator("#nav").evaluate("e=>e.inert")
        # Save the secondary choice and reload; no second explicit write occurs.
        editor(page)
        choose(page, "topbar")
        page.locator("#settingsCloseBtn").click()
        storage_before = raw(page)
        page.reload(wait_until="load")
        ready(page)
        assert_structure(page, "topbar")
        assert raw(page) == storage_before and ops(page) == []
        clean(observed)
        evidence["lifecycle"] = "PASS: 18 switches, original DOM/listeners, route/views/drafts/financial reads unchanged, Settings isolation and explicit choice reload"
    finally:
        finish_context(context)


def drawer_open(page, layout):
    page.locator('[data-shell-menu-toggle]').click()
    page.wait_for_function("document.documentElement.dataset.shellMenu==='open'")
    settle(page)
    selector = "#appSidebar" if layout == "sidebar" else "#nav"
    drawer = page.locator(selector)
    assert drawer.is_visible() and drawer.get_attribute("role") == "dialog"
    assert drawer.get_attribute("aria-modal") == "true"
    assert drawer.evaluate("e=>e.contains(document.activeElement)")
    assert page.locator("#appMain").evaluate("e=>e.inert")
    return drawer


def drawer_closed(page, restore=False):
    page.wait_for_function("document.documentElement.dataset.shellMenu!=='open'")
    settle(page)
    assert not page.locator("#appMain").evaluate("e=>e.inert")
    assert page.evaluate("document.body.style.overflow") != "hidden"
    if restore:
        assert page.locator('[data-shell-menu-toggle]').evaluate("e=>e===document.activeElement")


def module_entry_keys(page, layout, evidence):
    # N3 remains in the topbar's module panel. Entering N2 from its trigger
    # must never pick a hidden N3 item simply because it is last in DOM order.
    cases = [('forex-overview', 'exec', 'forex-overview', 'forex-planning'),
             ('forex-operation', 'exec', 'forex-operation', 'forex-planning'),
             ('research-forex', 'research', 'research-forex', 'research-others'),
             ('pivots', 'research', 'research-forex', 'research-others')]
    for route, module, current_child, last_child in cases:
        trigger = (f'#{module}NavTrigger' if layout == 'topbar'
                   else f'[data-nav-expand="{module}"]')
        for key, expected in [('ArrowUp', last_child), ('ArrowDown', current_child)]:
            go(page, route)
            page.locator(trigger).focus()
            page.keyboard.press(key)
            settle(page)
            target = page.locator(f'#{module}NavSubmenu [data-nav-child="{expected}"]')
            assert target.evaluate('e=>e===document.activeElement'), (layout, route, key, expected, 'trigger did not focus expected N2')
            assert target.evaluate("""e=>!e.closest('[hidden],[inert]')&&
              e.getBoundingClientRect().height>0&&getComputedStyle(e).visibility!=='hidden'"""), (layout, route, key, 'focus landed in an unavailable subtree')
            page.keyboard.press('Enter')
            settle(page)
            actual = page.evaluate('JPWNavigation.current().canonical')
            assert actual == expected, (layout, route, key, expected, actual)
            if key == 'ArrowUp' and module == 'exec':
                assert page.evaluate('JPWFx.ui.getView()') == 'overview'
            evidence.append({'layout': layout, 'from': route, 'key': key,
                             'focused_n2': expected, 'entered': actual, 'result': 'PASS'})


def run_navigation(browser, url, evidence):
    evidence['module_entry_keys'] = []
    for layout in ["sidebar", "topbar"]:
        context, page, observed = boot(browser, url, layout)
        try:
            before = raw(page)
            module_entry_keys(page, layout, evidence['module_entry_keys'])
            page.locator('#execNavTrigger').click()
            settle(page)
            assert page.evaluate("JPWNavigation.current().canonical") == "forex-overview"
            page.locator('[data-nav-child="forex-operation"]').click()
            settle(page)
            page.locator('[data-nav-local-surface="exec"][data-nav-local-view="motor"]').click()
            settle(page)
            assert page.evaluate("JPWExec.ui.getView()") == "motor"
            page.locator('#researchNavTrigger').click()
            settle(page)
            page.locator('[data-nav-local-surface="research"][data-nav-local-view="nocoda"]').click()
            settle(page)
            assert page.evaluate("JPWResearch.ui.getView()") == "nocoda"
            page.locator('#finpesNavTrigger').click()
            settle(page)
            page.locator('[data-nav-sub-view="cenarios"]').click()
            assert page.evaluate("JPWFin.ui.getView()") == "cenarios"
            if layout == "topbar":
                page.locator('#finpesNavTrigger').focus()
                page.keyboard.press('ArrowDown')
            else:
                page.locator('[data-nav-expand="finpes"]').focus()
                page.keyboard.press('ArrowDown')
            settle(page)
            assert page.locator('#finpesNavSubmenu').evaluate("e=>e.contains(document.activeElement)")
            page.keyboard.press('Home')
            assert page.locator('[data-nav-sub-view="overview"]').evaluate("e=>e===document.activeElement")
            page.keyboard.press('End')
            assert page.locator('[data-nav-sub-view="cenarios"]').evaluate("e=>e===document.activeElement")
            page.keyboard.press('ArrowUp')
            page.keyboard.press('Enter')
            assert page.evaluate("JPWFin.ui.getView()") == "comparativo"
            page.locator('#brandHomeBtn').click()
            settle(page)
            assert page.evaluate("JPWNavigation.current().canonical") == "dashboard"
            assert_structure(page, layout)
            assert raw(page) == before and ops(page) == []
            clean(observed)
        finally:
            finish_context(context)
        context, page, observed = boot(browser, url, layout, width=390)
        try:
            before = raw(page)
            drawer = drawer_open(page, layout)
            for key in ['Tab'] * 14 + ['Shift+Tab'] * 14:
                page.keyboard.press(key)
                assert drawer.evaluate("e=>e.contains(document.activeElement)"), "mobile focus escaped"
            page.keyboard.press('Escape')
            drawer_closed(page, restore=True)
            drawer_open(page, layout)
            page.locator('#sidebarClose').click()
            drawer_closed(page, restore=True)
            drawer_open(page, layout)
            # The topbar drawer spans the viewport width; click BELOW it.
            # The same visible backdrop point is outside the lateral drawer.
            page.locator('#sidebarBackdrop').click(position={"x": 385, "y": 800})
            drawer_closed(page, restore=True)
            drawer_open(page, layout)
            page.locator('#execNavTrigger').click()
            drawer_closed(page)
            assert page.evaluate("JPWNavigation.current().canonical") == "forex-overview"
            if layout == "sidebar":
                drawer_open(page, layout)
            page.locator('[data-nav-child="forex-operation"]').click()
            drawer_closed(page)
            assert page.evaluate("JPWExec.ui.getView()") == "panel"
            assert page.locator('#exec').evaluate("e=>e.contains(document.activeElement)")
            drawer_open(page, layout)
            page.set_viewport_size({"width": 1440, "height": 1000})
            drawer_closed(page)
            assert_structure(page, layout)
            assert raw(page) == before and ops(page) == []
            clean(observed)
        finally:
            finish_context(context)
    evidence["navigation"] = "PASS: physical N1/N2/N3, Home/End/arrows/Enter, mobile trap/Escape/backdrop/close, child focus and resize in both compositions"


def run_notes(browser, url, evidence):
    for layout in ['sidebar', 'topbar']:
        context, page, observed = boot(browser, url, layout)
        try:
            page.locator('#execNavTrigger').click()
            page.locator('[data-nav-child="forex-operation"]').click()
            settle(page)
            before = raw(page)
            page.locator('#headerNotesBtn').click()
            page.locator('#mvpNotesDrawer').wait_for(state='visible')
            settle(page)
            for width in [1440, 390, 1024, 320, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000 if width > 900 else 844})
                settle(page)
                assert page.evaluate("""() => {
                  const previous=document.activeElement;
                  const escaped=[...document.querySelectorAll('#nav > .tab,#navSubShell button,#navLocalSlot button')]
                    .some(el=>{el.focus();return document.activeElement===el;});
                  if(previous?.isConnected)previous.focus();return !escaped;
                }"""), (layout, width, 'navigation became focusable behind Tickets after resize')
                assert page.locator('#mvpNotesDrawer').evaluate("e=>!e.closest('[inert],[hidden],[aria-hidden=\"true\"]')")
            page.locator('#mvpNotesCloseBtn').click()
            page.locator('#mvpNotesOverlay').wait_for(state='hidden')
            settle(page)
            assert not page.locator('#nav').evaluate('e=>e.inert')
            assert not page.locator('#appMain').evaluate('e=>e.inert')
            page.locator('#finpesNavTrigger').click()
            settle(page)
            assert page.evaluate('JPWNavigation.current().primary') == 'personal-finance'
            assert raw(page) == before, 'opening/resizing/closing Tickets rewrote browser preferences'
            protected_opaque(page)
            clean(observed)
        finally:
            finish_context(context)
    evidence['notes'] = 'PASS: Tickets isolates both navigation layouts through five desktop/mobile resizes; close restores working navigation'


def run_visual(browser, url, evidence, capture, artifacts):
    evidence["visual_matrix"] = []
    evidence["screenshots"] = []
    builds = set()
    for layout in ["sidebar", "topbar"]:
        for rail in ["expanded", "collapsed"]:
            context, page, observed = boot(browser, url, layout, rail=rail)
            try:
                builds.add(page.evaluate("JP_WEALTH_BUILD_ID"))
                for style in ["classic", "pill", "kinetic"]:
                    editor(page)
                    page.locator(f'#navStyleSeg [data-nav-val="{style}"]').click()
                    for editor_theme in ['light', 'dark']:
                        page.evaluate('t=>document.documentElement.dataset.theme=t', editor_theme)
                        settle(page)
                        assert_layout_selection_visual(page, layout)
                        if capture and rail == 'expanded' and style == 'classic':
                            name = f'{layout}-editor-1440-{editor_theme}.png'
                            page.screenshot(path=str(artifacts / name), full_page=True)
                            evidence['screenshots'].append(name)
                    page.locator('#settingsCloseBtn').click()
                    settle(page)
                    assert mode(page) == layout and raw(page)["jpw_rail"] == rail
                    for width in [1440, 1024, 390, 320]:
                        page.set_viewport_size({"width": width, "height": 1000 if width > 900 else 844})
                        for theme in ["light", "dark"]:
                            page.evaluate("t=>document.documentElement.dataset.theme=t", theme)
                            go(page, 'forex-overview')
                            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), (layout, rail, style, width, theme, "overflow")
                            assert_document_flow(page, (layout, rail, style, width, theme, 'forex-overview'))
                            if width > 900:
                                assert page.locator('#nav > .tab.active').is_visible()
                                if style != "classic":
                                    page.wait_for_function("() => {const e=document.getElementById('navPillIndicator');return e.getBoundingClientRect().width>0&&e.style.transform.includes('translate')}")
                                    assert page.locator('#navPillIndicator').is_visible()
                                if layout == "sidebar":
                                    assert page.evaluate("appSidebar.getBoundingClientRect().right<=appMain.getBoundingClientRect().left+1")
                            else:
                                drawer_open(page, layout)
                                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
                                targets = page.locator('#nav > .tab,#sidebarClose').evaluate_all("els=>els.filter(e=>e.getClientRects().length).map(e=>({id:e.id,w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))")
                                assert targets and all(t['w'] >= 44 and t['h'] >= 44 for t in targets), targets
                                page.keyboard.press('Escape')
                                drawer_closed(page, restore=True)
                            if capture and rail == "expanded" and style == "classic" and width in [1440, 390]:
                                for route, label in [('dashboard', 'dashboard'), ('forex-overview', 'forex')]:
                                    go(page, route)
                                    assert_document_flow(page, (layout, rail, style, width, theme, route))
                                    name = f'{layout}-{label}-{width}-{theme}.png'
                                    page.screenshot(path=str(artifacts / name), full_page=True)
                                    evidence['screenshots'].append(name)
                            evidence['visual_matrix'].append({'layout': layout, 'rail': rail, 'style': style, 'width': width, 'theme': theme, 'result': 'PASS'})
                    page.set_viewport_size({"width": 1440, "height": 1000})
                protected_opaque(page)
                clean(observed)
            finally:
                finish_context(context)
    assert len(builds) == 1, builds
    evidence['browser_build'] = next(iter(builds))
    evidence['visual_limit'] = '1440/1024/390/320 CSS px; no claim of real browser zoom, screen reader session or exhaustive WCAG audit'


def run_portable(browser, url, evidence):
    portable_url = url.rsplit('/', 1)[0] + '/' + PORTABLE
    context, page, observed = boot(browser, portable_url, "topbar")
    try:
        build = page.evaluate('JP_WEALTH_BUILD_ID')
        assert build in (ROOT / 'build-id.js').read_text(), 'portable build differs from modular candidate'
        assert_structure(page, 'topbar')
        go(page, 'forex-operation')
        editor(page)
        before = current_snapshot(page)
        choose(page, 'sidebar')
        choose(page, 'topbar')
        assert current_snapshot(page) == before
        page.locator('#settingsCloseBtn').click()
        stored = raw(page)
        page.reload(wait_until='load')
        ready(page)
        assert_structure(page, 'topbar')
        assert raw(page) == stored and ops(page) == []
        clean(observed)
        evidence['portable'] = {'result': 'PASS', 'build': build,
            'scope': 'same composition/topology, explicit switches, unchanged context, reload/storage',
            'mounting': 'existing HTTP fixture: /dist/assets/ routes to the real repository /assets/; no error suppression',
            'limit': 'not proof of standalone operation without accompanying assets'}
    finally:
        finish_context(context)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifacts', type=Path, default=ARTIFACTS)
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--only', choices=['preferences', 'failures', 'lifecycle', 'navigation', 'notes', 'visual', 'portable'])
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    evidence = {'result': 'RUNNING', 'started_at_epoch': time.time(), 'source_sha256': hashes,
                'build_file': (ROOT / 'build-id.js').read_text().strip(), 'only': args.only}
    report = args.artifacts / (f'focal-{args.only}.json' if args.only else 'focal-results.json')
    server, url = serve(ROOT)
    try:
        with sync_playwright() as pw:
            browser = launch_browser(pw)
            evidence['browser'] = browser.version
            try:
                runs = {'preferences': lambda: run_preferences(browser, url, evidence),
                        'failures': lambda: run_failures(browser, url, evidence),
                        'lifecycle': lambda: run_lifecycle(browser, url, evidence),
                        'navigation': lambda: run_navigation(browser, url, evidence),
                        'notes': lambda: run_notes(browser, url, evidence),
                        'visual': lambda: run_visual(browser, url, evidence, args.capture, args.artifacts),
                        'portable': lambda: run_portable(browser, url, evidence)}
                for name, run in runs.items():
                    if args.only and args.only != name:
                        continue
                    evidence['current_group'] = name
                    try:
                        run()
                    except BaseException as error:
                        evidence['result'] = 'FAIL — classification requires triage'
                        evidence['error'] = repr(error)
                        report.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n')
                        raise
                    print(f'PASS navigation layout choice: {name}', flush=True)
                assert hashes == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}, 'candidate changed during focal execution'
                evidence['result'] = 'PASS'
                print('PASS navigation_layout_choice_test — declared groups only', flush=True)
            finally:
                browser.close()
    except Exception as error:
        evidence['result'] = 'FAIL — classification requires triage'
        evidence['error'] = repr(error)
        raise
    finally:
        evidence['elapsed_seconds'] = round(time.time() - evidence['started_at_epoch'], 3)
        report.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n')
        server.shutdown()


if __name__ == '__main__':
    main()
