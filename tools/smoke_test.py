#!/usr/bin/env python3
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import contextlib
import os
import socket
import threading
import time
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

with socket.socket() as s:
    s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
server=ThreadingHTTPServer(('127.0.0.1',port),Quiet)
thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()

errors=[]
try:
    with sync_playwright() as p:
        candidates=[
            os.environ.get('JP_WEALTH_CHROMIUM',''),
            '/usr/bin/chromium',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            str(Path.home()/'Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing')
        ]
        executable=next((x for x in candidates if x and Path(x).exists()),None)
        launch_options={'headless':True,'args':['--no-sandbox']}
        if executable: launch_options['executable_path']=executable
        browser=p.chromium.launch(**launch_options)
        page=browser.new_page()
        page.on('pageerror', lambda exc: errors.append('pageerror: '+str(exc)))
        page.on('console', lambda msg: errors.append('console error: '+msg.text) if msg.type=='error' else None)
        portable=ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
        html=portable.read_text(encoding='utf-8')
        # A-004: os textos da Zona de Perigo (card + prompt + alerta final, todos presentes
        # no monólito) declaram o comportamento real — preferências locais de interface
        # preservadas e cópias de recuperação intactas — sem enfraquecer a seriedade.
        assert 'Preferências locais de interface' in html, 'texto deve declarar a preservação das preferências'
        assert 'cópias de recuperação existentes não são apagadas' in html.lower() or \
               'Cópias de recuperação existentes não são apagadas' in html or \
               'cópias de recuperação existentes foram preservadas' in html, html.count('recuperação')
        assert 'TODA a base do JP Wealth' in html, 'o aviso destrutivo deve continuar sério e específico'
        assert 'Irreversível' in html or 'irreversível' in html
        assert 'apaga TODOS os dados (ordens' not in html, 'a promessa absoluta antiga deveria ter sido removida'
        storage_polyfill='<script>(()=>{const store={};Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>Object.prototype.hasOwnProperty.call(store,k)?store[k]:null,setItem:(k,v)=>store[k]=String(v),removeItem:k=>delete store[k],clear:()=>Object.keys(store).forEach(k=>delete store[k]),key:i=>Object.keys(store)[i]??null,get length(){return Object.keys(store).length}}});})();</script>' 
        html=html.replace('<head>','<head>'+storage_polyfill,1)
        page.set_content(html, wait_until='load')
        page.wait_for_timeout(500)
        facts=page.evaluate('''() => ({
          compute: typeof compute,
          render: typeof render,
          tabs: document.querySelectorAll('#nav .tab[data-screen]').length,
          headerActions: document.querySelectorAll('#headerActions .header-action').length,
          state: typeof S === 'object' && !!S.params,
          storageKey: typeof LSKEY !== 'undefined' ? LSKEY : null,
          title: document.title,
          iconPicker: typeof openAppIconPicker === 'function',
          iconConfig: !!document.querySelector('#appIconConfig'),
          manifestHref: document.querySelector('link[rel="manifest"]')?.getAttribute('href') || null
        })''')
        assert facts['compute']=='function', facts
        assert facts['render']=='function', facts
        assert facts['tabs']==7, facts
        assert facts['headerActions']==2, facts
        assert facts['state'] is True, facts
        assert facts['storageKey']=='jpwealth_v9_state', facts
        assert facts['iconPicker'] is True, facts
        assert facts['iconConfig'] is True, facts
        assert 'jp-wealth.webmanifest' in facts['manifestHref'], facts
        empty=page.evaluate('''() => ({
          monthly: document.querySelector('#mqlMonthly')?.textContent || '',
          ret: document.querySelector('#dRetAcum')?.textContent || '',
          dd: document.querySelector('#dDDmax')?.textContent || '',
          operator: document.querySelector('#obOperador')?.value ?? null,
          operatorPlaceholder: document.querySelector('#obOperador')?.getAttribute('placeholder') || '',
          supervisor: document.querySelector('#obSupervisor')?.value ?? null,
          supervisorPlaceholder: document.querySelector('#obSupervisor')?.getAttribute('placeholder') || ''
        })''')
        assert 'Sem dados ainda — registre fechamentos diários na aba 07 Contabilidade.' in empty['monthly'], empty
        assert '2026' not in empty['monthly'], empty
        assert empty['ret']=='—' and empty['dd']=='—', empty
        assert empty['operator']=='' and empty['supervisor']=='', empty
        assert empty['operatorPlaceholder']=='Preencher nome', empty
        assert empty['supervisorPlaceholder']=='Preencher nome', empty
        page.evaluate('''() => {
          window.alert=()=>{};
          const consent=document.querySelector('#obConsent');
          if(consent) consent.checked=true;
          document.querySelector('#modalConfirm')?.click();
        }''')
        page.wait_for_timeout(50)
        validation=page.evaluate('''() => ({
          ident: document.querySelector('[data-onbstep="ident"]')?.classList.contains('active') || false,
          operator: document.querySelector('#obOperador')?.value ?? null,
          supervisor: document.querySelector('#obSupervisor')?.value ?? null
        })''')
        assert validation['ident'] and validation['operator']=='' and validation['supervisor']=='', validation
        page.evaluate('''() => {
          window.prompt=()=> 'APAGAR';
          window.alert=()=>{};
          document.querySelector('#resetBtn')?.click();
        }''')
        page.wait_for_timeout(500)
        after_reset=page.evaluate('''() => ({
          ledger: Array.isArray(S.ledger) ? S.ledger.length : -1,
          monthly: document.querySelector('#mqlMonthly')?.textContent || '',
          operator: document.querySelector('#obOperador')?.value ?? null,
          supervisor: document.querySelector('#obSupervisor')?.value ?? null
        })''')
        assert after_reset['ledger']==0, after_reset
        assert '2026' not in after_reset['monthly'] and 'Sem dados ainda — registre fechamentos diários na aba 07 Contabilidade.' in after_reset['monthly'], after_reset
        assert after_reset['operator']=='' and after_reset['supervisor']=='', after_reset
        page.evaluate('''() => document.querySelector('#wipeAllBtn')?.click()''')
        page.wait_for_timeout(500)
        after_wipe=page.evaluate('''() => ({
          ledger: Array.isArray(S.ledger) ? S.ledger.length : -1,
          monthly: document.querySelector('#mqlMonthly')?.textContent || '',
          operator: document.querySelector('#obOperador')?.value ?? null,
          supervisor: document.querySelector('#obSupervisor')?.value ?? null
        })''')
        assert after_wipe['ledger']==0, after_wipe
        assert '2026' not in after_wipe['monthly'] and 'Sem dados ainda — registre fechamentos diários na aba 07 Contabilidade.' in after_wipe['monthly'], after_wipe
        assert after_wipe['operator']=='' and after_wipe['supervisor']=='', after_wipe
        real=page.evaluate('''() => {
          S.params.saldoIni=10000;
          S.ledger=[{data:'2026-01-31',saldo:10100}];
          renderDash();
          return {
            monthly: document.querySelector('#mqlMonthly')?.textContent || '',
            ret: document.querySelector('#dRetAcum')?.textContent || '',
            dd: document.querySelector('#dDDmax')?.textContent || ''
          };
        }''')
        assert '2026' in real['monthly'] and 'Sem dados ainda' not in real['monthly'], real
        assert real['ret']=='1.0%' and real['dd']=='0.0%', real
        edit=page.evaluate('''() => {
          S.ledger=[];
          S.onboarding={...S.onboarding, done:true, operador:'Operador Teste', supervisor:'Supervisor Teste'};
          closeModal();
          openOnboardingModal();
          return {
            operator: document.querySelector('#obOperador')?.value ?? null,
            supervisor: document.querySelector('#obSupervisor')?.value ?? null,
            operatorPlaceholder: document.querySelector('#obOperador')?.getAttribute('placeholder') || '',
            supervisorPlaceholder: document.querySelector('#obSupervisor')?.getAttribute('placeholder') || ''
          };
        }''')
        assert edit['operator']=='Operador Teste' and edit['supervisor']=='Supervisor Teste', edit
        assert edit['operatorPlaceholder']=='Preencher nome' and edit['supervisorPlaceholder']=='Preencher nome', edit
        page.evaluate('''() => { closeModal(); renderDash(); }''')
        page.evaluate('openAppIconPicker()')
        assert page.locator('[data-app-icon-option]').count()==2, 'biblioteca de ícones incompleta'
        page.evaluate('closeModal()')
        screens=page.eval_on_selector_all('#nav .tab[data-screen]', 'els => els.map(e => e.dataset.screen)')
        for screen in screens:
            ok=page.evaluate('''screen => {
              const b=document.querySelector(`#nav .tab[data-screen="${screen}"]`);
              if(!b) return false;
              b.click();
              return document.getElementById(screen)?.classList.contains('active') || false;
            }''', screen)
            assert ok, f'tela não ativou: {screen}'
        page.locator('#headerConfigBtn').focus()
        page.locator('#headerConfigBtn').press('Enter')
        assert page.locator('#settingsOverlay').evaluate("el => el.classList.contains('show')")
        assert not page.locator('#config').evaluate("el => el.classList.contains('active')")
        page.locator('#settingsCloseBtn').click()

        # Notas do MVP — botão, drawer, criação simples, badge, ocultar sem apagar, acesso pela
        # Central; schema v2: pastas (folders/folderId) presentes e preservadas nas mesmas ações.
        assert page.locator('#headerNotesBtn').is_visible(), 'botão Notas do MVP deveria estar visível por padrão'
        assert page.evaluate('S.mvpNotes.schemaVersion')==5, 'estado de notas deveria estar no schema v5'
        assert page.evaluate('S.mvpNotes.ui.drawerWidth')==980, 'preferência de largura do painel deveria existir com o padrão v5'
        assert page.evaluate('Array.isArray(S.mvpNotes.folders)'), 'schema v2 exige o array de pastas'
        page.locator('#headerNotesBtn').click()
        assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')"), 'drawer de Notas deveria abrir'
        page.evaluate("window.prompt=()=> 'Pasta de fumaça'")
        page.locator('#mvpNotesNewFolderBtn').click()
        assert page.evaluate('S.mvpNotes.folders.length')==1, 'pasta deveria ter sido criada'
        page.locator('#mvpNotesNewBtn').click()
        page.locator('#mvpNoteContent').fill('Nota de fumaça')
        assert page.evaluate('mvpNotesUI.draft.folderId')==page.evaluate('S.mvpNotes.folders[0].id'), 'nota nova em pasta ativa deveria herdar a pasta'
        page.locator('#mvpNotesSaveBtn').click()
        assert page.evaluate('S.mvpNotes.items.length')==1, 'nota deveria ter sido criada'
        assert page.evaluate('S.mvpNotes.items[0].folderId')==page.evaluate('S.mvpNotes.folders[0].id'), 'nota deveria estar vinculada à pasta'
        assert page.locator('#headerNotesBadge').inner_text()=='1', 'badge deveria contar a nota ativa'
        page.locator('#mvpNotesCloseBtn').click()
        page.locator('#headerConfigBtn').click()
        page.evaluate("settingsNavigateToLeaf('interface')")
        page.locator('[data-mvp-notes-visibility="hide"]').click()
        assert page.locator('#headerNotesBtn').is_hidden(), 'ocultar deveria esconder o botão do header'
        assert page.evaluate('S.mvpNotes.items.length')==1, 'ocultar o ícone não pode apagar a nota'
        assert page.evaluate('S.mvpNotes.folders.length')==1, 'ocultar o ícone não pode apagar a pasta'
        page.locator('#mvpNotesOpenFromSettingsBtn').click()
        assert page.locator('.mvpn-card').count()==1, 'painel deveria continuar acessível pelas Configurações com o ícone oculto'
        page.locator('#mvpNotesCloseBtn').click()
        page.locator('[data-mvp-notes-visibility="show"]').click()
        page.locator('#settingsCloseBtn').click()
        browser.close()
finally:
    server.shutdown(); server.server_close()

if errors:
    raise SystemExit('SMOKE FALHOU\n'+'\n'.join(errors))
print('SMOKE OK — estado vazio, resets, ledger real, onboarding, 7 áreas operacionais e Notas do MVP verificados.')
