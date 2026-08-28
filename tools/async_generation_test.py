#!/usr/bin/env python3
"""Geração de persistência x continuações assíncronas (JPW-FX-WIPE-RACE).

Contrato: uma operação assíncrona iniciada sob uma geração da persistência não pode
gravar depois que essa geração for invalidada por uma limpeza total. O caso real é
`updateFxRates()`, que já captura `jpWealthPersistenceEpoch()` antes do `await` e o
confere depois — o elo que faltava era `wipeAllData()`, que apagava a chave sem
invalidar a geração, deixando o guard existente sempre verdadeiro.

O teste é DETERMINÍSTICO: o `fetch` de cotações é substituído por uma promessa que só
resolve quando o teste manda. Não há sleep arbitrário nem espera probabilística — cada
etapa é destravada por estado observável (`__fxInFlight`, `__fxDone`).
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, socket, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = 'jpwealth_v9_state'

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

def serve():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{port}/'

# Portão manual sobre window.fetch: as chamadas de câmbio ficam PENDENTES até
# __fxRelease() ser chamado. Instalado antes de qualquer script da página.
GATE = """
window.__onbShown = true;
window.__fxPending = [];
window.__fxInFlight = 0;
const __origFetch = window.fetch;
window.fetch = function(input, init){
  const url = String((input && input.url) || input || '');
  if (url.includes('frankfurter')) {
    window.__fxInFlight++;
    return new Promise(resolve => {
      window.__fxPending.push(() => resolve(new Response(
        JSON.stringify({rate: 1.2345}),
        {status: 200, headers: {'Content-Type': 'application/json'}})));
    });
  }
  return __origFetch.apply(this, arguments);
};
window.__fxRelease = function(){
  const fns = window.__fxPending.splice(0);
  fns.forEach(fn => fn());
  return fns.length;
};
"""

def open_page(browser, url):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    ctx.add_init_script(GATE)
    page = ctx.new_page()
    erros = []
    page.on('pageerror', lambda e: erros.append(str(e)))
    page.goto(url, wait_until='load')
    page.wait_for_timeout(400)
    page.evaluate("""() => {
      closeModal();
      window.alert = () => {};
      window.prompt = () => 'APAGAR';
      window.confirm = () => true;
    }""")
    page.jpwealth_erros = erros
    page.jpwealth_ctx = ctx
    return page

def disparar_fx(page):
    """Dispara updateFxRates e devolve só quando o fetch estiver comprovadamente em voo."""
    page.evaluate("""() => {
      window.__fxDone = false;
      window.__fxPending = [];
      window.__fxInFlight = 0;
      Promise.resolve(updateFxRates()).then(() => { window.__fxDone = true; });
    }""")
    # destrava por estado observável: o fetch já foi emitido
    page.wait_for_function("window.__fxPending.length > 0")

def liberar_e_aguardar(page):
    """Libera as respostas retidas e espera TODA a continuação assíncrona terminar."""
    page.evaluate("window.__fxRelease()")
    page.wait_for_function("window.__fxDone === true")

def chave(page):
    return page.evaluate(f"localStorage.getItem({json.dumps(LSKEY)})")

def run_suite(browser, url, rotulo):
    # ---- A. uso normal: FX continua atualizando e persistindo ----
    page = open_page(browser, url)
    page.evaluate("S.onboarding={...S.onboarding, done:true}; save()")
    antes = page.evaluate("S.instruments[0].preco")
    disparar_fx(page)
    liberar_e_aguardar(page)
    assert page.evaluate("S.instruments[0].preco") != antes, f'[{rotulo}] A: FX deveria ter atualizado o preço'
    gravado = json.loads(chave(page))
    assert gravado['instruments'][0]['preco'] == page.evaluate("S.instruments[0].preco"), \
        f'[{rotulo}] A: uso normal deve persistir a cotação nova'

    # ---- B. wipe durante o fetch: o wipe vence, a continuação antiga não regrava ----
    disparar_fx(page)
    page.evaluate("wipeAllData()")
    assert chave(page) is None, f'[{rotulo}] B: wipeAllData deveria ter removido a chave'
    epoca_pos_wipe = page.evaluate("jpWealthPersistenceEpoch()")
    liberar_e_aguardar(page)
    assert chave(page) is None, \
        f'[{rotulo}] B: continuação de geração antiga REGRAVOU a chave após o wipe'
    assert page.evaluate("jpWealthPersistenceEpoch()") == epoca_pos_wipe, \
        f'[{rotulo}] B: a continuação antiga não pode mexer na geração'

    # ---- C. novo ciclo após o wipe: operações novas voltam a persistir ----
    page.evaluate("S.onboarding={...S.onboarding, done:true}; save()")
    assert chave(page) is not None, f'[{rotulo}] C: gravação normal deve voltar a funcionar após o wipe'
    disparar_fx(page)
    liberar_e_aguardar(page)
    depois = json.loads(chave(page))
    assert depois['instruments'][0]['preco'] == page.evaluate("S.instruments[0].preco"), \
        f'[{rotulo}] C: FX iniciada DEPOIS do wipe deve persistir normalmente'
    assert not page.jpwealth_erros, page.jpwealth_erros
    page.jpwealth_ctx.close()

    # ---- D. recuperação: continua bloqueando gravação, sem regressão ----
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    ctx.add_init_script(GATE)
    ctx.add_init_script(
        "try{localStorage.setItem(%s,'{\"params\":{\"saldoIni\":1');}catch(e){}" % json.dumps(LSKEY))
    page = ctx.new_page()
    page.goto(url, wait_until='load'); page.wait_for_timeout(400)
    page.evaluate("() => { closeModal(); window.alert=()=>{}; window.prompt=()=>'APAGAR'; }")
    assert page.evaluate("jpWealthLoadRecoveryActive()") is True, f'[{rotulo}] D: recuperação deveria estar ativa'
    assert page.evaluate("save()") is False, f'[{rotulo}] D: save deve continuar vetado em recuperação'
    bruto = chave(page)
    disparar_fx(page); liberar_e_aguardar(page)
    assert chave(page) == bruto, f'[{rotulo}] D: FX não pode sobrescrever o banco protegido'
    ctx.close()

    # ---- E. Finalizar Sessão: preservação intencional das Notas continua valendo ----
    page = open_page(browser, url)
    page.evaluate("""() => {
      S.onboarding={...S.onboarding, done:true, operador:'Op', supervisor:'Sup'};
      S.mvpNotes.items=[{id:'n1', ticket:'JPW-TESTE', content:'nota', folderId:'', createdAt:'2026-01-01', updatedAt:'2026-01-01'}];
      save(); markSessionCheckpoint();
      S=emptyJPWealthState();
      // API atual: o commit durável grava o estado passado com read-back (mesma
      // transição: estado vazio preservando as Notas vai ao disco).
      const commit=sessionCommitFinalizedState(S);
      if(!commit.ok) throw new Error('commit do estado finalizado falhou: '+(commit.erro&&commit.erro.message));
    }""")
    estado = json.loads(chave(page))
    assert estado is not None, f'[{rotulo}] E: Finalizar Sessão regrava o estado vazio POR DESENHO'
    assert estado['mvpNotes']['items'], f'[{rotulo}] E: as Notas do MVP devem sobreviver'
    assert estado['ledger'] == [] and estado['onboarding']['done'] is False, f'[{rotulo}] E: o resto deve estar vazio'
    page.jpwealth_ctx.close()

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
    print('ASYNC GENERATION OK — FX normal persiste; wipe durante fetch vence e a '
          'continuação antiga não regrava; ciclo novo volta a persistir; recuperação '
          'intacta; Notas preservadas no Finalizar Sessão (modular e portátil).')

if __name__ == '__main__':
    main()
