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


def run_grid_phase_scoped_by_operation(page):
    """maxGridPhaseReached vem SO dos eventos daquela operationId.

    A derivacao anterior recortava o transitionLog por janela temporal aberta
    so na borda inferior. O log e cumulativo e nunca podado, entao transicoes
    de OUTRAS operacoes entravam no calculo e o registro imutavel ficava com
    uma fase que aquela operacao nunca alcancou.
    """
    r = page.evaluate(
        """() => {
          const casos = {};
          const base = (id, extra) => {
            __semear(Object.assign({id}, extra||{}));
            S.transitionLog = [];
          };
          // 1. A chega a F3; B chega a F4. B nao pode contaminar A.
          base('op_A');
          S.transitionLog.push({fase:2, gridPhase:1, ts:'2026-08-02T00:00:00Z', operationId:'op_A'});
          S.transitionLog.push({fase:3, gridPhase:2, ts:'2026-08-03T00:00:00Z', operationId:'op_A'});
          S.transitionLog.push({fase:4, gridPhase:3, ts:'2026-08-09T00:00:00Z', operationId:'op_B'});
          casos.A = JPWOperation.buildSnapshot(S.activeOperation,{defenseCount:0}).record.maxGridPhaseReached;

          // 2. Downgrade posterior NAO apaga o maximo.
          S.transitionLog.push({fase:'downgrade 3\u21922', ts:'2026-08-04T00:00:00Z', operationId:'op_A'});
          casos.aposDowngrade = JPWOperation.buildSnapshot(S.activeOperation,{defenseCount:0}).record.maxGridPhaseReached;

          // 3. Legado adotado: sem delimitacao inequivoca -> null.
          base('op_L');
          S.activeOperation.adoptedLegacyAt = '2026-08-01T00:00:00Z';
          S.transitionLog.push({fase:3, gridPhase:2, ts:'2026-08-03T00:00:00Z', operationId:'op_L'});
          casos.legado = JPWOperation.buildSnapshot(S.activeOperation,{defenseCount:0}).record.maxGridPhaseReached;

          // 4. Eventos SEM gridPhase (alertas) com a mesma operationId nao contam.
          base('op_C');
          S.transitionLog.push({fase:'stop quantitativo acima da fase', ts:'2026-08-03T00:00:00Z', operationId:'op_C'});
          S.transitionLog.push({fase:'operação finalizada', ts:'2026-08-04T00:00:00Z', operationId:'op_C'});
          casos.soAlertas = JPWOperation.buildSnapshot(S.activeOperation,{defenseCount:0}).record.maxGridPhaseReached;

          // 5. Evento legado SEM operationId nao e atribuido por cronologia.
          base('op_D');
          S.transitionLog.push({fase:4, gridPhase:3, ts:'2026-08-03T00:00:00Z'});   // sem vinculo
          casos.semVinculo = JPWOperation.buildSnapshot(S.activeOperation,{defenseCount:0}).record.maxGridPhaseReached;
          return casos;
        }"""
    )
    assert r["A"] == 2, (
        f"maxGridPhaseReached de A = {r['A']!r}; esperado 2 (F3). Se for 3, os "
        "eventos da operacao B contaminaram o registro de A"
    )
    assert r["aposDowngrade"] == 2, (
        f"downgrade apagou o maximo atingido: {r['aposDowngrade']!r} — o que foi "
        "alcancado foi alcancado"
    )
    assert r["legado"] is None, (
        f"legado adotado recebeu fase {r['legado']!r} — sem delimitacao inequivoca "
        "o valor tem de ser null, nunca aproximado"
    )
    assert r["soAlertas"] == 0, (
        f"eventos sem gridPhase entraram no calculo: {r['soAlertas']!r}"
    )
    assert r["semVinculo"] == 0, (
        f"evento legado SEM operationId foi atribuido: {r['semVinculo']!r} — "
        "atribuicao por cronologia e exatamente a heuristica proibida"
    )


def run_transition_events_are_stamped(page):
    """Evento novo recebe o operationId da operacao viva; sem operacao, null."""
    r = page.evaluate(
        """() => {
          S.activeOperation = {schemaVersion:1, operationId:'op_stamp', openedAt:null,
                               openedAtSource:null, maxAccountPhaseReached:null};
          const comOp = operationStampTransition({fase:3, ts:'x'}, 2);
          S.activeOperation = null;
          const semOp = operationStampTransition({fase:3, ts:'x'}, 2);
          const semFase = operationStampTransition({fase:'downgrade 3\u21922', ts:'x'});
          return {comOp, semOp, semFase};
        }"""
    )
    assert r["comOp"]["operationId"] == "op_stamp" and r["comOp"]["gridPhase"] == 2, (
        f"evento nao foi carimbado com a operacao viva: {r['comOp']}"
    )
    assert r["semOp"]["operationId"] is None, (
        f"vinculo FABRICADO sem operacao viva: {r['semOp']['operationId']!r}"
    )
    assert "gridPhase" not in r["semFase"], (
        f"evento sem fase atingida ganhou gridPhase: {r['semFase']}"
    )


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


def run_save_exception_full_rollback(page):
    """save() LANCANDO nao pode deixar o estado vivo no candidato.

    save() devolve false nas duas falhas previstas, mas PODE lancar: o
    tratamento de erro dele chama renderPersistenceFailureWarning(), que toca
    DOM. Sem cobertura, a excecao escaparia depois de S ja ser o candidato —
    grades zeradas em memoria, nada gravado. O teste compara o ESTADO INTEIRO,
    e nao uma propriedade.
    """
    r = page.evaluate(
        """() => {
          __semear({ciclo:1234});
          save();
          const antes = JSON.stringify(S);
          const bak = window.save;
          window.save = () => { throw new Error('falha sintetica de gravacao'); };
          let res, erro = null;
          try { res = JPWOperation.finalize({defenseCount:0}); }
          catch(e) { erro = String(e); }
          window.save = bak;
          return {res, erro, antes, depois: JSON.stringify(S)};
        }"""
    )
    assert r["erro"] is None, (
        f"a excecao de save() ESCAPOU de finalizeOperation: {r['erro']} — "
        "o chamador ficaria sem saber o que aconteceu com o estado"
    )
    assert r["res"]["ok"] is False and r["res"]["motivo"] == "persist_exception", (
        f"excecao nao foi classificada: {r['res']}"
    )
    assert r["antes"] == r["depois"], (
        "S NAO voltou ao estado anterior apos a excecao — grades, cycleRealizado, "
        "operationHistory, transitionLog e activeOperation precisam ficar "
        "logicamente identicos ao que eram antes da tentativa"
    )


def run_save_exception_after_write_keeps_result(page):
    """save() que GRAVA e so entao lanca nao pode ser revertido.

    Segunda janela real de excecao: o setItem ocorre e o pos-processamento
    (clearPersistenceFailureState -> repintura, timer) lanca. Reverter aqui
    faria a MEMORIA divergir do DISCO no sentido oposto — o disco teria a
    finalizacao e a sessao nao —, e o proximo save() apagaria a finalizacao ja
    persistida. Por isso o desfecho e decidido lendo o documento de volta, e nao
    pela pilha: rollback cego passaria neste caso e destruiria o resultado.
    """
    r = page.evaluate(
        """() => {
          __semear({ciclo:900});
          save();
          const cicloAntes = S.cycleRealizado;
          const net = netOpAtual();
          const bak = window.save;
          // Grava DE VERDADE e so entao lanca.
          window.save = () => {
            localStorage.setItem('jpwealth_v9_state',
              JSON.stringify(S,(k,v)=>k==='investorPassword'?'':v));
            throw new Error('pos-processamento de save lancou');
          };
          let res, erro = null;
          try { res = JPWOperation.finalize({defenseCount:0}); }
          catch(e) { erro = String(e); }
          window.save = bak;
          const disco = JSON.parse(localStorage.getItem('jpwealth_v9_state'));
          return {
            res, erro,
            memRegistros: S.operationHistory.records.length,
            discoRegistros: (disco.operationHistory.records||[]).length,
            memCiclo: S.cycleRealizado, discoCiclo: disco.cycleRealizado,
            esperado: cicloAntes + net,
            memOrdens: JPWOperation.liveOrders().length
          };
        }"""
    )
    assert r["erro"] is None, f"excecao escapou: {r['erro']}"
    assert r["res"]["ok"] is True, (
        f"a finalizacao foi REVERTIDA apesar de ter sido gravada: {r['res']} — "
        "o disco ficaria com o registro e a sessao sem ele, e o proximo save() "
        "apagaria a finalizacao persistida"
    )
    assert r["memRegistros"] == r["discoRegistros"] == 1, (
        f"memoria e disco divergiram: mem={r['memRegistros']} disco={r['discoRegistros']}"
    )
    assert r["memCiclo"] == r["discoCiclo"] == r["esperado"], (
        f"ciclo divergente: mem={r['memCiclo']} disco={r['discoCiclo']} esperado={r['esperado']}"
    )
    assert r["memOrdens"] == 0, "grades nao foram liberadas apesar da gravacao bem-sucedida"


