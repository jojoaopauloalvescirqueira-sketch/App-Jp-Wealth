// ============ ESTUDOS DOS PIVOTS · INTERFACE (N1 — apresentação) ============
// Workspace do Execution Board para a memória empírica dos maiores pivots H1/H4
// identificados manualmente pelo operador.
//
// SEPARAÇÃO DE RESPONSABILIDADES, deliberada:
//   · a lista de instrumentos vem de instrumentCatalog() — NUNCA há símbolo
//     escrito aqui, e nenhuma cópia do catálogo entra no estado dos estudos;
//   · toda a matemática e a estatística vivem em 10-domain/10-pivot-studies.js,
//     puras e sem DOM; este arquivo lê entrada, chama o motor e escreve texto;
//   · a persistência é S.pivotStudies.studies, gravada apenas em ação explícita.
//
// PRINCÍPIO DE SEGURANÇA OPERACIONAL: nada aqui autoriza operação. Navegar até
// este workspace ou salvar um pivot não altera fase, clearance, risco,
// alavancagem, ordem, LIFO, quarentena ou qualquer estado estatutário.
//
// PRINCÍPIO ESTATÍSTICO: a amostra é escolhida pelo operador, que registra de
// propósito os MAIORES pivots que encontrou. Toda a tela fala de "pivots
// registrados neste estudo" e nenhuma frase converte essa amostra em
// probabilidade, frequência, expectativa ou alvo.

// Estado EFÊMERO — seleção, filtros, ordenação e rascunhos não salvos. Não
// entra em S, localStorage, backup, schema ou migração.
let pvInstrumentId = null;
let pvStudyId = null;
let pvNewStudyOpen = false;
let pvNewStudyDraft = { periodStart: '', periodEnd: '' };
let pvFormOpen = false;
let pvEditingId = null;      // null enquanto o formulário for de pivot novo
let pvDraft = null;
let pvDirty = false;
let pvFilters = { timeframe: 'all', direction: 'all', criterion: 'valid' };
let pvSort = { key: 'amplitude', ascending: false };
let pvHighlightId = null;

const PV_EMPTY_DRAFT = {
  timeframe: 'H4', startDatetime: '', startPrice: '',
  endDatetime: '', endPrice: '', maxCorrectionPct: '', notes: ''
};
const PV_FIELDS = ['timeframe', 'startDatetime', 'startPrice', 'endDatetime', 'endPrice', 'maxCorrectionPct', 'notes'];
const PV_SORT_LABELS = [
  ['amplitude', false, 'Amplitude ↓'], ['amplitude', true, 'Amplitude ↑'],
  ['date', true, 'Data'], ['duration', false, 'Duração'], ['correction', false, 'Correção']
];

function pvMath() { return (window.JPWPivots && window.JPWPivots.math) || null; }
function pvStudies() {
  return (S.pivotStudies && Array.isArray(S.pivotStudies.studies)) ? S.pivotStudies.studies : [];
}
function pvStudyById(id) { return pvStudies().find(st => st.id === id) || null; }
function pvStudiesFor(instrumentId) {
  return pvStudies().filter(st => st.instrumentId === instrumentId);
}

// ---- formatação ----------------------------------------------------------
// O catálogo não tem metadado de dígitos por instrumento (auditado nos Estudos
// NoCoda). Em vez de criar uma segunda tabela de precisão, preço usa formatter
// neutro de até 8 casas com zeros à direita removidos. O cálculo interno NUNCA
// depende deste texto.
function pvFmtPrice(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
  const trimmed = value.toFixed(8).replace(/0+$/, '').replace(/\.$/, '');
  return (trimmed === '' || trimmed === '-0' ? '0' : trimmed).replace('.', ',');
}
// fmtPct() é o formatador percentual canônico do app e recebe FRAÇÃO; as
// amplitudes já estão em pontos percentuais, daí o /100. Reusar é melhor que
// abrir um segundo formatador percentual só para esta tela.
function pvFmtPct(value) {
  return (typeof value === 'number' && Number.isFinite(value)) ? fmtPct(value / 100) : '—';
}
function pvFmtDuration(ms) {
  const math = pvMath();
  return (math && typeof ms === 'number' && Number.isFinite(ms)) ? math.formatDuration(ms) : '—';
}
// Exibe o carimbo como foi digitado, sem conversão de fuso: só reordena os
// campos para a convenção brasileira.
function pvFmtDatetime(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/.exec(String(value || ''));
  return match ? `${match[3]}/${match[2]}/${match[1]} ${match[4]}:${match[5]}` : '—';
}
function pvFmtDate(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value || ''));
  return match ? `${match[3]}/${match[2]}/${match[1]}` : '—';
}
function pvDirectionLabel(direction) {
  return direction === 'bullish' ? 'Alta' : (direction === 'bearish' ? 'Baixa' : '—');
}
// Três estados, não dois. Um registro vindo de backup pode trazer correção fora
// de 0–100%: chamá-lo de "excedido" seria impreciso, e apagá-lo é proibido.
function pvCriterionLabel(record) {
  if (!record.correctionInDomain) return 'correção fora de 0–100% — registro preservado';
  return record.withinRule ? 'critério informado: atendido' : 'critério informado: excedido';
}

// ---- seleção -------------------------------------------------------------

