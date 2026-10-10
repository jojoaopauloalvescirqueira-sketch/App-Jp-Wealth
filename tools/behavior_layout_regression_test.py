#!/usr/bin/env python3
"""Two observed clipping regressions over actual synthetic UI paths.

Four existing navigation layouts, CSS viewport widths and light/dark. This is
headless Chromium reflow, not physical touch, native zoom or screen-reader proof.
Every measurement/navigation leaves confirmed state and browser storage intact.
"""
import argparse
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
import time
import traceback
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap,assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from design_experience_test import Quiet,SETUP
from navigation_layout_choice_test import KEY
from notes_launcher_test import launch_options
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['src/styles/app.css','src/js/40-app/09-settings-modal.js','src/js/30-accounting/01-daily-ledger.js','index.html','build-id.js']
def hashes(root):return {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCES}
def snapshot(page):return page.evaluate("JSON.stringify({S,storage:Object.entries(localStorage).sort()})")
def accounting(page):
    before=snapshot(page)
    assert page.evaluate("JPWNavigation.navigate('forex-accounting')")
    d=page.evaluate("""() => {const wrapper=document.querySelector('#contab .jp-table-scroll'),table=wrapper.querySelector('table'),raw=JPWLedger.rows();return {width:innerWidth,scroll:document.documentElement.scrollWidth,wrapper:{width:wrapper.clientWidth,scroll:wrapper.scrollWidth,overflow:getComputedStyle(wrapper).overflowX},tableWidth:table.getBoundingClientRect().width,rows:raw.map(r=>({date:r.data,result:r.resultado,balance:r.saldo})),srText:[...table.querySelectorAll('.sr-only')].map(e=>e.textContent),title:document.querySelector('#contab h1').textContent}}""")
    assert d['title']=='Contabilidade' and [r['result'] for r in d['rows']]==[123,77],d
    assert d['scroll']<=d['width']+1,{'failure':'document reflow','measurement':d}
    assert d['wrapper']['overflow']=='auto' and d['wrapper']['scroll']>=max(d['wrapper']['width'],d['tableWidth'])-1,d
    if d['tableWidth']>d['wrapper']['width']+1:
        assert d['wrapper']['scroll']>d['wrapper']['width'],d
    else:
        assert d['wrapper']['scroll']<=d['wrapper']['width']+1,d
    assert d['srText'] and all(t.strip()=='derivado' for t in d['srText']),d
    assert snapshot(page)==before,'Accounting navigation/layout wrote confirmed state or preferences'
    return d
def appearance(page):
    before=snapshot(page)
    gear=page.locator('#headerConfigBtn');menu=page.locator('[data-shell-menu-toggle]')
    if not gear.is_visible():
        assert menu.is_visible(),'The Settings opener and public menu are both hidden'
        menu.focus();page.keyboard.press('Enter');gear.wait_for(state='visible')
    gear.focus();page.keyboard.press('Enter')
    assert page.locator('#settingsModal').is_visible()
    page.evaluate("settingsNavigate('appearance',{push:true,focus:true})")
    d=page.evaluate("""() => {const c=document.getElementById('settingsContent'),r=c.getBoundingClientRect(),pieces=[...document.querySelectorAll('[data-settings-panel=appearance] .app-icon-summary>div')].map(e=>({class:e.className,text:e.innerText,x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right,width:e.clientWidth,scroll:e.scrollWidth}));return {client:c.clientWidth,scroll:c.scrollWidth,right:r.right,pieces,title:document.querySelector('[data-settings-panel=appearance] .settings-hero-title').textContent,button:{width:document.getElementById('chooseAppIconBtn').getBoundingClientRect().width,height:document.getElementById('chooseAppIconBtn').getBoundingClientRect().height}}}""")
    assert d['title']=='Aparência' and len(d['pieces'])==3,d
    assert d['scroll']<=d['client']+1 and all(x['right']<=d['right']+1 and x['scroll']<=x['width']+1 for x in d['pieces']),{'failure':'Appearance content clips brand information','measurement':d}
    assert d['button']['width']>=44 and d['button']['height']>=32,d
    assert 'Versão ativa:' in d['pieces'][2]['text'],d
    page.locator('#settingsCloseBtn').click()
    focus_target='#headerConfigBtn' if gear.is_visible() else '[data-shell-menu-toggle]'
    page.wait_for_function('(selector)=>document.activeElement===document.querySelector(selector)',arg=focus_target)
    assert page.locator(focus_target).is_visible(),'Focus returned to a hidden header control'
    d['focusTarget']=focus_target
    assert snapshot(page)==before,'Appearance layout wrote confirmed state or preferences'
    return d
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);p.add_argument('--critical',action='store_true');a=p.parse_args();root=a.root.resolve();a.out.parent.mkdir(parents=True,exist_ok=True);start=time.monotonic();report={'inputs_before':hashes(root),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':[],'limits':['CSS viewport/headless Chromium only','Physical touch, native browser zoom and assistive-technology session NOT_RUN']}
    cases=[(320,'light','sidebar',accounting),(768,'light','sidebar',appearance)] if a.critical else [(w,t,m,f) for w in [320,390,768,1440] for t in ['light','dark'] for m in ['sidebar','topbar','glass','submenu'] for f in [accounting,appearance]]
    server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch_options())
        for w,t,m,test in cases:
          row={'name':f'{test.__name__}/{w}/{t}/{m}'};c=browser.new_context(viewport={'width':w,'height':1000},service_workers='block',reduced_motion='reduce');install_bootstrap(c);c.add_init_script('window.__onbShown=true;localStorage.setItem('+json.dumps(KEY)+','+json.dumps(m)+')');page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
          try:
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page);page.evaluate(SETUP,t);row['build']=page.evaluate('JP_WEALTH_BUILD_ID');row['measurement']=test(page);assert not errors,errors;assert_fixture_requests(c);row['result']='PASS'
          except Exception as e:
            row.update(result='PRODUCT_FAIL' if isinstance(e,AssertionError) else 'TEST_HARNESS_FAIL',detail=str(e),traceback=traceback.format_exc());page.screenshot(path=str(a.out.parent/(a.out.stem+'-'+row['name'].replace('/','-')+'.png')),full_page=True)
          finally:c.close();report['cases'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        browser.close()
    finally:
      server.shutdown();server.server_close();report['inputs_after']=hashes(root);report['source_unchanged']=report['inputs_before']==report['inputs_after'];report['durationSeconds']=time.monotonic()-start;a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report['source_unchanged'] and all(r['result']=='PASS' for r in report['cases']) else 1
if __name__=='__main__':raise SystemExit(main())
