#!/usr/bin/env python3
"""Caracterizacao do Planejamento FX: motor matematico puro e reservas FCR/FEO.

Executa a pagina modular servida por HTTP e usa somente as APIs publicas em
``window.JPWFx`` e ``reserveRequirementsCalc``. Cobre os casos 1-20 da
especificacao da tarefa (docs/work/ACTIVE-TASK.md), o requisito
Baseline x Forecast x Realizado e a caracterizacao da extracao de
``reserveCalc()`` do onboarding (mesma matematica, campo a campo).

Nenhuma fixture usa dados reais: a planilha historica contem anotacoes
pessoais e NUNCA entra neste repositorio; todos os valores abaixo sao
sinteticos.
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


def assert_close(actual, expected, tolerance=1e-9, label="valor"):
    assert actual is not None and abs(actual - expected) <= tolerance, (
        f"{label}: esperado {expected!r}, recebido {actual!r}"
    )


def prepare_page(browser, url, suppress_onboarding=True):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    if suppress_onboarding:
        context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    observed = {"pageerror": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.route(
        "**/api.frankfurter.dev/**",
        lambda route: route.fulfill(
            status=200, content_type="application/json", body='{"rates":{}}'
        ),
    )
    page.goto(url)
    page.wait_for_function("() => window.JPWFx && typeof reserveRequirementsCalc === 'function'")
    return context, page, observed


# Plano sintetico basico: fabrica no navegador com o proprio modelo publico.
MAKE_PLAN = """
(cfg) => {
  const plan = window.JPWFx.model.fxCreatePlan({
    name: 'Teste',
    now: '2026-01-15T12:00:00.000Z',
    assumptions: Object.assign({
      startMonth: '2026-01', horizonMonths: 12, initialBalanceUsd: 100,
      defaultMonthlyReturn: 0.05, yearOverrides: {}, monthOverrides: {},
      plannedContributions: {}, projectedFxRate: null
    }, cfg || {})
  });
  return plan;
}
"""


def run_engine_cases(page):
    ev = page.evaluate

    # CASOS 1/5/6: saldo 100, retorno 5%, sem aporte -> 105; retorno zero -> 100.
    rows = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{}});
        return window.JPWFx.engine.fxPlannedTimeline(plan.baseline).slice(0, 2);
    }}"""
    )
    assert_close(rows[0]["open"], 100, label="caso1 abertura")
    assert_close(rows[0]["profit"], 5, label="caso1 resultado")
    assert_close(rows[0]["close"], 105, label="caso1 fechamento")
    assert_close(rows[1]["open"], 105, label="caso1 encadeamento")
    zero = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{defaultMonthlyReturn: 0}});
        return window.JPWFx.engine.fxPlannedTimeline(plan.baseline)[0].close;
    }}"""
    )
    assert_close(zero, 100, label="caso5 retorno zero")

    # CASO 2: aporte 20 entra DEPOIS do resultado -> 125 (nunca 126).
    caso2 = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{plannedContributions: {{'2026-01': {{personalUsd: 20, propUsd: 0}}}}}});
        return window.JPWFx.engine.fxPlannedTimeline(plan.baseline)[0];
    }}"""
    )
    assert_close(caso2["close"], 125, label="caso2 fechamento")
    assert_close(caso2["profit"], 5, label="caso2 resultado nao inclui aporte do mes")

    # CASO 3: composicao 3 meses -> 100 * 1.05^3.
    caso3 = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{horizonMonths: 3}});
        const t = window.JPWFx.engine.fxPlannedTimeline(plan.baseline);
        return t[t.length - 1].close;
    }}"""
    )
    assert_close(caso3, 100 * 1.05**3, label="caso3 composicao")

    # CASO 4: retorno negativo.
    caso4 = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{defaultMonthlyReturn: -0.10}});
        return window.JPWFx.engine.fxPlannedTimeline(plan.baseline)[0].close;
    }}"""
    )
    assert_close(caso4, 90, label="caso4 retorno negativo")

    # CASO 7: aporte pessoal + prop firm separados por origem.
    caso7 = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{defaultMonthlyReturn: 0,
            plannedContributions: {{'2026-01': {{personalUsd: 10, propUsd: 5}}}}}});
        return window.JPWFx.engine.fxPlannedTimeline(plan.baseline)[0];
    }}"""
    )
    assert_close(caso7["personalUsd"], 10, label="caso7 pessoal")
    assert_close(caso7["propUsd"], 5, label="caso7 prop")
    assert_close(caso7["close"], 115, label="caso7 fechamento")

    # CASOS 8/20: horizontes 1, 12, 60, 120 geram exatamente N meses; 120 meses
    # sem drift relevante contra a forma fechada (tolerancia relativa 1e-9).
    for horizon in (1, 12, 60, 120):
        res = ev(
            f"""(h) => {{
            const make = {MAKE_PLAN};
            const plan = make({{horizonMonths: h, defaultMonthlyReturn: 0.01}});
            const t = window.JPWFx.engine.fxPlannedTimeline(plan.baseline);
            return {{n: t.length, close: t[t.length - 1].close,
                     first: t[0].month, last: t[t.length - 1].month}};
        }}""",
            horizon,
        )
        assert res["n"] == horizon, f"caso20 horizonte {horizon}: gerou {res['n']} meses"
        expected = 100 * 1.01**horizon
        assert_close(res["close"], expected, tolerance=abs(expected) * 1e-9,
                     label=f"caso8 forma fechada {horizon}m")
    assert res["first"] == "2026-01" and res["last"] == "2035-12", "caso8 datas do horizonte 120"

    # CASO 9: precedencia mes > ano > padrao.
    caso9 = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{startMonth: '2027-11', horizonMonths: 6,
            defaultMonthlyReturn: 0.015,
            yearOverrides: {{'2028': 0.012}}, monthOverrides: {{'2028-03': 0.008}}}});
        const t = window.JPWFx.engine.fxPlannedTimeline(plan.baseline);
        return t.map(r => [r.month, r.rate]);
    }}"""
    )
    expected_rates = {
        "2027-11": 0.015, "2027-12": 0.015, "2028-01": 0.012,
        "2028-02": 0.012, "2028-03": 0.008, "2028-04": 0.012,
    }
    for month, rate in caso9:
        assert_close(rate, expected_rates[month], label=f"caso9 taxa {month}")

    # CASOS 18/19: virada de ano continua (dez -> jan) e fevereiro de ano
    # bissexto presente na serie mensal.
    months = [m for m, _ in caso9]
    assert months == ["2027-11", "2027-12", "2028-01", "2028-02", "2028-03", "2028-04"], (
        f"caso18/19 sequencia de meses: {months}"
    )

    # CASO 11: cambio medio ponderado = soma BRL / soma USD (nunca media simples).
    caso11 = ev(
        """() => {
        const n = window.JPWFx.model.fxNormalizeContribution;
        const contributions = [
          n({month:'2026-01', source:'personal', originalCurrency:'BRL',
             originalAmount:10000, acquisitionFxRate:5.00}),
          n({month:'2026-02', source:'personal', originalCurrency:'BRL',
             originalAmount:10000, acquisitionFxRate:6.00}),
        ];
        return window.JPWFx.engine.fxCostBasis(contributions);
    }"""
    )
    assert_close(caso11["totalUsdAcquired"], 2000 + 10000 / 6, tolerance=1e-9, label="caso11 USD adquirido")
    assert_close(caso11["totalBrlInvested"], 20000, tolerance=1e-6, label="caso11 BRL investido")
    assert_close(caso11["weightedAverageFx"], 20000 / (2000 + 10000 / 6), tolerance=1e-9,
                 label="caso11 cambio medio")

    # CASO 12: credito USD-nativo (prop firm) nao altera o custo medio.
    caso12 = ev(
        """() => {
        const n = window.JPWFx.model.fxNormalizeContribution;
        const base = [
          n({month:'2026-01', source:'personal', originalCurrency:'BRL',
             originalAmount:10000, acquisitionFxRate:5.00}),
          n({month:'2026-02', source:'personal', originalCurrency:'BRL',
             originalAmount:10000, acquisitionFxRate:6.00}),
        ];
        const withProp = base.concat([n({month:'2026-03', source:'prop',
            originalCurrency:'USD', originalAmount:800})]);
        const a = window.JPWFx.engine.fxCostBasis(base);
        const b = window.JPWFx.engine.fxCostBasis(withProp);
        return {a: a.weightedAverageFx, b: b.weightedAverageFx,
                flag: withProp[2].affectsFxCostBasis,
                usd: withProp[2].usdAmount};
    }"""
    )
    assert caso12["flag"] is False, "caso12 USD-nativo deve nascer com affectsFxCostBasis=false"
    assert_close(caso12["usd"], 800, label="caso12 valor USD do credito")
    assert_close(caso12["b"], caso12["a"], label="caso12 custo medio inalterado")

    # CASOS 10/13 + REQUISITO ADICIONAL: fechar mes abaixo do plano, revisar
    # premissa futura e conferir Baseline x Forecast x Realizado.
    scenario = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const M = window.JPWFx.model, E = window.JPWFx.engine;
        let plan = make({{horizonMonths: 6, defaultMonthlyReturn: 0.05, projectedFxRate: 5.50}});
        // realizado de jan: -0.70% (entrada por taxa) + aporte pessoal de 10 via ledger
        plan.actuals['2026-01'] = M.fxNormalizeActual({{inputType:'rate', returnRate:-0.007,
            closedAt:'2026-02-01T10:00:00.000Z', updatedAt:'2026-02-01T10:00:00.000Z'}});
        plan.contributions.push(M.fxNormalizeContribution({{month:'2026-01', source:'personal',
            originalCurrency:'BRL', originalAmount:50, acquisitionFxRate:5.00,
            createdAt:'2026-01-20T00:00:00.000Z'}}));
        const before = {{
            baselineJan: E.fxPlannedTimeline(plan.baseline)[0].close,
            actual: E.fxActualTimeline(plan),
            forecast: E.fxForecastTimeline(plan)
        }};
        // revisao de premissa futura: 2% a.m. e projecao cambial 6.20
        plan = M.fxReviseAssumptions(plan, Object.assign({{}}, plan.current,
            {{defaultMonthlyReturn: 0.02, projectedFxRate: 6.20}}),
            {{now:'2026-02-05T09:00:00.000Z', note:'cenario revisado'}});
        const after = {{
            baseline: E.fxPlannedTimeline(plan.baseline),
            actual: E.fxActualTimeline(plan),
            forecast: E.fxForecastTimeline(plan),
            prevForecast: E.fxForecastAtRevision(plan, 0),
            cost: E.fxCostBasis(plan.contributions),
            overview: E.fxOverview(plan),
            revisions: plan.revisions.length,
            baselineDefault: plan.baseline.defaultMonthlyReturn,
            baselineFx: plan.baseline.projectedFxRate
        }};
        return {{before, after}};
    }}"""
    )
    # realizado: open 100, profit -0.7, aporte 10 (50 BRL / 5.00) -> close 109.3
    actual_row = scenario["after"]["actual"][0]
    assert_close(actual_row["profit"], -0.7, label="realizado resultado janeiro")
    assert_close(actual_row["contributionUsd"], 10, label="realizado aporte janeiro (ledger)")
    assert_close(actual_row["close"], 109.3, label="realizado fechamento janeiro")
    assert actual_row["derivedField"] == "usd", "entrada por taxa deriva o USD"
    # caso 10: realizado imutavel apos revisao de premissas
    assert scenario["before"]["actual"] == scenario["after"]["actual"], (
        "caso10: revisao de premissa alterou o realizado"
    )
    # baseline preservado (requisito adicional): 5% e cambio 5.50 originais
    assert_close(scenario["after"]["baselineDefault"], 0.05, label="baseline preservado (taxa)")
    assert_close(scenario["after"]["baselineFx"], 5.50, label="baseline preservado (fx projetado)")
    assert_close(scenario["after"]["baseline"][0]["close"], 105, label="baseline janeiro intacto")
    # forecast vigente parte do saldo REAL (109.3) com a nova premissa de 2%
    fev = scenario["after"]["forecast"][1]
    assert fev["phase"] == "forecast", "fevereiro deve ser projecao"
    assert_close(fev["open"], 109.3, label="forecast parte do fechamento real")
    assert_close(fev["close"], 109.3 * 1.02, label="forecast fevereiro com premissa revisada")
    # forecast anterior reconstruido da revisao preservada (premissa antiga de 5%)
    prev_fev = scenario["after"]["prevForecast"][1]
    assert_close(prev_fev["close"], 109.3 * 1.05, label="forecast anterior (premissa de 5%)")
    assert scenario["after"]["revisions"] == 1, "revisao deve ser registrada"
    # caso 13: revisao do cambio projetado nao tocou o custo historico de aquisicao
    assert_close(scenario["after"]["cost"]["weightedAverageFx"], 5.00,
                 label="caso13 custo de aquisicao intacto")
    # caso 17: planejado x realizado no overview
    var_jan = scenario["after"]["overview"]["varianceActualVsBaseline"][0]
    assert_close(var_jan["diffUsd"], 109.3 - 105, label="caso17 desvio USD janeiro")
    assert_close(scenario["after"]["overview"]["currentBalanceUsd"], 109.3,
                 label="overview patrimonio atual")

    # Entrada por USD deriva a taxa (dupla via sem divergencia) — metodologia MEI:
    # R_aj = (V_t - V_{t-1} - F_t) / V_{t-1}.
    usd_entry = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const M = window.JPWFx.model, E = window.JPWFx.engine;
        const plan = make({{horizonMonths: 3}});
        plan.actuals['2026-01'] = M.fxNormalizeActual({{inputType:'usd', profitUsd: 2.5,
            closedAt:'2026-02-01T00:00:00.000Z'}});
        plan.contributions.push(M.fxNormalizeContribution({{month:'2026-01', source:'prop',
            originalCurrency:'USD', originalAmount: 4}}));
        return E.fxActualTimeline(plan)[0];
    }}"""
    )
    assert usd_entry["derivedField"] == "rate", "entrada por USD deriva a taxa"
    assert_close(usd_entry["rate"], 2.5 / 100, label="taxa derivada = profit/open (R_aj)")
    assert_close(usd_entry["close"], 100 + 2.5 + 4, label="fechamento com credito prop")

    # Resumo anual derivado das datas (nunca blocos fixos).
    annual = ev(
        f"""() => {{
        const make = {MAKE_PLAN};
        const plan = make({{startMonth: '2026-11', horizonMonths: 4,
            defaultMonthlyReturn: 0.10}});
        const t = window.JPWFx.engine.fxPlannedTimeline(plan.baseline);
        return window.JPWFx.engine.fxAnnualSummary(t);
    }}"""
    )
    assert [a["year"] for a in annual] == ["2026", "2027"], "resumo anual por ano derivado"
    assert annual[0]["months"] == 2 and annual[1]["months"] == 2, "meses por ano"
    assert_close(annual[0]["composedReturn"], 1.10**2 - 1, label="retorno composto 2026")


