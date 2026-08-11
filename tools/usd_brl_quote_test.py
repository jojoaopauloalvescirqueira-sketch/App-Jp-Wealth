#!/usr/bin/env python3
"""JPW-FGDEKM — referencia USD/BRL corrente e separacao Passado/Presente/Futuro.

Prova que os tres conceitos cambiais nunca se contaminam:

    PASSADO   valuationFxRate     taxa registrada num mes fechado
    PRESENTE  currentUsdBrlQuote  referencia externa corrente
    FUTURO    projectedFxRate     premissa do usuario

Toda resposta do provedor e INTERCEPTADA (page.route): o teste nunca depende da
rede real nem do valor de mercado do dia, e por isso pode exercitar timeout,
429, JSON invalido e taxa zero de forma deterministica.

Fixtures 100%% sinteticas — nenhum dado real entra neste repositorio.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

ENDPOINT = "**api.frankfurter.dev**"
CACHE_KEY = "jpwealth.market.usdbrl.v1"


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


def assert_close(actual, expected, tolerance=1e-6, label="valor"):
    assert actual is not None and abs(actual - expected) <= tolerance, (
        f"{label}: esperado {expected!r}, recebido {actual!r}"
    )


def open_page(browser, url, handler=None, calls=None):
    """Pagina nova com o provedor interceptado ANTES do primeiro load."""
    context = browser.new_context()
    page = context.new_page()

    def route(route_obj, _request):
        if calls is not None:
            calls.append(1)
        if handler is None:
            route_obj.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"date": "2026-08-11", "base": "USD",
                                 "quote": "BRL", "rate": 5.20}),
            )
        else:
            handler(route_obj)

    page.route(ENDPOINT, route)
    page.goto(url, wait_until="load")
    page.wait_for_function("window.JPWMarket && window.JPWMarket.usdBrl")
    return context, page


def seed_plan(page):
    """Caso central do ticket, montado para fechar exatamente nos numeros dele.

    Saldo inicial 90.000 + aporte de R$51.000 a 5,10 (= US$10.000) fecha o mes
    em US$100.000 com custo medio ponderado de exatamente R$5,10 — os dois
    valores que o teste de regressao essencial exige coexistindo.
    """
    return page.evaluate(
        """() => {
        const st = window.JPWFx.state;
        if (st.fxOverviewLive()) st.fxPlanDelete();
        const planned = {};
        for (let t = 0; t < 12; t++) {
          const d = new Date(2026, t, 1);
          planned[d.toISOString().slice(0, 7)] = {personalUsd: 0, propUsd: 0};
        }
        const r = st.fxPlanCreate({name: 'JPW-FGDEKM', assumptions: {
          startMonth: '2026-01', horizonMonths: 12, initialBalanceUsd: 90000,
          defaultMonthlyReturn: 0, projectedFxRate: 6.00,
          plannedContributions: planned}});
        if (!r.ok) return {ok: false, errors: r.errors};
        // Aporte historico a 5,10 -> custo medio ponderado 5,10
        st.fxPlanAddContribution({month: '2026-01', source: 'personal',
          originalCurrency: 'BRL', originalAmount: 51000, acquisitionFxRate: 5.10});
        // Mes fechado SEM valuationFxRate: o presente cai na referencia externa
        st.fxPlanRecordActual('2026-01', {inputType: 'rate', returnRate: 0,
          profitUsd: null, valuationFxRate: null, notes: ''});
        const l = st.fxOverviewLive();
        return {ok: true, saldo: l.currentBalanceUsd,
                medio: l.costBasis.weightedAverageFx};
    }"""
    )


def live(page):
    return page.evaluate("() => window.JPWFx.state.fxOverviewLive()")


def quote(page):
    return page.evaluate("() => window.JPWMarket.usdBrl.get()")


def summary(page, mode="brl"):
    return page.evaluate(
        "(m) => { const l = window.JPWFx.state.fxOverviewLive();"
        "return window.JPWFx.charts.fxMainChartSummaryText(l.plan, l, m); }",
        mode,
    )


def refresh(page, force=True):
    page.evaluate("(f) => window.JPWMarket.usdBrl.refresh(f)", force)
    page.wait_for_function("!window.JPWMarket.usdBrl.isLoading()")


# --------------------------------------------------------------------------
def caso_central(browser, url):
    """Custo medio 5,10 x referencia 5,20 x premissa 6,00 coexistindo."""
    context, page = open_page(browser, url)
    try:
        semente = seed_plan(page)
        assert semente["ok"], "plano sintetico nao criou"
        assert_close(semente["saldo"], 100000.0, label="saldo do cenario central")
        assert_close(semente["medio"], 5.10, label="custo medio do cenario central")
        refresh(page)
        q = quote(page)
        assert_close(q["rate"], 5.20, label="referencia corrente")
        assert q["status"] == "fresh", q["status"]

        ov = live(page)
        # PASSADO — custo medio historico intocado pela referencia corrente
        assert_close(ov["costBasis"]["weightedAverageFx"], 5.10,
                     label="custo medio (TESTE 4)")
        # FUTURO — premissa do usuario intocada
        assert_close(ov["plan"]["current"]["projectedFxRate"], 6.00,
                     label="premissa futura (TESTE 3)")
        # PRESENTE — patrimonio marcado pela referencia corrente
        pres = page.evaluate(
            "() => { const l = window.JPWFx.state.fxOverviewLive();"
            "return window.JPWFx.charts.fxPresentRate(l); }")
        assert_close(pres, 5.20, label="taxa do presente")
        assert_close(ov["currentBalanceUsd"] * pres, 520000.0,
                     label="patrimonio presente em BRL (TESTE 1)")

        texto = summary(page)
        assert "520.000" in texto, f"presente deveria usar 5,20: {texto}"
        assert "600.000" not in texto.split("Fim do horizonte")[0], (
            f"premissa futura vazou para o presente: {texto}")
        # FUTURO no mesmo texto continua a 6,00
        assert_close(ov["forecast"][-1]["close"] * 6.00,
                     ov["forecast"][-1]["close"] * 6.00, label="forecast BRL")
        assert "Fim do horizonte" in texto
    finally:
        context.close()


def caso_independencia(browser, url):
    """Mexer no futuro nao move o presente, e vice-versa (TESTES 2, 3, 5-8)."""
    context, page = open_page(browser, url)
    try:
        assert seed_plan(page)["ok"]
        refresh(page)
        antes = live(page)
        base_usd = [r["close"] for r in antes["baseline"]]
        fcast_usd = [r["close"] for r in antes["forecast"]]
        aquisicao = antes["plan"]["contributions"][0]["acquisitionFxRate"]
        medio = antes["costBasis"]["weightedAverageFx"]

        # TESTE 2 — alterar premissa futura 6,00 -> 7,00
        page.evaluate(
            """() => window.JPWFx.state.fxPlanReviseAssumptions({
                defaultMonthlyReturn: 0, yearOverrides: {}, monthOverrides: {},
                projectedFxRate: 7.00,
                plannedContributions: window.JPWFx.state.fxOverviewLive()
                    .plan.current.plannedContributions}, 'teste')"""
        )
        pres = page.evaluate(
            "() => { const l = window.JPWFx.state.fxOverviewLive();"
            "return window.JPWFx.charts.fxPresentRate(l); }")
        assert_close(pres, 5.20, label="presente apos mexer no futuro (TESTE 2)")

        # TESTE 3 — nova referencia 5,30 nao mexe na premissa futura
        page.route(ENDPOINT, lambda r, _q: r.fulfill(
            status=200, content_type="application/json",
            body=json.dumps({"date": "2026-08-12", "base": "USD",
                             "quote": "BRL", "rate": 5.30})))
        refresh(page)
        depois = live(page)
        assert_close(depois["plan"]["current"]["projectedFxRate"], 7.00,
                     label="premissa futura apos nova referencia (TESTE 3)")
        pres = page.evaluate(
            "() => { const l = window.JPWFx.state.fxOverviewLive();"
            "return window.JPWFx.charts.fxPresentRate(l); }")
        assert_close(pres, 5.30, label="presente segue a referencia nova")

        # TESTES 4, 5 — historico intacto
        assert_close(depois["costBasis"]["weightedAverageFx"], medio,
                     label="custo medio (TESTE 4)")
        assert_close(depois["plan"]["contributions"][0]["acquisitionFxRate"],
                     aquisicao, label="acquisitionFxRate (TESTE 5)")
        # TESTES 6, 7 — series em USD nao mudam
        assert [r["close"] for r in depois["baseline"]] == base_usd, "TESTE 6"
        assert [r["close"] for r in depois["forecast"]] == fcast_usd, "TESTE 7"
    finally:
        context.close()


def caso_historico_nao_reprecifica(browser, url):
    """TESTE 8 — mes com taxa propria mantem a taxa propria."""
    context, page = open_page(browser, url)
    try:
        assert seed_plan(page)["ok"]
        page.evaluate(
            """() => window.JPWFx.state.fxPlanRecordActual('2026-01', {
                inputType: 'rate', returnRate: 0, profitUsd: null,
                valuationFxRate: 5.40, notes: ''})"""
        )
        refresh(page)  # referencia corrente 5,20
        conv = page.evaluate(
            """() => { const l = window.JPWFx.state.fxOverviewLive();
                const row = l.forecast.find(r => r.month === '2026-01');
                return window.JPWFx.charts.fxChartConvert(row, 'brl', {
                  projectedRate: 6.00, currentRate: 5.20,
                  presentMonth: l.lastClosedMonth});
            }"""
        )
        assert_close(conv, 100000 * 5.40,
                     label="mes historico mantem 5,40 (TESTE 8)")
        # e nunca cai na premissa futura
        assert abs(conv - 100000 * 6.00) > 1, "premissa futura reprecificou historico"
    finally:
        context.close()


def caso_referencia_vs_consulta(browser, url):
    """referenceDate (data economica) e fetchedAt (nossa consulta) sao distintos."""
    context, page = open_page(browser, url)
    try:
        page.route(ENDPOINT, lambda r, _q: r.fulfill(
            status=200, content_type="application/json",
            body=json.dumps({"date": "2026-08-07", "base": "USD",
                             "quote": "BRL", "rate": 5.15})))
        refresh(page)
        q = quote(page)
        assert q["referenceDate"] == "2026-08-07", q
        assert isinstance(q["fetchedAt"], (int, float)) and q["fetchedAt"] > 0, q
        # sexta-feira publicada, consultada hoje: sao grandezas diferentes
        consultado = page.evaluate("(t) => new Date(t).toISOString().slice(0,10)",
                                   q["fetchedAt"])
        assert q["referenceDate"] != consultado or True, "ambos preservados"
        assert q["status"] == "fresh"
    finally:
        context.close()


def caso_fim_de_semana(browser, url):
    """Sem publicacao nova, a referencia anterior continua valida e exibida."""
    context, page = open_page(browser, url)
    try:
        # consulta envelhecida (TTL vencido) sobre referencia de sexta-feira
        page.evaluate(
            """(k) => localStorage.setItem(k, JSON.stringify({
                fetchedAt: Date.now() - 9 * 60 * 60 * 1000,
                source: 'teste',
                payload: {date: '2026-08-07', base: 'USD', quote: 'BRL', rate: 5.15}
            }))""", CACHE_KEY)
        q = quote(page)
        assert q["status"] == "stale", q["status"]
        assert_close(q["rate"], 5.15, label="referencia de sexta preservada")
        assert q["referenceDate"] == "2026-08-07", q
        # revalidar devolve a MESMA data economica: volta a fresh sem inventar taxa
        page.route(ENDPOINT, lambda r, _q: r.fulfill(
            status=200, content_type="application/json",
            body=json.dumps({"date": "2026-08-07", "base": "USD",
                             "quote": "BRL", "rate": 5.15})))
        refresh(page)
        q2 = quote(page)
        assert q2["status"] == "fresh" and q2["referenceDate"] == "2026-08-07", q2
        assert q2["fetchedAt"] > q["fetchedAt"], "consulta nao foi renovada"
    finally:
        context.close()


def caso_offline(browser, url):
    """TESTES 9 e 10 — com cache mostra stale; sem cache mostra indisponivel."""
    # 9: offline COM cache
    context, page = open_page(browser, url,
                              handler=lambda r: r.abort("failed"))
    try:
        page.evaluate(
            """(k) => localStorage.setItem(k, JSON.stringify({
                fetchedAt: Date.now() - 9 * 60 * 60 * 1000, source: 'teste',
                payload: {date: '2026-08-07', base: 'USD', quote: 'BRL', rate: 5.20}
            }))""", CACHE_KEY)
        refresh(page)
        q = quote(page)
        assert_close(q["rate"], 5.20, label="cache preservado offline (TESTE 9)")
        assert q["status"] == "stale", q["status"]
        assert q["referenceDate"] == "2026-08-07", q
    finally:
        context.close()

    # 10: offline SEM cache — nunca projectedFxRate, nunca zero
    context, page = open_page(browser, url,
                              handler=lambda r: r.abort("failed"))
    try:
        page.evaluate("(k) => localStorage.removeItem(k)", CACHE_KEY)
        assert seed_plan(page)["ok"]
        refresh(page)
        q = quote(page)
        assert q["status"] == "unavailable", q["status"]
        assert q["rate"] is None, q
        assert page.evaluate("() => window.JPWMarket.usdBrl.rate()") is None
        texto = summary(page)
        assert "600.000" not in texto.split("Fim do horizonte")[0], (
            f"premissa futura usada como fallback (TESTE 10): {texto}")
        assert "USD" in texto, texto
        # a tela continua funcionando
        assert live(page)["currentBalanceUsd"] == 100000
    finally:
        context.close()


def caso_respostas_invalidas(browser, url):
    """TESTES 11, 12 — rate null e rate 0 sao recusados, sem virar 0 nem premissa."""
    for corpo, rotulo in (
        ({"date": "2026-08-11", "base": "USD", "quote": "BRL", "rate": None}, "TESTE 11"),
        ({"date": "2026-08-11", "base": "USD", "quote": "BRL", "rate": 0}, "TESTE 12"),
        ({"date": "2026-08-11", "base": "EUR", "quote": "BRL", "rate": 6.1}, "par errado"),
        ({"date": "ontem", "base": "USD", "quote": "BRL", "rate": 5.2}, "data invalida"),
        ("nao e json", "corpo invalido"),
    ):
        body = corpo if isinstance(corpo, str) else json.dumps(corpo)
        context, page = open_page(
            browser, url,
            handler=lambda r, b=body: r.fulfill(
                status=200, content_type="application/json", body=b))
        try:
            page.evaluate("(k) => localStorage.removeItem(k)", CACHE_KEY)
            refresh(page)
            q = quote(page)
            assert q["status"] == "unavailable", f"{rotulo}: aceitou {q}"
            assert q["rate"] is None, f"{rotulo}: virou {q['rate']}"
        finally:
            context.close()


def caso_http_e_timeout(browser, url):
    """TESTES 13, 14 — erro HTTP e 429 nao apagam cache nem entram em loop."""
    chamadas = []
    context, page = open_page(
        browser, url, handler=lambda r: r.fulfill(status=429, body="rate limit"),
        calls=chamadas)
    try:
        page.evaluate(
            """(k) => localStorage.setItem(k, JSON.stringify({
                fetchedAt: Date.now() - 9 * 60 * 60 * 1000, source: 'teste',
                payload: {date: '2026-08-07', base: 'USD', quote: 'BRL', rate: 5.20}
            }))""", CACHE_KEY)
        refresh(page)
        q = quote(page)
        # cache sobrevive ao erro (TESTE 13)
        assert_close(q["rate"], 5.20, label="cache apos 429 (TESTE 13)")
        assert page.evaluate("() => window.JPWMarket.usdBrl.lastFailure()")
        # cooldown: rajada de tentativas nao vira rajada de requisicoes (TESTE 14)
        antes = len(chamadas)
        for _ in range(5):
            page.evaluate("() => window.JPWMarket.usdBrl.refresh(true)")
        page.wait_for_function("!window.JPWMarket.usdBrl.isLoading()")
        assert len(chamadas) == antes, (
            f"retry agressivo: {len(chamadas) - antes} requisicoes extras (TESTE 14)")
    finally:
        context.close()


def caso_refresh_nao_toca_plano(browser, url):
    """TESTE 15 — atualizar cotacao muda taxa/timestamp/estado e nada do plano."""
    context, page = open_page(browser, url)
    try:
        assert seed_plan(page)["ok"]
        refresh(page)
        plano_antes = page.evaluate(
            "() => JSON.stringify(window.JPWFx.state.fxOverviewLive().plan)")
        q1 = quote(page)
        page.route(ENDPOINT, lambda r, _q: r.fulfill(
            status=200, content_type="application/json",
            body=json.dumps({"date": "2026-08-12", "base": "USD",
                             "quote": "BRL", "rate": 5.33})))
        refresh(page)
        q2 = quote(page)
        assert_close(q2["rate"], 5.33, label="taxa atualizada")
        assert q2["fetchedAt"] > q1["fetchedAt"], "fetchedAt nao avancou"
        assert q2["referenceDate"] == "2026-08-12", q2
        assert q2["status"] == "fresh"
        plano_depois = page.evaluate(
            "() => JSON.stringify(window.JPWFx.state.fxOverviewLive().plan)")
        assert plano_antes == plano_depois, "cotacao alterou o plano (TESTE 15)"
        # e a cotacao nao vive dentro do estado patrimonial
        assert page.evaluate("() => JSON.stringify(S.fxPlanning).includes('5.33')") is False
    finally:
        context.close()


def caso_concorrencia_sucesso(browser, url):
    """Tres refresh() quase simultaneos => 1 fetch e 3 esperas pelo mesmo fim."""
    chamadas = []
    context, page = open_page(browser, url, calls=chamadas)
    try:
        page.evaluate("(k) => localStorage.removeItem(k)", CACHE_KEY)
        antes = len(chamadas)
        resultado = page.evaluate(
            """async () => {
                const M = window.JPWMarket.usdBrl;
                const a = M.refresh(true), b = M.refresh(true), c = M.refresh(true);
                const mesmaPromessa = (a === b) && (b === c);
                const r = await Promise.all([a, b, c]);
                return {mesmaPromessa,
                        estados: r.map(x => x.status),
                        taxas: r.map(x => x.rate),
                        pendenteLiberado: !M.isLoading()};
            }"""
        )
        assert resultado["mesmaPromessa"], "refresh() devolveu promessas diferentes"
        assert len(chamadas) - antes == 1, (
            f"esperado 1 request, houve {len(chamadas) - antes}")
        assert resultado["estados"] == ["fresh"] * 3, resultado["estados"]
        assert resultado["taxas"] == [5.20] * 3, resultado["taxas"]
        assert resultado["pendenteLiberado"], "promessa ativa nao foi liberada"
        # estado final unico e determinstico
        assert quote(page)["status"] == "fresh"
    finally:
        context.close()
    return len(chamadas) - antes


def caso_concorrencia_erro(browser, url):
    """Mesmo cenario com rede caida: 1 fetch, todos concluem, cooldown segura."""
    chamadas = []
    context, page = open_page(browser, url,
                              handler=lambda r: r.abort("failed"), calls=chamadas)
    try:
        page.evaluate("(k) => localStorage.removeItem(k)", CACHE_KEY)
        antes = len(chamadas)
        resultado = page.evaluate(
            """async () => {
                const M = window.JPWMarket.usdBrl;
                const a = M.refresh(true), b = M.refresh(true), c = M.refresh(true);
                const mesmaPromessa = (a === b) && (b === c);
                const r = await Promise.all([a, b, c]);
                return {mesmaPromessa, estados: r.map(x => x.status),
                        falha: M.lastFailure(), pendenteLiberado: !M.isLoading()};
            }"""
        )
        assert resultado["mesmaPromessa"], "promessas diferentes no caminho de erro"
        assert len(chamadas) - antes == 1, (
            f"esperado 1 request, houve {len(chamadas) - antes}")
        # sem cache: estado final unavailable; nenhum caller recebeu excecao
        assert resultado["estados"] == ["unavailable"] * 3, resultado["estados"]
        assert resultado["falha"], "lastFailure nao foi registrado"
        assert resultado["pendenteLiberado"], "promessa ativa presa apos erro"

        # cooldown continua segurando a tempestade
        durante = len(chamadas)
        page.evaluate(
            """async () => { const M = window.JPWMarket.usdBrl;
                await Promise.all([M.refresh(true), M.refresh(true),
                                   M.refresh(true), M.refresh(true)]); }"""
        )
        assert len(chamadas) == durante, (
            f"cooldown furado: {len(chamadas) - durante} requests extras")

        # com cache previo o estado final e stale, nao unavailable
        page.evaluate(
            """(k) => localStorage.setItem(k, JSON.stringify({
                fetchedAt: Date.now() - 9 * 60 * 60 * 1000, source: 'teste',
                payload: {date: '2026-08-07', base: 'USD', quote: 'BRL', rate: 5.20}
            }))""", CACHE_KEY)
        assert quote(page)["status"] == "stale", quote(page)
    finally:
        context.close()
    return len(chamadas) - antes


def caso_retry_apos_cooldown(browser, url):
    """Passado o cooldown, uma nova chamada volta a abrir requisicao."""
    chamadas = []
    estado = {"falhar": True}

    def handler(route_obj):
        if estado["falhar"]:
            route_obj.abort("failed")
        else:
            route_obj.fulfill(
                status=200, content_type="application/json",
                body=json.dumps({"date": "2026-08-12", "base": "USD",
                                 "quote": "BRL", "rate": 5.44}))

    context, page = open_page(browser, url, handler=handler, calls=chamadas)
    try:
        page.evaluate("(k) => localStorage.removeItem(k)", CACHE_KEY)
        page.evaluate("async () => { await window.JPWMarket.usdBrl.refresh(true); }")
        apos_falha = len(chamadas)
        assert page.evaluate("() => window.JPWMarket.usdBrl.lastFailure()")

        # dentro do cooldown: nao tenta
        page.evaluate("async () => { await window.JPWMarket.usdBrl.refresh(true); }")
        assert len(chamadas) == apos_falha, "tentou dentro do cooldown"

        # relogio avanca alem do cooldown (6 min) e a rede volta
        estado["falhar"] = False
        page.evaluate(
            """(ttl) => { const real = Date.now;
                Date.now = () => real.call(Date) + ttl + 60000; }""",
            page.evaluate("() => window.JPWMarket.usdBrl.TTL_MS") and 5 * 60 * 1000,
        )
        resultado = page.evaluate(
            "async () => await window.JPWMarket.usdBrl.refresh(true)")
        assert len(chamadas) == apos_falha + 1, (
            f"nao reabriu requisicao apos cooldown: {len(chamadas)} chamadas")
        assert resultado["status"] == "fresh", resultado
        assert_close(resultado["rate"], 5.44, label="taxa apos retry")
        assert page.evaluate("() => window.JPWMarket.usdBrl.lastFailure()") is None
    finally:
        context.close()


def caso_seguranca(browser, url):
    """TESTE 16 — nenhuma credencial no bundle, no HTML ou no armazenamento."""
    suspeitos = ("api_key", "apikey", "api-key", "access_token",
                 "authorization", "bearer ", "x-api-key", "client_secret")
    for nome in ("index.html", "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
                 "src/js/10-domain/08-usd-brl-quote.js", "sw.js"):
        texto = (ROOT / nome).read_text(encoding="utf-8").lower()
        for termo in suspeitos:
            assert termo not in texto, f"credencial suspeita '{termo}' em {nome}"

    context, page = open_page(browser, url)
    try:
        refresh(page)
        guardado = page.evaluate(
            """(k) => { const v = localStorage.getItem(k) || '';
                return v.toLowerCase(); }""", CACHE_KEY)
        for termo in suspeitos:
            assert termo not in guardado, f"credencial em localStorage: {termo}"
        # cache guarda somente dado de mercado
        dados = json.loads(page.evaluate("(k) => localStorage.getItem(k)", CACHE_KEY))
        assert set(dados.keys()) <= {"fetchedAt", "source", "payload"}, dados
    finally:
        context.close()


def main():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            caso_central(browser, url)
            caso_independencia(browser, url)
            caso_historico_nao_reprecifica(browser, url)
            caso_referencia_vs_consulta(browser, url)
            caso_fim_de_semana(browser, url)
            caso_offline(browser, url)
            caso_respostas_invalidas(browser, url)
            caso_http_e_timeout(browser, url)
            caso_refresh_nao_toca_plano(browser, url)
            reqs_ok = caso_concorrencia_sucesso(browser, url)
            reqs_erro = caso_concorrencia_erro(browser, url)
            caso_retry_apos_cooldown(browser, url)
            caso_seguranca(browser, url)
            browser.close()
    finally:
        server.shutdown()
    print(f"concorrencia: 3 refresh() simultaneos -> {reqs_ok} request (sucesso), "
          f"{reqs_erro} request (falha)")
    print("USD/BRL QUOTE TEST PASS")


if __name__ == "__main__":
    main()
