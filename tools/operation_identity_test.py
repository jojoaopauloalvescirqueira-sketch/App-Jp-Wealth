#!/usr/bin/env python3
"""Caracterizacao da Camada 1 — Fundacao da Operacao Unica.

Ate esta versao a Operacao Unica nao existia como entidade: era um conceito
emergente do conteudo das grades. Este teste cobre o que a fundacao passou a
garantir — identidade estavel, ciclo de vida explicito, carimbos por ordem e
captura PROSPECTIVA e MONOTONICA da maior Fase da Conta atingida.

A invariante mais importante aqui nao e "o campo existe": e que informacao
DESCONHECIDA nunca vira zero, agora ou valor presumido. Um openedAt legado
permanece null, e o maximo de fase so cresce a partir do que foi efetivamente
observado.

Todas as fixtures sao SINTETICAS. O teste nao importa backup real e nao toca
credencial.
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
    # Rede externa neutralizada: o teste nao depende de feed nem de cotacao.
    page.route(
        "**/*",
        lambda route: route.continue_()
        if "127.0.0.1" in route.request.url
        else route.fulfill(status=200, content_type="application/json", body="{}"),
    )
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_function("() => typeof save === 'function' && typeof migrate === 'function'")
    return context, page, observed


def run_default_shape(page):
    """Estado novo nasce sem operacao e com envelope de historico vazio."""
    fatos = page.evaluate(
        """() => ({
          activeOperationDefault: DEFAULTS.activeOperation,
          historyDefault: JSON.parse(JSON.stringify(DEFAULTS.operationHistory)),
          temChaves: ('activeOperation' in DEFAULTS) && ('operationHistory' in DEFAULTS)
        })"""
    )
    assert fatos["temChaves"], "DEFAULTS nao declara as chaves da fundacao"
    assert fatos["activeOperationDefault"] is None, (
        f"default de activeOperation deveria ser null (nenhuma operacao em curso), "
        f"recebido {fatos['activeOperationDefault']!r} — objeto vazio seria operacao fantasma"
    )
    assert fatos["historyDefault"] == {"schemaVersion": 1, "records": []}, (
        f"envelope do historico divergente: {fatos['historyDefault']}"
    )


def run_legacy_adoption(page):
    """Operacao legada viva e ADOTADA: ganha identidade sem ganhar passado."""
    fatos = page.evaluate(
        """() => {
          // Estado anterior a esta versao: grades com operacao em curso e
          // nenhuma entidade. Exatamente o que existe hoje em campo.
          S.activeOperation = null;
          S.phases[0].orders[0] = {id:'G1',par:'EURUSD',tipo:'BUY',lote:1,entry:1.1,sl:1.09,tp:1.2,result:0,status:'Aberta'};
          migrate();
          const op = S.activeOperation;
          return {
            criada: !!op,
            id: op && op.operationId,
            openedAt: op && op.openedAt,
            openedAtSource: op && op.openedAtSource,
            maxFase: op && op.maxAccountPhaseReached,
            adotada: !!(op && op.adoptedLegacyAt)
          };
        }"""
    )
    assert fatos["criada"], "operacao legada viva nao foi adotada — ficaria sem identidade para sempre"
    assert isinstance(fatos["id"], str) and fatos["id"], f"identidade ausente: {fatos['id']!r}"
    assert fatos["openedAt"] is None, (
        f"openedAt legado deveria permanecer null, recebido {fatos['openedAt']!r} — "
        "inventar a abertura falsificaria proveniencia"
    )
    assert fatos["openedAtSource"] is None, f"proveniencia inventada: {fatos['openedAtSource']!r}"
    assert fatos["maxFase"] is None, (
        f"maxAccountPhaseReached legado deveria ser null e nao 0: {fatos['maxFase']!r} — "
        "desconhecido nao e Fase 1"
    )
    assert fatos["adotada"], "adocao nao foi marcada"


def run_existing_operation_unknowns(page):
    """Operacao JA existente com campos ausentes: desconhecido continua null.

    Complementa a adocao de legado, que cria o objeto ja normalizado e por isso
    nao exercita o ramo de reparo. Sem este caso, trocar `null` por `0` no
    normalizador passaria despercebido — e `0` nao e ausencia, e' "Fase 1".
    """
    fatos = page.evaluate(
        """() => {
          S.activeOperation = {operationId:'op_preexistente'};   // sem os demais campos
          migrate();
          const a = S.activeOperation;
          S.activeOperation = {operationId:'op_lixo', maxAccountPhaseReached:'abc', openedAt:42, openedAtSource:'inventada'};
          migrate();
          const b = S.activeOperation;
          S.activeOperation = {operationId:'op_alto', maxAccountPhaseReached:99};
          migrate();
          const c = S.activeOperation;
          return {
            idPreservado: a.operationId === 'op_preexistente',
            maxAusente: a.maxAccountPhaseReached,
            openedAtAusente: a.openedAt,
            sourceAusente: a.openedAtSource,
            maxLixo: b.maxAccountPhaseReached,
            openedAtLixo: b.openedAt,
            sourceInvalida: b.openedAtSource,
            maxTeto: c.maxAccountPhaseReached
          };
        }"""
    )
    assert fatos["idPreservado"], "identidade preexistente foi descartada"
    assert fatos["maxAusente"] is None, (
        f"max ausente virou {fatos['maxAusente']!r} — desconhecido nao e Fase 1"
    )
    assert fatos["maxLixo"] is None, f"max invalido virou {fatos['maxLixo']!r}"
    assert fatos["openedAtAusente"] is None and fatos["openedAtLixo"] is None, (
        "openedAt nao-string deveria virar null"
    )
    assert fatos["sourceAusente"] is None, f"proveniencia inventada: {fatos['sourceAusente']!r}"
    assert fatos["sourceInvalida"] is None, (
        f"proveniencia fora do vocabulario aceita: {fatos['sourceInvalida']!r}"
    )
    assert fatos["maxTeto"] == 3, f"max acima do teto nao foi limitado a 3: {fatos['maxTeto']!r}"


def run_unknown_is_never_zero(page):
    """DESCONHECIDO e FASE 1 sao estados diferentes, em toda a cadeia.

    `+null === 0` e `Number.isFinite(0) === true`: qualquer guarda escrita com
    coercao deixa um maximo NUNCA OBSERVADO virar "Fase 1 observada" — e o
    registro do Historico e imutavel, entao a afirmacao falsa fica para sempre.
    """
    r = page.evaluate(
        """() => {
          const casos = {};
          // normalizador
          S.activeOperation = {operationId:'op_n', maxAccountPhaseReached:null};
          migrate(); casos.normNull = S.activeOperation.maxAccountPhaseReached;
          S.activeOperation = {operationId:'op_n'};                       // ausente
          migrate(); casos.normAusente = S.activeOperation.maxAccountPhaseReached;
          S.activeOperation = {operationId:'op_n', maxAccountPhaseReached:'0'};  // string
          migrate(); casos.normString = S.activeOperation.maxAccountPhaseReached;
          S.activeOperation = {operationId:'op_n', maxAccountPhaseReached:0};    // Fase 1 REAL
          migrate(); casos.normZeroReal = S.activeOperation.maxAccountPhaseReached;
          // helper puro
          casos.helperNull = operationPhaseIdxOrNull(null);
          casos.helperZero = operationPhaseIdxOrNull(0);
          // captura: primeira observacao estabelece, mesmo sendo Fase 1
          S.params.saldoIni = 10000;
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.activeOperation = {schemaVersion:1, operationId:'op_cap', openedAt:null,
                               openedAtSource:null, maxAccountPhaseReached:null};
          // A captura NAO mora mais em save(): save() roda a cada tecla, e um
          // valor meio digitado nao pode virar evidencia historica. Aqui se
          // exercita a funcao de captura diretamente, que e o objeto deste teste
          // de unidade; QUAIS atos a disparam e propriedade de fiacao, coberta
          // por run_typing_does_not_forge_account_phase na suite de finalizacao.
          operationTouchAccountPhase();
          casos.aposPrimeiraCaptura = S.activeOperation.maxAccountPhaseReached;
          // renderizadores
          casos.fmtNull = operationFmtPhase(null);
          casos.fmtZero = operationFmtPhase(0);
          return casos;
        }"""
    )
    assert r["normNull"] is None, f"null virou {r['normNull']!r} no normalizador"
    assert r["normAusente"] is None, f"campo ausente virou {r['normAusente']!r}"
    assert r["normString"] is None, f"string '0' virou {r['normString']!r} — backup adulterado"
    assert r["normZeroReal"] == 0, f"Fase 1 REAL foi descartada: {r['normZeroReal']!r}"
    assert r["helperNull"] is None and r["helperZero"] == 0, f"helper: {r}"
    assert r["aposPrimeiraCaptura"] == 0, (
        f"a primeira captura nao estabeleceu o valor: {r['aposPrimeiraCaptura']!r} — "
        "desconhecido nao pode bloquear a observacao de Fase 1"
    )
    assert r["fmtNull"] == "—", f"desconhecido renderizado como {r['fmtNull']!r}"
    assert r["fmtZero"] != "—", f"Fase 1 real renderizada como travessao: {r['fmtZero']!r}"


def run_identity_stability(page):
    """operationId nasce UMA vez e sobrevive a migrate() e save() repetidos."""
    fatos = page.evaluate(
        """() => {
          const antes = S.activeOperation.operationId;
          migrate(); save(); migrate(); save();
          return {antes, depois: S.activeOperation.operationId};
        }"""
    )
    assert fatos["antes"] == fatos["depois"], (
        f"operationId mudou entre chamadas: {fatos['antes']} -> {fatos['depois']} — "
        "identidade recalculavel nao e identidade"
    )


def run_genesis_birth(page):
    """Abrir a Genese faz nascer a operacao com proveniencia automatica."""
    fatos = page.evaluate(
        """() => {
          // Base limpa: nenhuma operacao, grades zeradas.
          S.activeOperation = null;
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          const genese = S.phases[0].orders[0];
          genese.par = 'EURUSD'; genese.lote = 1; genese.entry = 1.1; genese.sl = 1.09;
          genese.status = 'Aberta';
          operationOnOrderStatus(genese, 'Aberta', 0, 0);
          const op = S.activeOperation;
          const primeiroOpenedAt = op.openedAt;
          const primeiroId = op.operationId;
          const ordemOpenedAt = genese.openedAt;
          // SENTINELA, e nao comparacao de relogio. Duas chamadas no mesmo
          // milissegundo produzem toISOString() identico, e a igualdade passaria
          // mesmo com sobrescrita — foi exatamente assim que um defeito plantado
          // sobreviveu ao teste. Marcando com um valor impossivel de ser gerado,
          // qualquer reescrita fica visivel.
          const SENT = '1970-01-01T00:00:00.000Z';
          genese.openedAt = SENT;
          op.openedAt = SENT;
          operationOnOrderStatus(genese, 'Aberta', 0, 0);
          return {
            nasceu: !!op,
            id: primeiroId,
            openedAt: primeiroOpenedAt,
            source: op.openedAtSource,
            ordemOpenedAt,
            openedAtEstavel: op.openedAt === SENT,
            idEstavel: op.operationId === primeiroId,
            ordemEstavel: genese.openedAt === SENT
          };
        }"""
    )
    assert fatos["nasceu"], "abrir a Genese nao criou a Operacao Unica"
    assert fatos["source"] == "genesis_transition", (
        f"proveniencia deveria ser genesis_transition, recebido {fatos['source']!r}"
    )
    assert isinstance(fatos["openedAt"], str) and fatos["openedAt"], "openedAt nao foi carimbado"
    assert isinstance(fatos["ordemOpenedAt"], str), "openedAt da ordem nao foi carimbado"
    assert fatos["openedAtEstavel"], "reabrir reescreveu o openedAt da operacao"
    assert fatos["idEstavel"], "reabrir gerou identidade nova"
    assert fatos["ordemEstavel"], "reabrir reescreveu o openedAt da ordem"


def run_order_close_stamp(page):
    """Fechar carimba closedAt uma vez; fechar de novo nao move o carimbo."""
    fatos = page.evaluate(
        """() => {
          const o = S.phases[0].orders[0];
          operationOnOrderStatus(o, 'Fechada', 0, 0);
          const primeiro = o.closedAt;
          operationOnOrderStatus(o, 'Fechada', 0, 0);
          return {primeiro, segundo: o.closedAt, openedAtIntacto: !!o.openedAt};
        }"""
    )
    assert isinstance(fatos["primeiro"], str) and fatos["primeiro"], "closedAt nao carimbado"
    assert fatos["primeiro"] == fatos["segundo"], (
        f"closedAt reescrito: {fatos['primeiro']} -> {fatos['segundo']}"
    )
    assert fatos["openedAtIntacto"], "fechar apagou o openedAt da ordem"


def run_phase_capture_monotonic(page):
    """maxAccountPhaseReached e capturado em ATO CONFIRMADO e NUNCA regride.

    A captura saiu de save() de proposito: save() roda a cada tecla dos campos
    numericos da grade, e um valor meio digitado nao pode virar evidencia
    historica. Aqui a captura e invocada diretamente — QUAIS atos a disparam e
    propriedade de fiacao, coberta em operation_finalize_test.py.
    """
    fatos = page.evaluate(
        """() => {
          const passos = [];
          const registrar = (rot) => passos.push({
            rot,
            faseAtual: currentAccountPhaseIdx(),
            max: S.activeOperation.maxAccountPhaseReached
          });
          // Fase da Conta deriva do drawdown: risco aberto + perdas.
          // Um prejuizo grande empurra a fase para cima.
          S.params.saldoIni = 10000;
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.phases[0].orders[0] = {id:'G',par:'EURUSD',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,result:0,status:'Fechada'};
          operationTouchAccountPhase(); save(); registrar('inicio');
          // Perda que eleva o drawdown e, com ele, a Fase da Conta.
          S.phases[0].orders[0].result = -900;
          operationTouchAccountPhase(); save(); registrar('apos perda');
          const pico = S.activeOperation.maxAccountPhaseReached;
          // Recuperacao: a fase VIGENTE cai, o maximo NAO pode cair junto.
          S.phases[0].orders[0].result = 0;
          operationTouchAccountPhase(); save(); registrar('apos recuperacao');
          return {passos, pico, maxFinal: S.activeOperation.maxAccountPhaseReached};
        }"""
    )
    passos = fatos["passos"]
    subiu = passos[1]["max"] is not None and (
        passos[0]["max"] is None or passos[1]["max"] >= passos[0]["max"]
    )
    assert subiu, f"maximo nao acompanhou a subida da fase: {passos}"
    assert fatos["maxFinal"] == fatos["pico"], (
        f"maximo REGREDIU quando a fase vigente caiu: pico {fatos['pico']} -> {fatos['maxFinal']} — "
        "monotonicidade e o contrato deste campo"
    )
    assert passos[2]["faseAtual"] is not None, "fase vigente ficou indeterminada"


def run_history_envelope(page):
    """Envelope do historico resiste a forma invalida e a id duplicado."""
    fatos = page.evaluate(
        """() => {
          S.operationHistory = 'lixo';
          migrate();
          const aposLixo = JSON.parse(JSON.stringify(S.operationHistory));
          S.operationHistory.records = [
            {operationId:'dup', schemaVersion:1},
            {operationId:'dup', schemaVersion:1},
            'nao e objeto'
          ];
          migrate();
          const ids = S.operationHistory.records.map(r => r.operationId);
          return {
            aposLixo,
            total: S.operationHistory.records.length,
            unicos: new Set(ids).size,
            temSnapshot: S.operationHistory.records.every(r => Array.isArray(r.ordersSnapshot))
          };
        }"""
    )
    assert fatos["aposLixo"] == {"schemaVersion": 1, "records": []}, (
        f"envelope invalido nao foi reconstruido: {fatos['aposLixo']}"
    )
    assert fatos["total"] == 2, f"registro nao-objeto deveria ser descartado: {fatos['total']}"
    assert fatos["unicos"] == 2, (
        "id duplicado sobreviveu — a idempotencia da finalizacao ficaria ambigua"
    )
    assert fatos["temSnapshot"], "ordersSnapshot nao foi garantido como array"


def run_not_applicable_is_normal_flow(page):
    """Estado legado/insuficiente e NAO APLICAVEL — tratado sem excecao."""
    fatos = page.evaluate(
        """() => {
          S.activeOperation = {schemaVersion:1, operationId:'x', openedAt:null,
                               openedAtSource:null, maxAccountPhaseReached:null};
          const bak = S.params;
          S.params = null;                    // base legada/malformada
          const probe = accountPhaseProbe();
          let ok = null, erro = null;
          try { operationTouchAccountPhase(); ok = save(); } catch(e) { erro = String(e); }
          const fault = S.activeOperation.phaseCaptureFault || null;
          S.params = bak;
          save();
          return {probeOk: probe.ok, probeIdx: probe.idx, ok, erro, fault};
        }"""
    )
    assert fatos["erro"] is None, f"save() lancou: {fatos['erro']}"
    assert fatos["ok"] is True, f"save() deixou de gravar: {fatos['ok']!r}"
    assert fatos["probeOk"] is True and fatos["probeIdx"] is None, (
        f"estado insuficiente deveria ser NAO APLICAVEL (ok=true, idx=null), "
        f"recebido ok={fatos['probeOk']} idx={fatos['probeIdx']!r}"
    )
    assert fatos["fault"] is None, (
        "estado legado foi classificado como DEFEITO — nao aplicavel nao e falha, "
        "e marcar tudo como falha tornaria a marca inutil"
    )


def run_capture_failure_is_observable(page):
    """Falha do MECANISMO nao pode passar por sucesso silencioso.

    Este e o endurecimento exigido: a fase sobe, a reconciliacao quebra, e o
    sistema NAO pode preservar o valor antigo fingindo que capturou. save()
    continua gravando — indisponibilidade global por causa de um campo derivado
    seria troca pior —, mas a lacuna fica registrada na propria entidade.
    """
    fatos = page.evaluate(
        """() => {
          S.params.saldoIni = 10000;
          S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
          S.activeOperation = {schemaVersion:1, operationId:'falha', openedAt:null,
                               openedAtSource:null, maxAccountPhaseReached:0};
          // Defeito INESPERADO do mecanismo — nao ausencia de dado.
          const bak = window.compute;
          window.compute = () => { throw new Error('falha sintetica de reconciliacao'); };
          // Condicao que ELEVARIA a fase se a captura estivesse sa.
          S.phases[0].orders[0] = {id:'G',par:'EURUSD',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,result:-900,status:'Fechada'};
          const probe = accountPhaseProbe();
          let ok = null, erro = null;
          try { operationTouchAccountPhase(); ok = save(); } catch(e) { erro = String(e); }
          const op = S.activeOperation;
          const snapshot = {
            probeOk: probe.ok,
            temRazao: typeof probe.erro === 'string' && probe.erro.length > 0,
            ok, erro,
            max: op.maxAccountPhaseReached,
            fault: op.phaseCaptureFault ? {temAt: !!op.phaseCaptureFault.at,
                                           razao: op.phaseCaptureFault.reason} : null
          };
          window.compute = bak;
          // Sucesso posterior NAO apaga a evidencia da falha.
          operationTouchAccountPhase(); save();
          snapshot.faultPersisteAposSucesso = !!S.activeOperation.phaseCaptureFault;
          return snapshot;
        }"""
    )
    assert fatos["erro"] is None, f"save() lancou: {fatos['erro']}"
    assert fatos["ok"] is True, (
        "save() parou de gravar por causa de um campo derivado — trocaria lacuna "
        "de evidencia por perda de dado do operador"
    )
    assert fatos["probeOk"] is False and fatos["temRazao"], (
        f"defeito do mecanismo foi classificado como ausencia de dado: {fatos}"
    )
    assert fatos["fault"] is not None, (
        "a falha foi ENGOLIDA: o sistema persistiu declarando captura que nao houve"
    )
    assert fatos["fault"]["temAt"] and fatos["fault"]["razao"], (
        f"marca de falha sem conteudo auditavel: {fatos['fault']}"
    )
    assert fatos["max"] == 0, (
        f"o maximo foi alterado apesar da falha: {fatos['max']!r} — "
        "capturar errado e pior que nao capturar"
    )
    assert fatos["faultPersisteAposSucesso"], (
        "um save() bem-sucedido apagou a evidencia da falha anterior — o maximo "
        "pode estar subestimado para sempre e a auditoria perderia o rastro"
    )


# ---------------------------------------------------------------------------
# Interacao C x A: a captura opera sobre a entidade que PERMANECE viva
# ---------------------------------------------------------------------------
# A captura da Fase da Conta rodava ANTES do fail-safe de orfandade. Quando o
# fail-safe descartava uma orfa e uma tese nova nascia no mesmo ato, a captura
# tinha ido para a entidade descartada e a recem-nascida saia sem observacao do
# proprio instante em que nasceu. Nao e afirmacao falsa — e subestimacao
# silenciosa do maximo, que a monotonicidade depois preserva errado.

# Funcao EXPLICITA: com duas atribuicoes soltas o Playwright trata a ultima
# expressao como a funcao a invocar, e chamava __ordemNova sem argumentos.
MONTA_FASE = """() => {
  window.__montaFase = (ciclo) => {
    S.params.saldoIni = 10000;
    // Reconstroi as grades: um caso anterior desta suite pode ter deixado
    // S.phases vazio, e ali o forEach nao lanca — so devolve S.phases[0]
    // indefinido depois, no lugar errado.
    if (!Array.isArray(S.phases) || S.phases.length !== 4) {
      S.phases = structuredClone(DEFAULTS.phases);
    }
    S.phases.forEach((ph,i) => { ph.orders = emptyOrders([5,4,3,2][i]); });
    S.cycleRealizado = ciclo;
    S.activeOperation = null;
    S.operationHistory = {schemaVersion:1, records:[]};
  };
  // Ordem NOVA: sem carimbo algum, e o que o fail-safe exige para agir.
  window.__ordemNova = (pi,oi,par) => {
    const o = S.phases[pi].orders[oi];
    o.id='X'; o.par=par||'EURUSD'; o.tipo='BUY'; o.lote=0.01;
    o.entry=1.10; o.sl=1.09; o.tp=1.20; o.result=0;
    // O status e aplicado ANTES da chamada, como o handler real faz:
    // operationOnOrderStatus so carimba datas e resolve a identidade — quem muda
    // o status e o chamador. Sem isto nenhuma ordem fica viva, o fail-safe de
    // orfandade dispara no ato seguinte e a entidade e trocada por engano.
    o.status='Aberta';
    delete o.openedAt; delete o.closedAt;
    return o;
  };
}
"""


def run_capture_lands_on_existing_entity(page):
    """(1) Entidade normal existente: a captura continua funcionando."""
    r = page.evaluate(
        """() => {
          __montaFase(-900);                       // Fase da Conta = indice 2
          S.activeOperation = {schemaVersion:1, operationId:'op_norm',
            openedAt:'2026-08-01T10:00:00.000Z', openedAtSource:'genesis_transition',
            maxAccountPhaseReached:null};
          const o = __ordemNova(0,0);
          o.openedAt = '2026-08-01T10:00:00.000Z';   // ja pertence: fail-safe nao age
          const faseDoAto = accountPhaseProbe().idx;
          operationOnOrderStatus(o, 'Aberta', 0, 0);
          return {faseDoAto, id:S.activeOperation.operationId,
                  max:S.activeOperation.maxAccountPhaseReached};
        }"""
    )
    assert r["faseDoAto"] == 2, f"fixture nao produziu fase definida: {r['faseDoAto']}"
    assert r["id"] == "op_norm", f"a identidade existente foi trocada: {r['id']!r}"
    assert r["max"] == 2, (
        f"a entidade existente nao recebeu a captura do ato: {r['max']!r}"
    )


def run_capture_lands_on_newborn_entity(page):
    """(2) Nenhuma entidade: nasce, e a fase DAQUELE ato e capturada nela."""
    r = page.evaluate(
        """() => {
          __montaFase(-900);                       // indice 2
          const o = __ordemNova(0,0);
          const faseDoAto = accountPhaseProbe().idx;
          operationOnOrderStatus(o, 'Aberta', 0, 0);
          const op = S.activeOperation;
          return {faseDoAto, nasceu: !!op, fonte: op && op.openedAtSource,
                  max: op && op.maxAccountPhaseReached};
        }"""
    )
    assert r["faseDoAto"] == 2, f"fixture: {r['faseDoAto']}"
    assert r["nasceu"] and r["fonte"] == "genesis_transition", f"nascimento: {r}"
    assert r["max"] == 2, (
        f"a entidade RECEM-NASCIDA saiu com maximo {r['max']!r} — a fase do "
        "proprio instante do nascimento nao foi observada"
    )


def run_orphan_is_discarded_without_receiving_the_capture(page):
    """(3) Orfa + tese nova: a captura vai para a NOVA, nao para a descartada."""
    r = page.evaluate(
        """() => {
          __montaFase(-900);                       // indice 2
          // Orfa: identidade viva sem nenhuma ordem operacional por tras.
          const orfa = {schemaVersion:1, operationId:'op_orfa',
            openedAt:'2026-07-01T10:00:00.000Z', openedAtSource:'genesis_transition',
            maxAccountPhaseReached:null};
          S.activeOperation = orfa;
          const o = __ordemNova(0,0, 'GBPUSD');    // tese NOVA, outro instrumento
          const faseDoAto = accountPhaseProbe().idx;
          operationOnOrderStatus(o, 'Aberta', 0, 0);
          const nova = S.activeOperation;
          return {faseDoAto,
                  orfaMax: orfa.maxAccountPhaseReached,
                  orfaId: orfa.operationId,
                  novaId: nova && nova.operationId,
                  novaMax: nova && nova.maxAccountPhaseReached,
                  novaAbertura: nova && nova.openedAt,
                  novaFonte: nova && nova.openedAtSource};
        }"""
    )
    assert r["faseDoAto"] == 2, f"fixture: {r['faseDoAto']}"
    assert r["novaId"] and r["novaId"] != r["orfaId"], (
        f"a identidade orfa foi HERDADA pela tese nova: {r['novaId']!r}"
    )
    assert r["novaAbertura"] != "2026-07-01T10:00:00.000Z", (
        "a abertura da operacao anterior foi transferida para a tese nova"
    )
    assert r["novaMax"] == 2, (
        f"a entidade nova saiu com maximo {r['novaMax']!r} — a captura foi para a "
        "entidade que seria descartada e o nascimento ficou sem observacao"
    )
    assert r["orfaMax"] is None, (
        f"a orfa DESCARTADA recebeu a captura definitiva ({r['orfaMax']!r}); o "
        "esforco de observacao foi gasto num objeto que deixou de existir"
    )


def run_peak_at_birth_survives_later_recovery(page):
    """(4) Pico so no nascimento: o maximo o preserva depois do recuo."""
    r = page.evaluate(
        """() => {
          __montaFase(-1600);                      // indice 3 — o PICO
          const o = __ordemNova(0,0);
          const faseNoNascimento = accountPhaseProbe().idx;
          operationOnOrderStatus(o, 'Aberta', 0, 0);
          const maxAposNascer = S.activeOperation.maxAccountPhaseReached;
          // A conta se recupera: a fase corrente cai.
          S.cycleRealizado = -200;
          const faseDepois = accountPhaseProbe().idx;
          // Novo ato confirmado, agora numa fase MENOR.
          const o2 = __ordemNova(0,1);
          operationOnOrderStatus(o2, 'Aberta', 0, 1);
          return {faseNoNascimento, maxAposNascer, faseDepois,
                  maxFinal:S.activeOperation.maxAccountPhaseReached};
        }"""
    )
    assert r["faseNoNascimento"] == 3 and r["faseDepois"] == 0, (
        f"a fixture nao produziu pico seguido de recuo: {r}"
    )
    assert r["maxAposNascer"] == 3, (
        f"o pico do nascimento nao foi capturado: {r['maxAposNascer']!r} — sem "
        "essa observacao nao ha o que a monotonicidade preserve depois"
    )
    assert r["maxFinal"] == 3, (
        f"o maximo regrediu para {r['maxFinal']!r} apos o recuo da conta"
    )


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            run_default_shape(page)
            run_legacy_adoption(page)
            run_existing_operation_unknowns(page)
            run_unknown_is_never_zero(page)
            run_identity_stability(page)
            run_genesis_birth(page)
            run_order_close_stamp(page)
            run_phase_capture_monotonic(page)
            run_history_envelope(page)
            run_not_applicable_is_normal_flow(page)
            run_capture_failure_is_observable(page)
            # ---- interacao C x A: ordem da captura ----
            page.evaluate(MONTA_FASE)
            run_capture_lands_on_existing_entity(page)
            run_capture_lands_on_newborn_entity(page)
            run_orphan_is_discarded_without_receiving_the_capture(page)
            run_peak_at_birth_survives_later_recovery(page)
            assert not observed["pageerror"], f"pageerror: {observed['pageerror']}"
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("OPERATION IDENTITY TEST PASS")


if __name__ == "__main__":
    main()
