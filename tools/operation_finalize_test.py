#!/usr/bin/env python3
"""Caracterizacao da Camada 2 — Finalizacao transacional da Operacao Unica.

O criterio critico deste teste nao e "funciona quando da certo". E o que
acontece quando NAO da: uma falha de persistencia no ponto relevante da
transacao nao pode deixar grade zerada, cycleRealizado incrementado nem
historico pela metade.

A falha e injetada onde ela realmente ocorre — no portao de persistencia que o
proprio projeto usa (jpWealthPersistenceBlocked) — e nao lancando uma excecao
antes da fase critica, que provaria apenas que o teste sabe lancar.

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
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.route(
        "**/*",
        lambda route: route.continue_()
        if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_function("() => !!window.JPWOperation && typeof save === 'function'")
    return context, page, observed


# Fixture: operacao encerrada (duas ordens fechadas, nenhuma aberta), com
# identidade e abertura conhecidas.
SEMEAR = """
  window.__semear = (opts) => {
    opts = opts || {};
    S.params.saldoIni = 10000;
    S.cycleRealizado = opts.ciclo === undefined ? 250 : opts.ciclo;
    S.operationHistory = {schemaVersion:1, records: opts.records || []};
    S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
    S.phases[0].orders[0] = {id:'G1',par:'EURUSD',tipo:'BUY',lote:1,entry:1.10,sl:1.09,tp:1.20,
                             result:400,status:'Fechada',openedAt:'2026-08-01T10:00:00.000Z',
                             closedAt:'2026-08-05T15:00:00.000Z'};
    S.phases[1].orders[0] = {id:'D1',par:'EURUSD',tipo:'BUY',lote:1,entry:1.11,sl:1.10,tp:1.21,
                             result:-150,status:'Fechada',openedAt:'2026-08-02T11:00:00.000Z',
                             closedAt:'2026-08-04T12:00:00.000Z'};
    if (opts.aberta) S.phases[0].orders[1] = {id:'A1',par:'EURUSD',tipo:'BUY',lote:1,entry:1.12,
                             sl:1.11,tp:1.22,result:0,status:'Aberta'};
    S.phaseUnlocked = [true,true,false,false];
    S.activeOperation = opts.semEntidade ? null : {
      schemaVersion:1, operationId: opts.id || 'op_fixture',
      openedAt: opts.openedAt === undefined ? '2026-08-01T10:00:00.000Z' : opts.openedAt,
      openedAtSource: opts.openedAt === null ? null : 'genesis_transition',
      maxAccountPhaseReached: opts.maxFase === undefined ? 1 : opts.maxFase,
      ...(opts.fault ? {phaseCaptureFault:{at:'2026-08-03T00:00:00.000Z', reason:'falha X'}} : {})
    };
  };
