#!/usr/bin/env python3
"""Cenarios (PF-05) — suite focal N3.

Cenario e hipotese INDEPENDENTE: le/copia um mes deliberadamente e jamais
escreve em months; mes editado jamais reescreve cenario. baselineFrom e
proveniencia, nunca vinculo vivo. Fixtures sinteticas.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
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
    context = browser.new_context(viewport={"width": 1440, "height": 950}, service_workers="block")
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


# ---------- BLOCOS C/D (UI) ----------

def boot_ui(browser, url, mutacao_js=None):
    ctx, page, erros = boot(browser, url, mutacao_js)
    page.evaluate("() => { navigateToScreen('finpes'); window.JPWFin.ui.selectView('cenarios'); }")
    return ctx, page, erros


def run_cd_ui_fluxo_real(browser, url, falhas):
    ctx, page, erros = boot_ui(browser, url)
    r = page.evaluate("""() => {
        // cancelar modal de novo cenario: zero mutacao
        const antes = JSON.stringify(S.personalFinance);
        window.JPWFinScenarios.render();
        document.querySelector('[data-fs-new]').click();
        document.getElementById('fsName').value = 'Nao Deve Existir';
        document.getElementById('modalCancel').click();
        const cancelou = antes === JSON.stringify(S.personalFinance);
        // cria pela UI: HOJE (horizon vazio) e MAR/2027
        document.querySelector('[data-fs-new]').click();
        document.getElementById('fsName').value = 'Base atual';
        document.getElementById('fsKind').value = 'BASE';
        document.getElementById('modalConfirm').click();
        window.JPWFinScenarios.render();
        document.querySelector('[data-fs-new]').click();
        document.getElementById('fsName').value = 'Aperto';
        document.getElementById('fsKind').value = 'PESSIMISTA';
        document.getElementById('fsHorizon').value = '2027-03';
        document.getElementById('modalConfirm').click();
        window.JPWFinScenarios.render();
        // itens pela UI (prompts stubados)
        const sc = S.personalFinance.scenarios[0];
        let fila = ['Salario', '12.000,00', 'Custo', '9.500,00'];
        window.prompt = () => fila.shift();
        document.querySelector(`[data-fs-add-item][data-fs-lista="incomes"][data-fs-sc="${sc.id}"]`).click();
        document.querySelector(`[data-fs-add-item][data-fs-lista="expenses"][data-fs-sc="${sc.id}"]`).click();
        const texto = document.getElementById('finpesScenariosRoot').innerText;
        return { cancelou, cenarios: S.personalFinance.scenarios.length,
                 hoje: texto.indexOf('HOJE'), mar: texto.indexOf('MARÇO 2027'),
                 agrupado: texto.indexOf('HOJE') >= 0 && texto.indexOf('MARÇO 2027') > texto.indexOf('HOJE'),
                 totais: texto.includes('R$ 12.000,00') && texto.includes('R$ 9.500,00') && texto.includes('R$ 2.500,00'),
                 semForecast: !/(previsão|probabilidade|resultado esperado)/i.test(texto) };
    }""")
    if not r["cancelou"]:
        falhas.append("CD: cancelar o modal MUTOU o estado")
    if r["cenarios"] != 2 or not r["agrupado"]:
        falhas.append(f"CD: agrupamento por horizonte (HOJE antes de MARÇO 2027) falhou: {r}")
    if not r["totais"]:
        falhas.append(f"CD: totais 12.000/9.500/2.500 nao renderizados")
    if not r["semForecast"]:
        falhas.append("CD: linguagem de FORECAST detectada — cenario e hipotese")
    ctx.close()


def run_cd_cascata_visual_e_copia_ui(browser, url, falhas):
    ctx, page, erros = boot_ui(browser, url)
    r = page.evaluate("() => {" + SEED_MES + """
        const m0 = S.personalFinance.months['2026-08'];
        pfActUpdateIncomeField('2026-08', m0.incomes[1].id, 'projectedAmount', 22000);
        window.JPWFinScenarios.render();
        // copia pela UI
        document.querySelector('[data-fs-from]').click();
        document.getElementById('fsFromMonth').value = '2026-08';
        document.getElementById('fsName').value = 'Base de agosto';
        document.getElementById('fsKind').value = 'BASE';
        document.getElementById('fsHorizon').value = '2027-03';
        document.getElementById('modalConfirm').click();
        window.JPWFinScenarios.render();
        const sc = S.personalFinance.scenarios[0];
        const texto = document.getElementById('finpesScenariosRoot').innerText;
        // cascata visual: saldo apos Aluguel = 1.222.000-172.000... receita total 1.200.000+22.000=1.222.000; despesa 172.000 -> saldo 1.050.000
        return { criado: !!sc, proveniencia: texto.includes('criado a partir de AGOSTO 2026'),
                 saldoCascata: texto.includes('R$ 10.500,00'),
                 baselineFrom: sc && sc.baselineFrom };
    }""")
    if not r["criado"] or r["baselineFrom"] != "2026-08":
        falhas.append(f"CD: copia pela UI falhou: {r}")
    if not r["proveniencia"]:
        falhas.append("CD: proveniencia 'criado a partir de AGOSTO 2026' ausente")
    if not r["saldoCascata"]:
        falhas.append("CD: saldo da cascata (R$ 10.500,00) ausente do card")
    ctx.close()


def run_cd_sentinela_visual(browser, url, falhas):
    mut = """
      S.personalFinance = { schemaVersion:1, moneyUnit:'XX_UNIT', months:{},
        recurringIncome:[], debts:[], creditLines:[],
        scenarios:[{id:'pfs_x', name:'X', horizon:null, kind:'BASE', incomes:[], expenses:[], baselineFrom:null, createdAt:'x'}] };
    """
    ctx, page, erros = boot_ui(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => {
        window.JPWFinScenarios.render();
        const root = document.getElementById('finpesScenariosRoot');
        return { botoesDesabilitados: [...root.querySelectorAll('[data-fs-new],[data-fs-from],[data-fs-add-item]')].every(b=>b.disabled),
                 banner: !document.getElementById('finpesUnitNotice').hidden,
                 intacto: S.personalFinance.moneyUnit==='XX_UNIT' };
    }""")
    if not r["botoesDesabilitados"] or not r["banner"] or not r["intacto"]:
        falhas.append(f"CD: sentinela visual falhou: {r}")
    ctx.close()


