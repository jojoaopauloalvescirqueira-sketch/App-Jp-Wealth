#!/usr/bin/env python3
"""CHG-JPW-SIDEBAR-20261001: real sidebar gestures in isolated synthetic origins.

The oracle is the approved UX contract, not controller internals. No real data,
financial rule, build, gate, classifier or persistent schema is changed here.
Existing fixtures supply the real application and inert external responses.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import traceback

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dashboard_macro_test import launch_browser
from dashboard_forex_relocation_test import serve
from navigation_layout_choice_test import boot, clean, finish_context, go, raw, ready, settle
from forex_execution_table_test import SEED as BOARD_SEED, HASH, field, order, set_field, prepare_drafts
from forex_accounts_workspace_test import SEED as ACCOUNTS_SEED

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACTS = Path('/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-sidebar-20261001/sidebar-focal')
PORTABLE = 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
SOURCES = ['index.html', 'src/styles/app.css', 'src/js/40-app/01-navigation.js',
           'src/js/40-app/11-operational-shell.js', 'src/js/20-ui/02-sidebar.js',
           'src/js/20-ui/12-nav-style.js', 'src/js/40-app/09-settings-modal.js',
           'tools/navigation_sidebar_hover_test.py', 'build-id.js']


def instrument(page):
    """Observe original dispatch/render functions; wrappers keep their returns."""
    page.evaluate("""() => {
      window.__shCalls=[];window.__shRefs=['nav','navSubShell','railToggle','navLocalSlot',
        'execNavContexts','researchNavContexts'].map(id=>document.getElementById(id));
      const wrap=(owner,key,label)=>{if(typeof owner?.[key]!=='function')return false;
        const original=owner[key];const spy=function(...args){__shCalls.push(label);return original.apply(this,args);};
        owner[key]=spy;return owner[key]===spy;};
      for(const name of ['navigateToScreen','navApply','boot','render','renderNocodaStudies',
        'renderPivotStudies','finpesOverviewRender','finpesBudgetRender','finpesDebtsRender',
        'finpesComparisonRender','finpesScenariosRender','alladinRender'])wrap(window,name,name);
      for(const [owner,key,label] of [[JPWForex,'ui','forex.render'],
        [window,'JPWFXConsolidated','consolidated.render']]){
        const ui=owner[key];if(ui&&typeof ui.render==='function'){
          const original=ui.render;owner[key]={...ui,render:function(...args){__shCalls.push(label);return original.apply(ui,args);}};
        }
      }
      for(const [key,label] of [['executionBoardUI','board.guard'],['accountsUI','accounts.guard']]){
        const ui=JPWForex[key];if(typeof ui?.guardNavigation!=='function')throw Error('Missing real guard '+key);
        const original=ui.guardNavigation;
        JPWForex[key]={...ui,guardNavigation:function(...args){__shCalls.push(label);return original.apply(ui,args);}};
      }
      if(!window.__shRefs.every(Boolean))throw Error('Missing stable navigation node');
      window.__nlOps=[];
    }""")


def snapshot(page):
    return page.evaluate("""() => ({route:JPWNavigation.current(),state:JSON.stringify(S),
      storage:__nlRaw(),location:document.getElementById('shellLocation').textContent,
      contexts:[...document.querySelectorAll('#navLocalSlot [data-nav-context]')]
        .map(e=>({key:e.dataset.navContext,hidden:e.hidden,inert:e.inert})),
      primary:[...document.querySelectorAll('#nav > .tab[aria-current="page"]')].map(e=>e.dataset.primary),
      local:[...document.querySelectorAll('#navLocalSlot [aria-current="page"]')]
        .map(e=>[e.dataset.navLocalSurface,e.dataset.navLocalView,e.dataset.navRoute])})""")


def assert_untouched(page, before, focus=None):
    assert snapshot(page) == before, 'exploration changed route, N3, data, preferences or location'
    assert page.evaluate('__shCalls') == [], page.evaluate('__shCalls')
    assert page.evaluate('__nlOps') == [], page.evaluate('__nlOps')
    assert page.evaluate('__shRefs.every(e=>e.isConnected&&document.getElementById(e.id)===e)'), 'navigation node replaced'
    if focus is not None:
        assert page.evaluate('document.activeElement.id') == focus, 'hover stole focus'
    assert page.evaluate("""() => {const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return new Set(ids).size===ids.length;}"""), 'duplicate IDs'


def visible_group(page):
    return page.locator('#navSubShell .nav-sub-menu').evaluate_all("""els=>els.filter(e=>
      !e.closest('[hidden],[inert]')&&e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden').map(e=>e.id)""")


def expect_group(page, key):
    page.wait_for_function("key=>document.getElementById(key+'NavTrigger').getAttribute('aria-expanded')==='true'", arg=key)
    assert visible_group(page) == [key + 'NavSubmenu'], visible_group(page)
    assert page.locator('#'+key+'NavTrigger').evaluate("e=>e.classList.contains('sidebar-group-open')")
    assert page.get_attribute('html', 'data-sidebar-group') == key


def close_group(page):
    page.locator('#nav > .tab[data-primary="dashboard"]').focus()
    page.keyboard.press('Escape')
    page.mouse.move(900, 700)
    page.wait_for_timeout(350)


def run_timing(browser, url, evidence, capture, artifacts):
    context, page, observed = boot(browser, url, 'sidebar')
    try:
        go(page, 'forex-management-accounts')
        page.locator('#brandHomeBtn').focus()
        instrument(page);before=snapshot(page);focus=page.evaluate('document.activeElement.id')
        page.locator('#toolsNavTrigger').hover()
        page.wait_for_timeout(200)
        assert page.locator('#toolsNavTrigger').get_attribute('aria-expanded') != 'true', 'hover opened before dwell'
        page.wait_for_timeout(250);expect_group(page,'tools')
        assert_untouched(page,before,focus)
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').hover()
        page.wait_for_timeout(350);expect_group(page,'tools')
        assert_untouched(page,before,focus)
        page.mouse.move(900,700);page.wait_for_timeout(100)
        expect_group(page,'tools')
        page.wait_for_timeout(300);expect_group(page,'exec')
        assert_untouched(page,before,focus)
        for key in ['research','tools','finpes']:
            page.locator('#'+key+'NavTrigger').hover();page.wait_for_timeout(80)
        page.mouse.move(900,700);page.wait_for_timeout(500)
        expect_group(page,'exec');assert_untouched(page,before,focus)
        # A previewed inactive module must not advertise its remembered local view.
        page.locator('#finpesNavTrigger').hover();page.wait_for_timeout(450)
        expect_group(page,'finpes')
        assert page.locator('#finpesNavSubmenu [aria-current="page"]').count()==0
        assert_untouched(page,before,focus)
        if capture:page.screenshot(path=str(artifacts/'n3-intact-other-group.png'))
        page.keyboard.press('Escape');expect_group(page,'exec')
        assert_untouched(page,before,focus)
        page.wait_for_timeout(500);expect_group(page,'exec')
        clean(observed)
        evidence['timing']='PASS: dwell/departure, pointer corridor, fast passes, Escape restores pin, no dispatch/guard/render/write/focus, active N3 intact'
    finally:finish_context(context)


def run_clicks(browser, url, evidence, capture, artifacts):
    context,page,observed=boot(browser,url,'sidebar')
    try:
        instrument(page);before=snapshot(page)
        page.locator('#toolsNavTrigger').click();assert_untouched(page,before);expect_group(page,'tools')
        page.mouse.move(900,700);page.wait_for_timeout(450);expect_group(page,'tools')
        page.locator('#toolsNavTrigger').click();page.wait_for_timeout(500)
        assert visible_group(page)==[], 'same parent click did not collapse or hover reopened it'
        assert_untouched(page,before)
        page.locator('#execNavTrigger').click();expect_group(page,'exec')
        page.keyboard.press('Escape');page.wait_for_timeout(500)
        assert visible_group(page)==[] and page.evaluate('document.activeElement.id')=='execNavTrigger'
        assert_untouched(page,before)
        page.mouse.move(900,700);page.locator('#execNavTrigger').click();expect_group(page,'exec')
        page.locator('#appMain').click(position={'x':300,'y':120})
        # Outside closes the temporary overlay; an expanded pinned group stays.
        expect_group(page,'exec');assert_untouched(page,before)
        page.locator('#execNavSubmenu [data-nav-child="forex-reserves"]').click();settle(page)
        calls=page.evaluate('__shCalls')
        assert calls.count('navigateToScreen')==1 and calls.count('navApply')==1, calls
        assert calls.count('board.guard')==1 and calls.count('accounts.guard')==1, calls
        assert page.evaluate('JPWNavigation.current().canonical')=='forex-reserves'
        assert page.evaluate("document.getElementById('fxreserves').contains(document.activeElement)")
        assert page.evaluate('JSON.stringify(S)')==before['state'] and raw(page)==before['storage']
        assert page.evaluate('__nlOps')==[]
        if capture:page.screenshot(path=str(artifacts/'leaf-single-dispatch.png'))
        clean(observed);evidence['clicks']='PASS: parent disclosure/pin/collapse, Escape suppression, expanded pin persistence and single guarded leaf dispatch'
    finally:finish_context(context)


def run_guard(browser,url,evidence,capture,artifacts):
    context,page,observed=boot(browser,url,'sidebar')
    try:
        go(page,'forex-operation');instrument(page)
        # Explicit negative-control fixture; guard itself is left in the dispatch.
        # A second positive control below proves that the leaf path also succeeds.
        page.evaluate("""() => {const ui=JPWForex.executionBoardUI,original=ui.guardNavigation;
          window.__shGuardOriginal=original;ui.guardNavigation=function(){__shCalls.push('fixture.refusal');return false;};}""")
        before=snapshot(page)
        page.locator('#toolsNavTrigger').click();expect_group(page,'tools')
        assert_untouched(page,before)
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click();settle(page)
        assert snapshot(page)==before and visible_group(page)==['toolsNavSubmenu']
        calls=page.evaluate('__shCalls');assert calls.count('navigateToScreen')==1 and calls.count('fixture.refusal')==1,calls
        assert page.evaluate('__nlOps')==[]
        page.evaluate("JPWForex.executionBoardUI.guardNavigation=__shGuardOriginal;__shCalls=[]")
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click();settle(page)
        assert page.evaluate('JPWNavigation.current().canonical')=='tools-calendar'
        assert page.evaluate('__shCalls.filter(n=>n===\'navigateToScreen\').length')==1
        clean(observed);evidence['guard']='PASS: real leaf event crosses one guard, refusal preserves route/N2/data; restored guard accepts same leaf'
    finally:finish_context(context)


def run_keyboard(browser,url,evidence,capture,artifacts):
    context,page,observed=boot(browser,url,'sidebar',rail='collapsed')
    try:
        instrument(page);before=snapshot(page)
        page.locator('#execNavTrigger').focus();page.keyboard.press('ArrowRight');expect_group(page,'exec')
        assert page.evaluate('document.activeElement.dataset.navChild')=='forex-consolidated'
        items=page.locator('#execNavSubmenu .nav-sub-level-primary [data-nav-child]')
        assert items.evaluate_all('els=>els.every(e=>e.tabIndex===0)'), 'visible N2 children missing from Tab sequence'
        page.keyboard.press('End');assert page.evaluate('document.activeElement.dataset.navChild')=='forex-reserves'
        page.keyboard.press('Home');assert page.evaluate('document.activeElement.dataset.navChild')=='forex-consolidated'
        page.keyboard.press('ArrowLeft');assert page.evaluate('document.activeElement.id')=='execNavTrigger'
        page.keyboard.press('ArrowRight')
        keys=items.evaluate_all('els=>els.map(e=>e.dataset.navChild)')
        seen=[]
        for _ in keys:
            seen.append(page.evaluate('document.activeElement.dataset.navChild'));page.keyboard.press('Tab')
        assert seen==keys,(seen,keys)
        # Leave the full overlay, rather than merely moving from N2 to another N1.
        for _ in range(18):
            if page.evaluate("!document.getElementById('appSidebar').contains(document.activeElement)"):break
            page.keyboard.press('Tab')
        assert page.evaluate("!document.getElementById('appSidebar').contains(document.activeElement)")
        focused=page.evaluate('document.activeElement.id');page.wait_for_timeout(350)
        assert page.get_attribute('html','data-sidebar-overlay')!='true'
        assert page.evaluate('document.activeElement.id')==focused, 'Tab departure stole focus'
        assert_untouched(page,before)
        page.locator('#researchNavTrigger').focus();page.keyboard.press('ArrowDown')
        assert page.evaluate('document.activeElement.id')=='execNavTrigger'
        page.keyboard.press('ArrowUp');assert page.evaluate('document.activeElement.id')=='researchNavTrigger'
        clean(observed);evidence['keyboard']='PASS: N1 arrows, Right/Left, Home/End, all visible N2 Tab stops and overlay departure without focus capture'
    finally:finish_context(context)


def run_drafts(browser,url,evidence,capture,artifacts):
    """Actual unchanged domain guards, with synthetic unsaved UI inputs."""
    context,page,observed=boot(browser,url,'sidebar')
    try:
        page.evaluate(BOARD_SEED);settle(page);prepare_drafts(page)
        set_field(page,'id','SIDEBAR-DRAFT')
        assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()'), 'fixture did not create a real draft'
        instrument(page);before=snapshot(page)
        page.locator('#toolsNavTrigger').hover();page.wait_for_timeout(450);expect_group(page,'tools')
        assert_untouched(page,before)
        page.locator('#toolsNavTrigger').click()
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
        page.locator('#ebLeaveStay').wait_for(state='visible')
        assert snapshot(page)==before and page.locator('#ebLeaveStay').evaluate('e=>e===document.activeElement')
        assert page.evaluate('__shCalls.filter(n=>n===\'navigateToScreen\').length')==1
        page.locator('#ebLeaveStay').click();settle(page);expect_group(page,'tools')
        assert field(page,'id').input_value()=='SIDEBAR-DRAFT'
        assert snapshot(page)==before and page.evaluate('__nlOps')==[]
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
        page.locator('#ebLeaveDiscard').click();settle(page)
        assert page.evaluate('JPWNavigation.current().canonical')=='tools-calendar'
        assert not page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
        assert raw(page)==before['storage'] and page.evaluate('JSON.stringify(S)')==before['state']

        # Existing validated table fixture supplies a complete new row. Saving
        # here is explicit and isolated; no financial expectation is weakened.
        go(page,'forex-operation')
        values=dict(id='SIDEBAR-SAVED',brokerHash=HASH,par='EURUSD',tipo='BUY',role='GENESIS',
                    lote='0.2',entry='1.2',sl='1.17',tp='1.26',status='Aberta',costs='0',
                    costBasis='SEPARATE_FROM_RESULT',stopValidated=True)
        for key,value in values.items():set_field(page,key,value)
        assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
        saved_before=raw(page);unrelated=page.evaluate('JSON.stringify(S.personalFinance)')
        page.evaluate('__shCalls=[];__nlOps=[]')
        page.locator('#toolsNavTrigger').click();expect_group(page,'tools')
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
        page.locator('#ebLeaveSave').click();settle(page)
        assert page.evaluate('JPWNavigation.current().canonical')=='tools-calendar'
        assert not page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
        assert order(page)['id']=='SIDEBAR-SAVED' and order(page)['brokerHash']==HASH
        assert raw(page)!=saved_before and page.evaluate('JSON.stringify(S.personalFinance)')==unrelated
        assert page.evaluate('__shCalls.filter(n=>n===\'navigateToScreen\').length')==1
        for key in ['jpw_nav','jpw_rail','jpw_nav_layout']:
            assert raw(page)[key]==saved_before[key]
        clean(observed)
    finally:finish_context(context)
    context,page,observed=boot(browser,url,'sidebar',rail='collapsed')
    try:
        page.evaluate(BOARD_SEED);settle(page);prepare_drafts(page)
        set_field(page,'id','SIDEBAR-COLLAPSED-DRAFT')
        assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
        instrument(page);before=snapshot(page)
        page.locator('#toolsNavTrigger').click();expect_group(page,'tools')
        assert page.get_attribute('html','data-sidebar-overlay')=='true'
        assert_untouched(page,before)
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
        page.locator('#ebLeaveStay').wait_for(state='visible')
        page.wait_for_timeout(500)
        assert page.get_attribute('html','data-sidebar-overlay')!='true'
        assert snapshot(page)==before and page.evaluate('__nlOps')==[]
        page.locator('#ebLeaveStay').click();settle(page);expect_group(page,'tools')
        assert page.get_attribute('html','data-sidebar-overlay')=='true', 'guard refusal discarded collapsed exploration'
        assert snapshot(page)==before and field(page,'id').input_value()=='SIDEBAR-COLLAPSED-DRAFT'
        assert page.evaluate('__shCalls.filter(n=>n===\'navigateToScreen\').length')==1
        assert page.evaluate('__nlOps')==[]
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
        page.locator('#ebLeaveStay').wait_for(state='visible')
        page.keyboard.press('Escape');settle(page);expect_group(page,'tools')
        assert not page.locator('#modalOverlay').evaluate('e=>e.classList.contains("show")')
        assert page.get_attribute('html','data-sidebar-overlay')=='true', 'modal Escape discarded collapsed exploration'
        assert snapshot(page)==before and field(page,'id').input_value()=='SIDEBAR-COLLAPSED-DRAFT'
        assert page.evaluate('__shCalls.filter(n=>n===\'navigateToScreen\').length')==2
        assert page.evaluate('__nlOps')==[]
        clean(observed)
        if capture:page.screenshot(path=str(artifacts/'collapsed-guard-refusal.png'))
    finally:finish_context(context)
    context,page,observed=boot(browser,url,'sidebar')
    try:
        page.evaluate(ACCOUNTS_SEED);settle(page)
        reason=page.locator('#fxAccountFacts [name="reason"]')
        reason.evaluate("e=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}")
        reason.fill('Synthetic unsaved account observation')
        assert page.evaluate('JPWForex.accountsUI.hasDrafts()'), 'fixture did not create an account draft'
        instrument(page);before=snapshot(page)
        page.locator('#toolsNavTrigger').hover();page.wait_for_timeout(450);expect_group(page,'tools')
        assert_untouched(page,before)
        page.locator('#toolsNavTrigger').click()
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
        page.locator('#fxAccountsStay').wait_for(state='visible')
        assert snapshot(page)==before
        page.locator('#fxAccountsStay').click();settle(page);expect_group(page,'tools')
        assert reason.input_value()=='Synthetic unsaved account observation' and snapshot(page)==before
        page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
        page.locator('#fxAccountsDiscard').click();settle(page)
        assert page.evaluate('JPWNavigation.current().canonical')=='tools-calendar'
        assert raw(page)==before['storage'] and page.evaluate('JSON.stringify(S)')==before['state']
        clean(observed)
        evidence['drafts']='PASS: actual Board stay/discard/save, collapsed Board refusal retains exploration, Accounts stay/discard; drafts and modal focus preserved'
    finally:finish_context(context)


def run_overlay(browser,url,evidence,capture,artifacts):
    rows=[]
    for style in ['classic','pill','kinetic']:
        context,page,observed=boot(browser,url,'sidebar',style=style,rail='collapsed')
        try:
            page.wait_for_timeout(400)
            page.locator('#brandHomeBtn').focus();instrument(page);before=snapshot(page)
            geometry=page.locator('#appMain').bounding_box();width=page.locator('#appSidebar').bounding_box()['width']
            assert abs(width-76)<=1,width
            rail=page.locator('#railToggle')
            assert rail.is_visible(), 'explicit rail control inaccessible while collapsed'
            rail_box=rail.bounding_box()
            assert rail_box['width']>=44 and rail_box['height']>=44,rail_box
            page.locator('#toolsNavTrigger').hover();page.wait_for_timeout(450);expect_group(page,'tools')
            page.wait_for_timeout(220)
            assert page.get_attribute('html','data-sidebar-overlay')=='true'
            expanded=page.locator('#appSidebar').bounding_box()['width'];assert abs(expanded-252)<=1,expanded
            assert page.locator('#appMain').bounding_box()==geometry,'temporary overlay reflowed content'
            assert page.get_attribute('html','data-rail')=='collapsed'
            indicator=page.locator('#navPillIndicator')
            if indicator.is_visible():
                pill=indicator.bounding_box();active=page.locator('#nav > .tab.active').bounding_box()
                assert abs(pill['y']-active['y'])<=2,(style,pill,active,'hover moved selection')
            assert_untouched(page,before,'brandHomeBtn')
            page.mouse.move(900,700);page.wait_for_timeout(550)
            assert page.get_attribute('html','data-sidebar-overlay')!='true'
            assert abs(page.locator('#appSidebar').bounding_box()['width']-76)<=1
            assert page.locator('#appMain').bounding_box()==geometry
            assert_untouched(page,before,'brandHomeBtn')
            saved=raw(page);page.evaluate('__nlOps=[]')
            rail.click();page.wait_for_timeout(220)
            assert page.get_attribute('html','data-rail')=='expanded'
            assert raw(page)['jpw_rail']=='expanded'
            assert {k:v for k,v in raw(page).items() if k!='jpw_rail'}=={k:v for k,v in saved.items() if k!='jpw_rail'}
            assert page.evaluate("__nlOps.length===1&&__nlOps.every(e=>e[0]==='set'&&e[1]==='jpw_rail')"),page.evaluate('__nlOps')
            rail.click();page.wait_for_timeout(220)
            assert page.get_attribute('html','data-rail')=='collapsed'
            assert raw(page)['jpw_rail']=='collapsed'
            assert page.evaluate("__nlOps.length===2&&__nlOps.every(e=>e[0]==='set'&&e[1]==='jpw_rail')"),page.evaluate('__nlOps')
            if capture:page.screenshot(path=str(artifacts/('collapsed-'+style+'.png')))
            saved=raw(page);page.reload(wait_until='load');ready(page)
            assert raw(page)==saved and page.evaluate('__nlOps')==[]
            assert page.get_attribute('html','data-nav-style')==style
            clean(observed);rows.append({'style':style,'result':'PASS'})
        finally:finish_context(context)
    evidence['overlay']=rows
    for key in ['research','exec','finpes','tools']:
        context,page,observed=boot(browser,url,'sidebar',rail='collapsed')
        try:
            instrument(page);before=snapshot(page)
            # First physical click, with no dwell or forced dispatch. Opening
            # on focus must not move the intended button away before pointerup.
            page.locator('#'+key+'NavTrigger').click();assert_untouched(page,before);expect_group(page,key)
            assert page.get_attribute('html','data-sidebar-overlay')=='true'
            page.mouse.move(900,700);page.wait_for_timeout(450);expect_group(page,key)
            page.locator('#appMain').click(position={'x':300,'y':120});page.wait_for_timeout(220)
            assert page.get_attribute('html','data-sidebar-overlay')!='true'
            assert_untouched(page,before);clean(observed)
        finally:finish_context(context)
    evidence['first_collapsed_click']='PASS: four real first clicks open/pin correct parent; overlay outside click closes without navigation'


def run_modals(browser,url,evidence,capture,artifacts):
    context,page,observed=boot(browser,url,'sidebar',rail='collapsed',alladin_active=True)
    try:
        saved=raw(page);go(page,'forex-management-accounts')
        page.evaluate("window.__shRail=document.getElementById('railToggle')")
        page.locator('#toolsNavTrigger').hover();page.wait_for_timeout(100)
        page.locator('#headerConfigBtn').click();page.locator('#settingsModal').wait_for(state='visible')
        page.wait_for_timeout(450)
        assert page.get_attribute('html','data-sidebar-overlay')!='true','pending hover survived Settings'
        assert page.locator('#railToggle').evaluate("e=>e===__shRail&&e.parentElement.id==='settingsRailSlot'")
        for layout in ['topbar','glass','submenu','sidebar']:
            page.evaluate("() => activateSettingsCategory('editor')")
            page.locator('#navLayoutSeg [data-nav-layout="'+layout+'"]').click();settle(page)
            assert page.locator('#railToggle').evaluate("e=>e===__shRail&&e.parentElement.id==='settingsRailSlot'")
            assert page.locator('#settingsModal').evaluate("e=>!e.closest('[inert],[hidden]')")
        page.locator('#settingsCloseBtn').click();settle(page)
        assert page.locator('#railToggle').evaluate("e=>e===__shRail&&e.parentElement.classList.contains('sidebar-heading')")
        # Only the explicit layout actions above may change their preference.
        assert {k:v for k,v in raw(page).items() if k!='jpw_nav_layout'}=={k:v for k,v in saved.items() if k!='jpw_nav_layout'}
        page.locator('#toolsNavTrigger').hover();page.wait_for_timeout(100)
        page.evaluate("openSettingsModal('interface')");page.locator('#mvpNotesOpenFromSettingsBtn').click();page.locator('#mvpNotesDrawer').wait_for(state='visible')
        page.wait_for_timeout(450)
        assert page.get_attribute('html','data-sidebar-overlay')!='true','pending hover survived Notes'
        assert page.locator('#nav').evaluate('e=>e.inert')
        page.locator('#mvpNotesCloseBtn').click();settle(page)
        assert page.locator('#mvpNotesOpenFromSettingsBtn').evaluate('e=>e===document.activeElement')
        page.locator('#settingsCloseBtn').click();settle(page)
        assert not page.locator('#nav').evaluate('e=>e.inert')
        page.locator('#brandHomeBtn').focus();page.locator('#toolsNavTrigger').hover();page.wait_for_timeout(100)
        modal_before=snapshot(page)
        page.evaluate('openEconomicCalendar(document.getElementById("brandHomeBtn"))')
        page.locator('#ecalOverlay').wait_for(state='visible');page.wait_for_timeout(450)
        assert page.get_attribute('html','data-sidebar-overlay')!='true'
        assert page.locator('#navSubShell').evaluate('e=>e.inert&&e.hidden'), 'calendar did not suspend N2'
        assert page.locator('#ecalOverlay').evaluate('e=>e.contains(document.activeElement)')
        assert snapshot(page)==modal_before
        page.evaluate('closeEconomicCalendar()');settle(page)
        assert page.evaluate('document.activeElement.id')=='brandHomeBtn'
        assert not page.locator('#nav').evaluate('e=>e.inert')
        go(page,'alladin')
        page.locator('#alladinTabs [data-alladin-view="instruments"]').click();settle(page)
        page.locator('#toolsNavTrigger').hover();page.wait_for_timeout(100)
        modal_before=snapshot(page)
        page.locator('#alladin button[data-ald-new="instrument"]').click()
        page.locator('#alladinModalOverlay').wait_for(state='visible');page.wait_for_timeout(450)
        assert page.get_attribute('html','data-sidebar-overlay')!='true'
        assert page.locator('#navSubShell').evaluate('e=>e.inert&&e.hidden'), 'Alladin dialog did not suspend N2'
        assert page.locator('#alladinModalOverlay').evaluate('e=>e.contains(document.activeElement)')
        assert snapshot(page)==modal_before
        page.locator('#alladinModalBox [data-ald-act="cancelar"]').click();settle(page)
        assert page.evaluate('document.activeElement.dataset.aldNew')=='instrument'
        assert not page.locator('#nav').evaluate('e=>e.inert')
        assert snapshot(page)==modal_before
        clean(observed);evidence['modals']='PASS: pending hover cancelled, Settings retains one borrowed rail through four layouts; Notes, Economic Calendar and synthetic opt-in Alladin preserve focus/state'
    finally:finish_context(context)


def run_geometry(browser,url,evidence,capture,artifacts):
    rows=[]
    for width in [320,390,900,1024,1440]:
        for theme in ['light','dark']:
            context,page,observed=boot(browser,url,'sidebar',width=width)
            try:
                page.evaluate('t=>document.documentElement.dataset.theme=t',theme)
                if width<=900:page.locator('[data-shell-menu-toggle]').click()
                before=page.evaluate('JPWNavigation.current()')
                page.locator('#execNavTrigger').click();expect_group(page,'exec');page.wait_for_timeout(220)
                assert page.evaluate('JPWNavigation.current()')==before,'touch parent navigated'
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,theme,'overflow')
                targets=page.locator('#execNavSubmenu .nav-sub-level-primary button').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect();return {w:r.width,h:r.height}})')
                assert len(targets)==7 and all(t['w']>=44 and t['h']>=44 for t in targets),(width,theme,targets)
                if width<=900:
                    assert page.get_attribute('html','data-shell-menu')=='open'
                    assert page.locator('#appSidebar').get_attribute('aria-modal')=='true'
                    assert page.locator('#appMain').evaluate('e=>e.inert')
                    assert page.get_attribute('html','data-sidebar-overlay')!='true'
                    page.locator('#execNavSubmenu [data-nav-child="forex-reserves"]').click();settle(page)
                    assert page.get_attribute('html','data-shell-menu')!='open'
                    assert page.evaluate("document.getElementById('fxreserves').contains(document.activeElement)")
                    assert not page.locator('#appMain').evaluate('e=>e.inert')
                if capture:page.screenshot(path=str(artifacts/(f'sidebar-{width}-{theme}.png')))
                if width==1440:
                    page.evaluate("document.documentElement.style.zoom='2'");page.wait_for_timeout(220)
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(theme,'200% overflow')
                    if capture:page.screenshot(path=str(artifacts/('sidebar-zoom200-'+theme+'.png')))
                    page.evaluate("document.documentElement.style.zoom=''")
                    page.emulate_media(reduced_motion='reduce')
                    assert page.locator('#appSidebar').evaluate("e=>getComputedStyle(e).transitionDuration.split(',').every(v=>parseFloat(v)===0)")
                clean(observed);rows.append({'width':width,'theme':theme,'result':'PASS'})
            finally:finish_context(context)
    evidence['geometry']=rows


