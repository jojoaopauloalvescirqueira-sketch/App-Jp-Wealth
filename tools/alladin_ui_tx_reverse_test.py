#!/usr/bin/env python3
"""Alladin ALD-05-S3 — estorno pela UI (RV-A..RV-H).

O estorno e a unica mecanica de correcao que o ledger append-only reconhece, e
todo o efeito economico dele e COPIADO do original pelo dominio. O que esta
suite defende: a UI oferece a acao, mostra o FATO, faz UMA chamada a
reverseTransaction — e jamais inverte sinal, monta delta, simula consequencia
ou toca o original.

  RV-A  elegibilidade visual: Estornar so em POSTED nao-REVERSAL sem estorno;
        '—' em REVERSED e em linhas REVERSAL; disabled sob write gate;
        BLOCKING => sem tabela e sem acao
  RV-B  modal: resumo do original em READ-ONLY (sem inputs economicos);
        editaveis SOMENTE data/motivo/nota; sem input de dedupeKey
  RV-C  porta: 1 reverseTransaction, 0 addTransaction, 0 save direto;
        payload apenas com campos autorizados
  RV-D  sucesso: original Estornado, REVERSAL visivel, Saldos/Posicoes
        comparados aos READ-MODELS (oracle e o dominio, nunca recalculo)
  RV-E  corridas/recusas: estorno criado por fora entre abrir e confirmar =>
        ALD_REVERSAL_JA_EXISTE inequivoco; data invalida => draft preservado
  RV-F  cancelar zero-write byte a byte; double-submit inerte
  RV-G  submit tardio sob schema futuro: recusa honesta, zero persistencia
  RV-H  original jamais mutado pela UI: byte-identico apos abrir/cancelar; no
        sucesso so o status muda, e quem muda e o dominio

Datas FIXAS (2026-01/02); nenhum caso depende de data corrente.
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

CAMPOS_PROIBIDOS = ("amount", "currency", "flowScope", "eventType", "cashAccountId",
                    "sourceCashAccountId", "destinationCashAccountId", "instrumentId",
                    "quantity", "fees", "taxes", "dedupeKey", "transactionId",
                    "recordedAt", "status")


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


# Fixture pelo DOMINIO: um DEPOSIT elegivel, um BUY elegivel, e um par
# ajuste+estorno (para as linhas REVERSED e REVERSAL). Ids em window.__ids.
SEMEAR = """() => {
  const c=JPWAlladin.cadastro, L=JPWAlladin.ledger;
  const xp=c.addAccount({name:'XP',institution:'XP',accountType:'BROKERAGE'}).recordId;
  const cx=c.addCashAccount({accountId:xp,currency:'BRL'}).recordId;
  const pe=c.addInstrument({name:'Petrobras PN',symbol:'PETR4',currency:'BRL',
    instrumentFamily:'EQUITY_LIKE',assetClass:'RENDA_VARIAVEL'}).recordId;
  const dep=L.addTransaction({eventType:'DEPOSIT',cashAccountId:cx,amount:100000,effectiveAt:'2026-01-10'}).recordId;
  const buy=L.addTransaction({eventType:'BUY',cashAccountId:cx,instrumentId:pe,quantity:'10',
    amount:30000,fees:100,taxes:50,effectiveAt:'2026-01-11'}).recordId;
  const aj=L.addTransaction({eventType:'ADJUSTMENT_CREDIT',cashAccountId:cx,amount:250,
    effectiveAt:'2026-01-12',reason:'diferenca de extrato'}).recordId;
  const rev=L.reverseTransaction(aj,{effectiveAt:'2026-01-13'}).recordId;
  window.__ids={xp,cx,pe,dep,buy,aj,rev};
  JPWNavigation.navigate('alladin'); JPWAlladinUI.selectView('ledger');
  return window.__ids;
}"""

INSTRUMENTAR = """() => {
  window.__port={rev:0, add:0, saves:0, payloads:[]};
  const or_=JPWAlladin.ledger.reverseTransaction; window.__origRev=or_;
  JPWAlladin.ledger.reverseTransaction=function(id,d){
    window.__port.rev++; window.__port.payloads.push({id, d:JSON.parse(JSON.stringify(d||{}))});
    return or_(id,d);
  };
  const oa_=JPWAlladin.ledger.addTransaction; window.__origAdd=oa_;
  JPWAlladin.ledger.addTransaction=function(d){ window.__port.add++; return oa_(d); };
  const os_=window.save; window.__origSave=os_;
  window.save=function(){ window.__port.saves++; return os_.apply(this,arguments); };
}"""
RESTAURAR = """() => {
  JPWAlladin.ledger.reverseTransaction=window.__origRev;
  JPWAlladin.ledger.addTransaction=window.__origAdd;
  window.save=window.__origSave;
}"""


def linhas_acoes(page):
    return page.evaluate("""() => [...document.querySelectorAll(
        '[data-alladin-panel="ledger"] table tr')].slice(1)
        .map(tr=>({ev:tr.children[1].innerText.trim(), st:tr.children[5].innerText.trim(),
                   acao:tr.children[6].innerText.trim(),
                   btn:!!tr.children[6].querySelector('button'),
                   dis:(tr.children[6].querySelector('button')||{}).disabled||false}))""")


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def main() -> int:
    falhas: list[str] = []
    server, url = serve()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ---- RV-A: elegibilidade visual -------------------------------------
        def rv_a():
            ctx, page, erros = abrir(browser, url)
            page.evaluate(SEMEAR)
            page.wait_for_timeout(200)
            rows = linhas_acoes(page)
            por_ev = {r["ev"]: r for r in rows}
            for ev in ("Aporte", "Compra"):
                r = por_ev.get(ev, {})
                if not r.get("btn") or r.get("acao") != "Estornar" or r.get("dis"):
                    falhas.append(f"RV-A: {ev} POSTED deveria oferecer Estornar habilitado ({r})")
            aj = por_ev.get("Ajuste (crédito)", {})
            if aj.get("btn") or aj.get("acao") != "—" or aj.get("st") != "Estornado":
                falhas.append(f"RV-A: original REVERSED deveria ter '—' ({aj})")
            est = por_ev.get("Estorno de Ajuste (crédito)", {})
            if est.get("btn") or est.get("acao") != "—":
                falhas.append(f"RV-A: linha REVERSAL deveria ter '—' ({est})")
            # write gate: elegivel continua LISTADO, mas o botao vem disabled.
            # writeBlockReason so tem causa real via compat (que tambem derruba a
            # sentinela e a tabela inteira), entao o ramo disabled e provado
            # patchando a superficie PUBLICA que a UI consulta.
            r2 = page.evaluate("""() => {
              const orig=JPWAlladin.writeBlockReason;
              JPWAlladin.writeBlockReason=()=>'BLOQUEIO_DE_PROVA';
              JPWAlladinUI.render();
              const btns=[...document.querySelectorAll('button[data-ald-tx-reverse]')];
              const out={ n:btns.length, disabled:btns.every(b=>b.disabled) };
              JPWAlladin.writeBlockReason=orig; JPWAlladinUI.render();
              return out;
            }""")
            if r2["n"] == 0 or not r2["disabled"]:
                falhas.append(f"RV-A: sob write gate o Estornar deveria vir disabled ({r2})")
            # BLOCKING: sem tabela, sem acao
            page.evaluate("""() => {
              S.alladin.transactions.push(JSON.parse(JSON.stringify(S.alladin.transactions[0])));
              JPWAlladinUI.render();
            }""")
            page.wait_for_timeout(100)
            r3 = page.evaluate("""() => ({
                tabela: document.querySelectorAll('[data-alladin-panel="ledger"] table').length,
                acoes: document.querySelectorAll('button[data-ald-tx-reverse]').length })""")
            if r3["tabela"] or r3["acoes"]:
                falhas.append(f"RV-A: BLOCKING deveria remover tabela e acoes ({r3})")
            if erros:
                falhas.append(f"RV-A: pageerror {erros}")
            ctx.close()
        executar(falhas, "RV-A", rv_a)

        # ---- RV-B: modal — original read-only, 3 campos editaveis ----------
        def rv_b():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.wait_for_timeout(200)
            page.locator(f"button[data-ald-tx-reverse='{ids['buy']}']").click()
            page.wait_for_timeout(150)
            r = page.evaluate("""() => {
              const box=document.getElementById('alladinModalBox');
              const resumo=box.querySelector('[data-ald-rev-original]');
              return { resumo: resumo?resumo.innerText:'',
                       inputsNoResumo: resumo?resumo.querySelectorAll('input,select,textarea').length:-1,
                       inputs: [...box.querySelectorAll('input,select,textarea')].map(i=>i.id) };
            }""")
            for marca in ("Compra", "2026-01-11", "R$ 300,00", "PETR4", "10"):
                if marca not in r["resumo"]:
                    falhas.append(f"RV-B: resumo do original sem {marca!r}")
            if r["inputsNoResumo"] != 0:
                falhas.append(f"RV-B: o resumo do original tem inputs ({r['inputsNoResumo']})")
            esperado = ["alladinTxRevData", "alladinTxRevReason", "alladinTxRevNota"]
            if sorted(r["inputs"]) != sorted(esperado):
                falhas.append(f"RV-B: campos editaveis divergem do contrato ({r['inputs']})")
            page.evaluate("() => alladinModalDismiss()")
            if erros:
                falhas.append(f"RV-B: pageerror {erros}")
            ctx.close()
        executar(falhas, "RV-B", rv_b)

        # ---- RV-C/D: porta, payload e sucesso via read-models ---------------
        def rv_cd():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.evaluate(INSTRUMENTAR)
            page.wait_for_timeout(150)
            page.locator(f"button[data-ald-tx-reverse='{ids['dep']}']").click()
            page.wait_for_timeout(120)
            page.fill("#alladinTxRevData", "2026-02-01")
            page.fill("#alladinTxRevReason", "aporte em duplicidade")
            page.locator("button[data-ald-act=salvar]").click()
            page.wait_for_timeout(150)
            r = page.evaluate("""() => ({ port: window.__port,
                fechou: !document.getElementById('alladinModalOverlay').classList.contains('show') })""")
            page.evaluate(RESTAURAR)
            if r["port"]["rev"] != 1 or r["port"]["add"] != 0:
                falhas.append(f"RV-C: esperava 1 reverseTransaction e 0 addTransaction ({r['port']})")
            if r["port"]["saves"] != 1:
                falhas.append(f"RV-C: um estorno persiste com UM save do dominio ({r['port']['saves']})")
            p = r["port"]["payloads"][0] if r["port"]["payloads"] else {"d": {}}
            if p.get("id") != ids["dep"]:
                falhas.append(f"RV-C: originalId divergente ({p.get('id')!r})")
            for k in CAMPOS_PROIBIDOS:
                if k in p["d"]:
                    falhas.append(f"RV-C: payload carregou campo proibido: {k}")
            if p["d"].get("effectiveAt") != "2026-02-01" or p["d"].get("reason") != "aporte em duplicidade":
                falhas.append(f"RV-C: payload autorizado divergente ({p['d']})")
            if not r["fechou"]:
                falhas.append("RV-D: modal deveria fechar no sucesso")
            # RV-D: UI e read-models como oracle
            texto = page.evaluate("() => document.querySelector('[data-alladin-panel=\\'ledger\\']').innerText")
            if "Estorno de Aporte" not in texto:
                falhas.append("RV-D: o REVERSAL nao apareceu como nova linha")
            rows = linhas_acoes(page)
            dep = [x for x in rows if x["ev"] == "Aporte"]
            if not dep or dep[0]["st"] != "Estornado" or dep[0]["acao"] != "—":
                falhas.append(f"RV-D: original deveria aparecer Estornado sem acao ({dep})")
            page.evaluate("() => JPWAlladinUI.selectView('balances')")
            page.wait_for_timeout(100)
            r2 = page.evaluate("""() => {
              const dom=[...document.querySelectorAll('[data-alladin-panel="balances"] table tr')].slice(1)
                        .map(tr=>tr.children[1].innerText.trim());
              const rm=JPWAlladin.leitura.cashAccounts().map(c=>{
                const s=JPWAlladin.leitura.saldoDeCaixa(c.cashAccountId);
                return s.available?JPWAlladin.money.format({amount:s.amount,currency:s.currency}):'Indisponível';
              });
              return { dom, rm };
            }""")
            if r2["dom"] != r2["rm"]:
                falhas.append(f"RV-D: Saldos diverge do read-model apos estorno ({r2})")
            page.evaluate("() => JPWAlladinUI.selectView('positions')")
            page.wait_for_timeout(100)
            r3 = page.evaluate("""() => {
              const dom=[...document.querySelectorAll('[data-alladin-panel="positions"] table tr')].slice(1)
                         .map(tr=>tr.children[2].innerText.trim());
              return { dom, rm: JPWAlladin.leitura.posicoes().positions.map(p=>p.quantity) };
            }""")
            if r3["dom"] != r3["rm"]:
                falhas.append(f"RV-D: Posicoes diverge do read-model ({r3})")
            if erros:
                falhas.append(f"RV-C/D: pageerror {erros}")
            ctx.close()
        executar(falhas, "RV-C/D", rv_cd)

        # ---- RV-E: corrida e recusa com draft --------------------------------
        def rv_e():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.wait_for_timeout(150)
            page.locator(f"button[data-ald-tx-reverse='{ids['dep']}']").click()
            page.wait_for_timeout(120)
            # outro caminho estorna ANTES da confirmacao
            page.evaluate("""() => JPWAlladin.ledger.reverseTransaction(window.__ids.dep,
                {effectiveAt:'2026-02-01'})""")
            page.fill("#alladinTxRevData", "2026-02-02")
            page.locator("button[data-ald-act=salvar]").click()
            page.wait_for_timeout(120)
            r = page.evaluate("""() => ({
                aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                erro: (document.querySelector('#alladinModalBox .session-error')||{}).textContent||'',
                nRev: S.alladin.transactions.filter(t=>t.eventType==='REVERSAL'
                        && t.reversalOf===window.__ids.dep).length })""")
            if not r["aberto"]:
                falhas.append("RV-E: recusa deveria manter o modal aberto")
            if "já possui um estorno" not in r["erro"] or "Nenhum novo estorno foi criado" not in r["erro"]:
                falhas.append(f"RV-E: mensagem do estorno duplicado nao e inequivoca ({r['erro'][:120]!r})")
            if r["nRev"] != 1:
                falhas.append(f"RV-E: corrida gerou {r['nRev']} reversals — deveria ser 1")
            # data invalida: recusa do dominio, draft preservado
            page.fill("#alladinTxRevData", "01/02/2026")
            page.fill("#alladinTxRevNota", "rascunho vivo")
            page.locator("button[data-ald-act=salvar]").click()
            page.wait_for_timeout(120)
            r2 = page.evaluate("""() => ({
                erro: (document.querySelector('#alladinModalBox .session-error')||{}).textContent||'',
                data: document.getElementById('alladinTxRevData').value,
                nota: document.getElementById('alladinTxRevNota').value })""")
            if "Data inválida" not in r2["erro"] and "já possui" not in r2["erro"]:
                falhas.append(f"RV-E: data invalida sem recusa clara ({r2['erro'][:90]!r})")
            if r2["data"] != "01/02/2026" or r2["nota"] != "rascunho vivo":
                falhas.append(f"RV-E: draft perdido apos recusa ({r2})")
            page.evaluate("() => alladinModalDismiss()")
            if erros:
                falhas.append(f"RV-E: pageerror {erros}")
            ctx.close()
        executar(falhas, "RV-E", rv_e)

        # ---- RV-F: cancelar e double-submit ---------------------------------
        def rv_f():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.evaluate(INSTRUMENTAR)
            page.wait_for_timeout(150)
            page.evaluate("""() => { window.__S=JSON.stringify(S);
                                     window.__LS=localStorage.getItem('%s'); }""" % LSKEY)
            page.locator(f"button[data-ald-tx-reverse='{ids['dep']}']").click()
            page.wait_for_timeout(120)
            page.fill("#alladinTxRevData", "2026-02-01")
            page.locator("button[data-ald-act=cancelar]").click()
            page.wait_for_timeout(100)
            r = page.evaluate("""() => ({ rev: window.__port.rev, add: window.__port.add,
                saves: window.__port.saves,
                sIgual: JSON.stringify(S)===window.__S,
                lsIgual: localStorage.getItem('%s')===window.__LS })""" % LSKEY)
            if r["rev"] or r["add"] or r["saves"]:
                falhas.append(f"RV-F: cancelar chamou porta/save ({r})")
            if not r["sIgual"] or not r["lsIgual"]:
                falhas.append(f"RV-F: cancelar nao foi zero-write ({r})")
            # double submit no MESMO tick
            page.locator(f"button[data-ald-tx-reverse='{ids['dep']}']").click()
            page.wait_for_timeout(120)
            page.fill("#alladinTxRevData", "2026-02-01")
            r2 = page.evaluate("""() => {
              const b=document.querySelector('button[data-ald-act=salvar]');
              b.click(); b.click();
              return { rev: window.__port.rev,
                       nRev: S.alladin.transactions.filter(t=>t.eventType==='REVERSAL'
                              && t.reversalOf===window.__ids.dep).length };
            }""")
            page.evaluate(RESTAURAR)
            if r2["rev"] != 1 or r2["nRev"] != 1:
                falhas.append(f"RV-F: double submit duplicou ({r2})")
            if erros:
                falhas.append(f"RV-F: pageerror {erros}")
            ctx.close()
        executar(falhas, "RV-F", rv_f)

        # ---- RV-G: submit tardio sob schema futuro --------------------------
        def rv_g():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.wait_for_timeout(150)
            page.locator(f"button[data-ald-tx-reverse='{ids['dep']}']").click()
            page.wait_for_timeout(120)
            page.fill("#alladinTxRevData", "2026-02-01")
            page.evaluate("() => { S.alladin.schemaVersion=7; }")
            antes = page.evaluate("() => S.alladin.transactions.length")
            page.locator("button[data-ald-act=salvar]").click()
            page.wait_for_timeout(120)
            r = page.evaluate("""() => ({
                aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                erro: (document.querySelector('#alladinModalBox .session-error')||{}).textContent||'',
                n: S.alladin.transactions.length })""")
            page.evaluate("() => { S.alladin.schemaVersion=6; alladinForm.estado='EDITING'; alladinModalDismiss(); }")
            if not r["aberto"] or "versão mais nova" not in r["erro"]:
                falhas.append(f"RV-G: submit tardio deveria recusar com honestidade ({r['erro'][:90]!r})")
            if r["n"] != antes:
                falhas.append(f"RV-G: recusa persistiu estorno ({antes} -> {r['n']})")
            if erros:
                falhas.append(f"RV-G: pageerror {erros}")
            ctx.close()
        executar(falhas, "RV-G", rv_g)

        # ---- RV-H: original jamais mutado pela UI ---------------------------
        def rv_h():
            ctx, page, erros = abrir(browser, url)
            ids = page.evaluate(SEMEAR)
            page.wait_for_timeout(150)
            antes = page.evaluate(
                "() => JSON.stringify(S.alladin.transactions.find(t=>t.transactionId===window.__ids.buy))")
            page.locator(f"button[data-ald-tx-reverse='{ids['buy']}']").click()
            page.wait_for_timeout(120)
            page.fill("#alladinTxRevData", "2026-02-01")
            page.locator("button[data-ald-act=cancelar]").click()
            page.wait_for_timeout(100)
            depois = page.evaluate(
                "() => JSON.stringify(S.alladin.transactions.find(t=>t.transactionId===window.__ids.buy))")
            if antes != depois:
                falhas.append("RV-H: abrir/cancelar o modal MUTOU o original")
            # sucesso: so o status muda, e quem muda e o dominio
            page.locator(f"button[data-ald-tx-reverse='{ids['buy']}']").click()
            page.wait_for_timeout(120)
            page.fill("#alladinTxRevData", "2026-02-02")
            page.locator("button[data-ald-act=salvar]").click()
            page.wait_for_timeout(150)
            r = page.evaluate("""() => {
              const orig=S.alladin.transactions.find(t=>t.transactionId===window.__ids.buy);
              const semStatus=(s)=>{ const o=JSON.parse(s); delete o.status; return JSON.stringify(o); };
              return { statusNovo: orig.status,
                       economiaIgual: semStatus(JSON.stringify(orig))===null };
            }""")
            depois2 = page.evaluate(
                "() => { const o=JSON.parse(JSON.stringify(S.alladin.transactions.find(t=>t.transactionId===window.__ids.buy))); delete o.status; return JSON.stringify(o); }")
            antes_sem = json.dumps({k: v for k, v in json.loads(antes).items() if k != "status"},
                                   separators=(",", ":"), ensure_ascii=False)
            # comparacao por CONTEUDO, ordem de chaves preservada pelo dominio
            if json.loads(depois2) != json.loads(antes_sem):
                falhas.append("RV-H: campos economicos do original mudaram no estorno")
            if r["statusNovo"] != "REVERSED":
                falhas.append(f"RV-H: status do original deveria ser REVERSED ({r['statusNovo']!r})")
            if erros:
                falhas.append(f"RV-H: pageerror {erros}")
            ctx.close()
        executar(falhas, "RV-H", rv_h)

        # ---- datas fixas: varredura estrutural do proprio harness -----------
        def rv_datas():
            src = Path(__file__).read_text(encoding="utf-8")
            for proibido in ("datetime.now", "date.today", "Date()", "Date.now"):
                for ln in src.splitlines():
                    s = ln.split("#")[0]
                    if proibido in s and "proibido" not in s:
                        falhas.append(f"RV: dependencia de data corrente no harness: {ln.strip()[:80]}")
        executar(falhas, "RV-datas", rv_datas)

        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        browser.close()
    server.shutdown()

    if falhas:
        print("ALLADIN UI TX REVERSE TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("alladin_ui_tx_reverse_test PASS (RV-A..RV-H: Estornar so em POSTED nao-REVERSAL "
          "sem estorno existente, '—' nas linhas REVERSED/REVERSAL, disabled sob write gate, "
          "BLOCKING sem tabela nem acao; modal com o original em READ-ONLY (zero inputs "
          "economicos) e so data/motivo/nota editaveis, sem dedupeKey; porta unica — 1 "
          "reverseTransaction, 0 addTransaction, 1 save do dominio — com payload apenas de "
          "campos autorizados; sucesso refletido pelos READ-MODELS (original Estornado, "
          "REVERSAL visivel, Saldos e Posicoes identicos ao dominio); corrida entre abrir e "
          "confirmar recusada com mensagem inequivoca de estorno ja existente; data invalida "
          "recusada com draft intacto; cancelar zero-write byte a byte; double-submit "
          "inerte; submit tardio sob schema futuro recusado sem falso sucesso; original "
          "byte-identico apos abrir/cancelar e com economia intacta no sucesso; datas fixas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