def run_cd_sentinela_leitura(browser, url, falhas):
    """Round-trip BRL_CENTS -> XX_UNIT -> BRL_CENTS (HA PF-05).

    Unidade desconhecida: a tela permanece legivel estruturalmente mas NAO
    interpreta montante algum como BRL (zero "R$", totais/cascata como "—",
    nenhum campo monetario editavel); toda escrita segue bloqueada e o agregado
    fica byte a byte intacto. Restaurada a unidade, os valores originais
    reaparecem exatamente.
    """
    ctx, page, erros = boot_ui(browser, url)
    r = page.evaluate("""() => {
        // fase 1 — BRL_CENTS: interpretacao monetaria normal
        pfActAddScenario({name:'Hipotese base', kind:'BASE', horizon:null});
        const sc = S.personalFinance.scenarios[0];
        pfActAddScenarioItem(sc.id,'incomes',{name:'Salario', amount:1000000});
        pfActAddScenarioItem(sc.id,'expenses',{name:'Moradia', amount:400000});
        pfActAddScenarioItem(sc.id,'expenses',{name:'Mercado', amount:250000});
        window.JPWFinScenarios.render();
        const root = document.getElementById('finpesScenariosRoot');
        const antesTexto = root.innerText;
        const brlNormal = antesTexto.includes('R$ 10.000,00')
          && antesTexto.includes('R$ 6.000,00') && antesTexto.includes('R$ 3.500,00');
        // fase 2 — XX_UNIT: leitura nao afirma BRL; escrita segue bloqueada
        const foto = JSON.stringify(S.personalFinance);
        S.personalFinance.moneyUnit = 'XX_UNIT';
        window.JPWFin.ui.selectView('cenarios');
        const t = root.innerText;
        const banner = !document.getElementById('finpesUnitNotice').hidden;
        const zeroBRL = !t.includes('R$');
        const totaisIndisponiveis = t.includes('Receita total: —')
          && t.includes('Despesa total: —') && t.includes('Sobra/Falta: —');
        // nomes vivem em value de <input> (nao aparecem em innerText)
        const nomes = [...root.querySelectorAll('input.fb-text')].map(el => el.value);
        const estrutura = t.includes('Hipotese base') && t.includes('CASCATA')
          && ['Salario','Moradia','Mercado'].every(n => nomes.includes(n));
        const semCampoMonetario = root.querySelectorAll('input.fb-money').length === 0;
        const affordancesInertes = [...root.querySelectorAll('button, input')].every(el => el.disabled);
        const escritaBloqueada =
          pfActAddScenarioItem(sc.id,'incomes',{name:'X', amount:1}).erro === 'READ_ONLY_UNSUPPORTED_MONEY_UNIT'
          && pfActUpdateScenarioItem(sc.id,'expenses',sc.expenses[0].id,'amount',1).erro === 'READ_ONLY_UNSUPPORTED_MONEY_UNIT'
          && pfActDeleteScenario(sc.id).erro === 'READ_ONLY_UNSUPPORTED_MONEY_UNIT';
        S.personalFinance.moneyUnit = 'BRL_CENTS';
        const agregadoIntacto = JSON.stringify(S.personalFinance) === foto;
        // fase 3 — restaurar: valores originais reaparecem exatamente
        window.JPWFin.ui.selectView('cenarios');
        const roundTrip = root.innerText === antesTexto;
        const bannerSumiu = document.getElementById('finpesUnitNotice').hidden;
        return { brlNormal, banner, zeroBRL, totaisIndisponiveis, estrutura,
                 semCampoMonetario, affordancesInertes, escritaBloqueada,
                 agregadoIntacto, roundTrip, bannerSumiu };
    }""")
    for chave, valor in r.items():
        if valor is not True:
            falhas.append(f"CD sentinela leitura: {chave} falhou: {r}")
            break
    if erros:
        falhas.append(f"CD sentinela leitura: pageerror: {erros[:2]}")
    ctx.close()


# ---------- X2-01: persistência PF; mesmas asserções antes/depois ----------

def x2_boot(browser, url, viewport=None):
    fixture = json.loads((ROOT / 'tools/fixtures/personal_finance_v1.json').read_text())['personalFinance']
    ctx, page, errors = boot(browser, url, 'S.personalFinance = ' + json.dumps(fixture) + ';')
    if viewport:
        page.set_viewport_size(viewport)
    page.evaluate("""() => {
      window.__x2alerts=[]; window.alert=m=>window.__x2alerts.push(String(m));
      window.__x2nativeSet=Storage.prototype.setItem;
      window.__x2nativeGet=Storage.prototype.getItem;
      window.__x2originalSave=save;
      window.__x2originalLog=dgLogChange;
      window.__x2quota=false; window.__x2readFail=false; window.__x2writes=0;
      Storage.prototype.setItem=function(k,v){
        if(k===LSKEY){ window.__x2writes++; if(window.__x2quota) throw new DOMException('Synthetic quota refusal','QuotaExceededError'); }
        return window.__x2nativeSet.call(this,k,v);
      };
      Storage.prototype.getItem=function(k){
        if(k===LSKEY && window.__x2readFail) throw new Error('Synthetic read refusal');
        return window.__x2nativeGet.call(this,k);
      };
    }""")
    return ctx, page, errors


