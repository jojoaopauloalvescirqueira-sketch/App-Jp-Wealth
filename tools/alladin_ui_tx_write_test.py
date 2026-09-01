#!/usr/bin/env python3
"""Alladin ALD-05-S2 — criacao de lancamento pela UI (TX-A..TX-N).

A UI coleta campos e faz UMA chamada a ledger.addTransaction. O que esta suite
defende nao e "o modal grava" — e que a UI jamais vire autoridade economica:
payload sem campos inventados, dinheiro so por money.parse, quantity verbatim,
recusa nunca vira sucesso, rascunho sobrevive a recusa, e o convite a escrita
desaparece exatamente onde a leitura ja recusou o agregado.

  TX-A  porta unica: um submit == uma chamada a addTransaction; zero save direto
  TX-B  payload sem campos do dominio (currency/flowScope/unitPrice/transactionId/
        recordedAt/status/dedupeKey) — no que a UI ENVIA e no persistido
  TX-C  dinheiro por money.parse: "1.234,56" vira 123456 minor — parseFloat morre
  TX-D  quantity verbatim: "1.50" recusada SEM correcao silenciosa; "1.5" byte-igual;
        "-5" recusada (entrada nao admite sinal — nada inventado)
  TX-E  os NOVE tipos criados pelo modal real
  TX-F  ajuste: reason persistido, note independente, flowScope ausente
  TX-G  transfer: duas pernas; mesma conta e moedas diferentes recusadas PELO
        DOMINIO; o destino NAO e pre-filtrado por moeda na UI
  TX-H  recusa: modal aberto, draft intacto, erro in-place, zero persistencia
  TX-I  double submit nao duplica
  TX-J  cancelar: S e localStorage byte-identicos, zero chamadas
  TX-K  write gate: CTA disabled sob schema futuro; submit tardio recusado sem
        falso sucesso
  TX-L  sentinela: BLOCKING nao convida escrita (CTA ausente); EMPTY legitimo convida
  TX-M  pos-sucesso: Lancamentos/Saldos/Posicoes refletem VIA READ-MODELS — o
        teste compara contra o dominio, jamais recalcula
  TX-N  datas fixas deterministicas; a suite nao depende de mes/data corrente
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
PRONTO = ("() => typeof S === 'object' && typeof save === 'function' "
          "&& window.JPWAlladinUI && window.JPWAlladin")


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


CONTEXTOS = []


def abrir(browser, url):
    ctx = browser.new_context(viewport={"width": 1440, "height": 950},
                              service_workers="block")   # QA-D1
    CONTEXTOS.append(ctx)
    ctx.add_init_script("window.__onbShown=true;")
    page = ctx.new_page()
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(PRONTO)
    page.wait_for_timeout(350)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return ctx, page, erros


# Cadastro semeado PELO DOMINIO; ids ficam em window.__ids. Duas contas BRL
# (para TRANSFER legitimo), uma USD (para a recusa de moeda) e um instrumento.
SEMEAR = """() => {
  const c=JPWAlladin.cadastro;
  const xp=c.addAccount({name:'XP',institution:'XP',accountType:'BROKERAGE'}).recordId;
  const btg=c.addAccount({name:'BTG',institution:'BTG',accountType:'BROKERAGE'}).recordId;
  window.__ids={
    cx:c.addCashAccount({accountId:xp,currency:'BRL'}).recordId,
    cb:c.addCashAccount({accountId:btg,currency:'BRL'}).recordId,
    cu:c.addCashAccount({accountId:xp,currency:'USD'}).recordId,
    pe:c.addInstrument({name:'Petrobras PN',symbol:'PETR4',currency:'BRL',
      instrumentFamily:'EQUITY_LIKE',assetClass:'RENDA_VARIAVEL'}).recordId,
  };
  JPWNavigation.navigate('alladin'); JPWAlladinUI.selectView('ledger');
  return window.__ids;
}"""

# Instrumentacao da porta: conta chamadas e captura o payload EXATO que a UI
# envia — a prova de TX-A/TX-B nao pode depender so da forma persistida, porque
# o dominio derruba/deriva campos; o que interessa e o que a UI AFIRMOU.
INSTRUMENTAR = """() => {
  window.__port={calls:0, payloads:[], saves:0};
  const orig=JPWAlladin.ledger.addTransaction;
  window.__origAdd=orig;
  JPWAlladin.ledger.addTransaction=function(d){
    window.__port.calls++; window.__port.payloads.push(JSON.parse(JSON.stringify(d)));
    return orig(d);
  };
  const os_=window.save; window.__origSave=os_;
  window.save=function(){ window.__port.saves++; return os_.apply(this,arguments); };
}"""
RESTAURAR = """() => {
  JPWAlladin.ledger.addTransaction=window.__origAdd;
  window.save=window.__origSave;
}"""

CAMPOS_PROIBIDOS_NO_PAYLOAD = ("currency", "flowScope", "unitPrice",
                               "transactionId", "recordedAt", "status", "dedupeKey")


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def novo_modal(page):
    page.locator("button[data-ald-tx-new]").click()
    page.wait_for_timeout(120)


def salvar(page):
    page.locator("button[data-ald-act=salvar]").click()
    page.wait_for_timeout(120)


def main() -> int:
    falhas: list[str] = []
    server, url = serve()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ---- TX-A/B/C: porta, payload e dinheiro num DEPOSIT real ----------
        def tx_abc():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.evaluate(INSTRUMENTAR)
            novo_modal(page)
            page.select_option("#alladinTxConta", ids["cx"])
            page.fill("#alladinTxValor", "1.234,56")   # separador de milhar: mata parseFloat
            page.fill("#alladinTxData", "2026-01-10")
            page.fill("#alladinTxNota", "aporte inicial")
            salvar(page)
            r = page.evaluate("""() => ({
                port: window.__port,
                esperado: JPWAlladin.money.parse('1.234,56','BRL').amount,
                rec: S.alladin.transactions[0] || null,
                aberto: document.getElementById('alladinModalOverlay').classList.contains('show') })""")
            page.evaluate(RESTAURAR)
            if r["port"]["calls"] != 1:
                falhas.append(f"TX-A: submit deveria chamar addTransaction UMA vez ({r['port']['calls']})")
            if r["port"]["saves"] != 1:
                falhas.append(f"TX-A: um lancamento persiste com UM save (do dominio); veio {r['port']['saves']}")
            if r["aberto"]:
                falhas.append("TX-A: modal deveria fechar no sucesso")
            payload = r["port"]["payloads"][0] if r["port"]["payloads"] else {}
            for k in CAMPOS_PROIBIDOS_NO_PAYLOAD:
                if k in payload:
                    falhas.append(f"TX-B: a UI enviou campo do dominio no payload: {k}")
            if r["esperado"] != 123456:
                falhas.append(f"TX-C: premissa do parser mudou ({r['esperado']})")
            if payload.get("amount") != 123456:
                falhas.append(f"TX-C: amount nao veio de money.parse em minor units "
                              f"({payload.get('amount')!r}) — parseFloat daria 1.234")
            rec = r["rec"] or {}
            if rec.get("amount") != 123456 or rec.get("currency") != "BRL" \
               or rec.get("flowScope") != "EXTERNAL" or rec.get("note") != "aporte inicial":
                falhas.append(f"TX-B: forma persistida divergente ({rec})")
            if erros:
                falhas.append(f"TX-ABC: pageerror {erros}")
            ctx.close()
        executar(falhas, "TX-A/B/C", tx_abc)

        # ---- TX-D/H: quantity verbatim; recusa preserva draft ---------------
        def tx_dh():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.evaluate("""() => {
              JPWAlladin.ledger.addTransaction({eventType:'DEPOSIT',cashAccountId:window.__ids.cx,
                amount:500000,effectiveAt:'2026-01-05'});
            }""")
            page.evaluate(INSTRUMENTAR)
            novo_modal(page)
            page.select_option("#alladinTxTipo", "BUY")
            page.wait_for_timeout(100)
            page.select_option("#alladinTxConta", ids["cx"])
            page.select_option("#alladinTxInstrumento", ids["pe"])
            page.fill("#alladinTxQuantidade", "1.50")
            page.fill("#alladinTxValor", "300,00")
            page.fill("#alladinTxData", "2026-01-11")
            salvar(page)
            r = page.evaluate("""() => ({
                aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                erro: (document.querySelector('#alladinModalBox .session-error')||{}).textContent||null,
                qtdInput: document.getElementById('alladinTxQuantidade').value,
                valorInput: document.getElementById('alladinTxValor').value,
                payloadQtd: window.__port.payloads[0] ? window.__port.payloads[0].quantity : null,
                nBuys: S.alladin.transactions.filter(t=>t.eventType==='BUY').length })""")
            if not r["aberto"] or not r["erro"]:
                falhas.append(f"TX-H: recusa deveria manter modal aberto com erro in-place ({r})")
            if r["nBuys"] != 0:
                falhas.append("TX-H: recusa PERSISTIU um lancamento")
            if r["payloadQtd"] != "1.50":
                falhas.append(f"TX-D: quantity nao foi VERBATIM ao dominio ({r['payloadQtd']!r})")
            if r["qtdInput"] != "1.50" or r["valorInput"] != "300,00":
                falhas.append(f"TX-D: o draft foi corrigido/perdido apos a recusa ({r})")
            if "1.5" not in (r["erro"] or ""):
                falhas.append(f"TX-D: o texto da recusa deveria explicar a grafia canonica ({r['erro']!r})")
            # corrige para canonica e registra
            page.fill("#alladinTxQuantidade", "1.5")
            salvar(page)
            r2 = page.evaluate("""() => {
                const b=S.alladin.transactions.find(t=>t.eventType==='BUY');
                return { qtd: b?b.quantity:null, fechou: !document.getElementById('alladinModalOverlay').classList.contains('show') };
            }""")
            if r2["qtd"] != "1.5" or not r2["fechou"]:
                falhas.append(f"TX-D: quantity canonica deveria persistir byte-igual ({r2})")
            # sinal negativo: recusado pelo dominio, sem invencao da UI
            novo_modal(page)
            page.select_option("#alladinTxTipo", "SELL")
            page.wait_for_timeout(100)
            page.select_option("#alladinTxConta", ids["cx"])
            page.select_option("#alladinTxInstrumento", ids["pe"])
            page.fill("#alladinTxQuantidade", "-5")
            page.fill("#alladinTxValor", "10,00")
            page.fill("#alladinTxData", "2026-01-12")
            salvar(page)
            r3 = page.evaluate("""() => ({
                aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                nSells: S.alladin.transactions.filter(t=>t.eventType==='SELL').length })""")
            page.evaluate(RESTAURAR)
            if not r3["aberto"] or r3["nSells"] != 0:
                falhas.append(f"TX-D: quantity com sinal deveria ser recusada ({r3})")
            if erros:
                falhas.append(f"TX-D/H: pageerror {erros}")
            ctx.close()
        executar(falhas, "TX-D/H", tx_dh)

        # ---- TX-E/F: os NOVE tipos pelo modal; ajuste com reason ------------
        def tx_ef():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            planos = [
                ("DEPOSIT",           {"conta": "cx", "valor": "5.000,00"}),
                ("WITHDRAWAL",        {"conta": "cx", "valor": "100,00"}),
                ("TRANSFER",          {"origem": "cx", "destino": "cb", "valor": "50,00"}),
                ("BUY",               {"conta": "cx", "inst": "pe", "qtd": "10", "valor": "300,00",
                                       "fees": "1,00", "taxes": "0,50"}),
                ("SELL",              {"conta": "cx", "inst": "pe", "qtd": "4", "valor": "140,00"}),
                ("FEE",               {"conta": "cx", "valor": "15,00"}),
                ("TAX",               {"conta": "cx", "valor": "7,00"}),
                ("ADJUSTMENT_CREDIT", {"conta": "cx", "valor": "2,50",
                                       "reason": "diferenca de extrato conciliada",
                                       "nota": "ver extrato"}),
                ("ADJUSTMENT_DEBIT",  {"conta": "cx", "valor": "0,90",
                                       "reason": "estorno de credito indevido"}),
            ]
            for i, (tipo, c) in enumerate(planos):
                novo_modal(page)
                page.select_option("#alladinTxTipo", tipo)
                page.wait_for_timeout(80)
                if "origem" in c:
                    page.select_option("#alladinTxOrigem", ids[c["origem"]])
                    page.select_option("#alladinTxDestino", ids[c["destino"]])
                else:
                    page.select_option("#alladinTxConta", ids[c["conta"]])
                if "inst" in c:
                    page.select_option("#alladinTxInstrumento", ids[c["inst"]])
                    page.fill("#alladinTxQuantidade", c["qtd"])
                    if "fees" in c: page.fill("#alladinTxFees", c["fees"])
                    if "taxes" in c: page.fill("#alladinTxTaxes", c["taxes"])
                if "reason" in c:
                    page.fill("#alladinTxReason", c["reason"])
                if "nota" in c:
                    page.fill("#alladinTxNota", c["nota"])
                page.fill("#alladinTxValor", c["valor"])
                page.fill("#alladinTxData", f"2026-02-{i+1:02d}")
                salvar(page)
                ok = page.evaluate(
                    "(tp) => S.alladin.transactions.filter(t=>t.eventType===tp).length", tipo)
                if not ok:
                    erro = page.evaluate(
                        "() => (document.querySelector('#alladinModalBox .session-error')||{}).textContent||''")
                    falhas.append(f"TX-E {tipo}: nao persistiu pelo modal ({erro[:90]!r})")
                    page.evaluate("() => alladinModalDismiss()")
            r = page.evaluate("""() => {
              const aj=S.alladin.transactions.find(t=>t.eventType==='ADJUSTMENT_CREDIT');
              const db=S.alladin.transactions.find(t=>t.eventType==='ADJUSTMENT_DEBIT');
              const buy=S.alladin.transactions.find(t=>t.eventType==='BUY');
              return { n:S.alladin.transactions.length,
                       ajReason:aj?aj.reason:null, ajNote:aj?aj.note:null,
                       ajTemFlow:aj?Object.prototype.hasOwnProperty.call(aj,'flowScope'):null,
                       dbReason:db?db.reason:null,
                       buyFees:buy?buy.fees:null, buyTaxes:buy?buy.taxes:null };
            }""")
            if r["n"] != 9:
                falhas.append(f"TX-E: esperava 9 lancamentos, ha {r['n']}")
            if r["ajReason"] != "diferenca de extrato conciliada" or r["ajNote"] != "ver extrato":
                falhas.append(f"TX-F: reason/note do ajuste divergentes ({r})")
            if r["ajTemFlow"]:
                falhas.append("TX-F: ajuste ganhou flowScope pela UI")
            if r["dbReason"] != "estorno de credito indevido":
                falhas.append(f"TX-F: reason do DEBIT divergente ({r['dbReason']!r})")
            if r["buyFees"] != 100 or r["buyTaxes"] != 50:
                falhas.append(f"TX-C: fees/taxes nao passaram por money.parse ({r})")
            if erros:
                falhas.append(f"TX-E/F: pageerror {erros}")
            ctx.close()
        executar(falhas, "TX-E/F", tx_ef)

        # ---- TX-G: transfer — recusas do dominio, sem pre-filtro ------------
        def tx_g():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            novo_modal(page)
            page.select_option("#alladinTxTipo", "TRANSFER")
            page.wait_for_timeout(100)
            # o destino oferece TODAS as contas ativas — inclusive a USD e a
            # propria origem: pre-filtrar seria a UI decidindo regra do dominio
            ops = page.evaluate("""() => [...document.querySelectorAll('#alladinTxDestino option')]
                                        .map(o=>o.value).filter(Boolean)""")
            for chave in ("cx", "cb", "cu"):
                if ids[chave] not in ops:
                    falhas.append(f"TX-G: destino pre-filtrado — {chave} ausente do seletor")
            # mesma conta
            page.select_option("#alladinTxOrigem", ids["cx"])
            page.select_option("#alladinTxDestino", ids["cx"])
            page.fill("#alladinTxValor", "10,00")
            page.fill("#alladinTxData", "2026-03-01")
            salvar(page)
            e1 = page.evaluate("() => (document.querySelector('#alladinModalBox .session-error')||{}).textContent||''")
            if "mesma conta" not in e1:
                falhas.append(f"TX-G: mesma conta deveria ser recusada pelo dominio ({e1[:80]!r})")
            # moedas diferentes
            page.select_option("#alladinTxDestino", ids["cu"])
            salvar(page)
            e2 = page.evaluate("() => (document.querySelector('#alladinModalBox .session-error')||{}).textContent||''")
            if "moedas diferentes" not in e2:
                falhas.append(f"TX-G: moedas diferentes deveriam ser recusadas pelo dominio ({e2[:80]!r})")
            n = page.evaluate("() => S.alladin.transactions.length")
            if n != 0:
                falhas.append(f"TX-G: recusa persistiu lancamento ({n})")
            # e o legitimo passa
            page.select_option("#alladinTxDestino", ids["cb"])
            salvar(page)
            n2 = page.evaluate("() => S.alladin.transactions.filter(t=>t.eventType==='TRANSFER').length")
            if n2 != 1:
                falhas.append("TX-G: transferencia legitima nao persistiu")
            if erros:
                falhas.append(f"TX-G: pageerror {erros}")
            ctx.close()
        executar(falhas, "TX-G", tx_g)

        # ---- TX-I/J: double submit e cancelamento ---------------------------
        def tx_ij():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.evaluate(INSTRUMENTAR)
            novo_modal(page)
            page.select_option("#alladinTxConta", ids["cx"])
            page.fill("#alladinTxValor", "100,00")
            page.fill("#alladinTxData", "2026-01-10")
            # dois cliques no MESMO tick: o segundo encontra a maquina fora de
            # EDITING (modal ja fechado pelo primeiro) e precisa ser inerte
            r = page.evaluate("""() => {
              const b=document.querySelector('button[data-ald-act=salvar]');
              b.click(); b.click();
              return { calls: window.__port.calls, n: S.alladin.transactions.length };
            }""")
            if r["calls"] != 1 or r["n"] != 1:
                falhas.append(f"TX-I: double submit duplicou ({r})")
            # cancelamento zero-write
            page.evaluate("""() => { window.__S=JSON.stringify(S);
                                     window.__LS=localStorage.getItem('%s');
                                     window.__port.calls=0; window.__port.saves=0; }""" % LSKEY)
            novo_modal(page)
            page.select_option("#alladinTxTipo", "ADJUSTMENT_DEBIT")
            page.wait_for_timeout(80)
            page.select_option("#alladinTxConta", ids["cx"])
            page.fill("#alladinTxValor", "9,99")
            page.fill("#alladinTxReason", "rascunho abandonado")
            page.locator("button[data-ald-act=cancelar]").click()
            page.wait_for_timeout(100)
            r2 = page.evaluate("""() => ({ calls: window.__port.calls, saves: window.__port.saves,
                sIgual: JSON.stringify(S)===window.__S,
                lsIgual: localStorage.getItem('%s')===window.__LS,
                fechou: !document.getElementById('alladinModalOverlay').classList.contains('show') })""" % LSKEY)
            page.evaluate(RESTAURAR)
            if r2["calls"] or r2["saves"]:
                falhas.append(f"TX-J: cancelar chamou porta/save ({r2})")
            if not r2["sIgual"] or not r2["lsIgual"] or not r2["fechou"]:
                falhas.append(f"TX-J: cancelar nao foi zero-write ({r2})")
            if erros:
                falhas.append(f"TX-I/J: pageerror {erros}")
            ctx.close()
        executar(falhas, "TX-I/J", tx_ij)

        # ---- TX-K/L: write gate e sentinela ---------------------------------
        def tx_kl():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            # EMPTY legitimo: CTA presente e habilitado
            r0 = page.evaluate("""() => { JPWAlladinUI.selectView('ledger');
              const b=document.querySelector('button[data-ald-tx-new]');
              return { existe: !!b, disabled: b?b.disabled:null }; }""")
            if not r0["existe"] or r0["disabled"]:
                falhas.append(f"TX-L: EMPTY legitimo deveria convidar escrita ({r0})")
            # schema futuro: CTA disabled
            r1 = page.evaluate("""() => { S.alladin.schemaVersion=7; JPWAlladinUI.render();
              const b=document.querySelector('button[data-ald-tx-new]');
              const painel=document.querySelector('[data-alladin-panel="ledger"]').innerText;
              return { existe: !!b, disabled: b?b.disabled:null, painel: painel.slice(0,80) }; }""")
            # sob schema futuro a SENTINELA tambem bloqueia (compat.readOnly):
            # o painel vira aviso e o CTA nem e renderizado — mais forte que
            # disabled, e igualmente valido para o contrato "nao convidar".
            if r1["existe"] and not r1["disabled"]:
                falhas.append(f"TX-K: CTA habilitado sob schema futuro ({r1})")
            # submit TARDIO: modal aberto sobre agregado valido; o estado piora
            # entre abrir e salvar — o dominio decide, sem falso sucesso
            page.evaluate("() => { S.alladin.schemaVersion=6; JPWAlladinUI.render(); }")
            page.wait_for_timeout(80)
            novo_modal(page)
            page.select_option("#alladinTxConta", ids["cx"])
            page.fill("#alladinTxValor", "10,00")
            page.fill("#alladinTxData", "2026-01-10")
            page.evaluate("() => { S.alladin.schemaVersion=7; }")
            salvar(page)
            r2 = page.evaluate("""() => ({
                aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                erro: (document.querySelector('#alladinModalBox .session-error')||{}).textContent||'',
                n: Array.isArray(S.alladin.transactions)?S.alladin.transactions.length:-1 })""")
            page.evaluate("() => { S.alladin.schemaVersion=6; alladinForm.estado='EDITING'; alladinModalDismiss(); }")
            if not r2["aberto"] or "versão mais nova" not in r2["erro"]:
                falhas.append(f"TX-K: submit sob schema futuro deveria recusar com honestidade ({r2['erro'][:90]!r})")
            if r2["n"] != 0:
                falhas.append(f"TX-K: recusa persistiu lancamento ({r2['n']})")
            # sentinela BLOCKING por corrupcao: CTA AUSENTE
            page.evaluate("""() => {
              JPWAlladin.ledger.addTransaction({eventType:'DEPOSIT',cashAccountId:window.__ids.cx,
                amount:1000,effectiveAt:'2026-01-10'});
              S.alladin.transactions.push(JSON.parse(JSON.stringify(S.alladin.transactions[0])));
              JPWAlladinUI.render();
            }""")
            page.wait_for_timeout(80)
            r3 = page.evaluate("""() => ({
                cta: !!document.querySelector('button[data-ald-tx-new]'),
                painel: document.querySelector('[data-alladin-panel="ledger"]').innerText.toLowerCase() })""")
            if r3["cta"]:
                falhas.append("TX-L: BLOCKING nao pode convidar escrita — CTA presente")
            if "indisponí" not in r3["painel"]:
                falhas.append("TX-L: painel corrompido deveria estar indisponivel")
            if erros:
                falhas.append(f"TX-K/L: pageerror {erros}")
            ctx.close()
        executar(falhas, "TX-K/L", tx_kl)

        # ---- TX-M: pos-sucesso reflete VIA read-models ----------------------
        def tx_m():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            novo_modal(page)
            page.select_option("#alladinTxConta", ids["cx"])
            page.fill("#alladinTxValor", "5.000,00")
            page.fill("#alladinTxData", "2026-01-10")
            salvar(page)
            novo_modal(page)
            page.select_option("#alladinTxTipo", "BUY")
            page.wait_for_timeout(80)
            page.select_option("#alladinTxConta", ids["cx"])
            page.select_option("#alladinTxInstrumento", ids["pe"])
            page.fill("#alladinTxQuantidade", "10")
            page.fill("#alladinTxValor", "300,00")
            page.fill("#alladinTxData", "2026-01-11")
            salvar(page)
            # Lancamentos: o painel reflete os fatos
            ledger_txt = page.evaluate("() => document.querySelector('[data-alladin-panel=\\'ledger\\']').innerText")
            for marca in ("Aporte", "Compra", "PETR4"):
                if marca not in ledger_txt:
                    falhas.append(f"TX-M: Lancamentos nao refletiu {marca!r}")
            # Saldos: DOM comparado ao read-model — o teste NAO recalcula
            page.evaluate("() => JPWAlladinUI.selectView('balances')")
            page.wait_for_timeout(100)
            r = page.evaluate("""() => {
              const dom=[...document.querySelectorAll('[data-alladin-panel="balances"] table tr')].slice(1)
                        .map(tr=>tr.children[1].innerText.trim());
              const rm=JPWAlladin.leitura.cashAccounts().map(c=>{
                const s=JPWAlladin.leitura.saldoDeCaixa(c.cashAccountId);
                return s.available?JPWAlladin.money.format({amount:s.amount,currency:s.currency}):'Indisponível';
              });
              return { dom, rm };
            }""")
            if r["dom"] != r["rm"]:
                falhas.append(f"TX-M: Saldos diverge do read-model\n   dom={r['dom']}\n   rm ={r['rm']}")
            # Posicoes: idem
            page.evaluate("() => JPWAlladinUI.selectView('positions')")
            page.wait_for_timeout(100)
            r2 = page.evaluate("""() => {
              const dom=[...document.querySelectorAll('[data-alladin-panel="positions"] table tr')].slice(1)
                         .map(tr=>tr.children[2].innerText.trim());
              return { dom, rm: JPWAlladin.leitura.posicoes().positions.map(p=>p.quantity) };
            }""")
            if r2["dom"] != r2["rm"]:
                falhas.append(f"TX-M: Posicoes diverge do read-model ({r2})")
            if erros:
                falhas.append(f"TX-M: pageerror {erros}")
            ctx.close()
        executar(falhas, "TX-M", tx_m)

        # ---- TX-N: nenhuma dependencia de data corrente ---------------------
        # Estrutural: todas as datas da suite sao FIXAS (2026-01/02/03) e nenhum
        # caso le mes corrente. A licao do repair do finpes-budget aplicada
        # desde o nascimento — este marcador existe para o revisor humano.
        def tx_n():
            src = Path(__file__).read_text(encoding="utf-8")
            for proibido in ("datetime.now", "date.today", "Date()", "Date.now"):
                # a unica excecao aceitavel seria em comentario; procurar em codigo
                for ln in src.splitlines():
                    s = ln.split("#")[0]
                    if proibido in s and "proibido" not in s:
                        falhas.append(f"TX-N: dependencia de data corrente no harness: {ln.strip()[:80]}")
        executar(falhas, "TX-N", tx_n)

        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        browser.close()
    server.shutdown()

    if falhas:
        print("ALLADIN UI TX WRITE TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("alladin_ui_tx_write_test PASS (TX-A..TX-N: porta unica com um addTransaction e "
          "um save por submit; payload sem currency/flowScope/unitPrice/ids/status/dedupe; "
          "dinheiro exclusivamente por money.parse em minor units (1.234,56 -> 123456, "
          "parseFloat morreria); quantity VERBATIM — 1.50 recusada sem correcao com draft "
          "intacto, 1.5 persistida byte-igual, sinal recusado; os NOVE tipos criados pelo "
          "modal real; ajuste com reason proprio, note independente e zero flowScope; "
          "transfer com destino sem pre-filtro e recusas do dominio para mesma conta e "
          "moedas distintas; double submit inerte; cancelar zero-write byte a byte; write "
          "gate na abertura e no submit tardio sem falso sucesso; BLOCKING nao convida "
          "escrita e EMPTY legitimo convida; pos-sucesso comparado aos read-models sem "
          "recalculo; datas fixas deterministicas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
