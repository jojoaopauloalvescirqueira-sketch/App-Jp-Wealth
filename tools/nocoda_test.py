#!/usr/bin/env python3
"""Caracterizacao dos Estudos NoCoda: geometria do canal e identidade de instrumento.

Segue o padrao consagrado do projeto para nucleo matematico: sobe a pagina
modular por HTTP, abre em Chromium e chama as funcoes PURAS pela superficie
publica `window.JPWNocoda.geometry`, comparando com tolerancia absoluta. A
matematica nunca e reimplementada aqui — o teste so confere resultados.

Todas as fixtures sao SINTETICAS. O teste nao cria ordem, nao fecha mes, nao
importa backup e nao toca credencial.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

TOL = 1e-10

# Fixture canonica da especificacao. Os valores esperados foram conferidos de
# forma independente antes de existir codigo de producao.
CANON = {
    "anchor1": {"datetime": "2021-01-04T11:00:00", "price": 1.23412},
    "anchor2": {"datetime": "2021-06-08T04:00:00", "price": 1.22513},
    "anchor3": {"datetime": "2021-03-16T08:00:00", "price": 1.17156},
}
CANON_BASE = 1.230001500134662
CANON_SIGNED = -0.058441500134662
CANON_RANGE = 0.058441500134662
CANON_SUBDIV = 0.007305187516833


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


def assert_close(actual, expected, tolerance=TOL, label="valor"):
    assert actual is not None and abs(actual - expected) <= tolerance, (
        f"{label}: esperado {expected!r}, recebido {actual!r} (delta {abs(actual - expected) if actual is not None else 'n/a'})"
    )


def prepare_page(browser, url):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    observed = {"pageerror": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.route(
        "**/*",
        lambda route: route.continue_()
        if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url)
    page.wait_for_function("() => window.JPWNocoda && window.JPWNocoda.geometry")
    return context, page, observed


def geom(page, anchors):
    return page.evaluate("a => window.JPWNocoda.geometry.compute(a)", anchors)


def run_canonical(page):
    """Fixture obrigatoria da especificacao. Se falhar, nada mais importa."""
    g = geom(page, CANON)
    assert g is not None, "geometria canonica devolveu null"
    assert_close(g["basePriceAtThirdAnchor"], CANON_BASE, label="P0AtT3")
    assert_close(g["signedRange"], CANON_SIGNED, label="signedRange")
    assert_close(g["channelRange"], CANON_RANGE, label="channelRange")
    assert_close(g["subdivisionRange"], CANON_SUBDIV, label="subdivisionRange")
    # A subdivisao e exatamente um oitavo do range, nao um valor independente.
    assert_close(g["subdivisionRange"], g["channelRange"] / 8, label="subdivisao = range/8")


def run_wrong_formulas_rejected(page):
    """O range NAO pode ser abs(P3-P1) nem abs(P3-P2) — ambos ignoram a inclinacao."""
    g = geom(page, CANON)
    ingenuo1 = abs(CANON["anchor3"]["price"] - CANON["anchor1"]["price"])
    ingenuo2 = abs(CANON["anchor3"]["price"] - CANON["anchor2"]["price"])
    assert abs(g["channelRange"] - ingenuo1) > 1e-4, (
        f"channelRange coincidiu com abs(P3-P1)={ingenuo1} — projecao temporal nao foi aplicada"
    )
    assert abs(g["channelRange"] - ingenuo2) > 1e-4, (
        f"channelRange coincidiu com abs(P3-P2)={ingenuo2} — projecao temporal nao foi aplicada"
    )


def run_invariants(page):
    """P0(T1)=P1, P0(T2)=P2 e P(-1,T3)=P3 — detectam inversao de sinal."""
    inv = page.evaluate(
        """a => {
          const G = window.JPWNocoda.geometry;
          const t1 = G.parseTime(a.anchor1.datetime);
          const t2 = G.parseTime(a.anchor2.datetime);
          const t3 = G.parseTime(a.anchor3.datetime);
          return {
            atT1: G.projectBasePrice(t1, a.anchor1.price, t2, a.anchor2.price, t1),
            atT2: G.projectBasePrice(t1, a.anchor1.price, t2, a.anchor2.price, t2),
            level0AtT3: G.levelPrice(0, t3, a),
            levelMinus1AtT3: G.levelPrice(-1, t3, a)
          };
        }""",
        CANON,
    )
    assert_close(inv["atT1"], CANON["anchor1"]["price"], label="P0(T1) = P1")
    assert_close(inv["atT2"], CANON["anchor2"]["price"], label="P0(T2) = P2")
    assert_close(inv["level0AtT3"], CANON_BASE, label="P(0,T3) = P0AtT3")
    assert_close(inv["levelMinus1AtT3"], CANON["anchor3"]["price"], label="P(-1,T3) = P3")


def run_horizontal_channel(page):
    """P1 == P2: linha 0 horizontal; o range vira a distancia vertical pura."""
    a = {
        "anchor1": {"datetime": "2021-01-01T00:00:00", "price": 1.10000},
        "anchor2": {"datetime": "2021-02-01T00:00:00", "price": 1.10000},
        "anchor3": {"datetime": "2021-01-15T00:00:00", "price": 1.09000},
    }
    g = geom(page, a)
    assert_close(g["basePriceAtThirdAnchor"], 1.10000, label="linha horizontal em T3")
    assert_close(g["signedRange"], -0.01, label="signedRange horizontal")
    assert_close(g["channelRange"], 0.01, label="channelRange horizontal")
    assert_close(g["subdivisionRange"], 0.00125, label="subdivisao horizontal")


def run_third_anchor_on_base_line(page):
    """Ancora 3 exatamente sobre a linha 0: range zero, subdivisao zero."""
    a = {
        "anchor1": {"datetime": "2021-01-01T00:00:00", "price": 1.00000},
        "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.10000},
        # Metade do intervalo -> a linha 0 vale exatamente 1.05.
        "anchor3": {"datetime": "2021-01-06T00:00:00", "price": 1.05000},
    }
    g = geom(page, a)
    assert_close(g["signedRange"], 0.0, label="signedRange sobre a linha")
    assert_close(g["channelRange"], 0.0, label="channelRange sobre a linha")
    assert_close(g["subdivisionRange"], 0.0, label="subdivisao sobre a linha")


def run_extrapolation(page):
    """T3 antes de T1 e depois de T2 sao legitimos — extrapolacao e permitida."""
    base = {
        "anchor1": {"datetime": "2021-01-01T00:00:00", "price": 1.00000},
        "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.10000},
    }
    antes = dict(base, anchor3={"datetime": "2020-12-27T00:00:00", "price": 0.90000})
    depois = dict(base, anchor3={"datetime": "2021-01-16T00:00:00", "price": 1.20000})
    entre = dict(base, anchor3={"datetime": "2021-01-06T00:00:00", "price": 1.00000})

    g_antes = geom(page, antes)
    assert g_antes is not None, "T3 antes de T1 foi rejeitado indevidamente"
    assert_close(g_antes["basePriceAtThirdAnchor"], 0.95, label="linha 0 extrapolada para tras")
    assert_close(g_antes["signedRange"], -0.05, label="signedRange extrapolado para tras")

    g_depois = geom(page, depois)
    assert g_depois is not None, "T3 depois de T2 foi rejeitado indevidamente"
    assert_close(g_depois["basePriceAtThirdAnchor"], 1.15, label="linha 0 extrapolada para frente")
    assert_close(g_depois["signedRange"], 0.05, label="signedRange extrapolado para frente")

    g_entre = geom(page, entre)
    assert_close(g_entre["basePriceAtThirdAnchor"], 1.05, label="linha 0 interpolada")
    assert_close(g_entre["signedRange"], -0.05, label="signedRange interpolado")


def run_signed_range_signs(page):
    """O sinal distingue de que lado da linha 0 esta a linha -1."""
    base = {
        "anchor1": {"datetime": "2021-01-01T00:00:00", "price": 1.00000},
        "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.00000},
    }
    acima = geom(page, dict(base, anchor3={"datetime": "2021-01-06T00:00:00", "price": 1.02000}))
    abaixo = geom(page, dict(base, anchor3={"datetime": "2021-01-06T00:00:00", "price": 0.98000}))
    assert acima["signedRange"] > 0, f"esperado sinal positivo, veio {acima['signedRange']}"
    assert abaixo["signedRange"] < 0, f"esperado sinal negativo, veio {abaixo['signedRange']}"
    # O modulo e o mesmo dos dois lados; so o sinal muda.
    assert_close(acima["channelRange"], abaixo["channelRange"], label="modulo simetrico")


def run_validation(page):
    """Entradas invalidas sao rejeitadas com erro por campo, nunca em silencio."""
    casos = [
        ("T1 == T2", {
            "anchor1": {"datetime": "2021-01-01T00:00:00", "price": 1.0},
            "anchor2": {"datetime": "2021-01-01T00:00:00", "price": 1.1},
            "anchor3": {"datetime": "2021-01-05T00:00:00", "price": 1.2},
        }),
        ("preco zero", {
            "anchor1": {"datetime": "2021-01-01T00:00:00", "price": 0},
            "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.1},
            "anchor3": {"datetime": "2021-01-05T00:00:00", "price": 1.2},
        }),
        ("preco negativo", {
            "anchor1": {"datetime": "2021-01-01T00:00:00", "price": -1.0},
            "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.1},
            "anchor3": {"datetime": "2021-01-05T00:00:00", "price": 1.2},
        }),
        ("preco vazio", {
            "anchor1": {"datetime": "2021-01-01T00:00:00", "price": ""},
            "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.1},
            "anchor3": {"datetime": "2021-01-05T00:00:00", "price": 1.2},
        }),
        ("data invalida", {
            "anchor1": {"datetime": "nao e data", "price": 1.0},
            "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.1},
            "anchor3": {"datetime": "2021-01-05T00:00:00", "price": 1.2},
        }),
        ("data inexistente", {
            "anchor1": {"datetime": "2021-02-31T00:00:00", "price": 1.0},
            "anchor2": {"datetime": "2021-01-11T00:00:00", "price": 1.1},
            "anchor3": {"datetime": "2021-01-05T00:00:00", "price": 1.2},
        }),
    ]
    for rotulo, a in casos:
        g = geom(page, a)
        assert g is None, f"{rotulo}: geometria deveria ser rejeitada, veio {g}"
        v = page.evaluate("a => window.JPWNocoda.geometry.validate(a)", a)
        assert not v["ok"], f"{rotulo}: validate deveria reprovar"
        assert v["errors"], f"{rotulo}: reprovou sem mensagem de erro"
        assert all(e.get("field") and e.get("message") for e in v["errors"]), (
            f"{rotulo}: erro sem campo ou sem mensagem: {v['errors']}"
        )

    # Nao finitos, que JSON nao transporta: construidos dentro da pagina.
    nao_finitos = page.evaluate(
        """() => {
          const G = window.JPWNocoda.geometry;
          const base = {
            anchor1:{datetime:'2021-01-01T00:00:00', price:1.0},
            anchor2:{datetime:'2021-01-11T00:00:00', price:1.1}
          };
          return {
            nan: G.compute(Object.assign({}, base, {anchor3:{datetime:'2021-01-05T00:00:00', price:NaN}})),
            inf: G.compute(Object.assign({}, base, {anchor3:{datetime:'2021-01-05T00:00:00', price:Infinity}}))
          };
        }"""
    )
    assert nao_finitos["nan"] is None, "NaN aceito como preco"
    assert nao_finitos["inf"] is None, "Infinity aceito como preco"

    # Controle legitimo: a fixture canonica CONTINUA passando na validacao —
    # sem isto, um validador que reprova tudo passaria neste bloco.
    v_ok = page.evaluate("a => window.JPWNocoda.geometry.validate(a)", CANON)
    assert v_ok["ok"], f"caso de controle valido foi reprovado: {v_ok['errors']}"


def run_level_scale(page):
    """Escala -4..+4 por indice inteiro, sem acumular 0,125 em laco."""
    scale = page.evaluate(
        """() => {
          const G = window.JPWNocoda.geometry;
          const levels = [];
          for (let k = 0; k < G.LEVEL_COUNT; k++) levels.push(G.levelAt(k));
          return {
            count: G.LEVEL_COUNT,
            step: G.STEP,
            subdivisions: G.SUBDIVISIONS,
            first: levels[0],
            last: levels[levels.length - 1],
            zeroExact: levels.includes(0),
            minusOneExact: levels.includes(-1),
            // Um laco que acumula +0.125 erra aqui; o indice inteiro nao.
            maxDrift: Math.max(...levels.map((v, k) => Math.abs(v - (-4 + k * 0.125))))
          };
        }"""
    )
    assert scale["count"] == 65, f"esperado 65 niveis, veio {scale['count']}"
    assert scale["subdivisions"] == 8, f"esperado 8 subdivisoes, veio {scale['subdivisions']}"
    assert_close(scale["step"], 0.125, label="passo")
    assert_close(scale["first"], -4.0, label="primeiro nivel")
    assert_close(scale["last"], 4.0, label="ultimo nivel")
    assert scale["zeroExact"], "nivel 0 nao e exato — sinal de acumulacao de ponto flutuante"
    assert scale["minusOneExact"], "nivel -1 nao e exato — sinal de acumulacao de ponto flutuante"
    assert scale["maxDrift"] < 1e-12, f"desvio de {scale['maxDrift']} entre indice e acumulacao"


def run_subdivision_count(page):
    """8 intervalos e 9 niveis entre -1 e 0 — guarda contra off-by-one."""
    faixa = page.evaluate(
        """() => {
          const G = window.JPWNocoda.geometry;
          const dentro = [];
          for (let k = 0; k < G.LEVEL_COUNT; k++) {
            const L = G.levelAt(k);
            if (L >= -1 - 1e-12 && L <= 0 + 1e-12) dentro.push(L);
          }
          return { niveis: dentro.length, intervalos: dentro.length - 1 };
        }"""
    )
    assert faixa["niveis"] == 9, f"esperado 9 niveis entre -1 e 0, veio {faixa['niveis']}"
    assert faixa["intervalos"] == 8, f"esperado 8 intervalos, veio {faixa['intervalos']}"


def run_instrument_identity(page):
    """instrumentId() e a identidade unica; instFor() concorda com ela."""
    ident = page.evaluate(
        """() => ({
          normaliza: ['eur/usd', 'EUR USD', ' eurusd ', 'Eur-Usd'].map(v => instrumentId(v)),
          vazio: [instrumentId(''), instrumentId(null), instrumentId(undefined)],
          catalogoTemId: instrumentCatalog().every(i => i.id === instrumentId(i.name)),
          concordaComInstFor: instrumentCatalog().every(i => {
            const found = instFor(i.name);
            return found && instrumentId(found.name) === i.id;
          }),
          operaveisNaoBanidos: instrumentCatalog().every(i => !(i.banned && !i.unlocked)),
          todosIncluiBanidos: instrumentCatalog({all:true}).length >= instrumentCatalog().length,
          semDuplicata: new Set(instrumentCatalog({all:true}).map(i => i.id)).size
                        === instrumentCatalog({all:true}).length
        })"""
    )
    assert all(v == "EURUSD" for v in ident["normaliza"]), f"normalizacao divergente: {ident['normaliza']}"
    assert all(v == "" for v in ident["vazio"]), f"entrada vazia deveria virar string vazia: {ident['vazio']}"
    assert ident["catalogoTemId"], "catalogo expoe id incoerente com instrumentId()"
    assert ident["concordaComInstFor"], "instrumentCatalog e instFor discordam sobre identidade"
    assert ident["operaveisNaoBanidos"], "catalogo operavel incluiu instrumento banido e travado"
    assert ident["todosIncluiBanidos"], "catalogo {all:true} nao e superconjunto do operavel"
    assert ident["semDuplicata"], "catalogo tem id duplicado"


def run_no_hardcoded_instruments():
    """Nenhum simbolo de instrumento pode estar escrito dentro do dominio NoCoda."""
    alvo = ROOT / "src/js/10-domain/09-nocoda-geometry.js"
    texto = alvo.read_text(encoding="utf-8")
    for simbolo in ("EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY",
                    "USDCHF", "USDCAD", "AUDCAD", "US500", "XAUUSD"):
        assert simbolo not in texto, (
            f"simbolo {simbolo} hardcoded em {alvo.name} — a fonte canonica e S.instruments"
        )


def open_nocoda(page):
    """NAV3-D: alias abre Research/Forex/NoCoda sem falso owner Exec."""
    assert page.evaluate("() => JPWNavigation.navigate('nocoda')") is True
    page.wait_for_function("() => window.JPWResearch.ui.getView() === 'nocoda'")
    state = page.evaluate("""() => ({
      primary:JPWNavigation.current().primary,
      child:JPWNavigation.current().child,
      canonical:JPWNavigation.current().canonical,
      view:JPWNavigation.current().localView,
      execActive:document.getElementById('exec').classList.contains('active')
    })""")
    assert state == {'primary':'research','child':'research-forex','canonical':'research-forex',
                     'view':{'surface':'research','view':'nocoda'},'execActive':False}, state
    page.wait_for_selector("#ncInstrument")


def set_datetime(page, selector, value):
    """Escreve num input datetime-local disparando o mesmo evento de uma tecla.

    `page.fill` NAO serve aqui: ele so aceita 'AAAA-MM-DDTHH:mm' e rejeita
    segundos como 'Malformed value'. E limitacao do Playwright, nao do produto —
    o campo tem step="1" e o navegador aceita segundos de um usuario real. Como
    a especificacao exige resolucao de segundos, o teste escreve o valor e
    dispara 'input', que e exatamente o evento que o bind da tela escuta.
    """
    page.evaluate(
        """([sel, val]) => {
          const el = document.querySelector(sel);
          el.value = val;
          el.dispatchEvent(new Event('input', {bubbles: true}));
        }""",
        [selector, value],
    )


def fill_anchors(page, a):
    """Preenche as seis entradas pelo caminho da aplicacao (dispara os binds)."""
    for n, key in enumerate(("anchor1", "anchor2", "anchor3"), start=1):
        set_datetime(page, f"#ncDate{n}", a[key]["datetime"])
        page.fill(f"#ncPrice{n}", str(a[key]["price"]))


def run_selector_is_derived(page):
    """O seletor deriva do catalogo canonico — sem lista propria."""
    facts = page.evaluate(
        """() => ({
          opcoes: [...document.querySelectorAll('#ncInstrument option')].map(o => o.value),
          catalogo: instrumentCatalog().map(i => i.id)
        })"""
    )
    assert facts["opcoes"] == facts["catalogo"], (
        f"seletor divergiu do catalogo: {facts['opcoes']} vs {facts['catalogo']}"
    )
    assert facts["opcoes"], "seletor vazio"

    # Instrumento novo na fonte canonica aparece sem editar a feature.
    page.evaluate(
        """() => { S.instruments.push({name:'TESTEXYZ', preco:1.5, cpl:100000, teto:0.05, updated:'2026-01-01'}); }"""
    )
    page.evaluate("() => window.JPWNocodaUI.render()")
    depois = page.evaluate("() => [...document.querySelectorAll('#ncInstrument option')].map(o => o.value)")
    assert "TESTEXYZ" in depois, f"instrumento novo do catalogo nao apareceu: {depois}"
    page.evaluate("() => { S.instruments = S.instruments.filter(i => i.name !== 'TESTEXYZ'); }")
    page.evaluate("() => window.JPWNocodaUI.render()")


def run_live_calculation_does_not_persist(page):
    """Calcular nao e salvar: digitar atualiza a previa sem tocar o estado."""
    antes = page.evaluate("() => JSON.stringify(S.nocoda.studies)")
    fill_anchors(page, CANON)
    previa = page.evaluate(
        "() => ({range: ncRange.textContent, sub: ncSubdivision.textContent})"
    )
    assert previa["range"] not in ("—", ""), "previa nao foi calculada ao digitar"
    assert previa["sub"] not in ("—", ""), "subdivisao nao foi calculada ao digitar"
    depois = page.evaluate("() => JSON.stringify(S.nocoda.studies)")
    assert antes == depois, "digitar persistiu estudo sem clique em salvar"


def run_save_and_reload(page):
    """Salvar persiste apenas causas; recarregar recupera e recalcula."""
    alvo = page.evaluate("() => ncInstrument.value")
    page.click("#ncSaveBtn")
    page.wait_for_function("() => document.getElementById('ncStatus').classList.contains('ok')")

    salvo = page.evaluate("id => S.nocoda.studies[id]", alvo)
    assert salvo, "estudo nao foi persistido"
    assert set(salvo.keys()) == {"anchor1", "anchor2", "anchor3", "updatedAt"}, (
        f"estudo persistiu campos alem das causas: {sorted(salvo.keys())}"
    )
    for key in ("channelRange", "subdivisionRange", "signedRange", "basePriceAtThirdAnchor", "levels"):
        assert key not in salvo, f"derivado {key} foi persistido"
    assert_close(salvo["anchor1"]["price"], CANON["anchor1"]["price"], label="preco 1 persistido")
    # Compara o INSTANTE, nao a string: quando os segundos sao zero o proprio
    # navegador normaliza 'T11:00:00' para 'T11:00' no datetime-local. Isso e
    # comportamento padrao do campo, nao perda de dado — o parser aceita as duas
    # formas e produz o mesmo timestamp. A preservacao de segundos NAO nulos e
    # verificada em run_seconds_are_preserved.
    mesmos_instantes = page.evaluate(
        """([salvo, canon]) => {
          const G = window.JPWNocoda.geometry;
          return ['anchor1','anchor2','anchor3'].every(k =>
            G.parseTime(salvo[k].datetime) === G.parseTime(canon[k].datetime));
        }""",
        [salvo, CANON],
    )
    assert mesmos_instantes, f"instante alterado ao salvar: {salvo}"
    primeiro_updated = salvo["updatedAt"]

    page.reload()
    page.wait_for_function("() => window.JPWNocoda && window.JPWNocodaUI")
    open_nocoda(page)
    recuperado = page.evaluate("id => S.nocoda.studies[id]", alvo)
    assert recuperado, "estudo nao sobreviveu ao reload"
    assert recuperado["updatedAt"] == primeiro_updated, "updatedAt mudou sozinho no reload"
    g = page.evaluate("id => window.JPWNocoda.geometry.compute(S.nocoda.studies[id])", alvo)
    assert_close(g["channelRange"], CANON_RANGE, label="range recalculado apos reload")
    assert_close(g["subdivisionRange"], CANON_SUBDIV, label="subdivisao recalculada apos reload")
    return alvo, primeiro_updated


def run_seconds_are_preserved(page):
    """Segundos nao podem ser descartados: mudam o range e sao parte do dado."""
    com_segundos = {
        "anchor1": {"datetime": "2021-01-04T11:00:37", "price": 1.23412},
        "anchor2": {"datetime": "2021-06-08T04:00:11", "price": 1.22513},
        "anchor3": {"datetime": "2021-03-16T08:00:53", "price": 1.17156},
    }
    fill_anchors(page, com_segundos)
    page.click("#ncSaveBtn")
    page.wait_for_function("() => document.getElementById('ncStatus').classList.contains('ok')")
    alvo = page.evaluate("() => ncInstrument.value")
    salvo = page.evaluate("id => S.nocoda.studies[id]", alvo)
    for n, key in enumerate(("anchor1", "anchor2", "anchor3"), start=1):
        assert salvo[key]["datetime"] == com_segundos[key]["datetime"], (
            f"segundos perdidos na ancora {n}: {salvo[key]['datetime']}"
        )
    # E os segundos realmente importam para o resultado.
    sem_segundos = {k: {"datetime": v["datetime"][:16] + ":00", "price": v["price"]}
                    for k, v in com_segundos.items()}
    dois = page.evaluate(
        "([a, b]) => [window.JPWNocoda.geometry.compute(a).channelRange, window.JPWNocoda.geometry.compute(b).channelRange]",
        [com_segundos, sem_segundos],
    )
    assert dois[0] != dois[1], "segundos nao influenciaram o resultado — resolucao foi truncada"


def run_updated_at_changes(page, alvo, anterior):
    """Editar e salvar de novo avanca updatedAt."""
    page.wait_for_timeout(1100)
    page.fill("#ncPrice3", "1.18000")
    page.click("#ncSaveBtn")
    page.wait_for_function("() => document.getElementById('ncStatus').classList.contains('ok')")
    novo = page.evaluate("id => S.nocoda.studies[id].updatedAt", alvo)
    assert novo != anterior, f"updatedAt nao mudou apos edicao ({novo})"


def run_no_leak_between_instruments(page):
    """Alterar um instrumento nao contamina outro."""
    ids = page.evaluate("() => [...document.querySelectorAll('#ncInstrument option')].map(o => o.value)")
    assert len(ids) >= 2, "catalogo com menos de dois instrumentos operaveis"
    primeiro, segundo = ids[0], ids[1]

    page.select_option("#ncInstrument", segundo)
    page.wait_for_function("id => ncInstrument.value === id", arg=segundo)
    vazio = page.evaluate("() => ({d: ncDate1.value, p: ncPrice1.value})")
    assert vazio["d"] == "" and vazio["p"] == "", (
        f"formulario do segundo instrumento veio preenchido com dados do primeiro: {vazio}"
    )

    outro = {
        "anchor1": {"datetime": "2022-02-01T09:00:00", "price": 2.0},
        "anchor2": {"datetime": "2022-03-01T09:00:00", "price": 2.2},
        "anchor3": {"datetime": "2022-02-15T09:00:00", "price": 2.0},
    }
    fill_anchors(page, outro)
    page.click("#ncSaveBtn")
    page.wait_for_function("() => document.getElementById('ncStatus').classList.contains('ok')")

    estudos = page.evaluate("() => S.nocoda.studies")
    assert estudos[primeiro]["anchor1"]["price"] != estudos[segundo]["anchor1"]["price"], (
        "os dois instrumentos ficaram com a mesma ancora"
    )
    assert_close(estudos[segundo]["anchor1"]["price"], 2.0, label="ancora do segundo instrumento")
    assert_close(estudos[primeiro]["anchor1"]["price"], CANON["anchor1"]["price"],
                 label="ancora do primeiro instrumento preservada")
    return primeiro, segundo


def run_removed_instrument_keeps_study(page, alvo):
    """Tirar o instrumento da lista operacional NAO apaga sua memoria tecnica."""
    page.evaluate(
        """id => {
          window.__ncBackup = S.instruments.find(i => instrumentId(i.name) === id);
          S.instruments = S.instruments.filter(i => instrumentId(i.name) !== id);
          save();
        }""",
        alvo,
    )
    page.reload()
    page.wait_for_function("() => window.JPWNocoda && window.JPWNocodaUI")
    sobreviveu = page.evaluate("id => !!(S.nocoda.studies && S.nocoda.studies[id])", alvo)
    assert sobreviveu, "estudo foi destruido ao remover o instrumento da lista operacional"
    fora_do_seletor = page.evaluate(
        "id => instrumentCatalog().every(i => i.id !== id)", alvo
    )
    assert fora_do_seletor, "instrumento removido continuou no catalogo"


def run_state_compat(browser, url, mutacao, rotulo):
    """Grava um estado 'antigo' derivado dos proprios DEFAULTS e recarrega.

    A base vem de structuredClone(DEFAULTS) e nao de um literal inventado: um
    objeto minimo escrito a mao produz estado degenerado (ex.: phases vazio) e
    quebraria renderizadores por motivo alheio a esta feature, medindo a fixture
    em vez do produto. `mutacao` recebe o clone e simula a condicao desejada.
    """
    context = browser.new_context(viewport={"width": 1280, "height": 860})
    context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url)
    page.wait_for_function("() => typeof DEFAULTS === 'object'")
    page.evaluate(
        """mut => {
          const legado = structuredClone(DEFAULTS);
          new Function('s', mut)(legado);
          localStorage.setItem('jpwealth_v9_state', JSON.stringify(legado));
        }""",
        mutacao,
    )
    page.reload()
    page.wait_for_function("() => window.JPWNocoda && typeof S === 'object'")
    forma = page.evaluate(
        """() => ({
          tipo: typeof S.nocoda,
          studies: typeof (S.nocoda || {}).studies,
          eArray: Array.isArray((S.nocoda || {}).studies),
          quantos: S.nocoda && S.nocoda.studies ? Object.keys(S.nocoda.studies).length : -1,
          versao: S.nocoda && S.nocoda.schemaVersion
        })"""
    )
    assert forma["tipo"] == "object", f"{rotulo}: S.nocoda com tipo {forma['tipo']}"
    assert forma["studies"] == "object" and not forma["eArray"], f"{rotulo}: studies com forma errada — {forma}"
    assert forma["quantos"] == 0, f"{rotulo}: default deveria ser vazio, veio {forma['quantos']}"
    assert forma["versao"] == 1, f"{rotulo}: schemaVersion incorreta — {forma['versao']}"
    assert not erros, f"{rotulo}: pageerror — {erros}"
    context.close()


def run_backup_roundtrip(page):
    """O backup completo carrega o agregado e a importacao o recupera."""
    dados = page.evaluate(
        """() => {
          const clone = structuredClone(S);
          return {temNoCoda: !!clone.nocoda, estudos: Object.keys(clone.nocoda.studies).length};
        }"""
    )
    assert dados["temNoCoda"], "backup completo nao levaria o agregado NoCoda"
    assert dados["estudos"] > 0, "pre-condicao falhou: nenhum estudo para exportar"

    restaurado = page.evaluate(
        """() => {
          const arquivo = JSON.parse(JSON.stringify(S));   // simula ida e volta pelo JSON
          const antes = JSON.stringify(S.nocoda.studies);
          S.nocoda = {schemaVersion: 1, studies: {}};       // perde tudo
          S.nocoda = structuredClone(arquivo.nocoda);       // restaura do arquivo
          migrate();
          return {igual: JSON.stringify(S.nocoda.studies) === antes,
                  chaves: Object.keys(S.nocoda.studies).length};
        }"""
    )
    assert restaurado["igual"], "estudos nao sobreviveram ao ciclo exportar/importar"
    assert restaurado["chaves"] > 0, "importacao restaurou mapa vazio"


def run_no_operational_mutation(page):
    """Navegar e salvar estudo nao alteram nenhum dominio operacional."""
    antes = page.evaluate(
        """() => JSON.stringify({
          params: S.params, phases: S.phases, ledger: S.ledger,
          instruments: S.instruments, accounts: S.accounts, fxPlanning: S.fxPlanning
        })"""
    )
    open_nocoda(page)
    fill_anchors(page, {
        "anchor1": {"datetime": "2023-01-02T10:00:00", "price": 1.5},
        "anchor2": {"datetime": "2023-02-02T10:00:00", "price": 1.6},
        "anchor3": {"datetime": "2023-01-20T10:00:00", "price": 1.4},
    })
    page.click("#ncSaveBtn")
    page.wait_for_function("() => document.getElementById('ncStatus').classList.contains('ok')")
    depois = page.evaluate(
        """() => JSON.stringify({
          params: S.params, phases: S.phases, ledger: S.ledger,
          instruments: S.instruments, accounts: S.accounts, fxPlanning: S.fxPlanning
        })"""
    )
    assert antes == depois, "salvar um estudo NoCoda alterou dominio operacional"


def main():
    run_no_hardcoded_instruments()
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            run_canonical(page)
            run_wrong_formulas_rejected(page)
            run_invariants(page)
            run_horizontal_channel(page)
            run_third_anchor_on_base_line(page)
            run_extrapolation(page)
            run_signed_range_signs(page)
            run_validation(page)
            run_level_scale(page)
            run_subdivision_count(page)
            run_instrument_identity(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()

            # Interface, persistencia e nao regressao, em contexto proprio para
            # partir de localStorage limpo. O confirm() de descarte e aceito
            # automaticamente: o fluxo do teste sempre quer prosseguir.
            context, page, observed = prepare_page(browser, url)
            page.on("dialog", lambda dialog: dialog.accept())
            open_nocoda(page)
            run_selector_is_derived(page)
            run_live_calculation_does_not_persist(page)
            alvo, carimbo = run_save_and_reload(page)
            run_seconds_are_preserved(page)
            run_updated_at_changes(page, alvo, carimbo)
            primeiro, segundo = run_no_leak_between_instruments(page)
            run_backup_roundtrip(page)
            run_no_operational_mutation(page)
            run_removed_instrument_keeps_study(page, primeiro)
            assert not observed["pageerror"], f"pageerror no fluxo de UI: {observed['pageerror']}"
            context.close()

            # Estado anterior a feature: a chave nem existe.
            run_state_compat(browser, url, "delete s.nocoda;", "estado legado sem a chave")
            # O caso que o laco generico de migrate() NAO cobre: chave presente
            # com tipo errado — e tambem o que um backup adulterado produziria.
            run_state_compat(browser, url, "s.nocoda = 'isto nao e um objeto';", "agregado com tipo errado")
            run_state_compat(browser, url, "s.nocoda = {schemaVersion: 0, studies: []};", "studies como array")
            browser.close()
    finally:
        server.shutdown()
    print("NOCODA TEST PASS")


if __name__ == "__main__":
    main()
