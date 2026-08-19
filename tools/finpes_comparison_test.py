#!/usr/bin/env python3
"""Comparativo Mensal (PF-04) — suite focal N3.

PF-04 e READ -> DERIVE -> COMPARE -> PRESENT: consome os consolidadores
canonicos do PF-02/PF-03 e jamais recalcula o dominio. Soma parcial nunca vira
baseline; M-1 e M-12 sao calendario, nunca "ultimo mes com dados"; sobra nao
tem percentual; ratio compara em pontos percentuais; credito vigente nao entra
em serie historica. Fixtures sinteticas; numero certo pelo motivo errado = falha.
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
        "() => typeof S === 'object' && typeof pfCompCompare === 'function'")
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => typeof S === 'object' && typeof pfCompCompare === 'function'")
    page.wait_for_timeout(350)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return context, page, erros


def executar(nome, fn, falhas):
    try:
        fn()
    except Exception as e:
        falhas.append(f"{nome}: EXCECAO no harness: {str(e).splitlines()[-1][:160]}")


SEED_MES_COMPLETO = """
      // mes COMPLETO em {K}
      pfActAddIncome('{K}', {name:'Salario', projectedAmount:1500000});
      (function(){ const m=S.personalFinance.months['{K}'];
        pfActUpdateIncomeField('{K}', m.incomes[0].id, 'receivedAmount', {REC});
        pfActSetIncomeStatus('{K}', m.incomes[0].id, 'RECEBIDA'); })();
      pfActAddExpense('{K}', {name:'Custo'});
      (function(){ const m=S.personalFinance.months['{K}'];
        pfActUpdateExpenseField('{K}', m.expenses[0].id, 'expectedAmount', {EXE});
        pfActUpdateExpenseField('{K}', m.expenses[0].id, 'executedCash', {EXE});
        pfActUpdateExpenseField('{K}', m.expenses[0].id, 'executedCard', 0);
        pfActSetExpenseStatus('{K}', m.expenses[0].id, 'PAGO'); })();
"""

def seed_completo(k, rec, exe):
    return SEED_MES_COMPLETO.replace('{K}', k).replace('{REC}', str(rec)).replace('{EXE}', str(exe))


def run_ab_mes_a_mes_completo(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + seed_completo('2026-07', 1400000, 1000000)
                      + seed_completo('2026-08', 1500000, 900000) + """
        // isca anti-recalculo: CANCELADA com recebido 0 explicito e projetado
        // alto — a metrica canonica NAO muda; qualquer soma propria denuncia.
        pfActAddIncome('2026-08', {name:'Cancelada Isca', projectedAmount:99900000});
        (function(){ const m=S.personalFinance.months['2026-08'];
          const i = m.incomes[m.incomes.length-1];
          pfActUpdateIncomeField('2026-08', i.id, 'receivedAmount', 0);
          pfActSetIncomeStatus('2026-08', i.id, 'CANCELADA'); })();
        const c = pfCompCompare('2026-08', '2026-07');
        return c.metrics;
    }""")
    m = r
    if not (m["receita"]["available"] and m["receita"]["delta"]==100000 and abs(m["receita"]["relativeChange"]-100000/1400000)<1e-12):
        falhas.append(f"AB: receita AGOxJUL deveria dar +100000 e +7,1%: {m['receita']}")
    if not (m["despesa"]["available"] and m["despesa"]["delta"]==-100000 and abs(m["despesa"]["relativeChange"]+0.1)<1e-12):
        falhas.append(f"AB: despesa deveria dar -100000 e -10%: {m['despesa']}")
    if not (m["sobra"]["available"] and m["sobra"]["delta"]==200000):
        falhas.append(f"AB: sobra deveria dar delta +200000: {m['sobra']}")
    if "relativeChange" in m["sobra"]:
        falhas.append("AB: SOBRA NAO TEM PERCENTUAL — chave relativeChange presente")
    if not m["comprometimento"]["available"]:
        falhas.append(f"AB: comprometimento deveria comparar: {m['comprometimento']}")
    else:
        pp = m["comprometimento"]["deltaPP"]
        esperado = (900000/1500000) - (1000000/1400000)
        if abs(pp-esperado)>1e-12:
            falhas.append(f"AB: delta deveria ser em PONTOS PERCENTUAIS ({esperado:.4f}): {pp}")
        if "relativeChange" in m["comprometimento"] or "delta" in m["comprometimento"]:
            falhas.append("AB: comprometimento deveria expor SO deltaPP")
    # divida: nenhum relevante nos dois -> COMPLETE 0 e 0, sem alteracao
    if not (m["divida"]["available"] and m["divida"]["delta"]==0 and m["divida"]["semAlteracao"] and m["divida"]["relativeChange"] is None):
        falhas.append(f"AB: divida 0x0 deveria ser sem alteracao com percentual N/A: {m['divida']}")
    ctx.close()


def run_ab_parcial_nao_vira_baseline(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + seed_completo('2026-08', 1500000, 900000) + """
        // JUL PARCIAL: receita sem recebido explicito
        pfActAddIncome('2026-07', {name:'Salario', projectedAmount:1400000});
        const c = pfCompCompare('2026-08', '2026-07');
        return { receita: c.metrics.receita, sobra: c.metrics.sobra };
    }""")
    if r["receita"]["available"] is not False or "parcial" not in r["receita"]["motivo"]:
        falhas.append(f"AB: JUL parcial NAO pode ser baseline — N/A com motivo: {r['receita']}")
    if r["sobra"]["available"] is not False:
        falhas.append("AB: sobra com origem parcial deveria ser N/A")
    ctx.close()


def run_ab_virtual_nao_pula_mes(browser, url, falhas):
    """AGO completo, JUL virtual, JUN completo: AGO x JUL = indisponivel.
    NUNCA substituir JUL por JUN."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + seed_completo('2026-06', 1300000, 800000)
                      + seed_completo('2026-08', 1500000, 900000) + """
        const c = pfCompCompare('2026-08', pfCompBaselines('2026-08').previousMonth);
        return { baseKey: c.baseKey, receita: c.metrics.receita,
                 junExiste: pfIsMaterialized('2026-06'), julVirtual: !pfIsMaterialized('2026-07') };
    }""")
    if r["baseKey"] != "2026-07":
        falhas.append(f"AB: baseline deveria ser EXATAMENTE 2026-07 (calendario), veio {r['baseKey']} — trocar por JUN muda a pergunta")
    if r["receita"]["available"] is not False or "não registrado" not in r["receita"]["motivo"]:
        falhas.append(f"AB: comparacao com mes virtual deveria ser indisponivel com motivo: {r['receita']}")
    if not (r["junExiste"] and r["julVirtual"]):
        falhas.append("AB: pre-condicao do cenario quebrada")
    ctx.close()


