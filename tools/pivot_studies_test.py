#!/usr/bin/env python3
"""Caracterizacao dos Estudos dos Pivots: matematica, estatistica e persistencia.

Segue o padrao consagrado do projeto para nucleo matematico: sobe a pagina
modular por HTTP, abre em Chromium e chama as funcoes PURAS pela superficie
publica `window.JPWPivots.math`, comparando com tolerancia absoluta. A
matematica nunca e reimplementada aqui — o teste so confere resultados
conferidos de forma independente antes de existir codigo de producao.

Todas as fixtures sao SINTETICAS. O teste nao cria ordem, nao fecha mes, nao
importa backup real e nao toca credencial.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

TOL = 1e-9

# Fixture canonica: e o exemplo da propria especificacao (secao 24). Amplitude,
# range, duracao e veredito do criterio foram conferidos a mao antes do codigo.
CANON = {
    "timeframe": "H4",
    "startDatetime": "2025-02-12T08:00:00", "startPrice": 1.08,
    "endDatetime": "2025-03-04T16:00:00", "endPrice": 1.14934,
    "maxCorrectionPct": 47.2, "notes": "",
}
CANON_ABS = 0.06934
CANON_PCT = 0.06934 / 1.08 * 100          # 6,4204%
CANON_MS = 20 * 86400000 + 8 * 3600000    # 20d 8h — fevereiro de 2025 tem 28 dias

# Amostra estatistica com valores exatos em binario: preco inicial 100 faz a
# amplitude percentual coincidir com a diferenca, sem residuo de ponto
# flutuante, e as medianas ficam conferiveis a mao.
#   amplitudes  2, 4, 5, 11  (%)     duracoes  1h, 2h, 3h, 10h    correcoes  10, 20, 30, 40
#   n par -> mediana da amplitude = (4+5)/2 = 4,5   media = 22/4 = 5,5   maximo = 11
#   mediana da duracao = (2h+3h)/2 = 2h30 = 9.000.000 ms   mediana da correcao = 25
SAMPLE = [
    {"id": "a", "timeframe": "H1", "startDatetime": "2025-01-01T00:00:00", "startPrice": 100,
     "endDatetime": "2025-01-01T01:00:00", "endPrice": 102, "maxCorrectionPct": 10},
    {"id": "b", "timeframe": "H1", "startDatetime": "2025-01-02T00:00:00", "startPrice": 100,
     "endDatetime": "2025-01-02T02:00:00", "endPrice": 96, "maxCorrectionPct": 20},
    {"id": "c", "timeframe": "H4", "startDatetime": "2025-01-03T00:00:00", "startPrice": 100,
     "endDatetime": "2025-01-03T03:00:00", "endPrice": 105, "maxCorrectionPct": 30},
    {"id": "d", "timeframe": "H4", "startDatetime": "2025-01-04T00:00:00", "startPrice": 100,
     "endDatetime": "2025-01-04T10:00:00", "endPrice": 111, "maxCorrectionPct": 40},
]
# Excede o criterio: fica gravado, fora da amostra principal.
OUTSIDE = {"id": "e", "timeframe": "H4", "startDatetime": "2025-01-05T00:00:00", "startPrice": 100,
           "endDatetime": "2025-01-05T04:00:00", "endPrice": 120, "maxCorrectionPct": 70}


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
        f"{label}: esperado {expected!r}, recebido {actual!r}"
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
    page.wait_for_function("() => window.JPWPivots && window.JPWPivots.math")
    return context, page, observed


def math_call(page, name, *args):
    return page.evaluate(f"a => window.JPWPivots.math.{name}(...a)", list(args))


# ---------------------------------------------------------------- estatica

def run_no_hardcoded_instruments():
    """Nenhum simbolo de instrumento pode estar escrito nos arquivos da feature."""
    for relative in ("src/js/10-domain/10-pivot-studies.js", "src/js/20-ui/15-pivot-studies.js"):
        texto = (ROOT / relative).read_text(encoding="utf-8")
        for simbolo in ("EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY",
                        "USDCHF", "USDCAD", "AUDCAD", "US500", "XAUUSD"):
            assert simbolo not in texto, (
                f"simbolo {simbolo} hardcoded em {relative} — a fonte canonica e instrumentCatalog()"
            )


def run_threshold_declared_once():
    """O 61,8 mora em UM lugar. Espalhado como magic number ele diverge."""
    dominio = (ROOT / "src/js/10-domain/10-pivot-studies.js").read_text(encoding="utf-8")
    assert dominio.count("61.8") == 1, "o limite de correcao aparece mais de uma vez no dominio"
    ui = (ROOT / "src/js/20-ui/15-pivot-studies.js").read_text(encoding="utf-8")
    assert "61.8" not in ui and "61,8" not in ui, "a interface repete o limite em vez de ler a constante"


# ---------------------------------------------------------------- matematica

def run_canonical(page):
    """A fixture da especificacao, ponta a ponta."""
    derived = math_call(page, "derive", CANON)
    assert derived is not None, "fixture canonica nao produziu derivados"
    assert derived["direction"] == "bullish", f"direcao: {derived['direction']}"
    assert_close(derived["absoluteRange"], CANON_ABS, 1e-12, "range absoluto")
    assert_close(derived["percentageRange"], CANON_PCT, TOL, "amplitude percentual")
    assert derived["durationMs"] == CANON_MS, f"duracao: {derived['durationMs']} vs {CANON_MS}"
    assert derived["withinRule"] is True, "correcao de 47,2% deveria atender ao criterio"
    assert math_call(page, "formatDuration", CANON_MS) == "20d 8h"


def run_direction_and_ranges(page):
    """Direcao DERIVADA nos tres casos, e as duas medidas de magnitude."""
    assert math_call(page, "direction", 1.0, 1.2) == "bullish"
    assert math_call(page, "direction", 1.2, 1.0) == "bearish"
    # Preco identico nao descreve pivot direcional: nem 'bullish', nem 'neutro'.
    assert math_call(page, "direction", 1.1, 1.1) is None, "preco igual produziu direcao"
    assert_close(math_call(page, "absoluteRange", 100, 111), 11, 1e-12, "range absoluto")
    assert_close(math_call(page, "percentageRange", 100, 111), 11, 1e-12, "amplitude")
    # A amplitude e relativa ao INICIO: a mesma diferenca de 10 vale 10% saindo
    # de 100 e 5% saindo de 200. Trocar o denominador passaria despercebido sem
    # este par.
    assert_close(math_call(page, "percentageRange", 200, 210), 5, 1e-12, "amplitude relativa ao inicio")
    assert_close(math_call(page, "percentageRange", 210, 200), 100 / 21, TOL, "amplitude na baixa")


def run_invalid_prices(page):
    """NaN, Infinity, zero, negativo e texto nao viram numero nem zero."""
    # NaN e Infinity nao atravessam JSON: sao construidos DENTRO da pagina.
    for literal in ("0", "-1.5", "NaN", "Infinity", "-Infinity", "'1.2'", "null", "undefined"):
        assert page.evaluate(f"() => window.JPWPivots.math.isValidPrice({literal})") is False, (
            f"isValidPrice aceitou {literal}"
        )
    assert page.evaluate("() => window.JPWPivots.math.isValidPrice(1.2)") is True
    for literal in ("NaN", "Infinity", "-Infinity", "'abc'", "''", "'  '", "null", "undefined"):
        assert page.evaluate(f"() => window.JPWPivots.math.parseNumber({literal})") is None, (
            f"parseNumber aceitou {literal}"
        )
    # Virgula decimal e a convencao de entrada do app.
    assert_close(page.evaluate("() => window.JPWPivots.math.parseNumber('1,2345')"), 1.2345, 1e-12, "virgula decimal")
    for bad in (0, -1):
        derived = math_call(page, "derive", dict(CANON, startPrice=bad))
        assert derived is None, f"derive aceitou preco inicial {bad}"


def run_duration(page):
    """Duracao exige fim estritamente posterior, e o formato e legivel."""
    assert math_call(page, "durationMs", "2025-01-01T00:00:00", "2025-01-01T00:00:00") is None, "datas iguais aceitas"
    assert math_call(page, "durationMs", "2025-01-02T00:00:00", "2025-01-01T00:00:00") is None, "fim anterior aceito"
    assert math_call(page, "durationMs", "2025-01-01T00:00:00", "2025-01-01T18:00:00") == 18 * 3600000
    assert math_call(page, "formatDuration", 18 * 3600000) == "18h"
    assert math_call(page, "formatDuration", 18 * 3600000 + 30 * 60000) == "18h 30min"
    assert math_call(page, "formatDuration", 45 * 60000) == "45min"
    assert math_call(page, "formatDuration", 4 * 86400000 + 12 * 3600000) == "4d 12h"
    assert math_call(page, "formatDuration", 2 * 86400000) == "2d"


def run_correction_rule(page):
    """61,8 e limite INVALIDANTE: estritamente menor atende, igual ja excede."""
    limite = page.evaluate("() => window.JPWPivots.math.MAX_CORRECTION_PCT")
    assert limite == 61.8, f"constante do criterio divergente: {limite}"
    assert math_call(page, "withinCorrectionRule", 0) is True, "correcao 0% deveria atender"
    assert math_call(page, "withinCorrectionRule", 61.79) is True
    assert math_call(page, "withinCorrectionRule", 61.8) is False, "61,8 exato deveria EXCEDER"
    assert math_call(page, "withinCorrectionRule", 61.81) is False
    assert math_call(page, "withinCorrectionRule", 95) is False


def run_correction_out_of_domain(page):
    """Correcao fora de 0-100 nao pode ser lida como 'atende ao criterio'.

    O formulario barra o valor, mas o formulario nao e o unico caminho de
    entrada: backup importado atravessa a normalizacao, que de proposito sanea
    so a forma e nao apaga registro. Uma regra unilateral (`< 61,8`) deixaria
    -500 entrar na amostra PRINCIPAL e envenenar a mediana das correcoes.
    """
    assert math_call(page, "correctionInDomain", 0) is True
    assert math_call(page, "correctionInDomain", 100) is True
    assert math_call(page, "correctionInDomain", -0.001) is False
    assert math_call(page, "correctionInDomain", 100.001) is False
    for fora in (-500, -0.001, 100.001, 1e9):
        assert math_call(page, "withinCorrectionRule", fora) is False, (
            f"correcao {fora} foi classificada como dentro do criterio"
        )

    envenenado = [dict(SAMPLE[0], id="veneno", maxCorrectionPct=-500)]
    stats = math_call(page, "stats", envenenado)
    assert stats["registered"] == 1, "o registro adulterado foi apagado"
    assert stats["n"] == 0, "correcao de -500% entrou na amostra principal"
    assert stats["outside"] == 1 and stats["outOfDomain"] == 1
    assert stats["medianCorrection"] is None, (
        f"mediana das correcoes contaminada por valor fora do dominio: {stats['medianCorrection']}"
    )
    # Ainda derivavel e visivel: preservado, apenas classificado a parte.
    derived = math_call(page, "derive", envenenado[0])
    assert derived is not None and derived["correctionInDomain"] is False


def run_validation(page):
    """Erros por CAMPO — a interface precisa saber onde apontar."""
    def campos(payload):
        result = math_call(page, "validate", payload)
        return result["ok"], sorted({e["field"] for e in result["errors"]})

    ok, _ = campos(CANON)
    assert ok, "caso de controle valido foi reprovado"

    casos = [
        (dict(CANON, timeframe="D1"), "timeframe", "timeframe fora de H1/H4"),
        (dict(CANON, timeframe="M30"), "timeframe", "timeframe fora de H1/H4"),
        (dict(CANON, startDatetime="2025-13-45T99:99"), "startDatetime", "data inexistente"),
        (dict(CANON, endDatetime=CANON["startDatetime"]), "endDatetime", "mesmo instante"),
        (dict(CANON, endDatetime="2025-01-01T00:00:00"), "endDatetime", "fim anterior ao inicio"),
        (dict(CANON, startPrice=0), "startPrice", "preco inicial zero"),
        (dict(CANON, endPrice=-1), "endPrice", "preco final negativo"),
        (dict(CANON, endPrice=CANON["startPrice"]), "endPrice", "precos iguais"),
        (dict(CANON, maxCorrectionPct=""), "maxCorrectionPct", "correcao ausente"),
        (dict(CANON, maxCorrectionPct=-5), "maxCorrectionPct", "correcao negativa"),
        (dict(CANON, maxCorrectionPct=150), "maxCorrectionPct", "correcao acima de 100%"),
    ]
    for payload, field, rotulo in casos:
        ok, fields = campos(payload)
        assert not ok, f"{rotulo}: passou pela validacao"
        assert field in fields, f"{rotulo}: erro reportado em {fields}, esperado {field}"

    # 61,8 NAO invalida o registro — apenas o classifica fora do criterio.
    ok, _ = campos(dict(CANON, maxCorrectionPct=61.8))
    assert ok, "correcao de 61,8% foi recusada na gravacao em vez de classificada"

    periodo = math_call(page, "validatePeriod", "2025-12-31", "2025-01-01")
    assert not periodo["ok"], "periodo invertido aceito"
    assert math_call(page, "validatePeriod", "2025-01-01", "2025-01-01")["ok"], "periodo de um dia recusado"
    assert not math_call(page, "validatePeriod", "2025-02-30", "2025-03-01")["ok"], "30 de fevereiro aceito"


def run_overlap(page):
    """Sobreposicao e AVISO, nao proibicao — a funcao so informa."""
    assert math_call(page, "periodsOverlap", "2025-01-01", "2025-06-30", "2025-04-01", "2025-12-31") is True
    assert math_call(page, "periodsOverlap", "2025-01-01", "2025-03-31", "2025-04-01", "2025-12-31") is False
    # Janelas fechadas: encostar num unico dia ja e sobreposicao.
    assert math_call(page, "periodsOverlap", "2025-01-01", "2025-04-01", "2025-04-01", "2025-12-31") is True


# ---------------------------------------------------------------- estatistica

def run_stats_empty_and_single(page):
    """n=0 nunca vira zero; n=1 faz max, media e mediana coincidirem."""
    vazio = math_call(page, "stats", [])
    assert vazio["n"] == 0
    for key in ("max", "mean", "median", "medianDurationMs", "medianCorrection"):
        assert vazio[key] is None, f"amostra vazia devolveu {key}={vazio[key]!r} em vez de ausencia"

    unico = math_call(page, "stats", [SAMPLE[0]])
    assert unico["n"] == 1
    assert_close(unico["max"], 2, 1e-12, "maximo com n=1")
    assert_close(unico["mean"], 2, 1e-12, "media com n=1")
    assert_close(unico["median"], 2, 1e-12, "mediana com n=1")


def run_stats_sample(page):
    """Amostra de 4 com valores exatos: mediana par, media, maximo e contagens."""
    stats = math_call(page, "stats", SAMPLE)
    assert stats["n"] == 4
    assert stats["registered"] == 4
    assert_close(stats["max"], 11, 1e-12, "maximo")
    assert stats["maxTimeframe"] == "H4"
    assert stats["maxPivotId"] == "d", f"maior pivot apontado: {stats['maxPivotId']}"
    assert_close(stats["mean"], 5.5, 1e-12, "media")
    assert_close(stats["median"], 4.5, 1e-12, "mediana com n par")
    assert stats["medianDurationMs"] == 9000000, f"duracao mediana: {stats['medianDurationMs']}"
    assert_close(stats["medianCorrection"], 25, 1e-12, "correcao mediana")
    assert stats["bullish"] == 3 and stats["bearish"] == 1, (
        f"distribuicao por direcao: {stats['bullish']}/{stats['bearish']}"
    )
    assert stats["timeframes"]["H1"]["n"] == 2 and stats["timeframes"]["H4"]["n"] == 2
    assert_close(stats["timeframes"]["H1"]["max"], 4, 1e-12, "maximo H1")
    assert_close(stats["timeframes"]["H4"]["max"], 11, 1e-12, "maximo H4")
    assert_close(stats["timeframes"]["H1"]["median"], 3, 1e-12, "mediana H1 (2 e 4)")
    assert_close(stats["timeframes"]["H4"]["median"], 8, 1e-12, "mediana H4 (5 e 11)")

    # n impar: tirando o de 11%, a mediana passa a ser o elemento central (4).
    impar = math_call(page, "stats", SAMPLE[:3])
    assert impar["n"] == 3
    assert_close(impar["median"], 4, 1e-12, "mediana com n impar")
    assert_close(impar["mean"], 11 / 3, TOL, "media com n impar")


def run_stats_criterion_scope(page):
    """Fora do criterio: contado a parte, incluido so quando o filtro pedir."""
    completo = SAMPLE + [OUTSIDE]
    principal = math_call(page, "stats", completo)
    assert principal["registered"] == 5, "total registrado deveria contar todos"
    assert principal["n"] == 4, "pivot fora do criterio entrou na amostra principal"
    assert principal["outside"] == 1
    assert_close(principal["max"], 11, 1e-12, "maximo contaminado pelo pivot fora do criterio")

    todos = math_call(page, "stats", completo, {"includeOutside": True})
    assert todos["n"] == 5, "filtro 'todos' nao incluiu o pivot fora do criterio"
    assert_close(todos["max"], 20, 1e-12, "maximo com todos os pivots")

    apenas_fora = math_call(page, "stats", completo, {"scope": "outside"})
    assert apenas_fora["n"] == 1 and apenas_fora["scope"] == "outside"
    assert_close(apenas_fora["max"], 20, 1e-12, "maximo do escopo 'fora do criterio'")

    # 61,8 exato pertence ao lado de fora.
    limite = math_call(page, "stats", [dict(SAMPLE[0], maxCorrectionPct=61.8)])
    assert limite["n"] == 0 and limite["outside"] == 1, "61,8 exato entrou na amostra principal"


def run_top(page):
    """TOP por amplitude, com identidade para a interface localizar o registro."""
    stats = math_call(page, "stats", SAMPLE)
    top_h4 = [t["id"] for t in stats["timeframes"]["H4"]["top"]]
    assert top_h4 == ["d", "c"], f"TOP H4 fora de ordem: {top_h4}"
    top_h1 = [t["id"] for t in stats["timeframes"]["H1"]["top"]]
    assert top_h1 == ["b", "a"], f"TOP H1 fora de ordem: {top_h1}"
    assert len(stats["timeframes"]["H1"]["top"]) <= 3


def run_median_direct(page):
    """A mediana em si, incluindo o caso par e a ordenacao numerica."""
    assert math_call(page, "median", []) is None
    assert_close(math_call(page, "median", [5]), 5, 1e-12, "mediana n=1")
    assert_close(math_call(page, "median", [1, 3]), 2, 1e-12, "mediana n=2")
    assert_close(math_call(page, "median", [3, 1, 2]), 2, 1e-12, "mediana desordenada")
    # Se ordenasse como texto, "10" viria antes de "9" e a mediana seria outra.
    assert_close(math_call(page, "median", [9, 10, 11, 2, 100]), 10, 1e-12, "mediana com ordenacao numerica")
    assert math_call(page, "mean", []) is None


# ---------------------------------------------------------------- ordenacao

def run_sorting(page):
    """Ordenacao NUMERICA nos quatro criterios, nos dois sentidos."""
    records = math_call(page, "records", SAMPLE + [OUTSIDE])

    def ids(key, ascending):
        return [r["id"] for r in page.evaluate(
            "a => window.JPWPivots.math.sort(a[0], a[1], a[2])", [records, key, ascending])]

    # Amplitudes 2, 4, 5, 11, 20 — em ordem lexicografica 11 e 20 viriam antes de 2.
    assert ids("amplitude", False) == ["e", "d", "c", "b", "a"], f"amplitude desc: {ids('amplitude', False)}"
    assert ids("amplitude", True) == ["a", "b", "c", "d", "e"], f"amplitude asc: {ids('amplitude', True)}"
    assert ids("date", True) == ["a", "b", "c", "d", "e"], f"data asc: {ids('date', True)}"
    assert ids("date", False) == ["e", "d", "c", "b", "a"], f"data desc: {ids('date', False)}"
    # Duracoes 1h, 2h, 3h, 10h, 4h.
    assert ids("duration", False) == ["d", "e", "c", "b", "a"], f"duracao desc: {ids('duration', False)}"
    # Correcoes 10, 20, 30, 40, 70.
    assert ids("correction", False) == ["e", "d", "c", "b", "a"], f"correcao desc: {ids('correction', False)}"
    # Chave desconhecida cai no padrao do estudo (maior amplitude primeiro).
    assert ids("inexistente", False) == ["e", "d", "c", "b", "a"], "chave invalida nao caiu no padrao"


# ---------------------------------------------------------------- interface

def open_pivots(page):
    """NAV3-D: alias abre Research/Forex/Pivots sem falso owner Exec."""
    assert page.evaluate("() => JPWNavigation.navigate('pivots')") is True
    page.wait_for_function("() => window.JPWResearch.ui.getView() === 'pivots'")
    state = page.evaluate("""() => ({
      primary:JPWNavigation.current().primary,
      child:JPWNavigation.current().child,
      canonical:JPWNavigation.current().canonical,
      view:JPWNavigation.current().localView,
      execActive:document.getElementById('exec').classList.contains('active')
    })""")
    assert state == {'primary':'research','child':'research-forex','canonical':'research-forex',
                     'view':{'surface':'research','view':'pivots'},'execActive':False}, state
    page.wait_for_selector("#pvInstrument")


def set_field(page, element_id, value):
    """`page.fill` recusa datetime-local com segundos ('Malformed value') — e uma
    limitacao do Playwright, nao do produto. Escrever direto e disparar o evento
    percorre o MESMO caminho que a digitacao real aciona."""
    page.evaluate(
        """a => { const el = document.getElementById(a[0]); el.value = a[1];
                  el.dispatchEvent(new Event('input', {bubbles: true})); }""",
        [element_id, value],
    )


def run_selector_is_derived(page):
    """O seletor nasce de instrumentCatalog(), e instrumento novo aparece sem
    editar a feature."""
    antes = page.evaluate("() => document.getElementById('pvInstrument').options.length")
    catalogo = page.evaluate("() => instrumentCatalog().length")
    assert antes == catalogo, f"seletor com {antes} opcoes para catalogo de {catalogo}"

    page.evaluate("""() => {
      S.instruments.push({name:'ZZZTEST', cpl:100000, teto:0.1, preco:1.5, updated:'2026-01-01'});
    }""")
    page.evaluate("() => window.JPWPivotsUI.render()")
    depois = page.evaluate(
        "() => Array.from(document.getElementById('pvInstrument').options).map(o => o.value)")
    assert "ZZZTEST" in depois, "instrumento novo do catalogo nao apareceu no seletor"
    page.evaluate("() => { S.instruments = S.instruments.filter(i => i.name !== 'ZZZTEST'); }")
    page.evaluate("() => window.JPWPivotsUI.render()")


def create_study(page, start, end):
    page.click("#pvNewStudyBtn")
    page.fill("#pvPeriodStart", start)
    page.fill("#pvPeriodEnd", end)
    page.click("#pvCreateStudyBtn")
    page.wait_for_selector("#pvAddPivotBtn")


def add_pivot(page, pivot):
    page.click("#pvAddPivotBtn")
    page.wait_for_selector("#pv_timeframe")
    page.select_option("#pv_timeframe", pivot["timeframe"])
    for field in ("startDatetime", "startPrice", "endDatetime", "endPrice", "maxCorrectionPct"):
        set_field(page, "pv_" + field, str(pivot[field]))
    page.click("#pvSavePivotBtn")
    page.wait_for_function("() => !document.getElementById('pv_timeframe')")


def run_create_and_register(page):
    """Fluxo real: criar estudo, registrar pivot e ver a tabela e o resumo."""
    create_study(page, "2025-01-01", "2025-12-31")
    estado = page.evaluate("() => S.pivotStudies.studies.length")
    assert estado == 1, f"estudo nao foi gravado ({estado})"
    assert page.evaluate("() => S.pivotStudies.studies[0].pivots.length") == 0, "estudo nasceu com pivot ficticio"

    add_pivot(page, CANON)
    gravado = page.evaluate("() => S.pivotStudies.studies[0].pivots[0]")
    assert gravado["timeframe"] == "H4"
    assert_close(gravado["startPrice"], CANON["startPrice"], 1e-12, "preco inicial gravado")
    # DERIVADO NAO PERSISTE: gravar direcao, amplitude ou duracao criaria uma
    # segunda fonte de verdade capaz de divergir das causas.
    for proibido in ("direction", "absoluteRange", "percentageRange", "duration",
                     "durationMs", "withinRule", "ranking"):
        assert proibido not in gravado, f"campo derivado '{proibido}' foi persistido"

    assert page.evaluate("() => document.querySelectorAll('[data-pv-row]').length") == 1
    resumo = page.evaluate("() => document.querySelector('.pv-metrics').innerText")
    assert "6,42%" in resumo, f"amplitude ausente do resumo: {resumo!r}"
    assert "20d 8h" in resumo, f"duracao ausente do resumo: {resumo!r}"


def run_live_calculation_does_not_persist(page):
    """Calcular nao e salvar: a previa acompanha a digitacao sem gravar nada."""
    antes = page.evaluate("() => JSON.stringify(S.pivotStudies)")
    page.click("#pvAddPivotBtn")
    page.wait_for_selector("#pv_timeframe")
    for field in ("startDatetime", "startPrice", "endDatetime", "endPrice", "maxCorrectionPct"):
        set_field(page, "pv_" + field, str(CANON[field]))
    previa = page.evaluate("() => document.getElementById('pvPreview').innerText")
    assert "6,42%" in previa, f"previa nao calculou ao vivo: {previa!r}"
    assert page.evaluate("() => JSON.stringify(S.pivotStudies)") == antes, "a previa gravou no estado"
    page.click("#pvCancelPivotBtn")
    page.wait_for_function("() => !document.getElementById('pv_timeframe')")
    assert page.evaluate("() => JSON.stringify(S.pivotStudies)") == antes, "cancelar deixou residuo"


def run_edit_updates_in_place(page):
    """Editar ATUALIZA o registro e recalcula; nao cria um segundo."""
    alvo = page.evaluate("() => S.pivotStudies.studies[0].pivots[0].id")
    carimbo = page.evaluate("() => S.pivotStudies.studies[0].pivots[0].updatedAt")
    page.click(f'[data-pv-edit="{alvo}"]')
    page.wait_for_selector("#pv_endPrice")
    set_field(page, "pv_endPrice", "1,20000")
    page.click("#pvSavePivotBtn")
    page.wait_for_function("() => !document.getElementById('pv_endPrice')")
    depois = page.evaluate("() => S.pivotStudies.studies[0].pivots")
    assert len(depois) == 1, f"editar criou registro novo ({len(depois)})"
    assert depois[0]["id"] == alvo, "a identidade do pivot mudou na edicao"
    assert_close(depois[0]["endPrice"], 1.2, 1e-12, "preco editado")
    assert depois[0]["updatedAt"] != carimbo, "updatedAt nao acompanhou a edicao"
    amplitude = page.evaluate(
        "() => window.JPWPivots.math.derive(S.pivotStudies.studies[0].pivots[0]).percentageRange")
    assert_close(amplitude, (1.2 - 1.08) / 1.08 * 100, TOL, "amplitude nao foi recalculada")


def run_outside_criterion_is_kept(page):
    """Editar para alem de 61,8% RECLASSIFICA; nunca apaga."""
    alvo = page.evaluate("() => S.pivotStudies.studies[0].pivots[0].id")
    page.click(f'[data-pv-edit="{alvo}"]')
    page.wait_for_selector("#pv_maxCorrectionPct")
    set_field(page, "pv_maxCorrectionPct", "70")
    page.click("#pvSavePivotBtn")
    page.wait_for_function("() => !document.getElementById('pv_maxCorrectionPct')")
    assert page.evaluate("() => S.pivotStudies.studies[0].pivots.length") == 1, "o registro foi destruido"
    # Filtro padrao (somente validos) esconde da lista, mas o dado continua la.
    assert page.evaluate("() => document.querySelectorAll('[data-pv-row]').length") == 0
    page.click('[data-pv-filter="criterion"][data-pv-value="all"]')
    page.wait_for_selector("[data-pv-row]")
    marcado = page.evaluate("() => document.querySelector('[data-pv-row]').className")
    assert "pv-outside" in marcado, f"pivot fora do criterio nao foi marcado: {marcado!r}"
    # Devolve o registro ao criterio para os proximos blocos.
    page.click(f'[data-pv-edit="{alvo}"]')
    page.wait_for_selector("#pv_maxCorrectionPct")
    set_field(page, "pv_maxCorrectionPct", "47,2")
    page.click("#pvSavePivotBtn")
    page.wait_for_function("() => !document.getElementById('pv_maxCorrectionPct')")
    page.click('[data-pv-filter="criterion"][data-pv-value="valid"]')


def run_form_belongs_to_selected_study(page):
    """Trocar de estudo fecha o formulario — salvar nunca vira no-op silencioso.

    O formulario e filho do estudo selecionado e edita um pivot DELE. Se
    sobrevivesse a troca, `pvEditingId` apontaria para registro de outro estudo,
    o save nao acharia o alvo e retornaria sem gravar e sem avisar: o operador
    digitaria, clicaria em salvar e nada aconteceria.
    """
    instrumento = page.evaluate("() => document.getElementById('pvInstrument').value")
    # Segundo estudo, vazio, no MESMO instrumento.
    create_study(page, "2023-01-01", "2023-12-31")
    origem = page.evaluate("() => document.getElementById('pvStudy').value")
    outro = page.evaluate(
        "a => Array.from(document.getElementById('pvStudy').options).map(o => o.value).find(v => v !== a)",
        origem)
    assert outro, "pre-condicao falhou: nao ha um segundo estudo para trocar"

    # Abre o formulario num estudo que TENHA pivot, sem sujar o rascunho.
    page.select_option("#pvStudy", outro)
    page.wait_for_function("a => document.getElementById('pvStudy').value === a", arg=outro)
    alvo = page.evaluate("() => { const b = document.querySelector('[data-pv-edit]'); return b && b.dataset.pvEdit; }")
    assert alvo, "pre-condicao falhou: estudo sem pivot para editar"
    page.click(f'[data-pv-edit="{alvo}"]')
    page.wait_for_selector("#pv_endPrice")

    page.select_option("#pvStudy", origem)
    page.wait_for_function("a => document.getElementById('pvStudy').value === a", arg=origem)
    assert page.evaluate("() => !document.getElementById('pv_endPrice')"), (
        "o formulario sobreviveu a troca de estudo e ficou apontando para outro registro"
    )
    # Mesma regra para a troca de instrumento.
    page.select_option("#pvStudy", outro)
    page.wait_for_function("a => document.getElementById('pvStudy').value === a", arg=outro)
    page.click(f'[data-pv-edit="{alvo}"]')
    page.wait_for_selector("#pv_endPrice")
    opcoes = page.evaluate(
        "() => Array.from(document.getElementById('pvInstrument').options).map(o => o.value)")
    vizinho = next(o for o in opcoes if o != instrumento)
    page.select_option("#pvInstrument", vizinho)
    page.wait_for_function("a => document.getElementById('pvInstrument').value === a", arg=vizinho)
    assert page.evaluate("() => !document.getElementById('pv_endPrice')"), (
        "o formulario sobreviveu a troca de instrumento"
    )
    page.select_option("#pvInstrument", instrumento)
    page.wait_for_function("a => document.getElementById('pvInstrument').value === a", arg=instrumento)
    # Remove o estudo auxiliar para nao perturbar os blocos seguintes.
    page.select_option("#pvStudy", origem)
    page.wait_for_function("a => document.getElementById('pvStudy').value === a", arg=origem)
    page.click("#pvDeleteStudyBtn")
    page.wait_for_function("a => !S.pivotStudies.studies.some(s => s.id === a)", arg=origem)


def run_broken_records_are_reachable(page):
    """Registro sem cálculo possível fica VISÍVEL e acionável, nunca preso.

    A normalização de propósito não valida a matemática — apagar entrada do
    operador em silêncio é proibido. Mas preservar sem dar acesso era pior: o
    total dizia "1 de 3" e os outros dois não apareciam em filtro nenhum, sem
    editar e sem excluir. Agora aparecem em linha degradada, com o motivo.
    """
    page.evaluate(
        """() => {
          const inst = document.getElementById('pvInstrument').value;
          const mk = (id, sp, ep, sd, ed) => ({id, timeframe:'H4', startDatetime:sd,
            startPrice:sp, endDatetime:ed, endPrice:ep, maxCorrectionPct:20,
            notes:'', createdAt:'', updatedAt:''});
          S.pivotStudies = {schemaVersion:1, studies:[{id:'QUEBRADO', instrumentId:inst,
            periodStart:'2025-01-01', periodEnd:'2025-12-31', createdAt:'', updatedAt:'',
            pivots:[
              mk('bom','1.10','1.20','2025-02-01T00:00:00','2025-02-05T00:00:00'),
              mk('igual','1.10','1.10','2025-03-01T00:00:00','2025-03-05T00:00:00'),
              mk('invertido','1.10','1.20','2025-04-10T00:00:00','2025-04-01T00:00:00')]}]};
          save(); window.JPWPivotsUI.render();
        }"""
    )
    visiveis = page.evaluate("() => [...document.querySelectorAll('[data-pv-row]')].map(r => r.dataset.pvRow)")
    assert set(visiveis) == {"bom", "igual", "invertido"}, f"registros sem cálculo ficaram invisíveis: {visiveis}"
    for alvo in ("igual", "invertido"):
        assert page.evaluate(f"() => !!document.querySelector('[data-pv-edit=\"{alvo}\"]')"), f"{alvo} sem ação de corrigir"
        assert page.evaluate(f"() => !!document.querySelector('[data-pv-delete=\"{alvo}\"]')"), f"{alvo} sem ação de excluir"
        assert page.evaluate(f"() => document.querySelector('[data-pv-row=\"{alvo}\"]').className").find("pv-broken") >= 0
    assert page.evaluate("() => !!document.querySelector('.pv-broken-note')"), "sem explicação do que são as linhas sem cálculo"
    # E a exclusão funciona de verdade — o registro deixa de estar preso.
    page.click('[data-pv-delete="igual"]')
    page.wait_for_function("() => !S.pivotStudies.studies[0].pivots.some(p => p.id === 'igual')")
    assert page.evaluate("() => S.pivotStudies.studies[0].pivots.length") == 2


def run_create_study_asks_before_discarding(page):
    """Criar estudo troca o foco: passa pela MESMA guarda de descarte dos outros."""
    page.evaluate(
        """() => {
          const inst = document.getElementById('pvInstrument').value;
          S.pivotStudies = {schemaVersion:1, studies:[{id:'A', instrumentId:inst,
            periodStart:'2025-01-01', periodEnd:'2025-12-31', createdAt:'', updatedAt:'', pivots:[]}]};
          save(); window.JPWPivotsUI.render();
        }"""
    )
    page.click("#pvAddPivotBtn")
    page.wait_for_selector("#pv_startPrice")
    page.evaluate("""() => { const e = document.getElementById('pv_startPrice');
                             e.value = '1,2345'; e.dispatchEvent(new Event('input', {bubbles:true})); }""")
    # O confirm() é instrumentado NA PÁGINA, e não pelo handler de diálogo do
    # Playwright: main() já registra um handler global que aceita tudo, e dois
    # handlers competindo tornariam o resultado dependente da ordem de registro.
    page.evaluate(
        "() => { window.__perguntas = []; window.__confirmOriginal = window.confirm;"
        "        window.confirm = m => { window.__perguntas.push(m); return false; }; }")
    page.click("#pvNewStudyBtn")
    page.wait_for_timeout(200)
    perguntas = page.evaluate("() => window.__perguntas")
    assert perguntas and "não salvas" in perguntas[0], f"criar estudo não perguntou antes de descartar: {perguntas}"
    assert page.evaluate("() => !!document.getElementById('pv_startPrice')"), (
        "recusar o descarte deveria preservar o formulário"
    )
    page.evaluate("() => { window.confirm = window.__confirmOriginal; }")
    page.evaluate("() => { window.JPWPivotsUI.render(); }")


def run_workspace_repaints_after_state_swap(page):
    """Trocar S por baixo da tela repinta o workspace, e nenhuma ação fica muda.

    boot() não desenhava os workspaces montados sob demanda: quem estivesse com
    Estudos dos Pivots aberto durante uma importação continuava vendo — e
    clicando — um estudo que a importação acabara de eliminar, com os três
    caminhos de ação morrendo em return silencioso.
    """
    page.evaluate(
        """() => {
          const inst = document.getElementById('pvInstrument').value;
          S.pivotStudies = {schemaVersion:1, studies:[{id:'ANTES', instrumentId:inst,
            periodStart:'2025-01-01', periodEnd:'2025-12-31', createdAt:'', updatedAt:'',
            pivots:[{id:'p1', timeframe:'H4', startDatetime:'2025-02-01T00:00:00', startPrice:1.1,
                     endDatetime:'2025-02-05T00:00:00', endPrice:1.2, maxCorrectionPct:20,
                     notes:'', createdAt:'', updatedAt:''}]}]};
          save(); window.JPWPivotsUI.render();
        }"""
    )
    assert page.evaluate("() => document.querySelectorAll('[data-pv-row]').length") == 1
    # Substituição de S pelo MESMO caminho de um import: troca e boot().
    page.evaluate("""() => { S.pivotStudies = {schemaVersion:1, studies:[]}; save(); boot(); }""")
    page.wait_for_timeout(200)
    assert page.evaluate("() => document.querySelectorAll('[data-pv-row]').length") == 0, (
        "a tela seguiu mostrando um estudo que já não existe"
    )
    assert page.evaluate("() => !document.querySelector('.pv-caption')"), "caption obsoleta permaneceu"


def run_multiple_studies_same_instrument(page):
    """Historico: periodos distintos coexistem e nao se sobrescrevem."""
    instrumento = page.evaluate("() => document.getElementById('pvInstrument').value")
    create_study(page, "2024-01-01", "2024-12-31")
    estudos = page.evaluate(
        "i => S.pivotStudies.studies.filter(s => s.instrumentId === i).length", instrumento)
    assert estudos == 2, f"segundo estudo do mesmo instrumento nao coexistiu ({estudos})"
    opcoes = page.evaluate("() => document.getElementById('pvStudy').options.length")
    assert opcoes == 2, f"seletor de estudo com {opcoes} opcoes"
    # O estudo de 2025 conserva seu pivot; o de 2024 nasceu vazio.
    contagens = page.evaluate("() => S.pivotStudies.studies.map(s => s.pivots.length)")
    assert sorted(contagens) == [0, 1], f"pivots vazaram entre estudos: {contagens}"


def run_no_leak_between_instruments(page):
    """Estudo de um instrumento nao aparece no outro."""
    opcoes = page.evaluate(
        "() => Array.from(document.getElementById('pvInstrument').options).map(o => o.value)")
    assert len(opcoes) >= 2, "catalogo pequeno demais para o teste de isolamento"
    primeiro, segundo = opcoes[0], opcoes[1]
    page.select_option("#pvInstrument", segundo)
    page.wait_for_function("i => document.getElementById('pvInstrument').value === i", arg=segundo)
    visiveis = page.evaluate("() => document.querySelectorAll('[data-pv-row]').length")
    assert visiveis == 0, f"pivots do outro instrumento vazaram ({visiveis})"
    assert page.evaluate("() => !!document.getElementById('pvAddPivotBtn')") is False, (
        "instrumento sem estudo ofereceu registro de pivot"
    )
    page.select_option("#pvInstrument", primeiro)
    page.wait_for_function("i => document.getElementById('pvInstrument').value === i", arg=primeiro)
    return primeiro, segundo


def run_reload_keeps_data(page):
    """Recarregar a pagina devolve estudos e pivots intactos."""
    antes = page.evaluate("() => JSON.stringify(S.pivotStudies)")
    page.reload()
    page.wait_for_function("() => window.JPWPivots && typeof S === 'object'")
    depois = page.evaluate("() => JSON.stringify(S.pivotStudies)")
    assert depois == antes, "o agregado nao sobreviveu ao reload"


def run_backup_roundtrip(page):
    """O backup completo carrega o agregado e a importacao o recupera."""
    dados = page.evaluate("() => ({tem: !!structuredClone(S).pivotStudies, n: S.pivotStudies.studies.length})")
    assert dados["tem"], "backup completo nao levaria o agregado"
    assert dados["n"] > 0, "pre-condicao falhou: nenhum estudo para exportar"
    restaurado = page.evaluate(
        """() => {
          const arquivo = JSON.parse(JSON.stringify(S));      // simula ida e volta pelo JSON
          const antes = JSON.stringify(S.pivotStudies.studies);
          S.pivotStudies = {schemaVersion: 1, studies: []};   // perde tudo
          S.pivotStudies = structuredClone(arquivo.pivotStudies);
          migrate();
          return {igual: JSON.stringify(S.pivotStudies.studies) === antes,
                  n: S.pivotStudies.studies.length};
        }"""
    )
    assert restaurado["igual"], "estudos nao sobreviveram ao ciclo exportar/importar"
    assert restaurado["n"] > 0, "importacao restaurou lista vazia"


def run_removed_instrument_keeps_study(page, instrumento):
    """Mudanca de configuracao nao destroi memoria tecnica (secao 53)."""
    antes = page.evaluate("i => S.pivotStudies.studies.filter(s => s.instrumentId === i).length", instrumento)
    assert antes > 0, "pre-condicao falhou: instrumento sem estudo"
    page.evaluate("i => { S.instruments = S.instruments.filter(x => x.name !== i); }", instrumento)
    page.evaluate("() => { migrate(); window.JPWPivotsUI.render(); }")
    depois = page.evaluate("i => S.pivotStudies.studies.filter(s => s.instrumentId === i).length", instrumento)
    assert depois == antes, "o estudo foi apagado junto com o instrumento"
    opcoes = page.evaluate(
        "() => Array.from(document.getElementById('pvInstrument').options).map(o => o.value)")
    assert instrumento in opcoes, "estudo virou dado orfao inacessivel apos remocao do instrumento"


def run_delete_pivot(page, instrumento):
    """Exclusao explicita remove o pivot — e so ele."""
    page.select_option("#pvInstrument", instrumento)
    page.wait_for_function("i => document.getElementById('pvInstrument').value === i", arg=instrumento)
    estudos_antes = page.evaluate("() => S.pivotStudies.studies.length")
    alvo = page.evaluate("() => document.querySelector('[data-pv-delete]').dataset.pvDelete")
    page.click(f'[data-pv-delete="{alvo}"]')
    page.wait_for_function(
        "a => !S.pivotStudies.studies.some(s => s.pivots.some(p => p.id === a))", arg=alvo)
    assert page.evaluate("() => S.pivotStudies.studies.length") == estudos_antes, (
        "excluir um pivot removeu tambem o estudo"
    )


def run_no_operational_mutation(page):
    """Nada nesta tela toca dominio operacional."""
    antes = page.evaluate(
        """() => JSON.stringify({
          params: S.params, phases: S.phases, ledger: S.ledger,
          instruments: S.instruments, accounts: S.accounts, quarantine: S.quarantine
        })"""
    )
    page.evaluate("() => window.JPWPivotsUI.render()")
    depois = page.evaluate(
        """() => JSON.stringify({
          params: S.params, phases: S.phases, ledger: S.ledger,
          instruments: S.instruments, accounts: S.accounts, quarantine: S.quarantine
        })"""
    )
    assert antes == depois, "renderizar Estudos dos Pivots alterou dominio operacional"


def run_no_inference_language(page):
    """A tela declara o vies de selecao e nao promete probabilidade."""
    texto = page.evaluate("() => document.getElementById('execPivots').innerText")
    assert "selecionada pelo operador" in texto, "o aviso de vies de amostra sumiu da tela"
    for proibido in ("chance de", "probabilidade de", "esperado para", "alvo provavel", "previsao"):
        assert proibido not in texto.lower(), f"linguagem inferencial na tela: {proibido!r}"


# ---------------------------------------------------------------- compatibilidade

def run_state_compat(browser, url, mutacao, rotulo):
    """Grava um estado 'antigo' derivado dos proprios DEFAULTS e recarrega.

    A base vem de structuredClone(DEFAULTS) e nao de um literal inventado: um
    objeto minimo escrito a mao produz estado degenerado e quebraria
    renderizadores por motivo alheio a esta feature.
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
    page.wait_for_function("() => window.JPWPivots && typeof S === 'object'")
    forma = page.evaluate(
        """() => ({
          tipo: typeof S.pivotStudies,
          lista: Array.isArray((S.pivotStudies || {}).studies),
          versao: (S.pivotStudies || {}).schemaVersion,
          quantos: ((S.pivotStudies || {}).studies || []).length
        })"""
    )
    assert forma["tipo"] == "object", f"{rotulo}: S.pivotStudies com tipo {forma['tipo']}"
    assert forma["lista"], f"{rotulo}: studies nao virou lista"
    assert forma["versao"] == 1, f"{rotulo}: schemaVersion {forma['versao']}"
    open_pivots(page)
    assert not erros, f"{rotulo}: pageerror {erros}"
    context.close()


