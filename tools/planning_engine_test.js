#!/usr/bin/env node
'use strict';
// Approved decision: docs/decisions/2026-10-20-planning-reference.md.
// Synthetic USD inputs only. Each expected amount below comes from opening
// balance interest and end-of-month flows, independently of engine helpers.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const file = path.join(root, 'src/js/30-accounting/06-planning/01-engine.js');
const context = { window: {} };
vm.createContext(context);
if (fs.existsSync(file)) vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: file });
assert.ok(context.window.JPWPlanning && context.window.JPWPlanning.engine,
  'PLN-ENGINE-EXPORT: pure planning engine must be exported');
const E = context.window.JPWPlanning.engine;
let count = 0;
function test(id, fn) { fn(); count++; console.log('PASS ' + id); }
function near(actual, expected, label = 'amount') {
  assert.equal(typeof actual, 'number', label);
  assert.ok(Math.abs(actual - expected) <= Math.max(1e-8, Math.abs(expected) * 1e-12), `${label}: ${actual} != ${expected}`);
}
function config(overrides = {}) {
  return Object.assign({ startMonth: '2026-01', initialUsd: 1000, profileId: 'base', monthlyContributionUsd: 100,
    goals: { adequate: null, ideal: { value: 30, currency: 'USD' } } }, overrides);
}
function plan(overrides = {}) { return E.createPlan(config(overrides), { id: 'p1', now: '2026-01-15T12:00:00.000Z' }); }
function account(p = plan(), id = 'a1') { return { id, name: id, broker: '', login: '', server: '', active: true, plan: p }; }
function envelope(accounts = []) { return { schemaVersion: 1, revision: 0, accounts, archive: [], audit: [], operations: [] }; }
function close(p, month, usd, quote) { p.results[month] = { usd, revision: 1, recordedAt: '2026-02-01T00:00:00Z' };
  p.closures[month] = { confirmed: true, confirmFlows: true, revision: 1, confirmedAt: '2026-02-01T00:00:00Z' };
  if (quote) p.closures[month].fxQuote = quote;
}
const quote = { rate: 5, referenceDate: '2026-01-15', fetchedAt: '2026-01-15T12:00:00Z', source: 'synthetic' };

