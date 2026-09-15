#!/usr/bin/env python3
"""Fiacao real da Operacao Unica: DOM -> evento -> dominio -> estado -> disco.

ESTE ARQUIVO EXISTE POR UM DEFEITO CONCRETO. O gancho que faz a Operacao Unica
nascer foi ligado ao laco de <input>, mas o campo Status e um <select>: a
chamada era codigo morto e a entidade jamais nascia pela interface. O tier
standard passava 16/16 e varias campanhas de mutation testing nao acusaram —
porque todos os testes chamavam operationOnOrderStatus() DIRETAMENTE.

Teste de dominio prova que a regra esta certa. Nao prova que ela e chamada.
Os registros sob teste passam pelos controles reais e por Salvar linha.
Fixtures podem preparar o estado; os atos de abertura/correcao verificam
DOM -> rascunho -> confirmacao explicita -> estado -> disco.
A mudanca de status isolada nao deve mais gravar automaticamente.

Todas as fixtures sao SINTETICAS.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import socket
import threading

import notes_launcher_test as launcher
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


# Prepara uma Genese pronta para abrir e REDESENHA a grade, para que os
# listeners reais sejam religados aos nos reais.
PREPARAR = """
  window.__descartaDrafts = () => {
    const keys=[...document.querySelectorAll('[data-eb-row].eb-dirty')].map(e=>e.dataset.ebRow);
    for(const k of keys)document.querySelector('[data-eb-cancel-row="'+k+'"]')?.click();
  };
  window.__salvarLinha = (pi,oi,allowRefusal=false) => {
    const reason=document.querySelector('[data-eb-reason="'+pi+':'+oi+'"]');
    if(reason){reason.value='Correção sintética justificada';reason.dispatchEvent(new Event('input',{bubbles:true}));}
    const button=document.querySelector('[data-eb-save-row="'+pi+':'+oi+'"]');
    if(!button)throw Error('Salvar linha não encontrado');
    button.click();
    const error=document.getElementById('ebError-'+pi+'-'+oi)?.textContent.trim()||'';
    if(error&&!allowRefusal)throw Error('Salvar linha '+pi+':'+oi+' recusado: '+error);
    return {ok:!error,error};
  };
  window.__prepararGenese = () => {
    __descartaDrafts();
    S.accounts=[{forexAccountId:'wiring_A',nome:'Mestre sintética wiring',tipo:'MESTRE',currency:'USD',sini:10000,satu:10000}];
    S.forex=JPWForex.state.empty();S.forex.activeAccountId='wiring_A';
    S.forex.accounts.wiring_A={si:10000,equity:10000,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',periodId:'wiring_P',source:'Synthetic wiring fixture',observedAt:'2026-09-15T12:00:00Z'};
    S.activeOperation = null;
    S.operationHistory = {schemaVersion:1, records:[]};
    S.params.saldoIni = 10000;
    S.phaseUnlocked = [true,false,false,false];
    S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
    const g = S.phases[0].orders[0];
    // Lote DENTRO do teto por operacao do instrumento: a fixture nao pode
    // depender de furar uma guarda normativa legitima. O teto vem do catalogo
    // vivo (instrumentCatalog), entao e lido daqui em vez de fixado a mao.
    const ins = (S.instruments||[]).find(i => i && i.name === 'EURUSD');
    const teto = ins && +ins.teto > 0 ? +ins.teto : 0.01;
    g.recordStatus='draft'; g.id='G1'; g.role='GENESIS'; g.par='EURUSD'; g.tipo='BUY'; g.lote=teto; g.entry=1.1000; g.sl=1.0950; g.tp=1.1200; g.costs=0; g.costBasis='SEPARATE_FROM_RESULT';
    save();render();JPWNavigation.navigate('forex-operation');JPWExec.ui.selectView('panel');renderPhases();
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
          const before=JSON.stringify({phases:S.phases,op:S.activeOperation}),raw=localStorage.getItem(LSKEY);
          sel.value = 'Aberta';
          sel.dispatchEvent(new Event('change', {bubbles:true}));
          const draftIntact=before===JSON.stringify({phases:S.phases,op:S.activeOperation})&&raw===localStorage.getItem(LSKEY);
          __salvarLinha(0,0);
          return {opcoes,draftIntact,status:S.phases[0].orders[0].status};
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
    assert r["draftIntact"], "trocar Status gravou antes de Salvar linha"
    assert r["status"] == "Aberta", f"a abertura foi recusada pelas guardas: {r}"

    estado = page.evaluate(
        """() => ({
          op: S.activeOperation,
          ordemOpenedAt: S.phases[0].orders[0].openedAt,
          disco: (__doDisco().activeOperation || null)
        })"""
    )
    assert estado["op"], (
        "salvar a Genese pelo <select> e botao reais NAO criou a Operacao Unica — o gancho "
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


def run_draft_cancel_writes_nothing(page):
    """Status, custo e geometria so mudam apos confirmacao da linha inteira."""
    page.evaluate("() => __prepararGenese()")
    r=page.evaluate("""() => {
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY);
      for(const [field,value] of [['status','Aberta'],['entry','1.15'],['costs','-12']]){
        const control=document.querySelector('[data-p="0"][data-o="0"][data-f="'+field+'"]');
        control.value=value;control.dispatchEvent(new Event('change',{bubbles:true}));
      }
      const typed=before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY);
      document.querySelector('[data-eb-cancel-row="0:0"]').click();
      return {typed,canceled:before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY),
        status:__selectStatus(0,0).value,hasDrafts:JPWForex.executionBoardUI.hasDrafts()};
    }""")
    assert r['typed'] and r['canceled'] and r['status']=='' and not r['hasDrafts'],r


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
          sel.dispatchEvent(new Event('change', {bubbles:true})); __salvarLinha(0,0);
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
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
          const g = S.phases[0].orders[0];
          g.recordStatus='draft';g.id='X'; g.par=''; g.role='GENESIS'; g.tipo='BUY'; g.lote=0.10; g.entry=1.10; g.sl=1.09;   // SEM par -> guarda recusa
          renderPhases();
          const sel = __selectStatus(0,0);
          sel.value = 'Aberta';
          sel.dispatchEvent(new Event('change', {bubbles:true})); const refusal=__salvarLinha(0,0,true);
          return {status:S.phases[0].orders[0].status,op:S.activeOperation,error:refusal.error};
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
          sel.value = 'Aberta'; sel.dispatchEvent(new Event('change', {bubbles:true})); __salvarLinha(0,0);
          renderPhases();
          const beforeClose=JSON.stringify(S),rawBeforeClose=localStorage.getItem(LSKEY);
          const sel2 = __selectStatus(0,0);
          sel2.value='Fechada';sel2.dispatchEvent(new Event('change',{bubbles:true}));__salvarLinha(0,0,true);
          const bypassRefused=beforeClose===JSON.stringify(S)&&rawBeforeClose===localStorage.getItem(LSKEY);
          document.querySelector('[data-eb-cancel-row="0:0"]').click();
          document.querySelector('[data-eb-close-row="0:0"]').click();
          const temModal = !!document.getElementById('closeConfirmInput');
          if (!temModal) return {erro:'modal de fechamento nao abriu'};
          document.getElementById('closeResultInput').value = '';
          document.getElementById('closeConfirmInput').value = 'FECHADO';
          document.getElementById('modalConfirm').click();
          const emptyRefused=beforeClose===JSON.stringify(S)&&rawBeforeClose===localStorage.getItem(LSKEY);
          document.getElementById('closeResultInput').value = '250';
          document.getElementById('closeConfirmInput').value = 'NAO';
          document.getElementById('modalConfirm').click();
          const wordRefused=beforeClose===JSON.stringify(S)&&rawBeforeClose===localStorage.getItem(LSKEY);
          document.getElementById('closeResultInput').value = '250';
          document.getElementById('closeConfirmInput').value = 'FECHADO';
          document.getElementById('modalConfirm').click();
          const o = S.phases[0].orders[0];
          return {bypassRefused,emptyRefused,wordRefused,status:o.status,result:o.result,closedAt:o.closedAt,openedAt:o.openedAt,accountId:o.accountId,periodId:o.periodId,costs:o.costs,costBasis:o.costBasis,disk:__doDisco().phases[0].orders[0]};
        }"""
    )
    assert "erro" not in r, r.get("erro")
    assert r['bypassRefused'] and r['emptyRefused'] and r['wordRefused'], r
    assert r["status"] == "Fechada" and r["result"] == 250, f"fechamento nao aplicou: {r}"
    assert isinstance(r["closedAt"], str) and r["closedAt"], (
        "closedAt nao foi carimbado pelo fluxo REAL de fechamento"
    )
    assert isinstance(r["openedAt"], str), "o fechamento apagou o openedAt da ordem"
    assert r["accountId"] == "wiring_A" and r["periodId"] == "wiring_P", r
    assert r["costs"] == 0 and r["costBasis"] == "SEPARATE_FROM_RESULT", r
    assert r["disk"]["status"] == "Fechada" and r["disk"]["result"] == 250, r


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
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
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
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
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
    """V11: elevated risk creates a fact, never an inferred grid transition."""
    r=page.evaluate("""() => {
      __prepararGenese();S.cycleRealizado=-360;S.phases[0].orders[0].lote=999;renderPhases();
      const before=JSON.stringify(S.phaseUnlocked),events=S.transitionLog.length;
      const sel=__selectStatus(0,0);sel.value='Aberta';sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
      return {status:S.phases[0].orders[0].status,op:S.activeOperation,unchanged:before===JSON.stringify(S.phaseUnlocked),events:events===S.transitionLog.length,max:operationResolveGridPhaseMax(S.activeOperation)};
    }""")
    assert r['status']=='Aberta' and r['op']['operationId'] and r['unchanged'] and r['events'] and r['max'] is None,r


def run_manual_risk_refusal_creates_no_entity(page):
    """Execution confirmation cannot veto recording an already executed fact."""
    r=page.evaluate("""() => {
      __prepararGenese();S.onboarding.epStatus='Não vou utilizar.';
      let confirmations=0;window.confirm=()=>{confirmations++;return false;};
      const sel=__selectStatus(0,0);sel.value='Aberta';sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
      return {confirmations,status:S.phases[0].orders[0].status,op:S.activeOperation};
    }""")
    assert r['confirmations']==0 and r['status']=='Aberta' and r['op']['operationId'],r


def run_deleting_last_operational_order_abandons(page):
    """Executed rows are voided by the real button, never physically deleted."""
    r=page.evaluate("""() => {
      __prepararGenese();window.prompt=()=> 'Duplicidade sintética';
      const sel=__selectStatus(0,0);sel.value='Aberta';sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
      const id=S.activeOperation.operationId,count=S.phases[0].orders.length;
      document.querySelector('[data-delorder="0:0"]').click();
      return {id,op:S.activeOperation,order:S.phases[0].orders[0],count,after:S.phases[0].orders.length,history:S.operationHistory.records.length,disk:__doDisco().phases[0].orders[0]};
    }""")
    assert r['op']['operationId']==r['id'] and r['count']==r['after'] and r['history']==0,r
    assert r['order']['recordStatus']=='voided' and r['disk']['recordStatus']=='voided' and r['order']['revisions'][-1]['reason']=='Duplicidade sintética',r


def run_deleting_one_of_many_keeps_the_operation(page):
    r=page.evaluate("""() => {
      __prepararGenese();window.prompt=()=> 'Duplicidade de uma linha';
      const s=__selectStatus(0,0);s.value='Aberta';s.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
      operationRecordOrder(0,1,{id:'D1',par:'EURUSD',tipo:'BUY',lote:1,entry:1.1,sl:1.09,status:'Fechada',result:-20},{reason:'Fato confirmado'});
      const id=S.activeOperation.operationId;renderPhases();document.querySelector('[data-delorder="0:1"]').click();
      return {id,after:S.activeOperation.operationId,first:S.phases[0].orders[0],second:S.phases[0].orders[1],count:operationLiveOrders().length};
    }""")
    assert r['id']==r['after'] and r['count']==2 and r['first']['recordStatus']=='recorded' and r['second']['recordStatus']=='voided',r


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
          sel.value='Aberta'; sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
          const op1 = JSON.parse(JSON.stringify(S.activeOperation));
          // Orfandade FORCADA: apaga a ordem sem passar pelo ato de exclusao,
          // para exercitar o fail-safe e nao a correcao do handler.
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
          S.activeOperation = JSON.parse(JSON.stringify(op1));
          save();
          const orfaViva = S.activeOperation && S.activeOperation.operationId;
          // Tese NOVA, outro instrumento.
          const g = S.phases[0].orders[0];
          g.recordStatus='draft';g.id='G2';g.role='GENESIS'; g.par='GBPUSD'; g.tipo='SELL'; g.lote=0.01; g.entry=1.27; g.sl=1.275; g.tp=1.20;
          renderPhases();
          const sel2 = __selectStatus(0,0);
          sel2.value='Aberta'; sel2.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
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
    """Clearing a factual status is refused; original identity/evidence survive."""
    r=page.evaluate("""() => {
      __prepararGenese();window.prompt=()=> 'Tentativa de retirar fato';
      let sel=__selectStatus(0,0);sel.value='Aberta';sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY);
      sel=__selectStatus(0,0);sel.value='';sel.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0,true);
      return {stateSame:before===JSON.stringify(S),diskSame:raw===localStorage.getItem(LSKEY),status:S.phases[0].orders[0].status};
    }""")
    assert r['stateSame'] and r['diskSame'] and r['status']=='Aberta',r


def run_withdrawing_one_order_keeps_the_operation(page):
    r=page.evaluate("""() => {
      __prepararGenese();let s=__selectStatus(0,0);s.value='Aberta';s.dispatchEvent(new Event('change',{bubbles:true})); __salvarLinha(0,0);
      operationRecordOrder(0,1,{id:'D1',par:'EURUSD',tipo:'BUY',lote:1,entry:1.1,sl:1.09,status:'Fechada',result:-20},{reason:'Fato confirmado'});
      const before=JSON.stringify(S),a=operationRecordOrder(0,1,{status:''},{reason:'Retirada indevida'});
      return {a,same:before===JSON.stringify(S),count:operationLiveOrders().length};
    }""")
    assert not r['a']['ok'] and r['same'] and r['count']==2,r


# ---------------------------------------------------------------------------
# Bloco D — preflight da finalizacao
# ---------------------------------------------------------------------------
# O preflight ORQUESTRA e nao consolida: bloqueia com a ordem impeditiva
# nomeada, pede complementacao dos resultados genuinamente ausentes, ou segue
# para a revisao canonica. finalizeOperation continua sendo a unica autoridade
# de consolidacao, e nada aqui a alcanca sem passar pela revisao.

PREPARAR_D = """() => {
  window.__avisos = [];
  window.alert = m => window.__avisos.push(String(m));
  window.confirm = () => true;
  window.prompt = () => null;
  // cfg: {abertas:[[pi,oi]], fechadas:[[pi,oi,result]]}  result null = ausente
  window.__cenarioD = (cfg) => {
    __descartaDrafts();
    S.params.saldoIni = 40000; S.cycleRealizado = 0;
    // Esta fixture preserva a grade LEGACY de quatro fases. Em seis grades,
    // Gênese/Defesa dependem de papel explícito, coberto no focal V11.
    S.phases = S.phases.slice(0,4);
    S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]||3); });
    S.phaseUnlocked = [true,false,false,false];
    S.operationHistory = {schemaVersion:1, records:[]};
    const base = (id,par) => ({id, par:par||'EURUSD', tipo:'BUY', lote:0.01,
      entry:1.10, sl:1.09, tp:1.20, openedAt:'2026-08-01T10:00:00.000Z'});
    (cfg.abertas||[]).forEach(([pi,oi], n) => {
      const o = base('A'+n); o.status='Aberta';
      S.phases[pi].orders[oi] = o;
    });
    (cfg.migradas||[]).forEach(([pi,oi], n) => {
      const o = base('M'+n); o.status='Migrada';
      delete o.result;                       // Migrada NUNCA foi fechada: nao tem resultado
      S.phases[pi].orders[oi] = o;
    });
    (cfg.fechadas||[]).forEach(([pi,oi,res], n) => {
      const o = base('F'+n); o.status='Fechada'; o.closedAt='2026-08-05T10:00:00.000Z';
      if (res === null || res === undefined) { delete o.result; } else { o.result = res; }
      S.phases[pi].orders[oi] = o;
    });
    S.activeOperation = {schemaVersion:1, operationId:'op_d',
      policySnapshot:{policyVersion:'LEGACY_UNRESOLVED'},
      openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
      maxAccountPhaseReached:0};
    save();
    navigateToScreen('exec'); JPWExec.ui.selectView('panel');
    render(); renderPhases();
  };
  window.__foto = () => JSON.stringify({
    ciclo:S.cycleRealizado, phases:S.phases, registros:S.operationHistory.records,
    op:S.activeOperation, unlocked:S.phaseUnlocked
  });
  window.__superficie = () => {
    const box = document.getElementById('modalBox');
    if (!document.getElementById('modalOverlay').classList.contains('show')) return 'fechada';
    if (box.querySelector('[data-compl="0"]')) return 'complementacao';
    if (box.querySelector('#finalConfirm')) return 'revisao';
    if (box.textContent.indexOf('Não é possível finalizar') >= 0) return 'bloqueio';
    return 'outra';
  };
  window.__clicaFinalizar = () => {
    const b = document.getElementById('archiveOpBtn');
    if (!b) return 'botao ausente';
    b.click();
    return __superficie();
  };
}"""


def run_preflight_blocks_open_genesis(page):
    """(1) Genese aberta: botao visivel, clique bloqueia, estado inalterado."""
    page.evaluate(PREPARAR_D)
    r = page.evaluate(
        """() => {
          __cenarioD({abertas:[[0,0]], fechadas:[[0,1,250]]});
          const btn = document.getElementById('archiveOpBtn');
          const visivel = btn && btn.style.display !== 'none';
          const antes = __foto();
          const superficie = __clicaFinalizar();
          const texto = document.getElementById('modalBox').textContent;
          return {visivel, superficie, texto, intacto: __foto() === antes,
                  registros: S.operationHistory.records.length};
        }"""
    )
    assert r["visivel"], (
        "o botao Finalizar Operacao esta ESCONDIDO com ordem aberta — a acao tem de "
        "existir e explicar, nao sumir"
    )
    assert r["superficie"] == "bloqueio", f"superficie apresentada: {r['superficie']!r}"
    assert "Ordem Gênese" in r["texto"], (
        f"a mensagem nao identifica a Genese: {r['texto'][:200]!r}"
    )
    assert "GÊNESE LEGACY" in r["texto"] and "ID A0" in r["texto"], "a ordem impeditiva nao foi nomeada na lista"
    assert r["intacto"], "o clique MUTOU o estado apesar do bloqueio"
    assert r["registros"] == 0, "o bloqueio gravou Historico"


def run_preflight_blocks_other_open_order(page):
    """(2) Outra ordem aberta: mesmo comportamento, sem citar Genese."""
    r = page.evaluate(
        """() => {
          __cenarioD({abertas:[[0,2]], fechadas:[[0,0,250]]});
          const antes = __foto();
          const superficie = __clicaFinalizar();
          const texto = document.getElementById('modalBox').textContent;
          return {superficie, texto, intacto: __foto() === antes};
        }"""
    )
    assert r["superficie"] == "bloqueio", f"superficie: {r['superficie']!r}"
    assert "Ordem Gênese" not in r["texto"], (
        "a mensagem culpou a Genese sendo outra a ordem aberta"
    )
    assert "SLOT LEGACY 1.3" in r["texto"] and "ID A0" in r["texto"], f"a ordem impeditiva nao foi nomeada: {r['texto'][:200]!r}"
    assert r["intacto"], "o clique mutou o estado"


def run_preflight_asks_for_the_single_missing_result(page):
    """(3) Uma fechada sem resultado: a superficie mostra exatamente aquela."""
    r = page.evaluate(
        """() => {
          __cenarioD({fechadas:[[0,0,250],[0,1,null]]});
          const superficie = __clicaFinalizar();
          const box = document.getElementById('modalBox');
          const campos = box.querySelectorAll('[data-compl]').length;
          return {superficie, campos, texto: box.textContent};
        }"""
    )
    assert r["superficie"] == "complementacao", f"superficie: {r['superficie']!r}"
    assert r["campos"] == 1, f"campos apresentados: {r['campos']} — so uma ordem falta"
    assert "SLOT LEGACY 1.2" in r["texto"] and "ID F1" in r["texto"], f"a ordem incompleta nao foi identificada: {r['texto'][:200]!r}"
    assert "GÊNESE" not in r["texto"], "pediu resultado de uma ordem que ja o tinha"


def run_preflight_uses_one_surface_for_many(page):
    """(4) Varias incompletas: UMA superficie, cada ordem identificada."""
    r = page.evaluate(
        """() => {
          __cenarioD({fechadas:[[0,0,null],[0,1,null],[1,0,null]]});
          const superficie = __clicaFinalizar();
          const box = document.getElementById('modalBox');
          const rotulos = [...box.querySelectorAll('[data-qid^="ord"] .ql')].map(x => x.textContent);
          return {superficie, campos: box.querySelectorAll('[data-compl]').length, rotulos};
        }"""
    )
    assert r["superficie"] == "complementacao", f"superficie: {r['superficie']!r}"
    assert r["campos"] == 3, f"esperava 3 campos numa unica superficie, veio {r['campos']}"
    assert len(set(r["rotulos"])) == 3, (
        f"os rotulos nao distinguem as ordens: {r['rotulos']} — o operador nao saberia "
        "qual resultado esta informando"
    )
    assert any("GÊNESE" in x for x in r["rotulos"]), f"rotulos: {r['rotulos']}"


def run_completion_accepts_zero_negative_positive(page):
    """(5)(6)(7) Zero, negativo e positivo sao complementacoes validas."""
    for txt, esperado in (("0", 0), ("-500", -500), ("1420,50", 1420.5)):
        r = page.evaluate(
            """txt => {
              __cenarioD({fechadas:[[0,0,null]]});
              __clicaFinalizar();
              document.querySelector('[data-compl="0"]').value = txt;
              document.getElementById('modalConfirm').click();
              return {superficie: __superficie(),
                      result: S.phases[0].orders[0].result,
                      tipo: typeof S.phases[0].orders[0].result};
            }""", txt)
        assert r["result"] == esperado and r["tipo"] == "number", (
            f"{txt!r}: gravou {r['result']!r} ({r['tipo']}), esperado {esperado}"
        )
        assert r["superficie"] == "revisao", (
            f"{txt!r}: apos completar, a superficie deveria ser a revisao canonica, "
            f"veio {r['superficie']!r}"
        )
        page.evaluate("() => closeModal()")


def run_completion_blocks_invalid(page):
    """(8) Invalido e parse parcial bloqueiam, e nada e aplicado."""
    for txt in ("", "abc", "1.2.3", "1.420,50"):
        r = page.evaluate(
            """txt => {
              __cenarioD({fechadas:[[0,0,null]]});
              const antes = __foto();
              __clicaFinalizar();
              document.querySelector('[data-compl="0"]').value = txt;
              document.getElementById('modalConfirm').click();
              return {superficie: __superficie(),
                      erroVisivel: !!document.querySelector('[data-qid="ord0"] .modal-err.show'),
                      temResult: Number.isFinite(S.phases[0].orders[0].result),
                      intacto: __foto() === antes};
            }""", txt)
        assert r["superficie"] == "complementacao", (
            f"{txt!r}: saiu da complementacao ({r['superficie']!r})"
        )
        assert r["erroVisivel"], f"{txt!r}: nao foi acusado"
        assert not r["temResult"], f"{txt!r}: gravou resultado apesar de invalido"
        assert r["intacto"], f"{txt!r}: mutou o estado"
        page.evaluate("() => closeModal()")


def run_completion_cancel_applies_nothing(page):
    """(9) Cancelar com valores parciais digitados nao aplica NADA."""
    r = page.evaluate(
        """() => {
          __cenarioD({fechadas:[[0,0,null],[0,1,null],[1,0,null]]});
          const antes = __foto();
          __clicaFinalizar();
          // O operador preenche DUAS das tres e desiste.
          document.querySelector('[data-compl="0"]').value = '250';
          document.querySelector('[data-compl="1"]').value = '-80';
          document.getElementById('modalCancel').click();
          return {superficie: __superficie(), intacto: __foto() === antes,
                  r0: Number.isFinite(S.phases[0].orders[0].result),
                  r1: Number.isFinite(S.phases[0].orders[1].result),
                  registros: S.operationHistory.records.length,
                  op: !!S.activeOperation};
        }"""
    )
    assert r["superficie"] == "fechada", f"o modal nao fechou: {r['superficie']!r}"
    assert not r["r0"] and not r["r1"], (
        "valores digitados e NAO confirmados foram aplicados — cancelar deixaria a "
        "operacao com metade dos resultados gravados"
    )
    assert r["intacto"], "cancelar mutou o estado"
    assert r["registros"] == 0, "cancelar gravou Historico"
    assert r["op"], "cancelar destruiu a operacao viva"


def run_completion_revalidates_then_reviews(page):
    """(10)(11)(12) Completo segue para a revisao; ja completo nao pergunta nada."""
    completo = page.evaluate(
        """() => {
          __cenarioD({fechadas:[[0,0,250],[0,1,-80]]});
          const superficie = __clicaFinalizar();
          return {superficie, temCampo: !!document.querySelector('[data-compl]')};
        }"""
    )
    assert completo["superficie"] == "revisao", (
        f"(11) operacao completa deveria ir direto a revisao, veio {completo['superficie']!r}"
    )
    assert not completo["temCampo"], "(11) abriu questionario sem haver o que completar"
    page.evaluate("() => closeModal()")

    encadeado = page.evaluate(
        """() => {
          __cenarioD({fechadas:[[0,0,null],[0,1,null]]});
          const s1 = __clicaFinalizar();
          document.querySelector('[data-compl="0"]').value = '250';
          document.querySelector('[data-compl="1"]').value = '-80';
          document.getElementById('modalConfirm').click();
          const s2 = __superficie();
          // A revisao tem de refletir os valores recem-informados.
          const box = document.getElementById('modalBox');
          const linhas = {};
          box.querySelectorAll('#finalReview .modal-q').forEach(q => {
            const l=q.querySelector('.ql'), v=q.querySelector('.op-final-val');
            if(l&&v) linhas[l.textContent.trim()] = v.textContent.trim();
          });
          return {s1, s2, linhas, net: netOpAtual(),
                  registros: S.operationHistory.records.length};
        }"""
    )
    assert encadeado["s1"] == "complementacao", f"(12) primeira superficie: {encadeado['s1']!r}"
    assert encadeado["s2"] == "revisao", (
        f"(10) apos completar, o preflight deveria revalidar e abrir a revisao, veio "
        f"{encadeado['s2']!r}"
    )
    assert encadeado["net"] == 170, f"(10) consolidado apos complementar: {encadeado['net']}"
    assert encadeado["registros"] == 0, (
        "(10) a complementacao gravou Historico — ela completa estado, nao finaliza"
    )
    assert "Resultado líquido" in encadeado["linhas"], (
        f"(10) a revisao nao apresentou o resultado: {list(encadeado['linhas'])}"
    )
    page.evaluate("() => closeModal()")


def run_completion_applies_all_or_nothing(page):
    """Confirmar com MISTURA de valido e invalido nao aplica NENHUM.

    Validar-e-aplicar em laco gravaria as ordens validas e recusaria as
    invalidas: a operacao ficaria com metade dos resultados dentro, e o operador
    veria a mesma tela sem saber que parte ja foi para o estado. O contrato e
    tudo-ou-nada.
    """
    r = page.evaluate(
        """() => {
          __cenarioD({fechadas:[[0,0,null],[0,1,null],[1,0,null]]});
          const antes = __foto();
          __clicaFinalizar();
          document.querySelector('[data-compl="0"]').value = '250';    // valido
          document.querySelector('[data-compl="1"]').value = 'abc';    // INVALIDO
          document.querySelector('[data-compl="2"]').value = '-80';    // valido
          document.getElementById('modalConfirm').click();
          return {superficie: __superficie(),
                  erro1: !!document.querySelector('[data-qid="ord1"] .modal-err.show'),
                  aplicados: [S.phases[0].orders[0].result,
                              S.phases[0].orders[1].result,
                              S.phases[1].orders[0].result].filter(Number.isFinite).length,
                  intacto: __foto() === antes};
        }"""
    )
    assert r["superficie"] == "complementacao", (
        f"saiu da complementacao com entrada invalida: {r['superficie']!r}"
    )
    assert r["erro1"], "a ordem invalida nao foi acusada"
    assert r["aplicados"] == 0, (
        f"{r['aplicados']} de 3 resultados foram aplicados apesar de um ser invalido — "
        "aplicacao PARCIAL: o operador ficaria com metade dos valores no estado sem "
        "saber, e cancelar nao teria o que desfazer"
    )
    assert r["intacto"], "o estado foi mutado por uma confirmacao recusada"
    page.evaluate("() => closeModal()")


def run_migrated_order_needs_no_result(page):
    """Ordem 'Migrada' nao tem resultado a informar, e nao pode bloquear.

    netOpAtual() soma exclusivamente `status==='Fechada'`. Uma Migrada e ordem
    VIVA — conta para a exclusividade da tese — mas nunca foi fechada: exigir
    resultado dela pediria um dado que aquela linha nao tem motivo para ter, e a
    finalizacao ficaria presa num questionario impossivel de satisfazer.
    """
    r = page.evaluate(
        """() => {
          __cenarioD({migradas:[[0,0]], fechadas:[[1,0,250]]});
          const vivas = operationLiveOrders().length;
          const pre = JPWOperation.preflight();
          const superficie = __clicaFinalizar();
          const campos = document.querySelectorAll('[data-compl]').length;
          const texto = document.getElementById('modalBox').textContent;
          return {vivas, estado: pre.estado, superficie, campos, texto};
        }"""
    )
    assert r["vivas"] == 2, (
        f"a fixture nao produziu Migrada + Fechada vivas: {r['vivas']} — sem a Migrada "
        "o caso nao exercita nada"
    )
    assert r["estado"] == "ready", (
        f"o preflight considerou a operacao incompleta ({r['estado']!r}) por causa de "
        "uma ordem Migrada, que nunca teve resultado a informar"
    )
    assert r["superficie"] == "revisao", f"superficie: {r['superficie']!r}"
    assert r["campos"] == 0, (
        f"abriu {r['campos']} campo(s) de complementacao para uma operacao completa"
    )
    page.evaluate("() => closeModal()")


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launcher.launch_options())
            context, page, observed = prepare_page(browser, url)
            page.evaluate(PREPARAR)
            run_draft_cancel_writes_nothing(page)
            run_genesis_birth_through_ui(page)
            run_identity_stable_across_renders(page)
            run_rejected_open_creates_nothing(page)
            run_unlock_by_own_genesis_is_stamped_with_real_identity(page)
            run_manual_risk_refusal_creates_no_entity(page)
            # ---- R2: retirada explicita da ordem do ciclo ----
            run_status_reverted_withdraws_the_order(page)
            run_withdrawing_one_order_keeps_the_operation(page)
            # ---- Bloco D: preflight da finalizacao ----
            page.evaluate(PREPARAR_D)
            run_preflight_blocks_open_genesis(page)
            run_preflight_blocks_other_open_order(page)
            run_preflight_asks_for_the_single_missing_result(page)
            run_preflight_uses_one_surface_for_many(page)
            run_completion_accepts_zero_negative_positive(page)
            run_completion_blocks_invalid(page)
            run_completion_cancel_applies_nothing(page)
            run_completion_revalidates_then_reviews(page)
            run_completion_applies_all_or_nothing(page)
            run_migrated_order_needs_no_result(page)
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
