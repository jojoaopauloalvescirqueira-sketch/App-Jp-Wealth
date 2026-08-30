#!/usr/bin/env python3
"""Alladin ALD-03 S1 — CASH LEDGER: o primeiro fato economico do dominio.

Mesmo contrato de harness do alladin_unit_test (decisao humana de 2026-08-20):
Chromium ISOLADO — sem app, sem DOM de producao, sem estado real, sem network.
A pagina e about:blank, toda requisicao e abortada e contada, e o unico codigo
injetado e um prelude de stubs seguido do MODULO SOB TESTE lido do disco.

O que esta suite prova (L1-L14):
  L1  DEPOSIT/WITHDRAWAL: efeito e saldo derivado
  L2  TRANSFER: um registro, dois efeitos, patrimonio global INALTERADO
      — o caso canonico "Internal Transfer Is Not Contribution"
  L3  flowScope e PERIMETRO, nao direcao; persistido e validado contra o evento
  L4  REVERSAL: original preservado, status REVERSED, net zero
  L5  as cinco proibicoes do reversal
  L6  campos economicos nunca sao informados pelo chamador na reversao
  L7  recusas de referencia, moeda e valor
  L8  dedupeKey: duplicidade de LANCAMENTO e fail-closed (nao aviso)
  L9  CashAccount inativa: lancamento novo recusa, historico e reversao seguem
  L10 qualidade BLOQUEANTE: saldo indisponivel, jamais parcial
  L11 ordem economica (effectiveAt, recordedAt, transactionId), nunca a do array
  L12 write gate e atomicidade: ato recusado nao deixa vestigio
  L13 DRAFT nao existe neste ciclo
  L14 nenhum saldo persistido — ALD-I27
  L15 conta referenciada: moeda/conta-mae imutaveis, mas encerrar e reverter seguem

ALD-03 S2 (L16-L29): a dupla atomica papel<->caixa.
  L16 BUY: UM registro, duas pernas; cashDelta = -(amount+fees+taxes); SEM flowScope
  L17 exemplo canonico da spec: DEPOSIT 10000 -> BUY 3000/10 -> saldo 6990
  L18 SELL: liquido positivo, zero e NEGATIVO todos representaveis
  L19 reversal de trade: par soma zero, quantity byte-igual, proibidos completos
  L20 recusas: instrumento, moeda, dedupe, overflow na escrita (MC-S2-2)
  L21 quantity: forma canonica estrita — uma grafia por valor
  L22 flowScope declarado em trade: RECUSA por presenca (undefined incluso); adulterado: ilegivel
  L23 instrumentFamily congela na primeira referencia economica
  L24 reversal com amount adulterado pos-escrita -> BLOCKING (MC-S2-1)
  L25 reversedEventType adulterado -> BLOCKING
  L26 trade-reversal com quantity/fees/taxes/instrumentId divergentes -> BLOCKING
  L27 flowScope do par divergente (presenca E valor, nos dois sentidos) -> BLOCKING
  L28 refs de caixa do par divergentes -> BLOCKING
  L29 acumulador do saldo nao atravessa regiao insegura (guarda POR PASSO)
"""
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODULO = ROOT / "src/js/10-domain/13-alladin.js"

