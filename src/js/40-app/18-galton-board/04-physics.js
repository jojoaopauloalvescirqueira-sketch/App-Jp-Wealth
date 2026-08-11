// ============ GALTON BOARD — MOTOR FISICO PLANCK.JS ============
// Passo fixo de 1/120 s, acumulador separado do render e aleatoriedade apenas
// na tolerancia fixa dos pinos e no ponto inicial de cada bola.
(function (global) {
  "use strict";

  var JPWGalton = global.JPWGalton || (global.JPWGalton = {});
  var configAPI = JPWGalton.config;
  var rngAPI = JPWGalton.rng;
  var CATEGORY_BOARD = 0x0001;
  var CATEGORY_BALL = 0x0002;
  var MAX_FRAME_SECONDS = 0.25;

  function copyOwn(source) {
    var target = {};
    if (!source || typeof source !== "object" || Array.isArray(source)) return target;
    Object.keys(source).forEach(function (key) { target[key] = source[key]; });
    return target;
  }

  function mergeConfig(base, patch) {
    var merged = copyOwn(base);
    Object.keys(copyOwn(patch)).forEach(function (key) { merged[key] = patch[key]; });
    return merged;
  }

  function requireDependencies(planckOverride) {
    if (!configAPI || !rngAPI) {
      throw new Error("JPWGalton.config e JPWGalton.rng devem ser carregados antes do motor fisico");
    }
    var planck = planckOverride || global.planck;
    if (!planck || typeof planck.World !== "function" || typeof planck.Vec2 !== "function") {
      throw new Error("Planck.js 1.5.0 nao esta disponivel no runtime");
    }
    if (typeof (planck.Circle || planck.CircleShape) !== "function" || typeof (planck.Edge || planck.EdgeShape) !== "function") {
      throw new Error("Planck.js nao expoe as formas Circle e Edge esperadas");
    }
    return planck;
  }

  function createEngine(options) {
    var settings = options && typeof options === "object" ? options : {};
    var planck = requireDependencies(settings.planck);
    var CircleShape = planck.Circle || planck.CircleShape;
    var EdgeShape = planck.Edge || planck.EdgeShape;
    var callbacks = {
      onSettle: typeof settings.onSettle === "function" ? settings.onSettle : null,
      onStateChange: typeof settings.onStateChange === "function" ? settings.onStateChange : null
    };
    var config = configAPI.validate(settings.config || configAPI.DEFAULTS).value;
    var seed = rngAPI.normalizeSeed(settings.seed === undefined ? rngAPI.newSeed() : settings.seed);
    var world = null;
    var boardBody = null;
    var geometry = null;
    var pegRng = null;
    var spawnRng = null;
    var collisionListener = null;
    var active = [];
    var histogram = [];
    var destroyed = false;
    var state = null;

    function freshState() {
      return {
        started: false,
        paused: false,
        queuedCount: 0,
        spawnedCount: 0,
        settledCount: 0,
        expiredCount: 0,
        expiredByReason: { outside: 0, maxAge: 0 },
        rejectedCount: 0,
        collisionCount: 0,
        simulatedTime: 0,
        stepCount: 0,
        nextBallId: 1,
        spawnAccumulator: 1 / config.releaseRate,
        frameAccumulator: 0,
        droppedTime: 0,
        lastSubsteps: 0,
        maxActiveObserved: 0,
        pendingSpawnX: null,
        releaseBlocked: false,
        releaseBlockedSteps: 0
      };
    }

    function gravityVector() {
      var radians = config.tiltDegrees * Math.PI / 180;
      return planck.Vec2(
        config.gravity * Math.sin(radians),
        -config.gravity * Math.cos(radians)
      );
    }

    function circle(center, radius) {
      return center ? new CircleShape(center, radius) : new CircleShape(radius);
    }

    function edge(x1, y1, x2, y2) {
      return new EdgeShape(planck.Vec2(x1, y1), planck.Vec2(x2, y2));
    }

    function createBoardFixtures() {
      boardBody = world.createBody({ type: "static", userData: { kind: "galton-board" } });
      geometry.pegs.forEach(function (peg) {
        boardBody.createFixture(circle(planck.Vec2(peg.x, peg.y), peg.radius), {
          density: 0,
          friction: config.ballFriction,
          restitution: config.ballRestitution,
          filterCategoryBits: CATEGORY_BOARD,
          filterMaskBits: CATEGORY_BALL,
          userData: { kind: "peg", id: peg.id, row: peg.row, column: peg.column }
        });
      });
      geometry.walls.forEach(function (wall) {
        boardBody.createFixture(edge(wall.x1, wall.y1, wall.x2, wall.y2), {
          density: 0,
          friction: config.ballFriction,
          restitution: Math.min(config.ballRestitution, 0.35),
          filterCategoryBits: CATEGORY_BOARD,
          filterMaskBits: CATEGORY_BALL,
          userData: { kind: wall.kind, index: wall.index }
        });
      });
    }

    function detachWorld() {
      if (world && collisionListener && typeof world.off === "function") {
        world.off("begin-contact", collisionListener);
      }
      if (world) {
        active.forEach(function (ball) {
          world.destroyBody(ball.body);
        });
      }
      active = [];
      boardBody = null;
      world = null;
      collisionListener = null;
    }

    function buildWorld() {
      pegRng = rngAPI.create(rngAPI.derive(seed, "pegs"));
      spawnRng = rngAPI.create(rngAPI.derive(seed, "spawn"));
      geometry = configAPI.createGeometry(config, pegRng.next);
      histogram = new Array(geometry.binCount).fill(0);
      state = freshState();
      world = planck.World({
        gravity: gravityVector(),
        allowSleep: true,
        continuousPhysics: true
      });
      if (typeof world.setContinuousPhysics === "function") world.setContinuousPhysics(true);
      collisionListener = function () { state.collisionCount += 1; };
      world.on("begin-contact", collisionListener);
      createBoardFixtures();
    }

    function ensureAlive() {
      if (destroyed) throw new Error("O motor Galton foi destruido");
    }

    function notifyState(reason) {
      if (callbacks.onStateChange) callbacks.onStateChange(snapshot(), reason);
    }

    function pendingSpawnX() {
      if (state.pendingSpawnX !== null) return state.pendingSpawnX;
      if (state.queuedCount <= 0 || active.length >= config.maxActiveBalls) return false;
      var releaseSample = spawnRng.signed(1);
      var jitter = releaseSample * config.releaseJitter * config.pegSpacing;
      // Jitter exatamente zero, soltura central, gravidade vertical e pino
      // nominal formam um equilibrio matematico perfeito sobre o primeiro
      // pino. Um desempate de 0,01% do espacamento, com sinal derivado da seed,
      // evita esse artefato numerico. Ele ocorre somente no instante inicial;
      // nunca ha sorteio ou impulso durante a trajetoria.
      if (
        config.releaseJitter === 0 &&
        config.pegTolerance === 0 &&
        Math.abs(config.releasePoint) < 1e-12 &&
        Math.abs(config.tiltDegrees) < 1e-12
      ) {
        jitter = (releaseSample < 0 ? -1 : 1) * config.pegSpacing * 0.0001;
      }
      state.pendingSpawnX = Math.max(geometry.release.minX, Math.min(geometry.release.maxX, geometry.release.x + jitter));
      return state.pendingSpawnX;
    }

    function releaseIsClear(x) {
      if (!config.ballCollisions) return true;
      var clearance = config.ballRadius * 2 + 0.01;
      var clearanceSquared = clearance * clearance;
      return active.every(function (ball) {
        var position = ball.body.getPosition();
        var dx = position.x - x;
        var dy = position.y - geometry.release.y;
        return dx * dx + dy * dy >= clearanceSquared;
      });
    }

    function spawnBall() {
      if (state.queuedCount <= 0 || active.length >= config.maxActiveBalls) return false;
      var x = pendingSpawnX();
      if (!releaseIsClear(x)) {
        state.releaseBlocked = true;
        state.releaseBlockedSteps += 1;
        return false;
      }
      state.releaseBlocked = false;
      state.pendingSpawnX = null;
      var id = state.nextBallId;
      state.nextBallId += 1;
      var body = world.createBody({
        type: "dynamic",
        position: planck.Vec2(x, geometry.release.y),
        bullet: true,
        // Uma bola quase central pode equilibrar sobre o primeiro pino. Se o
        // solver a adormecer ali, ela nunca recebe nova integracao e acabaria
        // expirada. Mantemos apenas as bolas dinamicas acordadas; corpos ja
        // assentados continuam removidos logo apos a janela de estabilidade.
        allowSleep: false,
        linearDamping: config.linearDamping,
        angularDamping: config.angularDamping,
        userData: { kind: "galton-ball", id: id }
      });
      body.createFixture(circle(null, config.ballRadius), {
        density: config.ballDensity,
        friction: config.ballFriction,
        restitution: config.ballRestitution,
        filterCategoryBits: CATEGORY_BALL,
        filterMaskBits: CATEGORY_BOARD | (config.ballCollisions ? CATEGORY_BALL : 0),
        userData: { kind: "galton-ball", id: id }
      });
      active.push({
        id: id,
        body: body,
        bornAt: state.simulatedTime,
        stableTime: 0
      });
      state.queuedCount -= 1;
      state.spawnedCount += 1;
      state.maxActiveObserved = Math.max(state.maxActiveObserved, active.length);
      return true;
    }

    function scheduleSpawns() {
      var interval = 1 / config.releaseRate;
      if (state.queuedCount <= 0 || active.length >= config.maxActiveBalls) {
        state.spawnAccumulator = Math.min(interval, state.spawnAccumulator + config.fixedTimeStep);
        return;
      }
      state.spawnAccumulator += config.fixedTimeStep;
      var spawnedThisStep = 0;
      while (
        state.queuedCount > 0 &&
        active.length < config.maxActiveBalls &&
        state.spawnAccumulator + 1e-12 >= interval &&
        spawnedThisStep < 16
      ) {
        if (!spawnBall()) {
          // Colisoes bola-bola exigem um emissor fisicamente livre. A fila e a
          // amostra de soltura ficam pendentes; nenhum corpo nasce sobreposto.
          state.spawnAccumulator = Math.min(state.spawnAccumulator, interval);
          break;
        }
        state.spawnAccumulator -= interval;
        spawnedThisStep += 1;
      }
      if (active.length >= config.maxActiveBalls) state.spawnAccumulator = Math.min(state.spawnAccumulator, interval);
    }

    function binIndexForX(x) {
      var raw = Math.floor((x - geometry.bounds.left) / config.pegSpacing);
      return Math.max(0, Math.min(geometry.binCount - 1, raw));
    }

    function inspectAndRetireBalls() {
      var survivors = [];
      var removals = [];
      active.forEach(function (ball) {
        var position = ball.body.getPosition();
        var velocity = ball.body.getLinearVelocity();
        var speed = Math.sqrt(velocity.x * velocity.x + velocity.y * velocity.y);
        var angularEdgeSpeed = Math.abs(ball.body.getAngularVelocity()) * config.ballRadius;
        var insideCompartment =
          position.y <= geometry.dividerTopY + config.ballRadius &&
          position.y >= geometry.floorY - config.ballRadius &&
          position.x >= geometry.bounds.left &&
          position.x <= geometry.bounds.right;
        if (insideCompartment && speed <= config.settleSpeed && angularEdgeSpeed <= config.settleSpeed * 1.5) {
          ball.stableTime += config.fixedTimeStep;
        } else {
          ball.stableTime = 0;
        }

        if (ball.stableTime + 1e-12 >= config.settleDuration) {
          removals.push({
            kind: "settled",
            ball: ball,
            x: position.x,
            y: position.y,
            binIndex: binIndexForX(position.x)
          });
          return;
        }

        var age = state.simulatedTime - ball.bornAt;
        var outside =
          position.y < geometry.bounds.bottom - config.rowSpacing * 2 ||
          position.x < geometry.bounds.left - config.pegSpacing * 2 ||
          position.x > geometry.bounds.right + config.pegSpacing * 2;
        if (outside || age >= config.maxBallAge) {
          removals.push({
            kind: "expired",
            reason: outside ? "outside" : "maxAge",
            ball: ball,
            x: position.x,
            y: position.y
          });
          return;
        }
        survivors.push(ball);
      });

      active = survivors;
      var settledEvents = [];
      removals.forEach(function (removal) {
        world.destroyBody(removal.ball.body);
        if (removal.kind === "settled") {
          histogram[removal.binIndex] += 1;
          state.settledCount += 1;
          settledEvents.push({
            id: removal.ball.id,
            binIndex: removal.binIndex,
            binCount: histogram[removal.binIndex],
            settledCount: state.settledCount,
            simulatedTime: state.simulatedTime,
            x: removal.x,
            y: removal.y
          });
        } else {
          state.expiredCount += 1;
          state.expiredByReason[removal.reason] += 1;
        }
      });

      if (callbacks.onSettle) {
        settledEvents.forEach(function (event) { callbacks.onSettle(event); });
      }
      return removals.length > 0;
    }

    function fixedStep() {
      scheduleSpawns();
      world.step(config.fixedTimeStep, config.velocityIterations, config.positionIterations);
      state.simulatedTime += config.fixedTimeStep;
      state.stepCount += 1;
      return inspectAndRetireBalls();
    }

    function enqueue(count) {
      ensureAlive();
      var requested = Math.floor(Number(count));
      if (!Number.isFinite(requested) || requested <= 0) return 0;
      var accepted = Math.min(requested, Math.max(0, config.maxQueue - state.queuedCount));
      var wasEmpty = state.queuedCount === 0;
      state.queuedCount += accepted;
      state.rejectedCount += requested - accepted;
      if (wasEmpty && accepted > 0) state.spawnAccumulator = Math.max(state.spawnAccumulator, 1 / config.releaseRate);
      notifyState("enqueue");
      return accepted;
    }

    function start() {
      ensureAlive();
      state.started = true;
      state.paused = false;
      notifyState("start");
      return snapshot();
    }

    function pause() {
      ensureAlive();
      if (state.started) state.paused = true;
      notifyState("pause");
      return snapshot();
    }

    function resume() {
      ensureAlive();
      state.started = true;
      state.paused = false;
      notifyState("resume");
      return snapshot();
    }

    function stop() {
      ensureAlive();
      state.started = false;
      state.paused = false;
      state.frameAccumulator = 0;
      notifyState("stop");
      return snapshot();
    }

    function step(elapsedSeconds) {
      ensureAlive();
      state.lastSubsteps = 0;
      if (!state.started || state.paused) return snapshot();
      var elapsed = Number(elapsedSeconds);
      if (!Number.isFinite(elapsed) || elapsed <= 0) return snapshot();
      var scaled = Math.min(elapsed, MAX_FRAME_SECONDS) * config.speed;
      state.frameAccumulator += scaled;
      var maximumAccumulator = config.fixedTimeStep * config.maxSubSteps;
      if (state.frameAccumulator > maximumAccumulator) {
        state.droppedTime += state.frameAccumulator - maximumAccumulator;
        state.frameAccumulator = maximumAccumulator;
      }
      var retired = false;
      while (
        state.frameAccumulator + 1e-12 >= config.fixedTimeStep &&
        state.lastSubsteps < config.maxSubSteps
      ) {
        retired = fixedStep() || retired;
        state.frameAccumulator -= config.fixedTimeStep;
        state.lastSubsteps += 1;
      }
      if (state.frameAccumulator < 0) state.frameAccumulator = 0;
      if (retired) notifyState("retire");
      return snapshot();
    }

    function tickFixed(steps) {
      ensureAlive();
      var count = Number(steps);
      if (!Number.isFinite(count) || count < 0 || Math.floor(count) !== count || count > 1000000) {
        throw new RangeError("tickFixed requer inteiro entre 0 e 1000000");
      }
      var retired = false;
      var index;
      for (index = 0; index < count; index += 1) retired = fixedStep() || retired;
      state.lastSubsteps = count;
      if (retired) notifyState("retire");
      return snapshot();
    }

    function setReleasePoint(value) {
      ensureAlive();
      config = configAPI.validate(mergeConfig(config, { releasePoint: value })).value;
      geometry.release.x = config.releasePoint * geometry.release.halfRange;
      notifyState("release-point");
      return config.releasePoint;
    }

    function setTilt(value) {
      ensureAlive();
      config = configAPI.validate(mergeConfig(config, { tiltDegrees: value })).value;
      world.setGravity(gravityVector());
      notifyState("tilt");
      return config.tiltDegrees;
    }

    function setSpeed(value) {
      ensureAlive();
      config = configAPI.validate(mergeConfig(config, { speed: value })).value;
      notifyState("speed");
      return config.speed;
    }

    function reset(resetOptions) {
      ensureAlive();
      var requested = resetOptions && typeof resetOptions === "object" ? resetOptions : {};
      if (requested.config) config = configAPI.validate(requested.config).value;
      if (requested.seed !== undefined) seed = rngAPI.normalizeSeed(requested.seed);
      detachWorld();
      buildWorld();
      notifyState("reset");
      return snapshot();
    }

    function configure(patch, configureOptions) {
      ensureAlive();
      var requested = configureOptions && typeof configureOptions === "object" ? configureOptions : {};
      config = configAPI.validate(mergeConfig(config, patch)).value;
      if (requested.seed !== undefined) seed = rngAPI.normalizeSeed(requested.seed);
      detachWorld();
      buildWorld();
      notifyState("configure");
      return snapshot();
    }

    function setSeed(nextSeed) {
      ensureAlive();
      seed = rngAPI.normalizeSeed(nextSeed);
      detachWorld();
      buildWorld();
      notifyState("seed");
      return seed;
    }

    function snapshot() {
      var balls = active.map(function (ball) {
        var position = ball.body.getPosition();
        var velocity = ball.body.getLinearVelocity();
        return {
          id: ball.id,
          x: position.x,
          y: position.y,
          vx: velocity.x,
          vy: velocity.y,
          speed: Math.sqrt(velocity.x * velocity.x + velocity.y * velocity.y),
          angle: ball.body.getAngle(),
          radius: config.ballRadius
        };
      });
      var running = !destroyed && state.started && !state.paused;
      return {
        config: copyOwn(config),
        geometry: geometry,
        balls: balls,
        histogram: histogram.slice(),
        settledCount: state.settledCount,
        activeCount: active.length,
        queuedCount: state.queuedCount,
        running: running,
        paused: !destroyed && state.started && state.paused,
        simulatedTime: state.simulatedTime,
        stepCount: state.stepCount,
        collisionCount: state.collisionCount,
        seed: seed,
        releasePoint: config.releasePoint,
        tiltDegrees: config.tiltDegrees,
        speed: config.speed,
        spawnedCount: state.spawnedCount,
        expiredCount: state.expiredCount,
        expiredByReason: copyOwn(state.expiredByReason),
        rejectedCount: state.rejectedCount,
        bodyCount: world && typeof world.getBodyCount === "function" ? world.getBodyCount() : active.length,
        maxActiveObserved: state.maxActiveObserved,
        droppedTime: state.droppedTime,
        lastSubsteps: state.lastSubsteps,
        releaseBlocked: state.releaseBlocked,
        releaseBlockedSteps: state.releaseBlockedSteps,
        idle: active.length === 0 && state.queuedCount === 0
      };
    }

    function destroy() {
      if (destroyed) return;
      detachWorld();
      destroyed = true;
      state.started = false;
      state.paused = false;
      state.queuedCount = 0;
      callbacks.onSettle = null;
      callbacks.onStateChange = null;
    }

    buildWorld();

    return Object.freeze({
      enqueue: enqueue,
      start: start,
      pause: pause,
      resume: resume,
      stop: stop,
      step: step,
      tickFixed: tickFixed,
      setReleasePoint: setReleasePoint,
      setTilt: setTilt,
      setSpeed: setSpeed,
      setSeed: setSeed,
      configure: configure,
      reset: reset,
      snapshot: snapshot,
      destroy: destroy
    });
  }

  JPWGalton.physics = Object.freeze({
    CATEGORY_BOARD: CATEGORY_BOARD,
    CATEGORY_BALL: CATEGORY_BALL,
    createEngine: createEngine
  });
  JPWGalton.createEngine = createEngine;
})(typeof window !== "undefined" ? window : globalThis);