// Instrumentos oferecidos: o catálogo operável MAIS os instrumentos que já
// possuem estudo. A união é o que garante a seção 53 — instrumento removido ou
// desativado no Motor de Lote sai da operação, mas sua memória técnica continua
// alcançável em vez de virar dado órfão inacessível.
function pvInstrumentOptions() {
  const catalog = (typeof instrumentCatalog === 'function') ? instrumentCatalog() : [];
  const options = catalog.map(i => ({ id: i.id, name: i.name, operable: true }));
  const known = new Set(options.map(o => o.id));
  pvStudies().forEach(st => {
    if (st.instrumentId && !known.has(st.instrumentId)) {
      known.add(st.instrumentId);
      options.push({ id: st.instrumentId, name: st.instrumentId, operable: false });
    }
  });
  return options;
}

function pvEnsureSelection() {
  const options = pvInstrumentOptions();
  if (!options.length) { pvInstrumentId = null; pvStudyId = null; return options; }
  if (!pvInstrumentId || !options.some(o => o.id === pvInstrumentId)) {
    // Preferir um instrumento que já tenha estudo evita abrir sempre no vazio.
    const withStudy = options.find(o => pvStudiesFor(o.id).length);
    pvInstrumentId = (withStudy || options[0]).id;
    pvStudyId = null;
  }
  const mine = pvStudiesFor(pvInstrumentId);
  if (!pvStudyId || !mine.some(st => st.id === pvStudyId)) pvStudyId = mine.length ? mine[0].id : null;
  return options;
}

// Guarda de descarte (seção 49). O app não tem arquitetura de rascunho e o
// padrão dominante de confirmação é confirm() nativo; basta impedir descarte
// silencioso, sem introduzir um sistema de drafts só para esta tela.
//
// Fecha o formulário nos DOIS caminhos, e não só quando havia alteração. O
// formulário é filho do estudo selecionado e edita um pivot dele: deixá-lo
// aberto ao trocar de estudo ou de instrumento o apontava para um registro que
// já não pertence à seleção, e o "Salvar" seguinte não encontrava o alvo e
// retornava em silêncio — o operador digitava, clicava e nada acontecia.
function pvConfirmDiscard() {
  if (pvDirty && !confirm('Há um pivot em edição com alterações não salvas. Continuar descarta essas alterações.')) return false;
  pvCloseForm();
  return true;
}

function pvCloseForm() {
  pvFormOpen = false; pvEditingId = null; pvDraft = null; pvDirty = false;
}

// O estudo em foco sumiu por baixo da tela — outra aba, importação de backup ou
// limpeza. Repintar ressincroniza a seleção; avisar é o que impede o clique de
// terminar em nada. O contrato anti-silêncio deste arquivo vale para os três
// caminhos de ação, não só para o salvar.
function pvStudyEmFoco(acao) {
  const study = pvStudyById(pvStudyId);
  if (study) return study;
  pvCloseForm();
  renderPivotStudies();
  alert('O estudo que estava aberto não existe mais nesta base — ela foi substituída em outra aba, por importação de backup ou por limpeza.\n\nNada foi ' + acao + '. A tela acaba de ser recarregada com o estado atual.');
  return null;
}

// ---- render --------------------------------------------------------------

function renderPivotStudies() {
  const root = document.getElementById('execPivots');
  if (!root) return;
  const math = pvMath();
  if (!math) return;

  const options = pvEnsureSelection();
  const head = `<h2>Estudos dos Pivots <span class="art">memória empírica — não autoriza operação</span></h2>`;

  if (!options.length) {
    root.innerHTML = `<div class="card">${head}
      <p class="expl">Nenhum instrumento operável no Motor de Lote e nenhum estudo gravado. O catálogo é a fonte canônica desta tela.</p></div>`;
    return;
  }

  const study = pvStudyById(pvStudyId);
  root.innerHTML = `
    <div class="card">
      ${head}
      <p class="expl">Registra os maiores pivots H1 e H4 que você identificou no gráfico e organiza a amostra: amplitude, duração, direção e a maior correção interna informada. O software não detecta pivots — ele estrutura, calcula, ordena e preserva o que você observou.</p>
      ${pvPickerHTML(options)}
      ${pvNewStudyOpen ? pvNewStudyHTML() : ''}
      ${study ? pvStudyHTML(study, math) : pvEmptyStudyHTML()}
    </div>`;

  pvBind(root);
  if (pvFormOpen) pvUpdateDerived();
  if (pvHighlightId) pvApplyHighlight();
}

function pvPickerHTML(options) {
  const instrumentOptions = options.map(o =>
    `<option value="${esc(o.id)}"${o.id === pvInstrumentId ? ' selected' : ''}>${esc(o.name)}${o.operable ? '' : ' (fora do catálogo)'}${pvStudiesFor(o.id).length ? ' ·' : ''}</option>`
  ).join('');
  const mine = pvStudiesFor(pvInstrumentId);
  const studyOptions = mine.length
    ? mine.map(st => `<option value="${esc(st.id)}"${st.id === pvStudyId ? ' selected' : ''}>${esc(pvFmtDate(st.periodStart))} → ${esc(pvFmtDate(st.periodEnd))} (${st.pivots.length})</option>`).join('')
    : '<option value="">nenhum estudo neste instrumento</option>';
  return `
    <div class="pv-picker">
      <div class="field">
        <label for="pvInstrument">Instrumento</label>
        <select id="pvInstrument">${instrumentOptions}</select>
      </div>
      <div class="field">
        <label for="pvStudy">Estudo</label>
        <select id="pvStudy"${mine.length ? '' : ' disabled'}>${studyOptions}</select>
      </div>
      <div class="pv-picker-actions">
        <button type="button" class="reset-btn" id="pvNewStudyBtn">Novo Estudo</button>
        ${pvStudyId ? '<button type="button" class="reset-btn pv-danger" id="pvDeleteStudyBtn">Excluir estudo</button>' : ''}
      </div>
      <p class="note pv-picker-note">O ponto marca instrumentos que já possuem estudo. Instrumento retirado do Motor de Lote continua listado enquanto tiver memória técnica gravada.</p>
    </div>`;
}