def run_malformed_records_survive(browser, url):
    """Registro malformado e SANEADO na forma, nunca apagado em silencio."""
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
        """() => {
          const legado = structuredClone(DEFAULTS);
          legado.pivotStudies = {schemaVersion: 1, studies: [
            // sem id, instrumento fora da forma canonica, pivots ausente
            {instrumentId: 'eur/usd', periodStart: '2025-01-01', periodEnd: '2025-12-31'},
            // ids duplicados e campo desconhecido que precisa atravessar
            {id: 'dup', instrumentId: 'GBPUSD', periodStart: '2025-01-01', periodEnd: '2025-06-30',
             observacaoFutura: 'preservar', pivots: [
               {id: 'p1', timeframe: 'h4', startDatetime: '2025-02-01T00:00:00', startPrice: 1,
                endDatetime: '2025-02-02T00:00:00', endPrice: 2, maxCorrectionPct: 10, campoNovo: 'x'},
               {id: 'p1', timeframe: 'D1', startDatetime: 'lixo', startPrice: 'texto',
                endDatetime: '', endPrice: null, maxCorrectionPct: 999}
             ]},
            'isto nao e um estudo'
          ]};
          localStorage.setItem('jpwealth_v9_state', JSON.stringify(legado));
        }"""
    )
    page.reload()
    page.wait_for_function("() => window.JPWPivots && typeof S === 'object'")
    resultado = page.evaluate(
        """() => {
          const st = S.pivotStudies.studies;
          const gbp = st.find(s => s.instrumentId === 'GBPUSD');
          return {
            estudos: st.length,
            canonizado: st.some(s => s.instrumentId === 'EURUSD'),
            comId: st.every(s => typeof s.id === 'string' && s.id.length > 0),
            pivotsArray: st.every(s => Array.isArray(s.pivots)),
            campoDesconhecido: gbp && gbp.observacaoFutura === 'preservar',
            pivotsGbp: gbp ? gbp.pivots.length : -1,
            idsUnicos: gbp ? new Set(gbp.pivots.map(p => p.id)).size : -1,
            campoNovoPivot: gbp && gbp.pivots[0].campoNovo === 'x',
            timeframeNormalizado: gbp && gbp.pivots[0].timeframe === 'H4',
            derivaveis: gbp ? gbp.pivots.filter(p => window.JPWPivots.math.derive(p)).length : -1
          };
        }"""
    )
    assert resultado["estudos"] == 2, f"estudos apos saneamento: {resultado['estudos']}"
    assert resultado["canonizado"], "instrumentId 'eur/usd' nao foi canonizado para EURUSD"
    assert resultado["comId"], "estudo ficou sem id"
    assert resultado["pivotsArray"], "pivots ausente nao virou lista"
    assert resultado["campoDesconhecido"], "campo desconhecido do estudo foi descartado"
    assert resultado["pivotsGbp"] == 2, "pivot malformado foi APAGADO em vez de preservado"
    assert resultado["idsUnicos"] == 2, "ids duplicados nao foram desambiguados"
    assert resultado["campoNovoPivot"], "campo desconhecido do pivot foi descartado"
    assert resultado["timeframeNormalizado"], "timeframe minusculo nao foi normalizado"
    assert resultado["derivaveis"] == 1, "o pivot incoerente entrou na estatistica"
    assert not erros, f"pageerror com registros malformados: {erros}"
    context.close()


