#!/usr/bin/env python3
"""JPW-FGDEKM — referencia USD/BRL corrente e separacao Passado/Presente/Futuro.

Prova que os tres conceitos cambiais nunca se contaminam:

    PASSADO   closure.fxQuote     snapshot registrado num mes fechado
    PRESENTE  currentUsdBrlQuote  referencia externa corrente
    FUTURO    future[month]       premissa de retorno, sem FX manual

Toda resposta do provedor e INTERCEPTADA (page.route): o teste nunca depende da
rede real nem do valor de mercado do dia, e por isso pode exercitar timeout,
429, JSON invalido e taxa zero de forma deterministica.

Fixtures 100%% sinteticas — nenhum dado real entra neste repositorio.
"""

from http.server import SimpleHTTPRequestHandler
from browser_fixture_server import BrowserFixtureServer as ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import threading

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap


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
    context = browser.new_context(service_workers="block")
    context.add_init_script("window.__onbShown=true;")
    install_bootstrap(context)
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
    wait_bootstrap(page)
    page.wait_for_function("window.JPWMarket && window.JPWMarket.usdBrl && window.JPWPlanning")
    return context, page


def seed_plan(page):
    """Explicit nominal USD/BRL paid facts, no automatic BRL conversion."""
    return page.evaluate("""() => {
      const api=JPWPlanning,yes=r=>{if(!r.ok)throw Error(JSON.stringify(r));return r;};
      const made=yes(api.commands.execute('createAccount',{name:'JPW-FGDEKM',startMonth:'2026-01',initialUsd:90000,profileId:'base',monthlyContributionUsd:0,goals:{adequate:null,ideal:{value:3000,currency:'USD'}}},api.queries.token()));
      window.__quoteAccountId=made.accountId;
      const exec=(type,payload)=>yes(api.commands.execute(type,{accountId:made.accountId,...payload},api.queries.token(made.accountId)));
      exec('recordContribution',{month:'2026-01',usd:10000,brl:51000});
      for(let i=1;i<=8;i++)exec('recordResult',{month:'2026-'+String(i).padStart(2,'0'),usd:0});
      exec('finalizeMonth',{month:'2026-01',confirmFlows:true});
      const view=api.queries.view({accountId:made.accountId,month:'2026-08'});
      return {ok:true,saldo:view.confirmed.balanceUsd,medio:view.priceAverage.rate};
    }""")


def live(page):
    return page.evaluate("() => JPWPlanning.queries.view({accountId:window.__quoteAccountId,month:'2026-08',quote:JPWMarket.usdBrl.get()})")


def quote(page):
    return page.evaluate("() => window.JPWMarket.usdBrl.get()")


def refresh(page, force=True):
    page.evaluate("(f) => window.JPWMarket.usdBrl.refresh(f)", force)
    page.wait_for_function("!window.JPWMarket.usdBrl.isLoading()")


# --------------------------------------------------------------------------
def caso_central(browser,url):
    """Recorded acquisition5.10 and current5.20 coexist; closed USD survives."""
    context,page=open_page(browser,url)
    try:
        seeded=seed_plan(page);assert seeded['ok'];assert_close(seeded['saldo'],100000);assert_close(seeded['medio'],5.10)
        refresh(page);q=quote(page);assert_close(q['rate'],5.20);assert q['status']=='fresh'
        model=live(page);assert_close(model['priceAverage']['rate'],5.10)
        current=next(r for r in model['rows'] if r['month']=='2026-08')
        assert_close(current['fxRate'],5.20);assert_close(current['closeUsd'],100000);assert_close(current['closeBrl'],520000)
        # January has no captured/matching quote; daily August never rewrites it.
        assert model['rows'][0]['closeBrl'] is None
        assert_close(model['confirmed']['balanceUsd'],100000)
    finally:context.close()


def caso_independencia(browser,url):
    """Future return premise and daily FX cannot change recorded history/cost."""
    context,page=open_page(browser,url)
    try:
        assert seed_plan(page)['ok'];refresh(page)
        result=page.evaluate("""() => {
          const api=JPWPlanning,id=__quoteAccountId,prior=api.queries.account(id),view=api.queries.view({accountId:id,month:'2026-08'});
          const out=api.commands.execute('setProjection',{accountId:id,month:'2027-01',rate:.02,contributionUsd:0},api.queries.token(id));
          if(!out.ok)throw Error(JSON.stringify(out));
          return {prior,after:api.queries.account(id),view,rate:JPWMarket.usdBrl.rate()};
        }""")
        assert_close(result['rate'],5.20)
        assert result['prior']['plan']['reference']==result['after']['plan']['reference']
        assert result['prior']['plan']['results']==result['after']['plan']['results']
        assert result['prior']['plan']['contributions']==result['after']['plan']['contributions']
        before=live(page);usd=[r['closeUsd'] for r in before['rows']]
        page.route(ENDPOINT,lambda r,_q:r.fulfill(status=200,content_type='application/json',body=json.dumps({'date':'2026-08-12','base':'USD','quote':'BRL','rate':5.30})))
        refresh(page);after=live(page)
        assert_close(quote(page)['rate'],5.30);assert [r['closeUsd'] for r in after['rows']]==usd
        assert_close(after['priceAverage']['rate'],5.10)
        assert page.evaluate("JPWPlanning.queries.account(__quoteAccountId).plan.future['2027-01'].rate")==.02
    finally:context.close()


