#!/usr/bin/env python3
"""Caracterização da Central de Configurações sem alterar dados operacionais."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse, base64, hashlib, json, os, struct, threading, zlib
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass
class BrowserFixtureServer(ThreadingHTTPServer):
    request_queue_size=128
    daemon_threads=True
def serve():
    server=BrowserFixtureServer(('127.0.0.1',0),Quiet); threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,f'http://127.0.0.1:{server.server_port}/index.html'
def assert_no_errors(observed):
    errors=[x for x in observed['console'] if x[0]=='error']
    assert not errors and not observed['pageerror'], {'console':errors,'pageerror':observed['pageerror'],'failed':observed['failed']}

def assert_content_landmark(page,title):
    # M-02: the application owns the sole main; a dialog's current page is a
    # named region, labelled by its existing changing heading, not another main.
    facts=page.evaluate("""()=>({
      mainIds:[...document.querySelectorAll('main')].map(el=>el.id),
      label:document.getElementById('settingsContent').getAttribute('aria-labelledby'),
      tabIndex:document.getElementById('settingsContent').tabIndex,
      hasClass:document.getElementById('settingsContent').classList.contains('settings-content'),
      inDialog:document.getElementById('settingsModal').contains(document.getElementById('settingsContent'))})""")
    print('SETTINGS LANDMARK '+json.dumps(facts,ensure_ascii=False),flush=True)
    assert facts=={'mainIds':['appMain'],'label':'settingsPageTitle','tabIndex':-1,'hasClass':True,'inDialog':True}, facts
    assert page.get_by_role('region',name=title,exact=True).get_attribute('id')=='settingsContent'

def run_existing_settings(browser,url):
    page=browser.new_page(viewport={'width':1440,'height':900}, service_workers='block')
    install_bootstrap(page.context)
    observed={'console':[],'pageerror':[],'failed':[]}
    page.on('console',lambda m:observed['console'].append((m.type,m.text)))
    page.on('pageerror',lambda e:observed['pageerror'].append(str(e)))
    page.on('requestfailed',lambda r:observed['failed'].append((r.url,r.failure)))
    page.goto(url,wait_until='load'); page.wait_for_timeout(700)
    wait_bootstrap(page)
    page.evaluate("""()=>{window.__onbShown=true;closeModal();window.alert=()=>{};window.confirm=()=>false;window.prompt=()=>null;
      S.onboarding={...S.onboarding,done:true,operador:'Nome Privado',supervisor:'Pessoa Privada'};save();markSessionCheckpoint();}""")
    before=page.evaluate('sessionStateFingerprint()')
    checkpoint=page.evaluate("sessionStorage.getItem('jpwealth_session_checkpoint_v1')")
    operational=page.locator('.screen.active').get_attribute('id')
    primary_before=page.locator('#nav > .tab.active').get_attribute('data-primary')
    page.locator('#headerConfigBtn').click(); assert page.locator('#settingsOverlay').is_visible()
    assert page.locator('.screen.active').get_attribute('id')==operational
    assert page.get_by_role('heading',name='Configurações').count()==1
    assert page.evaluate('sessionHasChanges()') is False
    assert_content_landmark(page,'Geral')

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

    # Abertura padrao em Geral, com as categorias principais na sidebar e apenas uma pagina ativa.
    assert page.locator('#settingsPageTitle').inner_text()=='Geral'
    assert page.locator('[data-settings-panel="general"]').is_visible()
    assert page.locator('[data-settings-panel]:not([hidden])').count()==1
    top_categories=['general','forex-preferences','appearance-interface','method-governance','operations','knowledge','data-security','about']
    assert page.locator('#settingsMenu [data-settings-category]').count()==len(top_categories)
    assert page.locator('#settingsModal [data-settings-category="probability-lab"], #settingsModal [data-nav-to="galton-board"], #settingsModal [data-galton-root]').count()==0
    for cat in top_categories:
      assert page.locator(f'#settingsMenu [data-settings-category="{cat}"]').count()==1

    # Aparência e Interface -> Aparência, Interface, Editor (subpáginas, não mais itens diretos da sidebar).
    page.locator('#settingsMenu [data-settings-category="appearance-interface"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Aparência e Interface'
    page.locator('[data-settings-panel="appearance-interface"] [data-nav-to="appearance"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Aparência'
    assert_content_landmark(page,'Aparência')
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

    # NAV2-I: Operacao mantém Parâmetros e a ação explícita `tool-check` dentro
    # de Settings. O mesmo grid físico é transportado, sem mudar tela/primary.
    page.locator('#settingsBackBtn').click(); page.locator('#settingsBackBtn').click()
    page.locator('#settingsMenu [data-settings-category="operations"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Operação'
    page.locator('[data-settings-panel="operations"] [data-nav-to="tool-params"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Parâmetros'
    assert page.locator('[data-settings-panel="tool-params"] #paramsWidgetGrid').is_visible()
    page.locator('#settingsBackBtn').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Operação'
    page.locator('[data-settings-panel="operations"] [data-nav-to="tool-check"]').click()
    assert page.locator('#settingsPageTitle').inner_text()=='Checklist'
    assert page.locator('#forexChecklistDialog #checkWidgetGrid').is_visible()
    check_settings=page.evaluate("""()=>({
      screen:document.querySelector('.screen.active')?.id,
      primary:document.querySelector('#nav > .tab.active')?.dataset.primary,
      grids:document.querySelectorAll('#checkWidgetGrid').length,
      parent:document.getElementById('checkWidgetGrid').closest('dialog')?.id
    })""")
    assert check_settings=={'screen':operational,'primary':primary_before,'grids':1,'parent':'forexChecklistDialog'}, check_settings

    assert page.evaluate('settingsState.suspended && document.getElementById("settingsModal").inert')
    page.locator('#forexChecklistClose').click()
    page.wait_for_function('!settingsState.suspended')

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
    # A restauração existente é assíncrona (requestAnimationFrame).
    # Esperar o foco correto sem aceitar um destino diferente ou ausente.
    expect(page.locator('#chooseAppIconBtn')).to_be_focused()
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
    geometry=page.evaluate("""()=>{
      const rect=id=>{const r=document.querySelector(id).getBoundingClientRect();return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};
      return {viewport:{width:innerWidth,height:innerHeight},overlay:rect('#settingsOverlay'),modal:rect('#settingsModal'),head:rect('#settingsModal .settings-modal-head'),body:rect('#settingsModal .settings-modal-body'),close:rect('#settingsCloseBtn')};
    }""")
    assert geometry['modal']['left']>=-1 and geometry['modal']['right']<=geometry['viewport']['width']+1, geometry
    assert geometry['modal']['top']>=-1 and geometry['modal']['bottom']<=geometry['viewport']['height']+1, geometry
    assert geometry['head']['left']>=geometry['modal']['left']-1 and geometry['head']['right']<=geometry['modal']['right']+1, geometry
    assert geometry['body']['left']>=geometry['modal']['left']-1 and geometry['body']['right']<=geometry['modal']['right']+1, geometry
    assert geometry['close']['left']>=geometry['modal']['left'] and geometry['close']['right']<=geometry['modal']['right'], geometry
    assert page.locator('.settings-sidebar').is_visible()
    assert not page.locator('#settingsContent').is_visible()
    page.locator('#settingsMenu [data-settings-category="data-security"]').click()
    assert modal.evaluate('el=>el.classList.contains("settings-mobile-detail")') is True
    assert page.locator('#settingsContent').is_visible()
    assert_content_landmark(page,'Dados e Segurança')
    assert not page.locator('.settings-sidebar').is_visible()
    page.locator('#settingsBackBtn').click()
    assert modal.evaluate('el=>el.classList.contains("settings-mobile-detail")') is False
    assert page.locator('.settings-sidebar').is_visible()
    assert not page.locator('#settingsContent').is_visible()
    page.set_viewport_size({'width':1440,'height':900})

    page.locator('#settingsCloseBtn').click(); assert page.evaluate('sessionHasChanges()') is False
    assert page.evaluate('sessionStateFingerprint()')==before
    check_restored=page.evaluate("""()=>({
      grids:document.querySelectorAll('#checkWidgetGrid').length,
      parent:document.getElementById('checkWidgetGrid').parentElement?.id,
      primary:document.querySelector('#nav > .tab.active')?.dataset.primary
    })""")
    assert check_restored=={'grids':1,'parent':'check','primary':primary_before}, check_restored

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

    assert_no_errors(observed)
    assert_fixture_requests(page.context)
    page.context.close()


# SETTINGS-MACOS-01: expectations agreed before product implementation. These
# helpers drive public DOM and browser storage, never a product-only test API.
PROFILE_KEY='jpwealth_local_profile_v1'
NO_PROFILE=object()


def synthetic_png(width=48,height=32):
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    compressor=zlib.compressobj()
    parts=[]
    for row in range(height):
        parts.append(compressor.compress(b'\0'+bytes((35,110+(row%100),170))*width))
    parts.append(compressor.flush())
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))
            +chunk(b'IDAT',b''.join(parts))+chunk(b'IEND',b''))


def profile_boot(browser,url,raw=NO_PROFILE,read_failure=False):
    context=browser.new_context(viewport={'width':1440,'height':950},service_workers='block')
    install_bootstrap(context)
    # Match the existing portable server fixture in finalize_session_test:
    # the portable document refers to ../assets through its current directory.
    origin=urlsplit(url)
    context.route(f'{origin.scheme}://{origin.netloc}/dist/assets/**',lambda route:route.continue_(
        url=route.request.url.replace('/dist/assets/','/assets/')))
    setup={'key':PROFILE_KEY,'present':raw is not NO_PROFILE,'raw':None if raw is NO_PROFILE else raw,'readFailure':read_failure}
    context.add_init_script("""(() => {
      const setup="""+json.dumps(setup,ensure_ascii=False)+""";
      const get=Storage.prototype.getItem,set=Storage.prototype.setItem,remove=Storage.prototype.removeItem;
      if(!sessionStorage.getItem('__settingsProfileSeeded')){
        if(setup.present)set.call(localStorage,setup.key,setup.raw);
        set.call(localStorage,'settings_profile_unrelated','synthetic-preserved');
        set.call(localStorage,'jpw_fs','1');set.call(localStorage,'jpw_rail','expanded');
        sessionStorage.setItem('__settingsProfileSeeded','1');
      }
      window.__onbShown=true;window.__profileTestOps=[];
      window.__profileTestReadFail=setup.readFailure;window.__profileTestWriteFail='';
      window.__profileTestRaw=()=>get.call(localStorage,setup.key);
      window.__profileTestOtherRaw=()=>Object.fromEntries(Object.keys(localStorage).sort()
        .filter(k=>k!==setup.key).map(k=>[k,get.call(localStorage,k)]));
      Storage.prototype.getItem=function(k){
        if(this===localStorage&&k===setup.key&&window.__profileTestReadFail)
          throw new DOMException('Synthetic profile read failure','SecurityError');
        return get.call(this,k);
      };
      Storage.prototype.setItem=function(k,v){
        if(this===localStorage&&k===setup.key){
          window.__profileTestOps.push(['set',k]);
          if(window.__profileTestWriteFail==='quota')throw new DOMException('Synthetic profile quota','QuotaExceededError');
          if(window.__profileTestWriteFail==='noop')return;
          if(window.__profileTestWriteFail==='truncate'){set.call(this,k,'{"schemaVersion":');return;}
        }
        return set.call(this,k,v);
      };
      Storage.prototype.removeItem=function(k){
        if(this===localStorage&&k===setup.key)window.__profileTestOps.push(['remove',k]);
        return remove.call(this,k);
      };
    })();""")
    page=context.new_page()
    observed={'console':[],'pageerror':[],'failed':[],'http_errors':[]}
    page.on('console',lambda m:observed['console'].append((m.type,m.text,m.location)))
    page.on('pageerror',lambda e:observed['pageerror'].append(str(e)))
    page.on('requestfailed',lambda r:observed['failed'].append((r.url,r.failure)))
    page.on('response',lambda r:observed['http_errors'].append({'url':r.url,'status':r.status,'resource_type':r.request.resource_type}) if r.status>=400 else None)
    page.goto(url,wait_until='load');wait_bootstrap(page)
    page.evaluate("() => {closeModal();window.alert=()=>{};window.confirm=()=>false;window.prompt=()=>null;}")
    # A virgin baseline's first reload adopts the legacy operation identity and
    # onboarding flag. The paired zero-profile-action control demonstrates this
    # on both inherited and current sources. Finish that normal boot BEFORE the
    # immutable state oracle; later reloads must still preserve every field.
    page.reload(wait_until='load');wait_bootstrap(page)
    page.evaluate("() => {closeModal();window.alert=()=>{};window.confirm=()=>false;window.prompt=()=>null;}")
    page.jpwealth_profile_observed=observed
    page.jpwealth_profile_before={'state':page.evaluate('JSON.stringify(S)'),
        'preferences':page.evaluate("() => Object.fromEntries(['jpw_fs','jpw_rail','jpw_nav','jpw_expl','jpwealth_v9_icon_theme','jpwealth_v9_icon_choice','settings_profile_unrelated'].map(k=>[k,localStorage.getItem(k)]))")}
    return context,page


def open_profile(page,keyboard=None):
    if not page.locator('#settingsOverlay').is_visible():page.locator('#headerConfigBtn').click()
    launcher=page.locator('#settingsProfileBtn')
    assert launcher.count()==1,'PROFILE CONTRACT: local identity launcher is required'
    if keyboard:
        launcher.focus();launcher.press(keyboard)
    else:launcher.click()
    expect(page.locator('#settingsPageTitle')).to_have_text('JP Wealth Account')
    assert page.locator('[data-settings-panel="account"]').is_visible()
    assert_content_landmark(page,'JP Wealth Account')


def profile_raw(page):
    return page.evaluate('window.__profileTestRaw()')


def profile_status(page,state):
    expect(page.locator('#settingsProfileStatus')).to_have_attribute('data-state',state)


def profile_close(context,page,allow_operational_change=False):
    assert_no_errors(page.jpwealth_profile_observed)
    assert_fixture_requests(context)
    if not allow_operational_change:
        current_state=page.evaluate('JSON.stringify(S)')
        old=json.loads(page.jpwealth_profile_before['state']);new=json.loads(current_state)
        state_diff={k:{'before':old.get(k),'after':new.get(k)} for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
        assert current_state==page.jpwealth_profile_before['state'],{'contract':'Profile actions must not alter S','differences':state_diff,'only_json_order_changed':not state_diff}
        preferences=page.evaluate("() => Object.fromEntries(['jpw_fs','jpw_rail','jpw_nav','jpw_expl','jpwealth_v9_icon_theme','jpwealth_v9_icon_choice','settings_profile_unrelated'].map(k=>[k,localStorage.getItem(k)]))")
        assert preferences==page.jpwealth_profile_before['preferences'],'Profile actions must preserve existing preferences'
    context.close()


def upload_profile(page,data,mime='image/png',name='synthetic-avatar.png'):
    page.locator('#settingsProfilePhotoInput').set_input_files({'name':name,'mimeType':mime,'buffer':data})
    page.wait_for_function("() => !['busy','info'].includes(document.getElementById('settingsProfileStatus')?.dataset.state)")


def save_profile(page):
    page.locator('#settingsProfileSaveBtn').click()
    profile_status(page,'success')


def run_profile_contract(browser,url):
    # A new feature must fail explicitly on the inherited candidate, not skip.
    context,page=profile_boot(browser,url)
    before=page.evaluate('JSON.stringify(S)')
    others=page.evaluate('window.__profileTestOtherRaw()')
    page.locator('#headerConfigBtn').click()
    assert page.locator('#settingsProfileBtn').count()==1,'PROFILE CONTRACT: local identity launcher is required'
    assert 'JP Wealth Account' in page.locator('#settingsProfileBtn').inner_text()
    assert 'Seu perfil' in page.locator('#settingsProfileName').inner_text()
    assert page.locator('#settingsMenu [data-settings-category]').count()==8
    assert page.locator('#settingsProfileBtn').get_attribute('aria-label').startswith('JP Wealth Account')
    open_profile(page,'Enter')
    assert page.locator('#settingsProfileStatus').get_attribute('role')=='status'
    assert page.locator('#settingsProfileStatus').get_attribute('aria-live')=='polite'
    assert profile_raw(page) is None
    page.locator('#settingsBackBtn').click()
    expect(page.locator('#settingsPageTitle')).to_have_text('Geral')
    page.locator('#settingsForwardBtn').click()
    expect(page.locator('#settingsPageTitle')).to_have_text('JP Wealth Account')
    page.locator('#settingsBackBtn').click();open_profile(page,'Space')
    assert page.evaluate('window.__profileTestOps')==[],'Read and navigation must never materialize profile'
    assert page.evaluate('JSON.stringify(S)')==before
    assert page.evaluate('window.__profileTestOtherRaw()')==others
    name='Pessoa Sintética de Identidade Local'
    page.locator('#settingsProfileNameInput').fill(name)
    assert profile_raw(page) is None,'Editing creates only a draft'
    assert page.locator('#settingsProfileName').inner_text()=='Seu perfil'
    save_profile(page)
    saved=json.loads(profile_raw(page))
    assert saved=={'schemaVersion':1,'displayName':name,'avatarDataUrl':None},saved
    expect(page.locator('#settingsProfileName')).to_have_text(name)
    # No reseeding after reload: actual UI write is what must survive.
    page.reload(wait_until='load');wait_bootstrap(page);page.evaluate('closeModal()');open_profile(page)
    expect(page.locator('#settingsProfileNameInput')).to_have_value(name)
    assert page.evaluate('window.__profileTestOps')==[],'Reload must not rewrite the profile'
    checkpoint=page.evaluate('JSON.stringify(S)')
    backup=page.evaluate("async () => JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-09-13T00:00:00Z').text())")
    assert json.loads(backup['workspace']['preferences'][PROFILE_KEY])['displayName']==name,'Complete backup must include the confirmed profile'
    assert name not in page.evaluate('JSON.stringify(S)')
    assert page.evaluate('JSON.stringify(S)')==checkpoint
    raw_before=profile_raw(page)
    page.locator('#settingsProfileNameInput').fill('Rascunho cancelado')
    page.locator('#settingsProfileCancelBtn').click()
    expect(page.locator('#settingsProfileNameInput')).to_have_value(name)
    assert profile_raw(page)==raw_before
    # Treat markup as text; never create active elements from a display name.
    html_name='<img src=x onerror=alert(1)>'
    page.locator('#settingsProfileNameInput').fill(html_name);save_profile(page)
    expect(page.locator('#settingsProfileName')).to_have_text(html_name)
    assert page.locator('#settingsProfileName img').count()==0
    for invalid in ['x'*121,'Nome\u202eoculto','Nome\u0007controle']:
        page.locator('#settingsProfileNameInput').fill(invalid)
        current=profile_raw(page)
        page.locator('#settingsProfileSaveBtn').click()
        assert page.locator('#settingsProfileStatus').get_attribute('data-state') in ('error','blocked')
        assert profile_raw(page)==current
    page.locator('#settingsProfileNameInput').fill('😀'*120);save_profile(page)
    assert len(json.loads(profile_raw(page))['displayName'])==120
    page.locator('#settingsProfileNameInput').fill('');save_profile(page)
    expect(page.locator('#settingsProfileName')).to_have_text('Seu perfil')
    profile_close(context,page)
    print('PROFILE PASS — absent, explicit save, history, keyboard, reload, name safety, S/backup isolation',flush=True)

    valid={'schemaVersion':1,'displayName':'Sintético anterior','avatarDataUrl':None,'futureField':{'preserve':True}}
    for failure in ('quota','noop'):
        raw=json.dumps(valid,ensure_ascii=False,separators=(',',':'))
        context,page=profile_boot(browser,url,raw);open_profile(page)
        page.locator('#settingsProfileNameInput').fill('Rascunho deve sobreviver')
        page.evaluate('(x)=>window.__profileTestWriteFail=x',failure)
        page.locator('#settingsProfileSaveBtn').click()
        profile_status(page,'error')
        assert profile_raw(page)==raw
        expect(page.locator('#settingsProfileName')).to_have_text(valid['displayName'])
        expect(page.locator('#settingsProfileNameInput')).to_have_value('Rascunho deve sobreviver')
        page.evaluate("window.__profileTestWriteFail=''")
        save_profile(page)
        assert json.loads(profile_raw(page))['futureField']==valid['futureField']
        profile_close(context,page)
    print('PROFILE PASS — quota/no-op refuse false success; draft and unknown fields preserved',flush=True)

    for raw,read_failure in [('{"schemaVersion":',False),
            (json.dumps({'schemaVersion':2,'displayName':'Futuro','avatarDataUrl':None}),False),
            (json.dumps(valid),True)]:
        context,page=profile_boot(browser,url,raw,read_failure);open_profile(page)
        profile_status(page,'blocked')
        assert not page.locator('#settingsProfileSaveBtn').is_enabled()
        assert not page.locator('#settingsProfileChoosePhotoBtn').is_enabled()
        assert profile_raw(page)==raw
        assert page.evaluate('window.__profileTestOps')==[]
        profile_close(context,page)
    print('PROFILE PASS — malformed/future/unreadable records preserved without writes',flush=True)

    context,page=profile_boot(browser,url,json.dumps(valid));open_profile(page)
    page.locator('#settingsProfileNameInput').fill('Resultado de gravação indeterminado')
    page.evaluate("window.__profileTestWriteFail='truncate'")
    page.locator('#settingsProfileSaveBtn').click();profile_status(page,'blocked')
    assert profile_raw(page)=='{"schemaVersion":'
    assert not page.locator('#settingsProfileSaveBtn').is_enabled()
    assert not page.locator('#settingsProfileCancelBtn').is_enabled(),'Indeterminate writes require reload, not a blind retry'
    expect(page.locator('#settingsProfileName')).to_have_text(valid['displayName'])
    expect(page.locator('#settingsProfileNameInput')).to_have_value('Resultado de gravação indeterminado')
    assert len(page.evaluate('window.__profileTestOps'))==1
    profile_close(context,page)
    print('PROFILE PASS — unconfirmed/truncated write blocks retry and retains draft',flush=True)

    context,a=profile_boot(browser,url,json.dumps(valid));open_profile(a)
    b=context.new_page();b.goto(url,wait_until='load');wait_bootstrap(b);b.evaluate('closeModal()');open_profile(b)
    b.locator('#settingsProfileNameInput').fill('Rascunho da aba B')
    a.locator('#settingsProfileNameInput').fill('Gravação confirmada da aba A');save_profile(a)
    profile_status(b,'blocked')
    expect(b.locator('#settingsProfileNameInput')).to_have_value('Rascunho da aba B')
    assert not b.locator('#settingsProfileSaveBtn').is_enabled()
    assert json.loads(profile_raw(a))['displayName']=='Gravação confirmada da aba A'
    b.locator('#settingsProfileCancelBtn').click()
    expect(b.locator('#settingsProfileNameInput')).to_have_value('Gravação confirmada da aba A')
    b.locator('#settingsProfileNameInput').fill('Revisão consciente da aba B');save_profile(b)
    expect(a.locator('#settingsProfileName')).to_have_text('Revisão consciente da aba B')
    assert_fixture_requests(context);profile_close(context,a)
    print('PROFILE PASS — second-tab save blocks stale draft; explicit cancellation adopts current value',flush=True)

    context,page=profile_boot(browser,url,json.dumps(valid));open_profile(page)
    for mime in ('image/png','image/jpeg','image/webp'):
        data=page.evaluate("mime=>{const c=document.createElement('canvas');c.width=640;c.height=320;const x=c.getContext('2d');x.fillStyle='#287bb4';x.fillRect(0,0,640,320);x.fillStyle='#ebad47';x.fillRect(0,0,220,320);return c.toDataURL(mime);}",mime)
        if mime=='image/webp':webp_source=base64.b64decode(data.split(',')[1])
        raw_before=profile_raw(page)
        upload_profile(page,base64.b64decode(data.split(',')[1]),mime,'synthetic.'+mime.split('/')[1])
        assert profile_raw(page)==raw_before,'Selection/preview is not persistence'
        assert page.locator('#settingsProfileSaveBtn').is_enabled()
        save_profile(page)
        profile=json.loads(profile_raw(page));avatar=profile['avatarDataUrl']
        assert avatar.startswith('data:image/jpeg;base64,')
        assert len(base64.b64decode(avatar.split(',')[1]))<=200*1024
        dimensions=page.evaluate("src=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve([i.naturalWidth,i.naturalHeight]);i.onerror=reject;i.src=src})",avatar)
        assert dimensions==[256,256],dimensions  # Center crop, never stretch the source into an ellipse.
        image=page.locator('#settingsProfileAvatar img')
        expect(image).to_be_visible()
        assert image.evaluate("e=>getComputedStyle(e).objectFit")=='cover'
        assert image.get_attribute('alt')=='','Adjacent name supplies identity without duplicate reading'
        assert json.loads(profile_raw(page))['futureField']==valid['futureField']
    raw_with_photo=profile_raw(page)
    jpeg=base64.b64decode(json.loads(raw_with_photo)['avatarDataUrl'].split(',')[1])
    sof=jpeg.index(b'\xff\xc0');segment_length=struct.unpack('>H',jpeg[sof+2:sof+4])[0]
    undecodable_jpeg=jpeg[:sof+2+segment_length]+b'\xff\xd9'
    page.locator('#settingsProfileRemovePhotoBtn').click()
    assert profile_raw(page)==raw_with_photo
    page.locator('#settingsProfileCancelBtn').click()
    assert profile_raw(page)==raw_with_photo
    page.locator('#settingsProfileRemovePhotoBtn').click();save_profile(page)
    assert json.loads(profile_raw(page))['avatarDataUrl'] is None
    page.reload(wait_until='load');wait_bootstrap(page);page.evaluate('closeModal()');open_profile(page)
    assert json.loads(profile_raw(page))['avatarDataUrl'] is None
    # A positive boundary prevents a validator that simply rejects large inputs
    # from passing only the negative checks. Padding lies after the PNG IEND;
    # the decoded image is exactly 16 MP and the upload is exactly 5 MiB.
    boundary=synthetic_png(4000,4000)
    boundary+=b'\0'*(5*1024*1024-len(boundary))
    assert len(boundary)==5*1024*1024
    upload_profile(page,boundary);save_profile(page)
    normalized=json.loads(profile_raw(page))['avatarDataUrl']
    assert normalized.startswith('data:image/jpeg;base64,') and len(normalized)<=200*1024
    # Header-only >16MP image, corrupt decode, MIME spoofing and size boundary.
    too_many_pixels=synthetic_png(4001,4000)
    invalid_images=[(b'not an image','image/png'),(synthetic_png(),'image/jpeg'),
        (b'\x89PNG\r\n\x1a\ntruncated','image/png'),
        (synthetic_png()+b'\0'*(5*1024*1024),'image/png'),(too_many_pixels,'image/png'),
        (b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>','image/svg+xml')]
    for data,mime in invalid_images:
        raw_before=profile_raw(page)
        if page.locator('#settingsProfileCancelBtn').is_enabled():page.locator('#settingsProfileCancelBtn').click()
        upload_profile(page,data,mime)
        profile_status(page,'error')
        assert profile_raw(page)==raw_before
        assert not page.locator('#settingsProfileSaveBtn').is_enabled()
    # A VP8X header cannot lie about the actual VP8/VP8L dimensions. Prove
    # refusal before decode, since the parser enforces the memory/size boundary.
    webp=bytearray(webp_source)
    offset=12;extended=False
    while offset+8<=len(webp):
        length=struct.unpack('<I',webp[offset+4:offset+8])[0]
        if webp[offset:offset+4]==b'VP8X':
            webp[offset+12:offset+18]=b'\0'*6;extended=True;break
        offset+=8+length+(length%2)
    if not extended:
        webp=webp[:12]+b'VP8X'+struct.pack('<I',10)+b'\0'*10+webp[12:]
    webp[4:8]=struct.pack('<I',len(webp)-8)
    page.evaluate("""() => {
      const descriptor=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
      window.__profileBlobDecodeAttempts=0;
      Object.defineProperty(HTMLImageElement.prototype,'src',{...descriptor,set(value){
        if(String(value).startsWith('blob:'))window.__profileBlobDecodeAttempts++;
        return descriptor.set.call(this,value);
      }});
    }""")
    raw_before=profile_raw(page)
    upload_profile(page,bytes(webp),'image/webp','synthetic-contradictory.webp')
    profile_status(page,'error')
    assert profile_raw(page)==raw_before
    assert page.evaluate('window.__profileBlobDecodeAttempts')==0
    profile_close(context,page)
    print('PROFILE PASS — PNG/JPEG/WebP normalization, replacement/removal, image limits and invalid bytes',flush=True)

    for invalid_avatar in ['data:image/jpeg;base64,broken','data:image/jpeg;base64,'+base64.b64encode(undecodable_jpeg).decode()]:
        broken={**valid,'avatarDataUrl':invalid_avatar}
        raw=json.dumps(broken)
        context,page=profile_boot(browser,url,raw);open_profile(page)
        assert profile_raw(page)==raw and page.evaluate('window.__profileTestOps')==[]
        expect(page.locator('#settingsProfileAvatar img')).to_have_count(0)
        page.locator('#settingsProfileRemovePhotoBtn').click();save_profile(page)
        assert json.loads(profile_raw(page))['avatarDataUrl'] is None
        assert json.loads(profile_raw(page))['futureField']==valid['futureField']
        profile_close(context,page)
    print('PROFILE PASS — invalid stored avatar fallback and explicit repair',flush=True)


def main():
    global ROOT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--only',choices=['all','existing','profile'],default='all')
    args=parser.parse_args();ROOT=args.root.resolve();os.chdir(ROOT)
    inputs=['index.html','src/styles/app.css','src/js/40-app/09-settings-modal.js','src/js/40-app/07-finalize-session.js','build-id.js']
    source_before={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in inputs}
    print('SETTINGS IDENTITY '+json.dumps({'root':str(ROOT),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_sha256':source_before},ensure_ascii=False),flush=True)
    server,url=serve()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
            try:
                if args.only in ('all','existing'):run_existing_settings(browser,url)
                if args.only in ('all','profile'):run_profile_contract(browser,url)
            finally:browser.close()
    finally:server.shutdown();server.server_close()
    source_after={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in inputs}
    print('SETTINGS IDENTITY AFTER '+json.dumps(source_after),flush=True)
    if source_after!=source_before:raise RuntimeError('ENVIRONMENT_ERROR: candidate inputs changed during Settings validation')
    print('SETTINGS MODAL OK — existing contracts and requested profile scenarios verified: '+args.only)


if __name__=='__main__':
    main()