def run_reserve_cases(page):
    ev = page.evaluate
    # CASOS 14/15/16 + caracterizacao da extracao de reserveCalc(): a funcao
    # compartilhada reproduz campo a campo a matematica original do onboarding
    # (15% do capital nominal, 6x despesas, coberturas, status, tom e deficit).
    scenarios = [
        # (capital, fcrCur, despesas, feoCur)
        (10000, 1500, 1000, 6000),   # exatamente nos minimos -> Regular/Regular
        (10000, 1200, 1000, 4500),   # deficit duplo
        (0, 0, 0, 0),                # bordas: divisoes por zero guardadas
        (200000, 45000, 3500, 12000),# FCR folgado, FEO insuficiente
    ]
    for capital, fcr_cur, monthly, feo_cur in scenarios:
        r = ev(
            "(args) => reserveRequirementsCalc({capital: args[0], fcrCurrent: args[1],"
            " monthlyExpenses: args[2], feoCurrent: args[3]})",
            [capital, fcr_cur, monthly, feo_cur],
        )
        fcr_req = capital * 0.15
        feo_req = monthly * 6
        assert_close(r["fcrReq"], fcr_req, label=f"FCR exigido ({capital})")
        assert_close(r["feoReq"], feo_req, label=f"FEO exigido ({monthly})")
        assert_close(r["fcrCoverage"], (fcr_cur / fcr_req * 100) if fcr_req > 0 else 0,
                     label="cobertura FCR")
        assert_close(r["feoCoverage"], (feo_cur / feo_req * 100) if feo_req > 0 else 0,
                     label="cobertura FEO")
        assert_close(r["feoMonths"], (feo_cur / monthly) if monthly > 0 else 0,
                     label="meses FEO")
        assert_close(r["fcrDiff"], fcr_cur - fcr_req, label="diferenca FCR")
        assert_close(r["feoDiff"], feo_cur - feo_req, label="diferenca FEO")
        exp_fcr_status = "Regular" if fcr_cur >= fcr_req else "Insuficiente"
        exp_feo_status = "Regular" if feo_cur >= feo_req else "Insuficiente"
        assert r["fcrStatus"] == exp_fcr_status, f"status FCR {capital}"
        assert r["feoStatus"] == exp_feo_status, f"status FEO {monthly}"
        regular = (exp_fcr_status == "Regular") + (exp_feo_status == "Regular")
        exp_general = {2: "Reservas regulares", 1: "Reservas parcialmente insuficientes",
                       0: "Reservas críticas"}[regular]
        exp_tone = {2: "var(--f1)", 1: "var(--f2)", 0: "var(--f4)"}[regular]
        assert r["generalStatus"] == exp_general, f"status geral ({regular} regulares)"
        assert r["generalTone"] == exp_tone, "tom geral preservado"
        assert r["hasDeficit"] == (fcr_cur < fcr_req or feo_cur < feo_req), "flag de deficit"


