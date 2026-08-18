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
          // A confirmacao manual so e PEDIDA sem protecao externa ativa. Sem
          // montar essa condicao, o caso nao existe e o teste passaria sem
          // exercitar nada — foi assim que uma mutacao sobreviveu.
          S.onboarding = S.onboarding || {};
          const _onbAntes = {done:S.onboarding.done, ep:S.onboarding.epStatus};
          S.onboarding.done = true;
          S.onboarding.epStatus = 'Não vou utilizar.';
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
          const fora = {exigiu, status:S.phases[0].orders[0].status,
                  op:S.activeOperation, unlockedAntes,
                  unlockedDepois:S.phaseUnlocked.slice(),
                  logAntes, logDepois:(S.transitionLog||[]).length};
          // RESTAURA a configuracao de protecao: deixa-la alterada faria o caso
          // seguinte herdar a confirmacao manual e falhar por contaminacao.
          S.onboarding.done = _onbAntes.done;
          S.onboarding.epStatus = _onbAntes.ep;
          save();
          return fora;
        }"""
    )
    assert r["exigiu"], (
        "a fixture nao produziu a condicao em que a confirmacao manual e pedida "
        "(protecao externa inativa + risco). Sem ela o caso nao existe e o teste "
        "passaria sem exercitar nada"
    )
    assert r["status"] != "Aberta", f"a ordem abriu apesar da recusa: {r['status']!r}"
    assert r["op"] is None, (
        f"a recusa criou entidade: {r['op']} — ordem recusada jamais cria operacao"
    )
    assert r["unlockedDepois"] == r["unlockedAntes"], (
        f"a recusa deixou fase destravada: {r['unlockedAntes']} -> {r['unlockedDepois']} — "
        "efeito colateral sobreviveu a um ato que nao aconteceu"
    )
    assert r["logDepois"] == r["logAntes"], "a recusa deixou evento no transitionLog"


def run_deleting_last_operational_order_abandons(page):
    """Excluir a ULTIMA ordem operacional abandona a operacao — sem fingir fim.

    A exclusao apaga a evidencia que constituia a Operacao Unica. Se a entidade
    sobrevivesse, a guarda de nascimento (`!S.activeOperation`) falharia na
    proxima Genese e a nova tese herdaria identidade, abertura e proveniencia.
    Abandono NAO e finalizacao: nenhum registro, nenhuma consolidacao, nenhum
    reset de fases.
    """
    r = page.evaluate(
        """() => {
          window.confirm = () => true;
          window.alert = () => {};
          __prepararGenese();
          S.cycleRealizado = 777;
          const sel = __selectStatus(0,0);
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true}));
          const opAntes = S.activeOperation && S.activeOperation.operationId;
          const antes = {ciclo:S.cycleRealizado, regs:S.operationHistory.records.length,
                         fases:S.phaseUnlocked.slice(), vivas:operationLiveOrders().length};
          const btn = document.querySelector('[data-delorder="0:0"]');
          if(!btn) return {erro:'botao de exclusao nao encontrado'};
          btn.click();
          const disco = __doDisco();
          return {opAntes, antes,
                  op: S.activeOperation,
                  ciclo:S.cycleRealizado, regs:S.operationHistory.records.length,
                  fases:S.phaseUnlocked.slice(), vivas:operationLiveOrders().length,
                  opNoDisco: disco.activeOperation,
                  regsNoDisco:(disco.operationHistory&&disco.operationHistory.records||[]).length};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["opAntes"], "a operacao nao nasceu na abertura"
    assert r["antes"]["vivas"] == 1, f"pre-condicao: {r['antes']}"
    assert r["vivas"] == 0, f"a exclusao nao removeu a ordem: {r['vivas']}"
    assert r["op"] is None, (
        f"a entidade sobreviveu a exclusao da ultima ordem operacional: {r['op']} — "
        "a proxima Genese herdaria identidade, abertura e proveniencia dela"
    )
    assert r["opNoDisco"] is None, "o abandono nao foi persistido"
    assert r["regs"] == r["antes"]["regs"] == 0 and r["regsNoDisco"] == 0, (
        f"o abandono inventou registro no Historico: {r['regs']}/{r['regsNoDisco']}"
    )
    assert r["ciclo"] == r["antes"]["ciclo"] == 777, (
        f"o abandono consolidou em cycleRealizado: {r['antes']['ciclo']} -> {r['ciclo']}"
    )
    assert r["fases"] == r["antes"]["fases"], (
        f"o abandono resetou fases: {r['antes']['fases']} -> {r['fases']}"
    )


