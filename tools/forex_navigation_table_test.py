#!/usr/bin/env python3
"""Forex table navigation: seven destinations, one History, isolated workspaces.
Synthetic fresh browser contexts; no financial fixture or external network.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright
from notes_launcher_test import launch_options
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]
CHILDREN = ['forex-consolidated', 'forex-management-accounts', 'forex-operation', 'forex-history',
            'forex-accounting', 'forex-planning', 'forex-reserves']
LABELS = ['Dashboard', 'Contas e Período', 'Execution Board', 'History',
          'Contabilidade', 'Planejamento', 'Reservas']
VIEWS = [('forex-operation', 'panel', 'executionBoard'),
         ('forex-history', 'history', 'execHistory'),
         ('forex-accounting', 'accounting', 'contab'),
         ('forex-management-accounts', 'accounts', 'contas'),
         ('motor', 'motor', 'motorWidgetGrid')]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            for layout in ['sidebar', 'topbar', 'glass', 'submenu']:
                context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
                context.add_init_script('window.__onbShown=true;localStorage.setItem("jpw_nav_layout",'+json.dumps(layout)+');')
                install_bootstrap(context)
                page = context.new_page(); page.set_default_timeout(5000)
                errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page)
                assert page.evaluate("JPWNavigation.children('forex').map(r=>r.id)") == CHILDREN
                assert page.locator('#execNavSubmenu [data-nav-child] .nav-sub-item-title').all_text_contents() == LABELS
                assert page.locator('#execNavSubmenu [data-nav-child]').count() == 7
                assert page.evaluate("execHistory.parentElement.id==='exec'&&!contab.contains(execHistory)")
                page.evaluate("""() => {
                  window.__navBefore=JSON.stringify(S); window.__navRaw=JSON.stringify({...localStorage});
                  window.__navNodes=['executionBoard','execWidgetGrid','execHistory','contab','contas','motorWidgetGrid'].map(id=>document.getElementById(id));
                  window.__navWrites=[];
                  for(const method of ['setItem','removeItem','clear']){const original=Storage.prototype[method];Storage.prototype[method]=function(...args){__navWrites.push(method);return original.apply(this,args);};}
                }""")
                for _ in range(2):
                    for route, view, host in VIEWS:
                        assert page.evaluate('(r)=>JPWNavigation.navigate(r)', route)
                        assert page.evaluate('JPWExec.ui.getView()') == view
                        assert page.locator('#'+host).is_visible(), (layout, route, host)
                        assert page.evaluate("""host=>['executionBoard','execHistory','contab','contas','motorWidgetGrid']
                          .filter(id=>id!==host).every(id=>document.getElementById(id).hidden&&document.getElementById(id).inert)""", host)
                        assert page.evaluate("(view)=>execWidgetGrid.hidden===(view!=='panel')", view)
                for alias, child, view in [('history', 'forex-history', 'history'), ('contab', 'forex-accounting', 'accounting'),
                    ('forex-reconciliation', 'forex-accounting', 'accounting'), ('contas','forex-management-accounts','accounts'),
                    ('forex-account','forex-management-accounts','accounts'), ('motor','forex-management-accounts','motor')]:
                    assert page.evaluate('(r)=>JPWNavigation.navigate(r)', alias)
                    assert page.evaluate('JPWNavigation.current().child') == child
                    assert page.evaluate('JPWExec.ui.getView()') == view
                # Moving between workspaces is presentation only and conserves exact nodes.
                assert page.evaluate('JSON.stringify(S)===__navBefore&&JSON.stringify({...localStorage})===__navRaw&&__navWrites.length===0')
                assert page.evaluate('__navNodes.every(el=>el===document.getElementById(el.id))')
                # Rejected destination must not replace the current route, panel or focus.
                page.evaluate("JPWNavigation.navigate('forex-operation');window.__navGuard=JPWForex.executionBoardUI.guardNavigation;JPWForex.executionBoardUI.guardNavigation=()=>false")
                assert not page.evaluate("JPWNavigation.navigate('forex-history')")
                assert page.evaluate("JPWNavigation.current().child==='forex-operation'&&JPWExec.ui.getView()==='panel'&&!executionBoard.hidden&&execHistory.hidden")
                page.evaluate('() => {JPWForex.executionBoardUI.guardNavigation=__navGuard;}')
                if layout == 'submenu':
                    # Management Accounts explores N3 without navigation; Board/History are leaves.
                    page.locator('#execNavTrigger').click()
                    before = page.evaluate('JPWNavigation.current()')
                    page.locator('[data-nav-child="forex-management-accounts"]').click()
                    assert page.get_attribute('html', 'data-submenu-level') == '3'
                    assert page.evaluate('JPWNavigation.current()') == before
                    page.locator('[data-nav-local-view="motor"]').click()
                    assert page.evaluate('JPWExec.ui.getView()') == 'motor'
                    page.locator('#submenuNavBack').click()
                    page.locator('[data-nav-child="forex-history"]').click()
                    assert page.get_attribute('html', 'data-submenu-level') == '2'
                    assert page.evaluate('JPWExec.ui.getView()') == 'history'
                assert not errors, errors
                assert_fixture_requests(context)
                context.close()
                print('PASS Forex table navigation:', layout)
            browser.close()
    finally:
        server.shutdown()

if __name__ == '__main__': main()
