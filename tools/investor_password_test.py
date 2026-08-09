#!/usr/bin/env python3
"""Política de segredo da senha de investidor.

Contrato: `investorPassword` nunca chega a armazenamento persistente — nem em
localStorage (save), nem no checkpoint de sessão, nem no backup exportado, nem
sobrevivendo de estados antigos via migrate(). Em memória funciona durante a
sessão; some no reload. O valor sintético de teste nunca aparece nos relatórios.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, socket, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

SEGREDO = 'FIXTURE-SINTETICA-9317'   # nunca imprimir em asserts

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def serve():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{port}/'

def open_page(browser, url, seed=None):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    ctx.add_init_script("window.__onbShown = true;")
    if seed is not None:
        ctx.add_init_script(
            "try{localStorage.setItem('jpwealth_v9_state',%s);}catch(e){}" % json.dumps(seed))
    page = ctx.new_page()
    page.route('**/api.frankfurter.dev/**', lambda r: r.fulfill(
        status=200, content_type='application/json', body='{"rates":{}}'))
    page.goto(url, wait_until='load')
    page.wait_for_timeout(600)
    return ctx, page

def run_suite(browser, url, rotulo):
    # 1) digitar senha em memória → save() → localStorage limpo, memória intacta
    ctx, page = open_page(browser, url)
    r = page.evaluate("""(seg) => {
      S.accounts[0].investorPassword = seg;
      S.onboarding.investorPassword = seg;
      save(); markSessionCheckpoint();
      return {
        ls: localStorage.getItem('jpwealth_v9_state').includes(seg),
        cp: (sessionStorage.getItem('jpwealth_session_checkpoint_v1')||'').includes(seg),
        mem: S.accounts[0].investorPassword === seg,
      }; }""", SEGREDO)
    assert r['mem'], f'[{rotulo}] a senha deve continuar utilizável em memória na sessão'
    assert not r['ls'], f'[{rotulo}] SEGREDO VAZOU para localStorage'
    assert not r['cp'], f'[{rotulo}] SEGREDO VAZOU para o checkpoint de sessão'

    # 2) digitar a senha NÃO acusa alterações não salvas (ela nunca será salva)
    assert page.evaluate('sessionHasChanges()') is False, \
        f'[{rotulo}] digitar a senha não pode gerar dirty de sessão'

    # 3) backup exportado nunca contém o segredo e declara segredosIncluidos:false
    blob = page.evaluate("""async () => {
      const b = dgBuildBackupBlob(1,'t.json',new Date().toISOString());
      return await b.text(); }""")
    assert SEGREDO not in blob, f'[{rotulo}] SEGREDO VAZOU para o backup'
    assert '"segredosIncluidos": false' in blob, f'[{rotulo}] envelope deve declarar false'

    # 4) reload: senha some da memória; nada persistiu
    page.reload(wait_until='load'); page.wait_for_timeout(600)
    r = page.evaluate("""(seg) => ({
      mem: S.accounts[0].investorPassword,
      onb: S.onboarding.investorPassword,
      ls: (localStorage.getItem('jpwealth_v9_state')||'').includes(seg) }）""".replace('）',')'), SEGREDO)
    assert r['mem'] == '' and r['onb'] == '', f'[{rotulo}] após reload a senha deve estar ausente'
    assert not r['ls'], f'[{rotulo}] SEGREDO no localStorage após reload'
    ctx.close()

    # 5) estado ANTIGO com senha em texto claro: estrutura aceita, segredo descartado
    estado_antigo = json.dumps({'params': {'saldoIni': 5000, 'saldoAtu': 5000},
                                'accounts': [{'nome': 'Legada', 'tipo': 'MESTRE', 'broker': 'X',
                                              'investorPassword': SEGREDO}]})
    ctx, page = open_page(browser, url, seed=estado_antigo)
    r = page.evaluate("""(seg) => {
      const ok = save();
      return { mem: S.accounts[0].investorPassword,
               nome: S.accounts[0].nome,
               ls: (localStorage.getItem('jpwealth_v9_state')||'').includes(seg),
               log: JSON.stringify(S.dataGovernance&&S.dataGovernance.changeLog||[]).includes(seg),
               gravou: ok }; }""", SEGREDO)
    assert r['nome'] == 'Legada', f'[{rotulo}] estrutura do estado antigo deve ser aceita'
    assert r['mem'] == '', f'[{rotulo}] migrate deveria descartar o segredo herdado'
    assert not r['ls'] and not r['log'], f'[{rotulo}] SEGREDO sobreviveu de estado antigo'
    assert r['gravou'] is True
    ctx.close()

def main():
    server, base = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            run_suite(browser, base + 'index.html', 'modular')
            run_suite(browser, base + 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html', 'portatil')
            browser.close()
    finally:
        server.shutdown()
    print('INVESTOR PASSWORD OK — memória de sessão funciona; localStorage, checkpoint, '
          'backup e migração de estados antigos nunca carregam o segredo (modular e portátil).')

if __name__ == '__main__':
    main()
