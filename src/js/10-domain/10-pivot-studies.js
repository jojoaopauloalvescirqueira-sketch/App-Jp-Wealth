// ============ ESTUDOS DOS PIVOTS · NUCLEO (N1 — dominio puro) ============
// Matematica e estatistica descritiva dos pivots registrados manualmente pelo
// operador. Deliberadamente puro: recebe numeros e strings, devolve numeros, e
// nao toca DOM, localStorage, S, rede ou qualquer modulo tardio.
//
// PRINCIPIO DE SEGURANCA OPERACIONAL: nada aqui autoriza operacao. O estudo e
// memoria tecnica retrospectiva — nenhuma funcao deste arquivo altera risco,
// fase, clearance, alavancagem, ordem, lote ou estado estatutario.
//
// PRINCIPIO ESTATISTICO: a amostra e SELECIONADA pelo operador, que registra
// deliberadamente os maiores pivots que encontrou. Por isso tudo aqui e
// descritivo da amostra e nada e inferencial: nao existe probabilidade,
// frequencia esperada, alvo, projecao ou "proximo pivot". Somar essas coisas
// aqui seria transformar viés de selecao em previsao.

const PIVOT_TIMEFRAMES = ['H1', 'H4'];

// CRITERIO DE CORRECAO NoCoda. Fonte normativa: especificacao do gestor para
// esta feature (secao 17), que fixa 61,8 como limite INVALIDANTE — a correcao
// precisa ser estritamente menor para o pivot entrar na amostra principal.
// Declarado uma unica vez: nenhum outro arquivo repete o numero.
const PIVOT_MAX_CORRECTION_PCT = 61.8;

// Limites da correcao informada. A retracao e uma fracao da propria perna: 0%
// significa movimento sem retracao interna e 100% significa que o preco voltou
// ao ponto de partida — alem disso o registro deixa de descrever este pivot.
const PIVOT_CORRECTION_MIN = 0;
const PIVOT_CORRECTION_MAX = 100;

const PIVOT_MS_HOUR = 3600000;
const PIVOT_MS_DAY = 86400000;

// Data sem hora, usada no periodo do estudo (AAAA-MM-DD).
const PIVOT_DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;

// ---- entrada -------------------------------------------------------------

// Carimbo de data/hora do pivot. Reusa a convencao temporal ja estabelecida
// pelos Estudos NoCoda (10-domain/09-nocoda-geometry.js) em vez de duplicar o
// parser: os dois recebem o MESMO carimbo sem fuso vindo do MetaTrader, e uma
// segunda implementacao seria uma segunda verdade sobre o mesmo dado. A leitura
// como UTC nao converte fuso nenhum — torna a aritmetica deterministica para
// que o mesmo estudo produza a mesma duracao em qualquer maquina.
function pivotParseTime(value) {
  return (typeof nocodaParseTime === 'function') ? nocodaParseTime(value) : null;
}

// Data do periodo. Devolve a string canonica AAAA-MM-DD ou null.
function pivotParseDate(value) {
  const match = PIVOT_DATE_RE.exec(String(value == null ? '' : value).trim());
  if (!match) return null;
  const year = +match[1], month = +match[2], day = +match[3];
  if (month < 1 || month > 12 || day < 1 || day > 31) return null;
  const ms = Date.UTC(year, month - 1, day);
  const back = new Date(ms);
  // Date.UTC transborda 31/02 para 03/03 em silencio.
  if (back.getUTCFullYear() !== year || back.getUTCMonth() !== month - 1 || back.getUTCDate() !== day) return null;
  return match[1] + '-' + match[2] + '-' + match[3];
}

// Numero digitado. Aceita virgula decimal, como o resto do app. String vazia,
// texto, NaN e Infinity devolvem null — nunca 0, que e valor observado.
function pivotParseNumber(raw) {
  if (typeof raw === 'number') return Number.isFinite(raw) ? raw : null;
  const text = String(raw == null ? '' : raw).trim().replace(',', '.');
  if (text === '') return null;
  const value = Number(text);
  return Number.isFinite(value) ? value : null;
}

function pivotIsValidPrice(value) {
  return typeof value === 'number' && Number.isFinite(value) && value > 0;
}

function pivotIsValidTimeframe(value) {
  return PIVOT_TIMEFRAMES.indexOf(String(value == null ? '' : value).toUpperCase()) >= 0;
}

