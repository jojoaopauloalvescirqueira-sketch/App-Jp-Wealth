#!/usr/bin/env python3
"""Causalidade entre gerações da base (ALD-C3-PRE-EPOCH).

O defeito que este protocolo fecha, medido antes dele: os dois transportes
(BroadcastChannel e evento `storage`) entregam a MESMA mensagem duas vezes, e o
dedup era um unico `sessionLastWipeToken` compartilhado pelos tres tipos de
evento. Um evento de outro tipo sobrescrevia o token e LIBERAVA o anterior para
reprocessamento. Sequencia F -> W -> reentrega de F executava a finalizacao
DEPOIS da limpeza total, regravando patrimonio numa base que o operador acabara
de apagar.

Relogio nao resolve: o token carrega `Date.now()` em base36, mas wall-clock nao e
monotonico e empata no mesmo milissegundo. Geracao resolve, porque e causal.

    baseEpoch      -> SEGURANCA: mensagem de geracao antiga nunca atua
    seenMessages   -> DEDUPLICACAO operacional dos dois transportes

Assimetria deliberada de versionamento:

    finalize  -> tipo NOVO (jpwealth-session-finalized-v2)
                 NAO atravessa builds: o handler legado zerava S.alladin
    wipe      -> tipo INALTERADO
    import    -> tipo INALTERADO
                 DEVEM atravessar: ignora-los deixaria uma aba operando sobre
                 uma base que ja nao existe

E1..E16. E6 e E15 servem o build BASELINE por `git archive`.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import io
import json
import os
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LSKEY = "jpwealth_v9_state"
EPOCH_KEY = "jpwealth_base_epoch_v1"
SENTINEL = "BASE-V0-LEGACY"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve(directory=None):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    if directory is None:
        server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    else:
        class Rooted(QuietHandler):
            def __init__(self, *a, **kw):
                super().__init__(*a, directory=str(directory), **kw)
        server = ThreadingHTTPServer(("127.0.0.1", port), Rooted)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


PRONTO = "() => typeof S === 'object' && typeof save === 'function'"
CONTEXTOS = []


def abrir(browser, url):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
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
    page.wait_for_timeout(400)
    page.evaluate("() => { window.alert=()=>{}; window.confirm=()=>true; window.prompt=()=>'APAGAR'; closeModal(); }")
    return ctx, page, erros


SEMEAR = """() => {
    if(typeof resumeJPWealthPersistence==='function') resumeJPWealthPersistence();
    S.accounts=[{id:'MARCADOR'}];
    S.alladin={schemaVersion:2, reportingCurrency:'BRL', instruments:[{instrumentId:'aldi_marcador'}],
               assets:[], accounts:[], cashAccounts:[]};
    save();
    return { contas:S.accounts.length, epoch: localStorage.getItem('%s') };
}""" % EPOCH_KEY

ESTADO = """() => ({
    contas: S.accounts.length,
    instrumentos: (S.alladin && S.alladin.instruments) ? S.alladin.instruments.length : -1,
    bloqueada: jpWealthPersistenceIsBlocked(),
    epoch: localStorage.getItem('%s'),
    discoTemPatrimonio: (localStorage.getItem('%s')||'').indexOf('aldi_marcador') !== -1,
    descartesLegado: sessionLegacyProtocolDiscards,
})""" % (EPOCH_KEY, LSKEY)


def executar(falhas, nome, fn):
    try:
        fn()
    except Exception as exc:
        falhas.append(f"{nome}: excecao na sonda — {exc}")


def main() -> int:
    servidor, url = serve()
    falhas: list[str] = []
    baseline_dir = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            # ---- E1: F(G1) -> W(G2) -> replay de F(G1) e REJEITADO ----
            def e1():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    const G1 = sessionEpochCurrent();
                    const F  = {type:'jpwealth-session-finalized-v2', token:'TOK_F', baseEpoch:G1};
                    // limpeza total real: rotaciona a geracao para G2
                    wipeAllData();
                    const G2 = sessionEpochCurrent();
                    // a aba volta a ter estado; o replay de F nao pode reintroduzir patrimonio
                    resumeJPWealthPersistence();
                    S.accounts=[{id:'POS_WIPE'}]; save();
                    sessionHandleRemoteMessage(F);
                    return { G1, G2, mudou: G1!==G2, contas:S.accounts.length,
                             discoTemPatrimonio:(localStorage.getItem('%s')||'').indexOf('aldi_marcador')!==-1 };
                }""" % LSKEY)
                if not r["mudou"]:
                    falhas.append("E1: wipeAllData nao rotacionou a geracao da base")
                if r["contas"] == 0 or r["discoTemPatrimonio"]:
                    falhas.append(f"E1: o replay de F(G1) ATUOU depois do wipe — {r}")
                if erros:
                    falhas.append(f"E1 pageerror: {erros}")
            executar(falhas, "E1", e1)

            # ---- E2: W(G2) e SO ENTAO a primeira entrega de F(G1) ----
            def e2():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    const G1 = sessionEpochCurrent();
                    const F  = {type:'jpwealth-session-finalized-v2', token:'TOK_F2', baseEpoch:G1};
                    wipeAllData();
                    resumeJPWealthPersistence();
                    S.accounts=[{id:'POS_WIPE'}]; save();
                    sessionHandleRemoteMessage(F);   // PRIMEIRA entrega, ja atrasada
                    return { contas:S.accounts.length };
                }""")
                if r["contas"] == 0:
                    falhas.append("E2: a PRIMEIRA entrega atrasada de F(G1) atuou depois do wipe")
                if erros:
                    falhas.append(f"E2 pageerror: {erros}")
            executar(falhas, "E2", e2)

            # ---- E3: CONTROLE — F(G2) legitimo pos-wipe e ACEITO ----
            def e3():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    wipeAllData();
                    resumeJPWealthPersistence();
                    S.accounts=[{id:'POS_WIPE'}];
                    S.alladin={schemaVersion:2, reportingCurrency:'BRL',
                               instruments:[{instrumentId:'aldi_marcador'}], assets:[], accounts:[], cashAccounts:[]};
                    save();
                    const G2 = sessionEpochCurrent();
                    sessionHandleRemoteMessage({type:'jpwealth-session-finalized-v2', token:'TOK_OK', baseEpoch:G2});
                    return { contas:S.accounts.length,
                             instrumentos:(S.alladin&&S.alladin.instruments)?S.alladin.instruments.length:-1 };
                }""")
                if r["contas"] != 0:
                    falhas.append(f"E3 CONTROLE: a guarda recusa TUDO — finalize legitimo nao executou ({r})")
                if r["instrumentos"] != 1:
                    falhas.append(f"E3: o finalize legitimo nao preservou o patrimonio ({r})")
                if erros:
                    falhas.append(f"E3 pageerror: {erros}")
            executar(falhas, "E3", e3)

            # ---- E4: F(G2) duplicado pelos DOIS transportes = efeito unico ----
            def e4():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    let execucoes=0;
                    const real = sessionHandleRemoteFinalization;
                    window.sessionHandleRemoteFinalization = (m) => { execucoes++; return real(m); };
                    const G = sessionEpochCurrent();
                    const F = {type:'jpwealth-session-finalized-v2', token:'TOK_DUP', baseEpoch:G};
                    sessionHandleRemoteMessage(F);   // BroadcastChannel
                    sessionHandleRemoteMessage(F);   // fallback por storage, mesmo token
                    return { execucoes, contas:S.accounts.length };
                }""")
                # o roteador chama o handler nas duas vezes; a dedup age DENTRO dele
                if r["contas"] != 0:
                    falhas.append("E4: o finalize legitimo nao executou nenhuma vez")
                if erros:
                    falhas.append(f"E4 pageerror: {erros}")
                r2 = page.evaluate("""() => {
                    // efeito unico: a segunda entrega nao pode reexecutar o corpo do handler
                    resumeJPWealthPersistence();
                    S.accounts=[{id:'DEPOIS'}]; save();
                    const G = sessionEpochCurrent();
                    sessionHandleRemoteMessage({type:'jpwealth-session-finalized-v2', token:'TOK_DUP', baseEpoch:G});
                    return { contas:S.accounts.length };
                }""")
                if r2["contas"] == 0:
                    falhas.append("E4: a mensagem JA PROCESSADA foi reexecutada (dedup type:token falhou)")
            executar(falhas, "E4", e4)

            # ---- E5: import G2->G3 invalida F(G2) ----
            def e5():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    const G2 = sessionEpochCurrent();
                    const F  = {type:'jpwealth-session-finalized-v2', token:'TOK_IMP', baseEpoch:G2};
                    // importacao integral rotaciona: G2 -> G3
                    const G3 = sessionEpochRotate();
                    S.accounts=[{id:'IMPORTADO'}]; save();
                    sessionHandleRemoteMessage(F);
                    return { mudou:G2!==G3, contas:S.accounts.length };
                }""")
                if not r["mudou"]:
                    falhas.append("E5: a rotacao nao mudou a geracao")
                if r["contas"] == 0:
                    falhas.append("E5: F(G2) atuou depois da importacao ter rotacionado para G3")
                if erros:
                    falhas.append(f"E5 pageerror: {erros}")
            executar(falhas, "E5", e5)

            # ---- E5b: a importacao REAL rotaciona a geracao ----
            def e5b():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                antes = page.evaluate("() => sessionEpochCurrent()")
                page.evaluate("""() => {
                    const doc = {tipo:'jpwealth_full_backup', versao:'V9.1', state: structuredClone(S)};
                    const f = new File([JSON.stringify(doc)], 'backup.json', {type:'application/json'});
                    importFullBackupFile(f);
                }""")
                page.wait_for_timeout(1200)
                depois = page.evaluate("() => sessionEpochCurrent()")
                if depois == antes:
                    falhas.append(f"E5b: a importacao REAL nao rotacionou a geracao ({antes!r})")
                if depois == SENTINEL:
                    falhas.append("E5b: a importacao deixou o SENTINEL em vez de uma geracao rotacionada")
                r = page.evaluate("""(g) => {
                    resumeJPWealthPersistence();
                    S.accounts=[{id:'POS_IMPORT'}]; save();
                    sessionHandleRemoteMessage({type:'jpwealth-session-finalized-v2', token:'TOK_PRE_IMP', baseEpoch:g});
                    return { contas:S.accounts.length };
                }""", antes)
                if r["contas"] == 0:
                    falhas.append("E5b: finalize da geracao anterior atuou depois da importacao real")
                if erros:
                    falhas.append(f"E5b pageerror: {erros}")
            executar(falhas, "E5b", e5b)

            # ---- E16: EMPATE/RETROCESSO DE RELOGIO — so a geracao distingue ----
            def e16():
                # Um mecanismo baseado em Date.now() aceitaria este F, porque o carimbo
                # dele NAO e anterior ao do wipe. A geracao rejeita, porque a base mudou.
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    const G1 = sessionEpochCurrent();
                    // token com carimbo DEPOIS do wipe, mas pertencente a geracao ANTERIOR
                    const futuro = (Date.now()+600000).toString(36)+'_relogioadiantado';
                    const F = {type:'jpwealth-session-finalized-v2', token:futuro, baseEpoch:G1};
                    wipeAllData();
                    resumeJPWealthPersistence();
                    S.accounts=[{id:'POS_WIPE'}]; save();
                    sessionHandleRemoteMessage(F);
                    return { contas:S.accounts.length, G1, G2:sessionEpochCurrent() };
                }""")
                if r["contas"] == 0:
                    falhas.append("E16: F de geracao anterior foi ACEITO por ter carimbo mais novo — "
                                  "a ordem esta vindo do relogio, nao da causalidade")
                if erros:
                    falhas.append(f"E16 pageerror: {erros}")
            executar(falhas, "E16", e16)

            # ---- E7: OLD finalize v1 -> receptor NOVO = descarte EXPLICITO ----
            def e7():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    const antes = sessionLegacyProtocolDiscards;
                    sessionHandleRemoteMessage({type:'jpwealth-session-finalized', token:'TOK_V1'});
                    return { contas:S.accounts.length,
                             instrumentos:(S.alladin&&S.alladin.instruments)?S.alladin.instruments.length:-1,
                             descartou: sessionLegacyProtocolDiscards - antes,
                             bloqueada: jpWealthPersistenceIsBlocked(),
                             disco: localStorage.getItem('%s')!==null };
                }""" % LSKEY)
                if r["contas"] == 0 or r["instrumentos"] != 1:
                    falhas.append(f"E7: finalize LEGADO executou no receptor novo — {r}")
                if r["descartou"] != 1:
                    falhas.append(f"E7: o descarte do protocolo legado nao foi EXPLICITO nem observavel ({r})")
                if r["bloqueada"] or not r["disco"]:
                    falhas.append(f"E7: o descarte executou parte do handler v2 ({r})")
                if erros:
                    falhas.append(f"E7 pageerror: {erros}")
            executar(falhas, "E7", e7)

            # ---- E8: geracao muda no meio da leitura => snapshot incoerente nunca usado ----
            def e8():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    let n=0;
                    window.sessionEpochCurrent = () => 'G' + (++n);   // muda a cada leitura
                    const leitura = sessionReadStable({ausenteAborta:false});
                    return { ok: leitura.ok, erro: (leitura.erro && leitura.erro.message) || '', leituras: n };
                }""")
                if r["ok"] is not False:
                    falhas.append("E8: leitura instavel foi ACEITA — snapshot pode pertencer a outra geracao")
                if r["leituras"] < 4:
                    falhas.append(f"E8: o seqlock nao releu a geracao apos o documento ({r})")
                if erros:
                    falhas.append(f"E8 pageerror: {erros}")
            executar(falhas, "E8", e8)

            # ---- E9: falha de geracao no fluxo LOCAL = zero efeito ----
            def e9():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                r = page.evaluate("""() => {
                    const tocadas=[]; const origSet = localStorage.setItem.bind(localStorage);
                    localStorage.setItem = (k,v) => { tocadas.push(k); return origSet(k,v); };
                    const origGet = localStorage.getItem.bind(localStorage);
                    localStorage.getItem = (k) => { if(k==='%s') throw new Error('storage indisponivel'); return origGet(k); };
                    window.__jpwealthDownload=null;
                    HTMLAnchorElement.prototype.click = function(){ window.__jpwealthDownload={f:this.download}; };
                    openFinalizeSessionFlow();
                    localStorage.getItem = origGet; localStorage.setItem = origSet;
                    const caixa=document.getElementById('modalBox');
                    return { tocadas, modal: caixa?(caixa.textContent||''):'',
                             exportou: !!window.__jpwealthDownload,
                             temExport: !!document.getElementById('sessionExport'),
                             temProceed: !!document.getElementById('sessionProceed'),
                             contas:S.accounts.length, bloqueada: jpWealthPersistenceIsBlocked(),
                             disco: localStorage.getItem('%s')!==null };
                }""" % (EPOCH_KEY, LSKEY))
                if r["exportou"]:
                    falhas.append("E9: houve EXPORTACAO apesar de a geracao nao ter sido estabelecida")
                if r["temExport"] or r["temProceed"]:
                    falhas.append("E9: o fluxo AVANCOU para export/confirmacao sem geracao confiavel")
                if "jpwealth_session_wipe_signal_v1" in r["tocadas"]:
                    falhas.append("E9: houve BROADCAST apesar da falha de geracao")
                if r["contas"] == 0 or not r["disco"]:
                    falhas.append(f"E9: houve CLEAR/persistencia destrutiva apesar da falha ({r})")
                if "Nada foi apagado" not in r["modal"]:
                    falhas.append(f"E9: nao houve recusa explicita ao operador ({r['modal'][:80]!r})")
                if erros:
                    falhas.append(f"E9 pageerror: {erros}")
            executar(falhas, "E9", e9)

            # ---- E10: bootstrap simultaneo em duas abas converge ao sentinel ----
            def e10():
                ctx, p1, er1 = abrir(browser, url)
                p2 = ctx.new_page()
                p2.route("**/*", lambda r: r.continue_() if "127.0.0.1" in r.request.url
                         else r.fulfill(status=200, content_type="application/json", body="{}"))
                p2.goto(url, wait_until="load"); p2.wait_for_function(PRONTO); p2.wait_for_timeout(300)
                p1.evaluate("() => localStorage.removeItem('%s')" % EPOCH_KEY)
                a = p1.evaluate("() => sessionEpochCurrent()")
                b = p2.evaluate("() => sessionEpochCurrent()")
                if a != SENTINEL or b != SENTINEL:
                    falhas.append(f"E10: bootstrap nao convergiu ao sentinel deterministico (aba1={a!r}, aba2={b!r})")
                if a != b:
                    falhas.append(f"E10: as duas abas se julgam de geracoes diferentes ({a!r} != {b!r})")
            executar(falhas, "E10", e10)

            # ---- E11/E12: wipe/import LEGADOS (sem epoch) sao PROCESSADOS e estabelecem geracao ----
            def e11_e12():
                for rotulo, tipo in (("E11 wipe legado", "jpwealth-base-wiped"),
                                     ("E12 import legado", "jpwealth-base-imported")):
                    ctx, page, erros = abrir(browser, url)
                    page.evaluate(SEMEAR)
                    r = page.evaluate("""(tipo) => {
                        const G1 = sessionEpochCurrent();
                        const F  = {type:'jpwealth-session-finalized-v2', token:'TOK_ANTES', baseEpoch:G1};
                        sessionHandleRemoteMessage({type:tipo, token:'TOK_LEGADO'});   // SEM baseEpoch
                        const G2 = sessionEpochCurrent();
                        resumeJPWealthPersistence();
                        S.accounts=[{id:'DEPOIS'}]; save();
                        sessionHandleRemoteMessage(F);   // finalize da geracao ANTERIOR
                        return { G1, G2, mudou:G1!==G2, contas:S.accounts.length };
                    }""", tipo)
                    if not r["mudou"] or not r["G2"]:
                        falhas.append(f"{rotulo}: o receptor novo nao estabeleceu geracao nova ({r})")
                    if r["G2"] == SENTINEL:
                        falhas.append(f"{rotulo}: a geracao nova e o SENTINEL, nao uma rotacao ({r})")
                    if r["contas"] == 0:
                        falhas.append(f"{rotulo}: finalize da geracao anterior ATUOU depois do evento legado ({r})")
                    if erros:
                        falhas.append(f"{rotulo} pageerror: {erros}")
            executar(falhas, "E11/E12", e11_e12)

            # ---- E13: falha ao estabelecer geracao apos evento legado = base obsoleta NAO volta ----
            def e13():
                for rotulo, tipo in (("E13 wipe", "jpwealth-base-wiped"), ("E13 import", "jpwealth-base-imported")):
                    ctx, page, erros = abrir(browser, url)
                    page.evaluate(SEMEAR)
                    r = page.evaluate("""(tipo) => {
                        window.sessionEpochRotate = () => null;      // rotacao impossivel
                        sessionHandleRemoteMessage({type:tipo, token:'TOK_LEG_FALHA'});
                        const podeGravar = save();
                        return { bloqueada: jpWealthPersistenceIsBlocked(), podeGravar,
                                 discoTemPatrimonio:(localStorage.getItem('%s')||'').indexOf('aldi_marcador')!==-1 };
                    }""" % LSKEY, tipo)
                    if r["bloqueada"] is not True or r["podeGravar"] is True:
                        falhas.append(f"{rotulo}: sem geracao estabelecida a aba continuou GRAVAVEL ({r})")
                    if erros:
                        falhas.append(f"{rotulo} pageerror: {erros}")
            executar(falhas, "E13", e13)

            # ---- E14: a geracao NAO entra no backup e NAO e restaurada por import ----
            def e14():
                ctx, page, erros = abrir(browser, url)
                page.evaluate(SEMEAR)
                conteudo = page.evaluate("""async () => {
                    let capturado=null;
                    const origBlob = window.Blob;
                    window.Blob = function(partes, opts){ capturado = String(partes && partes[0]); return new origBlob(partes, opts); };
                    window.URL.createObjectURL = () => 'blob:teste';
                    window.URL.revokeObjectURL = () => {};
                    HTMLAnchorElement.prototype.click = function(){};
                    await exportFullBackup({quiet:true});
                    window.Blob = origBlob;
                    return capturado;
                }""")
                if conteudo is None:
                    falhas.append("E14: nao foi possivel capturar o conteudo do backup")
                else:
                    if EPOCH_KEY in conteudo or SENTINEL in conteudo:
                        falhas.append("E14: a chave de geracao VAZOU para dentro do backup")
                if erros:
                    falhas.append(f"E14 pageerror: {erros}")
            executar(falhas, "E14", e14)

            # ---- E6 e E15: mixed-build contra o BASELINE servido por git archive ----
            def e6_e15():
                nonlocal baseline_dir
                sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
                tar_bytes = subprocess.run(["git", "archive", sha], cwd=ROOT,
                                           capture_output=True).stdout
                baseline_dir = tempfile.mkdtemp(prefix="jpwealth-baseline-")
                with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
                    tf.extractall(baseline_dir)
                srv_old, url_old = serve(baseline_dir)
                try:
                    # E6 captura a mensagem que o build NOVO REALMENTE emite — fabricar
                    # a mensagem a mao tornaria o caso cego a uma regressao do tipo no
                    # emissor, que e exatamente o que separa os dois protocolos.
                    ctx_novo, page_novo, err_novo = abrir(browser, url)
                    page_novo.evaluate(SEMEAR)
                    emitida = page_novo.evaluate("""() => {
                        let capturada=null;
                        const orig = localStorage.setItem.bind(localStorage);
                        localStorage.setItem = (k,v) => {
                            if(k==='jpwealth_session_wipe_signal_v1' && !capturada) capturada=v;
                            return orig(k,v);
                        };
                        openFinalizeSessionFlow();
                        finalizeJPWealthSession();
                        localStorage.setItem = orig;
                        return capturada;
                    }""")
                    if not emitida:
                        falhas.append("E6: nao foi possivel capturar a mensagem emitida pelo build novo")
                        return
                    if err_novo:
                        falhas.append(f"E6 pageerror (build novo): {err_novo}")

                    ctx, page, erros = abrir(browser, url_old)
                    page.evaluate(SEMEAR)
                    # E6: a mensagem REAL do build NOVO chega no build ANTIGO
                    r6 = page.evaluate("""(bruta) => {
                        sessionHandleRemoteMessage(JSON.parse(bruta));
                        return { tipo: JSON.parse(bruta).type, contas:S.accounts.length,
                                 instrumentos:(S.alladin&&S.alladin.instruments)?S.alladin.instruments.length:-1 };
                    }""", emitida)
                    if r6["contas"] == 0 or r6["instrumentos"] != 1:
                        falhas.append(f"E6: o build ANTIGO executou a finalizacao emitida pelo build novo "
                                      f"e destruiu estado — tipo emitido={r6['tipo']!r}, {r6}")
                    # E15: wipe/import do build NOVO (com epoch) no build ANTIGO ainda executam
                    r15w = page.evaluate("""() => {
                        sessionHandleRemoteMessage({type:'jpwealth-base-wiped', token:'TOK_W15', baseEpoch:'G-NOVA'});
                        return { contas:S.accounts.length, disco: localStorage.getItem('%s') };
                    }""" % LSKEY)
                    if r15w["disco"] is not None:
                        falhas.append(f"E15 wipe: o build ANTIGO nao executou a limpeza vinda do build novo — {r15w}")
                    if erros:
                        falhas.append(f"E6/E15 pageerror: {erros}")
                finally:
                    srv_old.shutdown()
            executar(falhas, "E6/E15", e6_e15)

            browser.close()
    finally:
        for ctx in CONTEXTOS:
            try:
                ctx.close()
            except Exception:
                pass
        servidor.shutdown()

    if falhas:
        print("SESSION EPOCH PROTOCOL TEST FALHOU")
        for f in falhas:
            print("  - " + f)
        return 1
    print("SESSION EPOCH PROTOCOL TEST PASS (E1-E16: replay pos-wipe rejeitado, entrega tardia rejeitada, "
          "finalize legitimo aceito, efeito unico nos dois transportes, import invalida geracao anterior, "
          "mixed-build nos dois sentidos, seqlock, fail-closed local, bootstrap deterministico convergente, "
          "wipe/import legados estabelecem geracao, falha de geracao nao regrava base obsoleta, "
          "geracao fora do backup, importacao real rotaciona, empate/retrocesso de relogio nao engana)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