def x2_snapshot(page):
    return page.evaluate("""() => ({pf:JSON.stringify(S.personalFinance),
      log:JSON.stringify(S.dataGovernance.changeLog),
      raw:window.__x2nativeGet.call(localStorage,LSKEY),
      scenarios:S.personalFinance.scenarios.length,
      unknown:jpWealthPersistenceOutcomeIsUnknown(), writes:window.__x2writes})""")


def x2_trace(name, value):
    print('X2 EVIDENCE ' + name + ': ' + json.dumps(value, ensure_ascii=False), flush=True)


def run_x2_refusal_retry(browser, url, failures):
    ctx, page, errors = x2_boot(browser, url)
    try:
        before = x2_snapshot(page)
        first = page.evaluate("""() => {
          window.__x2quota=true;
          return pfActAddScenario({name:'X2 retry',kind:'BASE',horizon:null});
        }""")
        rejected = x2_snapshot(page)
        page.evaluate("window.__x2quota=false")
        retry = page.evaluate("pfActAddScenario({name:'X2 retry',kind:'BASE',horizon:null})")
        after = x2_snapshot(page)
        x2_trace('refusal-retry', {'first':first,'retry':retry,'beforeCount':before['scenarios'],
                 'refusedCount':rejected['scenarios'],'finalCount':after['scenarios'],
                 'pfRollback':rejected['pf']==before['pf'],'logRollback':rejected['log']==before['log'],
                 'diskUnchanged':rejected['raw']==before['raw']})
        assert first['ok'] is False and first['persistido'] is False
        assert rejected['pf']==before['pf'] and rejected['log']==before['log'], 'ato recusado ficou em PF/log'
        assert rejected['raw']==before['raw'], 'recusa alterou disco'
        assert retry['ok'] is True and after['scenarios']==before['scenarios']+1, 'retry não foi único'
        assert json.loads(after['raw'])['personalFinance']==json.loads(after['pf'])
        page.reload(wait_until='load')
        assert page.evaluate('S.personalFinance.scenarios.length')==before['scenarios']+1
        assert not errors, errors
    finally:
        ctx.close()


def run_x2_refusal_matrix(browser, url, failures):
    # Every condition has positive evidence of no write; no exception from save
    # is treated as such. Different gates keep their original recovery semantics.
    for condition in ['quota','read','serialize','generic','recovery','conflict']:
        ctx, page, errors = x2_boot(browser, url)
        try:
            page.evaluate("""() => {
              S.dataGovernance.changeLog=Array.from({length:400},(_,i)=>({id:'old-'+i,ts:'2026-01-01T00:00:00Z',entity:'other',action:'kept',recordId:String(i),label:'synthetic'}));
              S.nocoda.x2Other={kept:'before'}; S.personalFinance.x2Unknown={nested:[null,0,'keep']};
              save();
              window.__x2pfRef=S.personalFinance;
            }""")
            before = x2_snapshot(page)
            page.evaluate("""condition => {
              if(condition==='quota') window.__x2quota=true;
              if(condition==='read') window.__x2readFail=true;
              if(condition==='serialize') S.nocoda.x2Cycle=S.nocoda;
              if(condition==='generic') blockJPWealthPersistence();
              if(condition==='recovery') jpWealthLoadRecovery.active=true;
              if(condition==='conflict'){
                const newer=JSON.parse(window.__x2nativeGet.call(localStorage,LSKEY));
                newer.nocoda.x2FromOtherTab='newer';
                window.__x2nativeSet.call(localStorage,LSKEY,JSON.stringify(newer));
              }
            }""", condition)
            disk_expected=page.evaluate('window.__x2nativeGet.call(localStorage,LSKEY)')
            result=page.evaluate("pfActAddScenario({name:'Must not exist',kind:'BASE',horizon:null})")
            after=x2_snapshot(page)
            x2_trace(condition,{'result':result,'pfRollback':before['pf']==after['pf'],
                     'logRollback':before['log']==after['log'],'diskUnchanged':disk_expected==after['raw'],
                     'globalKind':page.evaluate('jpWealthPersistenceFailure.kind')})
            assert result['ok'] is False and result['persistido'] is False, condition
            assert before['pf']==after['pf'] and before['log']==after['log'], condition+' ghost PF/log, including cap400'
            assert disk_expected==after['raw'], condition+' overwrote disk'
            assert page.evaluate("S.nocoda.x2Other.kept==='before'"), 'other aggregate rolled back'
            if condition=='conflict':
                assert page.evaluate("jpWealthPersistenceFailure.kind==='conflict'")
                page.reload(wait_until='load')
                assert page.evaluate("S.nocoda.x2FromOtherTab==='newer'")
            elif condition=='recovery':
                assert page.evaluate('jpWealthLoadRecovery.active')
            else:
                page.evaluate("""() => {window.__x2quota=false;window.__x2readFail=false;
                  delete S.nocoda.x2Cycle;resumeJPWealthPersistence();
                  S.nocoda.x2Later='later legitimate flow';save();} """)
                saved=page.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
                assert saved['personalFinance']==json.loads(before['pf']), 'later save incorporated ghost'
                assert saved['dataGovernance']['changeLog']==json.loads(before['log'])
                assert saved['nocoda']['x2Later']=='later legitimate flow'
                page.reload(wait_until='load')
                assert page.evaluate('JSON.stringify(S.personalFinance)')==before['pf']
        finally:
            ctx.close()