"""


def run_blocks_open_position(page):
    """Posicao aberta BLOQUEIA. Sem bypass."""
    r = page.evaluate("() => { __semear({aberta:true}); return JPWOperation.canFinalize(); }")
    assert r["ok"] is False and r["motivo"] == "open_position", f"posicao aberta nao bloqueou: {r}"
    r2 = page.evaluate("() => JPWOperation.finalize({defenseCount:0})")
    assert r2["ok"] is False and r2["motivo"] == "open_position", (
        f"finalize ignorou o bloqueio: {r2}"
    )


def run_blocks_empty(page):
    """Grade vazia nao oferece o que finalizar."""
    r = page.evaluate(
        """() => {
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          return JPWOperation.canFinalize();
        }"""
    )
    assert r["ok"] is False and r["motivo"] == "no_operation", f"grade vazia passou: {r}"


def run_success_path(page):
    """Sucesso: 1 registro, ciclo consolidado UMA vez, grades zeradas, entidade limpa."""
    r = page.evaluate(
        """() => {
          __semear({ciclo:250});
          const cicloAntes = S.cycleRealizado;
          const net = netOpAtual();
          const res = JPWOperation.finalize({defenseCount:2});
          return {
            res, cicloAntes, net,
            cicloDepois: S.cycleRealizado,
            registros: S.operationHistory.records.length,
            registro: S.operationHistory.records[0],
            activeOperation: S.activeOperation,
            ordensVivas: JPWOperation.liveOrders().length,
            phaseUnlocked: S.phaseUnlocked,
            ultimoLog: S.transitionLog[S.transitionLog.length-1]
          };
        }"""
    )
    assert r["res"]["ok"] is True, f"finalizacao falhou: {r['res']}"
    assert r["net"] == 250, f"resultado canonico inesperado: {r['net']}"
    assert r["cicloDepois"] == r["cicloAntes"] + r["net"], (
        f"cycleRealizado nao consolidou exatamente uma vez: "
        f"{r['cicloAntes']} + {r['net']} != {r['cicloDepois']}"
    )
    assert r["registros"] == 1, f"registros no historico: {r['registros']}"
    assert r["activeOperation"] is None, "activeOperation nao foi limpa"
    assert r["ordensVivas"] == 0, f"grade nao foi zerada: {r['ordensVivas']} ordens"
    assert r["phaseUnlocked"] == [True, False, False, False], (
        f"fases nao foram retravadas: {r['phaseUnlocked']}"
    )
    reg = r["registro"]
    assert reg["instrument"] == "EURUSD" and reg["direction"] == "BUY", f"tese perdida: {reg}"
    assert reg["netResult"] == 250, f"netResult divergente: {reg['netResult']}"
    assert reg["referenceBalance"] == 10000, f"base do retorno nao congelada: {reg}"
    assert reg["referenceBalanceType"] == "cycle_initial_balance"
    assert reg["closedAtSource"] == "formal_confirmation"
    assert reg["defenseCount"] == 2 and reg["defenseCountSource"] == "manual"
    assert len(reg["ordersSnapshot"]) == 2, f"ordens nao copiadas: {reg['ordersSnapshot']}"
    assert reg["maxAccountPhaseIntegrity"] == "observed", reg["maxAccountPhaseIntegrity"]
    assert r["ultimoLog"]["fase"] == "operação finalizada", r["ultimoLog"]


def run_idempotency(page):
    """Mesmo operationId ja no historico: nada acontece de novo."""
    r = page.evaluate(
        """() => {
          __semear({id:'op_dup', records:[{schemaVersion:1, operationId:'op_dup', ordersSnapshot:[]}], ciclo:100});
          const antes = {ciclo:S.cycleRealizado, n:S.operationHistory.records.length,
                         ordens:JPWOperation.liveOrders().length};
          const res = JPWOperation.finalize({defenseCount:0});
          return {res, antes, depois:{ciclo:S.cycleRealizado, n:S.operationHistory.records.length,
                  ordens:JPWOperation.liveOrders().length}};
        }"""
    )
    assert r["res"]["ok"] is False and r["res"]["motivo"] == "already_finalized", (
        f"segunda finalizacao foi aceita: {r['res']}"
    )
    assert r["antes"] == r["depois"], (
        f"estado mudou apesar da rejeicao: {r['antes']} -> {r['depois']} — "
        "duplo disparo duplicaria consolidacao"
    )


def run_persistence_failure_rollback(page):
    """CRITICO: falha de persistencia nao pode destruir a operacao viva."""
    r = page.evaluate(
        """() => {
          __semear({ciclo:777});
          const antes = {
            ciclo: S.cycleRealizado,
            registros: S.operationHistory.records.length,
            ordens: JPWOperation.liveOrders().length,
            opId: S.activeOperation.operationId,
            phaseUnlocked: JSON.parse(JSON.stringify(S.phaseUnlocked))
          };
          // Falha no PONTO relevante: o portao de persistencia do proprio
          // projeto. save() devolve false exatamente como no modo de
          // recuperacao A-005 ou com armazenamento bloqueado.
          jpWealthPersistenceBlocked = true;
          const res = JPWOperation.finalize({defenseCount:1});
          jpWealthPersistenceBlocked = false;
          const depois = {
            ciclo: S.cycleRealizado,
            registros: S.operationHistory.records.length,
            ordens: JPWOperation.liveOrders().length,
            opId: S.activeOperation && S.activeOperation.operationId,
            phaseUnlocked: JSON.parse(JSON.stringify(S.phaseUnlocked))
          };
          return {res, antes, depois};
        }"""
    )
    assert r["res"]["ok"] is False and r["res"]["motivo"] == "persist_failed", (
        f"falha de persistencia nao foi reportada: {r['res']}"
    )
    a, d = r["antes"], r["depois"]
    assert d["ordens"] == a["ordens"], f"GRADE FOI ZERADA apesar da falha: {a['ordens']} -> {d['ordens']}"
    assert d["ciclo"] == a["ciclo"], f"cycleRealizado consolidou apesar da falha: {a['ciclo']} -> {d['ciclo']}"
    assert d["registros"] == a["registros"], f"historico recebeu registro parcial: {d['registros']}"
    assert d["opId"] == a["opId"], f"identidade da operacao viva se perdeu: {a['opId']} -> {d['opId']}"
    assert d["phaseUnlocked"] == a["phaseUnlocked"], "fases foram retravadas apesar da falha"


def run_save_hook_never_resurrects(page):
    """O gancho centralizado em save() nao pode ressuscitar a operacao."""
    r = page.evaluate(
        """() => {
          __semear({});
          const res = JPWOperation.finalize({defenseCount:0});
          // Varios save() apos a finalizacao: nenhum pode recriar entidade
          // nem gerar identidade nova.
          save(); save(); save();
          return {ok:res.ok, activeOperation:S.activeOperation,
                  ordens:JPWOperation.liveOrders().length};
        }"""
    )
    assert r["ok"] is True, "fixture nao finalizou"
    assert r["activeOperation"] is None, (
        f"save() RESSUSCITOU a operacao apos a finalizacao: {r['activeOperation']} — "
        "risco criado pela centralizacao do gancho em save()"
    )
    assert r["ordens"] == 0, "grade voltou a ter ordens"


def run_snapshot_is_independent(page):
    """Snapshot nao pode COMPARTILHAR OBJETO com a ordem viva.

    A verificacao por JSON depois da finalizacao seria vazia: a transacao troca
    o estado inteiro, entao as ordens vivas novas nao sao as mesmas que o
    registro aponta e a comparacao passaria mesmo com referencia compartilhada.
    Foi tentando plantar esse defeito que a fraqueza apareceu. Aqui a identidade
    de objeto e testada NO ATO DA CONSTRUCAO, que e onde o risco existe, e
    depois se muta a ordem viva para provar que o registro nao acompanha.
    """
    r = page.evaluate(
        """() => {
          __semear({});
          const vivas = JPWOperation.liveOrders();
          const snap = JPWOperation.buildSnapshot(S.activeOperation, {defenseCount:0});
          const compartilhaObjeto = snap.record.ordersSnapshot.some(
            linha => vivas.some(v => v.o === linha));
          // Mutar a ordem VIVA que originou a primeira linha do snapshot.
          const resultAntes = snap.record.ordersSnapshot[0].result;
          vivas[0].o.result = 999999;
          const resultDepois = snap.record.ordersSnapshot[0].result;
          return {compartilhaObjeto, resultAntes, resultDepois};
        }"""
    )
    assert r["compartilhaObjeto"] is False, (
        "o snapshot guarda A PROPRIA ordem viva — alterar a operacao seguinte "
        "reescreveria a memoria historica da anterior"
    )
    assert r["resultDepois"] == r["resultAntes"], (
        f"mutar a ordem viva alterou o snapshot: {r['resultAntes']} -> {r['resultDepois']}"
    )


def run_return_is_frozen(page):
    """Retorno historico nao pode depender do saldo atual."""
    r = page.evaluate(
        """() => {
          __semear({});
          JPWOperation.finalize({defenseCount:0});
          const reg = S.operationHistory.records[0];
          const base1 = reg.referenceBalance;
          const ret1 = reg.netResult / reg.referenceBalance;
          S.params.saldoIni = 999999;   // saldo atual muda
          save();
          const r2 = S.operationHistory.records[0];
          return {base1, base2:r2.referenceBalance, ret1, ret2: r2.netResult / r2.referenceBalance};
        }"""
    )
    assert r["base1"] == r["base2"], f"base do retorno mudou com o saldo atual: {r}"
    assert abs(r["ret1"] - r["ret2"]) < 1e-12, f"retorno historico mudou: {r}"


def run_degraded_integrity_preserved(page):
    """phaseCaptureFault viaja para o snapshot e nao bloqueia a finalizacao."""
    r = page.evaluate(
        """() => {
          __semear({fault:true, maxFase:2});
          const res = JPWOperation.finalize({defenseCount:0});
          const reg = S.operationHistory.records[0];
          return {ok:res.ok, integridade:reg.maxAccountPhaseIntegrity,
                  max:reg.maxAccountPhaseReached, fault:reg.phaseCaptureFault};
        }"""
    )
    assert r["ok"] is True, "fault bloqueou a finalizacao — evidencia auxiliar nao pode impedir encerrar"
    assert r["integridade"] == "degraded", f"integridade nao foi marcada: {r['integridade']!r}"
    assert r["max"] == 2, f"valor conhecido foi descartado ou zerado: {r['max']!r}"
    assert r["fault"] and r["fault"]["reason"], f"evidencia da lacuna se perdeu: {r['fault']}"


def run_thesis_conflict_reported(page):
    """Instrumento divergente e REPORTADO, nunca escolhido em silencio."""
    r = page.evaluate(
        """() => {
          __semear({});
          S.phases[1].orders[0].par = 'GBPUSD';
          const res = JPWOperation.finalize({defenseCount:0});
          return {res, registros:S.operationHistory.records.length};
        }"""
    )
    assert r["res"]["ok"] is False and r["res"]["motivo"] == "instrument_conflict", (
        f"conflito de instrumento resolvido em silencio: {r['res']}"
    )
    assert r["registros"] == 0, "registro criado apesar do conflito"


# ---- Camada 2B — superficie de revisao ----

FOTO_FINANCEIRA = """
  window.__foto = () => JSON.stringify({
    ciclo: S.cycleRealizado,
    registros: (S.operationHistory.records||[]).length,
    ordens: JPWOperation.liveOrders().length,
    opId: S.activeOperation && S.activeOperation.operationId,
    phaseUnlocked: S.phaseUnlocked,
    logs: S.transitionLog.length
  });
