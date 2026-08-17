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

// ---- SUPERFÍCIE DE REVISÃO (Camada 2B) ----
// A revisão faz parte do protocolo de segurança, não do acabamento: dialogs
// nativos encadeados não são equivalentes a uma superfície que mostra a
// operação inteira antes de destruí-la. Reutiliza o modal do projeto
// (#modalOverlay/#modalBox, closeModal) — nenhum sistema paralelo.
//
// A UI NÃO consolida nada. Ela coleta, revisa e chama finalizeOperation();
// quem decide é o domínio.

function operationFmtDuration(openedAt, closedAt){
  const a=Date.parse(openedAt), b=Date.parse(closedAt);
  if(!Number.isFinite(a) || !Number.isFinite(b) || b<a) return '—';
  const min=Math.floor((b-a)/60000);
  const d=Math.floor(min/1440), h=Math.floor((min%1440)/60), m=min%60;
  if(d) return d+'d '+h+'h';
  if(h) return h+'h '+String(m).padStart(2,'0')+'min';
  return m+'min';
}

function operationFmtPhase(idx){
  if(!Number.isFinite(+idx)) return '—';
  const f=(S.matrix||[])[+idx];
  return (f && f.nome) ? f.nome : ('Fase '+((+idx)+1));
}

function operationReviewRow(rotulo, valor){
  return '<div class="modal-q"><div class="ql">'+esc(rotulo)+'</div><div class="op-final-val">'+esc(valor)+'</div></div>';
}

