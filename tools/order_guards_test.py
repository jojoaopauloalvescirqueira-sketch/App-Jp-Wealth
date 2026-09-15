#!/usr/bin/env python3
"""V11 recording guards: structural validation survives; eligibility is a finding.
Old cap, questionnaire and exclusive-thesis veto oracles were superseded by
CHG-FOREX-V11-CENTRAL-20260914; original sources remain in external evidence.
Results still distinguish absent, invalid and explicit zero, through real UI.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

import notes_launcher_test as launcher
import forex_recording_test as recording

def record_fixture(page):
    page.evaluate("""() => {
      const keys=[...document.querySelectorAll('[data-eb-row].eb-dirty')].map(e=>e.dataset.ebRow);
      for(const k of keys)document.querySelector('[data-eb-cancel-row="'+k+'"]')?.click();
      closeModal();
    }""")
    recording.seed(page)
    page.evaluate("() => {JPWExec.ui.selectView('panel');renderPhases();}")
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
    context = browser.new_context(viewport={"width":1440,"height":900}, service_workers="block", reduced_motion="reduce")
    page, observed = launcher.prepare(context, url)
    page.evaluate("() => {window.confirm=()=>true;window.prompt=()=> 'Correção sintética justificada';}")
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
    before=launcher.snapshot(page)
    page.evaluate(
        """d => { const sel = document.querySelector('#phaseContainer select[data-f="par"]');
                  if (!sel) throw new Error('select de par nao encontrado na grade');
                  sel.value = d; sel.dispatchEvent(new Event('change', {bubbles:true})); }""",
        destino,
    )
    launcher.unchanged(page,before,'Changing the instrument only updates the row draft')
    page.evaluate("""() => {
      const reason=document.querySelector('[data-eb-reason="0:0"]');
      if(!reason)throw Error('Motivo da linha nao encontrado');
      reason.value='Correção sintética justificada';reason.dispatchEvent(new Event('input',{bubbles:true}));
      document.querySelector('[data-eb-save-row="0:0"]').click();
    }""")
    page.wait_for_timeout(200)


def run_par_excedente_e_barrado(page):
    """V11: trocar par com risco elevado registra o fato e não destrava grades."""
    record_fixture(page)
    page.evaluate("() => {operationRecordOrder(0,0,__fact({lote:999}),{reason:'Execução excedente'});renderPhases();}")
    before=page.evaluate('JSON.stringify(S.phaseUnlocked)')
    troca_par(page,'GBPUSD')
    r=page.evaluate('S.phases[0].orders[0]')
    assert r['par']=='GBPUSD' and r['lote']==999 and r['recordVersion']==2,r
    assert page.evaluate('JSON.stringify(S.phaseUnlocked)')==before


def run_par_dentro_do_teto_passa(page):
    record_fixture(page)
    page.evaluate("() => {operationRecordOrder(0,0,__fact({lote:0.01}),{reason:'Execução'});renderPhases();}")
    troca_par(page,'USDJPY')
    assert page.evaluate('S.phases[0].orders[0].par')=='USDJPY'


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
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
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
          const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY);
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          if(before!==JSON.stringify(S)||raw!==localStorage.getItem(LSKEY))throw Error('Status gravou antes de Salvar linha');
          const reason=document.querySelector('[data-eb-reason="0:'+oi+'"]');
          reason.value='Abertura sintética confirmada';reason.dispatchEvent(new Event('input',{bubbles:true}));
          document.querySelector('[data-eb-save-row="0:'+oi+'"]').click();
          return {desabilitado:false,valorNoSelect:sel.value};
        }""", oi)


def _monta(page, par=None, tipo=None):
    page.evaluate(CENARIO_EXCLUSIVIDADE, {"par": par, "tipo": tipo} if par else {})
    instrumenta_confirmacoes(page)


def run_exclusividade_barra_outro_instrumento(page):
    record_fixture(page)
    r=page.evaluate("() => {operationRecordOrder(0,0,__fact(),{reason:'A'});const saved=operationRecordOrder(0,1,__fact({par:'GBPUSD'}),{reason:'B'});return {saved,findings:orderComplianceFindings()};}")
    assert r['saved']['ok'] and any(f['code']=='INSTRUMENT_CONFLICT' for f in r['findings']),r


def run_exclusividade_barra_direcao_contraria(page):
    record_fixture(page)
    r=page.evaluate("() => {operationRecordOrder(0,0,__fact(),{reason:'A'});const saved=operationRecordOrder(0,1,__fact({tipo:'SELL'}),{reason:'B'});return {saved,findings:orderComplianceFindings()};}")
    assert r['saved']['ok'] and any(f['code']=='DIRECTION_CONFLICT' for f in r['findings']),r


def run_exclusividade_permite_mesma_tese(page):
    record_fixture(page)
    r=page.evaluate("() => {const a=operationRecordOrder(0,0,__fact(),{reason:'A'}),b=operationRecordOrder(0,1,__fact(),{reason:'B'});return {a,b,thesis:operationResolveThesis(operationLiveOrders())};}")
    assert r['a']['ok'] and r['b']['ok'] and not r['thesis']['findings'],r


