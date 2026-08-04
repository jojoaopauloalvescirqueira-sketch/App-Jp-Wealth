#!/usr/bin/env python3
"""Caracterização da Central de Configurações sem alterar dados operacionais."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, socket, threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass
def serve():
    with socket.socket() as s: s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    server=ThreadingHTTPServer(('127.0.0.1',port),Quiet); threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,f'http://127.0.0.1:{port}/index.html'
def assert_no_errors(observed):
    errors=[x for x in observed['console'] if x[0]=='error']
    assert not errors and not observed['pageerror'], {'console':errors,'pageerror':observed['pageerror'],'failed':observed['failed']}

server,url=serve()
try:
  with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':900})
    observed={'console':[],'pageerror':[],'failed':[]}
    page.on('console',lambda m:observed['console'].append((m.type,m.text)))
    page.on('pageerror',lambda e:observed['pageerror'].append(str(e)))
    page.on('requestfailed',lambda r:observed['failed'].append((r.url,r.failure)))
    page.route('**/api.frankfurter.dev/**',lambda route:route.fulfill(status=200,content_type='application/json',body='{"rate":1}'))
    page.goto(url,wait_until='load'); page.wait_for_timeout(700)
    page.evaluate("""()=>{window.__onbShown=true;closeModal();window.alert=()=>{};window.confirm=()=>false;window.prompt=()=>null;
      S.onboarding={...S.onboarding,done:true,operador:'Nome Privado',supervisor:'Pessoa Privada'};save();markSessionCheckpoint();}""")
    before=page.evaluate('sessionStateFingerprint()')
    checkpoint=page.evaluate("sessionStorage.getItem('jpwealth_session_checkpoint_v1')")
    operational=page.locator('.screen.active').get_attribute('id')
    page.locator('#headerConfigBtn').click(); assert page.locator('#settingsOverlay').is_visible()
    assert page.locator('.screen.active').get_attribute('id')==operational
    assert page.get_by_role('heading',name='Configurações').count()==1
    assert page.evaluate('sessionHasChanges()') is False
    for category in ['about','appearance','interface','editor','educational','statute','parameters','backup']:
      page.locator(f'#settingsMenu [data-settings-category="{category}"]').click()
      assert page.locator(f'[data-settings-panel="{category}"]').is_visible()
    assert page.evaluate('sessionStateFingerprint()')==before
    assert page.evaluate("sessionStorage.getItem('jpwealth_session_checkpoint_v1')")==checkpoint
    page.locator('#settingsSearch').fill('pip'); assert 'pip' in page.locator('#settingsSearchResults').inner_text().lower()
    page.locator('#settingsSearch').fill('MDD'); assert 'MDD' in page.locator('#settingsSearchResults').inner_text()
    page.locator('#settingsSearch').fill('backup'); assert 'backup' in page.locator('#settingsSearchResults').inner_text().lower()
    page.locator('#settingsSearch').fill('Nome Privado'); assert 'Nenhuma' in page.locator('#settingsSearchResults').inner_text()
    page.evaluate("activateSettingsCategory('parameters')")
    page.locator('#settingsReviewPeriodBtn').click(); page.locator('#modalOverlay').wait_for(state='visible')
    assert page.locator('#settingsModal').evaluate('el=>el.inert') is True
    close=page.locator('#modalOverlay'); page.keyboard.press('Escape'); close.wait_for(state='hidden')
    assert page.locator('#settingsModal').evaluate('el=>!el.inert') is True
    page.evaluate("activateSettingsCategory('appearance')"); page.locator('#chooseAppIconBtn').scroll_into_view_if_needed(); page.locator('#chooseAppIconBtn').click(); page.locator('#modalOverlay').wait_for(state='visible')
    assert page.locator('#chooseAppIconBtn').count()==1
    assert page.locator('[data-settings-panel="appearance"] #chooseAppIconBtn').is_visible()
    assert page.locator('[data-settings-panel="interface"] #chooseAppIconBtn').count()==0
    page.keyboard.press('Escape'); page.locator('#modalOverlay').wait_for(state='hidden')
    assert page.locator('#settingsOverlay').is_visible()
    assert page.evaluate('document.activeElement.id')=='chooseAppIconBtn'
    page.locator('#settingsSearch').fill('ícone'); page.locator('#settingsSearchResults button').filter(has_text='Ícone do app').click()
    assert page.locator('[data-settings-panel="appearance"] #chooseAppIconBtn').is_visible()
    page.wait_for_function("document.querySelector('#appIconConfig')?.classList.contains('settings-search-hit')")
    page.evaluate("activateSettingsCategory('backup')"); page.locator('#wipeAllBtn').click(); assert page.locator('#settingsOverlay').is_visible()
    page.evaluate("""()=>{ for(let i=0;i<20;i++){ closeSettingsModal(); openSettingsModal(); } }""")
    debug=page.evaluate('window.__settingsModalDebug')
    assert debug['observerInstances']==1 and debug['opens']>=21, debug
    for width,height in [(1024,768),(768,900),(390,844),(320,700)]:
      page.set_viewport_size({'width':width,'height':height}); assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    page.locator('#settingsCloseBtn').click(); assert page.evaluate('sessionHasChanges()') is False
    assert page.evaluate('sessionStateFingerprint()')==before
    assert_no_errors(observed); browser.close()
finally:
  server.shutdown();server.server_close()
print('SETTINGS MODAL OK — abertura, navegação, busca declarativa, subdiálogos, foco, responsividade e invariância de estado verificados.')
