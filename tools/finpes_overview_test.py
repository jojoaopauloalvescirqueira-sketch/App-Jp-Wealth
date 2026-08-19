#!/usr/bin/env python3
"""Visao Geral (PF-06) — suite focal N3 procedimental.

READ -> CONSUME CANONICAL DERIVATIONS -> PRESENT. Zero segunda verdade:
os numeros exibidos DEVEM vir de pfCompMetrics/pfCreditKPIs/pfCompCompare/
pfPendingBefore; abrir/renderizar jamais salva, materializa ou muta o
agregado. Mes virtual declara-se nao registrado — nenhum realizado R$ 0
fabricado (armadilha da completude vacua provada no Discovery).
Fixtures sinteticas com valores DESACOPLADOS (projetado != recebido,
previsto != executado) — soma errada nao passa por coincidencia.
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


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://{'127.0.0.1'}:{port}/index.html"


def boot(browser, url, mutacao_js=None):
    context = browser.new_context(viewport={"width": 1440, "height": 950})
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
        "() => typeof S === 'object' && typeof pfCompMetrics === 'function'"
        " && typeof finpesOverviewRender === 'function'")
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => typeof S === 'object' && typeof finpesOverviewRender === 'function'")
    page.wait_for_timeout(350)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); navigateToScreen('finpes'); }")
    return context, page, erros


def executar(nome, fn, falhas):
    try:
        fn()
    except Exception as e:
        falhas.append(f"{nome}: EXCECAO no harness: {str(e).splitlines()[-1][:160]}")


def checar(r, erros, falhas, rotulo):
    for chave, valor in r.items():
        if valor is not True:
            falhas.append(f"{rotulo}: {chave} falhou: {json.dumps(r, ensure_ascii=False)[:600]}")
            break
    if erros:
        falhas.append(f"{rotulo}: pageerror: {erros[:2]}")


# ---------------------------------------------------------------- BLOCO A ----

def run_a_mes_virtual_zero_escrita(browser, url, falhas):
    """Mes corrente virtual: declara nao registrado, zero R$ no card do mes,
    zero save, zero materializacao, agregado byte a byte igual."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const foto = JSON.stringify(S.personalFinance);
        const mesesAntes = Object.keys(S.personalFinance.months).length;
        let saves = 0; const origSave = window.save;
        window.save = function(){ saves++; return origSave.apply(this, arguments); };
        finpesOverviewRender();
        window.save = origSave;
        const root = document.getElementById('finpesOverviewRoot');
        const cardMes = root.querySelector('.fo-card');
        const t = cardMes.innerText;
        return {
          declaraNaoRegistrado: t.includes('Mês ainda não registrado'),
          zeroRSNoCardDoMes: !t.includes('R$'),
          semSobraFabricada: !t.includes('Sobra'),
          zeroSave: saves===0,
          zeroMaterializacao: Object.keys(S.personalFinance.months).length===mesesAntes,
          agregadoIntacto: JSON.stringify(S.personalFinance)===foto,
        };
    }""")
    checar(r, erros, falhas, "A virtual/zero-escrita")
    ctx.close()


def run_a_mes_parcial_e_completo(browser, url, falhas):
    """Cobertura parcial mostra known como PARCIAL sem virar total; sobra
    parcial sem valor financeiro; completo espelha exatamente os helpers.
    Valores desacoplados: projetado 10.000 != recebido 7.000; previsto
    4.000 != executado 3.000."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey();
        pfActAddIncome(M, {name:'Salario', projectedAmount:1000000});
        pfActAddIncome(M, {name:'Freela', projectedAmount:200000});
        pfActAddExpense(M, {name:'Moradia'});
        pfActAddExpense(M, {name:'Mercado'});
        const mes = S.personalFinance.months[M];
        const sal = mes.incomes.find(i=>i.name==='Salario');
        const mor = mes.expenses.find(e=>e.name==='Moradia');
        const mer = mes.expenses.find(e=>e.name==='Mercado');
        pfActUpdateIncomeField(M, sal.id, 'receivedAmount', 700000);
        pfActUpdateExpenseField(M, mor.id, 'expectedAmount', 400000);
        pfActUpdateExpenseField(M, mor.id, 'executedCash', 300000);
        pfActUpdateExpenseField(M, mor.id, 'executedCard', 0);
        // fase parcial: receita 1/2, despesa 1/2
        finpesOverviewRender();
        const root = document.getElementById('finpesOverviewRoot');
        let t = root.querySelector('.fo-card').innerText;
        const linhaSobra = [...root.querySelectorAll('.fo-row')]
          .find(x=>x.innerText.includes('Sobra realizada')).innerText;
        const parcial = {
          receitaKnownParcial: t.includes('R$ 7.000,00 conhecidos') && t.includes('PARCIAL 1/2'),
          despesaKnownParcial: t.includes('R$ 3.000,00 conhecidos'),
          sobraSemValor: linhaSobra.includes('Dados incompletos') && !linhaSobra.includes('R$'),
          comprometimentoNA: t.includes('N/A — cobertura incompleta'),
          semDestinacoes: !t.includes('Destinado'),
        };
        // fase completa + destinacao
        const fre = mes.incomes.find(i=>i.name==='Freela');
        pfActUpdateIncomeField(M, fre.id, 'receivedAmount', 150000);
        pfActUpdateExpenseField(M, mer.id, 'executedCash', 50000);
        pfActUpdateExpenseField(M, mer.id, 'executedCard', 0);
        // contrato real do ato: label (nao name) — e a asserçao exige valor
        // NAO ZERO, senao o teste passa vacuamente com o ato recusado
        const aloc = pfActAddAllocation(M, {label:'Reserva', amount:100000});
        finpesOverviewRender();
        t = root.querySelector('.fo-card').innerText;
        const met = pfCompMetrics(M);
        const m2 = S.personalFinance.months[M];
        const completo = {
          alocacaoAceita: aloc.ok===true && pfTotalAllocated(m2)===100000,
          receitaIgualHelper: t.includes(formatBRLCents(met.receita.value)),
          despesaIgualHelper: t.includes(formatBRLCents(met.despesa.value)),
          sobraIgualHelper: t.includes(formatBRLCents(met.sobra.value)),
          comprometimentoPct: t.includes((met.comprometimento.value*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%'),
          destinadoNaoZero: t.includes('Destinado') && t.includes('R$ 1.000,00'),
          naoAlocadaExata: pfUnallocatedSurplus(m2)===met.sobra.value-100000
            && t.includes(formatBRLCents(met.sobra.value-100000)),
        };
        return Object.assign({}, parcial, completo);
    }""")
    checar(r, erros, falhas, "A parcial/completo")
    ctx.close()


def run_a_divida_sem_carry_forward(browser, url, falhas):
    """Sem dividas: zero demonstrado. Divida com snapshot so no mes anterior:
    competencia atual fica PARCIAL 0/1 e o balance anterior NAO aparece
    (nenhum carry-forward). Snapshot atual: COMPLETE."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey();
        const root = document.getElementById('finpesOverviewRoot');
        // precisa de mes materializado para a divida nao ficar UNAVAILABLE
        pfActAddIncome(M, {name:'Base', projectedAmount:100});
        finpesOverviewRender();
        let t = root.innerText;
        const semDividas = t.includes('Sem dívidas vigentes') && t.includes('zero demonstrado');
        // divida vigente com observacao APENAS em M-1 (valor isca 987.654,00).
        // Sondas ESCOPADAS a linha da divida — a raiz inteira tambem contem o
        // badge PARCIAL do card do mes, que mascararia a moldura de cobertura
        // (a mutacao MD2 sobreviveu exatamente assim).
        const linhaDivida = () => [...root.querySelectorAll('.fo-row')]
          .find(x=>x.innerText.includes('Dívida observada')).innerText;
        pfActAddDebt({creditor:'Banco X', type:'EMPRESTIMO', startMonth:pfMonthAdd(M,-3)});
        const debt = S.personalFinance.debts[0];
        pfActRecordDebtSnapshot(pfMonthAdd(M,-1), debt.id, {balance:98765400});
        finpesOverviewRender();
        const ld = linhaDivida();
        const parcialSemCarry = ld.includes('PARCIAL 0/1')
          && ld.includes('observados') && !ld.includes('todas observadas')
          && !root.innerText.includes('98.765.400') && !root.innerText.includes('R$ 987.654,00');
        // observacao da competencia atual
        pfActRecordDebtSnapshot(M, debt.id, {balance:1234500});
        finpesOverviewRender();
        const ld2 = linhaDivida();
        const completa = ld2.includes('R$ 12.345,00') && ld2.includes('todas observadas')
          && !ld2.includes('PARCIAL');
        return { semDividas, parcialSemCarry, completa };
    }""")
    checar(r, erros, falhas, "A divida/carry-forward")
    ctx.close()


def run_a_credito_vigente(browser, url, falhas):
    """Credito e posicao ATUAL: cobertura parcial explicita; used>limit da
    livre negativo e utilizacao >100% sem clamp; rotulo de estado vigente."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey();
        pfActAddIncome(M, {name:'Base', projectedAmount:100});
        const root = document.getElementById('finpesOverviewRoot');
        finpesOverviewRender();
        const semLinhas = root.innerText.includes('Nenhuma linha de crédito cadastrada');
        pfActAddCreditLine({institution:'Banco A', instrument:'Cartao A', totalLimit:1000000, used:450000});
        pfActAddCreditLine({institution:'Banco B', instrument:'Cartao B', used:200000});
        finpesOverviewRender();
        let t = root.innerText;
        const parcialExplicito = t.includes('POSIÇÃO ATUAL')
          && t.includes('estado vigente — não é dado do mês')
          && t.includes('PARCIAL 1/2')
          && t.includes('— cobertura incompleta');
        const lb = S.personalFinance.creditLines.find(l=>l.institution==='Banco B');
        pfActUpdateCreditLineField(lb.id, 'totalLimit', 100000);
        const la = S.personalFinance.creditLines.find(l=>l.institution==='Banco A');
        pfActUpdateCreditLineField(la.id, 'used', 1150000);
        finpesOverviewRender();
        t = root.innerText;
        const k = pfCreditKPIs();
        const estouroSemClamp = k.totalFree<0
          && t.includes(formatBRLCents(k.totalFree))
          && t.includes((k.utilizationConsolidated*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%')
          && k.utilizationConsolidated>1;
        return { semLinhas, parcialExplicito, estouroSemClamp };
    }""")
    checar(r, erros, falhas, "A credito vigente")
    ctx.close()


# ---------------------------------------------------------------- BLOCO B ----

def run_b_comparativo(browser, url, falhas):
    """Comparacao consome pfCompCompare: baseline parcial -> indisponivel com
    motivo; ambos completos -> numeros identicos ao helper; sobra sem %;
    comprometimento em p.p. com escala aplicada UMA vez."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey(), P = pfMonthAdd(M,-1);
        const root = document.getElementById('finpesOverviewRoot');
        const seed = (mk, recebida, executada) => {
          pfActAddIncome(mk, {name:'Renda', projectedAmount:999900});
          const mes = S.personalFinance.months[mk];
          const inc = mes.incomes.find(i=>i.name==='Renda');
          pfActUpdateIncomeField(mk, inc.id, 'receivedAmount', recebida);
          pfActAddExpense(mk, {name:'Gasto'});
          const e = mes.expenses.find(x=>x.name==='Gasto');
          pfActUpdateExpenseField(mk, e.id, 'expectedAmount', 555500);
          if(executada!==null){
            pfActUpdateExpenseField(mk, e.id, 'executedCash', executada);
            pfActUpdateExpenseField(mk, e.id, 'executedCard', 0);
          }
        };
        seed(M, 800000, 500000);         // atual completo
        seed(P, 1000000, null);          // anterior: despesa sem executado -> PARTIAL
        finpesOverviewRender();
        const cardComp = () => [...root.querySelectorAll('.fo-card')]
          .find(c=>c.innerText.includes('Vs mês anterior'));
        let t = cardComp().innerText;
        const baselineParcialIndisponivel = t.includes('comparação indisponível')
          && t.includes('parcial');
        // completa o baseline
        const mesP = S.personalFinance.months[P];
        const eP = mesP.expenses.find(x=>x.name==='Gasto');
        pfActUpdateExpenseField(P, eP.id, 'executedCash', 400000);
        pfActUpdateExpenseField(P, eP.id, 'executedCard', 0);
        finpesOverviewRender();
        t = cardComp().innerText;
        const comp = pfCompCompare(M, pfCompBaselines(M).previousMonth);
        const mr = comp.metrics.receita, ms = comp.metrics.sobra, mc = comp.metrics.comprometimento;
        const receitaIgualHelper = t.includes(formatBRLCents(mr.current))
          && t.includes(formatBRLCents(mr.baseline))
          && t.includes(((mr.relativeChange>=0?'+':'')+(mr.relativeChange*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%'));
        const linhaSobra = [...cardComp().querySelectorAll('.fo-row')]
          .find(x=>x.innerText.startsWith('Sobra')).innerText;
        const sobraSemPercentual = linhaSobra.includes(formatBRLCents(ms.current))
          && !linhaSobra.includes('%');
        const ppEsperado = (mc.deltaPP>=0?'+':'')+(mc.deltaPP*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+' p.p.';
        const linhaCompr = [...cardComp().querySelectorAll('.fo-row')]
          .find(x=>x.innerText.startsWith('Comprometimento')).innerText;
        const deltaPPUmaVez = linhaCompr.includes(ppEsperado);
        return { baselineParcialIndisponivel, receitaIgualHelper, sobraSemPercentual, deltaPPUmaVez };
    }""")
    checar(r, erros, falhas, "B comparativo")
    ctx.close()


def run_b_pendencias_e_escopo(browser, url, falhas):
    """Pendencias: somente meses ANTERIORES materializados com status
    PENDENTE; pendencia do mes corrente nao vaza. GUARDA DE ESCOPO: a Visao
    Geral tem exatamente 4 cards e jamais menciona Patrimonio/Inventario —
    esse dominio saiu de Financas Pessoais e vira roadmap proprio INV-*."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey(), A = pfMonthAdd(M,-2);
        const root = document.getElementById('finpesOverviewRoot');
        finpesOverviewRender();
        const cardPend = () => [...root.querySelectorAll('.fo-card')]
          .find(c=>c.innerText.includes('Pendências'));
        const vazio = cardPend().innerText.includes('Nenhuma pendência anterior');
        // pendencias em A (2 despesas + 1 nota) e no MES CORRENTE (nao deve vazar)
        pfActAddExpense(A, {name:'Luz atrasada'});
        pfActAddExpense(A, {name:'Agua atrasada'});
        pfActAddNote(A, 'conferir fatura');
        pfActAddExpense(M, {name:'Pendente do corrente'});
        finpesOverviewRender();
        const t = cardPend().innerText;
        const listaAnterior = t.includes(pfMonthLabel(A))
          && t.includes('2 despesas pendentes') && t.includes('1 nota pendente');
        const correnteNaoVaza = !t.includes(pfMonthLabel(M));
        // guarda de escopo: nem card, nem placeholder, nem palavra
        const raiz = root.innerText;
        const quatroCards = root.querySelectorAll('.fo-card').length===4;
        const semPatrimonioInventario =
          !/patrim[oô]nio/i.test(raiz) && !/invent[aá]rio/i.test(raiz)
          && !/PF-0[78]/.test(raiz);
        const semFuncaoPatrimonio = typeof window.foPatrimonioCardHTML === 'undefined';
        return { vazio, listaAnterior, correnteNaoVaza,
                 quatroCards, semPatrimonioInventario, semFuncaoPatrimonio };
    }""")
    checar(r, erros, falhas, "B pendencias/escopo")
    ctx.close()


# ---------------------------------------------------------------- BLOCO C ----

def run_c_integracao_zero_escrita(browser, url, falhas):
    """Navegar ate a Visao Geral pelo caminho real renderiza via
    FINPES_VIEW_RENDERERS e nao escreve: zero save, zero materializacao,
    agregado byte a byte igual, com estado rico semeado. Edicao retroativa
    reflete no proximo render (zero cache)."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey();
        pfActAddIncome(M, {name:'Renda', projectedAmount:1000000});
        const inc = S.personalFinance.months[M].incomes.find(i=>i.name==='Renda');
        pfActUpdateIncomeField(M, inc.id, 'receivedAmount', 700000);
        pfActAddCreditLine({institution:'Banco', totalLimit:500000, used:100000});
        const foto = JSON.stringify(S.personalFinance);
        const chavesAntes = Object.keys(S.personalFinance.months).join(',');
        let saves = 0; const origSave = window.save;
        window.save = function(){ saves++; return origSave.apply(this, arguments); };
        window.JPWFin.ui.selectView('overview');      // caminho real do modulo
        window.save = origSave;
        const root = document.getElementById('finpesOverviewRoot');
        const renderizou = root.querySelectorAll('.fo-card').length === 4
          && root.innerText.includes('R$ 7.000,00');
        const zeroSave = saves===0;
        const zeroMaterializacao = Object.keys(S.personalFinance.months).join(',')===chavesAntes;
        const agregadoIntacto = JSON.stringify(S.personalFinance)===foto;
        // retroativo: mudou no dominio -> proximo render reflete (sem cache)
        pfActUpdateIncomeField(M, inc.id, 'receivedAmount', 999000);
        window.JPWFin.ui.selectView('overview');
        const retroativoReflete = root.innerText.includes('R$ 9.990,00')
          && !root.innerText.includes('R$ 7.000,00');
        // schema v1 puro: render jamais acrescenta chave ao agregado — pega
        // cache persistido mesmo quando idempotente (o boot ja renderizou a
        // view default antes da fotografia, entao byte-igual nao basta).
        const schemaV1Puro = Object.keys(S.personalFinance).sort().join(',')
          === 'creditLines,debts,moneyUnit,months,recurringIncome,scenarios,schemaVersion';
        return { renderizou, zeroSave, zeroMaterializacao, agregadoIntacto, retroativoReflete, schemaV1Puro };
    }""")
    checar(r, erros, falhas, "C integracao/zero-escrita")
    ctx.close()


def run_c_sentinela_leitura(browser, url, falhas):
    """Recusa integral sob unidade desconhecida: zero R$ na raiz, texto de
    indisponibilidade, banner do modulo visivel, agregado intacto; round-trip
    restaura exatamente."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey();
        pfActAddIncome(M, {name:'Renda', projectedAmount:1000000});
        const inc = S.personalFinance.months[M].incomes.find(i=>i.name==='Renda');
        pfActUpdateIncomeField(M, inc.id, 'receivedAmount', 700000);
        window.JPWFin.ui.selectView('overview');
        const root = document.getElementById('finpesOverviewRoot');
        const antesTexto = root.innerText;
        const foto = JSON.stringify(S.personalFinance);
        S.personalFinance.moneyUnit = 'XX_UNIT';
        window.JPWFin.ui.selectView('overview');
        const t = root.innerText;
        const zeroRS = !t.includes('R$');
        const indisponivel = t.includes('Unidade monetária do agregado não reconhecida')
          && t.includes('consolidados financeiros indisponíveis');
        const banner = !document.getElementById('finpesUnitNotice').hidden;
        S.personalFinance.moneyUnit = 'BRL_CENTS';
        const agregadoIntacto = JSON.stringify(S.personalFinance)===foto;
        window.JPWFin.ui.selectView('overview');
        const roundTrip = root.innerText===antesTexto;
        const bannerSumiu = document.getElementById('finpesUnitNotice').hidden;
        return { zeroRS, indisponivel, banner, agregadoIntacto, roundTrip, bannerSumiu };
    }""")
    checar(r, erros, falhas, "C sentinela leitura")
    ctx.close()


# ---------------------------------------------------------------- BLOCO D ----

def run_d_responsivo_e_regressao(browser, url, falhas):
    """Desktop: cards lado a lado sem overflow horizontal; estreito: cards
    empilhados cabendo na viewport. Navegar pelos demais workspaces do modulo
    nao escreve e continua renderizando."""
    ctx, page, erros = boot(browser, url)
    page.evaluate("""() => {
        const M = pfCurrentMonthKey();
        pfActAddIncome(M, {name:'Renda', projectedAmount:1000000});
        pfActAddCreditLine({institution:'Banco', totalLimit:500000, used:100000});
        window.JPWFin.ui.selectView('overview');
    }""")
    desk = page.evaluate("""() => {
        const root = document.getElementById('finpesOverviewRoot');
        const cards = [...root.querySelectorAll('.fo-card')];
        const tops = new Set(cards.map(c=>Math.round(c.getBoundingClientRect().top)));
        return { ladoALado: tops.size < cards.length,
                 overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                 totalCards: cards.length };
    }""")
    page.set_viewport_size({"width": 400, "height": 900})
    page.evaluate("() => window.JPWFin.ui.selectView('overview')")
    estreito = page.evaluate("""() => {
        const root = document.getElementById('finpesOverviewRoot');
        const cards = [...root.querySelectorAll('.fo-card')];
        const tops = cards.map(c=>Math.round(c.getBoundingClientRect().top));
        return { empilhados: new Set(tops).size===cards.length,
                 overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                 cabem: cards.every(c=>c.getBoundingClientRect().width <= document.documentElement.clientWidth) };
    }""")
    page.set_viewport_size({"width": 1440, "height": 950})
    reg = page.evaluate("""() => {
        const foto = JSON.stringify(S.personalFinance);
        for(const v of ['mensal','dividas','comparativo','cenarios','overview'])
            window.JPWFin.ui.selectView(v);
        return { navegacaoNaoEscreve: JSON.stringify(S.personalFinance)===foto,
                 overviewRenderizado: document.getElementById('finpesOverviewRoot').children.length>0 };
    }""")
    r = { "desk_ladoALado": desk["ladoALado"], "desk_semOverflow": desk["overflowX"]==0,
          "quatroCards": desk["totalCards"]==4,
          "estreito_empilhados": estreito["empilhados"], "estreito_semOverflow": estreito["overflowX"]==0,
          "estreito_cabem": estreito["cabem"],
          "regressao_navegacaoNaoEscreve": reg["navegacaoNaoEscreve"],
          "regressao_overviewRenderizado": reg["overviewRenderizado"] }
    checar(r, erros, falhas, "D responsivo/regressao")
    ctx.close()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            executar("A virtual/zero-escrita", lambda: run_a_mes_virtual_zero_escrita(browser, url, falhas), falhas)
            executar("A parcial/completo", lambda: run_a_mes_parcial_e_completo(browser, url, falhas), falhas)
            executar("A divida", lambda: run_a_divida_sem_carry_forward(browser, url, falhas), falhas)
            executar("A credito", lambda: run_a_credito_vigente(browser, url, falhas), falhas)
            executar("B comparativo", lambda: run_b_comparativo(browser, url, falhas), falhas)
            executar("B pendencias/escopo", lambda: run_b_pendencias_e_escopo(browser, url, falhas), falhas)
            executar("C integracao", lambda: run_c_integracao_zero_escrita(browser, url, falhas), falhas)
            executar("C sentinela", lambda: run_c_sentinela_leitura(browser, url, falhas), falhas)
            executar("D responsivo", lambda: run_d_responsivo_e_regressao(browser, url, falhas), falhas)
            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES OVERVIEW TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
