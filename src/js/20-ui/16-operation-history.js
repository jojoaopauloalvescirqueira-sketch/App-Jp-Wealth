// ============ HISTÓRICO DE OPERAÇÕES ÚNICAS (Camada 3 — N1, leitura) ============
// Workspace do Execution Board. Consumidor ESTRITAMENTE somente leitura de
// S.operationHistory.records: nada aqui recalcula um fato histórico a partir das
// grades vivas. Resultado, timestamps, fases, defesas, ordens e referenceBalance
// vêm do snapshot que a Camada 2 preservou.
//
// A razão é a que sustenta o projeto inteiro: o estado atual da conta não pode
// reescrever o passado. Se o saldo mudar hoje, o retorno de uma operação
// encerrada em maio continua o mesmo, porque o denominador está congelado no
// registro.
//
// Selecionar, filtrar, ordenar, buscar e abrir detalhe são estado de
// APRESENTAÇÃO — vivem em variáveis de módulo e nunca entram em S, storage,
// backup, schema ou migração.

// var, e não const/let: mesmo motivo documentado em 17-economic-calendar.js —
// no monólito este arquivo pode ser alcançado por chamada de outro script antes
// de avaliar, e o nome precisa existir como undefined em vez de estourar na TDZ.
var histState = { instrument:'all', direction:'all', result:'all', query:'', selected:null };

function histRecords(){
  const h = S.operationHistory;
  return (h && Array.isArray(h.records)) ? h.records : [];
}

// ---- derivações puras sobre o snapshot (nunca sobre as grades) ----
function histNumber(value){
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;
  if (typeof value !== 'string' || !/^-?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(value.trim())) return null;
  const n = Number(value.trim());
  return Number.isFinite(n) ? n : null;
}
function histCapturedContext(r){
  // Only captured records participate. Conflicts stay unresolved; UI selection
  // and today's account facts can never provide a historical monetary unit.
  const contexts = [r, r && r.recordContext, r && r.finalizationContext].filter(x => x && typeof x === 'object');
  const values = key => [...new Set(contexts.flatMap(x =>
    [x[key], key === 'currency' && x.accountInputs && x.accountInputs.currency])
    .filter(x => typeof x === 'string' && x.trim()).map(x => x.trim()))];
  const currencies = values('currency'), accounts = values('accountId'), periods = values('periodId');
  // An explicit null records known absence (notably a LEGACY consolidation).
  // A later observation in either context must not fill that historical gap.
  const unitAbsent = r && Object.prototype.hasOwnProperty.call(r, 'currency') && r.currency === null;
  return {currency: !unitAbsent && currencies.length === 1 && /^[A-Z]{3}$/.test(currencies[0]) ? currencies[0] : null,
    accountId: accounts.length === 1 ? accounts[0] : null,
    periodId: periods.length === 1 ? periods[0] : null,
    currencyConflict: currencies.length > 1, identityConflict: accounts.length > 1 || periods.length > 1};
}
function histMoney(value, context){
  const n = histNumber(value);
  if (n == null) return '—';
  if (!context || !context.currency)
    return n.toLocaleString('pt-BR', {minimumFractionDigits:2,maximumFractionDigits:2}) + ' · unidade ausente';
  return fmtForexMoney(n, context);
}
function histPolicyLabel(r){
  const snapshot = r && (r.policySnapshot || (r.recordContext && r.recordContext.policySnapshot));
  const version = snapshot && (snapshot.policyVersion || snapshot.version);
  return snapshot && (snapshot.statuteVersion === 'V11' || /^JPW-FOREX-V11-/.test(version || '')) ? 'V11' : 'LEGACY';
}
function histDurationMs(r){
  const a = Date.parse(r && r.openedAt), b = Date.parse(r && r.closedAt);
  return (Number.isFinite(a) && Number.isFinite(b) && b >= a) ? (b - a) : null;
}
function histFmtDuration(ms){
  if (ms == null) return '—';
  const min = Math.floor(ms / 60000);
  const d = Math.floor(min / 1440), h = Math.floor((min % 1440) / 60), m = min % 60;
  if (d) return d + 'd ' + h + 'h';
  if (h) return h + 'h ' + String(m).padStart(2, '0') + 'min';
  return m + 'min';
}
function histReturnPct(r){
  const base = histNumber(r.referenceBalance), result = histNumber(r.netResult);
  if (base == null || base <= 0 || result == null) return null;
  return result / base * 100;
}
function histResultClass(r){
  const n = histNumber(r.netResult);
  if (n == null) return 'Não informado';
  return n > 0 ? 'Positiva' : (n < 0 ? 'Negativa' : 'Neutra');
}
function histFmtDate(iso){
  const t = Date.parse(iso);
  return Number.isFinite(t) ? new Date(t).toLocaleDateString('pt-BR') : '—';
}
function histPhaseName(idx, record){
  // typeof, e nao coercao: `+null === 0` renderizaria 'Fase 1' para um maximo
  // que nunca foi observado — o registro diz null e a tela mentiria.
  if (!Number.isInteger(idx) || idx < 0) return '—';
  return histPolicyLabel(record) + ' · Fase ' + (idx + 1);
}

