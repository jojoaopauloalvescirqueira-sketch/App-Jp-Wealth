#!/usr/bin/env python3
"""Orcamento Mensal (PF-02) — suite focal N3.

Cresce bloco a bloco (A..F). Cada caso acusa pela PROPRIEDADE violada.
Fixtures 100% sinteticas. Um numero certo pelo motivo errado e FALHA.
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
    return server, f"http://127.0.0.1:{port}/index.html"


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
        "() => typeof S === 'object' && window.JPWFinBudget && typeof pfMutate === 'function'")
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => typeof S === 'object' && window.JPWFinBudget && typeof pfMutate === 'function'")
    page.wait_for_timeout(350)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); navigateToScreen('finpes'); window.JPWFin.ui.selectView('mensal'); }")
    return context, page, erros


# ---------- BLOCO A ----------

def run_a_navegar_nao_escreve(page, falhas):
    """Mes virtual -> somente navegar -> NENHUM save, NENHUMA materializacao."""
    r = page.evaluate("""() => {
        const antes = JSON.stringify(S.personalFinance);
        let saves = 0;
        const orig = window.save;
        window.save = function(){ saves++; return orig.apply(this, arguments); };
        // navega 6 meses para tras e para frente + Hoje, pelos CONTROLES reais
        for(let i=0;i<6;i++) document.querySelector('[data-fb-nav="-1"]').click();
        for(let i=0;i<6;i++) document.querySelector('[data-fb-nav="1"]').click();
        document.querySelector('[data-fb-today]').click();
        window.save = orig;
        return { igual: antes === JSON.stringify(S.personalFinance), saves,
                 meses: Object.keys(S.personalFinance.months).length };
    }""")
    if not r["igual"]:
        falhas.append("A: navegar ALTEROU personalFinance")
    if r["saves"] != 0:
        falhas.append(f"A: navegar disparou save() {r['saves']}x")
    if r["meses"] != 0:
        falhas.append(f"A: navegar MATERIALIZOU {r['meses']} mes(es) — abrir nao e editar")


def run_a_chave_e_rotulo(page, falhas):
    r = page.evaluate("""() => ({
        atual: (typeof pfCurrentMonthKey==='function') ? pfCurrentMonthKey() : null,
        addamos: pfMonthAdd('2026-01',-1), viramos: pfMonthAdd('2026-12',1),
        rotulo: pfMonthLabel('2026-08'),
        rotuloVisivel: document.querySelector('.fb-month-label') && document.querySelector('.fb-month-label').textContent })""")
    if not r["atual"] or len(r["atual"]) != 7:
        falhas.append(f"A: chave do mes corrente invalida: {r['atual']}")
    if r["addamos"] != "2025-12" or r["viramos"] != "2027-01":
        falhas.append(f"A: aritmetica de mes errada na virada de ano: {r['addamos']} / {r['viramos']}")
    if r["rotulo"] != "AGOSTO 2026":
        falhas.append(f"A: rotulo localizado errado: {r['rotulo']}")
    if not r["rotuloVisivel"]:
        falhas.append("A: cabecalho sem rotulo do mes")


def run_a_selo_virtual(page, falhas):
    r = page.evaluate("""() => {
        document.querySelector('[data-fb-today]').click();
        const badge = document.querySelector('.fb-virtual-badge');
        return { temSelo: !!badge, texto: badge ? badge.textContent : '' };
    }""")
    if not r["temSelo"] or "PROJEÇÃO" not in r["texto"] or "não registrado" not in r["texto"]:
        falhas.append(f"A: mes virtual sem o selo 'PROJEÇÃO — mês não registrado': {r['texto']}")


def run_a_write_gate(browser, url, falhas):
    """pfMutate: unico canal de escrita. BRL_CENTS grava; unidade desconhecida
    bloqueia SEM tocar no agregado."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const r1 = pfMutate('teste_gate', pf => { pf.scenarios.push({id:pfId('pfs'), name:'gate-ok'}); return {recordId:'t1'}; });
        const gravou = JSON.parse(localStorage.getItem('jpwealth_v9_state')).personalFinance.scenarios.length;
        return { ok: r1.ok, persistido: r1.persistido, gravou };
    }""")
    if not (r["ok"] and r["persistido"] and r["gravou"] == 1):
        falhas.append(f"A: write gate nao gravou sob BRL_CENTS: {r}")
    ctx.close()

    mut = """
      S.personalFinance = { schemaVersion:1, moneyUnit:'XX_UNIT', months:{},
        recurringIncome:[], debts:[], creditLines:[], scenarios:[] };
    """
    ctx, page, erros = boot(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => {
        const antes = JSON.stringify(S.personalFinance);
        const r1 = pfMutate('teste_gate', pf => { pf.scenarios.push({id:'x'}); return {}; });
        return { ok: r1.ok, erro: r1.erro, intacto: antes === JSON.stringify(S.personalFinance) };
    }""")
    if r["ok"] is not False or r["erro"] != "READ_ONLY_UNSUPPORTED_MONEY_UNIT":
        falhas.append(f"A: gate deveria recusar unidade desconhecida: {r}")
    if not r["intacto"]:
        falhas.append("A: gate bloqueou mas o agregado foi MUTADO — a recusa tem que vir antes de fn")
    ctx.close()


