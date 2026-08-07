#!/usr/bin/env python3
"""Falha de gravação no armazenamento local (A-001, 00-core/04-persistence.js).

Protege o contrato: save() nunca falha em silêncio. Cobre o caminho saudável, a
primeira falha, falhas repetidas (sem spam nem duplicação), a recuperação e o
acesso ao backup a partir do aviso — nas versões modular e portátil.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, socket, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def serve():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{port}/'

def prepare_page(browser, url):
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    observed = {'console': [], 'pageerror': []}
    page.on('console', lambda m: observed['console'].append((m.type, m.text)))
    page.on('pageerror', lambda e: observed['pageerror'].append(str(e)))
    page.route('**/dist/assets/**', lambda route: route.continue_(
        url=route.request.url.replace('/dist/assets/', '/assets/')))
    page.route('**/api.frankfurter.dev/**', lambda route: route.fulfill(
        status=200, content_type='application/json', body='{"rate":1}'))
    page.goto(url, wait_until='load')
    page.wait_for_timeout(700)
    page.evaluate("""() => {
      window.__onbShown = true; closeModal();
      window.alert = () => {}; window.confirm = () => false; window.prompt = () => null;
    }""")
    page.jpwealth_observed = observed
    return page

def break_storage(page):
    """Faz apenas a chave principal lançar QuotaExceededError; as demais seguem normais."""
    page.evaluate("""() => {
      if(window.__origSetItem) return;
      window.__origSetItem = Storage.prototype.setItem;
      Storage.prototype.setItem = function(k, v){
        if(k === 'jpwealth_v9_state'){
          const err = new Error('QuotaExceededError'); err.name = 'QuotaExceededError'; throw err;
        }
        return window.__origSetItem.call(this, k, v);
      };
    }""")

def restore_storage(page):
    page.evaluate("""() => {
      if(!window.__origSetItem) return;
      Storage.prototype.setItem = window.__origSetItem;
      window.__origSetItem = null;
    }""")

def alert_facts(page):
    return page.evaluate("""() => {
      const el = document.getElementById('persistenceAlert');
      return {
        existe: !!el,
        visivel: !!el && el.innerHTML.trim() !== '' && getComputedStyle(el).display !== 'none',
        role: el && el.getAttribute('role'),
        ariaLive: el && el.getAttribute('aria-live'),
        texto: el ? el.innerText : '',
        classe: el ? el.className : '',
        botoes: el ? el.querySelectorAll('button').length : -1,
        savedTagVisivel: document.getElementById('savedTag').classList.contains('show'),
        estado: {ativo: jpWealthPersistenceFailure.active, contagem: jpWealthPersistenceFailure.count},
      };
    }""")

def run_suite(browser, url, rotulo):
    page = prepare_page(browser, url)

    # ---- 1. caminho saudável: grava, retorna true, nenhum aviso ----
    page.evaluate("S.params.saldoIni = 11111")
    assert page.evaluate('save()') is True, f'[{rotulo}] save() deveria retornar true'
    a = alert_facts(page)
    assert a['existe'], f'[{rotulo}] #persistenceAlert deveria existir no DOM'
    assert not a['visivel'], f'[{rotulo}] nenhum aviso deveria estar visível no caminho saudável'
    assert a['role'] == 'alert' and a['ariaLive'] == 'assertive', a
    assert a['estado'] == {'ativo': False, 'contagem': 0}, a
    assert page.evaluate("JSON.parse(localStorage.getItem('jpwealth_v9_state')).params.saldoIni") == 11111, \
        f'[{rotulo}] o estado deveria ter sido realmente gravado'

    # ---- 2. primeira falha: retorna false, avisa, orienta, oferece backup ----
    # Sem intervalo entre o save() bem-sucedido acima e este: o selo "salvo" ainda está
    # dentro da sua janela de 1200ms, então a falha precisa apagá-lo ativamente — selo
    # verde e aviso de erro juntos na tela diriam coisas opostas.
    assert page.evaluate("document.getElementById('savedTag').classList.contains('show')") is True, \
        f'[{rotulo}] pré-condição: o selo "salvo" deveria estar visível logo após o sucesso'
    break_storage(page)
    page.evaluate("S.params.saldoIni = 22222")
    assert page.evaluate('save()') is False, f'[{rotulo}] save() deveria retornar false na falha'
    a = alert_facts(page)
    assert a['visivel'], f'[{rotulo}] o aviso de falha deveria estar visível'
    assert 'Falha ao salvar os dados' in a['texto'], a['texto']
    assert 'não conseguiu gravar' in a['texto'], a['texto']
    assert 'Não recarregue' in a['texto'] and 'backup' in a['texto'], a['texto']
    assert page.locator('#persistenceAlertBackupBtn').count() == 1, f'[{rotulo}] ação de backup ausente'
    assert not a['savedTagVisivel'], f'[{rotulo}] indicador "salvo" não pode aparecer na falha'
    assert a['estado']['ativo'] is True and a['estado']['contagem'] == 1, a
    # console.error com a exceção original
    erros = [t for (tipo, t) in page.jpwealth_observed['console'] if tipo == 'error']
    assert any('falha ao gravar' in t.lower() for t in erros), erros
    # o disco ainda tem o valor anterior — a falha não corrompeu nada
    assert page.evaluate("JSON.parse(localStorage.getItem('jpwealth_v9_state')).params.saldoIni") == 11111

    # ---- 3. falhas repetidas: um único aviso, sem duplicação, app utilizável ----
    for _ in range(5):
        assert page.evaluate('save()') is False
    assert page.evaluate("document.querySelectorAll('#persistenceAlert').length") == 1
    assert page.locator('#persistenceAlertBackupBtn').count() == 1, f'[{rotulo}] botão duplicado'
    assert page.evaluate("document.getElementById('persistenceAlert').querySelectorAll('button').length") == 1
    assert page.evaluate('jpWealthPersistenceFailure.count') == 6, 'contagem interna deveria acumular'
    # o aplicativo continua utilizável: navegação e drawer de Notas respondem
    page.evaluate("navigateToScreen('contab')")
    assert page.evaluate("document.getElementById('contab').classList.contains('active')")
    page.evaluate("navigateToScreen('dash')")
    page.locator('#headerNotesBtn').click()
    assert page.locator('#mvpNotesOverlay').evaluate("el => el.classList.contains('show')")
    page.locator('#mvpNotesCloseBtn').click()
    # o aviso não aprisiona o foco nem bloqueia o resto da página
    page.locator('#persistenceAlertBackupBtn').focus()
    assert page.evaluate("document.activeElement.id") == 'persistenceAlertBackupBtn'
    page.locator('#headerConfigBtn').focus()
    assert page.evaluate("document.activeElement.id") == 'headerConfigBtn'

    # ---- 4. backup durante a falha usa o S em memória, não o disco ----
    page.evaluate("""() => {
      window.__blob = null;
      window.URL.createObjectURL = (b) => { window.__blob = b; return 'blob:persist-test'; };
      window.URL.revokeObjectURL = () => {};
      HTMLAnchorElement.prototype.click = function(){};
      window.confirm = () => false;   // exporta sem senhas
    }""")
    page.locator('#persistenceAlertBackupBtn').click()
    exportado = page.evaluate("window.__blob ? window.__blob.text() : null")
    assert exportado, f'[{rotulo}] o botão do aviso deveria acionar a exportação existente'
    import json as _json
    payload = _json.loads(exportado)
    assert payload['state']['params']['saldoIni'] == 22222, \
        'o backup deve refletir o estado em memória (22222), não o último gravado (11111)'

    # ---- 5. recuperação: volta a true, grava, encerra o estado de falha ----
    restore_storage(page)
    page.evaluate("S.params.saldoIni = 33333")
    assert page.evaluate('save()') is True, f'[{rotulo}] save() deveria voltar a retornar true'
    assert page.evaluate("JSON.parse(localStorage.getItem('jpwealth_v9_state')).params.saldoIni") == 33333
    a = alert_facts(page)
    assert a['estado'] == {'ativo': False, 'contagem': 0}, a
    assert 'is-failure' not in a['classe'], f'[{rotulo}] estado visual de falha deveria ter encerrado'
    assert 'Falha ao salvar' not in a['texto'], a['texto']
    assert 'restabelecida' in a['texto'].lower(), a['texto']

    # ---- 6. uma nova falha ainda é detectada depois da recuperação ----
    break_storage(page)
    assert page.evaluate('save()') is False
    a = alert_facts(page)
    assert a['visivel'] and 'Falha ao salvar os dados' in a['texto'], a
    assert a['estado']['ativo'] is True and a['estado']['contagem'] == 1, a
    restore_storage(page)
    assert page.evaluate('save()') is True

    # ---- 6b. falha de SERIALIZAÇÃO: capturada, tipo próprio, sem promessa vazia ----
    # Ciclo temporário em S: JSON.stringify lança TypeError antes de tocar o storage.
    page.evaluate("S.__cicloTeste = S")
    assert page.evaluate('save()') is False, f'[{rotulo}] save() deveria retornar false na falha de serialização'
    a = alert_facts(page)
    assert a['visivel'], f'[{rotulo}] aviso deveria aparecer na falha de serialização'
    assert 'preparar os dados' in a['texto'], a['texto']
    assert 'Falha ao salvar os dados' not in a['texto'], 'tipo errado de aviso para falha de serialização'
    assert 'pode falhar pelo mesmo motivo' in a['texto'], 'o aviso deve declarar a limitação do backup'
    assert 'anote manualmente' in a['texto'], a['texto']
    assert not a['savedTagVisivel'], f'[{rotulo}] selo "salvo" não pode aparecer'
    assert page.evaluate("jpWealthPersistenceFailure.kind") == 'serialize'
    erros = [t for (tipo, t) in page.jpwealth_observed['console'] if tipo == 'error']
    assert any('serializar' in t.lower() for t in erros), erros
    # o clique no botão não pode virar exceção não tratada — o catch interno avisa
    page.evaluate("window.__msgSerial = null; window.alert = m => { window.__msgSerial = String(m); }")
    page.locator('#persistenceAlertBackupBtn').click()
    assert page.evaluate("window.__msgSerial") is not None, 'o clique deveria produzir orientação, não exceção'
    assert 'anote manualmente' in page.evaluate("window.__msgSerial")
    assert not page.jpwealth_observed['pageerror'], page.jpwealth_observed['pageerror']
    page.evaluate("window.alert = () => {}")
    # remove o ciclo — S volta ao normal, sem resíduo do teste
    page.evaluate("delete S.__cicloTeste")
    assert page.evaluate('save()') is True, f'[{rotulo}] removido o ciclo, save() deveria voltar a funcionar'
    assert page.evaluate("'__cicloTeste' in S") is False, 'o ciclo de teste não pode permanecer em S'
    assert page.evaluate("localStorage.getItem('jpwealth_v9_state').includes('__cicloTeste')") is False

    # ---- 6c. corrida do timer: nova falha durante a janela de "restabelecida" ----
    break_storage(page)
    assert page.evaluate('save()') is False
    restore_storage(page)
    assert page.evaluate('save()') is True          # "Gravação restabelecida" + timer de 6s
    assert 'restabelecida' in alert_facts(page)['texto'].lower()
    break_storage(page)
    assert page.evaluate('save()') is False         # nova falha ANTES dos 6s
    page.wait_for_timeout(6600)                     # espera além do prazo do timer antigo
    a = alert_facts(page)
    assert a['visivel'], f'[{rotulo}] o timer antigo não pode limpar o aviso da nova falha'
    assert 'Falha ao salvar os dados' in a['texto'], a['texto']
    assert a['estado']['ativo'] is True, a
    assert page.locator('#persistenceAlertBackupBtn').count() == 1, 'ação de backup deveria continuar disponível'
    restore_storage(page)
    assert page.evaluate('save()') is True

    # ---- 6d. falha → recuperação → recuperação de novo: sem timers concorrentes ----
    break_storage(page)
    page.evaluate('save()')
    restore_storage(page)
    assert page.evaluate('save()') is True          # recuperação 1 (timer 1)
    break_storage(page)
    page.evaluate('save()')
    restore_storage(page)
    assert page.evaluate('save()') is True          # recuperação 2 (timer 1 cancelado, timer 2)
    assert 'restabelecida' in alert_facts(page)['texto'].lower()
    page.wait_for_timeout(6600)
    a = alert_facts(page)
    assert not a['visivel'], f'[{rotulo}] após a janela, o aviso de recuperação deveria ter sumido'
    assert a['estado'] == {'ativo': False, 'contagem': 0}, a

    # ---- 7. sem IDs duplicados e sem pageerror ----
    dup = page.evaluate("""() => {
      const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
      const c = {}; ids.forEach(i => c[i] = (c[i]||0)+1);
      return Object.entries(c).filter(([,n]) => n > 1);
    }""")
    assert dup == [], dup
    assert not page.jpwealth_observed['pageerror'], page.jpwealth_observed['pageerror']
    page.close()

server, base_url = serve()
try:
    with sync_playwright() as pw:
        candidates = [
            os.environ.get('JP_WEALTH_CHROMIUM', ''),
            '/usr/bin/chromium',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        ]
        executable = next((p for p in candidates if p and Path(p).exists()), None)
        options = {'headless': True, 'args': ['--no-sandbox']}
        if executable:
            options['executable_path'] = executable
        browser = pw.chromium.launch(**options)
        run_suite(browser, base_url + 'index.html', 'modular')
        run_suite(browser, base_url + 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html', 'portátil')
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print('PERSISTENCE FAILURE OK — caminho saudável, primeira falha, falhas repetidas, '
      'backup em memória, recuperação e redetecção verificados (modular e portátil).')
