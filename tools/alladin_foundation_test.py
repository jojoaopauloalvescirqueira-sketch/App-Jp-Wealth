#!/usr/bin/env python3
"""Alladin ALD-01 C1 — INTEGRACAO da Foundation Infrastructure no app real.

Prova as propriedades de persistencia do agregado S.alladin no navegador:
  A  migrate de base legada (sem a chave) — nasce de DEFAULTS, vizinhos intactos
  B  round-trip load→save byte-identico com registros e campos desconhecidos
  C  FAIL-CLOSED: schemaVersion futura — agregado byte-intacto, ato recusado,
     incompatibilidade exposta em JPWAlladin.compat()
  D  coercao de envelope APENAS em versao suportada; extras preservados
  E  contêiner nao-objeto renasce de DEFAULTS (nenhum registro a preservar)
  F  ROLLBACK POR BUILD ANTIGO: a revisao pre-Alladin (git archive do SHA
     pinado) carrega estado COM alladin, grava, e preserva a chave byte a byte
  G  string com forma de XSS em registro atravessa a migracao como TEXTO
  H  superficie window.JPWAlladin presente e coerente no app real
  I  ato via aldMutate registra no log operacional (dgLogChange) — log
     NAO-canonico por HD-6; nao e prova de ALD-I26
  J  save()===false e prova de nao-escrita no gate

Caso F e condicionado ao historico local: em clone raso sem o SHA base, o caso
e reportado como nao executado por ambiente (sem marcador de classificacao) e
os demais seguem valendo.
"""
import io
import json
import os
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = "jpwealth_v9_state"
# Ultima revisao ANTES da fundacao Alladin (merge da Remediation B do PF).
# Imutavel no historico: e o "build antigo" canonico da prova de rollback.
OLD_BUILD_SHA = "fc2973134cc72f9e17a747f9299f3979461d8bc8"

PRONTO_NOVO = "() => typeof S === 'object' && window.JPWAlladin && typeof aldMutate === 'function'"
PRONTO_ANTIGO = "() => typeof S === 'object' && typeof save === 'function' && typeof migrate === 'function'"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve(directory=None):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    handler = partial(QuietHandler, directory=str(directory)) if directory else QuietHandler
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