def run_a_materializacao_por_ato(page, falhas):
    """Materializar SO via ato (pfMutate + pfMaterializeMonth): estampa regras
    vigentes com ruleId e grava createdAt do ato."""
    r = page.evaluate("""() => {
        // regra vigente sintetica
        pfMutate('regra_teste', pf => {
            pf.recurringIncome.push({id:'pfr_t1', name:'Salario Sintetico', amount:1200000,
                periodicity:'MENSAL', startMonth:'2026-01', endMonth:null, active:true});
            return {};
        });
        const alvo = '2026-08';
        const virtAntes = pfVirtualIncomes(alvo).length;
        const r1 = pfMutate('materializa_teste', pf => { pfMaterializeMonth(pf, alvo); return {}; });
        const m = S.personalFinance.months[alvo];
        // segundo ato NAO recria nem duplica
        pfMutate('materializa_teste2', pf => { pfMaterializeMonth(pf, alvo); return {}; });
        const m2 = S.personalFinance.months[alvo];
        return { virtAntes, ok: r1.ok,
                 incomes: m ? m.incomes.length : -1,
                 ruleId: m && m.incomes[0] ? m.incomes[0].ruleId : null,
                 recebido: m && m.incomes[0] ? m.incomes[0].receivedAmount : 'x',
                 status: m && m.incomes[0] ? m.incomes[0].status : null,
                 temCreatedAt: !!(m && typeof m.createdAt==='string' && m.createdAt.length>10),
                 idempotente: m === m2 && m2.incomes.length === 1 };
    }""")
    if r["virtAntes"] != 1:
        falhas.append(f"A: mes virtual deveria derivar 1 projecao da regra; veio {r['virtAntes']}")
    if not r["ok"] or r["incomes"] != 1:
        falhas.append(f"A: materializacao nao estampou a regra vigente: {r}")
    if r["ruleId"] != "pfr_t1":
        falhas.append("A: ruleId nao preservado na estampa")
    if r["recebido"] is not None or r["status"] != "PROJETADA":
        falhas.append(f"A: estampa deveria nascer PROJETADA com recebido null: {r['recebido']} {r['status']}")
    if not r["temCreatedAt"]:
        falhas.append("A: createdAt do ato ausente")
    if not r["idempotente"]:
        falhas.append("A: segundo ato recriou/duplicou o mes — materializacao deve ser idempotente")


def run_a_regra_nao_reescreve_materializado(page, falhas):
    """Editar a regra depois muda apenas meses virtuais; o materializado fica."""
    r = page.evaluate("""() => {
        pfMutate('edita_regra', pf => {
            const regra = pf.recurringIncome.find(x=>x.id==='pfr_t1');
            regra.amount = 9900000; // 99.000,00
            return {};
        });
        const virt = pfVirtualIncomes('2026-09');   // setembro segue virtual
        const m = S.personalFinance.months['2026-08'];
        const ago = m && Array.isArray(m.incomes) ? m.incomes[0] : null;
        return { setembroVe: virt[0] ? virt[0].projectedAmount : null,
                 agostoFicou: ago ? ago.projectedAmount : 'ESTAMPA_AUSENTE' };
    }""")
    if r["setembroVe"] != 9900000:
        falhas.append(f"A: mes virtual deveria refletir a regra editada; veio {r['setembroVe']}")
    if r["agostoFicou"] != 1200000:
        falhas.append(f"A: REGRA REESCREVEU MES MATERIALIZADO ({r['agostoFicou']}) — historia nao se reescreve por automacao")


def executar(nome, fn, falhas):
    """Excecao de sonda vira FALHA NOMEADA e a suite continua: um crash jamais
    engole as acusacoes ja acumuladas (licao da mutacao MA2)."""
    try:
        fn()
    except Exception as e:
        falhas.append(f"{nome}: EXCECAO no harness (sonda sem guarda?): {str(e).splitlines()[-1][:160]}")


# ---------- BLOCO B ----------

def run_b_adicionar_materializa_uma_vez(browser, url, falhas):
    """Mes virtual -> adicionar receita -> materializa EXATAMENTE uma vez."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key = '2026-08';
        const antes = Object.keys(S.personalFinance.months).length;
        window.prompt = () => 'Aluguel Sintetico';
        const r1 = pfActAddIncome(key, { name:'Aluguel Sintetico', projectedAmount: 280000 });
        const r2 = pfActAddIncome(key, { name:'Freela Sintetico', projectedAmount: null });
        const m = S.personalFinance.months[key];
        return { antes, ok: r1.ok && r2.ok, meses: Object.keys(S.personalFinance.months).length,
                 linhas: m.incomes.length,
                 recebidoNasce: m.incomes[0].receivedAmount,
                 projNull: m.incomes[1].projectedAmount,
                 disco: JSON.parse(localStorage.getItem('jpwealth_v9_state')).personalFinance.months[key].incomes.length };
    }""")
    if r["antes"] != 0 or r["meses"] != 1:
        falhas.append(f"B: materializacao deveria acontecer exatamente uma vez: {r['antes']}->{r['meses']} meses")
    if not r["ok"] or r["linhas"] != 2 or r["disco"] != 2:
        falhas.append(f"B: adicionar receitas falhou ou nao persistiu: {r}")
    if r["recebidoNasce"] is not None:
        falhas.append("B: receita nova deveria nascer com recebido null")
    if r["projNull"] is not None:
        falhas.append("B: projetado vazio deveria ser null, nao coagido")
    ctx.close()


