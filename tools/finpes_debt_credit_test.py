#!/usr/bin/env python3
"""Dividas & Credito (PF-03) — suite focal N3.

Identidade temporal != observacao mensal. Estado atual jamais reinterpreta o
passado; dado antigo jamais vira fato atual. Cada caso acusa pela PROPRIEDADE.
Fixtures 100% sinteticas. Numero certo pelo motivo errado e falha.
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
        "() => typeof S === 'object' && typeof pfActAddDebt === 'function'")
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function(
            "() => typeof S === 'object' && typeof pfActAddDebt === 'function'")
    page.wait_for_timeout(350)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return context, page, erros


def executar(nome, fn, falhas):
    try:
        fn()
    except Exception as e:
        falhas.append(f"{nome}: EXCECAO no harness (sonda sem guarda?): {str(e).splitlines()[-1][:160]}")


# ---------- BLOCO A/B ----------

def run_ab_cenario_canonico_temporal(browser, url, falhas):
    """Divida JAN->OUT com snapshots AGO/SET/OUT; nova em DEZ. Populacoes e
    coberturas historicas exatas — quitacao nao reescreve o passado."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        const nb = pfActAddDebt({creditor:'Banco Sigma', type:'EMPRESTIMO', description:'24x',
            originalAmount:2208000, installmentAmount:92000, installmentsTotal:24,
            startMonth:'2026-01', closedMonth:null});
        const id = S.personalFinance.debts[0].id;
        pfActRecordDebtSnapshot('2026-08', id, {balance:1200000, installmentsPaid:16});
        pfActRecordDebtSnapshot('2026-09', id, {balance:1050000, installmentsPaid:17});
        pfActRecordDebtSnapshot('2026-10', id, {balance:0, installmentsPaid:18});
        // encerra em OUT (correcao de contrato valida: nenhum snapshot orfao)
        const d = S.personalFinance.debts[0];
        const quita = pfActUpdateDebt(id, {creditor:d.creditor, type:d.type, description:d.description,
            originalAmount:d.originalAmount, installmentAmount:d.installmentAmount,
            installmentsTotal:d.installmentsTotal, startMonth:d.startMonth, closedMonth:'2026-10'});
        // nova divida em DEZ
        pfActAddDebt({creditor:'Loja Epsilon', type:'CREDIARIO', description:'10x',
            originalAmount:450000, installmentAmount:45000, installmentsTotal:10,
            startMonth:'2026-12', closedMonth:null});
        const cov = k => pfDebtCoverage(k);
        return { quitaOk: quita.ok,
                 ago: {cov: cov('2026-08'), total: pfKnownDebtTotal('2026-08')},
                 out: {cov: cov('2026-10'), total: pfKnownDebtTotal('2026-10')},
                 nov: {cov: cov('2026-11'), total: pfKnownDebtTotal('2026-11')},
                 dez: {cov: cov('2026-12'), total: pfKnownDebtTotal('2026-12')},
                 semSaldoGlobal: !('balance' in S.personalFinance.debts[0]),
                 restantes: pfRemainingInstallments(S.personalFinance.debts[0], pfDebtSnapshotIn('2026-08', id)) };
    }""")
    if not r["quitaOk"]:
        falhas.append("AB: encerrar em OUT (sem orfaos) deveria ser aceito")
    if r["ago"] != {"cov":{"observadas":1,"relevantes":1,"completa":True},"total":1200000}:
        falhas.append(f"AB: AGO deveria ter 1/1 e 1.200000 — quitacao posterior NAO reescreve o passado: {r['ago']}")
    if r["out"] != {"cov":{"observadas":1,"relevantes":1,"completa":True},"total":0}:
        falhas.append(f"AB: OUT deveria ter 1/1 e 0: {r['out']}")
    if r["nov"] != {"cov":{"observadas":0,"relevantes":0,"completa":True},"total":0}:
        falhas.append(f"AB: NOV sem divida relevante = zero DEMONSTRADO: {r['nov']}")
    if r["dez"] != {"cov":{"observadas":0,"relevantes":1,"completa":False},"total":0}:
        falhas.append(f"AB: DEZ deveria ter Loja relevante sem snapshot (0/1): {r['dez']}")
    if not r["semSaldoGlobal"]:
        falhas.append("AB: debt.balance GLOBAL apareceu — proibido pelo schema congelado")
    if r["restantes"] != 8:
        falhas.append(f"AB: restantes derivado deveria ser 24-16=8: {r['restantes']}")
    ctx.close()


def run_ab_snapshot_guardas(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        pfActAddDebt({creditor:'Banco Tau', type:'CARTAO', description:'',
            originalAmount:null, installmentAmount:null, installmentsTotal:null,
            startMonth:'2026-06', closedMonth:'2026-09'});
        const id = S.personalFinance.debts[0].id;
        const foraAntes = pfActRecordDebtSnapshot('2026-05', id, {balance:1000});
        const foraDepois = pfActRecordDebtSnapshot('2026-10', id, {balance:1000});
        const semSaldo = pfActRecordDebtSnapshot('2026-07', id, {balance:null});
        const negativo = pfActRecordDebtSnapshot('2026-07', id, {balance:-5});
        const paidSemContrato = pfActRecordDebtSnapshot('2026-07', id, {balance:1000, installmentsPaid:3});
        const ok = pfActRecordDebtSnapshot('2026-07', id, {balance:98000});
        const corrige = pfActRecordDebtSnapshot('2026-07', id, {balance:97000});
        const m = S.personalFinance.months['2026-07'];
        return { foraAntesOk: foraAntes.ok, foraDepoisOk: foraDepois.ok,
                 semSaldoOk: semSaldo.ok, negativoOk: negativo.ok,
                 paidSemContratoOk: paidSemContrato.ok,
                 okOk: ok.ok && corrige.ok,
                 snapshots: m.debtSnapshots.length,
                 saldoFinal: m.debtSnapshots[0].balance,
                 paidFinal: m.debtSnapshots[0].installmentsPaid };
    }""")
    for campo, msg in [("foraAntesOk","snapshot antes da vigencia"),("foraDepoisOk","snapshot depois do encerramento"),
                       ("semSaldoOk","snapshot sem saldo"),("negativoOk","saldo negativo"),
                       ("paidSemContratoOk","parcelas pagas em divida sem contrato parcelado")]:
        if r[campo] is not False:
            falhas.append(f"AB: {msg} deveria ser recusado")
    if not r["okOk"] or r["snapshots"] != 1 or r["saldoFinal"] != 97000:
        falhas.append(f"AB: corrigir no mesmo mes deveria SUBSTITUIR (1 snapshot, 97000): {r}")
    if r["paidFinal"] is not None:
        falhas.append("AB: correcao sem installmentsPaid deveria registrar null")
    ctx.close()


