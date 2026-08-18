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
  const base = +r.referenceBalance;
  if (!Number.isFinite(base) || base <= 0) return null;
  return (+r.netResult || 0) / base * 100;
}
function histResultClass(r){
  const n = +r.netResult || 0;
  return n > 0 ? 'Positiva' : (n < 0 ? 'Negativa' : 'Neutra');
}
function histFmtDate(iso){
  const t = Date.parse(iso);
  return Number.isFinite(t) ? new Date(t).toLocaleDateString('pt-BR') : '—';
}
function histPhaseName(idx){
  // typeof, e nao coercao: `+null === 0` renderizaria 'Fase 1' para um maximo
  // que nunca foi observado — o registro diz null e a tela mentiria.
  if (typeof idx !== 'number' || !Number.isFinite(idx)) return '—';
  const f = (S.matrix || [])[+idx];
  return (f && f.nome) ? f.nome : ('Fase ' + ((+idx) + 1));
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
  const positivas = records.filter(r => (+r.netResult || 0) > 0).length;
  const resultados = records.map(r => +r.netResult || 0);
  const dur = histMedian(records.map(histDurationMs));
  const def = histMedian(records.map(r => Number.isFinite(+r.defenseCount) ? +r.defenseCount : null));
  return {
    n,
    acumulado: resultados.reduce((s, x) => s + x, 0),
    positivas,
    taxaPositivas: positivas / n * 100,
    duracaoMediana: dur,
    defesasMedianas: def,
    maior: Math.max(...resultados),
    menor: Math.min(...resultados)
  };
}

// ---- render ----
function histCard(rotulo, valor, nota){
  return '<div class="hist-stat"><div class="hist-stat-l">' + esc(rotulo) + '</div>' +
    '<div class="hist-stat-v">' + esc(valor) + '</div>' +
    (nota ? '<div class="hist-stat-n">' + esc(nota) + '</div>' : '') + '</div>';
}

function histRenderDetail(r){
  const ordens = (r.ordersSnapshot || []).map(o =>
    '<tr><td>' + esc(o.label || '(sem ID)') + '</td><td>' + esc('F' + o.phase) + '</td>' +
    '<td>' + esc(o.par || '—') + '</td><td>' + esc(o.tipo || '—') + '</td>' +
    '<td class="hist-num">' + esc(String(o.lote ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(String(o.entry ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(String(o.sl ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(String(o.tp ?? '—')) + '</td>' +
    '<td class="hist-num">' + esc(fmtMoney2(+o.result || 0)) + '</td>' +
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
    '<div><b>Instrumento</b><br>' + esc(r.instrument || '—') + '</div>' +
    '<div><b>Direção</b><br>' + esc(r.direction || '—') + '</div>' +
    '<div><b>Abertura</b><br>' + esc(r.openedAt ? histFmtDate(r.openedAt) : 'Desconhecida') +
      (r.openedAtSource ? ' <span class="hist-src">(' + esc(r.openedAtSource) + ')</span>' : '') + '</div>' +
    '<div><b>Encerramento</b><br>' + esc(histFmtDate(r.closedAt)) + '</div>' +
    '<div><b>Duração</b><br>' + esc(histFmtDuration(histDurationMs(r))) + '</div>' +
    '<div><b>Fase máxima da Conta</b><br>' + esc(histPhaseName(r.maxAccountPhaseReached)) +
      (degradada ? ' <span class="hist-degradada" title="Houve falha de captura durante a operação: este é o maior valor conhecido, não necessariamente o máximo absoluto.">máximo conhecido / integridade degradada</span>'
       : naoObservada ? ' <span class="hist-degradada" title="A captura da Fase da Conta nunca se aplicou durante esta operação, e nenhuma falha foi registrada. Ausência de medição, não medição de ausência.">não observada</span>' : '') + '</div>' +
    '<div><b>Fase máxima da Grade</b><br>' + esc(r.maxGridPhaseReached == null ? '—' : histPhaseName(r.maxGridPhaseReached)) + '</div>' +
    '<div><b>Defesas</b><br>' + esc(String(r.defenseCount ?? '—')) +
      (r.defenseCountSource ? ' <span class="hist-src">(' + esc(r.defenseCountSource) + ')</span>' : '') + '</div>' +
    '<div><b>Resultado líquido</b><br>' + esc(fmtMoney2(+r.netResult || 0)) + '</div>' +
    '<div><b>Base do retorno</b><br>' + esc(r.referenceBalance == null ? '—' : fmtMoney2(r.referenceBalance)) +
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
    '<p class="hist-ro">Registro histórico — somente leitura.</p></div>';
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
    histCard('Resultado líquido acumulado', fmtMoney2(st.acumulado)) +
    histCard('Taxa de operações positivas', st.taxaPositivas.toFixed(0) + '%',
             st.positivas + ' de ' + st.n + ' registradas') +
    histCard('Duração mediana',
             st.duracaoMediana.valor == null ? '—' : histFmtDuration(st.duracaoMediana.valor),
             'n = ' + st.duracaoMediana.n) +
    histCard('Defesas medianas',
             st.defesasMedianas.valor == null ? '—' : String(st.defesasMedianas.valor),
             'n = ' + st.defesasMedianas.n) +
    histCard('Maior resultado', fmtMoney2(st.maior)) +
    histCard('Menor resultado', fmtMoney2(st.menor));
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
      '<td class="hist-num hist-' + esc(cls.toLowerCase()) + '">' + esc(fmtMoney2(+r.netResult || 0)) + '</td>' +
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
      opcao('Neutra', 'Neutras', histState.result) + '</select></label>' +
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