def run_b_guardas_de_valor_e_status(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Salario', projectedAmount: 1200000 });
        const id = S.personalFinance.months[key].incomes[0].id;
        const negativa = pfActUpdateIncomeField(key, id, 'receivedAmount', -100);
        const recSemValor = pfActSetIncomeStatus(key, id, 'RECEBIDA');
        const poeZero = pfActUpdateIncomeField(key, id, 'receivedAmount', 0);
        const recComZero = pfActSetIncomeStatus(key, id, 'RECEBIDA');
        const limpaRecebida = pfActUpdateIncomeField(key, id, 'receivedAmount', null);
        const i = S.personalFinance.months[key].incomes[0];
        return { negOk: negativa.ok, semValorOk: recSemValor.ok, zeroOk: poeZero.ok && recComZero.ok,
                 limpaOk: limpaRecebida.ok, estado: {recebido: i.receivedAmount, status: i.status} };
    }""")
    if r["negOk"] is not False:
        falhas.append("B: valor negativo deveria ser recusado pela guarda de dominio")
    if r["semValorOk"] is not False:
        falhas.append("B: RECEBIDA sem recebido explicito deveria ser recusada")
    if not r["zeroOk"]:
        falhas.append("B: recebido 0 EXPLICITO deveria ser aceito e permitir RECEBIDA")
    if r["limpaOk"] is not False:
        falhas.append("B: limpar recebido de linha RECEBIDA deveria ser recusado")
    if r["estado"] != {"recebido": 0, "status": "RECEBIDA"}:
        falhas.append(f"B: estado final incoerente: {r['estado']}")
    ctx.close()


def run_b_cancelada_preserva_realizado(browser, url, falhas):
    """CANCELADA sai do projetado; o recebido informado permanece no realizado."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Projeto X', projectedAmount: 200000 });
        pfActAddIncome(key, { name:'Fixa', projectedAmount: 1000000 });
        const id = S.personalFinance.months[key].incomes[0].id;
        pfActUpdateIncomeField(key, id, 'receivedAmount', 50000);
        pfActSetIncomeStatus(key, id, 'CANCELADA');
        const m = S.personalFinance.months[key];
        return { projetado: pfProjectedIncome(m), recebido: pfKnownReceivedIncome(m),
                 aindaExiste: m.incomes.length };
    }""")
    if r["projetado"] != 1000000:
        falhas.append(f"B: CANCELADA deveria sair do projetado (esperava 1.000000, veio {r['projetado']})")
    if r["recebido"] != 50000:
        falhas.append(f"B: recebido da cancelada deveria permanecer no realizado (50000), veio {r['recebido']}")
    if r["aindaExiste"] != 2:
        falhas.append("B: cancelar nao e apagar — a linha deve continuar")
    ctx.close()


def run_b_recorrencia_fluxo_completo(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Salario', projectedAmount: 1200000 });
        const id = S.personalFinance.months[key].incomes[0].id;
        // liga recorrencia via ATO (o modal chama exatamente isto no confirmar)
        const liga = pfActConfigureRecurrence(key, id, { recorrente:true, amount:1200000, startMonth:'2026-08', endMonth:null });
        const setembroVirtual = pfVirtualIncomes('2026-09');
        // editar a regra: virtual muda, materializado nao
        const regra = S.personalFinance.recurringIncome[0];
        const edita = pfActConfigureRecurrence(key, id, { recorrente:true, amount:1300000, startMonth:'2026-08', endMonth:null });
        const setembroDepois = pfVirtualIncomes('2026-09');
        const agostoFicou = S.personalFinance.months['2026-08'].incomes[0].projectedAmount;
        // desligar nao apaga historico
        const desliga = pfActConfigureRecurrence(key, id, { recorrente:false });
        const setembroSem = pfVirtualIncomes('2026-09');
        const historicoFica = S.personalFinance.months['2026-08'].incomes.length;
        const linha0 = S.personalFinance.months[key].incomes[0] || null;
        return { ligaOk: liga.ok, ruleId: linha0 ? linha0.ruleId : 'LINHA_APAGADA',
                 virt1: setembroVirtual.length && setembroVirtual[0].projectedAmount,
                 virt2: setembroDepois.length && setembroDepois[0].projectedAmount,
                 agostoFicou, desligaOk: desliga.ok, virtSem: setembroSem.length,
                 historicoFica, regraFica: S.personalFinance.recurringIncome.length };
    }""")
    if not r["ligaOk"] or not r["ruleId"]:
        falhas.append(f"B: ligar recorrencia falhou ou nao vinculou ruleId: {r}")
    if r["virt1"] != 1200000:
        falhas.append(f"B: setembro virtual deveria projetar 1200000; veio {r['virt1']}")
    if r["virt2"] != 1300000:
        falhas.append(f"B: editar a regra deveria mudar o mes virtual; veio {r['virt2']}")
    if r["agostoFicou"] != 1200000:
        falhas.append(f"B: REGRA EDITADA REESCREVEU MES MATERIALIZADO: {r['agostoFicou']}")
    if not r["desligaOk"] or r["virtSem"] != 0:
        falhas.append(f"B: desligar deveria cessar projecoes futuras: {r}")
    if r["historicoFica"] != 1 or r["regraFica"] != 1:
        falhas.append("B: desligar APAGOU historico ou a regra — proibido")
    ctx.close()


def run_b_fantasma_edita_materializa(browser, url, falhas):
    """Editar linha fantasma de mes virtual materializa e aplica na estampa."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        pfMutate('seed', pf => { pf.recurringIncome.push({id:'pfr_g1', name:'Salario', amount:1200000,
            periodicity:'MENSAL', startMonth:'2026-01', endMonth:null, active:true}); return {}; });
        const alvo='2026-09';
        const antes = pfIsMaterialized(alvo);
        const r1 = pfActEditGhost(alvo, 'pfr_g1', 'receivedAmount', 1150000);
        const m = S.personalFinance.months[alvo];
        return { antes, ok: r1.ok, materializou: pfIsMaterialized(alvo),
                 recebido: m && m.incomes[0].receivedAmount,
                 projetadoDaRegra: m && m.incomes[0].projectedAmount,
                 ruleId: m && m.incomes[0].ruleId };
    }""")
    if r["antes"] is not False or not r["ok"] or not r["materializou"]:
        falhas.append(f"B: editar fantasma deveria materializar: {r}")
    if r["recebido"] != 1150000 or r["projetadoDaRegra"] != 1200000 or r["ruleId"] != "pfr_g1":
        falhas.append(f"B: estampa+edicao incoerentes: {r}")
    ctx.close()