def run_ab_materializacao_canonica(browser, url, falhas):
    """Snapshot em mes virtual materializa UMA vez pelo materializador canonico
    — estampando receitas recorrentes como qualquer primeiro ato."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        pfMutate('seed_regra', pf => { pf.recurringIncome.push({id:'pfr_dc', name:'Salario', amount:1200000,
            periodicity:'MENSAL', startMonth:'2026-01', endMonth:null, active:true}); return {}; });
        pfActAddDebt({creditor:'Banco Sigma', type:'EMPRESTIMO', description:'',
            originalAmount:null, installmentAmount:null, installmentsTotal:null,
            startMonth:'2026-01', closedMonth:null});
        const id = S.personalFinance.debts[0].id;
        const antes = Object.keys(S.personalFinance.months).length;
        pfActRecordDebtSnapshot('2026-08', id, {balance:500000});
        const m = S.personalFinance.months['2026-08'];
        return { antes, meses: Object.keys(S.personalFinance.months).length,
                 estampou: m.incomes.length===1 && m.incomes[0].ruleId==='pfr_dc',
                 temSnapshot: m.debtSnapshots.length===1 };
    }""")
    if r["antes"] != 0 or r["meses"] != 1:
        falhas.append(f"AB: materializacao deveria ocorrer exatamente uma vez: {r}")
    if not r["estampou"]:
        falhas.append("AB: PF-03 usou materializador NAO canonico — receita recorrente nao foi estampada")
    if not r["temSnapshot"]:
        falhas.append("AB: snapshot nao gravado")
    ctx.close()