def run_persisted_probe_cannot_be_fooled(page):
    """A confirmacao de gravacao nao pode confundir-se em nenhum dos casos.

    A sonda decide o desfecho quando save() lanca. Se ela afirmar "gravamos"
    sem termos gravado, o candidato fica vivo em memoria divergindo do disco —
    exatamente o que a transacao existe para impedir.
    """
    r = page.evaluate(
        """() => {
          const chave = 'jpwealth_v9_state';
          const nosso = {operationId:'op_probe', finalizedAt:'2026-08-17T12:00:00.000Z'};
          const bak = localStorage.getItem(chave);
          const casos = {};
          const por = (rotulo, valor) => {
            if (valor === null) localStorage.removeItem(chave);
            else localStorage.setItem(chave, valor);
            casos[rotulo] = operationPersistedHas(nosso);
          };
          por('storage vazio', null);
          por('string vazia', '');
          por('json invalido', '{ nao e json');
          por('documento nao-objeto', '[]');
          por('sem envelope', JSON.stringify({}));
          por('envelope sem records', JSON.stringify({operationHistory:{schemaVersion:1}}));
          por('records nao-array', JSON.stringify({operationHistory:{records:'x'}}));
          // O caso perigoso: MESMO ID, registro de outra finalizacao.
          por('mesmo id, finalizedAt diferente', JSON.stringify({operationHistory:{records:[
            {operationId:'op_probe', finalizedAt:'2020-01-01T00:00:00.000Z'}]}}));
          por('registro nulo na lista', JSON.stringify({operationHistory:{records:[null]}}));
          // O unico caso verdadeiro.
          por('nosso registro', JSON.stringify({operationHistory:{records:[
            {operationId:'op_probe', finalizedAt:'2026-08-17T12:00:00.000Z'}]}}));
          // Argumento invalido
          localStorage.setItem(chave, JSON.stringify({operationHistory:{records:[nosso]}}));
          casos['record nulo'] = operationPersistedHas(null);
          if (bak === null) localStorage.removeItem(chave); else localStorage.setItem(chave, bak);
          return casos;
        }"""
    )
    verdadeiro = r.pop("nosso registro")
    assert verdadeiro is True, "a sonda nao reconheceu o proprio registro gravado"
    falsos = {k: v for k, v in r.items() if v is not False}
    assert not falsos, (
        f"a sonda afirmou gravacao em caso(s) que nao a comprovam: {falsos} — "
        "cada um desses faria a memoria divergir do disco"
    )


def run_identity_not_forged_in_finalize(page):
    """Finalizacao nao fabrica identidade, e tentativas falhas nao a trocam."""
    ausente = page.evaluate(
        """() => {
          __semear({});
          S.activeOperation = null;      // viva, mas sem identidade
          const antes = JSON.stringify(S);
          const res = JPWOperation.finalize({defenseCount:0});
          return {res, mudou: JSON.stringify(S) !== antes};
        }"""
    )
    assert ausente["res"]["ok"] is False and ausente["res"]["motivo"] == "no_identity", (
        f"finalizacao fabricou identidade em vez de recusar: {ausente['res']}"
    )
    assert not ausente["mudou"], (
        "a tentativa recusada MUTOU o estado de entrada — identidade criada "
        "dentro da finalizacao deixa efeito colateral quando ela falha"
    )

    estavel = page.evaluate(
        """() => {
          __semear({});
          S.phases[1].orders[0].par = 'GBPUSD';        // conflito: vai falhar
          const id1 = S.activeOperation.operationId;
          JPWOperation.finalize({defenseCount:0});
          const id2 = S.activeOperation.operationId;
          JPWOperation.finalize({defenseCount:0});
          return {id1, id2, id3: S.activeOperation.operationId};
        }"""
    )
    assert estavel["id1"] == estavel["id2"] == estavel["id3"], (
        f"a identidade mudou entre tentativas falhas: {estavel} — uma Operacao "
        "Unica nao pode trocar de id conforme o numero de tentativas"
    )


def run_identity_born_in_lifecycle(page):
    """Ordem tornando-se operacional sem entidade faz a operacao nascer."""
    r = page.evaluate(
        """() => {
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.activeOperation = null;
          // NAO e a Genese abrindo: e uma ordem fechada direto pelo grid.
          const o = S.phases[1].orders[0];
          o.par='EURUSD'; o.tipo='BUY'; o.status='Fechada'; o.result=10;
          operationOnOrderStatus(o,'Fechada',1,0);
          const op = S.activeOperation;
          return {criou: !!op, openedAt: op && op.openedAt, fonte: op && op.openedAtSource};
        }"""
    )
    assert r["criou"], (
        "ordem operacional sem entidade nao fez a operacao nascer — ela chegaria "
        "a finalizacao sem identidade e seria recusada"
    )
    assert r["openedAt"] is None and r["fonte"] is None, (
        f"abertura inventada para ordem que nao e a Genese: {r}"
    )


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
          // Estado financeiro medido PRIMEIRO: se a mutacao fizer o modal
          // fechar, a leitura de DOM abaixo devolveria null e o teste quebraria
          // por TypeError em vez de acusar a propriedade violada.
          const depois = __foto();
          const aindaAberto = document.getElementById('modalOverlay').classList.contains('show');
          const nodeErr = document.querySelector('[data-qid="confirmtxt"] .modal-err');
          const err = !!nodeErr && nodeErr.classList.contains('show');
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
          const depois = __foto();
          const nodeErr = document.querySelector('[data-qid="defesas"] .modal-err');
          const err = !!nodeErr && nodeErr.classList.contains('show');
          closeModal();
          return {antes, depois, err};
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
          const depois = __foto();
          const nodeErr = document.querySelector('[data-qid="abertura"] .modal-err');
          const err = !!nodeErr && nodeErr.classList.contains('show');
          // agora com data valida
          const campoData = document.getElementById('finalOpenedAt');
          if (campoData) { campoData.value = '2026-08-01T10:00';
                           document.getElementById('modalConfirm').click(); }
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
          const depois = __foto();
          const aberto = document.getElementById('modalOverlay').classList.contains('show');
          const falha = document.getElementById('finalFail');
          const cta = document.getElementById('modalConfirm');
          const ctaLiberado = !!cta && !cta.disabled;
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


# ---------------------------------------------------------------------------
# Trilha de auditoria: mesma transacao, mesma gravacao (#4)
# ---------------------------------------------------------------------------
# dgLogChange documenta a propria doutrina: "quem muta o estado e quem
# persiste — o log entra na mesma gravacao". Registrar a finalizacao DEPOIS de
# save() viola isso: o evento existiria so na memoria da sessao e morreria no
# proximo reload. Os cinco casos abaixo fixam o contrato nas duas direcoes —
# se a finalizacao venceu, a auditoria esta NO DISCO; se foi revertida, a
# auditoria foi revertida junto.

AUDIT_HELPER = """
  window.__auditar = (id) => {
    const doc = JSON.parse(localStorage.getItem('jpwealth_v9_state') || '{}');
    const conta = (st) => {
      const log = (st && st.dataGovernance && st.dataGovernance.changeLog) || [];
      return log.filter(e => e.entity === 'operation'
                          && e.action === 'finalized'
                          && e.recordId === id).length;
    };
    return {mem: conta(S), disco: conta(doc),
            teto: (S.dataGovernance.changeLog || []).length >= DG_CHANGELOG_MAX};
  };
"""