function pvNewStudyHTML() {
  return `
    <fieldset class="pv-newstudy">
      <legend>Novo estudo</legend>
      <p class="note">O período é a janela histórica que você efetivamente analisou. Um mesmo instrumento pode ter vários estudos de períodos diferentes — nenhum sobrescreve o outro.</p>
      <div class="pv-newstudy-fields">
        <div class="field">
          <label for="pvPeriodStart">Data inicial</label>
          <input type="date" id="pvPeriodStart" value="${esc(pvNewStudyDraft.periodStart)}" aria-describedby="pvNewStudyErr">
        </div>
        <div class="field">
          <label for="pvPeriodEnd">Data final</label>
          <input type="date" id="pvPeriodEnd" value="${esc(pvNewStudyDraft.periodEnd)}" aria-describedby="pvNewStudyErr">
        </div>
      </div>
      <p class="pv-field-err" id="pvNewStudyErr" role="alert"></p>
      <div class="pv-actions">
        <button type="button" class="reset-btn" id="pvCreateStudyBtn">Criar</button>
        <button type="button" class="reset-btn ghost" id="pvCancelStudyBtn">Cancelar</button>
      </div>
    </fieldset>`;
}

function pvEmptyStudyHTML() {
  return `<p class="expl pv-empty">Nenhum estudo selecionado para este instrumento. Crie um estudo informando o período histórico analisado.</p>`;
}

function pvStudyHTML(study, math) {
  // Mesmo escopo para o resumo e para a lista: o filtro de critério governa os
  // dois, para que o "n" jamais descreva uma amostra diferente da tabela.
  const stats = math.stats(study.pivots, { scope: pvFilters.criterion });
  const records = pvVisibleRecords(study, math);
  // Registros que não produzem derivados (preços iguais, fim anterior ao início,
  // preço não numérico) vêm de backup — a normalização de propósito não valida a
  // matemática, para não apagar entrada do operador em silêncio. Preservar sem
  // dar acesso, porém, é pior que apagar: o total dizia "1 de 3" e os outros dois
  // não apareciam em filtro nenhum, sem editar e sem excluir. Ficam aqui, em
  // linha degradada, com o motivo e as duas ações — fora da amostra, como já
  // estavam, mas alcançáveis.
  const quebrados = study.pivots.filter(p => !math.derive(p));
  return `
    <div class="pv-study">
      <p class="pv-period">Período analisado <b>${esc(pvFmtDate(study.periodStart))} → ${esc(pvFmtDate(study.periodEnd))}</b></p>
      ${pvStatsHTML(stats)}
      ${pvFiltersHTML()}
      ${pvTableHTML(records, stats, quebrados, math)}
      <div class="pv-actions">
        <button type="button" class="reset-btn" id="pvAddPivotBtn"${pvFormOpen ? ' disabled' : ''}>+ Adicionar Pivot</button>
      </div>
      ${pvFormOpen ? pvFormHTML() : ''}
    </div>`;
}

// ---- estatística ---------------------------------------------------------

function pvMetric(label, value, sub) {
  return `<div class="metric"><div class="k">${label}</div><div class="v sm">${value}</div>${sub ? `<div class="sub">${sub}</div>` : ''}</div>`;
}

// "Sem dados" e "0%" são coisas diferentes: zero é um valor observado, ausência
// de observação não é. Amostra vazia nunca vira zero nesta tela.
function pvStatValue(value, formatter) {
  return (value === null || value === undefined) ? '<span class="muted">Sem dados</span>' : formatter(value);
}

function pvStatsHTML(stats) {
  const tfSummary = stats.timeframes;
  const scope = stats.scope === 'all' ? 'todos os pivots registrados'
    : (stats.scope === 'outside' ? 'somente os que excedem o critério' : 'pivots dentro do critério');
  return `
    <div class="pv-stats">
      <h3>Resumo da amostra <span class="art">n = ${stats.n} · ${scope}</span></h3>
      <div class="metrics pv-metrics">
        ${pvMetric('Pivots na amostra', String(stats.n), `H1 = ${tfSummary.H1.n} · H4 = ${tfSummary.H4.n}`)}
        ${pvMetric('Maior pivot registrado', pvStatValue(stats.max, pvFmtPct), stats.maxTimeframe ? esc(stats.maxTimeframe) : 'sem amostra')}
        ${pvMetric('Mediana da amplitude', pvStatValue(stats.median, pvFmtPct), 'medida central principal')}
        ${pvMetric('Média da amplitude', pvStatValue(stats.mean, pvFmtPct), 'secundária à mediana')}
        ${pvMetric('Duração mediana', pvStatValue(stats.medianDurationMs, pvFmtDuration), 'dos pivots da amostra')}
        ${pvMetric('Correção máxima mediana', pvStatValue(stats.medianCorrection, pvFmtPct), 'mediana das correções informadas')}
      </div>
      <div class="pv-split">
        ${pvComparisonHTML(stats)}
        ${pvTopHTML(stats)}
      </div>
      <p class="pv-distribution">Distribuição por direção nesta amostra — Alta: <b>${stats.bullish}</b> · Baixa: <b>${stats.bearish}</b>.</p>
      ${stats.outside ? `<p class="note pv-outside-note">${stats.outside} pivot(s) registrado(s) excede(m) o critério de ${pvFmtPct(pvMath().MAX_CORRECTION_PCT)} e ${stats.scope === 'valid' ? 'ficam fora da amostra principal' : 'compõem esta amostra pelo filtro de critério'}. Continuam gravados e podem ser editados.</p>` : ''}
      <p class="note pv-bias">Estatísticas descritivas dos pivots registrados neste estudo. A amostra é selecionada pelo operador e não representa a frequência de todos os pivots do instrumento — os números acima não estimam probabilidade, expectativa ou próximo movimento.</p>
    </div>`;
}