def run_exclusividade_termina_na_finalizacao(page):
    record_fixture(page)
    recording.conflicted_finalization(page)
    r=page.evaluate("() => {const saved=operationRecordOrder(0,0,__fact({par:'USDJPY'}),{reason:'Nova operação'});return {saved,history:S.operationHistory.records.length,live:operationLiveOrders().length};}")
    assert r['saved']['ok'] and r['history']==1 and r['live']==1,r


def run_estado_legado_conflitado_segue_bloqueado(page):
    record_fixture(page)
    recording.conflicted_finalization(page)


def run_rascunho_nao_constitui_tese(page):
    record_fixture(page)
    r=page.evaluate("() => {const a=operationRecordOrder(0,0,{par:'GBPUSD',tipo:'SELL'},{reason:'Rascunho'});return {a,op:S.activeOperation,live:operationLiveOrders().length};}")
    assert r['a']['ok'] and r['op'] is None and r['live']==0,r


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
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
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
  navigateToScreen('exec'); JPWExec.ui.selectView('panel'); renderPhases();
}"""


def run_committed_breach_is_observed(page):
    record_fixture(page)
    r=page.evaluate("() => {operationRecordOrder(0,0,__fact({lote:999}),{reason:'Fato excedente'});return {max:S.activeOperation.maxAccountPhaseReached,context:S.phases[0].orders[0].revisions[0].context,phase:JPWForex.state.read().accountPhase};}")
    assert r['max'] is None and r['context']['accountInputs'] is None,r
    assert r['phase']['status']!='OK',r


def run_reverted_breach_does_not_contaminate(page):
    record_fixture(page)
    recording.malformed_refused(page)


def run_refused_phase_change_still_observes(page):
    record_fixture(page)
    r=page.evaluate("() => {operationRecordOrder(0,0,__fact(),{reason:'Fato'});const before=JSON.stringify(S.phaseUnlocked),saved=operationRecordOrder(0,0,{sl:0},{reason:'Stop removido na execução'});return {saved,unlocks:before===JSON.stringify(S.phaseUnlocked),sl:S.phases[0].orders[0].sl};}")
    assert r['saved']['ok'] and r['unlocks'] and r['sl']==0,r


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
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
  S.phaseUnlocked = cfg.unlocked;
  S.phases[cfg.pi].orders[0] = {id:'G1', par:'USDJPY', tipo:'BUY', lote:0.05,
    entry:161.93, sl:161.43, tp:170, result:0, status:'Aberta',
    openedAt:'2026-08-01T10:00:00.000Z'};
  S.activeOperation = {schemaVersion:1, operationId:'op_r4',
    openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
    maxAccountPhaseReached:0};
  save();
  navigateToScreen('exec'); JPWExec.ui.selectView('panel'); renderPhases();
}"""


def run_accepted_pair_change_is_observed(page):
    record_fixture(page)
    page.evaluate("() => {operationRecordOrder(0,0,__fact(),{reason:'Fato'});renderPhases();}")
    troca_par(page,'USDJPY')
    r=page.evaluate('S.phases[0].orders[0]')
    assert r['revisions'][-1]['after']['par']=='USDJPY' and r['revisions'][-1]['before']['par']=='EURUSD',r


def run_rejected_pair_change_does_not_contaminate(page):
    record_fixture(page)
    page.evaluate("() => {operationRecordOrder(0,0,__fact(),{reason:'Fato'});renderPhases();}")
    before=launcher.snapshot(page)
    troca_par(page,'')
    launcher.unchanged(page,before,'missing instrument refuses without write')


# ---------------------------------------------------------------------------
# Bloco C — resultado da ordem: ausente, invalido e zero sao estados distintos
# ---------------------------------------------------------------------------
# `parseFloat(x)||0` colapsava tres estados num so. Uma ordem fechada sem
# resultado informado entrava em netOpAtual() como zero, e dali no consolidado da
# Operacao Unica e no registro imutavel do Historico — sem ninguem perceber.

MONTA_FECHAMENTO = """() => {
  const keys=[...document.querySelectorAll('[data-eb-row].eb-dirty')].map(e=>e.dataset.ebRow);
  for(const k of keys)document.querySelector('[data-eb-cancel-row="'+k+'"]')?.click();
  closeModal();
  window.__avisos = [];
  window.alert = m => window.__avisos.push(String(m));
  window.confirm = () => true;
  window.prompt = () => null;
  S.params.saldoIni = 40000; S.cycleRealizado = 0;
  S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
  S.phaseUnlocked = [true,false,false,false];
  S.phases[0].orders[0] = {id:'G1', par:'EURUSD', tipo:'BUY', lote:0.01,
    entry:1.10, sl:1.09, tp:1.20, status:'Aberta',
    openedAt:'2026-08-01T10:00:00.000Z'};
  delete S.phases[0].orders[0].result;
  S.activeOperation = {schemaVersion:1, operationId:'op_fech',
    openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
    maxAccountPhaseReached:0};
  save();
  navigateToScreen('exec'); JPWExec.ui.selectView('panel'); renderPhases();
}"""


def fecha_pela_ui(page, texto_resultado):
    """Abre o modal pelo botao Fechar ordem; confirma resultado no fluxo real."""
    return page.evaluate(
        """txt => {
          const button=document.querySelector('[data-eb-close-row="0:0"]');
          if(!button)return {erro:'botao Fechar ordem ausente'};
          button.click();
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
            browser = p.chromium.launch(**launcher.launch_options())
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
