(function (window) {
  'use strict';
  var ns = window.JPWTimeTwins = window.JPWTimeTwins || {};
  var limits = Object.freeze({ maxMonths: 360, maxInitial: 1000000, maxContribution: 100000, maxAnnualRate: .20 });

  function object(value, label) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new TypeError(label + ' deve ser um objeto.');
  }
  function number(value, min, max, label, integer) {
    if (typeof value !== 'number' || !Number.isFinite(value)) throw new TypeError(label + ' deve ser um número finito.');
    if ((integer && !Number.isInteger(value)) || value < min || value > max) throw new RangeError(label + ' fora dos limites permitidos: ' + min + ' a ' + max + '.');
    return value;
  }
  function actor(id) {
    if (id !== 'A' && id !== 'B') throw new RangeError('O investidor deve ser A ou B.');
    return id;
  }
  function validate(input) {
    object(input, 'O cenário');
    var copy = {
      id: actor(input.id),
      initialCapital: number(input.initialCapital, 0, limits.maxInitial, 'O capital inicial'),
      annualRate: number(input.annualRate, 0, limits.maxAnnualRate, 'A taxa efetiva anual'),
      horizonMonths: number(input.horizonMonths, 1, limits.maxMonths, 'O prazo em meses', true),
      contributions: []
    };
    if (!Array.isArray(input.contributions)) throw new TypeError('Os aportes devem formar uma lista.');
    if (input.contributions.length > limits.maxMonths) throw new RangeError('São permitidos até 360 aportes por cenário.');
    for (var index = 0; index < input.contributions.length; index++) {
      if (!Object.prototype.hasOwnProperty.call(input.contributions, index)) throw new TypeError('A lista de aportes não pode conter posições ausentes.');
    }
    var ids = new Set();
    input.contributions.forEach(function (item) {
      object(item, 'O aporte');
      if (typeof item.id !== 'string' || !item.id.trim() || item.id === 'initial' || ids.has(item.id)) throw new RangeError('Cada aporte deve ter uma identidade única e não reservada.');
      ids.add(item.id);
      copy.contributions.push({ id: item.id, month: number(item.month, 1, copy.horizonMonths, 'O mês do aporte', true), amount: number(item.amount, 0, limits.maxContribution, 'O valor do aporte') });
    });
    return copy;
  }
  function periodic(options) {
    object(options, 'As opções');
    var id = actor(options.id);
    var initial = options.initialCapital === undefined ? 1000 : options.initialCapital;
    var annual = options.annualRate === undefined ? .06 : options.annualRate;
    var horizon = options.horizonMonths === undefined ? 240 : options.horizonMonths;
    number(horizon, 1, limits.maxMonths, 'O prazo em meses', true);
    var amount = options.monthlyContribution === undefined ? 100 : options.monthlyContribution;
    number(amount, 0, limits.maxContribution, 'O aporte mensal');
    var start = options.startMonth === undefined ? 1 : options.startMonth;
    var end = options.endMonth === undefined ? horizon : options.endMonth;
    number(start, 1, horizon, 'O primeiro mês de aporte', true);
    number(end, 0, horizon, 'O último mês de aporte', true);
    var contributions = [];
    if (amount > 0) for (var month = start; month <= end; month++) contributions.push({ id: id + '-month-' + month, month: month, amount: amount });
    return validate({ id: id, initialCapital: initial, annualRate: annual, horizonMonths: horizon, contributions: contributions });
  }
  // Cap only ratio drift from floating-point arithmetic; money is never rounded.
  function share(value, total) { return total === 0 ? null : Math.min(1, Math.max(0, value / total)); }
  function project(input) {
    var scenario = validate(input);
    var rate = Math.pow(1 + scenario.annualRate, 1 / 12) - 1;
    var deposits = new Array(scenario.horizonMonths + 1).fill(0);
    var scheduled = 0;
    scenario.contributions.forEach(function (c) { deposits[c.month] += c.amount; scheduled += c.amount; });
    var balance = scenario.initialCapital;
    var paid = 0;
    var total = balance;
    var snapshots = [{ month: 0, balance: balance, totalContributed: total, pendingContributions: scheduled, interestEarned: 0, cumulativeReturns: 0, contribution: 0 }];
    var crossover = null;
    for (var month = 1; month <= scenario.horizonMonths; month++) {
      var interest = balance * rate;
      balance += interest + deposits[month];
      paid += deposits[month];
      total = scenario.initialCapital + paid;
      if (crossover === null && deposits[month] > 0 && interest > deposits[month]) crossover = month;
      snapshots.push({ month: month, balance: balance, totalContributed: total, pendingContributions: scheduled - paid, interestEarned: interest, cumulativeReturns: balance - total, contribution: deposits[month] });
    }
    var principals = scenario.contributions.map(function (c) { return { id: c.id, month: c.month, amount: c.amount }; });
    if (scenario.initialCapital > 0) principals.unshift({ id: 'initial', month: 0, amount: scenario.initialCapital });
    var cohorts = principals.map(function (c) {
      var value = c.amount * Math.pow(1 + rate, scenario.horizonMonths - c.month);
      return { id: c.id, month: c.month, principal: c.amount, finalValue: value, returns: value - c.amount, share: share(value, balance) };
    });
    return { scenario: scenario, monthlyRate: rate, snapshots: snapshots, cohorts: cohorts, finalBalance: balance, totalScheduledContributions: scheduled, firstCrossoverMonth: crossover };
  }
  // Revalidate the explicit scenario, so inspectors also accept serialized projections
  // and never trust mutable cached totals supplied by a caller.
  function projection(value) {
    object(value, 'A projeção');
    return project(value.scenario);
  }
  function selected(p, id) {
    if (typeof id !== 'string') throw new TypeError('A identidade do aporte deve ser um texto.');
    var c = p.cohorts.find(function (entry) { return entry.id === id; });
    if (!c) throw new RangeError('A identidade do aporte não existe neste cenário.');
    return c;
  }
  function inspect(value, id, month) {
    var p = projection(value);
    var c = selected(p, id);
    number(month, 0, p.scenario.horizonMonths, 'O mês de inspeção', true);
    var active = month >= c.month;
    var current = active ? c.principal * Math.pow(1 + p.monthlyRate, month - c.month) : 0;
    return { id: c.id, month: c.month, atMonth: month, active: active, principal: c.principal, value: current, returns: active ? current - c.principal : 0, share: !active ? null : share(current, p.snapshots[month].balance), projectedValue: c.finalValue, projectedShare: c.share };
  }
  function trace(value, id) {
    var p = projection(value);
    var c = selected(p, id);
    var result = [];
    for (var month = c.month; month <= p.scenario.horizonMonths; month++) {
      var multiplier = Math.pow(1 + p.monthlyRate, month - c.month);
      result.push({ month: month, value: c.principal * multiplier, multiplier: multiplier });
    }
    return result;
  }
  function without(value, id) {
    var p = projection(value);
    var c = selected(p, id);
    var reduced = p.scenario;
    if (c.id === 'initial') reduced.initialCapital = 0;
    else reduced.contributions = reduced.contributions.filter(function (entry) { return entry.id !== id; });
    // Recur without this trajectory instead of subtracting nearly equal floating
    // values; this also yields exact zero when the sole principal is removed.
    var counterfactual = project(reduced);
    var delta = p.finalBalance - counterfactual.finalBalance;
    return { finalBalance: counterfactual.finalBalance, delta: delta, relative: p.finalBalance === 0 ? null : delta / p.finalBalance, snapshots: counterfactual.snapshots.map(function (s) { return { month: s.month, balance: s.balance }; }) };
  }

  function difference(baseValue, nextValue) {
    var base = projection(baseValue);
    var next = projection(nextValue);
    var absolute = next.finalBalance - base.finalBalance;
    var contributed = next.snapshots[next.scenario.horizonMonths].totalContributed - base.snapshots[base.scenario.horizonMonths].totalContributed;
    return { absolute: absolute, relative: base.finalBalance === 0 ? null : absolute / base.finalBalance, contributed: contributed, returns: absolute - contributed };
  }
  ns.simulation = Object.freeze({ limits: limits, periodic: periodic, project: project, inspect: inspect, trace: trace, without: without, difference: difference });
})(window);