function pvComparisonHTML(stats) {
  const row = (label, pick, formatter) => `
    <tr><th scope="row">${label}</th>
      <td>${pvStatValue(pick(stats.timeframes.H1), formatter)}</td>
      <td>${pvStatValue(pick(stats.timeframes.H4), formatter)}</td></tr>`;
  return `
    <div class="pv-compare">
      <h4>H1 × H4</h4>
      <div class="jp-table-scroll">
        <table class="dtable pv-compare-table">
          <thead><tr><th scope="col">Medida</th><th scope="col">H1</th><th scope="col">H4</th></tr></thead>
          <tbody>
            <tr><th scope="row">n</th><td>${stats.timeframes.H1.n}</td><td>${stats.timeframes.H4.n}</td></tr>
            ${row('Máximo', s => s.max, pvFmtPct)}
            ${row('Mediana', s => s.median, pvFmtPct)}
            ${row('Duração mediana', s => s.medianDurationMs, pvFmtDuration)}
          </tbody>
        </table>
      </div>
      <p class="note">Diferenças observadas entre os dois timeframes desta amostra. Nenhuma conclusão automática é derivada daqui.</p>
    </div>`;
}

function pvTopHTML(stats) {
  const list = tf => {
    const top = stats.timeframes[tf].top;
    if (!top.length) return `<p class="note">${tf}: <span class="muted">Sem dados</span></p>`;
    // A numeracao e do proprio <ol>: repeti-la no rotulo do botao produziria
    // "1. 1. 4,07%" na tela e leitura duplicada em leitor de tela.
    return `<h5>TOP ${tf}</h5><ol class="pv-top-list">` + top.map(r =>
      `<li><button type="button" class="pv-top-link" data-pv-goto="${esc(r.id)}">${pvFmtPct(r.percentageRange)}</button>
        <span class="pv-top-when">${esc(pvFmtDatetime(r.pivot.startDatetime))}</span></li>`).join('') + '</ol>';
  };
  return `<div class="pv-top"><h4>Maiores amplitudes</h4>${list('H1')}${list('H4')}</div>`;
}

// ---- filtros, ordenação e tabela ----------------------------------------

function pvVisibleRecords(study, math) {
  let records = math.records(study.pivots);
  if (pvFilters.criterion === 'valid') records = records.filter(r => r.withinRule);
  else if (pvFilters.criterion === 'outside') records = records.filter(r => !r.withinRule);
  if (pvFilters.timeframe !== 'all') records = records.filter(r => r.timeframe === pvFilters.timeframe);
  if (pvFilters.direction !== 'all') records = records.filter(r => r.direction === pvFilters.direction);
  return math.sort(records, pvSort.key, pvSort.ascending);
}

function pvSegHTML(group, label, entries, current) {
  const buttons = entries.map(([value, text]) =>
    `<button type="button" data-pv-filter="${group}" data-pv-value="${value}" class="${value === current ? 'on' : ''}" aria-pressed="${value === current}">${text}</button>`
  ).join('');
  return `<div class="field pv-filter"><span class="pv-filter-label" id="pvFilter_${group}">${label}</span>
    <div class="seg" role="group" aria-labelledby="pvFilter_${group}">${buttons}</div></div>`;
}

function pvFiltersHTML() {
  const sortOptions = PV_SORT_LABELS.map(([key, ascending, text]) => {
    const value = key + ':' + (ascending ? 'asc' : 'desc');
    const selected = key === pvSort.key && ascending === pvSort.ascending;
    return `<option value="${value}"${selected ? ' selected' : ''}>${text}</option>`;
  }).join('');
  return `
    <div class="pv-filters">
      ${pvSegHTML('timeframe', 'Timeframe', [['all', 'Todos'], ['H1', 'H1'], ['H4', 'H4']], pvFilters.timeframe)}
      ${pvSegHTML('direction', 'Direção', [['all', 'Todas'], ['bullish', 'Alta'], ['bearish', 'Baixa']], pvFilters.direction)}
      ${pvSegHTML('criterion', 'Critério', [['valid', 'Somente válidos'], ['all', 'Todos'], ['outside', 'Fora do critério']], pvFilters.criterion)}
      <div class="field pv-filter">
        <label for="pvSort">Ordenar por</label>
        <select id="pvSort">${sortOptions}</select>
      </div>
    </div>`;
}