def run_b_modal_cancelar_zero_mutacao(browser, url, falhas):
    """Abrir o modal de recorrencia e CANCELAR: zero mutacao, zero save."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Salario', projectedAmount: 1200000 });
        window.JPWFinBudget.render();
        const antes = JSON.stringify(S.personalFinance);
        let saves = 0; const orig = window.save;
        window.save = function(){ saves++; return orig.apply(this, arguments); };
        document.querySelector('[data-fi-cfg]').click();          // abre modal real
        document.getElementById('fbRecOn').checked = true;         // mexe no formulario
        document.getElementById('fbRecAmount').value = '9.999,99';
        document.getElementById('modalCancel').click();            // cancela
        window.save = orig;
        return { igual: antes === JSON.stringify(S.personalFinance), saves,
                 fechou: !document.getElementById('modalOverlay').classList.contains('show') };
    }""")
    if not r["igual"] or r["saves"] != 0:
        falhas.append(f"B: cancelar o modal MUTOU estado ou gravou ({r['saves']} saves)")
    if not r["fechou"]:
        falhas.append("B: modal nao fechou no cancelar")
    ctx.close()


# ---------- BLOCO C ----------

def run_c_despesa_nasce_honesta(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        const r1 = pfActAddExpense(key, { name:'Internet Fibra' });
        const e = S.personalFinance.months[key].expenses[0];
        return { ok:r1.ok, status:e.status, chaves: Object.keys(e).sort(),
                 nulos: [e.targetAmount, e.expectedAmount, e.executedCash, e.executedCard, e.installments] };
    }""")
    if not r["ok"] or r["status"] != "PENDENTE":
        falhas.append(f"C: despesa deveria nascer PENDENTE: {r}")
    if r["nulos"] != [None,None,None,None,None]:
        falhas.append(f"C: campos deveriam nascer null (nunca 0): {r['nulos']}")
    if "executedTotal" in r["chaves"] or "remaining" in r["chaves"]:
        falhas.append(f"C: DERIVADO PERSISTIDO no registro: {r['chaves']}")
    ctx.close()


def run_c_pago_exige_dois_canais(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddExpense(key, { name:'Internet' });
        const id = S.personalFinance.months[key].expenses[0].id;
        pfActUpdateExpenseField(key, id, 'executedCash', 12000);
        const soUmCanal = pfActSetExpenseStatus(key, id, 'PAGO');       // card null
        pfActUpdateExpenseField(key, id, 'executedCard', 0);
        const doisCanais = pfActSetExpenseStatus(key, id, 'PAGO');      // 0 explicito vale
        const limpaCanal = pfActUpdateExpenseField(key, id, 'executedCard', null); // PAGO: recusa
        const e = S.personalFinance.months[key].expenses[0];
        return { soUmCanalOk: soUmCanal.ok, doisOk: doisCanais.ok, limpaOk: limpaCanal.ok,
                 final: { cash: e.executedCash, card: e.executedCard, status: e.status },
                 executadoLinha: pfExpenseExecutedKnown(e) };
    }""")
    if r["soUmCanalOk"] is not False:
        falhas.append("C: PAGO com apenas um canal informado deveria ser recusado")
    if not r["doisOk"]:
        falhas.append("C: PAGO com cash=12000 e card=0 explicito deveria ser aceito")
    if r["limpaOk"] is not False:
        falhas.append("C: limpar canal de linha PAGO deveria ser recusado")
    if r["final"] != {"cash":12000,"card":0,"status":"PAGO"} or r["executadoLinha"] != 12000:
        falhas.append(f"C: estado final incoerente: {r}")
    ctx.close()


def run_c_cancelado_preserva_realizado(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddExpense(key, { name:'Assinatura' });
        pfActAddExpense(key, { name:'Aluguel' });
        const m0 = S.personalFinance.months[key];
        const idA = m0.expenses[0].id, idB = m0.expenses[1].id;
        pfActUpdateExpenseField(key, idA, 'expectedAmount', 5000);
        pfActUpdateExpenseField(key, idA, 'executedCard', 3000);
        pfActUpdateExpenseField(key, idB, 'expectedAmount', 172000);
        pfActSetExpenseStatus(key, idA, 'CANCELADO');
        const m = S.personalFinance.months[key];
        return { previsto: pfPlannedExpenses(m), executado: pfKnownExecutedExpenses(m), linhas: m.expenses.length };
    }""")
    if r["previsto"] != 172000:
        falhas.append(f"C: CANCELADO deveria sair do previsto (172000), veio {r['previsto']}")
    if r["executado"] != 3000:
        falhas.append(f"C: executado do cancelado deveria permanecer (3000), veio {r['executado']}")
    if r["linhas"] != 2:
        falhas.append("C: cancelar nao e apagar")
    ctx.close()


def run_c_parcelamento(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddExpense(key, { name:'Emprestimo' });
        const id = S.personalFinance.months[key].expenses[0].id;
        const excede = pfActSetExpenseInstallments(key, id, { paid:25, total:24 });   // defeito da planilha
        const negativo = pfActSetExpenseInstallments(key, id, { paid:-1, total:24 });
        const valido = pfActSetExpenseInstallments(key, id, { paid:16, total:24 });
        const e = S.personalFinance.months[key].expenses[0];
        const gravado = JSON.stringify(e.installments);          // ANTES do limpa: e.installments e referencia viva
        const chaves = Object.keys(JSON.parse(gravado||'{}'));
        const limpa = pfActSetExpenseInstallments(key, id, null);
        return { excedeOk: excede.ok, negOk: negativo.ok, validoOk: valido.ok,
                 gravado, chaves,
                 limpo: S.personalFinance.months[key].expenses[0].installments };
    }""")
    if r["excedeOk"] is not False:
        falhas.append("C: paid > total deveria ser recusado — o defeito da FALTA negativa nao entra")
    if r["negOk"] is not False:
        falhas.append("C: parcela negativa deveria ser recusada")
    if not r["validoOk"] or r["gravado"] != '{"total":24,"paid":16}':
        falhas.append(f"C: parcelamento valido nao gravou como {{total,paid}}: {r['gravado']}")
    if "remaining" in r["chaves"]:
        falhas.append("C: remaining PERSISTIDO — e derivado")
    if r["limpo"] is not None:
        falhas.append("C: limpar parcelamento deveria voltar a null")
    ctx.close()


