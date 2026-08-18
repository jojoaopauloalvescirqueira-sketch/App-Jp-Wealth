#!/usr/bin/env python3
"""Round-trip de backup do personalFinance em CONTEXTO ISOLADO (PF-01, Bloco E).

Contrato exato do congelamento do schema:

    estado A (fixture sintetica) -> exportar -> CONTEXTO ISOLADO COM STORAGE
    VAZIO -> importar -> estado B -> comparar propriedades materiais

O "estado isolado vazio" e um BrowserContext novo do Playwright com
localStorage virgem — nao ha wipe envolvido, e este teste e INDEPENDENTE do
teste de Finalizar Sessao (sao operacoes semanticamente diferentes).

Prova: centavos exatos, null preservado, unknown fields preservados,
schemaVersion e moneyUnit preservados, months e arrays integrais. O formato
normativo de backup existente e usado como esta — nenhum backup paralelo.

Fixture: tools/fixtures/personal_finance_v1.json (100% sintetica).
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

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


def boot(browser, url):
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
    page.wait_for_timeout(400)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return context, page, erros


def main():
    servidor, url = serve()
    falhas = []
    caminho_backup = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            # ---- ESTADO A: semeia a fixture e exporta pelo controle REAL ----
            ctx_a, page_a, erros_a = boot(browser, url)
            page_a.evaluate("(pf) => { S.personalFinance = pf; save(); }", FIXTURE)
            page_a.evaluate("() => { document.getElementById('headerConfigBtn').click(); }")
            page_a.evaluate("settingsNavigateToLeaf('backup')")
            page_a.evaluate("""() => {
                window.URL.createObjectURL = (blob) => { window.__pfBlob = blob; return 'blob:pf'; };
                window.URL.revokeObjectURL = () => {};
                HTMLAnchorElement.prototype.click = function(){};
            }""")
            page_a.locator('#exportFullBackupBtn').click()
            exportado = page_a.evaluate("window.__pfBlob.text()")
            payload = json.loads(exportado)
            if payload.get("tipo") != "jpwealth_full_backup":
                falhas.append(f"envelope normativo violado: tipo={payload.get('tipo')}")
            if json_norm(payload.get("state", {}).get("personalFinance")) != json_norm(FIXTURE):
                falhas.append("o EXPORT ja perdeu ou alterou o agregado — antes mesmo do import")
            ctx_a.close()

            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                f.write(exportado)
                caminho_backup = f.name

            # ---- ESTADO B: contexto ISOLADO com storage virgem + import real ----
            ctx_b, page_b, erros_b = boot(browser, url)
            virgem = page_b.evaluate("() => JSON.stringify(S.personalFinance) === JSON.stringify(DEFAULTS.personalFinance)")
            if not virgem:
                falhas.append("o contexto B nao nasceu virgem — o isolamento do teste esta quebrado")
            page_b.evaluate("() => { document.getElementById('headerConfigBtn').click(); }")
            page_b.evaluate("settingsNavigateToLeaf('backup')")
            page_b.evaluate("window.confirm = () => true")
            page_b.locator('#importFullBackupInput').set_input_files(caminho_backup)
            page_b.wait_for_timeout(800)
            page_b.evaluate("() => { window.__onbShown = true; closeModal(); }")

            depois = page_b.evaluate("() => JSON.stringify(S.personalFinance)")
            b = json.loads(depois)
            if json_norm(b) != json_norm(FIXTURE):
                # acusa a PROPRIEDADE mais especifica possivel
                detalhes = []
                if b.get("schemaVersion") != FIXTURE["schemaVersion"]: detalhes.append("schemaVersion")
                if b.get("moneyUnit") != FIXTURE["moneyUnit"]: detalhes.append("moneyUnit")
                if b.get("extensaoFutura") != FIXTURE["extensaoFutura"]: detalhes.append("unknown field do agregado")
                if json_norm(b.get("months")) != json_norm(FIXTURE["months"]): detalhes.append("months")
                for k in ("recurringIncome", "debts", "creditLines", "scenarios"):
                    if json_norm(b.get(k)) != json_norm(FIXTURE[k]): detalhes.append(k)
                falhas.append("round-trip perdeu ou alterou: " + (", ".join(detalhes) or "diferenca nao localizada"))
            else:
                # propriedades materiais NOMINAIS, alem do deep-equal: centavos
                # exatos, null vs 0 explicito, unknown em registro
                m7 = b["months"]["2026-07"]
                if m7["incomes"][1]["receivedAmount"] is not None:
                    falhas.append("null virou outra coisa no round-trip")
                if m7["incomes"][2]["receivedAmount"] != 50000:
                    falhas.append("centavos nao sobreviveram exatos (recebido da cancelada)")
                if b["months"]["2026-08"]["incomes"][0]["receivedAmount"] != 0:
                    falhas.append("zero explicito nao sobreviveu como 0")
                if m7["expenses"][1]["executedCard"] is not None:
                    falhas.append("canal desconhecido (null) foi fabricado no round-trip")
                if b["creditLines"][0].get("notaEstouro") != "used > totalLimit e legitimo: 110%":
                    falhas.append("unknown field de registro perdido no round-trip")

            if erros_a or erros_b:
                falhas.append(f"pageerror: A={erros_a} B={erros_b}")
            ctx_b.close()
            browser.close()
    finally:
        servidor.shutdown()
        if caminho_backup:
            try: os.unlink(caminho_backup)
            except OSError: pass

    if falhas:
        print("FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("FINPES BACKUP ROUNDTRIP TEST PASS — export/import em contexto isolado preserva o agregado ao centavo")
    return 0


def json_norm(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


if __name__ == "__main__":
    sys.exit(main())