// Tabela com rótulos por célula (data-label): abaixo de 760px o CSS a converte
// em cards, sem markup duplicado e sem rolagem horizontal impraticável.
// Linha degradada de um registro incalculável: derivados como '—', motivo em
// palavras e as MESMAS ações da linha normal. Nunca é filtrada — nenhum filtro
// sabe classificá-la, e escondê-la de novo recriaria o dado preso.
function pvBrokenRowHTML(pivot, math, index) {
  const validation = math.validate(pivot);
  const motivo = (validation.errors && validation.errors.length)
    ? validation.errors[0].message
    : 'Registro incompleto para cálculo.';
  return `
    <tr data-pv-row="${esc(pivot.id)}" class="pv-broken">
      <td data-label="#">${index}</td>
      <td data-label="TF">${esc(pivot.timeframe || '—')}</td>
      <td data-label="Início">${esc(pvFmtDatetime(pivot.startDatetime))}<span class="pv-cell-sub">${esc(pvFmtPrice(pvMath().parseNumber(pivot.startPrice)))}</span></td>
      <td data-label="Fim">${esc(pvFmtDatetime(pivot.endDatetime))}<span class="pv-cell-sub">${esc(pvFmtPrice(pvMath().parseNumber(pivot.endPrice)))}</span></td>
      <td data-label="Direção">—</td>
      <td data-label="Amplitude">—</td>
      <td data-label="Duração">—</td>
      <td data-label="Correção">${pvFmtPct(pvMath().parseNumber(pivot.maxCorrectionPct))}<span class="pv-cell-sub">${esc(motivo)}</span></td>
      <td data-label="Ações" class="pv-row-actions">
        <button type="button" class="pv-mini" data-pv-edit="${esc(pivot.id)}">Corrigir</button>
        <button type="button" class="pv-mini pv-danger" data-pv-delete="${esc(pivot.id)}">Excluir</button>
      </td>
    </tr>`;
}

function pvTableHTML(records, stats, quebrados, math) {
  const rotos = quebrados || [];
  if (!records.length && !rotos.length) {
    return `<p class="expl pv-empty">${stats.registered
      ? 'Nenhum pivot atende aos filtros atuais. Os registros continuam gravados.'
      : 'Nenhum pivot registrado neste estudo ainda.'}</p>`;
  }
  const rows = records.map((r, index) => `
    <tr data-pv-row="${esc(r.id)}"${r.withinRule ? '' : ' class="pv-outside"'}>
      <td data-label="#">${index + 1}</td>
      <td data-label="TF">${esc(r.timeframe)}</td>
      <td data-label="Início">${esc(pvFmtDatetime(r.pivot.startDatetime))}<span class="pv-cell-sub">${esc(pvFmtPrice(pvMath().parseNumber(r.pivot.startPrice)))}</span></td>
      <td data-label="Fim">${esc(pvFmtDatetime(r.pivot.endDatetime))}<span class="pv-cell-sub">${esc(pvFmtPrice(pvMath().parseNumber(r.pivot.endPrice)))}</span></td>
      <td data-label="Direção">${pvDirectionLabel(r.direction)}</td>
      <td data-label="Amplitude"><b>${pvFmtPct(r.percentageRange)}</b><span class="pv-cell-sub">${esc(pvFmtPrice(r.absoluteRange))}</span></td>
      <td data-label="Duração">${esc(pvFmtDuration(r.durationMs))}</td>
      <td data-label="Correção">${pvFmtPct(r.maxCorrectionPct)}<span class="pv-cell-sub">${pvCriterionLabel(r)}</span></td>
      <td data-label="Ações" class="pv-row-actions">
        <button type="button" class="pv-mini" data-pv-edit="${esc(r.id)}">Editar</button>
        <button type="button" class="pv-mini pv-danger" data-pv-delete="${esc(r.id)}">Excluir</button>
      </td>
    </tr>`).join('');
  return `
    <div class="jp-table-scroll pv-tablewrap">
      <table class="dtable pv-table">
        <caption class="pv-caption">${records.length} de ${stats.registered} pivot(s) registrado(s) neste estudo${rotos.length ? ` · ${rotos.length} sem cálculo` : ''}</caption>
        <thead><tr>
          <th scope="col">#</th><th scope="col">TF</th><th scope="col">Início</th><th scope="col">Fim</th>
          <th scope="col">Direção</th><th scope="col">Amplitude</th><th scope="col">Duração</th>
          <th scope="col">Correção</th><th scope="col">Ações</th>
        </tr></thead>
        <tbody>${rows}${rotos.map((p, i) => pvBrokenRowHTML(p, math, records.length + i + 1)).join('')}</tbody>
      </table>
    </div>
    ${rotos.length ? `<p class="note pv-broken-note">${rotos.length} registro(s) não produz(em) cálculo e por isso ficam fora da amostra e de qualquer filtro — aparecem no fim da lista, com o motivo. Corrija ou exclua; nada foi apagado.</p>` : ''}`;
}

// ---- formulário do pivot -------------------------------------------------

function pvFieldHTML(field, label, input) {
  return `<div class="field">
    <label for="pv_${field}">${label}</label>
    ${input}
    <p class="pv-field-err" id="pvErr_${field}" role="alert"></p>
  </div>`;
}

