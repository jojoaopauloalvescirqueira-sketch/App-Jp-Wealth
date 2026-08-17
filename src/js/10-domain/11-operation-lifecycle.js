// ============ OPERAÇÃO ÚNICA · FINALIZAÇÃO TRANSACIONAL (Camada 2 — N3) ============
// Autoridade ÚNICA de encerramento. O arquivamento legado
// (30-accounting/04-patrimonial-simulation.js) passou a delegar para cá; não
// existem dois caminhos de consolidação, e por isso não existe risco de dupla
// contabilização em cycleRealizado.
//
// A ordem do fluxo antigo era destrutiva: consolidava, empurrava o log, ZERAVA
// as grades e só então chamava save() — cujo retorno era ignorado. Se a
// gravação falhasse (modo de recuperação A-005, cota cheia, bloqueio de
// persistência), a operação já tinha sido apagada da memória e nada dela
// sobrevivia. Aqui a regra é a inversa: preservar primeiro, consolidar depois,
// apagar por último — e apagar só dentro de um estado que já foi persistido.
//
// NADA de norma muda: netOpAtual() continua sendo a fórmula canônica do
// resultado, cycleRealizado continua sendo "resultado líquido acumulado de
// operações arquivadas no ciclo" e é incrementado exatamente UMA vez por
// operação formalmente finalizada.

const OPERATION_HISTORY_SCHEMA_VERSION = 1;
const OPERATION_GRID_SIZES = [5, 4, 3, 2];

// Guarda de reentrância NO DOMÍNIO, e não apenas na interface. Desabilitar o
// botão protege contra o segundo clique; não protege contra uma segunda chamada
// programática, e é a consolidação financeira que está em jogo.
let operationFinalizeInFlight = false;

// Uma ordem "existe" para efeito de operação quando tem status operacional.
// Linha em branco não conta — nem para snapshot, nem para ordersCount.
function operationOrderIsLive(o){
  return !!o && (o.status === 'Aberta' || o.status === 'Fechada' || o.status === 'Migrada');
}

function operationLiveOrders(){
  const out = [];
  (S.phases || []).forEach((ph, pi) => {
    ((ph && ph.orders) || []).forEach((o, oi) => { if (operationOrderIsLive(o)) out.push({ o, pi, oi }); });
  });
  return out;
}

// Pré-condições do encerramento (Art. 3.5§2 preservado).
// Posição aberta BLOQUEIA, sem bypass. Grade inteiramente vazia não oferece o
// que finalizar — e a ausência de operação não é erro, é ausência.
function operationCanFinalize(){
  const vivas = operationLiveOrders();
  const abertas = vivas.filter(x => x.o.status === 'Aberta');
  if (abertas.length) {
    return { ok:false, motivo:'open_position', abertas: abertas.length,
      mensagem:'A Operação não pode ser finalizada enquanto existir posição aberta vinculada à tese.' };
  }
  if (!vivas.length) {
    return { ok:false, motivo:'no_operation',
      mensagem:'Não há operação registrada nas grades para finalizar.' };
  }
  return { ok:true, ordens: vivas.length };
}

// Instrumento e direção vêm da operação, nunca de pergunta ao operador. Se as
// ordens divergirem, o conflito é REPORTADO — escolher uma em silêncio criaria
// memória histórica falsa.
function operationResolveThesis(vivas){
  const pares = [...new Set(vivas.map(x => String(x.o.par || '').trim().toUpperCase()).filter(Boolean))];
  const tipos = [...new Set(vivas.map(x => String(x.o.tipo || '').trim().toUpperCase()).filter(Boolean))];
  if (pares.length > 1) return { ok:false, motivo:'instrument_conflict', valores:pares };
  if (tipos.length > 1) return { ok:false, motivo:'direction_conflict', valores:tipos };
  return { ok:true, instrument: pares[0] || null, direction: tipos[0] || null };
}

// Fase da GRADE máxima, derivada do transitionLog — a única fase com evidência
// histórica no projeto. Só é derivável quando a janela da operação pode ser
// delimitada com segurança: sem openedAt não há recorte, e sem recorte o valor
// seria heurística sobre eventos de outras operações. Nesse caso: null.
function operationResolveGridPhaseMax(openedAt){
  if (typeof openedAt !== 'string' || !openedAt) return null;
  const inicio = Date.parse(openedAt);
  if (!Number.isFinite(inicio)) return null;
  let max = 0; // a Fase 1 está sempre destravada por contrato
  (S.transitionLog || []).forEach(ev => {
    if (!ev || typeof ev !== 'object') return;
    const ts = Date.parse(ev.ts);
    if (!Number.isFinite(ts) || ts < inicio) return;
    const n = Number(ev.fase);
    if (Number.isFinite(n) && n >= 1 && n <= 4) max = Math.max(max, n - 1);
  });
  return max;
}