RUNS={'timing':run_timing,'clicks':run_clicks,'guard':run_guard,'drafts':run_drafts,'keyboard':run_keyboard,
      'overlay':run_overlay,'modals':run_modals,'geometry':run_geometry}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--artifacts',type=Path,default=DEFAULT_ARTIFACTS)
    parser.add_argument('--capture',action='store_true')
    parser.add_argument('--only',choices=list(RUNS))
    parser.add_argument('--target',choices=['source','portable','both'],default='source')
    args=parser.parse_args();args.artifacts.mkdir(parents=True,exist_ok=True)
    paths=SOURCES+([PORTABLE] if args.target!='source' else [])
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    evidence={'result':'RUNNING','started_at_epoch':time.time(),'source_sha256':hashes,
              'scope':'synthetic sidebar UX only','target':args.target,'checks':[]}
    report=args.artifacts/'sidebar-results.json';report.write_text(json.dumps(evidence,indent=2))
    server,url=serve(ROOT)
    try:
        with sync_playwright() as pw:
            browser=launch_browser(pw);evidence['browser']=browser.version
            try:
                targets={'source':url,'portable':url.rsplit('/',1)[0]+'/'+PORTABLE}
                for target,target_url in targets.items():
                    if args.target not in [target,'both']:continue
                    folder=args.artifacts/target;folder.mkdir(exist_ok=True)
                    details={};evidence[target]=details
                    for name,run in RUNS.items():
                        if args.only and name!=args.only:continue
                        try:
                            run(browser,target_url,details,args.capture,folder)
                            item={'target':target,'check':name,'result':'PASS'}
                        except Exception as exc:
                            item={'target':target,'check':name,
                                  'result':'PRODUCT_FAIL' if isinstance(exc,(AssertionError,PlaywrightTimeout)) else 'TEST_HARNESS_FAIL',
                                  'error':str(exc),'traceback':traceback.format_exc()}
                        evidence['checks'].append(item);print(item['result'],target,name,item.get('error',''),flush=True)
                        report.write_text(json.dumps(evidence,indent=2,ensure_ascii=False))
            finally:browser.close()
    finally:
        server.shutdown();evidence['finished_at_epoch']=time.time()
        evidence['source_changed_during_run']=[p for p,h in hashes.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
        evidence['result']='PASS' if evidence['checks'] and all(c['result']=='PASS' for c in evidence['checks']) and not evidence['source_changed_during_run'] else 'PRODUCT_FAIL'
        report.write_text(json.dumps(evidence,indent=2,ensure_ascii=False))
    assert evidence['result']=='PASS',str(report)


if __name__=='__main__':main()