// ---- derivados -----------------------------------------------------------
// Nada abaixo e persistido: o estudo guarda as CAUSAS (timeframe, extremos de
// tempo e preco, correcao informada) e as consequencias sao recalculadas.

// Direcao DERIVADA, nunca digitada. Precos iguais nao descrevem pivot
// direcional — devolve null, e a camada de gravacao recusa o registro.
function pivotDirection(startPrice, endPrice) {
  if (!pivotIsValidPrice(startPrice) || !pivotIsValidPrice(endPrice)) return null;
  if (endPrice > startPrice) return 'bullish';
  if (endPrice < startPrice) return 'bearish';
  return null;
}

function pivotAbsoluteRange(startPrice, endPrice) {
  if (!pivotIsValidPrice(startPrice) || !pivotIsValidPrice(endPrice)) return null;
  return Math.abs(endPrice - startPrice);
}

// Amplitude percentual — a medida principal de magnitude entre pivots.
// M = |Pf - Pi| / Pi * 100. Sem arredondamento: quem arredonda e a apresentacao.
function pivotPercentageRange(startPrice, endPrice) {
  if (!pivotIsValidPrice(startPrice) || !pivotIsValidPrice(endPrice)) return null;
  return Math.abs(endPrice - startPrice) / startPrice * 100;
}

// Duracao em milissegundos. Exige fim ESTRITAMENTE posterior ao inicio.
function pivotDurationMs(startDatetime, endDatetime) {
  const start = pivotParseTime(startDatetime);
  const end = pivotParseTime(endDatetime);
  if (start === null || end === null || !(end > start)) return null;
  return end - start;
}

// "20d 8h", "18h", "18h 30min", "45min". Apresentacao apenas — a duracao
// comparada e ordenada e sempre o numero em milissegundos.
function pivotFormatDuration(ms) {
  if (typeof ms !== 'number' || !Number.isFinite(ms) || ms < 0) return '—';
  const days = Math.floor(ms / PIVOT_MS_DAY);
  const hours = Math.floor((ms % PIVOT_MS_DAY) / PIVOT_MS_HOUR);
  const minutes = Math.floor((ms % PIVOT_MS_HOUR) / 60000);
  if (days > 0) return hours > 0 ? days + 'd ' + hours + 'h' : days + 'd';
  if (hours > 0) return minutes > 0 ? hours + 'h ' + minutes + 'min' : hours + 'h';
  return minutes + 'min';
}

// DOMINIO da correcao, antes do criterio. A retracao e fracao da propria perna:
// fora de 0–100 o numero nao descreve este movimento, e nao ha veredito de
// criterio a dar sobre ele.
//
// A checagem vive AQUI, e nao apenas no formulario, porque o formulario nao e o
// unico caminho de entrada: um backup importado atravessa
// pivotStudiesNormalizeState(), que de proposito sanea so a FORMA e nao apaga
// registro do operador. Sem esta guarda, um arquivo com correcao negativa
// passaria no teste unilateral `< 61,8`, entraria na amostra PRINCIPAL como
// "atende ao criterio" e envenenaria a mediana das correcoes.
function pivotCorrectionInDomain(value) {
  return typeof value === 'number' && Number.isFinite(value)
    && value >= PIVOT_CORRECTION_MIN && value <= PIVOT_CORRECTION_MAX;
}

// CRITERIO INFORMADO, nao verificado. O app nao possui dados OHLC: ele registra
// o percentual que o operador identificou e o compara com o limite. Nenhuma
// funcao daqui afirma ter conferido o historico do grafico.
function pivotWithinCorrectionRule(maxCorrectionPct) {
  return pivotCorrectionInDomain(maxCorrectionPct)
    && maxCorrectionPct < PIVOT_MAX_CORRECTION_PCT;
}