def run_ab_ano_contra_ano_e_baseline_zero(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + seed_completo('2025-08', 1000000, 1000000)
                      + seed_completo('2026-08', 1500000, 900000) + """
        const yoy = pfCompCompare('2026-08', pfCompBaselines('2026-08').yearAgo);
        // baseline monetario ZERO: mes com receita recebida 0 explicita
        pfActAddIncome('2026-01', {name:'Unica', projectedAmount:100000});
        (function(){ const m=S.personalFinance.months['2026-01'];
          pfActUpdateIncomeField('2026-01', m.incomes[0].id, 'receivedAmount', 0);
          pfActSetIncomeStatus('2026-01', m.incomes[0].id, 'RECEBIDA'); })();
        pfActAddIncome('2026-02', {name:'Unica', projectedAmount:100000});
        (function(){ const m=S.personalFinance.months['2026-02'];
          pfActUpdateIncomeField('2026-02', m.incomes[0].id, 'receivedAmount', 50000);
          pfActSetIncomeStatus('2026-02', m.incomes[0].id, 'RECEBIDA'); })();
        const zeroBase = pfCompCompare('2026-02', '2026-01');
        return { yoyKey: yoy.baseKey, yoyReceita: yoy.metrics.receita,
                 zb: zeroBase.metrics.receita };
    }""")
    if r["yoyKey"] != "2025-08":
        falhas.append(f"AB: YoY deveria ser exatamente M-12 (2025-08): {r['yoyKey']}")
    if not (r["yoyReceita"]["available"] and r["yoyReceita"]["delta"]==500000 and abs(r["yoyReceita"]["relativeChange"]-0.5)<1e-12):
        falhas.append(f"AB: YoY receita deveria dar +500000/+50%: {r['yoyReceita']}")
    if not (r["zb"]["available"] and r["zb"]["delta"]==50000 and r["zb"]["relativeChange"] is None):
        falhas.append(f"AB: baseline 0 -> delta disponivel, percentual N/A (nunca infinito): {r['zb']}")
    ctx.close()


