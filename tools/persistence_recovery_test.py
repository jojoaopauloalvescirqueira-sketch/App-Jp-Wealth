#!/usr/bin/env python3
"""Modo de recuperação de carregamento (A-005, 00-core/04-persistence.js).

Protege o contrato: um banco salvo que não pode ser carregado com segurança (JSON
inválido ou migração que lança) NUNCA é sobrescrito automaticamente. O app abre com
base provisória, bloqueia gravações, preserva cópia bruta e exige decisão explícita
(download / importação validada / base vazia) — nas versões modular e portátil.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, socket, tempfile, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = 'jpwealth_v9_state'
BAD_JSON = '{"params":{"saldoIni":123'                       # sintaticamente inválido
BAD_MIGRATE = '{"params":{"saldoIni":123},"instruments":[null]}'  # JSON ok; migrate lança

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def serve():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{port}/'

def open_page(browser, url, seed=None):
    """Contexto novo por cenário: localStorage isolado. `seed` grava a chave principal
    ANTES de qualquer script da página rodar (add_init_script)."""
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    if seed is not None:
        ctx.add_init_script(
            "try{localStorage.setItem(%s,%s);}catch(e){}" % (json.dumps(LSKEY), json.dumps(seed)))
    page = ctx.new_page()
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
      window.alert = m => { (window.__alerts = window.__alerts || []).push(String(m)); };
      window.confirm = () => false; window.prompt = () => null;
    }""")
    page.jpwealth_observed = observed
    page.jpwealth_ctx = ctx
    return page

def close_page(page):
    assert not page.jpwealth_observed['pageerror'], page.jpwealth_observed['pageerror']
    page.jpwealth_ctx.close()

def recovery_facts(page):
    return page.evaluate("""() => ({
      ativo: jpWealthLoadRecovery.active,
      kind: jpWealthLoadRecovery.kind,
      chaveCopia: jpWealthLoadRecovery.recoveryKey,
      bloqueado: jpWealthPersistenceIsBlocked(),
      avisoVisivel: (() => { const el = document.getElementById('persistenceRecovery');
        return !!el && el.innerHTML.trim() !== '' && getComputedStyle(el).display !== 'none'; })(),
      avisoTexto: document.getElementById('persistenceRecovery')?.innerText || '',
      a001Visivel: (() => { const el = document.getElementById('persistenceAlert');
        return !!el && el.innerHTML.trim() !== ''; })(),
      chavePrincipal: localStorage.getItem('jpwealth_v9_state'),
      copias: (() => { const ks = []; for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith('jpwealth_v9_state_corrompido_')) ks.push(k); } return ks; })(),
      saveRetorna: save(),
      savedTag: document.getElementById('savedTag').classList.contains('show'),
      provisorioEhDefaults: S.params.saldoIni === DEFAULTS.params.saldoIni && S.ledger.length === 0,
    })""")

def assert_recovery_entered(page, seed, kinds):
    f = recovery_facts(page)
    assert f['ativo'] is True and f['bloqueado'] is True, f
    assert f['kind'] in kinds, f['kind']
    assert f['avisoVisivel'], 'aviso de recuperação deveria estar visível'
    assert 'não pôde ser carregado com segurança' in f['avisoTexto'], f['avisoTexto']
    assert 'Não registre novos dados' in f['avisoTexto'], f['avisoTexto']
    assert f['chavePrincipal'] == seed, 'chave principal deveria permanecer byte a byte intacta'
    assert len(f['copias']) == 1 and f['chaveCopia'] in f['copias'], f['copias']
    assert page.evaluate(f"localStorage.getItem({json.dumps(f['chaveCopia'])})") == seed
    assert f['saveRetorna'] is False and f['savedTag'] is False, f
    assert f['provisorioEhDefaults'], 'S deveria ser a base provisória (DEFAULTS)'
    assert f['a001Visivel'] is False, 'o aviso do A-001 não deve disparar por saves bloqueados'
    return f

