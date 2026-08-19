#!/usr/bin/env python3
"""Cenarios (PF-05) — suite focal N3.

Cenario e hipotese INDEPENDENTE: le/copia um mes deliberadamente e jamais
escreve em months; mes editado jamais reescreve cenario. baselineFrom e
proveniencia, nunca vinculo vivo. Fixtures sinteticas.
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
        "() => typeof S === 'object' && typeof pfActAddScenario === 'function'")
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => typeof S === 'object' && typeof pfActAddScenario === 'function'")
    page.wait_for_timeout(350)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return context, page, erros


def executar(nome, fn, falhas):
    try:
        fn()
    except Exception as e:
        falhas.append(f"{nome}: EXCECAO no harness: {str(e).splitlines()[-1][:160]}")


def run_a_crud_e_formulas(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const vazio = pfActAddScenario({name:'Base atual', kind:'BASE', horizon:null});
        const s0 = S.personalFinance.scenarios[0];
        const zeroDemonstrado = { r: pfScenarioIncome(s0), d: pfScenarioExpenses(s0), s: pfScenarioSurplus(s0) };
        pfActAddScenarioItem(s0.id,'incomes',{name:'Salario', amount:1200000});
        pfActAddScenarioItem(s0.id,'incomes',{name:'Aluguel', amount:280000});
        pfActAddScenarioItem(s0.id,'expenses',{name:'Custo fixo', amount:600000});
        pfActAddScenarioItem(s0.id,'expenses',{name:'Mercado', amount:200000});
        pfActAddScenarioItem(s0.id,'expenses',{name:'Lazer', amount:150000});
        const semValor = pfActAddScenarioItem(s0.id,'incomes',{name:'X', amount:null});
        const negativo = pfActAddScenarioItem(s0.id,'incomes',{name:'X', amount:-1});
        const zeroOk = pfActAddScenarioItem(s0.id,'expenses',{name:'Isento', amount:0});
        const casc = pfScenarioCascade(s0);
        // deficitario
        pfActAddScenario({name:'Aperto', kind:'PESSIMISTA', horizon:'2027-03'});
        const s1 = S.personalFinance.scenarios[1];
        pfActAddScenarioItem(s1.id,'incomes',{name:'R', amount:500000});
        pfActAddScenarioItem(s1.id,'expenses',{name:'D', amount:650000});
        // cascata em cenario DEFICITARIO: o saldo cruza zero no meio — qualquer
        // "protecao" (min/clamp) faz o ultimo saldo divergir do surplus
        const cascDef = pfScenarioCascade(s1);
        return { vazioOk: vazio.ok, zeroDemonstrado,
                 cascDefUltimo: cascDef.length ? cascDef[cascDef.length-1].saldo : null,
                 cascDefConfere: cascDef.length ? (cascDef[cascDef.length-1].saldo === pfScenarioSurplus(s1)) : false,
                 mesesMaterializados: Object.keys(S.personalFinance.months).length,
                 receita: pfScenarioIncome(s0), despesa: pfScenarioExpenses(s0), sobra: pfScenarioSurplus(s0),
                 semValorOk: semValor.ok, negativoOk: negativo.ok, zeroOkOk: zeroOk.ok,
                 cascataUltimo: casc.length ? casc[casc.length-1].saldo : null,
                 cascataConfere: casc.length ? (casc[casc.length-1].saldo === pfScenarioSurplus(s0)) : false,
                 deficit: pfScenarioSurplus(s1),
                 chavesCenario: Object.keys(s0).sort() };
    }""")
    if not r["vazioOk"] or r["zeroDemonstrado"] != {"r":0,"d":0,"s":0}:
        falhas.append(f"A: cenario vazio deveria demonstrar 0/0/0: {r['zeroDemonstrado']}")
    if r["receita"] != 1480000 or r["despesa"] != 950000 or r["sobra"] != 530000:
        falhas.append(f"A: 14.800/9.500/5.300 esperados: {r['receita']}/{r['despesa']}/{r['sobra']}")
    if r["semValorOk"] is not False:
        falhas.append("A: item sem valor NAO cria linha")
    if r["negativoOk"] is not False:
        falhas.append("A: valor negativo deveria ser recusado")
    if not r["zeroOkOk"]:
        falhas.append("A: amount 0 explicito e valido")
    if not r["cascataConfere"]:
        falhas.append(f"A: ultimo saldo da cascata deve coincidir com o surplus: {r['cascataUltimo']} vs {r['sobra']}")
    if r["deficit"] != -150000:
        falhas.append(f"A: deficit -1.500 sem clamp: {r['deficit']}")
    if not r["cascDefConfere"] or r["cascDefUltimo"] != -150000:
        falhas.append(f"A: cascata do deficitario deve TERMINAR em -150000 == surplus (sem min/clamp no meio): {r['cascDefUltimo']}")
    if r["mesesMaterializados"] != 0:
        falhas.append(f"A: atos de CENARIO materializaram {r['mesesMaterializados']} mes(es) — cenario jamais cria mes")
    if "surplus" in r["chavesCenario"] or "total" in r["chavesCenario"] or "cascade" in r["chavesCenario"]:
        falhas.append(f"A: DERIVADO PERSISTIDO no cenario: {r['chavesCenario']}")
    ctx.close()


