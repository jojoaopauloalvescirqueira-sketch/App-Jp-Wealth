#!/usr/bin/env python3
"""Bloco F: Clearance | Consolidado | Monitor dividem a linha, e o layout salvo sobrevive.

Duas metades, e a segunda e a que morde.

A VISUAL: os tres cartoes ocupam a MESMA linha no desktop largo, reorganizam-se
na faixa intermediaria e empilham no celular.

A DESTRUTIVA: `exec-lifo-monitor` se dividiu em `exec-consolidado` e
`exec-monitor`. Quem ja personalizou o Execution Board tem 4 ids gravados onde
o validador passa a esperar 5, e dashLayoutValidateScreenWidgets reprova por
TRES caminhos independentes — contagem, id desconhecido, obrigatorio ausente.
Cada um devolve null para a TELA INTEIRA: sem migracao, uma mudanca visual
apagaria silenciosamente toda a personalizacao gravada do operador.

Este teste grava uma preferencia com a forma ANTIGA e exige que ela sobreviva
com a intencao preservada, alem de exigir a linha de tres. Nao reimplementa o
validador: grava, recarrega e le o que o app fez.

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

CHAVE = "jpwealth.ui.widgetLayouts.v6"

# Preferencia com a forma ANTIGA (4 cartoes) e uma escolha nao-padrao que
# precisa sobreviver: o operador jogou o monitor para o TOPO da tela.
PREF_ANTIGA = {
    "version": 6,
    "screens": {
        "exec": {"widgets": [
            {"id": "exec-lifo-monitor",    "zone": "main", "size": "full", "order": 0},
            {"id": "exec-clearance",       "zone": "main", "size": "full", "order": 1},
            {"id": "exec-phase-grids",     "zone": "main", "size": "full", "order": 2},
            {"id": "exec-metrics-banners", "zone": "main", "size": "full", "order": 3},
        ]}
    },
}


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


def abrir(browser, url, pref=None, largura=1440):
    context = browser.new_context(viewport={"width": largura, "height": 1000})
    context.add_init_script("window.__onbShown=true;")
    if pref is not None:
        context.add_init_script(
            "try{localStorage.setItem(%s, %s);}catch(_){}"
            % (json.dumps(CHAVE), json.dumps(json.dumps(pref))))
    page = context.new_page()
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function("() => typeof S === 'object' && typeof dashLayoutApplyScreen === 'function'")
    return context, page


# Le a ORDEM e o TAMANHO efetivos dos cartoes do Execution Board direto do DOM,
# depois de o motor de grade ter reparenteado tudo no boot.
LER_CARTOES = """
() => [...document.querySelectorAll('#execWidgetGrid > [data-layout-card]')]
        .map(el => ({ id: el.dataset.layoutCard, size: el.dataset.widgetSize }))