def main():
    run_no_hardcoded_instruments()
    run_threshold_declared_once()
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()

            # Dominio puro.
            context, page, observed = prepare_page(browser, url)
            run_canonical(page)
            run_direction_and_ranges(page)
            run_invalid_prices(page)
            run_duration(page)
            run_correction_rule(page)
            run_correction_out_of_domain(page)
            run_validation(page)
            run_overlap(page)
            run_stats_empty_and_single(page)
            run_stats_sample(page)
            run_stats_criterion_scope(page)
            run_top(page)
            run_median_direct(page)
            run_sorting(page)
            assert not observed["pageerror"], f"pageerror no dominio: {observed['pageerror']}"
            context.close()

            # Interface e persistencia, em contexto proprio para partir de
            # localStorage limpo. O confirm() e aceito automaticamente: o fluxo
            # do teste sempre quer prosseguir.
            context, page, observed = prepare_page(browser, url)
            page.on("dialog", lambda dialog: dialog.accept())
            open_pivots(page)
            run_selector_is_derived(page)
            run_create_and_register(page)
            run_live_calculation_does_not_persist(page)
            run_edit_updates_in_place(page)
            run_outside_criterion_is_kept(page)
            run_form_belongs_to_selected_study(page)
            run_multiple_studies_same_instrument(page)
            primeiro, _ = run_no_leak_between_instruments(page)
            run_no_inference_language(page)
            run_reload_keeps_data(page)
            open_pivots(page)
            run_backup_roundtrip(page)
            run_no_operational_mutation(page)
            run_removed_instrument_keeps_study(page, primeiro)
            run_delete_pivot(page, primeiro)
            # Estes tres SUBSTITUEM S.pivotStudies inteiro para montar o cenario;
            # por isso vem no fim, depois dos blocos que dependem do estado
            # acumulado pelo fluxo acima.
            run_broken_records_are_reachable(page)
            run_create_study_asks_before_discarding(page)
            run_workspace_repaints_after_state_swap(page)
            assert not observed["pageerror"], f"pageerror no fluxo de UI: {observed['pageerror']}"
            context.close()

            # Estado anterior a feature: a chave nem existe.
            run_state_compat(browser, url, "delete s.pivotStudies;", "estado legado sem a chave")
            run_state_compat(browser, url, "s.pivotStudies = 'isto nao e um objeto';", "agregado com tipo errado")
            run_state_compat(browser, url, "s.pivotStudies = {schemaVersion: 0, studies: {}};", "studies como mapa")
            run_malformed_records_survive(browser, url)
            browser.close()
    finally:
        server.shutdown()
    print("PIVOT STUDIES TEST PASS")


if __name__ == "__main__":
    main()