def open_seeded(browser, url, seed_state_json):
    # Contexto novo com estado pre-semeado ANTES de qualquer script do app rodar.
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.add_init_script(
        "window.__onbShown=true;"
        f"try{{localStorage.setItem('jpwealth_v9_state', {json.dumps(seed_state_json)});}}catch(e){{}}"
    )
    page = context.new_page()
    observed = {"pageerror": []}
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.route(
        "**/api.frankfurter.dev/**",
        lambda route: route.fulfill(
            status=200, content_type="application/json", body='{"rates":{}}'
        ),
    )
    page.goto(url)
    page.wait_for_function("() => window.JPWFx && window.JPWFx.state")
    return context, page, observed


def run_state_cases(browser, url):
    context, page, observed = prepare_page(browser, url)
    ev = page.evaluate

    created = ev(
        """() => {
        const st = window.JPWFx.state;
        const first = st.fxPlanCreate({name:'Plano sintético', assumptions:{
            startMonth:'2026-01', horizonMonths:24, initialBalanceUsd:1000,
            defaultMonthlyReturn:0.01, projectedFxRate:5.40}});
        const dup = st.fxPlanCreate({name:'Segundo', assumptions:{
            startMonth:'2026-01', horizonMonths:12, initialBalanceUsd:1,
            defaultMonthlyReturn:0}});
        const outOfOrder = st.fxPlanRecordActual('2026-03', {inputType:'rate', returnRate:0.01});
        const close = st.fxPlanRecordActual('2026-01', {inputType:'rate', returnRate:0.01});
        const contrib = st.fxPlanAddContribution({month:'2026-01', source:'personal',
            originalCurrency:'BRL', originalAmount:500, acquisitionFxRate:5.00});
        // campos desconhecidos plantados direto no estado persistido
        S.fxPlanning.plan.customField = 'preservar';
        S.fxPlanning.plan.actuals['2026-01'].extensaoFutura = 'preservar-2';
        save();
        return {first: first.ok, dup: dup.errors || [], outOfOrder: outOfOrder.errors || [],
                close: close.ok, contrib: contrib.ok};
    }"""
    )
    assert created["first"], "criação do plano falhou"
    assert created["dup"], "segundo plano deveria ser recusado no MVP"
    assert any("contíguos" in e for e in created["outOfOrder"]), (
        f"fechamento fora de ordem deveria falhar: {created['outOfOrder']}"
    )
    assert created["close"] and created["contrib"], "fechamento/aporte válidos falharam"

    page.reload()
    page.wait_for_function("() => window.JPWFx && window.JPWFx.state")
    after = ev(
        """() => {
        const ov = window.JPWFx.state.fxOverviewLive();
        return {
            balance: ov ? ov.currentBalanceUsd : null,
            lastClosed: ov ? ov.lastClosedMonth : null,
            nextOpen: ov ? ov.nextOpenMonth : null,
            custom: S.fxPlanning.plan.customField,
            extensao: S.fxPlanning.plan.actuals['2026-01'].extensaoFutura,
            auditTypes: S.fxPlanning.auditLog.map(e => e.type),
            dgTouched: (S.dataGovernance.changeLog || []).some(e => e.entity === 'fxPlanning'),
            avgFx: ov ? ov.costBasis.weightedAverageFx : null
        };
    }"""
    )
    # 1000 * 1.01 + (500/5.00) = 1110 — sobrevive ao reload (round-trip localStorage)
    assert_close(after["balance"], 1110, label="round-trip: patrimônio após reload")
    assert after["lastClosed"] == "2026-01" and after["nextOpen"] == "2026-02", "meses após reload"
    assert after["custom"] == "preservar", "campo desconhecido do plano foi perdido"
    assert after["extensao"] == "preservar-2", "campo desconhecido do realizado foi perdido"
    for expected_event in ("FX_PLAN_CREATED", "FX_MONTH_ACTUAL_RECORDED", "FX_CONTRIBUTION_RECORDED"):
        assert expected_event in after["auditTypes"], f"auditoria sem {expected_event}"
    assert after["dgTouched"], "mutações FX devem marcar o changeLog da governança de backup"
    assert_close(after["avgFx"], 5.00, label="custo médio após reload")
    raw_state = ev("() => localStorage.getItem('jpwealth_v9_state')")
    context.close()

    # Base legada SEM o agregado: migrate() introduz DEFAULTS.fxPlanning sem perda.
    legacy = json.loads(raw_state)
    legacy.pop("fxPlanning", None)
    ctx2, page2, obs2 = open_seeded(browser, url, json.dumps(legacy))
    legacy_check = page2.evaluate(
        """() => ({
            hasAggregate: !!S.fxPlanning, plan: S.fxPlanning.plan,
            schema: S.fxPlanning.schemaVersion,
            saldoIni: S.params.saldoIni,
            ledgerLen: (S.ledger || []).length
        })"""
    )
    assert legacy_check["hasAggregate"] and legacy_check["plan"] is None, "base legada não ganhou o agregado"
    assert legacy_check["schema"] == 1, "schemaVersion do agregado legado"
    assert legacy_check["saldoIni"] == legacy["params"]["saldoIni"], "estado legado alterado indevidamente"
    assert not obs2["pageerror"], f"pageerror na base legada: {obs2['pageerror']}"
    ctx2.close()

    # Agregado corrompido (tipo inválido): guarda estrutural restaura a forma sem
    # tocar no resto do estado e sem quebrar o boot.
    corrupted = json.loads(raw_state)
    corrupted["fxPlanning"] = 5
    ctx3, page3, obs3 = open_seeded(browser, url, json.dumps(corrupted))
    corrupt_check = page3.evaluate(
        """() => ({plan: S.fxPlanning.plan, schema: S.fxPlanning.schemaVersion,
                   saldoIni: S.params.saldoIni})"""
    )
    assert corrupt_check["plan"] is None and corrupt_check["schema"] == 1, "guarda estrutural não recuperou o agregado"
    assert corrupt_check["saldoIni"] == corrupted["params"]["saldoIni"], "estado vizinho afetado pela recuperação"
    assert not obs3["pageerror"], f"pageerror com agregado corrompido: {obs3['pageerror']}"
    ctx3.close()