def run_ab_integridade_contrato_vs_historia(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        pfActAddDebt({creditor:'Banco Sigma', type:'EMPRESTIMO', description:'',
            originalAmount:null, installmentAmount:92000, installmentsTotal:24,
            startMonth:'2026-01', closedMonth:null});
        const id = S.personalFinance.debts[0].id;
        pfActRecordDebtSnapshot('2026-08', id, {balance:1200000, installmentsPaid:16});
        const base = () => { const d=S.personalFinance.debts[0]; return {creditor:d.creditor, type:d.type,
            description:d.description, originalAmount:d.originalAmount, installmentAmount:d.installmentAmount,
            installmentsTotal:d.installmentsTotal, startMonth:d.startMonth, closedMonth:d.closedMonth}; };
        const startOrfa  = pfActUpdateDebt(id, {...base(), startMonth:'2026-09'});
        const closedOrfa = pfActUpdateDebt(id, {...base(), closedMonth:'2026-07'});
        const totalMenor = pfActUpdateDebt(id, {...base(), installmentsTotal:15});
        const totalNull  = pfActUpdateDebt(id, {...base(), installmentsTotal:null});
        const excluir    = pfActDeleteDebt(id);
        const aindaExiste = S.personalFinance.debts.length===1;
        const valida     = aindaExiste ? pfActUpdateDebt(id, {...base(), closedMonth:'2026-10'}) : {ok:false};
        const d = S.personalFinance.debts[0] || null;
        return { startOrfa: {ok:startOrfa.ok, erro:startOrfa.erro},
                 closedOrfa: {ok:closedOrfa.ok, erro:closedOrfa.erro},
                 totalMenor: {ok:totalMenor.ok, erro:totalMenor.erro},
                 totalNull: {ok:totalNull.ok, erro:totalNull.erro},
                 excluirOk: excluir.ok, excluirErro: excluir.erro,
                 validaOk: valida.ok,
                 contratoIntacto: !!d && d.startMonth==='2026-01' && d.installmentsTotal===24 };
    }""")
    if r["startOrfa"]["ok"] is not False or "2026-08" not in r["startOrfa"]["erro"]:
        falhas.append(f"AB: mover inicio para depois do snapshot deveria bloquear NOMEANDO 2026-08: {r['startOrfa']}")
    if r["closedOrfa"]["ok"] is not False or "2026-08" not in r["closedOrfa"]["erro"]:
        falhas.append(f"AB: encerrar antes do snapshot deveria bloquear nomeando o conflito: {r['closedOrfa']}")
    if r["totalMenor"]["ok"] is not False or "16" not in r["totalMenor"]["erro"]:
        falhas.append(f"AB: reduzir total abaixo das 16 pagas observadas deveria bloquear: {r['totalMenor']}")
    if r["totalNull"]["ok"] is not False:
        falhas.append("AB: retirar o parcelamento com historico de pagas deveria bloquear")
    if r["excluirOk"] is not False or "2026-08" not in (r["excluirErro"] or ""):
        falhas.append(f"AB: excluir divida com snapshot deveria bloquear nomeando os meses: {r['excluirErro']}")
    if not r["validaOk"] or not r["contratoIntacto"]:
        falhas.append(f"AB: edicao valida (closed=OUT) deveria passar e as bloqueadas nao podem ter alterado nada: {r}")
    ctx.close()


def run_ab_cobertura_parcial_sem_carry_forward(browser, url, falhas):
    """Divida relevante sem snapshot no mes: cobertura parcial, e o total
    conhecido NAO herda a ultima observacao — dado antigo nao vira fato atual."""
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        pfActAddDebt({creditor:'A', type:'EMPRESTIMO', description:'', originalAmount:null,
            installmentAmount:null, installmentsTotal:null, startMonth:'2026-01', closedMonth:null});
        pfActAddDebt({creditor:'B', type:'CARTAO', description:'', originalAmount:null,
            installmentAmount:null, installmentsTotal:null, startMonth:'2026-01', closedMonth:null});
        const [a,b] = S.personalFinance.debts.map(d=>d.id);
        pfActRecordDebtSnapshot('2026-08', a, {balance:1200000});
        pfActRecordDebtSnapshot('2026-08', b, {balance:500000});
        pfActRecordDebtSnapshot('2026-09', a, {balance:1000000});
        // SET: B relevante, SEM snapshot — mas TEM observacao antiga (AGO)
        const ultima = pfLastObservation(b, '2026-09');
        return { covSet: pfDebtCoverage('2026-09'), totalSet: pfKnownDebtTotal('2026-09'),
                 ultimaDatada: ultima && ultima.monthKey };
    }""")
    if r["covSet"] != {"observadas":1,"relevantes":2,"completa":False}:
        falhas.append(f"AB: SET deveria ter cobertura 1/2: {r['covSet']}")
    if r["totalSet"] != 1000000:
        falhas.append(f"AB: total conhecido de SET deveria ser 1.000000 SEM carry-forward da observacao de AGO; veio {r['totalSet']}")
    if r["ultimaDatada"] != "2026-08":
        falhas.append(f"AB: ultima observacao datada deveria apontar 2026-08 (info secundaria): {r['ultimaDatada']}")
    ctx.close()