def run_ab_sobra_cruzando_zero(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + seed_completo('2026-07', 1000000, 1050000)   # sobra -500
                      + seed_completo('2026-08', 1500000, 1450000) + """       // sobra +500
        const c = pfCompCompare('2026-08', '2026-07');
        return c.metrics.sobra;
    }""")
    if not (r["available"] and r["current"]==50000 and r["baseline"]==-50000 and r["delta"]==100000):
        falhas.append(f"AB: sobra -500 -> +500 deveria dar delta +100000: {r}")
    if "relativeChange" in r:
        falhas.append("AB: sobra cruzando zero JAMAIS tem percentual (+200% seria absurdo)")
    ctx.close()


def run_ab_divida_no_comparativo(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + seed_completo('2026-07', 1000000, 800000)
                      + seed_completo('2026-08', 1000000, 800000) + """
        pfActAddDebt({creditor:'Sigma', type:'EMPRESTIMO', description:'', originalAmount:null,
            installmentAmount:null, installmentsTotal:null, startMonth:'2026-01', closedMonth:null});
        const id = S.personalFinance.debts[0].id;
        pfActRecordDebtSnapshot('2026-07', id, {balance:1500000});
        pfActRecordDebtSnapshot('2026-08', id, {balance:1200000});
        const ok = pfCompCompare('2026-08','2026-07').metrics.divida;
        // segunda divida relevante SEM snapshot em AGO -> divida parcial -> N/A
        pfActAddDebt({creditor:'Tau', type:'CARTAO', description:'', originalAmount:null,
            installmentAmount:null, installmentsTotal:null, startMonth:'2026-01', closedMonth:null});
        pfActRecordDebtSnapshot('2026-07', S.personalFinance.debts[1].id, {balance:100000});
        const parcial = pfCompCompare('2026-08','2026-07').metrics.divida;
        // snapshot futuro nao vaza: metrica de JUL nao muda por causa de AGO
        const julSozinho = pfCompMetrics('2026-07').divida;
        return { ok, parcial, julSozinho };
    }""")
    if not (r["ok"]["available"] and r["ok"]["delta"]==-300000 and abs(r["ok"]["relativeChange"]+0.2)<1e-12):
        falhas.append(f"AB: divida 15.000->12.000 deveria dar -300000/-20%: {r['ok']}")
    if r["parcial"]["available"] is not False or "parcial 1/2" not in r["parcial"]["motivo"]:
        falhas.append(f"AB: divida parcial em AGO deveria tornar a comparacao N/A nomeando 1/2: {r['parcial']}")
    if not (r["julSozinho"]["status"]=="COMPLETE" and r["julSozinho"]["value"]==1600000):
        falhas.append(f"AB: JUL continua completo com 16.000 — futuro nao contamina: {r['julSozinho']}")
    ctx.close()


def run_ab_edicao_retroativa_sem_cache(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + seed_completo('2026-07', 1400000, 1000000)
                      + seed_completo('2026-08', 1500000, 900000) + """
        const antes = pfCompCompare('2026-08','2026-07').metrics.receita.delta;
        // corrige JUL no ORCAMENTO (PF-02): recebido vira 1.450.000
        const m = S.personalFinance.months['2026-07'];
        pfActUpdateIncomeField('2026-07', m.incomes[0].id, 'receivedAmount', 1450000);
        const depois = pfCompCompare('2026-08','2026-07').metrics.receita.delta;
        return { antes, depois };
    }""")
    if r["antes"] != 100000 or r["depois"] != 50000:
        falhas.append(f"AB: edicao retroativa deveria refletir imediatamente (100000->50000): {r}")
    ctx.close()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            executar("AB mes a mes", lambda: run_ab_mes_a_mes_completo(browser, url, falhas), falhas)
            executar("AB parcial baseline", lambda: run_ab_parcial_nao_vira_baseline(browser, url, falhas), falhas)
            executar("AB virtual nao pula", lambda: run_ab_virtual_nao_pula_mes(browser, url, falhas), falhas)
            executar("AB yoy e zero", lambda: run_ab_ano_contra_ano_e_baseline_zero(browser, url, falhas), falhas)
            executar("AB sobra cruza zero", lambda: run_ab_sobra_cruzando_zero(browser, url, falhas), falhas)
            executar("AB divida", lambda: run_ab_divida_no_comparativo(browser, url, falhas), falhas)
            executar("AB retroativa", lambda: run_ab_edicao_retroativa_sem_cache(browser, url, falhas), falhas)
            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES COMPARISON TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