def run_x2_unknown_and_prewrite(browser, url, failures):
    for when in ['before-write','after-write']:
        ctx, page, errors=x2_boot(browser,url)
        try:
            before=x2_snapshot(page)
            page.evaluate("""when=>{
              save=function(){
                if(when==='after-write') window.__x2originalSave();
                throw new Error('Synthetic escaped save exception');
              };
            }""",when)
            first=page.evaluate("pfActAddScenario({name:'Uncertain',kind:'BASE',horizon:null})")
            uncertain=x2_snapshot(page)
            again=page.evaluate("""() => {resumeJPWealthPersistence();
              return pfActAddScenario({name:'Uncertain',kind:'BASE',horizon:null});} """)
            after=x2_snapshot(page)
            x2_trace(when,{'first':first,'again':again,'unknown':after['unknown'],
                     'tentativeCount':uncertain['scenarios'],'noSecondAct':uncertain['pf']==after['pf'],
                     'diskChanged':after['raw']!=before['raw']})
            assert first['ok'] is False and first['persistido'] is None and uncertain['unknown']
            assert 'não repita' in first['erro'].lower()
            assert uncertain['scenarios']==before['scenarios']+1, 'UNKNOWN rolled back without evidence'
            assert again['ok'] is False and again['persistido'] is None
            assert uncertain['pf']==after['pf'] and uncertain['log']==after['log'] and uncertain['raw']==after['raw']
            page.evaluate('() => {save=window.__x2originalSave;S.nocoda.x2Later=true;}')
            assert page.evaluate('save()') is False, 'global UNKNOWN barrier was reopened'
            page.reload(wait_until='load')
            expected=before['scenarios']+(1 if when=='after-write' else 0)
            assert page.evaluate('S.personalFinance.scenarios.length')==expected
        finally:
            ctx.close()
    # Exception before calling save is demonstrably pre-write, not UNKNOWN.
    ctx,page,errors=x2_boot(browser,url)
    try:
        before=x2_snapshot(page)
        page.evaluate("""() => {dgLogChange=function(){window.__x2originalLog.apply(null,arguments);throw new Error('Synthetic log failure');};} """)
        result=page.evaluate("pfActAddScenario({name:'Log refusal',kind:'BASE',horizon:null})")
        after=x2_snapshot(page)
        x2_trace('prewrite-log',{'result':result,'pfRollback':before['pf']==after['pf'],'logRollback':before['log']==after['log']})
        assert result['ok'] is False and result['persistido'] is False and not after['unknown']
        assert before['pf']==after['pf'] and before['log']==after['log'] and before['raw']==after['raw'] and before['writes']==after['writes']
    finally:
        ctx.close()


def run_x2_ui(browser,url,failures):
    for viewport,theme in [({'width':1440,'height':950},'dark'),({'width':390,'height':844},'light')]:
        ctx,page,errors=x2_boot(browser,url,viewport)
        try:
            page.evaluate("""theme=>{document.documentElement.dataset.theme=theme;
              navigateToScreen('finpes');window.JPWFin.ui.selectView('cenarios');} """,theme)
            before=x2_snapshot(page)
            page.locator('[data-fs-new]').click()
            page.locator('#fsName').fill('Synthetic retry UI')
            page.locator('#fsKind').select_option('PESSIMISTA')
            page.locator('#fsHorizon').fill('2027-03')
            page.evaluate('window.__x2quota=true')
            page.locator('#modalConfirm').click()
            rejected=x2_snapshot(page)
            draft={'name':page.locator('#fsName').input_value(),'kind':page.locator('#fsKind').input_value(),'horizon':page.locator('#fsHorizon').input_value()}
            alert=page.evaluate('window.__x2alerts.at(-1)')
            modal_visible=page.locator('#modalOverlay').is_visible()
            evidence_dir=os.environ.get('JPW_PF_EVIDENCE_DIR')
            if evidence_dir:
                page.screenshot(path=str(Path(evidence_dir)/('pf-refused-'+theme+'.png')),full_page=True)
            x2_trace('ui-refused-'+theme,{'draft':draft,'alert':alert,'modal':modal_visible,
                     'pfRollback':before['pf']==rejected['pf'],'logRollback':before['log']==rejected['log'],'diskUnchanged':before['raw']==rejected['raw']})
            assert modal_visible and draft=={'name':'Synthetic retry UI','kind':'PESSIMISTA','horizon':'2027-03'}
            assert alert and 'persist' in alert.lower()
            assert page.locator('#persistenceAlert').is_visible(), 'global failure banner disappeared'
            assert rejected['pf']==before['pf'] and rejected['log']==before['log'] and rejected['raw']==before['raw']
            page.evaluate('window.__x2quota=false')
            page.locator('#modalConfirm').click()
            assert not page.locator('#modalOverlay').is_visible()
            after=x2_snapshot(page)
            assert after['scenarios']==before['scenarios']+1
            assert json.loads(after['raw'])['personalFinance']==json.loads(after['pf'])
            page.reload(wait_until='load')
            assert page.evaluate("S.personalFinance.scenarios.filter(s=>s.name==='Synthetic retry UI').length")==1
            # New declined attempt then cancel; another flow must not carry it.
            page.evaluate("""() => {window.alert=()=>{};window.__x2nativeSet=Storage.prototype.setItem;
              Storage.prototype.setItem=function(k,v){if(k===LSKEY && window.__x2quota)throw new DOMException('Synthetic quota refusal','QuotaExceededError');return window.__x2nativeSet.call(this,k,v)};
              navigateToScreen('finpes');window.JPWFin.ui.selectView('cenarios');} """)
            page.locator('[data-fs-new]').click();page.locator('#fsName').fill('Cancelled after refusal')
            page.evaluate('window.__x2quota=true');page.locator('#modalConfirm').click();page.locator('#modalCancel').click()
            page.evaluate("() => {window.__x2quota=false;S.nocoda.x2Later='UI cancellation';save();}")
            page.reload(wait_until='load')
            assert page.evaluate("S.personalFinance.scenarios.filter(s=>s.name==='Cancelled after refusal').length")==0
            assert page.evaluate("S.nocoda.x2Later==='UI cancellation'")
            assert not errors, errors
        finally:
            ctx.close()