# ---------- BLOCO D ----------

def run_d_parcial_nao_vira_total(browser, url, falhas):
    """2 de 3 receitas conhecidas -> saldo conhecido aparece, Sobra Realizada NAO."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Salario', projectedAmount: 1200000 });
        pfActAddIncome(key, { name:'Aluguel', projectedAmount: 280000 });
        pfActAddIncome(key, { name:'FX', projectedAmount: null });
        const m0 = S.personalFinance.months[key];
        pfActUpdateIncomeField(key, m0.incomes[0].id, 'receivedAmount', 1200000);
        pfActUpdateIncomeField(key, m0.incomes[1].id, 'receivedAmount', 280000);
        // FX permanece null — cobertura 2/3
        const r1 = pfMonthSummary(S.personalFinance.months[key]);
        window.JPWFinBudget.render();
        const texto = document.getElementById('fbSummary').innerText;
        return { conhecido: r1.knownReceivedIncome, sobra: r1.realizedSurplus,
                 saldoAux: r1.knownBalance, ratio: r1.incomeExpenseRatio,
                 cobertura: r1.incomeCoverage,
                 mostraIncompleto: texto.includes('Dados incompletos'),
                 mostraAux: texto.includes('Saldo conhecido'),
                 naoRotulaComoSobra: !/Sobra realizada\s*R\$/.test(texto) };
    }""")
    if r["conhecido"] != 1480000:
        falhas.append(f"D: conhecido deveria ser 1.480000 (R$ 14.800,00); veio {r['conhecido']}")
    if r["sobra"] is not None or r["ratio"] is not None:
        falhas.append(f"D: SOBRA/RATIO NAO EXISTEM com cobertura 2/3: sobra={r['sobra']} ratio={r['ratio']}")
    if r["cobertura"] != {"conhecidas":2,"total":3,"completa":False}:
        falhas.append(f"D: cobertura errada: {r['cobertura']}")
    if not (r["mostraIncompleto"] and r["mostraAux"] and r["naoRotulaComoSobra"]):
        falhas.append(f"D: UI apresentou parcial como total: {r}")
    ctx.close()


def run_d_completo_e_deficitario(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Salario', projectedAmount: 500000 });
        const m0 = S.personalFinance.months[key];
        pfActUpdateIncomeField(key, m0.incomes[0].id, 'receivedAmount', 500000);
        pfActSetIncomeStatus(key, m0.incomes[0].id, 'RECEBIDA');
        pfActAddExpense(key, { name:'Aluguel' });
        const idE = S.personalFinance.months[key].expenses[0].id;
        pfActUpdateExpenseField(key, idE, 'expectedAmount', 600000);
        pfActUpdateExpenseField(key, idE, 'executedCash', 600000);
        pfActUpdateExpenseField(key, idE, 'executedCard', 0);
        pfActSetExpenseStatus(key, idE, 'PAGO');
        const r1 = pfMonthSummary(S.personalFinance.months[key]);
        window.JPWFinBudget.render();
        const texto = document.getElementById('fbSummary').innerText;
        return { completo: r1.completo, sobra: r1.realizedSurplus, ratio: r1.incomeExpenseRatio,
                 exibeNegativa: texto.includes('-R$ 1.000,00') };
    }""")
    if not r["completo"] or r["sobra"] != -100000:
        falhas.append(f"D: mes completo deficitario deveria dar sobra -100000 exatos; veio {r['sobra']}")
    if abs(r["ratio"] - 1.2) > 1e-9:
        falhas.append(f"D: ratio deveria ser 1,2 (120%); veio {r['ratio']}")
    if not r["exibeNegativa"]:
        falhas.append("D: sobra negativa deveria exibir -R$ 1.000,00 — deficit e legitimo, sem clamp")
    ctx.close()


def run_d_ratio_receita_zero(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Unico', projectedAmount: 100000 });
        const id = S.personalFinance.months[key].incomes[0].id;
        pfActUpdateIncomeField(key, id, 'receivedAmount', 0);   // zero EXPLICITO
        pfActSetIncomeStatus(key, id, 'RECEBIDA');
        const r1 = pfMonthSummary(S.personalFinance.months[key]);
        return { completo: r1.completo, sobra: r1.realizedSurplus, ratio: r1.incomeExpenseRatio };
    }""")
    if not r["completo"] or r["sobra"] != 0:
        falhas.append(f"D: receita 0 explicita e completa — sobra 0 real: {r}")
    if r["ratio"] is not None:
        falhas.append(f"D: ratio com receita zero deveria ser N/A (null), jamais divisao: {r['ratio']}")
    ctx.close()


# ---------- BLOCO E ----------