PRELUDE = """
window.__stub = { saves: 0, saveResult: true, logs: [] };
var S = { alladin: { schemaVersion: 4, reportingCurrency: 'BRL',
                     instruments: [], assets: [], accounts: [], cashAccounts: [],
                     transactions: [] },
          dataGovernance: { changeLog: [] } };
function save(){ window.__stub.saves += 1; return window.__stub.saveResult; }
const DG_CHANGELOG_MAX = 400;
function dgLogChange(entity, action, recordId, label){
  const e = { entity: entity, action: action, recordId: recordId, label: label };
  window.__stub.logs.push(e);
  S.dataGovernance.changeLog.push(e);
  if(S.dataGovernance.changeLog.length > DG_CHANGELOG_MAX){
    S.dataGovernance.changeLog = S.dataGovernance.changeLog.slice(-DG_CHANGELOG_MAX);
  }
}
// Fixture: duas corretoras, tres contas de caixa (duas BRL, uma USD).
function fixture(){
  S.alladin = { schemaVersion: 4, reportingCurrency: 'BRL', instruments: [], assets: [],
                accounts: [], cashAccounts: [], transactions: [] };
  S.dataGovernance.changeLog = [];
  window.__stub.saves = 0; window.__stub.saveResult = true;
  const c = JPWAlladin.cadastro;
  const xp  = c.addAccount({ name:'XP',  institution:'XP',  accountType:'BROKERAGE' }).recordId;
  const btg = c.addAccount({ name:'BTG', institution:'BTG', accountType:'BROKERAGE' }).recordId;
  return {
    xp, btg,
    caixaXP:  c.addCashAccount({ accountId: xp,  currency:'BRL' }).recordId,
    caixaBTG: c.addCashAccount({ accountId: btg, currency:'BRL' }).recordId,
    caixaUSD: c.addCashAccount({ accountId: xp,  currency:'USD' }).recordId,
    petr4:   c.addInstrument({ name:'Petrobras PN', symbol:'PETR4', currency:'BRL',
                               instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL' }).recordId,
    aaplUsd: c.addInstrument({ name:'Apple', symbol:'AAPL', currency:'USD',
                               instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL' }).recordId,
  };
}
"""


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:  # crash jamais engole as acusacoes ja acumuladas
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def main() -> int:
    falhas: list[str] = []
    bloqueadas = {"n": 0}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.on("pageerror", lambda e: falhas.append(f"pageerror: {e}"))

        def abortar(route):
            bloqueadas["n"] += 1
            route.abort()

        page.route("**/*", abortar)
        page.goto("about:blank")
        page.add_script_tag(content=PRELUDE)
        page.add_script_tag(content=MODULO.read_text(encoding="utf-8"))
        ev = page.evaluate

        # ---- L1: deposito e saque -------------------------------------------
        def l1():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const dep = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP,
                amount:100000, effectiveAt:'2026-01-10'});
              const s1 = R.saldoDeCaixa(f.caixaXP);
              const saq = L.addTransaction({eventType:'WITHDRAWAL', cashAccountId:f.caixaXP,
                amount:30000, effectiveAt:'2026-01-11'});
              const s2 = R.saldoDeCaixa(f.caixaXP);
              const rec = R.transactions().find(t => t.transactionId === dep.recordId);
              return { depOk:dep.ok && dep.persistido, saqOk:saq.ok,
                       s1:s1.amount, s1ok:s1.available, s2:s2.amount, moeda:s2.currency,
                       status:rec.status, temRecordedAt: typeof rec.recordedAt === 'string',
                       semSaldoNaConta: !('balance' in R.cashAccounts()[0]) };
            }""")
            if not r["depOk"] or not r["saqOk"]:
                falhas.append(f"L1: lancamento recusado ({r})")
            if r["s1"] != 100000 or r["s2"] != 70000:
                falhas.append(f"L1: saldo derivado divergente ({r['s1']}, {r['s2']})")
            if r["moeda"] != "BRL" or not r["s1ok"]:
                falhas.append(f"L1: moeda/disponibilidade divergentes ({r})")
            if r["status"] != "POSTED" or not r["temRecordedAt"]:
                falhas.append(f"L1: registro nasce fora do contrato ({r})")
            if not r["semSaldoNaConta"]:
                falhas.append("L1/ALD-I27: CashAccount ganhou campo de saldo")
        executar(falhas, "L1", l1)

        # ---- L2: transferencia NAO e aporte (caso canonico) ------------------
        def l2():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const antes = R.saldoDeCaixa(f.caixaXP).amount + R.saldoDeCaixa(f.caixaBTG).amount;
              const tr = L.addTransaction({eventType:'TRANSFER', sourceCashAccountId:f.caixaXP,
                destinationCashAccountId:f.caixaBTG, amount:40000, effectiveAt:'2026-01-12'});
              const depois = R.saldoDeCaixa(f.caixaXP).amount + R.saldoDeCaixa(f.caixaBTG).amount;
              const rec = R.transactions().find(t => t.transactionId === tr.recordId);
              return { ok:tr.ok, origem:R.saldoDeCaixa(f.caixaXP).amount,
                       destino:R.saldoDeCaixa(f.caixaBTG).amount,
                       antes, depois, flowScope:rec.flowScope,
                       registros: S.alladin.transactions.length };
            }""")
            if not r["ok"] or r["origem"] != 60000 or r["destino"] != 40000:
                falhas.append(f"L2: efeitos da transferencia divergentes ({r})")
            if r["antes"] != r["depois"]:
                falhas.append(f"L2 CANONICO: transferencia interna ALTEROU o patrimonio global "
                              f"({r['antes']} -> {r['depois']}) — seria contabilizada como aporte")
            if r["flowScope"] != "INTERNAL":
                falhas.append(f"L2: transferencia deveria ser INTERNAL ({r['flowScope']})")
            if r["registros"] != 2:
                falhas.append(f"L2: um fato economico deveria ser UM registro ({r['registros']})")
        executar(falhas, "L2", l2)

        # ---- L3: flowScope e perimetro, e e persistido -----------------------
        def l3():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'});
              const w = L.addTransaction({eventType:'WITHDRAWAL', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-01-11'});
              const t = L.addTransaction({eventType:'TRANSFER', sourceCashAccountId:f.caixaXP,
                destinationCashAccountId:f.caixaBTG, amount:100, effectiveAt:'2026-01-12'});
              const de = (id) => R.transactions().find(x => x.transactionId === id);
              // persistido no disco, nao inferido na leitura
              const noAgregado = S.alladin.transactions.every(x => typeof x.flowScope === 'string');
              const escopos = { dep:de(d.recordId).flowScope, saq:de(w.recordId).flowScope,
                                tr:de(t.recordId).flowScope };
              // SO DEPOIS de ler: registro incoerente e DADO INVALIDO, nunca
              // corrigido em silencio pela leitura.
              S.alladin.transactions[0].flowScope = 'INTERNAL';
              const saldo = R.saldoDeCaixa(f.caixaXP);
              return { ...escopos, noAgregado,
                       incoerenteBloqueia: saldo.available === false && saldo.quality === 'BLOCKING' };
            }""")
            if [r["dep"], r["saq"], r["tr"]] != ["EXTERNAL", "EXTERNAL", "INTERNAL"]:
                falhas.append(f"L3: flowScope divergente da tabela do perimetro ({r})")
            if not r["noAgregado"]:
                falhas.append("L3: flowScope nao foi persistido no agregado")
            if not r["incoerenteBloqueia"]:
                falhas.append("L3: flowScope incoerente com o evento foi ACEITO — deveria ser dado invalido")
        executar(falhas, "L3", l3)

        # ---- L4: reversal preserva o original e zera o efeito ----------------
        def l4():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const dep = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP,
                amount:50000, effectiveAt:'2026-01-10'});
              const antes = JSON.stringify(S.alladin.transactions[0]);
              const rev = L.reverseTransaction(dep.recordId, {effectiveAt:'2026-02-01', note:'estorno'});
              const orig = R.transactions().find(t => t.transactionId === dep.recordId);
              const nova = R.transactions().find(t => t.transactionId === rev.recordId);
              const depoisJson = JSON.stringify(S.alladin.transactions.find(t=>t.transactionId===dep.recordId));
              return { ok:rev.ok, saldo:R.saldoDeCaixa(f.caixaXP).amount,
                       statusOriginal:orig.status,
                       economicoIntacto: antes.replace('"POSTED"','"REVERSED"') === depoisJson,
                       revAmount:nova.amount, revMoeda:nova.currency, revFlow:nova.flowScope,
                       revRef:nova.reversalOf, revEvento:nova.eventType,
                       revEffective:nova.effectiveAt, origEffective:orig.effectiveAt,
                       registros:S.alladin.transactions.length };
            }""")
            if not r["ok"] or r["saldo"] != 0:
                falhas.append(f"L4: original + reversal deveriam somar zero ({r['saldo']})")
            if r["statusOriginal"] != "REVERSED":
                falhas.append(f"L4: lifecycle do original nao mudou ({r['statusOriginal']})")
            if not r["economicoIntacto"]:
                falhas.append("L4: a reversao ALTEROU campo economico do original")
            if r["revAmount"] != 50000 or r["revMoeda"] != "BRL" or r["revFlow"] != "EXTERNAL":
                falhas.append(f"L4: reversal nao copiou os valores economicos ({r})")
            if r["revRef"] is None or r["revEvento"] != "REVERSAL":
                falhas.append(f"L4: linkage do reversal ausente ({r})")
            if r["revEffective"] == r["origEffective"]:
                falhas.append("L4: a reversao herdou a data do original — e fato novo, com data propria")
            if r["registros"] != 2:
                falhas.append(f"L4: a reversao deveria acrescentar UM registro ({r['registros']})")
        executar(falhas, "L4", l4)

        # ---- L5: as proibicoes do reversal -----------------------------------
        def l5():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const dep = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'});
              const rev = L.reverseTransaction(dep.recordId, {effectiveAt:'2026-02-01'});
              const outra = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:2000, effectiveAt:'2026-01-15'});
              const antes = JSON.stringify(S.alladin.transactions);
              const out = {
                deReversal: L.reverseTransaction(rev.recordId, {effectiveAt:'2026-03-01'}).erro,
                duplicado:  L.reverseTransaction(dep.recordId, {effectiveAt:'2026-03-01'}).erro,
                inexistente:L.reverseTransaction('aldtx_nao_existe', {effectiveAt:'2026-03-01'}).erro,
                // numa transacao ainda NAO revertida, senao a guarda de duplicidade
                // dispara antes e o caso nao provaria a validacao de data
                semData:    L.reverseTransaction(outra.recordId, {}).erro,
                dataInvalida:L.reverseTransaction(outra.recordId, {effectiveAt:'01/02/2026'}).erro,
              };
              out.intacto = JSON.stringify(S.alladin.transactions) === antes;
              return out;
            }""")
            esperado = {"deReversal": "ALD_REVERSAL_DE_REVERSAL", "duplicado": "ALD_REVERSAL_JA_EXISTE",
                        "inexistente": "ALD_REGISTRO_NAO_ENCONTRADO",
                        "semData": "ALD_EFFECTIVE_AT_INVALIDA", "dataInvalida": "ALD_EFFECTIVE_AT_INVALIDA"}
            for chave, err in esperado.items():
                if r[chave] != err:
                    falhas.append(f"L5 '{chave}': esperado {err}, veio {r[chave]!r}")
            if not r["intacto"]:
                falhas.append("L5: uma reversao recusada mutou o ledger")
        executar(falhas, "L5", l5)

        # ---- L6: campos economicos nunca vem do chamador ---------------------
        def l6():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const dep = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'});
              const out = {};
              for(const campo of ['amount','currency','flowScope','eventType','cashAccountId',
                                  'sourceCashAccountId','destinationCashAccountId']){
                const d = {effectiveAt:'2026-02-01'}; d[campo] = 'x';
                out[campo] = L.reverseTransaction(dep.recordId, d).erro;
              }
              return out;
            }""")
            for campo, err in r.items():
                if err != "ALD_CAMPO_ECONOMICO_NAO_INFORMAVEL:" + campo:
                    falhas.append(f"L6 '{campo}': o chamador conseguiu informar valor economico ({err!r})")
        executar(falhas, "L6", l6)

        # ---- L7: recusas de referencia, moeda e valor ------------------------
        def l7():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const antes = JSON.stringify(S.alladin);
              const saves = window.__stub.saves;
              const out = {
                semConta:    L.addTransaction({eventType:'DEPOSIT', amount:100, effectiveAt:'2026-01-10'}).erro,
                contaFalsa:  L.addTransaction({eventType:'DEPOSIT', cashAccountId:'aldc_x', amount:100, effectiveAt:'2026-01-10'}).erro,
                eventoFalso: L.addTransaction({eventType:'SHORT_SELL', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-01-10'}).erro,
                amountZero:  L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:0, effectiveAt:'2026-01-10'}).erro,
                amountNeg:   L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:-5, effectiveAt:'2026-01-10'}).erro,
                amountFloat: L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:10.5, effectiveAt:'2026-01-10'}).erro,
                dataRuim:    L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100, effectiveAt:'10/01/2026'}).erro,
                mesmaConta:  L.addTransaction({eventType:'TRANSFER', sourceCashAccountId:f.caixaXP,
                               destinationCashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-01-10'}).erro,
                moedaDif:    L.addTransaction({eventType:'TRANSFER', sourceCashAccountId:f.caixaXP,
                               destinationCashAccountId:f.caixaUSD, amount:100, effectiveAt:'2026-01-10'}).erro,
                moedaDivergente: L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP,
                               currency:'USD', amount:100, effectiveAt:'2026-01-10'}).erro,
              };
              out.intacto = JSON.stringify(S.alladin) === antes;
              out.semSave = window.__stub.saves === saves;
              return out;
            }""")
            esperado = {"semConta": "ALD_REFERENCIA_AUSENTE:cashAccountId",
                        "contaFalsa": "ALD_CASHACCOUNT_NAO_ENCONTRADA",
                        "eventoFalso": "ALD_EVENT_TYPE_INVALIDO",
                        "amountZero": "ALD_AMOUNT_INVALIDO", "amountNeg": "ALD_AMOUNT_INVALIDO",
                        "amountFloat": "ALD_AMOUNT_INVALIDO", "dataRuim": "ALD_EFFECTIVE_AT_INVALIDA",
                        "mesmaConta": "ALD_TRANSFER_MESMA_CONTA",
                        "moedaDif": "ALD_TRANSFER_MOEDAS_DIFERENTES",
                        "moedaDivergente": "ALD_CURRENCY_DIVERGE_DA_CONTA"}
            for chave, err in esperado.items():
                if r[chave] != err:
                    falhas.append(f"L7 '{chave}': esperado {err}, veio {r[chave]!r}")
            if not r["intacto"]:
                falhas.append("L7: um lancamento recusado tocou o agregado")
            if not r["semSave"]:
                falhas.append("L7: um lancamento recusado chamou save()")
        executar(falhas, "L7", l7)

        # ---- L8: dedupe e fail-closed, nao aviso -----------------------------
        def l8():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const a = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000,
                effectiveAt:'2026-01-10', dedupeKey:'extrato-2026-01-10-001'});
              // mesma chave, OUTRA conta e outro valor: a chave e global
              const b = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaBTG, amount:9999,
                effectiveAt:'2026-01-11', dedupeKey:'extrato-2026-01-10-001'});
              const c = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000,
                effectiveAt:'2026-01-10', dedupeKey:'outra-chave'});
              const semChave1 = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:77, effectiveAt:'2026-01-12'});
              const semChave2 = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:77, effectiveAt:'2026-01-12'});
              return { primeira:a.ok, duplicada:b.ok, erroDup:b.erro, outra:c.ok,
                       avisos:(b.avisos||[]).length,
                       semChaveAmbas: semChave1.ok && semChave2.ok,
                       registros:S.alladin.transactions.length };
            }""")
            if not r["primeira"] or not r["outra"]:
                falhas.append(f"L8: lancamento legitimo recusado ({r})")
            if r["duplicada"] or r["erroDup"] != "ALD_DEDUPE_KEY_DUPLICADA":
                falhas.append(f"L8: duplicidade de LANCAMENTO deveria ser fail-closed ({r})")
            if r["avisos"]:
                falhas.append("L8: duplicidade economica virou AVISO — dinheiro nao se duplica com advertencia")
            if not r["semChaveAmbas"]:
                falhas.append("L8: sem dedupeKey o dominio nao deve inferir duplicidade")
            if r["registros"] != 4:
                falhas.append(f"L8: contagem de registros divergente ({r['registros']})")
        executar(falhas, "L8", l8)

        # ---- L9: conta inativa (emenda do gate) ------------------------------
        def l9():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura, c = JPWAlladin.cadastro;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaBTG, amount:5000, effectiveAt:'2026-01-10'});
              const tr = L.addTransaction({eventType:'TRANSFER', sourceCashAccountId:f.caixaBTG,
                destinationCashAccountId:f.caixaXP, amount:2000, effectiveAt:'2026-01-11'});
              const inativa = c.setRecordStatus('cashaccount', f.caixaBTG, 'INACTIVE');
              const saldoDepois = R.saldoDeCaixa(f.caixaBTG);
              const novo = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaBTG, amount:1, effectiveAt:'2026-02-01'});
              const rev = L.reverseTransaction(tr.recordId, {effectiveAt:'2026-02-02'});
              return { inativaOk:inativa.ok, saldo:saldoDepois.amount, disponivel:saldoDepois.available,
                       novoErro:novo.erro, reversalOk:rev.ok };
            }""")
            if not r["inativaOk"]:
                falhas.append("L9: inativar CashAccount COM historico foi recusado — o passado nao "
                              "impede encerrar a conta")
            if not r["disponivel"] or r["saldo"] != 3000:
                falhas.append(f"L9: historico deixou de valer apos a inativacao ({r})")
            if r["novoErro"] != "ALD_CASHACCOUNT_INATIVA":
                falhas.append(f"L9: lancamento NOVO em conta inativa deveria recusar ({r['novoErro']!r})")
            if not r["reversalOk"]:
                falhas.append("L9: reverter fato historico foi impedido pela inativacao posterior")
        executar(falhas, "L9", l9)

        # ---- L15: conta referenciada — o que trava e o que NAO trava ---------
        # A assimetria e o ponto: encerrar uma conta e um fato administrativo
        # legitimo, e o historico continua valendo; mas trocar sua MOEDA ou sua
        # conta-mae depois de haver lancamento reinterpreta o passado — os
        # registros ficam na moeda antiga e o saldo inteiro vira MOEDA_DIVERGENTE.
        # Corrigir cadastro depois de movimento exige outra conta, nao reescrever
        # o significado da que existe.
        def l15():
            r = ev("""() => {
              const f = fixture(), c = JPWAlladin.cadastro, L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const semUso = c.addCashAccount({accountId:f.btg, currency:'BRL'}).recordId;
              // antes de qualquer lancamento, editar e legitimo
              const antesCurrency = c.editCashAccount(semUso, {currency:'USD'});
              const tx = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP,
                amount:1000, effectiveAt:'2026-01-10'});
              const tr = L.addTransaction({eventType:'TRANSFER', sourceCashAccountId:f.caixaXP,
                destinationCashAccountId:f.caixaBTG, amount:400, effectiveAt:'2026-01-11'});
              return {
                antesDeUsar: antesCurrency.ok,
                editCurrency:  c.editCashAccount(f.caixaXP, {currency:'USD'}),
                editAccountId: c.editCashAccount(f.caixaXP, {accountId:f.btg}),
                // a ponta de DESTINO tambem esta referenciada
                editDestino:   c.editCashAccount(f.caixaBTG, {currency:'USD'}),
                editNadaEconomico: c.editCashAccount(f.caixaXP, {currency:'BRL'}),
                inativar: c.setRecordStatus('cashaccount', f.caixaXP, 'INACTIVE').ok,
                reversalAposInativar: L.reverseTransaction(tx.recordId, {effectiveAt:'2026-02-01'}).ok,
                saldo: R.saldoDeCaixa(f.caixaXP),
              };
            }""")
            if not r["antesDeUsar"]:
                falhas.append("L15: conta SEM lancamento deveria aceitar edicao de moeda")
            for campo in ("editCurrency", "editAccountId", "editDestino"):
                if r[campo]["ok"] or r[campo]["erro"] != "ALD_CASHACCOUNT_COM_LANCAMENTOS":
                    falhas.append(f"L15 [{campo}]: conta referenciada aceitou mudanca que "
                                  f"reinterpreta o passado ({r[campo]})")
            if not r["editNadaEconomico"]["ok"]:
                falhas.append(f"L15: reenviar a MESMA moeda nao e mudanca e deveria passar "
                              f"({r['editNadaEconomico']})")
            if not r["inativar"]:
                falhas.append("L15: encerrar conta com historico deveria continuar permitido")
            if not r["reversalAposInativar"]:
                falhas.append("L15: reverter fato historico apos a inativacao deveria ser permitido")
            if not r["saldo"]["available"]:
                falhas.append(f"L15: o saldo ficou indisponivel apos as recusas ({r['saldo']})")
        executar(falhas, "L15", l15)

        # ================= ALD-03 S2 — a dupla atomica papel<->caixa =========

        # ---- L16: BUY e UM registro com duas pernas; sem flowScope ----------
        def l16():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const b = L.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'100', amount:300000, fees:1000,
                taxes:500, effectiveAt:'2026-02-01'});
              const rec = R.transactions().find(t => t.transactionId === b.recordId);
              const cru = S.alladin.transactions[0];
              return { ok:b.ok && b.persistido, registros:S.alladin.transactions.length,
                       saldo:R.saldoDeCaixa(f.caixaXP),
                       temFsCru:Object.prototype.hasOwnProperty.call(cru,'flowScope'),
                       temFsDto:Object.prototype.hasOwnProperty.call(rec,'flowScope'),
                       quantity:rec.quantity, fees:rec.fees, taxes:rec.taxes,
                       amount:rec.amount, instrumentId:rec.instrumentId,
                       status:rec.status, moeda:rec.currency };
            }""")
            if not r["ok"] or r["registros"] != 1:
                falhas.append(f"L16: um fato economico deveria ser UM registro ({r})")
            if not r["saldo"]["available"] or r["saldo"]["amount"] != -301500:
                falhas.append(f"L16: cashDelta divergente de -(amount+fees+taxes) ({r['saldo']})")
            if r["temFsCru"] or r["temFsDto"]:
                falhas.append("L16: trade nasceu com flowScope — a AUSENCIA e contratual")
            if r["quantity"] != "100" or not isinstance(r["quantity"], str):
                falhas.append(f"L16: perna de papel nao persistiu quantity canonica ({r['quantity']!r})")
            if r["fees"] != 1000 or r["taxes"] != 500 or r["amount"] != 300000:
                falhas.append(f"L16: componentes divergentes ({r})")
            if r["instrumentId"] == "" or r["status"] != "POSTED" or r["moeda"] != "BRL":
                falhas.append(f"L16: forma do registro fora do contrato ({r})")
        executar(falhas, "L16", l16)

        # ---- L17: exemplo canonico da spec — DEPOSIT 10000, BUY 3000/10 -----
        def l17():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:10000, effectiveAt:'2026-02-01'});
              const b = L.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'100', amount:3000, fees:10,
                effectiveAt:'2026-02-02'});   // taxes AUSENTE na entrada
              const rec = S.alladin.transactions.find(t => t.transactionId === b.recordId);
              return { saldo:R.saldoDeCaixa(f.caixaXP).amount,
                       fees:rec.fees, taxes:rec.taxes,
                       temFees:Object.prototype.hasOwnProperty.call(rec,'fees'),
                       temTaxes:Object.prototype.hasOwnProperty.call(rec,'taxes') };
            }""")
            if r["saldo"] != 6990:
                falhas.append(f"L17 CANONICO: 10000 - (3000+10) deveria dar 6990, veio {r['saldo']}")
            if not r["temFees"] or not r["temTaxes"] or r["fees"] != 10 or r["taxes"] != 0:
                falhas.append(f"L17: taxes ausente na entrada deveria PERSISTIR 0 explicito ({r})")
        executar(falhas, "L17", l17)

        # ---- L18: SELL com liquido positivo, zero e negativo ---------------
        def l18():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const pos  = L.addTransaction({eventType:'SELL', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'10', amount:5000, fees:100, effectiveAt:'2026-02-01'});
              const s1 = R.saldoDeCaixa(f.caixaXP).amount;
              const zero = L.addTransaction({eventType:'SELL', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'1', amount:100, fees:100, effectiveAt:'2026-02-02'});
              const s2 = R.saldoDeCaixa(f.caixaXP).amount;
              const neg  = L.addTransaction({eventType:'SELL', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'0.5', amount:50, fees:100, taxes:10, effectiveAt:'2026-02-03'});
              const s3 = R.saldoDeCaixa(f.caixaXP);
              return { pos:pos.ok, zero:zero.ok, neg:neg.ok, s1, s2, s3:s3.amount,
                       ok3:s3.available, registros:S.alladin.transactions.length };
            }""")
            if not (r["pos"] and r["zero"] and r["neg"]):
                falhas.append(f"L18: SELL liquido zero/negativo deveria ser REPRESENTAVEL ({r})")
            if r["s1"] != 4900 or r["s2"] != 4900 or r["s3"] != 4840 or not r["ok3"]:
                falhas.append(f"L18: deltas divergentes (+4900, +0, -60) ({r})")
            if r["registros"] != 3:
                falhas.append(f"L18: registros divergentes ({r['registros']})")
        executar(falhas, "L18", l18)

        # ---- L19: reversal de trade — par soma zero, proibidos completos ----
        def l19():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const b = L.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'2.5', amount:1000, fees:10, taxes:5,
                effectiveAt:'2026-02-01'});
              const antes = R.saldoDeCaixa(f.caixaXP).amount;
              const rv = L.reverseTransaction(b.recordId, {effectiveAt:'2026-02-10'});
              const depois = R.saldoDeCaixa(f.caixaXP);
              const rev = S.alladin.transactions.find(t => t.transactionId === rv.recordId);
              const orig = S.alladin.transactions.find(t => t.transactionId === b.recordId);
              // proibidos: cada campo economico de trade recusa no reversal
              const s = L.addTransaction({eventType:'SELL', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'1', amount:100, effectiveAt:'2026-02-01'});
              const proibidos = ['quantity','fees','taxes','instrumentId','amount'].map(k => {
                const d = {effectiveAt:'2026-02-11'}; d[k] = k==='quantity' ? '9' : 9;
                return L.reverseTransaction(s.recordId, d).erro;
              });
              return { antes, depois:depois.amount, ok:depois.available,
                       revTipo:rev.reversedEventType, revQ:rev.quantity,
                       revFees:rev.fees, revTaxes:rev.taxes, revInst:rev.instrumentId===orig.instrumentId,
                       temFs:Object.prototype.hasOwnProperty.call(rev,'flowScope'),
                       origStatus:orig.status, proibidos,
                       registros:S.alladin.transactions.length };
            }""")
            if r["antes"] != -1015 or r["depois"] != 0 or not r["ok"]:
                falhas.append(f"L19: par nao somou zero no caixa ({r['antes']} -> {r['depois']})")
            if r["revTipo"] != "BUY" or r["revQ"] != "2.5" or r["revFees"] != 10 or r["revTaxes"] != 5 or not r["revInst"]:
                falhas.append(f"L19: reversal nao copiou a economia byte-igual ({r})")
            if r["temFs"]:
                falhas.append("L19: reversal de trade nasceu com flowScope")
            if r["origStatus"] != "REVERSED":
                falhas.append(f"L19: original nao marcou REVERSED ({r['origStatus']})")
            esperados = ["ALD_CAMPO_ECONOMICO_NAO_INFORMAVEL:" + k for k in
                         ["quantity","fees","taxes","instrumentId","amount"]]
            if r["proibidos"] != esperados:
                falhas.append(f"L19: proibidos divergentes ({r['proibidos']})")
            if r["registros"] != 3:
                falhas.append(f"L19: recusa de proibido deixou vestigio ({r['registros']})")
        executar(falhas, "L19", l19)

        # ---- L20: recusas de instrumento, moeda, dedupe e overflow ----------
        def l20():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, c = JPWAlladin.cadastro;
              const MAX = Number.MAX_SAFE_INTEGER;
              c.setRecordStatus('instrument', f.aaplUsd, 'INACTIVE');
              const base = {eventType:'BUY', cashAccountId:f.caixaXP, quantity:'1', amount:100, effectiveAt:'2026-02-01'};
              L.addTransaction({...base, instrumentId:f.petr4, dedupeKey:'trade-1'});
              return {
                semInstrumento: L.addTransaction({...base}).erro,
                inexistente:    L.addTransaction({...base, instrumentId:'aldi_fantasma'}).erro,
                inativo:        L.addTransaction({...base, instrumentId:f.aaplUsd}).erro,
                moedaDiverge:   L.addTransaction({eventType:'SELL', instrumentId:f.petr4,
                                  cashAccountId:f.caixaUSD, quantity:'1', amount:100,
                                  effectiveAt:'2026-02-01'}).erro,
                dedupe:         L.addTransaction({...base, instrumentId:f.petr4, dedupeKey:'trade-1'}).erro,
                overflowBuy:    L.addTransaction({...base, instrumentId:f.petr4, amount:MAX, fees:1}).erro,
                overflowSell:   L.addTransaction({eventType:'SELL', instrumentId:f.petr4,
                                  cashAccountId:f.caixaXP, quantity:'1', amount:1,
                                  fees:MAX, taxes:MAX, effectiveAt:'2026-02-01'}).erro,
                feesInvalida:   L.addTransaction({...base, instrumentId:f.petr4, fees:-1}).erro,
                taxesInvalido:  L.addTransaction({...base, instrumentId:f.petr4, taxes:1.5}).erro,
                registros: S.alladin.transactions.length };
            }""")
            esperado = { "semInstrumento":"ALD_REFERENCIA_AUSENTE:instrumentId",
                         "inexistente":"ALD_INSTRUMENT_NAO_ENCONTRADO",
                         "inativo":"ALD_INSTRUMENT_INATIVO",
                         "moedaDiverge":"ALD_INSTRUMENT_MOEDA_DIVERGE_DA_CONTA",
                         "dedupe":"ALD_DEDUPE_KEY_DUPLICADA",
                         "overflowBuy":"ALD_EFEITO_MONETARIO_FORA_DO_INTEIRO_SEGURO",
                         "overflowSell":"ALD_EFEITO_MONETARIO_FORA_DO_INTEIRO_SEGURO",
                         "feesInvalida":"ALD_FEES_INVALIDAS",
                         "taxesInvalido":"ALD_TAXES_INVALIDOS" }
            for k, v in esperado.items():
                if r[k] != v:
                    falhas.append(f"L20 {k}: esperado {v}, veio {r[k]!r}")
            if r["registros"] != 1:
                falhas.append(f"L20: recusa deixou vestigio ({r['registros']})")
        executar(falhas, "L20", l20)

        # ---- L21: quantity — uma grafia por valor ---------------------------
        def l21():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const probe = q => L.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:q, amount:100, effectiveAt:'2026-02-01'});
              const validas   = ['1','1.5','0.005','100.01','123456789.000000001'].map(q => probe(q).ok);
              const invalidas = ['0','01','1.0','1.50','.5','1.','1e5','-1','+1','1,5','abc','',
                                 '1'.repeat(65)].map(q => probe(q).erro);
              const naoString = probe(1.5).erro;
              return { validas, invalidas, naoString };
            }""")
            if r["validas"] != [True]*5:
                falhas.append(f"L21: forma canonica valida recusada ({r['validas']})")
            if r["invalidas"] != ["ALD_QUANTITY_INVALIDA"]*13 or r["naoString"] != "ALD_QUANTITY_INVALIDA":
                falhas.append(f"L21: grafia nao-canonica aceita ({r['invalidas']}, {r['naoString']!r})")
        executar(falhas, "L21", l21)

        # ---- L22: flowScope em trade — declarar semantica impossivel RECUSA -
        # A-B: o chamador que informa flowScope num trade declarou algo que nao
        # existe; apagar em silencio mascararia o erro do produtor. A regra e de
        # PRESENCA: {flowScope: undefined} tambem recusa. C: adulterar o dado
        # persistido continua ilegivel -> BLOCKING.
        def l22():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const base = {instrumentId:f.petr4, cashAccountId:f.caixaXP,
                            quantity:'1', amount:100, effectiveAt:'2026-02-01'};
              const buyValor  = L.addTransaction({eventType:'BUY',  ...base, flowScope:'EXTERNAL'});
              const sellValor = L.addTransaction({eventType:'SELL', ...base, flowScope:'INTERNAL'});
              const buyUndef  = L.addTransaction({eventType:'BUY',  ...base, flowScope:undefined});
              const aposRecusas = S.alladin.transactions.length;
              const b = L.addTransaction({eventType:'BUY', ...base});
              S.alladin.transactions.find(t => t.transactionId === b.recordId).flowScope = 'INTERNAL';
              const saldo = R.saldoDeCaixa(f.caixaXP);
              return { erros:[buyValor.erro, sellValor.erro, buyUndef.erro], aposRecusas,
                       disponivel:saldo.available, issues:saldo.issues.slice() };
            }""")
            if r["erros"] != ["ALD_FLOW_SCOPE_NAO_PERMITIDO_EM_TRADE"]*3:
                falhas.append(f"L22-A/B: flowScope declarado em trade deveria RECUSAR ({r['erros']})")
            if r["aposRecusas"] != 0:
                falhas.append(f"L22-A/B: recusa deixou Transaction no ledger ({r['aposRecusas']})")
            if r["disponivel"] or "ALD_TRANSACAO_ILEGIVEL" not in r["issues"]:
                falhas.append(f"L22-C: trade adulterado com flowScope deveria ser ILEGIVEL ({r})")
        executar(falhas, "L22", l22)

        # ---- L23: instrumentFamily congela na primeira referencia -----------
        def l23():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, c = JPWAlladin.cadastro;
              const antes = c.editInstrument(f.petr4, {instrumentFamily:'FUND_LIKE'});
              L.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'1', amount:100, effectiveAt:'2026-02-01'});
              const depois = c.editInstrument(f.petr4, {instrumentFamily:'EQUITY_LIKE'});
              const igual  = c.editInstrument(f.petr4, {instrumentFamily:'FUND_LIKE'});
              const symbol = c.editInstrument(f.petr4, {symbol:'PETR4X'});
              return { antes:antes.ok, depoisErro:depois.erro, igual:igual.ok, symbol:symbol.ok,
                       familia:S.alladin.instruments.find(i=>i.instrumentId===f.petr4).instrumentFamily };
            }""")
            if not r["antes"]:
                falhas.append("L23: curadoria ANTES do primeiro trade deveria ser livre")
            if r["depoisErro"] != "ALD_INSTRUMENT_COM_LANCAMENTOS":
                falhas.append(f"L23: familia nao congelou apos referencia ({r['depoisErro']!r})")
            if not r["igual"] or not r["symbol"]:
                falhas.append(f"L23: edicao sem troca de familia (ou de symbol) deveria seguir livre ({r})")
            if r["familia"] != "FUND_LIKE":
                falhas.append(f"L23: familia final divergente ({r['familia']})")
        executar(falhas, "L23", l23)

        # ---- L24-L28: MC-S2-1 — o par e julgado na LEITURA ------------------
        # A escrita constroi o reversal correto; estes casos adulteram o dado
        # PERSISTIDO e provam que o saldo vira INDISPONIVEL, nunca um numero
        # plausivel. O vetor do blocker: +10000 -9000 = +1000 "valido".
        def l24():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:10000, effectiveAt:'2026-02-01'});
              const rv = L.reverseTransaction(d.recordId, {effectiveAt:'2026-02-02'});
              const antes = R.saldoDeCaixa(f.caixaXP);
              const rev = S.alladin.transactions.find(t => t.transactionId === rv.recordId);
              rev.amount = 9000;   // adulteracao pos-escrita
              const depois = R.saldoDeCaixa(f.caixaXP);
              return { antes:antes.amount, okAntes:antes.available,
                       disponivel:depois.available, amount:depois.amount,
                       issues:depois.issues.slice(), id:rv.recordId };
            }""")
            if r["antes"] != 0 or not r["okAntes"]:
                falhas.append(f"L24: par legitimo deveria somar zero ({r})")
            if r["disponivel"] or r["amount"] is not None:
                falhas.append(f"L24 BLOCKER: reversal adulterado devolveu saldo com cara de valido ({r})")
            if ("ALD_REVERSAL_INCONSISTENTE:" + r["id"]) not in r["issues"]:
                falhas.append(f"L24: issue de inconsistencia ausente ({r['issues']})")
        executar(falhas, "L24", l24)

        def l25():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:5000, effectiveAt:'2026-02-01'});
              const rv = L.reverseTransaction(d.recordId, {effectiveAt:'2026-02-02'});
              const rev = S.alladin.transactions.find(t => t.transactionId === rv.recordId);
              rev.reversedEventType = 'WITHDRAWAL';   // mesmo flowScope EXTERNAL: registro segue legivel
              const s = R.saldoDeCaixa(f.caixaXP);
              return { disponivel:s.available, issues:s.issues.slice(), id:rv.recordId };
            }""")
            if r["disponivel"] or ("ALD_REVERSAL_INCONSISTENTE:" + r["id"]) not in r["issues"]:
                falhas.append(f"L25: reversedEventType adulterado nao virou BLOCKING ({r})")
        executar(falhas, "L25", l25)

        def l26():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const out = {};
              for(const [campo, valor] of [['quantity','999'],['fees',11],['taxes',6],['instrumentId','aldi_outro']]){
                S.alladin.transactions.length = 0;
                const b = L.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                  cashAccountId:f.caixaXP, quantity:'2.5', amount:1000, fees:10, taxes:5,
                  effectiveAt:'2026-02-01'});
                const rv = L.reverseTransaction(b.recordId, {effectiveAt:'2026-02-02'});
                const rev = S.alladin.transactions.find(t => t.transactionId === rv.recordId);
                rev[campo] = valor;
                const s = R.saldoDeCaixa(f.caixaXP);
                out[campo] = { disponivel:s.available,
                               marcado:s.issues.indexOf('ALD_REVERSAL_INCONSISTENTE:'+rv.recordId)>=0 };
              }
              return out;
            }""")
            for campo, res in r.items():
                if res["disponivel"] or not res["marcado"]:
                    falhas.append(f"L26 {campo}: divergencia no par de trade nao virou BLOCKING ({res})")
        executar(falhas, "L26", l26)

        def l27():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              // (a) reversal de DEPOSIT perde o flowScope -> registro ILEGIVEL
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-02-01'});
              const rv1 = L.reverseTransaction(d.recordId, {effectiveAt:'2026-02-02'});
              delete S.alladin.transactions.find(t => t.transactionId === rv1.recordId).flowScope;
              const sA = R.saldoDeCaixa(f.caixaXP);
              // (b) reversal de BUY ganha um flowScope -> registro ILEGIVEL
              S.alladin.transactions.length = 0;
              const b = L.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'1', amount:100, effectiveAt:'2026-02-01'});
              const rv2 = L.reverseTransaction(b.recordId, {effectiveAt:'2026-02-02'});
              S.alladin.transactions.find(t => t.transactionId === rv2.recordId).flowScope = 'INTERNAL';
              const sB = R.saldoDeCaixa(f.caixaXP);
              return { a:{disponivel:sA.available, ilegivel:sA.issues.indexOf('ALD_TRANSACAO_ILEGIVEL')>=0},
                       b:{disponivel:sB.available, ilegivel:sB.issues.indexOf('ALD_TRANSACAO_ILEGIVEL')>=0} };
            }""")
            if r["a"]["disponivel"] or not r["a"]["ilegivel"]:
                falhas.append(f"L27a: reversal de fluxo SEM flowScope deveria ser ilegivel ({r['a']})")
            if r["b"]["disponivel"] or not r["b"]["ilegivel"]:
                falhas.append(f"L27b: reversal de trade COM flowScope deveria ser ilegivel ({r['b']})")
        executar(falhas, "L27", l27)

        def l28():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-02-01'});
              const rv = L.reverseTransaction(d.recordId, {effectiveAt:'2026-02-02'});
              const rev = S.alladin.transactions.find(t => t.transactionId === rv.recordId);
              rev.cashAccountId = f.caixaBTG;   // mentira: o efeito continua vindo do original
              const xp = R.saldoDeCaixa(f.caixaXP), btg = R.saldoDeCaixa(f.caixaBTG);
              return { xp:{disponivel:xp.available, marcado:xp.issues.indexOf('ALD_REVERSAL_INCONSISTENTE:'+rv.recordId)>=0},
                       btg:{disponivel:btg.available, marcado:btg.issues.indexOf('ALD_REVERSAL_INCONSISTENTE:'+rv.recordId)>=0} };
            }""")
            for conta in ("xp","btg"):
                if r[conta]["disponivel"] or not r[conta]["marcado"]:
                    falhas.append(f"L28 {conta}: refs adulteradas do par nao viraram BLOCKING ({r[conta]})")
        executar(falhas, "L28", l28)

        # ---- L29: MC-S2-2 — o acumulador nunca atravessa regiao insegura ----
        def l29():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const MAX = Number.MAX_SAFE_INTEGER;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:MAX-10, effectiveAt:'2026-01-01'});
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:20, effectiveAt:'2026-01-02'});
              L.addTransaction({eventType:'WITHDRAWAL', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-01-03'});
              // final "voltaria" a MAX-90 (seguro) — mas o caminho passou por MAX+10
              const s = R.saldoDeCaixa(f.caixaXP);
              return { disponivel:s.available, amount:s.amount, marcado:s.issues.indexOf('ALD_SOMA_FORA_DO_INTEIRO_SEGURO')>=0 };
            }""")
            if r["disponivel"] or r["amount"] is not None or not r["marcado"]:
                falhas.append(f"L29: acumulador atravessou 2^53 e devolveu numero com cara de sao ({r})")
        executar(falhas, "L29", l29)

        # ---- L10: qualidade bloqueante, jamais saldo parcial ------------------
        def l10():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'});
              const bom = R.saldoDeCaixa(f.caixaXP);
              const out = { bomOk:bom.available, bomAmount:bom.amount, casos:{} };
              const testar = (rotulo, registro) => {
                const copia = S.alladin.transactions.slice();
                S.alladin.transactions.push(registro);
                const s = R.saldoDeCaixa(f.caixaXP);
                out.casos[rotulo] = { available:s.available, amount:s.amount,
                                      quality:s.quality, temIssue:(s.issues||[]).length > 0 };
                S.alladin.transactions = copia;
              };
              testar('lixo', { transactionId:'x' });
              testar('naoObjeto', 'texto');
              testar('amountNegativo', { transactionId:'aldtx_z', eventType:'DEPOSIT', status:'POSTED',
                flowScope:'EXTERNAL', amount:-1, currency:'BRL', effectiveAt:'2026-01-01',
                recordedAt:'2026-01-01T00:00:00.000Z', cashAccountId:f.caixaXP });
              testar('reversalOrfao', { transactionId:'aldtx_o', eventType:'REVERSAL', status:'POSTED',
                flowScope:'EXTERNAL', amount:10, currency:'BRL', effectiveAt:'2026-01-01',
                recordedAt:'2026-01-01T00:00:00.000Z', reversalOf:'aldtx_inexistente',
                reversedEventType:'DEPOSIT', cashAccountId:f.caixaXP });
              out.contaInexistente = R.saldoDeCaixa('aldc_nao_existe');
              return out;
            }""")
            if not r["bomOk"] or r["bomAmount"] != 1000:
                falhas.append(f"L10: base saudavel ja divergia ({r})")
            for rotulo, c in r["casos"].items():
                if c["available"] or c["amount"] is not None or c["quality"] != "BLOCKING" or not c["temIssue"]:
                    falhas.append(f"L10 [{rotulo}]: saldo PARCIAL apresentado como valido ({c}) — "
                                  "dado bloqueante deve tornar a metrica indisponivel")
            ci = r["contaInexistente"]
            if ci["available"] or ci["quality"] != "BLOCKING":
                falhas.append(f"L10: conta inexistente deveria ser BLOCKING ({ci})")
        executar(falhas, "L10", l10)

        # ---- L11: ordem economica, nunca a do array --------------------------
        def l11():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              // inseridos FORA de ordem cronologica de proposito
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-03-01'});
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:200, effectiveAt:'2026-01-01'});
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:300, effectiveAt:'2026-02-01'});
              return { ordemArray: S.alladin.transactions.map(t => t.effectiveAt),
                       ordemLeitura: R.transactions().map(t => t.effectiveAt),
                       saldo: R.saldoDeCaixa(f.caixaXP).amount };
            }""")
            if r["ordemLeitura"] != ["2026-01-01", "2026-02-01", "2026-03-01"]:
                falhas.append(f"L11: leitura nao esta em ordem economica ({r['ordemLeitura']})")
            if r["ordemArray"] == r["ordemLeitura"]:
                falhas.append("L11: o caso nao prova nada — a ordem de insercao ja era a cronologica")
            if r["saldo"] != 600:
                falhas.append(f"L11: soma independente de ordem divergiu ({r['saldo']})")
        executar(falhas, "L11", l11)

        # ---- L12: write gate e atomicidade -----------------------------------
        def l12():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              // persistencia recusada: nada sobra, nem no ledger nem no log
              const antes = JSON.stringify(S.alladin);
              const logAntes = JSON.stringify(S.dataGovernance.changeLog);
              window.__stub.saveResult = false;
              const t = L.addTransaction({eventType:'TRANSFER', sourceCashAccountId:f.caixaXP,
                destinationCashAccountId:f.caixaBTG, amount:100, effectiveAt:'2026-01-10'});
              const meio = { ok:t.ok, persistido:t.persistido, erro:t.erro,
                             intacto: JSON.stringify(S.alladin) === antes,
                             logIntacto: JSON.stringify(S.dataGovernance.changeLog) === logAntes };
              window.__stub.saveResult = true;
              // schema futuro: nenhum ato economico passa
              S.alladin.schemaVersion = 5;
              const bloqueado = {
                add: L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1, effectiveAt:'2026-01-10'}).erro,
                rev: L.reverseTransaction('aldtx_x', {effectiveAt:'2026-01-10'}).erro,
                gate: JPWAlladin.writeBlockReason(),
              };
              S.alladin.schemaVersion = 4;
              return { meio, bloqueado, trilha: S.dataGovernance.changeLog.map(e => e.action) };
            }""")
            m = r["meio"]
            if m["ok"] or m["persistido"] or m["erro"] != "persistencia recusada":
                falhas.append(f"L12: veredito de persistencia recusada divergente ({m})")
            if not m["intacto"]:
                falhas.append("L12: transferencia nao persistida deixou vestigio no ledger")
            if not m["logIntacto"]:
                falhas.append("L12: transferencia nao persistida deixou entrada no changeLog")
            b = r["bloqueado"]
            if b["gate"] != "READ_ONLY_FUTURE_SCHEMA" or b["add"] != "READ_ONLY_FUTURE_SCHEMA" \
               or b["rev"] != "READ_ONLY_FUTURE_SCHEMA":
                falhas.append(f"L12: schema futuro nao fechou o ledger ({b})")
        executar(falhas, "L12", l12)

        # ---- L13: DRAFT nao existe neste ciclo -------------------------------
        def l13():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const t = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1,
                effectiveAt:'2026-01-10', status:'DRAFT'});
              return { status: S.alladin.transactions[0].status,
                       vocabulario: JPWAlladin.catalogos().fechados.txStatus || null,
                       apis: Object.keys(JPWAlladin.ledger).sort() };
            }""")
            if r["status"] != "POSTED":
                falhas.append(f"L13: o chamador conseguiu criar registro fora de POSTED ({r['status']})")
            for api in r["apis"]:
                if "raft" in api or "post" in api.lower():
                    falhas.append(f"L13: API de DRAFT exposta neste ciclo ({api})")
            if r["apis"] != ["addTransaction", "reverseTransaction"]:
                falhas.append(f"L13: superficie do ledger diferente do contrato ({r['apis']})")
        executar(falhas, "L13", l13)

        # ---- L14: nenhum derivado persistido (ALD-I27) -----------------------
        def l14():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'});
              R.saldoDeCaixa(f.caixaXP); R.saldoDeCaixa(f.caixaXP);
              const bruto = JSON.stringify(S.alladin);
              return { proibidos: ['balance','saldo','holdings','positions','patrimonio',
                                   'currentValue','costBasis','pnl'].filter(k => bruto.indexOf('"'+k+'"') >= 0),
                       lerNaoMuta: (() => { const a = JSON.stringify(S.alladin);
                                            R.saldoDeCaixa(f.caixaXP); R.transactions();
                                            return JSON.stringify(S.alladin) === a; })(),
                       congelado: Object.isFrozen(R.saldoDeCaixa(f.caixaXP)) };
            }""")
            if r["proibidos"]:
                falhas.append(f"L14/ALD-I27: estado derivado PERSISTIDO no agregado ({r['proibidos']})")
            if not r["lerNaoMuta"]:
                falhas.append("L14: calcular saldo mutou o agregado")
            if not r["congelado"]:
                falhas.append("L14: o retorno do saldo nao e imutavel")
        executar(falhas, "L14", l14)

        browser.close()

    # `bloqueadas` fica como instrumento de diagnostico: uma pagina about:blank com
    # o modulo injetado nao emite requisicao nenhuma, e o esperado E zero. Qualquer
    # numero acima de zero significaria que algo tentou sair para a rede.
    if bloqueadas["n"]:
        falhas.append(f"harness: o modulo tentou {bloqueadas['n']} requisicao(oes) de rede")
    if falhas:
        print("ALLADIN LEDGER TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("alladin_ledger_test PASS (L1-L29: deposito/saque e saldo derivado; transferencia interna "
          "como UM registro que nao altera o patrimonio global — o caso canonico; flowScope como "
          "perimetro, persistido e validado; reversal preservando o original e somando zero, com suas "
          "cinco proibicoes e sem campo economico do chamador; recusas de referencia, moeda e valor; "
          "dedupe fail-closed; conta inativa recusa lancamento novo mas mantem historico e reversao; "
          "qualidade bloqueante nunca vira saldo parcial; ordem economica em vez da ordem do array; "
          "write gate transacional e schema futuro fechado; DRAFT ausente; zero derivado persistido; "
          "S2: BUY/SELL como UM registro de duas pernas sem flowScope, exemplo canonico 6990, "
          "SELL liquido negativo representavel, reversal copiando a economia byte-igual, "
          "consistencia cruzada do par na leitura (amount/tipo/campos/refs/flowScope adulterados "
          "viram BLOCKING), overflow recusado na escrita e acumulador com guarda por passo, "
          "quantity canonica de grafia unica, instrumentFamily congelada apos referencia)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
