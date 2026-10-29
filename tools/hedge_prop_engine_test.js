#!/usr/bin/env node
'use strict';
// Contract/oracles: BRIEF-HEDGE-PROP-20261027 and CHG-JPW-HEDGE-PROP-PRODUCT-20261027.
// Independent oracle: accumulated loss F * product(1 + targetPercent / drawdownPercent).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const sourcePath = path.resolve(__dirname, '../src/js/40-app/32-prop-firms/01-engine.js');
assert.ok(fs.existsSync(sourcePath), 'HEDGE-ENGINE-EXISTS: approved pure engine must exist');
const source = fs.readFileSync(sourcePath, 'utf8');
function load(withWindow, candidateSource) {
  const sandbox = {};
  ['document', 'localStorage', 'sessionStorage', 'fetch', 'XMLHttpRequest', 'S', 'navigator'].forEach(key => {
    Object.defineProperty(sandbox, key, { get() { throw Error('Forbidden effect: ' + key); } });
  });
  if (withWindow) sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(candidateSource, sandbox, { filename: sourcePath });
  return sandbox.JPWHedgeProp;
}
function close(actual, expected, label) {
  assert.equal(typeof actual, 'number', label);
  assert.ok(Number.isFinite(actual), label + ' finite');
  assert.ok(Math.abs(actual - expected) <= Math.max(1e-10, Math.abs(expected) * 1e-12), `${label}: ${actual} vs ${expected}`);
}
function fresh(overrides = {}) {
  return { nominalUSD: 200000, feeUSD: 1200, payoutPercent: 80, drawdownPercent: 7,
    targetsPercent: [10], refundUSD: 1200, ...overrides };
}
function outcome(result, id) { const row = result.outcomes.find(item => item.id === id); assert.ok(row, id); return row; }
function allFinite(value) {
  if (typeof value === 'number') assert.ok(Number.isFinite(value), 'no nonfinite result');
  else if (value && typeof value === 'object') Object.values(value).forEach(allFinite);
}
function freeze(value) { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; }

