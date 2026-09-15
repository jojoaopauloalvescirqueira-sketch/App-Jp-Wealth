#!/usr/bin/env python3
"""Execution Board: faixas compactas, geometria responsiva e identidade do Editor.

A campanha substitui os tres cartoes altos por faixas de conta, risco e
instrumentos. O nome historico do arquivo permanece porque o gate ja o chama.
As preferencias antigas continuam cobertas: migracao do antigo monitor,
ordem/tamanhos personalizados, nenhum widget perdido, nenhuma regravacao
causada por navegar/renderizar. A geometria exige largura util e conteudo
financeiro sem truncamento, nao apenas a existencia de classes CSS.
Todas as fixtures sao sinteticas; requisicoes externas sao interceptadas.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import sys
import threading

from playwright.sync_api import sync_playwright
import notes_launcher_test as launcher


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
    context = browser.new_context(viewport={"width": largura, "height": 1000}, service_workers="block", reduced_motion="reduce")
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
    page.click('#dashMacro [data-dm-card="forex"] .dm-cta')
    page.wait_for_selector("#fxconsolidated.active", state="attached")
    assert page.evaluate("JPWNavigation.navigate('forex-operation')")
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
    return { id, topo: Math.round(r.top), fundo: Math.round(r.bottom), esq: Math.round(r.left), larg: Math.round(r.width), altura: Math.round(r.height), gridWidth: Math.round(g.getBoundingClientRect().width), minHeight:getComputedStyle(el).minHeight };
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


def run_faixas_compactas(page, falhas, largura):
    """Conta, risco e instrumentos usam faixas com altura natural e leitura inteira."""
    cartoes = {c["id"]: c["size"] for c in page.evaluate(LER_CARTOES)}
    # IDs e metadados do Editor sobrevivem; o CSS adapta a composicao visual.
    esperado = {"exec-clearance": "full", "exec-consolidado": "full", "exec-monitor": "full"}
    for cid, size in esperado.items():
        if cartoes.get(cid) != size:
            falhas.append(f"{largura}px: identidade/tamanho Editor mudou para {cid}: {cartoes.get(cid)}")
    geo = page.evaluate(LER_GEOMETRIA)
    if any(g.get("ausente") for g in geo):
        falhas.append(f"{largura}px: faixa ausente {geo}")
        return
    for index, item in enumerate(geo):
        if item['larg'] < item['gridWidth'] - 3:
            falhas.append(f"{largura}px: {item['id']} nao ocupa a largura util: {item}")
        if item['altura'] <= 0:
            falhas.append(f"{largura}px: faixa invisivel {item}")
        if index and item['topo'] < geo[index-1]['fundo'] - 2:
            falhas.append(f"{largura}px: faixas se sobrepoem ou ainda dividem colunas altas: {geo}")
        if abs(item['esq']-geo[0]['esq']) > 2:
            falhas.append(f"{largura}px: margens desalinhadas {geo}")
        if item['minHeight'] not in ('0px', 'auto'):
            falhas.append(f"{largura}px: {item['id']} conserva altura minima artificial {item['minHeight']}")
    metrics = page.evaluate("""() => [...document.querySelectorAll('.eb-metric > strong')].map(e=>{
      const s=getComputedStyle(e),r=e.getBoundingClientRect();return {text:e.textContent,visible:r.width>0&&r.height>0,
        overflow:s.overflow,textOverflow:s.textOverflow,font:parseFloat(s.fontSize),width:r.width,scroll:e.scrollWidth};})""")
    # Closed diagnostic details are intentionally absent from layout.
    visible=[m for m in metrics if m['visible']]
    if len(visible)<10:
        falhas.append(f"{largura}px: metricas de resumo ausentes/invisiveis: {len(visible)}")
    for m in visible:
        if m['textOverflow']=='ellipsis' or m['overflow']=='hidden' and m['scroll']>m['width']+2:
            falhas.append(f"{largura}px: valor truncado {m}")
        if not 16 <= m['font'] <= 24:
            falhas.append(f"{largura}px: proporcao tipografica do valor fora da faixa: {m}")
    if page.evaluate('document.documentElement.scrollWidth > innerWidth + 2'):
        falhas.append(f"{largura}px: pagina possui overflow horizontal; tabelas devem rolar internamente")


def run_navegacao_preserva_preferencia(page, falhas):
    before=page.evaluate("key=>localStorage.getItem(key)", CHAVE)
    ids_before=page.evaluate(LER_CARTOES)
    ir_para_o_painel(page)
    for _ in range(2):
        page.evaluate("() => {render();renderPhases();JPWNavigation.navigate('dashboard');JPWNavigation.navigate('forex-operation');JPWExec.ui.selectView('panel');}")
    after=page.evaluate("key=>localStorage.getItem(key)", CHAVE)
    if before!=after:
        falhas.append('Navegacao/re-render regravou a preferencia de layout')
    if ids_before!=page.evaluate(LER_CARTOES):
        falhas.append('Navegacao/re-render mudou a ordem ou os tamanhos do Editor')
    ids=page.evaluate("() => ['execClearanceCard','execConsolidadoCard','execLifoMonitor','execPhaseGridsCard','executionBoardAccount','executionBoardRisk','executionBoardInstruments'].map(id=>[id,document.querySelectorAll('#'+id).length])")
    if any(count!=1 for _,count in ids):
        falhas.append(f'IDs duplicados ou ausentes depois da navegacao: {ids}')


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            navegador = pw.chromium.launch(**launcher.launch_options())

            ctx, page = abrir(navegador, url, pref=PREF_ANTIGA)
            run_migracao_preserva_personalizacao(page, falhas)
            run_navegacao_preserva_preferencia(page, falhas)
            ctx.close()

            ctx, page = abrir(navegador, url)
            ir_para_o_painel(page)
            run_faixas_compactas(page, falhas, 1440)
            ctx.close()

            ctx, page = abrir(navegador, url, largura=1100)
            ir_para_o_painel(page)
            run_faixas_compactas(page, falhas, 1100)
            ctx.close()

            ctx, page = abrir(navegador, url, largura=480)
            ir_para_o_painel(page)
            run_faixas_compactas(page, falhas, 480)
            ctx.close()

            navegador.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("PASS  faixas compactas responsivas, valores legiveis, IDs e personalizacao do Editor preservados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