def boot(browser, url, pronto, mutacao_js=None):
    context = browser.new_context(viewport={"width": 1440, "height": 950})
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
    page.wait_for_function(pronto)
    if mutacao_js:
        page.evaluate(f"""() => {{
            {mutacao_js}
            localStorage.setItem({json.dumps(LSKEY)}, JSON.stringify(S));
        }}""")
        page.reload(wait_until="load")
        page.wait_for_function(pronto)
    page.wait_for_timeout(300)
    return context, page, erros


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

        # ---- A: base legada sem a chave ------------------------------------
        def caso_a():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, "delete S.alladin;")
            r = page.evaluate("""() => ({
                forma: JSON.stringify(S.alladin),
                pf: !!(S.personalFinance && S.personalFinance.moneyUnit === 'BRL_CENTS'),
                saldo: S.params && typeof S.params.saldoIni === 'number',
            })""")
            esperado = json.dumps({"schemaVersion": 1, "reportingCurrency": "BRL",
                                   "instruments": [], "assets": [], "accounts": [],
                                   "cashAccounts": []}, separators=(",", ":"))
            if r["forma"] != esperado:
                falhas.append(f"A: agregado legado nao nasceu de DEFAULTS: {r['forma']}")
            if not (r["pf"] and r["saldo"]):
                falhas.append("A: vizinhos (personalFinance/params) alterados pela migracao do alladin")
            if erros:
                falhas.append(f"A: pageerror {erros}")
            ctx.close()
        executar(falhas, "A", caso_a)

        # ---- B: round-trip com registro e campos desconhecidos -------------
        FIXTURE_B = ("{schemaVersion:1, reportingCurrency:'BRL',"
                     "instruments:[{instrumentId:'aldi_fx_1', name:'Petrobras PN', symbol:'PETR4',"
                     " currency:'BRL', campoDesconhecido:{x:1}}],"
                     "assets:[], accounts:[], cashAccounts:[],"
                     "extensaoFutura:'preservar'}")

        def caso_b():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, f"S.alladin = {FIXTURE_B};")
            r = page.evaluate(f"""() => {{
                const esperado = JSON.stringify({FIXTURE_B});
                const aposLoad = JSON.stringify(S.alladin);
                S.theme = S.theme === 'dark' ? 'light' : 'dark';
                const gravou = save();
                const persistido = JSON.parse(localStorage.getItem({json.dumps(LSKEY)}));
                return {{ igualLoad: aposLoad === esperado,
                         igualDisco: JSON.stringify(persistido.alladin) === esperado,
                         gravouTheme: persistido.theme === S.theme, gravou }};
            }}""")
            if not r["igualLoad"]:
                falhas.append("B: load alterou registro/campo desconhecido do agregado")
            if not r["gravouTheme"]:
                falhas.append("B: save() nao regravou o estado (theme do disco difere) — round-trip nao provado")
            if not (r["gravou"] and r["igualDisco"]):
                falhas.append("B: round-trip via save() nao preservou byte a byte")
            if erros:
                falhas.append(f"B: pageerror {erros}")
            ctx.close()
        executar(falhas, "B", caso_b)

        # ---- C: fail-closed de schema futuro -------------------------------
        FIXTURE_C = ("{schemaVersion:3, reportingCurrency:42,"
                     "instruments:'nem-lista', novaColecao:[{id:1}]}")

        def caso_c():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, f"S.alladin = {FIXTURE_C};")
            r = page.evaluate(f"""() => {{
                const esperado = JSON.stringify({FIXTURE_C});
                const intacto = JSON.stringify(S.alladin) === esperado;
                const compat = JPWAlladin.compat();
                let fnRodou = false;
                const ato = aldMutate('c1_probe_bloqueado', () => {{ fnRodou = true; return {{recordId: 'x'}}; }});
                const aindaIntacto = JSON.stringify(S.alladin) === esperado;
                return {{ intacto, aindaIntacto, compat, ato, fnRodou }};
            }}""")
            if not (r["intacto"] and r["aindaIntacto"]):
                falhas.append("C: fail-closed violado — a migracao ou o ato tocou o agregado futuro")
            c = r["compat"]
            if not (c["readOnly"] is True and c["storedSchemaVersion"] == 3
                    and c["reason"] == "READ_ONLY_FUTURE_SCHEMA"):
                falhas.append(f"C: incompatibilidade nao exposta: {c!r}")
            if r["fnRodou"] or r["ato"].get("erro") != "READ_ONLY_FUTURE_SCHEMA":
                falhas.append(f"C: aldMutate nao recusou integralmente: {r['ato']!r}")
            if erros:
                falhas.append(f"C: pageerror {erros}")
            ctx.close()
        executar(falhas, "C", caso_c)

        # ---- C2: versao futura como STRING de digitos ('2') tambem fail-closed
        FIXTURE_C2 = "{schemaVersion:'2', reportingCurrency:'BRL', dadoFuturo:[1,2]}"

        def caso_c_string():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, f"S.alladin = {FIXTURE_C2};")
            r = page.evaluate(f"""() => {{
                const esperado = JSON.stringify({FIXTURE_C2});
                const intacto = JSON.stringify(S.alladin) === esperado;
                const compat = JPWAlladin.compat();
                const ato = aldMutate('probe_c2', () => ({{recordId: 'x'}}));
                return {{ intacto, compat, erro: ato.erro }};
            }}""")
            if not r["intacto"]:
                falhas.append("C2: versao futura em string foi coagida — fail-closed furado")
            if not (r["compat"]["readOnly"] is True and r["compat"]["storedSchemaVersion"] == 2
                    and r["erro"] == "READ_ONLY_FUTURE_SCHEMA"):
                falhas.append(f"C2: bloqueio/exposicao incoerente: {r!r}")
            if erros:
                falhas.append(f"C2: pageerror {erros}")
            ctx.close()
        executar(falhas, "C2", caso_c_string)

        # ---- D: coercao de envelope so em versao suportada -----------------
        def caso_d():
            ctx, page, erros = boot(
                browser, url, PRONTO_NOVO,
                "S.alladin = {schemaVersion:'x', reportingCurrency:7, instruments:'nope',"
                " assets:[{assetId:'alda_1', name:'Bem'}], extra:'fica'};")
            r = page.evaluate("""() => ({
                v: S.alladin.schemaVersion, rc: S.alladin.reportingCurrency,
                inst: JSON.stringify(S.alladin.instruments),
                assets: JSON.stringify(S.alladin.assets),
                extra: S.alladin.extra,
            })""")
            if r["v"] != 1 or r["rc"] != "BRL" or r["inst"] != "[]":
                falhas.append(f"D: envelope nao coagido como contrato: {r!r}")
            if r["assets"] != '[{"assetId":"alda_1","name":"Bem"}]' or r["extra"] != "fica":
                falhas.append(f"D: conteudo/extras nao preservados: {r!r}")
            if erros:
                falhas.append(f"D: pageerror {erros}")
            ctx.close()
        executar(falhas, "D", caso_d)

        # ---- E: contêiner nao-objeto renasce vazio -------------------------
        def caso_e():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, "S.alladin = 'corrompido';")
            r = page.evaluate("() => JSON.stringify(S.alladin)")
            if json.loads(r).get("schemaVersion") != 1 or json.loads(r).get("instruments") != []:
                falhas.append(f"E: contêiner escalar nao renasceu de DEFAULTS: {r}")
            if erros:
                falhas.append(f"E: pageerror {erros}")
            ctx.close()
        executar(falhas, "E", caso_e)

        # ---- F: rollback por build antigo (git archive do SHA pinado) ------
        def caso_f():
            tem_sha = subprocess.run(["git", "cat-file", "-e", OLD_BUILD_SHA],
                                     cwd=ROOT, capture_output=True).returncode == 0
            if not tem_sha:
                print("F: caso de rollback nao executado por ambiente (SHA base ausente do clone)")
                return
            with tempfile.TemporaryDirectory() as tmp:
                tar_bytes = subprocess.run(["git", "archive", OLD_BUILD_SHA], cwd=ROOT,
                                           capture_output=True, check=True).stdout
                with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
                    tf.extractall(tmp, filter="data")
                old_server, old_url = serve(directory=tmp)
                try:
                    fixture = ("{schemaVersion:1, reportingCurrency:'BRL',"
                               "instruments:[{instrumentId:'aldi_roll', symbol:'PETR4'}],"
                               "assets:[], accounts:[], cashAccounts:[], marca:'rollback'}")
                    ctx, page, erros = boot(browser, old_url, PRONTO_ANTIGO,
                                            f"S.alladin = {fixture};")
                    r = page.evaluate(f"""() => {{
                        const esperado = JSON.stringify({fixture});
                        const aposLoad = JSON.stringify(S.alladin) === esperado;
                        S.theme = S.theme === 'dark' ? 'light' : 'dark';
                        const gravou = save();
                        const persistido = JSON.parse(localStorage.getItem({json.dumps(LSKEY)}));
                        return {{ aposLoad, gravou,
                                 igualDisco: JSON.stringify(persistido.alladin) === esperado,
                                 gravouTheme: persistido.theme === S.theme,
                                 semModulo: typeof window.JPWAlladin === 'undefined' }};
                    }}""")
                    if not r["semModulo"]:
                        falhas.append("F: o 'build antigo' contem o modulo Alladin — extracao errada")
                    if not r["gravouTheme"]:
                        falhas.append("F: save() do build antigo nao regravou o estado — prova invalida")
                    if not (r["aposLoad"] and r["gravou"] and r["igualDisco"]):
                        falhas.append(f"F: build antigo NAO preservou S.alladin dormente: {r!r}")
                    if erros:
                        falhas.append(f"F: pageerror no build antigo {erros}")
                    ctx.close()
                finally:
                    old_server.shutdown()
        executar(falhas, "F", caso_f)

        # ---- G: payload com forma de XSS atravessa como texto --------------
        def caso_g():
            ctx, page, erros = boot(
                browser, url, PRONTO_NOVO,
                "S.alladin.assets = [{assetId:'alda_x',"
                " name:'<img src=x onerror=window.__xss=1>'}];")
            r = page.evaluate("""() => ({
                xss: window.__xss === undefined,
                texto: S.alladin.assets[0].name === '<img src=x onerror=window.__xss=1>',
            })""")
            if not r["xss"]:
                falhas.append("G: handler de payload executou durante a migracao")
            if not r["texto"]:
                falhas.append("G: payload nao atravessou como texto intacto")
            if erros:
                falhas.append(f"G: pageerror {erros}")
            ctx.close()
        executar(falhas, "G", caso_g)

        # ---- H, I, J no app real -------------------------------------------
        def caso_hij():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO)
            r = page.evaluate("""() => {
                const h = {
                    moedas: JPWAlladin.money.runtimeCurrencies(),
                    fmt: JPWAlladin.money.format({amount: 142050, currency: 'BRL'}),
                    compatOk: JPWAlladin.compat().readOnly === false,
                    // as constantes duplicadas (persistencia x dominio) DEVEM ser iguais
                    constEq: ALLADIN_SCHEMA_VERSION === JPWAlladin.compat().supportedSchemaVersion,
                };
                const antes = (S.dataGovernance.changeLog || []).length;
                const ato = aldMutate('c1_probe', () => ({recordId: 'probe'}), {label: 'c1_probe'});
                const log = (S.dataGovernance.changeLog || []).slice(-1)[0] || {};
                const i = { ato, delta: (S.dataGovernance.changeLog || []).length - antes,
                            entity: log.entity, action: log.action };
                const saveReal = save;
                window.save = () => false;
                let j;
                try { j = aldMutate('c1_probe_sem_disco', () => ({recordId: 'p2'})); }
                finally { window.save = saveReal; }
                return { h, i, j };
            }""")
            h, i, j = r["h"], r["i"], r["j"]
            if not (h["moedas"] == ["BRL", "USD"] and h["fmt"] == "R$ 1.420,50" and h["compatOk"]):
                falhas.append(f"H: superficie incoerente no app real: {h!r}")
            if h["constEq"] is not True:
                falhas.append("H: ALLADIN_SCHEMA_VERSION != ALD_SUPPORTED_SCHEMA_VERSION — constantes duplicadas divergiram")
            if not (i["ato"]["ok"] is True and i["delta"] == 1
                    and i["entity"] == "alladin" and i["action"] == "c1_probe"):
                falhas.append(f"I: log operacional nao registrou o ato: {i!r}")
            if not (j["ok"] is False and j["persistido"] is False):
                falhas.append(f"J: save()===false nao foi prova de nao-escrita: {j!r}")
            if erros:
                falhas.append(f"H/I/J: pageerror {erros}")
            ctx.close()
        executar(falhas, "HIJ", caso_hij)

        browser.close()
    server.shutdown()

    if falhas:
        print("alladin_foundation_test FALHOU")
        for f in falhas:
            print(" -", f)
        return 1
    print("alladin_foundation_test PASS (A-J; migracao, round-trip, fail-closed, rollback)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
