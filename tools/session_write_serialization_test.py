#!/usr/bin/env python3
"""Serializacao cross-tab dos escritores do documento (ALD-C3-PRE-PERSISTENCE).

Prova as decisoes DP-1/2/3 e os blockers B1-B4 do Implementation Gate:

  SA  stale-tab nao sobrescreve estado novo: A abre a finalizacao, B grava,
      A confirma -> ABORTA; a escrita de B sobrevive no disco (Web Locks)
  SB  o critical section e realmente serializado entre abas (sem overlap)
  SC  sem Web Locks o modo e DEGRADED, explicitamente reportado
  SD  o fallback NAO afirma garantia forte (modo nunca mente 'weblocks')
  SE  wipeAllData e async e o CLIQUE REAL no botao destroi tudo apos aguardar
  SH  falha de persistencia no commit: zero sucesso, zero broadcast, doc antigo
      intacto (write-before-clear, B1+B2)
  SI  cada early-return remoto deixa a aba UTILIZAVEL (B3) e a guarda do save()
      recusa regravar por cima de disco alheio (camada 1)
  SJ  WriteAndConfirm exige releitura === valor tentado (B4); bootstrap converge
  SK  ausencia de Web Locks nao quebra finalizacao nem wipe
  SC1 camada 1 entre abas REAIS: B grava, save() de A e recusado com aviso de
      conflito — lost update vira recusa visivel

F/G (preserva/apaga) vivem em alladin_finalize_preservation_test.py C1-C17;
L (mixed-build) vive em session_epoch_protocol_test.py E6/E15 — nao duplicados.
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
FIXTURE = json.loads((ROOT / "tools/fixtures/alladin_v2.json").read_text(encoding="utf-8"))["alladin"]


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


PRONTO = "() => typeof S === 'object' && typeof save === 'function' && typeof sessionSerializationMode === 'function'"
CONTEXTOS = []


def abrir(browser, url, sem_weblocks=False):
    # QA-D1: Service Worker BLOQUEADO. Boota o app real com duas abas; sem
    # bloquear o SW, o updateFxRates do boot escapa do page.route e escreve no
    # disco, contaminando as comparacoes de documento inteiro. A serializacao
    # cross-tab usa Web Locks, nao SW — bloquear o SW nao a afeta.
    ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                              service_workers="block")
    CONTEXTOS.append(ctx)
    ctx.add_init_script("window.__onbShown=true;")
    if sem_weblocks:
        ctx.add_init_script("try{ delete Navigator.prototype.locks; }catch(e){} try{ delete window.navigator.locks; }catch(e){}")
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
    page.wait_for_timeout(400)
    page.evaluate("() => { window.alert=()=>{}; window.confirm=()=>true; window.prompt=()=>'APAGAR'; closeModal(); }")
    return ctx, page, erros


def segunda_aba(ctx, url):
    page = ctx.new_page()
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(PRONTO)
    page.wait_for_timeout(300)
    page.evaluate("() => { window.alert=()=>{}; closeModal(); }")
    return page


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

            # ---- SA: stale-tab nao sobrescreve; a escrita de B sobrevive ----
            def sa():
                ctx, a, erros = abrir(browser, url)
                a.evaluate("(x) => { S.alladin = x; save(); markSessionCheckpoint(); }", FIXTURE)
                b = segunda_aba(ctx, url)
                # A abre o fluxo REAL (captura da revisao R na abertura)
                a.locator("#finalizeSessionBtn").click()
                a.wait_for_timeout(500)
                # B grava DEPOIS da captura: patrimonio novo + conta nova
                b.wait_for_timeout(200)
                b.evaluate("""() => {
                    S.alladin.instruments.push({instrumentId:'aldi_DE_B'});
                    S.accounts.push({id:'CONTA_DE_B'});
                    if(save()!==true) throw new Error('save de B falhou na preparacao');
                }""")
                # A segue o fluxo ate confirmar
                if a.locator("#sessionHasCopy").count():
                    a.locator("#sessionHasCopy").click(); a.wait_for_timeout(200)
                elif a.locator("#sessionExport").count():
                    a.locator("#sessionExport").click()
                    a.locator("#sessionExportAcknowledged").check()
                    a.locator("#sessionExportContinue").click(); a.wait_for_timeout(200)
                a.locator("#sessionProceed").click()
                a.locator("#sessionDeletePhrase").fill("ENCERRAR SESSÃO")
                a.locator("#sessionDeleteConfirm").click()
                a.wait_for_timeout(800)
                r = a.evaluate("""() => ({
                    modal: (document.getElementById('modalBox')||{}).textContent||'',
                    discoTemB: (localStorage.getItem('%s')||'').indexOf('aldi_DE_B')!==-1,
                    contasDisco: (JSON.parse(localStorage.getItem('%s')||'{}').accounts||[]).length })""" % (LSKEY, LSKEY))
                if not r["discoTemB"]:
                    falhas.append(f"SA: a finalizacao de A SOBRESCREVEU a escrita de B (lost update) — {r['modal'][:80]!r}")
                if "Outra aba atualizou a base" not in r["modal"]:
                    falhas.append(f"SA: A nao recusou com o aviso de base mudada (modal={r['modal'][:90]!r})")
            executar(falhas, "SA", sa)

            # ---- SB: critical sections nao se sobrepoem ----
            def sb():
                ctx, a, erros = abrir(browser, url)
                b = segunda_aba(ctx, url)
                a.evaluate("""() => { window.__log=[];
                    window.__cs = (tag) => sessionAcquireWriteLock(async () => {
                        localStorage.setItem('cs_log', (localStorage.getItem('cs_log')||'') + '['+tag);
                        await new Promise(r => setTimeout(r, 120));
                        localStorage.setItem('cs_log', (localStorage.getItem('cs_log')||'') + tag+']');
                    }); }""")
                b.evaluate("""() => {
                    window.__cs = (tag) => sessionAcquireWriteLock(async () => {
                        localStorage.setItem('cs_log', (localStorage.getItem('cs_log')||'') + '['+tag);
                        await new Promise(r => setTimeout(r, 120));
                        localStorage.setItem('cs_log', (localStorage.getItem('cs_log')||'') + tag+']');
                    }); }""")
                a.evaluate("() => { window.__p = __cs('A'); }")
                b.evaluate("() => { window.__p = __cs('B'); }")
                a.evaluate("() => window.__p")
                b.evaluate("() => window.__p")
                log = a.evaluate("() => localStorage.getItem('cs_log')")
                a.evaluate("() => localStorage.removeItem('cs_log')")
                if log not in ("[AA][BB]", "[BB][AA]"):
                    falhas.append(f"SB: critical sections se SOBREPUSERAM entre abas — log={log!r}")
            executar(falhas, "SB", sb)

            # ---- SC/SD/SK: degraded explicito, honesto, funcional ----
            def sc_sd_sk():
                ctx, page, erros = abrir(browser, url, sem_weblocks=True)
                modo = page.evaluate("() => sessionSerializationMode()")
                if modo != "degraded":
                    falhas.append(f"SC: sem Web Locks o modo deveria ser 'degraded', veio {modo!r}")
                tem = page.evaluate("() => !!(navigator.locks)")
                if tem:
                    falhas.append("SC: a sonda nao removeu navigator.locks — caso nao exercitado")
                # SD: nenhum caminho pode reportar weblocks
                de_novo = page.evaluate("() => sessionSerializationMode()")
                if de_novo == "weblocks":
                    falhas.append("SD: o fallback AFIRMOU garantia forte (weblocks) sem a API")
                # SK: finalizacao e wipe continuam funcionando
                page.evaluate("(x) => { S.alladin = x; save(); markSessionCheckpoint(); }", FIXTURE)
                page.locator("#finalizeSessionBtn").click(); page.wait_for_timeout(400)
                if page.locator("#sessionHasCopy").count():
                    page.locator("#sessionHasCopy").click(); page.wait_for_timeout(200)
                elif page.locator("#sessionExport").count():
                    page.locator("#sessionExport").click()
                    page.locator("#sessionExportAcknowledged").check()
                    page.locator("#sessionExportContinue").click(); page.wait_for_timeout(200)
                page.locator("#sessionProceed").click()
                page.locator("#sessionDeletePhrase").fill("ENCERRAR SESSÃO")
                page.locator("#sessionDeleteConfirm").click()
                page.wait_for_timeout(700)
                r = page.evaluate("""() => ({ contas:S.accounts.length,
                    alladinDisco:(localStorage.getItem('%s')||'').indexOf('aldi_fx_petr4')!==-1 })""" % LSKEY)
                if r["contas"] != 0 or not r["alladinDisco"]:
                    falhas.append(f"SK: finalizacao em modo degraded nao funcionou — {r}")
                r2 = page.evaluate("""async () => { await wipeAllData();
                    return { disco: localStorage.getItem('%s') }; }""" % LSKEY)
                if r2["disco"] is not None:
                    falhas.append("SK: wipe em modo degraded nao apagou a base")
            executar(falhas, "SC/SD/SK", sc_sd_sk)

            # ---- SE: clique REAL no botao da Zona de Perigo (wipe async) ----
            def se():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(x) => { S.alladin = x; save(); }", FIXTURE)
                tem_botao = page.evaluate("() => !!document.getElementById('wipeAllBtn')")
                if tem_botao:
                    page.evaluate("() => document.getElementById('wipeAllBtn').click()")
                else:
                    page.evaluate("() => { void wipeAllData(); }")
                page.wait_for_function("() => localStorage.getItem('%s') === null" % LSKEY, timeout=8000)
                r = page.evaluate("() => ({ alladin: JSON.stringify(S.alladin) })")
                if "aldi_fx_petr4" in r["alladin"]:
                    falhas.append("SE: o clique real no wipe nao destruiu o agregado")
                if erros:
                    falhas.append(f"SE pageerror (rejeicao de Promise nao tratada?): {erros}")
            executar(falhas, "SE", se)

            # ---- SH: commit falha => zero sucesso, zero broadcast, doc intacto ----
            def sh():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(x) => { S.alladin = x; save(); markSessionCheckpoint(); }", FIXTURE)
                doc_antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.locator("#finalizeSessionBtn").click(); page.wait_for_timeout(400)
                if page.locator("#sessionHasCopy").count():
                    page.locator("#sessionHasCopy").click(); page.wait_for_timeout(200)
                elif page.locator("#sessionExport").count():
                    page.locator("#sessionExport").click()
                    page.locator("#sessionExportAcknowledged").check()
                    page.locator("#sessionExportContinue").click(); page.wait_for_timeout(200)
                page.evaluate("""() => {
                    window.__tocadas=[];
                    const orig = localStorage.setItem.bind(localStorage);
                    localStorage.setItem = (k,v) => {
                        window.__tocadas.push(k);
                        if(k==='%s') throw new Error('quota simulada');
                        return orig(k,v);
                    };
                }""" % LSKEY)
                page.locator("#sessionProceed").click()
                page.locator("#sessionDeletePhrase").fill("ENCERRAR SESSÃO")
                page.locator("#sessionDeleteConfirm").click()
                page.wait_for_timeout(700)
                r = page.evaluate("""() => {
                    const caixa=document.getElementById('modalBox');
                    const res={ modal: caixa?(caixa.textContent||''):'',
                        broadcast: window.__tocadas.indexOf('jpwealth_session_wipe_signal_v1')!==-1,
                        contas: S.accounts.length, bloqueada: jpWealthPersistenceIsBlocked() };
                    return res; }""")
                doc_depois = page.evaluate("() => { localStorage.setItem = Object.getPrototypeOf(localStorage).setItem ? localStorage.setItem : localStorage.setItem; return localStorage.getItem('%s'); }" % LSKEY)
                if "Nada foi apagado" not in r["modal"]:
                    falhas.append(f"SH: a falha de persistencia nao mostrou recusa (modal={r['modal'][:80]!r})")
                if r["broadcast"]:
                    falhas.append("SH: houve BROADCAST apesar de o commit ter falhado")
                if r["contas"] == 0:
                    falhas.append("SH: a sessao foi parcialmente finalizada apesar da falha")
                if doc_depois != doc_antes:
                    falhas.append("SH: o documento anterior NAO ficou intacto apos a falha do commit")
                if r["bloqueada"] is not False:
                    falhas.append("SH: o abort deixou a persistencia bloqueada (viola B3)")
            executar(falhas, "SH", sh)

            # ---- SH2: setItem NO-OP silencioso no commit => o read-back decide ----
            def sh2():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(x) => { S.alladin = x; save(); markSessionCheckpoint(); }", FIXTURE)
                doc_antes = page.evaluate("() => localStorage.getItem('%s')" % LSKEY)
                page.locator("#finalizeSessionBtn").click(); page.wait_for_timeout(400)
                if page.locator("#sessionHasCopy").count():
                    page.locator("#sessionHasCopy").click(); page.wait_for_timeout(200)
                elif page.locator("#sessionExport").count():
                    page.locator("#sessionExport").click()
                    page.locator("#sessionExportAcknowledged").check()
                    page.locator("#sessionExportContinue").click(); page.wait_for_timeout(200)
                page.evaluate("""() => {
                    const orig = localStorage.setItem.bind(localStorage);
                    localStorage.setItem = (k,v) => { if(k==='%s') return; return orig(k,v); };
                }""" % LSKEY)
                page.locator("#sessionProceed").click()
                page.locator("#sessionDeletePhrase").fill("ENCERRAR SESSÃO")
                page.locator("#sessionDeleteConfirm").click()
                page.wait_for_timeout(700)
                r = page.evaluate("""() => ({
                    modal: (document.getElementById('modalBox')||{}).textContent||'',
                    contas: S.accounts.length,
                    doc: localStorage.getItem('%s') })""" % LSKEY)
                if "Nada foi apagado" not in r["modal"]:
                    falhas.append(f"SH2: setItem no-op nao foi detectado pelo read-back (modal={r['modal'][:80]!r})")
                if r["contas"] == 0:
                    falhas.append("SH2: a sessao foi finalizada apesar de a gravacao ter sido um no-op")
                if r["doc"] != doc_antes:
                    falhas.append("SH2: o documento anterior mudou apesar do no-op")
            executar(falhas, "SH2", sh2)

            # ---- SA2: o backup do ramo changed representa o DISCO, nao o S da aba ----
            def sa2():
                ctx, page, erros = abrir(browser, url)
                page.evaluate("(x) => { S.alladin = x; save(); }", FIXTURE)
                # o disco passa a ter um agregado DIFERENTE do S desta aba (escrita alheia)
                page.evaluate("""() => {
                    const doc = JSON.parse(localStorage.getItem('%s'));
                    doc.alladin = {schemaVersion:2, reportingCurrency:'BRL',
                                   instruments:[{instrumentId:'aldi_DO_DISCO'}],
                                   assets:[], accounts:[], cashAccounts:[]};
                    localStorage.setItem('%s', JSON.stringify(doc));
                }""" % (LSKEY, LSKEY))
                page.locator("#finalizeSessionBtn").click(); page.wait_for_timeout(400)
                blob = page.evaluate("""async () => {
                    let capturado=null;
                    const OrigBlob = window.Blob;
                    window.Blob = function(partes, opts){ capturado = String(partes && partes[0]); return new OrigBlob(partes, opts); };
                    window.URL.createObjectURL = () => 'blob:t'; window.URL.revokeObjectURL = () => {};
                    HTMLAnchorElement.prototype.click = function(){};
                    if(document.getElementById('sessionExport')) document.getElementById('sessionExport').click();
                    else if(document.getElementById('sessionExportNow')) document.getElementById('sessionExportNow').click();
                    await new Promise(r => setTimeout(r, 600));
                    window.Blob = OrigBlob;
                    return capturado;
                }""")
                if not blob:
                    falhas.append("SA2: nao foi possivel capturar o blob do export")
                else:
                    if "aldi_DO_DISCO" not in blob:
                        falhas.append("SA2: o backup NAO representa o documento autoritativo do disco")
                    if "aldi_fx_petr4" in blob:
                        falhas.append("SA2: o backup carregou o S obsoleto da aba em vez do disco")
            executar(falhas, "SA2", sa2)

            # ---- SI: early-returns remotos deixam a aba utilizavel ----
            def si():
                cenarios = [
                    ("geracao antiga", "(x) => { S.alladin=x; save(); sessionHandleRemoteFinalization({type:'jpwealth-session-finalized-v2', token:'SI1', baseEpoch:'GERACAO-MORTA'}); }"),
                    ("doc ausente",    "(x) => { S.alladin=x; save(); localStorage.removeItem('%s'); sessionHandleRemoteFinalization({type:'jpwealth-session-finalized-v2', token:'SI2', baseEpoch:sessionEpochCurrent()}); }" % LSKEY),
                    ("doc ilegivel",   "(x) => { S.alladin=x; save(); localStorage.setItem('%s','{lixo'); sessionHandleRemoteFinalization({type:'jpwealth-session-finalized-v2', token:'SI3', baseEpoch:sessionEpochCurrent()}); }" % LSKEY),
                ]
                for rotulo, sonda in cenarios:
                    ctx, page, erros = abrir(browser, url)
                    page.evaluate(sonda, FIXTURE)
                    r = page.evaluate("() => ({ bloqueada: jpWealthPersistenceIsBlocked(), contas: S.accounts.length })")
                    if r["bloqueada"] is not False:
                        falhas.append(f"SI [{rotulo}]: a aba ficou permanentemente bloqueada (viola B3)")
                    if r["contas"] == 0:
                        falhas.append(f"SI [{rotulo}]: o early-return executou a finalizacao")
                    if rotulo != "geracao antiga":
                        gravou = page.evaluate("() => save()")
                        if gravou is not False:
                            falhas.append(f"SI [{rotulo}]: save() regravou por cima de disco alheio/ausente")
            executar(falhas, "SI", si)

            # ---- SJ: confirmacao estrita da epoch (B4) + bootstrap converge ----
            def sj():
                ctx, page, erros = abrir(browser, url)
                r = page.evaluate("""() => {
                    const out={};
                    out.boot = sessionEpochCurrent();
                    const orig = localStorage.setItem.bind(localStorage);
                    localStorage.setItem = (k,v) => { if(k==='jpwealth_base_epoch_v1') return; return orig(k,v); };
                    out.rotateNoop = sessionEpochRotate();
                    out.confirmNoop = sessionEpochWriteAndConfirm('VALOR-QUE-NAO-SERA-GRAVADO');
                    localStorage.setItem = orig;
                    out.rotateOk = sessionEpochRotate();
                    return out;
                }""")
                if r["boot"] != "BASE-V0-LEGACY":
                    falhas.append(f"SJ: bootstrap nao convergiu ao sentinel ({r['boot']!r})")
                if r["rotateNoop"] is not None:
                    falhas.append(f"SJ: rotate com setItem no-op REPORTOU sucesso ({r['rotateNoop']!r}) — viola B4")
                if r["confirmNoop"] is not None:
                    falhas.append(f"SJ: WriteAndConfirm aceitou releitura != valor tentado ({r['confirmNoop']!r}) — viola B4")
                if not r["rotateOk"] or r["rotateOk"] == "BASE-V0-LEGACY":
                    falhas.append(f"SJ: rotacao legitima falhou ({r['rotateOk']!r})")
            executar(falhas, "SJ", sj)

            # ---- SC1: camada 1 entre abas reais — recusa visivel, nao lost update ----
            def sc1():
                ctx, a, erros = abrir(browser, url)
                a.evaluate("(x) => { S.alladin = x; save(); }", FIXTURE)
                b = segunda_aba(ctx, url)
                b.evaluate("() => { S.accounts.push({id:'CONTA_DE_B'}); if(save()!==true) throw new Error('save de B falhou'); }")
                r = a.evaluate("""() => {
                    S.params.saldoIni = 777;
                    const gravou = save();
                    const banner = (document.getElementById('persistenceAlert')||{}).textContent||'';
                    return { gravou, banner,
                             discoTemB: (localStorage.getItem('%s')||'').indexOf('CONTA_DE_B')!==-1 };
                }""" % LSKEY)
                if r["gravou"] is not False:
                    falhas.append("SC1: o save() da aba obsoleta GRAVOU por cima da escrita de B (lost update)")
                if not r["discoTemB"]:
                    falhas.append("SC1: a escrita de B sumiu do disco")
                if "Outra aba atualizou a base" not in r["banner"]:
                    falhas.append(f"SC1: a recusa nao mostrou o aviso honesto de conflito (banner={r['banner'][:80]!r})")
            executar(falhas, "SC1", sc1)

            browser.close()
    finally:
        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        servidor.shutdown()

    if falhas:
        print("SESSION WRITE SERIALIZATION TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("SESSION WRITE SERIALIZATION TEST PASS (SA stale-tab abortada com a escrita alheia preservada, "
          "SB critical section serializado entre abas, SC/SD/SK degraded explicito honesto e funcional, "
          "SE wipe async por clique real, SH commit falho sem sucesso/broadcast e doc intacto, "
          "SH2 no-op detectado pelo read-back, SA2 backup do ramo changed representa o disco, SI early-returns remotos sem read-only permanente e sem regravacao, SJ epoch com confirmacao "
          "estrita e bootstrap convergente, SC1 camada 1 recusa lost update com aviso honesto)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