test('PLN-01 profiles are hypothetical with approved monthly rates and annual products', () => {
  assert.equal(E.profiles.length, 4);
  for (const [id, rate, mdd] of [['high-risk', .06, .4], ['base', .03, .2], ['conservative', .02, .13], ['safety', .015, .1]]) {
    const p = E.profiles.find(p => p.id === id); assert.ok(p); near(p.rate, rate); near(p.mdd, mdd); near(p.annualRate, (1 + rate) ** 12 - 1);
  }
});
test('PLN-02 calendar is strict and crosses years without local date shifts', () => {
  assert.equal(E.monthKey('2026-01'), '2026-01'); assert.equal(E.monthKey('2026-13'), '');
  assert.equal(E.monthKey(''), ''); assert.equal(E.monthKey(202601), '');
  assert.equal(E.addMonths('2026-12', 1), '2027-01'); assert.equal(E.addMonths('2026-01', -1), '2025-12');
  assert.throws(() => E.addMonths('2026-13', 1)); assert.throws(() => E.addMonths('2026-01', 1.5));
});
test('PLN-03 reference uses 120 months and opening interest, preserving full precision', () => {
  const p = plan(), rows = E.timeline(p, { month: '2025-12' });
  assert.equal(rows.length, 120); assert.equal(rows[119].month, '2035-12');
  near(rows[0].openUsd, 1000); near(rows[0].resultUsd, 30); near(rows[0].closeUsd, 1130);
  near(rows[1].openUsd, 1130); near(rows[1].resultUsd, 33.9); near(rows[1].closeUsd, 1263.9);
  near(rows[2].resultUsd, 37.917); assert.equal(rows[0].phase, 'projected');
  near(rows[119].closeUsd, 1000 * 1.03 ** 120 + 100 * (1.03 ** 120 - 1) / .03);
});
test('PLN-04 current planned contribution lasts through month end, past unrecorded forecasts expire', () => {
  const p = plan(), rows = E.timeline(p, { month: '2026-02' });
  assert.equal(rows[0].phase, 'pending'); assert.equal(rows[1].phase, 'current');
  near(rows[0].contributionUsd, 0); near(rows[1].contributionUsd, 100); near(rows[2].contributionUsd, 100);
  assert.equal(rows[1].contributionSource,'projected');assert.equal(rows[1].resultSource,'projected');
  near(E.timeline(p,{month:'2026-01'})[0].closeUsd,1130);
  assert.equal(E.account(account(p), { month: '2026-02' }).confirmed.balanceUsd, null);
});
test('PLN-05 explicit USD result is retained and its rate derives from opening before end flows', () => {
  const p = plan(); p.contributions.push({ id: 'c1', month: '2026-01', usd: 100, brl: 500, revision: 1 });
  p.withdrawals.push({ id: 'w1', month: '2026-01', usd: 20, brl: null, revision: 1 }); close(p, '2026-01', 50);
  const row = E.timeline(p, { month: '2026-02' })[0];
  near(row.resultUsd, 50); near(row.rate, .05); near(row.closeUsd, 1130); assert.equal(row.finalized, true);
  assert.equal(row.phase, 'confirmed'); assert.equal(row.closeBrl, null);
  const c = E.account(account(p), { month: '2026-02' }).confirmed;
  near(c.balanceUsd, 1130); near(c.initialUsd, 1000); near(c.contributionsUsd, 100); near(c.resultUsd, 50); near(c.withdrawalsUsd, 20);
  near(p.results['2026-01'].usd, 50);
});
test('PLN-06 confirmation is contiguous, never crosses gaps or accepts a stale closure', () => {
  const p = plan(); close(p, '2026-01', 0); close(p, '2026-03', 0);
  let a = E.account(account(p), { month: '2026-04' }); assert.equal(a.confirmedThrough, '2026-01'); assert.equal(a.rows[2].finalized, false);
  p.closures['2026-01'].confirmed = false; a = E.account(account(p), { month: '2026-04' }); assert.equal(a.confirmedThrough, null);
  close(p, '2026-01', 0); p.closures['2026-01'].confirmFlows = false;
  assert.equal(E.account(account(p), { month: '2026-04' }).confirmedThrough, null);
});
test('PLN-07 blank rates use provisional zero, invalid rates propagate unavailability', () => {
  const p = plan(); p.future['2026-02'] = { rate: '', contributionUsd: 100 };
  let rows = E.timeline(p, { month: '2026-01' }); near(rows[1].rate, 0); near(rows[1].resultUsd, 0); assert.equal(rows[1].provisional, true);
  p.future['2026-02'].rate = -1.01; rows = E.timeline(p, { month: '2026-01' });
  assert.equal(rows[1].closeUsd, null); assert.equal(rows[2].closeUsd, null); assert.ok(rows[1].issues.length);
  p.future['2026-02'].rate = -1; near(E.timeline(p, { month: '2026-01' })[1].closeUsd, 100);
});
test('PLN-08 zero base accepts zero result and rejects a nonzero USD result', () => {
  const p = plan({ initialUsd: 0, monthlyContributionUsd: 0 }); close(p, '2026-01', 0);
  let row = E.timeline(p, { month: '2026-02' })[0]; near(row.closeUsd, 0); near(row.rate, 0); assert.equal(row.finalized, true);
  p.results['2026-01'].usd = 1; row = E.timeline(p, { month: '2026-02' })[0]; assert.equal(row.closeUsd, null); assert.equal(row.finalized, false);
});
test('PLN-09 negative ending wealth and overflow never masquerade as an available amount', () => {
  const p = plan(); p.withdrawals.push({ id: 'w', month: '2026-01', usd: 1100, revision: 1 });
  let rows = E.timeline(p, { month: '2026-02' }); assert.equal(rows[0].closeUsd, null); assert.equal(rows[1].openUsd, null);
  p.withdrawals = []; p.future['2026-03'] = { rate: Number.MAX_VALUE, contributionUsd: 100 };
  rows = E.timeline(p, { month: '2026-02' }); assert.equal(rows[2].closeUsd, null);
});
test('PLN-10 BRL goal conversion rounds once, captured quote does not float with daily rate', () => {
  const p = plan({ goals: { ideal: { value: 100, currency: 'BRL', quote: Object.assign({}, quote, { rate: 5.13 }) } } });
  near(p.goals.ideal.usd, 19.49); const before = JSON.stringify(p.reference);
  E.account(account(p), { month: '2026-01', quote: Object.assign({}, quote, { rate: 8 }) }); assert.equal(JSON.stringify(p.reference), before);
  near(p.goals.ideal.quote.rate, 5.13);
});
test('PLN-11 goal is the first sufficient monthly result, not closing capital, with calendar remaining months', () => {
  const p = plan({ goals: { adequate: null, ideal: { value: 30.5, currency: 'USD' } } });
  const a = E.account(account(p), { month: '2026-01' });
  assert.equal(a.goals.ideal.month, '2026-02'); assert.equal(a.goals.ideal.referenceMonth, '2026-02');
  assert.equal(a.goals.ideal.remainingMonths, 1); assert.equal(a.goals.ideal.status, 'PROJECTED');
  near(a.goals.ideal.requiredCapitalUsd, 1016.67); assert.equal(a.goals.adequate.status, 'NOT_INFORMED');
});
test('PLN-12 changed goal suspends date delta and reference is immutable', () => {
  const p = plan({ goals: { ideal: { value: 33, currency: 'USD' } } }); const ref = JSON.stringify(p.reference);
  p.goals.ideal = { value: 45, currency: 'USD', usd: 45, quote: null };
  const a = E.account(account(p), { month: '2026-01' }); assert.equal(a.goals.ideal.goalChanged, true); assert.equal(a.goals.ideal.deltaMonths, null);
  assert.equal(JSON.stringify(p.reference), ref);
});
test('PLN-13 unreachable goal has no invented date after 120 months', () => {
  const p = plan({ initialUsd: 0, monthlyContributionUsd: 0, goals: { ideal: { value: 100, currency: 'USD' } } });
  const g = E.account(account(p), { month: '2026-01' }).goals.ideal;
  assert.equal(g.month, null); assert.equal(g.remainingMonths, null); assert.equal(g.status, 'NOT_REACHED');
});
test('PLN-14 historical threshold is achieved only in continuously confirmed history', () => {
  const p = plan(); let a = E.account(account(p), { month: '2026-03' }); assert.equal(a.goals.ideal.status, 'PROJECTED'); assert.equal(a.goals.ideal.waitingForClosure, true);
  close(p, '2026-01', 30); a = E.account(account(p), { month: '2026-03' }); assert.equal(a.goals.ideal.status, 'ACHIEVED');
});
test('PLN-15 acquisition average uses known BRL costs and discloses missing cost coverage', () => {
  const p = plan(); p.contributions.push({ id: 'c1', month: '2026-01', usd: 100, brl: 500, revision: 1 }, { id: 'c2', month: '2026-02', usd: 200, brl: 1100, revision: 1 }, { id: 'c3', month: '2026-02', usd: 100, brl: null, revision: 1 });
  const avg = E.account(account(p), { month: '2026-03' }).priceAverage;
  near(avg.rate, 1600 / 300); near(avg.knownUsd, 300); near(avg.totalUsd, 400); near(avg.coverage, .75);
});
test('PLN-16 FX snapshots remain fixed on confirmed rows and unavailable FX does not erase USD', () => {
  const p = plan(); close(p, '2026-01', 30, quote);
  const rows = E.timeline(p, { month: '2026-02', quote: Object.assign({}, quote, { rate: 6 }) });
  near(rows[0].fxRate, 5); near(rows[0].closeBrl, 5150); near(rows[1].fxRate, 6);
  delete p.closures['2026-01'].fxQuote;
  const noFx = E.timeline(p, { month: '2026-02', quote }); assert.equal(noFx[0].closeBrl, null); near(noFx[0].closeUsd, 1030);
});
test('PLN-17 empty aggregate, inactive accounts and account filter are explicit', () => {
  const empty = E.portfolio(envelope(), { month: '2026-01' }); assert.equal(empty.rows.length, 0); assert.equal(empty.confirmed.balanceUsd, null); assert.equal(empty.status, 'EMPTY');
  const a1 = account(), p2 = E.createPlan(config(), { id: 'p2', now: '2026-01-15' }), a2 = account(p2, 'a2'); a2.active = false;
  assert.equal(E.portfolio(envelope([a1, a2]), { month: '2026-01' }).accounts.length, 1);
  assert.equal(E.portfolio(envelope([a1, a2]), { month: '2026-01', accountId: 'a2' }).accounts.length, 1);
});
for (const [offset, total] of [[9, 129], [21, 141], [179, 299]]) test('PLN-18 union calendar ' + total + ' months carries ended balances and respects not-started accounts', () => {
  const p1 = plan({ initialUsd: 100, monthlyContributionUsd: 0 });
  const year = 2026 + Math.floor(offset / 12), month = offset % 12 + 1;
  const p2 = E.createPlan(config({ startMonth: year + '-' + String(month).padStart(2, '0'), initialUsd: 200, monthlyContributionUsd: 0 }), { id: 'p2', now: '2026-01-01' });
  const view = E.portfolio(envelope([account(p1), account(p2, 'a2')]), { month: '2025-12' });
  assert.equal(view.rows.length, total); near(view.rows[0].openUsd, 100);
  near(view.rows[offset].openUsd, (offset < 120 ? 100 * 1.03 ** offset : 100 * 1.03 ** 120) + 200);
  near(view.rows[total - 1].closeUsd, 100 * 1.03 ** 120 + 200 * 1.03 ** 120);
  assert.equal(view.confirmed.balanceUsd, null);
});
test('PLN-19 consolidated month rate weights opening balances, annual compounds monthly rates', () => {
  const p1 = plan({ initialUsd: 100, monthlyContributionUsd: 0 }), p2 = plan({ initialUsd: 300, profileId: 'high-risk', monthlyContributionUsd: 0 }); p2.id = 'p2'; p2.reference.planId = 'p2';
  const view = E.portfolio(envelope([account(p1), account(p2, 'a2')]), { month: '2025-12' });
  near(view.rows[0].rate, 21 / 400); const final = 100 * 1.03 ** 12 + 300 * 1.06 ** 12;
  near(view.annual[0].rate, final / 400 - 1);
});
test('PLN-20 consolidated actual never invents a balance for an unconfirmed participating account', () => {
  const p1 = plan(), p2 = plan(); p2.id = 'p2'; p2.reference.planId = 'p2'; close(p1, '2026-01', 30);
  let v = E.portfolio(envelope([account(p1), account(p2, 'a2')]), { month: '2026-02' }); assert.equal(v.confirmed.balanceUsd, null);
  close(p2, '2026-01', 20); v = E.portfolio(envelope([account(p1), account(p2, 'a2')]), { month: '2026-02' });
  near(v.confirmed.balanceUsd, 2050); assert.equal(v.confirmedThrough, '2026-01');
});
test('PLN-21 stop simulation preserves history, compares final wealth and saved contributions', () => {
  const p = plan({ initialUsd: 1000 }); close(p, '2026-01', 50); const before = JSON.stringify(p);
  const s = E.simulate(p, { month: '2026-01', stopAfter: '2026-01' });
  near(s.rows[0].closeUsd, 1050); near(s.baseRows[0].closeUsd, 1050);
  near(s.finalUsd, 1050 * 1.03 ** 119); near(s.baselineFinalUsd - s.finalUsd, 100 * (1.03 ** 119 - 1) / .03);
  near(s.savedContributionsUsd, 11900); near(s.effectUsd, s.finalUsd - s.baselineFinalUsd); near(s.effectRate, s.effectUsd / s.baselineFinalUsd);
  assert.equal(JSON.stringify(p), before); assert.ok(s.goals.ideal); assert.ok(s.baseGoals.ideal);
});
test('PLN-22 increase simulation applies only future planned contributions, retaining effective ledger', () => {
  const p = plan(); p.contributions.push({ id: 'c1', month: '2026-02', usd: 30, brl: 150, revision: 1 }); const before = JSON.stringify(p);
  const s = E.simulate(p, { month: '2026-01', increaseUsd: 50, fromMonth: '2026-02' });
  near(s.rows[0].contributionUsd, 100); near(s.rows[1].contributionUsd, 30); near(s.effectUsd, 50 * (1.03 ** 118 - 1) / .03);
  assert.equal(JSON.stringify(p), before);
});
test('PLN-23 envelope validation rejects malformed known fields, unknown versions and secret material without mutation', () => {
  const env = envelope([account()]); env.extra = { retained: ['future extension'] }; env.accounts[0].extra = { retained: true }; const before = JSON.stringify(env);
  assert.equal(E.validateEnvelope(env).length, 0); assert.equal(JSON.stringify(env), before);
  for (const alter of [e => e.schemaVersion = 2, e => e.revision = -1, e => e.accounts[0].plan.initialUsd = '', e => e.accounts[0].plan.future['2026-02'] = { rate: -1.01 }, e => e.accounts[0].password = 'synthetic', e => e.accounts.push(JSON.parse(JSON.stringify(e.accounts[0])))]) {
    const v = JSON.parse(before); alter(v); assert.ok(E.validateEnvelope(v).length, 'invalid envelope must block commands');
  }
});
test('PLN-24 native form accepts fractional-cent premises while rejecting blank, invalid and nonfinite entries', () => {
  // Original Formulario HTML step=any and montarReferenciaFormularioStoikus_.
  for (const fields of [{ initialUsd: '' }, { initialUsd: -1 }, { initialUsd: Infinity }, { monthlyContributionUsd: -1 }, { profileId: 'forex' }, { goals: { ideal: null } }, { goals: { ideal: { value: 30, currency: 'BRL' } } }]) assert.throws(() => plan(fields));
  const p=plan({initialUsd:1000.001,monthlyContributionUsd:.001});
  near(E.timeline(p,{month:p.startMonth})[0].closeUsd,1000.001*1.03+.001);
  assert.equal(E.validateEnvelope(envelope([account(p)])).length,0);
});
test('PLN-25 percentage simulation preserves fractional cents until presentation', () => {
  const p = plan({ monthlyContributionUsd: 33.33 }), s = E.simulate(p, { month: '2026-01', increasePct: 5 });
  near(s.rows[1].plannedContributionUsd, 34.9965); assert.equal(s.viable, true);
  near(s.effectUsd, 1.6665 * (1.03 ** 119 - 1) / .03);
});
test('PLN-26 malformed or future envelopes cannot expose a valid-looking numeric aggregate', () => {
  for (const value of [null, { schemaVersion: 2, accounts: [account()] }, envelope([{ id: 'broken', name: 'broken', active: true, plan: null }])]) {
    const view = E.portfolio(value, { month: '2026-01' }); assert.equal(view.status, 'INVALID'); assert.equal(view.confirmed.balanceUsd, null); assert.equal(view.rows.length, 0);
  }
});
test('PLN-27 invalid profile and invalid explicit reference month are refused, not provisional zero', () => {
  const p = plan(); p.profileId = 'unknown'; assert.equal(E.timeline(p, { month: '2026-01' })[0].closeUsd, null);
  assert.throws(() => E.timeline(plan(), { month: '2026-13' })); assert.throws(() => E.simulate(plan(), { month: '' }));
});
test('PLN-28 envelope validation rejects stale goal conversion and malformed core records', () => {
  for (const alter of [e => e.accounts[0].plan.goals.ideal.usd = 999,
    e => e.accounts[0].plan.results['2026-01'] = { usd: '0', revision: 1 },
    e => e.accounts[0].plan.closures['2026-01'] = { confirmed: true, revision: 1 },
    e => e.accounts[0].plan.future['2036-01'] = { rate: 0 },
    e => e.accounts[0].plan.contributions.push({ id: 'c', month: '2026-01', usd: 1, brl: 0, revision: 1 })]) {
    const v = envelope([account()]); alter(v); assert.ok(E.validateEnvelope(v).length);
  }
});
test('PLN-29 stop cannot rewrite recorded or continuously confirmed months', () => {
  const p = plan(); close(p, '2026-01', 30); close(p, '2026-02', 31);
  p.contributions.push({ id: 'c1', month: '2026-02', usd: 50, brl: 250, revision: 1 });
  const s = E.simulate(p, { month: '2026-03', stopAfter: '2026-03', increasePct: 25 });
  near(s.rows[1].contributionUsd, 50); near(s.rows[1].closeUsd, 1111); assert.equal(s.rows[1].finalized, true);
  near(s.rows[2].contributionUsd, 100); near(s.rows[3].contributionUsd, 0);
});
test('PLN-30 corrected zero flow annuls money while preserving its prior record', () => {
  const p = plan(), previous = { id: 'c1', month: '2026-01', usd: 50, brl: 250, revision: 1 };
  p.contributions.push({ id: 'c1', month: '2026-01', usd: 0, brl: 0, revision: 2, previous });
  const v = envelope([account(p)]); assert.equal(E.validateEnvelope(v).length, 0); near(E.timeline(p, { month: '2026-02' })[0].contributionUsd, 0);
  delete p.contributions[0].previous; assert.ok(E.validateEnvelope(v).length); assert.equal(E.timeline(p, { month: '2026-02' })[0].closeUsd, null);
});
test('PLN-31 restart archives retain complete validated historical plans', () => {
  const v = envelope([account()]); const old = plan(); old.id = 'old'; old.reference.planId = 'old';
  v.archive.push({ id: 'archive1', accountId: 'a1', reason: 'restartPlan', archivedAt: '2026-02-01T00:00:00Z', account: { id: 'a1', name: 'a1', broker: '', login: '', server: '', active: true }, plan: old });
  assert.equal(E.validateEnvelope(v).length, 0); v.archive[0].plan.initialUsd = '';
  assert.ok(E.validateEnvelope(v).length);
});
test('PLN-32 historical conversion uses matching historical month and never daily quote', () => {
  const p = plan(); const nowQuote = Object.assign({}, quote, { rate: 6, fetchedAt: 1790000000000 });
  let rows = E.timeline(p, { month: '2026-03', quote: nowQuote }); assert.equal(rows[0].closeBrl, null); near(rows[2].fxRate, 6);
  rows = E.timeline(p, { month: '2026-03', quote: nowQuote, historicalQuotes: { '2026-01': quote } }); near(rows[0].closeBrl, 5150); assert.equal(rows[1].closeBrl, null);
  close(p, '2026-01', 30, Object.assign({}, quote, { rate: 4 }));
  rows = E.timeline(p, { month: '2026-03', quote: nowQuote, historicalQuotes: { '2026-01': quote } }); near(rows[0].closeBrl, 4120);
});
test('PLN-33 consolidation preserves historical FX absence and available matching month', () => {
  const p = plan(), v = envelope([account(p)]);
  let rows = E.portfolio(v, { month: '2026-03', quote }).rows; assert.equal(rows[0].closeBrl, null);
  rows = E.portfolio(v, { month: '2026-03', quote, historicalQuotes: { '2026-01': quote } }).rows; near(rows[0].closeBrl, 5150); assert.equal(rows[1].closeBrl, null);
});
test('PLN-34 invalid confirmed gaps and corrupted immutable reference block envelope', () => {
  const p = plan(), v = envelope([account(p)]); close(p, '2026-02', 30); assert.ok(E.validateEnvelope(v).length);
  p.closures = {}; p.results = {}; p.reference.rows[1].closeUsd += 1; assert.ok(E.validateEnvelope(v).length);
});
test('PLN-35 final closure is retained but carrying known balances never manufactures new closures', () => {
  const p1 = plan({ monthlyContributionUsd: 0 });
  for (let i = 0; i < 120; i++) { const month = (2026 + Math.floor(i / 12)) + '-' + String(i % 12 + 1).padStart(2, '0'); close(p1, month, 0); }
  const a = E.account(account(p1), { month: '2036-12' }); assert.equal(a.confirmedThrough, '2035-12'); near(a.confirmed.balanceUsd, 1000);
  const p2 = E.createPlan(config({ startMonth: '2036-12', initialUsd: 200, monthlyContributionUsd: 0 }), { id: 'p2', now: '2026-01-01' }); close(p2, '2036-12', 10);
  // Original Formulario.verified.gs545–549 sets confirmado=0 after any
  // account's horizon. Carrying its last USD position creates no new closure.
  const v = E.portfolio(envelope([account(p1), account(p2, 'a2')]), { month: '2036-12' }); assert.equal(v.confirmedThrough, '2035-12'); near(v.confirmed.balanceUsd, 1000);
  near(v.rows[130].openUsd, 1000); near(v.rows[130].resultUsd, 0); near(v.confirmed.initialUsd, 1000);
  assert.equal(v.rows[131].finalized,false);near(v.rows[131].closeUsd,1210);
});
test('PLN-36 operation receipts preserve identity, confirmed result and captured base', () => {
  const v = envelope([account()]); const op = { id: 'o1', type: 'createAccount', accountId: 'a1', planId: 'p1', at: '2026-01-15T00:00:00Z', signature: 'synthetic',
    base: { epoch: 0, revision: 0, accountId: null, planId: null, planRevision: null }, result: { ok: true, status: 'CONFIRMED', errors: [], accountId: 'a1', planId: 'p1', revision: 1, operationId: 'o1' } };
  v.operations.push(op); assert.equal(E.validateEnvelope(v).length, 0);
  for (const alter of [o => o.result.operationId = 'other', o => o.result.status = 'UNKNOWN', o => o.base.revision = -1, o => o.signature = null]) {
    const copy = JSON.parse(JSON.stringify(v)); alter(copy.operations[0]); assert.ok(E.validateEnvelope(copy).length);
  }
  v.operations.push(JSON.parse(JSON.stringify(op))); assert.ok(E.validateEnvelope(v).length);
});
test('PLN-37 consolidated acquisition weights known USD across accounts and discloses global coverage', () => {
  const first=plan(),second=E.createPlan(config(),{id:'p2',now:'2026-01-15'});
  first.contributions.push({id:'c1',month:'2026-01',usd:100,brl:500,revision:1});
  second.contributions.push({id:'c2',month:'2026-02',usd:300,brl:1800,revision:1},{id:'c3',month:'2026-02',usd:100,brl:null,revision:1});
  const input=envelope([account(first),account(second,'a2')]),before=JSON.stringify(input);
  const avg=E.portfolio(input,{month:'2026-03'}).priceAverage;
  assert.ok(avg,'portfolio must expose the acquisition read model');
  near(avg.rate,5.75);near(avg.knownUsd,400);near(avg.totalUsd,500);near(avg.coverage,.8);
  assert.notEqual(avg.rate,5.5,'account averages must never be averaged without weights');
  near(E.portfolio(input,{month:'2026-03',accountId:'a1'}).priceAverage.rate,5);
  const empty=E.portfolio(envelope(),{month:'2026-03'}).priceAverage;
  assert.equal(empty.rate,null);assert.equal(empty.coverage,null);near(empty.totalUsd,0);near(empty.knownUsd,0);
  assert.equal(JSON.stringify(input),before);
});
test('PLN-38 ended-account carry through a future gap never extends confirmed dates or invents actuals', () => {
  const first=plan({startMonth:'2016-01',initialUsd:1000,monthlyContributionUsd:0});
  for(let i=0;i<120;i++)close(first,(2016+Math.floor(i/12))+'-'+String(i%12+1).padStart(2,'0'),0);
  const second=E.createPlan(config({startMonth:'2030-01',initialUsd:200,monthlyContributionUsd:0}),{id:'p2',now:'2026-01-15'});
  const v=E.portfolio(envelope([account(first),account(second,'a2')]),{month:'2026-10'});
  assert.equal(v.confirmedThrough,'2025-12');near(v.confirmed.balanceUsd,1000);
  for(const row of v.rows.filter(r=>r.month>'2025-12'))assert.equal(row.finalized,false,row.month+' must not be a fabricated closure');
  const future=v.rows.find(r=>r.month==='2029-12');near(future.closeUsd,1000);near(future.resultUsd,0);assert.equal(future.phase,'projected');
});
test('PLN-39 current forecasts never duplicate actual contributions and closure uses only recorded flows', () => {
  const p=plan();p.results['2026-01']={usd:30,revision:1,recordedAt:'2026-01-15T00:00:00Z'};
  let row=E.timeline(p,{month:'2026-01'})[0];near(row.contributionUsd,100);near(row.actualContributionUsd,0);near(row.closeUsd,1130);assert.equal(row.finalized,false);
  assert.equal(row.resultSource,'recorded');assert.equal(row.contributionSource,'projected');
  p.contributions.push({id:'c1',month:'2026-01',usd:40,brl:200,revision:1});
  row=E.timeline(p,{month:'2026-01'})[0];near(row.plannedContributionUsd,100);near(row.actualContributionUsd,40);near(row.contributionUsd,40);near(row.closeUsd,1070);
  assert.equal(row.resultSource,'recorded');assert.equal(row.contributionSource,'recorded');
  close(p,'2026-01',30);row=E.timeline(p,{month:'2026-01'})[0];near(row.contributionUsd,40);near(row.closeUsd,1070);assert.equal(row.finalized,true);
  p.contributions=[];row=E.timeline(p,{month:'2026-01'})[0];near(row.contributionUsd,0);near(row.closeUsd,1030);assert.equal(row.finalized,true);
});
test('PLN-40 nested secret keys block every schema version without exposing or changing their values', () => {
  for(const key of ['password','passwd','senha','apiKey','api_key','api-key','private_key','authorization','access_token','clientSecret'])for(const version of [1,9]){
    const v=envelope([account()]);v.schemaVersion=version;v.futureExtension={nested:{[key]:'SYNTHETIC_SECRET_CANARY_NEVER_PRINT'}};const before=JSON.stringify(v);
    const errors=E.validateEnvelope(v);assert.ok(errors.some(e=>e.includes('segredo')),'secret key '+key+' must block');
    assert.ok(!errors.join(' ').includes('SYNTHETIC_SECRET_CANARY_NEVER_PRINT'));assert.equal(JSON.stringify(v),before);
  }
});
test('PLN-41 existing-plan stop preview rejects past dates and matches the applied next-month boundary', () => {
  const p=plan(),before=JSON.stringify(p);
  assert.throws(()=>E.simulate(p,{month:'2026-10',stopAfter:'2026-09'}),/parada|atual/i);
  const result=E.simulate(p,{month:'2026-10',stopAfter:'2026-10'}),applied=JSON.parse(before);applied.stopAfter='2026-10';
  near(result.rows[9].contributionUsd,100);near(result.rows[10].contributionUsd,0);
  const actual=E.timeline(applied,{month:'2026-10'});
  assert.deepEqual(JSON.parse(JSON.stringify(result.rows)),JSON.parse(JSON.stringify(actual)));
  assert.equal(JSON.stringify(p),before);
  near(E.simulate(plan({startMonth:'2027-01'}),{month:'2026-10',stopAfter:'2026-12'}).rows[0].contributionUsd,0);
  assert.equal(E.simulate(p,{month:'2036-01',stopAfter:'2035-12'}).effectUsd,0);
});
test('PLN-42 annual summaries retain provisional blank-rate coverage while explicit zero is definitive', () => {
  const p=plan();p.future['2026-02']={rate:null,contributionUsd:100};
  let view=E.account(account(p),{month:'2025-12'});assert.equal(view.annual[0].provisional,true);assert.equal(view.annual[1].provisional,false);
  near(view.annual[0].rate,1.03**11-1);
  assert.equal(E.portfolio(envelope([account(p)]),{month:'2025-12'}).annual[0].provisional,true);
  p.future['2026-02'].rate=0;view=E.account(account(p),{month:'2025-12'});assert.equal(view.annual[0].provisional,false);near(view.annual[0].rate,1.03**11-1);
});
test('PLN-43 stop bounds match native existing-plan calendar before start, current and after end', () => {
  const p=plan();assert.deepEqual(JSON.parse(JSON.stringify(E.stopBounds(p,{month:'2026-10'}))),{min:'2026-10',max:'2035-12'});
  assert.deepEqual(JSON.parse(JSON.stringify(E.stopBounds(p,{month:'2025-10'}))),{min:'2025-12',max:'2035-12'});
  assert.deepEqual(JSON.parse(JSON.stringify(E.stopBounds(p,{month:'2036-10'}))),{min:'2035-12',max:'2035-12'});
  assert.throws(()=>E.stopBounds(p,{month:'invalid'}));
});
test('PLN-44 stopping materializes only future zeros and later explicit edits override the marker', () => {
  const p=plan(),before=JSON.stringify(p);p.future['2026-12']={rate:.04,contributionUsd:300,extension:'keep'};
  const stopped=E.withContributionStop(p,{month:'2026-10',stopAfter:'2026-11'});
  assert.equal(stopped.stopAfter,'2026-11');near(stopped.future['2026-12'].contributionUsd,0);near(stopped.future['2026-12'].rate,.04);assert.equal(stopped.future['2026-12'].extension,'keep');
  assert.equal(p.stopAfter,null);assert.equal(Object.keys(p.future).length,1);assert.equal(JSON.stringify(p.reference),JSON.stringify(JSON.parse(before).reference));
  stopped.future['2026-12'].contributionUsd=200;near(E.timeline(stopped,{month:'2026-10'})[11].contributionUsd,200);
  const reapplied=E.withContributionStop(stopped,{month:'2026-10',stopAfter:'2026-11'});near(reapplied.future['2026-12'].contributionUsd,0);
  const later=E.withContributionStop(reapplied,{month:'2026-10',stopAfter:'2026-12'});near(later.future['2026-12'].contributionUsd,0);
  const sim=E.simulate(reapplied,{month:'2026-10',stopAfter:'2026-12'});
  assert.deepEqual(JSON.parse(JSON.stringify(sim.rows)),JSON.parse(JSON.stringify(E.timeline(later,{month:'2026-10'}))));
  const cleared=E.withContributionStop(later,{month:'2026-10',stopAfter:null});assert.equal(cleared.stopAfter,null);near(cleared.future['2026-12'].contributionUsd,0);
});
test('PLN-45 first viable stop meets the exact impact cap, including zero, 20 percent, 100 percent and no positive denominator', () => {
  const p=plan(),before=JSON.stringify(p);
  for(const [impactLimit,month] of [[0,'2035-12'],[.2,'2029-07'],[1,'2026-01']]){
    const found=E.findContributionStop(p,{month:'2026-01',impactLimit});assert.ok(found);assert.equal(found.stopAfter,month);assert.equal(found.impactLimit,impactLimit);assert.equal(found.result.withinImpactLimit,true);
    const total=1000*1.03**120+100*(1.03**120-1)/.03,n=(Number(month.slice(0,4))-2026)*12+Number(month.slice(5));
    const expectedImpact=100*(1.03**(120-n)-1)/.03/total;near(found.result.impactRate,expectedImpact);
    if(n>1&&impactLimit<1){const prior=100*(1.03**(121-n)-1)/.03/total;assert.ok(prior>impactLimit+1e-10);}
  }
  assert.equal(E.findContributionStop(plan({initialUsd:0,monthlyContributionUsd:0}),{month:'2026-01',impactLimit:1}),null);
  for(const impactLimit of [-.01,1.01,null,'0',Infinity])assert.throws(()=>E.findContributionStop(p,{month:'2026-01',impactLimit}));
  assert.equal(JSON.stringify(p),before);
});
test('PLN-46 manual stop preview exposes pure cap qualification and never counts retained future facts as savings', () => {
  const p=plan();p.contributions.push({id:'future-known',month:'2026-12',usd:30,brl:150,revision:1});
  const result=E.simulate(p,{month:'2026-10',stopAfter:'2026-10',impactLimit:0});
  //110 months follow October; December is an actual fact, leaving109 forecasts.
  assert.equal(result.withinImpactLimit,false);near(result.rows[11].contributionUsd,30);near(result.savedContributionsUsd,10900);
  const noCap=E.simulate(p,{month:'2026-10',stopAfter:'2026-10'});assert.equal(noCap.withinImpactLimit,null);assert.ok(noCap.impactRate>0);
});
test('PLN-47 configuration start range follows native 1900 through 2199 while month arithmetic stays generic', () => {
  assert.equal(E.startMonthRange.min,'1900-01');assert.equal(E.startMonthRange.max,'2199-12');
  assert.equal(plan({startMonth:'1900-01'}).startMonth,'1900-01');assert.equal(plan({startMonth:'2199-12'}).reference.rows[119].month,'2209-11');
  assert.throws(()=>plan({startMonth:'1899-12'}));assert.throws(()=>plan({startMonth:'2200-01'}));
  assert.equal(E.monthKey('0000-01'),'0000-01');assert.equal(E.addMonths('2199-12',120),'2209-12');
});