def run_suite(browser, url, rotulo):
    # ---- 6.1 estado válido: carregamento idêntico, sem bloqueio, sem aviso ----
    page = open_page(browser, url)
    page.evaluate("S.params.saldoIni = 44444")
    assert page.evaluate('save()') is True, f'[{rotulo}] banco válido: save() deveria funcionar'
    f = page.evaluate("""() => ({
      ativo: jpWealthLoadRecovery.active, bloqueado: jpWealthPersistenceIsBlocked(),
      aviso: document.getElementById('persistenceRecovery').innerHTML.trim() !== '',
      gravou: JSON.parse(localStorage.getItem('jpwealth_v9_state')).params.saldoIni === 44444 })""")
    assert f == {'ativo': False, 'bloqueado': False, 'aviso': False, 'gravou': True}, f
    close_page(page)

    # ---- 6.2 JSON inválido ----
    page = open_page(browser, url, seed=BAD_JSON)
    assert_recovery_entered(page, BAD_JSON, {'json-invalido'})
    erros = [t for (tipo, t) in page.jpwealth_observed['console'] if tipo == 'error']
    assert any('não pôde ser carregado com segurança' in t for t in erros), erros

    # ---- 6.4 chamadas durante/apos o boot não substituem a chave ----
    for _ in range(4):
        assert page.evaluate('save()') is False
    page.wait_for_timeout(1500)  # inclui updateFxRates→save() e timers do boot
    assert page.evaluate("localStorage.getItem('jpwealth_v9_state')") == BAD_JSON, \
        f'[{rotulo}] a chave principal foi alterada durante o boot'

    # ---- 6.5 download da cópia: texto bruto exato, sem save(), cópia permanece ----
    page.evaluate("""() => {
      window.__blob = null;
      window.URL.createObjectURL = b => { window.__blob = b; return 'blob:rec'; };
      window.URL.revokeObjectURL = () => {};
      HTMLAnchorElement.prototype.click = function(){ window.__dlName = this.download; };
    }""")
    page.locator('#persistenceRecoveryDownloadBtn').click()
    baixado = page.evaluate("window.__blob ? window.__blob.text() : null")
    assert baixado == BAD_JSON, f'[{rotulo}] o download deve conter exatamente o texto original'
    assert page.evaluate("window.__dlName").startswith('jpwealth_recuperacao_'), 'nome sem data/hora'
    f = recovery_facts(page)
    assert f['ativo'] and f['bloqueado'] and len(f['copias']) == 1, 'download não pode encerrar a proteção'
    close_page(page)

    # ---- 6.3 falha de migração sobre JSON válido (dado puro, sem monkey patch) ----
    page = open_page(browser, url, seed=BAD_MIGRATE)
    assert_recovery_entered(page, BAD_MIGRATE, {'migracao'})
    close_page(page)

    # ---- 6.7 importação INVÁLIDA durante a recuperação: nada muda ----
    page = open_page(browser, url, seed=BAD_JSON)
    assert_recovery_entered(page, BAD_JSON, {'json-invalido'})
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fx:
        fx.write(json.dumps({'tipo': 'jpwealth_full_backup', 'state': {'semParams': True}}))
        invalido = fx.name
    try:
        page.locator('#importFullBackupInput').set_input_files(invalido)
        page.wait_for_timeout(500)
    finally:
        Path(invalido).unlink(missing_ok=True)
    assert any('Backup inválido' in a for a in page.evaluate('window.__alerts || []'))
    f = recovery_facts(page)
    assert f['ativo'] and f['bloqueado'] and f['avisoVisivel'], 'importação inválida não pode encerrar a proteção'
    assert f['chavePrincipal'] == BAD_JSON and len(f['copias']) == 1, f
    close_page(page)

    # ---- 6.6 importação VÁLIDA: restaura, grava, desbloqueia, aviso sai, cópia fica ----
    page = open_page(browser, url)  # página saudável só para gerar o fixture válido
    estado_valido = page.evaluate("() => { const s = structuredClone(DEFAULTS); s.params.saldoIni = 77777; s.params.saldoAtu = 77777; return s; }")
    close_page(page)
    page = open_page(browser, url, seed=BAD_JSON)
    assert_recovery_entered(page, BAD_JSON, {'json-invalido'})
    chave_copia = page.evaluate('jpWealthLoadRecovery.recoveryKey')
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fx:
        fx.write(json.dumps({'tipo': 'jpwealth_full_backup', 'versao': 'V9.1', 'state': estado_valido}))
        valido = fx.name
    try:
        page.evaluate("() => { window.confirm = () => true; }")
        page.locator('#importFullBackupInput').set_input_files(valido)
        # A importacao roda sob o writer lock (DP-2): espera a CONDICAO OBSERVAVEL
        # de conclusao (o documento restaurado no disco), tolerando o instante em
        # que a chave ainda contem o JSON invalido semeado.
        page.wait_for_function(
            """() => { const r = localStorage.getItem('jpwealth_v9_state');
                       if (!r) return false;
                       try { return JSON.parse(r).params.saldoIni === 77777; }
                       catch (e) { return false; } }""", timeout=8000)
        page.evaluate("() => { window.__onbShown = true; closeModal(); }")
    finally:
        Path(valido).unlink(missing_ok=True)
    f = page.evaluate("""() => ({
      ativo: jpWealthLoadRecovery.active, bloqueado: jpWealthPersistenceIsBlocked(),
      aviso: document.getElementById('persistenceRecovery').innerHTML.trim() !== '',
      restaurado: S.params.saldoIni === 77777,
      gravado: JSON.parse(localStorage.getItem('jpwealth_v9_state')).params.saldoIni === 77777,
      saveOk: save() })""")
    assert f == {'ativo': False, 'bloqueado': False, 'aviso': False,
                 'restaurado': True, 'gravado': True, 'saveOk': True}, f
    assert page.evaluate(f"localStorage.getItem({json.dumps(chave_copia)})") == BAD_JSON, \
        'a cópia de recuperação deve permanecer como contingência após a importação'
    close_page(page)

    # ---- 6.8 aceitar base vazia: cancelar não muda nada; confirmar substitui ----
    page = open_page(browser, url, seed=BAD_JSON)
    assert_recovery_entered(page, BAD_JSON, {'json-invalido'})
    chave_copia = page.evaluate('jpWealthLoadRecovery.recoveryKey')
    page.evaluate("() => { window.confirm = () => false; }")          # cancela
    page.locator('#persistenceRecoveryResetBtn').click()
    f = recovery_facts(page)
    assert f['ativo'] and f['bloqueado'] and f['chavePrincipal'] == BAD_JSON, 'cancelar não pode mudar nada'
    page.evaluate("() => { window.__confirmMsg = null; window.confirm = m => { window.__confirmMsg = String(m); return true; }; }")
    page.locator('#persistenceRecoveryResetBtn').click()
    page.wait_for_timeout(500)
    page.evaluate("() => { window.__onbShown = true; closeModal(); }")
    msg = page.evaluate('window.__confirmMsg')
    assert 'sobrescrita' in msg and 'preservada' in msg and 'NÃO recupera' in msg, msg
    f = page.evaluate("""() => ({
      ativo: jpWealthLoadRecovery.active, bloqueado: jpWealthPersistenceIsBlocked(),
      aviso: document.getElementById('persistenceRecovery').innerHTML.trim() !== '',
      principalValida: (() => { try { return typeof JSON.parse(localStorage.getItem('jpwealth_v9_state')).params === 'object'; } catch(e){ return false; } })(),
      saveOk: save() })""")
    assert f == {'ativo': False, 'bloqueado': False, 'aviso': False, 'principalValida': True, 'saveOk': True}, f
    assert page.evaluate(f"localStorage.getItem({json.dumps(chave_copia)})") == BAD_JSON, \
        'a cópia de recuperação deve permanecer após aceitar a base vazia'
    close_page(page)

    # ---- 6.9 falha ao gravar a base vazia: nada é apagado, proteção continua ----
    page = open_page(browser, url, seed=BAD_JSON)
    assert_recovery_entered(page, BAD_JSON, {'json-invalido'})
    page.evaluate("""() => {
      window.__origSet = Storage.prototype.setItem;
      Storage.prototype.setItem = function(k, v){
        if (k === 'jpwealth_v9_state') { const e = new Error('QuotaExceededError'); e.name = 'QuotaExceededError'; throw e; }
        return window.__origSet.call(this, k, v);
      };
      window.confirm = () => true;
    }""")
    page.locator('#persistenceRecoveryResetBtn').click()
    page.wait_for_timeout(300)
    f = recovery_facts(page)
    assert f['ativo'] and f['bloqueado'], 'a proteção deve continuar após a falha de gravação'
    assert f['chavePrincipal'] == BAD_JSON, 'a chave problemática não pode ser apagada sem escrita bem-sucedida'
    assert len(f['copias']) == 1, f['copias']
    assert f['avisoVisivel'], 'o aviso de recuperação deve continuar'
    assert f['a001Visivel'], 'o A-001 deveria informar a falha de armazenamento da tentativa'
    assert any('não pôde ser gravada' in a for a in page.evaluate('window.__alerts || []'))
    # Bloco com corpo (retorno undefined): a expressão nua devolveria a função nativa
    # e o Playwright falharia ao serializá-la ("Illegal invocation"). Latente até aqui
    # porque o teste morria antes, na regressão do import.
    page.evaluate("() => { Storage.prototype.setItem = window.__origSet; }")
    close_page(page)

    # ---- 6.11 Finalizar Sessão durante recuperação: interrompido antes de qualquer escrita ----
    page = open_page(browser, url, seed=BAD_JSON)
    assert_recovery_entered(page, BAD_JSON, {'json-invalido'})
    copia = page.evaluate('jpWealthLoadRecovery.recoveryKey')
    page.locator('#finalizeSessionBtn').click()
    modal = page.evaluate("document.getElementById('modalBox').innerText")
    assert 'modo de recuperação' in modal, modal
    assert 'não pode ser executado' in modal, 'o fluxo normal não pode prosseguir em recuperação'
    assert 'ENCERRAR SESSÃO' not in modal and page.locator('#sessionProceed').count() == 0, \
        'nenhuma etapa do fluxo destrutivo normal pode ser oferecida'
    page.locator('#sessionCancel').click()
    # finalização vinda de OUTRA ABA: o cinto em clearJPWealthLocalData interrompe
    page.evaluate("sessionHandleRemoteFinalization({type:'jpwealth-session-finalized', token:'aba-remota'})")
    page.wait_for_timeout(200)
    f = recovery_facts(page)
    assert f['chavePrincipal'] == BAD_JSON, 'nem a finalização remota pode tocar a chave principal'
    assert page.evaluate(f"localStorage.getItem({json.dumps(copia)})") == BAD_JSON, 'a cópia deve sobreviver'
    assert f['ativo'] and f['avisoVisivel'] and f['saveRetorna'] is False, f

    # Overrides SEMPRE em bloco `() => { ... }`: se a string do evaluate termina numa
    # expressão-função (a própria atribuição), o Playwright A INVOCA — o contador de
    # prompt nascia em 1 sem clique algum. Latente até o import transacional destravar
    # os cenários além da linha 154.
    # ---- 6.12 Zona de Perigo durante recuperação: bloqueada antes do primeiro prompt ----
    page.evaluate("() => { window.__prompts = 0; window.prompt = () => { window.__prompts++; return 'APAGAR'; }; }")
    page.evaluate("window.__alerts = []")
    # O botão "Limpar dados salvos" vive num rodapé fora da rota padrão 'dash'
    # (DEFAULT_START_ROUTE do JPW-HJFGDE); o contrato sob teste é a GUARDA dentro de
    # wipeAllData(), então acionamos o listener real por dispatch em vez de exigir
    # visibilidade Playwright de um elemento de outra tela.
    page.evaluate("document.getElementById('resetBtn').click()")
    page.wait_for_timeout(200)
    assert page.evaluate('window.__prompts') == 0, 'a limpeza deve ser interrompida ANTES do prompt'
    assert any('modo de recuperação' in a for a in page.evaluate('window.__alerts')), \
        'o operador deve ser orientado às três ações de recuperação'
    f = recovery_facts(page)
    assert f['chavePrincipal'] == BAD_JSON and f['ativo'] and f['avisoVisivel'], f
    assert page.evaluate(f"localStorage.getItem({json.dumps(copia)})") == BAD_JSON, f
    close_page(page)

    # ---- 6.13 estado saudável: Finalizar Sessão e Zona de Perigo seguem normais ----
    page = open_page(browser, url)
    page.evaluate("""() => {
      S.onboarding = {...S.onboarding, done: true, operador: 'Op', supervisor: 'Sup'};
      S.params.saldoIni = 555; save(); markSessionCheckpoint();
    }""")
    page.locator('#finalizeSessionBtn').click()
    texto = page.evaluate("document.getElementById('modalBox').innerText").lower()
    assert 'finalizar sessão neste computador' in texto or 'alterações posteriores' in texto, \
        'em estado saudável o fluxo normal deve abrir'
    assert 'modo de recuperação' not in texto
    page.evaluate("document.getElementById('sessionCancel').click()")
    page.evaluate("() => { window.prompt = () => 'APAGAR'; window.alert = () => {}; }")
    # Mesmo motivo do 6.12: o botão vive fora da rota padrão 'dash'; o contrato é o
    # comportamento de wipeAllData(), acionado pelo listener real.
    page.evaluate("document.getElementById('resetBtn').click()")
    page.wait_for_timeout(600)
    page.evaluate("() => { window.__onbShown = true; closeModal(); }")
    assert page.evaluate('S.params.saldoIni') == page.evaluate('DEFAULTS.params.saldoIni'), \
        'em estado saudável a Zona de Perigo deve funcionar'
    assert page.evaluate('save()') is True
    close_page(page)

    # ---- 6.14 falha de LEITURA: sem cópia prometida, opções compatíveis ----
    # getItem interceptado ANTES dos scripts da página (init script) — load() real detecta.
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    ctx.add_init_script("""(() => {
      const orig = Storage.prototype.getItem;
      Storage.prototype.getItem = function(k){
        if (k === 'jpwealth_v9_state') { const e = new Error('SecurityError'); e.name = 'SecurityError'; throw e; }
        return orig.call(this, k);
      };
    })()""")
    page = ctx.new_page()
    page.on('pageerror', lambda e: (_ for _ in ()).throw(AssertionError(str(e))))
    page.route('**/dist/assets/**', lambda route: route.continue_(
        url=route.request.url.replace('/dist/assets/', '/assets/')))
    page.route('**/api.frankfurter.dev/**', lambda route: route.fulfill(
        status=200, content_type='application/json', body='{"rate":1}'))
    page.goto(url, wait_until='load')
    page.wait_for_timeout(700)
    page.evaluate("() => { window.__onbShown = true; closeModal(); window.alert = () => {}; }")
    f = page.evaluate("""() => ({
      ativo: jpWealthLoadRecovery.active, kind: jpWealthLoadRecovery.kind,
      bloqueado: jpWealthPersistenceIsBlocked(), raw: jpWealthLoadRecovery.raw,
      chaveCopia: jpWealthLoadRecovery.recoveryKey,
      texto: document.getElementById('persistenceRecovery').innerText,
      temDownload: !!document.getElementById('persistenceRecoveryDownloadBtn'),
      temImport: !!document.getElementById('persistenceRecoveryImportBtn'),
      temReset: !!document.getElementById('persistenceRecoveryResetBtn'),
      saveRecusa: save() === false })""")
    assert f['ativo'] and f['kind'] == 'leitura' and f['bloqueado'] and f['saveRecusa'], f
    assert f['raw'] is None and f['chaveCopia'] is None, 'sem conteúdo legível não há cópia'
    assert 'não pôde ser lido' in f['texto'], 'o aviso deve explicar a limitação da leitura'
    assert 'Cópia de recuperação:' not in f['texto'], 'nenhuma cópia pode ser prometida'
    assert not f['temDownload'] and f['temImport'] and f['temReset'], \
        'sem texto bruto: só importar backup e base vazia fazem sentido'
    ctx.close()

    # ---- 6.10 recarregamento em modo de recuperação: redetecção sem cópias duplicadas ----
    page = open_page(browser, url, seed=BAD_JSON)
    assert_recovery_entered(page, BAD_JSON, {'json-invalido'})
    page.reload(wait_until='load')
    page.wait_for_timeout(700)
    page.evaluate("""() => { window.__onbShown = true; closeModal();
      window.alert = () => {}; window.confirm = () => false; }""")
    f = recovery_facts(page)
    assert f['ativo'] and f['bloqueado'] and f['avisoVisivel'], 'recarregar deve redetectar a proteção'
    assert f['chavePrincipal'] == BAD_JSON, f
    assert len(f['copias']) == 1, f'cópias idênticas não devem se multiplicar a cada reload: {f["copias"]}'
    close_page(page)

