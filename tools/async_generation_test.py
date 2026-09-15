#!/usr/bin/env python3
"""Geração de persistência x continuações assíncronas (JPW-FX-WIPE-RACE).

Contrato: uma operação assíncrona iniciada sob uma geração da persistência não pode
gravar depois que essa geração for invalidada por uma limpeza total. O caso real é
`updateFxRates()`, que já captura `jpWealthPersistenceEpoch()` antes do `await` e o
confere depois — o elo que faltava era `wipeAllData()`, que apagava a chave sem
invalidar a geração, deixando o guard existente sempre verdadeiro.

O teste é DETERMINÍSTICO: o `fetch` de cotações é substituído por uma promessa que só
resolve quando o teste manda. Não há sleep arbitrário nem espera probabilística — cada
etapa é destravada pelo estado do coordenador e por `__fxDone`. As respostas
contêm identidade/data válidas; referências diárias não alteram preços manuais.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, socket, threading
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options

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
GATE = r"""
window.__onbShown = true;
window.__fxPending = [];
window.__fxInFlight = 0;
window.__fxGateRate = 1.2345;
const __origFetch = window.fetch;
window.fetch = function(input, init){
  const url = String((input && input.url) || input || '');
  const pair = url.match(/^https:\/\/api\.frankfurter\.dev\/v2\/rate\/([A-Z]{3})\/([A-Z]{3})$/);
  if (pair && pair[1]+pair[2] !== 'USDBRL') {
    window.__fxInFlight++;
    const payload = {base: pair[1], quote: pair[2], date:'2026-09-14', rate:window.__fxGateRate};
    return new Promise(resolve => {
      window.__fxPending.push(() => resolve(new Response(
        JSON.stringify(payload),
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
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block')
    install_bootstrap(ctx)
    ctx.add_init_script(GATE)
    page = ctx.new_page()
    erros = []
    page.on('pageerror', lambda e: erros.append(str(e)))
    page.goto(url, wait_until='load')
    # Finish the automatic producer before opening a fresh manual gate. Clearing
    # its pending resolver array would strand the same coalesced in-flight batch.
    page.wait_for_function("() => window.JPWForex?.marketQuotes?.get().busy && __fxPending.length===Object.keys(JPWForex.marketQuotes.pairs).length")
    page.evaluate("""async() => {
      const bootUpdate=updateFxRates();
      __fxRelease();
      await bootUpdate;
    }""")
    page.wait_for_function("() => !JPWForex.marketQuotes.get().busy && __fxPending.length===0")
    wait_bootstrap(page)
    page.evaluate("""() => {
      closeModal();
      window.alert = () => {};
      window.prompt = () => 'APAGAR';
      window.confirm = () => true;
    }""")
    page.jpwealth_erros = erros
    page.jpwealth_ctx = ctx
    return page

def disparar_fx(page, rate):
    """Dispara updateFxRates e devolve só quando o fetch estiver comprovadamente em voo."""
    page.evaluate("""rate => {
      if(JPWForex.marketQuotes.get().busy || __fxPending.length)throw Error('Previous quote producer is still active');
      window.__fxDone = false;
      window.__fxInFlight = 0;
      window.__fxGateRate = rate;
      Promise.resolve(updateFxRates()).then(() => { window.__fxDone = true; });
    }""", rate)
    # destrava por estado observável: o fetch já foi emitido
    page.wait_for_function("() => __fxPending.length===Object.keys(JPWForex.marketQuotes.pairs).length && JPWForex.marketQuotes.get().busy")

def liberar_e_aguardar(page):
    """Libera as respostas retidas e espera TODA a continuação assíncrona terminar."""
    page.evaluate("window.__fxRelease()")
    page.wait_for_function("window.__fxDone === true")
    page.wait_for_function("() => !JPWForex.marketQuotes.get().busy && __fxPending.length===0")

def chave(page):
    return page.evaluate(f"localStorage.getItem({json.dumps(LSKEY)})")

def run_suite(browser, url, rotulo):
    # ---- A. uso normal: FX continua atualizando e persistindo ----
    page = open_page(browser, url)
    page.evaluate("S.onboarding={...S.onboarding, done:true}; save()")
    antes = page.evaluate("structuredClone(S.instruments)")
    disparar_fx(page, 1.3456)
    liberar_e_aguardar(page)
    assert page.evaluate("structuredClone(S.instruments)") == antes, f'[{rotulo}] A: referência diária não sobrescreve catálogo/preço manual'
    gravado = json.loads(chave(page))
    referencias=gravado['forex']['dailyReferences']['quotes']
    assert len(referencias)==8 and all(q['rate']==1.3456 and q['referenceDate']=='2026-09-14' and
        q['source']=='Frankfurter' and q['sourceKind']=='DAILY_REFERENCE' and key==q['base']+q['quote'] for key,q in referencias.items()), \
        f'[{rotulo}] A: uso normal deve persistir referências identificadas'
    assert gravado['forex']['dailyReferences']==page.evaluate('S.forex.dailyReferences'), f'[{rotulo}] A: read-back do lote deve coincidir'

    # ---- B. wipe durante o fetch: o wipe vence, a continuação antiga não regrava ----
    disparar_fx(page, 1.4567)
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
    instrumentos_novo_ciclo=page.evaluate('structuredClone(S.instruments)')
    disparar_fx(page, 1.5678)
    liberar_e_aguardar(page)
    depois = json.loads(chave(page))
    assert depois['forex']['dailyReferences']['quotes']['EURUSD']['rate']==1.5678 and depois['forex']['dailyReferences']==page.evaluate('S.forex.dailyReferences'), \
        f'[{rotulo}] C: FX iniciada DEPOIS do wipe deve persistir normalmente'
    assert depois['instruments']==instrumentos_novo_ciclo==page.evaluate('structuredClone(S.instruments)'), f'[{rotulo}] C: catálogo preservado'
    assert not page.jpwealth_erros, page.jpwealth_erros
    assert_fixture_requests(page.jpwealth_ctx)
    page.jpwealth_ctx.close()

    # ---- D. recuperação: continua bloqueando gravação, sem regressão ----
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block')
    install_bootstrap(ctx)
    ctx.add_init_script(GATE)
    ctx.add_init_script(
        "try{localStorage.setItem(%s,'{\"params\":{\"saldoIni\":1');}catch(e){}" % json.dumps(LSKEY))
    page = ctx.new_page()
    page.goto(url, wait_until='load')
    page.wait_for_function("() => window.JPWForex?.marketQuotes && jpWealthLoadRecoveryActive() && !JPWForex.marketQuotes.get().busy")
    page.evaluate("() => { closeModal(); window.alert=()=>{}; window.prompt=()=>'APAGAR'; }")
    assert page.evaluate("jpWealthLoadRecoveryActive()") is True, f'[{rotulo}] D: recuperação deveria estar ativa'
    assert page.evaluate("save()") is False, f'[{rotulo}] D: save deve continuar vetado em recuperação'
    bruto = chave(page)
    requests_before=page.evaluate('__fxInFlight')
    blocked=page.evaluate('async()=>await updateFxRates()')
    assert blocked['ok'] is False and blocked['status']=='BLOCKED', f'[{rotulo}] D: produtor deve recusar antes da consulta'
    assert page.evaluate('__fxInFlight')==requests_before==0 and page.evaluate('__fxPending.length')==0, f'[{rotulo}] D: recuperação não deve emitir requisições de referências'
    assert chave(page) == bruto, f'[{rotulo}] D: FX não pode sobrescrever o banco protegido'
    assert_fixture_requests(ctx)
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
    assert_fixture_requests(page.jpwealth_ctx)
    page.jpwealth_ctx.close()

def main():
    server, base = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**launch_options())
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