// Mediana com n EXPLÍCITO. Desconhecido é excluído desta métrica e de mais
// nenhuma — a operação continua contando no total. Fundir as duas coisas
// transformaria ausência de dado em observação.
function histMedian(valores){
  const v = valores.filter(x => x != null && Number.isFinite(x)).sort((a, b) => a - b);
  if (!v.length) return { valor:null, n:0 };
  const meio = Math.floor(v.length / 2);
  const valor = v.length % 2 ? v[meio] : (v[meio - 1] + v[meio]) / 2;
  return { valor, n: v.length };
}

function histFilter(records){
  const q = String(histState.query || '').trim().toUpperCase();
  return records.filter(r => {
    if (histState.instrument !== 'all' && String(r.instrument || '') !== histState.instrument) return false;
    if (histState.direction !== 'all' && String(r.direction || '') !== histState.direction) return false;
    if (histState.result !== 'all' && histResultClass(r) !== histState.result) return false;
    if (q) {
      const alvo = [r.operationId, r.instrument, ...(r.ordersSnapshot || []).map(o => o.label)]
        .map(x => String(x || '').toUpperCase()).join(' ');
      if (!alvo.includes(q)) return false;
    }
    return true;
  }).sort((a, b) => (Date.parse(b.closedAt) || 0) - (Date.parse(a.closedAt) || 0));
}

// Estatística DESCRITIVA sobre o conjunto filtrado. Nenhum número aqui é
// previsão, expectativa ou score: são fatos observados, com o denominador dito.
function histStats(records){
  const n = records.length;
  if (!n) return { n:0 };
  const resultados = records.map(r => histNumber(r.netResult));
  const conhecidos = resultados.filter(x => x != null);
  const positivas = conhecidos.filter(x => x > 0).length;
  const contexts = records.map(histCapturedContext);
  const currencies = [...new Set(contexts.map(x => x.currency))];
  const comparable = conhecidos.length === n && currencies.length === 1 && currencies[0] != null;
  const monetaryReason = conhecidos.length !== n ? 'Há resultado não informado.'
    : contexts.some(x => !x.currency) ? 'Unidade ausente ou conflitante no registro.'
    : currencies.length !== 1 ? 'Moedas diferentes; sem conversão histórica registrada.' : '';
  const dur = histMedian(records.map(histDurationMs));
  const def = histMedian(records.map(r => histNumber(r.defenseCount)));
  return {
    n,
    acumulado: comparable ? conhecidos.reduce((s, x) => s + x, 0) : null,
    currency: comparable ? currencies[0] : null,
    monetaryReason,
    resultadosConhecidos: conhecidos.length,
    positivas,
    taxaPositivas: conhecidos.length ? positivas / conhecidos.length * 100 : null,
    duracaoMediana: dur,
    defesasMedianas: def,
    maior: comparable ? Math.max(...conhecidos) : null,
    menor: comparable ? Math.min(...conhecidos) : null
  };
}