// Optional source oracle: evaluate the original pure functions only. Platform
// APIs deliberately throw; invoking an Apps Script entry point cannot succeed.
if (process.argv.includes('--source-oracle')) {
  const dir = process.env.JPW_PLANNING_ORACLE_DIR || '/private/tmp/stoikus-auditoria-entrega-20261019/native';
  const sandbox = { SpreadsheetApp: new Proxy({}, { get() { throw Error('Platform call forbidden'); } }), Utilities: new Proxy({}, { get() { throw Error('Platform call forbidden'); } }) };
  vm.createContext(sandbox);
  for (const name of ['Prazos.gs', 'ParadaAportes.gs']) vm.runInContext(fs.readFileSync(path.join(dir, name), 'utf8'), sandbox, { filename: name });
  test('PLN-ORACLE-01 original Prazos compares first monthly income and immutable goal', () => {
    const p = plan({ goals: { ideal: { value: 33, currency: 'USD' } } }), a = E.account(account(p), { month: '2025-12' });
    const original = sandbox.calcularComparativoRendaStoikus_({ capital: 1000, plano: p.id, fechados: 0, metas: { ideal: 33 }, meses: a.rows.map(r => ({ mes: r.month, taxa: r.rate, resultado: r.resultUsd, patrimonio: r.closeUsd })), base: { plano: p.id, metas: { ideal: 33 }, trajetoria: a.referenceRows.map(r => ({ mes: r.month, resultado: r.resultUsd, patrimonio: r.closeUsd })) } });
    assert.equal(original[1].atual, a.goals.ideal.month); assert.equal(original[1].inicial, a.goals.ideal.referenceMonth); assert.equal(original[1].delta, a.goals.ideal.deltaMonths);
  });
  test('PLN-ORACLE-02 original Parada computes equal final wealth and contribution opportunity effect', () => {
    const p = plan(), s = E.simulate(p, { month: '2025-12', stopAfter: '2028-12' });
    const original = sandbox.compararParadaAportesStoikus_({ inicial: 1000, fechados: 0, meses: s.baseRows.map(r => ({ mes: r.month, taxa: r.rate, aporte: r.contributionUsd, saque: r.withdrawalUsd, patrimonio: r.closeUsd })) }, 35);
    near(original.com, s.baselineFinalUsd); near(original.sem, s.finalUsd); near(original.diferenca, -s.effectUsd); near(original.impacto, -s.effectRate); near(original.dispensados, s.savedContributionsUsd);
  });
  test('PLN-ORACLE-03 original Parada finds the same earliest viable stop within each impact limit', () => {
    const p=plan(),rows=E.timeline(p,{month:'2026-01'});
    const input={inicial:1000,fechados:0,meses:rows.map(r=>({mes:r.month,taxa:r.rate,aporte:r.contributionUsd,saque:r.withdrawalUsd,patrimonio:r.closeUsd}))};
    for(const impactLimit of [0,.2,1]){
      const native=sandbox.encontrarParadaAportesStoikus_(input,impactLimit,0),found=E.findContributionStop(p,{month:'2026-01',impactLimit});
      assert.equal(found.stopAfter,rows[native.indice].month);near(found.result.finalUsd,native.sem);near(found.result.impactRate,native.impacto);near(found.result.savedContributionsUsd,native.dispensados);
    }
    const native=sandbox.encontrarParadaAportesStoikus_(input,1,-1),found=E.findContributionStop(p,{month:'2025-12',impactLimit:1});
    assert.equal(native.indice,-1);assert.equal(found.stopAfter,'2025-12');near(found.result.finalUsd,native.sem);near(found.result.impactRate,native.impacto);
  });
}
console.log(`planning_engine_test: ${count} cases PASS`);
