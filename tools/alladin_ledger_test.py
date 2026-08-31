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

HARDENING read-side (L30-L36): invariantes de UNICIDADE/CARDINALIDADE que eram
write-only, revalidadas na leitura sobre agregado PERSISTIDO adulterado.
  L30 transactionId duplicado -> BLOCKING (saldo dobraria)
  L31 dois REVERSALs do mesmo original -> BLOCKING (contra em dobro)
  L32 dedupeKey duplicado com ids distintos -> BLOCKING (dinheiro fabricado)
  L33 pareamento status<->reversal (REVERSED sem par; POSTED com par) -> BLOCKING
  L34 saldo sob schema futuro -> BLOCKING (simetria com posicoes)
  L35 container transactions nao-array -> BLOCKING ('0 confiante' e falso)
  L36 SENSIBILIDADE: fato legitimo duplicado (sem dedupe) NAO e corrupcao -> soma

AMENDMENT (id canonico duplicado = ambiguidade de IDENTIDADE, aldFindIn first-match):
  L37 (H1) cashAccountId duplicado -> saldo BLOCKING + lancamento novo RECUSADO
  L38 (H4) transactionId duplicado -> reverseTransaction RECUSADO (write gate)
  L39 (H5) assetId duplicado -> escrita cadastral RECUSADA (write gate)

ALD-03 S3 — FEE/TAX standalone (despesa sem contraparte de trade):
  L40 FEE debita exato; forma persistida so-caixa (sem flowScope nem trade)
  L41 TAX debita exato
  L42 reversal de FEE e de TAX soma zero; reversal sem flowScope
  L43 campos proibidos recusados (instrumentId/quantity/fees/taxes/flowScope/
      transactionRef/refs de transferencia) — sem vinculo a trade
  L44 conta inativa recusa despesa nova; historico e reversao seguem valendo
  L45 moeda derivada da conta; divergente recusada
  L46 dedupe fail-closed; duas despesas iguais SEM dedupe sao dois fatos
  L47 despesa PERSISTIDA adulterada com campo de trade -> ILEGIVEL (BLOCKING)

ALD-03 S4 — ajuste de reconciliacao (diferenca de caixa sem contraparte):
  L48 ADJUSTMENT_CREDIT soma exato
  L49 ADJUSTMENT_DEBIT subtrai exato
  L50 reason obrigatorio (ausente/null/vazio/espacos/nao-texto), campo proprio
      e distinto de note; reason fora do ajuste e recusado
  L51 campos proibidos recusados por presenca (papel, vinculo, flowScope)
  L52 reversal de CREDIT e de DEBIT somam zero; reason do reversal e PROPRIO
  L53 conta inativa recusa ajuste novo; historico e reversao seguem valendo
  L54 dedupe fail-closed; dois ajustes iguais SEM dedupe sao dois fatos
  L55 forma persistida limpa; adulteracao pos-escrita -> ILEGIVEL
  L56 completude do ALD_CASH_DELTA: (a) todo tipo cash-affecting move o saldo;
      (b) tipo legivel SEM entrada na tabela vira BLOCKING com
      ALD_CASH_DELTA_AUSENTE — nunca delta 0 implicito — e o reversal orfao
      mantem o diagnostico proprio
