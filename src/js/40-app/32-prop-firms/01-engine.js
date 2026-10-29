/* Hedge Prop: synthetic endpoint model approved in BRIEF-HEDGE-PROP-20261027.
 * Pure classic script. Costs describe impact only; they never resize the hedge.
 */
(function (root) {
  'use strict';

  const missing = value => value === undefined || value === null ||
    (typeof value === 'string' && value.trim() === '');
  const finiteNumber = value => typeof value === 'number' && Number.isFinite(value);
  const problem = (code, field) => ({ code, field });
  const percentOf = (value, percent) => {
    const fraction = percent / 100;
    return fraction === 0 ? (value / 100) * percent : value * fraction;
  };
  function empty(status, errors) {
    return { ok: false, status, errors, costErrors: [], drawdownUSD: null,
      stages: [], funded: null, totals: null, outcomes: [] };
  }

  function calculate(input) {
    const errors = [];
    if (missing(input)) return empty('INVALID', [problem('MISSING', 'input')]);
    if (typeof input !== 'object' || Array.isArray(input)) return empty('INVALID', [problem('INVALID_INPUT', 'input')]);
    function number(value, field, valid) {
      if (missing(value)) errors.push(problem('MISSING', field));
      else if (!finiteNumber(value)) errors.push(problem('INVALID_NUMBER', field));
      else if (!valid(value)) errors.push(problem('OUT_OF_RANGE', field));
    }
    number(input.nominalUSD, 'nominalUSD', value => value > 0);
    number(input.feeUSD, 'feeUSD', value => value >= 0);
    number(input.payoutPercent, 'payoutPercent', value => value > 0 && value <= 100);
    number(input.drawdownPercent, 'drawdownPercent', value => value > 0 && value <= 100);
    number(input.refundUSD, 'refundUSD', value => value >= 0 && (!finiteNumber(input.feeUSD) || value <= input.feeUSD));
    const targets = input.targetsPercent;
    if (missing(targets)) errors.push(problem('MISSING', 'targetsPercent'));
    else if (!Array.isArray(targets) || (targets.length !== 1 && targets.length !== 2)) errors.push(problem('INVALID_TARGETS', 'targetsPercent'));
    else for (let i = 0; i < targets.length; i += 1) number(targets[i], `targetsPercent[${i}]`, value => value > 0);
    if (errors.length) return empty('INVALID', errors);

    const fee = input.feeUSD;
    const drawdown = percentOf(input.nominalUSD, input.drawdownPercent);
    const payout = input.payoutPercent / 100;
    const unrepresentable = field => empty('UNREPRESENTABLE', [problem('UNREPRESENTABLE', field)]);
    if (!finiteNumber(drawdown) || drawdown <= 0) return unrepresentable('drawdownUSD');
    if (payout <= 0) return unrepresentable('payoutPercent');
    const stages = [];
    let loss = fee;
    let evaluationCapital = 0;
    for (let i = 0; i < targets.length; i += 1) {
      const target = percentOf(input.nominalUSD, targets[i]);
      const ratio = loss / drawdown;
      const capital = ratio * target;
      const nextLoss = loss + capital;
      const nextCapital = evaluationCapital + capital;
      if (![target, ratio, capital, nextLoss, nextCapital].every(finiteNumber) || target <= 0 ||
          (fee > 0 && (ratio <= 0 || capital <= 0))) return unrepresentable(`stages[${i}]`);
      stages.push({ targetUSD: target, hedgeRatio: ratio, hedgeCapitalUSD: capital, accumulatedLossUSD: nextLoss });
      loss = nextLoss;
      evaluationCapital = nextCapital;
    }
    const fundedRatio = loss / drawdown;
    if (!finiteNumber(fundedRatio) || (fee > 0 && fundedRatio <= 0)) return unrepresentable('funded.hedgeRatio');
    if (fee > 0 && payout <= fundedRatio) {
      return { ok: false, status: 'INFEASIBLE', errors: [problem('PAYOUT_NOT_ABOVE_HEDGE', 'payoutPercent')],
        costErrors: [], drawdownUSD: drawdown, stages,
        funded: { hedgeRatio: fundedRatio, targetUSD: null, targetPercent: null, hedgeLossUSD: null, reserveUSD: null },
        totals: { feeUSD: fee, hedgeCapitalUSD: null, capitalIncludingFeeUSD: null, multipleIncludingFee: null }, outcomes: [] };
    }
    const fundedTarget = fee === 0 ? 0 : (loss - input.refundUSD) / (payout - fundedRatio);
    const targetPercent = fundedTarget / input.nominalUSD * 100;
    const fundedLoss = fundedRatio * fundedTarget;
    const reserve = 2 * fundedLoss;
    const hedgeCapital = evaluationCapital + reserve;
    const budget = fee + hedgeCapital;
    const multiple = fee === 0 ? null : budget / fee;
    if (![fundedTarget, targetPercent, fundedLoss, reserve, hedgeCapital, budget].every(finiteNumber) ||
        (multiple !== null && !finiteNumber(multiple)) || (fee > 0 && (fundedTarget <= 0 || fundedLoss <= 0))) return unrepresentable('funded');

    // Each cost cell is independent. Missing never means zero, and a bad cell
    // invalidates only paths that consume it; ideal financial results stay valid.
    const costErrors = [];
    const costs = [];
    const suppliedCosts = input.costs;
    const extraRows = Array.isArray(suppliedCosts) && suppliedCosts.length > targets.length + 1;
    const invalidCollection = extraRows || (!missing(suppliedCosts) && !Array.isArray(suppliedCosts));
    if (invalidCollection) costErrors.push(problem(extraRows ? 'EXTRA_COST_ROWS' : 'INVALID_COSTS', 'costs'));
    for (let i = 0; i <= targets.length; i += 1) {
      const supplied = Array.isArray(suppliedCosts) ? suppliedCosts[i] : undefined;
      const invalidRow = !missing(supplied) && (typeof supplied !== 'object' || Array.isArray(supplied));
      const row = {};
      ['passUSD', 'failUSD'].forEach(key => {
        const field = `costs[${i}].${key}`;
        const value = supplied && !invalidRow ? supplied[key] : undefined;
        if (invalidCollection || invalidRow) {
          row[key] = { status: 'INVALID', value: null, field };
          if (invalidRow) costErrors.push(problem('INVALID_COST_ROW', field));
        } else if (missing(value)) row[key] = { status: 'PENDING', value: null, field };
        else if (!finiteNumber(value) || value < 0) {
          row[key] = { status: 'INVALID', value: null, field };
          costErrors.push(problem('INVALID_COST', field));
        } else row[key] = { status: 'COMPLETE', value, field };
      });
      costs.push(row);
    }
    const outcomes = [];
    const prefix = [];
    function addOutcome(id, kind, stageIndex, idealNet, cells) {
      let costStatus = cells.some(cell => cell.status === 'INVALID') ? 'INVALID' :
        cells.some(cell => cell.status === 'PENDING') ? 'PENDING' : 'COMPLETE';
      let total = null;
      let net = null;
      if (costStatus === 'COMPLETE') {
        total = cells.reduce((sum, cell) => sum + cell.value, 0);
        net = idealNet - total;
        if (!finiteNumber(total) || !finiteNumber(net)) {
          costErrors.push(problem('UNREPRESENTABLE_COST_TOTAL', id));
          costStatus = 'INVALID'; total = null; net = null;
        }
      }
      outcomes.push({ id, kind, stageIndex, idealNetUSD: idealNet, estimatedCostsUSD: total,
        netAfterCostsUSD: net, costStatus, missingCostFields: cells.filter(cell => cell.status === 'PENDING').map(cell => cell.field) });
    }
    let previousLoss = fee;
    for (let i = 0; i < stages.length; i += 1) {
      addOutcome(`evaluation-fail-${i}`, 'EVALUATION_FAIL', i, -previousLoss + stages[i].hedgeRatio * drawdown, prefix.concat(costs[i].failUSD));
      prefix.push(costs[i].passUSD);
      previousLoss = stages[i].accumulatedLossUSD;
    }
    addOutcome('funded-fail', 'FUNDED_FAIL', null, -loss + fundedRatio * drawdown, prefix.concat(costs[stages.length].failUSD));
    addOutcome('funded-pass', 'FUNDED_PASS', null, -loss + (payout - fundedRatio) * fundedTarget + input.refundUSD, prefix.concat(costs[stages.length].passUSD));
    addOutcome('funded-no-receipt', 'FUNDED_NO_RECEIPT', null, -loss - fundedLoss, prefix.concat(costs[stages.length].passUSD));
    if (outcomes.some(row => !finiteNumber(row.idealNetUSD))) return unrepresentable('outcomes');
    return { ok: true, status: 'VALID', errors: [], costErrors, drawdownUSD: drawdown, stages,
      funded: { hedgeRatio: fundedRatio, targetUSD: fundedTarget, targetPercent, hedgeLossUSD: fundedLoss, reserveUSD: reserve },
      totals: { feeUSD: fee, hedgeCapitalUSD: hedgeCapital, capitalIncludingFeeUSD: budget, multipleIncludingFee: multiple }, outcomes };
  }
  root.JPWHedgeProp = Object.freeze({ calculate });
}(typeof window !== 'undefined' ? window : globalThis));