# ---- busca global por bypasses (estática): todo ponto que toca a chave principal deve
# estar classificado e protegido. Se um arquivo novo passar a escrever/remover LSKEY,
# esta asserção quebra e obriga a classificação consciente do novo ponto. ----
def audit_main_key_writers():
    escritores = []
    for f in sorted((ROOT / 'src' / 'js').rglob('*.js')):
        rel = str(f.relative_to(ROOT))
        for i, linha in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            # 'keys=[LSKEY]' captura a remoção indireta de clearJPWealthLocalData
            # (monta a lista e remove num loop — removeItem(key), não removeItem(LSKEY)).
            if ('setItem(LSKEY' in linha or 'removeItem(LSKEY' in linha
                    or 'localStorage[LSKEY]' in linha or 'keys=[LSKEY]' in linha):
                escritores.append((rel, i))
    arquivos = sorted({e[0] for e in escritores})
    assert arquivos == ['src/js/00-core/04-persistence.js', 'src/js/40-app/07-finalize-session.js'], \
        f'ponto NÃO CLASSIFICADO tocando a chave principal: {escritores}'
    # os pontos conhecidos fora de save() precisam da guarda de recuperação por perto
    finalize = (ROOT / 'src/js/40-app/07-finalize-session.js').read_text(encoding='utf-8')
    assert finalize.count('jpWealthLoadRecoveryActive') >= 3, \
        'guardas de recuperação ausentes em finalize-session (clearJPWealthLocalData, sessionCommitFinalizedState, openFinalizeSessionFlow)'
    # contrato ALD-C3-PRE-PERSISTENCE: o mecanismo ativo de gravação final é o commit
    # com read-back; o helper antigo de regravação cega não pode voltar como mecanismo.
    assert 'function sessionCommitFinalizedState(' in finalize, \
        'sessionCommitFinalizedState ausente — o commit durável da finalização sumiu'
    assert 'function persistNotesAfterSessionWipe(' not in finalize, \
        'persistNotesAfterSessionWipe voltou como mecanismo ativo — contrato write-before-clear violado'
    wipe = (ROOT / 'src/js/40-app/05-wipe-all.js').read_text(encoding='utf-8')
    assert 'jpWealthLoadRecoveryActive' in wipe, 'guarda de recuperação ausente na Zona de Perigo'

audit_main_key_writers()

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
print('PERSISTENCE RECOVERY OK — estado válido, JSON inválido, falha de migração, saves de '
      'boot, download bruto, importação válida/inválida, base vazia (aceita/cancelada/falha '
      'de gravação) e recarregamento sem duplicação verificados (modular e portátil).')