def run_audit_is_in_the_persisted_document(page):
    """Sucesso: o evento de auditoria esta no MESMO documento gravado.

    Este e o caso que a mutacao alvo quebra. Ele nao le a memoria para decidir:
    le o localStorage. Auditoria escrita depois de save() aparece em memoria e
    NAO aparece no disco, e e exatamente essa divergencia que o assert acusa.
    """
    r = page.evaluate(
        """() => {
          __semear({id:'op_audit_ok', ciclo:100});
          save();
          const antes = __auditar('op_audit_ok');
          const res = JPWOperation.finalize({defenseCount:0});
          return {res, antes, depois: __auditar('op_audit_ok')};
        }"""
    )
    assert r["res"]["ok"] is True, f"finalizacao falhou: {r['res']}"
    assert r["antes"]["mem"] == 0 and r["antes"]["disco"] == 0, (
        f"o evento ja existia antes da finalizacao: {r['antes']} — o teste nao "
        "estaria medindo nada"
    )
    assert not r["depois"]["teto"], (
        "o changeLog atingiu DG_CHANGELOG_MAX; o resultado mediria truncamento"
    )
    assert r["depois"]["mem"] == 1, f"auditoria ausente da memoria: {r['depois']}"
    assert r["depois"]["disco"] == 1, (
        f"AUDITORIA NAO CHEGOU AO DISCO: {r['depois']} — o evento foi registrado "
        "depois de save() e morre no proximo reload; a finalizacao ficaria "
        "gravada sem rastro no log de governanca"
    )


def run_audit_uses_the_real_operation_identity(page):
    """recordId e o operationId real, nao vazio nem uma segunda identidade."""
    r = page.evaluate(
        """() => {
          __semear({id:'op_audit_ident', ciclo:100});
          save();
          const res = JPWOperation.finalize({defenseCount:0});
          const doc = JSON.parse(localStorage.getItem('jpwealth_v9_state'));
          const ev = (doc.dataGovernance.changeLog || [])
            .filter(e => e.entity === 'operation' && e.action === 'finalized').pop();
          return {res, ev, recId: res.record.operationId,
                  histIds: doc.operationHistory.records.map(x => x.operationId)};
        }"""
    )
    assert r["res"]["ok"] is True, f"finalizacao falhou: {r['res']}"
    assert r["ev"], "nenhum evento de finalizacao no documento persistido"
    assert r["ev"]["recordId"] == "op_audit_ident", (
        f"recordId nao e a identidade real da operacao: {r['ev']['recordId']!r}"
    )
    assert r["ev"]["recordId"] == r["recId"], (
        "auditoria e registro historico usam identidades diferentes"
    )
    assert r["ev"]["recordId"] in r["histIds"], (
        "o recordId da auditoria nao localiza nenhum registro no Historico — "
        "o evento seria uma ancora morta"
    )


def run_audit_rolled_back_on_persist_failure(page):
    """save() devolve false: nenhum evento de finalizacao sobrevive em memoria."""
    r = page.evaluate(
        """() => {
          __semear({id:'op_audit_fail', ciclo:100});
          save();
          jpWealthPersistenceBlocked = true;
          const res = JPWOperation.finalize({defenseCount:0});
          jpWealthPersistenceBlocked = false;
          return {res, audit: __auditar('op_audit_fail')};
        }"""
    )
    assert r["res"]["ok"] is False, f"esperava falha de persistencia: {r['res']}"
    assert r["audit"]["mem"] == 0, (
        f"a auditoria SOBREVIVEU ao rollback: {r['audit']} — a sessao afirmaria "
        "no log de governanca que a operacao foi finalizada, enquanto a "
        "operacao continua viva e a grade intacta"
    )
    assert r["audit"]["disco"] == 0, f"auditoria de finalizacao inexistente foi gravada: {r['audit']}"


def run_audit_rolled_back_on_exception_before_write(page):
    """Excecao ANTES da gravacao: o rollback devolve tambem a trilha."""
    r = page.evaluate(
        """() => {
          __semear({id:'op_audit_throw', ciclo:100});
          save();
          const bak = window.save;
          window.save = () => { throw new Error('falha sintetica'); };
          let res, erro = null;
          try { res = JPWOperation.finalize({defenseCount:0}); } catch(e) { erro = String(e); }
          window.save = bak;
          return {res, erro, audit: __auditar('op_audit_throw')};
        }"""
    )
    assert r["erro"] is None, f"excecao escapou: {r['erro']}"
    assert r["res"]["ok"] is False and r["res"]["motivo"] == "persist_exception", (
        f"excecao nao classificada: {r['res']}"
    )
    assert r["audit"]["mem"] == 0 and r["audit"]["disco"] == 0, (
        f"a trilha de auditoria ficou fora do rollback: {r['audit']}"
    )


def run_audit_survives_exception_after_write(page):
    """Excecao APOS gravacao confirmada: a trilha ja esta no documento.

    Espelho do caso anterior. Como o resultado e mantido — o disco tem a
    finalizacao —, a auditoria precisa estar la junto, e nao pendurada num
    passo posterior que a excecao impediu de rodar.
    """
    r = page.evaluate(
        """() => {
          __semear({id:'op_audit_after', ciclo:100});
          save();
          const bak = window.save;
          window.save = () => {
            localStorage.setItem('jpwealth_v9_state',
              JSON.stringify(S,(k,v)=>k==='investorPassword'?'':v));
            throw new Error('pos-processamento lancou');
          };
          let res, erro = null;
          try { res = JPWOperation.finalize({defenseCount:0}); } catch(e) { erro = String(e); }
          window.save = bak;
          return {res, erro, audit: __auditar('op_audit_after')};
        }"""
    )
    assert r["erro"] is None, f"excecao escapou: {r['erro']}"
    assert r["res"]["ok"] is True, f"resultado gravado foi revertido: {r['res']}"
    assert r["audit"]["disco"] == 1, (
        f"o documento gravado ficou SEM a auditoria: {r['audit']} — a "
        "finalizacao esta no disco e o log de governanca nao a registra"
    )
    assert r["audit"]["mem"] == 1, f"memoria divergiu do disco: {r['audit']}"


def run_audit_single_event_per_operation(page):
    """Dupla tentativa: um unico evento para a mesma operationId."""
    r = page.evaluate(
        """() => {
          __semear({id:'op_audit_dupla', ciclo:100});
          save();
          const a = JPWOperation.finalize({defenseCount:0});
          const b = JPWOperation.finalize({defenseCount:0});
          return {a, b, audit: __auditar('op_audit_dupla')};
        }"""
    )
    assert r["a"]["ok"] is True, f"primeira finalizacao falhou: {r['a']}"
    assert r["b"]["ok"] is False, f"segunda finalizacao foi aceita: {r['b']}"
    assert r["audit"]["disco"] == 1, (
        f"a operacao gerou {r['audit']['disco']} eventos de finalizacao no log — "
        "o detalhamento cronologico contaria a mesma finalizacao duas vezes"
    )
    assert r["audit"]["mem"] == 1, f"memoria com contagem divergente: {r['audit']}"


# ---------------------------------------------------------------------------
# Revisao = snapshot (#5)
# ---------------------------------------------------------------------------
# Regra central: tudo que depende de entrada manual e sera imutavelmente
# persistido aparece na revisao com o VALOR QUE SERA GRAVADO. A revisao antiga
# era construida uma unica vez, na abertura do modal, com defenseCount:0 cravado
# e sem openedAtManual — o operador aprovava um registro e outro ia para o
# disco. Os testes digitam com evento `input` REAL: atribuir .value direto nao
# dispara repintura nenhuma e nao provaria nada sobre a fiacao.

