// ============ NOCODA · GEOMETRIA DO CANAL (N1 — dominio puro) ============
// Nucleo matematico do metodo NoCoda. E deliberadamente puro: recebe numeros e
// strings, devolve numeros, e nao toca DOM, localStorage, S, rede ou qualquer
// modulo tardio. Isso o torna testavel isoladamente e reutilizavel.
//
// PRINCIPIO DE SEGURANCA OPERACIONAL: nada aqui autoriza operacao. O estudo e
// memoria tecnica — nenhuma funcao deste arquivo altera risco, fase, clearance,
// alavancagem, ordem ou estado estatutario, e nenhum valor derivado daqui pode
// ser lido como permissao para operar.
//
// GEOMETRIA. As ancoras 1 e 2 definem a linha de nivel 0; a ancora 3 pertence a
// linha paralela de nivel -1. A linha 0 e linear no tempo:
//
//   P0(t) = P1 + (P2 - P1) * (t - T1) / (T2 - T1)
//
// O range do canal e medido na MESMA coordenada temporal — projetando a linha 0
// ate T3 — e nunca por abs(P3-P1) ou abs(P3-P2), que ignoram a inclinacao.

const NOCODA_STEP = 0.125;          // passo entre linhas consecutivas
const NOCODA_SUBDIVISIONS = 8;      // 1 / 0,125 — intervalos entre -1 e 0
const NOCODA_LEVEL_MIN = -4;
const NOCODA_LEVEL_MAX = 4;
// 64 intervalos entre -4 e +4, portanto 65 linhas contando as duas pontas.
const NOCODA_LEVEL_COUNT = (NOCODA_LEVEL_MAX - NOCODA_LEVEL_MIN) * NOCODA_SUBDIVISIONS + 1;

// Aceita 'AAAA-MM-DDTHH:MM:SS' e 'AAAA-MM-DD HH:MM:SS'; os segundos sao
// opcionais na entrada porque alguns navegadores omitem quando valem zero.
const NOCODA_TIME_RE = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?$/;

// Converte o carimbo digitado em milissegundos.
//
// Os componentes sao interpretados como UTC de proposito. O horario vem do
// MetaTrader e e um carimbo SEM fuso; se fosse lido como hora local, duas
// ancoras em lados opostos de uma virada de horario de verao produziriam uma
// diferenca de tempo distinta conforme o fuso de quem abre o app — e o mesmo
// estudo daria ranges diferentes em maquinas diferentes. Lendo como UTC a
// aritmetica fica deterministica em qualquer lugar, e a interface continua
// exibindo exatamente o que foi digitado. Nenhuma conversao de fuso ocorre.
function nocodaParseTime(value) {
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;
  const match = NOCODA_TIME_RE.exec(String(value == null ? '' : value).trim());
  if (!match) return null;
  const year = +match[1], month = +match[2], day = +match[3];
  const hour = +match[4], minute = +match[5], second = match[6] ? +match[6] : 0;
  if (month < 1 || month > 12 || day < 1 || day > 31) return null;
  if (hour > 23 || minute > 59 || second > 59) return null;
  const ms = Date.UTC(year, month - 1, day, hour, minute, second);
  if (!Number.isFinite(ms)) return null;
  // Rejeita data inexistente: Date.UTC transborda 31/02 para 03/03 em silencio.
  const back = new Date(ms);
  if (back.getUTCFullYear() !== year || back.getUTCMonth() !== month - 1 || back.getUTCDate() !== day) return null;
  return ms;
}

function nocodaIsValidPrice(value) {
  return typeof value === 'number' && Number.isFinite(value) && value > 0;
}

// Preco na linha de nivel 0 em qualquer instante t. Interpola e extrapola: t
// nao precisa estar entre T1 e T2.
function nocodaProjectBasePrice(t1, p1, t2, p2, t) {
  return p1 + (p2 - p1) * ((t - t1) / (t2 - t1));
}

// Nivel pelo indice inteiro k, k = 0..64. Usar indice em vez de acumular
// +0,125 num laco evita o erro binario que se soma a cada iteracao.
function nocodaLevelAt(k) {
  return NOCODA_LEVEL_MIN + k / NOCODA_SUBDIVISIONS;
}