def run_deleting_one_of_many_keeps_the_operation(page):
    """Sobrando ordem operacional, a operacao PERMANECE.

    Controle indispensavel: sem ele a correcao poderia ser a heuristica global
    "grade mexeu, dissolve", que mataria uma operacao viva.
    """
    r = page.evaluate(
        """() => {
          window.confirm = () => true; window.alert = () => {};
          __prepararGenese();
          const sel = __selectStatus(0,0);
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true}));
          const opAntes = S.activeOperation && S.activeOperation.operationId;
          // Segunda ordem operacional, na mesma tese.
          const d = S.phases[0].orders[1];
          d.id='D1'; d.par='EURUSD'; d.tipo='BUY'; d.lote=0.01; d.entry=1.10; d.sl=1.095; d.tp=1.12;
          d.status='Fechada'; d.result=-20; d.openedAt='2026-08-02T10:00:00.000Z';
          d.closedAt='2026-08-03T10:00:00.000Z';
          save(); renderPhases();
          const btn = document.querySelector('[data-delorder="0:1"]');
          if(!btn) return {erro:'botao de exclusao nao encontrado'};
          btn.click();
          return {opAntes, op:S.activeOperation && S.activeOperation.operationId,
                  vivas:operationLiveOrders().length};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["vivas"] == 1, f"esperava uma ordem operacional restante: {r['vivas']}"
    assert r["op"] == r["opAntes"], (
        f"a operacao foi dissolvida havendo ordem operacional restante: "
        f"{r['opAntes']} -> {r['op']} — 'grade mexeu' nao pode dissolver a tese"
    )


def run_new_thesis_never_inherits_orphan_identity(page):
    """FAIL-SAFE: identidade orfa nao e reutilizada pela tese seguinte.

    Reproduz a cadeia medida: operacao 1 aberta e fechada, linhas apagadas,
    operacao 2 em OUTRO instrumento. O registro imutavel da segunda chegava a
    afirmar a identidade, a abertura e a proveniencia automatica da primeira.
    """
    r = page.evaluate(
        """() => {
          window.confirm = () => true; window.alert = () => {};
          __prepararGenese();
          const sel = __selectStatus(0,0);
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true}));
          const op1 = JSON.parse(JSON.stringify(S.activeOperation));
          // Orfandade FORCADA: apaga a ordem sem passar pelo ato de exclusao,
          // para exercitar o fail-safe e nao a correcao do handler.
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.activeOperation = JSON.parse(JSON.stringify(op1));
          save();
          const orfaViva = S.activeOperation && S.activeOperation.operationId;
          // Tese NOVA, outro instrumento.
          const g = S.phases[0].orders[0];
          g.id='G2'; g.par='GBPUSD'; g.tipo='SELL'; g.lote=0.01; g.entry=1.27; g.sl=1.275; g.tp=1.20;
          renderPhases();
          const sel2 = __selectStatus(0,0);
          sel2.value='Aberta'; sel2.dispatchEvent(new Event('change',{bubbles:true}));
          const op2 = S.activeOperation;
          const log = ((S.dataGovernance||{}).changeLog||[])
            .filter(e => e && e.action==='orphan_discarded').map(e => e.recordId);
          return {op1:{id:op1.operationId, abertura:op1.openedAt, fonte:op1.openedAtSource},
                  orfaViva,
                  op2:op2 && {id:op2.operationId, abertura:op2.openedAt, fonte:op2.openedAtSource},
                  log};
        }"""
    )
    assert r["orfaViva"] == r["op1"]["id"], f"a orfa nao foi montada: {r}"
    assert r["op2"], "a nova tese nao produziu entidade"
    assert r["op2"]["id"] != r["op1"]["id"], (
        f"a tese nova HERDOU a identidade orfa ({r['op2']['id']}) — o registro "
        "imutavel afirmaria que ela e a operacao anterior"
    )
    assert r["op2"]["abertura"] != r["op1"]["abertura"], (
        f"a tese nova herdou a abertura da anterior: {r['op2']['abertura']}"
    )
    assert r["op2"]["fonte"] == "genesis_transition", (
        f"proveniencia da nova Genese: {r['op2']['fonte']!r}"
    )
    assert r["op1"]["id"] in r["log"], (
        f"o descarte da identidade orfa nao ficou auditavel: {r['log']} — "
        "bloquear em silencio esconde um estado inconsistente"
    )


def run_status_reverted_withdraws_the_order(page):
    """Devolver o Status a '—' retira a ordem do ciclo, e a tese seguinte e NOVA.

    Esta porta esvazia a Operacao Unica sem passar pela finalizacao, pelo
    reinicio de periodo nem pelo botao de exclusao. Antes, activeOperation
    sobrevivia orfa E o carimbo openedAt ficava na linha: reabrir a MESMA linha
    fazia `jaPertencia` valer true, o fail-safe ser pulado, e a tese nova herdar
    identidade, abertura e proveniencia da anterior.
    """
    r = page.evaluate(
        """() => {
          window.alert = () => {};
          window.confirm = () => true;
          window.prompt = () => null;
          __prepararGenese();
          const sel = __selectStatus(0,0);
          if (!sel) return {erro:'select ausente'};
          sel.value = 'Aberta'; sel.dispatchEvent(new Event('change', {bubbles:true}));
          const A = S.activeOperation;
          const carimboA = S.phases[0].orders[0].openedAt;
          const cicloAntes = S.cycleRealizado;
          const registrosAntes = S.operationHistory.records.length;
          const fasesAntes = S.phaseUnlocked.slice();

          // RETIRADA: o operador devolve o Status para '—'.
          const sel2 = __selectStatus(0,0);
          sel2.value = ''; sel2.dispatchEvent(new Event('change', {bubbles:true}));
          const aposRetirar = {
            op: S.activeOperation,
            status: S.phases[0].orders[0].status,
            openedAt: S.phases[0].orders[0].openedAt,
            closedAt: S.phases[0].orders[0].closedAt,
            vivas: operationLiveOrders().length,
            ciclo: S.cycleRealizado,
            registros: S.operationHistory.records.length,
            fases: S.phaseUnlocked.slice()
          };

          // Tese NOVA na MESMA linha.
          const g = S.phases[0].orders[0];
          g.par='GBPUSD'; g.tipo='SELL'; g.lote=0.01; g.entry=1.27; g.sl=1.271; g.tp=1.20;
          save(); renderPhases();
          const sel3 = __selectStatus(0,0);
          sel3.value = 'Aberta'; sel3.dispatchEvent(new Event('change', {bubbles:true}));
          const B = S.activeOperation;
          return {idA: A && A.operationId, aberturaA: A && A.openedAt, carimboA,
                  aposRetirar,
                  idB: B && B.operationId, aberturaB: B && B.openedAt,
                  fonteB: B && B.openedAtSource,
                  carimboB: S.phases[0].orders[0].openedAt,
                  cicloAntes, registrosAntes, fasesAntes};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["idA"] and r["carimboA"], f"a operacao A nao nasceu: {r}"
    ap = r["aposRetirar"]
    assert ap["status"] == "", f"o status nao foi devolvido a vazio: {ap['status']!r}"
    assert ap["vivas"] == 0, f"ainda ha ordem operacional: {ap['vivas']}"
    assert ap["openedAt"] is None and ap["closedAt"] is None, (
        f"os carimbos da LINHA sobreviveram a retirada: {ap['openedAt']!r} / "
        f"{ap['closedAt']!r} — sao eles que fazem o fail-safe ser pulado depois"
    )
    assert ap["op"] is None, (
        f"a identidade sobreviveu a retirada da ultima ordem operacional: {ap['op']}"
    )
    assert ap["registros"] == r["registrosAntes"], "a retirada gravou Historico"
    assert ap["ciclo"] == r["cicloAntes"], "a retirada mexeu em cycleRealizado"
    assert ap["fases"] == r["fasesAntes"], "a retirada resetou fases"
    assert r["idB"] and r["idB"] != r["idA"], (
        f"a tese nova HERDOU a identidade anterior: {r['idB']!r} == {r['idA']!r}"
    )
    assert r["aberturaB"] and r["aberturaB"] != r["aberturaA"], (
        f"a tese nova herdou a abertura da anterior: {r['aberturaB']!r}"
    )
    assert r["fonteB"] == "genesis_transition", f"proveniencia da nova: {r['fonteB']!r}"
    assert r["carimboB"] and r["carimboB"] != r["carimboA"], (
        f"o carimbo da linha nao foi refeito: {r['carimboB']!r}"
    )


def run_withdrawing_one_order_keeps_the_operation(page):
    """Retirar UMA linha, havendo outra ordem operacional, preserva a operacao."""
    r = page.evaluate(
        """() => {
          window.alert = () => {}; window.confirm = () => true; window.prompt = () => null;
          __prepararGenese();
          const s1 = __selectStatus(0,0);
          s1.value = 'Aberta'; s1.dispatchEvent(new Event('change', {bubbles:true}));
          const idAntes = S.activeOperation && S.activeOperation.operationId;
          const aberturaAntes = S.activeOperation && S.activeOperation.openedAt;
          // Segunda ordem da MESMA tese, tambem operacional.
          const d = S.phases[0].orders[1];
          d.id='D1'; d.par='EURUSD'; d.tipo='BUY'; d.lote=0.01;
          d.entry=1.1000; d.sl=1.0950; d.tp=1.1200;
          save(); renderPhases();
          const s2 = __selectStatus(0,1);
          if (!s2) return {erro:'select da segunda linha ausente'};
          s2.value = 'Aberta'; s2.dispatchEvent(new Event('change', {bubbles:true}));
          const vivasAntes = operationLiveOrders().length;
          // Retira SO a segunda.
          const s3 = __selectStatus(0,1);
          s3.value = ''; s3.dispatchEvent(new Event('change', {bubbles:true}));
          return {idAntes, aberturaAntes, vivasAntes,
                  vivasDepois: operationLiveOrders().length,
                  idDepois: S.activeOperation && S.activeOperation.operationId,
                  aberturaDepois: S.activeOperation && S.activeOperation.openedAt,
                  carimboRetirada: S.phases[0].orders[1].openedAt,
                  carimboMantida: S.phases[0].orders[0].openedAt};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["vivasAntes"] == 2, f"o cenario nao criou duas ordens vivas: {r['vivasAntes']}"
    assert r["vivasDepois"] == 1, f"a retirada nao removeu a linha: {r['vivasDepois']}"
    assert r["carimboRetirada"] is None, (
        f"o carimbo da linha retirada sobreviveu: {r['carimboRetirada']!r}"
    )
    assert r["carimboMantida"], "o carimbo da linha MANTIDA foi apagado indevidamente"
    assert r["idDepois"] == r["idAntes"], (
        f"a operacao perdeu a identidade ao retirar UMA linha: {r['idAntes']!r} -> "
        f"{r['idDepois']!r} — retirar uma ordem nao encerra a tese"
    )
    assert r["aberturaDepois"] == r["aberturaAntes"], "a abertura da operacao mudou"


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
            # ---- R2: retirada explicita da ordem do ciclo ----
            run_status_reverted_withdraws_the_order(page)
            run_withdrawing_one_order_keeps_the_operation(page)
            run_deleting_last_operational_order_abandons(page)
            run_deleting_one_of_many_keeps_the_operation(page)
            run_new_thesis_never_inherits_orphan_identity(page)
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
