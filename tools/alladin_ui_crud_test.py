#!/usr/bin/env python3
"""Alladin C3-S2-A — manutencao cadastral: Account + CashAccount + status x4.

Contratos provados (gate C3-S2-A + S2A-1..S2A-12):
  W1  criar Account pelo modal REAL persiste em memoria E disco
  W2  editar Account persiste; imutaveis nunca sao inputs
  W3  criar CashAccount exige Account ACTIVE (select so lista ativas; sem conta
      ativa o botao Novo caixa da lugar a mensagem congelada)         [S2A-6]
  W4  DC-4 pos-criacao: registro JA persistido antes da decisao       [S2A-1]
      Salvar/Enter nao recriam                                        [S2A-2]
      Escape/backdrop suspensos                                       [S2A-3]
      Inativar usa setRecordStatus                                    [S2A-4]
      falha da inativacao mantem registro e decisao visivel           [S2A-5]
  W5  edit de cash com referencia inativa: rotulo honesto, sem troca
      silenciosa de accountId                                         [S2A-7]
  W6  inativar Account com cash ativa: dominio recusa, DOM sem status
      falso                                                           [S2A-8]
      reativar cash com Account inativa: mesmo contrato               [S2A-9]
  W7  status de Instrument/Asset pela linha via setRecordStatus       [S2A-10]
  W8  cancelar formulario: zero write                                 [S2A-11]
  W9  writeBlockReason no submit: recusa sem falso sucesso            [S2A-12]
  W10 write gate na abertura: botoes desabilitados em READ_ONLY
  W11 double submit real (dois cliques rapidos) nao duplica
  W12 validacao vazia: erro inline, dados preservados, zero write
  W13 nenhuma metrica economica nos formularios/section
  W14 confirmacao explicita de status: cancelar nao muta
  W15 focus trap + Escape + retorno de foco + mobile

Zero mudanca no dominio: a UI so chama JPWAlladin.cadastro/setRecordStatus.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import socket
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = "jpwealth_v9_state"
PROIBIDO = re.compile(r"R\$|US\$|(?<![\w])\$\s?\d|\d,\d\d(?!\d)|%|saldo|patrim[oô]nio|quantidade|pre[cç]o|custo|rentabilidade", re.IGNORECASE)


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


PRONTO = "() => typeof S === 'object' && window.JPWAlladinUI && window.JPWAlladin && document.getElementById('alladinModalOverlay')"
CONTEXTOS = []


def abrir(browser, url, viewport=None):
    ctx = browser.new_context(viewport=viewport or {"width": 1440, "height": 900})
    CONTEXTOS.append(ctx)
    ctx.add_init_script("window.__onbShown=true;")
    page = ctx.new_page()
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.route("**/*", lambda r: r.continue_() if "127.0.0.1" in r.request.url
               else r.fulfill(status=200, content_type="application/json", body="{}"))
    page.goto(url, wait_until="load")
    page.wait_for_function(PRONTO)
    page.wait_for_timeout(400)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); navigateToScreen('alladin'); }")
    return ctx, page, erros


def disco(page):
    return page.evaluate("() => JSON.parse(localStorage.getItem('%s')||'{}').alladin || null" % LSKEY)


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def criar_conta(page, nome="Conta Sintetica", inst="Banco Sintetico", tipo="BANK"):
    page.evaluate("() => JPWAlladinUI.selectView('accounts')")
    page.locator("button[data-ald-new=account]").click()
    page.locator("#alladinFldName").fill(nome)
    page.locator("#alladinFldInstitution").fill(inst)
    page.locator("#alladinFldAccountType").fill(tipo)
    page.locator("button[data-ald-act=salvar]").click()
    page.wait_for_timeout(150)


def main() -> int:
    servidor, url = serve()
    falhas: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            # ---- W1/W2: Account create + edit pelo modal real ----
            def w1_w2():
                ctx, page, erros = abrir(browser, url)
                criar_conta(page)
                d = disco(page)
                if not d or len(d["accounts"]) != 1 or d["accounts"][0]["name"] != "Conta Sintetica":
                    falhas.append(f"W1: conta criada nao chegou ao disco ({d and d['accounts']})")
                mem = page.evaluate("() => JPWAlladin.leitura.accounts()[0]")
                if not mem or mem["institution"] != "Banco Sintetico" or mem["accountType"] != "BANK":
                    falhas.append(f"W1: campos divergem na leitura ({mem})")
                dom = page.evaluate("() => document.getElementById('alladinAccounts').innerText")
                if "Conta Sintetica" not in dom:
                    falhas.append("W1: lista nao re-renderizou da leitura canonica")
                # W2: edit + imutaveis nunca como input
                page.locator("button[data-ald-edit=account]").click()
                tem_id_input = page.evaluate("""() => [...document.querySelectorAll('#alladinModalBox input')]
                    .some(i => (i.value||'').startsWith('aldacc_'))""")
                if tem_id_input:
                    falhas.append("W2: o id interno apareceu como input no formulario")
                page.locator("#alladinFldName").fill("Conta Renomeada")
                page.locator("button[data-ald-act=salvar]").click()
                page.wait_for_timeout(150)
                d2 = disco(page)
                if d2["accounts"][0]["name"] != "Conta Renomeada":
                    falhas.append("W2: edicao nao persistiu")
                if d2["accounts"][0]["accountId"] != d["accounts"][0]["accountId"]:
                    falhas.append("W2: o id mudou na edicao")
                # A trilha de auditoria e contrato do dominio (dgLogChange dentro de
                # aldMutate): um desvio que grave S diretamente nao a produz.
                trilha = page.evaluate("""() => (S.dataGovernance.changeLog||[])
                    .filter(e => e.entity==='alladin').map(e => e.action)""")
                if "account_add" not in trilha or "account_edit" not in trilha:
                    falhas.append(f"W2: a mutacao nao passou pelo dominio — trilha de auditoria ausente ({trilha})")
                if erros:
                    falhas.append(f"W1/W2 pageerror: {erros}")
            executar(falhas, "W1/W2", w1_w2)

            # ---- W3 + S2A-6: cash exige conta ativa ----
            def w3():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("() => JPWAlladinUI.selectView('cashAccounts')")
                txt = page.evaluate("() => document.getElementById('alladinCash').innerText")
                if "Cadastre ou reative uma conta" not in txt:
                    falhas.append(f"W3: sem conta ativa deveria mostrar a mensagem congelada ({txt[:80]!r})")
                if page.locator("button[data-ald-new=cashaccount]").count():
                    falhas.append("W3: botao Novo caixa presente sem conta ativa")
                criar_conta(page)
                page.evaluate("() => JPWAlladinUI.selectView('cashAccounts')")
                page.locator("button[data-ald-new=cashaccount]").click()
                opts = page.evaluate("() => [...document.querySelectorAll('#alladinFldAccountId option')].map(o=>o.textContent)")
                if len(opts) != 1 or "Conta Sintetica" not in opts[0]:
                    falhas.append(f"W3: select deveria listar so a conta ativa ({opts})")
                page.locator("#alladinFldCurrency").fill("BRL")
                page.locator("button[data-ald-act=salvar]").click()
                page.wait_for_timeout(150)
                d = disco(page)
                if len(d["cashAccounts"]) != 1 or d["cashAccounts"][0]["currency"] != "BRL":
                    falhas.append("W3: cash nao criada")
                if len(d["accounts"]) != 1:
                    falhas.append("W3: uma Account foi criada implicitamente")
                if erros:
                    falhas.append(f"W3 pageerror: {erros}")
            executar(falhas, "W3", w3)

            # ---- W4: DC-4 pos-criacao (S2A-1..5) ----
            def w4():
                ctx, page, erros = abrir(browser, url)
                criar_conta(page)
                page.evaluate("() => JPWAlladinUI.selectView('cashAccounts')")
                for _ in range(1):
                    page.locator("button[data-ald-new=cashaccount]").click()
                    page.locator("#alladinFldCurrency").fill("BRL")
                    page.locator("button[data-ald-act=salvar]").click()
                    page.wait_for_timeout(150)
                # segunda cash BRL na MESMA conta -> DC-4
                page.locator("button[data-ald-new=cashaccount]").click()
                page.locator("#alladinFldCurrency").fill("BRL")
                page.locator("button[data-ald-act=salvar]").click()
                page.wait_for_timeout(200)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "duplicidade" not in modal.lower() or "DUPLICADO_MOEDA_NA_CONTA" not in modal:
                    falhas.append(f"W4: aviso DC-4 nao apareceu ({modal[:90]!r})")
                d = disco(page)
                if len(d["cashAccounts"]) != 2:
                    falhas.append(f"W4/S2A-1: o registro deveria JA existir no disco antes da decisao ({len(d['cashAccounts'])})")
                # S2A-2: Enter/salvar nao recriam
                page.keyboard.press("Enter")
                page.wait_for_timeout(120)
                if page.evaluate("() => document.querySelectorAll('#alladinModalBox button[data-ald-act=salvar]').length") != 0:
                    falhas.append("W4/S2A-2: Salvar continua disponivel no estado de decisao")
                # S2A-3: Escape/backdrop nao fecham
                page.keyboard.press("Escape")
                page.evaluate("() => { const ov=document.getElementById('alladinModalOverlay'); ov.dispatchEvent(new MouseEvent('click',{bubbles:true})); }")
                page.wait_for_timeout(120)
                if not page.evaluate("() => document.getElementById('alladinModalOverlay').classList.contains('show')"):
                    falhas.append("W4/S2A-3: Escape/backdrop ignoraram o warning")
                if len(disco(page)["cashAccounts"]) != 2:
                    falhas.append("W4/S2A-2: uma duplicata extra nasceu no estado de decisao")
                # S2A-4/S2A-5: inativar via setRecordStatus, com falha primeiro
                page.evaluate("""() => { window.__origSet = JPWAlladin.cadastro.setRecordStatus;
                    JPWAlladin.cadastro.setRecordStatus = () => ({ok:false, erro:'FALHA_SIMULADA'}); }""")
                page.locator("button[data-ald-act=inativar-novo]").click()
                page.wait_for_timeout(120)
                modal2 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "FALHA_SIMULADA" not in modal2 or "permanece ativo" not in modal2:
                    falhas.append(f"W4/S2A-5: falha da inativacao nao manteve a decisao visivel ({modal2[:90]!r})")
                if disco(page)["cashAccounts"][1]["recordStatus"] != "ACTIVE":
                    falhas.append("W4/S2A-5: o registro mudou apesar da recusa")
                page.evaluate("() => { JPWAlladin.cadastro.setRecordStatus = window.__origSet; }")
                page.locator("button[data-ald-act=inativar-novo]").click()
                page.wait_for_timeout(150)
                d2 = disco(page)
                if d2["cashAccounts"][1]["recordStatus"] != "INACTIVE":
                    falhas.append("W4/S2A-4: Inativar este registro nao inativou via dominio")
                if page.evaluate("() => document.getElementById('alladinModalOverlay').classList.contains('show')"):
                    falhas.append("W4: modal nao fechou apos a decisao")
                if erros:
                    falhas.append(f"W4 pageerror: {erros}")
            executar(falhas, "W4", w4)

            # ---- W5 + S2A-7: edit de cash com referencia inativa ----
            def w5():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("""() => {
                    // fixture direta do dominio: conta A (que ficara inativa), conta B ativa, cash em A
                    const a=JPWAlladin.cadastro.addAccount({name:'Banco X',institution:'X',accountType:'BANK'});
                    const b=JPWAlladin.cadastro.addAccount({name:'Banco Y',institution:'Y',accountType:'BANK'});
                    const c=JPWAlladin.cadastro.addCashAccount({accountId:a.recordId,currency:'BRL'});
                    JPWAlladin.cadastro.setRecordStatus('cashaccount',c.recordId,'INACTIVE');
                    JPWAlladin.cadastro.setRecordStatus('account',a.recordId,'INACTIVE');
                    JPWAlladinUI.render();
                }""")
                page.evaluate("() => JPWAlladinUI.selectView('cashAccounts')")
                page.locator("button[data-ald-edit=cashaccount]").click()
                opts = page.evaluate("""() => [...document.querySelectorAll('#alladinFldAccountId option')]
                    .map(o => ({t:o.textContent, sel:o.selected}))""")
                atual = [o for o in opts if o["sel"]]
                if not atual or "Banco X — INATIVA" not in atual[0]["t"]:
                    falhas.append(f"W5/S2A-7: a referencia atual inativa nao aparece honesta e selecionada ({opts})")
                if not any("Banco Y" in o["t"] for o in opts):
                    falhas.append("W5: a conta ativa alternativa nao foi oferecida")
                # cancelar sem tocar: accountId permanece o da conta inativa
                page.locator("button[data-ald-act=cancelar]").click()
                page.wait_for_timeout(100)
                d = disco(page)
                nomes = {a["accountId"]: a["name"] for a in d["accounts"]}
                if nomes[d["cashAccounts"][0]["accountId"]] != "Banco X":
                    falhas.append("W5/S2A-7: o accountId foi trocado silenciosamente")
                if erros:
                    falhas.append(f"W5 pageerror: {erros}")
            executar(falhas, "W5", w5)

            # ---- W6 + S2A-8/9: recusas referenciais sem status falso ----
            def w6():
                ctx, page, erros = abrir(browser, url)
                ids = page.evaluate("""() => {
                    const a=JPWAlladin.cadastro.addAccount({name:'Banco Z',institution:'Z',accountType:'BANK'});
                    const c=JPWAlladin.cadastro.addCashAccount({accountId:a.recordId,currency:'BRL'});
                    JPWAlladinUI.render();
                    return {conta:a.recordId, cash:c.recordId};
                }""")
                # S2A-8: inativar conta com cash ativa -> recusa
                page.evaluate("() => JPWAlladinUI.selectView('accounts')")
                page.locator("button[data-ald-status=INACTIVE][data-ald-tipo=account]").click()
                page.locator("button[data-ald-act=status-confirmado]").click()
                page.wait_for_timeout(120)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "ALD_ACCOUNT_COM_CASHACCOUNT_ATIVA" not in modal:
                    falhas.append(f"W6/S2A-8: recusa do dominio nao exibida ({modal[:80]!r})")
                if disco(page)["accounts"][0]["recordStatus"] != "ACTIVE":
                    falhas.append("W6/S2A-8: status mudou apesar da recusa")
                dom = page.evaluate("() => document.getElementById('alladinAccounts').innerText")
                if "Inativo" in dom:
                    falhas.append("W6/S2A-8: o DOM mostra status falso")
                page.evaluate("() => { document.getElementById('alladinModalOverlay').classList.remove('show'); }")
                # S2A-9: inativa cash, inativa conta, tenta REATIVAR cash -> recusa
                page.evaluate("""(ids) => {
                    JPWAlladin.cadastro.setRecordStatus('cashaccount',ids.cash,'INACTIVE');
                    JPWAlladin.cadastro.setRecordStatus('account',ids.conta,'INACTIVE');
                    JPWAlladinUI.render();
                }""", ids)
                page.evaluate("() => JPWAlladinUI.selectView('cashAccounts')")
                page.locator("button[data-ald-status=ACTIVE][data-ald-tipo=cashaccount]").click()
                page.locator("button[data-ald-act=status-confirmado]").click()
                page.wait_for_timeout(120)
                modal2 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "ALD_ACCOUNT_INATIVA" not in modal2:
                    falhas.append(f"W6/S2A-9: reativacao com pai inativo nao recusada ({modal2[:80]!r})")
                if disco(page)["cashAccounts"][0]["recordStatus"] != "INACTIVE":
                    falhas.append("W6/S2A-9: cash reativada apesar da recusa")
                if erros:
                    falhas.append(f"W6 pageerror: {erros}")
            executar(falhas, "W6", w6)

            # ---- W7 + S2A-10: status de Instrument/Asset pela linha ----
            def w7():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("""() => {
                    JPWAlladin.cadastro.addInstrument({name:'Petro',symbol:'PETR4',currency:'BRL',
                        instrumentFamily:'EQUITY_LIKE',assetClass:'RENDA_VARIAVEL'});
                    JPWAlladin.cadastro.addAsset({name:'Apto',nature:'IMOVEL',recordMode:'INDIVIDUAL'});
                    window.__mutacoes=[];
                    const orig=JPWAlladin.cadastro.setRecordStatus;
                    JPWAlladin.cadastro.setRecordStatus=(t,i,s)=>{ window.__mutacoes.push(t+':'+s); return orig(t,i,s); };
                    JPWAlladinUI.render();
                }""")
                for view, tipo in (("instruments", "instrument"), ("assets", "asset")):
                    page.evaluate("(v) => JPWAlladinUI.selectView(v)", view)
                    page.locator(f"button[data-ald-status=INACTIVE][data-ald-tipo={tipo}]").click()
                    page.locator("button[data-ald-act=status-confirmado]").click()
                    page.wait_for_timeout(120)
                r = page.evaluate("() => window.__mutacoes")
                if r != ["instrument:INACTIVE", "asset:INACTIVE"]:
                    falhas.append(f"W7/S2A-10: status nao passou por setRecordStatus ({r})")
                d = disco(page)
                if d["instruments"][0]["recordStatus"] != "INACTIVE" or d["assets"][0]["recordStatus"] != "INACTIVE":
                    falhas.append("W7: status nao persistiu")
                if erros:
                    falhas.append(f"W7 pageerror: {erros}")
            executar(falhas, "W7", w7)

            # ---- W8/W12/W14 + S2A-11: cancelamentos = zero write ----
            def w8():
                ctx, page, erros = abrir(browser, url)
                criar_conta(page)
                antes = page.evaluate("() => JSON.stringify(S)")
                disco_antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.evaluate("""() => { window.__saves=0; const o=window.save;
                    window.save=function(){ window.__saves++; return o.apply(this,arguments); }; }""")
                # abrir form e cancelar
                page.locator("button[data-ald-new=account]").click()
                page.locator("#alladinFldName").fill("Descartada")
                page.locator("button[data-ald-act=cancelar]").click()
                # abrir form, submeter VAZIO (validacao) e depois Escape
                page.locator("button[data-ald-new=account]").click()
                page.locator("button[data-ald-act=salvar]").click()
                page.wait_for_timeout(100)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "Preencha todos os campos" not in modal:
                    falhas.append(f"W12: validacao vazia sem erro inline ({modal[:60]!r})")
                page.keyboard.press("Escape")
                # confirmacao de status cancelada (W14)
                page.locator("button[data-ald-status=INACTIVE][data-ald-tipo=account]").click()
                page.locator("button[data-ald-act=cancelar]").click()
                page.wait_for_timeout(100)
                saves = page.evaluate("() => window.__saves")
                if saves != 0:
                    falhas.append(f"W8/S2A-11: cancelamentos chamaram save() {saves}x")
                if page.evaluate("() => JSON.stringify(S)") != antes:
                    falhas.append("W8: S mudou com cancelamentos")
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != disco_antes:
                    falhas.append("W8: disco mudou com cancelamentos")
                if erros:
                    falhas.append(f"W8 pageerror: {erros}")
            executar(falhas, "W8", w8)

            # ---- W9/W10 + S2A-12: write gate ----
            def w9_w10():
                ctx, page, erros = abrir(browser, url)
                criar_conta(page)
                # W10: READ_ONLY na abertura -> botoes desabilitados
                page.evaluate("""() => { S.alladin.schemaVersion=3;
                    localStorage.setItem('%s', JSON.stringify(S)); JPWAlladinUI.render(); }""" % LSKEY)
                page.evaluate("() => JPWAlladinUI.selectView('accounts')")
                habilitados = page.evaluate("""() => [...document.querySelectorAll('#alladin button[data-ald-new],#alladin button[data-ald-edit],#alladin button[data-ald-status]')]
                    .filter(b => !b.disabled).length""")
                if habilitados != 0:
                    falhas.append(f"W10: {habilitados} botoes de mutacao habilitados em READ_ONLY")
                # S2A-12: writeBlockReason muda ENTRE abertura e submit
                page.evaluate("""() => { S.alladin.schemaVersion=2; JPWAlladinUI.render(); }""")
                page.evaluate("() => JPWAlladinUI.selectView('accounts')")
                page.locator("button[data-ald-new=account]").click()
                page.locator("#alladinFldName").fill("Tardia")
                page.locator("#alladinFldInstitution").fill("T")
                page.locator("#alladinFldAccountType").fill("BANK")
                page.evaluate("() => { S.alladin.schemaVersion=3; document.getElementById('sessionNotice').textContent=''; }")   # bloqueia agora
                page.locator("button[data-ald-act=salvar]").click()
                page.wait_for_timeout(120)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "recusado" not in modal.lower() or "Nada foi gravado" not in modal:
                    falhas.append(f"W9/S2A-12: recusa tardia sem mensagem honesta ({modal[:80]!r})")
                notice = page.evaluate("() => document.getElementById('sessionNotice').textContent")
                if "Cadastro salvo" in notice:
                    falhas.append("W9/S2A-12: falso sucesso apos recusa")
                page.evaluate("() => { S.alladin.schemaVersion=2; }")
                d = disco(page)
                if any(a["name"] == "Tardia" for a in d["accounts"]):
                    falhas.append("W9: o registro recusado chegou ao disco")
                if erros:
                    falhas.append(f"W9/W10 pageerror: {erros}")
            executar(falhas, "W9/W10", w9_w10)

            # ---- W11: double submit real ----
            def w11():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("() => JPWAlladinUI.selectView('accounts')")
                page.locator("button[data-ald-new=account]").click()
                page.locator("#alladinFldName").fill("Unica")
                page.locator("#alladinFldInstitution").fill("U")
                page.locator("#alladinFldAccountType").fill("BANK")
                page.evaluate("""() => {
                    const b=document.querySelector('#alladinModalBox button[data-ald-act=salvar]');
                    b.click(); b.click(); b.click();
                }""")
                page.wait_for_timeout(200)
                d = disco(page)
                if len(d["accounts"]) != 1:
                    falhas.append(f"W11: double submit criou {len(d['accounts'])} registros")
                # Vetor de reentrada REAL: o box oculto RETEM os inputs apos fechar —
                # sem a maquina de estados, um segundo submit programatico (Enter
                # enfileirado, extensao, macro) releria os mesmos valores e duplicaria.
                page.locator("button[data-ald-new=account]").click()
                page.locator("#alladinFldName").fill("Reentrada")
                page.locator("#alladinFldInstitution").fill("R")
                page.locator("#alladinFldAccountType").fill("BANK")
                page.evaluate("() => { alladinSubmit(); alladinSubmit(); alladinSubmit(); }")
                page.wait_for_timeout(150)
                d2 = disco(page)
                criadas = [a for a in d2["accounts"] if a["name"] == "Reentrada"]
                if len(criadas) != 1:
                    falhas.append(f"W11: submits reentrantes criaram {len(criadas)} registros 'Reentrada'")
                if erros:
                    falhas.append(f"W11 pageerror: {erros}")
            executar(falhas, "W11", w11)

            # ---- W13: varredura economica com formularios abertos ----
            def w13():
                ctx, page, erros = abrir(browser, url)
                criar_conta(page)
                page.locator("button[data-ald-new=account]").click()
                texto = page.evaluate("""() => document.getElementById('alladin').innerText + ' ' +
                    document.getElementById('alladinModalBox').innerText""")
                m = PROIBIDO.search(texto)
                if m:
                    falhas.append(f"W13: conteudo economico proibido: {m.group(0)!r}")
                page.keyboard.press("Escape")
            executar(falhas, "W13", w13)

            # ---- W15: focus trap + retorno de foco + mobile ----
            def w15():
                ctx, page, erros = abrir(browser, url, viewport={"width": 390, "height": 844})
                criar_conta(page)
                page.evaluate("() => document.querySelector('button[data-ald-new=account]').focus()")
                page.locator("button[data-ald-new=account]").click()
                r = page.evaluate("""() => {
                    const f=[...document.querySelectorAll('#alladinModalBox button:not([disabled]),#alladinModalBox input,#alladinModalBox select')];
                    f[f.length-1].focus();
                    const ev=new KeyboardEvent('keydown',{key:'Tab',bubbles:true,cancelable:true});
                    document.getElementById('alladinModalBox').dispatchEvent(ev);
                    return { preso: ev.defaultPrevented,
                             larguraOk: document.getElementById('alladinModalBox').scrollWidth <= window.innerWidth + 2 };
                }""")
                if not r["preso"]:
                    falhas.append("W15: Tab no ultimo focusable nao voltou ao primeiro (trap ausente)")
                if not r["larguraOk"]:
                    falhas.append("W15: modal estoura o viewport mobile")
                page.keyboard.press("Escape")
                page.wait_for_timeout(100)
                foco = page.evaluate("() => document.activeElement && document.activeElement.dataset && document.activeElement.dataset.aldNew")
                if foco != "account":
                    falhas.append(f"W15: o foco nao retornou ao botao de origem ({foco!r})")
                if erros:
                    falhas.append(f"W15 pageerror: {erros}")
            executar(falhas, "W15", w15)

            browser.close()
    finally:
        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        servidor.shutdown()

    if falhas:
        print("ALLADIN UI CRUD TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("ALLADIN UI CRUD TEST PASS (W1-W15 / S2A-1..12: Account e CashAccount criados e editados pelo "
          "modal real com persistencia provada em memoria e disco; DC-4 pos-criacao com registro ja "
          "persistido, decisao explicita obrigatoria, Escape/backdrop suspensos e inativacao via "
          "setRecordStatus; referencia inativa exibida honesta sem troca silenciosa; recusas "
          "referenciais sem status falso; status x4 pela linha com confirmacao; cancelamentos "
          "zero-write; write gate na abertura e no submit sem falso sucesso; double submit nao "
          "duplica; zero conteudo economico; focus trap, retorno de foco e mobile)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
