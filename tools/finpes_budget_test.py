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
            executar("B add materializa 1x", lambda: run_b_adicionar_materializa_uma_vez(browser, url, falhas), falhas)
            executar("B guardas valor/status", lambda: run_b_guardas_de_valor_e_status(browser, url, falhas), falhas)
            executar("B cancelada preserva", lambda: run_b_cancelada_preserva_realizado(browser, url, falhas), falhas)
            executar("B recorrencia", lambda: run_b_recorrencia_fluxo_completo(browser, url, falhas), falhas)
            executar("B fantasma", lambda: run_b_fantasma_edita_materializa(browser, url, falhas), falhas)
            executar("B modal cancelar", lambda: run_b_modal_cancelar_zero_mutacao(browser, url, falhas), falhas)
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
