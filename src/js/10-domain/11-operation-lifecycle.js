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

// Fase da GRADE máxima, derivada dos eventos ESCOPADOS por operationId.
//
// A versão anterior recortava o transitionLog por janela temporal, aberta só na
// borda inferior. O log é cumulativo e nunca podado, então transições de outras
// operações — inclusive posteriores — entravam no cálculo e o registro histórico
// ficava com uma fase que aquela operação nunca alcançou.
//
// Agora o vínculo é explícito: cada evento carrega o operationId da operação
// viva no instante da transição, e só entram os que casam. Não há aproximação
// por cronologia, por ordem dos eventos nem por proximidade do openedAt.
//
// Operação ADOTADA como legada: null. A vida dela anterior a esta versão
// produziu eventos sem vínculo, e não existe delimitação inequívoca — atribuir
// os eventos "que parecem dela" seria exatamente a heurística proibida.
//
// Operação nascida sob o regime novo e sem evento de destravamento: 0. Não é
// suposição — é o contrato estrutural de que a Fase 1 está sempre destravada
// (phaseUnlocked[0]) somado à certeza de que qualquer destravamento posterior
// ao nascimento teria sido carimbado.
function operationResolveGridPhaseMax(op){
  if (!op || typeof op !== 'object') return null;
  if (typeof op.operationId !== 'string' || !op.operationId) return null;
  if (op.adoptedLegacyAt) return null;
  let max = 0;
  (S.transitionLog || []).forEach(ev => {
    if (!ev || typeof ev !== 'object') return;
    if (ev.operationId !== op.operationId) return;
    const idx = (typeof ev.gridPhase === 'number' && Number.isFinite(ev.gridPhase)) ? ev.gridPhase : null;
    if (idx === null) return;   // downgrade e alertas não carregam gridPhase
    max = Math.max(max, Math.min(3, Math.floor(idx)));
  });
  return max;
}

