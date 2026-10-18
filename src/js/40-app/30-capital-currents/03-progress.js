(function () {
  'use strict';
  var ns = window.JPWCapitalCurrents = window.JPWCapitalCurrents || {};
  var KEY = 'jpwealth_capital_field_v1', VERSION = 1;
  var IDS = ['intro-field', 'intro-pressure', 'intro-depth', 'release-pressure', 'same-pulse-depth', 'shallow-band'];
  var RANK = { skipped: 0, seen: 1, practiced: 2 };
  function empty() { return { version: VERSION, steps: {} }; }
  function plain(value) { return !!value && Object.prototype.toString.call(value) === '[object Object]'; }
  function dataProperty(value, key) {
    var descriptor = Object.getOwnPropertyDescriptor(value, key);
    return descriptor && descriptor.enumerable && Object.prototype.hasOwnProperty.call(descriptor, 'value') ? descriptor : null;
  }
  function valid(value) {
    if (!plain(value) || Reflect.ownKeys(value).length !== 2) return false;
    var version = dataProperty(value, 'version'), steps = dataProperty(value, 'steps');
    if (!version || version.value !== VERSION || !steps || !plain(steps.value)) return false;
    return Reflect.ownKeys(steps.value).every(function (id) {
      var status = dataProperty(steps.value, id);
      return IDS.indexOf(id) !== -1 && status && typeof status.value === 'string' &&
        Object.prototype.hasOwnProperty.call(RANK, status.value);
    });
  }
  function clone(value) {
    var result = empty(), steps = Object.getOwnPropertyDescriptor(value, 'steps').value;
    Object.keys(steps).forEach(function (id) { result.steps[id] = Object.getOwnPropertyDescriptor(steps, id).value; });
    return result;
  }
  function store(given) { return given === undefined ? window.localStorage : given; }
  function load(given) {
    try {
      var raw = store(given).getItem(KEY);
      if (raw === null) return { value: empty(), raw: raw, mode: 'ok', message: '' };
      var value;
      try { value = JSON.parse(raw); } catch (_) { /* Preserve unreadable bytes. */ }
      if (!valid(value)) return { value: empty(), raw: raw, mode: 'incompatible', message: 'Há um progresso incompatível preservado neste navegador. Recomece explicitamente para substituí-lo.' };
      return { value: clone(value), raw: raw, mode: 'ok', message: '' };
    } catch (_) {
      return { value: empty(), mode: 'temporary', message: 'O progresso ficará apenas nesta sessão: o armazenamento do navegador está indisponível.' };
    }
  }
  function failedWriteMode(target, original, completed, attempted) {
    if (completed) return 'conflict';
    if (!attempted) return 'temporary';
    try { return target.getItem(KEY) === original ? 'temporary' : 'conflict'; }
    catch (_) { return 'conflict'; }
  }
  function save(value, given, expectedRaw) {
    if (!valid(value)) return { ok: false, message: 'Progresso inválido; nenhuma gravação foi realizada.' };
    var current = load(given);
    if (arguments.length >= 3 && current.raw !== expectedRaw) return { ok: false, mode: 'conflict', message: 'O progresso mudou em outra aba. Releia antes de salvar.' };
    if (current.mode !== 'ok') return { ok: false, raw: current.raw, mode: current.mode, message: current.message };
    var wrote = false, attempted = false;
    try {
      var encoded = JSON.stringify(clone(value)), target = store(given);
      attempted = true; target.setItem(KEY, encoded); wrote = true;
      if (target.getItem(KEY) !== encoded) return { ok: false, mode: 'conflict', message: 'A gravação não pôde ser confirmada. Releia o progresso atualizado.' };
      return { ok: true, raw: encoded, mode: 'ok', message: '' };
    } catch (_) {
      var mode = failedWriteMode(target, current.raw, wrote, attempted);
      return { ok: false, mode: mode, message: mode === 'conflict' ? 'A gravação não pôde ser confirmada. Releia antes de tentar novamente.' : 'Não foi possível salvar. O progresso continua disponível somente nesta sessão.' };
    }
  }
  function mark(value, id, status) {
    if (!valid(value) || IDS.indexOf(id) === -1 || !Object.prototype.hasOwnProperty.call(RANK, status)) throw new RangeError('Etapa ou estado de progresso inválido.');
    var next = clone(value), previous = next.steps[id];
    if (previous === undefined || RANK[status] > RANK[previous]) next.steps[id] = status;
    return next;
  }
  function restart(given, expectedRaw) {
    var value = empty();
    var current = load(given), wrote = false, attempted = false;
    if (current.mode === 'temporary') return { value: value, mode: 'temporary', message: current.message };
    if (current.mode === 'incompatible' && arguments.length < 2) return { value: current.value, raw: current.raw, mode: 'conflict', message: 'Releia e confirme os bytes preservados antes de recomeçar.' };
    if (arguments.length >= 2 && current.raw !== expectedRaw) return { value: current.value, raw: current.raw, mode: 'conflict', message: 'O progresso mudou em outra aba. Releia antes de recomeçar.' };
    try {
      var encoded = JSON.stringify(clone(value)), target = store(given);
      attempted = true; target.setItem(KEY, encoded); wrote = true;
      if (target.getItem(KEY) !== encoded) return { value: value, mode: 'conflict', message: 'O reinício não pôde ser confirmado no navegador.' };
      return { value: value, raw: encoded, mode: 'ok', message: '' };
    } catch (_) {
      var mode = failedWriteMode(target, current.raw, wrote, attempted);
      return { value: value, mode: mode, message: mode === 'conflict' ? 'O reinício não pôde ser confirmado. Releia antes de tentar novamente.' : 'O reinício vale somente nesta sessão; o navegador não permitiu salvar.' };
    }
  }
  ns.progress = Object.freeze({ KEY: KEY, VERSION: VERSION, load: load, save: save, mark: mark, restart: restart });
}());