REVISAO_HELPER = """
  window.__digitar = (sel, val) => {
    const el = document.querySelector(sel);
    // Devolve null em vez de estourar. Se uma repintura destruir o campo, o
    // desfecho tem de chegar ao Python como DADO e ser acusado por assercao —
    // um TypeError aqui derrubaria o evaluate e a propriedade violada ficaria
    // sem acusacao nomeada.
    if (!el) return null;
    el.value = val;
    el.dispatchEvent(new Event('input', {bubbles:true}));
    return el.value;
  };
  window.__revisao = () => {
    const out = {};
    document.querySelectorAll('#finalReview .modal-q').forEach(q => {
      const l = q.querySelector('.ql'), v = q.querySelector('.op-final-val');
      if (l && v) out[l.textContent.trim()] = v.textContent.trim();
    });
    return out;
  };
"""


def run_review_equals_persisted_record(page):
    """PROVA DIRETA: o que a revisao mostra e o que o Historico recebe.

    Operacao legada, abertura X e defesas Y informadas pelo operador. A revisao
    e lida ANTES da confirmacao; o registro e lido DEPOIS; os dois textos tem de
    coincidir. Na versao anterior a revisao dizia "Desconhecida" e "0" enquanto
    o disco recebia X e Y.
    """
    r = page.evaluate(
        """() => {
          __semear({openedAt:null, id:'op_prev_par'});
          JPWOperation.openReview();
          __digitar('#finalOpenedAt', '2026-07-15T08:30');
          __digitar('#finalDefenses', '4');
          const previa = __revisao();
          __digitar('#finalConfirm', 'FECHADO');
          document.getElementById('modalConfirm').click();
          const recs = S.operationHistory.records;
          const rec = recs[recs.length-1] || null;
          // Formula CANONICA reescrita aqui de proposito, e nao lida do codigo
          // de producao: se a exibicao adulterar o valor (deslocamento de fuso
          // so no lado da tela, por exemplo), o teste tem de divergir.
          return {previa, rec,
                  esperadoISO: new Date(Date.parse('2026-07-15T08:30')).toISOString(),
                  esperadoTexto: rec && rec.openedAt
                    ? new Date(rec.openedAt).toLocaleString('pt-BR')+' (informada manualmente)'
                    : null};
        }"""
    )
    prev, rec = r["previa"], r["rec"]
    assert rec, "a finalizacao nao produziu registro"
    assert rec["openedAt"] == r["esperadoISO"], (
        f"abertura persistida diverge do informado: {rec['openedAt']} != {r['esperadoISO']}"
    )
    assert rec["defenseCount"] == 4, f"defesas persistidas: {rec['defenseCount']}"
    assert rec["openedAtSource"] == "manual_legacy", f"proveniencia: {rec['openedAtSource']}"
    # O texto exibido tem de ser o texto do registro gravado, nao um parecido.
    assert "Desconhecida" not in prev["Abertura"], (
        f"a revisao mostrou abertura desconhecida enquanto o disco recebeu "
        f"{rec['openedAt']} — o operador aprovou um registro e outro foi gravado"
    )
    assert "(informada manualmente)" in prev["Abertura"], (
        f"a proveniencia manual nao apareceu na revisao: {prev['Abertura']!r}"
    )
    # Igualdade EXATA, nao presenca de substring: uma divergencia de VALOR entre
    # o que foi lido e o que foi gravado passaria por qualquer teste de substring.
    assert prev["Abertura"] == r["esperadoTexto"], (
        f"a revisao exibiu {prev['Abertura']!r} e o registro imutavel guardou "
        f"{rec['openedAt']!r}, que se le como {r['esperadoTexto']!r} — o operador "
        "aprovou um horario e outro foi persistido"
    )
    assert prev["Defesas informadas"] == "4", (
        f"a revisao mostrou {prev['Defesas informadas']!r} e o disco recebeu "
        f"{rec['defenseCount']}"
    )
    assert prev["Duração até agora"] != "—", (
        "a duracao continuou indisponivel apesar da abertura informada"
    )


def run_review_recalculates_on_opened_at_change(page):
    """Alterar a abertura recalcula a duracao exibida."""
    r = page.evaluate(
        """() => {
          __semear({openedAt:null, id:'op_prev_dur'});
          JPWOperation.openReview();
          // Literal proximo do presente quebraria contra codigo CORRETO em
          // qualquer maquina cujo relogio local esteja atras da data escrita —
          // a duracao viraria '—' por abertura no futuro. Derivar do relogio.
          const pad = n => String(n).padStart(2,'0');
          const h = new Date(Date.now() - 3600*1000);
          const umaHoraAtras = h.getFullYear()+'-'+pad(h.getMonth()+1)+'-'+pad(h.getDate())
                             +'T'+pad(h.getHours())+':'+pad(h.getMinutes());
          __digitar('#finalOpenedAt', '2020-01-01T00:00');
          const antiga = __revisao();
          __digitar('#finalOpenedAt', umaHoraAtras);
          const recente = __revisao();
          return {antiga, recente, umaHoraAtras};
        }"""
    )
    a, b = r["antiga"], r["recente"]
    assert a["Duração até agora"] != "—" and b["Duração até agora"] != "—", (
        f"duracao indisponivel: {a['Duração até agora']!r} / {b['Duração até agora']!r}"
    )
    assert a["Duração até agora"] != b["Duração até agora"], (
        f"a duracao NAO reagiu a mudanca de abertura: continuou "
        f"{a['Duração até agora']!r} — a revisao esta congelada na abertura do modal"
    )
    assert a["Abertura"] != b["Abertura"], "a abertura exibida nao reagiu"


def run_review_absent_defenses_is_not_zero(page):
    """Campo vazio mostra AUSENTE na revisao. Nunca 0."""
    r = page.evaluate(
        """() => {
          __semear({id:'op_prev_vazio'});
          JPWOperation.openReview();
          const inicial = __revisao();
          __digitar('#finalDefenses', '7');
          const preenchida = __revisao();
          __digitar('#finalDefenses', '');
          const limpa = __revisao();
          return {inicial, preenchida, limpa};
        }"""
    )
    assert r["inicial"]["Defesas informadas"] == "Não informado", (
        f"revisao inicial mostrou {r['inicial']['Defesas informadas']!r} — "
        "ausencia de informacao virou afirmacao do operador"
    )
    assert r["preenchida"]["Defesas informadas"] == "7", (
        f"revisao nao acompanhou a digitacao: {r['preenchida']['Defesas informadas']!r}"
    )
    assert r["limpa"]["Defesas informadas"] == "Não informado", (
        f"apagar o campo deixou {r['limpa']['Defesas informadas']!r} na revisao"
    )


def run_review_explicit_zero_is_shown_and_persisted(page):
    """Zero DIGITADO e afirmacao: aparece como 0 e chega ao disco como 0."""
    r = page.evaluate(
        """() => {
          __semear({id:'op_prev_zero'});
          save();
          JPWOperation.openReview();
          __digitar('#finalDefenses', '0');
          const previa = __revisao();
          __digitar('#finalConfirm', 'FECHADO');
          document.getElementById('modalConfirm').click();
          // Leitura DEFENSIVA de proposito. Se a finalizacao for recusada, o
          // desfecho tem de chegar ao Python como dado para ser ACUSADO por
          // assercao — um TypeError aqui derrubaria o evaluate antes de
          // qualquer verificacao e daria falsa sensacao de deteccao.
          const disco = JSON.parse(localStorage.getItem('jpwealth_v9_state') || 'null');
          const recs = (disco && disco.operationHistory && disco.operationHistory.records) || [];
          const rec = recs[recs.length-1] || null;
          return {previa, gravou: !!rec,
                  defesas: rec ? rec.defenseCount : null,
                  fonte: rec ? rec.defenseCountSource : null};
        }"""
    )
    assert r["previa"]["Defesas informadas"] == "0", (
        f"zero digitado nao apareceu como 0: {r['previa']['Defesas informadas']!r}"
    )
    assert r["gravou"], (
        "a finalizacao foi recusada com zero defesas digitado — zero e uma "
        "afirmacao valida do operador, nao ausencia de informacao"
    )
    assert r["defesas"] == 0, f"zero digitado nao chegou ao disco: {r['defesas']!r}"
    assert r["fonte"] == "manual", f"proveniencia: {r['fonte']!r}"