function openFinalizeOperationModal(){
  const pre=operationCanFinalize();
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  if(!pre.ok){
    box.innerHTML='<h3>Finalizar Operação Única</h3>'+
      '<div class="modal-sub">'+esc(pre.mensagem||'A operação não pode ser finalizada agora.')+'</div>'+
      '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Fechar</button></div>';
    $('modalCancel').addEventListener('click',closeModal);
    $('modalCancel').focus();
    return;
  }
  const op=S.activeOperation||{operationId:'(será gerado na confirmação)'};
  // PRÉVIA: construída só para ser lida. buildSnapshot não muta estado algum.
  const previa=operationBuildSnapshot(op,{defenseCount:0});
  if(!previa.ok && (previa.motivo==='instrument_conflict' || previa.motivo==='direction_conflict')){
    const qual=previa.motivo==='instrument_conflict'?'instrumentos':'direções';
    box.innerHTML='<h3>Finalizar Operação Única</h3>'+
      '<div class="modal-sub">As ordens desta operação têm '+esc(qual)+' divergentes: <b>'+esc(previa.valores.join(' · '))+'</b>.<br>'+
      'A finalização está bloqueada. O sistema não escolhe um valor por você — isso criaria memória histórica falsa.</div>'+
      '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Fechar</button></div>';
    $('modalCancel').addEventListener('click',closeModal);
    $('modalCancel').focus();
    return;
  }
  if(!previa.ok){
    box.innerHTML='<h3>Finalizar Operação Única</h3>'+
      '<div class="modal-sub">Não foi possível montar a revisão ('+esc(previa.motivo)+').</div>'+
      '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Fechar</button></div>';
    $('modalCancel').addEventListener('click',closeModal);
    $('modalCancel').focus();
    return;
  }
  const r=previa.record;
  const legada=!r.openedAt;
  const retorno=(r.referenceBalance>0)?((r.netResult/r.referenceBalance)*100).toFixed(2)+'%':'—';
  const degradada=r.maxAccountPhaseIntegrity==='degraded';

  box.innerHTML=
    '<h3>Finalizar Operação Única</h3>'+
    '<div class="modal-sub">Encerra formalmente a tese, preserva a operação no Histórico, consolida o resultado no ciclo e libera as grades. '+
    'Diferente de <b>fechar uma ordem</b>, que encerra apenas uma posição individual.</div>'+
    operationReviewRow('Instrumento', r.instrument||'—')+
    operationReviewRow('Direção', r.direction||'—')+
    operationReviewRow('Abertura', r.openedAt?new Date(r.openedAt).toLocaleString('pt-BR'):'Desconhecida')+
    operationReviewRow('Encerramento formal', new Date(r.closedAt).toLocaleString('pt-BR'))+
    operationReviewRow('Duração', r.openedAt?operationFmtDuration(r.openedAt,r.closedAt):'—')+
    operationReviewRow('Ordens da operação', String(r.ordersSnapshot.length))+
    operationReviewRow('Resultado líquido', fmtMoney2(r.netResult))+
    operationReviewRow('Retorno sobre a base do ciclo', retorno)+
    operationReviewRow('Fase máxima da Conta', operationFmtPhase(r.maxAccountPhaseReached))+
    operationReviewRow('Fase máxima da Grade', r.maxGridPhaseReached==null?'—':operationFmtPhase(r.maxGridPhaseReached))+
    (degradada?('<div class="modal-q" data-qid="integridade"><div class="ql">Integridade da Fase máxima da Conta: <b>Degradada</b></div>'+
      '<div class="modal-sub">Houve falha de captura durante esta operação. O valor acima é o maior <b>conhecido</b>, não necessariamente o máximo absoluto atingido. A finalização não é bloqueada por isso.</div></div>'):'')+
    (legada?('<div class="modal-q" data-qid="abertura"><div class="ql">Data/hora de abertura da operação — obrigatória, pois não foi registrada automaticamente:</div>'+
      '<input type="datetime-local" id="finalOpenedAt"><div class="modal-err">Informe a data/hora de abertura.</div></div>'):'')+
    '<div class="modal-q" data-qid="defesas"><div class="ql">Número de defesas realizadas (inteiro ≥ 0):</div>'+
    '<input type="text" inputmode="numeric" id="finalDefenses" autocomplete="off" placeholder="informe">'+
    '<div class="modal-sub">O modelo de ordens não classifica defesa; a contagem é informada e fica registrada como tal.</div>'+
    '<div class="modal-err">Informe um inteiro maior ou igual a zero.</div></div>'+
    '<div class="modal-q" data-qid="confirmtxt"><div class="ql">Digite <b>FECHADO</b> para confirmar:</div>'+
    '<input type="text" id="finalConfirm" autocomplete="off"><div class="modal-err">Precisa digitar exatamente "FECHADO".</div></div>'+
    '<div class="modal-q" data-qid="falha" hidden><div class="modal-err show" id="finalFail"></div></div>'+
    '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Cancelar</button>'+
    '<button class="modal-btn confirm" id="modalConfirm">Finalizar Operação</button></div>';

  $('modalCancel').addEventListener('click',closeModal);
  const erro=(qid,on)=>{ const n=box.querySelector('[data-qid="'+qid+'"] .modal-err'); if(n) n.classList.toggle('show',!!on); };
  const btn=$('modalConfirm');
  btn.addEventListener('click',()=>{
    if(btn.disabled) return; // reentrância: o segundo clique não passa
    erro('defesas',false); erro('confirmtxt',false); if(legada) erro('abertura',false);
    let falhou=false;
    // Campo VAZIO não vira 0 em silêncio: zero defesas é uma afirmação do
    // operador, e precisa ser digitada.
    const dTxt=String(box.querySelector('#finalDefenses').value||'').trim();
    const d=/^\d+$/.test(dTxt)?parseInt(dTxt,10):NaN;
    if(!Number.isFinite(d)){ erro('defesas',true); falhou=true; }
    let openedAtManual='';
    if(legada){
      openedAtManual=String(box.querySelector('#finalOpenedAt').value||'').trim();
      if(!openedAtManual || !Number.isFinite(Date.parse(openedAtManual))){ erro('abertura',true); falhou=true; }
    }
    if(String(box.querySelector('#finalConfirm').value||'').trim()!=='FECHADO'){ erro('confirmtxt',true); falhou=true; }
    if(falhou) return;

    btn.disabled=true;
    const res=finalizeOperation({defenseCount:d, openedAtManual});
    if(!res.ok){
      // Falha NÃO fecha o modal comunicando sucesso. A operação continua viva
      // e o operador pode tentar de novo.
      const cx=box.querySelector('[data-qid="falha"]');
      const msg=box.querySelector('#finalFail');
      if(cx&&msg){ msg.textContent=res.mensagem||('A finalização não foi concluída ('+res.motivo+'). Nada foi alterado.'); cx.hidden=false; }
      btn.disabled=false;
      return;
    }
    closeModal();
    if(typeof render==='function') render();
    if(typeof renderPhases==='function') renderPhases();
    if(typeof renderLedger==='function') renderLedger();
  });
  const foco=box.querySelector(legada?'#finalOpenedAt':'#finalDefenses');
  if(foco) foco.focus();
}

// Superfície pública consumida pela interface (Painel Operacional) e pelos
// testes. O domínio não conhece DOM; a revisão é a única parte que o conhece.
window.JPWOperation = {
  canFinalize: operationCanFinalize,
  buildSnapshot: operationBuildSnapshot,
  finalize: finalizeOperation,
  liveOrders: operationLiveOrders,
  openReview: openFinalizeOperationModal
};