function pvFormHTML() {
  const d = pvDraft;
  const timeframeOptions = pvMath().TIMEFRAMES.map(tf =>
    `<option value="${tf}"${d.timeframe === tf ? ' selected' : ''}>${tf}</option>`).join('');
  return `
    <fieldset class="pv-form">
      <legend>${pvEditingId ? 'Editar pivot' : 'Novo pivot'}</legend>
      <div class="pv-form-grid">
        ${pvFieldHTML('timeframe', 'Timeframe', `<select id="pv_timeframe" data-pv-field="timeframe" aria-describedby="pvErr_timeframe">${timeframeOptions}</select>`)}
        ${pvFieldHTML('startDatetime', 'Data/hora inicial', `<input type="datetime-local" step="1" id="pv_startDatetime" data-pv-field="startDatetime" value="${esc(d.startDatetime)}" aria-describedby="pvErr_startDatetime">`)}
        ${pvFieldHTML('startPrice', 'Preço inicial', `<input type="text" inputmode="decimal" id="pv_startPrice" data-pv-field="startPrice" value="${esc(d.startPrice)}" placeholder="ex.: 1,23412" aria-describedby="pvErr_startPrice">`)}
        ${pvFieldHTML('endDatetime', 'Data/hora final', `<input type="datetime-local" step="1" id="pv_endDatetime" data-pv-field="endDatetime" value="${esc(d.endDatetime)}" aria-describedby="pvErr_endDatetime">`)}
        ${pvFieldHTML('endPrice', 'Preço final', `<input type="text" inputmode="decimal" id="pv_endPrice" data-pv-field="endPrice" value="${esc(d.endPrice)}" placeholder="ex.: 1,31207" aria-describedby="pvErr_endPrice">`)}
        ${pvFieldHTML('maxCorrectionPct', 'Maior correção interna (%)', `<input type="text" inputmode="decimal" id="pv_maxCorrectionPct" data-pv-field="maxCorrectionPct" value="${esc(d.maxCorrectionPct)}" placeholder="ex.: 47,2" aria-describedby="pvErr_maxCorrectionPct">`)}
      </div>
      ${pvFieldHTML('notes', 'Observação (opcional)', `<input type="text" id="pv_notes" data-pv-field="notes" value="${esc(d.notes)}" maxlength="140">`)}
      <p class="note">A correção é a maior retração interna que <b>você</b> identificou no gráfico. O app não possui dados OHLC: ele registra o percentual informado e o compara com o limite de ${pvFmtPct(pvMath().MAX_CORRECTION_PCT)} — não verifica o histórico do mercado.</p>
      <div class="metrics pv-preview" id="pvPreview"></div>
      <div id="pvFormErr"></div>
      <div class="pv-actions">
        <button type="button" class="reset-btn" id="pvSavePivotBtn">${pvEditingId ? 'Salvar alterações' : 'Salvar pivot'}</button>
        <button type="button" class="reset-btn ghost" id="pvCancelPivotBtn">Cancelar</button>
      </div>
    </fieldset>`;
}

// Recalcula somente a prévia. Não reconstrói o formulário: um innerHTML a cada
// tecla destruiria foco e posição do cursor.
function pvUpdateDerived() {
  const box = document.getElementById('pvPreview');
  const math = pvMath();
  if (!box || !math || !pvDraft) return null;
  const derived = math.derive({
    startPrice: pvDraft.startPrice, endPrice: pvDraft.endPrice,
    startDatetime: pvDraft.startDatetime, endDatetime: pvDraft.endDatetime,
    maxCorrectionPct: pvDraft.maxCorrectionPct
  });
  const correction = math.parseNumber(pvDraft.maxCorrectionPct);
  // Veredito em uma palavra: o cartao de metrica trunca com reticencias, e
  // "Critério informado: ate…" nao informa nada. A ressalva de que o criterio e
  // INFORMADO, e nao verificado, vive no rotulo e na legenda abaixo.
  const criterion = correction === null ? '—'
    : (!math.correctionInDomain(correction) ? 'Fora de 0–100%'
      : (math.withinCorrectionRule(correction) ? 'Atendido' : 'Excedido'));
  box.innerHTML =
    pvMetric('Direção', derived ? pvDirectionLabel(derived.direction) : '—') +
    pvMetric('Amplitude', derived ? pvFmtPct(derived.percentageRange) : '—', derived ? esc(pvFmtPrice(derived.absoluteRange)) : '') +
    pvMetric('Duração', derived ? esc(pvFmtDuration(derived.durationMs)) : '—') +
    pvMetric('Critério informado', criterion, `limite ${pvFmtPct(math.MAX_CORRECTION_PCT)}`);
  return derived;
}

function pvShowErrors(errors) {
  PV_FIELDS.forEach(field => {
    const box = document.getElementById('pvErr_' + field);
    const messages = errors.filter(e => e.field === field).map(e => e.message);
    if (box) box.textContent = messages.join(' ');
    const input = document.getElementById('pv_' + field);
    if (!input) return;
    if (messages.length) input.setAttribute('aria-invalid', 'true');
    else input.removeAttribute('aria-invalid');
  });
  const summary = document.getElementById('pvFormErr');
  if (summary) {
    summary.innerHTML = errors.length
      ? `<div class="pv-err" role="alert">${errors.map(e => esc(e.message)).join('<br>')}</div>`
      : '';
  }
}

// ---- ações ---------------------------------------------------------------

function pvTouchStudy(study) {
  study.updatedAt = new Date().toISOString();
}