"""

# Navega ate o Painel Operacional pelos controles REAIS, como o operador faria:
# o grid nasce `hidden` e quem o revela e o controlador de sub-view. Forcar
# display na mao mediria uma geometria que o app nunca produz.
def ir_para_o_painel(page):
    """Navega ate o Painel Operacional pelos controles REAIS, como o operador.

    O grid nasce `hidden` e quem o revela e o controlador de sub-view. Forcar
    display na mao mediria uma geometria que o app nunca produz.
    """
    page.click('[data-dash-go="exec"]')
    page.wait_for_selector("#exec.active", state="attached")
    # A mesma porta que o submenu usa: JPWExec.ui.selectView. Os botoes de
    # sub-view vivem num menu recolhido e nao sao clicaveis de cara — o teste do
    # submenu ja navega assim.
    page.evaluate("() => window.JPWExec.ui.selectView('panel')")
    page.wait_for_function(
        "() => { const g = document.getElementById('execWidgetGrid');"
        "  return !!g && !g.hidden && g.getBoundingClientRect().width > 0; }")


# Geometria real: onde cada cartao caiu depois do layout aplicado.
LER_GEOMETRIA = """
() => {
  const g = document.getElementById('execWidgetGrid');
  const alvo = ['exec-clearance','exec-consolidado','exec-monitor'];
  return alvo.map(id => {
    const el = g.querySelector(`[data-layout-card="${id}"]`);
    if (!el) return { id, ausente: true };
    const r = el.getBoundingClientRect();
    return { id, topo: Math.round(r.top), esq: Math.round(r.left), larg: Math.round(r.width) };
  });
}
"""


def run_migracao_preserva_personalizacao(page, falhas):
    """A preferencia ANTIGA sobrevive: nem e descartada, nem e reinterpretada."""
    cartoes = page.evaluate(LER_CARTOES)
    ids = [c["id"] for c in cartoes]

    if "exec-consolidado" not in ids or "exec-monitor" not in ids:
        falhas.append(f"os dois cartoes novos nao chegaram ao DOM: {ids}")
        return

    # A personalizacao era: o cartao dividido vinha ANTES do Clearance. Se a
    # migracao falhasse, o validador devolveria null e a tela cairia no PADRAO,
    # onde o Clearance e o primeiro. Esta e a assercao que separa as duas coisas.
    if ids.index("exec-consolidado") >= ids.index("exec-clearance"):
        falhas.append(
            "a personalizacao gravada foi perdida: o cartao dividido estava ANTES"
            f" do Clearance e voltou para depois — ordem efetiva {ids}."
            " Isto e o layout padrao, nao o do operador")

    # O Monitor nasce imediatamente depois do Consolidado, nao em lugar aleatorio.
    if ids.index("exec-monitor") != ids.index("exec-consolidado") + 1:
        falhas.append(
            f"o Monitor nao nasceu logo apos o Consolidado: {ids}")

    # O TAMANHO e coagido de proposito, nao herdado. O cartao antigo declarava
    # data-widget-allowed-sizes="full": `full` era o UNICO valor possivel, ou
    # seja, a ausencia de escolha. Herda-lo congelaria os dois cartoes em
    # largura cheia e a linha de tres nunca apareceria para quem personalizou
    # qualquer outra coisa da tela. A POSICAO, essa sim escolha real, foi
    # preservada logo acima.
    tam = {c["id"]: c["size"] for c in cartoes}
    for cid in ("exec-consolidado", "exec-monitor"):
        if tam.get(cid) != "compact":
            falhas.append(
                f"{cid} deveria ser coagido para 'compact' na migracao;"
                f" veio '{tam.get(cid)}' — herdou o 'full' que ninguem escolheu")

    # Nenhum cartao se perdeu no caminho.
    esperados = {"exec-clearance", "exec-consolidado", "exec-monitor",
                 "exec-phase-grids", "exec-metrics-banners"}
    if set(ids) != esperados:
        falhas.append(f"conjunto de cartoes mudou: {sorted(set(ids))}")


def run_padrao_monta_a_linha_de_tres(page, falhas):
    """Sem preferencia salva, o padrao novo poe os tres na primeira linha."""
    cartoes = {c["id"]: c["size"] for c in page.evaluate(LER_CARTOES)}
    esperado = {"exec-clearance": "medium", "exec-consolidado": "compact", "exec-monitor": "compact"}
    for cid, size in esperado.items():
        if cartoes.get(cid) != size:
            falhas.append(f"padrao: {cid} deveria nascer '{size}'; veio '{cartoes.get(cid)}'")

    geo = page.evaluate(LER_GEOMETRIA)
    if any(g.get("ausente") for g in geo):
        falhas.append(f"cartao ausente na geometria: {geo}")
        return

    topos = {g["topo"] for g in geo}
    if len(topos) != 1:
        falhas.append(
            "a 1440px os tres cartoes deveriam dividir UMA linha; caíram em topos"
            f" diferentes: {[(g['id'], g['topo']) for g in geo]}")

    esqs = [g["esq"] for g in geo]
    if len(set(esqs)) != 3 or esqs != sorted(esqs):
        falhas.append(
            f"os tres deveriam estar lado a lado, da esquerda para a direita: {esqs}")

    clear = next(g for g in geo if g["id"] == "exec-clearance")
    outros = [g for g in geo if g["id"] != "exec-clearance"]
    if not all(clear["larg"] > o["larg"] for o in outros):
        falhas.append(
            "o Clearance ocupa 2 das 4 colunas e deveria ser mais largo que os"
            f" outros dois: {[(g['id'], g['larg']) for g in geo]}")


def run_faixa_intermediaria_reorganiza(page, falhas):
    """A 1100px a linha se REORGANIZA, nao encolhe.

    Dois cartoes de 1 coluna a essa largura cairiam para ~140px, que e a zona
    em que dado financeiro trunca — o defeito ja documentado na faixa de
    metricas. Entao o Clearance toma a largura inteira e o Consolidado e o
    Monitor dividem a linha seguinte.
    """
    geo = {g["id"]: g for g in page.evaluate(LER_GEOMETRIA)}
    if any(g.get("ausente") for g in geo.values()):
        falhas.append(f"cartao ausente na faixa intermediaria: {geo}")
        return
    clear, cons, mon = geo["exec-clearance"], geo["exec-consolidado"], geo["exec-monitor"]
    if clear["topo"] >= cons["topo"]:
        falhas.append(
            "a 1100px o Clearance deveria ficar SOZINHO na primeira linha;"
            f" topos: clearance={clear['topo']} consolidado={cons['topo']}")
    if cons["topo"] != mon["topo"]:
        falhas.append(
            "a 1100px o Consolidado e o Monitor deveriam dividir a MESMA linha;"
            f" topos {cons['topo']} e {mon['topo']}")
    if cons["esq"] >= mon["esq"]:
        falhas.append(f"ordem invertida na faixa intermediaria: {cons['esq']} / {mon['esq']}")
    if not (cons["larg"] > 200 and mon["larg"] > 200):
        falhas.append(
            "a reorganizacao existe justamente para os cartoes nao encolherem;"
            f" larguras {cons['larg']} e {mon['larg']}")


def run_empilha_no_celular(page, falhas):
    geo = page.evaluate(LER_GEOMETRIA)
    if any(g.get("ausente") for g in geo):
        falhas.append(f"cartao ausente no celular: {geo}")
        return
    topos = [g["topo"] for g in geo]
    if len(set(topos)) != 3:
        falhas.append(f"a 480px os tres deveriam empilhar, um por linha: {topos}")
    esqs = {g["esq"] for g in geo}
    if len(esqs) != 1:
        falhas.append(f"empilhados, deveriam alinhar na mesma margem: {esqs}")


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            navegador = pw.chromium.launch()

            ctx, page = abrir(navegador, url, pref=PREF_ANTIGA)
            run_migracao_preserva_personalizacao(page, falhas)
            ctx.close()

            ctx, page = abrir(navegador, url)
            ir_para_o_painel(page)
            run_padrao_monta_a_linha_de_tres(page, falhas)
            ctx.close()

            ctx, page = abrir(navegador, url, largura=1100)
            ir_para_o_painel(page)
            run_faixa_intermediaria_reorganiza(page, falhas)
            ctx.close()

            ctx, page = abrir(navegador, url, largura=480)
            ir_para_o_painel(page)
            run_empilha_no_celular(page, falhas)
            ctx.close()

            navegador.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("PASS  linha de tres no desktop, empilhada no celular, personalizacao gravada preservada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
