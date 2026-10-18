(function (window) {
  'use strict';
  var ns = window.JPWTimeTwins = window.JPWTimeTwins || {};
  var key = 'jpwealth_time_twins_v1';
  var statuses = ['demonstrated', 'assisted', 'skipped'];
  function empty() { return { schemaVersion: 1, currentMissionId: 'early-start', missions: {} }; }
  function isObject(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
  function valid(value) {
    if (!isObject(value) || Object.keys(value).length !== 3 || !Object.prototype.hasOwnProperty.call(value, 'schemaVersion') || !Object.prototype.hasOwnProperty.call(value, 'currentMissionId') || !Object.prototype.hasOwnProperty.call(value, 'missions')) return false;
    if (value.schemaVersion !== 1 || ns.catalog.ids.indexOf(value.currentMissionId) < 0 || !isObject(value.missions)) return false;
    return Object.keys(value.missions).every(function (id) { return ns.catalog.ids.indexOf(id) >= 0 && statuses.indexOf(value.missions[id]) >= 0; });
  }
  function result(ok, blocked, value, raw, error) { return { ok: ok, blocked: blocked, value: value, raw: raw, error: error }; }
  function resolve(storage) {
    var resolved = storage === undefined ? window.localStorage : storage;
    if (!resolved || typeof resolved.getItem !== 'function') throw new Error('Armazenamento indisponível.');
    return resolved;
  }
  function parse(raw) {
    if (raw === null) return result(true, false, empty(), null, null);
    try {
      if (typeof raw !== 'string') throw new Error('Formato incompatível.');
      var value = JSON.parse(raw);
      if (!valid(value)) throw new Error('Progresso incompatível.');
      return result(true, false, value, raw, null);
    } catch (error) {
      return result(false, true, empty(), raw, 'O progresso salvo está corrompido ou é incompatível. Seus dados foram preservados; use Reiniciar explicitamente para substituí-los.');
    }
  }
  function read(storage) {
    try { return parse(resolve(storage).getItem(key)); }
    catch (error) { return result(false, false, empty(), undefined, 'O armazenamento não está disponível. O progresso ficará temporário nesta sessão.'); }
  }
  function save(value, options, restart) {
    options = options || {};
    var requested;
    try {
      if (!valid(value)) return result(false, false, empty(), undefined, 'O progresso informado tem campos ou estados inválidos.');
      // Copy only the documented envelope; never serialize parameters or caller objects.
      var missions = {};
      Object.keys(value.missions).forEach(function (id) { missions[id] = value.missions[id]; });
      requested = { schemaVersion: 1, currentMissionId: value.currentMissionId, missions: missions };
    } catch (error) { return result(false, false, empty(), undefined, 'O progresso informado não pôde ser validado.'); }
    var current = read(options.storage);
    if (current.raw === undefined) return current;
    if (options.expectedRaw === undefined || current.raw !== options.expectedRaw) return result(false, current.blocked, current.value, current.raw, 'Conflito: o progresso foi alterado em outra sessão. Releia antes de salvar.');
    if (current.blocked && !restart) return current;
    var raw = JSON.stringify(requested);
    try { resolve(options.storage).setItem(key, raw); }
    catch (error) { return result(false, false, requested, current.raw, 'Não foi possível salvar o progresso. Ele ficará temporário nesta sessão; o conteúdo anterior foi preservado.'); }
    var checked = read(options.storage);
    if (!checked.ok || checked.raw !== raw) return result(false, checked.blocked, requested, checked.raw, 'Não foi possível confirmar a gravação. O progresso pode ter sido alterado em outra sessão.');
    return result(true, false, requested, raw, null);
  }
  function write(value, options) { return save(value, options, false); }
  function restart(options) { return save(empty(), options, true); }
  ns.progress = Object.freeze({ key: key, read: read, write: write, restart: restart });
})(window);