function pvCreateStudy() {
  const math = pvMath();
  const validation = math.validatePeriod(pvNewStudyDraft.periodStart, pvNewStudyDraft.periodEnd);
  const box = document.getElementById('pvNewStudyErr');
  if (!validation.ok) {
    if (box) box.textContent = validation.errors.map(e => e.message).join(' ');
    return;
  }
  const { periodStart, periodEnd } = validation.values;
  // Sobreposição AVISA e não proíbe: metodologias ou revisões diferentes sobre
  // o mesmo período são legítimas, e a decisão é do operador.
  const overlapping = pvStudiesFor(pvInstrumentId)
    .filter(st => math.periodsOverlap(st.periodStart, st.periodEnd, periodStart, periodEnd));
  if (overlapping.length && !confirm(`Já existe outro estudo deste instrumento com período parcialmente coincidente (${pvFmtDate(overlapping[0].periodStart)} → ${pvFmtDate(overlapping[0].periodEnd)}).\n\nCriar mesmo assim?`)) return;

  // Criar um estudo TROCA o estudo em foco, então segue a mesma guarda de
  // descarte de todos os outros caminhos de troca (instrumento, estudo, Novo
  // Estudo, Editar, Cancelar). Sem ela, o painel "Novo estudo" e o formulário de
  // pivot podiam estar abertos ao mesmo tempo e o rascunho completo do operador
  // era apagado sem uma palavra. O confirm vem ANTES de criar: cancelar deixa
  // tudo como estava, e o operador pode salvar o pivot primeiro.
  if (!pvConfirmDiscard()) return;
  const now = new Date().toISOString();
  const study = {
    id: pivotStudyId(), instrumentId: pvInstrumentId,
    periodStart, periodEnd, createdAt: now, updatedAt: now, pivots: []
  };
  if (!S.pivotStudies || typeof S.pivotStudies !== 'object') S.pivotStudies = structuredClone(DEFAULTS.pivotStudies);
  if (!Array.isArray(S.pivotStudies.studies)) S.pivotStudies.studies = [];
  S.pivotStudies.studies.push(study);
  save();

  pvStudyId = study.id;
  pvNewStudyOpen = false;
  pvNewStudyDraft = { periodStart: '', periodEnd: '' };
  pvCloseForm(); // invariante: trocar o estudo em foco fecha o formulário
  renderPivotStudies();
}

function pvDeleteStudy() {
  const study = pvStudyById(pvStudyId);
  if (!study) return;
  const count = study.pivots.length;
  if (!confirm(`Excluir o estudo ${pvFmtDate(study.periodStart)} → ${pvFmtDate(study.periodEnd)} de ${study.instrumentId}?\n\n${count} pivot(s) registrado(s) serão apagados junto. A ação é irreversível.`)) return;
  S.pivotStudies.studies = pvStudies().filter(st => st.id !== study.id);
  save();
  pvStudyId = null;
  pvCloseForm();
  renderPivotStudies();
}

function pvOpenForm(pivotId) {
  const study = pvStudyEmFoco('registrado');
  if (!study) return;
  if (pivotId) {
    const pivot = study.pivots.find(p => p.id === pivotId);
    if (!pivot) return;
    pvEditingId = pivotId;
    pvDraft = {
      timeframe: pivot.timeframe, startDatetime: pivot.startDatetime,
      startPrice: pivot.startPrice == null ? '' : String(pivot.startPrice),
      endDatetime: pivot.endDatetime,
      endPrice: pivot.endPrice == null ? '' : String(pivot.endPrice),
      maxCorrectionPct: pivot.maxCorrectionPct == null ? '' : String(pivot.maxCorrectionPct),
      notes: pivot.notes || ''
    };
  } else {
    pvEditingId = null;
    pvDraft = Object.assign({}, PV_EMPTY_DRAFT);
  }
  pvFormOpen = true; pvDirty = false;
  renderPivotStudies();
  const first = document.getElementById('pv_timeframe');
  if (first) first.focus();
}

function pvSavePivot() {
  const math = pvMath();
  if (!math) return;
  const study = pvStudyEmFoco('salvo');
  if (!study) return;
  const validation = math.validate(pvDraft);
  pvShowErrors(validation.errors || []);
  if (!validation.ok) return;

  // Persiste somente as CAUSAS, já normalizadas. Direção, range, amplitude,
  // duração e o veredito do critério são recalculados a cada leitura.
  const values = validation.values;
  const now = new Date().toISOString();
  if (pvEditingId) {
    const pivot = study.pivots.find(p => p.id === pvEditingId);
    // Alvo sumiu (excluído em outra aba, ou estado recarregado por baixo).
    // Falhar em silêncio faria o operador digitar, clicar em salvar e não
    // receber nada — nem o registro, nem uma explicação.
    if (!pivot) {
      pvShowErrors([{ field: 'timeframe', message: 'O pivot que estava sendo editado não existe mais neste estudo. Nada foi salvo — feche o formulário e registre novamente.' }]);
      return;
    }
    // Editar ATUALIZA o registro; nunca cria um segundo. Campos desconhecidos
    // que tenham vindo de backup atravessam intactos.
    Object.assign(pivot, values, { updatedAt: now });
  } else {
    study.pivots.push(Object.assign({ id: pivotRecordId() }, values, { createdAt: now, updatedAt: now }));
  }
  pvTouchStudy(study);
  save();
  pvCloseForm();
  renderPivotStudies();
}