X2_PF_ACTIONS = [{'name': 'income_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');",
  'action': "pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})"},
 {'name': 'income_update_name',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');",
  'action': "pfActUpdateIncomeField('2026-08', S.personalFinance.months['2026-08'].incomes[0].id, 'name', "
            "'Synthetic revised income')"},
 {'name': 'income_update_money',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');",
  'action': "pfActUpdateIncomeField('2026-08', S.personalFinance.months['2026-08'].incomes[0].id, "
            "'receivedAmount', 415000)"},
 {'name': 'income_status',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');\n"
           "if ((pfActUpdateIncomeField('2026-08', S.personalFinance.months['2026-08'].incomes[0].id, "
           "'receivedAmount', 415000)).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActSetIncomeStatus('2026-08', S.personalFinance.months['2026-08'].incomes[0].id, 'RECEBIDA')"},
 {'name': 'income_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');",
  'action': "pfActDeleteIncome('2026-08', S.personalFinance.months['2026-08'].incomes[0].id)"},
 {'name': 'month_materialize_edit_ghost',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-07', {name:'Synthetic recurring source',projectedAmount:420000})).ok "
           "!== true) throw new Error('PF fixture setup act failed');\n"
           "if ((pfActConfigureRecurrence('2026-07', S.personalFinance.months['2026-07'].incomes[0].id, "
           "{recorrente:true,amount:420000,startMonth:'2026-08',endMonth:null})).ok !== true) throw new "
           "Error('PF fixture setup act failed');",
  'action': "pfActEditGhost('2026-08', S.personalFinance.recurringIncome[0].id, 'receivedAmount', 415000)"},
 {'name': 'recurrence_off',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');\n"
           "if ((pfActConfigureRecurrence('2026-08', S.personalFinance.months['2026-08'].incomes[0].id, "
           "{recorrente:true,amount:420000,startMonth:'2026-08',endMonth:null})).ok !== true) throw new "
           "Error('PF fixture setup act failed');",
  'action': "pfActConfigureRecurrence('2026-08', S.personalFinance.months['2026-08'].incomes[0].id, "
            '{recorrente:false})'},
 {'name': 'recurrence_on',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');",
  'action': "pfActConfigureRecurrence('2026-08', S.personalFinance.months['2026-08'].incomes[0].id, "
            "{recorrente:true,amount:420000,startMonth:'2026-08',endMonth:null})"},
 {'name': 'expense_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');",
  'action': "pfActAddExpense('2026-08', {name:'Synthetic expense'})"},
 {'name': 'expense_update_name',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddExpense('2026-08', {name:'Synthetic expense'})).ok !== true) throw new Error('PF "
           "fixture setup act failed');",
  'action': "pfActUpdateExpenseField('2026-08', S.personalFinance.months['2026-08'].expenses[0].id, 'name', "
            "'Synthetic revised expense')"},
 {'name': 'expense_update_money',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddExpense('2026-08', {name:'Synthetic expense'})).ok !== true) throw new Error('PF "
           "fixture setup act failed');",
  'action': "pfActUpdateExpenseField('2026-08', S.personalFinance.months['2026-08'].expenses[0].id, "
            "'expectedAmount', 14000)"},
 {'name': 'expense_status',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddExpense('2026-08', {name:'Synthetic expense'})).ok !== true) throw new Error('PF "
           "fixture setup act failed');\n"
           "if ((pfActUpdateExpenseField('2026-08', S.personalFinance.months['2026-08'].expenses[0].id, "
           "'executedCash', 12000)).ok !== true) throw new Error('PF fixture setup act failed');\n"
           "if ((pfActUpdateExpenseField('2026-08', S.personalFinance.months['2026-08'].expenses[0].id, "
           "'executedCard', 0)).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActSetExpenseStatus('2026-08', S.personalFinance.months['2026-08'].expenses[0].id, 'PAGO')"},
 {'name': 'expense_installments',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddExpense('2026-08', {name:'Synthetic expense'})).ok !== true) throw new Error('PF "
           "fixture setup act failed');",
  'action': "pfActSetExpenseInstallments('2026-08', S.personalFinance.months['2026-08'].expenses[0].id, "
            '{total:6,paid:2})'},
 {'name': 'expense_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddExpense('2026-08', {name:'Synthetic expense'})).ok !== true) throw new Error('PF "
           "fixture setup act failed');",
  'action': "pfActDeleteExpense('2026-08', S.personalFinance.months['2026-08'].expenses[0].id)"},
 {'name': 'allocation_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');",
  'action': "pfActAddAllocation('2026-08', {label:'Synthetic allocation', amount:15000})"},
 {'name': 'allocation_update_label',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddAllocation('2026-08', {label:'Synthetic allocation', amount:15000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');",
  'action': "pfActUpdateAllocationField('2026-08', S.personalFinance.months['2026-08'].allocations[0].id, "
            "'label', 'Synthetic revised allocation')"},
 {'name': 'allocation_update_amount',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddAllocation('2026-08', {label:'Synthetic allocation', amount:15000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');",
  'action': "pfActUpdateAllocationField('2026-08', S.personalFinance.months['2026-08'].allocations[0].id, "
            "'amount', 18500)"},
 {'name': 'allocation_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddAllocation('2026-08', {label:'Synthetic allocation', amount:15000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');",
  'action': "pfActDeleteAllocation('2026-08', S.personalFinance.months['2026-08'].allocations[0].id)"},
 {'name': 'note_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');",
  'action': "pfActAddNote('2026-08', 'Synthetic pending note')"},
 {'name': 'note_status',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddNote('2026-08', 'Synthetic pending note')).ok !== true) throw new Error('PF fixture "
           "setup act failed');",
  'action': "pfActToggleNoteStatus('2026-08', S.personalFinance.months['2026-08'].notes[0].id)"},
 {'name': 'note_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddNote('2026-08', 'Synthetic pending note')).ok !== true) throw new Error('PF fixture "
           "setup act failed');",
  'action': "pfActDeleteNote('2026-08', S.personalFinance.months['2026-08'].notes[0].id)"},
 {'name': 'debt_snapshot',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddDebt({creditor:'Synthetic creditor',type:'EMPRESTIMO',description:'Synthetic "
           "contract',originalAmount:240000,installmentAmount:20000,installmentsTotal:12,startMonth:'2026-01',closedMonth:null})).ok "
           "!== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActRecordDebtSnapshot('2026-08', S.personalFinance.debts[0].id, {balance:160000, "
            'installmentsPaid:4})'},
 {'name': 'debt_snapshot_remove',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddDebt({creditor:'Synthetic creditor',type:'EMPRESTIMO',description:'Synthetic "
           "contract',originalAmount:240000,installmentAmount:20000,installmentsTotal:12,startMonth:'2026-01',closedMonth:null})).ok "
           "!== true) throw new Error('PF fixture setup act failed');\n"
           "if ((pfActRecordDebtSnapshot('2026-08', S.personalFinance.debts[0].id, {balance:160000, "
           "installmentsPaid:4})).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActRemoveDebtSnapshot('2026-08', S.personalFinance.debts[0].id)"},
 {'name': 'debt_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');",
  'action': "pfActAddDebt({creditor:'Synthetic creditor',type:'EMPRESTIMO',description:'Synthetic "
            "contract',originalAmount:240000,installmentAmount:20000,installmentsTotal:12,startMonth:'2026-01',closedMonth:null})"},
 {'name': 'debt_update',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddDebt({creditor:'Synthetic creditor',type:'EMPRESTIMO',description:'Synthetic "
           "contract',originalAmount:240000,installmentAmount:20000,installmentsTotal:12,startMonth:'2026-01',closedMonth:null})).ok "
           "!== true) throw new Error('PF fixture setup act failed');\n"
           "if ((pfActRecordDebtSnapshot('2026-08', S.personalFinance.debts[0].id, {balance:160000, "
           "installmentsPaid:4})).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActUpdateDebt(S.personalFinance.debts[0].id, {creditor:'Synthetic revised "
            "creditor',type:'EMPRESTIMO',description:'Synthetic revised "
            "contract',originalAmount:240000,installmentAmount:18000,installmentsTotal:12,startMonth:'2026-01',closedMonth:'2026-12'})"},
 {'name': 'debt_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddDebt({creditor:'Synthetic creditor',type:'EMPRESTIMO',description:'Synthetic "
           "contract',originalAmount:240000,installmentAmount:20000,installmentsTotal:12,startMonth:'2026-01',closedMonth:null})).ok "
           "!== true) throw new Error('PF fixture setup act failed');",
  'action': 'pfActDeleteDebt(S.personalFinance.debts[0].id)'},
 {'name': 'credit_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');",
  'action': "pfActAddCreditLine({institution:'Synthetic institution',instrument:'Synthetic "
            "card',type:'CARTAO',totalLimit:500000,used:50000})"},
 {'name': 'credit_update_text',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddCreditLine({institution:'Synthetic institution',instrument:'Synthetic "
           "card',type:'CARTAO',totalLimit:500000,used:50000})).ok !== true) throw new Error('PF fixture "
           "setup act failed');",
  'action': "pfActUpdateCreditLineField(S.personalFinance.creditLines[0].id, 'institution', 'Synthetic "
            "revised institution')"},
 {'name': 'credit_update_money',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddCreditLine({institution:'Synthetic institution',instrument:'Synthetic "
           "card',type:'CARTAO',totalLimit:500000,used:50000})).ok !== true) throw new Error('PF fixture "
           "setup act failed');",
  'action': "pfActUpdateCreditLineField(S.personalFinance.creditLines[0].id, 'used', 65000)"},
 {'name': 'credit_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddCreditLine({institution:'Synthetic institution',instrument:'Synthetic "
           "card',type:'CARTAO',totalLimit:500000,used:50000})).ok !== true) throw new Error('PF fixture "
           "setup act failed');",
  'action': 'pfActDeleteCreditLine(S.personalFinance.creditLines[0].id)'},
 {'name': 'scenario_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');",
  'action': "pfActAddScenario({name:'Synthetic base',kind:'BASE',horizon:'2027-03'})"},
 {'name': 'scenario_update',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddScenario({name:'Synthetic base',kind:'BASE',horizon:'2027-03'})).ok !== true) throw "
           "new Error('PF fixture setup act failed');",
  'action': "pfActUpdateScenarioMeta(S.personalFinance.scenarios[0].id, {name:'Synthetic revised "
            "scenario',kind:'PESSIMISTA',horizon:'2027-06'})"},
 {'name': 'scenario_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddScenario({name:'Synthetic base',kind:'BASE',horizon:'2027-03'})).ok !== true) throw "
           "new Error('PF fixture setup act failed');",
  'action': 'pfActDeleteScenario(S.personalFinance.scenarios[0].id)'},
 {'name': 'scenario_item_add',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddScenario({name:'Synthetic base',kind:'BASE',horizon:'2027-03'})).ok !== true) throw "
           "new Error('PF fixture setup act failed');",
  'action': "pfActAddScenarioItem(S.personalFinance.scenarios[0].id, 'incomes', {name:'Synthetic scenario "
            "income',amount:210000})"},
 {'name': 'scenario_item_update_name',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddScenario({name:'Synthetic base',kind:'BASE',horizon:'2027-03'})).ok !== true) throw "
           "new Error('PF fixture setup act failed');\n"
           "if ((pfActAddScenarioItem(S.personalFinance.scenarios[0].id, 'incomes', {name:'Synthetic "
           "scenario income',amount:210000})).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActUpdateScenarioItem(S.personalFinance.scenarios[0].id, 'incomes', "
            "S.personalFinance.scenarios[0].incomes[0].id, 'name', 'Synthetic revised scenario income')"},
 {'name': 'scenario_item_update_amount',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddScenario({name:'Synthetic base',kind:'BASE',horizon:'2027-03'})).ok !== true) throw "
           "new Error('PF fixture setup act failed');\n"
           "if ((pfActAddScenarioItem(S.personalFinance.scenarios[0].id, 'incomes', {name:'Synthetic "
           "scenario income',amount:210000})).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActUpdateScenarioItem(S.personalFinance.scenarios[0].id, 'incomes', "
            "S.personalFinance.scenarios[0].incomes[0].id, 'amount', 230000)"},
 {'name': 'scenario_item_delete',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddScenario({name:'Synthetic base',kind:'BASE',horizon:'2027-03'})).ok !== true) throw "
           "new Error('PF fixture setup act failed');\n"
           "if ((pfActAddScenarioItem(S.personalFinance.scenarios[0].id, 'incomes', {name:'Synthetic "
           "scenario income',amount:210000})).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActDeleteScenarioItem(S.personalFinance.scenarios[0].id, 'incomes', "
            'S.personalFinance.scenarios[0].incomes[0].id)'},
 {'name': 'scenario_from_month',
  'setup': 'S.personalFinance = structuredClone(DEFAULTS.personalFinance);\n'
           "if (save() !== true) throw new Error('PF fixture reset was not saved');\n"
           "if ((pfActAddIncome('2026-08', {name:'Synthetic income', projectedAmount:420000})).ok !== true) "
           "throw new Error('PF fixture setup act failed');\n"
           "if ((pfActAddExpense('2026-08', {name:'Synthetic expense'})).ok !== true) throw new Error('PF "
           "fixture setup act failed');\n"
           "if ((pfActUpdateExpenseField('2026-08', S.personalFinance.months['2026-08'].expenses[0].id, "
           "'expectedAmount', 14000)).ok !== true) throw new Error('PF fixture setup act failed');",
  'action': "pfActCreateScenarioFromMonth('2026-08', {name:'Synthetic copied "
            "scenario',kind:'BASE',horizon:'2027-03'})"}]

