#!/usr/bin/env python3
"""Integridade do estado: backup hostil recusado e substituicao de base entre abas.

Quatro contratos que a caca a bugs mostrou quebrados, todos reproduzidos antes de
existir correcao:

1. Backup com agregado de FORMA errada era aceito, gravado no disco e so entao
   quebrava boot() — a base do operador morria sem copia de recuperacao e sem
   aviso, porque migrate() nao lancava e o modo A-005 nao entrava.
2. migrate() nao repunha sub-chaves de S.params. Sem saldoIni o terminal exibia
   "OPERACIONAL NORMAL / COERENTE" com risco aberto real, porque o denominador
   estatutario sumia e o veredito caia no ramo mais permissivo.
3. A importacao de backup nao atravessava as abas: a primeira gravacao da outra
   aba ressuscitava o documento anterior por cima do que o operador restaurara.
NAO INCLUIDO: o achado de que Finalizar Sessao apagaria os Tickets com uma
segunda aba aberta NAO reproduziu aqui — a aba remota grava o documento ja com o
Ticket, com ou sem correcao. Sem reproducao nao ha teste, e sem teste nao ha
correcao: fica registrado em CURRENT-STATE.md em vez de virar codigo por palpite.

Todas as fixtures sao SINTETICAS. Nenhuma credencial real e usada.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = "jpwealth_v9_state"
VIEWPORT = {"width": 1440, "height": 900}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


def abrir(ctx, url):
    page = ctx.new_page()
    page.on("dialog", lambda d: d.accept())
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function("() => typeof S === 'object'")
    return page


def contexto(browser):
    ctx = browser.new_context(viewport=VIEWPORT)
    ctx.add_init_script("window.__onbShown=true;")
    return ctx


# ---------------------------------------------------------------- 1. forma

def run_backup_de_forma_errada_e_recusado(browser, url):
    """Agregado com forma errada e recusado ANTES de tocar em qualquer coisa.

    A ordem antiga era fatal: S=imported e gravacao vinham antes de boot(), entao
    quando a excecao estourava a base original ja nao existia.
    """
    for chave in ("checklist", "accounts", "instruments"):
        ctx = contexto(browser)
        page = abrir(ctx, url)
        avisos = page.evaluate(
            """chave => {
              window.__avisos = [];
              window.alert = m => window.__avisos.push(String(m));
              window.confirm = () => true;
              S.ledger = [{data:'2026-01-01', nota:'FECHAMENTO DO OPERADOR'}];
              save();
              const antes = localStorage.getItem('jpwealth_v9_state');
              const mau = JSON.parse(JSON.stringify(S));
              mau[chave] = {};                       // objeto onde se espera lista
              const f = new File([JSON.stringify(mau)], 'mau.json', {type:'application/json'});
              importFullBackupFile(f);
              return {antes};
            }""",
            chave,
        )
        page.wait_for_timeout(600)
        estado = page.evaluate(
            """a => ({
              avisos: window.__avisos,
              discoIgual: localStorage.getItem('jpwealth_v9_state') === a,
              ledgerIntacto: S.ledger.length === 1 && S.ledger[0].nota === 'FECHAMENTO DO OPERADOR',
            })""",
            avisos["antes"],
        )
        assert any(chave in a for a in estado["avisos"]), (
            f"{chave}: recusa nao mencionou o agregado invalido: {estado['avisos']}"
        )
        assert estado["ledgerIntacto"], f"{chave}: dado do operador foi destruido pela importacao invalida"
        assert estado["discoIgual"], f"{chave}: o disco foi reescrito por um backup recusado"
        ctx.close()


# ---------------------------------------------------------------- 2. params

def run_params_sem_saldo_nao_declara_coerencia(browser, url):
    """Sem o denominador estatutario, o terminal recusa — nao declara COERENTE."""
    ctx = contexto(browser)
    page = abrir(ctx, url)
    page.evaluate(
        """() => {
          const doc = JSON.parse(JSON.stringify(S));
          delete doc.params.saldoIni;
          localStorage.setItem('jpwealth_v9_state', JSON.stringify(doc));
        }"""
    )
    page.reload(wait_until="load")
    page.wait_for_timeout(700)
    recuperacao = page.evaluate(
        "() => typeof jpWealthLoadRecoveryActive === 'function' && jpWealthLoadRecoveryActive()")
    assert recuperacao is True, (
        "estado sem saldoIni nao entrou no modo de recuperacao — o veredito cairia no ramo permissivo"
    )
    ctx.close()


def run_limiares_legados_sao_repostos(browser, url):
    """Limiar normativo ausente volta de DEFAULTS; saldo do operador nao e inventado."""
    ctx = contexto(browser)
    page = abrir(ctx, url)
    page.evaluate(
        """() => {
          const doc = JSON.parse(JSON.stringify(S));
          delete doc.params.vrmN; delete doc.params.vrmHV; delete doc.params.mdd;
          doc.params.saldoIni = 33333;              // dado do operador permanece
          localStorage.setItem('jpwealth_v9_state', JSON.stringify(doc));
        }"""
    )
    page.reload(wait_until="load")
    page.wait_for_timeout(600)
    lido = page.evaluate("() => ({n:S.params.vrmN, hv:S.params.vrmHV, mdd:S.params.mdd, saldo:S.params.saldoIni})")
    canonico = page.evaluate("() => ({n:DEFAULTS.params.vrmN, hv:DEFAULTS.params.vrmHV, mdd:DEFAULTS.params.mdd})")
    assert lido["n"] == canonico["n"] and lido["hv"] == canonico["hv"] and lido["mdd"] == canonico["mdd"], (
        f"limiares nao voltaram do catalogo oficial: {lido} vs {canonico}"
    )
    assert lido["saldo"] == 33333, f"o saldo do operador foi sobrescrito: {lido['saldo']}"
    ctx.close()


# ---------------------------------------------------------------- 3. import

def run_importacao_atravessa_as_abas(browser, url):
    """A base importada nao e revertida pela primeira gravacao da outra aba."""
    ctx = contexto(browser)
    abaA = abrir(ctx, url)
    abaB = abrir(ctx, url)
    abaA.evaluate(
        """() => {
          window.confirm = () => true;
          const doc = JSON.parse(JSON.stringify(S));
          doc.params.saldoIni = 999999;
          const f = new File([JSON.stringify(doc)], 'b.json', {type:'application/json'});
          importFullBackupFile(f);
        }"""
    )
    # A importacao e assincrona (writer lock, DP-2): o primeiro poll pode chegar
    # antes da primeira escrita — o predicado tolera a ausencia transitoria e
    # espera a CONDICAO OBSERVAVEL, sem atraso arbitrario.
    abaA.wait_for_function(
        """() => { const r = localStorage.getItem('jpwealth_v9_state');
                   if (!r) return false;
                   try { return JSON.parse(r).params.saldoIni === 999999; }
                   catch (e) { return false; } }""")
    # A aba remota adota a base importada (handler de difusao faz load()):
    # espera o estado observavel em vez de um timeout.
    abaB.wait_for_function("() => S && S.params && S.params.saldoIni === 999999", timeout=8000)
    abaB.evaluate("() => { save(); }")
    disco = abaB.evaluate("() => JSON.parse(localStorage.getItem('jpwealth_v9_state')).params.saldoIni")
    assert disco == 999999, f"a gravacao da outra aba ressuscitou a base anterior: saldoIni={disco}"
    ctx.close()


def main():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            run_backup_de_forma_errada_e_recusado(browser, url)
            run_params_sem_saldo_nao_declara_coerencia(browser, url)
            run_limiares_legados_sao_repostos(browser, url)
            run_importacao_atravessa_as_abas(browser, url)
            browser.close()
    finally:
        server.shutdown()
    print("STATE INTEGRITY TEST PASS")


if __name__ == "__main__":
    main()
