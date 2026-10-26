#!/usr/bin/env python3
"""Nocuda retirement and legacy compatibility; synthetic HTTP/file/portable/PWA."""
from pathlib import Path
import base64
import hashlib
import json
import os
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from browser_fixture_server import BrowserFixtureServer as ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from notes_launcher_test import launch_options

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=Path(os.environ.get('NOCUDA_EVIDENCE', ROOT/'tools/.artifacts/nocuda'))
EVIDENCE.mkdir(parents=True,exist_ok=True)
os.chdir(ROOT)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/index.html'
checks=[]
def check(name,test):
    assert test,name
    checks.append(name)
    print('PASS',name,flush=True)
def state(page):
    return page.evaluate('JSON.stringify({s:S,store:Object.fromEntries(Object.entries(localStorage))})')
def boot(browser,target,size=None,sw='block'):
    context=browser.new_context(viewport=size or {'width':1440,'height':1000},service_workers=sw,accept_downloads=True)
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true')
    page=context.new_page();errors=[]
    page.on('pageerror',lambda err: errors.append(str(err)))
    page.goto(target);wait_bootstrap(page)
    page.evaluate('window.__onbShown=true;closeModal();S.onboarding.done=true')
    return context,page,errors
try:
 with sync_playwright() as pw:
    browser=pw.chromium.launch(**launch_options())
    targets=[('http',url),('file',(ROOT/'index.html').as_uri()),('portable',(ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').as_uri())]
    for mode,target in targets:
        context,page,errors=boot(browser,target)
        baseline=state(page)
        # CHG-JPW-REMOVE-NOCUDA-CONTROLS: retired UI/global behavior replaces
        # the approved removed editor/source-generator/download assertions.
        check(mode+' retired submenu absent',page.locator('[data-nav-child="tools-nocuda"]').count()==0)
        check(mode+' retired panel absent',page.locator('#nocudaTool,#nocudaPayload,[data-nocuda-file]').count()==0)
        check(mode+' retired globals absent',page.evaluate("typeof JPWNocudaTransfer==='undefined'&&typeof JPWTools.generateEditable==='undefined'"))
        check(mode+' children',page.evaluate("JPWNavigation.children('tools').map(x=>x.id)")==['tools-calendar','tools-leverage','tools-normative','tools-minigames'])
        check(mode+' ordinary Stoikus entry',page.evaluate("JPWNavigation.navigate('tools-leverage')"))
        check(mode+' ordinary entry has no retirement notice',page.locator('#nocudaRetirementNotice').is_hidden())
        for local in [False,True]:
            before_refusal=state(page)
            before_route=page.evaluate('JPWNavigation.current()')
            before_notice=page.locator('#nocudaRetirementNotice').evaluate('(n)=>({hidden:n.hidden,text:n.textContent})')
            page.evaluate("()=>{const d=document.createElement('dialog');d.id='retirementRefusalDialog';d.textContent='Synthetic unsaved context';document.body.append(d);d.showModal();window.__retirementEvents=[];window.__retirementOff=JPWNavigation.subscribe(e=>__retirementEvents.push(e));}")
            check(mode+' refused alias '+str(local),not page.evaluate("local=>local?JPWNavigation.navigateLocal('tools','nocuda'):JPWNavigation.navigate('tools-nocuda')",local))
            check(mode+' refusal preserves context '+str(local),state(page)==before_refusal and page.evaluate('JPWNavigation.current()')==before_route)
            check(mode+' refusal no notice/event '+str(local),page.locator('#nocudaRetirementNotice').evaluate('(n)=>({hidden:n.hidden,text:n.textContent})')==before_notice and page.evaluate('__retirementEvents.length')==0)
            page.evaluate("__retirementOff();document.getElementById('retirementRefusalDialog').close();document.getElementById('retirementRefusalDialog').remove()")
        for local in [False,True]:
            check(mode+' legacy alias accepted '+str(local),page.evaluate("local=>local?JPWNavigation.navigateLocal('tools','nocuda'):JPWNavigation.navigate('tools-nocuda')",local))
            check(mode+' alias redirects '+str(local),page.evaluate("JPWNavigation.current().canonical==='tools-leverage'&&JPWTools.ui.getView()==='leverage'"))
            check(mode+' accepted alias retirement notice '+str(local),page.locator('#nocudaRetirementNotice').is_visible() and bool(page.locator('#nocudaRetirementNotice').inner_text().strip()))
        # A recovered legacy drawing stays readable/copyable, with no adapter.
        draft={'label':'Synthetic retired drawing','provider':'nocuda-transfer','version':1,'context':{'route':'tools-nocuda'},'baseReference':None,'text':'synthetic legacy payload <img src=x onerror=alert(1)>'}
        check(mode+' retired recovery inspect refuses',page.evaluate("item=>JPWWorkspaceDrafts.inspect(item).compatible===false",draft))
        route=page.evaluate('JPWNavigation.current()')
        check(mode+' retired recovery reopen refuses',page.evaluate("item=>JPWWorkspaceDrafts.reopen(item).ok===false",draft))
        check(mode+' recovery no state effects',state(page)==baseline and page.evaluate('JPWNavigation.current()')==route)
        page.evaluate("item=>{window.__retiredRecoveryBefore=S.workspaceRecovery;S.workspaceRecovery={drafts:[item]};jpwWorkspaceShowDrafts();}",draft)
        area=page.locator('#workspaceDraftDialog textarea')
        check(mode+' legacy recovery text exact',area.input_value()==draft['text'] and area.get_attribute('readonly') is not None)
        check(mode+' legacy recovery cannot reopen',page.locator('#workspaceDraftDialog button').filter(has_text='Conferir e reabrir campos').count()==0)
        # Selection and copy use the native readonly textarea, without executing markup.
        area.select_text()
        check(mode+' legacy recovery selectable',area.evaluate('(node)=>node.selectionStart===0&&node.selectionEnd===node.value.length'))
        check(mode+' recovery payload remains text',page.locator('#workspaceDraftDialog img').count()==0)
        page.evaluate("document.getElementById('workspaceDraftDialog').close();document.getElementById('workspaceDraftDialog').remove();if(__retiredRecoveryBefore===undefined)delete S.workspaceRecovery;else S.workspaceRecovery=__retiredRecoveryBefore;delete window.__retiredRecoveryBefore")
        check(mode+' calendar alias',page.evaluate("JPWNavigation.navigate('ecal')&&JPWNavigation.current().primary==='tools'"))
        page.wait_for_selector('#execEcal .calendar-grid [data-calendar-date]')
        check(mode+' single calendar DOM',page.locator('#tools #execEcal').count()==1 and page.locator('#research #execEcal').count()==0)
        check(mode+' monthly calendar mounted once',page.locator('#execEcal .calendar-panel').count()==1 and page.locator('#execEcal [data-calendar-date]').count()>=28)
        page.locator('#execEcal [data-calendar-action="filters"]').click()
        monthly_currencies=page.locator('#execEcal [data-calendar-filter="currencies"]')
        check(mode+' monthly own currencies',monthly_currencies.evaluate_all("nodes=>nodes.map(n=>n.value)")==['USD','GBP','JPY','NZD','CHF'])
        check(mode+' monthly default selection',monthly_currencies.evaluate_all('nodes=>nodes.every(n=>n.checked)'))
        check(mode+' monthly excludes weekly filter clones',page.locator('#execEcal [data-ecal-cur]').count()==0)
        check(mode+' old local redirect',page.evaluate("JPWNavigation.navigateLocal('research','calendar')&&JPWNavigation.current().canonical==='tools-calendar'"))
        check(mode+' calendar reentry retains single view',page.locator('#execEcal .calendar-panel').count()==1 and monthly_currencies.count()==5 and monthly_currencies.evaluate_all('nodes=>nodes.every(n=>n.checked)'))
        monthly=page.locator('#execEcal').inner_html()
        page.evaluate('JPWEcal.open()')
        page.wait_for_selector('#ecalOverlay.show')
        page.locator('#ecalFilters [data-ecal-cur="EUR"]').click()
        check(mode+' weekly EUR filter retained',page.locator('#ecalFilters [data-ecal-cur="EUR"]').get_attribute('aria-pressed')=='true')
        page.evaluate('JPWEcal.close()')
        check(mode+' weekly filter leaves monthly unchanged',page.locator('#execEcal').inner_html()==monthly)
        check(mode+' studies retained',page.evaluate("JPWNavigation.navigate('nocoda')&&JPWNavigation.current().primary==='research'&&JPWResearch.ui.getView()==='nocoda'"))
        check(mode+' no financial/storage changes',state(page)==baseline)
        check(mode+' no runtime errors',not errors)
        context.close()
    for width,height in [(1440,1000),(390,844)]:
        context,page,errors=boot(browser,url,{'width':width,'height':height})
        page.evaluate("JPWNavigation.navigate('tools-leverage')")
        for theme in ['light','dark']:
            page.evaluate("theme=>document.documentElement.setAttribute('data-theme',theme)",theme)
            page.wait_for_timeout(250)  # Settle existing theme color transitions before visual evidence.
            check(f'{width}/{theme} no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            page.screenshot(path=str(EVIDENCE/f'nocuda-{width}-{theme}.png'),full_page=True)
        if width==390:
            page.locator('[data-shell-menu-toggle]').click()
            page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').click()
            check('mobile navigation',page.evaluate("JPWNavigation.current().canonical==='tools-calendar'") and page.locator('#sidebarBackdrop').is_hidden())
        else:
            page.locator('#toolsNavSubmenu [data-nav-child="tools-leverage"]').focus();page.keyboard.press('ArrowUp')
            check('keyboard calendar focus',page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').evaluate('(node)=>node===document.activeElement'))
            page.keyboard.press('ArrowDown')
            check('keyboard Stoikus return focus',page.locator('#toolsNavSubmenu [data-nav-child="tools-leverage"]').evaluate('(node)=>node===document.activeElement'))
            page.keyboard.press('ArrowUp')
            check('keyboard calendar return focus',page.locator('#toolsNavSubmenu [data-nav-child="tools-calendar"]').evaluate('(node)=>node===document.activeElement'))
            page.keyboard.press('Enter')
            check('keyboard navigation',page.evaluate("JPWNavigation.current().canonical==='tools-calendar'"))
        check('responsive no runtime errors '+str(width),not errors)
        context.close()
    context,page,errors=boot(browser,url,sw='allow')
    page.wait_for_function('async()=>!!(await navigator.serviceWorker.getRegistration())?.active',timeout=20000)
    page.reload();wait_bootstrap(page)
    page.wait_for_function('navigator.serviceWorker.controller!==null')
    await_cache=page.evaluate("async()=>{const reg=await navigator.serviceWorker.ready;const keys=await caches.keys();return {active:!!reg.active,keys};}")
    check('PWA activated',await_cache['active'])
    context.set_offline(True)
    page.reload();wait_bootstrap(page)
    page.evaluate("JPWNavigation.navigate('tools-leverage')")
    check('PWA offline retired globals absent',page.evaluate("typeof JPWNocudaTransfer==='undefined'&&typeof JPWTools.generateEditable==='undefined'"))
    check('PWA offline retired UI absent',page.locator('#nocudaTool,[data-nocuda-file],[data-nav-child="tools-nocuda"]').count()==0)
    check('PWA offline alias redirects',page.evaluate("JPWNavigation.navigate('tools-nocuda')&&JPWNavigation.current().canonical==='tools-leverage'"))
    check('PWA no runtime errors',not errors)
    context.close();browser.close()
finally:server.shutdown()
(EVIDENCE/'result.json').write_text(json.dumps({'checks':checks,'count':len(checks)},ensure_ascii=False,indent=2))
print('PASS',len(checks),'Nocuda retirement checks')