"""


def run_modal_opens_without_mutation(page):
    """Abrir a revisao nao pode mutar nada."""
    r = page.evaluate(
        """() => {
          __semear({});
          const antes = __foto();
          JPWOperation.openReview();
          const aberto = document.getElementById('modalOverlay').classList.contains('show');
          const temConfirm = !!document.getElementById('finalConfirm');
          const depois = __foto();
          closeModal();
          return {antes, depois, aberto, temConfirm};
        }"""
    )
    assert r["aberto"] and r["temConfirm"], "modal de revisao nao abriu"
    assert r["antes"] == r["depois"], f"abrir o modal MUTOU estado: {r['antes']} -> {r['depois']}"


def run_modal_cancel_no_mutation(page):
    """Cancelar nao muta."""
    r = page.evaluate(
        """() => {
          __semear({});
          const antes = __foto();
          JPWOperation.openReview();
          document.getElementById('modalCancel').click();
          return {antes, depois: __foto(),
                  fechado: !document.getElementById('modalOverlay').classList.contains('show')};
        }"""
    )
    assert r["fechado"], "cancelar nao fechou o modal"
    assert r["antes"] == r["depois"], f"cancelar mutou estado: {r['antes']} -> {r['depois']}"


def run_wrong_confirmation_no_mutation(page):
    """FECHADO incorreto nao finaliza."""
    r = page.evaluate(
        """() => {
          __semear({});
          const antes = __foto();
          JPWOperation.openReview();
          document.getElementById('finalDefenses').value = '1';
          document.getElementById('finalConfirm').value = 'fechado';   // minusculo
          document.getElementById('modalConfirm').click();
          const aindaAberto = document.getElementById('modalOverlay').classList.contains('show');
          const err = document.querySelector('[data-qid="confirmtxt"] .modal-err').classList.contains('show');
          const depois = __foto();
          closeModal();
          return {antes, depois, aindaAberto, err};
        }"""
    )
    assert r["antes"] == r["depois"], f"confirmacao errada MUTOU estado: {r['antes']} -> {r['depois']}"
    assert r["aindaAberto"], "modal fechou apesar da confirmacao invalida"
    assert r["err"], "erro de confirmacao nao foi sinalizado"


def run_empty_defenses_is_not_zero(page):
    """Campo vazio NAO vira 0 em silencio; 0 digitado e legitimo."""
    vazio = page.evaluate(
        """() => {
          __semear({});
          const antes = __foto();
          JPWOperation.openReview();
          document.getElementById('finalConfirm').value = 'FECHADO';
          // defesas deixado VAZIO de proposito
          document.getElementById('modalConfirm').click();
          const err = document.querySelector('[data-qid="defesas"] .modal-err').classList.contains('show');
          const depois = __foto();
          closeModal();
          return {antes, depois, err, valorInicial: 0};
        }"""
    )
    assert vazio["antes"] == vazio["depois"], (
        "campo de defesas VAZIO finalizou a operacao — zero defesas e uma afirmacao "
        "do operador, nao um default silencioso"
    )
    assert vazio["err"], "campo vazio nao foi sinalizado como invalido"

    zero = page.evaluate(
        """() => {
          __semear({});
          JPWOperation.openReview();
          document.getElementById('finalDefenses').value = '0';
          document.getElementById('finalConfirm').value = 'FECHADO';
          document.getElementById('modalConfirm').click();
          const reg = S.operationHistory.records[0];
          return {n: S.operationHistory.records.length,
                  defesas: reg && reg.defenseCount, fonte: reg && reg.defenseCountSource};
        }"""
    )
    assert zero["n"] == 1, f"0 informado nao finalizou: {zero}"
    assert zero["defesas"] == 0 and zero["fonte"] == "manual", (
        f"zero informado nao foi persistido como tal: {zero}"
    )


def run_legacy_requires_manual_date(page):
    """Legado sem openedAt exige data no proprio modal."""
    r = page.evaluate(
        """() => {
          __semear({openedAt:null});
          const antes = __foto();
          JPWOperation.openReview();
          const temCampo = !!document.getElementById('finalOpenedAt');
          document.getElementById('finalDefenses').value = '0';
          document.getElementById('finalConfirm').value = 'FECHADO';
          document.getElementById('modalConfirm').click();   // sem informar a data
          const err = document.querySelector('[data-qid="abertura"] .modal-err').classList.contains('show');
          const depois = __foto();
          // agora com data valida
          document.getElementById('finalOpenedAt').value = '2026-08-01T10:00';
          document.getElementById('modalConfirm').click();
          const reg = S.operationHistory.records[0];
          return {temCampo, err, antes, depois,
                  n:S.operationHistory.records.length,
                  fonte: reg && reg.openedAtSource, abertura: reg && reg.openedAt};
        }"""
    )
    assert r["temCampo"], "modal nao ofereceu campo de abertura para operacao legada"
    assert r["err"], "data ausente nao foi sinalizada"
    assert r["antes"] == r["depois"], "finalizou sem a data obrigatoria"
    assert r["n"] == 1, f"nao finalizou com data valida: {r}"
    assert r["fonte"] == "manual_legacy", f"proveniencia errada: {r['fonte']!r}"
    assert r["abertura"], "abertura informada nao foi persistida"


def run_degraded_shown_in_review(page):
    """Integridade degradada aparece na revisao e nao bloqueia."""
    r = page.evaluate(
        """() => {
          __semear({fault:true, maxFase:2});
          JPWOperation.openReview();
          const bloco = document.querySelector('[data-qid="integridade"]');
          const txt = bloco ? bloco.textContent : '';
          document.getElementById('finalDefenses').value = '0';
          document.getElementById('finalConfirm').value = 'FECHADO';
          document.getElementById('modalConfirm').click();
          return {mostrou: !!bloco, txt, n: S.operationHistory.records.length};
        }"""
    )
    assert r["mostrou"], "integridade degradada nao foi mostrada na revisao"
    assert "Degradada" in r["txt"], f"aviso sem o termo esperado: {r['txt'][:120]}"
    assert r["n"] == 1, "a marca de degradacao bloqueou a finalizacao"


def run_persist_failure_keeps_modal(page):
    """save() false: modal NAO comunica sucesso e a operacao continua viva."""
    r = page.evaluate(
        """() => {
          __semear({});
          const antes = __foto();
          JPWOperation.openReview();
          document.getElementById('finalDefenses').value = '0';
          document.getElementById('finalConfirm').value = 'FECHADO';
          jpWealthPersistenceBlocked = true;
          document.getElementById('modalConfirm').click();
          jpWealthPersistenceBlocked = false;
          const aberto = document.getElementById('modalOverlay').classList.contains('show');
          const falha = document.getElementById('finalFail');
          const ctaLiberado = !document.getElementById('modalConfirm').disabled;
          const depois = __foto();
          closeModal();
          return {antes, depois, aberto, msg: falha ? falha.textContent : '', ctaLiberado};
        }"""
    )
    assert r["antes"] == r["depois"], f"falha de persistencia mutou estado: {r['antes']} -> {r['depois']}"
    assert r["aberto"], "modal fechou comunicando sucesso apesar de save() ter falhado"
    assert r["msg"], "falha nao foi comunicada ao operador"
    assert r["ctaLiberado"], "CTA ficou travado apos a falha — operador nao poderia tentar de novo"


def run_double_click_single_finalization(page):
    """Dois cliques rapidos: uma finalizacao."""
    r = page.evaluate(
        """() => {
          __semear({ciclo:500});
          const cicloAntes = S.cycleRealizado;
          const net = netOpAtual();
          JPWOperation.openReview();
          document.getElementById('finalDefenses').value = '0';
          document.getElementById('finalConfirm').value = 'FECHADO';
          const btn = document.getElementById('modalConfirm');
          btn.click(); btn.click(); btn.click();
          return {n: S.operationHistory.records.length,
                  ciclo: S.cycleRealizado, esperado: cicloAntes + net};
        }"""
    )
    assert r["n"] == 1, f"duplo clique criou {r['n']} registros"
    assert r["ciclo"] == r["esperado"], (
        f"duplo clique consolidou mais de uma vez: {r['ciclo']} != {r['esperado']}"
    )


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            page.evaluate(SEMEAR)
            page.evaluate(FOTO_FINANCEIRA)
            run_blocks_open_position(page)
            run_blocks_empty(page)
            run_success_path(page)
            run_idempotency(page)
            run_persistence_failure_rollback(page)
            run_save_hook_never_resurrects(page)
            run_snapshot_is_independent(page)
            run_return_is_frozen(page)
            run_degraded_integrity_preserved(page)
            run_thesis_conflict_reported(page)
            # ---- Camada 2B ----
            run_modal_opens_without_mutation(page)
            run_modal_cancel_no_mutation(page)
            run_wrong_confirmation_no_mutation(page)
            run_empty_defenses_is_not_zero(page)
            run_legacy_requires_manual_date(page)
            run_degraded_shown_in_review(page)
            run_persist_failure_keeps_modal(page)
            run_double_click_single_finalization(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("OPERATION FINALIZE TEST PASS")


if __name__ == "__main__":
    main()