def run_review_promises_no_fixed_closing_time(page):
    """closedAt e capturado na CONFIRMACAO, e a revisao nao finge outra coisa.

    Mostrar um horario de aparencia definitiva e gravar outro depois da revisao
    e a mesma divergencia que este bloco existe para eliminar. O contrato e
    dito por extenso, e o teste prova as duas metades: o texto nao promete um
    instante fixo, e o instante gravado e o da confirmacao — nao o da abertura
    do modal.
    """
    r = page.evaluate(
        """async () => {
          __semear({id:'op_prev_fecho'});
          save();
          JPWOperation.openReview();
          // Toda a digitacao ANTES da espera: a ultima repintura precisa ficar
          // do outro lado do intervalo, senao a assercao nao distingue o
          // carimbo da confirmacao do carimbo da repintura.
          __digitar('#finalDefenses', '0');
          __digitar('#finalConfirm', 'FECHADO');
          const previa = __revisao();
          const tUltimaRepintura = Date.now();
          await new Promise(res => setTimeout(res, 1200));
          const tConfirmacao = Date.now();
          document.getElementById('modalConfirm').click();
          const recs = S.operationHistory.records;
          const rec = recs[recs.length-1] || null;
          return {previa, tUltimaRepintura, tConfirmacao, gravou: !!rec,
                  closedAt: rec ? Date.parse(rec.closedAt) : null,
                  texto: rec ? rec.closedAt : null};
        }"""
    )
    fecho = r["previa"]["Encerramento formal"]
    assert fecho == "Registrado no instante da confirmação", (
        f"a revisao anuncia um horario de encerramento: {fecho!r} — o operador "
        "leria um instante e outro seria gravado"
    )
    assert r["gravou"], "a finalizacao nao produziu registro"
    assert r["tConfirmacao"] - r["tUltimaRepintura"] >= 1000, (
        "a espera nao ocorreu entre a ultima repintura e o clique; sem esse "
        "intervalo as duas hipoteses (carimbo na repintura, carimbo na "
        "confirmacao) produzem o mesmo resultado e a comparacao e vacua"
    )
    # A assercao DISCRIMINANTE: o carimbo tem de ser posterior a ultima
    # repintura por mais que o intervalo, e nao apenas "nao anterior a
    # confirmacao". Sem ela, reaproveitar o record da previa passaria.
    assert r["closedAt"] > r["tUltimaRepintura"] + 1000, (
        f"closedAt e o instante da REPINTURA, nao o da confirmacao: {r['texto']} "
        f"foi carimbado {r['tConfirmacao'] - r['closedAt']}ms antes do clique, "
        "enquanto a revisao afirmava 'Registrado no instante da confirmação'"
    )
    assert r["closedAt"] >= r["tConfirmacao"] - 50, (
        f"closedAt anterior a confirmacao: {r['texto']}"
    )


def run_review_repaint_preserves_typing(page):
    """A repintura nao pode destruir foco nem texto ja digitado.

    A revisao e repintada a cada tecla. Reescrever o modal inteiro seria a saida
    obvia e erraria: o operador perderia o foco e o conteudo dos campos a cada
    caractere — o mesmo defeito de foco ja identificado na busca do Historico.
    """
    r = page.evaluate(
        """() => {
          __semear({openedAt:null, id:'op_prev_foco'});
          JPWOperation.openReview();
          __digitar('#finalConfirm', 'FECHADO');
          __digitar('#finalOpenedAt', '2026-07-01T09:00');
          document.getElementById('finalDefenses').focus();
          __digitar('#finalDefenses', '1');
          const focoDepois = document.activeElement && document.activeElement.id;
          __digitar('#finalDefenses', '12');
          // Leitura DEFENSIVA: se a repintura destruir os campos, o desfecho tem
          // de chegar ao Python como dado e ser acusado por assercao. Um
          // TypeError aqui derrubaria o evaluate e deixaria a propriedade
          // violada sem acusacao nomeada.
          const campo = id => document.getElementById(id);
          return {
            focoDepois,
            focoFinal: document.activeElement && document.activeElement.id,
            temAbertura: !!campo('finalOpenedAt'),
            temConfirmacao: !!campo('finalConfirm'),
            temDefesas: !!campo('finalDefenses'),
            confirmacao: campo('finalConfirm') ? campo('finalConfirm').value : null,
            abertura: campo('finalOpenedAt') ? campo('finalOpenedAt').value : null,
            defesas: campo('finalDefenses') ? campo('finalDefenses').value : null,
            revisao: __revisao()
          };
        }"""
    )
    assert r["temAbertura"] and r["temConfirmacao"] and r["temDefesas"], (
        f"a repintura DESTRUIU campos de entrada: abertura={r['temAbertura']}, "
        f"confirmacao={r['temConfirmacao']}, defesas={r['temDefesas']} — reescrever "
        "o modal inteiro a cada tecla e a saida obvia e errada"
    )
    assert r["focoDepois"] == "finalDefenses" and r["focoFinal"] == "finalDefenses", (
        f"a repintura roubou o foco: {r['focoDepois']!r} -> {r['focoFinal']!r}"
    )
    assert r["confirmacao"] == "FECHADO", (
        f"a repintura apagou o campo de confirmacao: {r['confirmacao']!r}"
    )
    assert r["abertura"] == "2026-07-01T09:00", (
        f"a repintura apagou a abertura informada: {r['abertura']!r}"
    )
    assert r["defesas"] == "12", f"a repintura apagou as defesas: {r['defesas']!r}"
    assert r["revisao"]["Defesas informadas"] == "12", (
        f"a revisao ficou defasada do campo: {r['revisao']['Defesas informadas']!r}"
    )


def run_review_return_matches_history_formula(page):
    """O retorno aprovado na revisao e o retorno que o Historico mostrara.

    A formula do retorno esta implementada DUAS vezes: no modal (camada de
    dominio) e em histReturnPct (camada de interface). Sao numeros que precisam
    coincidir para sempre — o operador aprova um percentual e o Historico exibe
    aquele percentual anos depois. Enquanto houver duas implementacoes, este
    teste e o que impede a deriva silenciosa entre elas.
    """
    r = page.evaluate(
        """() => {
          const ler = (semBase) => {
            __semear({id: semBase ? 'op_ret_sembase' : 'op_ret_com'});
            const bak = S.params.saldoIni;
            if (semBase) S.params.saldoIni = 0;
            save();
            JPWOperation.openReview();
            const mostrado = __revisao()['Retorno sobre a base do ciclo'];
            __digitar('#finalDefenses', '0');
            __digitar('#finalConfirm', 'FECHADO');
            document.getElementById('modalConfirm').click();
            const recs = S.operationHistory.records;
            const rec = recs[recs.length-1] || null;
            S.params.saldoIni = bak;
            if (!rec) return {mostrado, gravou:false};
            const pct = histReturnPct(rec);
            return {mostrado, gravou:true, base: rec.referenceBalance,
                    historico: pct == null ? '—' : pct.toFixed(2) + '%'};
          };
          return {comBase: ler(false), semBase: ler(true)};
        }"""
    )
    for rotulo, c in (("com base", r["comBase"]), ("sem base", r["semBase"])):
        assert c["gravou"], f"{rotulo}: a finalizacao nao produziu registro"
        assert c["mostrado"] == c["historico"], (
            f"{rotulo}: a revisao mostrou {c['mostrado']!r} e o Historico mostrara "
            f"{c['historico']!r} para o MESMO registro — as duas implementacoes "
            "da formula do retorno divergiram"
        )
    assert r["comBase"]["mostrado"] != "—", (
        "o caso com base valida caiu no ramo indisponivel; a comparacao seria vacua"
    )
    assert r["semBase"]["mostrado"] == "—", (
        f"base ausente deveria ser indisponivel, veio {r['semBase']['mostrado']!r} — "
        "um denominador inexistente nao pode virar percentual"
    )
    assert r["semBase"]["base"] is None, (
        f"base congelada indevida: {r['semBase']['base']!r}"
    )