def run_ab_sem_historia_pode_excluir(browser, url, falhas):
    ctx, page, erros = boot(browser, url)
    r = page.evaluate("""() => {
        pfActAddDebt({creditor:'Temporaria', type:'OUTRO', description:'',
            originalAmount:null, installmentAmount:null, installmentsTotal:null,
            startMonth:'2026-01', closedMonth:null});
        const id = S.personalFinance.debts[0].id;
        const del = pfActDeleteDebt(id);
        return { ok: del.ok, restam: S.personalFinance.debts.length };
    }""")
    if not r["ok"] or r["restam"] != 0:
        falhas.append(f"AB: divida SEM historia deveria poder ser excluida deliberadamente: {r}")
    ctx.close()


def run_ab_write_gate(browser, url, falhas):
    mut = """
      S.personalFinance = { schemaVersion:1, moneyUnit:'XX_UNIT', months:{},
        recurringIncome:[], debts:[{id:'pfd_x', creditor:'X', type:'OUTRO', description:'',
          originalAmount:null, installmentAmount:null, installmentsTotal:null,
          startMonth:'2026-01', closedMonth:null}], creditLines:[], scenarios:[] };
    """
    ctx, page, erros = boot(browser, url, mutacao_js=mut)
    r = page.evaluate("""() => {
        const antes = JSON.stringify(S.personalFinance);
        const acts = [
          pfActAddDebt({creditor:'Y', type:'OUTRO', startMonth:'2026-01'}),
          pfActUpdateDebt('pfd_x', {creditor:'Z', type:'OUTRO', startMonth:'2026-01'}),
          pfActDeleteDebt('pfd_x'),
          pfActRecordDebtSnapshot('2026-05', 'pfd_x', {balance:1}),
        ];
        return { bloqueados: acts.every(a=>a.ok===false && a.erro==='READ_ONLY_UNSUPPORTED_MONEY_UNIT'),
                 intacto: antes === JSON.stringify(S.personalFinance) };
    }""")
    if not r["bloqueados"]:
        falhas.append("AB: unidade desconhecida deveria bloquear TODOS os atos de divida")
    if not r["intacto"]:
        falhas.append("AB: bloqueio mutou o agregado")
    ctx.close()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            executar("AB cenario temporal", lambda: run_ab_cenario_canonico_temporal(browser, url, falhas), falhas)
            executar("AB snapshot guardas", lambda: run_ab_snapshot_guardas(browser, url, falhas), falhas)
            executar("AB materializacao canonica", lambda: run_ab_materializacao_canonica(browser, url, falhas), falhas)
            executar("AB integridade contrato", lambda: run_ab_integridade_contrato_vs_historia(browser, url, falhas), falhas)
            executar("AB cobertura parcial", lambda: run_ab_cobertura_parcial_sem_carry_forward(browser, url, falhas), falhas)
            executar("AB excluir sem historia", lambda: run_ab_sem_historia_pode_excluir(browser, url, falhas), falhas)
            executar("AB write gate", lambda: run_ab_write_gate(browser, url, falhas), falhas)
            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES DEBT CREDIT TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
