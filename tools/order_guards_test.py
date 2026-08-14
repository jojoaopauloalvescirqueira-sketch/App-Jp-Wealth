#!/usr/bin/env python3
"""Guardas de ordem na grade: nenhuma edicao ultrapassa o teto de risco da fase.

O teto consolidado da grade e limite ESTATUTARIO. O ramo de <input> ja o
aplicava a lote, entrada e stop; a troca de PAR escapava da checagem e permitia
ultrapassar o limite sem alerta, sem reversao e sem o questionario de transicao —
o risco em USD de uma ordem depende de cpl e da conversao da moeda de cotacao,
entao trocar o instrumento move o risco tanto quanto trocar o lote.

Este teste NAO reimplementa formula alguma: monta a ordem, dispara a edicao pela
interface real e confere o veredito das funcoes do proprio app.

Todas as fixtures sao SINTETICAS.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


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


def prepare_page(browser, url):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    observed = {"pageerror": []}
    page.on("pageerror", lambda e: observed["pageerror"].append(str(e)))
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function("() => typeof S === 'object' && typeof checkPhaseCap === 'function'")
    return context, page, observed


# Cenario montado para que as guardas ANTERIORES deixem passar e o teto da FASE
# seja quem decide:
#   · uma unica posicao aberta, senao Operacao Unica (Art. 3.6) barra antes;
#   · lote dentro do Teto/Op dos dois instrumentos, senao a Regra 1 barra antes.
MONTA_CENARIO = """() => {
  S.phases.forEach(ph => ph.orders.forEach(o => { o.status='Vazia'; o.par=''; o.lote=0; }));
  const o = S.phases[0].orders[0];
  o.par='USDJPY'; o.status='Aberta'; o.tipo='Compra'; o.lote=0.05; o.entry=1.10; o.sl=1.00;
  save(); renderPhases();
  return {risco: orderRisk(o), teto: phaseTetoRisco(0), par: o.par};
}"""


def instrumenta_confirmacoes(page):
    page.evaluate(
        "() => { window.__avisos = [];"
        "        window.alert = m => { window.__avisos.push(String(m)); };"
        "        window.confirm = m => { window.__avisos.push(String(m)); return false; }; }")


def troca_par(page, destino):
    page.evaluate(
        """d => { const sel = document.querySelector('#phaseContainer select[data-f="par"]');
                  if (!sel) throw new Error('select de par nao encontrado na grade');
                  sel.value = d; sel.dispatchEvent(new Event('change', {bubbles:true})); }""",
        destino,
    )
    page.wait_for_timeout(200)


def run_par_excedente_e_barrado(page):
    """Trocar para um par que estoura o teto da fase: alerta e reversao."""
    base = page.evaluate(MONTA_CENARIO)
    assert base["risco"] < base["teto"], f"pre-condicao: a ordem ja nascia acima do teto ({base})"
    instrumenta_confirmacoes(page)
    troca_par(page, "EURUSD")

    avisos = page.evaluate("() => window.__avisos")
    estado = page.evaluate("() => ({par: S.phases[0].orders[0].par, risco: orderRisk(S.phases[0].orders[0])})")
    assert any("TETO DE RISCO" in a for a in avisos), f"nenhum alerta de teto foi emitido: {avisos}"
    assert estado["par"] == "USDJPY", f"a troca nao foi revertida: par ficou {estado['par']}"
    assert estado["risco"] <= base["teto"], (
        f"risco {estado['risco']} permaneceu acima do teto {base['teto']}"
    )
    # E o limite nao foi contornado por baixo: nenhuma fase destravou sozinha.
    assert page.evaluate("() => JSON.stringify(S.phaseUnlocked)") == "[true,false,false,false]", (
        "a troca de par destravou fase sem o questionario de transicao"
    )
    assert page.evaluate("() => S.transitionLog.length") == 0, "transicao registrada sem questionario"


def run_par_dentro_do_teto_passa(page):
    """Controle: a mesma troca, com lote que cabe no teto, NAO e barrada.

    Sem este caso o teste passaria com uma guarda que recusasse tudo.
    """
    page.evaluate(
        """() => {
          S.phases.forEach(ph => ph.orders.forEach(o => { o.status='Vazia'; o.par=''; o.lote=0; }));
          const o = S.phases[0].orders[0];
          o.par='USDJPY'; o.status='Aberta'; o.tipo='Compra'; o.lote=0.01; o.entry=1.10; o.sl=1.099;
          save(); renderPhases();
        }"""
    )
    instrumenta_confirmacoes(page)
    troca_par(page, "EURUSD")
    avisos = page.evaluate("() => window.__avisos")
    par = page.evaluate("() => S.phases[0].orders[0].par")
    assert not any("TETO DE RISCO" in a for a in avisos), f"troca legitima foi barrada: {avisos}"
    assert par == "EURUSD", f"troca legitima nao foi aplicada: par ficou {par}"


def main():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            run_par_excedente_e_barrado(page)
            run_par_dentro_do_teto_passa(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("ORDER GUARDS TEST PASS")


if __name__ == "__main__":
    main()
