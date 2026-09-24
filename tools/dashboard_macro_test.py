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
O resumo macro continua fora do layout: dois cartões ficam em #gdDashMain
e quatro em Forex, preservando os seis registros da preferência v6.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

CARDS = [
    ("forex", "forex-consolidated", "fxconsolidated"),
    ("personal-finance", "personal-finance", "finpes"),
    ("research", "research-forex", "research"),
    ("alladin", "alladin", "alladin"),
]


class Quiet(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".md": "text/markdown"}

    def log_message(self, *_args):
        pass


class BrowserFixtureServer(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True


def serve():
    server = BrowserFixtureServer(("127.0.0.1", 0), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/index.html"


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


def boot(browser, url, viewport=None, *, service_workers="allow", prepare_context=None, alladin_active=False):
    context = browser.new_context(viewport=viewport or {"width": 1440, "height": 900}, service_workers=service_workers)
    # Apenas cenários que entram no Alladin solicitam a fixture ativa.
    if alladin_active:
        context.add_init_script("localStorage.setItem('jpw_module_availability_v1',JSON.stringify({schemaVersion:1,modules:{alladin:'active'}}));")
    if prepare_context is not None:
        prepare_context(context)
    context.add_init_script("window.__onbShown = true;")
    page = context.new_page()
    observed = {"pageerror": [], "console": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.on("console", lambda msg: observed["console"].append(msg.text) if msg.type == "error" else None)
    # Origens externas sao servidas inertes: abortar produziria ERR_FAILED e
    # esvaziaria a assercao de "zero erro de console".
    if prepare_context is None:
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


# Projeção física do Dashboard após realocação; compatibilidade v6 tem teste focal.
GDDASHMAIN_RUNTIME = sorted(["institutional-panel", "quick-actions"])


def assert_migracao_forex_fatia2(page):
    """Fatia 2: a profundidade de Forex saiu do Dashboard e vive em execOverview.

    Sem duplicação: quatro widgets operacionais na Visão Geral, dois no Dashboard.
    """
    r = page.evaluate("""() => {
      const q = s => document.querySelectorAll(s).length;
      const OPERACIONAIS = ['motor', 'check', 'params'];
      return {
        analiseNoDash: q('#dash .gd-analysis-grid'),
        metodologiaNoDash: q('#dash #dashMethodology'),
        analiseNoExec: q('#execOverview .gd-analysis-grid'),
        metodologiaNoExec: q('#execOverview #dashMethodology'),
        // quatro cartões operacionais únicos na projeção Forex
        layoutCardsNoExecOverview: q('#execOverview [data-layout-card]'),
        // #dStatus e lido SEM guard em 03-main-render.js:293 — remove-lo derruba render()
        dStatus: q('#dStatus'),
        // Os três atalhos locais permanecem na Visão Geral.
        atalhosForexNoExec: q(OPERACIONAIS.map(k => `#execOverview [data-dash-go="${k}"]`).join(',')),
        atalhosForexNoDash: q(OPERACIONAIS.map(k => `#dash [data-dash-go="${k}"]`).join(',')),
        // O CTA legado do hero permanece; cockpit abre a operação em Forex.
        ctaAbrirForexNoDash: q('#dash [data-dash-go="exec"][data-route="forex-consolidated"]'),
      };
    }""")
    assert r["analiseNoDash"] == 0, f"Evolucao/Ritmo ainda no Dashboard: {r}"
    assert r["metodologiaNoDash"] == 0, f"Metodologia ainda no Dashboard: {r}"
    assert r["analiseNoExec"] == 1, f"Evolucao/Ritmo nao chegou a Visao Geral: {r}"
    assert r["metodologiaNoExec"] == 1, f"Metodologia nao chegou a Visao Geral: {r}"
    assert r["layoutCardsNoExecOverview"] == 4, f"projeção Forex incorreta: {r}"
    assert r["dStatus"] == 1, f"#dStatus perdido — render() quebraria: {r}"
    assert r["atalhosForexNoExec"] == 3, f"atalhos operacionais nao migraram: {r}"
    assert r["atalhosForexNoDash"] == 0, f"atalho operacional remanescente no Dashboard: {r}"
    assert r["ctaAbrirForexNoDash"] == 1, f"CTA legado incorreto: {r}"


def assert_gddashmain_intacto(page):
    """Somente os dois cartões remanescentes ficam no container físico Dashboard."""
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
        cta = page.locator(f"#dashMacroGrid [data-dm-card='{card}'] .dm-cta")
        cta.focus()
        cta.press("Enter")
        page.wait_for_timeout(120)
        estado = page.evaluate("""() => ({
          screen: document.querySelector('#appMain > .screen.active')?.id || null,
          canonical: window.JPWNavigation.current().canonical,
          focusInScreen: !!document.querySelector('#appMain > .screen.active')?.contains(document.activeElement),
          focusVisible: !!document.activeElement?.getClientRects().length,
        })""")
        assert estado["screen"] == tela, f"[{card}] tela errada: {estado}"
        assert estado["canonical"] == rota, f"[{card}] rota canonica errada: {estado}"
        assert estado["focusInScreen"] and estado["focusVisible"], f"[{card}] foco perdido ao navegar por teclado: {estado}"
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
        forexOk: !!document.querySelector("[data-dm-card='forex']") &&
          /selecion|conta|período|indispon/i.test(document.querySelector("[data-dm-card='forex']").innerText),
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

SURFACE_GEOMETRY = """() => {
  const $=s=>document.querySelector(s),style=(e,pseudo)=>getComputedStyle(e,pseudo);
  const visible=e=>!!e&&!!e.getClientRects().length&&style(e).visibility!=='hidden';
  const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
  const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
  const rgba=value=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=value;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data]};
  const background=e=>{for(let n=e;n;n=n.parentElement){const c=rgba(style(n).backgroundColor);if(c[3]===255)return c}return [255,255,255,255]};
  const border=(e,side)=>({width:parseFloat(style(e)['border'+side+'Width']),style:style(e)['border'+side+'Style'],color:rgba(style(e)['border'+side+'Color'])});
  const logo=$('.gd-logo'),header=$('body > header'),sidebar=$('#appSidebar');
  // A trilha estrutural do shell desenha a divisória até o fim do documento;
  // a barra interativa continua sem borda própria para não encerrar a linha
  // na altura da viewport.
  const rail=style(document.body,'::before');
  const railBorder={width:parseFloat(rail.borderRightWidth),style:rail.borderRightStyle,color:rgba(rail.borderRightColor),display:rail.display};
  return {
    viewport:innerWidth,client:document.documentElement.clientWidth,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
    zoom:parseFloat(style(document.documentElement).zoom)||1,theme:document.documentElement.dataset.theme,
    navigation:document.documentElement.dataset.navigation,rail:document.documentElement.dataset.rail,shell:document.documentElement.dataset.shell,
    grid:box($('#dashMacroGrid')),canvas:background($('#appMain')),panel:rgba(style(document.documentElement).getPropertyValue('--panel')),
    header:box(header),headerBorder:border(header,'Bottom'),sidebar:visible(sidebar)?box(sidebar):null,sidebarBorder:visible(sidebar)?border(sidebar,'Right'):null,sidebarRailBorder:railBorder,
    logo:{...box(logo),naturalWidth:logo.naturalWidth,naturalHeight:logo.naturalHeight},brand:box($('#brandHomeBtn')),
    actions:[...header.querySelectorAll('.header-actions button,[data-shell-menu-toggle]')].filter(visible).map(e=>({id:e.id||e.getAttribute('aria-label'),...box(e)})),
    cards:[...document.querySelectorAll('#dashMacroGrid [data-dm-card]')].map(card=>({id:card.dataset.dmCard,...box(card),background:rgba(style(card).backgroundColor),border:['Top','Right','Bottom','Left'].map(s=>border(card,s)),
      radius:parseFloat(style(card).borderTopLeftRadius),padding:['Top','Right','Bottom','Left'].map(s=>parseFloat(style(card)['padding'+s])),
      scroll:card.scrollWidth,client:card.clientWidth,head:box(card.querySelector('.dm-card-head')),body:box(card.querySelector('.dm-body')),
      bodyColumns:style(card.querySelector('.dm-body')).gridTemplateColumns.split(' ').length,
      elements:[...card.querySelectorAll('.dm-title,.dm-eyebrow,.dm-cta,.dm-note,.dm-empty,.dm-row,.dm-fact,.dm-event,.dm-link,.dm-partial,.dm-blocked')].filter(visible).map(e=>({tag:e.className,...box(e),scroll:e.scrollWidth,client:e.clientWidth}))}))
  };
}"""


def assert_superficies_dashboard(page, rotulo):
    """Limites de composição aprovados; texto multilinha não tem teto de altura."""
    r = page.evaluate(SURFACE_GEOMETRY)
    z = r['zoom']
    def inside(child, parent):
        return child['x'] >= parent['x']-1 and child['right'] <= parent['right']+1 and child['y'] >= parent['y']-1 and child['bottom'] <= parent['bottom']+1
    assert r['overflow'] <= 1, f'[{rotulo}] overflow horizontal da página: {r["overflow"]}'
    assert len(r['cards']) == 4, f'[{rotulo}] quatro painéis obrigatórios'
    previous = None
    for card in r['cards']:
        assert card['w'] >= r['grid']['w']*.98 and abs(card['x']-r['grid']['x']) <= 1, f'[{rotulo}] painel não ocupa a grade: {card}'
        assert card['right'] <= r['client']+1 and card['scroll'] <= card['client']+1, f'[{rotulo}] painel excede a área útil: {card}'
        if previous:
            gap = (card['y']-previous['bottom'])/z
            assert 12 <= gap <= (32 if r['viewport'] <= 900 else 40), f'[{rotulo}] empilhamento/gap incoerente: {gap}'
        previous = card
        assert 8 <= card['radius'] <= 20 and all(12 <= p <= 32 for p in card['padding']), f'[{rotulo}] raio/padding desproporcionais: {card}'
        assert all(.5 <= b['width'] <= 1.5 and b['style']=='solid' for b in card['border']), f'[{rotulo}] contorno do painel perdido: {card}'
        assert card['background'][3] == 255 and max(abs(a-b) for a,b in zip(card['background'],r['panel'])) <= 2, f'[{rotulo}] superfície difere do token panel: {card["background"]}, {r["panel"]}'
        assert sum(abs(a-b) for a,b in zip(card['background'][:3],r['canvas'][:3])) >= 8, f'[{rotulo}] painel indistinto do canvas'
        assert inside(card['head'],card) and inside(card['body'],card), f'[{rotulo}] cabeçalho/corpo escapam do painel: {card}'
        for element in card['elements']:
            assert inside(element,card) and element['scroll'] <= element['client']+1, f'[{rotulo}] texto/controle cortado: {element}'
        if r['viewport'] >= 1201 and z == 1:
            assert card['bodyColumns'] >= 2, f'[{rotulo}] resumo largo perdeu distribuição horizontal: {card["id"]}'
    line = r['headerBorder']
    assert .5 <= line['width'] <= 1.5 and line['style']=='solid' and line['color'][3] > 0, f'[{rotulo}] divisória horizontal ausente: {line}'
    if r['sidebar'] and r['viewport'] > 900 and r['navigation']=='sidebar':
        # A fixture também cobre a composição antiga, onde a trilha não é
        # montada. Quando presente, a linha estrutural é a referência visual;
        # fora dela, a borda do aside continua sendo o contrato legado.
        uses_structural_rail = r['shell']=='global-dashboard' and r['sidebarRailBorder']['width'] > 0
        side = r['sidebarRailBorder'] if uses_structural_rail else r['sidebarBorder']
        assert side['width'] == line['width'] and side['style']==line['style'] and side['color']==line['color'], f'[{rotulo}] divisórias não são coerentes: {line}, {side}'
        if uses_structural_rail:
            assert r['sidebarBorder']['width'] == 0, f'[{rotulo}] barra interativa não deve duplicar a trilha: {r["sidebarBorder"]}'
            assert side['display'] != 'none', f'[{rotulo}] trilha estrutural da barra lateral ausente: {side}'
        expected = 76 if r['rail']=='collapsed' else 252
        assert abs(r['sidebar']['w']/z-expected) <= 1, f'[{rotulo}] largura lateral alterada: {r["sidebar"]}'
    logo = r['logo']
    assert logo['naturalWidth'] > 0 and logo['naturalHeight'] > 0, f'[{rotulo}] ativo da marca não carregou'
    assert abs((logo['w']/logo['h'])/(logo['naturalWidth']/logo['naturalHeight'])-1) <= .02, f'[{rotulo}] marca distorcida: {logo}'
    assert (16 if r['viewport'] > 900 else 11) <= logo['h']/z <= 20, f'[{rotulo}] escala da marca fora da proposta: {logo}'
    assert inside(logo,r['brand']) and inside(r['brand'],r['header']), f'[{rotulo}] marca cortada: {logo}'
    for action in r['actions']:
        assert inside(action,r['header']) and action['right'] <= r['client']+1, f'[{rotulo}] ação global cortada: {action}'
        overlap = min(logo['right'],action['right'])-max(logo['x'],action['x'])
        assert overlap <= 1 or min(logo['bottom'],action['bottom']) <= max(logo['y'],action['y']), f'[{rotulo}] marca colide com ação global: {action}'
    return r


def assert_responsividade(browser, url):
    # DASHBOARD-SURFACES-01 substitui apenas o contrato 2x2 por quatro painéis.
    from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
    cases = [(w,t,'sidebar','expanded',1,False) for w in (320,390,601,768,900,1024,1440) for t in ('light','dark')]
    cases += [(w,t,'topbar','expanded',1,False) for w in (320,901,1024,1100,1440) for t in ('light','dark')]
    cases += [(1440,t,'sidebar','collapsed',1,False) for t in ('light','dark')]
    cases += [(w,t,'sidebar','expanded',1.25,True) for w in (390,1440) for t in ('light','dark')]
    evidence = Path(os.environ['JPW_DASHBOARD_EVIDENCE']).resolve() if os.environ.get('JPW_DASHBOARD_EVIDENCE') else None
    if evidence:
        assert not evidence.is_relative_to(ROOT), 'Evidência deve ficar fora do produto'
        evidence.mkdir(parents=True,exist_ok=False)
    results = []
    for width, theme, navigation, rail, zoom, long in cases:
        rotulo = f'{width}-{theme}-{navigation}-{rail}-csszoom{zoom}-long{int(long)}'
        def prepare(context):
            install_bootstrap(context)
            context.add_init_script('localStorage.setItem("jpw_nav_layout",'+json.dumps(navigation)+');localStorage.setItem("jpw_rail",'+json.dumps(rail)+');')
        context, page, observed = boot(browser, url, viewport={'width':width,'height':1000}, service_workers='block',prepare_context=prepare)
        result = {'case':rotulo,'result':'NOT_RUN','zoom_limit':'CSS zoom stress; not browser-native zoom proof'}
        results.append(result)
        try:
            wait_bootstrap(page)
            page.evaluate("theme=>{S.theme=theme;applyTheme();renderThemeSeg();JPWNavigation.navigate('dashboard');}",theme)
            page.wait_for_function("document.querySelector('.gd-logo').complete&&document.querySelector('.gd-logo').naturalWidth>0")
            assert page.evaluate('document.documentElement.dataset.navigation') == navigation
            assert page.locator('#themeSeg button.on').get_attribute('data-theme-val') == theme
            if zoom != 1:
                page.evaluate('z=>document.documentElement.style.zoom=String(z)',zoom)
            if long:
                page.evaluate("""() => {
                  for(const e of document.querySelectorAll('#dashMacro .dm-title'))e.textContent+=' — resumo sintético com identificação extensa';
                  for(const e of document.querySelectorAll('#dashMacro .dm-cta'))e.textContent+=' · consultar detalhes do módulo';
                }""")
            before = page.evaluate('JSON.stringify({state:S,storage:Object.entries(localStorage).sort()})')
            result['geometry'] = assert_superficies_dashboard(page,rotulo)
            if evidence:
                page.screenshot(path=str(evidence/(rotulo+'.png')),full_page=True)
            brand = page.locator('#brandHomeBtn')
            brand.focus()
            page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
            focus = brand.evaluate("e=>({active:e===document.activeElement,visible:e.matches(':focus-visible'),width:parseFloat(getComputedStyle(e).outlineWidth),style:getComputedStyle(e).outlineStyle})")
            # Chromium quantiza outlineWidth em CSS zoom; comparar pixels renderizados.
            assert focus['active'] and focus['visible'] and focus['width']*zoom >= 2 and focus['style'] != 'none', f'[{rotulo}] marca perdeu foco visível: {focus}'
            brand.press('Enter')
            assert page.evaluate('JPWNavigation.current().canonical') == 'dashboard'
            if width <= 900 and zoom == 1:
                toggle = page.locator('[data-shell-menu-toggle]')
                toggle.click()
                drawer = page.locator('#nav' if navigation=='topbar' else '#appSidebar')
                drawer_box = drawer.bounding_box()
                assert drawer.get_attribute('aria-modal') == 'true' and drawer_box and drawer_box['x'] >= -1 and drawer_box['x']+drawer_box['width'] <= width+1, f'[{rotulo}] gaveta não cabe na viewport'
                page.keyboard.press('Escape')
                assert toggle.get_attribute('aria-expanded') == 'false'
                page.wait_for_function("document.activeElement.matches('[data-shell-menu-toggle]')")
            assert page.evaluate('JSON.stringify({state:S,storage:Object.entries(localStorage).sort()})') == before, f'[{rotulo}] navegação da marca escreveu estado/preferências'
            assert not observed['pageerror'], f'[{rotulo}] {observed}'
            assert not observed['console'], f'[{rotulo}] {observed}'
            assert_fixture_requests(context)
            result['result'] = 'PASS'
            print('DASHBOARD SURFACES PASS '+rotulo,flush=True)
        except Exception as error:
            result['result'] = 'PRODUCT_FAIL' if isinstance(error,AssertionError) else 'TEST_HARNESS_FAIL'
            result['error'] = str(error)
            raise
        finally:
            if evidence:
                result['geometry_at_exit'] = page.evaluate(SURFACE_GEOMETRY)
                if not (evidence/(rotulo+'.png')).exists():
                    page.screenshot(path=str(evidence/(rotulo+'.png')),full_page=True)
                (evidence/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
            context.close()


def assert_atualizacao_agenda_e_foco(page):
    """Regressão real: cache muda, hook do feed deve atualizar o macro aberto."""
    page.evaluate("""() => {
      JPWNavigation.navigate('dashboard');
      const btn=document.querySelector('[data-dm-card="research"] .dm-cta');
      btn.focus();
      ffNewsWriteCache({version:1,generated_at:new Date().toISOString(),events:[
        {title:'Agenda <img src=x onerror="window.__dmXss=1">',country:'USD',
         date:new Date(Date.now()+60000).toISOString(),impact:'High'}]});
      ffNewsRenderAll();
    }""")
    page.wait_for_function("() => document.querySelector('[data-dm-card=research]').textContent.includes('Agenda <img')")
    r=page.evaluate("""() => ({
      foco:document.activeElement.matches('[data-dm-card="research"] .dm-cta'),
      xss:!!window.__dmXss, imgs:document.querySelectorAll('[data-dm-card="research"] img').length
    })""")
    assert r=={'foco':True,'xss':False,'imgs':0},r
    # Render geral também atualiza a macro, sem saída e reentrada.
    page.evaluate("""() => {
      S.accounts=[{forexAccountId:'MACRO_A',nome:'Mestre sintética',tipo:'MESTRE',platformCurrency:'USD'}];
      S.forex=JPWForex.state.empty();
      const p={periodId:'MACRO_P',accountId:'MACRO_A',startedAt:'2026-01-01',currency:'USD',si:12000,
        openingBook:12000,source:'synthetic macro',revision:1,activeOperation:null,
        phases:JPWForex.state.newOperationPhases(),ledger:[{accountId:'MACRO_A',periodId:'MACRO_P',currency:'USD',
          data:'2026-01-02',saldo:12345,resultado:345}],ledgerEvents:[]};
      S.forex.accountContexts={schemaVersion:1,revision:1,accounts:{MACRO_A:{accountId:'MACRO_A',
        currentPeriodId:'MACRO_P',periods:{MACRO_P:p}}},archivedAccounts:{},legacy:null};render();
    }""")
    page.wait_for_function("() => document.querySelector('[data-dm-card=forex]').textContent.includes('02/01/2026')")
    page.evaluate("() => { S.forex.accountContexts.accounts.MACRO_A.periods.MACRO_P.ledger.pop(); render(); }")


def assert_fuso_agenda(browser,url):
    ctx=browser.new_context(viewport={'width':1440,'height':900},timezone_id='America/Sao_Paulo',service_workers='block')
    try:
        page=ctx.new_page()
        page.add_init_script('window.__onbShown=true;')
        page.route('**/*',lambda route: route.continue_() if '127.0.0.1' in route.request.url else route.fulfill(status=200,content_type='application/json',body='{}'))
        page.goto(url,wait_until='load')
        page.wait_for_function('() => !!window.JPWDashMacro')
        r=page.evaluate("""() => {
          const now=Date.now;Date.now=()=>Date.parse('2026-09-08T12:00:00Z');
          ffNewsWriteCache({version:1,events:[{title:'Evento UTC',country:'USD',impact:'High',date:'2026-09-09T01:00:00Z'}]});
          JPWDashMacro.render();
          const text=document.querySelector('[data-dm-card=research]').textContent;
          Date.now=now;
          return text.includes('08/09/2026 · 22:00')&&!text.includes('09/09/2026');
        }""")
        assert r, 'data e horário divergiram no fuso local'
    finally:
        ctx.close()


def assert_links_profundos(page):
    routes=[('finpes','mensal','finpes'),('finpes','dividas','finpes'),
            ('finpes','comparativo','finpes'),('finpes','cenarios','finpes'),
            ('research','calendar','tools'),('research','nocoda','research'),
            ('research','pivots','research'),('alladin','balances','alladin'),
            ('alladin','ledger','alladin'),('alladin','positions','alladin')]
    for surface,view,screen in routes:
        page.evaluate("() => JPWNavigation.navigate('dashboard')")
        page.locator(f'#dashMacro [data-dm-surface="{surface}"][data-dm-view="{view}"]').click()
        assert page.locator(f'#{screen}').evaluate("el=>el.classList.contains('active')")
        if surface=='alladin':
            assert page.locator(f'[data-alladin-panel="{view}"]').is_visible()
        else:
            actual_surface="tools" if surface=="research" and view=="calendar" else surface
            actual=page.evaluate("s=>s==='finpes'?JPWFin.ui.getView():s==='tools'?JPWTools.ui.getView():JPWResearch.ui.getView()",actual_surface)
            assert actual==view,(surface,view,actual)
            current=page.evaluate("() => JPWNavigation.current().localView")
            assert current=={'surface':actual_surface,'view':view}, current

    page.evaluate("() => JPWNavigation.navigate('dashboard')")


def assert_resumos_preenchidos(browser,url):
    from alladin_ui_tx_reverse_test import SEMEAR
    from finpes_comparison_test import seed_completo
    ctx,page,observed=boot(browser,url,service_workers="block",alladin_active=True)
    try:
        # Relógio do DOMÍNIO fixo: meses corrente/anterior e fixtures correspondem.
        page.evaluate("() => { window.__dmMonth=pfCurrentMonthKey; pfCurrentMonthKey=()=> '2026-08'; }")
        page.evaluate("() => {"+seed_completo('2026-07',1400000,1000000)+seed_completo('2026-08',1500000,900000)+"}")
        page.evaluate(SEMEAR)
        page.evaluate("() => JPWNavigation.navigate('dashboard')")
        r=page.evaluate("""() => {
          JPWDashMacro.render();
          const text=id=>document.querySelector('[data-dm-card="'+id+'"]').textContent;
          const balance=JPWAlladin.leitura.saldoDeCaixa(__ids.cx);
          const state=JSON.stringify(S), storage=JSON.stringify({...localStorage});
          JPWDashMacro.render();
          return {balance:text('alladin').includes(JPWAlladin.money.format({amount:balance.amount,currency:balance.currency})),
            last:text('alladin').includes('13/01/2026'),
            compare:text('personal-finance').includes(foSignedMoney(pfCompCompare('2026-08','2026-07').metrics.sobra.delta)),
            unchanged:state===JSON.stringify(S)&&storage===JSON.stringify({...localStorage})};
        }""")
        assert all(r.values()),r
        r=page.evaluate("""() => {
          const st=JPWFx.state;
          const created=st.fxPlanCreate({name:'Plano de teste',assumptions:{startMonth:'2026-01',horizonMonths:24,initialBalanceUsd:1000,defaultMonthlyReturn:0.01,projectedFxRate:5.4}});
          const closed=st.fxPlanRecordActual('2026-01',{inputType:'rate',returnRate:0.02});
          const expected=st.fxOverviewLive();
          const before=JSON.stringify(S);
          JPWDashMacro.render();
          const text=document.querySelector('[data-dm-card=forex]').textContent;
          const valid=created.ok&&closed.ok&&text.includes('Selecione a conta operacional')&&
            !text.includes(fmtMoney2(expected.realizedProfitUsd))&&!text.includes(fmtMoney2(expected.deviationUsd));
          const stable=before===JSON.stringify(S);
          const old=S.fxPlanning.plan.current;delete S.fxPlanning.plan.current;
          const corrupt=JSON.stringify(S);
          JPWDashMacro.render();
          const refused=document.querySelector('[data-dm-card=forex]').textContent.includes('Selecione a conta operacional')&&corrupt===JSON.stringify(S);
          S.fxPlanning.plan.current=old;
          return {valid,stable,refused};
        }""")
        assert all(r.values()),r
        # O retorno parcial de um saldo deve ser mostrado como indisponível.
        # Corrupção real só-caixa, fronteira já caracterizada por E12b.
        r=page.evaluate("""() => {
          const dep=S.alladin.transactions.find(t=>t.transactionId===__ids.dep);
          const original=dep.currency;dep.currency='USD';
          JPWDashMacro.render();
          const text=document.querySelector('[data-dm-card=alladin]').textContent;
          dep.currency=original;
          JPWDashMacro.render();
          return text.includes('Saldo indisponível')&&!text.includes('9.999,99');
        }""")
        assert r,'saldo bloqueado foi apresentado como valor'
        assert not observed['pageerror'],observed
    finally:
        ctx.close()


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            context, page, observed = boot(browser, url, service_workers="block", alladin_active=True)
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
                assert_atualizacao_agenda_e_foco(page)
                assert_links_profundos(page)
                before=storage_snapshot(page)
                page.locator('#dmTools > summary').click()
                assert page.locator('#gdQuickCard').is_visible()
                assert not page.locator('#mcClearanceCard').is_visible()
                assert storage_snapshot(page)==before, 'abrir ferramentas escreveu em storage'
                page.locator('#dmTools > summary').click()

                assert not observed["pageerror"], observed
                assert not observed["console"], observed
            finally:
                context.close()
            assert_responsividade(browser, url)
            assert_resumos_preenchidos(browser,url)
            assert_fuso_agenda(browser,url)
            browser.close()
    finally:
        server.shutdown()
    print("DASHBOARD MACRO TEST PASS — quatro cards, layout isolado, semantica fail-closed, CA-12 e responsividade")


if __name__ == "__main__":
    main()
