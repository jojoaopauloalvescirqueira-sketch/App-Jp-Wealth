// ============ GALTON BOARD — PRNG DETERMINISTICO ============
// Nenhum caminho de trajetoria sorteia esquerda/direita. Este gerador e usado
// somente para a tolerancia fixa dos pinos e o jitter no instante da soltura.
(function (global) {
  "use strict";

  var JPWGalton = global.JPWGalton || (global.JPWGalton = {});
  var UINT32_RANGE = 4294967296;

  function hashString(value) {
    var text = String(value);
    var hash = 2166136261;
    var index;
    for (index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function normalizeSeed(seed) {
    if (typeof seed === "number" && Number.isFinite(seed)) return seed >>> 0;
    if (typeof seed === "bigint") return Number(seed & BigInt(0xffffffff)) >>> 0;
    if (typeof seed === "string" && /^\s*[+-]?\d+\s*$/.test(seed)) {
      var parsed = Number(seed);
      if (Number.isFinite(parsed)) return parsed >>> 0;
    }
    if (seed === undefined || seed === null || seed === "") return 0;
    return hashString(seed);
  }

  function derive(seed, label) {
    var base = normalizeSeed(seed);
    return hashString(String(base) + ":" + String(label));
  }

  function create(seed) {
    var initialSeed = normalizeSeed(seed);
    var state = initialSeed;

    function nextUint32() {
      state = (state + 0x6d2b79f5) >>> 0;
      var value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return (value ^ (value >>> 14)) >>> 0;
    }

    function next() {
      return nextUint32() / UINT32_RANGE;
    }

    return {
      seed: initialSeed,
      next: next,
      nextUint32: nextUint32,
      float: function (min, max) {
        var low = Number(min);
        var high = Number(max);
        if (!Number.isFinite(low) || !Number.isFinite(high) || high < low) {
          throw new RangeError("rng.float requer limites finitos e ordenados");
        }
        return low + (high - low) * next();
      },
      signed: function (amplitude) {
        var bound = Number(amplitude);
        if (!Number.isFinite(bound) || bound < 0) throw new RangeError("rng.signed requer amplitude nao negativa");
        return (next() * 2 - 1) * bound;
      },
      integer: function (min, max) {
        var low = Math.ceil(Number(min));
        var high = Math.floor(Number(max));
        if (!Number.isFinite(low) || !Number.isFinite(high) || high < low) {
          throw new RangeError("rng.integer requer limites inteiros e ordenados");
        }
        return low + Math.floor(next() * (high - low + 1));
      },
      fork: function (label) { return create(derive(initialSeed, label)); },
      getState: function () { return state >>> 0; },
      reset: function () { state = initialSeed; return state; }
    };
  }

  function newSeed() {
    var cryptoObject = global.crypto;
    if (cryptoObject && typeof cryptoObject.getRandomValues === "function") {
      var words = new Uint32Array(1);
      cryptoObject.getRandomValues(words);
      return words[0] >>> 0;
    }
    // Fallback sem Math.random para runtimes de teste antigos. A seed continua
    // explicita e reproduzivel depois de gerada, embora nao seja criptografica.
    var time = Date.now() >>> 0;
    var highResolution = global.performance && typeof global.performance.now === "function"
      ? Math.floor(global.performance.now() * 1000) >>> 0
      : 0;
    return hashString(String(time) + ":" + String(highResolution));
  }

  function sequence(seed, count) {
    var size = Math.max(0, Math.floor(Number(count) || 0));
    var generator = create(seed);
    var values = [];
    var index;
    for (index = 0; index < size; index += 1) values.push(generator.next());
    return values;
  }

  JPWGalton.rng = Object.freeze({
    hashString: hashString,
    normalizeSeed: normalizeSeed,
    derive: derive,
    create: create,
    newSeed: newSeed,
    sequence: sequence
  });
})(typeof window !== "undefined" ? window : globalThis);
