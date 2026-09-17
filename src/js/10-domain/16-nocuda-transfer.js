// Nocuda Tool transfer v1. Pure drawing data; no DOM, storage, network or S.
// A/B define line 17 (level 1); C belongs to line 9 (level 0).
(function (root) {
  'use strict';

  const MAX_LENGTH = 16384;
  const MAX_TIME = 4102444800000; // 2100-01-01T00:00:00.000Z
  const IDENTIFIER = /^[A-Za-z0-9._:/+-]{1,64}$/;
  const DECIMAL = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/;
  const INTEGER = /^-?(?:0|[1-9][0-9]*)$/;
  const GROUPS = ['s1', 's3', 's5', 's9', 's17', 'si', 'sx'];
  const KEYS = ['v', 'geom', 'id', 'src', 'symbol', 'feed', 'tf', 'scale',
    'a', 'b', 'c', 'd', 'ab', 'ac', 'step', 'before', 'after', 'ext',
    ...GROUPS, 'labels'];
  const VALUE_KEYS = KEYS.filter(function (key) { return !GROUPS.includes(key); }).concat('styles');
  const STYLE_KEYS = ['on', 'r', 'g', 'b', 'alpha', 'width', 'style'];
  const LABEL_KEYS = ['mode', 'size', 'r', 'g', 'b', 'alpha', 'pos', 'vert',
    'gapPercent', 'offsetBars', 'showLevel', 'showPrice', 'showMax', 'useLineColor'];

  function fail(code, message, field) {
    const error = new Error(message);
    error.code = code;
    error.field = field || '';
    throw error;
  }

  function integer(raw, min, max, field) {
    if (typeof raw !== 'string' || !INTEGER.test(raw)) {
      fail('INTEGER', 'Use um número inteiro decimal no campo ' + field + '.', field);
    }
    const number = Number(raw);
    if (!Number.isSafeInteger(number) || number < min || number > max) {
      fail('RANGE', 'Valor fora do intervalo permitido em ' + field + '.', field);
    }
    return number === 0 ? 0 : number;
  }

  function decimal(raw, min, max, field) {
    if (typeof raw !== 'string' || !DECIMAL.test(raw)) {
      fail('DECIMAL', 'Use ponto decimal, sem expoente, no campo ' + field + '.', field);
    }
    const number = Number(raw);
    if (!Number.isFinite(number) || number < min || number > max) {
      fail('RANGE', 'Valor fora do intervalo permitido em ' + field + '.', field);
    }
    return number;
  }

  function choice(raw, choices, field) {
    if (!choices.includes(raw)) fail('ENUM', 'Opção não suportada em ' + field + '.', field);
    return raw;
  }

  function identifier(raw, field) {
    if (!IDENTIFIER.test(raw)) {
      fail('IDENTIFIER', 'Identificador inválido em ' + field + ': use 1 a 64 caracteres ASCII sem espaços.', field);
    }
    return raw;
  }

  function parts(raw, count, field) {
    const result = raw.split(',');
    if (result.length !== count) fail('ARITY', 'Quantidade incorreta de componentes em ' + field + '.', field);
    return result;
  }

  function anchor(raw, field) {
    const p = parts(raw, 3, field);
    decimal(p[1], -1e12, 1e12, field + '.price');
    return {
      time: integer(p[0], 0, MAX_TIME, field + '.time'),
      price: p[1], // Do not round or reformat source prices.
      offset: integer(p[2], -840, 840, field + '.offset')
    };
  }

  function style(raw, field) {
    const p = parts(raw, 7, field);
    return {
      on: integer(p[0], 0, 1, field + '.on'),
      r: integer(p[1], 0, 255, field + '.r'),
      g: integer(p[2], 0, 255, field + '.g'),
      b: integer(p[3], 0, 255, field + '.b'),
      alpha: integer(p[4], 0, 100, field + '.alpha'),
      width: integer(p[5], 1, 5, field + '.width'),
      style: choice(p[6], ['S', 'D', 'P'], field + '.style')
    };
  }

  function labels(raw) {
    const p = parts(raw, 14, 'labels');
    return {
      mode: choice(p[0], ['M', 'A', 'N'], 'labels.mode'),
      size: integer(p[1], 8, 24, 'labels.size'),
      r: integer(p[2], 0, 255, 'labels.r'),
      g: integer(p[3], 0, 255, 'labels.g'),
      b: integer(p[4], 0, 255, 'labels.b'),
      alpha: integer(p[5], 0, 100, 'labels.alpha'),
      pos: choice(p[6], ['L', 'C', 'R', 'T'], 'labels.pos'),
      vert: choice(p[7], ['U', 'O', 'D'], 'labels.vert'),
      gapPercent: decimal(p[8], 0, 50, 'labels.gapPercent'),
      offsetBars: integer(p[9], -100, 100, 'labels.offsetBars'),
      showLevel: integer(p[10], 0, 1, 'labels.showLevel'),
      showPrice: integer(p[11], 0, 1, 'labels.showPrice'),
      showMax: integer(p[12], 0, 1, 'labels.showMax'),
      useLineColor: integer(p[13], 0, 1, 'labels.useLineColor')
    };
  }

  function verifyBarOrder(value) {
    const a = value.a.time;
    if (Math.sign(value.b.time - a) !== Math.sign(value.ab)) {
      fail('BAR_ORDER', 'As datas de A/B não correspondem à ordem informada dos candles.', 'ab');
    }
    if (Math.sign(value.c.time - a) !== Math.sign(value.ac)) {
      fail('BAR_ORDER', 'A data de C não corresponde à posição informada do candle.', 'ac');
    }
    if (Math.sign(value.c.time - value.b.time) !== Math.sign(value.ac - value.ab)) {
      fail('BAR_ORDER', 'As datas de B/C não correspondem à ordem informada dos candles.', 'ac');
    }
  }

  function read(text) {
    if (typeof text !== 'string') fail('TYPE', 'O código do desenho precisa ser texto.', '');
    if (text.length > MAX_LENGTH) fail('SIZE', 'O código excede o limite de 16 KiB.', '');
    if (!text.length) fail('EMPTY', 'Cole o código de um desenho Nocuda Tool.', '');
    if (!/^[\x21-\x7e]+$/.test(text)) {
      fail('CHARACTER', 'O código deve ter uma única linha ASCII, sem espaços nem caracteres invisíveis.', '');
    }
    const tokens = text.split('|');
    if (tokens.shift() !== 'NOCUDA') fail('MAGIC', 'Cabeçalho NOCUDA ausente ou inválido.', '');
    const fields = Object.create(null);
    tokens.forEach(function (token) {
      const pair = token.split('=');
      if (pair.length !== 2 || !pair[1]) fail('FIELD', 'Campo ausente ou malformado no código.', '');
      const key = pair[0];
      if (!KEYS.includes(key)) fail('UNKNOWN_FIELD', 'O código contém um campo não suportado.', '');
      if (Object.prototype.hasOwnProperty.call(fields, key)) fail('DUPLICATE_FIELD', 'Campo repetido: ' + key + '.', key);
      fields[key] = pair[1];
    });
    KEYS.forEach(function (key) {
      if (!Object.prototype.hasOwnProperty.call(fields, key)) fail('MISSING_FIELD', 'Campo obrigatório ausente: ' + key + '.', key);
    });
    choice(fields.v, ['1'], 'v');
    choice(fields.geom, ['bars1'], 'geom');
    choice(fields.step, ['0.125'], 'step');
    decimal(fields.d, -1e12, 1e12, 'd');
    const value = {
      v: 1,
      geom: 'bars1',
      id: identifier(fields.id, 'id'),
      src: choice(fields.src, ['TV', 'MT5', 'JPW'], 'src'),
      symbol: identifier(fields.symbol, 'symbol'),
      feed: identifier(fields.feed, 'feed'),
      tf: integer(fields.tf, 1, 2592000, 'tf'),
      scale: choice(fields.scale, ['L'], 'scale'),
      a: anchor(fields.a, 'a'),
      b: anchor(fields.b, 'b'),
      c: anchor(fields.c, 'c'),
      d: fields.d,
      ab: integer(fields.ab, -4999, 4999, 'ab'),
      ac: integer(fields.ac, -4999, 4999, 'ac'),
      step: '0.125',
      before: integer(fields.before, 0, 160, 'before'),
      after: integer(fields.after, 0, 160, 'after'),
      ext: choice(fields.ext, ['R', 'L', 'B', 'N'], 'ext'),
      styles: {},
      labels: labels(fields.labels)
    };
    GROUPS.forEach(function (key) { value.styles[key] = style(fields[key], key); });
    if (value.ab === 0) fail('DEGENERATE', 'A e B precisam estar em candles distintos.', 'ab');
    const width = Number(value.d);
    if (Math.abs(width) <= 1e-12) fail('DEGENERATE', 'A largura do canal precisa ser diferente de zero.', 'd');
    verifyBarOrder(value);
    const measured = Number(value.a.price) + (Number(value.b.price) - Number(value.a.price)) * value.ac / value.ab - Number(value.c.price);
    if (Math.abs(measured - width) > Math.max(1e-10, Math.abs(width) * 1e-8)) {
      fail('WIDTH_MISMATCH', 'A largura não corresponde às três âncoras e às distâncias entre candles.', 'd');
    }
    return value;
  }

  function objectKeys(value, expected, field) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) fail('TYPE', 'Objeto inválido em ' + field + '.', field);
    const actual = Object.keys(value);
    if (actual.length !== expected.length || expected.some(function (key) { return !Object.prototype.hasOwnProperty.call(value, key); })) {
      fail('OBJECT_FIELDS', 'Campos incompletos ou desconhecidos em ' + field + '.', field);
    }
  }

  function decimalText(value) {
    // A numeric label gap may stringify as 1e-7; the transport never uses exponents.
    const raw = String(value);
    if (typeof value !== 'number' || !/[eE]/.test(raw) || !Number.isFinite(value)) return raw;
    const pair = raw.toLowerCase().split('e');
    const sign = pair[0][0] === '-' ? '-' : '';
    const mantissa = pair[0].replace('-', '');
    const digits = mantissa.replace('.', '');
    const decimalAt = (mantissa.indexOf('.') < 0 ? mantissa.length : mantissa.indexOf('.')) + Number(pair[1]);
    if (decimalAt <= 0) return sign + '0.' + '0'.repeat(-decimalAt) + digits;
    if (decimalAt >= digits.length) return sign + digits + '0'.repeat(decimalAt - digits.length);
    return sign + digits.slice(0, decimalAt) + '.' + digits.slice(decimalAt);
  }

  function wire(value) {
    objectKeys(value, VALUE_KEYS, 'drawing');
    objectKeys(value.styles, GROUPS, 'styles');
    objectKeys(value.labels, LABEL_KEYS, 'labels');
    ['a', 'b', 'c'].forEach(function (key) {
      objectKeys(value[key], ['time', 'price', 'offset'], key);
      if (typeof value[key].price !== 'string') fail('TYPE', 'Preserve o preço como texto decimal em ' + key + '.', key + '.price');
    });
    if (typeof value.d !== 'string') fail('TYPE', 'Preserve a largura como texto decimal.', 'd');
    GROUPS.forEach(function (key) { objectKeys(value.styles[key], STYLE_KEYS, key); });
    const fields = Object.create(null);
    KEYS.forEach(function (key) {
      if (key === 'a' || key === 'b' || key === 'c') {
        fields[key] = [value[key].time, value[key].price, value[key].offset].join(',');
      } else if (GROUPS.includes(key)) {
        fields[key] = STYLE_KEYS.map(function (part) { return value.styles[key][part]; }).join(',');
      } else if (key === 'labels') {
        fields[key] = LABEL_KEYS.map(function (part) {
          return part === 'gapPercent' ? decimalText(value.labels[part]) : value.labels[part];
        }).join(',');
      } else {
        fields[key] = value[key];
      }
    });
    return 'NOCUDA|' + KEYS.map(function (key) { return key + '=' + fields[key]; }).join('|');
  }

  function serialize(value) {
    // Revalidate complete values; callers cannot accidentally export a partial edit.
    return wire(read(wire(value)));
  }

  function parse(text) {
    try {
      const value = read(text);
      return { ok: true, value: value, canonical: wire(value) };
    } catch (error) {
      return { ok: false, error: {
        code: error.code || 'INVALID',
        message: error.code ? error.message : 'Não foi possível interpretar o código do desenho.',
        field: error.field || ''
      } };
    }
  }

  function example() {
    return 'NOCUDA|v=1|geom=bars1|id=SYNTH-DEMO|src=JPW|symbol=SYNTH|feed=SYNTH|tf=3600|scale=L' +
      '|a=1767600000000,100.00000,0|b=1767614400000,104.00000,0|c=1767607200000,92.00000,0' +
      '|d=10.00000|ab=4|ac=2|step=0.125|before=8|after=24|ext=R' +
      '|s1=1,239,83,80,0,2,S|s3=1,239,83,80,10,1,D|s5=1,239,83,80,10,1,D' +
      '|s9=1,239,83,80,0,2,S|s17=1,239,83,80,0,2,S|si=1,239,83,80,65,1,P' +
      '|sx=1,239,83,80,75,1,P|labels=M,12,239,83,80,0,R,O,1,2,0,0,1,1';
  }

  function geometry(drawing) {
    const v = read(serialize(drawing));
    const slope = (Number(v.b.price) - Number(v.a.price)) / v.ab;
    const width = Number(v.d);
    const minBar = Math.min(0, v.ab, v.ac);
    const maxBar = Math.max(0, v.ab, v.ac);
    const lines = [];
    for (let ordinal = 1 - v.before; ordinal <= 17 + v.after; ordinal += 1) {
      const level = (ordinal - 9) / 8;
      const group = GROUPS.includes('s' + ordinal) ? 's' + ordinal : (ordinal < 1 || ordinal > 17 ? 'sx' : 'si');
      const marked = [1, 3, 5, 9, 17].includes(ordinal);
      const styleValue = v.styles[group];
      const labelOn = !!styleValue.on && v.labels.mode !== 'N' &&
        (v.labels.mode === 'A' || marked || (ordinal === 41 && !!v.labels.showMax));
      const base = Number(v.a.price) + (level - 1) * width;
      const isMax = ordinal === 41 && !!v.labels.showMax;
      lines.push({
        ordinal: ordinal, level: level, group: group, visible: !!styleValue.on,
        style: Object.assign({}, styleValue),
        label: labelOn ? (isMax ? 'MAX' : String(ordinal)) : '',
        fromPrice: base + slope * minBar, toPrice: base + slope * maxBar,
        atC: base + slope * v.ac
      });
    }
    return {
      slope: slope, width: width, minOrdinal: 1 - v.before, maxOrdinal: 17 + v.after,
      minBar: minBar, maxBar: maxBar,
      anchors: { a: { bar: 0, price: Number(v.a.price) }, b: { bar: v.ab, price: Number(v.b.price) }, c: { bar: v.ac, price: Number(v.c.price) } },
      lines: lines
    };
  }

  root.JPWNocudaTransfer = Object.freeze({ parse: parse, serialize: serialize, example: example, geometry: geometry });
})(typeof window !== 'undefined' ? window : globalThis);
