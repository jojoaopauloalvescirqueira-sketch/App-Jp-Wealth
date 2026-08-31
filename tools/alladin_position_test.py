#!/usr/bin/env python3
"""Alladin ALD-04 S1 — POSITION QUANTITY ENGINE: posicao derivada do ledger.

Mesmo contrato de harness do alladin_ledger_test: Chromium ISOLADO — sem app,
sem DOM de producao, sem estado real, sem network. A pagina e about:blank, toda
requisicao e abortada e contada, e o unico codigo injetado e um prelude de
stubs seguido do MODULO SOB TESTE lido do disco.

O que esta suite prova (P1-P17):
  P1  BUY unico vira UMA posicao (instrumentId+accountId), quantity byte-igual
  P2  BUY+BUY soma decimal exata
  P3  BUY+SELL parcial subtrai exato
  P4  posicao que fecha em zero SAI da colecao (DH-04-2) — available segue true
  P5  reversal de BUY neutraliza exatamente (posicao some)
  P6  reversal de SELL idem, sentido oposto
  P7  posicoes multiplas na mesma custodia (instrumentos distintos)
  P8  mesmo instrumento em Accounts diferentes = DUAS posicoes
  P9  duas CashAccounts do MESMO Account = UMA posicao (custodia e o Account)
  P10 precisao decimal exata + canonicalizacao ('0.1'+'0.2'='0.3'; '0.5'+'0.5'='1')
  P11 ledger/reversal adulterado -> BLOCKING, nunca posicao parcial
  P12 custodia/orfandade cadastral -> BLOCKING
  P13 resultado negativo e string assinada fiel ('-5'), SEM semantica de short
  P14 schema futuro com so eventos conhecidos -> BLOCKING (guard explicita)
  P15 mesma economia em ordem fisica diferente -> saida identica (determinismo)
  P16 derivado que ultrapassa 64 chars sai EXATO — sem truncar, sem recusar
  P17 moeda trade/caixa/instrumento divergente -> BLOCKING
  P18 BUY id duplicado -> BLOCKING (posicao dobraria)            [hardening read-side]
  P19 container transactions nao-array -> BLOCKING ('vazio confiante' e falso)
  P20 (H2) instrumentId duplicado -> posicao BLOCKING + BUY RECUSADO (write gate)
  P21 (H3) accountId duplicado    -> posicao BLOCKING + escrita RECUSADA (write gate)
  P22 (S3) FEE/TAX standalone NAO movem posicao; BUY mantem fees/taxes embutidos
"""
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODULO = ROOT / "src/js/10-domain/13-alladin.js"