def run_x2_all_actions(browser,url,failures):
    ctx,page,errors=x2_boot(browser,url)
    try:
        for case in X2_PF_ACTIONS:
            try:
                page.evaluate('() => {'+case['setup']+'}')
                page.evaluate("() => {S.personalFinance.x2Unknown={preserved:[null,0]};save();window.__x2wholeBefore=structuredClone(S);window.__x2reference=S.personalFinance;}")
                before=x2_snapshot(page)
                control=page.evaluate(case['action'])
                control_after=x2_snapshot(page)
                assert control['ok'] is True and control_after['pf']!=before['pf'], 'positive control must perform an effective act'
                assert page.evaluate('S.personalFinance===window.__x2reference'), 'success invalidated live PF references'
                page.evaluate("() => {S=structuredClone(window.__x2wholeBefore);save();window.__x2quota=true;}")
                before=x2_snapshot(page)
                refused=page.evaluate(case['action'])
                rejected=x2_snapshot(page)
                page.evaluate('window.__x2quota=false')
                retried=page.evaluate(case['action'])
                after=x2_snapshot(page)
                x2_trace('act-'+case['name'],{'control':control['ok'],'refused':refused['ok'],
                         'pfRollback':before['pf']==rejected['pf'],'logRollback':before['log']==rejected['log'],
                         'diskUnchanged':before['raw']==rejected['raw'],'retry':retried['ok']})
                assert refused['ok'] is False and refused['persistido'] is False, 'refused act reported success'
                assert rejected['pf']==before['pf'] and rejected['log']==before['log'], 'refused act remained in PF/log'
                assert rejected['raw']==before['raw'], 'refused write changed storage'
                assert retried['ok'] is True and len(json.loads(after['log']))==len(json.loads(before['log']))+1, 'retry did not record exactly one act'
                assert json.loads(after['raw'])['personalFinance']==json.loads(after['pf']), 'memory differs from persisted act'
                assert page.evaluate('S.personalFinance.x2Unknown.preserved[0]===null && S.personalFinance.x2Unknown.preserved[1]===0'), 'unknown field changed'
            except Exception as exc:
                failures.append('X2 act '+case['name']+': '+type(exc).__name__+': '+(str(exc) or 'invariant failed'))
            finally:
                page.evaluate('window.__x2quota=false')
        assert not errors, errors
    finally:
        ctx.close()