// Fotografia INDEPENDENTE da operação, construída antes de qualquer destruição.
// structuredClone por campo: o histórico jamais pode manter referência viva para
// S.phases — mutar a próxima operação não pode reescrever a anterior.
function operationBuildSnapshot(op, entrada){
  const vivas = operationLiveOrders();
  const tese = operationResolveThesis(vivas);
  if (!tese.ok) return tese;

  // openedAt legado: informado pelo operador, com proveniência explícita.
  // Nunca Date.now() disfarçado de abertura histórica.
  let openedAt = (typeof op.openedAt === 'string' && op.openedAt) ? op.openedAt : null;
  let openedAtSource = op.openedAtSource || null;
  if (!openedAt && entrada && typeof entrada.openedAtManual === 'string' && entrada.openedAtManual) {
    const t = Date.parse(entrada.openedAtManual);
    if (Number.isFinite(t)) { openedAt = new Date(t).toISOString(); openedAtSource = 'manual_legacy'; }
  }

  const defesas = Number(entrada && entrada.defenseCount);
  if (!Number.isFinite(defesas) || defesas < 0 || Math.floor(defesas) !== defesas) {
    return { ok:false, motivo:'defense_count_invalid' };
  }

  const saldoIni = Number(S.params && S.params.saldoIni);
  const record = {
    schemaVersion: OPERATION_HISTORY_SCHEMA_VERSION,
    operationId: op.operationId,

    instrument: tese.instrument,
    direction: tese.direction,

    openedAt,
    openedAtSource,
    closedAt: new Date().toISOString(),
    closedAtSource: 'formal_confirmation',

    // Base do retorno CONGELADA no registro. Sem isso o retorno de uma operação
    // passada mudaria quando o saldo atual mudasse — o histórico deixaria de ser
    // histórico. O denominador precisa continuar auditável anos depois.
    referenceBalance: Number.isFinite(saldoIni) && saldoIni > 0 ? saldoIni : null,
    referenceBalanceType: 'cycle_initial_balance',

    netResult: netOpAtual(), // fórmula canônica única — nunca reimplementada aqui

    defenseCount: defesas,
    // Não existe campo de papel na ordem; a taxonomia atual é POSICIONAL e
    // frágil (splice promove outra linha a Gênese, o espelhamento duplica
    // linhas). Contagem informada pelo operador, com a proveniência dita.
    defenseCountSource: 'manual',

    maxAccountPhaseReached: Number.isFinite(+op.maxAccountPhaseReached) ? +op.maxAccountPhaseReached : null,
    // Qualidade epistemológica do campo acima. Se houve falha de captura durante
    // a operação, o valor continua sendo o maior OBSERVADO — mas o histórico não
    // pode apresentá-lo como medição completa.
    maxAccountPhaseIntegrity: op.phaseCaptureFault ? 'degraded' : 'observed',
    phaseCaptureFault: op.phaseCaptureFault ? structuredClone(op.phaseCaptureFault) : null,

    maxGridPhaseReached: operationResolveGridPhaseMax(openedAt),

    // Sem identidade estável de ordem no modelo atual: o campo `id` é texto
    // livre do operador e a identidade de facto é posicional. Registramos a
    // posição de origem E o texto, sem fingir que existe orderId.
    ordersSnapshot: vivas.map(({ o, pi, oi }) => ({
      phase: pi + 1,
      gridIndex: oi,
      label: typeof o.id === 'string' ? o.id : '',
      par: o.par || '', tipo: o.tipo || '',
      lote: +o.lote || 0, entry: +o.entry || 0, sl: +o.sl || 0, tp: +o.tp || 0,
      result: +o.result || 0, status: o.status || '',
      openedAt: (typeof o.openedAt === 'string' && o.openedAt) ? o.openedAt : null,
      closedAt: (typeof o.closedAt === 'string' && o.closedAt) ? o.closedAt : null
    })),

    finalizedAt: new Date().toISOString()
  };
  if (op.adoptedLegacyAt) record.adoptedLegacyAt = op.adoptedLegacyAt;
  return { ok:true, record };
}