function pvDeletePivot(pivotId) {
  const study = pvStudyEmFoco('excluído');
  if (!study) return;
  const pivot = study.pivots.find(p => p.id === pivotId);
  if (!pivot) return;
  if (!confirm(`Excluir este pivot ${pivot.timeframe} (${pvFmtDatetime(pivot.startDatetime)} → ${pvFmtDatetime(pivot.endDatetime)})?\n\nA ação é irreversível.`)) return;
  study.pivots = study.pivots.filter(p => p.id !== pivotId);
  pvTouchStudy(study);
  save();
  if (pvEditingId === pivotId) pvCloseForm();
  renderPivotStudies();
}

// Localizar o registro a partir do ranking. Se os filtros vigentes escondem o
// alvo, eles são afrouxados — o clique perderia o sentido se não levasse a
// lugar nenhum. Nenhum dado muda: filtro é visualização.
function pvGoToPivot(pivotId) {
  const study = pvStudyById(pvStudyId);
  if (!study) return;
  const pivot = study.pivots.find(p => p.id === pivotId);
  if (!pivot) return;
  if (pvFilters.timeframe !== 'all' && pvFilters.timeframe !== pivot.timeframe) pvFilters.timeframe = 'all';
  pvFilters.direction = 'all';
  pvHighlightId = pivotId;
  renderPivotStudies();
}

function pvApplyHighlight() {
  const row = document.querySelector(`[data-pv-row="${pvHighlightId}"]`);
  pvHighlightId = null;
  if (!row) return;
  row.classList.add('pv-highlight');
  if (typeof row.scrollIntoView === 'function') row.scrollIntoView({ block: 'center' });
  setTimeout(() => row.classList.remove('pv-highlight'), 2200);
}

// ---- bind ----------------------------------------------------------------

function pvBind(root) {
  const instrument = root.querySelector('#pvInstrument');
  if (instrument) instrument.addEventListener('change', () => {
    if (!pvConfirmDiscard()) { instrument.value = pvInstrumentId; return; }
    pvInstrumentId = instrument.value; pvStudyId = null; pvNewStudyOpen = false;
    renderPivotStudies();
  });

  const studySelect = root.querySelector('#pvStudy');
  if (studySelect) studySelect.addEventListener('change', () => {
    if (!pvConfirmDiscard()) { studySelect.value = pvStudyId; return; }
    pvStudyId = studySelect.value;
    renderPivotStudies();
  });

  const newStudy = root.querySelector('#pvNewStudyBtn');
  if (newStudy) newStudy.addEventListener('click', () => {
    if (!pvConfirmDiscard()) return;
    pvNewStudyOpen = true; renderPivotStudies();
    const field = document.getElementById('pvPeriodStart');
    if (field) field.focus();
  });

  const deleteStudy = root.querySelector('#pvDeleteStudyBtn');
  if (deleteStudy) deleteStudy.addEventListener('click', pvDeleteStudy);

  ['periodStart', 'periodEnd'].forEach(key => {
    const input = root.querySelector('#pv' + key.charAt(0).toUpperCase() + key.slice(1));
    if (input) input.addEventListener('input', () => { pvNewStudyDraft[key] = input.value; });
  });
  const create = root.querySelector('#pvCreateStudyBtn');
  if (create) create.addEventListener('click', pvCreateStudy);
  const cancelStudy = root.querySelector('#pvCancelStudyBtn');
  if (cancelStudy) cancelStudy.addEventListener('click', () => {
    pvNewStudyOpen = false; pvNewStudyDraft = { periodStart: '', periodEnd: '' }; renderPivotStudies();
  });

  root.querySelectorAll('[data-pv-filter]').forEach(button => {
    button.addEventListener('click', () => {
      pvFilters[button.dataset.pvFilter] = button.dataset.pvValue;
      renderPivotStudies();
    });
  });
  const sort = root.querySelector('#pvSort');
  if (sort) sort.addEventListener('change', () => {
    const [key, direction] = sort.value.split(':');
    pvSort = { key, ascending: direction === 'asc' };
    renderPivotStudies();
  });

  const add = root.querySelector('#pvAddPivotBtn');
  if (add) add.addEventListener('click', () => pvOpenForm(null));
  root.querySelectorAll('[data-pv-edit]').forEach(button =>
    button.addEventListener('click', () => { if (pvConfirmDiscard()) pvOpenForm(button.dataset.pvEdit); }));
  root.querySelectorAll('[data-pv-delete]').forEach(button =>
    button.addEventListener('click', () => pvDeletePivot(button.dataset.pvDelete)));
  root.querySelectorAll('[data-pv-goto]').forEach(button =>
    button.addEventListener('click', () => pvGoToPivot(button.dataset.pvGoto)));

  root.querySelectorAll('[data-pv-field]').forEach(input => {
    input.addEventListener('input', () => {
      pvDraft[input.dataset.pvField] = input.value;
      pvDirty = true;
      // Calcular não é salvar: a prévia acompanha cada tecla, mas nada é
      // persistido antes da ação explícita de salvar.
      pvUpdateDerived();
    });
  });
  const savePivot = root.querySelector('#pvSavePivotBtn');
  if (savePivot) savePivot.addEventListener('click', pvSavePivot);
  const cancelPivot = root.querySelector('#pvCancelPivotBtn');
  if (cancelPivot) cancelPivot.addEventListener('click', () => {
    if (!pvConfirmDiscard()) return;
    pvCloseForm(); renderPivotStudies();
  });
}

// Superfície pública consumida pelo controlador de views do Execution Board.
window.JPWPivotsUI = { render: renderPivotStudies };
