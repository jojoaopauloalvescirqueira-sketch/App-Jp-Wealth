#!/usr/bin/env python3
"""Nocuda UI boundaries: synthetic data only; HTTP, file, portable and PWA."""
from pathlib import Path
import base64
import hashlib
import json
import os
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap

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
    browser=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True,args=['--no-sandbox'])
    targets=[('http',url),('file',(ROOT/'index.html').as_uri()),('portable',(ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').as_uri())]
    for mode,target in targets:
        context,page,errors=boot(browser,target)
        baseline=state(page)
        check(mode+' routes',page.evaluate("JPWNavigation.navigate('tools-nocuda')"))
        check(mode+' children',page.evaluate("JPWNavigation.children('tools').map(x=>x.id)")==['tools-calendar','tools-nocuda'])
        page.click('#nocudaExample');wire=page.locator('#nocudaCanonical').input_value()
        check(mode+' preview49',page.locator('#nocudaPreview line').count()==49)
        check(mode+' anchors3',page.locator('#nocudaAnchors tr').count()==3)
        with page.expect_download() as dl:page.click('#nocudaSave')
        data=Path(dl.value.path()).read_bytes()
        check(mode+' txt exact',data==wire.encode())
        page.set_input_files('#nocudaFile',{'name':'Nocuda.txt','mimeType':'text/plain','buffer':data})
        page.wait_for_function("document.getElementById('nocudaStatus').textContent.startsWith('Código válido')")
        check(mode+' ownfile valid',page.locator('#nocudaCanonical').input_value()==wire)
        page.fill('#nocudaPayload',wire+'|unknown=<img src=x onerror=alert(1)>');page.click('#nocudaValidate')
        check(mode+' invalid preserves',page.locator('#nocudaCanonical').input_value()==wire and page.locator('#nocudaPreview line').count()==49)
        check(mode+' stale actions blocked',page.locator('#nocudaCopy').is_disabled() and page.locator('#nocudaEditable').is_disabled())
        # Os únicos elementos de imagem permitidos são os dois ícones locais
        # das plataformas. O payload inválido não pode acrescentar nenhum nó.
        expected_icons = "imgs=>imgs.length===2&&imgs.every(img=>['assets/nocuda-tradingview.png','assets/nocuda-metatrader.png'].some(path=>img.getAttribute('src')===path||img.src.endsWith('/'+path)))"
        if mode == 'portable':
            expected_icons = "imgs=>imgs.length===2&&imgs.every(img=>img.src.startsWith('data:image/png;base64,'))"
        check(mode+' no injection',page.locator('#nocudaTool img').evaluate_all(expected_icons))
        check(mode+' drawing excluded from backup drafts',page.evaluate("jpwWorkspaceDrafts().every(x=>!x.text.includes('NOCUDA|'))"))
        page.click('#nocudaRestore')
        with page.expect_download() as dl:page.click('#nocudaEditable')
        generated=Path(dl.value.path()).read_text()
        check(mode+' generated preconfigured','const bool PRECONFIGURED = true // NOCUDA_PRECONFIGURED' in generated)
        check(mode+' generated blank symbol','input.string("", "Símbolo canônico' in generated)
        check(mode+' generated source retains grid','max_lines_count = 400' in generated)
        check(mode+' generated exact A price','input.price(100.00000,' in generated)
        check(mode+' generated seed',json.dumps(wire,ensure_ascii=False) in generated)
        # Generated artifacts change defaults only; parser and geometry source unchanged.
        original=(ROOT/'downloads/nocuda/Nocuda_Tool.pine').read_text().splitlines()
        result=generated.splitlines()
        check(mode+' generated same lines',len(original)==len(result))
        check(mode+' changed only allowlisted defaults',all(a==b or 'NOCUDA_DEFAULT:' in a or 'NOCUDA_PRECONFIGURED' in a for a,b in zip(original,result)))
        for filename in ['Nocuda_Tool.pine','Nocuda_Tool.mq5','Nocuda_Tool.ex5','TRADINGVIEW-LEIA-ME.md','MT5-LEIA-ME.md']:
            with page.expect_download() as dl:page.locator('[data-nocuda-file="'+filename+'"]').click()
            check(mode+' download '+filename,Path(dl.value.path()).read_bytes()==(ROOT/'downloads/nocuda'/filename).read_bytes())
        check(mode+' calendar alias',page.evaluate("JPWNavigation.navigate('ecal')&&JPWNavigation.current().primary==='tools'"))
        check(mode+' single calendar DOM',page.locator('#tools #execEcal').count()==1 and page.locator('#research #execEcal').count()==0)
        page.locator('#execEcal [data-ecal-cur="EUR"]').click()
        check(mode+' same filter',page.locator('#execEcal [data-ecal-cur="EUR"]').get_attribute('aria-pressed')=='true')
        check(mode+' old local redirect',page.evaluate("JPWNavigation.navigateLocal('research','calendar')&&JPWNavigation.current().canonical==='tools-calendar'"))
        check(mode+' studies retained',page.evaluate("JPWNavigation.navigate('nocoda')&&JPWNavigation.current().primary==='research'&&JPWResearch.ui.getView()==='nocoda'"))
        page.evaluate("JPWNavigation.navigate('tools-nocuda')")
        page.set_input_files('#nocudaFile',{'name':'huge.txt','mimeType':'text/plain','buffer':b'x'*16385})
        check(mode+' oversized refused','16 KiB' in page.locator('#nocudaStatus').inner_text())
        page.click('#nocudaRestore')
        check(mode+' no financial/storage changes',state(page)==baseline)
        page.click('#nocudaClear');check(mode+' explicit clear',page.locator('#nocudaResult').is_hidden() and page.locator('#nocudaPayload').input_value()=='')
        check(mode+' no runtime errors',not errors)
        context.close()
    for width,height in [(1440,1000),(390,844)]:
        context,page,errors=boot(browser,url,{'width':width,'height':height})
        page.evaluate("JPWNavigation.navigate('tools-nocuda')")
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
            page.locator('#toolsNavSubmenu [data-nav-child="tools-nocuda"]').focus();page.keyboard.press('ArrowUp');page.keyboard.press('Enter')
            check('keyboard navigation',page.evaluate("JPWNavigation.current().canonical==='tools-calendar'"))
        check('responsive no runtime errors '+str(width),not errors)
        context.close()
    context,page,errors=boot(browser,url,sw='allow')
    page.evaluate('navigator.serviceWorker.ready')
    page.reload();wait_bootstrap(page)
    page.wait_for_function('navigator.serviceWorker.controller!==null')
    await_cache=page.evaluate("async()=>{const reg=await navigator.serviceWorker.ready;const keys=await caches.keys();return {active:!!reg.active,keys};}")
    check('PWA activated',await_cache['active'])
    context.set_offline(True)
    page.reload();wait_bootstrap(page)
    page.evaluate("JPWNavigation.navigate('tools-nocuda')")
    for filename in ['Nocuda_Tool.pine','Nocuda_Tool.mq5','Nocuda_Tool.ex5','TRADINGVIEW-LEIA-ME.md','MT5-LEIA-ME.md']:
        result=page.evaluate("async name=>{const r=await fetch('downloads/nocuda/'+name);return {ok:r.ok,b:Array.from(new Uint8Array(await r.arrayBuffer()))};}",filename)
        check('PWA offline '+filename,result['ok'] and bytes(result['b'])==(ROOT/'downloads/nocuda'/filename).read_bytes())
    page.click('#nocudaExample')
    check('PWA offline sourcegen',page.evaluate('!!JPWTools.generateEditable(null,JPWNocudaTransfer.example())'))
    check('PWA no runtime errors',not errors)
    context.close();browser.close()
finally:server.shutdown()
(EVIDENCE/'result.json').write_text(json.dumps({'checks':checks,'count':len(checks)},ensure_ascii=False,indent=2))
print('PASS',len(checks),'Nocuda UI checks')
