#!/usr/bin/env python3
"""Alladin — INTEGRACAO da fundacao (C1) e do modelo cadastral (C2) no app real.

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
  M  MIGRACAO v1 -> v2 (ALD-02 C2, exigencia OP-3.1): carimbo da versao sem
     transformar registro nem tocar vizinhos
  P  PERSISTENCIA REVERSIVEL (OP-3.3): criar asset -> save -> RELOAD REAL ->
     asset integro, owners inclusive
  Q  FALHA PARCIAL NAO SALVA (OP-3.2): ato recusado deixa agregado E disco
     byte-identicos
  R  XSS e privacidade: texto livre e owners[].name atravessam como TEXTO; o log
     operacional nao carrega nome de proprietario

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
# Build do C1 (ALLADIN_SCHEMA_VERSION=1): o rollback que o bump OP-4 criou.
C1_BUILD_SHA = "3f1f9bc09b406f76f552a749e1a00b3f9bfcef24"

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
            esperado = json.dumps({"schemaVersion": 3, "reportingCurrency": "BRL",
                                   "instruments": [], "assets": [], "accounts": [],
                                   "cashAccounts": [], "transactions": []},
                                  separators=(",", ":"))
            if r["forma"] != esperado:
                falhas.append(f"A: agregado legado nao nasceu de DEFAULTS: {r['forma']}")
            if not (r["pf"] and r["saldo"]):
                falhas.append("A: vizinhos (personalFinance/params) alterados pela migracao do alladin")
            if erros:
                falhas.append(f"A: pageerror {erros}")
            ctx.close()
        executar(falhas, "A", caso_a)

        # ---- B: round-trip com registro e campos desconhecidos -------------
        FIXTURE_B = ("{schemaVersion:3, reportingCurrency:'BRL', transactions:[],"
                     "instruments:[{instrumentId:'aldi_fx_1', name:'Petrobras PN', symbol:'PETR4',"
                     " exchange:'B3', country:null, currency:'BRL', assetClass:'RENDA_VARIAVEL',"
                     " instrumentFamily:'EQUITY_LIKE', externalIdentifiers:{isin:'BRPETRACNPR6'},"
                     " symbolHistory:[{symbol:'PETR4X', exchange:'B3', from:null, to:'2026-01-02T00:00:00.000Z'}],"
                     " recordStatus:'ACTIVE', createdAt:'2026-01-01T00:00:00.000Z', campoDesconhecido:{x:1}}],"
                     "assets:[{assetId:'alda_fx_1', name:'Apartamento', nature:'IMOVEL', category:null,"
                     " subcategory:null, strategicPurpose:'MORADIA', strategicGroup:null, tags:['moradia'],"
                     " recordMode:'INDIVIDUAL', owners:[{name:'Joao', shareBp:5000, isSelf:true},"
                     " {name:'Maria', shareBp:5000}], location:'Sao Paulo', acquisitionDate:null,"
                     " recordStatus:'ACTIVE', lifecycleStatus:'ACTIVE', createdAt:'2026-01-01T00:00:00.000Z'}],"
                     "accounts:[{accountId:'aldacc_fx_1', name:'XP', institution:'XP CCTVM',"
                     " accountType:'BROKERAGE', recordStatus:'ACTIVE', createdAt:'2026-01-01T00:00:00.000Z'}],"
                     "cashAccounts:[{cashAccountId:'aldc_fx_1', accountId:'aldacc_fx_1', currency:'BRL',"
                     " recordStatus:'ACTIVE', createdAt:'2026-01-01T00:00:00.000Z'}],"
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
        FIXTURE_C = ("{schemaVersion:4, reportingCurrency:42,"
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
            if not (c["readOnly"] is True and c["storedSchemaVersion"] == 4
                    and c["reason"] == "READ_ONLY_FUTURE_SCHEMA"):
                falhas.append(f"C: incompatibilidade nao exposta: {c!r}")
            if r["fnRodou"] or r["ato"].get("erro") != "READ_ONLY_FUTURE_SCHEMA":
                falhas.append(f"C: aldMutate nao recusou integralmente: {r['ato']!r}")
            if erros:
                falhas.append(f"C: pageerror {erros}")
            ctx.close()
        executar(falhas, "C", caso_c)

        # ---- C2: versao futura como STRING de digitos ('2') tambem fail-closed
        FIXTURE_C2 = "{schemaVersion:'4', reportingCurrency:'BRL', dadoFuturo:[1,2]}"

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
            if not (r["compat"]["readOnly"] is True and r["compat"]["storedSchemaVersion"] == 4
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
            if r["v"] != 3 or r["rc"] != "BRL" or r["inst"] != "[]":
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
            if json.loads(r).get("schemaVersion") != 3 or json.loads(r).get("instruments") != []:
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
                    fixture = ("{schemaVersion:2, reportingCurrency:'BRL',"
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


        # ---- M: migracao v1 -> v2 (exigencia OP-3.1) ------------------------
        FIXTURE_M = ("{schemaVersion:1, reportingCurrency:'BRL', instruments:[],"
                     "assets:[{assetId:'alda_legado', name:'Bem legado'}],"
                     "accounts:[], cashAccounts:[]}")

        def caso_m():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, f"S.alladin = {FIXTURE_M};")
            r = page.evaluate("""() => ({
                versao: S.alladin.schemaVersion,
                registro: JSON.stringify(S.alladin.assets),
                rc: S.alladin.reportingCurrency,
                compat: JPWAlladin.compat(),
                pf: !!(S.personalFinance && S.personalFinance.moneyUnit === 'BRL_CENTS'),
                saldo: !!(S.params && typeof S.params.saldoIni === 'number'),
            })""")
            if r["versao"] != 3:
                falhas.append(f"M: v1 nao migrou para v2: {r['versao']!r}")
            if r["registro"] != '[{"assetId":"alda_legado","name":"Bem legado"}]':
                falhas.append(f"M: a migracao TRANSFORMOU o registro: {r['registro']}")
            if r["rc"] != "BRL" or not (r["pf"] and r["saldo"]):
                falhas.append("M: migracao tocou moeda de apresentacao ou vizinhos")
            if r["compat"]["readOnly"] is not False:
                falhas.append(f"M: estado migrado ficou bloqueado indevidamente: {r['compat']!r}")
            if erros:
                falhas.append(f"M: pageerror {erros}")
            ctx.close()
        executar(falhas, "M", caso_m)

        # ---- P: persistencia reversivel (exigencia OP-3.3) ------------------
        def caso_p():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO)
            criado = page.evaluate("""() => JPWAlladin.cadastro.addAsset({
                name: 'Apartamento', nature: 'IMOVEL', recordMode: 'INDIVIDUAL',
                location: 'Sao Paulo', acquisitionDate: '2020-03-15', tags: ['moradia'],
                owners: [{name: 'Joao Paulo', shareBp: 5000, isSelf: true},
                         {name: 'Maria', shareBp: 5000}]})""")
            if not (criado.get("ok") and criado.get("persistido")):
                falhas.append(f"P: ato de criacao nao persistiu: {criado!r}")
            page.reload(wait_until="load")
            page.wait_for_function(PRONTO_NOVO)
            depois = page.evaluate(
                "id => { const a=(S.alladin.assets||[]).filter(x=>x.assetId===id)[0];"
                " return a ? {nome:a.name, nature:a.nature, life:a.lifecycleStatus, rec:a.recordStatus,"
                " aq:a.acquisitionDate, tags:JSON.stringify(a.tags), owners:JSON.stringify(a.owners),"
                " versao:S.alladin.schemaVersion} : null; }", criado.get("recordId"))
            if not depois:
                falhas.append("P: asset nao sobreviveu ao reload")
            else:
                esperado = ('[{"name":"Joao Paulo","shareBp":5000,"isSelf":true},'
                            '{"name":"Maria","shareBp":5000}]')
                if depois["owners"] != esperado:
                    falhas.append(f"P: owners nao sobreviveram integros: {depois['owners']}")
                if not (depois["nome"] == "Apartamento" and depois["nature"] == "IMOVEL"
                        and depois["life"] == "ACTIVE" and depois["rec"] == "ACTIVE"
                        and depois["aq"] == "2020-03-15" and depois["tags"] == '["moradia"]'
                        and depois["versao"] == 3):
                    falhas.append(f"P: campos divergiram apos reload: {depois!r}")
            if erros:
                falhas.append(f"P: pageerror {erros}")
            ctx.close()
        executar(falhas, "P", caso_p)

        # ---- Q: falha parcial nao salva (exigencia OP-3.2) ------------------
        def caso_q():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO)
            r = page.evaluate(f"""() => {{
                const conta = JPWAlladin.cadastro.addAccount({{name:'XP', institution:'XP', accountType:'BROKERAGE'}});
                const antes = JSON.stringify(S.alladin);
                const discoAntes = localStorage.getItem({json.dumps(LSKEY)});
                const recusas = [
                  JPWAlladin.cadastro.addAsset({{name:'X', nature:'IMOVEL', recordMode:'INDIVIDUAL',
                     owners:[{{name:'A', shareBp:9000}},{{name:'B', shareBp:9000}}]}}),
                  JPWAlladin.cadastro.addInstrument({{name:'T', symbol:'T', currency:'BRL',
                     instrumentFamily:'CRYPTO', assetClass:'CRIPTO'}}),
                  JPWAlladin.cadastro.addCashAccount({{accountId:'inexistente', currency:'BRL'}}),
                ];
                return {{ contaOk: conta.ok && !!discoAntes && discoAntes.indexOf(conta.recordId) >= 0,
                         igual: JSON.stringify(S.alladin) === antes,
                         discoIgual: localStorage.getItem({json.dumps(LSKEY)}) === discoAntes,
                         erros: recusas.map(x => x.erro), oks: recusas.map(x => x.ok) }};
            }}""")
            if not r["contaOk"]:
                falhas.append("Q: caminho de ESCRITA morto no disco — a comparacao seria tautologia")
            if not r["igual"]:
                falhas.append("Q: ato recusado MUTOU o agregado — falha parcial salva")
            if not r["discoIgual"]:
                falhas.append("Q: ato recusado tocou o disco")
            if any(r["oks"]):
                falhas.append(f"Q: ato invalido reportou sucesso: {r['oks']!r}")
            if r["erros"] != ["ALD_OWNERSHIP_ACIMA_DE_100", "ALD_CRYPTO_SEM_NETWORK",
                              "ALD_ACCOUNT_NAO_ENCONTRADA"]:
                falhas.append(f"Q: erros nao acusam a propriedade violada: {r['erros']!r}")
            if erros:
                falhas.append(f"Q: pageerror {erros}")
            ctx.close()
        executar(falhas, "Q", caso_q)

        # ---- R: XSS em texto livre/owners e privacidade do log --------------
        def caso_r():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO)
            r = page.evaluate("""() => {
                const payload = '<img src=x onerror=window.__xss=1>';
                const dono = 'Maria <script>window.__xss=1</script>';
                const res = JPWAlladin.cadastro.addAsset({
                    name: payload, nature: 'BEM_PESSOAL', recordMode: 'INDIVIDUAL',
                    location: '<svg onload=window.__xss=1>', tags: ['<b>tag</b>'],
                    owners: [{name: dono, shareBp: 10000, isSelf: true}]});
                const a = (S.alladin.assets || []).slice(-1)[0] || {};
                const log = JSON.stringify((S.dataGovernance.changeLog || []).slice(-1)[0] || {});
                return { ok: res.ok, xss: window.__xss === undefined,
                         nomeTexto: a.name === payload,
                         ownerTexto: !!a.owners && a.owners[0].name === dono,
                         logSemNome: log.indexOf('Maria') === -1 && log.indexOf('img src') === -1,
                         logEntidade: log.indexOf('"entity":"alladin"') >= 0 };
            }""")
            if not r["ok"]:
                falhas.append("R: ato legitimo com texto perigoso deveria ser aceito (escape e da UI)")
            if not r["xss"]:
                falhas.append("R: payload EXECUTOU durante cadastro/persistencia")
            if not (r["nomeTexto"] and r["ownerTexto"]):
                falhas.append(f"R: payload nao atravessou como texto intacto: {r!r}")
            if not r["logSemNome"]:
                falhas.append("R: log operacional carregou nome de proprietario — quebra de privacidade")
            if not r["logEntidade"]:
                falhas.append("R: ato cadastral nao registrou no log operacional")
            if erros:
                falhas.append(f"R: pageerror {erros}")
            ctx.close()
        executar(falhas, "R", caso_r)


        # ---- F2: ROLLBACK AO BUILD C1 — o cenario que justificou o bump OP-4 -
        # F prova preservacao por IGNORANCIA (build pre-Alladin). F2 prova
        # preservacao por FAIL-CLOSED: o C1 conhece o agregado, ve stored=2 >
        # supported=1 e recusa tudo, mantendo o dado byte-intacto.
        def caso_f2():
            tem = subprocess.run(["git", "cat-file", "-e", C1_BUILD_SHA],
                                 cwd=ROOT, capture_output=True).returncode == 0
            if not tem:
                print("F2: nao executado por ambiente (SHA do C1 ausente do clone)")
                return
            with tempfile.TemporaryDirectory() as tmp:
                tar = subprocess.run(["git", "archive", C1_BUILD_SHA], cwd=ROOT,
                                     capture_output=True, check=True).stdout
                with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
                    tf.extractall(tmp, filter="data")
                srv, c1url = serve(directory=tmp)
                try:
                    ctx, page, erros = boot(browser, c1url, PRONTO_NOVO, f"S.alladin = {FIXTURE_B};")
                    r = page.evaluate(f"""() => {{
                        const esperado = JSON.stringify({FIXTURE_B});
                        const intacto = JSON.stringify(S.alladin) === esperado;
                        const compat = JPWAlladin.compat();
                        const ato = aldMutate('c2_probe_no_c1', () => ({{recordId:'x'}}));
                        S.theme = S.theme === 'dark' ? 'light' : 'dark';
                        const gravou = save();
                        const persistido = JSON.parse(localStorage.getItem({json.dumps(LSKEY)}));
                        return {{ intacto, compat, erro: ato.erro, gravou,
                                 gravouTheme: persistido.theme === S.theme,
                                 discoIntacto: JSON.stringify(persistido.alladin) === esperado,
                                 temCadastro: !!(JPWAlladin.cadastro) }};
                    }}""")
                    if r["temCadastro"]:
                        falhas.append("F2: o build extraido NAO e o C1 (ja tem atos cadastrais)")
                    c = r["compat"]
                    if not (c["readOnly"] is True and c["storedSchemaVersion"] == 3
                            and c["supportedSchemaVersion"] == 1):
                        falhas.append(f"F2: C1 nao entrou em fail-closed sobre agregado v2: {c!r}")
                    if r["erro"] != "READ_ONLY_FUTURE_SCHEMA":
                        falhas.append(f"F2: ato no build C1 nao foi recusado: {r['erro']!r}")
                    if not (r["intacto"] and r["gravou"] and r["gravouTheme"] and r["discoIntacto"]):
                        falhas.append(f"F2: agregado v2 nao sobreviveu byte-intacto ao build C1: {r!r}")
                    if erros:
                        falhas.append(f"F2: pageerror no build C1 {erros}")
                    ctx.close()
                finally:
                    srv.shutdown()
        executar(falhas, "F2", caso_f2)

        # ---- S: round-trip de BACKUP (export -> import) com registros C2 -----
        def caso_s():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, f"S.alladin = {FIXTURE_B};")
            r = page.evaluate(f"""() => {{
                const esperado = JSON.stringify({FIXTURE_B});
                const blob = dgBuildBackupBlob(1, 'teste.json', new Date().toISOString());
                return blob.text().then(txt => {{
                    const envelope = JSON.parse(txt);
                    const importado = normalizeImportedState(envelope);
                    return {{ tipo: envelope.tipo, semSegredo: envelope.segredosIncluidos === false,
                             noEnvelope: JSON.stringify(envelope.state.alladin) === esperado,
                             aposImport: JSON.stringify(importado.alladin) === esperado,
                             versao: importado.alladin.schemaVersion,
                             owners: JSON.stringify(importado.alladin.assets[0].owners),
                             vivo: JSON.stringify(S.alladin) === esperado }};
                }});
            }}""")
            if r["tipo"] != "jpwealth_full_backup" or not r["semSegredo"]:
                falhas.append(f"S: envelope de backup fora do contrato: {r!r}")
            if not r["noEnvelope"]:
                falhas.append("S: exportacao alterou o agregado")
            if not r["aposImport"]:
                falhas.append("S: round-trip export->import NAO preservou o agregado byte a byte")
            if r["versao"] != 3:
                falhas.append(f"S: versao apos importacao divergiu: {r['versao']!r}")
            if r["owners"] != ('[{"name":"Joao","shareBp":5000,"isSelf":true},'
                               '{"name":"Maria","shareBp":5000}]'):
                falhas.append(f"S: owners nao sobreviveram ao backup: {r['owners']}")
            if not r["vivo"]:
                falhas.append("S: a exportacao/importacao tocou o estado VIVO")
            if erros:
                falhas.append(f"S: pageerror {erros}")
            ctx.close()
        executar(falhas, "S", caso_s)

        # ---- T: import fail-closed para conteiner `alladin` invalido ----------
        # ALD-03-H0 · D-2. `alladin` era a UNICA chave cuja forma nao era recusada
        # na porta: array, escalar ou null EXPLICITO atravessavam a validacao e so
        # eram normalizados depois, trocando o agregado pelo default — perda
        # silenciosa do cadastro, e amanha da historia economica. Chave AUSENTE
        # continua legitima (backup legado). Toda recusa tem de acontecer ANTES de
        # o estado ser tocado: mesmo estado vivo, nenhum save, nenhum changeLog.
        def caso_t():
            ctx, page, erros = boot(browser, url, PRONTO_NOVO, f"S.alladin = {FIXTURE_B};")
            r = page.evaluate("""() => {
                // O payload base e o BACKUP REAL do produto: assim a unica coisa
                // sob teste e a chave `alladin`, e nao um envelope sintetico que
                // tropecaria noutra validacao qualquer.
                const blob = dgBuildBackupBlob(1, 'teste.json', new Date().toISOString());
                return blob.text().then(txt => {
                  const envelope = JSON.parse(txt);
                  const base = JSON.stringify(envelope.state);
                  const comAlladin = (valor) => {
                    const st = JSON.parse(base);
                    if(valor === undefined) delete st.alladin; else st.alladin = valor;
                    return st;
                  };
                  const vivoAntes = JSON.stringify(S.alladin);
                  const logAntes  = JSON.stringify((S.dataGovernance||{}).changeLog||[]);
                  let saves = 0; const saveOrig = window.save;
                  window.save = function(){ saves++; return saveOrig.apply(this, arguments); };
                  const tentar = (st) => {
                    try { const out = normalizeImportedState(st);
                          return { aceitou:true, temAlladin: !!out.alladin && typeof out.alladin==='object' }; }
                    catch(e){ return { aceitou:false, msg:String(e.message||e) }; }
                  };
                  const casos = {
                    ausente: tentar(comAlladin(undefined)),
                    objeto:  tentar(comAlladin(JSON.parse(base).alladin)),
                    lista:   tentar(comAlladin([])),
                    escalar: tentar(comAlladin('x')),
                    nulo:    tentar(comAlladin(null)),
                  };
                  window.save = saveOrig;
                  return { casos, saves,
                           vivoIntacto: JSON.stringify(S.alladin) === vivoAntes,
                           logIntacto: JSON.stringify((S.dataGovernance||{}).changeLog||[]) === logAntes };
                });
            }""")
            c = r["casos"]
            if not c["ausente"]["aceitou"]:
                falhas.append(f"T: backup LEGADO sem alladin deveria ser aceito ({c['ausente']})")
            if not c["objeto"]["aceitou"] or not c["objeto"].get("temAlladin"):
                falhas.append(f"T: backup com alladin valido deveria ser aceito ({c['objeto']})")
            for chave in ("lista", "escalar", "nulo"):
                if c[chave]["aceitou"]:
                    falhas.append(f"T: alladin invalido ({chave}) ATRAVESSOU a validacao de import")
                elif "alladin" not in c[chave].get("msg", ""):
                    falhas.append(f"T: recusa de {chave} sem mensagem honesta ({c[chave].get('msg')!r})")
            if not r["vivoIntacto"]:
                falhas.append("T: uma recusa de import alterou o estado VIVO")
            if not r["logIntacto"]:
                falhas.append("T: uma recusa de import deixou entrada no changeLog")
            if r["saves"] != 0:
                falhas.append(f"T: a validacao de import chamou save() {r['saves']}x")
            if erros:
                falhas.append(f"T: pageerror {erros}")
            ctx.close()
        executar(falhas, "T", caso_t)

        # ---- U: migracao v2 -> v3 e o ledger (ALD-03 S1) --------------------
        # O bump nao transforma dado: ele so garante a colecao e fecha a escrita
        # para builds anteriores. Os tres regimes precisam ser provados, porque a
        # diferenca entre eles e a diferenca entre criar, preservar e DESTRUIR
        # historia economica. O caso do array preexistente e o que impede uma
        # migracao "que garante []" de esvaziar um ledger que ja existia.
        def caso_u():
            TX = ("{transactionId:'aldtx_legado', eventType:'DEPOSIT', status:'POSTED',"
                  " flowScope:'EXTERNAL', amount:12345, currency:'BRL',"
                  " effectiveAt:'2026-01-10', recordedAt:'2026-01-10T00:00:00.000Z',"
                  " cashAccountId:'aldc_legado'}")
            for rotulo, fixture, esperado in (
                ("ausente",
                 "{schemaVersion:2, reportingCurrency:'BRL', instruments:[], assets:[],"
                 " accounts:[], cashAccounts:[]}",
                 {"versao": 3, "tx": "[]"}),
                ("array preexistente",
                 "{schemaVersion:2, reportingCurrency:'BRL', instruments:[], assets:[],"
                 " accounts:[], cashAccounts:[], transactions:[" + TX + "]}",
                 {"versao": 3, "tx": "PRESERVADO"}),
                ("forma invalida",
                 "{schemaVersion:2, reportingCurrency:'BRL', instruments:[], assets:[],"
                 " accounts:[], cashAccounts:[], transactions:'lixo'}",
                 {"versao": 2, "tx": '"lixo"'}),
            ):
                ctx, page, erros = boot(browser, url, PRONTO_NOVO, f"S.alladin = {fixture};")
                r = page.evaluate("""() => ({
                    versao: S.alladin.schemaVersion,
                    tx: JSON.stringify(S.alladin.transactions),
                    bloqueio: JPWAlladin.writeBlockReason(),
                })""")
                if r["versao"] != esperado["versao"]:
                    falhas.append(f"U [{rotulo}]: versao apos migracao {r['versao']!r}, "
                                  f"esperado {esperado['versao']}")
                if esperado["tx"] == "PRESERVADO":
                    if "aldtx_legado" not in r["tx"] or "12345" not in r["tx"]:
                        falhas.append(f"U [{rotulo}]: a migracao DESTRUIU o ledger preexistente "
                                      f"({r['tx'][:80]})")
                elif r["tx"] != esperado["tx"]:
                    falhas.append(f"U [{rotulo}]: transactions {r['tx'][:60]!r}, "
                                  f"esperado {esperado['tx']}")
                if rotulo == "forma invalida" and r["versao"] == 3:
                    falhas.append("U: forma invalida foi carimbada como migrada — o fail-closed "
                                  "deixaria de ver o problema")
                if erros:
                    falhas.append(f"U [{rotulo}]: pageerror {erros}")
                ctx.close()
        executar(falhas, "U", caso_u)

        browser.close()
    server.shutdown()

    if falhas:
        print("alladin_foundation_test FALHOU")
        for f in falhas:
            print(" -", f)
        return 1
    print("alladin_foundation_test PASS (A-J + M,P,Q,R,F2,S: migracao v1->v2, round-trip completo, fail-closed, rollback pre-Alladin e no C1, reload, falha parcial, XSS/privacidade, backup)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