// Valida as tres ancoras e devolve os valores ja normalizados em numeros.
// Erros sao por campo, para a interface poder apontar onde esta o problema.
function nocodaValidateAnchors(anchors) {
  const errors = [];
  const source = anchors && typeof anchors === 'object' ? anchors : {};
  const times = [];
  const prices = [];

  ['anchor1', 'anchor2', 'anchor3'].forEach((key, index) => {
    const anchor = source[key] && typeof source[key] === 'object' ? source[key] : {};
    const ms = nocodaParseTime(anchor.datetime);
    if (ms === null) {
      errors.push({ field: key + '.datetime', message: 'Data/hora da âncora ' + (index + 1) + ' é inválida.' });
    }
    times.push(ms);

    const raw = anchor.price;
    const price = typeof raw === 'number' ? raw : Number(String(raw == null ? '' : raw).trim().replace(',', '.'));
    if (!nocodaIsValidPrice(price)) {
      errors.push({ field: key + '.price', message: 'Valor da âncora ' + (index + 1) + ' precisa ser um número finito e positivo.' });
    }
    prices.push(nocodaIsValidPrice(price) ? price : null);
  });

  // T1 == T2 deixa a inclinacao da linha 0 indefinida (divisao por zero).
  // Nao ha restricao analoga para T3: interpolacao e extrapolacao sao ambas
  // legitimas, entao T3 pode estar antes, entre ou depois de T1 e T2.
  if (times[0] !== null && times[1] !== null && times[0] === times[1]) {
    errors.push({ field: 'anchor2.datetime', message: 'Âncoras 1 e 2 não podem ter a mesma data/hora — a inclinação da linha 0 ficaria indefinida.' });
  }

  if (errors.length) return { ok: false, errors, values: null };
  return {
    ok: true,
    errors: [],
    values: { t1: times[0], p1: prices[0], t2: times[1], p2: prices[1], t3: times[2], p3: prices[2] }
  };
}

// Resultado derivado do estudo. Nada disto e persistido: o estudo guarda as
// causas (as tres ancoras) e as consequencias sao recalculadas.
function nocodaGeometry(anchors) {
  const validation = nocodaValidateAnchors(anchors);
  if (!validation.ok) return null;
  const { t1, p1, t2, p2, t3, p3 } = validation.values;
  const basePriceAtThirdAnchor = nocodaProjectBasePrice(t1, p1, t2, p2, t3);
  const signedRange = p3 - basePriceAtThirdAnchor;
  const channelRange = Math.abs(signedRange);
  return {
    basePriceAtThirdAnchor,
    // O sinal diz de que lado da linha 0 esta a linha -1. Serve a geometria
    // completa do canal; a interface do MVP mostra so o modulo.
    signedRange,
    channelRange,
    subdivisionRange: channelRange / NOCODA_SUBDIVISIONS
  };
}

// Preco de qualquer nivel L no instante t: P(L,t) = P0(t) - L * signedRange.
// Em L=0 devolve a linha base; em L=-1, a linha que contem a terceira ancora.
// O MVP nao desenha as 65 linhas — esta funcao existe para o motor permanecer
// coerente e testavel quando isso for implementado.
function nocodaLevelPrice(level, t, anchors) {
  const validation = nocodaValidateAnchors(anchors);
  if (!validation.ok) return null;
  const { t1, p1, t2, p2, t3, p3 } = validation.values;
  const base = nocodaProjectBasePrice(t1, p1, t2, p2, t);
  const signedRange = p3 - nocodaProjectBasePrice(t1, p1, t2, p2, t3);
  return base - level * signedRange;
}

// Superficie publica do dominio. Somente matematica — sem estado, sem UI.
window.JPWNocoda = {
  geometry: {
    parseTime: nocodaParseTime,
    isValidPrice: nocodaIsValidPrice,
    projectBasePrice: nocodaProjectBasePrice,
    levelAt: nocodaLevelAt,
    levelPrice: nocodaLevelPrice,
    validate: nocodaValidateAnchors,
    compute: nocodaGeometry,
    STEP: NOCODA_STEP,
    SUBDIVISIONS: NOCODA_SUBDIVISIONS,
    LEVEL_MIN: NOCODA_LEVEL_MIN,
    LEVEL_MAX: NOCODA_LEVEL_MAX,
    LEVEL_COUNT: NOCODA_LEVEL_COUNT
  }
};
