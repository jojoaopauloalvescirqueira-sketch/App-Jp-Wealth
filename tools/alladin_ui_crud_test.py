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
    # QA-D1: Service Worker BLOQUEADO. Boota o app real; sem bloquear o SW, o
    # updateFxRates do boot escapa do page.route e escreve no disco, contaminando
    # as comparacoes byte-a-byte de persistencia. O SW tem suite propria.
    ctx = browser.new_context(viewport=viewport or {"width": 1440, "height": 900},
                              service_workers="block")
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


def colecao(page, nome):
    """Colecao do disco tolerante ao estado ainda NAO persistido: antes do
    primeiro save() o agregado nem existe, e ausencia e' o mesmo que vazio para
    quem pergunta 'o registro recusado chegou ao disco?'."""
    d = disco(page)
    return (d or {}).get(nome) or []


# Participacao de owners e' cadastral por decisao humana do gate S2-B ("nao se
# refere a performance nem a rentabilidade"), entao o '%' DESTE contexto sai da
# varredura antes dela rodar — qualquer outro '%' continua proibido.
PARTICIPACAO = re.compile(r"Participação (?:\(%\)|atribuída: (?:[\d.,]+%|—))")


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
                page.evaluate("""() => { S.alladin.schemaVersion=7;
                    localStorage.setItem('%s', JSON.stringify(S)); JPWAlladinUI.render(); }""" % LSKEY)
                page.evaluate("() => JPWAlladinUI.selectView('accounts')")
                habilitados = page.evaluate("""() => [...document.querySelectorAll('#alladin button[data-ald-new],#alladin button[data-ald-edit],#alladin button[data-ald-status]')]
                    .filter(b => !b.disabled).length""")
                if habilitados != 0:
                    falhas.append(f"W10: {habilitados} botoes de mutacao habilitados em READ_ONLY")
                # S2A-12: writeBlockReason muda ENTRE abertura e submit
                page.evaluate("""() => { S.alladin.schemaVersion=6; JPWAlladinUI.render(); }""")
                page.evaluate("() => JPWAlladinUI.selectView('accounts')")
                page.locator("button[data-ald-new=account]").click()
                page.locator("#alladinFldName").fill("Tardia")
                page.locator("#alladinFldInstitution").fill("T")
                page.locator("#alladinFldAccountType").fill("BANK")
                page.evaluate("() => { S.alladin.schemaVersion=7; document.getElementById('sessionNotice').textContent=''; }")   # bloqueia agora
                page.locator("button[data-ald-act=salvar]").click()
                page.wait_for_timeout(120)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "recusado" not in modal.lower() or "Nada foi gravado" not in modal:
                    falhas.append(f"W9/S2A-12: recusa tardia sem mensagem honesta ({modal[:80]!r})")
                notice = page.evaluate("() => document.getElementById('sessionNotice').textContent")
                if "Cadastro salvo" in notice:
                    falhas.append("W9/S2A-12: falso sucesso apos recusa")
                page.evaluate("() => { S.alladin.schemaVersion=6; }")
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
                texto = page.evaluate("""() => {
                    const cadastrais=['instruments','assets','accounts','cashAccounts'];
                    const ativo=cadastrais
                        .map(v=>document.querySelector('[data-alladin-panel="'+v+'"]'))
                        .find(el=>el && !el.hidden);
                    return (ativo?ativo.innerText:'') + ' ' +
                        document.getElementById('alladinModalBox').innerText;
                }""")
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

            # ================= C3-S2-B — INSTRUMENT =========================
            def abrir_form_instrument(page, **campos):
                page.evaluate("() => JPWAlladinUI.selectView('instruments')")
                page.locator("button[data-ald-new=instrument]").click()
                preencher_instrument(page, **campos)

            def preencher_instrument(page, name=None, symbol=None, family=None, asset_class=None,
                                     currency=None, exchange=None, country=None, network=None):
                if name is not None:
                    page.locator("#alladinFldName").fill(name)
                if symbol is not None:
                    page.locator("#alladinFldSymbol").fill(symbol)
                if family is not None:
                    page.locator("#alladinFldFamily").select_option(family)
                if asset_class is not None:
                    page.locator("#alladinFldAssetClass").fill(asset_class)
                if currency is not None and page.locator("#alladinFldCurrency:not([disabled])").count():
                    page.locator("#alladinFldCurrency").fill(currency)
                if exchange is not None:
                    page.locator("#alladinFldExchange").fill(exchange)
                if country is not None:
                    page.locator("#alladinFldCountry").fill(country)
                if network is not None:
                    page.locator("#alladinFldNetwork").fill(network)

            def salvar(page, espera=180):
                page.locator("#alladinModalBox button[data-ald-act=salvar]").click()
                page.wait_for_timeout(espera)

            # ---- I1/I2/I3: create, edit e moeda imutavel -------------------
            def i1_i3():
                ctx, page, erros = abrir(browser, url)
                abrir_form_instrument(page, name="Petrobras PN", symbol="PETR4", family="EQUITY_LIKE",
                                      asset_class="RENDA_VARIAVEL", currency="BRL", exchange="B3", country="Brasil")
                salvar(page)
                d = disco(page)
                if len(d["instruments"]) != 1:
                    falhas.append(f"I1: instrumento nao chegou ao disco ({d['instruments']})")
                else:
                    r = d["instruments"][0]
                    if (r["name"], r["symbol"], r["currency"], r["instrumentFamily"], r["exchange"]) != \
                       ("Petrobras PN", "PETR4", "BRL", "EQUITY_LIKE", "B3"):
                        falhas.append(f"I1: campos divergem no disco ({r})")
                    if r["symbolHistory"] != [] or r["recordStatus"] != "ACTIVE":
                        falhas.append(f"I1: shape inicial errado ({r.get('symbolHistory')}, {r.get('recordStatus')})")
                trilha = page.evaluate("""() => (S.dataGovernance.changeLog||[])
                    .filter(e => e.entity==='alladin').map(e => e.action)""")
                if "instrument_add" not in trilha:
                    falhas.append(f"I1: mutacao nao passou pelo dominio ({trilha})")
                # I3: moeda desabilitada no edit e AUSENTE do patch
                page.locator("button[data-ald-edit=instrument]").click()
                if not page.evaluate("() => document.getElementById('alladinFldCurrency').disabled"):
                    falhas.append("I3: campo de moeda editavel na edicao")
                nota = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "não pode ser alterada neste cadastro" not in nota:
                    falhas.append("I3: texto da moeda imutavel ausente")
                page.evaluate("""() => { window.__patches=[]; const o=JPWAlladin.cadastro.editInstrument;
                    JPWAlladin.cadastro.editInstrument=(i,p)=>{ window.__patches.push(p); return o(i,p); }; }""")
                page.locator("#alladinFldName").fill("Petrobras Preferencial")
                salvar(page)
                patches = page.evaluate("() => window.__patches")
                if len(patches) != 1 or set(patches[0]) != {"name"}:
                    falhas.append(f"I2/I3: patch deveria conter SO name ({patches})")
                d2 = disco(page)
                if d2["instruments"][0]["name"] != "Petrobras Preferencial":
                    falhas.append("I2: edicao nao persistiu")
                if d2["instruments"][0]["currency"] != "BRL" or d2["instruments"][0]["exchange"] != "B3":
                    falhas.append("I2: campos nao tocados foram alterados")
                if erros:
                    falhas.append(f"I1/I3 pageerror: {erros}")
            executar(falhas, "I1/I2/I3", i1_i3)

            # ---- I4/I5: symbolHistory pelo dominio; historico ilegivel -----
            def i4_i5():
                ctx, page, erros = abrir(browser, url)
                abrir_form_instrument(page, name="Magazine", symbol="MGLU3", family="EQUITY_LIKE",
                                      asset_class="RENDA_VARIAVEL", currency="BRL", exchange="B3")
                salvar(page)
                # nenhum input de historico existe em NENHUM estado (assert estrutural)
                page.locator("button[data-ald-edit=instrument]").click()
                estrut = page.evaluate("""() => {
                    const box=document.getElementById('alladinModalBox');
                    return { campos:[...box.querySelectorAll('input,select,textarea')].map(i=>i.id||i.name||'').join(','),
                             hidden:box.querySelectorAll('input[type=hidden]').length };
                }""")
                for proibido in ("History", "historico", "recordStatus", "createdAt", "instrumentId"):
                    if proibido.lower() in estrut["campos"].lower():
                        falhas.append(f"I4: campo proibido virou input ({proibido})")
                if estrut["hidden"]:
                    falhas.append("I4: existe input hidden no formulario")
                page.evaluate("""() => { window.__patches=[]; const o=JPWAlladin.cadastro.editInstrument;
                    JPWAlladin.cadastro.editInstrument=(i,p)=>{ window.__patches.push(p); return o(i,p); }; }""")
                page.locator("#alladinFldSymbol").fill("MGLU4")
                salvar(page)
                p1 = page.evaluate("() => window.__patches")
                if len(p1) != 1 or "symbolHistory" in p1[0]:
                    falhas.append(f"I4: a UI enviou symbolHistory no patch ({p1})")
                page.locator("button[data-ald-edit=instrument]").click()
                page.locator("#alladinFldSymbol").fill("MGLU3")
                salvar(page)
                hist = page.evaluate("() => JPWAlladin.leitura.instruments()[0].symbolHistory.map(h=>h.symbol)")
                if hist != ["MGLU3", "MGLU4"]:
                    falhas.append(f"I4: historico A->B->A deveria ser [MGLU3, MGLU4] ({hist})")
                exibido = page.evaluate("""() => { document.querySelector('button[data-ald-edit=instrument]').click();
                    const el=document.querySelector('[data-ald-symbol-history]'); return el?el.innerText:''; }""")
                if "MGLU3" not in exibido or "MGLU4" not in exibido:
                    falhas.append(f"I4: historico nao exibido como leitura no edit ({exibido!r})")
                page.keyboard.press("Escape")
                # I5: historico ilegivel -> recusa honesta; status continua funcionando
                page.evaluate("""() => { S.alladin.instruments[0].symbolHistory='lixo'; save(); JPWAlladinUI.render(); }""")
                page.locator("button[data-ald-edit=instrument]").click()
                page.locator("#alladinFldName").fill("Outro nome")
                salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "ALD_SYMBOL_HISTORY_ILEGIVEL" not in modal or "Nada foi gravado" not in modal:
                    falhas.append(f"I5: recusa por historico ilegivel nao exibida ({modal[:100]!r})")
                if page.evaluate("() => JPWAlladin.leitura.instruments()[0].name") == "Outro nome":
                    falhas.append("I5: edicao persistiu apesar da recusa")
                page.keyboard.press("Escape")
                page.wait_for_timeout(100)
                page.locator("button[data-ald-status=INACTIVE][data-ald-tipo=instrument]").click()
                page.locator("button[data-ald-act=status-confirmado]").click()
                page.wait_for_timeout(150)
                if disco(page)["instruments"][0]["recordStatus"] != "INACTIVE":
                    falhas.append("I5: rota de status bloqueada junto com o edit")
                if erros:
                    falhas.append(f"I4/I5 pageerror: {erros}")
            executar(falhas, "I4/I5", i4_i5)

            # ---- I6/I7/I8: CRYPTO/network + externalIdentifiers ------------
            def i6_i8():
                ctx, page, erros = abrir(browser, url)
                abrir_form_instrument(page, name="Tether", symbol="USDT", family="CRYPTO",
                                      asset_class="CRIPTO", currency="USD")
                if page.evaluate("() => document.getElementById('alladinFldNetworkWrap').hidden"):
                    falhas.append("I6: campo Rede nao apareceu para CRYPTO")
                salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "rede (network)" not in modal.lower():
                    falhas.append(f"I6: pre-check de rede ausente ({modal[:90]!r})")
                if colecao(page, "instruments"):
                    falhas.append("I6: instrumento nasceu sem rede")
                # bypass do pre-check: o DOMINIO tem de recusar sozinho
                r = page.evaluate("""() => JPWAlladin.cadastro.addInstrument({name:'T', symbol:'USDT',
                    currency:'USD', instrumentFamily:'CRYPTO', assetClass:'CRIPTO'})""")
                if r.get("ok") is not False or r.get("erro") != "ALD_CRYPTO_SEM_NETWORK":
                    falhas.append(f"I6: dominio nao recusou cripto sem rede ({r})")
                # I7: com rede persiste, e a rede vai para externalIdentifiers.network
                page.locator("#alladinFldNetwork").fill("ethereum")
                page.locator("button[data-ald-act=ext-add]").click()
                page.locator("[data-ald-ext-k]").last.fill("isin")
                page.locator("[data-ald-ext-v]").last.fill("BRUSDT000001")
                salvar(page)
                d = disco(page)
                if len(d["instruments"]) != 1:
                    falhas.append(f"I7: cripto com rede nao persistiu ({d['instruments']})")
                else:
                    ext = d["instruments"][0]["externalIdentifiers"]
                    if ext != {"isin": "BRUSDT000001", "network": "ethereum"}:
                        falhas.append(f"I7/I8: identificadores divergem ({ext})")
                # I8: linha vazia e' omitida; linha meio-preenchida recusa local
                page.locator("button[data-ald-edit=instrument]").click()
                if page.evaluate("""() => [...document.querySelectorAll('[data-ald-ext-k]')].map(i=>i.value).includes('network')"""):
                    falhas.append("I8: network duplicou como linha generica no editor")
                page.locator("button[data-ald-act=ext-add]").click()
                salvar(page)   # linha totalmente vazia: deve ser OMITIDA, nao erro
                if page.evaluate("() => document.getElementById('alladinModalOverlay').classList.contains('show')"):
                    modal2 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                    falhas.append(f"I8: linha vazia deveria ser omitida ({modal2[:80]!r})")
                page.locator("button[data-ald-edit=instrument]").click()
                page.locator("button[data-ald-act=ext-add]").click()
                page.locator("[data-ald-ext-k]").last.fill("cnpj")
                salvar(page)
                modal3 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "chave e conteúdo" not in modal3:
                    falhas.append(f"I8: linha meio-preenchida deveria recusar ({modal3[:90]!r})")
                rascunho = page.evaluate("() => document.querySelectorAll('[data-ald-ext-row]').length")
                if rascunho != 2:
                    falhas.append(f"I8: rascunho perdido no erro inline ({rascunho} linhas)")
                if colecao(page, "instruments")[0]["externalIdentifiers"].get("cnpj"):
                    falhas.append("I8: linha invalida foi gravada")
                page.evaluate("() => { alladinForm.estado='EDITING'; alladinModalDismiss(); }")
                if erros:
                    falhas.append(f"I6/I8 pageerror: {erros}")
            executar(falhas, "I6/I7/I8", i6_i8)

            # ---- I9 + WT4: moeda fora do runtime = informativo, nunca decisao
            def i9():
                ctx, page, erros = abrir(browser, url)
                abrir_form_instrument(page, name="ETF Europa", symbol="EEUR", family="FUND_LIKE",
                                      asset_class="FUNDO", currency="EUR")
                salvar(page)
                if page.evaluate("() => document.getElementById('alladinModalOverlay').classList.contains('show')"):
                    falhas.append("I9/WT4: aviso informativo abriu estado de decisao")
                notice = page.evaluate("() => document.getElementById('sessionNotice').innerText")
                if "MOEDA_FORA_DO_SUPORTE_DE_RUNTIME" not in notice:
                    falhas.append(f"I9: codigo do aviso informativo perdido ({notice!r})")
                if "fora do suporte" not in notice:
                    falhas.append(f"I9: aviso nao humanizado ({notice!r})")
                if "Inativar" in notice:
                    falhas.append("I9/WT4: aviso informativo ofereceu inativacao")
                if len(disco(page)["instruments"]) != 1:
                    falhas.append("I9: instrumento com moeda valida nao persistiu")
                if erros:
                    falhas.append(f"I9 pageerror: {erros}")
            executar(falhas, "I9", i9)

            # ---- I10/I11/I12: cancel, double submit, persistencia recusada --
            def i10_i12():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("() => JPWAlladinUI.selectView('instruments')")
                antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.evaluate("""() => { window.__saves=0; const o=window.save;
                    window.save=function(){ window.__saves++; return o.apply(this,arguments); }; }""")
                abrir_form_instrument(page, name="Descartado", symbol="XXXX3", family="EQUITY_LIKE",
                                      asset_class="y", currency="BRL")
                page.locator("button[data-ald-act=cancelar]").click()
                page.wait_for_timeout(120)
                if page.evaluate("() => window.__saves") != 0:
                    falhas.append("I10: cancelar chamou save()")
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != antes:
                    falhas.append("I10: disco mudou com cancelamento")
                # I11: double submit + reentrada programatica
                abrir_form_instrument(page, name="Unico", symbol="UNIC3", family="EQUITY_LIKE",
                                      asset_class="y", currency="BRL")
                page.evaluate("""() => { const b=document.querySelector('#alladinModalBox button[data-ald-act=salvar]');
                    b.click(); b.click(); b.click(); }""")
                page.wait_for_timeout(200)
                abrir_form_instrument(page, name="Reentrante", symbol="REEN3", family="EQUITY_LIKE",
                                      asset_class="y", currency="BRL")
                page.evaluate("() => { alladinSubmit(); alladinSubmit(); }")
                page.wait_for_timeout(200)
                nomes = [i["name"] for i in colecao(page, "instruments")]
                if nomes.count("Unico") != 1 or nomes.count("Reentrante") != 1:
                    falhas.append(f"I11: submits duplicaram registros ({nomes})")
                # I12: persistencia recusada -> sem falso sucesso, rascunho vivo
                page.evaluate("""() => { document.getElementById('sessionNotice').textContent='';
                    window.__saveOrig=window.save; window.save=()=>false; }""")
                abrir_form_instrument(page, name="Recusado", symbol="RECU3", family="EQUITY_LIKE",
                                      asset_class="y", currency="BRL")
                salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "persistencia recusada" not in modal:
                    falhas.append(f"I12: recusa de persistencia nao exibida ({modal[:90]!r})")
                if page.evaluate("() => document.getElementById('alladinFldName').value") != "Recusado":
                    falhas.append("I12: rascunho perdido apos recusa de persistencia")
                notice = page.evaluate("() => document.getElementById('sessionNotice').innerText")
                if "Cadastro salvo" in notice:
                    falhas.append("I12: falso sucesso apos persistencia recusada")
                page.evaluate("() => { window.save=window.__saveOrig; alladinForm.estado='EDITING'; alladinModalDismiss(); }")
                if any(i["name"] == "Recusado" for i in colecao(page, "instruments")):
                    falhas.append("I12: registro recusado chegou ao disco")
                if erros:
                    falhas.append(f"I10/I12 pageerror: {erros}")
            executar(falhas, "I10/I11/I12", i10_i12)

            # ================= C3-S2-B — ASSET ==============================
            def abrir_form_asset(page):
                page.evaluate("() => JPWAlladinUI.selectView('assets')")
                page.locator("button[data-ald-new=asset]").click()

            def add_owner(page, nome, pct, self_=False):
                page.locator("button[data-ald-act=owner-add]").click()
                page.locator("[data-ald-owner-nome]").last.fill(nome)
                page.locator("[data-ald-owner-pct]").last.fill(pct)
                if self_:
                    page.locator("[data-ald-owner-self]").last.check()

            # ---- A1/A2/A3: create, edit patch-diff, lifecycle read-only ----
            def a1_a3():
                ctx, page, erros = abrir(browser, url)
                abrir_form_asset(page)
                page.locator("#alladinFldName").fill("Apartamento")
                page.locator("#alladinFldNature").fill("IMOVEL")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                page.locator("#alladinFldLocation").fill("Sao Paulo")
                page.locator("#alladinFldAcqDate").fill("2020-01-15")
                page.locator("#alladinFldTags").fill("moradia, Moradia , litoral, moradia")
                salvar(page)
                d = disco(page)
                if len(d["assets"]) != 1:
                    falhas.append(f"A1: bem nao persistiu ({d['assets']})")
                else:
                    a = d["assets"][0]
                    if a["lifecycleStatus"] != "ACTIVE" or a["recordStatus"] != "ACTIVE":
                        falhas.append(f"A1: shape inicial errado ({a})")
                    if a["category"] is not None or a["owners"] != []:
                        falhas.append(f"A1: defaults divergem ({a['category']}, {a['owners']})")
                    if a["acquisitionDate"] != "2020-01-15":
                        falhas.append(f"A11: data nao persistiu ({a['acquisitionDate']})")
                    if a["tags"] != ["moradia", "Moradia", "litoral"]:
                        falhas.append(f"A10: tags divergem apos higiene de UI ({a['tags']})")
                # A3: lifecycle nunca e input; A2: patch so do campo alterado
                page.locator("button[data-ald-edit=asset]").click()
                campos = page.evaluate("""() => [...document.querySelectorAll('#alladinModalBox input,#alladinModalBox select')]
                    .map(i=>i.id).join(',')""")
                if "ifecycle" in campos or "recordStatus" in campos:
                    falhas.append(f"A3: lifecycle/recordStatus viraram input ({campos})")
                txt = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "movimentações patrimoniais" not in txt:
                    falhas.append("A3: texto do estado patrimonial ausente")
                if "ALD-03" in txt:
                    falhas.append("A3: nome interno ALD-03 exposto ao usuario")
                page.evaluate("""() => { window.__patches=[]; const o=JPWAlladin.cadastro.editAsset;
                    JPWAlladin.cadastro.editAsset=(i,p)=>{ window.__patches.push(p); return o(i,p); }; }""")
                page.locator("#alladinFldCategory").fill("Residencial")
                salvar(page)
                p = page.evaluate("() => window.__patches")
                if len(p) != 1 or set(p[0]) != {"category"}:
                    falhas.append(f"A2: patch deveria conter SO category ({p})")
                d2 = disco(page)
                a2 = d2["assets"][0]
                if a2["category"] != "Residencial" or a2["tags"] != ["moradia", "Moradia", "litoral"] \
                   or a2["location"] != "Sao Paulo" or a2["acquisitionDate"] != "2020-01-15":
                    falhas.append(f"A2: campos nao tocados mudaram ({a2})")
                if erros:
                    falhas.append(f"A1/A3 pageerror: {erros}")
            executar(falhas, "A1/A2/A3", a1_a3)

            # ---- A4..A9: owners, shareBp e conversao ------------------------
            def a4_a9():
                ctx, page, erros = abrir(browser, url)
                # A5: soma exata 10000 sem aviso; isSelf:false omitido
                abrir_form_asset(page)
                page.locator("#alladinFldName").fill("Casa")
                page.locator("#alladinFldNature").fill("IMOVEL")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                add_owner(page, "JP", "66,67", self_=True)
                add_owner(page, "Ana", "33,33")
                total = page.evaluate("() => document.querySelector('[data-ald-owner-total]').innerText")
                if "100%" not in total:
                    falhas.append(f"A5: total cadastral ao vivo incorreto ({total!r})")
                salvar(page)
                d = disco(page)
                owners = d["assets"][0]["owners"]
                if owners != [{"name": "JP", "shareBp": 6667, "isSelf": True}, {"name": "Ana", "shareBp": 3333}]:
                    falhas.append(f"A4/A5: owners divergem (conversao ou isSelf) ({owners})")
                notice = page.evaluate("() => document.getElementById('sessionNotice').innerText")
                if "OWNERSHIP_PARCIAL" in notice:
                    falhas.append("A5: soma exata gerou aviso de parcial")
                # A7: soma < 100% -> sucesso + aviso, modal FECHA (nao e decisao)
                abrir_form_asset(page)
                page.locator("#alladinFldName").fill("Sitio")
                page.locator("#alladinFldNature").fill("IMOVEL")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                add_owner(page, "JP", "70", self_=True)
                salvar(page)
                if page.evaluate("() => document.getElementById('alladinModalOverlay').classList.contains('show')"):
                    falhas.append("A7: ownership parcial abriu estado de decisao")
                notice = page.evaluate("() => document.getElementById('sessionNotice').innerText")
                if "OWNERSHIP_PARCIAL_NAO_ATRIBUIDA" not in notice or "não soma o total" not in notice:
                    falhas.append(f"A7: aviso de parcial ausente ou nao humanizado ({notice!r})")
                if [o["shareBp"] for o in disco(page)["assets"][1]["owners"]] != [7000]:
                    falhas.append("A7: conversao 70% -> 7000bp falhou")
                # A6: soma > 100% recusada, zero write
                abrir_form_asset(page)
                page.locator("#alladinFldName").fill("Excesso")
                page.locator("#alladinFldNature").fill("IMOVEL")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                add_owner(page, "JP", "60", self_=True)
                add_owner(page, "Ana", "40,01")
                antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "ALD_OWNERSHIP_ACIMA_DE_100" not in modal:
                    falhas.append(f"A6: recusa de soma>100 nao exibida ({modal[:90]!r})")
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != antes:
                    falhas.append("A6: disco mudou apesar da recusa")
                # A8: dois "Sou eu" -> recusa do dominio
                page.locator("[data-ald-owner-pct]").last.fill("30")
                page.locator("[data-ald-owner-self]").last.check()
                salvar(page)
                modal2 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "ALD_MULTIPLOS_ISSELF" not in modal2:
                    falhas.append(f"A8: dois isSelf nao recusados ({modal2[:90]!r})")
                # terceira casa decimal: erro inline, zero submit
                page.evaluate("""() => { window.__chamou=0; const o=JPWAlladin.cadastro.addAsset;
                    JPWAlladin.cadastro.addAsset=(d)=>{ window.__chamou++; return o(d); }; }""")
                # o caso da terceira casa fica ISOLADO: sem isSelf duplicado e com
                # soma valida, so a precisao pode reprovar — mutante que arredonde
                # 3 casas em silencio e' acusado por ISSO, nao por outro erro.
                page.locator("[data-ald-owner-self]").last.uncheck()
                page.locator("[data-ald-owner-pct]").first.fill("10")
                page.locator("[data-ald-owner-pct]").last.fill("33,333")
                salvar(page)
                modal3 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "duas casas decimais" not in modal3:
                    falhas.append(f"shareBp: terceira casa nao recusada inline ({modal3[:90]!r})")
                if page.evaluate("() => window.__chamou") != 0:
                    falhas.append("shareBp: terceira casa chegou a submeter ao dominio")
                # A9: nome duplicado -> sucesso + aviso (nao decisao)
                page.locator("[data-ald-owner-self]").last.uncheck()
                page.locator("[data-ald-owner-nome]").last.fill("jp ")
                page.locator("[data-ald-owner-pct]").last.fill("40")
                salvar(page)
                if page.evaluate("() => document.getElementById('alladinModalOverlay').classList.contains('show')"):
                    falhas.append("A9: nome duplicado abriu estado de decisao")
                notice = page.evaluate("() => document.getElementById('sessionNotice').innerText")
                if "OWNER_NOME_DUPLICADO" not in notice:
                    falhas.append(f"A9: aviso de nome duplicado ausente ({notice!r})")
                if erros:
                    falhas.append(f"A4/A9 pageerror: {erros}")
            executar(falhas, "A4..A9", a4_a9)

            # ---- A12..A15 + patch-diff de owners/tags nao alterados ---------
            def a12_a15():
                ctx, page, erros = abrir(browser, url)
                # A12: DC-3 — natureza de caixa recusada pelo dominio
                abrir_form_asset(page)
                page.locator("#alladinFldName").fill("Cofre")
                page.locator("#alladinFldNature").fill("Dinheiro em casa")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "ALD_NATURE_DE_CAIXA_PROIBIDA" not in modal:
                    falhas.append(f"A12: DC-3 nao recusou natureza de caixa ({modal[:90]!r})")
                if colecao(page, "assets"):
                    falhas.append("A12: bem de natureza-caixa nasceu")
                page.locator("#alladinFldNature").fill("IMOVEL")
                add_owner(page, "JP", "50", self_=True)
                page.locator("#alladinFldTags").fill("praia")
                salvar(page)
                # patch-diff: editar SO o nome nao envia owners nem tags
                page.evaluate("""() => { window.__patches=[]; const o=JPWAlladin.cadastro.editAsset;
                    JPWAlladin.cadastro.editAsset=(i,p)=>{ window.__patches.push(p); return o(i,p); }; }""")
                page.locator("button[data-ald-edit=asset]").click()
                page.locator("#alladinFldName").fill("Cofre Renomeado")
                salvar(page)
                p = page.evaluate("() => window.__patches")
                if len(p) != 1 or set(p[0]) != {"name"}:
                    falhas.append(f"patch-diff: owners/tags nao alterados viajaram no patch ({p})")
                d = colecao(page, "assets")[0]
                if [o["shareBp"] for o in d["owners"]] != [5000] or d["tags"] != ["praia"]:
                    falhas.append(f"patch-diff: owners/tags sofreram alteracao ({d['owners']}, {d['tags']})")
                # A13: cancelar zero-write
                antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.locator("button[data-ald-edit=asset]").click()
                page.locator("#alladinFldName").fill("Nao salvo")
                add_owner(page, "Fantasma", "10")
                page.locator("button[data-ald-act=cancelar]").click()
                page.wait_for_timeout(120)
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != antes:
                    falhas.append("A13: cancelar alterou o disco")
                # A14: double submit em Asset
                abrir_form_asset(page)
                page.locator("#alladinFldName").fill("Duplo")
                page.locator("#alladinFldNature").fill("BEM_DURAVEL")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                page.evaluate("""() => { const b=document.querySelector('#alladinModalBox button[data-ald-act=salvar]');
                    b.click(); b.click(); }""")
                page.wait_for_timeout(200)
                if [a["name"] for a in colecao(page, "assets")].count("Duplo") != 1:
                    falhas.append("A14: double submit duplicou o bem")
                # A15: persistencia recusada
                page.evaluate("""() => { document.getElementById('sessionNotice').textContent='';
                    window.__saveOrig=window.save; window.save=()=>false; }""")
                abrir_form_asset(page)
                page.locator("#alladinFldName").fill("Recusado")
                page.locator("#alladinFldNature").fill("BEM_DURAVEL")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                salvar(page)
                modal2 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "persistencia recusada" not in modal2:
                    falhas.append(f"A15: recusa de persistencia nao exibida ({modal2[:90]!r})")
                if "Cadastro salvo" in page.evaluate("() => document.getElementById('sessionNotice').innerText"):
                    falhas.append("A15: falso sucesso apos recusa")
                page.evaluate("() => { window.save=window.__saveOrig; alladinForm.estado='EDITING'; alladinModalDismiss(); }")
                if erros:
                    falhas.append(f"A12/A15 pageerror: {erros}")
            executar(falhas, "A12..A15", a12_a15)

            # ================= WARNINGS (WT1..WT5) ==========================
            def wt():
                ctx, page, erros = abrir(browser, url)
                # WT1: DUPLICADO em CREATE -> COMMITTED_WARNING com copia de criacao
                for nome in ("Vale", "Vale de novo"):
                    abrir_form_instrument(page, name=nome, symbol="VALE3", family="EQUITY_LIKE",
                                          asset_class="RENDA_VARIAVEL", currency="BRL", exchange="B3")
                    salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "foi criado" not in modal:
                    falhas.append(f"WT1: copia de CRIACAO ausente no estado de decisao ({modal[:110]!r})")
                if "mesmo símbolo" not in modal or "DUPLICADO_SYMBOL_EXCHANGE_CURRENCY" not in modal:
                    falhas.append(f"WT1: aviso nao humanizado ou codigo perdido ({modal[:110]!r})")
                page.locator("button[data-ald-act=manter]").click()
                page.wait_for_timeout(150)
                # WT2: DUPLICADO em EDIT -> copia de ALTERACAO (DH-S2B-2)
                abrir_form_instrument(page, name="Livre", symbol="LIVR3", family="EQUITY_LIKE",
                                      asset_class="RENDA_VARIAVEL", currency="BRL", exchange="B3")
                salvar(page)
                page.evaluate("""() => { const bs=[...document.querySelectorAll('button[data-ald-edit=instrument]')];
                    bs[bs.length-1].click(); }""")
                page.locator("#alladinFldSymbol").fill("VALE3")
                salvar(page)
                modal2 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "alteração foi salva" not in modal2.lower():
                    falhas.append(f"WT2: copia de EDICAO ausente — 'foi criado' seria falso ({modal2[:110]!r})")
                if "foi criado" in modal2:
                    falhas.append("WT2: copia de criacao exibida numa edicao")
                if page.evaluate("() => document.querySelectorAll('#alladinModalBox button[data-ald-act=salvar]').length"):
                    falhas.append("WT2: Salvar continua disponivel no estado de decisao")
                # a inativacao age sobre o registro EDITADO
                page.locator("button[data-ald-act=inativar-novo]").click()
                page.wait_for_timeout(200)
                d = disco(page)
                editado = [i for i in d["instruments"] if i["symbol"] == "VALE3" and i["name"] == "Livre"]
                if not editado or editado[0]["recordStatus"] != "INACTIVE":
                    falhas.append(f"WT2: inativacao nao atingiu o registro editado ({[(i['name'],i['recordStatus']) for i in d['instruments']]})")
                # WT3/WT5: DUPLICADO + informativo no MESMO ato -> ambos visiveis
                for nome in ("Euro A", "Euro B"):
                    abrir_form_instrument(page, name=nome, symbol="EEUR", family="FUND_LIKE",
                                          asset_class="FUNDO", currency="EUR")
                    salvar(page)
                modal3 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "DUPLICADO_SYMBOL_EXCHANGE_CURRENCY" not in modal3:
                    falhas.append(f"WT5: duplicidade ausente no estado de decisao ({modal3[:110]!r})")
                if "MOEDA_FORA_DO_SUPORTE_DE_RUNTIME" not in modal3:
                    falhas.append(f"WT3/WT5: aviso informativo SUMIU no estado de decisao ({modal3[:140]!r})")
                outros = page.evaluate("""() => { const el=document.querySelector('[data-ald-outros-avisos]'); return el?el.innerText:''; }""")
                if "MOEDA_FORA_DO_SUPORTE_DE_RUNTIME" not in outros or "não pedem decisão" not in outros:
                    falhas.append(f"WT5: informativo nao separado da razao da decisao ({outros!r})")
                # prova estrutural: 3 avisos entram, 3 codigos permanecem
                preservados = page.evaluate("""() => {
                    const box=document.getElementById('alladinModalBox');
                    alladinForm.avisos=['DUPLICADO_SYMBOL_EXCHANGE_CURRENCY','MOEDA_FORA_DO_SUPORTE_DE_RUNTIME','CODIGO_FUTURO_DESCONHECIDO'];
                    const t=alladinAvisosResumo(alladinForm.avisos);
                    return ['DUPLICADO_SYMBOL_EXCHANGE_CURRENCY','MOEDA_FORA_DO_SUPORTE_DE_RUNTIME','CODIGO_FUTURO_DESCONHECIDO']
                        .filter(c => t.indexOf(c)>=0).length;
                }""")
                if preservados != 3:
                    falhas.append(f"WT3: {3-preservados} codigo(s) perdido(s) na humanizacao (desconhecido deve sair cru)")
                # Guarda de reentrada no estado de DECISAO: um submit programatico
                # (Enter enfileirado, macro, extensao) nao pode reabrir o formulario
                # por cima da decisao pendente nem ressubmeter. Sem a guarda, o
                # submit releria o box sem inputs, cairia na validacao vazia e
                # RE-RENDERIZARIA o formulario — destruindo a decisao.
                antes_disco = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.evaluate("() => { alladinSubmit(); alladinSubmit(); }")
                page.wait_for_timeout(150)
                estado = page.evaluate("""() => ({
                    decisao: document.querySelectorAll('#alladinModalBox button[data-ald-act=manter]').length,
                    salvar: document.querySelectorAll('#alladinModalBox button[data-ald-act=salvar]').length,
                    estado: alladinForm.estado })""")
                if estado["decisao"] != 1 or estado["salvar"] != 0 or estado["estado"] != "COMMITTED_WARNING":
                    falhas.append(f"WT: submit reentrante corrompeu o estado de decisao ({estado})")
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != antes_disco:
                    falhas.append("WT: submit reentrante no estado de decisao escreveu no disco")
                page.locator("button[data-ald-act=manter]").click()
                page.wait_for_timeout(120)
                # Guarda de reentrada na CONFIRMACAO DE STATUS: aqui ela e' a UNICA
                # protecao. Sem ela, um submit programatico leria o formulario
                # inexistente, cairia na validacao vazia e ABRIRIA UM FORMULARIO DE
                # CRIACAO por cima da confirmacao — o operador pediu "Inativar" e
                # receberia "Novo instrumento", com o estado voltando a EDITING.
                criar_conta(page, nome="Conta Guarda")
                page.locator("button[data-ald-status=INACTIVE][data-ald-tipo=account]").first.click()
                antes_disco2 = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.evaluate("() => { alladinSubmit(); alladinSubmit(); }")
                page.wait_for_timeout(150)
                st = page.evaluate("""() => ({
                    confirmacao: document.querySelectorAll('#alladinModalBox button[data-ald-act=status-confirmado]').length,
                    salvar: document.querySelectorAll('#alladinModalBox button[data-ald-act=salvar]').length,
                    campos: document.querySelectorAll('#alladinModalBox input,#alladinModalBox select').length,
                    estado: alladinForm.estado })""")
                if st["confirmacao"] != 1 or st["salvar"] or st["campos"] or st["estado"] != "CONFIRM_STATUS":
                    falhas.append(f"WT: submit reentrante trocou a confirmacao de status por um formulario ({st})")
                if page.evaluate("() => localStorage.getItem('%s')" % LSKEY) != antes_disco2:
                    falhas.append("WT: submit reentrante na confirmacao de status escreveu no disco")
                page.locator("button[data-ald-act=cancelar]").click()
                page.wait_for_timeout(100)
                if erros:
                    falhas.append(f"WT pageerror: {erros}")
            executar(falhas, "WT1..WT5", wt)

            # ---- R1/R2/R8: write gate e varredura economica nos forms ricos --
            def r_infra():
                ctx, page, erros = abrir(browser, url, viewport={"width": 390, "height": 844})
                page.evaluate("""() => {
                    JPWAlladin.cadastro.addInstrument({name:'Petro',symbol:'PETR4',currency:'BRL',
                        instrumentFamily:'EQUITY_LIKE',assetClass:'RENDA_VARIAVEL'});
                    JPWAlladin.cadastro.addAsset({name:'Apto',nature:'IMOVEL',recordMode:'INDIVIDUAL',
                        owners:[{name:'JP',shareBp:5000,isSelf:true}]});
                    JPWAlladinUI.render();
                }""")
                # R8: varredura economica com os DOIS formularios ricos abertos
                for view, tipo in (("instruments", "instrument"), ("assets", "asset")):
                    page.evaluate("(v) => JPWAlladinUI.selectView(v)", view)
                    page.locator(f"button[data-ald-edit={tipo}]").click()
                    texto = page.evaluate("""() => {
                        const cadastrais=['instruments','assets','accounts','cashAccounts'];
                        const ativo=cadastrais
                            .map(v=>document.querySelector('[data-alladin-panel="'+v+'"]'))
                            .find(el=>el && !el.hidden);
                        return (ativo?ativo.innerText:'') + ' ' +
                            document.getElementById('alladinModalBox').innerText;
                    }""")
                    m = PROIBIDO.search(PARTICIPACAO.sub(" ", texto))
                    if m:
                        falhas.append(f"R8: conteudo economico proibido no form de {tipo}: {m.group(0)!r}")
                    largura = page.evaluate("() => document.getElementById('alladinModalBox').scrollWidth <= window.innerWidth + 2")
                    if not largura:
                        falhas.append(f"R6: form de {tipo} estoura o viewport mobile")
                    # R3/R5: trap + retorno de foco por seletor
                    if tipo == "asset":
                        preso = page.evaluate("""() => {
                            const f=[...document.querySelectorAll('#alladinModalBox button:not([disabled]),#alladinModalBox input,#alladinModalBox select')];
                            f[f.length-1].focus();
                            const ev=new KeyboardEvent('keydown',{key:'Tab',bubbles:true,cancelable:true});
                            document.getElementById('alladinModalBox').dispatchEvent(ev);
                            return ev.defaultPrevented;
                        }""")
                        if not preso:
                            falhas.append("R3: focus trap ausente no formulario rico")
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(120)
                foco = page.evaluate("() => document.activeElement && document.activeElement.dataset && document.activeElement.dataset.aldEdit")
                if foco != "asset":
                    falhas.append(f"R5: foco nao retornou ao botao de origem ({foco!r})")
                # R1: READ_ONLY desabilita TODOS os botoes de mutacao dos 4 tipos
                page.evaluate("""() => { S.alladin.schemaVersion=7;
                    localStorage.setItem('%s', JSON.stringify(S)); JPWAlladinUI.render(); }""" % LSKEY)
                for view in ("instruments", "assets"):
                    page.evaluate("(v) => JPWAlladinUI.selectView(v)", view)
                    hab = page.evaluate("""() => [...document.querySelectorAll('#alladin button[data-ald-new],#alladin button[data-ald-edit],#alladin button[data-ald-status]')]
                        .filter(b => !b.disabled).length""")
                    if hab:
                        falhas.append(f"R1: {hab} botoes habilitados em READ_ONLY ({view})")
                # R2: write gate tardio no submit do form rico
                page.evaluate("""() => { S.alladin.schemaVersion=6; JPWAlladinUI.render();
                    document.getElementById('sessionNotice').textContent=''; }""")
                page.evaluate("() => JPWAlladinUI.selectView('assets')")
                page.locator("button[data-ald-new=asset]").click()
                page.locator("#alladinFldName").fill("Tardio")
                page.locator("#alladinFldNature").fill("BEM_DURAVEL")
                page.locator("#alladinFldRecordMode").select_option("INDIVIDUAL")
                page.evaluate("() => { S.alladin.schemaVersion=7; }")
                salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "READ_ONLY_FUTURE_SCHEMA" not in modal or "Nada foi gravado" not in modal:
                    falhas.append(f"R2: bloqueio tardio sem mensagem honesta ({modal[:90]!r})")
                if "Cadastro salvo" in page.evaluate("() => document.getElementById('sessionNotice').innerText"):
                    falhas.append("R2: falso sucesso com write gate fechado")
                page.evaluate("() => { S.alladin.schemaVersion=6; }")
                if any(a["name"] == "Tardio" for a in colecao(page, "assets")):
                    falhas.append("R2: registro bloqueado chegou ao disco")
                if erros:
                    falhas.append(f"R-infra pageerror: {erros}")
            executar(falhas, "R1/R2/R8", r_infra)

            # ---- R7: teclado nos formularios ricos --------------------------
            def r7_teclado():
                # Pagina propria: o bloco R1/R2 escreve direto no localStorage, e a
                # guarda de concorrencia do save() passa a recusar — recusa legitima
                # do sistema que nada tem a ver com o caminho de teclado.
                ctx, page, erros = abrir(browser, url)
                page.evaluate("() => JPWAlladinUI.selectView('instruments')")
                page.locator("button[data-ald-new=instrument]").click()
                page.locator("#alladinFldName").fill("Por Teclado")
                page.locator("#alladinFldSymbol").fill("TECL3")
                page.locator("#alladinFldFamily").select_option("EQUITY_LIKE")
                page.locator("#alladinFldAssetClass").fill("RENDA_VARIAVEL")
                page.locator("#alladinFldCurrency").fill("BRL")
                page.locator("#alladinFldName").press("Enter")
                page.wait_for_timeout(200)
                criados = [i for i in colecao(page, "instruments") if i["name"] == "Por Teclado"]
                if len(criados) != 1:
                    falhas.append(f"R7: Enter no formulario rico nao criou exatamente um registro ({len(criados)})")
                if page.evaluate("() => document.getElementById('alladinModalOverlay').classList.contains('show')"):
                    falhas.append("R7: modal permaneceu aberto apos submissao por teclado")
                if erros:
                    falhas.append(f"R7 pageerror: {erros}")
            executar(falhas, "R7", r7_teclado)

            # ============ C3-S2-C — CORREÇÕES DE PRESERVAÇÃO ================
            # C1/C2/C3 + P1/P2/P3: `network` sobrevive por padrão e sai só por gesto.
            def c1_c3():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("""() => { JPWAlladin.cadastro.addInstrument({name:'Tether', symbol:'USDT',
                    currency:'USD', instrumentFamily:'CRYPTO', assetClass:'CRIPTO',
                    externalIdentifiers:{network:'ethereum', isin:'AAA111'}}); JPWAlladinUI.render(); }""")
                espiao = """() => { window.__p=[];
                    if(!window.__origEditInstrument) window.__origEditInstrument=JPWAlladin.cadastro.editInstrument;
                    JPWAlladin.cadastro.editInstrument=(i,p)=>{ window.__p.push(JSON.parse(JSON.stringify(p)));
                        return window.__origEditInstrument(i,p); }; }"""
                # C1/P1: troca de familia NAO toca a rede -> externalIdentifiers AUSENTE do patch
                page.evaluate("() => JPWAlladinUI.selectView('instruments')")
                page.locator("button[data-ald-edit=instrument]").click()
                page.evaluate(espiao)
                page.locator("#alladinFldFamily").select_option("EQUITY_LIKE")
                if page.evaluate("() => document.getElementById('alladinFldNetworkWrap').hidden"):
                    falhas.append("C1: o campo Rede sumiu ao sair de CRYPTO, escondendo o dado do operador")
                page.locator("#alladinFldAssetClass").fill("RENDA_VARIAVEL")
                salvar(page)
                patch = page.evaluate("() => window.__p")
                if len(patch) != 1 or "externalIdentifiers" in patch[0]:
                    falhas.append(f"P1: externalIdentifiers viajou no patch sem ter mudado ({patch})")
                ext = page.evaluate("() => JPWAlladin.leitura.instruments()[0].externalIdentifiers")
                if ext != {"network": "ethereum", "isin": "AAA111"}:
                    falhas.append(f"C1/B-1: a rede foi perdida na troca de familia ({ext})")
                d = colecao(page, "instruments")[0]["externalIdentifiers"]
                if d.get("network") != "ethereum":
                    falhas.append(f"C1: a rede nao sobreviveu no DISCO ({d})")
                # P2: alterar a rede -> externalIdentifiers PRESENTE, demais preservados
                page.locator("button[data-ald-edit=instrument]").click()
                page.evaluate(espiao)
                page.locator("#alladinFldNetwork").fill("polygon")
                salvar(page)
                patch2 = page.evaluate("() => window.__p")
                if len(patch2) != 1 or patch2[0].get("externalIdentifiers", {}) != {"network": "polygon", "isin": "AAA111"}:
                    falhas.append(f"P2: patch da rede alterada divergente ({patch2})")
                # C2/P3: limpar o campo em instrumento NAO-cripto remove de fato
                page.locator("button[data-ald-edit=instrument]").click()
                page.evaluate(espiao)
                page.locator("#alladinFldNetwork").fill("")
                salvar(page)
                patch3 = page.evaluate("() => window.__p")
                if len(patch3) != 1 or "network" in patch3[0].get("externalIdentifiers", {}):
                    falhas.append(f"P3: remocao explicita nao chegou ao patch ({patch3})")
                if colecao(page, "instruments")[0]["externalIdentifiers"] != {"isin": "AAA111"}:
                    falhas.append("P3: a remocao explicita nao persistiu")
                # C3: em CRYPTO a rede continua obrigatoria; esvaziar recusa, nada some
                page.locator("button[data-ald-edit=instrument]").click()
                page.locator("#alladinFldFamily").select_option("CRYPTO")
                page.locator("#alladinFldAssetClass").fill("CRIPTO")
                salvar(page)
                modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "rede (network)" not in modal.lower():
                    falhas.append(f"C3: CRYPTO sem rede deveria recusar ({modal[:80]!r})")
                # a chave `network` nunca vira linha generica
                page.locator("button[data-ald-act=ext-add]").click()
                page.locator("[data-ald-ext-k]").last.fill("network")
                page.locator("[data-ald-ext-v]").last.fill("solana")
                page.locator("#alladinFldNetwork").fill("solana")
                salvar(page)
                modal2 = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                if "campo Rede" not in modal2:
                    falhas.append(f"C3: linha generica 'network' deveria ser recusada ({modal2[:90]!r})")
                page.evaluate("() => { alladinForm.estado='EDITING'; alladinModalDismiss(); }")
                if erros:
                    falhas.append(f"C1/C3 pageerror: {erros}")
            executar(falhas, "C1/C2/C3 + P1/P2/P3", c1_c3)

            # C4/C5/C6 + P4/P5/P6: vocabulario fechado desconhecido e' preservado.
            def c4_c6():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("""() => {
                    JPWAlladin.cadastro.addInstrument({name:'Estranho', symbol:'EST3', currency:'BRL',
                        instrumentFamily:'EQUITY_LIKE', assetClass:'y'});
                    S.alladin.instruments[0].instrumentFamily='FAMILIA_FUTURA';
                    JPWAlladin.cadastro.addAsset({name:'Bem', nature:'IMOVEL', recordMode:'INDIVIDUAL'});
                    S.alladin.assets[0].recordMode='MODO_FUTURO';
                    save(); JPWAlladinUI.render(); }""")
                for view, tipo, campo, cru, valido in (
                        ("instruments", "instrument", "alladinFldFamily", "FAMILIA_FUTURA", "COMMODITY"),
                        ("assets", "asset", "alladinFldRecordMode", "MODO_FUTURO", "GROUPED")):
                    page.evaluate("(v) => JPWAlladinUI.selectView(v)", view)
                    page.locator(f"button[data-ald-edit={tipo}]").click()
                    # P4: abre selecionado no valor CRU, rotulado com honestidade
                    estado = page.evaluate("""(c) => { const el=document.getElementById(c);
                        const sel=el.options[el.selectedIndex];
                        return { valor:el.value, rotulo:sel?sel.textContent:'' }; }""", campo)
                    if estado["valor"] != cru:
                        falhas.append(f"P4: {campo} nao abriu no valor cru ({estado})")
                    if "não reconhecido" not in estado["rotulo"]:
                        falhas.append(f"P4: rotulo do valor desconhecido nao e honesto ({estado['rotulo']!r})")
                    if "corromp" in estado["rotulo"].lower():
                        falhas.append("P4: o rotulo afirma corrupcao do dado")
                    # P5: editar OUTRO campo nao normaliza; dominio recusa honestamente
                    espiao = ("() => { window.__p=[]; document.getElementById('sessionNotice').textContent='';"
                              " if(!window.__orig%s) window.__orig%s=JPWAlladin.cadastro.edit%s;"
                              " JPWAlladin.cadastro.edit%s=(i,p)=>{ window.__p.push(JSON.parse(JSON.stringify(p)));"
                              " return window.__orig%s(i,p); }; }")
                    alvo = "Instrument" if tipo == "instrument" else "Asset"
                    page.evaluate(espiao % (alvo, alvo, alvo, alvo, alvo))
                    page.locator("#alladinFldName").fill("Renomeado")
                    salvar(page)
                    patch = page.evaluate("() => window.__p")
                    chave = "instrumentFamily" if tipo == "instrument" else "recordMode"
                    if len(patch) != 1 or chave in patch[0]:
                        falhas.append(f"P5: {chave} entrou no patch sem o operador ter tocado ({patch})")
                    lido = page.evaluate("(t) => (t==='instrument'?JPWAlladin.leitura.instruments():JPWAlladin.leitura.assets())[0]", tipo)
                    if lido[chave] != cru:
                        falhas.append(f"P5/B-2: o valor desconhecido foi NORMALIZADO em silencio ({lido[chave]})")
                    modal = page.evaluate("() => document.getElementById('alladinModalBox').innerText")
                    if "não reconhece" not in modal or "selecione um valor" not in modal.lower():
                        falhas.append(f"P5: recusa sem texto humano de vocabulario ({modal[:120]!r})")
                    if "corromp" in modal.lower():
                        falhas.append("P5: a mensagem afirma corrupcao do dado")
                    if page.evaluate("(c) => document.getElementById(c).value", campo) != cru:
                        falhas.append("P5: o valor cru sumiu do formulario apos a recusa")
                    if page.evaluate("() => document.getElementById('alladinFldName').value") != "Renomeado":
                        falhas.append("P5: o rascunho foi perdido na recusa do formulario rico")
                    if "Cadastro salvo" in page.evaluate("() => document.getElementById('sessionNotice').innerText"):
                        falhas.append("P8: recusa de vocabulario disparou notice de sucesso")
                    # P6: escolher valor conhecido destrava e persiste
                    page.locator(f"#{campo}").select_option(valido)
                    page.evaluate(espiao % (alvo, alvo, alvo, alvo, alvo))
                    salvar(page)
                    patch2 = page.evaluate("() => window.__p")
                    if len(patch2) != 1 or patch2[0].get(chave) != valido:
                        falhas.append(f"P6: o valor escolhido nao entrou no patch ({patch2})")
                    lido2 = page.evaluate("(t) => (t==='instrument'?JPWAlladin.leitura.instruments():JPWAlladin.leitura.assets())[0]", tipo)
                    if lido2[chave] != valido:
                        falhas.append(f"P6: escolha deliberada nao persistiu ({lido2[chave]})")
                if erros:
                    falhas.append(f"C4/C6 pageerror: {erros}")
            executar(falhas, "C4/C5/C6 + P4/P5/P6", c4_c6)

            # C7 + P7/P8: Account e CashAccount preservam o rascunho em TODA recusa.
            def c7():
                ctx, page, erros = abrir(browser, url)
                # classes de erro por entidade. CashAccount CREATE nao tem validacao
                # local possivel (moeda vazia e' o unico campo livre) -> coberto em EDIT.
                casos = []
                # (1) Account CREATE — validacao local
                page.evaluate("() => JPWAlladinUI.selectView('accounts')")
                page.locator("button[data-ald-new=account]").click()
                page.locator("#alladinFldName").fill("Conta Digitada")
                page.locator("#alladinFldInstitution").fill("Instituicao Digitada")
                salvar(page)   # accountType vazio
                casos.append(("Account create/validacao local", page.evaluate("""() => ({
                    aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                    nome: (document.getElementById('alladinFldName')||{}).value,
                    inst: (document.getElementById('alladinFldInstitution')||{}).value,
                    erro: !!document.querySelector('#alladinModalBox .session-error'),
                    notice: document.getElementById('sessionNotice').innerText })""")))
                # (2) Account CREATE — persistencia recusada
                page.locator("#alladinFldAccountType").fill("BANK")
                page.evaluate("() => { window.__so=window.save; window.save=()=>false; }")
                salvar(page)
                casos.append(("Account create/persistencia recusada", page.evaluate("""() => ({
                    aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                    nome: (document.getElementById('alladinFldName')||{}).value,
                    inst: (document.getElementById('alladinFldInstitution')||{}).value,
                    erro: !!document.querySelector('#alladinModalBox .session-error'),
                    notice: document.getElementById('sessionNotice').innerText })""")))
                # (3) Account CREATE — write gate tardio
                page.evaluate("() => { window.save=window.__so; S.alladin.schemaVersion=7; }")
                salvar(page)
                casos.append(("Account create/write gate tardio", page.evaluate("""() => ({
                    aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                    nome: (document.getElementById('alladinFldName')||{}).value,
                    inst: (document.getElementById('alladinFldInstitution')||{}).value,
                    erro: !!document.querySelector('#alladinModalBox .session-error'),
                    notice: document.getElementById('sessionNotice').innerText })""")))
                page.evaluate("() => { S.alladin.schemaVersion=6; alladinForm.estado='EDITING'; alladinModalDismiss(); }")
                # (4) CashAccount EDIT — recusa do dominio (conta-mae inativa)
                page.evaluate("""() => {
                    const a=JPWAlladin.cadastro.addAccount({name:'Banco A',institution:'A',accountType:'BANK'});
                    const c=JPWAlladin.cadastro.addCashAccount({accountId:a.recordId,currency:'BRL'});
                    JPWAlladinUI.render(); window.__contaA=a.recordId; }""")
                page.evaluate("() => JPWAlladinUI.selectView('cashAccounts')")
                page.locator("button[data-ald-edit=cashaccount]").click()
                page.locator("#alladinFldCurrency").fill("USD")
                # a conta-mae e inativada ENTRE a abertura e o submit
                page.evaluate("""() => { JPWAlladin.cadastro.setRecordStatus('cashaccount',
                        JPWAlladin.leitura.cashAccounts()[0].cashAccountId,'INACTIVE');
                    JPWAlladin.cadastro.setRecordStatus('account', window.__contaA,'INACTIVE');
                    document.getElementById('sessionNotice').textContent=''; }""")
                salvar(page)
                casos.append(("CashAccount edit/recusa do dominio", page.evaluate("""() => ({
                    aberto: document.getElementById('alladinModalOverlay').classList.contains('show'),
                    nome: (document.getElementById('alladinFldCurrency')||{}).value,
                    inst: 'N/A',
                    erro: !!document.querySelector('#alladinModalBox .session-error'),
                    notice: document.getElementById('sessionNotice').innerText })""")))
                for nome, r in casos:
                    if not r["aberto"]:
                        falhas.append(f"C7 [{nome}]: o modal fechou na recusa")
                    if not r["erro"]:
                        falhas.append(f"C7 [{nome}]: nenhum erro visivel")
                    if "Cadastro salvo" in r["notice"]:
                        falhas.append(f"P8 [{nome}]: recusa disparou notice de sucesso")
                    if not r["nome"]:
                        falhas.append(f"P7 [{nome}]: o rascunho foi apagado ({r})")
                if casos[0][1]["nome"] != "Conta Digitada" or casos[0][1]["inst"] != "Instituicao Digitada":
                    falhas.append(f"P7: valores digitados nao sobreviveram identicos ({casos[0][1]})")
                if casos[3][1]["nome"] != "USD":
                    falhas.append(f"P7: a moeda digitada na cash nao sobreviveu ({casos[3][1]})")
                if erros:
                    falhas.append(f"C7 pageerror: {erros}")
            executar(falhas, "C7 + P7/P8", c7)

            # C8 + P9: rotulos de lifecycle sao exatamente o catalogo do dominio.
            def c8():
                ctx, page, erros = abrir(browser, url)
                r = page.evaluate("""() => ({
                    catalogo: JPWAlladin.catalogos().fechados.lifecycleStatus.slice().sort(),
                    mapa: Object.keys(ALLADIN_LIFECYCLE_LABEL).sort(),
                    status_catalogo: JPWAlladin.catalogos().fechados.recordStatus.slice().sort(),
                    status_mapa: Object.keys(ALLADIN_STATUS_LABEL).sort() })""")
                if r["catalogo"] != r["mapa"]:
                    falhas.append(f"P9/F-1: mapa de lifecycle diverge do catalogo do dominio "
                                  f"(so no mapa: {sorted(set(r['mapa'])-set(r['catalogo']))}; "
                                  f"so no catalogo: {sorted(set(r['catalogo'])-set(r['mapa']))})")
                if r["status_catalogo"] != r["status_mapa"]:
                    falhas.append(f"P9: mapa de recordStatus diverge do catalogo ({r})")
                # valor fora do catalogo continua exibido CRU
                page.evaluate("""() => { JPWAlladin.cadastro.addAsset({name:'Futuro', nature:'IMOVEL',
                        recordMode:'INDIVIDUAL'});
                    S.alladin.assets[0].lifecycleStatus='ESTADO_FUTURO'; save(); JPWAlladinUI.render(); }""")
                page.evaluate("() => JPWAlladinUI.selectView('assets')")
                txt = page.evaluate("() => document.getElementById('alladinAssets').innerText")
                if "ESTADO_FUTURO" not in txt:
                    falhas.append(f"C8: valor fora do catalogo deveria aparecer cru ({txt[:100]!r})")
                if erros:
                    falhas.append(f"C8 pageerror: {erros}")
            executar(falhas, "C8 + P9", c8)

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
    print("ALLADIN UI CRUD TEST PASS (S2-C C1-C8/P1-P9: a rede sobrevive a troca de familia e sai so por gesto explicito, sem viajar no patch quando nao mudou; vocabulario fechado desconhecido abre no valor cru com rotulo honesto, nunca e normalizado em silencio, e a recusa do dominio vem com rota de correcao; Account e CashAccount preservam o rascunho em validacao local, recusa do dominio, write gate tardio e persistencia recusada, sem notice de sucesso; rotulos de lifecycle iguais ao catalogo do dominio e valor fora dele exibido cru) + ")
    print("(S2-B I1-I12/A1-A15/WT1-WT5/R1-R8: Instrument e Asset criados e "
          "editados pelo modal real; moeda imutavel fora do patch; symbolHistory mantido SO pelo dominio "
          "e historico ilegivel recusado com honestidade; CRYPTO exige rede com fonte unica; "
          "identificadores externos com linha vazia omitida e meio-preenchida recusada; owners em basis "
          "points por aritmetica inteira (66,67+33,33=100%), soma>100 recusada, parcial e nome duplicado "
          "como aviso pos-sucesso; tags e data round-trip; lifecycleStatus jamais editavel; patch-diff "
          "envia so o alterado; taxonomia de avisos com duplicidade em decisao, informativos preservados "
          "e codigo desconhecido exibido cru; copia distinta para criacao e edicao) + ")
    print("(W1-W15 / S2A-1..12: Account e CashAccount criados e editados pelo "
          "modal real com persistencia provada em memoria e disco; DC-4 pos-criacao com registro ja "
          "persistido, decisao explicita obrigatoria, Escape/backdrop suspensos e inativacao via "
          "setRecordStatus; referencia inativa exibida honesta sem troca silenciosa; recusas "
          "referenciais sem status falso; status x4 pela linha com confirmacao; cancelamentos "
          "zero-write; write gate na abertura e no submit sem falso sucesso; double submit nao "
          "duplica; zero conteudo economico; focus trap, retorno de foco e mobile)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