PRELUDE = """
window.__stub = { saves: 0, saveResult: true, logs: [] };
var S = { alladin: { schemaVersion: 5, reportingCurrency: 'BRL',
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
// Fixture: duas corretoras; XP com DUAS caixas BRL e uma USD; BTG com uma BRL.
// Instrumentos: PETR4 (BRL) e AAPL (USD).
function fixture(){
  S.alladin = { schemaVersion: 5, reportingCurrency: 'BRL', instruments: [], assets: [],
                accounts: [], cashAccounts: [], transactions: [] };
  S.dataGovernance.changeLog = [];
  window.__stub.saves = 0; window.__stub.saveResult = true;
  const c = JPWAlladin.cadastro;
  const xp  = c.addAccount({ name:'XP',  institution:'XP',  accountType:'BROKERAGE' }).recordId;
  const btg = c.addAccount({ name:'BTG', institution:'BTG', accountType:'BROKERAGE' }).recordId;
  return {
    xp, btg,
    caixaXP:  c.addCashAccount({ accountId: xp,  currency:'BRL' }).recordId,
    caixaXP2: c.addCashAccount({ accountId: xp,  currency:'BRL' }).recordId,
    caixaBTG: c.addCashAccount({ accountId: btg, currency:'BRL' }).recordId,
    caixaUSD: c.addCashAccount({ accountId: xp,  currency:'USD' }).recordId,
    petr4:   c.addInstrument({ name:'Petrobras PN', symbol:'PETR4', currency:'BRL',
                               instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL' }).recordId,
    aaplUsd: c.addInstrument({ name:'Apple', symbol:'AAPL', currency:'USD',
                               instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL' }).recordId,
  };
}
// Atalho de compra/venda usado pelas sondas.
function trade(tipo, inst, caixa, q, amount){
  return JPWAlladin.ledger.addTransaction({ eventType:tipo, instrumentId:inst,
    cashAccountId:caixa, quantity:q, amount:(amount||100), effectiveAt:'2026-03-01' });
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

        # ---- P1: BUY unico ---------------------------------------------------
        def p1():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '100');
              const p = JPWAlladin.leitura.posicoes();
              return { ok:p.available, q:p.quality, n:p.positions.length,
                       pos:p.positions[0], xp:f.xp, petr4:f.petr4,
                       congelado:Object.isFrozen(p) && Object.isFrozen(p.positions),
                       lerNaoMuta: S.alladin.transactions.length===1 };
            }""")
            if not r["ok"] or r["q"] != "OK" or r["n"] != 1:
                falhas.append(f"P1: BUY unico nao virou UMA posicao ({r})")
            pos = r["pos"]
            if pos["instrumentId"] != r["petr4"] or pos["accountId"] != r["xp"] \
               or pos["quantity"] != "100" or pos["consideradas"] != 1:
                falhas.append(f"P1: forma da posicao divergente ({pos})")
            if not r["congelado"] or not r["lerNaoMuta"]:
                falhas.append(f"P1: retorno nao congelado ou leitura mutou ({r})")
        executar(falhas, "P1", p1)

        # ---- P2/P3: soma e subtracao exatas ----------------------------------
        def p2_p3():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '1.5');
              trade('BUY', f.petr4, f.caixaXP, '0.25');
              const soma = JPWAlladin.leitura.posicoes().positions[0].quantity;
              trade('SELL', f.petr4, f.caixaXP, '0.75');
              const sub = JPWAlladin.leitura.posicoes().positions[0];
              return { soma, sub:sub.quantity, consideradas:sub.consideradas };
            }""")
            if r["soma"] != "1.75":
                falhas.append(f"P2: '1.5'+'0.25' deveria dar '1.75' ({r['soma']!r})")
            if r["sub"] != "1" or r["consideradas"] != 3:
                falhas.append(f"P3: subtracao parcial divergente ({r})")
        executar(falhas, "P2/P3", p2_p3)

        # ---- P4: fechou em zero -> AUSENTE, available segue true -------------
        def p4():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '2.5');
              trade('SELL', f.petr4, f.caixaXP, '2.5');
              trade('BUY', f.aaplUsd, f.caixaUSD, '1');   // outra posicao viva
              const p = JPWAlladin.leitura.posicoes();
              return { ok:p.available, n:p.positions.length,
                       ids:p.positions.map(x=>x.instrumentId), aapl:f.aaplUsd };
            }""")
            if not r["ok"] or r["n"] != 1 or r["ids"] != [r["aapl"]]:
                falhas.append(f"P4: posicao zerada deveria SAIR da colecao (DH-04-2) ({r})")
        executar(falhas, "P4", p4)

        # ---- P5/P6: reversal neutraliza exatamente ---------------------------
        def p5_p6():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const b = trade('BUY', f.petr4, f.caixaXP, '2.5');
              const antes = JPWAlladin.leitura.posicoes().positions.length;
              L.reverseTransaction(b.recordId, {effectiveAt:'2026-03-02'});
              const aposB = JPWAlladin.leitura.posicoes();
              const s = trade('SELL', f.petr4, f.caixaXP2, '1');
              const meio = JPWAlladin.leitura.posicoes().positions[0].quantity;
              L.reverseTransaction(s.recordId, {effectiveAt:'2026-03-03'});
              const aposS = JPWAlladin.leitura.posicoes();
              return { antes, bOk:aposB.available, bN:aposB.positions.length,
                       meio, sOk:aposS.available, sN:aposS.positions.length };
            }""")
            if r["antes"] != 1 or not r["bOk"] or r["bN"] != 0:
                falhas.append(f"P5: reversal de BUY nao neutralizou exatamente ({r})")
            if r["meio"] != "-1" or not r["sOk"] or r["sN"] != 0:
                falhas.append(f"P6: reversal de SELL nao neutralizou exatamente ({r})")
        executar(falhas, "P5/P6", p5_p6)

        # ---- P7/P8/P9: identidade instrumentId+accountId ---------------------
        def p7_p8_p9():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '10');     // petr4 @ XP (caixa 1)
              trade('BUY', f.petr4, f.caixaXP2, '5');     // petr4 @ XP (caixa 2) -> MESMA posicao
              trade('BUY', f.petr4, f.caixaBTG, '7');     // petr4 @ BTG -> OUTRA posicao
              trade('BUY', f.aaplUsd, f.caixaUSD, '3');   // aapl @ XP
              const p = JPWAlladin.leitura.posicoes();
              return { ok:p.available, n:p.positions.length,
                       lista:p.positions.map(x => [x.instrumentId, x.accountId, x.quantity, x.consideradas]),
                       f:{xp:f.xp, btg:f.btg, petr4:f.petr4, aapl:f.aaplUsd} };
            }""")
            if not r["ok"] or r["n"] != 3:
                falhas.append(f"P7/P8/P9: esperava 3 posicoes ({r})")
            f = r["f"]
            por_chave = {(l[0], l[1]): (l[2], l[3]) for l in r["lista"]}
            if por_chave.get((f["petr4"], f["xp"])) != ("15", 2):
                falhas.append(f"P9: duas caixas do MESMO Account deveriam somar UMA posicao 15/2 ({r['lista']})")
            if por_chave.get((f["petr4"], f["btg"])) != ("7", 1):
                falhas.append(f"P8: mesmo instrumento em outra custodia deveria ser posicao propria ({r['lista']})")
            if por_chave.get((f["aapl"], f["xp"])) != ("3", 1):
                falhas.append(f"P7: posicao de outro instrumento na mesma custodia ausente ({r['lista']})")
        executar(falhas, "P7/P8/P9", p7_p8_p9)

        # ---- P10: precisao exata e canonicalizacao ---------------------------
        def p10():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '0.1');
              trade('BUY', f.petr4, f.caixaXP, '0.2');
              const a = JPWAlladin.leitura.posicoes().positions[0].quantity;
              const f2 = fixture();
              trade('BUY', f2.petr4, f2.caixaXP, '0.5');
              trade('BUY', f2.petr4, f2.caixaXP, '0.5');
              const b = JPWAlladin.leitura.posicoes().positions[0].quantity;
              const f3 = fixture();
              trade('BUY', f3.petr4, f3.caixaXP, '1.000000001');
              trade('BUY', f3.petr4, f3.caixaXP, '0.999999999');
              const c = JPWAlladin.leitura.posicoes().positions[0].quantity;
              return { a, b, c };
            }""")
            if r["a"] != "0.3":
                falhas.append(f"P10: '0.1'+'0.2' deveria dar '0.3' EXATO ({r['a']!r}) — float vazou?")
            if r["b"] != "1":
                falhas.append(f"P10: '0.5'+'0.5' deveria canonicalizar para '1' ({r['b']!r})")
            if r["c"] != "2":
                falhas.append(f"P10: fracoes longas alinhadas deveriam dar '2' ({r['c']!r})")
        executar(falhas, "P10", p10)

        # ---- P11: adulteracao -> BLOCKING ------------------------------------
        def p11():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              const b = trade('BUY', f.petr4, f.caixaXP, '2.5');
              const rv = L.reverseTransaction(b.recordId, {effectiveAt:'2026-03-02'});
              S.alladin.transactions.find(t => t.transactionId === rv.recordId).quantity = '999';
              const par = JPWAlladin.leitura.posicoes();
              const f2 = fixture();
              trade('BUY', f2.petr4, f2.caixaXP, '1');
              S.alladin.transactions[0].quantity = '01';   // registro ilegivel
              const ileg = JPWAlladin.leitura.posicoes();
              return { par:{ok:par.available, n:par.positions.length,
                            marcado:par.issues.some(i => i.indexOf('ALD_REVERSAL_INCONSISTENTE')===0)},
                       ileg:{ok:ileg.available, n:ileg.positions.length,
                             marcado:ileg.issues.indexOf('ALD_TRANSACAO_ILEGIVEL')>=0} };
            }""")
            for nome, res in r.items():
                if res["ok"] or res["n"] != 0 or not res["marcado"]:
                    falhas.append(f"P11 {nome}: adulteracao nao virou BLOCKING vazio ({res})")
        executar(falhas, "P11", p11)

        # ---- P12: orfandade cadastral -> BLOCKING ----------------------------
        def p12():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '1');
              S.alladin.transactions[0].cashAccountId = 'aldc_fantasma';
              const caixa = JPWAlladin.leitura.posicoes();
              const f2 = fixture();
              trade('BUY', f2.petr4, f2.caixaXP, '1');
              S.alladin.cashAccounts.find(c => c.cashAccountId === f2.caixaXP).accountId = 'aldacc_fantasma';
              const conta = JPWAlladin.leitura.posicoes();
              const f3 = fixture();
              trade('BUY', f3.petr4, f3.caixaXP, '1');
              S.alladin.transactions[0].instrumentId = 'aldi_fantasma';
              const inst = JPWAlladin.leitura.posicoes();
              return {
                caixa:{ok:caixa.available, m:caixa.issues.some(i=>i.indexOf('ALD_CASHACCOUNT_NAO_ENCONTRADA')===0)},
                conta:{ok:conta.available, m:conta.issues.some(i=>i.indexOf('ALD_ACCOUNT_NAO_ENCONTRADA')===0)},
                inst:{ok:inst.available, m:inst.issues.some(i=>i.indexOf('ALD_INSTRUMENT_NAO_ENCONTRADO')===0)} };
            }""")
            for nome, res in r.items():
                if res["ok"] or not res["m"]:
                    falhas.append(f"P12 {nome}: orfandade nao virou BLOCKING ({res})")
        executar(falhas, "P12", p12)

        # ---- P13: negativo fiel, sem semantica de short ----------------------
        def p13():
            r = ev("""() => {
              const f = fixture();
              const s = trade('SELL', f.petr4, f.caixaXP, '5');
              const inteiro = JPWAlladin.leitura.posicoes().positions[0];
              const f2 = fixture();
              trade('SELL', f2.petr4, f2.caixaXP, '0.25');
              const frac = JPWAlladin.leitura.posicoes().positions[0].quantity;
              return { ok:s.ok, q:inteiro.quantity, frac,
                       extras:Object.keys(inteiro).sort() };
            }""")
            if not r["ok"] or r["q"] != "-5" or r["frac"] != "-0.25":
                falhas.append(f"P13: negativo deveria ser string assinada fiel ({r})")
            if r["extras"] != ["accountId", "consideradas", "instrumentId", "quantity"]:
                falhas.append(f"P13: DTO ganhou campo alem do contrato (short/negative/side?) ({r['extras']})")
        executar(falhas, "P13", p13)

        # ---- P14: schema futuro com eventos conhecidos -> BLOCKING -----------
        def p14():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '1');
              S.alladin.schemaVersion = 6;
              const p = JPWAlladin.leitura.posicoes();
              S.alladin.schemaVersion = 5;
              const depois = JPWAlladin.leitura.posicoes();
              return { ok:p.available, n:p.positions.length,
                       marcado:p.issues.indexOf('READ_ONLY_FUTURE_SCHEMA')>=0,
                       voltou:depois.available && depois.positions.length===1 };
            }""")
            if r["ok"] or r["n"] != 0 or not r["marcado"]:
                falhas.append(f"P14: schema futuro deveria BLOQUEAR mesmo com eventos conhecidos ({r})")
            if not r["voltou"]:
                falhas.append(f"P14: engine nao voltou ao normal na versao corrente ({r})")
        executar(falhas, "P14", p14)

        # ---- P15: determinismo sob ordem fisica diferente --------------------
        def p15():
            r = ev("""() => {
              const f = fixture();
              trade('BUY',  f.petr4, f.caixaXP,  '10');
              trade('SELL', f.petr4, f.caixaXP2, '4');
              trade('BUY',  f.aaplUsd, f.caixaUSD, '2');
              trade('BUY',  f.petr4, f.caixaBTG, '1');
              const antes = JSON.stringify(JPWAlladin.leitura.posicoes());
              // mesma economia, ordem fisica invertida
              S.alladin.transactions.reverse();
              const depois = JSON.stringify(JPWAlladin.leitura.posicoes());
              return { igual: antes === depois, antes };
            }""")
            if not r["igual"]:
                falhas.append("P15: a ordem fisica do array vazou para o resultado")
        executar(falhas, "P15", p15)

        # ---- P16: derivado alem de 64 chars — exato --------------------------
        def p16():
            r = ev("""() => {
              const f = fixture();
              const grande = '9'.repeat(64);        // input valido no teto tecnico
              trade('BUY', f.petr4, f.caixaXP, grande);
              trade('BUY', f.petr4, f.caixaXP, grande);
              const q = JPWAlladin.leitura.posicoes().positions[0].quantity;
              // 2*(10^64-1) = 1 seguido de '9'*63 e '8' — 65 digitos exatos
              const esperado = '1' + '9'.repeat(63) + '8';
              return { q, esperado, len:q.length };
            }""")
            if r["q"] != r["esperado"] or r["len"] != 65:
                falhas.append(f"P16: derivado >64 chars deveria sair EXATO ({r['len']}, {r['q'][:20]}...)")
        executar(falhas, "P16", p16)

        # ---- P17: moeda divergente -> BLOCKING -------------------------------
        def p17():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '1');
              S.alladin.transactions[0].currency = 'USD';   // trade != caixa
              const tx = JPWAlladin.leitura.posicoes();
              const f2 = fixture();
              trade('BUY', f2.petr4, f2.caixaXP, '1');
              S.alladin.instruments.find(i => i.instrumentId === f2.petr4).currency = 'USD'; // instrumento != caixa
              const inst = JPWAlladin.leitura.posicoes();
              return { tx:{ok:tx.available, m:tx.issues.some(i=>i.indexOf('ALD_MOEDA_DIVERGENTE')===0)},
                       inst:{ok:inst.available, m:inst.issues.some(i=>i.indexOf('ALD_MOEDA_DIVERGENTE')===0)} };
            }""")
            for nome, res in r.items():
                if res["ok"] or not res["m"]:
                    falhas.append(f"P17 {nome}: divergencia de moeda nao virou BLOCKING ({res})")
        executar(falhas, "P17", p17)

        # ---- P18: BUY id duplicado -> posicao BLOCKING (nao dobra) -----------
        # Integridade estrutural na leitura: um BUY clonado (mesmo id) dobraria a
        # quantidade sem que aldTxLegivel, que so olha um registro, percebesse.
        def p18():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '100');
              S.alladin.transactions.push(JSON.parse(JSON.stringify(S.alladin.transactions[0])));
              const p = JPWAlladin.leitura.posicoes();
              return { av:p.available, n:p.positions.length,
                       m:p.issues.some(i=>i.indexOf('ALD_TRANSACTION_ID_DUPLICADO')===0) };
            }""")
            if r["av"] or r["n"] != 0 or not r["m"]:
                falhas.append(f"P18: BUY id duplicado deveria BLOQUEAR (posicao 200 falsa) ({r})")
        executar(falhas, "P18", p18)

        # ---- P19: container transactions NAO-array -> BLOCKING ---------------
        def p19():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '10');
              S.alladin.transactions = {corrompido:true};
              const p = JPWAlladin.leitura.posicoes();
              S.alladin.transactions = [];
              return { av:p.available, n:p.positions.length,
                       m:p.issues.indexOf('ALD_TRANSACOES_ILEGIVEIS')>=0 };
            }""")
            if r["av"] or r["n"] != 0 or not r["m"]:
                falhas.append(f"P19: container nao-array deveria BLOQUEAR ('vazio confiante' e falso) ({r})")
        executar(falhas, "P19", p19)

        # ---- P20 (H2): instrumentId duplicado -> posicao BLOCKING + BUY recusado
        def p20():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '10');
              S.alladin.instruments.push(JSON.parse(JSON.stringify(S.alladin.instruments.find(i=>i.instrumentId===f.petr4))));
              const p = JPWAlladin.leitura.posicoes();
              const w = JPWAlladin.ledger.addTransaction({eventType:'BUY', instrumentId:f.petr4,
                cashAccountId:f.caixaXP, quantity:'1', amount:100, effectiveAt:'2026-02-02'});
              return { av:p.available, m:p.issues.some(i=>i.indexOf('ALD_ID_DUPLICADO:instruments')===0),
                       wErr:w.erro, wPers:w.persistido };
            }""")
            if r["av"] or not r["m"]:
                falhas.append(f"P20: instrumentId duplicado nao bloqueou a posicao ({r})")
            if not (r["wErr"] or '').startswith('ALD_INTEGRIDADE_ESTRUTURAL') or r["wPers"]:
                falhas.append(f"P20: BUY sobre instrumento de identidade ambigua nao foi recusado ({r})")
        executar(falhas, "P20", p20)

        # ---- P21 (H3): accountId duplicado -> posicao BLOCKING + write recusado
        def p21():
            r = ev("""() => {
              const f = fixture();
              trade('BUY', f.petr4, f.caixaXP, '10');
              S.alladin.accounts.push(JSON.parse(JSON.stringify(S.alladin.accounts.find(x=>x.accountId===f.xp))));
              const p = JPWAlladin.leitura.posicoes();
              const w = JPWAlladin.cadastro.addInstrument({name:'Q', symbol:'VALE3', currency:'BRL',
                instrumentFamily:'EQUITY_LIKE', assetClass:'RENDA_VARIAVEL'});
              return { av:p.available, m:p.issues.some(i=>i.indexOf('ALD_ID_DUPLICADO:accounts')===0),
                       wErr:w.erro };
            }""")
            if r["av"] or not r["m"]:
                falhas.append(f"P21: accountId duplicado nao bloqueou a posicao ({r})")
            if not (r["wErr"] or '').startswith('ALD_INTEGRIDADE_ESTRUTURAL'):
                falhas.append(f"P21: escrita sobre accountId duplicado nao foi recusada ({r})")
        executar(falhas, "P21", p21)

        # ---- P22: FEE/TAX standalone NAO movem posicao (so-caixa) -----------
        # E a prova de que a despesa e economicamente separada do papel: o BUY
        # continua com seus fees/taxes EMBUTIDOS, e a despesa standalone nao
        # existe como perna de papel nem se mistura ao trade.
        def p22():
            r = ev("""() => {
              const f = fixture(), L = JPWAlladin.ledger;
              trade('BUY', f.petr4, f.caixaXP, '100', 300000);
              const buy = S.alladin.transactions[0];
              L.addTransaction({eventType:'FEE', cashAccountId:f.caixaXP, amount:1500, effectiveAt:'2026-03-02'});
              L.addTransaction({eventType:'TAX', cashAccountId:f.caixaXP, amount:500, effectiveAt:'2026-03-02'});
              const p = JPWAlladin.leitura.posicoes();
              const fee = S.alladin.transactions.find(t => t.eventType==='FEE');
              return { av:p.available, n:p.positions.length, q:(p.positions[0]||{}).quantity,
                       consideradas:(p.positions[0]||{}).consideradas,
                       buyTemFees:Object.prototype.hasOwnProperty.call(buy,'fees') &&
                                  Object.prototype.hasOwnProperty.call(buy,'taxes'),
                       feeTemInstrumento:Object.prototype.hasOwnProperty.call(fee,'instrumentId'),
                       feeTemRef:Object.prototype.hasOwnProperty.call(fee,'transactionRef') ||
                                 Object.prototype.hasOwnProperty.call(fee,'reversalOf') };
            }""")
            if not r["av"] or r["n"] != 1 or r["q"] != "100":
                falhas.append(f"P22: FEE/TAX moveram a posicao ({r})")
            if r["consideradas"] != 1:
                falhas.append(f"P22: despesa entrou na contagem da posicao ({r['consideradas']})")
            if not r["buyTemFees"]:
                falhas.append("P22: BUY perdeu os fees/taxes embutidos — trade NAO pode ser decomposto")
            if r["feeTemInstrumento"] or r["feeTemRef"]:
                falhas.append(f"P22: despesa standalone ganhou instrumento ou vinculo ({r})")
        executar(falhas, "P22", p22)

        browser.close()

    if bloqueadas["n"]:
        falhas.append(f"harness: o modulo tentou {bloqueadas['n']} requisicao(oes) de rede")
    if falhas:
        print("ALLADIN POSITION TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("alladin_position_test PASS (P1-P22: posicao derivada por instrumentId+accountId; "
          "soma/subtracao decimal exata em BigInt com canonicalizacao; zero sai da colecao; "
          "reversal neutraliza exatamente apos consistencia do par; duas caixas do mesmo Account "
          "somam UMA posicao e custodias distintas separam; negativo fiel sem semantica de short; "
          "adulteracao, orfandade cadastral, moeda divergente e schema futuro viram BLOCKING; "
          "saida deterministica; derivado alem de 64 chars sai exato; HARDENING: id duplicado e "
          "container nao-array bloqueiam; AMENDMENT: id canonico duplicado bloqueia posicao E recusa escrita; "
          "S3: FEE/TAX standalone nao movem posicao e o BUY mantem fees/taxes embutidos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
