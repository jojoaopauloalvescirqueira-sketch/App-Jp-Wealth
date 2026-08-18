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

    # O fluxo real de reinicio vive em commitOnboardingStart(), closure dentro
    # de openOnboardingModal() — as ~2 mil linhas ja registradas como divida no
    # CURRENT-STATE. Aciona-la exigiria preencher o formulario inteiro, e
    # refatora-la esta fora do escopo desta tarefa.
    #
    # Por isso a verificacao tem DUAS partes, e a distincao e explicita:
    # (a) GUARDA SOBRE O CODIGO REAL — le o arquivo servido e exige que o bloco
    #     de reinicio limpe a entidade e NAO toque no historico. E o que mata a
    #     mutacao; sem ela, alterar o fluxo passaria despercebido.
    # (b) COMPORTAMENTO — executa as mesmas mutacoes e prova que a Genese
    #     seguinte nasce sem herdar nada.
    fonte = page.evaluate(
        """async () => {
          const r = await fetch('/src/js/40-app/04-onboarding.js');
          const txt = await r.text();
          const i = txt.indexOf('S.cycleRealizado=0;');
          // a partir de i: a primeira ocorrencia desta ancora fica ANTES do bloco
          const j = txt.indexOf('S.onboarding=nextOnboarding;', i);
          if (i < 0 || j < 0 || j <= i) return {erro:'bloco de reinicio nao localizado'};
          const bloco = txt.slice(i, j);
          return {
            limpa: /S\.activeOperation\s*=\s*null/.test(bloco),
            tocaHistorico: /operationHistory/.test(bloco),
            consolida: /cycleRealizado\s*\+=/.test(bloco)
          };
        }"""
    )
    assert "erro" not in fonte, fonte.get("erro")
    assert fonte["limpa"], (
        "o fluxo REAL de reinicio de periodo nao limpa S.activeOperation — a "
        "Genese seguinte herdaria identidade, abertura e fase maxima"
    )
    assert not fonte["tocaHistorico"], (
        "o reinicio toca operationHistory — abandonar administrativamente NAO "
        "pode fabricar registro historico; encerrar e ato proprio"
    )
    assert not fonte["consolida"], "o reinicio consolida em cycleRealizado"

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


