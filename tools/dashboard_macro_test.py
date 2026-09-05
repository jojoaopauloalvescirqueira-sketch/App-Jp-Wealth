#!/usr/bin/env python3
"""DASH-MACRO-01 — Visao Executiva Macro do Dashboard.

Prova que o Dashboard resume os quatro modulos globais consumindo a fronteira
canonica de cada dominio, sem reproduzir formula, sem escrever estado e sem
transformar recusa em zero. Cobre tambem a regressao CA-12 da marca: acionar o
logo JA ESTANDO no Dashboard permanece correto e nao escreve em storage.

Invariantes centrais:
  PARTIAL     != total conhecido
  UNAVAILABLE != R$ 0
  BLOCKING    != 0 posicoes
  cache nulo  != 0 eventos
E o motor de layout permanece intocado: #gdDashMain conserva exatamente os
mesmos [data-layout-card], e a preferencia salva do operador sobrevive.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

CARDS = [
    ("forex", "forex-overview", "exec"),
    ("personal-finance", "personal-finance", "finpes"),
    ("research", "research-forex", "research"),
    ("alladin", "alladin", "alladin"),
]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


def launch_browser(playwright):
    candidates = [
        os.environ.get("JP_WEALTH_CHROMIUM", ""),
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    executable = next((item for item in candidates if item and Path(item).exists()), None)
    options = {"headless": True, "args": ["--no-sandbox"]}
    if executable:
        options["executable_path"] = executable
    return playwright.chromium.launch(**options)


def boot(browser, url, viewport=None):
    context = browser.new_context(viewport=viewport or {"width": 1440, "height": 900})
    context.add_init_script("window.__onbShown = true;")
    page = context.new_page()
    observed = {"pageerror": [], "console": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.on("console", lambda msg: observed["console"].append(msg.text) if msg.type == "error" else None)
    # Origens externas sao servidas inertes: abortar produziria ERR_FAILED e
    # esvaziaria a assercao de "zero erro de console".
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => window.JPWDashMacro && window.JPWNavigation "
        "&& document.querySelectorAll('#dashMacroGrid [data-dm-card]').length === 4"
    )
    return context, page, observed


def storage_snapshot(page):
    return page.evaluate("() => JSON.stringify({...localStorage})")


# ---------------------------------------------------------------- ESTRUTURA --

def assert_estrutura_e_isolamento_do_layout(page):
    """Os quatro cards existem, e a camada macro esta FORA do motor de layout."""
    dados = page.evaluate("""() => {
      const shell = document.getElementById('dashMacro');
      const grid = document.getElementById('dashMacroGrid');
      const main = document.getElementById('gdDashMain');
      return {
        existe: !!shell && !!grid,
        dentroDoDash: !!document.querySelector('#dash #dashMacro'),
        // a prova do isolamento: a secao NAO esta dentro do container governado
        dentroDoGdDashMain: !!(main && main.contains(shell)),
        dentroDoGdDashGrid: !!document.querySelector('#gdDashGrid #dashMacro'),
        // nenhum card macro pode carregar o atributo que o motor enumera
        cardsComLayoutCard: document.querySelectorAll('#dashMacro [data-layout-card]').length,
        ordens: [...document.querySelectorAll('#dashMacroGrid [data-dm-card]')].map(c => c.dataset.dmCard),
        focoDeterministico: !!document.querySelector('#dash [data-route-focus]'),
      };
    }""")
    assert dados["existe"], "a secao macro nao foi renderizada"
    assert dados["dentroDoDash"], "a secao macro precisa viver dentro de #dash"
    assert not dados["dentroDoGdDashMain"], f"macro dentro do container governado: {dados}"
    assert not dados["dentroDoGdDashGrid"], f"macro dentro de #gdDashGrid: {dados}"
    assert dados["cardsComLayoutCard"] == 0, f"card macro com [data-layout-card]: {dados}"
    assert dados["ordens"] == [c[0] for c in CARDS], f"cards/ordem divergentes: {dados}"
    assert dados["focoDeterministico"], "#dash sem destino de foco deterministico"


# O conjunto EM RUNTIME, nao o do HTML estatico: 12-global-dashboard.js realoca
# operational-clearance, quick-actions e onboarding-alert para dentro do grid no
# boot. Congelar os seis aqui e o que denuncia se DASH-MACRO-01 acrescentar,
# remover ou renomear qualquer widget governado pelo motor de layout.
GDDASHMAIN_RUNTIME = sorted([
    "institutional-panel", "news-high-impact", "onboarding-alert",
    "operational-clearance", "quick-actions", "vrm",
])


def assert_migracao_forex_fatia2(page):
    """Fatia 2: a profundidade de Forex saiu do Dashboard e vive em execOverview.

    Sem duplicacao: cada bloco existe em UM lugar so. E a migracao nao pode ter
    arrastado widget persistido nenhum — se tivesse, seria N2 disfarcada de N1.
    """
    r = page.evaluate("""() => {
      const q = s => document.querySelectorAll(s).length;
      return {
        analiseNoDash: q('#dash .gd-analysis-grid'),
        metodologiaNoDash: q('#dash #dashMethodology'),
        analiseNoExec: q('#execOverview .gd-analysis-grid'),
        metodologiaNoExec: q('#execOverview #dashMethodology'),
        // nada migrado pode carregar o atributo que o motor de layout enumera
        layoutCardsNoExecOverview: q('#execOverview [data-layout-card]'),
        // #dStatus e lido SEM guard em 03-main-render.js:293 — remove-lo derruba render()
        dStatus: q('#dStatus'),
        // os tres atalhos operacionais acompanharam o dominio
        atalhosForexNoExec: q('#execOverview [data-dash-go]'),
        atalhosForexNoDash: q('#dash [data-dash-go]'),
      };
    }""")
    assert r["analiseNoDash"] == 0, f"Evolucao/Ritmo ainda no Dashboard: {r}"
    assert r["metodologiaNoDash"] == 0, f"Metodologia ainda no Dashboard: {r}"
    assert r["analiseNoExec"] == 1, f"Evolucao/Ritmo nao chegou a Visao Geral: {r}"
    assert r["metodologiaNoExec"] == 1, f"Metodologia nao chegou a Visao Geral: {r}"
    assert r["layoutCardsNoExecOverview"] == 0, f"widget persistido migrado — isso seria N2: {r}"
    assert r["dStatus"] == 1, f"#dStatus perdido — render() quebraria: {r}"
    assert r["atalhosForexNoExec"] == 3, f"atalhos operacionais nao migraram: {r}"
    assert r["atalhosForexNoDash"] == 0, f"atalho de Forex remanescente no Dashboard: {r}"


def assert_gddashmain_intacto(page):
    """O conjunto de widgets personalizaveis nao muda por causa desta feature."""
    ids = page.evaluate(
        "() => [...document.querySelectorAll('#gdDashMain > [data-layout-card]')]"
        ".map(el => el.dataset.layoutCard).sort()"
    )
    assert ids == GDDASHMAIN_RUNTIME, f"#gdDashMain foi alterado: {ids} != {GDDASHMAIN_RUNTIME}"
    # nenhum id da camada macro pode ter vazado para o motor de layout
    vazou = [i for i in ids if i in {c[0] for c in CARDS}]
    assert not vazou, f"id da visao macro entrou no motor de layout: {vazou}"


def assert_preferencia_de_layout_sobrevive(page):
    """Uma preferencia ja gravada continua valida: nada de migracao silenciosa."""
    r = page.evaluate("""() => {
      const chaves = Object.keys(localStorage).filter(k => k.includes('widget') || k.includes('layout'));
      const antes = chaves.map(k => [k, localStorage.getItem(k)]);
      window.JPWDashMacro.render();
      const depois = chaves.map(k => [k, localStorage.getItem(k)]);
      return { igual: JSON.stringify(antes) === JSON.stringify(depois), chaves };
    }""")
    assert r["igual"], f"render alterou preferencia de layout: {r}"


# ------------------------------------------------------------------ LEITURA --

def assert_render_nao_escreve(page):
    antes = storage_snapshot(page)
    page.evaluate("() => window.JPWDashMacro.render()")
    page.evaluate("() => window.JPWNavigation.navigate('dashboard')")
    assert storage_snapshot(page) == antes, "render/navegacao escreveu em storage"


def assert_navegacao_dos_ctas(page):
    """Cada CTA leva a rota canonica do seu modulo, pelo roteador oficial."""
    for card, rota, tela in CARDS:
        # O caso real: o operador esta NO Dashboard e aciona o atalho. Partir de
        # outra tela deixaria o CTA oculto — #dash perde .active e o botao some.
        page.evaluate("() => window.JPWNavigation.navigate('dashboard')")
        page.wait_for_timeout(80)
        antes = storage_snapshot(page)
        page.locator(f"#dashMacroGrid [data-dm-card='{card}'] .dm-cta").click()
        page.wait_for_timeout(120)
        estado = page.evaluate("""() => ({
          screen: document.querySelector('#appMain > .screen.active')?.id || null,
          canonical: window.JPWNavigation.current().canonical,
        })""")
        assert estado["screen"] == tela, f"[{card}] tela errada: {estado}"
        assert estado["canonical"] == rota, f"[{card}] rota canonica errada: {estado}"
        assert storage_snapshot(page) == antes, f"[{card}] a navegacao escreveu em storage"
    page.evaluate("() => window.JPWNavigation.navigate('dashboard')")


# --------------------------------------------------------------- SEMANTICA ---

def assert_pf_unidade_desconhecida(page):
    """Unidade nao reconhecida recusa montantes — nunca presume moeda padrao."""
    r = page.evaluate("""() => {
      const original = S.personalFinance.moneyUnit;
      S.personalFinance.moneyUnit = 'DOGE_WEI';
      window.JPWDashMacro.render();
      const card = document.querySelector("[data-dm-card='personal-finance']");
      const txt = card.innerText;
      const out = { temRS: txt.includes('R$'), recusa: !!card.querySelector('.dm-blocked') };
      S.personalFinance.moneyUnit = original;
      window.JPWDashMacro.render();
      return out;
    }""")
    assert r["recusa"], f"unidade desconhecida deveria recusar integralmente: {r}"
    assert not r["temRS"], f"imprimiu R$ sob unidade desconhecida: {r}"


def assert_alladin_blocking_nao_vira_zero(page):
    """Schema futuro => indisponibilidade explicita, jamais '0 posicoes'."""
    r = page.evaluate("""() => {
      const original = S.alladin.schemaVersion;
      S.alladin.schemaVersion = 999;
      window.JPWDashMacro.render();
      const card = document.querySelector("[data-dm-card='alladin']");
      const txt = card.innerText;
      const out = {
        bloqueado: !!card.querySelector('.dm-blocked'),
        indisponivel: txt.toLowerCase().includes('indispon'),
        dizZeroPosicoes: /\\b0\\s+posi/i.test(txt),
        dizNenhuma: txt.toLowerCase().includes('nenhuma posi'),
      };
      S.alladin.schemaVersion = original;
      window.JPWDashMacro.render();
      return out;
    }""")
    assert r["bloqueado"], f"BLOCKING deveria ter superficie propria: {r}"
    assert r["indisponivel"], f"BLOCKING deveria dizer indisponivel: {r}"
    assert not r["dizZeroPosicoes"], f"BLOCKING virou '0 posicoes': {r}"
    assert not r["dizNenhuma"], f"BLOCKING virou 'nenhuma posicao': {r}"


def assert_pf_mes_virtual(page):
    """Mes nao materializado declara-se nao registrado — sem sobra R$ 0."""
    r = page.evaluate("""() => {
      const M = pfCurrentMonthKey();
      const met = pfCompMetrics(M);
      const card = document.querySelector("[data-dm-card='personal-finance']");
      const txt = card.innerText;
      return { materializado: met.materializado, declaraNaoRegistrado: txt.includes('não registrado'), txt };
    }""")
    if not r["materializado"]:
        assert r["declaraNaoRegistrado"], f"mes virtual deveria declarar-se nao registrado: {r['txt'][:200]}"


def assert_isolamento_de_falha(page):
    """Falha de um dominio nao derruba os outros tres cards."""
    r = page.evaluate("""() => {
      const original = window.JPWAlladin.compat;
      window.JPWAlladin = Object.assign({}, window.JPWAlladin, {
        compat: () => { throw new Error('falha sintetica'); }
      });
      window.JPWDashMacro.render();
      const out = {
        total: document.querySelectorAll('#dashMacroGrid [data-dm-card]').length,
        forexOk: !!document.querySelector("[data-dm-card='forex'] .dm-row"),
        alladinDegradado: !!document.querySelector("[data-dm-card='alladin'] .dm-blocked"),
      };
      window.JPWAlladin = Object.assign({}, window.JPWAlladin, { compat: original });
      window.JPWDashMacro.render();
      return out;
    }""")
    assert r["total"] == 4, f"uma falha derrubou a grade: {r}"
    assert r["forexOk"], f"falha do Alladin contaminou o Forex: {r}"
    assert r["alladinDegradado"], f"falha deveria virar estado rotulado: {r}"


# -------------------------------------------------------------- CA-12 MARCA --

def assert_marca_estando_no_dashboard(page):
    """CA-12: acionar o logo JA no Dashboard permanece correto e nao escreve.

    Regressao da navegacao existente — a implementacao da marca nao e tocada.
    """
    for rotulo, acionar in (
        ("clique", lambda: page.locator("#brandHomeBtn").click()),
        ("Enter", lambda: (page.locator("#brandHomeBtn").focus(), page.keyboard.press("Enter"))),
        ("Espaco", lambda: (page.locator("#brandHomeBtn").focus(), page.keyboard.press(" "))),
    ):
        page.evaluate("() => window.JPWNavigation.navigate('dashboard')")
        antes_estado = page.evaluate("() => window.JPWNavigation.current().canonical")
        assert antes_estado == "dashboard", f"[{rotulo}] o caso exige partir DO dashboard"
        antes_storage = storage_snapshot(page)
        acionar()
        page.wait_for_timeout(120)
        depois = page.evaluate("""() => ({
          screen: document.querySelector('#appMain > .screen.active')?.id || null,
          ativos: [...document.querySelectorAll('#appMain > .screen.active')].map(e => e.id),
          canonical: window.JPWNavigation.current().canonical,
          macro: document.querySelectorAll('#dashMacroGrid [data-dm-card]').length,
        })""")
        assert depois["screen"] == "dash", f"[{rotulo}] saiu do dashboard: {depois}"
        assert depois["ativos"] == ["dash"], f"[{rotulo}] mais de uma tela ativa: {depois}"
        assert depois["canonical"] == "dashboard", f"[{rotulo}] rota canonica: {depois}"
        assert depois["macro"] == 4, f"[{rotulo}] a visao macro se perdeu: {depois}"
        assert storage_snapshot(page) == antes_storage, f"[{rotulo}] escreveu em storage"


# ------------------------------------------------------------ RESPONSIVIDADE --

def assert_responsividade(browser, url):
    # DASH-MACRO-02A Fatia 1: desktop e 2x2 (2 colunas x 2 linhas), nao 1x4.
    # tablet e mobile colapsam para uma coluna — o breakpoint e 1100px.
    for rotulo, viewport, empilhado in (
        ("desktop", {"width": 1440, "height": 900}, False),
        ("tablet", {"width": 900, "height": 1000}, True),
        ("mobile", {"width": 390, "height": 844}, True),
    ):
        context, page, observed = boot(browser, url, viewport=viewport)
        try:
            r = page.evaluate("""() => {
              const cards = [...document.querySelectorAll('#dashMacroGrid [data-dm-card]')];
              const tops = new Set(cards.map(c => Math.round(c.getBoundingClientRect().top)));
              return {
                overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                colunas: tops.size,
                total: cards.length,
                cabem: cards.every(c => c.getBoundingClientRect().width <= document.documentElement.clientWidth),
              };
            }""")
            assert r["overflowX"] == 0, f"[{rotulo}] overflow horizontal: {r}"
            assert r["cabem"], f"[{rotulo}] card mais largo que a viewport: {r}"
            if empilhado:
                assert r["colunas"] == r["total"], f"[{rotulo}] cards nao empilharam: {r}"
            else:
                # 2x2: quatro cards em exatamente DUAS linhas distintas
                assert r["colunas"] == 2, f"[{rotulo}] esperado 2x2, veio {r['colunas']} linha(s): {r}"
            assert not observed["pageerror"], f"[{rotulo}] {observed}"
        finally:
            context.close()


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            context, page, observed = boot(browser, url)
            try:
                assert_estrutura_e_isolamento_do_layout(page)
                assert_migracao_forex_fatia2(page)
                assert_gddashmain_intacto(page)
                assert_preferencia_de_layout_sobrevive(page)
                assert_render_nao_escreve(page)
                assert_navegacao_dos_ctas(page)
                assert_pf_unidade_desconhecida(page)
                assert_pf_mes_virtual(page)
                assert_alladin_blocking_nao_vira_zero(page)
                assert_isolamento_de_falha(page)
                assert_marca_estando_no_dashboard(page)
                assert not observed["pageerror"], observed
                assert not observed["console"], observed
            finally:
                context.close()
            assert_responsividade(browser, url)
            browser.close()
    finally:
        server.shutdown()
    print("DASHBOARD MACRO TEST PASS — quatro cards, layout isolado, semantica fail-closed, CA-12 e responsividade")


if __name__ == "__main__":
    main()