// Uma operação não pode terminar antes de começar. Esta é a única regra
// cronológica desta guarda: nada de idade máxima, horário de mercado, dias
// úteis, duração mínima ou limite de calendário. Só a impossibilidade.
const OPERATION_MSG_ABERTURA_AUSENTE='Informe a data/hora de abertura.';
// Nem sucesso, nem falha comum. O texto NAO oferece "tente de novo": uma nova
// tentativa gravaria, e gravar e exatamente o que nao se pode fazer enquanto o
// desfecho da anterior for desconhecido.
const OPERATION_MSG_DESFECHO_INDETERMINADO='Não foi possível determinar com segurança se a finalização foi persistida. Novas gravações foram bloqueadas para preservar a integridade dos dados. Não repita a operação: verifique o estado gravado antes de qualquer nova ação.';
const OPERATION_MSG_CRONOLOGIA='A data/hora de abertura não pode ser posterior ao encerramento da operação.';

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

  // typeof number, e não Number(): `Number(null) === 0` faria uma contagem
  // AUSENTE virar "zero defesas informadas" — que é uma afirmação do operador,
  // não um default. O mesmo vale para string vazia, que Number() também zera.
  const defesas = (entrada && typeof entrada.defenseCount === 'number') ? entrada.defenseCount : NaN;
  if (!Number.isFinite(defesas) || defesas < 0 || Math.floor(defesas) !== defesas) {
    return { ok:false, motivo:'defense_count_invalid' };
  }

  // closedAt em variavel: a invariante precisa compara-lo com openedAt ANTES de
  // existir registro. Carimbado aqui, no ato da construcao — em finalizeOperation
  // isso e o instante efetivo da confirmacao.
  const closedAt = new Date().toISOString();

  // INTEGRIDADE CRONOLOGICA. Recusa e o unico desfecho: converter para null
  // apagaria uma afirmacao do operador, corrigir automaticamente inventaria
  // dado historico, e substituir por Date.now() seria o "agora disfarcado de
  // abertura" que esta base recusa em todos os outros pontos. Igualdade e
  // permitida — abrir e encerrar no mesmo instante e improvavel, nao impossivel.
  if (openedAt && Date.parse(openedAt) > Date.parse(closedAt)) {
    return { ok:false, motivo:'chronology_invalid',
      openedAt, closedAt, mensagem: OPERATION_MSG_CRONOLOGIA };
  }

  const saldoIni = Number(S.params && S.params.saldoIni);
  const record = {
    schemaVersion: OPERATION_HISTORY_SCHEMA_VERSION,
    operationId: op.operationId,

    instrument: tese.instrument,
    direction: tese.direction,

    openedAt,
    openedAtSource,
    closedAt,
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

    // operationPhaseIdxOrNull e nao `+op.…`: a coercao faria null virar 0 e
    // gravar "Fase 1 observada" num registro IMUTAVEL, sobre uma operação cuja
    // fase máxima nunca foi observada.
    maxAccountPhaseReached: operationPhaseIdxOrNull(op.maxAccountPhaseReached),
    // Qualidade epistemológica do campo acima, em TRÊS estados — porque três são
    // os desfechos reais da captura, e o par observed/degraded os reduzia a dois:
    //
    //   observed    a captura ocorreu ao menos uma vez e o valor veio dela;
    //   degraded    a captura FALHOU em algum momento, então o valor é o maior
    //               CONHECIDO e pode subestimar o máximo absoluto;
    //   unobserved  a captura nunca se aplicou — não há valor e não houve falha.
    //
    // `unobserved` não precisa de campo novo: é exatamente a ausência das duas
    // evidências. Valor presente ⟺ alguma captura teve sucesso, porque
    // operationTouchAccountPhase só grava quando o probe devolve índice.
    //
    // Sem o terceiro estado, uma operação cuja fase JAMAIS foi capturada era
    // persistida como 'observed' — o registro imutável afirmava uma observação
    // que nunca houve, que é a coerção que este projeto recusa em toda parte.
    maxAccountPhaseIntegrity: op.phaseCaptureFault
      ? 'degraded'
      : (operationPhaseIdxOrNull(op.maxAccountPhaseReached) === null ? 'unobserved' : 'observed'),
    phaseCaptureFault: op.phaseCaptureFault ? structuredClone(op.phaseCaptureFault) : null,

    maxGridPhaseReached: operationResolveGridPhaseMax(op),

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

// Pergunta ao DISCO se ESTE registro chegou lá. É a única fonte capaz de decidir
// o desfecho quando save() lança: a pilha não diz se a exceção veio antes ou
// depois do setItem, e adivinhar erraria metade das vezes.
//
// Compara operationId E finalizedAt, não só o id. Um registro anterior com o
// mesmo operationId — de outra aba que finalizou primeiro, ou de um documento
// que já continha aquela operação — passaria por um teste só de id e faria a
// função afirmar que gravamos o que não gravamos. finalizedAt é gerado na
// construção deste snapshot e distingue o nosso registro de qualquer outro.
//
// Qualquer dúvida devolve false: storage indisponível, JSON inválido, documento
// vazio ou envelope de forma inesperada. Falso negativo faz reverter, que é o
// desfecho compatível com a mensagem dada ao operador ("nada foi alterado"); e
// o estado converge no próximo carregamento, porque o disco é a fonte da
// verdade e um documento que contenha o registro trará activeOperation nula.
// DESFECHO DA GRAVAÇÃO, em três estados — porque três são os desfechos reais e
// a versão anterior devolvia booleano:
//
//   CONFIRMED      há evidência POSITIVA no disco de que ESTA tentativa gravou;
//   NOT_PERSISTED  há evidência positiva de que ela NÃO gravou;
//   UNKNOWN        não foi possível provar nem uma coisa nem outra.
//
// O booleano anterior colapsava UNKNOWN em NOT_PERSISTED — inclusive num
// `catch(_){ return false; }` que transformava leitura impossível em prova de
// ausência. Daí saía o pior cenário que este sistema pode produzir: setItem
// grava a finalização, uma exceção posterior interrompe o fluxo, a leitura de
// volta falha, o sistema conclui "não gravou", desfaz a memória para a operação
// ativa e o próximo save() sobrescreve o disco — a finalização persistida
// desaparece sem que ninguém saiba que existiu.
//
// A confirmação exige operationId E finalizedAt. Só o operationId não basta:
// uma tentativa ANTERIOR da mesma operação pode ter gravado, e confirmar por
// identidade daria como persistida uma tentativa que não foi esta.
function operationProbePersisted(record){
  if (!record || typeof record !== 'object' ||
      typeof record.operationId !== 'string' || typeof record.finalizedAt !== 'string') {
    // Sem pergunta bem formada não há resposta provada. Nunca NOT_PERSISTED.
    return 'UNKNOWN';
  }
  let raw;
  try{
    const chave = (typeof LSKEY === 'string' && LSKEY) ? LSKEY : 'jpwealth_v9_state';
    raw = localStorage.getItem(chave);
  }catch(_){
    return 'UNKNOWN';   // armazenamento inacessível: nada se prova
  }
  // Documento ausente é prova de ausência do registro: ele não pode estar num
  // documento que não existe.
  if (raw === null || raw === undefined || raw === '') return 'NOT_PERSISTED';
  if (typeof raw !== 'string') return 'UNKNOWN';
  let doc;
  try{ doc = JSON.parse(raw); }
  catch(_){ return 'UNKNOWN'; }   // ilegível depois de uma escrita possível
  if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return 'UNKNOWN';
  const env = doc.operationHistory;
  // Documento legível SEM o envelope: é um documento anterior a esta feature, ou
  // anterior à gravação. O registro comprovadamente não está lá — o candidato
  // sempre carrega operationHistory, então o que foi lido não é o que teríamos
  // acabado de gravar.
  if (!env || typeof env !== 'object' || !Array.isArray(env.records)) return 'NOT_PERSISTED';
  let achou;
  try{
    achou = env.records.some(r =>
      r && typeof r === 'object' &&
      r.operationId === record.operationId &&
      r.finalizedAt === record.finalizedAt);
  }catch(_){ return 'UNKNOWN'; }
  return achou ? 'CONFIRMED' : 'NOT_PERSISTED';
}

// Compatibilidade: verdadeiro SOMENTE com confirmação positiva. UNKNOWN nunca
// vira "sim", e também nunca vira "não" para quem consulta o desfecho completo.
function operationPersistedHas(record){
  return operationProbePersisted(record) === 'CONFIRMED';
}

// ---- TRANSAÇÃO ----
// ou toda a finalização acontece, ou nada acontece.
function finalizeOperation(entrada){
  if (operationFinalizeInFlight) return { ok:false, motivo:'in_flight' };
  operationFinalizeInFlight = true;
  try{
    const pre = operationCanFinalize();
    if (!pre.ok) return pre;

    // A identidade NÃO é fabricada aqui. Ela pertence ao ciclo de vida
    // (operationOnOrderStatus, no ato em que a operação passa a existir) e à
    // migração (adoção de legado em operationNormalizeState). Uma operação viva
    // que chega aqui sem entidade é violação de estado, não caso a remediar:
    // criar o id neste ponto mutaria o estado de ENTRADA de uma transação que
    // ainda pode falhar, e a tentativa seguinte geraria outro id — a Operação
    // Única trocaria de identidade conforme o número de tentativas.
    const op = S.activeOperation;
    if (!op || typeof op !== 'object') {
      return { ok:false, motivo:'no_identity',
        mensagem:'A operação não tem identidade registrada. Recarregue a página para que a normalização a estabeleça antes de finalizar.' };
    }

    // IDEMPOTÊNCIA: mesmo operationId já no histórico ⇒ nada acontece de novo.
    // Sem isto, um segundo disparo criaria segundo registro, somaria
    // cycleRealizado outra vez e faria segundo reset.
    const jaFinalizada = ((S.operationHistory || {}).records || []).some(r => r && r.operationId === op.operationId);
    if (jaFinalizada) return { ok:false, motivo:'already_finalized', operationId: op.operationId };

    // AQUI NAO SE CAPTURA. A observacao da Fase da Conta acontece no checkpoint
    // explicito de openFinalizeOperationModal, ANTES de a revisao ser montada.
    // Capturar neste ponto fazia a confirmacao alterar em silencio campos que o
    // operador acabara de revisar — maxAccountPhaseReached,
    // maxAccountPhaseIntegrity e phaseCaptureFault —, reabrindo a invariante
    // "revisao = snapshot" fixada em ba3be3a.
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
      // Vinculo explicito tambem aqui: o evento de encerramento pertence a esta
      // operacao e nao pode ser confundido com o de outra na auditoria.
      operationId: snap.record.operationId,
      resumo: { operationId: snap.record.operationId, resultado: snap.record.netResult,
                cicloAcumulado: candidato.cycleRealizado }
    });
    // Trilha de auditoria DENTRO do candidato, e não depois do save(). O
    // recordId e o operationId real — nao existe segunda identidade so para
    // auditoria. O log legado gravava recordId VAZIO e o evento ficava sem
    // ancora; agora ele aponta para a operacao que encerrou.
    if (typeof dgLogChange === 'function') {
      dgLogChange('operation', 'finalized', snap.record.operationId,
        'Operação Única finalizada e preservada no Histórico', candidato);
    }
    candidato.phases.forEach((ph, pi) => { ph.orders = emptyOrders(OPERATION_GRID_SIZES[pi] || 3); });
    candidato.phaseUnlocked = [true, false, false, false];
    candidato.activeOperation = null;

    const val = operationValidateCandidate(candidato, anterior, snap.record);
    if (!val.ok) return val;

    // Troca e persistência. save() serializa a global, então o candidato precisa
    // ser o S no instante da gravação.
    //
    // save() DEVOLVE false nas duas falhas previstas (serialização e
    // armazenamento), mas também PODE LANÇAR: o tratamento de erro dele chama
    // renderPersistenceFailureWarning(), que toca DOM, e o caminho de sucesso
    // chama clearPersistenceFailureState(). Sem o try, uma exceção escaparia
    // depois de S já ser o candidato — grades zeradas em memória, nada gravado.
    //
    // O rollback não pode ser cego: se a exceção vier DEPOIS de a gravação ter
    // ocorrido, reverter faria a memória divergir do disco no sentido oposto, e
    // o próximo save() apagaria a finalização já persistida. Por isso o desfecho
    // é decidido pelo DISCO, não pela pilha: lê-se de volta o documento e
    // pergunta-se se o registro está lá.
    S = candidato;
    let desfecho;
    try {
      // save() === false é PROVA de não-escrita: os portões retornam antes de
      // tocar no armazenamento, o erro de serialização retorna antes do setItem,
      // e setItem é atômico — se lançou, nada foi gravado. A ambiguidade vive
      // exclusivamente no caminho de EXCEÇÃO, que pode vir de antes da escrita
      // (setPersistenceFailureState) ou de depois dela (clearPersistenceFailureState,
      // repintura, timer).
      desfecho = (save() === true) ? 'CONFIRMED' : 'NOT_PERSISTED';
    } catch (e) {
      desfecho = operationProbePersisted(snap.record);
      const detalhe = String((e && e.message) || e);

      if (desfecho === 'UNKNOWN') {
        // TERCEIRO DESFECHO. Não se reverte às cegas e não se declara nada.
        //
        // A memória FICA no candidato — que é o que o disco pode conter —, e
        // toda gravação futura é vetada por uma barreira própria. Reverter aqui
        // seria apostar que a escrita não ocorreu; se tiver ocorrido, o próximo
        // save() apagaria uma finalização já persistida, e memória e disco
        // passariam a discordar sobre se uma operação financeira foi encerrada.
        //
        // Congelar preserva as duas possibilidades e transfere o desempate para
        // quem pode inspecionar o disco: uma pessoa.
        markJPWealthPersistenceOutcomeUnknown(
          'finalização de ' + snap.record.operationId + ': ' + detalhe);
        return { ok:false, motivo:'persist_outcome_unknown', bloqueado:true,
          operationId: snap.record.operationId, erro: detalhe,
          mensagem: OPERATION_MSG_DESFECHO_INDETERMINADO };
      }

      if (desfecho === 'NOT_PERSISTED') {
        S = anterior;
        return { ok:false, motivo:'persist_exception', erro: detalhe,
          mensagem:'A finalização foi cancelada: a gravação falhou. Nada foi alterado.' };
      }

      // CONFIRMED: gravou e só então lançou (repintura de aviso, timer). O estado
      // vivo já corresponde ao disco; reverter é que criaria a divergência. A
      // exceção é falha de efeito colateral, e não da finalização.
      if (typeof console !== 'undefined' && console.error) {
        console.error('[operação] finalização persistida, mas o pós-processamento de save() lançou:', e);
      }
    }
    if (desfecho !== 'CONFIRMED') {
      S = anterior;
      return { ok:false, motivo:'persist_failed',
        mensagem:'A finalização foi cancelada: o estado não pôde ser gravado. Nada foi alterado.' };
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
  // typeof, e não coerção: `+null === 0` mostraria "Fase 1" na revisão para um
  // máximo que nunca foi observado, e o operador confirmaria uma afirmação
  // falsa sobre o passado.
  if(typeof idx!=='number' || !Number.isFinite(idx)) return '—';
  const f=(S.matrix||[])[+idx];
  return (f && f.nome) ? f.nome : ('Fase '+((+idx)+1));
}

function operationReviewRow(rotulo, valor){
  return '<div class="modal-q"><div class="ql">'+esc(rotulo)+'</div><div class="op-final-val">'+esc(valor)+'</div></div>';
}

// Leitura ÚNICA do campo de defesas. A revisão e a confirmação precisam
// interpretar o texto digitado exatamente do mesmo jeito; duas regras de parse
// seriam duas respostas possíveis para "quantas defesas serão gravadas".
// NaN significa AUSENTE — nunca 0. Zero defesas é afirmação do operador.
function operationParseDefenses(txt){
  const t=String(txt==null?'':txt).trim();
  return /^\d+$/.test(t) ? parseInt(t,10) : NaN;
}

// Bloco de leitura da revisão, montado a partir de um registro JÁ construído.
// Recebe o record que seria persistido AGORA com as entradas correntes, e não
// valores soltos: o que o operador lê é o snapshot, não uma paráfrase dele.
function operationReviewHTML(r, defesas){
  const retorno=(r.referenceBalance>0)?((r.netResult/r.referenceBalance)*100).toFixed(2)+'%':'—';
  const degradada=r.maxAccountPhaseIntegrity==='degraded';
  const naoObservada=r.maxAccountPhaseIntegrity==='unobserved';
  const abertura=r.openedAt
    ? (new Date(r.openedAt).toLocaleString('pt-BR')+(r.openedAtSource==='manual_legacy'?' (informada manualmente)':''))
    : 'Desconhecida';
  return operationReviewRow('Instrumento', r.instrument||'—')+
    operationReviewRow('Direção', r.direction||'—')+
    operationReviewRow('Abertura', abertura)+
    // closedAt é capturado no instante EFETIVO da confirmação. Exibir aqui um
    // horário de aparência definitiva e gravar outro quarenta segundos depois
    // seria a mesma divergência que este bloco existe para eliminar. O contrato
    // é dito em vez de simulado.
    operationReviewRow('Encerramento formal', 'Registrado no instante da confirmação')+
    operationReviewRow('Duração até agora', r.openedAt?operationFmtDuration(r.openedAt,r.closedAt):'—')+
    operationReviewRow('Ordens da operação', String(r.ordersSnapshot.length))+
    operationReviewRow('Resultado líquido', fmtMoney2(r.netResult))+
    // A base do retorno e CONGELADA no registro e deriva de um parametro manual
    // (saldo inicial do ciclo). Mostrar so a porcentagem escondia o denominador
    // que sera auditado anos depois — 250/10000 e 250/12500 sao aprovacoes
    // diferentes que produziam a mesma linha de leitura.
    operationReviewRow('Base do retorno', r.referenceBalance==null?'—':fmtMoney2(r.referenceBalance))+
    operationReviewRow('Retorno sobre a base do ciclo', retorno)+
    // AUSENTE e ZERO são estados distintos e ambos visíveis. "Não informado"
    // jamais é persistido: finalizeOperation recusa antes de chegar ao disco.
    operationReviewRow('Defesas informadas', Number.isFinite(defesas)?String(defesas):'Não informado')+
    operationReviewRow('Fase máxima da Conta', operationFmtPhase(r.maxAccountPhaseReached))+
    operationReviewRow('Fase máxima da Grade', r.maxGridPhaseReached==null?'—':operationFmtPhase(r.maxGridPhaseReached))+
    (degradada?('<div class="modal-q" data-qid="integridade"><div class="ql">Integridade da Fase máxima da Conta: <b>Degradada</b></div>'+
      '<div class="modal-sub">Houve falha de captura durante esta operação. O valor acima é o maior <b>conhecido</b>, não necessariamente o máximo absoluto atingido. A finalização não é bloqueada por isso.</div></div>')
    :naoObservada?('<div class="modal-q" data-qid="integridade"><div class="ql">Integridade da Fase máxima da Conta: <b>Não observada</b></div>'+
      '<div class="modal-sub">A captura nunca se aplicou durante esta operação, e nenhuma falha foi registrada. O registro guardará a ausência como ausência — não como Fase 1 nem como medição concluída. A finalização não é bloqueada por isso.</div></div>'):'');
}

// ---------------------------------------------------------------------------
// PREFLIGHT DA FINALIZAÇÃO
// ---------------------------------------------------------------------------
// Orquestra; NÃO consolida. Decide entre bloquear, complementar ou seguir para a
// revisão canônica. A consolidação continua sendo exclusividade de
// finalizeOperation, e nada aqui a chama direto.
//
// Só ordens FECHADAS precisam de resultado: netOpAtual() soma exclusivamente
// `status==='Fechada'`. Exigir resultado de uma ordem 'Migrada' bloquearia a
// finalização por um dado que aquela linha nunca teve motivo para ter.
function operationOrderLabel(pi, oi, o){
  const slot = (pi===0 && oi===0) ? 'GÊNESE' : (pi===0 ? 'DEF '+oi : 'DEF '+(pi+1)+'.'+(oi+1));
  const partes = [slot];
  if (o && o.par) partes.push(String(o.par));
  if (o && o.id) partes.push('ID '+String(o.id));
  return partes.join(' · ');
}

function operationPreflight(){
  const vivas = operationLiveOrders();
  if (!vivas.length) {
    return { estado:'no_operation',
      mensagem:'Não há operação registrada nas grades para finalizar.' };
  }
  const abertas = vivas.filter(x => x.o.status === 'Aberta');
  if (abertas.length) return { estado:'blocked', abertas };
  const incompletas = vivas.filter(x =>
    x.o.status === 'Fechada' &&
    (typeof orderResultMissing === 'function' ? orderResultMissing(x.o) : !Number.isFinite(x.o.result)));
  if (incompletas.length) return { estado:'incomplete', incompletas };
  return { estado:'ready', ordens: vivas.length };
}

// Superfície de BLOQUEIO. Nomeia as ordens que impedem o encerramento e não muta
// nada — nem status, nem resultado, nem identidade. Antes o botão simplesmente
// sumia; agora ele existe e explica.
function openFinalizeBlockedModal(abertas){
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  const lista = abertas.map(x =>
    '<li>'+esc(operationOrderLabel(x.pi, x.oi, x.o))+'</li>').join('');
  const umaSo = abertas.length === 1;
  const genese = abertas.some(x => x.pi===0 && x.oi===0);
  box.innerHTML =
    '<h3>Finalizar Operação</h3>'+
    '<div class="modal-err show">🚫 Não é possível finalizar esta operação.</div>'+
    '<div class="modal-sub">'+
      (genese
        ? 'A Ordem Gênese permanece aberta. Feche a posição antes de realizar o encerramento formal.'
        : (umaSo
            ? 'Existe uma ordem aberta vinculada à operação. Feche todas as posições antes da consolidação.'
            : 'Existem ordens abertas vinculadas à operação. Feche todas as posições antes da consolidação.'))+
    '</div>'+
    '<div class="modal-q"><div class="ql">'+(umaSo?'Ordem aberta':'Ordens abertas')+':</div>'+
      '<ul style="margin:6px 0 0 18px">'+lista+'</ul></div>'+
    '<div class="modal-sub">Fechar uma ordem encerra uma posição. Finalizar a Operação Única consolida o resultado e a registra no Histórico — Art. 4.4.</div>'+
    '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Fechar</button></div>';
  $('modalCancel').addEventListener('click', closeModal);
  $('modalCancel').focus();
}

// Superfície de COMPLEMENTAÇÃO. Uma só, com todas as ordens incompletas
// identificadas. Os campos são RASCUNHO: nada toca S enquanto o operador não
// confirmar, e cancelar não deixa metade dos valores aplicados.
function openFinalizeCompletionModal(incompletas){
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  const linhas = incompletas.map((x, i) =>
    '<div class="modal-q" data-qid="ord'+i+'">'+
      '<div class="ql">'+esc(operationOrderLabel(x.pi, x.oi, x.o))+'</div>'+
      '<input type="text" inputmode="decimal" data-compl="'+i+'" autocomplete="off" placeholder="informe">'+
      '<div class="modal-err">Informe um número. Ponto ou vírgula decimal; sem separador de milhar. Em branco não é zero — se fechou no zero a zero, digite <b>0</b>.</div>'+
    '</div>').join('');
  box.innerHTML =
    '<h3>Finalizar Operação — completar resultados</h3>'+
    '<div class="modal-sub">'+
      (incompletas.length===1
        ? 'Uma ordem fechada está sem resultado informado. '
        : incompletas.length+' ordens fechadas estão sem resultado informado. ')+
      'O resultado entra no consolidado da Operação Única e no registro do Histórico, então precisa ser informado antes do encerramento.</div>'+
    linhas+
    '<div class="modal-actions">'+
      '<button class="modal-btn cancel" id="modalCancel">Cancelar</button>'+
      '<button class="modal-btn confirm" id="modalConfirm">Confirmar resultados</button>'+
    '</div>';
  $('modalCancel').addEventListener('click', closeModal);
  $('modalConfirm').addEventListener('click', () => {
    // RASCUNHO: lê tudo, valida tudo, e só então aplica. Validar-e-aplicar em
    // laço deixaria as primeiras ordens gravadas e as últimas não, se alguma
    // falhasse no meio — e cancelar depois disso não teria o que desfazer.
    const rascunho = [];
    let algumInvalido = false;
    incompletas.forEach((x, i) => {
      const campo = box.querySelector('[data-compl="'+i+'"]');
      const erro  = box.querySelector('[data-qid="ord'+i+'"] .modal-err');
      const v = (typeof orderParseResult === 'function')
        ? orderParseResult(campo ? campo.value : '')
        : NaN;
      if (!Number.isFinite(v)) { if (erro) erro.classList.add('show'); algumInvalido = true; }
      else { if (erro) erro.classList.remove('show'); rascunho.push({ x, v }); }
    });
    if (algumInvalido) return;   // NADA foi aplicado

    rascunho.forEach(({ x, v }) => { x.o.result = v; });
    save();
    closeModal();
    if (typeof render === 'function') render();
    if (typeof renderPhases === 'function') renderPhases();
    // REVALIDA antes de seguir: o estado mudou, e o preflight decide de novo.
    startFinalizeOperation();
  });
  const primeiro = box.querySelector('[data-compl="0"]');
  if (primeiro) primeiro.focus();
}

// PONTO DE ENTRADA do botão. Nunca chama finalizeOperation direto.
function startFinalizeOperation(){
  const pre = operationPreflight();
  if (pre.estado === 'blocked')    return openFinalizeBlockedModal(pre.abertas);
  if (pre.estado === 'incomplete') return openFinalizeCompletionModal(pre.incompletas);
  if (pre.estado === 'no_operation'){
    const box=$('modalBox');
    $('modalOverlay').classList.add('show');
    box.innerHTML='<h3>Finalizar Operação</h3>'+
      '<div class="modal-sub">'+esc(pre.mensagem)+'</div>'+
      '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Fechar</button></div>';
    $('modalCancel').addEventListener('click', closeModal);
    $('modalCancel').focus();
    return;
  }
  return openFinalizeOperationModal();
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
  // Entidade AUSENTE nao vira entidade de fachada. O placeholder anterior
  // ('(sera gerado na confirmacao)') era string nao-vazia, entao atravessava a
  // guarda de operationResolveGridPhaseMax — que existe para devolver null
  // quando NAO ha identidade — e a revisao passava a afirmar uma Fase maxima da
  // Grade sobre uma entidade que nao existe. Pior: montava a revisao inteira,
  // com botao de finalizar, para um estado que finalizeOperation recusa por
  // no_identity. O operador preencheria abertura e defesas para so entao
  // descobrir que nada seria gravado.
  //
  // Registro do que NAO se afirma aqui: numa grade sem evento de destravamento
  // carimbado, uma identidade legitima tambem produz 0 — esse zero e o contrato
  // documentado da funcao, nao efeito do placeholder. O defeito e afirmar
  // qualquer coisa sobre uma entidade inexistente e prometer um registro que
  // jamais sera gravado.
  const op=S.activeOperation;
  if(!op || typeof op!=='object'){
    box.innerHTML='<h3>Finalizar Operação Única</h3>'+
      '<div class="modal-sub">A operação não tem identidade registrada. Recarregue a página para que a normalização a estabeleça antes de finalizar.</div>'+
      '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Fechar</button></div>';
    $('modalCancel').addEventListener('click',closeModal);
    $('modalCancel').focus();
    return;
  }
  // CHECKPOINT EXPLICITO. Pedir a finalizacao e um ato do operador, e e AQUI que
  // a Fase da Conta e observada — uma vez so, antes de qualquer record existir.
  // Dai em diante a revisao e a confirmacao leem o mesmo valor, e a confirmacao
  // nao tem como alterar em silencio o que acabou de ser revisado.
  //
  // Cancelar nao desfaz esta observacao, e isso e correto: a fase daquele
  // instante existiu de verdade. O que nao pode existir e revisao e registro
  // divergindo.
  if(typeof operationTouchAccountPhase==='function') operationTouchAccountPhase();

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
  // Legado é propriedade da ENTIDADE, não do registro repintado: assim que o
  // operador digita a data, o record passa a ter openedAt, e recalcular a
  // partir dele faria o próprio campo de entrada desaparecer sob os dedos.
  const legada=!(typeof op.openedAt==='string' && op.openedAt);

  box.innerHTML=
    '<h3>Finalizar Operação Única</h3>'+
    '<div class="modal-sub">Encerra formalmente a tese, preserva a operação no Histórico, consolida o resultado no ciclo e libera as grades. '+
    'Diferente de <b>fechar uma ordem</b>, que encerra apenas uma posição individual.</div>'+
    '<div id="finalReview"></div>'+
    (legada?('<div class="modal-q" data-qid="abertura"><div class="ql">Data/hora de abertura da operação — obrigatória, pois não foi registrada automaticamente:</div>'+
      '<input type="datetime-local" id="finalOpenedAt"><div class="modal-err">'+esc(OPERATION_MSG_ABERTURA_AUSENTE)+'</div></div>'):'')+
    '<div class="modal-q" data-qid="defesas"><div class="ql">Número de defesas realizadas (inteiro ≥ 0):</div>'+
    '<input type="text" inputmode="numeric" id="finalDefenses" autocomplete="off" placeholder="informe">'+
    '<div class="modal-sub">O modelo de ordens não classifica defesa; a contagem é informada e fica registrada como tal.</div>'+
    '<div class="modal-err">Informe um inteiro maior ou igual a zero.</div></div>'+
    '<div class="modal-q" data-qid="confirmtxt"><div class="ql">Digite <b>FECHADO</b> para confirmar:</div>'+
    '<input type="text" id="finalConfirm" autocomplete="off"><div class="modal-err">Precisa digitar exatamente "FECHADO".</div></div>'+
    '<div class="modal-q" data-qid="falha" hidden><div class="modal-err show" id="finalFail"></div></div>'+
    '<div class="modal-actions"><button class="modal-btn cancel" id="modalCancel">Cancelar</button>'+
    '<button class="modal-btn confirm" id="modalConfirm">Finalizar Operação</button></div>';

  const inAbertura=legada?box.querySelector('#finalOpenedAt'):null;
  const inDefesas=box.querySelector('#finalDefenses');
  const revisao=box.querySelector('#finalReview');

  const erro=(qid,on)=>{ const n=box.querySelector('[data-qid="'+qid+'"] .modal-err'); if(n) n.classList.toggle('show',!!on); };
  // O campo de abertura tem DOIS motivos de recusa — ausente e cronologicamente
  // impossivel — e dizer "informe a data" para quem ja informou seria mentir
  // sobre o que esta errado.
  const msgAbertura=txt=>{ const n=box.querySelector('[data-qid="abertura"] .modal-err'); if(n) n.textContent=txt; };

  // ENTRADA CORRENTE: exatamente o objeto que finalizeOperation receberá. A
  // revisão e a confirmação leem a mesma fonte, então não existe o caso de o
  // operador aprovar um registro e outro ser gravado.
  const entradaCorrente=()=>({
    defenseCount: operationParseDefenses(inDefesas.value),
    openedAtManual: legada?String(inAbertura.value||'').trim():''
  });

  // REPINTURA da revisão a cada alteração de entrada manual. Só o bloco de
  // leitura é reescrito: recriar os <input> destruiria o foco e o texto já
  // digitado a cada tecla.
  function repintarRevisao(){
    const ent=entradaCorrente();
    // defenseCount ausente faria buildSnapshot recusar, e as demais linhas
    // ficariam sem revisão nenhuma. Nenhum outro campo do registro deriva de
    // defenseCount, então a construção usa 0 só para destravar o restante — o
    // valor MOSTRADO é o real, e "não informado" nunca chega ao disco.
    const p=operationBuildSnapshot(op,{
      defenseCount: Number.isFinite(ent.defenseCount)?ent.defenseCount:0,
      openedAtManual: ent.openedAtManual
    });
    // '—' significa dado INDISPONIVEL. Cronologia impossivel e dado
    // CONTRADITORIO — estados epistemicamente distintos, que nao podem ter a
    // mesma apresentacao. A revisao diz qual e o problema.
    const cronoInvalida = !p.ok && p.motivo==='chronology_invalid';
    revisao.innerHTML=p.ok
      ? operationReviewHTML(p.record, ent.defenseCount)
      : (cronoInvalida
          ? '<div class="modal-err show">'+esc(p.mensagem)+'</div>'
          : '<div class="modal-err show">Não foi possível montar a revisão ('+esc(p.motivo)+').</div>');
    if(cronoInvalida){ msgAbertura(OPERATION_MSG_CRONOLOGIA); erro('abertura',true); }
    // A validacao acompanha a revisao. Ligar so a leitura ao evento fazia o
    // modal afirmar duas coisas ao mesmo tempo: a linha "Abertura" ja exibindo
    // a data informada e, tres centimetros abaixo, a mensagem vermelha dizendo
    // que o campo esta ausente. O erro so e APAGADO quando a entrada passa a
    // ser valida; nunca aceso aqui, porque acusar antes da confirmacao seria
    // reclamar de um campo que o operador ainda esta preenchendo.
    if(Number.isFinite(ent.defenseCount)) erro('defesas',false);
    if(legada && ent.openedAtManual && Number.isFinite(Date.parse(ent.openedAtManual)) && !cronoInvalida){
      msgAbertura(OPERATION_MSG_ABERTURA_AUSENTE); erro('abertura',false);
    }
  }
  repintarRevisao();
  // 'change' alem de 'input': o seletor nativo de data e o preenchimento
  // automatico nem sempre emitem os dois, e uma revisao defasada de um campo
  // ja alterado e precisamente o defeito que este bloco elimina.
  ['input','change'].forEach(ev=>{
    if(inAbertura) inAbertura.addEventListener(ev,repintarRevisao);
    inDefesas.addEventListener(ev,repintarRevisao);
  });

  $('modalCancel').addEventListener('click',closeModal);
  const btn=$('modalConfirm');
  btn.addEventListener('click',()=>{
    if(btn.disabled) return; // reentrância: o segundo clique não passa
    erro('defesas',false); erro('confirmtxt',false); if(legada) erro('abertura',false);
    let falhou=false;
    // Campo VAZIO não vira 0 em silêncio: zero defesas é uma afirmação do
    // operador, e precisa ser digitada. Mesmo parse da revisão.
    const ent=entradaCorrente();
    if(!Number.isFinite(ent.defenseCount)){ erro('defesas',true); falhou=true; }
    if(legada && (!ent.openedAtManual || !Number.isFinite(Date.parse(ent.openedAtManual)))){
      msgAbertura(OPERATION_MSG_ABERTURA_AUSENTE); erro('abertura',true); falhou=true;
    }
    // A interface PERGUNTA ao domínio em vez de reimplementar a comparação: a
    // mesma função que constrói o registro decide se ele é possível, então as
    // duas pontas não podem divergir. A proteção real vive em
    // operationBuildSnapshot e vale mesmo para quem chame finalizeOperation
    // direto, sem passar por esta tela.
    if(!falhou){
      const prova=operationBuildSnapshot(op,{
        defenseCount: Number.isFinite(ent.defenseCount)?ent.defenseCount:0,
        openedAtManual: ent.openedAtManual
      });
      if(!prova.ok && prova.motivo==='chronology_invalid'){
        msgAbertura(prova.mensagem); erro('abertura',true); falhou=true;
      }
    }
    if(String(box.querySelector('#finalConfirm').value||'').trim()!=='FECHADO'){ erro('confirmtxt',true); falhou=true; }
    if(falhou) return;

    btn.disabled=true;
    const res=finalizeOperation(ent);
    if(!res.ok){
      // Falha NÃO fecha o modal comunicando sucesso. A operação continua viva
      // e o operador pode tentar de novo.
      const cx=box.querySelector('[data-qid="falha"]');
      const msg=box.querySelector('#finalFail');
      if(cx&&msg){ msg.textContent=res.mensagem||('A finalização não foi concluída ('+res.motivo+'). Nada foi alterado.'); cx.hidden=false; }
      if(res.motivo==='persist_outcome_unknown'){
        // O botão NÃO volta a ficar disponível. Nada aqui pode ser tentado de
        // novo: uma segunda tentativa gravaria, e gravar é justamente o que
        // destruiria o estado que a barreira existe para preservar. Também não
        // se repinta a revisão — ela descreveria uma transação cujo desfecho
        // ninguém conhece.
        return;
      }
      btn.disabled=false;
      // O modal continua aberto para nova tentativa, e ela pode acontecer muito
      // depois. Sem repintar, a revisao reaprovada ficaria carimbada na ultima
      // tecla digitada enquanto o registro receberia o closedAt da reconfirmacao.
      repintarRevisao();
      return;
    }
    closeModal();
    if(typeof render==='function') render();
    if(typeof renderPhases==='function') renderPhases();
    if(typeof renderLedger==='function') renderLedger();
  });
  const foco=legada?inAbertura:inDefesas;
  if(foco) foco.focus();
}

// Superfície pública consumida pela interface (Painel Operacional) e pelos
// testes. O domínio não conhece DOM; a revisão é a única parte que o conhece.
window.JPWOperation = {
  canFinalize: operationCanFinalize,
  buildSnapshot: operationBuildSnapshot,
  finalize: finalizeOperation,
  liveOrders: operationLiveOrders,
  openReview: openFinalizeOperationModal,
  // Ponto de entrada do botao: preflight -> bloqueio | complementacao | revisao.
  start: startFinalizeOperation,
  preflight: operationPreflight
};
