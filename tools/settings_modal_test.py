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

    # A-003: isolamento acessível usa os alvos REAIS (header, #appMain, #nav, .foot-note)
    # — os seletores antigos .topbar/#main não existiam e deixavam cabeçalho e conteúdo
    # operacional expostos. O modal em si nunca é inertizado; o foco não alcança o fundo.
    inert_on=page.evaluate("""()=>({
      header:document.querySelector('header').inert,
      appMain:document.querySelector('#appMain').inert,
      nav:document.querySelector('#nav').inert,
      foot:document.querySelector('.foot-note').inert,
      modal:document.getElementById('settingsModal').inert,
      ariaHeader:document.querySelector('header').getAttribute('aria-hidden')})""")
    assert inert_on=={'header':True,'appMain':True,'nav':True,'foot':True,'modal':False,'ariaHeader':'true'}, inert_on
    page.evaluate("document.getElementById('headerConfigBtn').focus()")
    assert page.evaluate("document.activeElement.id")!='headerConfigBtn', 'foco não pode alcançar o fundo inertizado'

    # Abertura padrão em Geral, com as seis categorias principais na sidebar e apenas uma página ativa.
    assert page.locator('#settingsPageTitle').inner_text()=='Geral'
    assert page.locator('[data-settings-panel="general"]').is_visible()
    assert page.locator('[data-settings-panel]:not([hidden])').count()==1
    top_categories=['general','appearance-interface','method-governance','knowledge','data-security','about']
    assert page.locator('#settingsMenu [data-settings-category]').count()==len(top_categories)
    for cat in top_categories:
      assert page.locator(f'#settingsMenu [data-settings-category="{cat}"]').count()==1

    # Aparência e Interface -> Aparência, Interface, Editor (subpáginas, não mais itens diretos da sidebar).
    page.locator('#settingsMenu [data-settings-category="appearance-interface"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Aparência e Interface'
    page.locator('[data-settings-panel="appearance-interface"] [data-nav-to="appearance"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Aparência'
    assert page.locator('#themeSeg').is_visible()
    assert page.locator('[data-settings-panel]:not([hidden])').count()==1
    page.locator('#settingsBackBtn').click()
    page.locator('[data-settings-panel="appearance-interface"] [data-nav-to="interface"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Interface'
    assert page.locator('#fsSeg').is_visible()
    page.locator('#settingsBackBtn').click()
    page.locator('[data-settings-panel="appearance-interface"] [data-nav-to="editor"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Editor'
    assert page.locator('[data-settings-panel="editor"]').is_visible()

    # Método e Governança -> Estatuto Operacional, Parâmetros e Calibração.
    page.locator('#settingsBackBtn').click(); page.locator('#settingsBackBtn').click()
    page.locator('#settingsMenu [data-settings-category="method-governance"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Método e Governança'
    page.locator('[data-settings-panel="method-governance"] [data-nav-to="statute"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Estatuto Operacional'
    assert page.locator('[data-settings-panel="statute"] .mc-disclosure').is_visible()
    page.locator('#settingsBackBtn').click()
    page.locator('[data-settings-panel="method-governance"] [data-nav-to="parameters"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Parâmetros e Calibração'
    assert page.locator('#pMDD').is_visible()
    assert page.locator('#settingsReviewPeriodBtn').is_visible()

    # Conhecimento -> Centro Educacional (rótulo novo; ID interno 'educational' preservado).
    page.locator('#settingsBackBtn').click(); page.locator('#settingsBackBtn').click()
    page.locator('#settingsMenu [data-settings-category="knowledge"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Conhecimento'
    page.locator('[data-settings-panel="knowledge"] [data-nav-to="educational"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Centro Educacional'
    assert page.locator('[data-settings-panel="educational"] .education-glossary').is_visible()

    # Dados e Segurança -> Backup e Recuperação, Armazenamento Local.
    page.locator('#settingsBackBtn').click(); page.locator('#settingsBackBtn').click()
    page.locator('#settingsMenu [data-settings-category="data-security"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Dados e Segurança'
    page.locator('[data-settings-panel="data-security"] [data-nav-to="backup"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Backup e Recuperação'
    assert page.locator('#exportFullBackupBtn').is_visible()
    assert page.locator('#importFullBackupBtn').is_visible()
    page.locator('#settingsBackBtn').click()
    page.locator('[data-settings-panel="data-security"] [data-nav-to="storage"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Armazenamento Local'
    assert page.locator('[data-settings-panel="storage"] .settings-facts').is_visible()

    # Sobre, categoria independente, com a versão visual vigente.
    page.locator('#settingsBackBtn').click(); page.locator('#settingsBackBtn').click()
    page.locator('#settingsMenu [data-settings-category="about"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Sobre'
    assert '1 beta' in page.locator('[data-settings-panel="about"]').inner_text()

    # Voltar e avançar dentro da pilha de navegação interna (não mexe na URL nem no histórico do navegador).
    page.locator('#settingsMenu [data-settings-category="appearance-interface"]').click()
    page.locator('[data-settings-panel="appearance-interface"] [data-nav-to="appearance"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Aparência'
    page.locator('#settingsBackBtn').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Aparência e Interface'
    page.locator('#settingsForwardBtn').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Aparência'

    assert page.evaluate('sessionStateFingerprint()')==before
    assert page.evaluate("sessionStorage.getItem('jpwealth_session_checkpoint_v1')")==checkpoint

    # Pesquisa: caminho hierárquico e abertura direta do resultado; MDD abre Parâmetros e Calibração.
    page.locator('#settingsSearch').fill('pip'); assert 'pip' in page.locator('#settingsSearchResults').inner_text().lower()
    page.locator('#settingsSearch').fill('MDD')
    assert 'MDD' in page.locator('#settingsSearchResults').inner_text()
    assert 'Método e Governança' in page.locator('#settingsSearchResults').inner_text()
    page.locator('#settingsSearchResults [data-settings-result]').first.click()
    assert page.locator('#settingsPageTitle').inner_text()=='Parâmetros e Calibração'
    page.locator('#settingsSearch').fill('backup'); assert 'backup' in page.locator('#settingsSearchResults').inner_text().lower()
    page.locator('#settingsSearch').fill('Nome Privado'); assert 'Nenhuma' in page.locator('#settingsSearchResults').inner_text()

    # Esc dentro da busca limpa o campo sem fechar a Central; Esc fora da busca fecha (fechamento global preservado).
    page.locator('#settingsSearch').press('Escape')
    assert page.locator('#settingsOverlay').is_visible()
    assert page.locator('#settingsSearch').input_value()==''
    page.locator('#settingsContent').focus()
    page.keyboard.press('Escape')
    assert not page.locator('#settingsOverlay').is_visible()
    page.locator('#headerConfigBtn').click()

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
    for width,height in [(1280,800),(1024,768),(760,900),(600,900),(400,844)]:
      page.set_viewport_size({'width':width,'height':height}); assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')

    # Mobile (<=760px): abre na lista de categorias em tela cheia; ao entrar numa categoria,
    # o conteúdo ocupa a tela inteira e o botão Voltar devolve à lista (não à página 'general').
    page.locator('#settingsCloseBtn').click()
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#headerConfigBtn').click()
    modal=page.locator('#settingsModal')
    assert page.locator('.settings-sidebar').is_visible()
    assert not page.locator('#settingsContent').is_visible()
    page.locator('#settingsMenu [data-settings-category="data-security"]').click()
    assert modal.evaluate('el=>el.classList.contains("settings-mobile-detail")') is True
    assert page.locator('#settingsContent').is_visible()
    assert not page.locator('.settings-sidebar').is_visible()
    page.locator('#settingsBackBtn').click()
    assert modal.evaluate('el=>el.classList.contains("settings-mobile-detail")') is False
    assert page.locator('.settings-sidebar').is_visible()
    assert not page.locator('#settingsContent').is_visible()
    page.set_viewport_size({'width':1440,'height':900})

    page.locator('#settingsCloseBtn').click(); assert page.evaluate('sessionHasChanges()') is False
    assert page.evaluate('sessionStateFingerprint()')==before

    # A-003: após fechar (inclusive depois dos 20 ciclos abre/fecha acima), o estado
    # anterior de inert/aria-hidden é restaurado exatamente — sem resíduo acumulado.
    inert_off=page.evaluate("""()=>({
      header:document.querySelector('header').inert,
      appMain:document.querySelector('#appMain').inert,
      nav:document.querySelector('#nav').inert,
      foot:document.querySelector('.foot-note').inert,
      ariaHeader:document.querySelector('header').getAttribute('aria-hidden'),
      snapshotLimpo:settingsInertSnapshot===null})""")
    assert inert_off=={'header':False,'appMain':False,'nav':False,'foot':False,'ariaHeader':None,'snapshotLimpo':True}, inert_off
    # o drawer de Notas continua isolando corretamente depois de tudo
    page.locator('#headerNotesBtn').click()
    assert page.evaluate("document.querySelector('header').inert") is True
    assert page.evaluate("document.querySelector('#appMain').inert") is True
    page.locator('#mvpNotesCloseBtn').click()
    assert page.evaluate("document.querySelector('header').inert") is False
    assert page.evaluate("document.querySelector('#appMain').inert") is False

    assert_no_errors(observed); browser.close()
finally:
  server.shutdown();server.server_close()
print('SETTINGS MODAL OK — abertura, navegação, busca declarativa, subdiálogos, foco, responsividade e invariância de estado verificados.')