def run_ui_flow(browser, url):
    # Fluxo real de interface na tela Contabilidade: criar plano, fechar mês,
    # registrar aporte, conferir KPIs/gráfico/tabela e contenção em viewport móvel.
    context, page, observed = prepare_page(browser, url)
    page.click('.tab[data-screen="fxplan"]')
    page.wait_for_selector("#fxpCreateBtn")
    # No estado vazio o submenu pode registrar a intenção visual, mas não cria
    # plano nem toca em S.fxPlanning. A criação continua sendo ação exclusiva
    # do formulário e a intenção volta a Visão Geral antes do fluxo principal.
    page.focus("#fxplanNavTrigger")
    page.keyboard.press("ArrowDown")
    page.click('#fxplanNavSubmenu [data-nav-sub-view="table"]')
    empty_nav = page.evaluate(
        "() => ({view: window.JPWFx.ui.getView(), plan: S.fxPlanning.plan, create: !!document.querySelector('#fxpCreateBtn')})"
    )
    assert empty_nav == {"view": "table", "plan": None, "create": True}, empty_nav
    page.evaluate("() => window.JPWFx.ui.selectView('overview')")
    page.fill("#fxpName", "Plano UI")
    page.fill("#fxpStart", "2026-01")
    page.fill("#fxpHorizon", "24")
    page.fill("#fxpInitial", "1000")
    page.fill("#fxpDefaultRate", "1,00")
    page.fill("#fxpProjFx", "5,40")
    page.click("#fxpCreateBtn")
    page.wait_for_selector("#fxpPanel-overview")
    page.wait_for_selector("#fxpMainChart svg")
    summary = page.text_content("#fxpMainChartSummary")
    assert summary and "projeção" in summary.lower(), "resumo textual do gráfico ausente"

    # O acionador continua filho direto de #nav para não quebrar Pill/Kinetic,
    # mas a segunda faixa é irmã estrutural do header, não popover interno.
    nav_contract = page.evaluate(
        """() => ({
          directTrigger: document.querySelector('#nav > #fxplanNavTrigger') !== null,
          directPanel: document.querySelector('#nav > #fxplanNavSubmenu') !== null,
          structuralOrder: document.querySelector('header').nextElementSibling?.id === 'navSubShell'
            && navSubShell.nextElementSibling?.id === 'gdContextRow',
          popupTriggers: [...document.querySelectorAll('#nav > .tab[aria-haspopup]')].map(el => el.id),
          keys: [...document.querySelectorAll('#fxplanNavSubmenu [data-nav-sub-view]')]
            .map(el => el.dataset.navSubView),
          descriptions: [...document.querySelectorAll('#fxplanNavSubmenu .nav-sub-item-desc')]
            .map(el => el.textContent.trim()),
          duplicateInternalNav: document.querySelectorAll('#fxPlanningRoot [data-fxp-view]').length,
          api: !!(window.JPWFx.ui && window.JPWFx.ui.selectView && window.JPWFx.ui.getView)
        })"""
    )
    assert nav_contract["directTrigger"] and not nav_contract["directPanel"], "faixa continuou presa dentro de #nav"
    assert nav_contract["structuralOrder"], f"faixa fora da ordem header → submenu → contexto: {nav_contract}"
    assert nav_contract["popupTriggers"] == [], f"faixa estrutural ainda anuncia popup: {nav_contract}"
    assert nav_contract["keys"] == ["overview", "planning", "actuals", "table"], nav_contract
    assert all(nav_contract["descriptions"]), "descrições contextuais ausentes"
    assert nav_contract["duplicateInternalNav"] == 0, "tabs equivalentes continuam dentro do conteúdo"
    assert nav_contract["api"], "superfície visual JPWFx.ui do submenu ausente"

    # Fechada ocupa zero; aberta cresce no fluxo, desloca contexto e conteúdo e
    # nunca sobrepõe a linha seguinte. A travessia por ponteiro preserva o delay.
    page.keyboard.press("Escape")
    page.wait_for_timeout(340)
    before_open = page.evaluate(
        """() => ({
          shell: navSubShell.getBoundingClientRect(),
          context: gdContextRow.getBoundingClientRect(),
          main: appMain.getBoundingClientRect()
        })"""
    )
    page.hover("#fxplanNavTrigger")
    page.wait_for_function("() => fxplanNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.wait_for_timeout(340)
    after_open = page.evaluate(
        """() => ({
          shell: navSubShell.getBoundingClientRect(),
          context: gdContextRow.getBoundingClientRect(),
          main: appMain.getBoundingClientRect(),
          position: getComputedStyle(navSubShell).position,
          shadow: getComputedStyle(navSubShell).boxShadow,
          tones: {
            header: getComputedStyle(document.querySelector('header')).backgroundColor,
            submenu: getComputedStyle(navSubShell).backgroundColor,
            context: getComputedStyle(gdContextRow).backgroundColor
          }
        })"""
    )
    shift = after_open["shell"]["height"] - before_open["shell"]["height"]
    assert shift > 70, f"faixa não ganhou altura estrutural: {before_open} -> {after_open}"
    assert after_open["context"]["y"] - before_open["context"]["y"] > 70, "contexto não foi deslocado"
    assert after_open["main"]["y"] - before_open["main"]["y"] > 70, "conteúdo não foi deslocado"
    assert after_open["shell"]["y"] + after_open["shell"]["height"] <= after_open["context"]["y"] + 1, (
        f"faixa sobrepõe contexto: {after_open}"
    )
    assert after_open["position"] == "static" and after_open["shadow"] == "none", after_open
    assert len(set(after_open["tones"].values())) == 3, f"faixa não tem terceiro tom próprio: {after_open['tones']}"
    page.hover("#fxplanNavSubmenu")
    page.wait_for_timeout(450)
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "true", "travessia acionador → faixa fechou cedo"
    page.mouse.move(12, 420)
    page.wait_for_timeout(250)
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "true", "delay menor que 300 ms"
    page.wait_for_timeout(220)
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "false", "submenu não fechou após 400 ms"

    # Teclado com roving tabindex, Home/End e retorno de foco por Escape.
    page.focus("#fxplanNavTrigger")
    page.keyboard.press("ArrowDown")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == "overview"
    page.keyboard.press("ArrowDown")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == "planning"
    page.keyboard.press("End")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == "table"
    page.keyboard.press("Home")
    assert page.evaluate("() => document.activeElement.dataset.navSubView") == "overview"
    page.keyboard.press("Escape")
    assert page.evaluate("() => document.activeElement.id") == "fxplanNavTrigger", "Escape não devolveu foco"
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "false"

    # Clique fixa a faixa: pointerleave, resize e novo clique no acionador não
    # fecham. Um item interno também mantém aberto; somente clique externo (ou
    # Escape acessível) encerra o estado fixado.
    page.click("#fxplanNavTrigger")
    pinned_open = page.evaluate(
        "() => ({expanded: fxplanNavTrigger.getAttribute('aria-expanded'), pinned: document.documentElement.dataset.navSubPinned})"
    )
    assert pinned_open == {"expanded": "true", "pinned": "true"}, pinned_open
    page.mouse.move(12, 420)
    page.wait_for_timeout(520)
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "true", "pointerleave fechou faixa fixada"
    page.set_viewport_size({"width": 1390, "height": 900})
    page.wait_for_timeout(80)
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "true", "resize fechou faixa fixada"
    page.click("#fxplanNavTrigger")
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "true", "novo clique alternou faixa fixada"
    page.click('#fxplanNavSubmenu [data-nav-sub-view="planning"]')
    assert page.evaluate("() => document.documentElement.dataset.navSubPinned") == "true"
    page.click("#fxPlanningRoot .fxp-note")
    outside_close = page.evaluate(
        "() => ({expanded: fxplanNavTrigger.getAttribute('aria-expanded'), pinned: document.documentElement.dataset.navSubPinned || null})"
    )
    assert outside_close == {"expanded": "false", "pinned": None}, f"clique externo não fechou: {outside_close}"
    page.set_viewport_size({"width": 1440, "height": 900})

    # Tab sai naturalmente da faixa sem criar focus trap; abertura por seta é
    # transitória e não cria o estado fixado.
    page.focus("#fxplanNavTrigger")
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Tab")
    page.wait_for_timeout(20)
    tab_exit = page.evaluate(
        "() => ({expanded: fxplanNavTrigger.getAttribute('aria-expanded'), pinned: document.documentElement.dataset.navSubPinned || null, inside: fxplanNavSubmenu.contains(document.activeElement)})"
    )
    assert tab_exit == {"expanded": "true", "pinned": None, "inside": False}, f"Tab ficou preso ou fixou a faixa: {tab_exit}"
    page.keyboard.press("Escape")
    assert page.get_attribute("#fxplanNavTrigger", "aria-expanded") == "false"

    # Cada destino usa a mesma chave dos renderizadores existentes, ativa
    # somente #fxplan e mantém uma única fonte visível de navegação.
    for key in ("overview", "planning", "actuals", "table"):
        page.focus("#fxplanNavTrigger")
        page.keyboard.press("ArrowDown")
        page.click(f'#fxplanNavSubmenu [data-nav-sub-view="{key}"]')
        selected = page.evaluate(
            """key => ({
              view: window.JPWFx.ui.getView(),
              screens: [...document.querySelectorAll('.screen.active')].map(el => el.id),
              current: document.querySelector(`#fxplanNavSubmenu [data-nav-sub-view="${key}"]`)?.getAttribute('aria-current'),
              duplicateInternalNav: document.querySelectorAll('#fxPlanningRoot [data-fxp-view]').length,
              expanded: fxplanNavTrigger.getAttribute('aria-expanded')
            })""",
            key,
        )
        assert selected == {
            "view": key,
            "screens": ["fxplan"],
            "current": "page",
            "duplicateInternalNav": 0,
            "expanded": "true",
        }, selected

    page.click('#fxplanNavSubmenu [data-nav-sub-view="actuals"]')
    page.wait_for_selector("#fxpActBtn")
    page.fill("#fxpActValue", "-0,70")
    page.click("#fxpActBtn")
    page.wait_for_selector('#fxpActMonth option[value="2026-02"]', state="attached")
    page.fill("#fxpCMonth", "2026-01")
    page.fill("#fxpCAmount", "540")
    page.fill("#fxpCRate", "5,40")
    page.click("#fxpCBtn")
    page.wait_for_selector('button[data-fxp-del]')

    page.evaluate("() => window.scrollTo(0, 0)")
    page.hover("#fxplanNavTrigger")
    page.wait_for_function("() => fxplanNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.click('#fxplanNavSubmenu [data-nav-sub-view="overview"]')
    page.wait_for_selector("#fxpMainChart svg")
    body_text = page.text_content("#fxPlanningRoot")
    # 1000 × (1 − 0,007) + 540/5,40 = 993 + 100 = 1.093,00
    assert "1.093,00" in body_text, "patrimônio do plano não reflete fechamento + aporte"
    assert "R$ 5,4000" in body_text, "câmbio médio de aquisição ausente na visão geral"

    page.evaluate("() => window.scrollTo(0, 0)")
    page.hover("#fxplanNavTrigger")
    page.wait_for_function("() => fxplanNavTrigger.getAttribute('aria-expanded') === 'true'")
    page.click('#fxplanNavSubmenu [data-nav-sub-view="table"]')
    page.wait_for_selector(".fxp-tablewrap .fxp-badge-real")
    table_text = page.text_content("#fxPlanningRoot")
    assert "BASELINE" in table_text and "VIGENTE" in table_text, "tabela sem separação baseline/vigente"

    # Navegação principal: as cinco telas alternam estados ativos exclusivos.
    nav_state = page.evaluate(
        """() => {
        const out=[];
        document.querySelectorAll('#nav .tab[data-screen]').forEach(t=>{
            t.click();
            out.push({screen:t.dataset.screen,
                      active:[...document.querySelectorAll('.screen.active')].map(s=>s.id),
                      tabActive:t.classList.contains('active')});
        });
        return out;
    }"""
    )
    assert [r["screen"] for r in nav_state] == ["dash", "exec", "contas", "contab", "fxplan"], (
        f"rail deveria ter as cinco telas na ordem: {nav_state}"
    )
    for row in nav_state:
        assert row["active"] == [row["screen"]], f"telas ativas divergentes: {row}"
        assert row["tabActive"], f"tab sem estado ativo: {row}"
    # Contabilidade sem restos da feature.
    assert page.evaluate(
        "() => document.querySelector('#contab #fxPlanningCard, #contab [id^=fxp], #contab .fxp-section') === null"
    ), "restos do Planejamento FX dentro de #contab"
    # Ativação hierárquica por teclado: Enter abre o submenu e Enter no item
    # seleciona o destino, preservando a navegação integral sem mouse.
    page.click('.tab[data-screen="dash"]')
    page.focus('.tab[data-screen="fxplan"]')
    page.keyboard.press("Enter")
    assert page.evaluate(
        "() => document.activeElement.dataset.navSubView === window.JPWFx.ui.getView() && document.documentElement.dataset.navSubPinned === 'true'"
    ), "Enter não focou o modo visual vigente"
    page.keyboard.press("Enter")
    page.wait_for_selector("#fxplan.active", state="attached")
    # Refresh estando em Planejamento FX: comportamento canônico atual (sem rota
    # persistida, o boot volta ao Dashboard) e o plano segue renderizado ao voltar.
    page.reload()
    page.wait_for_function("() => window.JPWFx && window.JPWFx.state")
    active_after = page.evaluate("() => [...document.querySelectorAll('.screen.active')].map(s=>s.id)")
    assert active_after == ["dash"], f"refresh deveria voltar ao Dashboard (rota não persistida): {active_after}"
    page.click('.tab[data-screen="fxplan"]')
    page.wait_for_selector(".fxp-section")

    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(250)
    page.click("[data-shell-menu-toggle]")
    page.click("#fxplanNavTrigger")
    page.wait_for_timeout(340)
    mobile_menu = page.evaluate(
        """() => ({
          shell: document.documentElement.dataset.shellMenu,
          fx: fxplanNavTrigger.getAttribute('aria-expanded'),
          shellHeight: navSubShell.getBoundingClientRect().height,
          contextY: gdContextRow.getBoundingClientRect().y,
          submenuBottom: navSubShell.getBoundingClientRect().bottom,
          position: getComputedStyle(navSubShell).position
        })"""
    )
    assert mobile_menu["shell"] is None and mobile_menu["fx"] == "true", mobile_menu
    assert mobile_menu["position"] == "static" and mobile_menu["shellHeight"] > 200, mobile_menu
    assert mobile_menu["submenuBottom"] <= mobile_menu["contextY"] + 1, f"submenu mobile sobreposto: {mobile_menu}"
    page.click('#fxplanNavSubmenu [data-nav-sub-view="actuals"]')
    mobile_selected = page.evaluate(
        """() => ({
          shell: document.documentElement.dataset.shellMenu || null,
          fx: fxplanNavTrigger.getAttribute('aria-expanded'),
          pinned: document.documentElement.dataset.navSubPinned,
          view: window.JPWFx.ui.getView(),
          active: [...document.querySelectorAll('.screen.active')].map(el => el.id)
        })"""
    )
    assert mobile_selected == {
        "shell": None, "fx": "true", "pinned": "true", "view": "actuals", "active": ["fxplan"]
    }, mobile_selected
    # Segundo toque no acionador mantém o estado fixado; tocar fora encerra.
    page.click("[data-shell-menu-toggle]")
    page.click("#fxplanNavTrigger")
    mobile_toggle = page.evaluate(
        "() => ({shell: document.documentElement.dataset.shellMenu || null, fx: fxplanNavTrigger.getAttribute('aria-expanded'), pinned: document.documentElement.dataset.navSubPinned})"
    )
    assert mobile_toggle == {"shell": None, "fx": "true", "pinned": "true"}, mobile_toggle
    page.click("#fxPlanningRoot .fxp-note")
    assert page.evaluate(
        "() => ({fx: fxplanNavTrigger.getAttribute('aria-expanded'), pinned: document.documentElement.dataset.navSubPinned || null})"
    ) == {"fx": "false", "pinned": None}, "toque externo não fechou faixa mobile"
    scroll = page.evaluate(
        "() => ({doc: document.documentElement.scrollWidth, win: window.innerWidth})"
    )
    assert scroll["doc"] <= scroll["win"] + 2, (
        f"scroll horizontal da página em viewport móvel: {scroll}"
    )
    assert not observed["pageerror"], f"pageerror no fluxo de UI: {observed['pageerror']}"
    context.close()


def run_onboarding_smoke(browser, url):
    # A delegacao de reserveCalc() nao pode quebrar a abertura automatica do
    # questionario de inicio (boot -> setTimeout -> openOnboardingModal).
    context, page, observed = prepare_page(browser, url, suppress_onboarding=False)
    page.wait_for_selector("#modalOverlay.show", state="attached", timeout=15000)
    page.wait_for_timeout(700)
    errors = [e for e in observed["pageerror"]]
    assert not errors, f"pageerror ao abrir onboarding: {errors}"
    context.close()


def main():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            run_engine_cases(page)
            run_reserve_cases(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()
            run_state_cases(browser, url)
            run_ui_flow(browser, url)
            run_onboarding_smoke(browser, url)
            browser.close()
    finally:
        server.shutdown()
    print("FX PLANNING TEST PASS")


if __name__ == "__main__":
    main()