SEED_MES = """
      // valores DESCOLADOS de proposito: recebido != projetado e executado !=
      // previsto — a copia canonica usa o PLANEJADO; qualquer mutante que leia
      // realizado produz numero diferente e se denuncia.
      pfActAddIncome('2026-08', {name:'Salario', projectedAmount:1200000});
      (function(){ const m=S.personalFinance.months['2026-08'];
        pfActUpdateIncomeField('2026-08', m.incomes[0].id, 'receivedAmount', 1100000); })();
      pfActAddIncome('2026-08', {name:'FX', projectedAmount:null});
      pfActAddIncome('2026-08', {name:'Cancelada', projectedAmount:500000});
      (function(){ const m=S.personalFinance.months['2026-08'];
        pfActUpdateIncomeField('2026-08', m.incomes[2].id, 'receivedAmount', 0);
        pfActSetIncomeStatus('2026-08', m.incomes[2].id, 'CANCELADA'); })();
      pfActAddExpense('2026-08', {name:'Aluguel'});
      (function(){ const m=S.personalFinance.months['2026-08'];
        pfActUpdateExpenseField('2026-08', m.expenses[0].id, 'expectedAmount', 172000);
        pfActUpdateExpenseField('2026-08', m.expenses[0].id, 'executedCash', 150000);
        pfActUpdateExpenseField('2026-08', m.expenses[0].id, 'executedCard', 0); })();
"""


def run_b_copia_bloqueia_fonte_incompleta(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + SEED_MES + """
        const antes = S.personalFinance.scenarios.length;
        const r1 = pfActCreateScenarioFromMonth('2026-08', {name:'Base', kind:'BASE', horizon:'2027-03'});
        return { ok: r1.ok, erro: r1.erro, criados: S.personalFinance.scenarios.length - antes };
    }""")
    if r["ok"] is not False or "FX" not in r["erro"]:
        falhas.append(f"B: fonte com FX sem projetado deveria BLOQUEAR nomeando a falta: {r}")
    if r["criados"] != 0:
        falhas.append("B: bloqueio deveria criar ZERO cenario — nada de copia parcial")
    ctx.close()