def run_review_non_integer_defenses_rejected(page):
    """Entrada nao-inteira: a regex estrita e um parseInt frouxo divergem AQUI.

    Os demais casos usam '4', '7', '0', '12' e '' — para todos eles as duas
    regras devolvem o mesmo resultado, entao nenhum deles prendia
    operationParseDefenses. '2.5' e '3x' sao os valores em que um parse frouxo
    persistiria 2 e 3 num registro imutavel enquanto a revisao dizia "Não
    informado". As duas metades sao asseveradas: o que a revisao mostra E o que
    a confirmacao faz.
    """
    r = page.evaluate(
        """() => {
          const casos = ['2.5', '3x', ' 4 4', '-1', '1e2'];
          const out = [];
          for (const txt of casos) {
            __semear({id:'op_parse_'+casos.indexOf(txt)});
            save();
            JPWOperation.openReview();
            __digitar('#finalDefenses', txt);
            const mostrado = __revisao()['Defesas informadas'];
            __digitar('#finalConfirm', 'FECHADO');
            document.getElementById('modalConfirm').click();
            out.push({
              txt, mostrado,
              registros: S.operationHistory.records.length,
              erroAceso: !!document.querySelector('[data-qid="defesas"] .modal-err.show'),
              aindaAberto: document.getElementById('modalOverlay').classList.contains('show')
            });
            closeModal();
          }
          return {out};
        }"""
    )
    for c in r["out"]:
        assert c["mostrado"] == "Não informado", (
            f"{c['txt']!r}: a revisao mostrou {c['mostrado']!r} — um parse frouxo "
            "leu um numero onde a regra estrita nao le nenhum"
        )
        assert c["registros"] == 0, (
            f"{c['txt']!r}: a finalizacao PERSISTIU um registro com defesas "
            "derivadas de texto que a revisao declarou nao informado"
        )
        assert c["erroAceso"], f"{c['txt']!r}: entrada invalida sem erro visivel"
        assert c["aindaAberto"], f"{c['txt']!r}: o modal fechou apesar da recusa"


def run_review_shows_frozen_return_base(page):
    """A base do retorno e persistida e imutavel: precisa estar na revisao.

    Ela deriva de um parametro manual (saldo inicial do ciclo) e fica CONGELADA
    no registro para continuar auditavel anos depois. Exibir so a porcentagem
    fazia 250/10000 e 250/12500 chegarem ao operador como uma unica linha de
    leitura, sem meio de distinguir qual denominador seria gravado.
    """
    r = page.evaluate(
        """() => {
          __semear({id:'op_base_visivel'});
          S.params.saldoIni = 12500;
          save();
          JPWOperation.openReview();
          const previa = __revisao();
          __digitar('#finalDefenses', '0');
          __digitar('#finalConfirm', 'FECHADO');
          document.getElementById('modalConfirm').click();
          const recs = S.operationHistory.records;
          const rec = recs[recs.length-1] || null;
          return {previa, gravou: !!rec,
                  base: rec ? rec.referenceBalance : null,
                  esperado: rec ? fmtMoney2(rec.referenceBalance) : null};
        }"""
    )
    assert r["gravou"], "a finalizacao nao produziu registro"
    assert r["base"] == 12500, f"base congelada inesperada: {r['base']!r}"
    assert "Base do retorno" in r["previa"], (
        f"a revisao nao exibe a base do retorno; linhas: {list(r['previa'])} — o "
        "operador aprova uma porcentagem sem ver o denominador que sera gravado"
    )
    assert r["previa"]["Base do retorno"] == r["esperado"], (
        f"a base exibida {r['previa']['Base do retorno']!r} diverge da persistida "
        f"{r['esperado']!r}"
    )


def run_review_without_identity_claims_nothing(page):
    """Sem identidade, a revisao nao inventa fase maxima nem promete registro.

    O fallback anterior fabricava {operationId:'(será gerado na confirmação)'}.
    Por ser string nao-vazia ele atravessava a guarda de
    operationResolveGridPhaseMax — que existe para devolver null sem identidade
    — e a revisao afirmava "Fase 1" como maximo OBSERVADO de uma operacao sem
    evento escopado nenhum. Desconhecido coagido a zero, sobre um registro que
    finalizeOperation recusaria por no_identity.
    """
    r = page.evaluate(
        """() => {
          __semear({id:'op_sem_id'});
          S.activeOperation = null;
          save();
          const antes = S.operationHistory.records.length;
          JPWOperation.openReview();
          const rev = __revisao();
          const texto = document.getElementById('modalBox').textContent;
          const temConfirmar = !!document.getElementById('modalConfirm');
          const res = JPWOperation.finalize({defenseCount:0});
          return {linhas: Object.keys(rev), faseGrade: rev['Fase máxima da Grade'],
                  texto, temConfirmar, motivo: res.motivo,
                  antes, depois: S.operationHistory.records.length};
        }"""
    )
    assert r["motivo"] == "no_identity", (
        f"o dominio deixou de recusar a operacao sem identidade: {r['motivo']!r}"
    )
    assert r["faseGrade"] is None, (
        f"a revisao afirmou 'Fase máxima da Grade: {r['faseGrade']}' para uma "
        "operacao SEM identidade — nenhum evento do transitionLog pode estar "
        "escopado nela, entao nao existe maximo observado a afirmar"
    )
    assert not r["temConfirmar"], (
        "a revisao ofereceu o botao de finalizar para uma operacao que o "
        "dominio recusa; o operador preencheria tudo para receber no_identity"
    )
    assert "identidade" in r["texto"], (
        f"a revisao nao explica por que nao da para finalizar: {r['texto'][:160]!r}"
    )
    assert r["depois"] == r["antes"] == 0, "algo foi persistido sem identidade"


def run_review_error_follows_the_repaint(page):
    """O modal nao pode afirmar duas coisas contraditorias ao mesmo tempo.

    Ligar a revisao ao evento 'input' sem ligar a validacao criava a assimetria:
    a linha "Abertura" ja exibindo a data informada e, logo abaixo, a mensagem
    vermelha dizendo que o campo esta ausente. Antes da mudanca as duas metades
    ficavam defasadas JUNTAS e a tela nunca se contradizia.
    """
    r = page.evaluate(
        """() => {
          __semear({openedAt:null, id:'op_err_sync'});
          save();
          JPWOperation.openReview();
          __digitar('#finalDefenses', '3');
          __digitar('#finalConfirm', 'FECHADO');
          document.getElementById('modalConfirm').click();  // recusa: abertura vazia
          const aceso = !!document.querySelector('[data-qid="abertura"] .modal-err.show');
          __digitar('#finalOpenedAt', 'nao-e-data');
          const aposInvalida = !!document.querySelector('[data-qid="abertura"] .modal-err.show');
          const revisaoInvalida = __revisao()['Abertura'];
          __digitar('#finalOpenedAt', '2026-07-01T09:00');
          const aposValida = !!document.querySelector('[data-qid="abertura"] .modal-err.show');
          const revisaoValida = __revisao()['Abertura'];
          return {aceso, aposInvalida, revisaoInvalida, aposValida, revisaoValida};
        }"""
    )
    assert r["aceso"], "a recusa nao acendeu o erro do campo de abertura"
    assert r["aposInvalida"], (
        "texto invalido APAGOU o erro; a mensagem so pode sair quando a entrada "
        "passa a ser valida"
    )
    assert "Desconhecida" in r["revisaoInvalida"], (
        f"texto invalido virou abertura na revisao: {r['revisaoInvalida']!r}"
    )
    assert not r["aposValida"], (
        f"a revisao passou a exibir {r['revisaoValida']!r} enquanto o campo "
        "continuava marcado em vermelho como ausente — o modal afirma a coisa e "
        "o contrario dela na mesma tela"
    )
    assert "(informada manualmente)" in r["revisaoValida"], (
        f"a revisao nao acompanhou a data valida: {r['revisaoValida']!r}"
    )