// Todos os derivados de um pivot persistido. Devolve null quando o registro nao
// descreve um pivot calculavel — a estatistica simplesmente o ignora, e nenhum
// dado e apagado por isso.
function pivotDerive(pivot) {
  if (!pivot || typeof pivot !== 'object') return null;
  const startPrice = pivotParseNumber(pivot.startPrice);
  const endPrice = pivotParseNumber(pivot.endPrice);
  const direction = pivotDirection(startPrice, endPrice);
  const durationMs = pivotDurationMs(pivot.startDatetime, pivot.endDatetime);
  if (direction === null || durationMs === null) return null;
  const correction = pivotParseNumber(pivot.maxCorrectionPct);
  return {
    direction,
    absoluteRange: pivotAbsoluteRange(startPrice, endPrice),
    percentageRange: pivotPercentageRange(startPrice, endPrice),
    durationMs,
    maxCorrectionPct: correction,
    // Distinguir "excede o criterio" de "valor fora do dominio" e o que permite
    // a interface dizer a verdade sobre cada registro sem apagar nenhum.
    correctionInDomain: pivotCorrectionInDomain(correction),
    withinRule: pivotWithinCorrectionRule(correction)
  };
}

// ---- validacao -----------------------------------------------------------
// Erros por CAMPO, para a interface poder apontar onde esta o problema.

function pivotValidate(input) {
  const errors = [];
  const source = input && typeof input === 'object' ? input : {};

  const timeframe = String(source.timeframe == null ? '' : source.timeframe).toUpperCase();
  if (!pivotIsValidTimeframe(timeframe)) {
    errors.push({ field: 'timeframe', message: 'Timeframe precisa ser H1 ou H4.' });
  }

  const start = pivotParseTime(source.startDatetime);
  if (start === null) errors.push({ field: 'startDatetime', message: 'Data/hora inicial é inválida.' });
  const end = pivotParseTime(source.endDatetime);
  if (end === null) errors.push({ field: 'endDatetime', message: 'Data/hora final é inválida.' });
  if (start !== null && end !== null && !(end > start)) {
    errors.push({
      field: 'endDatetime',
      message: start === end
        ? 'Início e fim não podem ser o mesmo instante.'
        : 'A data/hora final precisa ser posterior à inicial.'
    });
  }

  const startPrice = pivotParseNumber(source.startPrice);
  if (!pivotIsValidPrice(startPrice)) {
    errors.push({ field: 'startPrice', message: 'Preço inicial precisa ser um número finito e positivo.' });
  }
  const endPrice = pivotParseNumber(source.endPrice);
  if (!pivotIsValidPrice(endPrice)) {
    errors.push({ field: 'endPrice', message: 'Preço final precisa ser um número finito e positivo.' });
  }
  // Preco igual nos dois extremos nao e pivot direcional (secao 13): o registro
  // e recusado, e nao salvo como "neutro".
  if (pivotIsValidPrice(startPrice) && pivotIsValidPrice(endPrice) && startPrice === endPrice) {
    errors.push({ field: 'endPrice', message: 'Preço final igual ao inicial não descreve um pivot direcional.' });
  }

  const correction = pivotParseNumber(source.maxCorrectionPct);
  if (correction === null) {
    errors.push({ field: 'maxCorrectionPct', message: 'Informe a maior correção interna observada, em percentual.' });
  } else if (!pivotCorrectionInDomain(correction)) {
    // Mesma regra de dominio usada pela classificacao — uma fonte, dois usos.
    // Nao e o criterio de 61,8: este limite recusa entrada impossivel, e 61,8
    // classifica entrada valida.
    errors.push({ field: 'maxCorrectionPct', message: 'A correção precisa estar entre 0% e 100%.' });
  }

  if (errors.length) return { ok: false, errors, values: null };
  return {
    ok: true,
    errors: [],
    values: {
      timeframe,
      startDatetime: String(source.startDatetime),
      startPrice,
      endDatetime: String(source.endDatetime),
      endPrice,
      maxCorrectionPct: correction,
      notes: String(source.notes == null ? '' : source.notes).trim()
    }
  };
}

function pivotStudyValidatePeriod(periodStart, periodEnd) {
  const errors = [];
  const start = pivotParseDate(periodStart);
  if (start === null) errors.push({ field: 'periodStart', message: 'Data inicial do período é inválida.' });
  const end = pivotParseDate(periodEnd);
  if (end === null) errors.push({ field: 'periodEnd', message: 'Data final do período é inválida.' });
  // Periodo de um unico dia e legitimo, por isso <= e nao <.
  if (start !== null && end !== null && start > end) {
    errors.push({ field: 'periodEnd', message: 'A data final do período não pode ser anterior à inicial.' });
  }
  if (errors.length) return { ok: false, errors, values: null };
  return { ok: true, errors: [], values: { periodStart: start, periodEnd: end } };
}

