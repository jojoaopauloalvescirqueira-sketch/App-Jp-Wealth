#!/usr/bin/env python3
"""Finalizar Sessao preserva S.alladin INTEGRALMENTE (ALD-C3-PRE).

Contrato semantico congelado no gate de 2026-08-21:

    ENCERRAMENTO OPERACIONAL          LIMPEZA TOTAL
    finalizeJPWealthSession()         wipeAllData()
    sessionHandleRemoteFinalization() sessionHandleRemoteBaseWipe()
    -> S.alladin PRESERVADO           -> S.alladin APAGADO
       inclusive future-schema           inclusive future-schema

O contraste E o contrato: uma implementacao que preservasse o Alladin nos DOIS
atos passaria em C1-C3 e estaria errada. Por isso C4 exercita a Zona de Perigo
no mesmo arquivo.

Casos:
  C1/C2/C5  deep equality em memoria e disco; sessao de fato encerrada
  C3        future-schema sem normalize/migrate/downgrade, ATRAVESSANDO reload,
            com recusa REAL de escrita depois do ciclo
  C4        wipeAllData continua apagando (v2 e v3)
  C6        nenhuma chave nova E nenhuma contaminacao de chave auxiliar
  C7        dois ciclos consecutivos com reload real
  C8        falha de copia = falha do ato inteiro: nada apagado, nada avisado
            as outras abas, persistencia intacta, modal explicito, sem pageerror
  C9        fluxo CROSS-TAB preserva (o handler remoto tem cobertura propria)
  C10       fluxo cross-tab preserva o estado PERSISTIDO, nao a memoria obsoleta
            da aba receptora — finalizar jamais ressuscita registro apagado
  C11       cross-tab com estado persistido ilegivel ABORTA e deixa a aba
            bloqueada, em vez de cair na memoria velha
  C14       cross-tab com a chave principal AUSENTE (janela entre o sinal e a
            regravacao da aba de origem) tambem aborta: chave ausente e disco
            indeterminado, nao estado legado
  C12       a copia e profunda: mutar o estado antigo nao alcanca o preservado
  C13       estado legado sem o agregado nao quebra o fluxo

Fixture: tools/fixtures/alladin_v2.json (100% sintetica).
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
SINAL = "jpwealth_session_wipe_signal_v1"
FIXTURE = json.loads((ROOT / "tools/fixtures/alladin_v2.json").read_text(encoding="utf-8"))["alladin"]

# O mesmo agregado DEPOIS de o operador agir NOUTRA aba: status alterado, campo
# textual alterado e PII de terceiro alterada. E o retrato AUTORITATIVO — o que
# esta no disco. A aba que finaliza pode ter uma memoria anterior a isso, e o
# encerramento jamais pode desfazer esses tres atos.
def _mais_recente(base):
    import copy
    d = copy.deepcopy(base)
    d["instruments"][0]["name"] = "NOME CORRIGIDO PELO OPERADOR"
    d["instruments"][1]["recordStatus"] = "ACTIVE"
    d["assets"][0]["location"] = "ENDERECO CORRIGIDO PELO OPERADOR"
    d["assets"][0]["recordStatus"] = "INACTIVE"
    d["assets"][0]["owners"] = [{"name": "Operador Sintetico", "shareBp": 10000, "isSelf": True}]
    return d


MAIS_RECENTE = _mais_recente(FIXTURE)

# O mesmo agregado DEPOIS de o operador apagar registros. Como o Alladin nao tem
# ato de delecao (setRecordStatus so alterna ACTIVE/INACTIVE), editar o agregado e
# hoje o unico modo de eliminar um registro — e e justamente esse ato que uma aba
# obsoleta desfaria se a preservacao viesse da memoria em vez do disco.
REDUZIDO = {**FIXTURE, "assets": [], "accounts": [], "cashAccounts": []}

# Agregado de versao FUTURA: o fail-closed o protege byte-intacto contra atos do
# dominio; C3 exige que Finalizar Sessao tambem o preserve, e C4 que a Zona de
# Perigo o apague assim mesmo.
FUTURO = {
    "schemaVersion": 3,
    "reportingCurrency": "BRL",
    "instruments": [{"instrumentId": "aldi_v3", "campoDoFuturo": {"x": [1, 2]}}],
    "assets": [], "accounts": [], "cashAccounts": [],
    "colecaoQueNaoExisteNoV2": [{"id": 1}],
}


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


PRONTO = "() => typeof S === 'object' && typeof save === 'function' && window.JPWAlladin"

PREPARO = """() => {
    window.alert = () => {};
    closeModal();
    window.URL.createObjectURL = () => 'blob:jpwealth-test';
    window.URL.revokeObjectURL = () => {};
    HTMLAnchorElement.prototype.click = function(){ window.__jpwealthDownload={filename:this.download}; };
}"""

CONTEXTOS = []


def abrir(browser, url):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    CONTEXTOS.append(context)
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
    page.wait_for_function(PRONTO)
    page.wait_for_timeout(400)
    page.evaluate(PREPARO)
    return context, page, erros


def finalizar_fluxo_real(page, falhas, rotulo):
    """Percorre o fluxo REAL, pelos DOIS caminhos de entrada.

    O fluxo bifurca conforme o checkpoint: com alteracoes posteriores ao ultimo
    backup entra pela tela de export ('changed'); sem alteracoes entra pela
    escolha 'Voce possui uma copia?' ('safe'). Registrar QUAL tela apareceu e
    parte do contrato: se o checkpoint quebrar e os dois ramos virarem um so, a
    suite precisa reclamar em vez de seguir verde com metade da cobertura.
    """
    page.locator("#finalizeSessionBtn").click()
    page.wait_for_timeout(500)
    if page.locator("#sessionExport").count():
        entrada = "changed"
        page.locator("#sessionExport").click()
        page.locator("#sessionExportAcknowledged").check()
        page.locator("#sessionExportContinue").click()
        page.wait_for_timeout(200)
    elif page.locator("#sessionHasCopy").count():
        entrada = "safe"
        page.locator("#sessionHasCopy").click()
        page.wait_for_timeout(200)
    else:
        entrada = "NENHUMA"
        falhas.append(f"{rotulo}: nenhuma das telas de entrada do fluxo apareceu "
                      "(#sessionExport e #sessionHasCopy ausentes)")
    if not page.locator("#sessionProceed").count():
        falhas.append(f"{rotulo}: a tela de confirmacao (#sessionProceed) nao apareceu (entrada={entrada})")
        return entrada
    page.locator("#sessionProceed").click()
    page.locator("#sessionDeletePhrase").fill("ENCERRAR SESSÃO")
    page.locator("#sessionDeleteConfirm").click()
    page.wait_for_timeout(700)
    return entrada


def do_disco(page):
    return page.evaluate(
        f"""() => {{
            const raw = localStorage.getItem({json.dumps(LSKEY)});
            if(!raw) return null;
            try {{ const a = JSON.parse(raw).alladin; return a===undefined ? 'AUSENTE' : JSON.stringify(a); }}
            catch(e) {{ return 'CORROMPIDO'; }}
        }}""")


def igual(bruto, esperado):
    """Compara o agregado lido do produto com o esperado, por VALOR."""
    if bruto in (None, "AUSENTE", "CORROMPIDO"):
        return False
    try:
        return json.loads(bruto) == esperado
    except Exception:
        return False


# O emissor v2 so difunde DEPOIS de o documento final estar duravel no disco
# (write-before-clear + broadcast pos-commit). Semear o disco com o documento
# FINALIZADO reproduz exatamente o que o receptor encontra no produto real.
SEMEAR_DOC_FINALIZADO = """(a) => {
    const fin = emptyJPWealthState(a===null ? {} : {alladin:a});
    localStorage.setItem('jpwealth_v9_state', JSON.stringify(fin));
}"""

REMOTO = """(payload) => {
    // Protocolo v2 com a geracao CORRENTE: estes casos provam PRESERVACAO.
    // A causalidade entre geracoes tem suite propria (session_epoch_protocol_test.py).
    sessionHandleRemoteFinalization({type:'jpwealth-session-finalized-v2', token: payload,
                                     baseEpoch: sessionEpochCurrent()});
    return {
        memoria: JSON.stringify(S.alladin),
        contas: S.accounts.length,
        ledger: S.ledger.length,
        bloqueada: jpWealthPersistenceIsBlocked(),
    };
}"""


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def main() -> int:
    servidor, url = serve()
    falhas: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            # ---- C1 + C2 + C5: agregado povoado sobrevive; sessao encerra ----
            def c1_c2_c5():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FIXTURE):
                    falhas.append("C1/C2 pre-condicao: fixture nao sobreviveu ao save()")
                entrada = finalizar_fluxo_real(page, falhas, "C1/C2/C5")
                if entrada != "changed":
                    falhas.append(f"C1/C2/C5: esperado o caminho 'changed' (ha alteracoes pendentes), veio '{entrada}'")
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FIXTURE):
                    falhas.append("C1 MEMORIA: S.alladin difere da fixture apos Finalizar Sessao")
                disco = do_disco(page)
                if not igual(disco, FIXTURE):
                    falhas.append(f"C2 DISCO: agregado nao sobreviveu integralmente ({str(disco)[:60]})")
                resto = page.evaluate("""() => ({
                    contas: S.accounts.length, ledger: S.ledger.length,
                    ordens: S.phases[0].orders.filter(o => o.id).length,
                    onboarding: S.onboarding.done, saldo: S.params.saldoIni,
                    historico: S.operationHistory.records.length, mei: S.mei.history.length })""")
                if not (resto["contas"] == 0 and resto["ledger"] == 0 and resto["ordens"] == 0
                        and resto["onboarding"] is False and resto["saldo"] == 0
                        and resto["historico"] == 0 and resto["mei"] == 0):
                    falhas.append(f"C5: a preservacao transformou a finalizacao em no-op: {resto}")
                if erros:
                    falhas.append(f"C1/C2/C5 pageerror: {erros}")
            executar(falhas, "C1/C2/C5", c1_c2_c5)

            # ---- C3: future-schema sobrevive ao ciclo E ao reload ----
            def c3():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; localStorage.setItem('%s', JSON.stringify(S)); }" % LSKEY, FUTURO)
                finalizar_fluxo_real(page, falhas, "C3")
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FUTURO):
                    falhas.append("C3 MEMORIA: agregado v3 foi alterado")
                if not igual(do_disco(page), FUTURO):
                    falhas.append(f"C3 DISCO: agregado v3 nao sobreviveu intacto ({str(do_disco(page))[:80]})")
                # O reload e a passagem onde alladinNormalizeState teria de segurar:
                # sem ele, C3 nao prova que o fail-closed atravessa a persistencia.
                page.reload(wait_until="load")
                page.wait_for_function(PRONTO)
                page.wait_for_timeout(400)
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FUTURO):
                    falhas.append("C3 RELOAD: agregado v3 foi normalizado/rebaixado ao voltar do disco")
                compat = page.evaluate("() => JPWAlladin.compat()")
                if not (compat["readOnly"] is True and compat["storedSchemaVersion"] == 3):
                    falhas.append(f"C3: fail-closed nao continua valendo apos o ciclo: {compat}")
                # Recusa REAL de escrita — nao a aritmetica de readOnly, que a
                # igualdade acima ja implica.
                escrita = page.evaluate("""() => {
                    const r = JPWAlladin.cadastro.addInstrument({
                        instrumentFamily:'EQUITY', symbol:'XPTO3', name:'Teste', currency:'BRL' });
                    return { ok: r && r.ok, motivo: (r && r.erro) || JPWAlladin.writeBlockReason(),
                             instrumentos: S.alladin.instruments.length };
                }""")
                if escrita["ok"] is not False or escrita["instrumentos"] != len(FUTURO["instruments"]):
                    falhas.append(f"C3: agregado em schema futuro ACEITOU escrita apos o ciclo: {escrita}")
                if erros:
                    falhas.append(f"C3 pageerror: {erros}")
            executar(falhas, "C3", c3)

            # ---- C4: Zona de Perigo CONTINUA apagando (o contraste e o contrato) ----
            def c4():
                for rotulo, agregado in (("v2", FIXTURE), ("v3 (future-schema)", FUTURO)):
                    ctx, page, erros = abrir(browser, url)
                    page.evaluate("(a) => { S.alladin = a; save(); }", agregado)
                    apagou = page.evaluate("""async () => {
                        window.prompt = () => 'APAGAR';
                        window.confirm = () => true;
                        await wipeAllData();   // DP-2: a destruicao inteira roda no lock
                        return JSON.stringify(S.alladin);
                    }""")
                    vazio = {"schemaVersion": 2, "reportingCurrency": "BRL",
                             "instruments": [], "assets": [], "accounts": [], "cashAccounts": []}
                    if igual(apagou, agregado):
                        falhas.append(f"C4 [{rotulo}]: Zona de Perigo PRESERVOU o Alladin — over-preservation")
                    elif not igual(apagou, vazio):
                        falhas.append(f"C4 [{rotulo}]: apos wipeAllData o agregado nao voltou ao DEFAULTS: {apagou[:80]}")
                    if page.evaluate(f"() => localStorage.getItem({json.dumps(LSKEY)})") is not None:
                        falhas.append(f"C4 [{rotulo}]: a chave principal sobreviveu a limpeza total")
                    if erros:
                        falhas.append(f"C4 [{rotulo}] pageerror: {erros}")
            executar(falhas, "C4", c4)

            # ---- C6: nenhuma chave nova E nenhuma contaminacao de auxiliar ----
            def c6():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                # Semeia as auxiliares REAIS: sem elas o ciclo de remocao nunca e
                # exercido e C6 compara um conjunto de um elemento com outro igual.
                page.evaluate("""() => {
                    localStorage.setItem('jpw_rail','aberto');
                    localStorage.setItem('jpw_fs','1.0');
                    localStorage.setItem('jpwealth_v9_icon_choice','classic');
                }""")
                antes = set(page.evaluate("() => Object.keys(localStorage)"))
                finalizar_fluxo_real(page, falhas, "C6")
                depois = page.evaluate("() => Object.keys(localStorage)")
                novas = set(depois) - antes
                # C6 REVISADO (ALD-C3-PRE-EPOCH): nenhuma chave nova, EXCETO a chave
                # tecnica anti-replay de geracao da base — control plane, sem PII e sem
                # conteudo patrimonial. A excecao e nominal: qualquer outra chave falha.
                novas -= {"jpwealth_base_epoch_v1"}
                if novas:
                    falhas.append(f"C6: chave(s) nova(s) de localStorage apos o ciclo: {sorted(novas)}")
                epoch = page.evaluate("() => localStorage.getItem('jpwealth_base_epoch_v1')")
                if epoch is not None and ("aldi_" in epoch or "alda_" in epoch or "Sintetico" in epoch):
                    falhas.append(f"C6: a chave de geracao carrega conteudo patrimonial/PII: {epoch[:60]!r}")
                sobreviventes = [k for k in ("jpw_rail", "jpw_fs", "jpwealth_v9_icon_choice") if k in depois]
                if sobreviventes:
                    falhas.append(f"C6: chave auxiliar nao foi removida pelo ciclo: {sobreviventes}")
                # Contaminacao: nenhuma chave alem da principal pode conter o agregado.
                vazamento = page.evaluate("""() => Object.keys(localStorage)
                    .filter(k => k !== '%s')
                    .filter(k => (localStorage.getItem(k)||'').includes('aldi_'))""" % LSKEY)
                if vazamento:
                    falhas.append(f"C6: dado patrimonial vazou para chave auxiliar: {vazamento}")
                if erros:
                    falhas.append(f"C6 pageerror: {erros}")
            executar(falhas, "C6", c6)

            # ---- C7: dois ciclos consecutivos, com reload real entre eles ----
            def c7():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                e1 = finalizar_fluxo_real(page, falhas, "C7 ciclo 1")
                page.reload(wait_until="load")
                page.wait_for_function(PRONTO)
                page.wait_for_timeout(400)
                page.evaluate(PREPARO)
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FIXTURE):
                    falhas.append("C7: agregado nao sobreviveu ao RELOAD apos o 1o ciclo")
                # O segundo ciclo entra DELIBERADAMENTE pelo outro ramo: com o
                # checkpoint recem-marcado nao ha alteracoes pendentes, entao o
                # fluxo oferece 'Voce possui uma copia?'. Forcar e melhor que
                # torcer — deixar ao acaso do FX tornaria a cobertura do segundo
                # ramo intermitente e a suite, flaky.
                page.evaluate(PREPARO)
                page.evaluate("() => markSessionCheckpoint()")
                e2 = finalizar_fluxo_real(page, falhas, "C7 ciclo 2")
                page.reload(wait_until="load")
                page.wait_for_function(PRONTO)
                page.wait_for_timeout(400)
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FIXTURE):
                    falhas.append("C7: agregado nao sobreviveu ao SEGUNDO ciclo de Finalizar Sessao")
                if e1 != "changed" or e2 != "safe":
                    falhas.append(f"C7: os dois ramos de entrada do fluxo nao foram exercidos "
                                  f"(ciclo 1='{e1}', esperado 'changed'; ciclo 2='{e2}', esperado 'safe')")
                if erros:
                    falhas.append(f"C7 pageerror: {erros}")
            executar(falhas, "C7", c7)

            # ---- C8: leitura ilegivel aborta o ato ANTES de qualquer efeito ----
            def c8():
                # A captura acontece na ABERTURA do fluxo. Um disco ilegivel tem de
                # recusar ali: antes do export, antes de qualquer save(), antes do
                # clear e antes do broadcast. Por isso o caso usa o botao REAL.
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                page.evaluate("() => localStorage.setItem('%s', '{documento truncado')" % LSKEY)
                page.evaluate("""() => {
                    window.__tocadas = [];
                    const orig = localStorage.setItem.bind(localStorage);
                    localStorage.setItem = (k, v) => { window.__tocadas.push(k); return orig(k, v); };
                }""")
                page.locator("#finalizeSessionBtn").click()
                page.wait_for_timeout(500)
                r = page.evaluate("""() => {
                    const caixa = document.getElementById('modalBox');
                    return { tocadas: window.__tocadas,
                             modal: caixa ? (caixa.textContent || '') : '',
                             bloqueada: jpWealthPersistenceIsBlocked(),
                             contas: S.accounts.length,
                             instrumentos: (S && S.alladin && S.alladin.instruments) ? S.alladin.instruments.length : -1,
                             disco: localStorage.getItem('%s'),
                             temProceed: !!document.getElementById('sessionProceed'),
                             temExport: !!document.getElementById('sessionExport') };
                }""" % LSKEY)
                if "Nada foi apagado" not in r["modal"]:
                    falhas.append(f"C8: disco ilegivel nao mostrou a tela de recusa (modal={r['modal'][:90]!r})")
                if r["temProceed"] or r["temExport"]:
                    falhas.append("C8: o fluxo AVANCOU para export/confirmacao apesar de nao poder preservar")
                if SINAL in r["tocadas"]:
                    falhas.append("C8 ORDEM: as outras abas foram avisadas apesar do abort")
                if r["disco"] != "{documento truncado":
                    falhas.append(f"C8: o disco foi tocado apesar da recusa ({str(r['disco'])[:60]})")
                if r["bloqueada"] is not False:
                    falhas.append("C8: a recusa deixou a persistencia BLOQUEADA")
                if r["contas"] == 0:
                    falhas.append("C8: a sessao foi PARCIALMENTE finalizada — accounts foi zerado")
                if r["instrumentos"] != len(FIXTURE["instruments"]):
                    falhas.append(f"C8: S.alladin foi alterado apesar da recusa ({r['instrumentos']})")
                # CONTRATO NOVO (Camada 1): o disco contem uma escrita que esta aba nao
                # reconhece (o lixo plantado). save() DEVE ser recusado — gravar S por
                # cima seria o lost update que a guarda existe para impedir. E a recusa
                # nao pode bloquear a aba (B3): persistencia segue desbloqueada.
                pos = page.evaluate("() => ({ gravou: save(), bloqueada: jpWealthPersistenceIsBlocked() })")
                if pos["gravou"] is not False:
                    falhas.append("C8: save() gravou por cima de um disco que a aba nao reconhece")
                if pos["bloqueada"] is not False:
                    falhas.append("C8: a recusa da guarda deixou a persistencia BLOQUEADA")
                if erros:
                    falhas.append(f"C8 pageerror: {erros}")
            executar(falhas, "C8", c8)

            def c9():
                for rotulo, agregado in (("v2", FIXTURE), ("v3 (future-schema)", FUTURO)):
                    ctx, page, erros = abrir(browser, url)
                    # A fonte do fluxo remoto e o DISCO: e ele que precisa carregar o
                    # agregado, inclusive quando o build nao sabe ler a versao.
                    page.evaluate("(a) => { S.alladin = a; save(); }", agregado)
                    page.evaluate(SEMEAR_DOC_FINALIZADO, agregado)
                    r = page.evaluate(REMOTO, "aba-remota-c9-" + rotulo)
                    if not igual(r["memoria"], agregado):
                        falhas.append(f"C9 [{rotulo}] MEMORIA: finalizacao vinda de outra aba alterou o Alladin")
                    if not igual(do_disco(page), agregado):
                        falhas.append(f"C9 [{rotulo}] DISCO: agregado nao sobreviveu a finalizacao remota "
                                      f"({str(do_disco(page))[:70]})")
                    if not (r["contas"] == 0 and r["ledger"] == 0):
                        falhas.append(f"C9 [{rotulo}]: a finalizacao remota nao encerrou a sessao: {r}")
                    if agregado is FUTURO:
                        compat = page.evaluate("() => JPWAlladin.compat()")
                        if not (compat["readOnly"] is True and compat["storedSchemaVersion"] == 3):
                            falhas.append(f"C9 [{rotulo}]: a preservacao remota REBAIXOU a versao do agregado: {compat}")
                    if erros:
                        falhas.append(f"C9 [{rotulo}] pageerror: {erros}")
            executar(falhas, "C9", c9)

            # ---- C10: cross-tab usa o DISCO, nao a memoria obsoleta ----
            def c10():
                ctx, page, erros = abrir(browser, url)
                # Memoria desta aba: retrato ANTIGO, com os registros que o operador
                # ja apagou. Disco: documento autoritativo escrito pela aba que
                # finalizou, ja sem esses registros.
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                page.evaluate(SEMEAR_DOC_FINALIZADO, REDUZIDO)
                r = page.evaluate(REMOTO, "aba-remota-c10")
                if igual(r["memoria"], FIXTURE):
                    falhas.append("C10: a finalizacao remota RESSUSCITOU registros que o operador apagou "
                                  "(preservou a memoria obsoleta em vez do estado persistido)")
                elif not igual(r["memoria"], REDUZIDO):
                    falhas.append(f"C10 MEMORIA: agregado difere do estado persistido ({r['memoria'][:80]})")
                if not igual(do_disco(page), REDUZIDO):
                    falhas.append(f"C10 DISCO: o disco nao ficou com o agregado persistido ({str(do_disco(page))[:80]})")
                if erros:
                    falhas.append(f"C10 pageerror: {erros}")
            executar(falhas, "C10", c10)

            # ---- C11: cross-tab com disco ilegivel ABORTA (nao cai na memoria velha) ----
            def c11():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                page.evaluate("() => localStorage.setItem('%s', '{documento truncado')" % LSKEY)
                r = page.evaluate(REMOTO, "aba-remota-c11")
                bruto = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                if bruto != "{documento truncado":
                    falhas.append(f"C11: o disco ilegivel foi sobrescrito em vez de o ato abortar ({str(bruto)[:60]})")
                if r["contas"] == 0:
                    falhas.append("C11: a sessao foi finalizada mesmo sem conseguir ler o estado persistido")
                # CONTRATO B3: o abort nao pode deixar a aba permanentemente read-only.
                # A protecao anti-ressurreicao mudou de dono: e a guarda de concorrencia
                # do save() (o disco nao e o que esta aba conhece => escrita recusada).
                if r["bloqueada"] is not False:
                    falhas.append("C11: o abort remoto deixou a aba PERMANENTEMENTE bloqueada (viola B3)")
                pos = page.evaluate("() => save()")
                if pos is not False:
                    falhas.append("C11: save() sobrescreveu um disco que a aba nao reconhece — ressurreicao possivel")
                if erros:
                    falhas.append(f"C11 pageerror: {erros}")
            executar(falhas, "C11", c11)

            # ---- C14: cross-tab na JANELA em que a chave principal nao existe ----
            def c14():
                # Com write-before-clear + broadcast pos-commit, o emissor NUNCA remove
                # a chave principal: ausencia aqui e anomalia real (limpeza externa,
                # wipe legado). O handler recusa sem tocar nada e — contrato B3 — sem
                # deixar a aba permanentemente read-only; a guarda do save() e quem
                # impede a regravacao de memoria velha sobre o disco indeterminado.
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                page.evaluate("() => localStorage.removeItem('%s')" % LSKEY)
                r = page.evaluate(REMOTO, "aba-remota-c14")
                if igual(r["memoria"], {"schemaVersion": 2, "reportingCurrency": "BRL",
                                        "instruments": [], "assets": [], "accounts": [],
                                        "cashAccounts": []}):
                    falhas.append("C14: com a chave principal ausente o handler ZEROU o Alladin "
                                  "(tratou disco indeterminado como estado legado)")
                elif not igual(r["memoria"], FIXTURE):
                    falhas.append(f"C14: o agregado em memoria foi alterado pelo abort ({r['memoria'][:80]})")
                if do_disco(page) is not None:
                    falhas.append(f"C14: o handler GRAVOU no disco apesar de nao poder ler o estado persistido "
                                  f"({str(do_disco(page))[:80]})")
                if r["contas"] == 0:
                    falhas.append("C14: a sessao foi finalizada sem conseguir garantir a preservacao")
                if r["bloqueada"] is not False:
                    falhas.append("C14: o abort deixou a aba PERMANENTEMENTE bloqueada (viola B3)")
                pos = page.evaluate("() => save()")
                if pos is not False:
                    falhas.append("C14: save() gravou sobre um disco sem chave que a aba nao reconhece")
                if erros:
                    falhas.append(f"C14 pageerror: {erros}")
            executar(falhas, "C14", c14)

            # ---- C12: a copia e profunda (o preservado nao aliasa o estado antigo) ----
            def c12():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); window.__velho = S; }", FIXTURE)
                finalizar_fluxo_real(page, falhas, "C12")
                depois = page.evaluate("""() => {
                    window.__velho.alladin.instruments.push({instrumentId:'aldi_contaminado'});
                    return S.alladin.instruments.length;
                }""")
                if depois != len(FIXTURE["instruments"]):
                    falhas.append(f"C12: o agregado preservado APONTA para o estado antigo (aliasing) — "
                                  f"mutar o antigo alterou o novo ({depois} instrumentos)")
                if erros:
                    falhas.append(f"C12 pageerror: {erros}")
            executar(falhas, "C12", c12)

            # ---- C13: estado legado, sem o agregado, nao quebra o fluxo ----
            def c13():
                ctx, page, erros = abrir(browser, url)
                padrao = page.evaluate("() => { delete S.alladin; save(); return JSON.stringify(DEFAULTS.alladin); }")
                finalizar_fluxo_real(page, falhas, "C13")
                depois = page.evaluate("() => JSON.stringify(S.alladin)")
                if json.loads(depois) != json.loads(padrao):
                    falhas.append(f"C13: estado sem agregado nao voltou ao DEFAULTS apos o ciclo ({depois[:80]})")
                if erros:
                    falhas.append(f"C13 pageerror: {erros}")
            executar(falhas, "C13", c13)

            # ---- C15: fluxo LOCAL preserva o DISCO, nao a memoria obsoleta ----
            def c15():
                # Cenario da auditoria: a aba que finaliza tem um retrato ANTERIOR a
                # tres atos que o operador ja confirmou em outra aba — status,
                # campo textual e PII de terceiro. Finalizar jamais pode desfaze-los.
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                page.evaluate("""(r) => {
                    const doc = JSON.parse(localStorage.getItem('%s'));
                    doc.alladin = r;
                    localStorage.setItem('%s', JSON.stringify(doc));
                }""" % (LSKEY, LSKEY), MAIS_RECENTE)
                # Caminho 'changed' REAL: e nele que o export dispara
                # dgRegisterExportSuccess -> save(), que regrava o documento a partir
                # da memoria obsoleta. O snapshot tem de ter sido capturado ANTES.
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FIXTURE):
                    falhas.append("C15 pre-condicao: a memoria deveria estar obsoleta e nao esta")
                e15 = finalizar_fluxo_real(page, falhas, "C15")
                if e15 != "changed":
                    falhas.append(f"C15: esperado o caminho 'changed' (com export real), veio '{e15}'")
                disco = do_disco(page)
                if igual(disco, FIXTURE):
                    falhas.append("C15: Finalizar Sessao DESFEZ no disco atos ja confirmados pelo operador "
                                  "(gravou a memoria obsoleta por cima do estado persistido)")
                elif not igual(disco, MAIS_RECENTE):
                    falhas.append(f"C15 DISCO: o disco nao ficou com o estado persistido mais recente ({str(disco)[:80]})")
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), MAIS_RECENTE):
                    falhas.append("C15 MEMORIA: o estado vivo nao ficou com o agregado autoritativo")
                if erros:
                    falhas.append(f"C15 pageerror: {erros}")
            executar(falhas, "C15", c15)

            # ---- C16: fluxo LOCAL, future-schema vindo do DISCO, sem transformacao ----
            def c16():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(a) => { S.alladin = a; save(); }", FIXTURE)
                page.evaluate("""(r) => {
                    const doc = JSON.parse(localStorage.getItem('%s'));
                    doc.alladin = r;
                    localStorage.setItem('%s', JSON.stringify(doc));
                }""" % (LSKEY, LSKEY), FUTURO)
                # Caminho 'changed' REAL: e nele que o export dispara
                # dgRegisterExportSuccess -> save(), que regrava o documento a partir
                # da memoria obsoleta. O snapshot tem de ter sido capturado ANTES.
                e16 = finalizar_fluxo_real(page, falhas, "C16")
                if e16 != "changed":
                    falhas.append(f"C16: esperado o caminho 'changed' (com export real), veio '{e16}'")
                if not igual(do_disco(page), FUTURO):
                    falhas.append(f"C16 DISCO: o agregado v3 vindo do disco foi transformado ({str(do_disco(page))[:80]})")
                if not igual(page.evaluate("() => JSON.stringify(S.alladin)"), FUTURO):
                    falhas.append("C16 MEMORIA: o agregado v3 vindo do disco foi transformado")
                compat = page.evaluate("() => JPWAlladin.compat()")
                if not (compat["readOnly"] is True and compat["storedSchemaVersion"] == 3):
                    falhas.append(f"C16: a preservacao local REBAIXOU a versao do agregado: {compat}")
                if erros:
                    falhas.append(f"C16 pageerror: {erros}")
            executar(falhas, "C16", c16)

            # ---- C17: fluxo LOCAL com a chave ausente PROSSEGUE (base virgem) ----
            def c17():
                # Base virgem e base recem-limpa legitimamente nao tem LSKEY
                # (verificado). No fluxo local nada foi destruido ainda e nenhum
                # save() bem-sucedido ocorreu, logo nao ha patrimonio comprometido:
                # abortar aqui tornaria Finalizar Sessao inoperante numa maquina nova.
                ctx, page, erros = abrir(browser, url)
                page.evaluate("() => localStorage.removeItem('%s')" % LSKEY)
                finalizar_fluxo_real(page, falhas, "C17")
                r = page.evaluate("""() => ({
                    contas: S.accounts.length,
                    modal: (document.getElementById('modalBox') || {}).textContent || '',
                    alladin: JSON.stringify(S.alladin), padrao: JSON.stringify(DEFAULTS.alladin) })""")
                if "Nada foi apagado" in r["modal"]:
                    falhas.append("C17: o fluxo local ABORTOU numa base sem chave principal — "
                                  "Finalizar Sessao ficaria inoperante em maquina nova ou recem-limpa")
                if r["contas"] != 0:
                    falhas.append(f"C17: a sessao nao foi encerrada ({r['contas']} contas)")
                if json.loads(r["alladin"]) != json.loads(r["padrao"]):
                    falhas.append(f"C17: agregado inesperado apos o ciclo ({r['alladin'][:80]})")
                if erros:
                    falhas.append(f"C17 pageerror: {erros}")
            executar(falhas, "C17", c17)


            browser.close()
    finally:
        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        servidor.shutdown()

    if falhas:
        print("ALLADIN FINALIZE PRESERVATION TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("ALLADIN FINALIZE PRESERVATION TEST PASS (C1-C17: preservacao integral em memoria e disco, "
          "future-schema intacto atraves do reload e ainda somente-leitura, Zona de Perigo continua apagando, "
          "sessao encerrada, sem chave nova nem contaminacao de auxiliar, dois ciclos por caminhos distintos, "
          "atomicidade com ordem e persistencia assertadas, cross-tab preserva do estado persistido sem "
          "ressuscitar registro apagado, aborta bloqueado quando ilegivel, copia profunda, legado sem agregado)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
