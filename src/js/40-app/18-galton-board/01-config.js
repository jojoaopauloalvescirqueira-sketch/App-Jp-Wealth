// ============ GALTON BOARD — CONFIGURACAO E GEOMETRIA ============
// Modulo isolado do estado financeiro. Toda medida abaixo usa unidades do
// mundo fisico; releasePoint e a unica excecao, normalizada em [-1, 1].
(function (global) {
  "use strict";

  var JPWGalton = global.JPWGalton || (global.JPWGalton = {});
  var FIXED_TIME_STEP = 1 / 120;
  var SPEEDS = [0.5, 1, 2, 4];

  function deepFreeze(value) {
    if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
    Object.keys(value).forEach(function (key) { deepFreeze(value[key]); });
    return Object.freeze(value);
  }

  var LIMITS = deepFreeze({
    rows: { min: 6, max: 18, integer: true },
    pegSpacing: { min: 0.65, max: 1.4 },
    rowSpacing: { min: 0.55, max: 1.2 },
    pegRadius: { min: 0.05, max: 0.16 },
    ballRadius: { min: 0.08, max: 0.25 },
    ballDensity: { min: 0.25, max: 5 },
    ballRestitution: { min: 0, max: 0.9 },
    ballFriction: { min: 0, max: 1 },
    gravity: { min: 2, max: 20 },
    releaseJitter: { min: 0, max: 0.4 },
    pegTolerance: { min: 0, max: 0.04 },
    releasePoint: { min: -1, max: 1 },
    tiltDegrees: { min: -3, max: 3 },
    releaseRate: { min: 1, max: 120 },
    maxActiveBalls: { min: 20, max: 600, integer: true },
    maxQueue: { min: 500, max: 100000, integer: true },
    settleSpeed: { min: 0.04, max: 1 },
    settleDuration: { min: 0.15, max: 2 },
    maxBallAge: { min: 10, max: 120 },
    linearDamping: { min: 0, max: 1 },
    angularDamping: { min: 0, max: 1 },
    maxSubSteps: { min: 4, max: 32, integer: true },
    velocityIterations: { min: 4, max: 16, integer: true },
    positionIterations: { min: 2, max: 8, integer: true }
  });

  var DEFAULTS = deepFreeze({
    rows: 10,
    pegSpacing: 1,
    rowSpacing: 0.82,
    pegRadius: 0.09,
    ballRadius: 0.14,
    ballDensity: 1,
    ballRestitution: 0.28,
    ballFriction: 0.22,
    gravity: 9.81,
    releaseJitter: 0.07,
    pegTolerance: 0,
    ballCollisions: false,
    releasePoint: 0,
    tiltDegrees: 0,
    speed: 1,
    releaseRate: 24,
    maxActiveBalls: 240,
    maxQueue: 100000,
    settleSpeed: 0.22,
    settleDuration: 0.55,
    maxBallAge: 45,
    linearDamping: 0.08,
    angularDamping: 0.08,
    fixedTimeStep: FIXED_TIME_STEP,
    maxSubSteps: 16,
    velocityIterations: 8,
    positionIterations: 3
  });

  var PRESETS = deepFreeze({
    realistic: {
      id: "realistic",
      label: "Realista",
      description: "Contato moderadamente dissipativo e pequenas variacoes na soltura.",
      values: {
        ballRestitution: 0.28,
        ballFriction: 0.22,
        gravity: 9.81,
        releaseJitter: 0.07,
        pegTolerance: 0,
        ballCollisions: false
      }
    },
    idealized: {
      id: "idealized",
      label: "Idealizado",
      description: "Baixo atrito, colisao mais elastica e geometria perfeitamente simetrica.",
      values: {
        ballRestitution: 0.72,
        ballFriction: 0.02,
        gravity: 9.81,
        releaseJitter: 0.025,
        pegTolerance: 0,
        ballCollisions: false
      }
    },
    highDissipation: {
      id: "highDissipation",
      label: "Alta dissipacao",
      description: "Pouco ressalto e atrito elevado.",
      values: {
        ballRestitution: 0.06,
        ballFriction: 0.68,
        gravity: 9.81,
        releaseJitter: 0.07,
        pegTolerance: 0,
        ballCollisions: false
      }
    },
    lowDissipation: {
      id: "lowDissipation",
      label: "Baixa dissipacao",
      description: "Mais ressalto e atrito reduzido.",
      values: {
        ballRestitution: 0.55,
        ballFriction: 0.08,
        gravity: 9.81,
        releaseJitter: 0.07,
        pegTolerance: 0,
        ballCollisions: false
      }
    }
  });

  var PRESET_ALIASES = {
    "high-dissipation": "highDissipation",
    "low-dissipation": "lowDissipation"
  };

  function copyOwn(source) {
    var target = {};
    if (!source || typeof source !== "object" || Array.isArray(source)) return target;
    Object.keys(source).forEach(function (key) { target[key] = source[key]; });
    return target;
  }

  function finiteNumber(value) {
    if (typeof value === "string" && value.trim() === "") return null;
    var number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function boundedField(source, field, errors) {
    var spec = LIMITS[field];
    var candidate = finiteNumber(source[field]);
    if (source[field] === undefined) return DEFAULTS[field];
    if (candidate === null) {
      errors.push({ field: field, code: "not-finite", received: source[field] });
      return DEFAULTS[field];
    }
    if (spec.integer) candidate = Math.round(candidate);
    if (candidate < spec.min || candidate > spec.max) {
      errors.push({ field: field, code: "out-of-range", received: source[field], min: spec.min, max: spec.max });
      candidate = Math.max(spec.min, Math.min(spec.max, candidate));
    }
    return candidate;
  }

  function booleanField(value, fallback, field, errors) {
    if (value === undefined) return fallback;
    if (value === true || value === false) return value;
    if (value === "true") return true;
    if (value === "false") return false;
    errors.push({ field: field, code: "not-boolean", received: value });
    return fallback;
  }

  function closestSpeed(value) {
    var best = SPEEDS[0];
    var bestDistance = Infinity;
    SPEEDS.forEach(function (speed) {
      var distance = Math.abs(speed - value);
      if (distance < bestDistance) {
        best = speed;
        bestDistance = distance;
      }
    });
    return best;
  }

  function validate(input) {
    var source = copyOwn(input);
    var errors = [];
    var value = {};

    Object.keys(LIMITS).forEach(function (field) {
      value[field] = boundedField(source, field, errors);
    });
    value.ballCollisions = booleanField(source.ballCollisions, DEFAULTS.ballCollisions, "ballCollisions", errors);

    var requestedSpeed = source.speed === undefined ? DEFAULTS.speed : finiteNumber(source.speed);
    if (requestedSpeed === null || SPEEDS.indexOf(requestedSpeed) === -1) {
      errors.push({ field: "speed", code: "unsupported-speed", received: source.speed, allowed: SPEEDS.slice() });
      requestedSpeed = requestedSpeed === null ? DEFAULTS.speed : closestSpeed(requestedSpeed);
    }
    value.speed = requestedSpeed;

    // O passo e um invariante do experimento, nao uma preferencia configuravel.
    if (source.fixedTimeStep !== undefined && Math.abs(Number(source.fixedTimeStep) - FIXED_TIME_STEP) > 1e-12) {
      errors.push({ field: "fixedTimeStep", code: "fixed-invariant", received: source.fixedTimeStep });
    }
    value.fixedTimeStep = FIXED_TIME_STEP;

    // As imperfeicoes continuam microscopicas em relacao aos corpos. Esses
    // limites relacionais impedem que campos isoladamente validos deformem a
    // geometria ou transformem a soltura em um deslocamento macroscópico.
    var maxPegTolerance = value.pegRadius * 0.25;
    if (value.pegTolerance > maxPegTolerance) {
      errors.push({
        field: "pegTolerance",
        code: "peg-tolerance-relative",
        received: value.pegTolerance,
        maxForPegRadius: maxPegTolerance
      });
      value.pegTolerance = maxPegTolerance;
    }

    // Mantem corredor fisico entre pinos mesmo quando combinacoes individuais
    // estao dentro dos limites. O pior caso considera dois pinos deslocados em
    // sentidos opostos pela tolerancia fixa; a configuracao devolvida e segura.
    var sameRowDistance = Math.max(0, value.pegSpacing - value.pegTolerance * 2);
    var diagonalX = Math.max(0, value.pegSpacing * 0.5 - value.pegTolerance * 2);
    var diagonalY = Math.max(0, value.rowSpacing - value.pegTolerance * 2);
    var nearestPegDistance = Math.sqrt(diagonalX * diagonalX + diagonalY * diagonalY);
    var maxBallRadius = Math.min(sameRowDistance * 0.5, nearestPegDistance * 0.5) - value.pegRadius - 0.02;
    maxBallRadius = Math.max(LIMITS.ballRadius.min, Math.min(LIMITS.ballRadius.max, maxBallRadius));
    if (value.ballRadius > maxBallRadius) {
      errors.push({
        field: "ballRadius",
        code: "geometry-clearance",
        received: value.ballRadius,
        maxForGeometry: maxBallRadius
      });
      value.ballRadius = maxBallRadius;
    }

    var maxReleaseJitter = value.ballRadius * 0.5 / value.pegSpacing;
    if (value.releaseJitter > maxReleaseJitter) {
      errors.push({
        field: "releaseJitter",
        code: "release-jitter-relative",
        received: value.releaseJitter,
        maxForBallRadius: maxReleaseJitter
      });
      value.releaseJitter = maxReleaseJitter;
    }

    return {
      valid: errors.length === 0,
      value: value,
      errors: errors
    };
  }

  function applyPreset(presetId, overrides) {
    var canonicalId = PRESET_ALIASES[presetId] || presetId;
    var preset = PRESETS[canonicalId] || PRESETS.realistic;
    var combined = copyOwn(DEFAULTS);
    Object.keys(preset.values).forEach(function (key) { combined[key] = preset.values[key]; });
    Object.keys(copyOwn(overrides)).forEach(function (key) { combined[key] = overrides[key]; });
    return validate(combined).value;
  }

  function createGeometry(input, randomFn) {
    var config = validate(input).value;
    var rows = config.rows;
    var binCount = rows + 1;
    var topPegY = 0;
    var lastPegY = -(rows - 1) * config.rowSpacing;
    var dividerTopY = lastPegY - config.rowSpacing * 0.48;
    var floorY = dividerTopY - config.rowSpacing * 2.45;
    var releaseY = topPegY + config.rowSpacing * 1.75;
    var left = -binCount * config.pegSpacing * 0.5;
    var right = -left;
    var top = releaseY + config.rowSpacing * 0.55;
    var bottom = floorY;
    // O envelope inclinado acompanha os pinos externos. O controle normalizado
    // de soltura ocupa somente a abertura superior fisicamente segura; nao
    // deixa uma bola nascer do lado de fora das guias e contornar a malha.
    var guideTopHalfWidth = config.pegRadius + config.ballRadius + 0.22;
    var safeInset = config.ballRadius * 1.1;
    var releaseMinX = -guideTopHalfWidth + safeInset;
    var releaseMaxX = guideTopHalfWidth - safeInset;
    var releaseHalfRange = Math.max(0, Math.min(Math.abs(releaseMinX), Math.abs(releaseMaxX)));
    var pegRandom = typeof randomFn === "function" ? randomFn : function () { return 0.5; };
    var pegs = [];
    var bins = [];
    var dividerXs = [];
    var walls = [];
    var row;
    var column;

    for (row = 0; row < rows; row += 1) {
      for (column = 0; column <= row; column += 1) {
        var nominalX = (column - row * 0.5) * config.pegSpacing;
        var nominalY = topPegY - row * config.rowSpacing;
        var offsetX = 0;
        var offsetY = 0;
        if (config.pegTolerance > 0) {
          offsetX = (pegRandom() * 2 - 1) * config.pegTolerance;
          offsetY = (pegRandom() * 2 - 1) * config.pegTolerance;
        }
        pegs.push({
          id: "peg-" + row + "-" + column,
          row: row,
          column: column,
          nominalX: nominalX,
          nominalY: nominalY,
          offsetX: offsetX,
          offsetY: offsetY,
          x: nominalX + offsetX,
          y: nominalY + offsetY,
          radius: config.pegRadius
        });
      }
    }

    for (column = 0; column < binCount; column += 1) {
      var binLeft = left + column * config.pegSpacing;
      var binRight = binLeft + config.pegSpacing;
      bins.push({
        index: column,
        left: binLeft,
        right: binRight,
        centerX: (binLeft + binRight) * 0.5,
        width: config.pegSpacing,
        floorY: floorY,
        topY: dividerTopY
      });
    }

    var guideOuterX = (rows - 1) * config.pegSpacing * 0.5 + guideTopHalfWidth;
    walls.push({
      kind: "chute-left",
      x1: -guideTopHalfWidth,
      y1: topPegY,
      x2: -guideTopHalfWidth,
      y2: top
    });
    walls.push({
      kind: "chute-right",
      x1: guideTopHalfWidth,
      y1: topPegY,
      x2: guideTopHalfWidth,
      y2: top
    });
    walls.push({
      kind: "guide-left",
      x1: -guideTopHalfWidth,
      y1: topPegY,
      x2: -guideOuterX,
      y2: lastPegY
    });
    walls.push({
      kind: "guide-right",
      x1: guideTopHalfWidth,
      y1: topPegY,
      x2: guideOuterX,
      y2: lastPegY
    });
    walls.push({
      kind: "guide-left-lower",
      x1: -guideOuterX,
      y1: lastPegY,
      x2: left,
      y2: dividerTopY
    });
    walls.push({
      kind: "guide-right-lower",
      x1: guideOuterX,
      y1: lastPegY,
      x2: right,
      y2: dividerTopY
    });
    walls.push({ kind: "floor", x1: left, y1: floorY, x2: right, y2: floorY });
    walls.push({ kind: "left", x1: left, y1: floorY, x2: left, y2: top });
    walls.push({ kind: "right", x1: right, y1: floorY, x2: right, y2: top });
    for (column = 1; column < binCount; column += 1) {
      var dividerX = left + column * config.pegSpacing;
      dividerXs.push(dividerX);
      walls.push({
        kind: "divider",
        index: column - 1,
        x1: dividerX,
        y1: floorY,
        x2: dividerX,
        y2: dividerTopY
      });
    }

    var bounds = {
      left: left,
      right: right,
      bottom: bottom,
      top: top,
      width: right - left,
      height: top - bottom
    };

    return {
      rows: rows,
      binCount: binCount,
      pegs: pegs,
      bins: bins,
      bounds: bounds,
      worldBounds: bounds,
      floorY: floorY,
      dividerTopY: dividerTopY,
      dividerXs: dividerXs,
      guideTopHalfWidth: guideTopHalfWidth,
      guideOuterX: guideOuterX,
      walls: walls,
      release: {
        x: config.releasePoint * releaseHalfRange,
        y: releaseY,
        minX: releaseMinX,
        maxX: releaseMaxX,
        halfRange: releaseHalfRange
      }
    };
  }

  function theoryEligibility(input) {
    var config = validate(input).value;
    var reasons = [];
    if (Math.abs(config.releasePoint) > 1e-9) reasons.push("release-not-centered");
    if (Math.abs(config.tiltDegrees) > 1e-9) reasons.push("gravity-not-vertical");
    if (config.pegTolerance > 1e-12) reasons.push("peg-tolerance-breaks-symmetry");
    if (config.ballCollisions) reasons.push("ball-interactions-break-independence");
    return { eligible: reasons.length === 0, reasons: reasons };
  }

  function isTheoryEligible(input) {
    return theoryEligibility(input).eligible;
  }

  JPWGalton.config = deepFreeze({
    FIXED_TIME_STEP: FIXED_TIME_STEP,
    SPEEDS: SPEEDS.slice(),
    LIMITS: LIMITS,
    DEFAULTS: DEFAULTS,
    PRESETS: PRESETS,
    validate: validate,
    sanitize: function (input) { return validate(input).value; },
    applyPreset: applyPreset,
    createGeometry: createGeometry,
    geometry: createGeometry,
    theoryEligibility: theoryEligibility,
    isTheoryEligible: isTheoryEligible
  });
})(typeof window !== "undefined" ? window : globalThis);
