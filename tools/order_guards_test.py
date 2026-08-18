#!/usr/bin/env python3
"""Guardas de ordem na grade: nenhuma edicao ultrapassa o teto de risco da fase.

O teto consolidado da grade e limite ESTATUTARIO. O ramo de <input> ja o
aplicava a lote, entrada e stop; a troca de PAR escapava da checagem e permitia
ultrapassar o limite sem alerta, sem reversao e sem o questionario de transicao —
o risco em USD de uma ordem depende de cpl e da conversao da moeda de cotacao,
entao trocar o instrumento move o risco tanto quanto trocar o lote.

Este teste NAO reimplementa formula alguma: monta a ordem, dispara a edicao pela
interface real e confere o veredito das funcoes do proprio app.

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
    page.route(
        "**/*",
        lambda route: route.continue_() if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="load")
    page.wait_for_function("() => typeof S === 'object' && typeof checkPhaseCap === 'function'")
    return context, page, observed


# Cenario montado para que as guardas ANTERIORES deixem passar e o teto da FASE
# seja quem decide:
#   · uma unica posicao aberta, senao Operacao Unica (Art. 3.6) barra antes;
#   · lote dentro do Teto/Op dos dois instrumentos, senao a Regra 1 barra antes.
MONTA_CENARIO = """() => {
  S.phases.forEach(ph => ph.orders.forEach(o => { o.status='Vazia'; o.par=''; o.lote=0; }));
  const o = S.phases[0].orders[0];
  o.par='USDJPY'; o.status='Aberta'; o.tipo='Compra'; o.lote=0.05; o.entry=1.10; o.sl=1.00;
  save(); renderPhases();
  return {risco: orderRisk(o), teto: phaseTetoRisco(0), par: o.par};
}"""


def instrumenta_confirmacoes(page):
    page.evaluate(
        "() => { window.__avisos = [];"
        "        window.alert = m => { window.__avisos.push(String(m)); };"
        "        window.confirm = m => { window.__avisos.push(String(m)); return false; }; }")


def troca_par(page, destino):
    page.evaluate(
        """d => { const sel = document.querySelector('#phaseContainer select[data-f="par"]');
                  if (!sel) throw new Error('select de par nao encontrado na grade');
                  sel.value = d; sel.dispatchEvent(new Event('change', {bubbles:true})); }""",
        destino,
    )
    page.wait_for_timeout(200)


def run_par_excedente_e_barrado(page):
    """Trocar para um par que estoura o teto da fase: alerta e reversao."""
    base = page.evaluate(MONTA_CENARIO)
    assert base["risco"] < base["teto"], f"pre-condicao: a ordem ja nascia acima do teto ({base})"
    instrumenta_confirmacoes(page)
    troca_par(page, "EURUSD")

    avisos = page.evaluate("() => window.__avisos")
    estado = page.evaluate("() => ({par: S.phases[0].orders[0].par, risco: orderRisk(S.phases[0].orders[0])})")
    assert any("TETO DE RISCO" in a for a in avisos), f"nenhum alerta de teto foi emitido: {avisos}"
    assert estado["par"] == "USDJPY", f"a troca nao foi revertida: par ficou {estado['par']}"
    assert estado["risco"] <= base["teto"], (
        f"risco {estado['risco']} permaneceu acima do teto {base['teto']}"
    )
    # E o limite nao foi contornado por baixo: nenhuma fase destravou sozinha.
    assert page.evaluate("() => JSON.stringify(S.phaseUnlocked)") == "[true,false,false,false]", (
        "a troca de par destravou fase sem o questionario de transicao"
    )
    assert page.evaluate("() => S.transitionLog.length") == 0, "transicao registrada sem questionario"


def run_par_dentro_do_teto_passa(page):
    """Controle: a mesma troca, com lote que cabe no teto, NAO e barrada.

    Sem este caso o teste passaria com uma guarda que recusasse tudo.
    """
    page.evaluate(
        """() => {
          S.phases.forEach(ph => ph.orders.forEach(o => { o.status='Vazia'; o.par=''; o.lote=0; }));
          const o = S.phases[0].orders[0];
          o.par='USDJPY'; o.status='Aberta'; o.tipo='Compra'; o.lote=0.01; o.entry=1.10; o.sl=1.099;
          save(); renderPhases();
        }"""
    )
    instrumenta_confirmacoes(page)
    troca_par(page, "EURUSD")
    avisos = page.evaluate("() => window.__avisos")
    par = page.evaluate("() => S.phases[0].orders[0].par")
    assert not any("TETO DE RISCO" in a for a in avisos), f"troca legitima foi barrada: {avisos}"
    assert par == "EURUSD", f"troca legitima nao foi aplicada: par ficou {par}"


# ---------------------------------------------------------------------------
# Operacao Unica Exclusiva: a operacao continua em andamento com tudo fechado
# ---------------------------------------------------------------------------
# A guarda procurava referencia SO entre ordens `Aberta`. Fechar a ultima ordem
# nao finaliza a Operacao Unica — ela so termina na Finalizacao formal, que e o
# ato que limpa as grades. Com a Genese fechada e a operacao ainda viva, a
# guarda nao encontrava nada e liberava outro instrumento e outra direcao.
#
# O estado resultante era um beco sem saida: a Finalizacao o bloqueia, mas numa
# ordem fechada `par`, `tipo` e `status` ficam todos desabilitados na grade.
#
# Todos os casos passam pelo <select> REAL de status. Foi um teste que so olhava
# o dominio que deixou passar o BLOCKER de fiacao desta serie.

CENARIO_EXCLUSIVIDADE = """(opts) => {
  const teto = n => { const i = (S.instruments||[]).find(x => x.name === n); return i ? i.teto : 0.01; };
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
  // Genese EURUSD SELL — JA FECHADA. A operacao permanece viva.
  S.phases[0].orders[0] = {id:'G1', par:'EURUSD', tipo:'SELL', lote:0.01,
    entry:1.10, sl:1.101, tp:1.00, result:250, status:'Fechada',
    openedAt:'2026-08-01T10:00:00.000Z', closedAt:'2026-08-05T15:00:00.000Z'};
  S.phaseUnlocked = [true,false,false,false];
  S.activeOperation = {schemaVersion:1, operationId:'op_excl',
    openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
    maxAccountPhaseReached:0};
  if (opts && opts.par) {
    const c = S.phases[0].orders[1];
    c.par = opts.par; c.tipo = opts.tipo;
    c.lote = Math.min(0.01, teto(opts.par));
    c.entry = 1.10;
    c.sl = opts.tipo === 'SELL' ? 1.101 : 1.099;
    c.tp = opts.tipo === 'SELL' ? 1.00 : 1.20;
  }
  save(); renderPhases();
  return {vivas: (typeof operationLiveOrders === 'function') ? operationLiveOrders().length : null};
}"""


def abre_linha(page, oi):
    """Dispara a abertura pelo <select> de status REAL da grade."""
    return page.evaluate(
        """oi => {
          const sel = document.querySelector(
            '#phaseContainer select[data-p="0"][data-o="'+oi+'"][data-f="status"]');
          if (!sel) throw new Error('select de status nao encontrado para a linha '+oi);
          if (sel.disabled) return {desabilitado:true};
          sel.value = 'Aberta';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          return {desabilitado:false, valorNoSelect: sel.value};
        }""", oi)


def _monta(page, par=None, tipo=None):
    page.evaluate(CENARIO_EXCLUSIVIDADE, {"par": par, "tipo": tipo} if par else {})
    instrumenta_confirmacoes(page)


def run_exclusividade_barra_outro_instrumento(page):
    """Caso 1 — tudo fechado, tentar GBPUSD SELL: a interface bloqueia."""
    _monta(page, "GBPUSD", "SELL")
    abre_linha(page, 1)
    r = page.evaluate(
        """() => ({avisos: window.__avisos,
                  status: S.phases[0].orders[1].status,
                  par: S.phases[0].orders[1].par,
                  opId: S.activeOperation && S.activeOperation.operationId})"""
    )
    assert any("Operação Única" in a for a in r["avisos"]), (
        f"abertura de OUTRO instrumento nao foi barrada: {r['avisos']} — a operacao "
        "continua em andamento mesmo com todas as ordens fechadas"
    )
    assert r["status"] != "Aberta", (
        f"a ordem divergente ABRIU (status {r['status']!r}) e a operacao passou a "
        "conter duas teses; a Finalizacao ficaria bloqueada sem saida"
    )
    assert r["opId"] == "op_excl", "a identidade da operacao mudou"


def run_exclusividade_barra_direcao_contraria(page):
    """Caso 2 — tudo fechado, tentar EURUSD BUY: a interface bloqueia."""
    _monta(page, "EURUSD", "BUY")
    abre_linha(page, 1)
    r = page.evaluate(
        """() => ({avisos: window.__avisos, status: S.phases[0].orders[1].status,
                  tipo: S.phases[0].orders[1].tipo})"""
    )
    assert any("Operação Única" in a for a in r["avisos"]), (
        f"direcao contraria no MESMO instrumento nao foi barrada: {r['avisos']}"
    )
    assert r["status"] != "Aberta", (
        f"posicao na direcao contraria ABRIU (status {r['status']!r}) — ela nao "
        "pertence a mesma tese"
    )


def run_exclusividade_permite_mesma_tese(page):
    """Caso 3 — controle: nova EURUSD SELL nao e barrada pela exclusividade.

    Sem este caso o teste passaria com uma guarda que recusasse tudo.
    """
    _monta(page, "EURUSD", "SELL")
    abre_linha(page, 1)
    r = page.evaluate(
        """() => ({avisos: window.__avisos, status: S.phases[0].orders[1].status,
                  par: S.phases[0].orders[1].par, tipo: S.phases[0].orders[1].tipo})"""
    )
    assert not any("Operação Única" in a for a in r["avisos"]), (
        f"a MESMA tese foi barrada pela exclusividade: {r['avisos']}"
    )
    assert r["status"] == "Aberta", (
        f"reforco da mesma tese nao abriu (status {r['status']!r}, avisos {r['avisos']})"
    )


def run_exclusividade_termina_na_finalizacao(page):
    """Caso 4 — finalizada a operacao, outro instrumento constitui nova tese."""
    _monta(page)
    r0 = page.evaluate(
        """() => {
          const res = JPWOperation.finalize({defenseCount:0});
          renderPhases();
          return {ok:res.ok, motivo:res.motivo||null,
                  ativa: S.activeOperation, vivas: operationLiveOrders().length};
        }"""
    )
    assert r0["ok"], f"a finalizacao formal falhou: {r0}"
    assert r0["ativa"] is None, "activeOperation sobreviveu a finalizacao"
    assert r0["vivas"] == 0, f"grades nao foram liberadas: {r0['vivas']}"

    page.evaluate(
        """() => {
          const o = S.phases[0].orders[0];
          o.par='GBPUSD'; o.tipo='BUY'; o.lote=0.01; o.entry=1.27; o.sl=1.269; o.tp=1.35;
          save(); renderPhases();
        }"""
    )
    page.evaluate("() => { window.__avisos = []; }")
    abre_linha(page, 0)
    r = page.evaluate(
        """() => ({avisos: window.__avisos, status: S.phases[0].orders[0].status,
                  novaOp: !!S.activeOperation,
                  registros: S.operationHistory.records.length})"""
    )
    assert not any("Operação Única" in a for a in r["avisos"]), (
        f"a exclusividade da operacao ANTERIOR barrou a nova tese: {r['avisos']} — "
        "finalizar a operacao e o que libera outro instrumento"
    )
    assert r["status"] == "Aberta", f"a nova Genese nao abriu: {r}"
    assert r["registros"] == 1, "a operacao anterior sumiu do Historico"


def run_estado_legado_conflitado_segue_bloqueado(page):
    """Caso 5 — conflito preexistente continua bloqueado, sem correcao automatica.

    Este patch impede a CRIACAO do estado invalido. Ele nao reinterpreta dados
    passados: nenhuma ordem e escolhida, excluida, reaberta ou alterada.
    """
    r = page.evaluate(
        """() => {
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.phases[0].orders[0] = {id:'G1', par:'EURUSD', tipo:'SELL', lote:0.01,
            entry:1.10, sl:1.101, tp:1.00, result:400, status:'Fechada',
            openedAt:'2026-08-01T10:00:00.000Z', closedAt:'2026-08-05T15:00:00.000Z'};
          S.phases[0].orders[1] = {id:'D1', par:'GBPUSD', tipo:'BUY', lote:0.01,
            entry:1.27, sl:1.269, tp:1.35, result:-120, status:'Fechada',
            openedAt:'2026-08-06T09:00:00.000Z', closedAt:'2026-08-07T09:00:00.000Z'};
          S.phaseUnlocked=[true,false,false,false];
          S.activeOperation={schemaVersion:1, operationId:'op_legado',
            openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
            maxAccountPhaseReached:0};
          S.operationHistory={schemaVersion:1, records:[]};
          save();
          const antes = JSON.stringify(S.phases);
          const snap = JPWOperation.buildSnapshot(S.activeOperation, {defenseCount:0});
          const fim = JPWOperation.finalize({defenseCount:0});
          return {motivo: snap.motivo || null, valores: snap.valores || null,
                  ok: fim.ok, motivoFim: fim.motivo || null,
                  intacto: JSON.stringify(S.phases) === antes,
                  registros: S.operationHistory.records.length,
                  aindaViva: !!S.activeOperation};
        }"""
    )
    assert r["motivo"] == "instrument_conflict", (
        f"o conflito preexistente deixou de ser detectado: {r['motivo']!r}"
    )
    assert sorted(r["valores"] or []) == ["EURUSD", "GBPUSD"], (
        f"o bloqueio nao nomeia os valores em conflito: {r['valores']}"
    )
    assert r["ok"] is False and r["motivoFim"] == "instrument_conflict", (
        f"a finalizacao aceitou um estado conflitado: {r}"
    )
    assert r["intacto"], (
        "as grades foram ALTERADAS na tentativa — nenhuma ordem pode ser escolhida, "
        "excluida, reaberta ou corrigida automaticamente"
    )
    assert r["registros"] == 0, "um registro foi gravado a partir de estado conflitado"
    assert r["aindaViva"], "a operacao viva foi descartada"


def run_rascunho_nao_constitui_tese(page):
    """Linha preenchida porem NUNCA aberta nao e tese e nao bloqueia nada.

    A referencia e "pertence a operacao", nao "tem instrumento escrito". Um
    rascunho meio preenchido — instrumento escolhido, status ainda vazio — nao
    entrou na operacao, e trata-lo como tese faria uma linha esquecida barrar a
    propria Genese.
    """
    r = page.evaluate(
        """() => {
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.phaseUnlocked = [true,false,false,false];
          S.activeOperation = null;
          // Rascunho: instrumento escrito, jamais aberto.
          const d = S.phases[0].orders[1];
          d.par='GBPUSD'; d.tipo='BUY'; d.lote=0.01; d.entry=1.27; d.sl=1.269; d.tp=1.35;
          // Genese pretendida, em outro instrumento.
          const g = S.phases[0].orders[0];
          g.par='EURUSD'; g.tipo='SELL'; g.lote=0.01; g.entry=1.10; g.sl=1.101; g.tp=1.00;
          save(); renderPhases();
          return {vivasAntes: operationLiveOrders().length, rascunho: d.status};
        }"""
    )
    assert r["vivasAntes"] == 0, f"o rascunho ja contava como ordem viva: {r}"
    assert not r["rascunho"], f"o rascunho nasceu com status: {r['rascunho']!r}"
    # A instrumentacao e DESTE teste, e nao herdada do anterior: rodando
    # isolado, sem ela, nada captura alert() e a assercao sobre os avisos
    # passaria por vacuidade — sempre a lista vazia.
    instrumenta_confirmacoes(page)
    page.evaluate("() => { window.__avisos = []; }")
    abre_linha(page, 0)
    d = page.evaluate(
        """() => ({avisos: window.__avisos, status: S.phases[0].orders[0].status,
                  nasceu: !!S.activeOperation})"""
    )
    assert not any("Operação Única" in a for a in d["avisos"]), (
        f"um rascunho nunca aberto barrou a Genese: {d['avisos']} — ter instrumento "
        "escrito nao e pertencer a operacao"
    )
    assert d["status"] == "Aberta", f"a Genese nao abriu: {d}"
    assert d["nasceu"], "a operacao nao nasceu na abertura da Genese"


# ---------------------------------------------------------------------------
# R1 — breach que COMPROMETE o valor precisa observar a Fase da Conta
# ---------------------------------------------------------------------------
# handleStopLimitBreach nunca reverte o SL. Nos caminhos sem confirmacao — stop
# acima da fase recusado, limite da Genese, defesa final da Fase 4, limite
# absoluto — o valor PERMANECE e e persistido pelo save() interno, e a conta
# passa a operar acima do teto da fase por definicao de check.excede. Enquanto a
# captura morava dentro de save(), esses caminhos a recebiam de graca; ao tira-la
# de la, eles ficaram sendo os unicos que comprometem um valor sem observar a
# consequencia — e o registro imutavel saia com integridade 'observed' sobre um
# maximo que nunca foi medido.

CENARIO_R1 = """() => {
  window.__avisos = [];
  window.alert = m => window.__avisos.push(String(m));
  window.confirm = () => true;
  window.prompt = () => null;          // confirmacao formal RECUSADA
  S.params.saldoIni = 10000; S.cycleRealizado = 0;
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
  S.phaseUnlocked = [true,false,false,false];
  S.phases[0].orders[0] = {id:'G1', par:'EURUSD', tipo:'BUY', lote:0.05, entry:1.10,
    sl:1.09, tp:1.20, result:0, status:'Aberta', openedAt:'2026-08-01T10:00:00.000Z'};
  S.phases[0].orders[1] = {id:'D1', par:'EURUSD', tipo:'BUY', lote:0.05, entry:1.11,
    sl:1.10, tp:1.21, result:-150, status:'Fechada',
    openedAt:'2026-08-02T10:00:00.000Z', closedAt:'2026-08-03T10:00:00.000Z'};
  S.activeOperation = {schemaVersion:1, operationId:'op_r1',
    openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
    maxAccountPhaseReached:0};
  save();
  navigateToScreen('exec'); JPWExec.ui.selectView('motor'); renderPhases();
}"""


def run_committed_breach_is_observed(page):
    """Stop que sobrevive a guarda e fica persistido: a fase e capturada."""
    page.evaluate(CENARIO_R1)
    r = page.evaluate(
        """() => {
          const campo = f => document.querySelector(
            '#phaseContainer input[data-p="0"][data-o="0"][data-f="'+f+'"]');
          const st = () => ({fase:accountPhaseProbe().idx,
                             max:S.activeOperation.maxAccountPhaseReached,
                             sl:S.phases[0].orders[0].sl});
          const inicial = st();
          const sl = campo('sl');
          if (!sl) return {erro:'campo sl ausente'};
          sl.value = '1.05';
          sl.dispatchEvent(new Event('input', {bubbles:true}));
          const aposDigitar = st();
          sl.dispatchEvent(new Event('change', {bubbles:true}));
          return {inicial, aposDigitar, aposCommit: st(), avisos: window.__avisos};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["inicial"] == {"fase": 0, "max": 0, "sl": 1.09}, f"pre-condicao: {r['inicial']}"
    assert r["aposDigitar"]["fase"] == 1, (
        f"o valor digitado nao elevou a fase: {r['aposDigitar']} — sem isso o caso "
        "nao exercita nada"
    )
    assert r["aposDigitar"]["max"] == 0, (
        f"a DIGITACAO contaminou o maximo: {r['aposDigitar']['max']}"
    )
    assert any("acima do limite" in a or "TETO" in a or "Nenhuma fase" in a
               for a in r["avisos"]), f"o breach nao foi sinalizado: {r['avisos']}"
    assert r["aposCommit"]["sl"] == 1.05, (
        f"o stop foi revertido ({r['aposCommit']['sl']}) — o caso testado deixou de "
        "ser 'valor comprometido e persistido'"
    )
    assert r["aposCommit"]["fase"] == 1, f"fase apos o commit: {r['aposCommit']['fase']}"
    assert r["aposCommit"]["max"] == 1, (
        f"o stop ficou COMPROMETIDO e persistido, a conta passou a operar acima do "
        f"teto da fase, e o maximo continuou {r['aposCommit']['max']} — o registro "
        "sairia com integridade 'observed' sobre uma fase que ninguem mediu"
    )


def run_reverted_breach_does_not_contaminate(page):
    """Breach REVERTIDO nao move o maximo: o valor nao sobreviveu a guarda."""
    page.evaluate(CENARIO_R1)
    r = page.evaluate(
        """() => {
          const campo = f => document.querySelector(
            '#phaseContainer input[data-p="0"][data-o="0"][data-f="'+f+'"]');
          const st = () => ({fase:accountPhaseProbe().idx,
                             max:S.activeOperation.maxAccountPhaseReached,
                             entry:S.phases[0].orders[0].entry});
          const inicial = st();
          const en = campo('entry');
          if (!en) return {erro:'campo entry ausente'};
          en.dispatchEvent(new Event('focus', {bubbles:true}));
          en.value = '1.20';
          en.dispatchEvent(new Event('input', {bubbles:true}));
          const aposDigitar = st();
          en.dispatchEvent(new Event('change', {bubbles:true}));
          return {inicial, aposDigitar, aposCommit: st(), avisos: window.__avisos};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["aposDigitar"]["fase"] == 1 and r["aposDigitar"]["max"] == 0, (
        f"a digitacao nao produziu pico transitorio, ou o contaminou: {r['aposDigitar']}"
    )
    assert r["aposCommit"]["entry"] == 1.10, (
        f"o valor NAO foi revertido ({r['aposCommit']['entry']}) — o caso deixou de "
        "ser 'rejeitado e revertido'"
    )
    assert any("TETO DE RISCO" in a for a in r["avisos"]), (
        f"a reversao nao foi sinalizada: {r['avisos']}"
    )
    assert r["aposCommit"]["max"] == 0, (
        f"um valor REVERTIDO contaminou o maximo ({r['aposCommit']['max']}) — a "
        "captura so pode observar o que sobreviveu a guarda"
    )


def run_refused_phase_change_still_observes(page):
    """Confirmacao de mudanca de fase RECUSADA: o stop fica, a fase e observada.

    Ramo distinto do anterior. Aqui check.tipo==='fase' com uma fase que
    suportaria, entao o sistema PEDE a frase de confirmacao; recusada, a fase
    NAO e destravada — mas o stop permanece e e persistido, e a conta opera
    acima do teto. E o caminho que a auditoria apontou como o unico que
    comprometia sem observar.
    """
    r = page.evaluate(
        """() => {
          window.__avisos = [];
          window.alert = m => window.__avisos.push(String(m));
          window.confirm = () => true;
          window.prompt = () => null;          // RECUSA a frase
          S.params.saldoIni = 10000; S.cycleRealizado = -360;
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.phaseUnlocked = [true,false,false,false];
          S.phases[0].orders[0] = {id:'G1', par:'EURUSD', tipo:'BUY', lote:0.05,
            entry:1.10, sl:1.098, tp:1.20, result:0, status:'Aberta',
            openedAt:'2026-08-01T10:00:00.000Z'};
          S.activeOperation = {schemaVersion:1, operationId:'op_r1b',
            openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
            maxAccountPhaseReached:0};
          save();
          navigateToScreen('exec'); JPWExec.ui.selectView('motor'); renderPhases();
          const el = document.querySelector(
            '#phaseContainer input[data-p="0"][data-o="0"][data-f="sl"]');
          if (!el) return {erro:'campo sl ausente'};
          const st = () => ({fase:accountPhaseProbe().idx,
                             max:S.activeOperation.maxAccountPhaseReached,
                             sl:S.phases[0].orders[0].sl,
                             unlocked:S.phaseUnlocked.slice()});
          const inicial = st();
          el.dispatchEvent(new Event('focus', {bubbles:true}));
          el.value = '1.09';
          el.dispatchEvent(new Event('input', {bubbles:true}));
          const check = checkPhaseCap(0,0);
          const aposDigitar = st();
          el.dispatchEvent(new Event('change', {bubbles:true}));
          return {inicial, aposDigitar, check:{excede:check.excede, tipo:check.tipo},
                  suporte: phaseSupportForRisk(check.total),
                  aposCommit: st(), avisos: window.__avisos};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["check"]["excede"] and r["check"]["tipo"] == "fase" and r["suporte"] == 1, (
        f"o cenario nao caiu no ramo de MUDANCA DE FASE: {r['check']}, suporte "
        f"{r['suporte']} — este teste cobre um ramo diferente do limite da Genese"
    )
    assert any("Stop mantido para simulação" in a for a in r["avisos"]), (
        f"o aviso da confirmacao recusada nao apareceu: {r['avisos']}"
    )
    assert r["aposCommit"]["unlocked"] == [True, False, False, False], (
        f"a fase foi destravada apesar da recusa: {r['aposCommit']['unlocked']}"
    )
    assert r["aposCommit"]["sl"] == 1.09, (
        f"o stop foi revertido ({r['aposCommit']['sl']}) — o caso deixou de ser "
        "'valor comprometido'"
    )
    assert r["aposDigitar"]["max"] == 0, "a digitacao contaminou o maximo"
    assert r["aposCommit"]["max"] == 1, (
        f"o maximo continuou {r['aposCommit']['max']} — a confirmacao recusada nao "
        "reverte o stop, a conta opera acima do teto, e ninguem observou"
    )


# ---------------------------------------------------------------------------
# R4 — troca de Par ACEITA observa a Fase da Conta
# ---------------------------------------------------------------------------
# Trocar o instrumento muda orderRisk() tanto quanto mudar o lote: depende de cpl
# e da conversao da moeda de cotacao. A troca aceita e persistida pela saida
# terminal do laco de <select>, que ficou sem captura quando C a tirou de save()
# e a repos so no laco de <input>. A conta subia de fase, recuava depois, e o
# registro imutavel afirmava um maximo INFERIOR ao realmente atingido.

MONTA_R4 = """(cfg) => {
  window.__avisos = [];
  window.alert = m => window.__avisos.push(String(m));
  window.confirm = () => true;
  window.prompt = () => null;
  S.params.saldoIni = 40000; S.cycleRealizado = 0;
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
  S.phaseUnlocked = cfg.unlocked;
  S.phases[cfg.pi].orders[0] = {id:'G1', par:'USDJPY', tipo:'BUY', lote:0.05,
    entry:161.93, sl:161.43, tp:170, result:0, status:'Aberta',
    openedAt:'2026-08-01T10:00:00.000Z'};
  S.activeOperation = {schemaVersion:1, operationId:'op_r4',
    openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
    maxAccountPhaseReached:0};
  save();
  navigateToScreen('exec'); JPWExec.ui.selectView('motor'); renderPhases();
}"""


def run_accepted_pair_change_is_observed(page):
    """Troca aceita que eleva a fase e capturada, e o pico sobrevive ao recuo."""
    page.evaluate(MONTA_R4, {"pi": 1, "unlocked": [True, True, False, False]})
    r = page.evaluate(
        """() => {
          const o = () => S.phases[1].orders[0];
          const st = () => ({fase:accountPhaseProbe().idx,
                             max:S.activeOperation.maxAccountPhaseReached,
                             par:o().par, risco:orderRisk(o())});
          const inicial = {...st(), teto: phaseTetoRisco(1)};
          const sel = document.querySelector(
            '#phaseContainer select[data-p="1"][data-o="0"][data-f="par"]');
          if (!sel) return {erro:'select de par ausente'};
          sel.value = 'EURUSD';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          const aposTroca = st();
          // A conta RECUA: stop estreitado por <input>, que captura.
          const inp = document.querySelector(
            '#phaseContainer input[data-p="1"][data-o="0"][data-f="sl"]');
          if (!inp) return {erro:'input de sl ausente'};
          inp.dispatchEvent(new Event('focus', {bubbles:true}));
          inp.value = '161.92';
          inp.dispatchEvent(new Event('input', {bubbles:true}));
          inp.dispatchEvent(new Event('change', {bubbles:true}));
          return {inicial, aposTroca, aposRecuo: st(), avisos: window.__avisos};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert r["inicial"]["fase"] == 0 and r["inicial"]["max"] == 0, f"pre-condicao: {r['inicial']}"
    assert r["aposTroca"]["par"] == "EURUSD", (
        f"a troca foi revertida ({r['aposTroca']['par']}) — o caso deixou de ser "
        f"'troca aceita'. Risco {r['aposTroca']['risco']} contra teto "
        f"{r['inicial']['teto']}"
    )
    assert not any("TETO DE RISCO" in a for a in r["avisos"]), (
        f"a troca foi barrada: {r['avisos']}"
    )
    assert r["aposTroca"]["fase"] == 1, (
        f"a troca aceita nao elevou a Fase da Conta ({r['aposTroca']}) — sem isso o "
        "teste nao exercita o defeito"
    )
    assert r["aposTroca"]["max"] == 1, (
        f"a troca aceita e PERSISTIDA nao foi observada: maximo continuou "
        f"{r['aposTroca']['max']} com a conta na fase {r['aposTroca']['fase']}"
    )
    assert r["aposRecuo"]["fase"] == 0, (
        f"a conta nao recuou: {r['aposRecuo']} — sem o recuo nao se prova que o "
        "pico foi preservado"
    )
    assert r["aposRecuo"]["max"] == 1, (
        f"o maximo regrediu para {r['aposRecuo']['max']} depois do recuo — o "
        "registro imutavel afirmaria uma fase inferior a realmente atingida"
    )


def run_rejected_pair_change_does_not_contaminate(page):
    """Troca REVERTIDA pelo teto nao move o maximo."""
    page.evaluate(MONTA_R4, {"pi": 0, "unlocked": [True, False, False, False]})
    r = page.evaluate(
        """() => {
          const o = () => S.phases[0].orders[0];
          const st = () => ({fase:accountPhaseProbe().idx,
                             max:S.activeOperation.maxAccountPhaseReached,
                             par:o().par});
          const inicial = {...st(), teto: phaseTetoRisco(0)};
          const sel = document.querySelector(
            '#phaseContainer select[data-p="0"][data-o="0"][data-f="par"]');
          if (!sel) return {erro:'select de par ausente'};
          sel.value = 'EURUSD';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          return {inicial, depois: st(), avisos: window.__avisos};
        }"""
    )
    assert not r.get("erro"), r["erro"]
    assert any("TETO DE RISCO" in a for a in r["avisos"]), (
        f"a troca NAO foi barrada: {r['avisos']} — o caso deixou de ser 'recusada'"
    )
    assert r["depois"]["par"] == "USDJPY", (
        f"a troca recusada nao foi revertida: {r['depois']['par']}"
    )
    assert r["depois"]["max"] == 0, (
        f"uma troca RECUSADA e revertida contaminou o maximo ({r['depois']['max']}) — "
        "a captura so pode observar o que sobreviveu a guarda"
    )


# ---------------------------------------------------------------------------
# Bloco C — resultado da ordem: ausente, invalido e zero sao estados distintos
# ---------------------------------------------------------------------------
# `parseFloat(x)||0` colapsava tres estados num so. Uma ordem fechada sem
# resultado informado entrava em netOpAtual() como zero, e dali no consolidado da
# Operacao Unica e no registro imutavel do Historico — sem ninguem perceber.

MONTA_FECHAMENTO = """() => {
  window.__avisos = [];
  window.alert = m => window.__avisos.push(String(m));
  window.confirm = () => true;
  window.prompt = () => null;
  S.params.saldoIni = 40000; S.cycleRealizado = 0;
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
  S.phaseUnlocked = [true,false,false,false];
  S.phases[0].orders[0] = {id:'G1', par:'EURUSD', tipo:'BUY', lote:0.01,
    entry:1.10, sl:1.09, tp:1.20, status:'Aberta',
    openedAt:'2026-08-01T10:00:00.000Z'};
  delete S.phases[0].orders[0].result;
  S.activeOperation = {schemaVersion:1, operationId:'op_fech',
    openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
    maxAccountPhaseReached:0};
  save();
  navigateToScreen('exec'); JPWExec.ui.selectView('motor'); renderPhases();
}"""


def fecha_pela_ui(page, texto_resultado):
    """Abre o modal real pelo <select> de status e tenta confirmar."""
    return page.evaluate(
        """txt => {
          const sel = document.querySelector(
            '#phaseContainer select[data-p="0"][data-o="0"][data-f="status"]');
          if (!sel) return {erro:'select de status ausente'};
          sel.value = 'Fechada';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          const inp = document.getElementById('closeResultInput');
          if (!inp) return {erro:'modal de fechamento nao abriu'};
          inp.value = txt;
          document.getElementById('closeConfirmInput').value = 'FECHADO';
          document.getElementById('modalConfirm').click();
          const box = document.getElementById('modalBox');
          const erroVisivel = !!box.querySelector('[data-qid="resultado"] .modal-err.show');
          const o = S.phases[0].orders[0];
          return {erroVisivel,
                  aindaAberto: document.getElementById('modalOverlay').classList.contains('show'),
                  status: o.status,
                  result: Number.isFinite(o.result) ? o.result : null,
                  tipoResult: typeof o.result,
                  net: netOpAtual()};
        }""", texto_resultado)


def run_blank_result_blocks_close(page):
    """Resultado em branco NAO fecha a ordem, e nao vira zero."""
    page.evaluate(MONTA_FECHAMENTO)
    r = fecha_pela_ui(page, "")
    assert not r.get("erro"), r["erro"]
    assert r["erroVisivel"], "o campo de resultado nao acusou a ausencia"
    assert r["aindaAberto"], "o modal fechou apesar da recusa"
    assert r["status"] != "Fechada", (
        f"a ordem FECHOU sem resultado informado (status {r['status']!r})"
    )
    assert r["result"] is None, (
        f"resultado em branco virou {r['result']!r} — ausencia nao e zero, e esse "
        "zero entraria em netOpAtual() e no registro imutavel"
    )
    assert r["net"] == 0, f"netOpAtual contaminado: {r['net']}"


def run_invalid_result_blocks_close(page):
    """Texto invalido nao fecha — inclusive o que parseFloat aceitaria PELA METADE.

    "abc" e o caso facil: parseFloat tambem devolve NaN. O perigoso e o parse
    PARCIAL, que a regex existe para barrar:

        "1.420,50"  separador de milhar  -> parseFloat da 1.42   (erro de 1000x)
        "1.2.3"                          -> parseFloat da 1.2
        "12abc"                          -> parseFloat da 12

    Nesses, um `parseFloat` sozinho grava um numero PLAUSIVEL e errado num campo
    que alimenta a consolidacao e o registro imutavel. Sem eles, uma mutacao que
    remove a regex sobrevive.
    """
    for txt in ["abc", "1.2.3", "12abc", "1.420,50", "--5", "R$ 500"]:
        page.evaluate(MONTA_FECHAMENTO)
        r = fecha_pela_ui(page, txt)
        assert not r.get("erro"), r["erro"]
        assert r["erroVisivel"], f"{txt!r}: entrada invalida nao foi acusada"
        assert r["status"] != "Fechada", (
            f"{txt!r}: a ordem FECHOU com entrada invalida (status {r['status']!r})"
        )
        assert r["result"] is None, (
            f"{txt!r}: virou {r['result']!r} — um numero plausivel e errado entraria "
            "na consolidacao e no registro imutavel"
        )
        assert r["net"] == 0, f"{txt!r}: netOpAtual contaminado ({r['net']})"


def run_explicit_zero_is_a_valid_result(page):
    """Zero DIGITADO e afirmacao do operador: fecha e vale zero."""
    page.evaluate(MONTA_FECHAMENTO)
    r = fecha_pela_ui(page, "0")
    assert not r.get("erro"), r["erro"]
    assert not r["erroVisivel"], "zero explicito foi tratado como ausencia"
    assert r["status"] == "Fechada", f"zero explicito nao fechou a ordem: {r['status']!r}"
    assert r["result"] == 0 and r["tipoResult"] == "number", (
        f"zero explicito nao foi gravado como numero: {r['result']!r} ({r['tipoResult']})"
    )
    assert not r["aindaAberto"], "o modal nao fechou apos o sucesso"


def run_negative_and_positive_results_are_accepted(page):
    """Negativo e positivo fecham normalmente, com o sinal preservado."""
    page.evaluate(MONTA_FECHAMENTO)
    neg = fecha_pela_ui(page, "-500")
    assert neg["status"] == "Fechada" and neg["result"] == -500, (
        f"resultado negativo nao foi aceito: {neg}"
    )
    assert neg["net"] == -500, f"netOpAtual nao refletiu o prejuizo: {neg['net']}"

    page.evaluate(MONTA_FECHAMENTO)
    pos = fecha_pela_ui(page, "1420,50")
    assert pos["status"] == "Fechada" and pos["result"] == 1420.5, (
        f"resultado positivo com virgula decimal nao foi aceito: {pos}"
    )


def main():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            run_par_excedente_e_barrado(page)
            run_par_dentro_do_teto_passa(page)
            # ---- Operacao Unica Exclusiva (#7) ----
            run_exclusividade_barra_outro_instrumento(page)
            run_exclusividade_barra_direcao_contraria(page)
            run_exclusividade_permite_mesma_tese(page)
            run_rascunho_nao_constitui_tese(page)
            run_exclusividade_termina_na_finalizacao(page)
            run_estado_legado_conflitado_segue_bloqueado(page)
            # ---- R1: breach comprometido observa a Fase da Conta ----
            run_committed_breach_is_observed(page)
            run_reverted_breach_does_not_contaminate(page)
            run_refused_phase_change_still_observes(page)
            # ---- R4: troca de Par aceita observa a Fase da Conta ----
            run_accepted_pair_change_is_observed(page)
            run_rejected_pair_change_does_not_contaminate(page)
            # ---- Bloco C: ausente != invalido != zero ----
            run_blank_result_blocks_close(page)
            run_invalid_result_blocks_close(page)
            run_explicit_zero_is_a_valid_result(page)
            run_negative_and_positive_results_are_accepted(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("ORDER GUARDS TEST PASS")


if __name__ == "__main__":
    main()