def run_x2_defensive_outcomes(browser,url,failures):
    for value in ['undefined','null','0']:
        ctx,page,errors=x2_boot(browser,url)
        try:
            before=x2_snapshot(page)
            page.evaluate('save=()=>'+value)
            first=page.evaluate("pfActAddScenario({name:'Unknown return',kind:'BASE'})")
            attempt=x2_snapshot(page)
            second=page.evaluate("pfActAddScenario({name:'Unknown return',kind:'BASE'})")
            after=x2_snapshot(page)
            assert first['ok'] is False and first['persistido'] is None and attempt['unknown']
            assert attempt['scenarios']==before['scenarios']+1 and attempt['raw']==before['raw']
            assert second['persistido'] is None and attempt==after, 'UNKNOWN allowed blind retry'
            x2_trace('nonboolean-'+value,{'first':first,'second':second,'noRetry':attempt==after})
        finally:
            ctx.close()
    ctx,page,errors=x2_boot(browser,url)
    try:
        before=x2_snapshot(page)
        result=page.evaluate("""() => {
          const original=structuredClone;
          try {
            window.structuredClone=()=>{throw new Error('Synthetic clone refusal')};
            return pfActAddScenario({name:'Clone refused',kind:'BASE'});
          } finally { window.structuredClone=original; }
        }""")
        assert result['ok'] is False and result['persistido'] is False
        assert x2_snapshot(page)==before, 'clone refusal mutated state or called save'
        x2_trace('clone-refusal',{'result':result,'unchanged':True})
    finally:
        ctx.close()
    for written in [False,True]:
        ctx,page,errors=x2_boot(browser,url)
        try:
            before=x2_snapshot(page)
            page.evaluate("""written=>{save=function(){if(written)window.__x2originalSave();
              throw new Error('Synthetic escaped save exception');};
              navigateToScreen('finpes');JPWFin.ui.selectView('cenarios');} """,written)
            page.locator('[data-fs-new]').click()
            page.locator('#fsName').fill('Unknown UI')
            page.locator('#modalConfirm').click()
            first=x2_snapshot(page)
            assert page.locator('#modalOverlay').is_visible()
            assert page.locator('#fsName').input_value()=='Unknown UI'
            assert 'não repita' in page.evaluate('window.__x2alerts.at(-1)').lower()
            page.locator('#modalConfirm').click()
            assert x2_snapshot(page)==first and first['unknown'], 'UI UNKNOWN retried mutation'
            page.reload(wait_until='load')
            assert page.evaluate('S.personalFinance.scenarios.length')==before['scenarios']+int(written)
            assert not errors, errors
            x2_trace('unknown-ui-'+str(written),{'noRetry':True,'reloadCount':before['scenarios']+int(written)})
        finally:
            ctx.close()


