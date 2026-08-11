#!/usr/bin/env python3
"""Caracterizacao do Galton Board: matematica, fisica, persistencia e UI real.

O teste usa a pagina modular servida por HTTP e somente APIs publicas em
``window.JPWGalton``. Nao depende de rede, nao grava dados reais e nao usa um
limite de tempo como criterio de desempenho. O benchmark longo (10.000 bolas)
fica em ``tools/galton_board_benchmark.py``.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import socket
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}/index.html"


def assert_close(actual, expected, tolerance=1e-10, label="valor"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: esperado {expected!r}, recebido {actual!r}"
    )


def prepare_page(browser, url):
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        device_scale_factor=2,
        reduced_motion="reduce",
    )
    context.add_init_script("window.__onbShown=true;")
    page = context.new_page()
    observed = {"console": [], "pageerror": [], "failed": []}
    page.on("console", lambda message: observed["console"].append((message.type, message.text)))
    page.on("pageerror", lambda error: observed["pageerror"].append(str(error)))
    page.on("requestfailed", lambda request: observed["failed"].append((request.url, request.failure)))
    page.route(
        "**/api.frankfurter.dev/**",
        lambda route: route.fulfill(
            status=200, content_type="application/json", body='{"rate":1}'
        ),
    )
    # O contador de lifecycle e deliberadamente exposto apenas em origem local
    # com o opt-in de desenvolvimento; producao continua sem essa superficie.
    page.goto(url + "?galtonDebug=1", wait_until="load")
    page.wait_for_function(
        """() => window.JPWGalton && JPWGalton.config && JPWGalton.rng &&
          JPWGalton.statistics && JPWGalton.physics && JPWGalton.persistence &&
          JPWGalton.controller"""
    )
    page.evaluate(
        """() => {
          window.__onbShown = true;
          if (typeof closeModal === 'function') closeModal();
          window.alert = () => {};
          window.confirm = () => false;
          window.prompt = () => null;
        }"""
    )
    page.jpwealth_context = context
    page.jpwealth_observed = observed
    return page


def test_math_contract(page):
    result = page.evaluate(
        """() => {
          const {config, rng, statistics} = JPWGalton;
          const geometries = [6, 10, 18].map(rows => {
            const geometry = config.createGeometry({...config.DEFAULTS, rows});
            return {
              rows,
              pegs: geometry.pegs.length,
              bins: geometry.bins.length,
              dividers: geometry.dividerXs.length,
              releaseInside: geometry.release.x >= geometry.release.minX &&
                geometry.release.x <= geometry.release.maxX,
            };
          });
          const invalid = config.validate({
            ...config.DEFAULTS,
            rows: 999,
            ballRestitution: -5,
            tiltDegrees: 90,
            speed: 3,
            fixedTimeStep: 1 / 60,
          });
          const unsafeTolerance = config.validate({
            ...config.DEFAULTS,
            pegRadius: 0.05,
            pegTolerance: 0.04,
          });
          const unsafeJitter = config.validate({
            ...config.DEFAULTS,
            pegSpacing: 1.4,
            ballRadius: 0.08,
            releaseJitter: 0.4,
          });
          const extremeClearance = config.validate({
            ...config.DEFAULTS,
            pegSpacing: 0.65,
            rowSpacing: 0.55,
            pegRadius: 0.16,
            ballRadius: 0.139,
            pegTolerance: 0.04,
          });
          const presetIds = Object.keys(config.PRESETS);
          const presetValues = Object.fromEntries(presetIds.map(id => [
            id,
            config.applyPreset(id),
          ]));
          const eligibility = {
            centered: config.theoryEligibility(config.DEFAULTS),
            release: config.theoryEligibility({...config.DEFAULTS, releasePoint: 0.2}),
            tilt: config.theoryEligibility({...config.DEFAULTS, tiltDegrees: 0.5}),
            tolerance: config.theoryEligibility({...config.DEFAULTS, pegTolerance: 0.01}),
            interactions: config.theoryEligibility({...config.DEFAULTS, ballCollisions: true}),
          };
          const rngA = rng.sequence('JPW-seed', 12);
          const rngB = rng.sequence('JPW-seed', 12);
          const rngC = rng.sequence('outra-seed', 12);
          const gen = rng.create(20260811);
          const rngStateBefore = gen.getState();
          gen.next();
          const rngStateAfter = gen.getState();
          const histogram = [0, 1, 2, 1, 0];
          const description = statistics.describeHistogram(histogram);
          const binomial = statistics.binomialDistribution(4, 0.5);
          const comparison = statistics.compareToBinomial([1, 4, 6, 4, 1]);
          return {
            fixedStep: config.FIXED_TIME_STEP,
            limits: config.LIMITS,
            geometries,
            invalid,
            unsafeTolerance,
            unsafeJitter,
            extremeClearance,
            presetIds,
            presetValues,
            eligibility,
            rng: {
              same: JSON.stringify(rngA) === JSON.stringify(rngB),
              different: JSON.stringify(rngA) !== JSON.stringify(rngC),
              bounded: rngA.every(value => value >= 0 && value < 1),
              stateAdvanced: rngStateBefore !== rngStateAfter,
            },
            description,
            binomial,
            choose10_5: statistics.binomialCoefficient(10, 5),
            comparison,
          };
        }"""
    )

    assert_close(result["fixedStep"], 1 / 120, label="passo fixo")
    for geometry in result["geometries"]:
        rows = geometry["rows"]
        assert geometry["pegs"] == rows * (rows + 1) // 2, geometry
        assert geometry["bins"] == rows + 1, geometry
        assert geometry["dividers"] == rows, geometry
        assert geometry["releaseInside"], geometry

    invalid = result["invalid"]
    assert invalid["valid"] is False and invalid["errors"], invalid
    assert invalid["value"]["rows"] == result["limits"]["rows"]["max"]
    assert invalid["value"]["ballRestitution"] == result["limits"]["ballRestitution"]["min"]
    assert invalid["value"]["tiltDegrees"] == result["limits"]["tiltDegrees"]["max"]
    assert invalid["value"]["speed"] in (0.5, 1, 2, 4)
    assert_close(invalid["value"]["fixedTimeStep"], 1 / 120, label="invariante do passo")
    assert any(
        error["code"] == "peg-tolerance-relative"
        for error in result["unsafeTolerance"]["errors"]
    ), result["unsafeTolerance"]
    assert_close(
        result["unsafeTolerance"]["value"]["pegTolerance"],
        0.05 * 0.25,
        label="tolerancia relativa ao pino",
    )
    assert any(
        error["code"] == "release-jitter-relative"
        for error in result["unsafeJitter"]["errors"]
    ), result["unsafeJitter"]
    assert_close(
        result["unsafeJitter"]["value"]["releaseJitter"] * 1.4,
        result["unsafeJitter"]["value"]["ballRadius"] * 0.5,
        label="jitter relativo ao raio da bola",
    )
    assert any(
        error["code"] == "geometry-clearance"
        for error in result["extremeClearance"]["errors"]
    ), result["extremeClearance"]
    assert result["extremeClearance"]["value"]["ballRadius"] < 0.139

    assert set(result["presetIds"]) == {
        "realistic", "idealized", "highDissipation", "lowDissipation"
    }
    presets = result["presetValues"]
    assert presets["idealized"]["ballRestitution"] > presets["realistic"]["ballRestitution"]
    assert presets["highDissipation"]["ballFriction"] > presets["lowDissipation"]["ballFriction"]
    assert presets["realistic"]["ballCollisions"] is False

    eligibility = result["eligibility"]
    assert eligibility["centered"] == {"eligible": True, "reasons": []}
    assert eligibility["release"]["eligible"] is False
    assert "release-not-centered" in eligibility["release"]["reasons"]
    assert "gravity-not-vertical" in eligibility["tilt"]["reasons"]
    assert "peg-tolerance-breaks-symmetry" in eligibility["tolerance"]["reasons"]
    assert "ball-interactions-break-independence" in eligibility["interactions"]["reasons"]

    assert all(result["rng"].values()), result["rng"]
    stats = result["description"]
    assert stats["n"] == 4 and stats["mean"] == 2 and stats["mode"] == 2
    assert_close(stats["stdDev"], 2 ** -0.5, label="desvio padrao")
    assert_close(stats["skewness"], 0, label="assimetria")
    assert result["choose10_5"] == 252
    assert_close(sum(result["binomial"]), 1, label="soma binomial")
    expected = [0.0625, 0.25, 0.375, 0.25, 0.0625]
    for actual, reference in zip(result["binomial"], expected):
        assert_close(actual, reference, label="massa binomial")
    assert_close(result["comparison"]["totalVariation"], 0, label="comparacao binomial")


def test_physics_contract(page):
    result = page.evaluate(
        """() => {
          const base = {
            ...JPWGalton.config.DEFAULTS,
            rows: 8,
            releaseRate: 120,
            maxActiveBalls: 64,
            maxBallAge: 20,
            speed: 1,
          };

          // O acumulador deve converter dois meios-passos em um unico passo fisico.
          const accumulator = JPWGalton.physics.createEngine({config: base, seed: 17});
          accumulator.start();
          const a0 = accumulator.snapshot();
          const a1 = accumulator.step(1 / 240);
          const a2 = accumulator.step(1 / 240);
          const a3 = accumulator.step(1 / 60);
          accumulator.destroy();

          const settledEvents = [];
          const engine = JPWGalton.physics.createEngine({
            config: base,
            seed: 424242,
            onSettle: event => settledEvents.push(event),
          });
          const accepted = engine.enqueue(24);
          engine.start();
          let final = engine.snapshot();
          let guard = 0;
          while (!final.idle && guard < 20000) {
            final = engine.tickFixed(1);
            guard += 1;
          }

          // Mesma configuracao, seed, fila e numero de ticks => estado identico.
          function deterministicRun(seed) {
            const instance = JPWGalton.physics.createEngine({config: base, seed});
            instance.enqueue(36);
            instance.start();
            let snap = instance.snapshot();
            let ticks = 0;
            while (!snap.idle && ticks < 20000) {
              snap = instance.tickFixed(1);
              ticks += 1;
            }
            const fingerprint = {
              histogram: snap.histogram,
              settledCount: snap.settledCount,
              expiredCount: snap.expiredCount,
              stepCount: snap.stepCount,
              collisionCount: snap.collisionCount,
              maxActiveObserved: snap.maxActiveObserved,
            };
            instance.destroy();
            return fingerprint;
          }
          const deterministicA = deterministicRun(9090);
          const deterministicB = deterministicRun(9090);
          const deterministicOtherSeed = deterministicRun(9091);

          // O modo de interacao nao pode criar corpos sobrepostos no emissor.
          // A entrada maxima de tolerancia e normalizada antes de chegar ao mundo.
          const interactions = JPWGalton.physics.createEngine({
            config: {
              ...JPWGalton.config.DEFAULTS,
              releaseRate: 120,
              ballCollisions: true,
              pegTolerance: 0.04,
            },
            seed: 18473,
          });
          interactions.enqueue(100);
          interactions.start();
          let interactionFinal = interactions.snapshot();
          let interactionGuard = 0;
          while (!interactionFinal.idle && interactionGuard < 100000) {
            interactionFinal = interactions.tickFixed(1);
            interactionGuard += 1;
          }
          interactions.destroy();

          // Expiracao permanece um cleanup de seguranca e nunca vira amostra.
          const expiring = JPWGalton.physics.createEngine({
            config: {
              ...JPWGalton.config.DEFAULTS,
              rows: 18,
              gravity: 2,
              maxBallAge: 10,
            },
            seed: 7,
          });
          expiring.enqueue(1);
          expiring.start();
          let expiredFinal = expiring.snapshot();
          let expiredGuard = 0;
          while (!expiredFinal.idle && expiredGuard < 5000) {
            expiredFinal = expiring.tickFixed(1);
            expiredGuard += 1;
          }
          expiring.destroy();

          const summary = {
            fixed: {
              initial: a0.stepCount,
              half: a1.stepCount,
              twoHalves: a2.stepCount,
              plusSixtieth: a3.stepCount,
              lastSubsteps: a3.lastSubsteps,
            },
            accepted,
            guard,
            final,
            histogramTotal: final.histogram.reduce((sum, value) => sum + value, 0),
            eventCount: settledEvents.length,
            uniqueEventIds: new Set(settledEvents.map(event => event.id)).size,
            eventBinsValid: settledEvents.every(event =>
              event.binIndex >= 0 && event.binIndex < final.histogram.length),
            sameSeedEqual: JSON.stringify(deterministicA) === JSON.stringify(deterministicB),
            otherSeedDifferent:
              JSON.stringify(deterministicA.histogram) !==
              JSON.stringify(deterministicOtherSeed.histogram),
            deterministicA,
            interactionFinal,
            interactionGuard,
            expiredFinal,
          };
          engine.destroy();
          return summary;
        }"""
    )

    fixed = result["fixed"]
    assert fixed["initial"] == 0 and fixed["half"] == 0, fixed
    assert fixed["twoHalves"] == 1, fixed
    assert fixed["plusSixtieth"] == 3 and fixed["lastSubsteps"] == 2, fixed

    final = result["final"]
    assert result["accepted"] == 24
    assert result["guard"] < 20000, "motor nao ficou ocioso dentro da guarda deterministica"
    assert final["idle"] and final["activeCount"] == 0 and final["queuedCount"] == 0, final
    assert final["spawnedCount"] == 24 and final["settledCount"] == 24, final
    assert final["expiredCount"] == 0 and final["rejectedCount"] == 0, final
    assert result["histogramTotal"] == 24
    assert result["eventCount"] == result["uniqueEventIds"] == 24
    assert result["eventBinsValid"]
    assert final["bodyCount"] == 1, "corpos dinamicos devem ser removidos apos agregacao"
    assert final["maxActiveObserved"] <= final["config"]["maxActiveBalls"]
    assert result["sameSeedEqual"], result["deterministicA"]
    assert result["otherSeedDifferent"], (
        "as seeds escolhidas produziram histogramas iguais; ajuste a fixture deterministica"
    )
    interactions = result["interactionFinal"]
    assert result["interactionGuard"] < 100000, interactions
    assert interactions["spawnedCount"] == interactions["settledCount"] == 100, interactions
    assert interactions["expiredCount"] == interactions["rejectedCount"] == 0, interactions
    assert interactions["releaseBlockedSteps"] > 0, interactions
    assert_close(
        interactions["config"]["pegTolerance"],
        interactions["config"]["pegRadius"] * 0.25,
        label="tolerancia segura no smoke de colisoes",
    )
    expired = result["expiredFinal"]
    assert expired["expiredCount"] == 1 and expired["settledCount"] == 0, expired
    assert expired["expiredByReason"] == {"outside": 0, "maxAge": 1}, expired
    assert sum(expired["histogram"]) == 0, expired


def test_persistence_contract(page):
    result = page.evaluate(
        """() => {
          const persistence = JPWGalton.persistence;
          function storage(initial = {}, failWrite = false) {
            const data = new Map(Object.entries(initial));
            return {
              getItem(key) { return data.has(key) ? data.get(key) : null; },
              setItem(key, value) {
                if (failWrite) throw new DOMException('quota simulada', 'QuotaExceededError');
                data.set(key, String(value));
              },
              removeItem(key) { data.delete(key); },
              dump() { return Object.fromEntries(data); },
            };
          }

          const malformedRaw = '{invalido';
          const malformedStore = storage({[persistence.STORAGE_KEY]: malformedRaw});
          const malformed = persistence.read(malformedStore);
          const emptyStore = storage({[persistence.STORAGE_KEY]: ''});
          const empty = persistence.read(emptyStore);
          const throwingGetter = (() => {
            const descriptor = Object.getOwnPropertyDescriptor(window, 'localStorage');
            let readResult = null;
            let writeResult = null;
            let unexpected = null;
            try {
              Object.defineProperty(window, 'localStorage', {
                configurable: true,
                get() { throw new DOMException('acesso bloqueado', 'SecurityError'); },
              });
              readResult = persistence.read();
              writeResult = persistence.write({speed: 2});
            } catch (error) {
              unexpected = {name: error.name, message: error.message};
            } finally {
              if (descriptor) Object.defineProperty(window, 'localStorage', descriptor);
              else delete window.localStorage;
            }
            return {
              unexpected,
              read: readResult && {
                ok: readResult.ok,
                blocked: readResult.blocked,
                errorName: readResult.error && readResult.error.name,
              },
              write: writeResult && {
                ok: writeResult.ok,
                errorName: writeResult.error && writeResult.error.name,
              },
            };
          })();
          const invalidEnvelopes = [
            null,
            [],
            'texto',
            {},
            {schemaVersion: '1'},
            {schemaVersion: 1.5},
            {schemaVersion: 0},
          ].map(payload => {
            const raw = JSON.stringify(payload);
            const target = storage({[persistence.STORAGE_KEY]: raw});
            const result = persistence.read(target);
            return {
              blocked: result.blocked,
              ok: result.ok,
              hasError: Boolean(result.error),
              rawPreserved: target.getItem(persistence.STORAGE_KEY) === raw,
            };
          });
          const quota = persistence.write({speed: 4, rows: 12}, storage({}, true));

          const futurePayload = {
            schemaVersion: 99,
            preset: 'custom',
            showTheory: false,
            speed: 2,
            releasePoint: 0.25,
            tiltDegrees: -1.5,
            seed: 1234,
            futureTopLevel: {preservar: true},
            config: {
              ...JPWGalton.config.DEFAULTS,
              rows: 12,
              futurePhysicsField: {unit: 'JPW'},
            },
          };
          const futureRaw = JSON.stringify(futurePayload);
          const futureStore = storage({[persistence.STORAGE_KEY]: futureRaw});
          const futureRead = persistence.read(futureStore);
          const compatiblePayload = {...futurePayload, schemaVersion: 1};
          const compatibleStore = storage({
            [persistence.STORAGE_KEY]: JSON.stringify(compatiblePayload),
          });
          const read = persistence.read(compatibleStore);
          const write = persistence.write(
            read.value, compatibleStore, read.extensions, read.configExtensions
          );
          const roundTrip = JSON.parse(compatibleStore.getItem(persistence.STORAGE_KEY));

          const mainKey = 'jpwealth_v9_state';
          const beforeMain = localStorage.getItem(mainKey);
          const beforeS = JSON.stringify(S);
          localStorage.setItem('jpwealth_galton_unrelated_sentinel', 'preservar');
          const realWrite = persistence.write({...read.value, speed: 4}, localStorage);
          const isolation = {
            mainUntouched: localStorage.getItem(mainKey) === beforeMain,
            stateUntouched: JSON.stringify(S) === beforeS,
            unrelatedUntouched:
              localStorage.getItem('jpwealth_galton_unrelated_sentinel') === 'preservar',
            onlyPreferences:
              JSON.parse(localStorage.getItem(persistence.STORAGE_KEY)).histogram === undefined &&
              JSON.parse(localStorage.getItem(persistence.STORAGE_KEY)).balls === undefined,
            auxiliaryRegistered:
              typeof JP_WEALTH_AUX_STORAGE_KEYS !== 'undefined' &&
              JP_WEALTH_AUX_STORAGE_KEYS.includes(persistence.STORAGE_KEY),
          };
          localStorage.removeItem('jpwealth_galton_unrelated_sentinel');
          localStorage.removeItem(persistence.STORAGE_KEY);

          return {
            key: persistence.STORAGE_KEY,
            schema: persistence.SCHEMA_VERSION,
            malformed: {
              ok: malformed.ok,
              blocked: malformed.blocked,
              hasError: Boolean(malformed.error),
              rows: malformed.value.config.rows,
              rawPreserved: malformedStore.getItem(persistence.STORAGE_KEY) === malformedRaw,
            },
            empty: {
              ok: empty.ok,
              blocked: empty.blocked,
              hasError: Boolean(empty.error),
              rawPreserved: emptyStore.getItem(persistence.STORAGE_KEY) === '',
            },
            throwingGetter,
            invalidEnvelopes,
            future: {
              ok: futureRead.ok,
              blocked: futureRead.blocked,
              hasError: Boolean(futureRead.error),
              rawPreserved: futureStore.getItem(persistence.STORAGE_KEY) === futureRaw,
            },
            quota: {ok: quota.ok, hasError: Boolean(quota.error)},
            read: {
              ok: read.ok,
              rows: read.value.config.rows,
              speed: read.value.speed,
            },
            writeOk: write.ok,
            preservedTop: roundTrip.futureTopLevel,
            preservedConfig: roundTrip.config.futurePhysicsField,
            persistedSchema: roundTrip.schemaVersion,
            hasIntermediateState:
              roundTrip.histogram !== undefined || roundTrip.balls !== undefined ||
              roundTrip.queue !== undefined,
            realWriteOk: realWrite.ok,
            isolation,
          };
        }"""
    )

    assert result["key"] == "jpwealth_galton_preferences_v1"
    assert result["schema"] == 1
    assert result["malformed"]["ok"] is False and result["malformed"]["blocked"]
    assert result["malformed"]["hasError"] and result["malformed"]["rawPreserved"]
    assert result["malformed"]["rows"] == 10
    assert result["empty"] == {
        "ok": False, "blocked": True, "hasError": True, "rawPreserved": True
    }
    assert result["throwingGetter"] == {
        "unexpected": None,
        "read": {"ok": False, "blocked": True, "errorName": "SecurityError"},
        "write": {"ok": False, "errorName": "SecurityError"},
    }, result["throwingGetter"]
    assert result["invalidEnvelopes"] and all(
        item == {
            "blocked": True,
            "ok": False,
            "hasError": True,
            "rawPreserved": True,
        }
        for item in result["invalidEnvelopes"]
    ), result["invalidEnvelopes"]
    assert result["future"] == {
        "ok": False, "blocked": True, "hasError": True, "rawPreserved": True
    }
    assert result["quota"] == {"ok": False, "hasError": True}
    assert result["read"] == {"ok": True, "rows": 12, "speed": 2}
    assert result["writeOk"] and result["realWriteOk"]
    assert result["preservedTop"] == {"preservar": True}
    assert result["preservedConfig"] == {"unit": "JPW"}
    assert result["persistedSchema"] == 1
    assert result["hasIntermediateState"] is False
    assert all(result["isolation"].values()), result["isolation"]


def enter_galton(page):
    page.locator('#settingsMenu [data-settings-category="probability-lab"]').click()
    page.locator(
        '[data-settings-panel="probability-lab"] [data-nav-to="galton-board"]'
    ).click()
    page.locator('[data-settings-panel="galton-board"] [data-galton-root]').wait_for(
        state="visible"
    )
    page.wait_for_function(
        """() => document.querySelector('[data-galton-root]')?.__galtonController?.active === true"""
    )


def test_controller_recovery_guard(page):
    malformed = "{preferencias-galton-invalidas"
    page.evaluate(
        """value => localStorage.setItem(JPWGalton.persistence.STORAGE_KEY, value)""",
        malformed,
    )
    page.locator("#headerConfigBtn").click()
    enter_galton(page)
    page.locator('[data-galton-speed="2"]').click()
    assert page.evaluate(
        "localStorage.getItem(JPWGalton.persistence.STORAGE_KEY)"
    ) == malformed, "interacao comum nao pode sobrescrever preferencia ilegivel"
    assert page.locator("[data-galton-storage]").get_attribute("class").endswith("is-error")
    page.locator('[data-galton-action="restore-defaults"]').click()
    recovered = page.evaluate(
        "JSON.parse(localStorage.getItem(JPWGalton.persistence.STORAGE_KEY))"
    )
    assert recovered["schemaVersion"] == 1 and recovered["preset"] == "realistic"
    page.locator("#settingsCloseBtn").click()


def canvas_evidence(page):
    return page.evaluate(
        """() => {
          const canvas = document.querySelector('[data-galton-canvas]');
          const rect = canvas.getBoundingClientRect();
          const ctx = canvas.getContext('2d');
          const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
          let opaqueSamples = 0;
          const stride = Math.max(4, Math.floor(pixels.length / 5000 / 4) * 4);
          for (let index = 3; index < pixels.length; index += stride) {
            if (pixels[index] > 0) opaqueSamples += 1;
          }
          return {
            cssWidth: rect.width,
            cssHeight: rect.height,
            backingWidth: canvas.width,
            backingHeight: canvas.height,
            dpr: devicePixelRatio,
            opaqueSamples,
          };
        }"""
    )


def test_real_ui(page):
    page.locator("#headerConfigBtn").click()
    assert page.locator("#settingsOverlay").is_visible()
    enter_galton(page)
    assert page.locator("#settingsPageTitle").inner_text() == "Galton Board"
    assert page.locator("[data-galton-add]").count() == 4
    assert page.locator("[data-galton-speed]").count() == 4
    assert page.locator("[data-galton-canvas]").get_attribute("role") == "img"
    assert "Forex" in page.locator(".galton-disclaimer").inner_text()
    assert page.locator(".galton-info").count() >= 5
    assert page.locator('[data-galton-action="center"]').is_visible()
    assert page.locator('[data-galton-action="restore-defaults"]').is_visible()
    assert page.locator('[data-galton-action="restore-physics"]').count() == 1
    assert page.locator('[data-galton-pref="releasePoint"]').get_attribute("aria-label")
    assert page.locator('[data-galton-pref="tiltDegrees"]').get_attribute("aria-label")
    assert page.locator(".galton-table-wrap thead th").count() == 5

    # persist() tambem adquire o storage dentro da fronteira protegida.
    persist_security_error = page.evaluate(
        """() => {
          const descriptor=Object.getOwnPropertyDescriptor(window,'localStorage');
          const controller=document.querySelector('[data-galton-root]').__galtonController;
          let result=null,unexpected=null;
          try{
            Object.defineProperty(window,'localStorage',{configurable:true,
              get(){ throw new DOMException('acesso bloqueado','SecurityError'); }});
            result=controller.persist();
          }catch(error){ unexpected={name:error.name,message:error.message}; }
          finally{
            if(descriptor) Object.defineProperty(window,'localStorage',descriptor);
            else delete window.localStorage;
          }
          return {result,unexpected,status:document.querySelector('[data-galton-storage]').textContent};
        }"""
    )
    assert persist_security_error["result"] is False, persist_security_error
    assert persist_security_error["unexpected"] is None, persist_security_error
    assert "Não foi possível salvar" in persist_security_error["status"]

    # Operacao real por teclado: Enter/Space acionam os controles nativos.
    page.locator('[data-galton-add="1"]').focus()
    page.keyboard.press("Enter")
    assert page.locator("[data-galton-staged]").inner_text() == "1"
    page.locator('[data-galton-speed="2"]').focus()
    page.keyboard.press("Space")
    assert page.locator('[data-galton-speed="2"]').get_attribute("aria-pressed") == "true"
    page.locator('[data-galton-action="reset"]').focus()
    page.keyboard.press("Enter")
    assert page.locator("[data-galton-staged]").inner_text() == "0"

    # Epoch + hook impedem uma instancia antiga de ressuscitar preferencias apos wipe.
    wipe = page.evaluate(
        """() => {
          const root=document.querySelector('[data-galton-root]');
          const previous=root.__galtonController;
          const key=JPWGalton.persistence.STORAGE_KEY;
          localStorage.setItem(key, JSON.stringify({schemaVersion:1,preset:'realistic',
            showTheory:true,speed:4,releasePoint:.5,tiltDegrees:0,seed:9,config:{}}));
          window.JP_WEALTH_SESSION_WIPE_EPOCH=(Number(window.JP_WEALTH_SESSION_WIPE_EPOCH)||0)+1;
          localStorage.removeItem(key);
          const staleWrite=previous.persist();
          const replacement=window.handleGaltonSessionWipe();
          return {
            staleWrite,
            keyAbsent: localStorage.getItem(key)===null,
            previousDestroyed: previous.destroyed,
            replaced: replacement!==previous,
            active: replacement&&replacement.active,
            speed: replacement&&replacement.preferences.speed,
            releasePoint: replacement&&replacement.preferences.releasePoint,
          };
        }"""
    )
    assert wipe == {
        "staleWrite": False,
        "keyAbsent": True,
        "previousDestroyed": True,
        "replaced": True,
        "active": True,
        "speed": 1,
        "releasePoint": 0,
    }, wipe

    # Expiracoes de cleanup ficam visiveis e explicitamente fora do histograma.
    integrity = page.evaluate(
        """() => {
          const root=document.querySelector('[data-galton-root]');
          const controller=root.__galtonController;
          const snapshot=controller.snapshot();
          const expiredSnapshot={...snapshot,expiredCount:2,
            expiredByReason:{outside:1,maxAge:1}};
          controller.renderDOM(expiredSnapshot,true);
          const status=root.querySelector('[data-galton-integrity]');
          const observer=new MutationObserver(()=>{});
          observer.observe(status,{attributes:true,childList:true,characterData:true,subtree:true});
          controller.renderDOM(expiredSnapshot,true);
          controller.renderDOM(expiredSnapshot,true);
          const stableMutations=observer.takeRecords().length;
          observer.disconnect();
          const result={hidden:status.hidden,text:status.textContent,stableMutations};
          controller.renderDOM(snapshot,true);
          return result;
        }"""
    )
    assert integrity["hidden"] is False
    assert integrity["stableMutations"] == 0, integrity
    assert "2 bolas" in integrity["text"] and "não entram no histograma" in integrity["text"]

    # A live region so muda quando a faixa de orientacao estatistica muda.
    convergence_mutations = page.evaluate(
        """() => {
          const controller=document.querySelector('[data-galton-root]').__galtonController;
          const target=document.querySelector('[data-galton-convergence]');
          const observer=new MutationObserver(() => {});
          observer.observe(target,{childList:true,characterData:true,subtree:true});
          const snapshot=controller.snapshot();
          controller.renderDOM(snapshot,true);
          controller.renderDOM(snapshot,true);
          controller.renderDOM(snapshot,true);
          const count=observer.takeRecords().length;
          observer.disconnect();
          return count;
        }"""
    )
    assert convergence_mutations == 0, convergence_mutations

    canvas = canvas_evidence(page)
    assert canvas["cssWidth"] > 500 and canvas["cssHeight"] >= 320, canvas
    assert canvas["backingWidth"] >= canvas["cssWidth"] * canvas["dpr"] - 2, canvas
    assert canvas["backingHeight"] >= canvas["cssHeight"] * canvas["dpr"] - 2, canvas
    assert canvas["opaqueSamples"] > 20, canvas
    page.locator("[data-galton-canvas]").hover(
        position={"x": canvas["cssWidth"] / 2, "y": canvas["cssHeight"] - 35}
    )
    tooltip = page.locator("[data-galton-tooltip]")
    assert tooltip.is_visible()
    assert all(term in tooltip.inner_text() for term in ("Observações", "Empírico", "Teórico", "Δ"))

    # O emissor superior aceita clique para soltar uma unica bola, sem escolher bin.
    page.locator("[data-galton-canvas]").click(position={"x": canvas["cssWidth"] / 2, "y": 20})
    page.wait_for_function(
        """() => document.querySelector('[data-galton-root]').__galtonController.snapshot().spawnedCount === 1"""
    )
    page.locator('[data-galton-action="reset"]').click()

    # Centralizar e restaurar fisica sao distintos de Reset (que preserva config).
    page.locator('[data-galton-pref="releasePoint"]').fill("0.5")
    page.locator('[data-galton-pref="tiltDegrees"]').fill("1")
    page.locator('[data-galton-action="center"]').click()
    centered = page.evaluate(
        """() => document.querySelector('[data-galton-root]').__galtonController.snapshot()"""
    )
    assert centered["releasePoint"] == 0 and centered["tiltDegrees"] == 0
    page.locator("[data-galton-advanced] summary").click()
    page.locator('[data-galton-config="pegTolerance"]').fill("0.04")
    page.locator('[data-galton-config="pegTolerance"]').press("Tab")
    assert_close(
        float(page.locator('[data-galton-config="pegTolerance"]').input_value()),
        0.0225,
        label="controle sincronizado apos clamp relacional",
    )
    page.locator('[data-galton-config="rows"]').fill("12")
    page.locator('[data-galton-action="restore-physics"]').click()
    assert page.evaluate(
        "document.querySelector('[data-galton-root]').__galtonController.snapshot().config.rows"
    ) == 10

    # Controles reais: fila, execucao, pausa e velocidade nao recriam o motor.
    page.locator('[data-galton-add="10"]').click()
    assert page.locator("[data-galton-staged]").inner_text() == "10"
    page.locator('[data-galton-speed="4"]').click()
    assert page.locator('[data-galton-speed="4"]').get_attribute("aria-pressed") == "true"
    page.locator('[data-galton-action="execute"]').click()
    page.wait_for_function(
        """() => document.querySelector('[data-galton-root]').__galtonController
          .snapshot().spawnedCount > 0"""
    )
    running = page.evaluate(
        """() => document.querySelector('[data-galton-root]').__galtonController.snapshot()"""
    )
    assert running["running"] and running["spawnedCount"] > 0
    assert page.locator('[data-galton-action="pause"]').inner_text() == "Pausar"
    page.locator('[data-galton-action="pause"]').click()
    paused = page.evaluate(
        """() => document.querySelector('[data-galton-root]').__galtonController.snapshot()"""
    )
    assert paused["paused"]
    page.locator('[data-galton-action="pause"]').click()

    # Tabela DOM equivalente ao canvas e preferencia de movimento reduzido.
    rows = page.evaluate(
        """() => ({
          expected: document.querySelector('[data-galton-root]').__galtonController
            .snapshot().config.rows + 1,
          actual: document.querySelectorAll('[data-galton-bins] tr').length,
          focusable: [...document.querySelectorAll('[data-galton-bins] tr')]
            .every(row => row.tabIndex === 0),
          transition: getComputedStyle(document.querySelector('[data-galton-add="1"]'))
            .transitionDuration,
          animation: getComputedStyle(document.querySelector('[data-galton-add="1"]'))
            .animationName,
        })"""
    )
    assert rows["actual"] == rows["expected"] and rows["focusable"], rows
    assert rows["transition"] in ("0s", "0s, 0s") and rows["animation"] == "none", rows

    # Tema claro/escuro redesenha sem apagar o canvas.
    themes = page.evaluate(
        """() => {
          const root = document.documentElement;
          const stage = document.querySelector('.galton-stage');
          const controller = document.querySelector('[data-galton-root]').__galtonController;
          const previous = root.dataset.theme;
          root.dataset.theme = 'light'; controller.redraw();
          const light = getComputedStyle(stage).backgroundColor;
          root.dataset.theme = 'dark'; controller.redraw();
          const dark = getComputedStyle(stage).backgroundColor;
          root.dataset.theme = previous || 'dark'; controller.redraw();
          return {light, dark};
        }"""
    )
    assert themes["light"] != themes["dark"], themes
    assert canvas_evidence(page)["opaqueSamples"] > 20

    # Painel oculto pausa RAF; retorno reutiliza a instancia; fechar destroi tudo.
    before_lifecycle = page.evaluate(
        """() => ({
          mounts: window.__galtonDebug.mounts,
        })"""
    )
    page.evaluate("activateSettingsCategory('general')")
    lifecycle_hidden = page.evaluate(
        """() => {
          const controller = document.querySelector('[data-galton-root]').__galtonController;
          return {active: controller.active, raf: controller.raf,
            debugRaf: window.__galtonDebug.activeRaf,
            observers: window.__galtonDebug.resizeObservers};
        }"""
    )
    assert lifecycle_hidden == {"active": False, "raf": 0, "debugRaf": 0, "observers": 0}, lifecycle_hidden
    page.evaluate("activateSettingsCategory('galton-board')")
    reused = page.evaluate(
        """() => ({
          active: document.querySelector('[data-galton-root]').__galtonController.active,
          mounts: window.__galtonDebug.mounts,
        })"""
    )
    assert reused["active"] and reused["mounts"] == before_lifecycle["mounts"], reused

    page.locator('[data-galton-pref="releasePoint"]').fill("0.25")
    page.locator('[data-galton-pref="tiltDegrees"]').fill("0.5")
    page.locator('[data-galton-speed="2"]').click()
    expected_preferences = page.evaluate(
        """() => {
          const c=document.querySelector('[data-galton-root]').__galtonController;
          return {releasePoint:c.preferences.releasePoint,tiltDegrees:c.preferences.tiltDegrees,speed:c.preferences.speed};
        }"""
    )
    page.locator("#settingsCloseBtn").click()
    closed = page.evaluate(
        """() => ({
          controller: document.querySelector('[data-galton-root]').__galtonController,
          raf: window.__galtonDebug.activeRaf,
          observers: window.__galtonDebug.resizeObservers,
          mounts: window.__galtonDebug.mounts,
          destroys: window.__galtonDebug.destroys,
        })"""
    )
    assert closed["controller"] is None and closed["raf"] == 0 and closed["observers"] == 0, closed
    assert closed["mounts"] == closed["destroys"], closed

    # Reabrir nunca restaura bolas/resultados; preferencias continuam independentes.
    page.locator("#headerConfigBtn").click()
    enter_galton(page)
    reopened = page.evaluate(
        """() => document.querySelector('[data-galton-root]').__galtonController.snapshot()"""
    )
    assert reopened["settledCount"] == reopened["activeCount"] == reopened["queuedCount"] == 0
    assert reopened["releasePoint"] == expected_preferences["releasePoint"]
    assert reopened["tiltDegrees"] == expected_preferences["tiltDegrees"]
    assert reopened["speed"] == expected_preferences["speed"]
    page.locator("#settingsCloseBtn").click()

    # Geometria mobile: modal contido no viewport, sem overflow horizontal.
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator("#headerConfigBtn").click()
    enter_galton(page)
    mobile = page.evaluate(
        """() => {
          const modal = document.getElementById('settingsModal').getBoundingClientRect();
          const canvas = document.querySelector('[data-galton-canvas]').getBoundingClientRect();
          return {
            modal: {left: modal.left, top: modal.top, right: modal.right, bottom: modal.bottom},
            canvas: {left: canvas.left, right: canvas.right, width: canvas.width},
            viewport: {width: innerWidth, height: innerHeight},
            scrollWidth: document.documentElement.scrollWidth,
          };
        }"""
    )
    assert mobile["modal"]["left"] >= -1 and mobile["modal"]["top"] >= -1, mobile
    assert mobile["modal"]["right"] <= mobile["viewport"]["width"] + 1, mobile
    assert mobile["modal"]["bottom"] <= mobile["viewport"]["height"] + 1, mobile
    assert mobile["canvas"]["left"] >= -1 and mobile["canvas"]["right"] <= 391, mobile
    assert mobile["scrollWidth"] <= mobile["viewport"]["width"] + 1, mobile

    mobile_tooltip = page.evaluate(
        """() => {
          const root=document.querySelector('[data-galton-root]');
          const controller=root.__galtonController;
          controller.preferences.showTheory=false;
          const renderer=controller.renderer, tx=renderer.lastTransform;
          const count=renderer.binCount(renderer.lastSnapshot,tx.geometry);
          const bin=renderer.binScreenBounds(count-1,count,tx);
          const canvas=controller.canvas.getBoundingClientRect();
          controller.showBinTooltip({
            clientX:canvas.left+(bin.left+bin.right)/2,
            clientY:canvas.top+tx.floorY+20,
          });
          const stage=document.querySelector('.galton-stage').getBoundingClientRect();
          const tooltip=document.querySelector('[data-galton-tooltip]');
          const rect=tooltip.getBoundingClientRect();
          return {text:tooltip.textContent,hidden:tooltip.hidden,
            contained:rect.left>=stage.left-1&&rect.right<=stage.right+1&&
              rect.top>=stage.top-1&&rect.bottom<=stage.bottom+1};
        }"""
    )
    assert mobile_tooltip["hidden"] is False and mobile_tooltip["contained"], mobile_tooltip
    assert "Teórico —" in mobile_tooltip["text"] and "Δ —" in mobile_tooltip["text"]
    page.locator("#settingsCloseBtn").click()

    final_debug = page.evaluate("window.__galtonDebug")
    assert final_debug["activeRaf"] == 0 and final_debug["resizeObservers"] == 0, final_debug
    assert final_debug["mounts"] == final_debug["destroys"], final_debug

    # Nao tolera excecoes JS nem erros de console; requests externos foram mockados.
    errors = [item for item in page.jpwealth_observed["console"] if item[0] == "error"]
    assert not page.jpwealth_observed["pageerror"], page.jpwealth_observed
    assert not errors, {"console": errors, "failed": page.jpwealth_observed["failed"]}


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = prepare_page(browser, url)
            test_math_contract(page)
            test_physics_contract(page)
            test_persistence_contract(page)
            test_controller_recovery_guard(page)
            test_real_ui(page)
            page.jpwealth_context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    print(
        "GALTON BOARD PASS — geometria/configuracao, PRNG/estatistica, passo fixo e "
        "corpos rigidos deterministas, contabilizacao unica/remocao, persistencia "
        "isolada e UI real responsiva/acessivel/lifecycle verificados."
    )


if __name__ == "__main__":
    main()
