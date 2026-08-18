#!/usr/bin/env python3
"""As quatro fases sao desenhadas ao mesmo tempo, e a fase futura nao vira editavel.

O painel mostrava so a grade ativa: as anteriores ficavam atras de um botao e as
POSTERIORES nao existiam no DOM. O operador nao enxergava a estrutura
quadrifasica inteira.

Isto e APRESENTACAO. O risco real da mudanca nao e estetico, e de contrabando:
phaseBodyHTML calcula readOnly como isMigrada||frozen||isFechada, e
phaseFrozen(pi) e `pi<3 && phaseUnlocked[pi+1]` — para uma fase AINDA NAO
liberada isso da FALSO, ou seja, os campos viriam HABILITADOS. Desenhar o corpo
de uma fase futura deixaria lancar ordem numa fase que o Estatuto nao liberou.

Este teste prova as duas metades: as quatro aparecem, e a futura nao ganhou
nenhum controle. Nao reimplementa criterio de desbloqueio algum — le
phaseUnlocked antes e depois do render e exige que o desenho nao o toque.

Todas as fixtures sao SINTETICAS.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import sys
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
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof S === 'object' && typeof renderPhases === 'function'"
        " && typeof getMaxUnlockedIdx === 'function'")
    return context, page, erros


# Le o painel DEPOIS de renderizar, sem tocar em estado. Devolve, por cartao:
# indice, rotulo do crachao, se tem corpo com controles, e se tem botao MIGRAR.
LER_PAINEL = """
() => {
  const antes = JSON.stringify(S.phaseUnlocked);
  renderPhases();
  const depois = JSON.stringify(S.phaseUnlocked);
  const cont = document.getElementById('phaseContainer');
  const cartoes = [...cont.querySelectorAll('.phase[data-phase]')].map(el => {
    const corpo = el.querySelector('.phase-body');
    const controles = corpo ? [...corpo.querySelectorAll('input,select,textarea,button')] : [];
    return {
      idx: +el.dataset.phase,
      cracha: (el.querySelector('.badge')||{}).textContent || '',
      ativa: !!el.querySelector('.here'),
      controles: controles.length,
      habilitados: controles.filter(c => !c.disabled).length,
      texto: el.textContent || ''
    };
  });
  return {
    antes, depois,
    ativaIdx: getMaxUnlockedIdx(),
    cartoes,
    migrar: [...cont.querySelectorAll('[data-migrate]')].map(b => +b.dataset.migrate)
  };
}
"""


def montar(page, liberadas):
    """liberadas = quantas fases o Estatuto ja liberou (1..4)."""
    page.evaluate(
        """(n) => {
            S.phaseUnlocked = [true, n >= 2, n >= 3, n >= 4];
            S.quarantine = null;
        }""",
        liberadas,
    )


def checar(page, liberadas, falhas):
    montar(page, liberadas)
    r = page.evaluate(LER_PAINEL)
    rot = f"[{liberadas} fase(s) liberada(s)]"

    # 1. as QUATRO estao no DOM, na ordem F1 -> F4.
    idxs = [c["idx"] for c in r["cartoes"]]
    if idxs != [0, 1, 2, 3]:
        falhas.append(f"{rot} esperava as 4 fases na ordem 0,1,2,3; veio {idxs}")
        return
    crachas = [c["cracha"].strip() for c in r["cartoes"]]
    if crachas != ["F1", "F2", "F3", "F4"]:
        falhas.append(f"{rot} crachas fora de ordem: {crachas}")

    # 2. a grade ATIVA e exatamente a que getMaxUnlockedIdx aponta, e e unica.
    ativas = [c["idx"] for c in r["cartoes"] if c["ativa"]]
    if ativas != [r["ativaIdx"]]:
        falhas.append(
            f"{rot} grade ativa deveria ser so [{r['ativaIdx']}]; veio {ativas}")

    # 3. FASE FUTURA NAO GANHOU CONTROLE NENHUM — o coracao do teste.
    for c in r["cartoes"]:
        if c["idx"] > r["ativaIdx"] and c["controles"] != 0:
            falhas.append(
                f"{rot} fase futura {c['idx']} veio com {c['controles']} controle(s)"
                f" ({c['habilitados']} habilitado(s)): o desenho abriu edicao"
                " numa fase que o Estatuto nao liberou")

    # 4. fase ANTERIOR continua desenhada e read-only (nenhum campo habilitado).
    for c in r["cartoes"]:
        if c["idx"] < r["ativaIdx"] and c["habilitados"] != 0:
            falhas.append(
                f"{rot} fase anterior {c['idx']} tem {c['habilitados']} campo(s)"
                " habilitado(s): historico deixou de ser read-only")

    # 5. MIGRAR so existe preso a grade ativa, e so quando ha proxima fase.
    esperado = [r["ativaIdx"]] if r["ativaIdx"] < 3 else []
    if r["migrar"] != esperado:
        falhas.append(f"{rot} botoes MIGRAR esperados {esperado}; veio {r['migrar']}")

    # 6. DESENHAR NAO MEXE EM ESTADO NORMATIVO.
    if r["antes"] != r["depois"]:
        falhas.append(
            f"{rot} renderPhases alterou phaseUnlocked: {r['antes']} -> {r['depois']}")


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            navegador = pw.chromium.launch()
            contexto, page, erros = prepare_page(navegador, url)
            for liberadas in (1, 2, 3, 4):
                checar(page, liberadas, falhas)
            if erros:
                falhas.append(f"erro de pagina durante o render: {erros}")
            contexto.close()
            navegador.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("PASS  quatro fases simultaneas; futura sem controle; phaseUnlocked intacto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
