#!/usr/bin/env python3
"""Finalizar Sessao preserva personalFinance INTEGRALMENTE (PF-01, Bloco D).

personalFinance e memoria financeira longitudinal — nao pertence ao periodo de
trading que a Finalizacao encerra. Este teste percorre o fluxo REAL de
Finalizar Sessao (modal, export, frase de confirmacao) com o agregado semeado
pela fixture sintetica canonica, e exige DEEP EQUALITY antes/depois — nao
amostragem de duas ou tres propriedades.

Independente do teste de backup (finpes_backup_roundtrip_test.py): Finalizar
Sessao NAO e sinonimo de wipe, e os dois contratos se provam separados.

Fixture: tools/fixtures/personal_finance_v1.json (100% sintetica).
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
FIXTURE = json.loads((ROOT / "tools/fixtures/personal_finance_v1.json").read_text(encoding="utf-8"))["personalFinance"]


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


def click_id(page, element_id):
    page.locator("#" + element_id).click()


def modal_text(page):
    return page.locator("#modalBox").inner_text().lower()


def main():
    servidor, url = serve()
    falhas = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(viewport={"width": 1440, "height": 900})
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
            page.wait_for_function("() => typeof S === 'object' && typeof save === 'function'")
            # mesmo preparo do harness canonico de finalizacao: fecha o modal de
            # onboarding e stuba o download que o passo de export dispara.
            page.wait_for_timeout(500)
            page.evaluate("""() => {
                window.alert = () => {};
                closeModal();
                window.URL.createObjectURL = () => 'blob:jpwealth-test';
                window.URL.revokeObjectURL = () => {};
                HTMLAnchorElement.prototype.click = function(){ window.__jpwealthDownload={filename:this.download}; };
            }""")

            # semeia o agregado NAO TRIVIAL pela fixture canonica e persiste
            page.evaluate(
                """(pf) => { S.personalFinance = pf; save(); }""",
                FIXTURE,
            )
            antes = page.evaluate("() => JSON.stringify(S.personalFinance)")
            if json.loads(antes) != FIXTURE:
                falhas.append("semeadura da fixture nao sobreviveu ao save() — pre-condicao quebrada")

            # fluxo REAL de Finalizar Sessao. Como acabamos de semear e gravar,
            # a primeira tela e DETERMINISTICAMENTE o checkpoint de backup —
            # "existem alteracoes posteriores ao ultimo backup" — e nao o texto
            # de finalizacao direta.
            click_id(page, "finalizeSessionBtn")
            page.wait_for_timeout(300)
            if "posteriores ao último backup" not in modal_text(page):
                falhas.append(f"checkpoint de backup nao apareceu; modal: {modal_text(page)[:120]}")
            click_id(page, "sessionExport")
            page.locator("#sessionExportAcknowledged").check()
            click_id(page, "sessionExportContinue")
            click_id(page, "sessionProceed")
            page.locator("#sessionDeletePhrase").fill("APAGAR TUDO")
            page.locator("#sessionDeleteConfirm").click()
            page.wait_for_timeout(600)

            # DEEP EQUALITY do agregado inteiro, em memoria e no disco
            depois = page.evaluate("() => JSON.stringify(S.personalFinance)")
            if json.loads(depois) != FIXTURE:
                falhas.append(
                    "personalFinance NAO sobreviveu integralmente a Finalizar Sessao (memoria): "
                    "o agregado difere da fixture apos o fluxo")
            disco = page.evaluate(
                f"""() => {{
                    const raw = localStorage.getItem({json.dumps(LSKEY)});
                    if(!raw) return null;
                    try {{ return JSON.stringify(JSON.parse(raw).personalFinance); }}
                    catch(e) {{ return 'CORROMPIDO'; }}
                }}""")
            if disco is None:
                falhas.append("disco vazio apos finalizacao — a escrita deliberada pos-wipe nao preservou nada")
            elif disco == "CORROMPIDO" or json.loads(disco) != FIXTURE:
                falhas.append("personalFinance no DISCO difere da fixture apos Finalizar Sessao")

            # e o resto da sessao foi de fato encerrado (a heranca nao pode
            # ter transformado a finalizacao em no-op)
            resto = page.evaluate("""() => ({
                contas: S.accounts.length, ledger: S.ledger.length,
                onboarding: S.onboarding.done })""")
            if resto["contas"] != 0 or resto["ledger"] != 0 or resto["onboarding"] is not False:
                falhas.append(f"a finalizacao nao encerrou a sessao de trading: {resto}")

            paginas_com_erro = [e for e in erros if e]
            if paginas_com_erro:
                falhas.append(f"pageerror durante o fluxo: {paginas_com_erro}")

            context.close()
            browser.close()
    finally:
        servidor.shutdown()

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES FINALIZE PRESERVATION TEST PASS — agregado integro em memoria e no disco; sessao de trading encerrada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