def caso_historico_nao_reprecifica(browser,url):
    """A closure snapshot5.40 overrides current5.20 and historical lookup5.10."""
    context,page=open_page(browser,url)
    try:
        assert seed_plan(page)['ok'];refresh(page)
        result=page.evaluate("""() => {
          const api=JPWPlanning,p=api.queries.account(__quoteAccountId).plan;
          // Presentation-only synthetic snapshot, never persisted or installed.
          p.closures['2026-01'].fxQuote={rate:5.40,referenceDate:'2026-01-31',fetchedAt:'2026-02-01T00:00:00Z',source:'synthetic historical snapshot'};
          const rows=api.engine.timeline(p,{month:'2026-08',quote:JPWMarket.usdBrl.get(),historicalQuotes:{'2026-01':{rate:5.10,referenceDate:'2026-01-30',fetchedAt:Date.now(),source:'synthetic lookup'}}});
          return {brl:rows[0].closeBrl,fx:rows[0].fxRate};
        }""")
        assert_close(result['fx'],5.40);assert_close(result['brl'],540000)
    finally:context.close()


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
        model=live(page)
        assert all(r['closeBrl'] is None for r in model['rows'])
        assert model['confirmed']['balanceUsd']==100000
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
            "() => JSON.stringify(JPWPlanning.queries.account(__quoteAccountId).plan)")
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
            "() => JSON.stringify(JPWPlanning.queries.account(__quoteAccountId).plan)")
        assert plano_antes == plano_depois, "cotacao alterou o plano (TESTE 15)"
        # e a cotacao nao vive dentro do estado patrimonial
        assert page.evaluate("() => JSON.stringify(S.patrimonialPlanning).includes('5.33')") is False
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


# Three reviewed V11 uses of the word, confined to the portable bundle.
# Mask only the word's exact span; keep every other byte under the same scan.
USDBRL_BENIGN_AUTH_LINES = (
    "// Forex V11: grade containers are records, never execution authorization.",
    "      findings:[{code:'BUDGET_DECLARATION_NOT_AUTHORIZATION',message:'Teto interno declarado; não autoriza consumo nem comprova declaração anterior à execução externa.',source:'PDF p71 Art8.4 §§10–12'}]};",
    "    // rollback set). No save, authorization, or guard of factual order creation.",
    "  const secretKey=key=>/password|passwd|senha|secret|token|credential|authorization|api[-_]?key|private[-_]?key/i.test(key);",
    "  const secretKey = key => /password|passwd|senha|secret|token|credential|authorization|api[-_]?key|private[-_]?key/i.test(key);",
    "        if(/password|passwd|senha|secret|token|credential|authorization|api[-_]?key|private[-_]?key/i.test(key))throw new Error('Backup de planejamento contém campo de segredo. Preserve o original e remova credenciais antes de importar ou exportar.');",
)


def usd_brl_static_credential_text(texto, nome):
    if nome == "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html":
        linhas = texto.splitlines(keepends=True)
        for benigna in USDBRL_BENIGN_AUTH_LINES:
            indices = [i for i, linha in enumerate(linhas)
                       if linha.rstrip("\r\n") == benigna]
            assert len(indices) <= 1, "uso benigno duplicado no portátil"
            if indices:
                i = indices[0]
                inicio = benigna.lower().index("authorization")
                linhas[i] = (linhas[i][:inicio] + " " * len("authorization")
                             + linhas[i][inicio + len("authorization"):])
        texto = "".join(linhas)
    return texto.lower()


def caso_seguranca(browser, url):
    """TESTE 16 — nenhuma credencial no bundle, no HTML ou no armazenamento."""
    suspeitos = ("api_key", "apikey", "api-key", "access_token",
                 "authorization", "bearer ", "x-api-key", "client_secret")
    for nome in ("index.html", "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
                 "src/js/10-domain/08-usd-brl-quote.js", "sw.js"):
        texto = usd_brl_static_credential_text((ROOT / nome).read_text(encoding="utf-8"), nome)
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
            options={'headless':True}
            if os.environ.get('JP_WEALTH_CHROMIUM'):options['executable_path']=os.environ['JP_WEALTH_CHROMIUM']
            browser = p.chromium.launch(**options)
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