// ---- render ----
function histCard(rotulo, valor, nota){
  return '<div class="hist-stat"><div class="hist-stat-l">' + esc(rotulo) + '</div>' +
    '<div class="hist-stat-v">' + esc(valor) + '</div>' +
    (nota ? '<div class="hist-stat-n">' + esc(nota) + '</div>' : '') + '</div>';
}

function histRenderDetail(r){
  const context = histCapturedContext(r);
  const ordens = (r.ordersSnapshot || []).map(o =>
    '<tr><td>' + esc(o.label || '(sem ID)') + '</td><td>' + esc(histPhaseName(Number.isInteger(o.phase) ? o.phase - 1 : null, r)) + '</td>' +
    '<td>' + esc(o.par || '—') + '</td><td>' + esc(o.tipo || '—') + '</td>' +
    '<td class="hist-num">' + esc(String(o.lote ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(String(o.entry ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(String(o.sl ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(String(o.tp ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(histMoney(o.result, context)) + '</td>' +
    '<td>' + esc(o.status || '—') + '</td>' +
    '<td>' + esc(o.openedAt ? histFmtDate(o.openedAt) : '—') + '</td>' +
    '<td>' + esc(o.closedAt ? histFmtDate(o.closedAt) : '—') + '</td></tr>').join('');
  const ret = histReturnPct(r);
  const degradada = r.maxAccountPhaseIntegrity === 'degraded';
  // Registros gravados ANTES do terceiro estado existir trazem 'observed' mesmo
  // quando nada foi capturado. Nao se reescreve historico: eles ficam como
  // estao, e a Fase maxima aparece como '—' de qualquer forma.
  const naoObservada = r.maxAccountPhaseIntegrity === 'unobserved';
  return '<div class="hist-detail" data-hist-detail="' + esc(r.operationId) + '">' +
    '<div class="hist-detail-grid">' +
    '<div><b>Operation ID</b><br><span class="hist-mono">' + esc(r.operationId) + '</span></div>' +
    '<div><b>Conta capturada</b><br>' + esc(context.accountId || 'Não capturada') + '</div>' +
    '<div><b>Período capturado</b><br>' + esc(context.periodId || 'Não capturado') + '</div>' +
    '<div><b>Moeda capturada</b><br>' + esc(context.currency || (context.currencyConflict ? 'Conflitante · unidade ausente' : 'Unidade ausente')) + '</div>' +
    '<div><b>Instrumento</b><br>' + esc(r.instrument || '—') + '</div>' +
    '<div><b>Direção</b><br>' + esc(r.direction || '—') + '</div>' +
    '<div><b>Abertura</b><br>' + esc(r.openedAt ? histFmtDate(r.openedAt) : 'Desconhecida') +
      (r.openedAtSource ? ' <span class="hist-src">(' + esc(r.openedAtSource) + ')</span>' : '') + '</div>' +
    '<div><b>Encerramento</b><br>' + esc(histFmtDate(r.closedAt)) + '</div>' +
    '<div><b>Duração</b><br>' + esc(histFmtDuration(histDurationMs(r))) + '</div>' +
    '<div><b>Fase máxima da Conta</b><br>' + esc(histPhaseName(r.maxAccountPhaseReached, r)) +
      (degradada ? ' <span class="hist-degradada" title="Houve falha de captura durante a operação: este é o maior valor conhecido, não necessariamente o máximo absoluto.">máximo conhecido / integridade degradada</span>'
       : naoObservada ? ' <span class="hist-degradada" title="A captura da Fase da Conta nunca se aplicou durante esta operação, e nenhuma falha foi registrada. Ausência de medição, não medição de ausência.">não observada</span>' : '') + '</div>' +
    '<div><b>Fase máxima da Grade</b><br>' + esc(histPhaseName(r.maxGridPhaseReached, r)) + '</div>' +
    '<div><b>Defesas</b><br>' + esc(String(r.defenseCount ?? '—')) +
      (r.defenseCountSource ? ' <span class="hist-src">(' + esc(r.defenseCountSource) + ')</span>' : '') + '</div>' +
    '<div><b>Resultado líquido</b><br>' + esc(histMoney(r.netResult, context)) + '</div>' +
    '<div><b>Base do retorno</b><br>' + esc(histMoney(r.referenceBalance, context)) +
      ' <span class="hist-src">(' + esc(r.referenceBalanceType || '—') + ')</span></div>' +
    '<div><b>Retorno</b><br>' + esc(ret == null ? '—' : ret.toFixed(2) + '%') + '</div>' +
    '</div>' +
    '<div class="jp-table-scroll"><table class="hist-orders"><thead><tr>' +
    '<th scope="col">ID</th><th scope="col">Fase</th><th scope="col">Instrumento</th>' +
    '<th scope="col">Direção</th><th scope="col">Lote</th><th scope="col">Entrada</th>' +
    '<th scope="col">SL</th><th scope="col">TP</th><th scope="col">Resultado</th>' +
    '<th scope="col">Status</th><th scope="col">Abertura</th><th scope="col">Fechamento</th>' +
    '</tr></thead><tbody>' + (ordens || '<tr><td colspan="12">Sem ordens registradas.</td></tr>') +
    '</tbody></table></div>' +
    '<p class="hist-ro">Registro histórico — somente leitura.</p>' +
    '<button type="button" class="reset-btn" data-operation-copy="' + esc(r.operationId) + '">Copiar operação</button>' +
    '<p class="expl" data-operation-copy-feedback role="status" aria-live="polite"></p></div>';
}

// Estatisticas e tabela sao a parte que RESPONDE a filtro, busca e selecao.
// Ficam separadas da montagem para poderem ser repintadas sem recriar os
// controles: reescrever o cartao inteiro a cada tecla destroi o <input> de
// busca e o foco vai junto — o operador digitava uma letra e tinha de clicar
// no campo de novo para digitar a segunda.
function histStatsHTML(filtrados){
  const st = histStats(filtrados);
  if (!st.n) return '<p class="expl">Nenhuma operação atende aos filtros.</p>';
  return histCard('Operações finalizadas', String(st.n)) +
    histCard('Resultado líquido acumulado', histMoney(st.acumulado, st), st.monetaryReason) +
    histCard('Taxa de operações positivas', st.taxaPositivas == null ? '—' : st.taxaPositivas.toFixed(0) + '%',
             st.positivas + ' de ' + st.resultadosConhecidos + ' com resultado informado; ' + st.n + ' registradas') +
    histCard('Duração mediana',
             st.duracaoMediana.valor == null ? '—' : histFmtDuration(st.duracaoMediana.valor),
             'n = ' + st.duracaoMediana.n) +
    histCard('Defesas medianas',
             st.defesasMedianas.valor == null ? '—' : String(st.defesasMedianas.valor),
             'n = ' + st.defesasMedianas.n) +
    histCard('Maior resultado', histMoney(st.maior, st), st.monetaryReason) +
    histCard('Menor resultado', histMoney(st.menor, st), st.monetaryReason);
}

function histTableHTML(filtrados){
  const linhas = filtrados.map(r => {
    const ret = histReturnPct(r);
    const cls = histResultClass(r);
    const aberto = histState.selected === r.operationId;
    return '<tr class="hist-row" data-hist-id="' + esc(r.operationId) + '" tabindex="0" ' +
      'role="button" aria-expanded="' + (aberto ? 'true' : 'false') + '">' +
      '<td class="hist-mono">' + esc(String(r.operationId).slice(0, 14)) + '</td>' +
      '<td>' + esc(r.instrument || '—') + '</td>' +
      '<td>' + esc(r.direction || '—') + '</td>' +
      '<td>' + esc(r.openedAt ? histFmtDate(r.openedAt) : '—') + '</td>' +
      '<td>' + esc(histFmtDate(r.closedAt)) + '</td>' +
      '<td>' + esc(histFmtDuration(histDurationMs(r))) + '</td>' +
      '<td class="hist-num">' + esc(String(r.defenseCount ?? '—')) + '</td>' +
      '<td class="hist-num hist-' + esc(cls.toLowerCase().replace(/\s+/g, '-')) + '">' + esc(histMoney(r.netResult, histCapturedContext(r))) + '</td>' +
      '<td class="hist-num">' + esc(ret == null ? '—' : ret.toFixed(2) + '%') + '</td>' +
      '</tr>' + (aberto ? '<tr class="hist-detail-row"><td colspan="9">' + histRenderDetail(r) + '</td></tr>' : '');
  }).join('');
  return '<table class="hist-table"><thead><tr>' +
    '<th scope="col">Operação</th><th scope="col">Instrumento</th><th scope="col">Direção</th>' +
    '<th scope="col">Abertura</th><th scope="col">Fechamento</th><th scope="col">Duração</th>' +
    '<th scope="col">Defesas</th><th scope="col">Resultado</th><th scope="col">Retorno</th>' +
    '</tr></thead><tbody>' + (linhas || '<tr><td colspan="9">Nenhuma operação atende aos filtros.</td></tr>') +
    '</tbody></table>';
}

// As linhas sao recriadas a cada repintura, entao os ouvintes delas tambem.
// Os controles NAO passam por aqui: eles sobrevivem a repintura e receberiam
// ouvinte duplicado a cada tecla.
function histBindRows(root){
  root.querySelectorAll('[data-operation-copy]').forEach(btn => {
    btn.onclick = () => {
      const record = histRecords().find(r => r.operationId === btn.dataset.operationCopy);
      operationCopyToClipboard(btn, record, btn.closest('.hist-detail').querySelector('[data-operation-copy-feedback]'));
    };
  });
  root.querySelectorAll('.hist-row').forEach(tr => {
    const abrir = () => {
      const id = tr.dataset.histId;
      histState.selected = (histState.selected === id) ? null : id;
      histRepaintResults();
    };
    tr.addEventListener('click', abrir);
    tr.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrir(); }
    });
  });
}

// REPINTURA parcial. Nao toca nos controles nem no <input> de busca: o valor
// digitado, o foco e a posicao do cursor sao do operador, e nenhuma
// consequencia de filtrar justifica tira-los dele.
function histRepaintResults(){
  const root = document.getElementById('execHistory');
  if (!root) return;
  const alvoStats = root.querySelector('#histStats');
  const alvoTabela = root.querySelector('#histTabela');
  if (!alvoStats || !alvoTabela) { renderOperationHistory(); return; }
  const filtrados = histFilter(histRecords());
  alvoStats.innerHTML = histStatsHTML(filtrados);
  alvoTabela.innerHTML = histTableHTML(filtrados);
  histBindRows(root);
}

// MONTAGEM do workspace. Roda ao entrar na visao; a partir dai filtro, busca e
// selecao repintam apenas os resultados.
function renderOperationHistory(){
  const root = document.getElementById('execHistory');
  if (!root) return;
  const todos = histRecords();

  if (!todos.length) {
    root.innerHTML = '<div class="card"><h2>Histórico</h2>' +
      '<p class="expl">Sem operações finalizadas.</p></div>';
    return;
  }

  const filtrados = histFilter(todos);
  // A lista de instrumentos vem de TODOS os registros, nao dos filtrados: um
  // filtro nao pode apagar a propria opcao que permitiria desfaze-lo.
  const instrumentos = [...new Set(todos.map(r => String(r.instrument || '')).filter(Boolean))].sort();

  const opcao = (v, rot, atual) =>
    '<option value="' + esc(v) + '"' + (atual === v ? ' selected' : '') + '>' + esc(rot) + '</option>';

  root.innerHTML = '<div class="card">' +
    '<h2>Histórico</h2>' +
    '<p class="expl">Memória institucional das Operações Únicas finalizadas. Registro histórico é evidência: ' +
    'os números descrevem o que foi observado e não projetam desempenho futuro.</p>' +
    '<div class="hist-stats" id="histStats">' + histStatsHTML(filtrados) + '</div>' +
    '<div class="hist-filters">' +
    '<label>Instrumento <select id="histInstrument">' + opcao('all', 'Todos', histState.instrument) +
      instrumentos.map(i => opcao(i, i, histState.instrument)).join('') + '</select></label>' +
    '<label>Direção <select id="histDirection">' + opcao('all', 'Todas', histState.direction) +
      opcao('BUY', 'BUY', histState.direction) + opcao('SELL', 'SELL', histState.direction) + '</select></label>' +
    '<label>Resultado <select id="histResult">' + opcao('all', 'Todas', histState.result) +
      opcao('Positiva', 'Positivas', histState.result) + opcao('Negativa', 'Negativas', histState.result) +
      opcao('Neutra', 'Neutras', histState.result) + opcao('Não informado', 'Não informados', histState.result) + '</select></label>' +
    '<label>Buscar <input type="search" id="histQuery" value="' + esc(histState.query) +
      '" placeholder="id, instrumento ou ordem"></label>' +
    '</div>' +
    '<div class="jp-table-scroll" id="histTabela">' + histTableHTML(filtrados) + '</div></div>';

  // Filtros e seleção mudam APENAS estado de apresentação. Nenhum caminho deste
  // arquivo chama save(), muta S ou toca a memória institucional.
  const liga = (id, campo) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => { histState[campo] = el.value; histRepaintResults(); });
  };
  liga('histInstrument', 'instrument');
  liga('histDirection', 'direction');
  liga('histResult', 'result');
  const q = document.getElementById('histQuery');
  if (q) q.addEventListener('input', () => { histState.query = q.value; histRepaintResults(); });
  histBindRows(root);
}

// Contrato dos workspaces montados sob demanda (20-ui/13-exec-views.js).
window.JPWHistoryUI = { render: renderOperationHistory };

// A12: projeção textual de fatos, sem passar por render(), normalização ou
// operationBuildSnapshot(). Esses caminhos têm efeitos; copiar não confirma,
// finaliza ou registra nada. Whitelist deliberada: objetos de conta/onboarding,
// logs, notas livres e credenciais nunca são serializados para o clipboard.
function operationCopyScalar(value){
  if (typeof value === 'number') return Number.isFinite(value) ? String(value).replace('.', ',') : '';
  if (typeof value !== 'string') return '';
  return value.replace(/[\u0000-\u001f\u007f]+/g, ' ').trim();
}
function operationCopyNumber(value){
  if (typeof value === 'number') return operationCopyScalar(value);
  if (typeof value !== 'string') return '';
  const text = value.trim();
  if (text.toUpperCase() === 'PENDING') return 'PENDING';
  return /^-?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(text) && Number.isFinite(Number(text))
    ? text.replace('.', ',') : '';
}
function operationCopyMoney(value, context){
  const text = operationCopyNumber(value);
  if (!text || text === 'PENDING') return text;
  return histMoney(value, context);
}
function operationCopyHistoricalMoney(value, context){
  return operationCopyMoney(value, context);
}
function operationCopyOrderLines(o, position, historical, context){
  const monetary = historical ? context : histCapturedContext(o);
  const lines = [];
  const row = (label, value) => { if (value !== '') lines.push(label + ': ' + value); };
  const label = operationCopyScalar(historical ? o.label : o.id);
  lines.push('Ordem ' + position + (label ? ' — ' + label : ''));
  row('Instrumento', operationCopyScalar(o.par));
  row('Direção', operationCopyScalar(o.tipo));
  row('Status registrado', operationCopyScalar(o.status));
  row('Lote', operationCopyNumber(o.lote));
  row('Entrada', operationCopyNumber(o.entry));
  row('Stop loss', operationCopyNumber(o.sl));
  row('Take profit', operationCopyNumber(o.tp));
  // result é preenchimento de fechamento; zero na ordem aberta é default,
  // não resultado realizado. Não o promover a lucro/prejuízo nessa situação.
  if (o.status === 'Fechada') row('Resultado registrado (' + (monetary && monetary.currency || 'unidade ausente') + ')',
    operationCopyMoney(o.result, monetary));
  row('Abertura registrada', operationCopyScalar(o.openedAt));
  row('Fechamento registrado', operationCopyScalar(o.closedAt));
  return lines;
}
function operationCopyProjection(record){
  const historical = !!record;
  const captured = historical ? histCapturedContext(record) : null;
  const orders = historical
    ? (Array.isArray(record.ordersSnapshot) ? record.ordersSnapshot.map(o => ({o, position:histPhaseName(Number.isInteger(o.phase) ? o.phase - 1 : null, record) + '/' + (o.gridIndex + 1)})) : [])
    : operationLiveOrders().map(({o, pi, oi}) => ({o, position:'F' + (pi + 1) + '/' + (oi + 1)}));
  if (!historical && !orders.length) return null;
  const op = historical ? record : (S.activeOperation || {});
  const openCount = orders.filter(x => x.o.status === 'Aberta').length;
  const status = historical ? 'FINALIZADA — registro histórico'
    : !openCount ? 'SEM ORDENS ABERTAS — aguarda finalização formal'
    : orders.length === 1 ? 'ABERTA — entrada registrada' : 'EM ANDAMENTO';
  const lines = ['JP Wealth · Operação', status];
  const row = (label, value) => { if (value !== '') lines.push(label + ': ' + value); };
  row('Operação ID', operationCopyScalar(op.operationId));
  if (!op.operationId) lines.push('Identidade da operação não registrada.');
  if (historical) {
    row('Instrumento', operationCopyScalar(record.instrument));
    row('Direção', operationCopyScalar(record.direction));
  } else {
    const thesis = operationResolveThesis(orders);
    if (thesis.ok) {
      row('Instrumento', operationCopyScalar(thesis.instrument));
      row('Direção', operationCopyScalar(thesis.direction));
    }
    if (!thesis.ok || (thesis.findings || []).some(f => f.code === 'INSTRUMENT_CONFLICT' || f.code === 'DIRECTION_CONFLICT'))
      lines.push('Tese divergente entre as ordens registradas; confira instrumento e direção.');
  }
  row('Abertura registrada', operationCopyScalar(op.openedAt));
  row('Origem da abertura', operationCopyScalar(op.openedAtSource));
  if (historical) {
    row('Encerramento formal', operationCopyScalar(record.closedAt));
    row('Finalização registrada', operationCopyScalar(record.finalizedAt));
  }
  lines.push('Ordens registradas nas grades: ' + orders.length);
  orders.forEach(({o, position}) => lines.push('', ...operationCopyOrderLines(o, position, historical, captured)));
  if (historical) {
    lines.push('', 'Resultado da operação finalizada');
    const unit = captured.currency || 'unidade ausente';
    row('Resultado líquido registrado (' + unit + ')', operationCopyHistoricalMoney(record.netResult, captured));
    row('Base do retorno registrada (' + unit + ')', operationCopyHistoricalMoney(record.referenceBalance, captured));
    row('Defesas informadas', operationCopyNumber(record.defenseCount));
    row('Origem das defesas', operationCopyScalar(record.defenseCountSource));
    lines.push('', 'Contexto histórico capturado');
    row('Conta ID', operationCopyScalar(captured.accountId) || 'Não capturada');
    row('Período ID', operationCopyScalar(captured.periodId) || 'Não capturado');
    row('Moeda', captured.currency || (captured.currencyConflict ? 'Conflitante — unidade ausente' : 'Unidade ausente'));
    if (captured.identityConflict) lines.push('Identidades conflitantes nos contextos capturados.');
    const snapshot = record.policySnapshot || record.recordContext && record.recordContext.policySnapshot;
    row('Política capturada', operationCopyScalar(snapshot && (snapshot.policyVersion || snapshot.version)) || 'LEGACY_UNRESOLVED');
    for (const [label, context] of [['Entrada', record.recordContext], ['Fechamento', record.finalizationContext]]) {
      if (!context || typeof context !== 'object') continue;
      row(label + ' · conta ID', operationCopyScalar(context.accountId));
      row(label + ' · período ID', operationCopyScalar(context.periodId));
      row(label + ' · observação', operationCopyScalar(context.observedAt));
      row(label + ' · proveniência', operationCopyScalar(context.provenance));
    }
    lines.push('Equity final e DD não são inferidos dos contextos capturados.');
  } else {
    const closed = orders.filter(x => x.o.status === 'Fechada');
    if (closed.length) {
      lines.push('', 'Resultado fechado até agora');
      // O agregado existente aplica coerção a ausentes. Só consumi-lo quando
      // todos os resultados envolvidos são números informados, sem PENDING.
      const known = closed.every(({o}) => operationCopyNumber(o.result) && operationCopyNumber(o.result) !== 'PENDING');
      const currencies = [...new Set(closed.map(({o}) => histCapturedContext(o).currency))];
      const opCurrency = histCapturedContext(op).currency;
      const comparable = currencies.length === 1 && currencies[0] && (!opCurrency || opCurrency === currencies[0]);
      if (known && comparable) row('Resultado líquido das ordens fechadas (' + currencies[0] + ')', operationCopyMoney(netOpAtual(), {currency:currencies[0]}));
      else lines.push('Resultado líquido indisponível: há resultado não informado, PENDING ou moeda ausente/conflitante.');
    }
    lines.push('', 'Contexto atual do cadastro — não é snapshot da entrada');
    const master = typeof getMaster === 'function' ? getMaster() : null;
    if (master) row(master.tipo === 'MESTRE' ? 'Conta mestre cadastrada' : 'Conta cadastrada de referência', operationCopyScalar(master.nome));
    const key = S.period && S.period.profile;
    if (key === 'PENDING') row('Perfil cadastrado', 'PENDING');
    else if (typeof key === 'string' && RISK_PROFILES.some(p => p.key === key || p.name === key)) {
      row('Perfil cadastrado', operationCopyScalar(getActiveRiskProfile(key).name));
    }
    row('Período cadastrado', operationCopyScalar(S.period && S.period.nome));
    row('Início do período', operationCopyScalar(S.params && S.params.inicio));
    // This legacy scalar has no currency provenance. Neither the operation nor
    // the selected account establishes the unit of this independent book value.
    row('Saldo contábil atual (book, unidade ausente)', operationCopyMoney(S.params && S.params.saldoAtu));
    lines.push('Equity flutuante e veredito normativo não compõem esta cópia.');
  }
  return lines.join('\n');
}
function operationCopyToClipboard(btn, record, feedback){
  const notify = message => { if (feedback) feedback.textContent = message; };
  if (typeof jpWealthPersistenceOutcomeIsUnknown === 'function' && jpWealthPersistenceOutcomeIsUnknown()) {
    notify('Persistência indeterminada: confira o estado gravado antes de copiar a operação como confirmada.');
    return Promise.resolve(false);
  }
  const text = operationCopyProjection(record);
  if (!text) { notify('Não há operação registrada para copiar.'); return Promise.resolve(false); }
  if (btn && btn.__operationCopyInFlight) return Promise.resolve(false);
  if (btn) btn.__operationCopyInFlight = true;
  notify('Copiando operação…');
  // Reutiliza a API + fallback já suportados pelo portátil. Nenhum envio ou
  // abertura de aplicativo externo; a pessoa decide onde colar o texto.
  return Promise.resolve().then(() => mvpNotesCopyText(text)).then(() => {
    notify('Operação copiada. Cole o texto onde desejar.');
    return true;
  }, () => {
    notify('Não foi possível copiar a operação. O registro permanece preservado.');
    return false;
  }).finally(() => {
    if (btn) {
      btn.__operationCopyInFlight = false;
      // execCommand pode mover o foco para a textarea temporária. Só o devolver
      // se nenhum outro controle tiver recebido foco durante a cópia assíncrona.
      if (btn.isConnected && document.activeElement === document.body) btn.focus({preventScroll:true});
    }
  });
}
function renderOperationCopyAction(){
  const btn = document.getElementById('copyOperationBtn');
  if (!btn) return;
  btn.hidden = operationLiveOrders().length === 0;
  btn.disabled = btn.hidden;
  btn.onclick = () => operationCopyToClipboard(btn, null, document.getElementById('operationCopyFeedback'));
}