def run_e_destinacao_guardas(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        const semValor = pfActAddAllocation(key, { label:'Reserva', amount:null });
        const negativa = pfActAddAllocation(key, { label:'Reserva', amount:-100 });
        const ok1 = pfActAddAllocation(key, { label:'Reserva Emergencia', amount:100000 });
        const ok2 = pfActAddAllocation(key, { label:'Investimentos', amount:200000 });
        const m = S.personalFinance.months[key];
        return { semValorOk: semValor.ok, negOk: negativa.ok, criadas: m.allocations.length,
                 total: pfTotalAllocated(m) };
    }""")
    if r["semValorOk"] is not False:
        falhas.append("E: destinacao sem valor deveria ser recusada — linha sem valor nao se cria")
    if r["negOk"] is not False:
        falhas.append("E: destinacao negativa deveria ser recusada")
    if r["criadas"] != 2 or r["total"] != 300000:
        falhas.append(f"E: totalAllocated errado: {r}")
    ctx.close()


def run_e_excedente_sem_fabricacao(browser, url, falhas):
    """Realizado incompleto: destinar pode; saldo restante realizado NAO se fabrica."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        pfActAddIncome(key, { name:'Salario', projectedAmount: 500000 });  // recebido null -> incompleto
        pfActAddAllocation(key, { label:'Reserva', amount: 100000 });
        const m = S.personalFinance.months[key];
        const naoAlocadaIncompleto = pfUnallocatedSurplus(m);
        window.JPWFinBudget.render();
        const textoIncompleto = document.getElementById('fbAllocations').innerText;
        // completa o realizado: recebe 500, destina 600 -> excede (legitimo, alerta)
        pfActUpdateIncomeField(key, m.incomes[0].id, 'receivedAmount', 500000);
        pfActUpdateAllocationField(key, m.allocations[0].id, 'amount', 600000);
        const naoAlocadaCompleta = pfUnallocatedSurplus(S.personalFinance.months[key]);
        window.JPWFinBudget.render();
        const temAlerta = !!document.getElementById('fbAllocExceeds');
        const textoCompleto = document.getElementById('fbAllocations').innerText;
        return { naoAlocadaIncompleto, mostraSemSaldo: textoIncompleto.includes('realizado incompleto'),
                 destinouMesmoAssim: S.personalFinance.months[key].allocations.length===1,
                 naoAlocadaCompleta, temAlerta,
                 exibeNegativa: textoCompleto.includes('-R$ 1.000,00') };
    }""")
    if r["naoAlocadaIncompleto"] is not None:
        falhas.append(f"E: com realizado incompleto o saldo restante NAO existe; veio {r['naoAlocadaIncompleto']}")
    if not r["mostraSemSaldo"] or not r["destinouMesmoAssim"]:
        falhas.append(f"E: destinar deve continuar permitido sem fabricar saldo: {r}")
    if r["naoAlocadaCompleta"] != -100000:
        falhas.append(f"E: excedente negativo legitimo deveria ser -100000 sem clamp; veio {r['naoAlocadaCompleta']}")
    if not r["temAlerta"] or not r["exibeNegativa"]:
        falhas.append(f"E: alerta de excesso/valor negativo nao exibidos: {r}")
    ctx.close()


# ---------- BLOCO F ----------

def run_f_notas(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const key='2026-08';
        const vazia = pfActAddNote(key, '   ');
        const ok = pfActAddNote(key, 'Renegociar internet');
        const id = S.personalFinance.months[key].notes[0].id;
        const n0 = JSON.parse(JSON.stringify(S.personalFinance.months[key].notes[0]));
        pfActToggleNoteStatus(key, id);
        const dep = S.personalFinance.months[key].notes[0].status;
        pfActToggleNoteStatus(key, id);
        const volta = S.personalFinance.months[key].notes[0].status;
        return { vaziaOk: vazia.ok, ok: ok.ok, nasce: n0.status,
                 chaves: Object.keys(n0).sort(), dep, volta };
    }""")
    if r["vaziaOk"] is not False:
        falhas.append("F: nota vazia deveria ser recusada")
    if not r["ok"] or r["nasce"] != "PENDENTE":
        falhas.append(f"F: nota deveria nascer PENDENTE: {r}")
    if r["chaves"] != ["createdAt","id","status","text"]:
        falhas.append(f"F: nota deveria ter SO texto+status(+id,createdAt) — sem tags/prioridade: {r['chaves']}")
    if r["dep"] != "RESOLVIDO" or r["volta"] != "PENDENTE":
        falhas.append(f"F: toggle de status errado: {r['dep']}/{r['volta']}")
    ctx.close()


def _semear_pendencias(page):
    """Julho: 2 despesas + 1 nota pendentes; junho: 1 despesa. Mais um mes com
    nulls SEM status pendente — que NAO pode contar."""
    page.evaluate("""() => {
        for(const [k, desp, nota] of [['2026-06',1,0],['2026-07',2,1]]){
            for(let i=0;i<desp;i++) pfActAddExpense(k, { name:'Desp '+k+'-'+i });
            for(let i=0;i<nota;i++) pfActAddNote(k, 'Pend '+k);
        }
        // mes com null mas SEM pendencia de status: despesa CANCELADA com canais null
        pfActAddExpense('2026-05', { name:'Cancelada' });
        const id = S.personalFinance.months['2026-05'].expenses[0].id;
        pfActSetExpenseStatus('2026-05', id, 'CANCELADO');
        // nota resolvida tambem nao conta
        pfActAddNote('2026-05', 'Resolvida');
        pfActToggleNoteStatus('2026-05', S.personalFinance.months['2026-05'].notes[0].id);
    }""")