// Sobreposicao de janelas fechadas nos dois extremos. NAO proibe nada: existe
// para a interface poder AVISAR antes de criar um estudo concorrente, porque
// metodologias e revisoes diferentes sobre o mesmo periodo sao legitimas.
function pivotStudyPeriodsOverlap(aStart, aEnd, bStart, bEnd) {
  const a1 = pivotParseDate(aStart), a2 = pivotParseDate(aEnd);
  const b1 = pivotParseDate(bStart), b2 = pivotParseDate(bEnd);
  if (a1 === null || a2 === null || b1 === null || b2 === null) return false;
  return a1 <= b2 && b1 <= a2;
}

// ---- estatistica descritiva ----------------------------------------------

// Mediana correta: ordenacao NUMERICA, media dos dois centrais quando n e par.
// Amostra vazia devolve null — ausencia de observacao nao e zero observado.
function pivotMedian(values) {
  const list = (Array.isArray(values) ? values : []).filter(v => typeof v === 'number' && Number.isFinite(v));
  if (!list.length) return null;
  const sorted = list.slice().sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function pivotMean(values) {
  const list = (Array.isArray(values) ? values : []).filter(v => typeof v === 'number' && Number.isFinite(v));
  if (!list.length) return null;
  return list.reduce((sum, v) => sum + v, 0) / list.length;
}

function pivotMax(records) {
  let best = null;
  (records || []).forEach(r => {
    if (best === null || r.percentageRange > best.percentageRange) best = r;
  });
  return best;
}

// Records enriquecidos: o pivot persistido + seus derivados + o indice de
// origem, para a interface conseguir voltar ao registro a partir do ranking.
function pivotRecords(pivots) {
  const list = Array.isArray(pivots) ? pivots : [];
  const out = [];
  list.forEach((pivot, index) => {
    const derived = pivotDerive(pivot);
    if (!derived) return;
    out.push(Object.assign({ id: pivot.id, timeframe: String(pivot.timeframe || '').toUpperCase(), pivot, index }, derived));
  });
  return out;
}

function pivotTop(records, count) {
  return records.slice().sort((a, b) => b.percentageRange - a.percentageRange).slice(0, count);
}

// Sintese de um timeframe. Cada campo e null quando a amostra nao o sustenta —
// nunca 0, que seria observacao. `n` acompanha SEMPRE as medidas centrais.
function pivotTimeframeSummary(records) {
  const amplitudes = records.map(r => r.percentageRange);
  const durations = records.map(r => r.durationMs);
  const best = pivotMax(records);
  return {
    n: records.length,
    max: best ? best.percentageRange : null,
    maxPivotId: best ? best.id : null,
    mean: pivotMean(amplitudes),
    median: pivotMedian(amplitudes),
    medianDurationMs: pivotMedian(durations)
  };
}

// Estatistica descritiva do estudo.
//
// Por padrao SO os pivots dentro do criterio compoem a amostra principal: os
// que excedem 61,8% continuam gravados e contados a parte, nunca misturados em
// silencio. {includeOutside:true} — ou {scope:'all'} — inclui todos, quando o
// filtro pedir todos; {scope:'outside'} descreve somente os excedentes, para
// auditoria. A amostra descrita e SEMPRE a mesma que a lista exibe: numero de
// resumo divergente da tabela ao lado seria informacao errada.
const PIVOT_SCOPES = ['valid', 'all', 'outside'];
function pivotStudyStats(pivots, options) {
  const requested = options && typeof options.scope === 'string' ? options.scope : null;
  const scope = PIVOT_SCOPES.indexOf(requested) >= 0 ? requested
    : ((options && options.includeOutside) ? 'all' : 'valid');
  const all = pivotRecords(pivots);
  const sample = scope === 'all' ? all
    : all.filter(r => scope === 'outside' ? !r.withinRule : r.withinRule);
  const byTimeframe = {};
  PIVOT_TIMEFRAMES.forEach(tf => { byTimeframe[tf] = sample.filter(r => r.timeframe === tf); });

  const amplitudes = sample.map(r => r.percentageRange);
  const best = pivotMax(sample);
  const timeframes = {};
  PIVOT_TIMEFRAMES.forEach(tf => {
    timeframes[tf] = Object.assign(pivotTimeframeSummary(byTimeframe[tf]), { top: pivotTop(byTimeframe[tf], 3) });
  });

  return {
    // Total registrado x amostra considerada: a diferenca e o que o criterio
    // deixou de fora, e precisa ficar visivel.
    registered: (Array.isArray(pivots) ? pivots : []).length,
    computable: all.length,
    outside: all.filter(r => !r.withinRule).length,
    scope,
    includeOutside: scope === 'all',
    n: sample.length,
    max: best ? best.percentageRange : null,
    maxTimeframe: best ? best.timeframe : null,
    maxPivotId: best ? best.id : null,
    mean: pivotMean(amplitudes),
    median: pivotMedian(amplitudes),
    medianDurationMs: pivotMedian(sample.map(r => r.durationMs)),
    // Nome deliberadamente preciso: mediana das correcoes MAXIMAS INFORMADAS
    // nos pivots registrados — nao "correcao media do mercado". Só entram
    // valores dentro do dominio: uma mediana calculada sobre -500 nao seria
    // uma correcao, e o registro continua gravado e visivel de todo modo.
    medianCorrection: pivotMedian(sample.filter(r => r.correctionInDomain).map(r => r.maxCorrectionPct)),
    outOfDomain: all.filter(r => !r.correctionInDomain).length,
    bullish: sample.filter(r => r.direction === 'bullish').length,
    bearish: sample.filter(r => r.direction === 'bearish').length,
    timeframes
  };
}

// ---- ordenacao -----------------------------------------------------------
// Comparacao SEMPRE numerica. Ordenar amplitude como texto poria 10% antes de
// 9%; o mesmo vale para data, duracao e correcao.

const PIVOT_SORT_KEYS = ['amplitude', 'date', 'duration', 'correction'];

function pivotSortValue(record, key) {
  if (key === 'amplitude') return record.percentageRange;
  if (key === 'duration') return record.durationMs;
  if (key === 'correction') return typeof record.maxCorrectionPct === 'number' ? record.maxCorrectionPct : -Infinity;
  return pivotParseTime(record.pivot.startDatetime); // 'date'
}

// Padrao do estudo: maior amplitude primeiro — e exatamente o que a feature
// existe para responder. Desempate estavel pelo instante inicial.
function pivotSortRecords(records, key, ascending) {
  const sortKey = PIVOT_SORT_KEYS.indexOf(key) >= 0 ? key : 'amplitude';
  const factor = ascending ? 1 : -1;
  return records.slice().sort((a, b) => {
    const va = pivotSortValue(a, sortKey), vb = pivotSortValue(b, sortKey);
    if (va !== vb) return (va < vb ? -1 : 1) * factor;
    const ta = pivotParseTime(a.pivot.startDatetime), tb = pivotParseTime(b.pivot.startDatetime);
    return (ta === tb ? 0 : (ta < tb ? -1 : 1));
  });
}

// Superficie publica do dominio. Somente matematica — sem estado, sem UI.
window.JPWPivots = {
  math: {
    parseTime: pivotParseTime,
    parseDate: pivotParseDate,
    parseNumber: pivotParseNumber,
    isValidPrice: pivotIsValidPrice,
    isValidTimeframe: pivotIsValidTimeframe,
    direction: pivotDirection,
    absoluteRange: pivotAbsoluteRange,
    percentageRange: pivotPercentageRange,
    durationMs: pivotDurationMs,
    formatDuration: pivotFormatDuration,
    correctionInDomain: pivotCorrectionInDomain,
    withinCorrectionRule: pivotWithinCorrectionRule,
    derive: pivotDerive,
    validate: pivotValidate,
    validatePeriod: pivotStudyValidatePeriod,
    periodsOverlap: pivotStudyPeriodsOverlap,
    median: pivotMedian,
    mean: pivotMean,
    records: pivotRecords,
    stats: pivotStudyStats,
    sort: pivotSortRecords,
    TIMEFRAMES: PIVOT_TIMEFRAMES,
    MAX_CORRECTION_PCT: PIVOT_MAX_CORRECTION_PCT,
    CORRECTION_MIN: PIVOT_CORRECTION_MIN,
    CORRECTION_MAX: PIVOT_CORRECTION_MAX,
    SORT_KEYS: PIVOT_SORT_KEYS,
    SCOPES: PIVOT_SCOPES
  }
};