// Validação do próximo estado ANTES de ele virar o estado vivo. O que se checa
// aqui é exatamente o que não pode acontecer duas vezes nem pela metade.
function operationValidateCandidate(candidato, anterior, record){
  const antesN = ((anterior.operationHistory || {}).records || []).length;
  const depoisN = ((candidato.operationHistory || {}).records || []).length;
  if (depoisN !== antesN + 1) return { ok:false, motivo:'history_not_appended' };

  const ids = (candidato.operationHistory.records || []).map(r => r && r.operationId);
  if (new Set(ids).size !== ids.length) return { ok:false, motivo:'duplicate_operation_id' };

  const esperado = (+anterior.cycleRealizado || 0) + (+record.netResult || 0);
  if (Math.abs((+candidato.cycleRealizado || 0) - esperado) > 1e-9) {
    return { ok:false, motivo:'cycle_not_consolidated_once' };
  }
  if (candidato.activeOperation !== null) return { ok:false, motivo:'operation_not_cleared' };

  const sobrou = (candidato.phases || []).some(ph => ((ph && ph.orders) || []).some(operationOrderIsLive));
  if (sobrou) return { ok:false, motivo:'grid_not_reset' };
  return { ok:true };
}

// ---- TRANSAÇÃO ----
// ou toda a finalização acontece, ou nada acontece.
function finalizeOperation(entrada){
  if (operationFinalizeInFlight) return { ok:false, motivo:'in_flight' };
  operationFinalizeInFlight = true;
  try{
    const pre = operationCanFinalize();
    if (!pre.ok) return pre;

    // Identidade: operação viva sem entidade (fluxo que nunca passou pela
    // abertura da Gênese) recebe id agora, com abertura desconhecida.
    if (!S.activeOperation) {
      S.activeOperation = {
        schemaVersion: 1, operationId: operationRecordId(),
        openedAt: null, openedAtSource: null, maxAccountPhaseReached: null
      };
    }
    const op = S.activeOperation;

    // IDEMPOTÊNCIA: mesmo operationId já no histórico ⇒ nada acontece de novo.
    // Sem isto, um segundo disparo criaria segundo registro, somaria
    // cycleRealizado outra vez e faria segundo reset.
    const jaFinalizada = ((S.operationHistory || {}).records || []).some(r => r && r.operationId === op.operationId);
    if (jaFinalizada) return { ok:false, motivo:'already_finalized', operationId: op.operationId };

    const snap = operationBuildSnapshot(op, entrada);
    if (!snap.ok) return snap;

    // Candidato INDEPENDENTE. A partir daqui nada toca o estado vivo até a troca.
    const anterior = S;
    const candidato = structuredClone(S);
    candidato.operationHistory.records.push(snap.record);
    candidato.cycleRealizado = (+candidato.cycleRealizado || 0) + (+snap.record.netResult || 0);
    candidato.transitionLog.push({
      fase: 'operação finalizada',
      ts: snap.record.closedAt,
      resumo: { operationId: snap.record.operationId, resultado: snap.record.netResult,
                cicloAcumulado: candidato.cycleRealizado }
    });
    candidato.phases.forEach((ph, pi) => { ph.orders = emptyOrders(OPERATION_GRID_SIZES[pi] || 3); });
    candidato.phaseUnlocked = [true, false, false, false];
    candidato.activeOperation = null;

    const val = operationValidateCandidate(candidato, anterior, snap.record);
    if (!val.ok) return val;

    // Troca e persistência. save() serializa a global, então o candidato
    // precisa ser o S no instante da gravação — e volta a ser o anterior se a
    // gravação recusar. É por isso que o retorno de save() é verificado aqui,
    // coisa que o fluxo antigo nunca fez.
    S = candidato;
    if (!save()) {
      S = anterior;
      return { ok:false, motivo:'persist_failed',
        mensagem:'A finalização foi cancelada: o estado não pôde ser gravado. Nada foi alterado.' };
    }
    if (typeof dgLogChange === 'function') {
      dgLogChange('operation', 'finalized', snap.record.operationId, 'Operação Única finalizada e preservada no Histórico');
    }
    return { ok:true, record: snap.record };
  } finally {
    operationFinalizeInFlight = false;
  }
}

// Superfície pública consumida pela interface (Painel Operacional) e pelos
// testes. O domínio não conhece DOM.
window.JPWOperation = {
  canFinalize: operationCanFinalize,
  buildSnapshot: operationBuildSnapshot,
  finalize: finalizeOperation,
  liveOrders: operationLiveOrders
};