def run_f_pendencias_fluxo(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    _semear_pendencias(page)
    r = page.evaluate("""() => {
        const pend = pfPendingBefore(pfCurrentMonthKey());
        // entrada DELIBERADA no workspace dispara o modal (uma vez por sessao)
        window.JPWFin.ui.selectView('overview');
        window.JPWFin.ui.selectView('mensal');
        const modalTexto = document.getElementById('modalBox').innerText;
        const abriu = document.getElementById('modalOverlay').classList.contains('show');
        // Revisar abre o mes pendente mais antigo, EDITAVEL
        document.getElementById('fbPendReview').click();
        const foiPara = document.querySelector('.fb-month-label').textContent;
        // resolver a pendencia de junho NO PROPRIO junho (mes passado editavel)
        const idJun = S.personalFinance.months['2026-06'].expenses[0].id;
        pfActUpdateExpenseField('2026-06', idJun, 'executedCash', 10000);
        pfActUpdateExpenseField('2026-06', idJun, 'executedCard', 0);
        const pago = pfActSetExpenseStatus('2026-06', idJun, 'PAGO');
        const pendDepois = pfPendingBefore(pfCurrentMonthKey());
        window.JPWFinBudget.render();
        const bannerAindaTem = !!document.getElementById('fbPendingBanner');
        return { pend, modalTexto, abriu, foiPara, pagoOk: pago.ok,
                 pendDepois, bannerAindaTem };
    }""")
    esperado = [{"key":"2026-06","despesas":1,"notas":0},{"key":"2026-07","despesas":2,"notas":1}]
    if r["pend"] != esperado:
        falhas.append(f"F: pendencias erradas (null/resolvido NAO contam): {r['pend']}")
    if not r["abriu"] or "pendências de meses anteriores" not in r["modalTexto"]:
        falhas.append("F: modal de pendencias nao abriu na entrada deliberada")
    if "2 despesa(s)" not in r["modalTexto"] or "1 informação" not in r["modalTexto"]:
        falhas.append(f"F: contagens do modal erradas: {r['modalTexto'][:200]}")
    if r["foiPara"] != "JUNHO 2026":
        falhas.append(f"F: Revisar deveria abrir o mes pendente mais antigo editavel; foi para {r['foiPara']}")
    if not r["pagoOk"]:
        falhas.append("F: resolver pendencia em mes passado deveria ser permitido (edicao deliberada)")
    if r["pendDepois"] != [{"key":"2026-07","despesas":2,"notas":1}]:
        falhas.append(f"F: apos resolver junho, so julho deveria pender: {r['pendDepois']}")
    if not r["bannerAindaTem"]:
        falhas.append("F: banner deveria persistir enquanto julho pende")
    # modal NAO reabre por rerender, por Hoje nem por nova entrada na MESMA
    # sessao — E a sonda precisa estar NO MES CORRENTE, senao a guarda de
    # competencia mascara a falta da flag (a mutacao MF2 sobreviveu assim).
    r2 = page.evaluate("""() => {
        closeModal();
        document.querySelector('[data-fb-today]').click();      // volta ao corrente (gatilho deliberado)
        const aposHoje = document.getElementById('modalOverlay').classList.contains('show');
        closeModal();
        window.JPWFinBudget.render(); window.JPWFinBudget.render();
        window.JPWFin.ui.selectView('overview');
        window.JPWFin.ui.selectView('mensal');
        const aposReentrada = document.getElementById('modalOverlay').classList.contains('show');
        return { aposHoje, aposReentrada,
                 noCorrente: document.querySelector('.fb-month-label').textContent };
    }""")
    if r2["aposHoje"] or r2["aposReentrada"]:
        falhas.append(f"F: modal em LOOP — deveria aparecer uma vez por sessao: {r2}")
    ctx.close()


def run_f_resolver_tudo_apaga_banner(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    _semear_pendencias(page)
    r = page.evaluate("""() => {
        for(const k of ['2026-06','2026-07']){
            const m = S.personalFinance.months[k];
            for(const e of m.expenses.filter(x=>x.status==='PENDENTE')){
                pfActUpdateExpenseField(k, e.id, 'executedCash', 1000);
                pfActUpdateExpenseField(k, e.id, 'executedCard', 0);
                pfActSetExpenseStatus(k, e.id, 'PAGO');
            }
            for(const n of m.notes.filter(x=>x.status==='PENDENTE')) pfActToggleNoteStatus(k, n.id);
        }
        window.JPWFinBudget.render();
        return { pend: pfPendingBefore(pfCurrentMonthKey()).length,
                 banner: !!document.getElementById('fbPendingBanner') };
    }""")
    if r["pend"] != 0 or r["banner"]:
        falhas.append(f"F: com tudo resolvido o alerta deveria desaparecer: {r}")
    ctx.close()


def run_sentinela_leitura_pfclose02(browser, url, falhas):
    """PF-CLOSE-02: unidade desconhecida nao autoriza interpretar como BRL.

    Estrutura da tela permanece legivel (nomes, status, parcelas, coberturas,
    notas), mas nenhum montante e apresentado, nenhum campo monetario expoe
    valor, nenhum percentual monetariamente derivado sobrevive, escrita segue
    bloqueada e o round-trip BRL -> XX_UNIT -> BRL restaura exatamente.
    Zero DEVE virar "—", nao "R$ 0,00".
    """
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const M = pfCurrentMonthKey();
        // fixture com valores desacoplados E um zero canonico deliberado
        pfActAddIncome(M, {name:'Salario', projectedAmount:1000000});
        const mes = S.personalFinance.months[M];
        pfActUpdateIncomeField(M, mes.incomes[0].id, 'receivedAmount', 850000);
        pfActAddExpense(M, {name:'Isento'});
        pfActUpdateExpenseField(M, mes.expenses[0].id, 'expectedAmount', 0);   // zero canonico
        pfActUpdateExpenseField(M, mes.expenses[0].id, 'executedCash', 0);
        pfActUpdateExpenseField(M, mes.expenses[0].id, 'executedCard', 0);
        pfActSetExpenseInstallments(M, mes.expenses[0].id, {total:24, paid:16});
        pfActAddAllocation(M, {label:'Reserva', amount:300000});
        pfActAddNote(M, 'conferir fatura');
        window.JPWFinBudget.render();
        const root = document.getElementById('finpesBudgetRoot');
        const brlTexto = root.innerText;
        const brlOk = brlTexto.includes('R$ 8.500,00') && brlTexto.includes('R$ 10.000,00')
                   && brlTexto.includes('R$ 0,00');
        const foto = JSON.stringify(S.personalFinance);
        const lsAntes = localStorage.getItem('jpwealth_v9_state');
        const mesesAntes = Object.keys(S.personalFinance.months).join(',');

        // --- unidade desconhecida ---
        let saves = 0; const origSave = window.save;
        window.save = function(){ saves++; return origSave.apply(this, arguments); };
        S.personalFinance.moneyUnit = 'XX_UNIT';
        window.JPWFinBudget.render();
        const t = root.innerText;
        const semRS = !t.includes('R$');
        const semZeroBRL = !/R\$\s*0,00/.test(t);
        const semPercentual = !/%/.test(t);
        // estrutura nao monetaria preservada
        const valores = [...root.querySelectorAll('input')].map(i => i.value);
        const estrutura = valores.includes('Salario') && valores.includes('Isento')
          && valores.includes('Reserva') && valores.includes('16/24')
          && t.includes('conferir fatura') && t.includes('PENDENTE')
          && t.includes('Receitas') && t.includes('Despesas')
          && t.includes('Resumo do Mês') && t.includes('Destino do Excedente');
        // nenhum campo monetario expoe valor
        const semCampoMonetario = root.querySelectorAll('input.fb-money:not(.fb-parc)').length === 0;
        const inertes = [...root.querySelectorAll('input, select, button')]
          .filter(el => !el.hasAttribute('data-fb-nav') && !el.hasAttribute('data-fb-today')
                     && !el.hasAttribute('data-fb-review'))
          .every(el => el.disabled);
        // escrita bloqueada
        const atos = {
          income: pfActAddIncome(M, {name:'X', projectedAmount:1}).erro,
          incomeEdit: pfActUpdateIncomeField(M, mes.incomes[0].id, 'receivedAmount', 1).erro,
          expense: pfActAddExpense(M, {name:'Y'}).erro,
          expenseEdit: pfActUpdateExpenseField(M, mes.expenses[0].id, 'expectedAmount', 1).erro,
          alloc: pfActAddAllocation(M, {label:'Z', amount:1}).erro,
          note: pfActAddNote(M, 'nao deve entrar').erro,
        };
        const escritaBloqueada = Object.values(atos)
          .every(e => e === 'READ_ONLY_UNSUPPORTED_MONEY_UNIT');
        window.save = origSave;
        S.personalFinance.moneyUnit = 'BRL_CENTS';
        const agregadoIntacto = JSON.stringify(S.personalFinance) === foto;
        const lsIntacto = localStorage.getItem('jpwealth_v9_state') === lsAntes;
        const semMaterializacao = Object.keys(S.personalFinance.months).join(',') === mesesAntes;

        // --- round-trip ---
        window.JPWFinBudget.render();
        const roundTrip = root.innerText === brlTexto;
        return { brlOk, semRS, semZeroBRL, semPercentual, estrutura, semCampoMonetario,
                 inertes, escritaBloqueada, atos, zeroSave: saves===0,
                 agregadoIntacto, lsIntacto, semMaterializacao, roundTrip };
    }""")
    for chave, valor in r.items():
        if chave == 'atos':
            continue
        if valor is not True:
            falhas.append(f"PF-CLOSE-02 budget: {chave} falhou: {json.dumps(r, ensure_ascii=False)[:700]}")
            break
    if erros:
        falhas.append(f"PF-CLOSE-02 budget: pageerror: {erros[:2]}")
    ctx.close()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            ctx, page, erros = boot(browser, url)
            executar("A chave/rotulo", lambda: run_a_chave_e_rotulo(page, falhas), falhas)
            executar("A selo virtual", lambda: run_a_selo_virtual(page, falhas), falhas)
            executar("A navegar", lambda: run_a_navegar_nao_escreve(page, falhas), falhas)
            executar("A materializacao", lambda: run_a_materializacao_por_ato(page, falhas), falhas)
            executar("A regra x materializado", lambda: run_a_regra_nao_reescreve_materializado(page, falhas), falhas)
            if erros:
                falhas.append(f"pageerror: {erros}")
            ctx.close()

            executar("A write gate", lambda: run_a_write_gate(browser, url, falhas), falhas)
            executar("PF-CLOSE-02 sentinela leitura", lambda: run_sentinela_leitura_pfclose02(browser, url, falhas), falhas)
            executar("B add materializa 1x", lambda: run_b_adicionar_materializa_uma_vez(browser, url, falhas), falhas)
            executar("B guardas valor/status", lambda: run_b_guardas_de_valor_e_status(browser, url, falhas), falhas)
            executar("B cancelada preserva", lambda: run_b_cancelada_preserva_realizado(browser, url, falhas), falhas)
            executar("B recorrencia", lambda: run_b_recorrencia_fluxo_completo(browser, url, falhas), falhas)
            executar("B fantasma", lambda: run_b_fantasma_edita_materializa(browser, url, falhas), falhas)
            executar("B modal cancelar", lambda: run_b_modal_cancelar_zero_mutacao(browser, url, falhas), falhas)
            executar("C nasce honesta", lambda: run_c_despesa_nasce_honesta(browser, url, falhas), falhas)
            executar("C dois canais", lambda: run_c_pago_exige_dois_canais(browser, url, falhas), falhas)
            executar("C cancelado preserva", lambda: run_c_cancelado_preserva_realizado(browser, url, falhas), falhas)
            executar("C parcelamento", lambda: run_c_parcelamento(browser, url, falhas), falhas)
            executar("D parcial nao vira total", lambda: run_d_parcial_nao_vira_total(browser, url, falhas), falhas)
            executar("D completo/deficitario", lambda: run_d_completo_e_deficitario(browser, url, falhas), falhas)
            executar("D ratio receita zero", lambda: run_d_ratio_receita_zero(browser, url, falhas), falhas)
            executar("E guardas", lambda: run_e_destinacao_guardas(browser, url, falhas), falhas)
            executar("E excedente honesto", lambda: run_e_excedente_sem_fabricacao(browser, url, falhas), falhas)
            executar("F notas", lambda: run_f_notas(browser, url, falhas), falhas)
            executar("F pendencias fluxo", lambda: run_f_pendencias_fluxo(browser, url, falhas), falhas)
            executar("F resolver tudo", lambda: run_f_resolver_tudo_apaga_banner(browser, url, falhas), falhas)
            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES BUDGET TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
