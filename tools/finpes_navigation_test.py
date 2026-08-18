#!/usr/bin/env python3
"""Navegacao de Financas Pessoais (PF-01, Bloco F).

Prova o checklist minimo do NAVIGATION-HIERARCHY.md para o modulo novo:
menu principal 06, submenu com seis destinos, superficie JPWFin.ui, troca por
hidden+inert com nos MONTADOS, destino inicial, e a doutrina que aqui e tambem
fronteira de dominio: NAVEGAR JAMAIS ESCREVE NO ESTADO — abrir o modulo ou
trocar de workspace nao pode materializar mes nem disparar save().

Inclui a face visivel do sentinela: unidade monetaria desconhecida mostra o
banner de modo leitura; BRL_CENTS nao mostra.

Fixtures sinteticas.
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

LSKEY = "jpwealth_v9_state"
VIEWS = ["overview", "mensal", "dividas", "comparativo", "cenarios", "inventario"]
CONTAINERS = ["finpesOverview", "finpesMensal", "finpesDividas",
              "finpesComparativo", "finpesCenarios", "finpesInventario"]


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


def boot(browser, url, mutacao_js=None):
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
        "() => typeof S === 'object' && window.JPWFin && typeof window.JPWFin.ui.selectView === 'function'")
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => typeof S === 'object' && window.JPWFin && typeof window.JPWFin.ui.selectView === 'function'")
    page.wait_for_timeout(400)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return context, page, erros


def run_estrutura(page, falhas):
    r = page.evaluate(f"""() => {{
        const tab = document.querySelector('#finpesNavTrigger');
        const sub = document.getElementById('finpesNavSubmenu');
        const itens = sub ? [...sub.querySelectorAll('[data-nav-sub-view]')].map(b => b.dataset.navSubView) : [];
        const section = document.getElementById('finpes');
        const filhos = section ? {json.dumps(CONTAINERS)}.map(id => !!document.getElementById(id)) : [];
        return {{
          temTab: !!tab, numero: tab && tab.querySelector('.n') && tab.querySelector('.n').textContent,
          rotulo: tab && tab.querySelector('.lbl') && tab.querySelector('.lbl').textContent,
          dataScreen: tab && tab.dataset.screen,
          temSub: !!sub, itens, temSection: !!section, filhos,
          registrado: typeof NAV_SUBMENU_SURFACES === 'object' ? 'indireto' : 'n/a',
        }};
    }}""")
    if not r["temTab"] or r["dataScreen"] != "finpes":
        falhas.append(f"menu principal 06 ausente ou mal ligado: {r}")
    if r["numero"] != "06" or r["rotulo"] != "Finanças Pessoais":
        falhas.append(f"rotulo/numero errados: {r['numero']} {r['rotulo']}")
    if r["itens"] != VIEWS:
        falhas.append(f"submenu deveria ter exatamente {VIEWS}; veio {r['itens']}")
    if not r["temSection"] or not all(r["filhos"]):
        falhas.append(f"section/workspaces ausentes: {r['filhos']}")
    reg = page.evaluate(
        "() => typeof NAV_SUBMENU_SURFACES==='object' && !!NAV_SUBMENU_SURFACES.finpes"
        " && NAV_SUBMENU_SURFACES.finpes() === window.JPWFin.ui")
    if reg is not True:
        falhas.append("superficie finpes nao registrada no shell (NAV_SUBMENU_SURFACES)")


def run_troca_de_views(page, falhas):
    for view, cont in zip(VIEWS, CONTAINERS):
        r = page.evaluate(f"""() => {{
            const aceito = window.JPWFin.ui.selectView({json.dumps(view)});
            const estados = {json.dumps(CONTAINERS)}.map(id => {{
                const el = document.getElementById(id);
                return {{ id, hidden: el.hidden, inert: el.inert, montado: !!el }};
            }});
            return {{ aceito, atual: window.JPWFin.ui.getView(), estados }};
        }}""")
        if not r["aceito"] or r["atual"] != view:
            falhas.append(f"selectView('{view}') nao aceitou ou getView divergiu: {r['atual']}")
        for e in r["estados"]:
            esperado_oculto = e["id"] != cont
            if not e["montado"]:
                falhas.append(f"{e['id']} foi DESMONTADO na troca — contrato exige nos montados")
            if e["hidden"] != esperado_oculto or e["inert"] != esperado_oculto:
                falhas.append(
                    f"em '{view}': {e['id']} hidden={e['hidden']} inert={e['inert']}, esperava {esperado_oculto}")
    r = page.evaluate("() => window.JPWFin.ui.selectView('inexistente')")
    if r is not False:
        falhas.append("selectView de chave desconhecida deveria devolver false")


def run_navegacao_nao_escreve(page, falhas):
    r = page.evaluate("""() => {
        const antes = JSON.stringify(S.personalFinance);
        const antesTudo = JSON.stringify(S);
        let saves = 0;
        const saveOriginal = window.save;
        window.save = function(){ saves++; return saveOriginal.apply(this, arguments); };
        navigateToScreen('finpes');
        for(const v of ['mensal','dividas','comparativo','cenarios','inventario','overview'])
            window.JPWFin.ui.selectView(v);
        navigateToScreen('dash');
        navigateToScreen('finpes');
        window.save = saveOriginal;
        return { pfIgual: antes === JSON.stringify(S.personalFinance),
                 tudoIgual: antesTudo === JSON.stringify(S),
                 saves };
    }""")
    if not r["pfIgual"]:
        falhas.append("navegar ALTEROU personalFinance — navegacao jamais escreve (nem materializa mes)")
    if not r["tudoIgual"]:
        falhas.append("navegar alterou S em algum agregado")
    if r["saves"] != 0:
        falhas.append(f"navegacao disparou save() {r['saves']}x — render/navegacao nao grava")


def run_destino_inicial(page, falhas):
    # Gestos SEPARADOS, como o usuario real: sair e voltar no mesmo bloco
    # sincrono coalesce as mutacoes de classe num so callback do observer e
    # nao conta como entrada nova (contrato documentado no template do exec).
    page.evaluate("() => window.JPWFin.ui.selectView('cenarios')")
    page.evaluate("() => navigateToScreen('dash')")
    page.wait_for_timeout(80)
    page.evaluate("() => navigateToScreen('finpes')")
    page.wait_for_timeout(80)
    r = page.evaluate("() => window.JPWFin.ui.getView()")
    if r != "overview":
        falhas.append(f"entrada nova no modulo deveria abrir 'overview'; ficou em {r}")


def run_sentinela_visual(browser, url, falhas):
    mut = """
      S.personalFinance = { schemaVersion:1, moneyUnit:'USD_CENTS', months:{},
        recurringIncome:[], debts:[], creditLines:[], scenarios:[] };
    """
    ctx, page, erros = boot(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => {
        navigateToScreen('finpes');
        window.JPWFin.ui.selectView('overview');
        const el = document.getElementById('finpesUnitNotice');
        return { visivel: !!el && !el.hidden,
                 texto: el ? el.textContent : '' };
    }""")
    if not r["visivel"]:
        falhas.append("unidade desconhecida deveria mostrar o banner de modo leitura")
    if "modo leitura" not in r["texto"]:
        falhas.append("banner sem a mensagem de modo leitura")
    ctx.close()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            ctx, page, erros = boot(browser, url)
            run_estrutura(page, falhas)
            run_troca_de_views(page, falhas)
            run_navegacao_nao_escreve(page, falhas)
            run_destino_inicial(page, falhas)
            r = page.evaluate("() => ({ banner: document.getElementById('finpesUnitNotice').hidden })")
            if r["banner"] is not True:
                falhas.append("BRL_CENTS nao deveria mostrar o banner de modo leitura")
            if erros:
                falhas.append(f"pageerror: {erros}")
            ctx.close()

            run_sentinela_visual(browser, url, falhas)
            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES NAVIGATION TEST PASS — menu 06, seis destinos, hidden/inert, navegacao sem escrita, sentinela visual")
    return 0


if __name__ == "__main__":
    sys.exit(main())