def run_b_copia_correta_e_independencia(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("() => {" + SEED_MES + """
        // completa a fonte: FX ganha projetado
        const m0 = S.personalFinance.months['2026-08'];
        pfActUpdateIncomeField('2026-08', m0.incomes[1].id, 'projectedAmount', 22000);
        const r1 = pfActCreateScenarioFromMonth('2026-08', {name:'Base', kind:'BASE', horizon:'2027-03'});
        const sc = S.personalFinance.scenarios[0];
        const idsMes = new Set([...m0.incomes.map(i=>i.id), ...m0.expenses.map(e=>e.id)]);
        const idsCenario = [...sc.incomes.map(i=>i.id), ...sc.expenses.map(e=>e.id)];
        // captura IMEDIATA da copia (sc e referencia viva; as edicoes de
        // independencia abaixo nao podem contaminar a evidencia da copia)
        const incomesCopiados = sc.incomes.map(i=>({name:i.name, amount:i.amount}));
        const expensesCopiados = sc.expenses.map(e=>({name:e.name, amount:e.amount}));
        const copiadaCancelada = sc.incomes.some(i=>i.name==='Cancelada');
        const antesCenario = JSON.stringify(sc);
        // 1) editar o MES depois da copia: cenario nao muda
        pfActUpdateIncomeField('2026-08', m0.incomes[0].id, 'projectedAmount', 1300000);
        const cenarioIntacto = antesCenario === JSON.stringify(pfFindScenario(S.personalFinance, sc.id));
        // 2) editar o CENARIO: mes nao muda
        const antesMes = JSON.stringify(S.personalFinance.months['2026-08']);
        pfActUpdateScenarioItem(sc.id,'incomes',sc.incomes[0].id,'amount',9900000);
        pfActAddScenarioItem(sc.id,'expenses',{name:'Nova hipotese', amount:100});
        const mesIntacto = antesMes === JSON.stringify(S.personalFinance.months['2026-08']);
        // 3) excluir cenario: mes nao muda; nenhum mes materializado a mais
        const mesesAntes = Object.keys(S.personalFinance.months).length;
        pfActDeleteScenario(sc.id);
        const mesIntacto2 = antesMes === JSON.stringify(S.personalFinance.months['2026-08']);
        return { ok: r1.ok,
                 valores: { rec0: 1200000, copiado0: null },
                 incomes: incomesCopiados,
                 expenses: expensesCopiados,
                 baselineFrom: sc.baselineFrom,
                 idsNovos: idsCenario.every(id=>!idsMes.has(id)),
                 copiadaCancelada, cenarioIntacto, mesIntacto, mesIntacto2,
                 mesesDepois: Object.keys(S.personalFinance.months).length === mesesAntes,
                 cenariosRestantes: S.personalFinance.scenarios.length };
    }""")
    if not r["ok"]:
        falhas.append(f"B: copia com fonte completa deveria passar: {r}")
    if r["incomes"] != [{"name":"Salario","amount":1200000},{"name":"FX","amount":22000}]:
        falhas.append(f"B: copia deveria usar PROJETADO das nao-canceladas: {r['incomes']}")
    if r["expenses"] != [{"name":"Aluguel","amount":172000}]:
        falhas.append(f"B: copia deveria usar PREVISTO (nunca executado): {r['expenses']}")
    if r["copiadaCancelada"]:
        falhas.append("B: receita CANCELADA foi copiada — proibido")
    if r["baselineFrom"] != "2026-08":
        falhas.append(f"B: baselineFrom deveria registrar proveniencia: {r['baselineFrom']}")
    if not r["idsNovos"]:
        falhas.append("B: IDS DO MES REUTILIZADOS no cenario — copia deve ser profunda")
    if not r["cenarioIntacto"]:
        falhas.append("B: editar o mes depois da copia REESCREVEU o cenario — baseline virou vinculo vivo")
    if not r["mesIntacto"] or not r["mesIntacto2"]:
        falhas.append("B: editar/excluir cenario TOCOU no mes real — invariante N3 violada")
    if not r["mesesDepois"] or r["cenariosRestantes"] != 0:
        falhas.append(f"B: exclusao deveria remover so o cenario: {r}")
    ctx.close()


def run_b_virtual_nao_e_baseline(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        pfMutate('seed_regra', pf => { pf.recurringIncome.push({id:'pfr_s1', name:'Salario', amount:1200000,
            periodicity:'MENSAL', startMonth:'2026-01', endMonth:null, active:true}); return {}; });
        const r1 = pfActCreateScenarioFromMonth('2026-09', {name:'X', kind:'BASE', horizon:null});
        return { ok: r1.ok, erro: r1.erro, virtualProjeta: pfVirtualIncomes('2026-09').length===1,
                 criados: S.personalFinance.scenarios.length,
                 materializou: Object.keys(S.personalFinance.months).length };
    }""")
    if r["ok"] is not False or "não está registrado" not in r["erro"]:
        falhas.append(f"B: mes VIRTUAL nao pode ser baseline (mesmo com regra projetando): {r}")
    if r["criados"] != 0 or r["materializou"] != 0:
        falhas.append("B: tentativa bloqueada nao pode criar cenario NEM materializar mes")
    ctx.close()


def run_ab_write_gate(browser, url, falhas):
    mut = """
      S.personalFinance = { schemaVersion:1, moneyUnit:'XX_UNIT',
        months:{'2026-08':{createdAt:'x', incomes:[{id:'i1',name:'A',projectedAmount:100,receivedAmount:null,status:'PROJETADA',ruleId:null}], expenses:[], debtSnapshots:[], allocations:[], notes:[]}},
        recurringIncome:[], debts:[], creditLines:[],
        scenarios:[{id:'pfs_x', name:'X', horizon:null, kind:'BASE', incomes:[{id:'si1',name:'A',amount:1}], expenses:[], baselineFrom:null, createdAt:'x'}] };
    """
    ctx, page, erros = boot(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => {
        const antes = JSON.stringify(S.personalFinance);
        const acts = [
          pfActAddScenario({name:'Y', kind:'BASE', horizon:null}),
          pfActUpdateScenarioMeta('pfs_x', {name:'Z', kind:'LIVRE', horizon:null}),
          pfActDeleteScenario('pfs_x'),
          pfActAddScenarioItem('pfs_x','incomes',{name:'N', amount:1}),
          pfActUpdateScenarioItem('pfs_x','incomes','si1','amount',2),
          pfActDeleteScenarioItem('pfs_x','incomes','si1'),
          pfActCreateScenarioFromMonth('2026-08', {name:'W', kind:'BASE', horizon:null}),
        ];
        return { bloqueados: acts.every(a=>a.ok===false && a.erro==='READ_ONLY_UNSUPPORTED_MONEY_UNIT'),
                 erros: acts.map(a=>a.erro),
                 intacto: antes === JSON.stringify(S.personalFinance) };
    }""")
    if not r["bloqueados"]:
        falhas.append(f"AB: unidade desconhecida deveria bloquear TODOS os atos de cenario: {r['erros']}")
    if not r["intacto"]:
        falhas.append("AB: bloqueio mutou o agregado")
    ctx.close()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            executar("A crud/formulas", lambda: run_a_crud_e_formulas(browser, url, falhas), falhas)
            executar("B copia bloqueada", lambda: run_b_copia_bloqueia_fonte_incompleta(browser, url, falhas), falhas)
            executar("B copia/independencia", lambda: run_b_copia_correta_e_independencia(browser, url, falhas), falhas)
            executar("B virtual", lambda: run_b_virtual_nao_e_baseline(browser, url, falhas), falhas)
            executar("AB write gate", lambda: run_ab_write_gate(browser, url, falhas), falhas)
            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES SCENARIOS TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