def run_review_repaints_after_failed_attempt(page):
    """Retentativa depois de falha revisa de novo, e nao reaprova a tela velha.

    A falha de persistencia mantem o modal aberto e o botao habilitado — a
    segunda tentativa pode acontecer muito depois. Sem repintar, o operador
    reaprovaria uma revisao carimbada na ultima tecla enquanto finalizeOperation
    monta um snapshot novo. A base do retorno serve de sonda: ela deriva de um
    parametro que pode mudar entre as duas tentativas.
    """
    r = page.evaluate(
        """() => {
          __semear({id:'op_retry'});
          S.params.saldoIni = 10000;
          save();
          JPWOperation.openReview();
          __digitar('#finalDefenses', '0');
          __digitar('#finalConfirm', 'FECHADO');
          const antesDaFalha = __revisao()['Base do retorno'];
          // O parametro muda DEPOIS da ultima tecla: sem repintura na falha, a
          // revisao ficaria congelada no valor antigo.
          S.params.saldoIni = 12500;
          jpWealthPersistenceBlocked = true;
          document.getElementById('modalConfirm').click();
          jpWealthPersistenceBlocked = false;
          const depoisDaFalha = __revisao()['Base do retorno'];
          const aindaAberto = document.getElementById('modalOverlay').classList.contains('show');
          document.getElementById('modalConfirm').click();   // segunda tentativa
          const recs = S.operationHistory.records;
          const rec = recs[recs.length-1] || null;
          return {antesDaFalha, depoisDaFalha, aindaAberto,
                  gravou: !!rec, basePersistida: rec ? rec.referenceBalance : null,
                  esperado: fmtMoney2(12500)};
        }"""
    )
    assert r["aindaAberto"], "a falha fechou o modal"
    assert r["antesDaFalha"] != r["depoisDaFalha"], (
        f"a revisao NAO foi repintada apos a falha: continuou {r['antesDaFalha']!r} "
        "enquanto o proximo snapshot usaria outro denominador"
    )
    assert r["depoisDaFalha"] == r["esperado"], (
        f"revisao apos a falha: {r['depoisDaFalha']!r}, esperado {r['esperado']!r}"
    )
    assert r["gravou"], "a segunda tentativa nao concluiu"
    assert r["basePersistida"] == 12500, (
        f"a revisao reaprovada e o registro divergiram: exibia "
        f"{r['depoisDaFalha']!r} e persistiu {r['basePersistida']!r}"
    )


# ---------------------------------------------------------------------------
# Consistencia temporal do registro historico (#9)
# ---------------------------------------------------------------------------
# Invariante UNICA: openedAt <= closedAt. Uma operacao nao pode terminar antes
# de comecar. Nenhuma outra regra cronologica entra aqui — nem idade maxima,
# nem horario de mercado, nem dias uteis, nem duracao minima.


def run_chronology_accepts_opening_before_close(page):
    """Abertura anterior ao encerramento: aceita, como sempre foi."""
    r = page.evaluate(
        """() => {
          __semear({openedAt:'2026-08-01T10:00:00.000Z', id:'op_crono_ok'});
          save();
          JPWOperation.openReview();
          const revisao = document.getElementById('finalReview').textContent;
          __digitar('#finalDefenses','0'); __digitar('#finalConfirm','FECHADO');
          document.getElementById('modalConfirm').click();
          const recs = S.operationHistory.records;
          const rec = recs[recs.length-1] || null;
          return {gravou: !!rec, revisao,
                  ordem: rec ? Date.parse(rec.openedAt) <= Date.parse(rec.closedAt) : null};
        }"""
    )
    assert r["gravou"], "operacao cronologicamente valida foi recusada"
    assert r["ordem"] is True, "registro gravado fora de ordem"
    assert "posterior ao encerramento" not in r["revisao"], (
        "a revisao acusou cronologia impossivel num caso valido"
    )


def run_chronology_accepts_equal_timestamps(page):
    """openedAt == closedAt nao e proibido por esta regra.

    Igualdade exige relogio controlado: sem isso a comparacao seria "openedAt
    anterior por alguns milissegundos", que e outro caso. O relogio e congelado
    so durante a construcao e restaurado em seguida.
    """
    r = page.evaluate(
        """() => {
          const Real = Date;
          const fixo = Real.parse('2026-08-17T12:00:00.000Z');
          const Falso = class extends Real {
            constructor(...a){ if(!a.length) super(fixo); else super(...a); }
            static now(){ return fixo; }
          };
          __semear({openedAt:'2026-08-17T12:00:00.000Z', id:'op_crono_igual'});
          save();
          let res, snap;
          try {
            window.Date = Falso;
            snap = JPWOperation.buildSnapshot(S.activeOperation, {defenseCount:0});
            res = JPWOperation.finalize({defenseCount:0});
          } finally { window.Date = Real; }
          const recs = S.operationHistory.records;
          const rec = recs[recs.length-1] || null;
          return {snapOk: snap.ok, motivo: snap.motivo || null,
                  iguais: snap.ok ? snap.record.openedAt === snap.record.closedAt : null,
                  finalizou: res.ok, gravou: !!rec};
        }"""
    )
    assert r["snapOk"], (
        f"abertura IGUAL ao encerramento foi recusada por {r['motivo']!r} — a "
        "regra e openedAt > closedAt, nao >="
    )
    assert r["iguais"] is True, (
        "o relogio nao ficou congelado; o caso testado nao foi o de igualdade"
    )
    assert r["finalizou"] and r["gravou"], "a finalizacao com timestamps iguais falhou"


def run_chronology_blocks_future_opening_in_review(page):
    """Abertura posterior ao encerramento: a revisao ACUSA e o botao bloqueia.

    '—' significa dado indisponivel. Cronologia impossivel e dado contraditorio,
    e os dois estados nao podem ter a mesma apresentacao — era assim que o
    operador confirmava um registro imutavel afirmando que a operacao foi aberta
    depois de encerrada.
    """
    r = page.evaluate(
        """() => {
          __semear({openedAt:null, id:'op_crono_futuro'});
          save();
          const antes = {ciclo:S.cycleRealizado, registros:S.operationHistory.records.length,
                         ordens:JPWOperation.liveOrders().length,
                         fases:JSON.parse(JSON.stringify(S.phaseUnlocked)),
                         opId:S.activeOperation.operationId};
          JPWOperation.openReview();
          __digitar('#finalOpenedAt','2029-01-01T00:00');
          const revisao = document.getElementById('finalReview').textContent;
          const linhas = __revisao();
          const erroTexto = document.querySelector('[data-qid="abertura"] .modal-err').textContent;
          const erroAceso = !!document.querySelector('[data-qid="abertura"] .modal-err.show');
          __digitar('#finalDefenses','0'); __digitar('#finalConfirm','FECHADO');
          document.getElementById('modalConfirm').click();
          const depois = {ciclo:S.cycleRealizado, registros:S.operationHistory.records.length,
                          ordens:JPWOperation.liveOrders().length,
                          fases:JSON.parse(JSON.stringify(S.phaseUnlocked)),
                          opId:S.activeOperation && S.activeOperation.operationId};
          const disco = JSON.parse(localStorage.getItem('jpwealth_v9_state') || 'null');
          return {revisao, linhas, erroTexto, erroAceso, antes, depois,
                  aindaAberto: document.getElementById('modalOverlay').classList.contains('show'),
                  discoRegistros: disco ? (disco.operationHistory.records||[]).length : null};
        }"""
    )
    assert "posterior ao encerramento" in r["revisao"], (
        f"a revisao nao acusou a cronologia impossivel; exibiu {r['revisao'][:160]!r}"
    )
    assert "Duração até agora" not in r["linhas"], (
        "a revisao seguiu exibindo linhas normais e escondeu a contradicao num "
        "traco de 'indisponivel'"
    )
    assert r["erroAceso"], "o campo de abertura nao foi marcado como invalido"
    assert "posterior ao encerramento" in r["erroTexto"], (
        f"o campo diz {r['erroTexto']!r} — dizer 'informe a data' a quem ja "
        "informou mente sobre o que esta errado"
    )
    assert r["aindaAberto"], "o modal fechou apesar da recusa"
    a, d = r["antes"], r["depois"]
    assert d["registros"] == a["registros"] == 0, f"historico recebeu registro: {d['registros']}"
    assert r["discoRegistros"] == 0, f"disco recebeu registro: {r['discoRegistros']}"
    assert d["ciclo"] == a["ciclo"], f"cycleRealizado consolidou: {a['ciclo']} -> {d['ciclo']}"
    assert d["ordens"] == a["ordens"], f"grades foram zeradas: {a['ordens']} -> {d['ordens']}"
    assert d["fases"] == a["fases"], "fases foram retravadas"
    assert d["opId"] == a["opId"], "a identidade da operacao viva se perdeu"


