#!/usr/bin/env python3
"""Benchmark deterministico de 10.000 bolas para o Galton Board.

O tempo e informativo: o processo falha somente quando um invariante funcional
e violado (contagem, fila, corpos, limite ativo ou guarda de progresso). O
benchmark usa lotes de 500 e o passo fixo publico do motor; nao mede FPS/render.
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
TOTAL = 10_000
BATCH = 500
SEED = 20260811


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


def main():
    server, url = serve()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.add_init_script("window.__onbShown=true;")
            page.route(
                "**/api.frankfurter.dev/**",
                lambda route: route.fulfill(
                    status=200, content_type="application/json", body='{"rate":1}'
                ),
            )
            page.goto(url, wait_until="load")
            page.wait_for_function(
                "() => window.JPWGalton && JPWGalton.physics && JPWGalton.config"
            )
            report = page.evaluate(
                """({total, batch, seed}) => {
                  const config = {
                    ...JPWGalton.config.DEFAULTS,
                    rows: 10,
                    releaseRate: 120,
                    maxActiveBalls: 240,
                    maxQueue: 100000,
                    // O stress mede drenagem/contagem, nao o timeout de seguranca.
                    // Usa o teto validado para nao confundir uma trajetoria longa
                    // legitima com expiracao do harness.
                    maxBallAge: 120,
                    speed: 1,
                    ballCollisions: false,
                  };
                  const engine = JPWGalton.physics.createEngine({config, seed});
                  engine.start();
                  let submitted = 0;
                  let accepted = 0;
                  let fixedTicks = 0;
                  let outerIterations = 0;
                  let maxObservedByHarness = 0;
                  let snapshot = engine.snapshot();
                  const startedAt = performance.now();

                  // A fila e alimentada em lotes deterministas. O teto de corpos
                  // ativos pertence ao motor e e observado a cada bloco de 16 ticks.
                  while (outerIterations < 100000) {
                    if (submitted < total && snapshot.queuedCount <= batch) {
                      const requested = Math.min(batch, total - submitted);
                      const took = engine.enqueue(requested);
                      submitted += requested;
                      accepted += took;
                    }
                    snapshot = engine.tickFixed(16);
                    fixedTicks += 16;
                    outerIterations += 1;
                    maxObservedByHarness = Math.max(
                      maxObservedByHarness, snapshot.activeCount,
                      snapshot.maxActiveObserved
                    );
                    if (submitted === total && snapshot.idle) break;
                  }

                  const elapsedMs = performance.now() - startedAt;
                  const histogramTotal = snapshot.histogram.reduce(
                    (sum, value) => sum + value, 0
                  );
                  const descriptive = JPWGalton.statistics.describeHistogram(snapshot.histogram);
                  const comparison = JPWGalton.statistics.compareToBinomial(snapshot.histogram, 0.5);
                  const mirrorL1 = histogramTotal ? snapshot.histogram.reduce((sum, value, index) =>
                    sum + Math.abs(value - snapshot.histogram[snapshot.histogram.length - 1 - index]), 0
                  ) / (2 * histogramTotal) : null;
                  const result = {
                    seed,
                    requested: total,
                    batchSize: batch,
                    submitted,
                    accepted,
                    elapsedMs,
                    ballsPerSecond: elapsedMs > 0 ? total / (elapsedMs / 1000) : null,
                    fixedTicks,
                    outerIterations,
                    simulatedSeconds: snapshot.simulatedTime,
                    histogram: snapshot.histogram,
                    histogramTotal,
                    settledCount: snapshot.settledCount,
                    expiredCount: snapshot.expiredCount,
                    rejectedCount: snapshot.rejectedCount,
                    activeCount: snapshot.activeCount,
                    queuedCount: snapshot.queuedCount,
                    idle: snapshot.idle,
                    bodyCount: snapshot.bodyCount,
                    maxActiveConfigured: snapshot.config.maxActiveBalls,
                    maxActiveObserved: snapshot.maxActiveObserved,
                    maxObservedByHarness,
                    guardReached: outerIterations >= 100000,
                    qualitativeComparison: {
                      mean: descriptive.mean,
                      standardDeviation: descriptive.stdDev,
                      skewness: descriptive.skewness,
                      kurtosisExcess: descriptive.kurtosis,
                      totalVariationVsBinomial: comparison.totalVariation,
                      rmseVsBinomial: comparison.rmse,
                      mirrorL1,
                    },
                  };
                  engine.destroy();
                  return result;
                }""",
                {"total": TOTAL, "batch": BATCH, "seed": SEED},
            )
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    invariants = {
        "all_requests_accepted": report["submitted"] == report["accepted"] == TOTAL,
        "all_balls_settled": report["settledCount"] == report["histogramTotal"] == TOTAL,
        "no_expiration_or_rejection": report["expiredCount"] == report["rejectedCount"] == 0,
        "idle_without_dynamic_bodies": (
            report["idle"]
            and report["activeCount"] == 0
            and report["queuedCount"] == 0
            and report["bodyCount"] == 1
        ),
        "active_body_bound": (
            report["maxActiveObserved"] <= report["maxActiveConfigured"]
            and report["maxObservedByHarness"] <= report["maxActiveConfigured"]
        ),
        "completed_before_guard": not report["guardReached"],
        "histogram_shape": len(report["histogram"]) == 11,
    }
    report["invariants"] = invariants
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    failed = [name for name, passed in invariants.items() if not passed]
    assert not failed, f"invariantes violados: {', '.join(failed)}"
    print(
        "GALTON BENCHMARK PASS — 10.000 bolas em lotes deterministicos; "
        "tempo apenas informativo e limite de corpos preservado."
    )
    comparison = report["qualitativeComparison"]
    print(
        "Comparacao qualitativa (nao e gate nem ajuste): "
        f"TV binomial={comparison['totalVariationVsBinomial']:.4f}, "
        f"assimetria={comparison['skewness']:.4f}, "
        f"L1 espelhado={comparison['mirrorL1']:.4f}."
    )


if __name__ == "__main__":
    main()