"""
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODULO = ROOT / "src/js/10-domain/13-alladin.js"

PRELUDE = """
window.__stub = { saves: 0, saveResult: true, logs: [] };
var S = { alladin: { schemaVersion: 6, reportingCurrency: 'BRL',
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
  S.alladin = { schemaVersion: 6, reportingCurrency: 'BRL', instruments: [], assets: [],
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

        # ===== HARDENING (read-side): DADO INVÁLIDO -> BLOCKING, nunca número ==
        # As invariantes de UNICIDADE/CARDINALIDADE eram write-only; um agregado
        # PERSISTIDO adulterado produzia número plausível e falso. L30-L35 provam
        # que a leitura agora revalida; L36 prova que fato legítimo duplicado
        # (mesmo valor, id distinto, sem dedupe) NÃO é confundido com corrupção.

        # ---- L30: transactionId duplicado -> saldo BLOCKING ------------------
        def l30():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              S.alladin.transactions.push(JSON.parse(JSON.stringify(S.alladin.transactions[0])));
              const s = R.saldoDeCaixa(f.caixaXP);
              return { av:s.available, amount:s.amount, m:s.issues.some(i=>i.indexOf('ALD_TRANSACTION_ID_DUPLICADO')===0) };
            }""")
            if r["av"] or r["amount"] is not None or not r["m"]:
                falhas.append(f"L30: id duplicado nao virou BLOCKING (saldo dobraria) ({r})")
        executar(falhas, "L30", l30)

        # ---- L31: dois REVERSALs do mesmo original -> BLOCKING ----------------
        def l31():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const rv = L.reverseTransaction(d.recordId, {effectiveAt:'2026-01-11'});
              const rev = S.alladin.transactions.find(t=>t.transactionId===rv.recordId);
              const r2 = JSON.parse(JSON.stringify(rev)); r2.transactionId='aldtx_dup'; S.alladin.transactions.push(r2);
              const s = R.saldoDeCaixa(f.caixaXP);
              return { av:s.available, m:s.issues.some(i=>i.indexOf('ALD_REVERSAL_DUPLICADO')===0) };
            }""")
            if r["av"] or not r["m"]:
                falhas.append(f"L31: dois reversals do mesmo original nao bloquearam (saldo -100000 falso) ({r})")
        executar(falhas, "L31", l31)

        # ---- L32: dedupeKey duplicado com ids distintos -> BLOCKING ----------
        def l32():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10', dedupeKey:'sal'});
              const c = JSON.parse(JSON.stringify(S.alladin.transactions[0])); c.transactionId='outro'; S.alladin.transactions.push(c);
              const s = R.saldoDeCaixa(f.caixaXP);
              return { av:s.available, m:s.issues.some(i=>i.indexOf('ALD_DEDUPE_KEY_DUPLICADA')===0) };
            }""")
            if r["av"] or not r["m"]:
                falhas.append(f"L32: dedupeKey duplicado nao bloqueou (dinheiro fabricado) ({r})")
        executar(falhas, "L32", l32)

        # ---- L33: pareamento status<->reversal (REVERSED sem par; POSTED com par)
        def l33():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const rv = L.reverseTransaction(d.recordId, {effectiveAt:'2026-01-11'});
              // (a) apaga o reversal, original fica REVERSED sozinho
              S.alladin.transactions = S.alladin.transactions.filter(t=>t.transactionId!==rv.recordId);
              const semPar = R.saldoDeCaixa(f.caixaXP);
              // (b) recria par e mente o status do original para POSTED
              S.alladin.transactions.length=0;
              const d2 = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              L.reverseTransaction(d2.recordId, {effectiveAt:'2026-01-11'});
              S.alladin.transactions.find(t=>t.transactionId===d2.recordId).status='POSTED';
              const mente = R.saldoDeCaixa(f.caixaXP);
              return { a:{av:semPar.available, m:semPar.issues.some(i=>i.indexOf('ALD_REVERSAL_STATUS_INCONSISTENTE')===0)},
                       b:{av:mente.available, m:mente.issues.some(i=>i.indexOf('ALD_REVERSAL_STATUS_INCONSISTENTE')===0)} };
            }""")
            for nome, res in r.items():
                if res["av"] or not res["m"]:
                    falhas.append(f"L33 {nome}: pareamento status<->reversal nao bloqueou ({res})")
        executar(falhas, "L33", l33)

        # ---- L34: saldo sob SCHEMA FUTURO -> BLOCKING (simetria com posicoes) -
        def l34():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:5000, effectiveAt:'2026-01-10'});
              S.alladin.schemaVersion = 7;
              const s = R.saldoDeCaixa(f.caixaXP);
              S.alladin.schemaVersion = 6;
              const volta = R.saldoDeCaixa(f.caixaXP);
              return { av:s.available, m:s.issues.indexOf('READ_ONLY_FUTURE_SCHEMA')>=0, voltou:volta.available && volta.amount===5000 };
            }""")
            if r["av"] or not r["m"]:
                falhas.append(f"L34: saldo sob schema futuro deveria BLOQUEAR (numero nao confiavel) ({r})")
            if not r["voltou"]:
                falhas.append(f"L34: saldo nao voltou ao normal na versao corrente ({r})")
        executar(falhas, "L34", l34)

        # ---- L35: container transactions NAO-array -> BLOCKING ----------------
        def l35():
            r = ev("""() => {
              const f = fixture(), R = JPWAlladin.leitura;
              S.alladin.transactions = {bad:1};
              const s = R.saldoDeCaixa(f.caixaXP);
              S.alladin.transactions = [];
              return { av:s.available, m:s.issues.indexOf('ALD_TRANSACOES_ILEGIVEIS')>=0 };
            }""")
            if r["av"] or not r["m"]:
                falhas.append(f"L35: container nao-array deveria BLOQUEAR ('0 confiante' e falso) ({r})")
        executar(falhas, "L35", l35)

        # ---- L36: SENSIBILIDADE — fato legítimo duplicado NAO e corrupção -----
        def l36():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              // dois depositos IDENTICOS, ids distintos, SEM dedupe: dois fatos reais
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const s = R.saldoDeCaixa(f.caixaXP);
              return { av:s.available, amount:s.amount };
            }""")
            if not r["av"] or r["amount"] != 200000:
                falhas.append(f"L36: a guarda de integridade confundiu fato legitimo duplicado com corrupcao ({r})")
        executar(falhas, "L36", l36)

        # ===== AMENDMENT: id canonico DUPLICADO e ambiguidade de IDENTIDADE ====
        # aldFindIn resolve por first-match — na leitura E na escrita. Id canonico
        # duplicado => saldo/posicao atribuidos a referencia arbitraria (RT-H1) e
        # ato novo operaria sobre o registro errado (RT-H2). O write gate recusa
        # ANTES de qualquer aldMutate produzir mudanca.

        # ---- L37 (H1): cashAccountId duplicado -> saldo BLOCKING + lanc. recusado
        def l37():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const dup = JSON.parse(JSON.stringify(S.alladin.cashAccounts.find(c=>c.cashAccountId===f.caixaXP)));
              dup.accountId = f.btg; S.alladin.cashAccounts.push(dup);
              const s = R.saldoDeCaixa(f.caixaXP);
              const w = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1, effectiveAt:'2026-01-11'});
              return { sAv:s.available, sM:s.issues.some(i=>i.indexOf('ALD_ID_DUPLICADO:cashAccounts')===0),
                       wErr:w.erro, wPers:w.persistido, n:S.alladin.transactions.length };
            }""")
            if r["sAv"] or not r["sM"]:
                falhas.append(f"L37: cashAccountId duplicado nao bloqueou o saldo ({r})")
            if not (r["wErr"] or '').startswith('ALD_INTEGRIDADE_ESTRUTURAL') or r["wPers"] or r["n"] != 1:
                falhas.append(f"L37: lancamento novo sobre identidade ambigua nao foi recusado ({r})")
        executar(falhas, "L37", l37)

        # ---- L38 (H4): transactionId duplicado -> reverseTransaction recusado -
        def l38():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const d = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              S.alladin.transactions.push(JSON.parse(JSON.stringify(S.alladin.transactions[0])));
              const rv = L.reverseTransaction(d.recordId, {effectiveAt:'2026-01-11'});
              return { err:rv.erro, pers:rv.persistido, n:S.alladin.transactions.length };
            }""")
            if not (r["err"] or '').startswith('ALD_INTEGRIDADE_ESTRUTURAL') or r["pers"] or r["n"] != 2:
                falhas.append(f"L38: reverseTransaction sobre id ambiguo nao foi recusado ({r})")
        executar(falhas, "L38", l38)

        # ---- L39 (H5): assetId duplicado -> write gate recusado --------------
        def l39():
            r = ev("""() => {
              const f = fixture(), c = JPWAlladin.cadastro;
              const asset = c.addAsset({name:'Casa', nature:'IMOVEL', recordMode:'INDIVIDUAL'}).recordId;
              S.alladin.assets.push(JSON.parse(JSON.stringify(S.alladin.assets.find(x=>x.assetId===asset))));
              const w = c.addAccount({name:'Novo', institution:'N', accountType:'BANK'});
              return { err:w.erro, pers:w.persistido };
            }""")
            if not (r["err"] or '').startswith('ALD_INTEGRIDADE_ESTRUTURAL') or r["pers"]:
                falhas.append(f"L39: escrita sobre assetId duplicado nao foi recusada ({r})")
        executar(falhas, "L39", l39)

        # ===== ALD-03 S3 — FEE/TAX STANDALONE (despesa sem contraparte) =======
        # Despesa economica que NAO pertence a transacao alguma: custodia,
        # manutencao, imposto de periodo. So-caixa, sempre saida, sem flowScope
        # e SEM vinculo a trade — e a ausencia de vinculo que torna a dupla
        # contagem do ALD-I36 irrepresentavel, sem heuristica alguma.

        # ---- L40/L41: FEE e TAX debitam exato --------------------------------
        def l40_l41():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const fee = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:1500,
                effectiveAt:'2026-01-31', note:'custodia mensal'});
              const s1 = R.saldoDeCaixa(f.caixaXP);
              const tax = L.addTransaction({eventType:'TAX', cashAccountId:f.caixaXP, amount:500, effectiveAt:'2026-01-31'});
              const s2 = R.saldoDeCaixa(f.caixaXP);
              const rec = S.alladin.transactions.find(t => t.transactionId === fee.recordId);
              return { feeOk:fee.ok && fee.persistido, taxOk:tax.ok, s1:s1.amount, s2:s2.amount,
                       av:s2.available, status:rec.status, moeda:rec.currency,
                       campos:Object.keys(rec).sort() };
            }""")
            if not r["feeOk"] or not r["taxOk"]:
                falhas.append(f"L40/L41: FEE/TAX recusados ({r})")
            if r["s1"] != 98500:
                falhas.append(f"L40: FEE deveria debitar exato (100000-1500=98500), veio {r['s1']}")
            if r["s2"] != 98000 or not r["av"]:
                falhas.append(f"L41: TAX deveria debitar exato (98500-500=98000), veio {r['s2']}")
            if r["status"] != "POSTED" or r["moeda"] != "BRL":
                falhas.append(f"L40: forma do registro fora do contrato ({r})")
            # forma persistida: so-caixa, sem flowScope nem campos de trade
            esperado = ['amount','cashAccountId','currency','effectiveAt','eventType',
                        'note','recordedAt','status','transactionId']
            if r["campos"] != esperado:
                falhas.append(f"L40: forma persistida do FEE divergente ({r['campos']})")
        executar(falhas, "L40/L41", l40_l41)

        # ---- L42: reversal de FEE/TAX soma zero ------------------------------
        def l42():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const fee = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:1500, effectiveAt:'2026-01-31'});
              const antes = R.saldoDeCaixa(f.caixaXP).amount;
              const rv = L.reverseTransaction(fee.recordId, {effectiveAt:'2026-02-01'});
              const depois = R.saldoDeCaixa(f.caixaXP);
              const rev = S.alladin.transactions.find(t => t.transactionId === rv.recordId);
              const orig = S.alladin.transactions.find(t => t.transactionId === fee.recordId);
              const tax = L.addTransaction({eventType:'TAX', cashAccountId:f.caixaXP, amount:700, effectiveAt:'2026-02-02'});
              const rvT = L.reverseTransaction(tax.recordId, {effectiveAt:'2026-02-03'});
              const fim = R.saldoDeCaixa(f.caixaXP);
              return { antes, depois:depois.amount, av:depois.available,
                       revTipo:rev.reversedEventType, origStatus:orig.status,
                       revFs:Object.prototype.hasOwnProperty.call(rev,'flowScope'),
                       taxRev:rvT.ok, fim:fim.amount };
            }""")
            if r["antes"] != 98500 or r["depois"] != 100000 or not r["av"]:
                falhas.append(f"L42: par FEE+reversal nao somou zero ({r})")
            if r["revTipo"] != "FEE" or r["origStatus"] != "REVERSED" or r["revFs"]:
                falhas.append(f"L42: reversal de FEE fora do contrato ({r})")
            if not r["taxRev"] or r["fim"] != 100000:
                falhas.append(f"L42: par TAX+reversal nao somou zero ({r})")
        executar(falhas, "L42", l42)

        # ---- L43: campos proibidos recusados (sem vinculo, sem trade) --------
        def l43():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const base = {eventType:'FEE', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-03-01'};
              const out = {};
              for(const [k,v] of [['instrumentId',f.petr4],['quantity','1'],['fees',10],['taxes',5],
                                  ['flowScope','EXTERNAL'],['transactionRef','aldtx_x'],
                                  ['sourceCashAccountId',f.caixaBTG],['destinationCashAccountId',f.caixaBTG]]){
                const d = {...base}; d[k]=v;
                out[k] = L.addTransaction(d).erro;
              }
              const outTax = L.addTransaction({eventType:'TAX', cashAccountId:f.caixaXP, amount:100,
                effectiveAt:'2026-03-01', instrumentId:f.petr4}).erro;
              return { out, outTax, n:S.alladin.transactions.length };
            }""")
            for campo, erro in r["out"].items():
                if erro != 'ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA:'+campo:
                    falhas.append(f"L43 {campo}: despesa aceitou campo proibido ({erro!r})")
            if r["outTax"] != 'ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA:instrumentId':
                falhas.append(f"L43 TAX: proibicao nao vale para TAX ({r['outTax']!r})")
            if r["n"] != 0:
                falhas.append(f"L43: recusa deixou vestigio ({r['n']})")
        executar(falhas, "L43", l43)

        # ---- L44: conta inativa recusa novo; historico e reversao seguem -----
        def l44():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura, c = JPWAlladin.cadastro;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const fee = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:1500, effectiveAt:'2026-01-31'});
              c.setRecordStatus('cashaccount', f.caixaXP, 'INACTIVE');
              const novo = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-02-01'});
              const saldo = R.saldoDeCaixa(f.caixaXP);
              const rv = L.reverseTransaction(fee.recordId, {effectiveAt:'2026-02-02'});
              return { novoErro:novo.erro, saldoAv:saldo.available, saldo:saldo.amount, revOk:rv.ok };
            }""")
            if r["novoErro"] != "ALD_CASHACCOUNT_INATIVA":
                falhas.append(f"L44: conta inativa deveria recusar FEE novo ({r['novoErro']!r})")
            if not r["saldoAv"] or r["saldo"] != 98500:
                falhas.append(f"L44: historico deixou de valer apos inativar ({r})")
            if not r["revOk"]:
                falhas.append(f"L44: reversao de despesa antiga deveria seguir permitida ({r})")
        executar(falhas, "L44", l44)

        # ---- L45: moeda derivada da conta; divergente recusada ---------------
        def l45():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const ok = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaUSD, amount:100, effectiveAt:'2026-03-01'});
              const rec = S.alladin.transactions.find(t => t.transactionId === ok.recordId);
              const diverge = L.addTransaction({eventType:'TAX', cashAccountId:f.caixaXP, amount:100,
                effectiveAt:'2026-03-01', currency:'USD'}).erro;
              return { moeda:rec.currency, diverge };
            }""")
            if r["moeda"] != "USD":
                falhas.append(f"L45: moeda nao foi derivada da conta ({r['moeda']!r})")
            if r["diverge"] != "ALD_CURRENCY_DIVERGE_DA_CONTA":
                falhas.append(f"L45: moeda divergente deveria ser recusada ({r['diverge']!r})")
        executar(falhas, "L45", l45)

        # ---- L46: dedupe fail-closed tambem para despesa ---------------------
        def l46():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const a = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:1500,
                effectiveAt:'2026-01-31', dedupeKey:'custodia-jan'});
              const b = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:1500,
                effectiveAt:'2026-01-31', dedupeKey:'custodia-jan'});
              // sem dedupe, duas despesas iguais sao DOIS fatos legitimos
              const c1 = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:200, effectiveAt:'2026-02-01'});
              const c2 = L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:200, effectiveAt:'2026-02-01'});
              return { aOk:a.ok, bErro:b.erro, c1:c1.ok, c2:c2.ok,
                       saldo:JPWAlladin.leitura.saldoDeCaixa(f.caixaXP).amount };
            }""")
            if not r["aOk"] or r["bErro"] != "ALD_DEDUPE_KEY_DUPLICADA":
                falhas.append(f"L46: dedupe de despesa nao e fail-closed ({r})")
            if not (r["c1"] and r["c2"]) or r["saldo"] != -1900:
                falhas.append(f"L46: duas despesas iguais SEM dedupe deveriam ser dois fatos ({r})")
        executar(falhas, "L46", l46)

        # ---- L47: despesa ADULTERADA com campo de trade -> ILEGIVEL ---------
        # A proibicao vale na escrita E na leitura. Um FEE persistido que ganhe
        # instrumentId/quantity/fees/taxes depois (import forjado, edicao manual)
        # nao pode virar numero: a ausencia desses campos e contratual, como a do
        # flowScope num trade. Sem este caso, remover a guarda de LEITURA
        # sobrevive a mutacao (MF-5b) — o sobrevivente denuncia o teste.
        def l47():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const out = {};
              for(const [campo, valor] of [['instrumentId','aldi_x'],['quantity','5'],
                                           ['fees',10],['taxes',5]]){
                S.alladin.transactions.length = 0;
                L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
                L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:1500, effectiveAt:'2026-01-31'});
                const fee = S.alladin.transactions.find(t => t.eventType==='FEE');
                fee[campo] = valor;                       // adulteracao pos-escrita
                const s = R.saldoDeCaixa(f.caixaXP);
                out[campo] = { av:s.available, m:s.issues.indexOf('ALD_TRANSACAO_ILEGIVEL')>=0 };
              }
              return out;
            }""")
            for campo, res in r.items():
                if res["av"] or not res["m"]:
                    falhas.append(f"L47 {campo}: despesa adulterada com campo de trade deveria ser ILEGIVEL ({res})")
        executar(falhas, "L47", l47)

        # ===== ALD-03 S4: ADJUSTMENT_CREDIT / ADJUSTMENT_DEBIT ===============
        # Ajuste de reconciliacao: diferenca de caixa SEM contraparte economica
        # identificavel. Nao e fluxo externo e nao e ganho/perda — e o unico
        # evento cujo valor nao pode ser conferido contra nada, e por isso o
        # `reason` faz parte da FORMA do registro, nao da conveniencia do autor.
        # Se existe lancamento errado IDENTIFICAVEL, o caminho e REVERSAL.

        # ---- L48/L49: CREDIT soma exato, DEBIT subtrai exato -----------------
        def l48_l49():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const cr = L.addTransaction({eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP,
                amount:2500, effectiveAt:'2026-01-31', reason:'diferenca de extrato conciliada em 31/01'});
              const s1 = R.saldoDeCaixa(f.caixaXP);
              const db = L.addTransaction({eventType:'ADJUSTMENT_DEBIT', cashAccountId:f.caixaXP,
                amount:700, effectiveAt:'2026-02-01', reason:'estorno de credito indevido do banco'});
              const s2 = R.saldoDeCaixa(f.caixaXP);
              const rec = S.alladin.transactions.find(t => t.transactionId === cr.recordId);
              // o ajuste NAO contamina outra conta de caixa
              const outra = R.saldoDeCaixa(f.caixaBTG);
              return { crOk:cr.ok && cr.persistido, dbOk:db.ok, s1:s1.amount, s2:s2.amount,
                       av:s2.available, status:rec.status, moeda:rec.currency,
                       motivo:rec.reason, outra:outra.amount, outraAv:outra.available };
            }""")
            if not r["crOk"] or not r["dbOk"]:
                falhas.append(f"L48/L49: ajuste recusado ({r})")
            if r["s1"] != 102500:
                falhas.append(f"L48: CREDIT deveria somar exato (100000+2500), veio {r['s1']}")
            if r["s2"] != 101800 or not r["av"]:
                falhas.append(f"L49: DEBIT deveria subtrair exato (102500-700), veio {r['s2']}")
            if r["status"] != "POSTED" or r["moeda"] != "BRL":
                falhas.append(f"L48: forma do registro fora do contrato ({r})")
            if r["motivo"] != "diferenca de extrato conciliada em 31/01":
                falhas.append(f"L48: reason nao foi persistido integro ({r['motivo']!r})")
            if r["outra"] != 0 or not r["outraAv"]:
                falhas.append(f"L48: ajuste vazou para outra conta de caixa ({r})")
        executar(falhas, "L48/L49", l48_l49)

        # ---- L50: reason OBRIGATORIO, campo proprio, distinto de note --------
        # `note` e comentario livre e opcional desde o S1; `reason` e a unica
        # coisa que torna auditavel um numero que ninguem pode conferir. Um nao
        # cobre o outro: note preenchida NAO satisfaz reason.
        def l50():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const base = {eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP,
                            amount:100, effectiveAt:'2026-03-01'};
              const semReason  = L.addTransaction({...base}).erro;
              const nulo       = L.addTransaction({...base, reason:null}).erro;
              const vazio      = L.addTransaction({...base, reason:''}).erro;
              const espacos    = L.addTransaction({...base, reason:'   '}).erro;
              const tabNl      = L.addTransaction({...base,
                reason:String.fromCharCode(9,10)+' '}).erro;   // tab + newline + espaco
              const naoTexto   = L.addTransaction({...base, reason:42}).erro;
              const soNote     = L.addTransaction({...base, note:'era uma nota'}).erro;
              const debitoSem  = L.addTransaction({...base, eventType:'ADJUSTMENT_DEBIT'}).erro;
              // ambos presentes: campos DISTINTOS, persistidos separadamente
              const ok = L.addTransaction({...base, reason:'ajuste de conciliacao',
                                                    note:'ver extrato pagina 3'});
              const rec = S.alladin.transactions.find(t => t.transactionId === ok.recordId);
              // `reason` so existe no ajuste: declara-lo noutro tipo e recusado
              const emDeposito = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP,
                amount:100, effectiveAt:'2026-03-02', reason:'porque sim'}).erro;
              return { semReason, nulo, vazio, espacos, tabNl, naoTexto, soNote, debitoSem,
                       okOk:ok.ok, motivo:rec.reason, nota:rec.note, emDeposito,
                       n:S.alladin.transactions.length };
            }""")
            for rotulo in ["semReason","nulo","vazio","espacos","tabNl","naoTexto","soNote","debitoSem"]:
                if r[rotulo] != "ALD_REASON_OBRIGATORIO":
                    falhas.append(f"L50 {rotulo}: ajuste sem reason legivel foi aceito ({r[rotulo]!r})")
            if not r["okOk"] or r["motivo"] != "ajuste de conciliacao" or r["nota"] != "ver extrato pagina 3":
                falhas.append(f"L50: reason e note deveriam ser campos distintos e independentes ({r})")
            if r["emDeposito"] != "ALD_REASON_NAO_PERMITIDO:DEPOSIT":
                falhas.append(f"L50: reason fora do ajuste deveria ser recusado ({r['emDeposito']!r})")
            if r["n"] != 1:
                falhas.append(f"L50: recusa deixou vestigio ({r['n']})")
        executar(falhas, "L50", l50)

        # ---- L51: campos proibidos recusados por PRESENCA --------------------
        # Mesma familia so-caixa da despesa: nada de papel, nada de vinculo. O
        # ajuste NAO aponta para transacao original — se ha lancamento errado
        # identificavel, o caminho e REVERSAL, e a confusao entre os dois e
        # exatamente o que a proibicao de `transactionRef` torna irrepresentavel.
        def l51():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const base = {eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP, amount:100,
                            effectiveAt:'2026-03-01', reason:'conciliacao'};
              const out = {};
              for(const [k,v] of [['instrumentId',f.petr4],['quantity','1'],['fees',10],['taxes',5],
                                  ['flowScope','EXTERNAL'],['transactionRef','aldtx_x'],
                                  ['reversalOf','aldtx_y'],['transactionId','aldtx_z'],
                                  ['sourceCashAccountId',f.caixaBTG],['destinationCashAccountId',f.caixaBTG]]){
                const d = {...base}; d[k]=v;
                out[k] = L.addTransaction(d).erro;
              }
              // presenca com valor undefined tambem e declaracao (S2/flowScope)
              const undef = L.addTransaction({...base, flowScope:undefined}).erro;
              const noDebito = L.addTransaction({...base, eventType:'ADJUSTMENT_DEBIT',
                                                 instrumentId:f.petr4}).erro;
              return { out, undef, noDebito, n:S.alladin.transactions.length };
            }""")
            for campo, erro in r["out"].items():
                if erro != 'ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA:'+campo:
                    falhas.append(f"L51 {campo}: ajuste aceitou campo proibido ({erro!r})")
            if r["undef"] != 'ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA:flowScope':
                falhas.append(f"L51: flowScope:undefined tambem e presenca ({r['undef']!r})")
            if r["noDebito"] != 'ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA:instrumentId':
                falhas.append(f"L51: proibicao nao vale para ADJUSTMENT_DEBIT ({r['noDebito']!r})")
            if r["n"] != 0:
                falhas.append(f"L51: recusa deixou vestigio ({r['n']})")
        executar(falhas, "L51", l51)

        # ---- L52: reversal de ajuste soma zero; reason do reversal e PROPRIO -
        # Reverter um ajuste e OUTRO ato sem contraparte. Copiar o reason do
        # original seria fabricar justificativa para um fato novo — por isso ele
        # vem do chamador, como effectiveAt e note, e nao entra na comparacao
        # cruzada do par (aldReversalConsistente).
        def l52():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const cr = L.addTransaction({eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP,
                amount:2500, effectiveAt:'2026-01-31', reason:'diferenca de extrato'});
              const antesCr = R.saldoDeCaixa(f.caixaXP).amount;
              const rvCr = L.reverseTransaction(cr.recordId, {effectiveAt:'2026-02-01',
                reason:'conciliacao refeita: a diferenca era do banco'});
              const posCr = R.saldoDeCaixa(f.caixaXP);
              const rev = S.alladin.transactions.find(t => t.transactionId === rvCr.recordId);
              const orig = S.alladin.transactions.find(t => t.transactionId === cr.recordId);
              const db = L.addTransaction({eventType:'ADJUSTMENT_DEBIT', cashAccountId:f.caixaXP,
                amount:700, effectiveAt:'2026-02-02', reason:'estorno'});
              const antesDb = R.saldoDeCaixa(f.caixaXP).amount;
              const rvDb = L.reverseTransaction(db.recordId, {effectiveAt:'2026-02-03'});
              const posDb = R.saldoDeCaixa(f.caixaXP);
              return { antesCr, posCr:posCr.amount, avCr:posCr.available,
                       revTipo:rev.reversedEventType, origStatus:orig.status,
                       revFs:Object.prototype.hasOwnProperty.call(rev,'flowScope'),
                       revMotivo:rev.reason, origMotivo:orig.reason,
                       dbRevOk:rvDb.ok, antesDb, posDb:posDb.amount, avDb:posDb.available,
                       revDbTemMotivo:Object.prototype.hasOwnProperty.call(
                         S.alladin.transactions.find(t => t.transactionId === rvDb.recordId),'reason') };
            }""")
            if r["antesCr"] != 102500 or r["posCr"] != 100000 or not r["avCr"]:
                falhas.append(f"L52: par CREDIT+reversal nao somou zero ({r})")
            if r["revTipo"] != "ADJUSTMENT_CREDIT" or r["origStatus"] != "REVERSED" or r["revFs"]:
                falhas.append(f"L52: reversal de ajuste fora do contrato ({r})")
            if r["revMotivo"] != "conciliacao refeita: a diferenca era do banco":
                falhas.append(f"L52: reason do reversal deveria ser PROPRIO ({r['revMotivo']!r})")
            if r["revMotivo"] == r["origMotivo"]:
                falhas.append("L52: reason do reversal foi copiado do original")
            if not r["dbRevOk"] or r["antesDb"] != 99300 or r["posDb"] != 100000 or not r["avDb"]:
                falhas.append(f"L52: par DEBIT+reversal nao somou zero ({r})")
            if r["revDbTemMotivo"]:
                falhas.append("L52: reversal sem reason do chamador nao deveria carimbar reason")
        executar(falhas, "L52", l52)

        # ---- L53: conta inativa recusa ajuste novo; historico e reversao valem
        def l53():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura, c = JPWAlladin.cadastro;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const cr = L.addTransaction({eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP,
                amount:2500, effectiveAt:'2026-01-31', reason:'diferenca de extrato'});
              c.setRecordStatus('cashaccount', f.caixaXP, 'INACTIVE');
              const novo = L.addTransaction({eventType:'ADJUSTMENT_DEBIT', cashAccountId:f.caixaXP,
                amount:100, effectiveAt:'2026-02-01', reason:'tentativa'}).erro;
              const saldo = R.saldoDeCaixa(f.caixaXP);
              const rv = L.reverseTransaction(cr.recordId, {effectiveAt:'2026-02-02', reason:'refeita'});
              return { novo, saldoAv:saldo.available, saldo:saldo.amount, revOk:rv.ok,
                       fim:R.saldoDeCaixa(f.caixaXP).amount };
            }""")
            if r["novo"] != "ALD_CASHACCOUNT_INATIVA":
                falhas.append(f"L53: conta inativa deveria recusar ajuste novo ({r['novo']!r})")
            if not r["saldoAv"] or r["saldo"] != 102500:
                falhas.append(f"L53: historico deixou de valer apos inativar ({r})")
            if not r["revOk"] or r["fim"] != 100000:
                falhas.append(f"L53: reversao de ajuste antigo deveria seguir permitida ({r})")
        executar(falhas, "L53", l53)

        # ---- L54: dedupe fail-closed tambem para ajuste ----------------------
        def l54():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const base = {eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP, amount:2500,
                            effectiveAt:'2026-01-31', reason:'diferenca de extrato'};
              const a = L.addTransaction({...base, dedupeKey:'concil-jan'});
              const b = L.addTransaction({...base, dedupeKey:'concil-jan'});
              // sem dedupe, dois ajustes iguais sao DOIS fatos legitimos
              const c1 = L.addTransaction({...base, amount:200, effectiveAt:'2026-02-01'});
              const c2 = L.addTransaction({...base, amount:200, effectiveAt:'2026-02-01'});
              return { aOk:a.ok, bErro:b.erro, c1:c1.ok, c2:c2.ok,
                       saldo:JPWAlladin.leitura.saldoDeCaixa(f.caixaXP).amount };
            }""")
            if not r["aOk"] or r["bErro"] != "ALD_DEDUPE_KEY_DUPLICADA":
                falhas.append(f"L54: dedupe de ajuste nao e fail-closed ({r})")
            if not (r["c1"] and r["c2"]) or r["saldo"] != 2900:
                falhas.append(f"L54: dois ajustes iguais SEM dedupe deveriam ser dois fatos ({r})")
        executar(falhas, "L54", l54)

        # ---- L55: forma persistida limpa; adulteracao pos-escrita e ILEGIVEL -
        def l55():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const cr = L.addTransaction({eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP,
                amount:2500, effectiveAt:'2026-01-31', reason:'diferenca de extrato'});
              const rec = S.alladin.transactions.find(t => t.transactionId === cr.recordId);
              const forma = Object.keys(rec).sort();
              const bruto = JSON.stringify(S.alladin);
              // adulteracao pos-escrita: campo de trade, flowScope ou reason removido
              const out = {};
              for(const passo of [['instrumentId','aldi_x'],['quantity','5'],['fees',10],
                                  ['taxes',5],['flowScope','EXTERNAL'],['reason',null],
                                  ['reason',''],['reason','   ']]){
                S.alladin.transactions.length = 0;
                const t2 = L.addTransaction({eventType:'ADJUSTMENT_DEBIT', cashAccountId:f.caixaXP,
                  amount:700, effectiveAt:'2026-02-01', reason:'estorno'});
                const alvo = S.alladin.transactions.find(t => t.transactionId === t2.recordId);
                if(passo[1]===null && passo[0]==='reason') delete alvo.reason; else alvo[passo[0]] = passo[1];
                const s = R.saldoDeCaixa(f.caixaXP);
                out[passo[0]+':'+String(passo[1])] = { av:s.available,
                  m:s.issues.indexOf('ALD_TRANSACAO_ILEGIVEL')>=0, amount:s.amount };
              }
              return { forma, out, vinculo: bruto.indexOf('transactionRef')>=0 };
            }""")
            esperado = ['amount','cashAccountId','currency','effectiveAt','eventType',
                        'reason','recordedAt','status','transactionId']
            if r["forma"] != esperado:
                falhas.append(f"L55: forma persistida do ajuste divergente ({r['forma']})")
            if r["vinculo"]:
                falhas.append("L55: ajuste persistiu vinculo economico a transacao")
            for caso, res in r["out"].items():
                if res["av"] or not res["m"]:
                    falhas.append(f"L55 {caso}: ajuste adulterado deveria ser ILEGIVEL ({res})")
        executar(falhas, "L55", l55)

        # ---- L56: COMPLETUDE do ALD_CASH_DELTA -------------------------------
        # Metade A — propriedade: todo eventType legivel e cash-affecting move o
        # saldo. Nenhum deles pode passar pelo acumulador valendo zero.
        def l56a():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              const casos = {
                DEPOSIT:    {eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'},
                WITHDRAWAL: {eventType:'WITHDRAWAL', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'},
                TRANSFER:   {eventType:'TRANSFER', sourceCashAccountId:f.caixaXP,
                             destinationCashAccountId:f.caixaBTG, amount:1000, effectiveAt:'2026-01-10',
                             flowScope:'INTERNAL'},
                BUY:        {eventType:'BUY', cashAccountId:f.caixaXP, instrumentId:f.petr4,
                             quantity:'10', amount:1000, effectiveAt:'2026-01-10'},
                SELL:       {eventType:'SELL', cashAccountId:f.caixaXP, instrumentId:f.petr4,
                             quantity:'10', amount:1000, effectiveAt:'2026-01-11'},
                FEE:        {eventType:'FEE', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'},
                TAX:        {eventType:'TAX', cashAccountId:f.caixaXP, amount:1000, effectiveAt:'2026-01-10'},
                ADJUSTMENT_CREDIT: {eventType:'ADJUSTMENT_CREDIT', cashAccountId:f.caixaXP,
                             amount:1000, effectiveAt:'2026-01-10', reason:'conciliacao'},
                ADJUSTMENT_DEBIT:  {eventType:'ADJUSTMENT_DEBIT', cashAccountId:f.caixaXP,
                             amount:1000, effectiveAt:'2026-01-10', reason:'conciliacao'},
              };
              const out = {};
              for(const [tipo, d] of Object.entries(casos)){
                S.alladin.transactions.length = 0;
                L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:500000, effectiveAt:'2026-01-01'});
                if(tipo==='SELL') L.addTransaction({eventType:'BUY', cashAccountId:f.caixaXP,
                  instrumentId:f.petr4, quantity:'10', amount:1000, effectiveAt:'2026-01-05'});
                const base = JPWAlladin.leitura.saldoDeCaixa(f.caixaXP);
                const res = L.addTransaction(d);
                const s = JPWAlladin.leitura.saldoDeCaixa(f.caixaXP);
                out[tipo] = { ok:res.ok, erro:res.erro, av:s.available,
                              delta:s.amount - base.amount,
                              ausente:s.issues.some(i => i.indexOf('ALD_CASH_DELTA_AUSENTE')===0) };
              }
              return out;
            }""")
            for tipo, res in r.items():
                if not res["ok"]:
                    falhas.append(f"L56a {tipo}: lancamento legitimo recusado ({res['erro']!r})")
                elif not res["av"] or res["ausente"]:
                    falhas.append(f"L56a {tipo}: saldo bloqueado por delta ausente ({res})")
                elif res["delta"] == 0:
                    falhas.append(f"L56a {tipo}: evento cash-affecting nao moveu o saldo (delta 0 implicito)")
        executar(falhas, "L56a", l56a)

        # Metade B — a guarda: tipo LEGIVEL sem entrada em ALD_CASH_DELTA vira
        # BLOCKING com diagnostico proprio, NUNCA saldo `available` com delta 0.
        # Esta e a unica falha do modulo capaz de produzir NUMERO PLAUSIVEL E
        # FALSO em vez de recusa, entao ela precisa de prova direta. A tabela nao
        # e exportada; a sonda injeta o modulo com UMA entrada removida numa
        # pagina isolada. Sem este caso, MA-7 (volta do `: 0`) sobrevive.
        def l56b():
            fonte = MODULO.read_text(encoding="utf-8")
            alvo = "  TAX:        (tx, id) => (tx.cashAccountId===id ? -tx.amount : 0),\n"
            if fonte.count(alvo) != 1:
                falhas.append("L56b: ancora da entrada TAX em ALD_CASH_DELTA nao encontrada")
                return
            p2 = browser.new_page()
            p2.on("pageerror", lambda e: falhas.append(f"L56b pageerror: {e}"))
            p2.route("**/*", abortar)
            p2.goto("about:blank")
            p2.add_script_tag(content=PRELUDE)
            p2.add_script_tag(content=fonte.replace(alvo, "", 1))
            r = p2.evaluate("""() => {
              const f = fixture(), L = JPWAlladin.ledger, R = JPWAlladin.leitura;
              L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100000, effectiveAt:'2026-01-10'});
              const tax = L.addTransaction({eventType:'TAX', cashAccountId:f.caixaXP, amount:500, effectiveAt:'2026-01-31'});
              const s = R.saldoDeCaixa(f.caixaXP);
              // reversal orfao segue com o SEU proprio diagnostico
              S.alladin.transactions.length = 0;
              const dep = L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:100, effectiveAt:'2026-01-10'});
              const rv  = L.reverseTransaction(dep.recordId, {effectiveAt:'2026-01-11'});
              S.alladin.transactions = S.alladin.transactions.filter(x => x.transactionId !== dep.recordId);
              const o = R.saldoDeCaixa(f.caixaXP);
              return { escreveu:tax.ok, av:s.available, amount:s.amount, issues:s.issues,
                       ausente:s.issues.indexOf('ALD_CASH_DELTA_AUSENTE:'+tax.recordId)>=0,
                       orfaoAv:o.available,
                       orfao:o.issues.indexOf('ALD_REVERSAL_ORFAO:'+rv.recordId)>=0,
                       orfaoNaoAusente:!o.issues.some(i => i.indexOf('ALD_CASH_DELTA_AUSENTE')===0) };
            }""")
            p2.close()
            if not r["escreveu"]:
                falhas.append("L56b: a sonda nao conseguiu persistir o TAX legivel")
            if r["av"]:
                falhas.append(f"L56b: tipo legivel SEM cash delta produziu saldo disponivel ({r})")
            if r["amount"] is not None and r["amount"] == 100000:
                falhas.append("L56b: delta ausente virou zero implicito — saldo plausivel e FALSO")
            if not r["ausente"]:
                falhas.append(f"L56b: faltou ALD_CASH_DELTA_AUSENTE no diagnostico ({r['issues']})")
            if r["orfaoAv"] or not r["orfao"] or not r["orfaoNaoAusente"]:
                falhas.append(f"L56b: reversal orfao perdeu o diagnostico proprio ({r})")
        executar(falhas, "L56b", l56b)

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
              S.alladin.schemaVersion = 7;
              const bloqueado = {
                add: L.addTransaction({eventType:'DEPOSIT', cashAccountId:f.caixaXP, amount:1, effectiveAt:'2026-01-10'}).erro,
                rev: L.reverseTransaction('aldtx_x', {effectiveAt:'2026-01-10'}).erro,
                gate: JPWAlladin.writeBlockReason(),
              };
              S.alladin.schemaVersion = 6;
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
    print("alladin_ledger_test PASS (L1-L56: deposito/saque e saldo derivado; transferencia interna"
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
          "quantity canonica de grafia unica, instrumentFamily congelada apos referencia; "
          "HARDENING read-side: id/dedupe duplicados, dois reversals do mesmo original, "
          "pareamento status<->reversal, saldo sob schema futuro e container nao-array viram "
          "BLOCKING, enquanto fato legitimo duplicado sem dedupe segue somando; AMENDMENT: id "
          "canonico duplicado (cash/instrument/account/asset/tx) bloqueia leitura E recusa escrita; "
          "S3: FEE/TAX standalone debitam exato, revertem para zero, nao tem flowScope nem "
          "vinculo a trade, e recusam todo campo de trade — dupla contagem irrepresentavel; "
          "S4: ADJUSTMENT_CREDIT/DEBIT como diferenca de caixa sem contraparte, com reason "
          "obrigatorio e proprio, zero vinculo e zero campo de trade, revertendo para zero; "
          "e a COMPLETUDE do cash delta — tipo legivel sem entrada na tabela vira BLOCKING "
          "com ALD_CASH_DELTA_AUSENTE em vez de zero implicito)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