def run_x2_persistence(browser,url,failures):
    for name,fn in [('retry',run_x2_refusal_retry),('refusal matrix',run_x2_refusal_matrix),
                    ('unknown/prewrite',run_x2_unknown_and_prewrite),('UI',run_x2_ui),
                    ('all PF acts',run_x2_all_actions),('defensive outcomes',run_x2_defensive_outcomes)]:
        try:
            fn(browser,url,failures)
        except Exception as exc:
            # Preserve failed assertions even when they have no message. Do not
            # use executar's old splitlines[-1] collector for these new cases.
            failures.append('X2 '+name+': '+type(exc).__name__+': '+(str(exc) or 'invariant failed'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persistence-only", action="store_true", help="Executar somente regressões X2-01")
    args = parser.parse_args()
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            if not args.persistence_only:
                executar("A crud/formulas", lambda: run_a_crud_e_formulas(browser, url, falhas), falhas)
                executar("B copia bloqueada", lambda: run_b_copia_bloqueia_fonte_incompleta(browser, url, falhas), falhas)
                executar("B copia/independencia", lambda: run_b_copia_correta_e_independencia(browser, url, falhas), falhas)
                executar("B virtual", lambda: run_b_virtual_nao_e_baseline(browser, url, falhas), falhas)
                executar("AB write gate", lambda: run_ab_write_gate(browser, url, falhas), falhas)
                executar("CD ui fluxo", lambda: run_cd_ui_fluxo_real(browser, url, falhas), falhas)
                executar("CD cascata/copia ui", lambda: run_cd_cascata_visual_e_copia_ui(browser, url, falhas), falhas)
                executar("CD sentinela", lambda: run_cd_sentinela_visual(browser, url, falhas), falhas)
                executar("CD sentinela leitura", lambda: run_cd_sentinela_leitura(browser, url, falhas), falhas)
            run_x2_persistence(browser, url, falhas)
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