def run_chronology_domain_blocks_ui_bypass(page):
    """A protecao nao vive so na interface.

    Duas rotas que nao passam pela tela: chamada direta de finalize com
    openedAtManual no futuro, e entidade cuja PROPRIA openedAt ja e futura
    (estado corrompido ou vindo de importacao). As duas sao recusadas pelo
    dominio, e nada e mutado.
    """
    r = page.evaluate(
        """() => {
          const out = {};
          // (a) bypass pela chamada direta, sem abrir o modal
          __semear({openedAt:null, id:'op_bypass_a'});
          save();
          const antesA = JSON.stringify(S);
          const a = JPWOperation.finalize({defenseCount:0, openedAtManual:'2029-01-01T00:00'});
          out.a = {motivo:a.motivo, ok:a.ok, estadoIntacto: JSON.stringify(S) === antesA};
          // (b) a propria entidade tem abertura no futuro
          __semear({openedAt:'2031-05-05T10:00:00.000Z', id:'op_bypass_b'});
          save();
          const antesB = JSON.stringify(S);
          const b = JPWOperation.finalize({defenseCount:0});
          out.b = {motivo:b.motivo, ok:b.ok, estadoIntacto: JSON.stringify(S) === antesB};
          return out;
        }"""
    )
    for rot, c in (("chamada direta", r["a"]), ("entidade com abertura futura", r["b"])):
        assert c["ok"] is False, f"{rot}: o dominio ACEITOU cronologia impossivel"
        assert c["motivo"] == "chronology_invalid", (
            f"{rot}: recusado por {c['motivo']!r} em vez da regra cronologica"
        )
        assert c["estadoIntacto"], (
            f"{rot}: a recusa mutou o estado — nenhuma mutacao pode sobreviver a "
            "uma finalizacao rejeitada"
        )


def run_chronology_guard_holds_without_repaint(page):
    """A guarda do botao responde sozinha quando nenhuma repintura ocorreu.

    Caminho isolado de proposito: a data futura e atribuida ao campo SEM evento
    'input', depois do ultimo evento valido. Nenhuma repintura roda com esse
    valor, entao a revisao continua dizendo "Desconhecida" e quem tem de barrar
    e a guarda do proprio botao — que pergunta ao dominio em vez de
    reimplementar a comparacao. E tambem o unico caminho em que revisao e
    registro ainda poderiam divergir.
    """
    r = page.evaluate(
        """() => {
          __semear({openedAt:null, id:'op_crono_sem_repintura'});
          save();
          const antes = JSON.stringify(S);
          JPWOperation.openReview();
          __digitar('#finalDefenses','0');
          __digitar('#finalConfirm','FECHADO');
          // Sem evento: a repintura NAO roda com este valor.
          document.getElementById('finalOpenedAt').value = '2029-01-01T00:00';
          const revisaoAntes = document.getElementById('finalReview').textContent;
          // Sonda: a guarda do botao tem de barrar ANTES de invocar a transacao.
          // Se finalizeOperation for chamada, o contador sobe.
          const realFinalize = window.finalizeOperation;
          let chamadas = 0;
          window.finalizeOperation = (...a) => { chamadas++; return realFinalize(...a); };
          document.getElementById('modalConfirm').click();
          window.finalizeOperation = realFinalize;
          return {
            revisaoAntes, chamadas,
            falhaVisivel: !document.querySelector('[data-qid="falha"]').hidden,
            erroTexto: document.querySelector('[data-qid="abertura"] .modal-err').textContent,
            erroAceso: !!document.querySelector('[data-qid="abertura"] .modal-err.show'),
            registros: S.operationHistory.records.length,
            estadoIntacto: JSON.stringify(S) === antes,
            aindaAberto: document.getElementById('modalOverlay').classList.contains('show')
          };
        }"""
    )
    assert "Desconhecida" in r["revisaoAntes"], (
        "a repintura rodou com a data futura; o caminho isolado nao foi exercido "
        "e o teste mediria a guarda da revisao, nao a do botao"
    )
    assert r["registros"] == 0, (
        "a finalizacao PERSISTIU um registro cronologicamente impossivel por uma "
        "rota que nao passou pela revisao"
    )
    assert r["estadoIntacto"], "a recusa mutou o estado"
    assert r["erroAceso"], "o campo nao foi marcado como invalido"
    assert "posterior ao encerramento" in r["erroTexto"], (
        f"o campo acusou {r['erroTexto']!r} — dizer 'informe a data/hora' a quem "
        "acabou de informar esconde qual e o defeito real da entrada"
    )
    assert r["aindaAberto"], "o modal fechou apesar da recusa"
    # A guarda da interface existe para dar resposta IMEDIATA, sem entrar na
    # transacao. O dominio recusaria de qualquer forma — e ha teste separado
    # provando isso —, mas quem barra aqui e a tela, e barrar depois de invocar
    # a finalizacao nao e a mesma coisa que barrar antes.
    assert r["chamadas"] == 0, (
        f"finalizeOperation foi invocada {r['chamadas']}x apesar de a entrada ser "
        "cronologicamente impossivel; a interface delegou ao dominio o que devia "
        "recusar de imediato"
    )
    assert not r["falhaVisivel"], (
        "a recusa apareceu na caixa de falha da transacao em vez de no campo que "
        "esta invalido"
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
            run_grid_phase_scoped_by_operation(page)
            run_transition_events_are_stamped(page)
            run_idempotency(page)
            run_persistence_failure_rollback(page)
            run_save_exception_full_rollback(page)
            run_save_exception_after_write_keeps_result(page)
            run_persisted_probe_cannot_be_fooled(page)
            run_identity_not_forged_in_finalize(page)
            run_identity_born_in_lifecycle(page)
            run_save_hook_never_resurrects(page)
            run_snapshot_is_independent(page)
            run_return_is_frozen(page)
            run_degraded_integrity_preserved(page)
            run_thesis_conflict_reported(page)
            # ---- trilha de auditoria na mesma transacao (#4) ----
            page.evaluate(AUDIT_HELPER)
            run_audit_is_in_the_persisted_document(page)
            run_audit_uses_the_real_operation_identity(page)
            run_audit_rolled_back_on_persist_failure(page)
            run_audit_rolled_back_on_exception_before_write(page)
            run_audit_survives_exception_after_write(page)
            run_audit_single_event_per_operation(page)
            # ---- Camada 2B ----
            run_modal_opens_without_mutation(page)
            run_modal_cancel_no_mutation(page)
            run_wrong_confirmation_no_mutation(page)
            run_empty_defenses_is_not_zero(page)
            run_legacy_requires_manual_date(page)
            run_degraded_shown_in_review(page)
            run_persist_failure_keeps_modal(page)
            run_double_click_single_finalization(page)
            # ---- revisao = snapshot (#5) ----
            page.evaluate(REVISAO_HELPER)
            run_review_equals_persisted_record(page)
            run_review_recalculates_on_opened_at_change(page)
            run_review_absent_defenses_is_not_zero(page)
            run_review_explicit_zero_is_shown_and_persisted(page)
            run_review_promises_no_fixed_closing_time(page)
            run_review_repaint_preserves_typing(page)
            run_review_return_matches_history_formula(page)
            run_review_non_integer_defenses_rejected(page)
            run_review_shows_frozen_return_base(page)
            run_review_without_identity_claims_nothing(page)
            run_review_error_follows_the_repaint(page)
            run_review_repaints_after_failed_attempt(page)
            # ---- consistencia temporal (#9) ----
            run_chronology_accepts_opening_before_close(page)
            run_chronology_accepts_equal_timestamps(page)
            run_chronology_blocks_future_opening_in_review(page)
            run_chronology_domain_blocks_ui_bypass(page)
            run_chronology_guard_holds_without_repaint(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("OPERATION FINALIZE TEST PASS")


if __name__ == "__main__":
    main()