def run_unlock_by_own_genesis_is_stamped_with_real_identity(page):
    """A Genese que destrava fase carimba o evento com a identidade REAL.

    handleStopLimitBreach destrava a fase e carimba o evento via
    operationStampTransition, que le S.activeOperation. Enquanto o nascimento
    ficava DEPOIS dele, o destravamento provocado pela PROPRIA primeira ordem da
    operacao era carimbado com operationId:null; operationResolveGridPhaseMax
    descartava o evento orfao e devolvia 0, e o registro imutavel afirmava
    "Fase maxima da Grade: FASE 1" para uma operacao que viveu inteira na FASE 2
    — a fase que essa mesma ordem forcou.
    """
    r = page.evaluate(
        """() => {
          const avisos=[];
          window.alert = m => avisos.push(String(m));
          window.confirm = () => true;
          __prepararGenese();
          // Perda de ciclo arquivada: e ela que faz a Genese estourar o teto da
          // FASE 1 pelo ramo 'fase' (e nao pelo limite proprio da Genese), que e
          // a unica porta para o destravamento por stop quantitativo.
          S.cycleRealizado = -360;
          const g = S.phases[0].orders[0];
          g.lote = 0.05; g.entry = 1.08; g.sl = 1.07;
          save(); renderPhases();

          // checkPhaseCap retorna cedo quando o status nao e 'Aberta'. Para
          // PREVER o desfecho, aplica-se o status temporariamente e desfaz-se —
          // o ato real acontece pelo <select>, logo abaixo.
          g.status = 'Aberta';
          const check = checkPhaseCap(0,0);
          const suporte = phaseSupportForRisk(check.total);
          g.status = '';
          renderPhases();
          // Responde a frase EXATA que o sistema exige.
          window.prompt = () => 'CONFIRMO ' + S.phases[suporte].faseNome;

          const sel = __selectStatus(0,0);
          if (!sel) return {erro:'select de status nao encontrado'};
          sel.value = 'Aberta';
          sel.dispatchEvent(new Event('change', {bubbles:true}));

          const op = S.activeOperation;
          const eventos = (S.transitionLog||[]).map(e => ({
            fase:e.fase, gridPhase:e.gridPhase, operationId:e.operationId}));
          return {
            check:{excede:check.excede, tipo:check.tipo, total:check.total}, suporte,
            unlocked: S.phaseUnlocked.slice(),
            opId: op && op.operationId,
            eventos,
            gridMax: op ? operationResolveGridPhaseMax(op) : null,
            avisos
          };
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["check"]["excede"] and r["check"]["tipo"] == "fase", (
        f"a fixture nao levou ao ramo de destravamento por fase: {r['check']} — "
        "sem isso o teste nao exercita o defeito"
    )
    assert r["suporte"] == 1, f"a fase que suporta deveria ser a 2 (indice 1): {r['suporte']}"
    assert r["unlocked"] == [True, True, False, False], (
        f"a FASE 2 nao foi destravada: {r['unlocked']} — a confirmacao nao passou"
    )
    assert r["opId"], "a operacao nao nasceu"
    carimbados = [e for e in r["eventos"] if e.get("gridPhase") is not None]
    assert carimbados, f"nenhum evento de destravamento foi registrado: {r['eventos']}"
    for e in carimbados:
        assert e["operationId"] == r["opId"], (
            f"evento de destravamento carimbado com operationId {e['operationId']!r} "
            f"em vez de {r['opId']!r} — o destravamento causado pela propria Genese "
            "ficaria orfao e some do maximo da grade"
        )
    assert r["gridMax"] == 1, (
        f"maxGridPhaseReached = {r['gridMax']} — a operacao viveu na FASE 2 desde a "
        "sua primeira ordem, e o registro afirmaria FASE 1"
    )


def run_manual_risk_refusal_creates_no_entity(page):
    """Recusar a confirmacao manual de risco nao cria entidade nem efeito.

    Essa confirmacao ficava DEPOIS de handleStopLimitBreach. Um "nao" do
    operador ali reverteria uma abertura que ja tinha destravado fase e
    carimbado evento — efeito colateral sobrevivendo a um ato recusado. Ela
    passou a ser a ultima guarda REJEITADORA, antes do nascimento.
    """
    r = page.evaluate(
        """() => {
          window.alert = () => {};
          window.prompt = () => null;
          __prepararGenese();
          S.cycleRealizado = -360;
          const g = S.phases[0].orders[0];
          g.lote = 0.05; g.entry = 1.08; g.sl = 1.07;
          save(); renderPhases();
          const unlockedAntes = S.phaseUnlocked.slice();
          const logAntes = (S.transitionLog||[]).length;
          // O operador RECUSA a confirmacao manual de risco.
          window.confirm = () => false;
          const exigiu = shouldWarnManualRiskConfirmation();
          const sel = __selectStatus(0,0);
          sel.value = 'Aberta';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          return {exigiu, status:S.phases[0].orders[0].status,
                  op:S.activeOperation, unlockedAntes,
                  unlockedDepois:S.phaseUnlocked.slice(),
                  logAntes, logDepois:(S.transitionLog||[]).length};
        }"""
    )
    if not r["exigiu"]:
        # Sem Equity Protector inativo a confirmacao nao e pedida; o caso nao
        # existe nesta fixture e afirmar qualquer coisa aqui seria vacuo.
        assert r["op"], "a operacao deveria ter nascido quando nao ha confirmacao a recusar"
        return
    assert r["status"] != "Aberta", f"a ordem abriu apesar da recusa: {r['status']!r}"
    assert r["op"] is None, (
        f"a recusa criou entidade: {r['op']} — ordem recusada jamais cria operacao"
    )
    assert r["unlockedDepois"] == r["unlockedAntes"], (
        f"a recusa deixou fase destravada: {r['unlockedAntes']} -> {r['unlockedDepois']} — "
        "efeito colateral sobreviveu a um ato que nao aconteceu"
    )
    assert r["logDepois"] == r["logAntes"], "a recusa deixou evento no transitionLog"


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
            run_unlock_by_own_genesis_is_stamped_with_real_identity(page)
            run_manual_risk_refusal_creates_no_entity(page)
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
