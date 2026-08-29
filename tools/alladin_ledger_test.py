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
"""
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODULO = ROOT / "src/js/10-domain/13-alladin.js"

PRELUDE = """
window.__stub = { saves: 0, saveResult: true, logs: [] };
var S = { alladin: { schemaVersion: 3, reportingCurrency: 'BRL',
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
  S.alladin = { schemaVersion: 3, reportingCurrency: 'BRL', instruments: [], assets: [],
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
                eventoFalso: L.addTransaction({eventType:'BUY', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-01-10'}).erro,
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
              S.alladin.schemaVersion = 4;
              const bloqueado = {
                add: L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1, effectiveAt:'2026-01-10'}).erro,
                rev: L.reverseTransaction('aldtx_x', {effectiveAt:'2026-01-10'}).erro,
                gate: JPWAlladin.writeBlockReason(),
              };
              S.alladin.schemaVersion = 3;
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
    print("alladin_ledger_test PASS (L1-L14: deposito/saque e saldo derivado; transferencia interna "
          "como UM registro que nao altera o patrimonio global — o caso canonico; flowScope como "
          "perimetro, persistido e validado; reversal preservando o original e somando zero, com suas "
          "cinco proibicoes e sem campo economico do chamador; recusas de referencia, moeda e valor; "
          "dedupe fail-closed; conta inativa recusa lancamento novo mas mantem historico e reversao; "
          "qualidade bloqueante nunca vira saldo parcial; ordem economica em vez da ordem do array; "
          "write gate transacional e schema futuro fechado; DRAFT ausente; zero derivado persistido)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
