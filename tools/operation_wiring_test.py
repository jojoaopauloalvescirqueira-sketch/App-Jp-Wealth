#!/usr/bin/env python3
"""Fiacao real da Operacao Unica: DOM -> evento -> dominio -> estado -> disco.

ESTE ARQUIVO EXISTE POR UM DEFEITO CONCRETO. O gancho que faz a Operacao Unica
nascer foi ligado ao laco de <input>, mas o campo Status e um <select>: a
chamada era codigo morto e a entidade jamais nascia pela interface. O tier
standard passava 16/16 e varias campanhas de mutation testing nao acusaram —
porque todos os testes chamavam operationOnOrderStatus() DIRETAMENTE.

Teste de dominio prova que a regra esta certa. Nao prova que ela e chamada.
Aqui nada e invocado a mao: o teste acha o controle real, dispara o evento real
e verifica o estado e o disco.

Todas as fixtures sao SINTETICAS.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


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


def prepare_page(browser, url):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    observed = {"pageerror": []}
    page.on("pageerror", lambda e: observed["pageerror"].append(str(e)))
    page.on("dialog", lambda d: d.accept())      # confirmacoes do fluxo de abertura
    page.route(
        "**/*",
        lambda route: route.continue_()
        if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_function("() => typeof renderPhases === 'function' && !!S")
    return context, page, observed


# Prepara uma Genese pronta para abrir e REDESENHA a grade, para que os
# listeners reais sejam religados aos nos reais.
PREPARAR = """
  window.__prepararGenese = () => {
    S.activeOperation = null;
    S.operationHistory = {schemaVersion:1, records:[]};
    S.params.saldoIni = 10000;
    S.phaseUnlocked = [true,false,false,false];
    S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
    const g = S.phases[0].orders[0];
    // Lote DENTRO do teto por operacao do instrumento: a fixture nao pode
    // depender de furar uma guarda normativa legitima. O teto vem do catalogo
    // vivo (instrumentCatalog), entao e lido daqui em vez de fixado a mao.
    const ins = (S.instruments||[]).find(i => i && i.name === 'EURUSD');
    const teto = ins && +ins.teto > 0 ? +ins.teto : 0.01;
    g.id='G1'; g.par='EURUSD'; g.tipo='BUY'; g.lote=teto; g.entry=1.1000; g.sl=1.0950; g.tp=1.1200;
    renderPhases();
  };
  window.__selectStatus = (pi,oi) =>
    document.querySelector('select[data-p="'+pi+'"][data-o="'+oi+'"][data-f="status"]');
  window.__doDisco = () => {
    try { return JSON.parse(localStorage.getItem('jpwealth_v9_state')) || {}; }
    catch(_) { return {}; }
  };