// Every candidate runs the same contract suite, input fixtures and assertions.
// VM copies isolate the mutations from production; an import/syntax error is not
// a rejected financial mutation. Mutation anchors must exist exactly once.
function runContractSuite(candidateSource, quiet = false) {
  const api = load(true, candidateSource);
  assert.equal(typeof api.calculate, 'function');
  assert.ok(Object.isFrozen(api), 'export is frozen');
  const calc = api.calculate;
  let count = 0;
  function test(id, fn) {
    try { fn(); } catch (error) { error.testId = id; throw error; }
    count += 1;
    if (!quiet) console.log('PASS ' + id);
  }
  function invalid(input, field, code) {
    const result = calc(input);
    assert.equal(result.ok, false);
    assert.equal(result.status, 'INVALID');
    assert.ok(result.errors.some(error => error.field === field && (!code || error.code === code)), JSON.stringify(result.errors));
    allFinite(result);
  }

  test('HEDGE-ORACLE-ONE-PHASE', () => {
    const r = calc(fresh());
    assert.equal(r.ok, true); assert.equal(r.status, 'VALID');
    close(r.drawdownUSD, 14000, 'drawdown');
    close(r.stages[0].targetUSD, 20000, 'target');
    close(r.stages[0].hedgeCapitalUSD, 12000 / 7, 'stage capital');
    close(r.stages[0].accumulatedLossUSD, 20400 / 7, 'accumulated loss');
    close(r.funded.hedgeRatio, 51 / 245, 'funded ratio');
    close(r.funded.targetUSD, 84000 / 29, 'funded target');
    close(r.funded.reserveUSD, 1205.911330049261, 'reserve');
    close(r.totals.hedgeCapitalUSD, 2920.197044334975, 'hedge total');
    close(r.totals.capitalIncludingFeeUSD, 4120.197044334975, 'budget');
    close(r.totals.multipleIncludingFee, 3.4334975369458125, 'multiple');
    ['evaluation-fail-0', 'funded-fail', 'funded-pass'].forEach(id => close(outcome(r, id).idealNetUSD, 0, id));
    close(outcome(r, 'funded-no-receipt').idealNetUSD, -20400 / 7 - 602.9556650246305, 'no receipt loss');
  });
  test('HEDGE-ORACLE-TWO-PHASES-AND-COST-PATHS', () => {
    const r = calc(fresh({ drawdownPercent: 10, targetsPercent: [10, 5], costs: [
      { passUSD: 20, failUSD: 10 }, { passUSD: 30, failUSD: 15 }, { passUSD: 40, failUSD: 20 }
    ] }));
    assert.equal(r.ok, true);
    close(r.stages[0].hedgeCapitalUSD, 1200, 'phase 1'); close(r.stages[1].hedgeCapitalUSD, 1200, 'phase 2');
    close(r.stages[1].targetUSD, 10000, 'nominal resets'); close(r.stages[1].accumulatedLossUSD, 3600, 'loss');
    close(r.funded.hedgeRatio, 0.18, 'ratio'); close(r.funded.targetUSD, 120000 / 31, 'target');
    close(r.funded.reserveUSD, 43200 / 31, 'reserve');
    close(r.totals.hedgeCapitalUSD, 117600 / 31, 'capital'); close(r.totals.capitalIncludingFeeUSD, 154800 / 31, 'budget');
    [['evaluation-fail-0', -10], ['evaluation-fail-1', -35], ['funded-fail', -70], ['funded-pass', -90]].forEach(([id, net]) => {
      const row = outcome(r, id); close(row.netAfterCostsUSD, net, id); assert.equal(row.costStatus, 'COMPLETE');
    });
    const noReceipt = outcome(r, 'funded-no-receipt');
    close(noReceipt.estimatedCostsUSD, 90, 'no receipt follows pass cost');
    close(noReceipt.netAfterCostsUSD, noReceipt.idealNetUSD - 90, 'no receipt net');
  });
  test('HEDGE-REFUND-ZERO', () => close(calc(fresh({ refundUSD: 0 })).funded.targetUSD, 142800 / 29, 'zero refund'));
  test('HEDGE-COSTS-DO-NOT-RESIZE', () => {
    const a = calc(fresh()); const b = calc(fresh({ costs: [{ passUSD: 1e9, failUSD: 1234 }, { passUSD: 5e8, failUSD: 5678 }] }));
    assert.equal(JSON.stringify(a.stages), JSON.stringify(b.stages));
    assert.equal(JSON.stringify(a.funded), JSON.stringify(b.funded)); assert.equal(JSON.stringify(a.totals), JSON.stringify(b.totals));
    a.outcomes.forEach((row, i) => close(row.idealNetUSD, b.outcomes[i].idealNetUSD, 'ideal unchanged'));
  });
  test('HEDGE-MISSING-COSTS-ARE-PENDING-PER-PATH', () => {
    const r = calc(fresh({ costs: [{ passUSD: null, failUSD: 0 }, { passUSD: 0, failUSD: 0 }] }));
    assert.equal(r.ok, true); assert.equal(outcome(r, 'evaluation-fail-0').costStatus, 'COMPLETE');
    r.outcomes.filter(row => row.id !== 'evaluation-fail-0').forEach(row => {
      assert.equal(row.costStatus, 'PENDING'); assert.equal(row.estimatedCostsUSD, null); assert.equal(row.netAfterCostsUSD, null);
    });
    [undefined, null, '', []].forEach(costs => calc(fresh({ costs })).outcomes.forEach(row => {
      assert.equal(row.costStatus, 'PENDING'); assert.equal(row.netAfterCostsUSD, null);
    }));
  });
  test('HEDGE-INVALID-COST-ONLY-AFFECTS-ITS-PATHS', () => {
    [-1, NaN, Infinity, '0', false, {}, []].forEach(value => {
      const r = calc(fresh({ costs: [{ passUSD: 0, failUSD: value }, { passUSD: 0, failUSD: 0 }] }));
      assert.equal(r.ok, true); assert.equal(r.errors.length, 0); assert.ok(r.costErrors.some(e => e.field === 'costs[0].failUSD'));
      assert.equal(outcome(r, 'evaluation-fail-0').costStatus, 'INVALID');
      assert.equal(outcome(r, 'evaluation-fail-0').netAfterCostsUSD, null);
      assert.equal(outcome(r, 'funded-pass').costStatus, 'COMPLETE');
    });
  });
  test('HEDGE-COST-TOPOLOGY-AND-EXTRA-ROWS', () => {
    [undefined, null, '', '  '].forEach(missing => {
      const r = calc(fresh({ targetsPercent: [10, 5], drawdownPercent: 10, costs: [
        { passUSD: 0, failUSD: 0 }, { passUSD: missing, failUSD: 0 }, { passUSD: 0, failUSD: 0 }
      ] }));
      assert.equal(outcome(r, 'evaluation-fail-0').costStatus, 'COMPLETE');
      assert.equal(outcome(r, 'evaluation-fail-1').costStatus, 'COMPLETE');
      assert.equal(outcome(r, 'funded-pass').costStatus, 'PENDING');
      assert.equal(outcome(r, 'funded-fail').costStatus, 'PENDING');
    });
    [false, 0, 'costs', {}, [{ passUSD: 0, failUSD: 0 }, { passUSD: 0, failUSD: 0 }, { passUSD: 0, failUSD: 0 }]].forEach(costs => {
      const r = calc(fresh({ costs })); assert.equal(r.ok, true); assert.ok(r.costErrors.length > 0);
      r.outcomes.forEach(row => { assert.equal(row.costStatus, 'INVALID'); assert.equal(row.netAfterCostsUSD, null); });
    });
  });
  test('HEDGE-ZERO-FEE-VALID-WITH-COSTS', () => {
    const r = calc(fresh({ feeUSD: 0, refundUSD: 0, costs: [{ passUSD: 3, failUSD: 2 }, { passUSD: 4, failUSD: 5 }] }));
    assert.equal(r.ok, true); close(r.funded.targetUSD, 0, 'target'); close(r.funded.reserveUSD, 0, 'reserve');
    close(r.totals.capitalIncludingFeeUSD, 0, 'budget'); assert.equal(r.totals.multipleIncludingFee, null);
    close(outcome(r, 'funded-pass').netAfterCostsUSD, -7, 'zero fee still has costs');
  });
  test('HEDGE-MISSING-STRICT-NUMBERS-AND-LIMITS', () => {
    ['nominalUSD', 'feeUSD', 'payoutPercent', 'drawdownPercent', 'refundUSD'].forEach(field => {
      [undefined, null, '', '  '].forEach(value => invalid(fresh({ [field]: value }), field, 'MISSING'));
      ['200000', true, false, NaN, Infinity, -Infinity, {}, []].forEach(value => invalid(fresh({ [field]: value }), field, 'INVALID_NUMBER'));
    });
    invalid(null, 'input', 'MISSING'); invalid({}, 'nominalUSD', 'MISSING');
    invalid(fresh({ nominalUSD: 0 }), 'nominalUSD'); invalid(fresh({ nominalUSD: -1 }), 'nominalUSD');
    invalid(fresh({ feeUSD: -1 }), 'feeUSD'); invalid(fresh({ refundUSD: -1 }), 'refundUSD');
    invalid(fresh({ refundUSD: 1201 }), 'refundUSD'); invalid(fresh({ feeUSD: 0 }), 'refundUSD');
    ['payoutPercent', 'drawdownPercent'].forEach(field => [0, -1, 100.1].forEach(value => invalid(fresh({ [field]: value }), field)));
    [undefined, null, ''].forEach(value => invalid(fresh({ targetsPercent: value }), 'targetsPercent', 'MISSING'));
    [[], [1, 2, 3], '10', {}].forEach(value => invalid(fresh({ targetsPercent: value }), 'targetsPercent'));
    [0, -1, null, undefined, '', '10', true, NaN, Infinity].forEach(value => invalid(fresh({ targetsPercent: [value] }), 'targetsPercent[0]'));
    assert.equal(calc(fresh({ payoutPercent: 100, drawdownPercent: 100, targetsPercent: [150] })).ok, true);
  });
  test('HEDGE-INFEASIBLE-NO-INFINITE-OR-NEGATIVE-TARGET', () => {
    [18, 1].forEach(payoutPercent => {
      const r = calc(fresh({ drawdownPercent: 10, payoutPercent, targetsPercent: [10, 5] }));
      assert.equal(r.ok, false); assert.equal(r.status, 'INFEASIBLE'); assert.equal(r.funded.targetUSD, null); allFinite(r);
    });
    const boundary = calc(fresh({ nominalUSD: 1000, feeUSD: 10, drawdownPercent: 10, targetsPercent: [10], payoutPercent: 20, refundUSD: 10 }));
    assert.equal(boundary.status, 'INFEASIBLE');
  });
  test('HEDGE-UNREPRESENTABLE-IS-EXPLICIT', () => {
    [fresh({ nominalUSD: Number.MIN_VALUE }), fresh({ feeUSD: Number.MAX_VALUE, refundUSD: 0 }),
      fresh({ drawdownPercent: Number.MIN_VALUE }), fresh({ nominalUSD: Number.MAX_VALUE, targetsPercent: [200] })].forEach(input => {
      const r = calc(input); assert.equal(r.ok, false); assert.equal(r.status, 'UNREPRESENTABLE'); allFinite(r);
    });
  });
  test('HEDGE-UNREPRESENTABLE-PAYOUT-FIELD', () => {
    const r = calc(fresh({ payoutPercent: Number.MIN_VALUE }));
    assert.equal(r.status, 'UNREPRESENTABLE'); assert.equal(r.errors[0].field, 'payoutPercent');
  });
  test('HEDGE-COST-OVERFLOW-DOES-NOT-POISON-IDEAL', () => {
    const r = calc(fresh({ costs: [{ passUSD: Number.MAX_VALUE, failUSD: 0 }, { passUSD: Number.MAX_VALUE, failUSD: 0 }] }));
    assert.equal(r.ok, true); assert.equal(outcome(r, 'funded-pass').costStatus, 'INVALID'); allFinite(r);
  });
  test('HEDGE-ALGEBRAIC-REFERENCE-PERMUTATIONS-AND-SCALING', () => {
    for (const targets of [[6], [12], [6, 4], [4, 6], [1.5, 3.25]]) for (const scale of [0.1, 1, 7]) {
      const input = fresh({ nominalUSD: 100000 * scale, feeUSD: 200 * scale, refundUSD: 100 * scale, drawdownPercent: 8, targetsPercent: targets });
      const r = calc(input); assert.equal(r.ok, true);
      const loss = input.feeUSD * targets.reduce((factor, target) => factor * (1 + target / 8), 1);
      const ratio = loss / (input.nominalUSD * 0.08);
      const fundedTarget = (loss - input.refundUSD) / (0.8 - ratio);
      close(r.stages.at(-1).accumulatedLossUSD, loss, 'product oracle'); close(r.funded.targetUSD, fundedTarget, 'funded oracle');
      close(r.totals.hedgeCapitalUSD, loss - input.feeUSD + 2 * ratio * fundedTarget, 'capital oracle');
      allFinite(r);
    }
  });
  test('HEDGE-PURE-FROZEN-INPUT-AND-NO-DOM-STORAGE-NETWORK', () => {
    const input = freeze(fresh({ costs: [{ passUSD: 0, failUSD: 0 }, { passUSD: 0, failUSD: 0 }] }));
    const before = JSON.stringify(input); const a = calc(input); const b = calc(input);
    assert.equal(JSON.stringify(input), before); assert.equal(JSON.stringify(a), JSON.stringify(b));
    const globalApi = load(false, candidateSource); assert.ok(Object.isFrozen(globalApi)); assert.equal(globalApi.calculate(input).ok, true);
  });

  return count;
}
const count = runContractSuite(source);
const counterproofs = [
  { id: 'HEDGE-MUTANT-FEE-OMITTED-FROM-BUDGET', edits: [
    ['const budget = fee + hedgeCapital;', 'const budget = hedgeCapital;']
  ], expectedTest: 'HEDGE-ORACLE-ONE-PHASE' },
  { id: 'HEDGE-MUTANT-REFUND-PRESUMED', edits: [
    ['(loss - input.refundUSD) / (payout - fundedRatio)', '(loss - fee) / (payout - fundedRatio)']
  ], expectedTest: 'HEDGE-REFUND-ZERO' },
  { id: 'HEDGE-MUTANT-RATIO-ROUNDED-TWO-DIGITS', edits: [
    ['const ratio = loss / drawdown;', 'const ratio = Math.round(loss / drawdown * 100) / 100;'],
    ['const fundedRatio = loss / drawdown;', 'const fundedRatio = Math.round(loss / drawdown * 100) / 100;']
  ], expectedTest: 'HEDGE-ORACLE-ONE-PHASE' },
  { id: 'HEDGE-MUTANT-COSTS-COUNTED-TWICE', edits: [
    ['net = idealNet - total;', 'net = idealNet - 2 * total;']
  ], expectedTest: 'HEDGE-ORACLE-TWO-PHASES-AND-COST-PATHS' }
];
const rejectionResults = counterproofs.map(proof => {
  let mutantSource = source;
  proof.edits.forEach(([before, after]) => {
    assert.equal(mutantSource.split(before).length - 1, 1, proof.id + ': unique mutation anchor required');
    mutantSource = mutantSource.replace(before, after);
  });
  assert.notEqual(mutantSource, source, proof.id + ': candidate must actually change');
  // Loading is outside assert.throws, so a broken VM/import cannot count as RED.
  const mutantApi = load(true, mutantSource);
  assert.equal(typeof mutantApi.calculate, 'function', proof.id + ': runnable candidate required');
  let rejection;
  assert.throws(() => runContractSuite(mutantSource, true), error => {
    assert.equal(error.code, 'ERR_ASSERTION', proof.id + ': contract assertion must reject');
    assert.equal(error.testId, proof.expectedTest, proof.id + ': expected independent oracle must reject');
    rejection = { testId: error.testId, message: error.message, actual: error.actual, expected: error.expected };
    return true;
  }, proof.id + ': financial defect must fail the unchanged suite');
  console.log('PASS ' + proof.id + ' rejected by ' + rejection.testId);
  return { id: proof.id, result: 'PASS', mutantResult: 'PRODUCT_FAIL', engineEdited: false,
    candidateSha256: crypto.createHash('sha256').update(mutantSource).digest('hex'), edits: proof.edits, rejection };
});
// The original must still pass after all isolated mutations; no state leaks.
assert.equal(runContractSuite(source, true), count, 'original suite passes after counterproofs');
const receipt = {
  timestampUTC: new Date().toISOString(), result: 'PASS', originalCases: count,
  rejectedMutants: rejectionResults.length, originalAfterMutations: 'PASS',
  command: process.execPath + ' tools/hedge_prop_engine_test.js', runtime: process.version,
  scope: 'Pure engine contracts in isolated VMs; synthetic data; same suite and assertions for original/mutants',
  engineSha256: crypto.createHash('sha256').update(source).digest('hex'),
  testSha256: crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),
  counterproofs: rejectionResults
};
const receiptPath = path.resolve(__dirname, '../docs/validation/hedge-prop-20261027/engine-counterproofs.json');
fs.writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + '\n');
console.log(`HEDGE PROP ENGINE: ${count}/${count} PASS; COUNTERPROOFS ${rejectionResults.length}/${counterproofs.length} PASS`);