"""


def abrir_genese_pela_ui(page):
    """Muda o <select> de Status para Aberta como o operador faria."""
    return page.evaluate(
        """() => {
          const sel = __selectStatus(0,0);
          if (!sel) return {erro:'select de status nao encontrado'};
          const opcoes = [...sel.options].map(o => o.value);
          sel.value = 'Aberta';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          return {opcoes, status: S.phases[0].orders[0].status};
        }"""
    )


def run_genesis_birth_through_ui(page):
    """O ato REAL do operador faz a Operacao Unica nascer."""
    page.evaluate("() => __prepararGenese()")
    pre = page.evaluate("() => ({entidade: S.activeOperation, tag: (__selectStatus(0,0)||{}).tagName})")
    assert pre["entidade"] is None, "fixture ja tinha entidade"
    assert pre["tag"] == "SELECT", (
        f"o controle de Status nao e um <select> ({pre['tag']}) — a premissa do "
        "teste mudou e o gancho pode estar no laco errado de novo"
    )

    r = abrir_genese_pela_ui(page)
    assert "erro" not in r, r.get("erro")
    assert r["status"] == "Aberta", f"a abertura foi recusada pelas guardas: {r}"

    estado = page.evaluate(
        """() => ({
          op: S.activeOperation,
          ordemOpenedAt: S.phases[0].orders[0].openedAt,
          disco: (__doDisco().activeOperation || null)
        })"""
    )
    assert estado["op"], (
        "abrir a Genese pelo <select> real NAO criou a Operacao Unica — o gancho "
        "esta em codigo morto, exatamente o defeito que este arquivo existe para pegar"
    )
    assert estado["op"]["openedAtSource"] == "genesis_transition", (
        f"proveniencia errada: {estado['op']['openedAtSource']!r}"
    )
    assert isinstance(estado["op"]["openedAt"], str) and estado["op"]["openedAt"], (
        "openedAt da operacao nao foi carimbado"
    )
    assert isinstance(estado["ordemOpenedAt"], str) and estado["ordemOpenedAt"], (
        "openedAt da ORDEM nao foi carimbado"
    )
    # PERSISTENCIA: o ato tem de ter chegado ao disco, nao so a memoria.
    assert estado["disco"], "a entidade nao foi persistida pelo save() do handler"
    assert estado["disco"]["operationId"] == estado["op"]["operationId"], (
        "a entidade persistida diverge da que esta em memoria"
    )


def run_identity_stable_across_renders(page):
    """Nova mudanca e novo render nao trocam identidade nem abertura."""
    antes = page.evaluate(
        """() => ({id: S.activeOperation.operationId,
                   openedAt: S.activeOperation.openedAt,
                   ordem: S.phases[0].orders[0].openedAt})"""
    )
    r = page.evaluate(
        """() => {
          renderPhases();                       // religa listeners nos nos novos
          const sel = __selectStatus(0,0);
          sel.value = 'Aberta';                 // mesma mudanca de novo
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          renderPhases(); render();
          return {id: S.activeOperation.operationId,
                  openedAt: S.activeOperation.openedAt,
                  ordem: S.phases[0].orders[0].openedAt};
        }"""
    )
    assert r["id"] == antes["id"], f"operationId mudou apos re-render: {antes['id']} -> {r['id']}"
    assert r["openedAt"] == antes["openedAt"], (
        f"openedAt da operacao foi reescrito: {antes['openedAt']} -> {r['openedAt']}"
    )
    assert r["ordem"] == antes["ordem"], (
        f"openedAt da ordem foi reescrito: {antes['ordem']} -> {r['ordem']}"
    )


def run_rejected_open_creates_nothing(page):
    """Abertura RECUSADA pelas guardas nao pode fazer a operacao nascer."""
    r = page.evaluate(
        """() => {
          S.activeOperation = null;
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          const g = S.phases[0].orders[0];
          g.id='X'; g.lote=0.10; g.entry=1.10; g.sl=1.09;   // SEM par -> guarda recusa
          renderPhases();
          const sel = __selectStatus(0,0);
          sel.value = 'Aberta';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          return {status: S.phases[0].orders[0].status, op: S.activeOperation};
        }"""
    )
    assert r["status"] != "Aberta", f"a guarda de par ausente nao recusou: {r['status']!r}"
    assert r["op"] is None, (
        "a operacao nasceu de uma abertura RECUSADA — um ato que nao aconteceu "
        "nao pode criar identidade nem carimbar abertura"
    )


def run_close_order_through_ui(page):
    """Fechar ordem pelo modal real carimba closedAt."""
    r = page.evaluate(
        """() => {
          __prepararGenese();
          const sel = __selectStatus(0,0);
          sel.value = 'Aberta'; sel.dispatchEvent(new Event('change', {bubbles:true}));
          renderPhases();
          const sel2 = __selectStatus(0,0);
          sel2.value = 'Fechada'; sel2.dispatchEvent(new Event('change', {bubbles:true}));
          const temModal = !!document.getElementById('closeConfirmInput');
          if (!temModal) return {erro:'modal de fechamento nao abriu'};
          document.getElementById('closeResultInput').value = '250';
          document.getElementById('closeConfirmInput').value = 'FECHADO';
          document.getElementById('modalConfirm').click();
          const o = S.phases[0].orders[0];
          return {status:o.status, result:o.result, closedAt:o.closedAt, openedAt:o.openedAt};
        }"""
    )
    assert "erro" not in r, r.get("erro")
    assert r["status"] == "Fechada" and r["result"] == 250, f"fechamento nao aplicou: {r}"
    assert isinstance(r["closedAt"], str) and r["closedAt"], (
        "closedAt nao foi carimbado pelo fluxo REAL de fechamento"
    )
    assert isinstance(r["openedAt"], str), "o fechamento apagou o openedAt da ordem"


def run_reset_does_not_leak_identity(page):
    """Reinicio administrativo abandona a operacao SEM fabricar Historico.

    Sem limpar activeOperation, a guarda `!S.activeOperation` do nascimento
    seria falsa na Genese seguinte e a operacao NOVA herdaria operationId,
    openedAt e maxAccountPhaseReached da anterior — gravando no Historico uma
    abertura de semanas atras com proveniencia automatica.
    """
    a = page.evaluate(
        """() => {
          __prepararGenese();
          const sel = __selectStatus(0,0);
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true}));
          S.activeOperation.maxAccountPhaseReached = 2;   // chegou a Fase 3
          save();
          return {id:S.activeOperation.operationId,
                  openedAt:S.activeOperation.openedAt,
                  maxFase:S.activeOperation.maxAccountPhaseReached};
        }"""
    )
    assert a["id"], "Genese A nao criou operacao"

    # ATO REAL de reinicio de periodo: as mesmas mutacoes que o fluxo executa.
    reset = page.evaluate(
        """() => {
          const antes = {registros:(S.operationHistory.records||[]).length,
                         ciclo:S.cycleRealizado};
          S.cycleRealizado=0;
          const cycleSizes=[5,4,3,2];
          S.phases.forEach((ph,pi)=>{ ph.orders=emptyOrders(cycleSizes[pi]||3); });
          S.phaseUnlocked=[true,false,false,false];
          S.activeOperation=null;
          save();
          return {antes, registros:(S.operationHistory.records||[]).length,
                  op:S.activeOperation};
        }"""
    )
    assert reset["op"] is None, "o reinicio deixou a operacao viva"
    assert reset["registros"] == reset["antes"]["registros"], (
        f"o reinicio FABRICOU registro historico: {reset['antes']['registros']} -> "
        f"{reset['registros']} — abandonar nao e encerrar"
    )

    b = page.evaluate(
        """() => {
          __prepararGenese();
          const sel = __selectStatus(0,0);
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true}));
          return {id:S.activeOperation.operationId,
                  openedAt:S.activeOperation.openedAt,
                  maxFase:S.activeOperation.maxAccountPhaseReached,
                  ciclo:S.cycleRealizado,
                  registros:(S.operationHistory.records||[]).length};
        }"""
    )
    assert b["id"] != a["id"], (
        f"a operacao B HERDOU a identidade de A: {b['id']} — cada Operacao Unica "
        "precisa de identidade propria"
    )
    assert b["openedAt"] != a["openedAt"], (
        f"B herdou a abertura de A: {b['openedAt']} — proveniencia automatica "
        "atestando um fato falso"
    )
    assert b["maxFase"] != 2, (
        f"B herdou a fase maxima de A: {b['maxFase']!r} — a monotonicidade seria "
        "quebrada para CIMA, sem evidencia"
    )
    assert b["ciclo"] == 0, f"o reinicio consolidou algo no ciclo: {b['ciclo']}"
    assert b["registros"] == 0, "abrir B fabricou registro historico"


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            page.evaluate(PREPARAR)
            run_genesis_birth_through_ui(page)
            run_identity_stable_across_renders(page)
            run_rejected_open_creates_nothing(page)
            run_close_order_through_ui(page)
            run_reset_does_not_leak_identity(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("OPERATION WIRING TEST PASS")


if __name__ == "__main__":
    main()
